"""Static/document lock for the M112A runtime-entry proof boundary."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / (
    "docs/architecture/"
    "MILESTONE_112A_QUALIFYING_RUNTIME_ENTRY_AUTHORITATIVE_CONTEXT_HANDOFF_PROOF_BOUNDARY.md"
)


def _text() -> str:
    return RECORD.read_text(encoding="utf-8")


def test_m112a_selected_runtime_entry_model_is_locked():
    text = " ".join(_text().split())
    required = (
        "# Milestone 112A Qualifying Runtime Entry Authoritative Context Handoff Proof Boundary",
        "STRICT READ-ONLY CORE-ARCHITECTURE / RUNTIME-ENTRY / AUTHORITATIVE-CONTEXT-HANDOFF PROOF",
        "b808262f56ad9b393e0333199e84aeb66b1d382e",
        "MODEL_A_EXISTING_RUNTIME_ENTRY_ALREADY_PROVES_CANONICAL_HANDOFF",
        "MODEL_B_CANONICAL_CHAT_ENTRY_FUTURE_BOUNDARY_IS_QUALIFIED",
        "MODEL_C_EXISTING_CAPABILITY_WORKFLOW_FUTURE_BOUNDARY_IS_QUALIFIED",
        "MODEL_D_RUNTIME_SUPERVISOR_FUTURE_BOUNDARY_IS_QUALIFIED",
        "MODEL_E_NO_QUALIFYING_RUNTIME_ENTRY_CURRENTLY_PROVEN",
        "MODEL_F_EVIDENCE_INSUFFICIENT",
        "E_NO_QUALIFYING_RUNTIME_ENTRY_CURRENTLY_PROVEN",
        "LIVE RUNTIME ENTRIES: PRESENT",
        "RTE1_LIVE_NONCANONICAL_ENTRY",
        "QUALIFYING AUTHORITATIVE RUNTIME ENTRY: NOT PROVEN",
        "PROCESS-LOCAL CORE COORDINATION HANDOFF: PROVEN",
        "CANONICAL_GOAL_INTAKE_RUNTIME_ENTRY_OWNERSHIP_DECISION",
        "AUTHORITY / RUNTIME-ENTRY CONTRACT DECISION",
        "Future Build: NOT JUSTIFIED",
        "Generic Act: NOT_IMPLEMENTED / NOT_AUTHORIZED / NOT_GRANTED",
        "Patch security: PAUSED",
        "Next authorized action: HUMAN/PROJECT-MANAGER M112A CORRECTED RUNTIME-ENTRY PROOF REVIEW",
    )
    for marker in required:
        assert marker in text, marker


def test_m112a_locks_candidate_inventory_and_external_negative_boundaries():
    text = _text()
    required = (
        "RTE0_NO_RUNTIME_ENTRY",
        "RTE1_LIVE_NONCANONICAL_ENTRY",
        "RTE2_QUALIFYING_ENTRY_CANDIDATE_BOUNDARY",
        "RTE3_AUTHORITATIVE_RUNTIME_ENTRY_HANDOFF_PROVEN",
        "RTE4_DURABLE_AUTHORITATIVE_RUNTIME_ENTRY",
        "E1_LEGACY_ENTRY_CONTEXT_MISSING",
        "E2_NONAUTHORITATIVE_MEMORY_ENTRY",
        "E3_ACTION_WORKFLOW_SEPARATE_AUTHORITY",
        "E4_LIFECYCLE_ENTRY_NO_COGNITIVE_HANDOFF",
        "E5_NO_QUALIFYING_ASYNC_ENTRY",
        "E6_SEAM_WITHOUT_RUNTIME_CALLER",
        "POST /chat",
        "POST /memory/working/goal",
        "Action capability routes/services",
        "Runtime awakening/lifecycle",
        "Workers, schedulers, queues, event handlers",
        "CoreCoordination methods",
        "Production ThinkingProposal producer: ABSENT",
        "External canonical runtime consumer: ABSENT",
        "Durable/async canonical consumer: ABSENT",
        "Selected PlanStep external runtime consumer: ABSENT",
        "FABRICATION REQUIRED FOR CURRENT LIVE PRODUCER ATTEMPT: YES",
        "RAW REQUEST TRANSPORT: AVAILABLE",
        "CANONICAL GOAL INTAKE AT LIVE ENTRY: ABSENT",
        "AUTHORITATIVE TASKCONTEXT CREATION: PRESENT PROCESS-LOCALLY IN CORE COORDINATION",
        "AUTHORITATIVE TASKCONTEXT SELECTION FROM LIVE ENTRY: ABSENT",
        "CONTEXT REVISION HANDOFF FROM LIVE ENTRY: ABSENT",
        "REQUEST PROVENANCE: PARTIAL / NONCANONICAL",
        "COGNITIVE CONTEXT PROVENANCE: INCOMPLETE AT LIVE ENTRY",
        "RESTART RESTORATION: ABSENT",
        "DURABLE CANONICAL CONTEXT: ABSENT",
        "THINKINGPROPOSAL INPUT READINESS: INSUFFICIENT",
        "BUILD READINESS: NOT JUSTIFIED",
        "No live entry completes the authoritative sequence.",
        "No canonical worker, scheduler, queue, or event consumer was found.",
    )
    for marker in required:
        assert marker in text, marker


def test_m112a_preserves_authority_security_and_read_only_boundaries():
    text = _text()
    required = (
        "THINKING_PROPOSAL != EXECUTION_AUTHORIZATION",
        "GOVERNANCE_EVALUATION != EXECUTION_AUTHORIZATION",
        "GOAL/TASK/TASKCONTEXT OWNERSHIP != ACTION PERMISSION",
        "Generic Act: NOT_IMPLEMENTED",
        "Generic Act integration: NOT_AUTHORIZED",
        "Generic Act authority: NOT_GRANTED",
        "Patch security: PAUSED",
        "EXECUTION AUTHORITY INTRODUCED: NO",
        "No implementation contract is authorized.",
        "M112A does not implement, authorize, or reopen",
        "changes to `PROGRESS.md`",
        "commit, tag, push, or PM acceptance claims",
        "Production implementation: NOT CLAIMED",
        "commit: NONE",
        "tag: NONE",
        "push: NONE",
        "M112B: NOT AUTHORIZED",
        "M113: NOT AUTHORIZED",
        "1. Aether remains one persistent mind: YES",
        "2. Goal remains above procedure: YES",
        "3. Context remains Core Coordination responsibility: YES",
        "4. Human Authority remains required for Goal acceptance: YES",
        "5. /chat does not become a competing authority: YES",
        "6. Working Memory does not become Goal authority: YES",
        "7. Action workflows do not become Thinking authority: YES",
        "8. AetherRuntime does not become cognitive authority merely because it owns process lifetime: YES",
        "9. AetherOS remains mechanism/environment rather than cognitive authority: YES",
        "10. No Goal, Task, TaskContext, criteria, revision, or provenance is fabricated: YES",
        "11. ThinkingProposal remains separate from Action authorization: YES",
        "12. Observe and Verify remain required for outcome completion: YES",
        "13. No Commitment runtime, persistence, scheduler, background execution, capability discovery, delegation, or Generic Act is introduced: YES",
    )
    for marker in required:
        assert marker in text, marker

    forbidden = (
        "MODEL_D_NO_QUALIFYING_RUNTIME_ENTRY_CURRENTLY_JUSTIFIED",
        "D_NO_QUALIFYING_RUNTIME_ENTRY_CURRENTLY_JUSTIFIED",
        "MODEL_E_CANONICAL_ASYNC_ENTRY_EXISTS` | SELECTED",
        "QUALIFYING AUTHORITATIVE RUNTIME ENTRY: PROVEN",
        "Future Build: JUSTIFIED FOR PM REVIEW",
        "Production ThinkingProposal producer: PROVEN",
        "Generic Act: IMPLEMENTED",
    )
    for marker in forbidden:
        assert marker not in text, marker
