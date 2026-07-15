# 조사 자료와 범위 감사

## 1. 조사 기준

- 조사일: 2026-07-10 (Asia/Seoul)
- 대상 저장소: `ssafy-salman/salmanhae`
- 로컬 경로: `C:\Users\SSAFY\Documents\Projects\salmanhae`
- 신뢰도 표기:
  - **확인됨**: 코드, 실제 diff, GitHub 객체, 실행 기록 또는 최종 산출물로 직접 확인
  - **정황상 유력**: 여러 근거가 일치하지만 작성자의 의도나 운영 상태를 직접 확인하지 못함
  - **확인 필요**: 저장소 밖 정보 또는 실행 환경 확인이 필요

조사 시작 시 애플리케이션 작업 트리는 깨끗했다. 원격 기록 누락을 줄이기 위해 요청에서 허용한 `git fetch --all --prune --tags`만 실행했으며, 브랜치 전환·reset·rebase·merge·cherry-pick·commit·push는 수행하지 않았다.

## 2. 저장소 상태

| 항목 | 확인 결과 | 신뢰도 |
|---|---|---|
| 현재 브랜치 | `develop` | 확인됨 |
| 현재 HEAD | `eee70e8c0fea5137b24131e80971d8703ad2912f` | 확인됨 |
| 추적 브랜치 | `origin/develop`과 동일 | 확인됨 |
| 원격 | `origin = https://github.com/ssafy-salman/salmanhae.git` | 확인됨 |
| 원격 기본 브랜치 | `develop` | 확인됨 |
| GitHub 기본 브랜치 | `develop` | 확인됨 |
| 태그 | 없음 | 확인됨 |
| 공개 여부 | public repository | 확인됨 |
| GitHub 생성일 | 2026-06-12 13:56 KST (`2026-06-12T04:56:31Z`) | 확인됨 |
| 최신 원격 commit | `origin/main`의 `1e51396` (2026-06-26 09:00 KST) | 확인됨 |
| 초기 작업 트리 | 변경 없음 | 확인됨 |
| 조사 완료 작업 트리 | `portfolio-analysis/`만 신규 untracked; 기존 source·문서 변경 없음 | 확인됨 |

원격 브랜치는 symbolic `origin/HEAD`를 제외하고 14개를 확인했다.

```text
origin/artifact-docs
origin/codex/fix-f1-map-search-regions
origin/develop
origin/feat/108-design
origin/feature/3-transaction-trend-panel
origin/fix/105-prompt
origin/main
origin/phase/102-fix-regional-price-analysis
origin/phase/82-auth-api-store
origin/phase/84-authview-connect
origin/phase/86-router-guard-header
origin/phase/88-chat-session-store
origin/phase/88-chat-session-ui
origin/phase/98-fix-supabase-set-local
```

`develop`은 266개 commit을 포함하고, 모든 ref를 합친 고유 commit은 267개다. 차이는 `origin/main`의 최종 merge commit `1e51396`이다.

## 3. 조사한 Git 범위

