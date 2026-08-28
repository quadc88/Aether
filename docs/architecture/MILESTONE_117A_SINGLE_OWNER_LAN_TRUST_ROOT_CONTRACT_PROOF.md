# Milestone 117A Single-Owner LAN Trust-Root Contract Proof

Classification: STRICT READ-ONLY DISCOVERY / SINGLE-OWNER LAN TRUST-ROOT CONTRACT PROOF / DESIGN-RECORD-ONLY

Status: DESIGN / DISCOVERY ONLY / FINAL TARGETED CORRECTIVE PROOF PASS / PM REVIEW PENDING / NO PRODUCTION BUILD

M117A remains exclusively the `OWNER <-> AETHER INSTANCE` boundary. One Aether Instance has exactly one true Owner. This
second corrective pass closes the remaining transaction-ownership contradictions
identified during PM review without
implementing an Owner Authority Service, changing the current runtime, or
authorizing Build. Aether remains one persistent mind and one Aether Instance
has exactly one true Owner.
The invariant is also stated as: one Aether Instance has exactly one true Owner.

The selected product direction is one host, one instance, one Owner, private LAN
access, and no public Internet exposure. The design separates truthful local
bootstrap/recovery presence from the later authenticated LAN channel. It also
separates source authentication from intent interpretation, Goal authority from
Action authority, and execution from verified completion.

The binding equations are:

```text
SOURCE_AUTHENTICATION != INTENT_INTERPRETATION
IDENTITY_AUTHENTICATION != GOAL_AUTHORITY
GOAL_ACCEPTANCE != ACTION_AUTHORIZATION
ACTION_AUTHORIZATION != EXECUTION_SUCCESS
EXECUTION_SUCCESS != GOAL_COMPLETION
COMPLETION_REQUIRES_OBSERVATION_AND_VERIFICATION
AUTHENTICATED_OWNER != UNIVERSALLY_AUTHORIZED_CALLER
TYPED_INTERNAL_CALLER_CONTRACT != HUMAN_AUTHORITY
TRANSPORT != COGNITIVE_AUTHORITY
MEMORY != GOAL_AUTHORITY
RUNTIME_PROCESS_LIFETIME != COGNITIVE_AUTHORITY
GOAL/TASK/TASKCONTEXT_OWNERSHIP != ACTION_PERMISSION
```

## 1. Baseline and Scope

The pre-correction baseline was verified before the interrupted edit:

```text
branch: main
HEAD: 659a045e24f115ff3cb021f4702c2e59a1d75a88
main: 659a045e24f115ff3cb021f4702c2e59a1d75a88
origin/main: 659a045e24f115ff3cb021f4702c2e59a1d75a88
remote refs/heads/main: 659a045e24f115ff3cb021f4702c2e59a1d75a88
predecessor tag: milestone-116A-truthful-human-authority-trust-root-decision
predecessor tag peeled target: 659a045e24f115ff3cb021f4702c2e59a1d75a88
tracked changes: none
untracked files before correction: exactly the two M117A files
pre-correction design SHA-256: 7ad4a39a10160c3eaf746e4969de7326e5a9ec547a4af31058de09942489beee
pre-correction static-lock SHA-256: d64bef8259a189ae4b089bac4669aa0afafd5afee5c2f315001e726d2b0785ab
```

The only repository write paths are this design record and its static
documentation lock. No production code, existing test, dependency, API, route,
configuration, persistence, private runtime data, `PROGRESS.md`, or Git
reference is in scope. The second corrective summary is external:

```text
/home/aether/summaries/milestone_117A_second_corrective_single_owner_lan_trust_root_contract_proof_summary.txt
```

## 2. Milestone Lineage

M116A finalized the truthful negative/current-state trust-root decision.

M117A begins a new Project-Owner-requirements-derived single-owner LAN trust-root contract frontier.

M116A was not a partial production implementation milestone.

No M116B continuation was required.

M117A remains design/discovery/security-contract proof only.

The M116A predecessor is frozen. Its negative result is retained: the current
repository has no authenticated Owner source. M117A does not reinterpret that
negative result as a live implementation.

## 3. Frozen Product Direction

The target is private-LAN access to one Aether Instance. LAN location, a host
name, an OS account, a session, an IP address, or a process convention is not
itself Owner authority. Public listeners, public Internet exposure, plain HTTP
authority operations, SSH tunnels, and unknown proxies are outside the target.

The current repository facts remain explicit: `config/aether.yaml` binds the
current API to `127.0.0.1:8000`; no authentication middleware, WebAuthn
validator, trust-root service, session issuer, recovery service, revocation
store, TLS deployment, or authenticated source-event consumer exists. The
current `session_id`, identity-seed guard, Working Memory, AetherRuntime,
Python caller, and Action approval records are not Owner Authority.
No production authentication is implemented or claimed by this design-only pass.

## 4. Candidate Decisions

### Bootstrap presence candidates

`BOOTSTRAP_PRESENCE_A_COMMAND_RUNS_ON_HOST` proves only process placement.
`BOOTSTRAP_PRESENCE_B_PRIVILEGED_TTY_WITH_CALLER_ASSERTED_LOCALITY` trusts an
unverifiable caller assertion and is rejected. The bounded target is
`BOOTSTRAP_PRESENCE_C_OS_ATTESTED_LOCAL_CONSOLE_PRIVILEGED_IPC`. The negative
candidate `BOOTSTRAP_PRESENCE_D_NO_TRUTHFUL_LOCAL_BOOTSTRAP_PROVEN` describes
the current repository only, not the complete target design.

### Recovery presence candidates

`RECOVERY_PRESENCE_A_AUTHENTICATED_BROWSER_SESSION` is rejected because an
ordinary session cannot recover its own root. `RECOVERY_PRESENCE_B_COMMAND_RUNS_ON_HOST`
proves only process placement. The bounded target is
`RECOVERY_PRESENCE_C_OS_ATTESTED_LOCAL_CONSOLE_PLUS_OFFLINE_MATERIAL`. The
negative candidate `RECOVERY_PRESENCE_D_NO_TRUTHFUL_LOCAL_RECOVERY_PROVEN`
describes the current repository only.

### Authority boundary candidates

The required comparison is:

| Candidate | Security fact | Decision |
| --- | --- | --- |
| `AUTHORITY_BOUNDARY_A_SAME_PROCESS_MODULE` | Runtime memory separation is not a trust boundary | REJECTED |
| `AUTHORITY_BOUNDARY_B_SEPARATE_PROCESS_SAME_OS_PRINCIPAL` | Same unrestricted principal permits confused-deputy and direct-access bypass | REJECTED |
| `AUTHORITY_BOUNDARY_C_SEPARATE_OS_PRINCIPAL_RESTRICTED_IPC_PROTECTED_AUTHORITY_MATERIAL` | Separate service principal, protected material, and kernel-checked IPC | SELECTED |

The earlier summary-only label is retired. It is not a taxonomy replacement and
is not used as the selected authority model.

### Authentication termination candidates

