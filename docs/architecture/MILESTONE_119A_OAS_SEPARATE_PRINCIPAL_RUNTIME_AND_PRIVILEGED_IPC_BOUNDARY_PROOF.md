# M119A OAS Separate-Principal Runtime and Privileged IPC Boundary Proof

Document role: DESIGN / DISCOVERY / HOST-SECURITY-CONTRACT PROOF ONLY

This is a corrective M119A design record pending project-manager review. It is
subordinate to the Constitution, the overall Architecture, and the canonical
Security Architecture. It is not a new authority layer and does not authorize
production implementation, host configuration, a Build, or a successor
milestone.

## 1. Authority, Scope, and Corrected Decision

The preserved authority precedence is:

```text
CONSTITUTION
    >
ARCHITECTURE
    >
SECURITY_ARCHITECTURE
    >
CURRENT IMPLEMENTATION
```

Milestone records are design evidence and traceability records, not another
authority layer. Aether remains one persistent digital mind. AetherOS is its
operating environment and body. OAS is a bounded authority service, not a
second mind, agent, or cognitive runtime. Authentication is not intent
interpretation. Goal acceptance is not Action authorization. Action success is
not completion. Completion requires Observation and Verification.

The corrected M119A property is:

```text
ORDINARY_AETHER_RUNTIME
CANNOT
DIRECTLY READ, MUTATE, REPLACE, OR OPERATE
CANONICAL OAS SECURITY STATE
```

The selected design is Model D: a dedicated OAS service principal, a distinct
ordinary runtime service principal, a distinct human Owner login principal, a
root-owned local-console broker, and a dedicated bootstrap helper. The design
is internally executable on a host with the specified future accounts,
systemd units, PAM/logind support, filesystem modes, and socket activation.
None of those deployment objects exists as a result of this record.

M118A proves only a bounded durable SQLite security kernel. This correction
does not design WebAuthn request semantics, Goal operations,
AuthenticatedSourceEvent issuance, Generic Act, generalized
Tool-Operation-Capability authority, a generic identity registry, public
Internet exposure, multi-instance runtime, or multi-agent runtime expansion.
HA1 and GI2 remain incomplete.

The orthogonal status dimensions are:

```text
DECISION_STATUS: PROPOSED
DESIGN_STATUS: DESIGN_PROVEN
IMPLEMENTATION_STATUS: NOT_IMPLEMENTED
VERIFICATION_STATUS: TEST_VERIFIED
DEPLOYMENT_VERIFIED: NO
```

`TEST_VERIFIED` means only that the repository static proof verifies this
record's structure. It is not host configuration evidence, runtime proof, or
deployment verification.

## 2. Read-Only Discovery and Current Truth

Discovery was read-only. No host user, group, service, socket, credential,
permission, deployment file, or repository artifact was created or changed.
No password hashes, private keys, tokens, credentials, or unrelated personal
information were read or recorded.

### 2.1 Host facts

| Fact | Observed result | Consequence |
| --- | --- | --- |
| Operating system | Debian GNU/Linux 12 (bookworm), x86_64 | Linux Unix-domain peer credentials are available |
| Kernel | Linux 6.8.12-20-pve | The host kernel remains part of the trust base |
| Init/service manager | systemd 252, PID 1, system running | A future unit/socket-activation design is available |
| Current login/development principal | `aether`, uid/gid 1000 | Discovery fact only; not the future runtime or Owner boundary |
| Current supplementary groups | `aether`, `sudo`, `users` | Current account is not suitable as an ordinary service identity |
| Dedicated OAS identity | No `oas` user or group exists | No OAS principal is deployed |
| Filesystem | ext4 on `/dev/mapper/pve-vm--111--disk--0`, read-write root mount | POSIX ownership and mode controls are available |
| Unix IPC | `AF_UNIX`, `SO_PEERCRED`, `SCM_CREDENTIALS`, `SCM_RIGHTS` available | Kernel peer authentication and trusted internal descriptor passing are possible |
| Isolation tools | `setpriv`, `unshare`, `nsenter` available | Tools exist but no M119A isolation is deployed |
| Container tools | Docker and Podman not found | Containers are not the current deployment model |
| ACL/MAC tools | `getfacl`, `aa-status`, and `getenforce` not available | No ACL/MAC deployment evidence was established |

