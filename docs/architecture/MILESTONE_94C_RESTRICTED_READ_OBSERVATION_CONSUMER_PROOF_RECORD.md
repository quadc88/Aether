# Milestone 94C Restricted-Read Observation Consumer-Proof Decision Record

Classification: Architecture / integration decision record

Documentation-only. No runtime implementation.

This record is authoritative for Milestone 94C until explicitly revised by a
future separately authorized architecture milestone.

## 1. Purpose

Milestone 94C records the accepted consumer-proof decision for the Milestone
94B restricted-read Action -> call-local Observation -> capability-specific
Verification slice. It records why the existing Observation Intake contract
cannot truthfully consume that slice yet.

## 2. Scope

This Build adds only this decision record, a static design-lock test, and the
operative `PROGRESS.md` ledger update. It adds no production code, runtime
wiring, Observation Intake caller, API, configuration, schema, queue, store,
aggregator, Critic, Repair, Learning, or generic capability.

## 3. Current Milestone Authority

- Milestone 94: OPEN
- Milestone 94A: FINALIZED / DURABLE BOUNDARY
- Milestone 94B: FINALIZED / GIT-DURABLE / PM-ACCEPTED
- Milestone 94C: consumer-proof decision Build complete locally only after this
  Build passes
- Milestone 94D: NOT DEFINED

The accepted Plan binding is `M94C_RUNTIME_BRIDGE_NOT_JUSTIFIED` with selected
outcome `C_NOT_YET_COMPATIBLE`. Observation Intake remains
`DEFER_FIRST_SLICE`.

## 4. M94B Proven Producer

The proven M94B capability is exactly one governed capability:
`file.restricted_read`.

Its Phase-2 path is:

`POST /action/file/execute-approved-read` ->
`file_routes.execute_approved_read` ->
`handle_restricted_file_read_execution` ->
`execute_approved_restricted_read` -> dedicated restricted-read bridge ->
reader -> call-local `RestrictedReadObservation` -> capability verifier ->
response.

M94B supplies execution-attempt, approval, optional session, target,
capability, private scope, authorization, reader, truncation, privacy, not-found,
changed-during-read, error, and capability-verification fields. Its
`RestrictedReadObservation` is call-local. There is no persistent Observation
Record from 94B and no current Observation Intake production caller.

## 5. Existing Observation Intake Contract

The public function is `handle_observation_intake(request, context=None)`.
It requires non-empty `plan_step_id`, non-empty `collector_contract_id`, and a
non-empty `evidence_items` list. Each item requires `target`,
`observed_value`, and `expected_value`; `evidence_item_id` and per-item
`metadata` are optional.

Intake strictly compares `json.dumps(value, sort_keys=True)` values. Equal
normalized values are `matched`; otherwise they are `mismatched`. Validation,
normalization, and record building happen before persistence. Validation
failures save nothing; storage has no multi-record transaction or rollback.
Top-level metadata is validated but not copied. Per-item metadata is persisted.
The service context is accepted but ignored.

The existing persistent path is the private `observation_records/` directory,
with one JSON record per file. Existing API routes and models are unchanged.

## 6. Producer-to-Consumer Mapping Result

The mapping is not lossless and cannot be made truthful with a thin dictionary
adapter.

| Intake field | 94B source | Lossless | Fabrication | Semantic mismatch |
|---|---|---:|---:|---:|
| `plan_step_id` | none | NO | YES if substituted | YES |
| `collector_contract_id` | none | NO | YES if aliased | YES |
| `evidence_items` | one reader result / call-local observation | NO | YES if invented | YES |
| `target` | normalized target / reader path | YES as a factual path source | NO | NO, but privacy review required |
| `observed_value` | result, status, or content | NO as the existing value contract | YES if wrapped | YES |
| `expected_value` | none | NO | YES | YES |
| per-item `metadata` | selected safe fields only | NO complete mapping | YES if synthesized | YES if raw internals are carried |

Therefore the required provenance and classification contract is not proven.

## 7. `collector_contract_id` Decision

`COLLECTOR_CONTRACT_MAPPING: NOT_PROVEN`

94B has no collector-contract object or truthful collector-contract identity.
The following MUST NOT be substituted: `approval_id`,
`execution_attempt_id`, `session_id`, `capability_id`, `task_binding`, or
scope identity. Approval identity, attempt identity, capability identity, and
scope identity are different semantics from a declared collector contract.

## 8. `plan_step_id` Decision

`PLAN_STEP_MAPPING: NOT_PROVEN`

94B Phase-2 has no executor-plan-step identity. The following MUST NOT be
synthesized: `restricted_read`, `phase2`, `step1`, `capability_id`,
`approval_id`, `execution_attempt_id`, or `session_id`.

## 9. `expected` / `observed` Decision

`EXPECTED_OBSERVED_MAPPING: NOT_PROVEN`

94B contains no authoritative expected-value source. Do not invent `file should
exist`, `read should succeed`, `content should equal X`, expected status
success, or expected file metadata. A reader result and a capability verifier
status do not supply the existing Intake expected-versus-observed contract.

## 10. Verification-Layer Separation

`aether/verification/restricted_file_read.py` is capability-specific
deterministic Verification over one restricted-read result. Milestone 85
future Verification Aggregation is a future multi-observation,
lifecycle-level concept. The restricted-read verifier is not an aggregator,
does not consume Observation Records, and does not trigger Critic or Repair.

## 11. Observation Classification vs Capability Verification

Observation Classification is strict equality of supplied observed and expected
values. Capability Verification evaluates authorization, path, privacy,
bounded-read, and TOCTOU conditions. No direct semantic conversion is
authorized:

- `VERIFIED_SUCCESS != matched`
- `VERIFIED_PARTIAL != matched/mismatched`
- `DENIED != mismatched`
- `NOT_FOUND != mismatched`
- `CHANGED_DURING_READ != mismatched`
- `INTERNAL_ERROR != mismatched`

## 12. Ownership and Dependency Direction

- Action executes the restricted read.
- Observation captures a factual capability result.
- Verification evaluates that capability result.
- Observation Intake persists/classifies only when its contract is truthful.
- Lifecycle Decision remains queue-owned.
- Core Coordination transports execution/lifecycle state.
- Core Governance authorizes execution.
- Thinking is proposal-only.
- Persistence never creates execution authority.

The current 94B dependency direction remains isolated and valid. No consumer
direction from 94B into Observation Intake is proven.

## 13. Persistence and Privacy Decision

`Privacy-safe persistence: NOT_PROVEN`.

The 94B observation remains call-local. Future Observation persistence MUST NOT
automatically include raw file content, returned content, secret matches,
credentials, tokens, API keys, private keys, `RestrictedReadScope`,
`approved_root`, bound function, scope lock, scope dispatch state, raw reader
metadata, or authorization internals. Normalized private target/path must not
be persisted by default.

Any future persistent representation requires a separately authorized
data-minimization, retention, visibility, and access-control contract. Existing
privacy denial remains fail-closed.

## 14. Status Mapping Decision

For `VERIFIED_SUCCESS`, `VERIFIED_PARTIAL`, `DENIED`, `NOT_FOUND`,
`CHANGED_DURING_READ`, and `INTERNAL_ERROR`:

- Durable Observation Record now: NO
- Observation Intake now: NO
- Lifecycle transition: NONE
- Critic: NO
- Repair: NO
- Learning: NO
- Memory write: NO

All remain capability-local until another contract is authorized.

## 15. Observation Lifecycle Preservation

Existing Observation behavior is unchanged:

- `VALID_STATUSES` is exactly `pending`, `matched`, `mismatched`, `error`,
  `cancelled`.
- Intake-created records are `matched` or `mismatched`.
- Lifecycle decision at intake is `None`.
- Later update/cancel operations are pending-only.
- `decision` is queue-owned lifecycle metadata.
- `completed` is a service-envelope status only.
- Existing Observation Record API is unchanged.

## 16. API Decision

`NEW API: NO`.

Do not create or immediately implement `POST /observation-intake`, a second
restricted-read endpoint, a generic observation executor, or a generic tool
executor. Future API work requires a separately proven external consumer need.

## 17. Generic Capability Freeze

Preserve exactly `file.restricted_read`. No second capability, arbitrary tool
ID, generic Action bridge, generic `execute_tool` execution authority, generic
`/chat` execution authority, or generic approval-to-execute pipeline is
authorized.

## 18. Aggregator / Critic / Repair / Learn Freeze

Verification Aggregation, Critic triggering, Repair triggering, automatic retry,
alternate-path selection, Learning, episodic-memory persistence,
semantic-memory persistence, automatic ASC mutation, background execution, and
scheduler integration are NOT IMPLEMENTED and NOT AUTHORIZED.

## 19. Rejected Integration Models

- Outcome A - DIRECT INTAKE BRIDGE: REJECTED.
- Outcome B - THIN ADAPTER: REJECTED; dictionary reshaping cannot create
  missing semantics.
- Outcome D - CONTRACT REVISION REQUIRED: possible future direction, but NOT
  authorized by 94C itself.

## 20. Selected Outcome

Outcome C - Existing Observation Intake Contract Not Yet Compatible: SELECTED.

The current Observation Intake production caller is NONE. The current
restricted-read Observation is call-local. The current persistent Observation
Record from 94B is NONE. Observation Intake remains `DEFER_FIRST_SLICE`.

## 21. Runtime Bridge Decision

M94C runtime bridge: NOT JUSTIFIED.

No runtime wiring is authorized by this record. No production write set exists
for 94C beyond this documentation decision Build.

## 22. Required Future Prerequisites

Before any future restricted-read -> Observation Intake integration, a
separately authorized milestone must answer:

1. Whether restricted-read results should become durable Observation Records.
2. What real object owns `collector_contract_id`.
3. What real plan/action/goal object owns `plan_step_id`.
4. What authoritative source supplies `expected_value`.
5. What constitutes one evidence item.
6. What redacted observed representation is safe to persist.
7. What downstream consumer needs the persistent record.
8. Whether Verification Aggregation is required.
9. Retention and access-control rules.
10. Failure and persistence atomicity semantics.
11. Lifecycle ownership for capability outcomes.
12. Producer/consumer isolation tests.

No runtime implementation may precede these answers.

## 23. Future Contract-Revision Gate

Outcome D remains a possible future direction only if a separately authorized
contract-revision milestone proves that the historical collector-bound
Observation contract must be generalized. This record performs no revision.

## 24. Milestone 94 Closure Relationship

Milestone 94 remains OPEN. This Build does not close Milestone 94.
Milestone 94 closure requires separate PM review after 94C finalization.
No Milestone 94D is defined.

## 25. Architectural Invariants Preserved

The Build preserves the one-mind model, the separation of Action, Observation,
Verification, Governance, Coordination, Thinking, and Persistence ownership;
the Milestone 85 boundary; the single governed capability; privacy fail-closed
behavior; existing Observation statuses and lifecycle; existing API and
OpenAPI; and the prohibition on unproven consumers and fabricated provenance.

## 26. Authoritative-Until-Revised Clause

This record is authoritative for Milestone 94C until explicitly revised by a
future separately authorized architecture milestone. It does not authorize a
runtime bridge, Observation Intake caller, API, aggregator, Critic, Repair,
Learning, generic capability, commit, tag, push, or closure of Milestone 94.