`AUTH_TERMINATION_A_ORDINARY_AETHER_RUNTIME` is rejected because it exposes
reusable Owner material to ordinary runtime. The bounded target is
`AUTH_TERMINATION_B_OWNER_AUTHORITY_SERVICE`. The negative candidate
`AUTH_TERMINATION_C_NO_COMPLETE_TERMINATION_CONTRACT_PROVEN` describes current
runtime evidence only.

### TLS termination candidates

| Candidate | Security fact | Decision |
| --- | --- | --- |
| `TLS_MODEL_A_DIRECT_TLS_TERMINATION_AT_OWNER_AUTHORITY_SERVICE` | OAS owns certificate/origin validation and is the only LAN authority listener | SELECTED |
| `TLS_MODEL_B_PROTECTED_TRUSTED_PROXY_TO_RESTRICTED_AUTH_BACKEND` | Possible only with a separately authenticated proxy channel and inaccessible backend | DEFERRED_OUT_OF_BOUNDED_CONTRACT |
| `TLS_MODEL_C_NO_COMPLETE_TLS_TRUST_BOUNDARY_PROVEN` | Current repository state | EXPLICITLY_NOT_PROVEN |

### Credential candidates

| Candidate | Security fact | Decision |
| --- | --- | --- |
| `CREDENTIAL_MODEL_A_SYNCED_WEBAUTHN_PASSKEY_ALLOWED` | Does not define hardware identity or device-only revocation | Superseded by explicit mixed profile |
| `CREDENTIAL_MODEL_B_DEVICE_BOUND_WEBAUTHN_CREDENTIAL_REQUIRED` | Restricts portability and is not required for one logical Owner credential | Not selected |
| `CREDENTIAL_MODEL_C_HARDWARE_SECURITY_KEY_REQUIRED` | Excludes platform credentials unnecessarily | Not selected |
| `CREDENTIAL_MODEL_D_EXPLICIT_MIXED_WEBAUTHN_PROFILE` | Makes logical-credential and device semantics explicit | SELECTED |
| `CREDENTIAL_MODEL_E_NO_COMPLETE_CREDENTIAL_PROFILE_PROVEN` | Current repository state | EXPLICITLY_NOT_PROVEN |

## 5. Local Privileged Bootstrap Presence

`LOCAL_PRIVILEGED_BOOTSTRAP_PRESENCE` is the following complete target
contract. It is design proof, not live OS evidence.

The Owner Authority Service (OAS) accepts bootstrap authorization only from a
root-owned, dedicated local-presence helper over a restricted Unix socket. The
helper must be invoked from an active OS-recognized local console or local seat.
The OS session source must classify the session as non-remote and associate it
with the active seat. The helper supplies its socket peer credentials; Linux
kernel-supplied PID, UID, GID, and process-start identity are checked through
the IPC credential mechanism and protected process metadata.

The exact permitted helper principal is the dedicated `aether-local-presence`
OS principal. OAS validates the peer PID/UID/GID, process start identity, root
ownership and non-writable permissions of the helper executable, and the
helper’s OS-owned session/seat result. The host kernel and host root are
explicitly in the bounded trusted computing base for this local-presence
attestation. The Owner is the human performing the ceremony at that attested
seat; the OS principal is an enforcement fact, not the human identity.

The OS-owned seat source must report an active local seat, a non-remote session,
the session leader, and the allowed local session class. An absent, unavailable,
ambiguous, stale, or conflicting seat result rejects bootstrap before any state
change. Environment variables, caller flags, terminal text, IP addresses, and
metadata can be negative warning evidence only; they cannot establish locality.

The helper rejects SSH sessions, SSH port forwarding, SSH tunnels, remote pseudo-terminals, and any request carrying remote-session indicators. It does
not accept caller-supplied locality flags. A remote pseudo-terminal is not
converted into a local seat. If local-seat evidence is unavailable, the result
is `REJECT_BEFORE_MUTATION`.

Bootstrap Phase 1 creates one immutable instance identity, a new trust
generation, an enrollment Claim Token, and a durable `CLAIM_PENDING`
transaction only within one OAS transaction. Phase 1 creates no Owner
credential, no Owner session, and no `OWNED` state. It fails closed on
duplicate, stale, replayed, conflicting, or crashed transactions.

Bootstrap Phase 2 is completed through the OAS-owned browser listener after
the first device has received the protected Claim Token. Phase 2 is a WebAuthn
registration ceremony, not an authentication assertion. It can begin only for
a valid, unexpired, instance-bound, generation-bound `CLAIM_PENDING`
transaction protected by its Claim Token. OAS issues and owns a registration
challenge bound to that transaction, instance, generation, exact configured
HTTPS Owner origin, RP ID policy, and expiry. The browser performs the
WebAuthn create ceremony and returns client data whose expected ceremony type
is `webauthn.create`.

OAS validates the registration response and client data, requiring the stored
registration challenge to match exactly, the configured origin to match
exactly, the RP ID hash to match the configured instance-hostname policy, a
unique credential ID, a valid public key and supported algorithm, and explicit
user-presence and user-verification policy. The selected policy requires both
user presence and user verification. Attestation is optional and is not used
to claim physical-device identity. The registration challenge, Claim Token,
and registration response are consumed only in the successful Phase 2
transaction. Private credential material remains in the authenticator and
never enters OAS or ordinary Aether runtime.

After successful registration validation, OAS atomically consumes the Claim
Token and registration challenge, creates the first Owner credential and trust
record, transitions `CLAIM_PENDING -> OWNED`, and writes the canonical audit.
Phase 2 cannot create the pending transaction or proceed without the Phase 1
transaction. WebAuthn authentication occurs only later, after a credential is
registered, through a distinct assertion ceremony whose expected type is
`webauthn.get`.

## 6. Local Privileged Recovery Presence

`LOCAL_PRIVILEGED_RECOVERY_PRESENCE` uses the same OS-attested local-console
contract as bootstrap and additionally requires valid offline recovery material.
OAS, not the browser and not ordinary Aether runtime, validates the local
presence evidence. A missing, unavailable, remote, ambiguous, reused, expired,
or rate-limited presence result rejects recovery before mutation.

The root recovery predicate is:

```text
LOCAL_PRIVILEGED_RECOVERY_PRESENCE + VALID_OFFLINE_RECOVERY_MATERIAL
```

An ordinary authenticated browser session cannot enter `RECOVERY_PENDING` or
initiate recovery. A browser may participate in replacement credential
enrollment only after OAS has created a bounded `RECOVERY_PENDING` transaction
from both roots. Browser participation cannot substitute for local presence or
offline material and cannot create the pending transaction.

Recovery failure, abort, expiry, duplicate submission, crash before commit, or
invalid material preserves the previous authoritative `OWNED` state. Successful
recovery returns to `OWNED` only after one atomic security transaction.

## 7. Owner Authority Service Enforcement

The selected boundary is the required candidate C:

```text
AUTHORITY_BOUNDARY_C_SEPARATE_OS_PRINCIPAL_RESTRICTED_IPC_PROTECTED_AUTHORITY_MATERIAL
```

OAS runs under a dedicated OS service account distinct from ordinary Aether
runtime. Its credential database, session database, recovery verifier, Claim
Token verifier, and authority-evidence signing key are protected by file/key
ownership and permissions available only to OAS and the host-root TCB. The
ordinary runtime has the public verification key only.

