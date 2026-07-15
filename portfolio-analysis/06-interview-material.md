# 면접 준비 자료

## 1. 30초 프로젝트 소개

살만해는 청년 1인 가구가 계약 전에 매물 가격, 주변 안전시설, 실거래가, 임대차 법령을 한 흐름에서 확인하도록 만든 2인 팀 부동산 탐색 서비스입니다. 저는 국토부·안전시설 public data를 저장형 pipeline으로 만들고, 지도 API, 법률 RAG, Spring-FastAPI 분석 연동, Cloud Run 배포 자동화를 담당했습니다. 특히 provider마다 다른 안전시설 format·인증·좌표 차이를 공통 model과 source-isolated batch로 다루고, 확인된 403·401에 대응하는 코드를 보강했습니다.

## 2. 1분 프로젝트 소개

살만해는 실거래가 기반 합성 매물을 Naver map에서 탐색하고, AI가 매물 추천·법률 RAG·시세·안전 분석을 조합하는 2인 팀 프로젝트입니다. Frontend는 Spring Boot만 호출하고, Spring이 JWT 인증과 domain API를 담당한 뒤 FastAPI LangGraph service에 AI 요청을 위임합니다. 저는 국토부 실거래가 8개 endpoint configuration·공통 alias normalizer와 통계·합성 매물 pipeline, zoom별 region·cluster·property API, 법령 chunk·embedding·pgvector retrieval, 네 종류 안전시설 client와 시설 접근성 사전 계산 batch를 구현했습니다. 거래 raw 호환성은 4개 source에서 확인됩니다. Issue #90의 CCTV CSV 403과 Issue #92의 Cloud Run 401·Safemap key 오류, Web Mercator 좌표 문제에는 source별 parser·endpoint·key encoding으로 대응했습니다. 8 endpoint·안전시설 4종의 운영 성공과 사용자·성능 수치는 주장하지 않습니다.

## 3. 3분 프로젝트 소개

살만해는 청년 1인 가구가 집을 계약하기 전에 흩어진 실거래가, 주변 안전시설, 임대차 법령을 지도와 자연어 질문으로 함께 확인하도록 만든 서비스입니다. 발표자료는 2026년 5~6월 2인 팀 프로젝트로 기록하고, 현재 저장소에서 검증되는 구현 이력은 6월 12일부터 26일까지입니다. 실제 시작일은 `[본인 확인 필요]`입니다.

구조는 Vue frontend, Spring Boot backend, FastAPI AI backend, Supabase PostgreSQL·pgvector로 나눴습니다. Frontend는 FastAPI를 직접 호출하지 않고 Spring을 단일 gateway로 사용합니다. Spring은 JWT 인증과 매물·시세·안전 API를 담당하고, FastAPI는 LangGraph worker와 법률 vector search를 담당합니다. public data는 요청 경로 밖의 offline pipeline 또는 조건부 scheduled batch로 저장하도록 구현했으며 실제 scheduler 운영은 확인되지 않았습니다.

제가 담당한 첫 번째 영역은 data와 지도 backend입니다. 국토부 8개 endpoint 설정과 공통 alias normalizer를 만들고 실제 건물 anchor를 geocoding해 합성 매물과 지역·건물 통계를 생성했습니다. 초기에는 SQL Editor용 seed chunk를 만들었지만, 대용량 generated data가 repository에 남고 반복 실행이 어려워져 plan·run·migrate·load·verify와 충돌 키 upsert를 가진 offline pipeline으로 바꿨습니다. 저장소 raw/seed로 호환성이 확인되는 것은 4개 source 8,121건입니다. 지도는 zoom에 따라 region, grid cluster, 개별 매물을 반환하도록 하고 local-only keyword를 기존 filter builder와 viewport payload에 연결했습니다.

두 번째는 법률 RAG와 AI service 연동입니다. 법령을 content hash 기반으로 chunk하고 embedding을 pgvector에 upsert한 뒤 retrieved law/article만 answer 근거로 사용하도록 prompt와 card를 구성했습니다. non-production에서 PostgreSQL 직접 연결이 `OperationalError`로 실패하면 HTTPS REST로 vector rows를 읽어 local cosine top-k를 계산했고, production에서는 같은 오류를 숨기지 않았습니다. 시세·안전 worker는 Spring API를 내부 HTTP로 호출하고, `analysisCards`와 tool result의 실제 수치만 설명하도록 연결했습니다. 생성 답변의 정확성을 사후 보장하는 단계는 없습니다.

