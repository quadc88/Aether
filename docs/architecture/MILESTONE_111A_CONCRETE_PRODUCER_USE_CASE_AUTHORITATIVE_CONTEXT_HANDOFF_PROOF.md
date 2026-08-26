# Milestone 111A Concrete Producer Use Case and Authoritative Context Handoff Proof

Classification: STRICT READ-ONLY CORE-ARCHITECTURE / USE-CASE / AUTHORITATIVE-CONTEXT-HANDOFF PROOF

Status: DESIGN / DISCOVERY ONLY / COMPLETE LOCALLY / GIT DURABILITY NOT CLAIMED / PM REVIEW PENDING

M111A determines whether a real production use case currently provides a
truthful authoritative Goal, Task, and selected TaskContext handoff into a
future ThinkingProposal producer. It does not implement Thinking, a producer,
an adapter, a runtime bridge, or any downstream consumer.

The binding authority boundaries remain:

```text
THINKING_PROPOSAL != EXECUTION_AUTHORIZATION
GOVERNANCE_EVALUATION != EXECUTION_AUTHORIZATION
```

## 1. Current Git State

Direct Git verification before the M111A write set:

- branch: `main`;
- HEAD: `ccec307c3005460f55befc0b82cd1d42971f6ab0`;
- local `main`: `ccec307c3005460f55befc0b82cd1d42971f6ab0`;
- `origin/main`: `ccec307c3005460f55befc0b82cd1d42971f6ab0`;
- remote `main`: `ccec307c3005460f55befc0b82cd1d42971f6ab0`;
- tracked worktree: clean before the M111A write set;
- `git diff --check`: clean;
- no commit, tag, or push is authorized.

The only repository write set is:

1. `docs/architecture/MILESTONE_111A_CONCRETE_PRODUCER_USE_CASE_AUTHORITATIVE_CONTEXT_HANDOFF_PROOF.md`;
2. `tests/test_milestone_111a_concrete_producer_use_case_authoritative_context_handoff_proof.py`.

The PM evidence summary is external to the repository:

```text
/home/aether/summaries/milestone_111A_context_handoff_proof_summary.txt
```

## 2. M110A Durable Baseline

M110A is the current durable baseline:

```text
M110A: FINALIZED / COMMITTED / TAGGED / PUSHED / PM-ACCEPTED
HEAD: ccec307c3005460f55befc0b82cd1d42971f6ab0
Commit: ccec307c3005460f55befc0b82cd1d42971f6ab0
Tag: milestone-110A-thinkingproposal-production-producer-reentry-proof-boundary
```

M110A locked the following state:

```text
Canonical ThinkingProposal contract: PROVEN
Production ThinkingProposal producer: ABSENT
Producer classification: P2_LEGACY_OR_NONCANONICAL_PRODUCTION_OUTPUT
Adapter readiness: A1_ADAPTER_WOULD_FABRICATE_SEMANTICS
External canonical runtime consumer: ABSENT
Future Build: NOT JUSTIFIED
Patch security: PAUSED
Generic Act: NOT_IMPLEMENTED / NOT_AUTHORIZED / NOT_GRANTED
```

The frozen M110A design hash is
`573c10271af6b99b9deaf740b17d43f40eca2194e0a7ff5fbea83c9c97d6a9d0`.
The frozen M110A static-test hash is
`d237e14b4089f35d5ba6ecaae53cf05d0cdcd5dd5c2651223897f7d9f02902f7`.

## 3. Historical Baseline

### M96

M96 established the authoritative process-local cognitive foundation:

```text
Human Authority
-> accepted Goal
-> Core Coordination Task
-> authoritative TaskContext
-> selected TaskContext
-> ThinkingProposal
-> canonical Plan
-> canonical PlanStep
-> Core Governance evaluation
-> STOP BEFORE GENERIC ACT
```

M96B owns the in-memory Goal, Task, and TaskContext foundation. Goal acceptance
requires an explicit authority reference. Task creation requires an accepted
Goal and atomically creates the first authoritative TaskContext. Selection is
explicit, snapshots are immutable, revisions are explicit, and invalid or stale
bindings fail closed.

M96F provides the process-local consumer boundary at
`CoreCoordination.materialize_thinking_proposal`. It consumes an already-built
proposal; it does not call Thinking or create one.

### M98A

M98A proved:

```text
Think -> Plan process-local consumer: SATISFIED
Think -> Plan consumer outside the process-local seam: NOT YET SATISFIED
External canonical runtime consumer: ABSENT
```

`/chat`, `AetherRuntime`, the core loop, memory routes, action services, and
similar legacy plan records were not canonical Goal-to-Plan consumers.

