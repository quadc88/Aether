# Milestone 105A Patch Mutation Independent Security Fix Selection Boundary

Classification: STRICT READ-ONLY SECURITY / BUILD-PRIORITY / BOUNDARY-SELECTION

Status: SELECTION COMPLETE LOCALLY / ONE INDEPENDENT FIX JUSTIFIED FOR PM REVIEW

This record selects at most one future patch security fix without choosing a
canonical direct or final-real-apply route. It does not modify patch apply,
patch rollback, final-real-apply, approval semantics, routes, persistence, or
runtime data. It does not implement Generic Act.

## 1. Current Git State

Audit-start state:

- Branch: `main`.
- HEAD: `a705c4a96cb482e74f157f72e8a10c592a8d5466`.
- Local `main`, `origin/main`, and remote `main` matched.
- Tracked worktree: clean.
- M104A: FINALIZED / COMMITTED / TAGGED / PUSHED / PM-ACCEPTED baseline.
- M104A canonical mutation authority: `NOT PROVEN`.
- M104A selected model: `MODEL_F_NO_CANONICAL_AUTHORITY_DECISION_YET`.
- M104A build-readiness: `D_NO_CANONICAL_MODEL_PROVEN`.
- M103A findings resolved: NONE.
- Full-suite baseline: `3182/3182 passed, 0 failures, 0 errors, 9 warnings`.
- OpenAPI baseline: `306 paths / 112 schemas`.
- `api_server` baseline: `8 direct @app routes / 23 include_router / 0 direct
  /action/*`.
- M105A creates only this design candidate, its static/document lock, and the
  external PM evidence summary.
- No production edit, existing-test edit, `PROGRESS.md` edit, dependency edit,
  runtime/private-data edit, commit, tag, or push is authorized by M105A.

Git verification at audit start:

```text
git status: clean
branch: main
HEAD: a705c4a96cb482e74f157f72e8a10c592a8d5466
main: a705c4a96cb482e74f157f72e8a10c592a8d5466
origin/main: a705c4a96cb482e74f157f72e8a10c592a8d5466
remote main: a705c4a96cb482e74f157f72e8a10c592a8d5466
git diff --check: CLEAN
```

## 2. M104A Durable Baseline

M104A proved that direct patch mutation is a live production capability, that
final-real-apply is a real stronger human-reviewed workflow, and that neither
route is proven to be the universal canonical authority. M104A intentionally
selected no canonical route and no Build.

M103A recorded seven findings:

- F01 HIGH: direct authority divergence and missing direct attempt/session/
  identity/freshness/single-use boundary;
- F02 HIGH: reviewed-base and dry-run-to-final hash equality absent;
- F03 HIGH: rollback stale/replay risk because expected post-apply state is not
  checked and rollback has no single-use/concurrency claim;
- F04 HIGH: write and durable apply-record boundary is non-atomic;
- F05 MEDIUM: direct approval is status-read and reusable;
- F06 MEDIUM: final executor prior-applied check is not atomic against
  concurrency;
- F07 MEDIUM: audit and verification are separate non-transactional evidence
  stages.

M105A must not resolve these by selecting a canonical route. It asks whether one
local security boundary can be fixed independently of that unresolved policy.

## 3. Exact Objective

Answer:

```text
Is there ONE high-value patch mutation security fix that can be implemented
safely without first deciding whether direct patch apply or final-real-apply
is the canonical mutation authority?
```

An independent candidate must have a real production consumer, reduce a proven
gap, preserve both current trust models, fail closed, remain bounded, and have a
clear removal path. A desirable architectural improvement is not enough.

## 4. F01-F07 Reconstruction

