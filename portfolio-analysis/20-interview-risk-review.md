# 살만해 최종 포트폴리오 면접 방어 검수

> 검수 기준일: 2026-07-14  
> 관점: 신입 Java/Spring 백엔드 면접관  
> 근거 우선순위: 현재 코드·Git·PR/Issue → 로컬 보존 산출물 → 사용자 직접 답변. 로컬 산출물과 사용자 답변이 충돌하면 병기하며 임의로 합치지 않는다.

## 1. 결론

가장 강한 개인 사례는 **수동 실행형 거래 데이터 offline bootstrap**, **선택 매물 ID를 잇는 Spring–FastAPI 초기 계약**, **안전시설 adapter·좌표 정규화·시설 접근성 사전 계산**이다. 세 사례 모두 구현 근거는 강하지만 운영 성공, 현재 DB 상태, 완전한 자연키·멱등성, 실제 서비스 간 E2E, 검증된 치안 지표로 넓히면 방어가 무너진다.

이력서에는 거래 수치 중 **8개 source**와 **약 261만 정규화 row**만 유지한다. 나머지 지정 수치는 상세 포트폴리오의 실행 범위 설명에만 쓰고, `generated/properties.jsonl` 7행은 성과에서 삭제한다.

## 2. 보안 정보 검수

실제 값은 이 문서와 응답에 출력하지 않는다. 파일을 수정하거나 key를 회전하지 않았다.

| 의심 파일 | 값의 종류 | Git 추적 여부 | 삭제·회전 판단 |
|---|---|---|---|
| 저장소 루트 `.env` | DB 연결·계정, JWT, 내부 서비스 key, SMTP, Redis 연결 비밀값 | untracked, `.gitignore` 적용, 전체 history 추적 이력 없음 | 공유 금지·로컬 권한 제한. 이미 공유됐거나 노출 가능성이 있으면 관련 비밀값 회전 |
| `portfolio-analysis/12-confirmation-questions.md` | 공공데이터·Safemap 인증 key로 보이는 평문 값 | untracked이나 ignore되지 않음, 전체 history 추적 이력 없음 | 공유본에서 값 삭제/redaction 후 공급기관 key 회전 필요. `git add -A` 전 반드시 제외 |
| `portfolio-analysis.zip` | 이전 분석 문서 묶음 | untracked. 포함된 이전 `12`에서 동일 secret pattern은 발견하지 못함 | 현재 폴더를 다시 압축해 공유할 때는 먼저 `12` redaction |

추적 중인 `.env.example`, test 설정, 배포 가이드에서 탐지된 값은 placeholder·test 값·환경변수 참조였다. 회전 대상이 아니다.

## 3. 최종 주장 목록과 문장별 위험 평가

### CLM-01 — 프로젝트 한 줄 소개

- **현재 문장:** “청년 1인 가구가 거래 정보, 주변 안전시설, 임대차 법령을 지도와 자연어 질문 안에서 함께 비교하도록 만든 부동산 탐색 서비스”
- **위험 등급:** 안전
- **위험한 이유:** 제품 목적 문장으로 구현 범위와 대체로 일치한다. 다만 실제 중개 매물이나 검증된 치안·법률 판단 서비스처럼 들리면 안 된다.
- **근거:** 지도·거래·안전·법률 API와 Vue 화면, `docs/01_PRD.md`, 현재 코드.
- **면접관 질문:** “실제 매물인가요? 안전과 법률 판단을 보장하나요?”
- **안전한 수정 문장:** “실거래 기반 합성 매물, 주변 시설 접근성, 임대차 법령 검색을 지도와 자연어 질문으로 연결한 2인 팀 MVP입니다.”
- **코드·PR 위치:** `frontend/src/views/MapExplorer.vue`, `Chatbot.vue`, PR #17~#95.
- **반드시 공부할 내용:** `MVP_SYNTHETIC`의 의미, 시설 접근성 proxy, 법률 RAG의 품질 한계.

### CLM-02 — 개인 역할 범위

- **현재 문장:** “F-1·F-3·F-4의 Spring·FastAPI·Vue·DB 핵심을 구현했다.”
- **위험 등급:** 표현 축소 권장
- **위험한 이유:** Git diff는 넓은 개인 기여를 뒷받침하지만 “Frontend·Backend·DB 전체” 또는 제품 전체 단독 구현으로 들릴 수 있다.
- **근거:** 사용자 직접 답변, 사용자 author의 pipeline·RAG·chat·safety·map commit과 PR.
- **면접관 질문:** “JWT, Supervisor, 최종 챗봇 UI도 본인이 만들었나요?”
- **안전한 수정 문장:** “기능 단위 분담에서 거래·지도, 법률 RAG, 선택 매물 시세·시설 접근성의 초기 vertical code path를 여러 레이어에 걸쳐 구현했습니다.”
- **코드·PR 위치:** PR #8/#17~#50/#54~#79/#91~#95.
- **반드시 공부할 내용:** 본인 commit과 팀원 commit 경계, 공동 결과를 설명하는 법.

### CLM-03 — 8-source 정규화와 대규모 실행

