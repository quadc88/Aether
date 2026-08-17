# Milestone 96E Structured Thinking Proposal Contract Boundary

Classification: DESIGN / SEMANTIC CONTRACT BOUNDARY

Status: CONTRACT CONTENT ESTABLISHED LOCALLY / GIT LIFECYCLE EXTERNAL / PM ACCEPTANCE EXTERNAL

This record defines the minimum semantic contract required before any runtime
Think -> Plan consumer may exist. It is documentation and static-contract
scope only.

NO RUNTIME IMPLEMENTATION

No ThinkingProposal runtime class, producer, consumer, loop wiring, API,
persistence, Governance runtime change, Plan runtime change, or execution path
is implemented by this record.

## 1. Purpose and Provenance

Milestone 96D established the accepted prerequisite-discovery result:

- `B_THINK_OUTPUT_NOT_YET_PLAN_COMPATIBLE`;
- `MODEL_E_NO_RUNTIME_INTEGRATION_YET`;
- `READY_FOR_PM_M96_THINKING_PROPOSAL_PREREQUISITE_DEFINITION`.

That read-only decision proved the gap but did not define a proposal contract.
Milestone 96E defines the semantic boundary only. It does not relabel the
M96D discovery result as an implemented proposal contract.

The unresolved parent seam remains:

```text
Thinking -> structured proposal contract -> Core Coordination -> canonical Plan
```

The canonical Plan and PlanStep process-local runtime already exist. The
missing prerequisite is a truthful, immutable, non-authoritative structured
Thinking proposal that can later be consumed without inventing identity,
provenance, criteria, or failure semantics.

## 2. Selected Contract Model

Selected semantic model:

```text
MODEL B-S — STRUCTURED IMMUTABLE THINKING PROPOSAL WITH AUTHORITATIVE CONTEXT BINDING
```

The conceptual object is `ThinkingProposal`.

Thinking owns proposal semantics and proposal content. Thinking does not own:

- Goal identity or Goal authority;
- Task identity or Task lifecycle;
- TaskContext lifecycle, selection, or switching;
- canonical Plan identity, lifecycle, or criteria authority;
- PlanStep identity;
- Core Governance authorization;
- execution permission.

Core Coordination supplies and later validates the authoritative Goal, Task, and
explicitly selected TaskContext binding. Thinking may reference those
identities, but may never invent, derive, or alias them.

This is a semantic contract boundary, not a runtime schema or implementation.

## 3. Future Semantic Flow

The future flow is locked as an ownership direction only:

```text
Human Authority
  -> accepted Goal
Core Coordination
  -> Task
  -> authoritative TaskContext
  -> explicit selected TaskContext
authoritative binding context
  -> Thinking
Thinking
  -> immutable ThinkingProposal
Core Coordination
  -> validates binding
  -> validates freshness
  -> validates explicit completeness
  -> materializes canonical Plan / PlanStep only from supported fields
Core Governance
  -> evaluates canonical Plan / PlanStep before any future generic Act
STOP BEFORE GENERIC ACT
```

Milestone 96E implements none of these runtime arrows.

## 4. Proposal Identity and Revision

Every `ThinkingProposal` has a distinct conceptual identity:

- `proposal_id` — identity of this proposal object;
- `proposal_revision` — revision of this proposal only;
- `created_at` — proposal creation time.

`proposal_id` is semantically distinct from every other identity:

```text
proposal_id != goal_id != task_id != task_context_id != plan_id != plan_step_id
proposal_id != session_id != trace_id != approval_id
```

The following substitutions are forbidden:

- `session_id` for `proposal_id`;
- `trace_id` or `loop_trace` for `proposal_id`;
- `approval_id` for `proposal_id`;
- a request identifier, timestamp, tool identifier, or hash for `proposal_id`.

`proposal_revision` is not a TaskContext revision, Plan revision, loop count,
retry count, or approval revision. `created_at` is proposal creation time, not
authorization time. Time provides context, not authority.

