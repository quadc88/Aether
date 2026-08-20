# Milestone 101A Action Authority Consolidation Build-Scope Boundary

Classification: STRICT DESIGN / DISCOVERY / BUILD-SCOPE BOUNDARY

Status: DESIGN CANDIDATE / DISCOVERY COMPLETE LOCALLY / HUMAN-PROJECT-MANAGER REVIEW REQUIRED

This record defines the smallest defensible future Build boundary for the
M100A-selected live action-authority gap. It does not implement a runtime
change, migrate a route, alter restricted-read behavior, or authorize a Build.

## 1. Current Git State

- Branch: `main`.
- Durable M100A HEAD: `bed3667dcaf5304979c15d86605de75684ac7532`.
- Local `main`, `origin/main`, and remote `main` matched at audit start.
- Tracked worktree: clean at audit start.
- M100A: FINALIZED / COMMITTED / TAGGED / PUSHED.
- M101A creates only this design candidate and its static/document lock as
  local untracked evidence.
- No commit, tag, or push is authorized by M101A.

## 2. Current Authority

The M100A decision remains binding:

- Highest-priority gap:
  `GAP-01_LIVE_ACTION_AUTHORITY_CONSOLIDATION`.
- Selected direction: `ACTION_AUTHORITY_CONSOLIDATION_GAP`.
- Consumer-proof strength: `STRONG`.
- Authority risk: `HIGH`.
- Future Build: `JUSTIFIED FOR PM REVIEW ONLY`.
- Actual production Build: `NOT YET AUTHORIZED`.
- Generic Act: `NOT_IMPLEMENTED`.
- Generic Act integration: `NOT_AUTHORIZED`.
- Generic Act authority: `NOT_GRANTED`.

The existing ownership boundaries remain binding:

- Core Governance decides authorization and hard constraints.
- Core Coordination owns canonical execution context and attempt binding.
- Action services execute only within an applicable capability boundary.
- Interface routers expose current paths and do not become cognitive authority.
- Verification supplies evidence and owns verification status.
- `GOVERNANCE_EVALUATION != EXECUTION_AUTHORIZATION`.

M101A does not activate Goal-to-Plan, ThinkingProposal production, Generic Act,
`/chat` execution expansion, durable Observation, or any successor runtime.

## 3. Exact M101A Objective

Define the smallest safe implementation boundary that can reduce ambiguity
among live action authorities without changing current behavior or broadening
execution authority.

The first candidate is limited to `file.restricted_read`, because its current
governed path already demonstrates exact capability identity, target and
session binding, fresh evidence, single-use approval consumption, scope-bound
dispatch, privacy handling, call-local Observation, and deterministic
verification. Other active paths are classified, not migrated.

The boundary must make one existing capability's authority semantics explicit;
it must not create a generic Action framework or infer that all Action paths
share one authority contract.

## 4. Active Action Entry-Point Inventory

The following inventory is based on current production source. The route
registrations are in `aether/interface/api_server.py:108-153`; the relevant
router calls are listed below.

