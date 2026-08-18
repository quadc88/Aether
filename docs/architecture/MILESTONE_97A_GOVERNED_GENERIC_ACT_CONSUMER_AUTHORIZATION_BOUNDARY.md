# Milestone 97A Governed Generic Act Consumer & Authorization Boundary

Classification: DESIGN / DISCOVERY / CONSUMER-PROOF BOUNDARY

Status: DESIGN / DISCOVERY ONLY / COMPLETE LOCALLY / GIT DURABILITY NOT CLAIMED / PM REVIEW PENDING

This record defines a contract boundary only. It does not implement Generic
Act, Action dispatch, tool execution, an API, persistence, Observation Intake,
Critic, Repair, Learning, background execution, or a runtime successor.

## 1. Purpose

Milestone 97A determines whether the existing Milestone 96 Governance
evaluation has a truthful downstream consumer and what would be required
before a future Generic Act attempt could execute. It does not reinterpret a
Governance result as execution permission.

The binding safety equation is:

```text
GOVERNANCE_EVALUATION != EXECUTION_AUTHORIZATION
```

The design answers the consumer, authorization, identity, freshness, human
authority, and existing-execution-surface questions without wiring any path.

## 2. Starting Authority

- Branch: `main`.
- HEAD, `main`, and `origin/main`: `a62124ac92c03c363bcb942fb9191e7269d152f5`.
- Remote `main`: `a62124ac92c03c363bcb942fb9191e7269d152f5`.
- Worktree at read start: clean and unstaged.
- M96 closure tag: `milestone-96-authoritative-goal-to-plan-cognitive-foundation-closure` at `a62124ac92c03c363bcb942fb9191e7269d152f5`.
- M96 state: CLOSED / GIT-DURABLE / PM-ACCEPTED.
- Parent contract: `docs/architecture/MILESTONE_96_PARENT_CONTRACT_AUTHORITY.md`.
- Parent contract commit: `8f48a3e8424c1650b269d0a03c4330a799a0353e`.
- Parent contract SHA256: `4143aa7f968af38f112203b2493cecd19f4341c5f8ca4e78f1abc4c0b0d20336`.
- Architecture version: `0.3.0`.
- OpenAPI baseline: `306 paths / 112 schemas`.
- api_server baseline: `8 direct @app routes / 23 include_router / 0 direct /action/*`.

## 3. M96 Closure Inheritance

M97A inherits the exact M96 parent contract and closure record. M96 established
the process-local path:

```text
Human Authority
-> Goal acceptance
-> Goal
-> Task
-> authoritative TaskContext
-> selected TaskContext for reasoning turn
-> Thinking proposal
-> canonical Plan
-> canonical PlanStep
-> Core Governance evaluation
-> STOP BEFORE GENERIC ACT
```

M96G is the durable Governance contribution:

- Implementation commit: `9d288215f2483913ccc702916bbd39e8c487a4e0`.
- Implementation tag: `milestone-96G-canonical-plan-governance-evaluation`.
- PM acceptance: externally accepted.
- `CanonicalPlanGovernanceEvaluationRequest` and
  `CanonicalPlanGovernanceEvaluation` are immutable, process-local objects.
- The evaluation boundary is `before_generic_act`.
- `authorization_granted`, `execution_allowed`, and
  `action_dispatch_allowed` are always `False`.

M96 explicitly stopped before Generic Act. M97A does not reopen or weaken that
boundary, and M97A does not authorize M97B, M98, or any runtime successor.

## 4. Current Producer Inventory

| Current production surface | Role | Evidence | Finding |
|---|---|---|---|
| `aether/core/governance.py` | Defines and evaluates the request | `CanonicalPlanGovernanceEvaluationRequest` at lines 82-149; evaluator at lines 301-413 | REAL_RUNTIME_EVALUATOR, not a downstream Action consumer |
| `aether/core/task_context.py` | Core Coordination builds the request and calls Governance | `evaluate_canonical_plan_governance` at lines 638-742 | REAL_RUNTIME_CALLER / REQUEST PRODUCER |
| `aether/core/governance.py` result | Returns the immutable evaluation | Result fields at lines 176-250 | No execution scope, approval satisfaction, or authorization identity |

The Core Coordination caller returns the evaluation to its caller. It does not
read the result to authorize or dispatch an Action.

## 5. Current Consumer Inventory

### Production result consumer

```text
NO_CONSUMER
```

No production code consumes `CanonicalPlanGovernanceEvaluation` to authorize,
dispatch, or execute an Action. No production code consumes
`governance_decision == "evaluate"` as execution permission. The result's three
authorization flags are structurally required to remain false.

### Other references

