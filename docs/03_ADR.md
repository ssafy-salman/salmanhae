# Architecture Decision Records

### ADR-001: AI 백엔드를 Spring Boot와 분리하여 Python FastAPI로 운영
**결정**: LangGraph + Claude API를 담당하는 Python FastAPI 서버를 별도 Cloud Run 서비스로 분리한다.  
**이유**: LangGraph, langchain-anthropic 등 AI 라이브러리 생태계가 Python 중심이고, JVM에서 동일 기능을 구현하면 유지보수 비용이 높다.  
**트레이드오프**: 서비스 간 HTTP 통신 레이턴시 추가, 두 런타임 관리 필요. Spring Boot → FastAPI 내부망 통신 장애 시 AI 기능 전체 불능.

### ADR-002: DB를 Supabase(PostgreSQL + pgvector)로 일원화
**결정**: 관계형 데이터와 벡터 임베딩을 Supabase 단일 인스턴스에서 관리한다.  
**이유**: 별도 벡터 DB(Pinecone, Weaviate) 운영 없이 pgvector 익스텐션으로 동일 DB에서 유사도 검색 가능. 인프라 복잡도 감소.  
**트레이드오프**: pgvector는 전용 벡터 DB 대비 인덱싱 성능이 낮다. 문서 수십만 건 이상 시 재검토 필요.

### ADR-003: 공공 API 데이터를 런타임 직접 호출 대신 배치 캐싱
**결정**: 국토교통부 실거래가(8종)와 생활안전지도(4종) 데이터를 Spring Scheduler 배치로 사전 수집하여 PostgreSQL에 저장한다.  
**이유**: 공공 API는 응답 속도가 느리고 일일 호출 한도 제한이 있어 사용자 요청 시 직접 호출 시 UX 저하 및 장애 가능성이 있다.  
**트레이드오프**: 배치 주기만큼 데이터 최신성 지연 (실거래가: 1일, 안전시설: 7일). 신규 매물 등록 직후 데이터가 없을 수 있다.

### ADR-004: 안전 점수를 API 요청 시 계산하지 않고 배치로 사전 계산
**결정**: 매물별 반경 안전시설 개수 집계와 점수 계산을 배치에서 수행하여 `property_score_stat`에 저장한다.  
**이유**: 반경 쿼리(PostGIS ST_DWithin)를 매 요청마다 실행하면 응답 지연이 크다. 안전시설 데이터는 자주 바뀌지 않아 실시간 계산 불필요.  
**트레이드오프**: 새 안전시설이 추가되어도 다음 배치까지 점수에 반영되지 않는다.

### ADR-005: 인증을 Supabase Auth로 위임하고 Spring Boot에서 JWT 검증만 수행
**결정**: 회원가입·로그인은 Supabase Auth API를 Spring Boot가 래핑하여 프록시하고, 이후 모든 요청에서 Spring Security Filter가 Supabase JWT를 검증한다.  
**이유**: Auth 로직 직접 구현(비밀번호 해싱, 토큰 발급 등) 대비 개발 시간과 보안 리스크 감소.  
**트레이드오프**: Supabase Auth 장애 시 신규 로그인 불가. JWT 검증은 공개키 로컬 캐싱으로 완화.

### ADR-006: LangGraph 의도 분류를 단일 노드에서 처리
**결정**: 사용자 입력을 4가지 의도(매물 추천/법률 상담/시세 분석/안전 분석)로 분류하는 노드를 LangGraph 그래프 진입점에 배치하고, 의도에 따라 엣지가 분기된다.  
**이유**: 의도별 툴이 달라 단일 ReAct 루프보다 명시적 그래프 분기가 디버깅과 유지보수에 유리하다.  
**트레이드오프**: 의도 분류 실패 시 잘못된 툴 호출. 모호한 질문(예: "강남 안전한가요?"가 안전 분석인지 매물 추천인지)은 추가 처리 필요.

### ADR-007: Claude API 응답 파싱 시 JSON 코드블록 strip 처리
**결정**: Claude API가 JSON을 반환할 때 ```json ... ``` 코드블록으로 감싸는 경우가 있으므로 파싱 전 반드시 코드블록을 제거한다.  
**이유**: 코드블록 미처리 시 json.loads()에서 JSONDecodeError 발생. 프롬프트로 방지할 수 있지만 100% 보장이 안 되므로 파싱 단에서 방어 처리.  
**트레이드오프**: 없음 (순수 방어 코드).

### ADR-008: Frontend가 FastAPI를 직접 호출하지 않는다
**결정**: 모든 AI 에이전트 요청은 Frontend → Spring Boot → FastAPI 경로를 거친다.  
**이유**: FastAPI는 내부 서비스로 JWT 검증 로직 중복 없이 Spring Boot 필터에 위임할 수 있고, CORS 설정과 인증 정책을 Spring Boot에서 일관 관리한다.  
**트레이드오프**: Spring Boot가 단순 프록시 역할을 추가로 수행. 레이턴시 1홉 증가.
