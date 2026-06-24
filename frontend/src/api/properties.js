import http from './http.js'

const cleanParams = (params) =>
  Object.fromEntries(
    Object.entries(params).filter(([, value]) => value !== undefined && value !== null && value !== '')
  )

export const fetchProperties = async (params, client = http) => {
  const response = await client.get('/api/v1/properties', {
    params: cleanParams(params)
  })
  return response.data.data
}

export const fetchMapViewport = async (params, client = http) => {
  const response = await client.get('/api/v1/map/viewport', {
    params: cleanParams(params)
  })
  return response.data.data
}

export const fetchPropertyDetail = async (propertyId, client = http) => {
  const response = await client.get(`/api/v1/properties/${propertyId}`)
  return response.data.data
}
