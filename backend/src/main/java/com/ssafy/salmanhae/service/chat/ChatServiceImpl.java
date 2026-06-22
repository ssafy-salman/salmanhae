package com.ssafy.salmanhae.service.chat;

import com.ssafy.salmanhae.model.dto.auth.User;
import com.ssafy.salmanhae.model.dto.chat.ChatRequest;
import com.ssafy.salmanhae.model.dto.chat.ChatResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class ChatServiceImpl implements ChatService {

	private final AiAgentClient aiAgentClient;

	@Override
	public ChatResponse sendMessage(User user, ChatRequest request) {
		return aiAgentClient.sendMessage(user.getId(), request);
	}
}
