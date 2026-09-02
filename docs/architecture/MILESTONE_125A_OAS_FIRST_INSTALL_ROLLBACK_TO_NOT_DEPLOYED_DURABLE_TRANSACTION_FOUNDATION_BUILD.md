# Milestone 125A OAS First-Install Rollback to NOT_DEPLOYED Durable Transaction Foundation Build

Document role: IMPLEMENTATION, SECURITY, DURABILITY, AND TEST PROOF ONLY.

This record is subordinate to `CONSTITUTION > ARCHITECTURE > SECURITY_ARCHITECTURE > CURRENT IMPLEMENTATION`. M121A remains the deployment contract, M122A remains the repository artifact foundation, M123A remains the non-mutating readiness boundary, and M124A remains the controlled first-install transaction authorization boundary. M125A adds and finalizes an isolated-root rollback foundation; it does not authorize deployment, trust provisioning, host mutation, or an upgrade lifecycle.

## 1. Scope, Baseline, and Exact Artifacts

The verified baseline is:

```text
3aaff2a8ec188650ecb4e132a74d6ef92d3245a6
```

The M124A annotated tag points to the same commit. This build creates exactly these four repository artifacts:

```text
aether/deployment/first_install_rollback.py
tests/test_deployment_first_install_rollback.py
docs/architecture/MILESTONE_125A_OAS_FIRST_INSTALL_ROLLBACK_TO_NOT_DEPLOYED_DURABLE_TRANSACTION_FOUNDATION_BUILD.md
tests/test_milestone_125a_oas_first_install_rollback_to_not_deployed_durable_transaction_foundation_build.py
```

`PROGRESS.md`, all existing production modules, existing tests, finalized evidence, configuration, deployment artifacts, and Git references are protected. No real user, group, unit, release, socket, process, package, credential, key, token, or service-manager state is created or changed. No repository or external summary contains raw host identity, boot identity, credentials, or secrets.

## 2. Bounded Profile and Non-Goals

The only supported profile is:

```text
FIRST_INSTALL_LOCAL_AF_UNIX_ONLY
```

No packet is accepted, no trust material is provisioned, and no live deployment authority is created by this build.

The transaction is valid only for a first install. Upgrade rollback, schema migration, adoption of pre-existing state, automated recovery, public exposure, and generic act operations are rejected or remain outside this build. M125A proves a bounded rollback transaction foundation only inside an injected isolated temporary root. M125A does not prove rollback behavior on the real target host. M125A does not prove production trust material. M125A does not prove truthful Owner deployment or activation authority. M125A does not prove live transition of the target host to `NOT_DEPLOYED`. `DEPLOYMENT_STATE: NOT_DEPLOYED` describes the canonical project deployment state, not a newly observed target-host transition.

The rollback implementation has no account-management, systemd, shell, network, package, trust-bootstrap, or host-path adapter. M125A does not implement any privileged adapter; non-filesystem effects are represented only by the narrow injected `PrivilegedEffectAdapter` protocol. An adapter must return typed, request-bound, boot-bound receipts; an uncertain effect is never treated as absent.

## 3. Contract and Durable State

`RollbackTransactionIdentity` binds the transaction ID, profile, privacy-preserving target and boot digests, source commit, release ID, manifest digests, authorization digest, creation and expiry times, and record sequence. The rollback manifest digest is computed from the exact created-object inventory. The capability is issued by the existing isolated-root factory, is process-local and expiring, is sentinel-bound, and must carry the same transaction ID as the rollback request.

Each `CreatedObjectRecord` identifies one transaction-created filesystem object or one allowlisted privileged operation. Filesystem records bind a root-relative path, pre-existing state, expected type, owner, mode, content or metadata digest, creation evidence digest, dependency order, and inverse action. Privileged records have no filesystem path and name one exact operation. Duplicate steps, duplicate paths, ambiguous dependency order, traversal, absolute paths, symlinked parents, changed owner/mode/content, and ambiguous hard links fail closed.

