import assert from 'node:assert/strict'
import { test } from 'node:test'
import { createPinia, setActivePinia } from 'pinia'

import useMapStore from './mapStore.js'

const createStore = () => {
  setActivePinia(createPinia())
  return useMapStore()
}

test('viewport summary selection clears when property marker results arrive', () => {
  const store = createStore()
  store.selectViewportItem({ type: 'REGION_AVG', regionLevel: 'SIDO', regionName: '서울특별시' })

  store.applyViewportData({
    mode: 'PROPERTY_MARKER',
    items: [
      {
        type: 'PROPERTY',
        id: 1,
        title: '관악구 원룸',
        latitude: 37.470123,
        longitude: 126.936456
      }
    ],
    totalCount: 1
  })

  assert.equal(store.selectedViewportItem, null)
  assert.equal(store.properties.length, 1)
  assert.equal(store.properties[0].id, 1)
})

test('viewport summary selection remains for non-property viewport results', () => {
  const store = createStore()
  const selectedItem = { type: 'REGION_AVG', regionLevel: 'SIDO', regionName: '서울특별시' }
  store.selectViewportItem(selectedItem)

  store.applyViewportData({
    mode: 'SIDO_AVG',
    items: [
      {
        type: 'REGION_AVG',
        regionLevel: 'SIDO',
        regionName: '서울특별시',
        avgMonthlyRent: 550000
      }
    ],
    totalCount: 1
  })

  assert.deepEqual(store.selectedViewportItem, selectedItem)
  assert.equal(store.properties.length, 0)
})
