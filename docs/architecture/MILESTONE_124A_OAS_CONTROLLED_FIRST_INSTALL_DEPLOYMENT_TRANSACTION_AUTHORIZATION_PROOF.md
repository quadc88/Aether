# Milestone 124A OAS Controlled First-Install Deployment Transaction Authorization Proof

Document role: CORRECTIVE DESIGN / DISCOVERY / SECURITY / OPERATIONS CONTRACT
PROOF ONLY.

This record remains subordinate to:

```text
CONSTITUTION > ARCHITECTURE > SECURITY_ARCHITECTURE > CURRENT IMPLEMENTATION
```

M124A is authorized, started, and PM-authorized for finalization. M121A remains the
canonical repository-to-host deployment and rollback contract. M122A remains
the repository deployment-artifact foundation. M123A remains the finalized
non-mutating target-readiness evidence. This finalized negative-gated proof does
not begin a new milestone, assign a successor, implement Human Authority,
provision trust material, deploy OAS, or mutate the target host.

## 1. Scope and Baseline

The one bounded profile is:

```text
FIRST_INSTALL_LOCAL_AF_UNIX_ONLY
```

The transaction definition covers one empty target namespace, one candidate,
three pathname `AF_UNIX` `SOCK_SEQPACKET` sockets, one `aether-oas` service,
one root transaction executor, exact readiness and smoke gates, and an
explicit Owner activation hold point. It does not cover upgrade, schema
migration, adoption, automated recovery, upgrade rollback, public exposure,
or network deployment.

The immutable baseline is:

```text
M123A_FINAL_COMMIT: 71081299701e4bb1ed8b8914173176c3743cfef4
M123A_FINAL_TAG: milestone-123A-oas-target-host-deployment-readiness-non-mutating-rehearsal-proof
M123A_SOURCE_TREE: 150647beba7c01d854848129e9c5bcb0c51c74ce
```

Exactly these two repository artifacts are in scope:

```text
docs/architecture/MILESTONE_124A_OAS_CONTROLLED_FIRST_INSTALL_DEPLOYMENT_TRANSACTION_AUTHORIZATION_PROOF.md
tests/test_milestone_124a_oas_controlled_first_install_deployment_transaction_authorization_proof.py
```

`PROGRESS.md`, `README.md`, the Constitution, Architecture, Security
Architecture, all finalized historical records, production code, deployment
artifacts, dependencies, configuration, and Git references are protected. No
host user, group, directory, trust object, release, unit, socket, process,
package, credential, key, token, or service-manager state was created or
changed.

## 2. Corrected Status Model

These are independent facts:

| Dimension | Meaning | Current result |
| --- | --- | --- |
| deployment transaction definition | The packet, ordered actions, gates, and failure boundaries are specified | `YES` |
| deployment transaction authorization | A valid packet has been accepted for host mutation | `NO` |
| production trust-material availability | An approved signing authority, public anchor, candidate, and bootstrap authority are directly proven | `NO` |
| installed target-host trust state | The five fixed trust objects are already present on this host | `NOT_PRESENT` |
| rollback definition | Required rollback actions and evidence fields are specified | `YES` |
| rollback proof | The current implementation proves return to `NOT_DEPLOYED` for every interruption window | `NO` |
| deployment state | OAS is installed and active on the target | `NOT_DEPLOYED` |
| deployment verification | A real deployment has produced reviewed host-bound evidence | `NO` |
| PM review submission | This corrective record and summary are ready to evaluate | `YES` |

`DEPLOYMENT_TRANSACTION_DEFINED: YES` does not mean
`TRANSACTION_AUTHORIZED: YES`. `PRODUCTION_TRUST_MATERIAL_PROVEN: NO` does not
mean that production trust material is globally absent. `INSTALLED_TARGET_HOST_TRUST_STATE:
NOT_PRESENT` means only that the inspected target host has not received the
fixed objects. `ROLLBACK_DEFINED: YES` does not mean that rollback is proven.
Fail closed is not equivalent to `DEPLOYMENT_STATE: NOT_DEPLOYED` when durable
partial state may exist.

## 3. Corrected Trust-Material Model

### 3.1 Production signing authority

No approved production signing-authority record, approved key-ID set, or
independent custody/review evidence was supplied to this pass. No private-key
search, import, generation, or exposure was performed. The truthful result is:

```text
PRODUCTION_SIGNING_AUTHORITY_PROVEN: NO
```

This is a lack of direct proof in the available evidence, not a claim that an
external production authority cannot exist. It does not prove global
unavailability.

### 3.2 Production public trust anchor

No authorized out-of-band anchor source or independently approved fingerprint
was available to inspect. The repository test key and test fixture anchor are
not production authority. The truthful result is:

```text
PRODUCTION_PUBLIC_TRUST_ANCHOR_PROVEN: NO
```

The frozen M121A rule remains: the anchor is out-of-band, is not part of a
release, is never candidate-supplied, and is accepted only after independent
fingerprint approval.

### 3.3 Production signed release

No exact production-signed candidate release was directly proven. The
repository has a manifest generator, dependency lock, wheelhouse, four unit
files, and fixed verifier source, but these are not one production-signed
release. No candidate was promoted from a test fixture.

```text
PRODUCTION_SIGNED_CANDIDATE_PROVEN: NO
```

A future candidate must bind the source commit, source tree, release manifest,
dependency lock, offline wheelhouse, unit bundle, unit generation, runtime
entrypoint, initial schema, fixed verifier identity, release signature,
approval signature, approved test-evidence digest, and exact packet digest.

### 3.4 Installed target-host trust state

The fixed target paths were inspected read-only:

| Object | Installed state | Meaning |
| --- | --- | --- |
| `/etc/aether/release-trust-anchor.pub` | `NOT_PRESENT` | no installed public anchor observed |
| `/etc/aether/release-trust-anchor.fingerprint` | `NOT_PRESENT` | no installed approved anchor fingerprint observed |
| `/etc/aether/release-test-evidence.sha256` | `NOT_PRESENT` | no installed approved evidence digest observed |
| `/etc/aether/release-verifier.sha256` | `NOT_PRESENT` | no installed verifier approval observed |
| `/usr/libexec/aether-release-verify` | `NOT_PRESENT` | no installed fixed verifier observed |

The absence of these objects on a `NOT_DEPLOYED` target does not prove global
unavailability. It does prove that this target is not eligible for candidate
trust. The absence of `/opt/aether`, `/run/aether`, target principals, units,
activation record, and OAS state remains expected first-install output.

### 3.5 Trust bootstrap boundary

M121A places initial anchor provisioning and fixed-verifier custody outside the
candidate-controlled deployment transaction. A separately authorized host
trust-bootstrap operation must provision and verify the fixed objects before a
future OAS deployment transaction begins. M124A performs no such operation.
The deployment transaction may inspect trust-bootstrap prerequisites, but it
must reject before candidate acceptance when they are absent or ambiguous.

### 3.6 Candidate-supplied material prohibition

The candidate must never supply or select:

- a trust anchor;
- an anchor fingerprint;
- a test, development, or self-approved key;
- a verifier executable or verifier hash;
- a private key or credential;
- an alternate trust path;
- a replacement approval policy.

Private keys, credentials, raw signatures, raw machine IDs, raw boot IDs, and
secret-bearing material are excluded from the repository, test evidence, and
both M124A summaries.

## 4. Owner, Project Manager, and Executor Authority

The terms are not interchangeable.

### Project Manager

The Project Manager authorizes M124A scope, evaluates this architecture and its
evidence, may authorize repository finalization in a later decision, and may
return the proof for correction. The Project Manager cannot mint Owner
authentication evidence or silently authorize target-host mutation on behalf
of the Owner.

### Owner

The Owner reviews the exact Deployment Authorization Packet, authorizes the
exact target mutation transaction, and authorizes or rejects activation at the
explicit activation hold point. Owner authorization is one-use, exact-scope,
target-bound, boot-bound, digest-bound, and expiry-bound. It does not authorize
future upgrades, migrations, recovery, rollback, public exposure, or unrelated
root operations.

### Root transaction executor

The root transaction executor verifies the exact Owner evidence, PM-approved
scope, packet, trust material, replay state, and mutation digest. It executes
only the fixed manifest. Root possession is not Owner intent. Root cannot infer
Owner authorization, expand scope, replace the packet, select a trust root,
or substitute local root access for Owner confirmation.

### Ordinary Aether runtime

The ordinary runtime receives no root or deployment authority. It cannot mint
Owner evidence, change the packet, access the trust root, select a release,
modify the mutation manifest, write the activation record, control systemd,
or authorize activation.

### Current Owner-authority truth

