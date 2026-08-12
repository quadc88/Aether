# Milestone 94A Governed Read-Only File Inspection Boundary

Classification: BOUNDARY / DESIGN / CONTRACT-LOCK BUILD ONLY

Runtime capability: NONE

Tool execution: NONE

File Action invocation: NONE

Observation creation: NONE

API change: NONE

Configuration implementation: NONE

Execution-flag change: NONE

This decision record is the authoritative Milestone 94A synthesis of the
Milestone 94A Plan, the approval-continuity correction, and the approved-root
registration addendum. It freezes the future runtime contract only. It does
not implement the future Action, change the current runtime, or authorize
Milestone 94B or 94C.

## 1. Milestone and Build Status

Milestone 94 is OPEN and capability-driven. Its purpose is to connect exactly
one governed, bounded, read-only file-inspection capability from `/chat` to a
real observable result and deterministic verification while preserving
deny-by-default behavior for every other capability.

Milestone 94A is the current boundary, design, and contract-lock submilestone.
It adds no runtime capability and only freezes the future contract described
here. Milestone 94B is NOT AUTHORIZED and requires a fresh PM Plan and Build
definition. Milestone 94C is NOT DEFINED.

The exact authorized 94A Build paths are:

1. `PROGRESS.md`
2. `docs/architecture/MILESTONE_94A_GOVERNED_READ_ONLY_FILE_INSPECTION_BOUNDARY.md`
3. `tests/test_milestone_94a_governed_read_only_file_inspection_boundary.py`
4. `tests/test_progress_ledger_canonical_header.py`

Production changes are zero. README, Constitution, Architecture, configuration,
all production `aether/*`, existing architecture records, all existing tests
other than the canonical ledger test, private/runtime data, and API/OpenAPI
surfaces are protected.

## 2. No Runtime Capability

Milestone 94A does not execute tools, read a target file, create an Observation,
call Observation Intake, change Core Governance runtime, change `/chat`, change
configuration, change the restricted reader, create a registration API, change
API schemas, or change execution flags. It does not create a runtime Action,
scope, approval continuation, persistence record, or private runtime state.

The current `/chat` path remains Input -> Perception -> Thinking -> Core
Governance -> pending approval or structured response. Its first vertical-slice
break remains the Act boundary. `tool_execution_allowed` remains false.

## 3. Parent Milestone 94 Scope

The future parent capability is safe governed read-only inspection of one
explicitly approved regular project text file with bounded content and truthful
access, truncation, privacy, and deterministic verification status.

Milestone 94 does not authorize generic tool execution, write/delete,
shell/subprocess execution, network, email, patch apply, rollback, generic
approval-to-execution migration, generic Observation aggregation, Critic/Repair,
Learning integration, ASC runtime, background continuity, Resource Observation,
Resource Governance runtime, scheduler, economic capability, new cognitive
organs, identity changes, Constitution changes, or Architecture v0.4.

## 4. Correct Rule Inventory

Current raw Thinking rules are exactly:

- Rule 3: empty or whitespace input workflow clarification;
- Rule 7: low-risk tool suggestion soft signal;
- Rule 8: short input without a tool workflow clarification;
- Rule 9: default response workflow.

Current authoritative Core Governance hard constraints are exactly:

- Rule 1: identity integrity changed -> block;
- Rule 2: identity integrity missing or failed -> require approval;
- Rule 4: sensitive-term evidence -> require approval;
- Rule 5: high-risk evidence -> require approval;
- Rule 6: medium-risk non-None requested action -> require approval.

Rule 7 is a Soft Decision Signal. It is Thinking-owned proposal data only and
is not authorization. Rule 6 is not a current Thinking rule; its operative
ownership is Core Governance. Thinking proposes, Verification and Identity
supply evidence, Governance authorizes, Action executes only within an exact
authorization, Observation does not authorize, and Verification does not
execute or authorize.

## 5. Strategy C Authorization Lock

Selected authorization strategy: STRATEGY C.

Future Core Governance produces a non-public, call-local, exact, one-shot
scoped Action authorization companion as part of the one authoritative
Governance evaluation. The compatibility envelope remains the public decision
projection; the scope is not serialized into `policy_gate`, `policy_snapshot`,
ChatResponse, or loop trace.

The scope is not `tool_execution_allowed`, `execution_allowed`,
`policy_snapshot`, `suggested_tool`, a pending approval, an approved record,
an approval ID, tool registry authority, generic tool-executor authority, or
user-text authority. `tool_execution_allowed` remains false.

## 6. Exact Action Identity and Dispatch

The exact future capability identity is:

- capability ID: `file.restricted_read`;
- bound implementation:
  `aether.action.restricted_file_reader.read_restricted_file`;
