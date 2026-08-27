"""Static/document lock for the M116A trust-root decision."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / (
    "docs/architecture/"
    "MILESTONE_116A_TRUTHFUL_HUMAN_AUTHORITY_TRUST_ROOT_DECISION.md"
)


def _text() -> str:
    return " ".join(RECORD.read_text(encoding="utf-8").split())


def _assert_required(text: str, *markers: str) -> None:
    for marker in markers:
        assert marker in text, marker


def test_m116a_locks_negative_trust_root_and_deployment_decision():
    text = _text()
    _assert_required(
        text,
        "STRICT READ-ONLY DISCOVERY / TRUST-ROOT AND DEPLOYMENT DECISION / DESIGN-RECORD-ONLY",
        "SELECTED_TRUST_ROOT_MODEL:",
        "TRUST_ROOT_MODEL_K_NO_TRUTHFUL_SOURCE_CURRENTLY_AVAILABLE",
        "SELECTED_DEPLOYMENT_PROFILE:",
        "DEPLOYMENT_PROFILE_E_NOT_PROVEN",
        "OBSERVED_INTERFACE_CONTAINMENT:",
        "LOOPBACK_UNAUTHENTICATED_PROCESS",
        "LOOPBACK_BINDING_IS_AUTHENTICATION:",
        "CURRENT_TRUST_ROOT_STATE:",
        "NO_AUTHENTICATED_OWNER_SOURCE_EXISTS",
        "TRUST_ROOT_EXISTS_CURRENTLY: NO",
        "TRUTHFUL_HUMAN_AUTHORITY_CURRENTLY_PROVEN: NO",
        "SOURCE_AUTHENTICATION_PROVEN:",
        "REAL_HUMAN_AUTHORITY_SOURCE_PROVEN:",
        "DIRECT_GOAL_ACCEPTANCE_PROVEN:",
        "TRUST_ROOT_MATURITY: TR0_NO_TRUTHFUL_TRUST_ROOT",
        "HUMAN_AUTHORITY_MATURITY:",
        "HA1_REQUIRED_FIELDS_IDENTIFIED_BUT_SEMANTICS_INCOMPLETE",
        "HA2_PROVEN: NO",
        "GOAL_INTAKE_MATURITY:",
        "GI2_CANONICAL_OWNER_PROVEN_ENTRY_CONTRACT_INCOMPLETE",
        "MINIMALITY_DECISION: MINIMALITY_NOT_PROVEN",
        "BUILD_READINESS: BUILD_NOT_JUSTIFIED",
        "PRINCIPAL_DECISION:",
        "K_NO_TRUTHFUL_OWNER_AUTHORITY_SOURCE_OR_DEPLOYMENT_PROFILE_CURRENTLY_PROVEN",
        "No M116A PM approval, finalization, commit, tag, push, M116B, M117, or successor",
    )


def test_m116a_evaluates_all_trust_root_candidates_and_profiles():
    text = _text()
    _assert_required(
        text,
        "TRUST_ROOT_MODEL_A_PROCESS_LOCAL_CALLER_CONVENTION",
        "TRUST_ROOT_MODEL_B_OPERATING_SYSTEM_USER_AND_LOCAL_IPC_PEER_IDENTITY",
        "TRUST_ROOT_MODEL_C_OWNER_CONFIGURED_LOCAL_SECRET_OR_TOKEN",
        "TRUST_ROOT_MODEL_D_AUTHENTICATED_LOCAL_UI_SESSION",
        "TRUST_ROOT_MODEL_E_AUTHENTICATED_API_IDENTITY",
        "TRUST_ROOT_MODEL_F_SIGNED_EXTERNAL_AUTHORITY_EVENT",
        "TRUST_ROOT_MODEL_G_EXISTING_APPROVAL_UI_OR_APPROVAL_RECORD",
        "TRUST_ROOT_MODEL_H_REVERSE_PROXY_ASSERTED_IDENTITY",
        "TRUST_ROOT_MODEL_I_PHYSICAL_LOCAL_CONSOLE_OR_TTY",
        "TRUST_ROOT_MODEL_J_HYBRID_BOOTSTRAP_AND_AUTHENTICATED_CHANNEL",
        "TRUST_ROOT_MODEL_K_NO_TRUTHFUL_SOURCE_CURRENTLY_AVAILABLE",
        "DEPLOYMENT_PROFILE_A_SINGLE_OWNER_LOCAL_MACHINE",
        "DEPLOYMENT_PROFILE_B_SINGLE_OWNER_LOCAL_NETWORK",
        "DEPLOYMENT_PROFILE_C_REMOTE_SINGLE_OWNER",
        "DEPLOYMENT_PROFILE_D_MULTI_USER_REMOTE",
        "DEPLOYMENT_PROFILE_E_NOT_PROVEN",
        "CURRENTLY_EXISTS",
        "TARGET_CANDIDATE",
        "REJECTED",
        "NOT_PROVEN",
        "No target implementation model is selected",
    )


def test_m116a_rejects_existing_substitutes_for_human_authority():
    text = _text()
    _assert_required(
        text,
        "Aether self-integrity is not Human Authority",
        "Action authorization cannot be reused as Goal authority",
        "Loopback is a containment fact, not authentication",
        "TYPED_INTERNAL_CALLER_CONTRACT != HUMAN_AUTHORITY",
        "SOURCE_AUTHENTICATION != INTENT_INTERPRETATION",
        "GOAL_ACCEPTANCE_NEVER_AUTHORIZES_ACTION",
        "session_id",
        "caller-supplied metadata",
        "Working Memory",
        "AetherRuntime",
        "Core Governance",
        "no independently authenticated Human Authority source",
        "Source authentication remains separate from intent interpretation",
        "Goal acceptance",
        "Action",
        "Observation",
        "Verification",
        "Aether cannot appoint or replace its owner",
        "No generic identity registry",
        "No Generic Act",
        "CORE_DRIFT_DETECTED:",
        "NO",
    )
    forbidden = (
        "TRUST_ROOT_MODEL_K_NO_" + "TRUTHFUL_ROOT_CURRENTLY_PROVEN",
        "TR0_NO_TRUTHFUL_TRUST_ROOT_" + "CURRENTLY_PROVEN",
        "DEPLOYMENT_PROFILE_A_LOOPBACK_" + "UNAUTHENTICATED_PROCESS",
        "DEPLOYMENT_PROFILE_B_LOCAL_OS_BOUND_AUTHORITY_ADAPTER",
        "DEPLOYMENT_PROFILE_C_AUTHENTICATED_REMOTE_API",
        "DEPLOYMENT_PROFILE_D_SIGNED_EXTERNAL_AUTHORITY_PROVIDER",
        "DEPLOYMENT_PROFILE_E_MULTI_USER_REMOTE_SERVICE",
        "SELECTED_CURRENT_" + "DEPLOYMENT_PROFILE",
        "SELECTED_CURRENT_TRUST_ROOT_MODEL",
        "TRUST_ROOT_EXISTS_CURRENTLY: YES",
        "TRUTHFUL_HUMAN_AUTHORITY_CURRENTLY_PROVEN: YES",
        "HA2_PROVEN: YES",
        "TRUST_ROOT_MATURITY: TR3_",
        "TRUST_ROOT_MATURITY: TR4_",
        "TRUST_ROOT_MATURITY: TR5_",
        "BUILD_READINESS: BOUNDED_PROCESS_LOCAL_BUILD_JUSTIFIED",
        "BUILD_READINESS: BUILD_JUSTIFIED",
        "M116B: AUTHORIZED",
        "M117: AUTHORIZED",
        "Generic Act: IMPLEMENTED",
        "Generic Act: AUTHORIZED",
        "Production authentication: IMPLEMENTED",
        "trusted adapter: IMPLEMENTED",
    )
    for pattern in forbidden:
        assert not re.search(pattern, text), f"forbidden pattern found: {pattern}"


def test_m116a_locks_required_envelope_lifecycle_and_failure_semantics():
    text = _text()
    _assert_required(
        text,
        "owner/source identity",
        "authentication",
        "source-event identity",
        "source-event integrity",
        "exact raw instruction",
        "freshness",
        "replay protection",
        "trust-root generation",
        "revocation",
        "operation binding",
        "Goal/proposal/revision binding",
        "provenance",
        "Bootstrap",
        "Recovery",
        "Revocation",
        "owner-controlled source",
        "generation changes",
        "Any check fails -> reject before mutation",
        "VALIDATE_BEFORE_MUTATE_ONLY_ATOMICITY_NOT_PROVEN",
        "No current implementation is claimed",
    )


def test_m116a_locks_current_lifecycle_and_direct_instruction_decisions():
    text = _text()
    _assert_required(
        text,
        "CURRENT_TRUST_ROOT_STATE:",
        "NO_AUTHENTICATED_OWNER_SOURCE_EXISTS",
        "SELECTED_BOOTSTRAP_MODEL:",
        "NO_TRUTHFUL_OWNER_BOOTSTRAP_PROVEN",
        "SELECTED_RECOVERY_MODEL:",
        "NO_TRUTHFUL_OWNER_RECOVERY_PROVEN",
        "SELECTED_REVOCATION_MODEL:",
        "NO_TRUTHFUL_OWNER_REVOCATION_PROVEN",
        "SELECTED_SOURCE_EVENT_MODEL:",
        "NO_AUTHENTICATED_SOURCE_EVENT_PROVEN",
        "SELECTED_DIRECT_INSTRUCTION_MODEL:",
        "DIRECT_MODEL_E_NO_DIRECT_ACCEPTANCE_RULE_YET_PROVEN",
        "SELECTED_AUTHENTICATION_OWNER:",
        "NO_AUTHENTICATION_OWNER_PROVEN",
        "SELECTED_AUTHORITY_EVIDENCE_OWNER:",
        "NO_TRUTHFUL_AUTHORITY_EVIDENCE_OWNER_PROVEN",
        "SELECTED_GOAL_BINDING_OWNER:",
        "CORE_COORDINATION_GOAL_INTAKE",
        "DIRECT_GOAL_ACCEPTANCE_PROVEN:",
        "NO",
        "Explicit owner input",
        "Inferred or ambiguous intent",
        "Model confidence is not authority",
        "users should not need to provide procedures",
        "unnecessary confirmation ceremony",
        "No direct-acceptance rule is authorized now",
    )


def test_m116a_locks_current_ownership_and_scope_boundary():
    text = _text()
    _assert_required(
        text,
        "config/aether.yaml",
        "127.0.0.1",
        "api.port",
        "FastAPI",
        "aether/identity/guard.py",
        "Core Coordination/GoalIntake",
        "Approval queues",
        "No production module provides a Unix-socket identity",
        "No M116A PM approval",
        "PROGRESS.md",
        "production code",
        "existing tests",
        "dependencies",
        "routes",
        "APIs",
        "M116A is complete locally as a corrected design decision only",
        "No implementation milestone is started or authorized",
        "TR0_NO_TRUTHFUL_TRUST_ROOT",
        "TR1_TRUST_ROOT_REQUIREMENTS_IDENTIFIED",
        "TR2_BOUNDED_TRUST_ROOT_CONTRACT_PROVEN_DESIGN_ONLY",
        "TR3_BOUNDED_TRUST_ROOT_IMPLEMENTED_AND_TESTED",
        "TR4_LIVE_AUTHENTICATED_SOURCE_BOUND_TO_GOAL_INTAKE",
        "TR5_DURABLE_RECOVERABLE_OWNER_AUTHORITY",
        "deployment profile is not proven",
        "owner trust source is not selected",
        "bootstrap is not selected",
        "recovery is not selected",
        "revocation is not selected",
        "authenticated source-event ownership is not selected",
        "direct acceptance rule",
        "minimum evidence is not proven",
        "NEXT_FRONTIER:",
        "OWNER_CONTROLLED_AUTHORITY_SOURCE_AND_DEPLOYMENT_SELECTION",
        "NEXT_MILESTONE_TYPE:",
        "HUMAN/PROJECT-MANAGER TRUST-ROOT REQUIREMENTS DECISION",
        "OWNER_INPUT_REQUIRED_FOR_NEXT_FRONTIER:",
        "YES",
    )


def test_m116a_locks_predecessor_and_baseline():
    text = _text()
    _assert_required(
        text,
        "milestone-115A-human-authority-trust-root-proof-boundary",
        "1ccb578713bb01cef365899c17316208e6a4458e",
        "3267 passed",
        "M113A",
        "M114A",
        "M115A",
        "core/goal.py",
        "core/task_context.py",
        "core/coordination.py",
        "GoalIntake",
        "Core Coordination",
        "authority",
        "No M116B",
        "No M117",
        "commit",
        "tag",
        "push",
    )
