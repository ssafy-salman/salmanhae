# 최종 포트폴리오 근거 색인

## 1. 검증 기준

- **A — 코드·Git 확인:** 현재 코드, diff, commit, PR·Issue·Actions로 직접 확인.
- **L — 로컬 산출물 확인:** 사용자가 추가한 비추적 실행 폴더의 manifest·raw·JSONL을 직접 집계해 확인. Git 불변 이력은 아님.
- **U — 사용자 직접 답변:** 역할 배정, 이전 저장소, 배포 당시 행동처럼 저장소 밖 사실. 코드·Git과 충돌하지 않는 범위에서 사용.
- **B — 공동 결과:** 개인 구현과 팀원 구현이 이어진 최종 제품·UI·AI 흐름.
- **X — 충돌 또는 미확인:** 기억과 산출물이 다르거나 확인 자료가 없어 최종 성과 문장에서 제외.

우선순위는 코드·Git → 실행 산출물 → 사용자 직접 답변 → 기존 분석 문서다. `12-confirmation-questions.md`에 포함된 인증값은 근거로 인용하지 않았으며 최종 문서에도 복사하지 않았다.

## 2. 사용자 답변 검증 결과

| 질문 | 사용자 답변 요지 | 대조 결과 | 판정 | 최종 사용 방식 |
|---|---|---|---|---|
| 역할 | 레이어 전담 없이 기능을 선택했고 F-1·F-3·F-4 및 FE/BE/DB를 구현 | F-1 데이터·지도, F-3 법률 RAG, F-4 분석·안전의 사용자 commit/PR이 일치. 다만 팀원도 JWT·Supervisor·최종 UI 등 FE/BE/AI를 구현 | A+U, 일부 충돌 | “F-1·F-3·F-4의 Spring/FastAPI/Vue/DB 핵심 구현”으로 축소. “FE/BE/DB 전체 단독 구축” 금지 |
| 기간 | 2~3월 선행 작업, 5월부터 최종 기획, GitLab 이력 소실 | 발표자료는 2026.05~06, 현재 Git은 2026.06.12~26. 2~3월 작업과 이력 소실 원인은 저장소로 검증 불가 | A+U | “최종 MVP 2026.05~06, Git 검증 06.12~26”; 이전 작업은 사용자 진술로만 구분 |
| 거래 pipeline | 1년 전국 8종을 실행하고 약 8천 매물을 추가 | 추가 폴더는 12개 월 파티션·8 source를 확인. 그러나 16개 시·도·267개 `LAWD_CD` 조회 코드로 세종이 없고, lite 매물은 4,000건 | L, 숫자 충돌 | “2025-07~2026-06, 세종 제외 16개 시·도, 거래 2,612,697건”; 전국 전체·매물 8천 금지 |
| Supabase 거래 적재 | 당시 Supabase에 적재, rollback 자료 없음 | load/upsert 코드와 PR 실행 보고는 일치. `.env` 연결 변수는 존재하지만 현재 읽기 전용 접속은 timeout | A+U, 현재 미확인 | 역사적 적재는 사용자 직접 확인으로 표기. 현재 row·rollback 검증 금지 |
| 안전 API 운영 | Supabase 적재를 직접 확인 | 어떤 안전시설 row를 봤는지는 직접 답변으로만 확인. source별 HTTP 상태·건수·시각은 없고, 제시 명령에는 경찰 opt-in이 없다. 보안등 URL·key, 비상벨 base URL, percent-encoded 공공데이터 key도 현재 코드 계약과 충돌 가능. 현재 DB 접속도 실패 | U, 설정 충돌·범위 미확인 | “당시 일부 적재를 확인”까지만 사용. 4종 모두 성공·401 완전 해결 금지 |
| 문제 발견·테스트 | 배포 후 직접 확인, 테스트 코드는 Codex가 자동 작성 | Issue #90/#92/#94 작성·수정 주체는 사용자. CCTV 403 환경은 불명, 401만 Cloud Run 명시. Git은 사용자 계정의 테스트 commit·후속 수정을 보여주지만 Codex 답변의 대상 파일·사람 검토 범위는 특정하지 않음 | A+U | 배포 후 발견은 사용자 답변. 테스트 저작은 Q6 관련 범위에서도 대상 미특정으로 두고 pipeline·chat·legal 전체로 확대 금지 |
| 선택 매물 smoke·metadata 영향 | 잘 모름 | 정적 DTO drift는 확인했지만 실제 demo 영향과 배포 smoke 결과는 미확인 | X | `workersCalled`/`intent`의 정적 매핑 결과와 가능한 영향만 설명 |
| 법률 데이터 | Supabase에 남아 있을 것으로 예상 | 예상일 뿐이며 현재 DB 접속 실패. 법령 파일·row·model 불명 | X | ingestion/retrieval 코드 구현만 사용 |
| 법률 품질 | 사람 평가는 없고 평가했다면 AI | 사람 평가·정확도 지표 없음. AI 평가 결과도 확인 자료 없음 | X | prompt/card 구조 검증만 사용, 정확도·환각 방지 금지 |
| 안전 가중치 | 적절해 보여 직접 정했으며 수학적 계산은 없음 | 코드 상수와 사용자 author가 일치 | A+U | “개인이 정한 MVP 휴리스틱, 미보정”으로 명시 |
| scheduler 운영 | Cloud Run 단일 instance로 짧은 cron을 켠 뒤 로그 확인 후 비활성화 | 코드 기본은 off·월 1일 03:00/03:30, 저장소 배포 설정은 min 0/max 3. 사용자 명령 한 조각은 min/max 1·CPU throttling 해제, cron은 2분마다 초 0/30이고 다른 일회성 조각은 CPU 옵션을 생략. 실제 적용 로그는 미제공 | U, 일부 충돌 | “일회성 실행을 위해 일시 활성화했다고 답함”으로 한정. 초 30 offset은 수집 완료 뒤 30초를 보장하지 않으며 정기 운영·정확히 1회 성공 금지 |
| 리뷰 | CodeRabbit이 리뷰 전담 | GitHub review 객체가 CodeRabbit 중심이고 사람 review는 확인되지 않음 | A+U | 자동 리뷰와 후속 commit 반영으로 표현. 사람 코드 리뷰로 바꾸지 않음 |

