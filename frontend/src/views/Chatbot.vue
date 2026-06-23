<template>
  <section class="flex h-[650px] flex-col overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
    <header class="flex flex-col gap-3 border-b border-slate-100 bg-slate-50 p-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h2 class="text-base font-black text-slate-900">계약 법률 AI 상담</h2>
        <p class="mt-1 text-xs leading-5 text-slate-500">
          전월세 계약 전 확정일자, 보증금 회수, 전세사기 피해지원 관련 질문을 확인합니다.
        </p>
      </div>
      <span class="w-fit rounded-lg bg-emerald-100 px-3 py-1 text-xs font-black text-emerald-800">
        법률 RAG 연결
      </span>
    </header>

    <div ref="messageArea" class="flex-1 space-y-4 overflow-y-auto p-4">
      <div
        v-for="(message, index) in store.chatMessages"
        :key="index"
        :class="message.role === 'user' ? 'flex justify-end' : 'flex justify-start'"
      >
        <article
          :class="[
            'max-w-[88%] rounded-lg p-3 text-sm leading-relaxed',
            message.role === 'user'
              ? 'bg-brand text-white'
              : message.isError
                ? 'border border-rose-200 bg-rose-50 text-rose-700'
                : 'bg-slate-100 text-slate-800'
          ]"
        >
          <p v-if="message.role === 'bot'" class="mb-1 text-xs font-black text-brand-dark">
            살만해 계약 AI
          </p>
          <p class="whitespace-pre-line">{{ message.text }}</p>

          <div v-if="message.legalCards?.length" class="mt-3 space-y-2">
            <article
              v-for="card in message.legalCards"
              :key="`${card.lawName}-${card.articleNo}-${card.title}`"
              class="rounded-lg border border-slate-200 bg-white p-3 text-slate-800"
            >
              <div class="flex flex-col gap-1 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <p class="text-xs font-black text-brand-dark">{{ card.lawName }} {{ card.articleNo }}</p>
                  <h3 class="mt-1 text-sm font-black text-slate-900">{{ card.title }}</h3>
                </div>
                <span v-if="card.score !== null" class="w-fit rounded-md bg-slate-100 px-2 py-1 text-[11px] font-bold text-slate-600">
                  {{ Math.round(card.score * 100) }}%
                </span>
              </div>
              <p class="mt-2 text-xs leading-5 text-slate-600">{{ card.content }}</p>
            </article>
          </div>

          <div v-if="message.analysisCards?.length" class="mt-3 space-y-2">
            <article
              v-for="card in message.analysisCards"
              :key="`${card.type}-${card.title}`"
              class="rounded-lg border border-slate-200 bg-white p-3 text-slate-800"
            >
              <div class="flex items-start justify-between gap-3">
                <div class="min-w-0">
                  <p class="text-[11px] font-black tracking-normal text-brand-dark">{{ analysisLabel(card.type) }}</p>
                  <h3 class="mt-1 text-sm font-black text-slate-900">{{ card.title || analysisTitle(card.type) }}</h3>
                </div>
                <span
                  v-if="card.score !== null"
                  :class="[
                    'shrink-0 rounded-md px-2 py-1 text-[11px] font-black',
                    card.type === 'SAFETY' ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-700'
                  ]"
                >
                  {{ card.score }}점
                </span>
              </div>
              <p v-if="card.summary" class="mt-2 text-xs leading-5 text-slate-600">{{ card.summary }}</p>
              <dl v-if="analysisMetricEntries(card).length" class="mt-3 grid grid-cols-2 gap-2">
                <div
                  v-for="metric in analysisMetricEntries(card)"
                  :key="metric.key"
                  class="rounded-md border border-slate-100 bg-slate-50 px-2 py-2"
                >
                  <dt class="text-[11px] font-bold text-slate-500">{{ metric.label }}</dt>
                  <dd class="mt-1 text-xs font-black text-slate-900">{{ metric.value }}</dd>
                </div>
              </dl>
            </article>
          </div>
        </article>
      </div>

      <div v-if="store.isChatLoading" class="flex justify-start">
        <div class="rounded-lg bg-slate-100 px-3 py-2 text-xs font-bold text-slate-500">
          답변을 생성하는 중입니다...
        </div>
      </div>

      <div class="rounded-lg border border-slate-100 bg-slate-50 p-3">
        <p class="mb-2 text-xs font-black text-slate-700">자주 묻는 질문</p>
        <div class="grid gap-2 sm:grid-cols-3">
          <button
            v-for="question in quickQuestions"
            :key="question"
            type="button"
            :disabled="store.isChatLoading"
            class="rounded-lg border border-slate-200 bg-white p-2 text-left text-xs font-bold text-brand-dark transition hover:bg-brand-light disabled:cursor-not-allowed disabled:opacity-60"
            @click="send(question)"
          >
            {{ question }}
          </button>
        </div>
      </div>
    </div>

    <form class="flex gap-2 border-t border-slate-100 bg-slate-50 p-3" @submit.prevent="send(input)">
      <input
        v-model="input"
        type="text"
        :disabled="store.isChatLoading"
        placeholder="예: 확정일자는 언제 받아야 하나요?"
        class="min-w-0 flex-1 rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm outline-none transition focus:border-brand focus:ring-2 focus:ring-brand/20 disabled:bg-slate-100"
      />
      <button
        type="submit"
        :disabled="store.isChatLoading || !input.trim()"
        class="rounded-lg bg-brand px-5 py-3 text-sm font-black text-white shadow-sm transition hover:bg-brand-dark disabled:cursor-not-allowed disabled:opacity-60"
      >
        전송
      </button>
    </form>
  </section>
