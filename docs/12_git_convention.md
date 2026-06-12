# 12. Git 협업 컨벤션

## 브랜치 전략

```
main ← develop ← feature/*, fix/*, docs/*, refactor/*
```

| 브랜치 | 용도 |
|--------|------|
| `main` | 배포 가능 상태 유지 |
| `develop` | 통합 브랜치 — 기능 브랜치들의 merge 대상 |
| `feature/*` | 신규 기능 구현 |
| `fix/*` | 버그 수정 |
| `refactor/*` | 동작 변경 없는 코드 개선 |
| `docs/*` | 문서 변경 |

### 브랜치 네이밍

```
feature/{stage번호}-{slug}
fix/{slug}
refactor/{slug}
docs/{slug}
```

**예시**
```
feature/1-property-api
feature/2-safety-layer
fix/map-marker-duplicate
refactor/house-dao-query
docs/update-api-spec
```

---

## 커밋 메시지

```
type(scope): 한글 설명
```

### type

| type | 설명 |
|------|------|
| `feat` | 새 기능 |
| `fix` | 버그 수정 |
| `refactor` | 동작 변경 없는 코드 개선 |
| `test` | 테스트 추가/수정 |
| `docs` | 문서 변경 |
| `chore` | 빌드, 설정, 패키지 변경 |
| `style` | 포매팅 (기능 무관) |

### scope

| scope | 설명 |
|-------|------|
| `be` | 백엔드 전반 |
| `fe` | 프론트엔드 전반 |
| `property` | 매물 도메인 |
| `safety` | 안전시설 도메인 |
| `transaction` | 실거래가 도메인 |
| `auth` | 인증/인가 |
| `chat` | AI 챗봇/에이전트 |
| `wishlist` | 찜하기 |
| `db` | DB 스키마/마이그레이션 |
| `batch` | 배치/공공데이터 수집 |

### 예시

```
feat(property): 지도 범위 내 매물 조회 API 구현
feat(safety): CCTV·비상벨 레이어 토글 기능 추가
fix(property): 지도 범위 파라미터 누락 시 400 응답 처리
test(property): HouseInfoDAO 단위 테스트 추가
chore(be): Spring Boot 3.x 의존성 세팅
refactor(fe): mapStore 더미 데이터 → axios API 호출로 교체
docs: REST API 명세 v1 업데이트
```

---

## 이슈

### 라벨 구성

| 카테고리 | 라벨 |
|----------|------|
| **타입** | `feature` `bug` `test` `refactor` `docs` `chore` |
| **영역** | `frontend` `backend` `db` `ai` `batch` |
| **단계** | `stage-1` ~ `stage-9` |
| **우선순위** | `priority-high` `priority-mid` `priority-low` |

### 이슈 제목

```
[TYPE][F-N] 설명       ← 기능 작업
[TYPE] 설명            ← F-N 없는 작업
```

**예시**
```
[FEAT][F-1] 지도 범위 내 매물 조회 API
[FEAT][F-2] AI 에이전트 의도 분류 노드 구현
[BUG][F-6] 로그인 토큰 만료 시 리다이렉트 안됨
[TEST][F-1] PropertyService 단위 테스트
[CHORE] Spring Boot 프로젝트 초기 세팅
```

### 이슈 본문 템플릿

```markdown
## 목표
무엇을 구현 / 수정할지 한 줄 설명

## 작업 범위
- [ ] 세부 항목 1
- [ ] 세부 항목 2

## 참고
- 관련 문서: docs/06_rest_api_spec.md
- 관련 API: GET /api/v1/properties
```

---

## PR

### 제목

커밋 메시지와 동일한 형식 사용

```
feat(property): 지도 범위 내 매물 조회 API 구현
```

### 본문 템플릿

```markdown
## 변경 내용
- 구현/수정한 내용 목록

## 연결 이슈
closes #이슈번호

## 테스트
- [ ] 단위 테스트 통과
- [ ] 로컬 동작 확인
- [ ] API 응답 형식 명세 일치 확인 (06_rest_api_spec.md)
```

### 규칙

- **1 PR = 1 이슈 = 1 stage 작업 단위** 원칙
- 셀프 머지 금지 — 상대방 approve 후 merge
- `develop` ← feature 머지 시 **Squash and merge** 사용
- `main` ← develop 머지 시 **Merge commit** 사용

---

## 단계별 이슈·브랜치 매핑

로드맵(09_development_roadmap.md) 기준

| 단계 | 이슈 제목 | 브랜치 |
|------|-----------|--------|
| 1단계 | [FEAT][F-1] 더미 매물 API + 지도 연동 | `feature/1-property-api` |
| 2단계 | [FEAT][F-1] 안전시설 API + 레이어 | `feature/2-safety-api` |
| 3단계 | [FEAT][F-1] 실거래가 API + 레이어 | `feature/3-transaction-api` |
| 4단계 | [FEAT][F-1] 안전 점수 계산 | `feature/4-safety-score` |
| 5단계 | [FEAT][F-6] 인증 (Supabase Auth) | `feature/5-auth` |
| 6단계 | [FEAT][F-2] AI 에이전트 — 매물 추천 | `feature/6-ai-recommend` |
| 7단계 | [FEAT][F-3] AI 에이전트 — 법률 RAG | `feature/7-ai-legal-rag` |
| 8단계 | [FEAT][F-4] AI 에이전트 — 시세·안전 분석 | `feature/8-ai-analysis` |
| 9단계 | [FEAT][F-7] 찜하기 | `feature/9-wishlist` |

> 한 단계가 fe/be 양쪽 작업을 포함할 경우 이슈를 fe/be 두 개로 분리하고 같은 브랜치 prefix 사용  
> 예: `feature/1-property-api-be`, `feature/1-property-api-fe`
