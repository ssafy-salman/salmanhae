import http from './http.js'

export const sendVerificationEmail = (email) =>
  http.post('/api/v1/auth/email/send', { email })

export const verifyEmail = (email, code) =>
  http.post('/api/v1/auth/email/verify', { email, code })

export const signup = (email, password, nickname) =>
  http.post('/api/v1/auth/signup', { email, password, nickname })

export const login = (email, password) =>
  http.post('/api/v1/auth/login', { email, password })

export const logout = () =>
  http.post('/api/v1/auth/logout')

export const refresh = (refreshToken) =>
  http.post('/api/v1/auth/refresh', { refreshToken })
