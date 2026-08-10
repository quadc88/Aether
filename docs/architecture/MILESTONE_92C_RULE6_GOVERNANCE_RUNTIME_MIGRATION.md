# Milestone 92C Rule 6 Governance Runtime Migration

## 1. Status and Scope

Milestone 92C migrates operative Rule 6 authorization from Thinking to Core
Governance while preserving the current external behavior and execution safety
boundary. Rule 4 remains physically evaluated in Thinking. This record is the
complete implementation contract for the migration and is immutable from the
92C implementation tag through final closure.

Milestone 92B is durably closed at
`680878aeb9dc97e476d82751810899d41bddbe8b`. Its implementation provenance is
the immutable tag `milestone-92B-rule6-governance-migration-boundary` at
`22d819b6bd3a305536c0beba57f670a5433fe21e`.

92C adds no real execution, apply, rollback, evidence collection, automatic
Observe, background runtime, Resource Governance runtime, Economic Agency, API
surface, persistence, router, model, or loop capability.

## 2. Ownership Target

Thinking proposes. Verification supplies evidence. Governance authorizes.
Action executes only within authorization.

The operative Rule 6 owner after this migration is
`aether/core/governance.py::evaluate_authorization_envelope`. Thinking no
longer contains an operative Rule 6 branch. Rule 3 and Rule 4 provenance
remain produced by Thinking and transported by Core Coordination.

## 3. Exact Governance Trigger

Rule 6 selects only when all conditions are true:

```text
rule_3_4_precedence == "clear"
AND risk_evidence is a dict
AND risk_evidence["risk_level"] == "medium"
AND requested_action is not None
```

The comparison is exact and case-sensitive. Empty dictionaries, dictionaries
without `tool_id`, empty `tool_id`, strings, lists, integers, and unsupported
objects are all non-None and therefore match the trigger when the other gates
match. No truthiness, recognized-tool, registry, or `tool_id` requirement is
added.

## 4. Trigger and Formatter Separation

`RULE6_TRIGGER_MATCHED` is independent from
`RULE6_COMPATIBILITY_FORMATTER_SUCCEEDED`.

The compatibility formatter calls `requested_action.get("tool_id", "")` to
preserve the current behavior. Dict actions format successfully. Non-dict,
non-None actions match the trigger and then raise `AttributeError` during
formatting. Formatter failure never changes the trigger result to false.

## 5. Malformed Action Contract

For clear provenance and exact medium risk:

| requested_action | trigger | formatter/result |
|---|---|---|
| `None` | false | existing non-Rule-6 fallback |
| `{}` | true | approval; empty tool ID |
| `{"foo": "bar"}` | true | approval; empty tool ID |
| `{"tool_id": ""}` | true | approval |
| `{"tool_id": "x"}` | true | approval |
| `""` | true | `AttributeError` |
| `"tool"` | true | `AttributeError` |
| `[]` | true | `AttributeError` |
| `123` | true | `AttributeError` |
| unsupported object | true | `AttributeError` |

The same malformed failure class is used for direct Governance invocation and
the end-to-end chat pipeline. This is the authorized pipeline-equivalence
contract for unsupported internal action shapes.

Non-dict or missing/unknown risk evidence does not match the dict/medium gate.
Thinking's existing `risk.get(...)` behavior for malformed direct Thinking
inputs remains unchanged.

## 6. Rule 4 Boundary and Precedence

Rule 4 remains in Thinking at the secret-term branch and returns
`rule_4`. There is no Governance Rule 4 evaluator and Rule 4 migration is not
part of 92C.

The effective order is:

```text
Identity Rule 1 / Rule 2
-> Rule 3
-> Rule 4
-> Rule 5
-> Rule 6
-> Rule 7
-> Rule 8
-> Rule 9
```

Identity Governance decisions return before normal proposal evaluation. Rule 3
and Rule 4 signals are not `clear`, so they block Rule 6. Rule 5 high-risk
selection occurs before Rule 6. Rule 6 occurs before the remaining proposal
fallback behavior and therefore outranks Rules 7-9 only when selected.

