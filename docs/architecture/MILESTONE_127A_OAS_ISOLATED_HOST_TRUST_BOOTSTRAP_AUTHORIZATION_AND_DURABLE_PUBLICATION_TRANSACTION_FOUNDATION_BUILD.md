# M127A OAS Isolated Host Trust-Bootstrap Authorization and Durable Publication Transaction Foundation Build

## 1. Purpose and boundary

M127A is a bounded implementation foundation for the host trust-bootstrap
transaction selected by M126A. It proves authorization parsing, independent
evidence binding, durable transaction intent, prior-generation retention, exact
five-object publication, terminal observation, retry idempotency, and recovery
inside an explicitly issued isolated temporary root.

It does not install trust objects on a real host, deploy OAS, create an Aether
Instance, authenticate an Owner, provide a privileged adapter, or claim that
the filesystem mutation is atomic across `/etc/aether` and `/usr/libexec`.

## 2. Governing decision

The implementation uses the M126A selected model:

`BOOTSTRAP_AUTHORITY_ROOT_MODEL_A_OS_IMAGE_PROVISIONING_BASELINE`

The authority set is an injected authenticated result from a verified OS/image
baseline. The Python implementation cannot discover a host authority set,
replace it, or derive authority from root possession. The pre-instance release
trust model remains separate from Owner trust and future deployment authority.

## 3. Exact build artifacts

The repository scope is exactly:

1. `aether/deployment/host_trust_bootstrap.py`
2. `tests/test_deployment_host_trust_bootstrap.py`
3. `docs/architecture/MILESTONE_127A_OAS_ISOLATED_HOST_TRUST_BOOTSTRAP_AUTHORIZATION_AND_DURABLE_PUBLICATION_TRANSACTION_FOUNDATION_BUILD.md`
4. `tests/test_milestone_127a_oas_isolated_host_trust_bootstrap_authorization_and_durable_publication_transaction_foundation_build.py`

No `PROGRESS.md`, security canon, governance document, prior milestone
artifact, production trust file, live host path, or Git object is part of this
build.

The finalized Git closure is separately authorized for exactly these seven
repository paths:

1. `PROGRESS.md`
2. `docs/architecture/SECURITY_ARCHITECTURE.md`
3. `tests/test_security_architecture_canonization.py`
4. `aether/deployment/host_trust_bootstrap.py`
5. `tests/test_deployment_host_trust_bootstrap.py`
6. `docs/architecture/MILESTONE_127A_OAS_ISOLATED_HOST_TRUST_BOOTSTRAP_AUTHORIZATION_AND_DURABLE_PUBLICATION_TRANSACTION_FOUNDATION_BUILD.md`
7. `tests/test_milestone_127a_oas_isolated_host_trust_bootstrap_authorization_and_durable_publication_transaction_foundation_build.py`

The finalization paths contain only status, canonical traceability, static-lock,
and progress metadata changes; the approved implementation and behavioral test
behavior remain unchanged.

## 4. Trust roles and separation

The host trust-bootstrap authority authenticates the transaction envelope. The
root trust-bootstrap executor verifies the envelope and performs only the
allowlisted isolated-root filesystem effects. The fixed host verifier remains
an object being published and is not recursively used to establish its own
trust. Local-console evidence, governance evidence, image-baseline evidence,
and transaction authorization are independently represented.

Root is an executor, not a source of authority. Candidate, OAS, and ordinary
runtime code cannot supply the injected authority set or select a destination.
M127A does not implement a remote channel, systemd helper, account manager,
network listener, deployment adapter, Owner authority, or Generic Act.

Every verifier is configured by one explicit `TrustVerificationContext`. The
context contains immutable verifier configuration, an opaque process-local
identity, and a durable binding digest. Every verified baseline, authority set,
local-console result, governance result, and authorization carries that exact
context object. An isolated Foundation accepts only an authorization produced
under its configured context. This proves bounded context consumption only; it
does not prove who provisions production keys, the OS/image baseline, local
console authority, governance authority, or Owner authority.

