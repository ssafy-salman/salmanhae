package com.ssafy.salmanhae.service.safety.ingest;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.within;

import java.nio.charset.StandardCharsets;
import java.util.List;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.core.io.ClassPathResource;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.web.client.RestClient;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.ssafy.salmanhae.config.SafetyDataProperties;
import com.ssafy.salmanhae.model.dto.safety.SafetyFacilityType;

class SafetyFacilitySourceClientParserTest {

	private CctvOpenApiClient cctvOpenApiClient;
	private EmergencyBellOpenApiClient emergencyBellOpenApiClient;
	private SecurityLightOpenApiClient securityLightOpenApiClient;
	private SafemapPoliceFacilityClient safemapPoliceFacilityClient;

	@BeforeEach
	void setUp() {
		SafetyDataProperties properties = new SafetyDataProperties();
		RestClient.Builder restClientBuilder = RestClient.builder();
		ObjectMapper objectMapper = new ObjectMapper();
		cctvOpenApiClient = new CctvOpenApiClient(properties, restClientBuilder, objectMapper);
		emergencyBellOpenApiClient = new EmergencyBellOpenApiClient(properties, restClientBuilder, objectMapper);
		securityLightOpenApiClient = new SecurityLightOpenApiClient(properties, restClientBuilder, objectMapper);
		safemapPoliceFacilityClient = new SafemapPoliceFacilityClient(properties, restClientBuilder);
	}

	@Test
	void cctvJsonParserNormalizesRowsAndSkipsInvalidCoordinates() throws Exception {
		List<NormalizedSafetyFacility> facilities = cctvOpenApiClient.parseFacilities(fixture("cctv.json"));

		assertThat(facilities).hasSize(1);
		NormalizedSafetyFacility facility = facilities.getFirst();
		assertThat(facility.type()).isEqualTo(SafetyFacilityType.CCTV);
		assertThat(facility.name()).isEqualTo("Test CCTV");
		assertThat(facility.source()).isEqualTo(CctvOpenApiClient.SOURCE);
		assertThat(facility.sourceId()).isEqualTo("cctv-1");
		assertThat(facility.address()).isEqualTo("Seoul CCTV road address");
		assertThat(facility.description()).isEqualTo("fixture cctv");
		assertThat(facility.latitude()).isEqualByComparingTo("37.4703210");
		assertThat(facility.longitude()).isEqualByComparingTo("126.9361110");
	}

	@Test
	void cctvClientUsesPublicDataServiceKeyAndCapsPageSizeAtApiLimit() {
		SafetyDataProperties properties = new SafetyDataProperties();
		ReflectionTestUtils.setField(properties, "publicServiceKey", "public-data-key");
		ReflectionTestUtils.setField(properties, "cctvUrl", "https://apis.data.go.kr/1741000/cctv_info/info");
		ReflectionTestUtils.setField(properties, "pageSize", 1000);
		CapturingCctvOpenApiClient client = new CapturingCctvOpenApiClient(
				properties,
				RestClient.builder(),
				new ObjectMapper()
		);

		client.fetchFacilities();

		assertThat(client.capturedBaseUrl).isEqualTo("https://apis.data.go.kr/1741000/cctv_info/info");
		assertThat(client.capturedServiceKey).isEqualTo("public-data-key");
		assertThat(client.capturedPageSize).isEqualTo(100);
	}

	@Test
	void emergencyBellJsonParserNormalizesRowsAndSkipsInvalidCoordinates() throws Exception {
		List<NormalizedSafetyFacility> facilities =
				emergencyBellOpenApiClient.parseFacilities(fixture("emergency_bell.json"));

		assertThat(facilities).hasSize(1);
		NormalizedSafetyFacility facility = facilities.getFirst();
		assertThat(facility.type()).isEqualTo(SafetyFacilityType.EMERGENCY_BELL);
		assertThat(facility.name()).isEqualTo("Test Emergency Bell");
		assertThat(facility.source()).isEqualTo(EmergencyBellOpenApiClient.SOURCE);
		assertThat(facility.sourceId()).isEqualTo("bell-1");
		assertThat(facility.address()).isEqualTo("Seoul bell road address");
		assertThat(facility.description()).isEqualTo("fixture bell");
		assertThat(facility.latitude()).isEqualByComparingTo("37.4705000");
		assertThat(facility.longitude()).isEqualByComparingTo("126.9363000");
	}

	@Test
	void emergencyBellClientCapsPageSizeAtApiLimit() {
		SafetyDataProperties properties = new SafetyDataProperties();
		ReflectionTestUtils.setField(properties, "publicServiceKey", "emergency-key");
		ReflectionTestUtils.setField(properties, "emergencyBellUrl", "https://apis.data.go.kr/example/info");
		ReflectionTestUtils.setField(properties, "pageSize", 1000);
		CapturingEmergencyBellOpenApiClient client = new CapturingEmergencyBellOpenApiClient(
				properties,
				RestClient.builder(),
				new ObjectMapper()
		);

		client.fetchFacilities();

		assertThat(client.capturedBaseUrl).isEqualTo("https://apis.data.go.kr/example/info");
		assertThat(client.capturedServiceKey).isEqualTo("emergency-key");
		assertThat(client.capturedPageSize).isEqualTo(100);
	}

