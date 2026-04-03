import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios'
import { refreshToken } from './auth'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const API_PREFIX = `${API_BASE_URL}/api/v1`

export const http: AxiosInstance = axios.create({
  baseURL: API_PREFIX,
})

function getAccessToken() {
  return localStorage.getItem('access_token')
}

function getRefreshToken() {
  return localStorage.getItem('refresh_token')
}

function setAccessToken(token: string) {
  localStorage.setItem('access_token', token)
}

function clearTokens() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}

http.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = getAccessToken()
  if (token) {
    config.headers = config.headers ?? {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

let isRefreshing = false
let pending: Array<(token: string | null) => void> = []

function subscribe(cb: (token: string | null) => void) {
  pending.push(cb)
}

function flush(token: string | null) {
  pending.forEach((cb) => cb(token))
  pending = []
}

http.interceptors.response.use(
  (res) => res,
  async (err: AxiosError) => {
    const original = err.config as any
    const status = err.response?.status

    // Only attempt refresh for authenticated requests.
    if (status !== 401 || !original || original._retry) {
      return Promise.reject(err)
    }

    const refresh = getRefreshToken()
    if (!refresh) {
      clearTokens()
      return Promise.reject(err)
    }

    original._retry = true

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        subscribe((token) => {
          if (!token) return reject(err)
          original.headers = original.headers ?? {}
          original.headers.Authorization = `Bearer ${token}`
          resolve(http(original))
        })
      })
    }

    isRefreshing = true
    try {
      const data = await refreshToken(refresh)
      setAccessToken(data.access)
      flush(data.access)
      original.headers = original.headers ?? {}
      original.headers.Authorization = `Bearer ${data.access}`
      return http(original)
    } catch (refreshErr) {
      clearTokens()
      flush(null)
      return Promise.reject(refreshErr)
    } finally {
      isRefreshing = false
    }
  }
)
