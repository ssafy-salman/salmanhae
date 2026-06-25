# 07. DOMAIN_MODEL

## 모델 요약

| 모델 | 역할 |
| --- | --- |
| `Property` | 지도에 표시할 매물 후보 기본 정보. F-1 MVP는 실거래가 건물 anchor 기반 더미 매물 seed를 사용하고, 운영 단계에서는 합법적으로 확보한 매물 데이터를 같은 구조로 저장 |
| `TransactionHistory` | 국토교통부 실거래가 (전월세 + 매매 8종). F-1에서는 건물 anchor와 가격 기준 원천으로도 사용 |
| `SafetyFacility` | CCTV, 비상벨, 보안등, 치안시설 좌표 |
| `PropertyScoreStat` | 매물별 안전·가격 점수 사전 계산 통계 |
| `RegionPriceStat` | 지도 줌 레벨별 표시를 위한 지역 단위 실거래가 평균 |
| `LegalDocumentChunk` | F-3 법률 RAG 검색을 위한 법령 조문 chunk와 embedding |
| `User` | 로그인 사용자 정보 (Spring Security 자체 관리) |
| `Wishlist` | 찜한 매물 |
| `ConversationSession` | AI 에이전트 대화 세션 (1.5차) |
| `ConversationMessage` | 대화 메시지 원문 (1.5차) |

---

## Enum 기준

| Enum | 값 | 설명 |
| --- | --- | --- |
| `PropertyType` | `ONE_ROOM`, `OFFICETEL`, `VILLA`, `APARTMENT`, `MULTI_FAMILY` | 매물 또는 실거래가의 주택 유형 |
| `TransactionType` | `MONTHLY_RENT`, `JEONSE`, `SALE` | 월세, 전세, 매매 구분 |
| `PropertySource` | `MVP_SYNTHETIC`, `NAVER_REAL_ESTATE` | 매물 데이터 출처. `MVP_SYNTHETIC`은 실거래가 건물 anchor 기반 더미 매물 |
| `GeocodingQuality` | `BUILDING_EXACT`, `ADDRESS_EXACT`, `DONG_APPROX`, `FAILED` | 실거래가 주소성 정보를 좌표로 변환한 품질 |
| `SafetyFacilityType` | `CCTV`, `EMERGENCY_BELL`, `SECURITY_LIGHT`, `POLICE` | 안전시설 유형 |
| `RegionLevel` | `SIDO`, `SIGUNGU`, `DONG` | 지도 평균 표시용 행정구역 레벨 |
| `ConversationIntent` | `PROPERTY_SEARCH`, `LEGAL_CONSULT`, `PRICE_ANALYSIS`, `SAFETY_ANALYSIS`, `HUG_CALC` | AI 에이전트 의도 분류 |

---

## Property — 지도 표시용 매물 후보

F-1 MVP에서는 네이버부동산 실시간 크롤링 대신 국토교통부 실거래가에서 추출한 실제 건물·지역 anchor 위에 더미 매물 seed를 생성해 `properties`에 저장합니다. 이 데이터는 지도 범위 조회, 필터, 마커, 상세 화면 검증에 사용합니다.

운영 단계에서 제휴 매물 피드 또는 합법적으로 확보한 네이버부동산 매물 데이터가 준비되면 같은 테이블에 저장하되, `source`, `source_property_id`, `source_url`, `crawled_at`으로 출처와 중복을 관리합니다.

```
properties
- id
- title
- building_name
- building_key
- anchor_transaction_id
- property_type
- transaction_type
- deposit
- monthly_rent
- price
- maintenance_fee
- area_m2
- floor
- total_floor
- address
- road_address
- sido
- sigungu
- dong
- legal_dong_code
- latitude
- longitude
- geocoding_provider
- geocoding_quality
- geocoded_at
- description
- source                  ← MVP_SYNTHETIC / NAVER_REAL_ESTATE
- source_property_id
- source_url
- crawled_at
- registered_at
- is_active
- created_at
- updated_at
```

### 가격 필드 규칙

| transaction_type | deposit | monthly_rent | price |
| --- | --- | --- | --- |
| `MONTHLY_RENT` | 보증금 | 월세 | `null` |
| `JEONSE` | 전세 보증금 | `null` | `null` |
| `SALE` | `null` | `null` | 매매가 |

### F-1 seed 정책

- `source = MVP_SYNTHETIC`
- `source_property_id = synthetic-{building-key}-{sequence}`
- `source_url = null`
- `crawled_at = null`
- 실거래가 정규화 row에서 `building_key` 기준 건물 anchor를 추출합니다.
- 지오코딩 품질이 `BUILDING_EXACT` 또는 `ADDRESS_EXACT`인 anchor만 지도 bounds 조회용 매물로 생성합니다.
- 가격은 같은 건물 또는 같은 법정동·주택유형·면적대 실거래가 중앙값을 기준으로 생성합니다.
- 정규화 입력, 지오코딩 캐시, 생성 결과는 `data/pipeline/` 아래 로컬 산출물로 둡니다.
- Supabase 스키마는 `database/migrations/`를 적용하고, 데이터는 `scripts/data_pipeline/pipeline.py`가 직접 upsert합니다.

