<template>
  <div class="min-h-screen bg-slate-50 text-slate-800 flex flex-col">
    <header class="bg-white border-b border-slate-200 sticky top-0 z-50 px-4 py-3 shadow-sm">
      <div class="max-w-7xl mx-auto flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div class="flex items-center gap-3 cursor-pointer" @click="$router.push('/')">
          <img src="/salman_symbol_logo.png" alt="살만해 로고" class="w-11 h-11 rounded-xl object-cover bg-brand-light" />
          <div>
            <h1 class="text-xl font-black text-slate-900 tracking-tight flex items-center gap-2">
              살만해
              <span class="text-[11px] bg-brand-light text-brand-dark px-2 py-0.5 rounded-full font-bold">안심 주거 탐색</span>
            </h1>
            <p class="text-xs text-slate-500">실질 치안 통계 · HUG 126% 기준 · 청년 주거 커뮤니티</p>
          </div>
        </div>

        <nav class="flex flex-wrap gap-2 text-sm font-bold">
          <router-link v-for="item in navItems" :key="item.to" :to="item.to" class="px-3 py-2 rounded-xl text-slate-600 hover:bg-slate-100 transition" active-class="bg-brand text-white hover:bg-brand">
            {{ item.icon }} {{ item.label }}
          </router-link>
        </nav>

        <div class="flex items-center gap-3">
          <select v-model="store.currentRegion" @change="store.setRegion(store.currentRegion)" class="bg-slate-100 rounded-xl px-3 py-2 text-xs font-bold focus:outline-none">
            <option v-for="region in store.regions" :key="region.value" :value="region.value">
              {{ region.label }} · {{ region.desc }}
            </option>
          </select>
          <div class="hidden md:flex items-center gap-2 bg-slate-100 rounded-xl px-3 py-2 text-xs font-bold">
            <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span :class="store.regionStatus.tone">{{ store.regionStatus.text }}</span>
          </div>
        </div>
      </div>
    </header>

    <main class="flex-1 max-w-7xl w-full mx-auto p-4">
      <router-view />
    </main>

    <footer class="bg-white border-t border-slate-200 py-4 px-4 text-center">
      <p class="text-xs text-slate-400">© 2026 살만해. 국토교통부 실거래가, 공시가격, 생활안전지도 연동을 가정한 프론트엔드 시뮬레이터.</p>
    </footer>
  </div>
</template>

<script setup>
import useMapStore from './store/mapStore'

const store = useMapStore()
const navItems = [
  { to: '/', label: '매물·치안 탐색', icon: '🗺️' },
  { to: '/diagnosis', label: 'HUG 진단', icon: '🛡️' },
  { to: '/recommend', label: 'AI 추천', icon: '✨' },
  { to: '/chat', label: '계약 챗봇', icon: '🤖' },
  { to: '/community', label: '지역 후기', icon: '💬' }
]
</script>
