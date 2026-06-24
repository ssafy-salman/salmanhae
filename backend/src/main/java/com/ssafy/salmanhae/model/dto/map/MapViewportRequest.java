package com.ssafy.salmanhae.model.dto.map;

import com.ssafy.salmanhae.model.dto.property.PropertySearchCriteria;

public record MapViewportRequest(
		PropertySearchCriteria criteria,
		int zoom,
		Integer clusterThreshold
) {
}
