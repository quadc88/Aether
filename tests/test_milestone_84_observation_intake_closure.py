"""Doc-only closure lock test for Milestone 84 Observation Intake Closure.

Static text checks only. No service import, no endpoint invocation, no
TestClient, no runtime access, no file writes beyond reading the closure
document. Absence locks for router/API/bridge artifacts remain owned by
tests/test_observation_intake_boundary.py.
"""

from pathlib import Path

DOC = Path("docs/architecture/MILESTONE_84_OBSERVATION_INTAKE_CLOSURE.md")

TITLE = "# Milestone 84 Observation Intake Closure"

SECTIONS = (
    "## 1. Closure Status",
    "## 2. Milestone Purpose",
    "## 3. Delivered Artifacts",
    "## 4. Milestone 84A Design and Boundary Locks",
    "## 5. Milestone 84B Service Foundation",
    "## 6. Milestone 84C Consumer-Need Decision",
    "## 7. Final Architecture Boundary",
    "## 8. Non-Executing Contract",
    "## 9. Input Contract",
    "## 10. Strict Matching Contract",
    "## 11. Validation Atomicity",
    "## 12. Persistence Transactionality Limitation",
    "## 13. Metadata, Context, and Unknown-Field Decisions",
    "## 14. Observation Status and Lifecycle Decision Semantics",
    "## 15. Existing Observation Record API Relationship",
    "## 16. Router/API Decision",
    "## 17. Preserved Protected-Core Boundaries",
    "## 18. Test and Validation Baseline",
    "## 19. Deferred Work",
    "## 20. Future Consumer-Proof Gate",
    "## 21. Milestone 85 Eligibility",
    "## 22. Milestone 84 Closure Declaration",
)

TAGS = (
    "milestone-84A-observation-intake-bridge-design",
    "milestone-84A-observation-intake-boundary-tests",
    "milestone-84B-observation-intake-service-foundation",
)


def _text() -> str:
    return DOC.read_text(encoding="utf-8")


def _norm() -> str:
    return " ".join(_text().split())


def test_closure_doc_exists():
    assert DOC.exists()


def test_closure_doc_has_exact_title_and_sections():
    text = _text()
    assert text.startswith(TITLE + "\n")
    for section in SECTIONS:
        assert section in text


def test_closure_doc_locks_closure_timing():
    text = _text()
    for marker in (
        "Milestone 84 is not considered closed until 84D Finalization is accepted",
        "The local 84D Build does not close Milestone 84",
        "The local 84D Build does not start Milestone 85",
        "Commit, tag, and push occur only during 84D Finalization",
    ):
        assert marker in text
    assert "declared closed only after" in text
    assert "finalization acceptance" in text


def test_closure_doc_records_delivered_artifacts_and_tags():
    text = _text()
    for path_marker in (
        "docs/architecture/OBSERVATION_INTAKE_BRIDGE_DESIGN.md",
        "tests/test_observation_intake_bridge_design.py",
        "tests/test_observation_intake_boundary.py",
        "aether/action/services/observation_intake_service.py",
        "tests/test_observation_intake_service.py",
    ):
        assert path_marker in text
    for tag in TAGS:
        assert tag in text


def test_closure_doc_records_84c_decision():
    text = _norm()
    for marker in (
        "Confirmed production consumers: none",
        "Production importers of handle_observation_intake: zero",
        "Decision: defer integration",
        "84C Build: skipped because no consumer was proven",
        "The existence of a service is not sufficient justification for "
        "creating a router or endpoint",
    ):
        assert marker in text


def test_closure_doc_locks_functional_contract():
    text = _norm()
    for marker in (
        "handle_observation_intake(request, context=None)",
        "plan_step_id",
        "collector_contract_id",
        "evidence_items",
        "observed_value",
        "expected_value",
        "json.dumps(value, sort_keys=True)",
        "default=str is not used",
        "matched",
        "mismatched",
        "decision at creation: None",
        "Phase A: validate, normalize, classify, and build all records in memory",
        "Phase B: persist prepared records through queue.save_observation_record",
        "No persistence occurs before Phase A completes",
    ):
        assert marker in text


