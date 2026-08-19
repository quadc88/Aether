# Milestone 100A Active Runtime Gap and Consumer Priority Discovery

Classification: STRICT READ-ONLY ARCHITECTURE / RUNTIME DISCOVERY / PRIORITY ANALYSIS

Status: DESIGN CANDIDATE / DISCOVERY COMPLETE LOCALLY / PM PRIORITY REVIEW REQUIRED

This record identifies the highest-value real production runtime gap by
auditing existing producers, consumers, ownership, and authority boundaries.
It does not implement a runtime change, reopen M99A discovery, or authorize a
future Build.

## 1. Current Git State

- Branch: `main`.
- HEAD: `4d4e60edf87441aef51d6b948172e5ca03f77191`.
- `main`, `origin/main`, and remote `main` matched at audit start.
- Tracked worktree: clean.
- M99A: FINALIZED / COMMITTED / TAGGED / PUSHED / PM-ACCEPTED by current project authority.
- M99A producer-proof result: `D_NO_TRUTHFUL_PRODUCTION_THINKINGPROPOSAL_PRODUCER_CURRENTLY_JUSTIFIED`.
- M99A selected model: `MODEL_D_NO_PRODUCTION_THINKINGPROPOSAL_PRODUCER_YET`.
- Full-suite baseline: `3144/3144 passed, 0 failures, 0 errors, 9 warnings`.
- OpenAPI baseline: `306 paths / 112 schemas`.
- api_server baseline: `8 direct @app routes / 23 include_router / 0 direct /action/*`.
- M100A design and static-test candidates did not exist at audit start.

M100A authorizes only this design candidate, its static/document lock, and the
external PM evidence summary. It authorizes no production edit, `PROGRESS.md`
edit, commit, tag, push, or runtime data change.

## 2. Current Authority

The following boundaries remain binding:

- Generic Act: `NOT_IMPLEMENTED`.
- Generic Act integration: `NOT_AUTHORIZED`.
- Generic Act authority: `NOT_GRANTED`.
- M97A found no justified Generic Act consumer.
- M98A found no justified external canonical Goal-to-Plan runtime consumer.
- M99A found no truthful production ThinkingProposal producer currently
  justified.
- Thinking proposes.
- Core Coordination owns canonical identity, context selection, and state
  coordination.
- Core Governance owns authorization and hard constraints.
- Verification supplies evidence.
- Action executes only within an applicable authorization boundary.
- `GOVERNANCE_EVALUATION != EXECUTION_AUTHORIZATION`.

M100A does not reopen any negative result above. It asks a different question:
which already-active runtime path has the strongest real producer/consumer
pressure and the highest safety or correctness value to review next?

## 3. Exact Objective

Identify and rank only real runtime gaps supported by current production
behavior. For each candidate, prove:

1. a production producer;
2. a production consumer;
3. useful current behavior depending on the path;
4. an exact missing, duplicated, unsafe, or ambiguous boundary;
5. current ownership and authority risk;
6. concrete user or system value;
7. bounded future scope.

Tests, documentation, dormant foundations, and architectural desire are not
consumer proof.

## 4. Active Runtime Surface Inventory