M117A and the canonical Security Architecture state that HA1 remains
incomplete. No live source capable of producing truthful Owner deployment
authorization or activation evidence is currently implemented or proven.

```text
OWNER_DEPLOYMENT_AUTHORIZATION_SOURCE_PROVEN: NO
OWNER_ACTIVATION_CONFIRMATION_SOURCE_PROVEN: NO
```

M124A does not implement Human Authority. This is a deployment-authorization
prerequisite gap, not a reason to relabel a process-local caller as Owner.

## 5. Deployment Authorization Packet

### 5.1 Closed packet shape

The future packet has exactly these top-level fields:

```text
packet_version
packet_id
transaction_id
profile
target
candidate
trust
dependencies
units
authorization
timing
replay
mutation_manifest
rollback
```

The packet is canonical UTF-8 JSON with lexicographically sorted keys,
`separators=(',', ':')`, `ensure_ascii=true`, finite values only, bounded size,
no duplicate keys, no unknown fields, and no trailing newline. It is not
created by M124A.

### 5.2 Required bindings

| Object | Required fields |
| --- | --- |
| `target` | `target_host_identity_digest`, `observation_boot_digest`, `observation_digest`, `observation_time_utc` |
| `candidate` | `source_commit`, `source_tree`, `source_root_digest`, `release_id`, `manifest_sha256`, `manifest_length`, `envelope_sha256`, `manifest_version`, `runtime_entrypoint`, `initial_schema` |
| `trust` | `anchor_fingerprint`, `verifier_path`, `verifier_sha256`, `verifier_version`, `approved_test_evidence_digest`, `accepted_key_ids`, `signature_results` |
| `dependencies` | `closure_status`, `lock_digest`, `wheelhouse_digest`, `artifact_count`, `interpreter`, `platform` |
| `units` | `unit_generation_id`, `unit_bundle_digest`, `unit_names`, `unit_declaration_digest` |
| `authorization` | `project_manager_scope_record_digest`, `owner_authorization_record_digest`, `owner_activation_confirmation_record_digest`, `approval_id`, `scope_digest`, `review_status` |
| `timing` | `issued_at_utc`, `expires_at_utc`, `max_duration_seconds`, `monotonic_window_policy` |
| `replay` | `packet_digest`, `transaction_nonce`, `record_sequence`, `previous_record_digest`, `consumption_state` |
| `mutation_manifest` | `manifest_version`, `mutation_manifest_digest`, `ordered_step_ids` |
| `rollback` | `rollback_manifest_digest`, `empty_namespace_digest`, `rollback_owner`, `manual_review_policy` |

The packet binds the exact target, candidate, trust, dependency, unit,
authorization, replay, mutation, and rollback values. Release and approval
signatures reuse the M121A signing contract; the packet is not an alternate
signing authority.

### 5.3 Validation and hold sequence

1. Parse the bounded canonical packet and reject duplicate, missing, or unknown
   fields.
2. Verify packet identity, transaction nonce, expiry, profile, and replay
   state.
3. Recompute the packet digest without its digest field.
4. Revalidate target and boot identity read-only.
5. Verify PM scope evidence and exact Owner deployment authorization evidence.
6. Verify the independently approved trust bootstrap and fixed verifier.
7. Verify the production-signed candidate, source, manifest, dependencies,
   wheelhouse, runtime, initial schema, units, and generation.
8. Verify the complete mutation and rollback manifests.
9. Repeat all read-only checks while holding the transaction lock.
10. Enter `CANDIDATE_PENDING` only after the pre-activation verification hold
    point is closed.
11. Require the separate Phase 4 Owner activation confirmation unless the
    frozen authority architecture proves that the original one-use evidence
    explicitly and safely covers the final Phase 3 digest.

The current truth fails at steps 5 and 6. No packet is accepted and no target
mutation follows.

## 6. Complete Ordered Mutation Manifest

The manifest is represented as one structured record for every step. Every
record has the same required fields. `READ_ONLY` means no target mutation is
permitted by that step. `MUTATION` means a future separately authorized root
executor could perform the exact action only after its stated gates pass.

### M124A-00

- step ID: `M124A-00`
- phase: `PHASE 0 — OWNER AUTHORIZATION`
- exact action: Validate the exact packet, PM scope record, one-use Owner deployment authorization, target/profile/digest bindings, and expiry; do not consume or mutate.
- mutation or read-only classification: `READ_ONLY`
- executing authority/principal: Root transaction executor verifies; Project Manager scope and Owner authorization are separate evidence sources.
- exact target: Deployment Authorization Packet in external review evidence; no host path.
- expected previous state: No packet consumed; target `NO_DEPLOYMENT`.
- required preconditions: M124A scope is PM-authorized; packet is canonical; truthful Owner evidence exists; all required fields are exact.
- resulting state: `PACKET_PRESENT_UNCONSUMED` or rejected.
- postcondition: Every packet field and authority record digest matches the review scope.
- verification method: Canonical parser, signature verification, digest recomputation, scope comparison, and one-use/replay check.
- rollback or fail-closed action: Reject without consumption; preserve only bounded rejection evidence.
- automatic-rollback boundary: `NO`; no mutation occurs.
- sensitive-data classification: `NON_SECRET_DIGESTS_ONLY`; no credentials or private keys.
- Owner confirmation requirement: `YES`; exact deployment scope must be reviewed by Owner.
- durable evidence produced: Packet-validation result and rejected/accepted decision digest.

### M124A-01

- step ID: `M124A-01`
- phase: `PHASE 1 — READ-ONLY REVALIDATION`
- exact action: Revalidate target identity, boot identity, packet expiry, replay sequence, source identity, trust availability, installed trust state, empty namespace, and conflicting objects.
- mutation or read-only classification: `READ_ONLY`
- executing authority/principal: Root transaction executor.
- exact target: `/etc/machine-id` digest, boot digest, fixed trust paths, deployment namespace, principals, units, sockets, and processes.
- expected previous state: Packet present but unconsumed; no deployment mutation.
- required preconditions: M124A-00 accepted; read-only observation tools available; no secret values retained.
- resulting state: `REVALIDATED` or invalidated authorization.
- postcondition: Current observation equals every packet-bound target and precondition digest.
- verification method: M123A domain-separated identity digest, `lstat`, principal lookup, systemd read-only state, listener/process checks.
- rollback or fail-closed action: Invalidate packet; do not stage, provision, or consume.
- automatic-rollback boundary: `NO`; mismatch is reject-before-mutation.
- sensitive-data classification: `PRIVACY_PRESERVING_DIGESTS_ONLY`.
- Owner confirmation requirement: `NO` for observation; original Owner scope remains required.
- durable evidence produced: Redacted revalidation record with digest and status only.

### M124A-02

- step ID: `M124A-02`
- phase: `PHASE 1 — READ-ONLY REVALIDATION`
- exact action: Acquire the fixed exclusive transaction lock and bind it to the packet transaction identity.
- mutation or read-only classification: `MUTATION`
- executing authority/principal: Root transaction executor.
- exact target: `/run/lock/aether-install.lock`.
- expected previous state: No M124A transaction lock held; no deployment object created.
- required preconditions: M124A-01 passed; packet unexpired; transaction identity and replay sequence are unused.
- resulting state: `TRANSACTION_LOCK_HELD`.
- postcondition: One executor holds the lock for this transaction and no competing transaction is admitted.
- verification method: Exclusive file lock, transaction identity check, and process-local ownership check.
- rollback or fail-closed action: Release lock; preserve no deployment claim.
- automatic-rollback boundary: `NO`; lock release is not deployment rollback.
- sensitive-data classification: `NON_SECRET_TRANSACTION_ID`.
- Owner confirmation requirement: `NO`; Owner scope was checked at M124A-00.
- durable evidence produced: Lock-acquisition and transaction-binding record.

### M124A-03

- step ID: `M124A-03`
- phase: `PHASE 2 — INACTIVE STAGING`
- exact action: Create root-owned transaction staging below `/var/lib/aether/install/<tx>` without creating release, unit, socket, service, or current-link output.
- mutation or read-only classification: `MUTATION`
- executing authority/principal: Root transaction executor.
- exact target: Isolated transaction staging directory only.
- expected previous state: Transaction staging absent; target deployment namespace empty.
- required preconditions: M124A-02 held; packet and source identities remain valid; no symlink parent.
- resulting state: `STAGING_CREATED`.
- postcondition: Staging is mode `0700`, root-owned, transaction-bound, and outside live activation paths.
- verification method: `lstat`, owner/mode/type checks, sentinel and path containment checks.
- rollback or fail-closed action: Remove only exact transaction staging; ambiguous identity requires hold.
- automatic-rollback boundary: `NO`; current production API is isolated-root only and does not prove host cleanup.
- sensitive-data classification: `CANDIDATE_BYTES`; no credentials or private keys.
- Owner confirmation requirement: `NO`; staging is within the exact already-authorized scope.
- durable evidence produced: Staging identity and path-boundary record.

