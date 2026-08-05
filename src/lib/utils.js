/** Une clases condicionalmente sin dependencias externas. */
export function cn(...values) {
  return values.filter(Boolean).join(' ')
}

/** Etiqueta legible del nivel de riesgo según el idioma activo. */
export function riskLabelKey(level) {
  if (level === 'critical') return 'riskCritical'
  if (level === 'high') return 'riskHigh'
  if (level === 'medium') return 'riskMedium'
  return 'riskCalm'
}

/** Titular comunitario según el nivel de riesgo. */
export function headlineKey(level) {
  if (level === 'critical') return 'headlineCritical'
  if (level === 'high') return 'headlineHigh'
  if (level === 'medium') return 'headlineMedium'
  return 'headlineCalm'
}

/** Formatea la temperatura estimada con una cifra decimal. */
export function formatTemperature(value) {
  if (typeof value !== 'number' || Number.isNaN(value)) return '—'
  return `${value.toFixed(1).replace('.0', '')} °C`
}

/** Formatea la probabilidad como porcentaje entero. */
export function formatProbability(value) {
  if (typeof value !== 'number' || Number.isNaN(value)) return '—'
  return `${value} %`
}

/** Hora local corta a partir de una fecha ISO. */
export function formatTime(iso) {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleTimeString('es-PE', { hour: '2-digit', minute: '2-digit' })
  } catch {
    return '—'
  }
}