## 3. 새 거래 실행 산출물의 숫자

검증 대상은 Git에 추적되지 않은 `salmanhae-f1-molit-pipeline-20260624/`다. 파일 이름·manifest·20필드 JSONL 구조가 현재 `scripts/data_pipeline/pipeline.py`와 일치한다.

| 숫자 | 의미 | 환경·범위 | 확인 방법 | 주의사항 |
|---:|---|---|---|---|
| 8 | 아파트·오피스텔·연립다세대·단독다가구의 전월세·매매 조합인 거래 source 수 | `SOURCE_CONFIG`와 보존 manifest | 코드 key와 manifest distinct source 대조 | 이력서에 유지 가능. 네 provider가 아니라 8 endpoint/source |
| 267 | 공공 API 조회 입력에 사용한 5자리 `LAWD_CD` 수 | `data/reference/lawd-codes.csv`와 manifest | 기준 파일 행과 manifest distinct prefix 대조 | 행정구역의 완전한 전국 집합이 아니며 세종 `36110` 누락 이유는 미확인 |
| 12 | `dealYmd=202507..202606`의 월 파티션 수 | 보존 manifest | distinct `dealYmd` 대조 | “완결된 최근 1년”보다 “12개 월 파티션”이 정확. 재호출 시 정정 신고로 결과가 달라질 수 있음 |
| 25,632 | 고유 기본 요청 tuple 수 | 8 source × 267개 `LAWD_CD` 조회 코드 × 12개 월 파티션 | manifest의 `source·region·month` 조합을 중복 제거해 `8×267×12`와 대조 | page 단위 요청 수가 아니라 각 조건의 첫 page 기준 tuple 수 |
| 321 | pagination으로 추가된 page 수 | 302개 기본 tuple에서 page 2 이상 발생, 최대 page 4 | manifest에서 page 2 이상인 항목 집계 | 독립된 지역·월 조회나 paginated 그룹 수가 아니라 후속 page occurrence 수 |
| 25,953 | raw XML page 수 | 위 25,632개 그룹의 첫 page + 후속 321 page | manifest 행 수와 raw file 수 대조; 그룹마다 page 연속성·파일명과 XML `pageNo`·item 합과 `totalCount`를 전수 대조 | HTTP 재시도 횟수나 실제 네트워크 호출 횟수는 기록되지 않음 |
| 25,953 | `resultCode=000`, `resultMsg=OK`인 XML 수 | 위 raw 전체 | 모든 XML의 tag 전수 검색 | 현재 pipeline code는 future run에서 result code를 checkpoint로 검사하지 않음 |
| 2,751,295 | raw XML의 거래 item 합계 | 위 25,953개 응답 전체 | 요청 그룹별 XML item 수 합계와 응답 `totalCount` 대조 | 정규화 전 원시 항목 수이며 유효·고유 거래 수가 아님 |
| 2,612,697 | `normalize_row`를 통과하고 `(source_api, source_transaction_key)`로 dedupe된 unique JSONL 행 수 | 12개 월 파티션, 267개 조회 코드, 16개 시·도 | `normalized/transaction_history.jsonl` 전체 streaming 집계와 current normalizer replay | 세종이 없어 “전국 전체” 금지; 현재 DB row가 아님 |
| 138,598 | 원시 item과 unique 정규화 row의 차이 | 동일 보존 raw를 HEAD `pipeline.py`로 사후 재처리 | `6,370` normalizer reject + 동일 fingerprint 두 번째 이후 occurrence `132,228` = `138,598` | 원래 run counter가 아니라 사후 replay. 132,228은 실제 중복 거래 수가 아니며 reject 세부 원인은 미분리 |
| 45,447 | 전체 지역 통계 산출물 행 수 | 위 정규화 결과에서 파생 | `generated/region_price_stat.jsonl` 행 수 | DB 적재 건수 아님 |
| 301,603 | 전체 건물 통계 산출물 행 수 | 위 정규화 결과에서 파생 | `generated/building_price_stat.jsonl` 행 수 | DB 적재 건수 아님 |
| 19,386 | lite 거래 행 수 | 무료 요금제용 선택 subset | `lite/transaction_history.jsonl` 행 수 | 전체 261만 건과 다른 적재 후보 subset |
| 15,482 | lite 지역 통계 행 수 | lite 매물에 필요한 지역 + 광역 통계 | `lite/region_price_stat.jsonl` 행 수 | 전체 통계와 구분 |
| 5,512 | lite 건물 통계 행 수 | 선택 anchor | `lite/building_price_stat.jsonl` 행 수 | 전체 통계와 구분 |
| 4,000 | lite `MVP_SYNTHETIC` 매물 행 수 | 16개 시·도에 균형 선택 | `lite/properties.jsonl` 행 수와 loader 기본값 | 사용자 기억의 8,000과 충돌; 현재 DB count 미확인 |
| 7 | 초기 full 생성 경로의 합성 매물 행 수 | `generated/properties.jsonl` 중간 snapshot | 해당 파일 행 수 | 정확한 실행 경위 미확인. 성과 문장에서 삭제하고 evidence/risk 문서에만 보존 |
| 0 | `errors.json` 기록 오류 수 | 해당 실행 폴더 | JSON 직접 확인 | 모든 후속 처리·적재 성공을 보장하지 않음 |

