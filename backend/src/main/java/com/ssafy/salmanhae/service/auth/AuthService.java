package com.ssafy.salmanhae.service.auth;

import com.ssafy.salmanhae.common.exception.ApiException;
import com.ssafy.salmanhae.common.exception.ErrorCode;
import com.ssafy.salmanhae.model.dao.auth.UserDao;
import com.ssafy.salmanhae.model.dto.auth.LoginResponse;
import com.ssafy.salmanhae.model.dto.auth.RefreshTokenResponse;
import com.ssafy.salmanhae.model.dto.auth.User;
import com.ssafy.salmanhae.util.JwtUtil;
import io.jsonwebtoken.ExpiredJwtException;
import io.jsonwebtoken.JwtException;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserDao userDao;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;

    public void signup(String email, String password, String nickname) {
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

        return new LoginResponse(
                jwtUtil.generateAccessToken(email),
                jwtUtil.generateRefreshToken(email)
        );
    }

    public RefreshTokenResponse refresh(String refreshToken) {
        String email;
        try {
            email = jwtUtil.getEmail(refreshToken);
        } catch (ExpiredJwtException e) {
            throw new ApiException(ErrorCode.EXPIRED_TOKEN);
        } catch (JwtException | IllegalArgumentException e) {
            throw new ApiException(ErrorCode.INVALID_TOKEN);
        }

        String newAccessToken = jwtUtil.generateAccessToken(email);
        return new RefreshTokenResponse(newAccessToken);
    }
}