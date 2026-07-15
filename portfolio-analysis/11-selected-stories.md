# 포트폴리오 핵심 사례 선정

## 선정 결과

최종 핵심 사례는 다음 세 가지다.

1. **8개 공공 API endpoint 확장 경로와 4-source 검증을 갖춘 오프라인 거래 파이프라인**
2. **선택 매물 문맥을 Spring–FastAPI–Frontend로 연결한 서비스 간 계약**
3. **이질적인 네 안전시설 API를 격리하고 시설 접근성 점수를 사전 계산한 Spring 배치**

세 사례는 각각 데이터 모델링·적재, 인증 경계와 서비스 간 통합, 외부 API·좌표·배치 계산 역량을 보여준다. Java/Spring 직무 관련성을 가장 우선하는 지원처에서는 첫 사례를 “지도 줌 조회와 JDBC 필터 정합성”으로 교체할 수 있다.

---

## 핵심 사례 1 — 8개 endpoint 확장 경로와 4-source 검증을 갖춘 오프라인 거래 파이프라인

### 한 줄 요약

국토교통부 8개 endpoint configuration과 공통 alias normalizer를 만들고, 거래 식별 키·manifest raw-page 재사용·conflict upsert를 가진 오프라인 적재 흐름을 구현했다. raw 호환성은 네 source에서 확인했다.

### 배경

살만해는 외부 공공 API를 사용자 요청 때 직접 호출하지 않고, 거래 데이터를 미리 DB에 저장한 뒤 지도·검색·가격 분석에서 재사용해야 했다. 전월세와 매매, 아파트·오피스텔·연립다세대·단독다가구 조합별 8개 endpoint를 설정했고, code는 서로 다른 원시 필드 alias를 예상한다. 실제 raw 호환성은 네 source에서만 확인했다.

| source code | 국토부 service | 거래·주택 유형 | 현재 검증 범위 |
|---|---|---|---|
| `MOLIT_APT_RENT` | `RTMSDataSvcAptRent` | 아파트 전월세 | 원시 fixture와 과거 seed 확인 |
| `MOLIT_OFFICETEL_RENT` | `RTMSDataSvcOffiRent` | 오피스텔 전월세 | 과거 seed 확인 |
| `MOLIT_VILLA_RENT` | `RTMSDataSvcRHRent` | 연립다세대 전월세 | config·alias code만 확인 |
| `MOLIT_MULTI_FAMILY_RENT` | `RTMSDataSvcSHRent` | 단독다가구 전월세 | config·alias code만 확인 |
| `MOLIT_APT_SALE` | `RTMSDataSvcAptTradeDev` | 아파트 매매 | 원시 fixture와 과거 seed 확인 |
| `MOLIT_OFFICETEL_SALE` | `RTMSDataSvcOffiTrade` | 오피스텔 매매 | 과거 seed 확인 |
| `MOLIT_VILLA_SALE` | `RTMSDataSvcRHTrade` | 연립다세대 매매 | config·alias code만 확인 |
| `MOLIT_MULTI_FAMILY_SALE` | `RTMSDataSvcSHTrade` | 단독다가구 매매 | config·alias code만 확인 |

저장소에서 검증한 아파트 fixture와 seed 경로에서는 전월세 `deposit`·`monthlyRent`, 매매 `dealAmount`, 아파트·오피스텔 건물명 차이가 확인된다. 코드는 `rentDeposit`/`rentFee`, `dealAmt`, `mhouseNm`/`houseNm`/`danjiNm`, `dealArea`/`area`/`totalFloorAr`도 alias로 예상한다. 연립다세대·단독다가구 네 endpoint에는 fixture가 없어 이 alias의 실제 응답 호환을 확정하지 않았다.

### 문제

- 같은 의미의 필드가 `aptNm`, `offiNm`처럼 다른 이름으로 왔다.
- 전월세는 보증금·월세, 매매는 거래금액을 사용해 금액 구조가 달랐다.
- 재실행하면 같은 거래가 중복 삽입될 수 있었다.
- 원시 수집, 정규화, 통계·건물·매물 생성, DB 적재 중 어느 단계가 끝났는지 알아야 했다.
- 대용량 seed를 한 번의 메모리 내 변환으로만 처리하면 실패 후 전체를 다시 시작하기 쉬웠다.

### 원인

원천 API에 공통 식별자가 없고 endpoint별 schema가 달랐으며, 프로젝트 DB의 검색 모델과 원천 거래 모델도 일치하지 않았다. 따라서 단순 “API 호출기 여러 개”보다 source 차이를 흡수하는 정규화 경계와 결정적인 충돌 키가 필요했다.

### 내가 맡은 역할

Issue #7과 #32 및 PR #8과 #33의 핵심 파이프라인 diff를 작성했다. 8개 endpoint 설정, 필드 alias, 금액·계약 유형 변환, 거래 키, manifest, 통계·매물 파생, DB upsert와 검증 명령을 직접 구현했다. 외부 Supabase 실제 실행 환경과 API key 운영은 프로젝트 운영 범위이므로 개인 구현과 분리한다.

### 해결 과정

