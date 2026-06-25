# API 설계서

## 1. 공통 규칙

| 항목 | 내용 |
| --- | --- |
| Base URL | `/api/v1` |
| 응답 형식 | `{ "data": ..., "message": "OK" }` |
| 목록 응답 | `{ "data": { "items": [], "totalCount": 0 }, "message": "OK" }` |
| 인증 | `Authorization: Bearer {accessToken}` |
| JSON 스타일 | camelCase |
| 에러 형식 | `{ "code": "...", "message": "...", "status": 400 }` |

## 2. 인증 정책

| 구분 | 접근 |
| --- | --- |
| 공개 | 회원가입/로그인/토큰갱신/이메일 인증, 매물 조회, 지도 조회, 안전시설 조회, 시세 분석 |
| 인증 필요 | 로그아웃, AI 챗봇, 확장 기능인 찜하기/대화 세션/HUG 계산 |

Spring Security 설정상 `GET /api/v1/properties/**`, `GET /api/v1/map/**`, `GET /api/v1/safety/**`, `GET /api/v1/price-analysis`는 공개이며 나머지는 JWT 인증이 필요하다.

## 3. Spring Boot Public API

### 3.1 Auth API

| Method | Endpoint | 설명 | Request | Response |
| --- | --- | --- | --- | --- |
| POST | `/api/v1/auth/email/send` | 이메일 인증 코드 발송 | `{ email }` | `data: null` |
| POST | `/api/v1/auth/email/verify` | 인증 코드 검증 | `{ email, code }` | `data: null` |
| POST | `/api/v1/auth/signup` | 회원가입 | `{ email, password, nickname }` | `data: null` |
| POST | `/api/v1/auth/login` | 로그인 | `{ email, password }` | `{ accessToken, refreshToken }` |
| POST | `/api/v1/auth/refresh` | 토큰 갱신 | `{ refreshToken }` | `{ accessToken, refreshToken }` |
| POST | `/api/v1/auth/logout` | 로그아웃 | JWT | `data: null` |

### 3.2 Property API

| Method | Endpoint | 설명 | 인증 |
| --- | --- | --- | --- |
| GET | `/api/v1/properties` | 지도 bounds 내 매물 목록 조회 | 공개 |
| GET | `/api/v1/properties/{propertyId}` | 매물 상세 조회 | 공개 |
| GET | `/api/v1/properties/{propertyId}/transactions` | 매물 주변 실거래가 조회 | 공개 |
| GET | `/api/v1/properties/{propertyId}/safety-summary` | 매물 안전 요약 조회 | 공개 |

`GET /api/v1/properties` Query:

| 파라미터 | 필수 | 설명 |
| --- | --- | --- |
| `west`, `east`, `south`, `north` | O | 지도 bounds |
| `transactionType` | - | `MONTHLY_RENT`, `JEONSE`, `SALE` |
| `propertyType` | - | `ONE_ROOM`, `OFFICETEL`, `VILLA`, `APARTMENT`, `MULTI_FAMILY` |
| `minDeposit`, `maxDeposit` | - | 보증금 범위, 원 단위 |
| `minPrice`, `maxPrice` | - | 매매가 범위, 원 단위 |
| `keyword` | - | 제목/건물명/주소 검색어 |

### 3.3 Map Viewport API

| Method | Endpoint | 설명 | 인증 |
| --- | --- | --- | --- |
| GET | `/api/v1/map/viewport` | zoom별 지역 평균/클러스터/매물 표시 데이터 조회 | 공개 |

Query:

| 파라미터 | 필수 | 설명 |
| --- | --- | --- |
| `west`, `east`, `south`, `north` | O | 지도 bounds |
| `zoom` | O | 네이버지도 zoom |
| `transactionType`, `propertyType`, `minDeposit`, `maxDeposit`, `minPrice`, `maxPrice`, `keyword` | - | 매물 필터 |
| `clusterThreshold` | - | 명세상 선택값, 서버 기본 정책 사용 |

