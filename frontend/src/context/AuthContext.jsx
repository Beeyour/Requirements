import { createContext, useContext, useState, useCallback } from 'react'
import apiClient from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('srs_token'))
  const [user, setUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('srs_user') || 'null')
    } catch {
      return null
    }
  })

  const persist = useCallback((tokenVal, userVal) => {
    setToken(tokenVal)
    setUser(userVal)
    localStorage.setItem('srs_token', tokenVal)
    localStorage.setItem('srs_user', JSON.stringify(userVal))
  }, [])

  const login = useCallback(async (email, password) => {
    const { data } = await apiClient.post('/auth/login', { email, password })
    persist(data.access_token, { id: data.user_id, email: data.email })
  }, [persist])

  const register = useCallback(async (email, password) => {
    const { data } = await apiClient.post('/auth/register', { email, password })
    persist(data.access_token, { id: data.user_id, email: data.email })
  }, [persist])

  const logout = useCallback(() => {
    setToken(null)
    setUser(null)
    localStorage.removeItem('srs_token')
    localStorage.removeItem('srs_user')
  }, [])

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, isAuthenticated: !!token }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
