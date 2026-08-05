import { useEffect, useRef, useState } from 'react'
import { Volume2, Square } from 'lucide-react'
import { useApp } from '../context/app-context'

/**
 * Lee en voz alta los textos recibidos. Acepta claves de traducción
 * y también frases ya construidas con datos reales de la predicción.
 */
export function AudioButton({ texts = [], autoPlay = false }) {
  const { language, t } = useApp()
  const [speaking, setSpeaking] = useState(false)
  const [error, setError] = useState(false)
  const phrasesRef = useRef(texts)
  phrasesRef.current = texts

  const speak = () => {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
      setError(true)
      return
    }
    window.speechSynthesis.cancel()

    const message = phrasesRef.current
      .map(item => (translationsHas(t, item) ? t(item) : item))
      .filter(Boolean)
      .join('. ')

    const utterance = new SpeechSynthesisUtterance(message)
    utterance.lang = language === 'es' ? 'es-PE' : 'qu-PE'
    const voices = window.speechSynthesis.getVoices()
    const voice = voices.find(item => item.lang.toLowerCase().startsWith(language === 'es' ? 'es' : 'qu'))
    if (voice) utterance.voice = voice
    utterance.rate = 0.88
    utterance.onstart = () => setSpeaking(true)
    utterance.onend = () => setSpeaking(false)
    utterance.onerror = () => { setSpeaking(false); setError(true) }
    window.speechSynthesis.speak(utterance)
  }

  const stop = () => {
    if ('speechSynthesis' in window) window.speechSynthesis.cancel()
    setSpeaking(false)
  }

  useEffect(() => {
    if (autoPlay) speak()
    return () => {
      if (typeof window !== 'undefined' && 'speechSynthesis' in window) window.speechSynthesis.cancel()
    }
    // Solo al abrir la explicación.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [autoPlay])

  return (
    <div className="flex flex-col gap-2">
      <button
        type="button"
        onClick={speaking ? stop : speak}
        className="flex min-h-14 w-full items-center justify-center gap-3 rounded-xl border-2 border-primary bg-card px-5 text-lg font-extrabold text-primary transition-colors hover:bg-muted"
      >
        {speaking ? <Square aria-hidden="true" className="size-5" /> : <Volume2 aria-hidden="true" className="size-6" />}
        {speaking ? t('stopAudio') : t('listenAlert')}
        {speaking && <span className="sr-only">{t('listening')}</span>}
      </button>
      {error && (
        <p role="status" className="text-center text-sm font-medium text-muted-foreground">{t('audioUnavailable')}</p>
      )}
      {language === 'qu' && (
        <p className="text-center text-sm text-muted-foreground">{t('audioValidation')}</p>
      )}
    </div>
  )
}

/** Detecta si el texto recibido es una clave de traducción conocida. */
function translationsHas(t, key) {
  return typeof key === 'string' && !key.includes(' ') && t(key) !== key
}
