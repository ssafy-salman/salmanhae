# 살만해 면접 준비 팩

> 이 문서는 현재 코드, 커밋, PR·Issue, 자동 리뷰 기록, 보존 산출물과 `12-confirmation-questions.md`의 사용자 직접 답변을 함께 사용한다. 코드·Git으로 검증된 사실, 사용자가 직접 확인했다고 답한 사실, 현재도 미확인인 사실을 구분하며 서로 충돌하면 어느 한쪽으로 합치지 않는다.

## 답변 원칙

- 개인 기여는 직접 작성한 코드와 diff가 확인되는 A등급 범위에만 “제가 구현했습니다”라고 말한다.
- 팀원의 JWT core·LangGraph Supervisor·최종 챗봇 UI·안전 카드 UI는 공동 또는 팀원 기여로 분리한다.
- 역할은 Frontend/Backend 직군 분리가 아니라 기능 단위 분담이었다는 사용자 답변을 사용한다. 사용자는 주로 F-1·F-3·F-4와 그에 필요한 Spring·FastAPI·Vue·DB를 맡았다고 기억하며, 세부 구현은 Git diff로 다시 한정한다.
- 일정은 최종 기획·구현의 5~6월과 Git에서 검증되는 2026-06-12~06-26을 함께 쓴다. 2~3월 소규모 작업, 전면 재구성, GitLab 이력 소실은 사용자 직접 답변이며 현재 저장소로 재현되지 않는다.
- 테스트 정의, PR의 테스트 실행 기록, 배포 workflow 성공, 실제 운영 성공을 서로 다른 사실로 말한다.
- 사용자는 Q6에서 테스트 코드를 Codex가 생성했다고 답했지만 대상 파일과 사람 검토 범위는 특정하지 않았다. pipeline·chat·legal 테스트 전체의 저작 provenance로 확대하지 않으며, PR 리뷰는 CodeRabbit 자동 리뷰로 표현한다.
- 보존 폴더는 8개 source 실행을 검증하지만 범위는 세종을 제외한 16개 시·도의 267개 `LAWD_CD` 조회 코드다. “전국 전체”라고 말하지 않는다.
- 사용자의 “매물 8,000개” 기억과 보존 파일의 합성 매물 4,000행은 충돌한다. DB snapshot이 없으므로 8,000을 성과 수치로 쓰지 않는다.
- 안전 점수는 범죄 위험도나 치안 보장이 아니라 시설 접근성 비교용 보조 지표라고 먼저 밝힌다.
- 일회성 Cloud Run 배치 실행 조건과 당시 로그 확인은 사용자 직접 답변으로만 분류한다. 현재 운영 scheduler나 네 source의 정확한 적재 건수를 뜻하지 않는다.
- 해결하지 못한 `workersCalled`/`intent` 계약 drift와 timeout budget 역전을 숨기지 않는다.

---

## 1. 프로젝트 소개

### 30초 버전

살만해는 청년·1인 가구가 집을 고를 때 가격뿐 아니라 주변 안전시설과 법률 정보를 함께 확인하도록 돕는 2인 팀 부동산 탐색 서비스입니다. 직군이 아니라 기능 단위로 나눴고, 저는 주로 F-1·F-3·F-4에 필요한 Spring·FastAPI·Vue·DB를 오가며 거래 데이터 파이프라인, 선택 매물 서비스 계약, 네 종류 안전시설 수집과 시설 접근성 사전 계산을 구현했습니다. 외부 API 운영 여부와 서비스 간 응답 계약은 검증 수준까지 구분해 설명합니다.

### 1분 버전

살만해는 거래 정보만으로 집을 판단하기 어려운 청년·1인 가구를 위해 지도 검색, 가격 분석, 주변 시설 접근성, 법률 근거 기반 질의를 한 흐름으로 묶은 2인 팀 프로젝트입니다. 브라우저는 Vue에서 Spring Boot만 호출하고, Spring이 JWT 경계와 도메인 API를 담당하며 내부 HTTP로 FastAPI의 LangGraph 기반 AI 기능을 호출합니다. 저는 첫째, 국토교통부 8개 거래 source를 공통 모델로 정규화하고 결정적 fingerprint와 PostgreSQL conflict upsert를 적용한 수동 실행형 offline bootstrap을 만들었습니다. 보존 산출물에서 세종이 빠진 정규화 거래 2,612,697행을 확인했습니다. 둘째, 팀원이 구현한 JWT core와 Supervisor 위에서 선택 매물 ID가 Spring과 FastAPI를 거쳐 초기 분석 카드로 변환되는 코드 경로를 연결했습니다. 셋째, 네 시설 유형을 source별 client로 분리하고 좌표를 통합한 뒤 bbox와 Haversine 구면 근사로 시설 접근성 값을 사전 계산했습니다. 최종 UI는 팀원이 고도화했고, 현재는 `workersCalled`가 Spring DTO에서 유실되는 계약 부채를 가장 먼저 보완해야 합니다.

### 3분 버전

살만해는 청년과 1인 가구가 집을 찾을 때 가격, 주변 환경, 법률 정보를 각각 다른 서비스에서 확인해야 하는 불편을 줄이려는 2인 팀 프로젝트입니다. 사용자는 Vue 지도에서 매물을 고른 뒤 가격·안전을 질문하거나, 별도로 임대차 법률을 질문할 수 있습니다. 구조적으로 Frontend는 Spring Boot REST API만 호출합니다. Spring은 JWT 인증 경계, 매물·거래·가격·안전 도메인 API를 담당하고, FastAPI는 LangGraph worker와 pgvector 검색을 담당합니다. 두 backend는 각각 Cloud Run 배포 workflow를 가집니다.

제가 가장 깊게 맡은 첫 번째 영역은 거래 데이터 기반을 만드는 일이었습니다. 요청 때마다 공공 API를 부르지 않는다는 아키텍처 규칙에 따라, 외부 조회부터 XML 파싱, 공통 모델 정규화, SHA-1 기반 결정적 fingerprint, 통계·검색용 매물 파생, 네 테이블 conflict upsert까지 이어지는 오프라인 bootstrap을 구현했습니다. 상세 보존 폴더에는 8개 source × 267개 `LAWD_CD` 조회 코드 × 12개 월 파티션의 기본 tuple과 후속 page가 남아 있고 모든 XML은 별도 감사에서 `000/OK`였습니다. 다만 입력 기준 파일에 세종이 없어 “전국 전체”가 아닙니다. raw와 unique 정규화 결과의 차이는 이번 사후 재처리에서 normalizer reject와 동일 fingerprint 후속 occurrence로 나뉘었지만, 후자는 실제 중복 거래 수가 아닙니다. lite 매물은 실제 중개 매물이 아닌 `MVP_SYNTHETIC`이며, 사용자의 매물 8,000개 기억은 파일과 충돌하고 현재 DB snapshot이 없어 성과로 사용하지 않습니다.

두 번째는 선택 매물 문맥을 AI 분석까지 잃지 않고 전달하는 계약입니다. 팀원이 만든 Spring Security JWT core와 FastAPI Supervisor 위에 `POST /api/v1/chat`을 연결하고, Spring이 `X-Internal-Api-Key`로 `/internal/agent/chat`을 호출하도록 했습니다. Frontend의 `selectedPropertyId`는 Spring의 `Long`에서 FastAPI context의 문자열로 전달됩니다. FastAPI의 가격·안전 worker는 Spring API를 조회해 `toolResults`와 `analysisCards`를 구성하고, `generate_answer`가 이를 바탕으로 최종 답변을 만듭니다. 저는 이 서버 계약과 초기 카드 normalizer/rendering을 구현했고, 최종 챗봇·localStorage 세션 UI는 팀원이 고도화했습니다. 현재 `recentMessages`는 항상 빈 배열이라 서버 multi-turn memory는 아닙니다. 코드 감사에서는 FastAPI의 `workersCalled`, `toolResults`, `nextActions`가 Spring consumer DTO에 없고, 반대로 Spring이 producer에 없는 nullable `intent`를 선언하는 drift를 발견했습니다. 현재 기본 매핑에서 공통 메시지와 카드는 남을 수 있지만 실제 HTTP consumer test와 배포 smoke는 없습니다.

세 번째는 이질적인 안전시설 데이터를 요청 경로 밖에서 처리한 경험입니다. CCTV·비상벨·보안등·Safemap 치안시설은 JSON/XML, 인증 키, endpoint, 좌표계가 달라 source별 client/parser로 격리했습니다. 보안등 응답의 WGS84 좌표가 없을 때 Web Mercator로 가정한 fallback을 수동 역변환하고, merge bounds로 DB 후보를 줄인 뒤 Haversine 구면 근사로 고정 반경의 source row 수를 계산해 `property_score_stat`에 저장합니다. 가중치는 제가 “이 정도면 적절하다”고 판단해 고른 MVP heuristic이며 수학적 calibration은 없습니다. 사용자는 scheduler를 일시 활성화해 로그와 어떤 안전시설 row의 Supabase 적재를 확인했다고 답했습니다. 다만 경찰 opt-in과 별도 보안등 key 설정이 제시 명령에 없고 cron은 독립 실행되며 해당 로그·source별 건수·현재 DB도 없어 상시 운영이나 네 source 성공으로 확대하지 않습니다.

이 프로젝트를 통해 기능을 연결하는 것과 계약·데이터 품질을 운영 수준으로 보장하는 것은 다르다는 점을 배웠습니다. 다시 개선한다면 공유 schema와 실제 역직렬화 contract test를 CI gate로 묶고, 외부 데이터 수집에는 source별 run status·freshness·typed failure를 추가하겠습니다.

---

## 2. 핵심 사례 1 — 8개 source·12개 월 파티션 보존 산출물로 검증한 오프라인 거래 데이터 파이프라인

### 1분 설명

