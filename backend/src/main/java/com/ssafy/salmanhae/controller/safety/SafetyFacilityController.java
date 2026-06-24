package com.ssafy.salmanhae.controller.safety;

import java.math.BigDecimal;
import java.util.Arrays;
import java.util.List;

import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.ssafy.salmanhae.common.exception.ApiException;
import com.ssafy.salmanhae.common.exception.ErrorCode;
import com.ssafy.salmanhae.common.response.ApiResponse;
import com.ssafy.salmanhae.common.response.ListResponse;
import com.ssafy.salmanhae.model.dto.safety.SafetyFacilityQueryRequest;
import com.ssafy.salmanhae.model.dto.safety.SafetyFacilityResponse;
import com.ssafy.salmanhae.model.dto.safety.SafetyFacilityType;
import com.ssafy.salmanhae.service.safety.SafetyFacilityService;

@RestController
@RequestMapping("/api/v1/safety")
@Validated
public class SafetyFacilityController {

	private final SafetyFacilityService safetyFacilityService;

	public SafetyFacilityController(SafetyFacilityService safetyFacilityService) {
		this.safetyFacilityService = safetyFacilityService;
	}

	@GetMapping("/facilities")
	public ApiResponse<ListResponse<SafetyFacilityResponse>> getFacilities(
			@RequestParam(required = false) String types,
			@RequestParam BigDecimal west,
			@RequestParam BigDecimal east,
			@RequestParam BigDecimal south,
			@RequestParam BigDecimal north
	) {
		SafetyFacilityQueryRequest request = new SafetyFacilityQueryRequest(
				parseTypes(types),
				west,
				east,
				south,
				north
		);
		return ApiResponse.ok(safetyFacilityService.findFacilities(request));
	}

	private List<SafetyFacilityType> parseTypes(String rawTypes) {
		if (rawTypes == null || rawTypes.isBlank()) {
			return List.of();
		}
		try {
			return Arrays.stream(rawTypes.split(","))
					.map(String::trim)
					.filter(type -> !type.isEmpty())
					.map(SafetyFacilityType::valueOf)
					.distinct()
					.toList();
		} catch (IllegalArgumentException exception) {
			throw new ApiException(ErrorCode.INVALID_REQUEST);
		}
	}
}
