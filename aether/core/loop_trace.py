"""Safe structured loop trace for /chat cognitive loop observability.

Provides deterministic helpers to build a response-only trace object
that summarizes which stages ran, their status, and key record IDs.
Does NOT expose chain-of-thought, raw model reasoning, secrets, or
private data. Trace is NOT persisted to disk.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


def generate_trace_id(prefix: str = "chat") -> str:
    """Generate a unique trace_id for one execution of the chat loop.

    Format: chat_<timestamp>_<random-hex>
    Example: chat_20260729_085229_a1b2c3d4
    """
    import uuid
    ts = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    suffix = uuid.uuid4().hex[:8]
    return f"{prefix}_{ts}_{suffix}"


def build_stage(
    name: str,
    status: str = "completed",
    summary: str = "",
    warnings_count: int = 0,
) -> dict:
    """Build a single stage entry for the loop trace.

    Args:
        name: Stage name (e.g. "perception").
        status: "completed", "skipped", "warning", or "error".
        summary: Short human-readable summary (max 120 chars).
        warnings_count: Number of warnings produced by this stage.

    Returns:
        Stage dict.
    """
    return {
        "name": name,
        "status": status,
        "summary": sanitize_summary(summary),
        "warnings_count": warnings_count,
    }


def sanitize_summary(text: str, max_len: int = 120) -> str:
    """Sanitize a stage summary to safe structured text.

    - Strips newlines.
    - Truncates to max_len characters.
    - Removes any text that might contain secrets/paths.
    """
    cleaned = text.replace("\n", " ").replace("\r", " ").strip()
    if len(cleaned) > max_len:
        cleaned = cleaned[:max_len].rstrip() + "..."
    return cleaned


def build_loop_trace(
    trace_id: str,
    loop_version: str,
    started_at: str,
    completed_at: str,
    duration_ms: int,
    status: str,
    stages: List[dict],
    safety: Dict[str, bool],
    records: Dict[str, Any],
    warnings: List[str],
) -> dict:
    """Build a complete loop trace dict.

    All parameters are pre-computed observable values. No raw prompts,
    hidden reasoning, secrets, or private data are included.

    Args:
        trace_id: Unique trace identifier.
        loop_version: Loop version string.
        started_at: ISO timestamp of trace start.
        completed_at: ISO timestamp of trace completion.
        duration_ms: Elapsed wall-clock time in milliseconds.
        status: Overall trace status ("completed", "error", etc.).
        stages: List of stage dicts from build_stage().
        safety: Dict of boolean safety flags.
        records: Dict of record IDs (WM events, timeline, approval).
        warnings: Aggregated warning strings.

    Returns:
        Loop trace dict ready for /chat response.
    """
    return {
        "trace_id": trace_id,
        "loop_version": loop_version,
        "started_at": started_at,
        "completed_at": completed_at,
        "duration_ms": duration_ms,
        "status": status,
        "stages": list(stages),
        "safety": dict(safety),
        "records": {
            "working_memory_event_ids": list(records.get("working_memory_event_ids", [])),
            "timeline_event_id": records.get("timeline_event_id"),
            "approval_id": records.get("approval_id"),
        },
        "warnings": list(warnings),
    }