1. `SOURCE_CONFIG`에 전월세 네 endpoint와 매매 네 endpoint의 URL·property type·transaction family를 선언했다.
2. `FIELD_ALIASES`와 공통 normalizer로 source별 이름 차이를 흡수했다.
3. 금액을 원 단위로 통일하고 월세가 0이면 전세, 0보다 크면 월세로 구분했다.
4. 원천에 안정적인 거래 ID가 없어 source, 위치, 건물, 계약일, 면적, 층, 금액을 조합한 SHA-1 `source_transaction_key`를 만들었다.
5. fetch 결과와 metadata를 manifest에 남기고, manifest에 기록된 비어 있지 않은 원시 XML page는 건너뛰도록 했다. API `resultCode` 성공 여부를 별도 검증하지는 않는다.
6. 정규 거래에서 지역 통계, 건물 통계, geocode anchor, 검색용 매물을 파생했다.
7. `transaction_history`, `region_price_stat`, `building_price_stat`, `properties`를 한 DB connection과 commit 경계에서 conflict upsert했다.

### 핵심 구현

| 구현 | 코드상 역할 |
|---|---|
| `SOURCE_CONFIG` | 8개 endpoint의 URL, 매물유형, 거래군 설정 |
| `FIELD_ALIASES` / `normalize_row` | source별 원시 필드를 공통 20필드 거래 모델로 변환 |
| `source_transaction_key` | source·주소·건물·계약·금액을 결합한 중복 판단 키 생성 |
| `fetch_transactions` / `manifest.json` | 원시 XML과 요청 metadata를 남기고 기록된 비어 있지 않은 raw page 재요청 방지. 성공 checkpoint 보장은 아님 |
| `compute_stats` / `generate_properties` | 지역·건물 통계와 검색용 매물 파생 |
| `load_supabase` | 네 테이블을 한 transaction에서 batch upsert |
| `verify_db` | commit 이후 테이블 count 확인 |

공통 20필드는 `source_api`, `source_transaction_key`, 두 type, 시·도/시·군·구/동/법정동 코드, 지번·건물명·건물 키, 계약 연월·일, 보증금·월세·매매가, 면적·층·건축연도, 원본 JSON이다. 만원 단위 문자열은 원으로 바꾸고, 전월세 endpoint에서 월세가 0이면 전세로 정규화한다.

### 검증

- 커밋된 seed 결과에 거래 8,121건이 존재한다.
- 구성은 아파트 전월세 4,292건, 오피스텔 전월세 1,745건, 아파트 매매 1,786건, 오피스텔 매매 298건이다.
- 8,121건은 2026년 5–6월, 서울 강남·관악·마포, 수원 팔달, 부산 해운대 범위의 과거 결과물이다.
- PR #33에는 소규모 APT_RENT fetch, migration/load/verify 실행 기록이 있다.
- 현재 통합 파이프라인 전용 테스트는 없고, 기존 seed 테스트는 아파트 전월세·매매 fixture 중심이다.

### 결과

원천 schema 차이를 downstream에서 반복 처리하지 않고 정규화 경계에서 한 번 흡수했다. 동일한 source와 거래 키가 충돌하면 update하는 구조로 재적재 시 단순 중복 삽입을 막았고, 한 번 정규화한 거래를 통계·매물 생성에 재사용하도록 흐름을 일원화했다.

### 한계

- 코드 경로는 8개 endpoint를 지원하지만 커밋된 seed에서 실제 데이터가 확인되는 source는 네 종류다.
- “8종”은 8개의 endpoint/source code 조합을 뜻하며 여덟 가지 독립 도메인 모델을 뜻하지 않는다.
- fetch 실패 시 tuple의 다음 page를 중단하고 다음 tuple로 진행하지만 자동 retry/backoff는 없다.
- manifest는 기록된 비어 있지 않은 raw page 재사용 장치이며 API 성공 checkpoint나 exactly-once 처리 보장은 아니다.
- DB load는 코드상 한 transaction이지만 rollback fault-injection 테스트는 없다.
- scheduler나 운영 모니터링, reject ledger, 현재 Supabase row 증거는 없다.

### 보여주는 역량

- 이질적 외부 데이터의 canonical model 설계
- 중복 판단 기준과 transaction 경계 설계
- raw → normalize → aggregate → load 단계 분리
- 재실행 비용을 줄이는 raw-page reuse와 cache, 그리고 그 성공 판정 한계
- 검증 가능한 범위와 운영 미검증 범위를 구분하는 태도

### 근거

- Issue #7, #32
- PR #8, #33
- 커밋 `870fe41`, `d1124c8`, `1cebf2f`, `12ce917`, `1d903b2`, `8b88408`, `3e4c24c`, `d448e31`, `79ae977`, `1621d96`, `21e5e16`, `4a1a6fe`
- `scripts/data_pipeline/pipeline.py`
- `scripts/data_pipeline/README.md`

### 포트폴리오용 약 300자 버전

국토교통부 전월세·매매 8개 endpoint configuration과 alias normalizer를 만들어 20개 공통 필드 경로로 연결하고, source·위치·계약일·면적·금액을 조합한 거래 키를 설계했습니다. manifest raw-page 재사용과 geocode cache로 재실행 비용을 줄였고, 네 파생 테이블을 한 transaction에서 conflict upsert했습니다. 저장소 raw/seed로 호환성이 확인되는 것은 네 source 8,121건이며 나머지 네 endpoint는 fixture 검증이 필요합니다.

