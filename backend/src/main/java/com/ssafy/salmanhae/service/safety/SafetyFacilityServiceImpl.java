package com.ssafy.salmanhae.service.safety;

import org.springframework.stereotype.Service;

import com.ssafy.salmanhae.common.exception.ApiException;
import com.ssafy.salmanhae.common.exception.ErrorCode;
import com.ssafy.salmanhae.common.response.ListResponse;
import com.ssafy.salmanhae.model.dao.safety.SafetyFacilityDao;
import com.ssafy.salmanhae.model.dto.safety.SafetyFacilityQueryRequest;
import com.ssafy.salmanhae.model.dto.safety.SafetyFacilityResponse;

@Service
public class SafetyFacilityServiceImpl implements SafetyFacilityService {

	private final SafetyFacilityDao safetyFacilityDao;

	public SafetyFacilityServiceImpl(SafetyFacilityDao safetyFacilityDao) {
		this.safetyFacilityDao = safetyFacilityDao;
	}

	@Override
	public ListResponse<SafetyFacilityResponse> findFacilities(SafetyFacilityQueryRequest request) {
		if (request == null) {
			throw new ApiException(ErrorCode.INVALID_REQUEST);
		}
		request.validateBounds();
		return ListResponse.from(
				safetyFacilityDao.findInBounds(
								request.types(),
								request.west(),
								request.east(),
								request.south(),
								request.north()
						)
						.stream()
						.map(SafetyFacilityResponse::from)
						.toList()
		);
	}
}
