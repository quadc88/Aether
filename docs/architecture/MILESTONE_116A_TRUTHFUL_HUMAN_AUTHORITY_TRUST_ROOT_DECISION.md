# Milestone 116A Truthful Human Authority Trust Root Decision

Classification: STRICT READ-ONLY DISCOVERY / TRUST-ROOT AND DEPLOYMENT DECISION / DESIGN-RECORD-ONLY

Status: DESIGN / DISCOVERY ONLY / COMPLETE LOCALLY / PM REVIEW PENDING / NO PRODUCTION BUILD

M116A determines whether the repository currently contains a truthful Human
Authority trust root and which deployment boundary, if any, is justified. It
does not implement authentication, a trusted adapter, a Goal route, a session
system, persistence, recovery, revocation, a ThinkingProposal producer, Action
authority, Generic Act, `/chat` wiring, M116B, M117, or any successor milestone.

The decision is negative. Current runtime evidence supports only a process-local
loopback API with caller-supplied input and no independently authenticated
Human Authority source. A local process, session identifier, identity seed,
approval record, or typed envelope must not be relabeled as a human trust root.

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

The exact baseline was verified before this M116A write set:

```text
branch: main
HEAD: 1ccb578713bb01cef365899c17316208e6a4458e
main: 1ccb578713bb01cef365899c17316208e6a4458e
origin/main: 1ccb578713bb01cef365899c17316208e6a4458e
remote refs/heads/main: 1ccb578713bb01cef365899c17316208e6a4458e
predecessor tag: milestone-115A-human-authority-trust-root-proof-boundary
predecessor tag peeled target: 1ccb578713bb01cef365899c17316208e6a4458e
tracked worktree: clean
untracked files before M116A: none
git diff --check: clean
full pytest baseline: 3267 passed, 9 warnings
```

The only authorized repository outputs are:

1. `docs/architecture/MILESTONE_116A_TRUTHFUL_HUMAN_AUTHORITY_TRUST_ROOT_DECISION.md`;
2. `tests/test_milestone_116a_truthful_human_authority_trust_root_decision.py`.

`PROGRESS.md`, README, Constitution, Architecture, production code, existing
tests, dependencies, routes, APIs, runtime/private data, and Git references
remain outside the M116A write set. The required PM summary is external:

```text
/home/aether/summaries/milestone_116A_corrected_truthful_human_authority_trust_root_decision_summary.txt
```

No M116A PM approval, finalization, commit, tag, push, M116B, M117, or successor
milestone is claimed or authorized by this record. No M116B is started. No M117
is started.

## 2. Frozen Predecessor State

M116A does not reopen the M113A, M114A, or M115A decisions. The following are
frozen inputs:

```text
TARGET_HUMAN_AUTHORITY_MODEL:
HA_MODEL_D_TYPED_SCOPE_BOUND_NON_REPLAYABLE_HUMAN_AUTHORITY_ENVELOPE

CURRENT_RUNTIME_AUTHORITY_STATE:
HA_MODEL_F_NO_TRUTHFUL_TYPED_HUMAN_AUTHORITY_CONTRACT_CURRENTLY_PROVEN

SELECTED_THREAT_MODEL:
THREAT_MODEL_F_NO_TRUTHFUL_TRUST_BOUNDARY_CURRENTLY_PROVEN

SELECTED_ISSUER_MODEL:
ISSUER_MODEL_H_NO_TRUTHFUL_ISSUER_CURRENTLY_PROVEN

TRUST_BOUNDARY_VERDICT:
TRUST_BOUNDARY_CONTRACT_DEFINED_BUT_TRUST_ROOT_EXTERNAL_AND_UNPROVEN

HUMAN_AUTHORITY_MATURITY:
HA1_REQUIRED_FIELDS_IDENTIFIED_BUT_SEMANTICS_INCOMPLETE

HA2_PROVEN: NO
GOAL_INTAKE_MATURITY: GI2_CANONICAL_OWNER_PROVEN_ENTRY_CONTRACT_INCOMPLETE
MINIMALITY_DECISION: MINIMALITY_NOT_PROVEN
BUILD_READINESS: BUILD_NOT_JUSTIFIED
```

Core Coordination/GoalIntake remains the canonical process-local Goal owner.
Interfaces remain transports. Goal proposal and Goal acceptance remain
separate. Goal acceptance never creates Action authority. Completion still
requires independent Observation and Verification evidence, and
`A_REQUEST_TO_COMPLETE_IS_NOT_PROOF_OF_COMPLETION`.

