# Milestone 95B Minimal Observation Provenance Envelope Contract Foundation

Classification: PLAN / CONTRACT / SOURCE-OWNERSHIP BOUNDARY ONLY

This record defines a future contract foundation. It does not implement an
envelope, a runtime bridge, an Observation Intake caller, persistence, an API,
a capability, a consumer, Aggregation, Critic, Repair, Learning, retry, or
background execution.

## 1. Durable Authority and Scope

Milestone 94 is CLOSED / GIT-DURABLE / PM-ACCEPTED.

- closure commit: `6ecc5dd254335e8f6d0020050db0674d96a9fd05`;
- closure tag: `milestone-94-governed-read-only-action-vertical-slice-closure`;
- Milestone 95 is OPEN;
- Milestone 95A is FINALIZED / GIT-DURABLE / PM-ACCEPTED;
- M95A commit: `7dd77c7aff80aa2f30e25361e74bc73b51148ebc`;
- M95A parent: `6ecc5dd254335e8f6d0020050db0674d96a9fd05`.

M95B is authorized for Plan / Contract / Source-Ownership Boundary only.
M95B does not authorize implementation. M95C is NOT AUTHORIZED.

The immutable 95A conclusions remain:

- `plan_step_id`: `NOT_CURRENTLY_PROVABLE`;
- `collector_contract_id`: `NOT_CURRENTLY_PROVABLE`;
- `expected_value`: `CURRENT_INTAKE_EXPECTATION_MODEL_INCOMPATIBLE`;
- Observation identity: `NOT_CURRENTLY_PROVABLE`;
- privacy-safe persistable payload: `NOT_CURRENTLY_PROVABLE`;
- current durable restricted-read consumer: `NONE`;
- capability Verification consumer: `CALL_LOCAL_ONLY`;
- selected future foundation: `MODEL_B_JUSTIFIED`;
- current runtime containment: `MODEL_E`;
- runtime decision: `M95_PROVENANCE_FOUNDATION_REQUIRED_BEFORE_RUNTIME`.

## 2. Exact Question and Contract Answer

Question:

> What is the minimum truthful Observation Provenance Envelope contract that
> could later bind a real governed Action attempt to a factual Observation,
> capability Verification, privacy policy, and an explicitly proven downstream
> consumer without falsifying existing Observation Intake semantics?

Answer:

The minimum envelope is a versioned, producer-owned contract that preserves
distinct task, plan, plan-step, collector, approval, execution-attempt, Action,
capability, target, Observation, Verification, evidence-item, consumer, and
session identities. It must bind a fresh governed execution attempt to the
actual Action result, the factual Observation, and the capability-specific
Verification relationship. It must contain either a predeclared expectation
variant or an explicit no-applicable-expectation declaration, a privacy and
retention policy, and a real downstream consumer identity with an owned purpose
and access contract.

The envelope is eligible for future durable admission only when every required
owner, semantic relationship, privacy decision, consumer requirement, and
failure/idempotency/persistence gate is proven. A future required slot is not a
current runtime value. Missing owners are recorded as `OWNER_NOT_YET_DEFINED`;
they are never filled with aliases or placeholders.

## 3. Current Source Boundary

The current restricted-read chain is:

```text
POST /chat/restricted-read/resume
  -> handle_restricted_read_chat_resume
  -> ApprovedReadExecutionAttemptRequest
  -> execute_approved_restricted_read
  -> fresh Core Governance authorization
  -> claim approval for execution attempt
  -> dispatch_restricted_read
  -> read_restricted_file
  -> Action result
  -> call-local RestrictedReadObservation
  -> verify_restricted_file_read
  -> capability-specific response
```

The source proves a fresh internal `execution_attempt_id`, approval binding,
capability `file.restricted_read`, normalized target, read-only scope, bounded
read, a factual reader result, a call-local Observation, and six capability
Verification statuses. It does not prove an owned plan, collector contract,
stable Observation identity, expectation contract, privacy-safe durable payload,
or durable consumer.

