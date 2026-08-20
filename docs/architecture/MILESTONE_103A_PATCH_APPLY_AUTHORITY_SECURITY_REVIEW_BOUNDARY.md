# Milestone 103A Patch Apply Authority and Security Review Boundary

Classification: STRICT READ-ONLY SECURITY / AUTHORITY / CONSUMER-PROOF REVIEW

Status: REVIEW COMPLETE LOCALLY / REAL GAP / NO BUILD AUTHORIZED

This record audits the current patch mutation lifecycle. It does not modify
patch apply, patch rollback, final-real-apply, approval semantics, routes,
production code, or runtime data. It does not create a mutation authority
binding and does not reuse `RestrictedReadAuthorityBinding`.

## 1. Current Git State

Audit-start state:

- Branch: `main`.
- Expected HEAD: `04933f9ffc9c28c37014c0db3fcaf39cc4d7c0fc`.
- Local `main`, `origin/main`, and remote `main` matched.
- Tracked worktree: clean.
- M102A: FINALIZED / COMMITTED / TAGGED / PUSHED / PM-ACCEPTED baseline.
- M102A decision: `D_NO_SECOND_CAPABILITY_CURRENTLY_JUSTIFIED`.
- M102A highest-ranked near-candidate: `PATCH_APPLY_EXECUTION_PATH`.
- Patch authority concern: REAL.
- Patch Build: NOT AUTHORIZED.
- Full-suite durable baseline: `3172/3172 passed, 0 failures, 0 errors,
  9 warnings`.
- OpenAPI baseline: `306 paths / 112 schemas`.
- `api_server` baseline: `8 direct @app routes / 23 include_router / 0 direct
  /action/*`.
- M103A creates only this design candidate, its static/document lock, and the
  external PM evidence summary as local review evidence.
- No commit, tag, push, `PROGRESS.md` change, production edit, existing-test
  edit, dependency change, or runtime/private-data change is authorized.

Git verification at audit start:

```text
git status: clean
branch: main
HEAD: 04933f9ffc9c28c37014c0db3fcaf39cc4d7c0fc
main: 04933f9ffc9c28c37014c0db3fcaf39cc4d7c0fc
origin/main: 04933f9ffc9c28c37014c0db3fcaf39cc4d7c0fc
remote main: 04933f9ffc9c28c37014c0db3fcaf39cc4d7c0fc
git diff --check: CLEAN
```

## 2. Current Authority

The current ownership boundary remains:

- Core Governance owns authorization and hard constraints where its governed
  capability path is used.
- Core Coordination owns canonical execution context and execution-attempt
  binding where its governed path is used.
- Action services own patch proposal, review, apply, rollback, and final
  executor lifecycles.
- Interface routers expose routes and do not become cognitive authority.
- Verification supplies evidence and verification status; it does not authorize
  mutation.
- `GOVERNANCE_EVALUATION != EXECUTION_AUTHORIZATION`.
- Generic Act: `NOT_IMPLEMENTED`.
- Generic Act integration: `NOT_AUTHORIZED`.
- Generic Act authority: `NOT_GRANTED`.

The M101B `RestrictedReadAuthorityBinding` was inspected only as a boundary
reference. It binds existing restricted-read facts; it is not a patch contract,
not a generic identity, and not a permitted implementation template for M103A.

## 3. Exact Objective

Determine whether the current production patch-mutation system has a concrete
authority or security gap that justifies a future bounded Build.

The review must distinguish:

- legitimate action-specific authority;
- unsafe or ambiguous mutation authority;
- duplicate but non-harmful authority paths;
- a real bypass of a stronger required gate.

The review must not assume that final-real-apply is the universal canonical gate
for every patch route. It must state when that intent is NOT PROVEN.

## 4. Patch Runtime Inventory

| Stage | Production path | Current production role | Mutation? |
|---|---|---|---|
| Proposal creation | `patch_routes.py` -> `patch_service.py` -> `patch_proposal.create_patch_proposal` | Reads target, stores proposal, excerpt, diff preview, risk, and optional legacy approval item | NO |
| Proposal status | `patch-proposal/mark-status` -> `mark_patch_proposal_status` | Changes proposal lifecycle status when the supplied status is valid | NO |
| Patch review | `patch-review/review` -> `review_patch_proposal` | Records a human review and may change proposal status | NO |
| Legacy approval queue | `approval_queue.create_approval_item` / `get_approval_item` | Stores pending/approved/rejected/cancelled queue items | NO; status is consumed by local mutation paths |
| Direct patch apply | `patch-apply/apply` -> `apply_patch_proposal` | Rechecks proposal, reads target, replaces one exact excerpt, and optionally writes | YES when `dry_run=False` |
| Approved dry-run gate | `approved_dry_run_gate.execute_approved_dry_run` | Calls the same apply primitive with `dry_run=True` only | NO |
| Dry-run review | `dry_run_review_gate.submit_dry_run_review` | Records human acceptance/rejection of a completed dry-run | NO |
| Final approval gate | `real_apply_approval_gate.submit_real_apply_final_decision` | Records final decision and consumes a newly created legacy queue item later | NO |
| Final-real-apply executor | `final_real_apply_executor.execute_final_real_apply` | Refreshes readiness and calls the same apply primitive with `dry_run=False` | YES |
| Patch rollback | `patch-rollback/rollback` -> `rollback_patch_apply` | Replaces target content with a saved backup when local eligibility checks pass | YES when `dry_run=False` |
| Post-apply verification | `post_apply_verification_gate` | Records a human verification decision about an apply or rollback record | NO |
| Mutation/audit records | patch records, mutation log, Timeline, graph, Working Memory | Record lifecycle and result evidence | NO |