The OAS IPC endpoint is a root-owned restricted Unix socket or equivalent local
IPC. Kernel peer credentials are checked for every request. The caller matrix is
explicit:

| Caller | Allowed OAS operation | Forbidden |
| --- | --- | --- |
| `aether-local-presence` | bootstrap and recovery presence assertion | sessions, arbitrary signing, Goal operations |
| OAS-owned browser listener | credential assertion, session, Goal source-event request | local root transition without presence |
| ordinary Aether runtime | verify bounded signed evidence | credential/recovery access, signing, session minting |
| API handler | forward bounded request | evidence manufacture, key access, direct state commit |
| model/tool/plugin/Working Memory | none | all OAS operations |

Privileged bootstrap/recovery IPC is separate from ordinary authenticated
request processing. Direct IPC bypass, unknown peer, wrong UID, wrong executable,
wrong operation, malformed content, and unauthorized operation fail closed.
There is no unrestricted “sign arbitrary evidence” function. OAS verifies the
exact request content, operation, origin, session, generation, and Goal binding
before issuing evidence. No API handler, model, tool, plugin, Working Memory
object, or runtime callback can access protected signing material.

## 8. Authentication Termination

The selected termination owner is OAS. The complete termination map is:

| Material | Terminates at | Ordinary runtime receives |
| --- | --- | --- |
| WebAuthn registration challenge | OAS registration-challenge store | no |
| WebAuthn registration response | OAS registration verifier | no raw response after validation |
| WebAuthn authentication challenge | OAS authentication-challenge store | no |
| WebAuthn authentication assertion | OAS authentication verifier | no raw assertion after validation |
| raw bearer session cookie/token | OAS listener/session verifier | no raw reusable handle |
| CSRF token | OAS browser request validator | validation result only |
| recent-auth proof | OAS session/assurance validator | bounded assurance result only |
| Claim Token | OAS enrollment transaction | no plaintext token |
| offline recovery material | OAS local recovery verifier | no |
| authority-signing private key | protected OAS key store | no |
| AuthenticatedSourceEvent | emitted by OAS after all checks | signed bounded evidence only |

OAS may pass a request correlation identifier and a bounded public-verifiable
event to Core Coordination. It must never pass Owner private credential
material, offline recovery material, Claim Token plaintext, raw reusable
authentication secrets, or an unrestricted session-minting capability.

### WebAuthn Challenge Separation

Registration and authentication use separate OAS challenge records and separate
ceremonies. Registration is available only for a valid Claim Token-protected
`CLAIM_PENDING` transaction and uses `webauthn.create`. Authentication is
available only after a credential exists and uses `webauthn.get`. A registration
challenge cannot satisfy an authentication ceremony, and an authentication
challenge cannot register a credential. Each challenge is bound to the exact
instance, generation, origin, RP ID policy, operation, transaction, and expiry;
the corresponding response is rejected if its challenge, origin, ceremony
type, or RP ID hash differs. Neither challenge is reusable after its owning
successful transaction.

## 9. TLS, Origin, and LAN Deployment

The selected TLS contract is direct TLS termination at OAS. OAS owns the
certificate, hostname/origin policy, RP ID policy, and LAN listener. The
certificate covers the Owner-controlled hostname
`aether.<owner-controlled-domain>`; private DNS resolves that name only on the
Owner’s LAN. DNS ownership and certificate issuance/renewal are controlled by
the Owner through DNS-01 or an equivalent private certificate process. The
service is never publicly reachable. If the Owner cannot provide the selected
hostname and trusted certificate, authority operations fail closed rather than
falling back to an IP URL or HTTP.

The LAN listener is OAS only. The ordinary backend is not LAN-reachable and is
reachable only over OAS’s restricted authenticated IPC. There is no trusted
proxy in this bounded model. Incoming `Forwarded`, `X-Forwarded-For`,
`X-Forwarded-Proto`, Host aliases, and client-identity headers are ignored or
rejected, never trusted by default. Direct backend requests are rejected.
Effective-origin validation belongs to OAS and uses the exact configured HTTPS
origin. A proxy variant is a separately reviewed design, not an implicit
deployment assumption.

## 10. LAN WebAuthn Usability

The chosen usability model is an Owner-controlled domain with split-horizon
private DNS and a trusted certificate. It avoids requiring ordinary users to
install or administer a local CA while keeping the service LAN-only. The Owner
controls hostname, DNS, certificate issuance, renewal, and recovery. DNS-01
may use external DNS control without exposing the service listener.

| Concern | Bounded contract |
| --- | --- |
| hostname | `aether.<owner-controlled-domain>` only |
| DNS | Owner-controlled split-horizon/private DNS |
| certificate | Owner-controlled trusted certificate, renewed before expiry |
| RP ID | exact hostname registrable suffix selected with the certificate |
| allowed origins | exactly `https://aether.<owner-controlled-domain>` |
| first device | local bootstrap creates Claim Token; OAS browser enrollment consumes it |
| new device | existing Owner session plus recent authentication, or a new local pending enrollment |
| certificate recovery | local recovery transaction rebinds hostname/certificate; no HTTP fallback |
| desktop/laptop/phone/tablet | modern HTTPS WebAuthn clients or an enrolled hardware key; unsupported clients fail closed |
| ordinary CA administration | not required |
| public Internet exposure | never introduced; private DNS and listener policy remain LAN-only |

The first device must resolve the configured private hostname and validate the
certificate before enrollment. A raw `http://192.168.x.x` origin is never an
accepted authority origin. Certificate renewal failure blocks new authority
operations before expiry rather than weakening origin validation.

## 11. Credential and Passkey Semantics

The selected first-contract profile is an explicit mixed WebAuthn profile. The
profile permits synced passkeys and device-bound/hardware credentials, but it
does not confuse them:

- first credential enrollment is a WebAuthn registration ceremony (`webauthn.create`), not a WebAuthn authentication assertion;
- OAS validates registration client data, exact stored challenge, exact origin, RP ID hash, credential ID uniqueness, public-key algorithm, user presence, and user verification before creating `OwnerCredential`;
- later authentication is a separate WebAuthn assertion ceremony (`webauthn.get`) and is impossible before registration has committed;
- the attestation policy is optional-attestation/no-device-identity-claim; attestation metadata cannot prove a physical device unless a separately proven authenticator property establishes it;
- a synced passkey is one logical WebAuthn credential that may exist on several
  physical devices;
- a device-bound credential or hardware security key is separately enrolled and
  may have stronger device-loss handling;
- WebAuthn backup-eligibility and backup-state signals are recorded as
  authenticator assurance metadata, not as proof of human identity or physical
  possession;
- credential revocation revokes the logical credential record and every session
  bound to it;
- logical credential revocation is not physical-device revocation for a synced
  passkey;
- “lost phone -> revoke only that phone” is not promised for a synced passkey;
  it is available only where a separately enrolled device-bound credential has
  a truthful device-specific revocation property;
- hardware security keys are allowed but not mandatory;
- replacement and last-usable-credential rules are enforced by OAS.

## 12. Owner Session and CSRF Contract

