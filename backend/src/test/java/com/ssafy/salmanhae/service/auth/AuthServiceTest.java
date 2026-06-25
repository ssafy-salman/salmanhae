package com.ssafy.salmanhae.service.auth;

import com.ssafy.salmanhae.common.exception.ApiException;
import com.ssafy.salmanhae.common.exception.ErrorCode;
import com.ssafy.salmanhae.model.dao.auth.UserDao;
import com.ssafy.salmanhae.model.dto.auth.RefreshResponse;
import com.ssafy.salmanhae.model.dto.auth.User;
import com.ssafy.salmanhae.util.JwtUtil;
import io.jsonwebtoken.ExpiredJwtException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.redis.core.ValueOperations;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.test.util.ReflectionTestUtils;

import java.time.Duration;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;
import org.mockito.quality.Strictness;
import org.mockito.junit.jupiter.MockitoSettings;

@ExtendWith(MockitoExtension.class)
@MockitoSettings(strictness = Strictness.LENIENT)
class AuthServiceTest {

    @Mock private UserDao userDao;
    @Mock private PasswordEncoder passwordEncoder;
    @Mock private JwtUtil jwtUtil;
    @Mock private StringRedisTemplate redisTemplate;
    @Mock private ValueOperations<String, String> valueOps;

    @InjectMocks
    private AuthService authService;

    private static final String EMAIL = "test@example.com";
    private static final String REFRESH_TOKEN = "refresh-token";
    private static final String NEW_ACCESS_TOKEN = "new-access-token";
    private static final String NEW_REFRESH_TOKEN = "new-refresh-token";
    private static final long REFRESH_EXPIRATION = 604800000L;

    @BeforeEach
    void setUp() {
        when(redisTemplate.opsForValue()).thenReturn(valueOps);
        ReflectionTestUtils.setField(authService, "refreshTokenExpiration", REFRESH_EXPIRATION);
    }

    @Test
    void login_savesRefreshTokenToRedis() {
        User user = User.builder().email(EMAIL).password("encoded").nickname("테스터").build();
        when(userDao.findByEmail(EMAIL)).thenReturn(user);
        when(passwordEncoder.matches("password", "encoded")).thenReturn(true);
        when(jwtUtil.generateAccessToken(EMAIL)).thenReturn("access-token");
        when(jwtUtil.generateRefreshToken(EMAIL)).thenReturn(REFRESH_TOKEN);

        authService.login(EMAIL, "password");

        verify(valueOps).set(eq("refresh:" + EMAIL), eq(REFRESH_TOKEN), eq(Duration.ofMillis(REFRESH_EXPIRATION)));
    }

    @Test
    void refresh_validToken_rotatesTokens() {
        when(jwtUtil.getEmail(REFRESH_TOKEN)).thenReturn(EMAIL);
        when(valueOps.get("refresh:" + EMAIL)).thenReturn(REFRESH_TOKEN);
        when(jwtUtil.generateAccessToken(EMAIL)).thenReturn(NEW_ACCESS_TOKEN);
        when(jwtUtil.generateRefreshToken(EMAIL)).thenReturn(NEW_REFRESH_TOKEN);

        RefreshResponse response = authService.refresh(REFRESH_TOKEN);

        assertThat(response.getAccessToken()).isEqualTo(NEW_ACCESS_TOKEN);
        assertThat(response.getRefreshToken()).isEqualTo(NEW_REFRESH_TOKEN);
        verify(valueOps).set(eq("refresh:" + EMAIL), eq(NEW_REFRESH_TOKEN), eq(Duration.ofMillis(REFRESH_EXPIRATION)));
    }

    @Test
    void refresh_tokenNotInRedis_throwsException() {
        when(jwtUtil.getEmail(REFRESH_TOKEN)).thenReturn(EMAIL);
        when(valueOps.get("refresh:" + EMAIL)).thenReturn(null);

        assertThatThrownBy(() -> authService.refresh(REFRESH_TOKEN))
                .isInstanceOf(ApiException.class)
                .satisfies(e -> assertThat(((ApiException) e).getErrorCode())
                        .isEqualTo(ErrorCode.INVALID_TOKEN));
    }

    @Test
    void refresh_expiredToken_throwsException() {
        when(jwtUtil.getEmail(REFRESH_TOKEN)).thenThrow(ExpiredJwtException.class);

        assertThatThrownBy(() -> authService.refresh(REFRESH_TOKEN))
                .isInstanceOf(ApiException.class)
                .satisfies(e -> assertThat(((ApiException) e).getErrorCode())
                        .isEqualTo(ErrorCode.EXPIRED_TOKEN));
    }

    @Test
    void logout_deletesRefreshTokenFromRedis() {
        authService.logout(EMAIL);

        verify(redisTemplate).delete("refresh:" + EMAIL);
    }
}
