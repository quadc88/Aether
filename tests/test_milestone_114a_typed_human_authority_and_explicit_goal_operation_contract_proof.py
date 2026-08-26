"""Static/document lock for the M114A authority-contract proof."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / (
    "docs/architecture/"
    "MILESTONE_114A_TYPED_HUMAN_AUTHORITY_AND_EXPLICIT_GOAL_OPERATION_CONTRACT_PROOF.md"
)


def _text() -> str:
    return RECORD.read_text(encoding="utf-8")


def test_m114a_locks_selected_models_and_maturity():
    text = " ".join(_text().split())
    required = (
        "STRICT READ-ONLY DISCOVERY / AUTHORITY-CONTRACT PROOF / DESIGN-RECORD-ONLY",
        "HA_MODEL_A_RAW_STRING_REFERENCE_IS_SUFFICIENT",
        "HA_MODEL_B_ACTION_APPROVAL_IS_REUSED_AS_GOAL_AUTHORITY",
        "HA_MODEL_C_SESSION_OR_TRANSPORT_IDENTITY_IMPLIES_AUTHORITY",
        "HA_MODEL_D_TYPED_SCOPE_BOUND_NON_REPLAYABLE_HUMAN_AUTHORITY_ENVELOPE",
        "HA_MODEL_E_EXISTING_CANONICAL_AUTHORITY_PRIMITIVE_CAN_BE_SAFELY_REUSED",
        "HA_MODEL_F_NO_TRUTHFUL_TYPED_HUMAN_AUTHORITY_CONTRACT_CURRENTLY_PROVEN",
        "INTERPRETATION_MODEL_A_TRANSPORT_CLASSIFIES_AND_OWNS_THE_OPERATION",
        "INTERPRETATION_MODEL_B_WORKING_MEMORY_CLASSIFIES_AND_PROMOTES_GOALS",
        "INTERPRETATION_MODEL_C_AETHERRUNTIME_CLASSIFIES_AND_ACCEPTS_GOALS",
        "INTERPRETATION_MODEL_D_THINKING_MAY_PROPOSE_A_TYPED_INTERPRETATION_BUT_CANNOT_ACCEPT",
        "INTERPRETATION_MODEL_E_CALLER_SUPPLIES_AN_EXPLICIT_OPERATION_WITHOUT_NATURAL_LANGUAGE_CLASSIFICATION",
        "INTERPRETATION_MODEL_F_NO_GENERAL_INTERPRETER_IS_REQUIRED_FOR_THE_FIRST_BOUNDED_ENTRY",
        "INTERPRETATION_MODEL_G_NO_TRUTHFUL_INTERPRETATION_OWNER_CURRENTLY_PROVEN",
        "GOAL_OPERATION_MODEL_A_EXPLICIT_DISCRIMINATED_VOCABULARY_WITH_SEPARATE_PROPOSAL_AND_ACCEPTANCE",
        "TRANSPORT_MODEL_C_ONE_DISCRIMINATED_TYPED_GOAL_OPERATION_ROUTE_DELEGATES_TO_CORE_COORDINATION",
        "TARGET_DESIGN_DIRECTION: HA_MODEL_D_TYPED_SCOPE_BOUND_NON_REPLAYABLE_HUMAN_AUTHORITY_ENVELOPE",
        "CURRENT_RUNTIME_STATE: HA_MODEL_F_NO_TRUTHFUL_TYPED_HUMAN_AUTHORITY_CONTRACT_CURRENTLY_PROVEN",
        "HA0_NO_TYPED_HUMAN_AUTHORITY_CONTRACT",
        "HA1_REQUIRED_FIELDS_IDENTIFIED_BUT_SEMANTICS_INCOMPLETE",
        "HA2_TYPED_SCOPE_AND_VALIDATION_CONTRACT_PROVEN_DESIGN_ONLY",
        "HA3_BOUNDED_PROCESS_LOCAL_TYPED_AUTHORITY_IMPLEMENTED_AND_TESTED",
        "HA4_LIVE_ENTRY_AUTHORITY_IMPLEMENTED_AND_TESTED",
        "HA5_DURABLE_RESTART_SAFE_AUTHORITY_IMPLEMENTED_AND_TESTED",
        "GI2_CANONICAL_OWNER_PROVEN_ENTRY_CONTRACT_INCOMPLETE",
        "CURRENT_DESIGN_MATURITY: HA1_REQUIRED_FIELDS_IDENTIFIED_BUT_SEMANTICS_INCOMPLETE",
        "HUMAN_AUTHORITY_MATURITY: HA1_REQUIRED_FIELDS_IDENTIFIED_BUT_SEMANTICS_INCOMPLETE",
        "HA2_NOT_PROVEN",
        "BUILD_NOT_JUSTIFIED",
        "D_TYPED_AUTHORITY_SHAPE_AND_GOAL_OPERATIONS_IDENTIFIED_SECURITY_SEMANTICS_INCOMPLETE",
        "MINIMALITY_DECISION: MINIMALITY_NOT_PROVEN",
        "DIGEST_CANONICALIZATION: NOT_PROVEN",
        "ISSUER_TRUST_SEMANTICS: INCOMPLETE",
        "ACTOR_ISSUER_BINDING: INCOMPLETE",
        "REVOCATION_SEMANTICS: INCOMPLETE",
        "REPLAY_SEMANTICS: INCOMPLETE",
        "HIGH_LEVEL_FAILURE_CLOSED_SEQUENCE_IDENTIFIED",
        "HUMAN_AUTHORITY_SECURITY_SEMANTICS_COMPLETION_PROOF",
        "AUTHORITY-CONTRACT SEMANTIC COMPLETION PROOF",
    )
    for marker in required:
        assert marker in text, marker


def test_m114a_locks_authority_envelope_and_operation_boundaries():
    text = " ".join(_text().split())
    required = (
        "THINKING_PROPOSAL != GOAL_ACCEPTANCE",
        "GOAL_ACCEPTANCE != ACTION_AUTHORIZATION",
        "GOVERNANCE_EVALUATION != EXECUTION_AUTHORIZATION",
        "GOAL/TASK/TASKCONTEXT_OWNERSHIP != ACTION_PERMISSION",
        "TRANSPORT != COGNITIVE_AUTHORITY",
        "MEMORY != GOAL_AUTHORITY",
        "RUNTIME_PROCESS_LIFETIME != COGNITIVE_AUTHORITY",
        "envelope_version",
        "authority_id",
        "authority_kind",
        "actor_id",
        "issuer_id",
        "source_interface",
        "source_message_id",
        "request_id",
        "operation_payload_digest",
        "proposal_digest",
        "authority_scope",
        "issued_at",
        "valid_from",
        "expires_at",
        "nonce",
        "authority_generation",
        "evidence_reference",
        "parent_authority_id",
        "revocation_status",
        "session_id",
        "reason",
        "PROPOSE_GOAL",
        "ACCEPT_GOAL",
        "REJECT_GOAL",
        "GET_GOAL_STATUS",
        "CONTINUE_GOAL",
        "PAUSE_GOAL",
        "REVISE_GOAL",
        "CANCEL_GOAL",
        "MARK_GOAL_COMPLETE",
        "ACTION_AUTHORIZATION",
        "SEPARATE_OPERATIONS_UNTIL_SEPARATE_COMBINED_OPERATION_PROOF",
        "GOAL_ACCEPTANCE_NEVER_AUTHORIZES_ACTION",
        "No natural-language classifier is required or authorized",
        "A_REQUEST_TO_COMPLETE_IS_NOT_PROOF_OF_COMPLETION",
        "Only `PROPOSE_GOAL`, `ACCEPT_GOAL`, and the process-local owner lookup",
        "future candidate operations, not live canonical operations",
        "no live transport yet",
    )
    for marker in required:
        assert marker in text, marker


def test_m114a_locks_failure_closed_compatibility_and_non_authority():
    text = " ".join(_text().split())
    required = (
        "missing Human Authority",
        "malformed authority",
        "expired authority",
        "revoked authority",
        "replayed authority",
        "reused request identity",
        "wrong operation scope",
        "wrong Goal identity",
        "stale Goal revision",
        "changed proposal after authority",
        "ambiguous referent",
        "conflicting candidate Goals",
        "unsupported operation",
        "invalid lifecycle transition",
        "unauthorized continuation",
        "unauthorized revision",
        "unauthorized cancellation",
        "premature completion",
        "transport assigning authority",
        "Working Memory promotion",
        "AetherRuntime claiming cognitive ownership",
        "Thinking or model self-acceptance",
        "Action approval as Goal acceptance",
        "Goal acceptance as Action authorization",
        "missing provenance",
        "persistence/restoration assumed",
        "partial mutation before validation failure",
        "HIGH_LEVEL_FAILURE_CLOSED_SEQUENCE_IDENTIFIED",
        "COMPATIBILITY_DECISION",
        "LEGACY_RAW_REFERENCE_PROCESS_LOCAL_ONLY_NO_SILENT_AUTHORITY_PROMOTION",
        "cannot be migrated into Goal authority",
        "no silent authority promotion",
        "feature-disabled default",
        "no partial accepted state",
        "No operation may infer another operation",
        "A_REQUEST_TO_COMPLETE_IS_NOT_PROOF_OF_COMPLETION",
        "Human Authority alone cannot prove completion",
        "Action success alone cannot prove Goal completion",
        "Verification evidence alone does not mutate Goal state",
    )
    for marker in required:
        assert marker in text, marker


def test_m114a_locks_core_drift_and_scope_freeze():
    text = " ".join(_text().split())
    required = (
        "Does Aether remain one persistent digital mind?",
        "Does Core Coordination/GoalIntake remain canonical owner?",
        "Does Human Authority remain external authority evidence rather than a second mind?",
        "Does any transport become cognitive authority?",
        "Does Working Memory become Goal authority?",
        "Does AetherRuntime become cognitive authority?",
        "Does AetherOS become cognitive authority?",
        "Can Thinking or a model accept its own proposal?",
        "Is Goal acceptance separated from Action authorization?",
        "Are capability executors kept outside cognitive ownership?",
        "Is Context still Aether's responsibility?",
        "Is Goal still above procedure?",
        "Does completion still require verified outcome evidence?",
        "Is Generic Act still unauthorized?",
        "Is production readiness being falsely claimed?",
        "Has M114A expanded into an authority registry or generic runtime?",
        "CORE_DRIFT_DETECTED: NO",
        "Production implementation: NOT CLAIMED",
        "Live typed authority: NOT PROVEN",
        "M114B: NOT AUTHORIZED",
        "M115: NOT AUTHORIZED",
        "commit: NONE",
        "tag: NONE",
        "push: NONE",
        "No M114A PM approval, finalization, commit, tag, push, M114B, M115, or successor",
    )
    for marker in required:
        assert marker in text, marker

    forbidden = (
        "HUMAN_AUTHORITY_MATURITY: HA3_BOUNDED_PROCESS_LOCAL_TYPED_AUTHORITY_IMPLEMENTED_AND_TESTED",
        "HUMAN_AUTHORITY_MATURITY: HA4_LIVE_ENTRY_AUTHORITY_IMPLEMENTED_AND_TESTED",
        "HUMAN_AUTHORITY_MATURITY: HA5_DURABLE_RESTART_SAFE_AUTHORITY_IMPLEMENTED_AND_TESTED",
        "Production implementation: IMPLEMENTED",
        "M114B: AUTHORIZED",
        "M115: AUTHORIZED",
        "GENERIC_ACT_AUTHORIZED: YES",
        "HUMAN_AUTHORITY_MATURITY: HA2_TYPED_SCOPE_AND_VALIDATION_CONTRACT_PROVEN_DESIGN_ONLY",
        "PRINCIPAL_DECISION: D_TYPED_AUTHORITY_AND_EXPLICIT_OPERATION_DESIGN_PROVEN_LIVE_ENTRY_NOT_PROVEN",
        "NEXT_FRONTIER: HUMAN_AUTHORITY_ISSUER_REVOCATION_AND_LIVE_OPERATION_VALIDATION_PROOF",
        "NEXT_MILESTONE_TYPE: AUTHORITY-CONTRACT IMPLEMENTATION-READINESS REVIEW",
    )
    for marker in forbidden:
        assert marker not in text, marker
