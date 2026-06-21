import http from './http'

const cleanParams = (params) =>
  Object.fromEntries(
    Object.entries(params).filter(([, value]) => value !== undefined && value !== null && value !== '')
  )

export const fetchProperties = async (params) => {
  const response = await http.get('/api/v1/properties', {
    params: cleanParams(params)
  })
  return response.data.data
}

export const fetchPropertyDetail = async (propertyId) => {
  const response = await http.get(`/api/v1/properties/${propertyId}`)
  return response.data.data
}
