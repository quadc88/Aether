# Milestone 108A Patch Security Residual State and Next-Direction Boundary

Classification: STRICT READ-ONLY SECURITY-STATE CONSOLIDATION / NEXT-DIRECTION
DECISION

Status: REVIEW COMPLETE LOCALLY / PATCH SECURITY PAUSE / CORE ARCHITECTURE
CONSUMER-PROOF FRONTIER IDENTIFIED

M108A does not implement a patch security fix, modify patch runtime, alter
approval semantics, choose canonical patch authority, or implement Generic Act.
It consolidates the post-M105B/M107B state and chooses one next-direction model.

## 1. Current Git State

Git is authoritative. At M108A review start:

- branch: `main`;
- `HEAD`: `02b5bc72c5fa707bcbd4fc487ec3022e22bb2179`;
- local `main`: `02b5bc72c5fa707bcbd4fc487ec3022e22bb2179`;
- `origin/main`: `02b5bc72c5fa707bcbd4fc487ec3022e22bb2179`;
- remote `refs/heads/main`: `02b5bc72c5fa707bcbd4fc487ec3022e22bb2179`;
- tracked worktree: clean;
- `git diff --check`: clean;
- M107B durable tag:
  `milestone-107B-final-reviewed-base-execution-guard`;
- M108A creates only this design candidate and its static/document lock as
  local untracked evidence.

No `PROGRESS.md`, README, Constitution, Architecture, production, existing
test, dependency, route, API, or runtime/private-data change is authorized by
M108A.

## 2. M107B Durable Baseline

M107B is finalized, committed, tagged, and pushed at:

```text
02b5bc72c5fa707bcbd4fc487ec3022e22bb2179
```

Security fix:

```text
FINAL_REAL_APPLY_REVIEWED_BASE_EXECUTION_GUARD
```

The durable baseline is:

- full suite: `3233/3233 passed, 0 failures, 0 errors, 9 warnings`;
- OpenAPI: `306 paths / 112 schemas`;
- `api_server`: `8 direct @app routes / 23 include_router / 0 direct /action/*`;
- Generic Act: `NOT_IMPLEMENTED / NOT_AUTHORIZED / NOT_GRANTED`.

The M107B guard consumes only the final approval/gate's exact
`dry_run_patch_apply_id`. It requires a linked completed dry-run record,
`dry_run is True`, exact `status == "dry_run"`, a canonical lowercase
64-character `original_hash_before`, normalized target equality, a safe current
target read, and equality under existing UTF-8 SHA-256 semantics. Any failure
is rejected before the shared real mutation primitive. Direct patch apply,
rollback, approval semantics, and the universal authority question remain
outside the guard.

## 3. M105B Closure Verification

M105B F03 remains truthfully closed. `patch_rollback.py` consumes the existing
successful apply record and its `original_hash_after` as expected post-write
state. It reads and hashes the current target before any pre-rollback backup or
restore write. A missing, invalid, or mismatched expected hash fails closed.

M105B did not add persistence or schema migration, approval redesign, rollback
single-use, universal rollback authority, or concurrency semantics. The focused
M105B tests and the full regression remain passing.

```text
F03: RESOLVED / CLOSED BY M105B
```

## 4. M107B Closure Verification

M107B remains truthfully bounded to the final-real-apply workflow:

- exact `dry_run_patch_apply_id` linkage is consumed;
- the linked record must exist and be a completed dry-run;
- `original_hash_before` is validated as canonical lowercase SHA-256;
- linked normalized target and approved final normalized target must match;
- the current final target is read through the existing safe reader;
- current content is hashed with existing UTF-8 SHA-256 semantics;
- mismatch or missing/malformed/unreadable evidence fails closed before mutation;
- exact/unique excerpt matching is not a final-workflow fallback;
- no new persistence, schema, approval artifact, or authority artifact exists;
- direct patch apply remains unchanged.

```text
F02_FINAL_WORKFLOW: ADDRESSED
F02_DIRECT_PATH: HIGH / UNRESOLVED
Universal F02: NOT RESOLVED
```

The direct path still has no truthful reviewed-base source. M107B does not
transfer final-workflow evidence to direct apply.

## 5. F01-F07 Residual Reconstruction