The existing `handle_observation_intake(request, context=None)` contract requires
non-empty `plan_step_id`, non-empty `collector_contract_id`, non-empty
`evidence_items`, and each evidence item to contain `target`, `observed_value`,
and `expected_value`. It compares strict JSON-normalized values and persists
through the existing Observation Record queue. There is no current
restricted-read caller.

## 4. Identity Separation

These identities are semantically distinct and must never be aliased merely
because their representations are strings or UUIDs:

```text
task_id / task context identity
plan_id
plan_step_id
collector_contract_id
approval_id
execution_attempt_id
action_id
capability_id
observation_id
verification_id / verification relationship
evidence_item_id
consumer_id
session_id
```

Explicit non-aliasing rules:

- `approval_id != plan_step_id`;
- `execution_attempt_id != collector_contract_id`;
- file-access id != Action identity unless separately proven;
- reader file-access id != Observation identity unless separately proven;
- `session_id != task_id`;
- `capability_id != collector_contract_id`;
- `capability_id != observation_id`;
- `execution_attempt_id != observation_id`;
- `approval_id != observation_id`.

`task_binding` is not a plan step. A session is context, not task ownership. A
capability name is not an Observation identity. A generated storage id is not
producer provenance.

## 5. Envelope Field Ownership Matrix

The matrix is a contract decision, not an implementation schema. `Required`
means required for future durable eligibility, not necessarily present in every
call-local object. `Can be absent` describes only a separately declared
non-eligible or explicitly non-applicable envelope state.