### M99A

M99A proved:

```text
ThinkingProposal contract class: PRESENT
Current production ThinkingProposal producer: ABSENT
MODEL_D_NO_PRODUCTION_THINKINGPROPOSAL_PRODUCER_YET
D_NO_TRUTHFUL_PRODUCTION_THINKINGPROPOSAL_PRODUCER_CURRENTLY_JUSTIFIED
```

The legacy policy dictionary lacks proposal identity, authoritative binding,
proposal state, objective, completion/failure/blocked criteria, and complete
provenance. A policy adapter would fabricate or alias those semantics.

### M109A

M109A proved:

```text
MODEL_D_NO_RUNTIME_CONSUMER_YET
D_NO_REAL_RUNTIME_CONSUMER_CURRENTLY_JUSTIFIED
External canonical runtime consumer: ABSENT
Durable/async canonical consumer: ABSENT
Selected PlanStep external runtime consumer: ABSENT
```

M109A's external-consumer conclusion remains unchanged by M111A.

### M110A

M110A rechecked the production Thinking path and found no meaningful producer
change since M99A. It identified the next frontier as:

```text
CONCRETE_PRODUCER_USE_CASE_AND_AUTHORITATIVE_CONTEXT_HANDOFF_PROOF
```

M111A addresses that frontier as a proof question only.

## 4. Qualifying-Use-Case Rule

A qualifying use case must have all of the following:

1. a real production entry point;
2. a real user or system intent;
3. a canonical Goal or a truthful source from which one already exists;
4. a real Task;
5. an authoritative TaskContext;
6. a concrete caller;
7. a concrete downstream need for Thinking or Plan output;
8. an identifiable trust or authority boundary;
9. non-test runtime value.

Tests, fixtures, documents, dead routes, developer helpers, synthetic examples,
and manual object construction without a live runtime caller do not qualify.

## 5. Production Entry-Point Inventory

| Entry point | Caller | Input | Runtime status / audience | Goal | Task | TaskContext | Thinking | Plan consumed | Authority boundary | Real production value |
|---|---|---|---|---|---|---|---|---|---|---|
| `POST /chat` (`api_server.py:223-309`) | FastAPI request handler | `ChatRequest.text` or legacy `message`, session and metadata | Live user-facing HTTP path | NO; text is legacy intent only | NO | NO | YES, legacy policy dictionary | NO | Legacy policy/approval envelope; not canonical Goal authority | Text response, perception, risk, policy, approval request, and timeline |
| `AetherRuntime.process_chat` (`core/runtime.py:99-113`) | `/chat` handler | Text, session, metadata, forced-false execution flag | Live runtime delegate | NO | NO | NO | YES through legacy loop | NO | Runtime owns Working Memory and delegates to legacy loop | Session Working Memory and chat response |
| `aether/core/loop.py:28-332` | `AetherRuntime.process_chat` | Text plus Working Memory and metadata | Live internal chat loop | NO | NO | NO | YES through `_evaluate_chat_policy_with_precedence` | NO | Legacy loop stages and Core Governance authorization envelope | Perception, risk, tool suggestion, policy, approval, timeline, response |
| `POST /memory/working/goal` (`memory_routes.py:46-48`) | FastAPI request handler | `GoalRequest.goal` string | Live system/user memory route | NO; stores a Working Memory string | NO | NO | NO | NO | Working Memory ownership, not GoalIntake authority | Sets a short-term display/session goal |
| `CoreCoordination.create_goal` / `accept_goal` | No production caller; tests only | Goal text and explicit authority reference | Production library code, process-local only | YES | NO | NO | NO | NO | GoalIntake and explicit human authority reference | Canonical Goal foundation, but no live use-case caller |
| `CoreCoordination.create_task` | No production caller; tests only | Accepted Goal plus task scope/constraints | Production library code, process-local only | Existing accepted Goal | YES | YES, first context atomically created | NO | NO | Core Coordination owns Task and initial context | Canonical Task/context foundation, no live runtime value |
| `CoreCoordination.select_context` | No production caller; tests only | TaskContext snapshot or ID | Production library code, process-local only | Existing Goal binding | Existing Task binding | YES; explicit selection history | NO | NO | Core Coordination selection and revision checks | Authoritative selected-context seam, no runtime caller |
| `CoreCoordination.materialize_thinking_proposal` | No production caller; tests only | Caller-supplied `ThinkingProposal` | Production consumer method, process-local only | Loaded by proposal ID | Loaded by proposal ID | Loaded and freshness-checked | NO; it consumes Thinking output | YES, canonical Plan | Core Coordination binding validation; no execution authority | Process-local Think-to-Plan consumer only |
| Action capability routes/services | HTTP callers and action workflows | Capability-specific requests and records | Live user/system-facing bounded action paths | NO canonical Goal | NO canonical Task | NO canonical TaskContext | Legacy policy/evidence where applicable | NO canonical Plan | Capability-specific approval, authority binding, dispatch, verification | Restricted read, patch, repair, simulation, and review workflows |
| Workers, schedulers, queues, event handlers | None for canonical path | Action-specific records/queue items only | No canonical worker, scheduler, event bridge, or async consumer found | NO | NO | NO | NO | NO | Action-specific record ownership | Existing queues support bounded action workflows, not canonical cognitive handoff |

