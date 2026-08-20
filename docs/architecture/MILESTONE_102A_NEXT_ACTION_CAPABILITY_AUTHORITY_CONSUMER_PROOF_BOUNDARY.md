# Milestone 102A Next Action Capability Authority Consumer-Proof Boundary

Classification: STRICT READ-ONLY DISCOVERY / CONSUMER-PROOF BOUNDARY

Status: DISCOVERY COMPLETE LOCALLY / NO SECOND CAPABILITY BUILD JUSTIFIED

This record asks whether a second current production Action capability already
has a real authority-binding consumer need. It does not implement a second
binding, generalize `RestrictedReadAuthorityBinding`, modify production code,
or authorize a successor Build.

## 1. Current Git State

- Branch: `main`.
- HEAD: `6a30f34b829dfd645db2f8e2a1543d794d36f4c0`.
- Local `main`, `origin/main`, and remote `main` match.
- Tracked worktree: clean at audit start.
- M101B: FINALIZED / COMMITTED / TAGGED / PUSHED.
- M102A creates only this design candidate and its static/document lock as
  local untracked evidence.
- No `PROGRESS.md` change, production change, commit, tag, or push is
  authorized by M102A.

## 2. M101B Durable Baseline

- Full-suite baseline: `3168/3168 passed, 0 failures, 0 errors, 9 warnings`.
- OpenAPI: `306 paths / 112 schemas`.
- `api_server`: `8 direct @app routes / 23 include_router / 0 direct /action/*`.
- Current capability-specific binding: `file.restricted_read`.
- Implementation: `RestrictedReadAuthorityBinding`.
- Generic Act: `NOT_IMPLEMENTED`.
- Generic Act integration: `NOT_AUTHORIZED`.
- Generic Act authority: `NOT_GRANTED`.

M101B is a capability-specific reference, not a mandate to duplicate its
fields or contract for another path.

## 3. Exact M102A Objective

Determine whether any current production capability, other than the already
bound `file.restricted_read`, has both:

1. a real producer and real consumer using the capability today;
2. a concrete authority-binding ambiguity affecting that current behavior;
3. truthful capability-specific semantics that a bounded immutable contract can
   bind without changing legitimate behavior or broadening authority.

The question is not which capability would be convenient to bind next. A real
consumer must already depend on the authority-bearing path.

## 4. M101B Reference Semantics

`RestrictedReadAuthorityBinding` is useful evidence because it binds existing
facts without creating authority:

- capability identity `file.restricted_read`;
- execution-attempt identity;
- existing session identity;
- existing approval identity and restricted-read fingerprint;
- normalized target;
- `read_only` permission;
- existing `max_chars` bound;
- the existing Governance-minted `RestrictedReadScope`.

The service is immutable and only validates evidence. It does not decide
policy, claim approval, dispatch, read, create Observation, verify, or create
Generic Act semantics. The M101B current path remains:

```text
exact request and approval binding
  -> fresh Perception, Risk, Identity, and Thinking evidence
  -> Core Governance decision and RestrictedReadScope
  -> RestrictedReadAuthorityBinding validation
  -> atomic approval claim
  -> scope-bound bridge dispatch
  -> governed reader and call-local Observation
  -> immediate restricted-read verification
```

No candidate is assumed to have the same session, approval, target,
fingerprint, scope, freshness, privacy, or single-use semantics.

## 5. Active Capability Inventory

Only current production paths were audited:

- direct file read;
- tool planner and tool executor, including sandbox `file.restricted_read`;
- patch apply;
- patch rollback;
- approved dry-run and dry-run review;
- real-apply approval gate;
- final-real-apply executor;
- post-apply verification.

The canonical governed restricted-read path was used as the existing reference
and was not counted as a second candidate.

## 6. Producer and Consumer Matrix

