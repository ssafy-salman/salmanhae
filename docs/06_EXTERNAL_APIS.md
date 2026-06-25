# 06. EXTERNAL_APIS

## API 사용 원칙

| 방식 | 대상 | 이유 |
| --- | --- | --- |
| 프론트 직접 사용 | 네이버지도 SDK | 지도 렌더링, 확대/축소, 마커/클러스터 표시는 프론트 역할 |
| 백엔드 배치 수집 | 국토교통부 실거래가 8종 | 속도, 호출량, 장애 대응 때문에 DB 캐싱 필요 |
| 백엔드 seed/batch | 네이버지도 Geocoding API | 실거래가 주소성 정보를 지도 표시용 좌표로 변환. 사용자 요청 시점 호출 금지 |
| 백엔드 배치 수집 | 생활안전지도/재난안전 공공 API 4종 | 안전시설 데이터는 월 단위 갱신으로 충분하며 DB 저장 후 조회 |
| 백엔드 seed 생성 | 매물 데이터 | F-1 MVP는 실거래가에서 추출한 건물 anchor와 지오코딩 좌표를 기반으로 더미 매물을 생성하고, 운영 단계에서는 제휴 피드 또는 합법적으로 확보한 매물 데이터를 초기 저장 후 DB 데이터로 사용 |
| AI 서비스 (LangGraph) | 딥서치 API | 뉴스 RAG용 최신 부동산 뉴스 수집 (1.5차) |
| 백엔드 API 호출 | 국토부 공시가격 API | HUG 간이 계산용 (1.5차) |

WMS 기반 안전 레이어는 MVP에서 제외하고 이후 확장으로 미룹니다.

---

## 실거래가 API (국토교통부)

| 거래 유형 | 주택 유형 | 데이터명 | 링크 | 활용 |
| --- | --- | --- | --- | --- |
| 전월세 | 아파트 | 국토교통부_아파트 전월세 실거래가 자료 (XML) | https://www.data.go.kr/data/15126474/openapi.do | 지역 평균, 시세 비교, 가격 분석 |
| 전월세 | 오피스텔 | 국토교통부_오피스텔 전월세 실거래가 자료 (XML) | https://www.data.go.kr/data/15126475/openapi.do | 지역 평균, 시세 비교, 가격 분석 |
| 전월세 | 연립/다세대 | 국토교통부_연립다세대 전월세 실거래가 자료 (XML) | https://www.data.go.kr/data/15126473/openapi.do | 지역 평균, 시세 비교, 가격 분석 |
| 전월세 | 단독/다가구 | 국토교통부_단독/다가구 전월세 실거래가 자료 (XML) | https://www.data.go.kr/data/15126472/openapi.do | 지역 평균, 시세 비교, 가격 분석 |
| 매매 | 아파트 | 국토교통부_아파트 매매 실거래가 상세 자료 (XML) | https://www.data.go.kr/data/15126468/openapi.do | 지역 평균, 시세 비교, 가격 분석 |
| 매매 | 오피스텔 | 국토교통부_오피스텔 매매 실거래가 자료 (XML) | https://www.data.go.kr/data/15126464/openapi.do | 지역 평균, 시세 비교, 가격 분석 |
| 매매 | 연립/다세대 | 국토교통부_연립다세대 매매 실거래가 자료 (XML) | https://www.data.go.kr/data/15126467/openapi.do | 지역 평균, 시세 비교, 가격 분석 |
| 매매 | 단독/다가구 | 국토교통부_단독/다가구 매매 실거래가 자료 (XML) | https://www.data.go.kr/data/15126465/openapi.do | 지역 평균, 시세 비교, 가격 분석 |

수집 주기: 매일 새벽 배치. 저장 테이블: `transaction_history`.

실거래가 배치 후 시/도, 시/군/구, 읍/면/동 단위 평균을 계산해 지도 줌 레벨별 표시 데이터로 사용합니다.
F-1 MVP 단계에서는 `scripts/data_pipeline/pipeline.py`가 OpenAPI 응답을 가져와 정규화하고, 통계와 생성 매물을 Supabase에 직접 upsert합니다.

---

## 안전 API

| 분류 | 데이터명 | 형식 | 링크 | 활용 |
| --- | --- | --- | --- | --- |
| 생활안전지도 | CCTV 위치 | CSV | https://www.data.go.kr/data/15075538/fileData.do# | 지도 오버레이, 안전 점수 계산 |
| 생활안전지도 | 안전 비상벨 위치 정보 | XML/JSON | https://www.data.go.kr/data/15155046/openapi.do | 지도 오버레이, 안전 점수 계산 |
| 재난안전데이터공유플랫폼 | 보안등 | JSON | https://www.data.go.kr/data/15149415/openapi.do | 지도 오버레이, 야간 보행 안전 점수 |
| 생활안전지도 | 치안안전시설 | XML | https://www.data.go.kr/data/15101889/openapi.do | 지도 오버레이, 안전 점수 계산 |

