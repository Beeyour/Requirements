import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useTranslation } from 'react-i18next'
// Import the logo. Adjust the relative path if your Navbar isn't in a sibling folder to imgs
import logo from '../imgs/logo.png'

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
    // Changed py-4 to py-2 to reduce the overall height of the navbar
    <nav className="bg-transparent px-6 py-2 flex items-center justify-between">
      
      {/* LEFT: Logo + H1 Title */}
      <div className="flex items-center gap-4">
        <Link to="/" className="hover:opacity-80 transition-opacity">
          <img 
            src={logo} 
            alt={t('srs_analyst', 'SRS Analyst Logo')} 
            className="h-8 w-auto object-contain" 
          />
        </Link>
        
        {/* A subtle vertical divider between logo and title */}
        {projectName && <div className="h-6 w-px bg-slate-300 hidden sm:block"></div>}
        
        <h2 className="text-2xl sm:text-3xl font-bold text-slate-800 tracking-tight truncate max-w-xl">
          {projectName}
        </h2>
      </div>

      {/* RIGHT: Pill Buttons & Email */}
      <div className="flex items-center gap-4">
        
        {/* Translate Button: Pill shape, blue border, fills blue on hover */}
        <button
          onClick={toggleLanguage}
          className="px-4 py-1.5 text-sm font-medium text-brand-600 rounded-full hover:bg-brand-600 hover:text-white transition-all duration-200"
        >
          {t('change_language', 'عربي')}
        </button>

        <span className="text-slate-500 text-sm hidden sm:block">{user?.email}</span>
        
        {/* Sign Out Button: Pill shape, red border, fills red on hover */}
        <button 
          onClick={handleLogout} 
          className="px-4 py-1.5 text-sm font-medium text-red-500 border border-red-500 rounded-full hover:bg-red-500 hover:text-white transition-all duration-200"
        >
          {t('sign_out', 'Sign out')}
        </button>
      </div>
    </nav>
  )
}