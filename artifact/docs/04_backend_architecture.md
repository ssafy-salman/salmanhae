# 04. 시스템 아키텍처

## 전체 흐름

```
[사용자 브라우저]
       │
       ▼ ① 챗봇 메시지 전송 (JWT 포함)
[Spring Boot — Cloud Run]
       │
       ├─ ② Supabase JWT 검증 + 메시지 로깅 (Supabase DB)
       │
       ▼ ③ RAG 답변 요청 (HTTP POST)
[Python FastAPI + LangGraph — Cloud Run]
       │
       ├─ ④ 질문 임베딩 → Supabase pgvector 유사도 검색 (Top 3~5 문서)
       │
       ├─ ⑤ LLM API 호출 (Claude API)
       │     프롬프트: [참고 문서] + [사용자 질문] + [툴 결과]
       │
       ▼ ⑥ 생성된 답변 반환
[Spring Boot] ──▶ ⑦ 최종 답변 출력 ──▶ [사용자]
```

---

## 서비스별 역할

### Frontend (Vue 3 + 네이버지도 SDK)
- 네이버지도 SDK로 지도 렌더링, 마커, 레이어 표시
- Spring Boot REST API 호출 (매물, 안전, 실거래가)
- Spring Boot 챗봇 API 호출 (AI 에이전트)
- Supabase Auth JWT를 Axios Interceptor로 자동 첨부

### Spring Boot (Cloud Run)
- 회원가입/로그인/로그아웃 API 제공
- Supabase Auth API를 래핑해 JWT 발급 흐름을 중계
- Supabase JWT 검증 (Spring Security Filter)
- 공공데이터 배치 수집 → PostgreSQL 저장
- 지도/매물/안전/실거래가 REST API 제공
- FastAPI LangGraph 서버로 AI 에이전트 요청 프록시
- 메시지 로깅, 찜하기, 대화 세션 관리

### Python FastAPI + LangGraph (Cloud Run)
- 사용자 입력 의도 분류 (매물 추천 / 법률 상담 / 시세 분석 / 안전 분석)
- 의도별 툴 실행:
  - `search_properties` → Spring Boot API 호출
  - `legal_rag` → pgvector 법률 문서 검색
  - `analyze_price` → Spring Boot API 호출
  - `analyze_safety` → Spring Boot API 호출
  - `news_rag` → pgvector 뉴스 검색 (1.5차)
- Claude API로 최종 자연어 응답 생성

### Supabase
- Auth: JWT 발급, 이메일/소셜 로그인 관리
- DB (PostgreSQL): 매물, 실거래가, 안전시설, 찜하기, 대화 기록
- pgvector: 법률 문서 임베딩, 뉴스 임베딩

---

## 서비스 간 통신

| 출발 | 도착 | 방식 | 내용 |
| --- | --- | --- | --- |
| Frontend | Spring Boot | REST (HTTPS) | 매물 조회, 챗봇, 찜하기 등 |
| Spring Boot | FastAPI | HTTP POST (내부망) | RAG 답변 요청 |
| FastAPI | Spring Boot | HTTP GET (내부망) | 매물/시세/안전 툴 호출 |
| FastAPI | Supabase pgvector | SQL | 법률·뉴스 문서 유사도 검색 |
| FastAPI | Claude API | HTTPS | LLM 응답 생성 |
| Spring Boot | Supabase Auth | HTTPS | 회원가입·로그인 래핑, JWT 검증 |

---

## 데이터베이스 구조

PostgreSQL (Supabase) + pgvector를 사용합니다.

| 용도 | 상세 |
| --- | --- |
| 관계형 데이터 | 매물, 실거래가, 안전시설, 찜하기, 대화 세션·메시지, 사용자 |
| 벡터 데이터 | 법률 문서 임베딩, 뉴스 임베딩 (pgvector) |

---

## 안전 점수 계산

배치 작업으로 매물별 점수를 사전 계산해 `property_score_stat`에 저장합니다.

```
매물 기준 반경 검색
→ CCTV/비상벨/보안등/치안시설 개수 계산
→ 항목별 0~100 정규화
→ 가중 평균 (CCTV 30%, 비상벨 25%, 보안등 25%, 치안시설 20%)
→ property_score_stat 저장
```