### 면접 1분 답변

“지도와 가격 분석이 외부 API를 매 요청마다 부르지 않도록 국토부 데이터를 미리 적재해야 했습니다. 저는 전월세·매매와 매물 유형별 8개 endpoint를 설정하고 공통 alias normalizer와 20필드 model, source·위치·계약일·면적·층·금액 조합의 거래 키를 설계했습니다. manifest에 기록된 raw page를 재사용하고 네 파생 테이블을 한 transaction에서 conflict upsert합니다. 다만 API 성공 checkpoint·자동 재시도·운영 scheduler는 없고, 저장소 raw/seed로 호환성이 확인되는 것은 네 source 8,121건입니다. 그래서 ‘완전한 운영 파이프라인’보다 ‘중복에 강한 offline bootstrap’이라고 설명합니다.”

### 예상 꼬리질문 5개

1. **왜 자연키 대신 SHA-1 조합 키를 썼나요?**  
   원천 전체에 공통인 안정적 ID가 없어 재실행 시 같은 거래를 판별할 결정적 입력이 필요했다. 보안 목적의 hash가 아니라 고정 길이 충돌 키로 사용했다. 취소·정정 거래를 얼마나 동일 거래로 볼지는 추가 도메인 정책이 필요하다.

2. **어디까지 멱등한가요?**  
   같은 `(source_api, source_transaction_key)`가 들어오면 DB unique constraint와 `ON CONFLICT DO UPDATE`로 중복 row를 막는다. 외부 호출, 파일 기록, geocoding까지 exactly-once인 것은 아니므로 “멱등 파이프라인”보다 “중복에 강한 upsert”가 정확하다.

3. **transaction 경계는 어디인가요?**  
   `load_supabase`에서 거래·지역 통계·건물 통계·매물 batch를 한 connection으로 수행하고 마지막에 commit한다. migration은 별도 실행이고, 장애 주입 rollback 테스트는 아직 없다.

4. **왜 source별 adapter class 대신 설정과 alias를 택했나요?**  
   코드는 8 endpoint가 공통 XML 처리 경로를 따른다고 가정하고 설정·alias로 변이를 흡수한다. raw가 검증된 네 source에서는 field 이름·거래군 차이가 주된 변이였다. 나머지 fixture에서 구조 차이가 확인되면 source strategy로 분리해야 한다.

5. **다시 만든다면 무엇을 개선하겠나요?**  
   source별 fixture와 contract test, exponential backoff, 실패 row quarantine, run ID·단계별 metric, staging table 후 원자적 swap, source별 완료 watermark를 추가한다.

### 답변할 때 주의할 표현

- “8개 endpoint 지원”과 “실제 네 source seed 확인”을 한 문장 안에서 구분한다.
- “재실행 가능”을 “exactly-once”나 “완전한 멱등성”으로 바꾸지 않는다.
- 8,121건을 전국·12개월·운영 DB 현재 건수로 표현하지 않는다.
- Python 오프라인 도구라는 점을 숨기지 말고, Java/Spring 직무에서는 DB 모델·중복·transaction 판단을 중심으로 설명한다.

---

## 핵심 사례 2 — 선택 매물 문맥을 잃지 않는 Spring–FastAPI–Frontend 계약

### 한 줄 요약

팀원이 구현한 Spring JWT 경계 위에서 내부 키로 FastAPI를 호출하고, 선택 매물 ID를 가격·안전 DB API와 분석 카드까지 전달하는 계약을 구현했으며, 현재 코드 재검증에서 응답 메타데이터 drift까지 찾아냈다.

### 배경

프론트는 아키텍처 규칙상 FastAPI를 직접 호출할 수 없다. 사용자가 지도에서 선택한 매물을 질문 문맥으로 보내면 Spring이 인증·공개 API 경계를 담당하고, FastAPI의 worker가 Spring의 저장 데이터를 조회해 메시지와 카드를 만들어야 했다.

### 문제

- 브라우저 JWT와 내부 서비스 인증을 분리해야 했다.
- Java의 `Long` 매물 ID와 Python context의 문자열 ID를 양쪽 계약에서 맞춰야 했다.
- 가격 분석은 매물 상세, 최근 거래, 가격 분석 결과를 결합해야 했고 안전 분석은 사전 계산된 DB 값을 사용해야 했다.
- 실패를 정상 빈 카드와 구분해 전달해야 했다.
- 서비스가 독립적으로 진화하면 DTO 필드가 조용히 유실될 위험이 있었다.

### 원인

Spring, FastAPI, Frontend가 각각 다른 DTO와 timeout을 소유했고 자동 생성된 공유 schema나 consumer contract test가 없었다. 초기에는 필드가 맞았더라도 후속 FastAPI 응답 변경을 Spring의 Jackson이 알 수 없는 필드로 무시할 수 있었다.

### 내가 맡은 역할

