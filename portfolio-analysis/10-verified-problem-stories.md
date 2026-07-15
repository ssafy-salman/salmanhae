# 검증된 문제 해결 사례

## 1. 검증 방법

기존 문서에서 가장 강하다고 평가한 세 사례를 Issue의 문제 정의, PR 본문, 실제 diff, 후속 커밋, 현재 코드 순서로 다시 확인했다. “왜 그 선택을 했는가”는 기록된 근거만 사용했고, 로그나 회의 내용이 없으면 `[본인 확인 필요]`로 남겼다. 배포 성공과 기능 성공, 테스트 정의와 테스트 실행도 분리했다.

## 2. 집중 재검증 1 — 안전시설 API의 이질성·인증 실패·부분 실패

### 상황

매물 주변 안전시설을 요청 시점에 외부 API로 조회하지 않고, 배치로 수집해 DB에서 제공하는 기능을 구현하던 단계였다. 대상은 CCTV, 비상벨, 보안등, 경찰관서 네 종류였다.

### 실제 현상

- Issue #90에는 기존 CCTV CSV 접근의 HTTP 403이 기록돼 있다.
- Issue #92에는 Cloud Run 로그에서 CCTV·비상벨 401과 생활안전지도 API key 관련 오류가 기록돼 있다.
- 네 소스는 응답 형식, endpoint 설정, 인증 키, 좌표계가 서로 달랐다.
- 현재 client는 HTTP·parse 실패를 내부에서 빈 목록 또는 부분 목록으로 바꿀 수 있어, 상위 서비스의 `failedSourceCount`가 실제 실패를 놓칠 수 있다.

### 문제 발견 주체

Issue #90과 #92의 작성자와 후속 수정 커밋 작성자는 본인이다. 다만 최초로 로그를 본 사람이 본인인지, 팀원이 전달했는지까지는 저장소에서 확인되지 않는다. `[본인 확인 필요]`

### 원인

코드와 기록으로 확인되는 원인은 다음 범위다.

- CCTV CSV endpoint가 제공자 측에서 403을 반환했다. 제공자 내부의 구체 원인은 확인되지 않는다.
- 공공 API마다 키 전달 방식과 URL encoding 요구가 달랐고, 선택적 source까지 일괄 실행하면 설정되지 않은 키로 호출될 수 있었다.
- 보안등에는 WGS84뿐 아니라 Web Mercator 계열 `XMAP/YMAP/GEOM` 좌표가 포함될 수 있었다.
- client가 예외를 삼키는 구조 때문에 “실패했지만 0건 수집 성공처럼 보이는” 관측성 문제가 남았다.

### 내가 맡은 역할

| 활동 | 확인된 역할 |
|---|---|
| 문제 정의 | Issue #68/#70/#72/#74/#76/#78/#90/#92 작성 |
| 원인 분석 | endpoint·인증·좌표 형식 차이를 코드와 Issue에 반영 |
| 해결책 설계 | 공통 시설 모델, source별 client/parser, 좌표 정규화, source opt-in, key encoding, source 단위 계속 진행 구조 |
| 구현 | PR #69/#71/#73/#75/#77/#79/#91/#93의 핵심 diff 작성 |
| 테스트 | client/parser·좌표·점수 테스트 정의. PR 본문의 실행 기록은 있으나 현재 CI 배포 gate는 아님 |
| 코드 리뷰 | 자동 리뷰 지적과 후속 수정은 확인되나 사람 리뷰 과정은 저장소에서 확인되지 않음 |
| 프론트·다른 서버 조율 | PR #79에서 Spring summary를 FastAPI 안전 카드 경로에 연결. 최종 Chatbot 카드 디자인은 팀원 후속 변경 |
| 최종 병합 | 관련 PR의 merge는 확인되지만 승인·병합 주체를 개인 성과로 주장하지 않음 |

### 검토한 대안

- 거리 계산은 PostGIS `ST_DWithin`과 “DB bbox 후보 조회 후 Java Haversine”을 Phase 5 기록에서 비교했다. 프로젝트 제약에서 공간 확장 의존을 늘리지 않는 후자를 선택했다.
- 경찰관서 source는 필수 기본 실행 대신 설정된 경우만 켜는 opt-in으로 바꿨다.
- CCTV는 접근 불가능한 CSV 경로를 유지하지 않고 JSON API client로 교체했다.

