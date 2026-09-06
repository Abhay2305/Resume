import { createContext, useContext, useState, useCallback, useEffect, type ReactNode } from 'react'
import { getCurrentAdmin, logoutAdmin } from '../services/api/auth.service'
import type { AdminUser } from '../types/auth'

interface AuthContextType {
  admin: AdminUser | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (token: string, admin: AdminUser) => void
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | null>(null)

const TOKEN_KEY = 'procs_token'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [admin, setAdmin] = useState<AdminUser | null>(null)
  const [token, setToken] = useState<string | null>(() => sessionStorage.getItem(TOKEN_KEY))
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const restoreSession = async () => {
      const storedToken = sessionStorage.getItem(TOKEN_KEY)
      if (!storedToken) {
        setIsLoading(false)
        return
      }

      try {
        const admin = await getCurrentAdmin(storedToken)
        setToken(storedToken)
        setAdmin(admin)
      } catch {
        sessionStorage.removeItem(TOKEN_KEY)
        setToken(null)
        setAdmin(null)
      } finally {
        setIsLoading(false)
      }
    }

    restoreSession()
  }, [])

  const login = useCallback((newToken: string, newAdmin: AdminUser) => {
    sessionStorage.setItem(TOKEN_KEY, newToken)
    setToken(newToken)
    setAdmin(newAdmin)
  }, [])

  const logout = useCallback(async () => {
    try {
      await logoutAdmin()
    } catch {
      // Proceed with local logout even if API call fails
    } finally {
      sessionStorage.removeItem(TOKEN_KEY)
      setToken(null)
      setAdmin(null)
      window.location.href = '/login'
    }
  }, [])

  const value: AuthContextType = {
    admin,
    token,
    isAuthenticated: !!token && !!admin,
    isLoading,
    login,
    logout,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