세 번째는 안전시설 batch입니다. CCTV·비상벨·보안등·치안시설이 JSON·XML, 이전 CSV 경로와 서로 다른 좌표계를 사용했습니다. 공통 normalized model과 source-specific parser를 두고, 상위로 전달된 source 실패가 전체 batch를 중단하지 않게 했습니다. CCTV download 403 뒤 JSON OpenAPI로 교체했고, 401 기록 뒤 decoding key를 명시적으로 URL encode했습니다. 이것이 401의 단일 원인이었거나 수정 후 live 성공했다는 증거는 없습니다. Web Mercator 좌표는 WGS84로 변환했습니다. 시설을 저장한 뒤 매물별 300m·500m count와 규칙 기반 시설 접근성 점수를 미리 계산해 request path는 DB read만 수행하게 했습니다.

팀원은 Spring Security 인증 core와 현재 LangGraph Supervisor 전환을 주도했습니다. 저는 그 위에서 법률 RAG와 analysis worker, data·지도·안전·배포 경계를 담당했습니다. 현재는 Supervisor가 반환하는 `workersCalled`가 Spring·frontend까지 전달되지 않는 contract drift와, deploy workflow에 test gate가 없는 점을 가장 먼저 개선하고 싶습니다.

## 4. 가장 어려웠던 문제 답변

### 질문: 가장 어려웠던 문제는 무엇이었나요?

가장 어려웠던 문제는 안전시설 public API가 local fixture와 실제 호출에서 다르게 동작한 일이었습니다. Issue #90에는 실행 환경이 특정되지 않은 CCTV CSV 403이 기록됐고, Issue #92의 Cloud Run에서는 CCTV·비상벨 401과 Safemap key 오류가 기록됐습니다. 보안등은 좌표도 WGS84가 아니라 Web Mercator인 경우가 있었습니다.

먼저 장애를 source별로 분리했습니다. CCTV는 file download를 유지하지 않고 documented JSON OpenAPI로 바꿨고, public data의 decoding key는 `+`, `/`, `=`가 깨지지 않도록 URL query에서 명시적으로 encode했습니다. 별도 key가 필요한 Safemap은 opt-in으로 바꿔 다른 source 실행을 막지 않게 했습니다. response container와 좌표 변환은 source parser에 두고 fixture test를 추가했습니다. page cap과 timeout도 넣었습니다.

그 결과 상위로 전달된 한 provider 예외가 전체 batch를 중단하지 않고 다음 source를 시도할 수 있는 구조가 됐습니다. 다만 일부 client는 오류를 빈 결과로 바꿀 수 있고, 네 source의 수정 후 live 성공과 운영 row 수를 확인하지 못했습니다. 이 경험으로 외부 API 연동은 정상 response mapping보다 인증 문자, 좌표계, pagination, 부분 실패와 관측성을 설계하는 일이 더 중요하다는 것을 배웠습니다.

## 5. 기술 선택 이유 답변

### Spring Boot와 FastAPI를 왜 분리했나요?

인증·domain API는 Spring Security와 Java service 계층에서 일관되게 관리하고, LangGraph·embedding·pgvector retrieval은 Python ecosystem을 활용하기 위해 분리했습니다. Frontend가 FastAPI를 직접 호출하지 않게 해 JWT 검증을 Spring 하나로 모았습니다. trade-off는 service 간 HTTP failure와 두 runtime 운영 비용입니다. 이를 내부 API key, timeout, 확인된 오류의 structured fallback으로 일부 완화했지만 현재 timeout budget 역전, circuit breaker 부재, Cloud Run IAM 비공개 호출은 남은 과제입니다.

### PostgreSQL과 pgvector를 함께 쓴 이유는 무엇인가요?

매물·거래·안전시설 같은 관계형 data와 법령 vector를 한 Supabase PostgreSQL에서 관리해 별도 vector database 운영 복잡도를 줄이기 위해서입니다. 법령 chunk는 `content_hash` unique key와 conflict upsert를 사용하고 `<=>` cosine search를 적용했습니다. 대신 FastAPI가 DB schema에 직접 의존하고, 현재 데이터 규모와 품질 평가가 확인되지 않아 IVFFlat 설정을 재검증해야 한다는 trade-off가 있습니다.

### public API를 request-time에 호출하지 않은 이유는 무엇인가요?

