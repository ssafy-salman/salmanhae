import assert from 'node:assert/strict'
import { test } from 'node:test'

import {
  getPrimaryPriceValue,
  isPropertyItem,
  propertyDisplayTitle,
  propertyTypeLabel,
  regionLevelLabel,
  targetZoomForViewportItem,
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

test('region average marker uses region metadata and matching property count by default', () => {
  const item = {
    type: 'REGION_AVG',
    regionLevel: 'SIGUNGU',
    regionName: '관악구',
    avgDeposit: 98000000,
    avgMonthlyRent: 620000,
    transactionCount: 3
  }

  assert.equal(viewportMarkerKind(item), 'region')
  assert.deepEqual(viewportMarkerAnchor(item), { x: 58, y: 54 })
  assert.equal(getPrimaryPriceValue(item), 620000)
  assert.deepEqual(viewportMarkerLabel(item, { formatWons }), {
    eyebrow: '시/군/구',
    title: '관악구',
    value: '3개'
  })
})

test('region marker can still show representative price when explicitly requested', () => {
  const item = {
    type: 'REGION_AVG',
    regionLevel: 'SIGUNGU',
    regionName: '관악구',
    avgMonthlyRent: 620000,
    transactionCount: 3
  }

  assert.deepEqual(viewportMarkerLabel(item, { formatWons, showCount: false }), {
    eyebrow: '시/군/구',
    title: '관악구',
    value: '620000'
  })
})

test('monthly rent viewport items use monthly rent as representative price', () => {
  assert.equal(getPrimaryPriceValue({
    type: 'PROPERTY',
    transactionType: 'MONTHLY_RENT',
    deposit: 10000000,
    monthlyRent: 500000
  }), 500000)
  assert.equal(getPrimaryPriceValue({
    type: 'REGION_AVG',
    avgDeposit: 10000000,
    avgMonthlyRent: 500000
  }), 500000)
})

test('cluster marker uses count instead of mixed representative price', () => {
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
    value: '42개'
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

test('viewport labels translate region levels and property types', () => {
  assert.equal(regionLevelLabel('SIDO'), '시/도')
  assert.equal(regionLevelLabel('SIGUNGU'), '시/군/구')
  assert.equal(regionLevelLabel('DONG'), '읍/면/동')
  assert.equal(propertyTypeLabel('MULTI_FAMILY'), '다세대주택')
})

test('property display title removes raw enum labels and trailing item wording', () => {
  assert.equal(propertyDisplayTitle({
    id: 1,
    title: '대학동 MULTI_FAMILY 매물',
    propertyType: 'MULTI_FAMILY'
  }), '대학동 다세대주택')
  assert.equal(propertyDisplayTitle({
    id: 2,
    title: '신림동 원룸 매물',
    propertyType: 'ONE_ROOM'
  }), '신림동 원룸')
  assert.equal(propertyDisplayTitle({
    id: 3,
    title: '',
    buildingName: '',
    propertyType: 'MULTI_FAMILY'
  }), '다세대주택')
})

test('viewport item target zoom follows drill-down hierarchy', () => {
  assert.equal(targetZoomForViewportItem({ type: 'REGION_AVG', regionLevel: 'SIDO' }, 9), 10)
  assert.equal(targetZoomForViewportItem({ type: 'REGION_AVG', regionLevel: 'SIGUNGU' }, 10), 12)
  assert.equal(targetZoomForViewportItem({ type: 'REGION_AVG', regionLevel: 'DONG' }, 12), 14)
  assert.equal(targetZoomForViewportItem({ type: 'CLUSTER' }, 14), 16)
  assert.equal(targetZoomForViewportItem({ type: 'UNKNOWN' }, 20), 21)
})