The repository, `/home/aether/data`, and `/home/aether/data/private` are owned
by `aether:aether`; the repository and private-data directory are currently
mode `0755`. The current development account is login-capable and belongs to
sudo. These are not accepted deployment permissions.

### 2.2 Current runtime, data, and startup

The current API server constructs FastAPI at import time and has no OAS
import, startup/lifespan hook, authentication middleware, TLS listener, or
service launcher. The current runtime creates one process-global
`AetherRuntime` with process-local state. `/chat` explicitly disables tool
execution. No current path starts a separate OAS process.

The `aether.oas` public package is empty and no production module outside
`aether/oas` imports the kernel. This is only a static code/dependency
boundary. The kernel remains directly importable as a submodule, accepts a
caller-supplied SQLite path, and does not authenticate its initiator.

Configured runtime data is under `/home/aether/data`, with private data under
`/home/aether/data/private`. M118A's SQLite path is caller-supplied rather
than centrally deployed. No Aether or OAS service/socket unit, container
definition, init script, supervisor configuration, or other deployment
artifact exists in the repository or is installed for this host.

## 3. Corrected Principal Model

The current `aether` uid 1000 account is a human/development discovery fact
only. It is not assigned to the ordinary runtime in the target contract.

| Role | Target principal | Exact authority |
| --- | --- | --- |
| Human Owner login | `aether-owner`, dedicated local-login uid/gid | May initiate the fixed local-console authorization ceremony after fresh PAM authentication and TTY confirmation; no OAS state or service ownership |
| Ordinary Aether runtime | `aether-runtime`, dedicated non-login service uid/gid | May connect only to the OAS runtime read-result socket; no Owner session, sudo, polkit, helper, state, code, unit, or backup authority |
| OAS service | `aether-oas`, dedicated non-login service uid/gid | Operates canonical OAS state and receives systemd-activated OAS sockets; no installer or service-manager authority |
| Bootstrap helper | `aether-bootstrap`, dedicated non-login helper uid/gid | Receives one in-memory context over a broker-created private descriptor and may submit only the two bounded bootstrap operations |
| Installer/lifecycle administrator | `root` through explicitly bounded host procedures | Installs immutable code, creates identities/directories/units, starts/stops/upgrades, and performs approved recovery/migration/backup procedures |

The human Owner login principal and ordinary runtime service principal never
share a uid. `aether-runtime`, `aether-oas`, and `aether-bootstrap` are not
login-capable, do not share supplementary groups, and are never members of
the human Owner group. The ordinary runtime is not a member of the bootstrap,
OAS, or installer groups. The current `aether` account's sudo membership and
session bus are not inherited by `aether-runtime`.

The human Owner entitlement is the target local account `aether-owner`, access
to the systemd-created `owner-broker.sock` through its dedicated group, and
the broker's logind/PAM/TTY checks described below. It is not an undefined
group-plus-seat assertion. A local seat without fresh authentication is
insufficient.

## 4. Candidate Models and Launcher Selection

| Candidate | Authority and filesystem | Invocation and authentication | Verdict |
| --- | --- | --- | --- |
| A. Root-owned AF_UNIX privileged broker | Broker can own the human endpoint and launch a helper, while OAS state remains `aether-oas`-owned | Obtains human `SO_PEERCRED`, logind session evidence, and fresh PAM/TTY confirmation; exact context handoff is broker-held | Selected exact mechanism: one root broker with no arbitrary arguments or paths |
| B. Polkit/PAM-mediated privileged launcher | Helper and OAS can remain separate principals; state ownership is independent | A standalone launcher has no authenticated shell peer and polkit handoff to a one-use helper context is not defined here | Rejected; not internally executable without adding a broker/context carrier |
| C. Tightly scoped sudo/PAM command | Separate helper uid is possible, but sudo policy and environment/TTY behavior are host-specific | Fresh PAM can be required, but caller identity and one-use context handoff would rely on an unsafe ambient carrier | Rejected; insufficiently precise for this host-security proof |
| D. Other mechanism | Could be made equivalent only with a complete peer, presence, and context contract | No alternate mechanism is needed after selecting A | Not selected |
| E. No truthful model | Would stop without a host contract | Not required because systemd, Unix credentials, PAM/logind design, and POSIX modes provide a credible target | Not selected |