| Finding | Severity | Affected path | Current behavior | Risk | Existing mitigations | Production consumer | Canonical-route dependent? | Local fix possible? | Behavior change? | Stored data change? | API/route change? |
|---|---|---|---|---|---|---|---|---|---|---|---|
| F01 | HIGH | Direct apply and final comparison | Direct route can call `apply_patch_proposal(..., dry_run=False)` without final gate, canonical attempt, session/identity, freshness, or direct single-use | Old/cross-context authority may reach mutation | Approved proposal status, optional queue status, critical-path block, excerpt check, backup, hashes | Target file, apply record, audit readers | YES for any decision to make final gate universal; NO for a local direct check, but trust policy remains unresolved | Partially | YES if direct semantics become stricter | Maybe | NO for local checks |
| F02 | HIGH | Proposal/review/dry-run/final apply | Current content is re-read and excerpt must occur once; reviewed full base is not retained or compared | Stale target or target drift can receive an approved patch | Current read, exact excerpt count, execution before/after hashes | Target file and apply records | NO in principle, but exact integration differs by caller | Possible with new persistence/binding | YES for stale proposals | YES if base evidence is stored | NO necessarily |
| F03 | HIGH | Rollback | Rollback checks successful apply, backup path, current read, and backup/result hashes but not current hash equal to apply post-write hash; no rollback claim | Stale or replayed rollback can overwrite intervening legitimate content | Apply ID, backup root/path/size, current/backup/result hashes, pre-rollback backup, critical-path block | Restored target, rollback record, post-apply verification | NO; rollback can bind to an existing apply record under either direct or final workflow | YES with existing apply-record field | YES only when current state no longer matches expected apply state | NO | NO |
| F04 | HIGH | Apply write and records | Target write occurs before apply-record save; `write_text` is not atomic; auxiliary evidence is separate | Partial/unrecorded mutation or incomplete audit | Pre-write backup, failed record attempt, post-write hash on success | Target, apply record, rollback eligibility, audit readers | NO, but a complete transaction may affect all callers | Broad and unclear | YES | Likely | NO route change but persistence/recovery scope is broad |
| F05 | MEDIUM | Direct approval and apply | Legacy queue approval is read by status and not consumed once | Same approval can replay while excerpt remains applicable | Proposal status, current content/excerpt check | Repeated direct apply callers | Potentially; direct trust policy unresolved | Possible but changes approval semantics, explicitly out of scope | YES | Maybe | NO |
| F06 | MEDIUM | Final executor | `_has_applied_record` checks prior applied records before lower-level apply but check and write are not atomic | Concurrent final calls may both pass | Readiness refresh, gate ID, prior-record check, excerpt check | Target and executor records | NO for a final-local lock, though final workflow role remains separate | Possible with executor-local coordination | YES for concurrency behavior | Maybe | NO |
| F07 | MEDIUM | Apply/rollback/audit/verification | Apply records and auxiliary Timeline/graph/mutation/verification stages are separate | Mutation can lack complete auxiliary audit or verification | Primary records, warnings, backups, human verification gate | Audit readers, verifier, workflow reports | NO technically; broad lifecycle semantics affect both | Possible but broad | YES for failure/recovery behavior | Likely | NO route change |

F03 is the only HIGH finding with a small existing authoritative value that can
be checked locally without deciding which mutation route is canonical:
`patch_apply.original_hash_after` is recomputed from the target after a
successful real write, and `patch_rollback` already computes the current target
hash before restoring the backup.

## 5. Candidate Inventory

| Candidate | Boundary |
|---|---|
| `CAND_A_APPROVAL_TO_EXACT_PATCH_BINDING` | Bind approval to proposal, target, body, and exact reviewed facts |
| `CAND_B_REVIEWED_BASE_HASH_BINDING` | Persist and compare the exact base reviewed or dry-run |
| `CAND_C_DIRECT_APPROVAL_SINGLE_USE` | Add a direct-path approval claim/replay boundary |
| `CAND_D_FINAL_EXECUTOR_ATOMIC_SINGLE_USE` | Make final prior-use check atomic against concurrent execution |
| `CAND_E_ROLLBACK_STALE_REPLAY_PROTECTION` | Require current target hash to equal successful apply post-write hash before restore |
| `CAND_F_MUTATION_RECORD_ATOMICITY` | Add a write/backup/apply-record recovery or transactional seam |

No restricted-read binding, scope, fingerprint, or Generic Act model is a
candidate. Patch semantics must remain patch-specific.

## 6. Approval-to-Patch Binding Review

The legacy approval queue item stores request text, proposed action,
verification plan, risk, metadata, status, and decision time. The patch proposal
stores an optional `approval_id`. Direct apply reads the queue item's current
status only when `requires_user_approval` is true. It does not compare queue
content to the proposal.

Current approval binding is therefore:

- proposal ID: indirect through the proposal's stored approval ID;
- proposal revision: ABSENT;
- target path: ABSENT from approval content validation;
- normalized target: ABSENT;
- original excerpt: ABSENT;
- proposed excerpt: ABSENT;
- patch body/hash: ABSENT;
- base content/hash: ABSENT;
- session: ABSENT;
- actor: ABSENT;
- timestamp/freshness: decision time is recorded but not enforced as a TTL.

