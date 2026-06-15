# Salmanhae Phase Template

Use this template for `phases/{task-name}/phase{N}-{slug}.md`.

```markdown
# Phase {N}: {title}

## Goal
{1-2 sentence goal}

## Files
- `{path}` - {expected change}

## Done When
- [ ] {testable completion condition}
- [ ] Relevant tests pass

## Architecture Rules
- Business logic belongs in Service classes.
- Frontend calls Spring Boot REST APIs only.
- LangGraph and LLM calls live only in `backend-ai`.
- API keys and secrets come from environment variables.
- Update docs when API responses or domain models change.

## Implementation Instructions
{specific implementation instructions for Codex}

At the end of execution, report `STATUS: completed` or `STATUS: error`.
```