### 정규화 거래 source별 행 수

| source | 행 수 |
|---|---:|
| `MOLIT_APT_RENT` | 945,484 |
| `MOLIT_APT_SALE` | 506,866 |
| `MOLIT_MULTI_FAMILY_RENT` | 483,128 |
| `MOLIT_MULTI_FAMILY_SALE` | 40,024 |
| `MOLIT_OFFICETEL_RENT` | 270,637 |
| `MOLIT_OFFICETEL_SALE` | 37,822 |
| `MOLIT_VILLA_RENT` | 236,787 |
| `MOLIT_VILLA_SALE` | 91,949 |
| **합계** | **2,612,697** |

### 그 밖에 최종 문서에서 사용하는 수치

| 수치 | 의미·환경 | 확인 방법 | 제한 |
|---:|---|---|---|
| 2명 | 최종 MVP 팀 인원 | 발표자료·사용자 직접 답변·주요 Git author 대조 | 기능 전체를 50:50으로 나눴다는 뜻은 아님 |
| 2026.05~06 / 2026.06.12~26 | 각각 최종 기획·개발 표기 기간 / 현재 Git으로 직접 검증되는 commit 기간 | 발표자료·사용자 답변 / `git log --all` 최초·마지막 commit | 2~3월 선행 작업과 GitLab 이력 소실은 사용자 답변만 존재 |
| 20개 | `transaction_history` insert row의 현재 canonical field 수 | `normalize_row`, `TRANSACTION_COLUMNS`, JSONL key 대조 | 사전에 최적화한 성과 수치가 아님. alias 17 semantic slot 외에 config·manifest·계산 필드가 합쳐진 결과이며 `road_address` alias는 출력에 쓰이지 않음 |
| 8,121건 / 300건 | Git에 남은 초기 거래 seed / 초기 합성 매물 | 커밋된 과거 JSONL·SQL 산출물 행 수 | 2026년 5~6월·5개 지역·4 source의 별도 초기 표본; 대규모 보존 폴더나 현재 DB와 합산 금지 |
| 4,292 / 1,745 / 1,786 / 298 | 초기 8,121건의 아파트 전월세 / 오피스텔 전월세 / 아파트 매매 / 오피스텔 매매 행 수 | 초기 seed의 `source_api` 전수 집계 | 새 8-source 보존 실행의 source별 수치와 구분 |
| 2초·10초 / 5초 / 20초 | Spring→FastAPI connect·read / FastAPI→Spring 호출당 / LLM client의 코드 기본 timeout | 설정 class와 client 생성 코드 대조 | 실제 배포 환경변수·관측 latency가 아니며 순차 호출 때문에 전체 budget이 역전될 수 있음 |
| 100개 / 501m / 300m·500m | 안전 계산의 매물 chunk / 최대 500m+1m margin 후보 bounds / 세 시설·`POLICE` row 최종 반경 | `PropertySafetyScoreServiceImpl.java` 상수와 계산 순서 | 100개 chunk·1m margin의 benchmark 근거는 없고 501m는 최종 점수 반경이 아님 |
| 6,371,000m | Haversine 계산에 사용한 지구 반지름 상수 | 같은 service의 거리 함수 | 구면 근사 상수이며 측정 성과가 아님 |
| 10·3·20·1 / 30·25·25·20 / 0~100 | CCTV·비상벨·보안등·`POLICE` source row cap / 시설별 최대 기여점 / 최종 clamp 범위 | 점수 계산 상수·수식·테스트 대조 | 카메라 대수나 고유 설치지점 수로 별도 검증하지 않은 source row 수. 개인이 정한 미보정 MVP 휴리스틱이며 범죄 확률·치안 등급이 아님 |
| 800자 / 120자 / 1536차원 / top-k 3 | 법률 chunk 크기 / overlap / DB vector 차원 / 기본 검색·근거 카드 상한 | ingestion CLI, migration, retriever·node 기본값 | 실제 법령 row·embedding model·검색 품질은 미확인 |
| Spring 16회 / FastAPI 9회 / GitLab sync 8회 | 이전 분석 시점의 성공 GitHub Actions run snapshot | workflow별 run 목록을 `success`로 필터해 집계 | 시간이 지나면 바뀌며 E2E 성공률·무중단 배포 횟수가 아님. 최종 이력서 수치에서는 제거 |

