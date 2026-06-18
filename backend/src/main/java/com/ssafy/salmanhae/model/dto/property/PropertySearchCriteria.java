package com.ssafy.salmanhae.model.dto.property;

import java.math.BigDecimal;

import com.ssafy.salmanhae.common.exception.ApiException;
import com.ssafy.salmanhae.common.exception.ErrorCode;

public record PropertySearchCriteria(
		BigDecimal west,
		BigDecimal east,
		BigDecimal south,
		BigDecimal north,
		TransactionType transactionType,
		PropertyType propertyType,
		Long minDeposit,
		Long maxDeposit,
		Long minPrice,
		Long maxPrice
) {

	private static final BigDecimal MIN_LONGITUDE = BigDecimal.valueOf(-180);
	private static final BigDecimal MAX_LONGITUDE = BigDecimal.valueOf(180);
	private static final BigDecimal MIN_LATITUDE = BigDecimal.valueOf(-90);
	private static final BigDecimal MAX_LATITUDE = BigDecimal.valueOf(90);

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
		if (minDeposit != null && maxDeposit != null && minDeposit > maxDeposit) {
			throw new ApiException(ErrorCode.INVALID_REQUEST);
		}
		if (isNegative(minDeposit) || isNegative(maxDeposit)) {
			throw new ApiException(ErrorCode.INVALID_REQUEST);
		}
		if (minPrice != null && maxPrice != null && minPrice > maxPrice) {
			throw new ApiException(ErrorCode.INVALID_REQUEST);
		}
		if (isNegative(minPrice) || isNegative(maxPrice)) {
			throw new ApiException(ErrorCode.INVALID_REQUEST);
		}
	}

	private boolean isNegative(Long value) {
		return value != null && value < 0;
	}
}
