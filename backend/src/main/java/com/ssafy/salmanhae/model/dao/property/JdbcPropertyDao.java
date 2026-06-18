package com.ssafy.salmanhae.model.dao.property;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import org.springframework.jdbc.core.RowMapper;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.stereotype.Repository;

import com.ssafy.salmanhae.model.dto.property.PropertyRow;
import com.ssafy.salmanhae.model.dto.property.PropertySearchCriteria;
import com.ssafy.salmanhae.model.dto.property.PropertyType;
import com.ssafy.salmanhae.model.dto.property.TransactionType;

@Repository
public class JdbcPropertyDao implements PropertyDao {

	private static final String PROPERTY_COLUMNS = """
			id, title, building_name, building_key, address, road_address,
			legal_dong_code, property_type, transaction_type, deposit, monthly_rent,
			price, maintenance_fee, area_m2, floor, total_floor, latitude, longitude,
			description
			""";

	private final NamedParameterJdbcTemplate jdbcTemplate;

	public JdbcPropertyDao(NamedParameterJdbcTemplate jdbcTemplate) {
		this.jdbcTemplate = jdbcTemplate;
	}

	@Override
	public List<PropertyRow> findInBounds(PropertySearchCriteria criteria) {
		Map<String, Object> params = new HashMap<>();
		params.put("west", criteria.west());
		params.put("east", criteria.east());
		params.put("south", criteria.south());
		params.put("north", criteria.north());

		StringBuilder sql = new StringBuilder("""
				SELECT %s
				FROM properties
				WHERE is_active = true
				  AND longitude BETWEEN :west AND :east
				  AND latitude BETWEEN :south AND :north
				""".formatted(PROPERTY_COLUMNS));

		if (criteria.transactionType() != null) {
			sql.append(" AND transaction_type = :transactionType");
			params.put("transactionType", criteria.transactionType().name());
		}
		if (criteria.propertyType() != null) {
			sql.append(" AND property_type = :propertyType");
			params.put("propertyType", criteria.propertyType().name());
		}
		if (criteria.minDeposit() != null) {
			sql.append(" AND deposit >= :minDeposit");
			params.put("minDeposit", criteria.minDeposit());
		}
		if (criteria.maxDeposit() != null) {
			sql.append(" AND deposit <= :maxDeposit");
			params.put("maxDeposit", criteria.maxDeposit());
		}
		if (criteria.minPrice() != null) {
			sql.append(" AND price >= :minPrice");
			params.put("minPrice", criteria.minPrice());
		}
		if (criteria.maxPrice() != null) {
			sql.append(" AND price <= :maxPrice");
			params.put("maxPrice", criteria.maxPrice());
		}

		sql.append(" ORDER BY id ASC LIMIT 500");
		return jdbcTemplate.query(sql.toString(), params, propertyRowMapper());
	}

	@Override
	public Optional<PropertyRow> findActiveById(Long propertyId) {
		String sql = """
				SELECT %s
				FROM properties
				WHERE id = :id
				  AND is_active = true
				""".formatted(PROPERTY_COLUMNS);
		Map<String, Object> params = Map.of("id", propertyId);
		List<PropertyRow> rows = jdbcTemplate.query(sql, params, propertyRowMapper());
		return rows.stream().findFirst();
	}

	private RowMapper<PropertyRow> propertyRowMapper() {
		return (rs, rowNum) -> mapPropertyRow(rs);
	}

	private PropertyRow mapPropertyRow(ResultSet rs) throws SQLException {
		return new PropertyRow(
				rs.getLong("id"),
				rs.getString("title"),
				rs.getString("building_name"),
				rs.getString("building_key"),
				rs.getString("address"),
				rs.getString("road_address"),
				rs.getString("legal_dong_code"),
				PropertyType.valueOf(rs.getString("property_type")),
				TransactionType.valueOf(rs.getString("transaction_type")),
				nullableLong(rs, "deposit"),
				nullableLong(rs, "monthly_rent"),
				nullableLong(rs, "price"),
				nullableLong(rs, "maintenance_fee"),
				rs.getBigDecimal("area_m2"),
				nullableInteger(rs, "floor"),
				nullableInteger(rs, "total_floor"),
				rs.getBigDecimal("latitude"),
				rs.getBigDecimal("longitude"),
				rs.getString("description")
		);
	}

	private Long nullableLong(ResultSet rs, String column) throws SQLException {
		long value = rs.getLong(column);
		return rs.wasNull() ? null : value;
	}

	private Integer nullableInteger(ResultSet rs, String column) throws SQLException {
		int value = rs.getInt(column);
		return rs.wasNull() ? null : value;
	}
}
