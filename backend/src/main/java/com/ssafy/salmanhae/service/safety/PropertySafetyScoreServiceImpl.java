package com.ssafy.salmanhae.service.safety;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import com.ssafy.salmanhae.model.dao.property.PropertyDao;
import com.ssafy.salmanhae.model.dao.safety.SafetyFacilityDao;
import com.ssafy.salmanhae.model.dto.property.PropertyRow;
import com.ssafy.salmanhae.model.dto.safety.PropertySafetyScoreInput;
import com.ssafy.salmanhae.model.dto.safety.PropertySafetyScoreResult;
import com.ssafy.salmanhae.model.dto.safety.SafetyFacilityRow;
import com.ssafy.salmanhae.model.dto.safety.SafetyFacilityType;

@Service
public class PropertySafetyScoreServiceImpl implements PropertySafetyScoreService {

	private static final Logger log = LoggerFactory.getLogger(PropertySafetyScoreServiceImpl.class);

	private static final int NEAR_RADIUS_M = 300;
	private static final int POLICE_RADIUS_M = 500;
	private static final int CCTV_FULL_SCORE_COUNT = 10;
	private static final int BELL_FULL_SCORE_COUNT = 3;
	private static final int LIGHT_FULL_SCORE_COUNT = 20;
	private static final int POLICE_FULL_SCORE_COUNT = 1;
	private static final int PROPERTY_CHUNK_SIZE = 100;
	private static final double CCTV_WEIGHT = 30.0;
	private static final double BELL_WEIGHT = 25.0;
	private static final double LIGHT_WEIGHT = 25.0;
	private static final double POLICE_WEIGHT = 20.0;
	private static final double EARTH_RADIUS_M = 6_371_000.0;
	private static final double METERS_PER_DEGREE = Math.toRadians(1.0) * EARTH_RADIUS_M;
	private static final double BOUNDING_BOX_MARGIN_M = 1.0;
	private static final List<SafetyFacilityType> SCORE_TYPES = List.of(
			SafetyFacilityType.CCTV,
			SafetyFacilityType.EMERGENCY_BELL,
			SafetyFacilityType.SECURITY_LIGHT,
			SafetyFacilityType.POLICE
	);

	private final PropertyDao propertyDao;
	private final SafetyFacilityDao safetyFacilityDao;

	public PropertySafetyScoreServiceImpl(PropertyDao propertyDao, SafetyFacilityDao safetyFacilityDao) {
		this.propertyDao = propertyDao;
		this.safetyFacilityDao = safetyFacilityDao;
	}

	@Override
	public List<PropertySafetyScoreResult> recalculateAll() {
		List<PropertyRow> properties = propertyDao.findActivePropertiesForSafetyScoring();
		List<PropertyRow> spatiallyOrderedProperties = properties.stream()
				.sorted(Comparator.comparing(PropertyRow::latitude)
						.thenComparing(PropertyRow::longitude)
						.thenComparing(PropertyRow::id))
				.toList();
		List<PropertySafetyScoreResult> results = new ArrayList<>(spatiallyOrderedProperties.size());
		for (int start = 0; start < spatiallyOrderedProperties.size(); start += PROPERTY_CHUNK_SIZE) {
			List<PropertyRow> chunk = spatiallyOrderedProperties.subList(
					start,
					Math.min(start + PROPERTY_CHUNK_SIZE, spatiallyOrderedProperties.size())
			);
			List<SafetyFacilityRow> facilities = findNearbyCandidates(chunk);
			results.addAll(chunk.stream()
					.map(property -> calculateForProperty(property, facilities))
					.toList());
		}
		int upsertedCount = results.isEmpty() ? 0 : propertyDao.upsertSafetyScoreStats(results);
		log.info("Property safety score recalculation finished: calculated={}, upserted={}", results.size(), upsertedCount);
		return results;
	}

	@Override
	public PropertySafetyScoreResult calculateScore(PropertySafetyScoreInput input) {
		double weightedScore = weightedMetric(input.cctvCount300m(), CCTV_FULL_SCORE_COUNT, CCTV_WEIGHT)
				+ weightedMetric(input.bellCount300m(), BELL_FULL_SCORE_COUNT, BELL_WEIGHT)
				+ weightedMetric(input.lightCount300m(), LIGHT_FULL_SCORE_COUNT, LIGHT_WEIGHT)
				+ weightedMetric(input.policeCount500m(), POLICE_FULL_SCORE_COUNT, POLICE_WEIGHT);
		int safetyScore = Math.max(0, Math.min(100, (int) Math.round(weightedScore)));
		return new PropertySafetyScoreResult(
				input.propertyId(),
				safetyScore,
				input.cctvCount300m(),
				input.bellCount300m(),
				input.lightCount300m(),
				input.policeCount500m()
		);
	}

