package com.ssafy.salmanhae.controller.property;

import java.math.BigDecimal;
import java.util.List;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.ssafy.salmanhae.common.response.ApiResponse;
import com.ssafy.salmanhae.common.response.ListResponse;
import com.ssafy.salmanhae.model.dto.property.PropertyDetailResponse;
import com.ssafy.salmanhae.model.dto.property.PropertySearchCriteria;
import com.ssafy.salmanhae.model.dto.property.PropertySummaryResponse;
import com.ssafy.salmanhae.model.dto.property.PropertyType;
import com.ssafy.salmanhae.model.dto.property.TransactionType;
import com.ssafy.salmanhae.service.property.PropertyService;

@RestController
@RequestMapping("/api/v1/properties")
public class PropertyController {

	private final PropertyService propertyService;

	public PropertyController(PropertyService propertyService) {
		this.propertyService = propertyService;
	}

	@GetMapping
	public ApiResponse<ListResponse<PropertySummaryResponse>> searchProperties(
			@RequestParam BigDecimal west,
			@RequestParam BigDecimal east,
			@RequestParam BigDecimal south,
			@RequestParam BigDecimal north,
			@RequestParam(required = false) TransactionType transactionType,
			@RequestParam(required = false) PropertyType propertyType,
			@RequestParam(required = false) Long minDeposit,
			@RequestParam(required = false) Long maxDeposit,
			@RequestParam(required = false) Long minPrice,
			@RequestParam(required = false) Long maxPrice
	) {
		PropertySearchCriteria criteria = new PropertySearchCriteria(
				west,
				east,
				south,
				north,
				transactionType,
				propertyType,
				minDeposit,
				maxDeposit,
				minPrice,
				maxPrice
		);
		List<PropertySummaryResponse> properties = propertyService.searchProperties(criteria);
		return ApiResponse.ok(ListResponse.from(properties));
	}

	@GetMapping("/{propertyId}")
	public ApiResponse<PropertyDetailResponse> getProperty(@PathVariable Long propertyId) {
		return ApiResponse.ok(propertyService.getProperty(propertyId));
	}
}
