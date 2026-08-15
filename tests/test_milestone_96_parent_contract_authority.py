"""Static locks for the M96 parent contract authority record."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "docs/architecture/MILESTONE_96_PARENT_CONTRACT_AUTHORITY.md"
PROGRESS = ROOT / "PROGRESS.md"


def _text() -> str:
    return RECORD.read_text(encoding="utf-8")


def _normalized() -> str:
    return " ".join(_text().split())


def test_previous_parent_contract_finding_is_explicit():
    text = _normalized()
    assert "A standalone authoritative Milestone 96 parent contract was NOT previously proven" in text
    assert "not retroactively relabeled as a previously authoritative parent contract" in text


def test_parent_name_and_objective_are_exactly_locked():
    text = _normalized()
    assert "Milestone 96 — Authoritative Goal-to-Plan Cognitive Foundation" in text
    assert "minimum authoritative, process-local cognitive execution foundation" in text
    assert "while stopping before any generic Act" in text


def test_canonical_parent_path_is_locked():
    text = _normalized()
    for marker in (
        "Human Authority -> Goal acceptance -> Goal -> Task",
        "authoritative TaskContext",
        "selected TaskContext for reasoning turn",
        "Thinking proposal",
        "canonical Plan",
        "canonical PlanStep",
        "Core Governance evaluation",
        "STOP BEFORE GENERIC ACT",
    ):
        assert marker in text


def test_m96a_durable_contribution_is_locked():
    text = _normalized()
    for marker in (
        "M96A - DESIGN / OWNERSHIP BOUNDARY",
        "Goal Intake/Human Authority ownership of Goal",
        "Core Coordination ownership of Task and TaskContext",
        "canonical Plan/PlanStep ownership direction",
        "c86fcf05c12ae19bdf957b100ea2969905509e3a",
        "milestone-96A-authoritative-goal-task-plan-boundary",
        "M96A did not implement runtime Plan or PlanStep",
    ):
        assert marker in text


def test_m96b_durable_contribution_is_locked():
    text = _normalized()
    for marker in (
        "M96B - GOAL-FIRST PROCESS-LOCAL RUNTIME FOUNDATION",
        "explicit Goal acceptance",
        "accepted Goal -> atomic Task -> initial authoritative TaskContext",
        "process-local Core Coordination registry",
        "immutable snapshots/revisions",
        "M96B does not implement Plan, PlanStep, Think -> Plan",
        "32f9a36b7d847afb3960a6efd87c60978a656163",
        "milestone-96B-goal-first-in-memory-foundation",
    ):
        assert marker in text


def test_current_satisfied_obligations_are_locked():
    text = _normalized()
    for marker in (
        "Obligation 1 - Human-authority Goal admission",
        "Obligation 2 - Authoritative Task ownership",
        "Obligation 3 - Authoritative TaskContext",
        "Status: **SATISFIED**",
        "Current state: **SATISFIED / MUST REMAIN LOCKED**",
    ):
        assert marker in text


def test_current_unsatisfied_obligations_are_locked():
    text = _normalized()
    for marker in (
        "Obligation 4 - Canonical Plan runtime",
        "Obligation 5 - Canonical PlanStep runtime",
        "Obligation 6 - Think -> Plan authoritative consumer seam",
        "Obligation 7 - Governance before generic Act",
        "NOT YET SATISFIED",
    ):
        assert marker in text


def test_parent_non_goals_and_process_local_decision_are_locked():
    text = _normalized()
    for marker in (
        "Explicit Parent Non-Goals",
        "persistent Goal, Task, TaskContext, or Plan storage",
        "restart or cross-session restoration",
        "Observation Intake",
        "Verification Aggregation",
        "scheduler, background execution, or wake behavior",
        "process-local foundation",
        "Persistence is not a prerequisite for M96 closure",
    ):
        assert marker in text


def test_governance_ownership_and_stop_boundary_are_locked():
    text = _normalized()
    for marker in (
        "Thinking proposes",
        "Governance authorizes",
        "Verification supplies evidence",
        "Action executes only within authorization",
        "Core Governance owns authorization",
        "Core Coordination owns task/context continuity",
        "Time provides context, not authority",
        "Resource Observation reports facts; Resource Governance decides",
        "No silent context merge is permitted",
        "Generic Act remains unauthorized",
    ):
        assert marker in text


def test_m96_open_and_m96c_non_authorization_are_locked():
    text = _normalized()
    progress = PROGRESS.read_text(encoding="utf-8")
    for marker in (
        "M96: OPEN",
        "M96C: NOT AUTHORIZED",
        "does not authorize Git finalization",
        "does not authorize them",
    ):
        assert marker in text
    assert "M96 Parent Contract Authority" in progress
