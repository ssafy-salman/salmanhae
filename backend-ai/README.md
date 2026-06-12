# backend-ai

살만해 프로젝트의 내부 AI 에이전트 서버입니다. FastAPI와 LangGraph를 사용하며, 프론트엔드가 직접 호출하지 않고 Spring Boot Backend가 인증을 처리한 뒤 내부 API로 호출합니다.

## 역할

- 사용자 메시지 의도 분류
- 매물 추천/검색, 시세 분석, 안전 분석을 위한 Spring Boot API 도구 호출
- Supabase PostgreSQL + pgvector 기반 법률 상담 RAG
- GMS LLM API를 통한 최종 답변 생성
- Spring Boot가 사용하기 쉬운 JSON 응답 반환

## 실행 방법

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8080
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8080
```

## 환경변수

`.env.example`을 기준으로 로컬 `.env`를 구성합니다. 실제 키는 저장소에 커밋하지 않습니다.

| 이름 | 설명 |
| --- | --- |
| `APP_ENV` | 실행 환경 |
| `INTERNAL_API_KEY` | Spring Boot 내부 호출 검증 키 |
| `SPRING_API_BASE_URL` | Spring Boot API base URL |
| `SUPABASE_DB_URL` | Supabase PostgreSQL 연결 문자열 |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key |
| `GMS_API_KEY` | GMS LLM API key |
| `LLM_MODEL` | 사용할 LLM 모델 |
| `EMBEDDING_MODEL` | 사용할 embedding 모델 |
| `LANGSMITH_TRACING` | LangSmith tracing 여부 |
| `LANGSMITH_API_KEY` | LangSmith API key |

## API 명세

### GET /health

```json
{
  "status": "ok",
  "service": "backend-ai"
}
```

### POST /internal/agent/chat

Spring Boot만 호출하는 내부 API입니다. `X-Internal-Api-Key` 헤더가 필요합니다.

Request:

```json
{
  "userId": "uuid",
  "sessionId": null,
  "message": "관악구 보증금 5천 이하 원룸 추천해줘",
  "context": {
    "selectedPropertyId": null,
    "recentMessages": []
  }
}
```

Response:

```json
{
  "intent": "PROPERTY_SEARCH",
  "answer": "조건에 맞는 매물 1개를 찾았습니다.",
  "properties": [],
  "legalCards": [],
  "toolResults": {},
  "nextActions": []
}
```

## LangGraph 흐름

```txt
START
-> classify_intent
-> route_by_intent
   -> property_search
   -> legal_rag
   -> price_analysis
   -> safety_analysis
   -> fallback
-> generate_answer
-> END
```

의도 값:

- `PROPERTY_SEARCH`
- `LEGAL_CONSULT`
- `PRICE_ANALYSIS`
- `SAFETY_ANALYSIS`
- `HUG_CALC`
- `FALLBACK`

## 로컬 테스트

```bash
pytest
```

테스트 범위:

- `/health` 200 응답
- 내부 API 키 누락 시 401 응답
- 정상 채팅 요청 시 `intent`, `answer` 반환
- 대표 문장별 의도 분류

## Docker 실행

```bash
docker build -t backend-ai .
docker run --rm -p 8080:8080 --env-file .env backend-ai
```

Cloud Run 배포를 고려해 컨테이너는 기본적으로 8080 포트에서 실행됩니다.

## Spring Boot 연동 방식

- 프론트엔드는 Spring Boot의 `/api/v1/chat`만 호출합니다.
- Spring Boot는 Supabase JWT를 검증하고 사용자 식별을 완료합니다.
- Spring Boot가 `POST /internal/agent/chat`으로 `backend-ai`를 호출합니다.
- `backend-ai`는 `X-Internal-Api-Key`만 검증하고 사용자 인증을 직접 수행하지 않습니다.
- 매물/시세/안전 데이터는 `SpringClient`를 통해 Spring Boot API에서 조회합니다.
- 법률 RAG는 `backend-ai`가 Supabase pgvector를 직접 조회합니다.

## GitLab 동기화 workflow

`.github/workflows/sync-to-gitlab.yml`은 GitHub `main` 브랜치 push 또는 수동 실행 시 GitLab `master` 브랜치로 강제 동기화합니다.

필요한 GitHub Secret:

- `GITLAB_TOKEN`
