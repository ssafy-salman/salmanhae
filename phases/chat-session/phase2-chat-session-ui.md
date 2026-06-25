# Phase 2: Chatbot.vue 세션 UI

## 목표
Chatbot.vue에 세션 사이드바를 추가한다.
왼쪽에 "새 대화" 버튼과 최근 대화 목록이 표시되고,
오른쪽에 현재 세션의 대화 내용이 표시된다.

## 의존 Phase
- Phase 1 (chatSessionStore) 완료 필요

## 작업 파일
- `frontend/src/views/Chatbot.vue` — 세션 사이드바 + chatSessionStore 연동
- `frontend/src/main.js` — chatSessionStore.restoreSessions() 호출 추가

## 완료 조건
- [ ] chat-outer 내부에 세션 사이드바(chat-sidebar)가 추가됨
- [ ] 사이드바에 "새 대화" 버튼 — 클릭 시 createSession() 호출
- [ ] 사이드바에 세션 목록 — 제목·날짜 표시, 클릭 시 switchSession(id) 호출
- [ ] 현재 세션 항목에 active 스타일 적용
- [ ] 대화 영역은 chatSessionStore.chatMessages 기반으로 렌더링
- [ ] send() 함수에서 mapStore.sendChat → chatSessionStore.sendChat 호환
- [ ] main.js에서 앱 시작 시 chatSessionStore.restoreSessions() 호출

## 아키텍처 규칙 체크
- View는 입력 검증과 스토어 위임만 한다 — 비즈니스 로직 금지.
- UI Guide: 흰 배경, 둥근 패널, 낮은 대비 라인 유지.

## 구현 지시

### 레이아웃 변경

chat-outer에 flex 방향 유지, 사이드바를 왼쪽에 추가:

```
┌─────────────────────────────────────────────────────────┐
│ chat-outer (flex row, padding 7px, border-radius 24px)  │
│  ┌──────────────┐  ┌──────────────────────────────────┐ │
│  │ chat-sidebar │  │ chat-card                        │ │
│  │ w:220px      │  │ flex:1                           │ │
│  │              │  │ (기존 대화 영역)                   │ │
│  │ [+ 새 대화]  │  │                                  │ │
│  │ ─────────    │  │                                  │ │
│  │ 세션1        │  │                                  │ │
│  │ 세션2        │  │                                  │ │
│  └──────────────┘  └──────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### chat-sidebar CSS 가이드
- background: transparent (chat-outer의 F1F7F6~E3F2F0 그라데이션 그대로 보임)
- width: 220px, flex-shrink: 0
- padding: 12px 8px
- display: flex, flex-direction: column, gap: 6px

### 새 대화 버튼
```
background: #ffffff
border: 1px solid #e9e9eb
border-radius: 12px
padding: 10px 14px
font-size: 13px, font-weight: 600, color: #111827
hover: border-color #01bfa6, color #01bfa6
```

### 세션 항목
```
border-radius: 10px
padding: 10px 12px
cursor: pointer
background: transparent
hover: background #ffffff80

active (currentSessionId 일치):
  background: #ffffff
  border: 1px solid #e9e9eb

제목: font-size 13px, font-weight 500, color #111827, 1줄 말줄임
날짜: font-size 11px, color #9ca3af, margin-top 3px
```

### 날짜 포맷 함수
```js
const formatSessionDate = (iso) => {
  const d = new Date(iso)
  const now = new Date()
  const diffMs = now - d
  const diffDays = Math.floor(diffMs / 86400000)
  if (diffDays === 0) return '오늘'
  if (diffDays === 1) return '어제'
  if (diffDays < 7) return `${diffDays}일 전`
  return d.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' })
}
```

### script setup 변경
```js
import { useChatSessionStore } from '../store/chatSessionStore.js'
import useMapStore from '../store/mapStore.js'

const store = useMapStore()       // 지도 관련 state만 사용
const chatStore = useChatSessionStore()

// send 함수
const send = async (text) => {
  const message = String(text || '').trim()
  if (!message) return
  input.value = ''
  await nextTick()
  if (textarea.value) textarea.value.style.height = 'auto'
  const response = chatStore.sendChat(message, store.selectedPropertyId)
  await scrollToBottom()
  await response
  await scrollToBottom()
}
```

template에서 `store.chatMessages` → `chatStore.chatMessages`,
`store.isChatLoading` → `chatStore.isChatLoading` 으로 교체.

### main.js 추가
```js
import { useChatSessionStore } from './store/chatSessionStore.js'
// app.mount('#app') 직전에:
useChatSessionStore().restoreSessions()
```
