# Aether Security Architecture

Document role: CANONICAL LIVING SECURITY-DOMAIN ARCHITECTURE

This document records the current security and authority architecture for Aether.
It is a living architecture document, not a production security implementation,
deployment verification, or replacement for historical milestone evidence.

## 1. Purpose, Authority, and Scope

The scope is the security and authority domain of one Aether persistent digital
mind. It covers the Owner boundary, the proposed Owner Authority Service (OAS),
ordinary runtime, Core Coordination, security state, source evidence, recovery,
and the status of their current design and implementation.

This document must conform to `docs/CONSTITUTION.md` and
`docs/ARCHITECTURE.md`. It must not override either document, rewrite milestone
history, claim unimplemented security, or treat static tests as deployment proof.
It does not authorize a successor milestone. It introduces no Generic Act
authority and no generalized Tool-Operation-Capability security architecture.
Existing bounded governance, policy, approval, restricted-read, and action-control
mechanisms remain current implementation facts; they are not the future Tool
Security frontier. It introduces no multi-agent or multi-instance runtime, or
public Internet exposure.

## 2. Authority Precedence and Conflict Resolution

The exact authority precedence is:

```text
CONSTITUTION
    >
ARCHITECTURE
    >
SECURITY_ARCHITECTURE
    >
CURRENT IMPLEMENTATION
```

The Constitution is the highest technology-independent authority. `docs/ARCHITECTURE.md`
governs the overall Aether system. This document is canonical for the security
domain but remains subordinate to the Constitution and overall Architecture.
Current implementation must conform to all higher authorities; implementation
behavior cannot silently rewrite architecture.

Milestone architecture documents are not another authority level. They are:

```text
IMMUTABLE HISTORICAL EVIDENCE
+
DECISION PROVENANCE
+
TRACEABILITY RECORDS
```

Finalized M117A evidence is not modified or reinterpreted by this document.
`PROGRESS.md` is a project-status ledger, not an architecture authority source.

Conflicts resolve upward through the precedence chain. An implementation conflict
is an implementation defect, not an architecture rewrite. A security design
replacement requires explicit authorization and the evolution rules in section 17.

## 3. Orthogonal Security Status Dimensions

Every material security capability or invariant uses four independent dimensions:

```text
DECISION_STATUS:
PROPOSED | CURRENT | SUPERSEDED | REJECTED

DESIGN_STATUS:
UNDEFINED | PARTIAL | DESIGN_PROVEN

IMPLEMENTATION_STATUS:
NOT_IMPLEMENTED | PARTIALLY_IMPLEMENTED | IMPLEMENTED

VERIFICATION_STATUS:
NOT_VERIFIED | TEST_VERIFIED | DEPLOYMENT_VERIFIED
```

These dimensions are not interchangeable:

```text
DECISION_STATUS: CURRENT
does not imply
DESIGN_STATUS: DESIGN_PROVEN

DESIGN_STATUS: DESIGN_PROVEN
does not imply
IMPLEMENTATION_STATUS: IMPLEMENTED

IMPLEMENTATION_STATUS: IMPLEMENTED
does not imply
VERIFICATION_STATUS: TEST_VERIFIED

VERIFICATION_STATUS: TEST_VERIFIED
does not imply
VERIFICATION_STATUS: DEPLOYMENT_VERIFIED

MILESTONE_FINALIZED
does not imply
LIVE_SECURITY_PROVEN
```

`TEST_VERIFIED` means only that explicitly identified tests passed for the stated
layer and bounded scope. It is not runtime security proof or deployment security
proof. `DEPLOYMENT_VERIFIED` requires separately reviewed evidence from a real
bounded deployment identifying the applicable host, OS, configuration, network
boundary, permission boundary, evidence time, and known limitations.

No single combined maturity or security-status field replaces these dimensions.

## 4. Current Deployment and Trust Assumptions

The repository currently configures the API at `127.0.0.1:8000`. The target
security direction is private LAN access to one host and one Aether Instance, but
that target is not a deployed trust boundary. LAN location, hostname, OS account,
session identifier, IP address, process placement, caller convention, or static
documentation is not by itself Owner authority.

The current repository has no authenticated Owner source, authentication-facing
OAS boundary, WebAuthn, live TLS Owner channel, deployed OS-principal boundary,
live recovery ceremony, AuthenticatedSourceEvent issuance, or Core receipt
integration.

## 5. Security and Authority Taxonomy

The **Owner** is the intended human authority for one Aether Instance. The **OAS**
is the selected separate security service boundary that would terminate and
validate Owner authentication and issue bounded source evidence. OAS is not a
cognitive agent and cannot own canonical Goal meaning.

**Ordinary runtime** includes Aether runtime code, API handlers, models, tools,
plugins, Working Memory, and process-local callers. It cannot mint Owner evidence,
access protected signing material, or become a universal authority source.

**Core Coordination** is the internal cross-cutting owner of canonical Goal state
and, in the selected design, the Core-owned AuthenticatedSourceEventReceipt. It
does not mint or sign Owner evidence and does not turn authentication into intent
interpretation.

No generalized Tool-Operation-Capability security architecture is currently
established. No Generic Act authority exists. Existing bounded policy, approval,
restricted-read, and action-control mechanisms remain current implementation
facts. Those bounded mechanisms are not the future Tool Security frontier. The
future Tool-Operation-Capability frontier remains separate and unproven.

