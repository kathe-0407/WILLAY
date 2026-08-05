import { AppProvider, useApp } from './context/app-context'
import { CommunityPage } from './screens/community-page'
import { LoginPage } from './screens/login-page'
import { CoordinationPage } from './screens/coordination-page'

function CurrentView() {
  const { view, hydrated } = useApp()
  if (!hydrated) return <main className="min-h-screen bg-background" aria-busy="true" />
  if (view === 'login') return <LoginPage />
  if (view === 'coordination') return <CoordinationPage />
  return <CommunityPage />
}

export default function App() {
  return (
    <AppProvider>
      <CurrentView />
    </AppProvider>
  )
}