public API는 latency, daily limit, schema inconsistency, 일시 장애가 있습니다. 거래·안전시설은 즉시성이 낮으므로 미리 수집·정규화하고, 시설 접근성 점수까지 batch에서 계산해 request path를 stored-data read로 만들었습니다. 현재 scheduler는 기본 비활성이고 Spring `@Scheduled`가 Cloud Run scale-to-zero와 multi-instance에서 실행 보장을 갖지 못한다는 한계가 있어, 다시 구현하면 Cloud Scheduler와 Run Job으로 분리하겠습니다.

### LangGraph Supervisor를 왜 썼나요?

이 선택과 구현은 팀원이 주도했습니다. single-turn intent router가 복합 질문에서 하나의 worker만 호출하는 한계를 해결하려고 Supervisor loop로 전환했습니다. 저장된 38-case 평가에서 복합 의도 recall은 높아졌지만 latency도 크게 늘었습니다. 저는 Supervisor 자체가 아니라 그 graph가 사용하는 법률 RAG와 Spring analysis tool 경계를 구현했습니다.

## 6. 협업 갈등 또는 조율 경험 답변

저장소에는 사람 간 갈등이나 review 대화가 남아 있지 않아 갈등을 만들어 말하지 않겠습니다. 대신 확인 가능한 조율 경험은 GitHub 개발 흐름과 SSAFY GitLab 제출 흐름을 함께 맞춘 일입니다.

초기에는 module별 repository와 제출 artifact가 분리돼 있어 API code와 문서가 서로 다른 시점에 반영될 위험이 있었습니다. GitHub monorepo를 개발 source of truth로 두고 frontend·Spring·FastAPI·docs를 같은 PR에서 변경할 수 있게 했습니다. `main` push 때 전체 monorepo는 GitLab project로, `artifact/`는 subtree split으로 별도 artifact project에 sync했습니다. 두 backend deploy는 module path filter로 분리했습니다.

이 구조로 cross-module contract를 한 PR에서 볼 수 있고 제출 누락을 줄였습니다. 반대로 branch protection과 사람 approval 기록이 없고 final 단계에 direct `develop` commit이 늘었다는 한계도 있습니다. 다시 한다면 protected branch와 required test/review gate를 설정하겠습니다.

## 7. 본인 기여도 답변

저는 전체를 혼자 구현하지 않았습니다. 팀원은 Spring Security 인증, frontend auth/session, Router→Supervisor 전환, final UI를 주도했습니다.

제가 직접 소유한 영역은 다섯 가지입니다.

1. 국토부 8개 endpoint configuration·공통 alias normalizer, geocoding, 합성 매물, 통계·DB conflict upsert pipeline. raw 호환성은 4개 source 확인
2. 공개 매물 API와 zoom별 map viewport·filter consistency
3. 법령 chunk·embedding·pgvector retrieval·검색 근거 제한 answer와 non-prod fallback
4. 안전시설 4종 client/normalization, ingestion·시설 접근성 score batch, API 장애 대응 코드
5. Spring-FastAPI `analysisCards` contract와 초기 frontend card, Docker/Cloud Run deploy, GitLab sync

근거는 동일 email author commit 164개라는 숫자보다 해당 PR의 actual diff입니다. 대표적으로 data PR #8·#33, legal RAG #17~#35, analysis #37~#50, map #54~#67·#95, safety #69~#93이 있습니다.

## 8. backend 개발자로서 배운 점

- 외부 API client는 data mapping보다 retry 여부와 한도, timeout, key encoding, pagination, 좌표계, 부분 실패가 핵심입니다.
- 중복에 강한 ingestion은 결과 file 보존보다 unique key와 재실행 가능한 command로 확보해야 하며, 이를 exactly-once와 구분해야 합니다.
- AI service도 ordinary backend처럼 contract, timeout, fallback, observability, consumer compatibility가 필요합니다.
- batch precompute로 request path를 단순화할 수 있지만 scheduler 실행 보장까지 설계해야 합니다.
- test 수가 많아도 deploy gate와 consumer contract test가 없으면 integration drift가 남습니다.

## 9. 다시 개발한다면 바꿀 점