</template>

<script setup>
import { nextTick, ref } from 'vue'
import useMapStore from '../store/mapStore'

const store = useMapStore()
const input = ref('')
const messageArea = ref(null)
const quickQuestions = [
  '확정일자는 언제 받아야 하나요?',
  '전세 보증금을 돌려받으려면 어떤 순서를 확인해야 하나요?',
  '전세사기 피해지원 특별법은 어떤 경우에 도움이 되나요?'
]

const analysisLabels = {
  PRICE: 'PRICE ANALYSIS',
  SAFETY: 'SAFETY ANALYSIS'
}

const analysisTitles = {
  PRICE: '시세 분석',
  SAFETY: '안전 분석'
}

const metricLabels = {
  selectedPropertyId: '선택 매물',
  comparableTransactionCount: '실거래',
  regionStatCount: '지역 통계',
  buildingStatCount: '건물 통계',
  avgDeposit: '평균 보증금',
  avgMonthlyRent: '평균 월세',
  avgSalePrice: '평균 매매가',
  radius: '반경',
  safetyScore: '안전 점수',
  cctvCount300m: 'CCTV',
  bellCount300m: '비상벨',
  lightCount300m: '보안등',
  policeCount500m: '파출소'
}

const metricOrder = [
  'comparableTransactionCount',
  'avgDeposit',
  'avgMonthlyRent',
  'avgSalePrice',
  'radius',
  'safetyScore',
  'cctvCount300m',
  'bellCount300m',
  'lightCount300m',
  'policeCount500m'
]

const analysisLabel = (type) => analysisLabels[type] || 'ANALYSIS'
const analysisTitle = (type) => analysisTitles[type] || '분석 결과'

const formatWon = (value) => {
  const numberValue = Number(value)
  if (!Number.isFinite(numberValue)) return String(value)
  return `${numberValue.toLocaleString()}원`
}

const formatMetricValue = (key, value) => {
  if (['avgDeposit', 'avgMonthlyRent', 'avgSalePrice'].includes(key)) return formatWon(value)
  if (key === 'radius') return `${value}m`
  if (key === 'safetyScore') return `${value}점`
  if (key === 'comparableTransactionCount' || key === 'regionStatCount' || key === 'buildingStatCount') return `${value}건`
  if (['cctvCount300m', 'bellCount300m', 'lightCount300m', 'policeCount500m'].includes(key)) return `${value}개`
  return String(value)
}

const analysisMetricEntries = (card) => {
  const metrics = card?.metrics && typeof card.metrics === 'object' ? card.metrics : {}
  return metricOrder
    .filter((key) => metrics[key] !== null && metrics[key] !== undefined && metrics[key] !== '')
    .slice(0, 4)
    .map((key) => ({
      key,
      label: metricLabels[key] || key,
      value: formatMetricValue(key, metrics[key])
    }))
}

const scrollToBottom = async () => {
  await nextTick()
  if (messageArea.value) {
    messageArea.value.scrollTop = messageArea.value.scrollHeight
  }
}

const send = async (text) => {
  const message = String(text || '').trim()
  if (!message) return

  input.value = ''
  const response = store.sendChat(message)
  await scrollToBottom()
  await response
  await scrollToBottom()
}
</script>
