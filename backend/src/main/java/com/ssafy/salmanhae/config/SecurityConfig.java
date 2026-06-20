package com.ssafy.salmanhae.config;

import com.ssafy.salmanhae.service.CustomUserDetailsService;
import com.ssafy.salmanhae.util.JwtUtil;
import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
@EnableWebSecurity
@RequiredArgsConstructor
public class SecurityConfig {

    private final JwtUtil jwtUtil;
    private final CustomUserDetailsService userDetailsService;

    // Security Filter Chain 설정 — 요청이 들어오면 이 체인을 순서대로 통과하며 인증/인가 처리
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
                // REST API + JWT 방식이므로 CSRF 불필요
                .csrf(csrf -> csrf.disable())
                // JWT는 요청마다 토큰으로 인증하므로 서버 세션을 사용하지 않음
                .sessionManagement(session -> session
                        .sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                // 현재는 모든 경로 허용 — JWT 필터 완성 후 경로별 인증 조건 추가 예정
                .authorizeHttpRequests(auth -> auth
                        // 인증 없이 허용
                        .requestMatchers("/api/v1/auth/signup", "/api/v1/auth/login", "/api/v1/auth/refresh").permitAll()
                        .requestMatchers(HttpMethod.GET, "/api/v1/properties/**", "/api/v1/map/**", "/api/v1/safety/**", "/api/v1/price-analysis").permitAll()
                        // 나머지는 로그인 필요
                        .anyRequest().authenticated()
                );

        return http.build();
    }

    // 비밀번호 BCrypt 해시 인코더 — AuthService에서 회원가입/로그인 시 사용
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
