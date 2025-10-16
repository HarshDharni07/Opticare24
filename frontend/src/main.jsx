/**
 * Entry Point
 * Purpose: Bootstraps React application and renders <App />.
 * Reference: PROMPT.md → Frontend Global Architecture → Deployment & PWA.
 */

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'react-toastify/dist/ReactToastify.css'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
