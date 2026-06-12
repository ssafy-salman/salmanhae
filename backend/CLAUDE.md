# 살만해 — Backend

## 서비스
청년 1인 가구 안심 주거 탐색 서비스.
Spring Boot REST API + Supabase Auth + PostgreSQL.

## 기술 스택
- Java 17, Spring Boot 3, MyBatis
- PostgreSQL (Supabase), pgvector
- Supabase Auth (JWT 검증), Spring Security
- Maven

## 작업 전 반드시 읽을 것
../artifact/docs/ 의 모든 파일

## CRITICAL 규칙
- CRITICAL: 작업 시작 전 반드시 `bash scripts/new-issue.sh` 실행
- CRITICAL: 작업 완료 후 반드시 `bash scripts/ship.sh` 실행
- CRITICAL: GitHub 작업(커밋, PR)은 반드시 scripts/ 를 통해서만 할 것 — 직접 git commit / gh pr create 금지
- CRITICAL: API 응답 형식은 반드시 `06_rest_api_spec.md` 기준 준수 (`{ data, message }` 래퍼)
- CRITICAL: 에러 응답은 반드시 `{ code, message, status }` 형식 사용
- CRITICAL: 패키지 구조는 `04_backend_architecture.md` 기준 준수

## 명령어
- 빌드: `mvn package`
- 실행: `mvn spring-boot:run`
- 테스트: `mvn test`
