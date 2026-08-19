"""Static/document lock for the M100A runtime-gap priority discovery."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / (
    "docs/architecture/"
    "MILESTONE_100A_ACTIVE_RUNTIME_GAP_CONSUMER_PRIORITY_DISCOVERY.md"
)


def _text() -> str:
    return RECORD.read_text(encoding="utf-8")


def test_m100a_is_read_only_and_records_current_authority():
    text = _text()
    required = (
        "# Milestone 100A Active Runtime Gap and Consumer Priority Discovery",
        "STRICT READ-ONLY ARCHITECTURE / RUNTIME DISCOVERY / PRIORITY ANALYSIS",
        "DESIGN CANDIDATE / DISCOVERY COMPLETE LOCALLY / PM PRIORITY REVIEW REQUIRED",
        "4d4e60edf87441aef51d6b948172e5ca03f77191",
        "3144/3144 passed, 0 failures, 0 errors, 9 warnings",
        "306 paths / 112 schemas",
        "8 direct @app routes / 23 include_router / 0 direct /action/*",
        "Generic Act: `NOT_IMPLEMENTED`",
        "Generic Act integration: `NOT_AUTHORIZED`",
        "Generic Act authority: `NOT_GRANTED`",
    )
    for marker in required:
        assert marker in text, marker


def test_m100a_selected_gap_has_real_consumer_proof():
    text = _text()
    required = (
        "GAP-01: Live Action Authority Consolidation",
        "GAP-01_LIVE_ACTION_AUTHORITY_CONSOLIDATION",
        "ACTION_AUTHORITY_CONSOLIDATION_GAP",
        "HIGH_PRIORITY_REAL_GAP",
        "**Consumer-proof strength:** STRONG",
        "file_routes.py:48-60",
        "tool_executor_routes.py:21-31",
        "patch_routes.py:72-83",
        "core/coordination.py:33-122",
        "restricted_file_read_bridge.py:4-34",
        "There is no single current, capability-scoped action-binding boundary",
        "**Expected value:** One understandable authority boundary",
        "JUSTIFIED FOR PM REVIEW",
    )
    for marker in required:
        assert marker in text, marker


def test_candidate_table_and_priority_alternatives_are_locked():
    text = _text()
    required = (
        "## 11. Candidate Gap Table",
        "GAP-02",
        "GAP-03",
        "GAP-04",
        "GAP-05",
        "GAP-06",
        "GAP-07",
        "MEDIUM_PRIORITY_REAL_GAP",
        "LOW_PRIORITY_REAL_GAP",
        "NOT_JUSTIFIED",
        "## 12. Priority Model",
        "## 15. Selected Next Candidate",
        "Why alternatives are deferred",
    )
    for marker in required:
        assert marker in text, marker


def test_observation_chat_memory_time_and_governance_boundaries_are_locked():
    text = _text()
    required = (
        "## 7. Observation and Verification Audit",
        "No new evidence supports durable Observation as a general runtime consumer",
        "real current producer/consumer pair",
        "## 8. `/chat` Legacy-versus-Canonical Audit",
        "not authorization to\nwire `/chat` to Core Coordination",
        "## 9. Memory and Time Audit",
        "session identifiers do not isolate Working Memory or\nTimeline",
        "## 10. Governance, Approval, and Action Audit",
        "two stores",
        "fresh identity and policy checks",
    )
    for marker in required:
        assert marker in text, marker


def test_future_build_and_non_goals_are_frozen_without_authorization():
    text = _text()
    required = (
        "## 16. Smallest Possible Future Build Boundary",
        "beginning with\n`file.restricted_read`",
        "preserve call-local Observation without adding durable persistence",
        "## 18. Explicit Non-Goals",
        "any production code or runtime behavior change",
        "a ThinkingProposal producer, adapter, provider, or factory",
        "Generic Act, generic capability registry, or generic Action dispatch",
        "M100B, M101, or any successor Build",
        "commit, tag, push, or PM acceptance claim",
        "Runtime Build authorization: NOT GRANTED",
        "Next authorized action: HUMAN/PROJECT-MANAGER M100A PRIORITY REVIEW",
    )
    for marker in required:
        assert marker in text, marker
