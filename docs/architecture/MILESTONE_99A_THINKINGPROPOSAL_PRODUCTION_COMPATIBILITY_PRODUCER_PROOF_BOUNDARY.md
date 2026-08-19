# Milestone 99A ThinkingProposal Production Compatibility Producer Proof Boundary

Classification: STRICT READ-ONLY DESIGN / DISCOVERY / PRODUCER-PROOF

Status: DESIGN / DISCOVERY ONLY / COMPLETE LOCALLY / GIT DURABILITY NOT CLAIMED / PM ACCEPTANCE EXTERNAL

This record audits whether the current production Thinking path can truthfully
produce the canonical `ThinkingProposal` contract. It does not implement a
producer, adapter, provider, consumer, persistence path, API change, `/chat`
wiring, or runtime successor.

## 1. Current Git State

- Branch: `main`.
- HEAD: `a1b716748dcf7e45a263fed93da427c54cfcda75`.
- `main`, `origin/main`, and remote `main`: `a1b716748dcf7e45a263fed93da427c54cfcda75`.
- Worktree at audit start: clean and unstaged.
- M98A: FINALIZED / COMMITTED / TAGGED / PUSHED.
- OpenAPI baseline: `306 paths / 112 schemas`.
- api_server baseline: `8 direct @app routes / 23 include_router / 0 direct /action/*`.

M99A authorizes only this design record, its static/document-contract lock,
and the external PM summary. It does not authorize a commit, tag, push,
`PROGRESS.md` update, existing-test edit, production edit, or runtime-data edit.

## 2. Exact Objective

Determine whether a current production producer can emit a truthful immutable
`ThinkingProposal` for the existing process-local seam:

```text
authoritative Goal / Task / selected TaskContext
  -> Thinking
  -> immutable ThinkingProposal
  -> Core Coordination materialize_thinking_proposal
  -> canonical Plan
```

Producer proof is behavioral and semantic, not nominal. The existence of the
`ThinkingProposal` class, a consumer method, tests, or documentation does not
prove a production producer. A producer must supply every required semantic
without inventing authority, aliasing identity, or turning policy evidence
into canonical planning state.

## 3. Inherited Contract and Ownership

The canonical contract is the M96E/M96F `ThinkingProposal` boundary. The
production class is present at `aether/thinking/proposal.py:96-203`, and the
process-local consumer is present at
`aether/core/task_context.py:598-632`.

Thinking may own non-authoritative proposal semantics. Thinking does not own:

- accepted Goal identity or Goal authority;
- Task identity or Task lifecycle;
- TaskContext lifecycle, selection, or revision authority;
- canonical Plan or PlanStep identity, criteria, readiness, or lifecycle;
- Core Governance authorization;
- execution permission.

Core Coordination must supply and validate Goal, Task, selected TaskContext,
and current TaskContext revision. Core Coordination must fail closed and may
not infer missing proposal semantics from text, policy reasons, risk, tools,
response prose, or metadata.

## 4. Required Proposal Semantics

The `ThinkingProposal` contract requires these semantic groups:

| Group | Required truth | Current production Thinking evidence |
|---|---|---|
| Proposal identity | distinct `proposal_id`, positive `proposal_revision`, proposal `created_at` | none; `session_id`, `trace_id`, approval ID, timestamps, and hashes are forbidden aliases |
| Authoritative binding | `goal_id`, `task_id`, `task_context_id`, current `task_context_revision` from Core Coordination | no Goal, Task, or selected TaskContext enters the current Thinking path |
| State | exactly `PROPOSAL_READY` or `PROPOSAL_NOT_READY` | policy `decision_type` is not proposal state |
| Ready objective | explicit non-empty `proposed_objective` | no objective field; normalized user text is not an authorized objective mapping |
| Ready criteria | explicit non-empty completion, failure, and blocked criteria | no three proposal criteria are produced |
| Proposal content | rationale, constraints, assumptions, dependencies, verification, risk, action/tool relations as distinct evidence | only legacy policy reasons, next step, blocked reason, risk/tool dictionaries exist; no authorized field mapping exists |
| Provenance | all required source categories, including Goal/Task/TaskContext, Thinking, risk, tool, and time references | no complete structured provenance envelope is produced |
| Not-ready result | structured `not_ready_reason` with an allowed category | clarification and policy reasons are not structured proposal failure reasons |

