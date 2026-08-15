# Milestone 96A Authoritative Goal / TaskContext / Canonical Plan Boundary

Classification: DESIGN / OWNERSHIP BOUNDARY ONLY

Status: DESIGN BOUNDARY BUILD COMPLETE LOCALLY / PENDING PM REVIEW / GIT FINALIZATION

This record defines semantic ownership and identity boundaries. It does not
implement runtime objects, transitions, storage, APIs, or execution.

Explicit exclusions:

- NO RUNTIME IMPLEMENTATION
- NO API
- NO PERSISTENCE
- NO GENERIC ACT
- NO RESTRICTED-READ RETROFIT
- NO OBSERVATION INTAKE
- NO VERIFICATION AGGREGATION
- NO CRITIC
- NO REPAIR
- NO LEARNING
- NO RETRY
- NO BACKGROUND EXECUTION
- NO SECOND CAPABILITY
- NO COMMIT, TAG, OR PUSH

## 1. Purpose and Preserved Direction

M96A defines the authoritative semantic boundary for:

```text
Goal
  -> Task
  -> authoritative TaskContext
  -> Think proposal
  -> canonical Plan
  -> canonical PlanStep
  -> Governance evaluation
  -> STOP BEFORE GENERIC ACT
```

The first unproven canonical seam remains:

```text
Think -> Plan
```

This record establishes ownership and non-aliasing. It does not claim that
the runtime objects or transitions exist today.

The preserved architecture rules are:

- Thinking proposes.
- Core Governance authorizes.
- Verification supplies evidence.
- Action executes only within authorization.
- Core Coordination owns Task continuity and current-context selection.
- Time provides context, not authority.
- Context is distinct from Working Memory, Timeline, Loop Trace, and
  long-term Memory.

## 2. Goal Contract

Semantic owner: **Goal Intake under Human Authority**.

Goal is the human objective or intention from which one or more bounded Tasks
may be formed. Candidate fields are:

- `goal_id` — distinct Goal identity; never Goal text or a session identifier.
- `goal_text` — bounded human-provided objective or intention.
- `authority_reference` — accepting human-authority provenance; not an
  `approval_id` alias.
- `goal_status` — proposed, accepted, active, paused, completed, cancelled,
  expired, or rejected.
- `created_at` and `accepted_at`.
- `temporal_scope_reference` — a reference to Time semantics.
- `revision` — explicit Goal revision.
- `requested_outcome` — optional human-intent input.
- `goal_constraints` — optional human-stated constraints.

The Goal contract locks:

- `goal_id != goal_text`.
- `goal_id != session_id`.
- `authority_reference != approval_id` as an identity alias.
- Goal requested outcome is **NOT** authoritative Plan completion criteria.
- A Goal may be accepted before authoritative execution completion criteria
  are known.

Goal does not own:

- authoritative Plan completion criteria;
- authoritative Plan failure or blocked criteria;
- Plan readiness;
- PlanStep criteria;
- Action-attempt identity;
- Observation identity;
- Verification identity;
- execution authorization.

The explicit semantic rule is:

```text
Goal requested_outcome != authoritative Plan completion criteria
```

## 3. Task Contract

Semantic owner: **Core Coordination**.

Task is a bounded work or execution unit formed under a Goal. Candidate fields
are:

- `task_id`;
- explicit `goal_id` parent reference;
- `task_status` and lifecycle timestamps;
- bounded `task_scope` and `task_constraints` references or inputs;
- `task_context_id` as the current authoritative context reference;
- `current_plan_id` when a canonical Plan is selected;
- `current_plan_step_id` when a canonical PlanStep is selected;
- `completion_criteria_reference`;
- `governance_context_reference`;
- `time_context_reference`;
- `revision`.

`completion_criteria_reference` must resolve only to canonical Plan criteria
or canonical PlanStep criteria. Task must not define a competing local
authoritative criteria payload.

Task does not own Goal authority, Plan criteria, PlanStep criteria, Observation
facts, Verification status, approval state, or Action-attempt identity.