| Active path | Capability and caller | Current authorization, binding, and freshness | Dispatch, privacy, evidence, failure, and consumer |
|---|---|---|---|
| `/chat/restricted-read/resume` and `/action/file/execute-approved-read` | `file.restricted_read`; `file_routes.py:39-54` -> `restricted_file_read_execution_service.py:79-148` -> `core/coordination.py:33-122`. | `approval_decision_gate.py:19-71` validates exact action, fingerprint, approval state, consumed state, and session. Coordination parses the exact command, normalizes target, requires capability `file.restricted_read`, `read_only`, target, and `max_chars` equality, then recomputes perception, risk, identity, and policy before Core Governance authorization. | `approval_queue.py:309-376` atomically claims one approved record. Governance mints a bound `RestrictedReadScope`; `restricted_file_read_bridge.py:4-34` checks attempt, capability, target root, max chars, and one-use dispatch before calling governed reader mode. The reader enforces approved roots, sensitive paths, file type/size, changed-during-read detection, and content privacy scanning. It emits a call-local Observation consumed by `verify_restricted_file_read`; denials and execution errors fail closed. The current consumer is the restricted-read verifier and response path. |
| `/action/file/read` | Direct file read; `file_routes.py:57-60` -> `file_service.py:86-89`. | `read_restricted_file` defaults to `mode="direct"`; it uses the independent `ALLOWED_ROOTS` path check. No Core Governance decision, execution attempt, approval claim, freshness recheck, identity/session binding, or single-use claim is present. | Direct mode records a file-access audit and returns content after path, extension, size, and sensitive-path checks. It does not use governed approved roots, governed content scanning, or call-local restricted-read verification. The file service and access-audit endpoints consume the result. |
| Tool planner | Non-executing planning path; `tool_planner.py:250-344`. | Infers or accepts a tool ID, combines text risk with Tool Registry risk, decides approval and verification requirements, and may create a legacy approval item. It persists a plan but does not itself dispatch an Action. | Planning output is consumed by `execute_tool` and plan/status readers. It is not an authorization owner and must not be treated as one. Invalid, missing, disabled, or approval-required tools remain non-executable. |
| `/action/tool-executor/execute` | Local tool execution; `tool_executor_routes.py:21-31` -> `tool_execution_service.py:115-177` -> `tool_executor.py:332-403`. | Accepts `tool_id`, arbitrary `input_payload`, text, proposed action, metadata, and `dry_run`. Local planner/registry risk and approval state control execution. There is no canonical capability target/session/identity binding, fresh Core Governance recheck, or universal single-use claim. | `_safe_result` dispatches `file.restricted_read` at `tool_executor.py:199-204` without governed mode, and also dispatches patch apply/rollback. Results are logged to execution, Working Memory, Timeline, graph, and optional file audits. Local statuses are `approval_required`, `blocked`, `failed`, or tool result status. |
| `/action/patch-apply/apply` | Action-specific mutation; `patch_routes.py:72-80` -> `patch_service.py` -> `patch_apply.py:31-56`. | Proposal status, optional legacy queue item approval, critical-path block, direct file read, excerpt uniqueness, and current content are checked. `dry_run=False` writes after local checks. No canonical execution-attempt, identity/session, fresh Governance, or single-use claim exists. | Creates backup before write, records before/after hashes, apply status, mutation log, Timeline, and graph. Missing, unapproved, critical, ambiguous, or write-failure paths become blocked/failed records. Current consumers are patch records and audit records. |
| `/action/patch-rollback/rollback` | Action-specific restoration; `patch_routes.py:81-89` -> `patch_service.py` -> `patch_rollback.py:31-52`. | Requires a successful applied record, backup path, allowed backup location, and non-critical target. It has no canonical approval, identity/session, freshness, or universal single-use claim. | Creates a pre-rollback backup and compares current, backup, and after hashes. Ineligible, invalid, critical, or failed paths become blocked/failed records. Current consumers are rollback records and mutation/audit records. |
| Approved dry-run and review chain | Non-executing or action-specific planning records; `dry_run_routes.py:23-50`, `approved_dry_run_gate.py:29-57`, `dry_run_review_gate.py:27-51`. | Individual approval validation may allow a dry-run, but `dry_run_request.py:71-91` forces execution, tool execution, apply, and rollback false. Approved dry-run hard-codes `dry_run=True`; review records only human decisions. | Dry-run and review records are consumed by later mutation gates and human operators. Invalid, repeated, or incomplete records fail closed. They do not create a universal execution authority. |
| Final real-apply approval gate | Action-specific gated execution readiness; `real_apply_approval_gate.py:149-206`. | Requires accepted dry-run review and completed dry-run, then creates a legacy approval item. Final decision transitions to `final_approved`, `final_rejected`, or review-pending. It binds records by gate/proposal/apply IDs, not identity/session. | The gate only records readiness and final decision. Safe metadata filtering is applied. It never directly applies or rolls back; its current consumer is the final-real-apply executor. |
| Final-real-apply executor | Action-specific gated mutation; `final_real_apply_executor_routes.py:19-30` -> `final_real_apply_executor.py:165-201`. | `_refresh_readiness` requires final approval, approved legacy queue item, completed dry-run, approved proposal, and no prior applied executor record. One-use is gate-scoped by prior applied record, not a universal execution token. | Calls `apply_patch_proposal(..., dry_run=False)` only after readiness. It creates real apply, backup, rollback-availability, mutation, Timeline, and graph evidence. Post-apply verification is a separate human gate. Missing readiness or failed apply blocks. |
| Approval decision paths | Two stores exposed by `approval_routes.py:29-103`: individual approval records and legacy `approval_queue.json` items. | Individual records carry structured action, restricted-read fingerprint, status, context, and execution-consumed fields. The legacy queue carries request text, proposed action, verification plan, and metadata. Pending-only transitions are enforced in both stores, but they are not one shared authority. | The individual record is consumed by canonical restricted-read validation and atomic claim. Legacy items are consumed by tool, patch, and final-real-apply paths. Malformed, missing, mismatched, consumed, or already-decided records fail closed or remain unchanged with warnings. |
| Call-local Observation and verification | Evidence-only path; `restricted_file_read_observation.py:7-30` -> `coordination.py:99-115` -> `verification/restricted_file_read.py:10-28`. | Observation is created only after governed reader dispatch. It has no durable general lifecycle or separate universal identity. | It carries reader status, normalized target, bounded content, action ID, privacy flag, and truncation. Verification returns deterministic statuses including success, partial, denied, not found, changed, and internal error. The canonical consumer is immediate restricted-read verification; Observation Intake is a separate declarative record path. |

