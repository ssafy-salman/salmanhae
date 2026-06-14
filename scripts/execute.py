#!/usr/bin/env python3
"""
Harness Executor — Phase 순차 실행 + 상태 관리

사용법:
  python3 scripts/execute.py <task-name>
  python3 scripts/execute.py mvp
  python3 scripts/execute.py mvp --from 3   # Phase 3부터 재개
  python3 scripts/execute.py mvp --dry-run  # 실행 없이 Phase 목록만 출력

phases/<task-name>/phase{N}-{slug}.md 파일을 순서대로 실행합니다.
각 Phase 완료 후 phase{N}.status.json에 상태를 기록합니다.
"""

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


def load_phases(task_name: str) -> list[Path]:
    task_dir = PHASES_DIR / task_name
    if not task_dir.exists():
        print(f"❌ phases/{task_name}/ 폴더가 없습니다.", file=sys.stderr)
        sys.exit(1)

    phase_files = sorted(
        task_dir.glob("phase*.md"),
        key=lambda p: int(re.search(r"phase(\d+)", p.name).group(1))
    )
    if not phase_files:
        print(f"❌ phases/{task_name}/ 에 phase*.md 파일이 없습니다.", file=sys.stderr)
        sys.exit(1)
    return phase_files


def status_file(phase_path: Path) -> Path:
    stem = re.search(r"phase(\d+)", phase_path.name).group(0)
    return phase_path.parent / f"{stem}.status.json"


def load_status(phase_path: Path) -> dict:
    sf = status_file(phase_path)
    if sf.exists():
        return json.loads(sf.read_text())
    return {"status": STATUS_PENDING}


def save_status(phase_path: Path, status: str, detail: str = "", issue_number: int = 0):
    sf = status_file(phase_path)
    sf.write_text(json.dumps({
        "status": status,
        "phase": phase_path.name,
        "issue_number": issue_number,
        "timestamp": datetime.now().isoformat(),
        "detail": detail,
    }, ensure_ascii=False, indent=2))


