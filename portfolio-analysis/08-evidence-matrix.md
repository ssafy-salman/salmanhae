# 주장별 증거 매트릭스

## 1. 판정 기준

이 문서는 2026-07-10 현재 코드, 모든 Git ref, 실제 commit diff, GitHub Issue·PR 본문, CodeRabbit review와 후속 commit을 다시 대조한 결과다. PR 작성자만으로 소유권을 판단하지 않고, 기능이 처음 생긴 diff와 현재 핵심 line의 blame까지 확인했다.

| 등급 | 의미 | 포트폴리오 사용 원칙 |
|---|---|---|
| A | 본인이 직접 수행했고 code·commit·PR 근거가 충분함 | 제한사항을 함께 적으면 핵심 개인 기여로 사용 가능 |
| B | 본인 기여는 명확하지만 공동 작업이 포함돼 개인 범위를 조절해야 함 | 본인·팀원 역할을 함께 밝혀 공동·통합 기여로 사용 |
| C | 팀 성과이거나 PR 자기보고만 있어 개인·운영 결과를 분리하기 어려움 | 팀 결과 또는 정황으로만 사용 |
| D | 근거가 부족하거나 현재 문구가 구현보다 강함 | 본인 확인 전 성과 문장에 사용하지 않음 |
| E | 현재 코드와 다르거나 계획·미완성·폐기 상태 | 완료 성과로 사용 금지 |

## 2. 우선 검증한 다섯 주장

| 주장 | 종합 판정 | 실제 확인 범위 | 안전한 한 문장 |
|---|---|---|---|
| 국토부 실거래가 8종 정규화 및 재실행 가능한 데이터 파이프라인 | A: 8 endpoint 설정·공통 alias model·raw page 재사용·upsert 구현. D: 전체 실패 복구·운영 검증. E: 8종 전체 호환·전국 12개월 실행 완료 | `SOURCE_CONFIG`에 8 endpoint를 두고 alias normalizer 경로를 구현했다. PR #33 검증은 아파트 전월세 1지역·1개월·5건이며, raw/seed 호환성이 확인되는 것은 아파트·오피스텔 4 source뿐이다. | “국토부 8개 endpoint configuration과 공통 alias normalizer, 결정적 충돌 키 upsert를 가진 수동 offline bootstrap pipeline을 구현했다.” |
| 지도 zoom별 지역·클러스터·매물 API와 검색 필터 통합 | A: backend와 초기 FE. B: 최종 필터 UI는 팀 후속 변경 포함 | zoom mode와 keyword·단일 거래유형·매물유형·보증금·매매가 조건은 공통 DAO filter를 사용한다. 현재 월세 범위·복수 거래유형·`clusterThreshold`는 end-to-end 불일치가 남는다. | “Spring이 지원하는 검색 조건을 지역·grid cluster·개별 매물 query가 같은 DAO builder로 사용하게 했다.” |
| 법령 청킹부터 pgvector 검색·근거 답변까지의 법률 RAG | A: ingestion·retrieval·초기 card·answer. D: 현재 운영 dataset | 조문 JSON→800자/120자 overlap chunk→embedding→`vector(1536)`→cosine top-k→prompt 흐름이 있다. threshold와 live output 검증은 없다. | “법령 chunk·embedding·pgvector 검색 결과를 답변 context로 제한하는 grounding 장치를 구현했다.” |
| Spring–FastAPI 시세·안전 분석 계약과 UI 카드 연결 | A: 선택 매물 contract·Spring API·FastAPI mapping·초기 UI. B: 현재 전체 흐름 | 본인이 PR #37~#50에서 초기 vertical slice를 구현했다. 팀원이 Supervisor와 최종 Chatbot UI를 후속 변경했고 `workersCalled` drift가 남았다. | “선택 매물의 저장형 시세·안전 API를 FastAPI `analysisCards`와 초기 Vue 카드까지 연결했다.” |
| 4종 안전시설 수집, 좌표 변환, Haversine 기반 사전 안전 점수 | A: client/parser·변환·score code. D: 4종 운영 성공 | CCTV·비상벨·보안등·치안시설 code path와 점수식은 확인된다. 비상벨·보안등 URL은 설정 필요, Safemap은 기본 off, 운영 row는 미확인이다. | “안전시설 4종 client·정규화 구조와 Haversine 기반 시설 근접성 점수 batch를 구현했다.” |