## 5. Authority-Classification Table

| Path or component | Classification | Evidence-backed disposition |
|---|---|---|
| Governed restricted-read resume and approved execution | `CANONICAL_GOVERNED_CAPABILITY` | Keep as the reference capability. Any first Build must preserve its existing behavior and make its binding seam explicit. |
| Direct file read | `LEGACY_COMPATIBILITY_EXECUTION` and `DIRECT_UNIFIED_AUTHORITY_NOT_PROVEN` | `UNCHANGED_BUT_CLASSIFIED`; requires separate review before binding or migration. Do not silently treat direct mode as governed mode. |
| Tool planner | `NON_EXECUTING_PLANNING_PATH` | Remains a planner and risk/approval proposer, not an authorization or dispatch owner. |
| Tool executor, including sandbox `file.restricted_read` | `LEGACY_COMPATIBILITY_EXECUTION` | `QUARANTINED_AS_LEGACY` relative to the canonical governed capability; no first-Build migration. |
| Patch apply and patch rollback | `ACTION_SPECIFIC_GOVERNED_EXECUTION` | `EXEMPT_ACTION_SPECIFIC_AUTHORITY` for the first slice; preserve local proposal, backup, hash, and rollback semantics and require separate review for any change. |
| Final-real-apply approval and executor chain | `ACTION_SPECIFIC_GOVERNED_EXECUTION` | `EXEMPT_ACTION_SPECIFIC_AUTHORITY` for the first slice; it is a separate, stronger mutation chain, not a common authority for reads. |
| Generic approval validation and dry-run records | `NON_EXECUTING_PLANNING_PATH` | Evidence or readiness only; no execution authority and no Generic Act bridge. |
| Call-local restricted-read Observation | `EVIDENCE_ONLY` | Keep call-local and immediately consumed; do not add durable Observation in M101A or the first Build. |

Classification is not a safety verdict. It records which authority contract is
currently active and prevents accidental equivalence claims.

## 6. Ownership Matrix

| Concern | Current owner | M101A boundary decision |
|---|---|---|
| Policy and governance decision | Core Governance, especially `authorize_restricted_read_execution` and the compatibility envelope | Remains Core Governance. The first Build must call existing decision logic, not create a second policy authority. |
| Authorization binding | Canonical path spans approval decision gate, Core Coordination exact-request checks, and Governance scope minting | Make the `file.restricted_read` binding seam explicit under Core Coordination ownership. The seam binds capability, normalized target, permission, max chars, approval evidence, session, evidence snapshot, and execution attempt. It is not a universal registry. |
| Approval consumption | Individual approval record store and `claim_approval_for_execution` for canonical restricted read; legacy queue for local mutation chains | Preserve both stores. Canonical atomic claim remains the only first-slice execution claim. No approval-store migration. |
| Freshness validation | Core Coordination recomputes perception, risk, identity, and policy; Governance evaluates current evidence | Preserve the current execution-time re-evaluation order and fail closed on unavailable or failed evidence. |
| Single-use claim | Approval record atomic claim plus restricted-read scope dispatch lock | Preserve both mechanisms. The binding seam must not claim twice or replace either with a generic token. |
| Dispatch | `restricted_file_read_bridge.py` for canonical governed read; local Action functions for other paths | Preserve the existing restricted-read bridge as dispatch owner. The binding seam returns no content and does not dispatch. |
| Privacy enforcement | Governed reader and configured approved roots for canonical read; independent direct reader checks for direct paths | Preserve governed privacy and approved-root checks. Direct privacy semantics remain separately classified and are not silently upgraded. |
| Verification result binding | `verify_restricted_file_read` consumes the call-local Observation in Core Coordination | Preserve immediate call-local Observation consumption and deterministic result mapping. Verification owns status, not authorization. |
| Interface routing | FastAPI routers and service adapters | Interface remains exposure only. No route, request model, OpenAPI, or `api_server.py` change is required for the first Build. |

