package com.ssafy.salmanhae.model.dto.chat;

public record LegalCardResponse(
		String lawName,
		String articleNo,
		String title,
		String content,
		Double score
) {
}