- **현재 문장:** “8개 거래 source를 공통 모델로 정규화했고 보존 산출물에서 2,612,697행을 확인했다.”
- **위험 등급:** 안전
- **위험한 이유:** 숫자와 코드가 맞지만 Git 비추적 로컬 산출물, 세종 제외 범위, 현재 DB가 아니라는 조건이 빠지면 위험하다.
- **근거:** `SOURCE_CONFIG`, manifest/raw 전수 감사, normalized JSONL 행 수, 사후 replay.
- **면접관 질문:** “GitHub만으로 재현할 수 있나요? 전국 데이터와 현재 DB row인가요?”
- **안전한 수정 문장:** “국토부 8개 거래 source를 공통 모델로 정규화했고, 세종을 제외한 Git 비추적 보존 실행에서 약 261만 unique row를 확인했습니다.”
- **코드·PR 위치:** `scripts/data_pipeline/pipeline.py:33`, Issue #32, PR #33, commit `79ae977`~`4a1a6fe`.
- **반드시 공부할 내용:** 8 source 이름, 267 `LAWD_CD`, 12개 월 파티션, artifact와 DB의 차이.

### CLM-04 — 거래 key와 upsert

- **현재 문장:** “자연키를 설계하고 upsert로 재실행 멱등성을 보장했다.”
- **위험 등급:** 면접 위험
- **위험한 이유:** 현재 key는 15개 값의 SHA-1 fingerprint다. 같은 조건의 서로 다른 거래를 합칠 수 있고 정정 가격은 새 key가 될 수 있다. DB conflict write 외의 전체 파이프라인은 멱등하지 않다.
- **근거:** `source_transaction_key`, unique constraint, PostgreSQL `ON CONFLICT DO UPDATE`.
- **면접관 질문:** “동일 건물·층·면적·가격의 두 거래와 정정·취소 거래는 어떻게 구분합니까?”
- **안전한 수정 문장:** “원천 공통 ID가 없어 결정적 fingerprint를 도입하고, 동일 fingerprint 재입력의 단순 중복 insert를 PostgreSQL conflict upsert로 줄였습니다.”
- **코드·PR 위치:** `pipeline.py:350-420, 944-970`, migration, PR #8/#33.
- **반드시 공부할 내용:** 자연키와 fingerprint, false merge/split, upsert와 멱등성·exactly-once 차이.

### CLM-05 — Supabase 적재 성과

- **현재 문장:** “대규모 거래 결과를 Supabase에 적재했다.”
- **위험 등급:** 면접 위험
- **위험한 이유:** 사용자는 당시 적재를 직접 확인했다고 답했지만 어느 subset을 각 테이블에 몇 행 적재했는지, 당시 log·현재 row·rollback 결과가 없다.
- **근거:** load code와 PR 실행 보고는 A, 역사적 적재는 U, 현재 DB는 timeout.
- **면접관 질문:** “261만 건 전부 적재했나요? insert/update 수와 rollback을 보여줄 수 있나요?”
- **안전한 수정 문장:** “psycopg 기반 네 테이블 적재 경로를 구현했고 당시 Supabase 적재를 직접 확인했지만, 적재 subset과 현재 row 수는 보존되지 않았습니다.”
- **코드·PR 위치:** `pipeline.py:891-1147`, PR #33.
- **반드시 공부할 내용:** connection·commit 경계, batch size와 transaction의 차이, `verify_db`가 table total count만 출력한다는 점.

### CLM-06 — 선택 매물 계약 구현

- **현재 문장:** “선택 매물 ID가 Frontend→Spring→FastAPI를 거쳐 가격·안전 카드로 돌아오는 계약을 구현했다.”
- **위험 등급:** 표현 축소 권장
- **위험한 이유:** 세 모듈 코드 path와 module test는 있지만 실제 FastAPI JSON을 실제 `AiAgentClient`가 읽는 HTTP consumer test와 배포 E2E smoke가 없다.
- **근거:** request/response DTO와 worker/client 코드, PR #37~#50.
- **면접관 질문:** “PR #50이 최종 통합이라면 왜 Spring test가 `ChatService`를 mock합니까?”
- **안전한 수정 문장:** “선택 매물 ID를 세 모듈 사이로 전달하고 초기 분석 카드로 변환하는 코드 계약을 구현했으며, 실제 HTTP consumer test는 남은 과제입니다.”
- **코드·PR 위치:** `ChatRequest.java`, `AiAgentClient.java`, `schemas.py`, `spring_client.py`, `chat-normalizer.js`.
- **반드시 공부할 내용:** 정확한 DTO 변환, fallback/502 차이, timeout budget.

### CLM-07 — `workersCalled`/`intent` 계약 부채

- **현재 문장:** “`workersCalled`가 유실되고 Spring은 FastAPI에 없는 `intent`를 기대한다.”
- **위험 등급:** 안전
- **위험한 이유:** 정적 DTO drift는 확인됐다. 다만 Spring은 필수 intent를 강제하는 것이 아니라 nullable field를 선언하며 실제 사용자 영향은 미측정이다.
- **근거:** FastAPI schema/routes, Spring private response record, Frontend normalizer.
- **면접관 질문:** “그럼 현재 채팅은 전부 실패합니까? 실제 장애였나요?”
- **안전한 수정 문장:** “현재 기본 매핑에서 worker metadata는 Spring 경계에서 소비되지 않고 nullable `intent`는 null이 되지만, 공통 card type이 맞는 경우의 전체 HTTP 성공과 실제 UX 영향은 미확인입니다.”
- **코드·PR 위치:** PR #63 `d9c0e03`, `schemas.py:27`, `AiAgentClient.java:90`, `chat-normalizer.js:21`.
- **반드시 공부할 내용:** Jackson unknown-field 처리 조건, missing nullable property, consumer contract test.

