import { defineStore } from 'pinia'

const propertiesByRegion = {
  gwanak: [
    {
      id: 1,
      region: 'gwanak',
      name: '가온 리빙 하우스',
      type: '원룸(다가구)',
      deposit: 10000,
      rent: 45,
      marketPrice: 20000,
      publicPrice: 12000,
      seniorDeposits: 4000,
      collateral: 3000,
      address: '서울 관악구 대학동 1533-5',
      safetyScore: 94,
      crimeGrade: '1등급 (최상)',
      cctvs: 8,
      lamps: '최상',
      policeDist: '80m',
      description: '생활안전지도 기준 5대 범죄율 발생이 낮은 안심 치안 구역입니다. 야간 안심 조명이 보행로 전체에 확보되어 있습니다.',
      x: 180,
      y: 160,
      historicalPrices: [8000, 9000, 9500, 10000],
      reviews: [
        { user: '동글이', date: '2025.11', content: '여성안심귀갓길 바로 연결되어서 밤늦게 가도 골목이 밝아요.', rate: 5 },
        { user: '코딩새내기', date: '2026.01', content: '방음도 나쁘지 않고 편의점 접근성이 좋습니다. 다만 언덕길이 조금 있어요.', rate: 4 }
      ]
    },
    {
      id: 2,
      region: 'gwanak',
      name: '대학동 그린 원룸',
      type: '원룸(다가구)',
      deposit: 12000,
      rent: 38,
      marketPrice: 15000,
      publicPrice: 9000,
      seniorDeposits: 5000,
      collateral: 4000,
      address: '서울 관악구 대학동 1511-12',
      safetyScore: 68,
      crimeGrade: '4등급 (보통)',
      cctvs: 3,
      lamps: '보통',
      policeDist: '350m',
      description: '가로등 조도가 낮고 CCTV 밀도가 낮습니다. 일부 범죄주의구간과 겹쳐 밤길 보행 시 큰 도로 위주 이동이 권장됩니다.',
      x: 380,
      y: 280,
      historicalPrices: [10000, 11000, 11500, 12000],
      reviews: [
        { user: '자취의신', date: '2025.08', content: '가격은 낮은 편이지만 밤에는 골목이 어두워요.', rate: 3 }
      ]
    },
    {
      id: 3,
      region: 'gwanak',
      name: '샤로수 스마트 텔',
      type: '오피스텔(공동주택)',
      deposit: 16000,
      rent: 65,
      marketPrice: 22000,
      publicPrice: 14000,
      seniorDeposits: 0,
      collateral: 2000,
      address: '서울 관악구 청룡동 860-2',
      safetyScore: 88,
      crimeGrade: '2등급 (우수)',
      cctvs: 12,
      lamps: '우수',
      policeDist: '150m',
      description: '대로변에 위치해 조도가 균일하고 건물 내 보안 인프라가 우수합니다. 상권 밀집 구역과 가까워 주말 소음은 확인이 필요합니다.',
      x: 250,
      y: 320,
      historicalPrices: [14000, 15000, 15500, 16000],
      reviews: [
        { user: '안전제일', date: '2026.01', content: 'CCTV가 많고 관리가 잘 되어 택배 분실 걱정이 적습니다.', rate: 5 }
      ]
    }
  ],
  mapo: [
    {
      id: 4,
      region: 'mapo',
      name: '홍대 가온 빌라',
      type: '투룸(다세대주택)',
      deposit: 18000,
      rent: 60,
      marketPrice: 24000,
      publicPrice: 13000,
      seniorDeposits: 0,
      collateral: 3000,
      address: '서울 마포구 서교동 365-4',
      safetyScore: 72,
      crimeGrade: '5등급 (유흥가 인접 우려)',
      cctvs: 9,
      lamps: '최상',
      policeDist: '100m',
      description: '파출소와 가로등은 가깝지만 주변 유흥 상권 밀도가 높아 주말 야간 소음과 경범죄 주의가 필요합니다.',
      x: 200,
      y: 200,
      historicalPrices: [15000, 16000, 17500, 18000],
      reviews: [
        { user: '홍대생', date: '2025.12', content: '밝기는 밝은데 주말 새벽에는 외부 소음이 있습니다.', rate: 3 }
      ]
    }
  ]
}

const infraByRegion = {
  gwanak: {
    cctvs: [{ x: 100, y: 120 }, { x: 190, y: 150 }, { x: 210, y: 170 }, { x: 310, y: 290 }],
    lamps: [{ x: 140, y: 80 }, { x: 230, y: 190 }, { x: 350, y: 220 }],
    polices: [{ x: 150, y: 150, desc: '대학동안심치안센터' }],
    paths: [{ x1: 50, y1: 50, x2: 150, y2: 150 }, { x1: 150, y1: 150, x2: 250, y2: 320 }],
    crimeZones: ['130,220 180,240 220,180 150,170'],
    mainRoads: [
      [50, 50, 450, 50], [150, 50, 150, 400], [150, 320, 450, 320]
    ],
    subRoads: [[300, 50, 300, 320], [50, 180, 150, 180]]
  },
  mapo: {
    cctvs: [{ x: 120, y: 150 }, { x: 220, y: 180 }],
    lamps: [{ x: 150, y: 250 }, { x: 300, y: 100 }],
    polices: [{ x: 210, y: 210, desc: '서교 파출소' }],
    paths: [{ x1: 100, y1: 100, x2: 210, y2: 210 }],
    crimeZones: ['180,180 250,190 240,250 170,240'],
    mainRoads: [[50, 100, 450, 100], [210, 50, 210, 420]],
    subRoads: [[50, 250, 450, 250]]
  }
}

