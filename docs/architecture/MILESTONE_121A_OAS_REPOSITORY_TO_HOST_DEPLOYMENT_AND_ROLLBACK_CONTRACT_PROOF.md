# M121A OAS Repository-to-Host Deployment and Rollback Contract Proof

Document role: DESIGN / DISCOVERY / CORRECTIVE REPOSITORY-TO-HOST CONTRACT PROOF ONLY

PM disposition: `RETURN_M121A_FOR_SECOND_CORRECTION`

This corrective pass remains inside M121A. It does not begin M121B, M122, a
Build, deployment, host mutation, commit, tag, push, or a successor milestone.
The record is subordinate to the Constitution, overall Architecture, and
canonical Security Architecture. Milestone records remain immutable historical
evidence and are not another authority layer.

## 1. Authority, Scope, and Correction

The authority precedence is exact:

```text
CONSTITUTION
    >
ARCHITECTURE
    >
SECURITY_ARCHITECTURE
    >
CURRENT IMPLEMENTATION
```

Aether is one persistent digital mind. AetherOS is its operating environment
and body. OAS is a bounded authority service, not another mind, agent, or
cognitive runtime. The preserved security boundaries are:

```text
AUTHENTICATION != INTENT_INTERPRETATION
GOAL_ACCEPTANCE != ACTION_AUTHORIZATION
ACTION_SUCCESS != COMPLETION
COMPLETION REQUIRES OBSERVATION + VERIFICATION
```

M118A established the bounded durable SQLite OAS security-kernel foundation.
M119A selected the separate-principal and restricted-IPC architecture as design
proof. M120A implemented the bounded IPC and service foundation at:

```text
M120A_COMMIT: a5fcfeafafcabf26a5b4ceef6485817fe87f7887
M120A_TAG: milestone-120A-oas-socket-activated-service-bounded-ipc-foundation
M120A_TAG_PEELED_TARGET: a5fcfeafafcabf26a5b4ceef6485817fe87f7887
```

The corrected M121A boundary is:

```text
FINALIZED REPOSITORY IMPLEMENTATION
        ->
ROOT-OWNED, VERSIONED, VERIFIABLE, ATOMICALLY ACTIVATABLE,
ROLLBACK-SAFE HOST ARTIFACT CONTRACT
```

The PM correction found seven hard gates that were not closed by the previous
record:

| Gate | Objection | Corrective resolution |
| --- | --- | --- |
| A | `current` was switched before the identity used by startup was committed | One authoritative activation record authorizes a pending candidate; readiness is allowed only in `ACTIVATING`, and commit is a later record transition |
| B | M120A descriptor order was asserted without an explicit systemd supply mechanism | Service `[Service]` `Sockets=` lists the three socket units in exact runtime/bootstrap/broker order; every unit requires the complete set and M120A verifies names and descriptors 3/4/5 |
| C | Four unit files cannot be atomically replaced as one object and Conditions do not stop running units | A bounded quiesce protocol stops admission, all sockets, and OAS, proves cgroup/process/job absence, then invalidates generation gates before individual replacement |
| D | Ed25519 trust-root lifecycle and pre-candidate verification were incomplete | A fixed host verifier using one exact OpenSSL 3.0 `pkeyutl -verify -rawin` argv contract, a carried canonical approval payload, non-self-referential anchor fingerprint, dual-role signatures, rotation, and revocation is specified |
| E | Python environment and `-I` import claims contradicted the unit and real systemd metadata | Protocol inputs are validated exactly; safe manager metadata is ambient non-authority, ignored/cleared before application initialization, and never causes startup failure |
| F | FD limit, restart limit, inaccessible path, and namespace semantics were incomplete | FD arithmetic selects 512; systemd 252 start limits and `StartLimitAction=none` are explicit; `/var/log/aether` is removed; `RestrictNamespaces=yes` is defined as deny-all |
| G | `EXIT_A` lacked a precise future Build inventory | A staged repository Build inventory and separate isolated deployment, target deployment, and PM-review gates are enumerated |

Only these two repository artifacts are in scope for the corrective pass:

```text
docs/architecture/MILESTONE_121A_OAS_REPOSITORY_TO_HOST_DEPLOYMENT_AND_ROLLBACK_CONTRACT_PROOF.md
tests/test_milestone_121a_oas_repository_to_host_deployment_and_rollback_contract_proof.py
```

No existing repository file is modified. `PROGRESS.md`,
`SECURITY_ARCHITECTURE.md`, all historical M117A-M120A artifacts, production
code, dependencies, configuration, deployment files, units, installers,
entrypoints, and Git references remain outside this pass.

## 2. Read-Only Discovery and Current Truth

The corrective discovery was read-only. No host user, group, file, permission,
mount, service, socket, package, credential, secret, token, private key,
password hash, session, or unrelated personal information was changed. No
service was started or stopped and no `sudo` mutation was used.

### 2.1 Repository facts

| Discovery item | Observed fact | Consequence |
| --- | --- | --- |
| Packaging/build system | No `pyproject.toml`, `setup.py`, `setup.cfg`, Makefile, container file, wheel, sdist, or release tool exists | The future Build must define a reproducible release procedure |
| Dependency declaration | `requirements.txt` contains 16 exact direct package versions | Direct pins are only an input inventory |
| Dependency lock | No hashed lock, constraints file, wheelhouse, or package artifact exists | Target installation cannot resolve packages on the host |
| Current environment | `.venv` is ignored local state with Python 3.11.2 and packages beyond `requirements.txt` | Development state cannot be trusted as a release |
| Production OAS entrypoint | No `aether.oas.host_entrypoint` exists | Native readiness and production startup are not implemented |
| Deployment artifacts | No service/socket unit, installer, manifest, release verifier, or rollback tool exists | M121A defines these only as future Build inventory |
| Current configuration | `config/aether.yaml` binds the API to `127.0.0.1:8000` and data to `/home/aether/data` | Development paths are not deployment paths |
| Current path behavior | Configuration searches from `__file__` and `Path.cwd()`; M118A accepts an explicitly supplied SQLite path | Production must use fixed absolute paths |
| Existing OAS boundary | `aether.oas.__all__` is empty; M120A is not wired into the application | This is a static repository boundary, not OS isolation |

The current checkout is not reproducibly deployable. No production dependency
installation is authorized by M121A.

### 2.2 Host facts

| Discovery item | Observed fact | Consequence |
| --- | --- | --- |
| Operating system | Debian GNU/Linux 12, x86_64 | Linux-specific systemd and AF_UNIX contract is applicable |
| Kernel | Linux 6.8.12-20-pve | Linux peer credentials and `/proc/net/unix` evidence are available |
| Service manager | systemd 252.39, PID 1, running | The selected directives and explicit socket ordering are available for later verification |
| Current Python | `/usr/bin/python` and `.venv/bin/python` report Python 3.11.2 | Exact interpreter identity remains a manifest value |
| Development account | `aether`, uid/gid 1000, `/bin/bash`, supplementary `aether`, `sudo`, `users` | It is not a service principal |
| Target principals | `aether-owner`, `aether-runtime`, `aether-oas`, and `aether-bootstrap` do not exist | No target principal boundary is deployed |
| Parent paths | `/usr`, `/usr/local`, `/opt`, `/var`, `/var/lib`, `/etc/systemd`, `/etc/systemd/system`, and `/usr/libexec` are root-owned mode 0755 | Root-owned installation parents are available |
| Filesystem | `/` is ext4, read-write, with no separate `/opt` or `/var/lib` mount | No read-only mount claim is permitted |
| Runtime filesystem | `/run` is tmpfs, read-write, nosuid, nodev; `/run/aether/oas` does not exist | Systemd may own runtime socket creation later |
| Existing state and units | `/var/lib/aether/oas` does not exist; all four requested unit names are `LoadState=not-found` | No M119A/M120A host object is deployed |
| Verification tools | `systemd-analyze`, `systemctl`, `systemd-notify`, `sha256sum`, `setpriv`, `unshare`, and `nsenter` exist | Tool presence is not deployment evidence |
| MAC/ACL tools | `getfacl`, `aa-status`, and `getenforce` are unavailable | ACL, AppArmor, and SELinux state is not assumed |

Host compatibility is not host verification. These facts cannot promote
`DEPLOYMENT_VERIFIED`.

## 3. Corrective Hard-Gate Closure Matrix

`CLOSED_BY_DESIGN` means the contract is internally specified and statically
locked. It does not mean implemented, built, installed, ready, or deployed.