Spring의 chat controller/service/client 계약, 내부 API key, Spring의 가격·안전 조회 API, FastAPI의 실데이터 호출과 fallback, 프론트의 선택 매물 ID 전달과 초기 legal/analysis card normalizer·rendering을 구현했다. LangGraph supervisor, 현재 최종 챗봇 디자인과 세션 UX는 팀원의 후속 기여다.

### 해결 과정

1. 브라우저는 인증된 `POST /api/v1/chat`만 호출하도록 했다.
2. Spring `ChatRequest`가 `message`, 선택적 `sessionId`, `selectedPropertyId`를 수용하고 `message`의 비어 있음만 검증한 뒤 service에 위임하도록 했다.
3. `AiAgentClient`가 내부 `/internal/agent/chat` 요청을 만들고 `X-Internal-API-Key`를 붙였다.
4. `selectedPropertyId`를 FastAPI `context`에 문자열로 전달했다.
5. FastAPI `SpringClient`가 가격 질문이면 상세·거래·가격 분석 API를, 안전 질문이면 safety summary API를 호출했다.
6. worker 결과를 메시지와 `analysisCards`로 구성하고 Spring과 프론트가 소비하도록 했다.
7. API 실패는 FastAPI에서 구조화된 `SPRING_API_UNAVAILABLE`, Spring의 AI 호출 실패는 502로 드러내도록 했다.

### 핵심 구현

| 계층 | 역할 | 핵심 코드 |
|---|---|---|
| Frontend | 선택 매물 ID·질문 전송, 응답 normalize, 초기 카드 표시 | `frontend/src/api/chat.js`, `chat-normalizer.js` |
| Spring Controller | JWT가 적용되는 공개 chat endpoint, 입력 검증·위임 | `ChatController` |
| Spring Service/Client | 내부 request 조립, timeout, 내부 키, FastAPI 응답을 공개 DTO로 변환 | `ChatServiceImpl`, `AiAgentClient` |
| Spring 도메인 API | 저장된 매물·거래·가격 분석·안전 요약 제공 | property/safety controller·service |
| FastAPI schema/route | camelCase 내부 계약과 worker 결과 직렬화 | `app/api/schemas.py`, `routes.py` |
| FastAPI SpringClient | 선택 매물 기반 Spring API 호출과 오류 구조화 | `app/clients/spring_client.py` |
| LangGraph node | price/safety 결과를 카드와 답변 재료로 변환 | `price_analysis.py`, `safety_analysis.py` |

| 호출 방향 | endpoint·인증 | request 계약 | response·실패 계약 | timeout 기본값 |
|---|---|---|---|---|
| Browser→Spring | `POST /api/v1/chat`, 팀원 구현 JWT filter 적용 | `message: @NotBlank`, optional `sessionId`, optional `selectedPropertyId: Long` | `ApiResponse<ChatResponse>`; 빈 message는 validation error | 브라우저 Axios 설정 |
| Spring→FastAPI | `POST /internal/agent/chat`, `X-Internal-API-Key` | `userId`, `sessionId`, `message`, `context.selectedPropertyId: String?`, `recentMessages` | FastAPI JSON을 Spring DTO로 변환; transport/null 실패는 Spring 502 | connect 2초, read 10초 |
| FastAPI→Spring | 공개 `GET /api/v1/properties/**`, `/api/v1/price-analysis`를 service-to-service 호출; 별도 내부 key 없음 | 선택 ID, 거래 years=3, 분석 조건 또는 safety `radius=500` | HTTP·key·type/value 오류를 `SPRING_API_UNAVAILABLE` 성격의 fallback payload로 변환 | 호출당 5초 |
| Spring→Browser | 같은 chat POST 응답 | 해당 없음 | `intent`, `message`, `sessionId`, `properties`, `legalCards`, `analysisCards` | 바깥 Spring read budget의 영향 |

timeout은 코드 기본값이며 실제 배포 환경변수는 확인되지 않았다. 현재 최종 Vue UI는 analysis card의 type·title·summary·score·metrics를 표시하지만 markup/style·session UX는 팀원 후속 구현이다.

### 검증

- Issue #36/#38/#40/#45/#47/#49와 PR #37/#39/#41/#46/#48/#50에서 단계별 diff를 확인했다.
- Spring controller/client, FastAPI chat·worker, 프론트 normalizer 관련 테스트가 존재한다.
- 관련 PR이 병합되고 양 서비스 배포 workflow 성공 이력이 있다.
- 현재 정적 계약 대조 결과 메시지, legal card, analysis card는 공통 필드가 있으나 응답 전체는 일치하지 않는다.

### 결과

팀원이 구현한 Spring Security JWT 경계 위에 인증된 chat endpoint를 연결하고, FastAPI가 저장 데이터를 Spring의 공개 GET endpoint에서 service-to-service HTTP로 조회하는 구조를 완성했다. 선택 매물 ID가 브라우저 요청에서 AI worker까지 이어지고, 가격·안전 결과를 구조화된 카드로 반환할 수 있게 됐다. 이 과정에서 확인한 실패를 단순 빈 응답으로 숨기지 않는 오류 계약도 마련했다.

### 현재 발견한 계약 drift