The context has two deliberately separate identities. `process_identity` is a
unique opaque object allocated for each constructed context and is used for
same-process result mixing protection. `durable_fingerprint` is deterministic
and domain-separated. It hashes canonical configuration containing context
schema version, all five trust domains, image/local-console/governance public
key fingerprints, expected image-baseline digest, accepted algorithms, and the
verification-policy version. It contains no process random value. Therefore
identical exact configuration reconstructs the same durable fingerprint after a
restart while never reusing a process identity. Durable records persist this
fingerprint and reject a different reconstructed configuration.

## 5. Closed authenticated record contracts

### 5.1 TrustBootstrapAuthorizationPayload

```text
payload_version
authorization_id
transaction_id
target_host_identity_digest
target_boot_digest
trust_generation
minimum_accepted_generation
object_set_digest
requested_objects
mutation_scope
local_console_attestation_digest
governance_scope_digest
bootstrap_authority_root_fingerprint
bootstrap_authority_generation
authority_set_record_digest
issued_at_utc
expires_at_utc
nonce
```

The payload is canonical JSON with exact fields. Its object scope is the exact
five-object operation:

`PUBLISH_EXACT_FIVE_HOST_TRUST_OBJECTS_FOR_TARGET_HOST_AND_GENERATION`

### 5.2 TrustBootstrapAuthorizationEnvelope

```text
envelope_version
payload_sha256
authorizing_role
authorizing_authority_id
authenticated_evidence_algorithm
detached_signature
verification_key_or_trust_source
issued_at_utc
expires_at_utc
target_host_identity_digest
target_boot_digest
bootstrap_authority_root_fingerprint
bootstrap_authority_generation
authority_set_record_digest
trust_generation
object_set_digest
nonce
transaction_id
domain_separator
```

The domain separator is
`aether.m126a.trust-bootstrap-authorization.v1`. Signature verification uses
the exact M126A signing input: domain separator, NUL delimiter, canonical
payload bytes, a second NUL delimiter, and canonical envelope bytes with
`detached_signature` removed. Public keys are raw 32-byte values and signatures
are raw 64-byte values encoded as unpadded base64url.

The trust-source reference is closed and must identify the independently
authenticated preexisting OS/image authority set:

```text
source_kind
authority_set_path
authority_set_record_digest
authority_id
key_fingerprint_sha256
authority_generation
image_baseline_manifest_digest
```

### 5.3 LocalConsoleAttestationEvidence

```text
evidence_version
attestation_id
target_host_identity_digest
target_boot_digest
bootstrap_authority_root_fingerprint
bootstrap_authority_generation
authority_set_record_digest
local_console_authority_id
session_class
remote
fresh_authentication
human_confirmation_digest
issued_at_utc
expires_at_utc
nonce
evidence_algorithm
authenticated_evidence
```

The implementation requires a fresh, non-remote `LOCAL_CONSOLE` result and an
authenticated evidence marker. The local-console mechanism is injected; M127A
does not implement its hardware or OS authority source.

### 5.4 GovernanceScopeEvidence

```text
evidence_version
governance_evidence_id
milestone
approved_scope_digest
approved_policy_digest
approved_object_set_digest
approved_generation_policy_digest
issuer_role
issuer_authority_id
issued_at_utc
expires_at_utc
authenticated_evidence_algorithm
authenticated_evidence
```

Governance evidence is scope evidence, not host authority. It cannot authorize
deployment, activation, Owner authentication, or a successor milestone.

### 5.5 DurableConsumptionRecord

```text
record_version
transaction_id
authorization_id
verification_context_digest
envelope_sha256
payload_sha256
local_console_attestation_digest
governance_scope_digest
target_host_identity_digest
target_boot_digest
bootstrap_authority_root_fingerprint
bootstrap_authority_generation
authority_set_record_digest
trust_generation
object_set_digest
nonce
state
previous_record_digest
journal_head_digest
issued_at_utc
expires_at_utc
consumed_at_utc
result
failure_class
```

