# Milestone 123A OAS Final Targeted Readiness Classification and Non-Mutating Rehearsal Proof

Document role: CORRECTIVE DISCOVERY / READINESS / NON-MUTATING REHEARSAL PROOF ONLY.

This final targeted correction is subordinate to `CONSTITUTION > ARCHITECTURE >
SECURITY_ARCHITECTURE > CURRENT IMPLEMENTATION`. M121A remains the deployment
contract and M122A remains the finalized repository deployment-artifact
foundation. This record does not authorize finalization, live deployment, host
mutation, or deployment verification.

## 1. Preserved Scope and Baseline

The verified baseline is:

```text
d209aa7a4854bcc1daa5e2dd22e34e9ae9c2f089
```

Only these two repository artifacts are modified by this corrective pass:

```text
docs/architecture/MILESTONE_123A_OAS_TARGET_HOST_DEPLOYMENT_READINESS_AND_NON_MUTATING_REHEARSAL_PROOF.md
tests/test_milestone_123a_oas_target_host_deployment_readiness_and_non_mutating_rehearsAL_PROOF.py
```

`PROGRESS.md`, `README.md`, `CONSTITUTION.md`, `ARCHITECTURE.md`,
`SECURITY_ARCHITECTURE.md`, M119A-M122A records, production implementation,
deployment artifacts, dependencies, and Git references are protected. No
production path was selected for writing. No user, group, unit, release,
socket, process, package, credential, key, token, or service-manager state was
created or changed.

The requested M120A architecture record is absent from the checkout. The
finalized M120A implementation and static-test sources, together with the
M120A finalization summary, are the available evidence. No missing authority
record is invented.

## 2. Corrected Readiness Model

The prior record incorrectly treated absent deployment outputs as failed host
compatibility and treated deployment-time observations as current host blockers.
These dimensions are independent:

| Dimension | Exact meaning |
| --- | --- |
| `HOST_COMPATIBILITY` | Can this host support the finalized deployment contract, based on checks actually run? |
| `DEPLOYMENT_STATE` | Is OAS already installed and active? |
| `TARGET_HOST_READY_FOR_CONTROLLED_DEPLOYMENT_REVIEW` | Are unresolved host blockers absent such that PM could consider a separately authorized deployment transaction? |
| `DEPLOYMENT_VERIFIED` | Has a real deployment completed with reviewed host-bound evidence? |

Missing principals, units, release directories, activation records, sockets,
and the state database are classified as `EXPECTED_DEPLOYMENT_OUTPUT`. They
therefore imply `DEPLOYMENT_STATE: NOT_DEPLOYED`, not automatic host
incompatibility. They are not created during M123A.

The classification vocabulary is exact:

```text
EXPECTED_DEPLOYMENT_OUTPUT
REQUIRED_PREEXISTING_HOST_PREREQUISITE
CORRECTABLE_HOST_BLOCKER
STRUCTURAL_HOST_BLOCKER
DEPLOYMENT_TIME_VERIFICATION_CONDITION
OPTIONAL_DEFENSE_IN_DEPTH
OUT_OF_SCOPE_FOR_BOUNDED_FIRST_INSTALL
```

`EXIT_A_TARGET_READY_FOR_BOUNDED_FIRST_INSTALL_DEPLOYMENT_REVIEW` is reserved
for this bounded profile when required preexisting prerequisites pass, the
repository deployment artifacts prove the AF_UNIX-only contract, and no
structural or correctable blocker is present. `EXIT_B_HOST_READINESS_GAPS_REQUIRE_CORRECTION`
records an actual correctable prerequisite or insufficient profile evidence.
`EXIT_C_NO_SAFE_DEPLOYMENT_JUSTIFIED` is reserved for structural
incompatibility or an unacceptable security boundary; it is not selected merely
because the host is not deployed.

### Bounded profile

The sole M123A decision profile is:

```text
FIRST_INSTALL_LOCAL_AF_UNIX_ONLY
```

It covers an empty target namespace, one verified candidate release, three
pathname `AF_UNIX` `SOCK_SEQPACKET` endpoints, a separate `aether-oas`
principal, readiness and smoke gates, and a root-reviewed commit boundary. The
finalized unit artifacts directly prove `ListenSequentialPacket=` only,
`RestrictAddressFamilies=AF_UNIX`, and no TCP/IP listener. This is local IPC
containment proof, not proof of a deployed service.

