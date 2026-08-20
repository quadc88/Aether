"""Static/document lock for the M101A Build-scope boundary."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / (
    "docs/architecture/"
    "MILESTONE_101A_ACTION_AUTHORITY_CONSOLIDATION_BUILD_SCOPE_BOUNDARY.md"
)


def _text() -> str:
    return RECORD.read_text(encoding="utf-8")


def test_m101a_current_authority_and_reference_capability_are_locked():
    text = _text()
    required = (
        "# Milestone 101A Action Authority Consolidation Build-Scope Boundary",
        "STRICT DESIGN / DISCOVERY / BUILD-SCOPE BOUNDARY",
        "bed3667dcaf5304979c15d86605de75684ac7532",
        "GAP-01_LIVE_ACTION_AUTHORITY_CONSOLIDATION",
        "ACTION_AUTHORITY_CONSOLIDATION_GAP",
        "Consumer-proof strength: `STRONG`",
        "Authority risk: `HIGH`",
        "Future Build: `JUSTIFIED FOR PM REVIEW ONLY`",
        "Actual production Build: `NOT YET AUTHORIZED`",
        "Generic Act: `NOT_IMPLEMENTED`",
        "Generic Act integration: `NOT_AUTHORIZED`",
        "Generic Act authority: `NOT_GRANTED`",
        "`file.restricted_read`",
        "CANONICAL_GOVERNED_CAPABILITY",
        "ACTION_SPECIFIC_GOVERNED_EXECUTION",
        "LEGACY_COMPATIBILITY_EXECUTION",
        "DIRECT_UNIFIED_AUTHORITY_NOT_PROVEN",
        "NON_EXECUTING_PLANNING_PATH",
    )
    for marker in required:
        assert marker in text, marker


def test_m101a_ownership_and_build_models_are_locked():
    text = _text()
    required = (
        "## 6. Ownership Matrix",
        "Core Governance",
        "Core Coordination",
        "restricted_file_read_bridge.py",
        "verify_restricted_file_read",
        "MODEL_A_CAPABILITY_AUTHORITY_BINDING_SERVICE",
        "MODEL_B_SHARED_ACTION_AUTHORITY_REGISTRY",
        "MODEL_C_ROUTE_LEVEL_CLASSIFICATION_ONLY",
        "MODEL_D_NO_BUILD_YET",
        "A_SMALL_CAPABILITY_SCOPED_BUILD_JUSTIFIED",
        "Recommended Build scope: `JUSTIFIED FOR PM REVIEW` only.",
    )
    for marker in required:
        assert marker in text, marker


def test_m101a_smallest_boundary_and_contract_are_locked():
    text = _text()
    required = (
        "## 11. Exact Smallest Build Boundary",
        "aether/action/services/restricted_file_read_authority_binding.py",
        "aether/core/coordination.py",
        "RestrictedReadScope",
        "existing canonical restricted-read execution path",
        "No route, request model, OpenAPI, or `api_server.py` change",
        "## 12. Required Tests for a Future Build",
        "direct-mode fallback is impossible",
        "call-local Observation",
        "## 13. OpenAPI and `api_server` Impact",
        "306 paths / 112 schemas",
        "8 direct @app routes / 23 include_router / 0 direct /action/*",
    )
    for marker in required:
        assert marker in text, marker


def test_m101a_failure_rollback_and_non_goals_are_locked():
    text = _text()
    required = (
        "## 14. Failure-Closed Behavior",
        "There must be no fallback from a failed governed binding to direct reader mode",
        "## 15. Rollback and Removal Path",
        "without data migration",
        "## 17. Explicit Non-Goals",
        "Generic Act, generic capability registry, or generic Action dispatch",
        "M101B, M102, or any successor runtime Build",
        "commit, tag, push, or a PM acceptance claim",
        "Actual production Build authorization: NOT YET AUTHORIZED",
        "Next authorized action: HUMAN/PROJECT-MANAGER M101A BUILD-SCOPE REVIEW",
    )
    for marker in required:
        assert marker in text, marker
