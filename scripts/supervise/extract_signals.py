#!/usr/bin/env python3
"""
L2 signal extraction from Claude Code session transcripts.

Extracts four structural signal types:
- rollback: user correction followed by assistant reversing its own edit
- interruption: user message inserted mid-tool-sequence
- redo: same file edited 3+ times within 10-minute window
- l1_event: iron law violations from incidents log

Usage:
  python3 extract_signals.py <transcript.jsonl> [--session-id <id>]

Output: JSON array to stdout, each entry:
  {"signal_type": "...", "evidence": "...", "skill": "...", "timestamp": "..."}
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

INCIDENTS_PATH = Path.home() / ".claude" / "state" / "supervise-incidents.jsonl"

STRIP_TAGS = [
    "system-reminder", "task-notification", "command-name", "command-message",
]

SKILL_PHASE_MAP = {
    "dev-discover": "1", "dev-design": "2", "dev-plan": "3",
    "dev-code": "4", "dev-verify": "5", "dev-ship": "6",
    "dev-learn": "7", "dev-flow": "orchestrator",
}


def _parse_transcript(path: str) -> list[dict]:
    entries = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries


def _get_session_id(entries: list[dict]) -> str | None:
    for entry in entries[:5]:
        sid = entry.get("sessionId")
        if sid:
            return sid
    return None
def _find_nearest_skill(entries: list[dict], before_index: int) -> str:
    """Find the most recent Skill tool_use before the given index."""
    for i in range(before_index - 1, -1, -1):
        entry = entries[i]
        if entry.get("type") != "assistant":
            continue
        content = entry.get("message", {}).get("content", [])
        for block in content:
            if block.get("type") == "tool_use" and block.get("name") == "Skill":
                skill_name = block.get("input", {}).get("skill", "")
                if skill_name:
                    return skill_name
    return "unknown"


def _get_tool_uses(entry: dict) -> list[dict]:
    """Extract tool_use blocks from an assistant message."""
    if entry.get("type") != "assistant":
        return []
    content = entry.get("message", {}).get("content", [])
    return [b for b in content if b.get("type") == "tool_use"]


def _get_edit_file(tool_use: dict) -> str | None:
    """Extract file path from Edit/Write tool_use."""
    name = tool_use.get("name", "")
    inp = tool_use.get("input", {})
    if name == "Edit":
        return inp.get("file_path")
    if name == "Write":
        return inp.get("file_path")
    return None


def _get_timestamp(entry: dict) -> str | None:
    """Extract timestamp from entry."""
    return entry.get("timestamp") or entry.get("message", {}).get("timestamp")


def _detect_rollbacks(entries: list[dict]) -> list[dict]:
    """Detect rollback signals: user correction followed by assistant re-editing same file."""
    signals = []
    # Build sequence skipping tool_result entries (normal tool responses, not corrections)
    meaningful = []
    for i, entry in enumerate(entries):
        etype = entry.get("type")
        if etype == "assistant":
            meaningful.append(("assistant", i))
        elif etype == "user":
            content = entry.get("message", {}).get("content", [])
            if isinstance(content, list) and all(
                b.get("type") == "tool_result" for b in content
            ):
                continue
            meaningful.append(("user", i))

    for mi in range(2, len(meaningful)):
        if meaningful[mi][0] != "assistant":
            continue
        if meaningful[mi - 1][0] != "user":
            continue
        if meaningful[mi - 2][0] != "assistant":
            continue

        prev_edits = _get_tool_uses(entries[meaningful[mi - 2][1]])
        curr_edits = _get_tool_uses(entries[meaningful[mi][1]])

        prev_files = {_get_edit_file(t) for t in prev_edits if _get_edit_file(t)}
        curr_files = {_get_edit_file(t) for t in curr_edits if _get_edit_file(t)}

        overlap = prev_files & curr_files
        if overlap:
            signals.append({
                "signal_type": "rollback",
                "evidence": f"files re-edited after user correction: {', '.join(sorted(overlap))}",
                "skill": _find_nearest_skill(entries, meaningful[mi][1]),
                "timestamp": _get_timestamp(entries[meaningful[mi][1]]) or "",
            })
    return signals
def _detect_interruptions(entries: list[dict]) -> list[dict]:
    """Detect interruption signals: user text message inserted mid-tool-sequence."""
    signals = []
    for i in range(1, len(entries) - 1):
        if entries[i].get("type") != "user":
            continue
        # Skip tool_result entries — they are normal tool responses, not interruptions
        content = entries[i].get("message", {}).get("content", [])
        if isinstance(content, list) and all(
            b.get("type") == "tool_result" for b in content
        ):
            continue
        prev = entries[i - 1]
        if prev.get("type") != "assistant":
            continue
        prev_tools = _get_tool_uses(prev)
        if not prev_tools:
            continue
        signals.append({
            "signal_type": "interruption",
            "evidence": f"user message after {len(prev_tools)} tool calls",
            "skill": _find_nearest_skill(entries, i),
            "timestamp": _get_timestamp(entries[i]) or "",
        })
    return signals


def _detect_redos(entries: list[dict]) -> list[dict]:
    """Detect redo signals: same file edited 3+ times within 10-minute window."""
    signals = []
    file_edits: dict[str, list[tuple[int, str]]] = {}  # file -> [(index, timestamp)]

    for i, entry in enumerate(entries):
        if entry.get("type") != "assistant":
            continue
        for tool_use in _get_tool_uses(entry):
            fpath = _get_edit_file(tool_use)
            if fpath:
                ts = _get_timestamp(entry) or ""
                file_edits.setdefault(fpath, []).append((i, ts))

    for fpath, edits in file_edits.items():
        if len(edits) < 3:
            continue
        # Check 10-minute sliding window
        reported = False
        for start in range(len(edits) - 2):
            if reported:
                break
            window = edits[start:]
            # Try timestamp-based window
            try:
                t0 = datetime.fromisoformat(window[0][1])
                # Find the largest window within 600s
                end = 2
                for k in range(2, len(window)):
                    tn = datetime.fromisoformat(window[k][1])
                    if (tn - t0).total_seconds() <= 600:
                        end = k
                    else:
                        break
                if end >= 2:  # At least 3 edits in window
                    tn = datetime.fromisoformat(window[end][1])
                    signals.append({
                        "signal_type": "redo",
                        "evidence": f"{fpath} edited {end + 1} times in {int((tn - t0).total_seconds())}s",
                        "skill": _find_nearest_skill(entries, window[end][0]),
                        "timestamp": window[end][1],
                    })
                    reported = True
            except (ValueError, TypeError):
                # No valid timestamps, count-based fallback: report total edits
                signals.append({
                    "signal_type": "redo",
                    "evidence": f"{fpath} edited {len(edits)} times (no timestamp)",
                    "skill": _find_nearest_skill(entries, edits[-1][0]),
                    "timestamp": "",
                })
                reported = True

    return signals
def _detect_l1_events(session_id: str | None) -> list[dict]:
    """Detect L1 events from incidents log."""
    if not session_id or not INCIDENTS_PATH.exists():
        return []

    signals = []
    with open(INCIDENTS_PATH, "r") as f:
        for line in f:
            try:
                event = json.loads(line)
                if event.get("session") == session_id:
                    signals.append({
                        "signal_type": "l1_event",
                        "evidence": f"{event.get('rule')} / {event.get('action')} / {event.get('detail', '')}",
                        "skill": event.get("phase_inferred", "unknown"),
                        "timestamp": event.get("ts", ""),
                    })
            except json.JSONDecodeError:
                continue

    return signals


def extract_signals(transcript_path: str, session_id: str | None = None) -> list[dict]:
    """Core function: extract all signals from a transcript."""
    entries = _parse_transcript(transcript_path)
    if not entries:
        return []

    if not session_id:
        session_id = _get_session_id(entries)

    signals = []
    signals.extend(_detect_rollbacks(entries))
    signals.extend(_detect_interruptions(entries))
    signals.extend(_detect_redos(entries))
    signals.extend(_detect_l1_events(session_id))

    return signals


def main():
    if len(sys.argv) < 2:
        print("Usage: extract_signals.py <transcript.jsonl> [--session-id <id>]", file=sys.stderr)
        sys.exit(1)

    transcript_path = sys.argv[1]
    session_id = None
    if "--session-id" in sys.argv:
        idx = sys.argv.index("--session-id")
        if idx + 1 < len(sys.argv):
            session_id = sys.argv[idx + 1]

    signals = extract_signals(transcript_path, session_id)
    print(json.dumps(signals, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()



