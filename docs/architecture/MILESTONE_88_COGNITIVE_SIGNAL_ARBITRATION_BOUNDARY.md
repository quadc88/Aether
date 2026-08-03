# Milestone 88 Cognitive Signal Arbitration Classification Boundary

## 1. Status and Scope

Status: accepted Milestone 88A boundary decision record, complete locally but
not finalized, committed, tagged, or pushed.

This record is authoritative for the Cognitive Signal Arbitration classification
boundary until an explicitly authorized later architecture or boundary revision
supersedes it. Milestone 88A is documentation and tests only. It does not
implement, extract, redirect, or otherwise change the runtime authorization
boundary. Milestone 88 remains open, Milestone 89 has not started.

The classification is NOT a runtime object or input.

No runtime function currently consumes the classification.

No behavior changes are introduced.

## 2. Purpose

The current production `aether/thinking/policy.py::decide_chat_policy` contains
nine ordered decision branches that mix constitutional hard constraints,
operational safety constraints, soft preference signals, and workflow/default
rules. Architecture v0.3.0 §18.8 requires Core Governance to own Cognitive
Signal Arbitration — the separation of hard constraints from soft signals.

This record classifies each current rule according to four architectural
categories without changing any runtime behavior, any rule precedence, or any
decision result. It establishes the authoritative classification that a future
separately authorized milestone may use to relocate hard constraints from
Thinking into the existing Governance envelope.

## 3. Authoritative Existing Baseline

The accepted starting baseline is:

- Architecture v0.3.0 and Constitution v0.2.0;
- full suite 2213 passed before Milestone 88A;
- Milestone 87 boundary tests 76 passed;
- Governance/policy/core focused suite 592 passed;
- architecture and Observation focused suite 240 passed;
- PROGRESS consistency suite 55 passed;
- OpenAPI 304 paths and 108 schemas;
- `aether/interface/api_server.py`: 8 direct `@app` routes, 23
  `include_router` calls, and zero direct `/action/*` routes;
- Constitution SHA-256
  `0055748f683bf753b3471a0317b68677752c312d4030b12fbc71684fd3af3ee1`;
- canonical drift 0 at fingerprint
  `600fd549588be7f536f704bc999be1987dcdf550225f2dc11dbf2fbf63ec2bcd`;
- tracked private/runtime paths empty and `docs/history` clean;
- Milestone 87 finalized: the 76 finalized Milestone 87 boundary tests pass
  unchanged and the finalized record
  `docs/architecture/MILESTONE_87_CORE_GOVERNANCE_AUTHORIZATION_BOUNDARY.md`
  is not modified.

Milestone 85's Observe/Verify lifecycle boundary remains in force. No
Observation classification or record becomes an execution trigger.

## 4. Relationship to Architecture v0.3.0

Architecture v0.3.0 §18.4 states that Core Governance owns "the operative risk
classification used for authorization (Verification supplies evidence)."
§18.8 states that "Cognitive Signal Arbitration belongs to Core Governance"
and that "Hard constraints define the allowed decision space. Soft decision
signals rank options only inside that allowed space."

This record classifies the current Thinking-policy rules according to those
ownership assignments. It does not move any rule. It does not change any
runtime behavior. It records what the current architecture requires, not what
the current code physically implements.

## 5. Relationship to Milestone 87

Milestone 87 established:

- The authoritative Governance decision-envelope location
  (`aether/core/governance.py::evaluate_authorization_envelope`);
- Core Coordination as the exact production caller from
  `aether/core/loop.py`;
- The thin Action compatibility facade (`aether/action/policy_gate.py`);
- The non-operative evidence parameters
  `risk_evidence` and `identity_integrity_evidence`;
- The exact envelope shape and fail-closed behavior.

Milestone 88 classifies the existing Thinking proposal rules that feed into
the Milestone 87 Governance envelope. Milestone 88 does not reopen, modify,
amend, or append to the finalized Milestone 87 record. The 76 finalized
Milestone 87 tests remain unchanged and authoritative. Risk and Identity
evidence remain non-operative. No new Governance decision rule is added.