The exact selected launcher architecture is A. No properties from polkit,
sudo, or a standalone shell launcher are used:

```text
HUMAN OWNER aether-owner
  -> owner-broker.sock via SO_PEERCRED
  -> root owner broker: logind active-local-session gate
  -> one-shot PAM authentication and TTY confirmation
  -> broker registers one-use context on OAS broker.sock
  -> root broker launches fixed /usr/libexec/aether-oas-bootstrap
     as aether-bootstrap over a private inherited descriptor
  -> helper presents context on OAS bootstrap.sock via SO_PEERCRED
  -> M118A-bound OAS transaction and audit
```

The target mechanism is a root-owned broker with its own activated AF_UNIX
endpoint, not a standalone executable that claims to receive the human
shell's `SO_PEERCRED`. The broker receives the authenticated kernel peer
credentials directly, performs the host session and PAM checks, and retains
the resulting authorization context in memory while launching only the fixed
helper. The broker has no generic command or file-path authority.

## 5. Human Presence, Fresh Authentication, and Intent

The exact future caller is the local-login user `aether-owner`, with a
dedicated primary group of the same name. The exact entitlement source is the
systemd-created `owner-broker.sock` group permission plus the root broker's
exact uid and session checks. The broker requires:

```text
peer.uid == uid(aether-owner)
logind.User == aether-owner
logind.Active == true
logind.Remote == false
logind.Type == tty
logind.Class == user
```

The root broker invokes PAM directly using `pam_start` with the dedicated PAM
service `aether-oas-owner-bootstrap`, then `pam_acct_mgmt` and
`pam_authenticate` for `aether-owner`. It sets `PAM_TTY` to the controlling TTY
returned by logind and leaves `PAM_RHOST` empty. The PAM stack performs fresh
interactive authentication with no cached authorization. The broker rejects
a missing TTY, a noninteractive request, SSH, remote terminals, forwarded
agents, API calls, environment claims, and background service invocation. The
authentication evidence expires after 60 seconds and is consumed once.

Fresh authentication is not itself fresh intent. After PAM succeeds, the
fixed launcher displays a confirmation line on the same TTY containing the
exact operation `BEGIN_LOCAL_BOOTSTRAP_WINDOW`, the exact Aether Instance ID,
the current trust generation, and a fresh 128-bit confirmation nonce. The
human must type the displayed confirmation within 60 seconds. The nonce is
generated by the trusted launcher, is not caller-selected, and is accepted
once. A mismatched, expired, cancelled, or noninteractive confirmation fails
closed and is audited as a rejected attempt.

The root broker first asks OAS for an instance-bound challenge over
`broker.sock`; the Aether Instance ID and expected generation therefore come
from OAS and cannot be selected by the human. The final authorization is
bound to the challenge, operation, request identity, instance ID, and expected
trust generation.

`aether-runtime` cannot invoke or satisfy this ceremony because it has a
different uid, is not in the Owner group, fails the broker's peer and logind
checks, cannot access the Owner TTY or session bus, cannot supply fresh PAM
authentication or human confirmation, and cannot execute the fixed launcher
as `aether-bootstrap`.

## 6. Exact Authorization Context Contract

The authorization context is broker-held and OAS-registered, not a file,
environment variable, command-line argument, or runtime-readable token.