## 3. 상세 주장 매트릭스

### 3.1 데이터 파이프라인

| ID | 주장 | 등급 | commit | PR·Issue | 주요 파일 | 실제 기여·현재 상태 | 사용 | 안전한 표현 | 금지 표현 | 추가 확인 |
|---|---|---|---|---|---|---|---|---|---|---|
| DATA-01 | 국토부 8 endpoint 설정과 공통 거래 model | A | `79ae977`, `21e5e16` | [Issue #32](https://github.com/ssafy-salman/salmanhae/issues/32), [PR #33](https://github.com/ssafy-salman/salmanhae/pull/33) | [`pipeline.py`](../scripts/data_pipeline/pipeline.py), [`202606160001_create_properties.sql`](../database/migrations/202606160001_create_properties.sql) | 본인이 8 URL, source config, field alias, 20-field normalized row를 구현. 현재 CLI가 사용 | 핵심 | “8 endpoint를 수용하는 config+alias normalizer” | “8개 전용 adapter를 각각 구현” | villa·단독다가구 raw fixture |
| DATA-02 | 중복에 강하고 제한적으로 raw page를 재사용하는 재실행 | A: 구현, D: 실패 복구·운영 검증 | `79ae977`, `4a1a6fe` | PR #33 | `pipeline.py` fetch/load SQL | 결정적 composite hash·4 table `ON CONFLICT`, manifest의 비어 있지 않은 raw page 재사용, geocode cache·고정 random seed가 있음. API `resultCode` 검증, stale 삭제·자동 retry·stage ledger는 없고 FAILED geocode도 자동 재시도하지 않음 | 핵심, 범위 제한 | “결정적 key의 중복 row를 갱신하고 manifest raw page를 재사용” | “성공 검증된 page checkpoint·pipeline 전체 멱등” | 실패 재실행 운영 기록 |
| DATA-03 | DB load가 거래·통계·매물을 한 transaction으로 적재 | A: 코드, D: rollback 실증 | `4a1a6fe` | PR #33 | `load_supabase`, four upsert SQL | 네 table을 한 connection·commit으로 적재. migration과 verify는 별도 transaction이고 rollback 주입 test 없음 | 보조 | “DB load 단계는 한 transaction으로 묶음” | “fetch부터 migration·verify까지 전체 rollback” | 장애 주입 rollback test |
| DATA-04 | 8,121 거래·300 합성 매물 bootstrap | A: artifact 사실, D: 실제 DB 반영 | `1d903b2`, `d448e31` | [Issue #7](https://github.com/ssafy-salman/salmanhae/issues/7), [PR #8](https://github.com/ssafy-salman/salmanhae/pull/8) | 과거 `data/seed/*`, `database/seed/*` | 본인 diff에서 artifact 확인. 거래는 4 source, 202605~06, 5개 지역; 현재 파일은 제거됨. DB 반영은 PR 자기보고 | 숫자 범위 명시 시 사용 | “과거 표본 artifact 8,121건·매물 300건” | “전국 12개월 8종 8,121건을 현재 운영” | 실제 Supabase 반영·현재 row |
| DATA-05 | 전국 최근 12개월·8종 전체 실행 완료 | E | 없음 | PR #33은 limited sample만 기록 | `pipeline.py` | code capability는 있으나 전체 run 증거 없음 | 제외 | “전국 실행을 지원하도록 설계” | “전국 12개월 적재 완료” | 전체 run log·row·duration |
| DATA-06 | 자동 retry와 운영 scheduler | E | retry는 legacy seed script에만 존재 | 없음 | current `pipeline.py` | 새 fetch 분기 예외는 error JSON에 남기고 다음 request tuple로 진행하지만 cached XML·normalize parse 예외는 상위로 전파. 재실행은 수동 CLI이며 scheduler/action 없음 | 제외 | “일부 fetch 오류 기록 후 수동 재실행” | “전 단계 자동 복구·backoff retry·운영 정기 batch” | 운영 job 존재 여부 |

### 3.2 지도·검색

| ID | 주장 | 등급 | commit | PR·Issue | 주요 파일 | 실제 기여·현재 상태 | 사용 | 안전한 표현 | 금지 표현 | 추가 확인 |
|---|---|---|---|---|---|---|---|---|---|---|
| MAP-01 | zoom별 region/cluster/property API | A | `443685f`, `a4fbcfa`, `8782011`, `26c5b63` | [PR #54](https://github.com/ssafy-salman/salmanhae/pull/54), [#56](https://github.com/ssafy-salman/salmanhae/pull/56), [#62](https://github.com/ssafy-salman/salmanhae/pull/62), [#65](https://github.com/ssafy-salman/salmanhae/pull/65) | `MapViewportController`, `MapViewportServiceImpl`, `JdbcPropertyDao` | controller·service·SQL·초기 FE rendering을 본인이 구현. current frontend가 호출 | 핵심 | “zoom에 따라 지역·grid cluster·개별 매물을 반환” | “별도 clustering library 사용” | query latency·item count |
| MAP-02 | keyword 검색을 목록·지역·cluster 계약에 통합 | A | `a4fbcfa`, `ad3de24`, `6cb0c85` | [Issue #94](https://github.com/ssafy-salman/salmanhae/issues/94), [PR #95](https://github.com/ssafy-salman/salmanhae/pull/95) | `PropertySearchCriteria`, `appendPropertyFilters`, `mapStore.js` | 기존 가격·유형용 common builder는 `a4fbcfa`에 존재. 본인은 PR #95에서 local-only keyword를 viewport/public list에 추가하고 count marker를 구현했으며 trim·`%/_` escape 리뷰를 반영 | 핵심 | “기존 공통 filter 경로에 keyword와 public list를 정렬” | “PR #95에서 모든 filter builder를 처음 만들고 현재 UI의 모든 필터를 완전 통일” | 문제를 처음 본 실제 상황 |
| MAP-03 | 최종 월세 범위·복수 거래유형도 backend 반영 | D | 팀원 `d26ee43` 이후 current drift | PR #110 관련 | `mapStore.js`, controllers | FE는 월세 범위를 보내나 Spring은 받지 않음. 복수 유형은 parameter를 비움 | 제외·debt | “추가 UI 필터는 계약 확장 필요” | “복수 선택과 월세 범위까지 완료” | 최종 demo 증상 |
| MAP-04 | 넓은 zoom marker가 실거래가 평균 | E | `8782011`, `26c5b63` | PR #62, #65 | `findVisibleRegionAverageViewportItems` | current SQL은 활성 `properties`의 가격·개수를 집계 | 제외 | “활성 매물 대표 가격·count” | “region_price_stat 실거래가 평균” | 없음 |

### 3.3 법률 RAG

| ID | 주장 | 등급 | commit | PR·Issue | 주요 파일 | 실제 기여·현재 상태 | 사용 | 안전한 표현 | 금지 표현 | 추가 확인 |
|---|---|---|---|---|---|---|---|---|---|---|
| RAG-01 | 법령 ingestion→embedding→pgvector retrieval | A | `7de5ebe`, `cd30e7b`, `6941836` | [PR #19](https://github.com/ssafy-salman/salmanhae/pull/19), [#21](https://github.com/ssafy-salman/salmanhae/pull/21), [#25](https://github.com/ssafy-salman/salmanhae/pull/25) | `ingest_legal_docs.py`, `supabase_client.py`, `retriever.py`, legal migration | 본인이 chunk/hash/write/retrieval을 구현. current legal worker가 사용 | 핵심 또는 보조 | “800자·120자 overlap chunk와 cosine top-k 구현” | “법령 원문을 자동 최신 수집” | 운영 source JSON·row·법령 버전 |
| RAG-02 | 검색 근거로 답변을 제한하는 grounding 장치 | A | `3f49798`, `dc68f97` | [PR #23](https://github.com/ssafy-salman/salmanhae/pull/23), [#31](https://github.com/ssafy-salman/salmanhae/pull/31) | `prompts.py`, `llm_client.py` | retrieved card만 법률 답변 context에 넣고 no-card면 최종 법률 답변용 live LLM을 건너뜀(Supervisor routing은 별도). live output post-validation은 없음 | 보조 | “grounding prompt와 근거 없음 fallback 적용” | “환각을 방지·법적 정확성 보장” | RAG answer 평가 |
| RAG-03 | 유사도 threshold와 공식 출처 UI 제공 | E | 없음 | 없음 | retriever/card/UI | top-k 1~5만 있고 threshold 없음. `source_url`이 card에 전달되지 않음 | 제외·debt | “cosine score를 card에 노출” | “낮은 유사도 차단·공식 링크 제공” | threshold calibration |
| RAG-04 | 두 대상 법령이 현재 운영 DB에 적재 | D | PR #35 당시 direct cards 자기보고 | [PR #35](https://github.com/ssafy-salman/salmanhae/pull/35) | ignored `data/legal`, operating DB | code·문서 대상은 두 법령이나 repository input/current row 없음 | 본인 확인 후 사용 | “MVP 대상은 두 법령” | “현재 최신 법령이 운영 반영” | row count·effective date |
| RAG-05 | non-prod REST+local cosine fallback | A | `ddea200`, `ab4e546`, `0a9b0b2` | [Issue #34](https://github.com/ssafy-salman/salmanhae/issues/34), PR #35 | `supabase_client.py` | non-prod `psycopg.OperationalError`에서 project ref 추출과 service-role key가 가능하면 1000-row paging·memory cosine을 시도. production은 rethrow | 보조 | “조건을 만족한 direct PG OperationalError의 개발용 우회 경로” | “모든 개발·운영 DB 장애 fallback” | 실제 사용 환경 |
| RAG-06 | LangGraph Supervisor를 본인이 구현 | E | 팀원 `2d05761`~`91ccb72` | [PR #63](https://github.com/ssafy-salman/salmanhae/pull/63) | graph supervisor/builder | 본인은 legal worker 경계를 제공. Supervisor·38-case 평가 주도자는 팀원 | 개인 성과 제외 | “팀원이 만든 Supervisor가 본인 RAG worker를 호출” | “Supervisor를 설계·구현” | 저장소 밖 review 기여 |

### 3.4 Spring–FastAPI·Frontend 계약

| ID | 주장 | 등급 | commit | PR·Issue | 주요 파일 | 실제 기여·현재 상태 | 사용 | 안전한 표현 | 금지 표현 | 추가 확인 |
|---|---|---|---|---|---|---|---|---|---|---|
| INT-01 | 선택 매물 시세·안전 Spring API→FastAPI card | A | `45c393b`, `778e9f7`, `d4dcbe1`, `f60581f` | [PR #37](https://github.com/ssafy-salman/salmanhae/pull/37), [#39](https://github.com/ssafy-salman/salmanhae/pull/39), [#41](https://github.com/ssafy-salman/salmanhae/pull/41), [#46](https://github.com/ssafy-salman/salmanhae/pull/46) | Chat DTO/client, property/price controllers, AI nodes, `AnalysisAnswerService` | 본인이 selected ID·stored API·timeout/fallback·metric mapping을 구현. current path 존재 | 핵심 | “선택 매물 분석 vertical slice 구현” | “모든 시세 질의가 Spring을 사용” | current live smoke |
| INT-02 | 초기 legal/analysis 카드 UI 직접 구현 | A | `7dc4d1a`, `228c3fa`, `5716627` | [PR #27](https://github.com/ssafy-salman/salmanhae/pull/27), [#48](https://github.com/ssafy-salman/salmanhae/pull/48) | `chat-normalizer.js`, `chat.js`, 당시 `mapStore`, `Chatbot.vue` | 본인이 payload·normalizer·초기 rendering·tests를 구현 | 범위 명시 시 사용 | “초기 카드 연동과 렌더링 구현” | “현재 최종 Chatbot UI 전체 구현” | 없음 |
| INT-03 | 현재 최종 Chatbot UI도 본인 단독 | E | 팀원 `e4ba51a`, `dedb3d6`, `439e49a` | PR #80, #104 | current `Chatbot.vue`, `chatSessionStore.js` | 팀원이 최종 markup/style/session을 재설계. 본인 normalizer는 유지 | 제외 | “팀원이 최종 UI 재설계” | “최종 챗봇 디자인·세션 UI 단독 구현” | 저장소 밖 협업 |
| INT-04 | `workersCalled`가 end-to-end 전달 | E | 팀원 `d9c0e03`이 FastAPI만 변경 | PR #63 | FastAPI schema/routes, Spring `AiAgentClient`, FE normalizer | FastAPI list가 Spring에서 버려지고 `intent:null`, FE는 `''`. message/cards는 전달 가능 | debt만 | “worker metadata가 소비자에서 소실” | “채팅 전체가 항상 실패” | demo·network log |
| INT-05 | `workersCalled` mismatch 존재·원인 | C(팀 시스템의 현재 결함; 개인 성과 아님) | `d9c0e03`, 이후 fix 없음 | PR #63 본문도 Spring/FE 확인 필요 명시 | 위 파일과 tests | current static contract와 각 module test fixture가 직접 증명. 이번 감사 결과이며 당시 본인이 해결한 기능이 아님 | debt·개선 사례만 | “producer·consumer test 부재로 silent drift 잔존” | “내가 당시 발견·해결했다” | 실제 사용자 영향 |

### 3.5 안전시설·점수·운영

| ID | 주장 | 등급 | commit | PR·Issue | 주요 파일 | 실제 기여·현재 상태 | 사용 | 안전한 표현 | 금지 표현 | 추가 확인 |
|---|---|---|---|---|---|---|---|---|---|---|
| SAF-01 | 안전시설 4종 client/parser·공통 model | A | `4bf127f`, `48bda7e`, `26c7aa7` | [PR #73](https://github.com/ssafy-salman/salmanhae/pull/73), [#75](https://github.com/ssafy-salman/salmanhae/pull/75) | safety clients, `NormalizedSafetyFacility`, ingestion service | safety slice의 schema·client·service·tests를 본인이 구현 | 핵심 | “4종을 수용하는 수집·정규화 code path” | “4종 모두 운영 적재 성공” | source별 row·timestamp |
| SAF-02 | Web Mercator→WGS84 변환 | A | `d2aa9b6`, 관련 parser follow-up | [PR #91](https://github.com/ssafy-salman/salmanhae/pull/91) | `SecurityLightOpenApiClient` | `XMAP_CRTS/YMAP_CRTS`·`GEOM`을 구면 Mercator 공식으로 변환하고 fixture test | 핵심 세부 | “보안등 좌표를 WGS84로 변환” | “모든 source 좌표계를 자동 판별” | 실제 endpoint CRS 확인 |
| SAF-03 | Haversine 기반 사전 시설 근접성 점수 | A | `0bee1d6`, `a48138b`, `c00c00a`, `e05a637` | [PR #77](https://github.com/ssafy-salman/salmanhae/pull/77) | `PropertySafetyScoreServiceImpl`, score upsert | 매물별 501m 후보 bounds를 100개 chunk 단위로 merge해 DB 후보를 조회하고, 매물별 bounds 재검사와 Java Haversine 구면 근사로 300/500m count·cap·weight를 계산 | 핵심 | “시설 근접성 heuristic을 0~100으로 사전 계산” | “범죄 안전도·범죄 가능성 예측” | weights 근거·validation |
| SAF-04 | CCTV 403 경로 교체·401 위험 보강 | A: 변경, D: live 해결 | `d2aa9b6`, `7ab97f3`, `cad48d2`, direct `38199b5`, `02fa47a` | [Issue #90](https://github.com/ssafy-salman/salmanhae/issues/90), [#92](https://github.com/ssafy-salman/salmanhae/issues/92), PR #91, [#93](https://github.com/ssafy-salman/salmanhae/pull/93) | config/http/clients/tests/docs | 본인이 CSV→JSON, key encoding, page cap, Safemap opt-in을 구현. 수정 후 live status/row 없음 | 문제 해결 사례, 결과 제한 | “403-producing CSV 의존 제거·encoding risk 보강” | “401 원인을 확정하고 운영 해결 확인” | post-fix smoke log |
| SAF-05 | source 실패가 항상 DTO에 정확히 기록 | D | `26c7aa7` | PR #75 | ingestion service·concrete clients | service는 thrown RuntimeException을 격리하지만 concrete client는 일부 HTTP/parse error를 삼키고 partial/empty success처럼 반환 가능 | debt | “source 단위 계속 진행 구조” | “모든 실패가 failed count에 기록” | 실제 failure result |
| SAF-06 | 월 batch의 정시·단일 실행 보장 | E | 없음 | 없음 | conditional schedulers, Cloud Run workflow | default off, min=0/max=3, lock 없음 | 제외·debt | “월 cron code가 있으며 기본 off” | “Cloud Run에서 정시·한 번 실행” | 운영 trigger |
| SAF-07 | `radius=300/500`에 따라 안전 요약·점수가 동적으로 재계산 | E | current code | 없음 | `PropertyServiceImpl`, `JdbcPropertyDao.findSafetySummary`, AI `SpringClient` | Spring은 300/500을 검증하지만 DAO query는 radius를 조건에 쓰지 않고 응답에 echo한다. 값은 항상 300m 세 시설+500m 경찰의 사전 집계이며 AI는 `radius=500`을 보내 “500m 기준 점수”로 요약 | debt | “radius는 현재 표시 metadata이며 점수식 반경은 고정” | “요청 radius에 맞춘 동적 300/500m 안전 점수” | API 의도·UI 영향 |

### 3.6 팀·운영 주장

| ID | 주장 | 등급 | 근거 | 사용 원칙 |
|---|---|---|---|---|
| TEAM-01 | Supervisor 전환 후 38-case recall 40.6%→94.8% | C: 팀 결과 | 팀원 PR #63과 저장된 eval JSON. 평균 latency 1.54s→7.00s | 팀 결과·trade-off로만 언급, 본인 성과 금지 |
| TEAM-02 | Spring Security JWT core 구현 | E: 개인 주장, A: 팀 구현 | 팀원 PR #13·#28 | “팀원 인증 위에 chat 경계를 연결”로만 표현 |
| OPS-01 | Cloud Run·GitLab sync 배포 자동화 | A | 본인 PR #52, commit `2a81344`, 성공 Actions 이력 | “배포 자동화” 가능. “테스트 gate가 있는 CI”는 금지 |
| OPS-02 | 모든 현재 test가 통과하고 deploy가 이를 보장 | E | workflow에 test/lint 없음, Docker `-DskipTests`, 이번 조사 미실행 | 과거 PR 자기보고와 current 상태를 구분 |
| PRODUCT-01 | 실제 매물 중개·wishlist·server session·HUG 정밀판정 완성 | E | current code/migration 부재 또는 prototype | 완료 기능으로 사용 금지 |

## 4. 최종 사용 원칙

1. A 등급도 운영 수치·사용자 결과까지 자동으로 증명하지 않는다.
2. B 등급은 “본인이 만든 초기 경계”와 “팀원이 바꾼 현재 UI·Supervisor”를 시간순으로 말한다.
3. D·E 등급은 [`12-confirmation-questions.md`](12-confirmation-questions.md)의 답을 얻기 전 성과 문장으로 올리지 않는다.
4. `idempotent`, `grounded`, `safety` 같은 용어는 각각 **deterministic composite-key duplicate resistance**, **prompt-level grounding**, **시설 근접성 heuristic**으로 의미를 풀어 쓴다.
