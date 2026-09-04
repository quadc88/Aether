# M128A Privileged Host Trust-Bootstrap Runner, Process-Recovery, and Exact-Root Authority Contract Proof

Document role: DESIGN / DISCOVERY / SECURITY / OPERATIONS CONTRACT PROOF ONLY.

M128A is finalized as design/discovery/security-and-operations contract proof
only. It does not
implement a runner or admitter, create an inbox or service, provision trust
material, access a production key, install a host trust object, mutate a target
host, deploy OAS, or authorize a successor. It is subordinate to:

```text
CONSTITUTION > ARCHITECTURE > SECURITY_ARCHITECTURE > CURRENT MILESTONE AUTHORIZATION > CURRENT IMPLEMENTATION
```

Aether remains one persistent digital mind. AetherOS is its operating
environment and body. This record defines an OS boundary; it does not create a
second mind, agent, cognitive runtime, or Generic Act authority.

## 1. Purpose, Lineage, and Boundary

M127A proves an authenticated, durable host trust-bootstrap transaction inside
an explicitly issued temporary isolated root. Its `TemporaryRootCapability` is
process-bound and cannot be serialized or reconstructed by a later process.
M128A defines the missing real-host contract: complete evidence carriage,
privilege-separated admission, a kernel-attested initial host mount namespace,
exact fixed-path access, SQLite-only durable state, exact five-object publication,
and conservative process/reboot recovery.

The layered relationship is preserved:

| Milestone | Preserved contribution | M128A relationship |
| --- | --- | --- |
| M117A | One Aether Instance, one true Owner, separate local presence and Owner channel, and source/authentication/intent separation | Runner is not Owner, Aether, or intent interpreter |
| M118A | Bounded SQLite state, canonical request/audit digests, replay/conflict/idempotency, and state-plus-audit atomicity | SQLite discipline is reused without expanding OAS authority |
| M119A | Separate principals, root-owned launcher/broker, restricted IPC, fresh local presence, and no runtime inheritance | Runner and admitter are separate OS boundaries |
| M120A | Exact bounded AF_UNIX framing, peer checks, descriptors, deadlines, and fail-closed operation vocabulary | M128A has no client mutation socket |
| M121A | Root-owned release identity, exact verifier/trust root, activation records, boot-bound windows, and non-atomic multi-object recovery | Runner is a separate prerequisite boundary |
| M122A | Immutable repository artifact identity, fixed verifier separation, and capability-bound installation | M128A carries exact bytes, not caller-selected paths |
| M123A | Read-only target identity and non-mutating rehearsal | Host proof remains separate from readiness |
| M124A | Exact deployment packet, Owner activation boundary, five fixed objects, and ordered first-install mutation | M128A consumes trust-bootstrap authorization, not deployment authorization |
| M125A | Durable rollback evidence and no-guessing recovery semantics | The same evidence discipline applies to ingress and host recovery |
| M126A | Separate host-bootstrap authority, OS/image baseline root, authenticated envelope, local-console and governance evidence | M128A consumes complete raw records without reissuing them |
| M127A | Exact five-object publication, generation reservations, terminal Observation/Verification, and process-local capability boundary | M128A supplies the OS process, bytes, and recovery contract |

The current repository has no M128A production implementation. Standalone M118A
and M120A architecture records are absent from the checkout; their finalized
implementation/static tests and the canonical Security Architecture are the
available evidence. No missing record is invented.

## 2. Authority, Status, and Preserved Governance

Milestone records are immutable historical evidence and traceability records,
not an authority level. `SECURITY_ARCHITECTURE.md` remains canonical for the
security domain and subordinate to the Constitution and Architecture. Static
and test evidence is not live deployment evidence.

The preserved authority equations are:

```text
AUTHENTICATION != INTENT_INTERPRETATION
GOAL_ACCEPTANCE != ACTION_AUTHORIZATION
ACTION_SUCCESS != COMPLETION
COMPLETION REQUIRES OBSERVATION AND VERIFICATION
```

The target execution loop remains:

```text
Receive -> Understand -> Think -> Plan -> Act -> Observe -> Verify -> Critic -> Repair -> Learn -> Report
```

`TEST_VERIFIED` means only that the static lock verifies this document and
protected historical artifacts. It does not mean that any future component,
unit, inbox, namespace, host root, trust object, or deployment exists.

## 3. Selected Evidence-Carriage Model

Exactly one evidence-carriage model is selected:

```text
SELECTED_EVIDENCE_CARRIAGE_MODEL: MODEL_A_SELF_CONTAINED_SEALED_BUNDLE
MODEL_B_IMMUTABLE_ARTIFACT_REFERENCES: NOT_SELECTED
```

The bundle contains the complete raw records, signatures, and exact five
published object byte payloads. No artifact-store reference, caller-selected
path, filename lookup, extracted-field reconstruction, or alternate trust
source is used. The runner preserves the raw bytes and byte map required by the
M127A verification contract; it does not normalize, reorder, recreate, or
substitute signed input. The current M127A Python foundation uses an OpenSSL
subprocess, so M128A does not require the future runner to invoke that
child-producing API. A later Build must provide the same verification semantics
through the fixed in-process/native verifier boundary selected for this service.

### 3.1 Binary framing

The sealed bundle is a deterministic binary frame, not a JSON object containing
ambiguous nested encodings:

```text
magic: 16 fixed ASCII bytes = AETHER-M128A-BUNDLE
format_version: unsigned 16-bit big-endian integer
entry_count: unsigned 16-bit big-endian integer
entries: entry_count entries sorted by field name byte order
entry: name_length u16, name UTF-8 bytes, value_length unsigned 64-bit big-endian integer, value bytes
trailer: SHA-256 over magic through final value byte
```

Names are an exact allowlist. Names are unique, ASCII-compatible UTF-8, and
values are opaque bytes except where the entry definition below explicitly
requires canonical JSON or a signature. Lengths are checked before allocation.
There is no base64 layer inside a value, no compression, no nested frame, no
duplicate field, no padding, and no unknown entry. There is no duplicate field.
Multiple duplicate fields are
rejected before any raw record is passed to M127A.

### 3.2 Complete entry inventory and limits

The exact entries are:

```text
authority_set_raw
image_baseline_signature
local_console_raw
local_console_signature
governance_raw
governance_signature
authorization_payload_raw
authorization_envelope_raw
authorization_detached_signature
target_host_identity_digest
target_boot_digest
transaction_id
authorization_id
nonce
trust_generation
minimum_accepted_generation
requested_object_set
mutation_scope
object_set_digest
issued_at_utc
expires_at_utc
verification_context_fingerprint
object_0_path
object_0_bytes
object_0_size
object_0_sha256
object_1_path
object_1_bytes
object_1_size
object_1_sha256
object_2_path
object_2_bytes
object_2_size
object_2_sha256
object_3_path
object_3_bytes
object_3_size
object_3_sha256
object_4_path
object_4_bytes
object_4_size
object_4_sha256
```

The following extracted entries are transport headers only. The runner derives
their authoritative values from the raw signed records and exact byte payloads
and rejects any mismatch:

```text
target_host_identity_digest
transaction_id
nonce
trust_generation
minimum_accepted_generation
requested_object_set
mutation_scope
object_set_digest
issued_at_utc
expires_at_utc
verification_context_fingerprint
```

`validity_state` and `revocation_state` are deliberately not bundle entries.
They are derived by the runner from signed authority records, trusted current
time, generation policy, revocation data, and verification result. A diagnostic
copy of either value, if ever produced in a future export, is non-authoritative
and must match the derived result.

M127A-compatible limits are exact:

```text
MAX_RECORD_BYTES: 64 * 1024 per raw authority, local, governance, payload, or envelope record
MAX_SIGNATURE_BYTES: 4096 per detached signature entry
MAX_OBJECT_BYTES: 1024 * 1024 per published object byte entry
MAX_OBJECT_COUNT: 5
MAX_FRAME_OVERHEAD: 64 * 1024
MAX_BUNDLE_BYTES: MAX_FRAME_OVERHEAD + 5 * MAX_RECORD_BYTES + 4 * MAX_SIGNATURE_BYTES + 5 * MAX_OBJECT_BYTES
```

The aggregate bound is large enough for five M127A-size object payloads and all
five raw records plus four signature entries. In particular, the fixed verifier executable may exceed 64 KiB but may not exceed `MAX_OBJECT_BYTES`. The bundle
is rejected if any individual or aggregate limit is exceeded, if a declared
object size differs from its byte length, or if the aggregate frame length is
not exact.