Current production consumers are real: target files, patch apply records,
rollback records, mutation log readers, Timeline/graph readers, final executor
records, and post-apply human verification all consume patch lifecycle output.

## 5. Patch Mutation Lifecycle

### 5.1 Proposal creation

`create_patch_proposal` first calls `read_restricted_file(target_path, 12000,
source=patch_proposal)`. On failure it creates a rejected proposal. On success
it stores:

- a UUID proposal identity;
- caller-supplied target path and the reader's normalized path;
- request text, reason, and proposed-change summary;
- `original_excerpt`, truncated to 4000 characters;
- `proposed_excerpt`, truncated to 8000 characters;
- unified diff preview and patch text;
- risk level and `requires_user_approval`;
- a verification plan;
- optional `approval_id` from the legacy queue;
- caller metadata and warnings.

The proposal stores no proposal revision number, no reviewed-base content hash,
no patch-body hash, no session binding, no actor/identity binding, and no
execution-attempt identity. A revision console creates a new proposal UUID by
calling `create_patch_proposal`; it records a relation in its own private
console record but does not supersede or invalidate the old proposal
automatically.

### 5.2 Proposal review and approval

`review_patch_proposal` checks that a diff exists. For an `approve` decision it
requires a legacy queue item with status `approved` when the proposal says
`requires_user_approval`; it then marks the proposal `approved`. It does not
bind a review to a base hash, patch hash, session, identity, or execution
attempt. It does not itself consume mutation authority.

The direct patch apply path does not require a patch-review record. It requires
the stored proposal status to be `approved`. The public status endpoint can
change a proposal to a valid status, including `approved`, without proving that
a review record exists. A high-risk proposal still requires its associated
legacy approval item to be approved at apply time.

### 5.3 Direct real mutation

`apply_patch_proposal(proposal_id, dry_run=False)` performs these checks:

1. proposal exists;
2. proposal status is `approved`;
3. if `requires_user_approval` is true, the optional `approval_id` resolves to
   a legacy queue item whose status is `approved`;
4. normalized target is not one of the protected identity/governance paths;
5. current target can be read;
6. the stored `original_excerpt` occurs exactly once in current content.

It then computes `original_hash_before` from the content just read and
`original_hash_after` from the replacement content. For real apply it creates a
backup, writes the replacement directly with `Path.write_text`, computes the
post-write file hash, and records success with `applied=True`.

The direct route can mutate a real target with `dry_run=False`: YES.

The direct route does not require:

- a final-real-apply approval gate;
- an accepted dry-run or dry-run review;
- an execution-attempt identity;
- a session or actor/identity binding;
- an approval freshness deadline;
- a direct-path single-use claim;
- a reviewed-base content hash;
- a patch-body hash;
- an atomic write protocol;
- automatic post-apply verification.

### 5.4 Backup and apply result

The backup is copied before the write under the configured private patch backup
directory. Its filename contains the proposal ID, timestamp, and filename. The
apply record stores the backup path but not a backup content hash at creation.

The apply record is initialized as failed and contains proposal ID, target,
approval ID/status, before/after hash fields, backup path, dry-run state,
changed/applied flags, checks, warnings, and metadata. The record is persisted
after the write attempt, not transactionally with the target write.

### 5.5 Rollback

`rollback_patch_apply` requires:

- an existing apply record;
- apply status `success`;
- `applied=True`;
- a backup path;
- a non-critical target;
- a readable current target;
- a backup path inside the configured backup root, present, and at most 65536
  bytes.

It computes current and backup hashes, creates a pre-rollback backup, writes the
backup content directly, computes the resulting file hash, and marks success
when the resulting hash equals the backup hash. It binds rollback to `apply_id`
and the saved backup path. It does not require an approval record, session,
identity, execution attempt, or current-target hash equal to the original
apply's post-write hash. It has no prior-successful-rollback or concurrency
lock.

### 5.6 Verification and evidence

Patch apply, rollback, gate, executor, and verification records are durable
private JSON records. Normal successful apply also attempts mutation-log,
Timeline, graph, and Working Memory evidence. These auxiliary writes catch
their own failures and append warnings where the record remains available.

Post-apply verification is a separate human gate. It can open from a successful
direct patch apply, a final executor, or a successful rollback. It binds the
verification record to source record IDs, proposal ID, apply ID, rollback ID,
target, status, backup/rollback facts, and the human decision. It does not
re-read and independently prove the exact file content that was changed.

## 6. Authority-Chain Matrix

`ABSENT` means the runtime does not establish that binding. It is not inferred
from a nearby field or from architectural intent.

