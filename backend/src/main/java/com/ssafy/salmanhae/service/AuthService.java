package com.ssafy.salmanhae.service;

import com.ssafy.salmanhae.model.dao.UserDao;
import com.ssafy.salmanhae.model.dto.LoginResponse;
import com.ssafy.salmanhae.model.dto.User;
import com.ssafy.salmanhae.util.JwtUtil;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.Map;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserDao userDao;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;

    // 회원가입
    public void signup(String email, String password, String nickname) {
        User user = User.builder()
                .email(email)
                .password(passwordEncoder.encode(password))
                .nickname(nickname)
                .build();
        userDao.save(user);
    }

    // 로그인
    public LoginResponse login(String email, String password) {
        User user = userDao.findByEmail(email);
        if (user == null || !passwordEncoder.matches(password, user.getPassword())) {
            throw new IllegalArgumentException("이메일 또는 비밀번호가 올바르지 않습니다.");
        }

        return new LoginResponse(
                jwtUtil.generateAccessToken(email),
                jwtUtil.generateRefreshToken(email)
        );
    }
}