| Field | Semantic meaning; required/optional | Authoritative producer and creation | Current proof / new contract | Persistability and privacy | Consumer requirement / can be absent |
|---|---|---|---|---|---|
| `envelope_version` | Contract version; Required | Envelope contract owner at construction | No current envelope; NEW contract required | Low sensitivity; persist only with eligible envelope | Consumer needs parser version; no for durable eligibility |
| `task_binding` | Task context plus `task_id`; Required for task-scoped durability | Core Coordination from authoritative task context | Session exists, task owner does not; OWNER_NOT_YET_DEFINED | Metadata only after access policy; no private context leakage | Required by task consumer; absent only for explicitly non-task-scoped, non-eligible records |
| `plan_id` | Owning plan identity; Required for planned work | Plan owner | Not supplied; OWNER_NOT_YET_DEFINED | Provenance metadata; persist only under consumer policy | Required when consumer is plan-owned; absent only with explicit non-plan declaration |
| `plan_step_id` | Owning planned step identity; Required | Plan/step owner | NOT_CURRENTLY_PROVABLE; OWNER_NOT_YET_DEFINED | Provenance metadata; no alias permitted | Required for current Intake compatibility; cannot be absent for durable eligibility |
| `collector_contract_id` | Declared collector owner and output contract; Required | Collector contract owner | NOT_CURRENTLY_PROVABLE; OWNER_NOT_YET_DEFINED | Provenance metadata; no alias permitted | Required for current Intake compatibility; cannot be absent for durable eligibility |
| `execution_attempt_id` | One fresh governed attempt; Required | Core Coordination / execution service | Fresh call-local id is proven; durable ownership contract still required | Low-to-moderate correlation sensitivity; retain only under access policy | Required to bind Action attempt; cannot be absent from eligible envelope |
| `action_identity` | Identity of the actual Action invocation; Required | Action owner, separately from reader | Current reader id is not proven Action identity; NEW contract required | Correlation metadata; privacy review required | Required to prove Action binding; cannot be absent for durable eligibility |
| `capability_id` | Governed capability identity; Required | Capability registry / Governance contract | `file.restricted_read` is current source; generic ownership contract required | Low alone, sensitive with target/scope; policy controlled | Required for capability Verification; cannot be absent |
| `target_identity` | Subject/resource addressed by Action; Required | Action capability contract | Normalized target exists; privacy/redaction contract missing | Private path/resource data; persist only under privacy profile | Consumer needs subject identity or approved reference; cannot be absent without explicit opaque-reference semantics |
| `observation_identity` | Stable identity of factual Observation; Required | Observation producer contract | NOT_CURRENTLY_PROVABLE; OWNER_NOT_YET_DEFINED | Correlation metadata; persist only when consumer and policy permit | Required for Verification/evidence correlation; cannot be absent for durable eligibility |
| `observation_timestamp` | Time facts were observed; Required | Observation producer using Time context | Reader timestamps exist, Observation timestamp does not; NEW contract required | Time metadata; persist with provenance | Consumer needs freshness/audit; cannot be absent for durable eligibility |
| `observation_payload_reference` | Reference to approved factual payload representation; Required when payload exists | Observation producer plus privacy contract | No safe representation proven; NEW contract required | Prefer metadata/reference, not raw content; policy required | Consumer needs approved payload or explicit no-payload result; inline raw payload is not required |
| `capability_verification` | Capability-specific verification result object/reference; Required | Capability verifier | Six statuses are current call-local source; durable contract required | Status low sensitivity; reasons/target may be sensitive | Consumer needs status and subject relationship; cannot be collapsed into Intake status |
| `verification_relationship` | Explicit links among verification, Action attempt, Observation, and contract version; Required | Verification contract owner | Relationship is proven call-local only; NEW contract required | Correlation metadata; access controlled | Consumer needs provenance chain; cannot be absent for eligible envelope |
| `expectation_contract` | Expectation variant plus owner and declaration; Required or explicit no-applicable variant | Plan/collector/capability contract owner | Current expected value is absent and incompatible; OWNER_NOT_YET_DEFINED | May contain sensitive target/content policy; privacy controlled | Consumer needs comparison semantics; cannot be silently absent |
| `privacy_profile` | Secret, path, content, redaction, visibility, and access policy; Required | Privacy/Governance owner | Current response filter is not durable policy; NEW contract required | Policy metadata; itself access controlled | Required before any persistence; cannot be absent for eligible envelope |
| `retention_profile` | Retention, deletion, lifecycle, and review rules; Required | Data/consumer owner with Governance approval | Not current source; NEW contract required | Sensitive governance metadata; persist only with owner | Required before persistence; cannot be absent |
| `consumer_identity` | Real downstream consumer and purpose; Required | Consumer owner | Current durable consumer NONE; OWNER_NOT_YET_DEFINED | Access-controlled correlation metadata | Mandatory consumer-proof gate; cannot be absent for durable eligibility |
| `evidence_item_identity` | Consumer-owned evidence item correlation; Conditional required | Collector/consumer contract owner | Intake accepts it, restricted-read source does not own one; NEW contract required | Correlation metadata; policy controlled | Required only when selected consumer contract requires evidence items; otherwise explicit non-Intake state |
| `provenance_created_at` | Time envelope provenance was constructed; Required | Envelope owner using Time | No separate current value; NEW contract required | Low sensitivity timestamp; persist with envelope | Consumer needs audit chronology; cannot be absent for durable eligibility |

No field in this matrix authorizes runtime creation or persistence.

## 6. Missing Ownership Decisions

The following current fields are explicitly `OWNER_NOT_YET_DEFINED`:

- `plan_step_id`;
- `collector_contract_id`;
- `consumer_identity`;
- `observation_identity`;
- `expectation_contract`.

Future ownership may be established by separate plan, collector, Observation,
privacy, and consumer contracts. A placeholder such as `phase2`, `step1`, the
capability id, approval id, execution attempt id, session id, or reader file id
does not satisfy ownership.

## 7. Action-Attempt Binding

A future eligible envelope must preserve this causal and authority sequence:

1. A governed capability request identifies the requested capability and target.
2. Approval records prerequisite human-authority state and exact request binding.
3. Core Governance authorizes a fresh execution attempt with a bounded scope.
4. Core Coordination claims the approval for that `execution_attempt_id`.
5. The Action executes within the authorized scope and produces the factual result.
6. Observation represents facts about that result without inventing expectation or
   identity.
7. Capability Verification evaluates the Action result and Observation using its
   own status vocabulary.
8. A future envelope binds all identities and relationships without changing
   their semantic ownership.

Approval authorizes prerequisite state. It is not Action identity. Governance
authorization is not Observation. The reader file-access id is not Action
identity without a separately proven Action contract.

## 8. Observation Identity Options

