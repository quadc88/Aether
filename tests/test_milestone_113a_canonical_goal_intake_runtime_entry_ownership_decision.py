"""Static/document lock for the M113A Goal-intake ownership decision."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / (
    "docs/architecture/"
    "MILESTONE_113A_CANONICAL_GOAL_INTAKE_RUNTIME_ENTRY_OWNERSHIP_DECISION.md"
)


def _text() -> str:
    return RECORD.read_text(encoding="utf-8")


def test_m113a_locks_models_decision_transport_and_maturity():
    text = " ".join(_text().split())
    required = (
        "# Milestone 113A Canonical Goal-Intake Runtime-Entry Ownership Decision",
        "STRICT READ-ONLY AUTHORITY / RUNTIME-ENTRY CONTRACT DECISION",
        "MODEL_A_CHAT_DIRECTLY_OWNS_AND_ACCEPTS_CANONICAL_GOALS",
        "MODEL_B_WORKING_MEMORY_GOAL_IS_PROMOTED_TO_CANONICAL_GOAL",
        "MODEL_C_AETHERRUNTIME_OWNS_CANONICAL_GOAL_INTAKE",
        "MODEL_D_CORE_COORDINATION_OWNS_INTERFACE_AGNOSTIC_GOAL_INTAKE",
        "MODEL_E_EXPLICIT_GOAL_ENTRY_ROUTE_DELEGATES_TO_CORE_COORDINATION",
        "MODEL_F_CHAT_MAY_PROPOSE_BUT_NOT_ACCEPT_A_GOAL",
        "MODEL_G_NO_GOAL_INTAKE_BUILD_CURRENTLY_JUSTIFIED",
        "MODEL_H_EVIDENCE_INSUFFICIENT",
        "MODEL_D_CORE_COORDINATION_OWNS_INTERFACE_AGNOSTIC_GOAL_INTAKE",
        "MODEL_E_EXPLICIT_GOAL_ENTRY_ROUTE_DELEGATES_TO_CORE_COORDINATION",
        "D_CORE_COORDINATION_OWNS_GOAL_INTAKE_BUT_LIVE_ENTRY_CONTRACT_INCOMPLETE",
        "GI0_NO_CANONICAL_GOAL_INTAKE_OWNER",
        "GI1_LEGACY_OR_NONAUTHORITATIVE_INPUT_ONLY",
        "GI2_CANONICAL_OWNER_PROVEN_ENTRY_CONTRACT_INCOMPLETE",
        "GI3_BOUNDED_CANONICAL_GOAL_INTAKE_CONTRACT_PROVEN",
        "GI4_DURABLE_CANONICAL_GOAL_INTAKE",
        "Future Build: NOT JUSTIFIED",
        "Next frontier:",
        "TYPED_HUMAN_AUTHORITY_AND_EXPLICIT_GOAL_OPERATION_CONTRACT",
        "Next milestone type:",
        "AUTHORITY / GOAL-INTAKE CONTRACT PROOF",
        "Next authorized action: HUMAN/PROJECT-MANAGER M113A GOAL-INTAKE OWNERSHIP REVIEW",
    )
    for marker in required:
        assert marker in text, marker


def test_m113a_locks_input_distinction_and_proposal_acceptance_boundary():
    text = " ".join(_text().split())
    required = (
        "CONVERSATION",
        "QUESTION",
        "INFORMATION REQUEST",
        "STATUS INQUIRY",
        "REFERENCE TO AN EXISTING GOAL OR TASK",
        "CONTINUATION OF AN EXISTING GOAL",
        "PAUSE REQUEST",
        "CANCELLATION REQUEST",
        "CORRECTION OF AN EXISTING GOAL",
        "CLARIFICATION RESPONSE",
        "PROPOSED NEW GOAL",
        "EXPLICIT GOAL ACCEPTANCE",
        "ACTION AUTHORIZATION",
        "PROPOSE GOAL and ACCEPT GOAL: SEPARATE OPERATIONS",
        "Goal proposal contract",
        "Goal acceptance contract",
        "exact proposed Goal ID",
        "typed Human Authority envelope",
        "A combined operation is not part of the current contract",
        "PROPOSE_AND_ACCEPT_GOAL",
        "No general natural-language classifier is designed or authorized",
    )
    for marker in required:
        assert marker in text, marker


def test_m113a_locks_ownership_and_non_authority_boundaries():
    text = " ".join(_text().split())
    required = (
        "Core Coordination/GoalIntake",
        "GoalIntake stores the canonical field",
        "Core Coordination owns Task and first authoritative TaskContext",
        "Core Coordination owns Goal/Task/TaskContext",
        "Human Authority is the source",
        "Human Authority must supply valid evidence",
        "AetherRuntime may hold the process-local CoreCoordination instance",
        "AetherRuntime must not thereby own",
        "Working Memory `current_goal` string remains legacy/non-authoritative",
        "AetherOS provides clocks, processes, storage mechanisms",
        "Action approval is capability-specific",
        "Action approval records cannot serve as Goal authority",
        "Thinking may eventually propose interpretation",
        "ThinkingProposal and Goal intake remain separate",
        "Plan materialization remains separate from Action authorization",
        "authority_reference",
        "raw string is too weak for a live contract",
        "Existing Action approval records cannot serve as Goal authority",
        "No interface, runtime, memory object, or Action workflow owns every category",
    )
    for marker in required:
        assert marker in text, marker


def test_m113a_locks_build_gate_core_drift_and_forbidden_scope():
    text = " ".join(_text().split())
    required = (
        "Exact transport relationship",
        "Exact Human Authority source",
        "Exact minimal production write set",
        "No Action-authority escalation",
        "No ThinkingProposal producer dependency",
        "No persistence dependency",
        "No Generic Act dependency",
        "1. Aether remains one persistent mind: YES",
        "2. Goal remains above procedure: YES",
        "3. Context remains Core Coordination responsibility: YES",
        "4. Human Authority remains required for Goal acceptance: YES",
        "5. Conversation and Goal creation remain distinct: YES",
        "6. Goal proposal and Goal acceptance remain truthfully distinct: YES",
        "7. /chat is prevented from becoming a competing authority: YES",
        "8. Working Memory is prevented from becoming Goal authority: YES",
        "9. AetherRuntime is prevented from becoming cognitive authority: YES",
        "10. AetherOS remains mechanism/environment: YES",
        "11. Action approval and Goal authority remain separate: YES",
        "12. ThinkingProposal and Goal intake remain separate: YES",
        "13. Plan materialization remains separate from Action authorization: YES",
        "14. Observe and Verify remain required for outcome completion: YES",
        "15. Commitment runtime, persistence, scheduler, capability discovery, delegation, and Generic Act remain out of scope: YES",
        "Production implementation: NOT CLAIMED",
        "No Goal API is selected or implemented",
        "No `/chat` route changes",
        "M113B: NOT AUTHORIZED",
        "M114: NOT AUTHORIZED",
        "commit: NONE",
        "tag: NONE",
        "push: NONE",
        "Generic Act: NOT_IMPLEMENTED / NOT_AUTHORIZED / NOT_GRANTED",
        "Patch security: PAUSED",
    )
    for marker in required:
        assert marker in text, marker

    forbidden = (
        "Future Build: JUSTIFIED FOR PM REVIEW",
        "Production implementation: IMPLEMENTED",
        "Goal API: IMPLEMENTED",
        "M113B: AUTHORIZED",
        "M114: AUTHORIZED",
        "Generic Act: IMPLEMENTED",
    )
    for marker in forbidden:
        assert marker not in text, marker
