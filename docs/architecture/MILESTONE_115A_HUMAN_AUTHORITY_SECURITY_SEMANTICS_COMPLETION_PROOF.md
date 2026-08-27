# Milestone 115A Human Authority Security Semantics Completion Proof

Classification: STRICT READ-ONLY DISCOVERY / AUTHORITY-CONTRACT SEMANTIC COMPLETION PROOF / DESIGN-RECORD-ONLY

Status: DESIGN / DISCOVERY ONLY / COMPLETE LOCALLY / PM REVIEW PENDING / NO PRODUCTION BUILD

M115A correction: the earlier design claim that a process-local trusted caller
contract completed Human Authority semantics is rejected. A well-formed envelope
proves only that some in-process caller supplied well-formed data. It does not
prove that the caller was human, that actor identity is truthful, that a human
approved the operation, that the issuer is independently trusted, or that source
and evidence records are independently authentic. No live typed envelope or
trusted adapter exists. The internal caller, replay/mutation, digest, evidence,
and minimality contracts remain incomplete.

The preserved one-mind authority equations remain binding:

```text
THINKING_PROPOSAL != GOAL_ACCEPTANCE
GOAL_ACCEPTANCE != ACTION_AUTHORIZATION
GOVERNANCE_EVALUATION != EXECUTION_AUTHORIZATION
GOAL/TASK/TASKCONTEXT_OWNERSHIP != ACTION_PERMISSION
TRANSPORT != COGNITIVE_AUTHORITY
MEMORY != GOAL_AUTHORITY
RUNTIME_PROCESS_LIFETIME != COGNITIVE_AUTHORITY
```

## 1. Baseline and Write Boundary

The exact baseline was verified before this M115A write set:

```text
branch: main
HEAD: 0cf1ee3d4c8fb6d7a3a5c6f9d5a8168f2df25f8b
main: 0cf1ee3d4c8fb6d7a3a5c6f9d5a8168f2df25f8b
origin/main: 0cf1ee3d4c8fb6d7a3a5c6f9d5a8168f2df25f8b
remote refs/heads/main: 0cf1ee3d4c8fb6d7a3a5c6f9d5a8168f2df25f8b
predecessor tag: milestone-114A-typed-human-authority-goal-operation-contract-proof
predecessor tag peeled target: 0cf1ee3d4c8fb6d7a3a5c6f9d5a8168f2df25f8b
tracked worktree: clean
untracked files before M115A: none
git diff --check: clean
full pytest baseline: 3262 passed, 9 warnings
```

The only authorized repository outputs are:

1. `docs/architecture/MILESTONE_115A_HUMAN_AUTHORITY_SECURITY_SEMANTICS_COMPLETION_PROOF.md`;
2. `tests/test_milestone_115a_human_authority_security_semantics_completion_proof.py`.

`PROGRESS.md`, README, Constitution, Architecture, production code, existing tests, dependencies, routes, APIs, and runtime/private data remain outside the M115A write set. The PM summary is external:

```text
/home/aether/summaries/milestone_115A_human_authority_security_semantics_completion_proof_summary.txt
```

No M115A PM approval, finalization, commit, tag, push, M115B, M116, or successor milestone is claimed or authorized by this record.

## 2. Project Identity and Preserved Direction

Aether is one persistent digital mind. It is intended to understand desired outcomes, own context, identify capability gaps, decide whether to use tools, agents, experts, or humans, supervise execution, observe and verify results, repair failures, learn, and remain responsible until an outcome is complete or cancelled.

The preserved principles are:

1. Goal over procedure.
2. Context is Aether's responsibility.
3. Capability gaps are solvable problems.
4. Completion means a verified outcome.
5. Aether improves how it works.

AetherOS is the runtime environment and body, not cognitive authority. Tools, models, OpenCode, external agents, experts, and human executors are capabilities or executors, not separate Aether identities. Human Authority is authority evidence supplied by a human/source; it is not a second Aether mind.

M115A preserves every boundary established by M96, M113A, and M114A. It does not promote any transport, memory object, runtime process, or existing primitive into cognitive authority.

## 3. Required Reading and Evidence Basis

M115A accounted for:

- `PROGRESS.md`, `README.md`, `docs/CONSTITUTION.md`, and `docs/ARCHITECTURE.md`;
- the complete M113A and M114A design records and static locks;
- M96A, M96B, M96C, M96E, M96F, M96G, M96 parent closure, M97A, M98A,
  M99A, M100A, M101A, M101B, M102A, M103A, M104A, M105A, M105B, M106A,
  M107A, M108A, M109A, M110A, M111A, M112A, and their relevant locks;
- M94C, M95B, M95C, and restricted-read authority/consumer boundaries;
- `aether/core/goal.py`, `aether/core/task_context.py`, and `aether/core/coordination.py`;
- `aether/interface/api_models.py`, `aether/interface/api_server.py`, and
  `/chat` and Working Memory routes;
- `aether/core/runtime.py`, `aether/core/loop.py`, and loop trace;
- `aether/memory/working/store.py`;
- `aether/thinking/proposal.py` and `aether/thinking/policy.py`;
- `aether/core/governance.py`;
- approval queue, approval decision gate, human-authorization surfaces, and
  restricted-read authority binding;
- all production references to `GoalIntake` and `CoreCoordination`;
- `aether/time` clock interface.

The relevant source facts are:

- `Goal.authority_reference` is a non-empty raw string; accepted Goals reject
  strings beginning with `approval_*`, but no typed issuer, scope, expiry,
  revocation, request binding, or provenance envelope exists.
- `GoalIntake` is an in-memory registry with propose/register/accept/get/list.
- `CoreCoordination` owns the process-local Goal registry, accepted-Goal Task
  creation, atomic first TaskContext creation, context selection, immutable
  revisions, Plan/PlanStep materialization, and Governance request assembly.
- No production module instantiates `CoreCoordination` or calls its Goal, Task,
  TaskContext, selection, Plan, or Governance methods. Callers are definitions
  and tests.
- `/chat` accepts text/message, optional `session_id`, metadata, and an ignored
  execution flag; it routes through the legacy loop and does not construct a
  Goal, Task, TaskContext, ThinkingProposal, Plan, or canonical Governance
  result.
- Working Memory stores a mutable `current_goal` string and has no canonical
  Goal identity, authority, revision, Task binding, or provenance.
- ThinkingProposal is immutable and non-authoritative. No production producer
  exists; legacy Thinking policy output cannot be losslessly adapted.
- Core Governance evaluation is immutable and explicitly non-authorizing; its
  execution and dispatch flags remain false.
- Restricted-read approval and scope are capability-specific, exact-bound, and
  single-use. They are not Goal authority.
- `aether/time/clock.py` supplies `clock.now_iso()` as the process-local wall-clock
  source. There is no monotonic clock, no external time service, and no clock
  skew tolerance contract.
- No typed live Human Authority, request identity, source-message identity,
  authority scope, expiry, revocation, or Goal-binding contract currently exists.

## 4. Frozen M114A Result

M115A begins from the frozen M114A state and does not reopen M113A decisions:

```text
TARGET_HUMAN_AUTHORITY_MODEL:
HA_MODEL_D_TYPED_SCOPE_BOUND_NON_REPLAYABLE_HUMAN_AUTHORITY_ENVELOPE

CURRENT_RUNTIME_AUTHORITY_STATE:
HA_MODEL_F_NO_TRUTHFUL_TYPED_HUMAN_AUTHORITY_CONTRACT_CURRENTLY_PROVEN

PRINCIPAL_DECISION:
D_TYPED_AUTHORITY_SHAPE_AND_GOAL_OPERATIONS_IDENTIFIED_SECURITY_SEMANTICS_INCOMPLETE

HUMAN_AUTHORITY_MATURITY (M114A baseline):
HA1_REQUIRED_FIELDS_IDENTIFIED_BUT_SEMANTICS_INCOMPLETE

HA2_PROVEN:
NO

MINIMALITY_DECISION (M114A baseline):
MINIMALITY_NOT_PROVEN

VALIDATION_SEQUENCE_STATUS:
HIGH_LEVEL_FAILURE_CLOSED_SEQUENCE_IDENTIFIED

BUILD_READINESS (M114A baseline):
BUILD_NOT_JUSTIFIED

GOAL_INTAKE_MATURITY:
GI2_CANONICAL_OWNER_PROVEN_ENTRY_CONTRACT_INCOMPLETE
```

M114A identified the candidate envelope fields and the target design direction,
but did not complete the security-relevant semantics for any bounded threat model.
M115A addresses those gaps at design level for one explicitly bounded scope.

## 5. What Human Authority Proves and Does Not Prove

The intended Human Authority contract would prove exactly one thing, but M115A
does not currently prove it:

```text
HUMAN_AUTHORITY_TARGET:
ONE_EXACT_GOAL_OPERATION_AND_EXACT_CONTENT_UNDER_A_BOUNDED_CONTEXT
```

The current repository proves only that a process-local caller could supply a
well-formed structure under a future candidate contract. It does not prove that
an authorized human source approved one exact Goal operation or exact content.

Human Authority does NOT prove any of the following:

- that Aether interpreted the desired outcome correctly;
- that an Action is permitted;
- that a tool may execute;
- that spending is permitted;
- that external communication is permitted;
- that protected data may be accessed;
- that a result is correct;
- that a Goal is complete.

Those remain separate interpretation, Governance, Action, Observation, and
Verification concerns. Goal acceptance is authority evidence for a Goal transition
only. Goal acceptance never creates Action authority. It does not grant Action
permission, Plan permission, or Generic Act permission.

The proposed security machinery is not yet proportionate enough to justify a
Build: the trust root, evidence independence, atomicity, digest semantics, and
minimality remain unresolved. No generic registry, universal permission system,
or cross-domain escalation path is introduced. Fields without a truthful issuer,
validator, or consumer must remain candidates, not Human Authority evidence.

```text
TYPED_INTERNAL_CALLER_CONTRACT != HUMAN_AUTHORITY

TYPED_INTERNAL_CALLER_CONTRACT:
A process-local schema and validation boundary proving that a caller supplied
well-formed, scope-bound Goal-operation data.

HUMAN_AUTHORITY:
Independent evidence that an authorized human approved one exact Goal operation
and exact content.
```

M115A currently proves neither a completed internal caller validation contract
nor Human Authority because atomicity and digest semantics remain incomplete.

## 6. First Bounded Threat Model

M115A evaluates every required threat model against repository evidence.

### THREAT_MODEL_A_TRUST_ALL_LOCAL_INPUT

- Repository evidence: `/chat` accepts arbitrary text; Working Memory accepts
  arbitrary strings; no validation gate exists on raw input.
- Protected asset: canonical Goal state integrity.
- Trusted components: none with respect to authority.
- Untrusted components: all local input.
- Attacker capability: any local actor or process can supply arbitrary input.
- Impersonation risk: HIGH; any caller is trusted.
- Replay risk: HIGH; no nonce or request identity.
- Stale-state risk: HIGH; no revision or validity check.
- Process-restart implications: state lost, but no durability claim exists.
- Network implications: none; purely local.
- Compatibility: matches current permissive behavior.
- Acceptance/rejection reason: REJECTED; no trust boundary, no authority proof.

### THREAT_MODEL_B_SINGLE_USER_LOCAL_PROCESS_WITH_EXPLICIT_TRUSTED_CALLER (FUTURE CANDIDATE)

- Repository evidence: single-user Linux process; no multi-user isolation;
  AetherRuntime runs one process-local CoreCoordination instance; tests invoke
  CoreCoordination directly; no network-facing authority surface exists.
- Protected asset: canonical Goal state within the process.
- Trusted components: the explicit trusted caller interface boundary; the
  process-local CoreCoordination/GoalIntake owner.
- Untrusted components: all input outside the trusted caller boundary; legacy
  `/chat` text path; Working Memory string.
- Attacker capability: any process or user with access to the trusted caller
  interface; no cryptographic attacker model applies.
- Impersonation risk: LOW within the bounded process; the trusted caller is
  defined by the explicit interface contract, not by credential verification.
- Replay risk: CONTAINABLE; request_id plus nonce scoped to the process lifetime
  prevents reuse within the same process.
- Stale-state risk: CONTAINABLE; exact Goal ID, expected revision, and content
  digest prevent stale or wrong-target mutations.
- Process-restart implications: all authority state is process-local; restart
  invalidates all in-flight requests and requires fresh authority for new
  operations.
- Network implications: none; the threat model is process-local only.
- Compatibility: fully compatible with current process-local architecture.
- Acceptance/rejection reason: FUTURE CANDIDATE ONLY. It describes the intended
  process boundary for a typed internal caller contract, but currently proves
  only that some process-local caller supplied well-formed data. It does not
  prove that the caller is human or authorized by a human and requires a real
  trust root before it can be selected as Human Authority.

### THREAT_MODEL_C_AUTHENTICATED_API_CALLER

- Repository evidence: no authentication mechanism exists; no token, certificate,
  or credential verification is implemented.
- Protected asset: API caller identity.
- Trusted components: none; authentication is absent.
- Untrusted components: all callers.
- Attacker capability: any caller can impersonate any other caller.
- Impersonation risk: HIGH.
- Replay risk: HIGH.
- Stale-state risk: HIGH.
- Process-restart implications: irrelevant without authentication.
- Network implications: irrelevant; no authenticated surface exists.
- Compatibility: incompatible with current unauthenticated architecture.
- Acceptance/reception reason: REJECTED; no authenticated caller source exists
  and none is designed by this milestone.

### THREAT_MODEL_D_SIGNED_EXTERNAL_AUTHORITY_ENVELOPE

- Repository evidence: no signing library, key store, or signature verification
  exists; no external authority provider is referenced.
- Protected asset: envelope integrity and non-repudiation.
- Trusted components: none; signing infrastructure is absent.
- Untrusted components: all envelopes.
- Attacker capability: any actor can forge envelopes.
- Impersonation risk: HIGH.
- Replay risk: HIGH.
- Stale-state risk: HIGH.
- Process-restart implications: irrelevant without signing.
- Network implications: irrelevant; no signed surface exists.
- Compatibility: incompatible with current architecture.
- Acceptance/rejection reason: REJECTED; no signed external authority source
  exists and none is introduced by this milestone.

### THREAT_MODEL_E_MULTI_USER_REMOTE_AUTHORITY

- Repository evidence: no multi-user support; no remote authority service; no
  user directory; no cross-process coordination.
- Protected asset: multi-user authority isolation.
- Trusted components: none; multi-user infrastructure is absent.
- Untrusted components: all users and remote callers.
- Attacker capability: any user can impersonate any other user.
- Impersonation risk: HIGH.
- Replay risk: HIGH.
- Stale-state risk: HIGH.
- Process-restart implications: irrelevant without multi-user state.
- Network implications: irrelevant; no remote surface exists.
- Compatibility: incompatible with current single-process architecture.
- Acceptance/rejection reason: REJECTED; repository evidence does not justify
  multi-user remote deployment.

