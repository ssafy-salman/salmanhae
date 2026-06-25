// 채팅 관련 state/action은 chatSessionStore로 이관됨
import { defineStore } from 'pinia'
import { fetchMapViewport, fetchPropertyDetail } from '../api/properties.js'
import { isPropertyItem, VIEWPORT_MODES } from '../utils/mapViewport.js'

const DEFAULT_BOUNDS = {
  west: 126.76,
  east: 127.18,
  south: 37.42,
  north: 37.66
}

const DEFAULT_CENTER = {
  latitude: 37.5665,
  longitude: 126.978
}

const MONEY_UNIT = 10000
const MONEY_FILTER_KEYS = ['minDeposit', 'maxDeposit', 'minPrice', 'maxPrice']
const DISABLE_DEPOSIT_TRANSACTION_TYPES = ['JEONSE', 'SALE']

const toNumberOrEmpty = (value) => {
  if (value === '' || value === null || value === undefined) return ''
  const numberValue = Number(value)
  return Number.isFinite(numberValue) ? numberValue : ''
}

const toWonOrEmpty = (value) => {
  const numberValue = toNumberOrEmpty(value)
  return numberValue === '' ? '' : numberValue * MONEY_UNIT
}

const normalizeBounds = (bounds) => {
  if (!bounds) return null
  const normalized = {
    west: Number(bounds.west),
    east: Number(bounds.east),
    south: Number(bounds.south),
    north: Number(bounds.north)
  }
  const hasFiniteValues = Object.values(normalized).every(Number.isFinite)
  if (!hasFiniteValues) return null
  if (normalized.west < -180 || normalized.east > 180 || normalized.south < -90 || normalized.north > 90) return null
  if (normalized.west >= normalized.east || normalized.south >= normalized.north) return null
  return normalized
}

