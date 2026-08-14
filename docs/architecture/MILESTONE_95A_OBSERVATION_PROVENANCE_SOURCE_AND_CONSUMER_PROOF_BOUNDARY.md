# Milestone 95A Observation Provenance Source and Consumer-Proof Boundary

Classification: PLAN / CONTRACT / CONSUMER-PROOF ONLY

This is a documentation and static design-lock Build. It does not implement a
runtime bridge, an Observation Intake caller, a persistent Observation Record,
an API, a capability, an aggregator, Critic, Repair, Learning, retry, or
background execution.

## 1. Durable Parent Authority

Milestone 94 is externally CLOSED / GIT-DURABLE / PM-ACCEPTED.

- closure commit: `6ecc5dd254335e8f6d0020050db0674d96a9fd05`;
- closure tag: `milestone-94-governed-read-only-action-vertical-slice-closure`;
- 94A: FINALIZED / DURABLE BOUNDARY;
- 94B: FINALIZED / GIT-DURABLE / PM-ACCEPTED;
- 94C: FINALIZED / GIT-DURABLE / PM-ACCEPTED;
- 94D: FINALIZED / GIT-DURABLE / PM-ACCEPTED.

Milestone 95 is authorized for 95A Plan only. M95B is NOT AUTHORIZED.

The parent direction remains:

```text
real Action
  -> factual Observation
  -> truthful provenance
  -> durable evidence eligibility
  -> later consumer-proof integration
```

No provenance shortcut may turn an approval, execution attempt, session, or
capability identifier into a different semantic identity.

## 2. Exact 95A Question and Answer

94C incompatibility remains `C_NOT_YET_COMPATIBLE`.

Question:

> What is the minimum truthful provenance contract that must exist before a
> > call-local Action Observation may be admitted into the existing Observation
> > Intake / Observation Record system?

Answer:

The minimum contract must identify the actual planned step and collector
contract that own the observation, bind the observation to the actual Action
attempt and capability target, preserve the capability-specific verification
relationship, provide a predeclared expectation or explicitly prove that the
consumer contract is not applicable, and define a privacy-safe persistable
representation with retention and access rules. The current restricted-read
producer supplies none of the required plan-step, collector-contract,
expectation, stable-observation, downstream-consumer, or privacy-persistence
semantics. Therefore no call-local restricted-read Observation may currently be
admitted to Observation Intake.

## 3. Current Producer Inventory

The actual current restricted-read chain is:

```text
POST /chat/restricted-read/resume
  -> handle_restricted_read_chat_resume
  -> ApprovedReadExecutionAttemptRequest
  -> execute_approved_restricted_read
  -> fresh Core Governance authorization
  -> private one-shot Strategy C scope
  -> dispatch_restricted_read
  -> read_restricted_file
  -> Action result
  -> call-local RestrictedReadObservation
  -> verify_restricted_file_read
  -> capability-specific response
```

The current factual values are:

| Stage | Factual values proven by current source |
|---|---|
| Chat resume input | `approval_id`, exact `request_text`, optional `session_id` |
| Parsed Action request | capability `file.restricted_read`, target, `read_only`, bounded `max_chars` |
| Approval record | `approval_id`, request payload, fingerprint, created/updated timestamps, decision state, optional session metadata, consumed execution-attempt identity |
| Execution attempt | fresh internal `execution_attempt_id`, not returned in the response |
| Governance scope | capability, bound reader function, normalized target, approved root, read-only permission, max chars, execution attempt, session, optional `task_binding` |
| Current context | `session_id` is passed; no task or plan identity is supplied, so `task_binding` is normally `None` |
| Reader result | file-access `id`, created/updated timestamps, timezone, path, normalized path, allowed, status, reason, size, extension, content, regular-file flag, truncation, max chars, metadata, read-started, changed-during-read, privacy-filtered |
| Call-local Observation | reader status, normalized target, regular-file flag, extension, size, content only on success, truncation, reader file-access id as `action_id`, privacy-filtered flag |
| Capability Verification | `VERIFIED_SUCCESS`, `VERIFIED_PARTIAL`, `DENIED`, `NOT_FOUND`, `CHANGED_DURING_READ`, or `INTERNAL_ERROR` |
| Response | approval id/state, execution-attempt status, capability verification status, dispatch flag, bounded content on successful verification, truncation, safe reason, warnings, and `tool_execution_allowed: false` |

The Observation object has no `observation_id`, timestamp, approval id, session
id, execution-attempt id, capability id, task identity, plan-step identity,
collector-contract identity, expected value, or downstream consumer identity.
The Observation `action_id` is the reader's file-access id; current source does
not prove that it is an Action identity or an execution identity.

## 4. Current Consumer Inventory

The existing public Intake function is
`handle_observation_intake(request, context=None)`. It requires:

- non-empty `plan_step_id`;
- non-empty `collector_contract_id`;
- a non-empty `evidence_items` list;
- each evidence item to contain `target`, `observed_value`, and
  `expected_value`.

The existing builder/store contract additionally defines:

- generated `observation_id` and `observed_at`;
- optional `evidence_item_id`, `collector_contract_id`, and metadata;
- statuses `pending`, `matched`, `mismatched`, `error`, and `cancelled`;
- JSON serialization of observed and expected values;
- persistent queue envelope timestamps, lifecycle decision fields, warnings,
  and context metadata.

Intake computes `matched` or `mismatched` by strict equality of
`json.dumps(value, sort_keys=True)` for supplied observed and expected values.
It does not infer an expectation, call an executor, call Verification, or
automatically capture an Observation. Phase A builds all records before Phase B
persists them, but multiple Phase-B writes have no batch rollback.

The existing Observation Record router is a separate CRUD/lifecycle consumer
with four paths and five operation IDs. Its current contract is not a proven
restricted-read producer consumer. There is no current restricted-read caller
of `handle_observation_intake`.

Field semantics in the existing consumer are:

| Consumer field | Semantic role |
|---|---|
| `plan_step_id` | identity/provenance of the executor plan step |
| `collector_contract_id` | identity/provenance of the declared collector contract |
| `evidence_item_id` | downstream evidence-item correlation |
| `target` | subject of the observation |
| `observed_value` | actual value supplied by the producer |
| `expected_value` | predeclared comparison value supplied by the producer/contract |
| `metadata` | per-item supplemental metadata |
| `status` | Observation equality/lifecycle classification |
| `observation_id` | generated persistent record identity |
| timestamps and queue fields | storage and lifecycle semantics |

## 5. 94C Gap Re-Proof and Field Classification

The current source confirms the following classifications. A classification is
not an authorization to implement a mapping.

| Required field or relationship | Classification | Current proof / gap |
|---|---|---|
| `plan_step_id` | NOT_CURRENTLY_PROVABLE | no executor plan-step object or identity exists in this slice; `task_binding` is not a plan step |
| `collector_contract_id` | NOT_CURRENTLY_PROVABLE | no collector contract object or owner executes this slice |
| `expected_value` | NOT_CURRENTLY_PROVABLE | no predeclared expected file/content/state value exists |
| `observed_value` | NOT_CURRENTLY_PROVABLE | raw content/status/metadata exist, but no safe Intake observed-value representation is defined |
| target identity | PROVEN_EXISTING_SOURCE | normalized target/path exists; persistence privacy and redaction are not proven |
| Action identity | NOT_CURRENTLY_PROVABLE | capability and reader file-access id exist, but neither is proven to be an Action identity |
| Observation identity | NOT_CURRENTLY_PROVABLE | the dataclass is call-local and has no stable observation id |
| verification relationship | PROVEN_EXISTING_SOURCE | current coordination passes the same Action result and Observation to the capability verifier; the relationship is call-local only |
| privacy-safe persistable payload | NOT_CURRENTLY_PROVABLE | raw content, private paths, metadata, and authorization internals lack a persistence contract |
| downstream consumer identity | NOT_CURRENTLY_PROVABLE | no current durable restricted-read Observation consumer is proven |

The missing fields require new contracts before any truthful Intake admission;
aliases are not derivations. In particular, `approval_id` is not
`plan_step_id`, `execution_attempt_id` is not `collector_contract_id`, and a
reader file-access id is not automatically an Action or Observation identity.

## 6. Producer-to-Consumer Compatibility Matrix

| Consumer requirement | Consumer meaning | Producer source | Source truthfulness | Lossless mapping | New contract | Privacy risk | Decision |
|---|---|---|---|---:|---:|---|---|
| `plan_step_id` | planned execution-step identity | none; optional `task_binding` is not a plan step | absent | NO | YES | low identity risk, high provenance risk | reject admission |
| `collector_contract_id` | collector owner/contract identity | none | absent | NO | YES | correlation alias risk | reject admission |
| `evidence_items` | one or more contract-owned evidence items | one call-local reader result | incomplete | NO | YES | content/path leakage | no adapter |
| `target` | observed subject | normalized target/path | factual but private | YES as source only | privacy envelope needed | path disclosure | retain only under future policy |
| `observed_value` | actual comparable value | content, status, metadata, truncation | factual but heterogeneous | NO | YES | secrets, size, raw content | no current mapping |
| `expected_value` | predeclared comparison value | none | absent | NO | YES | false expectation risk | no synthesis |
| `metadata` | supplemental producer metadata | reader metadata and authorization internals | mixed/private | NO | YES | internals and paths | whitelist only in future |
| `status` | matched/mismatched equality result | capability verification status | different semantics | NO | YES if ever translated | false classification | preserve capability status separately |
| `observation_id` | durable record identity | none; generated by builder only | not producer provenance | NO | YES | identity collision/alias risk | generate only at authorized persistence |

