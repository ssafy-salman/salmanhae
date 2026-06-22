import axios from 'axios'

const viteEnv = import.meta.env || {}
const baseURL = viteEnv.VITE_API_BASE_URL || 'http://localhost:8080'

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
      window.localStorage.getItem('accessToken') ||
      window.localStorage.getItem('salmanhae.accessToken') ||
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

export default http
