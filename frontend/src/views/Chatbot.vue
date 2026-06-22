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
