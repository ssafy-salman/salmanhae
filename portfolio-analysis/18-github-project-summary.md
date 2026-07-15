# 살만해 — GitHub·포트폴리오 소개 섹션

## 한 줄 소개

청년 1인 가구가 지도에서 매물을 탐색하며 실거래가, 주변 안전시설, 임대차 법령을 한 흐름에서 비교하도록 만든 AI 기반 부동산 탐색 서비스입니다.

## 프로젝트 목적

집을 계약하기 전 사용자가 거래 정보, 생활 안전 관련 시설, 임대차 법령을 여러 서비스에서 따로 확인해야 하는 문제를 줄이는 것이 목표입니다. 외부 공공 API는 사용자 요청 때 직접 호출하지 않고 미리 수집·정규화한 데이터를 조회하며, 지도에서 선택한 매물은 AI 분석 문맥으로 전달합니다. 현재 매물은 실거래 건물과 가격 범위를 바탕으로 만든 `MVP_SYNTHETIC` 데이터이므로 실매물 중개 서비스가 아니라 탐색·분석 흐름을 검증한 MVP입니다.

## 핵심 기능

- 줌 단계에 따라 시·도, 시·군·구, 동, grid cluster, 개별 매물로 전환하는 지도 탐색
- 국토교통부 거래 데이터를 공통 모델로 변환해 통계와 검색용 매물을 생성하는 오프라인 적재 흐름
- 로그인 사용자의 선택 매물 ID를 Spring을 거쳐 FastAPI worker에 전달하는 AI 채팅
- 저장된 거래·가격 통계와 안전시설 접근성 값을 이용한 가격·안전 분석 카드
- 법령 chunk를 pgvector cosine 유사도로 검색해 답변 문맥과 최대 3개 근거 카드로 제공하는 법률 RAG
- 이메일 인증과 JWT access/refresh 인증, 브라우저 로컬 대화 세션

## 아키텍처 요약

```text
Vue 3 / Vercel
  ├─ Naver Maps JavaScript SDK
  └─ REST + JWT → Spring Boot / Cloud Run
                         ├─ PostgreSQL·pgvector / Redis
                         ├─ 내부 key → FastAPI·LangGraph / Cloud Run
                         │                 ├─ Spring의 매물·가격·안전 GET API
                         │                 └─ OpenAI-compatible chat·embedding API
                         └─ 안전시설 public API client와 조건부 사전 계산

Python offline pipeline → 국토교통부 API·Naver Geocoding → PostgreSQL
GitHub Actions → Spring/FastAPI 독립 배포·SSAFY GitLab 동기화
```

브라우저는 Spring REST API만 직접 호출합니다. Spring은 인증과 공개 API 경계를 담당하고 내부 HTTP로 FastAPI를 호출하며, FastAPI는 AI orchestration·pgvector 검색과 Spring의 저장 데이터 조회를 담당합니다.

## 기술 스택

| 영역 | 기술 | 실제 사용 목적 |
|---|---|---|
| Frontend | Vue 3, Vite, Pinia, Axios, Tailwind CSS, Naver Maps SDK | 지도·인증·채팅 화면, 상태 관리, Spring REST 호출 |
| Backend | Java 21, Spring Boot 3.5, Spring Security, JDBC, 일부 MyBatis | 공개 REST API, JWT 경계, 매물·가격·안전 조회, 외부 API 수집 |
| AI Backend | Python 3.12, FastAPI, LangGraph, httpx | 내부 AI API, worker orchestration, Spring·LLM·embedding 연동 |
| Data | Supabase PostgreSQL, pgvector, Redis | 거래·통계·합성 매물·안전시설·법령 vector, 인증 TTL 상태 |
| Infra | Docker, Cloud Run, Vercel, GitHub Actions | Spring/FastAPI 독립 배포, frontend 배포, GitLab sync |

## 내 주요 기여