| Gate | Required invariant | Design owner | Static structure | Runtime/deployment status | Result |
| --- | --- | --- | --- | --- | --- |
| A activation state | One record, explicit states, candidate authorization, non-circular readiness, crash recovery | Root lifecycle plus OAS startup | State table, field table, transition table, traces, rejection set | Not implemented; not deployed | CLOSED_BY_DESIGN |
| B descriptor order | Explicit `Sockets=` order and complete three-socket dependency | systemd plus M120A intake | Ordered unit table and FD mapping table | Not implemented as units; not deployed | CLOSED_BY_DESIGN |
| C unit generation | Generation-specific gates are absent during replacement and published only after complete verification | Root installer plus systemd Conditions | Generation protocol and power-loss table | Not implemented; not deployed | CLOSED_BY_DESIGN |
| D signing root | Fixed verifier, canonical domain/envelope, anchor lifecycle, dual-role approval, revocation | Host trust base plus release authority | Envelope/anchor tables and lifecycle rules | No verifier or key exists on target | CLOSED_BY_DESIGN |
| E Python coherence | Exact environment allowlist, truthful `-I`, fixed import root, coherent home | Release entrypoint plus unit | Environment, command, import-root, and path tables | Entrypoint not implemented | CLOSED_BY_DESIGN |
| F systemd resources | Conservative FD bound, restart throttle, supported hardening, truthful namespace/path semantics | systemd 252 plus OAS process | Resource calculation and directive table | Units not implemented | CLOSED_BY_DESIGN |
| G Build boundary | Every future artifact has a proposed path and separate review stage | Future repository Build | Inventory and stage table | Build not authorized | CLOSED_BY_DESIGN |

The static proof parses the structured tables and rejects contradictory values;
it is not satisfied by marker strings alone.

## 4. Activation Identity State Machine

### 4.1 States and single authoritative record

The single authoritative activation record is:

```text
/var/lib/aether/activation/activation-record.json
```

It is a root-owned regular file, mode `0444`, with no secret material. Root is
the only authority allowed to create or replace it. The OAS entrypoint may read
it; `aether-oas`, `aether-runtime`, and `aether-bootstrap` cannot write it.
The root lifecycle procedure serializes all transactions with:

```text
/run/lock/aether-install.lock
```

The record is canonical UTF-8 JSON with lexicographic Unicode keys,
`separators=(',', ':')`, `ensure_ascii=true`, finite integers only where
specified, and no implicit newline. A replacement is written to a root-owned
temporary file in the same directory, `fsync`ed, atomically renamed over the
record, and followed by `fsync` of the parent directory. A record digest is
the SHA-256 of those canonical payload bytes. There is no second authoritative
active-release identity object; the corrected contract uses only this record.

The complete state vocabulary is:

```text
NO_DEPLOYMENT
CANDIDATE_PENDING
QUIESCE_REQUIRED
ACTIVATING
COMMITTED
ROLLBACK_PENDING
RECOVERY_REQUIRED
```

The record has exactly these required fields:

| Field | Serialization and meaning |
| --- | --- |
| `record_version` | Integer `1`; record schema version |
| `state` | One exact state above |
| `transaction_id` | Root-approved bounded transaction identity; unique while pending |
| `record_sequence` | Strictly increasing integer; supports forward-consistency and accidental stale-state detection with retained transaction/audit evidence, but is not an independent anti-rollback anchor |
| `previous_record_digest` | Lowercase SHA-256 of the prior record, or `null` for first record |
| `host_boot_id` | Exact `/proc/sys/kernel/random/boot_id` captured for an activating window |
| `activation_issued_at_monotonic` | Numeric monotonic clock value captured by root when the pending activation is issued; operational authority for the same boot |
| `activation_expires_at_monotonic` | Numeric monotonic deadline; exactly `issued + bounded_duration`, required for pending states, and never extended by OAS |
| `activation_max_duration_seconds` | Fixed policy value `60`; the deadline cannot exceed this duration from issuance |
| `old_release_id` | Existing committed `r1-<64 hex>` release, or `null` for first install |
| `old_manifest_digest` | Old manifest digest, or `null` for first install |
| `candidate_release_id` | Candidate `r1-<64 hex>` release, or `null` in `NO_DEPLOYMENT` |
| `candidate_manifest_digest` | Candidate canonical manifest SHA-256 |
| `current_link_release_id` | `null`, old release, or candidate release as observed and authorized |
| `old_unit_generation_id` | Existing `g-<64 hex>` generation, or `null` for first install |
| `candidate_unit_generation_id` | Candidate `g-<64 hex>` generation |
| `unit_bundle_digest` | SHA-256 of the canonical four-unit byte bundle |
| `quiesce_state` | `NOT_STARTED`, `REQUIRED`, `PROVEN`, or `FAILED`; root-only replacement boundary state |
| `schema_before` | Exact M118A schema identity observed before activation |
| `schema_after` | Exact candidate-supported schema identity |
| `schema_compatibility` | `UNCHANGED`, `FORWARD_MIGRATION_REQUIRED`, or `INCOMPATIBLE` |
| `migration_state` | `NOT_STARTED`, `STARTED`, `COMMITTED`, or `ROLLED_BACK` |
| `readiness_result` | `NOT_RUN`, `PASSED`, `FAILED`, or `EXPIRED` plus bounded evidence digest |
| `smoke_result` | `NOT_RUN`, `PASSED`, `FAILED`, or `EXPIRED` plus bounded evidence digest |
| `commit_state` | `UNCOMMITTED`, `COMMITTED`, or `COMMIT_FAILED` |
| `rollback_state` | `NOT_REQUESTED`, `PENDING`, `COMPLETED`, or `BLOCKED` |
| `activation_reason` | Fixed vocabulary `FIRST_INSTALL`, `CODE_UPGRADE`, `SCHEMA_UPGRADE`, or `ROLLBACK` |
| `created_at_utc` / `updated_at_utc` | UTC audit metadata only; wall-clock values are never operational deadline authority |

`current_link_release_id` is an observed binding inside the authoritative
record, not an independent authority. The OAS entrypoint compares the actual
`/opt/aether/current` `lstat` target and manifest to the record before readiness.

### 4.2 Valid transitions

Only root may initiate lifecycle transitions; OAS may update only bounded
M118A state during the authorized candidate transaction and never this record.

| From | To | Exact guard and mutation |
| --- | --- | --- |
| absent record | `NO_DEPLOYMENT` | Root creates one canonical record only when no release, no current link, and no pending transaction exist |
| `NO_DEPLOYMENT` | `CANDIDATE_PENDING` | Root has a verified first-install bundle, unique transaction, exact `old_* = null`, and no existing canonical state that would be silently adopted |
| `COMMITTED` | `CANDIDATE_PENDING` | Root has a verified upgrade bundle, exact old release/generation/state identity, compatibility proof, and a new transaction |
| `CANDIDATE_PENDING` | `QUIESCE_REQUIRED` | Root has staged and verified the candidate bundle and begins the explicit admission/socket/service quiesce boundary |
| `QUIESCE_REQUIRED` | `ACTIVATING` | Root proves quiescence, replaces and verifies the unit generation, publishes its gate, records the monotonic activation window, and switches `current` |
| `ACTIVATING` | `COMMITTED` | Root observes candidate `READY=1`, bounded smoke pass, exact candidate link/manifest/unit/state identity, and no outstanding worker; root atomically records candidate as committed |
| `ACTIVATING` | `ROLLBACK_PENDING` | Readiness, smoke, identity, or deadline failure with a compatible old release and no irreversible migration commit |
| `ROLLBACK_PENDING` | `COMMITTED` | Root restores old link and old verified unit generation, restarts the old release, and records old identity only after readiness/smoke pass |
| any pending state | `RECOVERY_REQUIRED` | Expired/replayed/ambiguous record, unknown migration marker, missing old release, damaged anchor, or incompatible post-migration rollback |
| `RECOVERY_REQUIRED` | `CANDIDATE_PENDING` | Root-only recovery review creates a new transaction after preserving evidence; no automatic retry or guessing |

No transition skips `CANDIDATE_PENDING`. `COMMITTED` is written only after
readiness and smoke. A pending activation is valid only when the current boot
ID equals `host_boot_id`, the current monotonic value is below
`activation_expires_at_monotonic`, and the issued/deadline pair is exactly the
root-created bounded window. A boot-ID change expires every pending activation
automatically; UTC is audit metadata and cannot extend or revive it.

`record_sequence` is strictly increasing in the root procedure and, together
with `previous_record_digest`, proves forward consistency when compared with
retained transaction/audit evidence. It detects accidental stale state under
the trusted-root procedure. It is not an independent anti-rollback anchor:
malicious root can replace the record and associated host evidence. No stronger
replay claim is made; root remains the host trust base.

### 4.3 Truthful candidate startup rule

The candidate entrypoint does not require the candidate to be already
committed. It accepts exactly one pending authorization:

```text
record.state == ACTIVATING
record.transaction_id == approved transaction
record.host_boot_id == current boot ID
record.activation_issued_at_monotonic < now < record.activation_expires_at_monotonic
record.activation_expires_at_monotonic - record.activation_issued_at_monotonic <= 60
record.candidate_release_id == verified current-link release
record.candidate_manifest_digest == verified manifest digest
record.candidate_unit_generation_id == verified unit-generation gate
record.schema_compatibility != INCOMPATIBLE
record.commit_state == UNCOMMITTED
```

It also accepts a committed startup only when `state == COMMITTED`,
`commit_state == COMMITTED`, `current_link_release_id == candidate_release_id`,
and every record, manifest, unit, interpreter, dependency, and state identity
matches. `NO_DEPLOYMENT` may reach first-install readiness only through the
recorded `ACTIVATING` transition; it is never inferred from a missing file.

