# Milestone 98A Canonical Goal-to-Plan Runtime Consumer Proof Boundary

Classification: STRICT READ-ONLY DESIGN / DISCOVERY / CONSUMER-PROOF

Status: DESIGN / DISCOVERY ONLY / COMPLETE LOCALLY / GIT DURABILITY NOT CLAIMED / PM BUILD-SCOPE REVIEW PENDING

This record audits whether a truthful production runtime consumer exists for
the canonical M96 Goal-to-Plan cognitive path. It does not implement runtime
integration, modify production code, wire `/chat`, authorize Generic Act, or
authorize any Build.

The binding architecture invariant remains:

```text
GOVERNANCE_EVALUATION != EXECUTION_AUTHORIZATION
```

## 1. Current Git State

- Branch: `main`.
- HEAD: `4d45dbcc7613c746cb7b84279d95a46deaab0382`.
- `main`: `4d45dbcc7613c746cb7b84279d95a46deaab0382`.
- `origin/main`: `4d45dbcc7613c746cb7b84279d95a46deaab0382`.
- Remote `main`: `4d45dbcc7613c746cb7b84279d95a46deaab0382`.
- Worktree at read start: clean and unstaged.
- M97A commit: `4d45dbcc7613c746cb7b84279d95a46deaab0382`.
- M97A tag: `milestone-97A-governed-generic-act-consumer-authorization-boundary`.
- M97A: FINALIZED / COMMITTED / TAGGED / PUSHED / PM-ACCEPTED.
- Architecture version: `0.3.0`.
- OpenAPI baseline: `306 paths / 112 schemas`.
- api_server baseline: `8 direct @app routes / 23 include_router / 0 direct /action/*`.

M98A creates only this design record and its static/document-contract lock.
No commit, tag, push, production edit, existing-test edit, or runtime-data edit
is authorized by this milestone.

## 2. Current Authority

M96 remains CLOSED / GIT-DURABLE / PM-ACCEPTED. M97A established:

- consumer-proof result: `D_NO_REAL_CONSUMER_CURRENTLY_JUSTIFIED`;
- selected Generic Act model: `MODEL_D_NO_GENERIC_ACT_YET`;
- production Generic Act consumer: `NONE`;
- Generic Act: `NOT_IMPLEMENTED`;
- Generic Act integration: `NOT_AUTHORIZED`;
- Generic Act authority: `NOT_GRANTED`;
- M98: `NOT_AUTHORIZED` before this design/discovery review.

M98A is a separate consumer-proof review. It does not inherit a runtime
consumer from M97A and does not convert M97A's no-Generic-Act decision into a
runtime integration decision.

## 3. Exact M98A Objective

Determine whether an existing production component outside the current
process-local seam truthfully needs to consume all or the necessary canonical
parts of:

```text
Goal
-> Task
-> authoritative TaskContext
-> selected TaskContext
-> ThinkingProposal
-> canonical Plan
-> selected canonical PlanStep
-> Core Governance Evaluation
-> STOP BEFORE GENERIC ACT
```

The consumer-proof test is behavioral, not nominal. A real consumer must have
a current production need for canonical identity, ownership, selection,
revision, lifecycle, and result semantics. Tests, documentation, unused
helpers, legacy objects with similar names, and future architectural desire do
not prove a consumer.

## 4. Canonical M96 Producer Inventory

| Producer or owner | Current production evidence | M98A finding |
|---|---|---|
| Goal Intake | `aether/core/goal.py:155-186` stores proposed and accepted `Goal` objects in an in-memory process-local registry. | Real process-local Goal owner; no external runtime entrypoint. |
| Core Coordination Goal operations | `aether/core/task_context.py:339-370` delegates Goal creation, registration, acceptance, and lookup. | Real canonical owner; no `/chat` or API caller. |
| Task and first TaskContext | `aether/core/task_context.py:372-416` creates an accepted-Goal-bound `Task` and authoritative `TaskContext` atomically. | Real process-local producer; selection remains explicit. |
| TaskContext selection | `aether/core/task_context.py:453-483` selects one current context and records selection history. | Real process-local coordination state; not wired to the current chat runtime. |
| Canonical Plan | `aether/core/task_context.py:561-596` validates binding and creates an immutable process-local `Plan`. | Real producer; no production caller outside Core Coordination. |
| ThinkingProposal materialization | `aether/core/task_context.py:598-632` validates a ready proposal and materializes a canonical Plan. | Consumer seam exists process-locally; no production proposal producer feeds it. |
| Canonical PlanStep | `aether/core/task_context.py:764-820` creates and orders a PlanStep under one current Plan. | Explicit process-local operation; not reached by `/chat`. |
| Canonical Governance request/evaluation | `aether/core/task_context.py:638-742` builds the immutable request and calls `aether.core.governance.evaluate_canonical_plan_governance`. | Real caller and evaluator seam; result returns to the immediate caller and stops. |

