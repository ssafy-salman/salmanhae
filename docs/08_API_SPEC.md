# 08. API_SPEC

## 공통 규칙

- Base path: `/api/v1`
- 지도 범위 파라미터: `west`, `east`, `south`, `north`
- 응답 형식: camelCase JSON
- 인증: `Authorization: Bearer {jwt}`

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
| 400 | `INVALID_VERIFICATION_CODE` | 이메일 인증 코드가 올바르지 않음 |
| 401 | `UNAUTHORIZED` | 인증 토큰 없음 또는 자격증명 불일치 |
| 401 | `INVALID_TOKEN` | 서명 검증 실패 또는 Redis 불일치 리프레시 토큰 |
| 401 | `EXPIRED_TOKEN` | 만료된 리프레시 토큰 |
| 403 | `FORBIDDEN` | 권한 없음 (다른 사용자 리소스 접근 등) |
| 403 | `EMAIL_NOT_VERIFIED` | 이메일 인증 미완료 상태에서 회원가입 시도 |
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
| `minPrice` | — | 최소 매매가 (원) |
| `maxPrice` | — | 최대 매매가 (원) |
| `keyword` | — | 제목, 건물명, 지번 주소, 도로명 주소 검색어 |

프론트엔드 검색 폼은 금액을 `만원` 단위로 입력받고, Spring Boot API 호출 시 `minDeposit`, `maxDeposit`, `minPrice`, `maxPrice`를 원 단위로 변환해 전송합니다. 전세 또는 매매 거래 유형을 선택한 경우 보증금 입력값은 전송하지 않습니다.

F-1 MVP에서는 실거래가 건물 anchor 기반 `MVP_SYNTHETIC` 더미 매물을 조회합니다. 운영 단계에서는 제휴 피드 또는 합법적으로 확보한 매물 데이터를 `properties`에 저장한 뒤 같은 API로 조회합니다.

**Response — 매물 추천**
```json
{
  "data": {
    "items": [
      {
        "id": 1,
        "title": "대학동 그린빌",
        "buildingName": "그린빌",
        "address": "서울특별시 관악구 대학동 000-00",
        "propertyType": "ONE_ROOM",
        "transactionType": "MONTHLY_RENT",
        "deposit": 10000000,
        "monthlyRent": 550000,
        "price": null,
        "areaM2": 22.5,
        "floor": 3,
        "latitude": 37.470123,
        "longitude": 126.936456
      }
    ],
    "totalCount": 1
  },
  "message": "OK"
}
```

---

## Map View API

### 지도 줌 레벨별 표시 데이터 조회
```http
GET /api/v1/map/viewport?west=126.91&east=127.02&south=37.45&north=37.55&zoom=10
```

프론트는 네이버지도 SDK의 현재 bounds와 zoom을 전달하고, 백엔드는 줌 레벨에 맞춰 지역 평균 또는 매물/클러스터 데이터를 반환합니다.

**Query Params**

| 파라미터 | 필수 | 설명 |
| --- | --- | --- |
| `west` | ✅ | 서쪽 경도 |
| `east` | ✅ | 동쪽 경도 |
| `south` | ✅ | 남쪽 위도 |
| `north` | ✅ | 북쪽 위도 |
| `zoom` | ✅ | 네이버지도 현재 zoom |
| `transactionType` | — | `MONTHLY_RENT` / `JEONSE` / `SALE` |
| `propertyType` | — | `ONE_ROOM` / `OFFICETEL` / `APARTMENT` / `VILLA` / `MULTI_FAMILY` |
| `minDeposit` | — | 최소 보증금 (원) |
| `maxDeposit` | — | 최대 보증금 (원) |
| `minPrice` | — | 최소 매매가 (원) |
| `maxPrice` | — | 최대 매매가 (원) |
| `keyword` | — | 제목, 건물명, 지번 주소, 도로명 주소 검색어 |
| `clusterThreshold` | — | 매물 클러스터링 기준 수. 기본값은 서버 설정 사용 |

프론트엔드 검색 폼은 금액을 `만원` 단위로 입력받고, Spring Boot API 호출 시 `minDeposit`, `maxDeposit`, `minPrice`, `maxPrice`를 원 단위로 변환해 전송합니다. 전세 또는 매매 거래 유형을 선택한 경우 보증금 입력값은 전송하지 않습니다.

**표시 모드**

| mode | 지도 범위 | 반환 데이터 |
| --- | --- | --- |
| `SIDO_AVG` | 시/도 수준 | 시/도 대표 가격 |
| `SIGUNGU_AVG` | 시/군/구 수준 | 시/군/구 대표 가격 |
| `DONG_AVG` | 읍/면/동 수준 | 읍/면/동 대표 가격 |
| `PROPERTY_CLUSTER` | 거리/밀집 수준 | 원형 클러스터 |
| `PROPERTY_MARKER` | 상세 확대 | 개별 매물 |