| Finding | Original severity | Current severity | Current status | Affected path / production consumer | Current mitigations | Changed by | Remaining risk | Build-ready | Policy/broad blocker |
|---|---|---|---|---|---|---|---|---|---|
| F01 direct authority divergence | HIGH | HIGH | UNRESOLVED | Direct patch route, tool executor, self-modification, final workflow, target and audit readers | Proposal/status checks, optional queue status, critical-path block, exact excerpt, backup, hashes, final gate for final callers | None; M107B is final-base only | Direct mutation can remain outside the stronger final workflow; legitimacy and trust relationship are not proven | NO | `BLOCKED_BY_CANONICAL_POLICY` |
| F02 final reviewed-base binding | HIGH | CLOSED for final workflow | `PARTIALLY_CLOSED` overall | Final executor and shared mutation primitive | Exact linked dry-run record and current hash comparison | M107B | Direct callers remain without reviewed-base evidence | NO universal Build | Direct path requires new state or policy |
| F02 direct-path reviewed-base binding | HIGH | HIGH | UNRESOLVED | Direct patch apply and direct mutation consumers | Current proposal, target, excerpt, approval/status, execution hashes, backup | None; final-only M107B explicitly excludes it | Changed surrounding content may still pass the direct exact excerpt check; no reviewed-base source exists | NO | `BLOCKED_BY_CANONICAL_POLICY` and likely new persistence |
| F03 rollback expected-state binding | HIGH | CLOSED | RESOLVED | Rollback target, backup, rollback record, verification readers | Current target must equal successful apply `original_hash_after` before restore | M105B | Rollback single-use/concurrency and broader transactionality remain out of scope | CLOSED | None for the closed finding |
| F04 mutation/write-record atomicity | HIGH | HIGH | UNRESOLVED | Target write, apply record, backup, audit, rollback eligibility | Pre-write backup, failed record attempt, post-write hashes on successful paths | None; M105B/M107B do not change write ordering | Interruption or persistence failure can leave changed content without complete durable evidence | NO | `TOO_BROAD_CURRENTLY` / recovery contract |
| F05 reusable direct approval | MEDIUM | MEDIUM | UNRESOLVED | Legacy queue item and direct apply callers | Proposal/status checks and current excerpt checks; retries remain possible | None | Status-read approval can be reused; changing this changes direct retry/approval semantics | NO | `BLOCKED_BY_CANONICAL_POLICY` |
| F06 final executor concurrency | MEDIUM | MEDIUM | UNRESOLVED | Final executor, target, apply records, executor records | Readiness refresh and gate-scoped prior-applied check | None; M107B is not a claim or lock | Concurrent calls can pass before either applied record is durable | NO | `TOO_BROAD_CURRENTLY` / overlaps F04 |
| F07 audit/verification split | MEDIUM | MEDIUM | UNRESOLVED | Apply/rollback records, Timeline, graph, mutation log, post-apply verifier | Primary records, warnings, backups, human verification gate | None | Auxiliary evidence or later verification may be incomplete without proving target mutation unsafe in every case | NO | `TOO_BROAD_CURRENTLY` / monitor |

### 5.1 F01 residual review

F01 remains an authority-model divergence, not a newly proven unauthorized
mutation. Direct patch mutation is a live production capability and the
repository does not establish that direct callers are illegitimate. The
repository also does not establish final-real-apply as universal or prove an
intentional layered dual-trust policy.

A local direct check cannot decide whether direct mutation remains legitimate,
whether final-real-apply becomes canonical, or whether separate trust models
are intentional. Any meaningful F01 fix therefore requires a canonical-policy
decision and potentially caller migration. Disposition:

```text
BLOCKED_BY_CANONICAL_POLICY
```

### 5.2 F02 direct-path residual review

Direct patch apply still has no dry-run ID, reviewed-base hash, proposal/review
content identity, or full reviewed content source. Existing direct proposal,
review, approval, target, excerpt, and execution hashes do not identify the
bytes reviewed before direct mutation. M107B's final gate record is not a
direct-path artifact.

Fixing direct F02 would require choosing a direct trust contract, adding or
binding reviewed state at proposal/review time, changing direct retry or
approval semantics, or containing direct callers. None is a no-persistence
local continuation of M107B. Disposition:

```text
BLOCKED_BY_CANONICAL_POLICY
```

