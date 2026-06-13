# 아키텍처: 살만해

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
│   └── src/main/java/
│       ├── controller/    # REST 엔드포인트 (입력 검증만)
│       ├── service/       # 비즈니스 로직 (모든 로직 여기)
│       ├── repository/    # JPA Repository
│       ├── domain/        # Entity, Enum, VO
│       ├── dto/           # 요청/응답 DTO
│       ├── batch/         # Spring Scheduler 배치 작업
│       └── config/        # Security, CORS, Beans
└── backend-ai/        # Python FastAPI + LangGraph (Cloud Run)
    └── app/
        ├── api/           # FastAPI 라우터
        ├── graph/         # LangGraph 노드 + 엣지 정의
        ├── core/          # 설정, 의존성 주입
        ├── clients/       # 외부 HTTP 클라이언트 (Spring Boot 호출)
        └── rag/           # pgvector 검색 로직
```

## 패턴

| 패턴 | 적용 위치 |
|------|----------|
| Controller → Service → Repository | Spring Boot 전 도메인 |
| LangGraph State Machine | AI 에이전트 의도 분류 → 툴 선택 → 응답 생성 |
| Pinia Store per Feature | frontend 상태 관리 (map, chat, auth, wishlist) |
| Axios Interceptor | JWT 자동 첨부, 401 처리 |
| Batch → DB 캐싱 | 공공 API 데이터 (실거래가, 안전시설) — 런타임에 외부 호출 없음 |

## 데이터 흐름

### 매물 탐색 (비로그인)
```
Frontend → GET /api/v1/properties?bounds=... → Spring Boot → PostgreSQL
```

### AI 에이전트 (로그인)
```
Frontend → POST /api/v1/chat (JWT) → Spring Boot (JWT 검증)
  → POST /internal/agent → FastAPI + LangGraph
      ├─ search_properties → Spring Boot → PostgreSQL
      ├─ legal_rag → pgvector (Supabase)
      ├─ analyze_price → Spring Boot → PostgreSQL
      └─ 최종 응답 → Claude API
  → 응답 반환 → Frontend
```

### 배치 데이터 수집
```
Spring Scheduler
  → 국토교통부 API × 8 → transaction_history
  → 생활안전지도 API × 4 → safety_facility
  → 안전 점수 계산 → property_score_stat
```

## 서비스 간 통신 규칙

| 출발 | 도착 | 허용 |
|------|------|------|
| Frontend | Spring Boot | O (REST HTTPS) |
| Frontend | FastAPI | X (직접 호출 금지) |
| Spring Boot | FastAPI | O (내부 HTTP POST) |
| FastAPI | Spring Boot | O (내부 HTTP GET — 툴 호출) |
| FastAPI | Supabase pgvector | O (SQL) |
| FastAPI | Claude API | O (HTTPS) |