`SIDO_AVG`, `SIGUNGU_AVG`, `DONG_AVG`는 지도에 표시된 지역 마커를 확대했을 때 실제 매물이 비지 않도록 현재 bounds 안의 활성 매물을 행정구역별로 직접 집계합니다. `transactionType`, `propertyType`, 가격 범위, `keyword` 조건도 같은 방식으로 적용하며 조건에 맞는 매물이 없으면 해당 지역은 반환하지 않습니다. 월세 대표 가격은 보증금이 아니라 `avgMonthlyRent` 기준으로 표시합니다. 프론트엔드는 검색 조건이 활성화된 상태에서 지역 마커를 가격 대신 조건에 맞는 매물 수로 표시합니다.

초기 운영 threshold는 네이버지도 zoom 숫자를 기준으로 서버에서 결정합니다.

| zoom | mode | 설명 |
| --- | --- | --- |
| `<= 9` | `SIDO_AVG` | 시/도 대표 가격 표시 |
| `10`-`11` | `SIGUNGU_AVG` | 시/군/구 대표 가격 표시 |
| `12`-`13` | `DONG_AVG` | 읍/면/동 평균 표시 |
| `14`-`15` | `PROPERTY_CLUSTER` | 거리 수준 밀집 매물 클러스터 표시 |
| `>= 16` | `PROPERTY_MARKER` | 개별 매물 마커 표시 |

**지역 평균 Response**
```json
{
  "data": {
    "mode": "SIGUNGU_AVG",
    "items": [
      {
        "type": "REGION_AVG",
        "regionLevel": "SIGUNGU",
        "regionCode": "11620",
        "regionName": "관악구",
        "avgDeposit": 10000000,
        "avgMonthlyRent": 550000,
        "avgSalePrice": 720000000,
        "transactionCount": 2,
        "latitude": 37.4705615,
        "longitude": 126.936728
      }
    ],
    "totalCount": 1
  },
  "message": "OK"
}
```

**거리/밀집 Response**
```json
{
  "data": {
    "mode": "PROPERTY_CLUSTER",
    "items": [
      {
        "type": "CLUSTER",
        "clusterId": "cluster-37.471-126.938",
        "count": 42,
        "latitude": 37.47102,
        "longitude": 126.93811,
        "radiusM": 180,
        "avgDeposit": 12000000,
        "avgMonthlyRent": 580000
      }
    ],
    "totalCount": 1
  },
  "message": "OK"
}
```

**상세 확대 Response**
```json
{
  "data": {
    "mode": "PROPERTY_MARKER",
    "items": [
      {
        "type": "PROPERTY",
        "id": 1,
        "title": "대학동 그린빌",
        "transactionType": "MONTHLY_RENT",
        "deposit": 10000000,
        "monthlyRent": 550000,
        "price": null,
        "areaM2": 22.5,
        "latitude": 37.470123,
        "longitude": 126.936456
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
    "title": "대학동 그린빌",
    "buildingName": "그린빌",
    "buildingKey": "1162010200:ONE_ROOM:그린빌:000-00",
    "address": "서울특별시 관악구 대학동 000-00",
    "roadAddress": "서울특별시 관악구 대학길 00",
    "legalDongCode": "1162010200",
    "propertyType": "ONE_ROOM",
    "transactionType": "MONTHLY_RENT",
    "deposit": 10000000,
    "monthlyRent": 550000,
    "price": null,
    "maintenanceFee": 70000,
    "areaM2": 22.5,
    "floor": 3,
    "totalFloor": 5,
    "latitude": 37.470123,
    "longitude": 126.936456,
    "description": "대학가 인근 원룸입니다."
  },
  "message": "OK"
}
```

---

### 매물 주변 실거래가 조회
```http
GET /api/v1/properties/{propertyId}/transactions?years=3
```

매물의 `buildingKey`와 같은 거래를 우선 조회하고, 부족하면 같은 `legalDongCode`, `propertyType`, `transactionType`, `areaM2 ±10㎡` 조건의 최근 거래로 확장합니다.

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
        "price": null,
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
    "priceScore": 64,
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

Supervisor 패턴으로 구현되어 있으며, 복합 질문 시 여러 워커를 순차 실행하고 `workersCalled` 배열로 반환합니다.

**워커(worker) 목록**

| worker | 설명 |
| --- | --- |
| `PROPERTY_SEARCH` | 매물 추천·검색 (Text-to-SQL → Supabase 직접 조회) |
| `LEGAL_CONSULT` | 임대차 법률 상담 (pgvector RAG) |
| `PRICE_ANALYSIS` | 시세·실거래가 분석 (Spring Boot API) |
| `SAFETY_ANALYSIS` | 주변 안전시설·치안 분석 (Spring Boot API) |
| `GENERAL_CHAT` | 인사·잡담 등 부동산 무관 일반 대화 |

