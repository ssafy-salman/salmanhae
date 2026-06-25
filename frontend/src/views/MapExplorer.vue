<template>
  <div class="grid grid-cols-1 gap-4 lg:min-h-[660px] lg:grid-cols-12">
    <div class="relative h-[660px] lg:col-span-9 lg:h-[calc(100vh-132px)] lg:min-h-[660px]">
      <div ref="filterRef" class="absolute left-3 right-3 top-3 z-[1000]">
        <form
          class="flex items-center gap-1.5 rounded-2xl border border-slate-100 bg-white/90 px-2.5 py-2 shadow-xl shadow-slate-200/60 backdrop-blur-md"
          @submit.prevent="refreshFromFilters"
        >
          <!-- 검색 -->
          <label class="flex min-w-0 flex-1 items-center gap-1.5 rounded-xl bg-slate-50 px-2.5 py-1">
            <Search class="h-3.5 w-3.5 shrink-0 text-slate-400" aria-hidden="true" />
            <input
              v-model="store.searchKeyword"
              class="w-full bg-transparent text-xs text-slate-800 outline-none placeholder:font-normal placeholder:text-slate-400"
              type="search"
              placeholder="건물명 또는 주소 검색"
            />
          </label>

          <div class="h-5 w-px shrink-0 bg-slate-200"></div>

          <!-- 거래 pill (거래유형 + 가격 통합) -->
          <div class="shrink-0">
            <button
              type="button"
              @click="toggleDropdown('transaction')"
              :class="['flex h-7 items-center gap-1 rounded-full border px-2.5 text-[11px] font-semibold transition', transactionPillActive ? 'border-slate-900 bg-slate-900 text-white' : 'border-slate-200 bg-white text-slate-700 hover:border-slate-300 hover:bg-slate-50']"
            >
              {{ transactionPillLabel }}<ChevronDown class="h-3 w-3" aria-hidden="true" />
            </button>
            <div v-if="activeDropdown === 'transaction'" class="absolute right-0 top-full z-30 mt-1.5 w-64 rounded-2xl border border-slate-100 bg-white shadow-xl">
              <!-- 거래 유형 선택 (다중 선택) -->
              <div class="p-1.5">
                <button type="button" @click="store.setTransactionType('')" class="flex w-full items-center gap-2.5 rounded-xl px-2.5 py-2 text-xs transition hover:bg-slate-50">
                  <span :class="['flex h-4 w-4 shrink-0 items-center justify-center rounded border-2 transition', store.filters.transactionTypes.length === 0 ? 'border-brand bg-brand' : 'border-slate-300']">
                    <Check v-if="store.filters.transactionTypes.length === 0" class="h-2.5 w-2.5 text-white" aria-hidden="true" />
                  </span>
                  <span :class="store.filters.transactionTypes.length === 0 ? 'font-semibold text-slate-900' : 'text-slate-600'">전체</span>
                </button>
                <button v-for="opt in transactionOptions" :key="opt.value" type="button" @click="store.setTransactionType(opt.value)" class="flex w-full items-center gap-2.5 rounded-xl px-2.5 py-2 text-xs transition hover:bg-slate-50">
                  <span :class="['flex h-4 w-4 shrink-0 items-center justify-center rounded border-2 transition', store.filters.transactionTypes.includes(opt.value) ? 'border-brand bg-brand' : 'border-slate-300']">
                    <Check v-if="store.filters.transactionTypes.includes(opt.value)" class="h-2.5 w-2.5 text-white" aria-hidden="true" />
                  </span>
                  <span :class="store.filters.transactionTypes.includes(opt.value) ? 'font-semibold text-slate-900' : 'text-slate-600'">{{ opt.label }}</span>
                </button>
              </div>
              <!-- 가격 슬라이더 -->
              <div class="space-y-4 border-t border-slate-100 px-3 py-3">
                <!-- 보증금 (월세·전세·전체) -->
                <div v-if="!depositFilterDisabled">
                  <p class="text-xs font-semibold text-slate-900">보증금</p>
                  <p class="mt-0.5 text-[11px] text-slate-400">{{ depositRangeLabel }}</p>
                  <div class="relative mt-3 h-4">
                    <div class="pointer-events-none absolute top-1/2 h-1 w-full -translate-y-1/2 rounded-full bg-slate-200">
                      <div class="absolute h-full rounded-full bg-slate-900" :style="{ left: depositMinPct + '%', right: (100 - depositMaxPct) + '%' }"></div>
                    </div>
                    <input type="range" v-model.number="localMinDeposit" min="0" :max="localMaxDeposit" :step="DEPOSIT_STEP" class="dual-slider" />
                    <input type="range" v-model.number="localMaxDeposit" :min="localMinDeposit" :max="DEPOSIT_BOUND" :step="DEPOSIT_STEP" class="dual-slider" />
                  </div>
                  <div class="mt-1.5 flex justify-between text-[10px] text-slate-400">
                    <span>0</span><span>1억</span><span>10억</span><span>20억~</span>
                  </div>
                </div>
                <!-- 월세금 (월세·전체) -->
                <div v-if="store.filters.transactionTypes.length === 0 || store.filters.transactionTypes.includes('MONTHLY_RENT')">
                  <p class="text-xs font-semibold text-slate-900">월세</p>
                  <p class="mt-0.5 text-[11px] text-slate-400">{{ monthlyRentRangeLabel }}</p>
                  <div class="relative mt-3 h-4">
                    <div class="pointer-events-none absolute top-1/2 h-1 w-full -translate-y-1/2 rounded-full bg-slate-200">
                      <div class="absolute h-full rounded-full bg-slate-900" :style="{ left: monthlyRentMinPct + '%', right: (100 - monthlyRentMaxPct) + '%' }"></div>
                    </div>
                    <input type="range" v-model.number="localMinMonthlyRent" min="0" :max="localMaxMonthlyRent" :step="MONTHLY_RENT_STEP" class="dual-slider" />
                    <input type="range" v-model.number="localMaxMonthlyRent" :min="localMinMonthlyRent" :max="MONTHLY_RENT_BOUND" :step="MONTHLY_RENT_STEP" class="dual-slider" />
                  </div>
                  <div class="mt-1.5 flex justify-between text-[10px] text-slate-400">
                    <span>0</span><span>50만</span><span>100만</span><span>200만~</span>
                  </div>
                </div>
                <!-- 매매가 (매매·전체) -->
                <div v-if="store.filters.transactionTypes.length === 0 || store.filters.transactionTypes.includes('SALE')">
                  <p class="text-xs font-semibold text-slate-900">매매가</p>
                  <p class="mt-0.5 text-[11px] text-slate-400">{{ priceRangeLabel }}</p>
                  <div class="relative mt-3 h-4">
                    <div class="pointer-events-none absolute top-1/2 h-1 w-full -translate-y-1/2 rounded-full bg-slate-200">
                      <div class="absolute left-0 h-full rounded-full bg-slate-900" :style="{ right: (100 - priceMinPct) + '%' }"></div>
                    </div>
                    <input type="range" v-model.number="localMinPrice" min="0" :max="PRICE_BOUND" :step="PRICE_STEP" class="dual-slider" />
                  </div>
                  <div class="mt-1.5 flex justify-between text-[10px] text-slate-400">
                    <span>0</span><span>10억</span><span>20억</span><span>40억~</span>
                  </div>
                </div>
              </div>
              <!-- 초기화 -->
              <div class="border-t border-slate-100 px-3 py-2.5">
                <button type="button" @click="resetPriceFilters" class="flex items-center gap-1.5 text-[11px] font-semibold text-slate-400 transition hover:text-slate-700">
                  <RotateCw class="h-3 w-3" aria-hidden="true" />초기화
                </button>
              </div>
            </div>
          </div>

          <!-- 유형 pill -->
          <div class="shrink-0">
            <button
              type="button"
              @click="toggleDropdown('propertyType')"
              :class="['flex h-7 items-center gap-1 rounded-full border px-2.5 text-[11px] font-semibold transition', store.filters.propertyType ? 'border-slate-900 bg-slate-900 text-white' : 'border-slate-200 bg-white text-slate-700 hover:border-slate-300 hover:bg-slate-50']"
            >
              {{ propertyTypePillLabel }}<ChevronDown class="h-3 w-3" aria-hidden="true" />
            </button>
            <div v-if="activeDropdown === 'propertyType'" class="absolute right-0 top-full z-30 mt-1.5 w-28 overflow-hidden rounded-2xl border border-slate-100 bg-white shadow-xl">
              <div class="p-1">
                <button type="button" @click="store.filters.propertyType = ''; closeDropdown()" :class="['flex w-full items-center rounded-lg px-2.5 py-2 text-xs transition', !store.filters.propertyType ? 'bg-slate-900 font-semibold text-white' : 'text-slate-700 hover:bg-slate-50']">전체</button>
                <button
                  v-for="opt in propertyTypeOptions" :key="opt.value"
                  type="button"
                  @click="store.filters.propertyType = opt.value; closeDropdown()"
                  :class="['flex w-full items-center rounded-lg px-2.5 py-2 text-xs transition', store.filters.propertyType === opt.value ? 'bg-slate-900 font-semibold text-white' : 'text-slate-700 hover:bg-slate-50']"
                >{{ opt.label }}</button>
              </div>
            </div>
          </div>

          <div class="h-5 w-px shrink-0 bg-slate-200"></div>

          <button type="button" @click="resetFilters" class="h-7 shrink-0 rounded-lg px-2.5 text-[11px] font-semibold text-slate-500 transition hover:bg-slate-100">
            초기화
          </button>
        </form>
      </div>

      <section class="relative h-full overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
        <div ref="mapElement" class="h-full w-full bg-slate-100"></div>

        <div v-if="isMapLoading" class="absolute inset-0 z-10 flex items-center justify-center bg-slate-50">
          <div class="flex items-center gap-2 rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-bold text-slate-700 shadow-sm">
            <Loader2 class="h-4 w-4 animate-spin" aria-hidden="true" />
            지도 불러오는 중
          </div>
        </div>

        <div v-if="mapError" class="absolute inset-0 z-10 flex items-center justify-center bg-slate-50 p-6">
          <div class="max-w-sm rounded-2xl border border-amber-200 bg-white p-5 text-center shadow-sm">
            <AlertTriangle class="mx-auto h-8 w-8 text-amber-500" aria-hidden="true" />
            <h2 class="mt-3 text-sm font-bold text-slate-900">네이버 지도를 불러오지 못했습니다</h2>
            <p class="mt-2 text-xs leading-5 text-slate-500">{{ mapError }}</p>
            <p class="mt-3 text-xs font-bold text-slate-600">매물 목록은 기본 지도 범위로 조회됩니다.</p>
          </div>
        </div>

      <div class="absolute bottom-3 left-3 z-20 flex flex-wrap items-center gap-2 rounded-2xl border border-slate-200 bg-white/95 px-3 py-2 text-xs font-bold text-slate-600 shadow-sm backdrop-blur">
        <MapPin class="h-4 w-4 text-brand" aria-hidden="true" />
        <span>{{ viewportCountLabel }}</span>
        <span v-if="store.lastFetchedAt" class="text-slate-400">{{ formattedFetchedAt }}</span>
      </div>

      </section>
    </div>

    <aside class="flex h-[660px] flex-col lg:col-span-3 lg:h-[calc(100vh-132px)] lg:min-h-[660px]">
      <section class="flex min-h-0 flex-1 flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">

        <!-- 헤더 -->
        <div class="flex shrink-0 items-center justify-between border-b border-slate-100 px-4 py-3">
          <template v-if="store.selectedProperty">
            <button type="button" @click="store.closeProperty" class="flex items-center gap-1.5 text-xs font-semibold text-slate-500 transition hover:text-slate-800">
              <ChevronLeft class="h-4 w-4" aria-hidden="true" />
              목록으로
            </button>
            <span class="rounded-full bg-brand-light px-2 py-1 text-[10px] font-bold text-brand-dark">{{ transactionLabel(store.selectedProperty.transactionType) }}</span>
          </template>
          <template v-else>
            <h2 class="text-sm font-bold text-slate-900">지도 범위 매물</h2>
          </template>
        </div>

        <!-- 상세 뷰 -->
        <div v-if="store.selectedProperty" class="min-h-0 flex-1 overflow-y-auto">
          <div class="space-y-5 p-5">
            <div>
              <p class="text-xs font-bold text-brand-dark">{{ propertyTypeLabel(store.selectedProperty.propertyType) }}</p>
              <h2 class="mt-1 text-2xl font-bold text-slate-900">{{ displayTitle(store.selectedProperty) }}</h2>
              <p class="mt-2 text-sm leading-6 text-slate-500">{{ store.selectedProperty.address }}</p>
              <p v-if="store.selectedProperty.roadAddress" class="text-xs leading-5 text-slate-400">{{ store.selectedProperty.roadAddress }}</p>
            </div>

            <div class="rounded-2xl border border-brand/20 bg-brand-light p-4">
              <p class="text-xs font-bold text-brand-dark">가격</p>
              <p class="mt-1 text-xl font-bold text-slate-900">{{ priceText(store.selectedProperty) }}</p>
              <p v-if="store.selectedProperty.maintenanceFee" class="mt-2 text-xs font-bold text-slate-600">관리비 {{ formatWons(store.selectedProperty.maintenanceFee) }}</p>
            </div>

            <div class="grid grid-cols-2 gap-2">
              <div class="detail-stat">
                <span>전용 면적</span>
                <b>{{ areaText(store.selectedProperty) }}</b>
              </div>
              <div class="detail-stat">
                <span>층수</span>
                <b>{{ floorText(store.selectedProperty) }}</b>
              </div>
              <div class="detail-stat">
                <span>건물명</span>
                <b>{{ store.selectedProperty.buildingName || '-' }}</b>
              </div>
            </div>

            <div v-if="store.detailError" class="rounded-2xl border border-rose-100 bg-rose-50 p-4 text-xs font-bold leading-5 text-rose-700">
              {{ store.detailError }}
            </div>

            <div v-if="store.isDetailLoading" class="flex items-center justify-center rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm font-bold text-slate-500">
              <Loader2 class="mr-2 h-4 w-4 animate-spin" aria-hidden="true" />
              상세 정보를 불러오는 중입니다
            </div>

            <div class="rounded-2xl border border-slate-200 bg-white p-4">
              <div class="flex items-start justify-between gap-3">
                <div>
                  <p class="text-xs font-bold text-brand-dark">{{ transactionTrendLabel }}</p>
                  <h3 class="mt-1 text-base font-bold text-slate-900">실거래가 추이</h3>
                </div>
                <span v-if="store.selectedPropertyTransactionsTotal" class="rounded-full bg-slate-100 px-2 py-1 text-[10px] font-bold text-slate-500">
                  최근 {{ store.selectedPropertyTransactionsTotal.toLocaleString() }}건
                </span>
              </div>
              <div v-if="store.isTransactionsLoading" class="mt-4 flex items-center justify-center rounded-xl bg-slate-50 p-4 text-sm font-bold text-slate-500">
                <Loader2 class="mr-2 h-4 w-4 animate-spin" aria-hidden="true" />
                실거래가를 불러오는 중입니다
              </div>
              <div v-else-if="store.transactionError" class="mt-4 rounded-xl border border-rose-100 bg-rose-50 p-4 text-xs font-bold leading-5 text-rose-700">
                {{ store.transactionError }}
              </div>
              <div v-else-if="transactionTrend.points.length === 0" class="mt-4 rounded-xl bg-slate-50 p-4 text-sm font-bold text-slate-500">
                비교 가능한 최근 실거래가가 없습니다.
              </div>
              <div v-else class="mt-4 space-y-4">
                <div class="grid grid-cols-2 gap-2">
                  <div class="rounded-xl bg-slate-50 p-3">
                    <span class="text-[10px] font-bold text-slate-400">평균</span>
                    <b class="mt-1 block text-sm text-slate-900">{{ formatWons(transactionTrend.averageAmount) }}</b>
                  </div>
                  <div class="rounded-xl bg-slate-50 p-3">
                    <span class="text-[10px] font-bold text-slate-400">최근 거래</span>
                    <b class="mt-1 block text-sm text-slate-900">{{ formatWons(transactionTrend.latest?.amount) }}</b>
                  </div>
                </div>
                <div class="space-y-3">
                  <div
                    v-for="transaction in transactionTrend.points"
                    :key="`${transaction.contractYearMonth}-${transaction.amount}-${transaction.floor ?? 'floor'}`"
                    class="space-y-1.5"
                  >
                    <div class="flex items-center justify-between gap-3 text-xs font-bold">
                      <span class="text-slate-500">{{ transaction.contractYearMonth }}</span>
                      <span class="text-slate-900">{{ formatWons(transaction.amount) }}</span>
                    </div>
                    <div class="h-2 overflow-hidden rounded-full bg-slate-100">
                      <div class="h-full rounded-full bg-brand" :style="{ width: `${transaction.barWidth}%` }"></div>
                    </div>
                    <p class="text-[11px] font-semibold text-slate-400">{{ transactionMetaText(transaction) }}</p>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="publicDescription" class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
              <div class="flex items-center gap-2">
                <Building2 class="h-4 w-4 text-slate-400" aria-hidden="true" />
                <h3 class="text-sm font-bold text-slate-900">매물 메모</h3>
              </div>
              <p class="mt-3 text-sm leading-6 text-slate-600">{{ publicDescription }}</p>
            </div>
          </div>
        </div>

        <!-- 목록 뷰 -->
        <div v-else class="min-h-0 flex-1 overflow-y-auto p-3">
          <div v-if="store.isLoading" class="flex h-full items-center justify-center text-sm font-bold text-slate-500">
            <Loader2 class="mr-2 h-4 w-4 animate-spin" aria-hidden="true" />
            매물을 불러오는 중입니다
          </div>
          <div v-else-if="store.error" class="flex h-full items-center justify-center p-6 text-center">
            <div>
              <AlertTriangle class="mx-auto h-8 w-8 text-rose-500" aria-hidden="true" />
              <p class="mt-3 text-sm font-bold text-slate-900">매물 API 오류</p>
              <p class="mt-2 text-xs leading-5 text-slate-500">{{ store.error }}</p>
            </div>
          </div>
          <div v-else-if="store.selectedViewportItem" class="space-y-3">
            <article class="rounded-xl border border-brand/30 bg-brand-light p-4 shadow-sm">
              <p class="text-[11px] font-bold uppercase text-brand-dark">{{ selectedViewportSummary.eyebrow }}</p>
              <h3 class="mt-1 text-base font-bold text-slate-900">{{ selectedViewportSummary.title }}</h3>
              <p class="mt-2 text-xs leading-5 text-slate-600">{{ selectedViewportSummary.description }}</p>
              <div class="mt-4 grid grid-cols-2 gap-2">
                <div class="rounded-xl bg-white p-3">
                  <span class="text-[10px] font-bold text-slate-400">대표 가격</span>
                  <b class="mt-1 block text-sm text-slate-900">{{ selectedViewportSummary.price }}</b>
                </div>
                <div class="rounded-xl bg-white p-3">
                  <span class="text-[10px] font-bold text-slate-400">포함 매물</span>
                  <b class="mt-1 block text-sm text-slate-900">{{ selectedViewportSummary.count }}</b>
                </div>
              </div>
              <button class="mt-4 w-full rounded-xl bg-slate-900 px-3 py-2 text-xs font-bold text-white transition hover:bg-slate-800" type="button" @click="zoomToSelectedViewport">
                확대해서 보기
              </button>
            </article>
          </div>
          <div v-else-if="store.filteredProperties.length === 0" class="flex h-full items-center justify-center p-6 text-center">
            <div>
              <Home class="mx-auto h-8 w-8 text-slate-300" aria-hidden="true" />
              <p class="mt-3 text-sm font-bold text-slate-900">{{ emptyListText.title }}</p>
              <p class="mt-2 text-xs leading-5 text-slate-500">{{ emptyListText.description }}</p>
            </div>
          </div>
          <div v-else class="space-y-2">
            <article
              v-for="property in store.filteredProperties"
              :key="property.id"
              :class="[
                'cursor-pointer rounded-xl border p-3 transition',
                store.selectedPropertyId === property.id ? 'border-brand bg-brand-light shadow-sm' : 'border-slate-200 bg-slate-50 hover:bg-slate-100'
              ]"
              tabindex="0"
              @click="store.selectProperty(property.id)"
              @keydown.enter="store.selectProperty(property.id)"
              @keydown.space.prevent="store.selectProperty(property.id)"
            >
              <div class="flex items-start justify-between gap-3">
                <div class="min-w-0">
                  <p class="truncate text-sm font-bold text-slate-900">{{ displayTitle(property) }}</p>
                  <p class="mt-1 truncate text-xs font-semibold text-slate-500">{{ property.address }}</p>
                </div>
                <span class="shrink-0 rounded-full bg-white px-2 py-1 text-[10px] font-bold text-slate-600">{{ propertyTypeLabel(property.propertyType) }}</span>
              </div>
              <div class="mt-3 flex items-center justify-between gap-3 border-t border-slate-200/70 pt-3">
                <span class="text-sm font-bold text-slate-900">{{ priceText(property) }}</span>
                <span class="rounded-full bg-slate-900 px-2 py-1 text-[10px] font-bold text-white">{{ transactionLabel(property.transactionType) }}</span>
              </div>
              <p class="mt-2 text-xs font-semibold text-slate-500">{{ areaText(property) }} · {{ floorText(property) }}</p>
            </article>
          </div>
        </div>

      </section>
    </aside>

  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import {
  AlertTriangle,
  Building2,
  Check,
  ChevronDown,
  ChevronLeft,
  Home,
  Loader2,
  MapPin,
  RotateCw,
  Search,
  X
} from '@lucide/vue'
import useMapStore from '../store/mapStore'
import {
  buildTransactionTrend,
  trendLabelForTransactionType
} from '../utils/transactionTrend'
import { loadNaverMaps } from '../utils/naverMaps'
import {
  VIEWPORT_MODES,
  getPrimaryPriceValue,
  propertyDisplayTitle,
  propertyTypeLabel,
  regionLevelLabel,
  targetZoomForViewportItem,
  viewportMarkerAnchor,
  viewportMarkerKind,
  viewportMarkerLabel
} from '../utils/mapViewport'

