/**
 * Capa única de comunicación con el Backend API (FastAPI).
 * Endpoints reales expuestos por backend/routes.py:
 *   GET  /health
 *   GET  /estaciones
 *   POST /predict            { estacion, fecha?, escenario? }
 *   GET  /recommendation/{tipo}
 *   GET  /alerts
 * No se agregan endpoints que el backend no exponga.
 */

export const API_BASE_URL = (
  import.meta.env?.VITE_API_URL || 'http://localhost:8000'
).replace(/\/$/, '')

const DEFAULT_TIMEOUT = 12000

async function request(path, { method = 'GET', body, timeout = DEFAULT_TIMEOUT } = {}) {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), timeout)

  try {
    const res = await fetch(`${API_BASE_URL}${path}`, {
      method,
      headers: body ? { 'Content-Type': 'application/json' } : undefined,
      body: body ? JSON.stringify(body) : undefined,
      signal: controller.signal,
    })

    if (!res.ok) {
      throw new Error(`El servicio respondió ${res.status} en ${path}`)
    }

    return await res.json()
  } finally {
    clearTimeout(timer)
  }
}

/** GET /health → { status: "ok" } */
export async function checkHealth() {
  const data = await request('/health')
  return data?.status === 'ok'
}

/** GET /estaciones → ["Imata", ...] */
export async function fetchStations() {
  const data = await request('/estaciones')
  return Array.isArray(data) ? data : []
}

/**
 * POST /predict
 * @param {string} stationName Nombre de la estación (por ejemplo "Imata").
 * @param {string|null} escenario Modo demostración opcional: 'helada' | 'sin_helada'.
 */
export async function fetchPrediction(stationName, escenario = null) {
  const payload = { estacion: stationName }
  if (escenario) payload.escenario = escenario
  return request('/predict', { method: 'POST', body: payload })
}

/** GET /recommendation/{tipo} → { titulo, acciones[] } */
export async function fetchRecommendation(tipo) {
  return request(`/recommendation/${encodeURIComponent(tipo || 'HELADA')}`)
}

/** GET /alerts → historial del motor de olas de frío */
export async function fetchAlertLogs() {
  const data = await request('/alerts')
  return Array.isArray(data) ? data : []
}