## 4. Selected Runner and Plain Service Policy

The selected runner component is exactly:

```text
SELECTED_COMPONENT_MODEL: ONE_SHOT_OS_CONTROLLED_PRIVILEGED_SERVICE
SERVICE_IDENTITY: aether-host-trust-bootstrap-runner.service
EXECUTABLE: /usr/libexec/aether-host-trust-bootstrap-runner
SERVICE_TYPE: Type=oneshot
DESCRIPTOR_POLICY: NO_INHERITED_DESCRIPTORS
CLIENT_SOCKET: NONE
COGNITIVE_ROLE: NONE
```

The runner is an OS/deployment organ, not Aether and not an agent. It receives
no natural-language goal, chooses no release, interprets no Owner intent,
calls no tool, authorizes no Action, operates no OAS Goal state, and reports no
task completion. No caller arguments, stdin data, environment authority,
socket request, or inherited descriptor is accepted.

The selected process-restriction model is exactly:

```text
SELECTED_PROCESS_RESTRICTION_MODEL: MODEL_D_INITIAL_NAMESPACE_PREOPENED_DIRFDS_PLUS_IRREVERSIBLE_LANDLOCK_AND_SECCOMP
SYSTEMD_FILESYSTEM_CONFINEMENT: NONE
INPROCESS_FILESYSTEM_CONFINEMENT: PREOPENED_DIRFDS_PLUS_IRREVERSIBLE_LANDLOCK
POST_START_EXEC_RULE: FIXED_NATIVE_PROCESS_INSTALLS_IRREVERSIBLE_SECCOMP_FILTER
POST_START_PROCESS_CREATION_RULE: FIXED_NATIVE_PROCESS_DENIES_FORK_VFORK_CLONE_CLONE3
```

The fixed runner and fixed admitter are reviewed native static ELF executables,
not scripts and not interpreters. systemd creates each process by executing its
one fixed `ExecStart` path and supplies only process, capability, network, and
system-call policy. The unit-level policy deliberately provides no filesystem
confinement: every systemd directive that creates or changes a filesystem mount
namespace is absent. No private network namespace is required and no private
mount namespace is permitted. Mount-namespace equality with PID 1 is therefore
truthful and required; setting a filesystem directive to `no` would not itself
be treated as a security boundary.

The systemd 252 policy is intentionally not an exec allowlist. Its
`SystemCallFilter=@system-service` baseline is extended with the Landlock and
seccomp setup calls and an explicit pre-start deny list for process creation and
socket communication. Systemd's documented implicit allow-list behavior for
`execve()` and `execveat()` is accepted for the initial `ExecStart`. After entry,
the fixed process must call `prctl(PR_SET_NO_NEW_PRIVS, 1)` and install one
`SECCOMP_SET_MODE_FILTER` with `SECCOMP_FILTER_FLAG_TSYNC`. That irreversible
filter returns `EPERM` for `execve`, `execveat`, `fork`, `vfork`, `clone`, and
`clone3`; it is installed before any worker thread or untrusted input is
processed and cannot be removed or weakened. The process then checks
`/proc/self/status` for `NoNewPrivs: 1` and `Seccomp: 2`.

The future unit policy is:

```text
User=root
Group=root
SupplementaryGroups=
Type=oneshot
ExecStart=/usr/libexec/aether-host-trust-bootstrap-runner
WorkingDirectory=/
UMask=0077
RestrictAddressFamilies=AF_UNIX
IPAddressDeny=any
SystemCallFilter=@system-service landlock_create_ruleset landlock_add_rule landlock_restrict_self prctl seccomp
SystemCallFilter=~fork vfork clone clone3 socket socketpair connect bind listen accept accept4 sendto sendmsg recvfrom recvmsg
SystemCallErrorNumber=EPERM
NoNewPrivileges=yes
RestrictSUIDSGID=yes
CapabilityBoundingSet=
AmbientCapabilities=
LimitCORE=0
Restart=no
TimeoutStartSec=120s
TimeoutStopSec=15s
NotifyAccess=none
```

The selected initial-host-mount-namespace model means the unit-level policy
provides no filesystem confinement. The policy contains none of the
filesystem-namespace directives `NoExecPaths=`, `ExecPaths=`,
`ReadWritePaths=`, `ReadOnlyPaths=`, `InaccessiblePaths=`, `BindPaths=`,
`BindReadOnlyPaths=`, `TemporaryFileSystem=`, `RootDirectory=`, `RootImage=`,
`PrivateMounts=`, `PrivateTmp=`, `PrivateDevices=`, `ProtectSystem=`, or
`ProtectHome=`. Setting any of these to `no` would not itself be a security
boundary for this model. No private network namespace is required, and no
private mount namespace is permitted. `IPAddressDeny=any` and
`RestrictAddressFamilies=AF_UNIX` block ordinary IP access, while the pre-start
and post-start syscall filters block socket creation and socket I/O. No DNS,
outbound IP, local IPC, or client socket is available.

The admitter uses the same process-restriction model and the same
filesystem-neutral unit policy shape, with only `ExecStart=` changed to
`/usr/libexec/aether-host-trust-bootstrap-admitter`. It has no second
process-restriction or filesystem-confinement model. The admitter installs the
Landlock and irreversible seccomp restrictions before reading the import medium
or opening the inbox.

Failure to install the in-process filter, failure to observe `NoNewPrivs: 1` or
`Seccomp: 2`, a systemd policy mismatch, an unexpected descriptor, an unexpected
child, or any failed network restriction exits nonzero before durable SQLite
intent or ingress disposition. There is no claim that a static systemd filter
changes after service startup; the fixed process performs the named Landlock and
seccomp transitions.

The manager must verify effective policy with `systemd-analyze verify`,
`systemctl show`, `/proc/self/status`, `/proc/self/mountinfo`, and
`/proc/self/fd` before trusting a result. A policy mismatch, unexpected
descriptor, unexpected child, or failed syscall/network restriction fails
closed. `Restart=no` prevents service restart from becoming retry or authority
logic. Process exit status is never bootstrap success; durable SQLite state and
terminal Observation/Verification are required.

The plain oneshot service has no `NOTIFY_SOCKET` dependency and no notification
descriptor. The launcher clears `NOTIFY_SOCKET`. A zero exit means only that the
bounded process completed its inspection or durable disposition. service completion
is not bootstrap success.

### 4.1 Model D startup sequence and Landlock contract

The unit policy supplies no filesystem confinement. The selected Model D is the
single in-process filesystem-confinement model and applies independently to the
runner and admitter. The exact startup sequence is:

```text
1. systemd starts exactly one fixed native static ELF executable.
2. The trusted executable processes no caller input and no bundle bytes.
3. It verifies its executable, unit, cgroup, boot, and initial namespace identity.
4. It opens only the exact required root-owned paths using no-follow,
   descriptor-relative operations.
5. It records the exact expected device, inode, filesystem, owner, mode, and
   mount facts.
6. It sets PR_SET_NO_NEW_PRIVS.
7. It installs a Landlock ruleset bounded to the minimum required read/write
   directory and file handles.
8. It installs the irreversible TSYNC seccomp filter.
9. It closes every unnecessary descriptor.
10. It rechecks NoNewPrivs, Seccomp, descriptor inventory, namespace identity,
    and fixed-path identity.
11. Only after all restrictions succeed may it read the bundle or open SQLite.
12. Any unsupported Landlock ABI, incomplete handled-access set, failed rule,
    failed seccomp installation, unexpected descriptor, or identity drift fails
    closed before durable intent.
```

The future executable requires a Landlock ABI of at least 3 and queries
`LANDLOCK_CREATE_RULESET_VERSION` before creating a ruleset. It supplies the
exact `handled_access_fs` set for every required filesystem action through ABI 3:

```text
LANDLOCK_MINIMUM_ABI: 3
LANDLOCK_REQUIRED_HANDLED_ACCESS_FS: EXECUTE | WRITE_FILE | READ_FILE | READ_DIR | REMOVE_DIR | REMOVE_FILE | MAKE_CHAR | MAKE_DIR | MAKE_REG | MAKE_SOCK | MAKE_FIFO | MAKE_BLOCK | MAKE_SYM | REFER | TRUNCATE
CURRENT_PROBE_HOST_LANDLOCK_STATUS: UNSUPPORTED_EOPNOTSUPP
CURRENT_PROBE_HOST_SUCCESS_PATH_RUNNABLE: NO
LANDLOCK_UNSUPPORTED_BEHAVIOR: FAIL_CLOSED_BEFORE_DURABLE_INTENT
TARGET_BUILD_PROFILE_REQUIRES_LANDLOCK_ABI_3_OR_NEWER: YES
CURRENT_HOST_DEPLOYMENT_READY: NO
```

