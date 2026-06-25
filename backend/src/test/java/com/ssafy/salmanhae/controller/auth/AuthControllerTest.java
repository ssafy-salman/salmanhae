package com.ssafy.salmanhae.controller.auth;

import static org.hamcrest.Matchers.nullValue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.redis.core.ValueOperations;
import org.springframework.http.MediaType;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;
import org.springframework.transaction.annotation.Transactional;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
@Transactional
class AuthControllerTest {

	@Autowired
	private MockMvc mockMvc;

	@Autowired
	private ObjectMapper objectMapper;

	@MockBean
	private StringRedisTemplate redisTemplate;

	@MockBean
	private JavaMailSender mailSender;

	private ValueOperations<String, String> valueOps;

	private static final String EMAIL = "test@example.com";
	private static final String PASSWORD = "password123";
	private static final String NICKNAME = "테스터";

	@BeforeEach
	@SuppressWarnings("unchecked")
	void setUp() {
		valueOps = mock(ValueOperations.class);
		when(redisTemplate.opsForValue()).thenReturn(valueOps);
	}

	private void setEmailVerified(String email) {
		when(valueOps.get("email:verified:" + email)).thenReturn("true");
	}

	@Test
	void signupReturnsOk() throws Exception {
		setEmailVerified(EMAIL);

		mockMvc.perform(post("/api/v1/auth/signup")
						.contentType(MediaType.APPLICATION_JSON)
						.content("""
								{"email": "%s", "password": "%s", "nickname": "%s"}
								""".formatted(EMAIL, PASSWORD, NICKNAME)))
				.andExpect(status().isOk())
				.andExpect(jsonPath("$.data", nullValue()))
				.andExpect(jsonPath("$.message").value("OK"));
	}

	@Test
	void signupFailsWhenEmailNotVerified() throws Exception {
		mockMvc.perform(post("/api/v1/auth/signup")
						.contentType(MediaType.APPLICATION_JSON)
						.content("""
								{"email": "%s", "password": "%s", "nickname": "%s"}
								""".formatted(EMAIL, PASSWORD, NICKNAME)))
				.andExpect(status().isForbidden())
				.andExpect(jsonPath("$.code").value("EMAIL_NOT_VERIFIED"));
	}

	@Test
	void loginReturnsAccessTokenAndRefreshToken() throws Exception {
		setEmailVerified(EMAIL);
		signup(EMAIL, PASSWORD, NICKNAME);

		mockMvc.perform(post("/api/v1/auth/login")
						.contentType(MediaType.APPLICATION_JSON)
						.content("""
								{"email": "%s", "password": "%s"}
								""".formatted(EMAIL, PASSWORD)))
				.andExpect(status().isOk())
				.andExpect(jsonPath("$.data.accessToken").isNotEmpty())
				.andExpect(jsonPath("$.data.refreshToken").isNotEmpty())
				.andExpect(jsonPath("$.message").value("OK"));
	}

	@Test
	void loginRejectsInvalidCredentials() throws Exception {
		mockMvc.perform(post("/api/v1/auth/login")
						.contentType(MediaType.APPLICATION_JSON)
						.content("""
								{"email": "wrong@example.com", "password": "wrongpass"}
								"""))
				.andExpect(status().isUnauthorized())
				.andExpect(jsonPath("$.code").value("UNAUTHORIZED"));
	}

	@Test
	void refreshReturnsNewTokens() throws Exception {
		setEmailVerified(EMAIL);
		signup(EMAIL, PASSWORD, NICKNAME);

		MvcResult loginResult = mockMvc.perform(post("/api/v1/auth/login")
						.contentType(MediaType.APPLICATION_JSON)
						.content("""
								{"email": "%s", "password": "%s"}
								""".formatted(EMAIL, PASSWORD)))
				.andExpect(status().isOk())
				.andReturn();

		String refreshToken = objectMapper.readTree(loginResult.getResponse().getContentAsString())
				.path("data").path("refreshToken").asText();

		when(valueOps.get("refresh:" + EMAIL)).thenReturn(refreshToken);

		mockMvc.perform(post("/api/v1/auth/refresh")
						.contentType(MediaType.APPLICATION_JSON)
						.content("""
								{"refreshToken": "%s"}
								""".formatted(refreshToken)))
				.andExpect(status().isOk())
				.andExpect(jsonPath("$.data.accessToken").isNotEmpty())
				.andExpect(jsonPath("$.data.refreshToken").isNotEmpty());
	}

	@Test
	void refreshFailsWithInvalidToken() throws Exception {
		mockMvc.perform(post("/api/v1/auth/refresh")
						.contentType(MediaType.APPLICATION_JSON)
						.content("""
								{"refreshToken": "invalid.token.value"}
								"""))
				.andExpect(status().isUnauthorized())
				.andExpect(jsonPath("$.code").value("INVALID_TOKEN"));
	}

	private void signup(String email, String password, String nickname) throws Exception {
		mockMvc.perform(post("/api/v1/auth/signup")
						.contentType(MediaType.APPLICATION_JSON)
						.content("""
								{"email": "%s", "password": "%s", "nickname": "%s"}
								""".formatted(email, password, nickname)))
				.andExpect(status().isOk());
	}

}
