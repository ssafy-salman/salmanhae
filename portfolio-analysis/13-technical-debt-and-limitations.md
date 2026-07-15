# 기술 부채와 한계

## 우선순위 기준

- **P0**: 현재 서비스 경계에서 조용한 데이터 유실, 광범위한 실패, 보안 사고로 이어질 수 있어 다음 기능 개발 전에 다뤄야 한다.
- **P1**: 기능은 동작할 수 있지만 운영 신뢰성·데이터 정확성·회귀 방지에 직접 영향을 준다.
- **P2**: MVP에서는 수용 가능하나 규모 확대나 장기 운영 전에 개선해야 한다.

## 1. P0 — `workersCalled` 응답 계약의 조용한 유실

### 현재 상태

FastAPI `AgentChatResponse`는 `workersCalled`, `toolResults`, `nextActions`를 반환한다. Spring `AiAgentClient.AgentChatResponse`는 이 필드를 정의하지 않고 FastAPI 응답에 없는 `intent`를 기대한다. Jackson은 알 수 없는 필드를 무시하므로 공통 필드인 메시지와 카드는 역직렬화될 수 있지만 worker metadata와 도구 결과·후속 행동은 Spring 경계에서 사라진다. `intent`는 공개 Spring 응답에서 `null`, 프론트 normalizer에서 빈 문자열이 된다.

PR #63은 FastAPI 계약만 변경했고 본문에도 Spring·Frontend parsing 확인이 후속 작업으로 남았다. 이후 Spring/Frontend에서 `workersCalled`를 추가한 커밋은 없다. FastAPI producer test, Spring controller mock test, 프론트 자체 fixture는 있지만 실제 HTTP consumer contract test는 없다.

| 필드 | FastAPI 내부 응답 | Spring 내부 consumer | Spring 공개 응답 | Frontend normalizer | 현재 결과 |
|---|---|---|---|---|---|
| `workersCalled` | `list[str]`, 기본 `[]` | 정의 없음 | 정의 없음 | 정의 없음 | non-empty여도 Spring에서 유실 |
| `toolResults` | `dict[str, Any]`, 기본 `{}` | 정의 없음 | 정의 없음 | 정의 없음 | Spring에서 유실 |
| `nextActions` | `list[dict]`, 기본 `[]` | 정의 없음 | 정의 없음 | 정의 없음 | Spring에서 유실 |
| `intent` | 정의 없음 | nullable `String`으로 기대 | nullable `String` | `data.intent || ''` | `null`을 거쳐 빈 문자열 |
| `answer`/`message` | 필수 `answer: str` | `String answer` | `message`로 변환 | `data.message || ''` | 공통 경로는 유지 가능 |
| cards | list, 기본 `[]` | list | list | 배열 normalize | 공통 card는 유지 가능 |

불일치는 `workersCalled`가 비어 있지 않을 때도 역직렬화 자체를 실패시키지 않고 metadata만 잃는 조건에서 가장 분명하다. 현재 UI가 이 metadata를 표시하지 않으므로 일반 흐름에서 즉시 눈에 띄지 않을 수 있다. demo 영향은 별도 확인이 필요하다.

`workersCalled`는 공개 API 문서에도 명시돼 있어 확인된 public contract drift다. 반면 `toolResults`와 `nextActions`는 FastAPI schema에는 있지만 Spring 공개 API spec에는 원래 없으므로 “공개 필수 필드의 회귀”로 단정하지 않는다. `toolResults`는 실제 값이 생길 수 있어 service boundary에서 미전달되고, `nextActions`는 현재 node가 채우지 않아 기본 빈 배열인 미래 확장 gap이다.

### 발생 가능한 영향

- worker 실행 이력, tool result, next action 기반 UI·analytics가 조용히 잘못될 수 있다.
- 필드가 “없는 것”과 역직렬화 중 “유실된 것”을 관측할 수 없다.
- 현재 메시지와 카드가 표시된다는 이유로 계약 회귀가 배포 뒤에도 발견되지 않을 수 있다.
- 실제 demo·사용자 영향은 저장소만으로 확인되지 않으며 전체 채팅 장애라고 단정할 수 없다.

### 당시·현재 우선순위 판단

PR #63 본문은 Spring·Frontend parsing 확인을 후속으로 남겼지만 왜 병합 전에 처리하지 않았는지는 기록하지 않는다. 현재는 서비스 간 계약이 컴파일 경계를 넘어 조용히 깨지고 같은 유형이 다른 필드에도 반복될 수 있어 P0다. 가장 중요한 기술 부채로 선정한다.

