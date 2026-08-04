# Milestone 89 Identity Hard-Constraint Migration Boundary

## 1. Status and Scope

Status: accepted Milestone 89A boundary decision record, corrected by 89A-R,
89A-R2, 89A-R3, and 89B-R. Milestone 89B implemented, committed, tagged, and
pushed. Milestone 89 is now CLOSED. See Section 1.2 for finalization facts.

Milestone 89A-R2 is a DOCUMENTATION-AND-TESTS-ONLY SECOND RECONCILIATION PASS.
It corrected three remaining contract defects found by project-manager review:

1. the decision record had been expanded from the authorized exact
   twenty-four-section structure to twenty-five sections;
2. the Thinking-policy supersession matrix classified six tests as requiring
   amendment but listed only five in the exact amendment set;
3. the compatibility bridge did not define the exact runtime data path from
   Governance to Core Coordination and every downstream consumer.

Milestone 89A-R3 is a DOCUMENTATION-AND-TESTS-ONLY FINAL MIGRATION-BOUNDARY
RECONCILIATION PASS. It corrects three further defects found by
project-manager review:

1. the combined lightweight suite must include the Milestone 89 tests and
   therefore totals 322 (110 + 50 + 76 + 31 + 55) before any R3 test-count
   change, not 212;
2. Trace Strategy T1 recorded the Governance-derived effective policy under
   the Thinking stage, misrepresenting architectural authority; it is replaced
   by Strategy T3 — Truthful Raw Thinking Proposal Trace;
3. the partial supersession contract for
   `TestHardRules::test_tool_execution_always_false` did not precisely prove
   that raw Thinking no longer reacts to Identity status; the exact
   full-dictionary Identity-insensitivity contract is now locked.

This record is authoritative for the Identity Hard-Constraint migration
boundary until an explicitly authorized later architecture or boundary
revision supersedes it. Milestone 89A is documentation and tests only. It
does not migrate Rules 1 or 2, does not make Identity evidence operative,
and does not change any runtime behavior. Milestone 89 remains open,
Milestone 90 has not started.

The future migration is classified as:

EXTERNALLY DECISION-, APPROVAL-, RESPONSE-SHAPE-, AND EXECUTION-FLAG
PRESERVING, WITH AN INTENTIONAL DIAGNOSTIC TRACE SEMANTIC CHANGE AND
INTERNAL PHYSICAL-OWNERSHIP CHANGE

The entire migration is never called externally behavior-preserving without
this qualification. The intentional diagnostic trace semantic change is
limited to Identity-triggered Thinking-stage trace content (see Section 16.2
and Section 18.10).

### 1.1 Milestone 89B-R Build-Record Correction (supersession-matrix reconciliation)

Milestone 89B (Identity Hard-Constraint Runtime Extraction) completed locally
and passed its independent audit in every runtime, structural, regression,
isolation, and full-suite gate. The independent audit was marked FAIL only
because three necessary Milestone 88 test amendments were omitted from the
original project-manager amendment matrix. Milestone 89B-R is a DOCUMENTATION,
TEST-AUTHORIZATION-MATRIX, AND BUILD-RECORD RECONCILIATION: it formally
corrects the supersession matrix and Build records. The valid Milestone 89B
runtime implementation was NOT reverted and was NOT modified during
reconciliation.

Corrected authoritative supersession matrix (final):

- Milestone 87 (2): test_60_direct_identity_evidence_operative_only_for_identity_rules;
  test_62_identity_evidence_raw_values_absent_from_reason_and_warnings.
- Milestone 88 (7): test_07_actual_current_rule_count_is_seven;
  test_10_exact_trigger_conditions_from_ast;
  test_11_exact_current_decision_outputs;
  test_12_exact_confirmation_and_execution_fields;
  test_29_identity_evidence_operative_only_through_governance;
  test_30_exact_new_classification_string;
  test_45_only_authorized_production_modules_changed.
- Thinking (5 full + 1 partial): test_block_on_identity_changed;
  test_block_even_with_tool_and_medium_risk;
  test_require_approval_when_missing;
  test_require_approval_when_failed;
  test_identity_issues_have_high_confidence;
  test_tool_execution_always_false (partial, 18 of 30 parametrized cases).
- Total existing tests touched: 15 (14 full amendments + 1 partial
  amendment).

M88 Tests 07, 10, and 45 are EXPLICIT_89B_SUPERSESSION_AMENDMENT_REQUIRED:
each asserts against active production source (rule-branch count, AST trigger
and return locations, and the authorized production-change set) and cannot
retain its pre-migration contract after the authorized runtime migration.
M88 Tests 08 and 09 remain unchanged historical locks. Milestone 88 remains
historically valid as the classification boundary that first inventoried all
nine rules; Milestone 89B does not rewrite the historical classification.
Test 45 changes only from a tests-only source-protection assertion to the
exact authorized three-production-file migration assertion.

Exact nine-path Milestone 89B Build file set:
- `PROGRESS.md`;
- `aether/core/governance.py`;
- `aether/core/loop.py`;
- `aether/thinking/policy.py`;
- `docs/architecture/MILESTONE_89_IDENTITY_HARD_CONSTRAINT_MIGRATION_BOUNDARY.md`;
- `tests/test_milestone_87_core_governance_authorization_boundary.py`;
- `tests/test_milestone_88_cognitive_signal_arbitration_boundary.py`;
- `tests/test_milestone_89_identity_hard_constraint_migration_boundary.py`;
- `tests/test_thinking_policy.py`.

Exactly three production paths change: `aether/core/governance.py`,
`aether/core/loop.py`, and `aether/thinking/policy.py`.

Exact established test gate labels (independent-audit verified):
- Milestone 89: 150 passed; Milestone 88: 50 passed; Milestone 87: 76 passed;
- exact established Governance/policy/core gate: 592 passed;
- exact established Architecture/Observation gate: 240 passed;
- PROGRESS consistency: 55 passed;
- exact combined suite: 362 passed;
- full suite: 2413 passed;
- OpenAPI 304 paths / 108 schemas; api_server 8 direct `@app` routes / 23
  `include_router` / zero direct `/action/*`.

Supplemental expanded Governance-related run (597 passed) and supplemental expanded Architecture/Observation run (534 passed) are supplemental expanded runs only and never replace the established 592 and 240 gate labels.

## 2. Purpose

Milestone 88 classified Rules 1 and 2 as architectural hard constraints
owned by Core Governance but physically evaluated in Thinking. This record
documents the exact current behavior, the exact compatibility surface, and
the exact future migration requirements for moving Rules 1 and 2 from
Thinking into the existing Governance envelope.

The record establishes whether the migration can proceed safely and defines
the minimal set of future amendments required. Milestone 89A-R2 additionally
locks the exact future 89B runtime data path, the exact Core-Coordination
consumer routing, the selected trace strategy, the exact policy-snapshot
contract, and the reconciled supersession matrix.

## 3. Authoritative Existing Baseline

The accepted baseline at the start of Milestone 89A-R2 is:

- Architecture v0.3.0 and Constitution v0.2.0;
- full suite 2348 passed before Milestone 89A-R2 (2320 baseline + 28
  Milestone 89A-R reconciliation tests);
- Milestone 89A-R completed locally with 85 Milestone 89 tests across 14
  classes (13 original + TestReconciliationAccounting);
- Milestone 88 boundary tests 50 passed (corrected classification);
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
- Milestone 87 finalized: the 76 finalized Milestone 87 boundary tests
  pass unchanged and the finalized record is not modified;
- Milestone 88 finalized (corrected): the 50 finalized Milestone 88
  boundary tests pass unchanged and the finalized record is not modified;
- local repository changes at 89A-R2 preflight exactly:
  - `PROGRESS.md` (modified),
  - `docs/architecture/MILESTONE_89_IDENTITY_HARD_CONSTRAINT_MIGRATION_BOUNDARY.md`
    (new),
  - `tests/test_milestone_89_identity_hard_constraint_migration_boundary.py`
    (new);
- HEAD == origin/main == `943b442b3b765904fa508cc617ce25fd279a8b91`.

### 3.1 Milestone 89A-R3 preflight baseline (confirmed independently)

- Milestone 89 boundary suite: 110 passed (15 classes);
- Milestone 88 boundary suite: 50 passed;
- Milestone 87 boundary suite: 76 passed;
- Governance/policy/core focused suite: 592 passed;
- architecture and Observation focused suite: 240 passed;
- PROGRESS consistency suite: 55 passed;
- exact required combined suite (M89 + M88 + M87 + M86 + repair family):
  **322 passed** (110 + 50 + 76 + 31 + 55) — the Milestone 89 combined gate
  includes Milestone 89 and must never be recorded as 212. The exact
  combined-suite file list:
  1. `tests/test_milestone_89_identity_hard_constraint_migration_boundary.py`
     (110 at R3 preflight),
  2. `tests/test_milestone_88_cognitive_signal_arbitration_boundary.py` (50),
  3. `tests/test_milestone_87_core_governance_authorization_boundary.py` (76),
  4. `tests/test_milestone_86_architecture_evolution_contract.py` (31),
  5. `tests/test_repair_family_service_boundary.py` (55);
- full suite before R3 test-count change: 2373 passed
  (2348 pre-R2 + 25 R2 boundary tests);
- OpenAPI 304 paths and 108 schemas;
- api_server 8 direct `@app` routes / 23 `include_router` / 0 direct
  `/action/*`;
- Architecture v0.3.0 and Constitution SHA-256
  `0055748f683bf753b3471a0317b68677752c312d4030b12fbc71684fd3af3ee1`
  unchanged;
- canonical drift 0; tracked private/runtime empty; `docs/history` clean;
- production source unchanged; Milestone 87 and 88 records and tests
  unchanged;
- local repository changes at 89A-R3 preflight exactly the same three paths
  listed above.

Historical note: the figure 212 was the pre-Milestone-89 combined baseline
(M88 50 + M87 76 + M86 31 + repair family 55 = 212) excluding Milestone 89.
It is historical only and must not be reported as the Milestone 89 combined
result.

