package com.ssafy.salmanhae.model.dto.map;

import java.math.BigDecimal;

import com.ssafy.salmanhae.model.dto.property.TransactionType;

public record PropertyViewportItem(
		MapViewportItemType type,
		Long id,
		String title,
		TransactionType transactionType,
		Long deposit,
		Long monthlyRent,
		Long price,
		BigDecimal areaM2,
		BigDecimal latitude,
		BigDecimal longitude
) implements MapViewportItemResponse {
}
