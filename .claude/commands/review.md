# /review — 프로젝트 규칙 기반 코드 리뷰

현재 변경사항(git diff)을 살만해 프로젝트 규칙에 맞게 자동 리뷰합니다.

## 리뷰 체크리스트

### 1. ARCHITECTURE.md 폴더 구조 준수
- `docs/ARCHITECTURE.md` 의 디렉토리 구조와 파일이 올바른 위치에 있는가?
- 비즈니스 로직이 Service 클래스에 있고, Controller/Router는 위임만 하는가?
- FastAPI가 있는 backend-ai에만 LangGraph/LLM 코드가 있는가?

### 2. ADR 기술 스택 준수
- `docs/ADR.md` 의 결정 사항을 위반하지 않는가?
- Frontend가 FastAPI를 직접 호출하고 있지는 않은가? (ADR-008)
- Claude API 응답 파싱 시 코드블록 strip 처리가 있는가? (ADR-007)
- Supabase JWT 검증이 Spring Security Filter에서 이루어지는가? (ADR-005)

### 3. 테스트 작성 여부
- 새로 추가된 Service/비즈니스 로직에 대응하는 테스트가 있는가?
- 테스트 없이 구현 파일만 추가된 경우 경고를 출력한다.

### 4. CLAUDE.md CRITICAL 규칙 준수
- API 키·시크릿이 코드에 하드코딩되어 있지 않은가?
- 커밋 메시지가 `type(scope): 한글 설명 (#이슈번호)` 형식인가?
- MVP 제외 사항이 구현에 포함되어 있지 않은가?

### 5. UI 안티패턴 (Frontend 변경 시)
- `docs/UI_GUIDE.md` 의 안티패턴이 사용되었는가?
  - Glass morphism / 보라색 그라데이션 텍스트 / 네온 글로우
  - lucide-vue-next 외 아이콘 라이브러리 사용
  - 반응형 prefix 사용 (MVP 제외)

## 리뷰 결과 형식

각 카테고리별로 결과를 출력합니다:

```
✅ ARCHITECTURE: 폴더 구조 준수
⚠️  TESTS: UserService 추가됨, 대응 테스트 없음
❌ CRITICAL: API 키 하드코딩 발견 — backend/src/.../Config.java:42
✅ ADR: 기술 결정 준수
✅ UI: 안티패턴 없음
```

`❌` 항목은 반드시 수정 후 커밋해야 합니다.  
`⚠️` 항목은 수정을 권장하지만 진행은 가능합니다.

## 실행 방법

```
/review
```

`git diff HEAD` 를 기준으로 변경사항을 분석합니다.  
특정 파일만 검토하려면: `/review backend/src/main/java/service/PropertyService.java`
