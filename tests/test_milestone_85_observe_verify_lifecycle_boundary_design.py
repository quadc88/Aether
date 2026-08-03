from pathlib import Path

DOC_PATH = Path("docs/architecture/MILESTONE_85_OBSERVE_VERIFY_LIFECYCLE_BOUNDARY_RECORD.md")

TITLE = "# Milestone 85 Observation Classification, Verification Aggregation, and Lifecycle Boundary Record"

SECTIONS = (
    "## 1. Status and Scope",
    "## 2. Purpose",
    "## 3. Authoritative Existing Baseline",
    "## 4. Terminology",
    "## 5. Observation Classification",
    "## 6. Observation Intake Creation Semantics",
    "## 7. Observation Record Status Semantics",
    "## 8. Lifecycle Decision Fields",
    "## 9. Pending-Only Lifecycle Transitions",
    "## 10. Verification Aggregation",
    "## 11. Verification Aggregation Non-Goals",
    "## 12. Existing Verification-System Compatibility",
    "## 13. Simulation Verdict Boundary",
    "## 14. Verification Plan Boundary",
    "## 15. Evidence Contract Boundary",
    "## 16. Post-Apply Verification Gate Boundary",
    "## 17. Critic and Repair Triggering Boundary",
    "## 18. Producer Contract Gap",
    "## 19. Consumer Contract Gap",
    "## 20. Orphan-Component Rule",
    "## 21. Future Producer-Proof Gate",
    "## 22. Future Aggregator-Proof Gate",
    "## 23. Future Critic/Repair-Proof Gate",
    "## 24. Protected-Core and Interface Locks",
    "## 25. Persistence and Runtime Locks",
    "## 26. Deferred Questions",
    "## 27. Future Milestone Rules",
    "## 28. Milestone 85 Completion and Closure Rule",
)


def _text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def _normalized() -> str:
    return " ".join(_text().split())


def test_design_doc_exists_with_title_and_sections():
    assert DOC_PATH.exists()
    text = _text()
    assert TITLE in text
    for section in SECTIONS:
        assert section in text


def test_design_doc_is_design_only_and_authoritative():
    text = _normalized()
    for marker in (
        "design-only architecture boundary record",
        "Milestone 85 introduces no runtime capability",
        "This record is authoritative for the Observation Classification /",
        "until an explicitly authorized future architecture revision",
        "Milestone 85 is not considered closed until 85A Finalization is accepted",
        "does not close Milestone 85",
        "does not start Milestone 86",
    ):
        assert marker in text


def test_design_doc_locks_observation_classification():
    text = _normalized()
    for marker in (
        "json.dumps(value, sort_keys=True)",
        "normalized_observed = json.dumps(observed_value, sort_keys=True)",
        "normalized_expected = json.dumps(expected_value, sort_keys=True)",
        "matched iff normalized values are identical",
        "default=str",
        "type coercion",
        "fuzzy matching",
        "semantic matching",
        "numeric tolerance",
        "LLM judgment",
        "external verification",
        "1 != 1.0",
        '"1" != 1',
        "True != 1",
        "False != 0",
        "Observation Classification is complete",
        "must not repeat equality comparison as its primary",
    ):
        assert marker in text


def test_design_doc_locks_intake_creation_semantics():
    text = _normalized()
    for marker in (
        "handle_observation_intake(request, context=None)",
        "Phase A: validate, normalize, classify, and build all records in memory",
        "Phase B: persist through queue.save_observation_record",
        "No persistence occurs before Phase A completes",
        "zero saves",
        "zero persisted records",
        "no partial creation",
        "no orphan records",
        "matched or mismatched before persistence",
        "never pending",
        "completed is a service-envelope status, not an Observation Record status",
    ):
        assert marker in text


def test_design_doc_locks_status_vocabulary():
    text = _normalized()
    for status in ("pending", "matched", "mismatched", "error", "cancelled"):
        assert status in text
    assert "VALID_STATUSES" in text
    for marker in (
        "completed is not added to the Observation Record status set",
        "completed is not an Observation Record status",
    ):
        assert marker in text


def test_design_doc_locks_lifecycle_decision_fields():
    text = _normalized()
    for field in ("decision", "decided_at", "reviewer", "decision_reason"):
        assert field in text
    for marker in (
        "queue-owned lifecycle metadata",
        "At intake creation all remain None",
        "redefining decision as a Verification Verdict",
        "setting decision equal to Observation status at intake creation",
        "duplicate classification storage",
        "treating completed envelope status as a lifecycle decision",
    ):
        assert marker in text