### 5.3 F04 residual review

The current mutation sequence remains materially unchanged:

```text
backup
  -> target write
  -> apply-record persistence
  -> Timeline/graph/mutation-log attempts
  -> later verification eligibility
```

M105B adds rollback expected-state checking. M107B adds a final pre-dispatch
reviewed-base equality check. Neither changes target-write atomicity,
write-ahead state, durable recovery, fsync, record transactionality, or
post-write failure windows. F04 is therefore broad recovery/persistence
contract work, not a small next Build.

Disposition:

```text
TOO_BROAD_CURRENTLY
```

### 5.4 Medium residuals

- F05 remains a real direct-path replay concern, but its repair changes legacy
  approval consumption and retry semantics. Hash guards do not make approval
  single-use. Disposition: `BLOCKED_BY_CANONICAL_POLICY`.
- F06 remains a real final-path race. M107B is only a content equality guard;
  it adds no claim, reservation, lock, or single-use behavior. A safe F06
  repair overlaps mutation/record failure recovery. Disposition:
  `TOO_BROAD_CURRENTLY`.
- F07 remains an evidence completeness gap. Primary action records are durable
  and human verification is intentionally separate; no new incorrect mutation
  was proven. Disposition: `MONITOR` / `VALID_LATER_BUILD`, not a reason to
  delay broader architecture.

## 6. Authoritative Security Debt Table

| Finding | Scope | Severity | Status | Resolved by | Remaining risk | Production exposure | Build readiness | Blocker | Recommended disposition |
|---|---|---:|---|---|---|---|---|---|---|
| F01 | Direct versus final authority | HIGH | UNRESOLVED | None | Authority divergence and possible bypass of stronger workflow | Strong live consumers | No | Canonical policy | `BLOCKED_BY_CANONICAL_POLICY` |
| F02_FINAL_WORKFLOW | Final reviewed-base equality | HIGH | ADDRESSED | M107B | Current-state equality only; no historical change detection | Final executor | Yes, implemented | None within final scope | `PARTIALLY_CLOSED` |
| F02_DIRECT_PATH | Direct reviewed-base equality | HIGH | UNRESOLVED | None | Stale surrounding content can survive excerpt-only check | Direct mutation | No | Direct trust and persistence policy | `BLOCKED_BY_CANONICAL_POLICY` |
| F03 | Rollback expected state | HIGH | CLOSED | M105B | No rollback single-use/concurrency claim | Rollback route | Closed | None for F03 | `CLOSED` |
| F04 | Mutation and durable record boundary | HIGH | UNRESOLVED | None | Partial/unrecorded mutation and recovery ambiguity | All mutation callers | No | Broad recovery/persistence contract | `TOO_BROAD_CURRENTLY` |
| F05 | Direct approval replay | MEDIUM | UNRESOLVED | None | Reusable legacy approval and changed retry semantics | Direct route | No | Approval/trust policy | `BLOCKED_BY_CANONICAL_POLICY` |
| F06 | Final concurrency | MEDIUM | UNRESOLVED | None | Non-atomic readiness and applied-state claim | Final executor | No | F04 overlap | `TOO_BROAD_CURRENTLY` |
| F07 | Audit/verification split | MEDIUM | UNRESOLVED | None | Incomplete auxiliary evidence or later verification | Action evidence readers | No | Broad lifecycle scope | `MONITOR` |

## 7. Patch-Security Stopping Rule

The M108A stopping rule is satisfied:

| Requirement | Result | Evidence |
|---|---|---|
| Immediate independently-fixable HIGH risk addressed | YES | M105B closed F03; M107B addressed final-workflow F02 |
| Remaining HIGH risks require policy or broad architecture | YES | F01/F02 direct require trust/persistence policy; F04 requires recovery contract |
| MEDIUM risks do not justify delaying broader Aether work | YES | F05 changes approval semantics; F06 overlaps F04; F07 is evidence completeness |
| CRITICAL patch findings remain | NO | M103A/M107B state has zero CRITICAL findings |
| Current patch paths remain regression-clean | YES | M107B full suite `3233/3233`, focused locks passing |
| Safety fixes are Git-durable and fail closed | YES | M105B and M107B are committed/tagged/pushed; stale evidence rejects before mutation |

