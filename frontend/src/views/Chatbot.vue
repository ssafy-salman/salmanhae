<template>
  <div class="chat-page">
    <div class="chat-outer">

    <!-- Session Sidebar -->
    <div class="chat-sidebar">
      <button class="new-chat-btn" @click="chatStore.newChat()">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        새 대화
      </button>

      <div class="session-list">
        <button
          v-for="session in chatStore.sessionList"
          :key="session.id"
          :class="['session-item', session.id === chatStore.currentSessionId && 'session-item--active']"
          @click="chatStore.switchSession(session.id)"
        >
          <p class="session-item__title">{{ session.title }}</p>
          <p class="session-item__date">{{ formatSessionDate(session.createdAt) }}</p>
        </button>
      </div>
    </div>

    <div class="chat-card">

    <!-- Body -->
    <div ref="messageArea" class="chat-body">

      <!-- Welcome -->
      <template v-if="!chatStore.chatMessages.length">
        <div class="chat-welcome">
          <div class="welcome-orb" />
          <h2 class="welcome-title">안녕하세요!<br /><span class="welcome-accent">무엇이 궁금하신가요?</span></h2>
          <div class="examples__grid">
            <button
              v-for="item in examplePrompts"
              :key="item.text"
              class="example-card"
              :disabled="chatStore.isChatLoading"
              @click="send(item.text)"
            >
              <span class="example-card__icon" v-html="item.icon" />
              <p class="example-card__text">{{ item.text }}</p>
            </button>
          </div>
        </div>
      </template>

      <!-- Messages -->
      <template v-else>
        <div class="date-sep">Today {{ nowTime }}</div>

        <div v-for="(msg, i) in chatStore.chatMessages" :key="i" :class="['msg-group', msg.role === 'user' ? 'msg-group--user' : 'msg-group--bot']">
          <div :class="['msg-bubble', msg.role === 'user' ? 'msg-bubble--user' : 'msg-bubble--bot', msg.isError && 'msg-bubble--error']">
            <p class="msg-text">{{ msg.text }}</p>

            <div v-if="msg.properties?.length" class="card-list">
              <div
                v-for="prop in msg.properties"
                :key="prop.id"
                class="property-card"
                @click="store.selectProperty && store.selectProperty(prop)"
              >
                <div class="property-card__head">
                  <div class="property-card__info">
                    <p class="info-card__tag">{{ propTypeLabel(prop.property_type) }} · {{ txTypeLabel(prop.transaction_type) }}</p>
                    <h4 class="info-card__title">{{ prop.building_name || prop.title }}</h4>
                    <p class="property-card__address">{{ prop.address }}</p>
                  </div>
                  <p class="property-card__price">{{ formatPropertyPrice(prop) }}</p>
                </div>
                <div v-if="prop.area_m2 || prop.floor" class="property-card__meta">
                  <span v-if="prop.area_m2">{{ prop.area_m2 }}㎡</span>
                  <span v-if="prop.floor">{{ prop.floor }}층</span>
                </div>
              </div>
            </div>

            <div v-if="msg.legalCards?.length" class="card-list">
              <div v-for="card in msg.legalCards" :key="`${card.lawName}-${card.articleNo}`" class="info-card">
                <div class="info-card__head">
                  <div>
                    <p class="info-card__tag">{{ card.lawName }} {{ card.articleNo }}</p>
                    <h4 class="info-card__title">{{ card.title }}</h4>
                  </div>
                  <span v-if="card.score !== null" class="info-card__score">{{ Math.round(card.score * 100) }}%</span>
                </div>
                <p class="info-card__body">{{ card.content }}</p>
              </div>
            </div>

            <div v-if="msg.analysisCards?.length" class="card-list">
              <div v-for="card in msg.analysisCards" :key="`${card.type}-${card.title}`" class="info-card">
                <div class="info-card__head">
                  <div>
                    <p class="info-card__tag">{{ analysisLabel(card.type) }}</p>
                    <h4 class="info-card__title">{{ card.title || analysisTitle(card.type) }}</h4>
                  </div>
                  <span v-if="card.score !== null" class="info-card__score">{{ card.score }}점</span>
                </div>
                <p v-if="card.summary" class="info-card__body">{{ card.summary }}</p>
                <dl v-if="analysisMetricEntries(card).length" class="info-card__metrics">
                  <div v-for="m in analysisMetricEntries(card)" :key="m.key" class="metric-item">
                    <dt>{{ m.label }}</dt><dd>{{ m.value }}</dd>
                  </div>
                </dl>
              </div>
            </div>

            <div v-if="msg.role === 'bot'" class="msg-actions">
              <button class="action-btn" title="다시 생성" v-html="iconRefresh" />
              <button class="action-btn" title="복사" v-html="iconCopy" />
              <button class="action-btn" title="공유" v-html="iconShare" />
              <button class="action-btn" title="저장" v-html="iconBookmark" />
            </div>
          </div>
        </div>

        <div v-if="chatStore.isChatLoading" class="msg-group msg-group--bot">
          <div class="msg-bubble msg-bubble--bot">
            <div class="loading-dots"><span /><span /><span /></div>
          </div>
        </div>
      </template>
    </div>

    <!-- Input -->
    <div class="input-wrap">
      <div class="input-card">
        <div class="input-row">
          <textarea
            ref="textarea"
            v-model="input"
            class="input-field"
            placeholder="질문하거나 요청을 입력하세요..."
            rows="1"
            @keydown.enter.exact.prevent="send(input)"
            @input="autoResize"
          />
        </div>
        <div class="input-toolbar">
          <div class="toolbar-left">
            <button class="toolbar-btn" title="파일 첨부" v-html="iconAttach" />
            <button class="toolbar-btn" title="이미지" v-html="iconImage" />
            <button class="toolbar-btn" title="문서" v-html="iconDoc" />
            <button class="toolbar-btn" title="링크" v-html="iconLink" />
          </div>
          <button
            class="send-btn"
            :disabled="chatStore.isChatLoading || !input.trim()"
            @click="send(input)"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/>
            </svg>
          </button>
        </div>
      </div>
    </div>

    </div><!-- /chat-card -->
    </div><!-- /chat-outer -->
  </div>