The preserved boundaries are:

```text
AUTHENTICATION != INTENT_INTERPRETATION
GOAL_ACCEPTANCE != ACTION_AUTHORIZATION
ACTION_SUCCESS != COMPLETION
COMPLETION REQUIRES OBSERVATION + VERIFICATION
```

## 6. Architectural Trust Boundaries

The selected design boundary is `OWNER <-> AETHER INSTANCE`, constrained to one
host, one Aether Instance, one true Owner, and private LAN access. The selected
target separates a local OS-attested bootstrap/recovery presence boundary from a
later authenticated LAN channel.

The target OAS boundary uses a separate OS principal, restricted IPC, protected
authority material, direct TLS termination, exact origin/RP ID validation, and an
ordinary runtime that receives only bounded verifiable results. A proxy is not
trusted implicitly. Direct backend bypass is rejected by the target design.

These are design properties, not deployed security facts. Their implementation
and deployment verification status remains separate in section 14.

## 7. Owner Trust-Root Lifecycle

The finalized M117A target uses this lifecycle:

```text
UNCLAIMED -> CLAIM_PENDING -> OWNED
OWNED -> RECOVERY_PENDING -> OWNED
CLAIM_PENDING -> UNCLAIMED
```

Bootstrap Phase 1 is intended to establish an immutable instance identity, trust
generation, Claim Token, durable pending transaction, and audit without creating
a credential, session, or `OWNED` state. Phase 2 is intended to complete a valid
pending transaction through OAS and a separate WebAuthn registration ceremony.

The target bootstrap presence is an OS-attested local-console privileged IPC
contract. The target recovery presence is OS-attested local-console presence plus
offline material. An ordinary authenticated session cannot recover the root.
These contracts remain design-only and are not live OS evidence.

## 8. Authentication Channel Architecture

The target authenticated LAN channel terminates at OAS over direct TLS. OAS owns
the exact configured HTTPS origin and RP ID policy. Proxy forwarding and client
identity headers are not trusted by default, and the ordinary backend is not a
LAN authority listener.

WebAuthn registration and authentication are separate ceremonies. Registration
uses `webauthn.create` and an OAS-owned registration challenge bound to the
pending Claim transaction. Later authentication uses `webauthn.get` and a separate
authentication challenge. A challenge from one ceremony cannot satisfy the other.

The target session is server-side, opaque, short-lived, instance/credential/
generation-bound, and revocable. The target CSRF/origin contract includes exact
origin validation, restrictive cookie and CORS controls, a per-session CSRF token,
Fetch Metadata where available, and request binding. None of these target
properties is currently implemented or deployment-verified.

## 9. Canonical Security State and Audit

The target OAS durable security store owns canonical security state and its
non-secret `OwnerSecurityAuditEvent` in one transaction:

```text
SECURITY_STATE_COMMIT
+
CANONICAL_SECURITY_AUDIT_COMMIT
=
ONE_ATOMIC_SECURITY_TRANSACTION
```

The target record families include instance trust, Claim Token, Owner credential,
Owner session, recovery, authentication challenge, authenticated source event,
and Owner security audit. Private credentials, recovery plaintext, raw session
handles, Claim Token plaintext, and signing keys remain inside the protected OAS
boundary.

M118A implements the bounded OAS security-kernel store and its canonical state
plus audit transaction using SQLite. The implementation binds the complete
transaction request and committed audit event, validates paired evidence before
retry, validates the v1 store structure and SQLite integrity, and applies
deterministic resource bounds to canonical JSON. This establishes durable state,
not Owner authentication, a separate OS principal, or deployment verification.
The authentication-facing OAS remains unimplemented.

The original finalized M118A commit and annotated tag remain immutable historical
provenance:

```text
M118A_FINAL_COMMIT: a5188ae7e3aa1454bac1c21e5c5081e441687397
M118A_FINAL_TAG: milestone-118A-oas-durable-security-kernel-foundation
M118A_FINAL_TAG_OBJECT: 297a3620664eb025f8aeb1516fd435a94a85bea7
M118A_FINAL_TAG_PEELED_TARGET: a5188ae7e3aa1454bac1c21e5c5081e441687397
```

PM acceptance was initially held after a reproducible concurrent first-open
SQLite defect was confirmed: first-time WAL negotiation could return
`SQLITE_BUSY` before migration acquired `BEGIN IMMEDIATE`, and the old setup
path incorrectly translated that contention into `CorruptSchemaError`.

The bounded corrective pass was PM-accepted and is finalized by the corrective
Git closure. The connection boundary is explicit:

1. Open SQLite, enable foreign keys, and establish a bounded monotonic retry
   deadline of `2.0` seconds for first-open WAL setup.
2. Read the current journal mode. If it is already `WAL`, do not negotiate WAL
   again. Otherwise execute `PRAGMA journal_mode = WAL` with retries only for
   SQLite primary result codes `SQLITE_BUSY` or `SQLITE_LOCKED`.
3. Use exponential backoff beginning at `0.005` seconds and capped at `0.05`
   seconds. Exhaustion raises `DatabaseUnavailableError` with the original
   SQLite exception as its cause; there is no indefinite retry and no fallback
   to a weaker journal mode.