The source search found `CoreCoordination`, `GoalIntake`, proposal
materialization, and proposal constructors only in the canonical production
definitions and tests. There is no production constructor or caller outside
those definitions. Existing queue modules are persistence helpers for bounded
Action workflows; they do not accept canonical Goal/Task/TaskContext identity
and do not create an asynchronous canonical consumer.

## 6. Goal Authoritative Source Proof

| Candidate source | Creator and input | Identity / lifecycle | Downstream availability | Classification |
|---|---|---|---|---|
| `CoreCoordination.create_goal` -> `GoalIntake.propose` | Core Coordination receives goal text and optional references; `Goal.propose` creates a UUID identity | Immutable dataclass snapshot; process-local registry; proposal status until explicit acceptance | Available only through the same coordinator instance; no live caller reaches Thinking | `G3_CANONICAL_PROCESS_LOCAL_PRODUCTION` |
| `CoreCoordination.accept_goal` -> `Goal.accept` | Core Coordination receives a Goal and explicit authority reference | Same Goal identity, accepted revision, accepted timestamp; acceptance rejects missing or approval-derived authority | Available to Core Coordination methods only; not handed from a runtime entry to Thinking | `G3_CANONICAL_PROCESS_LOCAL_PRODUCTION` |
| `POST /memory/working/goal` | Memory service receives a string and calls `runtime.working_memory.set_goal` | Working Memory value has no canonical Goal identity, acceptance, authority, or lifecycle | Not available to canonical Thinking | `G1_LEGACY_INTENT_ONLY` |
| `POST /chat` | Chat text is normalized by perception and passed to policy | Text/session/trace values are not canonical Goal identity or authority | Not available to canonical Thinking | `G1_LEGACY_INTENT_ONLY` |
| M96 tests | Test helper manually creates and accepts Goals | Canonical test objects, not a runtime caller | Test-only | `G2_CANONICAL_BUT_TEST_ONLY` |

The canonical Goal source is truthful inside `CoreCoordination`, including
identity, accepted revision, explicit authority reference, and process-local
survival. It does not survive a process boundary, and no production entry point
currently provides its identity to a downstream Thinking boundary.

## 7. Task Authoritative Source Proof

| Candidate source | Creator and relationship | Identity / derivation | Thinking reachability | Classification |
|---|---|---|---|---|
| `CoreCoordination.create_task` | Core Coordination creates the Task only from an accepted or active Goal and atomically creates its first TaskContext | Fresh `task_id`, explicit `goal_id`, task scope/constraints, status, revision, and context reference | No production caller; process-local methods can retrieve it | `T3_CANONICAL_PROCESS_LOCAL_PRODUCTION` |
| `/chat` loop | No Task creation; text remains in the legacy loop | Session and trace identifiers are not Task identity | Does not reach canonical Thinking | `T0_NONE` |
| Working Memory goal route | No Task creation | Working Memory event/goal state is not Task identity | Does not reach canonical Thinking | `T0_NONE` |
| Action-specific services | Create action records, attempts, plans, or approvals under separate contracts | Those IDs are not canonical Task IDs and are not Goal-owned | Do not reach canonical Thinking | `T1_LEGACY_TASK_LIKE_DATA` |
| M96 tests | Test helpers create Tasks from accepted Goals | Canonical but test-only caller | Test-only materialization | `T2_CANONICAL_TEST_ONLY` |

Task identity is truthful when created by Core Coordination, but there is no
production caller that creates a Task and preserves its identity into Thinking.

## 8. TaskContext Authoritative Source Proof