## 6. Verification order

The executor performs no durable mutation before verification completes.

1. Require the capability issued by `create_isolated_root` for purpose
   `M127A_BOOTSTRAP` and the matching transaction root.
2. Validate exact canonical payload, envelope, authority-set, trust-source,
   local-console, and governance records.
3. Recompute payload and authority-set digests and bind every copied envelope
   field to the payload.
4. Verify authority generation, validity, revocation, host identity, current
   boot, nonce, expiry, and exact object scope.
5. Verify the detached Ed25519 signature under the independently injected
   OS/image authority baseline.
6. Validate object bytes and compute the exact object-set digest.
7. Only then persist `TRUST_BOOTSTRAP_REQUESTED`.

Bare digests, unsigned JSON, candidate keys, ordinary-runtime evidence, root-only
evidence, expired authorization, unknown authority, authority-generation
rollback, mismatched boot, and conflicting retry all fail closed.

## 7. The five fixed host trust objects

The only publication paths are:

| Object | Required mode | Boundary |
| --- | --- | --- |
| `/etc/aether/release-trust-anchor.pub` | `0444` | Canonical release trust anchor |
| `/etc/aether/release-trust-anchor.fingerprint` | `0444` | Approved anchor fingerprint |
| `/etc/aether/release-test-evidence.sha256` | `0444` | Approved test-evidence digest |
| `/etc/aether/release-verifier.sha256` | `0444` | Digest bound to verifier bytes |
| `/usr/libexec/aether-release-verify` | `0555` | Fixed verifier bytes |

All five paths are rooted below the injected capability root. Absolute caller
destinations, traversal, symlink parents, symlink targets, hard links, special
files, non-regular prior objects, private-key material, and extra publication
paths are rejected. The verifier digest is recomputed from the supplied
verifier bytes before publication.

## 8. Durable transaction protocol

The state store is the capability-root-relative
`/var/lib/aether/trust-bootstrap/state.sqlite3`. The state database is
`state.sqlite3`; SQLite WAL mode is established
before schema use, `synchronous=FULL` is required, and a capability-root
relative lock serializes transactions. The audit table records every durable
state transition with canonical record bytes and a digest.

The ordered state sequence is:

```text
TRUST_BOOTSTRAP_REQUESTED
TRUST_BOOTSTRAP_VALIDATED
PRIOR_GENERATION_RETAINED
NEXT_GENERATION_STAGED
PUBLISHING
VERIFYING
TRUST_SET_ACTIVE
RESTORING_PRIOR_GENERATION
TRUST_BOOTSTRAP_REVIEW_REQUIRED
```

The state store can commit state and audit atomically, but this does not make the five-object publication filesystem-atomic. The implementation writes each
object with exclusive no-follow creation, file fsync, replacement, and parent
directory fsync. A failure between `/usr/libexec` and `/etc/aether` publication
is therefore recovered by the retained prior generation, not described as an
atomic cross-directory operation.

Before `NEXT_GENERATION_STAGED` is committed, each staged object is created
with exclusive no-follow flags, written with bounded exact bytes, assigned its
fixed mode, flushed, fsynced, and checked by `fstat` for regular-file identity,
single link count, size, and mode. The transaction staging directory is then
checked for exactly five objects, aggregate digest equality, and no extras, and
is fsynced before the state transition. Pre-existing staging entries,
temporary publication files, symlinks, hard links, wrong modes, changed bytes,
and ambiguous cleanup targets fail closed.

The deterministic durability matrix includes `AFTER_STAGED_FILE_FSYNC_0` through
`AFTER_STAGED_FILE_FSYNC_4`, `AFTER_STAGING_DIRECTORY_FSYNC`,
`AFTER_AUDIT_BEFORE_METADATA`, `AFTER_METADATA_BEFORE_COMMIT`,
`BETWEEN_USR_LIBEXEC_AND_ETC_PUBLICATION`, and terminal state/audit commit
failures including `DURING_TERMINAL_STATE_UPDATE`,
`BETWEEN_TERMINAL_STATE_AND_AUDIT`, and `AFTER_TERMINAL_AUDIT_BEFORE_COMMIT`.
Every interruption is reopened through a new Foundation instance;
the journal is validated before any resume or recovery decision.