가격 분석의 기반 데이터는 사용자 요청 때마다 국토교통부 API에서 가져오지 않고 미리 적재해야 했습니다. source마다 건물명과 금액 필드가 달랐고 재실행 중복도 막아야 했습니다. 저는 8개 endpoint를 설정으로 선언하고 `FIELD_ALIASES`와 `normalize_row`로 현재 20개 필드의 공통 row를 만들었습니다. 만원 단위는 원으로 바꾸고 월세가 0이면 전세로 구분했습니다. source·위치·건물·계약일·면적·층·금액 조합의 SHA-1 `source_transaction_key`와 DB unique 조건으로 conflict update했습니다. 이 key는 자연키가 아니라 결정적 fingerprint이며 같은 조건의 서로 다른 거래를 합치거나 정정 거래를 새 row로 나눌 수 있습니다. 보존 산출물은 세종 제외 16개 시·도, 267개 `LAWD_CD` 조회 코드, 2025-07~2026-06의 8개 source를 포함합니다. lite 결과는 합성 매물 4,000행과 그 건물의 거래 19,386행이지만, 현재 DB row는 미확인입니다. exactly-once가 아니라 동일 fingerprint 재입력의 단순 중복 insert를 줄이는 수동 실행형 offline bootstrap입니다.

### 3분 설명

**요구사항과 문제**  
서비스의 지도와 가격 분석은 공공 거래 데이터에 의존하지만, 클라이언트 요청마다 외부 API를 호출하면 지연·quota·가용성이 사용자 경로에 들어옵니다. 그래서 원시 데이터를 미리 조회하고 DB에 적재하는 구조가 필요했습니다. 그런데 국토교통부 API는 주택·거래 유형마다 endpoint와 필드명이 달랐습니다. 전월세는 보증금과 월세, 매매는 거래금액을 쓰고 건물명도 `aptNm`, `offiNm`, `mhouseNm`, `houseNm`, `danjiNm`처럼 달라 단순 공통 parser만으로는 downstream 모델을 안정적으로 만들기 어려웠습니다.

**원인과 판단**  
source 차이를 통계·매물 생성 단계마다 반복 처리하면 변화가 여러 계층으로 퍼집니다. 저는 공통 XML 처리 흐름은 유지하되 endpoint와 거래·주택 유형은 `SOURCE_CONFIG`, 필드명 차이는 `FIELD_ALIASES`에서 흡수하도록 했습니다. 기존 Git seed만 보면 아파트·오피스텔 네 source 8,121건까지 확인됐지만, 이후 추가된 `salmanhae-f1-molit-pipeline-20260624` 보존 폴더에서 연립다세대·단독다가구를 포함한 8개 source 전체 실행을 별도로 검증했습니다. “기존 커밋 seed의 범위”와 “추가 보존 산출물의 범위”를 합쳐 말하지 않습니다.

**구현**  
흐름은 `fetch_transactions → normalize_manifest → compute_stats → geocode/generate_properties → load_supabase → verify_db`입니다. `normalize_row`는 source별 필드를 20개 공통 거래 필드로 바꾸고, 만원 단위 문자열을 원 단위 정수로 바꾸며, 월세가 0이면 전세로 분류합니다. 원천 전체에 공통인 안정적 ID가 없어서 source, 법정동·지번, 건물, 계약 연월·일, 면적, 층, 보증금·월세·매매가를 조합해 SHA-1 key를 만듭니다. 보안용 hash가 아니라 고정 길이 결정적 중복 판단 키입니다.

manifest는 요청 tuple과 raw XML 경로를 기록하고, 기록된 비어 있지 않은 파일이 있으면 재사용합니다. 코드 자체는 API `resultCode`를 성공 조건으로 검사하지 않으므로 manifest만 성공 checkpoint라고 부를 수는 없습니다. 이번 보존 산출물에서는 manifest와 별도로 XML 전부를 검사해 `resultCode`, `resultMsg`, page 연속성, 파일명과 XML `pageNo`, 각 요청의 item 합과 `totalCount`를 대조했습니다. 정규화된 거래에서 지역 통계·건물 통계·검색용 매물을 파생한 뒤 `transaction_history`, `region_price_stat`, `building_price_stat`, `properties`를 같은 DB connection에서 batch upsert하고 마지막에 한 번 commit합니다. migration과 DB count 검증은 별도 단계입니다.

**검증된 결과**  
보존 manifest의 기본 요청 조합은 8개 source × 267개 `LAWD_CD` 조회 코드 × 12개 월 파티션, 즉 25,632개입니다. 대량 응답의 추가 page occurrence 321개를 포함해 raw XML은 25,953개입니다. 기간은 `dealYmd` 202507~202606이고, 지역은 16개 시·도이며 세종특별자치시는 없습니다. 따라서 “1년치”는 12개 월 partition이라는 뜻으로 사용할 수 있지만 “전국 전체”는 사용할 수 없습니다. 모든 요청에서 page가 연속됐고 item 합과 `totalCount`, 파일명과 XML `pageNo`가 일치했습니다. XML 25,953개는 모두 `000/OK`였고 `errors.json`은 0건입니다.

raw XML의 `<item>`은 2,751,295개이고, `(source_api, source_transaction_key)`로 dedupe된 결과는 2,612,697행입니다. 원래 실행은 원인 counter를 남기지 않았지만, 이번 검수에서 보존 raw를 HEAD `pipeline.py`로 읽기 전용 재처리해 차이 138,598개를 `normalize_row` reject 6,370개와 동일 fingerprint의 두 번째 이후 occurrence 132,228개로 사후 분리했습니다. 132,228은 실제 중복 거래 수가 아니며 false merge 가능성을 포함하고, reject의 조건별 세부 건수는 아직 없습니다.

| source | 정규화 행 수 |
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

full 통계와 별도로 lite 파일에는 거래 19,386행과 `source=MVP_SYNTHETIC` 합성 매물 4,000행이 있습니다. 합성 매물은 실제 실거래 건물과 anchor 거래를 사용한 시연용 매물이지 중개사가 등록한 실매물이 아닙니다. `generated/properties.jsonl`의 7행은 정확한 실행 경위가 남지 않은 중간 snapshot이므로 면접 성과 수치에서 삭제하고 evidence 문서에만 둡니다.

사용자는 당시 Supabase 적재를 확인했고 “매물 8,000개”로 기억한다고 답했습니다. 적재했다는 사실은 사용자 직접 답변으로 기록하되, 보존 파일에는 4,000개만 있고 load log·당시 DB count·현재 DB count가 없어 8,000은 충돌하는 기억으로 남깁니다. 별도의 기존 seed 8,121건과 합성 매물 300개는 더 이른 소규모 산출물이므로 위 대규모 실행 수치와 합산하지 않습니다.

**한계와 개선**  
이번 파일 검증은 8개 source 실행의 결과를 보여주지만, 코드에는 자동 retry/backoff, 실패 row quarantine, source별 watermark, run ID·단계 status, 운영 scheduler, 전용 pipeline test가 없습니다. `errors.json=0`은 이 실행에서 기록된 fetch 예외가 없었다는 뜻이지 다른 실행의 복구 능력을 증명하지 않습니다. cached XML parse 오류는 실행을 중단할 수 있고 `FAILED` geocode cache도 자동 재시도하지 않습니다. 사용자는 과거 Supabase 적재를 확인했다고 답했지만 rollback fault-injection 자료와 현재 DB 행 수는 확인되지 않습니다. 개선한다면 source별 최소 fixture와 schema contract test를 만들고, request tuple별 시도 횟수·raw/valid/deduped row count·checksum·오류를 run table에 기록한 뒤 staging 완전성 검증을 통과한 결과만 publish하겠습니다.

**보여주는 역량**  
외부 데이터의 schema 차이를 경계에서 정규화하는 모델링, 결정적 식별자와 DB unique constraint의 결합, 적재 transaction 범위, 재실행·실패·검증의 의미를 구분하는 데이터 백엔드 역량을 보여줍니다.

### 코드 수준의 설명

```text
scripts/data_pipeline/pipeline.py

SOURCE_CONFIG (8 endpoint 설정)
  → fetch_transactions (raw XML + manifest)
  → normalize_manifest
      → FIELD_ALIASES
      → normalize_row (20 fields, 만원→원, 전세/월세 구분)
      → source_transaction_key (SHA-1 결정적 키)
  → compute_stats (지역/건물 통계)
  → generate_properties (검색용 매물 파생)
  → load_supabase
      → transaction_history ON CONFLICT (source_api, source_transaction_key)
      → region_price_stat ON CONFLICT (...)
      → building_price_stat ON CONFLICT (...)
      → properties ON CONFLICT (source, source_property_id)
      → 한 connection에서 commit
  → verify_db (테이블 count 출력)
```

- `SOURCE_CONFIG`에는 전월세·매매, 아파트·오피스텔·연립다세대·단독다가구 조합의 8개 endpoint가 있다. 이번 보존 폴더에서는 8개 source 모두 실제 XML과 정규화 행을 확인했다. 다만 그 범위는 세종 제외 16개 시·도다.
- `FIELD_ALIASES`는 같은 의미의 다른 원시 필드를 우선순위대로 찾는다. source별 분기문을 downstream에 흩뜨리지 않는 것이 목적이다.
- 공통 거래 모델은 `source_api`, `source_transaction_key`, 주택·거래 유형, 행정구역·법정동 코드, 지번·건물, 계약일, 금액, 면적·층·건축연도, `raw_json` 등 20개 필드다.
- 키는 DB surrogate id를 대체하는 원천 식별자다. 취소·정정 거래를 같은 거래로 볼지 별개로 볼지는 현재 조합만으로 완전히 해결되지 않는다.
- DB conflict upsert는 동일 unique key의 중복 insert를 막지만, 외부 fetch·manifest·geocoding·파일 기록까지 exactly-once로 만들지는 않는다.
- `load_supabase` 내부 네 batch는 같은 connection에서 실행하고 마지막에 `conn.commit()`한다. migration은 그 transaction에 포함되지 않으며 fault-injection rollback test는 없다.

### 예상 꼬리 질문 10개와 답변 핵심