| Surface | Current production path and useful behavior | Current finding |
|---|---|---|
| `/chat` | `api_server.py:223-267` -> `AetherRuntime.process_chat` -> `run_core_chat_loop`; produces perception, risk, policy, legacy authorization envelope, approval, timeline, and response data. | Active and coherent safety skeleton, but legacy and not canonical Goal-to-Plan. |
| `AetherRuntime.process_chat` | `aether/core/runtime.py:99-113` forwards text, session metadata, Working Memory, and a forced-false execution flag. | Real consumer of legacy loop; no canonical Goal, Task, or Plan input. |
| Perception | `aether/perception/text.py:59-95` produces normalized text, language, question/command hints, risk terms, warnings, and metadata. | Real producer consumed by risk, policy, and response; no authority gap found. |
| Thinking policy | `aether/thinking/policy.py:11-132` produces a policy dictionary for `respond_only`, clarification, or tool suggestion behavior. | Real producer consumed by the loop and legacy policy gate; M99A confirms it is not a ThinkingProposal producer. |
| Risk verification | `aether/verification/risk.py:201-313` classifies risk and builds verification guidance. | Real evidence producer consumed by policy, approval, and Governance paths; no single active consumer gap found. |
| Working Memory | `aether/core/runtime.py:9-13` owns one process-global store; loop and action services append events. | Real producer/consumer path, but `session_id` is metadata only and does not partition state. |
| Goal-related routes | Goal route behavior is Working Memory-oriented; Core Coordination goal operations are in `aether/core/task_context.py:339-414`. | Goal/Task/TaskContext foundation is real but no production caller consumes the canonical chain. |
| Core Coordination | Owns selected context, Plan, PlanStep, proposal materialization, and canonical Governance request assembly. | Real process-local owner and consumer, intentionally dormant outside its seam. |
| Core Governance | `/chat` uses the legacy authorization envelope; canonical restricted-read and Plan Governance have separate evaluators. | Multiple live authorization contracts exist across capability paths. |
| Approval request and queue | `/chat` creates individual approval records; legacy tool/patch paths use the approval-item queue. | Two active stores have different consumers and status/binding semantics. |
| Restricted-read resume | `/chat/restricted-read/resume` -> restricted-read coordination -> fresh policy/Governance -> approval claim -> Action bridge -> call-local Observation -> verifier. | Strongest current bounded action path; real consumer exists for call-local Observation. |
| Direct file read | `/action/file/read` -> `file_service.handle_file_read` -> `read_restricted_file` default direct mode. | Equivalent file-read capability follows a separate direct contract and does not use the canonical restricted-read envelope. |
| Tool planner/executor | `/action/tool-executor/execute` -> `tool_execution_service` -> `tool_executor.execute_tool`; sandbox handlers include restricted read, patch apply, and rollback. | Real action surface with local planning/approval/dry-run semantics distinct from Core Governance. |
| Patch apply/rollback | `/action/patch-apply/apply` and `/action/patch-rollback/rollback` call local patch functions; `dry_run=False` can write/restore after local checks. | Real mutation surfaces separate from final-real-apply executor and canonical `/chat` authorization. |
| Final real apply | Final-real-apply approval gate -> executor -> patch apply, with queue item, dry-run, final decision, one-use check, and backup. | Bounded action-specific chain exists; it does not unify other live action entry points. |
| Verification | Restricted-read verifier consumes call-local reader result; post-apply gate consumes action records and human decision. | Verification consumers are real but evidence contracts are not one lifecycle. |
| Observation Intake | `handle_observation_intake` accepts caller-supplied observed/expected values and persists declarative records. | Safe declarative producer; no automatic collector or proven post-action consumer. |
| Timeline and memory writes | Action services and loop write Timeline and Working Memory events. | Useful audit behavior; Timeline has no session or event/observation/decision distinction. |
| Time | `now_iso()` and timezone are captured by loop, action records, and Timeline. | Time facts are produced, but no current consumer requires a broad temporal provenance contract. |
| Identity integrity | Awakening and `/chat` verify identity; Governance rechecks identity for restricted read. | Real safety producer/consumer path; ownership is clear. |
| Background/scheduler | No production scheduler, worker, wake queue, or continuation runtime was found. | Absence is deliberate and has no current producer/consumer pressure. |

## 5. Producer and Consumer Inventory

### 5.1 Legacy Chat and Policy

`aether/core/runtime.py:99-113` is the production caller of
`aether/core/loop.py`. The loop consumes Perception, Risk, tool suggestion,
identity evidence, time, and Working Memory, then calls the Thinking policy,
legacy authorization envelope, approval builder/queue, Timeline, and response
builder. This is a real producer/consumer chain with current user-visible
behavior.

It is not currently a justified canonical consumer. It does not create a
canonical Goal, Task, selected TaskContext, ThinkingProposal, Plan, PlanStep,
or canonical Plan Governance request. M98A and M99A already record that this
absence is not itself a reason to wire `/chat`.

### 5.2 Canonical Coordination

