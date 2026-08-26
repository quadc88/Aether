# Milestone 113A Canonical Goal-Intake Runtime-Entry Ownership Decision

Classification: STRICT READ-ONLY AUTHORITY / RUNTIME-ENTRY CONTRACT DECISION

Status: DESIGN / DISCOVERY ONLY / COMPLETE LOCALLY / GIT DURABILITY NOT CLAIMED / PM REVIEW PENDING

M113A decides which component must own a future canonical Goal-intake
runtime-entry contract. It does not implement a Goal API, a runtime entry,
`/chat` wiring, an interpretation classifier, a producer, persistence, or any
successor runtime.

The selected ownership model is an architectural decision only. It is not a
production implementation, Build authorization, API authorization, or runtime
approval.

The binding authority boundaries remain:

```text
THINKING_PROPOSAL != EXECUTION_AUTHORIZATION
GOVERNANCE_EVALUATION != EXECUTION_AUTHORIZATION
GOAL/TASK/TASKCONTEXT OWNERSHIP != ACTION PERMISSION
```

## 1. Git Baseline and Write Boundary

Git was verified directly before this M113A write set:

```text
branch: main
HEAD: f1664e8c02a8565cb59b8143f0c6551dbf23fdcb
main: f1664e8c02a8565cb59b8143f0c6551dbf23fdcb
origin/main: f1664e8c02a8565cb59b8143f0c6551dbf23fdcb
remote main: f1664e8c02a8565cb59b8143f0c6551dbf23fdcb
M112A tag: milestone-112A-qualifying-runtime-entry-proof-boundary
M112A tag peeled target: f1664e8c02a8565cb59b8143f0c6551dbf23fdcb
tracked worktree: clean
git diff --check: clean
untracked files before M113A: none
```

The only repository files authorized for M113A are:

1. `docs/architecture/MILESTONE_113A_CANONICAL_GOAL_INTAKE_RUNTIME_ENTRY_OWNERSHIP_DECISION.md`;
2. `tests/test_milestone_113a_canonical_goal_intake_runtime_entry_ownership_decision.py`.

No tracked file is modified. `PROGRESS.md`, README, Constitution, Architecture,
production code, existing tests, dependencies, routes, APIs, and runtime/private
data remain outside the M113A write set. The summary is external:

```text
/home/aether/summaries/milestone_113A_goal_intake_ownership_decision_summary.txt
```

## 2. Project and Milestone Journey

M86 established the one-mind architecture, Core Governance, Core Coordination,
the Authoritative Shared Cognitive Context framework, ownership separation, and
the AetherOS mechanism boundary. AetherOS provides mechanisms and facts; it does
not own identity, Human Authority, Goal acceptance, Task ownership, context,
Governance judgment, or completion criteria.

M96 established the process-local canonical path:

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

M96 established Goal Intake/Human Authority ownership of Goal, Core Coordination
ownership of Task and TaskContext, immutable revisions, explicit selection, and
fail-closed bindings. The Goal, Task, TaskContext, Plan, PlanStep, and Governance
objects remain process-local. The M96 materializer consumes a caller-supplied
ThinkingProposal; it does not produce one.

M97A refused Generic Act without a truthful governed consumer. M98A found no
external production Goal-to-Plan consumer. M99A found no truthful production
ThinkingProposal producer. M100A identified live action-authority divergence,
while preserving the refusal to activate dormant cognitive foundations.

M101A and M101B bounded one capability-specific restricted-read authority binding
without creating a generic authority registry. M102A found no truthful second
capability binding. M103A through M107B reviewed and bounded patch-security
findings without selecting universal patch authority. M108A paused patch-security
implementation and returned to a core consumer-proof frontier.

M109A confirmed that the external Goal-to-Plan runtime consumer is absent. M110A
confirmed that the production Thinking path remains legacy/noncanonical and has
no truthful producer. M111A proved the authoritative Goal/Task/selected-
TaskContext handoff process-locally, but found no live production caller.

M112A found live runtime entries but classified them as:

```text
RTE1_LIVE_NONCANONICAL_ENTRY
MODEL_E_NO_QUALIFYING_RUNTIME_ENTRY_CURRENTLY_PROVEN
E_NO_QUALIFYING_RUNTIME_ENTRY_CURRENTLY_PROVEN
```

M112A selected this frontier:

```text
CANONICAL_GOAL_INTAKE_RUNTIME_ENTRY_OWNERSHIP_DECISION
```

M113A addresses ownership and contract readiness only. It does not turn the
frontier into implementation.

## 3. Exact Objective and Decision Vocabulary

M113A answers:

1. what a canonical Goal-intake runtime entry is;
2. which component owns the canonical Goal-intake contract;
3. how transport, interpretation, proposal, acceptance, context, lifecycle,
   provenance, and execution authority remain separate;