그 밖의 재시도 횟수, circuit breaker, distributed lock 대안은 Git/문서에 결정 기록이 없으므로 검토한 것처럼 쓰지 않는다.

### 최종 해결

- source별 client/parser를 공통 `SafetyFacility` 저장 모델로 변환했다.
- Web Mercator 좌표를 위·경도로 변환하는 경로를 추가했다.
- source별 API key URL encoding과 선택 실행 조건을 보강했다.
- 한 source가 상위로 예외를 던지면 나머지 source는 계속 처리하도록 수집 서비스를 구성했다.
- 수집과 별도로 bbox 후보 축소와 Haversine 거리 계산으로 매물별 시설 count를 사전 계산했다.

### 검증과 결과

- 네 source의 client/parser와 점수 계산 테스트 정의가 존재한다.
- 관련 PR은 병합됐고 후속 Cloud Run 배포 workflow 성공 이력이 있다.
- 코드 수준에서는 JSON CCTV 전환, key encoding, source opt-in이 현재 유지된다.
- 그러나 PR #93 이후 네 source가 실제 운영에서 모두 200 응답을 받고 행을 적재했다는 로그는 없다. 배포 성공은 외부 API 호출 성공을 증명하지 않는다.

### 현재 상태와 한계

핵심 구조는 현재 코드에 존재한다. 다만 client 내부 실패가 빈 결과로 축소될 수 있고, scheduler는 기본 비활성화이며 Cloud Run 다중 instance에서 단일 실행을 보장하는 lock이 없다. 따라서 이 사례는 **핵심 사례**로 사용할 수 있지만 “운영 장애 완전 해결”이 아니라 “이질적 외부 API를 격리하고 인증·좌표 위험을 줄인 구현”으로 표현해야 한다.

## 3. 집중 재검증 2 — 법률 RAG의 stub 제거와 개발 환경 DB fallback

### 상황

법률 질문 기능은 초기에 계약과 화면 흐름을 먼저 맞추는 stub 단계였고, 이후 실제 embedding·pgvector 검색과 근거 카드가 필요했다. 로컬 개발 환경에서는 직접 PostgreSQL 접속이 차단되는 경우도 고려해야 했다.

### 실제 현상

- 초기 계약 단계와 이후 실제 검색 구현이 별도 PR로 이어진다.
- `legal_document_chunks` 테이블, embedding vector, cosine 검색, 근거 카드 생성 코드가 현재 존재한다.
- 비운영 환경에서 `psycopg.OperationalError`가 발생하고 project ref 추출·service-role key 조건을 만족하면 REST 조회 후 로컬 cosine 계산을 시도한다.
- 실제 법령 원문 JSON, 현재 DB row 수, 검색 품질 평가 결과는 저장소에 없다.

### 문제 발견 주체

Issue #16부터 #34까지 단계별 Issue와 PR은 본인이 작성했다. 다만 “직접 DB 차단”을 최초로 경험한 환경과 로그는 PR 설명 외 독립 증거가 없어 구체 상황은 `[본인 확인 필요]`다.

### 원인

- stub은 검색 결과나 출처를 만들지 못해 실제 법률 답변 요구를 충족하지 못했다.
- 개발 네트워크에서 PostgreSQL 직접 접속이 `OperationalError`로 실패할 수 있었다.
- 검색 경로와 UI 계약을 한 번에 바꾸면 어느 계층에서 오류가 났는지 분리하기 어려웠다.

### 내가 맡은 역할

