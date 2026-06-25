import assert from 'node:assert/strict'
import { test } from 'node:test'

import { normalizeChatResponse } from './chat-normalizer.js'
import { sendChatMessage } from './chat.js'

test('normalizeChatResponse maps legal RAG response into chat payload', () => {
  const result = normalizeChatResponse({
    data: {
      intent: 'LEGAL_CONSULT',
      message: 'Check the cited law before signing.',
      sessionId: 'session-1',
      properties: [],
      legalCards: [
        {
          lawName: 'Housing Lease Protection Act',
          articleNo: 'Article 3-2',
          title: 'Deposit recovery',
          content: 'The tenant may recover the deposit before junior creditors.',
          score: 0.92
        }
      ]
    },
    message: 'OK'
  })

  assert.equal(result.intent, 'LEGAL_CONSULT')
  assert.equal(result.message, 'Check the cited law before signing.')
  assert.equal(result.sessionId, 'session-1')
  assert.deepEqual(result.properties, [])
  assert.deepEqual(result.legalCards, [
    {
      lawName: 'Housing Lease Protection Act',
      articleNo: 'Article 3-2',
      title: 'Deposit recovery',
      content: 'The tenant may recover the deposit before junior creditors.',
      score: 0.92
    }
  ])
})

test('normalizeChatResponse tolerates missing optional arrays', () => {
  const result = normalizeChatResponse({
    data: {
      intent: 'LEGAL_CONSULT',
      message: 'No legal references were found.',
      sessionId: null
    }
  })

  assert.deepEqual(result.properties, [])
  assert.deepEqual(result.legalCards, [])
  assert.deepEqual(result.analysisCards, [])
})

test('sendChatMessage includes selected property id in request payload', async () => {
  let capturedUrl = ''
  let capturedPayload = null
  const client = {
    async post(url, payload) {
      capturedUrl = url
      capturedPayload = payload
      return {
        data: {
          data: {
            intent: 'PRICE_ANALYSIS',
            message: '분석했습니다.',
            sessionId: 'session-1',
            properties: [],
            legalCards: [],
            analysisCards: []
          }
        }
      }
    }
  }

  await sendChatMessage(
    {
      message: '이 매물 시세 어때?',
      sessionId: 'session-1',
      selectedPropertyId: 17
    },
    client
  )

  assert.equal(capturedUrl, '/api/v1/chat')
  assert.deepEqual(capturedPayload, {
    message: '이 매물 시세 어때?',
    sessionId: 'session-1',
    selectedPropertyId: 17
  })
})

test('sendChatMessage omits empty selected property id', async () => {
  let capturedPayload = null
  const client = {
    async post(_url, payload) {
      capturedPayload = payload
      return {
        data: {
          data: {
            message: 'OK'
          }
        }
      }
    }
  }

  await sendChatMessage(
    {
      message: '안전 분석해줘',
      selectedPropertyId: null
    },
    client
  )

  assert.deepEqual(capturedPayload, {
    message: '안전 분석해줘',
    sessionId: null
  })
})

test('normalizeChatResponse maps price and safety analysis cards', () => {
  const result = normalizeChatResponse({
    data: {
      intent: 'SAFETY_ANALYSIS',
      message: '주변 안전 데이터는 안전 점수 78점으로 확인됩니다.',
      sessionId: 'session-2',
      analysisCards: [
        {
          type: 'PRICE',
          title: '시세 분석',
          summary: '최근 실거래 2건을 기준으로 확인했습니다.',
          score: null,
          metrics: {
            comparableTransactionCount: 2,
            avgDeposit: 10500000,
            avgMonthlyRent: 520000
          }
        },
        {
          type: 'SAFETY',
          title: '안전 분석',
          summary: '반경 500m 기준 안전 점수는 78점입니다.',
          score: 78,
          metrics: {
            radius: 500,
            cctvCount300m: 8,
            bellCount300m: 0
          }
        }
      ]
    }
  })

  assert.deepEqual(result.analysisCards, [
    {
      type: 'PRICE',
      title: '시세 분석',
      summary: '최근 실거래 2건을 기준으로 확인했습니다.',
      score: null,
      metrics: {
        comparableTransactionCount: 2,
        avgDeposit: 10500000,
        avgMonthlyRent: 520000
      }
    },
    {
      type: 'SAFETY',
      title: '안전 분석',
      summary: '반경 500m 기준 안전 점수는 78점입니다.',
      score: 78,
      metrics: {
        radius: 500,
        cctvCount300m: 8,
        bellCount300m: 0
      }
    }
  ])
})