The canonical producers are therefore real as a process-local foundation, but
their existence does not establish a second runtime consumer.

## 5. Runtime Consumer Inventory

| Candidate production component | What it actually consumes | Canonical M96 consumer proof |
|---|---|---|
| `POST /chat` | `ChatRequest.text` or legacy `message`, then `AetherRuntime.process_chat()` and a legacy loop result. | `NO_CONSUMER`: no Goal, Task, TaskContext, ThinkingProposal, Plan, PlanStep, or canonical Governance result. |
| `AetherRuntime.process_chat` | Text, session metadata, Working Memory, and the legacy chat loop. | `NO_CONSUMER`: delegates to `run_core_chat_loop`. |
| `aether/core/loop.py` | Perception, risk evidence, tool suggestion, Thinking policy dictionary, authorization envelope, approval request, timeline, and response fields. | `NO_CONSUMER`: no canonical Goal-to-Plan call or object. |
| Thinking policy | Perception/risk/tool dictionaries; policy returns a dictionary and never calls an external model/API. | `NO_CONSUMER`: it does not construct `ThinkingProposal`. |
| Working-memory Goal route | `GoalRequest.goal` passed to a Working Memory service. | `NO_CONSUMER`: it does not call `GoalIntake` or create canonical Goal identity. |
| Restricted-read resume/execution | Exact `file.restricted_read` action, approval record, session binding, fingerprint, capability-specific scope, dispatch, and verification. | `NO_CANONICAL_CONSUMER`: valid real execution surface, but not a consumer of canonical Plan/PlanStep Governance. |
| Legacy tool-plan route | Persisted mutable tool invocation plans from text, inferred tool, verification plan, and approval fields. | `NO_CANONICAL_CONSUMER`: similar name, separate contract and storage. |
| Tests and documents | Assertions and recorded architectural claims. | `TEST_ONLY_CONSUMER` or `DOCUMENT_ONLY_REFERENCE`, never production proof. |

No current production component outside Core Coordination consumes the
canonical Goal-to-Plan path. The historical statement remains factually true:

```text
Think -> Plan process-local consumer: SATISFIED
Think -> Plan consumer outside the process-local seam: NOT YET SATISFIED
```

## 6. `/chat` Audit

### 6.1 Entry and object flow

`aether/interface/api_server.py:223-299` accepts `ChatRequest.text` or the
legacy `message` field. It calls `runtime.process_chat()` and serializes the
returned dictionary into `ChatResponse`.

`aether/core/runtime.py:99-113` passes text, Working Memory, session ID,
metadata, and a forced-false tool-execution flag to
`run_core_chat_loop()`.

`aether/core/loop.py:28-332` performs this current path:

```text
text
-> perception
-> identity integrity check
-> time state
-> Working Memory event recording
-> risk classification
-> legacy tool suggestion
-> Thinking policy dictionary
-> authorization envelope
-> approval request/queue
-> no tool execution
-> timeline event
-> textual response
```

The returned `/chat` response contains perception, risk, suggested-tool,
Thinking-policy, authorization-envelope, approval, Working Memory, timeline,
and response fields. It does not contain or create canonical Goal, Task,
TaskContext, ThinkingProposal, Plan, PlanStep, or
`CanonicalPlanGovernanceEvaluation` objects.

### 6.2 Goal representation

The `/chat` request is text-first and has no canonical Goal authority or Goal
identity. The separate `POST /memory/working/goal` route accepts a
`GoalRequest`, but `aether/interface/routers/memory_routes.py:46-48` sends it
to Working Memory rather than `GoalIntake`. A Working Memory goal string is not
a canonical accepted Goal.

### 6.3 Divergence and duplication

The current `/chat` loop is a safe legacy skeleton. It deliberately keeps
execution disabled and uses `evaluate_authorization_envelope`, not the M96
canonical Plan Governance evaluator. Connecting it directly to the canonical
seam would require new semantics for human Goal authority, Task creation,
context selection, ThinkingProposal production, criteria, PlanStep selection,
and lifecycle transitions. Those semantics are not currently supplied by the
route or loop.

Therefore `/chat` is not a truthful current consumer. Wiring it now would be a
new architecture decision, not a cleanup of an already-existing consumer. It
would also risk making the interface or legacy loop a competing cognitive
authority and would duplicate current Working Memory, policy, tool, approval,
and timeline behavior before a consumer contract exists.

## 7. Core Loop Audit

`aether/core/loop.py` is the implementation behind the current HTTP chat
runtime, not an independent canonical cognitive runtime. Its inputs and
outputs remain dictionaries and legacy records. It has no import or call to:

- `GoalIntake`;
- `CoreCoordination.create_task`;
- `CoreCoordination.select_context`;
- `ThinkingProposal` production;
- `materialize_thinking_proposal`;
- `create_plan` or `create_plan_step`;
- `evaluate_canonical_plan_governance`.

