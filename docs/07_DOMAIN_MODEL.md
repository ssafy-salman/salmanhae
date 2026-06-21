# 07. DOMAIN_MODEL

## 모델 요약

| 모델 | 역할 |
| --- | --- |
| `Property` | 지도에 표시할 매물 후보 기본 정보. F-1 MVP는 실거래가 건물 anchor 기반 더미 매물 seed를 사용하고, 운영 단계에서는 합법적으로 확보한 매물 데이터를 같은 구조로 저장 |
| `TransactionHistory` | 국토교통부 실거래가 (전월세 + 매매 8종). F-1에서는 건물 anchor와 가격 기준 원천으로도 사용 |
| `SafetyFacility` | CCTV, 비상벨, 보안등, 치안시설 좌표 |
| `PropertyScoreStat` | 매물별 안전·가격 점수 사전 계산 통계 |
| `RegionPriceStat` | 지도 줌 레벨별 표시를 위한 지역 단위 실거래가 평균 |
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
| `RegionLevel` | `SIDO`, `SIGUNGU`, `EUPMYEONDONG` | 지도 평균 표시용 행정구역 레벨 |
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
- 정규화 입력은 `data/seed/transaction-history.seed.json`, 지오코딩 캐시는 `data/seed/geocoding-cache.json`, 생성 결과는 `data/seed/properties.seed.json`에 둡니다.
- Supabase 적용 SQL은 `database/migrations/202606160001_create_properties.sql`, seed SQL은 `database/seed/transaction_history_seed.sql`과 `database/seed/properties_seed.sql`에 둡니다.

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
- region_level            ← SIDO / SIGUNGU / EUPMYEONDONG
- region_code
- region_name
- property_type
- transaction_type
- avg_deposit
- avg_monthly_rent
- avg_sale_price
- transaction_count
- latitude
- longitude
- calculated_at
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
