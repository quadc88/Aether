# Milestone 96 Authoritative Goal-to-Plan Cognitive Foundation Parent Contract

Classification: PARENT CONTRACT AUTHORITY RECORD

Status: AUTHORITY CONTENT ESTABLISHED; GIT DURABILITY AND PUBLICATION ARE DETERMINED DIRECTLY BY GIT; PM ACCEPTANCE IS EXTERNAL TO THIS RECORD

This record is the first explicit authoritative Milestone 96 parent contract.
It is a documentation and static-contract authority lock only. It does not
implement runtime behavior, API behavior, persistence, or execution.

## 1. Historical Fact

A standalone authoritative Milestone 96 parent contract was NOT previously
proven.

The historical M96A direction is evidence informing this contract. M96A is not
retroactively relabeled as a previously authoritative parent contract.

This record establishes the first explicit authoritative Milestone 96 parent
contract using:

- current Architecture v0.3.0;
- durable M96A boundary evidence;
- durable M96B runtime evidence;
- current human/project-manager authority.

## 2. Newly Approved Parent Authority

Canonical parent name:

**Milestone 96 — Authoritative Goal-to-Plan Cognitive Foundation**

Parent objective:

Establish the minimum authoritative, process-local cognitive execution
foundation that carries an explicitly Human-Authority-accepted Goal into a
Core-Coordination-owned Task and authoritative TaskContext, then into a
canonical Plan and canonical PlanStep produced from Thinking under the
selected authoritative context and evaluated by Core Governance, while
stopping before any generic Act.

The parent preserves:

- Thinking proposes.
- Governance authorizes.
- Verification supplies evidence.
- Action executes only within authorization.
- M96 MUST STOP BEFORE GENERIC ACT.

Canonical M96 path:

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

This is not the complete Aether Execution Loop. The global canonical loop
remains:

```text
Receive Goal -> Understand -> Think -> Plan -> Act -> Observe -> Verify
-> Critic -> Repair -> Learn -> Report
```

## 3. Parent Completion Matrix

### Obligation 1 - Human-authority Goal admission

Required: explicit human authority/provenance, Goal identity distinct from
Task, and fail-closed invalid acceptance transitions.

Current contribution: M96B.

Status: **SATISFIED**.

### Obligation 2 - Authoritative Task ownership

Required: Core Coordination owns Task lifecycle, Task identity is distinct from
Goal, an accepted or active Goal is required before Task creation, and invalid
transitions fail closed.

Current contribution: M96A + M96B.

Status: **SATISFIED**.

### Obligation 3 - Authoritative TaskContext

Required: one authoritative TaskContext per active Task, one selected current
TaskContext per reasoning turn, explicit selection and switching, no silent
merge, immutable revisions/snapshots, and fail-closed unknown or terminal
selection.

Current contribution: M96A + M96B.

Status: **SATISFIED**.

### Obligation 4 - Canonical Plan runtime

Required eventually: canonical Plan identity referencing Goal, Task, and
authoritative TaskContext; lifecycle state; completion, failure, and blocked
criteria.

Current state: **NOT YET SATISFIED**. M96B references Plan identity direction
only and does not contain canonical Plan runtime.

### Obligation 5 - Canonical PlanStep runtime

Required eventually: canonical PlanStep identity, one canonical Plan parent,
ordered or explicit step identity, completion/failure/blocked criteria, and no
hidden step merging.

Current state: **NOT YET SATISFIED**.

### Obligation 6 - Think -> Plan authoritative consumer seam

Required eventually: one narrow proven runtime consumer using the selected
authoritative TaskContext, accepting a Thinking proposal, creating or updating
the canonical Plan under that Task, preserving Thinking as proposal authority,
and not granting execution authorization.

Current state: **NOT YET SATISFIED**. This is the first currently proven
unclosed cognitive seam.

### Obligation 7 - Governance before generic Act

Required eventually: canonical Plan/PlanStep reaches Core Governance;
Governance remains authorization owner; Thinking, Plan readiness, Task
readiness, and Goal acceptance do not authorize generic Act.

Current state: **NOT YET SATISFIED** as runtime completion. The STOP BEFORE
GENERIC ACT boundary is defined by M96A and remains locked.

### Obligation 8 - Architecture integrity

