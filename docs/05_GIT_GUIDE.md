# 05. GIT_GUIDE

## 브랜치 전략

```
main ← develop ← phase/*, feature/*, fix/*, refactor/*, docs/*
```

| 브랜치 | 관리 주체 | 용도 |
|--------|-----------|------|
| `main` | 수동 | 배포 가능 상태 유지 |
| `develop` | 수동 | 통합 브랜치 — 기능 브랜치들의 merge 대상 |
| `phase/*` | **execute.py 자동** | Harness Phase 단위 작업 |
| `feature/*` | 수동 | 신규 기능 구현 |
| `fix/*` | 수동 | 버그 수정 |
| `refactor/*` | 수동 | 동작 변경 없는 코드 개선 |
| `docs/*` | 수동 | 문서 변경 |

### 브랜치 네이밍

```
phase/{N}-{slug}          ← execute.py 자동 생성
feature/{stage번호}-{slug}
fix/{slug}
refactor/{slug}
docs/{slug}
```

### Merge 방식

| 방향 | 방식 |
|------|------|
| `phase/*` → `develop` | Squash merge |
| `feature/*` → `develop` | Squash merge |
| `fix/*` → `develop` | Squash merge |
| `develop` → `main` | Merge commit |

셀프 머지 금지 — Phase PR 포함 상대방 approve 후 merge.

---

## 커밋 메시지

```
type(scope): 한글 설명 (#이슈번호)        ← 수동 커밋
type(scope): 한글 설명 (#이슈번호) [ai]   ← execute.py 자동 커밋
```

이슈 번호는 항상 포함한다. execute.py가 Phase 커밋에 자동 삽입한다.

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
| `ai` | AI 백엔드 전반 |
| `property` | 매물 도메인 |
| `safety` | 안전시설 도메인 |
| `transaction` | 실거래가 도메인 |
| `auth` | 인증/인가 |
| `chat` | AI 챗봇/에이전트 |
| `wishlist` | 찜하기 |
| `db` | DB 스키마/마이그레이션 |
| `batch` | 배치/공공데이터 수집 |

### `[ai]` 태그

execute.py가 Phase 완료 후 자동 생성하는 커밋에만 붙인다. 수동 커밋에는 붙이지 않는다.

```
feat(fe): 지도 컴포넌트 초기 구현 (#12) [ai]
fix(fe): 마커 팝업 z-index 수정 (#8)
test(be): PropertyService 단위 테스트 추가 (#9)
```

---

## 이슈

### 라벨

| 카테고리 | 라벨 |
|----------|------|
| 타입 | `feature` `bug` `refactor` `docs` `chore` |
| 영역 | `frontend` `backend` `backend-ai` `db` |
| 기능 | `F-1` ~ `F-8` |
| 우선순위 | `priority-high` `priority-mid` `priority-low` |
| AI 자동 | `ai-generated` |

### 이슈 제목

```
[FEAT][F-N] 설명        ← 수동
[BUG][F-N] 설명         ← 수동
[CHORE] 설명            ← 수동
[Phase N] {slug}        ← execute.py 자동 생성 (ai-generated 라벨)
```

### 이슈 본문 템플릿

```markdown
## 목표
무엇을 구현 / 수정할지 한 줄 설명

## 작업 범위
- [ ] 세부 항목 1
- [ ] 세부 항목 2

## 참고
- 관련 문서: docs/08_API_SPEC.md
```

---

## PR

### 제목

```
feat(property): 지도 범위 내 매물 조회 API 구현      ← 수동
[Phase N] feat(ai): LangGraph 의도분류 노드 구현 [ai] ← execute.py 자동
```

### 본문 템플릿

```markdown
## 변경 내용
- 구현/수정한 내용 목록

## 연결 이슈
closes #이슈번호    ← 수동 PR만 해당. Phase PR은 이슈 없음

## 테스트
- [ ] 단위 테스트 통과
- [ ] 로컬 동작 확인
- [ ] API 응답 형식 확인 (docs/08_API_SPEC.md)
```

---

## 작업 흐름

### Harness 방식 (AI 주도 — Phase 단위 구현)

```
1. /harness 입력
   → AI가 docs/ 읽고 Phase 계획 제안 → 승인
2. phases/{task}/ 에 Phase 파일 생성됨
3. python3 scripts/execute.py {task-name}
   → Phase마다 GitHub 이슈 자동 생성 (ai-generated 라벨)
   → phase/* 브랜치 자동 생성
   → Claude 헤드리스 모드로 Phase 순차 실행
   → Phase 완료 시 커밋 생성 (#이슈번호 포함, [ai] suffix)
   → PR 자동 생성 (closes #이슈번호)
4. Phase PR → 상대방 approve → develop merge
```

### 수동 방식 (개별 버그·리팩터링·문서 작업)

```
1. GitHub 이슈 생성
   gh issue create --title "[FEAT][F-1] 매물 마커 표시" --label "feature,frontend,F-1"
2. 브랜치 생성
   git checkout -b feature/1-property-api
3. 작업 (직접 or AI 활용)
4. 커밋
   git commit -m "feat(fe): 매물 마커 표시 구현 (#3)"
5. PR 생성
   gh pr create --title "feat(fe): 매물 마커 표시 구현" --body "closes #3"
```

### AI에게 코드를 짜달라고 할 때

맥락 문서를 먼저 읽힌다:

```
이 파일들을 먼저 읽어줘:
- docs/01_PRD.md
- docs/02_ARCHITECTURE.md
- docs/03_ADR.md
그 다음 [작업 내용] 구현해줘.
```

GitHub 작업(커밋, PR)은 AI에게 직접 시키지 말고 수동으로 처리한다.  
단, execute.py가 Phase 작업의 일환으로 커밋·PR을 생성하는 것은 허용한다.

---

## 단계별 브랜치 매핑 (MVP 로드맵 기준)

| 단계 | 이슈 제목 | 브랜치 |
|------|-----------|--------|
| 1 | [FEAT][F-1] 더미 매물 API + 지도 연동 | `feature/1-property-api` |
| 2 | [FEAT][F-1] 안전시설 API + 레이어 | `feature/2-safety-api` |
| 3 | [FEAT][F-1] 실거래가 API + 레이어 | `feature/3-transaction-api` |
| 4 | [FEAT][F-1] 안전 점수 계산 | `feature/4-safety-score` |
| 5 | [FEAT][F-6] 인증 (Supabase Auth) | `feature/5-auth` |
| 6 | [FEAT][F-2] AI 에이전트 — 매물 추천 | `feature/6-ai-recommend` |
| 7 | [FEAT][F-3] AI 에이전트 — 법률 RAG | `feature/7-ai-legal-rag` |
| 8 | [FEAT][F-4] AI 에이전트 — 시세·안전 분석 | `feature/8-ai-analysis` |
| 9 | [FEAT][F-7] 찜하기 | `feature/9-wishlist` |

한 단계가 fe/be/ai 양쪽 작업을 포함하면 이슈를 분리하고 같은 prefix 사용.  
예: `feature/1-property-api-be`, `feature/1-property-api-fe`
