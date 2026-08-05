/**
 * Textos de la interfaz en Español y Runa simi (Quechua).
 * Las traducciones en quechua son una propuesta de trabajo y están
 * pendientes de validación con la comunidad de Imata.
 */

export const translations = {
  es: {
    appName: 'Willay',
    subtitle: 'Aviso claro para la comunidad',
    location: 'Imata, Arequipa',

    currentLanguage: 'Idioma actual:',
    spanish: 'Español',
    quechua: 'Runa simi',
    selected: 'seleccionado',

    listenAlert: 'Escuchar el aviso',
    stopAudio: 'Detener el audio',
    listening: 'Reproduciendo el aviso en voz alta',
    audioUnavailable: 'Este equipo no puede reproducir el audio. Puedes leer el aviso.',
    audioValidation: 'El audio en runa simi está pendiente de validación comunitaria.',

    riskCritical: 'Peligro muy alto',
    riskHigh: 'Peligro alto',
    riskMedium: 'Ten cuidado',
    riskCalm: 'Sin peligro por ahora',

    headlineCritical: 'Esta noche el frío puede dañar tus cultivos y tus animales',
    headlineHigh: 'Va a helar fuerte. Protege tus cultivos y tus animales',
    headlineMedium: 'Puede bajar mucho la temperatura. Conviene prepararse',
    headlineCalm: 'Por ahora no hay peligro de helada en Imata',

    eventHelada: 'Helada',
    eventFriaje: 'Friaje',

    temperature: 'Temperatura esperada',
    criticalHour: 'Hora más peligrosa',
    probability: 'Posibilidad de que ocurra',
    station: 'Estación',
    whatToDo: 'Qué debes hacer',
    whyLabel: 'Por qué te avisamos',
    lastUpdate: 'Última actualización',

    understood: 'Ya entendí qué hacer',
    understoodHint: 'Toca aquí si ya sabes qué hacer',
    explainAgain: 'Explícame de nuevo',
    explainAgainHint: 'Te lo decimos con palabras más simples',
    needHelp: 'Todavía necesito apoyo',
    needHelpHint: 'Un responsable de la comunidad te buscará',
    understoodTitle: 'Gracias. Tu respuesta quedó registrada',
    understoodBody: 'El comité de la comunidad ya sabe que entendiste el aviso.',
    helpTitle: 'Pedimos apoyo para ti',
    helpBody: 'Un responsable del comité de Imata se acercará a tu sector.',
    changeAnswer: 'Cambiar mi respuesta',

    explainTitle: 'Te lo explicamos paso a paso',
    explainClose: 'Ya entendí, cerrar',

    updating: 'Actualizando información de Imata…',
    staleWarning: 'No se pudo actualizar la información. Se muestra la última información disponible.',
    institutionalAccess: 'Acceso institucional',
    backToCommunity: 'Volver al aviso de la comunidad',
    mockLabel: 'Dato simulado',
  },
  qu: {
    appName: 'Willay',
    subtitle: 'Ayllupaq sut’i willakuy',
    location: 'Imata, Arequipa',

    currentLanguage: 'Kunan simi:',
    spanish: 'Español',
    quechua: 'Runa simi',
    selected: 'akllasqa',

    listenAlert: 'Willakuyta uyariy',
    stopAudio: 'Uyarichiyta sayachiy',
    listening: 'Willakuy uyarichkan',
    audioUnavailable: 'Kay antaqa manam uyarichiyta atinchu. Willakuyta ñawinchayta atinki.',
    audioValidation: 'Runa simipi uyarichiyqa ayllupa qawapayasqanta suyachkan.',

    riskCritical: 'Ancha hatun pelligru',
    riskHigh: 'Hatun pelligru',
    riskMedium: 'Allinta qaway',
    riskCalm: 'Kunanqa mana pelligruchu',

    headlineCritical: 'Kunan tuta chiriqa chakrakunata, uywakunatapas waqllichinman',
    headlineHigh: 'Sinchi qasaqa hamunqa. Chakraykita, uywaykitapas amachay',
    headlineMedium: 'Chiriqa sinchita uraykunman. Wakichikuy allin kanman',
    headlineCalm: 'Kunanqa Imatapi manam qasa pelligru kanchu',

    eventHelada: 'Qasa',
    eventFriaje: 'Chiri wayra',

    temperature: 'Suyasqa chiri',
    criticalHour: 'Aswan pelligru pacha',
    probability: 'Kanan atiynin',
    station: 'Musyana wasi',
    whatToDo: 'Imatataq ruwanayki',
    whyLabel: 'Imarayku willaykiku',
    lastUpdate: 'Qhipa musuqchay',

    understood: 'Ñam yacharuniña imatam ruwanay',
    understoodHint: 'Yachaptikiqa kayta llamiy',
    explainAgain: 'Huk kutimanta willaway',
    explainAgainHint: 'Aswan sut’i simiwan willasqayki',
    needHelp: 'Manaraqmi yanapay pisipanwan',
    needHelpHint: 'Ayllumanta huk kamachiq maskasunki',
    understoodTitle: 'Sulpayki. Kutichiyniykiqa qillqasqaña',
    understoodBody: 'Ayllupa kamachiqninkunaqa yachanña willakuyta hap’iqasqaykita.',
    helpTitle: 'Qampaq yanapayta mañakuniku',
    helpBody: 'Imata ayllupa kamachiqnin sectorniykiman asuykamunqa.',
    changeAnswer: 'Kutichiyniyta hukmanyachiy',

    explainTitle: 'Ch’ullalla ch’ullalla willasqayki',
    explainClose: 'Ñam yacharuni, wichqay',

    updating: 'Imatamanta willakuy musuqchakuchkan…',
    staleWarning: 'Manam musuqchayta atikurqachu. Qhipa willakuy rikuchkan.',
    institutionalAccess: 'Kamachikuqkunapaq yaykuna',
    backToCommunity: 'Ayllupa willakuyman kutiy',
    mockLabel: 'Yanqalla willakuy',
  },
}

export const languages = ['es', 'qu']
