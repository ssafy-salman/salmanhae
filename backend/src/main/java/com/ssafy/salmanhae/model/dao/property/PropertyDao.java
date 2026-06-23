package com.ssafy.salmanhae.model.dao.property;

import java.util.List;
import java.util.Optional;

import com.ssafy.salmanhae.model.dto.property.BuildingPriceStatResponse;
import com.ssafy.salmanhae.model.dto.property.PropertySafetySummaryResponse;
import com.ssafy.salmanhae.model.dto.property.PropertyTransactionResponse;
import com.ssafy.salmanhae.model.dto.property.PropertyType;
import com.ssafy.salmanhae.model.dto.property.RegionPriceStatResponse;
import com.ssafy.salmanhae.model.dto.property.PropertyRow;
import com.ssafy.salmanhae.model.dto.property.PropertySearchCriteria;
import com.ssafy.salmanhae.model.dto.property.TransactionType;

public interface PropertyDao {

	List<PropertyRow> findInBounds(PropertySearchCriteria criteria);

	Optional<PropertyRow> findActiveById(Long propertyId);

	List<PropertyTransactionResponse> findComparableTransactions(PropertyRow property, String minContractYearMonth);

	Optional<PropertySafetySummaryResponse> findSafetySummary(Long propertyId, Integer radius);

	List<RegionPriceStatResponse> findRegionPriceStats(
			String legalDongCode,
			PropertyType propertyType,
			TransactionType transactionType
	);

	List<BuildingPriceStatResponse> findBuildingPriceStats(
			String legalDongCode,
			PropertyType propertyType,
			TransactionType transactionType
	);
}