4. Verify the effective journal mode is exactly `WAL`, restore the normal
   `10000` millisecond busy timeout, set `PRAGMA synchronous = FULL`, and verify
   both synchronous `FULL` and foreign-key enforcement before returning a
   connection.
5. Only after connection setup succeeds does `migrate()` acquire `BEGIN
   IMMEDIATE`, create or validate the schema, and commit. WAL negotiation is
   not itself a canonical security-state transaction.

Transient SQLite contention is not store corruption. Actual malformed SQLite,
unsupported schema versions, and structural or integrity violations remain
separately classified as `CorruptSchemaError`. The code/dependency separation
remains a static boundary only; it is not OS/process isolation. Deployment
verification remains `NO`.

The request digest is SHA-256 over canonical JSON containing the domain
`aether.oas.security-kernel.request`, contract version, `transaction_id`,
`idempotency_key`, `aether_instance_id`, `expected_trust_generation`,
`exact_operation`, and payload. The audit-evidence digest is SHA-256 over
canonical JSON containing the domain `aether.oas.security-kernel.audit-evidence`,
evidence version, audit and transaction IDs, both generations, exact operation,
canonical request digest, idempotency key, committed result digest, event kind,
affected state reference, committed result classification, result marker, and
timestamp. Both representations are non-secret and deterministic.

The v1 canonical JSON limits are maximum depth `16`, encoded size `16384`
bytes, `128` collection items, `128` UTF-8 key bytes, `4096` UTF-8 string bytes,
and `128` integer digits. Unsupported values, non-finite numbers, and
secret-bearing fields are rejected.

## 10. Authenticated Source Evidence Boundary

OAS is the target issuer and signer of bounded `AuthenticatedSourceEvent`
evidence after authentication termination and exact request validation. The event
is not canonical Goal state. Core Coordination is the target owner of the durable
`AuthenticatedSourceEventReceipt` and canonical Goal state.

The selected source-event consumption model separates mutating and read-only Goal
operations. `PROPOSE_GOAL` and `ACCEPT_GOAL` target one Core transaction that
atomically records the receipt and bound Goal mutation. `GET_GOAL_STATUS` targets
one Core transaction that atomically records the receipt and a bounded result
snapshot or digest without a Goal transition.

No source-event issuer, receipt integration, or authenticated Goal operation is
live. Static M117A tests verify documentation structure only and do not verify a
runtime trust root.

## 11. Recovery, Revocation, and Higher Assurance

Recovery remains separate from ordinary authenticated sessions. The target uses
local presence plus offline high-entropy recovery material, protected verifiers,
attempt limits, explicit consumption or rotation, generation rotation, session
invalidation, and audit atomicity.

The target revocation model supports credential revocation, session revocation,
generation invalidation, recovery replacement, and recovery-material rotation. A
synced passkey is treated as one logical credential; logical revocation is not a
claim of physical-device revocation.

No recovery ceremony, live session issuer, revocation service, signing key, or
higher-assurance deployment exists in the current implementation.

## 12. Backup, Restore, Migration, Clone, and Split-Brain

The target distinctions are:

```text
BACKUP != RESTORE
BACKUP != CLONE_AUTHORIZATION
RESTORE != MIGRATION
CLONE_OR_FORK != SAME_ACTIVE_AETHER_IDENTITY
```

Backup is passive and excludes active authority material, sessions, Claim Tokens,
challenges, and transient replay state. Controlled restore creates a new trust
generation and invalidates stale authority. Migration requires coordinated source
quiescence and destination activation. A clone or fork receives a new
`aether_instance_id` and a new Owner trust root.

Absolute global split-brain prevention is not proven without external or hardware
coordination. No cloud or global coordinator is introduced by this architecture.

## 13. Relationship to the Aether Execution Chain

Aether remains one mind with the execution chain:

```text
Receive Goal -> Understand -> Think -> Plan -> Act -> Observe -> Verify
-> Critic -> Repair -> Learn -> Report
```

Owner authentication is an evidence boundary, not intent interpretation. Owner
authentication does not grant authority to tools, operations, capabilities, or
Generic Act. Core
Coordination remains the canonical Goal owner. Goal acceptance does not authorize
Action, Action success does not prove completion, and completion requires
Observation and Verification. Security architecture does not create a separate
agent, cognitive authority, Generic Act authority, or generalized
Tool-Operation-Capability security architecture. Existing bounded policy,
approval, restricted-read, and action-control mechanisms remain current
implementation facts and are not generalized Tool authority.

## 14. Current Security Status Matrix

Each row carries all four independent status dimensions. A target design status
does not promote that target to implementation or deployment verification.

