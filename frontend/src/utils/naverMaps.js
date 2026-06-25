let sdkPromise

const resolveIfReady = (resolve) => {
  if (window.naver?.maps) {
    resolve(window.naver.maps)
    return true
  }
  return false
}

const rejectAndAllowRetry = (reject, message) => {
  sdkPromise = null
  reject(new Error(message))
}

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
      if (resolveIfReady(resolve)) return

      const scriptState = existingScript.dataset.loadState
      const readyState = existingScript.readyState
      if (scriptState === 'error' || scriptState === 'loaded' || readyState === 'complete') {
        existingScript.remove()
      } else {
        existingScript.addEventListener('load', () => {
          if (!resolveIfReady(resolve)) {
            rejectAndAllowRetry(reject, 'Naver Maps SDK loaded without maps namespace.')
          }
        }, { once: true })
        existingScript.addEventListener('error', () => {
          existingScript.dataset.loadState = 'error'
          rejectAndAllowRetry(reject, 'Failed to load Naver Maps SDK.')
        }, { once: true })
        return
      }
    }

    if (document.getElementById('naver-map-sdk')) {
      return
    }

    const script = document.createElement('script')
    script.id = 'naver-map-sdk'
    script.async = true
    script.dataset.loadState = 'loading'
    script.src = `https://oapi.map.naver.com/openapi/v3/maps.js?ncpKeyId=${encodeURIComponent(clientId)}`
    script.onload = () => {
      script.dataset.loadState = 'loaded'
      if (resolveIfReady(resolve)) {
        return
      }
      rejectAndAllowRetry(reject, 'Naver Maps SDK loaded without maps namespace.')
    }
    script.onerror = () => {
      script.dataset.loadState = 'error'
      script.remove()
      rejectAndAllowRetry(reject, 'Failed to load Naver Maps SDK.')
    }
    document.head.appendChild(script)
  })

  return sdkPromise
}