| Field | Contract |
| --- | --- |
| Creator | The root owner broker after fresh PAM success and TTY confirmation |
| Form | 256-bit random opaque `context_id`; all authority fields are retained by OAS, not encoded in a caller token |
| Registration | Root broker sends the full authorization record to OAS's broker channel; OAS stores it in memory until one use or expiry |
| Required bindings | Protocol version, context ID, request ID, operation, Aether Instance ID, expected trust generation, authentication event ID, Owner login uid, logind session ID, issue time, monotonic expiry, helper invocation nonce, one-use flag |
| Lifetime | Maximum 60 seconds by monotonic clock; wall-clock time is audit metadata only |
| Helper handoff | Root broker creates a private `AF_UNIX` `SOCK_SEQPACKET` socketpair, forks the fixed helper, drops it to `aether-bootstrap`, and sends the context frame over inherited descriptor 3; no environment or argument carries authority |
| OAS validation | OAS checks helper `SO_PEERCRED` uid, context ID, helper invocation nonce, request ID, operation, expiry, one-use state, and its server-held instance/generation record |
| PID handling | PID is audit-only and never an authority binding; a pidfd/start-time check may identify the launcher process, so PID reuse cannot authorize a context |
| Theft/replay | Context exists only in broker/OAS memory, is one-use, expires, and is bound to the expected helper invocation; changed content or a second use is a conflict |
| Cancellation | Launcher revokes the server-held context and helper closes descriptor 3; OAS records cancellation or expiry and never continues silently |
| Lost reply | Retry uses the same request ID/context ID; OAS returns the one committed result or an explicit conflict/unavailability result |
| Consumer/revoker | Only OAS consumes the context for a bootstrap transaction; launcher may request revocation before use; OAS revokes all volatile contexts on service restart |
| Audit | OAS owns the durable audit event; it records context/request/authentication event IDs, operation, instance/generation, result class, and timestamps, never passwords or raw credentials |

The private socketpair descriptor passing is internal launcher-to-helper
transport created by the trusted launcher. It is not client-supplied
`SCM_RIGHTS`. OAS-facing clients cannot send ancillary descriptors; OAS
rejects `SCM_RIGHTS` and all unexpected ancillary data. A compromised ordinary
runtime cannot obtain the socketpair, context ID, OAS broker channel, or
helper uid.

## 7. Filesystem Contract

The target persistent state path is `/var/lib/aether/oas`, not the current
developer path. The target runtime path is `/run/aether/oas`. Root creates and
verifies these paths during installation; OAS does not create parent
directories or change ownership.

| Object | Owner | Mode | Authority rule |
| --- | --- | --- | --- |
| Installed OAS code and fixed launcher | `root:root` | directories `0755`, files `0644`, executable `0755` | `aether-runtime` cannot modify, replace, or inject code |
| `/var/lib/aether` | `root:root` | `0755` | Traversal only; no ordinary write |
| `/var/lib/aether/oas` | `aether-oas:aether-oas` | `0700` | Only OAS can access persistent state; root remains host trust base |
| SQLite database | `aether-oas:aether-oas` | `0600` | No ordinary read, mutate, replace, attach, or truncate |
| SQLite `-wal` and `-shm` | `aether-oas:aether-oas` | `0600` | Side files stay in the mode-0700 state directory |
| OAS migration/temp files | `aether-oas:aether-oas` | files `0600` in mode `0700` directory | No caller-selected path or shared `/tmp` use |
| Backup staging | `root:root` | `0700` | Administrator-only staging |
| Restored state | `aether-oas:aether-oas` | directory `0700`, files `0600` | Ownership/modes reset before restart |
| `/run/aether/oas` | `root:root` | `0755` | Systemd creates/removes socket entries; OAS has no directory write |

The ordinary runtime service has no write permission to code, units, state,
WAL/SHM, runtime directory, backups, logs, or helper. OAS uses `UMask=0077`
for files it creates inside its state directory. Startup fails closed for a
wrong owner, mode, symlink, mount, regular-file type, or unexpected side file.

## 8. Systemd Socket-Activation and Responsibility Contract

Model S1, systemd socket activation, is selected. OAS never binds, chowns,
renames, or removes endpoint files. Root-owned systemd socket units create and
clean them, and pass only the expected listening descriptors to their target
service.

### 8.1 Socket units

Every socket unit uses `ListenSequentialPacket=`, `Accept=no`,
`DirectoryMode=0755`, `Backlog=64` except the owner broker's `Backlog=8`,
`RemoveOnStop=yes`, and an exact path below `/run/aether/oas`.

| Unit | Listen path | SocketUser | SocketGroup | SocketMode | Receiver |
| --- | --- | --- | --- | --- | --- |
| `aether-oas-runtime.socket` | `/run/aether/oas/runtime.sock` | `aether-oas` | `aether-runtime` | `0660` | `aether-oas.service` |
| `aether-oas-bootstrap.socket` | `/run/aether/oas/bootstrap.sock` | `aether-oas` | `aether-bootstrap` | `0660` | `aether-oas.service` |
| `aether-oas-broker.socket` | `/run/aether/oas/broker.sock` | `aether-oas` | `root` | `0660` | `aether-oas.service` |
| `aether-oas-owner-broker.socket` | `/run/aether/oas/owner-broker.sock` | `root` | `aether-owner` | `0660` | `aether-oas-owner-broker.service` |

