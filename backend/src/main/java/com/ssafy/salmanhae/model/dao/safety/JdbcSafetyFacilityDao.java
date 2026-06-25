package com.ssafy.salmanhae.model.dao.safety;

import java.math.BigDecimal;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.jdbc.core.RowMapper;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.stereotype.Repository;

import com.ssafy.salmanhae.model.dto.safety.SafetyFacilityRow;
import com.ssafy.salmanhae.model.dto.safety.SafetyFacilityType;

@Repository
public class JdbcSafetyFacilityDao implements SafetyFacilityDao {

	private final NamedParameterJdbcTemplate jdbcTemplate;

	public JdbcSafetyFacilityDao(NamedParameterJdbcTemplate jdbcTemplate) {
		this.jdbcTemplate = jdbcTemplate;
	}

	@Override
	public List<SafetyFacilityRow> findInBounds(
			List<SafetyFacilityType> types,
			BigDecimal west,
			BigDecimal east,
			BigDecimal south,
			BigDecimal north
	) {
		Map<String, Object> params = new HashMap<>();
		params.put("west", west);
		params.put("east", east);
		params.put("south", south);
		params.put("north", north);

		StringBuilder sql = new StringBuilder("""
				SELECT id, type, name, address, latitude, longitude, source, source_id, description
				FROM safety_facility
				WHERE longitude BETWEEN :west AND :east
				  AND latitude BETWEEN :south AND :north
				""");
		if (types != null && !types.isEmpty()) {
			sql.append(" AND type IN (:types)");
			params.put("types", types.stream().map(Enum::name).toList());
		}
		sql.append(" ORDER BY type, name, id");

		return jdbcTemplate.query(sql.toString(), params, safetyFacilityRowMapper());
	}

	@Override
	public int upsert(SafetyFacilityRow row) {
		if (!hasUsableCoordinates(row)) {
			return 0;
		}

		Map<String, Object> params = rowParams(row);
		int updated = jdbcTemplate.update("""
				UPDATE safety_facility
				SET name = :name,
				    address = :address,
				    latitude = :latitude,
				    longitude = :longitude,
				    description = :description,
				    updated_at = CURRENT_TIMESTAMP
				WHERE type = :type
				  AND source = :source
				  AND source_id = :sourceId
				""", params);
		if (updated > 0) {
			return updated;
		}
		return jdbcTemplate.update("""
				INSERT INTO safety_facility (
				    type, name, address, latitude, longitude, source, source_id, description,
				    created_at, updated_at
				) VALUES (
				    :type, :name, :address, :latitude, :longitude, :source, :sourceId, :description,
				    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
				)
				""", params);
	}

	@Override
	public int upsertAll(List<SafetyFacilityRow> rows) {
		if (rows == null || rows.isEmpty()) {
			return 0;
		}
		return rows.stream()
				.mapToInt(this::upsert)
				.sum();
	}

	private Map<String, Object> rowParams(SafetyFacilityRow row) {
		Map<String, Object> params = new HashMap<>();
		params.put("type", row.type().name());
		params.put("name", row.name());
		params.put("address", row.address());
		params.put("latitude", row.latitude());
		params.put("longitude", row.longitude());
		params.put("source", row.source());
		params.put("sourceId", row.sourceId());
		params.put("description", row.description());
		return params;
	}

	private boolean hasUsableCoordinates(SafetyFacilityRow row) {
		if (row == null || row.type() == null || row.latitude() == null || row.longitude() == null) {
			return false;
		}
		return isInRange(row.latitude(), "-90", "90") && isInRange(row.longitude(), "-180", "180");
	}

	private boolean isInRange(BigDecimal value, String min, String max) {
		return value.compareTo(new BigDecimal(min)) >= 0 && value.compareTo(new BigDecimal(max)) <= 0;
	}

	private RowMapper<SafetyFacilityRow> safetyFacilityRowMapper() {
		return (rs, rowNum) -> new SafetyFacilityRow(
				rs.getLong("id"),
				SafetyFacilityType.valueOf(rs.getString("type")),
				rs.getString("name"),
				rs.getString("address"),
				rs.getBigDecimal("latitude"),
				rs.getBigDecimal("longitude"),
				rs.getString("source"),
				rs.getString("source_id"),
				rs.getString("description")
		);
	}
}