## 4. 최종 주장–근거 매핑

| 최종 문장 또는 주장 | 사용 문서 | 등급 | 관련 커밋 | PR | Issue | 코드·산출물 | 사용자 직접 확인 | 면접에서 설명할 위치 | 주의사항 |
|---|---|---:|---|---|---|---|---|---|---|
| `[CLM-01]` 실거래 기반 합성 매물·시설 접근성·임대차 법령 검색을 지도와 자연어 질문으로 연결한 2인 팀 MVP다. | 14~20 | A+B+U | `870fe41` 이후 기능 commit | #8~#95 | #7~#94 | `MapExplorer.vue`, `Chatbot.vue`, PRD와 발표자료 | 2인 팀·제품 목적 | 제품 범위와 합성 데이터 경계 | 실제 중개 매물, 검증된 치안·법률 판단 서비스로 표현 금지 |
| `[CLM-02]` 기능 단위 분담에서 F-1·F-3·F-4의 초기 vertical code path를 여러 레이어에 걸쳐 구현했다. | 14~20 | A+U | `870fe41`, `7de5ebe`, `45c393b`, `d4144bd` 등 | #8, #17~#50, #69~#95 | 관련 Issue | 사용자 author diff·PR | 레이어 전담 없는 기능 배정 | 본인/팀원 commit 경계 | 전체 FE/BE/DB 또는 제품 단독 구축 금지 |
| `[CLM-03]` 8개 거래 source를 공통 모델로 정규화하고 세종 제외 보존 실행에서 2,612,697 unique row를 확인했다. | 14~20 | A+L | `79ae977`~`4a1a6fe` | #33 | #32 | `pipeline.py`, 추가 폴더 manifest/raw/normalized | 해당 폴더가 당시 실행 결과 | artifact 범위와 현재 DB의 차이 | Git 비추적 산출물이며 현재 DB row가 아님 |
| `[CLM-04]` 결정적 fingerprint와 conflict upsert로 동일 fingerprint 재입력의 단순 중복 insert를 줄였다. | 14~20 | A | `d448e31`, `79ae977`, `4a1a6fe` | #8, #33 | #7, #32 | `pipeline.py`, migration | — | fingerprint 입력과 DB conflict 경계 | 자연키·정정/취소·false merge/split·exactly-once·전체 멱등성 보장 금지 |
| `[CLM-05]` psycopg 기반 네 테이블 적재 경로를 구현했고 당시 Supabase 적재를 확인했으나 subset과 현재 row 수는 미확인이다. | 14~20 | A+U | `4a1a6fe` | #33 | #32 | `pipeline.py::load_supabase` | 역사적 적재 확인 | 한 connection·commit 경계 | migration/verify는 별도이고 rollback fault test·실행별 insert/update 수 없음 |
| `[CLM-06]` 선택 매물 ID를 Frontend→Spring→FastAPI로 전달하고 초기 analysis card 코드 경로를 구현했다. | 14~20 | A+B | `45c393b`~`8a6c5de` | #37~#50 | #36~#49 | `ChatRequest.java`, `AiAgentClient.java`, `schemas.py`, `spring_client.py`, `chat-normalizer.js` | — | JWT/Supervisor/최종 UI는 팀원 | 실제 `AiAgentClient` HTTP consumer test와 배포 E2E smoke 없음 |
| `[CLM-07]` worker metadata 유실과 nullable `intent` 불일치는 현재 정적 계약 부채이며 해결되지 않았다. | 14~20 | A | `d9c0e03`, current HEAD | #63 | #51 | `schemas.py`, `AiAgentClient.java`, `ChatResponse.java`, `chat-normalizer.js` | 실제 UX 영향은 모름 | 현재 기본 converter의 정적 매핑 결과 | 카드 type drift·전체 HTTP 성공과 실제 사용자 영향은 미확인 |
| `[CLM-08]` localStorage 세션 UX는 있으나 agent 요청의 `recentMessages`는 빈 배열이다. | 14~20 | A+B | `dedb3d6`, `439e49a`, current HEAD | #83, #87 등 | 관련 Issue | `chatSessionStore.js`, `AiAgentClient.java` | — | 최종 세션 UI는 팀원 | 서버 측 multi-turn memory로 표현 금지 |
| `[CLM-09]` 법률 RAG와 선택 매물 가격·안전 worker·초기 card 연동을 구현했고 Supervisor와 최종 UI는 팀원 기여다. | 14~20 | A+B | `c311ffb`~`8a6c5de`; 팀원 `d9c0e03` 이후 | #17~#50; 팀원 #63/#80 이후 | #16~#49 등 | `ingest_legal_docs.py`, `legal_rag.py`, `spring_client.py` | 기능 배정 | 개인 worker와 팀원 Supervisor 경계 | AI 전체, Supervisor, JWT core, 최종 UI 단독 기여 금지 |
| `[CLM-10]` 네 시설 유형 adapter와 보안등 좌표 fallback의 Web Mercator 수동 역변환·Haversine 구면 근사 사전 계산을 구현했다. | 14~20 | A | `ea8bcbe`~`cad48d2` | #73/#77/#91/#93 | #72/#76/#90/#92 | `service/safety/ingest`, `PropertySafetyScoreServiceImpl.java` | 일부 배포 row 확인 | 네 source 운영 성공과 다름 | 한국 영역 sanity check·live CRS 검증이 없고 concrete client 오류 축소·Safemap 세부 유형 미필터링 한계 |
| `[CLM-11]` 안전 값은 개인이 정한 30/25/25/20 미보정 휴리스틱 기반 시설 접근성 proxy다. | 14~20 | A+U | `0bee1d6`, `a48138b` | #77 | #76 | `PropertySafetyScoreServiceImpl.java` | 수학 계산 없이 직접 결정 | source row count 기반 | 카메라 대수·고유 설치지점 수·범죄 확률·절대 치안·검증된 안전 등급으로 표현 금지 |
| `[CLM-12]` scheduler는 기본 off이고 일회성 실행을 위해 일시 활성화했다고 답했으나 source별 운영 성공은 미확인이다. | 14~20 | A+U | scheduler 관련 commit | #75, #77 | #74, #76 | scheduler classes·환경변수 이름 | 실행 명령·비활성화 절차 | default off와 일회성 실행 범위 | 실제 log·횟수·source별 성공 없음; 제시 설정 일부는 현재 계약과 충돌 가능 |
| `[CLM-13]` 사용자 답변은 관련 테스트의 Codex 생성을 말하고, Git은 별도로 사용자 test commit·PR 실행·자동 리뷰 후속 diff를 보여준다. | 14~20 | A+U | 테스트·후속 수정 commit | #50, #69~#95 | 관련 Issue | 각 module test, GitHub review | Codex 생성이라고 답함 | 두 근거의 정확한 파일·case 연결과 사람 설계/검토 범위 미확인 | 특정 PR 통합·직접 TDD 설계·작성 성과로 표현 금지 |
| `[CLM-14]` 2026-07-14 현재 Spring 77·Frontend 26·FastAPI 61 module test가 통과했다. | 14~20 | A | current HEAD | — | — | `backend/src/test`, `backend-ai/tests`, `frontend/src/**/*.test.mjs` | — | 같은 날 로컬 재실행 | HTTP consumer·live external API·DB·E2E 검증은 포함하지 않음 |
| `[CLM-15]` Spring·FastAPI Cloud Run 배포와 GitLab sync workflow를 구성했다. | 14~20 | A | `f6f6462` 등 workflow commit | #52 등 | #51 등 | `.github/workflows` | — | path별 workflow 구성 | 성공 run 횟수·무중단·E2E·test gate 성과로 확대 금지 |
| `[CLM-16]` CodeRabbit 지적을 후속 commit으로 반영했고 초기 계약·rendering 뒤 팀원이 최종 UI를 고도화했다. | 14~20 | A+B+U | `6cb0c85`, `537f9ab`; 팀원 `e4ba51a`, `dedb3d6`, `439e49a` | 다수 | — | GitHub review·follow-up diff·UI diff | CodeRabbit 중심 리뷰 | 사람 review·회의·발표 결과는 별도 사용자 답변 | 공동/팀 결과를 개인 성과로 사용 금지 |

