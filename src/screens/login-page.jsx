import { useState } from 'react'
import { ArrowLeft, Lock, ShieldCheck } from 'lucide-react'
import { useApp } from '../context/app-context'
import { Brand } from '../components/brand'
import { MockBadge } from '../components/status-banner'

/**
 * Acceso institucional. El backend no expone endpoints de autenticación,
 * por lo que la validación es SIMULADA (mock) para la demostración.
 */
const DEMO_CODE = 'IMATA'

export function LoginPage() {
  const { t, setView } = useApp()
  const [code, setCode] = useState('')
  const [error, setError] = useState(false)

  const submit = event => {
    event.preventDefault()
    if (code.trim().toUpperCase() === DEMO_CODE) {
      setError(false)
      setView('coordination')
      return
    }
    setError(true)
  }

  return (
    <main className="flex min-h-screen flex-col bg-background">
      <header className="border-b border-border bg-card">
        <div className="mx-auto flex w-full max-w-3xl items-center justify-between gap-4 px-5 py-5">
          <Brand />
          <button
            type="button"
            onClick={() => setView('community')}
            className="flex min-h-11 items-center gap-2 rounded-lg border border-border bg-card px-3 text-sm font-bold text-muted-foreground transition-colors hover:bg-muted"
          >
            <ArrowLeft aria-hidden="true" className="size-4" />
            {t('backToCommunity')}
          </button>
        </div>
      </header>

      <div className="mx-auto flex w-full max-w-md flex-1 flex-col justify-center gap-6 px-5 py-12">
        <div className="flex flex-col gap-3">
          <span className="flex size-12 items-center justify-center rounded-xl bg-primary text-primary-foreground">
            <Lock aria-hidden="true" className="size-6" />
          </span>
          <h1 className="font-serif text-3xl font-black tracking-tight text-balance">
            Centro de coordinación de Imata
          </h1>
          <p className="text-base leading-relaxed text-muted-foreground">
            Ingresa el código del comité para revisar la predicción del modelo y activar el aviso comunitario.
          </p>
        </div>

        <form onSubmit={submit} className="flex flex-col gap-4 rounded-2xl border border-border bg-card p-6 shadow-sm">
          <div className="flex items-center justify-between gap-3">
            <label htmlFor="code" className="text-sm font-bold uppercase tracking-wide text-muted-foreground">
              Código del comité
            </label>
            <MockBadge />
          </div>
          <input
            id="code"
            name="code"
            value={code}
            onChange={event => setCode(event.target.value)}
            autoComplete="off"
            placeholder="IMATA"
            aria-invalid={error}
            aria-describedby={error ? 'code-error' : 'code-hint'}
            className="min-h-14 rounded-xl border-2 border-border bg-background px-4 text-lg font-bold tracking-widest uppercase"
          />
          {error ? (
            <p id="code-error" role="alert" className="text-sm font-bold text-destructive">
              El código no coincide. Para la demostración usa IMATA.
            </p>
          ) : (
            <p id="code-hint" className="text-sm text-muted-foreground">
              Validación simulada: no hay servicio de autenticación en el backend.
            </p>
          )}
          <button
            type="submit"
            className="flex min-h-14 items-center justify-center gap-2 rounded-xl bg-primary px-5 text-lg font-black text-primary-foreground"
          >
            <ShieldCheck aria-hidden="true" className="size-5" />
            Entrar al centro de coordinación
          </button>
        </form>
      </div>
    </main>
  )
}
