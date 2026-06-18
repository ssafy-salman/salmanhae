package com.ssafy.salmanhae.model.dao.property;

import java.util.List;
import java.util.Optional;

import com.ssafy.salmanhae.model.dto.property.PropertyRow;
import com.ssafy.salmanhae.model.dto.property.PropertySearchCriteria;

public interface PropertyDao {

	List<PropertyRow> findInBounds(PropertySearchCriteria criteria);

	Optional<PropertyRow> findActiveById(Long propertyId);
}
