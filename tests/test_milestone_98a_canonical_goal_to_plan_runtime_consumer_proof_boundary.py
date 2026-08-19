"""Static/document lock for the M98A runtime consumer-proof boundary."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "docs/architecture/MILESTONE_98A_CANONICAL_GOAL_TO_PLAN_RUNTIME_CONSUMER_PROOF_BOUNDARY.md"


def test_m98a_runtime_consumer_proof_boundary_is_locked():
    text = " ".join(RECORD.read_text(encoding="utf-8").split())

    required = (
        "# Milestone 98A Canonical Goal-to-Plan Runtime Consumer Proof Boundary",
        "STRICT READ-ONLY DESIGN / DISCOVERY / CONSUMER-PROOF",
        "GOVERNANCE_EVALUATION != EXECUTION_AUTHORIZATION",
        "4d45dbcc7613c746cb7b84279d95a46deaab0382",
        "306 paths / 112 schemas",
        "8 direct @app routes / 23 include_router / 0 direct /action/*",
        "Goal -> Task -> authoritative TaskContext -> selected TaskContext",
        "ThinkingProposal -> canonical Plan -> selected canonical PlanStep",
        "Core Governance Evaluation -> STOP BEFORE GENERIC ACT",
        "aether/core/goal.py:155-186",
        "aether/core/task_context.py:598-632",
        "aether/core/task_context.py:638-742",
        "aether/core/task_context.py:764-820",
        "aether/interface/api_server.py:223-299",
        "aether/core/loop.py:28-332",
        "aether/thinking/proposal.py:96-177",
        "ThinkingProposal production status:",
        "Contract class: PRESENT",
        "Production producer/provider: ABSENT",
        "NO_CANONICAL_GOAL_TO_PLAN_RUNTIME_CONSUMER",
        "D_NO_REAL_RUNTIME_CONSUMER_CURRENTLY_JUSTIFIED",
        "MODEL_D_NO_RUNTIME_CONSUMER_YET",
        "Runtime Build: NOT YET JUSTIFIED",
        "Generic Act: NOT_IMPLEMENTED",
        "Generic Act integration: NOT_AUTHORIZED",
        "Generic Act authority: NOT_GRANTED",
        "Next authorized action: HUMAN/PROJECT-MANAGER M98A BUILD-SCOPE REVIEW",
    )
    for marker in required:
        assert marker in text, marker

    forbidden = (
        "A_REAL_RUNTIME_CONSUMER_JUSTIFIED",
        "MODEL_A_CHAT_AS_CANONICAL_COGNITIVE_CONSUMER` | SELECTED",
        "MODEL_B_CORE_LOOP_AS_CANONICAL_COGNITIVE_CONSUMER` | SELECTED",
        "MODEL_C_NEW_COORDINATION_RUNTIME_ENTRYPOINT` | SELECTED",
        "Runtime Build: JUSTIFIED FOR PM REVIEW",
        "Generic Act: IMPLEMENTED",
        "PROGRESS.md updated",
    )
    for marker in forbidden:
        assert marker not in text, marker
