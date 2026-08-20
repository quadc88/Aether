# Milestone 104A Patch Mutation Canonical Authority Decision Boundary

Classification: STRICT READ-ONLY ARCHITECTURE / SECURITY / AUTHORITY DECISION

Status: DECISION COMPLETE LOCALLY / NO CANONICAL MODEL PROVEN / NO BUILD

This record decides whether current patch mutation has a single canonical
authority model. It does not modify patch apply, patch rollback,
final-real-apply, approval semantics, routes, transactional behavior, or
runtime data. It does not implement Generic Act and does not select a future
successor Build.

## 1. Current Git State

Audit-start state:

- Branch: `main`.
- HEAD: `b36f95b7c7b05f4e1fb5624758c8b5d1f7bd3233`.
- Local `main`, `origin/main`, and remote `main` matched.
- Tracked worktree: clean.
- M103A: FINALIZED / COMMITTED / TAGGED / PUSHED / PM-ACCEPTED baseline.
- M103A decision: `B_REAL_PATCH_AUTHORITY_GAP_BUT_NO_BUILD_YET`.
- M103A selected model: `MODEL_F_SECURITY_GAP_REAL_BUT_BUILD_BOUNDARY_NOT_READY`.
- M103A findings: 0 CRITICAL, 4 HIGH, 3 MEDIUM.
- Full-suite baseline: `3177/3177 passed, 0 failures, 0 errors, 9 warnings`.
- OpenAPI baseline: `306 paths / 112 schemas`.
- `api_server` baseline: `8 direct @app routes / 23 include_router / 0 direct
  /action/*`.
- M104A creates only this design candidate, its static/document lock, and the
  external PM evidence summary.
- No production edit, existing-test edit, `PROGRESS.md` edit, dependency edit,
  runtime/private-data edit, commit, tag, or push is authorized by M104A.

Git verification at audit start:

```text
git status: clean
branch: main
HEAD: b36f95b7c7b05f4e1fb5624758c8b5d1f7bd3233
main: b36f95b7c7b05f4e1fb5624758c8b5d1f7bd3233
origin/main: b36f95b7c7b05f4e1fb5624758c8b5d1f7bd3233
remote main: b36f95b7c7b05f4e1fb5624758c8b5d1f7bd3233
git diff --check: CLEAN
```

## 2. M103A Durable Baseline

M103A proved that:

- direct patch apply real mutation is `YES`;
- final-real-apply is a stronger gate for its own workflow;
- direct mutation can bypass that stronger workflow;
- bypass classification is `C_LEGACY_PATH_PLUS_CANONICAL_STRONGER_PATH`;
- universal canonical mutation gate is `NOT YET PROVEN`;
- direct route unauthorized is `NOT PROVEN`;
- patch authority gap is `REAL`;
- findings are 0 CRITICAL, 4 HIGH, and 3 MEDIUM;
- future Build is `NOT JUSTIFIED`;
- Generic Act is `NOT_IMPLEMENTED / NOT_AUTHORIZED / NOT_GRANTED`.

M104A does not reopen or alter those findings. It asks whether the repository
now proves a canonical model that current patch mutation should converge toward.

## 3. Exact M104A Objective

Determine the authoritative execution model for current real patch mutation, if
the current production callers, trust purposes, approval lifecycle, mutation
correctness, rollback, verification, compatibility, and ownership prove one.

The decision must not be based on:

- implementation convenience;
- architectural aesthetics;
- the fact that final-real-apply has more checks;
- mechanical reuse of restricted-read semantics;
- tests or documentation without production caller proof.

The decision must distinguish a universal canonical gate from a stronger
workflow that serves only some high-risk or later-stage mutation cases.

## 4. Production Caller Inventory