</template>

<script setup>
import { nextTick, ref } from 'vue'
import useMapStore from '../store/mapStore'
import { useChatSessionStore } from '../store/chatSessionStore.js'

const store = useMapStore()
const chatStore = useChatSessionStore()
const input = ref('')
const messageArea = ref(null)
const textarea = ref(null)

const nowTime = new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })

const iconUser     = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>`
const iconBot      = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="5" r="2"/><path d="M12 7v4"/><line x1="8" y1="16" x2="8" y2="16"/><line x1="16" y1="16" x2="16" y2="16"/></svg>`
const iconRefresh  = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 .49-4.61"/></svg>`
const iconCopy     = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>`
const iconShare    = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>`
const iconBookmark = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>`
const iconBold     = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M6 4h8a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z"/><path d="M6 12h9a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z"/></svg>`
const iconItalic   = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="4" x2="10" y2="4"/><line x1="14" y1="20" x2="5" y2="20"/><line x1="15" y1="4" x2="9" y2="20"/></svg>`
const iconStrike   = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M17.3 12H21"/><path d="M3 12h4.7"/><path d="M7.7 12c-.2-.5-.3-1-.3-1.5C7.4 8 9.5 6 12 6s4.6 2 4.6 4.5c0 .5-.1 1-.3 1.5"/><path d="M6.4 17c.6 1.8 2.5 3 5.6 3 3.5 0 5.6-1.8 5.6-4.5 0-.5-.1-1-.3-1.5"/></svg>`
const iconLink     = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>`
const iconList     = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>`
const iconAttach   = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>`
const iconImage    = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>`

const iconDoc  = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>`
const iconKey  = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"/></svg>`
const iconMap  = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"/><line x1="8" y1="2" x2="8" y2="18"/><line x1="16" y1="6" x2="16" y2="22"/></svg>`
const iconChat2= `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>`

const examplePrompts = [
  { text: '확정일자는 언제 받아야 하나요?', icon: iconDoc },
  { text: '전세 보증금을 돌려받으려면 어떤 순서를 확인해야 하나요?', icon: iconKey },
  { text: '이 지역의 안전 점수는 어떻게 확인하나요?', icon: iconMap },
  { text: '전세사기 피해지원 특별법은 어떤 경우에 도움이 되나요?', icon: iconChat2 },
]

