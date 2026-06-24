# 02. ARCHITECTURE

## 전체 시스템 흐름

```
[사용자 브라우저]
       │
       ▼ ① 챗봇 메시지 전송 (JWT 포함)
[Spring Boot — Cloud Run]
       │
       ├─ ② Spring Security JWT 검증 + 메시지 로깅
       │
       ▼ ③ AI 에이전트 요청 (HTTP POST, 내부망)
[Python FastAPI + LangGraph — Cloud Run]
       │
       ├─ ④ supervisor (LLM) → 워커 선택
       │      ├─ PROPERTY_SEARCH → Text-to-SQL → Supabase 직접 조회
       │      ├─ LEGAL_CONSULT   → pgvector RAG (법률 문서 유사도 검색)
       │      ├─ PRICE_ANALYSIS  → Spring Boot API 호출
       │      ├─ SAFETY_ANALYSIS → Spring Boot API 호출
       │      └─ GENERAL_CHAT    → pass-through
       │      ↑── 워커 완료 후 supervisor로 복귀 (workers_called 누적)
       ├─ ⑤ FINISH → generate_answer (GMS API 호출)
       │
       ▼ ⑥ 생성된 답변 + workersCalled 반환
[Spring Boot] ──▶ ⑦ 최종 답변 출력 ──▶ [사용자]
```

## 디렉토리 구조

```
salmanhae/
├── frontend/          # Vue 3 + Vite + Pinia + Tailwind
│   └── src/
│       ├── components/    # 재사용 UI 컴포넌트
│       ├── views/         # 페이지 컴포넌트 (라우터 연결)
│       ├── stores/        # Pinia 상태 관리
│       ├── api/           # Axios 클라이언트 + API 함수
│       └── utils/         # 순수 유틸리티 함수
├── backend/           # Spring Boot 3 (Cloud Run)
│   └── src/main/java/com/ssafy/salmanhae/
│       ├── common/
│       │   ├── exception/ # ApiException, ErrorCode, GlobalExceptionHandler
│       │   └── response/  # ApiResponse, ListResponse
│       ├── config/        # SecurityConfig, WebConfig
│       ├── controller/
│       │   ├── auth/      # AuthController
│       │   └── property/  # PropertyController
│       ├── filter/        # JwtAuthenticationFilter
│       ├── model/
│       │   ├── dao/
│       │   │   ├── auth/     # UserDao (MyBatis @Mapper)
│       │   │   └── property/ # PropertyDao
│       │   └── dto/
│       │       ├── auth/     # User (implements UserDetails), LoginRequest, LoginResponse, SignupRequest, RefreshRequest, RefreshResponse, EmailSendRequest, EmailVerifyRequest
│       │       └── property/ # PropertyRow, PropertySummaryResponse, PropertyDetailResponse 등
│       ├── service/
│       │   ├── auth/      # AuthService, CustomUserDetailsService, EmailVerificationService
│       │   └── property/  # PropertyService, PropertyServiceImpl
│       ├── util/          # JwtUtil
│       └── batch/         # Spring Scheduler 배치 작업 (예정)
└── backend-ai/        # Python FastAPI + LangGraph (Cloud Run)
    └── app/
        ├── api/           # FastAPI 라우터
        ├── graph/         # LangGraph 노드 + 엣지 정의
        ├── core/          # 설정, 의존성 주입
        ├── clients/       # 외부 HTTP 클라이언트 (Spring Boot 호출)
        └── rag/           # pgvector 검색 로직
```

## 서비스별 역할

### Frontend (Vue 3 + 네이버지도 SDK)

- 네이버지도 SDK로 지도 렌더링, 마커, 레이어 표시
- Spring Boot REST API 호출 (매물, 안전, 실거래가, 챗봇)
- Spring Security JWT를 Axios Interceptor로 자동 첨부

### Spring Boot (Cloud Run)

- 회원가입/로그인/로그아웃/토큰 갱신 API (Spring Security 자체 구현)
- 회원가입 전 이메일 인증 (Gmail SMTP + Redis TTL 5분)
- JWT 발급 및 검증 (Spring Security Filter), 리프레시 토큰 Redis 저장 및 Token Rotation
- 공공데이터 배치 수집 → PostgreSQL 저장
- F-1 MVP 샘플 매물 및 운영 매물 데이터 저장/조회 API 제공
- 실거래가 건물 anchor 지오코딩 결과를 DB에 저장하고 지도 API에서는 저장 좌표만 조회
- 지도/매물/안전/실거래가 REST API 제공
- FastAPI로 AI 에이전트 요청 프록시 (Frontend는 FastAPI 직접 호출 불가)
- 메시지 로깅, 찜하기, 대화 세션 관리

