# Milestone 106A Remaining Patch High-Risk Fix Priority Boundary

Classification: STRICT READ-ONLY SECURITY / PRIORITY / CONSUMER-PROOF REVIEW

Status: REVIEW COMPLETE LOCALLY / NO NEXT INDEPENDENT HIGH FIX PROVEN

This record reviews the remaining M103A patch findings after M105B. It does not
implement a security fix, modify patch runtime, choose a canonical patch route,
change approval semantics, add transactional mutation behavior, or implement
Generic Act.

## 1. Current Git State

Git is authoritative. The required audit-start verification was:

```text
git status --short: (empty)

The only repository changes authorized by M106A are these two new local
untracked candidates:

- `docs/architecture/MILESTONE_106A_REMAINING_PATCH_HIGH_RISK_FIX_PRIORITY_BOUNDARY.md`
- `tests/test_milestone_106a_remaining_patch_high_risk_fix_priority_boundary.py`

No tracked file, production file, existing test, dependency, or runtime/private
data file is part of this milestone.

## 2. M105B Durable Baseline

M105B is finalized, committed, tagged, pushed, and PM-accepted at durable HEAD
`e373e60b3cba4bf0a144c2fa6ba1acd12e093753`.

M105B closed M103A F03 HIGH with rollback expected-state binding:

- a successful apply record's existing `original_hash_after` is the expected
  post-write state;
- rollback computes the current target hash before any pre-rollback backup or
  restore write;
- a missing, malformed, or mismatched expected hash fails closed;
- matching state remains eligible, including legitimate retry before state
  changes;
- persistence impact is NONE and schema migration is NONE;
- approval, direct apply, final-real-apply, canonical-route, API, and route
  semantics are unchanged.

F03 is CLOSED. M106A does not reopen rollback expected-state binding, rollback
single-use, rollback approval, or rollback concurrency.

The durable baseline remains:

- Full suite: `3201/3201 passed, 0 failures, 0 errors, 9 warnings`.
- OpenAPI: `306 paths / 112 schemas`.
- `api_server`: `8 direct @app routes / 23 include_router / 0 direct /action/*`.
- Canonical patch mutation authority: NOT PROVEN.
- Generic Act: NOT_IMPLEMENTED / NOT_AUTHORIZED / NOT_GRANTED.

## 3. Exact Objective

M106A answers:

```text
After F03 is removed, is there ONE remaining HIGH patch-security finding that
has a bounded, independent, production-justified next Build?
```

The ranking uses real production consumers, concrete security value,
independence from canonical-route selection, bounded implementation,
failure-closed behavior, compatibility, testability, and authority-broadening
risk. It does not rank by architecture elegance or by the number of checks in
the final-real-apply workflow.

## 4. Remaining Finding Reconstruction

M103A recorded F01, F02, and F04 as HIGH, and F05, F06, and F07 as MEDIUM.
M105B changed F03 only. It did not change the practical exploitability or
authority model of the other findings.

| Finding | Current severity | Affected path | Production consumer | Exact risk | Current mitigations | M105B practical effect | Canonical decision required for a fix? | Independent fix possible? | Behavior change required? | Data/schema migration? |
|---|---|---|---|---|---|---|---|---|---|---|
| F01 | HIGH | Direct real patch apply versus final-real-apply | Direct patch route, tool executor, self-modification, target and audit readers | A direct proposal/status/legacy-approval path can mutate without the stronger final workflow's attempt, session, freshness, or single-use boundary | Approved proposal status, conditional legacy queue status, critical-path block, exact-one excerpt, backup, hashes, records | NONE; F03 closure does not constrain apply authority | YES for route containment, final canonicality, or dual-trust policy; local checks alone do not settle legitimacy | Partial only; a truthful boundary is not selected | Yes for stricter direct callers | Local checks no; authority binding likely yes |
| F02 | HIGH | Proposal/review, dry-run, direct apply, final apply | Target file, direct apply result, dry-run/final workflow, verification and audit readers | Approved work can execute on changed surrounding content when the stored excerpt remains unique; final apply does not prove dry-run base equality | Current read, exact-one excerpt, execution-time before/after hashes, dry-run record linkage in final gate | NONE; F02 remains HIGH | NO for a final-only guard; YES or unresolved for a truthful universal direct-plus-final contract | Final-only partial fix is possible; cross-path fix is not proven bounded | Yes where stale state is rejected | Final-only no; universal reviewed-base binding likely yes |
| F04 | HIGH | Target write and apply-record persistence | Target file, apply record, rollback eligibility, audit readers | Partial or unrecorded mutation can survive a write, interruption, or persistence failure without normal durable recovery evidence | Pre-write backup, failed record attempt, post-write hash on successful path | NONE | NO in principle, but a complete fix is broad and affects all mutation callers | Not bounded for the next Build | Yes, especially failure/recovery behavior | Likely new recovery state/contracts |
| F05 | MEDIUM | Direct approval reuse | Direct apply callers and legacy approval consumers | Approved legacy queue status can be reused; approval does not bind exact patch facts or an execution claim | Proposal ID linkage, proposal status, current target/excerpt checks, retry of failed attempts | NONE | YES if single-use or direct legitimacy is policy; local claim changes direct approval semantics | Technically possible, policy-independent no | Yes; legitimate retries may change | Claim state or legacy contract impact likely |
| F06 | MEDIUM | Final executor readiness and shared apply call | Final executor, target, apply records, executor records | Concurrent calls can both pass the gate-scoped prior-applied check before either records completion | Immediate readiness refresh, gate key, sequential prior-record check, lower-level excerpt check | NONE; F03 rollback guard does not serialize final apply | NO for a final-local design | Possible in principle, but existing primitives do not prove a safe claim-to-mutation boundary | Yes for concurrent behavior | A reservation/claim state may be needed |
| F07 | MEDIUM | Apply/rollback records, auxiliary audit, post-apply verification | Human verifier, audit readers, workflow reports | Evidence can be incomplete or verification can remain unopened after a mutation; no independent byte re-read | Primary apply/rollback records, hashes, warnings, backups, separate human gate | NONE | NO | Possible but broad lifecycle design remains | Yes for evidence/failure behavior | Likely if durable recovery/evidence state is added |

### 4.1 Existing production records relevant to F02

The current records carry these facts:

- Proposal records carry `original_excerpt`, `proposed_excerpt`, `patch_text`,
  `diff_preview`, target paths, risk, and optional `approval_id`. They do not
  carry a reviewed-base hash or full reviewed content.
- Patch review records carry proposal identity, review decision, reviewer,
  target, diff presence, and approval status. They do not carry a base hash,
  patch-body hash, or execution identity.
- Every patch apply record carries `original_hash_before` and
  `original_hash_after` computed around that apply attempt. For a dry-run,
  `original_hash_before` is the base read at dry-run execution time.
- The accepted dry-run review and final approval records carry IDs linking to
  the dry-run apply record. They do not copy or independently validate its
  base hash.
- The final executor rechecks current proposal, queue, dry-run, and gate
  status, then calls the shared apply primitive. It currently does not compare
  current final content to the dry-run record's `original_hash_before`.
- Direct apply has no dry-run ID or reviewed-base record to consume. It reads
  current content and requires the stored excerpt to occur exactly once.

This means a reviewed-base hash already exists as execution evidence on a
dry-run apply record, but it is not a universal reviewed-base authority. A
future final-only guard could truthfully compare that existing dry-run
`original_hash_before` with the current final pre-write content. A direct path
has no equivalent reviewed-state source. Persisting a hash at proposal or
review time would be a new persistence/record contract and would require a
separate decision about which review state is authoritative.

## 5. F01 Analysis: Direct Authority Divergence

F01 remains HIGH because direct production callers can reach
`apply_patch_proposal(..., dry_run=False)` after local proposal/status and
conditional legacy approval checks without the final-real-apply chain. The
direct route, tool executor, and self-modification workflow are live consumers,
not test-only paths. The final executor remains a real stronger workflow for
its own callers.

The repository still does not prove that direct mutation is unauthorized, that
final-real-apply is universal, or that the two paths are an intentional dual
trust architecture. A fix that makes final-real-apply canonical, contains the
direct route, or creates a common direct execution authority necessarily makes
one of those policy decisions. A local direct-only strengthening would change
the trust and retry contract without proving which direct callers remain
legitimate.

Disposition: `BLOCKED_BY_CANONICAL_DECISION`. No Build is forced.

## 6. F02 Analysis: Reviewed-Base / Hash Binding

F02 is the highest-value remaining HIGH candidate, but it is not a proven next
Build boundary.

### 6.1 Base truth by path

For the final-real-apply workflow, the closest existing reviewed-base truth is
the dry-run apply record's `original_hash_before`. It is captured when the
approved dry-run executes, then linked through dry-run review and final gate
records. The final executor currently reads that record for readiness but does
not compare the hash with the content used by final mutation.

For direct apply, there is no reviewed-base hash, full reviewed content, or
dry-run record binding. Patch review proves diff presence and review state, not
the bytes that were reviewed. The direct primitive only reads current content
at execution and checks the exact stored excerpt.

### 6.2 Truthful guard assessment

A final-only future guard could be bounded as follows:

1. Use the final gate's linked dry-run apply record as the reviewed-base source.
2. Require a valid dry-run `original_hash_before`.
3. Read the current final target and compute the existing UTF-8 SHA-256.
4. Compare it before calling the shared real mutation primitive.
5. Fail closed on missing, malformed, or mismatched state.

That guard would protect final-real-apply consumers without new persistence,
schema migration, approval redesign, or canonical-route selection. It would
not truthfully fix direct apply, because direct callers have no corresponding
reviewed-base source. Adding a proposal/review-time hash would be newly
persisted state. Applying a dry-run hash to all direct calls would be a fake
universal binding because direct calls do not require that workflow.

### 6.3 Disposition

F02 is `VALID_LATER_BUILD` only as a separately scoped final-workflow design,
or `NEEDS_MORE_REVIEW` for any cross-path claim. M106A does not select it as a
next Build because the exact affected finding spans direct and final paths and
the evidence truth differs by trust model. The direct route's reviewed-base
source and compatibility policy remain unresolved.

## 7. F04 Analysis: Mutation / Record Atomicity

F04 remains HIGH. The current real apply sequence still writes the target after
backup creation and before durable apply-record persistence. `Path.write_text`
is not an atomic replace protocol. A process interruption, partial write, or
record persistence failure can leave changed target content without a normal
successful apply record. Auxiliary Timeline, graph, mutation-log, and later
verification writes are separate.

A true correction may require temporary-file and atomic-replace semantics,
write-ahead or reservation state, recovery states, fsync policy, backup
reservation, and explicit handling of mutation-success/record-failure. These
are new persistence and recovery contracts, not a small local guard.

Disposition: `TOO_BROAD_FOR_NEXT_BUILD`.

## 8. F05 Analysis: Reusable Direct Approval

The consumed object is the legacy `approval_queue.json` item referenced by the
proposal's `approval_id`. Direct apply reads its current `status`; it does not
claim or consume the item. The queue item does not independently bind exact
proposal revision, target, original excerpt, proposed excerpt, patch body,
base hash, session, actor, or execution attempt.

Reuse is observable and may be intentional for the current action-specific
workflow: failed or blocked attempts can be retried, and a status-read approval
is compatible with existing direct callers. A local atomic/single-use claim
would change those retry and approval semantics. The atomic
`claim_approval_for_execution` primitive belongs to the separate individual
approval-record store and is not the legacy queue item consumed by patch
apply. Reusing it would change the approval model rather than locally fixing
F05.

Disposition: `BLOCKED_BY_CANONICAL_DECISION`. No Build is recommended while
direct approval policy and retry intent remain unresolved.

## 9. F06 Analysis: Final Executor Concurrency / Single-Use

F06 remains MEDIUM, not HIGH. The final executor's gate-scoped check is
sequentially effective but not atomic with the shared mutation call.

### 9.1 Exact race

For two concurrent calls using the same final approval gate:

1. Call A loads the executor records and sees no applied record.
2. Call B loads the executor records before A saves an applied executor record
   and sees the same result.
3. Both refresh gate, proposal, legacy queue, and dry-run readiness.
4. Both call `apply_patch_proposal(..., dry_run=False)`.
5. Each lower-level apply creates its own apply record and backup attempt before
   saving its apply record after the target write.

If the first write removes the only original excerpt before the second read,
the second call commonly fails the exact-one excerpt check. That is not an
atomic guarantee. If both calls read the same old content before either write,
or if the replacement preserves a match, both can pass and duplicate writes,
backups, and apply records can result. Executor records can then disagree about
which apply completed, and post-apply verification can have ambiguous
execution identity.

### 9.2 Claim design proof

The storage owner for the intended claim is the final executor record store.
The natural key is `real_apply_approval_gate_id`; the state would need to move
from ready to a claimed/reserved state before the shared mutation call, then to
applied or failed.

The existing atomic primitive in `approval_queue.py` locks and atomically
replaces an individual approval record. It does not own the legacy approval
queue item or final executor record, so it cannot be reused truthfully without
changing approval semantics. The final executor JSON store has no equivalent
claim operation. A new executor-local file lock or atomic reservation would
need a defined crash and recovery contract.

Claim-before-mutation leaves a failure window: a process can crash after the
claim and before mutation, potentially blocking a legitimate retry. Mutation
before durable applied state leaves the same unrecorded-mutation problem as
F04. Claim failure, crash recovery, and post-mutation recording therefore
overlap the F04 boundary. A local claim cannot be called Build-ready without
deciding whether it reserves, consumes, expires, or recovers the final
authority.

Disposition: `VALID_LATER_BUILD`, but only after a separate executor claim
design proves safe separation from F04. It is not the next HIGH candidate.

## 10. F07 Analysis: Audit / Verification Evidence Split

F07 remains MEDIUM and currently proves an imperfect evidence architecture more
than a current mutation-safety failure. Apply and rollback records are primary
durable action records. Timeline, graph, Working Memory, and mutation-log
integrations catch their own failures and append warnings where possible.
Post-apply verification binds source record IDs, proposal/apply/rollback IDs,
target, status, and human decision, but does not independently reread and hash
the target. Verification is intentionally a separate evidence-only human gate.

The current evidence does not prove incorrect verification or an unverifiable
execution identity in every successful case. It proves that auxiliary audit
or later verification may be incomplete. Mutation-prevention findings rank
above this evidence gap.

Disposition: `LOWER_PRIORITY_EVIDENCE_GAP`.

## 11. Candidate Ranking

Scores are qualitative and reflect current production proof, not architecture
preference. F03 is excluded because M105B closed it.

| Rank | Finding | Current severity | Production consumer strength | Security value | Canonical-route independence | Behavior-change risk | Compatibility risk | Persistence impact | Concurrency impact | Implementation size | Failure-closed quality | Testability | Recommended status |
|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | F02 reviewed-base/hash binding | HIGH | STRONG | HIGH | PARTIAL: final-only is independent; universal direct-plus-final is not proven | MEDIUM/HIGH | MEDIUM | NONE for final-only; likely new state for universal | LOW | MEDIUM for final-only | STRONG if hash source is present | STRONG for final-only | `VALID_LATER_BUILD` |
| 2 | F06 final executor concurrency | MEDIUM | STRONG | MEDIUM | YES for final-local policy | MEDIUM | LOW/MEDIUM | Claim/reservation state may be required | HIGH | MEDIUM/LARGE | Not proven until crash behavior is defined | MEDIUM/STRONG | `VALID_LATER_BUILD` |
| 3 | F01 direct authority divergence | HIGH | STRONG | HIGH | NO while route legitimacy/canonicality is unresolved | HIGH | HIGH | Likely if attempt/identity binding is selected | MEDIUM | MEDIUM/LARGE | Possible only after policy | Medium | `BLOCKED_BY_CANONICAL_DECISION` |
| 4 | F04 mutation/record atomicity | HIGH | STRONG | HIGH | YES in principle | HIGH | HIGH | HIGH: recovery/transaction state likely | MEDIUM | LARGE | Strong only after recovery design | Complex | `TOO_BROAD_FOR_NEXT_BUILD` |
| 5 | F05 reusable direct approval | MEDIUM | STRONG | MEDIUM/HIGH | NO while direct approval/retry policy is unresolved | HIGH | HIGH | Claim state or legacy contract impact | MEDIUM | MEDIUM | Strong claim possible but semantics change | Strong | `BLOCKED_BY_CANONICAL_DECISION` |
| 6 | F07 audit/verification split | MEDIUM | STRONG | LOW/MEDIUM | YES technically, but lifecycle scope is broad | MEDIUM | MEDIUM | Likely for durable recovery/evidence contracts | LOW/MEDIUM | MEDIUM/LARGE | Current primary record is already fail-visible | Medium | `LOWER_PRIORITY_EVIDENCE_GAP` |

The table does not promote F02 to a next Build because its strongest bounded
shape is final-only while the finding's affected path includes direct apply.
That distinction is a trust-model boundary, not an implementation detail.

## 12. Selected Finding

```text
Selected finding: NONE
```

F02 ranks highest among the remaining HIGH findings for security value and
consumer strength, but no single truthful cross-path binding is proven. F01
requires a canonical authority decision. F04 is broad. F05 changes direct
approval semantics. F06 is lower severity and its claim boundary overlaps F04.
F07 is an evidence gap without a proven current safety failure.

M106A therefore does not select a finding or silently reinterpret a final-only
guard as a universal patch fix.

## 13. Selected Model

```text
Selected model: MODEL_F_NO_NEXT_INDEPENDENT_BUILD
```

This model records that M105B removed F03 but the remaining findings do not yet
prove one bounded, independent, production-justified HIGH Build. It preserves
the current direct and final trust models, avoids new authority, and returns
the unresolved boundary to the human/project-manager.

## 14. Build-Readiness Decision

Principal decision:

```text
E_NO_NEXT_INDEPENDENT_HIGH_FIX_PROVEN
```

Selected finding: `NONE`

Selected model: `MODEL_F_NO_NEXT_INDEPENDENT_BUILD`

Future Build: `NOT JUSTIFIED`

This is not a claim that F01, F02, or F04 ceased to be real HIGH gaps. It is a
finding that none presently satisfies all ten independence-gate requirements
as one small next Build without either making a path-policy decision,
introducing new reviewed state, or entering broad mutation/recovery design.

## 15. Independence Gate Result

| Requirement | M106A result |
|---|---|
| Real production consumer exists | YES for all six findings |
| Concrete HIGH-value safety/correctness gap exists | YES for F01, F02, F04; F03 is closed |
| No canonical-route selection required | NOT PROVEN for F01/F05; only partial for F02; yes locally for F04/F06/F07 |
| No Generic Act required | YES |
| No broad patch redesign required | NO for F04; not proven for F06; unresolved for cross-path F02 |
| No legitimate caller silently invalidated | NOT PROVEN for direct-path changes |
| Small production/test file set | Only final-only F02 is small; universal F02 is not bounded |
| Existing state truthfully supports fix or bounded new state justified | Final-only F02 uses existing state; universal F02 requires new state or policy |
| Failure behavior testable | YES in principle, but not enough to select a cross-path Build |
| Rollback/removal path clear | Local final-only removal is clear; no universal removal contract is selected |

## 16. Exact Future Build Boundary If Justified

No future Build is justified by M106A. Therefore no exact implementation
boundary is authorized.

A later PM-authorized review may separately consider a final-workflow-only F02
guard using the existing dry-run apply record hash, but that would need to state
explicitly that direct apply remains outside the binding. It must not be
presented as a universal F02 resolution. Alternatively, a later policy review
may decide the source of truth for direct reviewed-base state. Those are
separate choices, not a combined M106A Build.

## 17. Expected Future Build Files

```text
NONE SELECTED
```

No production or existing test file is authorized for a future Build by this
record.

## 18. Forbidden Build Files and Behaviors

Without a new PM-authorized decision, do not modify:

- `aether/action/patch_apply.py`;
- `aether/action/patch_rollback.py`;
- `aether/action/final_real_apply_executor.py`;
- `aether/action/real_apply_approval_gate.py`;
- `aether/action/approval_queue.py`;
- `aether/action/patch_proposal.py`;
- `aether/action/patch_review.py`;
- direct patch, tool-executor, or self-modification routes;
- any patch API model or route registration;
- `tests/test_patch_rollback_expected_state_binding.py`;
- `RestrictedReadAuthorityBinding` or restricted-read runtime;
- `PROGRESS.md`, README, Constitution, or Architecture;
- dependencies, runtime/private data, or stored records.

Do not implement F01, F02, F04, F05, F06, or F07 under M106A. In particular,
do not add reviewed-base persistence, make final-real-apply universal, add a
direct approval claim, add a final executor reservation, add transactional
mutation behavior, redesign rollback, or add automatic verification.

## 19. Persistence Impact

M106A persistence impact: NONE.

No record, field, schema, migration, lock file, reservation, recovery state,
or runtime data is created. The existing M105B `original_hash_after` contract
remains unchanged. The existing dry-run `original_hash_before` is evidence for
analysis only and is not newly promoted to universal authority.

## 20. Behavior-Change Impact

M106A behavior change: NONE.

No apply, rollback, final executor, approval, verification, route, API, or
failure behavior changes. F03 remains closed exactly as implemented by M105B.

## 21. Compatibility Impact

M106A compatibility impact: NONE.

Direct callers, self-modification, tool execution, final-real-apply, legacy
approval reuse, retry behavior, old records, and existing route contracts are
preserved. No caller is silently invalidated and no migration is introduced.

## 22. Concurrency Implications

M106A adds no concurrency behavior. The F06 race remains documented: the
gate-scoped prior-applied check is not atomic with the shared mutation call.
The M105B rollback expected-state check also does not claim to be a concurrent
rollback lock. No claim, reservation, lock, or recovery state is added.

## 23. Failure-Closed Behavior

Because M106A is read-only, existing failure behavior is preserved:

- M105B rollback rejects missing, malformed, or mismatched expected state
  before restore;
- direct and final patch apply continue to reject missing proposals, invalid
  status, missing required approval, critical targets, unreadable targets, and
  missing/ambiguous excerpts;
- final executor readiness continues to reject incomplete gates and prior
  sequential applied records;
- no new failure path is claimed by this review.

## 24. Rollback / Removal Path

The M106A design candidate and static contract test are untracked local review
evidence. Their removal path is deleting exactly those two files. No runtime
rollback, data conversion, schema rollback, route restoration, or production
change is necessary.

## 25. Authority Ownership

Current ownership remains unchanged:

- Human/project-manager owns the unresolved policy and Build authorization.
- Action services own direct patch, final executor, and rollback lifecycles.
- The final executor owns its local readiness check, not universal patch
  authority.
- The legacy approval queue owns its status record; it is not an exact patch
  authority and is not atomically claimed by M106A.
- Verification and post-apply verification supply evidence; they do not
  authorize mutation.
- The existing apply record owns `original_hash_after` as rollback expected
  state under M105B.
- No common patch mutation authority is selected.

## 26. Explicit Non-Goals

M106A does not:

- implement any security fix;
- modify patch runtime or patch mutation;
- modify `patch_rollback.py` or reopen F03;
- choose a canonical patch mutation route;
- declare direct patch apply unauthorized;
- make final-real-apply universal;
- change approval semantics, approval consumption, or retry policy;
- add reviewed-base persistence or a universal hash binding;
- add transactional mutation, atomic replace, write-ahead state, reservation,
  recovery state, or filesystem transaction semantics;
- add final executor concurrency claims or rollback concurrency claims;
- add automatic post-apply verification or durable evidence aggregation;
- implement Generic Act, generic mutation authority, shared Action authority,
  or a generic mutation registry;
- modify API routes, OpenAPI, `/chat`, `PROGRESS.md`, README, Constitution,
  Architecture, production code, existing tests, dependencies, or runtime data;
- commit, tag, push, begin M106B, or begin M107.

## 27. Build Authorization Gate

```text
M106A review: COMPLETE LOCALLY
M105B F03: CLOSED / RESOLVED
Principal decision: E_NO_NEXT_INDEPENDENT_HIGH_FIX_PROVEN
Selected finding: NONE
Selected model: MODEL_F_NO_NEXT_INDEPENDENT_BUILD
Future patch security Build: NOT JUSTIFIED / NOT AUTHORIZED
Canonical patch route: NOT SELECTED / NOT PROVEN
Generic Act: NOT_IMPLEMENTED / NOT_AUTHORIZED / NOT_GRANTED
```

No future Build is authorized by this record. A human/project-manager decision
is required before any remaining finding is implemented.

## 28. Next-Step Gate

```text
Next authorized action: HUMAN/PROJECT-MANAGER M106A HIGH-RISK PRIORITY REVIEW
No patch runtime change is authorized.
No approval change is authorized.
No canonical patch authority is selected.
No transactional mutation behavior is authorized.
No Generic Act is authorized.
No M106B or M107 is authorized.
```

Control returns to the human/project-manager.
