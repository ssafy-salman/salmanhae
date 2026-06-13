# SECURITY_POLICY: 살만해

## 기본 방향

Supabase Auth를 사용해 JWT를 발급합니다. 프론트엔드는 Spring Boot의 Auth API를 호출하고, Spring Boot는 Supabase Auth를 래핑해 회원가입·로그인·로그아웃 흐름을 중계합니다.

로그인 이후 일반 API 요청에서는 Spring Boot가 Supabase JWT를 검증합니다.

F-1(지도 탐색)과 지도 기반 시세·안전 분석 조회는 비로그인도 가능하며, AI 에이전트·찜하기·대화 세션·HUG 계산은 로그인이 필요합니다.

---

## 인증 흐름

```
사용자 로그인 요청
→ Spring Boot Auth API
→ Supabase Auth 호출
→ JWT 액세스 토큰 + 리프레시 토큰 발급
→ 프론트 Axios Interceptor에 저장
→ API 요청 시 Authorization: Bearer {token} 헤더 포함
→ Spring Security Filter에서 Supabase JWT 검증
→ SecurityContext에서 userId 추출
→ 컨트롤러에서 @AuthenticationPrincipal로 사용
```

---

## 공개 API (비로그인 허용)

| API | 이유 |
| --- | --- |
| `GET /api/v1/properties` | 매물 탐색은 공개 기능 |
| `GET /api/v1/properties/{id}` | 매물 상세는 공개 기능 |
| `GET /api/v1/properties/{id}/transactions` | 실거래가는 공개 데이터 기반 |
| `GET /api/v1/properties/{id}/safety-summary` | 안전 요약은 공개 데이터 기반 |
| `GET /api/v1/safety/facilities` | 안전시설은 공개 데이터 기반 |
| `GET /api/v1/price-analysis` | 지도·매물 상세에 포함되는 시세 분석 |
| `POST /api/v1/auth/signup` | 회원가입 |
| `POST /api/v1/auth/login` | 로그인 |

---

## 인증 필요 API

| API | 이유 |
| --- | --- |
| `POST /api/v1/chat` | AI 에이전트 (F-2~F-5) |
| `GET /api/v1/wishlist` | 찜 목록 조회 |
| `POST /api/v1/wishlist` | 찜하기 |
| `DELETE /api/v1/wishlist/{id}` | 찜 삭제 |
| `GET /api/v1/sessions` | 대화 세션 목록 (1.5차) |
| `GET /api/v1/hug-eligibility` | HUG 간이 계산 (1.5차) |

---

## JWT 사용 원칙

- 백엔드는 클라이언트가 보낸 userId를 직접 신뢰하지 않습니다.
- 사용자 식별은 반드시 Supabase JWT 검증 후 SecurityContext에서 가져옵니다.
- 리프레시 토큰은 Supabase에서 관리합니다. 별도 Redis 블랙리스트는 확장 단계에서 고려합니다.
- API 키(국토부, 네이버지도 등)는 절대 프론트에 노출하지 않습니다.