The append-only rollback journal is stored below the isolated root at `var/lib/aether/rollback/rollback-journal.jsonl`. Every record is canonical JSON, fsynced, directory-fsynced, and chained to its predecessor by SHA-256. The receipt journal is stored at `var/lib/aether/rollback/rollback-receipts.jsonl`; every typed receipt record has a `receipt_sequence`, is canonical, digest-bound, fsynced, and validated before it can resume a step. A bounded exclusive lock at `var/lib/aether/rollback/rollback.lock` prevents concurrent transaction execution and returns a conflict on timeout.

The durable state sequence is:

```text
ROLLBACK_REQUESTED
ROLLBACK_VALIDATING
ROLLBACK_IN_PROGRESS
ROLLBACK_VERIFYING
ROLLED_BACK_NOT_DEPLOYED
```

Any ambiguous object identity, missing expected evidence, failed privileged observation, malformed or conflicting journal, failed durability boundary, or unsupported profile produces a rejection or `ROOT_REVIEW_REQUIRED`; it cannot produce a success state.

## 4. Ordered Rollback Manifest

### M125A-01
- exact action: Bind the first-install transaction identity and rollback manifest digest.
- mutation or read-only classification: `READ_ONLY`
- executing authority/principal: Root transaction executor with process-local capability.
- exact target: One caller-selected isolated temporary root.
- expected previous state: Valid M124A transaction identity and no M125A journal.
- required preconditions: Exact profile, valid digests, UTC expiry window, first-install flags, matching capability transaction.
- resulting state: Transaction accepted for validation.
- postcondition: Identity and object inventory are cryptographically bound.
- verification method: Dataclass validation and canonical digest recomputation.
- rollback or fail-closed action: Reject identity or return root review; no effect occurs.
- automatic-rollback boundary: Before intent persistence.
- sensitive-data classification: Digests and bounded identifiers only.
- Owner confirmation requirement: No new Owner confirmation is implemented here.
- durable evidence produced: Transaction identity fields and rollback manifest digest.

### M125A-02
- exact action: Revalidate isolated-root capability, sentinel, ownership, mode, and root confinement.
- mutation or read-only classification: `READ_ONLY`
- executing authority/principal: Root transaction executor.
- exact target: Capability-bound temporary root.
- expected previous state: Fresh root created by the existing lifecycle factory.
- required preconditions: Capability is process-bound, unexpired, registered, and purpose-bound.
- resulting state: Filesystem rollback may address only the isolated root.
- postcondition: No protected host path or repository checkout is accepted.
- verification method: Existing lifecycle checks plus no-follow path checks.
- rollback or fail-closed action: Reject precondition and perform no mutation.
- automatic-rollback boundary: Before intent persistence.
- sensitive-data classification: No raw host identifiers retained.
- Owner confirmation requirement: Not applicable to isolated test roots.
- durable evidence produced: Capability sentinel and transaction-bound journal records.

### M125A-03
- exact action: Acquire the bounded rollback lock.
- mutation or read-only classification: `MUTATION` followed by `READ_ONLY`
- executing authority/principal: Root transaction executor.
- exact target: Isolated-root rollback lock file.
- expected previous state: No competing rollback holder.
- required preconditions: Lock parent is confined and free of symlinks.
- resulting state: One rollback executor owns the lock.
- postcondition: A competing executor receives `REJECTED_CONFLICT` after the bounded timeout.
- verification method: Non-blocking advisory lock probe and timeout test.
- rollback or fail-closed action: Release lock; return conflict without rollback effects.
- automatic-rollback boundary: Before intent persistence.
- sensitive-data classification: No sensitive data.
- Owner confirmation requirement: None.
- durable evidence produced: Lock file and journal attempt number.