4. whether proposal and acceptance must be separate;
5. the safe future relationship with `/chat`, Working Memory, AetherRuntime,
   AetherOS, and Action workflows; and
6. whether a bounded future Build is justified for PM review.

M113A does not classify natural language generally. It records the minimum
explicit information and authority required for a future interpretation or
transport contract. It does not claim that any current live component supplies
that contract.

## 4. Current Production Source Review

### 4.1 Canonical Goal source

`aether/core/goal.py` contains the process-local `Goal` and `GoalIntake`.
`Goal.propose` creates a distinct `goal_id`, stores `goal_text`, optional
`requested_outcome`, constraints, and an optional authority reference. A Goal
starts as `proposed`.

`Goal.accept` requires a non-empty `authority_reference`, rejects an
`approval_*` string as Goal authority, and creates an accepted revision. The
current reference is a raw string. It is sufficient for the process-local M96
tests, but it is not a typed live Human Authority envelope.

`GoalIntake` is an in-memory registry. It has no production caller from an
interface, runtime, memory route, worker, queue, or event handler.

### 4.2 Core Coordination source

`aether/core/task_context.py` contains `CoreCoordination` and the canonical
process-local state. It owns:

- Goal Intake access and Goal lookup;
- Task creation from an accepted or active Goal;
- atomic creation of the first TaskContext with the Task;
- immutable TaskContext revisions;
- explicit context selection and selection history;
- canonical Plan and PlanStep creation;
- ThinkingProposal materialization;
- canonical Plan Governance request assembly.

Core Coordination owns Goal/Task/TaskContext canonical state. Core Coordination
owns Task and first authoritative TaskContext creation after Goal acceptance.

No production module instantiates `CoreCoordination` or calls its Goal, Task,
TaskContext, selection, Plan, or Governance methods. Existing callers are tests
and definitions. This is canonical owner proof, not live entry proof.

### 4.3 `/chat` and AetherRuntime

The live chain is:

```text
POST /chat
-> api_server.chat
-> AetherRuntime.process_chat
-> run_core_chat_loop
-> perception / risk / tool suggestion / legacy Thinking policy
-> legacy Governance authorization envelope / approval request / response
```

`ChatRequest` transports `text`, legacy `message`, optional `session_id`, broad
`metadata`, and an ignored-for-execution `allow_tool_execution` flag. The route
prefers `text` and falls back to `message`. It does not transport a Goal ID,
requested-outcome authority, authority envelope, proposed Goal revision, or
acceptance operation.

`AetherRuntime` owns process readiness and one process-local Working Memory. It
delegates chat to the legacy loop. It does not own canonical Goal semantics.

The loop records Working Memory and Timeline events, classifies risk, calls the
legacy Thinking policy, builds a legacy authorization envelope, creates pending
approval records where required, and returns a structured response. It does not
call `GoalIntake`, `create_task`, `select_context`, `ThinkingProposal`, Plan
materialization, or canonical Plan Governance.

### 4.4 Working Memory

`WorkingMemory.current_goal` is a mutable process-local string. The route
`POST /memory/working/goal` transports only `GoalRequest.goal` and calls
`runtime.working_memory.set_goal`.

Working Memory has no canonical Goal ID, `authority_reference`, requested-outcome
owner, acceptance transition, Task binding, TaskContext selection, revision,
Goal provenance, or completion criteria. It remains a truthful legacy intent and
session-state surface, not Goal authority.

### 4.5 Action and approval workflows

The interface routers and services contain live capability-specific workflows for
restricted read, patch, rollback, tools, approvals, dry runs, simulations,
verification, evidence, repair, self-modification, and observations. They own
their own records, approvals, action attempts, dispatch, and verification
contracts.

The restricted-read path has the strongest bounded authority contract. It uses
an exact command, capability, target, permission, max-character bound, approval
fingerprint, optional session binding, fresh risk and identity evidence, a
Governance-minted scope, a single-use claim, dispatch, call-local Observation,
and immediate Verification. It is not canonical Goal authority.

Action approval is capability-specific. An approval record, approval ID, queue
item, execution attempt, or Action ID must not be promoted into Human Authority
for Goal acceptance.

### 4.6 Thinking and Governance

`aether/thinking/policy.py` returns a legacy policy dictionary. It does not create
`ThinkingProposal`, call a model provider, or own Goal acceptance. Its
`decision_type`, reasons, clarification text, risk, and tool fields cannot be
silently mapped to canonical Goal, proposal, or Plan semantics.

`aether/thinking/proposal.py` defines an immutable non-authoritative
`ThinkingProposal` contract. It requires distinct proposal identity and
revision, accepted Goal/Task/selected TaskContext references, criteria, state,
and complete provenance. No production producer exists.