Normal upgrade, schema migration, adoption of preexisting state, automated
recovery, and upgrade rollback are explicitly:

```text
OUT_OF_SCOPE_FOR_BOUNDED_FIRST_INSTALL
```

They are not exercised as successful lifecycle claims. Unsupported or
ambiguous inputs fail closed, remain unchanged, or require root review where
the finalized API does not expose an operation. No first-install rehearsal
silently substitutes a network-facing service or a prior-release lifecycle.

## 3. Privacy-Preserving Target Identity

The candidate is the bounded current execution environment. Raw identifying
values are not retained. The target identity is:

```text
TARGET_HOST_IDENTITY_DIGEST: 0af7fb998d39865964b44cf711843553575c6628565cf05be836c8da90246b1e
OBSERVATION_BOOT_DIGEST: 6d686112ab2bced110665bbb3eb2355a3c1e8fbae9b3e313ab563851d8725679
OBSERVATION_TIME_UTC: 2026-09-02T04:54:55+00:00
OBSERVATION_DIGEST: cadad1b1df4e3b842565790a61b5c9b0ced629937e854bf7429852405eb9a900
```

The exact canonicalization is UTF-8 JSON with lexicographically sorted object
keys, `separators=(',', ':')`, `ensure_ascii=true`, finite values only, and no
trailing newline, using the repository `canonical_json_bytes` implementation.
Domain-separated digests are exactly:

```text
H(domain, value) = SHA256(ASCII(domain) || 0x00 || canonical_json_bytes(value))
machine ID domain = aether.m123a.machine-id.v1
boot ID domain = aether.m123a.observation-boot.v1
target domain = aether.m123a.target-host-identity.v1
observation domain = aether.m123a.target-host-observation.v1
root device domain = aether.m123a.root-device.v1
```

The canonical stable target facts bind only the digest of `/etc/machine-id`,
OS ID/version/codename, architecture, systemd version and PID-1 comm, and a
digest of the root filesystem device plus root filesystem type. The observation
payload binds the target digest, the boot-ID digest, and the UTC observation
time. The raw machine ID and boot ID are never stored in the document,
summary, or test evidence. Repeating the same facts produces the same target
digest; changing architecture changes it. Changing only boot ID changes the
observation digest and does not change the target digest.

## 4. Complete Read-Only Preflight

Every required check was executed or explicitly classified. The only statuses
used are `PASS`, `FAIL`, `NOT_PRESENT`, `NOT_PROVEN`, and `NOT_APPLICABLE`.
`NOT_PROVEN` is not treated as `PASS`.

