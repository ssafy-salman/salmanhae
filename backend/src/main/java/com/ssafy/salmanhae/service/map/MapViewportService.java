package com.ssafy.salmanhae.service.map;

import com.ssafy.salmanhae.model.dto.map.MapViewportRequest;
import com.ssafy.salmanhae.model.dto.map.MapViewportResponse;

public interface MapViewportService {

	MapViewportResponse getViewport(MapViewportRequest request);
}
