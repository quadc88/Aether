# Milestone 95C Restricted-Read Durable Consumer Identity & Use-Case Proof Boundary

Classification: PLAN / CONSUMER-PROOF / OWNERSHIP DECISION ONLY

This record audits whether a real current downstream consumer requires durable
restricted-read Observation or provenance. It does not implement a provenance
envelope, Observation Intake caller, persistence, an Observation Record, an API,
a schema, a route, an operation ID, Verification Aggregation, Critic, Repair,
Learning, retry, background execution, a second capability, or generic
execution. It does not authorize Git lifecycle or M95D.

## 1. Durable Predecessor Authority

- Milestone 94: CLOSED / GIT-DURABLE / PM-ACCEPTED.
- Milestone 95: OPEN.
- Milestone 95A: FINALIZED / GIT-DURABLE / PM-ACCEPTED.
- M95A commit: `7dd77c7aff80aa2f30e25361e74bc73b51148ebc`.
- M95B: FINALIZED / GIT-DURABLE / PM-ACCEPTED.
- M95B commit: `1f2dc79c6af732a46a59964514059c14e41b20da`.
- M95B tag: `milestone-95B-minimal-observation-provenance-envelope-contract-foundation`.

M95B facts remain immutable for this audit:

- future provenance foundation: `MODEL_B_JUSTIFIED`;
- current runtime containment: `Model E`;
- runtime decision: `M95_PROVENANCE_FOUNDATION_REQUIRED_BEFORE_RUNTIME`;
- preferred payload direction: `D_METADATA_PLUS_STRUCTURED_EVIDENCE_REFERENCE`;
- Intake compatibility: `E_COMPATIBILITY_REMAINS_UNPROVEN`;
- current durable restricted-read consumer: `NONE`;
- `plan_step_id`: `NOT_CURRENTLY_PROVABLE` / `OWNER_NOT_YET_DEFINED`;
- `collector_contract_id`: `NOT_CURRENTLY_PROVABLE` / `OWNER_NOT_YET_DEFINED`;
- Observation identity: `NOT_CURRENTLY_PROVABLE` / `OWNER_NOT_YET_DEFINED`;
- privacy-safe persistent payload: `NOT_SAFE_TO_PERSIST`.

## 2. Exact M95C Question and Answer

Question:

> Does Aether currently have a REAL downstream consumer whose purpose genuinely
> > requires a durable restricted-read Observation / provenance envelope?

Answer: No current durable consumer is source-proven. The current call-local
Observation and capability-specific Verification are sufficient for the present
restricted-read slice. Durable restricted-read Observation is not presently
justified merely because storage, reporting, memory, ASC, or future loop terms
exist in the architecture.

Selected outcome:

`D_NO_DURABLE_CONSUMER_CURRENTLY_JUSTIFIED`

Runtime consequence:

`BLOCKED`

This is a consumer-proof decision, not a runtime deficiency finding. A future
consumer may be justified only by a separate source-backed plan that proves all
qualification fields and separately authorizes implementation.

## 3. Source Inventory and Current Restricted-Read Chain

The current governed restricted-read producer chain is:

```text
POST /chat/restricted-read/resume
  -> handle_restricted_read_chat_resume
  -> ApprovedReadExecutionAttemptRequest
  -> execute_approved_restricted_read
  -> fresh Core Governance authorization
  -> claim approval for a fresh execution_attempt_id
  -> dispatch_restricted_read
  -> read_restricted_file(mode="governed_chat")
  -> factual reader result
  -> call-local RestrictedReadObservation
  -> verify_restricted_file_read
  -> capability-specific response
```

The current source proves a fresh internal execution-attempt identifier,
approval binding, capability `file.restricted_read`, normalized target,
read-only scope, bounded read, factual reader result, a call-local Observation,
and six capability Verification statuses. It does not prove an authoritative
task owner, plan step, collector contract, stable Observation identity, durable
expectation, privacy-safe persistent payload, or durable consumer.

The current source surfaces audited were:

- `aether/core/coordination.py` and the restricted-read execution service;
- `aether/action/services/restricted_file_read_bridge.py`;
- `aether/action/restricted_file_reader.py` and
  `aether/action/restricted_file_read_observation.py`;
- `aether/verification/restricted_file_read.py`;
- `aether/action/services/observation_intake_service.py`;
- `aether/action/observation_record.py`;
- `aether/action/observation_record_queue.py`;
- `aether/action/services/observation_record_service.py`;
- `aether/interface/routers/observation_routes.py`;
- verification verdict/plan and post-apply verification services;
- `aether/core/runtime.py`, `aether/core/loop.py`, and `aether/core/loop_trace.py`;
- Working Memory, episodic, semantic, graph, and Timeline Memory surfaces;
- restricted file-access audit, mutation log, and repair completion reporting;
- the current four core files, M95A record, M95B record, and static locks.

No ASC runtime module or dedicated restricted-read reporting consumer exists.
The architecture defines ASC as a Core Coordination-owned framework, not a
database or automatic persistence target.

## 4. Consumer Qualification Standard

