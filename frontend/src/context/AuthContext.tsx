import React, { createContext, useContext, useEffect, useMemo, useState } from 'react'
import * as authApi from '../api/auth'

export type User = {
  id: number
  email: string
  first_name: string
  last_name: string
  role: string
  twofa_enabled: boolean
  permissions: string[]
}

type AuthContextValue = {
  user: User | null
  loading: boolean
  login: (email: string, password: string, otp?: string, backup_code?: string) => Promise<void>
  logout: () => void
  reload: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

function setTokens(access: string, refresh: string) {
  localStorage.setItem('access_token', access)
  localStorage.setItem('refresh_token', refresh)
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  const reload = async () => {
    const access = localStorage.getItem('access_token')
    if (!access) {
      setUser(null)
      return
    }
    try {
      const me = await authApi.me()
      setUser((prev) => {
        if (!prev) return me
        if (JSON.stringify(prev) === JSON.stringify(me)) return prev
        return me
      })
    } catch {
      setUser(null)
    }
  }

  useEffect(() => {
    ; (async () => {
      try {
        await reload()
      } finally {
        setLoading(false)
      }
    })()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const login = async (email: string, password: string, otp?: string, backup_code?: string) => {
    const tokens = await authApi.login(email, password, otp, backup_code)
    setTokens(tokens.access, tokens.refresh)
    await reload()
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setUser(null)
  }

  const value = useMemo<AuthContextValue>(
    () => ({ user, loading, login, logout, reload }),
    [user, loading]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}

export function roleIn(user: User | null, roles: string[]) {
  return !!user && roles.includes(user.role)
}

export function userDisplayName(user: User | null) {
  if (!user) return ''
  const name = `${user.first_name ?? ''} ${user.last_name ?? ''}`.trim()
  return name || user.email
}