| Capability/path | Production entry point | Real producer | Real consumer | Current authority model | Current binding and freshness | Evidence, failure, and value |
|---|---|---|---|---|---|---|
| Direct file read | `/action/file/read` -> `file_service.py:86-89` -> `read_restricted_file` | Route request and direct reader produce a file-access record | Endpoint response, file-access audit, status/list consumers, Working Memory/Timeline/graph integrations | `LEGACY_COMPATIBILITY_EXECUTION`; direct reader `ALLOWED_ROOTS` | Direct mode has normalized path, sensitive-path, extension, size, and existence checks. No Core Governance decision, approval claim, execution-attempt binding, session binding, freshness recheck, or single-use claim | Blocks invalid, sensitive, outside-root, missing, non-file, disallowed-extension, oversized, and read-error paths. It has real user-visible read value but intentionally different trust semantics from governed read |
| Tool planner | Planning service used by tool executor | Text/tool request, Tool Registry, and risk planner produce a persisted plan and optional legacy approval item | `execute_tool`, plan/list/status consumers, operators | `NON_EXECUTING_PLANNING_PATH` | Risk, tool policy, approval recommendation, and `allow_auto_execute` are recorded. It does not dispatch or establish execution authority | No tool, disabled tool, and approval-required paths do not execute. Planning is not a current Action consumer |
| Tool executor, including sandbox `file.restricted_read` | `/action/tool-executor/execute` -> `tool_execution_service.py:115-177` -> `tool_executor.py:332-403` | Tool request, planner, registry, and `_safe_result` produce execution record/result | Caller response, execution log, Working Memory, Timeline, graph, and optional file audit | `LEGACY_COMPATIBILITY_EXECUTION` for restricted read; local sandbox execution for other tools | Accepts arbitrary `tool_id` and `input_payload`; approval may be required, but there is no canonical target/session/identity binding, execution freshness recheck, or universal claim. Restricted read calls direct reader mode at `tool_executor.py:199-204` | Tool disabled, blocked sandbox, approval-required, and tool error paths fail closed locally. This is a real route consumer, but its restricted-read branch overlaps the existing capability rather than proving a second capability |
| Patch apply | `/action/patch-apply/apply` -> `patch_service.py` -> `patch_apply.py:31-56` | Approved patch proposal, optional legacy approval item, target content, and request `dry_run` produce an apply record | Target file mutation when `dry_run=False`, patch-apply record, mutation log, Timeline, graph, and later verification readers | `ACTION_SPECIFIC_GOVERNED_EXECUTION` | Binds proposal ID, stored normalized target, proposal status, optional approval item, exact original excerpt, current content, before/after hashes, and backup. No canonical execution attempt, session, identity, or universal single-use claim | Missing/unapproved/critical/ambiguous/read/write failures block or fail. It has strong mutation value and a real consumer, but its proposal/excerpt/hash/backup model is not equivalent to M101B |
| Patch rollback | `/action/patch-rollback/rollback` -> `patch_service.py` -> `patch_rollback.py:31-52` | Successful applied record and backup produce a rollback record | Target restoration, rollback record, mutation log, Timeline, graph, and post-apply review | `ACTION_SPECIFIC_GOVERNED_EXECUTION` | Binds apply ID, successful status, backup path under backup root, current/backup/after hashes, and pre-rollback backup. No approval record, session, identity, or generic execution claim | Missing/ineligible apply, invalid backup, critical target, hash, and write failures block or fail. Restoration semantics are coherent and distinct from read authority |
| Approved dry-run and dry-run review | `/approvals/{id}/dry-run-request`, dry-run gates, and review routes | Approved proposal/review records produce a dry-run record and human review decision | Later real-apply approval gate and human operator consume readiness/review records | `NON_EXECUTING_PLANNING_PATH` until a later action-specific gate | `dry_run=True` is hard-coded; execution, apply, and rollback permissions remain false. Records bind proposal/review/apply IDs but do not dispatch | Invalid, repeated, incomplete, or non-dry-run records fail closed. There is no current execution consumer at this layer |
| Real-apply approval gate | Real-apply gate routes and `real_apply_approval_gate.py:149-206` | Accepted dry-run review and completed dry-run produce a final approval readiness record and legacy approval item | Final-real-apply executor consumes gate, proposal, dry-run, and queue readiness | `ACTION_SPECIFIC_GOVERNED_EXECUTION` | Binds gate ID, proposal ID, patch review, dry-run apply, final decision, approval item, and sanitized target. No session or identity binding | Gate refuses incomplete chain and never directly applies. It has a real executor consumer and an explicit action-specific lifecycle |
| Final-real-apply | Final executor routes -> `final_real_apply_executor.py:92-116,181-201` | Gate, approved proposal, approved queue item, completed dry-run, and executor record produce real apply result | Target file mutation, apply/backup/rollback records, mutation log, Timeline, graph, and post-apply verifier | `ACTION_SPECIFIC_GOVERNED_EXECUTION` | Revalidates gate status, decision, proposal, queue status, dry-run status, and prior applied record. Gate-scoped one-use is enforced by `_has_applied_record`; target comes from approved proposal | Not-ready, repeated, missing, and failed conditions block. It has the strongest current mutation gate and a real consumer; no missing M101B-like contract is proven |
| Post-apply verification | Post-apply verification routes and `post_apply_verification_gate.py:63-101` | Completed real apply or rollback produces a verification-ready record | Human verifier consumes apply/rollback status and submits a verification decision | `EVIDENCE_ONLY` / action-specific human gate | Binds source record, proposal, apply/rollback IDs, target, status, backup/rollback facts, and human decision. It does not execute | Missing or invalid source/decision blocks. It is a verifier consumer, not an execution-authority consumer |