- FastAPI `AgentChatResponse`는 `workersCalled`, `toolResults`, `nextActions`를 반환한다. 이 중 공개 API 문서에도 명시된 것은 `workersCalled`이며 `nextActions`는 현재 기본 빈 배열이다.
- Spring `AiAgentClient.AgentChatResponse`에는 이 필드가 없고 `intent`를 기대한다.
- Jackson은 알 수 없는 필드를 무시하므로 메시지와 카드가 있으면 채팅 전체가 즉시 중단되지는 않는다.
- FastAPI에 없는 `intent`는 Spring 공개 응답에서 `null`, 프론트 normalizer에서 빈 문자열이 된다.
- 현재 영향은 non-empty가 될 수 있는 worker metadata·tool result가 Spring에 전달되지 않는다는 점이다. `nextActions`는 현재 항상 기본 빈 배열이라 현행 데이터 유실 사례가 아니라 미래 확장 gap이다. 실제 사용자 장애 범위는 확인되지 않았다.
- PR #63은 FastAPI 계약만 변경했고 Spring·Frontend parsing 확인을 후속 과제로 명시했다. 이를 잡는 HTTP consumer contract test는 없다.

### 한계

- 코드 기본값에서 Spring→FastAPI read timeout은 10초인데 FastAPI의 Spring GET 호출은 각 5초이고 가격 worker가 세 API를 순차 호출하며 LLM client 기본 timeout은 20초다. 배포 환경변수 값은 확인되지 않았지만 기본 budget은 외부가 내부 최악시간보다 짧다.
- retry, circuit breaker, distributed trace가 없다.
- 배포 성공 기록은 실제 선택 매물 E2E smoke를 증명하지 않는다.
- 초기 카드 연결은 본인 기여지만 최종 챗봇 UI·세션 UX는 팀원 기여다.

### 보여주는 역량

- Spring Security 경계와 내부 서비스 인증 분리
- Java/Python 간 DTO·타입·오류 계약 설계
- 저장 데이터 기반 AI tool 연결
- 서비스별 책임과 fallback 범위 설정
- 이미 끝난 구현도 현재 코드 기준으로 다시 감사해 drift를 찾는 태도

### 근거

- Issue #36, #38, #40, #45, #47, #49
- PR #37, #39, #41, #46, #48, #50, 계약 변경 PR #63
- 커밋 `45c393b`, `a3fabed`, `778e9f7`, `cf746ed`, `d4dcbe1`, `e774cce`, `f60581f`, `5e8843b`, `31dfd69`, `228c3fa`, `5716627`, `df50ade`, `8a6c5de`, `d9c0e03`
- `backend/.../service/chat/AiAgentClient.java`
- `backend-ai/app/api/schemas.py`
- `backend-ai/app/clients/spring_client.py`
- `frontend/src/api/chat-normalizer.js`

### 포트폴리오용 약 300자 버전

프론트가 FastAPI를 직접 호출하지 않는 원칙에 맞춰 팀원의 Spring JWT 경계 위에 인증된 chat 계약을 연결하고, `X-Internal-API-Key`로 AI 서비스를 호출하게 했습니다. 선택 매물 ID를 FastAPI context로 전달하고, AI worker가 Spring의 공개 상세·거래·가격·안전 GET API를 service-to-service로 조회해 분석 카드로 반환하도록 연결했습니다. 현재 감사에서는 `workersCalled`가 Spring DTO에서 유실되는 drift와 코드 기본 10초 외부 timeout보다 긴 내부 budget도 기술 부채로 확인했습니다.

### 면접 1분 답변

“아키텍처상 프론트는 Spring만 호출하고 FastAPI는 내부 서비스여야 했습니다. 팀원이 만든 Spring JWT 경계 위에 제가 인증된 chat endpoint를 연결하고, 내부 키로 FastAPI를 호출하게 했습니다. 선택 매물 ID를 넘기면 FastAPI worker가 Spring의 공개 매물·가격·안전 GET endpoint를 service-to-service로 조회해 카드 DTO를 만듭니다. 브라우저부터 AI worker까지 ID와 오류 형식을 맞추는 게 핵심이었습니다. 현재 코드를 다시 대조해보니 FastAPI의 `workersCalled`는 Spring DTO가 받지 않고, Spring은 없는 `intent`를 기대해 metadata가 조용히 유실됩니다. 전체 채팅 장애는 아니지만 consumer contract test 부재를 보여주는 기술 부채입니다.”

### 예상 꼬리질문 5개

1. **왜 프론트가 FastAPI를 직접 호출하지 않나요?**  
   JWT 검증과 사용자 권한, 공개 오류 계약을 Spring 한 곳에 유지하고 내부 AI 서비스의 key와 URL을 브라우저에 노출하지 않기 위해서다.

2. **`workersCalled` 불일치가 왜 컴파일 때 잡히지 않았나요?**  
   Java와 Python이 각자 DTO를 정의하고 JSON으로 통신한다. Jackson은 기본적으로 알 수 없는 응답 필드를 무시하므로 메시지·카드는 역직렬화되고 추가 metadata만 사라질 수 있다.

