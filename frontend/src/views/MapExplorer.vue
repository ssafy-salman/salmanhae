<template>
  <div class="grid grid-cols-1 gap-4 lg:grid-cols-12">
    <section class="relative h-[660px] overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm lg:col-span-8">
      <div class="absolute left-3 right-3 top-3 z-20 space-y-2">
        <form class="flex flex-col gap-2 rounded-2xl border border-slate-200 bg-white/95 p-3 shadow-sm backdrop-blur md:flex-row md:items-center" @submit.prevent="refreshFromFilters">
          <label class="flex min-w-0 flex-1 items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2">
            <Search class="h-4 w-4 shrink-0 text-slate-400" aria-hidden="true" />
            <input
              v-model="store.searchKeyword"
              class="w-full bg-transparent text-sm font-semibold text-slate-800 outline-none placeholder:text-slate-400"
              type="search"
              placeholder="건물명 또는 주소 검색"
            />
          </label>
          <button class="inline-flex items-center justify-center gap-2 rounded-xl bg-slate-900 px-4 py-2 text-sm font-bold text-white transition hover:bg-slate-800" type="submit">
            <RotateCw class="h-4 w-4" aria-hidden="true" />
            조회
          </button>
        </form>

        <form class="grid grid-cols-2 gap-2 rounded-2xl border border-slate-200 bg-white/95 p-3 shadow-sm backdrop-blur md:grid-cols-6" @submit.prevent="refreshFromFilters">
          <label class="filter-field">
            <span>거래</span>
            <select v-model="store.filters.transactionType">
              <option value="">전체</option>
              <option value="MONTHLY_RENT">월세</option>
              <option value="JEONSE">전세</option>
              <option value="SALE">매매</option>
            </select>
          </label>
          <label class="filter-field">
            <span>유형</span>
            <select v-model="store.filters.propertyType">
              <option value="">전체</option>
              <option value="ONE_ROOM">원룸</option>
              <option value="OFFICETEL">오피스텔</option>
              <option value="APARTMENT">아파트</option>
              <option value="VILLA">빌라</option>
              <option value="MULTI_FAMILY">단독/다가구</option>
            </select>
          </label>
          <label class="filter-field">
            <span>보증금 최소</span>
            <input v-model="store.filters.minDeposit" min="0" step="1000000" type="number" placeholder="원" />
          </label>
          <label class="filter-field">
            <span>보증금 최대</span>
            <input v-model="store.filters.maxDeposit" min="0" step="1000000" type="number" placeholder="원" />
          </label>
          <label class="filter-field">
            <span>매매가 최소</span>
            <input v-model="store.filters.minPrice" min="0" step="10000000" type="number" placeholder="원" />
          </label>
          <div class="flex items-end gap-2">
            <button class="h-10 flex-1 rounded-xl border border-slate-300 bg-white px-3 text-xs font-black text-slate-700 transition hover:bg-slate-50" type="button" @click="resetFilters">
              초기화
            </button>
            <button class="h-10 rounded-xl bg-brand px-3 text-xs font-black text-white transition hover:bg-brand-dark" type="submit">
              적용
            </button>
          </div>
        </form>
      </div>

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
          <h2 class="mt-3 text-sm font-black text-slate-900">네이버 지도를 불러오지 못했습니다</h2>
          <p class="mt-2 text-xs leading-5 text-slate-500">{{ mapError }}</p>
          <p class="mt-3 text-xs font-bold text-slate-600">매물 목록은 기본 지도 범위로 조회됩니다.</p>
        </div>
      </div>

      <div class="absolute bottom-3 left-3 z-20 flex flex-wrap items-center gap-2 rounded-2xl border border-slate-200 bg-white/95 px-3 py-2 text-xs font-bold text-slate-600 shadow-sm backdrop-blur">
        <MapPin class="h-4 w-4 text-brand" aria-hidden="true" />
        <span>{{ store.totalCount.toLocaleString() }}개 매물</span>
        <span v-if="store.lastFetchedAt" class="text-slate-400">{{ formattedFetchedAt }}</span>
      </div>
    </section>

    <aside class="flex h-[660px] flex-col gap-4 lg:col-span-4">
      <section class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
        <div class="flex items-center justify-between gap-3">
          <div>
            <p class="text-[11px] font-black uppercase text-brand-dark">F-1 Property Search</p>
            <h2 class="mt-1 text-lg font-black text-slate-900">지도 범위 매물</h2>
          </div>
          <SlidersHorizontal class="h-5 w-5 text-slate-400" aria-hidden="true" />
        </div>
        <p class="mt-2 text-xs leading-5 text-slate-500">현재 지도 화면 안의 매물을 Spring Boot API에서 조회합니다.</p>
      </section>

      <section class="min-h-0 flex-1 overflow-y-auto rounded-2xl border border-slate-200 bg-white p-3 shadow-sm">
        <div v-if="store.isLoading" class="flex h-full items-center justify-center text-sm font-bold text-slate-500">
          <Loader2 class="mr-2 h-4 w-4 animate-spin" aria-hidden="true" />
          매물을 불러오는 중입니다
        </div>

        <div v-else-if="store.error" class="flex h-full items-center justify-center p-6 text-center">
          <div>
            <AlertTriangle class="mx-auto h-8 w-8 text-rose-500" aria-hidden="true" />
            <p class="mt-3 text-sm font-black text-slate-900">매물 API 오류</p>
            <p class="mt-2 text-xs leading-5 text-slate-500">{{ store.error }}</p>
          </div>
        </div>

        <div v-else-if="store.filteredProperties.length === 0" class="flex h-full items-center justify-center p-6 text-center">
          <div>
            <Home class="mx-auto h-8 w-8 text-slate-300" aria-hidden="true" />
            <p class="mt-3 text-sm font-black text-slate-900">표시할 매물이 없습니다</p>
            <p class="mt-2 text-xs leading-5 text-slate-500">지도를 조금 넓히거나 필터를 초기화해보세요.</p>
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
                <p class="truncate text-sm font-black text-slate-900">{{ displayTitle(property) }}</p>
                <p class="mt-1 truncate text-xs font-semibold text-slate-500">{{ property.address }}</p>
              </div>
              <span class="shrink-0 rounded-full bg-white px-2 py-1 text-[10px] font-black text-slate-600">{{ propertyTypeLabel(property.propertyType) }}</span>
            </div>
            <div class="mt-3 flex items-center justify-between gap-3 border-t border-slate-200/70 pt-3">
              <span class="text-sm font-black text-slate-900">{{ priceText(property) }}</span>
              <span class="rounded-full bg-slate-900 px-2 py-1 text-[10px] font-black text-white">{{ transactionLabel(property.transactionType) }}</span>
            </div>
            <p class="mt-2 text-xs font-semibold text-slate-500">{{ areaText(property) }} · {{ floorText(property) }}</p>
          </article>
        </div>
      </section>
    </aside>

    <transition name="slide">
      <section v-if="store.selectedProperty" class="fixed inset-y-0 right-0 z-[100] w-full overflow-y-auto border-l border-slate-200 bg-white shadow-2xl md:w-[440px]">
        <div class="sticky top-0 z-10 flex items-center justify-between border-b border-slate-100 bg-white/95 p-4 backdrop-blur">
          <div class="flex items-center gap-2">
            <span class="rounded-full bg-brand-light px-2 py-1 text-[10px] font-black text-brand-dark">{{ transactionLabel(store.selectedProperty.transactionType) }}</span>
            <span class="text-xs font-bold text-slate-400">No. {{ store.selectedProperty.id }}</span>
          </div>
          <button class="flex h-9 w-9 items-center justify-center rounded-full bg-slate-100 text-slate-600 transition hover:bg-slate-200" type="button" @click="store.closeProperty">
            <X class="h-4 w-4" aria-hidden="true" />
            <span class="sr-only">닫기</span>
          </button>
        </div>

        <div class="space-y-5 p-5">
          <div>
            <p class="text-xs font-black text-brand-dark">{{ propertyTypeLabel(store.selectedProperty.propertyType) }}</p>
            <h2 class="mt-1 text-2xl font-black text-slate-900">{{ displayTitle(store.selectedProperty) }}</h2>
            <p class="mt-2 text-sm leading-6 text-slate-500">{{ store.selectedProperty.address }}</p>
            <p v-if="store.selectedProperty.roadAddress" class="text-xs leading-5 text-slate-400">{{ store.selectedProperty.roadAddress }}</p>
          </div>

          <div class="rounded-2xl border border-brand/20 bg-brand-light p-4">
            <p class="text-xs font-black text-brand-dark">가격</p>
            <p class="mt-1 text-xl font-black text-slate-900">{{ priceText(store.selectedProperty) }}</p>
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
            <div class="detail-stat">
              <span>법정동 코드</span>
              <b>{{ store.selectedProperty.legalDongCode || '-' }}</b>
            </div>
          </div>

          <div v-if="store.detailError" class="rounded-2xl border border-rose-100 bg-rose-50 p-4 text-xs font-bold leading-5 text-rose-700">
            {{ store.detailError }}
          </div>

          <div v-if="store.isDetailLoading" class="flex items-center justify-center rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm font-bold text-slate-500">
            <Loader2 class="mr-2 h-4 w-4 animate-spin" aria-hidden="true" />
            상세 정보를 불러오는 중입니다
          </div>

          <div v-if="store.selectedProperty.description" class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <div class="flex items-center gap-2">
              <Building2 class="h-4 w-4 text-slate-400" aria-hidden="true" />
              <h3 class="text-sm font-black text-slate-900">매물 메모</h3>
            </div>
            <p class="mt-3 text-sm leading-6 text-slate-600">{{ store.selectedProperty.description }}</p>
          </div>
        </div>
      </section>
    </transition>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import {
  AlertTriangle,
  Building2,
  Home,
  Loader2,
  MapPin,
  RotateCw,
  Search,
  SlidersHorizontal,
  X
} from '@lucide/vue'
import useMapStore from '../store/mapStore'
import { loadNaverMaps } from '../utils/naverMaps'