An exact approval fingerprint cannot be truthfully derived for all current patch
callers without choosing which proposal fields are authoritative, changing the
legacy approval contract, and deciding how revisions are represented. CAND_A is
therefore not independent enough for a first Build.

## 7. Reviewed-Base Binding Review

Proposal creation reads current target content and stores only an excerpt. Patch
review checks diff presence and proposal/queue state. Dry-run apply reads the
current target at dry-run execution and stores an execution-time
`original_hash_before`. Final execution re-reads current target and checks the
excerpt again, but does not compare its base to the dry-run hash.

The current evidence can distinguish:

- missing original excerpt: blocked;
- duplicate original excerpt: blocked;
- same excerpt on changed surrounding content: accepted;
- same target after another mutation that preserves one excerpt: accepted;
- stale proposal with absent/ambiguous excerpt: blocked.

The reviewed full base hash is absent from proposal and review records. The
dry-run hash is available in a dry-run apply record but is not a universal
reviewed-base authority and is not connected to direct apply. CAND_B requires
new persistence or a new record contract and affects both direct and final
workflows; it is a valid later Build, not the smallest independent first fix.

## 8. Single-Use and Replay Review

| Authority | Current claim/check | Atomicity | Owner | Retry behavior | M105A disposition |
|---|---|---|---|---|---|
| Direct mutation approval | Legacy queue status read; no claim | No claim | Patch service plus legacy queue | Failed or blocked direct attempts remain retryable | Do not change; canonical policy unresolved |
| Final-real-apply | Prior applied executor record per gate | Check is not atomic with apply | Final executor | Failed attempts can be retried after readiness | CAND_D is local but lower value than F03 |
| Rollback | No prior rollback claim; backup path remains eligible | No claim or lock | Patch rollback service | Repeated rollback can run if eligibility remains | CAND_E adds expected-state fail-closed check, not a universal claim |

CAND_C changes direct approval semantics and is explicitly not selected. CAND_D
could be independent of route selection but addresses MEDIUM F06 and needs a
concurrency coordination design around the mutation call. CAND_E does not mint a
single-use token: after a successful rollback, the target no longer equals the
apply post-write hash, so an immediate replay fails closed naturally. It still
does not claim to solve concurrent rollback races where two calls read the
expected state before either writes.

## 9. Mutation and Record Atomicity Review

The current real apply sequence is:

```text
read target -> compute replacement -> create backup -> write target
  -> compute post-write hash -> save apply record
  -> Timeline / graph / mutation log attempts -> later verification
```

The current rollback sequence is:

```text
read target and backup -> compute hashes -> create pre-rollback backup
  -> write backup content -> compute resulting hash -> save rollback record
  -> Timeline / graph / mutation log attempts -> later verification
```

Failures between backup, write, record, audit, and verification can leave
partial or incomplete evidence. A complete fix could require temporary files,
atomic replace, write-ahead records, recovery states, fsync policy, backup
reservation, schema changes, and recovery tests. That is broader than one
independent authority fix and is not a first Build.

Authority can be selected without atomicity work, and atomicity can be improved
without selecting a canonical route. CAND_F is therefore `TOO_BROAD_FOR_FIRST_BUILD`.

## 10. Rollback Security Review

Existing successful real apply records contain:

- `apply_id`;
- proposal ID;
- target and normalized path;
- `original_hash_after`, recomputed from the written file;
- backup path;
- success/applied state.

Existing rollback already computes:

- current target hash before restore;
- backup hash;
- result hash after restore;
- pre-rollback backup.

The smallest truthful independent boundary is to require, before creating the
pre-rollback backup or writing the backup content:

```text
current_hash_before == apply_record.original_hash_after
```

If the apply post-write hash is missing or the current target differs, rollback
must fail closed and must not write. This is expected-state binding, not a
canonical mutation authority and not a new approval semantic.

The check preserves legitimate retry behavior when the target is still exactly
the state produced by the apply. It intentionally rejects rollback after an
intervening mutation, because restoring the old backup would otherwise
overwrite unknown current work. It does not require a new persistence field,
API field, route, approval, session, or actor identity.

## 11. Candidate Score Table