	@Test
	void securityLightJsonParserNormalizesRowsAndSkipsInvalidCoordinates() throws Exception {
		List<NormalizedSafetyFacility> facilities =
				securityLightOpenApiClient.parseFacilities(fixture("security_light.json"));

		assertThat(facilities).hasSize(2);
		NormalizedSafetyFacility facility = facilities.getFirst();
		assertThat(facility.type()).isEqualTo(SafetyFacilityType.SECURITY_LIGHT);
		assertThat(facility.name()).isEqualTo("Test Security Light");
		assertThat(facility.source()).isEqualTo(SecurityLightOpenApiClient.SOURCE);
		assertThat(facility.sourceId()).isEqualTo("light-1");
		assertThat(facility.address()).isEqualTo("Seoul light address");
		assertThat(facility.description()).isEqualTo("508020");
		assertThat(facility.latitude().doubleValue()).isCloseTo(37.839708417620116, within(0.000001));
		assertThat(facility.longitude().doubleValue()).isCloseTo(126.93722623764315, within(0.000001));

		NormalizedSafetyFacility geomOnlyFacility = facilities.get(1);
		assertThat(geomOnlyFacility.name()).isEqualTo("Geom Only Security Light");
		assertThat(geomOnlyFacility.sourceId()).isEqualTo("light-geom");
		assertThat(geomOnlyFacility.address()).isEqualTo("Geom only light address");
		assertThat(geomOnlyFacility.latitude().doubleValue()).isCloseTo(37.839708417620116, within(0.000001));
		assertThat(geomOnlyFacility.longitude().doubleValue()).isCloseTo(126.93722623764315, within(0.000001));
	}

	@Test
	void securityLightClientUsesDedicatedServiceKey() {
		SafetyDataProperties properties = new SafetyDataProperties();
		ReflectionTestUtils.setField(properties, "publicServiceKey", "emergency-key");
		ReflectionTestUtils.setField(properties, "securityLightServiceKey", "security-light-key");
		ReflectionTestUtils.setField(properties, "securityLightUrl", "https://www.safetydata.go.kr/V2/api/DSSP-IF-00083");
		CapturingSecurityLightOpenApiClient client = new CapturingSecurityLightOpenApiClient(
				properties,
				RestClient.builder(),
				new ObjectMapper()
		);

		client.fetchFacilities();

		assertThat(client.capturedBaseUrl).isEqualTo("https://www.safetydata.go.kr/V2/api/DSSP-IF-00083");
		assertThat(client.capturedServiceKey).isEqualTo("security-light-key");
	}

	@Test
	void safemapPoliceXmlParserUsesIf0036SourceAndSkipsInvalidCoordinates() throws Exception {
		List<NormalizedSafetyFacility> facilities =
				safemapPoliceFacilityClient.parseFacilities(fixture("safemap_police.xml"));

		assertThat(facilities).hasSize(1);
		NormalizedSafetyFacility facility = facilities.getFirst();
		assertThat(facility.type()).isEqualTo(SafetyFacilityType.POLICE);
		assertThat(facility.name()).isEqualTo("Test Police Box");
		assertThat(facility.source()).isEqualTo(SafemapPoliceFacilityClient.SOURCE);
		assertThat(facility.sourceId()).isEqualTo("police-1");
		assertThat(facility.address()).isEqualTo("Seoul road police address");
	}

	private String fixture(String filename) throws Exception {
		return new ClassPathResource("fixtures/safety/" + filename)
				.getContentAsString(StandardCharsets.UTF_8);
	}

	private static class CapturingEmergencyBellOpenApiClient extends EmergencyBellOpenApiClient {

		private String capturedBaseUrl;
		private String capturedServiceKey;
		private int capturedPageSize;

		CapturingEmergencyBellOpenApiClient(
				SafetyDataProperties properties,
				RestClient.Builder restClientBuilder,
				ObjectMapper objectMapper
		) {
			super(properties, restClientBuilder, objectMapper);
		}

		@Override
		List<NormalizedSafetyFacility> fetchPagedJson(String baseUrl, String serviceKey, int requestedPageSize) {
			this.capturedBaseUrl = baseUrl;
			this.capturedServiceKey = serviceKey;
			this.capturedPageSize = requestedPageSize;
			return List.of();
		}
	}

	private static class CapturingCctvOpenApiClient extends CctvOpenApiClient {

		private String capturedBaseUrl;
		private String capturedServiceKey;
		private int capturedPageSize;

		CapturingCctvOpenApiClient(
				SafetyDataProperties properties,
				RestClient.Builder restClientBuilder,
				ObjectMapper objectMapper
		) {
			super(properties, restClientBuilder, objectMapper);
		}

		@Override
		List<NormalizedSafetyFacility> fetchPagedJson(String baseUrl, String serviceKey, int requestedPageSize) {
			this.capturedBaseUrl = baseUrl;
			this.capturedServiceKey = serviceKey;
			this.capturedPageSize = requestedPageSize;
			return List.of();
		}
	}

	private static class CapturingSecurityLightOpenApiClient extends SecurityLightOpenApiClient {

		private String capturedBaseUrl;
		private String capturedServiceKey;

		CapturingSecurityLightOpenApiClient(
				SafetyDataProperties properties,
				RestClient.Builder restClientBuilder,
				ObjectMapper objectMapper
		) {
			super(properties, restClientBuilder, objectMapper);
		}

		@Override
		List<NormalizedSafetyFacility> fetchPagedJson(String baseUrl, String serviceKey) {
			this.capturedBaseUrl = baseUrl;
			this.capturedServiceKey = serviceKey;
			return List.of();
		}
	}
}
