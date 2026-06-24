package com.ssafy.salmanhae.service.safety.ingest;

import java.math.BigDecimal;

import com.ssafy.salmanhae.model.dto.safety.SafetyFacilityRow;
import com.ssafy.salmanhae.model.dto.safety.SafetyFacilityType;

public record NormalizedSafetyFacility(
		SafetyFacilityType type,
		String name,
		String address,
		BigDecimal latitude,
		BigDecimal longitude,
		String source,
		String sourceId,
		String description
) {

	public boolean hasUsableCoordinates() {
		return latitude != null && longitude != null
				&& latitude.compareTo(BigDecimal.valueOf(-90)) >= 0
				&& latitude.compareTo(BigDecimal.valueOf(90)) <= 0
				&& longitude.compareTo(BigDecimal.valueOf(-180)) >= 0
				&& longitude.compareTo(BigDecimal.valueOf(180)) <= 0;
	}

	public SafetyFacilityRow toRow() {
		return new SafetyFacilityRow(
				null,
				type,
				name,
				address,
				latitude,
				longitude,
				source,
				sourceId,
				description
		);
	}
}
