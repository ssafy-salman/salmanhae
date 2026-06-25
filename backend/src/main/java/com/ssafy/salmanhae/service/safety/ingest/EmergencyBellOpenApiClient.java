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
public class EmergencyBellOpenApiClient extends AbstractJsonSafetyFacilityOpenApiClient {

	static final String SOURCE = "EMERGENCY_BELL_OPENAPI";
	private static final int MAX_PAGE_SIZE = 100;

	private final SafetyDataProperties properties;

	public EmergencyBellOpenApiClient(
			SafetyDataProperties properties,
			RestClient.Builder restClientBuilder,
			ObjectMapper objectMapper
	) {
		super(SOURCE, "emergency bell", properties, restClientBuilder, objectMapper);
		this.properties = properties;
	}

	@Override
	public List<NormalizedSafetyFacility> fetchFacilities() {
		return fetchPagedJson(
				properties.emergencyBellUrl(),
				properties.publicServiceKey(),
				Math.min(properties.pageSize(), MAX_PAGE_SIZE)
		);
	}

	@Override
	NormalizedSafetyFacility toFacility(JsonNode node) {
		BigDecimal latitude = SafetyFacilityParserSupport.decimal(
				node,
				"latitude", "lat", "위도", "la", "WGS84_LAT"
		);
		BigDecimal longitude = SafetyFacilityParserSupport.decimal(
				node,
				"longitude", "lng", "lon", "경도", "lo", "WGS84_LOT"
		);
		String name = SafetyFacilityParserSupport.text(
				node,
				"name", "facilityName", "fcltyNm", "시설명", "bellName", "INSTL_PSTN", "INSTL_PLC_TYPE"
		);
		if (name.isBlank()) {
			name = "안전비상벨";
		}
		String sourceId = SafetyFacilityParserSupport.text(
				node,
				"id", "sourceId", "source_id", "objtId", "bellId", "관리번호", "SFTY_EMRGNCBLL_MNG_NO", "MNG_NO"
		);
		if (sourceId.isBlank()) {
			sourceId = name + ":" + latitude + ":" + longitude;
		}
		String address = SafetyFacilityParserSupport.text(
				node,
				"address", "adres", "addr", "주소", "rnAdres", "LCTN_ROAD_NM_ADDR", "LCTN_LOTNO_ADDR"
		);
		String description = SafetyFacilityParserSupport.text(
				node,
				"description", "설명", "remark", "비고", "INSTL_PRPS", "MNG_INST_NM", "LINK_MTH"
		);
		return new NormalizedSafetyFacility(
				SafetyFacilityType.EMERGENCY_BELL,
				name,
				address,
				latitude,
				longitude,
				SOURCE,
				sourceId,
				description
		);
	}
}
