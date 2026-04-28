import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAuth } from '../context/AuthContext'

export default function LoginPage() {
  const { login, register } = useAuth()
  const navigate = useNavigate()
  
  // 1. Grab i18n along with t from the hook
  const { t, i18n } = useTranslation() 

  const [isRegister, setIsRegister] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // 2. Add the exact same toggle function we used in the Navbar
  const toggleLanguage = () => {
    const currentLang = i18n?.language || 'en';
    const newLang = currentLang.startsWith('en') ? 'ar' : 'en';
    i18n.changeLanguage(newLang);
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      if (isRegister) {
        await register(email, password)
      } else {
        await login(email, password)
      }
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || t('auth_failed'))
    } finally {
      setLoading(false)
    }
  }

  return (
    // Make sure this wrapper is relative so our absolute button positions correctly
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center p-4 relative">
      
      {/* --- NEW FLOATING LANGUAGE BUTTON --- */}
      <div className="absolute top-6 end-6">
        <button 
          onClick={toggleLanguage}
          className="text-sm font-medium text-slate-600 hover:text-brand-600 bg-white/80 backdrop-blur-md px-4 py-2 rounded-full shadow-sm border border-slate-200 transition-all hover:shadow hover:-translate-y-0.5"
        >
          {t('change_language')}
        </button>
      </div>
      {/* ------------------------------------ */}

      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-12 h-12 bg-brand-600 rounded-xl mb-4 shadow-sm">
            <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-slate-900">{t('srs_analyst')}</h1>
          <p className="text-slate-500 text-sm mt-1">{t('srs_analyst_subtitle')}</p>
        </div>

        <div className="bg-white rounded-2xl shadow-lg border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-800 mb-5 text-start">
            {isRegister ? t('create_account_title') : t('sign_in_title')}
          </h2>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700 text-start">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="text-start">
              <label className="block text-sm font-medium text-slate-700 mb-1">{t('email_label')}</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
                className="w-full border border-slate-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent text-start"
                placeholder={t('email_placeholder')}
                dir="ltr" 
              />
            </div>
            <div className="text-start">
              <label className="block text-sm font-medium text-slate-700 mb-1">{t('password_label')}</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete={isRegister ? 'new-password' : 'current-password'}
                className="w-full border border-slate-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent text-start"
                placeholder={t('password_placeholder')}
                dir="ltr"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 px-4 bg-brand-600 text-white text-sm font-medium rounded-lg hover:bg-brand-700 disabled:opacity-60 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
            >
              {loading && (
                <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
              )}
              {isRegister ? t('create_account_btn') : t('sign_in_btn')}
            </button>
          </form>

          <p className="mt-4 text-center text-sm text-slate-500">
            {isRegister ? t('already_have_account') : t('dont_have_account')}{' '}
            <button
              onClick={() => { setIsRegister(!isRegister); setError(null) }}
              className="text-brand-600 hover:text-brand-700 font-medium ms-1"
            >
              {isRegister ? t('sign_in_btn') : t('register_link')}
            </button>
          </p>
        </div>
      </div>
    </div>
  )
}