### CLM-08 — 세션과 대화 문맥

- **현재 문장:** “대화 세션을 지원한다.”
- **위험 등급:** 표현 축소 권장
- **위험한 이유:** UI는 localStorage로 대화를 묶지만 Spring은 `recentMessages=[]`을 보내며 서버 측 multi-turn memory 증거가 없다.
- **근거:** `chatSessionStore.js`, `AiAgentClient.ChatContext`.
- **면접관 질문:** “session ID가 있는데 이전 대화를 모델이 기억합니까?”
- **안전한 수정 문장:** “팀원이 localStorage 기반 세션 UX를 구현했으며, 현재 agent 요청은 과거 메시지를 전달하지 않습니다.”
- **코드·PR 위치:** `frontend/src/store/chatSessionStore.js`, `AiAgentClient.java:50`.
- **반드시 공부할 내용:** client-side grouping과 server conversation state의 차이.

### CLM-09 — AI 개인 기여

- **현재 문장:** “AI 채팅 기능을 구현했다.”
- **위험 등급:** 표현 축소 권장
- **위험한 이유:** 법률 RAG, SpringClient, 가격·안전 worker와 초기 card는 개인 기여지만 Supervisor와 최종 UX는 팀원 기여다.
- **근거:** PR #17/#37/#41/#46/#48/#50, 팀원 PR #63/#80 이후.
- **면접관 질문:** “LangGraph Supervisor와 JWT도 본인이 설계했나요?”
- **안전한 수정 문장:** “법률 ingestion·검색·근거 card와 선택 매물 가격·안전 worker의 초기 연동을 구현했고, Supervisor와 최종 UI는 팀원이 구현했습니다.”
- **코드·PR 위치:** `ingest_legal_docs.py`, `legal_rag.py`, `spring_client.py`, PR #17~#50.
- **반드시 공부할 내용:** Supervisor routing과 worker의 차이, pgvector retrieval 한계.

### CLM-10 — 안전시설 adapter와 좌표 계산

- **현재 문장:** “네 안전시설 API를 통합하고 정확한 거리로 사전 계산했다.”
- **위험 등급:** 표현 축소 권장
- **위험한 이유:** 네 provider의 운영 성공이 아니라 네 시설 유형의 adapter code path다. 좌표 변환과 Haversine은 library 없는 수동 공식·구면 근사다.
- **근거:** 네 client, parser fixture, score service, PR #73/#77/#91/#93, Issue #72/#76/#90/#92.
- **면접관 질문:** “변환 library와 CRS는 무엇입니까? 네 source가 운영에서 모두 성공했습니까?”
- **안전한 수정 문장:** “네 시설 유형의 Spring adapter 경로를 구현하고, 보안등 응답에서 WGS84가 없을 때 `XMAP/YMAP/GEOM`을 EPSG:3857로 가정해 수동 역변환한 뒤 bbox와 Haversine 구면 근사로 고정 반경 source row 수를 사전 계산했습니다.”
- **코드·PR 위치:** `service/safety/ingest`, `PropertySafetyScoreServiceImpl.java`, PR #73/#77/#91/#93.
- **반드시 공부할 내용:** EPSG:3857 역식, 두 지구 반지름, bbox/Haversine 오차, provider 실명 미확인 범위.

### CLM-11 — 안전 점수

- **현재 문장:** “주변 안전 점수를 계산했다.”
- **위험 등급:** 면접 위험
- **위험한 이유:** 범죄·인구·시간·시설 상태를 쓰지 않은 개인 휴리스틱이다. CCTV cap은 카메라 대수나 고유 설치지점 수로 검증하지 않은 source row 수다.
- **근거:** score 상수와 사용자 직접 답변.
- **면접관 질문:** “가중치의 통계 근거가 무엇이며 CCTV 10은 카메라 10대입니까?”
- **안전한 수정 문장:** “개인이 정한 미보정 가중치로 고정 반경 시설 row 접근성을 비교하는 MVP 보조값을 구현했습니다.”
- **코드·PR 위치:** `PropertySafetyScoreServiceImpl.java:25-93`, PR #77.
- **반드시 공부할 내용:** heuristic calibration, proxy metric, source failure 0과 실제 0의 구분.

### CLM-12 — 안전 batch 운영

- **현재 문장:** “Cloud Run scheduler로 네 시설을 수집해 Supabase 저장을 검증했다.”
- **위험 등급:** 면접 위험
- **위험한 이유:** 일시 실행은 사용자 답변뿐이고 실제 log·source별 수·적용 revision이 없다. 제시 명령에는 Safemap opt-in과 별도 보안등 key 설정이 보이지 않아 두 source의 성공·실패를 추론할 수 없고, 다른 source 설정도 현재 코드와 충돌할 가능성이 있다.
- **근거:** scheduler code/default off는 A, 일시 설정·일부 row 확인은 U.
- **면접관 질문:** “정확히 몇 번, 어떤 source가 성공했고 경찰 source는 어떻게 활성화했습니까?”
- **안전한 수정 문장:** “기본 off scheduler를 일시 활성화해 일부 row를 확인했다고 답했지만, source별 성공과 실행 횟수는 보존되지 않았습니다.”
- **코드·PR 위치:** scheduler classes, `application.properties:49-55`, `SafemapPoliceFacilityClient.java:25`, `.github/workflows/deploy-backend-cloud-run.yml:46-47`, PR #75/#77/#93, 사용자 답변의 일시 실행 명령.
- **반드시 공부할 내용:** Cloud Run scale-to-zero, 독립 cron, distributed lock, Cloud Scheduler/Run Job.