| 질문 | 모범 답변 핵심 |
|---|---|
| 1. 왜 요청 시 API 호출이 아니라 오프라인 적재를 선택했나요? | 외부 API 지연·quota·장애를 사용자 요청 경로에서 제거하고, 지도·가격 분석이 같은 DB snapshot을 조회하게 하기 위해서다. 실제 성능 개선 수치는 측정하지 않았다고 덧붙인다. |
| 2. 8개 endpoint를 실제로 모두 실행했나요? | Git 비추적 보존 폴더에서 8 source × 267 `LAWD_CD` 조회 코드 × 12개 월 파티션의 25,632개 기본 tuple과 pagination을 확인했다. 세종이 빠진 16개 시·도이고 현재 DB 적재 수치와도 구분한다. |
| 3. 충돌 키에는 무엇이 들어가나요? | source, 법정동·동·지번, 건물, 계약 연월·일, 주택·거래유형, 면적, 층, 보증금·월세·매매가의 15개 값을 직렬화해 SHA-1으로 만든다. 원천 공통 ID가 없어 도입한 fingerprint다. |
| 4. 왜 SHA-1인가요? 충돌 위험은요? | 보안이 아니라 고정 길이 fingerprint다. SHA-1 이론적 충돌보다 같은 날·건물·층·면적·가격의 서로 다른 거래가 합쳐지거나 정정 가격이 새 key가 되는 business-key false merge/split이 더 현실적인 위험이다. |
| 5. upsert를 구현했으면 멱등한 것 아닌가요? | DB write는 같은 `(source_api, key)` 입력의 중복 insert를 막는다. 하지만 fetch, raw 저장, manifest, geocode, 실패 재처리까지 동일한 결과를 보장하지 않으므로 파이프라인 전체 멱등성이나 exactly-once라고 하지 않는다. |
| 6. transaction 범위는 어디까지인가요? | `load_supabase`에서 거래·지역 통계·건물 통계·매물 네 batch가 한 DB connection과 최종 commit을 공유한다. migration과 이전 파일 생성 단계는 별도다. |
| 7. manifest는 어떤 보장을 하나요? | 코드상 manifest는 비어 있지 않은 raw XML의 재사용 목록일 뿐 성공 checkpoint는 아니다. 이번 검증에서는 manifest 밖에서 XML 25,953개의 `000/OK`, page 연속성, `totalCount` 일치를 별도로 확인했다. |
| 8. 중간 실패는 어떻게 처리되나요? | 이번 산출물의 `errors.json`은 0건이지만 자동 retry/backoff는 없다. 새 fetch 예외는 오류에 남길 수 있고 cached XML parse는 중단될 수 있다. 한 번의 무오류 결과와 복구 설계를 구분한다. |
| 9. 2,612,697건은 무엇을 의미하나요? | 세종 제외 16개 시·도·267 조회 코드·12개 월 파티션·8 source에서 current normalizer를 통과하고 source/fingerprint로 dedupe한 JSONL unique row 수다. 현재 Supabase 행 수가 아니다. 사후 replay에서 raw와의 차이는 reject 6,370 + 동일 fingerprint 후속 occurrence 132,228로 나뉘었다. |
| 10. 다시 만든다면 무엇을 먼저 추가하나요? | 8 source별 최소 fixture와 contract test, run ID·tuple status·attempt·row count·checksum, retry+jitter와 quarantine, staging 완전성 검증, source별 freshness/watermark를 추가한다. |

### 답변하면 안 되는 과장 표현

- “8종 데이터를 전국 전체에서 수집했습니다.”
- “정규화 거래 2,612,697건과 매물 8,000건이 현재 운영 DB에 있습니다.”
- “exactly-once와 완전한 멱등성을 보장했습니다.”
- “manifest가 성공한 단계부터 정확히 재개합니다.”
- “자동 retry와 scheduler를 구축했습니다.”
- “raw와 정규화의 138,598건 차이는 전부 중복입니다.”
- “`MVP_SYNTHETIC` 4,000개는 실제 중개 매물입니다.”

---

## 3. 핵심 사례 2 — 선택 매물 문맥을 전달하는 Spring–FastAPI–Frontend 서비스 계약

### 1분 설명

아키텍처상 Frontend는 FastAPI를 직접 호출할 수 없고 Spring의 JWT 검증을 거쳐야 했습니다. 저는 팀원이 만든 JWT core 위에 `POST /api/v1/chat` controller/service를 연결하고, Spring의 `AiAgentClient`가 내부 키로 FastAPI `/internal/agent/chat`을 호출하도록 구현했습니다. Frontend의 선택 매물 ID는 Spring `Long`에서 FastAPI `context.selectedPropertyId` 문자열로 전달됩니다. FastAPI의 가격·안전 worker는 Spring API를 조회해 `toolResults`와 `analysisCards`를 구성하고, `generate_answer`가 이를 바탕으로 최종 답변을 만듭니다. 저는 초기 normalizer와 카드 표시 계약까지 연결했습니다. 최종 챗봇과 localStorage 세션 UI는 팀원이 고도화했습니다. 현재는 FastAPI의 `workersCalled`가 Spring DTO에 없어 유실되고 Spring은 producer에 없는 nullable `intent`를 선언합니다. 현재 기본 converter에서 공통 메시지와 카드는 남을 수 있지만 실제 HTTP consumer test와 배포 smoke가 없어 전체 성공이나 장애를 단정하지 않습니다.

### 3분 설명

**요구사항과 경계**  
사용자가 지도에서 매물을 고른 뒤 “이 매물 가격이 적정한가”, “주변 시설은 어떤가”라고 물을 때 선택 ID가 AI 분석까지 전달돼야 했습니다. 동시에 Frontend는 Spring만 직접 호출하고, 인증이 필요한 chat은 Spring Security JWT 필터를 거쳐야 한다는 규칙이 있었습니다. Spring은 사용자·도메인·공개 API의 경계이고 LangGraph와 LLM은 FastAPI에만 있어야 했습니다.

**문제와 원인**  
Vue, Java, Python은 각각 다른 타입과 DTO를 사용합니다. Frontend의 선택 ID, Spring의 `Long`, FastAPI context의 `str | None`을 맞춰야 했고, 가격 분석은 매물 상세·최근 거래·가격 분석 결과를 조합해야 했습니다. 실패를 단순 빈 카드로 숨기면 정상적으로 분석 대상이 없는 경우와 Spring API 장애를 구분할 수 없습니다. 더 근본적으로는 세 서비스가 독립 DTO를 수기로 정의했는데 공유 schema와 실제 consumer contract test가 없어서 후속 변경이 조용히 어긋날 수 있었습니다.

**구현과 역할 경계**  
Browser는 `message`, 선택적 `sessionId`, `selectedPropertyId`를 `POST /api/v1/chat`으로 보냅니다. Spring `ChatRequest.message`는 `@NotBlank`로 검증되고 controller는 service에 위임합니다. `AiAgentClient`는 사용자 ID와 context를 조립하고 `X-Internal-Api-Key`를 붙여 FastAPI `/internal/agent/chat`을 호출합니다. `selectedPropertyId`는 문자열로 변환되고 `recentMessages`는 항상 빈 배열입니다. FastAPI `SpringClient`는 선택된 ID로 Spring의 공개 `GET /api/v1/properties/**`, `/api/v1/price-analysis`, safety summary API를 호출합니다. 가격 worker는 상세·거래·가격 분석을 순차 조회하고, 안전 worker는 사전 계산된 DB summary를 사용합니다. FastAPI 응답에는 `workersCalled`, `answer`, properties, cards, `toolResults`, `nextActions`가 있고 `intent`·`sessionId`는 없습니다. Spring은 `answer`를 공개 `message`로 바꾸고 요청의 `sessionId`를 그대로 돌려줍니다. 따라서 현재 세션은 브라우저 대화 묶음이지 서버 multi-turn memory가 아닙니다.

제가 직접 맡은 범위는 Spring chat controller/service/client, 내부 API key 계약, Spring 가격·안전 read API, FastAPI의 Spring 조회 client와 선택 ID 전달, 초기 legal/analysis card normalizer·rendering입니다. JWT core와 LangGraph Supervisor는 팀원 구현이고, 최종 챗봇 markup·style·세션 UX와 최종 안전 카드 UI도 팀원 후속 구현입니다.

**오류와 timeout**  
FastAPI는 Spring 조회 실패를 `SPRING_API_UNAVAILABLE` 형태의 구조화된 fallback으로 바꾸는 경로를 가지고, Spring은 FastAPI transport/null 실패를 `AI_SERVICE_UNAVAILABLE` 502로 변환합니다. 코드 기본값은 Spring→FastAPI connect 2초/read 10초, FastAPI→Spring 개별 호출 5초, LLM client 20초입니다. 가격 worker의 내부 호출이 순차이므로 바깥 10초보다 내부 최악 시간이 길어질 수 있습니다. 실제 배포 환경변수와 latency 측정값은 확인되지 않았습니다.

**달성한 결과와 현재 부채**  
선택 매물 ID가 세 모듈을 지나 분석 worker의 입력이 되고, 분석 결과를 카드로 표현할 초기 코드 계약을 구성했습니다. 하지만 후속 FastAPI 응답의 `workersCalled`, `toolResults`, `nextActions`를 Spring 내부 DTO가 선언하지 않고, 반대로 Spring은 producer에 없는 nullable `intent`를 선언합니다. 현재 기본 converter가 unknown top-level field를 무시하고 공통 field의 이름·type이 맞으면 `answer`와 카드는 남을 수 있지만 worker metadata는 유실되고 `intent`는 `null`, Frontend에서는 빈 문자열이 됩니다. 카드 내부 type이 맞지 않으면 변환 자체가 실패할 수 있습니다. `nextActions`는 현재 기본 빈 배열이고 `toolResults`가 공개 필수 field였다는 근거도 없으므로 사용자 회귀로 단정하지 않습니다. `workersCalled` drift와 실제 UX 영향도 구분합니다.

