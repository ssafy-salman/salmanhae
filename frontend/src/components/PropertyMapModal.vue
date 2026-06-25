<template>
  <Teleport to="body">
    <div class="modal-backdrop" @click.self="$emit('close')">
      <div class="modal">
        <div class="modal-header">
          <div class="modal-header__info">
            <p class="modal-header__tag">{{ propTypeLabel(prop.property_type) }} · {{ txTypeLabel(prop.transaction_type) }}</p>
            <h3 class="modal-header__title">{{ prop.building_name || prop.title }}</h3>
            <p class="modal-header__address">{{ prop.address }}</p>
          </div>
          <div class="modal-header__right">
            <p class="modal-header__price">{{ formatPropertyPrice(prop) }}</p>
            <button class="modal-close" @click="$emit('close')">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
        </div>

        <div class="modal-map-wrap">
          <div v-if="mapError" class="map-error">{{ mapError }}</div>
          <div v-else ref="mapEl" class="map-container" />
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref } from 'vue'
import { loadNaverMaps } from '../utils/naverMaps.js'

const props = defineProps({
  prop: { type: Object, required: true }
})
defineEmits(['close'])

const mapEl = ref(null)
const mapError = ref('')
let map = null
let marker = null

const propTypeLabels = { ONE_ROOM: '원룸', OFFICETEL: '오피스텔', VILLA: '빌라', APARTMENT: '아파트', MULTI_FAMILY: '다가구' }
const txTypeLabels = { MONTHLY_RENT: '월세', JEONSE: '전세', SALE: '매매' }
const propTypeLabel = (t) => propTypeLabels[t] || t || ''
const txTypeLabel = (t) => txTypeLabels[t] || t || ''
const toMan = (won) => Math.round(Number(won || 0) / 10000).toLocaleString()
const formatPropertyPrice = (p) => {
  if (p.transaction_type === 'MONTHLY_RENT') return `${toMan(p.deposit)}/${toMan(p.monthly_rent)}만원`
  if (p.transaction_type === 'JEONSE') return `전세 ${toMan(p.deposit)}만원`
  if (p.transaction_type === 'SALE') return `매매 ${toMan(p.price)}만원`
  return ''
}

onMounted(async () => {
  const lat = Number(props.prop.latitude)
  const lng = Number(props.prop.longitude)
  if (!Number.isFinite(lat) || !Number.isFinite(lng)) {
    mapError.value = '이 매물은 지도 좌표 정보가 없습니다.'
    return
  }

  try {
    const mapsApi = await loadNaverMaps()
    const center = new mapsApi.LatLng(lat, lng)
    map = new mapsApi.Map(mapEl.value, {
      center,
      zoom: 17,
      scaleControl: false,
      mapDataControl: false,
      zoomControl: true,
      zoomControlOptions: { position: mapsApi.Position.RIGHT_CENTER }
    })
    marker = new mapsApi.Marker({
      position: center,
      map,
      icon: {
        content: `<div style="
          width:20px;height:20px;border-radius:50%;
          background:#01bfa6;border:3px solid #fff;
          box-shadow:0 2px 8px rgba(1,191,166,0.5);
        "></div>`,
        anchor: new mapsApi.Point(10, 10)
      }
    })
  } catch (e) {
    mapError.value = '지도를 불러오지 못했습니다.'
  }
})

onBeforeUnmount(() => {
  marker?.setMap(null)
  map?.destroy?.()
})
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.modal {
  width: 100%;
  max-width: 600px;
  background: #fff;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding: 18px 20px 16px;
  border-bottom: 1px solid #f0f0f0;
}

.modal-header__tag {
  font-size: 11px;
  font-weight: 700;
  color: #01bfa6;
  margin-bottom: 4px;
}

.modal-header__title {
  font-size: 15px;
  font-weight: 700;
  color: #111827;
}

.modal-header__address {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 2px;
}

.modal-header__right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
  flex-shrink: 0;
}

.modal-header__price {
  font-size: 14px;
  font-weight: 700;
  color: #01bfa6;
  white-space: nowrap;
}

.modal-close {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: #f3f4f6;
  border-radius: 8px;
  cursor: pointer;
  color: #6b7280;
  transition: background 0.13s, color 0.13s;
}

.modal-close:hover {
  background: #e5e7eb;
  color: #111827;
}

.modal-close svg {
  width: 14px;
  height: 14px;
}

.modal-map-wrap {
  height: 380px;
  position: relative;
}

.map-container {
  width: 100%;
  height: 100%;
}

.map-error {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  font-size: 13px;
  color: #9ca3af;
}
</style>