The future implementation rejects `EOPNOTSUPP`, an ABI below 3, an unknown
access bit, a missing required handled bit, an unexpected ruleset size, an empty
rule, an `landlock_add_rule` failure, or a failed
`landlock_restrict_self`. It does not silently fall back to DAC, systemd, a
partial Landlock policy, or an unconfined service. The ruleset is installed
after `PR_SET_NO_NEW_PRIVS` and before the final seccomp filter. Landlock is
irreversible for the thread and its future children; the seccomp policy denies
children, so no worker or child can escape the combined restrictions.

Landlock rules are file-hierarchy rules, not exact filename ACLs. A rule on a
writable directory can allow creation or mutation of other names in that
directory. Therefore the trusted executable pre-opens exact directory and file
descriptors, uses only a fixed internal object vocabulary, accepts no
caller-selected path, resolves every relative name with `openat2`-equivalent
`RESOLVE_BENEATH | RESOLVE_NO_SYMLINKS` operations against the pre-opened
directory descriptor, and verifies device, inode, filesystem, owner, mode,
regular-file type, link count, size, and digest after every effect. Seccomp BPF
may check architecture, selected syscall numbers, and technically checkable
flag masks; it cannot safely compare an arbitrary pathname pointer to a string.
Path identity is consequently enforced by fixed native control flow,
descriptor-relative resolution, Landlock hierarchy rules, and postconditions,
not by a claimed pathname-aware seccomp rule.

Landlock does not restrict every filesystem operation, including `stat`,
`flock`, `chmod`, `chown`, several timestamp/xattr operations, or all ioctl
effects. The Model D filter denies unrelated mount and namespace operations,
`open_by_handle_at`, pathname-linking operations, permission/ownership changes
not required by the fixed publication algorithm, and all network/process
operations where the service does not require them. The fixed executable must
not rely on Landlock to enforce these limitations. A trusted native
postcondition check and the empty capability bounding set remain required.
The design does not claim protection from a compromised trusted executable,
kernel, PID 1, root administrator, OS image, or filesystem implementation.

The runner's exact pre-open and Landlock authority set is:

```text
RUNNER_READ_HANDLES: immutable OS/image policy; /proc identity facts; one sealed inbox candidate; state.sqlite3, state.sqlite3-wal, state.sqlite3-shm, state.lock; exact five existing trust-object paths for recovery and verification
RUNNER_WRITE_HANDLES: state.sqlite3, state.sqlite3-wal, state.sqlite3-shm, state.lock; inbox disposition; accepted/ and rejected/ archives; exact transaction staging and prior-object paths; exact five final trust-object paths
RUNNER_PATH_INPUT: NONE; fixed vocabulary only
RUNNER_LANDLOCK_MUTATION: WRITE_FILE, MAKE_REG, MAKE_DIR, REMOVE_FILE, REMOVE_DIR, REFER, and TRUNCATE only on the fixed handled hierarchies where the corresponding operation is required
RUNNER_FORBIDDEN: arbitrary host paths, arbitrary filenames, candidate paths, socket paths, mount paths, verifier selection, and every unrelated filesystem hierarchy
```

The admitter's separate exact authority set is:

```text
ADMITTER_READ_HANDLES: verified read-only import medium; admitter executable and immutable import policy; required procfs/kernel identity facts
ADMITTER_WRITE_HANDLES: /var/lib/aether/trust-bootstrap/inbox/ only, for one fixed transaction vocabulary and its exact temporary/ready names
ADMITTER_PATH_INPUT: NONE; transaction identity is parsed from verified bundle content, never from caller-selected paths
ADMITTER_LANDLOCK_MUTATION: WRITE_FILE, MAKE_REG, REMOVE_FILE, and REFER only on the fixed inbox hierarchy
ADMITTER_FORBIDDEN: state.sqlite3, state.sqlite3-wal, state.sqlite3-shm, state.lock, accepted/, rejected/, transactions/, /etc/aether, /usr/libexec/aether-release-verify, verifier staging, arbitrary host paths, and all unrelated filesystem hierarchies
```

The rules for the two services are not equivalent authority. The runner can
write the canonical SQLite sidecars and exact publication set; the admitter
cannot open or mutate any of them. Both services may pre-open only their own
listed handles and must close every descriptor outside that inventory before
input processing. A Landlock directory allowance is never treated as proof of
exact filename authority; the fixed vocabulary, no-follow resolution,
descriptor inventory, syscall restrictions, and postconditions provide the
remaining bounded controls.

The canonical namespace relationship is:

```text
MOUNT_NAMESPACE_POLICY: PID1_INITIAL_HOST_MOUNT_NAMESPACE_REQUIRED
SYSTEMD_PRIVATE_NETWORK_NAMESPACE: NOT_SELECTED
SYSTEMD_PRIVATE_MOUNT_NAMESPACE: FORBIDDEN
MOUNT_NAMESPACE_EQUALITY_GATE: /proc/self/ns/mnt == /proc/1/ns/mnt
```

No private network namespace is required. No private mount namespace is
permitted. The exact-root proof depends on the runner and admitter remaining in
PID 1's initial host mount namespace, so filesystem-namespace directives and
`PrivateNetwork` are excluded rather than used as security boundaries. Network
and socket denial is enforced independently through `RestrictAddressFamilies`,
`IPAddressDeny=any`, the pre-start `SystemCallFilter` restrictions, the
post-start irreversible TSYNC seccomp filter, an empty inherited-descriptor
inventory, no socket activation, no `NOTIFY_SOCKET`, and no client socket.
Failure to establish any required cgroup-BPF or syscall restriction fails closed
before bundle, inbox, or SQLite processing.

## 5. Concrete Initial-Host Namespace Evidence

Exactly one namespace evidence model is selected:

```text
SELECTED_NAMESPACE_MODEL: MODEL_A_KERNEL_SELF_ATTESTED_INITIAL_HOST_MOUNT_NAMESPACE
NAMESPACE_EQUALITY_TO_PID1: REQUIRED
NAMESPACE_RECORD: NONE
NAMESPACE_EVIDENCE_PRODUCER: LINUX_KERNEL_PROCFS_AND_STATX
```

The Linux kernel is the only namespace-fact producer. Its native mechanisms are
the runner's reads of `/proc/self/ns/mnt`, `/proc/1/ns/mnt`,
`/proc/self/mountinfo`, `/proc/sys/kernel/random/boot_id`, and descriptor-relative
`statx`/`fstatat` results for the fixed paths. There is no Aether-specific JSON
namespace record, no PID 1 custom writer, and no cryptographic namespace-evidence
key lifecycle. PID 1 starts the service, but it does not write or sign a custom
namespace record.

```text
NAMESPACE_FACTS: KERNEL_ATTESTED_AT_RUNNER_ENTRY
HOST_MOUNT_NAMESPACE: /proc/1/ns/mnt
SERVICE_MOUNT_NAMESPACE: /proc/self/ns/mnt
MOUNT_NAMESPACE_RELATION: MUST_BE_EQUAL
FIXED_PATH_RELATION: SERVICE_PATH_EQUALS_HOST_PATH
```

The producer is the Linux kernel, with the runner as its root consumer. systemd
starts the runner directly after applying the unit policy; no pre-start helper,
ExecStartPre probe, or post-start child produces evidence. The runner obtains
both sides of the claimed host-path relation because the selected service mount
namespace is the initial host mount namespace: the service path and intended
host path are the same absolute path, and `/proc/1/ns/mnt` must equal
`/proc/self/ns/mnt`.
`statx`/`fstatat` facts are collected after the runner enters and before any
candidate admission. The kernel facts are not signed; they are direct local
observations bounded by the kernel, PID 1, root filesystem, and root principal.

