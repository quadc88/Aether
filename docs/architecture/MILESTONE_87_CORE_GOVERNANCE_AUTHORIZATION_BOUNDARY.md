# Milestone 87 Core Governance Authorization Decision-Envelope Boundary

## 1. Status and Scope

Status: accepted Milestone 87A boundary decision record, complete locally but
not finalized, committed, tagged, or pushed.

This record is authoritative for the Milestone 87 authorization-envelope
foundation until an explicitly authorized later architecture or boundary
revision supersedes it. Milestone 87A is design-record and tests-only work. It
does not implement, extract, redirect, or otherwise change the runtime
authorization boundary. Milestone 87 remains open, Milestone 87B has not
started, and Milestone 88 has not started.

## 2. Purpose

The current production `/chat` chain contains a real authorization-like
decision boundary, but its responsibilities are divided incorrectly for Aether
Architecture v0.3.0: Thinking emits proposal fields that look authoritative and
the operative gate is physically located under Action. This record fixes the
ownership contract before any code is moved.

The boundary preserves current observable behavior. It introduces no new
policy input, permission, approval semantic, execution path, persistence,
endpoint, schema, or runtime capability.

## 3. Authoritative Existing Baseline

The accepted starting baseline is:

- Architecture v0.3.0 and Constitution v0.2.0;
- full suite 2137 passed before Milestone 87A;
- architecture and Observation focused suite 240 passed;
- PROGRESS consistency suite 55 passed;
- OpenAPI 304 paths and 108 schemas;
- `aether/interface/api_server.py`: 8 direct `@app` routes, 23
  `include_router` calls, and zero direct `/action/*` routes;
- Constitution SHA-256
  `0055748f683bf753b3471a0317b68677752c312d4030b12fbc71684fd3af3ee1`;
- canonical drift 0 at fingerprint
  `600fd549588be7f536f704bc999be1987dcdf550225f2dc11dbf2fbf63ec2bcd`;
- tracked private/runtime paths empty and `docs/history` clean.

Milestone 85's Observe/Verify lifecycle boundary remains in force. No
Observation classification or record becomes an execution trigger.

## 4. Architecture Ownership

Core Governance owns the authoritative authorization decision. Core
Coordination owns call sequencing and invokes Governance. Thinking owns
proposal generation. Verification and Identity supply evidence. Action owns
execution and downstream approval mechanics. Approval records represent human
review state but do not own authorization policy. Timeline and loop trace
record outcomes but do not decide them.

Aether remains one persistent identity. This boundary creates no second agent,
identity, task reality, or authority source.

## 5. Current Production Chain

The repository-proven chain is:

1. external `POST /chat`;
2. `aether.interface.api_server.chat` (Interface);
3. `aether.core.runtime.AetherRuntime.process_chat`;
4. `aether.core.loop.run_core_chat_loop` (Core Coordination);
5. `aether.perception.text.perceive_text_input`;
6. `aether.identity.guard.verify_identity_integrity` evidence;
7. `aether.time.clock.now_iso` and `time_state` facts;
8. optional `aether.memory.working.store.WorkingMemory` updates;
9. `aether.verification.risk.classify_risk` evidence;
10. `aether.core.loop._suggest_tool`, using
    `aether.action.tool_planner.infer_candidate_tool`, for a suggestion only;
11. `aether.thinking.policy.decide_chat_policy` proposal;
12. `aether.action.policy_gate.enforce_policy_gate`, the current operative
    gate;
13. `aether.action.approval_request.build_approval_request` where applicable;
14. optional `aether.action.approval_queue.create_approval_record` producing a
    pending record;
15. response construction, `aether.core.loop_trace.build_loop_trace`, and
    `aether.memory.timeline.recorder.record_event`.

Production importer inventory for `enforce_policy_gate`: exactly
`aether/core/loop.py`. The direct test importer is `tests/test_policy_gate.py`.
No router, API-only action path, or Observation component is a production
internal consumer of this gate.

## 6. Current Responsibility Mixing

`aether.thinking.policy.decide_chat_policy` correctly proposes a workflow, but
also emits `required_user_confirmation` and `tool_execution_allowed`, which
look like authorization fields. `aether.action.policy_gate.enforce_policy_gate`
then treats the Thinking output as its decision source and is physically under
Action even though the decision is normatively Governance-owned.

The current pure gate also couples a synthetic input of
`tool_execution_allowed=True` to `allowed=True`,
`tool_execution_allowed=True`, and `action_execution_allowed=True`. Existing
production Thinking outputs always set `tool_execution_allowed=False`, and the
core loop unconditionally reports `tool_execution_allowed=False` and
`tool_executed=False`. Milestone 87A records both facts. It does not hide the
legacy coupling and does not permit it to define the future architecture.