The entrypoint rejects an unrecorded candidate, stale or monotonic-expired
window, wrong boot ID,
wrong transaction, old record sequence, replayed record digest, mismatched
current link, mismatched unit generation, mismatched manifest, incompatible or
unexpected schema, missing state, wrong migration marker, or simultaneous
activation. It exits nonzero without `READY=1`.

### 4.4 First-install trace

First install is distinct from upgrade:

```text
NO_DEPLOYMENT
  -> CANDIDATE_PENDING (old release and old generation are null)
  -> QUIESCE_REQUIRED
  -> ACTIVATING (candidate generation gate verified; current points to candidate)
  -> READY=1 (candidate is authorized by the pending record, not committed)
  -> SMOKE_PASS
  -> COMMITTED (candidate identity becomes the sole committed identity)
```

First-install preconditions include no existing release, no current link, no
pending record, no existing canonical OAS state to adopt, an approved exact
initial schema contract, and the complete signed bundle. If OAS creates the
initial M118A schema during the authorized candidate transaction and readiness
then fails, the record and state are preserved for root recovery; they are not
silently deleted or replaced with a new instance.

### 4.5 Upgrade trace

Code-only upgrade and schema upgrade share the identity state machine:

```text
COMMITTED(old)
  -> CANDIDATE_PENDING(old + candidate)
  -> QUIESCE_REQUIRED
  -> ACTIVATING(old + candidate; current points to candidate)
  -> READY=1 (candidate authorization is pending-record based)
  -> SMOKE_PASS
  -> COMMITTED(candidate)
```

For `CODE_UPGRADE`, `schema_before == schema_after` and migration remains
`NOT_STARTED`. For `SCHEMA_UPGRADE`, a protected backup is recorded first,
OAS performs only the manifest-approved forward migration as `aether-oas`, and
`migration_state` becomes `COMMITTED` before the final commit. A candidate
cannot impersonate the old committed release, and the old release remains
retained until the final record transition.

### 4.6 Crash and power-loss recovery

| Interruption point | Durable result | Boot/recovery result |
| --- | --- | --- |
| Before pending record | Old committed state unchanged | Normal old release remains eligible |
| After pending record, before unit work | `CANDIDATE_PENDING` | Candidate is not activated; root may discard staging or continue exact transaction |
| During admission/socket/service quiesce | `QUIESCE_REQUIRED`, old gate and units unchanged | Root proves shutdown or aborts; no gate or unit mutation is permitted |
| After stop but before quiescence proof | `QUIESCE_REQUIRED`, stop result unresolved | Any process, listener, job, worker, or populated cgroup sends the transaction to recovery; old generation remains authoritative |
| During unit replacement | Old generation gate invalidated; candidate gate absent | Every socket and service Condition fails; mixed units cannot create sockets or start OAS |
| After complete unit verification, before `ACTIVATING` | Candidate gate exists, record still pending | Root must validate the exact transaction; no automatic candidate start |
| After `ACTIVATING`, before current switch | Record authorizes candidate but link still old | Candidate startup is impossible because link identity fails; root rolls back pending state |
| After current switch, before readiness | `ACTIVATING`, link candidate | Boot does not resume expired/old-boot activation; root restores old identity or enters recovery |
| After migration starts, before migration commit | M118A transaction marker is pending | OAS rolls back its transaction or enters bounded recovery; root never guesses |
| After readiness/smoke, before commit | `ACTIVATING`, results durable | Root repeats exact final commit or rolls back; no success claim is made |
| After committed record replacement | `COMMITTED`, candidate identity durable | Boot verifies record, link, unit gate, manifest, and state before readiness |
| During rollback | `ROLLBACK_PENDING` | No activation until old release/generation and state compatibility are reverified |
| Missing/corrupt record or anchor | Evidence is preserved | All units remain gated; state is `RECOVERY_REQUIRED` |

The protocol claims atomic replacement only for one file and one directory entry
at a time. It does not claim atomicity across the record, symlink, units,
generation gate, daemon-reload, process, or state database. The record and
explicit mismatch recovery make the multi-object operation crash-safe without
pretending it is one filesystem transaction.

## 5. Release Identity and Signing Trust Root

### 5.1 Release identity

The selected release model is:

```text
ROOT_OWNED_VERSIONED_CONTENT_ADDRESSED_RELEASE_DIRECTORIES
WITH_CANONICAL_MANIFEST_AND_DETACHED_ED25519_SIGNATURE_ENVELOPE
```

```text
/opt/aether
/opt/aether/releases/r1-<64 lowercase hexadecimal manifest digest>
/opt/aether/current
```

The release ID is `r1-` plus the SHA-256 of canonical manifest payload bytes.
The release directory is never edited in place. `current` is a root-owned
relative symlink to a verified release. The activation record, not a symlink or
filename, is authoritative.

The manifest has exactly these top-level keys:

```text
manifest_version
release_id_format
source
runtime
dependencies
build
files
units
schema_compatibility
policy
```

Every source file, installed file, interpreter identity, dependency artifact,
unit byte sequence, schema range, allowed path, Git commit/tag, source-tree
digest, builder identity, and reproducibility result is manifest-bound.

### 5.2 Fixed signing domain and envelope

The one approved signing mechanism is Ed25519 verified by the fixed host
verifier described below. No OpenSSL, Python package, or alternate verifier is
an interchangeable option.

The signing input is exact:

```text
SIGNED_BYTES =
ASCII("aether.m121a.release-manifest.v1")
+ BYTE(0x00)
+ UTF8(canonical_manifest_payload)
```

The detached signature envelope is canonical UTF-8 JSON with exactly these
top-level fields. The approval payload is carried in the envelope; it is not
reconstructed from unrelated metadata:

| Field | Exact contract |
| --- | --- |
| `envelope_version` | Integer `1` |
| `domain` | `aether.m121a.release-manifest.v1` |
| `manifest_version` | Exact manifest version, integer `1` for the first release format |
| `manifest_sha256` | Lowercase SHA-256 of canonical manifest bytes |
| `manifest_length` | UTF-8 byte length of canonical manifest bytes |
| `release_id` | Exact `r1-<64 hex>` derived from that digest |
| `approval_payload` | One canonical object with exactly the approval fields below |
| `release_signature` | One exact release signature object |
| `approval_signature` | One exact approval signature object |
| `rotation_signatures` | Empty outside rotation; exactly the separately required old/next role signatures during an approved overlap |

`approval_payload` has exactly these fields:

| Field | Exact contract |
| --- | --- |
| `manifest_digest` | Must equal the envelope `manifest_sha256` |
| `release_id` | Must equal the envelope `release_id` |
| `source_commit` | Exact full Git commit included in the manifest |
| `test_evidence_digest` | Lowercase SHA-256 of the named bounded test evidence |
| `approval_id` | Unique root/PM approval identity |
| `activation_release_policy` | Fixed policy object naming the permitted activation and rollback classes |
| `issued_at_utc` | UTC audit issuance time |
| `expires_at_utc` | UTC approval expiry; verifier requires current audit time before expiry |
| `approver_policy` | Exact role threshold and allowed approver key IDs |

The approval payload is canonical UTF-8 JSON with lexicographic Unicode keys,
`separators=(',', ':')`, `ensure_ascii=true`, finite values only, no implicit
newline, and no duplicate or unknown fields. The envelope uses the same
canonical serialization and has no fields beyond the table. Each signature
object has exactly `role`, `key_id`, `algorithm`, `encoding`, and `signature`.
`role` is fixed by its containing field (`release` or `approval`), `algorithm`
is `Ed25519`, `encoding` is `base64url-no-padding-64-raw-bytes`, `key_id` is an
exact anchor key identifier, and `signature` decodes to exactly 64 bytes. The
approval signature signs this exact carried payload:

```text
APPROVAL_BYTES =
ASCII("aether.m121a.release-approval.v1")
+ BYTE(0x00)
+ UTF8(canonical_approval_payload)
```

The release signature signs `SIGNED_BYTES`. The verifier rejects a missing
approval payload, payload/signature mismatch, payload/manifest mismatch,
expired approval, wrong release ID, wrong source commit, wrong test-evidence
digest, wrong approver role, duplicate or unknown fields, and conflicting
rotation signatures. A release signature proves artifact provenance; an
approval signature proves approval of that exact artifact and evidence. Neither
signature alone authorizes host activation: the activation transaction must
bind the same release ID, manifest digest, approval ID, and approval payload
digest.

Outside a rotation overlap, `rotation_signatures` is exactly `[]`. During an
approved overlap, `release_signature` and `approval_signature` use the next
role keys and `rotation_signatures` contains exactly one old release signature
and one old approval signature. The four signatures must have distinct key IDs
where required by the anchor policy, exactly two signatures per role, and
non-conflicting validity windows; a duplicate, unknown, revoked, retired, or
wrong-role rotation signature rejects the envelope.

### 5.3 Anchor, verifier, bootstrap, and custody

The trust anchor is:

```text
/etc/aether/release-trust-anchor.pub
```