## 6. Current Production Chain

The repository-proven chain is:

1. external `POST /chat`;
2. `aether.interface.api_server.chat` (Interface);
3. `aether.core.runtime.AetherRuntime.process_chat`;
4. `aether.core.loop.run_core_chat_loop` (Core Coordination);
5. `aether.perception.text.perceive_text_input`;
6. `aether.identity.guard.verify_identity_integrity` evidence;
7. `aether.time.clock.now_iso` and `time_state` facts;
8. optional `aether.memory.working.store.WorkingMemory` updates;
9. `aether.verification.risk.classify_risk` evidence;
10. `aether.core.loop._suggest_tool`, using
    `aether.action.tool_planner.infer_candidate_tool`, for a suggestion only;
11. `aether.thinking.policy.decide_chat_policy` proposal — **this record
    classifies the nine ordered branches of this function**;
12. `aether.core.governance.evaluate_authorization_envelope` — the current
    authoritative decision implementation, now receiving direct evidence as
    provenance inputs;
13. `aether.action.approval_request.build_approval_request` where applicable;
14. optional `aether.action.approval_queue.create_approval_record` producing a
    pending record;
15. response construction, `aether.core.loop_trace.build_loop_trace`, and
    `aether.memory.timeline.recorder.record_event`.

Production importer inventory for `evaluate_authorization_envelope`: exactly
`aether/core/loop.py` and `aether/action/policy_gate.py` (facade). The direct
test importers are
`tests/test_milestone_87_core_governance_authorization_boundary.py`,
`tests/test_policy_gate.py`, and `tests/test_core_loop.py`.

Production importer inventory for `decide_chat_policy`: exactly
`aether/core/loop.py`. The direct test importer is `tests/test_thinking_policy.py`.

## 7. Current Thinking-Policy Rule Inventory

The exact current ordered branches in
`aether/thinking/policy.py::decide_chat_policy` are:

| # | Source line | Triggering condition | Decision type |
|---|---|---|---|
| 1 | 53 | `identity_status == "changed"` | `block` |
| 2 | 72 | `identity_status in ("missing", "failed")` | `require_approval` |
| 3 | 90 | `not normalized_text or not normalized_text.strip()` | `ask_clarification` |
| 4 | 106 | `secret_found` (any term from `_SECRET_RISK_TERMS` in `risk_terms_detected`) | `require_approval` |
| 5 | 126 | `risk_level == "high"` | `require_approval` |
| 6 | 145 | `risk_level == "medium" and suggested_tool is not None` | `require_approval` |
| 7 | 163 | `risk_level == "low" and suggested_tool is not None` | `suggest_tool` |
| 8 | 181 | `not suggested_tool and len(normalized_text) < 10` | `ask_clarification` |
| 9 | 199 | (default — no condition) | `respond_only` |

All nine branches return a dict with keys: `decision_type`, `confidence`,
`reasons`, `required_user_confirmation`, `tool_suggestion_allowed`,
`tool_execution_allowed`, `blocked_reason`, `clarification_question`,
`next_step`, `warnings`. In all current branches `tool_execution_allowed` is
`False`. The legacy synthetic allow path (`tool_execution_allowed=True` in the
proposal) is handled by the Governance envelope, not by Thinking.

## 8. Classification Model

Four architectural categories, in order of authority:

### A. Constitutional Hard Constraint

A non-optimizable constraint directly grounded in a current Constitution
principle, priority, prohibition, Human Authority boundary, identity-integrity
requirement, privacy requirement, or high-risk requirement. These define the
hard boundary of the allowed decision space. No soft signal, convenience,
latency, cost, or optimization may override them.

### B. Operational Hard Constraint

A non-optimizable runtime safety or validity constraint that restricts the
allowed decision space but is not necessarily a direct quotation or standalone
article of the Constitution. These are mandatory because their violation would
create an unsafe or invalid runtime state. They cannot be overridden by
convenience, quality, latency, cost, or another soft signal.

### C. Soft Decision Signal