### M125A-04
- exact action: Persist rollback intent before any inverse effect.
- mutation or read-only classification: `MUTATION` followed by `READ_ONLY`
- executing authority/principal: Root transaction executor.
- exact target: Isolated-root rollback journal.
- expected previous state: No journal or a matching resumable journal.
- required preconditions: Journal path is regular, canonical, and chain-valid.
- resulting state: `ROLLBACK_REQUESTED` is durable.
- postcondition: A crash after intent persistence leaves evidence for resume.
- verification method: Canonical JSON, fsync, directory fsync, and chain validation.
- rollback or fail-closed action: Storage error is surfaced; no success is claimed.
- automatic-rollback boundary: Intent persistence is the first durable mutation.
- sensitive-data classification: Bounded digests and identifiers only.
- Owner confirmation requirement: Existing M124A authorization remains authoritative.
- durable evidence produced: Chained `ROLLBACK_REQUESTED` record.

### M125A-05
- exact action: Validate each created-object record and derive reverse dependency order.
- mutation or read-only classification: `READ_ONLY`
- executing authority/principal: Root transaction executor.
- exact target: Transaction rollback manifest.
- expected previous state: Exact transaction identity and unique object inventory.
- required preconditions: No duplicate step, path, or dependency order; first-install flags remain false.
- resulting state: Deterministic inverse plan.
- postcondition: Dependents are removed before their parents.
- verification method: Manifest digest and sorted reverse-order plan.
- rollback or fail-closed action: Reject identity or require root review.
- automatic-rollback boundary: Before first inverse action.
- sensitive-data classification: No raw host state.
- Owner confirmation requirement: None.
- durable evidence produced: `ROLLBACK_VALIDATING` record and ordered step IDs.

### M125A-06
- exact action: Persist the current inverse step before attempting it.
- mutation or read-only classification: `MUTATION` followed by `READ_ONLY`
- executing authority/principal: Root transaction executor.
- exact target: One transaction-bound object or allowlisted privileged operation.
- expected previous state: Previous journal record is durable and chain-valid.
- required preconditions: Step is present in the exact transaction manifest.
- resulting state: `ROLLBACK_IN_PROGRESS` identifies the current step.
- postcondition: Resume can observe an interrupted current step without guessing.
- verification method: Journal chain and current-step binding.
- rollback or fail-closed action: Retain evidence and require root review on ambiguity.
- automatic-rollback boundary: Before the inverse effect.
- sensitive-data classification: Bounded evidence digests only.
- Owner confirmation requirement: None.
- durable evidence produced: Chained current-step record.

### M125A-07
- exact action: Verify filesystem object identity before removal.
- mutation or read-only classification: `READ_ONLY`
- executing authority/principal: Root transaction executor.
- exact target: One root-relative transaction-created path.
- expected previous state: Object has expected type, owner, mode, link count, and content or metadata.
- required preconditions: No symlink parent, traversal, path escape, hard-link ambiguity, or identity drift.
- resulting state: Object is authorized for its exact inverse action.
- postcondition: A mismatch leaves the object unchanged and enters root review.
- verification method: `lstat`, owner/mode checks, content or metadata digest, and no-follow path checks.
- rollback or fail-closed action: `PARTIAL_ROLLBACK_ROOT_REVIEW_REQUIRED`.
- automatic-rollback boundary: Identity verification is required immediately before removal.
- sensitive-data classification: Content is hashed, not retained.
- Owner confirmation requirement: Manual review is required after an identity mismatch.
- durable evidence produced: Failure classification and retained evidence digest.

### M125A-08
- exact action: Remove one verified transaction-created filesystem object and fsync its parent.
- mutation or read-only classification: `MUTATION` followed by `READ_ONLY`
- executing authority/principal: Root transaction executor.
- exact target: One verified regular file, empty directory, or symlink below the isolated root.
- expected previous state: Verified object identity and no unknown directory children.
- required preconditions: Object is not pre-existing, is unchanged, and is not multiply linked.
- resulting state: Object is absent.
- postcondition: `lstat` visibility and durable parent state prove removal.
- verification method: Unlink/rmdir, parent directory fsync, and postcondition check.
- rollback or fail-closed action: Preserve remaining objects and require root review.
- automatic-rollback boundary: Only the current verified object is removed.
- sensitive-data classification: No object content is copied into evidence.
- Owner confirmation requirement: Required for filesystem failures or ambiguity.
- durable evidence produced: Step observation digest and completed-step journal record.