### CLM-13 — 테스트 역량

- **현재 문장:** “TDD로 테스트를 직접 설계·작성해 품질을 검증했다.”
- **위험 등급:** 삭제 권고
- **위험한 이유:** 사용자 답변상 관련 테스트 코드는 Codex가 생성했다. 정확한 대상 파일과 사람이 직접 설계·검토한 case가 특정되지 않는다.
- **근거:** 사용자 직접 답변, Git의 test commit·PR 실행 기록·CodeRabbit 후속 diff.
- **면접관 질문:** “직접 작성하지 않았다면 어떤 case를 왜 넣었고 실패 결과를 어떻게 해석했습니까?”
- **안전한 수정 문장:** “사용자 답변상 관련 테스트는 Codex가 생성했습니다. Git에서는 별도로 사용자 test commit·PR 실행 기록·자동 리뷰 후속 diff를 확인했지만, 두 근거가 가리키는 정확한 파일·case는 연결하지 못했습니다.”
- **코드·PR 위치:** 각 module tests, PR #50/#69~#95.
- **반드시 공부할 내용:** 현재 tests의 mock/fake 경계, 빠진 consumer contract case를 직접 설계하는 방법.

### CLM-14 — 현재 테스트 실행 결과

- **현재 문장:** “테스트가 모두 통과한다.”
- **위험 등급:** 표현 축소 권장
- **위험한 이유:** 이번 재실행은 Spring 77, Frontend 26, FastAPI 61 module tests 통과다. 실제 Spring↔FastAPI E2E와 DB·공공 API live test가 아니다.
- **근거:** 2026-07-14 현재 각 module 명령 재실행. FastAPI TestClient deprecation warning 1건.
- **면접관 질문:** “실제 서비스 간 JSON 계약과 외부 API도 포함됩니까?”
- **안전한 수정 문장:** “현재 HEAD의 세 module test suite는 통과했지만, 실제 HTTP consumer·live external API·E2E는 포함하지 않습니다.”
- **코드·PR 위치:** `backend/src/test`, `backend-ai/tests`, `frontend/src/**/*.test.mjs`.
- **반드시 공부할 내용:** unit/integration/consumer contract/E2E 구분.

### CLM-15 — 배포·협업 자동화

- **현재 문장:** “Spring 16회, FastAPI 9회, GitLab sync 8회 성공으로 안정성을 검증했다.”
- **위험 등급:** 삭제 권고
- **위험한 이유:** 확인 시점에 따라 바뀌는 workflow run 수이며 test gate·E2E·무중단을 뜻하지 않는다.
- **근거:** Actions snapshot과 workflow YAML.
- **면접관 질문:** “배포 전에 어떤 test가 gate이며 실패 rollback은 있습니까?”
- **안전한 수정 문장:** “Spring·FastAPI 경로별 Cloud Run 배포와 GitLab sync workflow를 구성했지만, 현재 test gate와 무중단 보장은 없습니다.”
- **코드·PR 위치:** `.github/workflows`, PR #52.
- **반드시 공부할 내용:** path filter, `needs`, artifact 동일성, rollout/rollback.

### CLM-16 — 협업·리뷰와 최종 UI

- **현재 문장:** “코드 리뷰와 최종 UI를 함께 완성했다.”
- **위험 등급:** 표현 축소 권장
- **위험한 이유:** 리뷰는 CodeRabbit 자동 리뷰가 중심이고 사람 review는 확인되지 않는다. 초기 지도·card는 개인, 최종 chat/session/safety UI는 팀원 후속 구현이다.
- **근거:** GitHub review objects, CodeRabbit follow-up commit, 팀원 UI commit.
- **면접관 질문:** “사람 간 review나 API 회의에서 어떤 피드백을 주고받았습니까?”
- **안전한 수정 문장:** “모노레포 PR에서 CodeRabbit 지적을 후속 commit으로 반영했고, 제 초기 계약·rendering 위에 팀원이 최종 UI를 고도화했습니다.”
- **코드·PR 위치:** CodeRabbit review와 `6cb0c85`, `537f9ab`; 팀원 `e4ba51a`, `dedb3d6`, `439e49a`.
- **반드시 공부할 내용:** 저장소로 확인되는 협업과 회의·발표처럼 사용자 답변만 있는 사실의 구분.

## 4. 가장 위험한 문장 10개

