# 김용휘의 기여

## 1. 본인 식별과 기여 판정 원칙

본인은 GitHub `HOKAGO-MEMORIES`, Git author `HOKAGO-MEMORIES`·`김용휘`·`Kim YongHwi`, email `minchotejava@gmail.com`로 확인됐다. 동일 email commit 164개, 본인 작성 PR 46개, 본인 작성 Issue 37개가 있다.

숫자만으로 기여도를 산정하지 않았다. 아래 항목은 본인 author의 기능 commit, 본인 작성 PR·Issue, 실제 diff, 최종 발표자료의 역할 언급을 함께 만족하는 범위만 담았다.

## 2. 핵심 기여 요약

| 범주 | 기여 내용 | 대표 근거 | 형태 | 포트폴리오 가치 |
|---|---|---|---|---|
| 데이터 모델링·외부 API | 국토부 8개 endpoint 설정과 공통 alias normalizer, 합성 매물·통계 offline pipeline | [PR #8](https://github.com/ssafy-salman/salmanhae/pull/8), [#33](https://github.com/ssafy-salman/salmanhae/pull/33) | Git 기록상 본인 주도. raw/seed 호환성은 4개 source 확인 | 매우 높음 |
| Backend API·지도 | bounds/detail API와 zoom별 region/cluster/property query, filter contract 구현 | [PR #10](https://github.com/ssafy-salman/salmanhae/pull/10), [#54](https://github.com/ssafy-salman/salmanhae/pull/54)~[#67](https://github.com/ssafy-salman/salmanhae/pull/67), [#95](https://github.com/ssafy-salman/salmanhae/pull/95) | BE/FE vertical slice | 매우 높음 |
| 법률 RAG·AI 연동 | 법령 chunk·embedding·pgvector retrieval·근거 제한 answer·live LLM·fallback·초기 UI 연결 | [PR #17](https://github.com/ssafy-salman/salmanhae/pull/17)~[#35](https://github.com/ssafy-salman/salmanhae/pull/35) | Git 기록상 본인 주도, Supervisor·최종 UI 제외 | 매우 높음 |
| 서비스 간 계약 | Spring 시세·안전 API와 FastAPI worker, `analysisCards`, frontend card를 연결 | [PR #37](https://github.com/ssafy-salman/salmanhae/pull/37)~[#50](https://github.com/ssafy-salman/salmanhae/pull/50) | Git 기록상 본인 주도, 다른 AI 변경과 통합 | 높음 |
| 안전 data·batch | 4종 source client/normalization, source 격리, 조건부 scheduler, Haversine 시설 접근성 score, API 장애 대응 코드 | [PR #69](https://github.com/ssafy-salman/salmanhae/pull/69)~[#93](https://github.com/ssafy-salman/salmanhae/pull/93) | Git 기록상 본인 주도, 4종 운영 성공은 미확인 | 매우 높음 |
| 배포·협업 infra | 모노레포 전환, GitHub→GitLab sync, Docker/Cloud Run workflow | [`a259751`](https://github.com/ssafy-salman/salmanhae/commit/a259751af0a8d864368b56549f962c83eba589cb), [PR #52](https://github.com/ssafy-salman/salmanhae/pull/52), [`2a81344`](https://github.com/ssafy-salman/salmanhae/commit/2a81344328900226045f3090474392f15d8c1d5f) | 공통 infra 주도 | 높음 |
| 테스트·문서화 | contract/parser/fallback/DAO/controller/store test와 API/domain/batch/deploy 문서 동기화 | 각 기능 PR의 test·docs diff | 기능과 함께 지속 | 높음 |

## 3. 상세 기여

### 3.1 국토부 실거래가 기반 데이터 파이프라인

- **무엇을 담당했는가**: 거래·매물 schema, 국토부 XML fetch/normalize, Naver geocoding, 합성 매물 seed, 지역·건물 통계, Supabase migration/load/verify pipeline.
- **왜 필요했는가**: 실제 중개 매물 공급원이 없는 MVP에서 임의 좌표·가격만 쓰지 않고 실제 거래 건물·가격 범위에 기반한 지도 탐색을 검증하기 위해서다.
- **어떻게 구현했는가**:
  - `source_api + source_transaction_key` unique key로 거래 중복 방지.
  - `building_key`로 거래와 매물 anchor 연결.
  - timeout과 API 기술문서 parameter 보정. 현재 통합 pipeline에는 자동 retry/backoff가 없음.
  - 초기에는 SQL Editor용 chunk를 생성했고, 이후 generated data를 Git에서 제거해 `pipeline.py`의 충돌 키 기반 DB upsert로 전환.
- **결과**: Git diff에서 거래 8,121건·매물 300건 artifact를 확인했고 PR #8에는 SQL Editor 반영 성공 보고가 있다. 실제 DB 반영은 독립 검증되지 않았다. 거래 artifact는 아파트·오피스텔 전월세·매매 4개 source, 2026년 5~6월 일부 지역 범위다. PR #33에서 더 넓은 지역·월·8 endpoint를 계획할 수 있는 plan/run/load/verify 명령으로 정리했지만 전체 실행과 현재 운영 row 수는 확인 필요다.
- **주요 파일**: [`scripts/data_pipeline/pipeline.py`](../scripts/data_pipeline/pipeline.py), [`database/migrations/202606160001_create_properties.sql`](../database/migrations/202606160001_create_properties.sql), [`database/migrations/202606230001_create_price_stats.sql`](../database/migrations/202606230001_create_price_stats.sql).
- **대표 commit**: `870fe41`, `d1124c8`, `1d903b2`, `d448e31`, `79ae977`, `4a1a6fe`.
- **기여 형태**: commit·PR 기록상 본인 주도. 생성 데이터를 소비한 backend/frontend는 팀 공통 결과이며, 저장소 밖 회의·pairing 여부는 확인 필요.
- **예상 후속 질문**: 8개 endpoint 설정 중 실제 raw 호환성을 확인한 source는 무엇이며 alias는 어떻게 설계했는가? 중복 판단 key는 왜 그 조합인가? 전체 실행 시 요청량·retry·checkpoint를 어떻게 보강할 것인가?

### 3.2 공개 매물 API와 지도 vertical slice

- **무엇을 담당했는가**: Spring 공개 매물 조회·상세 API, 공통 response/error, H2/MockMvc/HTTP tests, Axios/Naver map 연결, CORS, marker/detail panel.
- **왜 필요했는가**: DB에 넣은 합성 매물을 실제 사용자 지도 흐름까지 연결하고 backend contract를 검증하기 위해서다.
- **어떻게 구현했는가**: bounds validation과 transaction/property/price filter를 service/DAO로 넘기고, frontend는 지도 bounds가 바뀔 때 Spring만 호출하도록 구성했다.
- **결과**: [PR #10](https://github.com/ssafy-salman/salmanhae/pull/10)에서 API와 HTTP 통합 test, [PR #12](https://github.com/ssafy-salman/salmanhae/pull/12)에서 Naver map·detail·CORS를 연결했다.
- **주요 파일**: `PropertyController`, `PropertyServiceImpl`, `JdbcPropertyDao`, `frontend/src/api/properties.js`, `MapExplorer.vue`.
- **대표 commit**: `9b7c9f4`, `c1d8fbd`, `ad5a86b`, `af0c726`, `7946907`.
- **기여 형태**: backend와 frontend 연동을 본인이 주도. Naver map SDK와 Spring REST 경계를 함께 담당.
- **예상 후속 질문**: bounds validation 기준은 무엇인가? 왜 frontend가 FastAPI를 직접 호출하지 않는가? CORS와 Spring Security CORS의 차이는 무엇인가?

### 3.3 zoom별 viewport와 검색 contract 일치

- **무엇을 담당했는가**: zoom을 SIDO/SIGUNGU/DONG/cluster/property mode로 나누는 API, grid aggregate SQL, marker rendering, invalid bounds 방어, 가격·유형 공통 filter와 이후 keyword의 viewport/public list 연결.
- **왜 필요했는가**: 넓은 지도에서 개별 매물을 모두 반환하면 가독성과 응답량이 나빠지고, 프론트 local-only keyword와 region marker의 검색 상태가 달랐기 때문이다.
- **어떻게 구현했는가**:
  - server가 zoom에 따라 response item type을 결정.
  - cluster는 위경도 grid SQL aggregate.
  - broad zoom은 heavy region-stat join 대신 visible active property aggregate로 보정.
  - 초기 viewport 구현에서 가격·유형 DAO filter builder를 region/cluster/property query가 공유.
  - PR #95에서 keyword와 public bounds list를 기존 builder에 정렬하고, CodeRabbit 지적 후 `%`, `_`를 literal로 escape하며 frontend keyword를 trim.
- **결과**: [PR #54](https://github.com/ssafy-salman/salmanhae/pull/54)~[#67](https://github.com/ssafy-salman/salmanhae/pull/67), [#95](https://github.com/ssafy-salman/salmanhae/pull/95)에 backend full tests와 frontend test/build 기록이 있다.
- **대표 commit**: `443685f`, `a4fbcfa`, `8782011`, `26c5b63`, `deaddfc`, `ad3de24`, `6cb0c85`.
- **기여 형태**: backend query·API·frontend rendering을 본인이 연결.
- **예상 후속 질문**: zoom threshold를 어떻게 정했는가? grid cluster의 오차는? 지역 평균이 실거래가가 아닌 활성 매물 값인 이유는? filter query 중복을 어떻게 줄였는가?

### 3.4 법률 RAG 코드 경로

- **무엇을 담당했는가**: Spring/FastAPI chat contract, 법령 schema·chunk·hash·embedding·upsert, pgvector retrieval, 근거 제한 prompt/answer, frontend legal card 초기 연결, live LLM, non-prod fallback.
- **왜 필요했는가**: 법률 질문에 일반 LLM 지식만 답하면 근거를 확인할 수 없고, 초기 stub/template은 실제 검색·생성을 검증하지 못했다.
- **어떻게 구현했는가**:
  - law/article 단위 metadata와 `content_hash` unique key.
  - dry-run과 명시적 `--write`를 분리.
  - query embedding 후 `<=>` cosine search, top-k clamp·timeout.
  - legal card가 없을 때 최종 법률 답변용 live LLM을 호출하지 않는 deterministic 근거 부족 안내. Supervisor routing LLM은 별도.
  - non-prod에서 `psycopg.OperationalError`가 나면 project ref를 추출할 수 있고 service-role key가 설정된 경우 HTTPS REST로 rows를 읽고 local cosine 계산; production에서는 같은 오류를 숨기지 않음. 이는 모든 DB 오류를 처리하는 fallback이 아님.
- **결과**: [PR #17](https://github.com/ssafy-salman/salmanhae/pull/17)~[#35](https://github.com/ssafy-salman/salmanhae/pull/35)의 phase별 test 기록. PR #35 당시 34 tests passed와 direct FastAPI legalCards 3개 확인.
- **주요 파일**: `legal_document_chunks` migration, `ingest_legal_docs.py`, `embedding_client.py`, `supabase_client.py`, `retriever.py`, `prompts.py`, `llm_client.py`.
- **기여 형태**: 본인 주도. 이후 Supervisor graph 전환은 팀원 구현이므로 분리.
- **예상 후속 질문**: chunk 경계·hash 기준은? IVFFlat의 trade-off는? fallback을 production에서 막은 이유는? retrieval result로 hallucination을 어떻게 제한했는가?

### 3.5 Spring-FastAPI 시세·안전 분석 계약

- **무엇을 담당했는가**: `selectedPropertyId`, `analysisCards`, Spring 거래·시세·안전 API, FastAPI SpringClient, worker mapping, 저장 수치 기반 answer, frontend card 초기 연결, phase QA.
- **왜 필요했는가**: AI worker가 stub 값을 반환했고 Spring domain data와 AI answer 사이에 명시적 contract가 없었다.
- **어떻게 구현했는가**:
  - contract test를 먼저 만들고 양쪽 DTO/schema를 맞춤.
  - Spring API를 stored data 조회 전용으로 구성.
  - FastAPI에서 확인된 timeout·API failure·미선택 경로를 구조화된 fallback payload로 반환.
  - answer가 `analysisCards`와 `tool_results`의 실제 숫자만 사용하도록 별도 service/prompt를 구성하고 0값도 보존.
- **결과**: PR #50 기록상 backend chat test, AI 57 tests, frontend test/build. 이후 팀원의 Supervisor 응답 변경이 Spring/FE까지 동기화되지 않아 현재 `workersCalled` drift가 남았다.
- **대표 PR**: [#37](https://github.com/ssafy-salman/salmanhae/pull/37), [#39](https://github.com/ssafy-salman/salmanhae/pull/39), [#41](https://github.com/ssafy-salman/salmanhae/pull/41), [#46](https://github.com/ssafy-salman/salmanhae/pull/46), [#48](https://github.com/ssafy-salman/salmanhae/pull/48), [#50](https://github.com/ssafy-salman/salmanhae/pull/50).
- **기여 형태**: 서비스 간 vertical slice 주도. current Supervisor 자체는 팀원 기여.
- **예상 후속 질문**: 내부 API 인증은? circuit breaker가 없는 이유는? consumer contract test를 어떻게 추가할 것인가? 지역 시세와 선택 매물 시세의 data source가 왜 다른가?

### 3.6 안전시설 수집·사전 점수와 배포 로그 장애 대응

- **무엇을 담당했는가**: safety schema/API, JSON·XML parser와 이전 CSV 경로, source 격리 ingestion, 조건부 scheduler, Haversine 시설 접근성 score, `property_score_stat`, Spring→AI 연결, 403/401 기록에 대한 endpoint·key·coordinate 처리 수정.
- **왜 필요했는가**: provider마다 field·pagination·coordinate·인증 방식이 달랐고 request-time public API 호출은 느리고 불안정했다.
- **어떻게 구현했는가**:
  - 공통 `NormalizedSafetyFacility`과 source client interface.
  - invalid coordinate skip, XML parser 보안 hardening, page stop·cap.
  - source가 상위로 예외를 전달하면 나머지 upsert 계속. 다만 일부 client가 오류를 빈 결과로 바꿔 실패 count를 놓칠 수 있음.
  - candidate bounds로 시설을 줄인 뒤 Java Haversine으로 300m/500m count.
  - 30/25/25/20 규칙 기반 시설 접근성 score를 batch에서 계산해 저장. 범죄 발생 가능성을 계산하지 않음.
  - CCTV download 403 후 JSON OpenAPI 전환, Web Mercator→WGS84, decoding key 인코딩, Safemap opt-in.
- **결과**: [PR #69](https://github.com/ssafy-salman/salmanhae/pull/69)~[#93](https://github.com/ssafy-salman/salmanhae/pull/93)의 테스트 정의·PR 실행 기록과 deploy success가 있다. 이는 네 source의 live 수집 성공을 증명하지 않는다. Safemap은 opt-in이고 scheduler 운영 안정성은 남은 과제다.
- **대표 commit**: `4bf127f`, `26c7aa7`, `0bee1d6`, `e05a637`, `d2aa9b6`, `7ab97f3`, `cad48d2`, direct `38199b5`, `02fa47a`.
- **기여 형태**: 본인 주도. API source 자체의 품질과 운영 key는 외부 dependency.
- **예상 후속 질문**: 왜 PostGIS가 아닌 Haversine인가? candidate chunk 100의 근거는? 중복 scheduler를 어떻게 막을 것인가? provider schema 변경을 어떻게 감지할 것인가?

### 3.7 모노레포·GitLab 동기화·Cloud Run 배포

- **무엇을 담당했는가**: module 통합, Harness migration, GitHub main→GitLab monorepo/artifact sync, Spring·FastAPI Docker/Cloud Run action, deployment guide.
- **왜 필요했는가**: SSAFY 제출은 GitLab 경로를 요구하면서 실제 개발은 GitHub PR 중심이었고, 두 backend runtime을 독립적으로 배포해야 했다.
- **어떻게 구현했는가**:
  - single Git history와 module build 경계를 유지.
  - `git subtree split`으로 artifact만 별도 GitLab project에 sync.
  - path filter로 Spring/FastAPI deploy 분리.
  - secret은 GitHub/Cloud Run env로 분리.
- **결과**: GitHub Actions 이력에서 backend 16회, backend-ai 9회, GitLab sync 8회 success. Vercel production deployment도 success 기록.
- **대표 근거**: [`a259751`](https://github.com/ssafy-salman/salmanhae/commit/a259751af0a8d864368b56549f962c83eba589cb), [PR #5](https://github.com/ssafy-salman/salmanhae/pull/5), [PR #52](https://github.com/ssafy-salman/salmanhae/pull/52), [`2a81344`](https://github.com/ssafy-salman/salmanhae/commit/2a81344328900226045f3090474392f15d8c1d5f).
- **기여 형태**: 공통 infra 주도. 최종 GitLab 제출물은 팀 공동 결과.
- **예상 후속 질문**: 왜 main sync와 develop deploy인가? action에 test gate가 없는 이유는? GCP key JSON 대신 WIF를 쓰면 무엇이 달라지는가? artifact subtree의 장단점은?

### 3.8 테스트·문서·자동 review 반영

- **기여 내용**: 기능마다 controller/service/DAO/parser/fallback/store/util test와 API/domain/batch/deploy 문서를 같은 PR에 포함했다.
- **구체적 사례**:
  - PR #95에서 automated review 3건(SQL wildcard literal, API spec target, frontend trim)을 `6cb0c85`로 반영.
  - PR #77에서 candidate query·upsert·공간 순서를 여러 follow-up commit으로 보정.
  - PR #35에서 fallback을 production까지 삼키지 않도록 `0a9b0b2`로 제한.
- **제한**: 사람 review·approval·갈등 대화는 저장소에 없다. “팀원과 코드 리뷰로 합의했다”는 문장은 쓰지 않는다.

## 4. 본인 기여가 아닌 영역

| 영역 | 확인된 주도자 | 근거 | 포트폴리오 표현 |
|---|---|---|---|
| Spring Security 인증 core | `crolvlee` | PR #13, #28와 author | “팀원이 구현한 인증 체계 위에 인증된 chat contract를 연결” |
| Router→Supervisor 전환 | `crolvlee` | [PR #63](https://github.com/ssafy-salman/salmanhae/pull/63), Co-authored trailers | “팀원이 Supervisor로 확장; 나는 기존 RAG·analysis worker 경계를 제공” |
| auth frontend·router guard | `crolvlee` | PR #83, #85, #87 | 본인 구현으로 표현하지 않음 |
| final Chatbot markup/style·local session UI | `crolvlee` | PR #80, #89, #104 (후속 #107은 가격 카드 보정, #110은 지도 디자인) | 본인 구현으로 표현하지 않음 |

## 5. 포트폴리오용 핵심 문장

1. 국토부 8개 endpoint 설정과 공통 alias normalizer를 만들고 건물 anchor·통계·지오코딩·합성 매물을 연결한 offline pipeline을 구축했다. raw page 재사용과 충돌 키 upsert가 있으며, 저장소 artifact로 호환성이 확인되는 것은 4개 source 8,121건이다.
2. 서로 다른 format과 좌표계를 가진 네 안전시설 client를 공통 model로 통합하고, 403·401 기록에 대응해 endpoint·service key encoding을 보강했다. 네 source의 운영 성공은 별도 확인이 필요하다.
3. 법령을 content hash 기반으로 chunk·embedding하고 pgvector retrieval 결과를 prompt와 카드 근거로 제한하는 RAG를 구현했으며, non-prod `OperationalError`에는 REST fallback을 두되 production error는 숨기지 않았다.
4. 지도 zoom별 지역·cluster·매물 query와 당시 지원한 search filter를 하나의 DAO 조건 builder로 맞췄다. 현재 추가된 월세 범위·복수 거래유형은 다시 계약 정렬이 필요하다.
5. Spring의 stored 시세·안전 API를 FastAPI worker와 `analysisCards` contract로 연결하고, AI answer가 tool result의 구체 수치만 설명하도록 구성했다.

## 6. 기여도 표현 가이드

- 추천 표현: “김용휘가 구현한 PR 범위는 …”, “팀원이 만든 인증/Supervisor 위에 …를 연결했다.”
- 피할 표현: “전체 backend와 AI agent를 혼자 구현했다.”, “Supervisor를 설계했다.”, “JWT 인증을 구현했다.”
- 숫자로 기여율을 말해야 한다면 commit 수 대신 본인이 소유한 기능 범위와 대표 PR을 제시하고, 정확한 비율은 [`07-open-questions.md`](07-open-questions.md)의 확인 항목으로 남긴다.