| Candidate | Finding(s) addressed | Consumer strength | Security value | Canonical independence | Behavior risk | Compatibility risk | Persistence | API | Routes | Size | Failure-closed | Removal | Testability | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CAND_A_APPROVAL_TO_EXACT_PATCH_BINDING | F01, F05 and parts of F02 | STRONG | HIGH | PARTIAL; approval policy/revision unresolved | HIGH | HIGH | Likely new fields/compatibility | NONE expected | NONE expected | MEDIUM/LARGE | Possible | Medium | Medium | NEEDS_MORE_REVIEW |
| CAND_B_REVIEWED_BASE_HASH_BINDING | F02 | STRONG | HIGH | PARTIAL; direct and final evidence differ | MEDIUM/HIGH | MEDIUM | New proposal/review/base evidence likely | NONE | NONE | MEDIUM | Strong if present | Medium | Strong | VALID_LATER_BUILD |
| CAND_C_DIRECT_APPROVAL_SINGLE_USE | F01, F05 | STRONG | MEDIUM/HIGH | NO; direct legitimacy/retry policy unresolved | HIGH | HIGH | Claim state required | NONE | NONE | MEDIUM | Strong but changes retries | Medium | Strong | BLOCKED_BY_CANONICAL_DECISION |
| CAND_D_FINAL_EXECUTOR_ATOMIC_SINGLE_USE | F06 | STRONG | MEDIUM | YES for final-local workflow | MEDIUM | LOW/MEDIUM | Existing executor state, lock/recovery choice | NONE | NONE | MEDIUM | Strong if lock scope is right | Good | Medium | VALID_LATER_BUILD |
| CAND_E_ROLLBACK_STALE_REPLAY_PROTECTION | F03 | STRONG: rollback route, self-modification, verifier | HIGH | YES; reads existing apply expected state under either authority | LOW/MEDIUM | LOW/MEDIUM for stale rollback records | NONE; existing `original_hash_after` | NONE | NONE | SMALL | Strong; mismatch blocks before write | Simple code/test removal | Strong | STRONG_FIRST_BUILD_CANDIDATE |
| CAND_F_MUTATION_RECORD_ATOMICITY | F04, F07 | STRONG | HIGH | YES in principle | HIGH | HIGH | Recovery schema/transaction state likely | NONE | NONE | LARGE | Requires recovery design | Complex | Complex | TOO_BROAD_FOR_FIRST_BUILD |

## 12. Selected Candidate

Selected candidate:

```text
CAND_E_ROLLBACK_STALE_REPLAY_PROTECTION
```

Selected model:

```text
MODEL_E_ROLLBACK_EXPECTED_STATE_BINDING
```

Principal decision:

```text
A_INDEPENDENT_PATCH_SECURITY_BUILD_JUSTIFIED
```

Future Build:

```text
JUSTIFIED FOR PM REVIEW
```

This is a selection for a future PM-authorized Build, not implementation
authority. It is independent because it consumes an existing successful apply
record field and an existing current-target hash in the rollback owner. It does
not decide whether the apply came through the direct route or final executor.

It reduces HIGH F03 only. It does not claim to resolve F01, F02, F04, F05, F06,
or F07.

## 13. Independence Gate

| Requirement | CAND_E result |
|---|---|
| Proven current security/correctness gap | YES: stale sequential rollback can overwrite intervening content |
| Real production consumer | YES: rollback route, self-modification rollback, post-apply verification |
| Does not require canonical-route selection | YES |
| Does not invalidate a legitimate trust model | YES; direct and final apply remain unchanged |
| Does not require Generic Act | YES |
| Does not require broad approval redesign | YES |
| Bounded file/test scope | YES: rollback service plus focused tests |
| Failure-closed | YES: missing/mismatched expected state blocks before restore |
| Clear removal path | YES: remove comparison and focused tests; no data migration |

The expected-state check is narrower than a rollback redesign. It does not
introduce a rollback approval, universal single-use claim, session identity, or
new authority source.

## 14. Exact First Build Boundary If Later Authorized

The future Build, if separately authorized, must contain only:

1. Read the successful apply record's existing `original_hash_after`.
2. Compute the current target hash using the existing current-target read.
3. Fail closed before pre-rollback backup or write when the expected hash is
   absent or does not equal the current hash.
4. Preserve existing backup-root, critical-path, backup hash, result hash,
   pre-rollback backup, record, Timeline, graph, mutation log, and verification
   semantics.
5. Preserve retries after failed/ineligible attempts when the target still
   matches the successful apply's expected post-write state.
6. Add focused tests for matching state, stale state, missing expected hash,
   repeated successful rollback state, dry-run, and failure-closed no-write
   behavior.

This Build must not add an explicit rollback approval, modify direct apply,
modify final-real-apply, alter apply records, add a new persisted field, or
decide a canonical mutation route.

### Expected Build files

- `aether/action/patch_rollback.py` — one local expected-state guard only.
- `tests/test_patch_rollback_expected_state_binding.py` — new focused tests.

