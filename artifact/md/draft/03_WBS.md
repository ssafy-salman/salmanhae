# WBS

## 1. WBS 요약

| 단계 | 작업 패키지 | 주요 산출물 | 상태 |
| --- | --- | --- | --- |
| 1 | 기획/요구사항 | PRD, 기능 ID, MVP 범위 | 완료 |
| 2 | 아키텍처/도메인 설계 | 아키텍처 문서, 도메인 모델, API 명세 | 완료 |
| 3 | DB/데이터 파이프라인 | migration, 실거래가/안전시설 스키마, 법률 chunk 스키마 | 대부분 완료 |
| 4 | Backend API | 인증, 매물, 지도 viewport, 안전, 시세, 챗봇 프록시 | 대부분 완료 |
| 5 | AI Backend | LangGraph supervisor, 워커, RAG, Spring 연동 | 대부분 완료 |
| 6 | Frontend | 지도 탐색, 인증, 챗봇, 분석 카드 화면 | 대부분 완료 |
| 7 | 테스트/QA | 단위/통합 테스트, phase QA | 진행/보강 |
| 8 | 배포/운영 | Cloud Run, env, deployment guide | 문서화 완료/운영 준비 |
| 9 | 제출 산출물 | 요구사항정의서, UseCase, WBS, ERD, API, Class, 화면정의서, 발표/시연 구성안 | 초안 작성 |

## 2. 상세 WBS

| WBS ID | 작업명 | 세부 작업 | 담당 영역 | 산출물 | 상태 |
| --- | --- | --- | --- | --- | --- |
| 1.1 | 서비스 문제 정의 | 타깃 사용자, 문제, 차별점 정의 | 기획 | `docs/01_PRD.md` | 완료 |
| 1.2 | MVP 범위 정의 | F-1~F-8 기능 ID, MVP/1.5차 구분 | 기획 | 기능 목록 | 완료 |
| 2.1 | 시스템 아키텍처 | Frontend-Spring-FastAPI-Supabase-Redis 흐름 정의 | 공통 | `docs/02_ARCHITECTURE.md` | 완료 |
| 2.2 | 도메인 모델링 | 매물, 실거래가, 안전시설, 법률 chunk, 사용자 모델 정의 | 공통 | `docs/07_DOMAIN_MODEL.md` | 완료 |
| 2.3 | API 계약 | Spring REST API, AI 내부 API, 에러코드 정의 | 공통 | `docs/08_API_SPEC.md` | 완료 |
| 3.1 | 매물/실거래가 스키마 | `transaction_history`, `properties` 생성 | DB | migration SQL | 완료 |
| 3.2 | 시세 통계 스키마 | `region_price_stat`, `building_price_stat` 생성 | DB | migration SQL | 완료 |
| 3.3 | 법률 RAG 스키마 | `legal_document_chunks`, vector index 생성 | DB/AI | migration SQL | 완료 |
| 3.4 | 안전시설 스키마 | `safety_facility` 생성 | DB/Backend | migration SQL | 완료 |
| 3.5 | 안전 점수 스키마 | `property_score_stat` 생성 | DB/Backend | migration SQL | 완료 |
| 4.1 | 인증 API | 이메일 인증, 회원가입, 로그인, 토큰 갱신, 로그아웃 | Backend | `AuthController`, `AuthService` | 완료 |
| 4.2 | Spring Security | JWT 필터, 권한 정책, stateless session | Backend | `SecurityConfig`, `JwtAuthenticationFilter` | 완료 |
| 4.3 | 매물 API | bounds 조회, 상세 조회, 주변 실거래가, 안전 요약 | Backend | `PropertyController`, `PropertyService` | 완료 |
| 4.4 | 지도 viewport API | zoom별 지역 평균/클러스터/매물 모드 | Backend | `MapViewportController`, `MapViewportService` | 완료 |
| 4.5 | 안전시설 API | bounds/types 기반 안전시설 조회 | Backend | `SafetyFacilityController` | 완료 |
| 4.6 | 시세 분석 API | 지역/건물 시세 통계 조회 | Backend | `PriceAnalysisController` | 완료 |
| 4.7 | 챗봇 프록시 | Spring에서 backend-ai 내부 API 호출 | Backend | `ChatController`, `AiAgentClient` | 완료 |
| 5.1 | AI API | `/internal/agent/chat`, `/health` 구현 | AI Backend | FastAPI router | 완료 |
| 5.2 | Supervisor 그래프 | worker 선택 루프, FINISH 응답 생성 | AI Backend | `builder.py`, `supervisor.py` | 완료 |
| 5.3 | 매물 검색 워커 | 자연어 조건 추출, Supabase 매물 조회 | AI Backend | `property_search.py` | 완료 |
| 5.4 | 법률 RAG 워커 | embedding, pgvector 검색, 법률 카드 | AI Backend | `legal_rag.py`, retriever | 완료 |
| 5.5 | 시세/안전 워커 | Spring API 호출, 분석 카드 생성 | AI Backend | `price_analysis.py`, `safety_analysis.py` | 완료 |
| 6.1 | 지도 화면 | 검색/필터, 지도, 목록, 상세 패널 | Frontend | `MapExplorer.vue` | 완료 |
| 6.2 | 인증 화면 | 로그인, 이메일 인증, 회원가입 | Frontend | `AuthView.vue` | 완료 |
| 6.3 | 챗봇 화면 | 메시지, 법률 카드, 분석 카드, 입력창 | Frontend | `Chatbot.vue` | 완료 |
| 6.4 | 라우팅/상태 | Vue Router, Pinia, Axios interceptor | Frontend | router/store/api | 완료 |
| 7.1 | Backend 테스트 | Controller/Service/DAO 테스트 | QA | JUnit tests | 진행 |
| 7.2 | AI 테스트 | supervisor, RAG, Spring client 테스트 | QA | pytest tests | 진행 |
| 7.3 | Frontend 테스트 | API/store/util 테스트 | QA | Vitest tests | 진행 |
| 8.1 | 배포 문서 | Cloud Run, 환경변수, 운영 절차 | Infra | `docs/14_DEPLOYMENT_GUIDE.md` | 완료 |
| 9.1 | 제출 문서 초안 | 산출물 Markdown 초안 작성 | 문서 | `artifact/drafts` | 초안 완료 |
| 9.2 | 참고 명세 대응표 | SSAFY HOME 필수/평가 기준과 살만해 구현 범위 매핑 | 문서 | `10_REFERENCE_ALIGNMENT.md` | 초안 완료 |
| 9.3 | 제출 패키지 정리 | 설계 문서, Schema SQL, Spring/Vue/AI 소스, 활용 데이터셋, PPT/PDF, AI 사용 보고서 | 제출 | GitLab/zip/PPT | 제출 전 필요 |

## 3. 제출 전 체크리스트

| 항목 | 체크 |
| --- | --- |
| 요구사항과 구현 범위가 일치하는가 | 초안 반영 |
| MVP 제외 기능이 구현 완료처럼 적히지 않았는가 | 초안 반영 |
| API 명세와 Controller endpoint가 일치하는가 | 초안 반영 |
| ERD가 migration과 도메인 문서를 반영하는가 | 초안 반영 |
| 발표/시연 흐름이 3분 안에 가능한가 | 초안 반영 |
| 평가표의 완성도/편리성/AI활용성/발표/팀웍 기준을 발표 자료에 반영했는가 | 초안 반영 |
