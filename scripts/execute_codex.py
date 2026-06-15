#!/usr/bin/env python3
"""Codex Harness Executor - phase execution and status management.

This script is the Codex counterpart to scripts/execute.py. It intentionally
keeps the Claude executor unchanged for teammates who use Claude Code.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


PHASES_DIR = Path("phases")
STATUS_COMPLETED = "completed"
STATUS_ERROR = "error"
STATUS_PENDING = "pending"


def run_command(args: list[str], timeout: int | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, capture_output=True, text=True, check=False, timeout=timeout)


def load_phases(task_name: str) -> list[Path]:
    task_dir = PHASES_DIR / task_name
    if not task_dir.exists():
        print(f"ERROR: phases/{task_name}/ does not exist.", file=sys.stderr)
        sys.exit(1)

    phase_files = sorted(
        task_dir.glob("phase*.md"),
        key=lambda p: int(re.search(r"phase(\d+)", p.name).group(1)),
    )
    if not phase_files:
        print(f"ERROR: phases/{task_name}/ has no phase*.md files.", file=sys.stderr)
        sys.exit(1)
    return phase_files


def phase_num(phase_path: Path) -> str:
    match = re.search(r"phase(\d+)", phase_path.name)
    if not match:
        raise ValueError(f"Invalid phase filename: {phase_path}")
    return match.group(1)


def phase_slug(phase_path: Path) -> str:
    return re.sub(r"^phase\d+-", "", phase_path.stem)


def status_file(phase_path: Path) -> Path:
    return phase_path.parent / f"phase{phase_num(phase_path)}.status.json"


def load_status(phase_path: Path) -> dict:
    sf = status_file(phase_path)
    if sf.exists():
        return json.loads(sf.read_text(encoding="utf-8"))
    return {"status": STATUS_PENDING}


def save_status(phase_path: Path, status: str, detail: str = "", issue_number: int = 0) -> None:
    status_file(phase_path).write_text(
        json.dumps(
            {
                "status": status,
                "phase": phase_path.name,
                "issue_number": issue_number,
                "timestamp": datetime.now().isoformat(),
                "detail": detail,
                "runner": "codex",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def create_issue(phase_path: Path, task_name: str, enabled: bool) -> int:
    if not enabled:
        return 0

    num = phase_num(phase_path)
    slug = phase_slug(phase_path)
    title = f"[Phase {num}] {slug.replace('-', ' ')}"
    body = (
        f"## Phase {num} - {slug}\n\n"
        f"Task: `{task_name}`\n\n"
        f"Codex harness executor created this issue.\n"
        f"Phase file: `phases/{task_name}/phase{num}-{slug}.md`"
    )
    result = run_command(
        [
            "gh",
            "issue",
            "create",
            "--title",
            title,
            "--body",
            body,
            "--label",
            "ai-generated",
        ]
    )
    if result.returncode != 0:
        print("[WARN] GitHub issue creation failed; continuing without issue number.", file=sys.stderr)
        return 0
    url = result.stdout.strip().splitlines()[-1]
    match = re.search(r"/issues/(\d+)$", url)
    return int(match.group(1)) if match else 0


def create_pr(branch_name: str, phase_path: Path, issue_number: int, enabled: bool) -> str:
    if not enabled:
        return ""

    num = phase_num(phase_path)
    slug = phase_slug(phase_path)
    closes = f"closes #{issue_number}" if issue_number else ""
    body = (
        "## 변경 내용\n"
        f"Phase {num} Codex harness 자동 구현\n\n"
        "## 연결 이슈\n"
        f"{closes}\n\n"
        "## 테스트\n"
        "- [ ] 단위 테스트 통과\n"
        "- [ ] 로컬 동작 확인\n"
    )
    push_result = run_command(["git", "push", "-u", "origin", branch_name])
    if push_result.returncode != 0:
        raise RuntimeError(f"git push failed: {push_result.stderr.strip()}")
    result = run_command(
        [
            "gh",
            "pr",
            "create",
            "--title",
            f"[Phase {num}] {slug.replace('-', ' ')} [codex]",
            "--body",
            body,
            "--label",
            "ai-generated",
        ]
    )
    if result.returncode != 0:
        raise RuntimeError(f"gh pr create failed: {result.stderr.strip()}")
    return result.stdout.strip().splitlines()[-1] if result.returncode == 0 else ""


def build_prompt(phase_path: Path) -> str:
    phase_content = phase_path.read_text(encoding="utf-8")
    return f"""You are Codex working on the Salmanhae project.

Read and follow AGENTS.md plus the relevant docs before editing:
- docs/01_PRD.md
- docs/02_ARCHITECTURE.md
- docs/03_ADR.md
- docs/05_GIT_GUIDE.md
- docs/11_ROADMAP.md

Implement the following phase exactly. Use TDD where applicable.
Keep business logic in Service classes, keep LangGraph/LLM code only in backend-ai,
and never hardcode API keys or secrets.

When complete, make the final line exactly one of:
STATUS: completed
STATUS: error