export default defineStore('map', {
  state: () => ({
    currentRegion: 'seoul',
    selectedPropertyId: null,
    selectedProperty: null,
    selectedViewportItem: null,
    viewportMode: '',
    viewportItems: [],
    properties: [],
    totalCount: 0,
    bounds: { ...DEFAULT_BOUNDS },
    center: { ...DEFAULT_CENTER },
    zoom: 12,
    searchKeyword: '',
    filters: {
      transactionType: '',
      propertyType: '',
      minDeposit: '',
      maxDeposit: '',
      minPrice: '',
      maxPrice: ''
    },
    isLoading: false,
    isDetailLoading: false,
    error: '',
    detailError: '',
    lastFetchedAt: null,
    requestSeq: 0,
    detailRequestSeq: 0
  }),
  getters: {
    regions: () => [
      {
        value: 'seoul',
        label: '서울 주요 권역',
        desc: '시드 매물 조회'
      }
    ],
    currentProperties: (state) => state.properties,
    filteredProperties(state) {
      const keyword = state.searchKeyword.trim().toLowerCase()
      if (!keyword) return state.properties
      return state.properties.filter((property) => {
        const searchableText = [
          property.title,
          property.buildingName,
          property.address,
          property.roadAddress
        ].filter(Boolean).join(' ').toLowerCase()
        return searchableText.includes(keyword)
      })
    },
    regionStatus(state) {
      if (state.error) return { text: '매물 API 확인 필요', tone: 'text-rose-600' }
      if (state.isLoading) return { text: '매물 불러오는 중', tone: 'text-slate-600' }
      return { text: `${state.totalCount.toLocaleString()}개 매물 표시`, tone: 'text-emerald-700' }
    },
    normalizedSearchKeyword(state) {
      return state.searchKeyword.trim()
    },
    isDepositFilterDisabled(state) {
      return DISABLE_DEPOSIT_TRANSACTION_TYPES.includes(state.filters.transactionType)
    },
    apiFilters(state) {
      const isDepositDisabled = DISABLE_DEPOSIT_TRANSACTION_TYPES.includes(state.filters.transactionType)
      return {
        transactionType: state.filters.transactionType,
        propertyType: state.filters.propertyType,
        minDeposit: isDepositDisabled ? '' : toWonOrEmpty(state.filters.minDeposit),
        maxDeposit: isDepositDisabled ? '' : toWonOrEmpty(state.filters.maxDeposit),
        minPrice: toWonOrEmpty(state.filters.minPrice),
        maxPrice: toWonOrEmpty(state.filters.maxPrice)
      }
    },
    hasActiveFilters(state) {
      return Object.values(state.filters).some((value) => value !== '')
    },
    hasActiveSearchConditions() {
      return this.normalizedSearchKeyword !== '' || this.hasActiveFilters
    }
  },
  actions: {
    setRegion(region) {
      this.currentRegion = region
    },
    setBounds(bounds) {
      const normalized = normalizeBounds(bounds)
      if (!normalized) return false
      this.bounds = normalized
      return true
    },
    setCenter(center) {
      this.center = {
        latitude: Number(center.latitude),
        longitude: Number(center.longitude)
      }
    },
    setZoom(zoom) {
      this.zoom = Number(zoom)
    },
    setTransactionType(transactionType) {
      this.filters.transactionType = transactionType
      if (this.isDepositFilterDisabled) {
        this.filters.minDeposit = ''
        this.filters.maxDeposit = ''
      }
    },
    setFilter(key, value) {
      if (!(key in this.filters)) return
      if (key === 'transactionType') {
        this.setTransactionType(value)
        return
      }
      if (MONEY_FILTER_KEYS.includes(key)) {
        this.filters[key] = toNumberOrEmpty(value)
        return
      }
      this.filters[key] = value
    },
    resetFilters() {
      this.filters = {
        transactionType: '',
        propertyType: '',
        minDeposit: '',
        maxDeposit: '',
        minPrice: '',
        maxPrice: ''
      }
      this.searchKeyword = ''
      this.selectedViewportItem = null
    },
    applyViewportData(data) {
      this.viewportMode = data.mode || ''
      this.viewportItems = data.items || []
      this.properties = this.viewportItems.filter(isPropertyItem)
      this.totalCount = data.totalCount ?? this.viewportItems.length
      this.lastFetchedAt = new Date().toISOString()

      if (this.viewportMode === VIEWPORT_MODES.PROPERTY_MARKER || this.properties.length > 0) {
        this.selectedViewportItem = null
      }
    },
    async fetchViewport(bounds = this.bounds) {
      const seq = ++this.requestSeq
      this.isLoading = true
      this.error = ''
      this.setBounds(bounds)

      try {
        const data = await fetchMapViewport({
          ...this.bounds,
          zoom: this.zoom,
          keyword: this.normalizedSearchKeyword,
          ...this.apiFilters
        })

        if (seq !== this.requestSeq) return

        this.applyViewportData(data)

        if (this.selectedPropertyId && !this.properties.some((property) => property.id === this.selectedPropertyId)) {
          this.selectedPropertyId = null
          this.selectedProperty = null
        }
      } catch (error) {
        if (seq !== this.requestSeq) return
        this.error = error.response?.data?.message || '매물 데이터를 불러오지 못했습니다.'
        this.viewportMode = ''
        this.viewportItems = []
        this.properties = []
        this.totalCount = 0
      } finally {
        if (seq === this.requestSeq) {
          this.isLoading = false
        }
      }
    },
    async fetchProperties(bounds = this.bounds) {
      await this.fetchViewport(bounds)
    },
    async selectProperty(id) {
      const seq = ++this.detailRequestSeq
      this.selectedPropertyId = id
      this.selectedViewportItem = null
      this.detailError = ''
      this.selectedProperty = this.properties.find((property) => property.id === id) || null
      this.isDetailLoading = true

      try {
        const property = await fetchPropertyDetail(id)
        if (seq !== this.detailRequestSeq || this.selectedPropertyId !== id) return
        this.selectedProperty = property
      } catch (error) {
        if (seq !== this.detailRequestSeq || this.selectedPropertyId !== id) return
        this.detailError = error.response?.data?.message || '매물 상세 정보를 불러오지 못했습니다.'
      } finally {
        if (seq === this.detailRequestSeq) {
          this.isDetailLoading = false
        }
      }
    },
    closeProperty() {
      this.detailRequestSeq += 1
      this.selectedPropertyId = null
      this.selectedProperty = null
      this.detailError = ''
      this.isDetailLoading = false
    },
    selectViewportItem(item) {
      this.detailRequestSeq += 1
      this.selectedPropertyId = null
      this.selectedProperty = null
      this.detailError = ''
      this.isDetailLoading = false
      this.selectedViewportItem = item
    },
  }
})