A preference or ranking consideration that may influence selection only after
all hard constraints (A and B) are satisfied. A soft signal must not
independently override a hard constraint. It may influence tool suggestion,
quality, relevance, convenience, or response preference.

### D. Thinking Workflow / Default Rule

A workflow-selection, clarification, response-mode, fallback, or default rule
owned by Thinking rather than Governance arbitration. These select reasoning
or interaction flow without becoming authorization authority. They are not
automatically soft arbitration signals. They are not automatically hard
constraints.

## 9. Constitutional Hard Constraints

Rules directly grounded in the Constitution v0.2.0:

### Rule 1 — Identity integrity changed → block

**Constitution grounding:** §1.1 (Identity Seed must not be silently modified),
§1.2 (controlled modification only through explicit human-approved process),
§9.1 (identity remains, personality evolves).

**Paraphrase:** A changed identity seed checksum represents unauthorized
modification of the identity foundation. The Constitution requires explicit
human-approved processes for any identity modification. A changed checksum
without human review violates §1.1 and §1.2. Blocking is the only safe
response.

**Category: A (Constitutional Hard Constraint).**

### Rule 2 — Identity missing or failed → require_approval

**Constitution grounding:** §1.1 (Identity Seed integrity), §1.2 (controlled
modification), §10 (Human Authority — the user may inspect, edit, delete
memory; disable tools; approve or deny actions), §10.1 (limits of authority —
Aether must not silently corrupt identity continuity mechanisms).

**Paraphrase:** Missing or failed identity state means the identity integrity
guard cannot verify the seed. Proceeding without human review risks silent
identity corruption (§10.1) and bypasses the human-approved modification
process (§1.2). Human inspection is required before any action.

**Category: A (Constitutional Hard Constraint).**

### Rule 4 — Secret terms detected → require_approval

**Constitution grounding:** §6.1 (permission levels — write or execute tools
require user permission unless explicitly pre-approved; sensitive terms like
passwords, API keys, tokens must not be exposed), §10.1 (limits of authority
— Aether must not conceal consequential actions or bypass safety mechanisms).

**Paraphrase:** Text containing sensitive terms (passwords, tokens, API keys,
credentials) introduces a risk of unauthorized disclosure or credential
handling without explicit human review. The Constitution requires user
permission for write/execute actions and prohibits exposure of sensitive
values. Requiring approval is the minimum safe response.

**Category: A (Constitutional Hard Constraint).**

### Rule 5 — High risk → require_approval

**Constitution grounding:** §5.1 (high-risk actions require strong verification
and usually human confirmation — includes deleting/overwriting important files,
executing unknown code, changing identity/memory/security settings, actions
that could cause serious harm), §8.2 (known uncertainty — if action risk is
significant and confidence is low, Aether should pause, verify, ask for
clarification, ask for confirmation, refuse unsafe execution), §11.1 (safety
and responsibility — responsibility and verification override speed, convenience,
and obedience).

**Paraphrase:** High-risk actions as defined by the risk classifier match the
Constitution's enumeration of high-risk categories in §5.1. The Constitution
requires strong verification and usually human confirmation for such actions.
Requiring approval is the mandated minimum response.

**Category: A (Constitutional Hard Constraint).**

## 10. Operational Hard Constraints

Rules that are mandatory safety or validity constraints but not directly
quoting a standalone Constitution article:

### Rule 6 — Medium risk + tool candidate → require_approval

**Basis:** No single Constitution article directly mandates approval for
medium-risk tool use. However, the Constitution §5.1 enumerates "modifying
production systems" and "actions that could cause serious harm" as high-risk.
Medium risk with a tool suggestion represents a state between low-risk
conversation and high-risk destructive action. The precautionary requirement
is grounded in §11.1 (safety and responsibility override convenience) and
§8.2 (pause, verify, ask for confirmation when risk is significant). This is
an operational hard constraint: it restricts the allowed decision space by
requiring approval before a tool is suggested when risk is non-trivial, but
it is not a direct constitutional article.

**Category: B (Operational Hard Constraint).**

