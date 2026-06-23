package com.ssafy.salmanhae.model.dto.property;

import java.util.List;

public record PriceAnalysisResponse(
		String legalDongCode,
		PropertyType propertyType,
		TransactionType transactionType,
		List<RegionPriceStatResponse> regionStats,
		List<BuildingPriceStatResponse> buildingStats
) {
	public PriceAnalysisResponse {
		regionStats = regionStats == null ? List.of() : List.copyOf(regionStats);
		buildingStats = buildingStats == null ? List.of() : List.copyOf(buildingStats);
	}
}