| Reference | Classification | Evidence |
|---|---|---|
| `tests/test_milestone_96g_canonical_plan_governance_evaluation.py` | TEST_ONLY_CONSUMER | Constructs requests, calls the evaluator, and asserts result flags |
| `tests/test_milestone_96_authoritative_goal_to_plan_cognitive_foundation_closure.py` | TEST_ONLY_CONSUMER | Locks the M96G record and non-authority semantics |
| `tests/test_progress_ledger_canonical_header.py` | TEST_ONLY_CONSUMER | Locks current ledger terminology |
| M96 closure record and `PROGRESS.md` | DOCUMENT_ONLY_REFERENCE | Records the boundary and no-consumer state |

Naming, a returned object, or a test assertion is not evidence of a real
runtime consumer.

## 6. Existing Execution-Surface Inventory

| Existing mechanism | Generic Act contract compatibility | Current evidence and boundary |
|---|---|---|
| Capability-specific restricted read | NOT_PROVEN | `aether/core/coordination.py:33-122` and `aether/action/services/restricted_file_read_execution_service.py:79-148` consume an exact `file.restricted_read` action, approval record, session binding, and fingerprint. `restricted_file_read_bridge.py:4-34` consumes a single-use capability scope, not a Generic Act authorization. |
| Legacy tool executor | NO | `aether/action/tool_executor.py:332-403` selects from tool-planner output and sandbox allowlists, persists an execution log, and has no M96 Plan/Governance authorization input. |
| Action-specific patch apply | NO | `aether/action/patch_apply.py:31-56` consumes patch proposal and approval records, with `dry_run=False` causing the file write. It does not consume a canonical Governance evaluation. |
| Action-specific patch rollback | NO | `aether/action/patch_rollback.py:31-52` consumes an apply record and backup path. It has no Generic Act authorization binding. |
| Guided repair / proposal launchers | NO | `guided_repair_plan_launcher.py:67-161` stops at planning and `guided_proposal_decision_launcher.py:23-44` stops before dry run. These are planning/review surfaces, not Generic Act consumers. |
| Approval execution gates | NOT_PROVEN | `approval_decision_gate.py:19-71` validates restricted-read bindings and `:74-213` validates legacy action records while keeping execution false. `approval_queue.py:309-363` provides single-use claim state; real-apply gates remain action-specific. No Generic Act authorization input is consumed. |

Existing mechanisms must not be accepted as Generic Act consumer proof by
analogy. The one real restricted-read consumer is a separate capability-specific
contract and cannot be widened silently.

## 7. Governance Evaluation Semantics

`CanonicalPlanGovernanceEvaluationRequest` currently binds:

- `goal_id`, `task_id`, `task_context_id`, and `task_context_revision`;
- selected context identity;
- `plan_id`, `plan_revision`, `plan_step_id`, and `plan_step_revision`;
- current Plan, PlanStep, and TaskContext snapshots;
- proposal provenance, hard constraints, soft signals, and binding errors.

The evaluator fails closed for missing selection, stale snapshots, invalid
identity or parent bindings, stale Plan/PlanStep revisions, terminal Plan or
PlanStep state, blocked state, and hard-constraint violations. A successful
result means that the canonical Plan and selected current PlanStep were
evaluated under the supplied process-local evidence.

It does not mint an execution scope, identify an executable capability, record
an approval, bind action arguments, create a single-use dispatch claim, or
authorize Generic Act.

## 8. Execution Authorization Semantics

Execution authorization is a separate future contract. A future authorization
object, if separately authorized, would need to be issued by the authority
owner and would need to be narrower than a Governance evaluation. At minimum it
would need to bind the exact Plan/PlanStep state, the exact capability and
arguments, the applicable policy generation, any required human approval, an
expiry/freshness boundary, and a single-use execution identity.

The following are not equivalent to that future object:

- `evaluation_status == "EVALUATED"`;
- `governance_decision == "evaluate"`;
- Plan or PlanStep readiness;
- an approval request with status `pending`;
- an approved action-specific record;
- `execution_allowed`, `action_dispatch_allowed`, or `tool_execution_allowed`
  copied from an unrelated compatibility surface.

No execution authorization object is defined or implemented by M97A.

## 9. Identity Binding Matrix