```text
producer: Linux kernel
producer_mechanism: procfs namespace handles, mountinfo, boot_id, statx/fstatat
producer_principal: kernel
consumer_principal: root-owned fixed runner
start_order: systemd policy -> ExecStart -> filter transition -> kernel facts -> bundle read
host_facts: /proc/1/ns/mnt and fixed-path statx/fstatat
service_facts: /proc/self/ns/mnt, /proc/self/mountinfo, and fixed-path statx/fstatat
boot_binding: exact boot_id stored with the SQLite transaction
unit_binding: /proc/self/cgroup plus immutable OS/image unit-policy digest
executable_binding: /proc/self/exe plus immutable OS/image executable digest
```

The immutable OS/image baseline supplies only the expected fixed path inventory,
unit-policy digest, executable digest, and fixed-path policy. It does not supply
signed runtime namespace evidence. Root ownership and mode are file-integrity
postconditions, not cryptographic provenance.

```text
/usr/lib/aether/os-image/host-trust-bootstrap-path-policy.json
```

That manifest is root-owned, mode `0444`, regular, and covered by the approved
OS/image package digest and M126A policy. Its expected-value role is explicit;
it is not a runtime attestation source and cannot make a caller assertion true.
Ordinary Aether runtime and OAS runtime cannot replace the policy or alter the
kernel observations.

The complete fixed host-path set is visible at the same absolute paths in the
service and PID 1's initial mount namespace:

```text
SERVICE_PATH_EQUALS_PID1_PATH: /etc/aether
SERVICE_PATH_EQUALS_PID1_PATH: /usr/libexec
SERVICE_PATH_EQUALS_PID1_PATH: /var/lib/aether/trust-bootstrap
```

The runner independently checks current boot ID, equality of the two mount
namespace handles, `/proc/self/mountinfo`, `/proc/self/exe`, cgroup membership,
the immutable expected policy digest, every fixed directory and object identity,
and all descriptor-relative path constraints before candidate admission.
Missing, stale, contradictory, replaced, or unreadable kernel facts fail closed.
There is no runtime namespace record to own, sign, replay, replace, or recover;
replay resistance is the boot and SQLite transaction binding. A changed boot,
changed mount namespace, changed mountinfo, changed fixed-path identity, or
changed expected policy enters review and cannot resume forward publication.

The mount-namespace equality gate is evaluated before any input or state effect:
the runner must establish `/proc/self/ns/mnt == /proc/1/ns/mnt` before reading a
bundle, opening an inbox candidate, opening SQLite, creating durable intent, or
performing any filesystem mutation. Namespace inequality fails closed with no
durable intent. The admitter applies the same gate before reading the import
bundle or opening a candidate destination.

The approved writable paths are exactly:

| Service path | PID 1 initial-namespace path | Access | Identity check |
| --- | --- | --- | --- |
| `/etc/aether` | `/etc/aether` | exact five trust files only | namespace equality, device/inode, filesystem identity, metadata |
| `/usr/libexec` | `/usr/libexec` | fixed verifier object only | namespace equality, device/inode, filesystem identity, metadata |
| `/var/lib/aether/trust-bootstrap` | `/var/lib/aether/trust-bootstrap` | SQLite, ingress disposition, and transaction staging only | namespace equality, device/inode, filesystem identity, metadata |

The binding is the complete kernel namespace handle equality, mountinfo,
device/inode, filesystem, path, metadata, unit, boot, executable, and immutable
policy tuple. A caller-created, container-created, chroot-created,
bind-substituted, remounted, overlay, or otherwise substituted namespace is
rejected. Inequality with PID 1 is rejected. Equality is required by Model A;
it is a direct kernel observation, not a cryptographic statement about PID 1 or
the kernel.

## 6. Exact Root, Privilege Provenance, and Fixed Objects

The target is the intended host root represented by the service's verified
initial namespace and fixed paths, not a caller-selected directory, chroot, container root, or namespace
root. The runner opens service-visible directories with descriptor-relative
no-follow operations and an `openat2`-equivalent
`RESOLVE_BENEATH|RESOLVE_NO_SYMLINKS` policy. It rejects `..`, absolute request
paths, alternate separators, NUL bytes, mount crossings, symlink parents,
bind-mount substitution, hard-link count other than one, directories, devices,
FIFOs, sockets, and other special files.

The exact five fixed objects are:

```text
/etc/aether/release-trust-anchor.pub
/etc/aether/release-trust-anchor.fingerprint
/etc/aether/release-test-evidence.sha256
/etc/aether/release-verifier.sha256
/usr/libexec/aether-release-verify
```

UID 0 is necessary for future file effects but never sufficient for authority.
`OSRunnerIdentityEvidence` binds unit identity, executable identity, PID 1/systemd
identity, process identity, boot identity, namespace and fixed-path identity, fixed
configuration provenance, and capability policy. The runner verifies this
evidence before consuming any M126A/M127A record. A mathematically valid
authorization without OS provenance is rejected.

## 7. Object-Byte Provenance and M127A Verification Handoff

The five bytes originate from the future M122A-style immutable release-artifact
producer operating in an approved offline build/import environment. The
producer creates the fixed object byte payloads and complete signed M126A
evidence. The sealed Model A bundle is the transport boundary; no later
filename or artifact-store lookup is performed.

The admitter receives the complete bundle from the selected ingress source and
copies it without normalization. The runner independently verifies every `object_N`
path against the fixed ordered object set, every byte length and SHA-256 digest,
the aggregate object-set digest, and the signed `object_set_digest` in the
authorization payload and envelope. It then supplies the exact raw byte values
to the M127A semantic verification contract through its fixed in-process/native
verifier boundary. No digest is accepted without the corresponding bytes and
signed source records.

Missing object bytes, partial bundle availability, wrong length, wrong digest,
wrong path, duplicate path, extra object, mutable source, symlink, hard link,
special file, or changed bundle trailer fails closed before intent. The fixed
verifier executable is subject to the same 1 MiB per-object bound; it is not
silently constrained by the 64 KiB record bound.

## 8. Selected Admitter Privilege Model

Exactly one admitter model is selected:

```text
SELECTED_ADMITTER_MODEL: MODEL_B_ROOT_ONE_SHOT_CONFINED_ADMITTER
MODEL_A_NON_ROOT_ADMITTER: NOT_SELECTED
MODEL_C_REVIEWED_ROOT_OPERATOR_IMPORT: NOT_SELECTED
```

Exactly one offline ingress model is selected:

```text
SELECTED_INGRESS_MODEL: MODEL_A_M126A_OFFLINE_BUNDLE_ON_VERIFIED_READ_ONLY_MEDIA
INGRESS_PRODUCER: M126A_HOST_BOOTSTRAP_AUTHORITY_OFFLINE_BUNDLE_EXPORTER
INGRESS_MOUNT_MECHANISM: SYSTEMD_FIXED_READ_ONLY_BLOCK_DEVICE_MOUNT
INGRESS_INVOCATION_AUTHORITY: LOCAL_CONSOLE_ROOT_OPERATOR_REQUEST_PLUS_M126A_EVIDENCE
```

The ingress producer is a future controlled offline bundle exporter operating
under the M126A host-bootstrap authority design. M126A remains the
cryptographic authority, but M126A does not claim that production keys or this
exporter are implemented. The future exporter uses the separately governed
M126A custody and local-console evidence process; it introduces no new signer,
Owner, OAS authority, or key domain. Its input is an exact target host identity
and boot identity collected through the local-console ceremony. Its output is
the complete sealed bundle, including the M126A detached envelope signature and
all raw records. The bytes are transported on one removable block device whose expected device identity,
filesystem identity, read-only options, bundle path, size, and SHA-256 are in
the immutable OS/image import policy:

```text
/usr/lib/aether/os-image/host-trust-bootstrap-import-policy.json
DEVICE_ID: /dev/disk/by-id/aether-host-trust-bootstrap-import
MOUNT_PATH: /run/aether-host-trust-bootstrap/import
BUNDLE_PATH: /run/aether-host-trust-bootstrap/import/import.bundle
MOUNT_OPTIONS: ro,nosuid,nodev,noexec
```

The local operator physically presents that media and requests the fixed
systemd mount from an active non-remote local console. The same local operator
may request the admitter start through the root-owned systemd manager. This
start permission is only invocation control: it is not bootstrap authorization
and cannot make unsigned or incorrectly bound bytes valid. The bundle's exact
M126A signature, local-console evidence, governance evidence, target, boot,
nonce, and object bindings remain the authorization source. Ordinary Aether and
OAS have no systemd-manager IPC, mount permission, `/run` import-path access,
or service-start permission.

