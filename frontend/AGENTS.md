# 살만해 — Frontend

## 서비스
청년 1인 가구 안심 주거 탐색 서비스.
지도 기반 매물 탐색 + AI 에이전트 챗봇.

## 기술 스택
- Vue 3 (Composition API, `<script setup>`)
- Vite 5, TailwindCSS 3, Pinia 2, Vue Router 4
- Axios (Supabase JWT 인터셉터 포함)
- 네이버지도 SDK, @lucide/vue

## 작업 전 반드시 읽을 것
../artifact/docs/ 의 모든 파일

## CRITICAL 규칙
- CRITICAL: 작업 시작 전 반드시 `bash scripts/new-issue.sh` 실행
- CRITICAL: 작업 완료 후 반드시 `bash scripts/ship.sh` 실행
- CRITICAL: GitHub 작업(커밋, PR)은 반드시 scripts/ 를 통해서만 할 것 — 직접 git commit / gh pr create 금지
- CRITICAL: API 응답은 `{ data, message }` 래퍼 형식 — `response.data.data` 로 접근
- CRITICAL: 전역 상태는 Pinia store 에서만 관리 (mapStore, authStore, chatStore)
- CRITICAL: src/ 폴더 구조는 docs/01_frontend_development_plan.md 기준 준수
- CRITICAL: Recommend.vue, Diagnosis.vue 는 이전 프로토타입 — MVP 작업 시 수정하지 말 것
- CRITICAL: 외부 API 키는 프론트에 두지 않음 — 네이버지도 클라이언트 키만 환경변수로 관리

## 명령어
- 개발 서버: `pnpm dev`
- 빌드: `pnpm build`
- 미리보기: `pnpm preview`