The selected session is a server-side opaque, short-lived,
instance/credential/generation-bound, revocable session. OAS creates a random
handle, stores only a verifier/hash, and sets `Secure`, `HttpOnly`,
`SameSite=Strict` cookies. The record contains issued time, absolute expiry,
idle expiry, recent-auth time, assurance state, credential reference, instance
identity, trust generation, and revocation state. OAS owns revoke-one,
revoke-all, credential-revokes-sessions, and generation invalidation. Backups
exclude active sessions; restore and clone invalidate them.

The selected CSRF/origin contract requires exact OAS-owned origin validation,
restrictive no-ambient CORS, Secure/HttpOnly/SameSite cookies, a per-session
CSRF token, Fetch Metadata checks where available, rejection of cross-site
simple forms, state-changing content-type enforcement, and binding of the
validated request body to the source-event digest. Missing Origin, invalid
Origin, unsafe Fetch Metadata, wrong content type, missing CSRF token, stale
recent-auth, or direct-backend routing rejects before mutation. High-risk
operations require recent authentication again.

```text
AUTHENTICATED_BROWSER_SESSION
+
CROSS_SITE_REQUEST
!=
OWNER_AUTHORIZATION
```

## 13. Owner Lifecycle

Only these four lifecycle states are used:

```text
UNCLAIMED -> CLAIM_PENDING -> OWNED
OWNED -> RECOVERY_PENDING -> OWNED
CLAIM_PENDING -> UNCLAIMED
RECOVERY_PENDING -> OWNED unchanged on failure, abort, or expiry
```

| Transition | Initiator/evidence | Owner and transaction | Failure/retry/duplicate/crash |
| --- | --- | --- | --- |
| `UNCLAIMED -> CLAIM_PENDING` | local presence assertion | OAS Phase 1; durable pending transaction, instance identity, generation, Claim Token, and audit | reject invalid/remote; same request returns same pending result; crash rolls back; no credential or `OWNED` state is created |
| `CLAIM_PENDING -> OWNED` | OAS-created pending transaction + Claim Token + validated WebAuthn registration response | OAS Phase 2; one atomic security transaction consumes the token, registration challenge, and response, creates the credential/trust record, transitions state, and audits | invalid/replay rejects; retry is idempotent; crash preserves pending, an unconsumed token, and no credential |
| `CLAIM_PENDING -> UNCLAIMED` | token expiry/cancel by OAS | OAS transaction and audit | duplicate is no-op; crash leaves pending until expiry |
| `OWNED -> RECOVERY_PENDING` | local recovery presence + offline material | OAS; recovery transaction and audit | ordinary session rejected; duplicate request does not create a second pending state |
| `RECOVERY_PENDING -> OWNED` | validated replacement credential and recovery proof | OAS; generation/revocation/audit transaction | invalid proof preserves Owned generation; success retry returns same result |
| `RECOVERY_PENDING -> OWNED` unchanged | abort, expiry, or failed recovery | OAS records non-mutating audit outcome | no credential or generation change; crash preserves old authority |

## 14. Claim Token

The Claim Token is owned and issued by OAS during Bootstrap Phase 1 inside a
`CLAIM_PENDING` transaction. It contains a cryptographically random value with
at least 128 bits of entropy; OAS stores only a verifier, instance identity,
pending transaction identity, creation/expiry, attempt state, and consumed
state. Plaintext is displayed once through the protected local ceremony and is
never logged, backed up, or returned by ordinary API retrieval.

The token is instance-bound, generation-bound to the pending trust generation,
short-lived, single-use, and rate-limited. Phase 2 consumes it atomically with
the OAS-owned registration challenge and validated registration response,
first credential enrollment, the Owner trust record, `OWNED` transition, and
canonical audit. An invalid, expired, reused, duplicate, or wrong-instance
token cannot alter state. Identical Phase 1 retries return the recorded pending
result. Identical Phase 2 retries after commit return the recorded completion
result; conflicting retries reject. A crash before Phase 1 commit creates no
pending state. A crash after Phase 1 commit leaves the pending transaction and
unconsumed token. A crash before Phase 2 commit preserves that pending state,
unconsumed token, and no credential; a crash after Phase 2 commit exposes the
committed result but cannot repeat the transition. Backups exclude the token
and challenge.

## 15. Recovery Entropy and Contract

The recovery material is generated by an approved CSPRNG and has:

```text
RECOVERY_ENTROPY = CRYPTOGRAPHICALLY_SUFFICIENT_HIGH_ENTROPY_APPROXIMATELY_128_BITS_OR_MORE
```

The material is displayed once under local presence, stored offline by the
Owner, never retrievable through an ordinary API, and never logged or included
in backups. OAS stores a non-reversible verifier where practical, bound to the
`aether_instance_id` and recovery generation. It enforces attempt limitation,
backoff/rate limiting, reuse rejection, and successful consumption or explicit
rotation. The verifier and material are never accepted outside local recovery.

Root recovery requires local presence plus valid offline material. It does not
issue a permanent session. On success OAS atomically activates the replacement
credential, rotates trust generation, revokes old credentials and all sessions,
consumes or rotates material, invalidates challenges and Claim Tokens, commits
the canonical audit, and returns to `OWNED`. Failure preserves the prior
authoritative state.

The selected revocation contract supports revoke-one credential, revoke-one
session, revoke-all sessions, credential-to-session invalidation, generation
invalidation, recovery replacement, recovery-material rotation, and protection
against revoking the last usable credential without a valid replacement. It
does not cancel Goals or create Action authority.

## 16. Canonical Security Audit Atomicity

The canonical OAS durable security store owns state and audit together:

```text
SECURITY_STATE_COMMIT
+
CANONICAL_SECURITY_AUDIT_COMMIT
=
ONE_ATOMIC_SECURITY_TRANSACTION
```

The selected audit model applies to first Owner claim, credential enrollment,
credential revocation, recovery finalization, trust-generation rotation, and
recovery-material rotation. Each operation writes durable state and a
non-secret `OwnerSecurityAuditEvent` in the same transaction. A security state
commit cannot succeed if its canonical audit commit fails. External syslog,
SIEM, analytics, and observability are asynchronous copies outside the
canonical transaction and cannot authorize success. In-memory audit is never sufficient.

| Operation | Transaction owner | Crash before/after commit | Retry/duplicate |
| --- | --- | --- | --- |
| claim pending creation | OAS durable store | rollback / pending result retained | same Phase 1 transaction identity / reject conflict |
| registration challenge issue | OAS durable store | no challenge / challenge retained until expiry | same registration transaction identity / reject conflict |
| first credential registration and claim completion | OAS durable store | pending state / committed `OWNED` result retained | same Phase 2 transaction identity / reject conflict |
| credential revocation | OAS durable store | unchanged / revocation durable | idempotent / no second event |
| recovery finalization | OAS durable store | old Owned state / new generation durable | same result / reject old generation |
| trust-generation rotation | OAS durable store | old generation / new generation durable | idempotent / stale generation rejected |
| recovery-material rotation | OAS durable store | old verifier / new verifier durable | same result / reused material rejected |

## 17. Replay and Atomicity

