let sdkPromise

export const loadNaverMaps = () => {
  if (typeof window === 'undefined') {
    return Promise.reject(new Error('Naver Maps SDK can only be loaded in the browser.'))
  }

  if (window.naver?.maps) {
    return Promise.resolve(window.naver.maps)
  }

  const clientId = import.meta.env.VITE_NAVER_MAP_CLIENT_ID
  if (!clientId) {
    return Promise.reject(new Error('VITE_NAVER_MAP_CLIENT_ID is not configured.'))
  }

  if (sdkPromise) {
    return sdkPromise
  }

  sdkPromise = new Promise((resolve, reject) => {
    const existingScript = document.getElementById('naver-map-sdk')
    if (existingScript) {
      existingScript.addEventListener('load', () => resolve(window.naver.maps), { once: true })
      existingScript.addEventListener('error', () => reject(new Error('Failed to load Naver Maps SDK.')), { once: true })
      return
    }

    const script = document.createElement('script')
    script.id = 'naver-map-sdk'
    script.async = true
    script.src = `https://oapi.map.naver.com/openapi/v3/maps.js?ncpKeyId=${encodeURIComponent(clientId)}`
    script.onload = () => {
      if (window.naver?.maps) {
        resolve(window.naver.maps)
        return
      }
      reject(new Error('Naver Maps SDK loaded without maps namespace.'))
    }
    script.onerror = () => reject(new Error('Failed to load Naver Maps SDK.'))
    document.head.appendChild(script)
  })

  return sdkPromise
}