1. `workersCalled` OpenAPI/schema를 source of truth로 만들고 Spring·frontend generated client 또는 consumer contract test를 둡니다.
2. `users`를 포함한 모든 운영 migration을 처음부터 versioned schema로 관리합니다.
3. Spring·AI·frontend test와 build가 통과한 뒤에만 Cloud Run/Vercel 배포되게 합니다.
4. public data job을 Cloud Scheduler·Run Job으로 분리하고 중복 방지 key·distributed lock·run metrics를 둡니다.
5. pipeline 처리량, map query latency, batch duration, failed-source rate를 측정해 정량 결과를 남깁니다.
6. HUG·community·wishlist·server session prototype을 MVP code와 명확히 격리합니다.
7. JWT access/refresh token type claim, internal service IAM, secret WIF를 적용합니다.

## 10. 예상 면접 질문 20개와 답변 핵심

| # | 질문 | 답변 핵심 포인트 |
|---:|---|---|
| 1 | 왜 실제 매물이 아니라 합성 매물을 썼나요? | 공급 계약 없는 MVP; 실제 거래 건물·가격 범위 anchor; 중개 서비스로 오해하지 않기; source field `MVP_SYNTHETIC` |
| 2 | 국토부 8개 endpoint를 어떻게 통합했나요? | `SOURCE_CONFIG`+field alias→20개 common transaction fields; raw fixture/seed 검증은 4개 source; 나머지 4개는 fixture 필요; normalized data만 load |
| 3 | pipeline 재실행 중 중복은 어떻게 막나요? | `source_api + source_transaction_key`, property source unique, legal `content_hash`; upsert·verify command |
| 4 | 전국 최근 12개월이면 요청량이 큰데 어떻게 제어하나요? | lawd code×month×source plan, pagination, request delay, limit-regions/requests, raw manifest; 자동 retry/backoff·운영 분할·watermark는 개선점 |
| 5 | 지도 cluster를 어떻게 구현했나요? | server zoom mode; lat/lng grid aggregate SQL; property cap; 별도 cluster library 없음; grid 오차 trade-off |
| 6 | 지역 marker와 keyword 검색 상태가 왜 달랐나요? | keyword가 frontend local filter에만 존재; viewport payload·기존 common builder에 keyword 추가; public list 정렬; active search count; review 후 trim/escape |
| 7 | SQL injection은 어떻게 막았나요? | LLM arbitrary SQL 없음; allowed field/range map; psycopg/JDBC parameter binding; dynamic fragments는 code constant |
| 8 | 법령 chunk 전략은 무엇인가요? | 조문 metadata·deterministic chunk·hash; exact chunk size는 code 설명; dry-run/write 분리; content hash conflict |
| 9 | RAG hallucination을 어떻게 줄였나요? | retrieved legal cards만 법률 답변 context; retrieval 결과를 prompt/card에 전달하는 test; no-card면 최종 법률 답변용 live LLM 미호출(Supervisor routing은 별도); 사후 검증·품질 평가는 없어 방지 보장 금지 |
| 10 | REST fallback이 느리고 위험하지 않나요? | non-prod의 `psycopg.OperationalError`만 대상; paged rows+local cosine; production error propagation; 모든 오류를 복구하지 않는 개발 경로 |
| 11 | pgvector IVFFlat 설정은? | vector(1536), cosine, lists=100, current probes=100; 소규모 데이터에서 누락을 줄이려는 설정이나 측정 자료 없음; probes 최초 도입은 팀원, parameter binding 오류를 literal SQL로 고친 후속 수정은 본인 |
| 12 | 안전 점수 formula 근거는? | MVP documented heuristic 30/25/25/20, radius 300/500m, normalized cap; 공인 위험도 아님; calibration/user validation 필요 |
| 13 | distance 계산을 왜 Java에서 했나요? | current DB에 PostGIS 없음; bounds prefilter+Haversine; 100-property chunk; simple MVP; scale 시 PostGIS/tiling 검토 |
| 14 | 한 public API가 실패하면 어떻게 되나요? | 상위 source 예외는 분리하고 다음 source 계속; conflict upsert·page cap·timeout guard; 일부 client의 empty-result 변환 때문에 실패 관측 누락은 개선점 |
| 15 | Spring과 FastAPI failure를 어떻게 처리했나요? | connect/read timeout, internal API key, structured fallback card; current IAM/circuit breaker 부족 |
| 16 | JWT 인증을 직접 구현했나요? | core는 팀원 기여; 나는 authenticated chat contract·integration 사용; access 15m/refresh 7d, Redis rotation 구조 이해; 자신의 범위 명확히 |
| 17 | Supervisor 개선 수치는 본인 성과인가요? | 팀원 PR #63; team project result; 본인은 worker/RAG/tool boundary; recall-latency trade-off 설명 |
| 18 | CI/CD라고 부를 근거는? | actual Actions: Spring 16, AI 9, GitLab sync 8 success; Vercel deployment; 하지만 test gate 없음, CD 중심이라고 정확히 표현 |
| 19 | 현재 가장 심각한 결함은? | FastAPI `workersCalled` 등 metadata 유실과 Spring/FE `intent` drift; 전체 chat outage로 단정 금지; consumer contract test와 timeout budget을 먼저 개선 |
| 20 | 성능을 얼마나 개선했나요? | 내 기능의 before/after latency 수치는 없음; 구조적 결과만 말하기; Supervisor 저장 평가만 팀 결과로 인용; 앞으로 측정 계획 |