| Caller / entry point | Production path | Consumer and intended use | Human-facing / internal | Compatibility status | Direct real mutation dependency |
|---|---|---|---|---|---|
| Patch route | `POST /action/patch-apply/apply` -> `patch_service.handle_patch_apply` -> `apply_patch_proposal` | Public action response, patch apply record, target file, audit readers | Human-facing API and route service | Live supported action-specific path; not marked deprecated | YES; request can set `dry_run=False` |
| Tool executor | `/action/tool-executor/execute` -> `tool_executor._safe_result` -> `file.patch_apply` | Tool execution result, execution log, Working Memory, Timeline, graph, mutation records | Tool-facing/internal action surface | Live tool registry capability; default payload dry-run is true but false is accepted | YES; payload `dry_run` is passed through |
| Self-modification route | `/action/self-modification/apply` -> `apply_self_modification_session` -> `apply_patch_proposal` | Self-modification session status/history, target file, apply and rollback records | Human-facing workflow route | Live approval-preserving workflow; not final-executor-only | YES after session review/dry-run state in the wrapper |
| Approved dry-run gate | Approved proposal/review -> `execute_approved_dry_run` -> `apply_patch_proposal(..., True)` | Dry-run record and human review input | Human-facing readiness workflow | Non-mutating readiness path | NO |
| Final approval gate | Accepted dry-run review -> `open_real_apply_approval_gate` | Final readiness record and new legacy queue item | Human-facing high-risk approval workflow | Later-stage stronger workflow | NO |
| Final-real-apply executor | Final executor routes -> `execute_final_real_apply` -> `apply_patch_proposal(..., False)` | Final executor record, target, apply/backup/audit records | Human-facing high-risk workflow | Live stronger wrapper around the same primitive | YES |
| Rollback route | `/action/patch-rollback/rollback` -> `rollback_patch_apply` | Restored target, rollback record, audit consumers | Human-facing action route | Separate restoration capability | YES when `dry_run=False` |
| Post-apply verification | Post-apply gate from direct apply, executor, or rollback | Human verifier, verification record, workflow/report readers | Human-facing evidence workflow | Evidence-only, not mutation authority | NO |

These are production code callers, not only tests. The direct primitive is
called by the patch service, tool executor, self-modification cycle, approved
dry-run gate, and final-real-apply executor. The direct patch route and
self-modification route are not documented as disabled or superseded by the
final executor.

The final executor has a distinct production consumer and a distinct route
family. It is not only a test wrapper. Its own policy says it performs one
explicit final real apply after readiness, while the direct route remains live.

## 5. Direct Patch Apply Intent Analysis

### 5.1 Evidence for supported production capability

Direct patch apply is exposed through a named patch route, a patch lifecycle
service, a tool registry entry, and a self-modification route. The proposal
module calls the operation an approved excerpt replacement with backup. The
self-modification cycle records proposal, review, dry-run, apply, and rollback
state. The route is part of the live API inventory, not a test-only helper.

The current direct path has real action-specific controls:

- proposal status must be `approved`;
- high-risk proposals can require a legacy queue item in `approved` state;
- critical identity/governance paths are blocked;
- target is read before apply;
- the original excerpt must occur exactly once;
- a backup is attempted before write;
- before/after hashes and apply records are created;
- Timeline, graph, Working Memory, and mutation-log evidence is attempted;
- rollback is available from a successful apply record;
- post-apply verification can consume the apply record.

This is not evidence of a safe universal authority contract. It is evidence that
direct mutation is a real supported production capability with its own local
trust model and consumers.

### 5.2 Intent classification

Direct patch intent is:

```text
A_SUPPORTED_PRODUCTION_MUTATION_CAPABILITY
with canonical trust role F_UNRESOLVED
```

It is not proven to be merely an accidentally exposed internal primitive. It is
not proven to be a deprecated transitional path. It is also not proven to be a
lower-trust model intentionally authorized to coexist with final-real-apply.
The repository shows support and use, but not a complete policy statement that
defines how its trust differs from the final workflow.

## 6. Final-Real-Apply Intent Analysis

### 6.1 Evidence for a stronger workflow

Final-real-apply requires an accepted dry-run review, completed dry-run,
approved proposal, final decision, a newly created legacy queue item approved
by a human, and a readiness refresh immediately before the lower-level apply.
It records an executor identity and prevents a prior sequential applied record
for the same gate from being reused. Its route family is explicitly named
`final-real-apply-executor`.