The fixed mount unit is created by the pre-Aether OS image, not by this
repository. Before admitting bytes, the manager verifies the block-device major
and minor identity, filesystem UUID/type, mount flags, mount source, mount root,
regular-file/no-symlink status, root ownership, mode `0400`, exact bundle path,
and policy digest. The admitter verifies the same facts and copies bytes only;
the runner verifies the M126A raw envelope and detached signature independently.
Media replacement, writable remount, changed source, changed filesystem,
missing policy, or changed bundle digest fails closed before inbox disposition.
On the same boot, the mount, device identity, mount flags, and exact bundle digest
are revalidated immediately before each admission; unmount, reinsertion, or
replacement requires a new local-console request and fresh M126A evidence. After
a reboot, the old mount and bundle are stale and cannot be resumed; the new boot
requires a new target boot binding and a new local-console request. Cleanup
unmounts the medium only after the exact ready bytes have reached their durable
SQLite disposition and archive result. A repeated identical bundle is an
idempotent transaction retry, while a missing, duplicated, mutable, stale, or
conflicting source enters review and never becomes a new mutation intent.

The future admitter is a separate fixed service, not an authority record and
not the M126A cryptographic authority:

```text
SERVICE_IDENTITY: aether-host-trust-bootstrap-admitter.service
EXECUTABLE: /usr/libexec/aether-host-trust-bootstrap-admitter
SERVICE_TYPE: Type=oneshot
USER: root
GROUP: root
```

Its fixed read-only input source is the OS-mounted offline bundle at:

```text
/run/aether-host-trust-bootstrap/import/import.bundle
```

The source mount identity, source bytes, and source digest are checked against
the approved OS/image import policy. The admitter unit has no shell, caller
arguments, environment file, network, inherited descriptors, signing key,
external command, or access to `/etc/aether`, the trust verifier object,
`state.sqlite3`, `state.sqlite3-wal`, `state.sqlite3-shm`, `state.lock`,
`accepted/`, `rejected/`, or transaction staging. Its only writable path is the
fixed inbox directory.

The confined admitter policy is filesystem-neutral at the unit level:

```text
User=root
Group=root
Type=oneshot
ExecStart=/usr/libexec/aether-host-trust-bootstrap-admitter
UMask=0077
RestrictAddressFamilies=AF_UNIX
IPAddressDeny=any
SystemCallFilter=@system-service landlock_create_ruleset landlock_add_rule landlock_restrict_self prctl seccomp
SystemCallFilter=~fork vfork clone clone3 socket socketpair connect bind listen accept accept4 sendto sendmsg recvfrom recvmsg
SystemCallErrorNumber=EPERM
NoNewPrivileges=yes
CapabilityBoundingSet=
AmbientCapabilities=
Restart=no
NotifyAccess=none
```

Root possession is not authorization. The separate policy and executable
identity are independently verified by the runner's OS evidence. The admitter
cannot edit a ready file after sealing, read back source through an authority
path, delete or rename accepted/rejected evidence, access SQLite or trust-object
destinations, and cannot mint signatures, alter signed fields, lower generation policy, or
obtain general root execution. It transports complete signed evidence and
never becomes the cryptographic authorization source. Ordinary Aether runtime
and OAS runtime cannot access the admitter source or inbox; ordinary Aether
runtime and OAS runtime have no access to the import path.

## 9. Sealed Inbox Transaction

The fixed inbox is:

```text
/var/lib/aether/trust-bootstrap/inbox/
```

It is provisioned `root:root`, mode `0700`, regular, no-symlink, and no mount
substitution. The admitter is the only writer; the runner is the only reader
and disposition owner. Ordinary Aether runtime and OAS runtime have no access
to the inbox and cannot invoke either service.

The admitter performs exactly:

1. open `<transaction_id>.incoming.tmp` with exclusive creation, no-follow,
   regular-file enforcement, `root:root`, mode `0600`, and the aggregate bound;
2. write the complete binary bundle once and reject short, oversized,
   malformed, interrupted, or trailer-mismatched writes;
3. fsync the temporary file and verify exact bytes, length, mode, and digest;
4. atomically rename the temporary file in the same directory to
   `<transaction_id>.ready`; and
5. fsync the inbox directory.

The `.incoming.tmp` name is never a candidate. A partial temporary file is not
an accepted candidate. The runner never edits a ready file. After SQLite records an ingress disposition, the runner moves the exact
ready bytes to immutable `accepted/<transaction_id>.bundle` or
`rejected/<transaction_id>.bundle`, then fsyncs the archive directory. Archive
movement is not an atomic commit with SQLite and is never phase authority.

The selected admission rule is:

```text
ADMISSION_MODEL: ONE_SEALED_READY_CANDIDATE
```

Zero candidates is a no-op. One candidate is eligible only after complete
namespace, root, bundle, raw-record, signature, and byte verification. Multiple
non-identical ready candidates are ambiguity and fail closed. Byte-identical
copies with the same transaction ID and bundle digest resolve by deterministic
filename order to one transaction; the remaining copies are evidence-only.
Extra files, mismatched names, unknown entries, and ambiguous candidates are
not guessed or deleted.

## 10. Complete Raw Evidence and Authorization Consumption

The bundle carries the complete unchanged raw inputs required by the existing
M127A API:

| M127A input | Bundle entry | Authority treatment |
| --- | --- | --- |
| authority-set raw bytes | `authority_set_raw` | passed unchanged to image-baseline and authority verification |
| image-baseline signature | `image_baseline_signature` | passed unchanged as signature bytes |
| local-console raw bytes | `local_console_raw` | passed unchanged to local-console verification |
| local-console signature | `local_console_signature` | passed unchanged as signature bytes |
| governance raw bytes | `governance_raw` | passed unchanged to governance verification |
| governance signature | `governance_signature` | passed unchanged as signature bytes |
| authorization payload raw bytes | `authorization_payload_raw` | passed unchanged to authorization verification |
| authorization envelope raw bytes | `authorization_envelope_raw` | passed unchanged; contains detached signature and signed bindings |
| authorization detached signature | `authorization_detached_signature` | must exactly equal the detached signature encoded in the envelope; no second source is trusted |
| exact object bytes | `object_0..4_bytes` | passed unchanged after fixed-path, length, digest, and aggregate verification |

The runner independently verifies target host, target boot, transaction ID,
authorization ID, nonce, authority root fingerprint, authority-set digest,
authority generation, trust generation, minimum generation, exact requested
objects, mutation scope, object-set digest, local-console digest, governance
digest, issued/expiry times, signature domains, verification context, current
trusted time, revocation, and derived validity. The current
`target_boot_digest` is present in every authorization-consumption list and
binding matrix. `validity_state` and `revocation_state` cannot be trusted as
caller assertions.

The runner does not create a signature, import a key, select a trust source,
reconstruct a signed record, reorder or normalize raw bytes, substitute current
values, lower a generation floor, or convert bootstrap authorization into
deployment authorization. It does not import a key. It does not normalize.
Expired, revoked, missing, ambiguous, malformed,
or mismatched evidence is rejected before durable mutation intent.

`authorization_detached_signature` must exactly equal the detached signature
encoded in `authorization_envelope_raw`; a mismatch must fail closed before
durable intent. The runner decodes the envelope's detached-signature field and
compares the exact raw bytes, not a normalized or caller-derived representation.

## 11. One Canonical Durable SQLite Ledger

```text
CANONICAL_DURABLE_LEDGER: SQLITE_ONLY
STATE_AND_AUDIT_AUTHORITY: state.sqlite3
FILE_BASED_PHASE_AUTHORITY: NONE
```

The fixed state boundary is `/var/lib/aether/trust-bootstrap/`. Its inventory
is:

| Object | Owner | Mode/type | Authority rule |
| --- | --- | --- | --- |
| state directory | `root:root` | `0700` directory | fixed, no symlink or mount substitution |
| `state.sqlite3` | `root:root` | `0600` regular file | sole phase, generation, audit, ingress, Observation, and Verification authority |
| `state.sqlite3-wal` | `root:root` | `0600` SQLite sidecar | SQLite use only; never independent authority |
| `state.sqlite3-shm` | `root:root` | `0600` SQLite sidecar | SQLite use only; never independent authority |
| `state.lock` | `root:root` | `0600` regular file | bounded inter-process serialization |
| `inbox/` | `root:root` | `0700` directory | sealed evidence transport |
| `accepted/` and `rejected/` | `root:root` | `0700` directories | retained evidence transport, never phase authority |
| `transactions/<tx>/` | `root:root` | `0700` directory | exact staging and prior-object evidence |

