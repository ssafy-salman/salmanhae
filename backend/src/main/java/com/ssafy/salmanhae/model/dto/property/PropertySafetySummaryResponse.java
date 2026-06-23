package com.ssafy.salmanhae.model.dto.property;

public record PropertySafetySummaryResponse(
		Long propertyId,
		Integer radius,
		Integer safetyScore,
		Integer priceScore,
		Integer cctvCount300m,
		Integer bellCount300m,
		Integer lightCount300m,
		Integer policeCount500m
) {
}
