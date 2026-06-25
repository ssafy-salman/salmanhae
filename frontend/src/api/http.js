import axios from 'axios'

const viteEnv = import.meta.env || {}
const baseURL = viteEnv.VITE_API_BASE_URL || 'http://localhost:8080'

const ACCESS_KEY = 'salmanhae.accessToken'
const REFRESH_KEY = 'salmanhae.refreshToken'

const http = axios.create({
  baseURL,
  timeout: 10000,
  headers: {
    Accept: 'application/json'
  }
})

const readAccessToken = () => {
  try {
    if (typeof window === 'undefined' || !window.localStorage) return ''
    return (
      window.localStorage.getItem(ACCESS_KEY) ||
      window.localStorage.getItem('accessToken') ||
      ''
    )
  } catch {
    return ''
  }
}

http.interceptors.request.use((config) => {
  const token = readAccessToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

let isRefreshing = false
let pendingQueue = []

const flushQueue = (error, token = null) => {
  pendingQueue.forEach(({ resolve, reject }) => {
    if (error) reject(error)
    else resolve(token)
  })
  pendingQueue = []
}

http.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config

    if (error.response?.status !== 401 || original._retry) {
      return Promise.reject(error)
    }

    const storedRefresh = localStorage.getItem(REFRESH_KEY)
    if (!storedRefresh) {
      return Promise.reject(error)
    }

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        pendingQueue.push({ resolve, reject })
      }).then((token) => {
        original.headers.Authorization = `Bearer ${token}`
        return http(original)
      })
    }

    original._retry = true
    isRefreshing = true

    try {
      const res = await axios.post(`${baseURL}/api/v1/auth/refresh`, {
        refreshToken: storedRefresh,
      })
      const { accessToken, refreshToken } = res.data.data
      localStorage.setItem(ACCESS_KEY, accessToken)
      localStorage.setItem(REFRESH_KEY, refreshToken)
      http.defaults.headers.common.Authorization = `Bearer ${accessToken}`
      flushQueue(null, accessToken)
      original.headers.Authorization = `Bearer ${accessToken}`
      return http(original)
    } catch (refreshError) {
      flushQueue(refreshError)
      localStorage.removeItem(ACCESS_KEY)
      localStorage.removeItem(REFRESH_KEY)
      window.location.href = '/login'
      return Promise.reject(refreshError)
    } finally {
      isRefreshing = false
    }
  }
)

export default http
