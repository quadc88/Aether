# Milestone 84 Observation Intake Closure

## 1. Closure Status

- This is the closure record for Milestone 84.
- Milestone 84 is not considered closed until 84D Finalization is accepted.
- The local 84D Build does not close Milestone 84.
- The local 84D Build does not start Milestone 85.
- Commit, tag, and push occur only during 84D Finalization.

## 2. Milestone Purpose

Milestone 84 selected Candidate A: Observation Intake Bridge.

Its purpose was to provide a safe, declarative, non-executing producer
foundation for the closed Milestone 83 Observation Record Store.

The milestone did not implement the entire Observe stage. This closure record
distinguishes:

- Observation Intake service foundation: completed
- Real evidence collection: not implemented
- Tool-driven observation collection: not implemented
- Automatic observation capture: not implemented
- Execution-loop Observe wiring: not implemented
- Verification/Critic/Repair runtime linkage: not implemented
- Router/API: not implemented and not justified
- Consumer integration: deferred because no real consumer exists

## 3. Delivered Artifacts

Design record:

- docs/architecture/OBSERVATION_INTAKE_BRIDGE_DESIGN.md

Design lock:

- tests/test_observation_intake_bridge_design.py

Boundary lock:

- tests/test_observation_intake_boundary.py

Service implementation:

- aether/action/services/observation_intake_service.py

Focused service tests:

- tests/test_observation_intake_service.py

Milestone 84A Design Record:

- implementation commit: e17e5971843ea861e45e58920b587c729d103468
- tag: milestone-84A-observation-intake-bridge-design
- tag target: e17e5971843ea861e45e58920b587c729d103468
- ledger commit: 6dfeef01cb5f99bf4edf623c9346bade28af3bb8

Milestone 84A Boundary Tests:

- implementation commit: e8c2cfe01b51c307aa11464d67925878961412bf
- tag: milestone-84A-observation-intake-boundary-tests
- tag target: e8c2cfe01b51c307aa11464d67925878961412bf
- ledger commit: f31c14c2000902f28de2bb6d2f9c24864afe644f

Milestone 84B Service Foundation:

- implementation commit: e85aa0e8dd0f9f98d07254161b31a26fef588cf3
- tag: milestone-84B-observation-intake-service-foundation
- tag target: e85aa0e8dd0f9f98d07254161b31a26fef588cf3
- ledger commit: 0d7eecee0e11710e9aadbd74bb2b62cab9f4d60f

## 4. Milestone 84A Design and Boundary Locks

- The design document contains the locked Observation Intake contract.
- Design-lock tests remain doc-only.
- Boundary tests remain static and non-executing.
- The pre-84B service-absence assertion transitioned during 84B into a
  post-foundation service-existence assertion.
- The boundary test count remained 17.
- Router, API, API model, runtime bridge, and automatic capture remain
  absent.
- No safety boundary was weakened.

## 5. Milestone 84B Service Foundation

Public function:

- handle_observation_intake(request, context=None)

Architecture:

- plain action-layer service;
- no interface-layer import;
- no router dependency;
- no runtime-handler dependency;
- no network dependency;
- no tool execution;
- no evidence collection.

Processing model:

- Phase A: validate, normalize, classify, and build all records in memory.
- Phase B: persist prepared records through queue.save_observation_record.

No persistence occurs before Phase A completes.

## 6. Milestone 84C Consumer-Need Decision

The completed decision gate recorded:

- Confirmed production consumers: none
- Production importers of handle_observation_intake: zero
- Current workflow possessing all required intake fields: none
- Internal integration justified: no
- Adapter/bridge justified: no
- Router/API justified: no
- Decision: defer integration
- 84C Build: skipped because no consumer was proven

The existence of a service is not sufficient justification for creating a
router or endpoint.

## 7. Final Architecture Boundary

Observation Intake is an internal, non-executing action-layer capability with
no caller. It is the first safe producer for the closed Milestone 83
Observation Record Store, but no production workflow currently invokes it.

## 8. Non-Executing Contract

Observation Intake does not:

- execute tools;
- collect evidence;
- automatically capture observations;
- call real apply;
- call rollback;
- call policy or execution gates;
- call protected/core route functions;
- perform network calls;
- inspect external state;
- infer observations;
- use an LLM for matching;
- fabricate plan_step_id;
- fabricate collector_contract_id;
- fabricate evidence_items;
- modify external system state.

It only processes caller-supplied values.

## 9. Input Contract

Required top-level fields:

- plan_step_id
- collector_contract_id
- evidence_items

Optional top-level field:

- metadata

Evidence item fields:

- evidence_item_id: optional
- target: required
- observed_value: required
- expected_value: required
- metadata: optional

Forbidden generated/internal fields are rejected at the top level and inside
each evidence item. This closure record does not redefine or expand the
service contract.

## 10. Strict Matching Contract

- normalized(value) = json.dumps(value, sort_keys=True)
- default=str is not used.

No type coercion, no fuzzy matching, no semantic matching, no numeric
tolerance, no LLM judgment, and no external verification.

Distinctions:

- 1 != 1.0
- "1" != 1
- True != 1
- False != 0

Serialization failures raise ValueError with the cause preserved.

## 11. Validation Atomicity

- All validation and record preparation occurs before the first queue save.
- Any validation, normalization, or builder failure results in zero saves.
- Validation failures create zero persisted records.
- No partial creation occurs for validation failures.
- No orphan records occur for validation failures.

This is not storage-level transactionality; see the next section.