The final gate says it records readiness and does not apply directly. The final
executor says an explicit human execution may modify source files. Existing
repair-learning guidance says future high-risk self-modification should
preserve the full chain of proposal review, dry-run, dry-run review, final
approval, executor validation, rollback availability, post-apply verification,
and completion reporting.

### 6.2 Intent classification

Final-real-apply intent is:

```text
C_HUMAN_REVIEWED_HIGH_RISK_WORKFLOW
and D_LATER_STAGE_WRAPPER_AROUND_SHARED_PRIMITIVE
```

It is clearly a stronger workflow for high-risk or later-stage cases. It is not
proven to be the universal production mutation gate because:

- direct patch and self-modification routes remain live production callers;
- the final executor calls the same lower-level primitive rather than owning a
  distinct mutation implementation;
- no route or service contract says all real mutation must enter the final gate;
- no migration or deprecation record makes direct mutation compatibility-only.

Calling final-real-apply canonical solely because it has more checks would
exceed the evidence.

## 7. Authority Source-of-Truth Matrix

| Fact or record | Current authoritative source | Advisory / derived sources | Execution gate? | Verification-only? | Legacy / ambiguous role |
|---|---|---|---|---|---|
| Proposal identity | `patch_proposals.json` proposal `id` | Session, review, apply, gate records copy it | YES for local apply lookup | NO | No revision/version authority |
| Proposal status | Proposal record `status` | Review record status-after, session status | YES for apply and final executor | NO | Public status route can set lifecycle state |
| Proposal revision | None; revision console creates a new proposal ID | Revision console relation | NO | NO | Ambiguous because old proposals are not automatically invalidated |
| Review record | `patch_reviews.json` review record | Proposal status after review | NO for direct apply; YES for review workflow | NO | Direct apply does not require a review record |
| Approval record | Legacy `approval_queue.json` item for patch paths | Proposal `approval_id`, review status | Conditional direct gate; final executor gate | NO | Status-read, reusable, not exact patch authority |
| Individual approval store | Individual JSON approval record for restricted-read path | Restricted-read binding only | NO for patch mutation | NO | Separate capability store; not a patch source of truth |
| Dry-run result | Patch apply record plus approved dry-run gate | Dry-run review gate | YES for final workflow readiness | No | Derived readiness, not real mutation authorization alone |
| Dry-run review | Dry-run review gate decision | Final gate linkage | YES to open final gate | Review evidence | Human review, not direct execution authority |
| Final approval | Real-apply gate `final_decision` | Final executor readiness | YES for final workflow | NO | Only final workflow; not direct path authority |
| Final-ready state | Final executor record after readiness refresh | Gate, proposal, queue, dry-run records | YES for explicit executor call | NO | Gate-scoped and sequential-use check only |
| Target | Proposal target/normalized path, re-read by primitive | Apply, gate, executor, rollback copies | YES at execution | Verification copies it | Not bound to session/actor |
| Base content | Current content read at execution | Dry-run output does not persist full reviewed base | YES through excerpt check | Hash is evidence | Reviewed base is not authoritative |
| Base hash | None at proposal/review; apply computes current before hash | Apply record `original_hash_before` | Execution evidence, not stale-base gate | YES | Major ambiguity from M103A |
| Patch body | Proposal `proposed_excerpt` | Diff preview and patch text | YES as primitive input | Review presence | No body fingerprint |
| Patch/body hash | None | None | NO | NO | Absent |
| Backup | Apply record `backup_path` and backup file | Final executor rollback flag | YES for rollback eligibility | Evidence | No creation-time backup hash |
| Apply record | `patch_applies.json` apply record | Executor, mutation log, Timeline, graph | YES for rollback and post-apply gate | YES | Persisted after target write |
| Rollback record | `patch_rollbacks.json` rollback record | Post-apply verification and workflow reports | YES for rollback outcome | YES | No single-use/concurrency authority |
| Post-apply verification | Post-apply verification gate record | Reports and workflow completion | NO | YES | Human evidence, not authorization |

