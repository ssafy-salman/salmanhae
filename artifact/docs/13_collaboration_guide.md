# 13. 협업 가이드

## 개요

코드는 각자 자유롭게 짠다 (직접 or AI 활용).
GitHub 작업(이슈·브랜치·커밋·PR)은 항상 스크립트로 처리한다.

어떤 AI 도구를 쓰든 GitHub 히스토리가 동일한 컨벤션으로 쌓이는 게 목표다.

---

## 프로젝트 구조

```
frontend/
├── CLAUDE.md        ← Claude Code용 지시 파일 (이다인)
├── AGENTS.md        ← Codex용 지시 파일 (팀원)
└── scripts/
    ├── new-issue.sh ← 이슈 생성 + 브랜치 생성
    └── ship.sh      ← 커밋 + PR 생성

backend/
├── CLAUDE.md
├── AGENTS.md
└── scripts/
    ├── new-issue.sh
    └── ship.sh

artifact/docs/       ← 두 사람이 공통으로 읽는 맥락 문서
```

---

## 작업 흐름

### 1. 작업 시작

```bash
bash scripts/new-issue.sh
```

실행하면 프롬프트가 뜬다.

```
기능 ID (없으면 엔터): F-1
타입 (FEAT/BUG/CHORE/REFACTOR): FEAT
제목: 지도 범위 내 매물 마커 표시
```

자동으로 처리되는 것:
- GitHub 이슈 생성 — `[F-1][FEAT] 지도 범위 내 매물 마커 표시`
- 브랜치 생성 및 checkout — `feature/1-property-api`

### 2. 코드 작업

직접 짜도 되고, AI한테 시켜도 된다.  
AI를 쓴다면 작업 전에 `artifact/docs/` 폴더를 읽게 한다.

```
이 파일들을 먼저 읽어줘:
- artifact/docs/PRD.md
- artifact/docs/ARCHITECTURE.md
그 다음 [작업 내용] 구현해줘.
```

### 3. 작업 완료

```bash
bash scripts/ship.sh
```

자동으로 처리되는 것:
- 변경 파일 확인 및 stage
- 커밋 생성 — `feat(property): 매물 마커 표시 구현 (#3)`
- push
- PR 생성 — 이슈 자동 연결 (`closes #3`)

---

## 이슈 / 커밋 / PR 형식

### 이슈 제목

```
[FEAT][F-1] 지도 범위 내 매물 마커 표시
[BUG][F-6] 로그인 토큰 만료 시 리다이렉트 안됨
[CHORE] Spring Boot 프로젝트 초기 세팅
```

- 기능 작업이면 F-N 포함, 기타 작업이면 타입만
- F-N 기준은 `docs/02_mvp_scope.md` 참고

### 커밋 메시지

```
feat(property): 매물 마커 표시 구현 (#3)
fix(auth): 토큰 만료 리다이렉트 처리 (#7)
test(safety): SafetyFacilityService 단위 테스트 (#5)
```

- `ship.sh`가 자동 생성하므로 직접 쓸 일은 거의 없음

### 브랜치

```
feature/1-property-api
feature/2-safety-api
fix/map-marker-duplicate
```

- `new-issue.sh`가 자동 생성

---

## AI 사용 시 주의사항

| | Claude Code (이다인) | Codex (팀원) |
|---|---|---|
| 지시 파일 | `CLAUDE.md` 자동 로드 | `AGENTS.md` 자동 로드 |
| 맥락 문서 | 작업 전 `artifact/docs/` 읽힐 것 | 작업 전 `artifact/docs/` 읽힐 것 |
| GitHub 작업 | `scripts/` 사용 | `scripts/` 사용 |

AI한테 코드 짜달라고 할 때 GitHub 작업(커밋, PR)까지 시키지 말 것.  
GitHub 작업은 항상 스크립트로만 처리한다.

---

## 브랜치 전략

```
main ← develop ← feature/*, fix/*
```

- `feature/*` → `develop`: Squash merge
- `develop` → `main`: Merge commit
- 셀프 머지 금지 — 상대방 approve 후 merge