### M124A-04

- step ID: `M124A-04`
- phase: `PHASE 2 — INACTIVE STAGING`
- exact action: Copy every candidate file into staging using exclusive no-follow regular-file writes and bind each hash, size, mode, and path to the manifest.
- mutation or read-only classification: `MUTATION`
- executing authority/principal: Root transaction executor.
- exact target: `/var/lib/aether/install/<tx>/release` only.
- expected previous state: Empty transaction release staging.
- required preconditions: M124A-03 passed; source is not a development checkout; candidate manifest is exact.
- resulting state: `CANDIDATE_STAGED`.
- postcondition: Staged inventory equals the candidate manifest and is not reachable through live `current`.
- verification method: Rehash source and destination, compare file metadata, reject symlinks/hardlinks/special files.
- rollback or fail-closed action: Remove exact isolated staging; retain mismatch evidence; do not publish.
- automatic-rollback boundary: `NO`; only isolated cleanup is available in current API.
- sensitive-data classification: `CANDIDATE_BYTES`; secret-bearing files are prohibited.
- Owner confirmation requirement: `NO`.
- durable evidence produced: Staged inventory digest and copy result.

### M124A-05

- step ID: `M124A-05`
- phase: `PHASE 3 — PRE-ACTIVATION VERIFICATION HOLD POINT`
- exact action: Check that out-of-band trust bootstrap prerequisites are already installed and independently approved; never provision them from the candidate.
- mutation or read-only classification: `READ_ONLY`
- executing authority/principal: Root transaction executor reads fixed paths; separate trust-bootstrap authority is external to this transaction.
- exact target: `/etc/aether/release-trust-anchor.pub`, `/etc/aether/release-trust-anchor.fingerprint`, `/etc/aether/release-test-evidence.sha256`, `/etc/aether/release-verifier.sha256`, `/usr/libexec/aether-release-verify`.
- expected previous state: Fixed trust objects are present, regular, root-owned, exact-mode, and independently approved.
- required preconditions: Separate trust-bootstrap authorization and custody evidence; no candidate control of these paths.
- resulting state: `TRUST_BOOTSTRAP_READY` or `TRUST_BOOTSTRAP_MISSING`.
- postcondition: Anchor fingerprint, verifier digest, approved evidence digest, and fixed verifier identity are proven.
- verification method: `lstat`, owner/mode/link checks, canonical anchor parsing, fingerprint comparison, fixed verifier hash.
- rollback or fail-closed action: Reject candidate; do not create or replace any trust object.
- automatic-rollback boundary: `NO`; trust provisioning is outside the OAS transaction.
- sensitive-data classification: `PUBLIC_TRUST_METADATA_ONLY`; private keys are never read.
- Owner confirmation requirement: `YES` for separate trust-bootstrap authority; not satisfied here.
- durable evidence produced: Trust-prerequisite result with public fingerprints and hashes only.

### M124A-06

- step ID: `M124A-06`
- phase: `PHASE 3 — PRE-ACTIVATION VERIFICATION HOLD POINT`
- exact action: Verify the exact production-signed manifest and approval envelope with the fixed host verifier.
- mutation or read-only classification: `READ_ONLY`
- executing authority/principal: Fixed host verifier under root executor orchestration.
- exact target: Staged manifest/envelope and preexisting host trust objects.
- expected previous state: Candidate staged; trust bootstrap ready; no pending activation record.
- required preconditions: M124A-05 passed; source, release, anchor, approval, and verifier identities are bound.
- resulting state: `CANDIDATE_TRUST_VERIFIED` or rejected.
- postcondition: Release and approval signatures, roles, expiry, source, release ID, and anchor fingerprint all match.
- verification method: Fixed `/usr/libexec/aether-release-verify` and M121A exact OpenSSL invocation; no alternate verifier.
- rollback or fail-closed action: Reject candidate; do not write pending state; preserve only bounded trust failure evidence.
- automatic-rollback boundary: `NO`; no production candidate was accepted.
- sensitive-data classification: `PUBLIC_SIGNATURE_RESULT`; raw signature and key material are temporary only.
- Owner confirmation requirement: `NO`; trust provenance is not activation authority.
- durable evidence produced: Immutable transaction trust evidence before pending state.

### M124A-07

- step ID: `M124A-07`
- phase: `PHASE 3 — PRE-ACTIVATION VERIFICATION HOLD POINT`
- exact action: Verify dependency closure, offline wheelhouse, installed file hashes, runtime entrypoint, initial schema, exact unit bytes, and unit generation.
- mutation or read-only classification: `READ_ONLY`
- executing authority/principal: Root transaction executor and fixed unit/dependency verifiers.
- exact target: Staged release, `deployment/requirements.lock.json`, `deployment/wheelhouse`, runtime entrypoint, schema contract, and four unit files.
- expected previous state: Candidate trust verified; no live release, unit, socket, or state mutation.
- required preconditions: M124A-06 passed; lock status `COMPLETE`; wheelhouse is offline and exact.
- resulting state: `PRE_ACTIVATION_VERIFICATION_PASSED` or rejected.
- postcondition: Every source, dependency, wheel, runtime, schema, unit, generation, owner, mode, and hash binding matches.
- verification method: Manifest validation, closure verifier, inventory rehash, `verify_unit_bytes`, isolated `systemd-analyze verify`, effective-policy review.
- rollback or fail-closed action: Reject; remove only isolated staging; no pending record or live unit publication.
- automatic-rollback boundary: `NO`; current implementation has no production reverse transaction.
- sensitive-data classification: `NON_SECRET_HASHES_AND_METADATA`.
- Owner confirmation requirement: `NO`; this closes verification, not activation authority.
- durable evidence produced: Complete Phase 3 verification digest and hold-point result.

### M124A-08

- step ID: `M124A-08`
- phase: `PHASE 4 — EXPLICIT ACTIVATION AUTHORITY`
- exact action: Create the fixed principals and groups only after the final Phase 3 digest and exact Owner activation authority are accepted.
- mutation or read-only classification: `MUTATION`
- executing authority/principal: Root transaction executor; Owner authorizes scope; Project Manager does not substitute for Owner.
- exact target: `aether-owner`, `aether-runtime`, `aether-oas`, `aether-bootstrap`, and their fixed groups/IDs.
- expected previous state: All target names and numeric IDs absent; no partial principal state.
- required preconditions: Phase 3 hold closed; explicit Owner activation confirmation valid, or frozen architecture proves original coverage; empty-state gate passes.
- resulting state: `PRINCIPALS_CREATED` or rejected.
- postcondition: Exact IDs, shells, homes, primary groups, supplementary groups, and login policy match M119A.
- verification method: Root account/group database readback and collision checks without changing unrelated accounts.
- rollback or fail-closed action: No automatic deletion; preserve exact creation evidence and require manual privileged review.
- automatic-rollback boundary: `NO`; current API does not safely deprovision principals.
- sensitive-data classification: `PUBLIC_IDENTITY_METADATA`.
- Owner confirmation requirement: `YES`; activation authority is not inferred from root or PM review.
- durable evidence produced: Principal creation receipts and before/after identity digest.

### M124A-09

- step ID: `M124A-09`
- phase: `PHASE 4 — EXPLICIT ACTIVATION AUTHORITY`
- exact action: Create the fixed root, state, runtime, backup, rollback, activation, and `/var/empty` directories with exact ownership and modes.
- mutation or read-only classification: `MUTATION`
- executing authority/principal: Root transaction executor.
- exact target: `/etc/aether`, `/opt/aether`, `/var/lib/aether`, `/var/lib/aether/activation`, `/var/lib/aether/oas`, `/var/lib/aether/install`, `/var/lib/aether/backups`, `/var/lib/aether/rollback`, `/run/aether`, `/run/aether/oas`, `/var/empty`.
- expected previous state: Required first-install paths absent or only approved parent paths present; no symlink conflicts.
- required preconditions: M124A-08 passed; every object has exact owner/mode/type policy; no existing state is adopted.
- resulting state: `NAMESPACE_CREATED` or rejected.
- postcondition: Parents are exact, root-owned where specified, and no unauthorized files or mounts exist.
- verification method: `lstat`, owner/group/mode/type checks, mount and symlink checks, direct-child inventory.
- rollback or fail-closed action: Remove only exact transaction-created empty directories in reverse order; otherwise manual review.
- automatic-rollback boundary: `NO`; no complete production directory rollback API exists.
- sensitive-data classification: `NON_SECRET_PATH_METADATA`.
- Owner confirmation requirement: `YES`; directory creation is part of exact activated scope.
- durable evidence produced: Namespace creation inventory and ownership/mode digest.

