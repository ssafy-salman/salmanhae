import { defineStore } from 'pinia'
import { fetchProperties, fetchPropertyDetail } from '../api/properties'

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

const toNumberOrEmpty = (value) => {
  if (value === '' || value === null || value === undefined) return ''
  const numberValue = Number(value)
  return Number.isFinite(numberValue) ? numberValue : ''
}

export default defineStore('map', {
  state: () => ({
    currentRegion: 'seoul',
    selectedPropertyId: null,
    selectedProperty: null,
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
    requestSeq: 0
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
        const title = property.title || property.buildingName || ''
        const address = property.address || property.roadAddress || ''
        return title.toLowerCase().includes(keyword) || address.toLowerCase().includes(keyword)
      })
    },
    regionStatus(state) {
      if (state.error) return { text: '매물 API 확인 필요', tone: 'text-rose-600' }
      if (state.isLoading) return { text: '매물 불러오는 중', tone: 'text-slate-600' }
      return { text: `${state.totalCount.toLocaleString()}개 매물 표시`, tone: 'text-emerald-700' }
    },
    hasActiveFilters(state) {
      return Object.values(state.filters).some((value) => value !== '')
    }
  },
  actions: {
    setRegion(region) {
      this.currentRegion = region
    },
    setBounds(bounds) {
      this.bounds = {
        west: Number(bounds.west),
        east: Number(bounds.east),
        south: Number(bounds.south),
        north: Number(bounds.north)
      }
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
    setFilter(key, value) {
      if (!(key in this.filters)) return
      if (['minDeposit', 'maxDeposit', 'minPrice', 'maxPrice'].includes(key)) {
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
    },
    async fetchProperties(bounds = this.bounds) {
      const seq = ++this.requestSeq
      this.isLoading = true
      this.error = ''
      this.setBounds(bounds)

      try {
        const data = await fetchProperties({
          ...this.bounds,
          ...this.filters
        })

        if (seq !== this.requestSeq) return

        this.properties = data.items || []
        this.totalCount = data.totalCount ?? this.properties.length
        this.lastFetchedAt = new Date().toISOString()

        if (this.selectedPropertyId && !this.properties.some((property) => property.id === this.selectedPropertyId)) {
          this.selectedPropertyId = null
          this.selectedProperty = null
        }
      } catch (error) {
        if (seq !== this.requestSeq) return
        this.error = error.response?.data?.message || '매물 데이터를 불러오지 못했습니다.'
        this.properties = []
        this.totalCount = 0
      } finally {
        if (seq === this.requestSeq) {
          this.isLoading = false
        }
      }
    },
    async selectProperty(id) {
      this.selectedPropertyId = id
      this.detailError = ''
      this.selectedProperty = this.properties.find((property) => property.id === id) || null
      this.isDetailLoading = true

      try {
        this.selectedProperty = await fetchPropertyDetail(id)
      } catch (error) {
        this.detailError = error.response?.data?.message || '매물 상세 정보를 불러오지 못했습니다.'
      } finally {
        this.isDetailLoading = false
      }
    },
    closeProperty() {
      this.selectedPropertyId = null
      this.selectedProperty = null
      this.detailError = ''
    }
  }
})
