package com.ssafy.salmanhae.service.property;

import java.time.YearMonth;
import java.util.List;

import org.springframework.stereotype.Service;

import com.ssafy.salmanhae.common.exception.ApiException;
import com.ssafy.salmanhae.common.exception.ErrorCode;
import com.ssafy.salmanhae.model.dao.property.PropertyDao;
import com.ssafy.salmanhae.model.dto.property.PriceAnalysisResponse;
import com.ssafy.salmanhae.model.dto.property.PropertySafetySummaryResponse;
import com.ssafy.salmanhae.model.dto.property.PropertyDetailResponse;
import com.ssafy.salmanhae.model.dto.property.PropertyRow;
import com.ssafy.salmanhae.model.dto.property.PropertySearchCriteria;
import com.ssafy.salmanhae.model.dto.property.PropertySummaryResponse;
import com.ssafy.salmanhae.model.dto.property.PropertyTransactionResponse;
import com.ssafy.salmanhae.model.dto.property.PropertyType;
import com.ssafy.salmanhae.model.dto.property.TransactionType;

@Service
public class PropertyServiceImpl implements PropertyService {

	private final PropertyDao propertyDao;

	public PropertyServiceImpl(PropertyDao propertyDao) {
		this.propertyDao = propertyDao;
	}

	@Override
	public List<PropertySummaryResponse> searchProperties(PropertySearchCriteria criteria) {
		criteria.validateBounds();
		return propertyDao.findInBounds(criteria).stream()
				.map(PropertySummaryResponse::from)
				.toList();
	}

	@Override
	public PropertyDetailResponse getProperty(Long propertyId) {
		return propertyDao.findActiveById(propertyId)
				.map(PropertyDetailResponse::from)
				.orElseThrow(() -> new ApiException(ErrorCode.PROPERTY_NOT_FOUND));
	}

	@Override
	public List<PropertyTransactionResponse> getTransactions(Long propertyId, Integer years) {
		PropertyRow property = getActiveProperty(propertyId);
		int lookupYears = years == null ? 3 : years;
		if (lookupYears < 1) {
			throw new ApiException(ErrorCode.INVALID_REQUEST);
		}
		String minContractYearMonth = YearMonth.now().minusYears(lookupYears).toString().replace("-", "");
		return propertyDao.findComparableTransactions(property, minContractYearMonth);
	}

	@Override
	public PropertySafetySummaryResponse getSafetySummary(Long propertyId, Integer radius) {
		getActiveProperty(propertyId);
		Integer lookupRadius = radius == null ? 500 : radius;
		if (lookupRadius < 1) {
			throw new ApiException(ErrorCode.INVALID_REQUEST);
		}
		return propertyDao.findSafetySummary(propertyId, lookupRadius)
				.orElse(new PropertySafetySummaryResponse(propertyId, lookupRadius, null, null, 0, 0, 0, 0));
	}

	@Override
	public PriceAnalysisResponse getPriceAnalysis(
			String legalDongCode,
			PropertyType propertyType,
			TransactionType transactionType
	) {
		if (legalDongCode == null || legalDongCode.isBlank() || propertyType == null || transactionType == null) {
			throw new ApiException(ErrorCode.INVALID_REQUEST);
		}
		return new PriceAnalysisResponse(
				legalDongCode,
				propertyType,
				transactionType,
				propertyDao.findRegionPriceStats(legalDongCode, propertyType, transactionType),
				propertyDao.findBuildingPriceStats(legalDongCode, propertyType, transactionType)
		);
	}

	private PropertyRow getActiveProperty(Long propertyId) {
		return propertyDao.findActiveById(propertyId)
				.orElseThrow(() -> new ApiException(ErrorCode.PROPERTY_NOT_FOUND));
	}
}