**Note per Binding Correction §5:** This rule produces `require_approval`,
which deterministically removes the directly allowed path. It must not be
classified as a soft signal merely because it is precautionary or operational.
It is classified as an Operational Hard Constraint.

## 11. Soft Decision Signals

Rules that rank or prefer options only after hard constraints are satisfied:

### Rule 7 — Low risk + tool candidate → suggest_tool

**Basis:** Low-risk requests with a matched tool are not prohibited. The rule
suggests a tool but does not authorize execution (`tool_execution_allowed` is
`False`). This is a soft signal: it ranks tool suggestion as desirable within
the allowed decision space but does not create execution authority or override
any hard constraint.

**Category: C (Soft Decision Signal).**

## 12. Thinking Workflow and Default Rules

Rules that select reasoning or interaction flow without becoming authorization
authority:

### Rule 3 — Empty text → ask_clarification

**Basis:** Empty or whitespace-only input has no actionable content. The rule
routes to clarification rather than authorization. It is a workflow rule
owned by Thinking: it selects the interaction flow (ask for input) without
imposing a Governance constraint.

**Category: D (Thinking Workflow / Default Rule).**

### Rule 8 — Short input + no tool → ask_clarification

**Basis:** Very short input without a tool match is ambiguous. The rule routes
to clarification rather than authorization. It is a workflow rule owned by
Thinking: it selects the interaction flow (request more detail) without
imposing a Governance constraint.

**Category: D (Thinking Workflow / Default Rule).**

### Rule 9 — Default → respond_only

**Basis:** When no elevated risk, no special conditions, and no tool match are
detected, the default response mode is a textual reply. This is a workflow
default rule owned by Thinking: it selects the response mode without imposing
a Governance constraint.

**Category: D (Thinking Workflow / Default Rule).**

## 13. Rule-by-Rule Classification Table

| Order | Current condition | Current output | Current owner | Architectural category | Basis | Can optimization override it? | Future target owner | Runtime changed by M88A? |
|---|---|---|---|---|---|---|---|---|
| 1 | identity_status == "changed" | block, required_user_confirmation=True, tool_execution_allowed=False | aether/thinking/policy.py | Constitutional Hard Constraint | Constitution §1.1, §1.2, §9.1 | No | Core Governance (future, if authorized) | No |
| 2 | identity_status in ("missing", "failed") | require_approval, required_user_confirmation=True, tool_execution_allowed=False | aether/thinking/policy.py | Constitutional Hard Constraint | Constitution §1.1, §1.2, §10, §10.1 | No | Core Governance (future, if authorized) | No |
| 3 | empty/whitespace text | ask_clarification, required_user_confirmation=False, tool_execution_allowed=False | aether/thinking/policy.py | Thinking Workflow / Default Rule | Workflow routing | N/A (workflow) | Thinking (unchanged) | No |
| 4 | secret terms detected | require_approval, required_user_confirmation=True, tool_execution_allowed=False | aether/thinking/policy.py | Constitutional Hard Constraint | Constitution §6.1, §10.1 | No | Core Governance (future, if authorized) | No |
| 5 | risk_level == "high" | require_approval, required_user_confirmation=True, tool_execution_allowed=False | aether/thinking/policy.py | Constitutional Hard Constraint | Constitution §5.1, §8.2, §11.1 | No | Core Governance (future, if authorized) | No |
| 6 | risk_level == "medium" and suggested_tool is not None | require_approval, required_user_confirmation=True, tool_execution_allowed=False | aether/thinking/policy.py | Operational Hard Constraint | Constitution §11.1, §8.2 (operational interpretation) | No | Core Governance (future, if authorized) | No |
| 7 | risk_level == "low" and suggested_tool is not None | suggest_tool, required_user_confirmation=False, tool_execution_allowed=False | aether/thinking/policy.py | Soft Decision Signal | Operational preference within allowed space | Yes (within hard constraints) | Thinking (unchanged) | No |
| 8 | not suggested_tool and len(text) < 10 | ask_clarification, required_user_confirmation=False, tool_execution_allowed=False | aether/thinking/policy.py | Thinking Workflow / Default Rule | Workflow routing | N/A (workflow) | Thinking (unchanged) | No |
| 9 | (default) | respond_only, required_user_confirmation=False, tool_execution_allowed=False | aether/thinking/policy.py | Thinking Workflow / Default Rule | Default response mode | N/A (workflow) | Thinking (unchanged) | No |