### Option A: producer-time identity

The future Observation producer creates a stable `observation_id` when it
creates the factual Observation. The id is correlation metadata and does not
imply persistence. This gives Verification and any later consumer a stable
identity across an eligible envelope and preserves producer provenance.

Risk: the producer must own identity generation, collision resistance, privacy,
replay/idempotency, and the relationship to the factual Observation. Current
restricted-read source does not prove that owner.

### Option B: durable-admission identity

The Observation Record builder creates an id only when persistence is authorized.
This avoids orphan durable records but cannot identify the original call-local
Observation before admission and would make a generated storage id look like
producer provenance unless an additional producer identity is retained.

### Contract decision

For a future provenance envelope, producer-time stable identity is preferred as
the Observation identity contract, with durable storage allowed to preserve it
and optionally add a separate record identity. This is a future contract
direction only. Neither option is implemented by M95B. Until a producer owner,
replay rule, and consumer are proven, the current Observation remains call-local.

Explicit prohibitions:

- reader file-access id must not become `observation_id`;
- `execution_attempt_id` must not become `observation_id`;
- `approval_id` must not become `observation_id`.

## 9. Expectation Contract

The current Intake `expected_value` is a predeclared value compared with
`observed_value` using strict JSON equality. Restricted-read Verification is a
different capability-specific evaluation. M95B does not rewrite Intake.

| Model | Meaning | Intake relation | Contract decision |
|---|---|---|---|
| A. predeclared equality expectation | Expected JSON value owned by plan/collector | Potentially compatible only when exact source semantics are proven | Preserve as a distinct variant; no synthesis |
| B. policy/invariant expectation | Expected authorization, privacy, path, or state invariant | Not `matched`/`mismatched` equality | Separate policy contract required |
| C. capability-specific Verification expectation | Expected capability outcome/status | Not Intake equality | Preserve verifier vocabulary separately |
| D. no-applicable-expectation declaration | Explicit statement that no equality expectation applies, with owner, reason, and consumer contract | Not compatible with current Intake evidence item | Required explicit variant when applicable |

The envelope must record the expectation model, owner, contract version, and
whether an expected value exists. It must never derive `expected_value` from
success, target path, content, size, truncation, reader status, or Verification.

The six capability statuses remain separate:

```text
VERIFIED_SUCCESS
VERIFIED_PARTIAL
DENIED
NOT_FOUND
CHANGED_DURING_READ
INTERNAL_ERROR
```

They must not be mapped to `matched` or `mismatched`. Compatibility outcome:
`E_COMPATIBILITY_REMAINS_UNPROVEN`; any future adapter is a separate adapter
contract and may support only an explicitly proven strict subset.

## 10. Verification Relationship

A future envelope references, without implementing, the following:

- verification producer identity;
- capability-specific status vocabulary and contract version;
- verification subject (`execution_attempt_id`, `action_identity`, and
  `observation_identity`);
- Verification timestamp when the verifier contract supplies one;
- the relationship proving which Observation facts were evaluated.

The capability verifier remains a call-local consumer until a durable consumer
and persistence contract are separately proven. The envelope is not
Verification Aggregation. No aggregation, threshold, multi-observation merge,
Critic trigger, Repair trigger, or Learning trigger is defined here.

## 11. Privacy Envelope and Payload Direction

No persistence is authorized in M95B. The following representations were
evaluated:

| Representation | Main benefit | Main risk | Contract status |
|---|---|---|---|
| Raw content | Maximum consumer detail | Secrets, private paths, partial-content leakage, retention/reassembly risk | Reject as default; no source proof of safety |
| Redacted content | More useful than metadata-only | Secret detection/redaction correctness and redaction-as-evidence semantics | Requires separate policy and proof |
| Digest-only | Low content exposure and replay comparison | Does not explain status, target policy, or consumer meaning | Possible component, not sufficient alone |
| Metadata-only | Low payload exposure | May still disclose paths, scope, size, errors, or authorization internals | Possible component under allowlist |
| Structured evidence reference | Separates payload ownership and consumer access | Requires reference target, access control, retention, and availability contract | Preferred direction |

