# Milestone 85 Observation Classification, Verification Aggregation, and Lifecycle Boundary Record

## 1. Status and Scope

- This is a design-only architecture boundary record.
- Milestone 85 introduces no runtime capability.
- Milestone 85 creates no producer, consumer, aggregator, collector, bridge,
  adapter, router, endpoint, API model, queue, store, or persistence system.
- Milestone 85 is not considered closed until 85A Finalization is accepted.
- The local 85A Build does not close Milestone 85.
- The local 85A Build does not start Milestone 86.
- This record is authoritative for the Observation Classification /
  Verification Aggregation / Lifecycle Decision boundary until an explicitly
  authorized future architecture revision incorporates or supersedes it.

## 2. Purpose

- Prevent conflation between four separate concepts:
  1. Observation Classification;
  2. Verification Aggregation;
  3. Lifecycle Decision;
  4. Critic/Repair Triggering.
- Respond to the rejected initial Milestone 85 proposal, which incorrectly
  assumed that Observation Intake created pending records and did not already
  classify observed versus expected values.
- The rejected proposal is not an authoritative source; the authoritative
  direction is the accepted corrected Milestone 85 Plan.

## 3. Authoritative Existing Baseline

- Observation Intake public function:
  handle_observation_intake(request, context=None)
- Observation matching: json.dumps(value, sort_keys=True)
- Intake-created Observation Record statuses: matched, mismatched
- Intake-created status not used: pending
- Service envelope status: completed
- completed is a service-envelope status, not an Observation Record status.
- Queue lifecycle fields at intake creation:
  decision == None, decided_at == None, reviewer == None,
  decision_reason == None
- Existing Observation Record statuses: pending, matched, mismatched,
  error, cancelled
- VALID_STATUSES remains exactly {pending, matched, mismatched, error,
  cancelled}.
- completed is not added to the Observation Record status set.

## 4. Terminology

- Observation: a persisted record of supplied observed and expected values
  plus classification.
- Observation Classification: record-level strict equality classification
  performed by Observation Intake.
- Verification Aggregation: future higher-level evaluation over one or more
  already-classified records.
- Lifecycle Decision: queue-owned transition metadata for pending-only
  lifecycle operations.
- Verification Verdict: existing simulation-result-bound record family, not
  Observation aggregation.
- Critic/Repair Triggering: future downstream decision boundary, not
  implemented from Observation Records.
- Producer: component that supplies real intake-ready observation inputs.
- Consumer: component that uses classified records or a future aggregation
  result.
- Orphan Component: runtime component without a proven upstream producer or
  downstream consumer.

## 5. Observation Classification

- Lock:
  normalized_observed = json.dumps(observed_value, sort_keys=True)
  normalized_expected = json.dumps(expected_value, sort_keys=True)
- matched iff normalized values are identical.
- Prohibited: default=str, type coercion, fuzzy matching, semantic matching,
  numeric tolerance, LLM judgment, external verification.
- Preserved distinctions: 1 != 1.0; "1" != 1; True != 1; False != 0.
- Observation Classification is complete.
- It is not future Verification Aggregation work.
- A future aggregator must not repeat equality comparison as its primary
  responsibility.

## 6. Observation Intake Creation Semantics

- Phase A: validate, normalize, classify, and build all records in memory.
- Phase B: persist through queue.save_observation_record.
- No persistence occurs before Phase A completes.
- Validation, normalization, or builder failure: zero saves, zero persisted
  records, no partial creation, no orphan records.
- Intake-created records are matched or mismatched before persistence.
- Intake-created records are never pending.

## 7. Observation Record Status Semantics

- pending belongs to records created through paths that use the builder
  default or store creation path without intake classification.
- matched and mismatched are classification results.
- error remains an existing lifecycle/status vocabulary item but is not
  automatically produced by Observation Intake classification.
- cancelled belongs to the pending-only cancellation lifecycle.
- completed is not an Observation Record status.
- Status ownership is not redefined by this record.

## 8. Lifecycle Decision Fields

- decision, decided_at, reviewer, decision_reason are queue-owned lifecycle
  metadata.
- At intake creation all remain None.
- Prohibited:
  - redefining decision as a Verification Verdict;
  - setting decision equal to Observation status at intake creation;
  - using decision as duplicate classification storage;
  - treating completed envelope status as a lifecycle decision.

## 9. Pending-Only Lifecycle Transitions

