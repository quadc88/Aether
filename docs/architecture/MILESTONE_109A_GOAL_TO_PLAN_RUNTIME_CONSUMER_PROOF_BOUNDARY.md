# Milestone 109A Goal-to-Plan Runtime Consumer Proof Boundary

Classification: STRICT READ-ONLY DESIGN / DISCOVERY / CONSUMER-PROOF

Status: DESIGN / DISCOVERY ONLY / COMPLETE LOCALLY / GIT DURABILITY NOT CLAIMED / PM REVIEW PENDING

M109A audits whether a truthful production runtime consumer now exists for the
canonical Goal-to-Plan seam. It does not implement runtime integration, create
a ThinkingProposal producer, wire `/chat`, authorize Plan execution, authorize
Generic Act, or change any existing production contract.

The binding architecture invariant remains:

```text
GOVERNANCE_EVALUATION != EXECUTION_AUTHORIZATION
```

## 1. Current Git and Runtime Baseline

At M109A review start:

- branch: `main`;
- HEAD: `131c921ce263ef8ad83003f625058ba77568dea9`;
- local `main`: `131c921ce263ef8ad83003f625058ba77568dea9`;
- `origin/main`: `131c921ce263ef8ad83003f625058ba77568dea9`;
- remote `main`: `131c921ce263ef8ad83003f625058ba77568dea9`;
- worktree: clean before the M109A write set;
- `git diff --check`: clean;
- OpenAPI: `306 paths / 112 schemas`;
- `api_server`: `8 direct @app routes / 23 include_router / 0 direct /action/*`;
- M108A selected direction: `MODEL_B_PATCH_SECURITY_PAUSE_RETURN_TO_CORE_ARCHITECTURE`;
- M108A selected frontier: `GOAL_TO_PLAN_RUNTIME_CONSUMER_PROOF`;
- M108A Next Build: `NOT JUSTIFIED`.

M109A creates only this design record, its static/document-contract lock, and
the external summary at:

```text
/home/aether/summaries/milestone_109A_goal_to_plan_consumer_proof_summary.txt
```

No `PROGRESS.md`, README, Constitution, Architecture authority, production
code, existing test, dependency, route, API, persistence, queue, scheduler,
worker, or runtime/private-data change is authorized.

## 2. Exact Objective

Determine whether a real production component outside Core Coordination now
needs and can truthfully consume the necessary canonical chain:

```text
Goal
-> accepted Goal authority
-> Task
-> authoritative TaskContext
-> selected TaskContext
-> ThinkingProposal
-> canonical Plan
-> selected canonical PlanStep
-> Core Governance Evaluation
-> STOP BEFORE GENERIC ACT
```

Consumer proof is behavioral and semantic, not nominal. A real consumer must
have a current production caller and need for canonical identity, ownership,
selection, revision, lifecycle, criteria, stale-state behavior, and result
semantics. A class, helper, test, document, similarly named legacy plan, or
future architectural desire does not prove a consumer.

## 3. Inherited Authority

M96 remains the authoritative process-local Goal-to-Plan foundation. M98A
proved that no external canonical runtime consumer was justified. M99A proved
that the current production Thinking path has no truthful `ThinkingProposal`
producer. M108A selected this read-only consumer-proof frontier while pausing
patch-security implementation.

The current contract ownership is unchanged:

| Concern | Owner | Current boundary |
|---|---|---|
| Goal identity and human authority | Goal/Core Coordination | Process-local `GoalIntake`; no `/chat` handoff |
| Task and TaskContext continuity | Core Coordination | Authoritative in-memory objects; explicit selection |
| Thinking output | Thinking | Legacy policy dictionary; no production `ThinkingProposal` producer |
| Plan and PlanStep identity/lifecycle | Core Coordination | Process-local creation only |
| Governance evaluation | Core Governance via Core Coordination | Non-authorizing evaluation; stops before Generic Act |
| Interface input/output | Interface | Text/API serialization; not cognitive authority |
| Capability execution | Action services and capability-specific Governance | Separate contracts; not canonical Plan consumption |

## 4. Canonical Producer and Consumer Inventory