| 활동 | 확인된 역할 |
|---|---|
| 문제 발견 | 단계별 Issue 작성자는 본인. direct DB 차단을 처음 관찰한 사람·환경은 PR 자기보고 밖에서 확인되지 않음 |
| 원인 분석 | stub·외부 client 연결 시점·직접 PostgreSQL 오류와 운영 장애 은닉 위험을 분리 |
| 해결책 설계 | 800자 chunk/120자 overlap, content hash, vector(1536), cosine top-k, 최대 세 근거 카드, 비운영 fallback |
| 구현 | PR #17/#19/#21/#23/#25/#27/#31/#35의 핵심 코드 |
| 테스트 | chunk/upsert/retriever/answer/card/fallback 테스트와 PR 실행 기록 |
| 코드 리뷰 | 자동 리뷰와 후속 commit은 일부 확인되나 사람 review/approval은 확인되지 않음 |
| 프론트·다른 서버 조율 | 초기 Spring/FastAPI legal contract와 Vue legal card를 직접 연결. LangGraph supervisor는 팀원 후속 구현 |
| 최종 병합 | 관련 PR은 merge됐지만 승인·병합 주체를 본인 역할로 확대하지 않음 |

### 검토한 대안

- 초기 단계에서는 stub으로 계약을 먼저 고정하고, 이후 실제 DB 검색으로 교체하는 단계적 접근을 사용했다.
- 개발 DB 직접 연결 실패 시 전체 기능을 끄는 대신, 비운영 환경에서만 REST로 row를 가져와 로컬 cosine을 계산하는 fallback을 추가했다.
- 운영 환경에서는 이 fallback을 허용하지 않고 직접 DB 오류를 드러내도록 분리했다.

검색 임계값, reranker, hybrid search, embedding batch 방식은 선택 기록이 없으므로 실제 검토 대안으로 주장하지 않는다.

### 최종 해결

- 오프라인 JSON을 정규화하고 800자 단위로 chunk한 뒤 content hash로 upsert하는 CLI를 구현했다.
- OpenAI-compatible `/embeddings` 응답을 vector(1536)에 저장하고 pgvector cosine 거리로 검색한다.
- 최대 세 검색 결과만 prompt와 `legalCards`에 넣고, 결과가 없으면 최종 법률 답변용 live LLM을 호출하지 않고 근거 부족 안내를 반환한다. Supervisor routing LLM은 별도다.
- `psycopg.OperationalError`에 한해 비운영 REST fallback을 시도하며 project ref와 service-role key가 필요하다.
- LangGraph는 이 검색을 직접 수행하는 기술이 아니라, supervisor가 legal worker를 호출하는 오케스트레이션 계층으로 사용된다.

### 현재 RAG 구성 상세

| 항목 | 확인된 구현 | 검증 한계 |
|---|---|---|
| 대상 법령 | 설계 대상은 주택임대차보호법과 전세사기피해자 지원 및 주거안정 특별법 | 실제 입력 파일·현재 적재 row가 없어 두 법령 운영 사용은 미확인 |
| 수집 방식 | `lawId`, `lawName`, `articleNo`, `title`, `content`, `sourceUrl`을 가진 offline JSON 배열을 CLI가 읽음 | 법령 API 자동 수집·최신화 없음 |
| 전처리·chunk | whitespace 정규화, 기본 800자, overlap 120자, 조문 metadata 유지 | 의미 단위 splitter나 시행일 기준 분리 없음 |
| 중복 기준 | 법령 ID·조문·제목·chunk index·본문을 조합한 SHA-256 `content_hash` unique upsert | 삭제된 조문이나 변경된 chunk로 더 이상 생성되지 않는 기존 hash를 지우는 reconciliation이 없고 embedding model/version을 저장하지 않음 |
| embedding | 환경변수로 정한 OpenAI-compatible `/embeddings` endpoint·key·model | 실제 provider/model 미확인, 순차 호출, batch·retry·checkpoint 없음 |
| vector 저장 | PostgreSQL `vector(1536)` | embedding 길이를 write 전에 명시 검증하는 경로 없음 |
| index | embedding non-null row의 IVFFlat cosine, `lists=100`; 현재 query `probes=100` | 초기 probes 설정은 팀원 기여, data 규모 기반 tuning 자료 없음 |
| 검색 | query embedding, `<=>` cosine 거리, `1-distance` score | threshold·법령·시행일 filter·reranker 없음 |
| top-k | 기본 3, 입력을 1~5로 clamp | 낮은 관련성도 상위 결과면 포함 가능 |
| prompt | 최대 세 card의 법령명·조문·제목·본문을 reference로 넣고 그 범위만 사용하도록 지시 | 생성 답변이 reference만 썼는지 post-validation 없음 |
| 출처 표시 | card에 법령명·조문·제목·본문·score | `sourceUrl`·시행일이 현재 card/UI에 전달되지 않음 |
| 결과 없음 | card가 0개면 최종 법률 답변용 live LLM을 호출하지 않고 근거 부족 안내; Supervisor routing LLM은 별도 | embedding·DB 예외는 동일한 zero-result가 아니라 500으로 이어질 수 있음 |
| LangGraph 역할 | supervisor가 legal worker를 선택·호출하고 결과를 state에 합침 | chunk·embedding·pgvector 자체는 LangGraph 기능이 아님; supervisor는 팀원 구현 |
| 비운영 fallback | non-prod `psycopg.OperationalError`에서 project ref와 service-role key가 있으면 REST를 1,000행씩 읽어 memory cosine 계산 시도 | port 차단에만 한정되지 않음, 운영 rethrow, 다른 DB/embedding/REST 오류 미복구, 데이터 증가 시 비용 증가, fallback이어도 tool source는 `supabase-pgvector`로 기록돼 provenance 부정확 |