### M124A-10

- step ID: `M124A-10`
- phase: `PHASE 5 — BOUNDED ACTIVATION`
- exact action: Publish the verified release directory by atomic rename after all trust and pre-activation gates remain valid.
- mutation or read-only classification: `MUTATION`
- executing authority/principal: Root transaction executor.
- exact target: `/opt/aether/releases/<release_id>`.
- expected previous state: Release ID absent; `current` absent; staged release complete.
- required preconditions: M124A-07 passed; Owner activation authority valid; target remains empty; release is immutable and unreferenced.
- resulting state: `RELEASE_PUBLISHED`.
- postcondition: Published release inventory and digest equal the verified candidate; no mutable release path exists.
- verification method: Atomic rename, parent fsync, inventory rehash, owner/mode/link checks, release ID comparison.
- rollback or fail-closed action: Unlink only exact unreferenced candidate release and fsync parent; ambiguity enters recovery.
- automatic-rollback boundary: `NO`; installer API proves isolated roots only.
- sensitive-data classification: `CANDIDATE_BYTES_WITHOUT_SECRETS`.
- Owner confirmation requirement: `YES`; release publication is within exact Owner-authorized mutation scope.
- durable evidence produced: Release publication identity and parent-durability record.

### M124A-11

- step ID: `M124A-11`
- phase: `PHASE 5 — BOUNDED ACTIVATION`
- exact action: Publish the exact four unit files through root-owned temporary files and atomic renames after proven quiescence.
- mutation or read-only classification: `MUTATION`
- executing authority/principal: Root transaction executor; systemd is not the file writer.
- exact target: `/etc/systemd/system/aether-oas.service`, `aether-oas-runtime.socket`, `aether-oas-bootstrap.socket`, `aether-oas-broker.socket`.
- expected previous state: No target units for first install; no service, socket, process, job, or populated cgroup.
- required preconditions: Phase 3 passed; explicit first-install empty state; quiescence proof; unit generation matches packet.
- resulting state: `UNIT_BUNDLE_PUBLISHED` or mixed/ambiguous failure.
- postcondition: Every unit byte, owner, mode, generation condition, socket path, and AF_UNIX restriction matches.
- verification method: File rehash, `verify_unit_bytes`, isolated `systemd-analyze verify`, and readback before reload.
- rollback or fail-closed action: Do not start; remove or restore only a fully identified bundle; mixed state requires review.
- automatic-rollback boundary: `NO`; four-file replacement is not one atomic filesystem transaction.
- sensitive-data classification: `PUBLIC_UNIT_CONFIGURATION`.
- Owner confirmation requirement: `YES`.
- durable evidence produced: Unit publication and generation-binding record.

### M124A-12

- step ID: `M124A-12`
- phase: `PHASE 5 — BOUNDED ACTIVATION`
- exact action: Publish the exact generation gate only after the complete unit bundle is verified.
- mutation or read-only classification: `MUTATION`
- executing authority/principal: Root transaction executor.
- exact target: `/var/lib/aether/activation/unit-generations/<generation>.ready`.
- expected previous state: Candidate generation gate absent; all four unit files already match.
- required preconditions: M124A-11 complete; generation and unit bundle digest match packet; no gate collision.
- resulting state: `GENERATION_GATE_PUBLISHED`.
- postcondition: Gate is canonical, root-owned mode `0444`, and contains exact generation, unit hashes, transaction, and `VERIFIED` marker.
- verification method: Canonical JSON parse, digest recomputation, owner/mode/type check, generation condition readback.
- rollback or fail-closed action: Remove only exact unreferenced candidate gate; mixed unit/gate identity requires recovery.
- automatic-rollback boundary: `NO`; current API can install a gate but cannot prove whole-host reversal.
- sensitive-data classification: `NON_SECRET_HASHES_AND_TRANSACTION_ID`.
- Owner confirmation requirement: `YES`.
- durable evidence produced: Generation-gate publication digest.

### M124A-13

- step ID: `M124A-13`
- phase: `PHASE 5 — BOUNDED ACTIVATION`
- exact action: Write the canonical `CANDIDATE_PENDING` activation record only after durable trust evidence and all pre-activation identities exist.
- mutation or read-only classification: `MUTATION`
- executing authority/principal: Root transaction executor; OAS may read but not write this record.
- exact target: `/var/lib/aether/activation/activation-record.json`.
- expected previous state: No activation record; release and unit generation are candidate-published but inactive.
- required preconditions: M124A-05 through M124A-12 passed; trust evidence exists before pending; exact old identities are null.
- resulting state: `CANDIDATE_PENDING`.
- postcondition: Record is canonical, root-owned mode `0444`, transaction-bound, and contains no secret.
- verification method: Canonical record validation, exact field set, record digest, owner/mode/readback.
- rollback or fail-closed action: Preserve record on ambiguity; do not start; root-reviewed cancellation only.
- automatic-rollback boundary: `NO`; current lifecycle has no proven production cancellation-to-empty operation.
- sensitive-data classification: `NON_SECRET_LIFECYCLE_METADATA`.
- Owner confirmation requirement: `YES` already required at activation hold.
- durable evidence produced: Pending-record digest and previous-record binding.

### M124A-14

- step ID: `M124A-14`
- phase: `PHASE 5 — BOUNDED ACTIVATION`
- exact action: Request one fixed systemd daemon reload for the exact four-unit bundle.
- mutation or read-only classification: `MUTATION`
- executing authority/principal: Root transaction executor through the fixed systemd manager boundary.
- exact target: systemd manager unit graph; no shell or caller-selected unit set.
- expected previous state: Unit files and pending record published; selected OAS units inactive.
- required preconditions: Exact unit readback, generation gate, activation record, and manager boundary pass.
- resulting state: `MANAGER_RELOADED` or rejected.
- postcondition: Manager accepts only the exact unit syntax and conditions; no socket or service is started by reload.
- verification method: Fixed manager API result, unit properties, and no listener/process delta.
- rollback or fail-closed action: Stop transaction; reload alone is not reversed; later state must be reviewed.
- automatic-rollback boundary: `NO`; daemon-reload has no proven inverse.
- sensitive-data classification: `PUBLIC_MANAGER_METADATA`.
- Owner confirmation requirement: `NO`; reload is not activation.
- durable evidence produced: Manager reload result and unit-property digest.

### M124A-15

- step ID: `M124A-15`
- phase: `PHASE 5 — BOUNDED ACTIVATION`
- exact action: Switch `/opt/aether/current` to the verified relative candidate release link.
- mutation or read-only classification: `MUTATION`
- executing authority/principal: Root transaction executor.
- exact target: `/opt/aether/current`.
- expected previous state: `current` absent for first install; candidate release immutable and verified.
- required preconditions: Activation record pending; boot and monotonic window valid; Owner activation evidence still valid; generation gate exists.
- resulting state: `CURRENT_CANDIDATE_LINKED` and record remains uncommitted.
- postcondition: Link is root-owned, relative, points only to the packet release, and no commit claim is made.
- verification method: `lstat`, readlink target, release identity, record identity, and parent fsync.
- rollback or fail-closed action: Stop before socket start; remove exact first-install link or enter root-reviewed rollback; never infer commit.
- automatic-rollback boundary: `NO`; current API can create the link but not prove safe production removal after all later failures.
- sensitive-data classification: `NON_SECRET_RELEASE_ID`.
- Owner confirmation requirement: `YES`; final activation digest must remain covered by Owner evidence.
- durable evidence produced: Current-link publication and activation-window record.

### M124A-16

- step ID: `M124A-16`
- phase: `PHASE 5 — BOUNDED ACTIVATION`
- exact action: Start only the three ordered AF_UNIX socket units through systemd; never substitute IP listeners or direct OAS binding.
- mutation or read-only classification: `MUTATION`
- executing authority/principal: Root transaction executor requests; systemd owns socket creation; OAS does not bind paths.
- exact target: `/run/aether/oas/runtime.sock`, `/run/aether/oas/bootstrap.sock`, `/run/aether/oas/broker.sock`.
- expected previous state: No selected OAS sockets, service, process, or listener.
- required preconditions: Current link, record, generation, exact units, manager state, and boot window pass.
- resulting state: `SOCKETS_ACTIVE` or fail closed.
- postcondition: FD 3/4/5 order, names, path, type, owner/group/mode, and AF_UNIX restriction are exact.
- verification method: Systemd state, socket metadata, `/proc/net/unix`, descriptor intake, and no IP-listener check.
- rollback or fail-closed action: Stop all three sockets in one manager transaction; retain socket/process evidence; ambiguity requires review.
- automatic-rollback boundary: `NO`; current API has no complete live manager rollback proof.
- sensitive-data classification: `NON_SECRET_SOCKET_METADATA`.
- Owner confirmation requirement: `YES`.
- durable evidence produced: Socket activation result and ordered endpoint digest.