Milestone 85's Observe/Verify lifecycle boundary remains in force.

## 4. Relationship to Architecture v0.3.0

Architecture v0.3.0 §18.4 states that Core Governance owns "the operative
risk classification used for authorization (Verification supplies evidence)."
§18.8 states that "Cognitive Signal Arbitration belongs to Core Governance"
and that "Hard constraints define the allowed decision space. Soft decision
signals rank options only inside that allowed space."

The corrected Milestone 88 classification places Rules 1 and 2 as hard
constraints (Rules 1 as Constitutional Hard Constraint, Rules 2 as
Operational Hard Constraint with constitutional support). These rules are
architecturally owned by Core Governance but physically evaluated in
Thinking. The migration aligns physical ownership with architectural
ownership.

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

Milestone 89A does not reopen, modify, amend, or append to the finalized
Milestone 87 record. The 76 finalized Milestone 87 tests remain authoritative
(two tests — test_60 and test_62 — are amended under the separately authorized
89B/89B-R supersession matrix; the remainder pass unchanged). Risk and
Identity evidence remain non-operative in 89A.
No new Governance decision rule is added in 89A.

## 6. Relationship to Corrected Milestone 88

Milestone 88 (corrected by 88A-R) established:

- The exact 22-section classification record;
- The corrected four-category model: 2 Constitutional Hard Constraints
  (Rules 1, 5), 3 Operational Hard Constraints (Rules 2, 4, 6),
  1 Soft Decision Signal (Rule 7), 3 Thinking Workflow/Default Rules
  (Rules 3, 8, 9);
- The classification is NOT a runtime object;
- No runtime function currently consumes the classification;
- The 50 corrected Milestone 88 boundary tests pass unchanged.

Milestone 89A uses the corrected Milestone 88 classification as binding
authority. It does not modify the Milestone 88 record. The 50 corrected
Milestone 88 boundary tests pass (seven tests are amended under the separately
authorized 89B/89B-R supersession matrix — test_07, test_10, test_11, test_12,
test_29, test_30, test_45; the remainder pass unchanged, including historical
locks test_08 and test_09).

## 7. Current Production Chain

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
11. `aether.thinking.policy.decide_chat_policy` proposal — **Rules 1 and
    2 evaluated here physically**;
12. `aether.core.governance.evaluate_authorization_envelope` — **Rules 1
    and 2 NOT evaluated here currently (evidence non-operative)**;
13. `aether.action.approval_request.build_approval_request` where applicable;
14. optional `aether.action.approval_queue.create_approval_record` producing a
    pending record;
15. response construction, `aether.core.loop_trace.build_loop_trace`, and
    `aether.memory.timeline.recorder.record_event`.

Production importer inventory for `evaluate_authorization_envelope`: exactly
`aether/core/loop.py` and `aether/action/policy_gate.py` (facade).

Production importer inventory for `decide_chat_policy`: exactly
`aether/core/loop.py`.

## 8. Current Identity Evidence Contract

### 8.1 Producer: aether/identity/guard.py::verify_identity_integrity

Returns `_safe_summary(state)` which produces:

```python
{
    "status": str,           # "verified", "changed", "missing", "failed", or "unknown"
    "current_sha256": str,   # first 12 chars of SHA-256 (truncated)
    "known_sha256": str,     # first 12 chars of SHA-256 (truncated)
    "changed": bool,         # True iff status == "changed"
    "updated": str | None,   # ISO timestamp or None
    "warnings": list[str],   # descriptions of checksum_mismatch/file_missing/load_failed events
}
```

Possible `status` values (from source analysis):
- `"verified"` — checksum matches
- `"changed"` — checksum differs (Rule 1 trigger)
- `"missing"` — identity seed file not found (Rule 2 trigger)
- `"failed"` — guard state load/parse failed (Rule 2 trigger)
- `"unknown"` — default fallback if status key missing

### 8.2 Thinking Input

`decide_chat_policy` receives `identity_integrity_status: dict | None`.

Thinking extracts: `identity_status = identity_integrity_status.get("status", "")`

Then evaluates:
- Rule 1: `identity_status == "changed"` → block
- Rule 2: `identity_status in ("missing", "failed")` → require_approval

### 8.3 Governance Input (today)

`evaluate_authorization_envelope` receives `identity_integrity_evidence: dict | None`.

**Current behavior:** The parameter is accepted but NOT used in any decision branch.
The envelope evaluates only `thinking_policy`, `requested_action`, and `context`.

### 8.4 Evidence Equivalence

For ALL current policy inputs, evidence-present and evidence-absent calls
return exactly equal envelopes:

```python
evaluate_authorization_envelope(thinking_policy=p)
# ==
evaluate_authorization_envelope(thinking_policy=p, identity_integrity_evidence=e)
```

This equivalence holds for all 9 rule outputs plus missing/empty/malformed
policy inputs.

## 9. Current Rule 1 Contract

**Trigger:** `identity_status == "changed"` (from `identity_integrity_status.get("status", "")`)

**Current Thinking output:**
```python
{
    "decision_type": "block",
    "confidence": "high",
    "reasons": ["Identity seed checksum changed — integrity compromised."],
    "required_user_confirmation": True,
    "tool_suggestion_allowed": False,
    "tool_execution_allowed": False,
    "blocked_reason": "Identity integrity changed. Human review is required before continuing.",
    "clarification_question": None,
    "next_step": "Verify identity seed integrity before continuing.",
    "warnings": ["Identity seed integrity mismatch detected."],
}
```

**Governance envelope transformation:**
```python
{
    "allowed": False,
    "decision": "block",
    "reason": "Identity integrity changed. Human review is required before continuing.",
    "required_user_confirmation": True,
    "tool_execution_allowed": False,
    "action_execution_allowed": False,
    "requested_action": suggested_tool or None,
    "policy_snapshot": dict(thinking_policy),  # shallow copy of above
    "warnings": [],  # Governance clears warnings; Thinking warnings preserved in snapshot
}
```

**Downstream effects:**
- `build_approval_request(policy_gate=envelope)`:
  - `approval_required: True`
  - `approval_type: "blocked_identity_review"`
  - `approval_status: "pending"`
  - `reason: "Identity integrity changed. Human review is required before continuing."`
  - `required_confirmations` includes identity-specific items
- `run_core_chat_loop` response:
  - `execution_allowed: False`
  - `execution_decision: "block"`
  - `execution_reason: "Identity integrity changed..."`
  - `policy_gate: envelope` (as above)
- `build_loop_trace`:
  - `safety.tool_execution_allowed: False`
  - `safety.tool_executed: False`
  - `safety.execution_allowed: False`
  - `stages[policy_gate].summary: "Decision: block"`
- Timeline: `record_event(event_type="chat_input", title="Chat input (high)", ...)`

## 10. Current Rule 2 Contract

**Trigger:** `identity_status in ("missing", "failed")`

**Current Thinking output (status="missing"):**
```python
{
    "decision_type": "require_approval",
    "confidence": "high",
    "reasons": ["Identity integrity status is 'missing'. Human inspection is needed before proceeding."],
    "required_user_confirmation": True,
    "tool_suggestion_allowed": False,
    "tool_execution_allowed": False,
    "blocked_reason": None,
    "clarification_question": None,
    "next_step": "Human should inspect identity integrity status.",
    "warnings": ["Identity integrity status: missing."],
}
```

**Current Thinking output (status="failed"):**
```python
{
    "decision_type": "require_approval",
    "confidence": "high",
    "reasons": ["Identity integrity status is 'failed'. Human inspection is needed before proceeding."],
    "required_user_confirmation": True,
    "tool_execution_allowed": False,
    "blocked_reason": None,
    "clarification_question": None,
    "next_step": "Human should inspect identity integrity status.",
    "warnings": ["Identity integrity status: failed."],
}
```

**Governance envelope transformation:**
```python
{
    "allowed": False,
    "decision": "require_approval",
    "reason": "Human approval is required before execution.",
    "required_user_confirmation": True,
    "tool_execution_allowed": False,
    "action_execution_allowed": False,
    "requested_action": suggested_tool or None,
    "policy_snapshot": dict(thinking_policy),
    "warnings": [],
}
```

Note: Governance uses a GENERIC reason ("Human approval is required before execution.")
not the Thinking-specific reason. This is an INTERNAL SEMANTIC DIFFERENCE.

**Downstream effects:**
- `build_approval_request(policy_gate=envelope)`:
  - `approval_required: True`
  - `approval_type: "human_review"`
  - `approval_status: "pending"`
  - `reason: "Human approval is required before execution."`
  - Note: This differs from Rule 1's `approval_type: "blocked_identity_review"`
- `run_core_chat_loop` response:
  - `execution_allowed: False`
  - `execution_decision: "require_approval"`
  - `execution_reason: "Human approval is required before execution."`
- Loop trace stage: `"Decision: require_approval"`
- Timeline: same as Rule 1 (high importance)

## 11. Current Rule Precedence

Source order in `decide_chat_policy`:

1. Rule 1: identity_status == "changed" → block
2. Rule 2: identity_status in ("missing", "failed") → require_approval
3. Rule 3: empty text → ask_clarification
4. Rule 4: secret terms → require_approval
5. Rule 5: high risk → require_approval
6. Rule 6: medium risk + tool → require_approval
7. Rule 7: low risk + tool → suggest_tool
8. Rule 8: short input + no tool → ask_clarification
9. Rule 9: default → respond_only

Rules 1 and 2 PRECEDE all other rules. They short-circuit the entire chain.

## 12. Current Thinking-Policy Output Contract

All 9 rules return a dict with these exact keys:

| Key | Type | Rule 1 | Rule 2 |
|---|---|---|---|
| `decision_type` | str | "block" | "require_approval" |
| `confidence` | str | "high" | "high" |
| `reasons` | list[str] | 1-element | 1-element (f-string) |
| `required_user_confirmation` | bool | True | True |
| `tool_suggestion_allowed` | bool | False | False |
| `tool_execution_allowed` | bool | False | False |
| `blocked_reason` | str \| None | "Identity integrity changed..." | None |
| `clarification_question` | str \| None | None | None |
| `next_step` | str | "Verify identity seed..." | "Human should inspect..." |
| `warnings` | list[str] | 1-element | 1-element (f-string) |