| Candidate source | Creator and contents | Selection / provenance | Thinking reachability | Classification |
|---|---|---|---|---|
| `CoreCoordination.create_task` | Creates one immutable initial context with `task_context_id`, `task_id`, `goal_id`, revision, task status, execution phase, and reference fields | The context is not silently selected; selection is a separate operation | Available within the same coordinator only | `C3_CANONICAL_PROCESS_LOCAL_AUTHORITATIVE` |
| `CoreCoordination.select_context` | Selects an existing context by object or identity and records selection history | Explicit selected ID, timestamp, prior selection, and current revision; fail-closed for terminal contexts | Available to a future same-process caller, but no production caller exists | `C3_CANONICAL_PROCESS_LOCAL_AUTHORITATIVE` |
| `/chat` and Working Memory | Working Memory and loop records are not TaskContext snapshots | No canonical context identity, revision, selection, or source ownership | Does not reach canonical Thinking | `C1_NONAUTHORITATIVE_CONTEXT` |
| M96 tests | Manually create/select canonical contexts | Canonical and authoritative only inside tests | Test-only | `C2_CANONICAL_TEST_ONLY` |

The selected context is authoritative within the owning `CoreCoordination`
instance. Its payload is an immutable snapshot and its revision is checked by
the existing materializer. This is process-local authority, not runtime
integration, durable authority, or evidence that a live producer can call it.

## 9. Core Coordination Handoff Review

Core Coordination already provides the following process-local pre-Thinking
seam:

```text
CoreCoordination.create_goal
-> CoreCoordination.accept_goal
-> CoreCoordination.create_task
-> CoreCoordination.context_for_task
-> CoreCoordination.select_context
-> selected_context_id + selected TaskContext snapshot
```

The exact boundary is `aether/core/task_context.py:453-483`, where
`select_context` sets the selected context identity and records selection
history. The exact downstream consumer boundary is
`aether/core/task_context.py:598-632`, where
`materialize_thinking_proposal` accepts a caller-supplied proposal and checks:

- Goal, Task, and TaskContext ownership;
- current TaskContext revision;
- explicit selected-context identity;
- non-terminal Task state;
- canonical binding before Plan materialization.

This proves an authoritative **process-local pre-Thinking handoff seam**. It
does not prove that Core Coordination invokes Thinking. The method receives
Thinking output; it does not produce it. No production caller invokes
`select_context`, `materialize_thinking_proposal`, `create_plan`, or canonical
Governance. Existing callers are tests.

Therefore:

```text
Authoritative process-local context seam: PRESENT
Qualifying runtime caller into the seam: ABSENT
Thinking boundary invocation from production: ABSENT
```

Process-local availability is not external runtime integration.

## 10. Legacy Thinking Caller Review

The current production Thinking caller is:

```text
POST /chat
-> AetherRuntime.process_chat
-> run_core_chat_loop
-> _evaluate_chat_policy_with_precedence
```

`aether/thinking/policy.py` receives perception, risk, an optional suggested
tool, identity status, and metadata. It returns a legacy policy dictionary.

| Required canonical input | Current legacy caller |
|---|---|
| Canonical Goal | ABSENT; text and metadata are not accepted Goal authority |
| Canonical Task | ABSENT |
| Authoritative TaskContext | ABSENT |
| Selected context identity/revision | ABSENT |
| IDs and provenance | Session/trace/approval/time values exist in surrounding code, but none is a canonical Goal/Task/TaskContext or proposal identity |
| Current position relative to coordination | Policy is called before and outside canonical Core Coordination; there is no canonical coordination call |
| Truthful future producer input | NOT AVAILABLE at this caller without a new runtime handoff contract |

`aether/core/coordination.py` is a separate restricted-read execution workflow.
It calls the legacy policy for action-specific authorization evidence and does
not call Core Coordination or create canonical cognitive objects. It is not a
ThinkingProposal caller.

## 11. `/chat` and `AetherRuntime` Review

`/chat` has no truthful bridge into canonical Goal/Task/TaskContext. Specifically
it is missing:

1. an explicit human-authority Goal acceptance input and owner;
2. a canonical Goal identity carried past request handling;
3. Core Coordination Task creation and Task identity;
4. authoritative TaskContext creation and explicit selection;
5. selected context revision/provenance at the Thinking boundary;
6. a proposal-owned identity, state, objective, criteria, and source envelope;
7. a downstream canonical Plan/PlanStep consumer contract.

`AetherRuntime` owns Working Memory and delegates directly to the legacy loop.
`aether/core/loop.py` has no call to `GoalIntake`, `CoreCoordination`,
`select_context`, `ThinkingProposal`, `materialize_thinking_proposal`,
`create_plan`, `create_plan_step`, or canonical Plan Governance.

The Working Memory route has a real runtime caller but only sets a string in
Working Memory. It cannot be treated as a canonical Goal admission route.
Blindly wiring either surface into Core Coordination would create new authority,
lifecycle, criteria, selection, and failure semantics. M111A does not propose
that wiring.