`CoreCoordination` at `aether/core/task_context.py:339-871` is a real
process-local owner. Its materialization and Governance methods are consumed
by focused process-local callers and tests, but no current public runtime path
instantiates or drives the complete chain. This is a dormant foundation, not a
current high-priority runtime gap.

### 5.3 Active Action Producers and Consumers

There are multiple active action producers and consumers:

- The canonical restricted-read coordinator produces a fresh authorization
  decision and an execution scope; its Action bridge consumes that scope and
  returns a call-local Observation to the restricted-read verifier.
- The direct file route produces a direct reader request consumed by
  `read_restricted_file` in default `direct` mode and the file access audit
  helper.
- The tool executor produces a tool execution record consumed by its caller,
  execution log, Working Memory, Timeline, and optional audits.
- Patch routes produce patch proposal/review/apply/rollback records consumed by
  their local lifecycle functions and action services.
- The final-real-apply executor consumes a final approval gate, approved queue
  item, completed dry-run record, and approved patch proposal before invoking
  the patch apply function.

These are real producers and consumers, not hypothetical architecture arrows.
Their missing boundary is that equivalent action capability does not have one
uniform current authorization and binding contract.

## 6. Highest-Priority Real Gap

### GAP-01: Live Action Authority Consolidation

Recommended status: `HIGH_PRIORITY_REAL_GAP`

**Runtime path:**

```text
canonical restricted-read resume / execute-approved-read
  -> Core Coordination + Core Governance + Action scope

direct file read / tool executor / patch apply / patch rollback
  -> local Action services and capability-specific records
```

**Producer:**

- Canonical path: `aether/core/coordination.py:33-122` produces a fresh
  authorization decision, execution attempt binding, and restricted-read
  scope.
- Direct paths: `file_routes.py:57-60`, `tool_executor_routes.py:21-31`, and
  `patch_routes.py:72-83` produce requests consumed by direct Action services.

**Consumer:**

- Canonical Action bridge `aether/action/services/restricted_file_read_bridge.py:4-34`
  consumes the governed scope and the restricted-read verifier consumes its
  call-local Observation.
- Direct file reader, tool executor, patch apply, and patch rollback consume
  their own route/service inputs and local records.
- Final-real-apply executor consumes its own gate and readiness records at
  `aether/action/final_real_apply_executor.py:92-116,181-201`.

**Current production behavior:**

- `/chat/restricted-read/resume` and `execute-approved-read` perform exact
  request matching, approval binding, identity/risk/policy re-evaluation,
  execution-time Governance, single-use claim, scope-bound dispatch, and
  call-local verification.
- `/action/file/read` calls the same reader with default `direct` mode through
  `file_service.py:86-89`; it records a file audit but does not traverse the
  canonical restricted-read approval/scope path.
- `/action/tool-executor/execute` calls `execute_tool` through a separate
  sandbox/tool-plan path. `_safe_result` dispatches `file.restricted_read`,
  `file.patch_apply`, and `file.patch_rollback` at
  `aether/action/tool_executor.py:199-228`.
- `/action/patch-apply/apply` and `/action/patch-rollback/rollback` invoke
  local functions directly. `patch_apply.py:44-56` validates local proposal and
  optional legacy approval state, then writes when `dry_run` is false;
  `patch_rollback.py:43-52` restores a backup when its local record is
  eligible.
- Final-real-apply is more strongly gated, but it is a separate capability
  chain rather than the common authority boundary for all equivalent routes.

**Exact missing boundary:**

There is no single current, capability-scoped action-binding boundary that
classifies every live equivalent entry point, requires the appropriate fresh
authorization and identity/context binding, and makes the distinction between
the canonical restricted-read path, legacy compatibility paths, and the
final-real-apply path explicit. The result is not that every direct route is
currently unsafe in every configuration. The result is that the same class of
read or mutation can be reached through contracts with materially different
authority, freshness, privacy, approval, and evidence semantics.

Additional evidence is the current configuration:
`config/aether.yaml:23-25` sets `security.restricted_file_read.approved_roots`
to an empty list, and `aether/core/config.py:121-155` fails the governed path
closed when no approved roots exist. The direct reader retains an independent
`ALLOWED_ROOTS` and direct-mode behavior at
`aether/action/restricted_file_reader.py:16-22,224-265`. This is a concrete
configuration/authority divergence, not a target-architecture assumption.

