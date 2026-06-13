# 프로젝트: 살만해 (AI 에이전트 기반 부동산 탐색 서비스)

## 기술 스택

| 영역 | 기술 |
|------|------|
| Frontend | Vue 3, Vite, Pinia, Axios, 네이버지도 SDK, Tailwind CSS |
| Backend | Spring Boot 3, Spring Security, Supabase Auth, PostgreSQL |
| AI Backend | Python 3.11, FastAPI, LangGraph, Claude API (Anthropic) |
| DB | Supabase (PostgreSQL + pgvector) |
| Infra | Cloud Run (backend + backend-ai 각각 독립 배포) |
| Batch | Spring Scheduler (국토교통부·생활안전지도 공공 API) |

## 아키텍처 규칙

- CRITICAL: 모든 비즈니스 로직은 각 레이어의 Service 클래스에 위치한다. Controller/Router는 입력 검증과 위임만 한다.
- CRITICAL: AI 에이전트(LangGraph)는 backend-ai 서비스에만 존재한다. Spring Boot에서 직접 LLM을 호출하지 않는다.
- CRITICAL: API 키 및 시크릿은 환경변수로 관리한다. 코드에 하드코딩 절대 금지.
- CRITICAL: Spring Boot와 FastAPI 사이 통신은 내부 HTTP만 사용한다. Frontend가 FastAPI를 직접 호출하지 않는다.
- CRITICAL: 인증이 필요한 API(F-2~F-8)는 반드시 Supabase JWT 검증 필터를 거친다.
- 공공 API 데이터(실거래가, 안전시설)는 배치로 수집 후 DB에 저장하고, 클라이언트 요청 시에는 DB만 조회한다.
- pgvector 유사도 검색은 FastAPI(backend-ai)에서만 수행한다.
- Frontend는 Spring Boot REST API만 직접 호출한다.
- 데이터 모델 변경 시 docs/07_DOMAIN_MODEL.md를 함께 업데이트한다.
- 안전 점수 계산은 배치에서 사전 계산하여 property_score_stat에 저장한다.

## 개발 프로세스

- CRITICAL: 새 기능 구현 시 테스트를 먼저 작성하고, 테스트가 통과하는 구현을 작성한다 (TDD).
- CRITICAL: 커밋 메시지는 `type(scope): 한글 설명 (#이슈번호)` 형식을 따른다 (docs/05_GIT_GUIDE.md 참고).
- CRITICAL: execute.py 자동 커밋에는 `[ai]` suffix를 붙인다. 수동 커밋에는 붙이지 않는다.
- Phase 브랜치명: `phase/{N}-{slug}` (execute.py가 자동 생성).
- feature/fix/refactor 브랜치는 develop으로 merge하고, develop → main은 Merge commit 사용.
- API 응답 형식 변경 시 docs/08_API_SPEC.md를 반드시 업데이트한다.
- MVP 제외 기능(커뮤니티, 실매물 중개, HUG 정밀판정, 등기부등본 AI)은 구현하지 않는다.

## 명령어

```bash
# Frontend
cd frontend && pnpm dev          # 개발 서버
cd frontend && pnpm build        # 프로덕션 빌드
cd frontend && pnpm test         # 테스트

# Backend (Spring Boot)
cd backend && ./mvnw spring-boot:run    # 개발 서버
cd backend && ./mvnw test               # 테스트
cd backend && ./mvnw package            # 빌드

# AI Backend (FastAPI)
cd backend-ai && uvicorn app.main:app --reload  # 개발 서버
cd backend-ai && pytest tests/                  # 테스트
```

## 문서 위치

| 문서 | 경로 |
|------|------|
| 서비스 목표·기능 범위 | docs/01_PRD.md |
| 시스템 아키텍처·디렉토리 구조 | docs/02_ARCHITECTURE.md |
| 기술 결정 기록 | docs/03_ADR.md |
| UI 가이드·안티패턴 | docs/04_UI_GUIDE.md |
| Git·협업 컨벤션 | docs/05_GIT_GUIDE.md |
| 외부 API 목록 | docs/06_EXTERNAL_APIS.md |
| 데이터 모델 | docs/07_DOMAIN_MODEL.md |
| REST API 명세 | docs/08_API_SPEC.md |
| 배치·데이터 수집 | docs/09_BATCH_INGESTION.md |
| 보안 정책 | docs/10_SECURITY_POLICY.md |
| 개발 순서 (로드맵) | docs/11_ROADMAP.md |
| 확장 기능 계획 | docs/12_FUTURE_EXTENSIONS.md |