### 개선 방법

1. 공개 Spring DTO의 기준을 결정한다. metadata를 공개할 필요가 있다면 `workersCalled`, `toolResults`, `nextActions`를 명시하고 `intent`는 제거하거나 FastAPI가 제공하게 한다.
2. FastAPI OpenAPI schema 또는 versioned JSON fixture를 단일 계약 원천으로 둔다.
3. 실제 `AiAgentClient`가 producer fixture를 역직렬화하고 공개 `ChatResponse`로 변환하는 consumer contract test를 추가한다.
4. 프론트 normalizer도 같은 fixture를 소비하게 한다.
5. 예상하지 못한 필드와 필수 필드 누락을 배포 전 감지하도록 contract check를 CI gate에 넣는다.
6. 계약 version과 correlation ID를 로그에 남긴다.

### 포트폴리오·면접에서 설명하는 방법

“현재 코드를 producer와 consumer 관점에서 다시 대조하면서, FastAPI가 추가한 worker metadata가 Spring DTO에서 조용히 유실되는 문제를 발견했습니다. 메시지와 카드는 남아 전체 장애는 아니지만 consumer contract test 부재를 보여주는 사례입니다. 해결한다면 공유 schema·versioned fixture·실제 HTTP 역직렬화 테스트를 CI gate로 묶겠습니다.”라고 설명한다. 이미 해결했다고 말하지 않는다.

## 2. P0 — 바깥 timeout이 안쪽 최악 처리시간보다 짧은 budget 역전

### 현재 상태

코드 기본값에서 Spring→FastAPI는 connect 2초, read 10초다. FastAPI의 Spring API 호출 기본 timeout은 각 5초이고 가격 worker는 매물 상세·거래·가격 분석을 순차 호출한다. LLM client 기본 timeout은 20초다. 배포 환경변수는 확인되지 않았지만 기본값 기준 내부 합산 최악 시간이 외부 10초를 넘을 수 있다. retry, circuit breaker, deadline propagation은 없다.

### 발생 가능한 영향

- FastAPI가 정상 처리 중이어도 Spring이 먼저 502를 반환할 수 있다.
- 바깥 요청이 끊긴 뒤 내부 DB·LLM 작업이 계속돼 자원을 낭비할 수 있다.
- 부하가 높을 때 tail latency와 중복 요청이 악화될 수 있다.

### 당시·현재 우선순위 판단

각 timeout 값을 정한 당시의 latency budget이나 이 위험을 미룬 판단은 기록에 없다. 현재는 핵심 채팅 경로의 구조적 실패 조건이며 외부 서비스 지연 하나가 전체 요청을 끊을 수 있어 P0다.

### 개선 방법

- 전체 SLO와 latency budget을 먼저 정하고 각 내부 호출에 하위 deadline을 배분한다.
- 독립적인 Spring API는 병렬 호출하거나 선택 매물 분석용 aggregation endpoint로 합친다.
- LLM이 필요한 경로와 deterministic card 경로를 분리하고 취소 신호를 전파한다.
- idempotent하고 일시적인 오류에만 제한적 retry+jitter를 적용한다.
- correlation ID와 단계별 latency metric을 추가한다.

### 포트폴리오·면접에서 설명하는 방법

초기 연동 성과와 함께 “현재 감사에서 외부 10초보다 내부 합산 budget이 긴 위험을 찾았고, 다음 개선은 병렬화·deadline propagation·구간별 metric”이라고 말한다. 응답 시간이 실제로 10초를 넘었다는 관측 수치를 만들지 않는다.

## 3. P1 — 테스트가 배포를 막지 않는 CI/CD

### 현재 상태

Spring과 FastAPI에는 테스트가 있고 Actions 배포 성공 이력도 있다. 그러나 배포 workflow에서 테스트 job이 필수 gate가 아니며 Spring Docker package는 `-DskipTests`를 사용한다. Vercel check는 프론트 배포 상태이지 backend E2E 검증이 아니다.

### 발생 가능한 영향

- 단위 테스트가 깨진 commit도 image build와 배포까지 진행될 수 있다.
- 계약 drift나 migration 오류가 배포 뒤에 발견될 수 있다.
- “테스트가 있다”와 “검증된 artifact를 배포한다” 사이가 끊긴다.

### 당시·현재 우선순위 판단