const propTypeLabels = {
  ONE_ROOM: '원룸', OFFICETEL: '오피스텔', VILLA: '빌라',
  APARTMENT: '아파트', MULTI_FAMILY: '다가구',
}
const txTypeLabels = { MONTHLY_RENT: '월세', JEONSE: '전세', SALE: '매매' }
const propTypeLabel = (t) => propTypeLabels[t] || t || ''
const txTypeLabel = (t) => txTypeLabels[t] || t || ''
const formatPropertyPrice = (prop) => {
  const tx = prop.transaction_type
  if (tx === 'MONTHLY_RENT') return `${Number(prop.deposit || 0).toLocaleString()}/${Number(prop.monthly_rent || 0).toLocaleString()}만`
  if (tx === 'JEONSE') return `전세 ${Number(prop.deposit || 0).toLocaleString()}만`
  if (tx === 'SALE') return `매매 ${Number(prop.price || 0).toLocaleString()}만`
  return ''
}

const analysisLabels = { PRICE: 'PRICE ANALYSIS', SAFETY: 'SAFETY ANALYSIS' }
const analysisTitles = { PRICE: '시세 분석', SAFETY: '안전 분석' }
const metricLabels = {
  selectedPropertyId: '선택 매물', comparableTransactionCount: '실거래',
  regionStatCount: '지역 통계', buildingStatCount: '건물 통계',
  avgDeposit: '평균 보증금', avgMonthlyRent: '평균 월세',
  avgSalePrice: '평균 매매가', radius: '반경',
  safetyScore: '안전 점수', cctvCount300m: 'CCTV',
  bellCount300m: '비상벨', lightCount300m: '보안등', policeCount500m: '파출소'
}
const metricOrder = [
  'comparableTransactionCount','avgDeposit','avgMonthlyRent','avgSalePrice',
  'radius','safetyScore','cctvCount300m','bellCount300m','lightCount300m','policeCount500m'
]
const analysisLabel = (t) => analysisLabels[t] || 'ANALYSIS'
const analysisTitle = (t) => analysisTitles[t] || '분석 결과'
const formatWon = (v) => { const n = Number(v); return Number.isFinite(n) ? `${n.toLocaleString()}원` : String(v) }
const formatMetricValue = (k, v) => {
  if (['avgDeposit','avgMonthlyRent','avgSalePrice'].includes(k)) return formatWon(v)
  if (k === 'radius') return `${v}m`; if (k === 'safetyScore') return `${v}점`
  if (['comparableTransactionCount','regionStatCount','buildingStatCount'].includes(k)) return `${v}건`
  if (['cctvCount300m','bellCount300m','lightCount300m','policeCount500m'].includes(k)) return `${v}개`
  return String(v)
}
const analysisMetricEntries = (card) => {
  const m = card?.metrics && typeof card.metrics === 'object' ? card.metrics : {}
  return metricOrder.filter((k) => m[k] !== null && m[k] !== undefined && m[k] !== '').slice(0, 4)
    .map((k) => ({ key: k, label: metricLabels[k] || k, value: formatMetricValue(k, m[k]) }))
}

const formatSessionDate = (iso) => {
  const d = new Date(iso)
  const diffDays = Math.floor((Date.now() - d) / 86400000)
  if (diffDays === 0) return '오늘'
  if (diffDays === 1) return '어제'
  if (diffDays < 7) return `${diffDays}일 전`
  return d.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' })
}

const autoResize = () => {
  if (!textarea.value) return
  textarea.value.style.height = 'auto'
  textarea.value.style.height = Math.min(textarea.value.scrollHeight, 140) + 'px'
}
const scrollToBottom = async () => {
  await nextTick()
  if (messageArea.value) messageArea.value.scrollTop = messageArea.value.scrollHeight
}
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
</script>