Core Governance owns authorization and hard constraints. Canonical Plan
Governance evaluates a process-local Plan and selected PlanStep before Generic
Act, with authorization and execution flags permanently false.

## 5. Canonical Goal-Intake Runtime-Entry Rule

A canonical Goal-intake runtime entry is not merely a route, a text field, a
Working Memory string, or a Goal-like record. It is a transport-to-owner
boundary that:

1. receives a typed request from a real user or system caller;
2. preserves raw text and interface/source metadata without treating them as
   authority;
3. identifies the input operation or carries an explicit interpretation result;
4. distinguishes conversation, information, Goal operations, continuation,
   cancellation, and Action authorization;
5. carries a truthful requested outcome and explicit constraints when proposing
   a Goal;
6. reaches the canonical GoalIntake/Core Coordination owner;
7. preserves the exact proposed Goal identity and revision;
8. accepts a Goal only through a valid Human Authority source;
9. lets Core Coordination create the Task and first authoritative TaskContext;
10. explicitly selects the TaskContext and preserves its current revision;
11. preserves source, interface, human-authority, time, and provenance references;
12. fails closed on missing authority, ambiguous operation, stale identity,
    invalid lifecycle, missing provenance, or ownership conflict; and
13. does not create a ThinkingProposal or authorize Action merely by admitting a
    Goal.

The entry transports a request. It does not become the owner of canonical Goal,
Task, TaskContext, Governance, completion, or Action authority.

## 6. Required Input-Type Distinction

The following categories are distinct. A future interpretation contract may
propose a category, but current production has no truthful owner that performs
this complete classification. No general natural-language classifier is
designed or authorized by M113A.

| Input type | Goal transition by default | Required owner or evidence |
|---|---|---|
| `CONVERSATION` | None | Future interpretation contract; no canonical owner currently proven |
| `QUESTION` | None | Future interpretation contract; answer path is not Goal acceptance |
| `INFORMATION REQUEST` | None | Future interpretation contract; requested information is not a Goal automatically |
| `STATUS INQUIRY` | None; read an existing owner-owned record only | Core Coordination for canonical Goal/Task status; no current runtime bridge |
| `REFERENCE TO AN EXISTING GOAL OR TASK` | None; reference must resolve exactly | Core Coordination owns identity lookup; no current live caller |
| `CONTINUATION OF AN EXISTING GOAL` | No new Goal; continuation is an existing Task/Goal lifecycle operation | Core Coordination owns continuation state; Human Authority scope must remain valid |
| `PAUSE REQUEST` | No new Goal | Core Coordination owns task state; valid Human Authority is required |
| `CANCELLATION REQUEST` | No new Goal | Core Coordination owns lifecycle transition; valid Human Authority is required |
| `CORRECTION OF AN EXISTING GOAL` | No implicit replacement; exact Goal revision must be identified | GoalIntake/Core Coordination owns a future revision contract; current live owner unproven |
| `CLARIFICATION RESPONSE` | Does not automatically accept or create a Goal | Future interpretation contract must bind it to a pending clarification; current owner unproven |
| `PROPOSED NEW GOAL` | Creates a `proposed` Goal only | GoalIntake/Core Coordination owns identity and proposal state |
| `EXPLICIT GOAL ACCEPTANCE` | Accepts one exact proposed Goal only | Human Authority supplies valid acceptance evidence; Core Coordination applies transition |
| `ACTION AUTHORIZATION` | Never a Goal acceptance by itself | Core Governance and capability-specific Action owner; Goal authority remains separate |

Raw text, a session ID, metadata, an approval ID, a response, or a Working
Memory value cannot silently select one of these types as a canonical Goal
transition.

## 7. Ownership Table

The table distinguishes transport, proposal, canonical ownership, authority,
execution, evidence, and verified completion. `UNPROVEN` means the repository
does not currently prove a live owner for that boundary.