## 13. Current Governance-Envelope Contract

`evaluate_authorization_envelope` returns a dict with these exact keys:

| Key | Type | Rule 1 (via block) | Rule 2 (via require_approval) |
|---|---|---|---|
| `allowed` | bool | False | False |
| `decision` | str | "block" | "require_approval" |
| `reason` | str | blocked_reason from policy | "Human approval is required before execution." |
| `required_user_confirmation` | bool | True | True |
| `tool_execution_allowed` | bool | False | False |
| `action_execution_allowed` | bool | False | False |
| `requested_action` | dict|None | suggested_tool or None | suggested_tool or None |
| `policy_snapshot` | dict|None | dict(thinking_policy) | dict(thinking_policy) |
| `warnings` | list[str] | [] | [] |

## 14. Downstream Consumer Inventory

### 14.1 aether/core/loop.py (Core Coordination)
- Consumes: `policy_gate_result` (envelope)
- Fields read: `allowed`, `decision`, `reason`
- Also consumes: `thinking_policy` (separately, for response assembly)
- Persists: no (envelope passed to response dict)
- Exact equality required: yes (response fields copied verbatim)
- Future migration impact: LOW — envelope shape unchanged

### 14.2 aether/action/approval_request.py
- Consumes: `policy_gate` (envelope)
- Fields read: `decision`, `reason`
- Also consumes: `thinking_policy` (separately, for decision_type, blocked_reason)
- Persists: no (constructs approval_request dict)
- Exact equality required: structural (decision, reason values)
- Future migration impact: MEDIUM — reason field differs between Thinking and Governance for Rule 2

### 14.3 aether/core/loop_trace.py
- Consumes: safety flags and warning counts from loop
- Fields read: `tool_execution_allowed`, `tool_executed`, `execution_allowed`, `approval_required`
- Persists: no (trace is response-only)
- Exact equality required: no (booleans only)
- Future migration impact: LOW

### 14.4 aether/memory/timeline/recorder.py
- Consumes: risk_level (for importance), text (for description)
- Fields read: none from envelope directly
- Persists: yes (writes timeline event JSON)
- Exact equality required: N/A
- Future migration impact: NONE

### 14.5 aether/memory/working/store.py
- Consumes: text, perception metadata
- Fields read: none from envelope
- Persists: yes (in-memory deque)
- Exact equality required: N/A
- Future migration impact: NONE

### 14.6 aether/interface/api_server.py
- Consumes: envelope via loop response
- Fields read: response dict keys
- Persists: no
- Exact equality required: structural
- Future migration impact: LOW

## 15. Complete Compatibility Surface

| Surface | Rule 1 | Rule 2 | Classification |
|---|---|---|---|
| `/chat` response shape | exact | exact | EXACT VALUE |
| `decision_type` in response | "block" | "require_approval" | EXACT VALUE |
| `execution_allowed` | False | False | EXACT VALUE |
| `execution_decision` | "block" | "require_approval" | EXACT VALUE |
| `execution_reason` | blocked_reason | "Human approval..." | STRUCTURAL (reason differs) |
| `tool_execution_allowed` | False | False | EXACT VALUE |
| `approval_required` | True | True | EXACT VALUE |
| `approval_type` | "blocked_identity_review" | "human_review" | EXACT VALUE |
| `approval_status` | "pending" | "pending" | EXACT VALUE |
| `policy_snapshot` | dict(thinking_policy) | dict(thinking_policy) | EXACT VALUE |
| `loop_trace.safety` | exact | exact | EXACT VALUE |
| `timeline_event` | exact | exact | EXACT VALUE |
| `working_memory` | exact | exact | EXACT VALUE |
| `warnings` in envelope | [] | [] | EXACT VALUE |
| `warnings` in thinking_policy | 1-element | 1-element | INTENTIONALLY CHANGED INTERNAL SEMANTICS |

Key finding: The `reason` field in the Governance envelope differs between
Thinking-originated and Governance-originated evaluations for Rule 2:
- Thinking path: reason comes from `blocked_reason` in policy → "Identity integrity changed..."
- Governance block path: reason comes from `blocked_reason or "Policy blocked..."` → same
- Governance require_approval path: reason is always "Human approval is required before execution."
  (NOT the Thinking-specific reason)

This is an INTERNAL SEMANTIC CHANGE that affects the envelope's `reason` field.

### 15.1 Compatibility-Bridge Design

The future migration must preserve external and downstream compatibility while
eliminating Thinking as the authoritative evaluator of Rules 1 and 2. The
bridge design is:

1. `decide_chat_policy` produces a raw Thinking proposal without evaluating
   Rules 1 and 2.
2. `evaluate_authorization_envelope` evaluates Identity evidence authoritatively.
3. When Rule 1 or Rule 2 triggers, Governance produces a legacy-compatible
   effective policy snapshot matching the exact former Thinking-policy
   dictionary for that Identity state.
4. Core Coordination distinguishes:
   - `raw_thinking_policy` — output of `decide_chat_policy` (no Rules 1, 2)
   - `effective_thinking_policy` — compatibility projection matching legacy
   - `authorization_envelope` — final authoritative Governance decision
5. Existing downstream consumers receive the effective policy representation
   where exact compatibility requires it.

### 15.2 Compatibility Surface After Bridge

| Surface | Rule 1 (changed) | Rule 2 (missing/failed) | Classification |
|---|---|---|---|
| `/chat` response shape | exact | exact | EXACT VALUE |
| `decision_type` | "block" | "require_approval" | EXACT VALUE |
| `execution_allowed` | False | False | EXACT VALUE |
| `execution_decision` | "block" | "require_approval" | EXACT VALUE |
| `execution_reason` | blocked_reason | generic reason | STRUCTURAL |
| `tool_execution_allowed` | False | False | EXACT VALUE |
| `approval_required` | True | True | EXACT VALUE |
| `approval_type` | "blocked_identity_review" | "human_review" | EXACT VALUE |
| `approval_status` | "pending" | "pending" | EXACT VALUE |
| `policy_snapshot` | dict(effective_policy) | dict(effective_policy) | EXACT VALUE |
| `loop_trace.safety` | exact | exact | EXACT VALUE |
| `timeline_event` | exact | exact | EXACT VALUE |
| `working_memory` | exact | exact | EXACT VALUE |

### 15.3 Key Design Decisions

- `policy_snapshot` remains a shallow dictionary copy, but of the EFFECTIVE
  policy (not the raw Thinking proposal).
- The loop trace records the TRUTHFUL raw Thinking proposal in the Thinking
  stage and the authoritative Governance decision in the Governance/Policy-Gate
  stage (Strategy T3); it never records the Governance-derived effective policy
  as if Thinking had produced it.
- `build_approval_request` receives the effective policy to preserve exact
  approval_type and reason values.
- Governance warnings remain empty ([]); only the effective policy snapshot
  carries identity-specific information.
- Raw Identity Seed content, hashes, and evidence warnings NEVER enter
  reason, warnings, trace, approval records, or policy snapshots.

## 16. Internal Semantic Change Classification

The future migration is:

EXTERNALLY DECISION-, APPROVAL-, RESPONSE-SHAPE-, AND EXECUTION-FLAG
PRESERVING, WITH AN INTENTIONAL DIAGNOSTIC TRACE SEMANTIC CHANGE AND
INTERNAL PHYSICAL-OWNERSHIP CHANGE

### External Compatibility (preserved)
- `/chat` response shape: preserved
- `/chat` decision: preserved
- Approval requirement: preserved
- Execution flags: preserved
- Loop trace schema, stage names, stage ordering, and stage count: preserved
- Loop trace privacy guarantees: preserved
- Timeline behavior: preserved
- Working Memory behavior: preserved
- OpenAPI and API structure: preserved

### External Diagnostic Trace Semantic Change (intentional, limited)
- For Identity-triggered cases only, the Thinking-stage trace summary and the
  Thinking-stage warning count change from the effective (legacy Identity)
  policy to the truthful raw Thinking proposal (Strategy T3). This is an
  intentional diagnostic trace semantic change. It is NOT an external
  behavior-preserving change for that trace content.
- The Governance/Policy-Gate trace stage carries the authoritative Identity
  decision. The trace remains truthful about which organ proposed and which
  organ authorized.
- No trace schema, stage name, stage ordering, or stage-count change occurs.
- No trace privacy or leakage guarantee weakens.

