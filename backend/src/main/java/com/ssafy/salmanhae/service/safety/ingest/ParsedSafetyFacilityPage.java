package com.ssafy.salmanhae.service.safety.ingest;

import java.util.List;

record ParsedSafetyFacilityPage(
		List<NormalizedSafetyFacility> facilities,
		int rawItemCount
) {
}