| 순위 | 위험 문장 | 안전한 문장 |
|---:|---|---|
| 1 | 전국 1년치 8종 데이터를 운영 DB에 적재했다 | 세종 제외 16개 시·도의 12개 월 파티션을 조회한 Git 비추적 보존 산출물을 검증했다 |
| 2 | 자연키와 upsert로 전체 파이프라인 멱등성을 보장했다 | 결정적 fingerprint와 conflict upsert로 동일 fingerprint의 단순 중복 insert를 줄였다 |
| 3 | 정규화에서 138,598개의 중복을 제거했다 | 사후 replay에서 reject 6,370과 동일 fingerprint 후속 occurrence 132,228로 나뉘며 후자는 실제 중복 거래 수가 아니다 |
| 4 | Supabase에 261만 건과 매물 8천 개를 적재했다 | 당시 적재는 사용자 직접 확인이지만 subset·table row·현재 DB는 미확인이다 |
| 5 | 선택 매물 E2E 계약을 검증했다 | 세 모듈 코드 path와 module test를 구현했으나 실제 HTTP consumer test는 없다 |
| 6 | `workersCalled` 문제를 해결했다 | current static drift를 발견했으며 아직 해결하지 않았다 |
| 7 | 네 안전 API를 운영 통합했다 | 네 시설 유형을 수용하는 adapter code path를 구현했다 |
| 8 | Haversine으로 실제·정확한 거리를 계산했다 | bbox 후보 뒤 Haversine 구면 근사 거리를 계산했다 |
| 9 | 검증된 안전 점수를 만들었다 | 미보정 시설 row 접근성 proxy를 만들었다 |
| 10 | TDD로 테스트를 직접 설계·작성했다 | Codex 생성은 사용자 답변, test commit·PR 실행·자동 리뷰 diff는 Git 근거로 분리하고 정확한 파일 연결이나 직접 설계 저작은 주장하지 않는다 |

## 5. 지정 수치 집중 검수

| 수치 | 정확한 의미·산식 | 근거 | 환경·전체/일부 | 재현성 | 포트폴리오 사용 판단 |
|---:|---|---|---|---|---|
| 8 source | 아파트·오피스텔·연립다세대·단독다가구 × 전월세·매매 | `SOURCE_CONFIG`, manifest distinct source | 로컬 검증 실행의 source 전체 | 코드·artifact로 재현 | 이력서 유지 |
| 267 | 조회 입력의 5자리 `LAWD_CD` 수 | 기준 CSV 267행, manifest distinct prefix | 세종 없는 scoped input | 파일로 재현 | 상세만. “267개 시군구”보다 조회 코드라고 말함 |
| 12개 월 파티션 | `dealYmd=202507..202606`의 월별 조회 구간 | manifest | scoped artifact 전체, 데이터 완결성은 미보장 | 파일로 재현, 재호출 값은 바뀔 수 있음 | 상세만 |
| 25,632 | `8×267×12` 기본 source-region-month tuple | manifest unique tuple | 첫 page 기준 기본 그룹 | 재현 | 상세만 |
| 후속 page 321 | page 2 이상 manifest entry occurrence | manifest; 302개 tuple, 최대 page 4 | pagination 일부 | 재현 | 상세만. paginated 그룹 수와 구분 |
| XML 25,953 | `25,632+321` raw page 파일 | manifest/raw | scoped raw 전체 | 재현 | 상세만 |
| 원시 item 2,751,295 | 모든 raw XML의 `<item>` occurrence 합 | raw 전수 파싱·`totalCount` 대조 | scoped raw 전체, unique 거래 아님 | 로컬 artifact로 재현 | 상세만 |
| 정규화 2,612,697 | current normalizer 통과 뒤 source/fingerprint dedupe된 unique row | normalized JSONL·사후 replay | 검증 환경 파일, 현재 DB 아님 | 재현 | 이력서에는 “약 261만”만 유지 |
| 차이 138,598 | `2,751,295-2,612,697` = reject 6,370 + 후속 fingerprint occurrence 132,228 | HEAD `pipeline.py`로 read-only replay | 사후 분석, 원래 run counter 아님 | 로컬 raw가 있으면 재현 | 상세/면접팩만. 실제 중복 거래 수로 사용 금지 |
| 공통 필드 20 | 현재 `TRANSACTION_COLUMNS`의 canonical row field 수 | normalizer·insert column | code schema 결과 | 재현 | 상세만. 숫자 자체의 성과 가치는 낮음 |
| lite 매물 4,000 | `MVP_SYNTHETIC` subset row | `lite/properties.jsonl` | 전체 거래의 일부·DB 적재 미확인 | 파일로 재현 | 이력서 삭제, 상세에서 synthetic 설명용 |
| full 생성 7 | `generated/properties.jsonl`의 중간 합성 매물 row | 해당 파일 | 불완전한 intermediate snapshot | 행 수만 재현, 경위 미확인 | 성과에서 삭제, evidence/risk에만 보존 |

가장 방어하기 어려운 숫자는 **132,228**, **4,000**, **7**이다. 132,228은 실제 중복 거래가 아니고, 4,000은 합성 subset이며, 7은 경위가 남지 않은 intermediate snapshot이다.

## 6. 거래 파이프라인 압박 검수

