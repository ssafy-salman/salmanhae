package com.ssafy.salmanhae.controller.map;

import java.math.BigDecimal;

import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.ssafy.salmanhae.common.response.ApiResponse;
import com.ssafy.salmanhae.model.dto.map.MapViewportRequest;
import com.ssafy.salmanhae.model.dto.map.MapViewportResponse;
import com.ssafy.salmanhae.model.dto.property.PropertySearchCriteria;
import com.ssafy.salmanhae.model.dto.property.PropertyType;
import com.ssafy.salmanhae.model.dto.property.TransactionType;
import com.ssafy.salmanhae.service.map.MapViewportService;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;

@RestController
@RequestMapping("/api/v1/map")
@Validated
public class MapViewportController {

	private final MapViewportService mapViewportService;

	public MapViewportController(MapViewportService mapViewportService) {
		this.mapViewportService = mapViewportService;
	}

	@GetMapping("/viewport")
	public ApiResponse<MapViewportResponse> getViewport(
			@RequestParam BigDecimal west,
			@RequestParam BigDecimal east,
			@RequestParam BigDecimal south,
			@RequestParam BigDecimal north,
			@RequestParam @Min(0) @Max(21) Integer zoom,
			@RequestParam(required = false) TransactionType transactionType,
			@RequestParam(required = false) PropertyType propertyType,
			@RequestParam(required = false) Long minDeposit,
			@RequestParam(required = false) Long maxDeposit,
			@RequestParam(required = false) Long minPrice,
			@RequestParam(required = false) Long maxPrice,
			@RequestParam(required = false) Integer clusterThreshold
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
		return ApiResponse.ok(mapViewportService.getViewport(new MapViewportRequest(criteria, zoom, clusterThreshold)));
	}
}
