# 본인 확인 질문

아래 질문은 Git·코드만으로 답을 만들 수 없지만, 답에 따라 포트폴리오의 정확성과 설득력이 크게 달라지는 항목만 추렸다. 각 답에는 가능하면 날짜, 환경, 로그·화면·발표자료 위치를 함께 남긴다.

## 1. 공식 역할과 설계 책임 범위

### 질문

팀에서 공식적으로 맡은 역할은 무엇이었고, API·DB·AI·프론트 가운데 본인이 최종 의사결정을 맡은 범위는 어디까지였나요? 제품 요구사항과 가중치 같은 도메인 결정은 누가 승인했나요? `[본인 확인 필요]`

### 사용자 답변

- 1차 MVP로 몇개의 기능을 나눈 다음에 그걸 선택해서 구현했음
- 프론트엔드는 누가 담당, 백엔드는 누가 담당, 이런식은 아니었음
- docs/01_PRD 에 있는 내용을 보면 F-N으로 이루어져 있음
- F-1, F-3, F-4 이렇게 구현을 맡았던 걸로 기억
- 백엔드, 프론트엔드, 데이터베이스 구축은 내가 함

### 현재 확인된 내용

본인은 Spring, FastAPI, 데이터 파이프라인, 지도 프론트까지 넓은 diff를 작성했다. 저장소는 2인 팀을 가리키지만 공식 역할명과 의사결정권은 기록하지 않는다.

### 확인이 필요한 이유

“백엔드 담당”, “풀스택”, “AI 연동 설계” 중 어떤 소개가 정확한지와 공동 기여 경계를 정한다.

### 답에 따른 문장 예시

- **긍정적으로 확인된 경우**: “2인 팀에서 Spring 백엔드와 서비스 간 API 계약을 주도하고, 데이터·AI 계층은 팀원과 인터페이스를 합의했습니다.”
- **확인되지 않은 경우**: “Spring·데이터·AI 연동의 다수 기능을 구현했습니다.”

## 2. 실제 개발 기간과 저장소 이전 이력

### 질문

실제 개발 시작·종료일은 언제이며, 2026년 6월 12일 첫 Git 커밋 이전에 별도 GitLab·로컬 저장소·기획 기간이 있었나요? `[본인 확인 필요]`

### 사용자 답변
- 일단 대답은 '있었음'.
- 이 프로젝트가 2~3월부터 작은 단위의 요구사항으로 시작되는 프로젝트였음
- 프론트엔드가 주제면 프론트엔드 구현, 백엔드가 주제면 백엔드 구현
- 그런데 최종 구현 기획 단계에서 앞에 있던건 다 엎어버리고 새로 만들어서 실직적으론 5월부터
- 6월 12일이 첫 커밋인 건 깃랩에서 작업하던거를 밀어버리고 깃랩을 깃허브의 아카이브 형식으로 활용하다가 기존 커밋 날아가면서 생긴일
- 그래서 커밋상에서는 6월 12일이 첫 커밋이지만, 기획은 5월 부터 했음

### 현재 확인된 내용

현재 저장소의 확인 가능한 커밋 기간은 2026-06-12~2026-06-26이다. 발표자료에는 5~6월로 표기된 흔적이 있다.

### 확인이 필요한 이유

기간을 임의로 늘리거나 반대로 기획·이전 저장소 작업을 누락하지 않기 위해서다.

### 답에 따른 문장 예시

- **긍정적으로 확인된 경우**: “2026년 5월 기획을 시작해 6월 말 MVP를 완성했습니다. 코드 이력은 6월 12일부터 현재 저장소에 남아 있습니다.”
- **확인되지 않은 경우**: “현재 Git으로 검증되는 개발 기간은 2026년 6월 12~26일입니다.”

## 3. 8 endpoint 파이프라인의 실제 전체 실행 범위

### 질문

`scripts/data_pipeline/pipeline.py`를 실제로 어느 환경에서 어떤 region·month·source 조합으로 끝까지 실행했나요? 8개 endpoint별 요청·정규화 건수, 실행 시간, 실패 건수와 manifest를 보관하고 있나요? `[본인 확인 필요]`