def test_design_doc_locks_pending_only_transitions():
    text = _normalized()
    for marker in (
        "update_observation_record_status operates only when the current status is pending",
        "cancel_observation_record uses the same pending-only transition path",
        "the record is returned unchanged",
        "an in-memory warning is added",
        "the attempted transition is not persisted",
        "terminal with respect to this pending-only transition path",
        "Do not add a new lifecycle transition",
    ):
        assert marker in text


def test_design_doc_locks_classification_vs_aggregation():
    text = _normalized()
    for marker in (
        "Observation Classification: record-level strict equality classification",
        "Verification Aggregation: future higher-level evaluation over one or more",
        "It is not future Verification Aggregation work",
        "Conceptual definition only",
        "evidence sufficiency",
        "plan-step verification",
        "intended-effect confirmation",
        "goal completion conditions",
        "whether Critic or Repair consideration is required",
        "does not define a runtime module, API, schema, record type, or exact algorithm",
    ):
        assert marker in text


def test_design_doc_locks_aggregation_non_goals_and_deferred_questions():
    text = _normalized()
    for marker in (
        "repeat observed_value versus expected_value equality classification",
        "mutate matched/mismatched classification",
        "reuse pending-only lifecycle transitions to represent aggregation",
        "silently reuse simulation-verdict records",
        "silently reuse evidence-contract records",
        "silently invoke Critic or Repair",
        "execute tools",
        "collect evidence",
        "infer missing observations",
        "fabricate producer data",
        "call protected/core routes",
        "create external side effects",
        "### Deferred Aggregation Questions",
        "all-matched rule",
        "quorum or minimum-count rule",
        "missing evidence handling",
        "errored evidence handling",
        "cancelled evidence handling",
        "weighting",
        "confidence",
        "aggregation output record type",
        "not answered in Milestone 85",
    ):
        assert marker in text


def test_design_doc_locks_simulation_verdict_boundary():
    text = _normalized()
    for marker in (
        "verification_verdict_service consumes simulation_result_id",
        "simulation-safety invariants",
        "belongs to simulation results",
        "separate from Observation Record status and decision fields",
        "without a separate authorized design decision",
        "Simulation verdicts are not Observation aggregation",
    ):
        assert marker in text


def test_design_doc_locks_verification_plan_boundary():
    text = _normalized()
    for marker in (
        "verification_plan_service consumes text",
        "risk/action-type classification",
        "does not consume Observation Records",
        "not a Verification Aggregator for observations",
    ):
        assert marker in text


def test_design_doc_locks_evidence_contract_boundary():
    text = _normalized()
    for marker in (
        "Apply-executor evidence contracts represent evidence obligations",
        "approved plan intents",
        "not collected Observation values",
        "not Observation verification results",
        "evidence_contract_service is not an Observation aggregator",
    ):
        assert marker in text


def test_design_doc_locks_post_apply_gate_boundary():
    text = _normalized()
    for marker in (
        "post_apply_verification_gate_service consumes execution/gate records by",
        "not an Observation Record aggregator",
        "must not be silently repurposed",
    ):
        assert marker in text


def test_design_doc_locks_critic_repair_boundary():
    text = _normalized()
    for marker in (
        "Critic/Repair triggering from Observation Records is not implemented",
        "higher-level Verification Aggregation result",
        "not raw matched/mismatched records by default",
        "automatic repair launch",
        "retry behavior",
        "repair-cycle limits",
        "escalation",
        "human approval requirements",
        "trigger thresholds",
        "No automatic action follows Observation Classification",
    ):
        assert marker in text


def test_design_doc_locks_producer_and_consumer_gaps():
    text = _normalized()
    for marker in (
        "Production Observation Intake caller: none",
        "Real Observation producer: none",
        "Tool-driven evidence collector: none",
        "Automatic observation capture: none",
        "Observation Verification Aggregator: none",
        "Downstream consumer of an aggregation result: none",
        "Observation Record production consumer: none",
        "not authorized merely because the intake contract exists",
        "not authorized merely because classified records exist",
    ):
        assert marker in text


def test_design_doc_locks_orphan_component_rule():
    text = _normalized()
    for marker in (
        "exact upstream producer",
        "exact downstream consumer",
        "exact caller",
        "exact function",
        "exact invocation point",
        "exact input source",
        "exact output consumer",
        "valid dependency direction",
        "failure behavior",
        "lifecycle ownership",
        "persistence ownership",
        "execution classification",
        "focused test boundary",
        "ORPHAN RISK",
        "necessary foundational contract",
    ):
        assert marker in text