- **거래 데이터 적재:** 8개 국토교통부 endpoint configuration, source별 field alias, 공통 20필드 normalizer, 거래 충돌 키, manifest raw-page 재사용, 네 테이블 conflict upsert를 구현했습니다. 별도 보존된 2026-06-24 실행 산출물에서 8개 source의 raw XML 25,953개와 정규화 거래 2,612,697건을 확인했습니다. 범위는 2025-07~2026-06, 세종을 제외한 16개 시·도·267개 시군구 코드입니다.
- **서비스 간 계약:** 팀원이 만든 JWT core 위에 Spring chat controller/service/client와 내부 API key를 연결하고, 선택 매물 ID가 FastAPI의 가격·안전 worker와 초기 Vue 분석 카드까지 전달되도록 구현했습니다. 최종 챗봇 UI·세션 UX와 Supervisor는 팀원이 담당했습니다.
- **안전시설 수집·계산:** CCTV·비상벨·보안등·경찰관서 client/parser, Web Mercator→WGS84 변환, 시설 upsert, bbox+Haversine 기반 300m/500m 시설 수와 규칙 기반 접근성 값 사전 계산을 구현했습니다. 가중치와 cap은 제가 정한 MVP 휴리스틱이며 수학·통계적으로 보정한 값이 아닙니다.
- **지도·검색:** 줌별 지역·cluster·property API와 Spring이 지원하는 keyword·단일 거래유형·매물유형·보증금·매매가 조건을 공통 JDBC filter로 연결했습니다. 후속 UI의 월세 범위·복수 거래유형은 현재 backend 계약과 차이가 남아 있습니다.
- **법률 RAG·배포:** 법령 800자 chunk/120자 overlap, content hash upsert, pgvector cosine top-k 검색, prompt-level grounding과 개발 환경의 제한적 fallback을 구현하고 Spring·FastAPI를 별도 Cloud Run 서비스로 배포하는 workflow를 구성했습니다.

## 실행·배포 정보

```bash
# Frontend
cd frontend && pnpm dev

# Spring Backend
cd backend && ./mvnw spring-boot:run

# AI Backend
cd backend-ai && uvicorn app.main:app --reload
```

- `develop`의 `backend/**` 변경은 Spring Cloud Run, `backend-ai/**` 변경은 FastAPI Cloud Run workflow를 각각 실행합니다.
- Frontend는 Vercel Git integration으로 배포하며, `main` push는 monorepo와 artifact subtree를 SSAFY GitLab로 동기화합니다.
- GitHub 기록에서 Spring 16회, FastAPI 9회, GitLab sync 8회의 성공 run이 확인됩니다. 이는 workflow 실행 결과이며 기능 E2E 성공률이나 무중단 배포를 의미하지 않습니다.
- 당시 안전 배치는 Cloud Run scheduler를 짧은 간격으로 일시 활성화한 뒤 다시 비활성화했습니다. 남은 한 명령 조각은 min/max instance 1과 CPU throttling 해제를 포함하지만 실제 적용 로그·source별 적재 건수는 보존되지 않았습니다.
- 환경변수에 DB, Redis, SMTP, JWT, 내부 API key, 외부 공공 API key, chat·embedding endpoint/model을 설정해야 합니다. 시크릿은 환경변수로 주입하고 버전 관리에서 제외해야 합니다.

## 기술적 한계

- 추가 실행 폴더에서 8개 거래 source와 2,612,697건 정규화는 확인했지만 세종이 없어 “전국 전체”라고 하지 않습니다. 코드는 여전히 API result code를 성공 checkpoint로 검사하지 않고 자동 retry/backoff·운영 scheduler가 없습니다.
- 무료 요금제 적재용 lite 산출물은 거래 19,386건과 `MVP_SYNTHETIC` 매물 4,000건입니다. 당시 pipeline의 Supabase 적재는 확인했지만 적재 subset·테이블별 row는 남지 않았고 현재 DB 연결도 timeout이므로 현재 row 수와 “매물 8,000건”은 확인되지 않았습니다.
- FastAPI는 `workersCalled` 등을 반환하지만 Spring consumer DTO는 이를 받지 않고 FastAPI에 없는 `intent`를 기대합니다. 메시지와 카드는 남을 수 있으나 metadata가 조용히 유실될 수 있어 공유 schema와 consumer contract test가 필요합니다.
- 배포 후 어떤 안전시설 row의 Supabase 적재는 확인했지만, source별 HTTP 상태·건수·시각은 없습니다. 남은 명령에는 경찰 source opt-in이 없고 보안등 URL·key, 비상벨 base URL, 공공데이터 key 인코딩도 현재 코드 계약과 충돌할 여지가 있어 네 source 성공으로 확대하지 않습니다. 접근성 값은 범죄 가능성이나 절대 치안을 나타내지 않습니다.
- 법률 RAG는 ingestion·검색 경로가 구현돼 있지만 현재 법령 데이터셋, embedding model, 검색·답변 품질 평가는 확인되지 않았습니다.
- 배포 workflow는 테스트를 필수 gate로 사용하지 않고 Spring image build는 테스트를 건너뜁니다. 배포 전에 Frontend/Spring/FastAPI test와 계약 검증을 묶어야 합니다.

## 관련 문서

- [상세 포트폴리오](./14-final-portfolio.md)
- [이력서용 요약](./15-resume-version.md)
- [자기소개서 사례](./16-self-introduction-stories.md)
- [면접 준비 자료](./17-interview-pack.md)
- [근거 색인](./19-evidence-index.md)
- [프로젝트 요구사항](../docs/01_PRD.md)
- [아키텍처](../docs/02_ARCHITECTURE.md)
- [API 명세](../docs/08_API_SPEC.md)
