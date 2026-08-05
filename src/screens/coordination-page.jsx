import { useState } from 'react'
import {
  Activity,
  ArrowLeft,
  BellRing,
  CloudOff,
  FlaskConical,
  History,
  Map as MapIcon,
  Megaphone,
  RefreshCw,
  Trophy,
  Users,
  Wifi,
} from 'lucide-react'
import { useApp } from '../context/app-context'
import { Brand } from '../components/brand'
import { LanguageSelector } from '../components/language-selector'
import { StatusBanner, MockBadge } from '../components/status-banner'
import { MOCK_RANKING, MOCK_REQUESTS, MOCK_SECTORS } from '../data/mocks'
import {
  cn,
  formatProbability,
  formatTemperature,
  formatTime,
  headlineKey,
  riskLabelKey,
} from '../lib/utils'

const REQUEST_LABELS = {
  new: 'Nueva',
  progress: 'En atención',
  done: 'Atendida',
}

export function CoordinationPage() {
  const {
    t,
    setView,
    prediction,
    recommendation,
    station,
    stations,
    loading,
    apiOnline,
    refreshPrediction,
    alertLogs,
    alertActive,
    activateAlert,
  } = useApp()

  const [requests, setRequests] = useState(MOCK_REQUESTS)

  const advance = id => setRequests(items => items.map(item => (
    item.id === id
      ? { ...item, status: item.status === 'new' ? 'progress' : 'done' }
      : item
  )))

  return (
    <main data-risk={prediction.level} className="min-h-screen bg-background pb-16">
      <header className="border-b border-border bg-card">
        <div className="mx-auto flex w-full max-w-6xl flex-col gap-4 px-5 py-5 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex flex-wrap items-center gap-4">
            <Brand showSubtitle={false} />
            <span className="rounded-lg bg-muted px-3 py-1.5 text-sm font-bold text-muted-foreground">
              Centro de coordinación
            </span>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <ApiIndicator online={apiOnline} />
            <LanguageSelector compact />
            <button
              type="button"
              onClick={() => setView('community')}
              className="flex min-h-11 items-center gap-2 rounded-lg border border-border bg-card px-3 text-sm font-bold text-muted-foreground transition-colors hover:bg-muted"
            >
              <ArrowLeft aria-hidden="true" className="size-4" />
              {t('backToCommunity')}
            </button>
          </div>
        </div>
      </header>

      <div className="mx-auto flex w-full max-w-6xl flex-col gap-5 px-5 pt-6">
        <StatusBanner />

        <div className="grid gap-5 lg:grid-cols-[minmax(0,1.6fr)_minmax(0,1fr)]">
          <section className="risk-card flex flex-col gap-6 rounded-3xl border-2 p-6 shadow-sm">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div className="flex flex-col gap-2">
                <p className="text-sm font-bold uppercase tracking-widest text-muted-foreground">
                  {t('station')}: {prediction.station}
                </p>
                <h1 className="font-serif text-3xl font-black tracking-tight">
                  {prediction.type} · {prediction.risk}
                </h1>
              </div>
              <span className="risk-label inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-black uppercase tracking-wide">
                <Activity aria-hidden="true" className="size-4" />
                {t(riskLabelKey(prediction.level))}
              </span>
            </div>

            <dl className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
              <Metric label={t('temperature')} value={formatTemperature(prediction.temperature)} />
              <Metric label={t('probability')} value={formatProbability(prediction.probability)} />
              <Metric label={t('criticalHour')} value={prediction.criticalHour} />
              <Metric label={t('lastUpdate')} value={formatTime(prediction.receivedAt)} />
            </dl>

            <div className="flex flex-col gap-2 rounded-2xl border border-border bg-card p-4">
              <h2 className="text-sm font-bold uppercase tracking-widest text-muted-foreground">{t('whyLabel')}</h2>
              {prediction.factors.length > 0 ? (
                <ul className="flex flex-col gap-1.5">
                  {prediction.factors.map(factor => (
                    <li key={factor} className="flex items-start gap-2 text-base leading-relaxed">
                      <span aria-hidden="true" className="mt-2 size-2 shrink-0 rounded-full bg-primary" />
                      {factor}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-base text-muted-foreground">Sin factores reportados por el modelo.</p>
              )}
            </div>

            <div className="flex flex-col gap-3 rounded-2xl border border-border bg-card p-4">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <h2 className="text-sm font-bold uppercase tracking-widest text-muted-foreground">
                  {recommendation?.title || 'Acciones recomendadas'}
                </h2>
                <span className="text-xs font-bold uppercase tracking-wide text-muted-foreground">
                  {recommendation ? 'GET /recommendation' : 'Respaldo local'}
                </span>
              </div>
              <ul className="grid gap-2 sm:grid-cols-2">
                {(recommendation?.actions || [
                  'Cubrir cultivos y proteger sistemas de riego',
                  'Resguardar ganado en cobertizos',
                  'Informar a la comunidad local',
                  'Preparar suministros de emergencia',
                ]).map(action => (
                  <li key={action} className="rounded-xl border border-border bg-background px-3 py-2 text-sm font-semibold leading-relaxed">
                    {action}
                  </li>
                ))}
              </ul>
            </div>

            <div className="flex flex-col gap-3 rounded-2xl border border-border bg-card p-4">
              <h2 className="flex items-center gap-2 text-sm font-bold uppercase tracking-widest text-muted-foreground">
                <Megaphone aria-hidden="true" className="size-4" />
                Mensaje que verá el poblador
              </h2>
              <p className="font-serif text-xl font-black leading-snug text-balance">
                {t(headlineKey(prediction.level))}
              </p>
              <p className="text-sm text-muted-foreground">
                {t('criticalHour')}: {prediction.criticalHour} · {t('temperature')}: {formatTemperature(prediction.temperature)}
              </p>
              <button
                type="button"
                onClick={activateAlert}
                className="risk-button flex min-h-14 items-center justify-center gap-2 rounded-xl px-5 text-lg font-black text-[color:var(--risk-contrast)]"
              >
                <BellRing aria-hidden="true" className="size-5" />
                {alertActive ? 'Aviso comunitario activo' : 'Activar aviso comunitario'}
              </button>
              {alertActive && (
                <p role="status" className="text-sm font-semibold text-success-foreground">
                  El aviso quedó disponible en la vista comunitaria. No se envían SMS ni WhatsApp reales.
                </p>
              )}
            </div>
          </section>

          <div className="flex flex-col gap-5">
            <section className="flex flex-col gap-4 rounded-2xl border border-border bg-card p-5 shadow-sm">
              <h2 className="font-serif text-xl font-black tracking-tight">Consulta al modelo</h2>

              <div className="flex flex-col gap-2">
                <label htmlFor="station" className="text-sm font-bold uppercase tracking-wide text-muted-foreground">
                  {t('station')}
                </label>
                <select
                  id="station"
                  value={station}
                  onChange={event => refreshPrediction(event.target.value)}
                  className="min-h-12 rounded-xl border-2 border-border bg-background px-3 text-base font-semibold"
                >
                  {stations.map(item => <option key={item} value={item}>{item}</option>)}
                </select>
              </div>

              <button
                type="button"
                onClick={() => refreshPrediction(station)}
                disabled={loading}
                className="flex min-h-14 items-center justify-center gap-2 rounded-xl bg-primary px-4 text-base font-black text-primary-foreground disabled:opacity-60"
              >
                <RefreshCw aria-hidden="true" className={cn('size-5', loading && 'animate-spin')} />
                Actualizar datos de {station}
              </button>
              <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                Consulta real: POST /predict
              </p>

              <div className="flex flex-col gap-2 rounded-xl border border-border bg-muted/60 p-3">
                <p className="flex items-center gap-2 text-sm font-bold text-muted-foreground">
                  <FlaskConical aria-hidden="true" className="size-4" />
                  Usar escenario de demostración
                </p>
                <div className="flex flex-wrap gap-2">
                  <button
                    type="button"
                    onClick={() => refreshPrediction(station, 'helada')}
                    disabled={loading}
                    className="min-h-11 flex-1 rounded-lg border-2 border-border bg-card px-3 text-sm font-bold disabled:opacity-60"
                  >
                    Noche con helada
                  </button>
                  <button
                    type="button"
                    onClick={() => refreshPrediction(station, 'sin_helada')}
                    disabled={loading}
                    className="min-h-11 flex-1 rounded-lg border-2 border-border bg-card px-3 text-sm font-bold disabled:opacity-60"
                  >
                    Día sin helada
                  </button>
                </div>
                <p className="text-xs text-muted-foreground">
                  El escenario también usa POST /predict, con el parámetro `escenario` del backend.
                </p>
              </div>

              <p className="text-sm font-semibold text-muted-foreground">
                Origen del dato mostrado:{' '}
                <span className="text-foreground">
                  {prediction.source === 'api' && 'Predicción real del modelo'}
                  {prediction.source === 'demo' && 'Escenario de demostración del backend'}
                  {prediction.source === 'fallback' && 'Última información disponible'}
                </span>
              </p>
            </section>

            <section className="flex flex-col gap-3 rounded-2xl border border-border bg-card p-5 shadow-sm">
              <div className="flex items-center justify-between gap-3">
                <h2 className="flex items-center gap-2 font-serif text-xl font-black tracking-tight">
                  <History aria-hidden="true" className="size-5 text-primary" />
                  Historial de alertas
                </h2>
                {alertLogs.isMock && <MockBadge />}
              </div>
              <ul className="flex flex-col gap-2">
                {alertLogs.items.slice(0, 4).map((log, index) => (
                  <li key={`${log.fecha_hora}-${index}`} className="rounded-xl border border-border bg-background p-3">
                    <p className="text-sm font-black">{log.tipo_evento}</p>
                    <p className="text-xs font-semibold text-muted-foreground">{log.estacion} · {log.fecha_hora}</p>
                    <p className="mt-1 text-sm leading-relaxed">{log.mensaje}</p>
                  </li>
                ))}
              </ul>
              <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                {alertLogs.isMock ? 'Respaldo local' : 'GET /alerts'}
              </p>
            </section>
          </div>
        </div>

        <div className="grid gap-5 lg:grid-cols-3">
          <section className="flex flex-col gap-3 rounded-2xl border border-border bg-card p-5 shadow-sm lg:col-span-2">
            <div className="flex items-center justify-between gap-3">
              <h2 className="flex items-center gap-2 font-serif text-xl font-black tracking-tight">
                <Users aria-hidden="true" className="size-5 text-primary" />
                Solicitudes de apoyo
              </h2>
              <MockBadge />
            </div>
            <ul className="flex flex-col gap-2">
              {requests.map(item => (
                <li key={item.id} className="flex flex-wrap items-center gap-3 rounded-xl border border-border bg-background p-3">
                  <span className="request-dot size-3 shrink-0 rounded-full" data-status={item.status} aria-hidden="true" />
                  <div className="flex min-w-0 flex-1 flex-col">
                    <p className="text-sm font-black">{item.person} · {item.sector}</p>
                    <p className="text-sm leading-relaxed text-muted-foreground">{item.need}</p>
                  </div>
                  <span className="text-xs font-bold uppercase tracking-wide text-muted-foreground">
                    {REQUEST_LABELS[item.status]} · {item.time}
                  </span>
                  {item.status !== 'done' && (
                    <button
                      type="button"
                      onClick={() => advance(item.id)}
                      className="min-h-10 rounded-lg border-2 border-border bg-card px-3 text-sm font-bold"
                    >
                      {item.status === 'new' ? 'Tomar' : 'Cerrar'}
                    </button>
                  )}
                </li>
              ))}
            </ul>
          </section>

          <section className="flex flex-col gap-3 rounded-2xl border border-border bg-card p-5 shadow-sm">
            <div className="flex items-center justify-between gap-3">
              <h2 className="flex items-center gap-2 font-serif text-xl font-black tracking-tight">
                <Trophy aria-hidden="true" className="size-5 text-primary" />
                Respuesta por sector
              </h2>
              <MockBadge />
            </div>
            <ol className="flex flex-col gap-3">
              {MOCK_RANKING.map((item, index) => (
                <li key={item.sector} className="flex flex-col gap-1.5">
                  <div className="flex items-center justify-between gap-2 text-sm font-bold">
                    <span>{index + 1}. {item.sector}</span>
                    <span className="text-muted-foreground">{item.responseRate} %</span>
                  </div>
                  <div className="h-2.5 w-full overflow-hidden rounded-full bg-muted">
                    <div className="h-full rounded-full bg-primary" style={{ width: `${item.responseRate}%` }} />
                  </div>
                </li>
              ))}
            </ol>
          </section>
        </div>

        <section className="flex flex-col gap-4 rounded-2xl border border-border bg-card p-5 shadow-sm">
          <div className="flex items-center justify-between gap-3">
            <h2 className="flex items-center gap-2 font-serif text-xl font-black tracking-tight">
              <MapIcon aria-hidden="true" className="size-5 text-primary" />
              Mapa comunitario de Imata
            </h2>
            <MockBadge />
          </div>
          <div className="grid gap-4 md:grid-cols-[minmax(0,1.2fr)_minmax(0,1fr)]">
            <div className="relative aspect-[4/3] overflow-hidden rounded-2xl border border-border bg-muted">
              {MOCK_SECTORS.map(sector => {
                const rate = Math.round((sector.confirmed / sector.families) * 100)
                return (
                  <span
                    key={sector.id}
                    className="absolute flex -translate-x-1/2 -translate-y-1/2 flex-col items-center gap-1"
                    style={{ left: `${sector.x}%`, top: `${sector.y}%` }}
                  >
                    <span
                      className={cn(
                        'flex size-11 items-center justify-center rounded-full border-2 border-card text-xs font-black text-primary-foreground shadow-sm',
                        rate >= 70 ? 'bg-success' : rate >= 40 ? 'bg-warning' : 'bg-destructive',
                      )}
                    >
                      {rate}%
                    </span>
                    <span className="rounded-md bg-card px-2 py-0.5 text-xs font-bold">{sector.name}</span>
                  </span>
                )
              })}
            </div>
            <ul className="flex flex-col gap-2">
              {MOCK_SECTORS.map(sector => (
                <li key={sector.id} className="flex items-center justify-between gap-3 rounded-xl border border-border bg-background p-3">
                  <span className="text-sm font-black">{sector.name}</span>
                  <span className="text-sm font-semibold text-muted-foreground">
                    {sector.confirmed} de {sector.families} familias
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </section>
      </div>
    </main>
  )
}

function Metric({ label, value }) {
  return (
    <div className="flex flex-col gap-1 rounded-2xl border border-border bg-card p-4">
      <dt className="text-sm font-bold text-muted-foreground">{label}</dt>
      <dd className="text-2xl font-black tracking-tight">{value}</dd>
    </div>
  )
}

/** Indicador discreto del estado de GET /health. */
function ApiIndicator({ online }) {
  if (online === null) {
    return (
      <span className="flex min-h-11 items-center gap-2 rounded-lg border border-border bg-card px-3 text-sm font-bold text-muted-foreground">
        <Wifi aria-hidden="true" className="size-4" />
        Verificando backend…
      </span>
    )
  }

  return (
    <span
      className={cn(
        'flex min-h-11 items-center gap-2 rounded-lg border px-3 text-sm font-bold',
        online
          ? 'border-success/40 bg-success-soft text-success-foreground'
          : 'border-warning/40 bg-warning-soft text-warning-foreground',
      )}
    >
      {online ? <Wifi aria-hidden="true" className="size-4" /> : <CloudOff aria-hidden="true" className="size-4" />}
      {online ? 'Backend conectado' : 'API sin conexión'}
    </span>
  )
}