def test_design_doc_locks_proof_gates():
    text = _normalized()
    for marker in (
        "source of plan_step_id",
        "source of collector_contract_id",
        "source of evidence_items",
        "source of observed_value",
        "source of expected_value",
        "provenance and trust model",
        "privacy analysis",
        "supplied/collected/inferred/synthesized classification",
        "policy and approval requirements",
        "error behavior",
        "retry limits",
        "runtime/private persistence impact",
        "exact Observation Intake caller",
        "exact downstream consumer",
        "tool authorization",
        "side-effect classification",
        "execution sandbox",
        "timeout and retry policy",
        "rate-limit handling",
        "external-state verification",
        "human approval",
        "rollback or irreversibility analysis",
        "Milestone 85 authorizes none of this implementation",
        "separately justified initial caller",
        "exact record-selection rules",
        "grouping semantics",
        "exact output contract",
        "exact output consumer",
        "evidence-sufficiency semantics",
        "missing/errored/cancelled handling",
        "scope definition",
        "relationship to simulation verdicts",
        "relationship to verification plans",
        "relationship to evidence contracts",
        "relationship to post-apply gates",
        "Critic/Repair triggering ownership",
        "isolated test strategy",
        "no duplicate equality classification",
        "Do not approve an aggregator merely because classified records exist",
        "exact higher-level aggregation output",
        "exact trigger owner",
        "exact Critic or Repair entry point",
        "reason raw Observation status is insufficient",
        "trigger conditions",
        "human approval boundary",
        "retry and cycle-limit rules",
        "escalation behavior",
        "safety and policy review",
        "persistence and audit trail",
        "no automatic external action without explicit authorization",
    ):
        assert marker in text


def test_design_doc_locks_protected_core_and_interface():
    text = _normalized()
    for marker in (
        "304 paths",
        "108 schemas",
        "8 protected/core @app routes",
        "23 include_router calls",
        "zero direct /action/* routes",
        "Observation Intake router: absent",
        "Observation Verification Aggregation router: absent",
        "New API model: none",
        "Protected/core routes: unchanged",
        "raw len(app.routes)",
        "proven external consumer",
        "reason internal service use is insufficient",
        "access-control analysis",
        "exact route purpose",
        "intentional OpenAPI transition",
        "authorized boundary-test transition",
    ):
        assert marker in text


def test_design_doc_locks_persistence_and_runtime():
    text = _normalized()
    for marker in (
        "no: queue, store, persistence directory, schema migration, status migration,",
        "lifecycle migration, batch transaction layer, cleanup mechanism, rollback mechanism,",
        "real runtime/private writes, evidence collection, or tool execution",
        "The design lock test must not write files",
        "Tracked private/runtime remains empty",
        "docs/history remains clean",
        "Canonical drift remains 0",
    ):
        assert marker in text


def test_design_doc_locks_deferred_questions_and_future_milestone_rules():
    text = _normalized()
    for marker in (
        "## 26. Deferred Questions",
        "collector_contract_id semantics",
        "aggregation output type",
        "aggregation output vocabulary",
        "evidence sufficiency rules",
        "plan-step/action/goal scope",
        "aggregation persistence ownership",
        "aggregation lifecycle ownership",
        "downstream consumer",
        "Critic/Repair trigger semantics",
        "future ARCHITECTURE.md consolidation",
        "Deliberately deferred, not resolved speculatively",
        "## 27. Future Milestone Rules",
        "must pass the producer-proof gate",
        "must pass the aggregator-proof gate",
        "must pass its proof gate",
        "separate tests-only boundary step",
        "without a proven external consumer",
        "No Milestone 86 work begins automatically after Milestone 85",
    ):
        assert marker in text


def test_design_doc_locks_completion_and_closure_rule():
    text = _normalized()
    for marker in (
        "Milestone 85 contains only the 85A design-record chain",
        "Milestone 85 is not closed during the local Build",
        "design record validation",
        "doc-lock validation",
        "full-suite validation",
        "implementation commit",
        "milestone tag",
        "successful push",
        "post-push verification",
        "final ledger",
        "Finalization acceptance",
        "Milestone 86 remains not started",
    ):
        assert marker in text


def test_design_doc_has_no_runtime_instruction_language():
    lowered = _normalized().lower()
    for forbidden in (
        "run real apply",
        "execute rollback",
        "collect real evidence now",
        "start the server",
    ):
        assert forbidden not in lowered
