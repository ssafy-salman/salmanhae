# 살만해 — Backend

![로고](./docs/salman_full_logo.png)

AI 에이전트 기반 부동산 탐색 서비스 **살만해**의 Spring Boot 백엔드입니다.

---

## 기술 스택

| 구분 | 사용 기술 |
| --- | --- |
| Language | Java 17 |
| Framework | Spring Boot |
| Database | PostgreSQL + pgvector |
| Auth | Supabase Auth (JWT 검증) |
| Build | Maven |
| API | REST API |
| Batch | Spring Scheduler |

---

## 역할

- 공공데이터 배치 수집 및 DB 저장 (실거래가 8종, 안전시설 5종)
- 지도 범위 기반 매물·안전시설 조회
- 실거래가 조회 및 시세 분석
- 안전 점수 계산
- 찜하기 CRUD
- Supabase JWT 검증 (Spring Security Filter)
- FastAPI LangChain 서비스에서 호출하는 Tool API 제공

---

## API 목록

### Property
| Method | URL | 인증 | 설명 |
| --- | --- | --- | --- |
| `GET` | `/api/v1/properties` | 공개 | 지도 범위 내 매물 조회 |
| `GET` | `/api/v1/properties/{id}` | 공개 | 매물 상세 조회 |
| `GET` | `/api/v1/properties/{id}/transactions` | 공개 | 매물 주변 실거래가 조회 |
| `GET` | `/api/v1/properties/{id}/safety-summary` | 공개 | 매물 안전 요약 조회 |

### Safety
| Method | URL | 인증 | 설명 |
| --- | --- | --- | --- |
| `GET` | `/api/v1/safety/facilities` | 공개 | 지도 범위 내 안전시설 조회 |

### Price Analysis
| Method | URL | 인증 | 설명 |
| --- | --- | --- | --- |
| `GET` | `/api/v1/price-analysis` | 공개 | 지역 시세 분석 |

### AI 에이전트 (FastAPI LangChain Tool)
| Method | URL | 인증 | 설명 |
| --- | --- | --- | --- |
| `POST` | `/api/v1/chat` | 필요 | AI 에이전트 챗봇 |
| `GET` | `/api/v1/hug-eligibility` | 필요 | HUG 간이 계산 (1.5차) |

### Auth
| Method | URL | 인증 | 설명 |
| --- | --- | --- | --- |
| `POST` | `/api/v1/auth/signup` | 공개 | 회원가입 |
| `POST` | `/api/v1/auth/login` | 공개 | 로그인 |
| `POST` | `/api/v1/auth/logout` | 필요 | 로그아웃 |

### Wishlist
| Method | URL | 인증 | 설명 |
| --- | --- | --- | --- |
| `GET` | `/api/v1/wishlist` | 필요 | 찜 목록 조회 |
| `POST` | `/api/v1/wishlist` | 필요 | 찜하기 |
| `DELETE` | `/api/v1/wishlist/{id}` | 필요 | 찜 삭제 |

### Session (1.5차)
| Method | URL | 인증 | 설명 |
| --- | --- | --- | --- |
| `GET` | `/api/v1/sessions` | 필요 | 대화 세션 목록 |
| `GET` | `/api/v1/sessions/{id}/messages` | 필요 | 세션 메시지 조회 |

---

## 실행 방법

```bash
mvn spring-boot:run
```

기본 포트: `8080`

---

## 상세 문서

- `docs/` 폴더 참고
- 전체 아키텍처: `artifact/docs/04_backend_architecture.md`
- API 명세: `artifact/docs/06_rest_api_spec.md`
- 데이터 모델: `artifact/docs/05_domain_model.md`
- 배치 전략: `artifact/docs/07_batch_ingestion.md`
- 인증 정책: `artifact/docs/08_security_policy.md`
- Git 컨벤션: `artifact/docs/12_git_convention.md`