## 7. Selected Boundary

The selected boundary is one internal, call-local, non-persistent Core
Governance authorization decision envelope. It receives the existing Thinking
proposal plus direct call-local Verification and Identity evidence and returns
one compatibility envelope matching the current gate's observable result.

There must be one authoritative decision implementation. Thinking proposal
fields are inputs, not authority. Evidence is descriptive, not authority.
Governance makes the final decision. Action may execute only within separately
proven authorization; the `/chat` path remains non-executing.

## 8. Exact Caller and Invocation Point

The exact production caller is
`aether.core.loop.run_core_chat_loop`. The future invocation point is the
current Step 7c gate location, after Perception, Identity checking, Time facts,
Working Memory updates, Verification risk classification, tool suggestion, and
Thinking proposal generation, and before approval-request construction.

Core Coordination invokes the boundary and retains sequence ownership. The
boundary must not import the core loop or Interface.

## 9. Input Provenance and Authority

Inputs are separated by provenance:

- Non-authoritative proposal input: the current Thinking policy dictionary,
  including candidate `decision_type`, suggested workflow/tool, proposal
  reasons, requested confirmation, compatibility execution flags, blocked
  reason, clarification question, next step, confidence, and warnings.
- Evidence input: the raw existing `risk` dictionary from
  `classify_risk`, the raw existing `identity_status` dictionary from Identity,
  the `requested_action`/suggested tool, and existing call-local metadata or
  context such as `session_id`.
- Governance-owned constraint input: only the existing compatibility rules now
  implemented by `enforce_policy_gate`: missing proposal invalidation, explicit
  block, approval-required handling, execution-disabled denial, and the legacy
  explicit-allow compatibility branch.

Evidence copied into or reflected by Thinking does not become authoritative.
Milestone 87B must pass the raw existing risk and identity evidence directly to
Governance where available rather than relying solely on proposal reflection.
No ASC state, resource budget, permission profile, new Constitution object,
background-task state, or Observation aggregation result is introduced.

## 10. Thinking Proposal Contract

The current `decide_chat_policy` output is a non-authoritative proposal. Its
current keys are `decision_type`, `confidence`, `reasons`,
`required_user_confirmation`, `tool_suggestion_allowed`,
`tool_execution_allowed`, `blocked_reason`, `clarification_question`,
`next_step`, and `warnings`.

Thinking proposes. It does not grant execution permission. During compatibility
migration, `decision_type`, `required_user_confirmation`, and
`tool_execution_allowed` remain legacy compatibility/proposal data. They may
influence Governance but cannot bind it. Milestone 87A neither deletes nor
changes these fields.

## 11. Verification and Identity Evidence Contract

Verification supplies the existing risk evidence dictionary, including current
`risk_level`, `action_type`, confidence, and reasons where present. Identity
supplies the existing integrity-state dictionary or `None`, including current
status/change evidence where present. Requested action, suggested tool, and
existing metadata/context are call-local evidence or request facts.

Evidence describes the current condition and provenance. It does not itself
authorize, approve, or execute. The future boundary may not manufacture missing
evidence or infer approval from its presence.

## 12. Governance Decision-Envelope Contract

The future Governance-owned compatibility envelope preserves exactly the
current top-level shape returned by `enforce_policy_gate`:

- `allowed`;
- `decision`;
- `reason`;
- `required_user_confirmation`;
- `tool_execution_allowed`;
- `action_execution_allowed`;
- `requested_action`;
- `policy_snapshot`;
- `warnings`.

Milestone 87B may use a clearer internal representation only if it preserves
this observable compatibility shape and all consumer behavior. It may not add
an allow path or silently tighten behavior under a no-behavior-change label.

## 13. Decision-Envelope Field Semantics

- `allowed` (`bool`): legacy processing/gate compatibility result. It must not
  be consumed alone as tool/action execution authority. Current production
  `/chat` always receives `False`; the pure legacy gate's synthetic allow branch
  returns `True` and is retained as compatibility behavior pending separate
  authorization.
- `decision` (`str`): authoritative Governance compatibility classification.
  Current values are `invalid_policy`, `block`, `require_approval`, `deny`, or
  `allow`.
- `reason` (`str`): diagnostic explanation of the decision, not permission.
- `required_user_confirmation` (`bool`): confirmation/approval workflow
  requirement; it does not mean confirmation is completed.
- `tool_execution_allowed` (`bool`): explicit legacy execution-status output.
  It remains `False` throughout production `/chat`.
- `action_execution_allowed` (`bool`): explicit legacy action-status output.
  It remains `False` throughout production `/chat`.
- `requested_action` (`dict | None`): request/proposal provenance copied through
  unchanged; it is not authority.
