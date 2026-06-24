package com.ssafy.salmanhae.model.dto.map;

public sealed interface MapViewportItemResponse permits RegionAverageViewportItem, PropertyClusterViewportItem, PropertyViewportItem {

	MapViewportItemType type();
}
