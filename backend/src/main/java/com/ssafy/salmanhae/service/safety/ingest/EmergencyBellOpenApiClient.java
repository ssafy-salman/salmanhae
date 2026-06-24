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
		return fetchPagedJson(properties.emergencyBellUrl(), properties.publicServiceKey());
	}

	@Override
	NormalizedSafetyFacility toFacility(JsonNode node) {
		BigDecimal latitude = SafetyFacilityParserSupport.decimal(node, "latitude", "lat", "위도", "la");
		BigDecimal longitude = SafetyFacilityParserSupport.decimal(node, "longitude", "lng", "lon", "경도", "lo");
		String name = SafetyFacilityParserSupport.text(node, "name", "facilityName", "fcltyNm", "시설명", "bellName");
		if (name.isBlank()) {
			name = "안전비상벨";
		}
		String sourceId = SafetyFacilityParserSupport.text(
				node, "id", "sourceId", "source_id", "objtId", "bellId", "관리번호"
		);
		if (sourceId.isBlank()) {
			sourceId = name + ":" + latitude + ":" + longitude;
		}
		return new NormalizedSafetyFacility(
				SafetyFacilityType.EMERGENCY_BELL,
				name,
				SafetyFacilityParserSupport.text(node, "address", "adres", "addr", "주소", "rnAdres"),
				latitude,
				longitude,
				SOURCE,
				sourceId,
				SafetyFacilityParserSupport.text(node, "description", "설명", "remark", "비고")
		);
	}
}
