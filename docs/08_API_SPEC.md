# API_SPEC: 살만해

## 공통 규칙

- Base path: `/api/v1`
- 지도 범위 파라미터: `west`, `east`, `south`, `north`
- 응답 형식: camelCase JSON
- 인증: `Authorization: Bearer {supabase_jwt}`

---

## 공통 응답 형식

### 성공

```json
{
  "data": { ... },
  "message": "OK"
}
```

목록 조회의 경우:

```json
{
  "data": {
    "items": [ ... ],
    "totalCount": 24
  },
  "message": "OK"
}
```

### 에러

```json
{
  "code": "PROPERTY_NOT_FOUND",
  "message": "해당 매물을 찾을 수 없습니다.",
  "status": 404
}
```

---

## 에러코드 정의

### 4xx — 클라이언트 오류

| HTTP | code | 설명 |
| --- | --- | --- |
| 400 | `INVALID_REQUEST` | 요청 파라미터 누락 또는 형식 오류 |
| 400 | `INVALID_BOUNDS` | 지도 범위 파라미터 오류 (west/east/south/north) |
| 401 | `UNAUTHORIZED` | 인증 토큰 없음 또는 만료 |
| 403 | `FORBIDDEN` | 권한 없음 (다른 사용자 리소스 접근 등) |
| 404 | `PROPERTY_NOT_FOUND` | 매물 없음 |
| 404 | `WISHLIST_NOT_FOUND` | 찜 항목 없음 |
| 404 | `SESSION_NOT_FOUND` | 대화 세션 없음 |
| 409 | `ALREADY_WISHLISTED` | 이미 찜한 매물 |
| 409 | `EMAIL_ALREADY_EXISTS` | 이미 가입된 이메일 |

### 5xx — 서버 오류

| HTTP | code | 설명 |
| --- | --- | --- |
| 500 | `INTERNAL_SERVER_ERROR` | 서버 내부 오류 |
| 502 | `AI_SERVICE_UNAVAILABLE` | FastAPI AI 서비스 응답 없음 |
| 503 | `EXTERNAL_API_ERROR` | 공공데이터 외부 API 오류 |

---

## 공개 API vs 인증 필요 API

| 구분 | 예시 |
| --- | --- |
| 공개 | 매물 조회, 안전시설 조회, 실거래가 조회, 시세 분석 |
| 인증 필요 | AI 에이전트 챗봇, 찜하기, 대화 세션, HUG 계산 |

---

## Property API

### 지도 범위 내 매물 조회
```http
GET /api/v1/properties?west=126.91&east=127.02&south=37.45&north=37.55
```

**Query Params**

| 파라미터 | 필수 | 설명 |
| --- | --- | --- |
| `west` | ✅ | 서쪽 경도 |
| `east` | ✅ | 동쪽 경도 |
| `south` | ✅ | 남쪽 위도 |
| `north` | ✅ | 북쪽 위도 |
| `transactionType` | — | `MONTHLY_RENT` / `JEONSE` / `SALE` |
| `propertyType` | — | `ONE_ROOM` / `OFFICETEL` / `APARTMENT` / `VILLA` / `MULTI_FAMILY` |
| `minDeposit` | — | 최소 보증금 (원) |
| `maxDeposit` | — | 최대 보증금 (원) |

**Response**
```json
{
  "data": {
    "items": [
      {
        "id": 1,
        "buildingName": "대학동 그린빌",
        "address": "서울특별시 관악구 대학동 000-00",
        "propertyType": "ONE_ROOM",
        "transactionType": "MONTHLY_RENT",
        "deposit": 10000000,
        "monthlyRent": 550000,
        "areaM2": 22.5,
        "floor": 3,
        "latitude": 37.470123,
        "longitude": 126.936456,
        "safetyScore": 78
      }
    ],
    "totalCount": 1
  },
  "message": "OK"
}
```

---

### 매물 상세 조회
```http
GET /api/v1/properties/{propertyId}
```

**Response**
```json
{
  "data": {
    "id": 1,
    "buildingName": "대학동 그린빌",
    "address": "서울특별시 관악구 대학동 000-00",
    "roadAddress": "서울특별시 관악구 대학길 00",
    "legalDongCode": "1162010200",
    "propertyType": "ONE_ROOM",
    "transactionType": "MONTHLY_RENT",
    "deposit": 10000000,
    "monthlyRent": 550000,
    "maintenanceFee": 70000,
    "areaM2": 22.5,
    "floor": 3,
    "latitude": 37.470123,
    "longitude": 126.936456,
    "description": "대학가 인근 원룸입니다.",
    "scoreSummary": {
      "safetyScore": 78,
      "priceScore": 82,
      "cctvCount300m": 8,
      "bellCount300m": 2,
      "lightCount300m": 14,
      "policeCount500m": 1
    }
  },
  "message": "OK"
}
```

