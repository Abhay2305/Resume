import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import './styles/globals.css'
import App from './App.jsx'
import { AuthProvider } from './context/AuthContext.jsx'
import { TemplateCatalogProvider } from './context/TemplateCatalogContext.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AuthProvider>
      <TemplateCatalogProvider>
        <App />
      </TemplateCatalogProvider>
    </AuthProvider>
  </StrictMode>,
)