| Capability or invariant | DECISION_STATUS | DESIGN_STATUS | IMPLEMENTATION_STATUS | VERIFICATION_STATUS | Evidence or limitation |
| --- | --- | --- | --- | --- | --- |
| one Owner per Aether Instance | CURRENT | DESIGN_PROVEN | NOT_IMPLEMENTED | NOT_VERIFIED | M117A design record; no live trust root |
| hybrid bootstrap plus authenticated channel | CURRENT | DESIGN_PROVEN | NOT_IMPLEMENTED | NOT_VERIFIED | M117A design record; target only |
| OS-attested local-console bootstrap | CURRENT | DESIGN_PROVEN | NOT_IMPLEMENTED | NOT_VERIFIED | M117A/M119A design records; no live OS evidence |
| OS-attested recovery plus offline material | CURRENT | DESIGN_PROVEN | NOT_IMPLEMENTED | NOT_VERIFIED | M117A design record; no live ceremony |
| separate-principal OAS boundary | CURRENT | DESIGN_PROVEN | NOT_IMPLEMENTED | NOT_VERIFIED | M117A/M119A design records; no authentication-facing OAS boundary |
| direct TLS and exact origin/RP ID | CURRENT | DESIGN_PROVEN | NOT_IMPLEMENTED | NOT_VERIFIED | M117A design record; current API is loopback |
| WebAuthn registration/authentication separation | CURRENT | DESIGN_PROVEN | NOT_IMPLEMENTED | NOT_VERIFIED | M117A design record; no WebAuthn |
| server-side revocable Owner sessions | CURRENT | DESIGN_PROVEN | NOT_IMPLEMENTED | NOT_VERIFIED | M117A design record; no live session issuer |
| CSRF/origin and proxy-boundary controls | CURRENT | DESIGN_PROVEN | NOT_IMPLEMENTED | NOT_VERIFIED | M117A design record; no live Owner channel |
| canonical security state plus audit atomicity | CURRENT | DESIGN_PROVEN | NOT_IMPLEMENTED | NOT_VERIFIED | full target includes authentication-facing OAS record families; bounded M118A subset is separate below |
| bounded canonical OAS security-kernel state plus audit atomicity | CURRENT | DESIGN_PROVEN | IMPLEMENTED | TEST_VERIFIED | bounded M118A SQLite state-plus-audit transaction; no authentication or deployment claim |
| OAS AuthenticatedSourceEvent issuance | CURRENT | DESIGN_PROVEN | NOT_IMPLEMENTED | NOT_VERIFIED | M117A design record; no issuer |
| Core receipt and Goal operation transactions | CURRENT | DESIGN_PROVEN | NOT_IMPLEMENTED | NOT_VERIFIED | M117A design record; no integration |
| recovery separate from ordinary sessions | CURRENT | DESIGN_PROVEN | NOT_IMPLEMENTED | NOT_VERIFIED | M117A design record; no recovery service |
| backup/restore/clone trust separation | CURRENT | DESIGN_PROVEN | NOT_IMPLEMENTED | NOT_VERIFIED | M117A design record; no deployment |
| absolute global split-brain prevention | CURRENT | PARTIAL | NOT_IMPLEMENTED | NOT_VERIFIED | Not proven without external or hardware coordination |
| identity-seed integrity guard | CURRENT | PARTIAL | IMPLEMENTED | TEST_VERIFIED | `aether/identity/guard.py`; `tests/test_identity_guard.py`; bounded file-integrity primitive only |
| bounded governance, policy, approval, restricted-read, and action controls | CURRENT | PARTIAL | IMPLEMENTED | TEST_VERIFIED | `aether/core/governance.py`, `aether/action/policy_gate.py`; `tests/test_core_loop.py`, `tests/test_policy_gate.py`, `tests/test_chat_api.py`; not Owner authentication or generalized Tool authority |
| current `/chat` policy and default-deny execution surface | CURRENT | PARTIAL | IMPLEMENTED | TEST_VERIFIED | `aether/core/governance.py`, `aether/action/policy_gate.py`; pending review and default-deny behavior only |
| generalized Tool-Operation-Capability security architecture | CURRENT | UNDEFINED | NOT_IMPLEMENTED | NOT_VERIFIED | Separate future Tool Security frontier; bounded controls above do not establish it |
| immutable `aether_instance_id` and trust-generation binding | CURRENT | DESIGN_PROVEN | IMPLEMENTED | TEST_VERIFIED | bounded M118A store constraint and stale-generation checks; no live Owner source |
| Owner lifecycle-state foundation | CURRENT | DESIGN_PROVEN | IMPLEMENTED | TEST_VERIFIED | bounded four-state transition machine; test-only callers do not prove Owner authorization |
| security transaction identity and replay/conflict/idempotency primitives | CURRENT | DESIGN_PROVEN | IMPLEMENTED | TEST_VERIFIED | unique transaction/idempotency identities and complete versioned request digest binding |
| schema and migration foundation | CURRENT | DESIGN_PROVEN | IMPLEMENTED | TEST_VERIFIED | deterministic SQLite schema v1 initialization, validation, and idempotent migration |
| ordinary-runtime direct OAS mutation boundary | CURRENT | PARTIAL | IMPLEMENTED | TEST_VERIFIED | repository-wide AST lock, empty public package surface, explicit store path, and stdlib-only kernel imports; code/dependency boundary is not OS or process isolation |
| bounded canonical OAS IPC framing | CURRENT | DESIGN_PROVEN | IMPLEMENTED | TEST_VERIFIED | M120A versioned canonical JSON, digest binding, endpoint vocabularies, duplicate/unknown rejection, and resource bounds; no authentication claim |
| exact systemd socket-activation descriptor intake | CURRENT | DESIGN_PROVEN | IMPLEMENTED | TEST_VERIFIED | M120A exact runtime/bootstrap/broker descriptors, AF_UNIX/SOCK_SEQPACKET/path/owner/group/mode and fail-closed Linux kernel identity checks; no deployed unit or socket claim |
| bounded OAS runtime service foundation | CURRENT | DESIGN_PROVEN | IMPLEMENTED | TEST_VERIFIED | M120A real AF_UNIX service, SO_PEERCRED uid/gid/pid intake, 32-active/64-queued admission, bounded I/O and shutdown polling, and redacted status read; outstanding handlers are not forcibly terminated |
| bootstrap and broker fail-closed operation boundary | CURRENT | DESIGN_PROVEN | IMPLEMENTED | TEST_VERIFIED | M120A endpoint-specific allowlists return NOT_IMPLEMENTED without canonical mutation; authentication and authorization remain unimplemented |
| repository-to-host activation and rollback contract | CURRENT | DESIGN_PROVEN | NOT_IMPLEMENTED | TEST_VERIFIED | M121A design-only root-owned release identity, activation, quiesce, generation, signing, and rollback contract; no Build or host deployment |

