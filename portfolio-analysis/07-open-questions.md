# 추가 확인 질문

## 사용 방법

아래 질문은 저장소 근거만으로 확정할 수 없는 항목이다. 포트폴리오 제출 전 본인의 기억, 팀원 확인, 운영 console, 발표 결과 자료로 보충한다. 답을 얻기 전에는 임의 수치나 성공 표현을 넣지 않는다.

## 1. 최우선 확인

| 우선순위 | 질문 | 왜 확인해야 하는가 | 확인할 곳 | 답을 얻으면 바뀌는 문서 |
|---:|---|---|---|---|
| 1 | 김용휘의 공식 역할명과 팀 내 역할 분담 문구는 무엇이었나? | Git은 기능 소유를 보여 주지만 “backend lead”, “AI/backend” 같은 공식 명칭은 없음 | 팀 노션·발표 script·팀원 이다인 | 프로젝트 개요, 이력서 역할 |
| 2 | 정확한 시작일·종료일은 언제인가? | 발표자료는 `2026.05~06`, Git은 `06.12~06.26`만 확인 | WBS 원본·SSAFY 일정·개인 calendar | 개발 기간 |
| 3 | 모노레포 이전 frontend/backend/backend-ai repository URL과 history가 남아 있는가? | 현재 `a259751`은 working tree만 가져와 이전 개인별 기여를 보존하지 않음 | GitHub/GitLab 개인·조직 repository | 초기 기여·개발 기간·timeline |
| 4 | 운영 Supabase에 적용된 migration과 현재 table row 수는? | code가 있어도 `users` migration이 없고 pipeline 실제 load 상태가 불명확 | Supabase migration history·SQL count | 구현 범위·성과·배포 신뢰도 |
| 5 | 최신 Vercel·Cloud Run URL에서 회원가입→지도→chat smoke test가 현재 성공하는가? | deployment success와 실제 user flow 정상은 다름 | Vercel/Cloud Run console·browser smoke test | 실제 배포 여부·성과 |
| 6 | FastAPI `workersCalled`와 Spring/frontend `intent` 불일치는 최종 demo에서 어떤 증상을 냈는가? | current code에서 field 소실이 확인되며 portfolio 핵심 한계 | 당시 demo 영상·network log·팀 기억 | AI 기능 현재 상태·개선 story |
| 7 | 최종 발표 결과, 점수, 수상·심사 feedback이 있었나? | 저장소에는 객관적 발표 성과가 없음 | SSAFY 결과 공지·feedback sheet | 결과 및 성과 |
| 8 | 실제 사용자 또는 동료 test를 몇 명이 했고 어떤 feedback이 있었나? | 사용자 반응을 만들지 않기 위해 필요 | survey·test note·chat·발표 rehearsal | 사용자 성과·UX 개선 근거 |

## 2. 본인 기여 경계

| 질문 | 왜 필요한가 |
|---|---|
| 초기 PRD·architecture·ERD에서 김용휘가 직접 설계한 부분은 어디까지인가? | 최종 artifact는 공동 산출물이며 commit author만으로 회의 기여를 판단할 수 없음 |
| `a259751` 모노레포 import 전에 각 module은 누가 작성했나? | import commit author가 해당 source의 원저자를 뜻하지 않을 수 있음 |
| direct `develop` commit `38199b5`, `02fa47a`, `a130a36`, `02dd5ab`, `ba7c5da`는 어떤 상황에서 PR 없이 반영했나? | demo 직전 작업인지 합의된 hotfix인지 확인해야 collaboration 설명이 정확해짐 |
| PR #101의 기능 head commit은 김용휘인데 merge author가 이다인인 작업은 역할을 어떻게 나눴나? | 구현과 merge 행위를 구분하기 위해 필요 |
| 발표자료에서 김용휘는 RAG·CI/CD만 언급했는데 data·map·safety 역할도 공식 발표에 포함됐나? | Git 근거는 강하지만 공식 역할 소개와 차이가 있을 수 있음 |
| 팀원이 주도한 Supervisor에서 김용휘가 review·설계 의견을 낸 기록이 별도로 있는가? | GitHub에는 사람 review/comment가 없어 본인 협업 기여를 확인할 수 없음 |
| 본인 기여도를 비율로 요청받을 때 팀이 합의한 수치가 있는가? | commit 수를 기여율로 잘못 쓰지 않기 위해 필요 |