### 챗봇 메시지 전송 (인증 필요)
```http
POST /api/v1/chat
Authorization: Bearer {token}
```

**Request**
```json
{
  "message": "관악구 보증금 5천 이하 원룸 추천해줘",
  "sessionId": null,
  "selectedPropertyId": null
}
```

| 필드 | 필수 | 설명 |
| --- | --- | --- |
| `message` | ✅ | 사용자 질문 |
| `sessionId` | — | 대화 세션 ID. MVP에서는 `null` 허용 |
| `selectedPropertyId` | — | 지도/매물 상세에서 선택한 매물 ID. 시세·안전 분석 질문에서 사용 |

**Response — 매물 검색**
```json
{
  "data": {
    "workersCalled": ["PROPERTY_SEARCH"],
    "message": "관악구에서 조건에 맞는 매물 3개를 찾았습니다.",
    "sessionId": "session-uuid",
    "properties": [
      {
        "id": 1,
        "title": "대학동 그린빌",
        "building_name": "대학동 그린빌",
        "address": "서울특별시 관악구 대학동 123",
        "property_type": "ONE_ROOM",
        "transaction_type": "MONTHLY_RENT",
        "deposit": 5000000,
        "monthly_rent": 480000,
        "price": null,
        "area_m2": "23.14",
        "floor": 3,
        "latitude": "37.470123",
        "longitude": "126.936456"
      }
    ],
    "legalCards": [],
    "analysisCards": []
  },
  "message": "OK"
}
```

**Response — 법률 RAG**
```json
{
  "data": {
    "workersCalled": ["LEGAL_CONSULT"],
    "message": "관련 법령 근거 2개를 확인했습니다. 실제 계약 전에는 전문가 검토도 함께 권장합니다.",
    "sessionId": null,
    "properties": [],
    "legalCards": [
      {
        "lawName": "주택임대차보호법",
        "articleNo": "제3조의2",
        "title": "보증금의 회수",
        "content": "확정일자를 갖춘 임차인은 경매 또는 공매 시 후순위권리자보다 우선하여 보증금을 변제받을 수 있습니다.",
        "score": 0.86
      }
    ],
    "analysisCards": []
  },
  "message": "OK"
}
```

**Response — 시세·안전 분석 (복합 의도 예시)**
```json
{
  "data": {
    "workersCalled": ["SAFETY_ANALYSIS", "PRICE_ANALYSIS"],
    "message": "선택한 매물의 실거래가와 주변 안전시설 데이터를 기준으로 분석했습니다.",
    "sessionId": null,
    "properties": [],
    "legalCards": [],
    "analysisCards": [
      {
        "type": "PRICE",
        "title": "시세 분석",
        "summary": "주변 실거래가 대비 가격 적정성을 확인했습니다.",
        "score": null,
        "metrics": {
          "selectedPropertyId": "1",
          "comparableTransactionCount": 2,
          "regionStatCount": 1,
          "buildingStatCount": 1,
          "avgDeposit": 10500000,
          "avgMonthlyRent": 520000
        }
      },
      {
        "type": "SAFETY",
        "title": "안전 분석",
        "summary": "반경 500m 기준 안전 점수와 주요 안전시설 개수를 확인했습니다.",
        "score": 78,
        "metrics": {
          "selectedPropertyId": "1",
          "radius": 500,
          "safetyScore": 78,
          "cctvCount300m": 8,
          "bellCount300m": 0,
          "lightCount300m": 14,
          "policeCount500m": 1
        }
      }
    ]
  },
  "message": "OK"
}
```

`analysisCards[].metrics`는 카드 유형에 따라 달라질 수 있으며, 프론트엔드는 알 수 없는 metric key를 무시하고 위 표준 key를 우선 표시합니다.

---

## Auth API

Spring Boot가 Spring Security + JJWT로 자체 구현한 인증 API입니다. 프론트엔드는 이 API만 호출하며, 외부 Auth 서비스를 직접 호출하지 않습니다.

회원가입 전 이메일 인증이 필수입니다. 인증 코드는 Gmail SMTP로 발송되고 Redis에 5분간 보관됩니다.

### 이메일 인증 코드 발송
```http
POST /api/v1/auth/email/send
```
```json
{ "email": "user@example.com" }
```
**Response**
```json
{ "data": null, "message": "OK" }
```

### 이메일 인증 코드 검증
```http
POST /api/v1/auth/email/verify
```
```json
{ "email": "user@example.com", "code": "123456" }
```
**Response**
```json
{ "data": null, "message": "OK" }
```
**Error** — 코드 불일치 또는 만료 시: `400 INVALID_VERIFICATION_CODE`