| Stage | Producer | Consumer / owner | Authority type | Input identifiers | Output identifiers | Freshness | Single-use / replay | Target binding | Content / hash binding | Session / identity | Approval binding | Mutation permission | Evidence | Failure-closed behavior |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Proposal creation | Route request and `create_patch_proposal` | Proposal store / patch services | Planning record | target path, request text, metadata | proposal UUID, normalized path | Read-time target checks only | New proposal each call; no replay policy | Stored target and normalized path | Original/proposed excerpts; reviewed base hash ABSENT | ABSENT | Optional legacy queue ID | NO | Proposal record, Timeline, graph, mutation log | Reader failure creates rejected proposal |
| Proposal status | Status route | Proposal store and apply | Lifecycle state | proposal ID, requested status | updated proposal status | ABSENT | Any valid transition is accepted; no transition history in proposal | Inherited stored target | Inherited excerpts | ABSENT | Inherited approval ID | NO | Timeline event | Invalid status returns none; no review proof required |
| Patch review | Human review request | Patch review store and proposal status | REVIEW_ONLY plus proposal lifecycle | proposal ID, decision, reviewer | review UUID, proposal status after | ABSENT | Multiple review records can exist; no one-use claim | Copies target path | Diff existence only; base hash ABSENT | ABSENT | Checks legacy queue status if required | NO | Review record, Timeline, graph, mutation log | Missing diff or unapproved required queue blocks approval |
| Legacy queue item | Proposal/review/final gate | Direct apply, final gate/executor, tool paths | APPROVAL_RECORD / LEGACY_COMPATIBILITY_STATE | request text, action description, plan, metadata | approval item ID and status | Status checked; age/content freshness ABSENT | Status can be read repeatedly; no apply consumption | Not exact | Not exact | ABSENT | Proposal stores item ID; item does not verify proposal | Indirect only | Queue item and decision time | Non-approved status blocks paths that require it |
| Direct patch apply | Apply route and proposal record | `apply_patch_proposal`, target file | ACTION_SPECIFIC_GOVERNED_EXECUTION | proposal ID, dry-run flag, metadata | apply UUID, backup path, hashes, status | Current content read and excerpt check only | No execution attempt; same proposal can be retried if excerpt matches | Stored target and normalized path | Exact stored excerpt; before/after execution hashes; reviewed base hash ABSENT | ABSENT | Queue status only when proposal requires it | YES when false | Apply record, Timeline, graph, mutation log attempt | Missing/unapproved/critical/ambiguous/read/write failures block or fail |
| Approved dry-run gate | Approved proposal/review | Dry-run executor and human | READINESS_SIGNAL / PLANNING_ONLY | proposal/review IDs | gate ID, patch apply ID | Gate status only | Repeated completion blocked unless force metadata | Copied sanitized target | Delegates to dry-run apply; no review hash contract | ABSENT | Proposal/review linkage; no execution authorization | NO; hard-coded dry-run | Gate and dry-run record | Non-approved or repeated gate blocks |
| Dry-run review | Human reviewer | Real-apply gate | REVIEW_ONLY | approved gate ID, apply ID, decision | review gate ID, decision | No TTL or content recheck | One reviewed state unless force metadata | Copied target | Consumes dry-run status; no independent hash comparison | ABSENT | Human decision, not execution authorization | NO | Review record | Missing/incomplete dry-run blocks |
| Final approval gate | Accepted dry-run review | Final executor | EXECUTION_AUTHORIZATION readiness record | review/gate/apply/proposal IDs | gate ID, final decision, approval item ID | Status rechecked; no time freshness | Gate can remain approved; executor prior-record check is gate-scoped | Sanitized proposal target | IDs and dry-run linkage; no exact base/patch hash binding | ABSENT | Creates and stores legacy queue item; final decision separate | Indirect; executor must consume | Gate, queue, Timeline, graph, mutation log | Incomplete chain or non-approved decision blocks |
| Final executor readiness | Final gate, proposal, queue, dry-run records | Final executor | ACTION-SPECIFIC_EXECUTION_AUTHORIZATION | gate ID, proposal ID, queue ID, dry-run ID | executor record ID, ready/applied status | Rechecks current statuses immediately before call | `_has_applied_record` prevents prior applied record for same gate; not atomic with write | Current approved proposal target | Re-runs current excerpt checks through apply; no dry-run hash equality | ABSENT | Queue item must be approved; no consumed flag | YES only after readiness | Executor record, audit records | Missing status, proposal, queue, dry-run, or prior-use check blocks |
| Final real mutation | Final executor | Same `apply_patch_proposal` primitive and target | ACTION-SPECIFIC_GOVERNED_EXECUTION | executor/gate/proposal IDs | real apply ID, backup, hashes | Current content/excerpt only | Gate-scoped prior record; concurrent race not prevented | Proposal target and normalized path | Same direct apply semantics; no execution-attempt/session hash | ABSENT | Final gate and queue status | YES | Apply and executor records, Timeline, graph, mutation log attempt | Apply failure becomes blocked/failed; no automatic restore |
| Rollback | Rollback route and successful apply record | `rollback_patch_apply`, target file | ACTION-SPECIFIC_RESTORATION | apply ID, saved backup path | rollback ID, pre-backup, hashes | Current read and backup-path check only | No single-use or concurrency rule | Apply target and normalized path | Backup hash and resulting hash; expected current post-apply hash ABSENT | ABSENT | ABSENT | YES when false | Rollback record, Timeline, graph, mutation log attempt | Ineligible apply/path/hash/read/write failures block or fail |
| Post-apply verification | Apply/rollback/executor record | Human verifier | EVIDENCE_ONLY / REVIEW_ONLY | source ID, apply/rollback/proposal IDs | verification gate ID, decision | Record status only; no independent target re-read | One open decision unless force metadata | Copied source target | Record status and rollback facts; exact content proof ABSENT | ABSENT | ABSENT | NO | Verification record, Timeline, graph, mutation log | Invalid source/decision blocks |