3. **어떤 테스트를 추가하겠나요?**  
   FastAPI OpenAPI schema를 기준으로 생성한 fixture를 실제 `AiAgentClient`가 역직렬화하는 consumer contract test, Spring 공개 응답과 프론트 normalizer test를 하나의 versioned fixture로 연결하겠다.

4. **timeout은 어떻게 다시 설계하겠나요?**  
   상세와 거래처럼 독립 호출은 병렬화하되, 상세의 지역·유형 값에 의존하는 가격 분석은 그 뒤 실행하거나 하나의 aggregation API로 합친다. 전체 latency budget을 정하고 내부 호출·LLM에 하위 deadline을 전파하며, 외부 read timeout은 그 합과 여유보다 크게 둔다. 무작정 retry하면 지연만 키울 수 있어 오류 종류별로 제한한다.

5. **본인이 UI도 구현했나요?**  
   선택 매물 ID 전달과 초기 legal/analysis card normalizer·렌더링은 직접 구현했다. 현재 최종 챗봇 디자인과 세션 UX는 팀원의 후속 구현이므로 공동 결과로 설명한다.

### 답변할 때 주의할 표현

- `workersCalled` drift를 전체 채팅 장애나 실제 사용자 사고로 단정하지 않는다.
- “UI 전체 구현” 대신 “선택 매물 전달과 초기 카드 연결”이라고 말한다.
- Spring→FastAPI와 FastAPI→Spring의 반대 방향 호출을 구분한다.
- 배포 workflow 성공과 E2E 기능 검증을 동일시하지 않는다.

---

## 핵심 사례 3 — 네 안전시설 API 격리와 시설 접근성 사전 계산

### 한 줄 요약

응답·인증·좌표계가 다른 CCTV·비상벨·보안등·경찰관서 API를 source별 client로 격리하고, bbox+Haversine으로 매물별 시설 접근성 지표를 배치 계산해 사용자 요청에서는 DB만 조회하도록 구현했다.

### 배경

안전 분석은 외부 API를 매 채팅 요청마다 호출하지 않고 배치로 시설을 저장한 뒤, 매물별 점수를 `property_score_stat`에 사전 계산해야 했다. 네 source/code path는 JSON/XML, service key, 좌표 필드가 달랐다. Issue #90에는 실행 환경이 특정되지 않은 CCTV CSV 403이, Issue #92에는 Cloud Run의 CCTV·비상벨 401과 Safemap key 오류가 기록됐다.

### 문제

- CCTV CSV endpoint는 403을 반환했고 JSON endpoint로 전환해야 했다.
- Cloud Run에서는 CCTV·비상벨 401과 생활안전지도 key 오류가 기록됐다.
- 보안등 데이터는 위·경도 또는 Web Mercator 계열 좌표로 올 수 있었다.
- 한 source 실패가 전체 수집을 중단시키면 다른 데이터까지 갱신하지 못한다.
- 모든 매물과 모든 시설의 거리를 전수 계산하면 비용이 커진다.
- 시설 수를 “안전”이라는 하나의 숫자로 보여줄 때 해석 범위를 제한해야 했다.

| 시설 source | 응답·endpoint | 인증 | 좌표 처리 | 운영 확인 범위 |
|---|---|---|---|---|
| CCTV | data.go.kr `cctv_info/info` JSON, 코드상 기본 URL | `PUBLIC_DATA_SERVICE_KEY` 계열 | 위·경도 WGS84 필드 | CSV 403 뒤 JSON client·fixture 구현; 수정 후 live 적재 미확인 |
| 비상벨 | 환경변수로 주입하는 JSON endpoint | CCTV와 같은 public service key | 위·경도 WGS84 필드 | Cloud Run 401 기록; 수정 후 live 적재 미확인 |
| 보안등 | 환경변수로 주입하는 JSON endpoint | 별도 `SECURITY_LIGHT_SERVICE_KEY` | WGS84 또는 `XMAP/YMAP/GEOM` Web Mercator 역변환 | client·fixture 확인, live 적재 미확인 |
| 경찰관서 | 생활안전지도 `IF_0036` XML, 코드상 기본 URL | 별도 `SAFEMAP_SERVICE_KEY` | 응답 위·경도 | `safemap-police-enabled=true`일 때만 bean 활성; live 적재 미확인 |

### 원인

외부 API 계약이 균일하지 않고 인증 키의 전달·encoding 요구도 달랐다. 거리 계산은 DB의 단순 위·경도 범위와 실제 구면 거리가 다르며, 프로젝트는 PostGIS 의존 없이 후보를 효율적으로 줄여야 했다. 또한 수집 실패 관측과 실제 0건을 코드가 완전히 분리하지 못한 문제가 남아 있다.

### 내가 맡은 역할

안전시설 schema/API/client/parser/ingestion/score/AI 소비까지 이어지는 Issue #68~#78과 장애 대응 Issue #90/#92의 핵심 diff를 작성했다. source별 인증과 좌표 변환, Java 계산식, scheduler 조건, 테스트를 구현했다. 최종 챗봇 카드 디자인과 실제 Cloud Run 환경 운영은 개인 구현 범위와 분리한다.

### 해결 과정