## 12. Persistence Transactionality Limitation

- The queue persists one record per file.
- No batch transaction exists.
- No staging exists.
- No atomic multi-record commit exists.
- No rollback or cleanup API exists.
- A later save failure may leave earlier records persisted.
- Persistence exceptions propagate.
- No completed envelope is returned on failure.
- No cleanup or rollback is attempted.
- Queue-level transactionality remains deferred.

## 13. Metadata, Context, and Unknown-Field Decisions

- Top-level metadata: validated but not persisted
- Per-item metadata: persisted
- Unknown non-forbidden fields: tolerated and ignored
- Context: accepted but ignored
- Context forwarding: not performed
- context_metadata: remains empty at creation
- Forbidden field names appearing inside metadata: not recursively rejected
  solely by name

## 14. Observation Status and Lifecycle Decision Semantics

- Intake status: matched or mismatched
- Queue lifecycle decision at creation: None
- Service envelope status: completed

No `completed` status is added to Observation Record statuses.

The Milestone 83 status set remains: pending, matched, mismatched, error,
cancelled.

The intake service does not call update or cancellation lifecycle functions.
Milestone 83 lifecycle semantics remain unchanged.

## 15. Existing Observation Record API Relationship

The existing external API:

- POST /observation-records
- GET /observation-records
- GET /observation-records/{observation_id}
- PATCH /observation-records/{observation_id}/status
- POST /observation-records/{observation_id}/cancel

These produce exactly four OpenAPI path entries because methods share paths.

Observation Intake differs because it is:

- batch-oriented;
- strict matched/mismatched classification;
- validation-atomic;
- protected against caller-supplied generated/internal fields;
- intended as an internal producer capability.

The existing Observation Record API remains the only external store API. No
duplicate Observation Intake endpoint was added. Future API exposure requires
a proven consumer and separate planning.

## 16. Router/API Decision

- Router/API justified now: no

Reasons:

- no real consumer exists;
- no current workflow possesses the complete intake contract;
- a speculative endpoint would create a second external persistence path;
- authorization and consumer ownership are undefined;
- the finalized design explicitly requires consumer proof.

No router, endpoint, or API model was created.

## 17. Preserved Protected-Core Boundaries

Locked baseline:

- OpenAPI: 304 paths / 108 schemas
- Observation paths: exact 4
- Observation operation IDs: exact 5
- api_server.py: 8 protected/core @app routes / 23 include_router calls /
  zero direct /action/* routes

Also:

- Observation Intake router: absent
- Observation Intake endpoint: absent
- Observation Intake API model: absent
- Runtime bridge: absent
- Automatic observation capture: absent
- Production importer: none
- Milestone 83 builder/queue/service: unchanged
- Milestone 83 lifecycle: unchanged
- Protected Core Interface: unchanged

## 18. Test and Validation Baseline

Verified pre-84D baseline:

- Focused Observation Intake tests: 145 passed
- Design-lock tests: 14 passed
- Boundary tests: 17 passed
- Combined: 176 passed
- Milestone 83 observation regression: 294 passed
- Milestone 83 closure tests: 9 passed
- PROGRESS consistency: 55 passed
- Full suite before 84D: 2073 passed
- OpenAPI: 304 / 108
- api_server: 8 / 23 / 0
- Drift: 0

The 84D Build adds a doc-only closure lock test; the final total is recorded
after Build validation.

## 19. Deferred Work

1. Real evidence collection.
2. Tool-driven observation collection.
3. Automatic observation capture.
4. Execution-loop Observe-stage wiring.
5. Verification consumer integration.
6. Critic and Repair runtime linkage.
7. Timeline or memory-learning integration.
8. A real internal consumer for Observation Intake.
9. Router/API exposure only after consumer proof.
10. Queue-level batch transactionality, if ever required.
11. Access-control and authorization design for any future external intake.
12. Mapping future collector outputs into the intake evidence_items shape.

None of the deferred items is described as completed.

## 20. Future Consumer-Proof Gate

Before any future integration, proof is required of:

- exact caller;
- exact module and function;
- exact invocation point;
- actual plan_step_id source;
- actual collector_contract_id source;
- actual evidence_items source;
- caller-supplied observed_value;
- caller-supplied expected_value;
- valid dependency direction;
- non-execution preservation;
- failure propagation behavior;
- persistence-isolation tests;
- no speculative API exposure.

For any future router/API milestone, additionally require:

- a specific external consumer;
- why the existing Observation Record API is insufficient;
- request and response ownership;
- authentication and authorization analysis;
- intentional OpenAPI changes;
- intentional include_router changes;
- protected-core regression plan.

## 21. Milestone 85 Eligibility

- Milestone 85: not currently defined
- Milestone 85 may not start automatically.
- After 84D Finalization, the required next action is: human/project-manager
  review and acceptance of the 84D Finalization.
- Only after that review may a future Milestone 85 Plan be created.
- The future Milestone 85 Plan must determine: its actual objective; whether
  it depends on any deferred Observation Intake work; whether additional
  prerequisites are required.

This closure record does not define the content of Milestone 85.

## 22. Milestone 84 Closure Declaration

- Milestone 84 is not considered closed until 84D Finalization is accepted.
- The 84D local Build creates the closure artifact but does not close the
  milestone.
- Milestone 84 may be declared closed only after: closure document
  validation; closure lock tests; focused and full test validation;
  implementation commit; milestone tag; successful push; post-push
  verification; finalization acceptance.