## 5. 개인·공동·팀 전체 기여

### 개인 기여로 사용

- F-1의 거래 pipeline·DB migration·지도 API·초기 Vue 연동·검색 조건 정합성.
- F-3의 법률 ingestion·embedding client·pgvector retrieval·prompt-level grounding·초기 legal card.
- F-4의 선택 매물 Spring–FastAPI 계약, 가격·안전 read API, 네 안전시설 adapter, 보안등 좌표 fallback 변환, 시설 접근성 계산.
- 모노레포 전환, Spring/FastAPI Cloud Run workflow, GitLab sync와 CodeRabbit 후속 수정.
- 사용자 답변상 관련 테스트의 Codex 생성 사실과, Git에서 별도로 확인한 사용자 test commit·PR 실행·자동 리뷰 후속 diff. 두 근거의 정확한 파일·case 연결과 사람 설계·검토 범위가 없어 특정 PR 통합이나 직접 설계·작성 성과로는 사용하지 않음.

### 공동 기여로 표현

- 팀원의 JWT core 위에 연결한 인증 채팅 경로.
- 팀원의 Supervisor가 개인 구현 RAG·analysis worker를 호출하는 현재 AI 흐름.
- 개인의 초기 지도·카드 연결과 팀원의 최종 UI·세션 UX가 합쳐진 화면.
- 배포 환경에서 여러 모듈이 합쳐진 최종 서비스.

