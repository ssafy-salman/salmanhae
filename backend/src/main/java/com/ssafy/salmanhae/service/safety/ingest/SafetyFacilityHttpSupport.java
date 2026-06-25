package com.ssafy.salmanhae.service.safety.ingest;

import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.time.Duration;

import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.web.client.RestClient;

final class SafetyFacilityHttpSupport {

	private static final Duration CONNECT_TIMEOUT = Duration.ofSeconds(5);
	private static final Duration READ_TIMEOUT = Duration.ofSeconds(20);
	static final int MAX_PAGES = 1000;

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

	static String encodedQueryParam(String value) {
		return URLEncoder.encode(value == null ? "" : value, StandardCharsets.UTF_8);
	}

	static int cappedMaxPages(int maxPages) {
		return Math.min(maxPages, MAX_PAGES);
	}
}