const store = useMapStore()
const mapElement = ref(null)
const isMapLoading = ref(true)
const mapError = ref('')

// Filter dropdown
const filterRef = ref(null)
const activeDropdown = ref(null)

const toggleDropdown = (name) => {
  activeDropdown.value = activeDropdown.value === name ? null : name
}
const closeDropdown = () => { activeDropdown.value = null }

const handleClickOutside = (e) => {
  if (filterRef.value && !filterRef.value.contains(e.target)) closeDropdown()
}

// Price slider
const DEPOSIT_BOUND = 200000      // 20억 (만원)
const DEPOSIT_STEP = 5000
const MONTHLY_RENT_BOUND = 200    // 200만원 (만원)
const MONTHLY_RENT_STEP = 5
const PRICE_BOUND = 400000        // 40억 (만원)
const PRICE_STEP = 10000

const localMinDeposit = ref(0)
const localMaxDeposit = ref(DEPOSIT_BOUND)
const localMinMonthlyRent = ref(0)
const localMaxMonthlyRent = ref(MONTHLY_RENT_BOUND)
const localMinPrice = ref(0)

watch(() => activeDropdown.value, (val, oldVal) => {
  if (val === 'transaction') {
    localMinDeposit.value = Number(store.filters.minDeposit) || 0
    localMaxDeposit.value = Number(store.filters.maxDeposit) || DEPOSIT_BOUND
    localMinMonthlyRent.value = Number(store.filters.minMonthlyRent) || 0
    localMaxMonthlyRent.value = Number(store.filters.maxMonthlyRent) || MONTHLY_RENT_BOUND
    localMinPrice.value = Number(store.filters.minPrice) || 0
  }
  if (oldVal === 'transaction' && val === null) {
    refreshFromFilters()
  }
})

