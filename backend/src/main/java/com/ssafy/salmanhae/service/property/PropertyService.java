package com.ssafy.salmanhae.service.property;

import java.util.List;

import com.ssafy.salmanhae.model.dto.property.PriceAnalysisResponse;
import com.ssafy.salmanhae.model.dto.property.PropertySafetySummaryResponse;
import com.ssafy.salmanhae.model.dto.property.PropertyDetailResponse;
import com.ssafy.salmanhae.model.dto.property.PropertySearchCriteria;
import com.ssafy.salmanhae.model.dto.property.PropertySummaryResponse;
import com.ssafy.salmanhae.model.dto.property.PropertyTransactionResponse;
import com.ssafy.salmanhae.model.dto.property.PropertyType;
import com.ssafy.salmanhae.model.dto.property.TransactionType;

public interface PropertyService {

	List<PropertySummaryResponse> searchProperties(PropertySearchCriteria criteria);

	PropertyDetailResponse getProperty(Long propertyId);

	List<PropertyTransactionResponse> getTransactions(Long propertyId, Integer years);

	PropertySafetySummaryResponse getSafetySummary(Long propertyId, Integer radius);

	PriceAnalysisResponse getPriceAnalysis(
			String legalDongCode,
			PropertyType propertyType,
			TransactionType transactionType
	);
}
