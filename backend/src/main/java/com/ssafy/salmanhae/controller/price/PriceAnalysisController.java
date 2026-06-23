package com.ssafy.salmanhae.controller.price;

import com.ssafy.salmanhae.common.response.ApiResponse;
import com.ssafy.salmanhae.model.dto.property.PriceAnalysisResponse;
import com.ssafy.salmanhae.model.dto.property.PropertyType;
import com.ssafy.salmanhae.model.dto.property.TransactionType;
import com.ssafy.salmanhae.service.property.PropertyService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/price-analysis")
public class PriceAnalysisController {

	private final PropertyService propertyService;

	public PriceAnalysisController(PropertyService propertyService) {
		this.propertyService = propertyService;
	}

	@GetMapping
	public ApiResponse<PriceAnalysisResponse> getPriceAnalysis(
			@RequestParam String legalDongCode,
			@RequestParam PropertyType propertyType,
			@RequestParam TransactionType transactionType
	) {
		return ApiResponse.ok(propertyService.getPriceAnalysis(legalDongCode, propertyType, transactionType));
	}
}