## 12. Context Handoff Traces

### Trace A: `/chat` legacy user interaction

```text
POST /chat
  producer: FastAPI handler
  consumer: AetherRuntime.process_chat
  identity: request text, optional session_id, metadata
  provenance: request metadata and legacy loop trace only
  process boundary: one API process, no canonical coordinator
  durability: Working Memory/timeline/approval records use separate contracts
  failure: input validation and policy gates fail safely; no canonical objects exist
      -> Goal: NOT CREATED; G1 legacy intent only
      -> Task: NOT CREATED; T0
      -> authoritative TaskContext: NOT CREATED; C0/C1
      -> selected TaskContext: NOT CREATED
      -> Thinking boundary: legacy policy dictionary only
      -> Thinking output: P2 legacy/noncanonical output
      -> proposal materialization: NOT CALLED
      -> Plan: NOT CREATED
```

Semantics remain truthful because this path does not claim canonical planning.
It cannot serve as a producer handoff without fabricating missing authority and
proposal semantics.

### Trace B: Working Memory goal route

```text
POST /memory/working/goal
  producer: memory router / memory service
  consumer: runtime.working_memory.set_goal
  identity: no canonical Goal identity; one string value
  provenance: route input only
  process boundary: runtime process Working Memory
  durability: Working Memory contract, not canonical Goal persistence
  failure: route/service validation only; no Goal acceptance transition
      -> Goal: G1 legacy intent only
      -> Task: NOT CREATED
      -> TaskContext: NOT CREATED
      -> Thinking: NOT INVOKED
      -> Plan: NOT CREATED
```

This is a real route with non-test value, but it is not a qualifying use case
for a canonical Thinking handoff.

### Trace C: Core Coordination process-local seam

```text
process-local caller (currently tests only)
  -> create_goal / GoalIntake.propose
  -> accept_goal with explicit authority reference
  -> create_task from accepted Goal
  -> initial authoritative TaskContext
  -> select_context
  -> selected TaskContext identity and immutable snapshot
  -> Thinking boundary: NO production caller or invocation exists
  -> caller-supplied ThinkingProposal: TEST EVIDENCE ONLY
  -> materialize_thinking_proposal
  -> canonical Plan
  -> explicit PlanStep
  -> evaluate_canonical_plan_governance
```

At each canonical process-local step, producer and consumer identities are
explicit and binding failures are fail-closed. The process boundary is the
single coordinator instance. Durability is in-memory only. The trace proves
the handoff seam is architecturally available, but not that a production
entry point reaches it.

### Trace D: Restricted-read capability workflow

```text
restricted-read route
  -> capability-specific approval binding
  -> policy/risk evidence
  -> restricted-read authority binding
  -> dispatch
  -> observation and verification
```

This workflow has real production value and a clear capability authority
boundary. It does not create canonical Goal, Task, selected TaskContext,
ThinkingProposal, Plan, or canonical Plan Governance state. It is not a
candidate handoff into Thinking, and M111A does not reopen its security work.

## 13. Real Use-Case Candidate Table

| Use case name | Production entry point | Goal | Task | TaskContext | Thinking caller | Downstream consumer | Runtime value | Authority risk | Semantic fabrication required | Handoff readiness |
|---|---|---|---|---|---|---|---|---|---|---|
| Legacy chat assistance | `POST /chat` | `G1_LEGACY_INTENT_ONLY` | `T0_NONE` | `C0_NONE` | Legacy policy | Text response and approval record, not canonical Plan | PROVEN | High if text is promoted to authority | YES | `H1_REAL_USE_CASE_CONTEXT_MISSING` |
| Working-memory goal setting | `POST /memory/working/goal` | `G1_LEGACY_INTENT_ONLY` | `T0_NONE` | `C0_NONE` | None | Working Memory summary | PROVEN | Medium if memory string is promoted to Goal | YES | `H1_REAL_USE_CASE_CONTEXT_MISSING` |
| Core Coordination process-local handoff seam | `CoreCoordination` methods; no live production caller | `G3_CANONICAL_PROCESS_LOCAL_PRODUCTION` | `T3_CANONICAL_PROCESS_LOCAL_PRODUCTION` | `C3_CANONICAL_PROCESS_LOCAL_AUTHORITATIVE` | No production Thinking caller; proposal consumers are test callers | Process-local Plan and Governance evaluation | Foundation value only; no qualifying runtime use case | Low inside owner, unresolved at runtime boundary | YES for a producer caller and proposal semantics | `H3_AUTHORITATIVE_PROCESS_LOCAL_HANDOFF_PROVEN` |
| Restricted-read capability workflow | Action routes/services | `G0_NONE` | `T1_LEGACY_TASK_LIKE_DATA` | `C1_NONAUTHORITATIVE_CONTEXT` | Legacy policy evidence only | Capability execution and verification | PROVEN | Capability authority is separate and bounded | YES | `H0_NOT_REAL_USE_CASE` |
| Canonical worker/scheduler/event handoff | No entry point found | `G0_NONE` | `T0_NONE` | `C0_NONE` | None | None | NOT PROVEN | No owner or boundary exists | YES | `H0_NOT_REAL_USE_CASE` |