## 7. Authority Ownership Matrix

| Concern | Direct read | Tool path | Patch/final path | M102A finding |
|---|---|---|---|---|
| Authorization decision | Direct reader/path checks | Tool Registry/planner local decision | Proposal/review/legacy approval and final gate | No second path shares the full Core Governance ownership structure of M101B |
| Approval owner/consumer | None | Optional legacy approval item | Legacy queue for direct patch/final chain; proposal/review records | Approval semantics are materially different, so reuse is not truthful |
| Dispatch/execution owner | `read_restricted_file` direct mode | `tool_executor._safe_result` | `patch_apply`, `patch_rollback`, final executor | Each path owns action-specific dispatch; no common owner is proven |
| Freshness | Current direct file checks only | Plan-time risk and local execution record | Current proposal/dry-run/readiness rechecks | No shared freshness contract exists |
| Single use | None | No universal claim | Final executor gate-scoped prior-apply check; rollback eligibility | M101B atomic claim cannot be reused without changing semantics |
| Privacy/safety | Direct roots/path checks | Tool-local payload and reader behavior | Critical path blocks, hashes, backups, metadata filtering | Different safety contracts are intentional/action-specific |
| Verification/evidence | File access audit | Execution log/audit | Apply/rollback records and post-apply human gate | No new verifier requires a common binding provenance |

## 8. Direct File Analysis

Direct file read is a real production route and has a real response/audit
consumer. It relies on `read_restricted_file` default direct mode and the
independent `ALLOWED_ROOTS` contract. It does not use the canonical governed
approved-root configuration, approval record, session binding, or call-local
restricted-read verifier.

This overlap is with the same underlying file-read capability, not a second
capability. The direct route may intentionally serve compatibility behavior;
forcing it through canonical restricted-read authority would change its trust,
privacy, approval, and response semantics. The correct current outcome is:

```text
KEEP_SEPARATE
LEGACY_QUARANTINE_JUSTIFIED
REQUIRES_SEPARATE_SECURITY_REVIEW
```

No M102A binding is justified for it.

## 9. Tool Executor Analysis

The tool executor is a real production route and consumes tool plans, but it is
not one capability. It accepts arbitrary tool IDs and payloads, persists a plan
and execution record, and dispatches several unrelated tools. Its
`file.restricted_read` branch calls the existing reader in direct mode, so it
duplicates an already-bound capability through a legacy compatibility path.

The planner is not an execution authority: it creates plans and may create
legacy approval items, while the executor owns local sandbox dispatch. M101B
does not create an opportunity to safely reuse the restricted-read binding
without first changing the tool executor's capability and approval model. That
would be a migration or generic-action expansion, not a second capability
binding.

Outcome: `KEEP_SEPARATE_LEGACY_MODEL`; no tool-executor binding Build.

## 10. Patch Apply Analysis

Patch apply is the highest-ranked reviewed candidate because it has a real
production mutation consumer and high safety value. The direct route can invoke
`apply_patch_proposal(..., dry_run=False)` after proposal approval, optional
legacy queue approval, target checks, excerpt uniqueness, hashes, and backup.

The concrete authority concern is real: direct patch apply is not required to
traverse the stronger final-real-apply gate, and it has no universal
execution-attempt, session, identity, or single-use contract. However, the
current action-specific semantics are internally meaningful: proposal status,
target/excerpt binding, current-content check, hashes, backup, mutation record,
and rollback relationship are the facts its current consumer uses.

A second M101B-style binding would not solve this without deciding whether to
change direct patch behavior, migrate it to final-real-apply, or define a new
patch authority lifecycle. Each option carries high behavior-change and
rollback risk. The current evidence supports a separate security review, not a
second capability-binding Build.

Outcome: `KEEP_CURRENT_ACTION_SPECIFIC_MODEL`; defer any patch authority work.

