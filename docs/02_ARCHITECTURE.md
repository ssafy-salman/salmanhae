# 02. ARCHITECTURE

## 전체 시스템 흐름

```
[사용자 브라우저]
       │
       ▼ ① 챗봇 메시지 전송 (JWT 포함)
[Spring Boot — Cloud Run]
       │
       ├─ ② Supabase JWT 검증 + 메시지 로깅
       │
       ▼ ③ RAG 답변 요청 (HTTP POST, 내부망)
[Python FastAPI + LangGraph — Cloud Run]
       │
       ├─ ④ 질문 임베딩 → Supabase pgvector 유사도 검색 (Top 3~5)
       ├─ ⑤ Claude API 호출 (프롬프트: [참고 문서] + [질문] + [툴 결과])
       │
       ▼ ⑥ 생성된 답변 반환
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
│   └── src/main/java/com/ssafy/salman/
│       ├── config/        # Security, CORS, Swagger, Beans
│       ├── controller/    # REST 엔드포인트 (입력 검증·위임만)
│       ├── model/
│       │   ├── dao/       # MyBatis DAO 인터페이스 + Impl
│       │   └── dto/       # 요청/응답 데이터 객체
│       ├── service/       # 비즈니스 로직 인터페이스 + Impl
│       └── batch/         # Spring Scheduler 배치 작업
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
- Supabase Auth JWT를 Axios Interceptor로 자동 첨부

### Spring Boot (Cloud Run)
- 회원가입/로그인/로그아웃 API (Supabase Auth 래핑)
- Supabase JWT 검증 (Spring Security Filter)
- 공공데이터 배치 수집 → PostgreSQL 저장
- 지도/매물/안전/실거래가 REST API 제공
- FastAPI로 AI 에이전트 요청 프록시 (Frontend는 FastAPI 직접 호출 불가)
- 메시지 로깅, 찜하기, 대화 세션 관리

### Python FastAPI + LangGraph (Cloud Run)
- 사용자 입력 의도 분류 (매물 추천 / 법률 상담 / 시세 분석 / 안전 분석)
- 의도별 툴 실행:
  - `search_properties` → Spring Boot API 호출
  - `legal_rag` → pgvector 법률 문서 검색
  - `analyze_price` → Spring Boot API 호출
  - `analyze_safety` → Spring Boot API 호출
- Claude API로 최종 자연어 응답 생성

### Supabase
- Auth: JWT 발급, 이메일/소셜 로그인 관리
- DB (PostgreSQL): 매물, 실거래가, 안전시설, 찜하기, 대화 기록, 사용자
- pgvector: 법률 문서 임베딩, 뉴스 임베딩

## 서비스 간 통신 규칙

| 출발 | 도착 | 허용 | 내용 |
|------|------|------|------|
| Frontend | Spring Boot | O | REST HTTPS |
| Frontend | FastAPI | X | 직접 호출 금지 |
| Spring Boot | FastAPI | O | HTTP POST 내부망 |
| FastAPI | Spring Boot | O | HTTP GET 내부망 (툴 호출) |
| FastAPI | Supabase pgvector | O | SQL |
| FastAPI | Claude API | O | HTTPS |
| Spring Boot | Supabase Auth | O | HTTPS |

## 데이터베이스

PostgreSQL (Supabase) + pgvector 단일 인스턴스.

| 용도 | 테이블 |
|------|--------|
| 관계형 | property, transaction_history, safety_facility, wishlist, user, conversation_session, conversation_message |
| 벡터 | 법률 문서 임베딩, 뉴스 임베딩 (pgvector) |
| 통계 | property_score_stat (안전·가격 점수 사전 계산) |

## 배치 흐름

```
Spring Scheduler
  → 국토교통부 실거래가 API × 8 → transaction_history (매일)
  → 생활안전지도 API × 4       → safety_facility (주 1회)
  → 안전 점수 계산             → property_score_stat
      └─ 매물 기준 반경 검색
         → CCTV/비상벨/보안등/치안시설 개수 집계
         → 항목별 0~100 정규화
         → 가중 평균 (CCTV 30%, 비상벨 25%, 보안등 25%, 치안시설 20%)
```

## 설계 패턴

| 패턴 | 적용 위치 |
|------|----------|
| Controller → Service → DAO (MyBatis) | Spring Boot 전 도메인 |
| LangGraph State Machine | AI 에이전트 의도 분류 → 툴 선택 → 응답 생성 |
| Pinia Store per Feature | Frontend (map, chat, auth, wishlist) |
| Axios Interceptor | JWT 자동 첨부, 401 처리 |
| Batch → DB 캐싱 | 공공 API 데이터 — 런타임에 외부 호출 없음 |
