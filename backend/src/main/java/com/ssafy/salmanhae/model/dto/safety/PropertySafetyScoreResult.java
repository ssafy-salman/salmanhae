package com.ssafy.salmanhae.model.dto.safety;

public record PropertySafetyScoreResult(
		Long propertyId,
		int safetyScore,
		int cctvCount300m,
		int bellCount300m,
		int lightCount300m,
		int policeCount500m
) {
}