## 7. `file.restricted_read` Reference Model

The reference path is:

```text
approved chat action / approved execution request
  -> exact command, capability, target, permission, max_chars, session checks
  -> approval-record fingerprint and status validation
  -> fresh Perception, Risk, Identity, and Thinking evidence
  -> Core Governance authorization and RestrictedReadScope minting
  -> atomic single-use approval claim
  -> scope- and attempt-bound restricted-read bridge
  -> governed reader privacy and filesystem checks
  -> call-local RestrictedReadObservation
  -> immediate restricted-read verification
  -> response with no outward Observation object
```

The current evidence is concrete:

- Capability identity and exact request checks are in
  `aether/core/coordination.py:33-50`.
- Approval fingerprint and session binding are in
  `aether/action/approval_decision_gate.py:19-71` and
  `aether/action/approval_queue.py:15-43`.
- Fresh evidence and Governance scope construction are in
  `aether/core/coordination.py:62-92` and
  `aether/core/governance.py:449-524`.
- Atomic approval consumption is in
  `aether/action/approval_queue.py:309-376`.
- Scope-bound, one-use dispatch is in
  `aether/action/services/restricted_file_read_bridge.py:4-34`.
- Governed roots, privacy scanning, and changed-during-read handling are in
  `aether/action/restricted_file_reader.py:53-123`.
- Call-local evidence and verification are in
  `aether/action/restricted_file_read_observation.py:7-30` and
  `aether/verification/restricted_file_read.py:10-28`.

The existing configured governed roots are empty and the governed path fails
closed when no approved root exists. This is a current configuration result,
not permission to alter configuration or reader behavior in M101A.

## 8. Direct and Legacy Path Classification

M101A makes no route change. The following is the future classification needed
before any later review:

- Direct file read: leave unchanged but explicitly classify as direct-mode
  compatibility execution. A later review must decide whether it remains a
  compatibility path, is quarantined, or receives a separately designed
  capability binding. No direct route is presumed unsafe solely because it is
  different.
- Tool-executor `file.restricted_read`: quarantine as a legacy compatibility
  invocation relative to the canonical capability. It currently calls the
  reader without governed mode and lacks canonical request/session binding.
  No migration is proposed here.
- Tool planner: retain as a non-executing planner. Its risk and approval
  proposal is not an authorization decision.
- Patch apply: retain as action-specific governed execution with local
  proposal, approval-item, direct-reader, excerpt, backup, and hash semantics.
  It requires separate review before any capability binding.
- Patch rollback: retain as action-specific restoration with local eligibility,
  backup-path, hash, and pre-rollback-backup semantics. It is not a read
  capability and is outside the first Build.
- Final-real-apply: retain as a separate action-specific gated mutation chain.
  Its final approval, completed dry-run, legacy queue item, backup, and
  post-apply verification semantics must not be collapsed into restricted-read
  authority.

## 9. Build Model Comparison

| Model | Boundary | Evidence assessment |
|---|---|---|
| `MODEL_A_CAPABILITY_AUTHORITY_BINDING_SERVICE` | Add one capability-scoped binding seam for `file.restricted_read`, preserve current Governance, claim, bridge, reader, Observation, verification, and response behavior. | Best fit. Strong consumer proof, minimal behavior change, explicit ownership, focused tests, no route/API change, and reversible without data migration. |
| `MODEL_B_SHARED_ACTION_AUTHORITY_REGISTRY` | Introduce a shared registry/classification or authority layer across file, tool, patch, rollback, and final-real-apply paths. | Not selected. It would force unlike contracts together, risk broadening authority, and require multiple owner and migration decisions without a first-slice need. |
| `MODEL_C_ROUTE_LEVEL_CLASSIFICATION_ONLY` | Add metadata or documentation around current routes without a new binding owner. | Useful inventory but insufficient as a Build boundary. It would record ambiguity without reducing it for the strongest live capability. |
| `MODEL_D_NO_BUILD_YET` | Stop at discovery because even the first capability boundary cannot be defined safely. | Not selected. The canonical restricted-read path has sufficient exact contract and consumer proof for a bounded review, while all other paths can remain out of scope. |