사용자는 이 불일치가 발표 시연이나 실제 화면에 어떤 영향을 줬는지 모르겠다고 답했습니다. 따라서 이를 프로젝트 중 직접 발견·해결한 장애 사례로 말하지 않고, 사후 코드 감사에서 확인한 미해결 계약 부채로만 설명합니다.

**개선 설계와 학습**  
공개할 metadata 범위를 먼저 정하고, FastAPI OpenAPI 또는 versioned contract case를 계약 원천으로 두겠습니다. 각 case에 FastAPI 내부 응답 fixture와 그로부터 기대하는 Spring 공개 응답 fixture를 함께 관리하고, 실제 `AiAgentClient` 역직렬화 test와 Frontend normalizer test를 연결해 CI deploy gate에 넣겠습니다. 기능 연결보다 서비스 경계의 변화와 실패 의미를 검증하는 일이 더 중요하다는 점을 배웠습니다.

### 코드 수준의 설명

```text
Frontend
  POST /api/v1/chat
  { message, sessionId?, selectedPropertyId?: number }
        │ Spring Security JWT filter
        ▼
ChatController → ChatServiceImpl → AiAgentClient
  connect timeout 2s / read timeout 10s (코드 기본값)
  X-Internal-Api-Key
  POST /internal/agent/chat
  { userId, sessionId, message,
    context: { selectedPropertyId?: string, recentMessages: [] } }
        ▼
FastAPI AgentChatRequest / LangGraph worker
  SpringClient timeout 5s per call
  GET /api/v1/properties/**, /api/v1/price-analysis, safety-summary
        ▼
FastAPI AgentChatResponse
  { workersCalled, answer, properties, legalCards,
    analysisCards, toolResults, nextActions }
        ▼
Spring AgentChatResponse
  { intent, answer, properties, legalCards, analysisCards }
        ▼
Spring ChatResponse → frontend chat-normalizer.js
```

- `backend/.../controller/chat/ChatController.java`: 인증된 공개 chat endpoint와 입력 위임.
- `backend/.../service/chat/ChatServiceImpl.java`: service 경계.
- `backend/.../service/chat/AiAgentClient.java`: 내부 request 조립, 선택 ID 문자열 변환, 내부 키, timeout, FastAPI 응답의 Spring 공개 DTO 변환.
- `backend-ai/app/api/schemas.py`: alias 기반 camelCase request/response. 현재 producer에는 `workersCalled`가 있고 `intent`가 없다.
- `backend-ai/app/clients/spring_client.py`: FastAPI에서 Spring 도메인 GET API 호출과 오류 구조화.
- `frontend/src/api/chat-normalizer.js`: 공개 응답 normalize. 현재 `intent: data.intent || ''`.
- FastAPI→Spring 호출은 별도 내부 키를 붙이지 않는 공개 GET 경로다. “양방향 모두 내부 key 인증”이라고 말하면 안 된다.
- `sessionId`는 Spring이 요청 값을 echo하고 `recentMessages=[]`이므로 서버가 대화 이력을 기억한다고 말하면 안 된다.

### 예상 꼬리 질문 12개와 답변 핵심

| 질문 | 모범 답변 핵심 |
|---|---|
| 1. 왜 Frontend가 FastAPI를 직접 호출하지 않게 했나요? | JWT·사용자 권한과 공개 오류 계약을 Spring 경계에 모으고 AI service URL·key를 브라우저에 노출하지 않기 위해서다. 프로젝트 아키텍처 규칙이기도 했다. |
| 2. 선택 매물 정보 전체를 보내지 않고 ID를 보낸 이유는요? | 매물 전체를 복제하지 않고 ID만 전달해 저장 데이터를 다시 조회하므로 payload 중복과 매물 필드 변조 가능성을 줄인다. ID 유효성·인가 문제는 별도 검증 대상이다. |
| 3. Java `Long`과 Python 문자열 ID는 어떻게 맞췄나요? | Spring `AiAgentClient.selectedPropertyId`에서 `String.valueOf`로 변환하고 FastAPI Pydantic schema의 `selectedPropertyId` 문자열 또는 `None` 필드에 넣었다. null은 그대로 optional로 유지한다. |
| 4. FastAPI가 Spring을 호출할 때도 내부 API key를 쓰나요? | 현재는 아니다. FastAPI는 Spring의 공개 GET `/api/v1/properties/**`, `/api/v1/price-analysis`를 service-to-service로 호출한다. Spring→FastAPI POST에만 내부 key가 있다. 향후 권한·네트워크 경계를 재검토할 수 있다. |
| 5. 장애는 어떻게 전달되나요? | FastAPI의 Spring client는 HTTP 오류와 필수 필드 누락(`KeyError`), type·value 오류를 구조화된 `SPRING_API_UNAVAILABLE` fallback으로 바꾸는 경로가 있고, Spring의 FastAPI transport/null 실패는 `AI_SERVICE_UNAVAILABLE` 502가 된다. 모든 내부 예외가 같은 방식으로 복구된다고 말하지 않는다. |
| 6. timeout 설계는 안전한가요? | 코드 기본값 기준 안전하지 않다. 바깥 Spring read 10초보다 내부 5초 호출 여러 개와 LLM 20초 budget이 크다. 실제 장애 관측값은 없지만 구조적 inversion이어서 병렬화·deadline propagation이 필요하다. |
| 7. `workersCalled` 불일치가 왜 컴파일에서 잡히지 않았나요? | Java와 Python이 독립 DTO를 JSON으로 주고받고 현재 기본 converter가 unknown top-level field를 무시하기 때문이다. 이름·type이 맞는 공통 필드는 남을 수 있지만 카드 type drift까지 안전한 것은 아니다. |
| 8. 어떤 contract test를 추가하겠나요? | FastAPI 내부 응답 fixture를 MockWebServer/WireMock으로 `AiAgentClient`에 실제 응답하고 기대하는 Spring 공개 `ChatResponse` 변환을 검증한다. 같은 contract case에 공개 응답 fixture를 짝지어 Frontend normalizer test에 사용하고 CI gate로 묶는다. |
| 9. 본인이 최종 챗봇 UI까지 구현했나요? | 선택 매물 전송과 초기 legal/analysis card normalizer·rendering을 구현했다. 최종 markup·style·세션 UX와 최종 안전 카드 UI는 팀원이 고도화했다. |
| 10. 다시 설계한다면 무엇을 바꾸나요? | 공개 metadata를 먼저 결정하고 schema version을 둔다. OpenAPI 기반 생성 DTO 또는 versioned fixture, consumer contract test, correlation ID, 전체 latency budget과 하위 deadline, 독립 조회 병렬화를 적용한다. |
| 11. `sessionId`가 있는데 다중 턴 대화인가요? | 아니다. 현재 Spring은 `recentMessages=[]`을 보내고 공개 응답의 session ID도 request echo다. 팀원 UI가 localStorage에서 대화를 묶을 뿐 서버 memory 증거는 없다. |
| 12. FastAPI OpenAPI를 왜 계약 원천으로 쓰지 않았나요? | FastAPI가 `/openapi.json`을 자동 생성하지만 versioned artifact·DTO 생성·CI 검사에 사용하지 않았다. 당시 이유는 기록되지 않아 일정·판단을 추정하지 않고, 현재 개선안으로만 제안한다. |

### 답변하면 안 되는 과장 표현

- “JWT core와 Supervisor를 제가 구현했습니다.”
- “최종 챗봇·세션·안전 카드 UI를 혼자 구현했습니다.”
- “FastAPI와 Spring의 현재 계약은 완전히 일치합니다.”
- “`workersCalled` 불일치를 해결했습니다.”
- “현재 전체 채팅이 이 문제로 장애입니다.”
- “항상 10초 안에 응답합니다.”
- “양방향 service-to-service 호출이 모두 내부 key로 보호됩니다.”
- “배포 workflow 성공으로 선택 매물 E2E를 검증했습니다.”

---

## 4. 핵심 사례 3 — 네 시설 유형 adapter, 좌표 통합, 시설 접근성 사전 계산

### 1분 설명

안전 분석은 요청마다 외부 API를 호출하지 않고 시설 데이터를 미리 저장한 뒤 매물별 지표를 계산해야 했습니다. CCTV, 비상벨, 보안등, Safemap 치안시설은 JSON/XML, 인증 키, endpoint, 좌표계가 달라 source별 Spring client/parser로 격리했습니다. 보안등 응답에서 WGS84가 없을 때 Web Mercator로 가정한 fallback을 Java `Math`로 역변환했습니다. merge bounds로 DB 후보를 줄이고 Haversine 구면 근사로 고정 반경의 source row 수를 계산해 `property_score_stat`에 저장했습니다. 가중치는 제가 선택한 미보정 heuristic입니다. 사용자는 일회성 Cloud Run 설정에서 일부 Supabase 적재를 확인했다고 답했지만 당시 로그와 source별 행 수, 경찰 opt-in·별도 보안등 key 설정, 현재 DB는 재검증되지 않아 네 source나 상시 운영의 성공으로 표현하지 않습니다.

### 3분 설명

**요구사항과 문제**  
사용자가 매물의 주변 환경을 빠르게 비교하려면 매 요청에서 외부 source를 호출하고 모든 시설과 거리를 계산해서는 안 됐습니다. 공공 API 데이터는 배치로 수집해 DB에 저장하고 요청 시 DB만 조회한다는 규칙도 있었습니다. 대상은 CCTV, 비상벨, 보안등, Safemap `IF_0036` item을 `POLICE`로 정규화한 네 시설 유형이었습니다.

