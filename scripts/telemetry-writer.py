#!/usr/bin/env python3
"""LogosFortuna Telemetry Writer
UDIV faz olaylarini, agent basarisini ve dongu metriklerini JSONL'e yazar.

Kullanim:
    python3 telemetry-writer.py <event> --data '{"phase":"FAZ_1","duration_ms":4500}'

Tum veri lokal kalir, hicbir yere gonderilmez. Cikti dosyasi:
    .specify/telemetry/udiv-runs-YYYY-MM-DD.jsonl
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

VALID_EVENTS = {
    "phase_start",
    "phase_complete",
    "phase_rollback",
    "increment_attempt",
    "increment_success",
    "increment_failure",
    "agent_invoked",
    "agent_completed",
    "tool_call",
    "user_approval",
    "user_rejection",
    "install_proposal",
    "install_executed",
    "mcp_need_detected",
    "validation_score",
    "session_summary",
}


def get_telemetry_dir() -> Path:
    """Return per-project telemetry directory, creating if needed."""
    cwd = Path.cwd()
    telemetry_dir = cwd / ".specify" / "telemetry"
    telemetry_dir.mkdir(parents=True, exist_ok=True)
    return telemetry_dir


def get_daily_log_path() -> Path:
    """Return daily-rotated JSONL file path."""
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return get_telemetry_dir() / f"udiv-runs-{date_str}.jsonl"


def write_event(event: str, data: dict | None = None) -> None:
    """Append a single event line to today's telemetry log."""
    if event not in VALID_EVENTS:
        print(f"WARN: Unknown event type '{event}'. Allowed: {sorted(VALID_EVENTS)}", file=sys.stderr)

    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "session_id": os.environ.get("CLAUDE_SESSION_ID", "unknown"),
        "cwd": str(Path.cwd()),
    }
    if data:
        record["data"] = data

    log_path = get_daily_log_path()
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def summarize(days: int = 7) -> dict:
    """Aggregate the last N days into a quick report."""
    telemetry_dir = get_telemetry_dir()
    if not telemetry_dir.exists():
        return {"error": "no telemetry yet"}

    events_by_type: dict[str, int] = {}
    total_events = 0
    phase_durations: dict[str, list[float]] = {}

    for log_file in sorted(telemetry_dir.glob("udiv-runs-*.jsonl"))[-days:]:
        with log_file.open(encoding="utf-8") as fh:
            for line in fh:
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                total_events += 1
                evt = rec.get("event", "unknown")
                events_by_type[evt] = events_by_type.get(evt, 0) + 1

                if evt == "phase_complete":
                    data = rec.get("data", {})
                    phase = data.get("phase")
                    dur = data.get("duration_ms")
                    if phase and isinstance(dur, (int, float)):
                        phase_durations.setdefault(phase, []).append(float(dur))

    phase_avg = {
        p: round(sum(v) / len(v), 1) for p, v in phase_durations.items() if v
    }

    return {
        "days_analyzed": days,
        "total_events": total_events,
        "events_by_type": events_by_type,
        "phase_avg_duration_ms": phase_avg,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="LogosFortuna telemetry writer")
    sub = parser.add_subparsers(dest="cmd", required=True)

    write_p = sub.add_parser("write", help="Append a telemetry event")
    write_p.add_argument("event", help=f"Event type. Valid: {sorted(VALID_EVENTS)}")
    write_p.add_argument("--data", default=None, help="JSON-encoded data payload")

    sum_p = sub.add_parser("summarize", help="Summarize last N days")
    sum_p.add_argument("--days", type=int, default=7)

    args = parser.parse_args()

    if args.cmd == "write":
        data = None
        if args.data:
            try:
                data = json.loads(args.data)
            except json.JSONDecodeError as e:
                print(f"ERROR: --data is not valid JSON: {e}", file=sys.stderr)
                return 2
        write_event(args.event, data)
        return 0

    if args.cmd == "summarize":
        report = summarize(args.days)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
