package com.ssafy.salmanhae.model.dto.chat;

import java.util.Map;

public record AnalysisCardResponse(
		String type,
		String title,
		String summary,
		Integer score,
		Map<String, Object> metrics
) {
	public AnalysisCardResponse {
		metrics = metrics == null ? Map.of() : Map.copyOf(metrics);
	}
}
