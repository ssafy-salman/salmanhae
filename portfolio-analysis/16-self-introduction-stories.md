# 살만해 자기소개서 경험 소재

> 작성 원칙: 코드·Git·추가 실행 산출물을 우선하고, 개발 기간·기능 분담·배포 확인처럼 저장소 밖 사실은 사용자 직접 답변으로 표시했다. 기억과 산출물이 충돌하는 숫자는 더 좁은 값을 사용했다. Q6의 테스트 코드는 사용자 답변상 Codex가 생성했지만 대상 파일과 사람 검토 범위는 특정되지 않으므로, 어느 테스트도 “직접 작성”했다고 확대하지 않는다.

## 1. 기술적 문제 해결 경험 — 서로 다른 안전시설 API를 하나의 저장 경로로 통합

살만해에서 CCTV·비상벨·보안등·Safemap 치안시설 데이터를 수용하는 Spring 서버 영역을 맡았습니다. 배포 후 직접 확인하는 과정에서 CCTV CSV 403, Cloud Run의 CCTV·비상벨 401과 Safemap 키 오류를 만났고, fixture·응답 계약에는 WGS84와 `XMAP/YMAP/GEOM` 경로가 함께 있었습니다. 저는 문제를 전달 형식, 인증, 응답 구조, 좌표계로 나눴습니다. CCTV는 JSON OpenAPI로 전환하고 source별 client/parser가 필드와 좌표 정규화를 책임지게 했습니다. 보안등 응답에서 WGS84가 없을 때 Web Mercator로 가정한 좌표는 Java `Math`로 역변환하고, 누락되거나 전지구 위·경도 범위를 벗어난 값은 제외했습니다. 별도 키가 필요한 Safemap은 opt-in으로 격리했습니다. 다만 concrete client가 일부 HTTP·parse 오류를 빈 목록이나 부분 목록으로 축소해 실패가 0건처럼 보일 수 있다는 한계가 남았습니다. Git에는 관련 fixture·회귀 테스트가 있고, 별도로 사용자는 Q6의 관련 테스트를 Codex가 생성했다고 답했지만 정확한 파일·case와 사람 검토 범위는 연결하지 못했습니다. 사용자는 scheduler를 잠시 켜 어떤 안전시설 row의 Supabase 적재를 확인했다고 답했지만, 실행 로그와 source별 건수는 남아 있지 않습니다. 따라서 네 source의 운영 성공이나 401 완전 해결로 확대하지 않습니다. 이 경험으로 외부 API 연동에서는 정상 응답 매핑만큼 실패 의미와 관측 가능한 증거가 중요하다는 점을 배웠습니다.

## 2. 협업 경험 — GitHub 개발과 GitLab 제출 흐름을 모노레포로 정렬

2인 팀은 frontend/backend 전담이 아니라 기능 단위로 나눴고, 저는 F-1 지도·데이터, F-3 법률 RAG, F-4 시세·안전을 여러 레이어에 걸쳐 구현했습니다. 모듈과 제출 산출물이 분리돼 API 계약·문서의 반영 시점이 어긋날 위험이 있어 GitHub 모노레포를 개발 기준점으로 정하고 Vue·Spring·FastAPI·문서를 같은 변경 단위에서 다루도록 통합했습니다. `main` push 때 전체 저장소를 GitLab으로, `artifact/`는 subtree로 별도 동기화하고 두 backend 배포는 경로별로 분리했습니다. Git에는 이 workflow들의 반복 성공 이력이 있지만 기능 E2E 성공을 뜻하지는 않습니다. 팀원은 JWT core·Supervisor·최종 UI를 구현했고, 사람 리뷰 없이 CodeRabbit이 자동 리뷰를 담당했다는 점도 기록과 일치합니다. 반면 required approval·test gate가 없어 silent contract drift를 막지 못했습니다. 협업 자동화에는 배포뿐 아니라 책임 경계와 검증 조건이 포함돼야 함을 배웠습니다.

## 3. 도전적인 목표 경험 — 임시 seed를 반복 실행 가능한 거래 데이터 파이프라인으로 전환

