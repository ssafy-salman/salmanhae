<template>
  <div class="grid grid-cols-1 lg:grid-cols-12 gap-4">
    <section class="lg:col-span-8 bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden h-[620px] relative">
      <div class="absolute top-3 left-3 z-20 flex flex-wrap gap-2 max-w-[92%]">
        <button v-for="layer in layers" :key="layer.key" @click="store.toggleLayer(layer.key)" :class="layerButtonClass(layer.key)">
          <span>{{ layer.icon }}</span> {{ layer.label }}
        </button>
      </div>

      <div class="absolute bottom-3 left-3 z-20 bg-white/95 border border-slate-200 p-3 rounded-xl shadow-md text-[10px] space-y-1.5">
        <div class="font-bold text-slate-700 border-b border-slate-100 pb-1 mb-1">안전 인프라 및 범죄주의 구간</div>
        <div class="flex items-center gap-2"><span class="w-2.5 h-2.5 rounded-full bg-blue-500"></span> CCTV</div>
        <div class="flex items-center gap-2"><span class="w-2.5 h-2.5 rounded-full bg-yellow-400"></span> LED 보안등</div>
        <div class="flex items-center gap-2"><span class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> 치안센터 / 안심벨</div>
        <div class="flex items-center gap-2"><span class="h-1.5 w-6 rounded-full bg-teal-400 border border-dashed border-teal-700"></span> 안심귀갓길</div>
        <div class="flex items-center gap-2"><span class="w-4 h-2.5 bg-rose-500/20 border border-dashed border-rose-600"></span> 범죄주의 구간</div>
      </div>

      <div class="absolute bottom-3 left-1/2 -translate-x-1/2 z-20 bg-slate-900/95 text-white py-2 px-4 rounded-full text-xs shadow-md hidden md:flex items-center gap-2">
        <span>🛡️</span>
        <span>매물 마커를 클릭하면 HUG 가입성·실질 범죄지수·실거래 추이를 확인할 수 있습니다.</span>
      </div>

      <div class="relative w-full h-full bg-slate-100 overflow-hidden select-none">
        <svg class="absolute inset-0 w-full h-full" viewBox="0 0 520 460" preserveAspectRatio="xMidYMid slice">
          <rect width="520" height="460" fill="#f1f5f9" />
          <g stroke="#ffffff" stroke-width="14" stroke-linecap="round" stroke-linejoin="round">
            <line v-for="(road, index) in store.currentInfra.mainRoads" :key="`main-${index}`" :x1="road[0]" :y1="road[1]" :x2="road[2]" :y2="road[3]" />
          </g>
          <g stroke="#ffffff" stroke-width="7" stroke-linecap="round" stroke-linejoin="round">
            <line v-for="(road, index) in store.currentInfra.subRoads" :key="`sub-${index}`" :x1="road[0]" :y1="road[1]" :x2="road[2]" :y2="road[3]" />
          </g>
          <g v-show="store.activeLayers.path" stroke="#14b8a6" stroke-width="4" stroke-linecap="round" stroke-dasharray="7 7" class="glow-safe-path">
            <line v-for="(path, index) in store.currentInfra.paths" :key="`path-${index}`" :x1="path.x1" :y1="path.y1" :x2="path.x2" :y2="path.y2" class="animate-pulse-path" />
          </g>
          <g v-show="store.activeLayers.crimeZone" opacity="0.65">
            <polygon v-for="(zone, index) in store.currentInfra.crimeZones" :key="`zone-${index}`" :points="zone" class="crime-danger-zone" />
          </g>
        </svg>

        <template v-if="store.activeLayers.cctv">
          <div v-for="(point, index) in store.currentInfra.cctvs" :key="`cctv-${index}`" class="map-feature text-blue-600 border-blue-300 glow-cctv" :style="pointStyle(point)">📹</div>
        </template>
        <template v-if="store.activeLayers.lamp">
          <div v-for="(point, index) in store.currentInfra.lamps" :key="`lamp-${index}`" class="map-feature text-yellow-500 border-yellow-300 glow-lamp" :style="pointStyle(point)">💡</div>
        </template>
        <template v-if="store.activeLayers.police">
          <div v-for="(point, index) in store.currentInfra.polices" :key="`police-${index}`" class="absolute z-20 bg-white border border-emerald-400 text-emerald-700 text-[10px] font-black rounded-lg px-2 py-1 shadow" :style="pointStyle(point)">🏢 {{ point.desc }}</div>
        </template>

        <button v-for="property in store.currentProperties" :key="property.id" @click="store.selectProperty(property.id)" class="absolute z-30 group -translate-x-1/2 -translate-y-full" :style="pointStyle(property)">
          <div :class="['rounded-xl px-2.5 py-1.5 text-[11px] font-black shadow-md border-2 transition group-hover:scale-110', store.selectedPropertyId === property.id ? 'bg-amber-400 text-slate-900 border-white' : 'bg-brand text-white border-white']">
            🏠 {{ (property.deposit / 10000).toFixed(1) }}억/{{ property.rent }}
          </div>
          <div :class="['w-3 h-3 mx-auto -mt-1.5 rotate-45 border-r border-b border-white', store.selectedPropertyId === property.id ? 'bg-amber-400' : 'bg-brand']"></div>
        </button>
      </div>
    </section>

    <aside class="lg:col-span-4 flex flex-col gap-4 h-[620px]">
      <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-3 space-y-3">
        <div class="flex items-center gap-2 bg-slate-50 border border-slate-100 px-3 py-2 rounded-xl">
          <span class="text-slate-400">🔎</span>
          <input v-model="store.searchKeyword" type="text" placeholder="건물명 또는 주소 검색" class="bg-transparent text-sm w-full focus:outline-none" />
        </div>
        <div class="grid grid-cols-2 gap-2">
          <select v-model="store.filterType" class="bg-slate-50 border border-slate-200 rounded-lg p-2 text-xs font-bold focus:outline-none">
            <option value="all">모든 주거유형</option>
            <option value="다가구">원룸(다가구)</option>
            <option value="오피스텔">오피스텔</option>
            <option value="투룸">투룸</option>
          </select>
          <select v-model="store.sortType" class="bg-slate-50 border border-slate-200 rounded-lg p-2 text-xs font-bold focus:outline-none">
            <option value="safe">치안지수 높은순</option>
            <option value="price-low">월세 낮은순</option>
          </select>
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-slate-200 shadow-sm flex-1 overflow-y-auto p-3 space-y-2">
        <article v-for="property in store.filteredProperties" :key="property.id" @click="store.selectProperty(property.id)" :class="['p-3 rounded-xl border transition cursor-pointer', store.selectedPropertyId === property.id ? 'bg-brand-light border-brand shadow-sm' : 'bg-slate-50 border-slate-200 hover:bg-slate-100']">
          <div class="flex items-center justify-between gap-2">
            <span class="text-[10px] font-black px-2 py-0.5 rounded bg-blue-100 text-blue-700">{{ property.type }}</span>
            <span class="text-xs font-black text-emerald-600">🛡️ {{ property.safetyScore }}점</span>
          </div>
          <h3 class="font-black text-slate-900 text-sm mt-2 flex items-center justify-between">
            {{ property.name }}
            <span v-if="store.favorites.includes(property.id)" class="text-rose-500">♥</span>
          </h3>
          <p class="text-[11px] text-slate-500 mt-1">{{ property.address }}</p>
          <div class="flex items-center justify-between mt-3 pt-2 border-t border-slate-200/60">
            <span class="text-sm font-black text-slate-900">보증금 {{ (property.deposit / 10000).toFixed(1) }}억 / 월세 {{ property.rent }}</span>
            <span class="text-[10px] text-slate-500 bg-teal-50 px-2 py-0.5 rounded font-bold">{{ property.crimeGrade }}</span>
          </div>
        </article>
      </div>
    </aside>

    <transition name="slide">
      <section v-if="store.selectedProperty" class="fixed inset-y-0 right-0 w-full md:w-[480px] bg-white shadow-2xl z-[100] border-l border-slate-200 overflow-y-auto">
        <div class="sticky top-0 bg-white/95 backdrop-blur-md border-b border-slate-100 p-4 flex items-center justify-between z-10">
          <div class="flex items-center gap-2">
            <span class="bg-brand-light text-brand-dark text-[10px] font-black px-2 py-0.5 rounded">{{ store.selectedProperty.type }}</span>
            <span class="text-xs text-slate-500">매물 No. {{ store.selectedProperty.id }}</span>
          </div>
          <div class="flex gap-2">
            <button @click="store.toggleFavorite(store.selectedProperty.id)" :class="['w-8 h-8 rounded-full border flex items-center justify-center text-sm', store.favorites.includes(store.selectedProperty.id) ? 'bg-rose-50 border-rose-200 text-rose-500' : 'bg-white border-slate-200 text-slate-400']">♥</button>
            <button @click="store.closeProperty()" class="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-600">✕</button>
          </div>
        </div>

        <div class="p-5 space-y-5">
          <div>
            <h2 class="text-xl font-black text-slate-900">{{ store.selectedProperty.name }}</h2>
            <p class="text-sm text-slate-500">{{ store.selectedProperty.address }}</p>
            <div class="mt-3 flex items-center justify-between bg-brand-light p-3 rounded-xl border border-brand/20">
              <div><span class="text-xs font-bold text-brand-dark">희망 월세</span><p class="text-lg font-black text-brand-dark">보증금 {{ (store.selectedProperty.deposit / 10000).toFixed(1) }}억 / {{ store.selectedProperty.rent }}만원</p></div>
              <div class="text-right"><span class="text-[10px] text-slate-500">공시가격</span><p class="text-xs font-black">{{ formatMoney(store.selectedProperty.publicPrice) }}만원</p></div>
            </div>
          </div>

          <div class="bg-slate-50 p-4 rounded-2xl border border-slate-100 space-y-3">
            <div class="flex items-center justify-between">
              <h3 class="font-black text-sm">🛡️ 통합 치안 및 거주 안전 리포트</h3>
              <span class="bg-emerald-100 text-emerald-800 text-[10px] font-black px-2 py-0.5 rounded-full">{{ safetyLabel(store.selectedProperty.safetyScore) }}</span>
            </div>
            <div class="flex items-center gap-4">
              <div class="w-16 h-16 rounded-full bg-emerald-50 border-4 border-brand flex flex-col items-center justify-center text-brand-dark">
                <span class="text-xl font-black">{{ store.selectedProperty.safetyScore }}</span><span class="text-[8px] font-bold">안전 등급</span>
              </div>
              <div class="flex-1 space-y-1 text-[11px]">
                <p class="flex justify-between"><span class="text-slate-500 font-bold">범죄 발생률 등급</span><b>{{ store.selectedProperty.crimeGrade }}</b></p>
                <p class="flex justify-between"><span class="text-slate-500 font-bold">야간 조도</span><b>{{ store.selectedProperty.lamps }}</b></p>
                <p class="flex justify-between"><span class="text-slate-500 font-bold">CCTV 수</span><b>{{ store.selectedProperty.cctvs }}개</b></p>
              </div>
            </div>
            <p class="text-xs text-slate-600 bg-white p-3 rounded-xl border border-slate-200 leading-relaxed">{{ store.selectedProperty.description }}</p>
          </div>

          <div :class="['p-4 rounded-2xl border space-y-3', hugStatus(store.selectedProperty).eligible ? 'bg-emerald-50 border-emerald-100' : 'bg-rose-50 border-rose-100']">
            <div class="flex justify-between items-center">
              <h3 class="font-black text-xs">🧾 HUG 126% 가입 적격성 예비진단</h3>
              <span :class="['text-[10px] font-black px-2 py-0.5 rounded', hugStatus(store.selectedProperty).eligible ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-200 text-rose-950']">{{ hugStatus(store.selectedProperty).label }}</span>
            </div>
            <div class="bg-white/80 p-3 rounded-xl text-xs space-y-1 border border-white">
              <p class="flex justify-between"><span>HUG 가입 보증 한도</span><b>{{ formatMoney(hugStatus(store.selectedProperty).limit) }}만원</b></p>
              <p class="flex justify-between"><span>선순위 보증금</span><b>{{ store.selectedProperty.type.includes('다가구') ? formatMoney(store.selectedProperty.seniorDeposits) + '만원 확인 필요' : '개별등기' }}</b></p>
            </div>
            <p class="text-xs leading-relaxed">{{ hugStatus(store.selectedProperty).message }}</p>
            <router-link to="/diagnosis" class="block text-center bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs py-2 rounded-xl">이 매물 상세진단 실행</router-link>
          </div>

          <div>
            <h3 class="font-black text-sm mb-2">📈 국토부 실거래 신고 내역</h3>
            <svg class="w-full h-40 bg-slate-50 border border-slate-100 rounded-xl" viewBox="0 0 360 150">
              <polyline :points="chartPoints(store.selectedProperty.historicalPrices)" fill="none" stroke="#1ABC9C" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" />
              <circle v-for="(point, index) in chartPointArray(store.selectedProperty.historicalPrices)" :key="index" :cx="point.x" :cy="point.y" r="4" fill="#1ABC9C" />
              <text x="16" y="135" font-size="10" fill="#64748b">23년</text><text x="110" y="135" font-size="10" fill="#64748b">24년</text><text x="210" y="135" font-size="10" fill="#64748b">25년</text><text x="310" y="135" font-size="10" fill="#64748b">26년</text>
            </svg>
          </div>

          <div>
            <h3 class="font-black text-sm mb-2">👤 실거주자 후기</h3>
            <div class="space-y-2">
              <article v-for="review in store.selectedProperty.reviews" :key="review.user" class="bg-slate-50 p-3 rounded-xl border border-slate-100">
                <div class="flex justify-between text-[11px]"><b>{{ review.user }} <span class="text-slate-400 font-normal">({{ review.date }})</span></b><span class="text-amber-500 font-black">★ {{ review.rate }}</span></div>
                <p class="text-xs text-slate-600 mt-1 leading-relaxed">{{ review.content }}</p>
              </article>
            </div>
          </div>
        </div>
      </section>
    </transition>
  </div>
