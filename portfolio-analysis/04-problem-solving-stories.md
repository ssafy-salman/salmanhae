# 문제 해결 사례

## 활용 우선순위

| 순위 | 사례 | 추천 이유 |
|---:|---|---|
| ★ 1 | 안전시설 public API의 format·인증·좌표·배포 로그 장애 대응 | backend 외부 API, batch, 장애 추적, 방어 설계를 한 번에 설명 가능 |
| ★ 2 | 법률 RAG의 stub 제거와 제한된 network fallback | RAG grounding, content-hash upsert, failure policy, testability를 설명 가능 |
| ★ 3 | 지도 aggregate와 local keyword 검색의 불일치 해결 | API contract, SQL 재사용, FE-BE 조율, automated review 반영을 설명 가능 |
| 4 | commit된 seed를 전국 범위를 계획할 수 있는 offline bootstrap pipeline으로 전환 | 공공데이터 정규화·재실행·DB 중복 방지 upsert 경험 |
| 5 | 안전 점수를 request-time 계산에서 사전 계산으로 구성 | batch·spatial query·성능 구조를 설명 가능 |
| 6 | Spring-FastAPI 분석 contract를 stub에서 실제 data로 연결 | microservice contract와 fallback을 설명 가능 |
| 7 | 멀티레포→모노레포·GitLab sync·Cloud Run deploy | 협업·배포 경계와 trade-off를 설명 가능 |
| 8 | 매물 API를 Naver map까지 연결하며 CORS·계약을 검증 | 첫 vertical slice와 test-first 접근을 설명 가능 |

이 표는 “문제 해결 서사 자체의 선명도” 순위다. 최종 포트폴리오 3개는 역량 중복을 줄이기 위해 데이터 파이프라인·Spring–FastAPI 연동·안전시설을 선택했고, 지도는 최고 점수의 대체 사례, 법률 RAG는 보조 사례로 분류했다. 최종 판단은 [`10-verified-problem-stories.md`](10-verified-problem-stories.md)와 [`11-selected-stories.md`](11-selected-stories.md)를 따른다.

---

## ★ 1. 안전시설 public API의 format·인증·좌표·배포 로그 장애 대응

### 1. 상황

F-4 안전 분석을 위해 CCTV, 안전비상벨, 보안등, 치안시설 point data를 수집해 `safety_facility`에 저장하는 단계였다. Issue #90에는 실행 환경이 특정되지 않은 CCTV CSV 403이, Issue #92에는 Cloud Run의 CCTV·비상벨 401과 Safemap key 오류가 기록됐다. scheduler의 정기 실행 여부는 확인되지 않는다.

### 2. 문제

- 초기 CCTV LocalData CSV download가 403을 반환했다.
- CCTV·비상벨 JSON OpenAPI는 401 Unauthorized를 반환했다.
- Safemap IF_0036은 `SERVICE_KEY_IS_NOT_REGISTERED_ERROR`를 반환했다.
- 보안등 응답은 `body[]` 안에 있고 좌표가 WGS84가 아닌 Web Mercator인 경우가 있었다.
- provider마다 JSON·XML·CSV, field name, page limit, total count shape가 달랐다.

한 source의 실패가 전체 batch를 중단하거나 잘못된 좌표가 저장되면 매물별 안전 점수도 신뢰할 수 없게 된다.

### 3. 근거