Conclusion: no single record is the source of truth for all real mutation
authority. Proposal, legacy approval, current content, final gate, executor,
apply, rollback, and verification records each own a narrower fact. A single
universal canonical mutation authority is **NOT PROVEN**.

## 8. Minimum Mutation Authority Semantics

These labels describe what a future canonical real-mutation model would need to
bind truthfully. They do not authorize a Build and do not import restricted-read
fields mechanically.

| Semantic | Minimum assessment | Evidence and qualification |
|---|---|---|
| Proposal identity | REQUIRED | Every real mutation must identify the exact proposal consumed |
| Proposal revision | REQUIRED if mutable revisions remain; otherwise NOT JUSTIFIED as a separate field | Current revision creates a new proposal ID but does not define invalidation |
| Exact target | REQUIRED | Target selection is mutation-critical |
| Normalized target | REQUIRED | Existing reader/apply/rollback records depend on it |
| Reviewed base content/hash | REQUIRED for a high-assurance canonical path | Current excerpt-only check does not prove reviewed-base equality |
| Patch body / proposed excerpt | REQUIRED | Exact replacement body must be the reviewed body |
| Patch fingerprint/hash | REQUIRED for high-assurance approval binding | Current system has no body hash; a future model must choose a truthful patch representation |
| Approval identity | REQUIRED | Approval must identify the approval consumed by the chosen path |
| Approval freshness | REQUIRED for high-risk/final authorization; OPTIONAL for a separately defined low-risk path | No universal TTL is currently proven |
| Session identity | REQUIRED when caller/session context is part of trust; NOT JUSTIFIED as universal without caller policy | Current direct callers do not share one session contract |
| Actor/identity | REQUIRED for human-accountable high-risk mutation; NOT JUSTIFIED as a universal field yet | Current patch records do not bind actor identity |
| Execution-attempt identity | REQUIRED for any single-use high-assurance path | Final executor ID is not a universal execution attempt |
| Single-use claim | REQUIRED for final/high-risk authority; OPTIONAL only if a separate replay policy is explicitly accepted | Direct path has none; final check is not atomic |
| Dry-run result | REQUIRED for final/high-risk workflow; OPTIONAL for direct lower-risk path if preserved | Existing final chain consumes it |
| Dry-run review | REQUIRED for final/high-risk workflow; NOT JUSTIFIED for every direct apply without a policy decision | Existing direct path does not require it |
| Final approval | REQUIRED for final/high-risk workflow; NOT JUSTIFIED as universal until direct intent is resolved | Final gate owns this fact |
| Backup identity | REQUIRED for every real mutation | Rollback needs an exact backup relationship |
| Pre-write target hash | REQUIRED | Existing apply computes it at execution; future high-assurance review may need it earlier |
| Post-write target hash | REQUIRED | Existing apply computes it after successful write |
| Verification provenance | REQUIRED as durable linkage for high-risk mutation; not itself execution authority | Existing post-apply gate binds record IDs but not exact bytes |

The minimum is conditional because current production callers express more than
one trust workflow. Selecting a universal tuple now would either silently
invalidate direct callers or under-specify high-risk final callers.

## 9. M103A Finding-to-Model Mapping

M103A findings:

- `F01` HIGH: direct mutation lacks final gate, attempt, session/identity,
  freshness, and direct single-use.
- `F02` HIGH: reviewed-base hash and dry-run-to-final equality are absent.
- `F03` HIGH: rollback lacks current post-apply binding and single-use/concurrency
  protection.
- `F04` HIGH: target write and durable apply recording are not atomic.
- `F05` MEDIUM: direct approval is status-read and reusable.
- `F06` MEDIUM: final executor prior-use check is not atomic against concurrent
  execution.
- `F07` MEDIUM: audit and verification are separate, non-transactional evidence
  stages.