## 3. Required Evidence and Actual Runtime Boundary

The discovery reviewed the project constitution, architecture, progress, the
complete M113A/M114A/M115A records and locks, the relevant Goal, TaskContext,
Coordination, Runtime, Working Memory, Thinking, Governance, Action approval,
restricted-read, observation, verification, time, and API sources, plus their
production references and relevant tests.

The source ownership review included `aether/core/goal.py`,
`aether/core/task_context.py`, and `aether/core/coordination.py`, in addition to
the API and runtime files named below.

The relevant current source facts are:

- `config/aether.yaml` sets `api.host` to `127.0.0.1` and `api.port` to `8000`.
- The FastAPI application includes many routes but no observed authentication
  middleware, credential validator, owner provisioning, or Human Authority
  source boundary.
- `/chat` accepts text/message, optional `session_id`, and metadata. The
  `execution` behavior is forced false for the current milestone. The request
  fields are transport input, not authenticated source evidence.
- `session_id` is caller-supplied metadata copied through runtime and action
  records. It authenticates neither a caller nor an issuer.
- `aether/identity/guard.py` verifies the Aether identity-seed checksum. It
  protects seed integrity and does not authenticate an owner or human source.
- Approval queues, approval decision gates, and human-authorization records
  authorize capability-specific Action workflows. They do not prove Goal
  authority or the identity of the person who supplied them.
- Working Memory stores mutable process-local context and is not Goal authority.
- `AetherRuntime` owns process readiness and process-local orchestration, not
  cognitive authority.
- Core Governance evaluates authorization envelopes but is explicitly
  non-authorizing at the frozen boundary.
- No production module provides a Unix-socket identity, terminal identity,
  authenticated API identity, external signed authority, hardware-backed owner
  key, source-message authentication, revocation authority, or durable
  authority lifecycle.
- `uvicorn` is a dependency, but no repository service/proxy/deployment file
  establishes an authenticated deployment boundary.

Therefore the current source can prove only that a process-local caller sent
data to an interface. It cannot prove that the caller was a human, that an
actor identity is truthful, that an issuer is independently trusted, or that a
human approved one exact Goal operation and exact content.

## 4. Authorized Trust-Root Candidate Matrix

Every authorized candidate is evaluated without promoting a transport,
integrity check, Python caller, or capability approval into Human Authority.
Each row records the required current-state categories. `TARGET_CANDIDATE`
means a possible later design only; M116A selects no target implementation.

| Candidate | CURRENTLY_EXISTS | TARGET_CANDIDATE | REJECTED | NOT_PROVEN |
| --- | --- | --- | --- | --- |
| `TRUST_ROOT_MODEL_A_PROCESS_LOCAL_CALLER_CONVENTION` | NO | NO | YES | YES |
| `TRUST_ROOT_MODEL_B_OPERATING_SYSTEM_USER_AND_LOCAL_IPC_PEER_IDENTITY` | NO | YES | NO | YES |
| `TRUST_ROOT_MODEL_C_OWNER_CONFIGURED_LOCAL_SECRET_OR_TOKEN` | NO | YES | NO | YES |
| `TRUST_ROOT_MODEL_D_AUTHENTICATED_LOCAL_UI_SESSION` | NO | YES | NO | YES |
| `TRUST_ROOT_MODEL_E_AUTHENTICATED_API_IDENTITY` | NO | YES | NO | YES |
| `TRUST_ROOT_MODEL_F_SIGNED_EXTERNAL_AUTHORITY_EVENT` | NO | YES | NO | YES |
| `TRUST_ROOT_MODEL_G_EXISTING_APPROVAL_UI_OR_APPROVAL_RECORD` | YES, as Action records | NO | YES | YES |
| `TRUST_ROOT_MODEL_H_REVERSE_PROXY_ASSERTED_IDENTITY` | NO | YES | NO | YES |
| `TRUST_ROOT_MODEL_I_PHYSICAL_LOCAL_CONSOLE_OR_TTY` | NO | YES | NO | YES |
| `TRUST_ROOT_MODEL_J_HYBRID_BOOTSTRAP_AND_AUTHENTICATED_CHANNEL` | NO | YES | NO | YES |
| `TRUST_ROOT_MODEL_K_NO_TRUTHFUL_SOURCE_CURRENTLY_AVAILABLE` | YES, as a negative finding | NO | NO | NO |

For each candidate, the detailed evidence, trust anchor, lifecycle, attack
surface, usability, and decision are:

### TRUST_ROOT_MODEL_A_PROCESS_LOCAL_CALLER_CONVENTION

- Evidence: Python callers and well-formed process-local data exist.
- Trust anchor: none independent; the caller asserts its own authority.
- Bootstrap/recovery/revocation: none proven; no owner lifecycle exists.
- Source-event identity: no authenticated source-message identity.
- Attack surface: any process-local caller can impersonate the convention.
- Usability: easy, but unsafe and non-auditable.
- CURRENTLY_EXISTS: NO as Human Authority; TARGET_CANDIDATE: NO; REJECTED: YES;
  NOT_PROVEN: YES. Reason: `TYPED_INTERNAL_CALLER_CONTRACT != HUMAN_AUTHORITY`.

### TRUST_ROOT_MODEL_B_OPERATING_SYSTEM_USER_AND_LOCAL_IPC_PEER_IDENTITY

- Evidence: no Unix-socket, IPC peer-credential, owner enrollment, or OS-user
  binding is present.
- Trust anchor: would be an owner-controlled OS identity and IPC policy; none
  exists in the repository.
- Bootstrap/recovery/revocation: not selected and not proven.
- Source-event identity: would require authenticated peer plus exact source
  message; absent.
- Attack surface: local process impersonation, forwarding, privilege changes,
  and stale owner mapping.
- Usability: potentially usable for a single-owner host, but deployment
  assumptions are unproven.
- CURRENTLY_EXISTS: NO; TARGET_CANDIDATE: YES; REJECTED: NO; NOT_PROVEN: YES.
  Reason: future candidate only, not a current trust root.

### TRUST_ROOT_MODEL_C_OWNER_CONFIGURED_LOCAL_SECRET_OR_TOKEN

- Evidence: no configured owner secret/token, validator, rotation, or secure
  storage is present.
- Trust anchor: would be an owner-provisioned secret; no provisioning owner is
  proven.
- Bootstrap/recovery/revocation: none selected; compromise and recovery are
  unresolved.
- Source-event identity: a secret alone would still require request/message
  binding and replay controls.
- Attack surface: disclosure, replay, forwarding, and ambiguous deployment.
- Usability: familiar but requires secure secret lifecycle.
- CURRENTLY_EXISTS: NO; TARGET_CANDIDATE: YES; REJECTED: NO; NOT_PROVEN: YES.
  Reason: no actual secret or owner lifecycle is available.

### TRUST_ROOT_MODEL_D_AUTHENTICATED_LOCAL_UI_SESSION

- Evidence: no authenticated UI, local session issuer, or session lifecycle is
  present; `session_id` is caller metadata only.
- Trust anchor: would be an owner-authenticated UI session issuer; none exists.
- Bootstrap/recovery/revocation: not selected and not proven.
- Source-event identity: would require UI-issued source events, not a raw
  session label; absent.
- Attack surface: session theft, confused deputy, forwarding, and stale state.
- Usability: could avoid unnecessary confirmation ceremony if owner-bound, but
  no such binding is currently proven.
- CURRENTLY_EXISTS: NO; TARGET_CANDIDATE: YES; REJECTED: NO; NOT_PROVEN: YES.
  Reason: no authenticated UI source exists.

### TRUST_ROOT_MODEL_E_AUTHENTICATED_API_IDENTITY

- Evidence: FastAPI routes exist, but no authentication middleware, credential
  validator, identity provider, or owner policy exists.
- Trust anchor: would be an authenticated API identity provider; none exists.
- Bootstrap/recovery/revocation: not selected and not proven.
- Source-event identity: would require authenticated request identity and exact
  operation binding; absent.
- Attack surface: credential theft, replay, proxy ambiguity, and local/remote
  exposure ambiguity.
- Usability: potentially appropriate, but deployment and owner behavior are not
  established.
- CURRENTLY_EXISTS: NO; TARGET_CANDIDATE: YES; REJECTED: NO; NOT_PROVEN: YES.
  Reason: the API is transport only.

### TRUST_ROOT_MODEL_F_SIGNED_EXTERNAL_AUTHORITY_EVENT

- Evidence: no external issuer, key trust store, signature verifier, or signed
  source event exists.
- Trust anchor: would be owner-controlled issuer keys and a trust policy; none
  is provisioned.
- Bootstrap/recovery/revocation: key enrollment, rotation, recovery, and
  revocation are all unselected and unproven.
- Source-event identity: signature could support it only after issuer trust and
  exact operation binding are established.
