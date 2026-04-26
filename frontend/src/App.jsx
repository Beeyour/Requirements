import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import InterviewPage from './pages/InterviewPage'
import SRSPage from './pages/SRSPage'
import DiagramViewerPage from './pages/DiagramViewerPage'
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';

function ProtectedRoute() {
  const { isAuthenticated } = useAuth()
  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />
}

function PublicRoute() {
  const { isAuthenticated } = useAuth()
  return isAuthenticated ? <Navigate to="/" replace /> : <Outlet />
}

export default function App() {
  const { i18n } = useTranslation();

  useEffect(() => {
    // Add a safety check: only run if i18n is fully loaded and has the dir() function
    if (i18n && typeof i18n.dir === 'function') {
      document.documentElement.dir = i18n.dir();
      document.documentElement.lang = i18n.language;
    }
  }, [i18n, i18n?.language]);

  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<PublicRoute />}>
            <Route path="/login" element={<LoginPage />} />
          </Route>
          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/project/:id/interview" element={<InterviewPage />} />
            <Route path="/project/:id/srs" element={<SRSPage />} />
            <Route path="/project/:id/diagram/:type" element={<DiagramViewerPage />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
