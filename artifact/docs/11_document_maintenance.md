# 11. 문서 보강 기준

이 문서는 개발을 진행하면서 어떤 상황에서 어떤 문서를 수정하면 좋은지 정리한 문서입니다.

문서는 한 번에 완성하는 산출물이 아니라, 백엔드와 프론트엔드 구현이 구체화될 때 함께 갱신하는 기준서입니다. 구현 내용이 문서와 달라졌다면 코드만 맞추지 말고 관련 문서도 함께 수정합니다.

## 문서 수정 원칙

- MVP 범위가 바뀌면 `README.md`, `02_mvp_scope.md`, `09_development_roadmap.md`를 함께 확인합니다.
- API 요청/응답 형식이 바뀌면 `06_rest_api_spec.md`를 먼저 수정합니다.
- DB 테이블, 컬럼, enum, 인덱스가 바뀌면 `05_domain_model.md`를 수정합니다.
- 외부 API나 배치 수집 방식이 바뀌면 `03_external_apis.md`, `07_batch_ingestion.md`를 함께 수정합니다.
- 로그인, 권한, 공개 API 범위가 바뀌면 `08_security_policy.md`를 수정합니다.
- 장기 아이디어나 시장조사 내용은 `docs`가 아니라 `research`에 정리합니다.

## 상황별 수정 문서

| 상황 | 우선 수정 문서 | 함께 확인할 문서 |
| --- | --- | --- |
| MVP 포함/제외 기능이 바뀜 | `02_mvp_scope.md` | `README.md`, `09_development_roadmap.md`, `10_future_extensions.md` |
| API 엔드포인트가 추가됨 | `06_rest_api_spec.md` | `08_security_policy.md`, `09_development_roadmap.md` |
| API 요청 파라미터나 응답 JSON이 바뀜 | `06_rest_api_spec.md` | 프론트 화면 설계 문서 |
| 공개 API가 로그인 필요 API로 바뀜 | `08_security_policy.md` | `06_rest_api_spec.md` |
| DB 테이블이나 컬럼이 추가됨 | `05_domain_model.md` | `07_batch_ingestion.md` |
| enum 값이 추가되거나 이름이 바뀜 | `05_domain_model.md` | `06_rest_api_spec.md` |
| 지도 좌표 검색 방식이 바뀜 | `06_rest_api_spec.md` | `04_backend_architecture.md`, `05_domain_model.md` |
| 실거래가 매칭 기준이 바뀜 | `07_batch_ingestion.md` | `06_rest_api_spec.md`, `05_domain_model.md` |
| 안전 점수 산식이 바뀜 | `07_batch_ingestion.md` | `05_domain_model.md`, `06_rest_api_spec.md` |
| 외부 API 원천이 추가/제외됨 | `03_external_apis.md` | `07_batch_ingestion.md` |
| 배치 주기나 import 방식이 바뀜 | `07_batch_ingestion.md` | `03_external_apis.md` |
| 백엔드 패키지 구조가 정해짐 | `04_backend_architecture.md` | `09_development_roadmap.md` |
| 프론트 화면 구조가 정해짐 | 새 화면 설계 문서 | `06_rest_api_spec.md` |
| 에러 응답 규격이 정해짐 | `06_rest_api_spec.md` | `08_security_policy.md` |
| 커뮤니티나 AI 챗봇을 MVP로 당김 | `02_mvp_scope.md` | `08_security_policy.md`, `10_future_extensions.md` |

## 나중에 보강하면 좋은 문서

### 04_backend_architecture.md

백엔드 기본 프로젝트를 만든 뒤 실제 패키지 구조를 추가합니다.

예시:

```txt
com.salmanhae
  ├─ property
  ├─ transaction
  ├─ safety
  ├─ risk
  ├─ recommendation
  ├─ batch
  └─ common
```

추가하면 좋은 내용:

- controller, service, mapper, dto, entity 위치
- 공통 응답 포맷
- 예외 처리 구조
- MyBatis mapper XML 위치
- 배치 Job 구성

### 05_domain_model.md

실제 DB 설계가 시작되면 DDL 수준으로 보강합니다.

추가하면 좋은 내용:

- 컬럼 타입
- nullable 여부
- 기본값
- 인덱스
- unique 제약
- 외래키 관계
- seed 데이터 기준

### 06_rest_api_spec.md

프론트 목업과 백엔드 API 구현이 시작되면 가장 자주 수정될 문서입니다.

추가하면 좋은 내용:

- 공통 응답 포맷
- 공통 에러 응답
- 페이지네이션 규칙
- 정렬 규칙
- 필터 파라미터
- 프론트에서 사용하는 화면별 API 호출 순서

에러 응답 예시:

```json
{
  "code": "PROPERTY_NOT_FOUND",
  "message": "매물을 찾을 수 없습니다.",
  "status": 404
}
```

### 07_batch_ingestion.md

외부 데이터를 실제로 붙이기 시작하면 수집 실패와 중복 처리 기준을 보강합니다.

추가하면 좋은 내용:

- 배치 Job 이름
- 수동 실행 방법
- 실패 재시도 기준
- 중복 upsert 기준
- 마지막 수집 시각 저장 방식
- 좌표 없는 데이터 처리 기준

### 프론트 화면 설계 문서

프론트 목업을 만들기 시작하면 별도 문서를 추가하는 것이 좋습니다.

추천 파일명:

```txt
12_frontend_screen_flow.md
```

추가하면 좋은 내용:

- 메인 지도 화면 구성
- 매물 상세 드로어 구성
- 안전시설 레이어 토글
- 실거래가 차트
- 위험도 계산 패널
- 추천 패널
- 화면별 호출 API
- 로딩/빈 상태/에러 상태

## 커밋 전 확인 체크리스트

- 기능 범위 변경이 MVP 문서에 반영되었는가?
- API 변경이 `06_rest_api_spec.md`에 반영되었는가?
- DB 변경이 `05_domain_model.md`에 반영되었는가?
- 외부 데이터/배치 변경이 `03_external_apis.md` 또는 `07_batch_ingestion.md`에 반영되었는가?
- 인증 정책 변경이 `08_security_policy.md`에 반영되었는가?
- 구현 기준 문서와 research 문서의 역할이 섞이지 않았는가?