The OAS service receives exactly three descriptors named runtime, bootstrap,
and broker. It verifies `LISTEN_PID`, descriptor count, `SOCK_SEQPACKET`
type, listening state, `AF_UNIX` family, expected socket path, `fstat` owner,
group, mode, device/inode match to the path, and endpoint role before serving.
It rejects missing, extra, duplicated, or substituted descriptors. The owner
broker receives exactly one activated owner-broker descriptor and performs the
same type/path/inode checks. No client can create, rename, replace, or remove
these sockets because the parent directory and systemd lifecycle are root
owned.

### 8.2 OAS service unit target

The future `aether-oas.service` target is:

```text
User=aether-oas
Group=aether-oas
SupplementaryGroups=
UMask=0077
RuntimeDirectory= (not used; socket units own /run/aether/oas)
StateDirectory= (not used; root provisions /var/lib/aether/oas explicitly)
NoNewPrivileges=yes
PrivateTmp=yes
PrivateDevices=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/var/lib/aether/oas
RestrictAddressFamilies=AF_UNIX
RestrictSUIDSGID=yes
CapabilityBoundingSet=
AmbientCapabilities=
LimitCORE=0
Restart=on-failure
RestartSec=2s
TimeoutStartSec=30s
TimeoutStopSec=10s
Type=notify
NotifyAccess=main
```

The unit has no `ExecStartPre` that edits state as root. It starts after local
filesystem availability and socket units, validates the three activated
descriptors and state directory, performs M118A WAL/schema/integrity startup
checks as `aether-oas`, and sends readiness only after all checks pass. SQLite
WAL and SHM files are within the one allowed write path. OAS does not need
write access to `/run/aether/oas` because descriptors are already open.

### 8.3 Owner broker service unit target

The future `aether-oas-owner-broker.service` is root-owned because it must run
the host PAM/logind gate and drop the helper to its dedicated uid:

```text
User=root
Group=root
SupplementaryGroups=
UMask=0077
NoNewPrivileges=no
PrivateTmp=yes
PrivateDevices=no
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=
RestrictAddressFamilies=AF_UNIX
RestrictSUIDSGID=yes
CapabilityBoundingSet=CAP_SETUID CAP_SETGID
AmbientCapabilities=
LimitCORE=0
Restart=on-failure
RestartSec=2s
TimeoutStartSec=30s
TimeoutStopSec=10s
Type=notify
NotifyAccess=main
```

`PrivateDevices=no` is required only because the broker must use the verified
local controlling TTY for the PAM conversation. The broker reads the future
PAM configuration and logind session metadata, but has no OAS state path,
backup path, arbitrary executable, or shell authority. Its only output is the
fixed helper invocation and the OAS broker protocol. The broker drops all
supplementary groups, sets the helper uid/gid exactly, closes all unrelated
descriptors, passes only descriptor 3, and execs the root-owned fixed helper.

The broker is ordered after `aether-oas-broker.socket` and the activated owner
socket, and it fails requests with bounded unavailability if OAS is not ready.
The runtime and bootstrap socket units require the OAS service. Runtime and
bootstrap socket backlog is 64; OAS allows at most 32 active and 64 queued
requests. The owner broker allows at most four active ceremonies and eight
queued connections. Runtime requests have a one-second deadline, bootstrap
requests five seconds, and the owner ceremony 60 seconds. OAS startup and
shutdown timeouts are 30 and 10 seconds; owner broker shutdown is 10 seconds.

## 9. OAS IPC Protocol and Allowed Operations

OAS accepts `AF_UNIX` `SOCK_SEQPACKET` frames only. It validates
`SO_PEERCRED` on every accepted connection and ignores caller-supplied uid,
gid, pid, role, environment, path, and source address. The runtime endpoint
accepts only exact `aether-runtime`; the bootstrap endpoint accepts only exact
`aether-bootstrap`; the broker endpoint accepts only the root-owned broker
protocol. `SCM_RIGHTS` and all unexpected ancillary data are rejected on
client connections.