**API별 차이와 장애 기록**  
CCTV는 `apis.data.go.kr` 계열 `cctv_info/info` JSON endpoint와 `PUBLIC_DATA_SERVICE_KEY` 계열을 사용하고 WGS84 위·경도를 읽습니다. 이전 CSV endpoint의 403은 Issue #90에 있지만 실행 환경과 제공자 내부 원인은 확인되지 않습니다. 비상벨은 환경변수 JSON endpoint와 같은 public key 계열, WGS84 필드를 사용하며 Issue #92에 Cloud Run 401이 기록돼 있습니다. 보안등은 별도 `SECURITY_LIGHT_SERVICE_KEY`와 JSON endpoint를 사용하고 WGS84 또는 `XMAP/YMAP/GEOM` fallback을 처리합니다. CCTV를 포함한 실제 제공기관 명칭과 비상벨·보안등의 세부 기관은 저장소만으로 확정하지 않습니다. Safemap source는 `safemap.go.kr` 계열 생활안전지도 `IF_0036` XML과 별도 `SAFEMAP_SERVICE_KEY`를 쓰고 opt-in일 때만 client bean을 활성화하지만, `fclty_ty`로 경찰서만 filter하지 않고 item을 모두 `POLICE`로 매핑합니다. 공공 key는 raw 값을 code에서 encode하는 경로라 이미 percent-encoded 값을 넣으면 double-encoding 위험이 있습니다. 사용자 답변의 명령에는 Safemap opt-in과 별도 보안등 key 설정이 보이지 않고 두 보안등 URL·비상벨 base URL도 현재 코드와 충돌 가능해 source별 사후 성공을 확인할 수 없습니다. 기존 환경에 key가 남아 있었는지는 모르므로 실패했다고도 단정하지 않습니다.

**판단과 구현**  
하나의 거대한 client에서 분기하면 인증·pagination·parser 변경이 서로 영향을 줍니다. 그래서 source별 client/parser로 격리하고 결과를 `type`, `source`, `source_id`, 이름·주소·위경도의 공통 시설 모델로 바꿨습니다. 시설 저장은 `(type, source, source_id)` unique 기준의 row별 update 후 insert이며 source-level `@Transactional`, snapshot 승격, stale row 삭제가 없습니다. 반면 계산된 `property_score_stat` upsert 경로는 transaction을 사용합니다. 안전 batch 전체가 원자적·멱등하다고 말하지 않습니다.

좌표는 source adapter 경계에서 WGS84로 정규화했습니다. GIS library는 쓰지 않았고, 보안등 응답에서 WGS84가 없을 때의 `XMAP/YMAP/GEOM` fallback은 EPSG:3857을 가정해 반지름 6,378,137m와 Java `Math` 공식을 사용합니다. 점수 계산에서는 활성 매물을 100개 chunk로 나누고, 각 매물의 최대 반경에 1m margin을 더한 bounds를 합쳐 DB 후보를 조회합니다. 이후 매물별 bounds를 다시 확인하고 평균 지구 반지름 6,371,000m의 Haversine 구면 근사로 거리를 계산합니다. 두 반지름은 EPSG:3857 축 상수와 평균 지구 반경이라는 용도가 다릅니다. CCTV·비상벨·보안등 source row는 300m, `POLICE` source row는 500m 이내를 셉니다.

점수는 CCTV source row 10건, 비상벨 source row 3건, 보안등 source row 20건, `POLICE` source row 1건이 각각 최대 기여점에 도달하도록 정규화해 합산합니다. CCTV row의 description에 카메라 대수가 있어도 점수는 카메라 수가 아니라 row 수를 셉니다. 고유 설치지점 수로도 별도 검증하지 않았습니다. threshold와 weight는 제가 정한 MVP 제품 가설이며 수학 계산, 범죄 데이터 calibration, 전문가 검토는 없었습니다. `safety-summary`의 `radius=300/500` parameter는 재계산 조건이 아니라 응답에 echo되고 값은 고정 혼합식이라는 계약 부채도 있습니다.

**검증과 결과**  
source client/parser fixture, 좌표 변환, DAO, ingestion service, 점수 계산 테스트와 PR diff가 있습니다. Issue #68~#78, #90/#92와 PR #69~#79, #91/#93에서 구현·보강을 확인할 수 있습니다. 이와 별도로 사용자는 API 문제를 배포 후 직접 확인했고 Q6의 관련 테스트는 Codex가 생성했다고 답했지만, Git의 정확히 어느 파일·case를 가리키는지와 사람 검토 범위는 연결하지 못했습니다. PR 검토는 CodeRabbit 자동 리뷰였으므로 사람 리뷰로 말하지 않습니다.

운영 맥락은 별도 등급으로 답합니다. 사용자가 제시한 한 명령 조각은 Cloud Run service를 min/max instance 1로 두고 CPU throttling을 해제하며, 수집과 점수 cron을 2분마다 각각 초 0과 초 30에 시작하도록 설정합니다. 다른 “한 번만” 명령 조각은 CPU 옵션을 생략합니다. 사용자는 로그와 Supabase 적재를 확인한 뒤 비활성화했다고 답했지만, 초 30 offset은 수집 완료 후 30초를 보장하지 않고 cron이 정확히 한 번만 실행됐는지도 알 수 없습니다. 저장소 기본은 두 scheduler off·매월 1일 03:00/03:30 KST이고 배포 workflow는 min 0/max 3이므로, 당시 명령 기억·현재 코드 기본·현재 Cloud Run 상태를 구분합니다. 당시 source별 행 수, 401 수정 전후 응답, 현재 Supabase 행 수는 미확인입니다.

**남은 문제와 개선**  
상위 ingestion service는 source 예외를 잡아 다음 source로 진행하지만, concrete client가 HTTP/parse 오류를 빈 목록 또는 부분 목록으로 바꿀 수 있어 실패가 0건 성공처럼 보일 수 있습니다. typed result, source/page별 row count·status·freshness, staging snapshot과 승격, stale row reconciliation이 필요합니다. 한 답변 조각의 min=max=1·CPU throttling 해제 조건도 영구 단일 실행 보장이나 재시도·중복 방지를 제공하지 않습니다. 지속 운영이라면 Cloud Scheduler→Cloud Run Job, run ledger와 DB lock으로 바꾸는 것이 적합합니다.

**보여주는 역량**  
외부 시스템 차이를 adapter 경계에 가두는 설계, 좌표 정규화와 공간 후보 축소, 요청 비용을 배치로 이동하는 Spring/JDBC 설계, 부분 실패와 관측성의 trade-off를 설명할 수 있습니다.

### 코드 수준의 설명

| 시설 | client | 응답·인증 | 좌표 처리 | 확인 한계 |
|---|---|---|---|---|
| CCTV | `CctvOpenApiClient` | data.go.kr `cctv_info/info` JSON, `PUBLIC_DATA_SERVICE_KEY` 계열 | WGS84 | 이전 CSV 403 기록. JSON 전환 후 운영 적재 미확인 |
| 비상벨 | `EmergencyBellOpenApiClient` | 환경변수 JSON endpoint, public key 계열 | WGS84 | Cloud Run 401 기록. 사후 운영 성공 미확인 |
| 보안등 | `SecurityLightOpenApiClient` | 환경변수 JSON endpoint, `SECURITY_LIGHT_SERVICE_KEY` | WGS84 또는 Web Mercator | fixture·변환 코드 확인, live 적재 미확인 |
| Safemap 치안시설 | `SafemapPoliceFacilityClient` | 생활안전지도 `IF_0036` XML, `SAFEMAP_SERVICE_KEY`, opt-in | 응답 위·경도 | item 세부 유형 filter 없이 `POLICE` 정규화. key 오류 기록, live 적재 미확인 |

```text
source client/parser
  → 공통 SafetyFacility(type, source, sourceId, name, address, lat, lon)
  → (type, source, source_id) 기준 저장
  → PropertySafetyScoreServiceImpl.recalculateAll
      1. 활성 매물 좌표순 정렬
      2. 100개씩 chunk
      3. 매물별 501m bounds 생성 후 chunk bounds merge
      4. SafetyFacilityDao.findInBounds로 후보 조회
      5. 매물별 bounds 재검사
      6. Haversine 구면 근사 거리 계산
      7. 300m/500m count + cap/weight
      8. property_score_stat upsert
```

점수식은 다음과 같이 설명할 수 있다.

```text
score = round(
  min(cctvCount / 10, 1) * 30
  + min(bellCount / 3, 1) * 25
  + min(lightCount / 20, 1) * 25
  + min(policeCount / 1, 1) * 20
)
score = clamp(score, 0, 100)
```

이 식은 도메인 통계로 calibration된 범죄 예측식이 아니다. 시설 개수와 거리를 이용해 매물 간 상대적 시설 접근성을 비교하는 MVP 규칙이다.

### 예상 꼬리 질문 12개와 답변 핵심