| Model | Findings addressed | Findings remaining | Behavior / migration risk | Ownership effect | M104A result |
|---|---|---|---|---|---|
| `MODEL_A_STRENGTHEN_DIRECT_PATCH_APPROVAL_CONSUMPTION` | Could address parts of F01, F02, and F05 through exact approval/proposal/base binding; could add direct attempt/use semantics | F03, F04, F06, F07 unless separately expanded | Changes direct callers and approval replay behavior; stored records and review flow need compatibility rules | Keeps patch Action owner but creates a stronger direct boundary | Plausible future review; not selected |
| `MODEL_B_CONTAIN_DIRECT_PATCH_REAL_MUTATION` | Addresses the direct portion of F01 and F05 by removing direct real mutation | F02 in final primitive, F03, F04, F06, F07 | Breaks or changes public patch/self-modification callers; route policy and compatibility migration required | Moves real mutation ownership toward final executor | Not proven tolerable |
| `MODEL_C_CANONICALIZE_FINAL_REAL_APPLY` | Addresses direct bypass aspect of F01 and F05 for migrated callers | F02, F03, F04, F06, F07 remain in shared primitive/workflows | Requires caller migration, approval/readiness migration, route behavior change, and deprecation policy | Makes final executor the universal owner without current authority proof | Not proven |
| `MODEL_D_TRANSACTIONAL_PATCH_MUTATION_RECORD_BOUNDARY` | Addresses F04 and portions of F07 | F01, F02, F03, F05, F06 remain | Adds mutation/record behavior without resolving authority ownership | Keeps existing owners but adds a new atomicity owner | Separate axis, not first decision |
| `MODEL_E_LAYERED_DUAL_TRUST_MODEL` | Resolves the question of whether final is universal by documenting distinct trust purposes; does not technically remove F01-F07 | All substantive replay, base, rollback, atomicity, and audit gaps remain | Lowest immediate caller/migration risk, but requires explicit trust policy and does not erase security gaps | Preserves separate Action and final-workflow owners | Not proven because intentional non-conflict is not explicit enough |
| `MODEL_F_NO_CANONICAL_AUTHORITY_DECISION_YET` | Resolves no runtime finding; preserves all evidence and prevents an unsupported convergence claim | F01-F07 remain for a later bounded decision | No behavior, API, route, record, or migration impact | Preserves current owners while PM decides policy | SELECTED; evidence is insufficient for a canonical model |

M104A selects no model that silently treats the M103A findings as fixed. The
decision boundary itself is the smallest safe result.

## 10. Atomicity as a Separate Axis

Authority and atomicity are related but not identical:

- The authority decision can be made without implementing atomicity. A future
  policy can identify who may authorize mutation before deciding how target,
  backup, apply record, and audit writes become transactional.
- Atomicity can be improved without selecting a universal authority model. A
  patch-specific write/record seam could preserve current entry points while
  changing failure behavior, but that would be a separate design decision.
- Atomicity is **NOT REQUIRED IN THE FIRST BUILD** because M104A selects no
  canonical model and no Build is ready.
- If later selected, atomicity requires its own bounded milestone or an explicit
  proof that the chosen authority boundary cannot be truthful without it.

No transactional mutation behavior is added by M104A.

## 11. Rollback as a Separate Axis

Rollback should remain action-specific and separate from restricted-read
authority. Current evidence does not prove that rollback should share the same
execution approval as either direct apply or final-real-apply.

Current disposition:

- rollback authorization remains owned by the action-specific rollback path;
- no new approval requirement is selected;
- no universal single-use claim is selected;
- current post-apply hash binding is a real future concern but not redesigned;
- session/identity binding is not added;
- backup/apply/rollback relationships remain current behavior;
- rollback redesign is not required to decide the canonical authority model.

A future model that changes real mutation authority must separately prove how it
preserves rollback eligibility and prevents stale restoration. M104A does not
redesign rollback.

## 12. Compatibility and Migration Analysis