SQLite WAL mode with `synchronous=FULL` commits state and audit in one SQLite
transaction. Canonical tables or equivalent records are:

```text
ingress_disposition
transaction_record
prior_object
observation
verification
```

The audit chain stores `previous_audit_digest` and `audit_head_digest` inside
SQLite. There is no `journal.jsonl`, no separately fsynced file-based phase
journal, and no dual authority. Any future human-readable export is derived,
read-only, non-authoritative, regenerable, and cannot authorize recovery or
mutation. Missing or stale export does not corrupt valid SQLite state.

SQLite corruption, unknown schema, owner/mode drift, WAL/SHM loss, disk-full,
or fsync failure preserves evidence and enters
`TRUST_BOOTSTRAP_REVIEW_REQUIRED`. The runner does not recreate a damaged
database, infer active generation, use a sidecar/export as authority, or restore
an arbitrary backup.

## 12. Process-Crash and Reboot Recovery

The durable state vocabulary is:

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

Lock ordering is fixed:

1. verify OS runner identity, current boot, procfs namespace facts, exact root
   path identity, and effective service policy;
2. inspect the inbox without mutation;
3. acquire `state.lock`;
4. execute SQLite `BEGIN IMMEDIATE`;
5. resolve existing transaction, ingress disposition, and generation admission
   against canonical rows; and
6. commit the SQLite intent/phase record before any external host effect.

The new process receives no M127A `TemporaryRootCapability`. Same-boot recovery
revalidates the complete raw evidence, namespace/path identity, context, nonce, generation,
object bytes, and phase before exact continuation. After every publication
effect, the next process reopens and reobserves the affected path identity.
A same-boot crash is recoverable only after that complete revalidation.
Changed boot, changed namespace/path identity, changed PID 1 relationship, or changed evidence
never silently resumes forward activation. Changed-boot recovery is
restoration/review only unless a new separately authorized transaction is
admitted.

| Durable phase | Same-boot crash | Changed-boot recovery | Allowed mutation | Required evidence | Final result |
| --- | --- | --- | --- | --- | --- |
| no intent | no state to recover | no state to recover | none | fresh OS/namespace/root and authorization for new work | rejected or new transaction |
| `TRUST_BOOTSTRAP_REQUESTED` | recover frozen intent after revalidation | inspect read-only; restore/review only | exact known same-boot step | complete raw evidence and SQLite | continue or review |
| `TRUST_BOOTSTRAP_VALIDATED` | rerun exact validation | no forward continuation | exact restore only after reboot | signed records, bytes, namespace/path identity | restore or review |
| `PRIOR_GENERATION_RETAINED` | verify prior retention and continue | restore prior or review | staging same boot; reverse restore after reboot | prior identity and namespace/path facts | continue, restore, or review |
| `NEXT_GENERATION_STAGED` | rehash staged bytes and continue | remove exact staging only if safe | no live mutation after reboot | staging inventory | review or safe cleanup |
| `PUBLISHING` before rename | continue exact next effect | no forward publication | reverse restore only if exact | prior bytes and namespace/path facts | restore or review |
| `PUBLISHING` between directories | observe partial set | mixed set unusable | reverse restore only | all five paths and prior bytes | restore or review |
| after writes before `VERIFYING` | independently verify | read-only verify, restore, or review | no activation after reboot | live inventory and boot | verify or review |
| after terminal Observation before Verification | rerun Verification | no activation | terminal evidence uncommitted | Observation record | verify or review |
| after Verification before state/audit commit | rerun both records | no activation | state remains prior | Verification record | commit or review |
| after `TRUST_SET_ACTIVE` commit | report after exact read-only observation | read-only confirm only | no republish without fresh transaction | committed SQLite and live observation | result or review |
| `RESTORING_PRIOR_GENERATION` | inspect current step, never guess | increased review requirement | exact reverse step only | retained prior and namespace/path facts | restore or review |
| `TRUST_BOOTSTRAP_REVIEW_REQUIRED` | no automatic work | no automatic work | none without fresh review | complete failure evidence | operator/PM review |

## 13. Inbox, SQLite, and Archive Crash Ordering

The inbox and archives are evidence transport only. SQLite remains the sole
phase and audit authority. No archive rename is atomic with SQLite.

| Case | Canonical SQLite state | Allowed cleanup/retry | Duplicate behavior | Filesystem result | Audit/review result |
| --- | --- | --- | --- | --- | --- |
| `INBOX_CASE_1_BEFORE_TEMP_FSYNC` | no disposition or intent | admitter may remove only exact owned temporary after bounded age | no candidate exists | partial temp is ignored | no audit; review if ownership is uncertain |
| `INBOX_CASE_2_AFTER_TEMP_FSYNC_BEFORE_RENAME` | no disposition or intent | retry exact source or remove exact temp | no ready duplicate | temp remains non-candidate | no audit; review if bytes or metadata differ |
| `INBOX_CASE_3_AFTER_RENAME_BEFORE_INBOX_DIR_FSYNC` | no disposition or intent | runner treats ready file as candidate only after complete verification | same digest is one retry | ready may survive; no host effect | disposition/ambiguity review if directory durability is unknown |
| `INBOX_CASE_4_READY_BEFORE_SQLITE_DISPOSITION` | no disposition or intent | acquire lock and verify candidate; do not archive first | identical ready is same candidate | ready remains evidence | SQLite records disposition or review |
| `INBOX_CASE_5_AFTER_REJECTION_BEFORE_ARCHIVE` | rejection disposition is canonical | retry archive move idempotently; never retry mutation | same digest returns rejection | ready and rejected copies may coexist | no host effect; review only if bytes differ |
| `INBOX_CASE_6_AFTER_ACCEPTANCE_INTENT_BEFORE_ARCHIVE` | accepted ingress and durable intent are canonical | recover exact transaction; archive move may retry | ready retry resolves to transaction ID | ready remains until archive succeeds | no second intent or publication |
| `INBOX_CASE_7_AFTER_ARCHIVE_RENAME_BEFORE_DIR_FSYNC` | SQLite disposition/phase remains canonical | inspect both locations and fsync archive directory; never infer phase from move | duplicate archive is evidence only | archive may be durable or uncertain | review if bytes/digest/location cannot be reconciled |
| `INBOX_CASE_8_AFTER_ARCHIVE_FSYNC` | unchanged canonical SQLite result | no host retry from archive alone | repeated archive is idempotent evidence | accepted/rejected bytes retained | no authority gained |
| `INBOX_CASE_9_RECOVERY_WITH_READY_AND_ARCHIVE_COPIES` | SQLite transaction and digest decide | compare exact bytes; retain duplicates; recover only SQLite phase | identical copies resolve to one digest | no archive copy selects a phase | mismatch or extra candidate is `REVIEW_REQUIRED` |
| `INBOX_CASE_10_SQLITE_STATE_WITH_MISSING_TRANSPORT` | SQLite remains canonical but evidence completeness is checked | no forward mutation if required raw bundle is unavailable; restore/review | no reconstruction from digest | host unchanged or exact restore | missing evidence is `REVIEW_REQUIRED` |

## 14. Generation Admission Semantics

Every case obtains `state.lock` before `BEGIN IMMEDIATE`. M127A's generation
semantics are preserved and are not collapsed into a generic two-request rule:

