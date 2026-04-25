#!/usr/bin/env python3
"""
L3 historical session scanner for dev-supervise.

Enumerates Claude Code session transcripts, filters by repo scope,
runs L2 signal extraction on each, and aggregates results into a
ranked report with structured improvement suggestions.

Usage:
  python3 scan_history.py [--since 14d] [--scope project|global] [--repo-path /path/to/repo]

Output: Markdown report to stdout.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from extract_signals import extract_signals

CLAUDE_PROJECTS_DIR = Path.home() / ".claude" / "projects"
GLOBAL_OUTPUT_DIR = Path.home() / ".claude" / "skill-feedback"


def _parse_since(since_str: str) -> timedelta:
    match = re.match(r"(\d+)([dhm])", since_str)
    if not match:
        return timedelta(days=14)
    val, unit = int(match.group(1)), match.group(2)
    if unit == "d":
        return timedelta(days=val)
    if unit == "h":
        return timedelta(hours=val)
    if unit == "m":
        return timedelta(minutes=val)
    return timedelta(days=14)


def _get_session_cwd(transcript_path: str) -> str | None:
    """Read first few lines to extract cwd."""
    try:
        with open(transcript_path, "r") as f:
            for _ in range(10):
                line = f.readline()
                if not line:
                    break
                try:
                    entry = json.loads(line)
                    cwd = entry.get("cwd")
                    if cwd:
                        return cwd
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass
    return None
def _get_session_timestamp(transcript_path: str) -> datetime | None:
    """Get session start time from first entry (always returns UTC-aware)."""
    try:
        with open(transcript_path, "r") as f:
            line = f.readline()
            if line:
                entry = json.loads(line)
                ts = entry.get("timestamp")
                if ts:
                    dt = datetime.fromisoformat(ts)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    return dt
    except Exception:
        pass
    try:
        return datetime.fromtimestamp(os.path.getmtime(transcript_path), tz=timezone.utc)
    except Exception:
        return None


def _enumerate_sessions(scope: str, repo_path: str | None, since: timedelta) -> list[str]:
    """Find all relevant transcript files."""
    cutoff = datetime.now(timezone.utc) - since
    sessions = []

    if not CLAUDE_PROJECTS_DIR.exists():
        return sessions

    for project_dir in CLAUDE_PROJECTS_DIR.iterdir():
        if not project_dir.is_dir():
            continue
        conversations_dir = project_dir / "conversations"
        if not conversations_dir.exists():
            conversations_dir = project_dir
        for jsonl in conversations_dir.glob("*.jsonl"):
            ts = _get_session_timestamp(str(jsonl))
            if ts and ts < cutoff:
                continue

            if scope == "project" and repo_path:
                cwd = _get_session_cwd(str(jsonl))
                if cwd and not cwd.startswith(repo_path):
                    continue

            sessions.append(str(jsonl))

    return sessions


def _aggregate_signals(all_signals: list[dict]) -> dict[tuple[str, str], int]:
    """Aggregate signals by (skill, signal_type)."""
    counts: dict[tuple[str, str], int] = {}
    for sig in all_signals:
        key = (sig.get("skill", "unknown"), sig.get("signal_type", "unknown"))
        counts[key] = counts.get(key, 0) + 1
    return counts
def _generate_report(counts: dict[tuple[str, str], int], all_signals: list[dict],
                     since_str: str, scope: str, sessions_scanned: int) -> str:
    """Generate Markdown report."""
    today = datetime.now().strftime("%Y-%m-%d")
    lines = [
        f"# Skill Supervise Report - {today}",
        "",
        f"扫描范围: {scope} / 时间窗口: {since_str} / 扫描 session 数: {sessions_scanned}",
        "",
    ]

    if not counts:
        lines.append("未发现任何信号。")
        return "\n".join(lines)

    # Leaderboard
    lines.append("## 排行榜")
    lines.append("")
    lines.append("| Skill | 信号类型 | 次数 |")
    lines.append("|---|---|---|")

    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    for (skill, sig_type), count in sorted_counts:
        lines.append(f"| {skill} | {sig_type} | {count} |")

    lines.append("")

    # Structured suggestions for top issues
    lines.append("## 结构化改进建议")
    lines.append("")

    for (skill, sig_type), count in sorted_counts[:5]:
        lines.append(f"### {skill} / {sig_type}")
        # Collect evidence references
        evidence = [s for s in all_signals
                    if s.get("skill") == skill and s.get("signal_type") == sig_type]
        lines.append(f"- 证据: {count} 次出现")
        for e in evidence[:3]:
            lines.append(f"  - {e.get('evidence', 'n/a')}")
        if sig_type == "redo":
            lines.append("- 建议方向: 检查 SKILL.md 中下游触发条件描述，可能与实际可用性不一致")
        elif sig_type == "rollback":
            lines.append("- 建议方向: 检查 skill 输出质量，用户频繁纠正可能表明指令不够精确")
        elif sig_type == "interruption":
            lines.append("- 建议方向: 检查 skill 是否在不必要的地方执行过多工具调用")
        elif sig_type == "l1_event":
            lines.append("- 建议方向: 检查 iron law 违规模式，可能需要在 skill 中加强前置检查")
        lines.append("- 待人工: 阅读证据 → 改 SKILL.md → 走常规 review")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="L3 historical session scanner")
    parser.add_argument("--since", default="14d", help="Time window (e.g., 14d, 7d, 24h)")
    parser.add_argument("--scope", choices=["project", "global"], default="project")
    parser.add_argument("--repo-path", default=None, help="Repo root path for project scope")
    args = parser.parse_args()

    repo_path = args.repo_path
    if not repo_path and args.scope == "project":
        try:
            import subprocess
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True, text=True, timeout=5,
            )
            repo_path = result.stdout.strip() if result.returncode == 0 else None
        except Exception:
            pass

    since = _parse_since(args.since)
    sessions = _enumerate_sessions(args.scope, repo_path, since)

    all_signals = []
    for session_path in sessions:
        try:
            signals = extract_signals(session_path)
            all_signals.extend(signals)
        except Exception:
            continue

    counts = _aggregate_signals(all_signals)
    report = _generate_report(counts, all_signals, args.since, args.scope, len(sessions))
    print(report)


if __name__ == "__main__":
    main()