---

## TransactionHistory — 실거래가

전월세 4종 + 매매 4종 모두 동일 테이블에 저장합니다.

```
transaction_history
- id
- source_api
- source_transaction_key
- property_type
- transaction_type        ← MONTHLY_RENT / JEONSE / SALE
- sido
- sigungu
- dong
- legal_dong_code
- jibun
- building_name
- building_key
- contract_year_month
- contract_day
- deposit
- monthly_rent            ← 매매는 null
- price                   ← 매매가 (전월세는 null)
- area_m2
- floor
- build_year
- raw_json
- created_at
```

### building_key 생성 기준

`building_key`는 매물과 실거래가를 연결하는 내부 키입니다. 기본 형식은 `legal_dong_code + property_type + building_name + jibun`이며, 건물명이 없는 단독/다가구는 `legal_dong_code + property_type + jibun`을 사용합니다. 원천 API별 필드명이 다르므로 정규화 단계에서 동일한 규칙으로 생성합니다.

---

## RegionPriceStat — 지역별 실거래가 평균

실거래가 배치 후 시/도, 시/군/구, 읍/면/동 단위 평균을 계산해 지도 줌 레벨별 표시 데이터로 사용합니다.

```
region_price_stat
- id
- region_level            ← SIDO / SIGUNGU / DONG
- region_code
- sido
- sigungu
- dong
- property_type
- transaction_type
- avg_deposit
- median_deposit
- avg_monthly_rent
- median_monthly_rent
- avg_price
- median_price
- transaction_count
- sample_from_ym
- sample_to_ym
- created_at
- updated_at
```

---

## SafetyFacility — 안전시설

```
safety_facility
- id
- type
- name
- address
- latitude
- longitude
- source
- source_id
- description
- updated_at
```

---

## PropertyScoreStat — 매물별 점수

```
property_score_stat
- property_id
- safety_score
- price_score
- cctv_count_300m
- bell_count_300m
- light_count_300m
- police_count_500m
- updated_at
```

---

## LegalDocumentChunk — 법률 RAG 문서 chunk

F-3 MVP에서는 주택임대차보호법과 전세사기피해자 지원 및 주거안정에 관한 특별법 조문을 청킹해 `legal_document_chunks`에 저장합니다. pgvector 유사도 검색은 FastAPI(`backend-ai`)에서만 수행하며, Spring Boot는 법률 문서를 직접 검색하지 않습니다.

```text
legal_document_chunks
- id
- law_id
- law_name
- article_no
- article_title
- effective_date
- source_name
- source_url
- chunk_index
- content
- content_hash
- embedding              ← vector(1536), Phase 2 dry-run에서는 null 허용
- metadata_json
- created_at
- updated_at
```

### F-3 인덱싱 정책

- MVP 대상 법령은 `주택임대차보호법`, `전세사기피해자 지원 및 주거안정에 관한 특별법`으로 제한합니다.
- 원문 출처는 공식 법령 출처 URL을 `source_url`에 저장합니다.
- 같은 원문 chunk의 중복 적재를 막기 위해 `content_hash`를 고유 키로 사용합니다.
- Phase 2에서는 오프라인 JSON 입력을 검증하고 chunk row를 준비하는 dry-run까지만 구현합니다.
- 실제 embedding 생성과 Supabase upsert는 이후 Phase에서 `backend-ai` 인덱싱 단계로 연결합니다.

---

## User — 사용자

Spring Security가 인증을 직접 관리하며, 사용자 정보와 자격증명을 DB에 저장합니다.

```
users
- id           uuid        PK, gen_random_uuid()
- email        varchar(255) UNIQUE NOT NULL
- password     varchar(255) NOT NULL  ← BCrypt 해시
- nickname     varchar(50)  NOT NULL
- created_at   timestamptz  NOT NULL, now()
- updated_at   timestamptz  NOT NULL, now()
```

### Spring Security 바인딩

Java 클래스: `com.ssafy.salmanhae.model.dto.auth.User implements UserDetails`

| UserDetails 메서드 | 반환값 |
| --- | --- |
| `getUsername()` | `email` (Spring Security 내부 식별자) |
| `getPassword()` | BCrypt 해시된 password |
| `getAuthorities()` | `[ROLE_USER]` |
| `isAccountNonExpired()` / `isEnabled()` 등 | 항상 `true` (별도 잠금·만료 미구현) |

