package com.ssafy.salmanhae.service.safety.ingest;

import java.math.BigDecimal;
import java.util.List;

import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.ssafy.salmanhae.config.SafetyDataProperties;
import com.ssafy.salmanhae.model.dto.safety.SafetyFacilityType;

@Component
public class SecurityLightOpenApiClient extends AbstractJsonSafetyFacilityOpenApiClient {

	static final String SOURCE = "SECURITY_LIGHT_OPENAPI";
	private static final double WEB_MERCATOR_RADIUS = 6378137.0;

	private final SafetyDataProperties properties;

	public SecurityLightOpenApiClient(
			SafetyDataProperties properties,
			RestClient.Builder restClientBuilder,
			ObjectMapper objectMapper
	) {
		super(SOURCE, "security light", properties, restClientBuilder, objectMapper);
		this.properties = properties;
	}

	@Override
	public List<NormalizedSafetyFacility> fetchFacilities() {
		return fetchPagedJson(properties.securityLightUrl(), properties.securityLightServiceKey());
	}

	@Override
	NormalizedSafetyFacility toFacility(JsonNode node) {
		BigDecimal latitude = SafetyFacilityParserSupport.decimal(node, "latitude", "lat", "위도", "la", "WGS84_LAT");
		BigDecimal longitude = SafetyFacilityParserSupport.decimal(node, "longitude", "lng", "lon", "경도", "lo", "WGS84_LOT");
		if (!SafetyFacilityParserSupport.isUsableCoordinate(latitude, longitude)) {
			BigDecimal x = SafetyFacilityParserSupport.decimal(node, "XMAP_CRTS");
			BigDecimal y = SafetyFacilityParserSupport.decimal(node, "YMAP_CRTS");
			if (x == null || y == null) {
				BigDecimal[] point = webMercatorPoint(node);
				x = point[0];
				y = point[1];
			}
			BigDecimal[] wgs84 = toWgs84(x, y);
			latitude = wgs84[0];
			longitude = wgs84[1];
		}
		String name = SafetyFacilityParserSupport.text(
				node,
				"name", "facilityName", "fcltyNm", "시설명", "lightName", "FCLT_GVMNFC_NM", "FCLT_TYPE"
		);
		if (name.isBlank()) {
			name = "보안등";
		}
		String sourceId = SafetyFacilityParserSupport.text(
				node, "id", "sourceId", "source_id", "lightId", "관리번호", "SN"
		);
		if (sourceId.isBlank()) {
			sourceId = name + ":" + latitude + ":" + longitude;
		}
		String address = SafetyFacilityParserSupport.text(
				node, "address", "adres", "addr", "주소", "rnAdres", "ADDR", "ROAD_NM_ADDR"
		);
		String description = SafetyFacilityParserSupport.text(
				node, "description", "설명", "remark", "비고", "FCLT_CD", "FCLT_TYPE", "FCLT_GVMNFC_NM"
		);
		return new NormalizedSafetyFacility(
				SafetyFacilityType.SECURITY_LIGHT,
				name,
				address,
				latitude,
				longitude,
				SOURCE,
				sourceId,
				description
		);
	}

	private BigDecimal[] webMercatorPoint(JsonNode node) {
		String geom = SafetyFacilityParserSupport.text(node, "GEOM");
		if (geom.isBlank()) {
			return new BigDecimal[] { null, null };
		}
		int start = geom.indexOf('(');
		int end = geom.indexOf(')');
		if (start < 0 || end <= start) {
			return new BigDecimal[] { null, null };
		}
		String[] parts = geom.substring(start + 1, end).trim().split("\\s+");
		if (parts.length < 2) {
			return new BigDecimal[] { null, null };
		}
		return new BigDecimal[] {
				SafetyFacilityParserSupport.decimal(parts[0]),
				SafetyFacilityParserSupport.decimal(parts[1])
		};
	}

	private BigDecimal[] toWgs84(BigDecimal x, BigDecimal y) {
		if (x == null || y == null) {
			return new BigDecimal[] { null, null };
		}
		double longitude = Math.toDegrees(x.doubleValue() / WEB_MERCATOR_RADIUS);
		double latitude = Math.toDegrees(
				2 * Math.atan(Math.exp(y.doubleValue() / WEB_MERCATOR_RADIUS)) - Math.PI / 2
		);
		return new BigDecimal[] {
				BigDecimal.valueOf(latitude),
				BigDecimal.valueOf(longitude)
		};
	}
}
