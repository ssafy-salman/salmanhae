package com.ssafy.salmanhae.service.auth;

import com.ssafy.salmanhae.common.exception.ApiException;
import com.ssafy.salmanhae.common.exception.ErrorCode;
import com.ssafy.salmanhae.model.dao.auth.UserDao;
import com.ssafy.salmanhae.model.dto.auth.LoginResponse;
import com.ssafy.salmanhae.model.dto.auth.RefreshResponse;
import com.ssafy.salmanhae.model.dto.auth.User;
import com.ssafy.salmanhae.util.JwtUtil;
import io.jsonwebtoken.ExpiredJwtException;
import io.jsonwebtoken.JwtException;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.time.Duration;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserDao userDao;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;
    private final StringRedisTemplate redisTemplate;

    @Value("${jwt.refresh-token-expiration}")
    private long refreshTokenExpiration;

    private static final String REFRESH_PREFIX = "refresh:";

    public void signup(String email, String password, String nickname) {
        if (!Boolean.TRUE.toString().equals(redisTemplate.opsForValue().get("email:verified:" + email))) {
            throw new ApiException(ErrorCode.EMAIL_NOT_VERIFIED);
        }

        User user = User.builder()
                .email(email)
                .password(passwordEncoder.encode(password))
                .nickname(nickname)
                .build();
        userDao.save(user);
    }

    public LoginResponse login(String email, String password) {
        User user = userDao.findByEmail(email);
        if (user == null || !passwordEncoder.matches(password, user.getPassword())) {
            throw new ApiException(ErrorCode.UNAUTHORIZED);
        }

        String accessToken = jwtUtil.generateAccessToken(email);
        String refreshToken = jwtUtil.generateRefreshToken(email);
        redisTemplate.opsForValue().set(REFRESH_PREFIX + email, refreshToken, Duration.ofMillis(refreshTokenExpiration));

        return new LoginResponse(accessToken, refreshToken);
    }

    public RefreshResponse refresh(String refreshToken) {
        String email;
        try {
            email = jwtUtil.getEmail(refreshToken);
        } catch (ExpiredJwtException e) {
            throw new ApiException(ErrorCode.EXPIRED_TOKEN);
        } catch (JwtException | IllegalArgumentException e) {
            throw new ApiException(ErrorCode.INVALID_TOKEN);
        }

        String stored = redisTemplate.opsForValue().get(REFRESH_PREFIX + email);
        if (!refreshToken.equals(stored)) {
            throw new ApiException(ErrorCode.INVALID_TOKEN);
        }

        String newAccessToken = jwtUtil.generateAccessToken(email);
        String newRefreshToken = jwtUtil.generateRefreshToken(email);
        redisTemplate.opsForValue().set(REFRESH_PREFIX + email, newRefreshToken, Duration.ofMillis(refreshTokenExpiration));

        return new RefreshResponse(newAccessToken, newRefreshToken);
    }

    public void logout(String email) {
        redisTemplate.delete(REFRESH_PREFIX + email);
    }
}