export default defineStore('map', {
  state: () => ({
    currentRegion: 'gwanak',
    selectedPropertyId: null,
    favorites: [1, 3],
    searchKeyword: '',
    filterType: 'all',
    sortType: 'safe',
    activeLayers: {
      cctv: true,
      lamp: true,
      police: true,
      path: true,
      crimeZone: true
    },
    weights: {
      safety: 40,
      price: 30,
      traffic: 20,
      life: 10
    },
    calcBuildingType: 'multi',
    communityPosts: [
      { id: 1, region: 'gwanak', title: '가온 리빙 하우스 뒤쪽 골목 방범등 수리 완료', category: '치안 및 안전', content: 'LED 보안등으로 교체되어 퇴근길 체감 조도가 확실히 좋아졌습니다.', author: '가온골목대장', rate: 5, date: '2026-05-20' },
      { id: 2, region: 'gwanak', title: '대학동 녹두거리 계단 지름길 밤길 주의', category: '실거주 꿀팁', content: '골목 일부가 어두워서 3분 더 걸려도 대로변 안심귀갓길로 우회하는 편이 좋습니다.', author: '치안순찰대', rate: 2, date: '2026-05-18' }
    ],
    chatMessages: [
      { role: 'bot', text: '안녕하세요! HUG 126% 기준, 다가구 선순위 보증금, 임대인 세금 체납 확인 등 안전 계약 질문을 도와드릴게요.' }
    ]
  }),
  getters: {
    regions: () => [
      { value: 'gwanak', label: '서울시 관악구 대학동', desc: '청년 원룸 밀집 구역' },
      { value: 'mapo', label: '서울시 마포구 서교동', desc: '유흥 상권 인접지' }
    ],
    currentProperties: (state) => propertiesByRegion[state.currentRegion],
    currentInfra: (state) => infraByRegion[state.currentRegion],
    allProperties: () => Object.values(propertiesByRegion).flat(),
    selectedProperty(state) {
      return Object.values(propertiesByRegion).flat().find((property) => property.id === state.selectedPropertyId) || null
    },
    filteredProperties(state) {
      const keyword = state.searchKeyword.trim().toLowerCase()
      let list = [...propertiesByRegion[state.currentRegion]]
      if (keyword) {
        list = list.filter((property) => property.name.toLowerCase().includes(keyword) || property.address.toLowerCase().includes(keyword))
      }
      if (state.filterType !== 'all') {
        list = list.filter((property) => property.type.includes(state.filterType))
      }
      if (state.sortType === 'safe') list.sort((a, b) => b.safetyScore - a.safetyScore)
      if (state.sortType === 'price-low') list.sort((a, b) => (a.deposit + a.rent * 100) - (b.deposit + b.rent * 100))
      return list
    },
    communityForCurrentRegion(state) {
      return state.communityPosts.filter((post) => post.region === state.currentRegion)
    },
    regionStatus(state) {
      if (state.currentRegion === 'gwanak') return { text: '치안 안전 최고 1등급지', tone: 'text-emerald-700' }
      return { text: '유흥인접 폭력/경범죄 주의구간 포함', tone: 'text-rose-600' }
    }
  },
  actions: {
    setRegion(region) {
      this.currentRegion = region
      this.selectedPropertyId = null
    },
    selectProperty(id) {
      this.selectedPropertyId = id
    },
    closeProperty() {
      this.selectedPropertyId = null
    },
    toggleLayer(layerKey) {
      this.activeLayers[layerKey] = !this.activeLayers[layerKey]
    },
    toggleFavorite(id) {
      const index = this.favorites.indexOf(id)
      if (index >= 0) this.favorites.splice(index, 1)
      else this.favorites.push(id)
    },
    setWeight(key, value) {
      this.weights[key] = Number(value)
    },
    addCommunityPost(payload) {
      this.communityPosts.unshift({
        id: this.communityPosts.length + 1,
        region: this.currentRegion,
        date: new Date().toISOString().slice(0, 10),
        ...payload
      })
    },
    sendChat(text) {
      const message = text.trim()
      if (!message) return
      this.chatMessages.push({ role: 'user', text: message })
      let answer = '다세대인지 다가구인지 등기 상태를 먼저 확인해 주세요. 이후 공시가격, 보증금, 선순위 권리, 세금 체납 여부를 함께 검토하면 위험도를 더 정확히 판단할 수 있습니다.'
      if (message.includes('126') || message.includes('보증보험') || message.includes('HUG')) {
        answer = 'HUG 126% 기준은 공시가격 × 140% × 90%로 계산합니다. 즉 보증금이 공시가격의 126%를 초과하면 반환보증 가입이 어려울 수 있어 계약 전 공시가격과 보증금을 반드시 비교해야 합니다.'
      } else if (message.includes('다가구') || message.includes('선순위')) {
        answer = '다가구 주택은 호실별 개별 등기가 아니라 건물 전체 기준으로 권리관계가 얽힙니다. 내 보증금보다 먼저 배당받는 기존 세입자 보증금 총합을 확인해야 하며, 선순위 임차인 정보 제공 확인서를 요구하는 것이 좋습니다.'
      } else if (message.includes('세금') || message.includes('체납')) {
        answer = '임대인의 국세·지방세 체납은 경매 배당에서 세입자보다 앞설 수 있습니다. 계약 전 국세 및 지방세 완납증명서 제출 또는 미납 국세 열람 동의를 특약으로 두는 편이 안전합니다.'
      }
      this.chatMessages.push({ role: 'bot', text: answer })
    }
  }
})