The runtime operation vocabulary is exactly:

```text
PING
GET_BOUNDED_RUNTIME_STATUS
```

The bootstrap operation vocabulary is exactly:

```text
BEGIN_LOCAL_BOOTSTRAP_WINDOW
CANCEL_LOCAL_BOOTSTRAP_WINDOW
```

The root broker vocabulary is exactly:

```text
ISSUE_LOCAL_BOOTSTRAP_CHALLENGE
REGISTER_LOCAL_BOOTSTRAP_AUTHORIZATION
REVOKE_LOCAL_BOOTSTRAP_AUTHORIZATION
```

No endpoint accepts SQL, arbitrary method names, filesystem paths, backup
paths, migration paths, credentials, WebAuthn requests, Goal operations,
source events, Generic Act, or generic mutation requests. Runtime results are
at most 4096 bytes and contain only bounded non-secret availability, protocol,
schema, and redacted readiness classifications. They never return canonical
records, raw audit rows, credentials, recovery material, database paths, or
SQL errors.

Each frame is one versioned canonical request object no larger than 16384
bytes. Oversized, truncated, multi-object, unknown-field, unknown-version,
non-canonical, expired, and ancillary-data-bearing frames fail closed. The
envelope includes protocol version, request ID, operation, caller class,
deadline, and payload digest. Request identity and M118A transaction identity
are required for bootstrap mutation; identical retries may return one
committed result, while changed-content reuse is a conflict.

## 10. Startup, Crash, Shutdown, Migration, and Backup

Startup ordering is:

1. Root-owned systemd socket units create the parent directory and four
   endpoint files with their exact owner/group/mode and pass descriptors.
2. OAS validates descriptor count/type/path/inode and state ownership/modes.
3. OAS performs bounded M118A WAL setup, schema validation, integrity checks,
   and startup migration as `aether-oas`.
4. OAS validates broker peer policy and publishes readiness only after all
   endpoints are safe.
5. The ordinary runtime receives only the runtime socket's bounded results.

Any failed check stops service readiness. There is no weaker journal mode,
ordinary-runtime database, shared socket, alternate path, or client-selected
fallback. Systemd owns endpoint creation and cleanup on service/socket stop;
OAS only closes its descriptors and never recursively removes a directory.

On crash, SQLite atomicity rolls back incomplete canonical state and audit
work. Clients receive bounded unavailability and retry with the same request
identity. On restart OAS revalidates state, WAL/SHM ownership, and activated
descriptors; all volatile authorization contexts are revoked. A stale socket
cannot be replaced by OAS or a client because systemd owns the parent and
socket lifecycle.

Only root may install or upgrade code/units, start/stop services, stage
backups, or restore state. OAS performs normal schema migration as itself at
startup. An offline migration or restore stops OAS, uses an allowlisted OAS
procedure as `aether-oas`, validates schema/integrity/identity/generation,
resets ownership/modes, and restarts. Backups are root-owned mode `0700` and
are never selected by the runtime or helper. Audit records remain OAS-owned.
Logs contain only bounded non-secret classifications and IDs; they never
contain credentials, recovery material, Claim Token plaintext, SQL payloads,
database bytes, or raw private records. Service core dumps are disabled.

## 11. Threat Model and Corrected Runtime Analysis