	private PropertySafetyScoreResult calculateForProperty(PropertyRow property, List<SafetyFacilityRow> facilities) {
		CandidateBounds bounds = candidateBounds(property);
		int cctvCount300m = 0;
		int bellCount300m = 0;
		int lightCount300m = 0;
		int policeCount500m = 0;

		for (SafetyFacilityRow facility : facilities) {
			if (facility == null || facility.type() == null || facility.latitude() == null || facility.longitude() == null) {
				continue;
			}
			if (!bounds.contains(facility)) {
				continue;
			}
			double distanceMeters = distanceMeters(
					property.latitude(),
					property.longitude(),
					facility.latitude(),
					facility.longitude()
			);
			if (facility.type() == SafetyFacilityType.POLICE && distanceMeters <= POLICE_RADIUS_M) {
				policeCount500m++;
			} else if (distanceMeters <= NEAR_RADIUS_M) {
				if (facility.type() == SafetyFacilityType.CCTV) {
					cctvCount300m++;
				} else if (facility.type() == SafetyFacilityType.EMERGENCY_BELL) {
					bellCount300m++;
				} else if (facility.type() == SafetyFacilityType.SECURITY_LIGHT) {
					lightCount300m++;
				}
			}
		}

		return calculateScore(new PropertySafetyScoreInput(
				property.id(),
				cctvCount300m,
				bellCount300m,
				lightCount300m,
				policeCount500m
		));
	}

	private List<SafetyFacilityRow> findNearbyCandidates(List<PropertyRow> properties) {
		if (properties.isEmpty()) {
			return List.of();
		}
		CandidateBounds bounds = properties.stream()
				.map(this::candidateBounds)
				.reduce(CandidateBounds::merge)
				.orElseThrow();
		return safetyFacilityDao.findInBounds(SCORE_TYPES, bounds.west(), bounds.east(), bounds.south(), bounds.north());
	}

	private CandidateBounds candidateBounds(PropertyRow property) {
		BigDecimal latitude = property.latitude();
		BigDecimal longitude = property.longitude();
		double candidateRadiusM = POLICE_RADIUS_M + BOUNDING_BOX_MARGIN_M;
		double latitudeDelta = candidateRadiusM / METERS_PER_DEGREE;
		double longitudeMetersPerDegree = METERS_PER_DEGREE * Math.cos(Math.toRadians(latitude.doubleValue()));
		double longitudeDelta = candidateRadiusM / Math.max(1.0, longitudeMetersPerDegree);
		return new CandidateBounds(
				longitude.subtract(BigDecimal.valueOf(longitudeDelta)),
				longitude.add(BigDecimal.valueOf(longitudeDelta)),
				latitude.subtract(BigDecimal.valueOf(latitudeDelta)),
				latitude.add(BigDecimal.valueOf(latitudeDelta))
		);
	}

	private double weightedMetric(int count, int fullScoreCount, double weight) {
		if (count <= 0) {
			return 0.0;
		}
		double normalized = Math.min(1.0, (double) count / fullScoreCount);
		return normalized * weight;
	}

	private double distanceMeters(
			BigDecimal firstLatitude,
			BigDecimal firstLongitude,
			BigDecimal secondLatitude,
			BigDecimal secondLongitude
	) {
		double lat1 = Math.toRadians(firstLatitude.doubleValue());
		double lat2 = Math.toRadians(secondLatitude.doubleValue());
		double deltaLat = Math.toRadians(secondLatitude.subtract(firstLatitude).doubleValue());
		double deltaLon = Math.toRadians(secondLongitude.subtract(firstLongitude).doubleValue());
		double a = Math.sin(deltaLat / 2) * Math.sin(deltaLat / 2)
				+ Math.cos(lat1) * Math.cos(lat2) * Math.sin(deltaLon / 2) * Math.sin(deltaLon / 2);
		double c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
		return EARTH_RADIUS_M * c;
	}

	private record CandidateBounds(
			BigDecimal west,
			BigDecimal east,
			BigDecimal south,
			BigDecimal north
	) {

		private CandidateBounds merge(CandidateBounds other) {
			return new CandidateBounds(
					min(west, other.west),
					max(east, other.east),
					min(south, other.south),
					max(north, other.north)
			);
		}

		private boolean contains(SafetyFacilityRow facility) {
			return facility.longitude().compareTo(west) >= 0
					&& facility.longitude().compareTo(east) <= 0
					&& facility.latitude().compareTo(south) >= 0
					&& facility.latitude().compareTo(north) <= 0;
		}

		private BigDecimal min(BigDecimal first, BigDecimal second) {
			return first.compareTo(second) <= 0 ? first : second;
		}

		private BigDecimal max(BigDecimal first, BigDecimal second) {
			return first.compareTo(second) >= 0 ? first : second;
		}
	}
}
