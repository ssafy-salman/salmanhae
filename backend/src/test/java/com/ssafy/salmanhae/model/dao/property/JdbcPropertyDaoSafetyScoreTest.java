package com.ssafy.salmanhae.model.dao.property;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.List;
import java.util.Map;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.transaction.annotation.Transactional;

import com.ssafy.salmanhae.model.dto.safety.PropertySafetyScoreResult;

@SpringBootTest
@ActiveProfiles("test")
@Transactional
class JdbcPropertyDaoSafetyScoreTest {

	@Autowired
	private PropertyDao propertyDao;

	@Autowired
	private NamedParameterJdbcTemplate jdbcTemplate;

	@Test
	void upsertSafetyScoreStatsUpdatesSafetyFieldsAndPreservesPriceScore() {
		int affectedRows = propertyDao.upsertSafetyScoreStats(List.of(
				new PropertySafetyScoreResult(1L, 33, 1, 1, 1, 1)
		));

		Map<String, Object> row = jdbcTemplate.queryForMap(
				"""
				SELECT safety_score, price_score, cctv_count_300m, bell_count_300m,
				       light_count_300m, police_count_500m
				FROM property_score_stat
				WHERE property_id = :propertyId
				""",
				Map.of("propertyId", 1L)
		);

		assertThat(affectedRows).isEqualTo(1);
		assertThat(row.get("SAFETY_SCORE")).isEqualTo(33);
		assertThat(row.get("PRICE_SCORE")).isEqualTo(64);
		assertThat(row.get("CCTV_COUNT_300M")).isEqualTo(1);
		assertThat(row.get("BELL_COUNT_300M")).isEqualTo(1);
		assertThat(row.get("LIGHT_COUNT_300M")).isEqualTo(1);
		assertThat(row.get("POLICE_COUNT_500M")).isEqualTo(1);
	}
}
