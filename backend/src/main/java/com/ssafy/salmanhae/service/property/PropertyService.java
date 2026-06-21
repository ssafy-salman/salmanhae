package com.ssafy.salmanhae.service.property;

import java.util.List;

import com.ssafy.salmanhae.model.dto.property.PropertyDetailResponse;
import com.ssafy.salmanhae.model.dto.property.PropertySearchCriteria;
import com.ssafy.salmanhae.model.dto.property.PropertySummaryResponse;

public interface PropertyService {

	List<PropertySummaryResponse> searchProperties(PropertySearchCriteria criteria);

	PropertyDetailResponse getProperty(Long propertyId);
}