</template>

<script setup>
import useMapStore from '../store/mapStore'

const store = useMapStore()
const layers = [
  { key: 'cctv', label: 'CCTV', icon: '📹' },
  { key: 'lamp', label: '가로등/조도', icon: '💡' },
  { key: 'police', label: '관공서/안심벨', icon: '🏢' },
  { key: 'path', label: '안심귀갓길', icon: '🛣️' },
  { key: 'crimeZone', label: '범죄 위험 지역구간', icon: '⚠️' }
]

const layerButtonClass = (key) => {
  const active = store.activeLayers[key]
  if (key === 'crimeZone' && active) return 'layer-btn bg-rose-100 border-rose-300 text-rose-700 font-black'
  if (active) return 'layer-btn bg-brand-light border-brand/40 text-brand-dark font-bold'
  return 'layer-btn bg-white border-slate-200 text-slate-600 hover:bg-slate-50 font-bold'
}
const pointStyle = (point) => ({ left: `${point.x}px`, top: `${point.y}px` })
const formatMoney = (value) => Math.round(value).toLocaleString()
const safetyLabel = (score) => score >= 90 ? '안전 최우수' : score >= 80 ? '안전 우수' : score >= 70 ? '주의 필요' : '야간 주의'
const hugStatus = (property) => {
  const limit = Math.round(property.publicPrice * 1.26)
  const eligible = property.deposit <= limit
  return {
    limit,
    eligible,
    label: eligible ? 'HUG 요건 부합' : 'HUG 가입불가',
    message: eligible
      ? '보증금이 HUG 가입 허용선 안에 있습니다. 다가구라면 선순위 보증금까지 합산해 최종 부채비율을 확인하세요.'
      : `보증금 ${formatMoney(property.deposit)}만원이 HUG 한도 ${formatMoney(limit)}만원을 초과합니다. 보증보험 가입이 어려운 위험 매물입니다.`
  }
}
const chartPointArray = (prices) => {
  const min = Math.min(...prices)
  const max = Math.max(...prices)
  return prices.map((price, index) => {
    const x = 30 + index * 100
    const y = max === min ? 70 : 115 - ((price - min) / (max - min)) * 80
    return { x, y }
  })
}
const chartPoints = (prices) => chartPointArray(prices).map((point) => `${point.x},${point.y}`).join(' ')
</script>