- Attack surface: key compromise, stale signatures, replay, and issuer
  substitution.
- Usability: strong remote semantics but potentially high owner ceremony.
- CURRENTLY_EXISTS: NO; TARGET_CANDIDATE: YES; REJECTED: NO; NOT_PROVEN: YES.
  Reason: a cryptographic shape is not a current source.

### TRUST_ROOT_MODEL_G_EXISTING_APPROVAL_UI_OR_APPROVAL_RECORD

- Evidence: approval queues and human-authorization records exist for
  capability-specific Action workflows.
- Trust anchor: Action approval state, not independently authenticated Goal
  authority; it cannot be reused across authority domains.
- Bootstrap/recovery/revocation: Action-record lifecycle does not establish an
  owner lifecycle for Human Authority.
- Source-event identity: record metadata and `session_id` do not authenticate
  the person or source event.
- Attack surface: confused-deputy escalation, replay, and Goal/Action mixing.
- Usability: existing workflow is usable for bounded Action review only.
- CURRENTLY_EXISTS: YES as Action records; TARGET_CANDIDATE: NO; REJECTED: YES;
  NOT_PROVEN: YES. Reason: Action approval is not Goal authority.

### TRUST_ROOT_MODEL_H_REVERSE_PROXY_ASSERTED_IDENTITY

- Evidence: no reverse proxy, forwarded-identity trust policy, or deployment
  configuration is present. A proxy may exist outside the repository and is not
  proven by source inspection.
- Trust anchor: would be a separately authenticated and trusted proxy boundary;
  none is established.
- Bootstrap/recovery/revocation: not selected and not proven.
- Source-event identity: forwarded headers are not authenticated source events
  without a trusted proxy channel and exact binding.
- Attack surface: header spoofing, proxy bypass, forwarding, and exposure drift.
- Usability: transparent when correctly deployed, but operationally ambiguous.
- CURRENTLY_EXISTS: NO; TARGET_CANDIDATE: YES; REJECTED: NO; NOT_PROVEN: YES.
  Reason: external deployment facts cannot be inferred from loopback binding.

### TRUST_ROOT_MODEL_I_PHYSICAL_LOCAL_CONSOLE_OR_TTY

- Evidence: no console/TTY authority adapter or physical-presence record is
  present.
- Trust anchor: would be owner-controlled physical access plus an authenticated
  local source; physical presence alone is insufficient.
- Bootstrap/recovery/revocation: not selected and not proven.
- Source-event identity: no authenticated console event identity exists.
- Attack surface: unattended terminals, local forwarding, shared accounts, and
  ambiguous operator identity.
- Usability: direct and low-friction for one owner, but not remotely auditable.
- CURRENTLY_EXISTS: NO; TARGET_CANDIDATE: YES; REJECTED: NO; NOT_PROVEN: YES.
  Reason: no physical-console source is proven.

### TRUST_ROOT_MODEL_J_HYBRID_BOOTSTRAP_AND_AUTHENTICATED_CHANNEL

- Evidence: no bootstrap ceremony, owner enrollment, authenticated channel, or
  recovery/revocation authority exists.
- Trust anchor: would combine an owner-controlled bootstrap with a later
  authenticated channel; neither side is selected.
- Bootstrap/recovery/revocation: all are requirements, not current proof.
- Source-event identity: would require the authenticated channel to bind every
  event to the enrolled generation and exact operation.
- Attack surface: bootstrap substitution, recovery downgrade, channel mix-up,
  and generation rollback.
- Usability: potentially best for continuity, but also the broadest lifecycle
  design and not justified by current evidence.
- CURRENTLY_EXISTS: NO; TARGET_CANDIDATE: YES; REJECTED: NO; NOT_PROVEN: YES.
  Reason: no hybrid source or lifecycle is proven.

### TRUST_ROOT_MODEL_K_NO_TRUTHFUL_SOURCE_CURRENTLY_AVAILABLE

- Evidence: all current substitutes fail independent owner/source, issuer,
  source-event, binding, and lifecycle requirements.
- Trust anchor: explicit negative finding over inspected repository evidence;
  this is not an authority source.
- Bootstrap/recovery/revocation: no truthful owner lifecycle exists to select.
- Source-event identity: no authenticated source event is proven.
- Attack surface: the primary risk is false promotion of an untrusted substitute.
- Usability: accurately failure-closes Human Authority rather than accepting
  ambiguous input.
