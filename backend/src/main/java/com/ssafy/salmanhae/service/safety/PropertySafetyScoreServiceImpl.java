package com.ssafy.salmanhae.service.safety;

import java.math.BigDecimal;
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
	private static final double CCTV_WEIGHT = 30.0;
	private static final double BELL_WEIGHT = 25.0;
	private static final double LIGHT_WEIGHT = 25.0;
	private static final double POLICE_WEIGHT = 20.0;
	private static final double EARTH_RADIUS_M = 6_371_000.0;
	private static final double METERS_PER_LATITUDE_DEGREE = 111_320.0;
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
		List<PropertySafetyScoreResult> results = propertyDao.findActivePropertiesForSafetyScoring().stream()
				.map(this::calculateForProperty)
				.toList();
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

	private PropertySafetyScoreResult calculateForProperty(PropertyRow property) {
		List<SafetyFacilityRow> facilities = findNearbyCandidates(property);
		int cctvCount300m = 0;
		int bellCount300m = 0;
		int lightCount300m = 0;
		int policeCount500m = 0;

		for (SafetyFacilityRow facility : facilities) {
			if (facility == null || facility.type() == null || facility.latitude() == null || facility.longitude() == null) {
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

	private List<SafetyFacilityRow> findNearbyCandidates(PropertyRow property) {
		BigDecimal latitude = property.latitude();
		BigDecimal longitude = property.longitude();
		double latitudeDelta = POLICE_RADIUS_M / METERS_PER_LATITUDE_DEGREE;
		double longitudeMetersPerDegree = METERS_PER_LATITUDE_DEGREE * Math.cos(Math.toRadians(latitude.doubleValue()));
		double longitudeDelta = POLICE_RADIUS_M / Math.max(1.0, longitudeMetersPerDegree);
		return safetyFacilityDao.findInBounds(
				SCORE_TYPES,
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
}