수집 주기: 월 1회 배치. 저장 테이블: `safety_facility`.

---

## 매물 데이터

| 대상 | 방식 | 저장 방식 | 활용 |
| --- | --- | --- | --- |
| F-1 MVP 더미 매물 | 실거래가 건물 anchor + 지오코딩 좌표 + 실거래가 범위 기반 가격 생성 | `properties`에 저장 | 지도 매물 마커, 매물 상세, 필터, AI 추천 흐름 검증 |
| 운영 매물 | 제휴 피드, 중개사/임대인 등록, 합법 검토된 수집 데이터 | `properties`에 저장. 원천별 중복 기준 적용 | 지도 매물 마커, 매물 상세, AI 추천 |

프론트엔드는 항상 Spring Boot REST API만 호출합니다. 운영 단계에서 네이버부동산 등 외부 원천 수집을 도입하려면 대상 페이지 구조 변경, 이용약관, robots 정책, 법적 리스크를 별도 검토합니다.

---

## 지도 API

| API | 활용 |
| --- | --- |
| 네이버지도 SDK | 지도 렌더링, 확대/축소, 마커, 클러스터, 지역 평균 오버레이 표시 |
| 네이버지도 Geocoding API | seed/batch 시점에 건물명·지번 주소를 위도/경도로 변환 |

지도 표시 데이터는 네이버지도 SDK가 직접 외부 공공 API를 호출하지 않고, Spring Boot의 지도 조회 API에서 DB 기반으로 내려줍니다.
Geocoding 호출에는 `NAVER_MAPS_CLIENT_ID`, `NAVER_MAPS_CLIENT_SECRET` 환경변수를 사용합니다. 프론트 지도 SDK는 `VITE_NAVER_MAP_CLIENT_ID`만 사용하며 secret을 브라우저에 노출하지 않습니다.

### 줌 레벨별 표시 정책

| 지도 범위 | 표시 데이터 | 설명 |
| --- | --- | --- |
| 시/도 수준 | 시/도 실거래가 평균 | 넓은 범위에서는 광역 단위 평균 가격만 표시 |
| 시/군/구 수준 | 시/군/구 실거래가 평균 | 중간 범위에서는 기초지자체 단위 평균 가격 표시 |
| 읍/면/동 수준 | 읍/면/동 실거래가 평균 | 동네 단위 평균 가격 표시 |
| 상세 확대 | 매물 정보 | 개별 매물 마커 표시 |
| 상세 확대 + 밀집 지역 | 원형 클러스터 | 일정 수 이상 매물이 몰리면 원형 묶음으로 표시 |

---

## AI / 뉴스 API

| API | 활용 | 단계 |
| --- | --- | --- |
| 딥서치 API | 부동산 정책·시장 동향 뉴스 수집 → pgvector 인덱싱 → 뉴스 RAG | 1.5차 |

---

## 공시가격 API

| API | 활용 | 단계 |
| --- | --- | --- |
| 국토부 공시가격 API | HUG 간이 계산 시 공시가격 자동 조회 | 1.5차 |

---

## 데이터 저장 전략

| 데이터 | 저장 여부 | 테이블 | 갱신 주기 |
| --- | --- | --- | --- |
| F-1 MVP 더미 매물 | 저장 | `properties` | 오프라인 파이프라인으로 생성 후 Supabase upsert |
| 운영 매물 | 저장 | `properties` | 제휴/등록/합법 수집 정책 확정 후 수동 또는 주기 갱신 |
| 전월세 실거래가 | 저장 | `transaction_history` | MVP는 전국 최근 12개월 오프라인 upsert, 운영은 주기 갱신 |
| 매매 실거래가 | 저장 | `transaction_history` | MVP는 전국 최근 12개월 오프라인 upsert, 운영은 주기 갱신 |
| 지역별 실거래가 평균 | 저장 | `region_price_stat` | 오프라인 파이프라인에서 사전 계산 |
| 건물별 실거래가 통계 | 저장 | `building_price_stat` | 오프라인 파이프라인에서 사전 계산 |
| CCTV | 저장 | `safety_facility` | 월 1회 |
| 안전비상벨 | 저장 | `safety_facility` | 월 1회 |
| 보안등/방범등 | 저장 | `safety_facility` | 월 1회 |
| 치안시설 | 저장 | `safety_facility` | 월 1회 |
| 뉴스 (딥서치) | pgvector 저장 | `news_embeddings` | 주기적 재인덱싱 (1.5차) |