Preferred contract direction:

`D_METADATA_PLUS_STRUCTURED_EVIDENCE_REFERENCE`

The reference may contain an approved digest or approved redacted payload
reference, but it must not imply raw-content persistence. Before eligibility,
the privacy contract must evaluate secret exposure, normalized-path exposure,
partial-content leakage, truncation, changing-file/TOCTOU semantics,
error/denial leakage, retention, deletion, visibility, access-control ownership,
auditability, and consumer usefulness.

Current result: `NOT_CURRENTLY_PROVABLE` and `NOT_SAFE_TO_PERSIST`.

## 12. Consumer Identity Gate

`consumer_identity` is mandatory for future durable eligibility. An envelope is
not persistable merely because a producer can construct it.

The future consumer must be real and proven, with:

- a defined purpose;
- an owner and identity;
- required fields and semantics;
- access rights and visibility rules;
- retention need and deletion rules;
- Verification semantics and failure behavior;
- replay/idempotency requirements.

Current restricted-read durable consumer: `NONE`.

Therefore persistence remains NOT AUTHORIZED. Observation Intake, Observation
Record, Report, audit, task continuation, ASC context, Verification
Aggregation, Critic, Repair, and Learning are not current durable
restricted-read consumers merely by existing as modules or architecture terms.

## 13. Runtime Eligibility Gates

Every gate below must be proven before a later authorized runtime milestone may
introduce an Intake caller, durable Observation persistence, or consumer
integration:

1. plan-step owner and semantics;
2. collector-contract owner and semantics;
3. Action-attempt binding;
4. stable Observation identity and replay semantics;
5. expectation model and owner;
6. capability Verification relationship;
7. privacy-safe payload representation;
8. retention, deletion, visibility, and access policy;
9. real downstream consumer identity and purpose;
10. consumer-required fields and compatibility;
11. success, partial, denied, missing, changed, and error semantics;
12. idempotency and replay behavior;
13. persistence transaction, failure, cleanup, and partial-write semantics.

Current gate state: all mandatory future gates are `UNPROVEN` or
`OWNER_NOT_YET_DEFINED` for restricted-read durable admission. Runtime bridge,
Intake caller, persistence, and consumer integration remain `BLOCKED`.

## 14. Existing Intake Compatibility

Current outcome: `E_COMPATIBILITY_REMAINS_UNPROVEN`.

The future envelope does not losslessly adapt to current Intake because Intake
requires plan/collector ownership, equality expectation semantics, and
`matched`/`mismatched` lifecycle status while restricted-read produces
capability Verification statuses and heterogeneous facts. A future adapter may
be separately authorized only after a strict subset, owner map, privacy profile,
consumer, and classification relationship are proven. Existing Intake remains
unchanged.

## 15. Loop and Architecture Ownership

The existing architecture remains authoritative:

- Aether is one persistent digital intelligence;
- AetherOS is the environment/body/world;
- Core Governance owns authority, policy, permissions, safety, and mandatory
  verification boundaries;
- Core Coordination owns task continuity, orchestration, waiting, pause, resume,
  and handoff;
- Thinking proposes;
- Action executes only within authorization;
- Observation reports facts;
- Verification supplies evidence/evaluation;
- Time provides context, not authority;
- Resource Observation reports facts;
- Resource Governance decides;
- ASC is the Authoritative Shared Cognitive Context framework.

No new organ and no second Identity authority is defined. The loop distinctions
remain explicit:

```text
Observation != Verification
Verification != Aggregation
Aggregation != Critic
Critic != Repair
Repair != Learning
```

No Observation persistence may automatically trigger Critic, Repair, Learning,
Report, or background work.

## 16. Explicit Non-Authorization

M95B does not authorize:

- runtime envelope implementation;
- Observation Intake caller;
- persistent Observation Record;
- API, schema, operation ID, route, or capability;
- generic execution;
- Verification Aggregation;
- Critic, Repair, or Learning;
- second capability;
- retry or background execution;
- consumer integration;
- M95C;
- Git lifecycle.

M95B status during Build: COMPLETE LOCALLY / PENDING PM REVIEW.