### 검증과 결과

- 법률 관련 테스트와 PR의 실행 보고가 존재하고 모든 관련 PR은 병합됐다.
- 현재 코드에는 stub 대신 실제 retriever와 retrieved-card context를 쓰는 prompt-level grounded answer 경로가 연결돼 있다.
- fallback은 개발 편의 경로다. 모든 DB·embedding·REST 실패를 복구하지 않으며 운영 환경에서는 비활성이다.
- 법령 두 종의 현재 적재 여부, embedding model 실제 값, 검색 적중률과 답변 정확도는 확인되지 않는다.

### 현재 상태와 한계

코드 구조와 개인 기여는 강하지만 운영 데이터 증거가 약하다. “검색 근거를 prompt와 카드에 제한하는 grounding 장치”로는 표현 가능하고, “환각 방지·법률 정확성 보장”으로는 표현할 수 없다. Java/Spring 직무와의 직접성도 낮아 **보조 사례**가 적절하다.

## 4. 집중 재검증 3 — local keyword 결과와 줌 집계 마커의 검색 상태 불일치

### 상황

줌 단계별 region/cluster/property 조회를 완성한 뒤, 프론트 로컬 목록에만 적용되던 keyword를 지도 viewport·지역 집계에도 일관되게 반영해야 했다. 거래유형·매물유형·보증금·매매가는 이미 기존 `appendPropertyFilters`를 공유하고 있었다.

### 실제 현상

- Issue #94와 PR #95가 검색 조건 불일치를 명시한다.
- 기존 `JdbcPropertyDao.appendPropertyFilters`에 keyword 조건을 추가하고 public bounds list도 같은 helper를 재사용하게 한 diff가 있다.
- CodeRabbit은 LIKE wildcard escaping, 문서 대상, 프론트 trim을 지적했고 후속 커밋 `6cb0c85`에서 반영됐다.
- 현재는 지원되는 서버 필터에는 공통 조건이 적용되지만, 최종 프론트에 추가된 월세 범위와 복수 거래유형은 Spring 계약과 일치하지 않는다.

### 문제 발견 주체

Issue #94 작성자와 수정자는 본인이다. 최초 현상을 본인이 수동 테스트에서 발견했는지, 팀원이 전달했는지는 기록만으로 확정할 수 없다. `[본인 확인 필요]`

### 원인

keyword 검색이 프론트의 현재 property 배열을 local filter하는 데 머물고 viewport request에는 전달되지 않아 지역·cluster 집계는 keyword를 알 수 없었다. PR 첫 커밋에서 raw keyword·LIKE wildcard 처리 문제가 생겼지만 이는 자동 리뷰와 후속 `6cb0c85`에서 보정됐다. 이후 프론트와 서버가 독립적으로 필터를 확장하면서 월세 범위·복수 거래유형의 새 drift도 생겼다.

### 내가 맡은 역할