- `policy_snapshot` (`dict | None`): copied Thinking proposal provenance. It is
  not an authoritative Governance policy object.
- `warnings` (`list[str]`): diagnostics. Missing proposal currently yields one
  warning; other current branches normally yield an empty list.

Current defaults for `enforce_policy_gate` are
`thinking_policy=None`, `requested_action=None`, and `context=None`. `context`
is accepted but not used in the current decision.

## 14. Approval and Confirmation Boundary

These states are independent and must never be collapsed:

1. a proposal requests confirmation;
2. Governance requires approval;
3. an approval request object is constructed;
4. an approval record is pending;
5. Human Authority grants approval;
6. execution is separately authorized.

`build_approval_request` creates a non-executing object. The core loop may
persist a pending record through `create_approval_record`; that record remains
non-executing. Approval intent, request construction, pending status, or
`allowed=True` does not prove completed Human Authority approval or authorize
an external side effect. Existing approval persistence remains downstream and
is not moved by Milestone 87.

## 15. No-Execution Boundary

The production `/chat` invariants are:

- `tool_execution_allowed == False`;
- `action_execution_allowed == False` inside the current gate result;
- `tool_executed == False` in the core-loop response and trace;
- the `allow_tool_execution` argument is ignored;
- no tool/action executor is called after the gate;
- no real apply, rollback, evidence collection, external side effect, or
  Observation-driven action occurs;
- no approval request or pending approval record becomes execution
  automatically.

The selected boundary is internal, decision-only, call-local, and
non-executing.

## 16. Consumers and Compatibility Obligations

- `aether.action.approval_request.build_approval_request` reads `decision` and
  `reason` from the envelope; it also receives the Thinking proposal and other
  evidence separately. It does not mutate the envelope, persists nothing, and
  executes nothing. Milestone 87B must preserve request creation/non-creation,
  pending status, type, and reason.
- The optional approval path in
  `aether.core.loop.run_core_chat_loop` reads the approval builder's
  `approval_required`, not `allowed`; it may persist a pending record. It does
  not execute a tool/action. Milestone 87B must preserve this distinction.
- `run_core_chat_loop` reads `allowed`, `decision`, `reason`, and `warnings` for
  response and trace assembly and returns the full envelope as `policy_gate`.
  It does not mutate the envelope. Response keys and values must remain exact.
- `aether.core.loop_trace.build_loop_trace` receives copied booleans and warning
  counts from the loop. It persists nothing and executes nothing. Its safety
  structure must remain exact.
- `aether.memory.timeline.recorder.record_event` is downstream in the same loop
  but currently consumes no decision-envelope field; it receives chat/risk
  facts and writes the existing Timeline event. Milestone 87B must neither add
  envelope data nor change this persistence as part of extraction.

## 17. Failure and Fail-Closed Behavior

Current pure-gate behavior is locked:

- `thinking_policy is None` -> `invalid_policy`, `allowed=False`, confirmation
  required, both execution flags false, snapshot `None`, and warning
  `No thinking policy available to evaluate.`;
- explicit `decision_type == "block"` -> `block`, `allowed=False`, both
  execution flags false, confirmation required, with the supplied blocked
  reason or current fallback;
- `decision_type == "require_approval"` -> `require_approval`,
  `allowed=False`, both execution flags false, confirmation required;
- unknown, response-only, clarification, suggestion, malformed dictionary, or
  missing `decision_type` with no truthy `tool_execution_allowed` -> `deny`,
  `allowed=False`, both execution flags false;
- the current legacy synthetic truthy execution flag -> `allow` with true
  compatibility flags. Production Thinking never emits this state.

Ambiguous, malformed, contradictory, or incomplete authorization input must not
create execution permission. Milestone 87B must preserve current fail-closed
behavior. Any deliberate safety tightening that changes current observable
behavior requires separate explicit authorization and must not be hidden inside
the extraction.

## 18. Persistence, Privacy, and Side Effects

The Governance envelope is an in-memory return value scoped to one call. It has
no queue, store, schema, runtime/private directory, migration, lifecycle,
cleanup task, rollback, network access, or external side effect. It must not
add raw secrets, private data, or hidden reasoning to responses, traces, or
Timeline.

Existing optional approval and Timeline writes remain owned by their current
downstream components and are not part of the boundary implementation.

## 19. Physical Runtime Home Decision

Evaluated options:

- Option A, new top-level `aether/governance/authorization.py`: architecturally
  clear, but it creates a new package and import surface where the repository
  currently represents cross-cutting coordination/governance under `aether/core`.
- Option B, `aether/core/governance.py`: uses the existing Core package,
  represents the cross-cutting plane without inventing another organ/package,
  and permits a one-way import from the core loop.