- CURRENTLY_EXISTS: YES as the current negative finding; TARGET_CANDIDATE: NO;
  REJECTED: NO; NOT_PROVEN: NO. Reason: selected because no truthful source is
  currently available.

The selected trust-root decision is therefore:

```text
SELECTED_TRUST_ROOT_MODEL:
TRUST_ROOT_MODEL_K_NO_TRUTHFUL_SOURCE_CURRENTLY_AVAILABLE
```

No target implementation model is selected during M116A.

## 5. Authorized Deployment Profile Evaluation A-E

The authorized deployment taxonomy is preserved exactly:

### DEPLOYMENT_PROFILE_A_SINGLE_OWNER_LOCAL_MACHINE

Potentially a single owner operating a local machine. The loopback API fact is
compatible with this profile but does not prove it. CURRENTLY_EXISTS: NOT
PROVEN; TARGET_CANDIDATE: YES; REJECTED: NO.

### DEPLOYMENT_PROFILE_B_SINGLE_OWNER_LOCAL_NETWORK

Potentially a single owner reaching Aether over a local network. No network
exposure, reverse proxy, SSH tunnel, or owner relationship is proven.
CURRENTLY_EXISTS: NOT PROVEN; TARGET_CANDIDATE: YES; REJECTED: NO.

### DEPLOYMENT_PROFILE_C_REMOTE_SINGLE_OWNER

Potentially a single owner reaching Aether remotely. No remote exposure,
authentication, proxy, owner identity, or source boundary is proven.
CURRENTLY_EXISTS: NOT PROVEN; TARGET_CANDIDATE: YES; REJECTED: NO.

### DEPLOYMENT_PROFILE_D_MULTI_USER_REMOTE

Potentially a multi-user remote service. No multi-user policy, principal
isolation, authenticated identity, or remote deployment is proven.
CURRENTLY_EXISTS: NOT PROVEN; TARGET_CANDIDATE: YES; REJECTED: NO.

### DEPLOYMENT_PROFILE_E_NOT_PROVEN

The repository cannot establish who operates the host, whether deployment is
strictly local, whether a reverse proxy or SSH tunnelling is used, whether a
local process forwards requests, whether the actual owner is the caller, or
whether intended deployment is local-network or remote. CURRENTLY_EXISTS: YES
as the evidence state; TARGET_CANDIDATE: NO; REJECTED: NO.

The selected deployment result is:

```text
SELECTED_DEPLOYMENT_PROFILE:
DEPLOYMENT_PROFILE_E_NOT_PROVEN

OBSERVED_INTERFACE_CONTAINMENT:
LOOPBACK_UNAUTHENTICATED_PROCESS

LOOPBACK_BINDING_IS_AUTHENTICATION:
NO
```

The API currently binds to `127.0.0.1:8000`, which proves interface
containment only. Loopback is a containment fact, not authentication. Loopback
must not be promoted into owner identity or Human Authority. No target
deployment profile is selected during M116A.

## 6. Current Trust-Root State and Lifecycle Decisions

```text
CURRENT_TRUST_ROOT_STATE:
NO_AUTHENTICATED_OWNER_SOURCE_EXISTS

SOURCE_AUTHENTICATION_PROVEN:
NO

REAL_HUMAN_AUTHORITY_SOURCE_PROVEN:
NO

DIRECT_GOAL_ACCEPTANCE_PROVEN:
NO

SELECTED_BOOTSTRAP_MODEL:
NO_TRUTHFUL_OWNER_BOOTSTRAP_PROVEN

SELECTED_RECOVERY_MODEL:
NO_TRUTHFUL_OWNER_RECOVERY_PROVEN

SELECTED_REVOCATION_MODEL:
NO_TRUTHFUL_OWNER_REVOCATION_PROVEN

SELECTED_SOURCE_EVENT_MODEL:
NO_AUTHENTICATED_SOURCE_EVENT_PROVEN

SELECTED_AUTHENTICATION_OWNER:
NO_AUTHENTICATION_OWNER_PROVEN

SELECTED_AUTHORITY_EVIDENCE_OWNER:
NO_TRUTHFUL_AUTHORITY_EVIDENCE_OWNER_PROVEN

SELECTED_GOAL_BINDING_OWNER:
CORE_COORDINATION_GOAL_INTAKE
```

These identifiers describe current evidence, not a prohibition on later
selection of a truthful owner-controlled source. The current system must fail
closed rather than recover from `/chat`, Working Memory, runtime state,
identity checksums, Python callers, or Action approval records.

