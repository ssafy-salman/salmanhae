export const VIEWPORT_ITEM_TYPES = {
  REGION_AVG: 'REGION_AVG',
  CLUSTER: 'CLUSTER',
  PROPERTY: 'PROPERTY'
}

export const VIEWPORT_MODES = {
  SIDO_AVG: 'SIDO_AVG',
  SIGUNGU_AVG: 'SIGUNGU_AVG',
  DONG_AVG: 'DONG_AVG',
  PROPERTY_CLUSTER: 'PROPERTY_CLUSTER',
  PROPERTY_MARKER: 'PROPERTY_MARKER'
}

export const isPropertyItem = (item) => item?.type === VIEWPORT_ITEM_TYPES.PROPERTY

const PROPERTY_TYPE_LABELS = {
  ONE_ROOM: '원룸',
  OFFICETEL: '오피스텔',
  APARTMENT: '아파트',
  VILLA: '빌라',
  MULTI_FAMILY: '다세대주택'
}

export const getPrimaryPriceValue = (item) => {
  if (!item) return null
  if (item.transactionType === 'SALE') return item.avgSalePrice ?? item.price ?? null
  if (item.transactionType === 'JEONSE') return item.avgDeposit ?? item.deposit ?? null
  if (item.transactionType === 'MONTHLY_RENT') return item.avgMonthlyRent ?? item.monthlyRent ?? null
  return item.avgMonthlyRent ?? item.monthlyRent ?? item.avgSalePrice ?? item.price ?? item.avgDeposit ?? item.deposit ?? null
}

export const regionLevelLabel = (level) => ({
  SIDO: '시/도',
  SIGUNGU: '시/군/구',
  DONG: '읍/면/동'
}[level] || '지역')

export const propertyTypeLabel = (type) => PROPERTY_TYPE_LABELS[type] || '주거'

export const propertyDisplayTitle = (property) => {
  const fallback = property?.propertyType ? propertyTypeLabel(property.propertyType) : ''
  const rawTitle = String(property?.title || property?.buildingName || fallback || '').trim()
  const translatedType = Object.entries(PROPERTY_TYPE_LABELS).reduce(
    (title, [type, label]) => title.replaceAll(type, label),
    rawTitle
  )
  const cleanedTitle = translatedType
    .replace(/\s*매물\s*$/u, '')
    .replace(/\s+/g, ' ')
    .trim()

  if (cleanedTitle) return cleanedTitle
  if (fallback) return fallback
  return property?.id ? `No. ${property.id}` : '이름 없음'
}

export const targetZoomForViewportItem = (item, currentZoom = 0) => {
  if (item?.type === VIEWPORT_ITEM_TYPES.CLUSTER) return 16
  if (item?.regionLevel === 'SIDO') return 10
  if (item?.regionLevel === 'SIGUNGU') return 12
  if (item?.regionLevel === 'DONG') return 14
  return Math.min(21, Number(currentZoom || 0) + 1)
}

export const viewportMarkerKind = (item) => {
  if (item?.type === VIEWPORT_ITEM_TYPES.REGION_AVG) return 'region'
  if (item?.type === VIEWPORT_ITEM_TYPES.CLUSTER) return 'cluster'
  return 'property'
}

export const viewportMarkerAnchor = (item) => {
  const kind = viewportMarkerKind(item)
  if (kind === 'region') return { x: 58, y: 54 }
  if (kind === 'cluster') return { x: 42, y: 42 }
  return { x: 42, y: 44 }
}

export const viewportMarkerLabel = (item, { formatWons, transactionLabel, showCount = false } = {}) => {
  const formatPrice = formatWons || ((value) => String(value ?? '-'))
  if (item?.type === VIEWPORT_ITEM_TYPES.REGION_AVG) {
    const regionName = item.regionName || item.regionCode || '지역'
    return {
      eyebrow: regionLevelLabel(item.regionLevel),
      title: regionName,
      value: showCount ? `${Number(item.transactionCount || 0).toLocaleString()}개` : formatPrice(getPrimaryPriceValue(item))
    }
  }

  if (item?.type === VIEWPORT_ITEM_TYPES.CLUSTER) {
    return {
      eyebrow: `${Number(item.count || 0).toLocaleString()}개`,
      title: '매물 묶음',
      value: formatPrice(getPrimaryPriceValue(item))
    }
  }

  return {
    eyebrow: transactionLabel ? transactionLabel(item?.transactionType) : item?.transactionType || '매물',
    title: '',
    value: formatPrice(getPrimaryPriceValue(item))
  }
}