### 사용자 답변
- 최상단에 추가한 'salmanhae-f1-molit-pipeline-20260624' 폴더에 있는 파일이 그것
- 전국의 전체 데이터를 1년간 데이터라고 기억 중
- 그래서 얻어낸 실거래가 데이터를 통해 8000개의 매물 데이터 추가함


### 현재 확인된 내용

코드는 8개 endpoint를 지원한다. 커밋된 8,121건 seed에는 아파트·오피스텔 전월세·매매 네 source만 있다. PR #33에는 APT_RENT 소규모 실행 기록만 있다.

### 확인이 필요한 이유

“8개 endpoint 구현”을 “8개 모두 실수집 검증”으로 올릴 수 있는지 결정한다.

### 답에 따른 문장 예시

- **긍정적으로 확인된 경우**: “8개 endpoint를 모두 실행해 source별 정규화 건수와 실패 manifest를 확인했습니다.”라고 로그와 수치를 함께 쓴다.
- **확인되지 않은 경우**: “8개 endpoint code path를 구현했고, 저장소 결과물로는 네 source 8,121건을 확인했습니다.”

## 4. Supabase 실제 적재와 rollback 검증

### 질문

파이프라인 결과를 실제 Supabase에 적재했나요? 당시와 현재의 네 테이블 row 수, 중복 전후 비교, 재실행 결과, load 중 실패를 발생시킨 rollback 검증 자료가 있나요? `[본인 확인 필요]`

### 사용자 답변
- supabase에 적재했음
- rollback 검증자료는 아마 없을 것 같음


### 현재 확인된 내용

코드는 네 테이블을 한 connection에서 upsert하고 commit한다. PR 본문에는 migrate/load/verify 실행 보고가 있으나 외부 DB snapshot과 장애 주입 결과는 없다.

### 확인이 필요한 이유

transaction 설계를 코드 수준 B에서 실제 검증 A로 높일 수 있는 핵심 증거다.

### 답에 따른 문장 예시

- **긍정적으로 확인된 경우**: “동일 seed 재적재 후 거래 row 수가 증가하지 않았고, 의도적 중간 실패에서 네 테이블 변경이 rollback됨을 확인했습니다.”
- **확인되지 않은 경우**: “한 transaction에서 conflict upsert하도록 구현했으며 실제 rollback 검증은 남아 있지 않습니다.”

## 5. 안전시설 PR #93 이후 운영 API 상태

### 질문

PR #93 배포 뒤 CCTV·비상벨·보안등·경찰관서 각각의 HTTP 상태, 수집 row 수, 실행 시각을 확인했나요? 여전히 비활성화한 source가 있다면 무엇인가요? `[본인 확인 필요]`

### 사용자 답변
- supabase에 적재된 거 확인
- 만약 supabase 확인이 필요하다면 최상단 .env로 직접 접속해봐도 됨

### 현재 확인된 내용

PR #93은 key encoding과 source 설정을 수정했다. 이전 로그의 401은 확인되지만 수정 후 네 source 성공 로그는 저장소에 없다. 경찰관서는 기본 opt-in이다.

### 확인이 필요한 이유

“인증 위험을 코드로 보강”과 “운영 401 해결 완료” 사이의 증거 등급을 결정한다.

### 답에 따른 문장 예시

- **긍정적으로 확인된 경우**: “배포 후 실행에서 CCTV·비상벨은 200과 적재 건수를 확인했고, 경찰관서는 키 미발급으로 비활성화했습니다.”처럼 source별로 쓴다.
- **확인되지 않은 경우**: “401 로그를 바탕으로 key encoding과 선택 실행을 보강했지만 운영 성공 여부는 확인하지 못했습니다.”

## 6. 주요 문제의 최초 발견 과정

### 질문

안전시설 403·401, 지도 필터 불일치, 개발 DB 차단은 각각 누가 어떤 테스트·로그·사용자 행동으로 처음 발견했나요? 재현 절차나 당시 화면을 갖고 있나요? `[본인 확인 필요]`