## 7. Governance Implementation Shape

The implementation uses one private helper in `governance.py`:
`_format_rule_6_compatibility_policy(requested_action)`.

`evaluate_authorization_envelope` calls the Rule 6 trigger after the existing
Governance Rule 5 branch and before generic proposal/fallback handling. No new
public Governance component or output field is introduced.

## 8. Compatibility Projection

The Rule 6 policy snapshot contains exactly:

```text
decision_type=require_approval
confidence=medium
reasons=["Medium-risk request with suggested tool '{tool_id}'. Requires human approval before tool use."]
required_user_confirmation=True
blocked_reason=None
clarification_question=None
next_step=Review suggested tool and confirm before proceeding.
```

The envelope contains `allowed=False`, `decision=require_approval`, generic
reason `Human approval is required before execution.`, false execution flags,
unchanged requested action, and the projection as `policy_snapshot`.

## 9. Thinking Deauthorization

The operative medium-risk Rule 6 branch is removed from
`_evaluate_chat_policy_with_precedence`. For a medium-risk non-None action
without Rule 3/4 conditions, Thinking falls through to the neutral
`respond_only` proposal with `clear` provenance. Governance then selects Rule
6 exactly once.

Rule 3, Rule 4, Rule 7, Rule 8, and Rule 9 remain otherwise unchanged.

## 10. T3 Trace Contract

- Thinking trace represents the raw neutral proposal.
- `rule_3_4_precedence` remains private transport.
- Governance/Policy-Gate trace represents the authoritative Rule 6 result.
- `policy_snapshot` is the effective compatibility projection.
- `authorization_envelope` is the final authority.
- No trace claims Thinking authoritatively selected Rule 6.

## 11. Consumer and Transport Contract

`run_core_chat_loop` remains byte-identical. It continues to transport raw
Thinking policy, requested action, risk evidence, and precedence provenance to
Governance, then consumes the envelope policy snapshot for approval, response,
and trace construction.

No API, router, model, persistence, or loop path changes are required.

## 12. Exact External Scenarios

- Medium plus normal dict: Thinking neutral; Governance approval.
- Medium plus empty dict: Governance approval.
- Medium plus missing `tool_id`: Governance approval with empty ID.
- Medium plus `None`: no Rule 6; existing fallback.
- High plus tool: Rule 5 wins.
- Low plus tool: Rule 7 remains `suggest_tool` and non-executing.
- Rule 3 plus medium: Rule 3 blocks Rule 6.
- Rule 4 plus medium: Rule 4 blocks Rule 6.
- Identity Rule 1 plus medium: Identity block wins.
- Identity Rule 2 plus medium: Identity approval wins.
- Unknown or missing risk: Rule 6 does not select.

## 13. Exact Existing Supersession Matrix

Only these eight semantic targets may change:

1. `tests/test_thinking_policy.py::TestMediumRiskWithTool::test_medium_risk_tool_requires_approval`
2. `tests/test_milestone_88_cognitive_signal_arbitration_boundary.py::TestDecisionRecordStructure::test_07_actual_current_rule_count_is_seven`
3. `tests/test_milestone_88_cognitive_signal_arbitration_boundary.py::TestDecisionRecordStructure::test_09_exact_source_order_preserved`
4. `tests/test_milestone_88_cognitive_signal_arbitration_boundary.py::TestRuleInventoryAndOutputs::test_10_exact_trigger_conditions_from_ast`
5. `tests/test_milestone_88_cognitive_signal_arbitration_boundary.py::TestRuleInventoryAndOutputs::test_11_exact_current_decision_outputs`
6. `tests/test_milestone_88_cognitive_signal_arbitration_boundary.py::TestRuleInventoryAndOutputs::test_12_exact_confirmation_and_execution_fields`
7. `tests/test_milestone_89_identity_hard_constraint_migration_boundary.py::TestRulePrecedence::test_23_current_source_order_preserved`
8. `tests/test_milestone_91b_rule5_governance_migration_boundary.py::test_25_scenario_field_exact_matrix[s08_medium_tool]`

