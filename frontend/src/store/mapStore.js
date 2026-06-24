import { defineStore } from 'pinia'
import { sendChatMessage } from '../api/chat'
import { fetchMapViewport, fetchPropertyDetail } from '../api/properties'

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
    isChatLoading: false,
    error: '',
    detailError: '',
    chatError: '',
    chatSessionId: null,
    chatMessages: [
      {
        role: 'bot',
        text: '계약서, 보증금 회수, 확정일자처럼 헷갈리는 전월세 법률 질문을 물어보세요.',
        legalCards: [],
        analysisCards: []
      }
    ],
    lastFetchedAt: null,
    requestSeq: 0,
    detailRequestSeq: 0,
    chatRequestSeq: 0
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
    async fetchViewport(bounds = this.bounds) {
      const seq = ++this.requestSeq
      this.isLoading = true
      this.error = ''
      this.setBounds(bounds)

      try {
        const data = await fetchMapViewport({
          ...this.bounds,
          zoom: this.zoom,
          ...this.filters
        })

        if (seq !== this.requestSeq) return

        this.viewportMode = data.mode || ''
        this.viewportItems = data.items || []
        this.properties = this.viewportItems.filter((item) => item.type === 'PROPERTY')
        this.totalCount = data.totalCount ?? this.viewportItems.length
        this.lastFetchedAt = new Date().toISOString()

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
    async sendChat(message) {
      const text = String(message || '').trim()
      if (!text || this.isChatLoading) return

      const seq = ++this.chatRequestSeq
      this.chatMessages.push({ role: 'user', text })
      this.isChatLoading = true
      this.chatError = ''

      try {
        const response = await sendChatMessage({
          message: text,
          sessionId: this.chatSessionId,
          selectedPropertyId: this.selectedPropertyId
        })

        if (seq !== this.chatRequestSeq) return

        this.chatSessionId = response.sessionId || this.chatSessionId
        this.chatMessages.push({
          role: 'bot',
          text: response.message,
          intent: response.intent,
          legalCards: response.legalCards,
          analysisCards: response.analysisCards,
          properties: response.properties
        })
      } catch (error) {
        if (seq !== this.chatRequestSeq) return
        this.chatError = error.response?.data?.message || 'AI 계약 상담 응답을 불러오지 못했습니다.'
        this.chatMessages.push({
          role: 'bot',
          text: this.chatError,
          isError: true,
          legalCards: [],
          analysisCards: []
        })
      } finally {
        if (seq === this.chatRequestSeq) {
          this.isChatLoading = false
        }
      }
    }
  }
})