| 활동 | 확인된 역할 |
|---|---|
| 초기 설계·구현 | zoom별 controller/service/DAO 계약, 집계 SQL, 프론트 API·렌더링을 PR #54~#67에서 구현 |
| 문제 발견 | Issue #94 작성자는 본인이나 최초 관찰·제보 주체는 확인되지 않음 |
| 원인 분석 | local-only keyword와 viewport request의 계약 단절을 특정. raw keyword·LIKE wildcard는 PR 중간 리뷰에서 추가 발견 |
| 해결책 설계 | 기존 DAO filter builder에 keyword를 추가하고 검색 중 count marker를 사용 |
| 구현 | keyword criteria·public list helper 재사용, 프론트 viewport payload, marker rendering 수정 |
| 테스트 | no-result, literal wildcard, payload/store/marker와 Spring test 실행 기록 |
| 코드 리뷰 | wildcard escape와 trim 등 자동 리뷰 3건을 후속 커밋으로 수정; 사람 리뷰는 확인되지 않음 |
| 프론트·다른 서버 조율 | 당시 backend query와 Vue request/rendering을 직접 함께 수정. 팀원이 최종 필터 UI를 후속 변경 |
| 최종 병합 | PR #95 merge와 두 번째 자동 리뷰의 actionable comment 없음은 확인되나 승인 주체는 주장하지 않음 |

### 검토한 대안

ADR-010에는 zoom 구간별로 광역 region, cluster, property를 나누는 선택이 기록돼 있다. PR #95 기록에서 확인되는 제품 선택은 검색 중 대표 가격 대신 matching count를 표시하는 것이다. 별도 query builder나 specification 패턴을 비교한 기록은 없으며 기존 helper를 확장했다.

### 최종 해결

- 기존 `appendPropertyFilters`의 단일 거래유형, 매물유형, 보증금, 매매가 조건에 keyword를 추가했다.
- region, cluster, viewport property와 public bounds list가 이를 공유한다.
- 사용자 keyword를 trim하고 SQL LIKE wildcard를 escape한다.
- 프론트는 줌에 맞춰 `<=9` 시·도, `10–11` 시·군·구, `12–13` 동, `14–15` cluster, `>=16` property API를 선택한다.

### 검증과 결과

- DAO·service·controller·프론트 테스트와 PR의 리뷰 후속 수정이 확인된다.
- 관련 PR은 병합됐고 현재 코드에도 공통 조건 경로가 남아 있다.
- 정량적인 응답 시간 개선 수치는 없다.
- 광역 `averagePrice`는 활성 매물의 가격 평균이며 실거래가 통계 테이블 평균이 아니다.

### 현재 상태와 한계

keyword와 당시 지원 조건 범위에서는 해결이 유지된다. 하지만 월세 범위, 복수 거래유형, `clusterThreshold`는 현재 UI/API 계약이 어긋난다. 따라서 “모든 필터 정합성 해결”이 아니라 **local-only keyword의 서버 계약 통합과 이후 발생한 drift를 함께 설명하는 핵심 또는 1순위 보조 사례**로 적합하다.

## 5. 나머지 검증 사례 요약

### 5.1 8개 endpoint 대응 오프라인 데이터 파이프라인

- **문제**: 이질적인 거래 응답을 검색 가능한 단일 모델로 만들고, 대용량 seed를 중복 없이 다시 적재할 필요가 있었다.
- **본인 기여**: endpoint 설정, alias 정규화, 20개 공통 필드, 거래 키, manifest와 geocode cache, 네 파생 테이블 upsert를 구현했다.
- **증거**: Issue #7/#32, PR #8/#33과 관련 diff. 커밋된 seed는 8,121건이다.
- **경계**: 8개 endpoint configuration·alias code path와 과거 seed 결과는 확인되지만 raw/seed 호환성이 검증된 source는 네 종류뿐이다. 자동 retry·scheduler·전국 완전 수집은 없다.
- **분류**: Java/Spring 외 데이터·DB 역량을 보이는 **핵심 사례 후보**.

### 5.2 시설 접근성 점수의 배치 사전 계산