### 회원가입
```http
POST /api/v1/auth/signup
```
```json
{ "email": "user@example.com", "password": "password123", "nickname": "홍길동" }
```
이메일 인증(`/email/verify`) 완료 후 10분 이내에 호출해야 합니다.

**Response**
```json
{ "data": null, "message": "OK" }
```
**Error** — 인증 미완료 시: `403 EMAIL_NOT_VERIFIED`

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
    "accessToken": "jwt-access-token",
    "refreshToken": "jwt-refresh-token"
  },
  "message": "OK"
}
```

### 토큰 갱신 (Token Rotation)
```http
POST /api/v1/auth/refresh
```
```json
{ "refreshToken": "jwt-refresh-token" }
```
갱신 시 액세스 토큰과 리프레시 토큰을 **모두 새로 발급**합니다 (Token Rotation). 프론트는 두 토큰을 모두 교체해야 합니다.

**Response**
```json
{
  "data": {
    "accessToken": "new-jwt-access-token",
    "refreshToken": "new-jwt-refresh-token"
  },
  "message": "OK"
}
```
**Error** — 서명 불일치·Redis 불일치: `401 INVALID_TOKEN` / 만료: `401 EXPIRED_TOKEN`

### 로그아웃
```http
POST /api/v1/auth/logout
Authorization: Bearer {token}
```
Redis에서 리프레시 토큰을 삭제하여 이후 갱신을 차단합니다.

**Response**
```json
{ "data": null, "message": "OK" }
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

**Response**
```json
{
  "data": {
    "legalDongCode": "1162010200",
    "propertyType": "ONE_ROOM",
    "transactionType": "MONTHLY_RENT",
    "regionStats": [
      {
        "regionLevel": "DONG",
        "regionCode": "1162010200",
        "sido": "서울특별시",
        "sigungu": "관악구",
        "dong": "대학동",
        "avgDeposit": 10500000,
        "medianDeposit": 10000000,
        "avgMonthlyRent": 520000,
        "medianMonthlyRent": 520000,
        "avgPrice": null,
        "medianPrice": null,
        "transactionCount": 3,
        "sampleFromYm": "2026-03",
        "sampleToYm": "2026-05"
      }
    ],
    "buildingStats": [
      {
        "buildingKey": "1162010200:ONE_ROOM:그린빌:12-3",
        "buildingName": "그린빌",
        "sido": "서울특별시",
        "sigungu": "관악구",
        "dong": "대학동",
        "avgDeposit": 11000000,
        "medianDeposit": 11000000,
        "avgMonthlyRent": 510000,
        "medianMonthlyRent": 510000,
        "avgPrice": null,
        "medianPrice": null,
        "transactionCount": 2,
        "sampleFromYm": "2026-04",
        "sampleToYm": "2026-05"
      }
    ]
  },
  "message": "OK"
}
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

## F-4 Safety Analysis Contract

`GET /api/v1/properties/{propertyId}/safety-summary?radius=500` returns stored values from `property_score_stat`. The endpoint must not call public safety APIs at request time.

Backend AI `SAFETY_ANALYSIS` uses Spring Boot only:

1. Read `selectedPropertyId` from the chat context.
2. Call `GET /api/v1/properties/{propertyId}/safety-summary?radius=500`.
3. Copy `safetyScore`, `cctvCount300m`, `bellCount300m`, `lightCount300m`, and `policeCount500m` into the safety analysis card metrics.
4. Generate a Korean answer that clearly shows the score and facility counts when present.

If `selectedPropertyId` is missing, backend-ai returns a selection-required fallback instead of calling Spring. If Spring is unavailable, backend-ai returns a controlled fallback with `error = SPRING_API_UNAVAILABLE`.

## F-4 Safety-Aware Property Search

For chat property recommendations, backend-ai may include precomputed safety score fields from `property_score_stat` in each `properties[]` item:

```json
{
  "id": 1,
  "title": "Gwanak One Room",
  "building_name": "Green Villa",
  "address": "Seoul Gwanak-gu ...",
  "property_type": "ONE_ROOM",
  "transaction_type": "MONTHLY_RENT",
  "deposit": 10000000,
  "monthly_rent": 500000,
  "price": null,
  "area_m2": 22.5,
  "floor": 3,
  "latitude": 37.470123,
  "longitude": 126.936456,
  "safety_score": 91,
  "cctv_count_300m": 12,
  "bell_count_300m": 3,
  "light_count_300m": 21,
  "police_count_500m": 1
}
```

When the extracted property-search criteria contains `sort_by = "safety_desc"`, backend-ai orders recommendations by `property_score_stat.safety_score DESC NULLS LAST`. If `min_safety_score` is present, backend-ai filters out rows below that stored score. This still uses stored DB values only; public safety APIs are not called during chat requests.
