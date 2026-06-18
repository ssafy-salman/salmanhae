package com.ssafy.salmanhae.service.property;

import java.util.List;

import org.springframework.stereotype.Service;

import com.ssafy.salmanhae.common.exception.ApiException;
import com.ssafy.salmanhae.common.exception.ErrorCode;
import com.ssafy.salmanhae.model.dao.property.PropertyDao;
import com.ssafy.salmanhae.model.dto.property.PropertyDetailResponse;
import com.ssafy.salmanhae.model.dto.property.PropertySearchCriteria;
import com.ssafy.salmanhae.model.dto.property.PropertySummaryResponse;

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
}