| 질문 | 현재 근거로 가능한 답변 | 한계·공부할 점 |
|---|---|---|
| 8 source는 무엇인가 | `APT/OFFICETEL/VILLA/MULTI_FAMILY` 각각 RENT/SALE | `VILLA`=연립·다세대, `MULTI_FAMILY`=단독·다가구 |
| 왜 20개 필드인가 | source/id 2, 유형 2, 위치·건물 7, 계약 2, 금액 3, 면적·층·연도 3, raw 1의 현재 row 결과 | 사전 최적화 숫자가 아님. alias slot은 17개이며 `road_address` alias는 출력 미사용 |
| source별 필드 차이 | 건물명·면적·보증금·월세·매매가·계약일·동 alias가 다름 | 첫 non-empty를 고르며 동시 alias 충돌 검증 없음 |
| alias normalizer 입출력 | XML item dict + manifest metadata → 20-field normalized dict 또는 reject | reject 상세 reason counter 없음 |
| 충돌 키 구성 | source, 법정동·동·지번, 건물, 계약일, 유형, 면적, 층, 세 금액의 15값 SHA-1 | 보안 hash가 아니라 fingerprint |
| 자연키로 충분한가 | 아니다 | 동일조건 거래 false merge, 정정 false split, 취소 상태 미모델링 |
| upsert 방식 | psycopg `executemany` + PostgreSQL `INSERT ... ON CONFLICT DO UPDATE` | ORM 사용 아님 |
| 재실행 시 무엇이 갱신되나 | 같은 fingerprint이면 비식별 컬럼과 raw JSON 등이 update | 가격·날짜 같은 fingerprint 입력이 바뀌면 새 row 가능 |
| transaction 경계 | load 호출의 네 table batch가 한 connection·마지막 commit 공유 | migration·file generation·verify는 밖, fault-injection 없음 |
| 일부 page 실패 | 예외를 `errors.json`에 남기고 해당 tuple page loop를 중단한 뒤 다음 tuple 가능 | retry/backoff·completeness gate 없음, 앞 page가 부분 publish될 수 있음 |
| 138,598을 왜 분리 못했나 | 원래 run은 counter가 없었지만 이번 사후 replay로 상위 두 원인은 분리함 | reject 조건별 세부 원인과 실제 중복/false merge 비율은 여전히 모름 |
| HTTP 성공과 유효 수집 | non-2xx는 예외지만 status를 ledger에 저장하지 않고 code는 `resultCode`를 checkpoint로 검사하지 않음 | 이번 artifact만 별도 전수 감사로 `000/OK`; DB 성공과는 별개 |
| 세종 누락 이유 | 기준 `lawd-codes.csv`에 `36110`이 없음 | 누락한 정확한 경위는 Git으로 확인 불가 |
| 오프라인 적재 이유 | 외부 API latency·quota·장애를 요청 경로에서 제거하고 같은 DB snapshot 사용 | 성능 개선 수치 없음 |
| scheduler 없이 pipeline인가 | fetch→normalize→derive→load 단계가 있어 pipeline이라 부를 수 있음 | “수동 실행형 offline bootstrap”으로 한정. 운영·증분·정기 pipeline 금지 |

## 7. Spring–FastAPI–Frontend 계약 압박 검수

### 실제 계약

| 구간 | 필드·동작 |
|---|---|
| Frontend→Spring | `message`, `sessionId`, optional `selectedPropertyId` |
| Spring DTO | `message: @NotBlank String`, `sessionId: String`, `selectedPropertyId: Long` |
| Spring→FastAPI | `userId`, `sessionId`, `message`, `context.selectedPropertyId: String?`, `recentMessages: []`, 내부 key |
| FastAPI→Spring | `workersCalled`, `answer`, properties, legal/analysis cards, `toolResults`, `nextActions`; `intent/sessionId` 없음 |
| Spring→Frontend | nullable `intent`, `answer→message`, request `sessionId` echo, properties/cards; worker metadata 없음 |
| Frontend normalize | missing intent→`''`; 현재 화면은 intent로 분기하지 않음 |

### 압박 답변

- **본인 범위:** Spring chat controller/service/client, 내부 key, 선택 ID 변환, Spring 가격·안전 read API, FastAPI SpringClient와 price/safety worker 연결, 초기 card normalizer/rendering.
- **팀원 범위:** JWT core, Supervisor와 `workersCalled` 전환, 최종 chat/localStorage session/safety-card UI.
- **실패 처리:** Spring→FastAPI non-2xx·timeout·null은 주로 502 `AI_SERVICE_UNAVAILABLE`. FastAPI 내부 Spring 조회의 HTTP 오류·필수 필드 누락(`KeyError`)·type/value 오류는 200 agent response 안의 `SPRING_API_UNAVAILABLE` fallback이 될 수 있다.
- **timeout:** outer Spring read 10초보다 내부 5초 순차 호출과 20초 LLM 기본값이 커 구조적 budget inversion이 있다. 실제 배포 override·latency는 미확인이다.
- **`workersCalled`:** current default mapping에서 Spring이 소비하지 않는다. 해결되지 않았다.
- **`intent`:** Spring nullable field에 null, Frontend에서 빈 문자열. “필수 intent 때문에 전체 실패”는 틀리다.
- **실제 역직렬화:** unknown top-level field는 현재 default converter에서 무시될 수 있으나 card field/type drift는 전체 conversion failure가 될 수 있다. 실제 `AiAgentClient` HTTP test가 없다.
- **변경 감지:** 각 module test는 fake/mock/fixture이고 연결 contract를 검사하지 않는다. 현재 CI deploy gate도 없다.
- **OpenAPI:** FastAPI가 자동 생성하지만 versioned artifact·codegen·consumer CI에 쓰지 않았다. 당시 미사용 이유는 기록되지 않았다.
- **추가할 consumer test:** MockWebServer/WireMock으로 실제 FastAPI fixture를 응답하고 실제 `AiAgentClient`의 request key·Long→String·`recentMessages=[]`와 response mapping을 검증한다. 같은 Spring public fixture를 Frontend normalizer에 재사용하고 null/additive/type error/non-2xx/timeout을 CI gate에 포함한다.

## 8. 안전시설 접근성 압박 검수

