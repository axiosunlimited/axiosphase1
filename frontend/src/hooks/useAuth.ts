import { useEffect, useState } from 'react'
import * as authApi from '../api/auth'

export type User = {
  id: number
  email: string
  first_name: string
  last_name: string
  role: string
  twofa_enabled: boolean
}

export function useAuth() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  async function loadMe() {
    const access = localStorage.getItem('access_token')
    if (!access) {
      setUser(null)
      setLoading(false)
      return
    }
    try {
      const me = await authApi.me()
      setUser(me)
    } catch {
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadMe()
  }, [])

  return { user, setUser, loading, reload: loadMe }
}
