"""Static design locks for the documentation-only Milestone 94C decision."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "docs/architecture/MILESTONE_94C_RESTRICTED_READ_OBSERVATION_CONSUMER_PROOF_RECORD.md"


def _text() -> str:
    return RECORD.read_text(encoding="utf-8")


def test_record_exists_and_has_required_headings():
    text = _text()
    assert text.startswith("# Milestone 94C Restricted-Read Observation Consumer-Proof Decision Record")
    for heading in (
        "## 1. Purpose",
        "## 2. Scope",
        "## 3. Current Milestone Authority",
        "## 4. M94B Proven Producer",
        "## 5. Existing Observation Intake Contract",
        "## 6. Producer-to-Consumer Mapping Result",
        "## 7. `collector_contract_id` Decision",
        "## 8. `plan_step_id` Decision",
        "## 9. `expected` / `observed` Decision",
        "## 10. Verification-Layer Separation",
        "## 11. Observation Classification vs Capability Verification",
        "## 12. Ownership and Dependency Direction",
        "## 13. Persistence and Privacy Decision",
        "## 14. Status Mapping Decision",
        "## 15. Observation Lifecycle Preservation",
        "## 16. API Decision",
        "## 17. Generic Capability Freeze",
        "## 18. Aggregator / Critic / Repair / Learn Freeze",
        "## 19. Rejected Integration Models",
        "## 20. Selected Outcome",
        "## 21. Runtime Bridge Decision",
        "## 22. Required Future Prerequisites",
        "## 23. Future Contract-Revision Gate",
        "## 24. Milestone 94 Closure Relationship",
        "## 25. Architectural Invariants Preserved",
        "## 26. Authoritative-Until-Revised Clause",
    ):
        assert heading in text, heading


def test_decision_and_contract_gaps_are_locked():
    text = _text()
    for marker in (
        "M94C runtime bridge: NOT JUSTIFIED",
        "Outcome C - Existing Observation Intake Contract Not Yet Compatible: SELECTED",
        "The current Observation Intake production caller is NONE.",
        "restricted-read Observation is call-local.",
        "Record from 94B is NONE.",
        "Observation Intake remains `DEFER_FIRST_SLICE`",
        "COLLECTOR_CONTRACT_MAPPING: NOT_PROVEN",
        "PLAN_STEP_MAPPING: NOT_PROVEN",
        "EXPECTED_OBSERVED_MAPPING: NOT_PROVEN",
        "Privacy-safe persistence: NOT_PROVEN",
        "approval_id",
        "execution_attempt_id",
        "session_id",
        "capability_id",
        "task_binding",
        "scope identity",
        "restricted_read",
        "phase2",
        "step1",
        "file should\nexist",
        "read should succeed",
        "content should equal X",
    ):
        assert marker in text, marker


def test_verification_statuses_are_not_observation_classification():
    text = _text()
    for marker in (
        "capability-specific\ndeterministic Verification",
        "future multi-observation,",
        "lifecycle-level concept",
        "VERIFIED_SUCCESS != matched",
        "VERIFIED_PARTIAL != matched/mismatched",
        "DENIED != mismatched",
        "NOT_FOUND != mismatched",
        "CHANGED_DURING_READ != mismatched",
        "INTERNAL_ERROR != mismatched",
        "No direct semantic conversion is",
        "authorized:",
    ):
        assert marker in text, marker


def test_privacy_status_lifecycle_and_freezes_are_locked():
    text = _text()
    for marker in (
        "raw file content",
        "returned content",
        "secret matches",
        "credentials",
        "tokens",
        "API keys",
        "private keys",
        "RestrictedReadScope",
        "approved_root",
        "bound function",
        "scope lock",
        "scope dispatch state",
        "raw reader",
        "metadata",
        "authorization internals",
        "Normalized private target/path must not\nbe persisted by default",
        "Durable Observation Record now: NO",
        "Observation Intake now: NO",
        "Lifecycle transition: NONE",
        "Critic: NO",
        "Repair: NO",
        "Learning: NO",
        "Memory write: NO",
        "VALID_STATUSES` is exactly `pending`, `matched`, `mismatched`, `error`,",
        "Lifecycle decision at intake is `None`",
        "Later update/cancel operations are pending-only",
        "`decision` is queue-owned lifecycle metadata",
        "`completed` is a service-envelope status only",
        "NEW API: NO",
        "Verification Aggregation, Critic triggering, Repair triggering",
        "NOT IMPLEMENTED and NOT AUTHORIZED",
        "Preserve exactly `file.restricted_read`",
        "Milestone 94 remains OPEN",
        "No Milestone 94D is defined",
    ):
        assert marker in text, marker


def test_outcomes_and_no_runtime_bridge_are_locked():
    text = _text()
    assert "Outcome A - DIRECT INTAKE BRIDGE: REJECTED" in text
    assert "Outcome B - THIN ADAPTER: REJECTED" in text
    assert "Outcome D - CONTRACT REVISION REQUIRED: possible future direction" in text
    assert "No runtime wiring is authorized by this record." in text
    assert "No production write set exists" in text


def test_record_is_static_documentation_only():
    source = Path(__file__).read_text(encoding="utf-8")
    assert "Test" + "Client" not in source
    assert "sub" + "process" not in source
    assert "import " + "aether" not in source
    assert "observation_record_" + "queue" not in source
    assert "handle_observation_" + "intake" not in source
    assert "execute_approved_" + "restricted_read" not in source
    assert "authorize_restricted_" + "read_execution" not in source
    assert "op" + "en(" not in source.replace('"op" + "en("', "")
    assert ".write_" + "text(" not in source