It is a root-owned regular file mode `0444`, canonical UTF-8 JSON, and not part
of any release. The canonical anchor payload has exactly
`anchor_version`, `anchor_id`, `keys`, `rotation_policy`, and `revocations`.
Each key has `key_id`, `role`, `algorithm`, `public_key_encoding`, `public_key`,
`status`, `not_before`, and `not_after`. Public keys are base64-encoded DER
SubjectPublicKeyInfo bytes. The canonical anchor envelope has exactly
`anchor_version`, `anchor_id`, `keys`, `rotation_policy`, `revocations`, and
`anchor_fingerprint`; its payload is the canonical serialization of the first
five fields and never contains `anchor_fingerprint`.

The non-self-referential fingerprint contract is exact:

```text
ANCHOR_DOMAIN = ASCII("aether.m121a.release-trust-anchor.v1")
ANCHOR_PAYLOAD = canonical JSON of {anchor_version, anchor_id, keys,
                                    rotation_policy, revocations}
ANCHOR_FINGERPRINT = SHA256(ANCHOR_DOMAIN + BYTE(0x00)
                            + UTF8(ANCHOR_PAYLOAD))
ANCHOR_ENVELOPE = ANCHOR_PAYLOAD plus anchor_fingerprint
```

The verifier rejects duplicate or unknown fields, computes the fingerprint
from `ANCHOR_PAYLOAD` before accepting the envelope field, and compares the
lowercase digest with the externally approved fingerprint. It verifies the
anchor fingerprint before using any key, then verifies key shape, role,
validity, revocation, and the envelope. Rotation publishes a new externally
approved fingerprint before the overlap window; recovery restores only that
fingerprint-approved anchor and never accepts a candidate-supplied anchor.

The one approved verifier is:

```text
VERIFIER: /usr/libexec/aether-release-verify
CRYPTO_EXECUTABLE: /usr/bin/openssl
CRYPTO_POLICY: OpenSSL 3.0 Ed25519 pkeyutl verification only
```

The verifier is a separately approved root-owned host-trust artifact, present
and hash-verified before any candidate release is trusted. It parses the
canonical anchor, validates the non-self-referential fingerprint, reconstructs
the two domain-separated signed byte streams, and materializes only temporary
mode-0600 objects in root staging:

```text
/var/lib/aether/install/<tx>/verify/release-signed-bytes.bin
/var/lib/aether/install/<tx>/verify/release-signature.raw
/var/lib/aether/install/<tx>/verify/release-key.spki.der
/var/lib/aether/install/<tx>/verify/approval-signed-bytes.bin
/var/lib/aether/install/<tx>/verify/approval-signature.raw
/var/lib/aether/install/<tx>/verify/approval-key.spki.der
```

`<tx>` is generated only by the root procedure; no caller chooses a directory,
file, or option. The staging directory is `root:root`, mode `0700`; each
temporary regular file is `root:root`, mode `0600`, opened with `O_CREAT|O_EXCL`
and `O_NOFOLLOW`. Signed-byte inputs are bounded to the canonical manifest or
approval limits; raw signatures are exactly 64 bytes; DER public keys are
bounded to 4096 bytes and must be one valid SubjectPublicKeyInfo. Each write is
flushed, `fsync`ed, and the directory is `fsync`ed before verification.

For each role, the host verifier calls `execve` with this fixed argv and no
shell, using `LC_ALL=C` and no caller environment:

```text
/usr/bin/openssl
pkeyutl
-verify
-rawin
-in
/var/lib/aether/install/<tx>/verify/<role>-signed-bytes.bin
-sigfile
/var/lib/aether/install/<tx>/verify/<role>-signature.raw
-inkey
/var/lib/aether/install/<tx>/verify/<role>-key.spki.der
-pubin
-keyform
DER
```

The only substitution is the verifier's fixed `role` (`release` or
`approval`) and root-generated `<tx>` path. No caller-selected option, key,
path, or input is accepted. Stdout and stderr are each capped at 4096 bytes;
the only accepted stdout is the OpenSSL 3.0 success line
`Signature Verified Successfully\n`, stderr must be empty, and exit status `0`
is required. Any other output, nonzero status, timeout, malformed key,
malformed signature, wrong role, wrong key ID, expired/revoked key, or
verification failure rejects the bundle. Release and approval are always
separate invocations. Temporary files are unlinked only after the result is
durably recorded, then the directory is fsynced; failed cleanup leaves the
transaction in recovery rather than silently claiming success.

The candidate cannot supply, replace, or select the verifier, its executable,
its anchor, or its trust path. Debian package identity, exact executable hash,
and OpenSSL version are host evidence requirements. M121A does not install
either file.

Initial anchor provisioning is out-of-band: the Owner/PM approves the full
anchor fingerprint through a separately recorded two-person review; root
installs it only after verifying the fingerprint through that independent
channel; and the anchor file is fsynced before any release bundle is accepted.
The initial private signing keys are generated offline, encrypted under the
release authority's custody policy, and never reach the target host, release
bundle, backup, manifest, log, process environment, or OAS state.

### 5.4 Rotation, revocation, rollback, and disaster recovery

| Lifecycle event | Exact rule |
| --- | --- |
| Normal release | One non-revoked `release` key plus one non-revoked `approval` key; roles and key IDs must differ |
| Planned rotation | Anchor contains old and next key for each role with independent validity windows and an out-of-band next-anchor fingerprint |
| Rotation overlap | During the overlap window, every release requires both old and next signatures for each role, four signatures total; after expiry, old keys are not accepted |
| Revocation | Anchor records key ID and UTC revocation time; verifier rejects that key for new activation and rollback regardless of release retention |
| Compromised key | PM/Owner publishes an out-of-band corrected anchor fingerprint, marks the key revoked, rejects affected releases, and requires a newly signed release; no automatic fallback occurs |
| Rollback | Only a retained release whose release and approval keys remain valid and non-revoked may be activated; a retired or revoked key cannot authorize rollback |
| Damaged/missing anchor | Verification fails closed; no release, unit, socket, service, or rollback starts; root restores the exact fingerprint-approved anchor through disaster recovery |
| Audit | Record anchor fingerprint, verifier hash/version, key IDs, signature results, approval ID, manifest digest, transaction ID, and timestamps; never record private material |

The trust anchor is not release-supplied and is not silently replaced by a
candidate. A signature proves provenance under the approved key policy; it does
not prove a trustworthy root host, correct target, readiness, or deployment.

## 6. Python Runtime, Import Roots, and Environment

### 6.1 Fixed interpreter and command

The production interpreter is a root-owned regular executable:

```text
PRODUCTION_PYTHON: /usr/bin/python3.11
PYTHON_OWNER: root:root
PYTHON_VERSION_POLICY: exact manifest value
PYTHON_REQUIRED_TYPE: regular executable
```

The release contains a root-owned relative link:

```text
/opt/aether/current/runtime/bin/python -> /usr/bin/python3.11
```

The corrected exact `ExecStart` is:

```text
/opt/aether/current/runtime/bin/python -I -B -S -c 'import sys; sys.path.insert(0,"/opt/aether/current/runtime/lib/python3.11/site-packages"); from aether.oas.host_entrypoint import main; raise SystemExit(main())'
```

The fixed module remains `aether.oas.host_entrypoint`. The standard-library-only
bootstrap expression inserts exactly one absolute release root before importing
that module. It is not caller-controlled and does not use `PYTHONPATH`, current
directory discovery, a user site, or a mutable checkout.

### 6.2 Import-root proof

The future Build installs the complete application and dependency closure at:

```text
/opt/aether/current/runtime/lib/python3.11/site-packages
```

The import roots after the fixed bootstrap are exactly:

| Root | Source | Allowed |
| --- | --- | --- |
| `/usr/lib/python3.11` and the exact standard-library paths from the approved interpreter | `/usr/bin/python3.11` | Yes |
| `/opt/aether/current/runtime/lib/python3.11/site-packages` | Current verified release, inserted by fixed `-c` expression | Yes |
| Current working directory | `WorkingDirectory` only | No import authority |
| User site | Python isolated mode `-I` | No |
| System site packages | Python `-S` | No |
| `PYTHONPATH` and `PYTHONHOME` | Environment | No |
| Development checkout | No path insertion or fallback | No |

The verifier runs the exact command with a poisoned current directory and
forbidden Python variables, then proves that the imported module file is below
the candidate release root, has the manifest hash, and is not from the
checkout. Failure prevents readiness.

### 6.3 Exact environment and home

Python hash randomization is not required to be deterministic and no claim is
made for `PYTHONHASHSEED`. `-B` is the sole bytecode-disable mechanism;
`-I` ignores Python environment variables and `-S` disables site initialization.

The environment policy has two distinct classes. The following values are the
only authority-bearing or protocol inputs that the entrypoint snapshots and
validates:

```text
PROTOCOL_ENVIRONMENT:
LISTEN_PID
LISTEN_FDS
LISTEN_FDNAMES
NOTIFY_SOCKET
LANG=C.UTF-8
LC_ALL=C.UTF-8
TZ=UTC
HOME=/var/empty
```

`LISTEN_PID`, `LISTEN_FDS`, `LISTEN_FDNAMES`, and `NOTIFY_SOCKET` are validated
exactly for the systemd protocol. `LANG`, `LC_ALL`, `TZ`, and `HOME` are
validated against the fixed unit values when intentionally required. A missing
required protocol value, malformed value, wrong PID/count/name, unexpected
fixed locale/timezone/home value, or protocol mismatch fails closed.

