import { defineStore } from 'pinia'
import { login as apiLogin, logout as apiLogout, signup as apiSignup } from '../api/auth.js'

const ACCESS_KEY = 'salmanhae.accessToken'
const REFRESH_KEY = 'salmanhae.refreshToken'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    accessToken: '',
    refreshToken: '',
  }),

  getters: {
    isLoggedIn: (state) => !!state.accessToken,
  },

  actions: {
    restoreSession() {
      this.accessToken = localStorage.getItem(ACCESS_KEY) || ''
      this.refreshToken = localStorage.getItem(REFRESH_KEY) || ''
    },

    _saveTokens(accessToken, refreshToken) {
      this.accessToken = accessToken
      this.refreshToken = refreshToken
      localStorage.setItem(ACCESS_KEY, accessToken)
      localStorage.setItem(REFRESH_KEY, refreshToken)
    },

    _clearTokens() {
      this.user = null
      this.accessToken = ''
      this.refreshToken = ''
      localStorage.removeItem(ACCESS_KEY)
      localStorage.removeItem(REFRESH_KEY)
    },

    async login(email, password) {
      const res = await apiLogin(email, password)
      const { accessToken, refreshToken } = res.data.data
      this._saveTokens(accessToken, refreshToken)
    },

    async logout() {
      try {
        await apiLogout()
      } finally {
        this._clearTokens()
      }
    },

    async signup(email, password, nickname) {
      await apiSignup(email, password, nickname)
    },
  },
})
