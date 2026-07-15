# 살만해 — 이력서용 요약

## 프로젝트 한 줄 소개

1. 공공데이터와 AI로 매물의 가격·안전시설·임대차 정보를 함께 탐색하는 서비스
2. 청년 1인 가구가 거래·생활 안전·법령을 한 흐름에서 비교하는 부동산 탐색 서비스
3. 지도에서 고른 매물을 저장 데이터와 AI 분석 카드로 연결한 주거 탐색 서비스

## 프로젝트 설명 — 3줄 버전

청년 1인 가구가 실거래가, 주변 안전시설, 임대차 법령을 따로 찾아야 하는 불편을 줄이기 위해 2명이 개발한 부동산 탐색 서비스입니다.  
Vue 지도 클라이언트는 Spring Boot REST API만 호출하고, Spring이 JWT 인증 경계와 저장 데이터 조회를 담당하며 내부 HTTP로 FastAPI·LangGraph 분석을 연결합니다.  
레이어별 전담 없이 기능 단위로 나눴고, 저는 F-1 지도·데이터, F-3 법률 RAG, F-4 시세·안전의 Git으로 확인되는 핵심을 Spring·Vue·FastAPI·DB에 걸쳐 구현했습니다. JWT core·Supervisor·최종 챗봇 UI는 팀원이 담당했습니다.

## 담당 업무 — 4개 불릿 버전

- 국토교통부 8개 거래 source의 필드 차이를 공통 모델로 정규화하고, 결정적 중복 판단 fingerprint와 PostgreSQL `ON CONFLICT` 적재를 구현했습니다. 보존된 오프라인 실행 산출물에서 정규화 거래 약 261만 행을 확인했습니다(세종 제외, 현재 DB 행 수 아님).
- 팀원이 만든 Spring Security JWT 경계 위에 인증된 채팅 API와 내부 API key를 적용하고, 선택 매물 ID가 Frontend→Spring→FastAPI worker로 전달되어 가격·안전 카드로 변환되는 초기 코드 계약과 렌더링을 구현했습니다. 실제 배포 E2E 성공을 뜻하지는 않습니다.
- JSON/XML·인증·좌표 필드가 다른 네 시설 유형의 Spring adapter 경로를 구현하고, 보안등 좌표 fallback의 Web Mercator 수동 역변환과 bbox+Haversine 구면 근사로 고정 반경 source row를 사전 계산하도록 구성했습니다.
- 줌 단계별 지역·클러스터·매물 조회와 지원 검색 조건을 공통 JDBC builder로 연결하고, 법령 chunk·embedding·pgvector 검색 및 Spring/FastAPI 독립 Cloud Run 배포 workflow를 구현했습니다.

## 기술 스택 — 목적 포함 한 줄

Vue 3·Vite·Pinia(지도·채팅 UI와 상태), Java 21·Spring Boot 3.5·Spring Security·JDBC(공개 API·인증 경계·도메인 조회·외부 API 수집), Python 3.12·FastAPI·LangGraph(내부 AI orchestration), PostgreSQL·pgvector·Redis(거래·통계·법령 vector·인증 상태), Docker·Cloud Run·Vercel·GitHub Actions(서비스별 빌드·배포와 GitLab 동기화)에 사용했습니다.

## 검증된 대표 성과

- 외부 거래 데이터를 source·위치·건물·계약일·면적·층·금액 기반 fingerprint로 식별하고, 거래·지역 통계·건물 통계·합성 매물 네 테이블을 한 DB connection과 commit 경계에서 conflict upsert하도록 구현했습니다. 이 fingerprint가 완전한 자연키라는 의미는 아닙니다.
- 선택 매물 문맥을 세 모듈 사이로 전달하고 저장된 가격·안전 결과를 초기 카드 계약으로 연결했습니다. 실제 HTTP consumer test가 없고 `workersCalled`/`intent` drift가 남아 있어 완전한 E2E 계약으로 표현하지 않습니다.
- 네 시설 유형의 응답·인증·좌표 차이를 client/parser 경계에서 격리하고, 고정 반경의 source row 수를 사전 계산했습니다. 결과는 범죄 위험도가 아닌 미보정 시설 접근성 보조 지표입니다.

## 기재 범위와 제한

- 본인 직접 기여로 확인된 것은 데이터 파이프라인, Spring·FastAPI 연동, 초기 카드 연결, 안전시설 수집·계산, 지도 backend·초기 frontend, 법률 ingestion·검색, 배포 workflow입니다.
- JWT core, LangGraph Supervisor, 최종 챗봇·안전 카드 UI와 세션 UX는 팀원 기여이므로 팀 결과와 개인 기여를 구분합니다.
- 최종 프로젝트 기간은 2026.05~06으로 표기합니다. 현재 저장소에서 직접 검증되는 구현 이력은 2026-06-12~06-26이며, 그 이전 GitLab 이력 유실 경위는 직접 답변으로만 분류합니다.
- 안전 배치는 Cloud Run에서 짧은 간격으로 일시 활성화한 뒤 끄고 어떤 안전시설 row의 Supabase 적재를 확인했습니다. 실행 로그·source별 건수·현재 DB snapshot이 없고 제시 명령에는 경찰 source opt-in도 없어 운영 4종 성공으로 확대하지 않습니다.
- 테스트 파일과 PR의 과거 실행 기록은 존재하지만, 사용자 답변상 관련 테스트 코드는 Codex가 생성했습니다. 정확한 대상 파일과 사람이 설계·검토한 범위가 특정되지 않아 테스트 직접 작성 성과로 기재하지 않습니다.
