package com.ssafy.salmanhae.service.auth;

import com.ssafy.salmanhae.common.exception.ApiException;
import com.ssafy.salmanhae.common.exception.ErrorCode;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.stereotype.Service;

import java.security.SecureRandom;
import java.time.Duration;

@Service
@RequiredArgsConstructor
public class EmailVerificationService {

    private final StringRedisTemplate redisTemplate;
    private final JavaMailSender mailSender;

    @Value("${spring.mail.username}")
    private String senderEmail;

    private static final String VERIFY_PREFIX = "email:verify:";
    private static final String VERIFIED_PREFIX = "email:verified:";

    public void sendCode(String email) {
        String code = String.format("%06d", new SecureRandom().nextInt(1_000_000));
        redisTemplate.opsForValue().set(VERIFY_PREFIX + email, code, Duration.ofMinutes(5));

        SimpleMailMessage message = new SimpleMailMessage();
        message.setFrom(senderEmail);
        message.setTo(email);
        message.setSubject("[살만해] 이메일 인증 코드");
        message.setText("인증 코드: " + code + "\n5분 내에 입력해주세요.");
        mailSender.send(message);
    }

    public void verifyCode(String email, String code) {
        String saved = redisTemplate.opsForValue().get(VERIFY_PREFIX + email);

        if (saved == null || !saved.equals(code)) {
            throw new ApiException(ErrorCode.INVALID_VERIFICATION_CODE);
        }

        redisTemplate.delete(VERIFY_PREFIX + email);
        redisTemplate.opsForValue().set(VERIFIED_PREFIX + email, "true", Duration.ofMinutes(10));
    }
}