---

## 데이터 품질 주의 사항

- 공공데이터는 제공 기관마다 좌표계, 주소 형식, 컬럼명이 다를 수 있습니다.
- 좌표가 없는 실거래가 데이터는 seed/batch 생성 시점에 지오코딩하고, 사용자 요청 시점에는 DB에 저장된 좌표만 사용합니다.
- 같은 시설이 여러 원천에 중복될 수 있으므로 `source`, `source_id`, `type`, `latitude`, `longitude`를 함께 보고 중복을 줄입니다.
- 실거래가는 신고와 공개 사이에 시차가 있으므로 신고된 공개 데이터 기준으로 안내합니다.
- F-1 더미 매물은 `source = MVP_SYNTHETIC`으로 저장하고, `building_key`로 실거래가 건물 anchor와 연결합니다.
- 운영 매물은 원천별 중복 등록 가능성이 있으므로 `source`, `source_property_id`, `source_url`, `crawled_at` 기준으로 중복을 줄입니다.

## F-4 Safety Facility Source Clients

Phase 3 adds source clients and parsers for safety-facility ingestion. The batch job must load
these APIs, normalize them into `safety_facility`, and later calculate scores from stored DB rows
instead of calling public APIs during user requests.

| Source | Type | Default endpoint/config | Format | Notes |
| --- | --- | --- | --- | --- |
| CCTV OpenAPI | `CCTV` | `safety.data.cctv-url`, default `https://apis.data.go.kr/1741000/cctv_info/info` | JSON | Uses `safety.data.public-service-key` or `PUBLIC_DATA_SERVICE_KEY`. The `/info` endpoint exposes `WGS84_LAT` and `WGS84_LOT`; `numOfRows` is capped at 100. |
| Emergency bell OpenAPI | `EMERGENCY_BELL` | `safety.data.emergency-bell-url` | JSON | Endpoint is environment-specific; uses `safety.data.public-service-key` or `PUBLIC_DATA_SERVICE_KEY`. The `/info` endpoint exposes `WGS84_LAT` and `WGS84_LOT`; `numOfRows` is capped at 100. |
| Security light OpenAPI | `SECURITY_LIGHT` | `safety.data.security-light-url` | JSON | Endpoint is environment-specific; uses `safety.data.security-light-service-key` or `SECURITY_LIGHT_SERVICE_KEY`. `body[]` rows expose `XMAP_CRTS` and `YMAP_CRTS` in Web Mercator and are converted to WGS84 before storage. |
| SafetyMap police facility IF_0036 | `POLICE` | `safety.data.safemap-police-url`, default `https://www.safemap.go.kr/openapi2/IF_0036` | XML | Uses `safety.data.safemap-service-key` or `SAFEMAP_SERVICE_KEY`; `x` is longitude and `y` is latitude. |

Common paging config: `safety.data.page-size` defaults to `1000`. Emergency bell requests are capped at `100` because the API rejects larger `numOfRows` values.

## F-4 Safety API Operations

The F-4 MVP uses public safety APIs only in backend batch jobs. Runtime user requests read Spring Boot DB-backed APIs only.

| Data | Public source format | Stored table | Runtime use |
| --- | --- | --- | --- |
| CCTV | JSON | `safety_facility` | Map overlay and safety score count within 300m. |
| Emergency bell | JSON or XML depending on configured endpoint | `safety_facility` | Safety score count within 300m. |
| Security light | JSON | `safety_facility` | Safety score count within 300m. |
| Police/security facility | SafetyMap XML | `safety_facility` | Safety score count within 500m. |

Operators must configure service keys as environment variables:

- `PUBLIC_DATA_SERVICE_KEY` for public-data endpoints such as emergency bell that require a service key.
- `SECURITY_LIGHT_SERVICE_KEY` for the security light endpoint when it uses a separate issued key.
- `SAFEMAP_SERVICE_KEY` for the SafetyMap police/security facility source.

Operators can override source endpoints and paging with non-secret environment variables:

- `SAFETY_DATA_CCTV_URL` should point at the CCTV `/info` base URL without query parameters or `serviceKey` when overriding the default.
- `SAFETY_DATA_EMERGENCY_BELL_URL` should point at the actual emergency bell `/info` base URL without query parameters or `serviceKey`.
- `SAFETY_DATA_SECURITY_LIGHT_URL` should be the security light base URL without query parameters or `serviceKey`.
- `SAFETY_DATA_PAGE_SIZE=100` is recommended for the shared batch setting.

Do not expose these keys to the frontend. The frontend and backend-ai call Spring Boot APIs only. WMS-based safety layers are not part of the MVP stored-data flow.