```text
Patch-security stopping point reached: YES
Highest remaining patch risk: F02_DIRECT_PATH, co-equal HIGH policy residuals F01/F04
Next patch-security Build: NOT JUSTIFIED
```

This is a stopping point for the next milestone direction, not a claim that all
patch findings are resolved.

## 8. Non-Patch Architecture Frontier Inventory

M108A does not treat dormant foundations or architectural desire as current
consumer proof. Three non-patch frontiers remain candidates for later proof:

| Frontier | Current durable state | Last milestone | Real producer proof | Real consumer proof | Authority risk | Runtime gap | Build-ready | Core-loop value |
|---|---|---|---|---|---|---|---|---|
| `GOAL_TO_PLAN_RUNTIME_CONSUMER_PROOF` | Goal/Task/TaskContext/Plan/PlanStep/Governance exist process-locally; `/chat` and `core/loop.py` remain legacy text/policy paths | M98A | Process-local producers YES; external runtime producer/consumer NO | External canonical consumer ABSENT | High if `/chat` or legacy loop is made a competing authority | Think -> Plan outside Core Coordination is not wired | NO | Directly concerns `Receive Goal -> Think -> Plan` without fabricating a consumer |
| `THINKINGPROPOSAL_PRODUCTION_PRODUCER_PROOF` | `ThinkingProposal` contract and process-local consumer exist; current production producer remains absent | M99A | Current production producer NO | External consumer needing proposal NO | High if legacy policy fields are mapped into canonical criteria | No truthful producer identity, criteria, provenance, or selected-context handoff | NO | Protects truthful transition from legacy thinking to canonical planning |
| `ACTION_AUTHORITY_CONSOLIDATION_NON_PATCH_BOUNDARY` | M101B bound `file.restricted_read`; M102A found no truthful second capability binding; unlike direct/tool/action contracts remain | M100A/M101B/M102A | Multiple live action producers YES | Live restricted-read consumer YES; no common cross-capability consumer contract | High; generic or canonical authority could broaden scope | Equivalent capabilities use different trust contracts | NO | Concerns safe `Act -> Observe -> Verify` authority, but remains adjacent to patch policy |

The first two frontiers are not Build-ready because their missing producer or
consumer proof is explicit. The third has real action consumers, but M102A
already found no truthful second capability binding and the remaining
cross-capability relationship includes unresolved patch policy. None supports a
runtime Build under M108A.

## 9. Patch Versus Core-Architecture Priority

| Dimension | Continue patch security | Return to broader architecture |
|---|---|---|
| Security urgency | HIGH residuals remain, but F01/F02 direct are policy-blocked and F04 is broad | No new CRITICAL patch risk is waiting; core loop proof is a separate leverage question |
| User/runtime value | Protects direct/failure/concurrency edges | Can establish truthful Goal -> Think -> Plan -> Act -> Observe -> Verify progression |
| Architectural leverage | Local unless canonical authority is selected | High if a real owner and consumer are proven; low if speculative |
| Dependency unblock value | Requires direct trust, approval, or recovery decisions | Consumer proof can prevent unsafe `/chat` or producer invention |
| Scope certainty | Remaining fixes are not small/bounded under current policy | A read-only consumer-proof milestone is bounded; Build is not yet justified |
| Consumer proof | Strong for patch paths, but residual contracts disagree | No external canonical Goal-to-Plan consumer currently proven |
| Authority risk | High; local fixes may silently choose authority | High if legacy loop is made canonical without contract; manageable in discovery |
| Implementation readiness | No next patch Build satisfies independence gate | Discovery/consumer proof is the correct next type, not implementation |
| Local-optimization risk | High; may deepen patch-specific architecture before core direction | Lower if proof-only and no runtime wiring |
| Architectural-drift risk | Patch work can postpone core-loop decisions | Core work can drift if it fabricates producer/consumer semantics; proof gate prevents that |

The comparison supports pausing patch-security implementation while returning to
core architecture through a read-only consumer-proof milestone.

## 10. Direction-Model Comparison