당시 workflow는 빠른 서비스별 배포를 먼저 완성했지만 test gate를 제외한 이유를 명시한 기록은 없다. 현재 기능 수와 서비스 수를 고려하면 회귀 방지의 기반이므로 P1이다. 계약 P0 수정과 함께 gate를 만들 필요가 있다.

### 개선 방법

- Spring `mvn test`, FastAPI `pytest`, Frontend test/build를 별도 job으로 실행하고 deploy가 모두를 `needs`로 의존하게 한다.
- migration dry-run 또는 ephemeral PostgreSQL integration test를 추가한다.
- 동일 commit SHA로 검증한 image digest만 배포한다.
- 배포 후 인증된 smoke test와 rollback 조건을 둔다.

### 포트폴리오·면접에서 설명하는 방법

“테스트 코드와 배포 자동화는 구현했지만 둘이 gate로 연결되지 않은 것이 한계”라고 구분한다. Actions 성공 횟수를 품질 수치로 사용하지 않는다.

## 4. P1 — 데이터 파이프라인의 source 완전성·재시도·실행 증거 부족

### 현재 상태

`pipeline.py`는 8개 endpoint를 설정하지만 저장소 raw/seed 호환성은 네 source만 확인된다. 새 fetch 분기의 예외는 error를 기록하고 다음 request tuple로 넘어갈 수 있으나 cached XML·normalize parse 예외는 상위로 전파되고 자동 retry/backoff가 없다. manifest는 기록된 비어 있지 않은 raw 파일 존재를 기준으로 건너뛰며 API `resultCode`를 검사하지 않는다. `FAILED` geocode cache도 다음 실행에서 자동 재시도하지 않는다. run ID, stage status, reject ledger, source별 watermark와 current pipeline 전용 contract test도 없다.

### 발생 가능한 영향

- 일시적 네트워크 오류가 특정 지역·월의 영구 누락으로 남을 수 있다.
- “0건 정상”과 parse 실패·source 미실행을 구분하기 어렵다.
- schema drift가 8개 중 fixture가 없는 source에서 늦게 발견될 수 있다.
- stale output과 이번 run output이 섞여도 실행 단위로 추적하기 어렵다.

### 당시·현재 우선순위 판단

초기에는 backend/frontend를 unblock하는 bootstrap과 수동 재실행 경로를 우선한 기록이 있다. 운영 수준의 retry·완전성 검증을 뒤로 미룬 구체 판단은 없다. 현재는 지도·가격 분석의 기반 데이터 품질에 직접 영향을 주므로 P1이다.

### 개선 방법

- 8개 endpoint configuration(`source_api`) 각각의 최소 raw fixture와 schema contract test를 만든다.
- request tuple별 status, attempt, row count, checksum, error를 run table/manifest에 기록한다.
- exponential backoff와 최대 시도, 실패 quarantine, 재처리 명령을 분리한다.
- staging table에 적재한 뒤 completeness 검증 후 publish한다.
- source별 expected/received count와 freshness를 metric으로 노출한다.

### 포트폴리오·면접에서 설명하는 방법

“결정적 key의 중복 방지 upsert와 manifest raw-page 재사용은 구현했지만 성공 checkpoint·운영 retry·완전성 증명은 없다”고 말한다. ‘멱등성’은 DB conflict upsert의 범위로 한정한다.

## 5. P1 — 안전시설 실패를 0건으로 오인할 수 있는 관측성 문제

### 현재 상태

상위 ingestion service는 source client가 던진 `RuntimeException`을 잡아 다음 source를 진행한다. 그러나 concrete client의 HTTP/parse 경로는 오류를 빈 목록 또는 부분 목록으로 바꿀 수 있다. 이 경우 `failedSourceCount`가 0인데 실제로는 source가 실패했을 수 있다. source 단위 transaction과 stale row 정리도 없다.

### 발생 가능한 영향

- 데이터 미수집을 실제 주변 시설 0건으로 해석해 점수가 낮아질 수 있다.
- 운영자는 성공 로그만 보고 외부 계약 파손을 놓칠 수 있다.
- 부분 페이지 적재 뒤에도 최신 데이터처럼 제공될 수 있다.

### 당시·현재 우선순위 판단

당시에는 한 source 예외가 전체 batch를 중단하지 않는 계속 진행 구조를 먼저 구현했다. concrete client가 오류를 빈 값으로 바꾸는 관측성 trade-off를 의도적으로 수용했다는 기록은 없다. 현재는 사용자에게 제공되는 점수의 입력 신뢰성을 해치므로 P1이다.

