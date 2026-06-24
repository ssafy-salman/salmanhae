package com.ssafy.salmanhae.service.map;

import org.springframework.stereotype.Service;

import com.ssafy.salmanhae.common.exception.ApiException;
import com.ssafy.salmanhae.common.exception.ErrorCode;
import com.ssafy.salmanhae.model.dto.map.MapViewportMode;
import com.ssafy.salmanhae.model.dto.map.MapViewportRequest;
import com.ssafy.salmanhae.model.dto.map.MapViewportResponse;

@Service
public class MapViewportServiceImpl implements MapViewportService {

	@Override
	public MapViewportResponse getViewport(MapViewportRequest request) {
		if (request == null || request.criteria() == null) {
			throw new ApiException(ErrorCode.INVALID_REQUEST);
		}
		request.criteria().validateBounds();
		return MapViewportResponse.empty(resolveMode(request.zoom()));
	}

	private MapViewportMode resolveMode(int zoom) {
		if (zoom <= 11) {
			return MapViewportMode.SIGUNGU_AVG;
		}
		if (zoom <= 13) {
			return MapViewportMode.DONG_AVG;
		}
		if (zoom <= 15) {
			return MapViewportMode.PROPERTY_CLUSTER;
		}
		return MapViewportMode.PROPERTY_MARKER;
	}
}