- update_observation_record_status operates only when the current status is
  pending.
- cancel_observation_record uses the same pending-only transition path.
- For a non-pending record:
  - the record is returned unchanged;
  - an in-memory warning is added;
  - the attempted transition is not persisted.
- Intake-created matched/mismatched records are terminal with respect to this
  pending-only transition path.
- Prohibit reopening them through the existing transition function.
- Do not add a new lifecycle transition.

## 10. Verification Aggregation

- Conceptual definition only.
- A future Verification Aggregator may consume one or more already-classified
  Observation Records and form a higher-level conclusion about:
  - evidence sufficiency;
  - plan-step verification;
  - intended-effect confirmation;
  - goal completion conditions;
  - whether Critic or Repair consideration is required.
- Potential grouping identifiers may include plan_step_id.
- collector_contract_id may be used only after its semantics are separately
  defined.
- This record does not define a runtime module, API, schema, record type, or
  exact algorithm.

## 11. Verification Aggregation Non-Goals

- A future aggregator must not:
  - repeat observed_value versus expected_value equality classification;
  - mutate matched/mismatched classification;
  - reuse pending-only lifecycle transitions to represent aggregation;
  - silently reuse simulation-verdict records;
  - silently reuse evidence-contract records;
  - silently invoke Critic or Repair;
  - execute tools;
  - collect evidence;
  - infer missing observations;
  - fabricate producer data;
  - call protected/core routes;
  - create external side effects.

### Deferred Aggregation Questions

- Explicitly deferred, not answered in Milestone 85:
  - all-matched rule;
  - quorum or minimum-count rule;
  - missing evidence handling;
  - errored evidence handling;
  - cancelled evidence handling;
  - weighting;
  - confidence;
  - plan-step versus action versus goal scope;
  - aggregation output record type;
  - persistence ownership;
  - lifecycle ownership;
  - output vocabulary;
  - exact downstream consumer.

## 12. Existing Verification-System Compatibility

- Current verification components are not Observation-compatible by default.
- Each boundary is documented accurately below; none is claimed to be an
  Observation Record aggregator.

## 13. Simulation Verdict Boundary

- verification_verdict_service consumes simulation_result_id.
- The simulation-verdict builder evaluates simulation-safety invariants.
- Its verdict family belongs to simulation results.
- Its lifecycle and verdict vocabulary are separate from Observation Record
  status and decision fields.
- Observation Records may not be routed through it without a separate
  authorized design decision.
- Simulation verdicts are not Observation aggregation.

## 14. Verification Plan Boundary

- verification_plan_service consumes text.
- It performs risk/action-type classification.
- It does not consume Observation Records.
- It is not a Verification Aggregator for observations.

## 15. Evidence Contract Boundary

- Apply-executor evidence contracts represent evidence obligations derived
  from approved plan intents.
- They are not collected Observation values.
- They are not Observation verification results.
- evidence_contract_service is not an Observation aggregator.

## 16. Post-Apply Verification Gate Boundary

- post_apply_verification_gate_service consumes execution/gate records by
  source identifiers.
- It is not an Observation Record aggregator.
- It must not be silently repurposed.

## 17. Critic and Repair Triggering Boundary

- Critic/Repair triggering from Observation Records is not implemented.
- A future trigger should consume an explicitly designed higher-level
  Verification Aggregation result, not raw matched/mismatched records by
  default.
- This record does not define:
  - automatic repair launch;
  - retry behavior;
  - repair-cycle limits;
  - escalation;
  - human approval requirements;
  - trigger thresholds.
- Preserved: No automatic action follows Observation Classification.

## 18. Producer Contract Gap

- Production Observation Intake caller: none
- Real Observation producer: none
- Tool-driven evidence collector: none
- Automatic observation capture: none
- The meaning of collector_contract_id is not yet authoritatively defined
  beyond being a required intake context identifier.
- Producer implementation is not authorized merely because the intake
  contract exists.

## 19. Consumer Contract Gap

- Observation Verification Aggregator: none
- Downstream consumer of an aggregation result: none
- Observation Record production consumer: none
- Consumer implementation is not authorized merely because classified
  records exist.

## 20. Orphan-Component Rule

- A new runtime component in the Observation/Verification chain must identify
  both:
  1. its exact upstream producer;
  2. its exact downstream consumer.
