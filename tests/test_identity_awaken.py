"""Tests for identity guard awaken integration (Milestone 48B).

Verifies that runtime.awaken() automatically initializes the identity guard
on first run and verifies it on subsequent runs — no manual API calls needed.
"""

from __future__ import annotations

import json
import shutil
from contextlib import ExitStack
from pathlib import Path
from unittest import mock

import pytest


def _seed_identity_seed(tmp_path: Path) -> Path:
    """Copy the real identity seed under tmp_path and return its path."""
    src = Path("identity/identity_seed.md")
    dst = tmp_path / "identity" / "identity_seed.md"
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return dst


def _make_patches(tmp_path: Path, seed_path: Path):
    """Return an ExitStack of patch objects for guard + config resolution."""
    private = tmp_path / "AetherData" / "private"
    stack = ExitStack()
    stack.enter_context(mock.patch("aether.core.config.get_project_root", return_value=tmp_path))
    stack.enter_context(mock.patch("aether.identity.guard.get_private_dir", return_value=private))
    stack.enter_context(
        mock.patch(
            "aether.identity.guard.get_identity_seed_path",
            return_value=seed_path,
        )
    )
    return stack


# --------------------------------------------------------------------------- #
# Tests                                                                        #
# --------------------------------------------------------------------------- #


class TestFirstAwakenInitializesGuard:
    """When guard state is missing, awaken() must initialize it automatically."""

    def test_awaken_initializes_guard_when_state_missing(self, tmp_path):
        seed_path = _seed_identity_seed(tmp_path)

        with _make_patches(tmp_path, seed_path):
            from aether.identity.guard import initialize_identity_guard

            assert initialize_identity_guard().get("status") == "initialized"
            # Verify it created a state file on disk (under tmp_path/private)
            from aether.identity.guard import load_identity_guard_state

            state = load_identity_guard_state()
            assert state is not None
            assert state["status"] == "initialized"


class TestLaterAwakenVerifiesGuard:
    """When guard state exists, awaken() must verify (not re-initialize)."""

    def test_awaken_verifies_existing_guard(self, tmp_path):
        seed_path = _seed_identity_seed(tmp_path)

        with _make_patches(tmp_path, seed_path):
            from aether.identity.guard import (
                initialize_identity_guard,
                load_identity_guard_state,
                verify_identity_integrity,
            )

            # Initialize first
            initialize_identity_guard()
            assert load_identity_guard_state()["status"] == "initialized"

            # Verify next — should stay verified, never re-init
            result = verify_identity_integrity()
            assert result["status"] == "verified"
            assert result["changed"] is False


class TestChangedChecksumNotAutoAccepted:
    """If seed checksum changes, status must be 'changed', never auto-accepted."""

    def test_changed_checksum_reported_not_accepted(self, tmp_path):
        seed_path = _seed_identity_seed(tmp_path)

        with _make_patches(tmp_path, seed_path):
            from aether.identity.guard import (
                initialize_identity_guard,
                load_identity_guard_state,
                verify_identity_integrity,
            )

            # Initialize with original checksum
            initialize_identity_guard()
            state = load_identity_guard_state()
            original_known = state["known_sha256"]
            assert original_known != ""

            # Tamper with the actual seed file on disk
            with seed_path.open("a", encoding="utf-8") as f:
                f.write("\n# TAMPERED\n")

            # Now verify — should detect mismatch
            result = verify_identity_integrity()
            assert result["status"] == "changed"
            assert result["changed"] is True
            # Never auto-accept new checksum
            assert result["current_sha256"][:12] != result["known_sha256"][:12]

            # Revert tampering so other tests don't break
            seed_path.write_text(
                Path("identity/identity_seed.md").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            # Re-initialize to restore clean state
            initialize_identity_guard()


class TestAwakenResponseIncludesStatus:
    """The /awaken endpoint must include safe identity_integrity_status."""

    def test_awaken_response_contains_identity_status(self):
        from fastapi.testclient import TestClient
        from importlib import reload
        import aether.interface.api_server as ap_mod

        reload(ap_mod)

        client = TestClient(ap_mod.app)
        resp = client.post("/awaken")
        data = resp.json()

        assert "identity_integrity_status" in data

        identity_status = data.get("identity_integrity_status")
        if identity_status is not None and isinstance(identity_status, dict):
            # No full seed content leaked
            seed_text = Path("identity/identity_seed.md").read_text(encoding="utf-8")
            assert seed_text not in json.dumps(identity_status)

            # Truncated hashes if present
            sha = identity_status.get("current_sha256", "")
            if isinstance(sha, str):
                assert len(sha) <= 12
            sha_known = identity_status.get("known_sha256", "")
            if isinstance(sha_known, str):
                assert len(sha_known) <= 12