The proposal is an immutable snapshot. Substantive change requires a new
proposal revision or a new proposal identity according to a future runtime
contract. No silent mutation and no silent cross-context merge are permitted.

## 5. Authoritative Context Binding

The proposal binding contains references to:

- `goal_id`;
- `task_id`;
- `task_context_id`;
- `task_context_revision`.

These values must originate from already-authoritative Core Coordination state.
They must not be derived from:

- `session_id`;
- `trace_id` or `loop_trace`;
- `approval_id`;
- request text or normalized user text;
- arbitrary metadata;
- timestamps;
- tool IDs;
- policy rules.

Before any future materialization, Core Coordination must validate that:

1. the Goal exists and is authoritative;
2. the Task exists and belongs to the Goal;
3. the TaskContext exists and belongs to the Task and Goal;
4. the TaskContext is the authoritative current context;
5. the TaskContext was explicitly selected for the reasoning turn;
6. the supplied TaskContext revision is current for the handoff;
7. no terminal, stale, superseded, blocked, or otherwise invalid context is
   silently revived or merged.

Milestone 96E defines these requirements only. No validator is implemented.

## 6. Structured Proposal Content

The non-authoritative proposal content distinguishes the following semantic
fields. Every Plan-facing field remains a proposal:

- `proposed_objective`;
- `proposed_completion_criteria`;
- `proposed_failure_criteria`;
- `proposed_blocked_criteria`;
- `rationale`;
- `constraints_references`;
- `assumptions`;
- `dependency_proposals`;
- `verification_requirement_proposals`;
- `risk_evidence_references`;
- `requested_action_relation`;
- `tool_suggestion_relation`;
- `provenance`.

The fields above do not make a canonical Plan. ThinkingProposal is not a
canonical Plan and does not own canonical Plan criteria, Plan identity, Plan
lifecycle, Plan readiness, PlanStep identity, or execution authorization.

`requested_action_relation` and `tool_suggestion_relation` are evidence of a
requested or suggested operation only. They are not Action-attempt identity,
PlanStep identity, Plan readiness, approval, permission, or execution.

## 7. Criteria Authority and Non-Fabrication

Thinking may propose criteria. Thinking does not make criteria authoritative.

The following remain proposals only:

- `proposed_completion_criteria`;
- `proposed_failure_criteria`;
- `proposed_blocked_criteria`.

Future Core Coordination materialization must validate explicit proposal
content, reject missing required criteria, reject invalid criteria, preserve
provenance, and materialize authoritative criteria under the canonical Plan
stage. It must not use prose fallback, inference fallback, or default fabricated
criteria.

The following are not authoritative canonical Plan criteria:

- `Goal.requested_outcome`;
- `Goal.goal_constraints`;
- `Task.task_scope`;
- `Task.task_constraints`;
- `TaskContext.completion_criteria_reference`;
- Thinking `reasons`;
- Thinking `next_step`;
- Thinking `warnings`;
- Thinking `blocked_reason`;
- Governance `reason`;
- Governance denial;
- risk level;
- tool suggestion;
- `response_text`;
- normalized user text.

These may be source evidence only when a future, separately authorized mapping
rule explicitly permits their use. Milestone 96E introduces no implicit
mapping rule.

The canonical Plan stage remains the sole authority for canonical Plan
completion, failure, and blocked criteria. Proposal existence does not change
that ownership.

## 8. Structured Provenance

`provenance` is structured evidence, not authorization and not free-form
reasoning text. It must preserve source-category distinctions without merging
their authority.

At minimum, provenance distinguishes references to:

- Human / Goal authority;
- Goal source;
- Task source;
- TaskContext source;
- Thinking reasoning/proposal source;
- Verification / risk evidence;
- tool-suggestion evidence;
- Time context.

Each category remains owned by its existing source authority. Provenance may
identify where a value came from; it cannot grant permission, replace an
authoritative identity, or convert evidence into a canonical criterion.

`loop_trace` is not proposal provenance identity. A policy reason is not a
provenance envelope. A risk level is not a durable evidence reference. A tool
ID is not proposal identity or PlanStep identity.

