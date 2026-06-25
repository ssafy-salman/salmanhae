# ERD

## 1. 작성 기준

- 기준 시점: 2026-06-25
- 기준 데이터: 실제 Supabase `public` schema 메타데이터 조회 결과
- 조회 범위: `information_schema.tables`, `information_schema.columns`, `information_schema.table_constraints`, `pg_indexes`, `pg_class`
- 비고: `schema_migrations`는 실제 DB에 존재하지만 마이그레이션 관리용 메타 테이블이므로 비즈니스 ERD에서는 제외하고 별도 표로 분리한다.

## 2. 실제 테이블 목록

| 테이블 | 용도 | 추정 row 수 |
| --- | --- | ---: |
| `users` | Spring Security 사용자 인증 정보 | -1 |
| `transaction_history` | 국토교통부 실거래가 정규화 데이터 | 47,273 |
| `properties` | 지도에 표시할 매물 후보 | 8,305 |
| `region_price_stat` | 지도 줌 레벨별 지역 단위 시세 통계 | 20,595 |
| `building_price_stat` | 건물 anchor 단위 시세 통계 | 11,182 |
| `safety_facility` | CCTV, 비상벨, 보안등, 치안시설 좌표 | 2,470 |
| `property_score_stat` | 매물별 안전/가격 점수 사전 계산 결과 | 8,305 |
| `legal_document_chunks` | 법률 RAG chunk 및 embedding | 117 |
| `schema_migrations` | DB migration 적용 이력 | -1 |

`row 수`는 PostgreSQL `pg_class.reltuples` 기반 추정값이다.

## 3. 실제 비즈니스 ERD

```mermaid
erDiagram
    TRANSACTION_HISTORY ||--o{ PROPERTIES : anchors
    PROPERTIES ||--o| PROPERTY_SCORE_STAT : has_score

    TRANSACTION_HISTORY }o--o{ REGION_PRICE_STAT : aggregates_region_stats
    TRANSACTION_HISTORY }o--o{ BUILDING_PRICE_STAT : aggregates_building_stats
    SAFETY_FACILITY }o--o{ PROPERTY_SCORE_STAT : precomputed_into

    USERS {
        uuid id PK
        varchar email UK
        varchar password
        varchar nickname
        timestamptz created_at
        timestamptz updated_at
    }

    TRANSACTION_HISTORY {
        bigint id PK
        varchar source_api UK
        varchar source_transaction_key UK
        varchar property_type
        varchar transaction_type
        varchar sido
        varchar sigungu
        varchar dong
        varchar legal_dong_code
        varchar jibun
        varchar building_name
        varchar building_key
        varchar contract_year_month
        integer contract_day
        bigint deposit
        integer monthly_rent
        bigint price
        numeric area_m2
        integer floor
        integer build_year
        jsonb raw_json
        timestamptz created_at
    }

    PROPERTIES {
        bigint id PK
        varchar title
        varchar building_name
        varchar building_key
        bigint anchor_transaction_id FK
        varchar property_type
        varchar transaction_type
        bigint deposit
        integer monthly_rent
        bigint price
        integer maintenance_fee
        numeric area_m2
        integer floor
        integer total_floor
        text address
        text road_address
        varchar sido
        varchar sigungu
        varchar dong
        varchar legal_dong_code
        numeric latitude
        numeric longitude
        varchar geocoding_provider
        varchar geocoding_quality
        timestamptz geocoded_at
        text description
        varchar source UK
        varchar source_property_id UK
        text source_url
        timestamptz crawled_at
        date registered_at
        boolean is_active
        timestamptz created_at
        timestamptz updated_at
    }

    PROPERTY_SCORE_STAT {
        bigint property_id PK_FK
        integer safety_score
        integer price_score
        integer cctv_count_300m
        integer bell_count_300m
        integer light_count_300m
        integer police_count_500m
        timestamptz created_at
        timestamptz updated_at
    }

    REGION_PRICE_STAT {
        bigint id PK
        varchar region_level UK
        varchar region_code UK
        varchar sido
        varchar sigungu
        varchar dong
        varchar property_type UK
        varchar transaction_type UK
        bigint avg_deposit
        bigint median_deposit
        integer avg_monthly_rent
        integer median_monthly_rent
        bigint avg_price
        bigint median_price
        integer transaction_count
        varchar sample_from_ym
        varchar sample_to_ym
        timestamptz created_at
        timestamptz updated_at
    }

    BUILDING_PRICE_STAT {
        bigint id PK
        varchar building_key UK
        varchar building_name
        varchar sido
        varchar sigungu
        varchar dong
        varchar legal_dong_code
        varchar property_type UK
        varchar transaction_type UK
        bigint avg_deposit
        bigint median_deposit
        integer avg_monthly_rent
        integer median_monthly_rent
        bigint avg_price
        bigint median_price
        integer transaction_count
        varchar sample_from_ym
        varchar sample_to_ym
        timestamptz created_at
        timestamptz updated_at
    }

    SAFETY_FACILITY {
        bigint id PK
        varchar type UK
        varchar name
        text address
        numeric latitude
        numeric longitude
        varchar source UK
        varchar source_id UK
        text description
        timestamptz created_at
        timestamptz updated_at
    }

    LEGAL_DOCUMENT_CHUNKS {
        bigint id PK
        varchar law_id
        varchar law_name
        varchar article_no
        varchar article_title
        date effective_date
        varchar source_name
        text source_url
        integer chunk_index
        text content
        char content_hash UK
        vector embedding
        jsonb metadata_json
        timestamptz created_at
        timestamptz updated_at
    }
```

