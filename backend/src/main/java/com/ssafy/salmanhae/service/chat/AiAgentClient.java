package com.ssafy.salmanhae.service.chat;

import com.ssafy.salmanhae.common.exception.ApiException;
import com.ssafy.salmanhae.common.exception.ErrorCode;
import com.ssafy.salmanhae.model.dto.chat.ChatRequest;
import com.ssafy.salmanhae.model.dto.chat.ChatResponse;
import com.ssafy.salmanhae.model.dto.chat.LegalCardResponse;
import java.time.Duration;
import java.util.List;
import java.util.Map;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;

@Component
public class AiAgentClient {

	private final RestClient restClient;
	private final String internalApiKey;

	public AiAgentClient(
			@Value("${ai.agent.base-url}") String baseUrl,
			@Value("${ai.agent.internal-api-key}") String internalApiKey,
			@Value("${ai.agent.connect-timeout-ms:2000}") long connectTimeoutMs,
			@Value("${ai.agent.read-timeout-ms:10000}") long readTimeoutMs
	) {
		SimpleClientHttpRequestFactory requestFactory = new SimpleClientHttpRequestFactory();
		requestFactory.setConnectTimeout(Duration.ofMillis(connectTimeoutMs));
		requestFactory.setReadTimeout(Duration.ofMillis(readTimeoutMs));
		this.restClient = RestClient.builder()
				.baseUrl(baseUrl)
				.requestFactory(requestFactory)
				.build();
		this.internalApiKey = internalApiKey;
	}

	public ChatResponse sendMessage(String userId, ChatRequest request) {
		AgentChatResponse response;
		try {
			response = restClient.post()
					.uri("/internal/agent/chat")
					.header("X-Internal-Api-Key", internalApiKey)
					.body(new AgentChatRequest(
							userId,
							request.sessionId(),
							request.message(),
							new ChatContext(null, List.of())
					))
					.retrieve()
					.body(AgentChatResponse.class);
		} catch (RestClientException exception) {
			throw new ApiException(ErrorCode.AI_SERVICE_UNAVAILABLE);
		}

		if (response == null) {
			throw new ApiException(ErrorCode.AI_SERVICE_UNAVAILABLE);
		}

		return new ChatResponse(
				response.intent(),
				response.answer(),
				request.sessionId(),
				response.properties(),
				response.legalCards()
		);
	}

	private record AgentChatRequest(
			String userId,
			String sessionId,
			String message,
			ChatContext context
	) {
	}

	private record ChatContext(
			String selectedPropertyId,
			List<Map<String, String>> recentMessages
	) {
	}

	private record AgentChatResponse(
			String intent,
			String answer,
			List<Map<String, Object>> properties,
			List<LegalCardResponse> legalCards
	) {
	}
}
