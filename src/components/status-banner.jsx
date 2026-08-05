import { Loader2, CloudOff, FlaskConical } from 'lucide-react'
import { useApp } from '../context/app-context'
import { cn } from '../lib/utils'

/** Aviso de carga o de información desactualizada, sin errores técnicos. */
export function StatusBanner() {
  const { loading, stale, t } = useApp()

  if (loading) {
    return (
      <p role="status" className="flex items-center gap-3 rounded-xl border border-border bg-card px-4 py-3 text-base font-semibold text-muted-foreground">
        <Loader2 aria-hidden="true" className="size-5 animate-spin" />
        {t('updating')}
      </p>
    )
  }

  if (stale) {
    return (
      <p role="status" className="flex items-start gap-3 rounded-xl border border-warning/40 bg-warning-soft px-4 py-3 text-base font-semibold text-warning-foreground">
        <CloudOff aria-hidden="true" className="mt-0.5 size-5 shrink-0" />
        {t('staleWarning')}
      </p>
    )
  }

  return null
}

/** Etiqueta reutilizable para todo bloque que aún usa datos simulados. */
export function MockBadge({ className }) {
  const { t } = useApp()
  return (
    <span className={cn('inline-flex items-center gap-1.5 rounded-md border border-border bg-muted px-2 py-1 text-xs font-bold uppercase tracking-wide text-muted-foreground', className)}>
      <FlaskConical aria-hidden="true" className="size-3.5" />
      {t('mockLabel')}
    </span>
  )
}
