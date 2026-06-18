package com.ssafy.salmanhae.model.dto.property;

import java.math.BigDecimal;

public record PropertyDetailResponse(
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

	public static PropertyDetailResponse from(PropertyRow row) {
		return new PropertyDetailResponse(
				row.id(),
				row.title(),
				row.buildingName(),
				row.buildingKey(),
				row.address(),
				row.roadAddress(),
				row.legalDongCode(),
				row.propertyType(),
				row.transactionType(),
				row.deposit(),
				row.monthlyRent(),
				row.price(),
				row.maintenanceFee(),
				row.areaM2(),
				row.floor(),
				row.totalFloor(),
				row.latitude(),
				row.longitude(),
				row.description()
		);
	}
}
