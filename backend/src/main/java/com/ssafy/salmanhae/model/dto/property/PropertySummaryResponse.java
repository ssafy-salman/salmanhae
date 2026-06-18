package com.ssafy.salmanhae.model.dto.property;

import java.math.BigDecimal;

public record PropertySummaryResponse(
		Long id,
		String title,
		String buildingName,
		String address,
		PropertyType propertyType,
		TransactionType transactionType,
		Long deposit,
		Long monthlyRent,
		Long price,
		BigDecimal areaM2,
		Integer floor,
		BigDecimal latitude,
		BigDecimal longitude
) {

	public static PropertySummaryResponse from(PropertyRow row) {
		return new PropertySummaryResponse(
				row.id(),
				row.title(),
				row.buildingName(),
				row.address(),
				row.propertyType(),
				row.transactionType(),
				row.deposit(),
				row.monthlyRent(),
				row.price(),
				row.areaM2(),
				row.floor(),
				row.latitude(),
				row.longitude()
		);
	}
}
