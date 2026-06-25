package com.ssafy.salmanhae.model.dto.map;

import java.math.BigDecimal;

public record PropertyClusterViewportItem(
		MapViewportItemType type,
		String clusterId,
		int count,
		BigDecimal latitude,
		BigDecimal longitude,
		Integer radiusM,
		Long avgDeposit,
		Long avgMonthlyRent,
		Long avgSalePrice
) implements MapViewportItemResponse {
}