- [Issue #72](https://github.com/ssafy-salman/salmanhae/issues/72), [PR #73](https://github.com/ssafy-salman/salmanhae/pull/73): 첫 4종 client/parser
- [Issue #90](https://github.com/ssafy-salman/salmanhae/issues/90), [PR #91](https://github.com/ssafy-salman/salmanhae/pull/91): CSV 403→CCTV JSON OpenAPI
- [Issue #92](https://github.com/ssafy-salman/salmanhae/issues/92), [PR #93](https://github.com/ssafy-salman/salmanhae/pull/93): 401, key encoding, Safemap opt-in, page cap
- direct commit `38199b5`: 보안등 key 분리
- direct commit `02fa47a`: 비상벨 response shape 보정
- 현재 파일: [`SafetyDataProperties.java`](../backend/src/main/java/com/ssafy/salmanhae/config/SafetyDataProperties.java), [`AbstractJsonSafetyFacilityOpenApiClient.java`](../backend/src/main/java/com/ssafy/salmanhae/service/safety/ingest/AbstractJsonSafetyFacilityOpenApiClient.java), [`SecurityLightOpenApiClient.java`](../backend/src/main/java/com/ssafy/salmanhae/service/safety/ingest/SecurityLightOpenApiClient.java)

### 4. 원인

1. CSV file download endpoint가 HTTP 403을 반환했다. 제공자 측의 구체 원인은 기록만으로 확인되지 않는다.
2. public data의 decoding service key에 `+`, `/`, `=`가 포함돼 URL construction 과정에서 의미가 깨질 위험이 있었다. PR은 encoding을 보강했지만 이것이 401의 단일 원인이었다는 사후 증거는 없다.
3. Safemap key는 다른 public data portal key와 별도였고 당시 응답은 등록되지 않은 key라고 알렸다.
4. 보안등 좌표와 response container가 fixture로 가정한 shape와 달랐다.
5. 한 추상 client에 여러 provider를 억지로 맞추기보다, 공통 paging과 source-specific mapping의 경계가 필요했다.

### 5. 검토한 선택지

기록으로 확인되는 선택지는 다음뿐이다.

- CCTV: CSV download 유지 vs 행정안전부 `/info` JSON OpenAPI 전환
- Safemap: 잘못된 key로 계속 실패 vs valid key가 있을 때만 source bean 활성화
- service key: 이미 encoding된 값을 그대로 전달 vs decoding 원문을 명시적으로 URL encode
- 대용량 source: 전체 page 무제한 수집 vs `max-pages`로 smoke test·운영 범위 제한

다른 vendor나 scraping을 검토했다는 기록은 없어 대안으로 쓰지 않는다.

### 6. 선택과 판단

- CCTV는 file download dependency를 제거하고 documented JSON OpenAPI로 전환했다.
- `NormalizedSafetyFacility`을 공통 output으로 두고 provider별 parser가 field·coordinate만 책임지게 했다.
- public data service key는 decoding 원문을 environment에 두고 URL query에서 명시적으로 encoding했다.
- valid Safemap key가 없을 때는 해당 source만 비활성화해 다른 세 source가 계속 동작하게 했다.
- `max-pages`와 source별 page-size cap을 두어 smoke test와 무한 paging 위험을 제어했다.

### 7. 구현

- `SafetyFacilitySourceClient` interface와 공통 normalized record
- JSON 공통 paging client: connect/read timeout, total count, empty page, invalid page size, max pages guard
- source별 mapping: 여러 field alias, invalid coordinate skip, fallback source id
- XML parser: DTD·external entity를 끈 안전한 설정
- Web Mercator `XMAP_CRTS/YMAP_CRTS` 또는 `GEOM` point를 WGS84로 변환
- `SafetyFacilityIngestionService`가 상위로 전달된 source 예외를 source별로 잡고 result count를 관리. 일부 concrete client는 HTTP·parse 오류를 빈/부분 결과로 바꿔 실패 count가 누락될 수 있음

### 8. 검증

- 현재 JSON/XML fixture 기반 parser tests와 초기 CSV parser test 이력
- service-key special character와 page cap tests
- source 하나가 실패해도 나머지가 upsert되는 service test
- PR #91·#93의 backend full test 기록
- PR check의 CodeRabbit/Vercel success와 해당 merge 뒤 Cloud Run deploy Action success. Vercel check는 backend 외부 API 성공을 검증하지 않음

현재 조사에서 public API를 재호출하거나 운영 table row를 세지 않았으므로 live data 완전성은 검증하지 않았다.

### 9. 결과

- CCTV source가 실패하던 file download에서 JSON OpenAPI로 교체됐다.
- JSON·XML·좌표계 차이를 공통 domain model로 흡수했다.
- 설정되지 않은 Safemap source를 opt-in으로 분리해 다른 source 실행을 막지 않게 했다.
- request URL, page cap, timeout, malformed payload에 방어 경계가 생겼다.
- PR #93 이후 CCTV·비상벨·보안등·Safemap의 live 수집 성공과 적재 건수는 모두 추가 확인이 필요하다.

### 10. 내 기여

Issue #72·#90·#92와 PR #73·#91·#93의 작성자, 관련 head commit author, direct follow-up commit author가 모두 본인이다. schema·API·score와 AI 연동도 본인이 이어서 구현했다. public API 제공기관의 data 품질은 본인 통제 범위가 아니다.

### 11. 배운 점

외부 API 연동은 “HTTP 호출 성공”이 끝이 아니라, key encoding, provider별 page contract, 좌표계, 부분 실패, 운영 smoke 범위를 service 설계에 포함해야 한다는 점을 보여준다. 신입 backend 포트폴리오에서는 장애 증상→원인→source 격리→회귀 test의 흐름으로 설명하기 좋다.

### 12. 신뢰도

client/parser·좌표·인증 처리 코드는 **확인됨**. 네 source의 live 수집 성공, 401 해소, 운영 DB 적재량은 **확인 필요**.

---

## ★ 2. 법률 RAG의 stub 제거와 제한된 network fallback

### 1. 상황

법률 질문에 `legalCards`를 반환하는 chat contract와 pgvector schema를 phase로 구현하던 중이었다. 초기 구현에는 stub retrieval과 deterministic template answer가 섞여 있었다.

### 2. 문제

- 검색된 법령 card가 있어도 answer가 고정 template처럼 보였다.
- production client가 실제 pgvector가 아닌 stub result를 반환한 시점이 있었다.
- 개발 환경에서 Supabase PostgreSQL 직접 연결이 `OperationalError`로 실패해 Spring 전체 흐름을 확인하지 못한 기록이 있다.
- DB 연결 실패를 무조건 fallback으로 숨기면 production 장애도 정상 응답처럼 보일 위험이 있었다.
- 근거 card가 없을 때 법령 조항을 만들어내면 안 됐다.

### 3. 근거

- [PR #17](https://github.com/ssafy-salman/salmanhae/pull/17)~[#27](https://github.com/ssafy-salman/salmanhae/pull/27): contract→schema→retriever→근거 제한 answer→upsert→초기 UI
- [Issue #30](https://github.com/ssafy-salman/salmanhae/issues/30), [PR #31](https://github.com/ssafy-salman/salmanhae/pull/31): live LLM 연결
- [Issue #34](https://github.com/ssafy-salman/salmanhae/issues/34), [PR #35](https://github.com/ssafy-salman/salmanhae/pull/35): local network fallback
- current code: [`retriever.py`](../backend-ai/app/rag/retriever.py), [`supabase_client.py`](../backend-ai/app/clients/supabase_client.py), [`llm_client.py`](../backend-ai/app/clients/llm_client.py)

### 4. 원인

초기 phase가 contract와 안전한 test boundary를 먼저 만들면서 실제 external client 연결이 뒤 phase로 미뤄졌다. 이후 local network 제약이 direct PostgreSQL 기반 통합 검증을 막았다. 또한 “개발 편의 fallback”과 “운영 장애 정책”을 구분하지 않으면 장애 은닉이 발생할 수 있었다.

### 5. 검토한 선택지

- 고정 template 유지 vs configured OpenAI-compatible `/chat/completions` 호출
- PostgreSQL pgvector만 허용 vs non-production에서 HTTPS REST rows + local cosine fallback
- 모든 환경에서 fallback vs production에서는 `OperationalError` 전파
- write가 기본인 ingestion vs dry-run 기본 + 명시적 `--write`

### 6. 선택과 판단

- card가 있을 때 live LLM을 호출하되 key 미설정·provider 실패 시 deterministic answer로 기능을 유지했다.
- 법령 answer prompt는 retrieved reference만 근거로 사용하도록 지시했다. 생성 결과의 인용을 사후 검증하는 단계는 없다.
- non-production에서 `psycopg.OperationalError`가 나고 DB URL에서 project ref를 추출할 수 있으며 service-role key가 설정된 경우 Supabase REST로 embedding rows를 읽고 local cosine top-k를 계산했다. port 차단 외 같은 예외도 이 경로를 탈 수 있다.
- production은 DB 장애를 숨기지 않고 예외를 올리도록 environment guard를 추가했다.
- ingestion은 dry-run과 write를 분리하고 `content_hash` conflict target으로 중복에 강한 upsert를 구현했다.

### 7. 구현

- `legal_document_chunks`: metadata, `content_hash`, `vector(1536)`, IVFFlat index
- deterministic chunk/hash·document validation
- embedding client와 vector client protocol 분리
- whitespace query skip, top-k 1~5 clamp, connect/statement timeout
- `<=>` cosine ordering과 normalized `legalCards`
- retrieved reference만 사용하도록 지시하는 prompt와 “근거 없음” fallback
- chat completion response shape 방어 parsing
- REST pagination, vector string parse, local cosine

### 8. 검증

- fake embedding/vector/HTTP client로 외부 network 없는 unit tests
- hash·chunk·dry-run·write·upsert tests
- prompt와 card에 전달되는 law/article가 retrieval 결과와 일치하는 test
- production mode에서 fallback하지 않는 test
- PR #35 기록: 34 tests passed, direct FastAPI에서 `LEGAL_CONSULT`, legalCards 3개, LLM answer 확인
- Spring browser flow는 당시 network 때문에 미검증으로 PR에 명시

### 9. 결과

- stub retrieval과 template-only answer가 실제 embedding→pgvector→검색 근거 제한 answer 경로로 바뀌었다.
- local network 제약에서도 retrieval logic을 검증할 경로가 생겼다.
- production DB 장애는 fallback으로 은닉하지 않게 됐다.
- 현재 운영 DB에 법령 chunk가 실제 몇 건 적재됐는지는 확인하지 못했다.

### 10. 내 기여

PR #17~#35의 해당 법률 RAG PR과 commit은 모두 본인 author다. 이후 Router→Supervisor 전환(PR #63)은 팀원 `crolvlee` 작업이므로 본인 기여가 아니다.

### 11. 배운 점

RAG 품질은 model 호출만이 아니라 source ingestion, 중복 방지, retrieval contract, 근거 없음 처리, 장애 policy에서 결정된다는 점을 보여준다. 또한 fallback은 “항상 성공하는 code”가 아니라 environment별 failure semantics를 설계해야 한다. 현재 구현은 품질 평가나 환각 방지를 보장하지 않는다.

### 12. 신뢰도

**확인됨.** 운영 embedding row와 live end-to-end는 **확인 필요**.

---

## ★ 3. 지도 aggregate와 local keyword 검색의 불일치 해결

### 1. 상황

zoom별 `REGION_AVG`·`CLUSTER`·`PROPERTY` API를 만든 뒤 keyword, 거래 유형, 가격 filter를 적용하는 실제 지도 검색 단계였다.

### 2. 문제

keyword는 프론트의 현재 상세 매물 배열에만 local filter로 적용되고 viewport request에는 전달되지 않아 시/도·시/군/구·읍/면/동 marker와 검색 상태가 달랐다. 기존 거래유형·매물유형·보증금·매매가 조건은 이미 region/cluster/property가 DAO helper로 공유했다. 앞선 지도 QA에서는 넓은 zoom 401, cluster click 후 empty list, monthly rent marker가 deposit을 표시하는 별도 문제도 있었다.

### 3. 근거

- [Issue #64](https://github.com/ssafy-salman/salmanhae/issues/64), [PR #65](https://github.com/ssafy-salman/salmanhae/pull/65)
- [Issue #66](https://github.com/ssafy-salman/salmanhae/issues/66), [PR #67](https://github.com/ssafy-salman/salmanhae/pull/67)
- [Issue #94](https://github.com/ssafy-salman/salmanhae/issues/94), [PR #95](https://github.com/ssafy-salman/salmanhae/pull/95)
- CodeRabbit first review: SQL wildcard literal, API spec target, frontend keyword trim 3건
- follow-up commit [`6cb0c85`](https://github.com/ssafy-salman/salmanhae/commit/6cb0c85533af65572dc474313b790c0a28374609)

### 4. 원인

- frontend keyword가 local computed 목록에만 적용되고 viewport request에는 포함되지 않았다.
- PR #95 첫 커밋은 viewport에 raw keyword를 보냈고, 이는 최초 장애 원인이 아니라 리뷰 과정에서 발견된 중간 구현 문제였다.
- 첫 커밋의 SQL `LIKE`는 사용자 `%`, `_`를 literal이 아닌 wildcard로 처리했다.
- 지도 SDK가 이동 중 순간적인 invalid bounds를 내보낼 수 있었다.
- 초기 broad zoom query가 region stats join에 과도하게 의존했다.

### 5. 검토한 선택지

- region marker를 기존 price로 유지 vs active search일 때 matching property count 표시
- local-only keyword 유지 vs 기존 DAO 공통 filter builder와 public list까지 keyword 확장
- broad zoom region-stat join 유지 vs visible active property aggregate
- invalid bounds를 error로 노출 vs last valid bounds 유지

### 6. 선택과 판단

검색 중에는 region 대표 가격보다 “조건에 맞는 매물 수”가 사용자 상태와 더 잘 맞는다고 판단했다. 기존 단일 거래유형·매물유형·보증금·매매가 filter helper에 keyword를 추가하고 public list도 이를 재사용하게 했으며, 리뷰 후 keyword를 trim·literal escape했다. transient invalid bounds 방어는 앞선 지도 QA에서 별도로 구현됐다.

### 7. 구현

- `PropertySearchCriteria.keyword`와 keyword helper
- 기존 `appendPropertyFilters`에 keyword 추가, public bounds list도 재사용
- title, building name, address, road address를 `LOWER(COALESCE(...)) LIKE :keywordPattern ESCAPE '!'`로 검색
- region/cluster/property query에 지원 criteria 적용
- active search getter와 count label rendering
- zoom/center 순서와 last valid bounds 보존
- monthly rent representative label과 enum Korean label

### 8. 검증

- no-result일 때 region marker도 사라지는 backend tests
- literal `%`, `_` keyword 회귀 보정
- frontend API payload, store, marker label unit tests
- PR #95 기록: frontend test/build, selected Spring tests, full Spring tests
- first CodeRabbit review 3건 후 follow-up commit, second review “No actionable comments”
- Vercel preview success. 이는 frontend build/preview 증거이며 backend query 정합성 증거는 아님

### 9. 결과

keyword와 기존 지원 filter가 public 목록·region/cluster/property viewport에 적용되고, 검색 중 marker는 matching count를 보여 주게 됐다. transient map state 방어는 앞선 QA의 별도 성과다. 현재 frontend의 일부 rent-range·multi-select contract에는 추가 불일치가 남아 있다.

### 10. 내 기여

viewport phase PR #54~#67, Issue/PR #94/#95와 review follow-up commit은 모두 본인 author다. PR #110의 final UI design은 팀원 작업이며, 그 뒤 count label direct follow-up `a130a36`만 본인 기여다.

### 11. 배운 점

검색 기능은 endpoint 하나의 filter가 아니라 목록·aggregate·marker·URL parameter·local state가 같은 contract를 공유해야 완성된다. automated review도 “수정했다”보다 첫 지적→follow-up diff→재검증을 보여 주는 근거로 쓸 수 있다.

### 12. 신뢰도

**확인됨.** 남은 frontend filter drift는 current code 기준 **확인됨**.

---

## 4. commit된 seed를 전국 범위를 계획할 수 있는 offline pipeline으로 전환

### 1. 상황

F-1 초기 구현은 국토부 XML에서 거래를 뽑아 JSON·SQL seed를 만들었다. PR #8에는 Supabase SQL Editor 수동 반영 성공 보고가 있으나 외부 DB는 독립 검증되지 않았다.

### 2. 문제

- 거래 JSON과 SQL이 매우 커 repository와 review에 부담이 됐다.
- SQL Editor query size 때문에 file을 여러 chunk로 나눠야 했다.
- 중복 source key가 있어 `ON CONFLICT` 단계가 실패했다.
- 한 번 만든 sample seed로는 전국·최근 12개월을 반복 갱신하기 어렵다.

### 3. 근거

- [Issue #7](https://github.com/ssafy-salman/salmanhae/issues/7), [PR #8](https://github.com/ssafy-salman/salmanhae/pull/8)
- commit `3e4c24c`: SQL chunk 생성
- commit `d448e31`: duplicate key 제거
- [Issue #32](https://github.com/ssafy-salman/salmanhae/issues/32), [PR #33](https://github.com/ssafy-salman/salmanhae/pull/33)
- current [`pipeline.py`](../scripts/data_pipeline/pipeline.py)

### 4. 원인

초기 목표가 backend/frontend 개발을 빠르게 unblock하는 bootstrap이어서 generated artifact를 일시 보존했다. 이 방식은 재현 가능한 운영 ingestion과 책임이 달랐다. source별 XML shape와 pagination을 공통 model로 만들고 DB까지 이어지는 command가 필요했다.

### 5. 검토한 선택지

- generated seed를 계속 version control vs reference code만 남기고 local artifact ignore
- SQL Editor chunk 수동 실행 vs pipeline DB migration/upsert
- sample 지역 고정 vs lawd code CSV로 전국 request plan

### 6. 선택과 판단

초기 seed는 API·지도 contract가 동작하는지 검증하는 데 사용하고, 다음 단계에서 source code와 reference CSV만 보존하는 offline pipeline으로 교체했다. 사용자 요청 시 public API를 부르지 않는 architecture 원칙도 유지했다.

### 7. 구현

- 8 endpoint configuration·request plan과 pagination. raw/seed 호환성은 4개 source만 확인
- HTTP timeout, raw XML local cache와 manifest. manifest의 비어 있지 않은 raw page를 재사용하지만 API `resultCode` 검증과 자동 retry/backoff는 없음
- common `transaction_history` normalization
- `building_key` anchor와 geocoding cache
- region/building stats
- actual transaction range 기반 `MVP_SYNTHETIC` property
- migrate/load/verify와 unique key upsert
- generated `data/pipeline` ignore

### 8. 검증

- PR #8: Git diff에 8,121 transaction·300 property artifact와 duplicate fix·chunk 확인. 거래는 4개 source이며 SQL Editor 반영은 PR 자기보고
- PR #33: `py_compile`, APT_RENT 1지역×1개월×5행 limited plan/run, migrate-db, load-db, verify-db 실행 보고
- CodeRabbit review follow-up 2회

### 9. 결과

대용량 generated seed가 current repository에서 제거되고, 지역·기간·source를 parameter로 받아 반복 실행할 수 있는 pipeline이 남았다. 실제 전국 12개월 전체 실행 row 수와 소요 시간은 확인되지 않았다.

### 10. 내 기여

두 Issue와 두 PR, 그 사이 모든 핵심 commit이 본인 author다.

### 11. 배운 점

bootstrap data와 운영 ingestion을 같은 산출물로 취급하면 repository와 DB 반영 절차가 복잡해진다. 재실행 가능성은 결과 file을 commit하는 것이 아니라 input·transformation·충돌 키 기반 load command를 보존하는 데서 나온다. 현재 구현이 exactly-once나 완전한 운영 재현성을 보장하는 것은 아니다.

### 12. 신뢰도

**확인됨.** 전체 전국 run 성능·row 수는 **확인 필요**.

---

## 5. 안전 점수를 request-time 계산이 아닌 사전 계산으로 구성

### 1. 상황

정규화한 안전시설을 매물 상세와 AI 안전 분석에서 빠르게 사용해야 했다.

### 2. 문제

사용자 요청마다 여러 public API를 호출하거나 모든 시설과 distance를 계산하면 latency와 provider 장애가 사용자 응답에 직접 전파된다. 매물마다 CCTV·비상벨·보안등·치안시설 radius와 weight도 일관되게 적용해야 했다.

### 3. 근거

- [`docs/03_ADR.md`](../docs/03_ADR.md): batch precompute 결정
- [Issue #76](https://github.com/ssafy-salman/salmanhae/issues/76), [PR #77](https://github.com/ssafy-salman/salmanhae/pull/77)
- [PR #79](https://github.com/ssafy-salman/salmanhae/pull/79): AI consumption verification
- current [`PropertySafetyScoreServiceImpl.java`](../backend/src/main/java/com/ssafy/salmanhae/service/safety/PropertySafetyScoreServiceImpl.java)

### 4. 원인

시설은 relatively static하고 매물별 radius count는 반복 사용된다. runtime query와 batch calculation의 경계를 분리하지 않으면 같은 distance work를 계속 수행하게 된다.

### 5. 검토한 선택지

기록으로 확인되는 선택지는 request-time public API/계산, batch precompute, 그리고 거리 계산에서 PostGIS `ST_DWithin`과 bounds prefilter+Java Haversine 비교다. Phase 5 기록에서 공간 확장 의존을 늘리지 않는 후자를 택했다. Redis cache를 실제 검토했다는 기록은 없다.

### 6. 선택과 판단

시설을 먼저 DB에 저장하고, 조건부 monthly score scheduler가 매물별 count와 score를 `property_score_stat`에 upsert하도록 했다. scheduler 기본값은 비활성이다. API와 AI는 stored values만 읽게 했다.

### 7. 구현

- active property를 latitude/longitude 순으로 정렬해 100개 chunk
- 각 매물의 501m candidate bounds를 계산하고 100개 chunk 범위를 merge
- merge bounds로 DB 후보를 조회한 뒤 매물별 bounds로 다시 축소
- 고정 지구 반지름을 사용한 Java Haversine 구면 근사 거리
- CCTV·bell·light 300m, police 500m count
- normalized cap과 30/25/25/20 규칙 기반 시설 접근성 score
- PostgreSQL upsert가 existing `price_score`를 보존

### 8. 검증

- score boundary unit tests
- scheduler disabled/enabled tests
- JDBC upsert test와 H2 compatibility fallback
- candidate query·spatial ordering 관련 3회 review follow-up commit
- Spring `safety-summary`→FastAPI card/answer test

### 9. 결과

사용자 요청은 public API와 distance full scan을 하지 않고 stored score/count를 반환한다. formula와 radius가 code·docs에 고정됐다. 이 값은 범죄 발생 가능성이 아니라 시설 접근성 proxy이며 가중치 calibration은 없다. scheduler가 Cloud Run API instance 안에 있어 scale-to-zero·multiple instance 문제도 남는다.

### 10. 내 기여

schema부터 AI consumption까지 PR #69~#79를 본인이 구현했다.

### 11. 배운 점

성능 개선은 숫자를 만들기 전에 workload의 시간축을 바꾸는 문제다. 변경이 느린 data는 write/batch time에 계산하고 request path를 read-only로 만들 수 있다. 단, scheduler의 실행 보장까지 포함해야 운영 설계가 완성된다.

### 12. 신뢰도

구조와 test는 **확인됨**. 운영 scheduler 실행 횟수·실제 latency 개선 수치는 **확인 필요**.

---

## 6. Spring-FastAPI 분석 contract를 stub에서 실제 data로 연결

### 1. 상황

AI graph에는 PRICE_ANALYSIS와 SAFETY_ANALYSIS node가 있었지만 처음에는 stub summary를 반환했다.

### 2. 문제

- AI answer가 실제 거래·안전 data와 연결되지 않았다.
- 선택 매물 ID를 frontend→Spring→FastAPI로 전달하는 field가 없었다.
- Spring API failure나 미선택 상태의 response shape가 정해져 있지 않았다.
- answer가 `0` value를 missing으로 처리하거나 hardcoded text만 말할 수 있었다.

### 3. 근거

- [PR #37](https://github.com/ssafy-salman/salmanhae/pull/37), [#39](https://github.com/ssafy-salman/salmanhae/pull/39), [#41](https://github.com/ssafy-salman/salmanhae/pull/41), [#46](https://github.com/ssafy-salman/salmanhae/pull/46), [#48](https://github.com/ssafy-salman/salmanhae/pull/48), [#50](https://github.com/ssafy-salman/salmanhae/pull/50)
- current Spring `PropertyController`, `PriceAnalysisController`, FastAPI `spring_client.py`, analysis nodes/service

### 4. 원인

module별 stub과 DTO가 독립적으로 존재했고, user-selected context와 analysis metric contract가 없었다. 서비스 간 HTTP failure를 domain result와 transport error 중 어디서 처리할지도 정해야 했다.

### 5. 검토한 선택지

- stub 유지 vs Spring stored data API 호출
- failure를 graph exception으로 중단 vs controlled fallback card
- answer service hardcode vs metrics/tool result를 prompt와 deterministic fallback 모두에 전달

### 6. 선택과 판단

Frontend는 Spring만 호출하고, Spring이 authenticated user context와 selected property를 FastAPI 내부 endpoint에 전달한다. FastAPI worker는 인증 없이 공개된 Spring의 매물·가격·안전 GET endpoint를 service-to-service HTTP로 호출하고 확인된 오류를 structured result로 만든다. answer prompt에는 card와 tool result에 존재하는 수치만 설명하도록 지시한다.

### 7. 구현

- `selectedPropertyId`, `analysisCards`, metrics map contract
- transactions, safety-summary, price-analysis Spring endpoints
- FastAPI SpringClient timeout·fallback
- price/safety node mapping
- `AnalysisAnswerService`와 저장 수치 제한 prompt
- 0-value preservation
- frontend normalizer·초기 compact card

### 8. 검증

- contract test를 먼저 추가한 phase sequence
- success, missing selection, API unavailable tests
- PR #50 기록: Spring chat test, FastAPI 57 tests, frontend test/build
- API spec의 card type별 variable metrics 문서화

### 9. 결과

stub이 실제 stored transaction·safety data 기반 card와 answer 경로로 교체됐다. 그러나 뒤이어 팀원 PR #63이 FastAPI response의 `intent`를 공개 문서에도 있는 `workersCalled`로 교체한 뒤 Spring/FE consumer는 갱신되지 않았다. `toolResults`와 `nextActions`도 FastAPI schema에만 있고 Spring은 여전히 FastAPI에 없는 `intent`를 기대한다. 다만 두 필드는 Spring 공개 spec의 필수 항목이 아니고 `nextActions`는 현재 기본 빈 배열이다. 공통 메시지·카드는 남을 수 있어 전체 채팅 장애라고 단정할 수 없지만 worker metadata가 조용히 유실되는 current contract drift다.

### 10. 내 기여

PR #37~#50은 본인 author다. Supervisor response 변경 PR #63은 팀원 기여이며, current drift는 공동 system integration의 미해결 항목이다.

### 11. 배운 점

provider 단위 test가 모두 통과해도 consumer contract test가 없으면 다음 architecture change에서 drift가 생긴다. 서비스 간 contract는 schema만이 아니라 양쪽 versioning·compatibility·end-to-end test까지 포함해야 한다.

### 12. 신뢰도

과거 구현·test는 **확인됨**. current drift도 **확인됨**.

---

## 7. 멀티레포→모노레포·GitLab sync·Cloud Run deploy

### 1. 상황

frontend, Spring, AI, artifact가 분리돼 있었고 GitHub 중심 개발과 SSAFY GitLab 제출을 동시에 만족해야 했다.

### 2. 문제

- module별 변경과 API docs를 한 PR에서 함께 review하기 어렵다.
- 제출용 GitLab monorepo와 artifact project를 수동으로 맞추면 누락 위험이 있다.
- Spring과 FastAPI는 runtime·environment·scaling 설정이 다르다.

### 3. 근거

- [`a259751`](https://github.com/ssafy-salman/salmanhae/commit/a259751af0a8d864368b56549f962c83eba589cb): monorepo migration
- [PR #5](https://github.com/ssafy-salman/salmanhae/pull/5): Codex Harness migration
- [PR #52](https://github.com/ssafy-salman/salmanhae/pull/52): Spring Docker/deployment guide
- [`2a81344`](https://github.com/ssafy-salman/salmanhae/commit/2a81344328900226045f3090474392f15d8c1d5f): 두 Cloud Run actions
- current workflows와 GitHub Actions run history

### 4. 원인

개발 host와 제출 host가 다르고, artifact는 별도 project도 요구됐다. 초기 migration은 repository working tree를 한 번에 가져와 legacy source와 compiled class까지 포함한 과도기 상태였다.

### 5. 검토한 선택지

- multi-repo 유지 vs monorepo
- GitLab을 primary로 직접 개발 vs GitHub primary + main push sync
- artifact manual copy vs `git subtree split`
- manual Cloud Run deploy vs path-filtered Actions

### 6. 선택과 판단

GitHub monorepo를 개발 source of truth로 두고 `main`을 GitLab에 sync했다. artifact folder는 subtree history로 별도 target에 push했다. 두 backend는 module path가 바뀔 때만 독립 deploy했다.

### 7. 구현

- root module layout와 single Git history
- main→GitLab `HEAD:master`
- `git subtree split --prefix=artifact`
- multi-stage Spring Docker, Python FastAPI Docker
- `develop` path-filtered deploy, GitHub secret 기반 GCP auth

### 8. 검증

- current branch·remote·workflow code 확인
- GitHub run history: backend 16, backend-ai 9, sync 8 success
- Vercel latest production/preview deployment success
- PR #52 당시 Docker daemon과 backend test 일부는 미검증으로 명시

### 9. 결과

한 PR에서 cross-module contract와 docs를 검토할 수 있고, final `main`이 GitLab 두 target에 자동 반영됐다. 다만 deploy action에 test/lint gate가 없고 GCP JSON key·public internal API 방식의 보안 개선이 남는다.

### 10. 내 기여

monorepo migration, sync action, Harness migration, Docker/deploy action과 guide의 author가 본인이다. final artifact 내용은 팀 공동 산출물이다.

### 11. 배운 점

모노레포는 folder를 합치는 일이 아니라 build boundary, release trigger, 제출 repository, secret과 branch flow를 함께 다시 정의하는 작업이다. CI/CD의 “배포 자동화”와 “품질 gate”는 별개라는 한계도 설명해야 한다.

### 12. 신뢰도

**확인됨.** live service smoke test와 branch approval process는 **확인 필요**.

---

## 8. 매물 API를 Naver map까지 연결하며 CORS·계약 검증

### 1. 상황

실거래가 anchor 기반 `properties`를 만든 직후, 첫 사용자 가치인 지도 탐색을 backend와 frontend에 연결하는 단계였다.

### 2. 문제

- bounds·filter·detail API가 없었다.
- 잘못된 bounds, 음수 filter, 없는/비활성 매물의 error contract가 없었다.
- browser frontend에서 Spring API CORS preflight를 통과해야 했다.
- map loading·list loading·detail loading의 error state를 분리해야 했다.

### 3. 근거

- [Issue #9](https://github.com/ssafy-salman/salmanhae/issues/9), [PR #10](https://github.com/ssafy-salman/salmanhae/pull/10)
- [Issue #11](https://github.com/ssafy-salman/salmanhae/issues/11), [PR #12](https://github.com/ssafy-salman/salmanhae/pull/12)
- commits `9b7c9f4`, `c1d8fbd`, `ad5a86b`, `af0c726`, `7946907`

### 4. 원인

초기 monorepo에는 UI mock과 AI skeleton은 있었지만 현재 schema를 읽는 Spring domain layer와 client contract가 없었다. backend response·error와 frontend SDK lifecycle을 동시에 맞춰야 했다.

### 5. 검토한 선택지

기록에는 다른 architecture 대안이 없다. 문서 규칙에 따라 Frontend→Spring REST만 허용하고 Controller→Service→DAO로 구현했다. 이를 실제로 비교 검토한 선택지처럼 과장하지 않는다.

### 6. 선택과 판단

첫 phase에서 API contract와 H2 fixture/controller·HTTP tests를 만들고, 다음 phase에서 Axios·Naver map을 연결했다. CORS는 backend WebConfig와 Security CORS를 맞추고 preflight integration test를 추가했다.

### 7. 구현

- bounds/filter request와 validation
- common `ApiResponse`/`ErrorResponse`, error code
- JDBC parameter query와 property detail mapping
- Naver map script loader, env client ID
- bounds event→API→marker/list→detail drawer
- loading/error state와 API base URL env

### 8. 검증

- MockMvc success/error/filter tests
- random-port HTTP integration test
- H2 schema/data fixture
- CORS preflight test
- frozen install과 frontend production build 기록
- CodeRabbit review 후 backend/frontend follow-up commits

### 9. 결과

DB의 합성 매물이 공개 Spring API를 거쳐 Naver map marker와 detail panel로 연결됐다. 이후 viewport·검색·transaction trend 기능이 이 경계를 확장했다.

### 10. 내 기여

두 Issue·PR의 author와 핵심 code commit author가 본인이다. 인증 UI와 final design은 팀원 기여다.

### 11. 배운 점

첫 vertical slice에서는 많은 기능보다 validation·error·CORS·test fixture를 포함한 작은 contract를 끝까지 연결하는 것이 후속 기능의 기반이 된다.

### 12. 신뢰도

**확인됨**.

---

## 참고: 핵심 기능이지만 본인 사례로 쓰면 안 되는 것

Router→Supervisor 전환과 38-case 평가([PR #63](https://github.com/ssafy-salman/salmanhae/pull/63))는 팀원 `crolvlee`가 주도했다. 발표나 면접에서는 “팀원이 multi-worker orchestration을 확장했고, 나는 그 graph가 사용하는 법률 RAG와 Spring 분석 tool 경계를 구현했다”고 말하는 것이 정확하다.
