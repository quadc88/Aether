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
It does not broaden M118A or authorize its start. It introduces no Generic Act
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

The current repository has no authenticated Owner source, production OAS,
WebAuthn, live TLS Owner channel, deployed OS-principal boundary, live recovery
ceremony, AuthenticatedSourceEvent issuance, or Core receipt integration.

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

This is a design contract. No production OAS durable security store or audit
transaction has been implemented.

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
| OS-attested local-console bootstrap | CURRENT | DESIGN_PROVEN | NOT_IMPLEMENTED | NOT_VERIFIED | M117A design record; no live OS evidence |
| OS-attested recovery plus offline material | CURRENT | DESIGN_PROVEN | NOT_IMPLEMENTED | NOT_VERIFIED | M117A design record; no live ceremony |
| separate-principal OAS boundary | CURRENT | DESIGN_PROVEN | NOT_IMPLEMENTED | NOT_VERIFIED | M117A design record; no production OAS |
| direct TLS and exact origin/RP ID | CURRENT | DESIGN_PROVEN | NOT_IMPLEMENTED | NOT_VERIFIED | M117A design record; current API is loopback |
| WebAuthn registration/authentication separation | CURRENT | DESIGN_PROVEN | NOT_IMPLEMENTED | NOT_VERIFIED | M117A design record; no WebAuthn |
| server-side revocable Owner sessions | CURRENT | DESIGN_PROVEN | NOT_IMPLEMENTED | NOT_VERIFIED | M117A design record; no live session issuer |
| CSRF/origin and proxy-boundary controls | CURRENT | DESIGN_PROVEN | NOT_IMPLEMENTED | NOT_VERIFIED | M117A design record; no live Owner channel |
| canonical security state plus audit atomicity | CURRENT | DESIGN_PROVEN | NOT_IMPLEMENTED | NOT_VERIFIED | M117A design record; no OAS store |
| OAS AuthenticatedSourceEvent issuance | CURRENT | DESIGN_PROVEN | NOT_IMPLEMENTED | NOT_VERIFIED | M117A design record; no issuer |
| Core receipt and Goal operation transactions | CURRENT | DESIGN_PROVEN | NOT_IMPLEMENTED | NOT_VERIFIED | M117A design record; no integration |
| recovery separate from ordinary sessions | CURRENT | DESIGN_PROVEN | NOT_IMPLEMENTED | NOT_VERIFIED | M117A design record; no recovery service |
| backup/restore/clone trust separation | CURRENT | DESIGN_PROVEN | NOT_IMPLEMENTED | NOT_VERIFIED | M117A design record; no deployment |
| absolute global split-brain prevention | CURRENT | PARTIAL | NOT_IMPLEMENTED | NOT_VERIFIED | Not proven without external or hardware coordination |
| identity-seed integrity guard | CURRENT | PARTIAL | IMPLEMENTED | TEST_VERIFIED | `aether/identity/guard.py`; `tests/test_identity_guard.py`; bounded file-integrity primitive only |
| bounded governance, policy, approval, restricted-read, and action controls | CURRENT | PARTIAL | IMPLEMENTED | TEST_VERIFIED | `aether/core/governance.py`, `aether/action/policy_gate.py`; `tests/test_core_loop.py`, `tests/test_policy_gate.py`, `tests/test_chat_api.py`; not Owner authentication or generalized Tool authority |
| current `/chat` policy and default-deny execution surface | CURRENT | PARTIAL | IMPLEMENTED | TEST_VERIFIED | `aether/core/governance.py`, `aether/action/policy_gate.py`; pending review and default-deny behavior only |
| generalized Tool-Operation-Capability security architecture | CURRENT | UNDEFINED | NOT_IMPLEMENTED | NOT_VERIFIED | Separate future Tool Security frontier; bounded controls above do not establish it |

## 15. Current Implemented Security Surface

Direct repository inspection identifies only lower-level safeguards:

- `config/aether.yaml` configures the API on loopback `127.0.0.1:8000`.
- The identity guard stores and checks an identity-seed SHA-256 integrity state.
- Core Governance and the policy gate evaluate authorization envelopes for the
  current process-local action surface.
- The current chat loop keeps tool execution disabled and returns pending review
  structures rather than performing automatic tool execution.
- Existing tests cover these bounded primitives and current API behavior.

The current implementation truth is also explicit: no production OAS; no live
authenticated Owner source; no WebAuthn; no live TLS Owner channel; no deployed
OS-principal boundary; no live recovery ceremony; no AuthenticatedSourceEvent
issuance; no Core receipt integration; HA1 remains incomplete; GI2 remains
incomplete; no Generic Act authority; no generalized Tool-Operation-Capability
security architecture; no unrestricted Action authority; existing bounded
governance, policy, approval, restricted-read, and action-control mechanisms
remain current implementation facts; no public Internet; no multi-instance
runtime; and no multi-agent runtime expansion. Owner authentication does not grant
authority to tools, operations, capabilities, or Generic Act.
No M118A artifact is created by this gate.

These primitives do not establish a truthful human source, OAS, WebAuthn, TLS
Owner channel, OS-principal boundary, recovery root, source-event issuer, Core
receipt, or deployment-verifiable security architecture.

## 16. Future and Unproven Security Frontiers

The following remain future or unproven: live Owner trust-root enrollment; OAS
implementation; WebAuthn; TLS/DNS/certificate/LAN listener deployment; OS
attestation; Claim Token human delivery; recovery ceremonies; live sessions; real
signing keys; AuthenticatedSourceEvent issuance; Core receipt and Goal Intake
integration; deployment verification; global split-brain coordination; and any
security expansion beyond the one-mind Owner boundary.

M118A is the next separately authorized bounded foundation Build, but this gate
does not start it.

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

The next authorized boundary is:

```text
M118A - Owner Authority Service Durable Security Kernel Foundation Build
M118A_AUTHORIZED: YES_NOT_STARTED
M118A_STARTED: NO
```

M118A in scope:

- OAS domain/service boundary;
- canonical durable OAS security-state foundation;
- `aether_instance_id` and trust-generation binding;
- Owner lifecycle-state foundation;
- security transaction identity;
- replay/conflict/idempotency primitives;
- atomic canonical state plus `OwnerSecurityAuditEvent` commit;
- crash, rollback, retry, concurrency, and fault-injection proof;
- code boundary preventing ordinary-runtime direct mutation;
- required schema/migration foundation.

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

This canonization gate does not start M118A. The three future constitutional
principles identified for governance review are not accepted constitutional text
and belong only in the external Phase 1 summary.
