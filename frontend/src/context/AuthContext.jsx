import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { api } from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('finscope_token'))
  const [user, setUser] = useState(null)
  const [ready, setReady] = useState(!localStorage.getItem('finscope_token'))

  useEffect(() => {
    if (!token) {
      setUser(null)
      setReady(true)
      return
    }
    let cancelled = false
    api
      .get('/auth/me')
      .then((response) => {
        if (!cancelled) setUser(response.data)
      })
      .catch(() => {
        if (!cancelled) {
          localStorage.removeItem('finscope_token')
          setToken(null)
          setUser(null)
        }
      })
      .finally(() => {
        if (!cancelled) setReady(true)
      })
    return () => {
      cancelled = true
    }
  }, [token])

  const value = useMemo(
    () => ({
      token,
      user,
      ready,
      login(nextToken) {
        localStorage.setItem('finscope_token', nextToken)
        setReady(false)
        setToken(nextToken)
      },
      logout() {
        localStorage.removeItem('finscope_token')
        setToken(null)
        setUser(null)
      },
    }),
    [token, user, ready],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used inside AuthProvider')
  return context
}