1. 시설을 `type`, `source`, `source_id`, 이름, 주소, 위도, 경도의 공통 모델로 저장했다.
2. CCTV·비상벨·보안등 JSON client와 경찰관서 XML client를 분리했다.
3. source별 field alias와 pagination을 parser 안에 가뒀다.
4. WGS84는 그대로 사용하고 `XMAP/YMAP/GEOM`은 Web Mercator 역변환을 적용했다.
5. `(type, source, source_id)` unique 기준으로 update 후 insert했다.
6. 수집 서비스는 상위로 전달된 source 예외를 기록하고 다음 source로 진행하도록 했다.
7. 각 매물의 501m 후보 bounds를 만들고 100개 chunk 범위로 merge해 DB 후보를 조회한 뒤, 다시 매물별 bounds와 Java Haversine 구면 근사 거리로 판정했다.
8. CCTV·비상벨·보안등은 300m, 경찰관서는 500m 안의 수를 세고 cap과 weight로 0–100 점수를 계산했다.
9. 시설 수집과 점수 재계산 scheduler를 각각 조건부로 두어 요청 경로에서는 DB만 조회하게 했다.

### 핵심 구현

| 구현 | 현재 코드상 내용 |
|---|---|
| 네 source client | CCTV JSON, 비상벨 JSON, 보안등 JSON, 생활안전지도 경찰관서 XML |
| 인증 | public service key 계열과 source별 별도 key, URL encoding, 경찰관서 opt-in |
| 좌표 | WGS84 직접 사용, Web Mercator `XMAP/YMAP/GEOM` 역변환 |
| 저장 중복 기준 | `(type, source, source_id)` unique; source ID가 없으면 제한적 fallback ID |
| 후보 축소 | 매물별 최대 반경 500m+1m bounds를 만들고 100개 chunk의 merge bounds로 DB 조회, 이후 매물별 bounds 재검사 |
| 거리 판정 | 지구 반지름 6,371,000m를 사용한 Haversine 구면 근사 |
| 반경 | CCTV·비상벨·보안등 300m, 경찰관서 500m |
| cap/weight | CCTV 10→30, 비상벨 3→25, 보안등 20→25, 경찰관서 1→20 |
| 점수 | cap으로 정규화한 가중합을 반올림하고 0–100 clamp |
| scheduler | 매월 1일 03:00 수집, 03:30 점수; 기본값 비활성 |

### 검증

- source client/parser fixture와 좌표 변환, DAO, ingestion service, 점수 계산 테스트가 존재한다.
- Issue #90→PR #91에서 CCTV JSON client 전환, Issue #92→PR #93에서 key encoding과 source 설정 보강 diff를 확인했다.
- 관련 PR은 병합됐고 후속 Spring 배포 workflow 성공 이력이 있다.
- 테스트 정의 수는 확인되지만 workflow가 test gate가 아니므로 배포 때 항상 실행됐다고 말할 수 없다.

### 결과

외부 API별 변이를 client/parser 경계에 가두고 공통 시설 모델로 저장하는 구조를 만들었다. 거리 계산은 merge bounds와 매물별 bounds로 후보를 줄인 뒤 Haversine 구면 근사로 반경을 판정해, 사용자 요청에서 외부 API나 전체 거리 계산을 하지 않아도 저장된 시설 count와 점수를 제공할 수 있게 했다. 403·401 기록에 대응해 endpoint와 key 처리도 보강했다.

### 한계

- PR #93 이후 네 API의 실제 운영 성공 로그와 적재 row 수가 없다.
- client가 일부 오류를 빈 결과로 반환해 source 실패가 성공 0건처럼 보일 수 있다.
- row별 update→insert라 source 전체 원자성이나 stale row 삭제를 보장하지 않는다.
- scheduler는 기본 비활성이고 Cloud Run 다중 instance의 중복 실행 방지 lock이 없다.
- CCTV row 수는 camera 대수와 같지 않을 수 있다.
- 가중치는 통계적으로 calibration되지 않았고, 범죄 발생 건수를 사용하지 않는다.
- 데이터 미수집 0건과 실제 주변 시설 0건을 구분하는 freshness/completeness 상태가 없다.
- `safety-summary`의 `radius=300/500`은 현재 조회 조건이 아니라 응답에 echo된다. 점수는 항상 CCTV·비상벨·보안등 300m와 경찰관서 500m의 혼합식인데 FastAPI는 이를 “반경 500m 기준 점수”로 요약한다.

### 보여주는 역량

- Spring의 외부 API adapter와 실패 격리
- JSON/XML·인증·좌표계 차이 정규화
- 계산 비용을 요청 경로 밖으로 옮기는 배치 설계
- chunk merge bounds prefilter와 매물별 Haversine 거리 판정의 결합
- 도메인 지표의 의미와 한계를 명시하는 판단

### 근거