A candidate qualifies only if current source proves all of the following:

1. consumer identity;
2. consumer owner / cognitive organ;
3. real purpose;
4. why call-local Observation is insufficient;
5. why durable state is needed;
6. exact fields consumed;
7. whether raw content is needed;
8. whether metadata/reference is sufficient;
9. Observation identity semantics;
10. Action-attempt binding;
11. Verification relationship;
12. expectation model;
13. access and visibility requirements;
14. retention requirements;
15. deletion requirements;
16. idempotency and replay requirements;
17. failure and cleanup semantics;
18. whether the current producer can truthfully supply the fields;
19. whether the architecture authorizes the relationship.

If a critical requirement is absent, the candidate is `NOT_PROVEN`. A module
does not qualify because it stores JSON, has an ID, is an endpoint, accepts
metadata, appears in the loop, or is named Observation, Verification, Report,
audit, memory, ASC, Critic, Repair, or Learning.

## 5. Candidate Consumer Matrix

| Candidate | Current producer | Current reader/consumer proof | Purpose | Durability required | Required fields | Identity owner | Privacy contract | Retention contract | Compatibility | Decision |
|---|---|---|---|---|---|---|---|---|---|---|
| Observation Intake | caller-supplied generic Intake service | no restricted-read caller; strict Intake requirements only | build and persist caller-supplied equality observations | generic Intake persists, but no restricted-read need | plan step, collector, evidence items, target, observed value, expected value | absent for restricted-read | absent | absent | incompatible | `NOT_PROVEN`; future adapter target only |
| capability Verification | restricted-read Action result and call-local Observation | direct coordinator call is proven | evaluate capability-specific read outcome | no; current verifier consumes call-local output | reader result, Observation, authorization state | call-local verifier relationship | no durable policy | none | separate status vocabulary | current call-local consumer; not durable |
| Core Coordination / task continuation | restricted-read resume request | no active restricted-read continuation reader | continue an authorized task across turns | architecture describes future continuation, current slice does not use one | authoritative task, task context, wake/resume bindings, facts needed later | no current task owner; `session_id` is not `task_id` | absent | absent | not proven | `NOT_PROVEN` |
| Report | response and existing report services | no reader of a future restricted-read envelope | explain outcomes to a human | no current restricted-read report requirement | report-specific evidence and purpose are not defined | no consumer owner | absent | absent | not proven | `NOT_PROVEN` |
| audit / trace | file-access audit, Timeline, mutation log, response-only loop trace | logs exclude or summarize data; no envelope reader | operational review and safe observability | no durable restricted-read envelope need proven | audit fields are not provenance-consumer fields | audit/log owners do not own this consumer | existing filters are not envelope policy | absent | not proven | `NOT_PROVEN` |
| ASC active task context | Core Coordination-owned architecture framework; Working Memory runtime | no current ASC runtime object or later restricted-read reader | hold authoritative task context and references | no restricted-read persistence need proven | task-owned context and approved references | task owner absent in current slice | absent | absent | not proven | `NOT_PROVEN` |
| Verification Aggregation | no implementation | no current consumer | future multi-observation combination | no current need or implementation | future aggregation contract absent | absent | absent | absent | not proven | `NOT_PROVEN` |
| Critic | no restricted-read Observation consumer or trigger | no current reader | future failure analysis | no current need or plan | aggregation and critic inputs absent | absent | absent | absent | not proven | `NOT_PROVEN` |
| Repair | no restricted-read Observation consumer or trigger | no current reader | future plan repair | no current need or plan | critic/repair plan inputs absent | absent | absent | absent | not proven | `NOT_PROVEN` |
| Learning | no restricted-read Observation consumer or trigger | no current reader | future experience and procedure learning | no current need or verified learning contract | verified experience and admission contract absent | absent | absent | absent | not proven | `NOT_PROVEN` |

No matrix row is `PROVEN` as a durable restricted-read consumer.

## 6. Observation Intake Audit

Observation Intake is a generic mechanism for a caller that supplies:

- non-empty `plan_step_id`;
- non-empty `collector_contract_id`;
- non-empty `evidence_items`;
- `target`, `observed_value`, and `expected_value` for each item.

It strictly compares JSON-normalized observed and expected values and persists
through the existing Observation Record queue. It does not capture an
Observation, call an executor, call capability Verification, or infer an
expectation. The current restricted-read path has no Intake caller.

The existing Intake lifecycle (`matched`, `mismatched`, and queue lifecycle
states) is not the six-status capability Verification vocabulary. The following
statuses remain separate and must not be mapped to `matched` or `mismatched`:

```text
VERIFIED_SUCCESS
VERIFIED_PARTIAL
DENIED
NOT_FOUND
CHANGED_DURING_READ
INTERNAL_ERROR
```

M95C does not rewrite Intake or synthesize `expected_value`. Result:

`E_COMPATIBILITY_REMAINS_UNPROVEN`

Observation Intake is `NOT_JUSTIFIED` as a current restricted-read caller and
is only a possible future adapter target after a separate compatibility,
ownership, privacy, and consumer contract.

