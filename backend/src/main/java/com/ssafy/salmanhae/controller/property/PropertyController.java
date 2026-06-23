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
import com.ssafy.salmanhae.model.dto.property.PropertySafetySummaryResponse;
import com.ssafy.salmanhae.model.dto.property.PropertySearchCriteria;
import com.ssafy.salmanhae.model.dto.property.PropertySummaryResponse;
import com.ssafy.salmanhae.model.dto.property.PropertyTransactionResponse;
import com.ssafy.salmanhae.model.dto.property.PropertyType;
import com.ssafy.salmanhae.model.dto.property.TransactionType;
import com.ssafy.salmanhae.service.property.PropertyService;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import org.springframework.validation.annotation.Validated;

@RestController
@RequestMapping("/api/v1/properties")
@Validated
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
		criteria.validateBounds();
		List<PropertySummaryResponse> properties = propertyService.searchProperties(criteria);
		return ApiResponse.ok(ListResponse.from(properties));
	}

	@GetMapping("/{propertyId}")
	public ApiResponse<PropertyDetailResponse> getProperty(@PathVariable @NotNull @Positive Long propertyId) {
		return ApiResponse.ok(propertyService.getProperty(propertyId));
	}

	@GetMapping("/{propertyId}/transactions")
	public ApiResponse<ListResponse<PropertyTransactionResponse>> getPropertyTransactions(
			@PathVariable @NotNull @Positive Long propertyId,
			@RequestParam(required = false) @Min(1) @Max(10) Integer years
	) {
		return ApiResponse.ok(ListResponse.from(propertyService.getTransactions(propertyId, years)));
	}

	@GetMapping("/{propertyId}/safety-summary")
	public ApiResponse<PropertySafetySummaryResponse> getPropertySafetySummary(
			@PathVariable @NotNull @Positive Long propertyId,
			@RequestParam(required = false) @Min(300) @Max(500) Integer radius
	) {
		return ApiResponse.ok(propertyService.getSafetySummary(propertyId, radius));
	}
}