### M124A-17

- step ID: `M124A-17`
- phase: `PHASE 5 — BOUNDED ACTIVATION`
- exact action: Admit the `aether-oas` service and require exact readiness evidence before any smoke or commit decision.
- mutation or read-only classification: `MUTATION`
- executing authority/principal: Systemd starts `aether-oas`; root observes; OAS can report only its bounded readiness result.
- exact target: `aether-oas.service`, `/opt/aether/current`, `/var/lib/aether/oas/security_kernel.sqlite3`, and activated descriptors.
- expected previous state: Exact sockets active; service absent or inactive; activation record pending; commit state uncommitted.
- required preconditions: Bounded deadline valid; service principal, runtime import root, state schema, systemd security policy, peer checks, and socket identities pass.
- resulting state: `READY` or `READINESS_FAILED`.
- postcondition: Native `READY=1` occurs only after descriptor, principal, sandbox, schema, manifest, unit, and state checks pass.
- verification method: `READY=1`, effective systemd properties, process UID/GID, import-path probe, SQLite integrity/schema, no IP listener.
- rollback or fail-closed action: Stop service and sockets; preserve readiness failure evidence; do not commit or claim deployment verification.
- automatic-rollback boundary: `NO`; readiness failure can leave durable partial objects and current API lacks complete reverse cleanup.
- sensitive-data classification: `NON_SECRET_READINESS_AND_STATE_DIGESTS`.
- Owner confirmation requirement: `YES`; readiness is not Owner activation authority.
- durable evidence produced: Readiness result, process/socket observations, and state digest.

### M124A-18

- step ID: `M124A-18`
- phase: `PHASE 7 — COMMIT OR FAIL CLOSED` then `PHASE 8 — REPORT`
- exact action: Run the bounded smoke verification; commit only if readiness and smoke pass inside the valid window; then perform post-commit verification, evidence closure, and lock release.
- mutation or read-only classification: `MUTATION` followed by `READ_ONLY`
- executing authority/principal: Root transaction executor performs the lifecycle transition; Owner does not delegate future scope; Project Manager reviews evidence afterward.
- exact target: Activation record, OAS bounded smoke operation, current link, unit/generation gate, process/socket/state observations, and evidence store.
- expected previous state: `ACTIVATING`, current points to candidate, commit state `UNCOMMITTED`, readiness `PASSED`, smoke not yet run.
- required preconditions: M124A-17 readiness passed; Owner activation confirmation covers the final digest; smoke is exact and local; deadline and boot match.
- resulting state: `COMMITTED` only after all postconditions, otherwise `ROLLBACK_PENDING`, `RECOVERY_REQUIRED`, or `FAILED_CLOSED`.
- postcondition: Commit record, current link, unit generation, state, audit continuity, service, sockets, and evidence agree; report distinguishes every lifecycle state.
- verification method: Lifecycle transition guard, smoke result, record/link/unit/state rehash, process/socket/systemd observation, unexpected-mutation snapshot, evidence closure.
- rollback or fail-closed action: Never convert failure to completion; stop/restore only identities proven safe, otherwise retain all evidence for manual privileged review.
- automatic-rollback boundary: `NO`; current implementation cannot prove rollback to `NOT_DEPLOYED` for every later interruption.
- sensitive-data classification: `NON_SECRET_RESULT_AND_DIGESTS`.
- Owner confirmation requirement: `YES` before activation/commit; PM review is separate and post-evidence.
- durable evidence produced: Smoke, commit-or-failure, postcondition, rollback/recovery, and closure records.

Trust-bootstrap provisioning is intentionally absent from the mutation list. It
is a separately authorized prerequisite under M121A. A candidate-controlled
step for anchor or verifier installation would invalidate this manifest.

## 7. Exact Phase Model

### PHASE 0 — OWNER AUTHORIZATION

The exact packet, mutation digest, rollback digest, target digest, boot digest,
source, trust identity, profile, expiry, and one-use scope must be reviewed by
the Owner. Project Manager approval of milestone scope is separate and cannot
substitute for the Owner. No mutation occurs.

### PHASE 1 — READ-ONLY REVALIDATION

Root rechecks target and boot identity, expiry, replay, source/tag/hash,
production trust availability, installed trust prerequisites, empty state, and
conflicting objects. Any mismatch invalidates the authorization. The lock is
transaction serialization, not Owner authority.

### PHASE 2 — INACTIVE STAGING

Only packet-bound isolated staging and candidate copying are permitted. No
socket or service starts, no live current link is created, and no `COMMITTED`
claim is possible.

### PHASE 3 — PRE-ACTIVATION VERIFICATION HOLD POINT

Before activation, the root executor must verify production signature, anchor
and fingerprint, fixed verifier, dependency closure, installed file hashes,
ownership and modes, exact units, effective systemd security properties,
AF_UNIX-only restriction, absence of IP listeners, initial empty state, exact
initial schema, and durable trust evidence before pending state. This is a
hold point, not an activation permission.

### PHASE 4 — EXPLICIT ACTIVATION AUTHORITY

The safe current rule requires a second exact Owner confirmation over the final
Phase 3 digest. The original packet explicitly covers the final Phase 3 digest
only if the frozen authority architecture proves that its one-use evidence
explicitly covers that final digest and cannot be expanded. Root, systemd, OAS,
Project Manager, and the candidate cannot self-confirm. No truthful live Owner
source currently produces this evidence, so activation is blocked.

### PHASE 5 — BOUNDED ACTIVATION

Only the ordered local sockets and the bounded service readiness path may run.
The activation window is boot-bound and monotonic, readiness is required, and
no direct commit is permitted.

### PHASE 6 — OBSERVATION AND VERIFICATION

Observe process principal, socket ownership/modes, effective systemd policy,
AF_UNIX-only endpoints, readiness, smoke result, database identity/integrity,
audit continuity, exact record/link/unit bindings, and unexpected mutations.
Test verification and readiness are not deployment verification.

### PHASE 7 — COMMIT OR FAIL CLOSED

Commit only after all required evidence and Owner authority pass. A failure
does not become completion. If safe removal cannot be proven, retain evidence
and require manual privileged review; do not relabel that state `NOT_DEPLOYED`.

### PHASE 8 — REPORT

The report distinguishes `AUTHORIZED`, `STAGED`, `ACTIVATED`, `OBSERVED`,
`VERIFIED`, `COMMITTED`, `ROLLED_BACK`, `FAILED_CLOSED`, and
`DEPLOYMENT_VERIFIED`. A static or isolated test result never becomes a live
deployment result.

## 8. Rollback Proof Matrix

The required terminal objective is a genuinely empty, reviewed first-install
namespace with `DEPLOYMENT_STATE: NOT_DEPLOYED`. The current finalized
implementation exposes isolated-root installation and logical lifecycle
transitions, but no complete production inverse for principals, directories,
units, manager state, sockets, current link, release, activation record, and
OAS state as one transaction. Consequently the global result is:

```text
ROLLBACK_TO_NOT_DEPLOYED_PROVEN: NO
```

`FAILED_CLOSED` means that no further unauthorized action occurs. It does not
prove `NOT_DEPLOYED`. Manual privileged review is disposition evidence only;
it is not automatic rollback proof.

### Rollback window: before packet consumption

- starting state: `NO_DEPLOYMENT`; packet unconsumed.
- objects that may exist: read-only observation artifacts only.
- exact durable evidence: target observation digest and no-mutation snapshot.
- automatic rollback available: `NO`; no rollback is needed.
- implementation/API supporting automatic rollback: none; rejection is read-only.
- exact safe removal sequence: remove no target object; discard process-local packet view.
- identity and unchanged-object checks: repeat M123A bounded path, principal, unit, socket, listener, and process snapshot.
- evidence that must be retained: rejection reason, packet digest, observation digest.
- manual privileged review requirement: `NO` if the unchanged snapshot is complete.
- terminal state: `FAILED_CLOSED`, target remains `NOT_DEPLOYED`.
- whether NOT_DEPLOYED is actually proven: `YES`, by unchanged read-only snapshot only.
- forbidden success claim: authorization, staging, activation, commit, or deployment verification.