## 11. 각 질문에 답할 때 지켜야 할 선

- “운영에서 4종 API가 모두 정상 수집됐다” → 네 source 모두 수정 후 성공 로그가 없으므로 금지.
- “전체 AI agent를 만들었다” → Supervisor는 팀원 기여이므로 금지.
- “JWT 인증을 구현했다” → 본인은 core author가 아니므로 금지.
- “성능을 N% 개선했다” → 본인 기능의 before/after 수치가 없으므로 금지.
- “사용자가 만족했다” → 사용자 test 기록이 없으므로 금지.
- “모든 test가 현재 통과한다” → 이번 조사에서 재실행하지 않았으므로 과거 PR 기록이라고 한정.

## 12. 이력서용 핵심 문장 3개

1. 국토부 실거래가 8개 endpoint configuration과 공통 alias normalizer를 만들고, 건물 anchor·Naver geocoding·지역/건물 통계·합성 매물을 연결한 충돌 키 기반 offline pipeline을 구현했습니다. 저장소에서 호환성이 확인되는 것은 4개 source 8,121건이며 DB 반영은 PR 보고 수준입니다.
2. JSON·XML·Web Mercator 좌표와 서로 다른 인증 방식을 가진 네 안전시설 client를 공통 domain으로 통합하고, CCTV 403·service key 401 기록에 source 전환·URL encoding·failure isolation 코드로 대응했습니다. 운영 성공은 별도 확인이 필요합니다.
3. 법령 chunk·embedding·pgvector retrieval과 검색 근거 제한 answer를 구현하고, Spring 시세·안전 API를 FastAPI worker·초기 frontend analysis card까지 contract test 중심으로 연결했습니다.

## 13. 자기소개서에 활용할 경험 3개

### 경험 1. 정상 fixture를 넘어 배포 로그 실패로 보강한 외부 API client

fixture 기반 parser 이후 Issue #90에는 CCTV CSV 403이, Issue #92의 Cloud Run 로그에는 401·invalid key가 기록됐다. 제공자 내부 원인이나 401의 단일 원인을 단정하지 않고 source contract를 재검토해 CCTV OpenAPI 전환, decoding key encoding, Safemap opt-in, Web Mercator 변환, source isolation을 적용했다. “문제가 생기면 재현 가능한 경계와 회귀 test로 바꾸는 개발자”라는 소재로 활용할 수 있다.

### 경험 2. 임시 seed를 반복 실행 가능한 pipeline으로 바꾼 경험

빠른 UI 검증을 위해 대용량 seed와 SQL chunk를 먼저 만들었지만, repository 크기와 수동 DB 반영 문제가 드러났다. 초기 결과를 버리는 데 그치지 않고 전국 범위를 만들 수 있는 request plan, common normalization, geocoding, stats, conflict upsert, verify command로 전환했다. 자동 retry·운영 scheduler는 없으므로 “임시 구현의 목적을 인정하면서 재실행 가능한 bootstrap 경계로 리팩터링한 경험”으로 활용할 수 있다.

### 경험 3. AI도 contract가 깨질 수 있다는 것을 발견한 경험

Spring-FastAPI `analysisCards`를 contract test로 연결했지만 뒤의 Supervisor 변경에서 `intent`가 `workersCalled`로 바뀌며 consumer drift가 남았다. 이를 숨기지 않고 producer·consumer schema test, compatibility strategy, CI gate가 필요하다는 개선안으로 정리했다. “완성 주장보다 system boundary를 검증하고 한계를 설명하는 태도”를 보여 주는 소재다.