| Case | Admission, rows, and reservation | Inbox disposition | Filesystem, audit, and review |
| --- | --- | --- | --- |
| `GENERATION_CASE_1_IDENTICAL_TRANSACTION_RETRY` | same transaction ID, nonce, bytes, and bindings resolve to one existing row and durable result | archive duplicate after disposition | no second reservation or host effect; original audit remains authoritative |
| `GENERATION_CASE_2_DIFFERENT_TRANSACTION_SAME_NONCE` | complete authorization verification occurs; first exact reservation commit wins; loser creates no transaction, reservation, audit, staging, observation, verification, or host residue | retain/reject loser evidence | only winner may publish; ambiguity requires review |
| `GENERATION_CASE_3_DIFFERENT_TRANSACTION_SAME_GENERATION` | one generation reservation wins; loser is stale/conflict with no intent | reject loser without replacement | no loser mutation or active-generation change |
| `GENERATION_CASE_4_LOWER_THEN_HIGHER_AFTER_TERMINAL` | lower transaction reaches terminal state; separately sealed higher candidate is admitted later | archive each by transaction ID | two historical successful records; `active_generation` is higher |
| `GENERATION_CASE_5_HIGHER_THEN_STALE_LOWER` | higher generation reserves/activates first; later lower candidate fails floor/current check | reject and retain lower evidence | no lower mutation or metadata regression |
| `GENERATION_CASE_6_MULTIPLE_READY_CANDIDATES` | zero is no-op; one is eligible; identical copies resolve by digest/name; non-identical copies are ambiguity | retain all evidence; no guessing | no reservation or host effect for ambiguity; review |
| `GENERATION_CASE_7_NEW_CANDIDATE_DURING_NONTERMINAL_TRANSACTION` | existing transaction remains sole mutable transaction until terminal or review | leave new candidate sealed | no second intent/publication; review on conflict |
| `GENERATION_CASE_8_RECOVERY_WITH_NEW_CANDIDATE_PRESENT` | recovery resolves existing SQLite transaction before candidate admission | candidate waits sealed | no candidate effect during recovery; ambiguity is review |
| `GENERATION_CASE_9_BURNED_THEN_HIGHER` | `BURNED` cannot be reused; later valid higher candidate may reserve after terminal disposition | reject burned reuse; archive higher result | burn and later activation remain historical; floor advances |

`active_generation` identifies the current highest active generation. A lower
generation can be a valid historical success before a later higher generation;
it is stale after the higher generation. A burned generation is never reused.

## 15. Cross-Directory Publication and Terminal Evidence

The five objects span `/usr/libexec` and `/etc/aether`; publication is not one
filesystem-atomic operation. Before each effect, SQLite durably records prior
bytes or absence, metadata, device/inode, namespace/path identity, generation, and
object digest. Replacement uses a same-directory root-owned temporary regular
file, exclusive no-follow creation, bounded bytes, exact mode, file fsync,
atomic same-directory rename, directory fsync, and a subsequent SQLite phase
record.

A mixed set is unusable and cannot be consumed or reported active. Restoration
uses reverse order and exact identity checks. Cross-directory atomicity between
the two directories and SQLite is explicitly not proven.

`TRUST_SET_ACTIVE` requires one SQLite transaction containing terminal
Observation, terminal Verification, canonical audit, and the active transition:

```text
TERMINAL_OBSERVATION_COMMIT
+ TERMINAL_VERIFICATION_COMMIT
+ CANONICAL_AUDIT_COMMIT
+ TRUST_SET_ACTIVE_STATE_COMMIT
= ONE_ATOMIC_SQLITE_TRANSACTION
```

Terminal ACTIVE requires atomic Observation and Verification. Observation alone
cannot create active state. Verification independently reopens service-visible
paths, SQLite, namespace facts, fixed verifier identity, exact bytes, object
digests, generation bindings, authorization bindings, and recovery result.

## 16. Authority Separation and Negative Guarantees

| Actor or artifact | May do | May not do |
| --- | --- | --- |
| Aether Core | coordinate goals and receive bounded public result evidence | mint bootstrap authorization, sign evidence, or grant root mutation |
| OAS runtime | retain bounded security state and consume public results | mint authorization, become root, select paths, or access inbox/ledger |
| ordinary Aether runtime | receive bounded reviewed status | invoke runner/admitter, access evidence, pass paths, or inherit authority |
| confined admitter | transport one complete sealed bundle | mint signatures, alter signed fields, lower generation, or execute general root work |
| M126A authority record | authorize one exact five-object transaction when valid | authorize deployment, Owner intent, Generic Act, or unrelated mutation |
| SQLite record | identify phase, generation, audit, ingress, and evidence | act as a reusable root capability or bearer token |
| privileged runner | verify raw records/bytes, bind exact host paths, publish five objects, recover phases | interpret goals, authorize Action, create keys, select trust, or mutate arbitrary state |
| root operator | perform separately reviewed operational inspection | substitute UID 0 for authorization or edit sealed/signed scope |
| systemd/PID 1 and kernel | provide OS, process, namespace, fixed-path, and syscall policy facts | become Owner intent or general application authority |

```text
AETHER_CORE_CANNOT_MINT_BOOTSTRAP_AUTHORIZATION: YES
OAS_RUNTIME_CANNOT_MINT_BOOTSTRAP_AUTHORIZATION: YES
OAS_RUNTIME_CANNOT_GAIN_ROOT_MUTATION_AUTHORITY: YES
RUNNER_CANNOT_INTERPRET_GOALS: YES
RUNNER_CANNOT_AUTHORIZE_GENERAL_ACTION: YES
ADMITTER_CANNOT_MINT_BOOTSTRAP_AUTHORIZATION: YES
PERSISTED_TRANSACTION_IS_NOT_BEARER_CAPABILITY: YES
BOOTSTRAP_SUCCESS_IS_NOT_TASK_COMPLETION: YES
GENERIC_ACT_AUTHORIZED: NO
```

## 17. Threat and Failure Matrix

`REVIEW_REQUIRED` never means success. Each row specifies detection, allowed
mutation, canonical state, filesystem result, evidence result, and disposition.

| Threat/failure | Detection | Allowed mutation | Canonical state | Filesystem/evidence result | Disposition |
| --- | --- | --- | --- | --- | --- |
| unauthorized service invocation | fixed units, no socket, no arguments, local-console gate | none | no intent | unchanged | rejected |
| forged runner or admitter identity | immutable OS/image, unit, cgroup, pidfd, `/proc/self/exe` digest | none | no intent | unchanged | review if ambiguous |
| namespace inequality with PID 1 | compare `/proc/self/ns/mnt` and `/proc/1/ns/mnt` handles | none | no intent | fixed-path claim invalid; no input read | review |
| procfs namespace fact unavailable | open/read of fixed procfs namespace handles and mount facts | none | no intent | namespace identity unproven | review |
| boot identity mismatch | current `boot_id` versus signed target and SQLite binding | none | frozen/review | no forward publication | restore/review |
| fixed-path device/inode/filesystem drift | descriptor-relative `statx`/`fstatat`, mountinfo, owner/mode/link checks | none | no intent or frozen | fixed path identity invalid | review |
| bind/remount/overlay substitution | mountinfo, device/inode, filesystem identity, namespace equality, postcondition recheck | none | no intent or frozen | substituted path rejected | review |
| executable or unit-policy digest mismatch | `/proc/self/exe`, cgroup/unit identity, immutable OS/image digest | none | no intent | trusted executable/policy unproven | review |
| unsupported or incomplete Landlock ABI | version query, exact ruleset size, handled-access bitset, required ABI 3 | none | no intent | no filesystem restriction claimed | fail closed |
| Landlock rule installation failure | every `landlock_add_rule` and `landlock_restrict_self` return value | none | no intent | no restricted input or mutation | fail closed |
| seccomp installation failure | `PR_SET_NO_NEW_PRIVS`, TSYNC result, `/proc/self/status` | none | no intent | no post-start process/socket boundary | fail closed |
| unexpected open descriptor | `/proc/self/fd` inventory against pre-open handle manifest | none | no intent | descriptor set rejected | review |
| unexpected child or process | cgroup/process inventory and seccomp fork/clone denial | none | no intent | no child authority | fail closed |
| filesystem authority outside selected rule set | Landlock access result, fixed dirfds, no caller paths, openat2 resolution, capability postcondition | none | no intent | outside access denied or detected | review/fail closed |
| changed path identity after restriction | repeat `statx`/`fstatat`, mountinfo, descriptor and digest checks | none | frozen/review | changed object not consumed | review |
| incomplete raw evidence | exact entry inventory and M127A input check | none | no intent | unchanged | rejected/review |
| object byte substitution | fixed path, length, digest, trailer, signed object set | none | no intent | unchanged | review |
| malformed or oversized bundle | binary framing and all limits | none | no intent | unchanged | rejected |
| read-only import-media replacement or remount | device major/minor, filesystem identity, source, flags, path, bytes, digest | no archive or inbox mutation before check | no disposition | source invalid; medium remains evidence | review |
| ready-file ambiguity | inbox inventory and exact digest comparison | ingress review only | no intent | unchanged | review |
| replayed nonce | SQLite uniqueness and transaction binding | none | prior result unchanged | unchanged | rejected or idempotent result |
| reused/stale generation | floor and reservation uniqueness | none | floor unchanged | unchanged | rejected |
| SQLite corruption or WAL/SHM loss | schema, integrity, owner/mode, sidecar and audit checks | none | preserve evidence | unchanged | review |
| disk full or fsync failure | bounded file/dir/SQLite result | exact restore only | prior/review | uncertain effect retained | review |
| partial publication or failed restoration | phase, retained prior identity, all-five observation/postcondition | restoration only | `PUBLISHING` or restoring/review | mixed set unusable or partial retained | restore/review |
| failed Observation or Verification | independent reopen, rehash, metadata, namespace/path and evidence checks | none | no active state | unchanged or partial observed | review |
| expired or revoked evidence | trusted time, signed validity, revocation and frozen transaction rules | none for new work | frozen only | no new publication | fresh evidence/review |
| network/socket policy drift | effective unit and seccomp policy, address-family result | none | no intent | unchanged | review |

