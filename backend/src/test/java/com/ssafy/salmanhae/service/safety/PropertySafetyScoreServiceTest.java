package com.ssafy.salmanhae.service.safety;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.argThat;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.math.BigDecimal;
import java.util.List;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import com.ssafy.salmanhae.model.dao.property.PropertyDao;
import com.ssafy.salmanhae.model.dao.safety.SafetyFacilityDao;
import com.ssafy.salmanhae.model.dto.property.PropertyRow;
import com.ssafy.salmanhae.model.dto.property.PropertyType;
import com.ssafy.salmanhae.model.dto.property.TransactionType;
import com.ssafy.salmanhae.model.dto.safety.PropertySafetyScoreInput;
import com.ssafy.salmanhae.model.dto.safety.PropertySafetyScoreResult;
import com.ssafy.salmanhae.model.dto.safety.SafetyFacilityRow;
import com.ssafy.salmanhae.model.dto.safety.SafetyFacilityType;

@ExtendWith(MockitoExtension.class)
class PropertySafetyScoreServiceTest {

	@Mock
	private PropertyDao propertyDao;

	@Mock
	private SafetyFacilityDao safetyFacilityDao;

	@Test
	void calculateScoreUsesDocumentedWeightsAndCaps() {
		PropertySafetyScoreService service = new PropertySafetyScoreServiceImpl(propertyDao, safetyFacilityDao);

		PropertySafetyScoreResult result = service.calculateScore(
				new PropertySafetyScoreInput(1L, 8, 2, 14, 1)
		);

		assertThat(result.safetyScore()).isEqualTo(78);
		assertThat(result.cctvCount300m()).isEqualTo(8);
		assertThat(result.bellCount300m()).isEqualTo(2);
		assertThat(result.lightCount300m()).isEqualTo(14);
		assertThat(result.policeCount500m()).isEqualTo(1);
	}

	@Test
	void recalculateAllCountsFacilitiesByRadiusAndUpsertsResults() {
		PropertyRow property = property(1L, "37.4700000", "126.9360000");
		when(propertyDao.findActivePropertiesForSafetyScoring()).thenReturn(List.of(property));
		when(safetyFacilityDao.findInBounds(
				argThat(types -> types != null && types.size() == 4),
				argThat(west -> west.compareTo(new BigDecimal("126.931")) < 0),
				argThat(east -> east.compareTo(new BigDecimal("126.941")) > 0),
				argThat(south -> south.compareTo(new BigDecimal("37.466")) < 0),
				argThat(north -> north.compareTo(new BigDecimal("37.474")) > 0)
		)).thenReturn(List.of(
				facility(SafetyFacilityType.CCTV, "37.4701000", "126.9361000"),
				facility(SafetyFacilityType.EMERGENCY_BELL, "37.4702000", "126.9361000"),
				facility(SafetyFacilityType.SECURITY_LIGHT, "37.4703000", "126.9361000"),
				facility(SafetyFacilityType.POLICE, "37.4735000", "126.9360000"),
				facility(SafetyFacilityType.CCTV, "37.4800000", "126.9360000")
		));
		when(propertyDao.upsertSafetyScoreStats(argThat(results -> results != null && results.size() == 1)))
				.thenReturn(1);
		PropertySafetyScoreService service = new PropertySafetyScoreServiceImpl(propertyDao, safetyFacilityDao);

		List<PropertySafetyScoreResult> results = service.recalculateAll();

		assertThat(results).hasSize(1);
		PropertySafetyScoreResult result = results.getFirst();
		assertThat(result.propertyId()).isEqualTo(1L);
		assertThat(result.cctvCount300m()).isEqualTo(1);
		assertThat(result.bellCount300m()).isEqualTo(1);
		assertThat(result.lightCount300m()).isEqualTo(1);
		assertThat(result.policeCount500m()).isEqualTo(1);
		assertThat(result.safetyScore()).isEqualTo(33);
		verify(propertyDao).upsertSafetyScoreStats(results);
	}

	private PropertyRow property(Long id, String latitude, String longitude) {
		return new PropertyRow(
				id,
				"Test Property",
				"Test Building",
				"building-key",
				"address",
				"road address",
				"1162010200",
				PropertyType.ONE_ROOM,
				TransactionType.MONTHLY_RENT,
				10_000_000L,
				550_000L,
				null,
				70_000L,
				new BigDecimal("22.50"),
				3,
				5,
				new BigDecimal(latitude),
				new BigDecimal(longitude),
				"description"
		);
	}

	private SafetyFacilityRow facility(SafetyFacilityType type, String latitude, String longitude) {
		return new SafetyFacilityRow(
				null,
				type,
				type.name(),
				"address",
				new BigDecimal(latitude),
				new BigDecimal(longitude),
				"TEST",
				type.name() + "-1",
				"description"
		);
	}
}
