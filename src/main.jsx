import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import '@fontsource/geist/400.css'
import '@fontsource/geist/600.css'
import '@fontsource/geist/700.css'
import '@fontsource/geist/900.css'
import '@fontsource/lora/700.css'
import '@fontsource/lora/700-italic.css'
import App from './App'
import './styles.css'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