## 9. Constraints Boundary

Goal constraints remain owned by Goal Intake under Human Authority. Task
constraints remain owned by Core Coordination. ThinkingProposal may refer to
applicable authoritative constraints but may not:

- rewrite them silently;
- discard them silently;
- change their precedence silently;
- merge metadata into them as equal authority;
- treat a policy reason or tool suggestion as an authoritative constraint.

Conflicting constraints require a non-fabricating proposal failure state. No
constraint winner may be inferred by the proposal boundary.

## 10. Explicit Proposal Outcome

The conceptual proposal state is one of exactly two semantic outcomes:

```text
PROPOSAL_READY
PROPOSAL_NOT_READY
```

`PROPOSAL_NOT_READY` must include a structured `not_ready_reason`. The reason
must identify the failure category and preserve relevant source references; it
must not be only arbitrary response prose.

At minimum, the reason categories are:

- `missing_selected_task_context`;
- `stale_task_context_revision`;
- `missing_proposed_completion_criteria`;
- `missing_proposed_failure_criteria`;
- `missing_proposed_blocked_criteria`;
- `clarification_required`;
- `insufficient_user_intent`;
- `conflicting_constraints`;
- `unsupported_provenance`;
- `invalid_authoritative_binding`.

No canonical Plan may be created when proposal state is `PROPOSAL_NOT_READY`.
Missing or invalid semantics must not be repaired by copying response prose,
Thinking reasons, `next_step`, warnings, `blocked_reason`, risk, or tool
suggestions into Plan criteria.

## 11. Clarification Boundary

The current policy outputs remain policy/workflow outputs:

- `ask_clarification`;
- `clarification_question`;
- `next_step`.

A clarification-required result is distinct from all of the following:

- `PROPOSAL_READY`;
- canonical Plan ready;
- Plan blocked;
- Governance denied;
- execution blocked.

Clarification does not materialize a ThinkingProposal with invented objective
or criteria, and it does not materialize a canonical Plan.

## 12. Ownership Matrix

| Concern | Authoritative owner | ThinkingProposal role | Explicit non-owner |
|---|---|---|---|
| Human objective and Goal authority | Goal Intake / Human Authority | reference evidence only | ThinkingProposal |
| Goal identity | Goal Intake | reference `goal_id` supplied by Core Coordination | ThinkingProposal |
| Task lifecycle and identity | Core Coordination | reference `task_id` supplied by Core Coordination | ThinkingProposal |
| TaskContext lifecycle | Core Coordination | reference selected context and revision | ThinkingProposal |
| Context selection and switching | Core Coordination | consume selected binding only | ThinkingProposal |
| Proposed planning semantics | Thinking | own proposal content | canonical Plan |
| Canonical Plan identity and lifecycle | Core Coordination / canonical Plan stage | propose content only | ThinkingProposal |
| Canonical Plan criteria | canonical Plan stage | propose criteria only | ThinkingProposal, Goal, TaskContext |
| PlanStep identity and lifecycle | Core Coordination / canonical PlanStep contract | propose step-related evidence only | ThinkingProposal |
| Verification evidence | Verification | reference evidence only | ThinkingProposal |
| Risk authorization decision | Core Governance | reference risk evidence only | ThinkingProposal |
| Permission and execution authorization | Core Governance | never grant | ThinkingProposal, Plan readiness |
| Action occurrence | Action occurrence contract | relation only | ThinkingProposal, PlanStep ID |
| Time facts and temporal context | Time | reference only | ThinkingProposal |

Core Coordination validates binding, freshness, and explicit supported fields;
materializes canonical Plan and PlanStep state; and fails closed. Core
Coordination does not become a semantic reasoner and may not invent missing
proposal semantics.

## 13. Governance and Execution Separation

Milestone 96E does not modify Core Governance runtime. A future canonical
Plan/PlanStep consumer requires separate authorization before Governance
integration.

These distinctions are locked:

```text
ThinkingProposal ready       != canonical Plan ready
ThinkingProposal ready       != Plan authorized
canonical Plan ready         != execution authorized
Goal accepted                != execution authorized
Task active                  != execution authorized
TaskContext selected         != execution authorized
Governance evaluation        != Action execution
```

Thinking proposes. Core Coordination materializes canonical planning state.
Core Governance authorizes. Verification supplies evidence. Action executes
only within authorization. M96 remains STOP BEFORE GENERIC ACT.

## 14. Immutability and Proposal / Plan Separation

ThinkingProposal is a non-authoritative immutable proposal snapshot. Canonical
Plan is Core-Coordination-materialized authoritative task planning state. Core
Governance authorization is a separate authorization decision over a future
execution path. None are aliases.

ThinkingProposal creation does not create a Plan. Canonical Plan creation does
not authorize Act. Governance evaluation does not execute Act.

Proposal revision, TaskContext revision, and Plan revision are distinct
concepts. No revision may be inferred from another revision or from loop,
retry, or approval counts.

## 15. Runtime, API, Persistence, and Capability Freeze

Milestone 96E authorizes no:

- runtime ThinkingProposal class;
- producer implementation;
- Think -> Plan consumer;
- loop or `/chat` wiring;
- Core Governance runtime change;
- Plan or PlanStep runtime change;
- API, router, request model, response model, or OpenAPI change;
- JSON store, queue, database, private record, restart restoration, or
  cross-session restoration;
- generic Act, tool execution, Observation Intake, Verification Aggregation,
  Critic, Repair, Learning, retry, scheduler, or background execution.

The following runtime files are frozen by this milestone:

- `aether/core/loop.py`;
- `aether/core/governance.py`;
- `aether/thinking/policy.py`;
- current Goal / Task / TaskContext runtime;
- current Plan / PlanStep runtime;
- `aether/interface/api_server.py` and routers/models.

## 16. Exact Authorized Write Set

Exactly four repository paths are authorized:

1. `docs/architecture/MILESTONE_96E_STRUCTURED_THINKING_PROPOSAL_CONTRACT_BOUNDARY.md`;
2. `tests/test_milestone_96e_structured_thinking_proposal_contract_boundary.py`;
3. `PROGRESS.md`;
4. `tests/test_progress_ledger_canonical_header.py`.

Production dirty paths: zero. No fifth path is authorized.

The static lock is exactly 14 ordinary top-level tests. It imports no Aether
runtime modules, invokes no endpoint, uses no TestClient, accesses no private
runtime data, and writes no files.

## 17. Parent Accounting

After this local Build:

- Goal admission: **SATISFIED**;
- Task: **SATISFIED**;
- TaskContext: **SATISFIED**;
- Canonical Plan: **SATISFIED**;
- Canonical PlanStep: **SATISFIED**;
- Think -> Plan consumer: **NOT YET SATISFIED**;
- Governance-before-generic-Act: **NOT YET SATISFIED**;
- Structured Thinking Proposal prerequisite contract: **ESTABLISHED LOCALLY**;
- M96: **OPEN**;
- M95: **CLOSED / GIT-DURABLE / PM-ACCEPTED**;
- M95 reopened: **NO**.

Documentation alone does not satisfy the Think -> Plan runtime obligation.

## 18. Temporal Truth and Non-Authorization

This record may claim only that contract content is established locally and the
runtime prerequisite is not implemented. It does not self-assert:

- a future commit SHA;
- future tag existence;
- remote publication;
- future PM durable acceptance.

Git determines commit, tag, and publication state. PM acceptance is external.

Current decision state is:

```text
M96E CONTRACT CONTENT ESTABLISHED LOCALLY
NO RUNTIME THINKINGPROPOSAL IMPLEMENTATION
THINK -> PLAN CONSUMER NOT YET SATISFIED
GOVERNANCE-BEFORE-GENERIC-ACT NOT YET SATISFIED
M96 OPEN
GIT LIFECYCLE EXTERNAL
PM ACCEPTANCE EXTERNAL
```

No runtime successor milestone is authorized by this record; future work requires separate project-manager authority.