Systemd may also inject ambient non-authority metadata, including
`INVOCATION_ID`, `JOURNAL_STREAM`, `PATH`, `USER`, `LOGNAME`, `SHELL`,
`SYSTEMD_EXEC_PID`, and other version-dependent manager variables. These values
are never trusted for paths, identity, authorization, release selection, state,
units, keys, or configuration; they are never logged with values and are not a
startup failure merely because systemd supplied them. The fixed entrypoint
snapshots only the required protocol inputs, copies them into explicit
in-memory values, clears all other environment entries before application
initialization, and then continues without treating the environment as an
authority source.

The unit does not use `EnvironmentFile`, `PassEnvironment`, `PYTHONHASHSEED`, or
`PYTHONDONTWRITEBYTECODE`. `PYTHONPATH`, `PYTHONHOME`, user site, system site,
caller configuration, and development-checkout fallback remain prohibited.

`/var/empty` is a required provisioned object: `root:root`, directory mode
`0555`, no symlink, no regular files, and no service-principal write or execute
authority beyond directory traversal needed to use it as `HOME`. The service
does not write its home. Working directory is `/opt/aether/current`; canonical
state is `/var/lib/aether/oas/security_kernel.sqlite3`.

## 7. Principals, Filesystem, and Canonical State

### 7.1 Principals

The five-principal separation from M119A is preserved:

| Role | User | UID | Primary group/GID | Shell and groups |
| --- | --- | ---: | --- | --- |
| Human Owner | `aether-owner` | 3001 | `aether-owner`/3001 | `/bin/bash`; no supplementary groups |
| Ordinary runtime | `aether-runtime` | 3002 | `aether-runtime`/3002 | `/usr/sbin/nologin`; no supplementary groups |
| OAS service | `aether-oas` | 3003 | `aether-oas`/3003 | `/usr/sbin/nologin`; no supplementary groups |
| Bootstrap helper | `aether-bootstrap` | 3004 | `aether-bootstrap`/3004 | `/usr/sbin/nologin`; no supplementary groups |
| Lifecycle administrator | `root` | 0 | `root`/0 | Host root policy |

IDs are fixed target values. Root fails closed on name, UID, GID, shell, home,
primary group, collision, or membership mismatch and never remaps IDs or reuses
the current `aether` account. Rollback and uninstall preserve all principals;
M121A never deprovisions them.

### 7.2 Canonical objects

| Object | Owner | Mode/type | Rule |
| --- | --- | --- | --- |
| `/opt/aether` | `root:root` | directory `0755` | Installation root; service principals cannot write |
| `/opt/aether/releases` | `root:root` | directory `0755` | Only verified release directories |
| `/opt/aether/releases/r1-<digest>` | `root:root` | directory `0555` | Immutable-by-service release |
| `/opt/aether/current` | `root:root` | relative symlink | Derived current reference; checked against record |
| `/etc/aether` | `root:root` | directory `0755` | Trust/configuration parent |
| `/etc/aether/release-trust-anchor.pub` | `root:root` | regular file `0444` | Out-of-band public trust anchor |
| `/var/lib/aether` | `root:root` | directory `0755` | State parent |
| `/var/lib/aether/activation` | `root:root` | directory `0755` | Activation record and generation gates |
| `/var/lib/aether/activation/activation-record.json` | `root:root` | regular file `0444` | Sole activation authority record |
| `/var/lib/aether/activation/unit-generations` | `root:root` | directory `0755` | Generation markers |
| `/var/lib/aether/oas` | `aether-oas:aether-oas` | directory `0700` | Sole persistent OAS state directory |
| `/var/lib/aether/oas/security_kernel.sqlite3` | `aether-oas:aether-oas` | regular file `0600` | Canonical M118A state |
| SQLite `-wal` and `-shm` | `aether-oas:aether-oas` | regular files `0600` | Never copied independently |
| `/var/lib/aether/install` | `root:root` | directory `0700` | Transaction staging |
| `/var/lib/aether/backups` | `root:root` | directory `0700` | Protected backup staging |
| `/var/lib/aether/rollback` | `root:root` | directory `0700` | Retained rollback records |
| `/run/aether` | `root:root` | directory `0755` | Volatile runtime parent |
| `/run/aether/oas` | `root:root` | directory `0755` | Systemd socket parent |
| `/var/empty` | `root:root` | directory `0555` | Non-writable service home |
| `/etc/systemd/system` unit files | `root:root` | regular files `0644` | Exactly four manifest-bound units |
| application logs | none | not provisioned | Journal only |

The canonical activation record is readable by OAS but writable only by root.
OAS may write only SQLite state and its bounded temporary directory. Ordinary
runtime has no state, code, unit, activation, backup, account, or service
manager access. All paths are checked with `lstat`; unexpected symlinks,
hardlinks, devices, FIFOs, mounts, path traversal, world/group write bits, and
special files fail closed.

## 8. Systemd Socket Set and Descriptor Order

### 8.1 Exact ordered set

The service unit contains this explicit ordered declaration; systemd 252 uses
the declaration order for the activation descriptor order:

```text
Sockets=aether-oas-runtime.socket aether-oas-bootstrap.socket aether-oas-broker.socket
```

The exact ordered mapping is:

| Order | FD | Socket unit | `FileDescriptorName` | Path | Expected peer |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 3 | `aether-oas-runtime.socket` | `runtime` | `/run/aether/oas/runtime.sock` | `aether-runtime` uid/gid 3002/3002 |
| 2 | 4 | `aether-oas-bootstrap.socket` | `bootstrap` | `/run/aether/oas/bootstrap.sock` | `aether-bootstrap` uid/gid 3004/3004 |
| 3 | 5 | `aether-oas-broker.socket` | `broker` | `/run/aether/oas/broker.sock` | root uid/gid 0/0 |

The M120A intake contract remains exact:

```text
LISTEN_FDNAMES=runtime:bootstrap:broker
LISTEN_FDS=3
descriptor 3 -> runtime
descriptor 4 -> bootstrap
descriptor 5 -> broker
```

The entrypoint verifies `LISTEN_PID`, exactly three descriptors, the exact
names, AF_UNIX, SOCK_SEQPACKET, listening state, path, owner/group/mode, inode
identity, and endpoint role before readiness. It never relies on enumeration
of `/run`, descriptor discovery, or dictionary order.

`FileDescriptorName=` supplies the names, and M120A still checks exact names,
paths, types, and roles rather than trusting names alone. No file-descriptor
store descriptors are authorized; `FileDescriptorStoreMax=0` is explicit in
the service unit. Multiple simultaneous socket activation is therefore still
limited to the three declared listening sockets and cannot introduce arbitrary
stored descriptors. Future Build tests must parse the generated units with the
real systemd 252 `systemd-analyze verify` contract and run an isolated
systemd-compatible socket-activation test, not only inspect text. Deployment
verification must record the actual `LISTEN_FDNAMES` value and FD 3/4/5 role
mapping from the reviewed target.

### 8.2 Dependency, manual-start, and restart behavior

The service `[Unit]` has `Requires=` and `After=` for all three socket units,
plus the explicit `Sockets=` declaration. Each socket has `Service=` pointing
to the service, but none has `Requires=aether-oas.service`; this avoids a
socket/service dependency cycle. Each socket has `Before=aether-oas.service`,
`PartOf=aether-oas.service`, and the same generation and activation-record
conditions as the service.

Starting one socket manually is not a partial-service path: systemd expands the
service dependency transaction to all three sockets. If any socket cannot be
activated or its generation condition is false, the service is not started.
Direct `systemctl start aether-oas.service` likewise requires the complete
ordered set; it fails rather than accepting fewer descriptors. A service process
that receives fewer, extra, or renamed descriptors exits without readiness.

Stopping or restarting the service propagates to all three sockets through
`PartOf`. The sockets are then recreated in the same explicit order. Queued
connections are intentionally rejected during that boundary; clients receive
bounded unavailability and retry with a new connection. No queued connection is
claimed to survive a service restart.

### 8.3 Socket unit contract

Each socket unit has these exact properties:

```text
ListenSequentialPacket=/run/aether/oas/<role>.sock
SocketUser=aether-oas
SocketGroup=<role group>
SocketMode=0660
Backlog=64
Accept=no
DirectoryMode=0755
RemoveOnStop=yes
Service=aether-oas.service
```

`SocketGroup` is `aether-runtime`, `aether-bootstrap`, and `root` for the three
ordered units. There are no owner-broker units in M121A; that M119A frontier is
preserved but not installed or implemented.

## 9. Unit-Generation Transaction and Power Loss

### 9.1 Generation identity and gates

Every complete four-unit bundle has one generation ID:

```text
g-<64 lowercase hexadecimal unit-bundle digest>
```

The bundle digest is SHA-256 over the canonical ordered concatenation of the
four unit names, exact unit bytes, and NUL separators. The generation gate is:

```text
/var/lib/aether/activation/unit-generations/g-<digest>.ready
```

