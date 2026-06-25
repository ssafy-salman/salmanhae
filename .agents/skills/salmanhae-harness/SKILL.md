---
name: salmanhae-harness
description: Plan, review, and run Salmanhae phase-based development work in Codex. Use when the user asks for the harness workflow, phase planning, executing phases with Codex, or reviewing changes against Salmanhae project rules.
---

# Salmanhae Harness

## Overview

This skill is the Codex counterpart to the existing Claude harness. Keep the Claude files intact; use this skill to plan phases, run phase execution through `scripts/execute_codex.py`, and review work against the repository rules.

## Required Context

Before planning or implementing, read the smallest relevant set:

- Always read `AGENTS.md`, `docs/01_PRD.md`, `docs/02_ARCHITECTURE.md`, `docs/03_ADR.md`, `docs/05_GIT_GUIDE.md`, and `docs/11_ROADMAP.md`.
- For UI work, also read `docs/04_UI_GUIDE.md`.
- For API or response changes, also read `docs/08_API_SPEC.md`.
- For model or schema changes, also read `docs/07_DOMAIN_MODEL.md`.
- For auth/security changes, also read `docs/10_SECURITY_POLICY.md`.
- For batch or external API changes, also read `docs/06_EXTERNAL_APIS.md` and `docs/09_BATCH_INGESTION.md`.

## Plan Phases

When the user asks to use the harness or to break work into phases:

1. Identify the roadmap stage and feature ID (`F-1` through `F-8`).
2. Exclude non-MVP work unless the user explicitly asks for a later phase.
3. Split the task into 3-7 independently reviewable phases.
4. Show the phase list and ask for approval before creating files.
5. After approval, create `phases/{task-name}/phase{N}-{slug}.md` files.

Each phase file must use:

```markdown
# Phase {N}: {title}

## Goal
{1-2 sentence goal}

## Files
- `{path}` - {expected change}

## Done When
- [ ] {testable completion condition}

## Architecture Rules
- {relevant AGENTS.md or docs rule}

## Implementation Instructions
{specific instructions for Codex}
```

## Execute Phases

Use the Codex executor instead of the Claude executor:

```bash
python scripts/execute_codex.py {task-name} --dry-run
python scripts/execute_codex.py {task-name}
python scripts/execute_codex.py {task-name} --from 3
```

Use `--dry-run` first. Use `--no-github` when testing locally without creating GitHub issues or PRs.

The legacy executor remains available for teammates:

```bash
python scripts/execute.py {task-name}
```

## Review Changes

When the user asks for harness review, review `git diff HEAD` using:

- architecture boundaries from `docs/02_ARCHITECTURE.md`
- ADR decisions from `docs/03_ADR.md`
- TDD and commit rules from `AGENTS.md` and `docs/05_GIT_GUIDE.md`
- API and domain document sync requirements
- UI constraints from `docs/04_UI_GUIDE.md` when frontend files changed

Lead with blocking findings first. Mark missing tests or missing doc updates clearly.
