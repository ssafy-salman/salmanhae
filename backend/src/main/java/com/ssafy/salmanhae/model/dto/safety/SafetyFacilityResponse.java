package com.ssafy.salmanhae.model.dto.safety;

import java.math.BigDecimal;

public record SafetyFacilityResponse(
		Long id,
		SafetyFacilityType type,
		String name,
		BigDecimal latitude,
		BigDecimal longitude
) {
	public static SafetyFacilityResponse from(SafetyFacilityRow row) {
		return new SafetyFacilityResponse(
				row.id(),
				row.type(),
				row.name(),
				row.latitude(),
				row.longitude()
		);
	}
}
