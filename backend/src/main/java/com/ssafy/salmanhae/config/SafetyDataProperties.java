package com.ssafy.salmanhae.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

@Component
public class SafetyDataProperties {

	private static final String DEFAULT_CCTV_URL = "https://apis.data.go.kr/1741000/cctv_info/info";
	private static final String DEFAULT_SAFEMAP_POLICE_URL = "https://www.safemap.go.kr/openapi2/IF_0036";
	private static final int DEFAULT_PAGE_SIZE = 1000;

	@Value("${safety.data.public-service-key:}")
	private String publicServiceKey;

	@Value("${safety.data.safemap-service-key:}")
	private String safemapServiceKey;

	@Value("${safety.data.security-light-service-key:}")
	private String securityLightServiceKey;

	@Value("${safety.data.cctv-url:}")
	private String cctvUrl;

	@Value("${safety.data.emergency-bell-url:}")
	private String emergencyBellUrl;

	@Value("${safety.data.security-light-url:}")
	private String securityLightUrl;

	@Value("${safety.data.safemap-police-url:}")
	private String safemapPoliceUrl;

	@Value("${safety.data.page-size:1000}")
	private Integer pageSize;

	public String publicServiceKey() {
		return firstNonBlank(publicServiceKey, System.getenv("PUBLIC_DATA_SERVICE_KEY"));
	}

	public String safemapServiceKey() {
		return firstNonBlank(safemapServiceKey, System.getenv("SAFEMAP_SERVICE_KEY"));
	}

	public String securityLightServiceKey() {
		return firstNonBlank(securityLightServiceKey, System.getenv("SECURITY_LIGHT_SERVICE_KEY"));
	}

	public String cctvUrl() {
		return defaultIfBlank(cctvUrl, DEFAULT_CCTV_URL);
	}

	public String emergencyBellUrl() {
		return blankToEmpty(emergencyBellUrl);
	}

	public String securityLightUrl() {
		return blankToEmpty(securityLightUrl);
	}

	public String safemapPoliceUrl() {
		return defaultIfBlank(safemapPoliceUrl, DEFAULT_SAFEMAP_POLICE_URL);
	}

	public int pageSize() {
		return pageSize == null || pageSize < 1 ? DEFAULT_PAGE_SIZE : pageSize;
	}

	private String defaultIfBlank(String value, String fallback) {
		String normalized = blankToEmpty(value);
		return normalized.isBlank() ? fallback : normalized;
	}

	private String firstNonBlank(String primary, String fallback) {
		String normalized = blankToEmpty(primary);
		return normalized.isBlank() ? blankToEmpty(fallback) : normalized;
	}

	private String blankToEmpty(String value) {
		return value == null ? "" : value.trim();
	}
}