Zoom별 mode:

| zoom | mode |
| --- | --- |
| `<= 9` | `SIDO_AVG` |
| `10-11` | `SIGUNGU_AVG` |
| `12-13` | `DONG_AVG` |
| `14-15` | `PROPERTY_CLUSTER` |
| `>= 16` | `PROPERTY_MARKER` |

### 3.4 Safety API

| Method | Endpoint | 설명 | 인증 |
| --- | --- | --- | --- |
| GET | `/api/v1/safety/facilities` | 안전시설 조회 | 공개 |

Query:

| 파라미터 | 필수 | 설명 |
| --- | --- | --- |
| `west`, `east`, `south`, `north` | O | 조회 bounds |
| `types` | - | `CCTV,EMERGENCY_BELL,SECURITY_LIGHT,POLICE` |

### 3.5 Price Analysis API

| Method | Endpoint | 설명 | 인증 |
| --- | --- | --- | --- |
| GET | `/api/v1/price-analysis` | 지역/건물 시세 통계 조회 | 공개 |

Query:

| 파라미터 | 필수 | 설명 |
| --- | --- | --- |
| `legalDongCode` | O | 법정동 코드 |
| `propertyType` | O | 매물 유형 |
| `transactionType` | O | 거래 유형 |

### 3.6 Chat API

| Method | Endpoint | 설명 | 인증 |
| --- | --- | --- | --- |
| POST | `/api/v1/chat` | AI 에이전트 메시지 전송 | 필요 |

Request:

```json
{
  "message": "관악구 보증금 5천 이하 원룸 추천해줘",
  "sessionId": null,
  "selectedPropertyId": null
}
```

Response 핵심 필드:

| 필드 | 설명 |
| --- | --- |
| `intent` | Spring 응답에 담기는 AI intent/workers 정보 |
| `message` 또는 `answer` | 자연어 답변 |
| `properties` | 매물 추천 카드 |
| `legalCards` | 법률 RAG 근거 카드 |
| `analysisCards` | 시세/안전 분석 카드 |

## 4. Backend AI Internal API

| Method | Endpoint | 설명 | 인증 |
| --- | --- | --- | --- |
| GET | `/health` | AI 서버 health check | 공개 |
| POST | `/internal/agent/chat` | Spring Boot가 호출하는 내부 에이전트 API | `X-Internal-Api-Key` |

Request:

```json
{
  "userId": "user@example.com",
  "sessionId": null,
  "message": "이 매물 안전한지 봐줘",
  "context": {
    "selectedPropertyId": "1",
    "recentMessages": []
  }
}
```

Response:

```json
{
  "workersCalled": ["SAFETY_ANALYSIS", "PRICE_ANALYSIS"],
  "answer": "선택한 매물의 실거래가와 주변 안전시설 데이터를 기준으로 분석했습니다.",
  "properties": [],
  "legalCards": [],
  "analysisCards": [],
  "toolResults": {},
  "nextActions": []
}
```

## 5. 주요 에러코드

| HTTP | Code | 설명 |
| --- | --- | --- |
| 400 | `INVALID_REQUEST` | 요청 파라미터 누락/형식 오류 |
| 400 | `INVALID_BOUNDS` | 지도 bounds 오류 |
| 400 | `INVALID_VERIFICATION_CODE` | 이메일 인증 코드 오류 |
| 401 | `UNAUTHORIZED` | 인증 실패 |
| 401 | `INVALID_TOKEN` | JWT/refresh token 검증 실패 |
| 401 | `EXPIRED_TOKEN` | 만료된 refresh token |
| 403 | `EMAIL_NOT_VERIFIED` | 이메일 인증 미완료 |
| 404 | `PROPERTY_NOT_FOUND` | 매물 없음 |
| 502 | `AI_SERVICE_UNAVAILABLE` | backend-ai 응답 없음 |
| 503 | `EXTERNAL_API_ERROR` | 공공 API 오류 |