The gate is a root-owned regular file mode `0444` containing the generation ID,
bundle digest, four unit hashes, transaction ID, and `VERIFIED` marker in
canonical JSON. All four units in that generation contain an exact
generation-specific `ConditionPathExists` for this gate. The gate is not the
commit record: an `ACTIVATING` candidate may have a verified gate while the
activation record remains uncommitted.

### 9.2 Quiesce before replacement

`ConditionPathExists` is evaluated when a unit activation job is admitted. It
does not stop an already-running socket or service when its generation gate is
removed. Therefore the old generation is quiesced before any gate invalidation
or first live-unit replacement:

| Quiesce step | Root action | Required proof or failure result |
| --- | --- | --- |
| 1 | Stop new admission by marking the lifecycle transaction quiescing and refusing new install/activation work | No new activation job is admitted; failure aborts before unit mutation |
| 2 | Stop all three socket units in one manager transaction | Runtime, bootstrap, and broker listeners stop; failure aborts |
| 3 | Stop `aether-oas.service` | OAS receives bounded M120A shutdown; failure aborts |
| 4 | Wait at most `TimeoutStopSec=10s` for the M120A shutdown result | Clean result requires no outstanding worker; timeout is a failed quiesce |
| 5 | Verify no OAS process, accepted connection, socket unit, listener, activation job, or outstanding worker remains | Any remaining object aborts with old generation still authoritative |
| 6 | Verify systemd unit state and the service cgroup are inactive and empty | Unknown, active, stopping, queued, or populated cgroup state aborts |
| 7 | Record the quiesce evidence and only then invalidate the old generation gate | The next replacement step is permitted only after all proofs pass |

Power loss during this boundary is fail-closed: a pending `QUIESCE_REQUIRED`
record leaves the old gate and units unchanged until quiescence is retried, or
enters `RECOVERY_REQUIRED` if the observed state is ambiguous. A gate prevents
future activation but cannot terminate an already-running unit; safe
replacement depends on proven quiescence plus an absent generation gate.

### 9.3 Replacement protocol

The corrected protocol is not an atomic replacement of four files:

| Step | Root action | Required durable condition |
| --- | --- | --- |
| 1 | Acquire install lock and read one committed record | No simultaneous transaction |
| 2 | Stage candidate units under `/var/lib/aether/install/<tx>/units` | Mode 0700, root-only, complete file list |
| 3 | Verify all staged bytes, manifest hashes, owner/mode/type, and generation digest | Candidate bundle complete |
| 4 | Stop new admission, all three socket units, and `aether-oas.service`; wait for bounded M120A shutdown | Quiesce protocol is entered before any live unit mutation |
| 5 | Verify no process, connection, listener, socket unit, activation job, worker, active cgroup, or populated cgroup remains | Quiescence is proven; otherwise abort with no unit mutation |
| 6 | Invalidate the old live generation gate by same-directory rename to a transaction quarantine name and fsync its parent | No old socket or service Condition can pass; running units were already stopped |
| 7 | Replace each live unit independently through root-owned temp file, file fsync, rename, and parent-directory fsync | Mixed files may exist physically but are not activatable |
| 8 | Run `systemd-analyze verify` and one `daemon-reload` | Manager accepted candidate syntax |
| 9 | Verify `systemctl cat`, effective properties, exact four unit bytes, and all generation references | Complete candidate generation proven |
| 10 | Atomically install candidate `g-<digest>.ready` and fsync the generation directory and parent | All Conditions for exactly this generation can pass |
| 11 | Write `ACTIVATING` record and switch `current` only in the prescribed activation transaction | Candidate is authorized, not committed |
| 12 | Start the three sockets in the one systemd transaction and observe readiness/smoke | Candidate evidence collected |

The old committed generation gate is invalidated only after quiescence and
before the first live unit replacement. No operation claims atomicity across
the four files. A candidate generation gate is published only after every live
unit and effective property has been verified, so a power loss between any two
replacements leaves no generation gate and therefore no socket or service can
activate.

### 9.3 Boot and mismatch behavior

| Boot condition | Unit result | Recovery result |
| --- | --- | --- |
| Committed record and matching generation gate exist | Conditions may pass; OAS still verifies every identity before readiness | Normal verified startup |
| Committed record exists but gate is missing | All four units are condition-failed | Root restores the last complete unit generation or enters `RECOVERY_REQUIRED` |
| Pending record or candidate gate exists after reboot with a different boot ID | Entry and unit policy refuse automatic activation | Root reviews exact pending transaction; no automatic candidate resume |
| Unit file references `g-X` but only `g-Y.ready` exists | That unit condition fails; the complete set cannot start | Root restores a complete set |
| Unit hashes or effective properties differ from the gate | Root invalidates the gate before activation; service remains unready | Recovery preserves evidence and restores last complete set |
| Mixed live files after power loss | At least one unit has no matching complete gate | No socket creation or OAS start is permitted |

The gate is required on every socket unit capable of creating an endpoint and on
the service unit capable of starting OAS. Code-only activation leaves the unit
generation unchanged and therefore does not perform a unit-generation upgrade;
the activation record still changes through the same candidate state machine.

## 10. Executable Systemd Resource and Hardening Contract

### 10.1 File-descriptor calculation

The M120A admission ceiling is 32 active plus 64 queued accepted connections.
The conservative descriptor calculation is:

| Resource | Count |
| --- | ---: |
| Activated listening sockets | 3 |
| Accepted client connections, 32 active + 64 queued | 96 |
| SQLite-related descriptors, 32 connections x database/WAL/SHM | 96 |
| Native systemd notification socket | 1 |
| Interpreter, manifest, trust-anchor, and bounded staging descriptors | 8 |
| epoll/event, bookkeeping, and journal-related descriptors | 16 |
| Explicit reserve | 64 |
| Conservative total | 284 |

The selected unit value is:

```text
LimitNOFILE=512
```

This leaves 228 descriptors above the calculated 284 bound. The service rejects
admission above the M120A 32-active/64-queued ceiling rather than relying on
the kernel limit as its concurrency policy.

### 10.2 Restart and shutdown contract

The exact restart policy is:

```text
Restart=on-failure
RestartSec=2s
StartLimitIntervalSec=60s
StartLimitBurst=5
StartLimitAction=none
```

After five failures in 60 seconds, systemd leaves the service failed and does
not select another release, interpreter, state path, or API. Operator recovery
is explicit: inspect the activation record/journal, correct or roll back through
the root lifecycle procedure, then use `systemctl reset-failed` and start the
complete socket set. No automatic fallback is permitted.

`TasksMax=128` covers one main thread, three accept threads, 32 worker threads,
systemd/runtime overhead, and bounded reserve. `MemoryMax=512M` and
`CPUQuota=100%` are resource ceilings, not readiness shortcuts; integrity
verification must complete within `TimeoutStartSec=30s` or readiness fails.
The service has `TimeoutStopSec=10s`. Application shutdown stops admission,
cancels queued work, requests non-waiting executor cancellation, and polls
tracked work. A non-interruptible worker remains explicitly outstanding; the
service never records a clean stop or commits a candidate while it remains.
Systemd may terminate the process at its stop deadline, which is recorded as a
bounded failed stop and never as successful shutdown.

### 10.3 Systemd 252 directive semantics

Every selected directive below is mandatory. The future installer rejects a
host whose `systemd-analyze --version` is not the approved systemd 252 policy,
whose `systemd-analyze verify` reports an unknown/unsupported mandatory
directive, or whose effective properties differ from the manifest. There is no
weaker hardening fallback.

| Directive | systemd 252 meaning and access consequence |
| --- | --- |
| `User`, `Group`, `SupplementaryGroups=` | Runs exactly as `aether-oas` with no supplementary groups |
| `NoNewPrivileges=yes` | Prevents privilege gains after exec |
| `PrivateTmp=yes` | Private temporary namespace; shared `/tmp` is unavailable |
| `PrivateDevices=yes` | Device nodes are inaccessible; no device access is needed |
| `ProtectSystem=strict` | System hierarchy is read-only except explicit write paths |
| `ProtectHome=yes` | `/home`, `/root`, and `/run/user` are inaccessible |
| `ReadOnlyPaths=/opt/aether /etc/aether/release-trust-anchor.pub` | Code and trust anchor are read-only |
| `ReadWritePaths=/var/lib/aether/oas` | Only canonical OAS state is writable |
| `RestrictAddressFamilies=AF_UNIX` | Network families are denied; inherited AF_UNIX descriptors remain usable |
| `RestrictSUIDSGID=yes` | Setuid/setgid and file capability transitions are denied |
| `CapabilityBoundingSet=` and `AmbientCapabilities=` | No Linux capabilities are retained or ambient |
| `LockPersonality=yes` | Personality changes are denied |
| `ProtectKernelTunables`, `ProtectKernelModules`, `ProtectKernelLogs`, `ProtectControlGroups`, `ProtectClock` = `yes` | Kernel and manager control surfaces are inaccessible |
| `RestrictNamespaces=yes` | Boolean yes denies creation and entry of all process namespaces after systemd setup; this is not the opposite of restriction |
| `RestrictRealtime=yes` | Realtime scheduling is denied |
| `SystemCallArchitectures=native` | Only the host native syscall ABI is allowed |
| `LimitCORE=0` | No core dumps |
| `TasksMax=128` | Cgroup task ceiling described above |
| `MemoryMax=512M`, `CPUQuota=100%` | Cgroup memory and CPU ceilings described above |
| `FileDescriptorStoreMax=0` | No systemd file-descriptor-store descriptors are retained or passed |
| `Type=notify`, `NotifyAccess=main` | Only the main OAS process may establish readiness |
| `ConditionPathExists=` and `AssertPathExists=` | Every socket and service is gated by activation record, exact generation marker, and current root |

