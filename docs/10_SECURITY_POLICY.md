# 10. SECURITY_POLICY

## 기본 방향

Spring Security + JWT를 사용해 자체적으로 JWT를 발급하고 검증합니다. 외부 Auth 서비스에 의존하지 않으며, 회원가입·로그인·토큰 갱신 흐름을 Spring Boot 내에서 완결합니다.

F-1(지도 탐색)과 지도 기반 시세·안전 분석 조회는 비로그인도 가능하며, AI 에이전트·찜하기·대화 세션·HUG 계산은 로그인이 필요합니다.

---

## 인증 흐름

### 회원가입 (이메일 인증 포함)

```
① POST /api/v1/auth/email/send (email)
   → EmailVerificationService가 6자리 코드 생성 (SecureRandom)
   → Redis에 email:verify:{email} = code 저장 (TTL 5분)
   → Gmail SMTP로 인증 코드 발송

② POST /api/v1/auth/email/verify (email + code)
   → Redis에서 email:verify:{email} 조회 후 비교
   → 일치하면 email:verified:{email} = "true" 저장 (TTL 10분)
   → email:verify:{email} 키 삭제

③ POST /api/v1/auth/signup (email + password + nickname)
   → email:verified:{email} 키 확인 → 없으면 403 EMAIL_NOT_VERIFIED
   → BCrypt로 비밀번호 해시 후 DB 저장
```

### 로그인 및 토큰 발급

```
POST /api/v1/auth/login (email + password)
→ BCrypt로 저장된 password_hash 비교
→ JWT로 액세스 토큰(15분) + 리프레시 토큰(7일) 발급
→ Redis에 refresh:{email} = refreshToken 저장 (TTL 7일)
→ 프론트 Axios Interceptor에 저장
```

### 인증된 요청

```
API 요청 시 Authorization: Bearer {accessToken} 헤더 포함
→ Spring Security JwtAuthenticationFilter에서 토큰 서명·만료 검증
→ CustomUserDetailsService.loadUserByUsername(email)로 User 객체 조회
→ UsernamePasswordAuthenticationToken으로 감싸 SecurityContext에 저장
→ 컨트롤러에서 @AuthenticationPrincipal User로 사용
```

### 토큰 갱신 (Token Rotation)

```
POST /api/v1/auth/refresh (refreshToken)
→ JWT 서명·만료 검증
→ Redis refresh:{email} 값과 일치 여부 확인 (불일치 시 401)
→ 새 액세스 토큰 + 새 리프레시 토큰 발급 (rotation)
→ Redis refresh:{email} 갱신
→ 두 토큰 모두 응답
```

### 로그아웃

```
POST /api/v1/auth/logout
→ SecurityContext에서 email 추출
→ Redis refresh:{email} 삭제 → 이후 해당 리프레시 토큰으로 갱신 불가
```

---

## Redis 키 구조

| 키 | 값 | TTL | 용도 |
| --- | --- | --- | --- |
| `email:verify:{email}` | 6자리 코드 | 5분 | 이메일 인증 코드 |
| `email:verified:{email}` | `"true"` | 10분 | 인증 완료 상태 (회원가입 허용 플래그) |
| `refresh:{email}` | JWT 리프레시 토큰 | 7일 | 리프레시 토큰 저장 (rotation·무효화) |

---

## 토큰 정책

| 항목 | 값 |
| --- | --- |
| 액세스 토큰 만료 | 15분 |
| 리프레시 토큰 만료 | 7일 |
| 서명 알고리즘 | HS256 (서버 시크릿 키) |
| JWT 시크릿 키 | Spring 프로퍼티 `jwt.secret`으로 주입. 로컬: `backend/.env`의 `JWT_SECRET`, 운영: 환경변수 `JWT_SECRET`. 코드에 하드코딩 금지 |
| 리프레시 토큰 저장 | Redis (`refresh:{email}`, TTL 7일). 갱신 시 rotate 발급. 로그아웃 시 삭제로 무효화. |
| 이메일 인증 | 회원가입 전 필수. Gmail SMTP + Redis로 6자리 코드 검증 (TTL 5분). |

---

## 공개 API (비로그인 허용)

| API | 이유 |
| --- | --- |
| `GET /api/v1/properties` | 매물 탐색은 공개 기능 |
| `GET /api/v1/properties/{id}` | 매물 상세는 공개 기능 |
| `GET /api/v1/map/viewport` | 지도 줌 레벨별 표시 데이터는 공개 기능 |
| `GET /api/v1/properties/{id}/transactions` | 실거래가는 공개 데이터 기반 |
| `GET /api/v1/properties/{id}/safety-summary` | 안전 요약은 공개 데이터 기반 |
| `GET /api/v1/safety/facilities` | 안전시설은 공개 데이터 기반 |
| `GET /api/v1/price-analysis` | 지도·매물 상세에 포함되는 시세 분석 |
| `POST /api/v1/auth/email/send` | 이메일 인증 코드 발송 |
| `POST /api/v1/auth/email/verify` | 이메일 인증 코드 검증 |
| `POST /api/v1/auth/signup` | 회원가입 (이메일 인증 필수) |
| `POST /api/v1/auth/login` | 로그인 |
| `POST /api/v1/auth/refresh` | 토큰 갱신 (Token Rotation) |

---

## 인증 필요 API

| API | 이유 |
| --- | --- |
| `POST /api/v1/chat` | AI 에이전트 (F-2~F-5) |
| `POST /api/v1/auth/logout` | 로그아웃 (Redis 리프레시 토큰 무효화) |
| `GET /api/v1/wishlist` | 찜 목록 조회 |
| `POST /api/v1/wishlist` | 찜하기 |
| `DELETE /api/v1/wishlist/{id}` | 찜 삭제 |
| `GET /api/v1/sessions` | 대화 세션 목록 (1.5차) |
| `GET /api/v1/hug-eligibility` | HUG 간이 계산 (1.5차) |

---

## JWT 사용 원칙

- 백엔드는 클라이언트가 보낸 userId를 직접 신뢰하지 않습니다.
- 사용자 식별은 반드시 JWT 서명 검증 후 SecurityContext에서 가져옵니다.
- 리프레시 토큰은 Redis에 저장하며, 갱신 시 rotate 발급하고 로그아웃 시 삭제합니다.
- 이메일 인증 코드와 리프레시 토큰은 Redis TTL로 자동 만료합니다.
- 국토부, 생활안전지도, 재난안전, 크롤링 관련 키와 시크릿은 절대 프론트에 노출하지 않습니다.
- 네이버지도 SDK처럼 브라우저에서 직접 쓰는 공개 클라이언트 키는 도메인 제한을 걸고, 서버용 시크릿과 분리합니다.
- 비밀번호는 BCrypt로 해시하여 DB에 저장합니다. 평문 저장 금지.