### THREAT_MODEL_F_NO_TRUTHFUL_TRUST_BOUNDARY_CURRENTLY_PROVEN (CURRENT)

- Repository evidence: current production has no typed Human Authority envelope,
  no issuer, no revocation source, no replay guard, no digest contract.
- Protected asset: none; no authority boundary is proven.
- Trusted components: none for Goal authority.
- Untrusted components: all input paths.
- Attacker capability: unrestricted within the process.
- Impersonation risk: HIGH.
- Replay risk: HIGH.
- Stale-state risk: HIGH.
- Process-restart implications: stateless; no durability claim.
- Network implications: none.
- Compatibility: describes current state accurately.
- Acceptance/rejection reason: SELECTED as the current Human Authority threat
  model. The repository proves no truthful trust boundary. THREAT_MODEL_B is
  retained only as a future bounded candidate.

```text
SELECTED_THREAT_MODEL:
THREAT_MODEL_F_NO_TRUTHFUL_TRUST_BOUNDARY_CURRENTLY_PROVEN
```

## 7. Authority Source and Issuer Models

M115A evaluates every required issuer model against repository evidence.

### ISSUER_MODEL_A_RAW_REQUEST_SOURCE

- Exists: YES; raw request text is received by `/chat` and legacy paths.
- Identity proved: none; raw text is not an identity.
- Human actor proved: NO.
- Authenticity established: NO.
- Actor-to-issuer binding: absent.
- Goal operation attestation: absent.
- Revocation owner: none.
- Replay owner: none.
- Failure behavior: passes through without validation.
- Second cognitive authority risk: HIGH; would promote raw input to authority.
- First bounded contract support: NO.
- Decision: REJECTED.

### ISSUER_MODEL_B_SESSION_ID_AS_ISSUER

- Exists: YES; `session_id` is optional ChatRequest metadata.
- Identity proved: session correlation only.
- Human actor proved: NO.
- Authenticity established: NO.
- Actor-to-issuer binding: absent.
- Goal operation attestation: absent.
- Revocation owner: none.
- Replay owner: none.
- Failure behavior: silently ignored or passed as metadata.
- Second cognitive authority risk: HIGH; turns session into competing authority.
- First bounded contract support: NO.
- Decision: REJECTED; consistent with M114A HA_MODEL_C rejection.

### ISSUER_MODEL_C_AETHERRUNTIME_AS_ISSUER

- Exists: YES; `AetherRuntime` exists and owns Working Memory and process routing.
- Identity proved: process lifetime only.
- Human actor proved: NO.
- Authenticity established: NO.
- Actor-to-issuer binding: absent.
- Goal operation attestation: absent.
- Revocation owner: none.
- Replay owner: none.
- Failure behavior: delegates to legacy loop without authority validation.
- Second cognitive authority risk: HIGH; would make process lifetime cognitive authority.
- First bounded contract support: NO.
- Decision: REJECTED; consistent with M114A INTERPRETATION_MODEL_C rejection.

### ISSUER_MODEL_D_EXISTING_ACTION_APPROVAL_SYSTEM_AS_ISSUER

- Exists: YES; approval queue, approval decision gate, and restricted-read
  authority binding exist.
- Identity proved: action fingerprint and capability scope only.
- Human actor proved: NO; approvals are capability-specific, not Goal-specific.
- Authenticity established: NO for Goal authority.
- Actor-to-issuer binding: absent for Goal operations.
- Goal operation attestation: absent; approvals attest to Action permission only.
- Revocation owner: approval status/cancellation/consumption only.
- Replay owner: single-use Action claim only.
- Failure behavior: approved Actions proceed; rejected Actions fail closed.
- Second cognitive authority risk: HIGH; converts capability permission into
  cognitive Goal authority.
- First bounded contract support: NO.
- Decision: REJECTED; consistent with M114A HA_MODEL_B rejection.

### ISSUER_MODEL_E_TRUSTED_LOCAL_HUMAN_AUTHORITY_ADAPTER (FUTURE CANDIDATE)

- Exists: NO as a production component; the design contract defines it.
- Identity proved: only that a process-local caller supplied a structure; no
  human identity is proved.
- Human actor proved: NO. A non-empty actor_id is not proof of a human.
- Authenticity established: NOT_PROVEN. A caller-supplied envelope and a
  hardcoded issuer name do not establish issuer authenticity.
- Actor-to-issuer binding: NOT_PROVEN. The proposed request-context binding is
  self-asserted and has no independent evidence.
- Goal operation attestation: the envelope's `operation` field explicitly states
  the Goal operation; the adapter validates it against the operation subset.
- Revocation owner: NOT_PROVEN; no truthful owner exists.
- Replay owner: candidate Core Coordination/GoalIntake ownership is incomplete
  until claim consumption and mutation are atomic.
- Failure behavior: candidate reject-before-mutation behavior is incomplete.
- Second cognitive authority risk: HIGH if the adapter is treated as its own
  trust root; Core Coordination must remain the canonical owner.
- First bounded contract support: NO for Human Authority; future candidate only
  for an internal caller contract after a real trust root is selected.
- Decision: FUTURE CANDIDATE ONLY; NOT A CURRENT HUMAN AUTHORITY SOURCE.

### ISSUER_MODEL_F_AUTHENTICATED_INTERFACE_IDENTITY_PROVIDER

- Exists: NO; no authentication or identity provider exists.
- Identity proved: N/A.
- Human actor proved: N/A.
- Authenticity established: N/A.
- Actor-to-issuer binding: N/A.
- Goal operation attestation: N/A.
- Revocation owner: N/A.
- Replay owner: N/A.
- Failure behavior: N/A.
- Second cognitive authority risk: N/A.
- First bounded contract support: NO; requires infrastructure not present.
- Decision: REJECTED; no truthful identity provider exists.

### ISSUER_MODEL_G_SIGNED_EXTERNAL_AUTHORITY_PROVIDER

- Exists: NO; no signing library, key store, or external authority provider exists.
- Identity proved: N/A.
- Human actor proved: N/A.
- Authenticity established: N/A.
- Actor-to-issuer binding: N/A.
- Goal operation attestation: N/A.
- Revocation owner: N/A.
- Replay owner: N/A.
- Failure behavior: N/A.
- Second cognitive authority risk: N/A.
- First bounded contract support: NO; requires infrastructure not present.
- Decision: REJECTED; no signed external authority source exists.

### ISSUER_MODEL_H_NO_TRUTHFUL_ISSUER_CURRENTLY_PROVEN (CURRENT)

- Exists: YES as a description of current runtime state.
- Identity proved: none.
- Human actor proved: NO.
- Authenticity established: NO.
- Actor-to-issuer binding: absent.
- Goal operation attestation: absent.
- Revocation owner: none.
- Replay owner: none.
- Failure behavior: no issuer validation occurs.
- Second cognitive authority risk: N/A; no issuer exists to become authority.
- First bounded contract support: NO; this is the current state.
- Decision: SELECTED as the current issuer model. ISSUER_MODEL_E remains a
  future candidate and cannot establish its own trustworthiness.

```text
SELECTED_ISSUER_MODEL:
ISSUER_MODEL_H_NO_TRUTHFUL_ISSUER_CURRENTLY_PROVEN
```

## 8. Proportional Authority Levels