OAS is the atomic owner for local bootstrap authorization, Claim Token issue,
Claim Token Phase 2 validation and consumption, WebAuthn registration-challenge
issue and consume, WebAuthn authentication-challenge issue and consume, session
issue, recent-auth challenge, credential enrollment/revocation, session
revoke/revoke-all, recovery initiation/finalization, and recovery-material
rotation. OAS issues and signs the bounded source event but does not consume it
for Goal state. Core Coordination is the atomic owner for source-event receipt
and the operation-specific result.

Every one-use item has a durable transaction identity, nonce or challenge,
expiry, consumed marker, and generation. Identical retries are idempotent after
a committed result. Conflicting payload, operation, origin, Goal revision,
instance, generation, credential, or transaction identity rejects. A duplicate
cannot cause a second canonical transition. A crash before commit leaves the
old state; a crash after commit leaves the new state and audit together.

The selected source-event consumption transaction is owned by Core Coordination.
Core verifies the OAS signature, exact instance/generation/origin/operation and
Goal revision, then atomically records the source-event receipt and performs the
canonical Goal transition. If either receipt or Goal transition fails, neither
commits. A committed receipt and Goal transition are retained together;
identical event retries return the recorded result and conflicting or replayed
events reject. OAS cannot commit Goal state, and Core cannot mint or sign a
source event.

## 18. Backup, Restore, Migration, Clone, and Split-Brain

The design decisions are explicit:

```text
BACKUP != RESTORE
BACKUP != CLONE_AUTHORIZATION
RESTORE != MIGRATION
CLONE_OR_FORK != SAME_ACTIVE_AETHER_IDENTITY
AETHER_IDENTITY_CONTINUITY_REQUIRES_EXPLICIT_RESTORE_OR_MIGRATION_SEMANTICS
```

### BACKUP

Backup is a passive protected snapshot. It cannot self-activate. It excludes
host-activation private material, authority-signing private material, active
sessions, Claim Tokens, challenges, and transient replay state. It may contain
explicitly protected public credential records and non-secret audit history,
but copying the snapshot does not copy active authority.

### RESTORE

Restore is controlled local recovery on a destination. It binds the destination
host and `aether_instance_id`, creates a new continuity/trust generation,
invalidates sessions, challenges, Claim Tokens, and stale evidence, and
requires credential replacement or an explicitly authorized continuity proof.
Raw backup data cannot self-activate.

### MIGRATION

Migration requires coordinated source quiescence, Owner authorization,
destination activation, trust/key transition, source deactivation/tombstone, and
an audit transaction. Uncoordinated file copying is not migration. Implementation
is out of scope.

### CLONE/FORK

Clone/fork receives a new `aether_instance_id` and a new Owner trust root. It
may retain explicitly identified memory lineage but cannot retain active Owner
credentials, sessions, recovery material, Claim Tokens, or authority keys.

### GLOBAL SPLIT-BRAIN PREVENTION

Isolated simultaneous restores may both run. Neither isolated copy can
necessarily detect the other without external or hardware coordination. The
design does not claim absolute global single-active-instance prevention. Stale
authority fails only when detectable through generation, hostname, certificate,
or activation evidence. No cloud/global coordinator is introduced.

## 19. Minimum Records and Field Classification

The eight trust-root/security records are design-level OAS-owned records.
`KEEP`, `CONDITIONAL`, `REMOVE`, and `DEFER` are field decisions; no
security-essential field is unresolved. `AuthenticatedSourceEvent` is OAS-issued
and OAS-owned signed evidence. `AuthenticatedSourceEventReceipt` is a separate
Core-owned record. Canonical Goal state is also Core-owned and is not an OAS
security record.

| Record | Minimum fields and classification |
| --- | --- |
| `AetherInstanceTrust` | `aether_instance_id` KEEP; lifecycle state KEEP; trust/continuity generation KEEP; Owner scope KEEP; credential-set reference KEEP; created/rotated times KEEP; active flag KEEP; private key REMOVE; ordinary caller metadata REMOVE |
| `ClaimTokenRecord` | token-record ID KEEP; `aether_instance_id` KEEP; pending generation KEEP; verifier KEEP; created/expiry KEEP; attempts KEEP; consumed state/time KEEP; plaintext token REMOVE; backup export REMOVE |
| `OwnerCredential` | credential ID KEEP; `aether_instance_id` KEEP; public key KEEP; RP ID KEEP; credential type KEEP; backup eligibility/state CONDITIONAL; created/revoked state KEEP; credential generation KEEP; private key REMOVE |
| `OwnerSession` | session ID KEEP; verifier/hash KEEP; `aether_instance_id` KEEP; credential ID KEEP; generation KEEP; issued/absolute/idle expiry KEEP; recent-auth/assurance KEEP; revoked state KEEP; raw handle REMOVE |
| `RecoveryRecord` | recovery ID KEEP; `aether_instance_id` KEEP; source/target generation KEEP; verifier reference KEEP; attempt/expiry/consumed state KEEP; pending transaction KEEP; recovery plaintext REMOVE; backup export REMOVE |
| `AuthChallenge` | challenge ID KEEP; challenge hash KEEP; `aether_instance_id` KEEP; credential/RP/origin KEEP; issued/expiry KEEP; request binding KEEP; consumed state KEEP; raw reusable assertion REMOVE |
| `AuthenticatedSourceEvent` | event ID KEEP; `aether_instance_id` KEEP; credential/session reference KEEP; trusted origin KEEP; raw request digest KEEP; exact operation KEEP; Goal/revision binding CONDITIONAL by operation; issued/expiry KEEP; nonce KEEP; generation KEEP; assurance/recent-auth KEEP; authority signature KEEP; private signing key REMOVE |
| `OwnerSecurityAuditEvent` | audit ID KEEP; transaction ID KEEP; event kind KEEP; `aether_instance_id` KEEP; generation KEEP; affected record/reference KEEP; result KEEP; non-secret evidence digest KEEP; timestamp KEEP; raw credentials/recovery/plaintext REMOVE; external log copy DEFER |
| `AuthenticatedSourceEventReceipt` | `receipt_id` KEEP; `event_id` KEEP; `event_nonce` KEEP; `aether_instance_id` KEEP; `trust_generation` KEEP; authenticated event digest KEEP; raw request digest KEEP; exact operation KEEP; Goal ID CONDITIONAL by operation; expected Goal revision CONDITIONAL by operation; Core transaction identity KEEP; committed result or result digest KEEP; resulting Goal ID/revision CONDITIONAL by mutation; `received_at` KEEP; `committed_at` KEEP; replay/conflict status KEEP; unique `(event_id)` and `(event_nonce)` constraints KEEP; Owner private credential/session/Claim Token/recovery/signing key REMOVE |

OAS-owned trust-root/security records are owned and validated by OAS, persisted
in its durable security store, bound to `aether_instance_id` and applicable
generation, and have explicit replay, revocation, retention, backup, restore,
and audit rules. The OAS-issued `AuthenticatedSourceEvent` is signed bounded
evidence, not canonical Goal state. The Core-owned
`AuthenticatedSourceEventReceipt` is persisted and validated by Core
Coordination, bound to the event instance/generation, and participates in the
Core receipt transaction. Core Coordination owns canonical Goal state and its
operation-specific mutation or read-result semantics. Public keys and digests
are public/verifiable; verifiers and state are protected; private credentials,
recovery plaintext, session handles, Claim Token plaintext, and signing keys
remain inside OAS. The Core receipt contains none of those secrets and cannot
mint or alter an `AuthenticatedSourceEvent`. Goal records contain no security
secret.

