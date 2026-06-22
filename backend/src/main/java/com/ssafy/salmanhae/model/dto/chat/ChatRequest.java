package com.ssafy.salmanhae.model.dto.chat;

import jakarta.validation.constraints.NotBlank;

public record ChatRequest(
		@NotBlank String message,
		String sessionId
) {
}
