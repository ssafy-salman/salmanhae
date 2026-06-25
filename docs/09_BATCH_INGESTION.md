# 09. BATCH_INGESTION

## 배치가 필요한 이유

외부 공공 API와 수집 원천을 사용자 요청마다 실시간 호출하면 응답 속도가 느려지고 장애에 취약합니다. 실거래가, 안전시설, 매물 데이터는 백엔드 수집 작업이나 seed 적재로 미리 DB에 저장하고, 클라이언트 요청 시에는 DB만 조회합니다.

---

## 실거래가 수집

| 항목 | 내용 |
| --- | --- |
| 대상 API | 국토교통부 실거래가 공공 API 8종 (전월세 4종 + 매매 4종) |
| 주택 유형 | 아파트, 오피스텔, 연립/다세대, 단독/다가구 |
| 수집 주기 | 매일 새벽 배치 |
| 저장 테이블 | `transaction_history` |
| 활용 | 지도 지역 평균, 매물 상세 시세 비교, 시세 분석, 가격 점수 계산 |

운영 구현에서는 Spring Batch 또는 Scheduler가 국토교통부 API를 호출하고 XML 응답을 즉시 파싱해 `transaction_history`에 저장합니다. XML 원문 파일을 저장소에 커밋하지 않습니다. 현재 MVP는 `scripts/data_pipeline/pipeline.py`로 전국 최근 12개월 데이터를 오프라인 수집한 뒤 Supabase에 직접 upsert합니다.

### 실거래가 매칭 기준 (MVP)

| 우선순위 | 기준 | 설명 |
| --- | --- | --- |
| 1 | 건물 anchor | 매물의 `building_key`와 같은 실거래가 row를 최우선 조회 |
| 2 | 법정동 코드 | 매물의 `legal_dong_code`와 같은 법정동의 거래를 우선 조회 |
| 3 | 주택 유형 | 매물의 `property_type`과 같은 유형의 거래를 우선 사용 |
| 4 | 전용면적 | 매물 `area_m2` 기준 ±10㎡ 범위를 유사 거래로 판단 |
| 5 | 거래 기간 | 기본 최근 3년 거래 사용 |
| 6 | 거래 종류 | 전세는 보증금 중심, 월세는 보증금과 월세를 함께 비교 |

### 지역 평균 계산

실거래가 수집 후 지도 줌 레벨별 표시를 위해 지역 평균을 계산합니다.

```
transaction_history 적재
→ 시/도 평균 계산
→ 시/군/구 평균 계산
→ 읍/면/동 평균 계산
→ region_price_stat 저장
```

| 지역 레벨 | 지도 표시 |
| --- | --- |
| `SIDO` | 시/도 실거래가 평균 |
| `SIGUNGU` | 시/군/구 실거래가 평균 |
| `DONG` | 읍/면/동 실거래가 평균 |

MOLIT 실거래가 API의 `LAWD_CD`는 시군구 5자리 코드이므로, 동 단위 `region_code`는 `LAWD_CD:동명` 형식의 composite key를 사용합니다.

---

## 안전시설 수집

| 항목 | 내용 |
| --- | --- |
| 대상 데이터 | CCTV, 안전비상벨, 보안등/방범등, 치안시설 (파출소·지구대) |
| 수집 주기 | 월 1회 배치 |
| 저장 테이블 | `safety_facility` |
| 활용 | 지도 오버레이, 안전 요약, 안전 점수 계산 |

WMS 기반 범죄주의구간 레이어는 MVP에서 제외합니다.

---

## 매물 수집

| 항목 | 내용 |
| --- | --- |
| F-1 MVP 대상 | 실거래가 건물 anchor 기반 더미 매물 |
| F-1 MVP 방식 | 오프라인 파이프라인이 실거래가 정규화, 지오코딩, 통계/매물 생성 후 Supabase에 직접 upsert |
| 운영 대상 | 제휴 매물 피드, 중개사/임대인 등록, 합법 검토된 수집 데이터 |
| 운영 방식 | 원천 정책 확정 후 DB 저장 |
| 저장 테이블 | `properties` |
| 활용 | 지도 매물 마커, 매물 상세, AI 매물 추천 |

F-1 MVP의 `MVP_SYNTHETIC` 매물은 실거래가에서 추출한 실제 건물·지역 정보를 anchor로 사용합니다. 매물 가격은 같은 건물 또는 같은 법정동·유형·면적대 실거래가의 중앙값을 기준으로 생성합니다. 운영 매물 자동 갱신 주기는 원천 계약, 페이지 구조 변경 리스크, 약관/법적 검토가 끝난 뒤 확정합니다.

