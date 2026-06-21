package com.ssafy.salmanhae.controller.auth;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.Map;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.test.context.ActiveProfiles;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@ActiveProfiles("test")
class AuthHttpIntegrationTest {

	@Autowired
	private TestRestTemplate restTemplate;

	@Test
	void signupLoginFlow() {
		HttpHeaders headers = new HttpHeaders();
		headers.setContentType(MediaType.APPLICATION_JSON);

		// 회원가입
		ResponseEntity<Map> signupResponse = restTemplate.postForEntity(
				"/api/v1/auth/signup",
				new HttpEntity<>("""
						{"email": "flow@example.com", "password": "password123", "nickname": "플로우"}
						""", headers),
				Map.class
		);
		assertThat(signupResponse.getStatusCode()).isEqualTo(HttpStatus.OK);
		assertThat(signupResponse.getBody()).containsEntry("message", "OK");

		// 로그인 → 토큰 발급 확인
		ResponseEntity<Map> loginResponse = restTemplate.postForEntity(
				"/api/v1/auth/login",
				new HttpEntity<>("""
						{"email": "flow@example.com", "password": "password123"}
						""", headers),
				Map.class
		);
		assertThat(loginResponse.getStatusCode()).isEqualTo(HttpStatus.OK);

		Map<String, Object> data = (Map<String, Object>) loginResponse.getBody().get("data");
		assertThat((String) data.get("accessToken")).isNotBlank();
		assertThat((String) data.get("refreshToken")).isNotBlank();
	}

	@Test
	void loginWithWrongPasswordReturns401() {
		HttpHeaders headers = new HttpHeaders();
		headers.setContentType(MediaType.APPLICATION_JSON);

		ResponseEntity<Map> response = restTemplate.postForEntity(
				"/api/v1/auth/login",
				new HttpEntity<>("""
						{"email": "nobody@example.com", "password": "wrong"}
						""", headers),
				Map.class
		);
		assertThat(response.getStatusCode()).isEqualTo(HttpStatus.UNAUTHORIZED);
		assertThat(response.getBody()).containsEntry("code", "UNAUTHORIZED");
	}
}
