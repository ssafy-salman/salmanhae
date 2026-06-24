package com.ssafy.salmanhae.model.dto.map;

import java.math.BigDecimal;

public record RegionAverageViewportItem(
		MapViewportItemType type,
		String regionLevel,
		String regionCode,
		String regionName,
		Long avgDeposit,
		Long avgMonthlyRent,
		Long avgSalePrice,
		Integer transactionCount,
		BigDecimal latitude,
		BigDecimal longitude
) implements MapViewportItemResponse {
}
