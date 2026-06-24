package com.ssafy.salmanhae.service.safety.ingest;

import java.util.List;

public interface SafetyFacilitySourceClient {

	String sourceName();

	List<NormalizedSafetyFacility> fetchFacilities();
}