## 10. Selected Build Model and Decision

Build-scope decision:

```text
A_SMALL_CAPABILITY_SCOPED_BUILD_JUSTIFIED
```

Selected model:

```text
MODEL_A_CAPABILITY_AUTHORITY_BINDING_SERVICE
```

Recommended Build scope: `JUSTIFIED FOR PM REVIEW` only.

This decision means that a separately authorized future Build can implement a
small `file.restricted_read` binding seam. It does not authorize implementation
now and does not classify any other Action path as equivalent.

## 11. Exact Smallest Build Boundary

If separately authorized, the first Build should:

1. Add one capability-scoped binding contract for `file.restricted_read`.
2. Have the existing `execute_approved_restricted_read` path consume that
   contract before approval claim and dispatch, without changing its response
   shape or decision order.
3. Keep Core Governance as the authorization decision owner.
4. Keep Core Coordination as the execution-attempt and context-binding owner.
5. Keep the approval record store as the atomic claim owner.
6. Keep the restricted-read bridge as the dispatch owner.
7. Keep the governed reader as the privacy owner and the existing verifier as
   the verification owner.
8. Preserve exact capability, normalized target, `read_only` permission,
   bounded `max_chars`, approval fingerprint, session, identity, risk, policy,
   approved-root, attempt, and single-use semantics.
9. Return a bound scope or a safe denial. The binding contract must not return
   file content, create a generic Action, or dispatch a tool.
10. Leave direct file read, tool executor, patch apply/rollback, final-real-
    apply, approval-store migration, and Observation persistence outside scope.

### Proposed contract

The future contract is capability-specific, not a generic registry:

- Input: the existing approved-read request, parsed exact action, approval
  binding result, fresh identity/risk/policy evidence, session/context, and a
  newly created execution-attempt ID.
- Output: an immutable `authorized`/denied result containing the existing
  `RestrictedReadScope` when authorized, safe reason/warnings when denied, and
  the same attempt binding. It contains no raw content and has no generic
  `action_type` dispatch hook.
- Consumer: the existing canonical restricted-read execution path reached by
  `/chat/restricted-read/resume` and `/action/file/execute-approved-read`.
- Unchanged behavior: request matching, fresh evidence evaluation, approval
  claim timing, scope dispatch, governed privacy, call-local Observation,
  verification statuses, response shape, and `tool_execution_allowed=False`.

### Expected future Build files

Expected files a separately authorized first Build may modify:

- `aether/action/services/restricted_file_read_authority_binding.py` (new,
  capability-specific binding contract and implementation seam).
- `aether/core/coordination.py` (minimal delegation to the seam; no route,
  response, authorization rule, or dispatch behavior change).
- `tests/test_restricted_read_authority_binding.py` (new focused contract and
  failure-closed tests).
- A narrowly scoped existing restricted-read test may be extended only if the
  separately authorized Build requires it; no unrelated test family should be
  changed.

### Files that must not be modified by the first Build

- `aether/interface/api_server.py` and all route modules.
- `aether/interface/api_models.py` and OpenAPI-facing schemas.
- `aether/action/restricted_file_reader.py` and governed/direct reader policy.
- `aether/core/governance.py` authorization decision semantics.
- `aether/action/approval_queue.py` stores or claim protocol.
- `aether/action/services/restricted_file_read_bridge.py` dispatch behavior.
- `aether/action/restricted_file_read_observation.py` and
  `aether/verification/restricted_file_read.py` evidence semantics.
- Direct file, tool executor/planner, patch apply/rollback, dry-run, final
  real-apply, and post-apply verification paths.
- Generic Act, `/chat` loop wiring, Goal/Task/Plan, ThinkingProposal,
  Observation Intake, persistence, scheduler, or private runtime data.

## 12. Required Tests for a Future Build

The separately authorized Build must prove, without invoking a route or
changing public API:

- exact capability identity is required;
- normalized target, read-only permission, and `max_chars` are exact;
- approval fingerprint, status, session, and consumed state are exact;
- fresh identity, risk, policy, and approved-root checks are preserved;
- the execution attempt is bound to the returned scope;
- approval claim remains atomic and one-use;
- scope dispatch remains one-use and rejects a second attempt;
- direct-mode fallback is impossible from the canonical binding seam;
- governed privacy filtering and changed-during-read behavior remain intact;
- call-local Observation is produced and immediately verified;
- all invalid or unavailable evidence fails closed without content disclosure;
- response shape and `tool_execution_allowed=False` remain unchanged;
- OpenAPI and `api_server` route baselines remain unchanged.

