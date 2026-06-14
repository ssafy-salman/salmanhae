# 07. DOMAIN_MODEL

## 모델 요약

| 모델 | 역할 |
| --- | --- |
| `Property` | 지도에 표시할 더미 매물 기본 정보 |
| `TransactionHistory` | 국토교통부 실거래가 (전월세 + 매매 8종) |
| `SafetyFacility` | CCTV, 비상벨, 보안등, 치안시설 좌표 |
| `PropertyScoreStat` | 매물별 안전·가격 점수 사전 계산 통계 |
| `User` | 로그인 사용자 정보 (Supabase Auth 연동) |
| `Wishlist` | 찜한 매물 |
| `ConversationSession` | AI 에이전트 대화 세션 (1.5차) |
| `ConversationMessage` | 대화 메시지 원문 (1.5차) |

---

## Enum 기준

| Enum | 값 | 설명 |
| --- | --- | --- |
| `PropertyType` | `ONE_ROOM`, `OFFICETEL`, `VILLA`, `APARTMENT`, `MULTI_FAMILY` | 매물 또는 실거래가의 주택 유형 |
| `TransactionType` | `MONTHLY_RENT`, `JEONSE`, `SALE` | 월세, 전세, 매매 구분 |
| `SafetyFacilityType` | `CCTV`, `EMERGENCY_BELL`, `SECURITY_LIGHT`, `POLICE` | 안전시설 유형 |
| `ConversationIntent` | `PROPERTY_SEARCH`, `LEGAL_CONSULT`, `PRICE_ANALYSIS`, `SAFETY_ANALYSIS`, `HUG_CALC` | AI 에이전트 의도 분류 |

---

## Property — 더미 매물

```
property
- id
- building_name
- address
- road_address
- legal_dong_code
- property_type
- transaction_type
- deposit
- monthly_rent
- maintenance_fee
- area_m2
- floor
- latitude
- longitude
- description
- created_at
```

---

## TransactionHistory — 실거래가

전월세 4종 + 매매 4종 모두 동일 테이블에 저장합니다.

```
transaction_history
- id
- property_type
- transaction_type        ← MONTHLY_RENT / JEONSE / SALE
- legal_dong_code
- contract_year_month
- contract_day
- deposit
- monthly_rent            ← 매매는 null
- sale_price              ← 매매가 (전월세는 null)
- area_m2
- floor
- build_year
- source_api
- created_at
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

Supabase Auth가 인증을 관리하며, Spring Boot DB에는 최소 정보만 저장합니다.

```
users
- id                      ← Supabase Auth UUID와 동일
- email
- nickname
- created_at
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