M115A evaluates whether all Goal operations require identical authority strength.

The candidate first-bounded operation subset is:

```text
SELECTED_OPERATION_SUBSET:
CANDIDATE_PROCESS_LOCAL_SUBSET_PROPOSE_ACCEPT_GET_STATUS
```

No operation may infer another operation from raw text, silence, continuity,
Working Memory, model confidence, tool availability, or an approval record.

These three operations differ in authority strength:

- `PROPOSE_GOAL`: may be produced without Human Authority and creates only a
  proposed Goal. A future contract requires provenance and deterministic content
  binding; it grants no Action authority.
- `ACCEPT_GOAL`: requires truthful Human Authority, which is currently
  NOT_PROVEN. Exact Goal ID, revision, and content must be bound; no live typed
  acceptance is proven and no Action authorization is created.
- `GET_GOAL_STATUS`: read-only. Human Authority and read-access control are
  separate concerns; current process-local lookup proves neither access control
  nor Human Authority and creates no mutation or Action authority.

All other Goal lifecycle operations (`REJECT_GOAL`, `CONTINUE_GOAL`, `PAUSE_GOAL`,
`REVISE_GOAL`, `CANCEL_GOAL`, `MARK_GOAL_COMPLETE`) and `ACTION_AUTHORIZATION`
are DEFERRED to future milestones. They are not part of the first bounded contract.

High-impact Action authorization remains explicitly outside this Goal contract,
consistent with M114A's `GOAL_ACCEPTANCE_NEVER_AUTHORIZES_ACTION` decision.

## 9. Issuer and Actor Semantics

For the current model (THREAT_MODEL_F + ISSUER_MODEL_H), M115A finds the
following candidate semantics unresolved. THREAT_MODEL_B and ISSUER_MODEL_E are
future candidates only:

- **Trusted issuer identity**: NOT_PROVEN. A named local interface is not an
  independently trusted issuer.
- **Issuer authenticity**: NOT_PROVEN. A well-formed envelope and hardcoded
  issuer name do not establish authenticity.
- **Actor identity**: NOT_PROVEN. A caller-supplied actor_id is not proof of a
  human actor.
- **Actor-to-issuer binding**: NOT_PROVEN. The proposed request-context binding
  is self-asserted and has no independent evidence.
- **Human-presence or human-origin evidence**: NOT_PROVEN. `actor_id` and
  `evidence_reference` are caller-supplied provenance fields.
- **Source-message identity**: NOT_PROVEN. `source_message_id` is caller-owned;
  no independently owned source event resolver exists.
- **Operation/request identity**: request_id is a candidate process-local
  identifier, not human authority proof.
- **Exact Goal/proposal binding**: the candidate fields are insufficient until
  digest canonicalization and atomicity are complete.
- **Responsibility for validation**: the proposed adapter/Core Coordination split
  is a future design, not a current validator or implementation.

Where truth cannot be claimed:

```text
actor_truthfulness: NOT_PROVEN
cryptographic_non_repudiation: NOT_PROVEN
external_identity_verification: NOT_PROVEN
issuer_authenticity: NOT_PROVEN
actor_issuer_binding: NOT_PROVEN
source_message_independence: NOT_PROVEN
evidence_source_independence: NOT_PROVEN
```

## 10. Revocation Semantics

For the future candidate process-local model, M115A identifies a revocation
shape, but the current repository proves no revocation owner:

- **Revocation necessity**: NOT REQUIRED for the first bounded contract. Within
  a single process lifetime, each request is unique (via `request_id` + `nonce`),
  and process restart invalidates all in-flight authority. A long-lived revocation
  registry is unnecessary and would introduce a universal authority service
  contrary to the minimality principle.
- **Short-lived single-use authority**: FUTURE CANDIDATE ONLY. Each proposed
  envelope would be valid for a single operation within a bounded time window.
- **Issuer generation/epoch**: NOT_PROVEN. The `authority_generation` field is
  retained only as a future candidate; no revocation registry validates it.
- **Explicit revocation records**: NOT INTRODUCED for the first bounded contract.
- **Process-local revocation only**: NOT_PROVEN; no revocation registry exists.
- **Durable revocation**: NOT INTRODUCED.
- **No truthful revocation owner**: CURRENTLY UNRESOLVED. Request uniqueness and
  process lifetime are not a substitute for a revocation owner.

```text
SELECTED_REVOCATION_MODEL:
NO_TRUTHFUL_REVOCATION_OWNER_CURRENTLY_PROVEN
```

Revocation owner: NOT_PROVEN.
Generation owner: NONE (no generation registry for bounded model).
Lookup source: NOT_PROVEN.
Lookup failure behavior: NOT_PROVEN.
Expiry relationship: governed by `expires_at` field in the envelope.
Stale generation behavior: N/A.
Restart behavior: candidate process-local state would be invalidated on restart;
this does not solve in-process interruption semantics.
Durability claim: NONE; process-local only.

## 11. Replay, Retry, and Atomicity

For the future candidate process-local model, M115A identifies a replay shape;
it does not prove its atomicity:

- **Request-ID owner**: Core Coordination/GoalIntake owns the request-ID space
  within the process lifetime.
- **Nonce owner**: Core Coordination/GoalIntake owns the nonce space within the
  process lifetime.
- **Uniqueness scope**: process lifetime; request IDs and nonces are unique only
  within the running process.
- **Replay-state owner**: Core Coordination/GoalIntake owns replay state (a
  set of consumed `(request_id, nonce)` pairs) within the process lifetime.
- **When a claim is consumed**: candidate point is after validation and before
  canonical mutation. Atomic consumption is NOT_PROVEN.
- **Whether validation and Goal mutation are atomic**: NOT_PROVEN. The design
  requires a single owner and transaction boundary, but no implementation is
  authorized and the replay claim, Goal mutation, and result are not proven as
  one atomic transition.
- **Retry after timeout**: a retry with the same `request_id` is treated as a
  replay and rejected. A retry with a fresh `request_id` and `nonce` is allowed.
- **Exact duplicate behavior**: candidate exact duplicate (same `request_id` +
  `nonce`) is rejected as replay. Exact-once behavior is NOT_PROVEN.
- **Conflicting duplicate behavior**: conflicting duplicates (same `request_id`,
  different `nonce`) are rejected as replay.
- **Crash before mutation**: no mutation occurs; the request is lost. The caller
  must retry with a fresh `request_id` and `nonce`.
- **Crash after mutation but before response**: mutation and result-record state
  can diverge; the caller must query status, but duplicate-prevention semantics
  are NOT_PROVEN.
- **Process restart**: all replay state, nonce state, and in-flight authority is
  lost. Fresh requests require fresh `request_id`, `nonce`, and envelope.
- **Retention**: process-local only; no durable retention is claimed.
- **Durable versus process-local guarantees**: process-local guarantees only.

```text
SELECTED_REPLAY_MODEL:
PROCESS_LOCAL_REPLAY_SHAPE_IDENTIFIED_ATOMICITY_INCOMPLETE
SELECTED_ATOMICITY_MODEL:
VALIDATE_BEFORE_MUTATE_ONLY_ATOMICITY_NOT_PROVEN
```

## 12. Digest Canonicalization

For the future candidate bounded model, M115A identifies a digest shape but does
not prove an implementation-ready canonicalization contract:

- **Purpose**: binds the exact operation content (requested outcome and constraints)
  to the authority envelope, preventing content tampering after issuance.