The Core-owned receipt contract is:

```text
AuthenticatedSourceEventReceipt
receipt_id
event_id
event_nonce
aether_instance_id
trust_generation
authenticated_event_digest
raw_request_digest
exact_operation
goal_id (when applicable)
expected_goal_revision (when applicable)
core_transaction_id
committed_result_or_result_digest
resulting_goal_id (when applicable)
resulting_goal_revision (when applicable)
received_at
committed_at
replay_conflict_status
UNIQUE(event_id)
UNIQUE(event_nonce)
OWNER: CORE_COORDINATION
```

OAS must not own or mutate this receipt. Core Coordination rejects wrong
instance, stale generation, changed authenticated-event or raw-request digest,
changed operation, changed Goal binding, and conflicting Core transaction
identity before commit. A receipt contains no Owner private credential, session
secret, Claim Token, recovery material, or OAS signing key. Unique event and
nonce constraints prevent a second canonical operation.

## 20. Authenticated Source Event

The source-event contract is signed bounded evidence minted only by OAS after
authentication termination and exact request validation. Its minimum fields are:

```text
event_id
aether_instance_id
credential_reference
session_reference
trusted_origin
raw_request_digest
exact_operation
issued_at
expires_at
nonce
trust_generation
assurance_state
recent_auth_at
authority_signature
```

OAS alone may mint and sign the event. Ordinary runtime has verification
material only. Wrong instance, stale generation, expired event, reused
nonce/event ID, changed raw request, changed operation, wrong origin, changed
Goal/revision, invalid signature, or insufficient recent authentication rejects
before Core receipt commit. Core Coordination verifies and records the event in
the Core-owned receipt and owns the operation-specific result; it does not
interpret source intent, mint or sign Owner evidence, or grant Action authority.
Event issuance by OAS is not event consumption: only Core Coordination consumes
the event through the receipt transaction described below.

### Core-Owned Source-Event Receipt and Goal Operation Semantics

The selected source-event consumption model distinguishes mutating and
read-only Goal operations. `AuthenticatedSourceEventReceipt` is the durable
Core-owned replay and result record for both classes. OAS-issued event evidence
and the Core-owned receipt remain separate records, and neither operation class
changes that ownership boundary.

The mutating Goal operations are exactly:

```text
PROPOSE_GOAL
ACCEPT_GOAL
```

For either mutating operation, Core validates the exact operation, request and
event digests, instance, generation, Goal binding, and expected revision. It
then commits the receipt and the bound canonical Goal mutation together:

```text
CORE_SOURCE_EVENT_RECEIPT_COMMIT
+
BOUND_CANONICAL_GOAL_MUTATION_COMMIT
=
ONE_ATOMIC_CORE_COORDINATION_TRANSACTION
```

If either component fails, neither commits. An identical committed retry
returns the recorded result without a second mutation. A conflicting retry,
changed digest, changed operation, changed Goal binding, stale generation, or
replayed event rejects.

The read-only Goal operation is exactly:

```text
GET_GOAL_STATUS
```

`GET_GOAL_STATUS` validates the exact event/request/instance/generation binding,
binds the receipt to the Goal ID and observed Goal revision, and commits the
receipt with a bounded status result snapshot or result digest:

```text
CORE_SOURCE_EVENT_RECEIPT_COMMIT
+
BOUND_GOAL_STATUS_RESULT_SNAPSHOT_OR_DIGEST_COMMIT
=
ONE_ATOMIC_CORE_COORDINATION_READ_RECEIPT_TRANSACTION
```

This read receipt performs no Goal transition and grants no Goal mutation or
Action authority. An identical committed retry returns the recorded result or
the explicitly recorded equivalent snapshot/digest. Conflicting or replayed
content rejects. Failure before commit records neither the receipt nor the
status result. The event remains exact-operation/request/instance/generation
bound for this read-only path.

The formal decision block records that source authentication does not equal
intent interpretation, Goal acceptance does not authorize Action, Action
success does not prove completion, and completion requires Observation and
Verification.

## 21. Exact Goal and One-Mind Boundary

The only Owner Goal operations are `PROPOSE_GOAL`, `ACCEPT_GOAL`, and
`GET_GOAL_STATUS`. Propose and Accept are the mutating operations, and Status is
read-only. Propose does not accept. Accept requires exact existing Goal ID,
expected revision, canonical operation payload/digest, valid source event, and
Core Coordination’s atomic compare-and-accept. A stale, duplicate, changed,
or ambiguous request fails closed. Natural-language text, model confidence,
ThinkingProposal, session metadata, or a request to complete cannot silently
become acceptance. `GET_GOAL_STATUS` cannot create, revise, accept, or otherwise
transition a Goal.

Goal acceptance does not authorize Action. Action success does not prove
completion. Observation and Verification remain necessary. Aether cannot appoint
or replace its Owner. No multi-instance runtime, generic identity registry,
second mind, public exposure, or production authentication is introduced.

## 22. Complete Hard-Gate Matrix

The following is the corrected design-proof matrix. Every material requirement
has an explicit design owner, security fact, validator, failure result, section,
static-lock coverage, current-runtime status, and future runtime-test obligation.
Every final design verdict in this matrix is approved; the
selected exit requires every row below to be `PROVEN_BY_DESIGN`.

The matrix includes the canonical security mutation plus audit commit atomic
requirement as a distinct hard gate.