### Internal Semantic Changes (intentional)
- Where Rules 1 and 2 are evaluated: Governance instead of Thinking
- Whether Identity evidence is operative: yes (for Rules 1, 2 only)
- Semantics of direct calls to `evaluate_authorization_envelope`: evidence now affects output for identity conditions
- Relationship between evidence-present and evidence-absent calls: NO LONGER EQUIVALENT for identity conditions
- Physical ownership of Rules 1 and 2: Governance instead of Thinking
- `reason` field in envelope for Rule 2: Governance uses generic reason, not Thinking-specific reason
- `policy_snapshot` content: may differ (Governance may synthesize proposal vs. copying Thinking's)

### 16.1 Exact Future Data Path

One exact future 89B data path is locked using three conceptual objects:

| Object | Producer | Future contents | Authority |
|---|---|---|---|
| `raw_thinking_policy` | `aether.thinking.policy.decide_chat_policy` | Rules 3, 4, 5, 6, 7, 8, 9 only (Rules 1 and 2 removed) | non-authoritative proposal |
| `authorization_envelope` | `aether.core.governance.evaluate_authorization_envelope` | validates the proposal per existing Governance precedence; evaluates Identity Rules 1 and 2 exactly once; preserves risk evidence as non-operative; produces the authoritative decision; produces the compatibility projection for Identity-triggered cases | authoritative decision |
| `effective_thinking_policy` | `aether.core.loop.run_core_chat_loop` (selected from `authorization_envelope["policy_snapshot"]`) | legacy-compatible projection for Identity-triggered cases; shallow copy of `raw_thinking_policy` for non-Identity-triggered cases | compatibility projection (formatting only) |

**Effective Thinking Policy source (default expected):**

```python
effective_thinking_policy = authorization_envelope["policy_snapshot"]
```

for all downstream consumers. For non-Identity-triggered cases,
`authorization_envelope["policy_snapshot"]` must remain the shallow copy of
`raw_thinking_policy`. For Identity-triggered cases,
`authorization_envelope["policy_snapshot"]` must be the legacy-compatible
projection produced by Governance. No new public envelope key is added:
repository evidence confirms Core Coordination can distinguish the raw
proposal from the effective projection using two local variables.

### 16.2 Future Trace Strategy (T3 — Truthful Raw Thinking Proposal Trace)

Selected strategy: **Strategy T3 — Truthful Raw Thinking Proposal Trace**.

Future computational order (unchanged):

Thinking -> Governance

Rejected strategy T1 (Deferred Thinking-Stage Recording) recorded the
Governance-derived effective policy under the Thinking stage, making the trace
appear as if Thinking selected the Identity hard-constraint result. T1 is
rejected because it misrepresents architectural authority.

Future trace semantics under T3:

**Thinking Stage**
- Source: `raw_thinking_policy`.
- Meaning: the actual non-authoritative proposal produced by Thinking after
  Rules 1 and 2 have been removed (Rules 3-9 only).
- It must not contain a Governance-generated Identity block or Identity
  approval projection.
- `summary=Decision: {raw_thinking_policy.get('decision_type', 'unknown')}`,
  `warnings_count=len(raw_thinking_policy.get("warnings", []))`.

**Governance / Policy-Gate Stage**
- Source: `authorization_envelope`.
- Meaning: the authoritative decision, including Identity Rule 1 or Rule 2
  when triggered.

**Effective Compatibility Policy**
- Source: `authorization_envelope["policy_snapshot"]`.
- Use: approval builder; response builder; returned legacy `thinking_policy`;
  returned legacy decision and confirmation fields; other downstream
  compatibility consumers where required.
- Must NOT be used to falsify the recorded raw Thinking stage.

Trace compatibility classification for Identity-triggered cases: INTENTIONAL
DIAGNOSTIC TRACE SEMANTIC CHANGE — the Thinking-stage summary and warnings
count differ from the legacy effective Identity policy. For non-Identity
cases the raw proposal equals the effective policy (shallow copy), so the
Thinking-stage trace content is unchanged. No duplicate stage is added. No
stage name, ordering, or stage-count change occurs. The Governance/Policy-Gate
stage always carries the authoritative Identity decision.

### 16.3 Response and Execution-Reason Source Fields

The response text is generated from the **effective thinking policy**:
`_build_response` reads `decision_type`, `blocked_reason`, and
`clarification_question` from the policy dict passed to it. After 89B that
dict is `effective_thinking_policy`.

The `execution_reason` in the `/chat` response and loop response is generated
from the **authorization envelope**: `execution_reason =
policy_gate_result.get("reason")`.

Explicit source fields:
- Response text: effective policy (via `_build_response` 4th argument).
- `execution_decision`: authorization envelope (`decision`).
- `execution_reason`: authorization envelope (`reason`).
- `decision_type`: effective policy (`decision_type`).
- `blocked_reason`: effective policy (`blocked_reason`); for Rule 2 it is
  `None`, and the externally observed reason is the envelope's generic reason.
- `required_user_confirmation`, `clarification_question`: effective policy.
- `policy_gate` in the response: the authorization envelope verbatim.

### 16.4 Approval Compatibility (exact source fields)

Because `build_approval_request` consumes both `policy_gate` (envelope) and
`thinking_policy` (effective policy after 89B):

- Rule 1 still yields `approval_type: "blocked_identity_review"`:
  - trigger source: envelope `decision == "block"` or effective
    `decision_type == "block"`;
  - reason source: effective `blocked_reason` (fallback: envelope reason);
  - summary source: effective `decision_type == "block"` →
    "Approval required before blocked action may proceed.";
- Rule 2 still yields `approval_type: "human_review"`:
  - trigger source: envelope `decision == "require_approval"`;
  - reason source: envelope generic reason
    "Human approval is required before execution." (currently externally
    observed);
  - effective policy `next_step` and `warnings` fields remain available where
    currently returned via `thinking_policy`.
- All other fields preserved: approval_required, approval_status, risk fields,
  decision_type, execution_decision, requested_action, summary,
  required_confirmations, safety_checks, expiry, metadata.
- Passing `effective_thinking_policy` is sufficient.
- `approval_request.py` requires NO modification.
- `approval_queue.py` requires NO modification.

## 17. Evidence Operativity and Supersession Analysis

### Current state (89A)
- `identity_integrity_evidence` parameter accepted but NOT used
- Evidence-present and evidence-absent calls return identical envelopes
- Rules 1 and 2 evaluated exclusively in Thinking

### Future state (89B, if authorized)
- `identity_integrity_evidence` becomes operative for Rules 1 and 2
- Evidence-present calls for identity conditions produce the same decision as Thinking
- Evidence-absent calls fall through to Thinking proposal evaluation
- Rules 1 and 2 physically evaluated in Governance
- Thinking stops evaluating Rules 1 and 2 (falls through to Rule 3)

### Direct-call compatibility matrix

| Identity evidence | Thinking policy | Governance behavior (future) | Equivalent to current? |
|---|---|---|---|
| `{"status": "changed"}` | any | block (from evidence) | YES (Rule 1 override) |
| `{"status": "missing"}` | any | require_approval (from evidence) | YES (Rule 2 override) |
| `{"status": "failed"}` | any | require_approval (from evidence) | YES (Rule 2 override) |
| `{"status": "verified"}` | block | block (from policy) | YES |
| `{"status": "verified"}` | require_approval | require_approval (from policy) | YES |
| `None` | block | block (from policy) | YES |
| `None` | any | evaluate policy normally | YES |
| malformed | any | fall through to policy | YES |

### Precedence decision (locked for 89B)
The migration evaluates Identity constraints with **evidence-first override**:
after a valid Thinking proposal exists, Governance evaluates safe Identity
evidence; if it triggers Rule 1 or 2, Governance returns directly without
further evaluating the Thinking proposal branch. This preserves current
precedence (Rules 1, 2 come first).

### 17.1 Future Governance Precedence

1. If `thinking_policy is None`, retain existing `invalid_policy` result.
2. If `thinking_policy` is not a dictionary, do not silently broaden the
   contract without authorization.
3. After a valid Thinking proposal exists, evaluate safe Identity evidence.
4. For a dictionary evidence object:
   - status `changed` activates Rule 1;
   - status `missing` or `failed` activates Rule 2;
   - any other status falls through to proposal evaluation.
5. Missing `status` key falls through.
6. `None` evidence falls through.
7. Non-dictionary Identity evidence must not raise a new exception; fall
   through safely.
8. When `status` conflicts with the `changed` boolean, the `status` field
   is authoritative (preserving current Thinking semantics).
9. Do not echo raw hashes, Identity Seed content, evidence warning payloads,
   or unexpected evidence fields into response reason, Governance warnings,
   trace, approval records, or policy snapshots.
10. Risk evidence remains non-operative.

### 17.2 Single-Authority and Single-Trigger-Evaluation Rule

After 89B:

- Thinking must not authoritatively evaluate Rules 1 or 2.
- Governance must be the sole authoritative evaluator.
- Trigger evaluation must occur exactly once, inside Governance.
- The compatibility snapshot must not become a second decision engine.
- A formatting or projection helper may reproduce legacy fields but must not
  independently decide whether a constraint triggers.
- Core Coordination (the loop) must not re-evaluate Identity status.
- The approval builder must not re-evaluate Identity status.
- Risk evidence must remain non-operative.
- Action must receive authorization rather than create it.

The future 89B test plan includes an AST and behavioral proof of single
trigger evaluation: static verification that
`evaluate_authorization_envelope` reads the evidence `status` field exactly
once, plus a behavioral test that Governance returning the identity decision
does not require or trigger any second status evaluation in the loop or the
approval builder.

### 17.3 Effective Policy Projection Is Formatting Only

The compatibility projection may format legacy fields only after Governance
has already selected Rule 1 or Rule 2. It must not independently determine
whether a constraint triggers. The projection selection receives an
already-authoritative internal result from Governance (the selected
decision_type and the relevant legacy output fields). It is a pure
formatter: it constructs the exact former Thinking-policy dictionary for the
already-selected Identity state.

### 17.4 Future Policy-Snapshot Contract

- For non-Identity cases: `policy_snapshot == shallow copy of
  raw_thinking_policy`.
- For Rule 1: `policy_snapshot == exact former Rule 1 Thinking-policy
  dictionary` (see "## 9. Current Rule 1 Contract").
- For Rule 2 missing: `policy_snapshot == exact former Rule 2
  missing-policy dictionary` (see "## 10. Current Rule 2 Contract").
- For Rule 2 failed: `policy_snapshot == exact former Rule 2
  failed-policy dictionary` (see "## 10. Current Rule 2 Contract").
- The input raw policy and evidence dictionaries must remain unmodified.
- Nested mutable values must not be newly mutated (shallow-copy semantics
  remain the same as today).
- No evidence fields may be copied into `policy_snapshot`.
- No public envelope key is added.

This is an INTENTIONALLY CHANGED INTERNAL SEMANTIC: `policy_snapshot`
represents the EFFECTIVE compatibility policy after 89B, not the raw Thinking
proposal. Direct callers distinguish raw proposal from effective projection via
separate local variables in the loop (no new envelope key required).

## 18. Finalized-Test Impact Inventory

### 18.1 Milestone 87 exact test-impact table

| File | Class | Test name | Classification | Reason |
|---|---|---|---|---|
| test_milestone_87...py | TestGovernanceModuleExtraction | test_49_governance_function_signature_exact | UNCHANGED_CURRENT_CONTRACT | Signature unchanged; 89B reuses same params |
| test_milestone_87...py | TestGovernanceModuleExtraction | test_58_core_loop_passes_identity_evidence_directly | UNCHANGED_CURRENT_CONTRACT | Loop still passes identity_integrity_evidence |
| test_milestone_87...py | TestGovernanceModuleExtraction | test_60_direct_identity_evidence_operative_only_for_identity_rules | EXPLICIT_89B_SUPERSESSION_AMENDMENT_REQUIRED | After 89B, identity evidence becomes operative |
| test_milestone_87...py | TestGovernanceModuleExtraction | test_61_direct_evidence_absent_from_policy_snapshot | UNCHANGED_CURRENT_CONTRACT | Only checks risk_evidence; risk remains non-operative |
| test_milestone_87...py | TestGovernanceModuleExtraction | test_62_identity_evidence_raw_values_absent_from_reason_and_warnings | EXPLICIT_89B_SUPERSESSION_AMENDMENT_REQUIRED | After 89B, identity evidence may influence reason |
| test_milestone_87...py | TestGovernanceModuleExtraction | test_64_input_dictionaries_not_mutated | UNCHANGED_CURRENT_CONTRACT | Mutation prevention must still hold |

### 18.2 Milestone 88 exact test-impact table

| File | Class | Test name | Classification | Reason |
|---|---|---|---|---|
| test_milestone_88...py | TestDecisionRecordStructure | test_07_actual_current_rule_count_is_seven | EXPLICIT_89B_SUPERSESSION_AMENDMENT_REQUIRED | Active source lock: Thinking physically owns Rules 3 through 9 after 89B, so the source contains seven return branches rather than nine |
| test_milestone_88...py | TestDecisionRecordStructure | test_08_every_source_rule_inventoried_once | UNCHANGED_CURRENT_CONTRACT | Checks historical M88 record |
| test_milestone_88...py | TestDecisionRecordStructure | test_09_exact_source_order_preserved | UNCHANGED_CURRENT_CONTRACT | Checks historical M88 record |
| test_milestone_88...py | TestRuleInventoryAndOutputs | test_10_exact_trigger_conditions_from_ast | EXPLICIT_89B_SUPERSESSION_AMENDMENT_REQUIRED | Active AST return-location lock: must reflect the exact seven Rules 3-through-9 return locations in Thinking |
| test_milestone_88...py | TestRuleInventoryAndOutputs | test_11_exact_current_decision_outputs | EXPLICIT_89B_SUPERSESSION_AMENDMENT_REQUIRED | Asserts current Thinking behavior for all 9 rules |
| test_milestone_88...py | TestRuleInventoryAndOutputs | test_12_exact_confirmation_and_execution_fields | EXPLICIT_89B_SUPERSESSION_AMENDMENT_REQUIRED | Asserts current Thinking behavior for identity cases |
| test_milestone_88...py | TestOwnershipAndSeparation | test_27_no_evidence_activation_is_claimed | UNCHANGED_CURRENT_CONTRACT | Checks historical M88 record |
| test_milestone_88...py | TestOwnershipAndSeparation | test_28_risk_evidence_remains_non_operative | UNCHANGED_CURRENT_CONTRACT | Risk evidence remains non-operative |
| test_milestone_88...py | TestOwnershipAndSeparation | test_29_identity_evidence_operative_only_through_governance | EXPLICIT_89B_SUPERSESSION_AMENDMENT_REQUIRED | After 89B, identity evidence becomes operative |
| test_milestone_88...py | TestNoBehaviorChange | test_30_exact_new_classification_string | EXPLICIT_89B_SUPERSESSION_AMENDMENT_REQUIRED | Classification changed to the exact 89B classification string |
| test_milestone_88...py | TestNoProductionSourceChanges | test_45_only_authorized_production_modules_changed | EXPLICIT_89B_SUPERSESSION_AMENDMENT_REQUIRED | 89B is an explicitly authorized runtime migration: exactly the three production modules change |

Historical-purpose preservation: Milestone 88 remains historically valid as
the classification boundary that first inventoried all nine rules. Milestone
89B does not rewrite the historical classification. Tests 07 and 10 change
only because they inspect active production source; the historical rule
inventory remains protected by the finalized Milestone 88 architecture
record, unchanged M88 Tests 08 and 09, this decision record, and the active
Milestone 89 migration tests. Test 45 changes only from a tests-only
source-protection assertion to the exact authorized three-production-file
migration assertion.

### 18.3 Thinking-policy exact test-impact table

`tests/test_thinking_policy.py` contains six tests affected by 89B and two
tests that remain unchanged.

| File | Class | Test name | Classification | Reason |
|---|---|---|---|---|
| test_thinking_policy.py | TestIdentityChanged | test_block_on_identity_changed | EXPLICIT_89B_SUPERSESSION_AMENDMENT_REQUIRED | Thinking no longer evaluates Rule 1 |
| test_thinking_policy.py | TestIdentityChanged | test_block_even_with_tool_and_medium_risk | EXPLICIT_89B_SUPERSESSION_AMENDMENT_REQUIRED | Thinking no longer evaluates Rule 1 |
| test_thinking_policy.py | TestIdentityMissingOrFailed | test_require_approval_when_missing | EXPLICIT_89B_SUPERSESSION_AMENDMENT_REQUIRED | Thinking no longer evaluates Rule 2 |
| test_thinking_policy.py | TestIdentityMissingOrFailed | test_require_approval_when_failed | EXPLICIT_89B_SUPERSESSION_AMENDMENT_REQUIRED | Thinking no longer evaluates Rule 2 |
| test_thinking_policy.py | TestHardRules | test_tool_execution_always_false | PARTIAL_EXPLICIT_89B_SUPERSESSION_AMENDMENT_REQUIRED | 18 of 30 parametrized cases are Identity-triggered; 12 remain unchanged |
| test_thinking_policy.py | TestConfidenceLevels | test_identity_issues_have_high_confidence | EXPLICIT_89B_SUPERSESSION_AMENDMENT_REQUIRED | Identity cases no longer produce high-confidence from Thinking |

Affected Thinking tests: **6** (5 full amendments + 1 partial amendment).

### 18.4 test_tool_execution_always_false full-body audit

`TestHardRules::test_tool_execution_always_false` iterates:

- status in (`"verified"`, `"changed"`, `"missing"`, `"failed"`, `None`);
- risk_level in (`"low"`, `"medium"`, `"high"`);
- has_tool in (`True`, `False`).

That is 5 × 3 × 2 = 30 parametrized cases. Every case runs
`decide_chat_policy` and asserts the single invariant
`result["tool_execution_allowed"] is False`.

Case inventory:
- **Identity-related cases (18):** status `"changed"` (6 cases — Rule 1,
  decision_type `block`), status `"missing"` (6 cases — Rule 2,
  decision_type `require_approval`), status `"failed"` (6 cases — Rule 2,
  decision_type `require_approval`).
- **Non-Identity cases (12):** status `"verified"` (6 cases) and
  `identity_integrity_status=None` (6 cases). These fall through to Rules 3-9
  (e.g. low+tool → `suggest_tool`, high → `require_approval`, else
  `respond_only`), always with `tool_execution_allowed is False`.

Classification:
**PARTIAL_EXPLICIT_89B_SUPERSESSION_AMENDMENT_REQUIRED.**

Exact Identity-related cases that must change (18):
- all 6 `status == "changed"` cases;
- all 6 `status == "missing"` cases;
- all 6 `status == "failed"` cases.

Exact non-Identity cases that remain (12):
- all 6 `status == "verified"` cases;
- all 6 `identity_integrity_status is None` cases.

Replacement contract for every Identity-related case (exact, R3):
- retain `result["tool_execution_allowed"] is False` for ALL 30 parametrized
  cases (full-matrix execution invariant preserved);
- additionally prove raw-Thinking Identity insensitivity: for each fixed
  combination of perception, risk, suggested_tool, and metadata, the future
  raw Thinking result for `status == "changed"`, `status == "missing"`, and
  `status == "failed"` must EQUAL the raw Thinking result for the explicit
  neutral baseline `identity_integrity_status=None` using the same
  non-Identity inputs;
- the equality contract covers the FULL returned dictionary:
  `decision_type`, `confidence`, `reasons`,
  `required_user_confirmation`, `tool_suggestion_allowed`,
  `tool_execution_allowed`, `blocked_reason`, `clarification_question`,
  `next_step`, and `warnings`;
- a negative decision assertion alone (`decision_type != "block"`) is NOT
  sufficient; the equality contract is the only proof that Thinking no longer
  evaluates Identity Rules 1 or 2;
- the equality contract correctly permits `require_approval` when caused by
  Rule 5 (secret/risk terms) or Rule 6 (high/medium risk with tool) — such
  `require_approval` results are produced by the neutral baseline too and are
  NOT Identity Rule 2 decisions.

Neutral baseline selection: `identity_integrity_status=None` is the explicit
neutral baseline used consistently throughout the partial contract. It
matches the existing parametrization (`{"status": status} if status else
None`), represents the complete absence of an Identity condition, and equals
a Governance-side non-trigger under the future classification.

Why the whole test must not be deleted:
- it is the only test enforcing the hard invariant that
  `tool_execution_allowed is False` across the full risk × tool matrix;
- 12 of its 30 cases test non-Identity behavior that remains valid after 89B;
- after partial amendment it continues to enforce the invariant while proving
  Rules 1 and 2 were removed from Thinking.

### 18.4b Exact per-test supersession contract (R3)

For every affected Thinking test: exact current assertion, exact future
amendment, exact replacement assertion, and the exact Milestone 89 test that
locks the replacement behavior.

| Test | Exact current assertion | Exact future amendment | Exact replacement assertion | M89 lock test |
|---|---|---|---|---|
| TestIdentityChanged::test_block_on_identity_changed | `decision_type == "block"`, `required_user_confirmation is True`, `tool_execution_allowed is False`, `blocked_reason is not None`, `tool_suggestion_allowed is False` for status "changed" (low risk, no tool) | Thinking no longer evaluates Rule 1; identity input must not alter the raw result | raw result for "changed" equals raw result for `identity_integrity_status=None` (full dictionary, same perception/risk/tool); execution invariant retained | TestR3FinalLock::test_identity_insensitivity_full_dictionary_equality |
| TestIdentityChanged::test_block_even_with_tool_and_medium_risk | `decision_type == "block"` for status "changed" (medium risk, tool present) | Thinking no longer evaluates Rule 1 | raw result for "changed" equals raw result for the neutral baseline (medium risk + tool → Rule 6 `require_approval`), proving Rule 1 removed | TestR3FinalLock::test_rule5_rule6_approval_still_permitted |
| TestIdentityMissingOrFailed::test_require_approval_when_missing | `decision_type == "require_approval"`, `required_user_confirmation is True` for status "missing" (low risk, no tool) | Thinking no longer evaluates Rule 2 | raw result for "missing" equals raw result for the neutral baseline (low risk, no tool, no secrets → `respond_only` or `ask_clarification`), proving Rule 2 removed | TestR3FinalLock::test_identity_insensitivity_full_dictionary_equality |
| TestIdentityMissingOrFailed::test_require_approval_when_failed | `decision_type == "require_approval"` for status "failed" (low risk, no tool) | Thinking no longer evaluates Rule 2 | raw result for "failed" equals raw result for the neutral baseline, proving Rule 2 removed | TestR3FinalLock::test_identity_insensitivity_full_dictionary_equality |
| TestConfidenceLevels::test_identity_issues_have_high_confidence | `confidence == "high"` for statuses changed/missing/failed | Thinking no longer derives confidence from Identity status | raw confidence for changed/missing/failed equals raw confidence for the neutral baseline (same non-Identity inputs) | TestR3FinalLock::test_identity_insensitivity_full_dictionary_equality |
| TestHardRules::test_tool_execution_always_false (partial) | `tool_execution_allowed is False` for all 30 parametrized cases | 18 Identity cases additionally prove full-dictionary identity insensitivity vs neutral baseline; 12 non-Identity cases unchanged | keep `tool_execution_allowed is False` for all 30; for changed/missing/failed assert full-dictionary equality with `identity_integrity_status=None` (same perception/risk/tool) | TestR3FinalLock::test_identity_insensitivity_full_dictionary_equality + test_invariant_retained_all_30 |

### 18.5 Exact supersession amendment set (authoritative counts)

The exact counts below are identical in this record, in the Milestone 89
boundary tests, in PROGRESS.md, and in the external summaries:

- **Full amendments: 14 tests.**
  - Milestone 87 (2): test_60, test_62.
  - Milestone 88 (7): test_07, test_10, test_11, test_12, test_29, test_30,
    test_45.
  - Thinking (5): test_block_on_identity_changed,
    test_block_even_with_tool_and_medium_risk,
    test_require_approval_when_missing, test_require_approval_when_failed,
    test_identity_issues_have_high_confidence.
- **Partial amendments: 1 test.**
  - Thinking: test_tool_execution_always_false (18 of 30 parametrized cases;
    12 cases unchanged).
- **Affected Thinking tests total: 6** (5 full + 1 partial).
- **Tests touched across finalized suites: 15** (14 full + 1 partial).

Milestone 87 tests that remain VALID unchanged:
- test_49_governance_function_signature_exact
- test_58_core_loop_passes_identity_evidence_directly
- test_61_direct_evidence_absent_from_policy_snapshot
- test_64_input_dictionaries_not_mutated

Milestone 88 tests that remain VALID unchanged:
- test_08_every_source_rule_inventoried_once
- test_09_exact_source_order_preserved
- test_28_risk_evidence_remains_non_operative

Thinking-policy tests that remain VALID unchanged:
- TestHardRules::test_decision_has_all_fields
- TestConfidenceLevels::test_default_has_medium_confidence

### 18.6 Replacement-assertion inventory

| Test | Replacement assertion |
|---|---|
| M87 test_60 | Amend to state evidence is non-operative EXCEPT for identity constraints (Rules 1, 2) where it becomes operative |
| M87 test_62 | Amend to allow identity evidence to influence the `reason` field when Governance evaluates Rules 1 or 2 authoritatively |
| M88 test_11 | Amend to reflect Rules 1 and 2 are no longer evaluated by Thinking; exact outputs superseded by Milestone 89 assertions |
| M88 test_12 | Amend to reflect identity branches removed from Thinking; identity-specific assertions superseded by Milestone 89 assertions |
| M88 test_07 | Retain the exact active-source rule-branch count lock at seven return branches (Rules 3-9 only), reflecting that 89B physically removed Rules 1 and 2 from Thinking |
| M88 test_10 | Retain the exact active AST trigger/return-location lock for the seven Rules 3-through-9 return locations |
| M88 test_45 | Replace the tests-only no-production-change assertion with the exact authorized three-production-file change assertion (governance.py, loop.py, policy.py) |
| M88 test_29 | Amend to state identity evidence is non-operative EXCEPT for Rules 1 and 2 in the future migration |
| M88 test_30 | Update classification from "no behavior change" to the exact 89B classification string |
| Thinking test_block_on_identity_changed | Raw result for status "changed" must equal the neutral-baseline (`identity_integrity_status=None`) result for the same non-Identity inputs (full dictionary); superseded by Milestone 89 assertions |
| Thinking test_block_even_with_tool_and_medium_risk | Status "changed" no longer blocks in Thinking; raw result equal to neutral-baseline result (Rule 6 approval may occur) |
| Thinking test_require_approval_when_missing | Status "missing" no longer yields Identity require_approval from Thinking; raw result equal to neutral-baseline result |
| Thinking test_require_approval_when_failed | Status "failed" no longer yields Identity require_approval from Thinking; raw result equal to neutral-baseline result |
| Thinking test_identity_issues_have_high_confidence | Identity statuses no longer produce high confidence from Thinking; confidence equal to neutral-baseline confidence |
| Thinking test_tool_execution_always_false (partial) | 18 Identity cases: retain the always-false invariant AND assert full-dictionary equality with `identity_integrity_status=None` (same perception/risk/tool); 12 non-Identity cases unchanged |

### 18.7 Core-loop/chat/approval/trace test-impact audit (exact body proof, R3)

Full bodies of `tests/test_core_loop.py` (270 lines, 24 tests),
`tests/test_chat_api.py` (7089 lines), and
`tests/test_cognitive_loop_trace_hardening.py` (90 lines, 7 tests) were read
for this audit. No current test asserts Identity-triggered Thinking-stage
trace summary content, Identity-triggered Thinking-stage warning count,
exact full-trace equality, or exact stage sequence. Every relevant test is
classified below.

| File | Tests | Classification | Exact body evidence |
|---|---|---|---|
| test_core_loop.py | all 24 | UNCHANGED_CURRENT_CONTRACT | Contains zero `loop_trace` references; asserts required fields, execution flags, approval flow, and decision fields only — all preserved under T3 |
| test_chat_api.py | all | UNCHANGED_CURRENT_CONTRACT | Contains zero `loop_trace` references; high-risk tests (e.g. `Delete all private memory...`) assert `approval_required`, `approval_status`, `approval_request`, `approval_id`, `approval_record`, `thinking_policy["tool_execution_allowed"]` — all preserved by the effective policy / envelope; no Thinking-stage trace content asserted |
| test_cognitive_loop_trace_hardening.py | test_loop_trace_does_not_include_user_text | UNCHANGED_CURRENT_CONTRACT | Privacy-only; no stage content asserted |
| test_cognitive_loop_trace_hardening.py | test_loop_trace_does_not_include_normalized_text | UNCHANGED_CURRENT_CONTRACT | Privacy-only |
| test_cognitive_loop_trace_hardening.py | test_loop_trace_does_not_include_metadata_values | UNCHANGED_CURRENT_CONTRACT | Privacy-only |
| test_cognitive_loop_trace_hardening.py | test_loop_trace_does_not_include_session_id | UNCHANGED_CURRENT_CONTRACT | Privacy-only |
| test_cognitive_loop_trace_hardening.py | test_loop_trace_summaries_are_tightly_truncated | UNCHANGED_CURRENT_CONTRACT | Summary length <= 120; raw summaries are sanitized by `sanitize_summary` |
| test_cognitive_loop_trace_hardening.py | test_loop_trace_stage_count_matches_expected_minimum | UNCHANGED_CURRENT_CONTRACT | Asserts only `len(stages) >= 12`; T3 changes no stage count |
| test_cognitive_loop_trace_hardening.py | test_loop_trace_high_risk_summary_does_not_dump_approval_record | UNCHANGED_CURRENT_CONTRACT | Privacy-only; raw approval record must not appear in trace — holds under T3 |
| test_cognitive_loop_contract.py | trace_id presence tests | UNCHANGED_CURRENT_CONTRACT | Asserts only `loop_trace` is a dict and `trace_id` starts with `chat_`; shape-only |
| test_approval_request.py (all) | UNCHANGED_CURRENT_CONTRACT | Approval request shape preserved |
| test_approval_queue.py (all) | UNCHANGED_CURRENT_CONTRACT | Pending record shape preserved |
| test_policy_gate.py (all) | UNCHANGED_CURRENT_CONTRACT | Facade delegation preserved |
| test_identity_guard.py, test_identity_awaken.py, test_risk_expansion.py, test_protected_core_routes_boundary.py, test_full_suite_private_persistence_isolation.py (all) | UNCHANGED_CURRENT_CONTRACT | Outside the migration boundary |

Classification results: ZERO tests require EXPLICIT_89B_SUPERSESSION_AMENDMENT
or PARTIAL_EXPLICIT_89B_SUPERSESSION_AMENDMENT for trace/core-loop/chat
behavior. No trace test is added to the 89B amendment matrix. The R2 claim
that existing trace tests remain unchanged is confirmed with exact body
proof; under T3 the trace remains truthful without weakening any assertion
these tests make.

### 18.8 Decision-gate result: READY_WITH_EXPLICIT_SUPERSESSION_AMENDMENTS

The migration can proceed ONLY if a future 89B prompt explicitly authorizes
the amendments listed in "## 18.5". Final authorized 89B test-amendment
matrix (exact paths and names):

Milestone 87 (2):
1. `tests/test_milestone_87_core_governance_authorization_boundary.py::TestGovernanceModuleExtraction::test_60_direct_identity_evidence_operative_only_for_identity_rules`
2. `tests/test_milestone_87_core_governance_authorization_boundary.py::TestGovernanceModuleExtraction::test_62_identity_evidence_raw_values_absent_from_reason_and_warnings`

Milestone 88 (7):
3. `tests/test_milestone_88_cognitive_signal_arbitration_boundary.py::TestDecisionRecordStructure::test_07_actual_current_rule_count_is_seven`
4. `tests/test_milestone_88_cognitive_signal_arbitration_boundary.py::TestRuleInventoryAndOutputs::test_10_exact_trigger_conditions_from_ast`
5. `tests/test_milestone_88_cognitive_signal_arbitration_boundary.py::TestRuleInventoryAndOutputs::test_11_exact_current_decision_outputs`
6. `tests/test_milestone_88_cognitive_signal_arbitration_boundary.py::TestRuleInventoryAndOutputs::test_12_exact_confirmation_and_execution_fields`
7. `tests/test_milestone_88_cognitive_signal_arbitration_boundary.py::TestOwnershipAndSeparation::test_29_identity_evidence_operative_only_through_governance`
8. `tests/test_milestone_88_cognitive_signal_arbitration_boundary.py::TestNoBehaviorChange::test_30_exact_new_classification_string`
9. `tests/test_milestone_88_cognitive_signal_arbitration_boundary.py::TestNoProductionSourceChanges::test_45_only_authorized_production_modules_changed`

Thinking (full, 5):
10. `tests/test_thinking_policy.py::TestIdentityChanged::test_block_on_identity_changed`
11. `tests/test_thinking_policy.py::TestIdentityChanged::test_block_even_with_tool_and_medium_risk`
12. `tests/test_thinking_policy.py::TestIdentityMissingOrFailed::test_require_approval_when_missing`
13. `tests/test_thinking_policy.py::TestIdentityMissingOrFailed::test_require_approval_when_failed`
14. `tests/test_thinking_policy.py::TestConfidenceLevels::test_identity_issues_have_high_confidence`

Thinking (partial, 1):
15. `tests/test_thinking_policy.py::TestHardRules::test_tool_execution_always_false`
    (18 of 30 parametrized cases amended; 12 remain unchanged)

Total existing tests touched: 15 (14 full amendments + 1 partial amendment).

## 19. Future Migration Dependency Direction

Identity evidence (loop.py → Governance)
→ Identity hard-constraint migration (89B): REQUIRED

Rule precedence preservation:
→ Governance must evaluate identity constraints BEFORE policy evaluation: REQUIRED

Direct-call compatibility:
→ Evidence-first override semantics: REQUIRED

Test supersession:
→ Authorized amendment of M87 tests 60, 62; M88 tests 07, 10, 11, 12, 29,
  30, 45; and Thinking tests (5 full + 1 partial): REQUIRED

Single-authority and exact data path:
→ effective_thinking_policy routing from authorization envelope: REQUIRED

Trace strategy:
→ T3 truthful raw Thinking proposal trace (Thinking stage = raw policy;
  Governance stage = authorization envelope; effective policy never falsifies
  the Thinking stage): REQUIRED

Trace-test impact:
→ exact audit shows zero trace/core-loop/chat tests require amendment
  (all UNCHANGED_CURRENT_CONTRACT): REQUIRED

## 20. Future Milestone 89B File Matrix

The matrix is separated into production files, existing tests authorized for
amendment, the Milestone 89 test, and protected files.

### Production Files Expected to Change

- `aether/core/governance.py` — evaluate Identity constraint Rules 1 and 2
  exactly once; preserve risk evidence as non-operative; produce the
  authoritative decision; produce the legacy-compatible projection in
  `policy_snapshot` for Identity-triggered cases.
- `aether/thinking/policy.py` — remove Rules 1 and 2 (fall through to Rule 3);
  retain the raw proposal with Rules 3-9 only.
- `aether/core/loop.py` — pass `raw_thinking_policy` to Governance; derive
  `effective_thinking_policy = authorization_envelope["policy_snapshot"]`;
  pass `effective_thinking_policy` to the approval-request builder, response
  builder, and returned policy/decision fields; apply trace strategy T3
  (Thinking stage recorded from `raw_thinking_policy`; Governance/Policy-Gate
  stage recorded from `authorization_envelope`; effective policy never used
  to falsify the raw Thinking stage).

### Exact Core-Loop Consumer Mapping (future 89B)

| Core-loop use | Current object | Future object (T3) | Compatibility requirement | Production change required? |
|---|---|---|---|---|
| Thinking-stage trace summary | thinking_policy | raw_thinking_policy | stage name/order preserved; summary from raw proposal; intentional diagnostic change for Identity-triggered cases | yes (loop.py, T3) |
| Thinking-stage warnings count | thinking_policy | raw_thinking_policy | count from raw warnings; intentional diagnostic change when raw differs from former Identity policy | yes (loop.py, T3) |
| Governance call | thinking_policy | raw_thinking_policy | evidence-first override evaluated once in Governance | yes (loop.py) |
| approval-request builder | thinking_policy + policy_gate_result | effective_thinking_policy + authorization_envelope | approval_type/reason preserved | yes (loop.py) |
| response builder | thinking_policy | effective_thinking_policy | response text from effective policy | yes (loop.py) |
| returned `thinking_policy` | thinking_policy | effective_thinking_policy | response key value preserved | yes (loop.py) |
| returned `decision_type` | thinking_policy | effective_thinking_policy | value preserved | yes (loop.py) |
| returned `required_user_confirmation` | thinking_policy | effective_thinking_policy | value preserved | yes (loop.py) |
| returned `clarification_question` | thinking_policy | effective_thinking_policy | value preserved | yes (loop.py) |
| returned `blocked_reason` | thinking_policy | effective_thinking_policy | value preserved | yes (loop.py) |
| Governance/Policy-Gate trace stage | policy_gate_result | authorization_envelope | authoritative Identity decision in the correct stage | yes (loop.py, T3) |
| loop-trace construction | thinking_policy + policy_gate_result | raw_thinking_policy + authorization_envelope | Thinking stage truthful raw; Governance stage envelope; safety flags preserved (T3) | yes (loop.py) |
| API response model | result dict | result dict (effective fields) | `/chat` shape preserved | no (api_server/api_models unchanged) |
| Timeline event | risk facts only | risk facts only (envelope NOT consumed) | importance/event_type unchanged | no |
| Working Memory event | perception metadata only | perception metadata only (envelope NOT consumed) | unchanged | no |

### Existing Tests Explicitly Authorized for Future Amendment

- `tests/test_milestone_87_core_governance_authorization_boundary.py`:
  - TestGovernanceModuleExtraction::test_60_direct_identity_evidence_operative_only_for_identity_rules
  - TestGovernanceModuleExtraction::test_62_identity_evidence_raw_values_absent_from_reason_and_warnings
    (test_61 remains valid — only checks risk_evidence)
- `tests/test_milestone_88_cognitive_signal_arbitration_boundary.py`:
  - TestDecisionRecordStructure::test_07_actual_current_rule_count_is_seven
  - TestRuleInventoryAndOutputs::test_10_exact_trigger_conditions_from_ast
  - TestRuleInventoryAndOutputs::test_11_exact_current_decision_outputs
  - TestRuleInventoryAndOutputs::test_12_exact_confirmation_and_execution_fields
  - TestOwnershipAndSeparation::test_29_identity_evidence_operative_only_through_governance
  - TestNoBehaviorChange::test_30_exact_new_classification_string
  - TestNoProductionSourceChanges::test_45_only_authorized_production_modules_changed
- `tests/test_thinking_policy.py`:
  - TestIdentityChanged::test_block_on_identity_changed
  - TestIdentityChanged::test_block_even_with_tool_and_medium_risk
  - TestIdentityMissingOrFailed::test_require_approval_when_missing
  - TestIdentityMissingOrFailed::test_require_approval_when_failed
  - TestConfidenceLevels::test_identity_issues_have_high_confidence
  - TestHardRules::test_tool_execution_always_false (partial — 18 of 30
    parametrized cases; 12 non-Identity cases remain unchanged)

### Milestone 89 Test

- `tests/test_milestone_89_identity_hard_constraint_migration_boundary.py` —
  add migration verification tests locking the exact data path, T3 trace
  strategy, single-trigger AST/behavioral proof, policy-snapshot contract,
  Identity-insensitivity contract, exact trace-test impact inventory,
  separated matrices, and post-migration contract.

### Final trace/core-loop/chat amendment set

- NONE. The exact audit (Section 18.7) proves every current
  trace/core-loop/chat test is UNCHANGED_CURRENT_CONTRACT. No trace test is
  authorized for amendment in 89B.

### Protected Files

- `aether/action/policy_gate.py` — no change (facade unchanged)
- `aether/action/approval_request.py` — no change (consumes effective policy)
- `aether/action/approval_queue.py` — no change
- `aether/core/loop_trace.py` — no change (trace shape preserved)
- `aether/memory/timeline/recorder.py` — no change
- `aether/memory/working/store.py` — no change
- `aether/identity/guard.py` — no change
- All other `aether/*` files
- `docs/CONSTITUTION.md`, `docs/ARCHITECTURE.md`, `README.md`
- `docs/architecture/MILESTONE_87_CORE_GOVERNANCE_AUTHORIZATION_BOUNDARY.md`
- `docs/architecture/MILESTONE_88_COGNITIVE_SIGNAL_ARBITRATION_BOUNDARY.md`
- All finalized M87 and M88 tests (amended only via authorized supersession)

## 21. Failure and Malformed-Evidence Rules

### Current behavior (evidence non-operative):
- `None` evidence → fall through to Thinking proposal evaluation
- Malformed evidence → ignored (parameter accepted but not read)
- Missing `status` key → `.get("status", "")` returns `""` → no rule triggered

### Future behavior (89B, if authorized):
- `None` evidence → fall through to Thinking proposal evaluation (same as current)
- `{"status": "changed"}` → Rule 1: block
- `{"status": "missing"}` → Rule 2: require_approval
- `{"status": "failed"}` → Rule 2: require_approval
- `{"status": "verified"}` → no rule triggered, fall through
- `{"status": "unknown"}` → no rule triggered, fall through
- Missing `status` key → `""` → no rule triggered, fall through
- Malformed (non-dict) → catch exception, fall through to Thinking proposal
- Conflicting `status` and `changed` fields → use `status` (consistent with current Thinking)

### Single-authority and single-trigger lock:
- Trigger evaluation occurs exactly once, in Governance.
- Core Coordination must not re-evaluate Identity status.
- The approval builder must not re-evaluate Identity status.
- The compatibility projection is formatting only; it receives an
  already-authoritative internal result and never independently decides
  whether a constraint triggers.

### Privacy requirements:
- No raw Identity Seed content may enter Governance
- Only the safe summary (truncated hashes, status string) may be used
- No hash exposure beyond current `_safe_summary` output
- No evidence fields are copied into `policy_snapshot`
- No new public envelope key is added

### Trace truthfulness (Strategy T3):
- The Thinking trace stage records only the raw Thinking proposal; it must
  never contain a Governance-generated Identity block or Identity approval
  projection
- The Governance/Policy-Gate trace stage records the authoritative
  authorization envelope, including Identity Rule 1 or Rule 2 when triggered
- The effective compatibility policy is never used to falsify the recorded
  raw Thinking stage
- Raw Identity data (hashes, seed content, warnings) never enters the trace
  at any stage

### Mutation requirements:
- Evidence dictionaries must not be mutated by Governance
- `raw_thinking_policy` must not be mutated by Governance
- The effective projection must not be re-fed back into the input dictionaries
- Current behavior: evidence not mutated (not used)
- Future behavior: evidence must not be mutated (provenance-only input)

### Policy-snapshot semantics (future 89B):
- Non-Identity: shallow copy of `raw_thinking_policy`
- Rule 1: exact former Rule 1 Thinking-policy dictionary
- Rule 2 missing: exact former Rule 2 missing-policy dictionary
- Rule 2 failed: exact former Rule 2 failed-policy dictionary
- Nested mutable values are shallow-copied (unchanged from today)

## 22. Protected Files and Non-Goals

### Protected versus future-amendable (exact, R3)

During Milestone 89A-R3 (and all of 89A, 89A-R, 89A-R2):
- all Milestone 87 and 88 records and tests are PROTECTED and UNCHANGED;
- all production source is PROTECTED and UNCHANGED.

During a separately authorized Milestone 89B:
- only the exact tests listed in the final supersession matrix (Section 18.5
  and the 89B test-amendment matrix in Section 20) may be amended;
- finalized architecture records (Milestone 87 record, Milestone 88 record,
  Constitution, ARCHITECTURE.md) remain protected;
- every amendment must preserve its historical purpose or explicitly record
  supersession.

This record never uses an unqualified statement that Milestone 87 and 88
tests are both permanently protected and simultaneously authorized for
amendment: they are protected during 89A (all passes), and the exact named
tests become amendable ONLY under a separately authorized 89B prompt.

Protected and unchanged in Milestone 89A (including 89A-R, 89A-R2, and
89A-R3): all
`aether/*`, all existing tests other than the new Milestone 89 boundary test,
Constitution, Architecture, README, existing architecture records (including
Milestone 87 and 88 records), API models, routers, endpoints, queues, stores,
schemas, `docs/history`, dependency files, and runtime/private data.

Non-goals include:
- Migrating Rules 1 or 2 during 89A (including 89A-R and 89A-R2)
- Making Identity evidence operative during 89A (including 89A-R and 89A-R2)
- Changing any runtime behavior
- Adding persistence, APIs, routers, or execution paths
- Modifying any finalized Milestone 87 or 88 artifact
- Beginning Milestone 89B
- Closing Milestone 89
- Defining Milestone 90

## 23. Completion and Acceptance Criteria

Milestone 89A-R3 completes locally when:

1. This decision record exists with the exact H1 and exactly 24 top-level
   `##` sections, with no top-level Section 25.
2. All compatibility-bridge content remains present, integrated into sections
   15, 16, 17, 18, 20, and 21.
3. The Thinking-policy supersession matrix is internally consistent: 6
   affected tests (5 full amendments + 1 partial amendment), with
   `test_tool_execution_always_false` classified as
   PARTIAL_EXPLICIT_89B_SUPERSESSION_AMENDMENT_REQUIRED.
4. The exact future 89B data path is locked: `raw_thinking_policy` (producer
   `decide_chat_policy`) → `authorization_envelope` (producer
   `evaluate_authorization_envelope`) → `effective_thinking_policy` (source
   `authorization_envelope["policy_snapshot"]`).
5. The exact Core-loop consumer mapping is recorded.
6. Trace strategy T3 (Truthful Raw Thinking Proposal Trace) is selected;
   T1 is rejected; the Thinking trace stage uses the raw policy, the
   Governance/Policy-Gate stage uses the authoritative envelope, and the
   effective policy is never used to falsify the Thinking trace.
7. The intentional diagnostic trace semantic change classification is exact
   and the migration is never called externally behavior-preserving without
   the trace qualification.
8. The exact trace-test impact audit (Section 18.7) proves zero
   trace/core-loop/chat tests require amendment.
9. The partial Thinking amendment proves Identity insensitivity via
   full-dictionary equality with the explicit neutral baseline
   `identity_integrity_status=None`.
10. Single-authority and single-trigger evaluation are locked.
11. The policy-snapshot contract is exact.
12. The future production and test file matrices are separated; the
    protected-versus-future-amendable distinction is exact.
13. The exact combined suite (M89 + M88 + M87 + M86 + repair family) is
    executed and recorded: 322 before any R3 test-count change, adjusted only
    by the exact number of newly added Milestone 89 tests; 212 is never
    recorded as the Milestone 89 combined result.
14. The boundary-test suite passes with its exact test count.
15. All existing Milestone 87 tests pass unchanged (76 passed).
16. All existing Milestone 88 tests pass unchanged (50 passed).
17. All existing Governance/policy/core focused tests pass (592 passed).
18. All architecture and Observation tests pass (240 passed).
19. PROGRESS consistency tests pass (55 passed).
20. OpenAPI remains 304/108 and api_server remains 8/23/0.
21. Constitution SHA is unchanged.
22. `aether/*` production source is unchanged.
23. The finalized Milestone 87 and 88 records and tests are unchanged.
24. Drift is 0.
25. Full suite passes.

Reconciliation decision gate: READY_WITH_EXPLICIT_SUPERSESSION_AMENDMENTS is
retained because every condition holds: record has exactly 24 sections; the
actual combined suite includes Milestone 89 (322 + N); trace strategy is T3;
the trace-test impact audit is exact; the partial Thinking amendment proves
Identity insensitivity; the exact production file matrix is defined; the
exact existing-test amendment matrix is defined; single authority is
preserved; no Identity data leakage is introduced; and no production source
or finalized artifact changed during R3.

Human/project-manager review and acceptance is the next authorized action.

## 24. Milestone 89 Finalization and Closure Rule

Milestone 89A-R3 completes locally only when this record and its corrected
contract suite pass every focused, architecture, Observation, protected-core,
Constitution, OpenAPI, structural, isolation, drift, combined-suite (including
Milestone 89), and full-suite gate, after which PROGRESS.md may be updated
truthfully. It remains unfinalized and uncommitted.

Milestone 89 remains open after 89A-R3. Human/project-manager review is the
next authorized action. Only explicit acceptance may authorize Milestone
89B — Identity Hard-Constraint Runtime Extraction. Milestone 89 closes
only after its separately authorized extraction and finalization sequence.
Milestone 90 does not start automatically.

### 24.1 Milestone 89B Runtime Implementation

Milestone 89B executed the runtime extraction: Identity Rules 1 and 2 moved
from Thinking to Core Governance. T3 Truthful Raw Thinking Proposal Trace
implemented. External decision, approval, response shape, and execution flags
preserved.

Implementation commit: `6e5c7b8474314d21723a08c1655843548eb7d65e`
Implementation tag: `milestone-89B-identity-hard-constraint-governance-migration`
Implementation tag target: `6e5c7b8474314d21723a08c1655843548eb7d65e`
Implementation push: confirmed on origin/main

### 24.2 Milestone 89C Finalization and Process Deviation Record

Milestone 89C attempted the authorized two-commit finalization structure
(one implementation commit + one ledger commit). The implementation commit
and tag are valid. However, the actual pushed history contains one original
ledger commit followed by four post-finalization test-correction commits,
for a total of six commits after the pre-Milestone-89 baseline instead of
the originally planned two.

Original finalization ledger commit: `05141f7ffea028ea8e749313a1de1cb2f046b5db`
Post-finalization test-correction commits:
- `e025f5ede85aebefb2593be6ea850b1f808312ee` — Fix M89/M88 tests for post-finalization state detection
- `9220822d45bd9dd3a1dccf0b9f8ce6f539f0912c` — Fix _changed_paths for post-finalization state
- `e17df6200704fc8bb691c380e453efecbacfb2cc` — Fix _amended_test_sets to compare against implementation commit
- `c4371eb6a7db3d014e8b6aacf42bcdf0393be459` — Fix _amended_test_sets to compare implementation vs pre-implementation

The rebase attempts and resets that occurred during execution were aborted;
no pushed commit was rewritten. Current runtime semantics and all regression
gates remain valid.

### 24.3 Milestone 89C-R Record Correction

Milestone 89C-R transparently corrects the closure records to reflect the
actual immutable six-commit history. No history is rewritten. Runtime and
test files remain byte-identical.

Milestone 89: CLOSED
Milestone 90: not started