The strongest candidate is the Core Coordination process-local seam, but it is
not itself a qualifying concrete production use case because it has no live
production caller and no Thinking invocation.

## 14. Selected Strongest Candidate

Selected use case:

```text
CORE_COORDINATION_PROCESS_LOCAL_AUTHORITATIVE_CONTEXT_HANDOFF_SEAM
```

This is a candidate seam, not a proven qualifying runtime use case.

| Required proof item | Evidence |
|---|---|
| Entry point | `CoreCoordination.create_goal`, `accept_goal`, `create_task`, and `select_context` |
| Goal source | `GoalIntake` creates a distinct Goal; `accept_goal` requires explicit non-approval authority reference |
| Task source | `create_task` requires accepted/active Goal and binds a fresh Task identity to it |
| TaskContext source | `create_task` atomically creates the first immutable authoritative context |
| Selected-context source | `select_context` stores selected identity and selection history; selection is explicit |
| Handoff boundary | `select_context` at `task_context.py:453-483`; proposal binding/materialization at `task_context.py:598-632` |
| Legacy/canonical Thinking relationship | Legacy policy is outside Core Coordination; no production canonical Thinking caller exists |
| Downstream need | Process-local `ThinkingProposal` consumption into canonical Plan and Governance evaluation |
| Authority boundary | Core Coordination owns Goal/Task/TaskContext binding; Thinking remains non-authoritative; Governance evaluates without execution authority |
| Runtime caller | NOT PROVEN; source search finds tests, not a production caller |
| Consumer value | Proven only as an in-memory architectural foundation and test-exercised process-local seam |

The seam provides truthful references and an authoritative selected snapshot to
a future same-process producer boundary, but the repository does not prove the
runtime entry that would invoke it. It therefore cannot justify producer Build.

## 15. Fabrication Check

No current qualifying production use case can supply all required producer
semantics. Using the legacy `/chat` caller would require fabricating or silently
aliasing:

- `proposal_id`;
- `proposal_revision`;
- proposal-owned `created_at`;
- `PROPOSAL_READY` or structured `PROPOSAL_NOT_READY` state;
- a proposed objective;
- completion criteria;
- failure criteria;
- blocked criteria;
- `thinking_proposal_source` provenance;
- the complete source envelope joining Goal, Task, selected TaskContext,
  Thinking, risk/tool evidence, and time;
- an authoritative Goal identity, Task identity, or TaskContext identity if the
  caller remains `/chat` or Working Memory.

The current process-local seam can provide Goal, Task, and selected
TaskContext references **only after** a real runtime caller enters Core
Coordination. It does not provide proposal identity, proposal state, objective,
criteria, or a producer-owned source envelope. There is no current
model/provider/inference provenance to invent, and the contract does not permit
inventing one.

Fabrication required: `YES` for any producer attempt from current live callers.
No producer Build or adapter is recommended.

## 16. Architecture-Level Handoff Contract

No implementation contract is authorized. The minimum future architecture
boundary, if separately authorized after a real caller is proven, is:

```text
authoritative runtime entry
  -> accepted Goal reference and provenance
  -> Core Coordination Task reference
  -> explicitly selected TaskContext reference and current revision
  -> truthful authoritative context snapshot
  -> Thinking producer-owned proposal identity/state/content/provenance
  -> CoreCoordination.materialize_thinking_proposal
```

A future handoff may consume:

- Goal identity/reference and accepted authority already owned by Core
  Coordination;
- Task identity/reference and current lifecycle state;
- selected TaskContext identity/reference and current revision;
- the authoritative context payload already owned by Core Coordination;
- request and evidence metadata already truthfully available from the runtime
  entry.

The future producer must own and truthfully create proposal identity, proposal
revision, proposal creation time, readiness state, proposal objective,
criteria, and Thinking source provenance. The handoff must fail closed on
missing authority, missing selection, stale revisions, terminal state,
conflicting ownership, missing criteria, or incomplete provenance.

The handoff must not invent execution authority, approval, Generic Act,
context provenance, user intent, Plan identity, or Action permission.

