'use client'

import { AppProvider, useApp } from '@/src/context/app-context'
import { CommunityPage } from '@/src/screens/community-page'
import { LoginPage } from '@/src/screens/login-page'
import { CoordinationPage } from '@/src/screens/coordination-page'

function CurrentView() {
  const { view, hydrated } = useApp()
  if (!hydrated) return <main className="min-h-screen bg-background" aria-busy="true" />
  if (view === 'login') return <LoginPage />
  if (view === 'coordination') return <CoordinationPage />
  return <CommunityPage />
}

export function AppShell() {
  return <AppProvider><CurrentView /></AppProvider>
}