**Owner:** Core Governance owns authorization and hard constraints; Action
services own capability execution; Core Coordination owns canonical context
and execution binding; Interface owns route exposure only.

**Authority risk:** High. A future caller or operator can treat a local
approval, dry-run flag, tool-plan decision, or direct file-access record as
equivalent to the canonical Governance decision when it is not. Direct reads
also use a separate privacy path. Direct patch mutation has a separate local
gate and does not require the final-real-apply executor chain.

**Expected value:** One understandable authority boundary for current actions,
consistent privacy and freshness semantics, less approval confusion, clearer
audit records, and reduced risk of accidental authority broadening. It would
also make future observation and repair decisions more trustworthy without
inventing a Generic Act.

**Consumer-proof strength:** STRONG. Multiple live routes and services
produce and consume real action requests and results. The canonical restricted
read has a proven current consumer; the direct routes have proven live service
consumers; the conflict is in the boundary between them.

## 7. Observation and Verification Audit

M95's call-local Observation boundary remains factually valid.

- `RestrictedReadObservation` is produced from the governed reader result by
  `restricted_file_read_observation.py:20-30`.
- `dispatch_restricted_read` returns it at
  `restricted_file_read_bridge.py:27-34`.
- `CoreCoordination.execute_approved_restricted_read` immediately passes it to
  `verify_restricted_file_read` at `core/coordination.py:99-104` and removes it
  from the outward response.
- This is a real current producer/consumer pair.

No new evidence supports durable Observation as a general runtime consumer:

- `observation_record.py:8-18` is explicitly a declarative builder and does
  not observe, collect, execute, or persist.
- `observation_intake_service.py:8-24,141-239` accepts caller-supplied
  observed and expected values, compares them, and persists records; it does
  not collect facts from an Action.
- Post-apply verification consumes action records and a human decision rather
  than independently collected Observation evidence.

Finding: Observation lifecycle disconnect is a real medium-priority contract
gap, but no new durable consumer justifies reopening M95 persistence. It is
deferred behind the action authority boundary and a concrete collector/consumer
use case.

## 8. `/chat` Legacy-versus-Canonical Audit

The current `/chat` path is a functioning, deterministic safety skeleton:

```text
text -> perception -> identity -> time -> Working Memory -> risk
  -> tool suggestion -> Thinking policy -> legacy policy gate
  -> approval request/queue -> Timeline -> response
```

It has a real consumer: the API response and current operators consume its
policy, approval, timeline, and response results. Its safe behavior includes
forced-false tool execution and no Action dispatch.

The current problem is not that `/chat` lacks the canonical Goal-to-Plan path.
M98A/M99A already found no justified external consumer or ThinkingProposal
producer. The relevant M100A tension is narrower: `/chat` and direct Action
routes expose legacy policy/approval semantics while canonical restricted-read
uses a separate Governance path. This is part of GAP-01, not authorization to
wire `/chat` to Core Coordination.

No independent `/chat` priority gap was selected because the legacy path is
currently coherent and the authority divergence is better addressed at the
active Action entry-point boundary.

## 9. Memory and Time Audit

### Working Memory and Timeline

The runtime creates one process-global `WorkingMemory` at
`aether/core/runtime.py:9-13`. `/chat` passes `session_id` as event metadata,
but `WorkingMemory` stores one deque, one current goal, one milestone, and one
notes list at `aether/memory/working/store.py:6-70`. Timeline records at
`aether/memory/timeline/recorder.py:31-60` have time, type, title, description,
importance, and related files, but no session identifier.

This is a real medium-priority privacy/context gap if the public runtime is
used concurrently: session identifiers do not isolate Working Memory or
Timeline. It is bounded and user-visible, but it is not higher priority than
the active action-authority divergence because the current runtime was designed
as one short-lived local process store and the canonical Goal/Task path is not
active.

### Episodic, Semantic, and Procedural Memory