The M91B source function may change, but only `s08_medium_tool` changes
semantically. All other parameter cases and Rule 5 cases remain equivalent.

## 14. New Migration Test Inventory

Exactly 24 non-parametrized tests are required in
`tests/test_milestone_92c_rule6_governance_runtime_migration.py`:

CURRENT_TO_TARGET_MIGRATION_LOCK:
1. `test_current_rule6_trigger_exact` — exact four trigger gates.
2. `test_current_rule6_projection_fields_exact` — all projection fields.
3. `test_current_rule6_empty_and_missing_tool_id_inputs` — dict edge cases.
4. `test_current_rule6_malformed_tool_behavior` — formatter failure boundary.

GOVERNANCE_RULE6_AUTHORITY:
5. `test_governance_rule6_single_authority` — only Governance selects.
6. `test_governance_rule6_exact_trigger_gate` — trigger truth table.
7. `test_governance_rule6_projection_matches_legacy` — compatibility equality.
8. `test_governance_rule6_malformed_action_raises_exactly` — direct/pipeline exception.
9. `test_governance_rule5_precedes_rule6` — Rule 5 precedence.

THINKING_RULE6_DEAUTHORIZATION:
10. `test_thinking_no_operative_rule6_branch` — no Thinking Rule 6 branch.
11. `test_thinking_medium_tool_returns_neutral_proposal` — raw neutrality.
12. `test_thinking_rule3_rule4_provenance_retained` — sidecar preservation.
13. `test_thinking_rules7_8_9_unchanged` — remaining rule behavior.

PRECEDENCE_EQUIVALENCE:
14. `test_identity_rules_precede_rule6` — identity wins.
15. `test_rule3_provenance_blocks_rule6` — Rule 3 blocks.
16. `test_rule4_provenance_blocks_rule6` — Rule 4 blocks.
17. `test_rule6_precedes_rule7` — Rule 6 outranks Rule 7.
18. `test_rule6_unknown_and_missing_risk_do_not_trigger` — risk gates.

COMPATIBILITY_PROJECTION:
19. `test_rule6_envelope_flags_are_non_executing` — false execution flags.
20. `test_rule6_approval_request_consumes_projection` — approval consumer.
21. `test_rule6_trace_separates_raw_and_authoritative_policy` — T3 trace.
22. `test_rule6_response_shape_and_openapi_unchanged` — public shape.

NON_CAPABILITY_LOCK:
23. `test_no_rule4_migration_or_duplicate_evaluator` — authority boundary.
24. `test_no_capability_expansion_or_loop_mutation` — no capability/loop drift.

Arithmetic: 4 + 5 + 4 + 5 + 4 + 2 = 24; parametrized tests: 0; full suite
target: 2547 + 24 = 2571.

## 15. Canonical Rename and Lifecycle

Rename `test_previous_closure_tag_is_92a` to
`test_previous_accepted_closure_tag_is_consistent` during this Build. The old
name is removed once and the truthful generic name is added once; collection
remains 23.

Implementation-stage canonical delta:
- Modified: three lifecycle functions.
- Removed name: `test_previous_closure_tag_is_92a`.
- Added name: `test_previous_accepted_closure_tag_is_consistent`.
- Current closure-tag body remains 92B.
- Count: 23.

At implementation Build, `PROGRESS.md` records a local 92C implementation
candidate, not durable 92C closure. Final closure changes the generic previous
closure assertion from 92A to 92B and updates current 92C closure provenance.

## 16. Migration Record and Lifecycle

The migration record is complete and final at Build time:
`docs/architecture/MILESTONE_92C_RULE6_GOVERNANCE_RUNTIME_MIGRATION.md`.