watch(() => store.filters.propertyType, () => refreshFromFilters())

watch([localMinDeposit, localMaxDeposit, localMinMonthlyRent, localMaxMonthlyRent, localMinPrice], () => {
  store.filters.minDeposit = localMinDeposit.value > 0 ? localMinDeposit.value : ''
  store.filters.maxDeposit = localMaxDeposit.value < DEPOSIT_BOUND ? localMaxDeposit.value : ''
  store.filters.minMonthlyRent = localMinMonthlyRent.value > 0 ? localMinMonthlyRent.value : ''
  store.filters.maxMonthlyRent = localMaxMonthlyRent.value < MONTHLY_RENT_BOUND ? localMaxMonthlyRent.value : ''
  store.filters.minPrice = localMinPrice.value > 0 ? localMinPrice.value : ''
})

const depositMinPct = computed(() => (localMinDeposit.value / DEPOSIT_BOUND) * 100)
const depositMaxPct = computed(() => (localMaxDeposit.value / DEPOSIT_BOUND) * 100)
const monthlyRentMinPct = computed(() => (localMinMonthlyRent.value / MONTHLY_RENT_BOUND) * 100)
const monthlyRentMaxPct = computed(() => (localMaxMonthlyRent.value / MONTHLY_RENT_BOUND) * 100)
const priceMinPct = computed(() => (localMinPrice.value / PRICE_BOUND) * 100)

