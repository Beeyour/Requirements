import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useTranslation } from 'react-i18next'

export default function Navbar({ projectName, backTo, backLabel }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const { t, i18n } = useTranslation()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const toggleLanguage = () => {
    // Safely get the language. If it's undefined, pretend it's 'en'
    const currentLang = i18n?.language || 'en';
    
    // Switch between 'ar' and 'en'
    const newLang = currentLang.startsWith('en') ? 'ar' : 'en';
    
    i18n.changeLanguage(newLang);
  }

  return (
    <nav className="bg-white border-b border-slate-200 px-6 py-3 flex items-center justify-between">
      <div className="flex items-center gap-3">
        {backTo && (
          <Link to={backTo} className="text-slate-500 hover:text-slate-700 text-sm flex items-center gap-1">
            {/* Use t() to translate */}
            {t('dashboard')}
          </Link>
        )}
        <Link to="/" className="font-bold text-brand-600 text-lg tracking-tight">
          {t('srs_analyst')}
        </Link>
      </div>

      <div className="flex items-center gap-4">
        {/* Language Switcher Button */}
        <button
          onClick={toggleLanguage}
          className="text-sm font-medium text-brand-600 hover:text-brand-800 transition-colors"
        >
          {t('change_language')}
        </button>

        <span className="text-slate-500 text-sm hidden sm:block">{user?.email}</span>
        <button onClick={handleLogout} className="text-sm text-slate-600 hover:text-red-600 transition-colors">
          {t('sign_out')}
        </button>
      </div>
    </nav>
  )
}