### M125A-09
- exact action: Preserve verified pre-existing filesystem objects.
- mutation or read-only classification: `READ_ONLY`
- executing authority/principal: Root transaction executor.
- exact target: Object marked `PRESENT` in the transaction manifest.
- expected previous state: Object existed before this transaction.
- required preconditions: Current type, owner, mode, and content or metadata still match.
- resulting state: Pre-existing object remains unchanged.
- postcondition: Final verification proves preservation.
- verification method: Same identity checks used before removal.
- rollback or fail-closed action: Root review on any mismatch.
- automatic-rollback boundary: Never remove a pre-existing object.
- sensitive-data classification: Digest-only observation.
- Owner confirmation requirement: Required for mismatch disposition.
- durable evidence produced: Preservation observation digest.

### M125A-10
- exact action: Apply one non-filesystem inverse only through the injected adapter.
- mutation or read-only classification: `MUTATION`
- executing authority/principal: Injected privileged-effect adapter; never this module directly.
- exact target: One allowlisted service/socket or transaction-created principal/group effect.
- expected previous state: Exact request identity, operation, and boot digest.
- required preconditions: Adapter identity is non-empty and receipt contract is satisfied.
- resulting state: Adapter returns `APPLIED` or `ALREADY_ABSENT` with typed receipt.
- postcondition: External effect is receipt-bound and observable.
- verification method: Request digest, adapter identity, operation, boot digest, and typed receipt checks.
- rollback or fail-closed action: Adapter failure or uncertainty enters root review.
- automatic-rollback boundary: No direct privileged fallback exists.
- sensitive-data classification: Receipt contains bounded result and digests only.
- Owner confirmation requirement: Existing explicit authorization is not minted here.
- durable evidence produced: Per-effect receipt and receipt digest.

### M125A-11
- exact action: Persist the privileged-effect receipt before advancing the inverse journal.
- mutation or read-only classification: `MUTATION` followed by `READ_ONLY`
- executing authority/principal: Root transaction executor.
- exact target: Isolated-root receipt journal.
- expected previous state: Typed receipt returned by one adapter call.
- required preconditions: Receipt digest and request binding are valid.
- resulting state: Effect evidence is durable and replay-safe.
- postcondition: Resume validates the stored receipt and does not reapply the effect.
- verification method: Canonical receipt digest, fsync, directory fsync, and retry test.
- rollback or fail-closed action: Storage failure is surfaced; uncertain effect is observed, not repeated.
- automatic-rollback boundary: Before journal completion of the step.
- sensitive-data classification: No secret or raw identity values.
- Owner confirmation requirement: None.
- durable evidence produced: Receipt journal entry and digest.

### M125A-12
- exact action: Observe an interrupted filesystem or privileged step before resuming.
- mutation or read-only classification: `READ_ONLY`
- executing authority/principal: Root transaction executor and injected observation adapter.
- exact target: Current transaction step only.
- expected previous state: Durable `ROLLBACK_IN_PROGRESS` current-step record.
- required preconditions: Journal identity and current step are exact.
- resulting state: Step is completed only when absence or a valid receipt is proven.
- postcondition: Unknown state remains root review; no effect is guessed.
- verification method: Filesystem identity/absence observation or adapter `OBSERVE` receipt.
- rollback or fail-closed action: `ROOT_REVIEW_REQUIRED` with retained evidence.
- automatic-rollback boundary: No repeated mutation follows uncertain observation.
- sensitive-data classification: Observation digests only.
- Owner confirmation requirement: Manual privileged review for uncertainty.
- durable evidence produced: Interruption observation journal record.

