package com.ssafy.salmanhae.service.safety;

import com.ssafy.salmanhae.common.response.ListResponse;
import com.ssafy.salmanhae.model.dto.safety.SafetyFacilityQueryRequest;
import com.ssafy.salmanhae.model.dto.safety.SafetyFacilityResponse;

public interface SafetyFacilityService {

	ListResponse<SafetyFacilityResponse> findFacilities(SafetyFacilityQueryRequest request);
}