### 사용자 답변
- 배포 하고 직접 확인함
- 테스트 코드는 코덱스가 자동으로 작성

### 현재 확인된 내용

관련 Issue는 본인 계정으로 작성됐고 본인이 수정했다. 그러나 최초 관찰자가 누구인지와 발견 맥락은 Git만으로 확정되지 않는다.

### 확인이 필요한 이유

문제 발견, 원인 분석, 구현을 모두 혼자 했다고 오인시키지 않으면서 디버깅 과정을 구체화할 수 있다.

### 답에 따른 문장 예시

- **긍정적으로 확인된 경우**: “Cloud Run 수집 로그의 source별 status를 확인하다 CCTV 401을 발견했고 로컬 동일 요청과 URL encoding 차이를 비교했습니다.”
- **확인되지 않은 경우**: “Issue에 기록된 401을 기준으로 인증 전달 경로를 수정했습니다.”

## 7. 선택 매물 채팅의 배포 후 smoke test와 `workersCalled` 영향

### 질문

배포 환경에서 선택 매물 가격·안전 질문을 실제로 끝까지 실행한 기록이 있나요? non-empty `workersCalled`·`toolResults`가 Spring에서 미전달되면서 화면, 로그, analytics, 발표 demo에 어떤 영향이 있었나요? 현재 빈 배열인 `nextActions`는 미래 사용 계획이 있었나요? `[본인 확인 필요]`

### 사용자 답변
- 이 부분은 잘 모르겠음

### 현재 확인된 내용

현재 DTO 대조에서 metadata 유실과 `intent` null은 확인된다. 메시지·카드 공통 필드는 남으므로 전체 채팅 장애라고 단정할 수 없다.

### 확인이 필요한 이유

가장 중요한 계약 부채의 실제 심각도를 정하고, “사고를 발견했다”는 허위 서사를 막는다.

### 답에 따른 문장 예시

- **긍정적으로 확인된 경우**: “같은 요청의 FastAPI 응답·로그에는 `workersCalled: ["PRICE_ANALYSIS"]`가 있었지만 Spring 공개 응답은 `intent: null`이었고, 메시지·카드는 표시됐습니다.”처럼 실제 캡처 범위만 쓴다.
- **확인되지 않은 경우**: “정적 계약 감사에서 metadata가 조용히 유실될 가능성을 확인했으며 실제 사용자 영향은 아직 측정하지 못했습니다.”

## 8. 법률 RAG의 현재 데이터와 embedding 설정

### 질문

실제로 적재한 법령 파일, 법령명·기준일, chunk row 수, 사용 embedding provider/model과 차원은 무엇인가요? 현재 운영 DB에도 남아 있나요? `[본인 확인 필요]`

### 사용자 답변

- supabase에 남아있을 것으로 예상

### 현재 확인된 내용

코드는 임의 법령 JSON을 받아 vector(1536)로 저장한다. 설계 문서는 두 법령을 말하지만 원문 파일과 DB row가 없고 model은 환경변수로만 정해진다.

### 확인이 필요한 이유

법률 RAG를 운영 사례로 쓸 수 있는지, 코드 구현 사례로만 제한해야 하는지 결정한다.

### 답에 따른 문장 예시

- **긍정적으로 확인된 경우**: “2026-06-xx 기준 두 법령 N개 조문을 M개 chunk로 적재했고, 모델 X의 1536차원 embedding을 사용했습니다.”
- **확인되지 않은 경우**: “법령 JSON을 chunk·embedding·upsert하는 경로를 구현했지만 현재 적재 데이터는 확인되지 않습니다.”

## 9. 법률 답변 품질 검증

### 질문

법률 질문 test set, 기대 조문, top-k 적중률, 답변 근거 일치 여부를 사람이 평가한 기록이 있나요? 실제 사용자 또는 지도교사 피드백이 있었나요? `[본인 확인 필요]`

### 사용자 답변
- 사람이 직접 평가하진 않았음
- 평가했다면 에이전트 AI가 수행함

### 현재 확인된 내용