- Issue #68, #70, #72, #74, #76, #78, #90, #92
- PR #69, #71, #73, #75, #77, #79, #91, #93
- 커밋 `d4144bd`, `6afe60f`, `ea8bcbe`, `4bf127f`, `48bda7e`, `b242b29`, `007bd48`, `26c7aa7`, `6be6cef`, `0bee1d6`, `a48138b`, `c00c00a`, `e05a637`, `428f37e`, `2c4a47f`, `d2aa9b6`, `537f9ab`, `7ab97f3`, `cad48d2`
- `PropertySafetyScoreServiceImpl.java`
- `SafetyFacilityIngestionServiceImpl.java`
- `service/safety/ingest/*Client.java`
- `SafetyFacilityIngestionScheduler.java`, `PropertySafetyScoreScheduler.java`

### 포트폴리오용 약 300자 버전

CCTV CSV 403과 Cloud Run의 CCTV·비상벨 401이 기록됐고, 네 시설 source는 JSON/XML·인증 키·좌표계가 달랐습니다. Spring source client로 변이를 격리하고 Web Mercator 좌표를 WGS84로 변환했으며, 실패 source가 다른 수집을 막지 않도록 구성했습니다. 매물별 후보는 chunk merge bounds로 줄인 뒤 Haversine으로 300m/500m를 판정해 사전 저장했습니다. 이 점수는 범죄 위험도가 아닌 시설 접근성 proxy이며, 네 source의 운영 성공은 추가 확인이 필요합니다.

### 면접 1분 답변

“안전 분석에서 네 외부 API를 사용자 요청 때마다 호출하면 지연과 장애가 그대로 노출됩니다. Issue에는 CCTV CSV 403과 Cloud Run의 CCTV·비상벨 401이 각각 기록됐고, source마다 응답 형식, key, 좌표계도 달랐습니다. 저는 source별 Spring client와 parser로 차이를 격리하고 Web Mercator 좌표를 위·경도로 변환했습니다. 거리 계산은 각 매물의 501m 후보 bounds를 100개 단위로 합쳐 DB 후보를 조회하고, 매물별 bounds와 Haversine으로 300m/500m를 판정했습니다. 결과를 사전 저장해 조회 경로는 DB만 봅니다. 다만 운영 성공 로그가 없고 이 수치는 범죄도가 아닌 시설 접근성 proxy입니다.”

### 예상 꼬리질문 5개

1. **왜 bbox와 Haversine을 함께 썼나요?**  
   Haversine만 모든 시설에 적용하면 후보 수가 커진다. DB에서 위·경도 사각형 후보를 먼저 줄이고 Java에서 구면 근사 거리를 계산해 300m/500m 기준을 판정했다.

2. **PostGIS를 쓰지 않은 이유는 무엇인가요?**  
   Phase 기록에서 `ST_DWithin`과 비교했으나 당시 schema와 배포에서 공간 extension 의존을 추가하지 않는 쪽을 택했다. 데이터 규모가 커지면 GiST index와 PostGIS가 더 적합할 수 있다.

3. **부분 실패를 정말 처리하나요?**  
   상위로 전달된 source 예외는 기록하고 다음 source로 진행한다. 하지만 일부 concrete client가 예외를 빈 목록으로 바꾸므로 실패 count가 정확하지 않은 한계가 있다. 개선 시 typed failure result를 반환하게 한다.

4. **왜 이 값을 안전 점수라 부르나요?**  
   제품 명칭은 안전 점수지만 구현은 주변 시설 접근성의 규칙 기반 proxy다. 범죄 확률을 예측하지 않는다. UI와 면접에서는 ‘시설 접근성 점수’라고 설명하고 freshness를 함께 노출해야 한다.

5. **Cloud Run에서 scheduler가 안전한가요?**  
   기본 비활성이고 활성화해도 scale-to-zero와 다중 instance 때문에 정확한 실행·단일 실행을 보장하지 않는다. Cloud Scheduler가 인증된 batch endpoint/job을 호출하고 DB advisory lock이나 job table로 중복을 막는 구조가 낫다.

### 답변할 때 주의할 표현

- “네 client를 구현했다”와 “네 API가 운영에서 모두 성공했다”를 구분한다.
- 401의 단일 원인과 완전 해결을 단정하지 않는다.
- 점수를 범죄 위험도, 실제 치안, 범죄 발생 가능성으로 부르지 않는다.
- 최종 AI 카드 UI는 공동 결과이며 개인 기여는 수집·계산·API·초기 연결에 한정한다.

---

## 보조 사례 우선순위

### 1순위 — 지도 줌 조회와 지원 필터 정합성

Java/Spring/JDBC 직무 관련성과 증거 강도가 가장 높다. `region → cluster → property` 데이터량 제어, 공통 SQL 조건, wildcard escape와 현재 UI drift까지 설명할 수 있다. 세 핵심 사례 중 하나의 증거를 더 보수적으로 가져가야 할 때 교체한다.

### 2순위 — 법률 RAG와 비운영 fallback

pgvector 검색·근거 카드·fallback 범위를 설명하는 AI 차별화 사례다. 운영 법령 데이터와 품질 지표가 확인되기 전에는 핵심 성과보다 기술 보조 사례로 둔다.

### 3순위 — 모노레포 분리 배포

Spring과 FastAPI의 Docker·Cloud Run 분리 경험을 짧게 보완한다. 테스트 gate와 실제 smoke 증거가 없으므로 “무중단 운영”이나 “검증된 production 안정성”으로 확대하지 않는다.