The implementation record is complete and requires no ordinary closure-stage
content mutation. It has no moving-HEAD requirement, self-referential future
commit SHA, or closure-dependent text. It must remain byte-identical from the
implementation tag through final closure.

Proposed implementation tag:
`milestone-92C-rule6-governance-runtime-migration`.

Every pushed stage must be green in a clean checkout. Stage 1 is the complete
implementation commit plus immutable tag. Stage 2 modifies only `PROGRESS.md`
and `tests/test_progress_ledger_canonical_header.py`. No migration record,
production file, new migration test, or existing supersession test changes at
closure.

## 17. Historical 92B Test Harness Correction

The 92B Boundary Test #6 originally compared the immutable 92B implementation
canonical test to the current worktree canonical test. Its historical purpose
is only to verify the 92B implementation-to-92B-final-closure delta. The 92C
Build corrects the harness to load the final closure canonical test from the
immutable 92B final closure commit
`680878aeb9dc97e476d82751810899d41bddbe8b`.

The historical Build expected delta remains exactly four; the historical Closure
expected delta remains exactly five, including the historical
`test_previous_closure_tag_is_92a` name. Future truthful canonical evolution
does not alter those historical comparisons. The 92B decision record remains
byte-identical.

## 18. Protected and Non-Capability Scope

The following remain always byte-identical throughout the 92C Build:

- `aether/core/loop.py`
- `docs/architecture/MILESTONE_92_RULE6_GOVERNANCE_MIGRATION_BOUNDARY.md`
- `README.md`
- `docs/CONSTITUTION.md`
- `docs/ARCHITECTURE.md`
- API/router/model/persistence paths

The 92B decision record is frozen and remains byte-identical. The 92B boundary
test is an explicitly authorized one-time historical harness correction during
this 92C Build. That correction only replaces the future-current-worktree
closure baseline with the immutable 92B final closure commit, preserves the
historical Build and Closure allowed sets, preserves the Test #6 function name,
preserves boundary count 48, and does not rewrite the 92B architecture decision
record.

After the future 92C implementation commit and tag, the corrected 92B boundary
test becomes frozen and must remain byte-identical through ordinary Stage-2
closure. The migration record, production files, 92C migration test, and four
existing supersession test files are also frozen after the implementation tag.

No Rule 4 migration, Candidate A-F implementation, real execution/apply,
rollback, evidence collection, automatic Observe, background runtime, Resource
Governance runtime, Economic Agency, API expansion, persistence expansion,
new endpoint, or loop change is authorized.

## 19. Exact Eleven-Path Build Scope

PRODUCTION (2):
1. `aether/thinking/policy.py`
2. `aether/core/governance.py`

MIGRATION RECORD (1):
3. `docs/architecture/MILESTONE_92C_RULE6_GOVERNANCE_RUNTIME_MIGRATION.md`

NEW MIGRATION TEST (1):
4. `tests/test_milestone_92c_rule6_governance_runtime_migration.py`

EXISTING SUPERSESSION TESTS (4):
5. `tests/test_thinking_policy.py`
6. `tests/test_milestone_88_cognitive_signal_arbitration_boundary.py`
7. `tests/test_milestone_89_identity_hard_constraint_migration_boundary.py`
8. `tests/test_milestone_91b_rule5_governance_migration_boundary.py`

HISTORICAL 92B TEST HARNESS CORRECTION (1):
9. `tests/test_milestone_92_rule6_governance_migration_boundary.py`

LEDGER (1):
10. `PROGRESS.md`

CANONICAL (1):
11. `tests/test_progress_ledger_canonical_header.py`

Total unique Build paths: 11.

The 92B boundary test is not byte-identical throughout this Build; it is the
single authorized historical harness correction described in Section 17. It is
frozen after the 92C implementation tag. No twelfth path exists.

## 20. Build Completion Gates

