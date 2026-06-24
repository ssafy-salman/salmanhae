export const VIEWPORT_ITEM_TYPES = {
  REGION_AVG: 'REGION_AVG',
  CLUSTER: 'CLUSTER',
  PROPERTY: 'PROPERTY'
}

export const VIEWPORT_MODES = {
  SIGUNGU_AVG: 'SIGUNGU_AVG',
  DONG_AVG: 'DONG_AVG',
  PROPERTY_CLUSTER: 'PROPERTY_CLUSTER',
  PROPERTY_MARKER: 'PROPERTY_MARKER'
}

export const isPropertyItem = (item) => item?.type === VIEWPORT_ITEM_TYPES.PROPERTY

export const getPrimaryPriceValue = (item) => {
  if (!item) return null
  return item.avgSalePrice ?? item.price ?? item.avgDeposit ?? item.deposit ?? item.avgMonthlyRent ?? item.monthlyRent ?? null
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

export const viewportMarkerLabel = (item, { formatWons, transactionLabel } = {}) => {
  const formatPrice = formatWons || ((value) => String(value ?? '-'))
  if (item?.type === VIEWPORT_ITEM_TYPES.REGION_AVG) {
    const regionName = item.regionName || item.regionCode || '지역'
    return {
      eyebrow: item.regionLevel || 'REGION',
      title: regionName,
      value: formatPrice(getPrimaryPriceValue(item))
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