## 4. Authoritative TaskContext Contract

Semantic owner: **Core Coordination**.

TaskContext is the single authoritative current-state envelope for one Task at
one context revision. Candidate fields are:

- `task_context_id`;
- `task_id` and `goal_id` explicit references;
- `context_revision` and lifecycle timestamps;
- `task_status`;
- `execution_phase` snapshot or reference;
- `current_plan_id` and `current_plan_step_id` selected canonical references;
- `completion_criteria_reference`;
- `governance_context_reference`;
- approval and permission references;
- `time_context_reference`;
- `working_memory_references`;
- call-local `observation_references` when applicable;
- `verification_references` when applicable;
- context-selection and context-switch metadata.

TaskContext carries state and references only. It does not own a completion
criteria payload, execution authorization, Memory, Working Memory, a
scheduler, a queue, or global mutable task state.

`completion_criteria_reference` must resolve to canonical Plan or canonical
PlanStep completion criteria. It must not contain independently authoritative
criteria. TaskContext criteria are **REFERENCE ONLY**.

## 5. ASC Cardinality and Selection

The Authoritative Shared Cognitive Context (ASC) is one architecture framework,
not one global mutable task object.

- One ASC architecture framework exists.
- Every active Task has exactly one authoritative TaskContext.
- Every reasoning turn has exactly one selected current TaskContext.
- Waiting and paused Tasks may retain separate TaskContexts.
- Background is a separate future capability boundary and is not implemented.
- Context selection and switching are explicit Core Coordination operations.
- Governance constrains authority-sensitive selection and switching.
- No silent merge, overwrite, fallback adoption, or cross-task context
  transfer is allowed.
- A stale, expired, cancelled, superseded, or blocked context is not silently
  revived.

The ASC is not:

- Working Memory;
- Timeline or Loop Trace;
- long-term Memory;
- a database or persistence store;
- a scheduler or queue;
- an authorization source;
- a new cognitive organ or agent.

## 6. Canonical Plan Contract

Semantic owner: **canonical Plan stage / planning contract**.

The canonical Plan is the authoritative planning-stage contract selected for a
TaskContext. Candidate fields are:

- `plan_id`;
- `goal_id`, `task_id`, and `task_context_id` explicit parent references;
- `plan_status`;
- ordered `plan_step_ids`;
- authoritative `completion_criteria`;
- authoritative `failure_criteria`;
- authoritative `blocked_criteria`;
- `plan_not_ready_reason`;
- `plan_revision`;
- creation and selection timestamps;
- bounded proposal/evidence references;
- Governance constraint references.

Allowed `plan_status` values are:

```text
proposed
not_ready
ready
selected
superseded
blocked
completed
cancelled
rejected
```

The canonical Plan owns:

- authoritative Plan completion criteria;
- authoritative Plan failure criteria;
- authoritative Plan blocked criteria.

The canonical Plan must derive these criteria from the Goal, Task, applicable
constraints, and planning evidence. If authoritative criteria cannot be
derived, Plan status is `not_ready` and `plan_not_ready_reason` is required.
Generic Act is then **NO**.

Plan readiness and Plan selection are not execution authorization. A Plan may
describe an action without executing it.

Existing tool plans, simulation plans, apply-executor plans, verification
plans, repair plans, and other UUID-bearing local plans remain
capability/workflow-specific. They must not be silently relabeled as the
canonical Plan.

## 7. Canonical PlanStep Contract

Semantic owner: **canonical Plan / PlanStep contract**.

PlanStep is an owned semantic unit in a canonical Plan. Candidate fields are:

- `plan_step_id`;
- `plan_id` and `task_context_id` explicit parent references;
- sequence and dependency references;
- `step_type`;
- bounded proposal or Action reference;
- authoritative `step_completion_criteria`, or explicit
  `no_applicable_expectation`;
- authoritative step failure and blocked criteria where applicable;
- `step_status`;
- Governance requirement references;
- Time scope references.