The Foundation revalidates its immutable verification context, current target
identity and boot, authority validity, generation, nonce, object-set digest,
and authorization expiry while holding the state lock immediately before a
new durable intent. A new expired authorization creates no transaction or
audit intent. A started retry is matched against the complete frozen context,
evidence, authority, target, boot, nonce, generation, scope, and digest set;
expiry may not create a new intent or expand it. An identical terminal retry
returns only the validated recorded result.

The durable generation contract is explicit. `highest_seen_or_reserved_generation`
is advanced only when a `REQUESTED` intent reserves a generation. A
`generation_reservations` row records `RESERVED`, `ACTIVE`, or `BURNED`; a
terminal review burns the generation and a terminal active commit marks it
active. `active_generation` advances only at the terminal `TRUST_SET_ACTIVE`
commit and never advances for a failed or review-required publication. `ACTIVE`
on a historical reservation means that transaction successfully activated; it
does not mean that multiple trust sets are simultaneously current. The single
`schema_metadata.active_generation` value identifies the current highest active
generation.
`minimum_accepted_generation` is a monotonic policy floor and is never lowered.
The transaction's `minimum_accepted_generation` is part of its frozen identity.
Thus a failed generation cannot be reused, a prior active generation remains
truthful during recovery, and burned and active generations are never conflated.

## 9. Prior-generation retention and recovery

Before the first publication, every fixed object is captured as exact prior bytes,
presence, mode, owner, group, and regular-file link identity in the
durable state store. No prior object is overwritten in the retained evidence.

An interruption leaves durable transaction intent and any partial filesystem
state. Recovery requires the transaction ID, takes the same isolated-root
lock, restores the retained prior bytes in reverse publication order, fsyncs
each result, and records terminal `ROOT_REVIEW_REQUIRED`. Automatic recovery
does not claim that a live host is safe, active, or deployed. If no prior
generation existed, recovery removes any partial new objects and still ends in
root review.

Recovery creates independent `RecoveryObservation` and `RecoveryVerification`
records after rereading all five paths, including absent paths, exact bytes,
digests, modes, owner/group model, link count, link identity, and staging
absence. The recovery evidence, terminal review transition, and audit entry
commit atomically. Exact restoration reports
`PRIOR_GENERATION_RESTORED_REVIEW_REQUIRED`; ambiguous restoration records its
failure class and remains review-required. Recovery never silently activates
the interrupted generation.

Identical completed retry returns the original terminal result without
republishing. A retry with a different payload digest, envelope digest, nonce,
object set, target, generation, or authority cannot overwrite the transaction.
Expiry prevents a new mutation intent; an already-started transaction retains
its durable evidence and requires recovery review rather than silently
starting a new operation.

No Python authorization object is treated as crash persistence. The
`bootstrap_from_raw` API accepts the original bounded non-secret canonical
authority, local-console, governance, payload, and envelope bytes plus their
signatures. It reconstructs the configured context, parses the bytes again,
reverifies every signature, and only then calls the durable consumer. An
expired authorization can be supplied only for an already existing identical
intent; the normal consumption-time path still rejects an expired new intent.
Changed evidence, payload, envelope, object bytes, target, boot, nonce,
authority, context fingerprint, or generation fails closed. This is a safe
reconstruction API, not proof of production context provenance.

## 10. Negative authority boundaries

M127A does not create, search for, import, display, copy, install, rotate, or
access private keys. It does not access live `/etc`, `/usr`, `/var`, account,
systemd, socket, network, or deployment authority. The isolated root is created
only by `create_isolated_root`, is process-bound, expires, is mode `0700`, and
contains the lifecycle sentinel required by the existing capability contract.