| 질문 | 모범 답변 핵심 |
|---|---|
| 1. 왜 API별 client를 분리했나요? | JSON/XML, endpoint, key, pagination, 좌표 alias가 달라 변경과 실패 범위를 source 내부에 가두기 위해서다. 공통 모델 이후 ingestion·score는 source를 몰라도 된다. |
| 2. 403과 401의 원인은 무엇이었나요? | 403은 이전 CCTV CSV 접근에서 기록됐지만 환경·제공자 내부 원인은 미확인이다. Cloud Run 401과 key 관련 오류는 Issue에 있고 사용자는 배포 후 직접 확인했다고 답했다. key 전달·encoding 보강을 구현했지만 보존된 사후 응답은 없어 하나의 원인·완전 해결로 묶지 않는다. |
| 3. 좌표 변환은 어디서 했나요? | 보안등 source client 경계에서 WGS84가 없을 때 EPSG:3857로 가정한 `XMAP/YMAP/GEOM` fallback을 별도 GIS library 없이 Java `Math` 역식으로 바꾼다. fixture·전지구 범위 검증일 뿐 한국 영역 sanity check와 provider live CRS 검증은 아니다. |
| 4. 왜 Haversine을 선택했나요? | phase 범위에서 공간 extension 없이 bbox보다 정밀한 원형 반경의 구면 근사 판정을 구현하기 위해서다. DB bbox로 후보를 줄인 뒤 적용하며 PostGIS와의 benchmark는 없다. |
| 5. bbox만으로는 안 되나요? | 위·경도 사각형은 원형 반경 밖의 후보도 포함한다. bbox는 저렴한 prefilter이고 Haversine이 최종 300m/500m 판정을 한다. |
| 6. 왜 100개 chunk와 501m bounds인가요? | 매물별 DB query와 전체 Cartesian 비교를 줄이기 위해 100개 매물의 후보 bounds를 합쳐 조회한다. 최대 반경 500m에 1m margin을 둔다. 100이라는 값의 성능 benchmark 근거는 저장소에 없다고 밝힌다. |
| 7. 가중치는 어떻게 정했나요? | 제가 “이 정도면 적절하다”고 판단해 CCTV 30, 비상벨 25, 보안등 25, `POLICE` 20으로 정했다. count는 source row 기준이고 수학적 derivation이나 통계 calibration은 없는 MVP heuristic이다. |
| 8. 부분 실패는 안전하게 처리되나요? | 상위 서비스는 source 예외 후 다음 source를 진행하지만 일부 client는 오류를 빈/부분 목록으로 바꿀 수 있어 실패 count가 틀릴 수 있다. typed success/failure와 source snapshot 승격이 필요하다. |
| 9. scheduler를 Cloud Run에서 실제로 실행했나요? | 사용자는 짧은 cron을 켜 로그를 확인한 뒤 비활성화했다고 답했다. 한 명령 조각은 min=max 1·CPU throttling 해제이고 두 cron은 2분마다 초 0/30에 독립 시작한다. 적용 로그가 없어 정확한 횟수·선후관계·현재 설정은 모르며 상시 월간 운영이나 exactly-once라고 하지 않는다. |
| 10. 네 API가 실제 운영에서 모두 성공했나요? | 사용자는 배포 후 어떤 안전시설 row의 Supabase 적재를 봤다고 답했다. 그러나 명령에 경찰 opt-in이 없고 다른 source 설정도 코드와 충돌 가능하며, source별 성공 건수·응답·현재 DB snapshot이 없어 네 API 성공으로 표현하지 않는다. |
| 11. HTTP 200이면 수집 성공인가요? | 아니다. 오류 body·parse 문제를 concrete client가 빈/부분 목록으로 축소할 수 있고 상위 `failedSourceCount`가 이를 놓칠 수 있다. 실제 0건과 수집 실패를 구분할 typed result가 필요하다. |
| 12. 시설 수집과 점수 저장의 transaction은 같나요? | 아니다. 시설 DAO는 row별 update→insert이며 source snapshot transaction이 없고 stale row도 지우지 않는다. score stat upsert 경로만 transaction을 사용한다. |

### 답변하면 안 되는 과장 표현

- “네 안전시설 API가 상시 운영에서 항상 정상 수집됩니다.”
- “401의 단일 원인을 밝혀 완전히 해결했습니다.”
- “CCTV 403은 Cloud Run에서 발생했습니다.”
- “이 점수는 범죄 위험도 또는 지역 치안 수준입니다.”
- “300m와 500m를 parameter에 따라 동적으로 다시 계산합니다.”
- “부분 실패를 모두 정확히 감지합니다.”
- “Cloud Run에서 scheduler가 매월 정확히 한 번 동작하도록 보장했습니다.”
- “가중치는 통계적으로 검증됐습니다.”
- “안전 테스트 전략과 모든 테스트 코드를 제가 수작업으로 설계했습니다.”
- “CodeRabbit 자동 리뷰를 사람 동료의 승인 리뷰로 받았습니다.”

---

## 5. 기술 질문 15개

### 1. 왜 배치 또는 오프라인 적재 구조를 선택했나요?

공공 거래·안전시설 API의 지연, quota, 장애를 사용자 요청 경로에 넣지 않고 동일한 DB snapshot으로 지도와 분석을 제공하기 위해서입니다. 안전 점수도 거리 계산을 요청마다 반복하지 않고 `property_score_stat`에 미리 저장했습니다. 실제 latency 개선 수치는 측정하지 않았습니다. 거래 pipeline의 운영 scheduler는 없고, 안전 batch는 사용자가 2분 주기의 초 0/30 cron을 일시 활성화했다가 껐다고 답했습니다. 정확한 실행 횟수와 수집 완료→계산 순서는 확인되지 않아 상시 주기 실행으로 말하지 않습니다.

### 2. upsert와 멱등성의 차이는 무엇인가요?

upsert는 특정 unique key가 충돌했을 때 insert 대신 update하는 DB 쓰기 방식입니다. 멱등성은 같은 입력이나 요청을 여러 번 적용해도 관찰 가능한 최종 결과가 같다는 더 넓은 성질입니다. 이 프로젝트는 거래 DB write에서 `(source_api, source_transaction_key)` 충돌의 중복 insert를 막지만 fetch 호출, raw 파일, manifest, geocode, 실패 재처리까지 같은 상태를 보장하지 않습니다. 그래서 “중복 방지 upsert”라고 말하고 파이프라인 전체 멱등성·exactly-once라고 하지 않습니다.

### 3. 충돌 키는 어떻게 정했나요?

원천 API 전체에 공통인 안정적 거래 ID가 없어 source, 법정동·지번, 건물명/키, 계약 연월·일, 면적, 층, 보증금·월세·매매가를 조합해 결정적 SHA-1 key를 만들었습니다. source까지 포함해 서로 다른 API의 우연한 동일 거래가 섞이지 않게 했습니다. 정정·취소 거래가 기존 key와 어떤 관계인지, hash 충돌을 어떻게 감사할지는 남은 과제입니다.

### 4. 트랜잭션 범위는 어디인가요?

`load_supabase`에서 `transaction_history`, `region_price_stat`, `building_price_stat`, `properties`의 batch upsert가 한 psycopg connection을 공유하고 마지막에 한 번 commit합니다. 따라서 그 적재 호출 안의 DB write는 함께 commit/rollback될 수 있습니다. migration, raw fetch, 정규화 파일 생성, geocoding은 이 DB transaction 밖입니다. 사용자는 당시 Supabase 적재를 확인했다고 답했지만 rollback fault-injection 자료와 당시·현재 DB count는 없습니다.

### 5. API별 client를 왜 분리했나요?

안전시설 source마다 JSON/XML, URL·pagination, key와 encoding, field alias, 좌표계가 달랐습니다. 이를 하나의 client에서 조건문으로 처리하면 한 source 변경이 다른 source 회귀로 번질 수 있습니다. source client/parser는 외부 계약을 공통 `SafetyFacility`로 번역하고, ingestion과 점수 서비스는 source 세부사항을 모르도록 분리했습니다.

### 6. Haversine 공식을 선택한 이유는 무엇인가요?

phase 범위에서 공간 extension을 도입하지 않고 위·경도 두 점의 구면 근사 거리를 Java에서 계산할 수 있었기 때문입니다. 모든 시설에 적용하면 비싸므로 DB의 merged bbox로 후보를 줄인 뒤 사용했습니다. Haversine은 지구를 구로 근사하므로 고정밀 공간 분석을 보장하지 않으며, 300~500m MVP 비교 규칙에 적용한 구현입니다. PostGIS와의 정확도·성능 benchmark는 없습니다.

### 7. 좌표계 변환은 어디에서 수행했나요?

외부 source adapter 경계에서 수행했습니다. WGS84 위·경도는 그대로 사용하고, 보안등 응답에서 WGS84가 없을 때의 `XMAP/YMAP/GEOM` fallback만 EPSG:3857로 가정해 별도 GIS library 없이 Java `Math` 역식으로 바꿉니다. fixture 허용오차와 전지구 범위만 검증했으며 한국 영역 sanity check나 provider의 live CRS 전체를 증명한 것은 아닙니다. DB와 점수 계산 코드는 공통 좌표만 봅니다.

### 8. Spring과 FastAPI의 책임을 어떻게 분리했나요?

Spring은 JWT 인증, 사용자·매물·거래·가격·안전 도메인 API와 공개 오류 계약을 담당합니다. FastAPI는 LangGraph worker, LLM 호출, pgvector 유사도 검색을 담당합니다. Frontend는 Spring만 호출하고 Spring이 내부 키로 FastAPI를 호출합니다. 선택 매물 가격·안전 분석은 Spring GET API를 사용하고, 매물 검색·지역 시세·법률 vector 검색은 FastAPI가 Supabase를 직접 조회합니다. 현재 FastAPI→Spring 공개 GET에는 별도 내부 key가 없다는 점도 함께 설명합니다.

### 9. DTO 계약 불일치를 어떻게 방지할 것인가요?

producer와 consumer가 각자 비슷한 이름의 DTO를 수기로 유지하는 방식을 끝내야 합니다. 공개할 필드와 optional/required 의미를 정한 뒤 FastAPI OpenAPI 또는 별도 versioned schema를 단일 계약 원천으로 두고, 실제 producer JSON fixture를 Spring `AiAgentClient`가 역직렬화하는 consumer test와 Frontend normalizer test를 함께 실행하겠습니다. 계약 검사를 CI 배포 선행 조건으로 둡니다.

### 10. OpenAPI와 공유 schema의 장단점은 무엇인가요?

OpenAPI는 HTTP endpoint, request/response, validation을 문서화하고 client/DTO 생성에 활용하기 좋으며 FastAPI가 자연스럽게 산출할 수 있습니다. 하지만 생성 코드 갱신과 호환성 정책을 지키지 않으면 spec만 최신이고 consumer가 뒤처질 수 있습니다. JSON Schema·Proto 같은 공유 schema는 타입 원천을 더 명확히 할 수 있지만 Java·Python·JavaScript 빌드 체계에 생성·배포 단계를 추가합니다. 어떤 형식이든 실제 consumer 역직렬화 test와 versioning이 없으면 drift를 완전히 막지 못합니다.

### 11. contract test를 어떻게 작성할 것인가요?

