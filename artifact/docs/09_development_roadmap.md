# 09. 개발 순서

## MVP

### 1단계. 더미 매물 API + 지도 연동
- 더미 매물 DB seed
- `GET /api/v1/properties` (지도 범위 조회)
- `GET /api/v1/properties/{id}` (매물 상세)
- 네이버지도 마커 표시, 필터, 클러스터링

### 2단계. 안전시설 API + 레이어
- 생활안전지도 공공 API 5종 배치 수집 → `safety_facility` 저장
- `GET /api/v1/safety/facilities`
- 지도 안전 레이어 토글 (CCTV, 비상벨, 보안등, 치안시설, WMS)

### 3단계. 실거래가 API + 레이어
- 국토교통부 실거래가 8종 배치 수집 → `transaction_history` 저장
- `GET /api/v1/properties/{id}/transactions`
- 지도 실거래가 레이어 토글

### 4단계. 안전 점수 계산
- 매물별 반경 안전시설 개수 계산
- `property_score_stat` 저장
- `GET /api/v1/properties/{id}/safety-summary`

### 5단계. 인증 (Supabase Auth)
- 회원가입 / 로그인 / 로그아웃
- Spring Security Filter → Supabase JWT 검증
- 비로그인 F-1 허용, 로그인 필요 API 분리

### 6단계. AI 에이전트 — 매물 추천 (LangGraph)
- LangGraph 의도 분류 노드
- `search_properties` 툴 → Spring Boot 호출
- 자연어 입력 → 매물 추천 카드 반환 → 지도 마커 연동

### 7단계. AI 에이전트 — 법률 RAG
- 주택임대차보호법·전세사기특별법 문서 청킹 → pgvector 저장
- `legal_rag` 툴 → 유사도 검색 → LLM 해설 생성
- 왼쪽 패널 법령 카드 표시

### 8단계. AI 에이전트 — 시세·안전 분석
- `analyze_price` 툴 → Spring Boot 호출
- `analyze_safety` 툴 → Spring Boot 호출
- LLM 요약 응답 생성

### 9단계. 찜하기
- `wishlist` 테이블
- `POST/GET/DELETE /api/v1/wishlist`
- 지도 찜 마커 표시, 찜 목록 페이지

---

## 1.5차

- F-4 뉴스 RAG: 딥서치 API → pgvector 인덱싱 → 뉴스 카드 표시
- F-5 HUG 간이 계산: 공시가격 API 연동 → HUG/HF/SGI 추정
- F-6 소셜 로그인: 네이버 OAuth2.0
- F-8 대화 세션·요약 메모리: LangGraph 상태 관리, `conversation_session`·`conversation_message` 테이블

---

## 확장

- 실제 매물 크롤링 또는 제휴 API 연동
- 등기부등본 Claude Vision API 분석
- 정교한 HUG/HF/SGI 판정 (등기부등본 데이터 기반)
- 커뮤니티 (지역/건물 후기)
- 개인화 추천 (찜·조회 이력 기반)