### M125A-13
- exact action: Verify all filesystem postconditions and all privileged absence observations.
- mutation or read-only classification: `READ_ONLY`
- executing authority/principal: Root transaction executor plus injected adapter observation.
- exact target: Complete transaction object inventory.
- expected previous state: All inverse steps completed or safely observed.
- required preconditions: No remaining created object, and all pre-existing objects match.
- resulting state: Transaction satisfies isolated-root `NOT_DEPLOYED` conditions.
- postcondition: Exact final observation digest is durable.
- verification method: Full inventory scan and `ABSENT` privileged receipts.
- rollback or fail-closed action: Root review; never emit successful final state.
- automatic-rollback boundary: Final verification has no further automatic mutation.
- sensitive-data classification: Aggregate digests only.
- Owner confirmation requirement: No new confirmation is inferred.
- durable evidence produced: `ROLLBACK_VERIFYING` and final observation digest.

### M125A-14
- exact action: Persist terminal `ROLLED_BACK_NOT_DEPLOYED` only after all gates pass.
- mutation or read-only classification: `MUTATION` followed by `READ_ONLY`
- executing authority/principal: Root transaction executor.
- exact target: Isolated-root rollback journal.
- expected previous state: Durable final verification success.
- required preconditions: Every inverse step is completed, absent, or pre-existing and unchanged; privileged absence is proven.
- resulting state: `ROLLED_BACK_NOT_DEPLOYED`.
- postcondition: Repeated execution returns the same terminal result without new effects.
- verification method: Final journal record, terminal replay test, and full test suite.
- rollback or fail-closed action: Storage or verification failure prevents terminal success.
- automatic-rollback boundary: Terminal record is the final mutation.
- sensitive-data classification: Status and digests only.
- Owner confirmation requirement: This is evidence, not deployment authority.
- durable evidence produced: Terminal chained journal record.

## 5. Failure and Recovery Matrix

| Failure or recovery window | Starting state | Required result | Automatic rollback available | Evidence retained | Forbidden claim |
| --- | --- | --- | --- | --- | --- |
| Before intent persistence | Valid transaction, no journal | Reject or retry with no effect | `NO` | No fabricated evidence | No rollback success |
| After intent persistence | `ROLLBACK_REQUESTED` durable | Resume from durable intent | `YES` for known transaction only | Intent journal | No host deployment conclusion |
| Before inverse action | Current step durable | Resume after revalidation | `YES` only after identity check | Current-step journal | No blind removal |
| After filesystem mutation before journal advance | Object may be absent | Observe and review if identity is not proven | `NO` when ambiguous | Journal plus filesystem observation | No guessed completion |
| After privileged apply before receipt | External state uncertain | Observe through adapter; otherwise root review | `NO` | Current-step journal | No repeated privileged apply |
| After receipt before journal advance | Receipt durable | Validate receipt and advance without reapply | `YES` | Receipt and journal | No duplicate effect |
| Journal or receipt write failure | Effect or evidence boundary failed | Surface storage failure and retain prior evidence | `NO` | Prior fsynced records | No terminal success |
| Identity, owner, mode, content, or hard-link mismatch | Object changed or ambiguous | `PARTIAL_ROLLBACK_ROOT_REVIEW_REQUIRED` | `NO` | Failure classification and digest | No ownership inference |
| Lock contention | Another executor holds lock | `REJECTED_CONFLICT` after bounded timeout | `NO` | Lock path and no mutation | No concurrent execution claim |
| Final verification mismatch | Inverses incomplete | Root review | `NO` | Verification journal | No `NOT_DEPLOYED` proof |
| Unsupported upgrade, migration, or adoption | Out-of-scope request | `REJECTED_UNSUPPORTED_PROFILE` | `NO` | No mutation | No upgrade rollback claim |
| Successful isolated-root completion | All gates pass | `ROLLED_BACK_NOT_DEPLOYED` | `YES` within root | Complete chain and receipts | No real-host deployment claim |

`NOT_DEPLOYED` in this record is explicitly scoped to the isolated temporary root. It is not a statement about global host state, production trust material, live deployment, or service-manager state.

## 6. Verification