def test_closure_doc_locks_policy_decisions():
    text = _norm()
    for marker in (
        "Top-level metadata: validated but not persisted",
        "Per-item metadata: persisted",
        "Unknown non-forbidden fields: tolerated and ignored",
        "Context: accepted but ignored",
        "Context forwarding: not performed",
        "context_metadata: remains empty at creation",
        "Forbidden generated/internal fields are rejected at the top level",
        "results in zero saves",
        "create zero persisted records",
        "No partial creation occurs for validation failures",
        "No orphan records occur for validation failures",
        "No batch transaction exists",
        "No rollback or cleanup API exists",
        "Persistence exceptions propagate",
        "No completed envelope is returned on failure",
        "Queue-level transactionality remains deferred",
    ):
        assert marker in text


def test_closure_doc_locks_architecture_boundaries_and_api_relationship():
    text = _norm()
    for marker in (
        "304 paths / 108 schemas",
        "Observation paths: exact 4",
        "Observation operation IDs: exact 5",
        "8 protected/core @app routes",
        "23 include_router calls",
        "zero direct /action/* routes",
        "POST /observation-records",
        "GET /observation-records/{observation_id}",
        "PATCH /observation-records/{observation_id}/status",
        "POST /observation-records/{observation_id}/cancel",
        "the only external store API",
        "No duplicate Observation Intake endpoint was added",
        "Router/API justified now: no",
        "intended as an internal producer capability",
    ):
        assert marker in text


def test_closure_doc_records_deferred_work_and_consumer_gate():
    text = _norm()
    for marker in (
        "1. Real evidence collection.",
        "2. Tool-driven observation collection.",
        "3. Automatic observation capture.",
        "4. Execution-loop Observe-stage wiring.",
        "5. Verification consumer integration.",
        "6. Critic and Repair runtime linkage.",
        "7. Timeline or memory-learning integration.",
        "8. A real internal consumer for Observation Intake.",
        "9. Router/API exposure only after consumer proof.",
        "10. Queue-level batch transactionality, if ever required.",
        "11. Access-control and authorization design for any future external intake.",
        "12. Mapping future collector outputs into the intake evidence_items shape.",
        "None of the deferred items is described as completed",
        "actual plan_step_id source",
        "actual collector_contract_id source",
        "actual evidence_items source",
        "caller-supplied observed_value",
        "caller-supplied expected_value",
        "valid dependency direction",
        "non-execution preservation",
        "failure propagation behavior",
        "persistence-isolation tests",
        "no speculative API exposure",
        "authentication and authorization analysis",
        "intentional OpenAPI changes",
        "intentional include_router changes",
        "protected-core regression plan",
    ):
        assert marker in text


def test_closure_doc_does_not_claim_observation_implementation():
    lowered = _norm().lower()
    for marker in (
        "real evidence collection: not implemented",
        "tool-driven observation collection: not implemented",
        "automatic observation capture: not implemented",
        "execution-loop observe wiring: not implemented",
        "verification/critic/repair runtime linkage: not implemented",
        "router/api: not implemented and not justified",
        "consumer integration: deferred because no real consumer exists",
    ):
        assert marker in lowered
    for forbidden in (
        "run real apply",
        "execute rollback",
        "collect real evidence now",
        "full observe loop",
        "observe loop is implemented",
    ):
        assert forbidden not in lowered


def test_closure_doc_records_milestone_85_eligibility():
    text = _norm()
    for marker in (
        "Milestone 85: not currently defined",
        "Milestone 85 may not start automatically",
        "human/project-manager review and acceptance of the 84D Finalization",
        "future Milestone 85 Plan",
        "does not define the content of Milestone 85",
    ):
        assert marker in text
