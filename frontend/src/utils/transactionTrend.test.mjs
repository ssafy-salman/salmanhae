import assert from 'node:assert/strict'
import { test } from 'node:test'

import {
  buildTransactionTrend,
  trendAmountForTransaction,
  trendLabelForTransactionType
} from './transactionTrend.js'

test('trendAmountForTransaction uses the primary price by transaction type', () => {
  assert.equal(trendAmountForTransaction({
    transactionType: 'SALE',
    price: 620000000,
    deposit: 10000000,
    monthlyRent: 500000
  }), 620000000)
  assert.equal(trendAmountForTransaction({
    transactionType: 'JEONSE',
    deposit: 180000000
  }), 180000000)
  assert.equal(trendAmountForTransaction({
    transactionType: 'MONTHLY_RENT',
    deposit: 10000000,
    monthlyRent: 520000
  }), 520000)
})

test('buildTransactionTrend sorts transactions and calculates average with bar widths', () => {
  const trend = buildTransactionTrend([
    { transactionType: 'SALE', contractYearMonth: '2026-05', price: 600000000 },
    { transactionType: 'SALE', contractYearMonth: '2026-03', price: 300000000 },
    { transactionType: 'SALE', contractYearMonth: '2026-04', price: null }
  ])

  assert.equal(trend.averageAmount, 450000000)
  assert.equal(trend.latest.contractYearMonth, '2026-05')
  assert.deepEqual(trend.points.map((point) => point.contractYearMonth), ['2026-03', '2026-05'])
  assert.deepEqual(trend.points.map((point) => point.barWidth), [50, 100])
})

test('trendLabelForTransactionType returns a human label for the primary amount', () => {
  assert.equal(trendLabelForTransactionType('SALE'), '매매가')
  assert.equal(trendLabelForTransactionType('JEONSE'), '전세가')
  assert.equal(trendLabelForTransactionType('MONTHLY_RENT'), '월세')
})
