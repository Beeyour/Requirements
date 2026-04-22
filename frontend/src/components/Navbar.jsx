import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Navbar({ projectName, backTo, backLabel }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <nav className="bg-white border-b border-slate-200 px-6 py-3 flex items-center justify-between">
      <div className="flex items-center gap-3">
        {backTo && (
          <Link
            to={backTo}
            className="text-slate-500 hover:text-slate-700 text-sm flex items-center gap-1"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            {backLabel || 'Back'}
          </Link>
        )}
        <Link to="/" className="font-bold text-brand-600 text-lg tracking-tight">
          SRS Analyst
        </Link>
        {projectName && (
          <>
            <span className="text-slate-300">/</span>
            <span className="text-slate-700 font-medium text-sm truncate max-w-xs">{projectName}</span>
          </>
        )}
      </div>
      <div className="flex items-center gap-4">
        <span className="text-slate-500 text-sm hidden sm:block">{user?.email}</span>
        <button
          onClick={handleLogout}
          className="text-sm text-slate-600 hover:text-red-600 transition-colors"
        >
          Sign out
        </button>
      </div>
    </nav>
  )
}