FastAPI의 non-empty `workersCalled`, `toolResults`, 카드와 의도적으로 정의한 `intent` 정책을 포함하는 versioned contract case를 만듭니다. 내부 응답 fixture는 MockWebServer나 WireMock이 `/internal/agent/chat`에서 반환하고, 실제 `AiAgentClient.sendMessage`를 호출해 기대하는 Spring 공개 `ChatResponse` fixture로 변환되는지 검증합니다. Frontend `chat-normalizer` test는 이 공개 응답 fixture를 읽습니다. 필수 필드 누락·unknown enum·null·빈 배열·추가 필드의 호환성도 테스트하고 deploy job이 이 test를 `needs`로 의존하게 합니다. 이는 앞으로 추가할 설계이며 현재 수행된 contract test라고 말하지 않습니다.

### 12. pgvector 검색은 일반 SQL 검색과 무엇이 다른가요?

일반 equality·LIKE 검색은 값이나 문자열 조건이 명시적으로 일치하는 행을 찾는 반면, pgvector는 query embedding과 저장 embedding 사이의 거리로 의미상 가까운 chunk를 순위화합니다. 이 프로젝트는 `vector(1536)`, cosine 거리 `<=>`, 기본 top-k 3과 IVFFlat index를 사용합니다. 사용자는 법률 데이터가 Supabase에 남아 있을 것으로 예상한다고 답했지만 현재 row·원문·embedding model을 조회하지 않았으므로 데이터 현존 사실로 확정하지 않습니다. threshold·법령/시행일 filter·reranker·품질 평가도 없습니다.

### 13. prompt-level grounding의 한계는 무엇인가요?

검색된 최대 세 법률 card의 문맥만 사용하라고 prompt에 넣고 결과가 없을 때 최종 법률 답변용 LLM 호출을 생략하는 것은 답변 범위를 좁히는 장치입니다. 하지만 모델이 실제로 문맥만 사용했는지 사후 검증하지 않고, 검색 자체가 틀리거나 오래된 법령이면 답변도 틀릴 수 있습니다. 사용자는 사람이 직접 평가하지 않았고, 평가가 있었다면 AI가 했을 것이라고 불확실하게 기억합니다. 보존된 평가 결과가 없으므로 “환각 방지”나 정확성 개선 수치는 사용하지 않습니다.

### 14. fallback이 장애를 숨길 가능성은 없나요?

있습니다. 법률 RAG의 비운영 fallback은 `psycopg.OperationalError`에서 조건이 맞으면 REST로 전체 row를 페이지당 1,000개씩 읽어 메모리 cosine을 계산합니다. 개발 편의는 높이지만 데이터가 커질수록 latency·메모리가 늘고, fallback인데도 provenance가 `supabase-pgvector`로 남는 문제도 있습니다. 안전 client도 오류를 빈 목록으로 바꿔 실패를 0건처럼 보이게 할 수 있습니다. fallback은 typed result, metric, 명확한 환경 제한과 함께 사용해야 합니다.

### 15. 운영 환경과 개발 환경 설정을 어떻게 분리할 것인가요?

API key·DB URL·내부 key·모델·timeout은 환경변수와 secret manager로 주입하고 코드에 기본 비밀값을 두지 않습니다. profile은 기능과 실패 정책을 분리하되, 운영에서는 개발용 전체-row REST fallback처럼 장애를 숨길 수 있는 경로를 비활성화합니다. startup validation으로 필수 설정 누락을 즉시 실패시키고, source별 opt-in과 설정 상태를 metric에 남기며, 실제 배포 값은 저장소 기본값과 다를 수 있음을 문서화합니다.

---

## 6. 기여도·테스트 질문 8개

### 1. 정말 혼자 구현했나요?

프로젝트 전체는 2인 공동 작업입니다. 역할은 Frontend/Backend로 고정하지 않고 F-N 기능 단위로 나눴고, 사용자는 주로 F-1·F-3·F-4와 그 기능에 필요한 Spring·FastAPI·Vue·DB 작업을 맡았다고 답했습니다. Git으로 단독 성과를 확인할 수 있는 범위는 거래 pipeline의 endpoint 설정·normalizer·충돌 키·upsert, 지도 zoom API와 keyword 통합, 법률 ingestion·pgvector 검색·prompt grounding, Spring–FastAPI 선택 매물 계약과 초기 카드 연동, 네 안전시설 client·좌표 변환·거리 사전 계산, Spring/FastAPI 배포 workflow입니다. JWT core, LangGraph Supervisor, 최종 챗봇·세션 UI와 최종 안전 카드 UI는 팀원 기여입니다.

### 2. 팀원과 어떤 방식으로 역할을 나눴나요?

사용자 답변상 작은 기능을 고른 뒤 그 기능의 Frontend·Backend·DB까지 이어서 맡는 방식이었고, Git diff에서도 팀원은 인증 core·Supervisor·후속 UI 고도화, 저는 데이터·Spring 도메인 API·서비스 간 계약·외부 API adapter·초기 화면 연동을 주로 맡은 형태가 확인됩니다. Issue와 PR 단위로 모노레포에서 통합했고 리뷰 기록은 CodeRabbit 자동 리뷰가 중심입니다. 최종 기획은 5~6월, Git 검증 기간은 2026-06-12~06-26입니다. 2~3월 소규모 작업과 전면 재구성, GitLab 이력 소실은 사용자 직접 답변이라 Git 사실과 분리합니다. 회의 주기·발표 성과는 여전히 미확인입니다.

### 3. 본인이 가장 많이 기여한 부분은 무엇인가요?

기여율을 숫자로 말하지는 않겠습니다. 가장 깊게 설명할 수 있는 부분은 이질적인 외부 데이터를 공통 모델과 DB 계약으로 바꾸는 일, Spring과 FastAPI의 책임 경계를 연결하는 일, 요청 시 비용이 큰 시설 거리 계산을 배치 사전 계산으로 옮긴 일입니다. 각 영역에서 Issue, PR, 현재 코드와 한계를 직접 열어 설명할 수 있습니다.

### 4. 프론트엔드 코드를 직접 구현했나요?

네. 지도 API 호출·렌더링, 선택 매물 ID 전송, 초기 legal/analysis card normalizer와 rendering은 직접 구현했습니다. 다만 최종 지도 필터 UI와 최종 챗봇 markup·style·세션 UX, 최종 안전 카드 UI는 팀원이 후속 고도화했습니다. 그래서 “프론트 전체 구현”이 아니라 “백엔드 계약을 소비하는 초기 연동”으로 설명합니다.

### 5. AI 기능은 어느 정도 직접 구현했나요?

법률 chunk ingestion, OpenAI-compatible embedding 호출, pgvector cosine 검색, 근거 card와 prompt-level grounding, 비운영 fallback, FastAPI의 Spring 조회 client와 가격·안전 worker 연결 일부를 구현했습니다. LangGraph Supervisor 자체는 팀원 구현입니다. 사용자는 법률 데이터가 Supabase에 남아 있을 것으로 예상하지만 확신하지 못했고 사람 평가도 하지 않았다고 답했습니다. 따라서 현재 데이터 현존, 검색 정확도, 환각 방지 효과는 성과로 주장하지 않습니다.

### 6. 최종 UI를 누가 구현했나요?

제가 선택 매물 전달과 초기 법률·분석 카드 계약 및 표시 경로를 만들었고, 팀원이 최종 챗봇 디자인·세션 UX와 최종 안전 카드 UI를 고도화했습니다. 현재 화면은 두 사람의 연속된 변경 결과이므로 공동 결과로 표현합니다.

### 7. 테스트를 직접 설계하고 작성했나요?

사용자 직접 답변상 관련 테스트 코드는 Codex가 생성했습니다. Git은 별도로 사용자 계정 commit, 과거 PR 실행 결과, CodeRabbit 지적과 후속 수정을 보여주지만 두 근거가 가리키는 정확한 파일·case는 연결하지 못했습니다. 사람이 어떤 case를 설계·검토했는지도 특정하지 못하므로 “TDD로 테스트를 직접 설계·작성했다”거나 “Codex 생성물을 특정 PR에 통합했다”고 단정하지 않습니다. 대신 확인 가능한 테스트 실행 경계와 실제 consumer contract test가 빠졌다는 한계를 설명합니다.

### 8. 현재 테스트는 실제로 통과하나요?

2026-07-14 로컬 검수 실행 기준으로 현재 HEAD의 Spring 77개, Frontend 26개, FastAPI 61개 테스트가 통과했습니다. 이 숫자는 모듈 test 결과이며 Spring `ChatControllerTest`가 service를 mock하고 FastAPI·Frontend도 fake/fixture를 사용하므로 서비스 간 E2E 증거는 아닙니다. FastAPI에서는 TestClient deprecation warning 1건도 확인했습니다.

---

## 7. 기술 부채 집중 질문 — `workersCalled`와 `intent` 계약 불일치

### 현재 문제 설명

FastAPI `AgentChatResponse`는 다음 필드를 반환한다.

```text
workersCalled: list[str] = []
answer: str
properties: list = []
legalCards: list = []
analysisCards: list = []
toolResults: dict = {}
nextActions: list = []
```

Spring `AiAgentClient.AgentChatResponse`는 다음 nullable 필드를 선언한다.

```text
intent: String
answer: String
properties: List
legalCards: List
analysisCards: List
```

따라서 FastAPI에만 있는 `workersCalled`, `toolResults`, `nextActions`는 Spring 경계에서 소비되지 않고, Spring에만 있는 `intent`는 `null`이 된다. Spring 공개 `ChatResponse`도 worker metadata를 노출하지 않으며 Frontend normalizer는 `intent`가 null이면 빈 문자열로 바꾼다. PR #63 이후 양쪽 consumer를 함께 갱신한 근거가 없고 실제 HTTP consumer contract test도 없다.

### 왜 전체 장애가 아닐 수 있는가

현재 `RestClient.builder()`의 기본 Jackson converter는 알 수 없는 최상위 JSON 필드를 무시합니다. FastAPI `answer`와 카드 필드가 Spring record의 이름·type과 맞으면 메시지와 일부 카드는 역직렬화될 수 있고, nullable `intent`는 null이 되어 Frontend에서 빈 문자열로 바뀝니다. 반면 카드 내부 type drift는 전체 변환 실패가 될 수 있고 실제 HTTP consumer test도 없습니다. 따라서 정적 metadata 유실은 확인되지만 모든 채팅의 성공·실패와 실제 화면 영향은 단정하지 않습니다.