The service can still read its verified release, trust anchor, and activation
record, write its OAS state, use inherited activation descriptors, and send the
native `NOTIFY_SOCKET` datagram. Unsupported mandatory hardening fails closed
before unit activation; it is never silently omitted.

### 10.4 Exact service unit target

The future service unit has this exact responsibility. `<generation>` is
replaced by the unit bundle's fixed 64-hex generation at Build time:

```text
[Unit]
Description=Aether bounded OAS service
Requires=aether-oas-runtime.socket aether-oas-bootstrap.socket aether-oas-broker.socket
After=local-fs.target aether-oas-runtime.socket aether-oas-bootstrap.socket aether-oas-broker.socket
ConditionPathExists=/var/lib/aether/activation/activation-record.json
ConditionPathExists=/var/lib/aether/activation/unit-generations/g-<generation>.ready
AssertPathExists=/opt/aether/current
StartLimitIntervalSec=60s
StartLimitBurst=5
StartLimitAction=none

[Service]
Sockets=aether-oas-runtime.socket aether-oas-bootstrap.socket aether-oas-broker.socket
User=aether-oas
Group=aether-oas
SupplementaryGroups=
ExecStart=/opt/aether/current/runtime/bin/python -I -B -S -c 'import sys; sys.path.insert(0,"/opt/aether/current/runtime/lib/python3.11/site-packages"); from aether.oas.host_entrypoint import main; raise SystemExit(main())'
WorkingDirectory=/opt/aether/current
Environment=LANG=C.UTF-8
Environment=LC_ALL=C.UTF-8
Environment=TZ=UTC
Environment=HOME=/var/empty
UMask=0077
Type=notify
NotifyAccess=main
NoNewPrivileges=yes
PrivateTmp=yes
PrivateDevices=yes
ProtectSystem=strict
ProtectHome=yes
ReadOnlyPaths=/opt/aether /etc/aether/release-trust-anchor.pub
ReadWritePaths=/var/lib/aether/oas
RestrictAddressFamilies=AF_UNIX
RestrictSUIDSGID=yes
CapabilityBoundingSet=
AmbientCapabilities=
LockPersonality=yes
ProtectKernelTunables=yes
ProtectKernelModules=yes
ProtectKernelLogs=yes
ProtectControlGroups=yes
ProtectClock=yes
RestrictNamespaces=yes
RestrictRealtime=yes
SystemCallArchitectures=native
LimitCORE=0
LimitNOFILE=512
FileDescriptorStoreMax=0
TasksMax=128
MemoryMax=512M
CPUQuota=100%
Restart=on-failure
RestartSec=2s
TimeoutStartSec=30s
TimeoutStopSec=10s
StandardOutput=journal
StandardError=journal

[Install]
```

`[Install]` is explicitly empty. The service is not independently enabled:
the three socket units are the activation entrypoints and a root lifecycle
procedure starts/stops the complete socket transaction. No `WantedBy=` or
`Alias=` is generated, so an enable operation cannot create a partial-service
path.

There is no `EnvironmentFile`, `PassEnvironment`, Python hash-seed claim,
shell wrapper, root `ExecStartPre` mutation, `/var/log/aether` path, network
address family, writable release path, or optional hardening downgrade.

## 11. Root Installation, Migration, Rollback, and Recovery

### 11.1 Installation phases

The future installer is one fixed non-interpreting root procedure. It accepts a
verified bundle and one approved transaction record, never arbitrary commands,
paths, owners, modes, unit text, shell text, or cleanup instructions.

| Phase | Required action |
| --- | --- |
| 1 preflight | Lock, host identity, systemd policy, space, principals, parents, and current activation record |
| 2 trust verification | Verify anchor, fixed verifier, manifest envelope, approval, commit/tag/source digest, and bundle closure |
| 3 principal verification | Verify or create only missing exact target principals; never remap or delete existing identities |
| 4 object verification | Verify mounts, types, links, ownership, modes, and absence of unexpected objects |
| 5 candidate staging | Extract under root-only staging with traversal, duplicate, special-file, and size rejection |
| 6 file verification | Apply manifest-bound modes/ownership classes and verify every file hash |
| 7 activation record | Create `CANDIDATE_PENDING` with old/candidate identity, transaction, schema, expiry, and unit generation |
| 8 unit generation staging | Stage all four units and candidate generation metadata; no live unit replacement yet |
| 9 quiesce | Stop new admission, all three sockets, and OAS; wait for bounded M120A shutdown and prove process/connection/listener/job/worker/cgroup absence |
| 10 unit generation commit | Invalidate old gate only after quiescence, replace units one at a time, reload, verify effective properties, publish candidate gate |
| 11 candidate activation | Write `ACTIVATING`, atomically switch `current`, and start the complete socket transaction |
| 12 readiness | Observe main-process `READY=1` after all startup checks and exact descriptor validation |
| 13 smoke | Run only bounded PING/status and negative access checks; no Owner/auth/state mutation |
| 14 activation commit | Atomically replace record with `COMMITTED` candidate identity after readiness and smoke |
| 15 evidence | Retain record/generation/manifest/unit/process/quiesce evidence; remove only transaction staging |

The old release remains available through phase 13. Unit replacement is not
called atomic; the generation gate is the fail-closed barrier.

### 11.2 Migration and backup

Before schema-affecting work, root quiesces OAS, creates a protected consistent
SQLite backup under root-only mode `0700` staging, records schema, instance ID,
trust generation, committed release, manifest digest, ownership/modes, WAL/SHM
handling, and integrity evidence, then authorizes the candidate transaction.
WAL and SHM are checkpointed or included through SQLite's consistent backup
procedure; copying side files independently is invalid.

Forward migration is executed only by the fixed candidate OAS process as
`aether-oas` under `schema_compatibility=FORWARD_MIGRATION_REQUIRED`. It uses
the manifest-approved migration identity and marker, never arbitrary SQL,
caller paths, root SQL text, or ordinary runtime. `migration_state` is durable
and distinguishes `STARTED` from `COMMITTED`.

### 11.3 Failure and rollback rules

| Condition | Result |
| --- | --- |
| Signature, approval, manifest, source, file, principal, or path failure | Candidate staging is deleted; old committed identity remains |
| Unit replacement or reload failure | Generation gate remains absent; root restores the previous complete unit set before re-publishing its gate |
| Candidate readiness or smoke failure before migration commit | Record becomes `ROLLBACK_PENDING`; candidate stops; old link/generation is restored and reverified |
| Code rollback with unchanged schema | Allowed only after old release/key/unit/state identity passes current verification |
| Migration fails before commit | OAS transaction rolls back; backup is retained; old release/state remains |
| Migration commits and old release supports new schema | Code rollback may use old release after compatibility proof |
| Migration commits and old release does not support new schema | No automatic code rollback; service remains stopped in `RECOVERY_REQUIRED` |
| Unknown migration marker or partial observation | Preserve backup/evidence; no guessed retry or automatic restore |
| Revoked signing key on retained release | Release cannot activate or roll back; obtain a newly approved release |
| Power loss after record `COMMITTED` | Boot verifies the committed record and gate; failure leaves service unready for root recovery |
| Stale socket/process | Exact cgroup, inode, peer, and generation checks fail closed; no adoption |

Code rollback never automatically reverses canonical security state. Database
restore is a separate destructive-risk operation requiring explicit approval,
valid backup, schema/integrity proof, instance binding, trust-generation policy,
and an independently reviewed recovery procedure. At most three complete
releases are retained, and garbage collection never removes the active release,
rollback floor, open-recovery backup, canonical state, or audit evidence.

### 11.4 Disable, uninstall, and recovery

| Operation | Effect and preservation rule |
| --- | --- |
| Disable service | Stop/disable the three sockets; preserve releases, state, backups, principals, and evidence |
| Uninstall inactive code | Remove only verified inactive releases beyond retention; preserve state and trust generation |
| Remove units | Only after disabled and no pending transaction; preserve state and principals |
| Delete principals | Separate root-approved host lifecycle operation; not authorized here |
| Missing release provenance | Keep service stopped; restore a verified compatible release or reviewed recovery |
| Missing canonical state | Fail as `STATE_MISSING`; never create a new instance or trust root silently |
| Valid reinstall | Bind to existing `aether_instance_id` and trust generation after integrity proof |
| Clone/fork | New instance ID and Owner trust root; never reuse active authority |

## 12. Deployment Attestation and Verification Boundary

`DEPLOYMENT_VERIFIED` requires a reviewed evidence bundle tied to one host, one
committed activation record, one manifest, and one evidence time. The following
evidence is mandatory:

| Evidence class | Required evidence |
| --- | --- |
| Host | Host identity, OS, architecture, kernel, boot ID, timestamp, collector |
| Systemd | Exact version, PID 1, effective unit bytes/properties, dependencies, conditions, and `systemctl cat` |
| Trust | Anchor fingerprint, fixed verifier hash, OpenSSL version/hash, key statuses, envelope and approval results |
| Release | Manifest, detached envelope, source commit/tag/tree digest, dependency lock, release ID |
| Files | Every release/unit/gate/record hash, type, owner, mode, link, mount, and unexpected-object scan |
| Runtime | Interpreter inode/version/ABI/hash, exact import roots, environment allowlist, module path, no user/system site |
| Principals | All five UID/GID/shell/home/group and collision facts |
| State | Activation record, current link, OAS database/WAL/SHM, schema, generation, backup, rollback evidence |
| Sockets | Actual AF_UNIX/SOCK_SEQPACKET type, paths, modes, inode identity, descriptor names/order, peer credentials |
| Process | UID/GID/groups, command line, cgroup, working directory, capabilities, resource limits |
| Access | Negative `aether-runtime` reads/writes/mutations for code, units, state, sockets, accounts, backups, and manager |
| Readiness | Real main-process systemd notify after all checks, timing, failures, and timeout evidence |
| Lifecycle | Failed readiness, unchanged-schema rollback, migration, power-loss/generation gate, stale-object, and retention drills |
| Logging | Secret-free journal, bounded classifications, restart throttling, no private material |
| Review | Evidence validity window, reviewer, limitations, and explicit static/isolated/host distinction |

Static tests, local builds, unit parsing, isolated socket tests, source hashes,
and test-double readiness can establish `TEST_VERIFIED` only. They cannot
establish `DEPLOYMENT_VERIFIED`.

## 13. Threat Model and Fail-Closed Results

| Threat | Prevention/detection | Result |
| --- | --- | --- |
| Circular pending activation | Single record, explicit pending state, candidate identity, expiry, commit-after-smoke | Reject startup or recover; never infer committed identity |
| Replayed activation record | Sequence, previous digest, transaction, boot ID, expiry, exact candidate/unit/state bindings | Fail closed |
| Simultaneous transactions | Root lock and record transaction identity | Second transaction rejected |
| Mixed unit generation | Invalidate old gate before individual replacements; generation-specific Conditions | No socket or service activation |
| Unspecified FD order | Explicit service `Sockets=` list and M120A name/FD checks | Reject missing, extra, reordered, or substituted descriptors |
| Stale or revoked signing key | Anchor status/validity/revocation and fixed verifier | Candidate and rollback rejected |
| Target private key exposure | Offline custody; no private material in bundle, host, backup, log, env, or OAS | Signing cannot occur on target |
| Import-path substitution | `-I -B -S`, fixed release insertion, manifest module hash, no checkout/user/system site | Startup fails closed |
| Environment injection | Exact allowlist and fixed-value validation before import | Startup fails closed |
| Service state write abuse | Separate UID, state directory 0700, one write path, systemd `ReadWritePaths` | Access denied and evidence fails |
| Root/kernel/systemd compromise | Explicit host trust-base assumption | Not claimed prevented |
| False readiness | Main-process native notify only after record, release, unit, state, descriptor, and migration checks | No readiness claim |
| Resource exhaustion | 32 active/64 queued admission, 512 FD limit, TasksMax/memory/CPU ceilings | Bounded rejection or failed service |
| Restart storm | 5 starts per 60 seconds, `StartLimitAction=none` | Failed state; no fallback |
| Worker beyond shutdown budget | Tracked outstanding work and no clean-stop claim | Candidate cannot commit; systemd may bound termination |
| Backup disclosure | Root-only mode 0700 staging and no runtime path | Evidence failure and no claim |
| State rollback corruption | Forward-only schema policy, backup, migration marker, no automatic destructive restore | Recovery required |
| Development checkout substitution | Signed source/tree identity and release-only import root | Staging/readiness rejection |

## 14. Future Repository Build Boundary

`EXIT_A` is not permission to implement. The future repository deployment-artifact
Build inventory is precise and remains a separate PM decision.

| Category | Proposed path | Required artifact/test |
| --- | --- | --- |
| Production OAS entrypoint | `aether/oas/host_entrypoint.py` | Fixed record/generation/state/descriptor startup; `tests/test_oas_host_entrypoint.py` |
| Native systemd notification | `aether/oas/systemd_notify.py` | Direct `NOTIFY_SOCKET` datagram and failure tests; `tests/test_oas_systemd_notify.py` |
| Manifest schema | `aether/deployment/manifest_schema.py` | Canonical fields, types, hashes, and compatibility tests |
| Manifest generator | `aether/deployment/manifest_generator.py` | Reproducible source/file/unit/dependency manifest tests |
| Release verifier | `aether/deployment/release_verifier.py` plus host `/usr/libexec/aether-release-verify` | Fixed OpenSSL Ed25519 envelope/anchor verification tests |
| Dependency lock/wheelhouse | `deployment/requirements.lock.json` and `deployment/wheelhouse/` | Complete transitive hashes, markers, platform artifacts, offline install tests |
| Four units | `deployment/systemd/aether-oas.service`, `aether-oas-runtime.socket`, `aether-oas-bootstrap.socket`, `aether-oas-broker.socket` | Byte/hash/order/`systemd-analyze verify` tests |
| Fixed installer | `aether/deployment/installer.py` | Lock, record, fsync, generation gate, staged replacement, recovery tests |
| Lifecycle/rollback tool | `aether/deployment/lifecycle.py` | First install, upgrade, migration, rollback, power-loss state-machine tests |
| Offline unit verifier | `aether/deployment/unit_verifier.py` | Effective-property and generation-bundle tests |
| Evidence collector | `aether/deployment/evidence_collector.py` | Host-bound redacted evidence schema and completeness tests |
| Artifact-specific tests | `tests/test_m121a_*` and named tests above | Static, isolated, failure-injection, and negative-access coverage |

The future work is staged:

| Stage | Scope | Authorization boundary |
| --- | --- | --- |
| Build stage | Repository release code, manifest, lock/wheelhouse, verifier, four units, installer, lifecycle tool, and tests | Separate PM-approved repository Build; no host mutation |
| Isolated proof stage | Temporary non-production root, fake principals, unit parser, release verification, failure and power-loss simulation | Separate review; no production state or host service |
| Target deployment stage | One separately authorized root deployment to one reviewed host with full evidence | Not authorized by M121A |
| Deployment review stage | PM review of host-bound evidence before any deployment claim | Required before `DEPLOYMENT_VERIFIED` |

No automatic sequence combines repository Build with live root deployment.

## 15. Exclusions, Status, and Stop Boundary

M121A does not:

- update `PROGRESS.md`;
- update `SECURITY_ARCHITECTURE.md`;
- modify production code or existing tests;
- create units, an installer, an entrypoint, a release bundle, a manifest, a verifier, or a rollback tool;
- install dependencies or packages;
- create or modify users, groups, permissions, mounts, services, sockets, or host configuration;
- implement Owner authentication, WebAuthn, TLS, sessions, Claim, recovery, PAM, or the Owner broker;
- issue `AuthenticatedSourceEvent` or integrate Core receipts/Goal operations;
- introduce Generic Act, generalized Tool-Operation-Capability authority, public Internet, multi-instance runtime, or multi-agent runtime;
- claim a read-only mount, live principal, live unit, readiness, or deployment verification;
- commit, tag, push, or modify any Git reference; or
- authorize or number a successor milestone.

There is exactly one authoritative M121A status block:

```text
AUTHORITATIVE_M121A_STATUS_BEGIN
M121A_SECOND_CORRECTIVE_PASS_COMPLETE: YES
M121A_CORRECTIVE_PASS_COMPLETE: YES
M121A_AUTHORIZED: YES
M121A_STARTED: YES
M121A_FINALIZED: NO
DECISION_STATUS: CURRENT
DESIGN_STATUS: DESIGN_PROVEN
IMPLEMENTATION_STATUS: NOT_IMPLEMENTED
VERIFICATION_STATUS: TEST_VERIFIED
DEPLOYMENT_VERIFIED: NO
SELECTED_EXIT: EXIT_A
BUILD_AUTHORIZED: NO
HOST_MUTATION_PERFORMED: NO
PROGRESS_UPDATED: NO
SECURITY_ARCHITECTURE_UPDATED: NO
COMMIT_CREATED: NO
TAG_CREATED: NO
PUSH_PERFORMED: NO
SUCCESSOR_AUTHORIZED: NO
SUCCESSOR_NUMBER_ASSIGNED: NO
READY_FOR_PM_REVIEW: YES
AUTHORITATIVE_M121A_STATUS_END
```

`EXIT_A` means the corrected design gates are closed and a future repository
deployment-artifact Build may be considered in a separate PM decision. It does
not mean implementation, build authorization, host deployment, readiness, or
deployment verification. The corrective stop boundary is reached after this
document, its static proof, and the corrected external summary are written and
the required validations pass. The next action is another PM hard-gate review.