## 7. Direct Patch Apply Analysis

### 7.1 Exact answers

- Can direct patch apply mutate a real target with `dry_run=False`? **YES.**
- Required proposal state: stored proposal exists and has status `approved`.
- Proposal/review state required: proposal approval state is required; a patch
  review record is **not** required by `apply_patch_proposal`.
- Is approval required? **Conditional.** High-risk/critical proposals set
  `requires_user_approval=True`; lower-risk proposals may not require a queue
  item. If required, the stored legacy queue item must currently be approved.
- Does approval bind the exact proposal? **Indirectly by the proposal's stored
  `approval_id`; the queue item does not independently validate proposal data.**
- Does approval bind a proposal revision? **NO.** No revision/version field is
  checked by direct apply.
- Does approval bind target? **NO exact approval binding.** The proposal binds
  its stored target, not the queue item's request content.
- Does approval bind content hash? **NO.**
- Does approval bind patch body? **NO.**
- Does approval bind session? **NO.**
- Does approval bind actor/identity? **NO.**
- Does approval bind an execution attempt? **NO.**
- Does approval bind time/freshness? **NO TTL or decision-age check.**
- Does direct patch apply consume approval once? **NO.** It reads legacy queue
  status and does not claim or consume the item.
- Can the same approval be replayed? **YES, subject to the proposal and current
  excerpt checks.**
- Can the same proposal be applied multiple times? **There is no explicit
  single-use rule.** A second application is usually blocked if the original
  excerpt disappeared, but it is not prevented by authority state and can recur
  when the excerpt remains or reappears.
- What prevents stale-target mutation? **Only the current exact excerpt count
  check.** A reviewed-base hash is absent. Unrelated changes that leave the
  excerpt unique do not block.
- What prevents patch-body substitution? **The route accepts only proposal ID,
  so the caller cannot pass a new body at apply time.** There is no persisted
  patch-body hash or protected proposal-record integrity proof.
- What prevents target substitution? **Apply uses the stored proposal target,
  not a target supplied in the apply request.** There is no session or identity
  binding to the target.
- What prevents cross-session reuse? **Nothing in direct patch apply.**
- What prevents cross-user or cross-context reuse? **Nothing in direct patch
  apply beyond possession of the proposal ID and any required queue approval.**
- What happens if the file changed after review? **If the original excerpt is
  absent, apply blocks; if it remains exactly once, apply proceeds against the
  changed file.**
- What happens if backup succeeds but write fails? **The apply record becomes
  failed with the backup path and `applied=False`; no normal rollback is
  eligible because rollback requires a successful applied record.**
- What happens if mutation succeeds but recording fails? **The normal path
  persists the apply record after the write and catches auxiliary Timeline,
  graph, and mutation-log failures as warnings. A process or persistence
  failure between write and apply-record save can leave target mutation without
  a durable apply record.**

### 7.2 Authority interpretation

Direct patch apply is not an unprotected arbitrary write: it has meaningful
action-specific proposal, status, target, critical-path, excerpt, backup, and
hash controls. Those controls are useful to its current consumers.

It is nevertheless weaker than the final-real-apply chain and lacks several
authority facts that matter for mutation: execution attempt, session/identity,
fresh reviewed-base binding, direct single-use, and atomic write/recording
behavior. The route is live and its mutation consumer is proven.

## 8. Final-Real-Apply Analysis

The final-real-apply path is a stronger action-specific workflow:

```text
approved proposal/review
  -> approved dry-run gate
  -> completed dry-run apply record
  -> accepted dry-run human review
  -> final-real-apply approval gate
  -> final decision approve_real_apply
  -> new legacy approval queue item approved
  -> executor readiness refresh
  -> gate-scoped prior-apply check
  -> same apply_patch_proposal(..., dry_run=False) primitive
  -> apply / backup / hashes / records
  -> separate post-apply human verification
```

Additional readiness required:

- accepted dry-run review;
- completed dry-run record with `dry_run=True` and status `dry_run`;
- proposal currently `approved`;
- final gate status `final_approved` and decision
  `approve_real_apply`;
- final gate's legacy queue item currently `approved`;
- no prior executor record for the same gate with status `applied`.

Approval freshness: status is refreshed immediately before execution, but no
decision timestamp TTL or identity/session freshness is enforced.

Approval single-use: the final executor has a gate-scoped prior-applied-record
check. This is a meaningful single-use rule for sequential reuse, but the
check-and-apply sequence is not transactionally locked; concurrent executor
calls can both pass `_has_applied_record` before either applied record is saved.

Exact mutation binding: gate, proposal, queue, and dry-run IDs are bound in
records. The executor reuses the proposal's target and re-runs current excerpt
checks through the lower-level apply function. It does not prove that the
current base content or patch body is byte-identical to the content reviewed in
the dry-run.

Same lower-level primitive: **YES.** The final executor calls
`apply_patch_proposal(record["proposal_id"], False, ...)`.

Can direct patch apply bypass it? **YES.** The direct patch route calls the same
primitive without opening or consuming final gate, dry-run, review, or final
queue records.

Is that bypass intentional and architecture-authorized? The repository proves
that both are live action-specific paths and that final-real-apply is stronger.
It does **not** prove that final-real-apply is the universal required gate for
the direct route, nor that the direct route is unauthorized. The bypass is
therefore observable, but its intended policy classification is **NOT PROVEN**.