## 18. Limitations and Trusted-Computing-Base Assumptions

This design does not prove production OS/image provenance, PID 1, kernel,
systemd version or effective policy, root filesystem, initial mount-namespace
equality, package provenance, root administrator, offline producer, real host
trust object, signing custody, production trust material, or the absence of TCB
compromise. The trusted computing base includes the kernel, PID 1, root
filesystem, immutable OS/image policy, fixed executables, and local root
administration. A compromised kernel, PID 1, root administrator, OS image,
filesystem implementation, or already-compromised trusted executable can bypass
or replace the observations and restrictions assumed here.

Landlock and seccomp enforcement are not implemented or deployment-verified.
Landlock is a hierarchy access-control layer, not an exact filename ACL; it does
not restrict every filesystem operation, and its pre-opened descriptors remain
usable after restriction. Seccomp cannot safely compare arbitrary pathname
pointers, and the fixed native vocabulary, openat2-equivalent resolution,
descriptor inventory, capability removal, and postconditions remain necessary.
The current host feature probe reports seccomp active but Landlock disabled;
unsupported or incomplete Landlock on an intended deployment fails closed.
Exact real-host binding remains design-only.

The design contract may still be reviewed and finalized as design-only evidence,
but the current probe host cannot execute the successful privileged-runner path.
A future Build milestone must not claim live Landlock enforcement on this host.
Successful-path verification requires a separately verified compatible kernel and
host profile, preferably an isolated test host or VM with Landlock ABI 3 or
newer. No deployment to the current host is justified unless its capability is
changed and independently reverified. Failure-closed behavior on an unsupported
host is required, but it is not a substitute for testing the successful
Landlock path.

It does not claim a live process, service, inbox, verified import medium, bundle,
SQLite database, host trust object, backup, live recovery, boot-time behavior,
target fsync semantics, cross-directory atomicity, production implementation,
deployment, rollback, host mutation, public Internet exposure, multi-instance
runtime, multi-agent runtime, Generic Act authority, or Tool-Operation-Capability
expansion. No production private keys are created or accessed. No M126A
production keys or exporter are claimed to exist. Tool-Operation-Capability
security remains a separate future frontier.

## 19. Exit Recommendation and Build Boundary

All fourth-targeted-corrective design questions are bounded sufficiently to recommend a
narrowly scoped implementation review, subject to PM decision:

```text
SELECTED_EXIT: EXIT_A
EXIT_A_MEANING: BOUNDED_PRIVILEGED_RUNNER_BUILD_JUSTIFIED_FOR_PM_REVIEW
```

EXIT_A is only a recommendation for a bounded implementation foundation whose
successful Landlock behavior must be tested on a compatible isolated test host
or VM. It does not imply current-host deployment readiness. It does not imply
runtime security proof. It does not imply successful Landlock enforcement on
this host. It does not imply production trust-bootstrap readiness or
authorization to upgrade or modify this host.

This is not finalization or build approval. Future implementation would require
a separately authorized inventory, complete raw-evidence adapter, OS/image and
PID 1 evidence, effective systemd policy verification, fixed-path and
restriction rehearsal,
failure injection, and deployment authorization. Build, production
implementation, deployment, rollback, target-host mutation, and successor work
remain unauthorized.

## 20. External Evidence Summaries

The initial and first-corrective summaries are preserved unchanged:

```text
/home/aether/summaries/milestone_128A_privileged_host_trust_bootstrap_runner_process_recovery_and_exact_root_authority_contract_proof_summary.txt
/home/aether/summaries/milestone_128A_corrected_privileged_host_trust_bootstrap_runner_process_recovery_and_exact_root_authority_contract_proof_summary.txt
```

The second-corrective summary is evidence only and is outside repository scope:

```text
/home/aether/summaries/milestone_128A_second_corrective_privileged_host_trust_bootstrap_runner_process_recovery_and_exact_root_authority_contract_proof_summary.txt
```

The third-corrective summary is evidence only and is outside repository scope:

```text
/home/aether/summaries/milestone_128A_third_corrective_privileged_host_trust_bootstrap_runner_process_recovery_and_exact_root_authority_contract_proof_summary.txt
```

The fourth-targeted-corrective summary is evidence only and is outside
repository scope:

```text
/home/aether/summaries/milestone_128A_fourth_targeted_corrective_privileged_host_trust_bootstrap_runner_process_recovery_and_exact_root_authority_contract_proof_summary.txt
```

The fifth-targeted-corrective summary is evidence only and is outside
repository scope:

```text
/home/aether/summaries/milestone_128A_fifth_targeted_corrective_privileged_host_trust_bootstrap_runner_process_recovery_and_exact_root_authority_contract_proof_summary.txt
```

The finalization summary is evidence only and is outside repository scope:

```text
/home/aether/summaries/milestone_128A_privileged_host_trust_bootstrap_runner_process_recovery_and_exact_root_authority_contract_proof_finalization_summary.txt
```

The finalization record updates `PROGRESS.md` and
`SECURITY_ARCHITECTURE.md` as the only current architectural/status ledgers;
the milestone contract remains otherwise unchanged.

## 21. Authoritative M128A Status

```text
AUTHORITATIVE_M128A_STATUS_BEGIN
M128A_AUTHORIZED: YES
M128A_STARTED: YES
M128A_FINALIZED: YES
M128A_TYPE: DESIGN_DISCOVERY_SECURITY_AND_OPERATIONS_CONTRACT_PROOF
DECISION_STATUS: CURRENT
DESIGN_STATUS: DESIGN_PROVEN
IMPLEMENTATION_STATUS: NOT_IMPLEMENTED
VERIFICATION_STATUS: TEST_VERIFIED
DEPLOYMENT_VERIFIED: NO
DEPLOYMENT_STATE: NOT_DEPLOYED
PRIVILEGED_RUNNER_IMPLEMENTED: NO
PROCESS_INDEPENDENT_RECOVERY_IMPLEMENTED: NO
EXACT_REAL_ROOT_BINDING_IMPLEMENTED: NO
PRODUCTION_OS_PROVENANCE_VERIFIED: NO
PRODUCTION_TRUST_MATERIAL_PROVEN: NO
PRODUCTION_PRIVATE_KEYS_CREATED: NO
PRODUCTION_PRIVATE_KEYS_ACCESSED: NO
HOST_TRUST_OBJECTS_INSTALLED: NO
LIVE_DEPLOYMENT_AUTHORIZED: NO
LIVE_ROLLBACK_AUTHORIZED: NO
TARGET_HOST_MUTATION_PERFORMED: NO
CURRENT_HOST_DEPLOYMENT_READY: NO
CURRENT_PROBE_HOST_LANDLOCK_STATUS: UNSUPPORTED_EOPNOTSUPP
CURRENT_PROBE_HOST_SUCCESS_PATH_RUNNABLE: NO
GENERIC_ACT_AUTHORIZED: NO
BUILD_AUTHORIZED: NO
PROGRESS_UPDATED: YES
SECURITY_ARCHITECTURE_UPDATED: YES
COMMIT_CREATED: YES
TAG_CREATED: YES
PUSH_PERFORMED: YES
SUCCESSOR_AUTHORIZED: NO
SUCCESSOR_NUMBER_ASSIGNED: NO
READY_FOR_PM_REVIEW: NO
AUTHORITATIVE_M128A_STATUS_END
```

M128A is finalized as Git-durable design/discovery/security-and-operations
contract proof only. EXIT_A remains only a future PM-review frontier for a
bounded implementation foundation; it does not authorize Build, deployment,
host mutation, or a successor. The current probe host remains Landlock
unsupported and not deployment-ready.
No production implementation, admitter, inbox, service, deployment, host
mutation, signing, private-key access, or successor milestone is claimed.
