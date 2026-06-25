# SSAFY 참고 명세/평가표 대응표

## 1. 참고 파일

| 파일 | 반영한 내용 |
| --- | --- |
| `자바전공 [SSAFYHome] Final.pdf` | SSAFY HOME 목표, 예시 요구사항, 최종 산출물 목록, 발표 PPT 포함 항목 |
| `평가표.xlsx` | 완성도 40점, 편리성 20점, AI활용성 20점, 발표 10점, 팀웍 10점 평가 기준 |

## 2. 최종 산출물 제출 기준 대응

| 참고 명세 산출물 | 현재 artifact 대응 | 보강 필요 여부 |
| --- | --- | --- |
| 요구사항 정의서 | `01_REQUIREMENTS_DEFINITION.md` | 작성 완료, 팀원/일정 정보 추가 가능 |
| Use-Case 다이어그램 | `02_USECASE_DIAGRAM.md` | Mermaid 렌더링 후 이미지/PDF 변환 권장 |
| 클래스 다이어그램 | `06_CLASS_DIAGRAM.md` | 핵심 클래스 중심 초안 완료 |
| ER 다이어그램 | `04_ERD.md` | 실제 Supabase public schema 기준으로 갱신 완료 |
| WBS & 간트 차트 | `03_WBS.md`, 기존 `wbs & gantt/*.xlsx` | 기존 엑셀과 초안 내용 동기화 권장 |
| 화면 설계서 | `07_SCREEN_DEFINITION.md`, 기존 `usecase & design/Screen_Design_Web.pdf` | 실제 화면 캡처 추가 권장 |
| 기타 참고 문서 | `docs/` 전체, `10_REFERENCE_ALIGNMENT.md` | README에서 링크 정리 권장 |
| DB Schema.sql | `database/migrations/*.sql` | 제출 zip에 포함 |
| Spring Boot 프로젝트 소스 | `backend/` | 제출 zip에 포함 |
| Vue.js 프로젝트 소스 | `frontend/` | 제출 zip에 포함 |
| 활용 데이터셋 | `data/`, `database/`, 수집/정규화 산출물 | 용량/개인키 제외 확인 필요 |
| 발표용 PPT/PDF | `08_PRESENTATION_PPT_OUTLINE.md` | 실제 PPT 제작 필요 |
| AI 사용 보고서 | `08_PRESENTATION_PPT_OUTLINE.md` 5장 기준 | PPT에 별도 섹션 추가 권장 |

## 3. SSAFY HOME 예시 요구사항 대응

| 예시 요구사항 | 참고 우선순위 | 살만해 대응 |
| --- | --- | --- |
| F01 주택 실거래가 정보 수집 | 필수 | 국토교통부 실거래가를 `transaction_history`에 정규화 저장 |
| F02 주택 실거래가 검색 | 필수 | 지도 조회, 주변 실거래가, 시세 분석 API로 제공 |
| F12 회원 관리 | 필수 | 이메일 인증 기반 회원가입, 사용자 DB 저장 |
| F13 로그인 관리 | 필수 | 로그인/로그아웃/refresh token rotation 구현 |
| F16 CCTV 설치 현황 정보 수집 | 권장/추가 | CCTV, 비상벨, 보안등, 치안시설을 `safety_facility`에 저장 |
| F17 CCTV 설치 현황 검색 | 권장/추가 | 안전시설 API와 안전 분석 카드로 제공 |
| NF1 공공데이터 정확성 | 비기능 | 공공 API 수집 후 DB 저장, 런타임 외부 호출 최소화 |
| NF3 응답성 | 비기능 | 시세/안전 점수 사전 계산, viewport 조회 최적화 |
| NF4 사용자 편의성 | 비기능 | 지도+챗봇, 필터, 상세 drawer, 분석 카드 제공 |
| NF5 MSA REST API | 비기능 | Spring Boot와 FastAPI backend-ai 분리 |
| NF6 MSA OAuth | 비기능 | OAuth 대신 자체 JWT 구현, OAuth는 확장 후보 |

## 4. 평가표 기준 대응 전략

| 평가 구분 | 배점 | 제출/발표에서 보여줄 근거 |
| --- | --- | --- |
| 완성도 | 40 | PRD의 핵심 아이디어가 지도 탐색, AI 추천, 법률 RAG, 시세/안전 분석으로 이어지는 흐름을 시연한다. |
| 편리성 | 20 | 지도 필터, zoom별 표시, 상세 drawer, 챗봇 카드형 응답으로 사용자 중심 UI를 강조한다. |
| AI활용성 | 20 | LangGraph supervisor, worker 분기, pgvector RAG, Spring API tool 호출, 프롬프트 전략을 설명한다. |
| 발표 | 10 | PPT에 문제 정의, 시장/차별화, 개발 결과, 시스템 구조도, 화면 흐름, 핵심 알고리즘, 기대 효과, 회고를 포함한다. |
| 팀웍 | 10 | phase 기반 작업, 역할 분담, 테스트/문서 협업, Git 운영 방식을 정리한다. |

## 5. 우수 PPT 예시 참고 포인트

우수 PPT 예시는 필수 목차를 단순 나열하기보다 실제 발표용 흐름으로 재구성했다. 살만해 PPT에도 아래 포인트를 추가하면 발표 설득력이 좋아진다.

| 참고 포인트 | 살만해 적용 방향 |
| --- | --- |
| 섹션 구분 슬라이드 | `기획 배경`, `시스템 설계`, `시연`, `주요 기능`, `고도화`, `기대 효과`처럼 발표 호흡을 끊어준다. |
| Page Flow 중심 설명 | 지도 홈 → 로그인 → 챗봇 → AI 응답 → 분석 구조 순서로 실제 화면 캡처를 이어 보여준다. |
| 고도화 적용 방안 | LangGraph Supervisor, pgvector RAG, 배치 데이터 적재, 안전 점수 사전 계산, 지도 viewport 모드를 문제-해결-결과 형식으로 정리한다. |
| 기대 효과 강조 | 청년 1인 가구의 계약 전 판단 비용 감소, 법률/시세/안전 정보 통합, AI 기반 상담 경험을 마지막에 압축한다. |
| 시연 영상 분리 | 실제 시연 중 장애를 대비해 3분 UCC 또는 녹화본을 PPT 중간에 넣을 수 있게 준비한다. |

## 6. 제출 전 보강 체크리스트

| 항목 | 상태 |
| --- | --- |
| Mermaid 다이어그램을 이미지 또는 PDF로 변환 | 필요 |
| 화면정의서에 실제 화면 캡처 삽입 | 필요 |
| 기존 WBS/Gantt 엑셀과 `03_WBS.md` 내용 동기화 | 필요 |
| 발표 PPT에 AI 사용 보고서 섹션 추가 | 필요 |
| 발표 PPT에 Page Flow와 고도화 적용 방안 섹션 추가 | 권장 |
| 배포 URL 기준 화면 캡처와 시연 접근 순서 반영 | 반영 |
| Vercel SPA 직접 URL 진입 404 가능성에 대비한 시연 동선 준비 | 필요 |
| README에 설계 문서/소스/데이터셋 위치 정리 | 필요 |
| `.env`, API key, 시크릿, 대용량 임시 산출물 제외 확인 | 필요 |