The behavioral lock exercises success, pre-existing preservation, reverse dependency ordering, symlink safety, hard-link ambiguity, path confinement, privileged adapter binding, all durable crash windows, receipt-chain tampering and non-replay, expiry and resumability, boot and capability identity mismatch, unsupported lifecycle modes, journal corruption, bounded lock conflict, storage failure, and typed request closure. The static lock verifies exact scope, canonical status, forbidden host operations, isolated-root-only paths, and this ordered manifest.

The test environment does not provision trust material, invoke a real privileged adapter, run systemd, create accounts, publish units, or mutate a target host. M125A does not prove production trust material or truthful Owner deployment or activation authority. `VERIFICATION_STATUS: TEST_VERIFIED` is not deployment verification. Those remain deployment-time and owner-authorized boundaries.

## 7. Authoritative Status

```text
AUTHORITATIVE_M125A_STATUS_BEGIN
M125A_AUTHORIZED: YES
M125A_STARTED: YES
M125A_FINALIZED: YES
M125A_TYPE: BOUNDED_IMPLEMENTATION_FOUNDATION_BUILD
DECISION_STATUS: CURRENT
DESIGN_STATUS: DESIGN_PROVEN
IMPLEMENTATION_STATUS: IMPLEMENTED
VERIFICATION_STATUS: TEST_VERIFIED
DEPLOYMENT_VERIFIED: NO
DEPLOYMENT_STATE: NOT_DEPLOYED
DEPLOYMENT_PROFILE: FIRST_INSTALL_LOCAL_AF_UNIX_ONLY
ROLLBACK_FOUNDATION_IMPLEMENTED: YES
ISOLATED_ROOT_ROLLBACK_PROVEN: YES
LIVE_ROLLBACK_PROVEN: NO
PRIVILEGED_ADAPTERS_IMPLEMENTED: NO
PRODUCTION_TRUST_MATERIAL_PROVEN: NO
TRUTHFUL_OWNER_DEPLOYMENT_AUTHORITY_PROVEN: NO
ROLLBACK_TO_NOT_DEPLOYED_LIVE_PROVEN: NO
SELECTED_EXIT: EXIT_A_BOUNDED_ROLLBACK_FOUNDATION_FINALIZED
BUILD_AUTHORIZED: YES
LIVE_ROLLBACK_AUTHORIZED: NO
LIVE_DEPLOYMENT_AUTHORIZED: NO
TARGET_HOST_MUTATION_PERFORMED: NO
TRUST_PROVISIONING_AUTHORIZED: NO
UPGRADE_AUTHORIZED: NO
SCHEMA_MIGRATION_AUTHORIZED: NO
ADOPTION_AUTHORIZED: NO
PUBLIC_EXPOSURE_AUTHORIZED: NO
GENERIC_ACT_AUTHORIZED: NO
PROGRESS_UPDATED: YES
COMMIT_CREATED: YES
TAG_CREATED: YES
PUSH_PERFORMED: YES
SUCCESSOR_AUTHORIZED: NO
SUCCESSOR_NUMBER_ASSIGNED: NO
READY_FOR_PM_REVIEW: NO
AUTHORITATIVE_M125A_STATUS_END
```

`EXIT_A_BOUNDED_ROLLBACK_FOUNDATION_FINALIZED` records Git-durable closure of the bounded M125A artifact and isolated-root proof. It is not general or live rollback proof and does not authorize a live rollback, deployment, trust provisioning, or any target-host mutation. `DEPLOYMENT_STATE: NOT_DEPLOYED` remains the canonical project deployment state, not a newly observed target-host transition.

## 8. Git-Durable Closure

The finalization commit, annotated tag, remote publication, exact five-path scope, and post-publication object identities are recorded in the external finalization summary:

```text
/home/aether/summaries/milestone_125A_oas_first_install_rollback_to_not_deployed_durable_transaction_foundation_build_finalization_summary.txt
```

The finalization summary is evidence, not authority. It preserves the bounded claim boundary and does not authorize live operations or a successor milestone.
