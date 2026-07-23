"""Identity seed integrity guard for Aether.

Per Constitution 1.1–1.2, the identity seed must not be silently modified.
This module computes a SHA-256 checksum on load, stores it under private_dir,
and detects tampering or unauthorized changes on subsequent verifications.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Optional

from aether.core.config import ensure_dir, get_identity_seed_path, get_private_dir
from aether.time.clock import get_timezone, now_iso


GUARD_SUBDIR = "identity_guard"
GUARD_FILENAME = "identity_seed_integrity.json"


def _guard_state_path() -> Path:
    return ensure_dir(
        get_private_dir() / GUARD_SUBDIR,
        create=True,
    ) / GUARD_FILENAME


def _compute_sha256(file_path: Path) -> str:
    """Return hex SHA-256 digest of a file."""
    h = hashlib.sha256()
    with file_path.open("rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def _new_state(seed_path_str: str, sha256_hex: str) -> dict:
    ts = now_iso()
    tz = get_timezone()
    return {
        "type": "identity_seed_integrity",
        "version": "0.1.0",
        "created": ts,
        "updated": ts,
        "timezone": tz,
        "identity_seed_path": seed_path_str,
        "current_sha256": sha256_hex,
        "known_sha256": sha256_hex,
        "status": "initialized",
        "events": [
            {
                "time": ts,
                "event": "initialized",
                "description": "Identity seed guard initialized with current checksum.",
                "sha256_prefix": sha256_hex[:12],
            }
        ],
    }


def _safe_summary(state: dict) -> dict:
    """Return a safe copy with truncated hashes — never exposes full paths or seed content."""
    return {
        "status": state.get("status", "unknown"),
        "current_sha256": (state.get("current_sha256") or "")[:12],
        "known_sha256": (state.get("known_sha256") or "")[:12],
        "changed": state.get("status") == "changed",
        "updated": state.get("updated"),
        "warnings": [
            e.get("description", "")
            for e in state.get("events", [])
            if e.get("event") in ("checksum_mismatch", "file_missing", "load_failed")
        ],
    }


# ------------------------------------------------------------------ #
# Public API                                                           #
# ------------------------------------------------------------------ #


def initialize_identity_guard(metadata: Optional[dict] = None) -> dict:
    """Initialize the identity guard by computing and storing the seed checksum.

    Creates the guard state file at:
        <private_dir>/identity_guard/identity_seed_integrity.json

    Returns:
        The guard state dict (with full paths and hashes included).
    """
    seed_path = get_identity_seed_path()

    if not seed_path.exists():
        raise FileNotFoundError(f"Identity Seed not found: {seed_path}")

    sha256_hex = _compute_sha256(seed_path)
    state = _new_state(str(seed_path), sha256_hex)

    if metadata:
        state["metadata"] = metadata

    _guard_state_path().write_text(
        json.dumps(state, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return state


def load_identity_guard_state() -> Optional[dict]:
    """Load the guard state from disk, or return None if missing."""
    path = _guard_state_path()
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def verify_identity_integrity(metadata: Optional[dict] = None) -> dict:
    """Verify the current identity seed against the stored checksum.

    Behavior:
    - If no guard state exists: raises FileNotFoundError (call initialize first).
    - If checksum matches: status stays "verified".
    - If checksum differs: status becomes "changed" — does NOT auto-accept.

    Returns:
        Safe summary dict with truncated hashes. Never exposes seed content.
    """
    seed_path = get_identity_seed_path()
    guard_path = _guard_state_path()

    if not guard_path.exists():
        raise FileNotFoundError(
            "No identity guard state found. Call initialize_identity_guard() first."
        )

    try:
        state = json.loads(guard_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        state = _new_state(str(seed_path), "failed")
        state["status"] = "failed"
        state["events"].append({
            "time": now_iso(),
            "event": "load_failed",
            "description": "Failed to load or parse guard state file.",
        })
        guard_path.write_text(
            json.dumps(state, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return _safe_summary(state)

    old_known = state.get("known_sha256", "")

    if not seed_path.exists():
        state["status"] = "missing"
        state["current_sha256"] = ""
        state["updated"] = now_iso()
        state["events"].append({
            "time": now_iso(),
            "event": "file_missing",
            "description": f"Identity seed file is missing: {seed_path.name}",
        })
        guard_path.write_text(
            json.dumps(state, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return _safe_summary(state)

    current_sha256 = _compute_sha256(seed_path)
    state["current_sha256"] = current_sha256
    state["updated"] = now_iso()

    if current_sha256 == old_known:
        state["status"] = "verified"
        state["events"].append({
            "time": now_iso(),
            "event": "verified",
            "description": "Identity seed checksum matches known value.",
            "sha256_prefix": current_sha256[:12],
        })
    else:
        state["status"] = "changed"
        state["events"].append({
            "time": now_iso(),
            "event": "checksum_mismatch",
            "description": (
                f"Identity seed checksum changed! "
                f"known={old_known[:12]} current={current_sha256[:12]}"
            ),
            "known_sha256_prefix": old_known[:12],
            "current_sha256_prefix": current_sha256[:12],
        })

    guard_path.write_text(
        json.dumps(state, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return _safe_summary(state)


def identity_guard_status() -> dict:
    """Return a safe status summary of the identity guard.

    Returns empty-safe summary if no guard state exists yet.
    """
    path = _guard_state_path()
    if not path.exists():
        return {
            "status": "not_initialized",
            "current_sha256": "",
            "known_sha256": "",
            "changed": False,
            "updated": None,
            "warnings": [],
        }

    state = load_identity_guard_state()
    if state is None:
        return {
            "status": "failed",
            "current_sha256": "",
            "known_sha256": "",
            "changed": False,
            "updated": None,
            "warnings": ["Failed to load guard state."],
        }

    return _safe_summary(state)