No owner bootstrap, recovery, revocation, or authenticated source-event
consumer is present. A future source must define owner-controlled enrollment,
recovery and generation changes, revocation and rotation, source-event identity
and integrity, exact operation binding, and failure before Goal mutation.

### Bootstrap

`SELECTED_BOOTSTRAP_MODEL` records that no truthful owner bootstrap is proven.
Self-issued runtime state, an identity seed, a caller request, or an Action
approval record cannot bootstrap its own Human Authority.

### Recovery

`SELECTED_RECOVERY_MODEL` records that no truthful owner recovery is proven. A
restart or lost credential must fail closed rather than fall back to an
unauthenticated transport or process-local state.

### Revocation

`SELECTED_REVOCATION_MODEL` records that no truthful owner revocation is
proven. Missing revocation data cannot be treated as active authority.

Aether self-integrity is not Human Authority. Action authorization cannot be
reused as Goal authority.

## 7. Direct Instruction and Authentication Boundary

```text
SELECTED_DIRECT_INSTRUCTION_MODEL:
DIRECT_MODEL_E_NO_DIRECT_ACCEPTANCE_RULE_YET_PROVEN
```

A trusted source has not yet been proven, so direct atomic Goal acceptance
cannot be proven. Explicit owner input could become a future authority source
only after an owner-controlled trust root and deployment profile are selected.
Inferred or ambiguous intent remains proposal/clarification only. Model
confidence is not authority. Aether remains responsible for context, users
should not need to provide procedures, and unnecessary confirmation ceremony
should be avoided in a future design. No direct-acceptance rule is authorized
now.

The direct-instruction candidates remain distinct:

| Model | Meaning | Current decision |
| --- | --- | --- |
| DIRECT_MODEL_A_RAW_TEXT_AS_ACCEPTANCE | Interpret arbitrary text as authority | REJECTED |
| DIRECT_MODEL_B_TYPED_INTERNAL_CALLER | Well-formed in-process operation | NOT HUMAN AUTHORITY |
| DIRECT_MODEL_C_AUTHENTICATED_OWNER_INPUT | Authenticated owner submits exact operation | FUTURE CANDIDATE ONLY |
| DIRECT_MODEL_D_INFERRED_INTENT_AS_ACCEPTANCE | Infer acceptance from intent or confidence | REJECTED |
| DIRECT_MODEL_E_NO_DIRECT_ACCEPTANCE_RULE_YET_PROVEN | No truthful direct acceptance rule exists | SELECTED CURRENT MODEL |

Source authentication remains separate from intent interpretation. Natural-
language input, a request to complete, a Goal proposal, a ThinkingProposal, and
caller metadata can describe intent or correlate a workflow; none authenticates
the source. Authentication also does not prove interpretation, Action
permission, tool execution, protected-data access, or completion.

```text
TYPED_INTERNAL_CALLER_CONTRACT != HUMAN_AUTHORITY
SOURCE_AUTHENTICATION != INTENT_INTERPRETATION
GOAL_ACCEPTANCE_NEVER_AUTHORIZES_ACTION
```

## 8. Minimum Future Evidence Status

Every category below is a future requirement, not current proof:

| Evidence category | Current status |
| --- | --- |
| owner/source identity | NOT PROVEN |
| authentication | NOT PROVEN |
| source-event identity | NOT PROVEN |
| source-event integrity | NOT PROVEN |
| exact raw instruction | NOT PROVEN |
| freshness | NOT PROVEN |
| replay protection | NOT PROVEN |
| trust-root generation | NOT PROVEN |
| revocation | NOT PROVEN |
| operation binding | NOT PROVEN |
| Goal/proposal/revision binding | NOT PROVEN |
| provenance | NOT PROVEN |

The exact minimum must be derived only after a real trust-root model and
deployment profile are selected. M116A does not recreate the M114A/M115A
oversized envelope and does not select a target implementation model.

```text
MINIMALITY_DECISION:
MINIMALITY_NOT_PROVEN
```

## 9. Evidence, Ownership, and Failure Closure

The current ownership matrix is:

| Concern | Current owner/evidence | Authority result |
| --- | --- | --- |
| HTTP/API transport | FastAPI routes | Transport only |
| Caller/session metadata | Request model and runtime propagation | Correlation only |
| Aether identity integrity | Identity guard and seed checksum | Self-integrity only |
| Goal state | Core Coordination/GoalIntake process-local owner | Canonical Goal owner, not issuer |
| Working Memory | Runtime Working Memory store | Memory, not Goal authority |
| Action approval | Approval queues/gates and capability bindings | Action-specific, not Goal authority |
| Governance | Core Governance evaluation | Non-authorizing evaluation |
| Human Authority issuer | None proven | No truthful source |
| Revocation/recovery owner | None proven | No lifecycle authority |