- permission class: `read_only`;
- dispatch owner: a dedicated direct Action bridge called by Core Coordination
  only after the Governance scope is present.

The canonical `/chat` path must not use `execute_tool()`, generic registry
dispatch, HTTP self-calling of `/action/file/read`, or a duplicate reader
implementation. Existing direct APIs and the sandbox executor remain separate
compatibility surfaces and do not grant `/chat` authority.

## 7. Scope Binding and Lifetime

The future scope binds the exact capability, exact bound implementation, exact
normalized target, approved-root identity, read-only permission class, current
execution attempt, current request/task context, bounded allowed parameters,
and one dispatch only.

Scope semantics are non-persistent, non-serializable, non-transferable,
non-replayable, single-dispatch, invalid after dispatch, invalid after request
completion, and invalid when current Governance re-evaluation fails. The scope
must not cross turns. Approval evidence may cross turns, but it never becomes a
scope.

Any missing, extra, stale, malformed, over-broad, or mismatched scope fails
closed. No Action derives a scope from a boolean, registry entry, user text,
pending approval, policy snapshot, suggested tool, or approval ID.

## 8. Approval Continuity

APPROVAL MAY PERSIST.

EXECUTION AUTHORIZATION MUST NOT PERSIST.

A persisted approved record is human-decision continuity evidence only. It is
not execution authority, a scope, a reusable grant, or an execution trigger;
it is not a scheduler instruction or a background wake marker. Pending approval never
dispatches. An approved record alone never dispatches.

Every future execution attempt requires current approval evidence when approval
is required, fresh current evidence, fresh Governance evaluation, a fresh
call-local scope, and immediate one-shot dispatch. Approval decision is not
approval-triggered execution. There is no same-turn callback, automatic
continuation, scheduler, or background wakeup.

## 9. Execution-Time Governance Reauthorization

At actual future execution time, Core Governance must re-evaluate current:

- identity integrity;
- Rule 4 sensitive-term evidence;
- risk and precedence;
- approved-root policy;
- exact capability;
- bound function;
- exact normalized target and containment;
- permission class;
- privacy conditions;
- request/task context;
- approval continuity.

Changed material conditions fail closed or require fresh human approval. No old
approval becomes permanent authority. The current repository has no truthful
post-approval execution entrypoint, so the entrypoint is:

`EXECUTION_ATTEMPT_ENTRYPOINT: DEFERRED_WITH_REASON`

A later authorized 94B Plan must define the real coordination call before any
runtime implementation. It must not invent a new `/chat` field, approval-resume
route, automatic approval callback, background continuation, scheduler, or auto
execution after approval.

## 10. Approved-Root Human Authorization

`ROOT_REGISTRATION_MECHANISM: MANUAL_ADMIN_CONFIG_EDIT`

The authoritative storage is `config/aether.yaml`. The existing authoritative
resolver is `aether/core/config.py`. A human or administrator deliberately
edits deployment configuration through the normal administrative/configuration
workflow. No approved-root registration API is introduced by Milestone 94.

The future conceptual configuration is:

```yaml
security:
  restricted_file_read:
    approved_roots:
      - <human/admin configured root>
```

The exact production key and accessor are NOT IMPLEMENTED by 94A and may only
be finalized by a later authorized runtime Build after config-schema
compatibility inspection. Missing configuration, an empty root list, or a
malformed root list denies access. `/chat`, Thinking, the tool registry,
environment variables, and automatic project-root inference have no authority
to add or expand roots. `/home/aether/projects/Aether` is not hardcoded as
authority.

Root configuration is policy input only and does not create Action authority.
Human root registration never overrides hard privacy or system-path denies.

## 11. Root, Containment, and Privacy Locks

The future root contract preserves Windows/POSIX support, project-relative root
resolution through the authoritative project-root resolver, `Path.resolve()`
normalization, path-relationship containment rather than string-prefix checks,
traversal escape denial, symlink-outside-root denial, regular-file-only reads,
the existing extension allowlist, the 64 KiB target file limit, and bounded
`max_chars`.

Read-only is not privacy-safe. Future `/chat` reads require pre-read
sensitive-path hard denial, Rule 4 before Action, deterministic high-confidence
content-level secret filtering, and fail-closed behavior when that filter is
unavailable. No LLM, fuzzy model, or semantic classifier is a hard privacy
decision.

The content filter may suppress output but may not authorize, widen scope,
renew authorization, or create approval. Raw content, secrets, and matched
values must not enter the scope, policy snapshot, approval records, warnings,
loop trace, Observation records, or generic audit metadata. The `/chat`-specific
read audit mode must not persist raw returned content. Existing direct API
behavior remains frozen unless separately reviewed.

## 12. Observation Intake and Stage Separation

`OBSERVATION_INTAKE: DEFER_FIRST_SLICE`.

