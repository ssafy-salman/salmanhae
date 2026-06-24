package com.ssafy.salmanhae.service.safety.ingest;

import java.math.BigDecimal;
import java.net.URI;
import java.util.ArrayList;
import java.util.List;

import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;
import org.springframework.web.util.UriComponentsBuilder;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.ssafy.salmanhae.config.SafetyDataProperties;
import com.ssafy.salmanhae.model.dto.safety.SafetyFacilityType;

@Component
public class EmergencyBellOpenApiClient implements SafetyFacilitySourceClient {

	static final String SOURCE = "EMERGENCY_BELL_OPENAPI";

	private final SafetyDataProperties properties;
	private final RestClient restClient;
	private final ObjectMapper objectMapper;

	public EmergencyBellOpenApiClient(
			SafetyDataProperties properties,
			RestClient.Builder restClientBuilder,
			ObjectMapper objectMapper
	) {
		this.properties = properties;
		this.restClient = restClientBuilder.build();
		this.objectMapper = objectMapper;
	}

	@Override
	public String sourceName() {
		return SOURCE;
	}

	@Override
	public List<NormalizedSafetyFacility> fetchFacilities() {
		return fetchPagedJson(properties.emergencyBellUrl(), properties.publicServiceKey());
	}

	public List<NormalizedSafetyFacility> parseFacilities(String json) {
		try {
			JsonNode root = objectMapper.readTree(json);
			return parseFacilities(root);
		} catch (Exception exception) {
			throw new IllegalArgumentException("Invalid emergency bell JSON payload", exception);
		}
	}

	private List<NormalizedSafetyFacility> fetchPagedJson(String baseUrl, String serviceKey) {
		if (baseUrl == null || baseUrl.isBlank()) {
			return List.of();
		}
		List<NormalizedSafetyFacility> facilities = new ArrayList<>();
		int pageNo = 1;
		int totalCount = -1;
		while (totalCount < 0 || facilities.size() < totalCount) {
			URI uri = UriComponentsBuilder.fromUriString(baseUrl)
					.queryParam("serviceKey", serviceKey)
					.queryParam("pageNo", pageNo)
					.queryParam("numOfRows", properties.pageSize())
					.queryParam("type", "json")
					.queryParam("returnType", "json")
					.build(true)
					.toUri();
			String body = restClient.get().uri(uri).retrieve().body(String.class);
			try {
				JsonNode root = objectMapper.readTree(body);
				if (totalCount < 0) {
					totalCount = SafetyFacilityParserSupport.totalCount(root);
				}
				List<NormalizedSafetyFacility> page = parseFacilities(root);
				if (page.isEmpty()) {
					break;
				}
				facilities.addAll(page);
			} catch (Exception exception) {
				throw new IllegalArgumentException("Invalid emergency bell JSON payload", exception);
			}
			pageNo++;
		}
		return facilities;
	}

	private List<NormalizedSafetyFacility> parseFacilities(JsonNode root) {
		return SafetyFacilityParserSupport.itemNodes(root).stream()
				.map(this::toFacility)
				.filter(NormalizedSafetyFacility::hasUsableCoordinates)
				.toList();
	}

	private NormalizedSafetyFacility toFacility(JsonNode node) {
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
