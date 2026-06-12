<template>
  <div class="space-y-4">
    <section class="bg-gradient-to-r from-brand to-brand-dark text-white rounded-2xl p-6 shadow-md relative overflow-hidden">
      <div class="absolute right-0 bottom-0 opacity-20 translate-x-10 translate-y-10 text-9xl">✨</div>
      <div class="relative z-10 max-w-2xl">
        <span class="bg-white/20 text-white text-xs px-3 py-1 rounded-full font-black inline-block mb-2">살만해 AI 솔루션</span>
        <h2 class="text-2xl font-black mb-1">종합 치안 등급 & 가성비 맞춤형 매물 추천</h2>
        <p class="text-sm text-emerald-50">CCTV, 조도, 범죄주의구간, HUG 가입 가능성, 교통·생활 편의성을 가중치로 계산합니다.</p>
      </div>
    </section>

    <div class="grid grid-cols-1 md:grid-cols-12 gap-4">
      <aside class="md:col-span-4 bg-white rounded-2xl border border-slate-200 p-4 shadow-sm space-y-4">
        <h3 class="font-black text-slate-900 border-b border-slate-100 pb-2">🎚️ 내 선호도 가중치</h3>
        <div v-for="item in weightItems" :key="item.key">
          <div class="flex justify-between text-xs font-bold text-slate-700 mb-1"><span>{{ item.icon }} {{ item.label }}</span><span class="text-brand-dark">{{ store.weights[item.key] }}%</span></div>
          <input type="range" min="0" max="100" :value="store.weights[item.key]" @input="store.setWeight(item.key, $event.target.value)" class="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-brand" />
        </div>
      </aside>

      <section class="md:col-span-8 space-y-3">
        <article v-for="(property, index) in scoredProperties" :key="property.id" class="bg-white rounded-2xl border border-slate-200 p-4 shadow-sm hover:shadow-md transition flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div class="flex items-center gap-4">
            <div class="w-16 h-16 bg-brand-light border-2 border-brand/30 rounded-2xl flex flex-col items-center justify-center text-brand-dark font-black shrink-0">
              <span class="text-[10px] text-slate-500 font-bold">적합도</span>
              <span class="text-lg">{{ property.finalScore }}%</span>
            </div>
            <div>
              <div class="flex flex-wrap items-center gap-2">
                <span class="bg-brand-light text-brand-dark text-[10px] font-black px-2 py-0.5 rounded-full">AI 추천 {{ index + 1 }}위</span>
                <span class="text-xs text-slate-400">{{ property.address }}</span>
              </div>
              <h4 class="font-black text-slate-950 text-base mt-1">{{ property.name }} <span class="text-xs font-normal text-slate-500">({{ property.type }})</span></h4>
              <p class="text-xs text-slate-600 mt-1">보증금 <b>{{ (property.deposit / 10000).toFixed(1) }}억 / 월세 {{ property.rent }}만원</b> · 치안 {{ property.crimeGrade }} · HUG {{ property.hugEligible ? '가능' : '주의' }}</p>
            </div>
          </div>
          <button @click="selectOnMap(property)" class="bg-brand hover:bg-brand-dark text-white font-black text-xs px-4 py-2.5 rounded-xl transition">위치 확인</button>
        </article>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import useMapStore from '../store/mapStore'

const store = useMapStore()
const router = useRouter()
const weightItems = [
  { key: 'safety', label: '실제 치안/범죄 안전도', icon: '🛡️' },
  { key: 'price', label: '가성비 및 HUG 적합도', icon: '💰' },
  { key: 'traffic', label: '대중교통 인접도', icon: '🚇' },
  { key: 'life', label: '생활 편의성', icon: '☕' }
]

const scoredProperties = computed(() => store.allProperties.map((property) => {
  const hugEligible = property.deposit <= property.publicPrice * 1.26
  const priceScore = hugEligible ? 95 : 30
  const trafficScore = property.id === 3 ? 95 : 70
  const lifeScore = property.region === 'mapo' ? 90 : 75
  const w = store.weights
  const finalScore = Math.round(((property.safetyScore * w.safety) + (priceScore * w.price) + (trafficScore * w.traffic) + (lifeScore * w.life)) / 100)
  return { ...property, hugEligible, finalScore }
}).sort((a, b) => b.finalScore - a.finalScore))

const selectOnMap = (property) => {
  store.setRegion(property.region)
  store.selectProperty(property.id)
  router.push('/')
}
</script>