### Rollback window: after packet consumption but before mutation

- starting state: packet consumed in replay state; target still `NO_DEPLOYMENT`.
- objects that may exist: replay/consumption evidence only.
- exact durable evidence: consumed packet digest, nonce, sequence, and unchanged target snapshot.
- automatic rollback available: `NO`; replay consumption is not deployment rollback.
- implementation/API supporting automatic rollback: no production packet-consumption API exists.
- exact safe removal sequence: do not reuse packet; invalidate consumed authorization; remove no target object.
- identity and unchanged-object checks: compare every selected target path and manager observation to Phase 1.
- evidence that must be retained: consumed packet and invalidation records.
- manual privileged review requirement: `NO` only when the unchanged snapshot is complete.
- terminal state: `FAILED_CLOSED`; target remains un-deployed.
- whether NOT_DEPLOYED is actually proven: `YES` only for the unchanged target snapshot, not global rollback proof.
- forbidden success claim: consumed authorization equals activation or deployment.

### Rollback window: inactive staging

- starting state: `STAGING_CREATED` or `CANDIDATE_STAGED`; target namespace unchanged.
- objects that may exist: isolated `/var/lib/aether/install/<tx>` staging.
- exact durable evidence: staging inventory, transaction identity, and pre-target snapshot.
- automatic rollback available: `NO`; current cleanup is isolated-root scoped.
- implementation/API supporting automatic rollback: `RepositoryInstaller.stage_release` in an explicit temporary root only; no production inverse.
- exact safe removal sequence: verify transaction path, owner, type, and inventory; remove staging children, fsync parent, then remove empty transaction directory.
- identity and unchanged-object checks: verify no target release, unit, record, link, principal, socket, process, or manager delta.
- evidence that must be retained: staging removal result and unchanged target snapshot.
- manual privileged review requirement: `YES` if any staging identity or target snapshot is ambiguous.
- terminal state: `FAILED_CLOSED` or `RECOVERY_REQUIRED`.
- whether NOT_DEPLOYED is actually proven: `YES` only after complete unchanged target observation; not a general rollback proof.
- forbidden success claim: candidate trust, activation, or deployment verification.

### Rollback window: trust evidence before pending

- starting state: trust verified; `CANDIDATE_PENDING` not written.
- objects that may exist: durable transaction trust evidence and verifier staging.
- exact durable evidence: immutable evidence file with transaction, release, anchor, verifier, dependency, and unit identities.
- automatic rollback available: `NO`; evidence is immutable and no production cancellation inverse is exposed.
- implementation/API supporting automatic rollback: `verify_candidate_before_pending` writes evidence but does not provide complete target cleanup.
- exact safe removal sequence: retain evidence for identical retry; any cleanup requires root review, identity check, unlink, and parent fsync.
- identity and unchanged-object checks: confirm no activation record, current link, live unit, socket, process, or state database was created.
- evidence that must be retained: immutable trust evidence and failure/cleanup decision.
- manual privileged review requirement: `YES` for cleanup or conflicting evidence.
- terminal state: `FAILED_CLOSED` with durable partial evidence or `RECOVERY_REQUIRED`.
- whether NOT_DEPLOYED is actually proven: `NO`; fail closed is not equivalent to empty deployment state.
- forbidden success claim: pending, activation, or `NOT_DEPLOYED` rollback proof.

### Rollback window: principal creation

- starting state: `NAMESPACE_EMPTY` before principal mutation.
- objects that may exist: one or more fixed users/groups, possibly partially created.
- exact durable evidence: per-principal creation result, exact IDs, group membership, shell, home, and prior absence.
- automatic rollback available: `NO`; no safe production principal deprovisioning API is implemented.
- implementation/API supporting automatic rollback: none; M119A defines principals but current code does not provision them.
- exact safe removal sequence: stop all transaction work; enumerate exact created identities; do not delete if any mismatch, reuse, login, or external membership exists; root review required.
- identity and unchanged-object checks: compare name, UID, GID, home, shell, groups, processes, and unrelated account database entries.
- evidence that must be retained: account database before/after digests and root review record.
- manual privileged review requirement: `YES`.
- terminal state: `RECOVERY_REQUIRED` or reviewed `FAILED_CLOSED` with partial principals.
- whether NOT_DEPLOYED is actually proven: `NO`.
- forbidden success claim: empty namespace, deployment verification, or automatic rollback.

### Rollback window: directory creation

- starting state: required target parents absent except approved host parents.
- objects that may exist: some fixed directories and mode/ownership changes.
- exact durable evidence: per-path type, owner, group, mode, parent, and creation digest.
- automatic rollback available: `NO`; no complete production directory inverse is implemented.
- implementation/API supporting automatic rollback: isolated-root directory primitives only; no target-host transaction executor.
- exact safe removal sequence: remove only exact empty transaction-created children in reverse order; never remove preexisting parents; fsync every parent.
- identity and unchanged-object checks: `lstat`, direct-child inventory, mount, symlink, link-count, and owner/mode comparison.
- evidence that must be retained: before/after path snapshots and removal result.
- manual privileged review requirement: `YES` for any non-empty, changed, or ambiguous path.
- terminal state: `RECOVERY_REQUIRED` or partial namespace requiring review.
- whether NOT_DEPLOYED is actually proven: `NO`.
- forbidden success claim: fail closed equals empty target.

### Rollback window: release publication

- starting state: candidate release staged and release ID absent from `/opt/aether/releases`.
- objects that may exist: immutable candidate release directory.
- exact durable evidence: release inventory, release ID, manifest digest, parent fsync, and reference scan.
- automatic rollback available: `NO`; current installer publication is not a production inverse contract.
- implementation/API supporting automatic rollback: `RepositoryInstaller.stage_release` only under an explicit isolated root.
- exact safe removal sequence: stop activation; verify release is unreferenced and exact; remove release tree; fsync release parent; otherwise stop.
- identity and unchanged-object checks: release hash/inventory, current link, record, units, sockets, processes, and state.
- evidence that must be retained: release removal or hold decision and all identity checks.
- manual privileged review requirement: `YES` unless exact unreferenced cleanup is proven by a separately implemented executor.
- terminal state: partial release retained or `RECOVERY_REQUIRED`.
- whether NOT_DEPLOYED is actually proven: `NO` under current implementation.
- forbidden success claim: current active, committed, or deployment-verified release.

### Rollback window: unit publication

- starting state: no selected target units and no active OAS manager transaction.
- objects that may exist: zero to four unit files, possibly mixed.
- exact durable evidence: each file hash, owner, mode, generation reference, and prior absence.
- automatic rollback available: `NO`; four-file replacement is not filesystem-atomic.
- implementation/API supporting automatic rollback: `replace_unit_bundle` supports isolated-root publication only and has no complete production inverse.
- exact safe removal sequence: stop admission; stop any selected units; verify all four identities; remove exact first-install files or restore exact previous bundle; reload manager only after consistency.
- identity and unchanged-object checks: file bytes, generation gate, manager state, jobs, sockets, process, and cgroup checks.
- evidence that must be retained: mixed-state inventory, stop result, and restoration/removal result.
- manual privileged review requirement: `YES` for mixed or unknown state.
- terminal state: `RECOVERY_REQUIRED` or partial unit state.
- whether NOT_DEPLOYED is actually proven: `NO`.
- forbidden success claim: unit presence equals active deployment.

### Rollback window: generation gate

- starting state: candidate units verified; candidate gate absent.
- objects that may exist: candidate `.ready` gate, possibly with unit mismatch.
- exact durable evidence: canonical gate payload, transaction ID, generation, and unit hashes.
- automatic rollback available: `NO`; gate installation has no whole-transaction inverse.
- implementation/API supporting automatic rollback: `install_generation_gate` only operates under an explicit isolated root.
- exact safe removal sequence: verify gate unreferenced and exact; unlink and fsync generation directory; if units differ, hold.
- identity and unchanged-object checks: all unit conditions, gate contents, manager state, and listener/process observations.
- evidence that must be retained: gate removal/hold result and generation mismatch evidence.
- manual privileged review requirement: `YES` on any mismatch.
- terminal state: `RECOVERY_REQUIRED` or partial activation artifacts.
- whether NOT_DEPLOYED is actually proven: `NO`.
- forbidden success claim: generation gate equals readiness or commit.

### Rollback window: daemon reload

