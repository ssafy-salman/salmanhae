package com.ssafy.salmanhae.controller.chat;

import com.ssafy.salmanhae.common.response.ApiResponse;
import com.ssafy.salmanhae.model.dto.auth.User;
import com.ssafy.salmanhae.model.dto.chat.ChatRequest;
import com.ssafy.salmanhae.model.dto.chat.ChatResponse;
import com.ssafy.salmanhae.service.chat.ChatService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/chat")
@RequiredArgsConstructor
public class ChatController {

	private final ChatService chatService;

	@PostMapping
	public ApiResponse<ChatResponse> sendMessage(
			@AuthenticationPrincipal User user,
			@Valid @RequestBody ChatRequest request
	) {
		return ApiResponse.ok(chatService.sendMessage(user, request));
	}
}