| Check | Status | Classification | Observed bounded result |
| --- | --- | --- | --- |
| `distribution_version` | PASS | REQUIRED_PREEXISTING_HOST_PREREQUISITE | Debian GNU/Linux 12 |
| `kernel_architecture` | PASS | REQUIRED_PREEXISTING_HOST_PREREQUISITE | Linux x86_64 |
| `systemd_pid1_identity` | PASS | REQUIRED_PREEXISTING_HOST_PREREQUISITE | systemd 252.39, PID 1, running |
| `cgroup_version` | PASS | REQUIRED_PREEXISTING_HOST_PREREQUISITE | cgroup v2 interface present |
| `python_311_runtime` | PASS | REQUIRED_PREEXISTING_HOST_PREREQUISITE | `/usr/bin/python3.11`, Python 3.11.2, cpython-311, `-I -S` probe passed |
| `openssl_ed25519_pkeyutl` | PASS | REQUIRED_PREEXISTING_HOST_PREREQUISITE | OpenSSL 3.0.20, ephemeral Ed25519 sign/verify passed |
| `clock_utc_approval_window` | PASS | REQUIRED_PREEXISTING_HOST_PREREQUISITE | UTC conversion and 60-second bounded window probe passed |
| `timezone` | PASS | REQUIRED_PREEXISTING_HOST_PREREQUISITE | effective timezone UTC |
| `disk_capacity` | PASS | REQUIRED_PREEXISTING_HOST_PREREQUISITE | available blocks positive; exact capacity not retained |
| `inode_capacity` | PASS | REQUIRED_PREEXISTING_HOST_PREREQUISITE | available inodes positive; exact capacity not retained |
| `selinux_status` | NOT_PRESENT | OPTIONAL_DEFENSE_IN_DEPTH | SELinux interface absent; not required by the bounded AF_UNIX-only contract |
| `apparmor_status` | NOT_PRESENT | OPTIONAL_DEFENSE_IN_DEPTH | AppArmor profile interface absent; not required by the bounded AF_UNIX-only contract |
| `effective_systemd_security_policy` | NOT_PROVEN | DEPLOYMENT_TIME_VERIFICATION_CONDITION | target units are absent; effective deployed properties must be verified during a future authorized deployment |
| `uid_gid_separation` | PASS | REQUIRED_PREEXISTING_HOST_PREREQUISITE | POSIX identity primitives and `setpriv` available |
| `principal_name_numeric_conflicts` | PASS | REQUIRED_PREEXISTING_HOST_PREREQUISITE | target names and required runtime/OAS numeric IDs have no conflicts |
| `linux_capability_support` | PASS | REQUIRED_PREEXISTING_HOST_PREREQUISITE | `/proc/self/status` and capability tooling available |
| `systemd_sandbox_directives` | PASS | REQUIRED_PREEXISTING_HOST_PREREQUISITE | isolated `systemd-analyze verify` accepted the finalized directives |
| `af_unix` | PASS | REQUIRED_PREEXISTING_HOST_PREREQUISITE | AF_UNIX socket creation passed |
| `sock_seqpacket` | PASS | REQUIRED_PREEXISTING_HOST_PREREQUISITE | AF_UNIX SOCK_SEQPACKET creation passed |
| `so_peercred` | PASS | REQUIRED_PREEXISTING_HOST_PREREQUISITE | SO_PEERCRED socketpair probe passed |
| `socket_activation` | PASS | REQUIRED_PREEXISTING_HOST_PREREQUISITE | systemd and ordered socket contract statically verified |
| `sd_notify` | PASS | REQUIRED_PREEXISTING_HOST_PREREQUISITE | native UNIX datagram `READY=1` probe passed |
| `pathname_abstract_socket` | PASS | REQUIRED_PREEXISTING_HOST_PREREQUISITE | pathname and abstract AF_UNIX probes passed |
| `parent_ownership_modes` | PASS | REQUIRED_PREEXISTING_HOST_PREREQUISITE | required parents root-owned mode 0755 |
| `symlink_conflicts` | PASS | REQUIRED_PREEXISTING_HOST_PREREQUISITE | no symlink conflict at selected deployment roots |
| `mount_types_flags` | PASS | REQUIRED_PREEXISTING_HOST_PREREQUISITE | `/proc/self/mountinfo` root and `/run` records observable; no read-only claim made |
| `executable_bit_preservation` | PASS | REQUIRED_PREEXISTING_HOST_PREREQUISITE | fixed verifier source mode 0555 |
| `atomic_rename` | PASS | REQUIRED_PREEXISTING_HOST_PREREQUISITE | temporary-root rename probe passed |
| `hard_link_publication` | PASS | REQUIRED_PREEXISTING_HOST_PREREQUISITE | temporary-root hard-link publication probe passed |
| `directory_fsync` | PASS | REQUIRED_PREEXISTING_HOST_PREREQUISITE | temporary-root directory fsync probe passed |
| `file_fsync` | PASS | REQUIRED_PREEXISTING_HOST_PREREQUISITE | temporary-root file fsync probe passed |
| `sqlite_wal_locking` | PASS | REQUIRED_PREEXISTING_HOST_PREREQUISITE | WAL mode and competing writer lock probe passed |
| `rollback_storage_capacity` | PASS | REQUIRED_PREEXISTING_HOST_PREREQUISITE | available rollback storage blocks positive |
| `private_lan_containment` | PASS | REQUIRED_PREEXISTING_HOST_PREREQUISITE | bounded profile has only repository-proven AF_UNIX endpoints and no IP listener |
| `profile_artifact_af_unix_only` | PASS | REQUIRED_PREEXISTING_HOST_PREREQUISITE | all three socket units use ListenSequentialPacket and service restricts families to AF_UNIX |
| `public_exposure_requirement` | PASS | REQUIRED_PREEXISTING_HOST_PREREQUISITE | M123A requires no public exposure |
| `dns_tls_scope` | NOT_APPLICABLE | REQUIRED_PREEXISTING_HOST_PREREQUISITE | DNS/TLS are outside M123A and are not assumed |
| `conflicting_production_listener` | PASS | REQUIRED_PREEXISTING_HOST_PREREQUISITE | no selected OAS UNIX listener present |
| `existing_principals` | NOT_PRESENT | EXPECTED_DEPLOYMENT_OUTPUT | all four target names absent |
| `existing_units` | NOT_PRESENT | EXPECTED_DEPLOYMENT_OUTPUT | all four OAS units absent |
| `existing_release_paths` | NOT_PRESENT | EXPECTED_DEPLOYMENT_OUTPUT | `/opt/aether` release namespace absent |
| `existing_sockets` | NOT_PRESENT | EXPECTED_DEPLOYMENT_OUTPUT | `/run/aether/oas` absent |
| `existing_processes` | NOT_PRESENT | EXPECTED_DEPLOYMENT_OUTPUT | no OAS process present |
| `existing_activation_record` | NOT_PRESENT | EXPECTED_DEPLOYMENT_OUTPUT | activation record absent |
| `existing_state_database` | NOT_PRESENT | EXPECTED_DEPLOYMENT_OUTPUT | OAS SQLite state absent |