| Threat | Control and prevention | Residual risk |
| --- | --- | --- |
| Compromised `aether-runtime` process | Different uid, no state/code/unit write, no Owner/bootstrap group, runtime socket read-only | It can consume allowed status and attempt denial of service |
| Runtime becomes human Owner | `aether-runtime` is a non-login uid distinct from `aether-owner`; no Owner group or session bus access | A host administrator can reconfigure identities |
| Runtime invokes privileged launcher | Polkit subject uid, active/local/nonremote tty rule, fresh PAM, nonce confirmation, fixed executable | A valid human Owner can authorize the limited ceremony |
| Runtime satisfies fresh human authentication | Cannot access Owner TTY/session bus or provide PAM secret and human nonce; no environment claim is trusted | Same-uid Owner compromise is outside the runtime threat because uids are distinct |
| Runtime joins Owner/bootstrap groups | Groups are root-provisioned and service has no group-management authority | Root can change group membership |
| Runtime executes helper as target uid | No launcher execution, no setuid helper, root-owned executable and broker-only descriptor handoff | Root compromise can execute it |
| Runtime connects to bootstrap endpoint | Socket mode/group and exact `SO_PEERCRED` require `aether-bootstrap` | A compromised helper uid could use its limited vocabulary |
| Runtime steals/replays context | No readable context file/env/argv; context is broker/OAS memory, one-use, 60-second monotonic expiry, helper nonce-bound | Root, kernel, or a compromised broker/helper can access its own live context |
| Runtime writes OAS code or units | Installed image and units are root-owned and non-writable | Root/operator installation error remains possible |
| Runtime writes state/WAL/SHM | State directory `0700`, files `0600`, separate uid, no parent write | Root can bypass modes |
| Runtime writes socket directory | Parent is root-owned and systemd-created; OAS has no directory write | Root/systemd compromise can replace endpoints |
| Runtime accesses backups/logs | Root-owned backup staging and restricted log policy | Host log/backup administrator can access them |
| Runtime uses status as mutation oracle | Runtime result is bounded readiness/status only; no canonical records, SQL, operation result, or mutation call | Availability pressure and metadata leakage within the fixed result remain |
| Socket activation widens authority | Exact systemd descriptor count/type/path/inode/owner/mode checks; endpoint role is fixed | A malicious root systemd configuration defeats local checks |
| Service restart widens authority | Atomic SQLite transactions, context revocation, descriptor validation, no fallback | Repeated crashes can deny service |
| Root/administrator compromise | Explicitly not prevented | Root can read, mutate, replace, impersonate, or disable every local boundary |

The ordinary runtime cannot inherit the human's sudo, polkit, session-bus,
TTY, agent, environment, or credential authority because it runs under a
separate non-login uid. The current `aether` account's shared development
properties are not part of the target runtime contract.

Root remains the host trust base. Kernel, systemd-manager, host-TCB, physical,
and equivalent privilege compromise are outside this proof. No protection
against root compromise is claimed.

## 12. Test and Deployment-Verification Boundary

The static M119A test verifies the structured design record, tables, exact
principal separation, selected root-broker/PAM chain, context lifecycle, socket
activation ownership, exact systemd values, threat coverage, exclusions, and
status. It does not create or inspect host objects.

Later host tests must verify actual target users/groups and non-login shells;
root-owned installed code and units; database/WAL/SHM modes; socket type,
owner, group, mode, activation descriptors and peer credentials; root-broker/logind
session facts; one-shot PAM and TTY confirmation; context expiry/replay/PID
reuse behavior; helper uid transition; crash/restart/migration/backup
behavior; effective systemd hardening; and secret-free logs. These tests are
not deployment verification until run against the reviewed target deployment.

The selected model is not deployed. The repository, current private-data
directory, current `aether` uid, and current absence of service units are
discovery facts, not proof of the target boundary.

## 13. Explicit Exclusions and M119A Status

This finalized record does not itself establish:

- production OAS code or service behavior;
- users, groups, services, sockets, credentials, PAM/polkit rules, sudoers, or deployment files;
- host permission or filesystem changes;
- canonical Security Architecture or PROGRESS.md status;
- WebAuthn request semantics or Owner credential semantics;
- Goal operations, Goal Intake integration, or Core receipts;
- AuthenticatedSourceEvent issuance;
- Generic Act or generalized Tool-Operation-Capability authority;
- a generic identity registry;
- public Internet, multi-instance, or multi-agent runtime expansion;
- a Build milestone or a successor milestone number.

The exact M119A lifecycle/status block is:

```text
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
PROGRESS_UPDATED: YES
SECURITY_ARCHITECTURE_UPDATED: YES
COMMIT_CREATED: YES
TAG_CREATED: YES
PUSH_PERFORMED: YES
SUCCESSOR_NUMBER_ASSIGNED: NO
PM_ACCEPTED: YES
```

Selected exit: `EXIT_A`.

`EXIT_A` means the corrected separate-principal, human-presence, launcher,
authorization-context, socket-ownership, and systemd contracts are internally
executable and complete enough to recommend a narrowly scoped Build for PM
review. It is not Build authorization. No successor number is assigned.
