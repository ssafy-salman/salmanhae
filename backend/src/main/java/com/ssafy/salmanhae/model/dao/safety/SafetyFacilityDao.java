package com.ssafy.salmanhae.model.dao.safety;

import java.math.BigDecimal;
import java.util.List;

import com.ssafy.salmanhae.model.dto.safety.SafetyFacilityRow;
import com.ssafy.salmanhae.model.dto.safety.SafetyFacilityType;

public interface SafetyFacilityDao {

	List<SafetyFacilityRow> findInBounds(
			List<SafetyFacilityType> types,
			BigDecimal west,
			BigDecimal east,
			BigDecimal south,
			BigDecimal north
	);

	int upsert(SafetyFacilityRow row);

	int upsertAll(List<SafetyFacilityRow> rows);
}