The canonical consumer accepts only an actual `ThinkingProposal`; it rejects
`PROPOSAL_NOT_READY`, stale context revisions, unselected contexts, and invalid
ownership bindings. It copies only the three explicit proposal criteria and
proposal provenance into the authoritative Plan. It does not provide a
missing producer or repair an incomplete proposal.

## 5. Current Production Thinking Path

The current policy implementation at `aether/thinking/policy.py:11-132`
accepts perception, risk, suggested-tool, identity-status, and metadata
dictionaries. It returns a legacy policy dictionary containing fields such as:

- `decision_type`;
- `confidence`;
- `reasons`;
- `required_user_confirmation`;
- `tool_suggestion_allowed` and `tool_execution_allowed`;
- `blocked_reason`;
- `clarification_question` and `next_step`;
- `warnings`.

The current loop at `aether/core/loop.py:28-332` obtains perception, identity
status, time, risk, a suggested tool, the policy dictionary, a legacy
authorization envelope, approval data, timeline data, and response text. It
does not create or receive a canonical Goal, Task, selected TaskContext,
`ThinkingProposal`, Plan, PlanStep, or canonical Plan Governance result.

The current path therefore proves a legacy policy producer, not a
`ThinkingProposal` producer. Its available values cannot truthfully fill the
canonical contract:

- `decision_type` cannot be substituted for `proposal_state`;
- `reasons`, `next_step`, `warnings`, `blocked_reason`, or `response_text`
  cannot be substituted for objective or criteria;
- normalized user text cannot silently become `proposed_objective`;
- risk level and tool suggestion are evidence references only, not criteria,
  PlanStep identity, approval, or execution authority;
- session, trace, approval, request, timestamp, tool, or text identifiers
  cannot become `proposal_id`;
- metadata cannot become authoritative Goal, Task, or TaskContext binding;
- existing time output cannot become proposal creation time without a producer
  contract that owns proposal identity and creation.

## 6. Production Producer Inventory

| Candidate source | Actual current behavior | Producer proof |
|---|---|---|
| `aether/thinking/policy.py` | Returns a legacy policy dictionary and does not construct `ThinkingProposal`. | NO |
| `aether/core/loop.py` | Orchestrates the legacy chat path and passes policy output to a legacy authorization gate. | NO |
| `POST /chat` / `AetherRuntime.process_chat` | Accepts text and session metadata and delegates to the legacy loop. | NO |
| Core Coordination | Owns authoritative process-local Goal/Task/TaskContext state and consumes a supplied proposal. | Consumer/owner, not a current Thinking producer |
| Tests and documentation | Construct or describe proposals for contract proof. | Test/document evidence only |

There is no current production Thinking provider, factory, adapter, API
caller, persistence path, or external runtime consumer that needs a
`ThinkingProposal`. The M98A result remains intact: the process-local consumer
is satisfied, while no external canonical runtime consumer is proven.

## 7. Candidate Producer Models

| Model | Decision | Evidence-based reason |
|---|---|---|
| `MODEL_A_LEGACY_POLICY_TO_PROPOSAL_ADAPTER` | REJECTED | The policy dictionary lacks binding, identity, criteria, state, and provenance. An adapter would invent or silently map semantics and would make the legacy path a competing cognitive authority. |
| `MODEL_B_CORE_LOOP_THINKINGPROPOSAL_PRODUCER` | REJECTED | The core loop has the same text-first legacy inputs and no authoritative Goal/Task/TaskContext handoff. Reusing its response or policy fields would violate non-fabrication rules. |
| `MODEL_C_COORDINATION_BOUND_PROPOSAL_PROVIDER` | NOT JUSTIFIED | A future provider could preserve ownership only after a real production use case, selected-context caller, complete producer contract, and separately authorized runtime design exist. None is currently proven. |
| `MODEL_D_NO_PRODUCTION_THINKINGPROPOSAL_PRODUCER_YET` | SELECTED | It is the only model supported by current production evidence and preserves the existing canonical ownership boundary without speculative runtime integration. |