### F-1 오프라인 생성 흐름

```
국토교통부 실거래가 OpenAPI 호출
→ XML 응답을 로컬 `data/pipeline/raw/`에 임시 저장
→ `data/pipeline/normalized/transaction_history.jsonl` 생성
→ building_key 기준 건물 anchor 추출
→ 네이버 Geocoding 캐시로 latitude/longitude 부여
→ 지역/건물별 시세 통계 JSONL 생성
→ 실거래가 중앙값 기준 MVP 더미 매물 JSONL 생성
→ Supabase에 직접 upsert
```

오프라인 적재 명령:

```bash
python scripts/data_pipeline/pipeline.py run --months 12 --scope nationwide --migrate-db --load-db
```

로컬 raw XML, JSONL, geocoding cache는 git에 올리지 않습니다. 전국 수집에는 `data/reference/lawd-codes.csv`가 필요하며, 이 파일은 행정표준코드 기반 시군구 목록으로 로컬에서 준비합니다.

### F-1 오프라인 산출물 보존 정책

`data/raw/`, `data/seed/`, `data/pipeline/`, `database/seed/` 아래의 생성 산출물은 레포에 보관하지 않습니다. Supabase에는 파이프라인이 직접 upsert하고, 재현이 필요하면 같은 명령을 다시 실행합니다.

이 산출물은 운영 수집 방식이 아니라 MVP bootstrap을 위한 임시 결과입니다. 운영 단계에서 주기적 최신화가 필요해지면 같은 정규화/적재 로직을 Spring Scheduler 또는 별도 job으로 옮기고, 로컬 산출물은 계속 gitignore 대상으로 유지합니다.

---

## 점수 계산 배치

안전시설과 실거래가가 저장된 뒤 매물별 점수를 계산합니다.

```
매물 기준 반경 검색
→ CCTV/비상벨/보안등/치안시설 개수 계산
→ 안전 점수 계산 (항목별 0~100 정규화 → 가중 평균)
→ 실거래가 기반 가격 점수 계산
→ property_score_stat 저장
```

가격 점수는 실거래가 배치 후 매일 재계산할 수 있습니다. 안전 점수는 안전시설 월 1회 갱신 후 재계산합니다.

### 안전 점수 가중치

| 항목 | 반경 | 가중치 |
| --- | --- | --- |
| CCTV | 300m | 30% |
| 안전비상벨 | 300m | 25% |
| 보안등/방범등 | 300m | 25% |
| 치안시설 (파출소·지구대) | 500m | 20% |

---

## 뉴스 인덱싱 (1.5차)

| 항목 | 내용 |
| --- | --- |
| 대상 | 딥서치 API 기반 부동산 정책·시장 동향 뉴스 |
| 처리 | 청킹 → 임베딩 → pgvector 저장 |
| 수집 주기 | 주기적 재인덱싱 (최신성 유지) |
| 활용 | F-4 뉴스 RAG 응답 생성 |

---

## MVP 오프라인 적재 방식

F-1 MVP에서는 Spring Batch/Scheduler를 바로 운영하지 않고, 오프라인 데이터 파이프라인으로 전국 최근 12개월 실거래가와 MVP 더미 매물을 미리 생성해 Supabase에 upsert합니다.

```bash
python scripts/data_pipeline/pipeline.py run --months 12 --scope nationwide --migrate-db --load-db
```

정책은 다음과 같습니다.

- 수집 범위: 전국 최근 12개월
- 대상 API: 아파트, 오피스텔, 연립/다세대, 단독/다가구의 매매와 전월세 전체
- 실거래가: `transaction_history`에 누적 upsert
- 시세 통계: `region_price_stat`, `building_price_stat`에 사전 계산 upsert
- 매물 데이터: 실거래가 건물 anchor당 1~2개 `MVP_SYNTHETIC` 매물 생성 후 `properties`에 upsert
- geocoding 실패 정책: 거래 데이터는 저장하고, 좌표가 없는 건물은 매물 생성만 skip
- 기존 DB 데이터 처리: truncate 없이 unique key 기준 누적 upsert

이 방식은 데모/MVP에서 안정적인 지도 매물 탐색과 시세 비교를 제공하기 위한 bootstrap 방식입니다. 운영 단계에서 주기적 최신화가 필요해지면 같은 정규화/적재 로직을 Spring Scheduler 또는 별도 job으로 옮깁니다.