## 13. OpenAPI and `api_server` Impact

Expected first-Build impact:

- OpenAPI: no change; baseline remains `306 paths / 112 schemas`.
- `api_server`: no change; baseline remains `8 direct @app routes / 23 include_router / 0 direct /action/*`.
- Routes: no route additions, removals, prefixes, operation IDs, request
  models, or response models.
- The existing two canonical restricted-read entry points remain the callers;
  direct and legacy paths remain classified but untouched.

## 14. Failure-Closed Behavior

The first Build must deny before dispatch when any of these is true:

- request text is not the exact restricted-read command;
- capability, permission, target, normalized target, or `max_chars` differs;
- approval is missing, not approved, malformed, stale, mismatched, or already
  consumed;
- session, identity, risk, policy, or execution-attempt evidence is missing,
  invalid, changed, or unavailable;
- no approved governed root exists, target is outside it, or the target is
  sensitive, invalid, oversized, non-file, or disallowed;
- binding scope, approved root, reader function, or attempt ID is invalid;
- atomic approval claim fails or dispatch has already been consumed;
- privacy scanning or changed-during-read checking cannot complete safely;
- verification cannot bind the reader result to the call-local Observation.

There must be no fallback from a failed governed binding to direct reader mode,
tool executor mode, patch mode, or Generic Act. No content is returned for a
denied or unverifiable attempt.

## 15. Rollback and Removal Path

The future Build must be removable without data migration:

1. Revert the minimal delegation in `core/coordination.py`.
2. Remove the capability-specific binding module and its focused tests.
3. Re-run the pre-Build restricted-read, authority, API, and OpenAPI regression
   locks.
4. Confirm no route, schema, approval-store, private-data, or public-record
   migration occurred.

The first Build must not rewrite approval records, create new durable Action
records, or alter existing route data, so rollback is code removal rather than
state conversion.

## 16. Authority Risks

Future implementation must avoid:

- turning the binding seam into a generic capability registry;
- letting the binding seam decide policy or replace Core Governance;
- moving approval consumption into Interface or a legacy service;
- treating direct-mode reads as governed reads without separate review;
- using tool plans, dry-run flags, or local queue items as canonical authority;
- broadening read-only capability into mutation or generic execution;
- adding durable Observation because call-local evidence exists;
- collapsing patch/final-real-apply authority into restricted-read authority;
- changing exact target, session, privacy, freshness, single-use, or verifier
  semantics silently;
- making a successful Build depend on `/chat` wiring, Generic Act, or dormant
  Goal-to-Plan components.

## 17. Explicit Non-Goals

M101A does not authorize:

- Action Authority Consolidation implementation;
- Generic Act, generic capability registry, or generic Action dispatch;
- `/chat` execution expansion or Goal-to-Plan activation;
- a ThinkingProposal producer or new M96 runtime consumer;
- durable Observation, Observation aggregation, Critic, Repair, or Learning;
- retry, scheduler, background execution, or new runtime loops;
- broad approval redesign or approval-store migration;
- broad tool-executor rewrite;
- patch apply/rollback migration or final-real-apply migration;
- any new public API, route, schema, or OpenAPI change;
- M101B, M102, or any successor runtime Build;
- changes to `PROGRESS.md`, README, Constitution, Architecture, production
  code, existing tests, or runtime/private data;
- commit, tag, push, or a PM acceptance claim.

## 18. Build Authorization Gate

```text
M101A design/discovery: COMPLETE LOCALLY
Selected model: MODEL_A_CAPABILITY_AUTHORITY_BINDING_SERVICE
Build-scope decision: A_SMALL_CAPABILITY_SCOPED_BUILD_JUSTIFIED
Recommended Build scope: JUSTIFIED FOR PM REVIEW
Actual production Build authorization: NOT YET AUTHORIZED
```

`JUSTIFIED FOR PM REVIEW` is evidence for a bounded future decision. It is not
permission to implement the selected model.

## 19. Next-Step Gate

```text
Next authorized action: HUMAN/PROJECT-MANAGER M101A BUILD-SCOPE REVIEW
M101B: NOT AUTHORIZED
M102: NOT AUTHORIZED
Generic Act: NOT_IMPLEMENTED / NOT_AUTHORIZED / NOT_GRANTED
```

Control returns to the human/project-manager. No production Build is started by
this milestone.
