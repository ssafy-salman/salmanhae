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
public class CctvOpenApiClient extends AbstractJsonSafetyFacilityOpenApiClient {

	static final String SOURCE = "CCTV_OPENAPI";
	private static final int MAX_PAGE_SIZE = 100;

	private final SafetyDataProperties properties;

	public CctvOpenApiClient(
			SafetyDataProperties properties,
			RestClient.Builder restClientBuilder,
			ObjectMapper objectMapper
	) {
		super(SOURCE, "CCTV", properties, restClientBuilder, objectMapper);
		this.properties = properties;
	}

	@Override
	public List<NormalizedSafetyFacility> fetchFacilities() {
		return fetchPagedJson(
				properties.cctvUrl(),
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
				"name", "facilityName", "fcltyNm", "시설명",
				"INSTL_PSTN", "CCTV_INSTL_PSTN", "INSTL_PLC", "INSTL_PRPS", "MNG_INST_NM"
		);
		if (name.isBlank()) {
			name = "CCTV";
		}
		String sourceId = SafetyFacilityParserSupport.text(
				node,
				"id", "sourceId", "source_id", "관리번호", "시설관리번호", "CCTV관리번호",
				"CCTV_MNG_NO", "MNG_NO"
		);
		if (sourceId.isBlank()) {
			sourceId = name + ":" + latitude + ":" + longitude;
		}
		String address = SafetyFacilityParserSupport.text(
				node,
				"address", "주소", "소재지도로명주소", "소재지지번주소", "rnAdres",
				"LCTN_ROAD_NM_ADDR", "LCTN_LOTNO_ADDR"
		);
		String description = SafetyFacilityParserSupport.text(
				node,
				"description", "설명", "용도", "비고",
				"INSTL_PRPS", "MNG_INST_NM", "CCTV_CNT", "CAMERA_CNT"
		);
		return new NormalizedSafetyFacility(
				SafetyFacilityType.CCTV,
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
