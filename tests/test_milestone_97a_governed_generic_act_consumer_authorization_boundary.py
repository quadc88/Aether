"""Static/document-contract locks for the M97A consumer-proof boundary."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "docs/architecture/MILESTONE_97A_GOVERNED_GENERIC_ACT_CONSUMER_AUTHORIZATION_BOUNDARY.md"


def _text() -> str:
    return RECORD.read_text(encoding="utf-8")


def _normalized() -> str:
    return " ".join(_text().split())


def test_title_classification_and_starting_authority_are_locked():
    text = _normalized()
    for marker in (
        "# Milestone 97A Governed Generic Act Consumer & Authorization Boundary",
        "Classification: DESIGN / DISCOVERY / CONSUMER-PROOF BOUNDARY",
        "DESIGN / DISCOVERY ONLY",
        "a62124ac92c03c363bcb942fb9191e7269d152f5",
        "milestone-96-authoritative-goal-to-plan-cognitive-foundation-closure",
        "M96 state: CLOSED / GIT-DURABLE / PM-ACCEPTED",
        "Architecture version: `0.3.0`",
        "OpenAPI baseline: `306 paths / 112 schemas`",
        "api_server baseline: `8 direct @app routes / 23 include_router / 0 direct /action/*`",
    ):
        assert marker in text


def test_m96_closure_inheritance_and_stop_boundary_are_locked():
    text = _normalized()
    for marker in (
        "M96 Closure Inheritance",
        "Human Authority -> Goal acceptance -> Goal -> Task",
        "selected TaskContext for reasoning turn",
        "Thinking proposal -> canonical Plan -> canonical PlanStep",
        "Core Governance evaluation -> STOP BEFORE GENERIC ACT",
        "9d288215f2483913ccc702916bbd39e8c487a4e0",
        "milestone-96G-canonical-plan-governance-evaluation",
        "authorization_granted",
        "execution_allowed",
        "action_dispatch_allowed",
        "always `False`",
        "M97A does not authorize M97B, M98, or any runtime successor",
    ):
        assert marker in text


def test_producer_inventory_and_real_runtime_call_are_locked():
    text = _normalized()
    for marker in (
        "Current Producer Inventory",
        "aether/core/governance.py",
        "CanonicalPlanGovernanceEvaluationRequest",
        "aether/core/task_context.py",
        "REAL_RUNTIME_EVALUATOR",
        "REAL_RUNTIME_CALLER / REQUEST PRODUCER",
        "Core Coordination caller returns the evaluation to its caller",
        "does not read the result to authorize or dispatch an Action",
    ):
        assert marker in text


def test_no_production_result_consumer_and_reference_classifications_are_locked():
    text = _normalized()
    for marker in (
        "Current Consumer Inventory",
        "NO_CONSUMER",
        "No production code consumes",
        "CanonicalPlanGovernanceEvaluation",
        "TEST_ONLY_CONSUMER",
        "DOCUMENT_ONLY_REFERENCE",
        "Naming, a returned object, or a test assertion is not evidence of a real runtime consumer",
    ):
        assert marker in text


def test_existing_execution_surface_inventory_is_locked():
    text = _normalized()
    for marker in (
        "Existing Execution-Surface Inventory",
        "Capability-specific restricted read",
        "Legacy tool executor",
        "Action-specific patch apply",
        "Action-specific patch rollback",
        "Guided repair / proposal launchers",
        "Approval execution gates",
        "NOT_PROVEN",
        "Existing mechanisms must not be accepted as Generic Act consumer proof by analogy",
    ):
        assert marker in text


def test_governance_evaluation_and_execution_authorization_are_distinct():
    text = _normalized()
    for marker in (
        "GOVERNANCE_EVALUATION != EXECUTION_AUTHORIZATION",
        "Governance Evaluation Semantics",
        "evaluation_status == \"EVALUATED\"",
        "governance_decision == \"evaluate\"",
        "does not mint an execution scope",
        "Execution Authorization Semantics",
        "No execution authorization object is defined or implemented by M97A",
        "pending, historical, or consumed approval",
    ):
        assert marker in text


def test_identity_binding_matrix_is_complete_and_non_fabricating():
    text = _normalized()
    for marker in (
        "Identity Binding Matrix",
        "goal_id",
        "task_id",
        "task_context_id",
        "task_context_revision",
        "plan_id",
        "plan_revision",
        "selected `plan_step_id`",
        "Thinking proposal identity/revision",
        "governance_evaluation_id",
        "Governance policy/profile identity",
        "Human approval identity",
        "Capability/action identity",
        "Arguments/input fingerprint",
        "Authority/freshness timestamp or generation",
        "No absent identifier is fabricated by M97A",
    ):
        assert marker in text


def test_freshness_and_staleness_matrix_is_fail_closed():
    text = _normalized()
    for marker in (
        "Freshness and Staleness Matrix",
        "Selected Task changed",
        "TaskContext changed",
        "Plan changed",
        "Selected PlanStep changed",
        "ThinkingProposal changed",
        "Governance policy changed",
        "Governance evaluation stale",
        "Approval absent, rejected, cancelled, or consumed",
        "Requested Action differs from evaluated Action",
        "Arguments differ from evaluated arguments",
        "Authority expired",
        "Task paused, cancelled, or completed",
        "Reject",
        "M97A adds no runtime checks or execution path",
    ):
        assert marker in text


def test_human_authority_and_organ_ownership_are_locked():
    text = _normalized()
    for marker in (
        "Human Authority Analysis",
        "NOT_YET_PROVABLE",
        "existing restricted-read approval rule must not be generalized",
        "Organ Ownership",
        "Thinking proposes",
        "Core Governance owns policy, authority, and authorization decisions",
        "Core Coordination owns Goal/Task/TaskContext continuity",
        "Action executes only after a valid future authorization",
        "Verification supplies evidence after Action",
        "AetherOS supplies facts and mechanisms",
    ):
        assert marker in text


def test_asc_capability_and_observation_boundaries_are_locked():
    text = _normalized()
    for marker in (
        "ASC and TaskContext Safety",
        "one Authoritative Shared Cognitive Context framework",
        "one authoritative TaskContext per active Task",
        "one selected current TaskContext per reasoning turn",
        "no silent merge",
        "file.restricted_read",
        "M97A does not add or authorize",
        "Observation, Persistent Observation Record, Observation Intake",
        "Verification Aggregation",
        "no Generic Act consumer exists",
    ):
        assert marker in text


def test_consumer_proof_model_decision_and_non_goals_are_locked():
    text = _normalized()
    for marker in (
        "Consumer-Proof Decision",
        "D_NO_REAL_CONSUMER_CURRENTLY_JUSTIFIED",
        "Generic Act Model Comparison",
        "MODEL_A_DIRECT_GOVERNANCE_RESULT_CONSUMER",
        "MODEL_B_IMMUTABLE_EXECUTION_AUTHORIZATION_OBJECT",
        "MODEL_C_CAPABILITY_SPECIFIC_ADAPTERS_ONLY",
        "MODEL_D_NO_GENERIC_ACT_YET",
        "Selected Model or No-Model Decision",
        "Rejected Models",
        "Explicit Non-Goals",
        "M97B, M98, or any successor runtime milestone",
        "Git lifecycle operation",
    ):
        assert marker in text


def test_future_prerequisites_closure_gate_and_static_only_boundary_are_locked():
    text = _normalized()
    for marker in (
        "Future Runtime Prerequisites",
        "one real consumer and its owning organ",
        "an explicit authorization contract distinct from Governance evaluation",
        "expiry, stale-state, cancellation, pause, and single-use behavior",
        "post-Action result shape sufficient for later truthful Observe/Verify work",
        "No item above is implemented or authorized by M97A",
        "Closure and Next-Step Gate",
        "M97A: DESIGN / DISCOVERY ONLY",
        "Generic Act: NOT_IMPLEMENTED",
        "Generic Act integration: NOT_AUTHORIZED",
        "Generic Act authority: NOT_GRANTED",
        "Next authorized action: human/project-manager M97A Build review",
    ):
        assert marker in text

    source = Path(__file__).read_text(encoding="utf-8")
    for forbidden in (
        "from " + "aether",
        "import " + "aether",
        "Test" + "Client",
        "sub" + "process",
        "write" + "_text(",
        "json." + "dump",
        "@pytest.mark." + "parametrize",
    ):
        assert forbidden not in source