const formatSliderVal = (val, bound) => {
  if (val >= bound) return `${Math.floor(bound / 10000)}억~`
  if (val === 0) return '0'
  if (val >= 10000) {
    const eok = Math.floor(val / 10000)
    const rest = val % 10000
    return rest > 0 ? `${eok}억 ${rest.toLocaleString()}만` : `${eok}억`
  }
  return `${val.toLocaleString()}만`
}

const depositRangeLabel = computed(() => {
  const min = localMinDeposit.value
  const max = localMaxDeposit.value
  if (min === 0 && max >= DEPOSIT_BOUND) return '전체'
  if (min === 0) return `~${formatSliderVal(max, DEPOSIT_BOUND)}`
  if (max >= DEPOSIT_BOUND) return `${formatSliderVal(min, DEPOSIT_BOUND)}~`
  return `${formatSliderVal(min, DEPOSIT_BOUND)} ~ ${formatSliderVal(max, DEPOSIT_BOUND)}`
})

const priceRangeLabel = computed(() => {
  const min = localMinPrice.value
  return min === 0 ? '전체' : `${formatSliderVal(min, PRICE_BOUND)}~`
})

const monthlyRentRangeLabel = computed(() => {
  const min = localMinMonthlyRent.value
  const max = localMaxMonthlyRent.value
  if (min === 0 && max >= MONTHLY_RENT_BOUND) return '전체'
  if (min === 0) return `~${max.toLocaleString()}만`
  if (max >= MONTHLY_RENT_BOUND) return `${min.toLocaleString()}만~`
  return `${min.toLocaleString()}만 ~ ${max.toLocaleString()}만`
})

