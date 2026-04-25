#!/usr/bin/env python3
"""
L1 real-time iron law guard for dev:* workflow.

Claude Code PreToolUse/PostToolUse hook that enforces:
- Iron Law 6: worktree-before-work (DENY on main/master outside .worktrees/)
- Iron Law 7: commit-by-user-trigger (DENY git commit/push/pr outside dev-ship)
- Iron Law 4: evidence-before-assertion (WARN on claims without test evidence)

Registered in .claude/settings.json as:
  PreToolUse  matcher: "Bash|Write|Edit"
  PostToolUse matcher: "Bash"

stdin: JSON {"tool_name": "...", "tool_input": {...}}
stdout: JSON {} (allow) | {"permissionDecision":"deny","message":"..."} | {"permissionDecision":"ask","message":"..."}

On ANY error: outputs {} (silent allow) — never blocks user workflow.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SKILL_PHASE_MAP = {
    "dev-discover": "1",
    "dev-design": "2",
    "dev-plan": "3",
    "dev-code": "4",
    "dev-verify": "5",
    "dev-ship": "6",
    "dev-learn": "7",
    "dev-flow": "orchestrator",
}

COMMIT_PATTERNS = [
    "git commit", "git push", "gh pr create", "gh pr merge",
]

ASSERTION_KEYWORDS_ZH = ["完成", "通过", "已修复", "已解决"]
ASSERTION_KEYWORDS_EN = ["works", "passing", "all green", "fixed", "resolved", "done"]

TEST_COMMANDS = ["pytest", "npm test", "cargo test", "go test", "bundle exec", "vitest", "jest", "mocha", "make test"]

INCIDENTS_PATH = Path.home() / ".claude" / "state" / "supervise-incidents.jsonl"


def _allow():
    print("{}")
    sys.exit(0)


def _deny(message: str):
    print(json.dumps({"permissionDecision": "deny", "message": message}))
    sys.exit(0)


def _warn(message: str):
    print(json.dumps({"permissionDecision": "ask", "message": message}))
    sys.exit(0)


def _log_incident(rule: str, tool: str, detail: str, action: str, phase: str):
    INCIDENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "session": os.environ.get("CLAUDE_SESSION_ID", "unknown"),
        "rule": rule,
        "tool": tool,
        "detail": detail,
        "action": action,
        "phase_inferred": phase,
    }
    with open(INCIDENTS_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")


def _get_current_branch() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception:
        return None


def _is_in_worktree() -> bool:
    cwd = os.getcwd()
    return "/.worktrees/" in cwd or "\\.worktrees\\" in cwd


def _infer_current_phase() -> str:
    """Infer current phase from transcript by finding most recent Skill tool_use."""
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    if not project_dir:
        return "unknown"

    try:
        conversations_dir = Path(project_dir) / "conversations"
        if not conversations_dir.exists():
            return "unknown"

        # Find most recent .jsonl file
        transcripts = sorted(conversations_dir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not transcripts:
            return "unknown"

        # Read last 100 lines (reverse scan for recent Skill call)
        with open(transcripts[0], "r") as f:
            lines = f.readlines()

        for line in reversed(lines[-100:]):
            try:
                entry = json.loads(line)
                if entry.get("type") == "assistant":
                    content = entry.get("message", {}).get("content", [])
                    for block in content:
                        if block.get("type") == "tool_use" and block.get("name") == "Skill":
                            skill_name = block.get("input", {}).get("skill", "")
                            # Map dev-* to phase, or find nearest dev-* ancestor
                            if skill_name in SKILL_PHASE_MAP:
                                return SKILL_PHASE_MAP[skill_name]
            except (json.JSONDecodeError, KeyError):
                continue

        return "unknown"
    except Exception:
        return "unknown"


def _check_iron_law_6(tool_name: str) -> None:
    """Iron Law 6: worktree-before-work."""
    if tool_name not in ["Write", "Edit"]:
        return

    branch = _get_current_branch()
    if branch in ["main", "master"] and not _is_in_worktree():
        _log_incident("worktree", tool_name, f"branch={branch}", "deny", "n/a")
        _deny("铁律 6 违规：在 main/master 分支且不在 .worktrees/ 中。请通过 `compound-engineering:git-worktree` 创建任务级 worktree。")


def _check_iron_law_7(command: str, phase: str) -> None:
    """Iron Law 7: commit-by-user-trigger."""
    if phase == "6" or phase == "orchestrator":  # dev-ship or dev-flow exemption
        return
    if phase == "unknown":  # Cannot determine phase — allow to avoid false blocks
        return

    for pattern in COMMIT_PATTERNS:
        if pattern in command:
            _log_incident("commit-trigger", "Bash", f"cmd={command[:50]}", "deny", phase)
            _deny(f"铁律 7 违规：在 Phase {phase} 中执行 git commit/push/pr。请显式触发 `/dev:ship` 或在消息中明示授权。")


def _check_iron_law_4_posttooluse() -> None:
    """Iron Law 4: evidence-before-assertion (PostToolUse only)."""
    # This is a simplified check - full implementation would scan recent assistant text
    # and check for test commands in last N tool calls. For now, log a warning placeholder.
    # Real implementation deferred to when we have full transcript access in PostToolUse context.
    pass


def main():
    try:
        # Read stdin
        input_data = json.loads(sys.stdin.read())
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})

        # Infer phase (may return "unknown" if transcript unavailable)
        phase = _infer_current_phase()

        # PreToolUse checks
        if tool_name in ["Bash", "Write", "Edit"]:
            # Iron Law 6: worktree check
            _check_iron_law_6(tool_name)

            # Iron Law 7: commit trigger check (Bash only)
            if tool_name == "Bash":
                command = tool_input.get("command", "")
                _check_iron_law_7(command, phase)

        # PostToolUse checks (tool_name will be same as PreToolUse)
        # Iron Law 4 check is complex and deferred - would need recent assistant text + tool history
        # For now, we skip it in this initial implementation

        # All checks passed
        _allow()

    except Exception:
        # On ANY error: silent allow
        _allow()


if __name__ == "__main__":
    main()