### 팀 전체 결과로만 사용

- 최종 발표·시연 산출물.
- Supervisor 평가 산출물은 팀 전체 결과로만 다루며 개인 성과 수치로 사용하지 않는다.
- JWT·chat·Supervisor·지도·RAG·안전·UI가 결합된 제품 전체.

## 6. 여전히 사용하지 않는 주장

- 세종을 포함한 전국 전체 수집.
- 합성 매물 8,000건 적재 또는 현재 Supabase row 수.
- 동일 seed 재적재 후 row 불변과 fault-injection rollback 성공.
- 네 안전 API의 source별 200·건수·시각, 경찰 source 활성화, 401 완전 해결. 특히 제시 명령에는 경찰 opt-in이 없고 보안등·비상벨·key 전달 일부가 현재 코드 계약과 맞지 않을 수 있다.
- 선택 매물 채팅의 배포 후 smoke 성공과 `workersCalled`의 실제 사용자 영향.
- 운영 법률 row·embedding provider/model·법률 답변 정확도·사람 평가.
- scheduler가 정확히 한 번만 실행됐거나 정기 운영됐다는 주장.
- 발표 점수·수상·심사 의견·사용자 수·사용자 만족도·성능 향상률.

## 7. 보안 주의

실제 값은 이 문서와 완료 보고에 출력하지 않는다.