const hasPriceFilter = computed(() =>
  !!store.filters.minDeposit || !!store.filters.maxDeposit ||
  !!store.filters.minMonthlyRent || !!store.filters.maxMonthlyRent ||
  !!store.filters.minPrice
)

const transactionOptions = [
  { value: 'MONTHLY_RENT', label: '월세' },
  { value: 'JEONSE', label: '전세' },
  { value: 'SALE', label: '매매' }
]

const propertyTypeOptions = [
  { value: 'ONE_ROOM', label: '원룸' },
  { value: 'OFFICETEL', label: '오피스텔' },
  { value: 'APARTMENT', label: '아파트' },
  { value: 'VILLA', label: '빌라' },
  { value: 'MULTI_FAMILY', label: '다세대' }
]

const transactionPillLabel = computed(() => {
  const types = store.filters.transactionTypes
  if (types.length === 0) return '거래'
  if (types.length === 1) return transactionOptions.find(o => o.value === types[0])?.label ?? '거래'
  return types.map(t => transactionOptions.find(o => o.value === t)?.label ?? t).join('·')
})

const transactionPillActive = computed(() =>
  store.filters.transactionTypes.length > 0 || hasPriceFilter.value
)

const propertyTypePillLabel = computed(() =>
  propertyTypeOptions.find(o => o.value === store.filters.propertyType)?.label ?? '유형'
)

