# Milestone 86 Architecture Evolution Decision

## 1. Status and Scope

This record is the decision record for Milestone 86: Architecture Evolution — Governance, Coordination, and AetherOS Infrastructure.

Status: complete locally as a documentation-only architecture-contract Build. Not finalized; not committed; not tagged; not pushed. Milestone 86 is not closed. Milestone 87 is not started.

Scope: this revision defines how governance, coordination, cognitive context, time reasoning, resource observation, and optional economic capability are described in the architecture. It introduces no runtime capability, no queue, no store, no persistence directory, no schema, no router, no endpoint, no API model, no service, no scheduler, and no agent.

## 2. Purpose

This record exists to:

- Record the accepted corrected Milestone 86 Plan direction for the architecture evolution.
- Replace the rejected initial Milestone 86 plan proposal with the corrected architecture model.
- Define the authoritative shared cognitive context framework and its ownership contract.
- Define Core Governance and Core Coordination as internal cross-cutting layers of one persistent mind.
- Define the time reasoning boundary, controlled background continuity, and resource observation boundary.
- Record the exact architecture invariants and the regression locks separately.
- Provide the authoritative-until-revised successor artifact for the Milestone 85 record chain.

## 3. Authoritative Existing Baseline

The following were verified before this Build:

- HEAD == origin/main == ebb4daabda1bfedf81fb69007424335efcad5716.
- Working tree clean; git diff --check clean.
- Tag milestone-85A-observe-verify-lifecycle-boundary-record at b5bad5407a9e23c93b4cac61d914f1faa1267591.
- Milestone 85 closed; Milestone 86 not started.
- ARCHITECTURE.md version 0.2.0; CONSTITUTION.md version 0.2.0.
- Focused baseline 209 passed; full suite 2106 passed.
- OpenAPI 304 paths / 108 schemas; api_server 8 @app routes / 23 include_router / zero direct /action/*.
- Real-root/docs-history drift 0 (fingerprint 600fd549588be7f536f704bc999be1987dcdf550225f2dc11dbf2fbf63ec2bcd).
- Tracked private/runtime empty; docs/history clean.
- Both future file paths absent before this Build.

## 4. Authorization and Rejected Plan

The initial Milestone 86 plan proposal (milestone_86_plan.txt) was rejected by the project manager. It is preserved as historical evidence only and is superseded.

The corrected Milestone 86 Plan (milestone_86_plan_corrected.txt) was accepted and is authoritative for this Build, together with the binding project-manager amendments stated in the 86A Build authorization. Where the amendments conflict with the corrected Plan wording, the amendments govern.

## 5. Corrected Architecture Model

Aether is one persistent mind. The corrected architecture model contains:

- Domain A — Identity and Constitutional Foundation: the foundational anchor. Not a second Identity organ; Aether has one persistent identity.
- Domain B — Core Governance: an internal cross-cutting layer, never a separate agent. Owns Constitution Runtime Enforcement, Governance Policy, Cognitive Signal Arbitration, Resource Governance, permissions, privacy, safety, mandatory verification, and approval boundaries.
- Domain C — Core Coordination: an internal cross-cutting layer, never a separate agent. Owns the Authoritative Shared Cognitive Context framework, Execution Loop coordination, Controlled Background Continuity, and dependency/waiting/pause/resume/handoff state.
- Domain D — Nine Cognitive Organs, unchanged: Identity, Time, Memory, Perception, Thinking, Verification, Action, Learning, Interface. Time retains Temporal Context and Multi-timescale Reasoning. The Identity organ loads and verifies the same continuous identity.
- Domain E — AetherOS Infrastructure: mechanisms and raw facts only. Provides Resource Observation and timing mechanisms without temporal interpretation or governance authority.
- Domain F — Optional Extensions: outside the Core; holds Economic Capability; cannot redefine the Core.

No new agent, no new organ, no second identity, and no runtime change. Constitution impact: NONE.

## 6. Identity Anchor and Identity Organ

Aether has one persistent identity. The Identity and Constitutional Foundation domain is the foundational anchor of the architecture model: the foundational continuity and constitutional reference of the same single Aether identity. It is not a second Identity component, not a second cognitive organ, and not a second authority source. The anchor is a reference, not a duplicate.

The Identity organ, one of the nine cognitive organs, loads, represents, protects, and verifies that same continuous identity across the lifetime of the mind. The Identity organ is not itself described as a separate foundational identity or parallel identity state. There is one identity, one mind, one agent.

## 7. Core Governance

Core Governance is an internal cross-cutting layer of the single mind, never a separate agent. It spans every Execution Loop stage.

Core Coordination is an internal cross-cutting layer of the single mind, never a separate agent. It spans every Execution Loop stage.

Core Governance owns:

- Constitution Runtime Enforcement — applies the existing Constitution at runtime.
- Governance Policy.
- Cognitive Signal Arbitration.
- Resource Governance.
- Permission scope.
- Privacy boundaries.
- Safety prohibitions.
- Mandatory verification requirements.
- Approval boundaries.
- The operative risk classification used for authorization (Verification supplies evidence).

Core Governance is itself bounded by the same hard constraints it enforces. It never becomes an agent; it is a layer of the one mind.

## 8. Cognitive Signal Arbitration — Hard Constraints and Soft Signals

Cognitive Signal Arbitration belongs to Core Governance.

Hard constraints define the allowed decision space. Soft decision signals rank options only inside that allowed space. Hard constraints must never be overridden by optimization.

Hard constraints:

- The Constitution.
- Valid Human Authority boundaries.
- Safety prohibitions.
- Identity integrity.
- Permission scope.
- Privacy.
- Mandatory verification.
- Resource hard limits.
- Minimum reversibility requirements where applicable.
- Explicit execution prohibitions.

Soft decision signals:

- Goal relevance.
- Evidence strength.
- Time sensitivity.
- Resource feasibility.
- Degree of reversibility.
- Expected quality.
- Latency.
- Learning value.
- Operational efficiency.
- Convenience.

No numerical weights and no universal scoring function are defined. Arbitrating signals is not permission granting; arbitration selects among options that are already allowed. Reversibility has a dual role: mandatory reversibility requirements may be hard constraints, while among allowed options, greater reversibility may be a soft preference.

## 9. Thinking and Governance Responsibility Split

Thinking proposes. Governance authorizes. Verification supplies evidence. Action executes only within authorization.

Thinking owns: intent, planning, reasoning, workflow selection, risk framing, resource need proposals, and prompt construction.

Governance owns: whether a proposed path is allowed, permissions, policy profile, operative risk classification, approval boundaries, and resource decisions.

The current deterministic Thinking Policy and the current Safety Stack remain unchanged by this milestone. This section is documentation only; no runtime refactor is performed.

## 10. Authoritative Shared Cognitive Context

The Authoritative Shared Cognitive Context (ASC) is an architecture framework, not one global mutable task object. The ASC framework is owned by Core Coordination.

- One ASC architecture framework exists.
- Every active task has exactly one authoritative task context.
- One reasoning turn has exactly one current task context.
- Waiting, paused, or background tasks may retain separate task contexts.
- No silent merging or overwriting of task contexts occurs.
- Switching the current task context is an explicit Core Coordination operation, subject to Core Governance constraints.

Locked invariants:

- One framework, one authoritative context per active task.
- One reasoning turn, one current task context.
- No silent cross-task context merging.

The phrase "Aether has exactly one ASC" must be read as one architecture framework, not a single global mutable object.

The ASC carries four categories of content:

- Goal and Task Context: current goal, active task, execution phase, completion criteria.
- Authority and Governance Context: permission scope, policy profile, risk classification, resource budget, temporal scope, approval state.
- Operational Context: execution-phase state and working-memory references relevant to the task.
- Cognitive References: references to memory, observation, and verification content relevant to the task.

ASC non-goals: the ASC is not a database, not a memory tier, not a scheduler, not a queue, not a new cognitive organ, and not an authorization source.

## 11. Shared Context Ownership Map

Every authoritative category has exactly one owner. Read access does not imply write authority. A contributor may propose an update without becoming the owner.

- Current Goal: Human Authority / Goal Intake.
- Active Task: Core Coordination.
- Execution Phase: Core Coordination.
- Permission Scope: Human Authority and Core Governance.
- Policy Profile: Core Governance.
- Risk Classification: Verification supplies evidence; Core Governance owns the operative classification used for authorization.
- Resource Budget: Resource Governance.
- Temporal Scope: Time.
- Completion Criteria: the Plan stage and planning contract define; Verification evaluates; Core Coordination references.
- Working-Memory References: Memory.
- Observation References: the Observation boundary (Milestone 85 record).
- Verification References: Verification.
- Approval State: the Human Authority / Governance approval boundary.

Locks: one owner per category; read access does not imply write authority; a contributor may propose without owning. No new Planning cognitive organ is introduced; "Plan" refers to the canonical loop planning stage.

## 12. State and Memory Separation

- Authoritative Shared Cognitive Context: current authoritative task state.
- Working Memory: temporary reasoning and task content.
- Timeline / Loop Trace: historical record of events and stage progression.
- Long-term Memory: persisted episodic, semantic, and procedural knowledge.

Lock: context is not memory. Current state and historical trace are separate. Historical information may inform current state but may not silently overwrite it. Memory may supply context but may not independently redefine current Goal, permission, authority, or execution phase.

## 13. Temporal Context — Four Time Semantics and Five Scopes

Temporal Context and Multi-timescale Reasoning belong to the Time cognitive organ. AetherOS Infrastructure supplies only timing mechanisms and raw clock facts. Temporal reasoning is cognition, not infrastructure.

Four time semantics:

- Event Time: when the external or internal event actually occurred.
- Observation Time: when Aether or another observer perceived or obtained the event.
- Recording Time: when the information entered an Aether record, memory, timeline, or store.
- Decision Time: when Aether formed or authorized a conclusion based on the information.

The four semantics differ because observation latency, batching or delayed persistence, re-observation, delayed evaluation, and re-authorization after new evidence can separate them. Distinguishing them matters for causality (ordering by event time can differ from ordering by recording time; causality must not be inferred from recording order alone), evidence freshness (a fact may be old at decision time even when freshly recorded), auditability (records must distinguish the four timestamps so review can reconstruct what was known when), Verification (outdated-information detection depends on separating event time from decision time), Planning (deadlines and schedules use event and decision time, not recording time), Memory integrity (recency, expiry, and review scheduling rely on the four semantics), and Learning (whether a lesson still applies depends on when it was learned versus when conditions changed).

Five temporal reasoning scopes:

- Immediate Context: the current moment, response, or action.
- Execution Context: the duration of the current task or plan.
- Personal Timeline: the temporally ordered history relevant to Aether's identity continuity and its relationship with the human authority or current person context.
- Domain/Social Context: the external domain and social environment.
- Long-term Context: identity continuity, memory aging, and growth.

Locks: these are reasoning scopes, not mandatory separate storage systems. Multi-timescale reasoning must not create a separate temporal agent; it is a property of the single mind. Time provides context, not authority. Historical patterns and long-term habits must not override explicit current human instructions. A past authorization must not be treated as permanent authorization.

## 14. Controlled Background Continuity

Controlled Background Continuity is the continued progress of an authorized goal across turns, under binding constraints.

Ownership split:

- Core Coordination owns continuation state and task continuity.
- Core Governance owns continuing authorization and constraints.
- Time / AetherOS provide wake, expiry, scheduling, and timer mechanisms.

Every background continuation must remain bound to: the originating goal; the exact task; the authoritative task-context identifier; the Human Authority scope; the permission scope; the policy profile; the risk state; the resource budget; the wake condition; the expiry; the cancellation mechanism; the checkpoint; the verification criteria; and the audit trail.

Locks: background continuity continues an authorized goal. It does not create a new goal or new authority. It must not: extend expired authority; retry indefinitely; silently perform external actions; reinterpret old permissions as permanent; change completion criteria without authorization; or silently merge context into another task.

No scheduler and no background runtime is implemented by Milestone 86.

## 15. Resource Observation and Resource Governance

Resource Observation remains part of AetherOS Infrastructure.

Resource Observation is explicitly distinct from the Execution Loop Observe stage: Resource Observation reports factual, time-bounded conditions about the operating environment; the Observe stage (Milestone 83/84/85 boundary) verifies observable evidence of intended effects.

Resource Observation may report factual, time-bounded conditions such as: CPU/GPU/NPU/RAM/storage state; model load and availability; provider availability; quota and rate limits; tool health; network state; latency; active workload; data locality; privacy zone; background-task consumption.

Resource Observation does not authorize, allocate, select, terminate, or expand resources.

Lock: resource facts must be time-bounded. Resource Observation reports; Resource Governance decides.

## 16. Optional Economic Capability

Economic Reasoning is an optional analysis capability: cost comparison, budgeting, financial research, business planning, and economic simulation.

Economic Agency is an optional execution capability: purchasing, payment, transfer, investment execution, financial commitments, and contractual financial actions.

Milestone 86 defines only: optional status; the Governance dependency; the Human Authority requirement; the verification and audit requirement; amount and scope boundaries; and reversibility and irreversibility analysis.

Milestone 86 must not define: wallets, tokens, autonomous earning, autonomous trading, payment infrastructure, or market agents.

Locks: optional extensions cannot redefine the Core. Economic Agency requires a separate future authorized architecture and safety milestone.

## 17. Architecture Invariant Set and Regression Locks

### 17.1 Architecture invariants (23)

1. One Persistent Identity — Aether is a single persistent digital intelligence with one continuous identity; no second mind or agent.
2. Nine Cognitive Organs Remain — Identity, Time, Memory, Perception, Thinking, Verification, Action, Learning, Interface; no organ is split, merged, or removed; Learning remains a scaffold.
3. Governance Is Cross-Cutting — Core Governance spans every Execution Loop stage.
4. Coordination Is Cross-Cutting — Core Coordination spans every Execution Loop stage.
5. One ASC Architecture Framework — one framework, not one global mutable task object.
6. One Authoritative Context Per Active Task — every active task has exactly one authoritative task context.
7. One Current Task Context Per Reasoning Turn — one reasoning turn, one current task context.
8. No Silent Cross-Task Context Merging — no silent merging or overwriting of task contexts.
9. Context Is Not Memory — the ASC (current authoritative task state) is distinct from Working Memory, Timeline/Loop Trace, and long-term Memory.
10. Every Authoritative Category Has an Owner — one owner per authoritative field category.
11. Read Access Does Not Imply Write Authority — contributors may propose updates without becoming owners.
12. Hard Constraints Before Optimization — hard constraints define the allowed decision space; soft signals rank options only inside it; hard constraints are never overridden by optimization.
13. Time Provides Context, Not Authority — temporal interpretation is the Time organ's responsibility; AetherOS supplies mechanisms only.
14. Resource Observation Reports, Governance Decides — observation never authorizes, allocates, selects, terminates, or expands resources.
15. Resource Facts Are Time-Bounded — resource facts are time-bounded conditions, never permanent truths.
16. Background Continuity Does Not Create Authority — it continues an authorized goal; it never creates a new goal or new authority.
17. Budget Cannot Override Safety — budget, latency, cost, and efficiency may not override Constitution, safety, identity integrity, permission, privacy, or required verification.
18. Current State and Historical Trace Are Separate — history may inform current state but may not silently overwrite it.
19. Optional Extensions Cannot Redefine the Core — Economic Capability and future extensions remain optional and bounded.
20. Thinking Proposes, Governance Authorizes — the Workflow and Policy Layer proposes; Core Governance decides whether the proposed path is allowed; Verification supplies evidence; Action executes only within authorization.
21. Canonical Execution Loop Remains Unchanged — "Receive Goal → Understand → Think → Plan → Act → Observe → Verify → Critic → Repair → Learn → Report".
22. Milestone 85 Observation/Verification Boundary Remains in Force — the Milestone 85 record is incorporated by reference and not altered.
23. Milestone 86 Adds No Runtime Capability — no aether/* source changes; Governance, Coordination, and AetherOS Infrastructure are contracts in documentation only.

### 17.2 Regression locks (separate from the invariants)

- OpenAPI: 304 paths / 108 schemas.
- api_server.py: 8 @app routes / 23 include_router / zero direct /action/*.
- Full-suite baseline: 2106 passed (2084 baseline + 22 Milestone 85A design-lock tests).
- Focused baseline: 209 passed.
- Drift: 0 — canonical fingerprint 600fd549588be7f536f704bc999be1987dcdf550225f2dc11dbf2fbf63ec2bcd.
- Tracked private/runtime: empty; docs/history: clean.

Regression metrics are not substitutes for architecture invariants; they are held separately.

## 18. Placement Map

The corrected content is placed as follows:

- P1: ARCHITECTURE.md header version marker changed from 0.2.0 to 0.3.0; Status and Depends-on lines unchanged (Constitution remains v0.2.0).
- P2: ARCHITECTURE.md new subsection 4.9 "Temporal context and multi-timescale reasoning" inserted after subsection 4.8, before section 5 (Memory).
- P3: ARCHITECTURE.md section 7.4 appended with the proposals-not-authorizations clarification and the "Thinking proposes. Governance authorizes." sentence.
- P4: ARCHITECTURE.md section 13 diagram replaced with the cross-cutting diagram; the canonical loop sentences remain unchanged.
- P5: ARCHITECTURE.md new section 18 "Architecture Evolution — Governance, Coordination, and AetherOS Infrastructure" with subsections 18.1-18.14.
- P6: Relationship to Milestone 85 recorded inside ARCHITECTURE.md section 18.13 with the exact supersession clause.
- README: one minimal clarification paragraph appended (section 33 of the corrected Plan).
- CONSTITUTION.md: no change; byte-identical.
- The detailed ownership table lives in this decision record (section 11); ARCHITECTURE.md retains the concise invariants and the four-category list in section 18.6.

## 19. Relationship to Existing Records

This revision is the explicitly authorized architecture evolution for Milestone 86. It incorporates the Milestone 85 Observation Classification / Verification Aggregation / Lifecycle Decision Boundary Record by reference and does not alter it; that record remains fully in force. The governance, coordination, and infrastructure sections added by this revision extend the architecture without reopening the observation/verification boundary.

This record supersedes the rejected initial Milestone 86 plan proposal, which is preserved as historical evidence only. CONSTITUTION.md remains protected and byte-identical; no constitutional article is added.

## 20. Future Capability Gates and Milestone 86 Closure Rule

- No future milestone may introduce a runtime component described here (scheduler, background runtime, economic agency, temporal agent, resource governor, or new cognitive organ) without a separately authorized architecture and safety milestone.
- Producer-proof gate: any future component that could feed the ASC framework or Resource Observation must be justified by an actual, proven consumer.
- Aggregator-proof gate: no aggregation behavior may be added without a proven consumer and a separately authorized plan.
- Critic/Repair-proof gate: no critic or repair triggering may be wired without a separately authorized plan.
- Milestone 86 is not considered closed until 86A Finalization is accepted. The local 86A Build does not close Milestone 86 and does not start Milestone 87. Milestone 87 may not start automatically.
