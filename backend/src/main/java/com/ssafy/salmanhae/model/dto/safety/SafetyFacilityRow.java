package com.ssafy.salmanhae.model.dto.safety;

import java.math.BigDecimal;

public record SafetyFacilityRow(
		Long id,
		SafetyFacilityType type,
		String name,
		String address,
		BigDecimal latitude,
		BigDecimal longitude,
		String source,
		String sourceId,
		String description
) {
}