`JwtAuthenticationFilter`는 토큰에서 email을 꺼내 `CustomUserDetailsService.loadUserByUsername(email)`로 `User` 객체를 조회하고, 이를 `UsernamePasswordAuthenticationToken`으로 감싸 `SecurityContextHolder`에 저장합니다.

---

## Wishlist — 찜하기

```
wishlist
- id
- user_id
- property_id
- created_at
```

---

## ConversationSession — 대화 세션 (1.5차)

```
conversation_session
- id
- user_id
- title
- current_intent
- summary
- created_at
- updated_at
```

---

## ConversationMessage — 대화 메시지 (1.5차)

```
conversation_message
- id
- session_id
- role                    ← user / assistant
- content
- metadata_json           ← 선택 매물 ID, 참조 법령 등
- created_at
```

---

## F-1 오프라인 매물 데이터셋

F-1 MVP는 국토교통부 실거래가 데이터를 건물 anchor의 원천으로 사용하고, 그 위에 지도 탐색용 더미 매물 데이터를 생성합니다. 이 매물은 실시간 중개 매물이 아니라 실제 건물/지역 기반의 MVP 검증용 데이터입니다. 따라서 지도, 필터, 상세 조회, 이후 시세 비교 흐름은 현실적인 주소와 거래 범위를 기준으로 테스트할 수 있습니다.

### 원천 실거래가

`transaction_history`는 국토교통부 실거래가 OpenAPI 8종을 정규화해 저장합니다.

- 아파트 전월세/매매
- 오피스텔 전월세/매매
- 연립다세대 전월세/매매
- 단독다가구 전월세/매매

MVP bootstrap 기준은 전국 최근 12개월입니다. 기존 DB 데이터는 truncate하지 않고 unique key 기준으로 누적 upsert합니다.

주요 연결 키:

- `source_api`
- `source_transaction_key`
- `property_type`
- `transaction_type`
- `legal_dong_code`
- `building_key`

`building_key`는 실거래가, 건물별 시세 통계, 생성 매물을 연결하는 anchor입니다.

### 시세 통계

`region_price_stat`는 지도 줌 레벨별 시세 표시를 위한 지역 단위 통계를 저장합니다.

- `region_level`: `SIDO`, `SIGUNGU`, `DONG`
- `region_code`: 레벨에 따라 시도 2자리, 시군구 5자리, 동 단위는 `LAWD_CD:동명`
- `property_type`
- `transaction_type`
- 평균/중앙값 보증금, 월세, 매매가
- `sample_from_ym`, `sample_to_ym`

`building_price_stat`는 실제 건물 anchor 단위의 시세 통계를 저장합니다.

- `building_key`
- `legal_dong_code`
- `property_type`
- `transaction_type`
- 평균/중앙값 보증금, 월세, 매매가
- `sample_from_ym`, `sample_to_ym`

두 통계 테이블은 API 요청 시 계산하지 않고 오프라인 파이프라인에서 미리 계산해 저장합니다.

### 생성 매물

F-1 MVP 생성 매물은 `properties`에 다음 기준으로 저장합니다.

- `source = 'MVP_SYNTHETIC'`
- `building_key`는 실거래가 anchor에서 복사
- `source_property_id`는 `building_key`와 거래 유형 기반으로 생성
- `anchor_transaction_id`는 `transaction_history.source_transaction_key`로 연결
- 좌표는 네이버 Geocoding 결과를 사용

생성 정책:

- geocoding이 성공한 건물 anchor마다 1~2개 생성
- geocoding 실패 시 실거래가 row는 유지하고 매물 생성만 skip
- 기존 DB 데이터는 삭제하지 않고 upsert

raw XML, JSONL, geocoding cache, SQL chunk 같은 파일은 로컬 파이프라인 산출물입니다. git에 커밋하지 않으며, 운영 수집 job이 같은 역할을 대체하면 삭제해도 됩니다.

## F-4 Safety Score Stored Model

`SafetyFacility` stores normalized point data from monthly safety facility ingestion. The MVP score flow uses these stored points only; it does not call public APIs during map, detail, chat, or AI analysis requests.

`PropertyScoreStat` stores precomputed per-property score data:

| Field | Meaning |
| --- | --- |
| `property_id` | Target property ID. |
| `safety_score` | Rounded weighted score from CCTV, emergency bell, security light, and police/security facility counts. |
| `price_score` | Preserved by the safety score batch; populated by price scoring when available. |
| `cctv_count_300m` | CCTV count within 300m. |
| `bell_count_300m` | Emergency bell count within 300m. |
| `light_count_300m` | Security light count within 300m. |
| `police_count_500m` | Police/security facility count within 500m. |
| `updated_at` | Last score-stat update timestamp. |

The safety score batch upserts `safety_score` and the safety count fields while preserving existing `price_score`. New score-stat rows may have `price_score = null` until the price scoring flow fills it.