The absent deployment namespace is expected output, not a host blocker:

| Missing item | Classification | Deployment-state meaning |
| --- | --- | --- |
| `aether-owner/aether-runtime/aether-oas/aether-bootstrap` | EXPECTED_DEPLOYMENT_OUTPUT | target principals not deployed |
| `aether-oas.service` and three socket units | EXPECTED_DEPLOYMENT_OUTPUT | target units not deployed |
| `/opt/aether/releases` and `/opt/aether/current` | EXPECTED_DEPLOYMENT_OUTPUT | target release not deployed |
| `/var/lib/aether/activation/activation-record.json` | EXPECTED_DEPLOYMENT_OUTPUT | target activation state not deployed |
| `/run/aether/oas` and its sockets | EXPECTED_DEPLOYMENT_OUTPUT | target IPC endpoints not deployed |
| `/var/lib/aether/oas/security_kernel.sqlite3` | EXPECTED_DEPLOYMENT_OUTPUT | target OAS state not deployed |

No `STRUCTURAL_HOST_BLOCKER` or `CORRECTABLE_HOST_BLOCKER` was observed for the
bounded profile. The absent SELinux interface is not required by this profile;
the absent AppArmor interface is `OPTIONAL_DEFENSE_IN_DEPTH`. Effective
systemd properties are a `DEPLOYMENT_TIME_VERIFICATION_CONDITION`, not current
host incompatibility. The correct result is `HOST_COMPATIBILITY: PASSED` for
the bounded profile while `DEPLOYMENT_STATE` remains `NOT_DEPLOYED`.

## 5. Isolated Rehearsal Matrix

Each in-scope row is exercised by the M123A behavioral lock or by the retained
M122A trust lock. Every case is bounded to a fresh temporary root. Excluded
rows are classification boundaries, not upgrade or migration rehearsals. A
rejected result means the starting state/evidence remains unchanged and the
forbidden action is not silently inferred.