- Option C, leave the authoritative implementation under Action: rejected
  because it preserves the ownership inversion; Action must be downstream.
- Option D, place it under Thinking or Verification: rejected because neither
  owns authorization.

Selected future physical home: `aether/core/governance.py` (Option B). The
existing `aether/core/__init__.py` already establishes the package; no new
`__init__.py` is required. This file is not created in Milestone 87A.

## 20. Import and Dependency Direction

The selected future direction is:

`aether.thinking.policy` -> proposal value passed by caller

`aether.verification.risk` and `aether.identity.guard` -> evidence values passed
by caller

`aether.core.loop` (Coordination) -> imports and invokes
`aether.core.governance`

`aether.core.governance` -> returns the authoritative compatibility envelope

Action approval builder, response assembly, trace, and Timeline -> downstream
consumers called by the loop

`aether.core.governance` must not import `aether.core.loop`, Interface, routers,
Action executors, approval queue, Timeline, or persistence. The Action
compatibility facade may import Core Governance. This direction avoids a cycle:
the loop imports Governance; Governance imports neither loop nor Action; the
legacy Action facade imports Governance.

## 21. Milestone 87B Migration Rule

Selected migration: move the authoritative compatibility logic atomically to
`aether/core/governance.py`, redirect the production core-loop importer to that
module, and convert `aether/action/policy_gate.py` into a thin compatibility
facade that delegates to the single Core Governance implementation while
preserving its existing signature for direct importers/tests.

The future Governance entry point must receive the Thinking proposal and the
raw existing risk/identity evidence plus requested action/context. Those direct
evidence parameters add provenance, not new policy behavior. The compatibility
facade supplies absent evidence as `None` because its historical signature did
not receive them.

Exact tentative Milestone 87B changed-file matrix:

- create `aether/core/governance.py`;
- modify `aether/core/loop.py` only at the authorization import/invocation and
  direct existing evidence handoff;
- modify `aether/action/policy_gate.py` into the compatibility facade;
- modify
  `tests/test_milestone_87_core_governance_authorization_boundary.py` to lock
  the implemented home/delegation while preserving behavioral cases;
- modify `PROGRESS.md` only after all 87B validation gates pass;
- create only the separately authorized external 87B summary outside Git.

There must be no second live decision engine, fallback engine, or silent
behavior change. No existing test needs to be weakened or deleted.

## 22. Boundary-Test Contract

`tests/test_milestone_87_core_governance_authorization_boundary.py` locks:

- this path, H1, and exact 24-section structure;
- Architecture v0.3.0 ownership and Milestone 85 continuity;
- exact production call site and complete direct-importer inventory;
- current gate signature, envelope keys, types, defaults, warnings, and
  malformed/block/approval/response-only/legacy behavior;
- Thinking proposal non-authority and direct evidence provenance;
- `allowed` separation from execution and approval state;
- approval request/pending-record non-execution;
- production `/chat` no-execution AST invariants and absence of executor calls;
- exact selected home, dependency direction, compatibility-facade migration,
  and no-parallel-gate rule;
- no persistence/API/router/model/runtime implementation in 87A;
- OpenAPI 304/108 and api_server 8/23/0 records;
- Milestone 87 remains open and Milestone 88 does not start automatically.

The suite uses only static inspection and pure deterministic gate/builder calls.
It does not use TestClient, invoke endpoints, write queues/Timeline/private
state, execute a tool/action, modify configuration, or access the network.

## 23. Protected-Core and Non-Goals

Protected and unchanged in Milestone 87A: all `aether/*`, all existing tests,
Constitution, Architecture, README, existing architecture records, API models,
routers, endpoints, queues, stores, schemas, `docs/history`, dependency files,
and runtime/private data.

Non-goals include full Constitution Runtime Enforcement, full Cognitive Signal
Arbitration, ASC, Resource Observation/Governance, Temporal Context, Controlled
Background Continuity, Observation aggregation, Economic Capability, behavior
changes, policy tightening, execution enablement, and any interface or
persistence expansion.

## 24. Milestone 87 Completion and Closure Rule

Milestone 87A completes locally only when this record and its new contract suite
pass every focused, architecture, Observation, protected-core, Constitution,
OpenAPI, structural, isolation, drift, and full-suite gate, after which
PROGRESS.md may be updated truthfully. It remains unfinalized and uncommitted.

Milestone 87 remains open after 87A. Human/project-manager review is the next
authorized action. Only explicit acceptance may authorize Milestone 87B — Core
Governance Authorization Decision-Envelope Extraction. Milestone 87 closes only
after its separately authorized extraction and finalization sequence. Milestone
88 does not start automatically.