<style scoped>
.chat-page {
  height: calc(100vh - 56px);
  background: linear-gradient(to top, rgba(1, 191, 166, 0.1) 0%, #ffffff 45%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px 40px;
}

.chat-outer {
  width: 100%;
  max-width: 1100px;
  flex: 1;
  min-height: 0;
  display: flex;
  padding: 7px;
  gap: 7px;
  border-radius: 24px;
  background: linear-gradient(to bottom, #F1F7F6 0%, #E3F2F0 100%);
  border: 1px solid #e9e9eb;
  box-shadow: 0 40px 80px 20px rgba(233, 240, 238, 0.25);
}

/* Sidebar */
.chat-sidebar {
  width: 200px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 8px 6px;
  overflow: hidden;
}

.new-chat-btn {
  display: flex;
  align-items: center;
  gap: 7px;
  width: 100%;
  padding: 10px 13px;
  background: #ffffff;
  border: 1px solid #e9e9eb;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
  color: #111827;
  cursor: pointer;
  transition: border-color 0.13s, color 0.13s;
  flex-shrink: 0;
}
.new-chat-btn svg { width: 14px; height: 14px; flex-shrink: 0; }
.new-chat-btn:hover { border-color: #01bfa6; color: #01bfa6; }

.session-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.session-list::-webkit-scrollbar { width: 3px; }
.session-list::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 3px; }

.session-item {
  width: 100%;
  padding: 9px 11px;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 10px;
  text-align: left;
  cursor: pointer;
  transition: background 0.12s, border-color 0.12s;
}
.session-item:hover { background: #D8E9E7; }
.session-item--active {
  background: #D8E9E7;
  border-color: transparent;
}
.session-item--active .session-item__title {
  color: #1a3d3a;
}
.session-item--active .session-item__date {
  color: #5a8480;
}
.session-item__title {
  font-size: 12.5px;
  font-weight: 500;
  color: #111827;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin: 0;
}
.session-item__date {
  font-size: 11px;
  color: #9ca3af;
  margin: 3px 0 0;
}

.chat-card {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: #ffffff;
  border-radius: 20px;
  border: 1px solid #e9e9eb;
  overflow: hidden;
}

/* Body */
.chat-body {
  flex: 1;
  overflow-y: auto;
  width: 100%;
  padding: 32px 32px 20px;
  display: flex;
  flex-direction: column;
  gap: 28px;
}

/* Welcome */
.chat-welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  text-align: center;
  padding-top: 40px;
}
.welcome-orb {
  width: 64px; height: 64px; border-radius: 50%;
  background: radial-gradient(circle at 35% 35%, #5eead4, #01bfa6 60%, #019c87);
  box-shadow: 0 8px 28px rgba(1, 191, 166, 0.3);
}
.welcome-title {
  font-size: 28px; font-weight: 700; color: #0d1110;
  line-height: 1.3; letter-spacing: -0.02em;
}
.welcome-accent { color: #01bfa6; }

.examples__grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 10px; width: 100%; max-width: 560px;
}
.example-card {
  display: flex; flex-direction: column; align-items: flex-start; gap: 12px;
  padding: 16px; background: #fff; border: 1.5px solid #e5e7eb;
  border-radius: 14px; text-align: left; cursor: pointer;
  transition: border-color 0.13s, box-shadow 0.13s;
}
.example-card:hover:not(:disabled) { border-color: #01bfa6; box-shadow: 0 2px 12px rgba(1,191,166,0.1); }
.example-card:disabled { opacity: 0.45; cursor: not-allowed; }
.example-card__icon { color: #01bfa6; display: flex; }
.example-card__icon :deep(svg) { width: 18px; height: 18px; }
.example-card__text { font-size: 13px; font-weight: 500; color: #374151; line-height: 1.5; }

/* Date separator */
.date-sep {
  text-align: center; font-size: 11px; font-weight: 500;
  color: #9ca3af; letter-spacing: 0.02em;
}

/* Message group */
.msg-group { display: flex; }
.msg-group--user { justify-content: flex-end; }
.msg-group--bot  { justify-content: flex-start; }

.msg-bubble {
  max-width: 72%;
  padding: 12px 16px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.7;
}
.msg-bubble--user {
  background: #F5F6F6;
  color: #1f2937;
  border: 1px solid #e9e9eb;
  border-bottom-right-radius: 4px;
}
.msg-bubble--bot {
  background: #ffffff;
  color: #1f2937;
  border: 1px solid #e9e9eb;
  border-bottom-left-radius: 4px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.msg-bubble--error { background: #fef2f2; color: #dc2626; border-color: #fecaca; }
.msg-text { white-space: pre-line; }

/* Message actions */
.msg-actions {
  display: flex; align-items: center; gap: 2px; margin-top: 8px; padding-top: 6px; border-top: 1px solid #f3f4f6;
}
.action-btn {
  width: 30px; height: 30px; display: flex; align-items: center; justify-content: center;
  border: none; background: none; border-radius: 7px;
  color: #9ca3af; cursor: pointer; transition: background 0.13s, color 0.13s;
}
.action-btn :deep(svg) { width: 14px; height: 14px; }
.action-btn:hover { background: #f0fdf9; color: #01bfa6; }

/* Loading */
.loading-dots { display: flex; gap: 5px; padding: 6px 0; }
.loading-dots span {
  width: 6px; height: 6px; border-radius: 50%; background: #a7f3d0;
  animation: bounce 1.2s infinite ease-in-out;
}
.loading-dots span:nth-child(2) { animation-delay: 0.2s; }
.loading-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce { 0%,80%,100%{transform:translateY(0)}40%{transform:translateY(-6px)} }

/* Property cards */
.property-card {
  background: #fff; border: 1px solid #e5e7eb; border-radius: 10px;
  padding: 12px; cursor: pointer; transition: border-color 0.13s, box-shadow 0.13s;
}
.property-card:hover { border-color: #01bfa6; box-shadow: 0 2px 8px rgba(1,191,166,0.1); }
.property-card__head { display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; }
.property-card__info { flex: 1; min-width: 0; }
.property-card__address { font-size: 11px; color: #9ca3af; margin: 2px 0 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.property-card__price { font-size: 13px; font-weight: 700; color: #01bfa6; white-space: nowrap; flex-shrink: 0; }
.property-card__meta { display: flex; gap: 8px; margin-top: 6px; }
.property-card__meta span { font-size: 11px; color: #6b7280; background: #f3f4f6; padding: 2px 7px; border-radius: 4px; }

/* Info cards */
.card-list { margin-top: 10px; display: flex; flex-direction: column; gap: 8px; }
.info-card { background: #fff; border: 1px solid #e5e7eb; border-radius: 10px; padding: 12px; }
.info-card__head { display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; margin-bottom: 6px; }
.info-card__tag { font-size: 11px; font-weight: 700; color: #01bfa6; margin-bottom: 3px; }
.info-card__title { font-size: 13px; font-weight: 700; color: #111827; }
.info-card__score { font-size: 11px; font-weight: 600; background: #ccfbf1; color: #01bfa6; padding: 3px 8px; border-radius: 6px; flex-shrink: 0; }
.info-card__body { font-size: 12px; line-height: 1.6; color: #6b7280; }
.info-card__metrics { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-top: 8px; }
.metric-item { background: #f9fafb; border: 1px solid #f0f0f0; border-radius: 7px; padding: 7px 10px; }
.metric-item dt { font-size: 10px; font-weight: 600; color: #9ca3af; margin-bottom: 2px; }
.metric-item dd { font-size: 12px; font-weight: 700; color: #111827; }

/* Input */
.input-wrap {
  flex-shrink: 0;
  padding: 0 20px 20px;
}
.input-card {
  background: #fff;
  border: 1.5px solid #e9e9eb;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 24px rgba(0,0,0,0.07);
  transition: border-color 0.15s, box-shadow 0.15s;
}
.input-card:focus-within {
  border-color: #99f6e4;
  box-shadow: 0 4px 24px rgba(1,191,166,0.1);
}

.input-row {
  padding: 18px 20px 14px;
}
.input-field {
  width: 100%; min-height: 22px; max-height: 140px;
  border: none; background: transparent; outline: none; resize: none;
  font-size: 14.5px; font-weight: 400; color: #111827;
  font-family: inherit; line-height: 1.6;
}
.input-field::placeholder { color: #c2c7c5; }

.input-toolbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 16px;
  border-top: 1px solid #f3f4f6;
}
.toolbar-left { display: flex; align-items: center; gap: 6px; }
.toolbar-btn {
  width: 36px; height: 36px; display: flex; align-items: center; justify-content: center;
  border: none; background: none; border-radius: 10px;
  color: #6b7280; cursor: pointer; transition: background 0.13s, color 0.13s;
}
.toolbar-btn :deep(svg) { width: 20px; height: 20px; }
.toolbar-btn:hover { background: #f0fdf9; color: #01bfa6; }

.send-btn {
  height: 44px; padding: 0 24px;
  display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #5eead4 0%, #01bfa6 50%, #0891b2 100%);
  color: #fff; border: none; border-radius: 999px; cursor: pointer;
  transition: opacity 0.13s, box-shadow 0.13s;
  box-shadow: 0 4px 16px rgba(1,191,166,0.4);
}
.send-btn svg { width: 18px; height: 18px; }
.send-btn:hover:not(:disabled) { opacity: 0.88; }
.send-btn:disabled { opacity: 0.3; cursor: not-allowed; box-shadow: none; }
</style>