### 개선 방법

- client 반환을 `Success(rows, pageStats)` / `Failure(source, status, cause)` 같은 typed result로 바꾼다.
- source·page별 요청/성공/parse/drop row와 freshness를 저장한다.
- staging+source transaction으로 완전한 run만 current snapshot으로 승격한다.
- safety summary에 `calculatedAt`, source freshness, completeness를 포함한다.
- alert는 HTTP status와 연속 실패 횟수를 기준으로 둔다.

### 포트폴리오·면접에서 설명하는 방법

부분 실패 격리의 장점과 “예외를 너무 일찍 빈 값으로 바꾸면 관측성을 잃는다”는 한계를 함께 설명한다. 네 source 운영 성공을 주장하지 않는다.

## 6. P1 — 시설 접근성 proxy를 범죄 안전도로 오해할 위험

### 현재 상태

점수는 CCTV·비상벨·보안등 300m, 경찰관서 500m count를 cap/weight로 합산한다. 범죄 발생, 시간대, 시설 가동 상태, CCTV camera 수, 인구 노출을 사용하지 않는다. 가중치와 반경의 통계적 calibration도 없다. AI prompt 일부에는 “범죄율”을 연상시키는 문구가 있어 실제 metric과 의미가 어긋날 수 있다.

### 발생 가능한 영향

- 사용자가 점수를 실제 범죄 가능성 또는 보증된 안전으로 오해할 수 있다.
- source 누락과 지역별 시설 정책 차이가 점수 편향으로 이어질 수 있다.
- 중요한 주거 결정을 단일 미검증 지표에 의존하게 할 수 있다.

### 당시·현재 우선순위 판단

당시에는 MVP 규칙 기반 점수를 구현했지만 가중치의 도메인 검증을 미룬 근거와 승인자는 기록돼 있지 않다. 현재는 도메인 오해와 사용자 의사결정 위험이 커 P1이다.

### 개선 방법

- 명칭을 “안전시설 접근성”으로 바꾸고 계산 근거·갱신 시각·source 완전성을 함께 표시한다.
- 가중치와 반경을 정책 설정으로 분리하고 근거 문서를 남긴다.
- 사용자 연구 또는 공개 데이터로 sensitivity·calibration을 수행한다.
- AI prompt에서 범죄율·치안 보장 표현을 제거하고 proxy 한계를 강제한다.

### 포트폴리오·면접에서 설명하는 방법

계산 최적화 사례로 사용하되 “시설 접근성 proxy이며 치안을 예측하지 않는다”고 먼저 말한다. 수치가 0–100이라는 이유로 정확한 확률처럼 설명하지 않는다.

## 7. P1 — 법률 RAG의 운영 데이터·검색 품질·fallback 범위

### 현재 상태

법률 ingestion과 pgvector 검색 코드는 있으나 실제 원문 파일, 현재 row 수, embedding model 값, 품질 test set이 없다. 검색은 top-k 1–5와 cosine 유사도를 사용하지만 threshold·법령/시행일 filter·reranker가 없다. 비운영 fallback은 `psycopg.OperationalError`에서 project ref를 추출하고 service-role key가 있을 때 REST를 1,000행씩 읽어 로컬 cosine을 계산하며, 운영에서는 오류를 다시 던진다. fallback을 사용해도 tool source metadata는 `supabase-pgvector`로 남는다.

### 발생 가능한 영향

- 관련성이 낮은 chunk도 top-k에 포함될 수 있다.
- 구법·현행법과 source freshness를 답변에서 구분하지 못할 수 있다.
- 데이터가 늘면 REST fallback의 메모리·latency가 급증한다.
- embedding/DB/REST의 다른 오류는 node 바깥으로 전파돼 500이 될 수 있다.

### 당시·현재 우선순위 판단

당시 phase는 stub 제거, 실제 retrieval, 개발 fallback 순으로 코드 경로를 우선했다. 운영 dataset과 품질 평가를 뒤로 미룬 구체 결정은 기록에 없다. 현재는 법률 답변의 신뢰성과 실패 범위에 직접 영향을 주므로 운영 기능으로 사용할 경우 P1이다. demo용 비운영 경로라면 범위를 명시하고 후순위로 둘 수 있다.

### 개선 방법