| Component | Current production evidence | M109A result |
|---|---|---|
| `aether/core/goal.py:155-186` | `GoalIntake` stores proposed and accepted Goals in an in-memory registry. | Canonical process-local Goal owner; no external caller. |
| `aether/core/task_context.py:339-416` | `CoreCoordination` creates accepted-Goal-bound Task and first authoritative TaskContext. | Canonical process-local producer; no runtime entrypoint. |
| `aether/core/task_context.py:453-483` | Explicit context selection and selection history. | Real selection state; not connected to `/chat` or another production runtime. |
| `aether/core/task_context.py:561-596` | Explicitly selected context creates immutable canonical Plan. | Process-local producer; no production caller outside Core Coordination. |
| `aether/core/task_context.py:598-632` | Ready `ThinkingProposal` is validated and materialized into a Plan. | Existing process-local consumer seam; no production proposal producer feeds it. |
| `aether/core/task_context.py:764-820` | Ordered canonical PlanStep is created under a current Plan. | Process-local operation; no external consumer. |
| `aether/core/task_context.py:638-742` | Current Plan and selected PlanStep become a Governance evaluation request/result. | Immediate Core Coordination caller; result is non-authorizing and stops. |
| `aether/thinking/proposal.py:96-203` | Immutable `ThinkingProposal` contract is defined. | Contract present; production producer absent. |

The canonical foundation is therefore real, but it remains one process-local
owner and immediate consumer. No second production consumer is established by
the existence of those methods.

## 5. Production Runtime Consumer Audit

### 5.1 `/chat`, runtime, and core loop

`aether/interface/api_server.py:223-309` accepts text or the legacy message
field, delegates to `AetherRuntime.process_chat`, and serializes a legacy loop
result. `aether/core/runtime.py:99-113` passes text, session metadata, Working
Memory, and a forced-false execution flag to `run_core_chat_loop`.

`aether/core/loop.py:28-332` currently performs:

```text
text
-> perception
-> identity integrity check
-> time state
-> Working Memory recording
-> risk classification
-> legacy tool suggestion
-> Thinking policy dictionary
-> legacy authorization envelope
-> approval request/queue
-> no tool execution
-> timeline event
-> textual response
```

This path does not create or consume canonical Goal, Task, TaskContext,
ThinkingProposal, Plan, PlanStep, or `CanonicalPlanGovernanceEvaluation`.
Its `execution_allowed` field is a legacy authorization-envelope result, not
canonical Plan Governance authorization. `/chat` is therefore not a truthful
canonical consumer.

### 5.2 Interface and Working Memory routes

The current API exposes no Goal-to-Plan runtime route. The Working Memory goal
route stores a goal string in Working Memory; it does not call `GoalIntake` and
does not create an accepted canonical Goal. Proposal-review, revision, repair,
tool-plan, verification-plan, simulation-plan, and executor routes expose
separate action-specific records. Their `plan` or `proposal` names do not make
them consumers of the M96 canonical chain.

### 5.3 Action services, queues, and persistence

Restricted-read execution is a real capability-specific path with approval,
authority binding, dispatch, and verification. Patch, repair, apply,
simulation, executor, and tool services likewise use their own contracts and
records. The audit found no worker, scheduler, queue, persistence adapter, or
event bridge that accepts canonical Goal/Task/TaskContext/Plan/PlanStep
identity and consumes canonical Governance evaluation.

These paths must not be generalized by naming similarity or by analogy to
canonical planning. They are not M109A consumer proof.

### 5.4 Core Coordination itself

Core Coordination is the process-local owner and the immediate caller of the
canonical materialization and Governance methods. That satisfies the existing
process-local Think -> Plan seam. It does not satisfy the question of whether
an external production runtime consumer exists.

## 6. ThinkingProposal Producer Dependency

`aether/thinking/policy.py:11-132` returns a legacy policy dictionary. It does
not construct a `ThinkingProposal`, and its fields cannot be silently mapped
into canonical proposal semantics:

- `decision_type` is not `PROPOSAL_READY` or `PROPOSAL_NOT_READY`;
- reasons, warnings, next-step text, blocked text, and response prose are not
  objective or completion/failure/blocked criteria;
- normalized user text is not an authorized `proposed_objective` mapping;
- session, trace, approval, request, text, timestamp, or tool identifiers are
  not proposal identity;
- metadata is not accepted Goal, Task, or selected TaskContext authority;
- risk and tool dictionaries are evidence references, not PlanStep identity or
  execution authority;
- the required complete provenance categories are not produced.

The only production materialization seam is
`CoreCoordination.materialize_thinking_proposal()`. The repository contains no
production provider, factory, adapter, API caller, persistence path, or worker
that emits a truthful `ThinkingProposal`. Existing proposal constructors are
test evidence for the process-local contract, not production producer proof.

Therefore the missing producer is a dependency of any future external
consumer, but it is not a reason to invent a producer during this consumer
proof. M99A remains unchanged:

```text
ThinkingProposal contract class: PRESENT
Core Coordination process-local consumer: SATISFIED
Current production ThinkingProposal producer: ABSENT
```

## 7. Consumer-Proof Decision

```text
D_NO_REAL_RUNTIME_CONSUMER_CURRENTLY_JUSTIFIED
```

Evidence-backed reasoning:

1. Core Coordination is the only current canonical owner and immediate
   process-local consumer.
2. `/chat`, `AetherRuntime`, and `core/loop.py` remain text-first legacy paths
   with no canonical Goal authority, selected context, proposal, Plan, or
   canonical Governance result.
3. No API, worker, scheduler, queue, event bridge, persistence path, or Action
   service consumes the full canonical identity and lifecycle boundary.
4. The current Thinking path still has no truthful production
   `ThinkingProposal` producer.
5. Similar legacy plan/proposal records and capability-specific consumers do
   not establish canonical consumer proof.

The resulting state is:

```text
Think -> Plan process-local consumer: SATISFIED
Think -> Plan consumer outside Core Coordination: NOT YET SATISFIED
External canonical runtime consumer: ABSENT
```

## 8. Candidate Model Comparison

| Model | Result | Evidence-based reason |
|---|---|---|
| `MODEL_A_CHAT_AS_CANONICAL_CONSUMER` | REJECTED | `/chat` has no accepted Goal authority, TaskContext selection, proposal producer, canonical Plan, or canonical Governance result. |
| `MODEL_B_CORE_LOOP_AS_CANONICAL_CONSUMER` | REJECTED | The core loop is the same legacy text/policy path and would require invented adapter semantics. |
| `MODEL_C_NEW_COORDINATION_RUNTIME_ENTRYPOINT` | NOT JUSTIFIED | A future entrypoint could preserve ownership, but no real production caller, use case, producer, lifecycle boundary, or consumer output contract is proven. |
| `MODEL_D_NO_RUNTIME_CONSUMER_YET` | SELECTED | Current production evidence supports only the existing process-local seam and does not justify speculative integration. |

Selected model:

```text
MODEL_D_NO_RUNTIME_CONSUMER_YET
```

## 9. Required Future Prerequisites

A separately authorized future runtime design must first establish:

1. One concrete production use case and one owning runtime component.
2. A truthful caller for accepted Goal authority, Task creation, and explicit
   TaskContext selection.
3. A real ThinkingProposal producer with distinct identity, revision, state,
   criteria, and complete provenance.
4. Exact Goal, Task, TaskContext, Plan, and selected PlanStep identity and
   revision binding across the consumer boundary.
5. Process lifetime, persistence, restart, privacy, selection, cancellation,
   stale-state, and failure behavior when scope crosses the process boundary.
6. A canonical Governance caller that preserves
   `GOVERNANCE_EVALUATION != EXECUTION_AUTHORIZATION`.
7. An output contract that stops before Generic Act and cannot silently
   authorize Action or execution.
8. Focused static, runtime, safety, and API regression tests under a separately
   authorized Build scope.
9. Explicit PM approval before production code, API, persistence, worker,
   scheduler, queue, or `/chat` changes.

These are proof prerequisites, not implementation authorization.

## 10. Explicit Non-Goals and Write Set

M109A does not implement or authorize:

- a Goal-to-Plan external runtime consumer;
- a ThinkingProposal producer, adapter, provider, or factory;
- `/chat`, `AetherRuntime`, or core-loop wiring;
- Goal/Task/TaskContext persistence, restart restoration, or API integration;
- Plan/PlanStep execution or Action dispatch;
- Observation Intake, Persistent Observation, Verification Aggregation, Critic,
  Repair, Learning, retry, background execution, worker, scheduler, or wake
  behavior;
- changes to patch, rollback, approval, restricted-read, tool, repair, apply,
  simulation, or executor contracts;
- Generic Act, a generic capability registry, or execution authorization;
- `PROGRESS.md`, README, Constitution, Architecture authority, production code,
  existing tests, dependencies, runtime/private data, commit, tag, or push.

The exact repository write set is:

1. `docs/architecture/MILESTONE_109A_GOAL_TO_PLAN_RUNTIME_CONSUMER_PROOF_BOUNDARY.md`;
2. `tests/test_milestone_109a_goal_to_plan_runtime_consumer_proof_boundary.py`.

The PM summary is external to the repository:

```text
/home/aether/summaries/milestone_109A_goal_to_plan_consumer_proof_summary.txt
```

## 11. Build and Generic Act Gates

```text
External runtime consumer: NOT PROVEN
ThinkingProposal production producer: ABSENT
Runtime Build: NOT JUSTIFIED
Generic Act: NOT_IMPLEMENTED
Generic Act integration: NOT_AUTHORIZED
Generic Act authority: NOT_GRANTED
```

M109A is complete locally only when the static/document lock passes. It is not
Git durability, PM acceptance, runtime approval, or Build authorization.

```text
Next authorized action: HUMAN/PROJECT-MANAGER M109A CONSUMER-PROOF REVIEW
```
