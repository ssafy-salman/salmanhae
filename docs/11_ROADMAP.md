# 11. ROADMAP

## MVP

### 1단계. 실거래가 anchor 기반 더미 매물 API + 지도 연동
- 국토교통부 실거래가에서 실제 건물·지역 anchor를 추출하고 지오코딩 좌표를 붙인 뒤 더미 매물 seed 생성
- 더미 매물 가격은 같은 건물 또는 같은 법정동·유형·면적대 실거래가 범위를 기준으로 생성
- 생성된 더미 매물을 `properties`에 저장하고, 원천 실거래가 row는 `transaction_history`에 저장
- 운영 단계 매물 수급은 제휴 피드, 중개사/임대인 등록, 합법 검토된 수집 데이터 중 확정
- `GET /api/v1/properties` (지도 범위 조회)
- `GET /api/v1/properties/{id}` (매물 상세)
- 네이버지도 마커 표시, 기본 필터

### 2단계. 안전시설 API + 레이어
- 생활안전지도/재난안전 공공 API 4종 월 1회 배치 수집 → `safety_facility` 저장
- `GET /api/v1/safety/facilities`
- 지도 안전 레이어 토글 (CCTV, 비상벨, 보안등, 치안시설)

### 3단계. 실거래가 API + 지도 평균 레이어
- 국토교통부 실거래가 8종 배치 수집 고도화 → `transaction_history` 갱신
- 시/도·시/군/구·읍/면/동 평균 계산 → `region_price_stat` 저장
- `GET /api/v1/properties/{id}/transactions`
- `GET /api/v1/map/viewport`
- 지도 줌 레벨별 실거래가 평균 표시

### 4단계. 안전 점수 계산
- 매물별 반경 안전시설 개수 계산
- `property_score_stat` 저장
- `GET /api/v1/properties/{id}/safety-summary`

### 5단계. 인증 (Spring Security JWT)
- 회원가입 / 로그인 / 로그아웃 / 토큰 갱신
- Spring Security Filter → JWT 서명·만료 검증
- BCrypt 비밀번호 해싱, 리프레시 토큰 DB 저장
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

- WMS 기반 안전 레이어
- 공인중개사 제휴 API 연동
- 등기부등본 Claude Vision API 분석
- 정교한 HUG/HF/SGI 판정 (등기부등본 데이터 기반)
- 커뮤니티 (지역/건물 후기)
- 개인화 추천 (찜·조회 이력 기반)
