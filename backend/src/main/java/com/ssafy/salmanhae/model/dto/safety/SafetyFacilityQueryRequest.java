package com.ssafy.salmanhae.model.dto.safety;

import java.math.BigDecimal;
import java.util.List;

import com.ssafy.salmanhae.common.exception.ApiException;
import com.ssafy.salmanhae.common.exception.ErrorCode;

public record SafetyFacilityQueryRequest(
		List<SafetyFacilityType> types,
		BigDecimal west,
		BigDecimal east,
		BigDecimal south,
		BigDecimal north
) {

	private static final BigDecimal MIN_LONGITUDE = BigDecimal.valueOf(-180);
	private static final BigDecimal MAX_LONGITUDE = BigDecimal.valueOf(180);
	private static final BigDecimal MIN_LATITUDE = BigDecimal.valueOf(-90);
	private static final BigDecimal MAX_LATITUDE = BigDecimal.valueOf(90);

	public SafetyFacilityQueryRequest {
		types = types == null ? List.of() : List.copyOf(types);
	}

	public void validateBounds() {
		if (west == null || east == null || south == null || north == null) {
			throw new ApiException(ErrorCode.INVALID_BOUNDS);
		}
		if (west.compareTo(east) >= 0 || south.compareTo(north) >= 0) {
			throw new ApiException(ErrorCode.INVALID_BOUNDS);
		}
		if (west.compareTo(MIN_LONGITUDE) < 0 || east.compareTo(MAX_LONGITUDE) > 0
				|| south.compareTo(MIN_LATITUDE) < 0 || north.compareTo(MAX_LATITUDE) > 0) {
			throw new ApiException(ErrorCode.INVALID_BOUNDS);
		}
	}
}
