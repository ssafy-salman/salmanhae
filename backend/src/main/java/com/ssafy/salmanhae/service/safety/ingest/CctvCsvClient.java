package com.ssafy.salmanhae.service.safety.ingest;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import com.ssafy.salmanhae.config.SafetyDataProperties;
import com.ssafy.salmanhae.model.dto.safety.SafetyFacilityType;

@Component
public class CctvCsvClient implements SafetyFacilitySourceClient {

	static final String SOURCE = "CCTV_CSV";

	private final SafetyDataProperties properties;
	private final RestClient restClient;

	public CctvCsvClient(SafetyDataProperties properties, RestClient.Builder restClientBuilder) {
		this.properties = properties;
		this.restClient = restClientBuilder.build();
	}

	@Override
	public String sourceName() {
		return SOURCE;
	}

	@Override
	public List<NormalizedSafetyFacility> fetchFacilities() {
		String body = restClient.get()
				.uri(properties.cctvUrl())
				.retrieve()
				.body(String.class);
		return parseFacilities(body);
	}

	public List<NormalizedSafetyFacility> parseFacilities(String csv) {
		return SafetyFacilityParserSupport.parseCsv(csv).stream()
				.map(this::toFacility)
				.filter(NormalizedSafetyFacility::hasUsableCoordinates)
				.toList();
	}

	private NormalizedSafetyFacility toFacility(Map<String, String> row) {
		BigDecimal latitude = SafetyFacilityParserSupport.decimal(SafetyFacilityParserSupport.value(
				row, "latitude", "lat", "위도", "WGS84위도"
		));
		BigDecimal longitude = SafetyFacilityParserSupport.decimal(SafetyFacilityParserSupport.value(
				row, "longitude", "lng", "lon", "경도", "WGS84경도"
		));
		String sourceId = SafetyFacilityParserSupport.value(
				row, "id", "source_id", "관리번호", "시설관리번호", "CCTV관리번호"
		);
		String name = SafetyFacilityParserSupport.value(row, "name", "시설명", "설치목적", "관리기관명");
		if (name.isBlank()) {
			name = "CCTV";
		}
		if (sourceId.isBlank()) {
			sourceId = name + ":" + latitude + ":" + longitude;
		}
		return new NormalizedSafetyFacility(
				SafetyFacilityType.CCTV,
				name,
				SafetyFacilityParserSupport.value(row, "address", "주소", "소재지도로명주소", "소재지지번주소"),
				latitude,
				longitude,
				SOURCE,
				sourceId,
				SafetyFacilityParserSupport.value(row, "description", "설명", "용도")
		);
	}
}
