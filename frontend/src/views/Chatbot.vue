<template>
  <div class="bg-white rounded-2xl border border-slate-200 shadow-sm flex flex-col h-[650px]">
    <div class="border-b border-slate-100 p-4 flex items-center justify-between bg-slate-50 rounded-t-2xl">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 bg-brand-light rounded-xl flex items-center justify-center text-brand-dark text-xl">🤖</div>
        <div>
          <h3 class="font-black text-slate-900">살만해 안심 계약 AI 챗봇</h3>
          <p class="text-[11px] text-slate-500">HUG 126%, 다가구 선순위, 세금 체납 확인 등 계약 전 안전 질문을 답변합니다.</p>
        </div>
      </div>
      <span class="hidden sm:inline text-xs bg-emerald-100 text-emerald-800 px-3 py-1 rounded-full font-black">법률 가이드 연동 시뮬레이터</span>
    </div>

    <div ref="messageArea" class="flex-1 overflow-y-auto p-4 space-y-4">
      <div v-for="(message, index) in store.chatMessages" :key="index" :class="message.role === 'user' ? 'flex justify-end' : 'flex justify-start'">
        <div :class="message.role === 'user' ? 'max-w-[80%] bg-brand text-white p-3 rounded-2xl rounded-tr-none text-sm' : 'max-w-[80%] bg-slate-100 text-slate-800 p-3 rounded-2xl rounded-tl-none text-sm leading-relaxed'">
          <p v-if="message.role === 'bot'" class="font-black text-brand-dark text-xs mb-1">AI 안심계약 위원</p>
          {{ message.text }}
        </div>
      </div>

      <div class="bg-slate-50 border border-slate-100 rounded-2xl p-3 max-w-[80%]">
        <p class="font-bold text-slate-700 text-xs mb-2">💡 자주 묻는 질문</p>
        <div class="flex flex-col gap-1.5">
          <button v-for="question in quickQuestions" :key="question" @click="send(question)" class="text-left text-xs bg-white hover:bg-brand-light text-brand-dark p-2 rounded-lg border border-slate-200 transition font-bold">
            {{ question }}
          </button>
        </div>
      </div>
    </div>

    <form @submit.prevent="send(input)" class="border-t border-slate-100 p-3 bg-slate-50 flex gap-2 rounded-b-2xl">
      <input v-model="input" type="text" placeholder="임대인 세금 체납 확인 서류 등 궁금증을 질문하세요..." class="flex-1 bg-white border border-slate-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-brand" />
      <button class="bg-brand hover:bg-brand-dark text-white px-5 py-3 rounded-xl text-sm font-black shadow-sm transition">전송</button>
    </form>
  </div>
</template>

<script setup>
import { nextTick, ref } from 'vue'
import useMapStore from '../store/mapStore'

const store = useMapStore()
const input = ref('')
const messageArea = ref(null)
const quickQuestions = [
  'HUG 보증보험 가입 기준인 126% 규정이 무엇인가요?',
  '다가구 주택 계약 시 선순위 보증금을 왜 확인해야 하나요?',
  '집주인의 세금 체납 여부는 어떤 서류로 확인하나요?'
]

const send = async (text) => {
  const message = text.trim()
  if (!message) return
  store.sendChat(message)
  input.value = ''
  await nextTick()
  if (messageArea.value) messageArea.value.scrollTop = messageArea.value.scrollHeight
}
</script>