Current runtime writes Timeline and Working Memory events. The repository has
memory storage forms and action-specific records, but M100A found no current
production consumer requiring a broad episodic, semantic, or procedural memory
redesign. Existing memory writes support audit and short-term continuity; they
do not prove a missing consumer contract by architecture alone.

### Time semantics

`now_iso()` and timezone facts are produced by loop, action records, Timeline,
and identity paths. Current consumers use timestamps for ordering, record
identity, and audit. No current production consumer requires distinct event,
observation, recording, and decision time semantics before a bounded action
authority boundary exists. This is a low-priority context gap, not the selected
candidate.

## 10. Governance, Approval, and Action Audit

### Canonical restricted-read path

`core/coordination.py:53-98` validates the approval binding, re-evaluates risk,
identity, and policy, calls `authorize_restricted_read_execution`, claims the
approval for one execution attempt, dispatches a bound scope, and verifies the
result. This is the clearest current Governance-to-Action chain.

### Approval authority split

`approval_queue.py:212-217` explicitly maintains two stores:

- legacy `approval_queue.json` items created by `create_approval_item`;
- individual approval records created by `create_approval_record`.

Tool planner and patch functions consume legacy approval items, while
restricted-read validation consumes individual approval records. This is a
real medium-priority authority/conformance gap: approval status in one store
does not universally control or describe the other store's consumer.

### Direct mutation paths

Patch apply and rollback have local proposal, review, approval-item, backup,
hash, and dry-run checks. Final-real-apply has a stronger separate chain with a
final approval gate, human queue item, completed dry run, single-use check, and
backup. The issue is not absence of all safety controls. The issue is multiple
live authority contracts and direct route access to equivalent mutations.

### Identity and execution freshness

Identity integrity is checked during awakening and `/chat`; canonical
restricted-read performs fresh identity and policy checks at execution time.
The direct patch and tool paths do not consume the same canonical execution
attempt binding. This strengthens GAP-01 without proving a need for Generic Act.

## 11. Candidate Gap Table

| Gap ID | Runtime path | Producer | Consumer | Current behavior | Exact gap | Evidence | Architecture impact | Authority risk | Implementation size | Expected value | Consumer proof strength | Recommended status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| GAP-01 | Governed restricted read versus direct file/tool/patch routes | Core Coordination/Governance scope plus direct Action route handlers | Restricted-read bridge/verifier plus direct readers, tool executor, patch functions, and final executor | Equivalent live actions use different binding, approval, privacy, freshness, and evidence paths | No one capability-scoped authority boundary covers all active entry points | `core/coordination.py:33-122`; `file_routes.py:48-60`; `tool_executor_routes.py:21-31`; `patch_routes.py:72-83`; `patch_apply.py:44-56` | Reduces competing Action/Governance authorities | High | Medium, if bounded to one capability first | Consistent safety, privacy, approval, and audit semantics | STRONG | HIGH_PRIORITY_REAL_GAP |
| GAP-02 | Legacy approval item queue versus approval record store | Tool planner/patch paths and `/chat` approval builder | Legacy action consumers versus restricted-read execution | Two JSON-backed approval representations coexist with different IDs and consumers | One approval decision is not universally visible, bindable, or consumable across live paths | `approval_queue.py:108-144,212-275`; `approval_decision_gate.py:19-71` | Clarifies Action/Governance ownership | High | Medium | Reliable approval meaning and audit | STRONG | MEDIUM_PRIORITY_REAL_GAP |
| GAP-03 | Restricted-read Observation versus ObservationRecord/Intake | Governed reader produces call-local Observation; callers produce Intake records | Restricted-read verifier versus record store/post-apply workflows | Call-local evidence is consumed immediately; Intake persists caller-supplied comparisons | No current producer-owned evidence lifecycle connects real Action outcome to later consumer | `restricted_file_read_observation.py:20-30`; `coordination.py:99-104`; `observation_intake_service.py:141-239` | Affects Verify/Repair/Learning boundaries | Medium-high | Large and consumer-dependent | Objective post-action evidence | STRONG for call-local; NONE for durable general consumer | MEDIUM_PRIORITY_REAL_GAP |
| GAP-04 | Global Working Memory/Timeline with session-aware `/chat` | Runtime loop and action services | `/chat`, memory routes, operators, audit readers | Session IDs are metadata; state and Timeline are process/global | Concurrent sessions can share context, notes, event counts, and timeline without isolation | `core/runtime.py:9-13`; `memory/working/store.py:6-70`; `timeline/recorder.py:31-60` | Affects Memory/Interface continuity | Medium-high | Medium | Privacy and correct task context | STRONG | MEDIUM_PRIORITY_REAL_GAP |
| GAP-05 | Goal/Task/ThinkingProposal/Plan foundation | Core Coordination methods | Only process-local coordinator callers | Canonical objects work in a bounded seam but no production runtime consumes them | No external consumer exists to justify activation | `core/task_context.py:339-871`; M98A/M99A boundary evidence | Latent architecture split only | Latent, not active | Large | Goal continuity if a real consumer appears | NONE outside seam | NOT_JUSTIFIED |
| GAP-06 | Timestamp and Timeline records | Time clock and record builders | Audit, ordering, and status readers | Timestamps exist but temporal meanings are not separated | No current consumer requires a full temporal provenance contract | `core/loop.py:101-107`; `timeline/recorder.py:40-53` | Context quality, not current authority | Low | Medium | Better freshness/audit later | Weak | LOW_PRIORITY_REAL_GAP |
| GAP-07 | Scheduler/background continuity | None | None | No scheduler, worker, or wake runtime | No active producer/consumer exists | Architecture boundary and runtime inventory | Introducing one would be speculative | High if added without authority | Large | Future continuity only | NONE | NOT_JUSTIFIED |

