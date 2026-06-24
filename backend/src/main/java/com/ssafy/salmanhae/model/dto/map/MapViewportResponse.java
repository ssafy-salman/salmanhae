package com.ssafy.salmanhae.model.dto.map;

import java.util.List;

public record MapViewportResponse(
		MapViewportMode mode,
		List<MapViewportItemResponse> items,
		int totalCount
) {

	public static MapViewportResponse empty(MapViewportMode mode) {
		return new MapViewportResponse(mode, List.of(), 0);
	}
}
