package com.ssafy.salmanhae.service.safety.ingest;

import java.time.Duration;

import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.web.client.RestClient;

final class SafetyFacilityHttpSupport {

	private static final Duration CONNECT_TIMEOUT = Duration.ofSeconds(5);
	private static final Duration READ_TIMEOUT = Duration.ofSeconds(20);

	private SafetyFacilityHttpSupport() {
	}

	static RestClient restClient(RestClient.Builder builder) {
		SimpleClientHttpRequestFactory requestFactory = new SimpleClientHttpRequestFactory();
		requestFactory.setConnectTimeout(CONNECT_TIMEOUT);
		requestFactory.setReadTimeout(READ_TIMEOUT);
		return builder.clone()
				.requestFactory(requestFactory)
				.build();
	}
}
