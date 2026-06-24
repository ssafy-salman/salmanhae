import assert from 'node:assert/strict'
import { test } from 'node:test'

import { fetchMapViewport } from './properties.js'

test('fetchMapViewport calls zoom-aware viewport endpoint with cleaned params', async () => {
  let capturedUrl = ''
  let capturedConfig = null
  const client = {
    async get(url, config) {
      capturedUrl = url
      capturedConfig = config
      return {
        data: {
          data: {
            mode: 'PROPERTY_CLUSTER',
            items: [],
            totalCount: 0
          }
        }
      }
    }
  }

  const result = await fetchMapViewport(
    {
      west: 126.93,
      east: 126.94,
      south: 37.46,
      north: 37.48,
      zoom: 14,
      transactionType: 'MONTHLY_RENT',
      propertyType: '',
      minDeposit: null,
      maxDeposit: undefined
    },
    client
  )

  assert.equal(capturedUrl, '/api/v1/map/viewport')
  assert.deepEqual(capturedConfig, {
    params: {
      west: 126.93,
      east: 126.94,
      south: 37.46,
      north: 37.48,
      zoom: 14,
      transactionType: 'MONTHLY_RENT'
    }
  })
  assert.deepEqual(result, {
    mode: 'PROPERTY_CLUSTER',
    items: [],
    totalCount: 0
  })
})