## 7. Verification Consumer Audit

Capability Verification is a current call-local consumer of the Action result
and call-local Observation. `verify_restricted_file_read` returns exactly:

```text
VERIFIED_SUCCESS
VERIFIED_PARTIAL
DENIED
NOT_FOUND
CHANGED_DURING_READ
INTERNAL_ERROR
```

It does not require a stable durable Observation identity, persistent payload,
or persistent provenance envelope in the current source. Those requirements are
`NOT_PROVEN`, not silently converted to `NO` for a future contract.

Capability Verification is not Verification Aggregation. No current source
requires persistence merely because Verification exists.

## 8. Core Coordination and Task Continuation Audit

The current restricted-read request carries optional `session_id`; the source
does not supply an authoritative `task_id`, plan, or active task continuation
consumer. `execution_attempt_id` is fresh attempt identity and must not be
substituted for task identity. Approval identity and session identity are also
not task identity.

The architecture describes future background continuity bindings including an
authoritative task context, wake condition, expiry, cancellation, checkpoint,
verification criteria, and audit trail. It does not implement a scheduler or a
restricted-read continuation reader. Therefore task continuation is
`NOT_PROVEN`, with runtime persistence `BLOCKED`.

## 9. Report, Audit, Trace, and Timeline Audit

The current loop trace is response-only and not persisted to disk, Timeline,
Memory, Graph, or files. It summarizes safe public stage information and does
not read restricted-read Observation data.

The governed file-access audit intentionally excludes content, metadata, and
path from its audit record. It is an operational audit trail, not a durable
Observation/provenance consumer.

Timeline, mutation log, repair completion reports, and public repair reports
record their own operational events or sanitized repair lifecycle data. None
currently reads a restricted-read provenance envelope or requires one for its
purpose. Writing logs or reports does not prove a downstream consumer.

## 10. ASC, Memory, Aggregation, Critic, Repair, and Learning Audit

ASC is the Authoritative Shared Cognitive Context framework owned by Core
Coordination. The architecture explicitly states that ASC is not a database,
memory tier, scheduler, queue, new organ, or authorization source. No current
ASC runtime module reads a restricted-read Observation after the originating
call.

Working Memory stores current runtime events and optional session context. The
episodic, semantic, graph, and Timeline Memory implementations are general
memory facilities; their existence does not establish a restricted-read
consumer, retention purpose, access contract, or durable field requirement.

Verification Aggregation is not implemented. Critic, Repair, and Learning have
no current restricted-read consumer or authorized trigger. M95C does not wire
any of them.

## 11. Identity and Ownership Truth

The following non-aliasing rules remain binding:

- `approval_id != plan_step_id`;
- `execution_attempt_id != collector_contract_id`;
- file-access id != Action identity unless separately proven;
- reader file-access id != Observation identity unless separately proven;
- `session_id != task_id`;
- `capability_id != collector_contract_id`;
- `capability_id != observation_id`;
- `execution_attempt_id != observation_id`;
- `approval_id != observation_id`.

No placeholder identity satisfies consumer proof. M95C does not assign owners to
`plan_step_id`, `collector_contract_id`, Observation identity, privacy payload,
or consumer identity.

## 12. Architecture Ownership

The existing architecture remains authoritative:

- Aether is one persistent digital intelligence;
- AetherOS is the runtime/body/world;
- Core Governance owns authority and governance;
- Core Coordination owns orchestration and continuity;
- ASC is the Authoritative Shared Cognitive Context framework;
- Time provides context, not authority;
- Resource Observation reports facts;
- Resource Governance decides;
- Thinking proposes;
- Governance authorizes;
- Verification supplies evidence;
- Action executes within authorization.

The distinctions remain explicit:

```text
Observation != Verification
Verification != Aggregation
Aggregation != Critic
Critic != Repair
Repair != Learning
```

Observation does not gain authority, and the provenance envelope is not an
authority source.

## 13. Selected Outcome and Runtime Consequence

Selected outcome:

`D_NO_DURABLE_CONSUMER_CURRENTLY_JUSTIFIED`

Runtime eligibility:

`BLOCKED`

Explicit current consequences:

- Persistent restricted-read Observation: `NOT JUSTIFIED`;
- Observation Intake caller: `NOT JUSTIFIED`;
- provenance envelope runtime: `NOT JUSTIFIED`;
- current call-local Observation: `REMAINS AUTHORITATIVE`;
- current capability Verification: `REMAINS AUTHORITATIVE`;
- current durable restricted-read consumer: `NONE`;
- future runtime persistence: `BLOCKED`.

No runtime deficiency is implied merely by the absence of persistence.

## 14. Explicit Non-Authorization

M95C does not authorize:

- runtime provenance envelope implementation;
- Observation Intake caller;
- Observation Record creation or persistence;
- API, schema, route, or operation ID;
- Verification Aggregation;
- Critic, Repair, or Learning;
- second capability;
- generic execution;
- retry or background execution;
- consumer integration;
- M95D;
- Git lifecycle.

M95C status during Build: COMPLETE LOCALLY / PENDING PM REVIEW.