## 15. Current Implemented Security Surface

Direct repository inspection identifies only lower-level safeguards:

- `config/aether.yaml` configures the API on loopback `127.0.0.1:8000`.
- The identity guard stores and checks an identity-seed SHA-256 integrity state.
- Core Governance and the policy gate evaluate authorization envelopes for the
  current process-local action surface.
- The current chat loop keeps tool execution disabled and returns pending review
  structures rather than performing automatic tool execution.
- Existing tests cover these bounded primitives and current API behavior.
- The bounded M118A OAS security kernel persists instance trust, lifecycle state,
  security transactions, and canonical audit events in a SQLite store under the
  explicitly supplied private store path.
- The M118A kernel requires exact transaction identity, instance and generation
  binding, operation/digest binding including the idempotency identity, and
  commits canonical state plus audit as one SQLite transaction.
- The request digest includes a versioned OAS domain separator, transaction ID,
  idempotency key, instance ID, expected generation, exact operation, and
  canonical payload.
- The audit evidence digest includes a versioned OAS audit domain, audit and
  transaction IDs, both generations, operation, request digest, idempotency key,
  result digest, event kind, state reference, result classification, result
  marker, and timestamp.
- A recorded retry is returned only after canonical result, result digest,
  transaction status/bindings, and exactly one consistent audit event are
  verified. Inconsistent evidence fails closed.
- The M118A module is not imported by any production module outside `aether/oas`;
  `aether.oas` has an empty public package surface and exposes no mutation API;
  the kernel requires an explicit store path. This is a static code/dependency boundary only, not OS, process,
  deployment, credential, or malicious same-process isolation.
- The repository-wide AST lock covers the production source tree, while the
  reverse kernel dependency lock permits only standard-library imports.
- The complete transaction request and complete versioned non-secret audit-evidence
  digest are independently bound; exactly one consistent audit event
  is required for a committed retry.
- Canonical JSON rejects secret-bearing fields and unsupported/non-finite values,
  and enforces fixed depth, encoded-size, collection, key, string, and integer
  limits defined by the kernel.
- M120A adds a standalone bounded OAS IPC foundation under `aether/oas`: canonical
  versioned request/response framing, payload digest binding, exact endpoint
  vocabularies, strict systemd socket-activation intake, kernel peer credentials,
  bounded 32-active/64-queued request admission, deadline-aware receive/response
  I/O, bounded shutdown polling, and a redacted runtime status read. Bootstrap and
  broker operations fail closed and do not mutate canonical security state.
- M120A is a repository-tested service foundation only. It does not provide Owner
  authentication, WebAuthn, TLS, live OS-principal deployment, authenticated source
  evidence, Core receipt integration, or deployment verification. Socket activation
  and principal expectations remain explicit deployment-contract inputs rather than
  host evidence.
- The corrective M120A proof fails closed when Linux `/proc/net/unix` identity
  evidence is unavailable, malformed, oversized, or non-matching; portable
  pathname checks are not treated as equivalent Linux kernel proof. Lifecycle
  admission and reservation accounting are condition-guarded and future-backed.
  Shutdown cancels queued work, closes tracked client connections, calls the
  executor's non-waiting cancellation API, and polls tracked completion only until
  the caller's timeout. A worker that cannot be interrupted remains explicitly
  outstanding rather than being represented as stopped.
- Request deadlines are absolute caller values. Known receive and response I/O use
  the remaining budget, expiry is checked before dispatch and before returning a
  result, and typed deadline failures are classified without exception-string
  matching. The M118A status read itself is not forcibly interruptible by M120A;
  the service therefore never reports a successful status after expiry, but a slow
   underlying read may remain an outstanding worker beyond a bounded shutdown call.
   This is a documented M120A limitation and remains deployment-unverified.

M121A canonizes a repository-to-host deployment and rollback contract as design and
discovery evidence only. The contract uses one root-owned authoritative activation
record, a versioned and signed release identity, explicit candidate/activation/
commit/rollback states, pre-replacement quiescence, generation-specific gates,
bounded monotonic activation deadlines, and fail-closed readiness and smoke checks.
The future repository Build inventory and isolated proof stage remain separate from
target deployment and deployment review. No M121A production entrypoint, manifest,
verifier, unit bundle, installer, lifecycle tool, host artifact, or deployment has
been implemented or verified.