| Requirement | Design/security fact | Owner/validator | Failure result | Section | Static lock | Current runtime | Later test | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| truthful local privileged bootstrap presence | OS seat, non-remote session, kernel peer credentials, exact helper principal, host root/kernel TCB | OAS validates helper and OS source | reject before mutation | 5 | required-presence assertions | not implemented | adversarial OS/IPC tests | PROVEN_BY_DESIGN |
| truthful local privileged recovery presence | Same attestation plus offline material | OAS | preserve Owned | 6 | recovery/presence assertions | not implemented | recovery-origin tests | PROVEN_BY_DESIGN |
| protected authentication boundary | OAS terminates all reusable authentication | OAS | reject untrusted input | 7-8 | boundary/termination markers | not implemented | process/IPC isolation tests | PROVEN_BY_DESIGN |
| runtime cannot manufacture Owner evidence | key and signing operation inaccessible; verification only | OAS and kernel permissions | reject unsigned/untrusted event | 7-8 | runtime prohibition assertions | not implemented | key-access and forgery tests | PROVEN_BY_DESIGN |
| explicit TLS/proxy trust boundary | direct OAS TLS; proxy deferred and not trusted | OAS | reject unknown origin/proxy | 9 | TLS comparison markers | not implemented | TLS/proxy tests | PROVEN_BY_DESIGN |
| proxy headers not implicit | forwarding headers ignored/rejected | OAS | reject or ignore header | 9 | header markers | not implemented | spoofing tests | PROVEN_BY_DESIGN |
| direct backend bypass fails closed | backend OAS IPC-only and LAN-inaccessible | OAS/kernel | reject direct backend | 9 | bypass marker | not implemented | socket exposure tests | PROVEN_BY_DESIGN |
| ordinary session cannot recover | recovery needs local presence plus offline material | OAS | preserve Owned | 6, 12, 15 | explicit session prohibition | not implemented | browser recovery tests | PROVEN_BY_DESIGN |
| credential semantics explicit | registration (`webauthn.create`) is distinct from later authentication (`webauthn.get`); mixed profile distinguishes logical synced and device-bound credentials | OAS | reject wrong ceremony/challenge or apply logical revocation | 5, 8, 11 | credential/challenge markers | not implemented | WebAuthn ceremony and backup-state tests | PROVEN_BY_DESIGN |
| security mutation plus audit atomic | same OAS durable transaction | OAS store | rollback all | 16 | equation/operation table | not implemented | crash/transaction tests | PROVEN_BY_DESIGN |
| backup/restore split-brain limit | passive backup, explicit restore, new clone identity, no absolute global claim | OAS/destination activation | stale/ambiguous authority rejects | 18 | lifecycle markers | not implemented | restore/clone tests | PROVEN_BY_DESIGN |
| LAN WebAuthn usability | private DNS, Owner domain, trusted cert, exact RP ID/origin | OAS/Owner deployment | no HTTP/IP fallback | 9-10 | usability markers | not implemented | device/browser matrix | PROVEN_BY_DESIGN |
| CSRF/origin abuse | exact origin, CSRF, SameSite, Fetch Metadata, body binding | OAS | reject before mutation | 12 | CSRF equation/markers | not implemented | cross-site tests | PROVEN_BY_DESIGN |
| recovery entropy | CSPRNG, approximately 128 bits or more, verifier, no retrieval | OAS | reject invalid/reused material | 14-15 | entropy markers | not implemented | entropy/lifecycle tests | PROVEN_BY_DESIGN |
| bootstrap/auth/session/recovery/revocation atomicity | two-phase Claim lifecycle plus explicit authentication/recovery/revocation transactions and crash semantics | OAS durable store | old state, pending state, or committed state only | 5, 13-17 | lifecycle/atomicity tables | not implemented | fault-injection tests | PROVEN_BY_DESIGN |
| minimal data contract | eight OAS-owned trust-root/security records, one OAS-issued event record, one Core-owned receipt record, and Core-owned canonical Goal state with every field classified | OAS and Core Coordination by record | reject unknown/missing essential field or ownership mismatch | 19 | record names/classifications | not implemented | schema/property tests | PROVEN_BY_DESIGN |
| authenticated source event | OAS signs exact fields; Core owns the durable receipt and operation-specific result | OAS issuance; Core Coordination receipt/result transaction | reject before receipt commit or roll back receipt with failed operation | 17, 19-21 | event/receipt markers | not implemented | forgery/replay/atomicity tests | PROVEN_BY_DESIGN |
| mutating and read-only Goal operation semantics | PROPOSE_GOAL and ACCEPT_GOAL atomically commit receipt plus mutation; GET_GOAL_STATUS atomically commits receipt plus bound status result without Goal transition | Core Coordination | reject conflicting/replayed content; commit neither receipt nor result on failure | 20-21 | operation/atomicity markers | not implemented | mutation/read-receipt tests | PROVEN_BY_DESIGN |
| one-instance/one-Owner boundary | instance identity and one Owner lifecycle | OAS | wrong instance/generation rejects | 1-3, 18-19 | one-Owner markers | not implemented | identity/clone tests | PROVEN_BY_DESIGN |
| no production implementation | design-only write scope | static lock/Git | no runtime claim | 1, 23 | explicit no-implementation lock | current | scope audit | PROVEN_BY_DESIGN |
| no Generic Act or generic identity registry | downstream boundaries unchanged | static lock/design | no authorization expansion | 21, 23 | explicit prohibition lock | current | scope audit | PROVEN_BY_DESIGN |

## 23. Authorized Exit and Build Boundary

The design is complete at the design-only level. `EXIT_A` is a PM-review
recommendation, not Build authorization. No production implementation or live
trust-root proof is claimed. The Build gate is represented as “justified for PM
review” only because all design hard gates and minimality are explicit; PM must
separately authorize any implementation.

No successor milestone number is assigned. The next action is neutral PM/Owner
review of whether a future implementation Build should be authorized.

## 24. Core-Drift Review

The corrected design confirms:

- Aether remains one persistent mind;
- one Aether Instance has exactly one Owner;
- OAS is non-cognitive;
- Core Coordination remains canonical Goal owner;
- source authentication remains separate from intent interpretation;
- authenticated source cannot silently become an interpreted Goal;
- model confidence cannot become Human Authority;
- Aether cannot appoint or replace Owner;
- Goal acceptance does not authorize Action;
- Action success does not prove completion;
- completion requires Observation and Verification;
- LAN location does not become authentication;
- proxy metadata does not become authority;
- session state does not become universal authority;
- no generic identity registry exists;
- no multi-instance runtime exists;
- no public Internet exposure is introduced;
- no Generic Act is authorized;
- no production implementation occurred.

## 25. Authoritative Formal Decision Block

There is exactly one authoritative formal decision block in this record.