## 17. ThinkingProposal Semantic Compatibility

| Required semantic | Current evidence | Classification |
|---|---|---|
| Goal identity/reference | Core Coordination process-local seam | `AVAILABLE_BY_EXISTING_REFERENCE` |
| Task identity/reference | Core Coordination process-local seam | `AVAILABLE_BY_EXISTING_REFERENCE` |
| Selected TaskContext identity/reference | Explicit process-local selection | `AVAILABLE_BY_EXISTING_REFERENCE` |
| Authoritative context payload | Immutable selected context snapshot | `AVAILABLE_DIRECTLY` within same process |
| Current context revision | Core Coordination snapshot and materializer checks | `AVAILABLE_BY_EXISTING_REFERENCE` |
| Request/provenance metadata | Partial request, risk, tool, and time evidence in legacy path | `DERIVABLE_TRUTHFULLY` only where source ownership is preserved |
| Distinct proposal identity | No production producer | `MISSING` / `FABRICATION_REQUIRED` |
| Proposal revision and creation time | No producer-owned values | `MISSING` / `FABRICATION_REQUIRED` |
| Proposal ready/not-ready state | Legacy `decision_type` is not proposal state | `MISSING` / `FABRICATION_REQUIRED` |
| Proposed objective | No authorized mapping from text or policy | `MISSING` / `FABRICATION_REQUIRED` |
| Completion/failure/blocked criteria | No authoritative producer source | `MISSING` / `FABRICATION_REQUIRED` |
| Complete provenance | Goal/Task/Context/Thinking source handoff absent from live callers | `MISSING` / `FABRICATION_REQUIRED` |

The process-local handoff is therefore not sufficient for a full producer input
contract. It supplies a truthful authoritative context seam, not a complete
ThinkingProposal.

## 18. External-Consumer Separation

M109A remains unchanged:

```text
External canonical runtime consumer: ABSENT
Durable/async consumer: ABSENT
Selected PlanStep external consumer: ABSENT
```

The process-local `materialize_thinking_proposal` method is an immediate
consumer of a caller-supplied proposal. It is not an external runtime consumer,
durable consumer, asynchronous consumer, PlanStep executor, or Action
authority. M111A proves producer-input context readiness only; it does not
activate Goal-to-Plan consumption.

## 19. Final Classifications

```text
Concrete production use case: NOT PROVEN
Selected use case: CORE_COORDINATION_PROCESS_LOCAL_AUTHORITATIVE_CONTEXT_HANDOFF_SEAM
Goal classification: G3_CANONICAL_PROCESS_LOCAL_PRODUCTION in Core Coordination; G1 for live chat inputs
Task classification: T3_CANONICAL_PROCESS_LOCAL_PRODUCTION in Core Coordination; T0 for live chat inputs
TaskContext classification: C3_CANONICAL_PROCESS_LOCAL_AUTHORITATIVE in Core Coordination; C0/C1 for live chat inputs
Authoritative context handoff: PROVEN process-locally only
Handoff classification: H3_AUTHORITATIVE_PROCESS_LOCAL_HANDOFF_PROVEN
Producer input readiness: R2_PARTIAL_TRUTHFUL_CONTEXT_AVAILABLE
Real production caller: NOT PROVEN
Fabrication required: YES for any current producer attempt
Goal identity truthful: YES within Core Coordination; NO at current live Thinking caller
Task identity truthful: YES within Core Coordination; NO at current live Thinking caller
TaskContext identity truthful: YES within Core Coordination; NO at current live Thinking caller
Context provenance truthful: PARTIAL in the seam; NOT COMPLETE at a live producer boundary
ThinkingProposal input semantics sufficient: NO
External canonical runtime consumer: ABSENT
Durable/async consumer: ABSENT
```

H3 is deliberately process-local. It is not H4 and does not assert a runtime
caller or a production Thinking invocation.

## 20. Model Comparison

| Model | Result | Evidence |
|---|---|---|
| `MODEL_A_CONCRETE_AUTHORITATIVE_HANDOFF_NOW_PROVEN` | REJECTED | No qualifying production caller reaches the canonical seam, and no full producer input contract is available. |
| `MODEL_B_PROCESS_LOCAL_HANDOFF_PROVEN_BUT_RUNTIME_CALLER_MISSING` | SELECTED | Core Coordination provides truthful process-local Goal/Task/selected-TaskContext authority and binding checks, but source review finds no qualifying runtime caller. |
| `MODEL_C_REAL_USE_CASE_EXISTS_BUT_CONTEXT_NOT_AUTHORITATIVE` | NOT SELECTED | `/chat` and Working Memory have real runtime value, but they are legacy intent surfaces rather than a qualifying concrete producer use case; the stronger canonical seam exists separately and remains callerless. |
| `MODEL_D_NO_CONCRETE_PRODUCER_USE_CASE_CURRENTLY_JUSTIFIED` | NOT SELECTED | A process-local authoritative handoff seam is proven, so the evidence is stronger than no seam; the missing proof is the runtime caller. |
| `MODEL_E_EVIDENCE_INSUFFICIENT` | REJECTED | Direct source, caller, route, queue, and historical-record review is sufficient for the bounded Model B result. |

