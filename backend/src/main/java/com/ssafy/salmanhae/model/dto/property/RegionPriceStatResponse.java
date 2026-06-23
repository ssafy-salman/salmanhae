package com.ssafy.salmanhae.model.dto.property;

public record RegionPriceStatResponse(
		String regionLevel,
		String regionCode,
		String sido,
		String sigungu,
		String dong,
		Long avgDeposit,
		Long medianDeposit,
		Long avgMonthlyRent,
		Long medianMonthlyRent,
		Long avgPrice,
		Long medianPrice,
		Integer transactionCount,
		String sampleFromYm,
		String sampleToYm
) {
}