## 3. Data·외부 API

| 질문 | 왜 필요한가 | 현재 판정 |
|---|---|---|
| 전국 최근 12개월·8종 pipeline을 실제 끝까지 실행했나? | PR #33은 limited sample와 DB 명령 검증만 명시 | 확인 필요 |
| 전체 실행 시 거래·건물·합성 매물·통계 row 수와 소요 시간은? | 검증 가능한 정량 성과 후보 | 확인 필요 |
| Naver geocoding success/failure/cache hit 비율은? | data coverage와 retry 전략 설명에 필요 | 확인 필요 |
| PR #8의 8,121 거래·300 매물은 어떤 지역·기간 sample인가? | 숫자의 범위를 정확히 설명해야 함 | 확인 필요 |
| data provider 이용약관과 public data attribution은 최종 제출에서 어떻게 처리했나? | 합법성·출처 질문 대비 | 문서 일부 확인, 최종 확인 필요 |
| CCTV·비상벨·보안등은 운영에서 각각 몇 건 적재됐나? | “4종 통합”과 “실제 수집 성공”을 구분 | 확인 필요 |
| Safemap valid key를 결국 발급받아 수집했나? | current code는 default off | 확인 필요 |
| public API schema 변경이나 failure를 monitoring하는 방법이 있었나? | 운영 대응 설명에 필요 | code상 structured metrics/alert 없음 |

## 4. 성능·품질 수치

| 질문 | 왜 필요한가 |
|---|---|
| viewport API의 zoom별 p50/p95 latency와 response item 수는? | “성능 개선”을 수치로 말하려면 필요 |
| heavy region-stat join에서 visible-property aggregate로 바꾼 before/after query plan은? | PR #62의 구조적 안정화 외 실제 효과를 확인 |
| 안전 score batch의 매물 수, 시설 수, duration, memory는? | chunk 100·bounds prefilter의 효과 확인 |
| request-time 계산과 precompute API latency 차이는? | batch 선택의 정량 근거 |
| 법률 RAG retrieval precision 또는 answer correctness 평가는 했나? | Supervisor routing 평가와 RAG answer 품질은 다른 문제 |
| stored Supervisor 38-case 평가를 같은 model·dataset으로 재현할 수 있나? | 결과 JSON은 있으나 이번 조사에서 재실행하지 않음 |
| current HEAD의 Spring·FastAPI·frontend test가 모두 통과하는가? | PR 당시 통과와 current status를 구분 |
| test coverage를 측정한 적이 있는가? | test 함수 수를 coverage로 오해하지 않기 위해 필요 |

수치가 확인되기 전에는 “응답 속도 N% 개선”, “정확도 N%”, “전국 데이터 N만 건”을 포트폴리오에 쓰지 않는다.

## 5. 배포·운영

| 질문 | 왜 필요한가 | 현재 확인 범위 |
|---|---|---|
| Cloud Run 실제 service URL과 현재 health는? | Actions success만으로 live status를 보장하지 않음 | run success만 확인 |
| backend 16회·AI 9회 deploy 중 rollback·failure가 없었나? | `gh run list`에는 success만 보이지만 삭제·외부 장애 여부 불명 | 확인 필요 |
| Vercel production domain을 지금도 사용할 수 있나? | GitHub deployment URL은 immutable build URL일 수 있음 | latest success만 확인 |
| Cloud Run environment variable과 secret이 실제로 모두 설정됐나? | workflow는 env를 merge하지 않고 기존 service 설정에 의존 | 확인 필요 |
| scheduler가 Cloud Run에서 실제 월 1회 실행됐나? | min=0·max=3에서 정시/중복 risk | 확인 필요 |
| duplicate scheduler run을 방지하는 lock이 있었나? | code에는 distributed lock이 없음 | 없음으로 확인됨; 운영 workaround 확인 필요 |
| FastAPI Cloud Run은 public URL+API key였나, IAM private였나? | current guide는 API key 방식, security 설명에 중요 | code는 API key, console 확인 필요 |
| GCP service account JSON key를 폐기했나? | secret hygiene와 현재 보안 상태 | 확인 필요 |