| Concern | A strengthen direct | B contain direct | C canonical final | D transactional boundary | E layered dual trust | F no decision |
|---|---|---|---|---|---|---|
| Existing direct route | Changes checks and replay behavior | Real mutation may stop | Must migrate or deprecate | Preserved with changed failure behavior | Preserved | Preserved |
| Tool executor | Payload and approval semantics change | Real apply tool may break | Must route through final readiness | Preserved | Preserved | Preserved |
| Self-modification | Session wrapper semantics change | Direct apply stage breaks | Must migrate workflow | Preserved with new failure semantics | Preserved | Preserved |
| Final executor | Could remain separate | Becomes more central | Becomes universal | Shares lower-level seam | Remains stronger workflow | Remains stronger workflow |
| API behavior | Possible response/status changes | Route capability changes | Route migration/deprecation | Failure timing may change | No immediate change | No immediate change |
| Approval migration | Possible binding/replay migration | Final queue becomes required | Direct approvals migrate to final records | None necessarily | None immediately | None |
| Stored records | New fields or compatibility readers | Existing direct records need interpretation | Existing direct records need migration policy | Atomic record schema concerns | No changes | No changes |
| Rollback | Must preserve old apply records | Must preserve old direct records | Must preserve both old and final records | Failure behavior changes | No immediate change | No immediate change |
| Operational rollback | Code rollback possible but policy migration risk | Route rollback risk | Migration rollback risk | Atomicity rollback complexity | Low | Lowest |

No candidate currently satisfies a safe, bounded, behavior-preserving first Build
without a prior policy decision. Model F has the smallest immediate change:
none.

## 13. Canonical Authority Decision Gate

| Requirement | Result | Evidence |
|---|---|---|
| Production consumer proven | YES | Direct, self-modification, tool, and final callers are live |
| Trust model clear | NO | Direct and final purposes are distinguishable but universal relationship is not explicit |
| Authority ownership identifiable | PARTIAL | Action services own local paths; no common patch authority owner is proven |
| Resolves at least one HIGH M103A finding | NO for a safe implementation model; Model E only classifies ambiguity | No selected model changes F01-F04 |
| Does not silently invalidate legitimate callers | YES for Model F | No runtime behavior changes |
| First Build can be bounded | NO | Policy, owner, and migration choices remain open |
| Does not require Generic Act | YES | No Generic Act dependency is needed |
| Preserves failure-closed behavior | YES for no-change decision | Existing behavior remains untouched |

The gate fails for selecting a canonical implementation model. The correct
decision is `D_NO_CANONICAL_MODEL_PROVEN`.

## 14. Model Comparison and Selected Principal Model

Selected principal model:

```text
MODEL_F_NO_CANONICAL_AUTHORITY_DECISION_YET
```

Build-readiness decision:

```text
D_NO_CANONICAL_MODEL_PROVEN
```

This is not a finding that the patch system has no authority. It is a finding
that current evidence proves multiple real callers and a stronger workflow but
does not prove the policy relationship required to make one authority model
canonical. The direct route cannot be called invalid; final-real-apply cannot be
called universal; and a dual-trust model cannot be asserted as intentional and
non-conflicting without a new authority decision.

## 15. Smallest Future Build Boundary If Later Justified

M104A authorizes no Build.

The smallest future Build boundary cannot be selected until a new PM-authorized
decision chooses one coherent subject:

- exact direct approval-to-patch binding;
- reviewed-base hash binding;
- direct single-use/execution-attempt binding;
- direct-route containment;
- final-real-apply canonical routing; or
- transactional apply-record boundary.

These are alternatives, not a combined scope. A later decision must identify the
one selected owner, callers, record compatibility rule, rollback behavior,
failure behavior, and exact files before implementation.

## 16. Expected Future Build Files

None selected by M104A.

No future file may be inferred from this record. In particular, M104A does not
authorize changes to patch apply, patch rollback, final-real-apply, approval
stores, routes, or restricted-read authority.

## 17. Forbidden Future Build Files and Behaviors

Without a new PM-authorized decision, do not modify:

- `aether/action/patch_proposal.py`;
- `aether/action/patch_review.py`;
- `aether/action/patch_apply.py`;
- `aether/action/patch_rollback.py`;
- `aether/action/real_apply_approval_gate.py`;
- `aether/action/final_real_apply_executor.py`;
- `aether/action/approval_queue.py`;
- patch routes, self-modification routes, or API schemas;
- `RestrictedReadAuthorityBinding` or restricted-read runtime;
- `PROGRESS.md`, README, Constitution, or Architecture;
- existing tests, dependencies, runtime/private data, or stored records.

Do not strengthen approvals, quarantine direct routes, canonicalize
final-real-apply, add transactional mutation behavior, redesign rollback, or
introduce Generic Act under M104A.

## 18. Authority Ownership

Current ownership remains split and must not be collapsed:

| Concern | Current owner | M104A conclusion |
|---|---|---|
| Policy decision | Human/project-manager plus existing action-specific policy inputs | No universal patch policy owner is proven |
| Approval decision | Human through legacy queue, patch review, and final gate workflows | Different approval stores remain distinct |
| Execution authorization | Direct patch service checks or final gate/executor chain | No common patch execution authority is proven |
| Approval consumption | Direct path reads legacy queue status; final executor reads final queue status; restricted-read has separate atomic claim | No patch-wide consumption owner is proven |
| Mutation dispatch | Patch service / tool executor / final executor wrappers | Shared lower-level primitive is not a shared authority |
| Mutation primitive | `aether.action.patch_apply.apply_patch_proposal` | Preserve; no modification |
| Backup creation | `patch_apply.create_backup` | Action-specific owner; preserve |
| Apply recording | `patch_apply` record store plus auxiliary audit services | Durable record is not transactional authority |
| Verification | Post-apply verification gate and human verifier | Evidence-only; does not authorize |
| Rollback authorization | `patch_rollback.rollback_patch_apply` eligibility checks | Separate action-specific owner; preserve |

## 19. Behavior, API, Route, and Rollback Impact

- Behavior change: NONE.
- API impact: NONE.
- Route impact: NONE.
- Approval migration: NONE.
- Stored-record migration: NONE.
- Rollback path: unchanged and preserved as action-specific.
- Operational rollback: remove the two local evidence files; no runtime/data
  rollback is needed.

## 20. Explicit Non-Goals

M104A does not:

- implement patch runtime changes;
- modify patch apply, patch rollback, or final-real-apply;
- disable, quarantine, or migrate direct patch routes;
- change approval semantics or approval stores;
- add transactional mutation behavior;
- redesign rollback;
- implement Generic Act, generic mutation authority, generic capability
  registry, shared action binding, generic dispatch, or generic verification;
- generalize M101B beyond `file.restricted_read`;
- add durable Observation or new verification persistence;
- change routes, APIs, schemas, `/chat`, or runtime/private data;
- modify `PROGRESS.md`, README, Constitution, Architecture, production code,
  or existing tests;
- commit, tag, push, or claim PM acceptance;
- begin M104B or M105.

## 21. Build Authorization Gate

```text
M104A decision review: COMPLETE LOCALLY
Canonical mutation authority proven: NO
Selected principal model: MODEL_F_NO_CANONICAL_AUTHORITY_DECISION_YET
Build-readiness decision: D_NO_CANONICAL_MODEL_PROVEN
Future patch authority Build: NOT JUSTIFIED / NOT AUTHORIZED
Generic Act: NOT_IMPLEMENTED / NOT_AUTHORIZED / NOT_GRANTED
```

## 22. Next-Step Gate

```text
Next authorized action: HUMAN/PROJECT-MANAGER M104A AUTHORITY DECISION REVIEW
No canonical patch authority model is selected for implementation.
No patch runtime change is authorized.
No approval strengthening is authorized.
No direct-route containment is authorized.
No final-real-apply canonicalization is authorized.
No transactional mutation behavior is authorized.
No M104B or M105 is authorized.
```

Control returns to the human/project-manager.