The matrix is semantically incompatible even where individual values are
strings or dictionaries.

## 7. `plan_step_id` Source Proof

Classification: `NEW_PLAN_STEP_CONTRACT_REQUIRED`.

The current execution has a fresh execution attempt and an optional session,
but no planned step object. `task_binding` is only an optional field in the
private Governance scope and is not populated by the current resume path. The
capability name, `phase2`, `step1`, approval id, execution-attempt id, session
id, and task binding must not be relabeled as `plan_step_id`.

## 8. `collector_contract_id` Source Proof

Classification: `NEW_COLLECTOR_CONTRACT_REQUIRED`.

The current restricted-read slice does not execute under a collector contract.
It has no collector object, contract owner, declared collection plan, or
consumer identity. Approval id, execution-attempt id, session id, capability id,
or scope identity must not be used as `collector_contract_id`.

## 9. `expected_value` Semantics

The current Intake contract treats `expected_value` as a supplied,
predeclared value for strict equality. Restricted-read verification instead
checks authorization, path containment, privacy, regular-file state, size and
read bounds, TOCTOU identity, decoding/read safety, and truncation.

These are not equivalent expectations:

- expected file existence is not an expected content value;
- expected readable state is not an expected observation;
- expected content is not supplied by this Action;
- expected privacy state is a policy condition, not an observed value;
- expected truncation behavior is not predeclared by the current Intake caller;
- expected immutable snapshot is not established by best-effort TOCTOU checks;
- verification completion is not an Intake equality expectation.

Classification: `CURRENT_INTAKE_EXPECTATION_MODEL_INCOMPATIBLE`.

No expectation may be synthesized after reading the file.

## 10. `observed_value` Semantics and Privacy

`RestrictedReadObservation` can hold raw bounded content on a successful read,
plus status, target, size, extension, truncation, reader id, and privacy flag.
That shape is factual for the call, but it is not a safe durable
`observed_value` contract. A blocked, missing, changed, or error result has
different semantics from a successful content value.

The current source proves no safe persistence choice among raw content,
redacted content, metadata-only, digest-only, or structured evidence reference.
Raw content may contain secrets; normalized paths may disclose private targets;
metadata may contain authorization or scope internals; partial content has
retention and reassembly concerns; and error details may disclose sensitive
path state. The current reader's privacy filter prevents disclosure for this
Action response but does not define durable Observation redaction, retention,
visibility, or access control.

Classification: `REQUIRES_SEPARATE_PRIVACY_CONTRACT` and, under the current
contract, `NOT_SAFE_TO_PERSIST`.

No persistence is authorized by 95A.

## 11. Verification Relationship

The six capability-specific statuses are:

`VERIFIED_SUCCESS`, `VERIFIED_PARTIAL`, `DENIED`, `NOT_FOUND`,
`CHANGED_DURING_READ`, and `INTERNAL_ERROR`.

Existing Intake classification is not sufficient. A translation layer from
these statuses to `matched` or `mismatched` would be untruthful because Intake
classification means strict equality of expected and observed values, while
capability Verification means authorization and read-integrity evaluation.

The current truthful relationship is:

- preserve capability Verification separately;
- do not collapse `VERIFIED_SUCCESS` into `matched`;
- do not collapse `VERIFIED_PARTIAL` into `matched` or `mismatched`;
- do not collapse `DENIED`, `NOT_FOUND`, `CHANGED_DURING_READ`, or
  `INTERNAL_ERROR` into `mismatched`;
- do not treat the capability verifier as Verification Aggregation;
- do not trigger Critic, Repair, or Learning.

The existing Intake model is incompatible with this producer until a new
contract defines both the provenance and the classification relationship.

## 12. Privacy-Safe Persistence Proof

Classification: `NOT_SAFE_TO_PERSIST` under existing contracts.

Current unresolved persistence questions are:

- secret detection beyond the current disclosure filter;
- raw-content retention and deletion;
- redaction and whether redaction is itself evidence;
- normalized path privacy and approved-root disclosure;
- size bounds, truncation, and partial-read semantics;
- changing-file and TOCTOU representation;
- safe error and denial payloads;
- retention, lifecycle, visibility, and access-control ownership.

The current file-access audit excludes content, metadata, and path from its
governed-chat audit record, but that is not an Observation Record contract and
does not establish a durable provenance envelope. A future envelope may use
metadata-only, digest-only, or a structured evidence reference, but 95A does
not select or implement that representation.

## 13. Consumer-Proof Gate

Candidate consumer inventory:

| Candidate | Classification | Evidence |
|---|---|---|
| capability Verification | PROVEN_CURRENT_CONSUMER for call-local producer output only | current coordinator directly invokes the restricted-read verifier |
| Observation Intake / Observation Record | NOT_JUSTIFIED as a restricted-read durable consumer | existing contract exists, but no restricted-read caller and semantic mappings are missing |
| Verification Aggregation | NOT_IMPLEMENTED | future multi-observation lifecycle concept; no current restricted-read consumer |
| Critic | NOT_IMPLEMENTED | no current Observation Record consumer proven |
| Repair | NOT_IMPLEMENTED | no current Observation Record consumer proven |
| Learn | NOT_IMPLEMENTED | no current Observation Record consumer proven |
| Report or audit | NOT_JUSTIFIED | file-access audit is separate and not an Observation Record consumer |
| task continuation or ASC context | NOT_IMPLEMENTED | no current durable restricted-read consumer identity |

Current proven durable consumer: NONE.

Because no current durable consumer exists, durable persistence and Intake
admission remain deferred. No Aggregator, Critic, Repair, or Learning shortcut
is permitted.

## 14. Candidate Contract Models

### Model A - Adapt directly to existing Intake

Rejected. It would require false aliases for plan-step and collector identity,
invent an expectation, and collapse capability statuses into equality statuses.

### Model B - Minimal Observation Provenance Envelope

Justified as the minimum future contract foundation, not as runtime
authorization. The envelope must be owned by a real producer/plan/collector
contract and explicitly bind the Action attempt, capability, target identity,
Observation identity, capability Verification, privacy-safe payload reference,
and downstream consumer. It avoids relabeling existing IDs and keeps the
existing Intake contract unchanged until semantic compatibility is proven.

Truthfulness: YES only after each owner is defined. Architecture fit: YES.
Privacy: requires an explicit envelope policy. Identity semantics: preserves
distinct identities. Future reuse: high. Coupling: bounded upstream contract.
Migration cost: future, separately authorized. Consumer proof: still required.

### Model C - Capability-specific durable evidence record

Not justified yet. It could preserve capability statuses and privacy-specific
payloads, but no durable consumer, retention contract, or evidence-record owner
is currently proven. It would add persistence before consumer proof.

### Model D - Revise Observation Intake

Not justified yet. The existing Intake contract is used by current callers and
its strict equality semantics are internally coherent. No source evidence
proves that it should be generalized for restricted-read capability results.

### Model E - Keep Observation call-local

Required current runtime containment. It preserves the truthful current slice
until a real consumer and provenance contract exist, but it is not itself a
proven provenance foundation for future persistence.

## 15. Selected Model and Runtime Decision

Selected model: `MODEL_B_JUSTIFIED` as a future contract foundation only,
combined with Model E as the current runtime containment boundary.

Runtime decision: `M95_PROVENANCE_FOUNDATION_REQUIRED_BEFORE_RUNTIME`.

No runtime bridge is justified. No 95B runtime plan may introduce an Intake
caller, persistence, or consumer integration until the provenance envelope,
privacy contract, expectation/classification semantics, and real consumer are
separately proven and authorized.

## 16. Explicit Deferred Boundaries

The following remain outside 95A and are not assigned automatically to M95B:

- Observation Intake integration or caller;
- persistent Observation Record;
- provenance envelope runtime implementation;
- `plan_step_id` producer contract;
- `collector_contract_id` producer contract;
- expected-value contract;
- privacy-safe durable payload, redaction, digest, or evidence reference;
- Verification Aggregation;
- Critic;
- Repair;
- Learning;
- second governed capability;
- generic capability execution;
- generic `/chat` executor;
- automatic retry;
- background execution;
- new API, schema, operation ID, or route.

M95B: NOT AUTHORIZED.

## 17. Architecture and Interface Safety

The one persistent digital intelligence, AetherOS environment/body/world, one
ASC architecture framework, canonical Execution Loop, and stage ownership are
unchanged:

```text
Receive Goal -> Understand -> Think -> Plan -> Act -> Observe -> Verify
-> Critic -> Repair -> Learn -> Report
```

Thinking proposes. Governance authorizes. Verification supplies evidence. Action
executes only within authorization. Time provides context, not authority.
Resource Observation reports. Resource Governance decides.

There is no generic `/chat` execution authority. OpenAPI remains 306 paths / 112
schemas; `api_server` remains 8 direct `@app` routes / 23 routers / 0 direct
`/action/*` routes; operation IDs remain `resume_restricted_read_chat` and
`execute_approved_read`. No API, schema, operation ID, capability, or
production file is changed.

## 18. No Implementation Authorization

This record does not authorize runtime code, persistence, API work, a bridge,
an Intake caller, Aggregation, Critic, Repair, Learning, Git lifecycle, or
Milestone 95B. It is a source-and-consumer proof boundary only.

95A status during Build: COMPLETE LOCALLY / PENDING PM REVIEW.