---
{phase_content}
---
"""


def run_codex(prompt: str, codex_bin: str, timeout: int, extra_args: list[str]) -> subprocess.CompletedProcess[str]:
    return run_command([codex_bin, "exec", *extra_args, prompt], timeout=timeout)


def ensure_branch(branch_name: str) -> None:
    check_result = run_command(["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch_name}"])
    if check_result.returncode == 0:
        # Branch exists, just checkout
        result = run_command(["git", "checkout", branch_name])
    else:
        # Branch doesn't exist, create it
        result = run_command(["git", "checkout", "-b", branch_name])
    if result.returncode != 0:
        print(result.stderr.strip(), file=sys.stderr)
        sys.exit(result.returncode)


def commit_phase(phase_path: Path, issue_number: int) -> None:
    num = phase_num(phase_path)
    slug = phase_slug(phase_path).replace("-", " ")
    issue_tag = f" (#{issue_number})" if issue_number else ""
    run_command(["git", "add", "-A"])
    result = run_command(["git", "commit", "-m", f"feat(harness): {num}단계 {slug} 구현{issue_tag}"])
    if result.returncode != 0:
        print("[WARN] Commit failed. Check git status manually.", file=sys.stderr)
        if result.stderr.strip():
            print(result.stderr.strip(), file=sys.stderr)


def run_phase(phase_path: Path, task_name: str, args: argparse.Namespace) -> tuple[str, str, int]:
    num = phase_num(phase_path)
    slug = phase_slug(phase_path)
    branch_name = f"phase/{num}-{slug}"

    issue_number = create_issue(phase_path, task_name, enabled=not args.no_github)
    ensure_branch(branch_name)

    start = time.time()
    result = run_codex(
        build_prompt(phase_path),
        codex_bin=args.codex_bin,
        timeout=args.timeout,
        extra_args=args.codex_arg or [],
    )
    elapsed = int(time.time() - start)
    output = result.stdout + result.stderr

    if result.returncode != 0 or "STATUS: error" in output:
        status = STATUS_ERROR
    elif "STATUS: completed" in output:
        status = STATUS_COMPLETED
    else:
        status = STATUS_COMPLETED

    if status == STATUS_COMPLETED and not args.no_github:
        commit_phase(phase_path, issue_number)
        pr_url = create_pr(
            branch_name,
            phase_path,
            issue_number,
            enabled=not args.no_github and not args.no_pr,
        )
        if pr_url:
            print(f"\n  PR: {pr_url}", flush=True)
    elif status == STATUS_COMPLETED:
        print("\n  --no-github enabled: leaving changes uncommitted for local review.", flush=True)

    detail = output[-1000:] if len(output) > 1000 else output
    save_status(phase_path, status, detail, issue_number)
    return status, detail, elapsed


def print_header(task_name: str, phases: list[Path], pending_count: int) -> None:
    print("=" * 50)
    print("  Codex Harness Executor")
    print(f"  Task: {task_name} | Phases: {len(phases)} | Pending: {pending_count}")
    print("=" * 50)


def main() -> None:
    parser = argparse.ArgumentParser(description="Codex Harness Phase Executor")
    parser.add_argument("task", help="Task name under phases/<task>/")
    parser.add_argument("--from", dest="from_phase", type=int, default=1, help="Phase number to start from")
    parser.add_argument("--dry-run", action="store_true", help="Print phase status without execution")
    parser.add_argument("--no-github", action="store_true", help="Skip GitHub issue, push, and PR creation")
    parser.add_argument("--no-pr", action="store_true", help="Create issues but skip PR creation")
    parser.add_argument("--codex-bin", default="codex", help="Codex executable name or path")
    parser.add_argument("--timeout", type=int, default=900, help="Per-phase Codex timeout in seconds")
    parser.add_argument(
        "--codex-arg",
        action="append",
        help="Extra argument passed to `codex exec`; repeat for multiple args",
    )
    args = parser.parse_args()

    phases = load_phases(args.task)
    statuses = [load_status(p) for p in phases]
    pending = [p for p, s in zip(phases, statuses) if s["status"] == STATUS_PENDING]

    if args.dry_run:
        print_header(args.task, phases, len(pending))
        for index, (phase, st) in enumerate(zip(phases, statuses), 1):
            icon = {"completed": "OK", "error": "ERR", "pending": "TODO"}.get(st["status"], "?")
            print(f"  {icon} Phase {index}: {phase.stem}")
        return

    print_header(args.task, phases, len(pending))
    success_count = 0
    for phase in phases:
        num = int(phase_num(phase))
        if num < args.from_phase:
            print(f"  SKIP Phase {num}: {phase.stem}")
            continue

        st = load_status(phase)
        if st["status"] == STATUS_COMPLETED:
            issue_tag = f" (#{st.get('issue_number')})" if st.get("issue_number") else ""
            print(f"  OK Phase {num}: {phase.stem}{issue_tag} [already completed]")
            success_count += 1
            continue

        print(f"  RUN Phase {num}: {phase.stem} ...", end="", flush=True)
        try:
            status, detail, elapsed = run_phase(phase, args.task, args)
        except subprocess.TimeoutExpired:
            status, detail, elapsed = STATUS_ERROR, f"Timeout after {args.timeout}s", args.timeout
            save_status(phase, status, detail)
        except Exception as exc:
            status, detail, elapsed = STATUS_ERROR, str(exc), 0
            save_status(phase, status, detail)

        if status == STATUS_COMPLETED:
            print(f" [{elapsed}s] OK")
            success_count += 1
        else:
            print(f" [{elapsed}s] ERR")
            print(f"\n  Error detail:\n{detail}", file=sys.stderr)
            print(f"\n  Phase {num} failed. Fix the error and rerun with --from {num}.")
            sys.exit(1)

    print("=" * 50)
    if success_count == len(phases):
        print(f"  Task '{args.task}' completed.")
    else:
        print(f"  Task '{args.task}' partially completed ({success_count}/{len(phases)}).")
    print("=" * 50)


if __name__ == "__main__":
    main()
