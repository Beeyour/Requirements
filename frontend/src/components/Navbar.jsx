import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useTranslation } from 'react-i18next'

export default function Navbar({ projectName }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const { t, i18n } = useTranslation()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const toggleLanguage = () => {
    const currentLang = i18n?.language || 'en';
    const newLang = currentLang.startsWith('en') ? 'ar' : 'en';
    i18n.changeLanguage(newLang);
  }

  return (
    <nav className="bg-white border-b border-slate-200 px-6 py-3 flex items-center justify-between relative">
      
      {/* LEFT: SRS Analyst (Acts as Back to Dashboard) */}
      <div className="flex-1 flex items-center justify-start">
        <Link to="/" className="font-bold text-brand-600 text-lg tracking-tight hover:text-brand-700 transition-colors">
          {t('srs_analyst')}
        </Link>
      </div>

      {/* CENTER: Project Name (Absolutely centered) */}
      <div className="absolute left-1/2 -translate-x-1/2 font-semibold text-slate-800 hidden sm:block truncate max-w-[40%]">
        {projectName}
      </div>

      {/* RIGHT: Translate, Email, Sign Out */}
      <div className="flex-1 flex items-center justify-end gap-4">
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