## F-4 Safety Facility Ingestion Scheduler

Phase 4 wires the safety source clients into a Spring service and scheduler. The scheduler is
disabled by default so local and test profiles never call public APIs unexpectedly.

| Config | Default | Description |
| --- | --- | --- |
| `safety.ingestion.scheduler.enabled` / `SAFETY_INGESTION_SCHEDULER_ENABLED` | `false` | Enables the monthly scheduler when set to `true`. |
| `safety.ingestion.scheduler.cron` / `SAFETY_INGESTION_SCHEDULER_CRON` | `0 0 3 1 * *` | Runs at 03:00 on the first day of every month. |
| `safety.ingestion.scheduler.zone` / `SAFETY_INGESTION_SCHEDULER_ZONE` | `Asia/Seoul` | Scheduler timezone. |

`SafetyFacilityIngestionService` runs each source independently. If one source fails, the failure is
logged and recorded in `SafetyFacilityIngestionResult`, while the remaining sources continue. Stored
rows are accumulated through `SafetyFacilityDao.upsertAll`, so rerunning the batch is idempotent for
the unique `(type, source, source_id)` safety facility key.

## Phase 5 Property Safety Score Calculation Scheduler

Phase 5 recalculates `property_score_stat.safety_score` from stored `safety_facility` rows. It never
calls public APIs during user requests; user-facing safety summary APIs read only precomputed DB rows.

| Metric | Radius | Full-score cap | Weight |
| --- | --- | --- | --- |
| CCTV | 300m | 10 facilities | 30% |
| Emergency bell | 300m | 3 facilities | 25% |
| Security light | 300m | 20 facilities | 25% |
| Police/security facility | 500m | 1 facility | 20% |

Each metric is normalized as `min(count / full-score-cap, 1.0)`, then multiplied by its weight. The
weighted total is rounded to the nearest integer and clamped to `0..100`. If no facility data exists
for a metric, that metric contributes `0`.

| Config | Default | Description |
| --- | --- | --- |
| `safety.score.scheduler.enabled` / `SAFETY_SCORE_SCHEDULER_ENABLED` | `false` | Enables the monthly safety score scheduler when set to `true`. |
| `safety.score.scheduler.cron` / `SAFETY_SCORE_SCHEDULER_CRON` | `0 30 3 1 * *` | Runs after the safety facility refresh by default. |
| `safety.score.scheduler.zone` / `SAFETY_SCORE_SCHEDULER_ZONE` | `Asia/Seoul` | Scheduler timezone. |

The upsert updates `safety_score` and safety facility counts while preserving existing `price_score`.
New rows are inserted with `price_score = null` until a price scoring batch fills that value.

## Phase 6 Safety Batch Runbook

F-4 safety data is now a two-step stored-data flow:

1. Safety facility ingestion reads configured public API sources and upserts normalized point data into `safety_facility`.
2. Property safety score recalculation reads only `safety_facility` and active geocoded `properties`, then upserts `property_score_stat`.

Recommended monthly production order:

```bash
SAFETY_INGESTION_SCHEDULER_ENABLED=true
SAFETY_SCORE_SCHEDULER_ENABLED=true
```

Default schedule in `Asia/Seoul`:

| Step | Default cron | Purpose |
| --- | --- | --- |
| Safety facility ingestion | `0 0 3 1 * *` | Refresh CCTV, emergency bell, security light, and police/security facility point rows. |
| Property safety score recalculation | `0 30 3 1 * *` | Recalculate per-property safety score and facility counts after ingestion. |

Required keys must be supplied through environment variables or platform secret settings, never committed:

| Environment variable | Used by |
| --- | --- |
| `PUBLIC_DATA_SERVICE_KEY` | Public data sources such as emergency bell and security light when endpoint URLs require a service key. |
| `SAFEMAP_SERVICE_KEY` | SafetyMap police/security facility XML source. |

Verification checklist:

- `GET /api/v1/safety/facilities` returns stored point rows from `safety_facility`.
- `GET /api/v1/properties/{id}/safety-summary?radius=500` returns `safetyScore`, `priceScore`, and count fields from `property_score_stat`.
- Backend AI `SAFETY_ANALYSIS` calls Spring Boot `safety-summary` and surfaces the precomputed score/count fields in the analysis card and answer.
- User-facing APIs must not call public safety APIs directly.

MVP scope is point-data safety facilities only. WMS-only safety layers remain excluded from this batch flow and should be handled as a separate future map-layer feature.
