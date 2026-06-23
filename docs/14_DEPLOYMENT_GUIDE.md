# 14. 배포 가이드

## 목표 구성

```text
Vercel                 frontend
Cloud Run              backend (Spring Boot)
Cloud Run              backend-ai (FastAPI)
Upstash Redis          이메일 인증 코드, refresh token
Supabase PostgreSQL    서비스 DB, pgvector
```

프론트엔드는 Spring Boot REST API만 호출합니다. FastAPI는 Spring Boot에서만 호출하는 내부 AI 서비스로 취급합니다.

## 현재까지 완료한 것

- Upstash TCP 연결값을 Spring Boot 환경변수로 받을 수 있도록 Redis 설정을 확장했습니다.
- `backend/.env.example`에 Cloud Run에서 사용할 Spring Boot 환경변수 예시를 추가했습니다.

```properties
spring.data.redis.host=${REDIS_HOST:localhost}
spring.data.redis.port=${REDIS_PORT:6379}
spring.data.redis.username=${REDIS_USERNAME:}
spring.data.redis.password=${REDIS_PASSWORD:}
spring.data.redis.ssl.enabled=${REDIS_SSL_ENABLED:false}
```

## Upstash Redis 값 매핑

Upstash 콘솔에서는 `Connect > TCP` 값을 사용합니다. `REST` 값은 현재 Spring Boot 코드에서 사용하지 않습니다.

| Upstash 화면 | Cloud Run 환경변수 | 예시/내용 |
| --- | --- | --- |
| Endpoint | `REDIS_HOST` | `adapted-dory-38225.upstash.io` |
| Port | `REDIS_PORT` | `6379` |
| Username | `REDIS_USERNAME` | `default` |
| Token | `REDIS_PASSWORD` | Upstash Token 값 |
| TLS/SSL | `REDIS_SSL_ENABLED` | `true` |

Upstash가 보여주는 TCP URL은 아래 형태입니다.

```text
redis://default:<token>@adapted-dory-38225.upstash.io:6379
```

이 URL을 그대로 넣지 말고 위 표처럼 나눠서 Spring Boot 환경변수에 넣습니다.

## Spring Boot Cloud Run 환경변수

Cloud Run 서비스명 예시: `salmanhae-api`

| 환경변수 | 내용 |
| --- | --- |
| `SUPABASE_DB_URL` | Spring JDBC URL. 예: `jdbc:postgresql://<supabase-pooler-host>:6543/postgres` |
| `SUPABASE_DB_USERNAME` | Supabase DB 사용자. 예: `postgres.<project-ref>` |
| `SUPABASE_DB_PASSWORD` | Supabase DB 비밀번호 |
| `JWT_SECRET` | JWT 서명용 긴 랜덤 문자열 |
| `APP_CORS_ALLOWED_ORIGINS` | Vercel 프론트 도메인. 로컬 포함 시 `http://localhost:5173,https://<frontend>.vercel.app` |
| `REDIS_HOST` | Upstash TCP Endpoint |
| `REDIS_PORT` | Upstash TCP Port |
| `REDIS_USERNAME` | `default` |
| `REDIS_PASSWORD` | Upstash Token |
| `REDIS_SSL_ENABLED` | `true` |
| `MAIL_USERNAME` | Gmail SMTP 계정 |
| `MAIL_PASSWORD` | Gmail 앱 비밀번호 |
| `AI_AGENT_BASE_URL` | FastAPI Cloud Run URL |
| `INTERNAL_API_KEY` | Spring Boot와 FastAPI가 공유하는 내부 API 키 |
| `AI_AGENT_CONNECT_TIMEOUT_MS` | FastAPI 연결 타임아웃. 기본 `2000` |
| `AI_AGENT_READ_TIMEOUT_MS` | FastAPI 응답 타임아웃. 기본 `10000` |

배포 예시:

```bash
cd backend

gcloud run deploy salmanhae-api \
  --source . \
  --region asia-northeast3 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 3 \
  --set-env-vars SUPABASE_DB_URL="jdbc:postgresql://<supabase-pooler-host>:6543/postgres" \
  --set-env-vars SUPABASE_DB_USERNAME="postgres.<project-ref>" \
  --set-env-vars SUPABASE_DB_PASSWORD="<supabase-db-password>" \
  --set-env-vars JWT_SECRET="<long-random-secret>" \
  --set-env-vars APP_CORS_ALLOWED_ORIGINS="https://<frontend>.vercel.app" \
  --set-env-vars REDIS_HOST="adapted-dory-38225.upstash.io" \
  --set-env-vars REDIS_PORT="6379" \
  --set-env-vars REDIS_USERNAME="default" \
  --set-env-vars REDIS_PASSWORD="<upstash-token>" \
  --set-env-vars REDIS_SSL_ENABLED="true" \
  --set-env-vars MAIL_USERNAME="<gmail-address>" \
  --set-env-vars MAIL_PASSWORD="<gmail-app-password>" \
  --set-env-vars AI_AGENT_BASE_URL="https://<backend-ai-cloud-run-url>" \
  --set-env-vars INTERNAL_API_KEY="<spring-fastapi-shared-secret>"
```

## FastAPI Cloud Run 환경변수

Cloud Run 서비스명 예시: `salmanhae-ai`