The only safe current behavior is failure closure:

```text
Any check fails -> reject before mutation
```

1. If no independently authenticated issuer exists, reject Human Authority.
2. If actor, issuer, source message, request, Goal, revision, operation, or
   content binding is missing, reject before mutation.
3. If validity, nonce, replay, revocation, or evidence resolution cannot be
   verified, reject before mutation.
4. If bootstrap or recovery ownership is ambiguous, require a new external
   owner ceremony; never self-authorize from runtime state.
5. If the source is authenticated but intent interpretation is uncertain,
   preserve the source evidence while requesting clarification; do not invent
   Goal content.

No current implementation is claimed for this sequence. In particular,
`VALIDATE_BEFORE_MUTATE_ONLY_ATOMICITY_NOT_PROVEN` remains true, and there is no
live source or consumer capable of proving the sequence.

## 10. Human Authority, Goal Maturity, and Build Gate

```text
TRUST_ROOT_MATURITY:
TR0_NO_TRUTHFUL_TRUST_ROOT

HUMAN_AUTHORITY_MATURITY:
HA1_REQUIRED_FIELDS_IDENTIFIED_BUT_SEMANTICS_INCOMPLETE

GOAL_INTAKE_MATURITY:
GI2_CANONICAL_OWNER_PROVEN_ENTRY_CONTRACT_INCOMPLETE

HA2_PROVEN:
NO

MINIMALITY_DECISION:
MINIMALITY_NOT_PROVEN

PRINCIPAL_DECISION:
K_NO_TRUTHFUL_OWNER_AUTHORITY_SOURCE_OR_DEPLOYMENT_PROFILE_CURRENTLY_PROVEN

BUILD_READINESS:
BUILD_NOT_JUSTIFIED
```

No Build is justified because the deployment profile is not proven; the owner
trust source is not selected; bootstrap is not selected; recovery is not
selected; revocation is not selected; authenticated source-event ownership is
not selected; the direct acceptance rule and minimum evidence are not proven.
M116A does not recommend a token, UI, OS credential, proxy, signature, or hybrid
Build. Design work and loopback containment do not advance Human Authority or
Goal maturity.

The minimum evidence is not proven and remains deferred until a real trust-root
and deployment profile are selected.

The authorized trust-root maturity scale is:

```text
TR0_NO_TRUTHFUL_TRUST_ROOT
TR1_TRUST_ROOT_REQUIREMENTS_IDENTIFIED
TR2_BOUNDED_TRUST_ROOT_CONTRACT_PROVEN_DESIGN_ONLY
TR3_BOUNDED_TRUST_ROOT_IMPLEMENTED_AND_TESTED
TR4_LIVE_AUTHENTICATED_SOURCE_BOUND_TO_GOAL_INTAKE
TR5_DURABLE_RECOVERABLE_OWNER_AUTHORITY
```

## 11. Scope Lock and Non-Goals

This record does not authorize or claim:

- production authentication or an authenticated API;
- a trusted local Human Authority adapter;
- an external identity provider or signature verifier;
- OS, terminal, hardware, or network identity as a trust root;
- owner enrollment, bootstrap, recovery, rotation, or revocation;
- a live typed Human Authority envelope or Goal operation route;
- `/chat` or any existing route as a canonical authority consumer;
- persistence, restart restoration, replay storage, or transaction atomicity;
- Goal-to-Plan runtime integration or a ThinkingProposal producer;
- Action authorization expansion, Generic Act, execution, or external effects;
- M116B, M117, or any successor milestone;
- PM approval, finalization, commit, tag, or push.

The static lock for this record is
`tests/test_milestone_116a_truthful_human_authority_trust_root_decision.py`.
The static lock must remain documentation-only and must not instantiate
production runtime, call an API, mutate data, or create authority records.

## 12. Core-Direction Review

M116A preserves the project direction:

- Aether remains one persistent mind.
- Core Coordination/GoalIntake remains canonical Goal owner.
- Human Authority remains external evidence, not a second mind.
- Authentication remains non-cognitive and separate from interpretation.
- Ambiguous input cannot silently become accepted.
- Context remains Aether's responsibility and Goal remains above procedure.
- Goal acceptance does not authorize Action.
- Action success does not prove completion; Verification remains required.
- Aether cannot appoint or replace its owner.
- No generic identity registry and no Generic Act are introduced.
- No production readiness claim is made.

