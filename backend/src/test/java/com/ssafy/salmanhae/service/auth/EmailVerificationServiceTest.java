package com.ssafy.salmanhae.service.auth;

import com.ssafy.salmanhae.common.exception.ApiException;
import com.ssafy.salmanhae.common.exception.ErrorCode;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.redis.core.ValueOperations;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.test.util.ReflectionTestUtils;

import java.time.Duration;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class EmailVerificationServiceTest {

    @Mock
    private StringRedisTemplate redisTemplate;

    @Mock
    private JavaMailSender mailSender;

    @Mock
    private ValueOperations<String, String> valueOps;

    @InjectMocks
    private EmailVerificationService emailVerificationService;

    private static final String EMAIL = "test@example.com";

    @BeforeEach
    void setUp() {
        when(redisTemplate.opsForValue()).thenReturn(valueOps);
        ReflectionTestUtils.setField(emailVerificationService, "senderEmail", "sender@gmail.com");
    }

    @Test
    void sendCode_savesCodeToRedisAndSendsEmail() {
        emailVerificationService.sendCode(EMAIL);

        verify(valueOps).set(eq("email:verify:" + EMAIL), anyString(), eq(Duration.ofMinutes(5)));
        verify(mailSender).send(any(SimpleMailMessage.class));
    }

    @Test
    void verifyCode_validCode_savesVerifiedKey() {
        when(valueOps.get("email:verify:" + EMAIL)).thenReturn("123456");

        emailVerificationService.verifyCode(EMAIL, "123456");

        verify(redisTemplate).delete("email:verify:" + EMAIL);
        verify(valueOps).set(eq("email:verified:" + EMAIL), eq("true"), eq(Duration.ofMinutes(10)));
    }

    @Test
    void verifyCode_invalidCode_throwsException() {
        when(valueOps.get("email:verify:" + EMAIL)).thenReturn("123456");

        assertThatThrownBy(() -> emailVerificationService.verifyCode(EMAIL, "999999"))
                .isInstanceOf(ApiException.class)
                .satisfies(e -> assertThat(((ApiException) e).getErrorCode())
                        .isEqualTo(ErrorCode.INVALID_VERIFICATION_CODE));
    }

    @Test
    void verifyCode_codeNotFound_throwsException() {
        when(valueOps.get("email:verify:" + EMAIL)).thenReturn(null);

        assertThatThrownBy(() -> emailVerificationService.verifyCode(EMAIL, "123456"))
                .isInstanceOf(ApiException.class)
                .satisfies(e -> assertThat(((ApiException) e).getErrorCode())
                        .isEqualTo(ErrorCode.INVALID_VERIFICATION_CODE));
    }
}