Canonical production mutation gate: final-real-apply is a canonical stronger
workflow for its own entry point. It is **NOT PROVEN** to be the canonical gate
for every production patch mutation.

## 9. Direct Apply versus Final-Real-Apply

| Concern | Direct patch apply | Final-real-apply | Evidence classification |
|---|---|---|---|
| Entry point | `/action/patch-apply/apply` | Final executor open/execute routes | Different live entry points |
| Caller | Route/service or tool path | Explicit final executor | Different trust workflows |
| Trust level | Action-specific proposal/status checks | Stronger dry-run/review/final gate chain | Final path stronger |
| Proposal | Required and currently approved | Required and rechecked approved | Shared proposal fact |
| Review | Not required by primitive | Accepted dry-run review required | Inconsistent requirement |
| Dry-run | Optional request flag; can be false directly | Completed dry-run required | Direct bypass exists |
| Approval | Conditional legacy queue status | Final gate plus new legacy queue status | Different stores/semantics |
| Approval freshness | Current status only | Current statuses only; no TTL | No temporal freshness contract |
| Approval single-use | ABSENT | Gate-scoped prior applied record; race not closed | Material difference |
| Target binding | Stored proposal target and normalized path | Current approved proposal target | Shared but no identity/session |
| Patch-body binding | Stored excerpts, no hash | Same lower-level stored excerpts | No separate body hash |
| Hash binding | Computes current before/after at execution | Same | Execution evidence, not reviewed-base proof |
| Backup | Before real write | Same | Shared primitive |
| Execution attempt | ABSENT | Executor record ID, not canonical attempt binding | Different record identity, no universal claim |
| Session/identity | ABSENT | ABSENT | Missing in both |
| Verification | Separate optional post-apply gate | Separate post-apply gate | Human evidence path |
| Audit evidence | Apply record plus auxiliary attempts | Executor and apply records plus auxiliary attempts | Final path has more chain evidence |
| Rollback | Eligible from successful apply record | Executor exposes rollback availability from successful apply | Shared rollback semantics |
| Failure behavior | Block/failed record; no automatic restore | Block/failed executor and apply records; no automatic restore | No transactional mutation |
| Intended production use | Direct action-specific mutation | Strong final human-reviewed mutation | Both live; universal canonicality NOT PROVEN |

Classification: **C. LEGACY PATH + CANONICAL STRONGER PATH**, with an important
qualification: “canonical stronger path” is proven for the final-real-apply
workflow, not as a universal requirement for every direct patch caller. The
evidence is insufficient to classify the direct route as an unauthorized bypass
without a new policy decision.

## 10. Approval Authority Review

| Representation | Classification | What it actually authorizes |
|---|---|---|
| Proposal status `draft` / `approval_required` / `approved` | READINESS_SIGNAL / LIFECYCLE STATE | Eligibility for later local checks; not sufficient by itself for high-risk queue-required apply |
| Patch review record | REVIEW_ONLY | Human review decision and proposal lifecycle transition; not execution authorization by itself |
| Legacy `approval_queue.json` item | APPROVAL_RECORD / LEGACY_COMPATIBILITY_STATE | Status consumed by direct patch apply when proposal requires it, and by final executor; no exact target/body/hash/session binding and no consumption claim |
| Individual approval record store | APPROVAL_RECORD for canonical restricted-read semantics | Not consumed by direct patch apply; its atomic claim is not part of patch apply |
| Approved dry-run gate | READINESS_SIGNAL / PLANNING_ONLY | Allows one guarded dry-run; hard-codes `dry_run=True` |
| Dry-run review decision `accept` | REVIEW_ONLY | Allows opening the final-real-apply approval gate; does not mutate |
| Real-apply approval gate final decision | EXECUTION_AUTHORIZATION for the final executor workflow | Establishes final readiness only; it never mutates directly |
| Final executor `ready` record | EXECUTION_AUTHORIZATION readiness | Allows explicit executor call after refresh; gate-scoped prior-use check applies |
| Post-apply verification decision | REVIEW_ONLY / EVIDENCE_ONLY | Records human assessment; does not apply or rollback |

There are multiple approval stores and multiple readiness records. Runtime
evidence does not support treating every `approved`, `accept`, or ready flag as
universal mutation authority.

## 11. Replay and Single-Use Security Review

| Scenario | Current result |
|---|---|
| Same approval + same patch | Direct apply can repeat; queue status is not consumed. Final gate blocks a prior sequential applied executor record for that gate. |
| Same approval + modified patch | The apply primitive uses stored proposal excerpts, not a request body. Proposal-record mutation or a different proposal is not bound by approval content. |
| Same approval + different target | Direct apply uses the stored proposal target; approval does not independently bind target. A different proposal/approval path can target elsewhere. |
| Same proposal after target content changes | Blocks only if original excerpt is absent or non-unique. Unrelated changes that preserve one match are accepted. |
| Same request after successful apply | No explicit direct-path one-use rule. Usually excerpt absence blocks, but this is content-dependent, not authority state. |
| Same request after failed apply | Can be retried; failed records do not consume direct authority. |
| Same backup for repeated rollback | No single-use check; repeated rollback can use the same backup if eligibility remains. |
| Concurrent apply attempts | No direct lock. Final executor's prior-record check is a check-then-apply race. |
| Concurrent rollback attempts | No rollback lock or claim. Both can read and write the same target/backup sequence. |