## 11. Patch Rollback Analysis

Rollback has a real restoration consumer, but its authority is the successful
apply record and backup eligibility. Its current target, backup-root, hash,
pre-rollback-backup, and `dry_run` semantics are coherent for restoration. It
does not share restricted-read approval, privacy, or scope semantics.

Outcome: `KEEP_CURRENT_ACTION_SPECIFIC_MODEL`; no binding adoption justified.

## 12. Final-Real-Apply Analysis

Final-real-apply has the strongest action-specific gate among mutation paths.
The executor refreshes gate, proposal, legacy queue, completed dry-run, and
prior-application state immediately before applying. The gate binds the
proposal/dry-run/review/final-decision chain and creates a final approval item.
The executor has a real mutation consumer and post-apply verifier.

Its remaining absence of session or identity fields is not proof that the
current lifecycle is incoherent. Adding restricted-read-style binding would
weaken or replace a distinct mutation authority model. Preserve it and require
a separate security review for any future change.

Outcome: `KEEP_CURRENT_ACTION_SPECIFIC_MODEL`.

## 13. Dry-Run and Real-Apply Transition Analysis

Dry-run is explicitly non-executing. It calls patch apply with `dry_run=True`,
records the result, and requires human review before the real-apply gate. The
real-apply gate then creates a separate legacy approval item and final decision;
the executor revalidates all readiness records before mutation.

This is a real producer/consumer chain, but the dry-run layer is not an
execution-capability consumer. It does not justify an immutable authority
binding, and the transition records are not equivalent to M101B's governed
restricted-read scope.

Outcome: `DEFER`; preserve the current action-specific chain.

## 14. Candidate Ranking

| Candidate ID | Capability/path | Production consumer proof | Exact authority-binding gap | Current owner model | Safety impact | Behavior-change risk | Implementation scope | Similarity to M101B | Recommendation |
|---|---|---|---|---|---|---|---|---|---|
| CAND-01 | Patch apply direct mutation | STRONG: target file, apply record, mutation/audit readers | Direct apply can bypass final-real-apply readiness and lacks universal attempt/session/identity binding | Action-specific proposal/approval/apply owner | HIGH | HIGH | Large separate security review | Superficial: mutation proposal/hash/backup semantics differ | `KEEP_CURRENT_ACTION_SPECIFIC_MODEL` |
| CAND-02 | Final-real-apply executor | STRONG: real patch mutation and post-apply verifier | No new missing binding is proven; gate/proposal/dry-run/queue chain is explicit and revalidated | Action-specific final gate/executor owner | HIGH | HIGH | Large and tightly gated | Superficial: distinct mutation lifecycle | `KEEP_CURRENT_ACTION_SPECIFIC_MODEL` |
| CAND-03 | Direct file read | STRONG: endpoint response and file-access audit | No canonical approval/attempt binding, but this is an intentional direct compatibility contract and the same file capability | Direct reader/interface compatibility owner | MEDIUM-HIGH | HIGH | Route/security migration | Same underlying file capability, not a second capability | `KEEP_SEPARATE_LEGACY_MODEL` |
| CAND-04 | Tool executor restricted-read branch | STRONG: execution result/log/audit | Direct-mode duplicate of `file.restricted_read` with arbitrary payload; no second capability semantics | Tool planner/registry/executor | HIGH | HIGH | Tool capability migration | Superficial and overlapping, not a second capability | `KEEP_SEPARATE_LEGACY_MODEL` |
| CAND-05 | Patch rollback | STRONG: restored target and rollback/audit readers | No universal claim, but backup/apply/hash eligibility is coherent for restoration | Action-specific rollback owner | HIGH | HIGH | Separate restoration review | Superficial: restoration differs from read authorization | `KEEP_CURRENT_ACTION_SPECIFIC_MODEL` |
| CAND-06 | Dry-run/review transition | No executing consumer at dry-run layer; later gate consumes readiness | It records non-execution readiness, not a missing execution binding | Action-specific gate owners | MEDIUM | HIGH | Gate redesign | Not comparable to M101B | `DEFER` |

Number of qualifying real second-capability candidates: `0`.

The highest-ranked reviewed path is `CAND-01`, but it is not selected as a
second capability Build. It has strong producer/consumer proof and a real
authority concern, yet its current action-specific model does not establish a
safe, bounded, behavior-preserving M101B-style contract.

## 15. Selected Capability and Decision

Selected capability:

```text
NONE
```

Decision:

```text
D_NO_SECOND_CAPABILITY_CURRENTLY_JUSTIFIED
```

Selected model:

```text
MODEL_E_NO_SECOND_BUILD_YET
```

No second capability currently proves both a need for and truthful semantics
for a new explicit authority-binding contract. This is not a finding that the
other paths have no authority risks. It is a finding that those risks are
either compatibility overlap with `file.restricted_read`, coherent
action-specific lifecycles, or broad migration problems that cannot be safely
solved by a small second binding.

## 16. Generic Abstraction Gate

Generic abstraction pressure: `NOT PROVEN`.

M101B plus the reviewed paths do not prove two capabilities with materially
equivalent:

- authority decision ownership;
- approval-consumption semantics;
- freshness semantics;
- execution-attempt binding needs;
- single-use behavior;
- privacy/safety rules;
- failure-closed behavior;
- current consumer requirements.

The repository has multiple real Action consumers, but code reuse or shared
route exposure is not semantic equivalence. No generic authority registry,
Generic Act, or shared Action abstraction is authorized or implemented.

## 17. Observation and Verification Implications

M101B created no new production evidence consumer pressure:

- the new binding validates existing evidence before the same restricted-read
  execution and does not create a new Observation;
- the call-local restricted-read Observation remains immediately consumed by
  its existing verifier;
- patch and final-real-apply verifiers continue to consume action records and
  human decisions, not a new common Observation contract;
- no current consumer requires durable Observation or authority provenance from
  another capability.

Decision: no durable Observation reopening and no second evidence-binding Build.

## 18. Smallest Possible Future Build Boundary

M102A selects no capability, so it defines no authorized future Build files.
The smallest defensible next action for the closest candidate is a separate
read-only patch authority/security review that first decides whether direct
patch apply remains compatible, is quarantined, or must enter the final gate.
That review must not reuse `RestrictedReadAuthorityBinding` mechanically and
must not modify production code under M102A.

No future Build may be inferred from this record. Any later patch or tool work
requires a new capability-specific decision with its own truthful fields and
consumer proof.

## 19. Files and Runtime Boundary

M102A authorizes only these two untracked candidates:

- this design record;
- its static/document-contract test.

No future Build file is selected. The following remain forbidden without a new
decision:

- all production code and existing tests;
- `RestrictedReadAuthorityBinding` generalization;
- direct file, tool, patch, rollback, dry-run, final-real-apply, and approval
  migration;
- routes, APIs, schemas, `/chat` wiring, runtime/private data;
- Generic Act, shared Action authority, M101B successor work, M102, M103, or
  any successor milestone.

## 20. Authority Risks

- Treating direct file access or tool-plan approval as canonical Governance
  authority remains unsafe to assume.
- Treating patch proposal approval as equivalent to final-real-apply readiness
  remains a real risk requiring separate review, not silent migration.
- Treating a strong mutation consumer as proof of M101B field equivalence would
  create a false abstraction.
- Treating M101B's immutable contract as a reusable generic identity would
  broaden authority without evidence.
- Reopening durable Observation without a new consumer would add persistence
  without a truthful lifecycle.

## 21. Explicit Non-Goals

M102A does not:

- implement a second capability binding;
- modify or generalize `RestrictedReadAuthorityBinding`;
- modify production code, routes, APIs, schemas, or existing tests;
- migrate direct file read, tool executor, patch apply/rollback, dry-run, or
  final-real-apply;
- create a shared Action authority registry or Generic Act;
- add durable Observation, aggregation, Critic, Repair, Learning, retry,
  scheduler, or background execution;
- update `PROGRESS.md`;
- commit, tag, push, or claim PM acceptance;
- begin M102, M103, or a successor Build.

## 22. Build Authorization Gate

```text
M102A discovery: COMPLETE LOCALLY
Selected capability: NONE
Decision: D_NO_SECOND_CAPABILITY_CURRENTLY_JUSTIFIED
Selected model: MODEL_E_NO_SECOND_BUILD_YET
Second capability Build authorization: NOT GRANTED
Generic Act: NOT_IMPLEMENTED / NOT_AUTHORIZED / NOT_GRANTED
```

## 23. Next-Step Gate

```text
Next authorized action: HUMAN/PROJECT-MANAGER M102A CONSUMER-PROOF REVIEW
No second capability binding is authorized.
No shared Action authority is authorized.
```

Control returns to the human/project-manager.