실제 중개 매물 없이도 실거래 기반 탐색을 보여 주는 것이 목표였습니다. 초기 seed와 분할 SQL은 화면을 빠르게 열었지만, 생성 파일이 커지고 중복 key로 적재가 실패해 지역·기간 확장에 맞지 않았습니다. 저는 국토교통부 8개 거래 source를 설정으로 분리하고 source별 alias를 공통 모델에서 흡수했습니다. 위치·건물·계약일·면적·층·금액 조합의 결정적 key와 DB unique constraint를 두고 거래·지역 통계·건물 통계·합성 매물을 한 connection에서 conflict upsert하도록 구성했습니다. 추가 보존 폴더에서 정규화 거래 2,612,697행을 확인했지만 세종이 빠진 오프라인 파일 산출물이고, 당시 적재 subset·현재 DB·rollback은 확인되지 않았습니다. 그래서 “전국 전체”, “현재 운영 DB의 261만 건”, “매물 8,000개”로 넓혀 말하지 않습니다. 이 경험으로 큰 숫자보다 범위·환경·확인 방법을 함께 남겨야 방어 가능한 성과가 된다는 점을 배웠습니다.

## 4. 실패 또는 아쉬운 점과 개선 경험 — 서비스 간 계약이 조용히 어긋난 문제

제가 Spring–FastAPI–Frontend 사이에 `selectedPropertyId`와 `analysisCards`의 초기 코드 경로를 연결했을 때 성공·미선택·API 실패 fixture를 다루는 모듈별 mock 테스트가 함께 들어갔습니다. 그러나 어느 테스트도 실제 FastAPI JSON을 실제 `AiAgentClient`가 HTTP로 역직렬화하는 경계를 통과하지 않았습니다. 이후 팀원이 router를 Supervisor로 확장하면서 FastAPI는 `workersCalled`를 반환하게 됐지만 Spring과 frontend consumer가 함께 갱신되지 않았습니다. 현재 기본 DTO 매핑에서는 추가 metadata가 버려지고 Spring의 nullable `intent`는 `null`, Frontend에서는 빈 문자열이 될 수 있습니다. 공통 답변과 카드가 남을 가능성은 있지만 실제 배포 smoke가 없어 사용자 장애로 단정하지 않습니다. 이런 조용한 계약 불일치를 최종 통합에서 막지 못한 점이 가장 큰 아쉬움입니다. 다시 설계한다면 자동 생성되는 FastAPI OpenAPI를 versioned contract artifact로 관리하고, 실제 `AiAgentClient` consumer test와 같은 fixture를 쓰는 frontend normalizer test를 CI 배포 선행 조건으로 묶겠습니다. 이 경험으로 테스트 수보다 변경이 서비스 경계를 통과하는 모습을 검증하는지가 중요하다는 점을 배웠습니다.

## 5. 백엔드 직무 역량 경험 — 지도 목록·집계·검색 상태를 하나의 계약으로 맞춤

지도 화면은 좁은 범위에서는 개별 매물을 보여 주지만 넓은 범위에서 모두 반환하면 응답량과 가독성이 나빠집니다. 저는 Spring에서 zoom에 따라 시·도, 시·군·구, 읍·면·동, grid cluster, 개별 매물의 다섯 응답 모드를 선택하고 JDBC 집계 쿼리와 Vue marker까지 연결했습니다. 이후 Issue에 기록된 frontend 목록과 지역 marker의 keyword 불일치를 기준으로 원인을 특정하고 수정했습니다. 기존의 단일 거래유형·매물유형·보증금·매매가 조건 builder에 keyword를 추가하고, public bounds와 region·cluster·property query가 같은 조건을 쓰도록 정렬했습니다. 자동 리뷰에서 공백 keyword와 SQL `LIKE`의 `%`, `_`가 wildcard로 해석되는 문제가 드러나 frontend trim과 `ESCAPE '!'` 기반 literal 처리를 보강했습니다. no-result와 payload·marker label을 다루는 frontend/Spring 테스트와 후속 diff가 존재합니다. 그 결과 당시 서버가 지원한 조건에서는 목록과 집계가 같은 검색 상태를 표현했습니다. 최종 UI의 월세 범위와 복수 거래유형은 Spring 계약과 다시 맞춰야 합니다. 이 경험으로 백엔드 역량은 API 하나가 아니라 조회 의미, SQL 안전성, aggregate와 소비 계약을 함께 맞추는 능력임을 배웠습니다.

## 활용 시 주의할 선

- 안전 사례에서 “401을 완전히 해결했다”거나 “네 source가 운영에서 모두 성공했다”고 말하지 않는다.
- 파이프라인 사례에서 8개 source 실행과 2,612,697건 정규화는 말할 수 있지만, 세종이 빠진 범위를 “전국 전체”로 넓히거나 lite 매물 4,000건을 8,000건으로 바꾸지 않는다. exactly-once라고도 표현하지 않는다.
- 협업 사례에서 사람 간 리뷰·갈등·회의 내용을 추정하지 않는다.
- 계약 사례에서 현재 `workersCalled` 불일치를 해결했다고 말하지 않는다.
- 지도 사례에서 최종 UI의 모든 필터가 서버와 일치한다고 말하지 않는다.