- 법령명·조문·시행일·source URL을 versioned dataset으로 관리한다.
- 기대 조문이 있는 질문 set으로 top-k recall과 답변 citation 일치율을 평가한다.
- threshold와 metadata filter를 도입하고 zero-result 처리 기준을 측정한다.
- fallback은 서버 측 vector RPC 또는 제한된 후보 query로 바꾸고 circuit·timeout을 명시한다.
- 답변 생성 뒤 인용된 근거가 실제 card에 있는지 post-validation한다.

### 포트폴리오·면접에서 설명하는 방법

“근거를 prompt와 카드에 제한하는 grounding 장치”로 설명한다. 환각·법률 정확성을 보장했다고 말하지 않고 fallback은 개발 환경 편의 장치라고 밝힌다.

## 8. P1 — 지도 필터의 Frontend–Spring 계약 drift

### 현재 상태

Spring의 공통 JDBC filter는 단일 거래유형, 매물유형, 보증금, 매매가, keyword를 지원한다. 최종 프론트는 월세 최소·최대와 복수 거래유형 상태를 갖지만 Spring controller/criteria는 이를 받지 않는다. 복수 거래유형은 한 개일 때만 `transactionType`을 보내고 둘 이상이면 비워 unfiltered가 된다. `clusterThreshold`는 API에 있으나 query에 쓰이지 않는다.

### 발생 가능한 영향

- 화면에는 활성 필터가 보이지만 지도 count와 상세 결과가 사용자가 기대한 조건을 따르지 않을 수 있다.
- 과거 PR #95에서 해결한 정합성 문제가 새로운 필드에서 재발한다.
- backend가 무시한 입력을 사용자에게 알리지 않아 디버깅이 어렵다.

### 당시·현재 우선순위 판단

PR #95 당시 지원 조건은 공통화됐고, 현재 drift는 후속 UI 확장 뒤 생겼으므로 당시에 의도적으로 미룬 문제로 볼 수 없다. 현재 검색 신뢰성과 핵심 UI에 직접 영향을 주므로 P1이다.

### 개선 방법

- filter schema를 한 곳에서 versioning하고 OpenAPI 기반 client를 생성한다.
- 복수 거래유형과 월세 범위를 지원하거나 UI에서 제거·비활성화한다.
- region/cluster/property/list에 동일 fixture를 적용하는 parameterized contract test를 만든다.
- 사용하지 않는 `clusterThreshold`는 구현하거나 계약에서 제거한다.

### 포트폴리오·면접에서 설명하는 방법

PR #95에서 “당시 지원 조건을 공통화했다”고 한정하고, 후속 UI 확장으로 새 drift가 생긴 사실을 함께 말한다. “모든 필터를 해결했다”고 하지 않는다.

## 9. P1 — 안전 요약 `radius`가 계산에는 쓰이지 않고 표시값으로만 echo

### 현재 상태

`GET /api/v1/properties/{id}/safety-summary`는 `radius=300` 또는 `500`을 검증한다. 그러나 `JdbcPropertyDao.findSafetySummary`의 SQL은 radius를 조건으로 사용하지 않고 `property_score_stat`의 고정 `cctv_count_300m`, `bell_count_300m`, `light_count_300m`, `police_count_500m`, `safety_score`를 읽은 뒤 요청 radius를 응답에 그대로 넣는다. FastAPI는 항상 `radius=500`을 보내고 이 혼합 반경 점수를 “반경 500m 기준 안전 점수”라고 요약한다.

### 발생 가능한 영향

- `radius=300`과 `500`의 응답 값이 같으면서 표시 radius만 달라질 수 있다.
- 사용자는 모든 시설과 점수가 선택한 단일 반경으로 다시 계산됐다고 오해할 수 있다.
- API 문서·FastAPI 요약·실제 고정 계산식이 서로 다른 의미를 전달한다.

### 당시·현재 우선순위 판단

사전 계산된 고정 metric을 재사용하면서 radius parameter를 유지한 이유나 동적 반경을 미룬 판단은 기록에 없다. 현재 사용자에게 계산 의미를 잘못 전달할 수 있어 P1이다.

### 개선 방법

- 고정 반경 제품이라면 `radius` parameter를 제거하고 각 metric 이름의 300m/500m를 그대로 노출하며 “혼합 시설 접근성 점수”로 설명한다.
- 동적 반경이 요구사항이면 반경별 통계를 별도 저장하거나 시설 table에서 bounds+거리 query로 계산하고 score formula도 반경별로 정의한다.
- `radius=300`과 `500` fixture가 기대대로 다른 결과를 내는 contract test를 Spring–FastAPI 사이에 추가한다.
- FastAPI의 “반경 500m 기준 안전 점수” 문구를 실제 고정식에 맞춘다.

