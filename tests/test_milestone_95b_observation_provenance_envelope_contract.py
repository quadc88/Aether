"""Static contract locks for the Milestone 95B provenance envelope foundation."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "docs/architecture/MILESTONE_95B_MINIMAL_OBSERVATION_PROVENANCE_ENVELOPE_CONTRACT.md"


def _text() -> str:
    return RECORD.read_text(encoding="utf-8")


def test_title_scope_and_durable_95a_authority_are_locked():
    text = _text()
    for marker in (
        "# Milestone 95B Minimal Observation Provenance Envelope Contract Foundation",
        "Classification: PLAN / CONTRACT / SOURCE-OWNERSHIP BOUNDARY ONLY",
        "Milestone 94 is CLOSED / GIT-DURABLE / PM-ACCEPTED",
        "Milestone 95A is FINALIZED / GIT-DURABLE / PM-ACCEPTED",
        "7dd77c7aff80aa2f30e25361e74bc73b51148ebc",
        "M95B is authorized for Plan / Contract / Source-Ownership Boundary only",
        "M95C is NOT AUTHORIZED",
    ):
        assert marker in text


def test_identity_separation_and_non_aliasing_are_locked():
    text = _text()
    for marker in (
        "task_id / task context identity",
        "plan_id",
        "plan_step_id",
        "collector_contract_id",
        "approval_id",
        "execution_attempt_id",
        "action_id",
        "capability_id",
        "observation_id",
        "verification_id / verification relationship",
        "evidence_item_id",
        "consumer_id",
        "session_id",
        "approval_id != plan_step_id",
        "execution_attempt_id != collector_contract_id",
        "file-access id != Action identity",
        "session_id != task_id",
        "capability_id != collector_contract_id",
        "capability_id != observation_id",
        "execution_attempt_id != observation_id",
        "approval_id != observation_id",
    ):
        assert marker in text


def test_field_ownership_matrix_and_missing_owner_rule_are_locked():
    text = _text()
    for marker in (
        "## 5. Envelope Field Ownership Matrix",
        "envelope_version",
        "task_binding",
        "action_identity",
        "target_identity",
        "observation_identity",
        "observation_payload_reference",
        "capability_verification",
        "verification_relationship",
        "expectation_contract",
        "privacy_profile",
        "retention_profile",
        "consumer_identity",
        "evidence_item_identity",
        "provenance_created_at",
        "OWNER_NOT_YET_DEFINED",
        "A future required slot is not a",
    ):
        assert marker in text


def test_action_attempt_provenance_binding_is_locked():
    text = _text()
    for marker in (
        "## 7. Action-Attempt Binding",
        "governed capability request",
        "Approval records prerequisite human-authority state",
        "Core Governance authorizes a fresh execution attempt",
        "Core Coordination claims the approval",
        "The Action executes within the authorized scope",
        "Observation represents facts about that result",
        "Capability Verification evaluates",
        "Approval authorizes prerequisite state. It is not Action identity.",
    ):
        assert marker in text


def test_observation_identity_options_and_contract_decision_are_locked():
    text = _text()
    for marker in (
        "## 8. Observation Identity Options",
        "Option A: producer-time identity",
        "Option B: durable-admission identity",
        "producer-time stable identity is preferred",
        "Neither option is implemented by M95B",
        "reader file-access id must not become `observation_id`",
        "`execution_attempt_id` must not become `observation_id`",
        "`approval_id` must not become `observation_id`",
    ):
        assert marker in text


def test_expectation_models_and_intake_non_mapping_are_locked():
    text = _text()
    for marker in (
        "## 9. Expectation Contract",
        "A. predeclared equality expectation",
        "B. policy/invariant expectation",
        "C. capability-specific Verification expectation",
        "D. no-applicable-expectation declaration",
        "CURRENT_INTAKE_EXPECTATION_MODEL_INCOMPATIBLE",
        "It must never derive `expected_value`",
        "VERIFIED_SUCCESS",
        "VERIFIED_PARTIAL",
        "DENIED",
        "NOT_FOUND",
        "CHANGED_DURING_READ",
        "INTERNAL_ERROR",
        "They must not be mapped to `matched` or `mismatched`.",
        "E_COMPATIBILITY_REMAINS_UNPROVEN",
    ):
        assert marker in text


def test_capability_verification_relationship_is_separate_from_aggregation():
    text = _text()
    for marker in (
        "## 10. Verification Relationship",
        "verification producer identity",
        "verification subject",
        "observation_identity",
        "The capability verifier remains a call-local consumer",
        "The envelope is not",
        "No aggregation",
        "Critic trigger",
        "Repair trigger",
        "Learning trigger",
    ):
        assert marker in text


def test_privacy_payload_direction_and_persistence_block_are_locked():
    text = _text()
    for marker in (
        "## 11. Privacy Envelope and Payload Direction",
        "Raw content",
        "Redacted content",
        "Digest-only",
        "Metadata-only",
        "Structured evidence reference",
        "D_METADATA_PLUS_STRUCTURED_EVIDENCE_REFERENCE",
        "secret exposure",
        "normalized-path exposure",
        "partial-content leakage",
        "changing-file/TOCTOU semantics",
        "retention",
        "deletion",
        "visibility",
        "access-control ownership",
        "NOT_CURRENTLY_PROVABLE",
        "NOT_SAFE_TO_PERSIST",
        "No persistence is authorized in M95B",
    ):
        assert marker in text


def test_consumer_proof_and_runtime_eligibility_gates_are_locked():
    text = _text()
    for marker in (
        "## 12. Consumer Identity Gate",
        "consumer_identity",
        "Current restricted-read durable consumer: `NONE`.",
        "real and proven",
        "purpose",
        "access rights",
        "retention need",
        "## 13. Runtime Eligibility Gates",
        "plan-step owner",
        "collector-contract owner",
        "stable Observation identity",
        "idempotency and replay behavior",
        "persistence transaction, failure, cleanup",
        "Runtime bridge,",
    ):
        assert marker in text


def test_no_runtime_or_later_loop_shortcut_is_locked():
    text = _text()
    for marker in (
        "## 16. Explicit Non-Authorization",
        "runtime envelope implementation",
        "Observation Intake caller",
        "persistent Observation Record",
        "Verification Aggregation",
        "Critic, Repair, or Learning",
        "second capability",
        "retry or background execution",
        "M95C",
        "M95B status during Build: COMPLETE LOCALLY / PENDING PM REVIEW.",
        "Observation != Verification",
        "Verification != Aggregation",
        "Aggregation != Critic",
        "Critic != Repair",
        "Repair != Learning",
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
        "http" + "x",
        "re" + "quests",
            "sock" + "et",
    ):
        assert forbidden not in source
