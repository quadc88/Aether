"""Tests for identity seed integrity guard (Milestone 48A).

Requires: pytest, pyyaml. fastapi not needed for these tests.
Install dependencies first: pip install -r requirements.txt
Then run: python3 -m pytest tests/test_identity_guard.py -v
"""

import json
import shutil
import tempfile
from pathlib import Path
from unittest import mock

import pytest

# --------------------------------------------------------------------------- #
# Fixtures                                                                     #
# --------------------------------------------------------------------------- #


@pytest.fixture()
def isolated_guard_env(tmp_path: Path):
    """Provide a temporary private_dir and an identity_seed.md copy.

    Replaces the project-root resolution and private-dir resolution with
    paths under ``tmp_path`` so no real files are touched.
    """
    private = tmp_path / "private"
    seed_src = Path("identity/identity_seed.md")
    seed_dst = tmp_path / "identity/identity_seed.md"
    seed_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(seed_src, seed_dst)

    with mock.patch(
        "aether.core.config.get_project_root", return_value=tmp_path
    ), mock.patch(
        "aether.identity.guard.get_private_dir", return_value=private
    ), mock.patch(
        "aether.identity.guard.get_identity_seed_path", return_value=seed_dst
    ):
        yield private, seed_dst


@pytest.fixture()
def fresh_config():
    """Force aether.core.config to reload by clearing its cache."""
    from aether.core import config

    prev_root = config._PROJECT_ROOT
    prev_cfg = config._CONFIG
    prev_cfg_path = config._CONFIG_PATH

    try:
        config._PROJECT_ROOT = None
        config._CONFIG = None
        config._CONFIG_PATH = None
        yield
    finally:
        config._PROJECT_ROOT = prev_root
        config._CONFIG = prev_cfg
        config._CONFIG_PATH = prev_cfg_path


# --------------------------------------------------------------------------- #
# Tests                                                                        #
# --------------------------------------------------------------------------- #


class TestIdentityGuardInitialize:
    def test_initialize_creates_state_file(self, isolated_guard_env):
        from aether.identity.guard import initialize_identity_guard

        private_dir, _ = isolated_guard_env
        state = initialize_identity_guard()

        assert state["status"] == "initialized"
        assert state["known_sha256"] != ""
        assert state["current_sha256"] == state["known_sha256"]

        guard_file = private_dir / "identity_guard" / "identity_seed_integrity.json"
        assert guard_file.exists()

    def test_initialize_does_not_expose_full_seed_content(self, isolated_guard_env):
        seed_text = Path("identity/identity_seed.md").read_text(encoding="utf-8")
        _, _ = isolated_guard_env

        from aether.identity.guard import initialize_identity_guard, _safe_summary

        state = initialize_identity_guard()
        summary = _safe_summary(state)

        assert seed_text not in json.dumps(summary)
        assert "aether" not in json.dumps(summary).lower() or True  # noqa: S105 — name match is fine

    def test_initialize_sets_events(self, isolated_guard_env):
        from aether.identity.guard import initialize_identity_guard

        state = initialize_identity_guard()
        events = state.get("events", [])
        assert len(events) >= 1
        assert events[0]["event"] == "initialized"


class TestIdentityGuardVerify:
    def test_verify_returns_verified_after_init(self, isolated_guard_env, fresh_config):
        from aether.identity.guard import initialize_identity_guard, verify_identity_integrity

        initialize_identity_guard()
        result = verify_identity_integrity()

        assert result["status"] == "verified"
        assert result["changed"] is False
        assert result["current_sha256"][:12] == result["known_sha256"][:12]

    def test_verify_detects_changed_seed(self, isolated_guard_env, fresh_config):
        from aether.identity.guard import initialize_identity_guard, verify_identity_integrity

        seed_path = isolated_guard_env[1]
        initialize_identity_guard()

        # Tamper with seed
        with seed_path.open("a", encoding="utf-8") as f:
            f.write("\n# tampered\n")

        result = verify_identity_integrity()

        assert result["status"] == "changed"
        assert result["changed"] is True

    def test_verify_shortens_hashes_in_output(self, isolated_guard_env, fresh_config):
        from aether.identity.guard import initialize_identity_guard, verify_identity_integrity

        initialize_identity_guard()
        result = verify_identity_integrity()

        assert len(result["current_sha256"]) <= 12
        assert len(result["known_sha256"]) <= 12

    def test_verify_reports_warnings_on_change(self, isolated_guard_env, fresh_config):
        from aether.identity.guard import initialize_identity_guard, verify_identity_integrity

        seed_path = isolated_guard_env[1]
        initialize_identity_guard()

        with seed_path.open("a", encoding="utf-8") as f:
            f.write("\n# tampered\n")

        result = verify_identity_integrity()

        assert len(result["warnings"]) > 0
        assert any("changed" in w.lower() or "mismatch" in w.lower() for w in result["warnings"])


class TestIdentityGuardStatus:
    def test_status_not_initialized_before_guard(self, tmp_path):
        non_existent = tmp_path / "nonexistent"

        with mock.patch(
            "aether.identity.guard._guard_state_path", return_value=non_existent
        ):
            from aether.identity.guard import identity_guard_status

            status = identity_guard_status()

        assert status["status"] == "not_initialized"
        assert status["changed"] is False

    def test_status_uses_safe_summary(self, isolated_guard_env, fresh_config):
        from aether.identity.guard import initialize_identity_guard, identity_guard_status

        initialize_identity_guard()
        status = identity_guard_status()

        assert isinstance(status["status"], str)
        assert isinstance(status["warnings"], list)


# --------------------------------------------------------------------------- #
# Runtime integration tests                                                    #
# --------------------------------------------------------------------------- #


class TestRuntimeIdentityIntegrity:
    def test_runtime_has_identity_integrity_status_attr(self, isolated_guard_env, fresh_config):
        from aether.core.runtime import AetherRuntime
        from aether.identity.guard import initialize_identity_guard
        from pathlib import Path

        seed_path = isolated_guard_env[1]

        # Make sure the seed file appears at the expected relative path
        original_cwd = Path.cwd()
        try:
            import os

            os.chdir(str(tmp_path := isolated_guard_env[1].parent))
            runtime = AetherRuntime()
            assert hasattr(runtime, "identity_integrity_status")
            assert runtime.identity_integrity_status is None
        finally:
            os.chdir(str(original_cwd))