const store = useMapStore()
const mapElement = ref(null)
const isMapLoading = ref(true)
const mapError = ref('')

let mapsApi = null
let map = null
let idleListener = null
let markers = []
let markerListeners = []

const formattedFetchedAt = computed(() => {
  if (!store.lastFetchedAt) return ''
  return new Intl.DateTimeFormat('ko-KR', {
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(store.lastFetchedAt))
})

const displayTitle = (property) => property.title || property.buildingName || `매물 ${property.id}`

const transactionLabel = (type) => ({
  MONTHLY_RENT: '월세',
  JEONSE: '전세',
  SALE: '매매'
}[type] || '거래')

const propertyTypeLabel = (type) => ({
  ONE_ROOM: '원룸',
  OFFICETEL: '오피스텔',
  APARTMENT: '아파트',
  VILLA: '빌라',
  MULTI_FAMILY: '단독/다가구'
}[type] || '주거')

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

const areaText = (property) => {
  if (!property.areaM2) return '면적 정보 없음'
  const pyeong = Number(property.areaM2) / 3.3058
  return `${Number(property.areaM2).toFixed(1)}m² (${pyeong.toFixed(1)}평)`
}

const floorText = (property) => {
  const floor = property.floor ? `${property.floor}층` : '층수 미상'
  return property.totalFloor ? `${floor} / ${property.totalFloor}층` : floor
}

const getMapBounds = () => {
  const bounds = map.getBounds()
  const sw = bounds.getSW()
  const ne = bounds.getNE()
  return {
    west: sw.lng(),
    south: sw.lat(),
    east: ne.lng(),
    north: ne.lat()
  }
}

const markerContent = (property, isSelected) => {
  const background = isSelected ? '#101311' : '#1ABC9C'
  const label = property.transactionType === 'SALE' ? formatWons(property.price) : formatWons(property.deposit)

  return `
    <button type="button" style="
      position: relative;
      min-width: 74px;
      border: 2px solid #fff;
      border-radius: 14px;
      background: ${background};
      color: #fff;
      padding: 7px 10px;
      font-size: 12px;
      font-weight: 900;
      line-height: 1;
      box-shadow: 0 10px 24px rgba(15, 23, 42, 0.22);
      cursor: pointer;
      white-space: nowrap;
    ">
      ${transactionLabel(property.transactionType)} ${label}
      <span style="
        position: absolute;
        left: 50%;
        bottom: -6px;
        width: 10px;
        height: 10px;
        transform: translateX(-50%) rotate(45deg);
        background: ${background};
        border-right: 2px solid #fff;
        border-bottom: 2px solid #fff;
      "></span>
    </button>
  `
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

  store.filteredProperties.forEach((property) => {
    if (!property.latitude || !property.longitude) return

    const marker = new mapsApi.Marker({
      position: new mapsApi.LatLng(property.latitude, property.longitude),
      map,
      icon: {
        content: markerContent(property, store.selectedPropertyId === property.id),
        anchor: new mapsApi.Point(42, 44)
      }
    })
    const listener = mapsApi.Event.addListener(marker, 'click', () => store.selectProperty(property.id))
    markers.push(marker)
    markerListeners.push(listener)
  })
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
  await store.fetchViewport(getMapBounds())
}

const refreshFromFilters = async () => {
  await refreshFromMapBounds()
}

const resetFilters = async () => {
  store.resetFilters()
  await refreshFromMapBounds()
}

watch(
  [() => store.filteredProperties, () => store.selectedPropertyId],
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
  try {
    mapsApi = await loadNaverMaps()
    map = new mapsApi.Map(mapElement.value, {
      center: new mapsApi.LatLng(store.center.latitude, store.center.longitude),
      zoom: store.zoom,
      minZoom: 9,
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
  if (idleListener) mapsApi?.Event.removeListener(idleListener)
  clearMarkers()
})
</script>