## 12. Priority Model

Candidates were ranked in this order:

1. real production consumer proof;
2. safety and correctness impact;
3. ownership clarity;
4. reduction of duplicate or competing authority;
5. verification and evidence improvement;
6. user/system value;
7. bounded implementation scope;
8. regression risk.

GAP-01 ranks first because it has multiple live producers and consumers,
directly affects real reads and mutations, and can be bounded to one existing
capability without activating canonical Goal-to-Plan or Generic Act. GAP-02 is
closely related but is a narrower contract split inside the same broader
authority problem. GAP-03 and GAP-04 have real consumers but lower immediate
action-safety impact. GAP-05 and GAP-07 lack the required external consumer
proof. GAP-06 has no current decision or action consumer that requires it.

## 13. Rejected Speculative Gaps

- ThinkingProposal production or a legacy-policy adapter: rejected by M99A;
  no truthful producer and no justified external consumer exists.
- `/chat` wiring to Goal/Task/Plan: rejected by M98A/M99A; architecture desire
  is not a current consumer.
- Generic Act or a generic capability registry: not implemented, authorized,
  or granted; no consumer proof exists.
- Durable Observation persistence or general Observation Aggregation: rejected
  as a current Build direction because no new durable consumer or collector is
  proven; M95 call-local restricted-read evidence remains authoritative for its
  current consumer.
- Broad memory redesign: rejected because current Memory and Timeline have real
  bounded use and no broad redesign consumer is proven.
- Full event/observation/recording/decision time model: deferred because no
  current consumer requires it before action authority is bounded.
- Scheduler, background worker, retry loop, Critic, Repair, or Learning
  runtime: not justified without active production producers and consumers.

## 14. Highest-Value Finding

```text
GAP-01_LIVE_ACTION_AUTHORITY_CONSOLIDATION
```

This is the only candidate selected for PM review. It is not a Generic Act
proposal and does not imply that all Action services must be merged. The
finding is that current equivalent action entry points need an explicit
ownership and authority classification before any successor runtime work can
be safely chosen.

## 15. Selected Next Candidate

Selected direction:

```text
ACTION_AUTHORITY_CONSOLIDATION_GAP
```

Why selected:

- It has the strongest current production producer/consumer evidence.
- It affects actual file-read and mutation paths, not dormant architecture.
- It exposes multiple authority contracts and inconsistent freshness/binding
  semantics.
