# MILESTONE 122A OAS Repository Deployment Artifact Foundation Build

Document role: repository-only Build evidence. This document does not authorize
target deployment, host mutation, readiness, or deployment verification.

## 1. Authority and Scope

The authority order remains `CONSTITUTION > ARCHITECTURE >
SECURITY_ARCHITECTURE > CURRENT IMPLEMENTATION`. M121A design evidence remains
immutable historical evidence. M122A implements only the repository and
isolated-root deployment artifact foundation for the existing OAS contract.

The Build includes a fixed production entrypoint, native systemd notification,
canonical manifest and approval envelope validation, offline dependency closure,
four-unit generation verification, capability-bound isolated-root installation,
typed activation lifecycle, transaction-bound quiescence evidence, release
verification, and bounded non-deployment evidence collection. The current
correction adds a standalone dependency-free fixed verifier artifact, a root-side
pre-`CANDIDATE_PENDING` trust transaction, immutable canonical trust evidence,
exact release inventory, installed dependency `RECORD` verification, actual
interpreter/module probing, and explicit socket descriptor names. The candidate
entrypoint does not import or call the repository release-verifier module.

## 2. Explicit Exclusions

No live host was changed. No users, groups, mounts, services, sockets, systemd
state, production credentials, private keys, Owner authentication, WebAuthn,
TLS, recovery ceremony, AuthenticatedSourceEvent, Core receipt, Generic Act,
generalized Tool-Operation-Capability authority, public Internet, multi-agent
runtime, or multi-instance runtime was added.

## 3. Artifact Inventory

| Surface | Repository artifact | Boundary |
| --- | --- | --- |
| Entrypoint | `aether/oas/host_entrypoint.py` | Fixed protocol environment, activation identity, manifest, unit, runtime snapshot, and gate checks precede `READY=1` |
| Notification | `aether/oas/systemd_notify.py` | Native AF_UNIX datagram only; no subprocess fallback |
| Manifest | `aether/deployment/manifest_schema.py`, `manifest_generator.py` | Closed nested schema, canonical JSON, file/unit/Git/runtime binding |
| Trust verification | `aether/deployment/trust_bootstrap.py` | Root-side verification orchestration; the candidate entrypoint has no release-signature authority |
| Fixed trust artifact | `deployment/fixed_verifier/aether-release-verify`, `aether/deployment/trust_bootstrap.py` | Root-side fixed artifact identity, independent approvals, pre-pending verification, and durable transaction-bound evidence |
| Dependencies | `deployment/requirements.lock.json`, `deployment/wheelhouse/` | 16 pinned, hashed, size-bound Python 3.11 Linux x86_64 wheels; offline-only policy |
| Unit generation | `deployment/systemd/`, `aether/deployment/unit_verifier.py` | Complete ordered four-unit bundle and generation gate |
| Installation | `aether/deployment/installer.py` | Explicit isolated-root capability; no host default or shell command path |
| Lifecycle | `aether/deployment/lifecycle.py` | Canonical activation record, bounded transitions, durable writes, typed quiescence proof |
| Evidence | `aether/deployment/evidence_collector.py` | Bounded, redacted, explicitly non-deployment evidence |

## 4. Safety Invariants

Temporary-root authority is issued only for an absolute existing directory that
is not a protected host root, development checkout, symlinked path, writable by
group/other, or missing the process-local sentinel. Mutating isolated-root
operations require the matching capability and process identity. Production
root access is available only through the explicit fixed entrypoint read path;
the installer and lifecycle write paths cannot select it.

All candidate files reject symlinks and special files. New files use exclusive
creation and no-follow flags where applicable. File and directory durability
boundaries are fsynced before identity is advanced. Existing generation gates
are never silently overwritten.

The root trust operation reads the anchor and approval digests only from fixed
root-owned paths, verifies the fixed verifier's owner, mode, hard-link identity,
and approved digest, invokes the standalone verifier with a fixed environment,
and writes one immutable canonical evidence file per transaction. A retry may
replay the identical evidence; conflicting evidence cannot replace it. The
candidate reads this evidence as a gate and has no release-signature authority.

The M121A manifest source shape binds commit, tree, and root digest. M122A does
not invent a source tag field or derive a synthetic tag from the commit.

Activation cannot reach `ACTIVATING` without a valid typed quiescence proof.
Quiescence requires inactive service and socket units, zero OAS processes, zero
accepted connections, and zero outstanding workers for the transaction.

## 5. Verification Evidence

Named focused tests are present under `tests/test_oas_host_entrypoint.py`,
`tests/test_oas_systemd_notify.py`, `tests/test_deployment_manifest_schema.py`,
`tests/test_deployment_manifest_generator.py`,
`tests/test_deployment_fixed_verifier.py`,
`tests/test_deployment_installer.py`, `tests/test_deployment_lifecycle.py`,
`tests/test_deployment_unit_verifier.py`,
`tests/test_deployment_evidence_collector.py`,
`tests/test_deployment_dependency_lock.py`, and the retained M122A lock.

The dependency closure verifier reports `COMPLETE` for 16 artifacts. The current
focused M122A surface includes a complete signed-release transaction fixture
using the real lock and wheelhouse, real Ed25519/OpenSSL verification, all four
units, immutable evidence, retry/revalidation, revocation, changed-input,
concurrency, crash-ordering, and dependency rejection tests. The complete
repository suite passes 3,556 tests with 10 existing warnings.
Compilation and `git diff --check` pass. `systemd-analyze verify` passes in an
isolated temporary root containing the four units, their target dependencies,
the activation gates, and a temporary interpreter placeholder; this remains
static verification only and is not deployment evidence.

## 6. Authoritative Status

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
SUCCESSOR_AUTHORIZED: NO
SUCCESSOR_NUMBER_ASSIGNED: NO
READY_FOR_PM_REVIEW: NO
PROGRESS_UPDATED: YES
COMMIT_CREATED: YES
TAG_CREATED: YES
PUSH_PERFORMED: YES
```

The original M122A finalization commit is
`76901b6fb619776e0fbc53c5a30995faa5bcf070`, and the original milestone tag is
`milestone-122A-oas-repository-deployment-artifact-foundation`. This correction
is metadata consistency only: it removes contradictory duplicate completion
markers and changes no implementation or deployment state.

The Build stops at this evidence boundary. No M122B, M123, or other successor
is authorized or numbered.
