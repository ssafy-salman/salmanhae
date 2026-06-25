export const trendAmountForTransaction = (transaction) => {
  if (!transaction) return null
  if (transaction.transactionType === 'SALE') return transaction.price ?? null
  if (transaction.transactionType === 'JEONSE') return transaction.deposit ?? null
  return transaction.monthlyRent ?? null
}

export const trendLabelForTransactionType = (transactionType) => ({
  SALE: '매매가',
  JEONSE: '전세가',
  MONTHLY_RENT: '월세'
}[transactionType] || '거래가')

export const buildTransactionTrend = (transactions = []) => {
  const points = transactions
    .map((transaction) => ({
      ...transaction,
      amount: trendAmountForTransaction(transaction)
    }))
    .filter((transaction) => (
      transaction.amount !== null
      && transaction.amount !== undefined
      && Number.isFinite(Number(transaction.amount))
    ))
    .sort((a, b) => String(a.contractYearMonth || '').localeCompare(String(b.contractYearMonth || '')))

  const amounts = points.map((point) => Number(point.amount))
  const maxAmount = Math.max(...amounts, 0)
  const averageAmount = amounts.length > 0
    ? Math.round(amounts.reduce((sum, amount) => sum + amount, 0) / amounts.length)
    : null

  return {
    points: points.map((point) => ({
      ...point,
      barWidth: maxAmount > 0 ? Math.max(12, Math.round((Number(point.amount) / maxAmount) * 100)) : 0
    })),
    averageAmount,
    latest: points.at(-1) || null
  }
}