Current `/chat` has no truthful source for `plan_step_id`,
`collector_contract_id`, or `evidence_items`. No trace ID, approval ID,
file-access ID, execution ID, or generated placeholder may substitute for those
fields. The first future runtime slice may create one capability-specific
in-memory Observation, but it must not call `handle_observation_intake()` or
persist an Observation Record.

Action result, Observation, and Verification remain distinct:

- Action result: the actual bounded restricted-reader result;
- Observation: the factual, privacy-filtered capability-specific in-memory
  observable result;
- Verification: deterministic evaluation of scope, Action result, Observation,
  and response linkage.

Observation does not authorize. Verification does not execute or authorize.

## 13. Deterministic Verification Vocabulary

The exact six future statuses are:

1. `VERIFIED_SUCCESS` - authorized, complete bounded read with all checks pass
   and no truncation;
2. `VERIFIED_PARTIAL` - valid bounded read with truthful truncation;
3. `DENIED` - governance, path, privacy, scope, or hard policy denial;
4. `NOT_FOUND` - authorized target absent at Action time, never empty success;
5. `CHANGED_DURING_READ` - detectable target, symlink, size, identity, or
   relevant stat change between checks and completion;
6. `INTERNAL_ERROR` - malformed, unexpected, verifier, decoding, or audit
   failure preventing a truthful success claim.

No generic Verification Aggregator is introduced.

## 14. TOCTOU Contract

Authorization-time target identity does not prove read-completion identity. A
future Action re-resolves immediately before reading; the existing reader keeps
defense-in-depth checks; and pre/post identity/stat comparison is best-effort.
Detectable target, symlink, size, or identity changes produce
`CHANGED_DURING_READ`. There is no silent retry, no false atomicity claim, and
no OS-specific transactional filesystem requirement in 94A.

## 15. Compatibility and Trace Truthfulness

94A changes none of the existing direct API semantics for `POST /action/file/read`,
the restricted reader, restricted browser browse/search, sandbox `execute_tool`,
the `file.restricted_read` sandbox branch, registry, planner, self-inspection,
file-access audit, Timeline, Graph, Working Memory, or direct tool-execution
logs.

There is no ChatResponse expansion, public Observation field, public scope
field, public verification aggregate, or OpenAPI expansion. The expected
OpenAPI shape remains 304 paths / 108 schemas. `api_server.py` remains 8 direct
`@app` routes / 23 included routers / 0 direct `/action/*` routes and receives
no feature logic.

Future trace attribution is truthful: Thinking proposes; Governance authorizes;
Action dispatches and returns a bounded result; Observation records a factual
post-Action result; Verification evaluates deterministically; Response reports
the result. The trace must never claim Thinking executed or authorized,
Governance observed content, Observation authorized, or Verification executed
or authorized. No private scope or raw content enters trace output.

## 16. Failure, Persistence, and Consumer-Proof Contract

Future failure behavior is fail-closed for outside-root, sensitive-path,
unsupported-extension, oversized, permission-denied, missing, directory or
special-file, decode/read, truncation, Governance-denial, Observation-mapping,
Verification, audit-persistence, and content-secret-filter failures. Target
mutation is NONE. Persistence is bounded audit/runtime persistence only; no
scope persistence, raw content in `/chat` audit mode, generic execution log
through the selected direct bridge, or persisted Observation Record in the first
slice.

The future dependency direction is:

```text
/chat
 -> Core Coordination
 -> Thinking proposal
 -> Core Governance
 -> approval evidence when required
 -> fresh scoped authorization
 -> dedicated direct Action bridge
 -> existing restricted reader
 -> Action result
 -> in-memory capability Observation
 -> deterministic capability verifier
 -> existing response mapping
```

There is no orphan component and no generic executor fallback. The preferred
future sequence is Option A. It requires a fresh PM Plan and Build definition
for 94B, including the truthful post-approval entrypoint, exact config
key/accessor compatibility, production modules, supersession set, test
families, and runtime persistence behavior. 94C remains not defined.

## 17. Temporal and Lifecycle Truth

STATE_A: PASS - this dirty precommit candidate records only current local Build
content and does not claim a future commit, tag, push, or PM acceptance.

STATE_B: PASS - a future boundary commit is not claimed by this record.

STATE_C: PASS - a future push is not claimed by this record.

STATE_D: PASS - future PM durable acceptance is not claimed by this record.

Git remains authoritative for durability, tag, and publication state. No Git
lifecycle operation is part of this Build.

## 18. Final Decision

Milestone 94A Build: complete

Decision: `READY_FOR_MILESTONE_94A_PM_BUILD_REVIEW`

READY does not authorize commit, tag, push, or Milestone 94B. Next authorized
action: human/project-manager review.