| Model | Evidence assessment | Result |
|---|---|---|
| `MODEL_A_CONTINUE_PATCH_SECURITY` | No remaining patch HIGH is both independently bounded and policy-free. F02 direct lacks a source; F01 needs authority policy; F04 is broad. | REJECTED |
| `MODEL_B_PATCH_SECURITY_PAUSE_RETURN_TO_CORE_ARCHITECTURE` | M105B/M107B address the immediate independently bounded safety gaps; remaining patch debt is policy/broad; a core consumer-proof frontier can be examined without implementation. | **SELECTED** |
| `MODEL_C_ONE_MORE_PATCH_PROOF_THEN_PAUSE` | No single final patch proof is decision-critical enough to precede the already justified stopping point. M107B supplied the final-workflow proof and direct residual is policy-bound. | REJECTED |
| `MODEL_D_ARCHITECTURE_STATE_INSUFFICIENT_FOR_DIRECTION` | Evidence is sufficient to establish patch stopping and identify the Goal-to-Plan consumer-proof frontier, even though no Build is ready. | REJECTED |

## 11. Selected Direction and Principal Decision

```text
Selected direction model:
MODEL_B_PATCH_SECURITY_PAUSE_RETURN_TO_CORE_ARCHITECTURE

Principal decision:
B_PATCH_SECURITY_STABLE_ENOUGH_RETURN_TO_CORE

Selected next frontier:
GOAL_TO_PLAN_RUNTIME_CONSUMER_PROOF

Next milestone type:
CONSUMER_PROOF

Next Build:
NOT JUSTIFIED
```

The next proof milestone should determine whether one real production runtime
component currently needs and can truthfully consume the existing process-local
Goal -> Task -> selected TaskContext -> ThinkingProposal -> Plan -> PlanStep ->
Governance seam. It must inventory producer, caller, identity, ownership,
criteria, lifecycle, privacy, persistence, restart, and failure semantics. It
must not wire `/chat`, map legacy policy fields, create a ThinkingProposal
producer, activate Plan execution, or introduce Generic Act without a separate
decision.

Reason patch work should pause:

1. F03 is closed and final-workflow F02 is addressed with durable fail-closed
   guards.
2. The remaining HIGH patch risks are not independently Build-ready: F01 and
   direct F02 require authority/persistence policy, while F04 requires broad
   recovery and transaction design.
3. Medium risks do not currently justify delaying a core architecture proof.
4. The selected core frontier is directly tied to Aether's stated loop but is
   still only a consumer-proof question, avoiding speculative runtime wiring.

## 12. Explicit Non-Goals

M108A does not:

- implement F01, F02 direct path, F04, F05, F06, or F07;
- reopen or modify M105B F03 rollback behavior;
- modify patch apply, patch rollback, final-real-apply, direct routes, or
  approval semantics;
- add persistence, schema, migration, transaction, reservation, or concurrency
  behavior;
- choose canonical patch mutation authority;
- wire `/chat` to Goal-to-Plan;
- create a ThinkingProposal producer or adapter;
- activate Plan execution, Observation Intake, Verification Aggregation,
  Critic, Repair, Learning, retry, background execution, or scheduler runtime;
- implement Generic Act or any generic authority registry;
- update `PROGRESS.md`, README, Constitution, Architecture, production code,
  existing tests, dependencies, or runtime/private data;
- commit, tag, push, begin M108B, or begin M109.

## 13. Generic Act Status

```text
Generic Act: NOT_IMPLEMENTED
Generic Act integration: NOT_AUTHORIZED
Generic Act authority: NOT_GRANTED
```

## 14. M108A Next-Step Gate

```text
M108A review: COMPLETE LOCALLY
Patch-security stopping point: YES
Selected direction model: MODEL_B_PATCH_SECURITY_PAUSE_RETURN_TO_CORE_ARCHITECTURE
Principal decision: B_PATCH_SECURITY_STABLE_ENOUGH_RETURN_TO_CORE
Selected next frontier: GOAL_TO_PLAN_RUNTIME_CONSUMER_PROOF
Next milestone type: CONSUMER_PROOF
Next Build: NOT JUSTIFIED
Canonical patch authority: NOT PROVEN
Generic Act: NOT_IMPLEMENTED / NOT_AUTHORIZED / NOT_GRANTED
```

Next authorized action: HUMAN/PROJECT-MANAGER M108A NEXT-DIRECTION REVIEW.
M108A itself authorizes no implementation and returns control to the
human/project-manager.