| Case | Starting state | Resulting state/result | Forbidden transition or failure | Evidence/recovery boundary |
| --- | --- | --- | --- | --- |
| `first_install` | `CANDIDATE_PENDING` | `ACTIVATING` then `COMMITTED` after readiness and smoke | direct commit before readiness/smoke rejected | generation gate and temporary `current`; root-only |
| `excluded_normal_upgrade` | `FIRST_INSTALL_LOCAL_AF_UNIX_ONLY` | `NOT_ATTEMPTED` | upgrade is outside bounded profile | no upgrade mutation |
| `excluded_schema_migration` | `FIRST_INSTALL_LOCAL_AF_UNIX_ONLY` | `NOT_ATTEMPTED` | schema migration is outside bounded profile | incompatibility fails closed |
| `excluded_adoption` | `FIRST_INSTALL_LOCAL_AF_UNIX_ONLY` | `NOT_ATTEMPTED` | adoption of existing state is outside bounded profile | empty-state gate; no adoption |
| `excluded_automated_recovery` | ambiguous or interrupted state | `REJECTED_OR_ROOT_REVIEW` | automated recovery/guessing | no automatic repair |
| `excluded_upgrade_rollback` | `FIRST_INSTALL_LOCAL_AF_UNIX_ONLY` | `NOT_ATTEMPTED` | upgrade rollback is outside bounded profile | unknown release fails closed; no rollback mutation |
| `complete_signed_release_trust` | no pending record | verified trust result | invalid signature/input rejected | complete signed fixture; no host paths |
| `trust_evidence_before_pending` | no pending record | immutable evidence then `CANDIDATE_PENDING` | pending record before trust publication forbidden | evidence preserved and retry-idempotent |
| `quiescence` | `CANDIDATE_PENDING` | typed quiescence proof | unbound/stale proof rejected | transaction, boot, adapter and time bound |
| `activating` | `QUIESCE_REQUIRED` | `ACTIVATING` | activation without proven quiescence rejected | generation/current switch remains isolated |
| `ready_smoke_guard` | `ACTIVATING` | commit only when both pass | missing readiness or smoke rejects commit | activation record unchanged |
| `committed` | `ACTIVATING` with both pass | `COMMITTED` | no direct commit shortcut | commit state set only by transition |
| `verification_failure_before_pending` | no pending record | failure; no pending record | unverified release cannot enter pending | no evidence/record promotion |
| `crash_after_evidence_before_pending` | no pending record | durable evidence; no pending record | interrupted record write cannot promote state | retry uses preserved evidence |
| `quiescence_failure` | `CANDIDATE_PENDING` | failure; unchanged pending state | active service/socket/work rejects proof | no unit directory mutation |
| `unit_generation_mismatch` | `CANDIDATE_PENDING` | failure; unchanged state | candidate generation mismatch rejects replacement | no unit directory mutation |
| `dependency_mismatch` | signed candidate before pending | failure; no pending record | lock/wheel mismatch rejects trust | prior evidence/record preserved |
| `link_switch_before_readiness_failure` | `ACTIVATING` | commit rejected; `ROLLBACK_PENDING` allowed | readiness cannot be inferred from link | temporary link remains bounded |
| `readiness_timeout` | activation window | invalid window; no commit | expired deadline rejects activation | no deadline extension |
| `smoke_failure` | `ACTIVATING` with readiness only | commit rejected | failed smoke rejects commit | state remains uncommitted |
| `schema_incompatibility` | activation with incompatible schema marker | state validation rejected | incompatible schema cannot be accepted | recovery requires root review |
| `rollback_release_mismatch` | candidate link active | restore rejected | unknown release cannot replace current link | current link unchanged |
| `stale_activation` | expired activation window | invalid | stale window rejected | no automatic retry |
| `wrong_boot_identity` | valid activation window | invalid | boot mismatch rejected | no activation promotion |
| `expired_activation_window` | valid activation window | invalid at deadline | deadline boundary rejected | monotonic authority only |

The finalized M122A APIs do not expose a complete automatic `RECOVERY_REQUIRED`
transition or a dedicated schema-migration rollback operation. The lock proves
those paths fail closed rather than pretending they are complete. They remain
outside the bounded first-install profile and do not prevent the bounded
isolated result from being `PASSED`.

## 6. Bounded Non-Mutation Proof

Before and after the host inspection/rehearsal, the lock captures only bounded
metadata for these selected paths:

```text
/etc/aether
/etc/systemd/system
/usr/libexec
/opt/aether
/var/lib/aether
/run/aether
```

For each selected path it compares existence, file type, owner, group, mode,
size, timestamp, and direct child-name set. It also compares the selected OAS
unit manager observations, target principal absence, selected OAS socket
presence, and OAS process count. No file contents or secret-bearing data are
read for this snapshot. The behavioral lock proves equality before and after:

```text
new selected path: none
selected metadata/content boundary changed: no
service-manager mutation: no
principal created: no
listener started: no
OAS production process launched: no
```

