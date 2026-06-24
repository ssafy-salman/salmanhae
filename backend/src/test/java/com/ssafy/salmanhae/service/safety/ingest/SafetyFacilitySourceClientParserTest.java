package com.ssafy.salmanhae.service.safety.ingest;

import static org.assertj.core.api.Assertions.assertThat;

import java.nio.charset.StandardCharsets;
import java.util.List;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.core.io.ClassPathResource;
import org.springframework.test.context.ActiveProfiles;

import com.ssafy.salmanhae.model.dto.safety.SafetyFacilityType;

@SpringBootTest
@ActiveProfiles("test")
class SafetyFacilitySourceClientParserTest {

	@Autowired
	private CctvCsvClient cctvCsvClient;

	@Autowired
	private EmergencyBellOpenApiClient emergencyBellOpenApiClient;

	@Autowired
	private SecurityLightOpenApiClient securityLightOpenApiClient;

	@Autowired
	private SafemapPoliceFacilityClient safemapPoliceFacilityClient;

	@Test
	void cctvCsvParserNormalizesRowsAndSkipsInvalidCoordinates() throws Exception {
		List<NormalizedSafetyFacility> facilities = cctvCsvClient.parseFacilities(fixture("cctv.csv"));

		assertThat(facilities).hasSize(1);
		NormalizedSafetyFacility facility = facilities.getFirst();
		assertThat(facility.type()).isEqualTo(SafetyFacilityType.CCTV);
		assertThat(facility.name()).isEqualTo("Test CCTV");
		assertThat(facility.source()).isEqualTo(CctvCsvClient.SOURCE);
		assertThat(facility.sourceId()).isEqualTo("cctv-1");
		assertThat(facility.latitude()).isEqualByComparingTo("37.4703210");
		assertThat(facility.longitude()).isEqualByComparingTo("126.9361110");
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
	}

	@Test
	void securityLightJsonParserNormalizesRowsAndSkipsInvalidCoordinates() throws Exception {
		List<NormalizedSafetyFacility> facilities =
				securityLightOpenApiClient.parseFacilities(fixture("security_light.json"));

		assertThat(facilities).hasSize(1);
		NormalizedSafetyFacility facility = facilities.getFirst();
		assertThat(facility.type()).isEqualTo(SafetyFacilityType.SECURITY_LIGHT);
		assertThat(facility.name()).isEqualTo("Test Security Light");
		assertThat(facility.source()).isEqualTo(SecurityLightOpenApiClient.SOURCE);
		assertThat(facility.sourceId()).isEqualTo("light-1");
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
}
