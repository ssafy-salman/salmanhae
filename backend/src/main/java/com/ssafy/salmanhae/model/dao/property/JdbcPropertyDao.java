package com.ssafy.salmanhae.model.dao.property;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.math.BigDecimal;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import org.springframework.jdbc.core.RowMapper;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.stereotype.Repository;

import com.ssafy.salmanhae.model.dto.map.MapViewportItemType;
import com.ssafy.salmanhae.model.dto.map.PropertyClusterViewportItem;
import com.ssafy.salmanhae.model.dto.map.RegionAverageViewportItem;
import com.ssafy.salmanhae.model.dto.property.BuildingPriceStatResponse;
import com.ssafy.salmanhae.model.dto.property.PropertySafetySummaryResponse;
import com.ssafy.salmanhae.model.dto.property.PropertyRow;
import com.ssafy.salmanhae.model.dto.property.PropertySearchCriteria;
import com.ssafy.salmanhae.model.dto.property.PropertyTransactionResponse;
import com.ssafy.salmanhae.model.dto.property.PropertyType;
import com.ssafy.salmanhae.model.dto.property.RegionPriceStatResponse;
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

		sql.append(" ORDER BY id ASC");
		return jdbcTemplate.query(sql.toString(), params, propertyRowMapper());
	}

	@Override
	public List<PropertyRow> findViewportProperties(PropertySearchCriteria criteria, int limit) {
		Map<String, Object> params = new HashMap<>();
		params.put("west", criteria.west());
		params.put("east", criteria.east());
		params.put("south", criteria.south());
		params.put("north", criteria.north());
		params.put("limit", limit);

		StringBuilder sql = new StringBuilder("""
				SELECT %s
				FROM properties
				WHERE is_active = true
				  AND longitude BETWEEN :west AND :east
				  AND latitude BETWEEN :south AND :north
				""".formatted(PROPERTY_COLUMNS));
		appendPropertyFilters(sql, params, "", criteria);
		sql.append(" ORDER BY id ASC LIMIT :limit");
		return jdbcTemplate.query(sql.toString(), params, propertyRowMapper());
	}

	@Override
	public List<RegionAverageViewportItem> findRegionAverageViewportItems(
			PropertySearchCriteria criteria,
			String regionLevel,
			int limit
	) {
		Map<String, Object> params = new HashMap<>();
		params.put("west", criteria.west());
		params.put("east", criteria.east());
		params.put("south", criteria.south());
		params.put("north", criteria.north());
		params.put("regionLevel", regionLevel);
		params.put("limit", limit);

		String centerColumns;
		String centerGroupBy;
		String joinCondition;
		String regionNameExpression;
		if ("DONG".equals(regionLevel)) {
			centerColumns = "sido, sigungu, dong, legal_dong_code AS region_code";
			centerGroupBy = "sido, sigungu, dong, legal_dong_code";
			joinCondition = "rs.region_code = visible.region_code";
			regionNameExpression = "rs.dong";
		} else {
			centerColumns = "sido, sigungu, NULL AS dong, NULL AS region_code";
			centerGroupBy = "sido, sigungu";
			joinCondition = "rs.sido = visible.sido AND rs.sigungu = visible.sigungu";
			regionNameExpression = "rs.sigungu";
		}

		StringBuilder visibleSql = new StringBuilder("""
				SELECT %s,
				       AVG(latitude) AS latitude,
				       AVG(longitude) AS longitude
				FROM properties
				WHERE is_active = true
				  AND longitude BETWEEN :west AND :east
				  AND latitude BETWEEN :south AND :north
				""".formatted(centerColumns));
		appendPropertyFilters(visibleSql, params, "", criteria);
		visibleSql.append("\nGROUP BY ").append(centerGroupBy);

		StringBuilder sql = new StringBuilder("""
				WITH visible AS (
				    %s
				)
				SELECT rs.region_level,
				       rs.region_code,
				       %s AS region_name,
				       CAST(SUM(CASE WHEN rs.avg_deposit IS NOT NULL THEN rs.avg_deposit * rs.transaction_count ELSE 0 END)
				            / NULLIF(SUM(CASE WHEN rs.avg_deposit IS NOT NULL THEN rs.transaction_count ELSE 0 END), 0) AS BIGINT) AS avg_deposit,
				       CAST(SUM(CASE WHEN rs.avg_monthly_rent IS NOT NULL THEN rs.avg_monthly_rent * rs.transaction_count ELSE 0 END)
				            / NULLIF(SUM(CASE WHEN rs.avg_monthly_rent IS NOT NULL THEN rs.transaction_count ELSE 0 END), 0) AS BIGINT) AS avg_monthly_rent,
				       CAST(SUM(CASE WHEN rs.avg_price IS NOT NULL THEN rs.avg_price * rs.transaction_count ELSE 0 END)
				            / NULLIF(SUM(CASE WHEN rs.avg_price IS NOT NULL THEN rs.transaction_count ELSE 0 END), 0) AS BIGINT) AS avg_sale_price,
				       SUM(rs.transaction_count) AS transaction_count,
				       visible.latitude,
				       visible.longitude
				FROM region_price_stat rs
				JOIN visible ON %s
				WHERE rs.region_level = :regionLevel
				""".formatted(visibleSql, regionNameExpression, joinCondition));
		appendRegionStatFilters(sql, params, "rs", criteria);
		sql.append(" \nGROUP BY rs.region_level, rs.region_code, ")
				.append(regionNameExpression)
				.append(", visible.latitude, visible.longitude")
				.append(" \nORDER BY transaction_count DESC, region_name ASC")
				.append(" \nLIMIT :limit");
		return jdbcTemplate.query(sql.toString(), params, regionAverageMapper());
	}

	@Override
	public List<PropertyClusterViewportItem> findPropertyClusters(
			PropertySearchCriteria criteria,
			BigDecimal gridSize,
			int limit
	) {
		Map<String, Object> params = new HashMap<>();
		params.put("west", criteria.west());
		params.put("east", criteria.east());
		params.put("south", criteria.south());
		params.put("north", criteria.north());
		params.put("gridSize", gridSize);
		params.put("radiusM", gridSize.multiply(BigDecimal.valueOf(111_000)).divide(BigDecimal.valueOf(2)).intValue());
		params.put("limit", limit);

		StringBuilder bucketedSql = new StringBuilder("""
				SELECT CAST(FLOOR(latitude / :gridSize) AS BIGINT) AS lat_bucket,
				       CAST(FLOOR(longitude / :gridSize) AS BIGINT) AS lng_bucket,
				       latitude, longitude, deposit, monthly_rent, price
				FROM properties
				WHERE is_active = true
				  AND longitude BETWEEN :west AND :east
				  AND latitude BETWEEN :south AND :north
				""");
		appendPropertyFilters(bucketedSql, params, "", criteria);
		StringBuilder sql = new StringBuilder("""
				WITH bucketed AS (
				    %s
				)
				SELECT lat_bucket,
				       lng_bucket,
				       COUNT(*) AS property_count,
				       AVG(latitude) AS latitude,
				       AVG(longitude) AS longitude,
				       :radiusM AS radius_m,
				       AVG(deposit) AS avg_deposit,
				       AVG(monthly_rent) AS avg_monthly_rent,
				       AVG(price) AS avg_sale_price
				FROM bucketed
				""".formatted(bucketedSql));
		sql.append("""
				GROUP BY lat_bucket, lng_bucket
				ORDER BY property_count DESC, latitude ASC, longitude ASC
				LIMIT :limit
				""");
		return jdbcTemplate.query(sql.toString(), params, propertyClusterMapper());
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

	@Override
	public List<PropertyTransactionResponse> findComparableTransactions(PropertyRow property, String minContractYearMonth) {
		String sql = """
				SELECT transaction_type, contract_year_month, deposit, monthly_rent, price, area_m2, floor,
				       CASE WHEN building_key = :buildingKey THEN 0 ELSE 1 END AS match_rank
				FROM transaction_history
				WHERE contract_year_month >= :minContractYearMonth
				  AND transaction_type = :transactionType
				  AND property_type = :propertyType
				  AND (
				        building_key = :buildingKey
				        OR (
				             legal_dong_code = :legalDongCode
				             AND area_m2 BETWEEN :minAreaM2 AND :maxAreaM2
				        )
				  )
				ORDER BY match_rank ASC, contract_year_month DESC, contract_day DESC NULLS LAST, id DESC
				LIMIT 20
				""";
		BigDecimal areaM2 = property.areaM2();
		Map<String, Object> params = Map.of(
				"buildingKey", property.buildingKey(),
				"minContractYearMonth", minContractYearMonth,
				"transactionType", property.transactionType().name(),
				"propertyType", property.propertyType().name(),
				"legalDongCode", property.legalDongCode(),
				"minAreaM2", areaM2.subtract(BigDecimal.TEN),
				"maxAreaM2", areaM2.add(BigDecimal.TEN)
		);
		return jdbcTemplate.query(sql, params, propertyTransactionMapper());
	}

	@Override
	public Optional<PropertySafetySummaryResponse> findSafetySummary(Long propertyId, Integer radius) {
		String sql = """
				SELECT property_id, safety_score, price_score, cctv_count_300m, bell_count_300m,
				       light_count_300m, police_count_500m
				FROM property_score_stat
				WHERE property_id = :propertyId
				""";
		List<PropertySafetySummaryResponse> rows = jdbcTemplate.query(
				sql,
				Map.of("propertyId", propertyId),
				(rs, rowNum) -> new PropertySafetySummaryResponse(
						rs.getLong("property_id"),
						radius,
						nullableInteger(rs, "safety_score"),
						nullableInteger(rs, "price_score"),
						nullableInteger(rs, "cctv_count_300m"),
						nullableInteger(rs, "bell_count_300m"),
						nullableInteger(rs, "light_count_300m"),
						nullableInteger(rs, "police_count_500m")
				)
		);
		return rows.stream().findFirst();
	}

	@Override
	public List<RegionPriceStatResponse> findRegionPriceStats(
			String legalDongCode,
			PropertyType propertyType,
			TransactionType transactionType
	) {
		String sql = """
				SELECT region_level, region_code, sido, sigungu, dong, avg_deposit, median_deposit,
				       avg_monthly_rent, median_monthly_rent, avg_price, median_price,
				       transaction_count, sample_from_ym, sample_to_ym
				FROM region_price_stat
				WHERE region_code = :legalDongCode
				  AND property_type = :propertyType
				  AND transaction_type = :transactionType
				ORDER BY region_level, region_code
				""";
		Map<String, Object> params = Map.of(
				"legalDongCode", legalDongCode,
				"propertyType", propertyType.name(),
				"transactionType", transactionType.name()
		);
		return jdbcTemplate.query(sql, params, regionPriceStatMapper());
	}

	@Override
	public List<BuildingPriceStatResponse> findBuildingPriceStats(
			String legalDongCode,
			PropertyType propertyType,
			TransactionType transactionType
	) {
		String sql = """
				SELECT building_key, building_name, sido, sigungu, dong, avg_deposit, median_deposit,
				       avg_monthly_rent, median_monthly_rent, avg_price, median_price,
				       transaction_count, sample_from_ym, sample_to_ym
				FROM building_price_stat
				WHERE legal_dong_code = :legalDongCode
				  AND property_type = :propertyType
				  AND transaction_type = :transactionType
				ORDER BY transaction_count DESC, building_key ASC
				LIMIT 20
				""";
		Map<String, Object> params = Map.of(
				"legalDongCode", legalDongCode,
				"propertyType", propertyType.name(),
				"transactionType", transactionType.name()
		);
		return jdbcTemplate.query(sql, params, buildingPriceStatMapper());
	}

	private RowMapper<PropertyRow> propertyRowMapper() {
		return (rs, rowNum) -> mapPropertyRow(rs);
	}

	private RowMapper<RegionAverageViewportItem> regionAverageMapper() {
		return (rs, rowNum) -> new RegionAverageViewportItem(
				MapViewportItemType.REGION_AVG,
				rs.getString("region_level"),
				rs.getString("region_code"),
				rs.getString("region_name"),
				nullableLong(rs, "avg_deposit"),
				nullableLong(rs, "avg_monthly_rent"),
				nullableLong(rs, "avg_sale_price"),
				nullableInteger(rs, "transaction_count"),
				rs.getBigDecimal("latitude"),
				rs.getBigDecimal("longitude")
		);
	}

	private RowMapper<PropertyClusterViewportItem> propertyClusterMapper() {
		return (rs, rowNum) -> new PropertyClusterViewportItem(
				MapViewportItemType.CLUSTER,
				"cluster-" + rs.getLong("lat_bucket") + "-" + rs.getLong("lng_bucket"),
				rs.getInt("property_count"),
				rs.getBigDecimal("latitude"),
				rs.getBigDecimal("longitude"),
				rs.getInt("radius_m"),
				nullableAverageLong(rs, "avg_deposit"),
				nullableAverageLong(rs, "avg_monthly_rent"),
				nullableAverageLong(rs, "avg_sale_price")
		);
	}

	private RowMapper<PropertyTransactionResponse> propertyTransactionMapper() {
		return (rs, rowNum) -> new PropertyTransactionResponse(
				TransactionType.valueOf(rs.getString("transaction_type")),
				formatYearMonth(rs.getString("contract_year_month")),
				nullableLong(rs, "deposit"),
				nullableLong(rs, "monthly_rent"),
				nullableLong(rs, "price"),
				rs.getBigDecimal("area_m2"),
				nullableInteger(rs, "floor")
		);
	}

	private RowMapper<RegionPriceStatResponse> regionPriceStatMapper() {
		return (rs, rowNum) -> new RegionPriceStatResponse(
				rs.getString("region_level"),
				rs.getString("region_code"),
				rs.getString("sido"),
				rs.getString("sigungu"),
				rs.getString("dong"),
				nullableLong(rs, "avg_deposit"),
				nullableLong(rs, "median_deposit"),
				nullableLong(rs, "avg_monthly_rent"),
				nullableLong(rs, "median_monthly_rent"),
				nullableLong(rs, "avg_price"),
				nullableLong(rs, "median_price"),
				nullableInteger(rs, "transaction_count"),
				formatYearMonth(rs.getString("sample_from_ym")),
				formatYearMonth(rs.getString("sample_to_ym"))
		);
	}

	private RowMapper<BuildingPriceStatResponse> buildingPriceStatMapper() {
		return (rs, rowNum) -> new BuildingPriceStatResponse(
				rs.getString("building_key"),
				rs.getString("building_name"),
				rs.getString("sido"),
				rs.getString("sigungu"),
				rs.getString("dong"),
				nullableLong(rs, "avg_deposit"),
				nullableLong(rs, "median_deposit"),
				nullableLong(rs, "avg_monthly_rent"),
				nullableLong(rs, "median_monthly_rent"),
				nullableLong(rs, "avg_price"),
				nullableLong(rs, "median_price"),
				nullableInteger(rs, "transaction_count"),
				formatYearMonth(rs.getString("sample_from_ym")),
				formatYearMonth(rs.getString("sample_to_ym"))
		);
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

	private String formatYearMonth(String yearMonth) {
		if (yearMonth == null || yearMonth.length() != 6) {
			return yearMonth;
		}
		return yearMonth.substring(0, 4) + "-" + yearMonth.substring(4);
	}

	private void appendPropertyFilters(
			StringBuilder sql,
			Map<String, Object> params,
			String alias,
			PropertySearchCriteria criteria
	) {
		String prefix = alias == null || alias.isBlank() ? "" : alias + ".";
		if (criteria.transactionType() != null) {
			sql.append(" AND ").append(prefix).append("transaction_type = :transactionType");
			params.put("transactionType", criteria.transactionType().name());
		}
		if (criteria.propertyType() != null) {
			sql.append(" AND ").append(prefix).append("property_type = :propertyType");
			params.put("propertyType", criteria.propertyType().name());
		}
		if (criteria.minDeposit() != null) {
			sql.append(" AND ").append(prefix).append("deposit >= :minDeposit");
			params.put("minDeposit", criteria.minDeposit());
		}
		if (criteria.maxDeposit() != null) {
			sql.append(" AND ").append(prefix).append("deposit <= :maxDeposit");
			params.put("maxDeposit", criteria.maxDeposit());
		}
		if (criteria.minPrice() != null) {
			sql.append(" AND ").append(prefix).append("price >= :minPrice");
			params.put("minPrice", criteria.minPrice());
		}
		if (criteria.maxPrice() != null) {
			sql.append(" AND ").append(prefix).append("price <= :maxPrice");
			params.put("maxPrice", criteria.maxPrice());
		}
	}

	private void appendRegionStatFilters(
			StringBuilder sql,
			Map<String, Object> params,
			String alias,
			PropertySearchCriteria criteria
	) {
		String prefix = alias == null || alias.isBlank() ? "" : alias + ".";
		if (criteria.transactionType() != null) {
			sql.append(" AND ").append(prefix).append("transaction_type = :transactionType");
			params.put("transactionType", criteria.transactionType().name());
		}
		if (criteria.propertyType() != null) {
			sql.append(" AND ").append(prefix).append("property_type = :propertyType");
			params.put("propertyType", criteria.propertyType().name());
		}
	}

	private Long nullableAverageLong(ResultSet rs, String column) throws SQLException {
		BigDecimal value = rs.getBigDecimal(column);
		return value == null ? null : value.longValue();
	}
}