## 6. 기능 구현 상태

| 질문 | 왜 필요한가 | code 판정 |
|---|---|---|
| `users` table은 수동으로 생성했나? SQL이 별도 저장소에 있나? | 운영 migration만으로 auth 재현 불가 | main migration 없음 |
| wishlist를 demo에서 사용했나? | docs는 MVP지만 code 없음 | 계획만 존재 |
| `chatSessionStore`의 localStorage session을 server session으로 소개했나? | 과장 방지 | frontend local only |
| HUG diagnosis 화면은 최종 navigation/demo에 포함됐나? | code에는 prototype이 있으나 MVP 제외와 충돌 | route는 있으나 header nav에는 없음 |
| community·Recommend prototype은 최종 기능인가 초기 mock인가? | route가 남아 있지만 store contract가 맞지 않음 | 잔존 mock 정황 유력 |
| frontend 안전시설 layer를 실제로 표시했나? | safety backend와 AI는 있지만 map layer는 확인되지 않음 | 미구현 |
| `price_score`를 계산한 외부 script나 manual data가 있나? | schema field는 있으나 main source 계산 없음 | 확인 필요 |
| frontend의 `minMonthlyRent/maxMonthlyRent`와 multi transaction filter는 최종 demo에서 정확히 동작했나? | current Spring contract와 drift | 확인 필요 |

## 7. 협업·Git process

| 질문 | 왜 필요한가 |
|---|---|
| README의 “상대방 approve 후 merge”를 실제로 어떻게 수행했나? | GitHub review/approval 객체에는 사람 기록이 없음 |
| branch protection을 사용하지 않은 이유는? | main/develop 모두 unprotected로 확인 |
| final direct commit과 `#0` commit을 허용한 기준은 무엇이었나? | traceability 개선점 설명 |
| PR #1만 parent가 1개인 이유와 실제 merge method는? | 나머지 61개와 병합 방식이 다름 |
| CodeRabbit 지적을 누가 triage했고 false positive를 어떻게 판단했나? | 자동 review 활용 역량을 구체화 |
| GitLab sync 충돌이나 force push가 있었나? | workflow는 normal push이며 conflict 대응 기록 없음 |
| API contract 변경 회의나 합의 문서가 별도로 있는가? | 사람 간 조율 근거를 보강할 수 있음 |

## 8. 발표 전 본인이 기억을 보충할 질문

1. safety API의 403·401을 처음 어디에서 발견했고, 어떤 log가 결정적이었나?
2. service key가 encoding 문제라는 것을 어떤 비교로 확인했나?
3. Web Mercator를 처음 알아챈 실제 좌표 예시는 무엇이었나?
4. SQL Editor chunk limit은 어떤 error message나 size에서 발생했나?
5. duplicate source key는 원천 API 중 어떤 조합에서 생겼나?
6. RAG REST fallback을 만들 때 local network 제약 외 다른 제약이 있었나?
7. 지도 broad zoom 401의 정확한 원인은 인증인가 query/API gateway인가?
8. PR #95 search mismatch를 사용자 test 중 발견했나, code review 중 발견했나?
9. 가장 많은 시간을 쓴 기능과 가장 큰 설계 판단은 무엇이었나?
10. 최종 시연에서 본인이 직접 설명한 화면·기술은 무엇이었나?

이 질문은 저장소에서 답을 만들지 말고, 기억나는 범위만 보충한 뒤 사실·해석을 구분해 기록한다.