| Semantic category | Mechanism/transport | Canonical owner | Authority or evidence status |
|---|---|---|---|
| Raw transport | Interface or future transport adapter | Interface owns transport only | No cognitive authority |
| Raw user text | Request body and source capture | Interface preserves it; future interpretation may read it | Not a Goal by itself |
| Interface metadata | Interface request metadata | Interface preserves source metadata | Metadata is provenance input, not authority |
| Session identity | Runtime/session transport | A future runtime context contract; current session is metadata only | Not Goal, Task, or context identity |
| Requested-outcome interpretation | Future Thinking/interpretation contract | `UNPROVEN` in current production | Must propose, not accept, authority |
| Proposed Goal identity | GoalIntake under Core Coordination | Core Coordination/GoalIntake | Process-local `Goal.propose` is proven |
| Goal `requested_outcome` | Goal proposal payload | GoalIntake stores the canonical field | Human/interpretation source must be explicit |
| Goal constraints | Goal proposal payload | GoalIntake stores canonical constraints | Governance may constrain later; it does not rewrite Goal authority |
| Goal provenance | Source and authority envelope | GoalIntake under Core Coordination | Current Goal has incomplete live provenance |
| Goal acceptance | Typed acceptance transition | Core Coordination/GoalIntake applies it | Human Authority must supply valid evidence |
| Human Authority reference | Explicit authority envelope | Human Authority is the source; Core Coordination validates the boundary | Current raw string is too weak for a live contract |
| Goal lifecycle | Goal state transitions | Core Coordination/GoalIntake | Current propose/accept/reject only; live lifecycle is unproven |
| Task creation | Accepted Goal binding | Core Coordination | Process-local atomic Goal -> Task -> first context is proven |
| Task lifecycle | Task state and revision | Core Coordination | Current live lifecycle entry is unproven |
| TaskContext creation | Task creation operation | Core Coordination | Authoritative process-locally |
| TaskContext selection | Explicit selection operation | Core Coordination | Authoritative process-locally; no live caller |
| TaskContext revision | Immutable context evolution | Core Coordination | Freshness and stale-state checks are process-local |
| Current-context switch | Explicit switch operation | Core Coordination | No silent switch or merge |
| Time facts | Clock and runtime mechanisms | Time/AetherOS supplies facts; Time interprets them | Time facts do not grant authority |
| Governance evaluation | Canonical evaluation request/result | Core Governance | Non-authorizing; before Generic Act |
| ThinkingProposal production | Proposal construction | Thinking | Current production owner absent; proposal remains non-authoritative |
| Plan materialization | Caller-supplied proposal consumer | Core Coordination | Process-local only; no execution authority |
| Action authorization | Capability policy and approval boundary | Core Governance plus capability-specific owner | Never inferred from Goal ownership |
| Action execution | Capability dispatch | Action services/Action | Only within applicable authorization |
| Observation | Capability-specific result evidence | Observation boundary or capability owner | Call-local restricted-read Observation is separate |
| Verification | Outcome evidence assessment | Verification | Supplies evidence and status, not Goal or Action authority |
| Commitment continuation | Authorized Goal/Task continuation state | Core Coordination, with Governance constraints | No Commitment runtime or live continuation owner exists |

No interface, runtime, memory object, or Action workflow owns every category.

## 8. Goal proposal contract

A future Goal proposal is a non-accepted candidate. It may contain:

- raw goal text;
- a requested outcome supplied or explicitly confirmed by the human;
- explicit constraints;
- source interface and source message/reference;
- source caller identity where truthfully available;
- event, observation, and recording time references as distinct facts;
- non-authoritative provenance metadata; and
- a distinct immutable proposed Goal identity and revision owned by GoalIntake.

A proposal must not claim:

- accepted Human Authority;
- Goal acceptance;
- Task identity;
- selected TaskContext;
- completion criteria as canonical Plan criteria;
- ThinkingProposal identity;
- Plan identity;
- Governance authorization; or
- Action authorization.

The proposal operation must fail closed when requested outcome, source, required
constraints, or provenance is missing or ambiguous. It must not infer a
requested outcome from arbitrary conversation text without an explicit future
interpretation contract.

## 9. Goal acceptance contract

Acceptance is a separate authority-bearing transition. It must identify:

- the exact proposed Goal ID;
- the exact proposed Goal revision or proposal digest;
- a typed Human Authority envelope or separately proven authority source;
- the accepting actor or authority identity;
- acceptance time and relevant time semantics;
- the authority scope and applicable expiry or validity boundary;
- any explicitly authorized correction to requested outcome or constraints; and
- the resulting accepted Goal revision.

Acceptance must fail closed when the Goal is missing, already terminal, stale,
ambiguous, owned by another coordinator, missing valid authority, outside the
authority scope, expired, or bound to an Action approval instead of Goal
authority.

Goal acceptance creates no TaskContext implicitly in the acceptance record. Core
Coordination may then create the Task and first authoritative TaskContext through
its own operation, preserving the accepted Goal identity and revision.

## 10. Proposal and Acceptance Separation

The default decision is:

```text
PROPOSE GOAL and ACCEPT GOAL: SEPARATE OPERATIONS
```

The separation is required because proposal records possible intent while
acceptance grants authoritative Goal status. Keeping them distinct prevents
conversation, interpretation, and authority from collapsing into one operation.

A combined operation is not part of the current contract and is not justified
for a future Build by M113A. A later decision could permit an explicit combined
operation only if all of the following are present in one typed request:

- an explicit operation meaning `PROPOSE_AND_ACCEPT_GOAL`, not ordinary text;
- a complete requested outcome and constraints;
- an immutable Human Authority envelope with actor, source, scope, time,
  validity/expiry, and request identity;
- exact binding between the authority envelope and the proposed Goal content;
- a fresh proposed Goal identity and revision;
- no use of an Action approval ID as Goal authority;
- atomic failure before either accepted state is exposed when any check fails; and
- a response that distinguishes proposed and accepted revisions.

Until that contract is separately proven, a single operation must not infer that
an untyped message both proposes and accepts a Goal.

## 11. Human Authority and `authority_reference` Review

The current `Goal.authority_reference` is a non-empty arbitrary string except
that strings beginning with `approval_` are rejected. Existing tests use values
such as `human:event-1`. This proves a process-local reference boundary, not a
typed live authority contract.

The current field is too weak for a future live entry because it does not
structurally bind:

- actor or human identity;
- source interface and source message/request identity;
- authority scope;
- requested Goal or exact Goal revision;
- acceptance time versus event time;
- expiry or validity period;
- authority generation or revocation state;
- correction scope; or
- provenance of how the reference was obtained.

A future live boundary requires an immutable Human Authority envelope or an
equivalent typed contract. It should carry actor/source identity, exact Goal
proposal binding, scope, event/acceptance time, validity or expiry, and a
non-replayable request or authority revision where the authority model requires
it. M113A does not implement that object.

Existing Action approval records cannot serve as Goal authority. They are
capability-specific, may authorize a restricted read or mutation workflow, and
have different status, fingerprint, scope, claim, and consumption semantics.
Human review of an Action is not automatically acceptance of a cognitive Goal.

Adding a typed authority envelope plus a live transport, lifecycle, and
provenance contract exceeds a small proven Build boundary at this point.

## 12. Chat Relationship

Current `/chat` remains a legacy conversation and policy route. It does not own
canonical Goal intake and must not automatically turn each message into a Goal.

A future interface may transport explicit requests for:

- conversation or question handling;
- a proposed Goal;
- clarification of a pending proposal;
- reference to an existing Goal or Task;
- status of an existing Goal or Task;
- continuation, pause, or cancellation; or
- acceptance of an exact previously proposed Goal.

Any such request must delegate canonical transitions to GoalIntake/Core
Coordination. A chat route may never directly grant Action authority. It must
not map a policy `decision_type`, approval request, session ID, or response text
into Goal authority.

The current evidence does not justify wiring `/chat` to Core Coordination. The
safe future relationship is transport-only and explicit. Chat interpretation,
if later selected, requires a separate interpretation contract and must preserve
the distinction between conversation and Goal operations.

## 13. Working Memory Relationship

Working Memory may reference a canonical Goal ID, selected TaskContext ID,
current task summary, recent interaction, or temporary interpretation state after
a truthful canonical handoff exists.

Working Memory must not independently define or overwrite:

- canonical Goal identity or requested outcome;
- Goal acceptance or Human Authority;
- Task identity or lifecycle;
- TaskContext identity, selection, or revision;
- completion criteria;
- Governance evaluation; or
- Action authority.

The existing Working Memory `current_goal` string remains legacy/non-authoritative
input. It may be deprecated or replaced only through a separately authorized
compatibility decision. M113A does not modify it.

## 14. Runtime and AetherOS Relationship

AetherRuntime may safely own, in a future bounded contract:

- one process-local CoreCoordination instance;
- initialization and shutdown;
- process lifetime;
- routing between interfaces and Core Coordination; and
- access to the currently selected context through owner APIs.

AetherRuntime must not thereby own:

- requested-outcome interpretation;
- Goal acceptance;
- Human Authority;
- TaskContext selection policy;
- Governance decisions;
- ThinkingProposal content;
- completion criteria; or
- Action authorization.

AetherOS provides clocks, processes, storage mechanisms, network mechanisms, and
other runtime facts. It does not own cognitive semantics, Goal acceptance,
TaskContext authority, Governance, or completion judgment.

## 15. Candidate Ownership Models