No universal single-use policy should be invented here. The evidence supports
recording that direct apply and rollback lack one, while final executor has a
sequential gate-scoped check with a concurrency gap.

## 12. Content-Integrity Review

| Value | Runtime role | Authority classification |
|---|---|---|
| `original_excerpt` | Exact replacement anchor; must occur once at apply time | Execution-gating, but not reviewed-base proof |
| `proposed_excerpt` | Replacement body stored in proposal | Execution input; no separate hash |
| `patch_text` / `diff_preview` | Human-readable preview and review presence check | Review-only |
| Proposal target / normalized path | Selects target and backup destination | Execution-gating target binding |
| `original_hash_before` | Hash of content read immediately before replacement | Execution evidence; not stored at proposal/review time |
| `original_hash_after` | Hash of updated content, and recomputed file hash after write | Post-write execution evidence |
| Backup content | Restoration source | Rollback input; backup hash computed during rollback |
| `backup_hash` | Hash of backup text during rollback | Rollback gating and verification |
| `hash_after` | Hash after rollback write | Rollback verification |
| Post-apply status | Record status and human verification input | Evidence-only after mutation |

An approved patch can execute against content different from the content
available when the proposal was created or reviewed if the original excerpt
still occurs exactly once. The current system does not store or compare a
reviewed-base hash, full reviewed content, patch-body hash, or dry-run
before/after hash against final apply.

## 13. Failure Atomicity Review

| Failure point | Current behavior | Evidence gap |
|---|---|---|
| Backup creation fails | Exception is caught; apply status is failed; target write is not reached | No mutation; no automatic retry/cleanup contract |
| Backup succeeds, write never starts | Failed apply record contains backup path after `done`; rollback rejects because apply is not successful | Backup can remain orphaned and is not a normal rollback candidate |
| Partial write | `Path.write_text` can fail after target alteration; exception marks record failed and `applied=False` | Partial target mutation may have no successful apply status or rollback eligibility |
| Write completes, post-write hash fails | Exception marks failed after target may already be changed | No automatic restore and no proven successful apply record |
| Write completes, apply-record save fails/crashes | Target mutation occurs before `done()` persists the apply record | Mutation can lack durable apply record |
| Apply record saves, Timeline/graph fails | Auxiliary exception becomes warning; apply record remains the primary durable evidence | Auxiliary audit is incomplete but no universal audit transaction exists |
| Mutation log fails | Warning is appended after the apply record save; persisted record may not contain the warning | Mutation log may not prove the event |
| Mutation succeeds, verification not opened | No automatic verification is required by apply primitive | Mutation can exist without verification decision |
| Rollback write fails after pre-backup | Failed rollback record retains pre-backup path if assigned; target may be partially changed | No atomic restore or automatic second recovery path |
| Verification opens against record | Gate binds record IDs and status, not an independent current file read | Verification can prove lifecycle record linkage, not exact bytes |

The current implementation provides useful records and backups but does not
provide transactionality between target mutation, apply record, mutation log,
Timeline, and verification. This is a security/correctness concern, not an
authorization to redesign the subsystem in M103A.

## 14. Security Findings

| Finding ID | Path | Severity | Current behavior | Producer | Consumer | Authority owner | Exact risk | Exploit / precondition | Current controls | Intentional? | Consumer proof | Disposition |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| M103A-F01 | Direct patch apply | HIGH | Direct route mutates after local proposal/status/optional queue checks without final gate, execution attempt, session/identity, freshness, or direct single-use | Proposal/status/review/queue and apply route | Target file, apply record, audit readers | Action-specific patch service; broader authorization intent NOT PROVEN | An old or cross-context approval/proposal can authorize a mutation outside the stronger final workflow | Possession of proposal ID and applicable queue approval; no caller binding | Approved status, critical path block, exact excerpt, backup, hashes, records | Separate action-specific path is documented; universal direct authorization is NOT PROVEN | STRONG: live target mutation and durable apply consumers | SEPARATE_SECURITY_REVIEW |
| M103A-F02 | Direct apply and final apply | HIGH | No reviewed-base hash or dry-run-to-final hash equality; current unique excerpt is sufficient | Proposal creation/review and current reader | Target mutation | Patch apply owner; review authority boundary incomplete | Stale-target or target-drift mutation after review | Unrelated target changes leave original excerpt exactly once | Current read, normalized path, exact-one excerpt, before/after hashes | NOT PROVEN | STRONG | SEPARATE_SECURITY_REVIEW |
| M103A-F03 | Rollback | HIGH | Rollback trusts successful apply record and backup path, not current target post-apply hash; no one-use/concurrency claim | Successful apply and rollback request | Restored target and rollback record | Action-specific rollback owner | A stale or replayed rollback can overwrite intervening legitimate content | Valid apply backup remains available and rollback caller can invoke route | Backup-root/path/size check, current read, hashes, pre-rollback backup, critical-path block | Action-specific restoration is coherent; stale restore policy NOT PROVEN | STRONG: restoration and review consumers | SEPARATE_SECURITY_REVIEW |
| M103A-F04 | Apply write and record boundary | HIGH | Target write occurs before apply record persistence; direct `write_text` is not atomic and failures do not automatically restore | Apply primitive | Target file, apply record, rollback eligibility | Patch executor and record stores | Partial/unrecorded mutation can leave target changed with failed or absent apply evidence and no normal rollback eligibility | I/O failure, process interruption, or persistence failure during/after write | Pre-write backup, failed record attempt, post-write hash on success path | NOT PROVEN | STRONG for target; incomplete for failure consumers | SEPARATE_SECURITY_REVIEW |
| M103A-F05 | Direct apply replay | MEDIUM | Queue approval is status-read, not consumed; no direct proposal execution claim | Legacy approval queue and apply route | Repeated apply requests | Legacy queue plus patch service | Same approval can be reused until content checks happen to block it | Repeated caller retains proposal ID and queue item stays approved | Current proposal status and excerpt check | Likely legacy/action-specific, but replay intent NOT PROVEN | STRONG | DOCUMENT_BOUNDARY |
| M103A-F06 | Final executor concurrency | MEDIUM | Gate-scoped prior-applied-record check is not atomic with lower-level mutation | Final gate/executor | Target and executor records | Final executor owner | Concurrent calls can pass readiness before either applied record is durable | Concurrent execution against same approved gate | Recheck statuses, prior-record check, apply excerpt check | Final path clearly intends one-use sequentially; concurrency guarantee ABSENT | STRONG | SEPARATE_SECURITY_REVIEW |
| M103A-F07 | Apply/verification/audit lifecycle | MEDIUM | Apply records attempt Timeline, graph, mutation log, and later human verification separately; no transactional audit or automatic verification | Apply/rollback and audit services | Human verifier, audit readers, workflow reports | Action evidence owners; verification does not authorize | Mutation may lack auxiliary audit or verification decision even while target changed | Auxiliary writer failure or no later verification submission | Primary apply/rollback records, warnings, backups | Human verification is intentionally separate; completeness boundary NOT PROVEN | STRONG | DOCUMENT_BOUNDARY |