No packet, release deployment, trust provisioning on a target host, Owner
authorization, instance binding, activation, rollback, Generic Act, or successor
milestone is authorized or performed. `VERIFICATION_STATUS: TEST_VERIFIED` is
test evidence only and is not deployment verification.

## 11. Verification evidence

The behavioral suite proves:

- RFC 8032 Ed25519 acceptance and tamper rejection using precomputed fixtures
  plus test-only ephemeral Ed25519 signatures. Test private keys are created
  only below pytest temporary directories, removed after evidence construction,
  and never persisted in repository artifacts.
- Exact verification-context binding, arbitrary verifier/key substitution
  rejection, complete signed-envelope tamper coverage, and independent
  local-console/governance binding coverage.
- Exact closed record fields and independent evidence requirements.
- Isolated capability enforcement and host-root rejection.
- WAL-first durable state and audit publication.
- Atomic state, audit, and metadata commit gates, nonce/generation uniqueness,
  schema/journal corruption rejection, durable staging fsync, and the complete
  failpoint matrix.
- Exact five-object paths, modes, bytes, digest binding, and ownership.
- Identical retry idempotency and conflicting retry rejection.
- Independently valid same-nonce and same-generation authorization arbitration
  after every competing request passes the complete AuthorizationVerifier path.
- Lower-then-higher and higher-then-lower valid generation ordering, monotonic
  metadata, higher-generation publication, and burned-generation non-reuse.
- Interruption after partial publication, retained prior evidence, reverse
  restoration, independent recovery Observation/Verification, and terminal
  review state.
- Concurrent Foundation serialization and filesystem safety coverage for
  symlinks, hard links, special files, wrong modes, traversal, extra objects,
  missing objects, and ambiguous temporary paths.
- Expired or unauthenticated evidence rejection before state-database creation.
- Secret-material exclusion from publication and returned evidence.

The resumed fourth pass uses ephemeral test signing only. It does not add a
signing API or key handling to `aether/`, does not access any pre-existing
private key, and does not create production signing capability:

```text
TEST_ONLY_EPHEMERAL_KEYS_USED: YES
TEST_PRIVATE_KEYS_PERSISTED: NO
TEST_PRIVATE_KEYS_ENTERED_GIT_ARTIFACTS: NO
PRODUCTION_PRIVATE_KEYS_CREATED: NO
PRODUCTION_PRIVATE_KEYS_ACCESSED: NO
PRODUCTION_SIGNING_CAPABILITY_IMPLEMENTED: NO
```

The tests do not prove who provisions the production verification context,
production keys, OS/image baseline, local-console authority, governance
authority, or Owner authority. They do not prove mutation of a real target
host, production key custody, truthful Owner deployment authority, or
deployment readiness.

## 12. Fourth-pass claim-to-test evidence