| 의심 파일 | 값의 종류 | Git 상태 | 조치 |
|---|---|---|---|
| 저장소 루트 `.env` | DB 연결·계정, JWT, 내부 서비스 key, SMTP, Redis 연결 비밀값 | 현재 untracked·`.gitignore` 적용, 전체 Git history에서 추적 이력 없음 | 로컬 보관 권한을 제한하고 공유하지 않는다. 이미 공유됐거나 노출 가능성이 있으면 관련 비밀값을 회전한다 |
| `portfolio-analysis/12-confirmation-questions.md` | 공공데이터·Safemap 인증 key로 보이는 평문 값 | 현재 untracked이나 ignore되지 않음, 전체 Git history에서 추적 이력 없음 | 공유본에서 즉시 redaction/삭제하고 공급기관 key를 회전한다. `git add -A` 전에 반드시 제외한다 |
| `portfolio-analysis.zip` | 이전 시점의 분석 문서 묶음 | untracked. 포함된 이전 `12`를 패턴 검사했을 때 같은 인증값은 발견하지 못함 | 현재 분석 폴더를 다시 압축해 공유하려면 먼저 `12`를 redaction한다 |

추적 중인 `.env.example`, test 설정, 배포 가이드의 탐지 값은 placeholder·test 값·환경변수 참조로 확인돼 회전 대상에서 제외했다. 자동 삭제나 인증값 회전은 수행하지 않았다.

## 8. 이번 검수의 테스트 실행 상태

- Spring: 2026-07-14 현재 `mvnw test`를 재실행해 **77 tests, failure/error 0**을 확인했다. 이는 현재 Spring module test 결과이며 서비스 간 E2E가 아니다.
- Frontend: 잠긴 의존성을 임시 설치한 뒤 현재 HEAD에서 **26 tests, failure 0**을 확인했다. 테스트 후 `node_modules`와 workspace cache는 삭제했다.
- FastAPI: 임시 Python 3.12 가상환경에서 현재 HEAD를 설치해 **61 tests, failure 0**을 확인했다. Starlette TestClient deprecation warning 1건이 있었고 임시 환경은 삭제했다.
- 테스트 저작: 사용자 직접 답변상 관련 테스트 코드는 Codex가 생성했다. 정확한 파일·사람의 test-case 설계·검토 범위가 미확인이므로 “TDD로 직접 설계·작성했다”는 주장에는 사용하지 않는다.
