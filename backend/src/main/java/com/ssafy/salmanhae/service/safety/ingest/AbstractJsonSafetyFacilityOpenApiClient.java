package com.ssafy.salmanhae.service.safety.ingest;

import java.net.URI;
import java.util.ArrayList;
import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.client.RestClient;
import org.springframework.web.util.UriComponentsBuilder;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.ssafy.salmanhae.config.SafetyDataProperties;

abstract class AbstractJsonSafetyFacilityOpenApiClient implements SafetyFacilitySourceClient {

	private final Logger log = LoggerFactory.getLogger(getClass());

	private final String sourceName;
	private final String payloadName;
	private final SafetyDataProperties properties;
	private final RestClient restClient;
	private final ObjectMapper objectMapper;

	AbstractJsonSafetyFacilityOpenApiClient(
			String sourceName,
			String payloadName,
			SafetyDataProperties properties,
			RestClient.Builder restClientBuilder,
			ObjectMapper objectMapper
	) {
		this.sourceName = sourceName;
		this.payloadName = payloadName;
		this.properties = properties;
		this.restClient = SafetyFacilityHttpSupport.restClient(restClientBuilder);
		this.objectMapper = objectMapper;
	}

	@Override
	public String sourceName() {
		return sourceName;
	}

	List<NormalizedSafetyFacility> fetchPagedJson(String baseUrl, String serviceKey) {
		if (baseUrl == null || baseUrl.isBlank()) {
			return List.of();
		}
		List<NormalizedSafetyFacility> facilities = new ArrayList<>();
		int pageNo = 1;
		int totalCount = -1;
		while (totalCount < 0 || (pageNo - 1) * properties.pageSize() < totalCount) {
			URI uri = UriComponentsBuilder.fromUriString(baseUrl)
					.queryParam("serviceKey", serviceKey)
					.queryParam("pageNo", pageNo)
					.queryParam("numOfRows", properties.pageSize())
					.queryParam("type", "json")
					.queryParam("returnType", "json")
					.build()
					.encode()
					.toUri();
			String body;
			try {
				body = restClient.get().uri(uri).retrieve().body(String.class);
			} catch (RuntimeException exception) {
				log.warn("Failed to fetch {} safety facilities from {}", payloadName, baseUrl, exception);
				break;
			}
			if (body == null || body.isBlank()) {
				break;
			}
			ParsedSafetyFacilityPage page;
			try {
				page = parsePage(body);
			} catch (IllegalArgumentException exception) {
				log.warn("Failed to parse {} safety facilities from {}", payloadName, baseUrl, exception);
				break;
			}
			if (totalCount < 0) {
				totalCount = totalCount(body);
			}
			if (page.rawItemCount() == 0) {
				break;
			}
			facilities.addAll(page.facilities());
			if (page.rawItemCount() < properties.pageSize()) {
				break;
			}
			pageNo++;
		}
		return facilities;
	}

	public List<NormalizedSafetyFacility> parseFacilities(String json) {
		return parsePage(json).facilities();
	}

	private ParsedSafetyFacilityPage parsePage(String json) {
		try {
			return parsePage(objectMapper.readTree(json));
		} catch (Exception exception) {
			throw new IllegalArgumentException("Invalid " + payloadName + " JSON payload", exception);
		}
	}

	private ParsedSafetyFacilityPage parsePage(JsonNode root) {
		List<JsonNode> items = SafetyFacilityParserSupport.itemNodes(root);
		List<NormalizedSafetyFacility> facilities = items.stream()
				.map(this::toFacility)
				.filter(NormalizedSafetyFacility::hasUsableCoordinates)
				.toList();
		return new ParsedSafetyFacilityPage(facilities, items.size());
	}

	private int totalCount(String json) {
		try {
			return SafetyFacilityParserSupport.totalCount(objectMapper.readTree(json));
		} catch (Exception exception) {
			return -1;
		}
	}

	abstract NormalizedSafetyFacility toFacility(JsonNode node);
}