---

### 매물 주변 실거래가 조회
```http
GET /api/v1/properties/{propertyId}/transactions?years=3
```

**Response**
```json
{
  "data": {
    "items": [
      {
        "transactionType": "MONTHLY_RENT",
        "contractYearMonth": "2026-05",
        "deposit": 10000000,
        "monthlyRent": 520000,
        "areaM2": 21.8,
        "floor": 2
      }
    ],
    "totalCount": 15
  },
  "message": "OK"
}
```

---

### 매물 안전 요약 조회
```http
GET /api/v1/properties/{propertyId}/safety-summary?radius=500
```

**Response**
```json
{
  "data": {
    "propertyId": 1,
    "radius": 500,
    "safetyScore": 78,
    "cctvCount300m": 8,
    "bellCount300m": 2,
    "lightCount300m": 14,
    "policeCount500m": 1
  },
  "message": "OK"
}
```

---

## Safety API

### 안전시설 조회
```http
GET /api/v1/safety/facilities?types=CCTV,EMERGENCY_BELL&west=126.91&east=127.02&south=37.45&north=37.55
```

**Response**
```json
{
  "data": {
    "items": [
      {
        "id": 201,
        "type": "CCTV",
        "name": "대학동 방범 CCTV 12",
        "latitude": 37.470321,
        "longitude": 126.936111
      }
    ],
    "totalCount": 2
  },
  "message": "OK"
}
```

---

## AI 에이전트 API

### 챗봇 메시지 전송 (인증 필요)
```http
POST /api/v1/chat
Authorization: Bearer {token}
```

**Request**
```json
{
  "message": "관악구 보증금 5천 이하 원룸 추천해줘",
  "sessionId": null
}
```

**Response**
```json
{
  "data": {
    "intent": "PROPERTY_SEARCH",
    "message": "관악구에서 조건에 맞는 매물 3개를 찾았습니다.",
    "sessionId": "session-uuid",
    "properties": [
      {
        "id": 1,
        "buildingName": "대학동 그린빌",
        "deposit": 5000000,
        "monthlyRent": 480000,
        "safetyScore": 78,
        "latitude": 37.470123,
        "longitude": 126.936456
      }
    ],
    "legalCards": null
  },
  "message": "OK"
}
```

---

## Auth API

Auth API는 Spring Boot가 제공하는 래핑 API입니다. 프론트엔드는 Supabase Auth를 직접 호출하지 않고, Spring Boot Auth API를 호출합니다. Spring Boot는 내부에서 Supabase Auth API를 호출해 회원가입, 로그인, 로그아웃을 처리하고 발급된 JWT를 프론트에 반환합니다.

### 회원가입
```http
POST /api/v1/auth/signup
```
```json
{ "email": "user@example.com", "password": "password123" }
```

### 로그인
```http
POST /api/v1/auth/login
```
```json
{ "email": "user@example.com", "password": "password123" }
```
**Response**
```json
{
  "data": {
    "accessToken": "jwt-token",
    "refreshToken": "refresh-token",
    "user": { "id": "uuid", "email": "user@example.com", "nickname": null }
  },
  "message": "OK"
}
```

### 로그아웃
```http
POST /api/v1/auth/logout
Authorization: Bearer {token}
```

---

## Wishlist API (인증 필요)

### 찜 목록 조회
```http
GET /api/v1/wishlist
Authorization: Bearer {token}
```

### 찜하기
```http
POST /api/v1/wishlist
Authorization: Bearer {token}
```
```json
{ "propertyId": 1 }
```

### 찜 삭제
```http
DELETE /api/v1/wishlist/{wishlistId}
Authorization: Bearer {token}
```

---

## Price Analysis API

### 지역 시세 분석
```http
GET /api/v1/price-analysis?legalDongCode=1162010200&propertyType=ONE_ROOM&transactionType=MONTHLY_RENT
```

---

## HUG 계산 API (1.5차, 인증 필요)

```http
POST /api/v1/hug-eligibility
Authorization: Bearer {token}
```
```json
{
  "propertyId": 1,
  "deposit": 150000000,
  "priorDebt": 30000000
}
```

---

## 대화 세션 API (1.5차, 인증 필요)

```http
GET /api/v1/sessions
GET /api/v1/sessions/{sessionId}/messages
```
