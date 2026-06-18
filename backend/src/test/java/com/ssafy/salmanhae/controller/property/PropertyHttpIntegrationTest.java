package com.ssafy.salmanhae.controller.property;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.Map;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.test.context.ActiveProfiles;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@ActiveProfiles("test")
class PropertyHttpIntegrationTest {

	@Autowired
	private TestRestTemplate restTemplate;

	@Test
	void propertyEndpointsRespondOverHttp() {
		ResponseEntity<Map> listResponse = restTemplate.getForEntity(
				"/api/v1/properties?west=126.93&east=126.94&south=37.46&north=37.48",
				Map.class
		);

		assertThat(listResponse.getStatusCode()).isEqualTo(HttpStatus.OK);
		assertThat(listResponse.getBody()).containsEntry("message", "OK");

		ResponseEntity<Map> detailResponse = restTemplate.getForEntity(
				"/api/v1/properties/1",
				Map.class
		);

		assertThat(detailResponse.getStatusCode()).isEqualTo(HttpStatus.OK);
		assertThat(detailResponse.getBody()).containsEntry("message", "OK");

		ResponseEntity<Map> notFoundResponse = restTemplate.getForEntity(
				"/api/v1/properties/9999",
				Map.class
		);

		assertThat(notFoundResponse.getStatusCode()).isEqualTo(HttpStatus.NOT_FOUND);
		assertThat(notFoundResponse.getBody()).containsEntry("code", "PROPERTY_NOT_FOUND");
	}
}