| 환경변수 | 내용 |
| --- | --- |
| `APP_ENV` | 운영 환경. 예: `prod` |
| `INTERNAL_API_KEY` | Spring Boot와 동일한 내부 API 키 |
| `SPRING_API_BASE_URL` | Spring Boot Cloud Run URL |
| `SPRING_API_TIMEOUT_SECONDS` | Spring Boot 호출 타임아웃. 예: `5` |
| `SUPABASE_DB_URL` | Python용 Postgres URL. 예: `postgresql://<user>:<password>@<host>:5432/postgres` |
| `SUPABASE_CONNECT_TIMEOUT_SECONDS` | DB 연결 타임아웃. 예: `5` |
| `SUPABASE_STATEMENT_TIMEOUT_MS` | 쿼리 타임아웃. 예: `5000` |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key. 서버 전용 |
| `GMS_API_KEY` | 생활안전지도 등 서버 측 공공 API 키가 필요한 경우 |
| `LLM_BASE_URL` | LLM API base URL. 기본 `https://api.openai.com/v1` |
| `LLM_MODEL` | 사용할 LLM 모델명 |
| `EMBEDDING_API_KEY` | 임베딩 API 키 |
| `EMBEDDING_BASE_URL` | 임베딩 API base URL |
| `EMBEDDING_MODEL` | 사용할 임베딩 모델명 |
| `LANGSMITH_TRACING` | LangSmith 추적 사용 여부. 기본 `false` |
| `LANGSMITH_API_KEY` | LangSmith 사용 시 API 키 |

배포 예시:

```bash
cd backend-ai

gcloud run deploy salmanhae-ai \
  --source . \
  --region asia-northeast3 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 2 \
  --set-env-vars APP_ENV="prod" \
  --set-env-vars INTERNAL_API_KEY="<spring-fastapi-shared-secret>" \
  --set-env-vars SPRING_API_BASE_URL="https://<backend-cloud-run-url>" \
  --set-env-vars SPRING_API_TIMEOUT_SECONDS="5" \
  --set-env-vars SUPABASE_DB_URL="postgresql://<user>:<password>@<host>:5432/postgres" \
  --set-env-vars SUPABASE_CONNECT_TIMEOUT_SECONDS="5" \
  --set-env-vars SUPABASE_STATEMENT_TIMEOUT_MS="5000" \
  --set-env-vars SUPABASE_SERVICE_ROLE_KEY="<supabase-service-role-key>" \
  --set-env-vars LLM_MODEL="<llm-model>" \
  --set-env-vars EMBEDDING_API_KEY="<embedding-api-key>" \
  --set-env-vars EMBEDDING_MODEL="<embedding-model>"
```

현재 FastAPI의 `/internal/agent/chat`은 `X-Internal-Api-Key`로 보호됩니다. Cloud Run IAM 비공개 호출까지 적용하려면 Spring Boot에서 Google ID token을 붙여 호출하도록 별도 구현이 필요합니다.

## Vercel 환경변수

Vercel 프로젝트 root는 `frontend`로 설정합니다.

| 환경변수 | 내용 |
| --- | --- |
| `VITE_API_BASE_URL` | Spring Boot Cloud Run URL |
| `VITE_NAVER_MAP_CLIENT_ID` | 브라우저에 노출 가능한 네이버 지도 SDK Client ID |

Vercel 설정:

```text
Root Directory: frontend
Framework Preset: Vite
Install Command: pnpm install
Build Command: pnpm build
Output Directory: dist
```

## 배포 순서

1. Supabase schema와 seed 데이터가 운영 DB에 적용되어 있는지 확인합니다.
2. Upstash Redis TCP 값을 확인하고 Spring Boot 환경변수에 매핑합니다.
3. `backend-ai`를 Cloud Run에 먼저 배포합니다.
4. `backend`를 Cloud Run에 배포하면서 `AI_AGENT_BASE_URL`에 FastAPI URL을 넣습니다.
5. Vercel에 `frontend`를 배포하고 `VITE_API_BASE_URL`에 Spring Boot URL을 넣습니다.
6. 최종 Vercel 도메인을 `APP_CORS_ALLOWED_ORIGINS`에 반영하고 Spring Boot Cloud Run 서비스를 재배포합니다.
7. 이메일 인증, 로그인, 토큰 갱신, 지도 매물 조회, AI 채팅 순서로 smoke test를 수행합니다.

## 배포 후 확인

FastAPI:

```bash
curl https://<backend-ai-cloud-run-url>/health
```

Spring Boot:

```bash
curl https://<backend-cloud-run-url>/api/v1/properties
```

프론트:

```text
https://<frontend>.vercel.app
```

브라우저에서 지도 SDK 로딩, API CORS, 로그인 후 JWT 포함 요청이 정상 동작하는지 확인합니다.

## 다음에 남은 작업

- Spring Boot용 `backend/Dockerfile`을 추가해 Cloud Run 배포 방식을 고정합니다.
- 운영 secret은 `--set-env-vars` 대신 Secret Manager로 옮기는 것을 검토합니다.
- FastAPI Cloud Run을 공개 URL + 내부 API 키 방식에서 IAM 비공개 호출 방식으로 강화할지 결정합니다.
- Spring Scheduler 배치는 운영 중복 실행 위험이 있으므로 Cloud Scheduler + Cloud Run Job 분리를 검토합니다.
