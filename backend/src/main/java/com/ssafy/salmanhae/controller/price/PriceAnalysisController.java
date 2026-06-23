package com.ssafy.salmanhae.controller.price;

import com.ssafy.salmanhae.common.response.ApiResponse;
import com.ssafy.salmanhae.model.dto.property.PriceAnalysisResponse;
import com.ssafy.salmanhae.model.dto.property.PropertyType;
import com.ssafy.salmanhae.model.dto.property.TransactionType;
import com.ssafy.salmanhae.service.property.PropertyService;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/price-analysis")
@Validated
public class PriceAnalysisController {

	private final PropertyService propertyService;

	public PriceAnalysisController(PropertyService propertyService) {
		this.propertyService = propertyService;
	}

	@GetMapping
	public ApiResponse<PriceAnalysisResponse> getPriceAnalysis(
			@RequestParam @NotBlank @Pattern(regexp = "\\d{10}") String legalDongCode,
			@RequestParam @NotNull PropertyType propertyType,
			@RequestParam @NotNull TransactionType transactionType
	) {
		return ApiResponse.ok(propertyService.getPriceAnalysis(legalDongCode, propertyType, transactionType));
	}
}
