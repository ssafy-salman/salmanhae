import assert from 'node:assert/strict'
import { test } from 'node:test'

import { normalizeChatResponse } from './chat-normalizer.js'

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
})