- Future proposals must prove: exact caller, exact function, exact invocation
  point, exact input source, exact output consumer, valid dependency
  direction, failure behavior, lifecycle ownership, persistence ownership,
  execution classification, and a focused test boundary.
- A service, builder, schema, queue, or record type without a proven
  counterpart must be marked: ORPHAN RISK
- It must not be implemented unless it is a necessary foundational contract
  that cannot be expressed safely as documentation alone.

## 21. Future Producer-Proof Gate

- Require, before any real producer implementation: source of plan_step_id,
  source of collector_contract_id, source of evidence_items, source of
  observed_value, source of expected_value, provenance and trust model,
  privacy analysis, supplied/collected/inferred/synthesized classification,
  policy and approval requirements, error behavior, retry limits,
  runtime/private persistence impact, exact Observation Intake caller, and
  exact downstream consumer.
- For tool-driven collection additionally require: tool authorization,
  side-effect classification, execution sandbox, timeout and retry policy,
  rate-limit handling, external-state verification, human approval, and
  rollback or irreversibility analysis.
- Milestone 85 authorizes none of this implementation.

## 22. Future Aggregator-Proof Gate

- Require, before any aggregator implementation: a real Observation producer
  or separately justified initial caller, exact record-selection rules,
  grouping semantics, exact output contract, exact output consumer,
  evidence-sufficiency semantics, missing/errored/cancelled handling, scope
  definition, relationship to simulation verdicts, relationship to
  verification plans, relationship to evidence contracts, relationship to
  post-apply gates, persistence ownership, lifecycle ownership, Critic/Repair
  triggering ownership, isolated test strategy, and no duplicate equality
  classification.
- Do not approve an aggregator merely because classified records exist.

## 23. Future Critic/Repair-Proof Gate

- Before Critic/Repair triggering from observation-derived verification,
  require: exact higher-level aggregation output, exact trigger owner, exact
  Critic or Repair entry point, reason raw Observation status is insufficient,
  trigger conditions, human approval boundary, retry and cycle-limit rules,
  escalation behavior, safety and policy review, persistence and audit trail,
  failure behavior, and no automatic external action without explicit
  authorization.
- Milestone 85 authorizes none of this implementation.

## 24. Protected-Core and Interface Locks

- OpenAPI: 304 paths / 108 schemas.
- api_server.py: 8 protected/core @app routes / 23 include_router calls /
  zero direct /action/* routes.
- Observation Intake router: absent.
- Observation Verification Aggregation router: absent.
- New API model: none.
- Protected/core routes: unchanged.
- Do not use raw len(app.routes) as an independent hard lock.
- Future API work requires: proven external consumer, reason internal service
  use is insufficient, access-control analysis, exact route purpose,
  intentional OpenAPI transition, and authorized boundary-test transition.

## 25. Persistence and Runtime Locks

- Milestone 85 introduces no: queue, store, persistence directory, schema
  migration, status migration, lifecycle migration, batch transaction layer,
  cleanup mechanism, rollback mechanism, real runtime/private writes,
  evidence collection, or tool execution.
- The design lock test must not write files.
- Tracked private/runtime remains empty.
- docs/history remains clean.
- Canonical drift remains 0.

## 26. Deferred Questions

- Deliberately deferred, not resolved speculatively:
  - collector_contract_id semantics;
  - aggregation output type;
  - aggregation output vocabulary;
  - evidence sufficiency rules;
  - missing/errored/cancelled handling;
  - plan-step/action/goal scope;
  - aggregation persistence ownership;
  - aggregation lifecycle ownership;
  - downstream consumer;
  - Critic/Repair trigger semantics;
  - future ARCHITECTURE.md consolidation.

## 27. Future Milestone Rules

- A future producer milestone must pass the producer-proof gate.
- A future aggregator milestone must pass the aggregator-proof gate.
- A future Critic/Repair integration must pass its proof gate.
- Any future runtime milestone may require a separate tests-only boundary
  step.
- No API milestone may begin without a proven external consumer.
- No Milestone 86 work begins automatically after Milestone 85.

## 28. Milestone 85 Completion and Closure Rule

- Milestone 85 contains only the 85A design-record chain.
- Milestone 85 is not closed during the local Build.
- Milestone 85 closes only after: design record validation, doc-lock
  validation, full-suite validation, implementation commit, milestone tag,
  successful push, post-push verification, final ledger, and Finalization
  acceptance.
- Milestone 86 remains not started.
