#!/usr/bin/env python3
"""Codex hook bridge for Salmanhae project checks."""

from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Any


DANGEROUS_PATTERNS = [
    "rm -rf",
    "git push --force",
    "git push -f",
    "git reset --hard",
    "git clean -f",
    "git clean -fd",
    "DROP TABLE",
    "DROP DATABASE",
    "TRUNCATE",
    "rm -r /",
    "chmod -R 777",
    "> /dev/sda",
    "mkfs",
    "dd if=",
    "fork bomb",
    ":(){ :|:& };:",
]


def read_payload() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}
    return payload if isinstance(payload, dict) else {"value": payload}


def nested(data: dict[str, Any], *paths: str) -> str:
    for path in paths:
        cur: Any = data
        for part in path.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                cur = None
                break
        if cur is not None:
            return str(cur)
    return ""


def find_command(payload: dict[str, Any]) -> str:
    return (
        os.getenv("CODEX_TOOL_INPUT_COMMAND")
        or os.getenv("CLAUDE_TOOL_INPUT_COMMAND")
        or nested(
            payload,
            "command",
            "input.command",
            "tool_input.command",
            "toolInput.command",
            "arguments.command",
            "params.command",
        )
    )


def find_file_path(payload: dict[str, Any]) -> str:
    return (
        os.getenv("CODEX_TOOL_INPUT_FILE_PATH")
        or os.getenv("CLAUDE_TOOL_INPUT_FILE_PATH")
        or nested(
            payload,
            "file_path",
            "filePath",
            "input.file_path",
            "input.filePath",
            "tool_input.file_path",
            "toolInput.filePath",
            "arguments.file_path",
            "arguments.filePath",
            "params.file_path",
            "params.filePath",
        )
    )


def find_exit_code(payload: dict[str, Any]) -> int:
    raw = (
        os.getenv("CODEX_TOOL_RESULT_EXIT_CODE")
        or os.getenv("CLAUDE_TOOL_RESULT_EXIT_CODE")
        or nested(payload, "exit_code", "exitCode", "result.exit_code", "result.exitCode")
        or "0"
    )
    try:
        return int(raw)
    except ValueError:
        return 0


def find_output(payload: dict[str, Any]) -> str:
    return (
        os.getenv("CODEX_TOOL_RESULT_OUTPUT")
        or os.getenv("CLAUDE_TOOL_RESULT_OUTPUT")
        or nested(payload, "output", "result.output", "result.stdout", "stdout", "stderr")
    )


def pre_bash(payload: dict[str, Any]) -> int:
    command = find_command(payload)
    lowered = command.lower()
    for pattern in DANGEROUS_PATTERNS:
        if pattern.lower() in lowered:
            print("[Dangerous Command Guard] blocked dangerous command.", file=sys.stderr)
            print(f"command: {command}", file=sys.stderr)
            print(f"pattern: {pattern}", file=sys.stderr)
            return 2
    return 0


def is_implementation_file(path: str) -> bool:
    normalized = path.replace("\\", "/")
    lower = normalized.lower()
    if any(part in lower for part in ("test", "spec")):
        return False
    return (
        ("/service/" in normalized and normalized.endswith(".java"))
        or ("/graph/" in normalized and normalized.endswith(".py"))
        or ("/rag/" in normalized and normalized.endswith(".py"))
        or ("/composables/" in normalized and normalized.endswith(".ts"))
    )


def expected_test_patterns(path: str) -> list[str]:
    p = Path(path)
    stem = p.stem
    if p.suffix == ".java":
        return [f"{stem}Test.java"]
    if p.suffix == ".py":
        return [f"test_{stem}.py"]
    if p.suffix == ".ts":
        return [f"{stem}.test.ts"]
    return []


def post_edit(payload: dict[str, Any]) -> int:
    file_path = find_file_path(payload)
    if not file_path or not is_implementation_file(file_path):
        return 0

    found = False
    root = Path.cwd()
    for pattern in expected_test_patterns(file_path):
        if any(root.rglob(pattern)):
            found = True
            break

    if not found:
        print(
            f"[TDD Guard] No matching test file found for implementation change: {file_path}",
            file=sys.stderr,
        )
        print("Add or update tests before committing this feature work.", file=sys.stderr)
    return 0


def post_bash(payload: dict[str, Any]) -> int:
    exit_code = find_exit_code(payload)
    if exit_code == 0:
        return 0

    output = find_output(payload)
    digest = hashlib.md5(output[:200].encode("utf-8", errors="ignore")).hexdigest()
    state_dir = Path(tempfile.gettempdir()) / "salmanhae-codex-circuit-breaker"
    state_dir.mkdir(parents=True, exist_ok=True)
    state_file = state_dir / digest

    now = int(time.time())
    window = 60
    threshold = 5
    timestamps: list[int] = []
    if state_file.exists():
        for line in state_file.read_text(encoding="utf-8").splitlines():
            try:
                ts = int(line)
            except ValueError:
                continue
            if now - ts <= window:
                timestamps.append(ts)
    timestamps.append(now)
    state_file.write_text("\n".join(str(ts) for ts in timestamps), encoding="utf-8")

    if len(timestamps) >= threshold:
        print(
            f"[Circuit Breaker] Same command error repeated {len(timestamps)} times in {window}s.",
            file=sys.stderr,
        )
        print("Pause and inspect the root cause before retrying.", file=sys.stderr)
    return 0


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: codex_hook_bridge.py pre-bash|post-edit|post-bash", file=sys.stderr)
        return 2
    payload = read_payload()
    mode = sys.argv[1]
    if mode == "pre-bash":
        return pre_bash(payload)
    if mode == "post-edit":
        return post_edit(payload)
    if mode == "post-bash":
        return post_bash(payload)
    print(f"unknown mode: {mode}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