Critical findings: `0`.

High findings: `4`.

Medium findings: `3`.

Low findings: `0`.

## 15. Observation and Verification Implications

Patch mutation already produces durable action-specific evidence:

- proposal, review, apply, rollback, gate, executor, and verification records;
- target path and proposal/apply/rollback identifiers;
- before/after or backup hashes at the relevant execution stage;
- backup and pre-rollback backup paths;
- mutation-log, Timeline, graph, and Working Memory attempts.

Post-apply verification can prove that a human reviewed a specific apply,
executor, or rollback record and can link that record to a proposal and target.
Rollback can prove which apply record supplied the backup through `apply_id`.

The evidence does not prove:

- that final apply used the exact bytes reviewed in dry-run;
- that the target was unchanged since review except for the excerpt check;
- that every auxiliary audit write succeeded;
- that a target mutation always has a durable apply record after interruption;
- that post-apply verification necessarily occurs;
- that verification independently re-reads and hashes the target.

Evidence is durable and action-specific, not a new common Observation lifecycle.
No current consumer justifies adding durable Observation persistence or a common
authority provenance record in M103A.

## 16. Build-Justification Gate

| Gate condition | M103A result |
|---|---|
| Real current production mutation consumer | SATISFIED: direct apply, final apply, and rollback mutate real targets |
| Concrete authority/security gap | SATISFIED: direct gate divergence, stale-base acceptance, replay/rollback gaps, and non-atomic failure windows |
| Can produce incorrect/unauthorized mutation, replay, drift, stale execution, or unverifiable mutation | SATISFIED as risk; exploit policy for direct bypass is not fully classified |
| Missing-boundary owner identifiable | PARTIALLY SATISFIED: patch Action owns execution; Core Governance/Coordination ownership for this path is not selected by current runtime |
| Smallest safe fix bounded | NOT SATISFIED: requires policy choice among strengthening, containment, or canonicalization, plus write/record atomicity decisions |
| Does not require Generic Act | SATISFIED |
| Does not require broad patch redesign | NOT PROVEN; safe failure and replay fixes may affect the patch lifecycle and rollback semantics |

Because the smallest safe owner and boundary are not yet selected, a future
Build is **NOT JUSTIFIED** by M103A. The findings justify a further policy and
security decision, not implementation.

## 17. Build Model Comparison

| Model | Description | M103A assessment |
|---|---|---|
| `MODEL_A_PATCH_EXECUTION_AUTHORITY_BINDING` | New immutable patch-specific execution-attempt binding derived from patch semantics | NOT SELECTED; owner, fields, and interaction with existing queue/final gate are not bounded |
| `MODEL_B_STRENGTHEN_EXISTING_PATCH_APPROVAL_CONSUMPTION` | Preserve action-specific model and strengthen exact binding, freshness, and single-use at existing seam | PLAUSIBLE but not bounded; could change approval reuse and direct-route behavior |
| `MODEL_C_ROUTE_CONTAINMENT` | Restrict or quarantine weaker direct mutation while preserving stronger workflow | PLAUSIBLE; requires an explicit policy decision that direct route is legacy or unsafe |
| `MODEL_D_CANONICALIZE_FINAL_REAL_APPLY` | Require every production real mutation to traverse final-real-apply | NOT PROVEN; current architecture exposes direct mutation as a live action-specific path |
| `MODEL_E_KEEP_CURRENT_PATCH_AUTHORITY_MODEL` | Treat current local model as coherent enough for no change | NOT SELECTED; concrete stale/failure/replay gaps remain |
| `MODEL_F_SECURITY_GAP_REAL_BUT_BUILD_BOUNDARY_NOT_READY` | Record real risk while deferring implementation until policy and owner are selected | SELECTED; best fit for current evidence |

## 18. Decision