const resetPriceFilters = () => {
  localMinDeposit.value = 0
  localMaxDeposit.value = DEPOSIT_BOUND
  localMinMonthlyRent.value = 0
  localMaxMonthlyRent.value = MONTHLY_RENT_BOUND
  localMinPrice.value = 0
}

let mapsApi = null
let map = null
let idleListener = null
let markers = []
let markerListeners = []

const transactionTypeModel = computed({
  get: () => store.filters.transactionType,
  set: (value) => store.setTransactionType(value)
})

const depositFilterDisabled = computed(() => store.isDepositFilterDisabled)

const formattedFetchedAt = computed(() => {
  if (!store.lastFetchedAt) return ''
  return new Intl.DateTimeFormat('ko-KR', {
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(store.lastFetchedAt))
})

const isPropertyMode = computed(() => store.viewportMode === VIEWPORT_MODES.PROPERTY_MARKER)

const visibleMapItems = computed(() => (
  isPropertyMode.value ? store.filteredProperties : store.viewportItems
))

const viewportCountLabel = computed(() => {
  const count = store.totalCount.toLocaleString()
  if (store.viewportMode === VIEWPORT_MODES.PROPERTY_CLUSTER) return `${count}개 그룹`
  if ([VIEWPORT_MODES.SIDO_AVG, VIEWPORT_MODES.SIGUNGU_AVG, VIEWPORT_MODES.DONG_AVG].includes(store.viewportMode)) return `${count}개 지역`
  return `${count}개 매물`
})

const emptyListText = computed(() => {
  if (!isPropertyMode.value && store.viewportItems.length > 0) {
    return {
      title: '상세 매물은 확대 후 표시됩니다',
      description: '현재 줌에서는 지역 평균 또는 매물 묶음을 지도에 표시합니다.'
    }
  }
  return {
    title: '표시할 매물이 없습니다',
    description: '지도를 조금 넓히거나 필터를 초기화해보세요.'
  }
})

const publicDescription = computed(() => {
  const description = store.selectedProperty?.description?.trim()
  if (!description) return ''
  if (description.includes('MVP 더미') || description.includes('실거래가 건물 정보')) return ''
  return description
})

const transactionTrend = computed(() => buildTransactionTrend(store.selectedPropertyTransactions))

const transactionTrendLabel = computed(() => (
  trendLabelForTransactionType(store.selectedProperty?.transactionType)
))

const displayTitle = (property) => propertyDisplayTitle(property)

const transactionLabel = (type) => ({
  MONTHLY_RENT: '월세',
  JEONSE: '전세',
  SALE: '매매'
}[type] || '거래')

const formatWons = (value) => {
  if (value === null || value === undefined) return '-'
  const man = Math.round(Number(value) / 10000)
  if (!Number.isFinite(man)) return '-'
  if (man >= 10000) {
    const eok = Math.floor(man / 10000)
    const rest = man % 10000
    return rest > 0 ? `${eok}억 ${rest.toLocaleString()}만` : `${eok}억`
  }
  return `${man.toLocaleString()}만`
}

const priceText = (property) => {
  if (property.transactionType === 'SALE') return `매매 ${formatWons(property.price)}`
  if (property.transactionType === 'JEONSE') return `전세 ${formatWons(property.deposit)}`
  return `보증금 ${formatWons(property.deposit)} / 월세 ${formatWons(property.monthlyRent)}`
}

const selectedViewportSummary = computed(() => {
  const item = store.selectedViewportItem
  if (!item) {
    return { eyebrow: '', title: '', description: '', price: '-', count: '-' }
  }

  const price = formatWons(getPrimaryPriceValue(item))
  if (item.type === 'CLUSTER') {
    return {
      eyebrow: '매물 묶음',
      title: `${Number(item.count || 0).toLocaleString()}개 매물`,
      description: '선택한 묶음 주변으로 지도를 이동했습니다. 확대해서 개별 매물을 확인할 수 있습니다.',
      price,
      count: `${Number(item.count || 0).toLocaleString()}개`
    }
  }

  return {
    eyebrow: regionLevelLabel(item.regionLevel),
    title: item.regionName || item.regionCode || '지역 평균',
    description: '선택한 지역의 화면 내 매물을 기준으로 대표 가격과 매물 수를 보여줍니다.',
    price,
    count: `${Number(item.transactionCount || 0).toLocaleString()}개`
  }
})

const areaText = (property) => {
  if (!property.areaM2) return '면적 정보 없음'
  const pyeong = Number(property.areaM2) / 3.3058
  return `${Number(property.areaM2).toFixed(1)}m² (${pyeong.toFixed(1)}평)`
}

const floorText = (property) => {
  const floor = property.floor ? `${property.floor}층` : '층수 미상'
  return property.totalFloor ? `${floor} / ${property.totalFloor}층` : floor
}

const transactionMetaText = (transaction) => {
  const parts = []
  if (transaction.areaM2) parts.push(areaText(transaction))
  if (transaction.floor) parts.push(`${transaction.floor}층`)
  if (transaction.transactionType === 'MONTHLY_RENT' && transaction.deposit) {
    parts.push(`보증금 ${formatWons(transaction.deposit)}`)
  }
  return parts.join(' · ') || '상세 조건 미상'
}

const escapeHtml = (value) => String(value ?? '')
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;')
  .replaceAll("'", '&#39;')

const getMapBounds = () => {
  const bounds = map.getBounds()
  const sw = bounds.getSW()
  const ne = bounds.getNE()
  const nextBounds = {
    west: sw.lng(),
    south: sw.lat(),
    east: ne.lng(),
    north: ne.lat()
  }
  const hasFiniteValues = Object.values(nextBounds).every(Number.isFinite)
  if (!hasFiniteValues || nextBounds.west >= nextBounds.east || nextBounds.south >= nextBounds.north) return null
  return nextBounds
}

const propertyMarkerContent = (property, isSelected) => {
  const bg = isSelected ? 'rgba(15,23,42,0.88)' : 'rgba(26,188,156,0.82)'
  const border = isSelected ? 'rgba(255,255,255,0.22)' : 'rgba(255,255,255,0.55)'
  const shadow = isSelected
    ? '0 2px 12px rgba(0,0,0,0.28), inset 0 1px 0 rgba(255,255,255,0.1)'
    : '0 2px 12px rgba(26,188,156,0.38), inset 0 1px 0 rgba(255,255,255,0.28)'
  const txLabel = escapeHtml(transactionLabel(property.transactionType))
  const price = escapeHtml(formatWons(getPrimaryPriceValue(property)))

  return `
    <button type="button" style="
      position: relative;
      display: inline-flex;
      align-items: center;
      gap: 5px;
      padding: 5px 10px 6px;
      border: 1.5px solid ${border};
      border-radius: 100px;
      background: ${bg};
      -webkit-backdrop-filter: blur(12px) saturate(160%);
      backdrop-filter: blur(12px) saturate(160%);
      color: #fff;
      font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: -0.025em;
      line-height: 1;
      white-space: nowrap;
      box-shadow: ${shadow};
      cursor: pointer;
    ">
      <span style="font-size:10px; font-weight:600; opacity:0.72;">${txLabel}</span>
      <span style="width:1px; height:8px; background:rgba(255,255,255,0.28); border-radius:1px; flex-shrink:0;"></span>
      <span>${price}</span>
      <span style="
        position: absolute;
        left: 50%;
        bottom: -5px;
        width: 8px;
        height: 8px;
        transform: translateX(-50%) rotate(45deg);
        background: ${bg};
        border-right: 1.5px solid ${border};
        border-bottom: 1.5px solid ${border};
      "></span>
    </button>
  `
}

const regionMarkerContent = (item) => {
  const label = viewportMarkerLabel(item, {
    formatWons,
    transactionLabel,
    showCount: true
  })
  return `
    <button type="button" style="
      position: relative;
      max-width: 116px;
      border: 1.5px solid rgba(255,255,255,0.22);
      border-radius: 14px;
      background: rgba(15,23,42,0.82);
      -webkit-backdrop-filter: blur(14px) saturate(160%);
      backdrop-filter: blur(14px) saturate(160%);
      color: #fff;
      padding: 6px 11px 7px;
      font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: -0.02em;
      line-height: 1.2;
      box-shadow: 0 2px 12px rgba(0,0,0,0.2), inset 0 1px 0 rgba(255,255,255,0.1);
      cursor: pointer;
      text-align: center;
      white-space: nowrap;
    ">
      <span style="display:block; overflow:hidden; text-overflow:ellipsis; font-size:10px; font-weight:600; opacity:0.55;">${escapeHtml(label.title)}</span>
      <span style="display:block; margin-top:2px; color:#1ABC9C;">${escapeHtml(label.value)}</span>
      <span style="
        position: absolute;
        left: 50%;
        bottom: -5px;
        width: 8px;
        height: 8px;
        transform: translateX(-50%) rotate(45deg);
        background: rgba(15,23,42,0.82);
        border-right: 1.5px solid rgba(255,255,255,0.22);
        border-bottom: 1.5px solid rgba(255,255,255,0.22);
      "></span>
    </button>
  `
}

const clusterMarkerContent = (item) => {
  const label = viewportMarkerLabel(item, { formatWons, transactionLabel })
  return `
    <button type="button" style="
      width: 76px;
      height: 76px;
      border: 1.5px solid rgba(255,255,255,0.5);
      border-radius: 999px;
      background: rgba(26,188,156,0.78);
      -webkit-backdrop-filter: blur(14px) saturate(160%);
      backdrop-filter: blur(14px) saturate(160%);
      color: #fff;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      box-shadow: 0 0 0 6px rgba(26,188,156,0.18), 0 4px 16px rgba(26,188,156,0.35), inset 0 1px 0 rgba(255,255,255,0.25);
      cursor: pointer;
      text-align: center;
      font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
      line-height: 1.15;
    ">
      <span style="font-size:15px; font-weight:800; letter-spacing:-0.03em;">${escapeHtml(label.value)}</span>
      <span style="margin-top:3px; max-width:60px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; font-size:10px; font-weight:600; opacity:0.82;">${escapeHtml(label.title)}</span>
    </button>
  `
}

const markerContent = (item) => {
  const kind = viewportMarkerKind(item)
  if (kind === 'region') return regionMarkerContent(item)
  if (kind === 'cluster') return clusterMarkerContent(item)
  return propertyMarkerContent(item, store.selectedPropertyId === item.id)
}

const clearMarkers = () => {
  markerListeners.forEach((listener) => mapsApi?.Event.removeListener(listener))
  markerListeners = []
  markers.forEach((marker) => marker.setMap(null))
  markers = []
}

const renderMarkers = () => {
  if (!mapsApi || !map) return
  clearMarkers()

  visibleMapItems.value.forEach((item) => {
    if (!item.latitude || !item.longitude) return
    const anchor = viewportMarkerAnchor(item)

    const marker = new mapsApi.Marker({
      position: new mapsApi.LatLng(item.latitude, item.longitude),
      map,
      icon: {
        content: markerContent(item),
        anchor: new mapsApi.Point(anchor.x, anchor.y)
      }
    })
    const listener = mapsApi.Event.addListener(marker, 'click', () => handleMarkerClick(item))
    markers.push(marker)
    markerListeners.push(listener)
  })
}

const handleMarkerClick = (item) => {
  if (item.type === 'PROPERTY') {
    store.selectProperty(item.id)
    return
  }
  store.selectViewportItem(item)
  focusViewportItem(item)
}

const zoomToSelectedViewport = () => {
  const item = store.selectedViewportItem
  focusViewportItem(item)
}

const focusViewportItem = (item) => {
  if (!item || !mapsApi || !map) return
  const latitude = Number(item.latitude)
  const longitude = Number(item.longitude)
  if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) return

  const nextZoom = Math.max(map.getZoom(), targetZoomForViewportItem(item, map.getZoom()))
  const nextCenter = new mapsApi.LatLng(latitude, longitude)
  map.setZoom(nextZoom)
  map.setCenter(nextCenter)
  store.setZoom(nextZoom)
  store.setCenter({ latitude, longitude })
}

