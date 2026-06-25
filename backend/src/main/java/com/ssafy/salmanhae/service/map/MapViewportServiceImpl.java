package com.ssafy.salmanhae.service.map;

import java.math.BigDecimal;
import java.util.List;

import org.springframework.stereotype.Service;

import com.ssafy.salmanhae.common.exception.ApiException;
import com.ssafy.salmanhae.common.exception.ErrorCode;
import com.ssafy.salmanhae.model.dao.property.PropertyDao;
import com.ssafy.salmanhae.model.dto.map.MapViewportItemResponse;
import com.ssafy.salmanhae.model.dto.map.MapViewportItemType;
import com.ssafy.salmanhae.model.dto.map.MapViewportMode;
import com.ssafy.salmanhae.model.dto.map.MapViewportRequest;
import com.ssafy.salmanhae.model.dto.map.MapViewportResponse;
import com.ssafy.salmanhae.model.dto.map.PropertyViewportItem;
import com.ssafy.salmanhae.model.dto.property.PropertyRow;

@Service
public class MapViewportServiceImpl implements MapViewportService {

	private static final int REGION_ITEM_LIMIT = 200;
	private static final int CLUSTER_ITEM_LIMIT = 500;
	private static final int PROPERTY_ITEM_LIMIT = 500;
	private static final BigDecimal CLUSTER_GRID_ZOOM_14 = new BigDecimal("0.005");
	private static final BigDecimal CLUSTER_GRID_ZOOM_15 = new BigDecimal("0.0025");

	private final PropertyDao propertyDao;

	public MapViewportServiceImpl(PropertyDao propertyDao) {
		this.propertyDao = propertyDao;
	}

	@Override
	public MapViewportResponse getViewport(MapViewportRequest request) {
		if (request == null || request.criteria() == null) {
			throw new ApiException(ErrorCode.INVALID_REQUEST);
		}
		request.criteria().validateBounds();
		MapViewportMode mode = resolveMode(request.zoom());
		return switch (mode) {
			case SIDO_AVG -> MapViewportResponse.from(
					mode,
					propertyDao.findRegionAverageViewportItems(request.criteria(), "SIDO", REGION_ITEM_LIMIT)
			);
			case SIGUNGU_AVG -> MapViewportResponse.from(
					mode,
					propertyDao.findRegionAverageViewportItems(request.criteria(), "SIGUNGU", REGION_ITEM_LIMIT)
			);
			case DONG_AVG -> MapViewportResponse.from(
					mode,
					propertyDao.findRegionAverageViewportItems(request.criteria(), "DONG", REGION_ITEM_LIMIT)
			);
			case PROPERTY_CLUSTER -> MapViewportResponse.from(
					mode,
					propertyDao.findPropertyClusters(request.criteria(), clusterGridSize(request.zoom()), CLUSTER_ITEM_LIMIT)
			);
			case PROPERTY_MARKER -> MapViewportResponse.from(
					mode,
					toPropertyItems(propertyDao.findViewportProperties(request.criteria(), PROPERTY_ITEM_LIMIT))
			);
		};
	}

	private MapViewportMode resolveMode(int zoom) {
		if (zoom <= 9) {
			return MapViewportMode.SIDO_AVG;
		}
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

	private BigDecimal clusterGridSize(int zoom) {
		return zoom <= 14 ? CLUSTER_GRID_ZOOM_14 : CLUSTER_GRID_ZOOM_15;
	}

	private List<MapViewportItemResponse> toPropertyItems(List<PropertyRow> properties) {
		return properties.stream()
				.map(property -> (MapViewportItemResponse) new PropertyViewportItem(
						MapViewportItemType.PROPERTY,
						property.id(),
						property.title(),
						property.transactionType(),
						property.deposit(),
						property.monthlyRent(),
						property.price(),
						property.areaM2(),
						property.latitude(),
						property.longitude()
				))
				.toList();
	}
}