단위 테스트는 prompt와 카드 구조, zero-result 처리를 검증한다. retrieval·답변 품질 지표와 사람 평가는 없다.

### 확인이 필요한 이유

“근거 카드 구현”을 “정확한 법률 답변”으로 확대할 수 있는지 판단한다.

### 답에 따른 문장 예시

- **긍정적으로 확인된 경우**: “대표 질문 N개에서 기대 조문 top-3 포함률 X%를 확인하고 오답 유형을 분류했습니다.”
- **확인되지 않은 경우**: “근거가 prompt와 카드에 들어가는 구조를 검증했으며 답변 정확도 평가는 하지 못했습니다.”

## 10. 안전시설 가중치와 제품 명칭의 결정 근거

### 질문

CCTV 30, 비상벨 25, 보안등 25, 경찰관서 20과 각 cap·반경은 누가 어떤 자료나 사용자 가설로 결정했나요? ‘안전 점수’가 시설 접근성 proxy임을 발표·UI에서 설명했나요? `[본인 확인 필요]`

### 사용자 답변
- 이 정도면 적절하지 않나? 싶어서 작성했음
- 뭔가 수학적으로 계산했던건 아님

### 현재 확인된 내용

수치와 계산식은 코드에 고정돼 있지만 통계 calibration, 전문가 검토, 범죄 데이터는 없다.

### 확인이 필요한 이유

규칙 기반 제품 가설과 검증된 안전 지표를 구분하고 도메인 과장을 방지한다.

### 답에 따른 문장 예시

- **긍정적으로 확인된 경우**: “MVP 우선순위 회의에서 시설 접근성 proxy로 합의한 규칙이며 치안 예측이 아님을 UI에 고지했습니다.”
- **확인되지 않은 경우**: “MVP용 규칙 기반 시설 접근성 지표이며 가중치의 통계적 타당성은 검증하지 못했습니다.”

## 11. scheduler의 실제 운영 방식

### 질문

Cloud Run에서 안전시설 수집과 점수 재계산 scheduler 환경변수를 실제로 켰나요? scale-to-zero, 다중 instance 중복 실행, 실행 실패를 어떻게 관리했나요? 별도 Cloud Scheduler나 수동 실행이 있었나요? `[본인 확인 필요]`

### 사용자 답변
- batch 때 사용한건 아래와 같음

- batch때 사용

```jsx
PROJECT_ID="salmanhae"
REGION="asia-northeast3"
SERVICE="salmanhae-api"

PUBLIC_DATA_SERVICE_KEY=
SAFEMAP_SERVICE_KEY=

EMERGENCY_BELL_URL="https://apis.data.go.kr/1741000/emergency_call_box_info"
SECURITY_LIGHT_URL=

gcloud config set project $PROJECT_ID

gcloud run services update $SERVICE `
  --region $REGION `
  --min-instances 1 `
  --max-instances 1 `
  --no-cpu-throttling `
  --update-env-vars "PUBLIC_DATA_SERVICE_KEY=$PUBLIC_DATA_SERVICE_KEY,SAFEMAP_SERVICE_KEY=$SAFEMAP_SERVICE_KEY,SAFETY_DATA_EMERGENCY_BELL_URL=$EMERGENCY_BELL_URL,SAFETY_DATA_SECURITY_LIGHT_URL=$SECURITY_LIGHT_URL,SAFETY_DATA_PAGE_SIZE=1000,SAFETY_INGESTION_SCHEDULER_ENABLED=true,SAFETY_INGESTION_SCHEDULER_CRON=0 */2 * * * *,SAFETY_INGESTION_SCHEDULER_ZONE=Asia/Seoul,SAFETY_SCORE_SCHEDULER_ENABLED=true,SAFETY_SCORE_SCHEDULER_CRON=30 */2 * * * *,SAFETY_SCORE_SCHEDULER_ZONE=Asia/Seoul"
  
  
$PROJECT_ID = "salmanhae"
$REGION = "asia-northeast3"
$SERVICE = "salmanhae-api"

