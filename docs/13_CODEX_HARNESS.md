# 13. CODEX_HARNESS

## 목적

기존 Claude Code 하네스는 그대로 유지하면서, 같은 Phase 기반 작업 방식을 Codex에서도 사용할 수 있게 합니다.

| 용도 | Claude | Codex |
| --- | --- | --- |
| 프로젝트 지침 | `CLAUDE.md` | `AGENTS.md` |
| 하네스 명령 | `.claude/commands/harness.md` | `.agents/skills/salmanhae-harness/SKILL.md` |
| 리뷰 명령 | `.claude/commands/review.md` | `salmanhae-harness` skill의 review 절차 |
| Phase 실행기 | `scripts/execute.py` | `scripts/execute_codex.py` |
| 도구 훅 | `.claude/settings.json` | `.codex/hooks.json` |

## Codex에서 Phase 계획하기

Codex에게 다음처럼 요청합니다.

```text
$salmanhae-harness 를 사용해서 F-1 더미 매물 API + 지도 연동을 Phase로 쪼개줘.
```

Codex는 문서를 읽고 3~7개 Phase 계획을 제안합니다. 승인 후 `phases/{task-name}/phase{N}-{slug}.md` 파일을 생성합니다.

## Codex에서 Phase 실행하기

먼저 dry-run으로 Phase 목록과 상태를 확인합니다.

```bash
python scripts/execute_codex.py {task-name} --dry-run
```

GitHub 이슈와 PR을 만들지 않고 로컬에서 실행 테스트를 하려면:

```bash
python scripts/execute_codex.py {task-name} --no-github
```

`--no-github` 모드는 이슈 번호 없는 커밋을 만들지 않기 위해 변경사항을 커밋하지 않고 로컬에 남깁니다.

GitHub 이슈, Phase 브랜치, 커밋, PR까지 생성하려면:

```bash
python scripts/execute_codex.py {task-name}
```

중간 실패 후 특정 Phase부터 재개하려면:

```bash
python scripts/execute_codex.py {task-name} --from 3
```

## 주의사항

- `scripts/execute.py`는 Claude용으로 그대로 둡니다.
- `scripts/execute_codex.py`는 `codex exec`를 호출하므로 Codex CLI 로그인이 필요합니다.
- GitHub 이슈와 PR 생성을 사용하려면 `gh` CLI 로그인이 필요합니다.
- 큰 자동 실행 전에는 항상 `--dry-run`을 먼저 사용합니다.
- 수동 개발은 기존 `feature/*`, `fix/*`, `docs/*` 브랜치 흐름을 계속 사용합니다.

## Codex Hooks

`.codex/hooks.json`은 Codex 도구 실행 전후에 다음 검사를 수행합니다.

- 위험 명령 차단
- Service, LangGraph, RAG 등 구현 파일 변경 시 테스트 파일 존재 여부 경고
- 같은 명령 오류가 짧은 시간에 반복되면 회로 차단 경고

Claude용 shell hook은 `scripts/hooks/*.sh`에 그대로 남아 있습니다.
