"""Static/document locks for the M109A runtime consumer-proof boundary."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / (
    "docs/architecture/"
    "MILESTONE_109A_GOAL_TO_PLAN_RUNTIME_CONSUMER_PROOF_BOUNDARY.md"
)
POLICY = ROOT / "aether/thinking/policy.py"
LOOP = ROOT / "aether/core/loop.py"
API_SERVER = ROOT / "aether/interface/api_server.py"
TASK_CONTEXT = ROOT / "aether/core/task_context.py"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_m109a_record_locks_negative_consumer_decision_and_scope():
    text = " ".join(_text(RECORD).split())
    required = (
        "# Milestone 109A Goal-to-Plan Runtime Consumer Proof Boundary",
        "STRICT READ-ONLY DESIGN / DISCOVERY / CONSUMER-PROOF",
        "131c921ce263ef8ad83003f625058ba77568dea9",
        "306 paths / 112 schemas",
        "8 direct @app routes / 23 include_router / 0 direct /action/*",
        "Goal -> accepted Goal authority -> Task -> authoritative TaskContext",
        "ThinkingProposal -> canonical Plan -> selected canonical PlanStep",
        "Core Governance Evaluation -> STOP BEFORE GENERIC ACT",
        "D_NO_REAL_RUNTIME_CONSUMER_CURRENTLY_JUSTIFIED",
        "MODEL_D_NO_RUNTIME_CONSUMER_YET",
        "Think -> Plan process-local consumer: SATISFIED",
        "Think -> Plan consumer outside Core Coordination: NOT YET SATISFIED",
        "External canonical runtime consumer: ABSENT",
        "Runtime Build: NOT JUSTIFIED",
        "Next authorized action: HUMAN/PROJECT-MANAGER M109A CONSUMER-PROOF REVIEW",
    )
    for marker in required:
        assert marker in text, marker


def test_m109a_record_preserves_producer_and_authority_boundaries():
    text = _text(RECORD)
    required = (
        "ThinkingProposal contract class: PRESENT",
        "Current production ThinkingProposal producer: ABSENT",
        "decision_type` is not `PROPOSAL_READY` or `PROPOSAL_NOT_READY`",
        "normalized user text is not an authorized `proposed_objective` mapping",
        "GOVERNANCE_EVALUATION != EXECUTION_AUTHORIZATION",
        "Generic Act: NOT_IMPLEMENTED",
        "Generic Act integration: NOT_AUTHORIZED",
        "Generic Act authority: NOT_GRANTED",
        "a Goal-to-Plan external runtime consumer",
        "a ThinkingProposal producer, adapter, provider, or factory",
        "`PROGRESS.md`, README, Constitution, Architecture authority, production code",
    )
    for marker in required:
        assert marker in text, marker


def test_m109a_record_contains_candidate_models_and_exact_write_set():
    text = _text(RECORD)
    required = (
        "MODEL_A_CHAT_AS_CANONICAL_CONSUMER",
        "MODEL_B_CORE_LOOP_AS_CANONICAL_CONSUMER",
        "MODEL_C_NEW_COORDINATION_RUNTIME_ENTRYPOINT",
        "MODEL_D_NO_RUNTIME_CONSUMER_YET",
        "MILESTONE_109A_GOAL_TO_PLAN_RUNTIME_CONSUMER_PROOF_BOUNDARY.md",
        "test_milestone_109a_goal_to_plan_runtime_consumer_proof_boundary.py",
        "/home/aether/summaries/milestone_109A_goal_to_plan_consumer_proof_summary.txt",
        "No API, worker, scheduler, queue, event bridge, persistence path",
    )
    for marker in required:
        assert marker in text, marker

    forbidden = (
        "MODEL_A_CHAT_AS_CANONICAL_CONSUMER` | SELECTED",
        "MODEL_B_CORE_LOOP_AS_CANONICAL_CONSUMER` | SELECTED",
        "MODEL_C_NEW_COORDINATION_RUNTIME_ENTRYPOINT` | SELECTED",
        "External runtime consumer: PROVEN",
        "Runtime Build: JUSTIFIED",
        "Generic Act: IMPLEMENTED",
        "PROGRESS.md updated",
    )
    for marker in forbidden:
        assert marker not in text, marker


def test_current_legacy_thinking_path_is_not_a_canonical_proposal_producer():
    policy = _text(POLICY)
    assert '"decision_type": "ask_clarification"' in policy
    assert '"decision_type": "suggest_tool"' in policy
    assert '"decision_type": "respond_only"' in policy
    assert "ThinkingProposal" not in policy
    assert "proposed_completion_criteria" not in policy
    assert "proposed_failure_criteria" not in policy
    assert "proposed_blocked_criteria" not in policy


def test_current_chat_and_api_paths_have_no_canonical_consumer_wiring():
    loop = _text(LOOP)
    api_server = _text(API_SERVER)
    assert "ThinkingProposal" not in loop
    assert "materialize_thinking_proposal" not in loop
    assert "create_task" not in loop
    assert "select_context" not in loop
    assert "create_plan" not in loop
    assert "create_plan_step" not in loop
    assert "evaluate_canonical_plan_governance" not in loop
    assert "ThinkingProposal" not in api_server
    assert "CoreCoordination" not in api_server
    assert "/goal-to-plan" not in api_server


def test_core_coordination_is_the_only_production_materialization_seam():
    source = _text(TASK_CONTEXT)
    assert "def materialize_thinking_proposal(self, proposal: Any) -> Plan:" in source
    assert "return self.create_plan(" in source
    assert "def evaluate_canonical_plan_governance(" in source
    assert "def create_plan_step(" in source

    external_materializers = []
    for path in (ROOT / "aether").rglob("*.py"):
        if path != TASK_CONTEXT and "materialize_thinking_proposal(" in _text(path):
            external_materializers.append(path)
    assert external_materializers == []

    proposal_constructors = []
    for path in (ROOT / "aether").rglob("*.py"):
        if path == ROOT / "aether/thinking/proposal.py":
            continue
        if re.search(r"\bThinkingProposal\s*\(", _text(path)):
            proposal_constructors.append(path)
    assert proposal_constructors == []
