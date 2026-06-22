package com.ssafy.salmanhae.service.chat;

import com.ssafy.salmanhae.model.dto.auth.User;
import com.ssafy.salmanhae.model.dto.chat.ChatRequest;
import com.ssafy.salmanhae.model.dto.chat.ChatResponse;

public interface ChatService {
	ChatResponse sendMessage(User user, ChatRequest request);
}
