import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { translations } from '../data/translations'
import {
  FALLBACK_PREDICTION,
  FALLBACK_STATIONS,
  MOCK_ALERT_LOGS,
} from '../data/mocks'
import {
  checkHealth,
  fetchAlertLogs,
  fetchPrediction,
  fetchRecommendation,
  fetchStations,
} from '../services/api'

const AppContext = createContext(null)

const STATION_DEFAULT = 'Imata'
const LANGUAGE_KEY = 'willay:language'

/** Normaliza el campo `riesgo` del backend a un nivel visual del tema. */
export function riskToLevel(riesgo) {
  const value = String(riesgo || '').toUpperCase()
  if (value.includes('CRÍTIC') || value.includes('CRITIC') || value.includes('EXTREM')) return 'critical'
  if (value.includes('ALTO') || value.includes('SEVER')) return 'high'
  if (value.includes('MEDIO') || value.includes('MODERAD')) return 'medium'
  return 'calm'
}

/** Convierte la respuesta de POST /predict en el modelo que usa la interfaz. */
function mapPrediction(data, source) {
  const probabilidad = Number(data?.probabilidad)
  const temperatura = Number(data?.temperatura_estimada)

  return {
    station: data?.estacion || STATION_DEFAULT,
    type: String(data?.tipo || 'HELADA').toUpperCase(),
    risk: data?.riesgo || 'ALTO',
    level: riskToLevel(data?.riesgo),
    probability: Number.isFinite(probabilidad) ? Math.round(probabilidad * 100) : null,
    temperature: Number.isFinite(temperatura) ? temperatura : null,
    criticalHour: data?.hora_critica || '—',
    factors: Array.isArray(data?.factores) ? data.factores.filter(Boolean) : [],
    source,
    receivedAt: new Date().toISOString(),
  }
}

export function AppProvider({ children }) {
  const [language, setLanguageState] = useState('es')
  const [hydrated, setHydrated] = useState(false)
  const [view, setView] = useState('community')

  const [station, setStation] = useState(STATION_DEFAULT)
  const [stations, setStations] = useState(FALLBACK_STATIONS)
  const [prediction, setPrediction] = useState(() => mapPrediction(FALLBACK_PREDICTION, 'fallback'))
  const [recommendation, setRecommendation] = useState(null)
  const [alertLogs, setAlertLogs] = useState({ items: MOCK_ALERT_LOGS, isMock: true })

  const [loading, setLoading] = useState(false)
  const [stale, setStale] = useState(false)
  const [apiOnline, setApiOnline] = useState(null)

  const [alertActive, setAlertActive] = useState(false)
  const [response, setResponse] = useState('pending')

  useEffect(() => {
    try {
      const stored = window.localStorage.getItem(LANGUAGE_KEY)
      if (stored === 'es' || stored === 'qu') setLanguageState(stored)
    } catch {
      // El almacenamiento local puede estar bloqueado; se mantiene español.
    }
    setHydrated(true)
  }, [])

  const setLanguage = useCallback(value => {
    setLanguageState(value)
    try {
      window.localStorage.setItem(LANGUAGE_KEY, value)
    } catch {
      // Sin persistencia disponible: el idioma sigue activo en la sesión.
    }
  }, [])

  const t = useCallback(key => translations[language]?.[key] ?? translations.es[key] ?? key, [language])

  /** POST /predict + GET /recommendation/{tipo} */
  const refreshPrediction = useCallback(async (targetStation = station, escenario = null) => {
    setStation(targetStation)
    setLoading(true)
    try {
      const data = await fetchPrediction(targetStation, escenario)
      const mapped = mapPrediction(data, escenario ? 'demo' : 'api')
      setPrediction(mapped)
      setStale(false)
      setApiOnline(true)

      try {
        const rec = await fetchRecommendation(mapped.type)
        if (Array.isArray(rec?.acciones) && rec.acciones.length > 0) {
          setRecommendation({ title: rec.titulo, actions: rec.acciones, isMock: false })
        }
      } catch {
        // Sin recomendaciones del backend se conservan las anteriores.
      }

      return mapped
    } catch (error) {
      console.warn('[Willay] No se pudo consultar el Backend API:', error.message)
      setStale(true)
      setApiOnline(false)
      return null
    } finally {
      setLoading(false)
    }
  }, [station])

  const loadAlertLogs = useCallback(async () => {
    try {
      const items = await fetchAlertLogs()
      if (items.length > 0) setAlertLogs({ items, isMock: false })
    } catch {
      setAlertLogs({ items: MOCK_ALERT_LOGS, isMock: true })
    }
  }, [])

  // Arranque: /health, /estaciones y una primera predicción de Imata.
  useEffect(() => {
    let active = true

    checkHealth()
      .then(ok => { if (active) setApiOnline(ok) })
      .catch(() => { if (active) setApiOnline(false) })

    fetchStations()
      .then(list => { if (active && list.length > 0) setStations(list) })
      .catch(() => {
        // Se conserva el catálogo local de respaldo.
      })

    refreshPrediction(STATION_DEFAULT)
    loadAlertLogs()

    return () => { active = false }
    // Solo en el arranque de la aplicación.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const activateAlert = useCallback(() => {
    setAlertActive(true)
    setResponse('pending')
  }, [])

  const value = useMemo(() => ({
    language,
    setLanguage,
    t,
    hydrated,
    view,
    setView,
    station,
    stations,
    prediction,
    recommendation,
    alertLogs,
    loading,
    stale,
    apiOnline,
    alertActive,
    activateAlert,
    response,
    setResponse,
    refreshPrediction,
    loadAlertLogs,
  }), [
    language, setLanguage, t, hydrated, view, station, stations, prediction, recommendation,
    alertLogs, loading, stale, apiOnline, alertActive, activateAlert, response, refreshPrediction,
    loadAlertLogs,
  ])

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>
}

export function useApp() {
  const context = useContext(AppContext)
  if (!context) throw new Error('useApp debe usarse dentro de AppProvider')
  return context
}