PlanStep owns authoritative step criteria or the explicit
`no_applicable_expectation` marker. PlanStep identity is not ordinal position,
Action attempt, Observation, Verification, approval, execution record, or
collector contract. A caller-supplied `plan_step_id` is not proof of canonical
PlanStep identity.

Retry semantics, if ever separately authorized, must create a distinct
`action_attempt_id`; an existing PlanStep ID cannot be used as an Action
identity.

## 8. Exact Ownership Matrix

Each category has exactly one authoritative owner. Read access, proposal, or
transport does not imply write authority.

| Category | Exactly one authoritative owner | Allowed contributors | Forbidden alias or mistaken owner |
|---|---|---|---|
| Human objective/intention | Goal Intake | Human Authority, Interface | Working Memory, `session_id` |
| Goal identity | Goal Intake | Core Coordination references | `goal_text`, `approval_id` |
| Goal authority/provenance | Goal Intake | Human Authority supplies event | `approval_id`, `session_id` |
| Goal status/revision | Goal Intake | Core Coordination reports task relation | Task or Plan status |
| Requested outcome and Goal constraints | Goal Intake | Human Authority supplies; Thinking interprets | Plan completion criteria |
| Task identity/lifecycle | Core Coordination | Goal Intake requests; Thinking proposes scope | `goal_id`, `session_id`, `plan_id` |
| TaskContext identity/lifecycle | Core Coordination | stage inputs; Governance constrains | `session_id`, `approval_id` |
| Current TaskContext selection/switch | Core Coordination | Core Governance constrains | Interface, Time, `session_id` |
| Canonical Plan semantics | canonical Plan stage / planning contract | Thinking proposes | local plan IDs |
| Canonical Plan completion/failure/blocked criteria | canonical Plan stage / planning contract | Goal/Task inputs, Thinking, Verification | Goal `requested_outcome`, TaskContext payload |
| Canonical PlanStep identity/criteria | canonical Plan / PlanStep contract | Thinking proposes | Observation caller, ordinal alone |
| TaskContext completion criteria reference | Core Coordination | Plan resolves target | local criteria payload |
| Permission / authorization policy | Core Governance | Thinking proposes; Verification supplies evidence | Plan readiness |
| Operational risk for authorization | Core Governance | Verification supplies evidence | Thinking confidence |
| Temporal facts/scope | Time | AetherOS supplies mechanisms and raw clock facts | timestamp as authority |
| Working-memory content | Memory | loop stages write bounded events | Goal, Plan, criteria |
| Action-attempt identity | Action occurrence contract | Core Coordination binds call | `plan_step_id`, file-access ID |
| Approval state | Human Authority / Core Governance boundary | Interface submits decision | Goal, Plan, PlanStep |
| Observation facts/identity | Observation producer boundary | Action supplies result | Action or PlanStep alias |
| Verification evidence/status/identity | Verification contract | Action/Observation supply facts | approval or Observation alias |
| Persistence eligibility/privacy | Core Governance | producer and consumer prove need | presence of a record store |
| Consumer identity/use | concrete downstream consumer contract | producer supplies compatible data | speculative future consumer |

## 9. Governance and Time Separation

Thinking proposes. Governance authorizes. Verification supplies evidence. Action
executes only within authorization.

Core Governance owns Constitution enforcement, permission scope, privacy
boundaries, safety prohibitions, mandatory verification, approval boundaries,
and operative risk classification for authorization.

Core Governance does not own Goal identity, Task continuity, canonical Plan
semantics, Time facts, Observation facts, or Verification evidence.

Time owns clock facts, timestamp semantics, temporal scope, freshness,
duration, deadlines, expiry, and decision-time references. Time provides
context, not authority. Time does not select a Goal, create a Task, own a
Plan, grant permission, revive an approval, or authorize an Action.

AetherOS supplies timing mechanisms and raw clock facts. AetherOS does not own
temporal reasoning.

## 10. Lifecycle and Stop Boundary

The future recommended lifecycle is:

1. Goal Intake receives explicit human objective/intention.
2. Goal Intake accepts or rejects the Goal under Human Authority.
3. The Goal may be accepted before completion criteria are known.
4. Core Coordination forms a bounded Task and one authoritative TaskContext.
5. Core Coordination selects exactly one TaskContext for the reasoning turn.
6. Understand and Think read context and produce proposals.
7. Canonical Plan derives authoritative completion, failure, and blocked
   criteria and PlanSteps, or returns `not_ready`.
8. Core Coordination binds selected Plan and PlanStep references to the
   TaskContext.
9. Core Governance evaluates the applicable authorization envelope.
10. **STOP BEFORE GENERIC ACT.**

No implementation of these transitions is included in M96A.

## 11. Frozen M94/M95 Runtime Boundary

M96A does not reopen, extend, or retrofit M94/M95.

- Capability: `file.restricted_read`.
- Governed capability count: `1`.
- Generic `/chat` execution authority: **NO**.
- Restricted-read Observation: **CALL_LOCAL / AUTHORITATIVE**.
- Restricted-read Verification: **CALL_LOCAL / AUTHORITATIVE**.
- Persistent restricted-read Observation: **NONE / NOT JUSTIFIED**.
- Restricted-read persistence eligibility: **BLOCKED**.
- Observation Intake caller: **NONE / NOT PROVEN**.
- Verification Aggregation: **NOT WIRED**.
- Critic: **NOT WIRED**.
- Repair: **NOT WIRED** as a canonical trigger.
- Learning: **NOT WIRED**.
- Retry: **NO**.
- Background execution: **NO**.
- Generic executor: **NO**.
- Second capability: **NO**.
- Provenance-envelope runtime: **NO**.
- Durable restricted-read consumer: **NONE**.

No Goal, Task, TaskContext, Plan, or PlanStep identity is retrofitted into the
existing restricted-read path. M95's negative durable-consumer result is not a
runtime defect.

## 12. Identity Non-Aliasing

These are distinct semantic identities:

```text
goal_id != task_id != task_context_id != plan_id != plan_step_id !=
approval_id != action_attempt_id != observation_id != verification_id !=
session_id
```

Absence is allowed when the semantic object does not yet exist. Fabrication is
not allowed. Missing identities must not be filled with `session_id`,
`approval_id`, file-access ID, request ID, generic record ID, timestamp, hash,
or another UUID merely because one is available.

## 13. Future Slices and Build Boundary

Future slices are recommendations only and are not authorized by this record:

- Slice A: contract, ownership, and static design lock.
- Slice B: narrow in-memory Core Coordination TaskContext foundation.
- Slice C: bounded Receive Goal -> Think -> Plan path, stopping before generic
  Act.
- Slice D: separate downstream consumer-proof review.

The minimum first Build candidate path set is exactly:

```text
docs/architecture/MILESTONE_96A_AUTHORITATIVE_GOAL_TASK_PLAN_BOUNDARY.md
```

The first Build is documentation and static design-lock scope only. It has no
production runtime file, API, persistence, route, schema, capability,
Observation Intake caller, provenance envelope, or restricted-read binding.
`PROGRESS.md` and the canonical ledger test are current-ledger reconciliation
paths authorized by the PM scope; no fifth path is allowed.

M96A runtime implementation: **NOT AUTHORIZED**.

## 14. Verification and Non-Authorization

The design lock must remain static/document-content-only. It must not import
Aether runtime modules, invoke endpoints, use a client, write private data,
execute Action, or create persistence.

The authorized four-path Build must preserve:

- production diff empty;
- OpenAPI 306 paths / 112 schemas;
- api_server 8 direct `@app` routes / 23 `include_router` / 0 direct
  `/action/*`;
- protected README, Constitution, and Architecture files unchanged;
- M95 closure tag unchanged;
- no runtime implementation or Git lifecycle.

The local Build remains pending PM review and Git finalization. It does not
claim a future commit, tag, push, or PM acceptance.
