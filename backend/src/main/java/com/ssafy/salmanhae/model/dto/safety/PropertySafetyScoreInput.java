package com.ssafy.salmanhae.model.dto.safety;

public record PropertySafetyScoreInput(
		Long propertyId,
		int cctvCount300m,
		int bellCount300m,
		int lightCount300m,
		int policeCount500m
) {
}