- **문제**: 매물 요청마다 모든 시설과 거리를 계산하면 외부 API와 계산 비용이 사용자 요청 경로에 들어간다.
- **본인 기여**: 각 매물의 501m 후보 bounds를 100개 chunk 단위로 merge해 DB 후보를 조회하고, 매물별 bounds 재검사 뒤 Java Haversine 구면 근사로 CCTV·비상벨·보안등 300m, 경찰관서 500m count를 구했다. cap/weight를 적용해 0–100으로 저장했다.
- **증거**: Issue #76 / PR #77, 관련 service·repository·test diff.
- **경계**: 이 값은 시설 접근성 proxy다. 범죄 발생 데이터나 통계적 calibration이 없으며 시설 누락과 실제 0건을 구분하지 못한다. `safety-summary`의 `radius=300/500`은 계산 조건이 아니라 응답에 echo되고, 실제 값은 고정된 300m 세 시설+500m 경찰 혼합식이다.
- **분류**: 안전시설 장애 대응과 결합할 때 강한 **핵심 사례 구성 요소**.

### 5.3 선택 매물 기반 Spring–FastAPI 분석 카드 연동

- **문제**: 인증된 사용자의 선택 매물 문맥을 AI가 사용하려면 Spring DB API, 내부 계약, FastAPI worker, 프론트 카드가 이어져야 했다.
- **본인 기여**: Spring chat 경계, 내부 API key, 가격·안전 API, 선택 매물 ID 전달, FastAPI tool 호출과 초기 카드 normalizer/rendering을 구현했다.
- **증거**: Issue #36/#38/#40/#45/#47/#49와 PR #37/#39/#41/#46/#48/#50.
- **경계**: 최종 챗봇 UI·세션 UX는 팀원 후속 기여다. 현재 `workersCalled` 등 응답 메타데이터가 Spring에서 유실되고, timeout budget도 역전돼 있다.
- **분류**: 서비스 간 계약과 협업을 보여주는 **핵심 사례 후보**.

### 5.4 모노레포 분리 배포

- **문제**: Spring과 FastAPI를 각각 독립 Cloud Run 서비스로 패키징·배포해야 했다.
- **본인 기여**: 서비스별 Dockerfile, GitHub Actions, 내부 URL·secret 연결과 배포 수정 diff가 확인된다.
- **증거**: Spring 배포 16회, FastAPI 배포 9회 성공 이력.
- **경계**: workflow가 테스트를 gate하지 않고 Spring image는 `-DskipTests`로 package한다. 성공 이력은 기능 smoke test가 아니다.
- **분류**: **보조 사례**.

### 5.5 최초 공개 매물 API와 계층 경계

- **문제**: 프론트가 DB에 직접 접근하지 않고 Spring의 공개 read API를 통해 검증된 조건으로 매물 정보를 조회해야 했다. 현재 `GET /api/v1/properties/**`는 `permitAll`이므로 JWT 필수 API로 설명하지 않는다.
- **본인 기여**: controller는 검증·위임, service는 비즈니스 로직, repository는 DB 접근으로 분리된 초기 Spring API의 상당 부분을 구현했다.
- **증거**: 초기 backend 관련 커밋·PR과 현재 layer 구조.
- **경계**: 프로젝트 전체 인증·도메인 모델은 팀 결과이며, 본인 단독 설계 범위를 더 세밀하게 말하려면 초기 회의 기록이 필요하다.
- **분류**: **보조 사례**.

## 6. 전체 사례 점수

각 항목은 5점 만점이다. 점수는 기술 규모가 아니라 Java/Spring 포트폴리오에서 증거를 가지고 설명할 수 있는 정도를 평가한다.

| 사례 | Java/Spring 직무 관련성 | 기술적 깊이 | 문제 구체성 | 원인 분석 | 개인 경계 | 증거 | 결과 명확성 | 면접 확장성 | 차별성 | 과장 없이 설명 | 합계 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 지도 조건 정합성 | 5 | 4 | 5 | 5 | 5 | 5 | 4 | 5 | 4 | 5 | **47** |
| Spring–FastAPI 선택 매물 연동 | 5 | 5 | 5 | 4 | 5 | 5 | 3 | 5 | 4 | 4 | **45** |
| 안전시설 API 장애·부분 실패 | 5 | 4 | 5 | 3 | 5 | 5 | 3 | 5 | 4 | 5 | **44** |
| 법률 RAG stub·fallback | 3 | 5 | 5 | 4 | 5 | 5 | 4 | 5 | 5 | 3 | **44** |
| 8 endpoint 데이터 파이프라인 | 3 | 5 | 5 | 4 | 5 | 4 | 3 | 5 | 5 | 4 | **43** |
| 시설 접근성 사전 계산 | 5 | 4 | 4 | 4 | 5 | 5 | 3 | 5 | 4 | 4 | **43** |
| 최초 공개 매물 API·계층 경계 | 5 | 3 | 4 | 4 | 5 | 5 | 4 | 4 | 3 | 5 | **42** |
| 모노레포 분리 배포 | 3 | 4 | 4 | 4 | 5 | 5 | 4 | 4 | 4 | 3 | **40** |

