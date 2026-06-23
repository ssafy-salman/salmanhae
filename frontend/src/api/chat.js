import http from './http.js'
import { normalizeChatResponse } from './chat-normalizer.js'

export { normalizeChatResponse }

export const sendChatMessage = async ({ message, sessionId = null, selectedPropertyId = null } = {}, client = http) => {
  const trimmedMessage = String(message || '').trim()
  if (!trimmedMessage) {
    throw new Error('message must not be blank')
  }

  const payload = {
    message: trimmedMessage,
    sessionId
  }
  if (selectedPropertyId !== null && selectedPropertyId !== undefined && selectedPropertyId !== '') {
    payload.selectedPropertyId = selectedPropertyId
  }

  const response = await client.post('/api/v1/chat', payload)
  return normalizeChatResponse(response.data)
}