The current implementation truth is also explicit: no authenticated or
deployment-verified OAS boundary; no live authenticated Owner source; no WebAuthn;
no live TLS Owner channel; no deployed OS-principal boundary; no live recovery ceremony; no AuthenticatedSourceEvent
issuance; no Core receipt integration; HA1 remains incomplete; GI2 remains
incomplete; no Generic Act authority; no generalized Tool-Operation-Capability
security architecture; no unrestricted Action authority; existing bounded
governance, policy, approval, restricted-read, and action-control mechanisms
remain current implementation facts; no public Internet; no multi-instance
runtime; and no multi-agent runtime expansion. Owner authentication does not grant
authority to tools, operations, capabilities, or Generic Act.
The preceding canonization gate created no M118A implementation artifact; the
separately authorized M118A implementation was historically finalized by the
Git closure recorded below. The post-finalization concurrency correction is
PM-accepted and durable in the corrective Git closure; it does not alter that
historical closure.

These primitives do not establish a truthful human source, OAS, WebAuthn, TLS
Owner channel, OS-principal boundary, recovery root, source-event issuer, Core
receipt, or deployment-verifiable security architecture.

## 16. Future and Unproven Security Frontiers

The following remain future or unproven: live Owner trust-root enrollment;
authentication-facing OAS implementation; WebAuthn; TLS/DNS/certificate/LAN listener deployment; OS
attestation; Claim Token human delivery; recovery ceremonies; live sessions; real
signing keys; AuthenticatedSourceEvent issuance; Core receipt and Goal Intake
integration; deployment verification; global split-brain coordination; and any
security expansion beyond the one-mind Owner boundary.

M118A is a separately authorized bounded foundation Build recorded below as
started and historically finalized; this finalization does not authorize a
successor. Its PM acceptance is distinct from Git finalization.

The post-finalization correction state is explicit:

```text
M118A_GIT_FINALIZED: YES
M118A_PM_ACCEPTED: YES
M118A_CONCURRENCY_DEFECT_CONFIRMED: YES
M118A_CONCURRENCY_CORRECTION_IMPLEMENTED_LOCALLY: YES
M118A_CONCURRENCY_CORRECTION_PENDING_PM_REVIEW: NO
M118A_CONCURRENCY_CORRECTION_TEST_VERIFIED: YES
M118A_CONCURRENCY_CORRECTION_GIT_DURABLE: YES
DEPLOYMENT_VERIFIED: NO
PROGRESS_UPDATED: YES
COMMIT_CREATED: YES
TAG_CREATED: YES
PUSH_PERFORMED: YES
SUCCESSOR_MILESTONE_AUTHORIZED: NO
```

M119A is the current, PM-accepted design decision extending the separate-principal
OAS boundary from a design direction into an internally executable host-security
contract. The selected overall model is Model D: a dedicated OAS boundary plus a
bounded helper/broker mechanism. The selected launcher is a root-owned,
systemd-activated AF_UNIX owner broker. The target principals are distinct
`aether-owner`, `aether-runtime`, `aether-oas`, `aether-bootstrap`, and `root`
roles; the ordinary runtime never shares the Owner uid or inherits Owner session,
TTY, sudo, polkit, group, environment, or credential authority.

The owner broker authenticates the kernel peer with `SO_PEERCRED`, requires an
active local non-remote TTY logind session, performs fresh PAM authentication,
and requires a same-TTY one-use confirmation nonce. It retains a one-use,
instance/generation-bound authorization context in memory and launches only the
fixed helper as `aether-bootstrap` over an inherited private descriptor. Systemd
owns and activates the runtime, bootstrap, broker, and owner-broker sockets;
OAS validates exact descriptor identity and accepts only bounded allowlisted
operations. This contract does not authorize arbitrary commands, paths, SQL,
Generic Act, or generalized Tool-Operation-Capability authority.

M119A remains design proof only: `IMPLEMENTATION_STATUS: NOT_IMPLEMENTED`,
`VERIFICATION_STATUS: TEST_VERIFIED`, and `DEPLOYMENT_VERIFIED: NO`. The current
host has no selected principals, units, sockets, or deployed boundary. A future
Build remains separately authorized only for PM review; no Build or successor is
authorized by M119A.

M120A is the separately authorized bounded implementation pass for the executable
OAS IPC/service foundation. Its production code and named adversarial tests are
implemented and test-verified, but no host deployment is claimed. The M120A
implementation does not promote the authentication-facing OAS boundary or any
Owner authority path to live security.

## 17. Security Architecture Evolution Rules

Every future security-affecting milestone must classify its effect as exactly one
of:

```text
NO_CHANGE | EXTEND | REPLACE | SUPERSEDE
```

It must preserve immutable historical milestone records, update this document when
current architecture or status changes, cite the responsible milestone and
bounded evidence, identify affected status dimensions independently, leave
unaffected dimensions unchanged, and include applicable tests or deployment
evidence. Explicit authorization is required before replacing a `CURRENT` design.
An ordinary refactor must never silently alter the trust model.