No existing API model, router, approval store, or other production file is in
the selected boundary.

### Files explicitly forbidden for the first Build

- `aether/action/patch_apply.py`;
- `aether/action/final_real_apply_executor.py`;
- `aether/action/real_apply_approval_gate.py`;
- `aether/action/approval_queue.py`;
- `aether/action/patch_proposal.py`;
- `aether/action/patch_review.py`;
- direct patch routes and self-modification routes;
- restricted-read authority files and `RestrictedReadAuthorityBinding`;
- Generic Act or shared mutation authority;
- `PROGRESS.md`, README, Constitution, Architecture, dependencies, and runtime
  or private data;
- transactional mutation/record logic and rollback schema migration.

## 15. Build Impact

- Behavior change: rollback becomes stricter only when current state no longer
  equals the successful apply's recorded post-write state.
- Legitimate retry behavior: preserved when the expected state still matches.
- Compatibility: old successful apply records without `original_hash_after`
  become ineligible rather than risking stale restore; no migration is selected.
- Persistence impact: NONE; use existing apply record field and rollback record.
- API impact: NONE.
- Route impact: NONE.
- Approval impact: NONE.
- Canonical-route impact: NONE.
- Rollback/removal path: remove the local guard and focused tests; no data
  conversion or route rollback is required.

## 16. Failure-Closed Rules

The future selected Build must block before restore when:

- apply record is absent, unsuccessful, unapplied, or has no backup;
- expected post-apply hash is absent or malformed;
- target read fails;
- current hash cannot be computed;
- current hash differs from the apply record's post-write hash;
- target is critical;
- backup path is outside the configured backup root, absent, or oversized;
- backup read or backup hash fails;
- dry-run is requested for a real mutation path incorrectly;
- any existing rollback eligibility check fails.

No backup restore, pre-rollback write, or target mutation occurs on expected
state mismatch. The existing successful result-hash check remains in force.

## 17. Authority Ownership

- Execution authorization: unchanged; direct patch service checks remain direct,
  final gate/executor checks remain final.
- Approval consumption: unchanged; no approval is read or claimed by the
  selected rollback guard.
- Mutation dispatch: unchanged; `patch_rollback.rollback_patch_apply` remains
  the rollback dispatcher.
- Mutation primitive: unchanged; `aether.action.patch_apply.apply_patch_proposal`.
- Backup creation: unchanged; existing patch and pre-rollback backup owners.
- Rollback authorization: remains action-specific and separate.
- Apply record authority: existing successful `original_hash_after` is the
  expected-state source for rollback.
- Verification: unchanged; post-apply verification remains evidence-only.

The guard validates an existing fact. It does not mint authority, decide policy,
consume approval, or choose which apply route was canonical.

## 18. Explicit Non-Goals

M105A does not:

- modify patch runtime code;
- implement the selected rollback fix;
- modify direct patch apply or final-real-apply;
- choose a canonical patch mutation route;
- disable or quarantine direct patch apply;
- change approval semantics or approval consumption;
- add reviewed-base binding or direct single-use semantics;
- add transactional mutation logic;
- redesign rollback;
- reuse `RestrictedReadAuthorityBinding`, `RestrictedReadScope`, or restricted
  read approval semantics;
- implement Generic Act, generic mutation authority, or a capability registry;
- modify `PROGRESS.md`, README, Constitution, Architecture, production code,
  existing tests, dependencies, or runtime/private data;
- commit, tag, push, or begin M105B or M106.

## 19. Build Authorization Gate

```text
M105A selection: COMPLETE LOCALLY
Principal decision: A_INDEPENDENT_PATCH_SECURITY_BUILD_JUSTIFIED
Selected candidate: CAND_E_ROLLBACK_STALE_REPLAY_PROTECTION
Selected model: MODEL_E_ROLLBACK_EXPECTED_STATE_BINDING
Canonical-route decision required: NO
Future Build: JUSTIFIED FOR PM REVIEW
Implementation authorization: NOT GRANTED
Generic Act: NOT_IMPLEMENTED / NOT_AUTHORIZED / NOT_GRANTED
```

## 20. Next-Step Gate

```text
Next authorized action: HUMAN/PROJECT-MANAGER M105A SECURITY FIX SELECTION REVIEW
No implementation is authorized by M105A.
No patch runtime change is authorized.
No approval change is authorized.
No canonical route is selected.
No M105B or M106 is authorized.
```

Control returns to the human/project-manager.
