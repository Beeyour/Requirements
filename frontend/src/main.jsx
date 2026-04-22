import React from 'react'
import ReactDOM from 'react-dom/client'
import './i18n';
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <Suspense fallback={<div className="p-4 text-center">Loading...</div>}>
      <App />
    </Suspense>
  </React.StrictMode>,
)
