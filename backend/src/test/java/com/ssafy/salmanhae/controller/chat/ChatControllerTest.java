package com.ssafy.salmanhae.controller.chat;

import static org.hamcrest.Matchers.hasSize;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.ssafy.salmanhae.model.dto.auth.User;
import com.ssafy.salmanhae.model.dto.chat.ChatResponse;
import com.ssafy.salmanhae.model.dto.chat.LegalCardResponse;
import com.ssafy.salmanhae.service.chat.ChatService;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;
import org.springframework.transaction.annotation.Transactional;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
@Transactional
class ChatControllerTest {

	@Autowired
	private MockMvc mockMvc;

	@Autowired
	private ObjectMapper objectMapper;

	@MockitoBean
	private ChatService chatService;

	@Test
	void chatRequiresAuthentication() throws Exception {
		mockMvc.perform(post("/api/v1/chat")
						.contentType(MediaType.APPLICATION_JSON)
						.content("""
								{"message": "확정일자는 언제 받아야 하나요?", "sessionId": null}
								"""))
				.andExpect(status().isUnauthorized());
	}

	@Test
	void chatReturnsLegalConsultContractForAuthenticatedUser() throws Exception {
		when(chatService.sendMessage(any(User.class), any()))
				.thenReturn(new ChatResponse(
						"LEGAL_CONSULT",
						"확정일자는 보증금 우선변제를 위해 전입신고와 함께 빠르게 받는 것이 좋습니다.",
						null,
						List.of(),
						List.of(new LegalCardResponse(
								"주택임대차보호법",
								"제3조의2",
								"보증금의 회수",
								"확정일자를 갖춘 임차인은 경매 또는 공매 시 후순위권리자보다 우선하여 보증금을 변제받을 수 있습니다.",
								0.92
						))
				));

		mockMvc.perform(post("/api/v1/chat")
						.header("Authorization", "Bearer " + loginAccessToken())
						.contentType(MediaType.APPLICATION_JSON)
						.content("""
								{"message": "확정일자는 언제 받아야 하나요?", "sessionId": null}
								"""))
				.andExpect(status().isOk())
				.andExpect(jsonPath("$.message").value("OK"))
				.andExpect(jsonPath("$.data.intent").value("LEGAL_CONSULT"))
				.andExpect(jsonPath("$.data.message").isNotEmpty())
				.andExpect(jsonPath("$.data.properties", hasSize(0)))
				.andExpect(jsonPath("$.data.legalCards", hasSize(1)))
				.andExpect(jsonPath("$.data.legalCards[0].lawName").value("주택임대차보호법"))
				.andExpect(jsonPath("$.data.legalCards[0].articleNo").value("제3조의2"));
	}

	private String loginAccessToken() throws Exception {
		String email = "chat-user@example.com";
		String password = "password123";
		mockMvc.perform(post("/api/v1/auth/signup")
						.contentType(MediaType.APPLICATION_JSON)
						.content("""
								{"email": "%s", "password": "%s", "nickname": "챗테스터"}
								""".formatted(email, password)))
				.andExpect(status().isOk());

		MvcResult result = mockMvc.perform(post("/api/v1/auth/login")
						.contentType(MediaType.APPLICATION_JSON)
						.content("""
								{"email": "%s", "password": "%s"}
								""".formatted(email, password)))
				.andExpect(status().isOk())
				.andReturn();

		JsonNode body = objectMapper.readTree(result.getResponse().getContentAsString());
		return body.path("data").path("accessToken").asText();
	}
}