| Claim | Exact test node(s) | Result | Evidence inspected | Remaining limitation |
| --- | --- | --- | --- | --- |
| Deterministic context reconstruction | `test_context_has_distinct_process_identity_and_restart_stable_durable_fingerprint` | Pass | two contexts and fresh interpreter fingerprint | production provenance unproven |
| Fresh-process reconstruction boundary | `test_context_has_distinct_process_identity_and_restart_stable_durable_fingerprint`; `test_fresh_context_raw_evidence_reconstruction_allows_only_identical_expired_intent` | Pass | fresh interpreter digest and raw re-verification API | lifecycle capability remains process-bound |
| Frozen expired retry | `test_expiry_after_requested_allows_only_frozen_recovery_and_changed_retry_fails`; `test_fresh_context_raw_evidence_reconstruction_allows_only_identical_expired_intent` | Pass | durable identity, changed evidence, review result | no live restart authority |
| Signed authorization | `test_context_bound_precomputed_signature_and_m126a_fingerprints`; `test_every_signed_envelope_field_rejects_independent_tampering` | Pass | canonical payload/envelope and OpenSSL result | fixture authority only |
| SQLite atomicity | `test_journal_and_schema_corruption_fails_closed`; `test_complete_failpoint_matrix_has_exact_restart_outcome` | Pass | WAL schema, audit chain, commit failpoints | filesystem is not cross-directory atomic |
| Generation semantics | `test_generation_metadata_corruption_is_named_and_fail_closed`; `test_complete_failpoint_matrix_has_exact_restart_outcome`; `test_valid_lower_then_higher_generation_preserves_history_and_advances_active_set`; `test_valid_higher_then_lower_generation_is_stale_without_intent_or_regression`; `test_valid_burned_generation_cannot_be_reused_before_later_generation_activates` | Pass | reservation rows, active/highest/minimum metadata, historical active reservation, stale rejection, burned reservation, later active generation | production generation authority remains unproven |
| Concurrency classes | `test_concurrency_identical_transaction_uses_separate_foundations_and_one_commit`; `test_concurrency_same_transaction_conflicts_have_one_exact_winner`; `test_concurrency_resume_and_two_recovery_callers_have_one_terminal_review`; `test_concurrency_recovery_and_lock_timeout_are_serialized` | Pass | winner, counts, chain, lock, terminal evidence | valid multi-generation signatures are not production evidence |
| Valid same-nonce arbitration | `test_valid_same_nonce_competition_arbitrates_after_both_authorizations_verify` | Pass | two distinct transaction IDs, same nonce, different valid generations, both fully verified before controlled ordering; one winner and one nonce uniqueness conflict; no loser residue | test-only ephemeral authority; isolated root only |
| Valid same-generation arbitration | `test_valid_same_generation_competition_reserves_one_generation` | Pass | two distinct transaction IDs, different valid nonces, same generation, both fully verified before controlled ordering; one active reservation and stale loser with no intent | test-only ephemeral authority; stale gate precedes a second insert |
| Valid generation ordering | `test_valid_lower_then_higher_generation_preserves_history_and_advances_active_set`; `test_valid_higher_then_lower_generation_is_stale_without_intent_or_regression` | Pass | consecutive valid signed generations, exact 14/7 audit counts, two terminal evidence pairs or one unchanged pair, monotonic metadata and final higher objects | production authority and cross-directory atomicity unproven |
| Burned generation and later generation | `test_valid_burned_generation_cannot_be_reused_before_later_generation_activates` | Pass | review recovery burns generation 2; valid generation-2 retry creates no intent; valid generation 3 activates with exact recovery and terminal evidence counts | live-host recovery authority unproven |
| Failpoint groups | `test_complete_failpoint_matrix_has_exact_restart_outcome` | Pass | every listed failpoint's exact prefix, result, counts, reservation, active generation, staging, and objects | process-bound capability in tests |
| Journal corruption | `test_journal_and_schema_corruption_fails_closed`; `test_audit_canonical_link_corruption_fails_closed` | Pass | named JSON/column corruption | SQLite direct tamper is test-only |
| Terminal evidence | `test_successful_bootstrap_commits_terminal_observation_and_verification`; `test_each_terminal_evidence_json_field_corruption_targets_intended_table` | Pass | observation/verifications rows and self-digests | no external observer |
| Recovery evidence | `test_recovery_evidence_bytes_and_digest_corruption_are_independent`; `test_complete_prior_generation_is_restored_and_verified` | Pass | recovery Observation/Verification and prior bytes | review remains required |
| Staging durability | `test_complete_failpoint_matrix_has_exact_restart_outcome`; `test_each_staged_identity_condition_reaches_its_named_rejection` | Pass | exclusive files, fsync points, exact directory set | crash durability is bounded to temporary roots |
| Filesystem identity | `test_each_symlink_identity_boundary_is_independent`; `test_current_and_retained_hard_link_and_mode_identity_are_independent`; `test_fifo_non_regular_and_publication_temporary_path_are_rejected_separately` | Pass | lstat, link count, mode, path and special-file branches | host root is not exercised |
| Secret exclusion | `test_no_private_key_pem_or_live_completion_claims_are_present`; `test_object_scope_and_content_matrix_fails_before_intent` | Pass | source/docs/objects and pre-intent rejection | no production key custody proof |