| Model | Disposition | Evidence-based reason |
|---|---|---|
| `MODEL_A_CHAT_DIRECTLY_OWNS_AND_ACCEPTS_CANONICAL_GOALS` | REJECTED | `/chat` is text-first, has no typed Human Authority source, and automatic acceptance would turn every message into a Goal and make the route a competing authority. |
| `MODEL_B_WORKING_MEMORY_GOAL_IS_PROMOTED_TO_CANONICAL_GOAL` | REJECTED | The current string has no Goal identity, authority, acceptance, lifecycle, revision, or provenance. |
| `MODEL_C_AETHERRUNTIME_OWNS_CANONICAL_GOAL_INTAKE` | REJECTED | Process lifetime and Working Memory ownership do not make AetherRuntime a cognitive or Human Authority owner. |
| `MODEL_D_CORE_COORDINATION_OWNS_INTERFACE_AGNOSTIC_GOAL_INTAKE` | SELECTED | M96 proves Core Coordination/GoalIntake as the only canonical process-local Goal/Task/TaskContext owner; interfaces can transport requests without owning semantics. |
| `MODEL_E_EXPLICIT_GOAL_ENTRY_ROUTE_DELEGATES_TO_CORE_COORDINATION` | SELECTED AS TRANSPORT CHOICE, NOT OWNER | A dedicated typed transport can preserve Model D, but route/API choice is not itself ownership and no route is implemented by M113A. |
| `MODEL_F_CHAT_MAY_PROPOSE_BUT_NOT_ACCEPT_A_GOAL` | NOT CURRENTLY JUSTIFIED | This may be a future chat relationship, but current `/chat` lacks an interpretation, authority, provenance, and proposal contract. It cannot be implemented or assumed now. |
| `MODEL_G_NO_GOAL_INTAKE_BUILD_CURRENTLY_JUSTIFIED` | NOT SELECTED AS OWNER; BUILD RESULT | The canonical owner is proven process-locally, but the live entry contract is incomplete, so no Build is justified. |
| `MODEL_H_EVIDENCE_INSUFFICIENT` | REJECTED | Source, caller, architecture, and test evidence is sufficient for a bounded ownership decision and a negative Build decision. |

Selected principal ownership model:

```text
MODEL_D_CORE_COORDINATION_OWNS_INTERFACE_AGNOSTIC_GOAL_INTAKE
```

Selected transport model:

```text
MODEL_E_EXPLICIT_GOAL_ENTRY_ROUTE_DELEGATES_TO_CORE_COORDINATION
```

The transport model is subordinate to the ownership model. It does not authorize
a route, API, or `/chat` change.

## 16. Selected Ownership Contract

Core Coordination, through GoalIntake, must own the canonical interface-agnostic
Goal-intake contract. The ownership split is:

```text
Interface transport
-> explicit typed intake request
-> GoalIntake/Core Coordination validation
-> proposed Goal identity
-> separate Human Authority acceptance
-> Core Coordination Task creation
-> Core Coordination TaskContext creation and selection
-> future same-process Thinking boundary
```

The interface does not own the Goal. AetherRuntime may hold the process-local
CoreCoordination instance but does not own Goal semantics. Working Memory may
reference state but does not own it. Thinking may interpret or propose content
under a future contract but does not accept the Goal. Governance authorizes
applicable operations and Action remains separate.

## 17. Failure-Closed Requirements

A future canonical Goal-intake boundary must reject before canonical state changes
when:

- the operation type is absent, ambiguous, or unsupported;
- a conversation, question, information request, or status inquiry is presented
  without explicit Goal operation semantics;
- proposed outcome or required constraints are missing or ambiguous;
- the source interface or source message identity is unavailable when required;
- Human Authority is absent, malformed, expired, out of scope, or not bound to
  the exact proposed Goal;
- an Action approval is supplied as Goal authority;
- the proposed Goal ID or revision is unknown, stale, terminal, or owned by a
  different coordinator;
- a correction does not identify the exact Goal revision;
- a continuation, pause, or cancellation lacks an existing owner-owned Goal or
  Task reference and valid authority;
- Task creation is attempted without an accepted Goal;
- TaskContext creation or selection fails, is stale, terminal, or unowned;
- provenance is incomplete or conflicts across source categories;
- an interpretation result is not explicit enough to distinguish Goal intake
  from conversation; or
- any downstream Thinking or Plan contract would require fabricated identity,
  criteria, provenance, or authority.

No fallback may promote raw text, Working Memory, session metadata, approval
records, or Action records into a canonical Goal after a failure.

## 18. Provenance and Lifecycle Readiness

Required future provenance categories include:

- raw source text or structured requested outcome;
- source interface and source message/request identity;
- human actor or authority source;
- exact proposed Goal identity and revision;
- acceptance identity and acceptance time;
- event, observation, recording, and decision time where applicable;
- interpretation source and uncertainty;
- correction/reference/continuation source; and
- downstream Core Coordination handoff identity.

Current live entry provenance is partial/noncanonical. `session_id` and broad
metadata are not a provenance envelope. `Goal` stores no complete live source
envelope. The process-local Core Coordination seam preserves identity and
revision after entry, but no live entry supplies those values.

Current lifecycle readiness is also incomplete. Goal has proposed/accepted and
some terminal statuses, but no live Goal lifecycle transport exists for active,
pause, cancellation, correction, continuation, expiry, or status inquiry. Task
and TaskContext lifecycle methods are process-local. Restart restoration,
durable canonical context, and background continuation are absent by design.

