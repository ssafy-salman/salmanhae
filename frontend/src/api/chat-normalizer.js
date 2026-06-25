const asArray = (value) => (Array.isArray(value) ? value : [])

const normalizeLegalCard = (card = {}) => ({
  lawName: card.lawName || '',
  articleNo: card.articleNo || '',
  title: card.title || '',
  content: card.content || '',
  score: typeof card.score === 'number' ? card.score : null
})

const asObject = (value) => (value && typeof value === 'object' && !Array.isArray(value) ? value : {})

const normalizeAnalysisCard = (card = {}) => ({
  type: card.type || '',
  title: card.title || '',
  summary: card.summary || '',
  score: typeof card.score === 'number' ? card.score : null,
  metrics: { ...asObject(card.metrics) }
})

export const normalizeChatResponse = (body = {}) => {
  const data = body.data || {}
  return {
    intent: data.intent || '',
    message: data.message || '',
    sessionId: data.sessionId || null,
    properties: asArray(data.properties),
    legalCards: asArray(data.legalCards).map(normalizeLegalCard),
    analysisCards: asArray(data.analysisCards).map(normalizeAnalysisCard)
  }
}