const refreshFromMapBounds = async () => {
  if (!map) {
    await store.fetchViewport()
    return
  }

  store.setCenter({
    latitude: map.getCenter().lat(),
    longitude: map.getCenter().lng()
  })
  store.setZoom(map.getZoom())
  const bounds = getMapBounds()
  await store.fetchViewport(bounds || store.bounds)
}

const refreshFromFilters = async () => {
  await refreshFromMapBounds()
}

const resetFilters = async () => {
  store.resetFilters()
  resetPriceFilters()
  await refreshFromMapBounds()
}

watch(
  [() => store.viewportItems, () => store.filteredProperties, () => store.selectedPropertyId],
  () => renderMarkers(),
  { deep: true }
)

watch(
  () => store.selectedProperty,
  (property) => {
    if (!mapsApi || !map || !property?.latitude || !property?.longitude) return
    map.panTo(new mapsApi.LatLng(property.latitude, property.longitude))
  }
)

onMounted(async () => {
  document.addEventListener('mousedown', handleClickOutside)
  try {
    mapsApi = await loadNaverMaps()
    map = new mapsApi.Map(mapElement.value, {
      center: new mapsApi.LatLng(store.center.latitude, store.center.longitude),
      zoom: store.zoom,
      minZoom: 9,
      maxZoom: 21,
      scaleControl: false,
      mapDataControl: false,
      zoomControl: true,
      zoomControlOptions: {
        position: mapsApi.Position.RIGHT_CENTER
      }
    })
    idleListener = mapsApi.Event.addListener(map, 'idle', refreshFromMapBounds)
    await refreshFromMapBounds()
  } catch (error) {
    mapError.value = error.message || '지도 SDK 설정을 확인해주세요.'
    await store.fetchViewport()
  } finally {
    isMapLoading.value = false
  }
})

onBeforeUnmount(() => {
  document.removeEventListener('mousedown', handleClickOutside)
  if (idleListener) mapsApi?.Event.removeListener(idleListener)
  clearMarkers()
})

</script>

<style scoped>
.dual-slider {
  position: absolute;
  width: 100%;
  height: 100%;
  background: none;
  -webkit-appearance: none;
  appearance: none;
  pointer-events: none;
}

.dual-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  pointer-events: auto;
  width: 18px;
  height: 18px;
  background: #fff;
  border: 2.5px solid #0f172a;
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 1px 4px rgba(15, 23, 42, 0.18);
}

.dual-slider::-webkit-slider-runnable-track {
  background: none;
}

.dual-slider::-moz-range-thumb {
  pointer-events: auto;
  width: 18px;
  height: 18px;
  background: #fff;
  border: 2.5px solid #0f172a;
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 1px 4px rgba(15, 23, 42, 0.18);
}

.dual-slider::-moz-range-track {
  background: none;
}
</style>