Principal decision:

```text
B_REAL_PATCH_AUTHORITY_GAP_BUT_NO_BUILD_YET
```

Selected model:

```text
MODEL_F_SECURITY_GAP_REAL_BUT_BUILD_BOUNDARY_NOT_READY
```

The current patch authority is not declared universally unsafe. Its local
action-specific controls are real and valuable. The review does prove a real
security/correctness gap at the boundary between direct patch mutation,
final-real-apply, stale content, replay, rollback, and failure atomicity. A
safe Build cannot be selected until the human/project-manager decides whether
the direct route remains a legitimate compatibility model, becomes contained,
or must enter a stronger canonical gate, and which failure/replay semantics may
change.

No Build model is authorized. This is not `C_BOUNDED_PATCH_AUTHORITY_BUILD_JUSTIFIED`.
It is not `D_DIRECT_PATCH_PATH_CONTAINMENT_REVIEW_JUSTIFIED` or
`E_FINAL_REAL_APPLY_CANONICALIZATION_REVIEW_JUSTIFIED` because current evidence
does not choose either policy.

## 19. Smallest Future Build Boundary If Later Justified

M103A authorizes no future Build. If a later PM decision selects a Build, the
smallest defensible boundary must first choose one of these explicit scopes:

1. strengthen direct patch approval consumption and exact reviewed-base
   binding;
2. contain the direct route and preserve final-real-apply;
3. canonicalize final-real-apply for all real patch mutation; or
4. design a patch-specific transactional mutation/record boundary.

No single future boundary can be selected without deciding whether direct apply
is legacy compatibility, a legitimate separate trust model, or an unauthorized
bypass. Any later Build must derive fields from patch semantics, not restricted
read semantics, and must separately address proposal revision, content/base
binding, approval freshness, replay/concurrency, atomic write, durable apply
recording, rollback eligibility, and verification evidence.

## 20. Expected Future Build Files If Justified

None selected by M103A.

Any later PM-authorized Build must identify exact files first. It must not infer
that `RestrictedReadAuthorityBinding`, `RestrictedReadScope`, `read_only`,
`max_chars`, restricted-read fingerprints, or restricted-read approval fields
apply to patch mutation.

## 21. Forbidden Future Build Files and Behaviors

Without a new PM-authorized decision, do not modify:

- `aether/action/patch_apply.py`;
- `aether/action/patch_rollback.py`;
- `aether/action/final_real_apply_executor.py`;
- `aether/action/real_apply_approval_gate.py`;
- patch proposal/review/approval semantics;
- patch routes or API schemas;
- `RestrictedReadAuthorityBinding` or restricted-read runtime;
- Generic Act, shared Action authority, or a generic mutation registry;
- durable Observation or new verification persistence;
- `PROGRESS.md`, README, Constitution, or Architecture;
- existing tests, dependencies, runtime/private data, or routes.

Do not silently consume legacy approvals, make final-real-apply universal,
quarantine direct routes, add session identity, or add single-use semantics
under this review.

## 22. Authority Risks

- A legacy queue item can be mistaken for exact mutation authority even though
  it does not bind target, body, hash, session, identity, or attempt.
- A proposal `approved` status can be mistaken for proof that a patch review
  record exists.
- A unique current excerpt can be mistaken for proof that reviewed base content
  is unchanged.
- Final-real-apply's gate-scoped sequential check can be mistaken for an atomic
  universal single-use guarantee.
- A successful backup can be mistaken for a complete rollback transaction.
- A durable apply record can be mistaken for proof that every Timeline, graph,
  mutation-log, and verification consumer succeeded.
- A direct route can be treated as unauthorized solely because final-real-apply
  is stronger; the repository does not prove that policy.
- A future patch authority design could broaden authority by mechanically
  reusing restricted-read identity or approval fields.

## 23. Explicit Non-Goals

M103A does not:

- modify patch apply, patch rollback, or final-real-apply;
- modify approval semantics or approval stores;
- create a mutation authority binding;
- reuse `RestrictedReadAuthorityBinding`;
- quarantine routes;
- canonicalize final-real-apply;
- implement Generic Act or shared Action authority;
- add durable Observation, aggregation, Critic, Repair, Learning, retry,
  scheduler, background execution, or runtime loops;
- change routes, APIs, schemas, OpenAPI, `/chat`, or runtime/private data;
- modify `PROGRESS.md`, README, Constitution, Architecture, production code,
  or existing tests;
- commit, tag, push, or claim PM acceptance;
- begin M103B or M104.

## 24. Build Authorization Gate

```text
M103A review: COMPLETE LOCALLY
Principal decision: B_REAL_PATCH_AUTHORITY_GAP_BUT_NO_BUILD_YET
Selected model: MODEL_F_SECURITY_GAP_REAL_BUT_BUILD_BOUNDARY_NOT_READY
Future patch authority Build: NOT JUSTIFIED / NOT AUTHORIZED
Generic Act: NOT_IMPLEMENTED / NOT_AUTHORIZED / NOT_GRANTED
Durable Observation change: NOT AUTHORIZED
```

## 25. Next-Step Gate

```text
Next authorized action: HUMAN/PROJECT-MANAGER M103A SECURITY REVIEW
No patch runtime change is authorized.
No mutation authority binding is authorized.
No direct-route containment is authorized.
No final-real-apply canonicalization is authorized.
No M103B or M104 is authorized.
```

Control returns to the human/project-manager.