A status may move to `IMPLEMENTED` only when corresponding production code exists.
It may move to `TEST_VERIFIED` only when named, bounded test evidence exists. It
may move to `DEPLOYMENT_VERIFIED` only through separately reviewed real-deployment
evidence. Test evidence is never deployment evidence.

## 18. Milestone and Evidence Traceability

M117A is frozen design evidence and decision provenance supporting the current
bounded single-owner LAN trust-root direction. M117A is not another layer in the
current authority precedence chain. Current normative authority comes from the
Constitution, Architecture, and the subordinate canonical Security Architecture.
M117A remains immutable historical evidence and traceability. A later authorized
decision may supersede a current security design without rewriting M117A.

The M117A evidence reference is:

```text
Evidence:
docs/architecture/MILESTONE_117A_SINGLE_OWNER_LAN_TRUST_ROOT_CONTRACT_PROOF.md
Approved artifact SHA-256:
a56d3d433cd787f7ee902c0861953b604fd20861d3e9adabcd5adcaefee9673b
Static-lock SHA-256:
b6c150821b9d996fe2f6982c2062b937d3c5bcc9381a152598d0446c88e19d85
TR2_PROVEN: YES_DESIGN_ONLY
M117A_FINALIZED: YES
```

M117A evidence is immutable historical evidence, decision provenance, and
traceability. It does not prove live security. The current implementation truth
is recorded in sections 4, 14, and 15 rather than inferred from milestone status.

The M119A evidence reference is:

```text
Evidence:
docs/architecture/MILESTONE_119A_OAS_SEPARATE_PRINCIPAL_RUNTIME_AND_PRIVILEGED_IPC_BOUNDARY_PROOF.md
Finalized artifact SHA-256:
2f6d36d503a41aec1513605cfc26bd77755aa0d0fd821683b2a783513193646b
Static-lock:
tests/test_milestone_119a_oas_separate_principal_runtime_and_privileged_ipc_boundary_proof.py
Finalized static-lock SHA-256:
780dd0da75733f8443abe4817f90d95526dbddc477c1e420bd843357b0a17e50
Selected exit: EXIT_A
M119A_AUTHORIZED: YES
M119A_STARTED: YES
M119A_FINALIZED: YES
DECISION_STATUS: CURRENT
DESIGN_STATUS: DESIGN_PROVEN
IMPLEMENTATION_STATUS: NOT_IMPLEMENTED
VERIFICATION_STATUS: TEST_VERIFIED
DEPLOYMENT_VERIFIED: NO
BUILD_JUSTIFIED_FOR_PM_REVIEW: YES
BUILD_AUTHORIZED: NO
PM_ACCEPTED: YES
SUCCESSOR_NUMBER_ASSIGNED: NO
```

M119A is finalized design evidence and current security-domain traceability. It
does not prove live authentication, OS separation, deployment, or production
security, and it does not authorize a successor milestone.

The M118A implementation boundary is:

```text
M118A - Owner Authority Service Durable Security Kernel Foundation Build
M118A_AUTHORIZED: YES
M118A_STARTED: YES
M118A_FINALIZED: YES
```

M118A in scope:

- OAS domain/service boundary;
- canonical durable OAS security-state foundation;
- `aether_instance_id` and trust-generation binding;
- Owner lifecycle-state foundation;
- security transaction identity;
- replay/conflict/idempotency primitives;
- complete versioned request-digest binding;
- complete versioned non-secret audit-evidence digest binding;
- atomic canonical state plus `OwnerSecurityAuditEvent` commit;
- crash, rollback, retry, concurrency, and fault-injection proof;
- code/dependency boundary preventing ordinary-runtime direct mutation;
- required schema/migration and SQLite integrity foundation;
- deterministic bounded canonical JSON serialization.

M118A out of scope:

- WebAuthn;
- TLS, DNS, certificates, or LAN listeners;
- real local-console helper or OS attestation;
- Claim Token human delivery;
- recovery ceremonies;
- live sessions;
- real signing keys;
- AuthenticatedSourceEvent issuance;
- AuthenticatedSourceEventReceipt;
- Core Coordination or Goal Intake integration;
- routes, `/chat`, UI, or public APIs;
- Generic Act;
- generalized Tool-Operation-Capability authority;
- public Internet;
- multi-instance runtime;
- multi-agent runtime.

The preceding canonization gate did not start M118A. This separately authorized
implementation pass has started and finalized M118A. The three future
constitutional principles identified for governance review are not accepted
constitutional text and belong only in the external Phase 1 summary.

The M120A implementation boundary is:

```text
M120A - OAS Socket-Activated Service and Bounded IPC Foundation
M120A_AUTHORIZED: YES
M120A_STARTED: YES
M120A_FINALIZED: YES
DECISION_STATUS: CURRENT
DESIGN_STATUS: DESIGN_PROVEN
IMPLEMENTATION_STATUS: IMPLEMENTED
VERIFICATION_STATUS: TEST_VERIFIED
DEPLOYMENT_VERIFIED: NO
BUILD_AUTHORIZED: YES
SUCCESSOR_NUMBER_ASSIGNED: NO
```

M120A evidence reference:

```text
Production:
aether/oas/ipc_protocol.py
aether/oas/socket_activation.py
aether/oas/service.py
Static and AF_UNIX test lock:
tests/test_m120a_oas_socket_activated_service_bounded_ipc_foundation.py
```

M120A is limited to bounded IPC/service mechanics and fail-closed endpoint
scaffolding. It excludes Owner authentication, WebAuthn, TLS, live systemd or OS
principal deployment, credential issuance, authenticated source events, Core
receipt integration, Generic Act, generalized Tool-Operation-Capability authority,
public Internet, multi-instance runtime, and multi-agent runtime.

The M121A evidence reference is:

```text
Evidence:
docs/architecture/MILESTONE_121A_OAS_REPOSITORY_TO_HOST_DEPLOYMENT_AND_ROLLBACK_CONTRACT_PROOF.md
Approved artifact SHA-256:
0c3f81f9f8486f912ba28546fd6e23457a88ef4e75f2d9c66628e24f05ff48eb
Static-lock:
tests/test_milestone_121a_oas_repository_to_host_deployment_and_rollback_contract_proof.py
Original static-lock SHA-256:
6f670e78a3eec5c4ac386822f120c0a24ac557ba09ae946d9d33614dabd39d5c
Approved static-lock SHA-256:
32fe0862b6ac8dad5b243772630d4d33ffb30258702b7b8ed0df522ea08dd087
PM disposition: APPROVE_M121A_FINALIZATION
M121A_AUTHORIZED: YES
M121A_STARTED: YES
M121A_FINALIZED: YES
DECISION_STATUS: CURRENT
DESIGN_STATUS: DESIGN_PROVEN
IMPLEMENTATION_STATUS: NOT_IMPLEMENTED
VERIFICATION_STATUS: TEST_VERIFIED
DEPLOYMENT_VERIFIED: NO
SELECTED_EXIT: EXIT_A
BUILD_AUTHORIZED: NO
HOST_MUTATION_PERFORMED: NO
PM_ACCEPTED: YES
PROGRESS_UPDATED: YES
SECURITY_ARCHITECTURE_UPDATED: YES
COMMIT_CREATED: YES
TAG_CREATED: YES
PUSH_PERFORMED: YES
SUCCESSOR_AUTHORIZED: NO
SUCCESSOR_NUMBER_ASSIGNED: NO
```

M121A remains design/discovery and security-contract proof only. Its two source
artifacts are immutable evidence and remain byte-for-byte unchanged; the future
repository deployment-artifact Build, isolated proof, target deployment, and
deployment review are separate authorization boundaries. `EXIT_A` does not
authorize implementation, host mutation, readiness, or deployment verification.

The M121A static lock has one successor-compatibility correction: the obsolete
assertions that M122A artifact paths must be absent were removed from the
successor lock, while all substantive M121A document and authority assertions
remain unchanged. The original M121A static-lock SHA-256 is preserved as
`6f670e78a3eec5c4ac386822f120c0a24ac557ba09ae946d9d33614dabd39d5c`; the
successor-compatible lock SHA-256 is
`32fe0862b6ac8dad5b243772630d4d33ffb30258702b7b8ed0df522ea08dd087`.

M122A is a separately authorized repository-only deployment artifact Build. It
adds implementation surfaces for the fixed OAS entrypoint, native notification,
 strict manifest and release verification, offline dependency closure, ordered
 unit generation, capability-bound isolated-root installation, lifecycle and
quiescence evidence, and bounded non-deployment evidence collection. Its trust
correction separates the root-owned fixed verifier and durable verification
evidence from the candidate runtime; the candidate does not supply an anchor
fingerprint or invoke release-signature verification. M122A does
not implement Owner authentication, promote the M121A contract to deployment,
or mutate the live host. Its current status is:

```text
M122A_AUTHORIZED: YES
M122A_STARTED: YES
M122A_FINALIZED: YES
DECISION_STATUS: CURRENT
DESIGN_STATUS: DESIGN_PROVEN
IMPLEMENTATION_STATUS: IMPLEMENTED
VERIFICATION_STATUS: TEST_VERIFIED
DEPLOYMENT_VERIFIED: NO
SELECTED_EXIT: EXIT_A
BUILD_AUTHORIZED: YES
HOST_MUTATION_PERFORMED: NO
PROGRESS_UPDATED: NO
COMMIT_CREATED: NO
TAG_CREATED: NO
PUSH_PERFORMED: NO
SUCCESSOR_AUTHORIZED: NO
SUCCESSOR_NUMBER_ASSIGNED: NO
READY_FOR_PM_REVIEW: NO
PROGRESS_UPDATED: YES
COMMIT_CREATED: YES
TAG_CREATED: YES
PUSH_PERFORMED: YES
```

The M122A evidence reference is:

```text
docs/architecture/MILESTONE_122A_OAS_REPOSITORY_DEPLOYMENT_ARTIFACT_FOUNDATION_BUILD.md
/home/aether/summaries/milestone_122A_end_to_end_trust_transaction_closure_summary.txt
M122A_AUTHORIZED: YES
M122A_FINALIZED: YES
DEPLOYMENT_VERIFIED: NO
IMPLEMENTATION_STATUS: IMPLEMENTED
VERIFICATION_STATUS: TEST_VERIFIED
SELECTED_EXIT: EXIT_A
```
