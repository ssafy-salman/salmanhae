<p align="center">
  <img src="artifact/logo/salman_full_logo.png" alt="살만해" width="260" />
</p>

> AI 에이전트 기반 부동산 탐색 서비스

---

## 기술 스택

| 영역       | 기술                                                    |
| ---------- | ------------------------------------------------------- |
| Frontend   | Vue 3, Vite, Pinia, Axios, 네이버지도 SDK, Tailwind CSS |
| Backend    | Spring Boot 3, Spring Security, MyBatis, MySQL          |
| AI Backend | Python 3.12, FastAPI, LangGraph, Claude API             |
| DB         | Supabase (PostgreSQL + pgvector)                        |
| Infra      | Cloud Run (backend · backend-ai 독립 배포)              |

---

## 프로젝트 구조

```
salmanhae/
├── frontend/          # Vue 3
│   └── src/
│       ├── components/
│       ├── views/
│       ├── stores/    # Pinia
│       └── api/       # Axios
├── backend/           # Spring Boot 3
│   └── src/main/java/com/ssafy/salman/
│       ├── config/
│       ├── controller/
│       ├── model/
│       │   ├── dao/   # MyBatis DAO 인터페이스 + Impl
│       │   └── dto/
│       ├── service/   # 인터페이스 + Impl
│       └── batch/     # 공공데이터 수집 스케줄러
├── backend-ai/        # FastAPI + LangGraph
│   └── app/
│       ├── api/
│       ├── graph/     # LangGraph 노드 + 엣지
│       ├── clients/   # Spring Boot HTTP 클라이언트
│       └── rag/       # pgvector 검색
├── docs/              # 프로젝트 문서 (01~12)
├── phases/            # Harness Phase 지시서
└── scripts/           # execute.py, hooks
```

---

## 실행 방법

```bash
# Frontend
cd frontend && pnpm install && pnpm dev

# Backend
cd backend && ./mvnw spring-boot:run

# AI Backend
cd backend-ai && uvicorn app.main:app --reload
```

---

## 개발 워크플로우

### 브랜치 구조

```
main ← develop ← feature/*, fix/*, phase/*
```

`develop`이 실제 작업 브랜치. `main`은 배포할 때만.

---

### 기본 개발 플로우

**1. GitHub에서 이슈 생성**

- 템플릿 3개 중 선택 (기능 / 버그 / 잡무)
- 제목 형식: `[FEAT][F-1] 더미 매물 API 구현`
- 라벨: 영역(`frontend`, `backend`, `backend-ai`) + 기능(`F-1`~`F-8`)
- F-1~F-8이 뭔지는 `docs/01_PRD.md` 참고

**2. 브랜치 생성 후 작업**

```bash
git checkout develop
git checkout -b feature/1-property-api
```

**3. 커밋**

```bash
git commit -m "feat(be): 매물 조회 API 구현 (#이슈번호)"
```

**4. PR 생성 → 상대방 approve → develop merge (Merge Commit)**

---

### Harness 플로우

```bash
# Claude Code에서
/harness
# → docs/ 읽고 Phase 계획 제안 → 승인하면 phases/ 폴더에 지시서 생성

python3 scripts/execute.py {task-name}
# → Phase마다 자동으로:
#    이슈 생성 → 브랜치 생성 → 코드 작성 → 커밋 → PR 생성
```

`phases/` 폴더에 Phase 지시서(`.md`)와 실행 결과(`.status.json`)가 쌓입니다.
중간에 실패하면 `--from N`으로 해당 Phase부터 재시작할 수 있습니다.

이후 동일하게 **상대방 approve → develop merge**

---

### 커밋 메시지 형식

```
feat(fe): 지도 마커 표시 구현 (#3)
fix(be): 매물 조회 오류 수정 (#7)
feat(ai): LangGraph 의도분류 구현 (#12)
```

| type       | 언제                | scope   | 영역       |
| ---------- | ------------------- | ------- | ---------- |
| `feat`     | 새 기능             | `fe`    | 프론트엔드 |
| `fix`      | 버그 수정           | `be`    | 백엔드     |
| `refactor` | 동작 변경 없는 개선 | `ai`    | AI 백엔드  |
| `test`     | 테스트              | `db`    | DB         |
| `docs`     | 문서                | `batch` | 배치       |
| `chore`    | 설정·빌드           |         |            |

---

### 규칙

- 셀프 머지 금지 — 내 PR은 상대방이 approve해야 merge
- merge는 모두 **Merge commit**
- 이슈 번호 항상 포함 — 커밋 메시지에 `(#N)` 필수

---

## 문서

| 문서                      | 내용                        |
| ------------------------- | --------------------------- |
| `docs/01_PRD.md`          | 기능 ID (F-1~F-8), MVP 범위 |
| `docs/02_ARCHITECTURE.md` | 서비스 구조, 디렉토리       |
| `docs/03_ADR.md`          | 기술 결정 기록              |
| `docs/04_UI_GUIDE.md`     | 디자인 기준, CSS 토큰       |
| `docs/05_GIT_GUIDE.md`    | 컨벤션 상세                 |
| `docs/11_ROADMAP.md`      | 개발 순서                   |
