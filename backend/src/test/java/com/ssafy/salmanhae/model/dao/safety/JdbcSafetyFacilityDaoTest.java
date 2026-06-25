package com.ssafy.salmanhae.model.dao.safety;

import static org.assertj.core.api.Assertions.assertThat;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.test.context.ActiveProfiles;

import com.ssafy.salmanhae.model.dto.safety.SafetyFacilityRow;
import com.ssafy.salmanhae.model.dto.safety.SafetyFacilityType;

@SpringBootTest
@ActiveProfiles("test")
class JdbcSafetyFacilityDaoTest {

	@Autowired
	private SafetyFacilityDao safetyFacilityDao;

	@Autowired
	private NamedParameterJdbcTemplate jdbcTemplate;

	@Test
	void findInBoundsFiltersByTypesAndCoordinates() {
		List<SafetyFacilityRow> rows = safetyFacilityDao.findInBounds(
				List.of(SafetyFacilityType.CCTV, SafetyFacilityType.EMERGENCY_BELL),
				new BigDecimal("126.9300000"),
				new BigDecimal("126.9400000"),
				new BigDecimal("37.4600000"),
				new BigDecimal("37.4800000")
		);

		assertThat(rows)
				.extracting(SafetyFacilityRow::type)
				.containsExactly(SafetyFacilityType.CCTV, SafetyFacilityType.EMERGENCY_BELL);
	}

	@Test
	void upsertUpdatesExistingSourceRow() {
		SafetyFacilityRow updated = new SafetyFacilityRow(
				null,
				SafetyFacilityType.CCTV,
				"Updated CCTV",
				"updated address",
				new BigDecimal("37.4720000"),
				new BigDecimal("126.9380000"),
				"TEST",
				"cctv-1",
				"updated"
		);

		int affectedRows = safetyFacilityDao.upsert(updated);
		Integer count = jdbcTemplate.queryForObject(
				"""
				SELECT COUNT(*)
				FROM safety_facility
				WHERE type = 'CCTV'
				  AND source = 'TEST'
				  AND source_id = 'cctv-1'
				""",
				Map.of(),
				Integer.class
		);
		String name = jdbcTemplate.queryForObject(
				"""
				SELECT name
				FROM safety_facility
				WHERE type = 'CCTV'
				  AND source = 'TEST'
				  AND source_id = 'cctv-1'
				""",
				Map.of(),
				String.class
		);

		assertThat(affectedRows).isEqualTo(1);
		assertThat(count).isEqualTo(1);
		assertThat(name).isEqualTo("Updated CCTV");
	}

	@Test
	void upsertSkipsRowsWithInvalidCoordinates() {
		SafetyFacilityRow invalid = new SafetyFacilityRow(
				null,
				SafetyFacilityType.POLICE,
				"Invalid Police",
				"invalid address",
				new BigDecimal("91.0000000"),
				new BigDecimal("126.9380000"),
				"TEST",
				"invalid-police",
				null
		);

		int affectedRows = safetyFacilityDao.upsert(invalid);
		Integer count = jdbcTemplate.queryForObject(
				"""
				SELECT COUNT(*)
				FROM safety_facility
				WHERE source = 'TEST'
				  AND source_id = 'invalid-police'
				""",
				Map.of(),
				Integer.class
		);

		assertThat(affectedRows).isZero();
		assertThat(count).isZero();
	}
}