Selected model:

```text
MODEL_B_PROCESS_LOCAL_HANDOFF_PROVEN_BUT_RUNTIME_CALLER_MISSING
```

## 21. Principal Decision

```text
Selected model: MODEL_B_PROCESS_LOCAL_HANDOFF_PROVEN_BUT_RUNTIME_CALLER_MISSING
Selected use case: CORE_COORDINATION_PROCESS_LOCAL_AUTHORITATIVE_CONTEXT_HANDOFF_SEAM
Handoff classification: H3_AUTHORITATIVE_PROCESS_LOCAL_HANDOFF_PROVEN
Producer input readiness: R2_PARTIAL_TRUTHFUL_CONTEXT_AVAILABLE
Principal decision: B_RUNTIME_ENTRY_TO_AUTHORITATIVE_CONTEXT_PROOF_REQUIRED_NEXT
Next frontier: QUALIFYING_RUNTIME_ENTRY_TO_AUTHORITATIVE_CONTEXT_HANDOFF_PROOF
Next milestone type: RUNTIME-ENTRY / AUTHORITATIVE-CONTEXT-HANDOFF-PROOF
Future Build: NOT JUSTIFIED
```

The exact missing proof is a real production runtime caller that can enter the
existing Core Coordination seam with a truthful accepted Goal, create or bind
the Task, explicitly select the authoritative TaskContext, and preserve the
identity/revision/provenance boundary into a future Thinking producer. The
producer itself must not be built until that caller and contract are separately
authorized and proven.

## 22. Alternative Core Frontiers for PM Prioritization

These are proof frontiers only, not implementation authorization:

1. **Canonical chat-entry authority proof:** determine whether a future
   user-facing entry can establish explicit Goal authority and enter the
   existing Core Coordination seam without making `/chat` a competing
   authority.
2. **Capability-workflow-to-context proof:** determine whether one existing
   capability workflow has a truthful system intent and owner that can bind to
   Goal/Task/TaskContext without importing Action authority into Thinking.
3. **Runtime supervisor/context-lifetime proof:** determine whether an existing
   system-facing runtime supervisor can own process lifetime, selection,
   cancellation, stale-state, and restart boundaries for the process-local
   context seam, without adding a worker or persistence implementation.

None is selected as a Build. The selected next frontier remains proof of a
qualifying runtime entry into the existing seam.

## 23. Authority Non-Escalation and Security Pause

The following remain unchanged:

```text
THINKING_PROPOSAL != EXECUTION_AUTHORIZATION
GOVERNANCE_EVALUATION != EXECUTION_AUTHORIZATION
Goal/Task/TaskContext ownership does not grant Action permission
```

Generic Act:

```text
Generic Act: NOT_IMPLEMENTED
Generic Act integration: NOT_AUTHORIZED
Generic Act authority: NOT_GRANTED
```

Patch security remains paused. M105B F03 remains resolved and M107B F02
final-workflow remains addressed. M111A does not inspect, modify, or reopen
patch-security findings.

## 24. Explicit Non-Goals

M111A does not implement or authorize:

- a ThinkingProposal producer, adapter, provider, factory, model, or inference runtime;
- changes to `aether/thinking/policy.py` or any Thinking runtime behavior;
- changes to Core Coordination runtime behavior;
- `/chat`, `AetherRuntime`, or `aether/core/loop.py` wiring;
- Goal-to-Plan runtime consumption or an external consumer;
- persistence, restart restoration, worker, scheduler, queue, event, or async integration;
- PlanStep execution, Action dispatch, or execution authority;
- Generic Act or capability generalization;
- patch-security work;
- changes to `PROGRESS.md`, README, Constitution, Architecture authority, production code, existing tests, dependencies, or runtime/private data;
- commit, tag, push, or PM acceptance claims.

## 25. Next-Step Gate

M111A is complete locally when this design record and its static/document lock
pass. That result is not Git durability, PM acceptance, runtime approval,
producer authorization, or Build authorization.

```text
Next authorized action: HUMAN/PROJECT-MANAGER M111A HANDOFF-PROOF REVIEW
```