$PUBLIC_DATA_SERVICE_KEY = 
$SAFEMAP_SERVICE_KEY =

$EMERGENCY_BELL_URL = "https://apis.data.go.kr/1741000/emergency_call_box_info"
$SECURITY_LIGHT_URL = "https://www.safetydata.go.kr/V2/api/DSSP-IF-00083?serviceKey=AWQBPX6SLBTY063W"

gcloud config set project $PROJECT_ID  
```

- batch 한 번만 돌리기

```jsx
gcloud run services update "$SERVICE" \
  --region "$REGION" \
  --min-instances 1 \
  --max-instances 1 \
  --update-env-vars "PUBLIC_DATA_SERVICE_KEY=$PUBLIC_DATA_SERVICE_KEY,SAFEMAP_SERVICE_KEY=$SAFEMAP_SERVICE_KEY,SAFETY_DATA_EMERGENCY_BELL_URL=$EMERGENCY_BELL_URL,SAFETY_DATA_SECURITY_LIGHT_URL=$SECURITY_LIGHT_URL,SAFETY_DATA_PAGE_SIZE=1000,SAFETY_INGESTION_SCHEDULER_ENABLED=true,SAFETY_INGESTION_SCHEDULER_CRON=0 */2 * * * *,SAFETY_INGESTION_SCHEDULER_ZONE=Asia/Seoul,SAFETY_SCORE_SCHEDULER_ENABLED=true,SAFETY_SCORE_SCHEDULER_CRON=30 */2 * * * *,SAFETY_SCORE_SCHEDULER_ZONE=Asia/Seoul"
```

- 실행 확인

```jsx
gcloud run services logs read salmanhae-api \
  --region asia-northeast3 \
  --limit 100
```

- 한 번 돌린 뒤 끄기

```jsx
gcloud run services update salmanhae-api \
  --region asia-northeast3 \
  --update-env-vars "SAFETY_INGESTION_SCHEDULER_ENABLED=false,SAFETY_SCORE_SCHEDULER_ENABLED=false"
```

### 현재 확인된 내용

코드 기본값은 두 scheduler 모두 false다. cron은 매월 1일 03:00/03:30 KST이고 분산 lock은 없다. 배포 설정에서 활성화 여부는 확인되지 않는다.

### 확인이 필요한 이유

“운영 배치”라는 표현의 사용 가능 여부와 실제 갱신 주기를 결정한다.

### 답에 따른 문장 예시

- **긍정적으로 확인된 경우**: “발표 기간에는 단일 instance에서 환경변수를 켜고 수동 로그로 실행을 확인했습니다.”처럼 한계를 함께 쓴다.
- **확인되지 않은 경우**: “조건부 scheduler 코드를 구현했지만 운영 활성화와 단일 실행은 검증되지 않았습니다.”

## 12. 저장소 밖 협업·발표·사용자 결과

### 질문

GitHub에 남지 않은 사람 리뷰, 페어 프로그래밍, API 계약 회의, 발표 평가, 사용자 테스트 피드백이 있나요? 누가 어떤 제안을 했고 본인이 어떻게 반영했는지 증거를 남길 수 있나요? `[본인 확인 필요]`

### 사용자 답변

- 리뷰는 codeRabbit이 전담으로 한게 맞음

### 현재 확인된 내용

GitHub PR에는 사람 리뷰가 거의 없고 CodeRabbit·Vercel 기록이 중심이다. 발표 점수와 사용자 피드백은 저장소에서 확인되지 않는다.

### 확인이 필요한 이유

협업 역량과 결과를 구체화하되 자동 리뷰를 사람 협업으로 바꾸거나 발표 성과를 만들어내지 않기 위해서다.

### 답에 따른 문장 예시

- **긍정적으로 확인된 경우**: “팀원과 응답 DTO를 회의에서 합의했고, 제가 Spring 계약을 구현한 뒤 팀원이 supervisor와 최종 UI를 연결했습니다.”
- **확인되지 않은 경우**: “Issue와 PR 단위로 계층을 나눠 구현했고 자동 리뷰 지적을 후속 커밋에 반영했습니다.”