This is a bounded observed-path result. It is not an absolute claim about every
byte or process on the host. Temporary-root files created by the rehearsal are
outside the repository and selected production paths and are removed with the
pytest temporary-root lifecycle.

## 7. Validation Evidence

The final targeted M123A lock is
`tests/test_milestone_123a_oas_target_host_deployment_readiness_and_non_mutating_rehearsAL_PROOF.py`.
The complete signed M122A trust transaction and all deployment/OAS focused
tests were run. The full repository suite was mandatory and passed:

```text
final targeted M123A lock: 13 passed
M119A lock: 15 passed
M120A lock: 45 passed
M121A lock: 13 passed
M122A lock: 9 passed
deployment and OAS focused tests: 109 passed
complete repository suite: 3569 passed, 10 warnings, 0 failed, 0 skipped, 0 xfailed
Python compilation: passed
dependency closure verification: passed in the M122A trust matrix
isolated-root systemd-analyze verify: exit 0
git diff --check: passed
conflict-marker and whitespace checks: passed
```

The 10 warnings are existing dependency/test-framework warnings. No test result
is live deployment evidence.

## 8. Authoritative Status

The M123A static lock extracts the single bounded block between the two status
markers, parses every non-marker line as one `KEY: VALUE` entry, rejects
duplicate keys and duplicate marker pairs, and compares the complete mapping to
the canonical schema. It therefore rejects missing keys, unexpected keys,
obsolete aliases, duplicate fields, and conflicting values; it does not accept
marker or field substrings found elsewhere in this document. `TEST_VERIFIED`
and `DEPLOYMENT_VERIFIED` are separate fields, with deployment verification
remaining `NO`.

```text
AUTHORITATIVE_M123A_STATUS_BEGIN
M123A_AUTHORIZED: YES
M123A_STARTED: YES
M123A_FINALIZED: YES
DECISION_STATUS: CURRENT
DESIGN_STATUS: DESIGN_PROVEN
IMPLEMENTATION_STATUS: IMPLEMENTED
VERIFICATION_STATUS: TEST_VERIFIED
DEPLOYMENT_VERIFIED: NO
DEPLOYMENT_STATE: NOT_DEPLOYED
DEPLOYMENT_PROFILE: FIRST_INSTALL_LOCAL_AF_UNIX_ONLY
HOST_COMPATIBILITY: PASSED
ISOLATED_REHEARSAL: PASSED
TARGET_HOST_READY_FOR_CONTROLLED_DEPLOYMENT_REVIEW: YES
SELECTED_EXIT: EXIT_A_TARGET_READY_FOR_BOUNDED_FIRST_INSTALL_DEPLOYMENT_REVIEW
BUILD_AUTHORIZED: NO
LIVE_DEPLOYMENT_AUTHORIZED: NO
UPGRADE_AUTHORIZED: NO
SCHEMA_MIGRATION_AUTHORIZED: NO
PUBLIC_EXPOSURE_AUTHORIZED: NO
ADOPTION_AUTHORIZED: NO
AUTOMATED_RECOVERY_AUTHORIZED: NO
UPGRADE_ROLLBACK_AUTHORIZED: NO
HOST_MUTATION_PERFORMED: NO
PROGRESS_UPDATED: YES
COMMIT_CREATED: YES
TAG_CREATED: YES
PUSH_PERFORMED: YES
SUCCESSOR_AUTHORIZED: NO
SUCCESSOR_NUMBER_ASSIGNED: NO
READY_FOR_PM_REVIEW: NO
AUTHORITATIVE_M123A_STATUS_END
```

`EXIT_A_TARGET_READY_FOR_BOUNDED_FIRST_INSTALL_DEPLOYMENT_REVIEW` is selected
for the `FIRST_INSTALL_LOCAL_AF_UNIX_ONLY` profile. Required preexisting host
prerequisites pass, the finalized repository artifacts prove the AF_UNIX-only
local IPC boundary, and no structural or correctable blocker was observed.
Effective systemd properties remain a deployment-time verification condition;
SELinux/AppArmor are optional defense-in-depth and are not required by this
profile. Upgrade, migration, adoption, automated recovery, and upgrade rollback
remain explicitly out of scope. A separately authorized deployment remains
prohibited by this record.