### 어떤 데이터가 유실될 수 있는가

- `workersCalled`: 실제 호출된 worker 목록. public API 문서에도 있어 확인된 public contract drift다.
- `toolResults`: FastAPI 내부 결과가 생겨도 Spring이 전달하지 않는다. 다만 Spring 공개 API의 필수 필드였다는 근거는 없다.
- `nextActions`: Spring에서 전달되지 않는다. 현재 graph는 기본 빈 배열이어서 현재 데이터 유실 사고라기보다 미래 확장 gap에 가깝다.
- `intent`: producer에 없으므로 Spring에서는 `null`, Frontend에서는 `''`가 된다.
- `answer`·properties·cards: 공통 필드라 보존될 수 있다. 실제 모든 payload 조합의 E2E 성공은 별도 확인이 필요하다.

### 어떻게 재현할 것인가

1. FastAPI schema와 같은 JSON fixture를 만든다. `workersCalled`에는 `PRICE_ANALYSIS`처럼 non-empty 값을 넣고, `answer`와 `analysisCards`도 넣으며 `intent`는 넣지 않는다.
2. MockWebServer 또는 WireMock에서 `/internal/agent/chat` 요청에 이 fixture를 반환한다.
3. 실제 `AiAgentClient.sendMessage`를 호출한다.
4. 반환된 Spring `ChatResponse`에서 message/card는 존재하지만 `intent`는 null이고 worker metadata를 담을 필드 자체가 없음을 확인한다.
5. 이 Spring 공개 응답을 `ApiResponse.data`에 담아 `frontend/src/api/chat-normalizer.js`에 넣고, `intent`가 빈 문자열이 되며 worker 목록을 소비할 필드가 없음을 확인한다.

현재 코드에 이 재현을 이미 수행한 테스트가 있다고 말하지 않는다. 위 절차는 추가할 재현 설계다.

### 어떻게 테스트할 것인가

1. **Producer schema test**: FastAPI OpenAPI와 `AgentChatResponse`가 required/optional, alias, 기본값을 유지하는지 검증한다.
2. **Spring consumer contract test**: versioned FastAPI 내부 응답 fixture를 실제 `AiAgentClient`가 HTTP로 받아 역직렬화하고 기대하는 Spring 공개 `ChatResponse` fixture로 변환하게 한다.
3. **Frontend consumer test**: 같은 contract case에 짝지은 Spring 공개 `ApiResponse` fixture로 normalizer가 metadata·null·빈 배열을 의도대로 처리하는지 검증한다.
4. **호환성 case**: 필수 필드 누락, additive field, unknown worker enum, null, 빈 배열, non-empty metadata를 각각 넣는다.
5. **CI gate**: Spring test, FastAPI test, Frontend test/build를 통과한 동일 commit artifact만 배포한다. 현재 workflow는 이 gate가 아니다.

### 어떻게 수정할 것인가

첫째, 제품에 공개할 metadata를 결정합니다. worker 실행 이력과 후속 행동이 UI·analytics에 필요하다면 Spring 내부·공개 DTO와 Frontend model에 `workersCalled`, 필요한 `toolResults`, `nextActions`를 명시합니다. 외부에 공개하면 안 되는 tool raw data라면 Spring 경계에서 의도적으로 제거하고 그 정책을 schema에 기록합니다.

둘째, `intent`의 소유권을 결정합니다. FastAPI가 routing 결과를 안정적인 public intent로 제공할지, 아니면 Spring과 Frontend에서 필드를 제거할지 한 방향을 선택합니다. 지금처럼 producer에는 없고 consumer만 기대하게 두지 않습니다.

셋째, OpenAPI 또는 versioned JSON Schema를 기준으로 DTO를 생성하거나 검증하고, 내부 응답과 기대 공개 응답을 한 contract case로 묶은 consumer test를 CI gate에 넣습니다. field 이름만 고치는 일로 끝내지 않고 같은 유형의 조용한 유실을 막습니다.

### 다시 설계한다면 어떻게 할 것인가

- 외부 공개 응답과 내부 agent 응답을 별도 version으로 정의한다.
- `answer`, `cards`, `execution metadata`를 명시적 하위 객체로 나누고 각 필드의 공개 여부·nullable·기본값을 정한다.
- FastAPI OpenAPI를 artifact로 versioning하고 Spring/Frontend 생성 또는 검증 작업을 빌드에 포함한다.
- correlation ID, schema version, 호출 worker와 단계별 latency를 서비스 경계 로그에 남긴다.
- 전체 chat deadline을 먼저 정한 뒤 Spring→FastAPI, FastAPI→Spring, LLM에 하위 budget을 배분하고 취소를 전파한다.
- 독립적인 매물 상세·거래·가격 조회는 병렬화하거나 선택 매물 분석 aggregation API로 합친다.
- 현재 가장 먼저 적용할 순서는 schema 정렬 → 실제 consumer 역직렬화 test → CI gate → latency budget 개선이다.

### 이 부채를 1분 안에 설명하는 답변

“현재 코드를 producer와 consumer 관점에서 다시 대조하면서 FastAPI가 반환하는 `workersCalled`가 Spring DTO에 없어 유실되고, 반대로 Spring은 producer에 없는 nullable `intent`를 선언한다는 점을 발견했습니다. 현재 기본 converter에서 이름·type이 맞는 `answer`와 카드는 남을 수 있지만 실제 HTTP consumer test가 없어 전체 채팅 장애나 성공을 단정할 수는 없습니다. 저는 이를 이미 해결했다고 말하지 않고, FastAPI OpenAPI나 versioned contract case를 원천으로 두고 실제 `AiAgentClient` 역직렬화 결과와 Frontend normalizer를 연속 검증한 뒤 CI 배포 gate에 넣는 것이 우선 개선이라고 설명하겠습니다.”

---

## 8. 마지막 점검표

면접 직전에는 각 답변을 다음 기준으로 줄여 말한다.

- 8개 source 실행 범위를 세종 제외 16개 시·도·267개 `LAWD_CD` 조회 코드·12개 월 파티션으로 말했는가?
- 25,632개 기본 요청, 321개 추가 page, XML 25,953개를 서로 다른 숫자로 설명했는가?
- raw item과 정규화 row의 차이를 원래 run counter가 아니라 HEAD normalizer의 사후 replay로 분리했다고 밝혔는가? 132,228을 실제 중복 거래 수라고 부르지 않았는가?
- 합성 매물 4,000행을 기억 속 8,000개나 실제 중개 매물로 바꾸지 않았는가?
- 과거 Supabase 적재 사용자 답변과 당시·현재 DB count 미확인을 구분했는가?
- upsert 범위와 전체 멱등성을 구분했는가?
- 기능 단위 F-1·F-3·F-4 역할 기억과 Git으로 확인한 세부 diff를 구분했는가?
- 5~6월 최종 기획, Git 6/12~6/26, 2~3월·GitLab 이력 소실의 근거 등급을 구분했는가?
- JWT core·Supervisor·최종 UI를 팀원 기여로 분리했는가?
- FastAPI→Spring GET이 현재 별도 내부 key를 쓰지 않는다고 정확히 말했는가?
- `workersCalled` drift를 해결했다고 말하지 않았는가?
- 선택 채팅의 실제 사용자 영향은 모른다는 답변을 장애 사례로 확대하지 않았는가?
- 안전 지표를 시설 접근성 proxy로 설명했는가?
- 안전 가중치를 개인 heuristic으로 말하고 수학·통계 근거를 만들지 않았는가?
- CCTV cap이 카메라 대수나 검증된 고유 설치지점 수가 아니라 source row 기준이라고 설명했는가?
- Haversine을 실제·정확한 거리라고 부르지 않고 구면 근사라고 했는가?
- 403, Cloud Run 401, key 오류를 하나의 원인으로 합치지 않았는가?
- Q6의 Codex 테스트 생성 답변을 대상이 특정되지 않은 다른 테스트 전체로 확대하지 않았는가?
- CodeRabbit 자동 리뷰와 배포 후 사용자 직접 확인을 사람 리뷰·보존 운영 로그로 바꾸지 않았는가?
- 일시 Cloud Run batch 답변을 정확히 1회·수집 완료 30초 후 계산·계속 켜진 월간 scheduler로 바꾸지 않았는가?
- 경찰 opt-in 누락과 source 설정 충돌 가능성을 숨긴 채 네 API 성공을 주장하지 않았는가?
- 법률 데이터 현존 예상과 사람 평가 부재를 정확히 말했는가?
- 확인할 수 없는 사용자 수·시연 결과·협업 방식·운영 row 수를 만들지 않았는가?

## 근거 바로가기

- 거래 파이프라인: Issue #7/#32, PR #8/#33, `scripts/data_pipeline/pipeline.py`, `salmanhae-f1-molit-pipeline-20260624/manifest.json`, `raw/molit/`, `normalized/`, `generated/`, `lite/`
- 서비스 계약: Issue #36/#38/#40/#45/#47/#49, PR #37/#39/#41/#46/#48/#50/#63, `AiAgentClient.java`, `backend-ai/app/api/schemas.py`, `backend-ai/app/clients/spring_client.py`, `frontend/src/api/chat-normalizer.js`
- 안전시설: Issue #68/#70/#72/#74/#76/#78/#90/#92, PR #69/#71/#73/#75/#77/#79/#91/#93, `PropertySafetyScoreServiceImpl.java`, `SafetyFacilityIngestionServiceImpl.java`, `service/safety/ingest/*Client.java`
- 기여 경계와 기술 부채: `09-contribution-boundaries.md`, `13-technical-debt-and-limitations.md`
- 사용자 직접 답변과 충돌 기록: `12-confirmation-questions.md`