Required throughout: one persistent Aether intelligence, nine cognitive organs,
Core Coordination continuity/context ownership, Core Governance authorization,
one ASC framework, one authoritative TaskContext per active Task, one selected
TaskContext per reasoning turn, no silent merge, Time as context not authority,
Resource Observation as fact reporting, and Resource Governance as decision
authority.

Current state: **SATISFIED / MUST REMAIN LOCKED**.

## 4. Explicit Parent Non-Goals

The following are NOT REQUIRED FOR M96 PARENT CLOSURE:

- persistent Goal, Task, TaskContext, or Plan storage;
- restart or cross-session restoration;
- HTTP/API exposure;
- generic POST /chat integration or full /chat replacement;
- generic Act or a second governed capability;
- restricted-read retrofit or Persistent Observation Record integration;
- Observation Intake or Verification Aggregation;
- Critic, Repair, Learning, or automatic retry;
- scheduler, background execution, or wake behavior;
- multi-goal arbitration, goal switching policy, or full goal-completion
  propagation into Report/Learn.

These may become future milestones. They are not automatically M96 obligations.

M96 explicitly permits a process-local foundation. Persistence is not a
prerequisite for M96 closure and requires a separately proven downstream need
and lifecycle contract. No JSON, database, or private store is authorized by
this record.

## 5. Durable Contributions

### M96A - DESIGN / OWNERSHIP BOUNDARY

M96A established Goal Intake/Human Authority ownership of Goal, Core
Coordination ownership of Task and TaskContext, ASC cardinality and selection,
canonical Plan/PlanStep ownership direction, completion/failure/blocked
criteria requirements, Thinking proposes, Governance authorizes, and STOP
BEFORE GENERIC ACT.

M96A did not implement runtime Plan or PlanStep.

Durable identity:

- commit: `c86fcf05c12ae19bdf957b100ea2969905509e3a`
- tag: `milestone-96A-authoritative-goal-task-plan-boundary`

### M96B - GOAL-FIRST PROCESS-LOCAL RUNTIME FOUNDATION

M96B established explicit Goal acceptance; distinct Goal, Task, and
TaskContext identities; accepted Goal -> atomic Task -> initial authoritative
TaskContext; a process-local Core Coordination registry; dependency-injected
clock; immutable snapshots/revisions; explicit selection and switching; and no
silent merge.

M96B does not implement Plan, PlanStep, Think -> Plan, Governance Plan
evaluation, generic Act, API, persistence, or loop integration.

Durable identity:

- commit: `32f9a36b7d847afb3960a6efd87c60978a656163`
- tag: `milestone-96B-goal-first-in-memory-foundation`

## 6. Remaining Parent Work

After this authority record becomes durable, the known remaining M96
substantive work is limited to:

1. canonical Plan / PlanStep process-local foundation;
2. one proven authoritative Think -> Plan consumer seam;
3. Core Governance evaluation boundary before generic Act.

This record does not define implementation details for items 2 or 3 and does
not authorize them.

## 7. Architecture and Safety Locks

- Aether remains one persistent digital intelligence.
- AetherOS remains runtime/world/body.
- Core Governance owns authorization and constitutional safety enforcement.
- Core Coordination owns task/context continuity and coordination semantics.
- ASC remains one Authoritative Shared Cognitive Context framework.
- Context remains distinct from Working Memory, Timeline, Trace, and long-term
  Memory.
- Time provides context, not authority.
- Resource Observation reports facts; Resource Governance decides.
- No second Identity organ is created.
- No silent context merge is permitted.
- Generic Act remains unauthorized.
- No API, persistence, /chat wiring, loop wiring, Observation Intake,
  Aggregation, Critic, Repair, Learning, background execution, or scheduler is
  introduced by this record.

## 8. Lifecycle and Non-Authorization

M95: CLOSED / GIT-DURABLE / PM-ACCEPTED.

M96A: FINALIZED / GIT-DURABLE / PM-ACCEPTED.

M96B: FINALIZED / GIT-DURABLE / PM-ACCEPTED.

M96 parent contract authority content: ESTABLISHED.

Git determines whether this record is committed, tagged, and published.

PM durable acceptance is a separate external review decision.

M96: OPEN.

M96C: NOT AUTHORIZED.

This record does not authorize Git finalization, a parent tag, a push, M96C,
or any other milestone.
