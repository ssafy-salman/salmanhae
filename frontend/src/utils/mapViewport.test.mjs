import assert from 'node:assert/strict'
import { test } from 'node:test'

import {
  getPrimaryPriceValue,
  isPropertyItem,
  viewportMarkerAnchor,
  viewportMarkerKind,
  viewportMarkerLabel
} from './mapViewport.js'

const formatWons = (value) => `${value}`

test('viewport utilities identify property items for side-list rendering', () => {
  assert.equal(isPropertyItem({ type: 'PROPERTY', id: 1 }), true)
  assert.equal(isPropertyItem({ type: 'REGION_AVG', regionName: '관악구' }), false)
  assert.equal(isPropertyItem({ type: 'CLUSTER', count: 12 }), false)
})

test('region average marker uses region metadata and representative price', () => {
  const item = {
    type: 'REGION_AVG',
    regionLevel: 'SIGUNGU',
    regionName: '관악구',
    avgDeposit: 98000000,
    avgMonthlyRent: 620000
  }

  assert.equal(viewportMarkerKind(item), 'region')
  assert.deepEqual(viewportMarkerAnchor(item), { x: 58, y: 54 })
  assert.equal(getPrimaryPriceValue(item), 98000000)
  assert.deepEqual(viewportMarkerLabel(item, { formatWons }), {
    eyebrow: 'SIGUNGU',
    title: '관악구',
    value: '98000000'
  })
})

test('cluster marker shows count and representative price', () => {
  const item = {
    type: 'CLUSTER',
    count: 42,
    avgDeposit: 12000000,
    avgMonthlyRent: 580000
  }

  assert.equal(viewportMarkerKind(item), 'cluster')
  assert.deepEqual(viewportMarkerAnchor(item), { x: 42, y: 42 })
  assert.deepEqual(viewportMarkerLabel(item, { formatWons }), {
    eyebrow: '42개',
    title: '매물 묶음',
    value: '12000000'
  })
})

test('property marker keeps transaction label behavior', () => {
  const item = {
    type: 'PROPERTY',
    transactionType: 'SALE',
    price: 720000000
  }

  assert.equal(viewportMarkerKind(item), 'property')
  assert.equal(getPrimaryPriceValue(item), 720000000)
  assert.deepEqual(
    viewportMarkerLabel(item, {
      formatWons,
      transactionLabel: (type) => (type === 'SALE' ? '매매' : type)
    }),
    {
      eyebrow: '매매',
      title: '',
      value: '720000000'
    }
  )
})