The filtered full-suite validation uses exactly three node-specific
`--deselect` entries for historical repository-scope assertions. It does not
use `--ignore` and therefore runs all other M124A, M125A, and M126A tests.
This section and the external third corrective summary are evidence, not
authority.

## 13. Finalized Authoritative Status

```text
AUTHORITATIVE_M127A_STATUS_BEGIN
M127A_AUTHORIZED: YES
M127A_STARTED: YES
M127A_FINALIZED: YES
M127A_TYPE: BOUNDED_IMPLEMENTATION_SECURITY_TRANSACTION_FOUNDATION_BUILD
DECISION_STATUS: CURRENT
DESIGN_STATUS: DESIGN_PROVEN
IMPLEMENTATION_STATUS: IMPLEMENTED
VERIFICATION_STATUS: TEST_VERIFIED
DEPLOYMENT_VERIFIED: NO
DEPLOYMENT_STATE: NOT_DEPLOYED
DEPLOYMENT_PROFILE: ISOLATED_ROOT_ONLY
ISOLATED_AUTHORITY_CONSUMPTION_IMPLEMENTED: YES
AUTHENTICATED_ENVELOPE_VERIFICATION_IMPLEMENTED: YES
DURABLE_BOOTSTRAP_TRANSACTION_IMPLEMENTED: YES
ISOLATED_FIVE_OBJECT_PUBLICATION_IMPLEMENTED: YES
TERMINAL_OBSERVATION_VERIFICATION_IMPLEMENTED: YES
VALID_AUTHORIZATION_CONCURRENCY_PROVEN: YES_TEST_ONLY
GENERATION_RESERVATION_SEMANTICS_PROVEN: YES_TEST_ONLY
FILESYSTEM_CROSS_DIRECTORY_ATOMICITY_PROVEN: NO
PRODUCTION_OS_IMAGE_BASELINE_VERIFIED: NO
PRODUCTION_TRUST_MATERIAL_PROVEN: NO
PRODUCTION_PRIVATE_KEYS_CREATED: NO
PRODUCTION_PRIVATE_KEYS_ACCESSED: NO
PRODUCTION_SIGNING_CAPABILITY_IMPLEMENTED: NO
TEST_ONLY_EPHEMERAL_KEYS_USED: YES
TEST_PRIVATE_KEYS_PERSISTED: NO
TEST_PRIVATE_KEYS_ENTERED_GIT_ARTIFACTS: NO
PRIVATE_KEYS_CREATED: NO
PRIVATE_KEYS_ACCESSED: NO
HOST_TRUST_OBJECTS_INSTALLED: NO
TRUTHFUL_OWNER_DEPLOYMENT_AUTHORITY_PROVEN: NO
LIVE_DEPLOYMENT_AUTHORIZED: NO
LIVE_ROLLBACK_AUTHORIZED: NO
TARGET_HOST_MUTATION_PERFORMED: NO
GENERIC_ACT_AUTHORIZED: NO
BUILD_AUTHORIZED: YES
PROGRESS_UPDATED: YES
SECURITY_ARCHITECTURE_UPDATED: YES
COMMIT_CREATED: YES
TAG_CREATED: YES
PUSH_PERFORMED: YES
SUCCESSOR_AUTHORIZED: NO
SUCCESSOR_NUMBER_ASSIGNED: NO
READY_FOR_PM_REVIEW: NO
AUTHORITATIVE_M127A_STATUS_END
```

`PRIVATE_KEYS_CREATED` and `PRIVATE_KEYS_ACCESSED` in this status block refer to
production/deployment custody and remain `NO`; the test-only disposable keys
are separately identified and never constitute production trust material.

M127A is finalized as a bounded isolated-root implementation foundation. It is
Git-durable, committed, tagged, and pushed only after the exact seven-path
finalization closure; deployment remains unverified and no host mutation is
claimed. This record remains evidence and traceability, not authority for a
successor milestone.
