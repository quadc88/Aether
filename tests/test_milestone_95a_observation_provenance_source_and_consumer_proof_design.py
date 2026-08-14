"""Static content locks for the Milestone 95A provenance boundary."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "docs/architecture/MILESTONE_95A_OBSERVATION_PROVENANCE_SOURCE_AND_CONSUMER_PROOF_BOUNDARY.md"


def _text() -> str:
    return RECORD.read_text(encoding="utf-8")


def test_title_purpose_and_m94_durable_parent_are_locked():
    text = _text()
    for marker in (
        "# Milestone 95A Observation Provenance Source and Consumer-Proof Boundary",
        "Classification: PLAN / CONTRACT / CONSUMER-PROOF ONLY",
        "Milestone 94 is externally CLOSED / GIT-DURABLE / PM-ACCEPTED",
        "6ecc5dd254335e8f6d0020050db0674d96a9fd05",
        "milestone-94-governed-read-only-action-vertical-slice-closure",
        "Milestone 95 is authorized for 95A Plan only",
        "M95B is NOT AUTHORIZED",
    ):
        assert marker in text


def test_94c_incompatibility_facts_are_locked():
    text = _text()
    for marker in (
        "94C Gap Re-Proof",
        "plan_step_id",
        "collector_contract_id",
        "expected_value",
        "NOT_CURRENTLY_PROVABLE",
        "CURRENT_INTAKE_EXPECTATION_MODEL_INCOMPATIBLE",
        "C_NOT_YET_COMPATIBLE",
        "`approval_id` is not\n`plan_step_id`",
        "`execution_attempt_id` is not `collector_contract_id`",
        "Current proven durable consumer: NONE.",
    ):
        assert marker in text


def test_producer_inventory_is_locked():
    text = _text()
    for marker in (
        "POST /chat/restricted-read/resume",
        "fresh Core Governance authorization",
        "private one-shot Strategy C scope",
        "dispatch_restricted_read",
        "read_restricted_file",
        "call-local RestrictedReadObservation",
        "verify_restricted_file_read",
        "execution_attempt_id",
        "capability `file.restricted_read`",
        "normalized target",
        "privacy-filtered",
        "CHANGED_DURING_READ",
    ):
        assert marker in text


def test_consumer_requirement_inventory_is_locked():
    text = _text()
    for marker in (
        "handle_observation_" + "intake(request, context=None)",
        "non-empty `plan_step_id`",
        "non-empty `collector_contract_id`",
        "`evidence_items` list",
        "`observed_value`",
        "`expected_value`",
        "`matched` or `mismatched`",
        "json.dumps(value, sort_keys=True)",
        "persistent queue envelope",
        "no current restricted-read caller",
    ):
        assert marker in text


def test_semantic_compatibility_and_provenance_classification_are_locked():
    text = _text()
    for marker in (
        "Producer-to-Consumer Compatibility Matrix",
        "Lossless mapping",
        "New contract",
        "target identity",
        "Action identity",
        "Observation identity",
        "verification relationship",
        "downstream consumer identity",
        "NEW_PLAN_STEP_CONTRACT_REQUIRED",
        "NEW_COLLECTOR_CONTRACT_REQUIRED",
        "No expectation may be synthesized",
        "semantically incompatible",
    ):
        assert marker in text


def test_privacy_and_verification_relationship_are_locked():
    text = _text()
    for marker in (
        "REQUIRES_SEPARATE_PRIVACY_CONTRACT",
        "NOT_SAFE_TO_PERSIST",
        "raw content",
        "normalized paths",
        "retention, lifecycle, visibility, and access-control",
        "VERIFIED_SUCCESS",
        "VERIFIED_PARTIAL",
        "DENIED",
        "NOT_FOUND",
        "CHANGED_DURING_READ",
        "INTERNAL_ERROR",
        "do not collapse",
        "preserve capability Verification separately",
    ):
        assert marker in text


def test_consumer_proof_and_candidate_model_decision_are_locked():
    text = _text()
    for marker in (
        "Current proven durable consumer: NONE.",
        "PROVEN_CURRENT_CONSUMER",
        "NOT_JUSTIFIED",
        "NOT_IMPLEMENTED",
        "Model A",
        "Model B",
        "Model C",
        "Model D",
        "Model E",
        "MODEL_B_JUSTIFIED",
        "Model E as the current runtime containment boundary",
        "No Aggregator, Critic, Repair, or Learning shortcut",
    ):
        assert marker in text


def test_no_runtime_bridge_or_downstream_shortcut_and_m95b_gate_are_locked():
    text = _text()
    for marker in (
        "M95_PROVENANCE_FOUNDATION_REQUIRED_BEFORE_RUNTIME",
        "No runtime bridge is justified",
        "No 95B runtime plan",
        "does not authorize runtime code",
        "Observation Intake integration or caller",
        "persistent Observation Record",
        "Verification Aggregation",
        "Critic",
        "Repair",
        "Learning",
        "generic `/chat` executor",
        "M95B: NOT AUTHORIZED.",
        "COMPLETE LOCALLY / PENDING PM REVIEW",
    ):
        assert marker in text

    source = Path(__file__).read_text(encoding="utf-8")
    for forbidden in (
        "Test" + "Client",
        "sub" + "process",
        "handle_observation_" + "intake(",
        "execute_approved_" + "restricted_read(",
        ".write_" + "text(",
        "import " + "aether",
    ):
        assert forbidden not in source
