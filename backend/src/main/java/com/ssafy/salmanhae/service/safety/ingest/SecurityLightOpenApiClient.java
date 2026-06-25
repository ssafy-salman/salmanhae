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
		BigDecimal latitude = SafetyFacilityParserSupport.decimal(node, "latitude", "lat", "위도", "la");
		BigDecimal longitude = SafetyFacilityParserSupport.decimal(node, "longitude", "lng", "lon", "경도", "lo");
		String name = SafetyFacilityParserSupport.text(node, "name", "facilityName", "fcltyNm", "시설명", "lightName");
		if (name.isBlank()) {
			name = "보안등";
		}
		String sourceId = SafetyFacilityParserSupport.text(
				node, "id", "sourceId", "source_id", "lightId", "관리번호"
		);
		if (sourceId.isBlank()) {
			sourceId = name + ":" + latitude + ":" + longitude;
		}
		return new NormalizedSafetyFacility(
				SafetyFacilityType.SECURITY_LIGHT,
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