```text
AUTHORITATIVE_FORMAL_DECISION_BLOCK_BEGIN
SELECTED_DEPLOYMENT_PROFILE:
DEPLOYMENT_PROFILE_B_SINGLE_OWNER_LOCAL_NETWORK
SELECTED_TARGET_TRUST_ROOT_MODEL:
TRUST_ROOT_MODEL_J_HYBRID_BOOTSTRAP_AND_AUTHENTICATED_CHANNEL
CURRENT_TRUST_ROOT_STATE:
NO_AUTHENTICATED_OWNER_SOURCE_EXISTS
ENTRY_TRUST_ROOT_MATURITY:
TR1_TRUST_ROOT_REQUIREMENTS_IDENTIFIED
TARGET_TRUST_ROOT_MATURITY:
TR2_BOUNDED_TRUST_ROOT_CONTRACT_PROVEN_DESIGN_ONLY
RESULT_TRUST_ROOT_MATURITY:
TR2_BOUNDED_TRUST_ROOT_CONTRACT_PROVEN_DESIGN_ONLY
TR2_PROVEN:
YES
SELECTED_BOOTSTRAP_PRESENCE_MODEL:
BOOTSTRAP_PRESENCE_C_OS_ATTESTED_LOCAL_CONSOLE_PRIVILEGED_IPC
SELECTED_RECOVERY_PRESENCE_MODEL:
RECOVERY_PRESENCE_C_OS_ATTESTED_LOCAL_CONSOLE_PLUS_OFFLINE_MATERIAL
SSH_BOOTSTRAP_ALLOWED:
NO
SSH_RECOVERY_ALLOWED:
NO
SELECTED_AUTHORITY_BOUNDARY_MODEL:
AUTHORITY_BOUNDARY_C_SEPARATE_OS_PRINCIPAL_RESTRICTED_IPC_PROTECTED_AUTHORITY_MATERIAL
SELECTED_AUTHENTICATION_TERMINATION_MODEL:
AUTH_TERMINATION_B_OWNER_AUTHORITY_SERVICE
AETHER_RUNTIME_CAN_MINT_OWNER_EVIDENCE:
NO
SELECTED_TLS_TERMINATION_MODEL:
TLS_MODEL_A_DIRECT_TLS_TERMINATION_AT_OWNER_AUTHORITY_SERVICE
PROXY_HEADERS_TRUSTED_BY_DEFAULT:
NO
DIRECT_BACKEND_BYPASS_ALLOWED:
NO
SELECTED_CREDENTIAL_MODEL:
CREDENTIAL_MODEL_D_EXPLICIT_MIXED_WEBAUTHN_PROFILE
SELECTED_WEBAUTHN_ENROLLMENT_MODEL:
WEBAUTHN_REGISTRATION_CEREMONY_OAS_CHALLENGE_BOUND_CLAIM_PENDING
WEBAUTHN_REGISTRATION_CEREMONY_TYPE:
webauthn.create
WEBAUTHN_AUTHENTICATION_CEREMONY_TYPE:
webauthn.get
WEBAUTHN_USER_PRESENCE_REQUIRED:
YES
WEBAUTHN_USER_VERIFICATION_REQUIRED:
YES
WEBAUTHN_ATTESTATION_POLICY:
OPTIONAL_NO_PHYSICAL_DEVICE_IDENTITY_CLAIM
SYNCED_PASSKEY_POLICY:
SYNCED_PASSKEYS_ALLOWED_LOGICAL_CREDENTIAL_REVOCATION_NOT_PHYSICAL_DEVICE_REVOCATION
CREDENTIAL_REVOCATION_EQUALS_PHYSICAL_DEVICE_REVOCATION:
NO
SELECTED_SESSION_MODEL:
SESSION_MODEL_A_SERVER_SIDE_OPAQUE_SHORT_LIVED_GENERATION_BOUND_REVOCABLE
SELECTED_CSRF_ORIGIN_MODEL:
CSRF_ORIGIN_MODEL_A_EXACT_ORIGIN_TOKEN_SAMESITE_FETCH_METADATA_AND_BODY_BINDING
ORDINARY_SESSION_CAN_ENTER_RECOVERY:
NO
RECOVERY_ENTROPY:
CRYPTOGRAPHICALLY_SUFFICIENT_HIGH_ENTROPY_APPROXIMATELY_128_BITS_OR_MORE
SELECTED_RECOVERY_MODEL:
RECOVERY_MODEL_C_LOCAL_OS_ATTESTED_PRESENCE_PLUS_OFFLINE_MATERIAL_GENERATION_ROTATION
SELECTED_REVOCATION_MODEL:
REVOCATION_MODEL_A_CREDENTIAL_SESSION_AND_GENERATION_REVOCATION
SELECTED_AUDIT_ATOMICITY_MODEL:
AUDIT_ATOMICITY_MODEL_A_SINGLE_DURABLE_SECURITY_TRANSACTION
CANONICAL_SECURITY_MUTATION_WITHOUT_AUDIT_CAN_SUCCEED:
NO
SELECTED_BACKUP_MODEL:
BACKUP_MODEL_A_PASSIVE_PROTECTED_NO_ACTIVE_AUTHORITY
SELECTED_RESTORE_MODEL:
RESTORE_MODEL_A_CONTROLLED_LOCAL_GENERATION_ROTATING_RESTORE
SELECTED_MIGRATION_MODEL:
MIGRATION_MODEL_A_COORDINATED_SOURCE_QUIESCE_DESTINATION_ACTIVATION
SELECTED_CLONE_MODEL:
CLONE_MODEL_A_NEW_AETHER_INSTANCE_ID_AND_NEW_OWNER_TRUST_ROOT
GLOBAL_SPLIT_BRAIN_PREVENTION:
NOT_PROVEN_WITHOUT_EXTERNAL_OR_HARDWARE_COORDINATION
AETHER_INSTANCE_BINDING:
ALL_OWNER_TRUST_RECORDS_BOUND_TO_AETHER_INSTANCE_ID
SELECTED_SOURCE_EVENT_MODEL:
SOURCE_EVENT_MODEL_A_SIGNED_EXACT_REQUEST_BOUND_OWNER_EVENT
SELECTED_CLAIM_ENROLLMENT_TRANSACTION_MODEL:
CLAIM_ENROLLMENT_MODEL_A_TWO_PHASE_PENDING_THEN_ATOMIC_COMPLETION
SELECTED_SOURCE_EVENT_CONSUMPTION_MODEL:
SOURCE_EVENT_CONSUMPTION_MODEL_B_CORE_ATOMIC_RECEIPT_AND_BOUND_OPERATION_RESULT
CROSS_BOUNDARY_ATOMIC_GOAL_RECEIPT:
REQUIRED_IN_CORE_COORDINATION_OPERATION_RESULT_TRANSACTION
AUTHENTICATED_SOURCE_EVENT_OWNER:
OAS_ISSUED_SIGNED_EVIDENCE
AUTHENTICATED_SOURCE_EVENT_RECEIPT_OWNER:
CORE_COORDINATION
CORE_CANONICAL_GOAL_STATE_OWNER:
CORE_COORDINATION
MUTATING_GOAL_OPERATIONS:
PROPOSE_GOAL | ACCEPT_GOAL
READ_ONLY_GOAL_OPERATION:
GET_GOAL_STATUS
SOURCE_AUTHENTICATION_EQUALS_INTENT_INTERPRETATION:
NO
GOAL_ACCEPTANCE_AUTHORIZES_ACTION:
NO
ACTION_SUCCESS_PROVES_COMPLETION:
NO
COMPLETION_REQUIRES_OBSERVATION_AND_VERIFICATION:
YES
HUMAN_AUTHORITY_MATURITY:
HA1_REQUIRED_FIELDS_IDENTIFIED_BUT_SEMANTICS_INCOMPLETE
GOAL_INTAKE_MATURITY:
GI2_CANONICAL_OWNER_PROVEN_ENTRY_CONTRACT_INCOMPLETE
MINIMALITY_DECISION:
MINIMAL_CONTRACT_PROVEN_FOR_BOUNDED_SINGLE_OWNER_LAN_DESIGN
BUILD_READINESS:
BOUNDED_TRUST_ROOT_BUILD_JUSTIFIED_FOR_PM_REVIEW
CORE_DRIFT_DETECTED:
NO
NEXT_FRONTIER:
OWNER_PROJECT_MANAGER_REVIEW_OF_BOUNDED_TRUST_ROOT_BUILD_READINESS
NEXT_MILESTONE_TYPE:
UNASSIGNED_PENDING_OWNER_PM_DECISION
M117B_AUTHORIZED:
NO
M118_AUTHORIZED:
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
AUTHORITATIVE_FORMAL_DECISION_BLOCK_END
```

The old summary-only boundary label is not selected and is absent from this
corrected record. This EXIT_A result remains a PM-review recommendation only;
it does not authorize Build, finalize M117A, or begin any successor.