Summary counts:
- Constitutional Hard Constraints (A): 4 rules (1, 2, 4, 5)
- Operational Hard Constraints (B): 1 rule (6)
- Soft Decision Signals (C): 1 rule (7)
- Thinking Workflow / Default Rules (D): 3 rules (3, 8, 9)
- Total: 9 rules

## 14. Rule Precedence and Non-Override Contract

The exact source precedence is preserved:

1. Rule 1 (identity changed) — highest priority, blocks all further processing.
2. Rule 2 (identity missing/failed) — second priority, requires approval.
3. Rule 3 (empty text) — third priority, clarification.
4. Rule 4 (secret terms) — fourth priority, requires approval.
5. Rule 5 (high risk) — fifth priority, requires approval.
6. Rule 6 (medium risk + tool) — sixth priority, requires approval.
7. Rule 7 (low risk + tool) — seventh priority, suggestion only.
8. Rule 8 (short input + no tool) — eighth priority, clarification.
9. Rule 9 (default) — lowest priority, respond only.

Lock:

- Current source order remains unchanged.
- Milestone 88A does not reorder rules.
- A later soft signal cannot override an earlier hard constraint.
- Workflow/default selection cannot create authorization.
- Governance remains the authority owner even though current hard rules may
  still be physically evaluated in Thinking.
- Current physical placement does not redefine architectural ownership.
- No source migration is claimed.
- No evidence activation is claimed.

## 15. Proposal, Evidence, and Authority Ownership

Thinking proposes. Governance authorizes. Verification and Identity supply
evidence. Action executes only within authorization.

- `decide_chat_policy` (Thinking) produces the non-authoritative proposal.
- `verify_identity_integrity` (Identity) supplies direct evidence.
- `classify_risk` (Verification) supplies direct evidence.
- `evaluate_authorization_envelope` (Core Governance) makes the authoritative
  decision.
- The classification in this record does not change any of these roles.

## 16. Current Runtime Behavior

The current runtime behavior is unchanged by Milestone 88A:

- All nine decision branches produce exactly the same outputs as before.
- `tool_execution_allowed` is `False` in all Thinking branches.
- `required_user_confirmation` values are unchanged.
- `blocked_reason`, `clarification_question`, `next_step`, `warnings` are
  unchanged.
- No new execution path is created.
- No approval semantics are changed.
- No persistence is added.
- No API, router, endpoint, model, or schema is changed.
- The `/chat` response shape is unchanged.

## 17. Future Migration Implications

The record may identify future possibilities such as:

- Relocating verified Constitutional Hard Constraints (Rules 1, 2, 4, 5) from
  Thinking into the Governance envelope as hard-constraint enforcement.
- Relocating the Operational Hard Constraint (Rule 6) into Governance.
- Retaining Soft Decision Signals (Rule 7) and Workflow/Default Rules (Rules
  3, 8, 9) in Thinking.
- Allowing Governance to receive direct risk and Identity evidence for a
  separately authorized hard-constraint activation.
- Removing legacy authorization-like proposal fields from Thinking after
  compatibility proof.

These are implications only.

Do not authorize:

- source migration;
- evidence activation;
- behavior changes;
- policy tightening;
- new allow or deny paths.

Future work requires a new post-Milestone-88 selection Plan.

## 18. Boundary-Test Contract

`tests/test_milestone_88_cognitive_signal_arbitration_boundary.py` locks:

- the exact H1 and 22-section structure;
- documentation/tests-only scope;
- classification is not a runtime object;
- no current runtime consumer is claimed;
- the four exact classification categories;
- the actual current rule count (9);
- every source rule inventoried once with exact order;
- exact trigger conditions and stable AST markers;
- exact current decision outputs;
- exact confirmation/execution compatibility fields;
- the exact architectural classification table;
- constitutional grounding cited only when verified present;
- operational hard constraints distinct from constitutional ones;
- mandatory approval rules not misclassified as soft signals;
- soft signals cannot override hard constraints;
- workflow/default rules separately classified;
- clarification/default routing does not become Governance authority;
- current physical ownership versus architectural ownership;
- Thinking proposes; Governance authorizes; Verification and Identity supply
  evidence; Action executes only within authorization;
- current rule precedence remains unchanged;
- no source migration is claimed;
- no evidence activation is claimed;
- risk evidence remains non-operative;
- identity evidence remains non-operative;
- no runtime behavior change;
- no execution enabled;
- no persistence added;
- Milestone 87 record remains referenced and unchanged;
- existing 76 Milestone 87 tests remain authoritative;
- Architecture remains 0.3.0;
- Constitution remains 0.2.0;
- OpenAPI 304/108 is recorded;
- api_server 8/23/0 is recorded;
- Milestone 88 remains open;
- Milestone 89 does not start automatically;
- Milestone 88 closes only after 88A Finalization;
- future migration requires a new Plan.

The suite uses only static inspection and pure deterministic policy calls.
It does not use TestClient, invoke endpoints, write files, persist records,
execute tools/actions, or access the network.

## 19. Protected Files and Non-Goals

Protected and unchanged in Milestone 88A: all `aether/*`, all existing tests,
Constitution, Architecture, README, existing architecture records (including
the finalized Milestone 87 record), API models, routers, endpoints, queues,
stores, schemas, `docs/history`, dependency files, and runtime/private data.

Non-goals include:
- moving any rule from Thinking into Governance;
- changing rule precedence;
- changing any decision result;
- enabling tool or action execution;
- making risk or Identity evidence operative;
- adding persistence, queues, stores, schemas, routers, endpoints, or API
  models;
- modifying the finalized Milestone 87 decision record;
- modifying the finalized Milestone 87 boundary tests;
- modifying docs/ARCHITECTURE.md or docs/CONSTITUTION.md;
- beginning Milestone 88B, 88C, or any future extraction;
- defining Milestone 89.

## 20. Completion and Acceptance Criteria

Milestone 88A completes locally when:

1. This decision record exists with the exact H1 and all 22 sections.
2. The boundary-test suite exists and passes.
3. All existing Milestone 87 tests pass unchanged (76 passed).
4. All existing Governance/policy/core focused tests pass (592 passed).
5. All architecture and Observation tests pass (240 passed).
6. PROGRESS consistency tests pass (55 passed).
7. OpenAPI remains 304/108 and api_server remains 8/23/0.
8. Constitution SHA is unchanged.
9. `aether/*` production source is unchanged.
10. The finalized Milestone 87 record and tests are unchanged.
11. Drift is 0.
12. Full suite passes.

Human/project-manager review and acceptance is the next authorized action.

## 21. Milestone 88 Finalization and Closure Rule

Milestone 88A completes locally only when this record and its new contract
suite pass every focused, architecture, Observation, protected-core,
Constitution, OpenAPI, structural, isolation, drift, and full-suite gate,
after which PROGRESS.md may be updated truthfully. It remains unfinalized
and uncommitted.

Milestone 88 remains open after 88A. Human/project-manager review is the next
authorized action. Only explicit acceptance may authorize a future Milestone
88B or later step. Milestone 88 closes only after its separately authorized
Finalization sequence. Milestone 89 does not start automatically.

## 22. Deferred Behavioral Work

The following behavioral work is deferred and NOT authorized by this record:

- Relocating Constitutional Hard Constraints (Rules 1, 2, 4, 5) from Thinking
  into Governance as hard-constraint enforcement.
- Relocating the Operational Hard Constraint (Rule 6) into Governance.
- Activating `risk_evidence` or `identity_integrity_evidence` to alter
  decision results.
- Adding new allow or deny paths.
- Changing rule precedence.
- Any behavior change to the `/chat` response.

Any of the above requires a new post-Milestone-88 selection Plan and separate
explicit authorization.