The loop's `execution_allowed` is a projection from the legacy authorization
envelope. It is not canonical Plan Governance authorization and cannot become
such by field-name similarity. The loop also sets `tool_execution_allowed` and
`tool_executed` false and does not dispatch Action.

Core loop consumer status:

```text
NO_CANONICAL_GOAL_TO_PLAN_RUNTIME_CONSUMER
```

## 8. ThinkingProposal Producer Audit

`aether/thinking/proposal.py:96-177` defines an immutable, non-authoritative
`ThinkingProposal` contract with required Goal/Task/TaskContext identity,
revisions, criteria, state, and provenance. This is a production source class,
not proof of a production producer.

Current facts:

- `aether/thinking/policy.py:1-6` explicitly states that the policy layer does
  not execute tools or call external APIs.
- `aether/thinking/policy.py:11-132` returns a policy dictionary for the chat
  path, not a `ThinkingProposal`.
- The only production materialization seam is
  `CoreCoordination.materialize_thinking_proposal()` at
  `aether/core/task_context.py:598-632`.
- No current Thinking provider, factory, API, persistence path, or `/chat`
  caller creates a truthful `ThinkingProposal`.
- Existing tests construct proposals for the process-local contract; tests are
  not production producers.

An adapter from the current policy dictionary to `ThinkingProposal` would have
to invent or obtain at least accepted Goal identity, Task identity,
authoritative TaskContext identity and revision, explicit criteria, proposal
state, proposal revision, and complete provenance categories. The current
dictionary does not contain those semantics. No real downstream consumer
currently requires such an adapter, so creating it would fail the consumer-proof
gate and would be premature.

ThinkingProposal production status:

```text
Contract class: PRESENT
Production producer/provider: ABSENT
/chat wiring: ABSENT
Persistence: ABSENT
External runtime consumer: ABSENT
```

## 9. Legacy Versus Canonical Paths

The repository contains several separate meanings of planning and proposal:

| Surface | Current contract | Why it is not M98A consumer proof |
|---|---|---|
| Canonical `Plan` / `PlanStep` | Immutable Core Coordination process-local objects in `task_context.py`. | No external production caller. |
| Tool invocation plan | Mutable dictionaries persisted by `aether/action/tool_planner.py:187-344`; exposed by tool-plan routes. | Text/tool/verification contract, not Goal/Task/TaskContext/Plan Governance. |
| Verification plan | Risk-derived dictionary used by legacy services. | Evidence/planning helper, not canonical Plan. |
| Patch, repair, apply, simulation plans | Action-specific records and proposal workflows. | Separate bounded contracts with no canonical M96 input. |
| `/chat` Thinking policy | Policy dictionary from perception, risk, and tool suggestion. | No ThinkingProposal identity, criteria, or canonical context. |
| Restricted-read execution | Capability-specific approval, fingerprint, scope, dispatch, and verification. | Real action-specific consumer, not canonical Goal-to-Plan consumer. |

`aether/action/tool_planner.py:250-344` persists a tool invocation plan after
inferring a tool and verification plan. `aether/interface/routers/tool_registry_plan_routes.py:95-117`
exposes that separate plan. This is naming overlap, not shared canonical
authority.

The restricted-read path is also real but bounded separately:

- `aether/interface/routers/file_routes.py:39-54` exposes resume and approved
  read routes.
- `aether/action/services/restricted_file_read_execution_service.py:79-148`
  validates the stored action, fingerprint, session binding, and approval.
- `aether/core/coordination.py:33-122` performs the capability-specific
  attempt, dispatch, and verification.

Neither path consumes canonical Plan/PlanStep Governance evaluation. Neither
may be generalized by analogy.

## 10. Ownership Analysis

| Concern | Current owner | M98A finding |
|---|---|---|
| Human Goal authority and Goal acceptance | Human Authority through Goal/Core Coordination contract | No `/chat` entrypoint supplies this canonical contract. |
| Goal, Task, TaskContext continuity | Core Coordination | Correct process-local owner; no external runtime consumer. |
| Thinking proposal content | Thinking | Contract exists; producer is absent. |
| Plan and PlanStep continuity/selection | Core Coordination | Process-local creation and selection only. |
| Governance policy and canonical evaluation | Core Governance; Core Coordination assembles the request | Evaluation is non-authorizing and stops before Generic Act. |
| Verification evidence | Verification surfaces | Supplies evidence; does not become canonical execution authority. |
| Interface input/output | Interface | Must not become cognitive authority; current `/chat` remains separate. |
| Capability-specific execution | Action services and Core Governance boundaries | Restricted-read is separate and cannot prove a canonical consumer. |

The repository has one coherent owner for the process-local canonical seam. It
does not have a second owner that needs to consume the seam at runtime.

