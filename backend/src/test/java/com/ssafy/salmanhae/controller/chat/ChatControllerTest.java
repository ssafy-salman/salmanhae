package com.ssafy.salmanhae.controller.chat;

import static org.hamcrest.Matchers.hasSize;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.ssafy.salmanhae.model.dto.auth.User;
import com.ssafy.salmanhae.model.dto.chat.AnalysisCardResponse;
import com.ssafy.salmanhae.model.dto.chat.ChatRequest;
import com.ssafy.salmanhae.model.dto.chat.ChatResponse;
import com.ssafy.salmanhae.model.dto.chat.LegalCardResponse;
import com.ssafy.salmanhae.service.chat.ChatService;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.redis.core.ValueOperations;
import org.springframework.http.MediaType;
import org.springframework.mail.javamail.JavaMailSender;
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

	@MockitoBean
	private StringRedisTemplate redisTemplate;

	@MockitoBean
	private JavaMailSender mailSender;

	private ValueOperations<String, String> valueOps;

	@BeforeEach
	@SuppressWarnings("unchecked")
	void setUp() {
		valueOps = mock(ValueOperations.class);
		when(redisTemplate.opsForValue()).thenReturn(valueOps);
	}

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
						)),
						List.of()
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
				.andExpect(jsonPath("$.data.legalCards[0].articleNo").value("제3조의2"))
				.andExpect(jsonPath("$.data.legalCards[0].title").value("보증금의 회수"))
				.andExpect(jsonPath("$.data.legalCards[0].content").isNotEmpty())
				.andExpect(jsonPath("$.data.legalCards[0].score").value(0.92));
	}

	@Test
	void chatAcceptsSelectedPropertyAndReturnsAnalysisCards() throws Exception {
		when(chatService.sendMessage(any(User.class), any()))
				.thenReturn(new ChatResponse(
						"PRICE_ANALYSIS",
						"선택한 매물의 실거래가를 기준으로 시세를 분석했습니다.",
						null,
						List.of(),
						List.of(),
						List.of(new AnalysisCardResponse(
								"PRICE",
								"시세 분석",
								"주변 실거래가 대비 가격 적정성을 확인했습니다.",
								null,
								Map.of("selectedPropertyId", "1", "stub", true)
						))
				));

		mockMvc.perform(post("/api/v1/chat")
						.header("Authorization", "Bearer " + loginAccessToken())
						.contentType(MediaType.APPLICATION_JSON)
						.content("""
								{"message": "이 매물 가격이 비싼 편이야?", "sessionId": null, "selectedPropertyId": 1}
								"""))
				.andExpect(status().isOk())
				.andExpect(jsonPath("$.data.intent").value("PRICE_ANALYSIS"))
				.andExpect(jsonPath("$.data.analysisCards", hasSize(1)))
				.andExpect(jsonPath("$.data.analysisCards[0].type").value("PRICE"))
				.andExpect(jsonPath("$.data.analysisCards[0].title").value("시세 분석"))
				.andExpect(jsonPath("$.data.analysisCards[0].summary").isNotEmpty())
				.andExpect(jsonPath("$.data.analysisCards[0].metrics.selectedPropertyId").value("1"));

		ArgumentCaptor<ChatRequest> requestCaptor = ArgumentCaptor.forClass(ChatRequest.class);
		verify(chatService).sendMessage(any(User.class), requestCaptor.capture());
		assertEquals(1L, requestCaptor.getValue().selectedPropertyId());
	}

	@Test
	void chatReturnsSafetyAnalysisCardForAuthenticatedUser() throws Exception {
		when(chatService.sendMessage(any(User.class), any()))
				.thenReturn(new ChatResponse(
						"SAFETY_ANALYSIS",
						"선택한 매물 주변 안전 데이터를 확인했습니다.",
						null,
						List.of(),
						List.of(),
						List.of(new AnalysisCardResponse(
								"SAFETY",
								"안전 분석",
								"반경 500m 기준 안전 점수는 78점입니다.",
								78,
								Map.of(
										"selectedPropertyId", "1",
										"radius", 500,
										"safetyScore", 78,
										"cctvCount300m", 8,
										"bellCount300m", 0,
										"lightCount300m", 14,
										"policeCount500m", 1
								)
						))
				));

		mockMvc.perform(post("/api/v1/chat")
						.header("Authorization", "Bearer " + loginAccessToken())
						.contentType(MediaType.APPLICATION_JSON)
						.content("""
								{"message": "이 매물 주변 안전은 어때?", "sessionId": null, "selectedPropertyId": 1}
								"""))
				.andExpect(status().isOk())
				.andExpect(jsonPath("$.data.intent").value("SAFETY_ANALYSIS"))
				.andExpect(jsonPath("$.data.analysisCards", hasSize(1)))
				.andExpect(jsonPath("$.data.analysisCards[0].type").value("SAFETY"))
				.andExpect(jsonPath("$.data.analysisCards[0].title").value("안전 분석"))
				.andExpect(jsonPath("$.data.analysisCards[0].summary").isNotEmpty())
				.andExpect(jsonPath("$.data.analysisCards[0].score").value(78))
				.andExpect(jsonPath("$.data.analysisCards[0].metrics.selectedPropertyId").value("1"))
				.andExpect(jsonPath("$.data.analysisCards[0].metrics.radius").value(500))
				.andExpect(jsonPath("$.data.analysisCards[0].metrics.safetyScore").value(78))
				.andExpect(jsonPath("$.data.analysisCards[0].metrics.cctvCount300m").value(8))
				.andExpect(jsonPath("$.data.analysisCards[0].metrics.bellCount300m").value(0))
				.andExpect(jsonPath("$.data.analysisCards[0].metrics.lightCount300m").value(14))
				.andExpect(jsonPath("$.data.analysisCards[0].metrics.policeCount500m").value(1));

		ArgumentCaptor<ChatRequest> requestCaptor = ArgumentCaptor.forClass(ChatRequest.class);
		verify(chatService).sendMessage(any(User.class), requestCaptor.capture());
		assertEquals(1L, requestCaptor.getValue().selectedPropertyId());
	}

	private String loginAccessToken() throws Exception {
		String email = "chat-user@example.com";
		String password = "password123";
		when(valueOps.get("email:verified:" + email)).thenReturn("true");
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
		String accessToken = body.path("data").path("accessToken").asText();
		assertFalse(accessToken.isBlank(), "login response must include non-empty accessToken");
		return accessToken;
	}
}