def create_issue(phase_num: str, phase_stem: str, task_name: str) -> int:
    """GitHub 이슈를 생성하고 이슈 번호를 반환한다. 실패 시 0 반환."""
    slug = re.sub(r"^phase\d+-", "", phase_stem)
    title = f"[Phase {phase_num}] {slug.replace('-', ' ')}"
    body = (
        f"## Phase {phase_num} — {slug}\n\n"
        f"Task: `{task_name}`\n\n"
        f"Harness execute.py가 자동 생성한 이슈입니다.\n"
        f"Phase 파일: `phases/{task_name}/phase{phase_num}-{slug}.md`"
    )
    result = subprocess.run(
        [
            "gh", "issue", "create",
            "--title", title,
            "--body", body,
            "--label", "ai-generated",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return 0
    # gh 출력 마지막 줄이 이슈 URL
    url = result.stdout.strip().splitlines()[-1]
    match = re.search(r"/issues/(\d+)$", url)
    return int(match.group(1)) if match else 0


def create_pr(branch_name: str, phase_num: str, phase_stem: str, issue_number: int) -> str:
    """PR을 생성하고 PR URL을 반환한다."""
    slug = re.sub(r"^phase\d+-", "", phase_stem)
    title = f"[Phase {phase_num}] {slug.replace('-', ' ')}"
    closes = f"closes #{issue_number}" if issue_number else ""
    body = (
        f"## 변경 내용\n"
        f"Phase {phase_num} Harness 자동 구현\n\n"
        f"## 연결 이슈\n"
        f"{closes}\n\n"
        f"## 테스트\n"
        f"- [ ] 단위 테스트 통과\n"
        f"- [ ] 로컬 동작 확인\n"
    )
    subprocess.run(["git", "push", "-u", "origin", branch_name], capture_output=True, check=False)
    result = subprocess.run(
        [
            "gh", "pr", "create",
            "--title", title,
            "--body", body,
            "--label", "ai-generated",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip().splitlines()[-1] if result.returncode == 0 else ""


def run_phase(phase_path: Path, task_name: str) -> tuple[str, str, int]:
    """Claude headless 모드로 Phase를 실행하고 (status, detail, elapsed)을 반환."""
    phase_content = phase_path.read_text(encoding="utf-8")
    phase_num = re.search(r"phase(\d+)", phase_path.name).group(1)
    branch_name = f"phase/{phase_num}-{re.sub(r'^phase\d+-', '', phase_path.stem)}"

    # GitHub 이슈 생성
    issue_number = create_issue(phase_num, phase_path.stem, task_name)
    issue_tag = f" (#{issue_number})" if issue_number else ""

    # Phase 브랜치 생성
    subprocess.run(["git", "checkout", "-b", branch_name], capture_output=True, check=False)

    prompt = f"""당신은 살만해 프로젝트의 AI 에이전트입니다.

다음 Phase 지시서를 읽고 정확히 구현하세요.
작업 완료 후 반드시 마지막 줄에 STATUS: completed 또는 STATUS: error 를 출력하세요.

---
{phase_content}
---

구현을 시작하세요.
"""

    start = time.time()
    result = subprocess.run(
        ["claude", "-p", prompt, "--allowedTools", "Edit,Write,Bash,Read"],
        capture_output=True,
        text=True,
        timeout=600,
    )
    elapsed = int(time.time() - start)
    output = result.stdout + result.stderr

    # 상태 파싱
    if "STATUS: completed" in output:
        status = STATUS_COMPLETED
    elif result.returncode != 0 or "STATUS: error" in output:
        status = STATUS_ERROR
    else:
        status = STATUS_COMPLETED

    if status == STATUS_COMPLETED:
        slug = re.sub(r"^phase\d+-", "", phase_path.stem)
        commit_msg = f"feat: phase {phase_num} {slug.replace('-', ' ')}{issue_tag}"
        subprocess.run(["git", "add", "-A"], check=False)
        subprocess.run(["git", "commit", "-m", commit_msg], check=False)

        # PR 생성
        pr_url = create_pr(branch_name, phase_num, phase_path.stem, issue_number)
        if pr_url:
            print(f"\n  PR: {pr_url}", flush=True)

    detail = output[-500:] if len(output) > 500 else output
    save_status(phase_path, status, detail, issue_number)
    return status, detail, elapsed


def print_header(task_name: str, phases: list[Path], pending_count: int):
    print("=" * 50)
    print(f"  Harness Executor")
    print(f"  Task: {task_name} | Phases: {len(phases)} | Pending: {pending_count}")
    print("=" * 50)


def main():
    parser = argparse.ArgumentParser(description="Harness Phase Executor")
    parser.add_argument("task", help="Task 이름 (phases/<task>/ 폴더명)")
    parser.add_argument("--from", dest="from_phase", type=int, default=1,
                        help="시작할 Phase 번호 (기본: 1)")
    parser.add_argument("--dry-run", action="store_true",
                        help="실행 없이 Phase 목록만 출력")
    args = parser.parse_args()

    phases = load_phases(args.task)
    statuses = [load_status(p) for p in phases]
    pending = [p for p, s in zip(phases, statuses) if s["status"] == STATUS_PENDING]

    if args.dry_run:
        print_header(args.task, phases, len(pending))
        for i, (phase, st) in enumerate(zip(phases, statuses), 1):
            icon = {"completed": "✓", "error": "✗", "pending": "○"}.get(st["status"], "?")
            print(f"  {icon} Phase {i}: {phase.stem}")
        return

    print_header(args.task, phases, len(pending))

    success_count = 0
    for phase in phases:
        phase_num = int(re.search(r"phase(\d+)", phase.name).group(1))
        if phase_num < args.from_phase:
            print(f"  ⏭  Phase {phase_num}: {phase.stem} [건너뜀]")
            continue

        st = load_status(phase)
        if st["status"] == STATUS_COMPLETED:
            issue_tag = f" (#{st.get('issue_number')})" if st.get("issue_number") else ""
            print(f"  ✓  Phase {phase_num}: {phase.stem}{issue_tag} [이미 완료]")
            success_count += 1
            continue

        print(f"  ▶  Phase {phase_num}: {phase.stem} ...", end="", flush=True)

        try:
            status, detail, elapsed = run_phase(phase, args.task)
        except subprocess.TimeoutExpired:
            status, detail, elapsed = STATUS_ERROR, "타임아웃 (600s 초과)", 600
            save_status(phase, status, detail)
        except Exception as e:
            status, detail, elapsed = STATUS_ERROR, str(e), 0
            save_status(phase, status, detail)

        if status == STATUS_COMPLETED:
            print(f" [{elapsed}s] ✓")
            success_count += 1
        else:
            print(f" [{elapsed}s] ✗")
            print(f"\n  에러 상세:\n{detail}", file=sys.stderr)
            print(f"\n  Phase {phase_num} 실패. 에러를 수정 후 --from {phase_num} 옵션으로 재실행하세요.")
            sys.exit(1)

    print("=" * 50)
    if success_count == len(phases):
        print(f"  Task '{args.task}' completed!")
    else:
        print(f"  Task '{args.task}' 일부 완료 ({success_count}/{len(phases)})")
    print("=" * 50)


if __name__ == "__main__":
    main()