## 4. 실제 Foreign Key

| From | To | 관계 | 삭제 규칙 |
| --- | --- | --- | --- |
| `properties.anchor_transaction_id` | `transaction_history.id` | 매물 seed가 기준 실거래가 row를 참조 | `NO ACTION` |
| `property_score_stat.property_id` | `properties.id` | 매물별 점수 row가 매물 row를 참조 | `CASCADE` |

`region_price_stat`, `building_price_stat`, `safety_facility`, `legal_document_chunks`, `users`는 실제 DB상 다른 비즈니스 테이블과 FK가 없다. 통계 테이블은 `legal_dong_code`, `building_key`, `property_type`, `transaction_type` 같은 업무 키로 조회/집계에 연결된다.

## 5. 주요 Unique/Index

| 테이블 | 제약/인덱스 | 컬럼 |
| --- | --- | --- |
| `users` | `users_email_key` | `email` |
| `transaction_history` | `transaction_history_source_unique` | `source_api`, `source_transaction_key` |
| `transaction_history` | `idx_transaction_history_building` | `building_key`, `contract_year_month desc` |
| `transaction_history` | `idx_transaction_history_match` | `legal_dong_code`, `property_type`, `transaction_type`, `area_m2`, `contract_year_month desc` |
| `properties` | `properties_source_unique` | `source`, `source_property_id` |
| `properties` | `idx_properties_viewport` | `is_active`, `longitude`, `latitude` |
| `properties` | `idx_properties_filters` | `transaction_type`, `property_type`, `deposit`, `price` |
| `properties` | `idx_properties_region` | `sido`, `sigungu`, `dong` |
| `properties` | `idx_properties_building` | `building_key` |
| `region_price_stat` | `region_price_stat_unique` | `region_level`, `region_code`, `property_type`, `transaction_type` |
| `building_price_stat` | `building_price_stat_unique` | `building_key`, `property_type`, `transaction_type` |
| `building_price_stat` | `idx_building_price_stat_region` | `legal_dong_code`, `property_type`, `transaction_type` |
| `safety_facility` | `uq_safety_facility_source` | `type`, `source`, `source_id` |
| `safety_facility` | `idx_safety_facility_bounds` | `longitude`, `latitude` |
| `safety_facility` | `idx_safety_facility_type_bounds` | `type`, `longitude`, `latitude` |
| `legal_document_chunks` | `legal_document_chunks_content_hash_unique` | `content_hash` |
| `legal_document_chunks` | `idx_legal_document_chunks_embedding` | `embedding vector_cosine_ops`, `embedding is not null` |
| `legal_document_chunks` | `idx_legal_document_chunks_metadata` | `metadata_json` GIN |

## 6. 실제 스키마와 기존 초안 차이

| 항목 | 기존 초안 | 실제 Supabase 확인 결과 |
| --- | --- | --- |
| `wishlist` | ERD에 포함 | 실제 `public` 테이블 없음 |
| `conversation_session` | ERD에 포함 | 실제 `public` 테이블 없음 |
| `conversation_message` | ERD에 포함 | 실제 `public` 테이블 없음 |
| `schema_migrations` | 미표기 | 실제 존재, migration 관리용 테이블 |
| 주요 관계 | 기획 모델 일부 포함 | 실제 FK는 `properties -> transaction_history`, `property_score_stat -> properties` 2개 |

## 7. 확장 예정 모델

아래 모델은 PRD/API 명세에는 있으나 2026-06-25 기준 실제 Supabase `public` schema에는 없다. 제출 문서에서는 실제 ERD가 아니라 향후 확장 모델 또는 로드맵으로 분리한다.

| 모델 | 용도 |
| --- | --- |
| `wishlist` | 찜한 매물 |
| `conversation_session` | AI 대화 세션 |
| `conversation_message` | 대화 메시지 및 참조 메타데이터 |
