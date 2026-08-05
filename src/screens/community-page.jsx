import { useMemo, useState } from 'react'
import {
  AlertTriangle,
  CheckCircle2,
  Clock,
  HandHeart,
  Info,
  Repeat,
  ShieldCheck,
  Snowflake,
  Thermometer,
  Lock,
} from 'lucide-react'
import { useApp } from '../context/app-context'
import { Brand, LocationLabel } from '../components/brand'
import { LanguageSelector } from '../components/language-selector'
import { AudioButton } from '../components/audio-button'
import { StatusBanner } from '../components/status-banner'
import {
  cn,
  formatProbability,
  formatTemperature,
  headlineKey,
  riskLabelKey,
} from '../lib/utils'

const DEFAULT_ACTIONS = {
  HELADA: [
    'Cubrir cultivos y proteger sistemas de riego',
    'Resguardar ganado en cobertizos',
    'Informar a la comunidad local',
    'Preparar suministros de emergencia',
  ],
  FRIAJE: [
    'Asegurar techos, puertas y ventanas',
    'Tener ropa de abrigo a disposición',
    'Proteger a niñas, niños y adultos mayores',
    'Evitar exposición prolongada al frío',
  ],
}

export function CommunityPage() {
  const { t, prediction, recommendation, setView, language } = useApp()
  const [explain, setExplain] = useState(false)
  const [response, setResponse] = useState('pending')

  const actions = useMemo(() => {
    if (recommendation?.actions?.length) return recommendation.actions
    return DEFAULT_ACTIONS[prediction.type] || DEFAULT_ACTIONS.HELADA
  }, [recommendation, prediction.type])

  const eventName = prediction.type === 'FRIAJE' ? t('eventFriaje') : t('eventHelada')

  const spokenMessage = useMemo(() => ([
    headlineKey(prediction.level),
    `${eventName} en ${prediction.station}`,
    `${t('temperature')}: ${formatTemperature(prediction.temperature)}`,
    `${t('criticalHour')}: ${prediction.criticalHour}`,
    ...actions,
  ]), [prediction, actions, eventName, t])

  return (
    <main data-risk={prediction.level} className="min-h-screen bg-background pb-16">
      <header className="border-b border-border bg-card">
        <div className="mx-auto flex w-full max-w-3xl flex-col gap-4 px-5 py-5 md:flex-row md:items-center md:justify-between">
          <Brand />
          <LanguageSelector compact />
        </div>
      </header>

      <div className="mx-auto flex w-full max-w-3xl flex-col gap-5 px-5 pt-6">
        <div className="flex items-center justify-between gap-4">
          <LocationLabel />
          <button
            type="button"
            onClick={() => setView('login')}
            className="flex min-h-11 items-center gap-2 rounded-lg border border-border bg-card px-3 text-sm font-bold text-muted-foreground transition-colors hover:bg-muted"
          >
            <Lock aria-hidden="true" className="size-4" />
            {t('institutionalAccess')}
          </button>
        </div>

        <StatusBanner />

        <section className="risk-card overflow-hidden rounded-3xl border-2 shadow-sm">
          <div className="risk-strip h-2 w-full" aria-hidden="true" />
          <div className="flex flex-col gap-6 p-6 md:p-8">
            <div className="flex flex-wrap items-center gap-3">
              <span className="risk-label inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-black uppercase tracking-wide">
                <AlertTriangle aria-hidden="true" className="size-4" />
                {t(riskLabelKey(prediction.level))}
              </span>
              <span className="inline-flex items-center gap-2 rounded-lg border border-border bg-card px-3 py-2 text-sm font-bold text-muted-foreground">
                <Snowflake aria-hidden="true" className="size-4" />
                {eventName} · {prediction.station}
              </span>
            </div>

            <h1 className="font-serif text-3xl font-black leading-tight tracking-tight text-balance md:text-4xl">
              {t(headlineKey(prediction.level))}
            </h1>

            <dl className="grid gap-3 sm:grid-cols-3">
              <div className="flex flex-col gap-1 rounded-2xl border border-border bg-card p-4">
                <dt className="flex items-center gap-2 text-sm font-bold text-muted-foreground">
                  <Thermometer aria-hidden="true" className="size-4" />
                  {t('temperature')}
                </dt>
                <dd className="text-3xl font-black tracking-tight">{formatTemperature(prediction.temperature)}</dd>
              </div>
              <div className="flex flex-col gap-1 rounded-2xl border border-border bg-card p-4">
                <dt className="flex items-center gap-2 text-sm font-bold text-muted-foreground">
                  <Clock aria-hidden="true" className="size-4" />
                  {t('criticalHour')}
                </dt>
                <dd className="text-3xl font-black tracking-tight">{prediction.criticalHour}</dd>
              </div>
              <div className="flex flex-col gap-1 rounded-2xl border border-border bg-card p-4">
                <dt className="flex items-center gap-2 text-sm font-bold text-muted-foreground">
                  <ShieldCheck aria-hidden="true" className="size-4" />
                  {t('probability')}
                </dt>
                <dd className="text-3xl font-black tracking-tight">{formatProbability(prediction.probability)}</dd>
              </div>
            </dl>

            <div className="flex flex-col gap-3">
              <h2 className="font-serif text-2xl font-black tracking-tight">{t('whatToDo')}</h2>
              <ul className="flex flex-col gap-3">
                {actions.map((action, index) => (
                  <li key={action} className="flex items-start gap-3 rounded-2xl border border-border bg-card p-4 text-lg font-semibold leading-relaxed">
                    <span className="risk-button flex size-8 shrink-0 items-center justify-center rounded-lg text-base font-black text-[color:var(--risk-contrast)]">
                      {index + 1}
                    </span>
                    {action}
                  </li>
                ))}
              </ul>
            </div>

            <AudioButton texts={spokenMessage} />
          </div>
        </section>

        {prediction.factors.length > 0 && (
          <section className="flex flex-col gap-3 rounded-2xl border border-border bg-card p-5">
            <h2 className="flex items-center gap-2 font-serif text-xl font-black tracking-tight">
              <Info aria-hidden="true" className="size-5 text-primary" />
              {t('whyLabel')}
            </h2>
            <ul className="flex flex-col gap-2">
              {prediction.factors.map(factor => (
                <li key={factor} className="flex items-start gap-2 text-base leading-relaxed text-muted-foreground">
                  <span aria-hidden="true" className="mt-2 size-2 shrink-0 rounded-full bg-primary" />
                  {factor}
                </li>
              ))}
            </ul>
          </section>
        )}

        {response === 'pending' ? (
          <section className="flex flex-col gap-3">
            <h2 className="sr-only">{t('whatToDo')}</h2>
            <button
              type="button"
              onClick={() => setResponse('understood')}
              className="flex min-h-20 items-center gap-4 rounded-2xl border-2 border-success bg-success-soft px-5 text-left transition-colors hover:brightness-98"
            >
              <CheckCircle2 aria-hidden="true" className="size-8 shrink-0 text-success" />
              <span className="flex flex-col">
                <span className="text-xl font-black text-success-foreground">{t('understood')}</span>
                <span className="text-sm font-medium text-success-foreground/80">{t('understoodHint')}</span>
              </span>
            </button>

            <button
              type="button"
              onClick={() => setExplain(value => !value)}
              aria-expanded={explain}
              className="flex min-h-20 items-center gap-4 rounded-2xl border-2 border-primary bg-card px-5 text-left transition-colors hover:bg-muted"
            >
              <Repeat aria-hidden="true" className="size-8 shrink-0 text-primary" />
              <span className="flex flex-col">
                <span className="text-xl font-black text-primary">{t('explainAgain')}</span>
                <span className="text-sm font-medium text-muted-foreground">{t('explainAgainHint')}</span>
              </span>
            </button>

            <button
              type="button"
              onClick={() => setResponse('help')}
              className="flex min-h-20 items-center gap-4 rounded-2xl border-2 border-warning bg-warning-soft px-5 text-left transition-colors hover:brightness-98"
            >
              <HandHeart aria-hidden="true" className="size-8 shrink-0 text-warning-foreground" />
              <span className="flex flex-col">
                <span className="text-xl font-black text-warning-foreground">{t('needHelp')}</span>
                <span className="text-sm font-medium text-warning-foreground/80">{t('needHelpHint')}</span>
              </span>
            </button>
          </section>
        ) : (
          <section
            className={cn(
              'flex flex-col gap-4 rounded-2xl border-2 p-6',
              response === 'understood' ? 'border-success bg-success-soft' : 'border-warning bg-warning-soft',
            )}
          >
            <div className="flex items-start gap-4">
              {response === 'understood'
                ? <CheckCircle2 aria-hidden="true" className="size-9 shrink-0 text-success" />
                : <HandHeart aria-hidden="true" className="size-9 shrink-0 text-warning-foreground" />}
              <div className="flex flex-col gap-1">
                <h2 className="font-serif text-2xl font-black tracking-tight">
                  {t(response === 'understood' ? 'understoodTitle' : 'helpTitle')}
                </h2>
                <p className="text-base leading-relaxed">
                  {t(response === 'understood' ? 'understoodBody' : 'helpBody')}
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={() => setResponse('pending')}
              className="min-h-12 self-start rounded-xl border-2 border-foreground/20 bg-card px-4 text-base font-bold"
            >
              {t('changeAnswer')}
            </button>
          </section>
        )}

        {explain && (
          <section className="flex flex-col gap-4 rounded-2xl border-2 border-primary bg-accent p-6">
            <h2 className="font-serif text-2xl font-black tracking-tight text-accent-foreground">{t('explainTitle')}</h2>
            <ol className="flex flex-col gap-3">
              {[
                `${eventName}: ${prediction.station}.`,
                `${t('criticalHour')}: ${prediction.criticalHour}.`,
                `${t('temperature')}: ${formatTemperature(prediction.temperature)}.`,
                ...actions,
              ].map((line, index) => (
                <li key={`${line}-${index}`} className="flex items-start gap-3 text-lg font-semibold leading-relaxed text-accent-foreground">
                  <span className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-primary text-base font-black text-primary-foreground">
                    {index + 1}
                  </span>
                  {line}
                </li>
              ))}
            </ol>
            <AudioButton key={language} texts={spokenMessage} autoPlay />
            <button
              type="button"
              onClick={() => setExplain(false)}
              className="min-h-12 self-start rounded-xl bg-primary px-5 text-base font-bold text-primary-foreground"
            >
              {t('explainClose')}
            </button>
          </section>
        )}
      </div>
    </main>
  )
}