No Generic Act is introduced or authorized by M116A.

```text
CORE_DRIFT_DETECTED:
NO
```

## 13. Final Decision

```text
SELECTED_TRUST_ROOT_MODEL:
TRUST_ROOT_MODEL_K_NO_TRUTHFUL_SOURCE_CURRENTLY_AVAILABLE

SELECTED_DEPLOYMENT_PROFILE:
DEPLOYMENT_PROFILE_E_NOT_PROVEN

OBSERVED_INTERFACE_CONTAINMENT:
LOOPBACK_UNAUTHENTICATED_PROCESS

LOOPBACK_BINDING_IS_AUTHENTICATION:
NO

CURRENT_TRUST_ROOT_STATE:
NO_AUTHENTICATED_OWNER_SOURCE_EXISTS

SELECTED_BOOTSTRAP_MODEL:
NO_TRUTHFUL_OWNER_BOOTSTRAP_PROVEN

SELECTED_RECOVERY_MODEL:
NO_TRUTHFUL_OWNER_RECOVERY_PROVEN

SELECTED_REVOCATION_MODEL:
NO_TRUTHFUL_OWNER_REVOCATION_PROVEN

SELECTED_SOURCE_EVENT_MODEL:
NO_AUTHENTICATED_SOURCE_EVENT_PROVEN

SELECTED_DIRECT_INSTRUCTION_MODEL:
DIRECT_MODEL_E_NO_DIRECT_ACCEPTANCE_RULE_YET_PROVEN

SELECTED_AUTHENTICATION_OWNER:
NO_AUTHENTICATION_OWNER_PROVEN

SELECTED_AUTHORITY_EVIDENCE_OWNER:
NO_TRUTHFUL_AUTHORITY_EVIDENCE_OWNER_PROVEN

SELECTED_GOAL_BINDING_OWNER:
CORE_COORDINATION_GOAL_INTAKE

PRINCIPAL_DECISION:
K_NO_TRUTHFUL_OWNER_AUTHORITY_SOURCE_OR_DEPLOYMENT_PROFILE_CURRENTLY_PROVEN

TRUST_ROOT_EXISTS_CURRENTLY: NO
TRUTHFUL_HUMAN_AUTHORITY_CURRENTLY_PROVEN: NO
TRUST_ROOT_MATURITY: TR0_NO_TRUTHFUL_TRUST_ROOT
HUMAN_AUTHORITY_MATURITY: HA1_REQUIRED_FIELDS_IDENTIFIED_BUT_SEMANTICS_INCOMPLETE
HA2_PROVEN: NO
GOAL_INTAKE_MATURITY: GI2_CANONICAL_OWNER_PROVEN_ENTRY_CONTRACT_INCOMPLETE
MINIMALITY_DECISION: MINIMALITY_NOT_PROVEN
BUILD_READINESS: BUILD_NOT_JUSTIFIED

SOURCE_AUTHENTICATION_PROVEN:
NO

REAL_HUMAN_AUTHORITY_SOURCE_PROVEN:
NO

DIRECT_GOAL_ACCEPTANCE_PROVEN:
NO

GOAL_ACCEPTANCE_AUTHORIZES_ACTION:
NO

COMPLETION_REQUIRES_VERIFICATION:
YES

GENERIC_IDENTITY_REGISTRY_INTRODUCED:
NO

OWNER_INPUT_REQUIRED_FOR_NEXT_FRONTIER:
YES

CORE_DRIFT_DETECTED:
NO

PRODUCTION_IMPLEMENTATION_PERFORMED:
NO

PROGRESS_UPDATED:
NO

COMMIT_CREATED:
NO

TAG_CREATED:
NO

PUSH_PERFORMED:
NO

NEXT_FRONTIER:
OWNER_CONTROLLED_AUTHORITY_SOURCE_AND_DEPLOYMENT_SELECTION

NEXT_MILESTONE_TYPE:
HUMAN/PROJECT-MANAGER TRUST-ROOT REQUIREMENTS DECISION

M116B_AUTHORIZED:
NO

M117_AUTHORIZED:
NO

READY_FOR_PM_REVIEW:
YES
```

M116A is complete locally as a corrected design decision only, not a
finalization.
The next step requires project-owner input about intended deployment and
acceptable owner-authentication and recovery behavior. No implementation
milestone is started or authorized by this record.