Selected model:

```text
MODEL_D_NO_PRODUCTION_THINKINGPROPOSAL_PRODUCER_YET
```

Decision:

```text
D_NO_TRUTHFUL_PRODUCTION_THINKINGPROPOSAL_PRODUCER_CURRENTLY_JUSTIFIED
```

## 8. Non-Fabrication and Authority Boundary

M99A locks these negative rules:

1. No policy dictionary is a `ThinkingProposal` by name similarity.
2. No current input or output supplies a truthful proposal identity.
3. No current chat/session/trace path supplies authoritative Goal, Task, or
   selected TaskContext binding.
4. No policy reason, response field, risk field, tool suggestion, or metadata
   may be copied into canonical Plan criteria without a separately authorized
   mapping contract.
5. Clarification remains a policy/workflow result and does not become
   `PROPOSAL_NOT_READY` without structured proposal semantics and reason.
6. A proposal, even if later produced, remains non-authoritative and does not
   authorize a Plan, Governance, Generic Act, or Action execution.
7. No producer is justified merely to populate an unused process-local seam.

## 9. Future Producer Prerequisites

A separately authorized future milestone must first establish:

1. one concrete production use case and one owning runtime component;
2. a truthful accepted-Goal, Task, and explicitly selected TaskContext caller;
3. producer-owned proposal identity, revision, creation time, and lifecycle;
4. explicit ready and not-ready semantics with all required criteria;
5. complete structured provenance with source-category ownership preserved;
6. stale, terminal, superseded, conflicting, and missing-context behavior;
7. process lifetime, persistence, restart, and privacy behavior if scope crosses
   the current process-local boundary;
8. a consumer contract that preserves `GOVERNANCE_EVALUATION !=
   EXECUTION_AUTHORIZATION` and stops before Generic Act;
9. PM authorization before production code, API, persistence, or `/chat`
   changes.

These are prerequisites and proof requirements, not implementation
authorization.

## 10. Explicit Non-Goals and Write Set

M99A does not implement or authorize:

- a ThinkingProposal producer, adapter, provider, or factory;
- `/chat`, `AetherRuntime`, or core-loop wiring;
- Goal/Task/TaskContext integration outside existing Core Coordination;
- Plan, PlanStep, or Governance runtime changes;
- API, router, model, OpenAPI, persistence, queue, or database changes;
- Generic Act, Action dispatch, tool execution, or execution authorization;
- Observation Intake, Verification Aggregation, Critic, Repair, Learning,
  retry, scheduler, background execution, or restart restoration;
- `PROGRESS.md`, README, Constitution, Architecture, production code, or any
  existing test change;
- commit, tag, push, or PM acceptance claims.

The exact repository write set is:

1. `docs/architecture/MILESTONE_99A_THINKINGPROPOSAL_PRODUCTION_COMPATIBILITY_PRODUCER_PROOF_BOUNDARY.md`;
2. `tests/test_milestone_99a_thinkingproposal_production_compatibility_producer_proof_boundary.py`.

The PM summary is external to the repository:
`/home/aether/summaries/milestone_99A_producer_proof_summary.txt`.

## 11. Final M99A State

```text
ThinkingProposal contract class: PRESENT
Core Coordination process-local consumer: SATISFIED
Current production ThinkingProposal producer: ABSENT
Truthful production producer currently justified: NO
Selected model: MODEL_D_NO_PRODUCTION_THINKINGPROPOSAL_PRODUCER_YET
Legacy policy adapter: REJECTED
Core-loop producer: REJECTED
Coordination-bound provider: NOT JUSTIFIED
Runtime producer implementation: NOT AUTHORIZED
External canonical runtime consumer: NOT YET SATISFIED
Generic Act: NOT_IMPLEMENTED
Generic Act integration: NOT_AUTHORIZED
Generic Act authority: NOT_GRANTED
```

M99A is complete locally only when the static/document lock passes. That
result is not Git durability, PM acceptance, runtime approval, or Build
authorization.