| 항목 | 확인된 사실 | 인정할 한계 |
|---|---|---|
| 네 유형 | CCTV, 비상벨, 보안등, Safemap `IF_0036` item의 `POLICE` 정규화 | `fclty_ty`로 실제 경찰서만 filter하지 않음 |
| 확인된 endpoint·서비스 | CCTV 기본 URL은 `apis.data.go.kr` 계열, Safemap 기본 URL은 `safemap.go.kr/IF_0036` 계열 | 실제 제공기관 명칭과 비상벨·보안등 세부 기관은 저장소만으로 확정 불가 |
| 인증 | public-data key 계열, 보안등 별도 key, Safemap 별도 key+opt-in | 제시 명령에 police opt-in과 별도 보안등 key 설정이 보이지 않음; 기존 환경값 유무를 몰라 성공·실패 모두 추정 금지 |
| key encoding | raw public key를 code에서 URL encode | 이미 encoded key면 double-encoding 위험. 해당 배포 값 미확인 |
| 응답 구조 | CCTV/비상벨/보안등 JSON, Safemap XML; source alias/pagination 차이 | live response 전체와 수정 후 성공 log 미보존 |
| 좌표 | 각 adapter는 WGS84를 우선 사용하고, 보안등 응답의 WGS84가 없을 때만 `XMAP/YMAP/GEOM` fallback을 EPSG:3857로 가정 | provider live CRS 전체 검증 아님 |
| 변환 | 보안등 fallback에서 GIS library 없이 R=6,378,137m의 Web Mercator 역식을 Java `Math`로 구현 | fixture 허용오차·전지구 범위만 검증; 한국 영역 sanity check와 live CRS 확인 없음 |
| 거리 | score service에서 R=6,371,000m Haversine 구면 근사 | “실제·정확한 거리” 금지 |
| 반경 | 세 유형 300m, `POLICE` row 500m | API `radius`는 계산에 쓰이지 않고 echo됨 |
| 가중치 | row cap 10/3/20/1과 최대 기여 30/25/25/20 | 개인 heuristic, calibration·전문가 검토 없음; CCTV row≠camera count |
| 부분 실패 | 상위 service는 throw source 다음 진행 | concrete client가 오류를 empty/partial로 축소해 failed=0 가능 |
| DB write | 시설은 row update→insert, score stat은 transactional upsert | source snapshot·stale deletion·batch 전체 원자성 없음 |
| scheduler | code default off, 월 1일 03:00/03:30 | 일시 실행 명령은 독립 cron, 정확히 1회·선후 보장 없음 |
| Supabase | 사용자가 어떤 안전시설 row를 봤다고 답함 | 유형·수·시각·score row·현재 DB 미확인 |
| 지표 의미 | 시설 접근성 비교용 MVP proxy | 범죄 위험·절대 치안·안전 보장 아님 |

## 9. AI와 테스트 기여 검수

| 구분 | 사용할 수 있는 주장 | 금지할 주장 |
|---|---|---|
| 개인 AI | 법률 ingestion·embedding client·pgvector retrieval·근거 card·prompt grounding, SpringClient, price/safety worker 초기 연동 | Supervisor·전체 agent architecture 단독 구현 |
| 팀원 AI/인증 | Supervisor, `workersCalled` response 전환, JWT core | 개인 기여로 전환 |
| 테스트 생성 | 사용자 답변상 Codex 생성. Git에는 별도로 사용자 test commit·PR 실행·CodeRabbit 후속 수정이 존재하나 정확한 파일·case 연결은 미확인 | 특정 PR 통합·직접 hand-written·직접 TDD 설계라고 단정 |
| 사람 설계·검토 | 정확한 파일·case·검토 범위 미확인 | 추정 |
| 현재 실행 | 2026-07-14 로컬 검수에서 Spring 77, Frontend 26, FastAPI 61 통과 | 서비스 간 E2E·live API·현재 DB 검증으로 확대 |
| 본인 테스트 역량 | mock/fake 경계를 구분하고 빠진 consumer contract test를 설계·설명하는 범위 | 기존 모든 test의 설계 저작 성과 |

## 10. 팀원 기여와 혼동하기 쉬운 항목

- Spring Security JWT core는 팀원 기여이고, 본인은 그 위에 chat endpoint를 연결했다.
- LangGraph Supervisor와 `workersCalled` 전환은 팀원 기여이고, 본인은 legal/price/safety worker와 초기 계약을 구현했다.
- 최종 챗봇 markup·style, localStorage session UX, 최종 safety card UI는 팀원 기여다.
- 현재 화면과 agent flow는 개인·팀원 변경이 이어진 공동 결과다.
- CodeRabbit 자동 review를 사람 review·pair programming·회의 합의로 바꾸지 않는다.

## 11. 코드 복습이 필요한 위치

1. `scripts/data_pipeline/pipeline.py:33-103, 350-524, 891-1147` — source, alias, fingerprint, fetch failure, dedupe, transaction/upsert.
2. `database/migrations/202606160001_create_properties.sql` — 거래 unique 조건과 schema.
3. `backend/.../service/chat/AiAgentClient.java` — 정확한 request/response 변환과 timeout.
4. `backend-ai/app/api/schemas.py`, `api/routes.py` — producer response와 없는 `intent`.
5. `backend-ai/app/clients/spring_client.py` — 세 순차 조회, fallback, public GET.
6. `frontend/src/api/chat-normalizer.js`, `chatSessionStore.js` — metadata 유실, localStorage session.
7. `backend/.../service/safety/ingest/*Client.java` — 인증, parser, error swallowing, Safemap opt-in.
8. `SecurityLightOpenApiClient.java` — EPSG:3857 수동 역변환.
9. `PropertySafetyScoreServiceImpl.java` — bbox, Haversine, row counts, caps/weights.
10. 두 scheduler와 `application.properties` — default off, cron, Cloud Run 한계.