### Python FastAPI + LangGraph (Cloud Run)

- **Supervisor 패턴** (LangGraph 순환 그래프): LLM이 워커를 하나씩 선택·실행하고 `workers_called`에 누적한 뒤 다시 supervisor로 돌아가 다음 워커를 결정하는 루프. `FINISH` 결정 시 `generate_answer`로 이동
- 사용 가능한 워커 (5종):
  - `PROPERTY_SEARCH` → LLM이 조건 추출(Text-to-SQL) 후 Supabase DB 직접 조회
  - `LEGAL_CONSULT` → pgvector 법률 문서 유사도 검색
  - `PRICE_ANALYSIS` → Spring Boot API 호출
  - `SAFETY_ANALYSIS` → Spring Boot API 호출
  - `GENERAL_CHAT` → pass-through (인사·잡담 등 부동산 무관 대화)
- GMS API(OpenAI-compatible)로 최종 자연어 응답 생성
- 응답에 `workersCalled` 배열 포함 (단일 의도: 1개, 복합 의도: 2~3개)

### Redis

- 이메일 인증 코드 (`email:verify:{email}`, TTL 5분)
- 이메일 인증 완료 플래그 (`email:verified:{email}`, TTL 10분)
- 리프레시 토큰 (`refresh:{email}`, TTL 7일)
- 로컬 개발: `localhost:6379` / 운영: 환경변수 `REDIS_HOST`, `REDIS_PORT`

### Supabase

- DB (PostgreSQL): 매물, 실거래가, 안전시설, 찜하기, 대화 기록, 사용자
- pgvector: 법률 문서 임베딩, 뉴스 임베딩

## 서비스 간 통신 규칙

| 출발        | 도착              | 허용 | 내용                      |
| ----------- | ----------------- | ---- | ------------------------- |
| Frontend    | Spring Boot       | O    | REST HTTPS                |
| Frontend    | FastAPI           | X    | 직접 호출 금지            |
| Spring Boot | FastAPI           | O    | HTTP POST 내부망          |
| FastAPI     | Spring Boot       | O    | HTTP GET 내부망 (툴 호출) |
| FastAPI     | Supabase pgvector | O    | SQL                       |
| FastAPI     | Claude API        | O    | HTTPS                     |

## 데이터베이스

PostgreSQL (Supabase) + pgvector 단일 인스턴스.

| 용도   | 테이블                                                                                                     |
| ------ | ---------------------------------------------------------------------------------------------------------- |
| 관계형 | properties, transaction_history, safety_facility, wishlist, user, conversation_session, conversation_message |
| 벡터   | 법률 문서 임베딩, 뉴스 임베딩 (pgvector)                                                                   |
| 통계   | property_score_stat (매물별 안전·가격 점수), region_price_stat (지도 지역별 실거래가 평균)                  |

## 배치 흐름

```
Spring Scheduler
  → 국토교통부 실거래가 API × 8 → transaction_history (매일)
      └─ 시/도·시/군/구·읍/면/동 평균 계산 → region_price_stat
  → 생활안전지도/재난안전 API × 4 → safety_facility (월 1회)
  → 실거래가 건물 anchor 지오코딩   → properties (F-1 더미 매물 seed 생성)
  → 운영 매물 데이터               → properties (초기 저장 후 DB 조회)
  → 점수 계산                    → property_score_stat
      └─ 매물 기준 반경 검색
         → CCTV/비상벨/보안등/치안시설 개수 집계
         → 항목별 0~100 정규화
         → 가중 평균 (CCTV 30%, 비상벨 25%, 보안등 25%, 치안시설 20%)
```

## 설계 패턴

| 패턴                                 | 적용 위치                                   |
| ------------------------------------ | ------------------------------------------- |
| Controller → Service → DAO (MyBatis) | Spring Boot 전 도메인                       |
| LangGraph Supervisor 패턴            | supervisor → 워커(다중) → supervisor 루프 → 응답 생성 |
| Pinia Store per Feature              | Frontend (map, chat, auth, wishlist)        |
| Axios Interceptor                    | JWT 자동 첨부, 401 처리                     |
| Batch → DB 캐싱                      | 공공 API 데이터 — 런타임에 외부 호출 없음   |
