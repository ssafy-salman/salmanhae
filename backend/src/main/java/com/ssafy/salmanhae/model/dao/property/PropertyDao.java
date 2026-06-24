package com.ssafy.salmanhae.model.dao.property;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;

import com.ssafy.salmanhae.model.dto.map.PropertyClusterViewportItem;
import com.ssafy.salmanhae.model.dto.map.RegionAverageViewportItem;
import com.ssafy.salmanhae.model.dto.property.BuildingPriceStatResponse;
import com.ssafy.salmanhae.model.dto.property.PropertySafetySummaryResponse;
import com.ssafy.salmanhae.model.dto.property.PropertyTransactionResponse;
import com.ssafy.salmanhae.model.dto.property.PropertyType;
import com.ssafy.salmanhae.model.dto.property.RegionPriceStatResponse;
import com.ssafy.salmanhae.model.dto.property.PropertyRow;
import com.ssafy.salmanhae.model.dto.property.PropertySearchCriteria;
import com.ssafy.salmanhae.model.dto.property.TransactionType;
import com.ssafy.salmanhae.model.dto.safety.PropertySafetyScoreResult;

public interface PropertyDao {

	List<PropertyRow> findInBounds(PropertySearchCriteria criteria);

	List<PropertyRow> findViewportProperties(PropertySearchCriteria criteria, int limit);

	List<RegionAverageViewportItem> findRegionAverageViewportItems(
			PropertySearchCriteria criteria,
			String regionLevel,
			int limit
	);

	List<PropertyClusterViewportItem> findPropertyClusters(
			PropertySearchCriteria criteria,
			BigDecimal gridSize,
			int limit
	);

	Optional<PropertyRow> findActiveById(Long propertyId);

	List<PropertyRow> findActivePropertiesForSafetyScoring();

	List<PropertyTransactionResponse> findComparableTransactions(PropertyRow property, String minContractYearMonth);

	Optional<PropertySafetySummaryResponse> findSafetySummary(Long propertyId, Integer radius);

	int upsertSafetyScoreStats(List<PropertySafetyScoreResult> results);

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
