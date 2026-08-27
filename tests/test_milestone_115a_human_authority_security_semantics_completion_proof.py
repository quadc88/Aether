"""Static/document lock for the M115A security-semantics correction."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / (
    "docs/architecture/"
    "MILESTONE_115A_HUMAN_AUTHORITY_SECURITY_SEMANTICS_COMPLETION_PROOF.md"
)


def _text() -> str:
    return " ".join(RECORD.read_text(encoding="utf-8").split())


def _assert_required(text: str, *markers: str) -> None:
    for marker in markers:
        assert marker in text, marker


def test_m115a_locks_corrected_models_and_maturity():
    text = _text()
    _assert_required(
        text,
        "STRICT READ-ONLY DISCOVERY / AUTHORITY-CONTRACT SEMANTIC COMPLETION PROOF / DESIGN-RECORD-ONLY",
        "HA_MODEL_D_TYPED_SCOPE_BOUND_NON_REPLAYABLE_HUMAN_AUTHORITY_ENVELOPE",
        "HA_MODEL_F_NO_TRUTHFUL_TYPED_HUMAN_AUTHORITY_CONTRACT_CURRENTLY_PROVEN",
        "HA1_REQUIRED_FIELDS_IDENTIFIED_BUT_SEMANTICS_INCOMPLETE",
        "HA2_PROVEN: NO",
        "HUMAN_AUTHORITY_MATURITY: HA1_REQUIRED_FIELDS_IDENTIFIED_BUT_SEMANTICS_INCOMPLETE",
        "GI2_CANONICAL_OWNER_PROVEN_ENTRY_CONTRACT_INCOMPLETE",
        "SELECTED_THREAT_MODEL: THREAT_MODEL_F_NO_TRUTHFUL_TRUST_BOUNDARY_CURRENTLY_PROVEN",
        "SELECTED_ISSUER_MODEL: ISSUER_MODEL_H_NO_TRUTHFUL_ISSUER_CURRENTLY_PROVEN",
        "SELECTED_AUTHORITY_SCOPE: GOAL_OPERATION_BOUNDARY_PROPOSE_ACCEPT_GET_STATUS_ONLY",
        "SELECTED_OPERATION_SUBSET: CANDIDATE_PROCESS_LOCAL_SUBSET_PROPOSE_ACCEPT_GET_STATUS",
        "SELECTED_REPLAY_MODEL: PROCESS_LOCAL_REPLAY_SHAPE_IDENTIFIED_ATOMICITY_INCOMPLETE",
        "SELECTED_REVOCATION_MODEL: NO_TRUTHFUL_REVOCATION_OWNER_CURRENTLY_PROVEN",
        "SELECTED_DIGEST_MODEL: CANONICAL_OPERATION_CONTENT_DIGEST_SHAPE_IDENTIFIED_SEMANTICS_INCOMPLETE",
        "SELECTED_TIME_MODEL: PROCESS_LOCAL_WALL_CLOCK_WITH_FIVE_MINUTE_MAX_VALIDITY",
        "SELECTED_EVIDENCE_MODEL: PROCESS_LOCAL_EVIDENCE_SHAPE_NOT_INDEPENDENTLY_PROVEN",
        "SELECTED_ATOMICITY_MODEL: VALIDATE_BEFORE_MUTATE_ONLY_ATOMICITY_NOT_PROVEN",
        "PRINCIPAL_DECISION: F_NO_TRUTHFUL_HUMAN_AUTHORITY_TRUST_ROOT_AND_SECURITY_CONTRACT_INCOMPLETE",
        "MINIMALITY_DECISION: MINIMALITY_NOT_PROVEN",
        "BUILD_READINESS: BUILD_NOT_JUSTIFIED",
        "NEXT_FRONTIER: TRUTHFUL_HUMAN_AUTHORITY_TRUST_ROOT_DECISION",
        "NEXT_MILESTONE_TYPE: AUTHORITY-SOURCE / TRUST-BOUNDARY DECISION",
    )


def test_m115a_rejects_internal_caller_and_ha2_promotion():
    text = _text()
    _assert_required(
        text,
        "TYPED_INTERNAL_CALLER_CONTRACT != HUMAN_AUTHORITY",
        "TYPED_INTERNAL_CALLER_CONTRACT",
        "HUMAN_AUTHORITY:",
        "HUMAN_AUTHORITY_TARGET:",
        "actor_truthfulness: NOT_PROVEN",
        "issuer_authenticity: NOT_PROVEN",
        "actor_issuer_binding: NOT_PROVEN",
        "source_message_independence: NOT_PROVEN",
        "evidence_source_independence: NOT_PROVEN",
        "ISSUER_MODEL_E_TRUSTED_LOCAL_HUMAN_AUTHORITY_ADAPTER (FUTURE CANDIDATE)",
        "ISSUER_MODEL_H_NO_TRUTHFUL_ISSUER_CURRENTLY_PROVEN (CURRENT)",
        "THREAT_MODEL_B_SINGLE_USER_LOCAL_PROCESS_WITH_EXPLICIT_TRUSTED_CALLER (FUTURE CANDIDATE)",
        "THREAT_MODEL_F_NO_TRUTHFUL_TRUST_BOUNDARY_CURRENTLY_PROVEN (CURRENT)",
        "Goal acceptance never creates Action authority",
        "GOAL_ACCEPTANCE_NEVER_AUTHORIZES_ACTION",
    )
    forbidden = (
        "HUMAN_AUTHORITY_MATURITY: HA2_",
        "HUMAN_AUTHORITY_MATURITY: HA3_",
        "HUMAN_AUTHORITY_MATURITY: HA4_",
        "HUMAN_AUTHORITY_MATURITY: HA5_",
        "BUILD_READINESS: BOUNDED_PROCESS_LOCAL_BUILD_JUSTIFIED_FOR_PM_REVIEW",
        "MINIMALITY_DECISION: MINIMALITY_PROVEN",
        "SELECTED_THREAT_MODEL: THREAT_MODEL_B_",
        "SELECTED_ISSUER_MODEL: ISSUER_MODEL_E_",
        "HA2_PROVEN: YES",
        "Generic Act: IMPLEMENTED",
        "Generic Act: AUTHORIZED",
        "M115B: AUTHORIZED",
        "M116: AUTHORIZED",
    )
    for pattern in forbidden:
        assert not re.search(pattern, text), f"forbidden pattern found: {pattern}"


def test_m115a_locks_candidate_envelope_and_unresolved_security_semantics():
    text = _text()
    _assert_required(
        text,
        "envelope_version",
        "authority_id",
        "authority_kind",
        "actor_id",
        "issuer_id",
        "source_interface",
        "source_message_id",
        "request_id",
        "operation",
        "goal_id",
        "expected_goal_revision",
        "operation_content_digest",
        "authority_scope",
        "issued_at",
        "valid_from",
        "expires_at",
        "nonce",
        "evidence_reference",
        "KEEP CANDIDATE",
        "CONDITIONAL",
        "REMOVE",
        "DEFER",
        "MINIMALITY_NOT_PROVEN",
        "session_id",
        "reason",
        "proposal_digest",
        "constraint_digest",
        "operation_payload_digest",
        "authority_generation",
        "parent_authority_id",
        "revocation_status",
        "digest canonicalization",
        "compatibility are unresolved",
    )


def test_m115a_locks_failure_closed_boundaries_and_core_drift():
    text = _text()
    _assert_required(
        text,
        "THINKING_PROPOSAL != GOAL_ACCEPTANCE",
        "GOAL_ACCEPTANCE != ACTION_AUTHORIZATION",
        "GOVERNANCE_EVALUATION != EXECUTION_AUTHORIZATION",
        "GOAL/TASK/TASKCONTEXT_OWNERSHIP != ACTION_PERMISSION",
        "TRANSPORT != COGNITIVE_AUTHORITY",
        "MEMORY != GOAL_AUTHORITY",
        "RUNTIME_PROCESS_LIFETIME != COGNITIVE_AUTHORITY",
        "A_REQUEST_TO_COMPLETE_IS_NOT_PROOF_OF_COMPLETION",
        "Observation and Verification remain separate",
        "VALIDATION_SEQUENCE:",
        "Any check fails -> reject before mutation",
        "PROCESS_LOCAL_REPLAY_SHAPE_IDENTIFIED_ATOMICITY_INCOMPLETE",
        "VALIDATE_BEFORE_MUTATE_ONLY_ATOMICITY_NOT_PROVEN",
        "CANONICAL_OPERATION_CONTENT_DIGEST_SHAPE_IDENTIFIED_SEMANTICS_INCOMPLETE",
        "missing provenance",
        "persistence/restoration assumed",
        "partial mutation before validation failure",
        "CORE_DRIFT_RISK: INTERNAL_CALLER_MISLABELED_AS_HUMAN_AUTHORITY_DETECTED_AND_REJECTED",
        "CORE_DRIFT_DETECTED_IN_CORRECTED_DECISION: NO",
        "CORE_DRIFT_DETECTED: NO",
        "Production implementation: NOT CLAIMED",
        "Live typed authority: NOT PROVEN (design-only)",
        "Live canonical Goal entry: NOT PROVEN",
        "M115B: NOT AUTHORIZED",
        "M116: NOT AUTHORIZED",
        "commit: NONE",
        "tag: NONE",
        "push: NONE",
        "No M115A PM approval, finalization, commit, tag, push, M115B, M116, or successor",
        "The Build must NOT include",
        "/chat wiring",
        "persistence or durable restoration",
        "Generic Act integration",
        "Action authority expansion",
    )


def test_m115a_locks_predecessor_and_baseline():
    text = _text()
    _assert_required(
        text,
        "milestone-114A-typed-human-authority-goal-operation-contract-proof",
        "0cf1ee3d4c8fb6d7a3a5c6f9d5a8168f2df25f8b",
        "3262 passed",
        "M114A",
        "M113A",
        "M96",
        "core/goal.py",
        "core/task_context.py",
        "core/coordination.py",
        "GoalIntake",
        "CoreCoordination",
        "authority_reference",
        "approval_*",
    )