| Identity or binding | M97A classification | Current evidence / future boundary |
|---|---|---|
| `goal_id` | REQUIRED | Present in Plan, PlanStep, and M96G request/result; future authorization must match the accepted Goal. |
| `task_id` | REQUIRED | Present in Plan, PlanStep, and M96G request/result; no cross-Task reuse. |
| `task_context_id` | REQUIRED | Present and selected explicitly; future authorization must use one current context only. |
| `task_context_revision` | REQUIRED | Present and freshness-checked by M96; future authorization must bind the exact revision. |
| `plan_id` | REQUIRED | Present and parent-checked by M96; future authorization must name the exact Plan. |
| Plan revision identity | REQUIRED | `plan_revision` exists and is checked by M96; future authorization must bind it. |
| selected `plan_step_id` | REQUIRED | `plan_step_id` and `plan_step_revision` exist; an actual Action attempt must name the exact selected step. |
| Thinking proposal identity/revision | NOT_CURRENTLY_PROVABLE | M96 preserves proposal provenance but does not expose a required `thinking_proposal_id` and `proposal_revision` in the Governance result. Future use requires explicit binding if proposal lineage is material. |
| `governance_evaluation_id` | NOT_CURRENTLY_PROVABLE | M96G has no evaluation identity or issuance timestamp. A future authorization must not refer to an unidentifiable evaluation. |
| Governance policy/profile identity | NOT_CURRENTLY_PROVABLE | M96 carries constraints and context references, but no stable policy/profile generation identity in the evaluation contract. |
| Human approval identity | NOT_CURRENTLY_PROVABLE for generic policy; REQUIRED when a future policy requires approval | Existing restricted-read approval identity is capability-specific and cannot establish the generic rule. |
| Capability/action identity | REQUIRED | A future authorization must identify the exact capability and action type; M96G does not mint this scope. |
| Arguments/input fingerprint | REQUIRED | Exact action arguments must be fingerprinted and compared before dispatch; existing restricted-read proves this pattern only for that capability. |
| Authority/freshness timestamp or generation | REQUIRED | M96 has object timestamps/revisions but no authorization expiry or evaluation generation. A future authorization must add a fail-closed freshness boundary. |

No absent identifier is fabricated by M97A.

## 10. Freshness and Staleness Matrix

| Condition | Current M96 evidence | Future authorization behavior |
|---|---|---|
| Selected Task changed | No standalone Task revision is bound in the M96G request | Reject as stale unless exact Task identity and revision still match. |
| TaskContext changed | Snapshot and revision checks exist | Reject immediately; do not reuse the old authorization. |
| Plan changed | Plan snapshot and `plan_revision` checks exist | Reject on any Plan identity, revision, status, or binding change. |
| Selected PlanStep changed | PlanStep snapshot and revision checks exist | Reject on identity, parent, sequence, status, or revision change. |
| ThinkingProposal changed | No direct proposal identity is currently bound | Reject in a future contract when proposal lineage is required and identity/revision differs. |
| Governance policy changed | No policy generation identity is currently bound | Reject unless the authorization was issued under the current exact policy/profile generation. |
| Governance evaluation stale | No evaluation identity, issuance time, or expiry exists | Reject; a future authorization must reference a current, identifiable evaluation. |
| Approval absent, rejected, cancelled, or consumed | Existing approval paths fail closed and restricted-read claims are single-use | Reject; never treat pending, historical, or consumed approval as current authority. |
| Requested Action differs from evaluated Action | Restricted-read exact action binding exists; no Generic Act binding exists | Reject on capability, action type, target, or any identity mismatch. |
| Arguments differ from evaluated arguments | Restricted-read fingerprint exists; no generic fingerprint exists | Reject on any input or argument fingerprint mismatch. |
| Authority expired | No generic expiry exists | Reject after expiry or missing freshness proof. |
| Task paused, cancelled, or completed | M96 context snapshots and terminal Plan/Step checks fail closed; no Generic Act consumer exists | Reject terminal tasks; paused/waiting use requires an explicit future policy and fresh authorization, never implicit continuation. |

These are design requirements only. M97A adds no runtime checks or execution
path.

## 11. Human Authority Analysis

The Constitution preserves human authority and requires stronger review for
high-risk actions. Existing restricted-read execution requires an approved,
exactly bound action-specific approval record. Existing real-apply surfaces
require a separate human approval path and revalidation.

For a Generic Act contract, the approval rule is:

```text
NOT_YET_PROVABLE
```

M97A cannot truthfully select ALWAYS, BY_RISK, or NO_APPROVAL because no real
Generic Act consumer, capability policy, risk profile, or authorization object
currently exists. The existing restricted-read approval rule must not be
generalized by analogy, and current approval runtime is unchanged.

## 12. Organ Ownership

- Thinking proposes proposal content and rationale.
- Core Governance owns policy, authority, and authorization decisions.
- Core Coordination owns Goal/Task/TaskContext continuity, Plan continuity,
  selection, and handoff coordination.
- Action executes only after a valid future authorization is supplied.
- Verification supplies evidence after Action; it does not become an execution
  authority source.
- AetherOS supplies facts and mechanisms, not Governance interpretation.

M97A does not move authority into Action, execution into Governance, or policy
ownership into Core Coordination.

## 13. ASC and TaskContext Safety

The M96 ASC contract remains binding:

- one Authoritative Shared Cognitive Context framework;
- one authoritative TaskContext per active Task;
- one selected current TaskContext per reasoning turn;
- waiting, paused, and background contexts remain separate;
- no silent merge, overwrite, fallback adoption, or cross-Task transfer;
- explicit context switching belongs to Core Coordination under Governance
  constraints.

A future Generic Act authorization must name one exact Task and one exact
TaskContext. It must never combine context from multiple Tasks or silently
adopt a newly selected context.

## 14. Consumer-Proof Decision

```text
D_NO_REAL_CONSUMER_CURRENTLY_JUSTIFIED
```

This is evidence-backed, not roadmap-driven. Core Coordination is a real caller
of Governance, but no production downstream consumer reads the evaluation to
authorize or execute Action. Existing capability-specific and action-specific
surfaces do not prove a Generic Act consumer.

## 15. Generic Act Model Comparison

| Model | Result | Reason |
|---|---|---|
| `MODEL_A_DIRECT_GOVERNANCE_RESULT_CONSUMER` | REJECTED | Contradicts the M96G invariant that evaluation is not execution authorization and all execution flags remain false. |
| `MODEL_B_IMMUTABLE_EXECUTION_AUTHORIZATION_OBJECT` | FUTURE POSSIBILITY, NOT SELECTED | Could provide identity, freshness, scope, approval, and single-use binding, but no real consumer or complete policy/identity contract currently justifies defining it. |
| `MODEL_C_CAPABILITY_SPECIFIC_ADAPTERS_ONLY` | EXISTING PATTERN, NOT A M97A DECISION | Restricted-read has a bounded adapter, but no Generic Act consumer exists and this cannot justify a generic capability registry or broadened authority. |
| `MODEL_D_NO_GENERIC_ACT_YET` | SELECTED | Truthfully records the absence of a proven Generic Act consumer and prevents speculative runtime authority. |

## 16. Selected Model or No-Model Decision

```text
MODEL_D_NO_GENERIC_ACT_YET
```

M97A defines no authorization object, no Generic Act consumer, no capability
registry authority, and no adapter. The next runtime design may only begin
after a separately authorized consumer-proof decision identifies a real
consumer and a complete bounded contract.

## 17. Rejected Models

Direct consumption is rejected because `EVALUATED` is deliberately non-
authorizing. An immutable authorization object is not rejected as a future
engineering possibility, but defining it now would invent missing policy,
approval, evaluation identity, and consumer requirements. Capability-specific
adapters remain valid only when separately justified by an actual capability
consumer; they do not constitute Generic Act proof.

## 18. Explicit Non-Goals

M97A does not add or authorize:

- Generic Act implementation or dispatch;
- Action execution or tool execution;
- `/chat` execution expansion or loop wiring;
- API routes, schemas, operation IDs, or persistence;
- a second governed capability or generic capability registry authority;
- Observation, Persistent Observation Record, Observation Intake, or
  Verification Aggregation;
- Critic, Repair, Learning, retry, scheduler, background execution, or wake
  behavior;
- a consumer of the existing restricted-read capability beyond its current
  contract;
- a new approval policy or changes to current approval runtime;
- M97B, M98, or any successor runtime milestone;
- commit, tag, push, or any Git lifecycle operation.

## 19. Future Runtime Prerequisites

A separately authorized future runtime effort would need to prove, before any
execution wiring:

1. one real consumer and its owning organ;
2. an explicit authorization contract distinct from Governance evaluation;
3. exact Goal/Task/TaskContext/Plan/PlanStep identity and revision binding;
4. identifiable Governance evaluation and policy/profile generation;
5. capability/action identity and canonical argument fingerprint;
6. human approval policy and approval identity where required;
7. expiry, stale-state, cancellation, pause, and single-use behavior;
8. a bounded Action bridge that cannot broaden capability scope;
9. post-Action result shape sufficient for later truthful Observe/Verify work;
10. focused static, runtime, and safety evidence under a separately authorized
    repository scope.

No item above is implemented or authorized by M97A.

## 20. Closure and Next-Step Gate

M97A design/discovery content is COMPLETE LOCALLY when this record and its
static lock pass validation. That local result does not make M97A Git-durable,
does not grant Generic Act authority, and does not start a successor milestone.

Current truthful state:

- M96: CLOSED / GIT-DURABLE / PM-ACCEPTED.
- M97A: DESIGN / DISCOVERY ONLY.
- Generic Act: NOT_IMPLEMENTED.
- Generic Act integration: NOT_AUTHORIZED.
- Generic Act authority: NOT_GRANTED.
- Consumer-proof decision: `D_NO_REAL_CONSUMER_CURRENTLY_JUSTIFIED`.
- Selected model: `MODEL_D_NO_GENERIC_ACT_YET`.
- M97A runtime successor: NOT AUTHORIZED.

Next authorized action: human/project-manager M97A Build review.