### 포트폴리오·면접에서 설명하는 방법

점수 계산 자체는 고정 300m/500m 시설 접근성 사전 계산으로 설명한다. 현재 API의 `radius`는 계산 parameter가 아니며 이를 동적 반경 기능처럼 말하지 않는다.

## 10. P2 — scheduler와 Cloud Run 실행 모델 불일치

### 현재 상태

Spring `@Scheduled` 수집·점수 job은 기본 비활성이고 cron만 정의한다. Cloud Run은 scale-to-zero와 복수 instance가 가능하며 실행 보장·leader election·distributed lock이 코드에 없다.

### 발생 가능한 영향

- instance가 없으면 정시에 실행되지 않거나 여러 instance가 동시에 실행할 수 있다.
- 외부 API quota 중복 소비, row 경합, 부분 데이터가 발생할 수 있다.

### 당시·현재 우선순위 판단

scheduler를 기본 비활성으로 둔 이유와 실제 운영 trigger 선택은 기록에 없다. 현재 실제 활성화 여부가 확인되지 않아 P2로 둔다. 운영 정기 갱신을 켠다면 즉시 P1로 올려야 한다.

### 개선 방법

Cloud Scheduler→인증된 Cloud Run Job 또는 batch endpoint로 실행 주체를 외부화하고, DB advisory lock/job lease로 단일 실행을 보장한다. run status와 재처리 명령도 함께 둔다.

### 포트폴리오·면접에서 설명하는 방법

“조건부 scheduler를 구현했다”까지만 말하고 운영 주기 실행을 주장하지 않는다. Cloud 환경에선 application scheduler보다 외부 scheduler+job lock이 적합하다는 개선 판단을 덧붙인다.

## 11. P2 — 데이터 freshness·provenance의 사용자 노출 부족

### 현재 상태

거래, 안전시설, 법률 chunk에는 source 정보가 일부 있지만 사용자가 보는 카드·지도에서 수집 시각, 기준 월, source 완전성, 법령 시행일을 일관되게 노출하지 않는다. 안전 카드의 metric 구성도 API 문서와 일부 어긋나며 최대 네 metric만 보이는 UI에서는 경찰관서 값이 가려질 수 있다.

### 발생 가능한 영향

- 사용자가 오래되거나 부분적인 데이터를 최신·완전한 정보로 오해할 수 있다.
- 같은 숫자가 왜 바뀌었는지 운영자가 추적하기 어렵다.

### 당시·현재 우선순위 판단

기능 카드와 지도 연결을 먼저 구현했고 provenance 노출을 후순위로 정했다는 명시적 기록은 없다. 현재 MVP 핵심 동작을 막지는 않지만 부동산·안전·법률이라는 고위험 정보의 신뢰성에 중요해 P2다.

### 개선 방법

공통 provenance DTO에 `source`, `observedAt`, `calculatedAt`, `coverage`, `version`을 두고 카드·지도에 기준 시점을 표시한다. API 문서와 UI metric 제한도 함께 정렬한다.

### 포트폴리오·면접에서 설명하는 방법

단순 기능 수보다 “데이터의 출처와 신선도를 제품 계약으로 포함해야 한다”는 학습으로 설명한다.

## 12. 우선 개선 순서

1. FastAPI–Spring–Frontend chat schema를 정렬하고 consumer contract test를 CI gate에 추가한다.
2. 전체 chat latency budget을 재설계하고 단계별 metric을 넣는다.
3. 테스트를 배포 선행 조건으로 묶는다.
4. 안전시설과 거래 pipeline에 source별 run status·freshness·typed failure를 추가한다.
5. 안전 요약의 고정 반경 의미와 `radius` 계약을 정렬한다.
6. 지도 filter schema를 정렬한다.
7. 법률 retrieval 품질 set과 데이터 provenance를 만든다.
8. 운영 정기 갱신이 필요할 때 Cloud Scheduler/Job과 분산 lock으로 전환한다.

가장 중요한 한 가지는 **`workersCalled`로 드러난 서비스 간 consumer contract 부재**다. 특정 필드 하나를 추가하는 수정으로 끝내기보다, 같은 종류의 조용한 유실을 배포 전에 막는 schema와 테스트 체계로 해결해야 한다.