- **Input object**: the operation payload consisting of `requested_outcome` and
  `goal_constraints` for `PROPOSE_GOAL`; the exact proposed Goal content for
  `ACCEPT_GOAL`.
- **Schema/version**: envelope version `v1`; digest schema is versioned with the
  envelope.
- **Exact included fields**: `requested_outcome` (string), `goal_constraints`
  (sorted-key mapping), and `operation` (literal).
- **Excluded provenance-only fields**: `authority_id`, `actor_id`, `issuer_id`,
  `source_interface`, `source_message_id`, `request_id`, `nonce`,
  `authority_generation`, `evidence_reference`, `session_id`, `reason`, timestamps.
- **Encoding**: UTF-8 JSON, sorted keys, no trailing whitespace, no null bytes.
- **Key ordering**: lexicographic sort on all mapping keys at all nesting levels.
- **Unicode/text normalization**: NFC normalization on all string fields.
- **Handling of null, absent, and empty values**: null is excluded; absent is
  excluded; empty string is included as `""`; operation-specific handling remains
  incomplete.
- **List ordering**: order is significant and preserved as provided.
- **Constraint ordering**: lexicographic sort on constraint keys.
- **Timestamp handling**: timestamps are EXCLUDED from the payload digest; they
  are hashed separately in the envelope integrity digest if needed.
- **Domain-separation prefix**: `M115A_GOAL_PAYLOAD_DIGEST:v1:` prefixed to the
  canonical serialized payload before hashing.
- **Digest algorithm**: SHA-256.
- **Representation**: lowercase hexadecimal.
- **Comparison**: exact byte-for-byte comparison of hex digests.
- **Version migration**: envelope version check rejects unknown versions; no
  migration is performed by M115A.
- **Failure behavior**: reject on serialization failure or algorithm mismatch.

M115A does not determine that one digest can safely replace the separate
`operation_payload_digest`, `proposal_digest`, and `constraint_digest` fields.
Consolidation remains a future candidate because exact operation schemas,
Goal identity/revision binding, and compatibility are incomplete. Fields not
required for the bounded contract remain unresolved (see Section 16).

```text
SELECTED_DIGEST_MODEL:
CANONICAL_OPERATION_CONTENT_DIGEST_SHAPE_IDENTIFIED_SEMANTICS_INCOMPLETE
```

## 13. Time Semantics

For the future candidate bounded model, M115A records bounded time semantics only;
they are not current authority proof:

- **Canonical timestamp format**: ISO 8601, UTC, with fractional seconds:
  `YYYY-MM-DDTHH:MM:SS.sssZ`.
- **Clock source**: `aether.time.clock.now_iso()` (AetherOS process-local wall-clock).
- **Monotonic versus wall-clock purpose**: wall-clock is used for human-visible
  timestamps (`issued_at`, `valid_from`, `expires_at`). Monotonic time is NOT
  available and is NOT required for the bounded model.
- **Permitted skew**: ZERO; the bounded model assumes a single process with no
  distributed clock. Skew is not modeled.
- **`issued_at`**: the wall-clock time when the envelope was issued. Owned by the
  trusted caller adapter. Provenance only; not used for authority validation
  beyond expiry check.
- **`valid_from`**: the earliest time at which the envelope is valid. Owned by
  the issuer. Used for time-window validation.
- **`expires_at`**: the latest time at which the envelope is valid. Owned by the
  issuer. Expired envelopes are rejected.
- **Maximum validity**: 5 minutes for the first bounded contract. This is a
  design constraint; longer validity increases replay risk without benefit for
  process-local single-use.
- **Expiry failure**: reject with clear error; do not accept stale authority.
- **Clock-unavailable behavior**: reject; do not synthesize time.
- **Restart behavior**: all timestamps are invalid after process restart because
  the clock source is process-local. Fresh envelopes are required.
- **Clock rollback/jump behavior**: INCOMPLETE; no rollback or forward-jump
  policy is specified beyond zero permitted distributed skew.

AetherOS supplies clock facts. It does not become authority or interpret human
intent.

```text
SELECTED_TIME_MODEL:
PROCESS_LOCAL_WALL_CLOCK_WITH_FIVE_MINUTE_MAX_VALIDITY
```

This is a bounded design candidate only. Wall-clock validity does not prove human
origin and cannot repair a missing trust root.

## 14. Evidence and Audit

For the future candidate bounded model, M115A records evidence and audit shapes
only; independence and authenticity are NOT_PROVEN:

- **Evidence-reference owner**: the trusted caller adapter owns evidence references
  within the process lifetime.
- **Evidence lookup**: candidate process-local lookup within the adapter's
  evidence store. No external evidence resolver exists.
- **Authenticity**: NOT_PROVEN. Evidence created and validated by the same
  untrusted caller boundary is not independent Human Authority evidence.
- **Retention**: process-local only; no durable retention is claimed.
- **Privacy**: evidence references are process-local and not exposed outside the
  trusted boundary.
- **Redaction**: not required for process-local bounded model.
- **Failure audit owner**: candidate Core Coordination/GoalIntake ownership is
  not implemented or proven.
- **Failure event schema**: `{ event_type, timestamp, operation, goal_id, failure_reason, request_id, actor_id }`.
- **Durability**: process-local only; audit events are lost on restart.
- **Access boundary**: process-local; no external access is claimed.

M115A separates:
- Human Authority evidence (envelope provenance);
- Goal provenance (source interface, source message, actor, time);
- Action approval (capability-specific, separate domain);
- Observation (capability-specific result evidence);
- Verification (outcome evidence assessment);
- Operational logs (process-local audit events).

These are NOT merged into one generic evidence registry. Each retains its own
owner and schema.

```text
SELECTED_EVIDENCE_MODEL:
PROCESS_LOCAL_EVIDENCE_SHAPE_NOT_INDEPENDENTLY_PROVEN
```

## 15. Validation and Mutation Sequence

M115A records a candidate validation sequence, not a proven runtime contract:

1. **Parse/version**: Adapter receives the typed request. Validates envelope
   version against known versions. Unknown version -> reject.
2. **Operation**: Adapter validates the `operation` field against the selected
    operation subset `{PROPOSE_GOAL, ACCEPT_GOAL, GET_GOAL_STATUS}`. unsupported
    operation -> reject.
3. **Issuer and actor**: Adapter validates `issuer_id` matches the trusted local
    interface identity. Validates `actor_id` is non-empty. Invalid issuer or empty
     actor -> reject. malformed authority envelope shape -> reject.
4. **Authority scope**: Adapter validates `authority_scope` covers the requested
   operation and Goal ID (if applicable). Scope violation -> reject.
5. **Source/request identity**: Adapter validates `source_interface` and
   `source_message_id` are non-empty and consistent. Invalid source identity ->
   reject.
 6. **Goal identity and revision**: For `ACCEPT_GOAL`, Core Coordination validates
    `goal_id` exists and `expected_goal_revision` matches current revision. For
    `PROPOSE_GOAL`, no existing Goal is required. For `GET_GOAL_STATUS`,
     `goal_id` is validated for existence. wrong Goal identity -> reject. stale
     Goal revision -> reject. Invalid Goal identity or stale revision -> reject.
  7. **Canonical content digest**: Candidate Core Coordination logic would compare
     a canonical digest, but exact operation schemas and Goal identity/revision
     inclusion are incomplete. Mismatch or changed proposal after authority would
     reject; no implementation-ready digest contract exists.
  8. **Time**: Adapter validates `valid_from <= now <= expires_at` using the
      process-local clock. Out-of-window -> reject. expired authority -> reject.
