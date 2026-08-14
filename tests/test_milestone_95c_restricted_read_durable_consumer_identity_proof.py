"""Static consumer-proof locks for Milestone 95C."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "docs/architecture/MILESTONE_95C_RESTRICTED_READ_DURABLE_CONSUMER_IDENTITY_PROOF.md"


def _text() -> str:
    return RECORD.read_text(encoding="utf-8")


def test_title_classification_and_predecessor_authority_are_locked():
    text = _text()
    for marker in (
        "# Milestone 95C Restricted-Read Durable Consumer Identity & Use-Case Proof Boundary",
        "Classification: PLAN / CONSUMER-PROOF / OWNERSHIP DECISION ONLY",
        "Milestone 94: CLOSED / GIT-DURABLE / PM-ACCEPTED",
        "Milestone 95A: FINALIZED / GIT-DURABLE / PM-ACCEPTED",
        "M95B: FINALIZED / GIT-DURABLE / PM-ACCEPTED",
        "1f2dc79c6af732a46a59964514059c14e41b20da",
    ):
        assert marker in text


def test_consumer_question_and_qualification_standard_are_locked():
    text = _text()
    for marker in (
        "## 2. Exact M95C Question and Answer",
        "Does Aether currently have a REAL downstream consumer",
        "D_NO_DURABLE_CONSUMER_CURRENTLY_JUSTIFIED",
        "## 4. Consumer Qualification Standard",
        "why call-local Observation is insufficient",
        "exact fields consumed",
        "idempotency and replay requirements",
        "whether the architecture authorizes the relationship",
        "If a critical requirement is absent, the candidate is `NOT_PROVEN`.",
    ):
        assert marker in text


def test_complete_candidate_matrix_is_locked():
    text = _text()
    for marker in (
        "## 5. Candidate Consumer Matrix",
        "Observation Intake",
        "capability Verification",
        "Core Coordination / task continuation",
        "Report",
        "audit / trace",
        "ASC active task context",
        "Verification Aggregation",
        "Critic",
        "Repair",
        "Learning",
        "No matrix row is `PROVEN` as a durable restricted-read consumer.",
    ):
        assert marker in text


def test_observation_intake_decision_and_non_mapping_are_locked():
    text = _text()
    for marker in (
        "## 6. Observation Intake Audit",
        "no restricted-read caller",
        "E_COMPATIBILITY_REMAINS_UNPROVEN",
        "Observation Intake is `NOT_JUSTIFIED` as a current restricted-read caller",
        "VERIFIED_SUCCESS",
        "VERIFIED_PARTIAL",
        "DENIED",
        "NOT_FOUND",
        "CHANGED_DURING_READ",
        "INTERNAL_ERROR",
        "matched` or `mismatched",
        "does not rewrite Intake or synthesize `expected_value`",
    ):
        assert marker in text


def test_verification_call_local_distinction_is_locked():
    text = _text()
    for marker in (
        "## 7. Verification Consumer Audit",
        "Capability Verification is a current call-local consumer",
        "not Verification Aggregation",
        "stable durable Observation identity",
        "persistent payload",
        "persistent provenance envelope",
        "NOT_PROVEN",
        "Capability Verification is not Verification Aggregation.",
    ):
        assert marker in text


def test_task_continuation_report_audit_and_asc_gates_are_locked():
    text = _text()
    for marker in (
        "## 8. Core Coordination and Task Continuation Audit",
        "authoritative `task_id`",
        "`session_id` is not `task_id`",
        "## 9. Report, Audit, Trace, and Timeline Audit",
        "operational audit trail",
        "not read restricted-read Observation data.",
        "## 10. ASC, Memory, Aggregation, Critic, Repair, and Learning Audit",
        "ASC is the Authoritative Shared Cognitive Context framework",
        "not a database",
        "ASC runtime module reads a restricted-read Observation",
        "Verification Aggregation is not implemented",
    ):
        assert marker in text


def test_privacy_retention_access_replay_and_cleanup_requirements_are_locked():
    text = _text()
    for marker in (
        "Privacy contract",
        "Retention contract",
        "access and visibility requirements",
        "deletion requirements",
        "idempotency and replay requirements",
        "failure and cleanup semantics",
        "privacy-safe persistent payload: `NOT_SAFE_TO_PERSIST`",
        "Persistent restricted-read Observation: `NOT JUSTIFIED`",
        "future runtime persistence: `BLOCKED`",
    ):
        assert marker in text


def test_identity_non_aliasing_and_architecture_ownership_are_locked():
    text = _text()
    for marker in (
        "## 11. Identity and Ownership Truth",
        "approval_id != plan_step_id",
        "execution_attempt_id != collector_contract_id",
        "reader file-access id != Observation identity",
        "session_id != task_id",
        "capability_id != observation_id",
        "No placeholder identity satisfies consumer proof.",
        "## 12. Architecture Ownership",
        "Aether is one persistent digital intelligence",
        "Core Governance owns authority and governance",
        "Core Coordination owns orchestration and continuity",
        "ASC is the Authoritative Shared Cognitive Context framework",
        "Thinking proposes",
        "Governance authorizes",
        "Action executes within authorization",
        "Observation != Verification",
        "Repair != Learning",
    ):
        assert marker in text


def test_selected_outcome_runtime_consequence_and_current_truth_are_locked():
    text = _text()
    for marker in (
        "## 13. Selected Outcome and Runtime Consequence",
        "D_NO_DURABLE_CONSUMER_CURRENTLY_JUSTIFIED",
        "Runtime eligibility:",
        "`BLOCKED`",
        "Observation Intake caller: `NOT JUSTIFIED`",
        "provenance envelope runtime: `NOT JUSTIFIED`",
        "current call-local Observation: `REMAINS AUTHORITATIVE`",
        "current capability Verification: `REMAINS AUTHORITATIVE`",
        "current durable restricted-read consumer: `NONE`",
        "No runtime deficiency is implied",
    ):
        assert marker in text


def test_explicit_non_authorization_and_static_only_scope_are_locked():
    text = _text()
    for marker in (
        "## 14. Explicit Non-Authorization",
        "runtime provenance envelope implementation",
        "Observation Intake caller",
        "Observation Record creation or persistence",
        "Verification Aggregation",
        "Critic, Repair, or Learning",
        "second capability",
        "retry or background execution",
        "consumer integration",
        "M95D",
        "Git lifecycle",
        "M95C status during Build: COMPLETE LOCALLY / PENDING PM REVIEW.",
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