- Governance is the single operative Rule 6 authority.
- Thinking Rule 6 authority is removed.
- Rule 4 remains in Thinking and is not migrated.
- Exact trigger and formatter distinction pass.
- Rule 5, Rules 3/4/7/8/9, and T3 pass.
- `loop.py` remains byte-identical.
- Exact eight supersessions only; M91B semantic change is s08 only.
- Exact 24 new tests collect/pass.
- Canonical count remains 23.
- 92B Boundary 48, Progress 322, Architecture/Observation 363 pass.
- Full suite is 2571 with 9 existing / 0 new warnings.
- OpenAPI remains 304 / 108; api_server remains 8 / 23 / 0.
- Protected hashes remain unchanged.
- Exact eleven-path dirty/build scope; nothing staged; no commit/tag/push.

Build scope coherence requires the exact eleven-path matrix in Section 19,
including the one authorized 92B historical boundary-harness correction.
Stage 2 closure remains limited to `PROGRESS.md` and
`tests/test_progress_ledger_canonical_header.py` only.

## 21. Required Footer

Milestone 92C Build complete: yes
Outcome: PASS
Repository modified: yes, exactly eleven authorized paths
HEAD: 680878aeb9dc97e476d82751810899d41bddbe8b
origin/main: 680878aeb9dc97e476d82751810899d41bddbe8b
Rule 6 operative authority: Core Governance
Thinking Rule 6 operative branch: absent
Governance Rule 6 helper: `_format_rule_6_compatibility_policy`, called by the envelope
Governance Rule 6 trigger: clear + dict risk evidence + exact medium + non-None action
Malformed non-dict action: trigger true, formatter AttributeError
Rule 4 physical evaluator: Thinking
Governance Rule 4 evaluator: none
Rule 5 precedence: PASS
Rules 3/7/8/9: PASS
Raw Thinking medium-tool result: respond_only / clear
Effective medium-tool result: require_approval
T3 trace: PASS
loop.py preserved: yes
Migration record: docs/architecture/MILESTONE_92C_RULE6_GOVERNANCE_RUNTIME_MIGRATION.md
Migration record immutable-ready: yes
92C proposed implementation tag: milestone-92C-rule6-governance-runtime-migration
Exact supersession nodes: 8/8
M91B semantic supersession: s08_medium_tool only
92B decision record: byte-identical and frozen throughout 92C
92B boundary test: one authorized historical harness correction; frozen after implementation tag
New migration tests: 24/24
Parametrized: 0
Canonical old function removed: yes
Canonical stable function added: yes
Canonical collected: 23/23
92B Boundary: 48/48
Progress: 322/322
Architecture/Observation: 363/363
Full: 2571/2571
Warnings: 9 existing / 0 new
OpenAPI: 304 / 108
api_server: 8 / 23 / 0
Protected hashes unchanged: yes
Exact eleven-path dirty/build scope: yes
Dirty paths: 11/11
Staged: none
Commit: none
Tag: none
Push: none
Production/runtime capability expansion: none
Rule 4 migration: not started
Candidate A-F: deferred
Milestone 92C durably finalized: no
Next authorized action if PASS: human/project-manager review before any implementation commit or tag

MILESTONE_92C_RULE6_GOVERNANCE_RUNTIME_MIGRATION_BUILD_COMPLETE
Outcome: PASS
Rule 6 owner: Core Governance
Thinking Rule 6: REMOVED
Governance Rule 6: PASS
Malformed contract: PASS
Rule 4: Thinking
Rule 5 precedence: PASS
loop.py: PRESERVED
Supersessions: 8/8
s08 lock: PASS
New tests: 24/24
Canonical: 23/23
92B Boundary: 48/48
Progress: 322/322
Architecture/Observation: 363/363
Full: 2571/2571
OpenAPI: 304 / 108
api_server: 8 / 23 / 0
Dirty paths: 11/11
Commit: none
Tag: none
Push: none
92C durably finalized: no
Next authorized action: human/project-manager review
Do not commit. Do not tag. Do not push. Do not begin closure.
