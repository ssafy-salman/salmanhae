package com.ssafy.salmanhae.service.safety;

import java.util.List;

import com.ssafy.salmanhae.model.dto.safety.PropertySafetyScoreInput;
import com.ssafy.salmanhae.model.dto.safety.PropertySafetyScoreResult;

public interface PropertySafetyScoreService {

	List<PropertySafetyScoreResult> recalculateAll();

	PropertySafetyScoreResult calculateScore(PropertySafetyScoreInput input);
}
