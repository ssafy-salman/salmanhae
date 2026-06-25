# Phase 1: chatSessionStore 구현

## 목표
여러 대화 세션을 관리하는 Pinia 스토어를 만들고, mapStore에 있던 chatMessages·chatSessionId를 이관한다.
세션은 localStorage에 영속화하여 새로고침 후에도 유지된다.

## 작업 파일
- `frontend/src/store/chatSessionStore.js` — 신규 생성
- `frontend/src/store/mapStore.js` — chatMessages·chatSessionId·isChatLoading·chatError·chatRequestSeq·sendChat 제거, chatSessionStore 위임으로 교체

## 완료 조건
- [ ] chatSessionStore에서 sessions 배열(id, title, messages, createdAt) 관리
- [ ] currentSessionId로 현재 세션 식별
- [ ] createSession() — 새 빈 세션 생성 후 currentSessionId 전환
- [ ] switchSession(id) — 다른 세션으로 전환
- [ ] addMessage(role, payload) — 현재 세션에 메시지 추가
- [ ] sendChat(message) — mapStore.sendChat 로직을 chatSessionStore로 이관
- [ ] sessions를 localStorage('salmanhae.chatSessions')에 저장·복원
- [ ] mapStore에서 채팅 관련 state/action 제거, chatSessionStore를 re-export

## 아키텍처 규칙 체크
- 비즈니스 로직(sendChat)은 Service 레이어(Store)에만 위치 — Controller(View)는 위임만 한다.
- API 키 하드코딩 금지 (chat.js의 baseURL은 환경변수 사용 중 — 변경 없음).

## 구현 지시

### chatSessionStore.js 구조

```js
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
    sessions: [],           // Session[]
    currentSessionId: null, // string | null
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
```

### mapStore.js 변경

아래 state 필드 제거:
- `chatSessionId`, `chatMessages`, `isChatLoading`, `chatError`, `chatRequestSeq`

아래 action 제거:
- `sendChat`

파일 상단에 주석 한 줄 추가:
```js
// 채팅 관련 state/action은 chatSessionStore로 이관됨
```