9. **Revocation**: NOT APPLICABLE for process-local single-use model. Skip.
  10. **Replay/idempotency**: Candidate Core Coordination logic would check
      `(request_id, nonce)` within process lifetime. Replay -> reject; replayed
      authority -> reject. Claim consumption is not proven atomic.
 11. **Lifecycle validity**: Core Coordination validates the Goal lifecycle
     transition is valid (e.g., `ACCEPT_GOAL` requires `proposed` status).
     invalid lifecycle transition -> reject. Invalid transition -> reject.
12. **Provenance**: Adapter validates all required provenance fields are present
    and consistent. Missing provenance -> reject.
13. **Validation result**: All checks pass -> proceed to mutation. Any check
    fails -> reject before mutation.
  14. **Canonical mutation**: Candidate Core Coordination would perform the
     canonical operation under an owned transaction boundary; no such boundary
     is implemented or proven.
  15. **Replay/result recording**: Candidate replay and result recording are
     separate requirements; their atomic relationship is NOT_PROVEN.
  16. **Failure audit**: Candidate failure audit is outside the canonical
     transaction unless a future design proves otherwise.
17. **Returned result**: The result is returned to the caller. No partial state
    is exposed on failure.

```text
VALIDATION_SEQUENCE:
PARSE_VERSION -> OPERATION -> ISSUER_ACTOR -> SCOPE -> SOURCE_ID -> GOAL_ID_REVISION
-> CONTENT_DIGEST -> TIME -> REPLAY -> LIFECYCLE -> PROVENANCE -> MUTATE -> RECORD -> AUDIT -> RESULT
```

Required boundary: steps 1-13 must validate before mutation; step 14 must not
be exposed as committed until replay and result recording have an atomic owner.
This is not proven. no partial mutation is intended on validation failure, but
partial mutation before validation failure is not proven impossible.
missing provenance -> reject. persistence/restoration assumed -> reject.

Owner of every step:
- Steps 1-4, 8, 12: trusted caller adapter.
- Steps 5, 6, 7, 9, 10, 11, 13, 14, 15, 16, 17: Core Coordination/GoalIntake.

## 16. Minimal Envelope Decision

M115A records a candidate table for every M114A field. KEEP and CONDITIONAL are
design candidates only; no field is thereby proven truthful or minimal.

| M114A Field | M115A Decision | Reason | Supported Operation | Threat Addressed | Owner | Validator | Current Truthful Source | Authority or Provenance |
|---|---|---|---|---|---|---|---|---|
| `envelope_version` | KEEP | Required for version negotiation | All | Unknown version rejection | Envelope contract owner | Adapter | none | Provenance only |
| `authority_id` | KEEP | Required for distinct authority evidence identity | All | Impersonation within bounded model | Issuer | Adapter | none | Authority identity |
| `authority_kind` | KEEP | Required to declare human authority kind | All | Wrong-kind envelope rejection | Issuer | Adapter | none | Authority classification |
| `actor_id` | KEEP CANDIDATE | Caller-supplied actor label; human identity not proven | All | Unattributed authority | Issuer candidate | Candidate adapter | caller payload | Unproven identity evidence |
| `issuer_id` | KEEP CANDIDATE | Caller-supplied issuer label; issuer authenticity not proven | All | Untrusted issuer rejection | Issuer candidate | Candidate adapter | caller payload | Unproven provenance |
| `source_interface` | KEEP CANDIDATE | Candidate source-channel provenance only | All | Interface spoofing | Caller | Candidate adapter | caller payload | Provenance only |
| `source_message_id` | KEEP CANDIDATE | Caller-supplied source binding; independence not proven | All | Source reuse across operations | Caller | Candidate adapter | caller payload | Unproven source binding |
| `request_id` | KEEP CANDIDATE | Candidate request identity for process-local replay shape | All | Replay detection | Caller | Candidate Core Coordination | caller payload | Not Human Authority proof |
| `operation` | KEEP | Required for exact operation discrimination | All | Wrong operation scope | Caller | Adapter | request discriminant | Authority and mutation binding |
| `goal_id` | CONDITIONAL | Required for ACCEPT/GET; absent for PROPOSE | ACCEPT, GET | Wrong Goal targeting | Caller | Core Coordination | GoalIntake lookup | Core Coordination-owned identity |
| `expected_goal_revision` | CONDITIONAL | Required for ACCEPT; absent for PROPOSE | ACCEPT | Stale-state guard | Caller | Core Coordination | GoalIntake current revision | Core Coordination validates |
| `operation_content_digest` | KEEP CANDIDATE | Candidate content binding; canonicalization incomplete | PROPOSE, ACCEPT | Content tampering | Caller | Candidate Core Coordination | unspecified canonical serialization | Unproven content binding |
| `authority_scope` | KEEP CANDIDATE | Candidate scope boundary; issuer trust not proven | All | Scope violation | Issuer candidate | Candidate adapter + Core Coordination | caller payload | Unproven authority boundary |
| `issued_at` | KEEP | Required for issuance time fact | All | Stale issuance | Issuer | Adapter | AetherOS clock | Provenance |
| `valid_from` | KEEP | Required for validity window start | All | Premature use | Issuer | Adapter | AetherOS clock | Authority validity |
| `expires_at` | KEEP | Required for validity window end | All | Expired authority | Issuer | Adapter | AetherOS clock | Authority validity |
| `nonce` | KEEP | Required for replay guard | All | Replay detection | Caller | Core Coordination | request context | Authority evidence |
| `evidence_reference` | KEEP CANDIDATE | Caller-supplied evidence reference; independence not proven | All | Unsubstantiated authority | Issuer candidate | Candidate adapter | caller payload | Provenance only |
| `session_id` | REMOVE | Provenance-only correlation; not required for bounded contract | All | None | Caller | Adapter | optional metadata | Provenance only; omitted for minimality |
| `reason` | REMOVE | Provenance-only; does not authorize | All | None | Caller | Adapter | optional text | Provenance only; omitted for minimality |
| `proposal_digest` | REMOVE | Consolidated into `operation_content_digest` | All | None | — | — | — | Redundant with consolidated digest |
| `constraint_digest` | REMOVE | Consolidated into `operation_content_digest` | All | None | — | — | — | Redundant with consolidated digest |
| `operation_payload_digest` | REMOVE | Consolidated into `operation_content_digest` | All | None | — | — | — | Redundant with consolidated digest |
| `authority_generation` | DEFER | Not required for process-local single-use; retained for future | All | Future revocation | — | — | — | Provenance only; not validated in first contract |
| `parent_authority_id` | REMOVE | Delegated authority is not supported in first contract | All | None | — | — | — | Forbidden in first contract; cannot be migrated into Goal authority |
| `revocation_status` | REMOVE | Not caller-controlled; validator obtains current status | All | None | — | — | — | Validation result, not trusted payload |
| `goal_constraints` | CONDITIONAL | Included in `operation_content_digest` for PROPOSE; validated for ACCEPT | PROPOSE, ACCEPT | Content integrity | GoalIntake | Core Coordination | Goal.intact_constraints | Part of content digest binding |
| `requested_outcome` | CONDITIONAL | Included in `operation_content_digest` for PROPOSE; validated for ACCEPT | PROPOSE, ACCEPT | Content integrity | GoalIntake | Core Coordination | Goal.requested_outcome | Part of content digest binding |

### 16.1 Minimal Envelope Schema

The candidate envelope for a future bounded contract contains:

```text
envelope_version: string (required)
authority_id: string (required)
authority_kind: literal "human" (required)
actor_id: string (required)
issuer_id: string (required)
source_interface: string (required)
source_message_id: string (required)
request_id: string (required)
operation: enum {PROPOSE_GOAL, ACCEPT_GOAL, GET_GOAL_STATUS} (required)
goal_id: string or null (conditional)
expected_goal_revision: positive int or null (conditional)
operation_content_digest: string SHA-256 hex (required for PROPOSE/ACCEPT)
authority_scope: structured scope (required)
issued_at: ISO 8601 timestamp (required)
valid_from: ISO 8601 timestamp (required)
expires_at: ISO 8601 timestamp (required)
nonce: string (required)
evidence_reference: structured reference (required)
```

Fields `session_id`, `reason`, `proposal_digest`, `constraint_digest`,
`operation_payload_digest`, `authority_generation`, `parent_authority_id`,
and `revocation_status` are EXCLUDED from the minimal bounded envelope.

### 16.2 Minimality Decision

```text
MINIMALITY_DECISION:
MINIMALITY_NOT_PROVEN
```

Minimality is unresolved because issuer truth, evidence independence, digest
semantics, operation-specific requirements, and compatibility are unresolved.
The candidate envelope is Goal-specific; it introduces no generic registry and
does not authorize Action or Generic Act.

## 17. Completion Boundary

```text
A_REQUEST_TO_COMPLETE_IS_NOT_PROOF_OF_COMPLETION
```

Human Authority may authorize a completion request but cannot supply outcome proof.
Observation and Verification remain separate. No Goal completion transition is
authorized or implemented by M115A. `MARK_GOAL_COMPLETE` remains a future
candidate and is not a live canonical operation.

Completion requires:
1. Human Authority authorizes the completion request (bounded operation subset
   does not include `MARK_GOAL_COMPLETE`).
2. Observation supplies outcome evidence.
3. Verification evaluates evidence against exact Goal outcome criteria.
4. Core Coordination owns a future completion transition only after a separate
   lifecycle contract is proven.

## 18. Maturity Gate

The M114A Human Authority maturity scale is preserved:

```text
HA0_NO_TYPED_HUMAN_AUTHORITY_CONTRACT
HA1_REQUIRED_FIELDS_IDENTIFIED_BUT_SEMANTICS_INCOMPLETE
HA2_TYPED_SCOPE_AND_VALIDATION_CONTRACT_PROVEN_DESIGN_ONLY (NOT CURRENTLY ATTAINED)
HA3_BOUNDED_PROCESS_LOCAL_TYPED_AUTHORITY_IMPLEMENTED_AND_TESTED
HA4_LIVE_ENTRY_AUTHORITY_IMPLEMENTED_AND_TESTED
HA5_DURABLE_RESTART_SAFE_AUTHORITY_IMPLEMENTED_AND_TESTED
```

M115A selects:

```text
HUMAN_AUTHORITY_MATURITY:
HA1_REQUIRED_FIELDS_IDENTIFIED_BUT_SEMANTICS_INCOMPLETE
```

Rationale: M115A identifies the security-relevant design questions for the
candidate process-local subset, but the current repository proves no truthful
issuer, actor binding, atomicity, digest canonicalization, evidence independence,
or minimality:

- Issuer trust semantics: NOT_PROVEN.
- Actor/issuer binding: NOT_PROVEN.
- Revocation semantics: NOT_PROVEN.
- Replay semantics: PROCESS_LOCAL_REPLAY_SHAPE_IDENTIFIED_ATOMICITY_INCOMPLETE.
- Digest canonicalization: CANONICAL_OPERATION_CONTENT_DIGEST_SHAPE_IDENTIFIED_SEMANTICS_INCOMPLETE.
- Time semantics: bounded process-local wall-clock candidate; rollback/jump behavior incomplete.
- Evidence resolution: NOT_PROVEN independently authentic.
- Failure audit: candidate schema only; owner and atomic boundary incomplete.
- Validation/mutation atomicity: VALIDATE_BEFORE_MUTATE_ONLY_ATOMICITY_NOT_PROVEN.
- Envelope minimality: MINIMALITY_NOT_PROVEN.

```text
HA2_PROVEN: NO
```

HA1 does not imply live runtime implementation, durable or cross-process
authority, production Build authorization, or extension to other threat models
or operation subsets.

Existing Goal-intake maturity remains unchanged:

```text
GOAL_INTAKE_MATURITY:
GI2_CANONICAL_OWNER_PROVEN_ENTRY_CONTRACT_INCOMPLETE
```

Creating this design record does not advance GI maturity. GI3 requires a live
entry contract with a proven transport, which M115A does not implement.

## 19. Build-Readiness Gate

M115A evaluates Build readiness for the candidate process-local model:

| Required condition | M115A result |
|---|---|
| HA2 proven for bounded model | NO; HA2_PROVEN: NO |
| Threat model exact | THREAT_MODEL_F_NO_TRUTHFUL_TRUST_BOUNDARY_CURRENTLY_PROVEN |
| Issuer/source exists or bounded source contract proven | NO; ISSUER_MODEL_H_NO_TRUTHFUL_ISSUER_CURRENTLY_PROVEN |
| Envelope is minimal | MINIMALITY_NOT_PROVEN |
| Validation ownership exact | Candidate ownership identified; current validator and mutation boundary not proven |
| Replay and atomicity exact for process boundary | PROCESS_LOCAL_REPLAY_SHAPE_IDENTIFIED_ATOMICITY_INCOMPLETE |
| Digest canonicalization exact | CANONICAL_OPERATION_CONTENT_DIGEST_SHAPE_IDENTIFIED_SEMANTICS_INCOMPLETE |
| Time semantics exact | INCOMPLETE; process-local wall clock has no proven rollback/jump policy |
| Evidence and audit boundaries exact | PROCESS_LOCAL_EVIDENCE_SHAPE_NOT_INDEPENDENTLY_PROVEN |
| Compatibility and rollback exact | LEGACY_RAW_REFERENCE_PROCESS_LOCAL_ONLY_NO_SILENT_AUTHORITY_PROMOTION; compatibility contract unresolved |
| Build limited to process-local Goal authority | NOT JUSTIFIED |
| No /chat wiring needed | YES, and no wiring is authorized |
| No persistence needed | YES for this discovery record; durability is not proven |
| No Generic Act expansion needed | YES; Generic Act remains unauthorized |
| No Action authority expansion needed | YES; Goal acceptance never authorizes Action |

```text
BUILD_READINESS:
BUILD_NOT_JUSTIFIED
```

A later Build requires a truthful trust-root decision and completion of the
issuer, evidence, digest, atomicity, minimality, and compatibility contracts.
No Build is recommended by this record.

The Build must NOT include:
- `/chat` wiring;
- persistence or durable restoration;
- Generic Act integration;
- Action authority expansion;
- cross-process or network authority;
- revocation registry;
- signed external authority.

## 20. Required Design Decisions