## 11. Consumer-Proof Decision

```text
D_NO_REAL_RUNTIME_CONSUMER_CURRENTLY_JUSTIFIED
```

Evidence-backed reasoning:

1. Core Coordination is the real process-local producer, owner, and immediate
   caller of canonical Governance evaluation.
2. The current `/chat` runtime does not create or consume canonical Goal,
   Task, TaskContext, ThinkingProposal, Plan, PlanStep, or Governance result.
3. The current Thinking path has no production `ThinkingProposal` producer.
4. Restricted-read and legacy tool/action surfaces have separate contracts and
   do not consume canonical Plan Governance.
5. No production behavior currently requires an external consumer of the
   canonical chain.

The process-local M96 consumer remains SATISFIED. The external runtime
consumer gap remains NOT YET SATISFIED.

## 12. Candidate Model Comparison

| Model | Decision | Evidence-based reason |
|---|---|---|
| `MODEL_A_CHAT_AS_CANONICAL_COGNITIVE_CONSUMER` | REJECTED | `/chat` is text/Working-Memory/legacy-policy based, has no canonical Goal authority or proposal producer, and wiring it now would add interface-to-cognition authority and duplicate state. |
| `MODEL_B_CORE_LOOP_AS_CANONICAL_COGNITIVE_CONSUMER` | REJECTED | The current core loop is the same legacy `/chat` loop, not a canonical Goal-to-Plan runtime. It lacks the required inputs and would need an invented adapter. |
| `MODEL_C_NEW_COORDINATION_RUNTIME_ENTRYPOINT` | NOT JUSTIFIED | A dedicated entrypoint could be a future ownership-preserving design, but there is no proven production caller, use case, proposal producer, or runtime boundary requiring it now. |
| `MODEL_D_NO_RUNTIME_CONSUMER_YET` | SELECTED | It is the only model supported by current production evidence and preserves existing ownership without speculative integration. |

Selected model:

```text
MODEL_D_NO_RUNTIME_CONSUMER_YET
```

## 13. Required Future Prerequisites

A separately authorized future runtime design must first provide:

1. A concrete production use case and one owning runtime component.
2. A truthful caller for accepted Goal authority, Task creation, and explicit
   TaskContext selection.
3. A real ThinkingProposal producer with complete criteria, state, revision,
   identity, and provenance semantics.
4. Exact Goal, Task, TaskContext, Plan, and selected PlanStep identity and
   revision binding across the consumer boundary.
5. Defined process lifetime, persistence, restart, selection, cancellation,
   stale-state, and failure behavior if the consumer crosses process scope.
6. A canonical Governance caller that preserves
   `GOVERNANCE_EVALUATION != EXECUTION_AUTHORIZATION`.
7. A consumer output contract that does not silently authorize Generic Act or
   Action execution.
8. Focused static, runtime, and safety tests plus regression evidence under a
   separately authorized Build scope.
9. Explicit PM approval before any production code, API, persistence, or
   `/chat` change.

These are prerequisites, not implementation instructions or authorization.

## 14. Explicit Non-Goals

M98A does not implement or authorize:

- Goal/Task/TaskContext runtime integration outside the process-local seam;
- a ThinkingProposal producer, adapter, provider, or persistence path;
- Plan or PlanStep runtime wiring;
- `/chat` wiring or interface redesign;
- Core loop replacement or new runtime entrypoint;
- Generic Act, Action dispatch, tool execution, or execution authorization;
- a new capability or generic capability registry;
- Observation Intake, Persistent Observation, Verification Aggregation,
  Critic, Repair, Learning, retry, scheduler, background execution, or wake
  behavior;
- changes to restricted-read or existing action-specific contracts;
- M97B, M98 runtime Build, or any successor milestone;
- `PROGRESS.md`, README, Constitution, Architecture, production code, existing
  tests, runtime data, commit, tag, or push.

## 15. Build Authorization Gate

```text
Runtime Build: NOT YET JUSTIFIED
```

M98A proves the absence of a real external runtime consumer. It does not
authorize a runtime Build and does not select `/chat`, Core Loop, or a new
Coordination entrypoint for implementation. Any future Build requires a new
PM decision after a truthful consumer and complete boundary contract are
identified.

Generic Act state remains:

```text
Generic Act: NOT_IMPLEMENTED
Generic Act integration: NOT_AUTHORIZED
Generic Act authority: NOT_GRANTED
```

## 16. Next-Step Gate

The two M98A files are complete locally when the static/document lock passes.
That result is not Git durability, Build authorization, or runtime approval.

```text
Next authorized action: HUMAN/PROJECT-MANAGER M98A BUILD-SCOPE REVIEW
```

No commit, tag, push, PROGRESS update, runtime Build, Generic Act, or next
milestone is authorized by this record.