## 19. API, Persistence, and Compatibility Impact

Current M113A impact:

```text
production behavior: NONE
API impact: NONE
route impact: NONE
persistence impact: NONE
schema impact: NONE
runtime/private-data impact: NONE
existing compatibility impact: NONE
```

No Goal API is selected or implemented. No `/chat` route changes. No Working
Memory behavior changes. No persistence, restart restoration, worker, scheduler,
queue, event, Commitment, or background behavior is selected.

## 20. Build-Readiness Gate

| Required condition | M113A result |
|---|---|
| One canonical ownership model | PROVEN: Core Coordination/GoalIntake process-locally |
| Exact transport relationship | PREFERRED: explicit typed transport delegating to Core Coordination; not implemented |
| Exact Human Authority source | NOT PROVEN for a live entry |
| Proposal and acceptance semantics | Architecture selected; live contract incomplete |
| Goal identity and revision semantics | Process-local semantics proven; live entry handoff absent |
| Provenance requirements | Required categories identified; current live envelope absent |
| Task creation/binding ownership | Core Coordination proven process-locally |
| TaskContext creation/selection ownership | Core Coordination proven process-locally |
| Failure-closed behavior | Process-local checks proven; live entry boundary incomplete |
| No competing authority | Target preserved; `/chat` and Working Memory remain non-authoritative |
| No Action-authority escalation | Preserved |
| No ThinkingProposal producer dependency | Preserved; producer remains absent |
| No persistence dependency | Preserved |
| No Generic Act dependency | Preserved |
| Exact minimal production write set | NOT SELECTED because contract is incomplete |
| Focused future tests | Requirements identified; no Build authorized |
| Compatibility impact | Current behavior unchanged; future compatibility policy unresolved |
| Removal/rollback boundary | No Build selected |

The Build gate therefore resolves:

```text
Future Build: NOT JUSTIFIED
```

This is not a rejection of Model D ownership. It means the owner is proven, but
the live authority-bearing entry contract is not sufficiently complete for a
truthful bounded implementation review.

## 21. Ownership-Maturity Classification

The M113A ownership-intake maturity levels are:

```text
GI0_NO_CANONICAL_GOAL_INTAKE_OWNER
No canonical owner is identified, or multiple competing owners claim Goal intake.

GI1_LEGACY_OR_NONAUTHORITATIVE_INPUT_ONLY
Live input exists, but it is raw text, Working Memory, legacy policy, or another
non-authoritative contract with no canonical Goal owner handoff.

GI2_CANONICAL_OWNER_PROVEN_ENTRY_CONTRACT_INCOMPLETE
One canonical owner is proven process-locally, but no live entry provides the
complete typed operation, Human Authority, provenance, lifecycle, and fail-closed
handoff contract.

GI3_BOUNDED_CANONICAL_GOAL_INTAKE_CONTRACT_PROVEN
One owner, transport relationship, authority source, proposal/acceptance,
provenance, lifecycle, failure, and compatibility contract is complete and
proven for a bounded live entry, without implementation being implied.

GI4_DURABLE_CANONICAL_GOAL_INTAKE
GI3 is proven and the canonical Goal-intake identity, authority, lifecycle,
provenance, and restoration behavior survive the required process/lifecycle
boundary with a durable consumer.
```

Selected classification:

```text
GI2_CANONICAL_OWNER_PROVEN_ENTRY_CONTRACT_INCOMPLETE
```

GI0 is rejected because Core Coordination/GoalIntake is a proven canonical
process-local owner. GI1 describes current live `/chat` and Working Memory input
but not the overall ownership maturity. GI3 is not proven because the live
transport, typed Human Authority, interpretation, provenance, and lifecycle
contract are incomplete. GI4 is not proven because canonical context is
process-local and not durable across restart.

## 22. Core-Drift Gate

The selected positive ownership model preserves all required invariants:

```text
1. Aether remains one persistent mind: YES
2. Goal remains above procedure: YES
3. Context remains Core Coordination responsibility: YES
4. Human Authority remains required for Goal acceptance: YES
5. Conversation and Goal creation remain distinct: YES
6. Goal proposal and Goal acceptance remain truthfully distinct: YES
7. /chat is prevented from becoming a competing authority: YES
8. Working Memory is prevented from becoming Goal authority: YES
9. AetherRuntime is prevented from becoming cognitive authority: YES
10. AetherOS remains mechanism/environment: YES
11. Action approval and Goal authority remain separate: YES
12. ThinkingProposal and Goal intake remain separate: YES
13. Plan materialization remains separate from Action authorization: YES
14. Observe and Verify remain required for outcome completion: YES
15. Commitment runtime, persistence, scheduler, capability discovery, delegation, and Generic Act remain out of scope: YES
```