### 항목별 점수 근거

- **지도 조건 정합성 — 47점**: 직무 관련성 5(Spring/JDBC 핵심 경로), 난이도 4(줌별 집계와 keyword 조건), 문제 구체성 5(local 목록·viewport 마커 불일치), 원인 5(keyword가 frontend local state에만 머문 경계), 개인 경계 5(초기 구현·Issue·수정 diff 소유), 증거 5(PR #54~#67/#95·review 후속), 결과 4(keyword·지원 조건 일치, 정량 성능 없음), 면접 확장성 5(SQL·API·FE 계약), 차별성 4(지도 집계라는 구체 맥락), 과장 억제 5(기존 filter helper와 현재 drift까지 구분 가능).
- **Spring–FastAPI 선택 매물 연동 — 45점**: 직무 관련성 5(Spring 공개·내부 API 경계), 난이도 5(Java/Python/Frontend와 오류 계약), 문제 구체성 5(stub·선택 ID·카드 연결), 원인 4(분산 DTO는 명확하나 실제 운영 실패 로그 부족), 개인 경계 5(PR #37~#50 diff), 증거 5(양 서버·프론트 코드와 test), 결과 3(live smoke와 현재 완전성 미확인), 면접 확장성 5(보안·timeout·contract), 차별성 4(AI도 backend 계약으로 설명), 과장 억제 4(최종 UI·metadata drift를 반드시 병기해야 함).
- **안전시설 API 장애·부분 실패 — 44점**: 직무 관련성 5(Spring external client·batch), 난이도 4(JSON/XML·인증·좌표), 문제 구체성 5(403·401·key error), 원인 3(encoding 위험은 보이지만 제공자 단일 원인·사후 성공 미확인), 개인 경계 5(Issue와 핵심 diff 소유), 증거 5(PR #69~#93·fixture/test), 결과 3(code hardening은 확인되나 live row 없음), 면접 확장성 5(실패 격리·관측성), 차별성 4(좌표와 부분 실패 결합), 과장 억제 5(“운영 해결” 대신 변경 범위로 말할 수 있음).
- **법률 RAG stub·fallback — 44점**: 직무 관련성 3(Python 비중이 높음), 난이도 5(ingestion·embedding·vector·fallback), 문제 구체성 5(stub과 직접 DB 오류), 원인 4(단계적 구현·환경 경계는 명확하나 실제 차단 맥락 일부 자기보고), 개인 경계 5(PR #17~#35 핵심 diff), 증거 5(schema·tests·PR), 결과 4(실제 code path는 있으나 운영 dataset 없음), 면접 확장성 5(RAG·failure semantics), 차별성 5(검색과 운영 경계를 함께 설명), 과장 억제 3(품질·환각·최신 법령을 쉽게 과장할 수 있음).
- **8 endpoint 데이터 파이프라인 — 43점**: 직무 관련성 3(Python offline 도구, DB 설계는 관련), 난이도 5(config·alias·파생·upsert), 문제 구체성 5(대용량 seed·중복·수동 적재), 원인 4(bootstrap 한계와 key 필요성), 개인 경계 5(두 PR 핵심 diff 소유), 증거 4(4 source artifact와 제한 실행은 있으나 나머지 fixture/current 전용 test 없음), 결과 3(8 endpoint 전체 호환·운영 DB 미확인), 면접 확장성 5(model·transaction·retry), 차별성 5(실제 공공데이터 변이), 과장 억제 4(endpoint 설정과 검증 source를 나누면 설명 가능).
- **시설 접근성 사전 계산 — 43점**: 직무 관련성 5(Spring service·JDBC·batch), 난이도 4(bbox+구면 거리·upsert), 문제 구체성 4(request-time 비용은 구조적으로 명확하나 실측 없음), 원인 4(반복 거리 계산), 개인 경계 5(PR #77 diff), 증거 5(service·DAO·test·ADR), 결과 3(latency 수치·scheduler run 없음), 면접 확장성 5(PostGIS·batch·locking), 차별성 4(공간 계산), 과장 억제 4(시설 proxy 한계를 계속 밝혀야 함).
- **최초 공개 매물 API·계층 경계 — 42점**: 직무 관련성 5(Spring REST 기본기), 난이도 3(전형적 controller/service/DAO), 문제 구체성 4(DB seed를 지도 가치로 연결), 원인 4(직접 DB 접근을 막는 계층 경계), 개인 경계 5(초기 API/FE diff), 증거 5(MockMvc·HTTP·PR), 결과 4(현재 path 유지, 운영 traffic 없음), 면접 확장성 4(validation·CORS·공개 read 정책), 차별성 3(일반적인 CRUD 성격), 과장 억제 5(코드 범위가 선명함).
- **모노레포 분리 배포 — 40점**: 직무 관련성 3(backend 지원 역량), 난이도 4(두 runtime·subtree sync), 문제 구체성 4(GitHub 개발과 GitLab 제출·독립 배포), 원인 4(repository·artifact 경계), 개인 경계 5(workflow diff 소유), 증거 5(Actions run·commit), 결과 4(성공 run 존재), 면접 확장성 4(image·secret·WIF), 차별성 4(SSAFY 제출 sync), 과장 억제 3(test gate·smoke 부재를 숨기기 쉬움).

### 점수 근거 요약

- **지도**는 local-only keyword가 viewport와 어긋난 현상, Java/JDBC·Vue 수정까지 추적 가능하다. 다만 기존 가격·유형 filter builder까지 PR #95에서 새로 만든 것은 아니며 정량 성능 결과가 없다.
- **서비스 간 연동**은 계약·보안·오류 전파·UI 소비까지 확장성이 높다. 현재 계약 drift 때문에 결과 점수를 낮췄다.
- **안전시설**은 Spring batch와 외부 API 방어 설계가 강하다. 운영 성공 증거와 단일 원인 규명이 부족하다.
- **법률 RAG**는 기술 깊이가 높지만 Java/Spring 직접성과 운영 데이터 증거가 약하다.
- **데이터 파이프라인**은 모델링과 중복 방지 설명이 강하지만 Python 오프라인 도구이며 8 endpoint 전체 raw 호환·실행 증거가 없다.
- **시설 점수**는 계산 경로가 명확하지만 도메인 유효성 검증이 없다.
- **초기 API**는 기본기가 분명한 대신 다른 지원자와의 차별성이 낮다.
- **배포**는 실제 실행 이력이 있으나 테스트 gate와 배포 후 검증이 부족하다.

## 7. 최종 활용 분류

| 분류 | 사례 |
|---|---|
| 핵심 사례 | 데이터 파이프라인, Spring–FastAPI 선택 매물 연동, 안전시설 수집·시설 접근성 사전 계산 |
| 1순위 대체 사례 | 지도 줌 조회·검색 조건 정합성 |
| 보조 사례 | 법률 RAG, 최초 공개 매물 API, 모노레포 분리 배포 |
| 기술 설명에만 사용 | 구체 운영 증거가 없는 scheduler·fallback 범위 설명 |
| 제외 | `workersCalled`를 이미 해결한 성과로 제시, 범죄 안전도·전국 8종 운영 수집·환각 방지 보장 |

점수만 따르면 지도가 가장 높지만, 최종 세 사례는 데이터 모델링, 서비스 간 계약, Spring 외부 API·배치라는 서로 다른 역량을 보여주도록 구성했다. Java/Spring 지원처에서 세 사례 모두를 짧게 말해야 한다면 데이터 파이프라인 대신 지도를 선택해도 된다.