## 12. 기술적으로 추가 공부할 주제

- 공공데이터 정정·취소를 포함한 durable source identity와 temporal model.
- staging→completeness validation→publish, run ledger, watermark, retry/backoff/quarantine.
- PostgreSQL `ON CONFLICT`, transaction isolation, bulk load·lock·rollback fault test.
- OpenAPI compatibility, generated DTO, consumer-driven contract test와 schema versioning.
- timeout budget, deadline propagation, cancellation, circuit breaker와 structured fallback.
- EPSG:3857/WGS84, Haversine error, PostGIS `ST_DWithin`·GiST 비교.
- batch on Cloud Run: Cloud Scheduler/Run Job, advisory lock, idempotent job design.
- proxy metric calibration, missing-source bias, freshness와 explainability.
- AI RAG 평가 set, retrieval precision/recall, citation validity, model/version provenance.

## 13. 핵심 사례별 압박 질문

### 거래

1. 267이 행정구역 전체 수가 아니라 조회 code 수라는 차이는 무엇인가?
2. 왜 source_transaction_key가 자연키가 아니며 실제 false merge를 어떻게 측정할 것인가?
3. 가격 정정이 들어오면 왜 conflict update가 아니라 새 row가 될 수 있는가?
4. HTTP 200 오류 XML과 valid data 성공을 어떻게 구분할 것인가?
5. page 3 실패 뒤 page 1~2가 publish되는 것을 어떻게 막을 것인가?
6. 현재 DB에 몇 행이 있고 rollback은 검증했는가?

### 계약

1. `sessionId`가 있는데 왜 `recentMessages=[]`인가?
2. actual FastAPI JSON을 Spring이 읽는 test가 왜 없는가?
3. `workersCalled` 유실이 실제 장애였다는 증거가 있는가?
4. outer 10초와 inner 5초×3·LLM 20초를 어떻게 재설계할 것인가?
5. OpenAPI가 자동 생성되는데 왜 consumer drift를 못 잡았는가?
6. fallback 200과 transport 502의 사용자 의미는 어떻게 통일할 것인가?

### 안전시설

1. 네 provider가 아니라 네 시설 유형이라고 해야 하는 이유는 무엇인가?
2. Web Mercator와 Haversine의 지구 반지름이 다른 이유는 무엇인가?
3. CCTV 10은 camera 10대인가 row 10건인가?
4. HTTP 200 error body와 blank URL이 왜 성공 0건처럼 보일 수 있는가?
5. 시설 row 저장과 score stat 저장의 transaction 경계가 왜 다른가?
6. police opt-in 없이 네 source 성공을 어떻게 주장할 수 있는가?

## 14. 면접에서 인정해야 하는 한계

- 대규모 거래 artifact는 Git 비추적이며 GitHub만으로는 재현할 수 없다.
- 세종 누락 경위, reject 상세 원인, fingerprint false merge 비율은 모른다.
- 당시·현재 Supabase table row, 적재 subset, rollback 결과를 확인하지 못했다.
- 선택 매물 서비스의 실제 HTTP consumer test와 배포 smoke가 없다.
- `workersCalled`/`intent` drift는 해결되지 않았고 실제 사용자 영향은 모른다.
- 안전 source별 post-fix HTTP status·row·시각, Safemap 실행 여부를 모른다.
- 시설 접근성 가중치는 개인 heuristic이고 범죄 안전도 검증이 없다.
- 테스트는 Codex 생성 답변이 있어 직접 설계·작성 성과로 주장하지 않는다.
- 발표 점수·시연 성공 범위·사용자 피드백·사람 review는 확인되지 않았다.

## 15. 면접 전 최종 체크리스트

- [ ] “전국” 대신 “세종 제외 16개 시·도·267 `LAWD_CD` 조회 코드”라고 말한다.
- [ ] 이력서에서는 `8 source`, `약 261만 row`만 먼저 말한다.
- [ ] 25,632/321/25,953의 단위를 tuple/page/XML로 구분한다.
- [ ] 132,228을 실제 중복 거래 수라고 하지 않는다.
- [ ] key를 자연키가 아닌 fingerprint라고 부른다.
- [ ] upsert와 전체 멱등성·exactly-once를 구분한다.
- [ ] Supabase 과거 직접 확인과 현재 DB 미확인을 분리한다.
- [ ] 선택 매물 코드 path와 E2E 검증을 구분한다.
- [ ] `workersCalled`와 `intent`를 해결했다고 말하지 않는다.
- [ ] localStorage session을 server memory라고 하지 않는다.
- [ ] 네 시설 유형 adapter와 네 source 운영 성공을 구분한다.
- [ ] Haversine을 구면 근사라고 말한다.
- [ ] CCTV count가 source row 기준임을 말한다.
- [ ] 시설 접근성 proxy를 범죄 안전 점수라고 하지 않는다.
- [ ] Codex 생성 테스트를 직접 설계·작성했다고 하지 않는다.
- [ ] JWT·Supervisor·최종 UI를 팀원 기여로 분리한다.
- [ ] `12-confirmation-questions.md`를 공유·stage하기 전에 secret을 redaction하고 key를 회전한다.