- 전체 고유 commit: 267개
- root commit: [`b993971`](https://github.com/ssafy-salman/salmanhae/commit/b9939714d7f03f6db4d66da7305afeab2f6b511f), 2026-06-12
- 모든 ref 기준 최신 commit: [`1e51396`](https://github.com/ssafy-salman/salmanhae/commit/1e51396fe1e157d2d4a8698186048ba9d26e4da5), 2026-06-26
- 분석한 이력: `git log --all`, first-parent 이력, 작성자별 이력, 주요 PR head commit, merge commit, 직접 `develop`에 들어간 commit
- diff 확인: 모노레포 전환, 데이터 파이프라인, 매물·지도 API, 법률 RAG, Spring-FastAPI 분석 연동, 안전시설 배치·점수, 배포·동기화, 최종 산출물 관련 핵심 commit

Git 저장소에 남은 개발 이력은 2026-06-12~2026-06-26이다. 최종 발표자료 1쪽은 프로젝트 기간을 **2026.05~2026.06**으로 표시한다. 따라서 포트폴리오의 개발 기간은 발표자료 기준 `2026.05~2026.06`, Git 근거가 직접 남은 기간은 `2026.06.12~2026.06.26`으로 구분한다.

## 4. Git 작성자와 본인 식별

로컬 설정:

```text
user.name  = HOKAGO-MEMORIES
user.email = minchotejava@gmail.com
```

전체 author 집계:

| author | email | commit 수 |
|---|---|---:|
| `HOKAGO-MEMORIES` | `minchotejava@gmail.com` | 66 |
| `김용휘` | `minchotejava@gmail.com` | 51 |
| `Kim YongHwi` | `minchotejava@gmail.com` | 47 |
| `crolvlee` | `leecrolv@gmail.com` | 82 |
| `crolvlee` | `135516362+crolvlee@users.noreply.github.com` | 20 |
| `coderabbitai[bot]` | bot noreply | 1 |

### 본인 대응 관계

다음 근거가 모두 일치하므로 `HOKAGO-MEMORIES`, `김용휘`, `Kim YongHwi`를 본인으로 식별했다.

1. 세 이름의 commit email이 모두 `minchotejava@gmail.com`이다.
2. 로컬 Git 설정이 `HOKAGO-MEMORIES / minchotejava@gmail.com`이다.
3. GitHub CLI가 `HOKAGO-MEMORIES` 계정으로 인증돼 있다.
4. GitHub 프로필 표시 이름이 `Kim YongHwi`이고, 해당 계정이 작성한 PR head commit email도 동일하다.
5. 최종 발표자료가 팀원을 `김용휘`, `이다인`으로 명시한다.
6. 발표자료의 김용휘 회고는 법률 RAG와 CI/CD 경험을 언급하며, 해당 영역의 PR·commit author가 위 계정과 일치한다.

따라서 본인 email 기준 commit은 164개다. 이 수에는 GitHub가 만든 merge commit도 포함되므로 코드량이나 기여 비율로 사용하지 않았다.

### author와 committer

- 로컬 작업 commit은 대체로 author와 committer가 동일하다.
- GitHub에서 생성된 merge commit은 author가 PR 병합 계정의 표시 이름이고 committer는 `GitHub <noreply@github.com>`이다.
- committer 집계에서 GitHub가 68개인 이유 때문에 merge commit author만으로 구현자를 판단하지 않았다.
- 예: PR #101의 merge commit author는 `crolvlee`지만, 기능 head commit [`b1e88cb`](https://github.com/ssafy-salman/salmanhae/commit/b1e88cbf41529202429a8973930cc53d80ce1802)은 `김용휘` 작성이다.

### Co-authored-by

- Co-authored trailer가 있는 commit: 39개
- `Claude Sonnet 4.6`: 38개
- `CodeRabbit`: 1개
- 본인 email의 commit 중 Co-authored trailer가 있는 commit: 0개

해당 39개는 모두 `crolvlee` 또는 bot author 쪽에 있으며 본인 기여로 귀속하지 않았다.

## 5. GitHub 조사 범위

GitHub CLI 인증과 `repo`, `workflow`, `read:org` 범위가 확인되어 PR·Issue·리뷰·Actions·Deployment를 조회했다.

| 항목 | 결과 |
|---|---:|
| 전체 PR | 62 |
| 병합 PR | 62 |
| 열린/병합되지 않은 PR | 0 |
| 본인 작성 PR | 46 |
| 팀원 작성 PR | 16 |
| 전체 Issue | 53 |
| 닫힌 Issue | 53 |
| 열린 Issue | 0 |
| 본인 작성 Issue | 37 |
| 팀원 작성 Issue | 16 |
| PR review 객체 | 56, 전부 `coderabbitai` |
| PR 일반 댓글 | 94 (`coderabbitai` 58, `vercel` 36) |
| Issue 댓글 | 0 |
| 사람의 review·일반 댓글 | 확인되지 않음 |

모든 PR은 `#1`~`#115` 사이의 번호를 사용한다. Issue와 PR이 번호 공간을 공유하므로 번호가 연속적이지 않다.

### 병합 방식과 보호 정책

- GitHub 설정은 merge commit, squash, rebase를 모두 허용한다.
- 62개 PR 중 61개 merge SHA는 부모가 2개인 merge commit이다.
- PR #1의 merge SHA [`8aaabf8`](https://github.com/ssafy-salman/salmanhae/commit/8aaabf89c20c2b51c78999b5797ae9671761b7f6)는 부모가 1개다. squash 계열 병합으로 보이지만 GitHub API에 명시적 방식이 남아 있지 않아 **정황상 유력**으로만 기록한다.
- `develop`, `main` 모두 GitHub branch protection이 설정돼 있지 않다.
- README는 셀프 merge 금지와 상대방 approve를 규칙으로 적지만, 사람 review/approval 기록은 확인되지 않았다. 문서 규칙의 실제 준수 여부는 확인 필요다.

### CI·배포·동기화 기록

GitHub Actions 실행 이력에서 다음 성공 기록을 확인했다.

| workflow | 성공 실행 수 | 최신 성공 |
|---|---:|---|
| Deploy backend to Cloud Run | 16 | 2026-06-25, `43d7623` |
| Deploy backend-ai to Cloud Run | 9 | 2026-06-26, `ba7c5da` |
| Sync monorepo to GitLab | 8 | 2026-06-26, `1e51396` |
| Dependency Graph | 3 | 2026-06-23 |

GitHub Deployment에는 Vercel Preview 62회, Production 38회가 남아 있고 최신 상태는 모두 `success`다. 이는 배포 작업 성공 근거이지 실제 사용자 시나리오 전체 정상 동작이나 운영 안정성 근거는 아니다.

PR check rollup에는 CodeRabbit 60회, Vercel 36회, Vercel Preview Comments 31회, 일부 Cloud Run/GitLab workflow 성공이 있다. 현재 workflow에는 테스트·lint gate가 없으므로 성공 배포가 전체 테스트 통과를 의미하지 않는다.

## 6. 읽은 주요 자료

### 프로젝트·설계 문서

- [`README.md`](../README.md)
- [`docs/01_PRD.md`](../docs/01_PRD.md)
- [`docs/02_ARCHITECTURE.md`](../docs/02_ARCHITECTURE.md)
- [`docs/03_ADR.md`](../docs/03_ADR.md)
- [`docs/05_GIT_GUIDE.md`](../docs/05_GIT_GUIDE.md)
- [`docs/06_EXTERNAL_APIS.md`](../docs/06_EXTERNAL_APIS.md)
- [`docs/07_DOMAIN_MODEL.md`](../docs/07_DOMAIN_MODEL.md)
- [`docs/08_API_SPEC.md`](../docs/08_API_SPEC.md)
- [`docs/09_BATCH_INGESTION.md`](../docs/09_BATCH_INGESTION.md)
- [`docs/10_SECURITY_POLICY.md`](../docs/10_SECURITY_POLICY.md)
- [`docs/11_ROADMAP.md`](../docs/11_ROADMAP.md)
- [`docs/14_DEPLOYMENT_GUIDE.md`](../docs/14_DEPLOYMENT_GUIDE.md)
- 기능별 `phases/` 지시서와 status/QA 문서

### 실제 구현 근거

- `backend/pom.xml`, `frontend/package.json`, `backend-ai/pyproject.toml`
- Dockerfile 2개, 환경변수 예시, application 설정
- GitHub Actions workflow 3개
- Spring controller/service/DAO/filter/scheduler와 테스트
- FastAPI route/schema, LangGraph graph/node/client/RAG와 테스트·평가 결과
- Vue router/store/api/view와 Node 테스트
- DB migration 6개와 데이터 파이프라인

### 제출 산출물

- `artifact/md/` 설계 문서
- `artifact/03. WBS.pdf` 4쪽: 텍스트 추출 및 렌더링 확인
- `artifact/관통발표자료.pdf` 19쪽: 전체 PNG 렌더링 후 주요 페이지 시각 확인
- 발표자료 확인 내용: 2인 팀, `김용휘·이다인`, 기간 `2026.05~2026.06`, 김용휘 회고의 RAG·CI/CD 언급

PDF는 렌더링으로 시각 검토했고, 그 내용은 코드·Git과 일치할 때만 확정 근거로 사용했다. 발표자료의 `Python 3.11` 표기는 현재 `pyproject.toml`/Dockerfile의 Python 3.12와 달라 현재 스택에는 반영하지 않았다.

## 7. 커밋 메시지와 실제 diff 교차 확인

핵심 기능 commit의 메시지는 대체로 diff와 일치했다. 다만 다음처럼 제목보다 실제 범위가 넓거나, 이력 해석에 주의할 사례가 있다.

| commit | 메시지 | 실제 diff와 주의점 |
|---|---|---|
| [`a259751`](https://github.com/ssafy-salman/salmanhae/commit/a259751af0a8d864368b56549f962c83eba589cb) | `멀티레포를 모노레포로 마이그레이션` | 세 모듈을 합친 것은 맞지만 legacy backend와 `target/*.class`, artifact gitlink까지 들어온 과도기 commit이다. 이후 정리 commit을 함께 봐야 한다. |
| [`f647cc6`](https://github.com/ssafy-salman/salmanhae/commit/f647cc68f5c61809819e5feb34b93e723fc9bc47) | `fix(harness)... (#9)` | 내용은 정확하지만 Property API PR #10 안에 별도 harness 수정이 섞였다. 한 PR=한 문제로 단순화하면 안 된다. |
| [`428f37e`](https://github.com/ssafy-salman/salmanhae/commit/428f37e373710b573d3ed1e55593e02a82aa8d64) | `test(ai): 안전 분석 경로 검증 및 문서화` | 테스트·문서 외에도 `llm_client`, `spring_client`, `supabase_client`, state, 서비스 production code를 수정했다. 실제 범위가 `test`보다 넓다. |
| [`2a81344`](https://github.com/ssafy-salman/salmanhae/commit/2a81344328900226045f3090474392f15d8c1d5f) | `chore(be): Cloud Run 배포 액션 추가` | Spring뿐 아니라 backend-ai 배포 workflow도 함께 추가했다. `be` scope보다 넓다. |
| PR #106·#109·#113·#115 | 제목 `PR` | 브랜치 동기화 목적은 diff와 merge graph로만 알 수 있고 제목은 내용을 설명하지 않는다. |

## 8. 분석 제한사항

1. 현재 테스트를 재실행하지 않았다. 테스트 실행은 `target`, cache, `__pycache__` 등 저장소 내 산출물을 만들 수 있고 이번 요청은 조사 문서만 생성하도록 제한했기 때문이다.
2. PR 본문의 과거 테스트 결과와 GitHub check는 기록으로 인용했으며 현재 HEAD의 통과를 의미하지 않는다.
3. Supabase 운영 DB의 현재 row 수, migration 적용 상태, 법령 embedding 적재 상태는 확인하지 못했다.
4. Cloud Run 서비스의 실제 URL과 smoke test 결과는 확인하지 못했다. Actions의 배포 성공만 확인했다.
5. Vercel deployment 성공은 확인했지만 사용자 시나리오를 브라우저로 재실행하지 않았다.
6. 사람 review/approval이 없으므로 협업 갈등·합의의 대화 내용은 저장소에서 복원할 수 없다.
7. 모노레포 이전 개별 저장소의 독립 Git history는 현재 저장소에 보존돼 있지 않다.
8. 발표 성적, 심사 피드백, 사용자 수, 사용자 테스트, 성능 부하 테스트는 확인되지 않았다.
9. commit 수는 작업 분할과 merge 방식의 영향을 받으므로 기여 비율로 해석하지 않았다.

추가 확인이 필요한 항목은 [`07-open-questions.md`](07-open-questions.md)에 모았다.
