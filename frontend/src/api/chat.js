import http from './http.js'
import { normalizeChatResponse } from './chat-normalizer.js'

export { normalizeChatResponse }

export const sendChatMessage = async ({ message, sessionId = null } = {}, client = http) => {
  const trimmedMessage = String(message || '').trim()
  if (!trimmedMessage) {
    throw new Error('message must not be blank')
  }

  const response = await client.post('/api/v1/chat', {
    message: trimmedMessage,
    sessionId
  })
  return normalizeChatResponse(response.data)
}