- starting state: published units/gate and no OAS socket or service start.
- objects that may exist: manager has reloaded unit definitions; no required live endpoint.
- exact durable evidence: reload result, effective unit properties, manager state, and no listener/process delta.
- automatic rollback available: `NO`; daemon reload has no inverse operation in the current API.
- implementation/API supporting automatic rollback: systemd manager only; no transaction-level reverse proof.
- exact safe removal sequence: do not claim reversal; stop transaction, restore/remove exact units if separately proven, then reload after consistency.
- identity and unchanged-object checks: manager unit graph, jobs, file identities, sockets, processes, and cgroups.
- evidence that must be retained: manager result and all observations.
- manual privileged review requirement: `YES` if any job or unit state is unexpected.
- terminal state: `FAILED_CLOSED` or `RECOVERY_REQUIRED`.
- whether NOT_DEPLOYED is actually proven: `NO`; manager reload is not state rollback.
- forbidden success claim: reload equals activation or deployment.

### Rollback window: pending activation record

- starting state: candidate release/units/gate published; no current link or service.
- objects that may exist: root-owned `CANDIDATE_PENDING` record and trust evidence.
- exact durable evidence: canonical record, record digest, previous-record digest, and trust evidence.
- automatic rollback available: `NO`; lifecycle API has no complete production cancel-to-empty transition.
- implementation/API supporting automatic rollback: `write_record` and `transition` support bounded records, not whole-host rollback.
- exact safe removal sequence: do not start; preserve record; root-reviewed cancellation may remove only exact unreferenced outputs after all checks.
- identity and unchanged-object checks: record, release, units, gate, link, sockets, process, state, and principals.
- evidence that must be retained: pending record and cancellation/recovery disposition.
- manual privileged review requirement: `YES`.
- terminal state: `CANDIDATE_PENDING`, `RECOVERY_REQUIRED`, or partial first-install state.
- whether NOT_DEPLOYED is actually proven: `NO`.
- forbidden success claim: pending equals active, verified, or committed.

### Rollback window: current-link switch

- starting state: pending record; `current` absent; no service/socket active.
- objects that may exist: candidate `current` relative symlink.
- exact durable evidence: link target, record binding, parent fsync, boot, and expiry.
- automatic rollback available: `NO`; `activate_current` has no complete production inverse.
- implementation/API supporting automatic rollback: `RepositoryInstaller.activate_current` only in isolated roots.
- exact safe removal sequence: stop any activation; verify link exactly points to candidate; unlink first-install link and fsync parent; otherwise retain and review.
- identity and unchanged-object checks: link, release, record, unit/gate, sockets, process, and state.
- evidence that must be retained: link removal/hold result and activation-window evidence.
- manual privileged review requirement: `YES` after any manager or process interaction.
- terminal state: `ROLLBACK_PENDING` or `RECOVERY_REQUIRED`.
- whether NOT_DEPLOYED is actually proven: `NO`.
- forbidden success claim: current link equals commit or deployment verification.

### Rollback window: socket activation

- starting state: candidate current link and pending record; sockets inactive.
- objects that may exist: one to three socket endpoints and manager jobs.
- exact durable evidence: endpoint type/path/owner/group/mode/inode, FD order, manager jobs, and listener snapshot.
- automatic rollback available: `NO`; no complete manager/socket inverse is proven by current implementation.
- implementation/API supporting automatic rollback: systemd socket units and M120A stop semantics; not a first-install rollback proof.
- exact safe removal sequence: stop all three sockets in one transaction; verify no endpoints/listeners/jobs remain; clean only exact transaction objects.
- identity and unchanged-object checks: `/proc/net/unix`, socket metadata, manager state, process/cgroup state, and target paths.
- evidence that must be retained: stop result and endpoint/process evidence.
- manual privileged review requirement: `YES` on partial stop or unknown endpoint.
- terminal state: `ROLLBACK_PENDING` or `RECOVERY_REQUIRED`.
- whether NOT_DEPLOYED is actually proven: `NO`.
- forbidden success claim: socket existence equals OAS readiness or commit.

### Rollback window: service start before readiness

- starting state: sockets active; service not ready; record uncommitted.
- objects that may exist: OAS process, cgroup, SQLite state, journal entries, sockets.
- exact durable evidence: process UID/GID, service state, readiness result, state integrity/schema, socket evidence.
- automatic rollback available: `NO`; current API cannot reverse arbitrary service/state side effects.
- implementation/API supporting automatic rollback: M120A bounded shutdown and M122A lifecycle guards; no complete production inverse.
- exact safe removal sequence: stop service and sockets; wait bounded shutdown; verify no process/job/worker; preserve state and evidence; root review.
- identity and unchanged-object checks: process, cgroup, sockets, state/WAL/SHM, record, link, units, and audit continuity.
- evidence that must be retained: startup failure and all durable state observations.
- manual privileged review requirement: `YES`.
- terminal state: `RECOVERY_REQUIRED` or partial first-install state.
- whether NOT_DEPLOYED is actually proven: `NO`.
- forbidden success claim: process start or `READY=1` absent means empty deployment.

### Rollback window: readiness before smoke

- starting state: `ACTIVATING`; readiness passed; smoke not run; commit uncommitted.
- objects that may exist: active service, sockets, current link, activation record, initial OAS state.
- exact durable evidence: readiness evidence and activation record digest.
- automatic rollback available: `NO`; readiness has no automatic empty-state inverse.
- implementation/API supporting automatic rollback: `transition` blocks direct commit but does not remove host objects.
- exact safe removal sequence: do not commit; stop service/sockets; verify all identities; root-reviewed cleanup or recovery.
- identity and unchanged-object checks: record, link, units, sockets, service, state, audit, and target snapshot.
- evidence that must be retained: readiness evidence, stop result, and cleanup/recovery decision.
- manual privileged review requirement: `YES`.
- terminal state: `ROLLBACK_PENDING` or `RECOVERY_REQUIRED`.
- whether NOT_DEPLOYED is actually proven: `NO`.
- forbidden success claim: readiness equals smoke, commit, or deployment verification.

### Rollback window: smoke before commit

- starting state: readiness passed; smoke running or result unresolved; commit uncommitted.
- objects that may exist: all activation objects and bounded smoke side effects.
- exact durable evidence: smoke request/result digest, record, process, socket, state, and audit observations.
- automatic rollback available: `NO`; no complete smoke-side-effect inverse is implemented.
- implementation/API supporting automatic rollback: lifecycle transition requires smoke pass for commit but does not prove cleanup.
- exact safe removal sequence: stop before commit; preserve smoke evidence; remove only proven transaction objects; hold on unknown side effect.
- identity and unchanged-object checks: smoke scope/result, current link, record, unit/gate, service, sockets, database, and audit.
- evidence that must be retained: smoke result and all failure/cleanup evidence.
- manual privileged review requirement: `YES` on unresolved result or side effect.
- terminal state: `ROLLBACK_PENDING` or `RECOVERY_REQUIRED`.
- whether NOT_DEPLOYED is actually proven: `NO`.
- forbidden success claim: smoke pass or absent response equals commit.

### Rollback window: commit before postcondition closure

- starting state: `COMMITTED` record written; post-commit checks incomplete.
- objects that may exist: complete candidate deployment and committed activation record.
- exact durable evidence: committed record, current link, unit/gate, readiness/smoke, and transaction evidence.
- automatic rollback available: `NO`; commit is durable and no safe automatic first-install inverse exists.
- implementation/API supporting automatic rollback: `transition(..., COMMITTED)` only; no production rollback executor.
- exact safe removal sequence: preserve committed evidence; stop services only through root review; do not rewrite history or delete ambiguous state.
- identity and unchanged-object checks: every committed object plus post-commit manager/process/socket/state evidence.
- evidence that must be retained: committed record and mismatch evidence.
- manual privileged review requirement: `YES`.
- terminal state: `COMMITTED_WITH_VERIFICATION_GAP` or `RECOVERY_REQUIRED`.
- whether NOT_DEPLOYED is actually proven: `NO`.
- forbidden success claim: committed equals deployment verified.

### Rollback window: host reboot

- starting state: any pending or activating first-install transaction.
- objects that may exist: durable record, release, units, gate, current link, state, or principals.
- exact durable evidence: pre-reboot transaction record, boot binding, object inventory, and post-reboot observations.
- automatic rollback available: `NO`; boot change invalidates the activation window but does not remove durable state.
- implementation/API supporting automatic rollback: `ActivationWindow` rejects wrong boot; no cleanup inverse.
- exact safe removal sequence: do not auto-start candidate; verify boot mismatch; preserve evidence; root reviews removal or recovery.
- identity and unchanged-object checks: boot digest, record, current link, units/gate, sockets, processes, state, and manager jobs.
- evidence that must be retained: pre/post reboot observation and boot mismatch.
- manual privileged review requirement: `YES`.
- terminal state: `RECOVERY_REQUIRED` or partial durable state.
- whether NOT_DEPLOYED is actually proven: `NO`.
- forbidden success claim: boot rejection equals rollback to empty.