## 23. What M113A Proved

M113A proved:

- Core Coordination/GoalIntake is the only canonical process-local Goal-intake
  owner supported by current architecture and source evidence.
- Interfaces must remain transports, not canonical Goal owners.
- A future dedicated explicit Goal-entry transport is preferable to silently
  promoting `/chat` or Working Memory.
- Goal proposal and Goal acceptance must remain separate by default.
- Human Authority must be represented by a future typed, exact, scope-bound
  authority contract rather than a raw Action approval or arbitrary string.
- Core Coordination must create/bind Task and TaskContext and explicitly select
  context; it must own revisions and lifecycle state.
- Thinking may eventually propose interpretation or ThinkingProposal content,
  but it does not accept Goals or authorize Action.
- AetherRuntime may transport to Core Coordination without becoming cognitive
  authority.
- Working Memory, Action approvals, capability records, session IDs, and
  metadata are not canonical Goal authority.
- The overall maturity is `GI2_CANONICAL_OWNER_PROVEN_ENTRY_CONTRACT_INCOMPLETE`.
- No small future Build is currently justified.

## 24. What M113A Did Not Prove

M113A did not prove:

- a live canonical Goal-intake runtime entry;
- a production caller of `CoreCoordination.create_goal`, `accept_goal`,
  `create_task`, or `select_context`;
- a typed Human Authority envelope;
- a complete requested-outcome interpretation contract;
- a natural-language input classifier;
- safe automatic proposal-and-acceptance from ordinary chat text;
- `/chat` as a canonical Goal transport;
- Working Memory as Goal authority;
- AetherRuntime or AetherOS as cognitive authority;
- Goal lifecycle transport for pause, cancellation, continuation, correction,
  or expiry;
- durable or restart-restored Goal/Task/TaskContext state;
- a ThinkingProposal producer;
- Goal-to-Plan runtime execution;
- Action authorization, Generic Act, or capability delegation;
- a future API shape or route implementation; or
- a Future Build authorization.

## 25. Explicit Non-Goals and Authorization State

M113A does not implement or authorize:

- a Goal API or Goal route;
- `/chat` wiring into Core Coordination;
- Working Memory promotion;
- a general natural-language classifier;
- a ThinkingProposal producer, adapter, provider, factory, model, or inference;
- Goal-to-Plan execution or PlanStep execution;
- persistence, restart restoration, Commitment runtime, workers, schedulers,
  queues, events, background execution, or delegation;
- capability discovery, Generic Act, or generic Action authority;
- Action approval reuse as Goal authority;
- changes to `PROGRESS.md`, README, Constitution, Architecture, production code,
  existing tests, dependencies, routes, APIs, or runtime/private data;
- M113B, M114, or any successor milestone;
- commit, tag, push, or PM acceptance claims.

```text
Production implementation: NOT CLAIMED
Future Build: NOT JUSTIFIED
Generic Act: NOT_IMPLEMENTED / NOT_AUTHORIZED / NOT_GRANTED
Patch security: PAUSED
M113B: NOT AUTHORIZED
M114: NOT AUTHORIZED
commit: NONE
tag: NONE
push: NONE
```

## 26. Principal Decision and Next Frontier

Selected ownership model:

```text
MODEL_D_CORE_COORDINATION_OWNS_INTERFACE_AGNOSTIC_GOAL_INTAKE
```

Selected transport choice:

```text
MODEL_E_EXPLICIT_GOAL_ENTRY_ROUTE_DELEGATES_TO_CORE_COORDINATION
```

Selected maturity:

```text
GI2_CANONICAL_OWNER_PROVEN_ENTRY_CONTRACT_INCOMPLETE
```

Principal decision:

```text
D_CORE_COORDINATION_OWNS_GOAL_INTAKE_BUT_LIVE_ENTRY_CONTRACT_INCOMPLETE
```

Future Build:

```text
NOT JUSTIFIED
```

Next frontier:

```text
TYPED_HUMAN_AUTHORITY_AND_EXPLICIT_GOAL_OPERATION_CONTRACT
```

Next milestone type:

```text
AUTHORITY / GOAL-INTAKE CONTRACT PROOF
```

The next proof must decide the typed Human Authority envelope, explicit Goal
operation vocabulary, interpretation ownership, proposal/acceptance transport,
Goal lifecycle transitions, provenance envelope, and compatibility boundary. It
must remain proof-only until a later PM decision establishes a sufficiently small
Build.

```text
Next authorized action: HUMAN/PROJECT-MANAGER M113A GOAL-INTAKE OWNERSHIP REVIEW
```

Control returns to the human/project manager. No M113B, M114, or successor
milestone may begin from this record.
