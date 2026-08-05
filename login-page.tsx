'use client'

import { useEffect, useState } from 'react'
import { Volume2, Square } from 'lucide-react'
import { useApp } from '@/src/context/app-context'
import type { TranslationKey } from '@/src/data/translations'

export function AudioButton({ textKeys, autoPlay = false }: { textKeys: TranslationKey[]; autoPlay?: boolean }) {
  const { language, t } = useApp()
  const [speaking, setSpeaking] = useState(false)
  const [error, setError] = useState(false)

  const speak = () => {
    if (!('speechSynthesis' in window)) { setError(true); return }
    window.speechSynthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(textKeys.map(t).join('. '))
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

  const stop = () => { window.speechSynthesis.cancel(); setSpeaking(false) }

  useEffect(() => {
    if (autoPlay) speak()
    return () => { if ('speechSynthesis' in window) window.speechSynthesis.cancel() }
    // Auto-play only when explanation is opened.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [autoPlay])

  return (
    <div className="flex flex-col gap-2">
      <button type="button" onClick={speaking ? stop : speak} className="flex min-h-14 w-full items-center justify-center gap-3 rounded-xl border-2 border-primary bg-background px-5 text-lg font-extrabold text-primary transition-colors hover:bg-muted focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-ring/30">
        {speaking ? <Square aria-hidden="true" className="size-5" /> : <Volume2 aria-hidden="true" className="size-6" />}
        {speaking ? t('stopAudio') : t('listenAlert')}
        {speaking && <span className="sr-only">{t('listening')}</span>}
      </button>
      {error && <p role="status" className="text-center text-sm font-medium text-muted-foreground">{t('audioUnavailable')}</p>}
      {language === 'qu' && <p className="text-center text-sm text-muted-foreground">{t('audioValidation')}</p>}
    </div>
  )
}