### Rollback window: executor crash

- starting state: any manifest step in progress.
- objects that may exist: any prefix of the ordered mutation manifest.
- exact durable evidence: last durable step record, lock state, object inventory, manager/process/socket state.
- automatic rollback available: `NO`; no journaled production inverse exists.
- implementation/API supporting automatic rollback: isolated-root fsync primitives and lifecycle records only.
- exact safe removal sequence: reacquire root review lock; identify last durable step; verify every object; remove/restore only exact identities; otherwise recovery.
- identity and unchanged-object checks: all manifest targets, transaction IDs, hashes, owners, modes, manager jobs, processes, sockets, and state.
- evidence that must be retained: crash boundary and all before/after observations.
- manual privileged review requirement: `YES`.
- terminal state: `RECOVERY_REQUIRED` unless a separately proven prefix cleanup exists.
- whether NOT_DEPLOYED is actually proven: `NO`.
- forbidden success claim: crash absence or process exit equals rollback.

### Rollback window: lost controlling session

- starting state: Owner authorization or activation hold in progress.
- objects that may exist: any mutation prefix already durable; no valid interactive confirmation.
- exact durable evidence: authorization consumption, session/nonce state, last step, and target snapshot.
- automatic rollback available: `NO`; lost session revokes intent but cannot reverse host mutations.
- implementation/API supporting automatic rollback: none; M117A local authority source is not implemented.
- exact safe removal sequence: invalidate unused authorization; stop new work; review durable prefix and clean only exact safe objects.
- identity and unchanged-object checks: packet nonce, Owner record, target objects, manager/process/socket/state evidence.
- evidence that must be retained: lost-session event, nonce state, and all mutation evidence.
- manual privileged review requirement: `YES` if any mutation began.
- terminal state: `FAILED_CLOSED` or `RECOVERY_REQUIRED`.
- whether NOT_DEPLOYED is actually proven: `NO` after any mutation prefix.
- forbidden success claim: root continuation or session loss equals Owner approval.

### Rollback window: authorization expiry

- starting state: packet or activation window unexpired before boundary.
- objects that may exist: any staged or partial activation output.
- exact durable evidence: issued/expiry monotonic values, boot identity, last step, and object inventory.
- automatic rollback available: `NO`; expiry blocks future action but does not erase durable output.
- implementation/API supporting automatic rollback: `ActivationWindow.valid` and lifecycle guards reject expiry; no whole-host inverse.
- exact safe removal sequence: stop activation; never extend deadline; preserve evidence; root reviews exact cleanup or recovery.
- identity and unchanged-object checks: monotonic window, boot, packet digest, record, link, units, sockets, process, and state.
- evidence that must be retained: expiry result and post-expiry observation.
- manual privileged review requirement: `YES` after any mutation.
- terminal state: `FAILED_CLOSED` or `RECOVERY_REQUIRED`.
- whether NOT_DEPLOYED is actually proven: `NO` after any durable prefix.
- forbidden success claim: expiry rejection equals empty target.

### Rollback window: rollback failure

- starting state: `ROLLBACK_PENDING` with removal or restoration attempted.
- objects that may exist: candidate and partial old/empty namespace objects.
- exact durable evidence: rollback step results, identity comparisons, current record, link, units, manager, sockets, process, and state.
- automatic rollback available: `NO`; a failed rollback cannot invoke an unproven second rollback.
- implementation/API supporting automatic rollback: lifecycle has a logical `ROLLBACK_PENDING` state; no complete production inverse.
- exact safe removal sequence: stop all further activation; preserve every object; do not retry guessed operations; manual privileged review.
- identity and unchanged-object checks: complete path/object inventory, ownership, hashes, manager state, process/cgroup/socket state, and audit continuity.
- evidence that must be retained: failed rollback record and all attempted actions.
- manual privileged review requirement: `YES`.
- terminal state: `RECOVERY_REQUIRED`.
- whether NOT_DEPLOYED is actually proven: `NO`.
- forbidden success claim: fail-closed rollback equals `NOT_DEPLOYED`.

### Rollback window: post-commit mismatch

- starting state: `COMMITTED`; post-commit verification finds a mismatched object or policy.
- objects that may exist: full candidate deployment plus unexpected or changed state.
- exact durable evidence: committed record, mismatch object identity, manager/process/socket/state observations, and verifier result.
- automatic rollback available: `NO`; post-commit correction is not a first-install inverse proof.
- implementation/API supporting automatic rollback: no production rollback executor; retained-release rollback policy is M121A design only.
- exact safe removal sequence: do not erase evidence; stop only through root review; validate release/approval policy before any restoration.
- identity and unchanged-object checks: all committed identities, expected policy, audit continuity, and unexpected-mutation snapshot.
- evidence that must be retained: mismatch report, committed evidence, and review decision.
- manual privileged review requirement: `YES`.
- terminal state: `DEPLOYMENT_VERIFICATION_FAILED` or `RECOVERY_REQUIRED`.
- whether NOT_DEPLOYED is actually proven: `NO`.
- forbidden success claim: committed or test-verified equals deployment verified or rolled back.

## 9. Current Discovery and Exit

The host observation remains compatible with the bounded AF_UNIX profile and
the expected first-install namespace is absent. That does not close the
production trust, Owner authorization, or rollback-proof gates. The installed
trust objects are absent, but global production trust-material availability is
not claimed absent. No production-signed candidate, separate trust-bootstrap
authorization, truthful Owner deployment authorization source, or truthful
Owner activation-confirmation source was directly proven.

The architecture is viable enough to define the transaction, but required
trust, Owner-authority, and rollback proof is missing. The only authorized
M124A exit that fits is:

```text
EXIT_B_PREREQUISITES_OR_RECOVERY_GAPS_REQUIRE_CORRECTION
```

This is not the obsolete M123A host-readiness exit. It does not authorize
trust provisioning, Build, deployment, mutation, activation, upgrade,
migration, adoption, recovery, rollback, public exposure, or a successor.

## 10. Authoritative Status

The static lock extracts exactly the single block between the markers, parses
each non-marker line as one `KEY: VALUE` entry, rejects duplicate or unknown
keys, rejects duplicate markers and obsolete aliases, and compares the complete
mapping to the canonical schema.

```text
AUTHORITATIVE_M124A_STATUS_BEGIN
M124A_AUTHORIZED: YES
M124A_STARTED: YES
M124A_FINALIZED: YES
M124A_TYPE: DESIGN_DISCOVERY_SECURITY_AND_OPERATIONS_CONTRACT_PROOF
DECISION_STATUS: CURRENT
DESIGN_STATUS: PARTIAL
IMPLEMENTATION_STATUS: NOT_IMPLEMENTED
VERIFICATION_STATUS: TEST_VERIFIED
DEPLOYMENT_VERIFIED: NO
DEPLOYMENT_STATE: NOT_DEPLOYED
DEPLOYMENT_PROFILE: FIRST_INSTALL_LOCAL_AF_UNIX_ONLY
DEPLOYMENT_TRANSACTION_DEFINED: YES
PRODUCTION_TRUST_MATERIAL_PROVEN: NO
ROLLBACK_TO_NOT_DEPLOYED_PROVEN: NO
TARGET_READY_FOR_EXPLICIT_OWNER_DEPLOYMENT_AUTHORIZATION_REVIEW: NO
SELECTED_EXIT: EXIT_B_PREREQUISITES_OR_RECOVERY_GAPS_REQUIRE_CORRECTION
LIVE_DEPLOYMENT_AUTHORIZED: NO
TARGET_HOST_MUTATION_PERFORMED: NO
UPGRADE_AUTHORIZED: NO
SCHEMA_MIGRATION_AUTHORIZED: NO
PUBLIC_EXPOSURE_AUTHORIZED: NO
ADOPTION_AUTHORIZED: NO
AUTOMATED_RECOVERY_AUTHORIZED: NO
GENERIC_ACT_AUTHORIZED: NO
PROGRESS_UPDATED: YES
COMMIT_CREATED: YES
TAG_CREATED: YES
PUSH_PERFORMED: YES
SUCCESSOR_AUTHORIZED: NO
SUCCESSOR_NUMBER_ASSIGNED: NO
READY_FOR_PM_REVIEW: NO
AUTHORITATIVE_M124A_STATUS_END
```

The status records PM-authorized finalization of a negative-gated design and
security proof. It does not authorize trust bootstrap, implementation, live
deployment, host mutation, or a successor milestone. No successor number is
assigned.
