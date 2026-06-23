package com.ssafy.salmanhae.model.dto.chat;

import java.util.List;
import java.util.Map;

public record ChatResponse(
		String intent,
		String message,
		String sessionId,
		List<Map<String, Object>> properties,
		List<LegalCardResponse> legalCards,
		List<AnalysisCardResponse> analysisCards
) {
	public ChatResponse {
		properties = properties == null ? List.of() : properties.stream()
				.map(Map::copyOf)
				.toList();
		legalCards = legalCards == null ? List.of() : List.copyOf(legalCards);
		analysisCards = analysisCards == null ? List.of() : List.copyOf(analysisCards);
	}
}
