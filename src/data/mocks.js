/**
 * DATOS SIMULADOS (MOCK)
 * ----------------------------------------------------------------
 * El backend actual NO expone endpoints para estos módulos, por lo
 * que se mantienen como simulación local para la demostración.
 * Todo lo que se consume desde aquí se muestra en la interfaz con la
 * etiqueta "Dato simulado" y nunca se presenta como dato real.
 *
 * Endpoints reales disponibles hoy: /health, /estaciones, /predict,
 * /recommendation/{tipo}, /alerts.
 */

export const IS_MOCK = true

/** Sectores de la comunidad y confirmaciones de los pobladores. */
export const MOCK_SECTORS = [
  { id: 'centro', name: 'Imata Centro', families: 42, confirmed: 31, x: 46, y: 38 },
  { id: 'pampa', name: 'Pampa Alta', families: 28, confirmed: 12, x: 24, y: 62 },
  { id: 'rio', name: 'Orilla del río', families: 19, confirmed: 17, x: 68, y: 66 },
  { id: 'estancia', name: 'Estancia Sur', families: 23, confirmed: 6, x: 58, y: 20 },
]

/** Solicitudes de apoyo levantadas por los pobladores. */
export const MOCK_REQUESTS = [
  {
    id: 'sol-104',
    sector: 'Pampa Alta',
    person: 'Familia Quispe Ccama',
    need: 'Necesita mantas térmicas para 40 alpacas',
    status: 'new',
    time: '04:12',
  },
  {
    id: 'sol-103',
    sector: 'Estancia Sur',
    person: 'Rosa Huamaní',
    need: 'Pide apoyo para cubrir el sembrío de papa',
    status: 'progress',
    time: '03:48',
  },
  {
    id: 'sol-102',
    sector: 'Imata Centro',
    person: 'Puesto de salud',
    need: 'Solicita abrigo para adultos mayores',
    status: 'done',
    time: '02:20',
  },
]

/** Ranking de sectores por respuesta comunitaria. */
export const MOCK_RANKING = [
  { sector: 'Orilla del río', responseRate: 89 },
  { sector: 'Imata Centro', responseRate: 74 },
  { sector: 'Pampa Alta', responseRate: 43 },
  { sector: 'Estancia Sur', responseRate: 26 },
]

/** Respaldo del historial cuando GET /alerts no responde. */
export const MOCK_ALERT_LOGS = [
  {
    tipo_evento: 'INICIO DE OLA DE FRÍO',
    estacion: 'Imata',
    fecha_hora: '2025-08-01 00:00:00',
    mensaje: 'Se inicia un periodo de heladas recurrentes en Imata.',
    accion_requerida: 'Activar coberturas térmicas y resguardar ganado.',
  },
  {
    tipo_evento: 'HELADA NOCTURNA',
    estacion: 'Imata',
    fecha_hora: '2025-07-28 04:00:00',
    mensaje: 'Helada severa confirmada durante la madrugada.',
    accion_requerida: 'Revisar cultivos y reportar pérdidas al comité.',
  },
]

/** Catálogo local usado solo si GET /estaciones no responde. */
export const FALLBACK_STATIONS = [
  'Imata',
  'Chivay',
  'Pampacolca',
  'Condoroma',
  'Crucero Alto',
  'Pillones',
  'Pampilla',
  'Arequipa - Cayma',
]

/** Última información conocida de Imata, usada como respaldo offline. */
export const FALLBACK_PREDICTION = {
  estacion: 'Imata',
  tipo: 'HELADA',
  riesgo: 'ALTO',
  probabilidad: 0.95,
  temperatura_estimada: -12.4,
  hora_critica: '04:00 AM',
  factores: [
    'Temperatura mínima bajo cero proyectada (+6h)',
    'Altitud elevada (Puna de Arequipa >3,800 msnm)',
  ],
}
