const asArray = (value) => (Array.isArray(value) ? value : [])

const normalizeLegalCard = (card = {}) => ({
  lawName: card.lawName || '',
  articleNo: card.articleNo || '',
  title: card.title || '',
  content: card.content || '',
  score: typeof card.score === 'number' ? card.score : null
})

export const normalizeChatResponse = (body = {}) => {
  const data = body.data || {}
  return {
    intent: data.intent || '',
    message: data.message || '',
    sessionId: data.sessionId || null,
    properties: asArray(data.properties),
    legalCards: asArray(data.legalCards).map(normalizeLegalCard)
  }
}