- It has direct safety, privacy, verification, and audit value.
- It can be bounded to one existing capability before any broader action work.
- It does not require `/chat` wiring, ThinkingProposal production, Goal-to-Plan
  activation, or Generic Act.

Why alternatives are deferred:

- `OBSERVATION_CONSUMER_GAP` has a real call-local consumer but no new durable
  consumer; persistence would be speculative.
- `APPROVAL_AUTHORITY_CONSOLIDATION_GAP` is real but is a sub-boundary of the
  broader live Action authority divergence.
- `WORKING_MEMORY_GOAL_AUTHORITY_GAP` has real session/context value but less
  immediate execution-safety impact and would require a bounded session owner.
- `LEGACY_CHAT_AUTHORITY_DUPLICATION_GAP` is not independently justified; the
  stronger evidence is at active Action entry points, not `/chat` itself.
- `RUNTIME_TIME_PROVENANCE_GAP` has no current blocking consumer.
- canonical Goal-to-Plan and ThinkingProposal producer work remain explicitly
  not justified by M98A/M99A.

## 16. Smallest Possible Future Build Boundary

If PM authorizes a future Build, the smallest defensible scope is one
capability-scoped action authority review and containment, beginning with
`file.restricted_read`:

1. inventory and classify every live entry point for that capability;
2. define one owner for authorization binding and one owner for Action
   dispatch;
3. preserve the existing restricted-read exact command, approval, identity,
   risk, session, freshness, single-use, privacy, and verification checks;
4. explicitly classify or quarantine direct and tool-executor routes rather
   than silently treating them as equivalent;
5. preserve call-local Observation without adding durable persistence;
6. add focused boundary/regression tests and API baseline checks;
7. stop before Generic Act, canonical Goal-to-Plan activation, and unrelated
   patch/rollback unification.

This is a recommendation for a separately authorized future plan, not an M100A
implementation instruction.

## 17. Authority Risks

Any future action-boundary work must avoid:

- making Interface or a legacy service a new cognitive authority;
- treating a local approval item or dry-run flag as Core Governance authority;
- broadening a read-only capability into generic execution;
- converting direct action compatibility paths into Generic Act;
- changing action identity, scope, or single-use semantics silently;
- fabricating Observation provenance or persisting call-local evidence without a
  proven consumer;
- deriving canonical Goal, Task, TaskContext, or ThinkingProposal data from
  action metadata;
- merging unrelated action-specific contracts under one unbounded registry;
- changing `/chat`, API, persistence, or protected-core ownership without a new
  separately authorized milestone.

## 18. Explicit Non-Goals

M100A does not implement or authorize:

- any production code or runtime behavior change;
- a ThinkingProposal producer, adapter, provider, or factory;
- `/chat` wiring or canonical Goal-to-Plan runtime integration;
- Generic Act, generic capability registry, or generic Action dispatch;
- approval-store migration or action execution unification;
- Observation persistence, collection, or Verification Aggregation;
- Plan execution, Critic, Repair, Learning, retry, scheduler, or background
  runtime;
- memory redesign or temporal provenance runtime;
- API, router, schema, OpenAPI, persistence, or private runtime changes;
- `PROGRESS.md`, README, Constitution, Architecture, or existing test changes;
- M100B, M101, or any successor Build;
- commit, tag, push, or PM acceptance claim.

## 19. Build Authorization Gate

```text
M100A discovery: COMPLETE LOCALLY
Selected direction: ACTION_AUTHORITY_CONSOLIDATION_GAP
Recommended future Build: JUSTIFIED FOR PM REVIEW
Runtime Build authorization: NOT GRANTED
```

"JUSTIFIED FOR PM REVIEW" means only that the evidence supports a bounded
future design review. It is not permission to implement the selected gap.

## 20. Next-Step Gate

```text
M100A static/document lock: REQUIRED
M100A Git durability: NOT AUTHORIZED
M100A PM priority decision: PENDING EXTERNAL REVIEW
Next authorized action: HUMAN/PROJECT-MANAGER M100A PRIORITY REVIEW
```

Control returns to the human/project-manager. No successor milestone is
selected or authorized by this record.
