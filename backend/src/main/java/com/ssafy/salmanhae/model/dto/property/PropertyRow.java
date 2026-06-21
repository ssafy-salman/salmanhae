package com.ssafy.salmanhae.model.dto.property;

import java.math.BigDecimal;

public record PropertyRow(
		Long id,
		String title,
		String buildingName,
		String buildingKey,
		String address,
		String roadAddress,
		String legalDongCode,
		PropertyType propertyType,
		TransactionType transactionType,
		Long deposit,
		Long monthlyRent,
		Long price,
		Long maintenanceFee,
		BigDecimal areaM2,
		Integer floor,
		Integer totalFloor,
		BigDecimal latitude,
		BigDecimal longitude,
		String description
) {
}