```text
SELECTED_THREAT_MODEL:
THREAT_MODEL_F_NO_TRUTHFUL_TRUST_BOUNDARY_CURRENTLY_PROVEN

SELECTED_ISSUER_MODEL:
ISSUER_MODEL_H_NO_TRUTHFUL_ISSUER_CURRENTLY_PROVEN

SELECTED_AUTHORITY_SCOPE:
GOAL_OPERATION_BOUNDARY_PROPOSE_ACCEPT_GET_STATUS_ONLY

SELECTED_OPERATION_SUBSET:
CANDIDATE_PROCESS_LOCAL_SUBSET_PROPOSE_ACCEPT_GET_STATUS

SELECTED_REPLAY_MODEL:
PROCESS_LOCAL_REPLAY_SHAPE_IDENTIFIED_ATOMICITY_INCOMPLETE

SELECTED_REVOCATION_MODEL:
NO_TRUTHFUL_REVOCATION_OWNER_CURRENTLY_PROVEN

SELECTED_DIGEST_MODEL:
CANONICAL_OPERATION_CONTENT_DIGEST_SHAPE_IDENTIFIED_SEMANTICS_INCOMPLETE

SELECTED_TIME_MODEL:
PROCESS_LOCAL_WALL_CLOCK_WITH_FIVE_MINUTE_MAX_VALIDITY

SELECTED_EVIDENCE_MODEL:
PROCESS_LOCAL_EVIDENCE_SHAPE_NOT_INDEPENDENTLY_PROVEN

SELECTED_ATOMICITY_MODEL:
VALIDATE_BEFORE_MUTATE_ONLY_ATOMICITY_NOT_PROVEN

PRINCIPAL_DECISION:
F_NO_TRUTHFUL_HUMAN_AUTHORITY_TRUST_ROOT_AND_SECURITY_CONTRACT_INCOMPLETE

HUMAN_AUTHORITY_MATURITY:
HA1_REQUIRED_FIELDS_IDENTIFIED_BUT_SEMANTICS_INCOMPLETE

GOAL_INTAKE_MATURITY:
GI2_CANONICAL_OWNER_PROVEN_ENTRY_CONTRACT_INCOMPLETE

MINIMALITY_DECISION:
MINIMALITY_NOT_PROVEN

BUILD_READINESS:
BUILD_NOT_JUSTIFIED

NEXT_FRONTIER:
TRUTHFUL_HUMAN_AUTHORITY_TRUST_ROOT_DECISION

NEXT_MILESTONE_TYPE:
AUTHORITY-SOURCE / TRUST-BOUNDARY DECISION
```

## 21. Core-Drift Evaluation

- Does Aether remain one persistent digital mind?
  YES. The design preserves the Constitution/Architecture one-mind model and gives
  Human Authority evidence, not a second Aether identity.

- Does Core Coordination/GoalIntake remain canonical owner?
  YES, process-locally. The frozen M113A owner is unchanged.

- Does Human Authority remain external authority evidence rather than another mind?
  INTENDED YES, but no truthful Human Authority evidence is currently proven.
  The envelope identifies only caller-supplied actor/source fields and creates no
  identity or cognitive organ.

- Does any transport become cognitive authority?
  NO. The selected transport (future explicit Goal route) delegates to Core
  Coordination and cannot assign canonical authority. transport assigning
  authority -> reject.

- Does Working Memory become Goal authority?
  NO. It remains legacy state/reference only. Working Memory promotion -> reject.

- Does AetherRuntime become cognitive authority?
  NO. Process lifetime and routing remain infrastructure roles. AetherRuntime claiming cognitive ownership -> reject.

- Does AetherOS become cognitive authority?
  NO. It supplies clocks and mechanisms, not cognitive semantics.

- Can Thinking or a model accept its own proposal?
  NO. Thinking/model output remains non-authoritative; Core Coordination validates
  and Human Authority supplies acceptance. Thinking or model self-acceptance -> reject.

- Is Goal acceptance separated from Action authorization?
  YES. The explicit decision is `GOAL_ACCEPTANCE_NEVER_AUTHORIZES_ACTION`.
  Action approval as Goal acceptance -> reject. Goal acceptance as Action
  authorization -> reject.

- Are capability executors kept outside cognitive ownership?
  YES. Tools, models, OpenCode, external agents, experts, and human executors are
  capabilities/executors and Action remains capability-specific.

- Is Context still Aether's responsibility?
  YES. Core Coordination owns Task/TaskContext continuity and selection within the
  one mind.

- Is Goal still above procedure?
  YES. Explicit Goal operation and authority precede procedure; no procedure may
  replace Goal authority.

- Does completion still require verified outcome evidence?
  YES. `MARK_GOAL_COMPLETE` requires a future verified outcome contract; an
  assertion, proposal, or Action approval is insufficient.

- Is Generic Act still unauthorized?
  YES. Governance evaluation and Goal acceptance remain non-executing; Generic Act
  is not implemented or authorized.

- Is production readiness being falsely claimed?
  NO. Status is HA1, GI2, and BUILD_NOT_JUSTIFIED. No implementation is
  authorized by this record.

- Has M115A expanded into an authority registry or generic runtime?
  NO. It defines a bounded design contract only, adds no registry, no runtime,
  no API, no persistence, and no capability generalization.

- Is the envelope Goal-specific?
  CANDIDATE YES. The proposed envelope is scoped to Goal operations only and
  does not generalize to Action, Governance, or other authority domains.

- Is capability-specific Action authority duplicated?
  NO. Action authority remains in the existing capability-specific approval
  system. The Goal envelope does not reference or reuse Action approval records.

- Does the bounded Build authorization imply production implementation?
  NO. `BUILD_NOT_JUSTIFIED` is a discovery result, not implementation
  authorization.

```text
CORE_DRIFT_RISK: INTERNAL_CALLER_MISLABELED_AS_HUMAN_AUTHORITY_DETECTED_AND_REJECTED
CORE_DRIFT_DETECTED_IN_CORRECTED_DECISION: NO
CORE_DRIFT_DETECTED: NO
```

## 22. Explicit Non-Goals and Authorization State

M115A does not implement or authorize:

- a live typed Human Authority runtime object, issuer component, validator,
  revocation service, or replay store;
- a Goal runtime entry, Goal API, Goal route, or `/chat` wiring;
- a natural-language interpreter or classifier;
- a Goal lifecycle transport for REJECT, CONTINUE, PAUSE, REVISE, CANCEL, or
  MARK_COMPLETE;
- a producer or adapter for ThinkingProposal;
- Goal-to-Plan runtime execution;
- persistence, queues, workers, schedulers, background continuation, or
  cross-process authority;
- a cross-domain authority registry or Action approval reuse;
- Generic Act, Action execution expansion, or capability delegation;
- no Generic Act integration in the bounded Build;
- changes to `PROGRESS.md`, README, Constitution, Architecture, production code,
  existing tests, dependencies, routes, APIs, or runtime/private data;
- M115B, M116, or any successor milestone;
- commit, tag, push, project-manager approval, or finalization claims.

```text
Production implementation: NOT CLAIMED
Human Authority runtime: NOT IMPLEMENTED
Live typed authority: NOT PROVEN (design-only)
Live canonical Goal entry: NOT PROVEN
No live canonical Goal entry is implemented by this milestone.
Durable authority: NOT PROVEN
Future Build: NOT AUTHORIZED; BUILD_NOT_JUSTIFIED
Generic Act: NOT_IMPLEMENTED / NOT_AUTHORIZED / NOT_GRANTED
M115B: NOT AUTHORIZED
M116: NOT AUTHORIZED
commit: NONE
tag: NONE
push: NONE
```

M115A returns control to the human/project manager. It is not finalized or PM
approved by this record. no production Build is authorized by this record. The next authorized action is:

```text
NEXT_AUTHORIZED_ACTION:
HUMAN/PROJECT-MANAGER REVIEW OF THE M115A DESIGN RECORD AND BUILD JUSTIFICATION
```
