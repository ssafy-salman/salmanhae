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

test('selectViewportItem clears selected property transaction state', () => {
  const store = createStore()
  store.selectedPropertyId = 1
  store.selectedProperty = { id: 1, title: '정동' }
  store.selectedPropertyTransactions = [{ contractYearMonth: '2026-05', price: 610000000 }]
  store.selectedPropertyTransactionsTotal = 1
  store.transactionError = '이전 오류'
  store.isTransactionsLoading = true

  const selectedItem = { type: 'REGION_AVG', regionLevel: 'DONG', regionName: '정동' }
  store.selectViewportItem(selectedItem)

  assert.equal(store.selectedPropertyId, null)
  assert.equal(store.selectedProperty, null)
  assert.deepEqual(store.selectedPropertyTransactions, [])
  assert.equal(store.selectedPropertyTransactionsTotal, 0)
  assert.equal(store.transactionError, '')
  assert.equal(store.isTransactionsLoading, false)
  assert.deepEqual(store.selectedViewportItem, selectedItem)
})

test('setBounds keeps the last valid bounds when map reports a transient invalid range', () => {
  const store = createStore()
  const previousBounds = { ...store.bounds }

  assert.equal(store.setBounds({
    west: Number.NaN,
    east: 127.02,
    south: 37.45,
    north: 37.55
  }), false)
  assert.deepEqual(store.bounds, previousBounds)

  assert.equal(store.setBounds({
    west: 127.02,
    east: 126.91,
    south: 37.45,
    north: 37.55
  }), false)
  assert.deepEqual(store.bounds, previousBounds)
})

test('search condition state uses trimmed keyword', () => {
  const store = createStore()

  store.searchKeyword = '   '
  assert.equal(store.normalizedSearchKeyword, '')
  assert.equal(store.hasActiveSearchConditions, false)

  store.searchKeyword = '  그린빌  '
  assert.equal(store.normalizedSearchKeyword, '그린빌')
  assert.equal(store.hasActiveSearchConditions, true)
})

test('money filters are entered in ten-thousand won units and sent as won', () => {
  const store = createStore()

  store.filters.transactionType = 'MONTHLY_RENT'
  store.filters.minDeposit = 500
  store.filters.maxDeposit = 1000
  store.filters.minPrice = 70000
  store.filters.maxPrice = 80000

  assert.equal(store.apiFilters.minDeposit, 5000000)
  assert.equal(store.apiFilters.maxDeposit, 10000000)
  assert.equal(store.apiFilters.minPrice, 700000000)
  assert.equal(store.apiFilters.maxPrice, 800000000)
})

test('deposit filters are disabled and cleared for non-monthly transactions', () => {
  const store = createStore()

  store.filters.minDeposit = 500
  store.filters.maxDeposit = 1000

  store.setTransactionType('JEONSE')
  assert.equal(store.isDepositFilterDisabled, true)
  assert.equal(store.filters.minDeposit, '')
  assert.equal(store.filters.maxDeposit, '')
  assert.equal(store.apiFilters.minDeposit, '')
  assert.equal(store.apiFilters.maxDeposit, '')

  store.setTransactionType('MONTHLY_RENT')
  assert.equal(store.isDepositFilterDisabled, false)
})
