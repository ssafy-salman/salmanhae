import { defineStore } from 'pinia'
import { sendChatMessage } from '../api/chat.js'

const STORAGE_KEY = 'salmanhae.chatSessions'
const MAX_SESSIONS = 20

const generateId = () => `sess_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`

const makeSession = () => ({
  id: generateId(),
  title: '새 대화',
  messages: [],
  createdAt: new Date().toISOString(),
})

export const useChatSessionStore = defineStore('chatSession', {
  state: () => ({
    sessions: [],
    currentSessionId: null,
    isChatLoading: false,
    chatError: '',
    _chatRequestSeq: 0,
  }),

  getters: {
    currentSession: (state) =>
      state.sessions.find((s) => s.id === state.currentSessionId) ?? null,
    chatMessages: (state) =>
      state.sessions.find((s) => s.id === state.currentSessionId)?.messages ?? [],
    sessionList: (state) =>
      [...state.sessions].sort((a, b) => b.createdAt.localeCompare(a.createdAt)),
  },

  actions: {
    restoreSessions() {
      try {
        const raw = localStorage.getItem(STORAGE_KEY)
        if (!raw) return
        const parsed = JSON.parse(raw)
        if (Array.isArray(parsed) && parsed.length) {
          this.sessions = parsed.slice(0, MAX_SESSIONS)
          this.currentSessionId = this.sessions[0].id
        }
      } catch {
        // ignore
      }
    },

    _persist() {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(this.sessions.slice(0, MAX_SESSIONS)))
      } catch {
        // ignore
      }
    },

    createSession() {
      const session = makeSession()
      this.sessions.unshift(session)
      this.currentSessionId = session.id
      this._persist()
      return session
    },

    switchSession(id) {
      if (this.sessions.some((s) => s.id === id)) {
        this.currentSessionId = id
      }
    },

    _ensureSession() {
      if (!this.currentSessionId || !this.sessions.some((s) => s.id === this.currentSessionId)) {
        this.createSession()
      }
    },

    _updateTitle(session, firstUserMessage) {
      if (session.title === '새 대화') {
        session.title = firstUserMessage.slice(0, 30) + (firstUserMessage.length > 30 ? '…' : '')
      }
    },

    async sendChat(message, selectedPropertyId = null) {
      const text = String(message || '').trim()
      if (!text || this.isChatLoading) return

      this._ensureSession()
      const session = this.sessions.find((s) => s.id === this.currentSessionId)
      if (!session) return

      const seq = ++this._chatRequestSeq
      session.messages.push({ role: 'user', text })
      this._updateTitle(session, text)
      this._persist()

      this.isChatLoading = true
      this.chatError = ''

      try {
        const response = await sendChatMessage({
          message: text,
          sessionId: session.id,
          selectedPropertyId,
        })
        if (seq !== this._chatRequestSeq) return

        session.messages.push({
          role: 'bot',
          text: response.message,
          intent: response.intent,
          legalCards: response.legalCards,
          analysisCards: response.analysisCards,
          properties: response.properties,
        })
        this._persist()
      } catch (error) {
        if (seq !== this._chatRequestSeq) return
        this.chatError = error.response?.data?.message || 'AI 응답을 불러오지 못했습니다.'
        session.messages.push({
          role: 'bot',
          text: this.chatError,
          isError: true,
          legalCards: [],
          analysisCards: [],
        })
        this._persist()
      } finally {
        if (seq === this._chatRequestSeq) this.isChatLoading = false
      }
    },
  },
})
