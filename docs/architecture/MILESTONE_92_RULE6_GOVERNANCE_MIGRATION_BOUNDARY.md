# Milestone 92 Rule 6 Medium-Risk Tool Governance Migration Boundary

## 1. Status and Scope

Milestone 92B is a boundary-only local Build. It reconciles the truthful
current ledger, records the future Rule 6 Governance migration contract, and
adds static/pure boundary tests. It does not migrate runtime ownership.

92A is externally PM CLOSED. 92B is complete locally and awaits independent
audit. It is not finalized, committed, tagged, or pushed. Functional
Milestone 92 has started through this boundary milestone only. Rule 6 runtime
migration has not started. Future 92C is separately gated and unauthorized.

Actual repository Build paths are exactly four: `PROGRESS.md`, this decision
record, the new 48-test boundary file, and the canonical ledger test file.
The three core boundary artifacts are the ledger, this record, and the new
boundary test. The fourth path is the narrow canonical lifecycle supersession.

## 2. Purpose and Classification

Rule 6 is classified as an Operational Hard Constraint. Its future
architectural authority is Core Governance. Thinking remains the current
physical evaluator until a separately authorized 92C migration.

This record is documentation and contract tests only. No new classifier,
public API field, persistence model, executor, evidence collector, apply path,
rollback path, Observe integration, or background runtime is introduced.

## 3. Current Architectural Authority

The current physical evaluator is
`aether/thinking/policy.py::_evaluate_chat_policy_with_precedence`.
The existing Governance authority is
`aether/core/governance.py::evaluate_authorization_envelope`.

Thinking proposes. Verification supplies evidence. Governance authorizes.
Action executes only within authorization. The current Rule 6 proposal is
transported through Core Coordination to the Governance envelope, but 92B
does not add an operative Governance Rule 6 branch.

## 4. Current Rule 6 Trigger and Output

The exact current trigger is:

```text
risk_level == "medium" and suggested_tool is not None
```

The comparison is case-sensitive. `suggested_tool is None` does not trigger.
An empty dictionary is non-None and triggers. A dictionary without `tool_id`
is non-None and triggers; its current reason formatting reads the missing ID as
an empty string. An unsupported non-dictionary malformed shape currently fails
through `.get(...)` when the branch formats the reason. No semantic repair or
broader malformed-value handling is authorized.

The current output from source is a ten-key policy dictionary:

```text
decision_type=require_approval
confidence=medium
reasons=["Medium-risk request with suggested tool '{tool_id}'. Requires human approval before tool use."]
required_user_confirmation=True
tool_suggestion_allowed=True
tool_execution_allowed=False
blocked_reason=None
clarification_question=None
next_step=Review suggested tool and confirm before proceeding.
warnings=["Medium-risk tool usage requires human confirmation."]
```

The current sidecar provenance for Rule 6 is `clear`.

## 5. Current Ownership Split

Thinking physically evaluates Rules 3, 4, 6, 7, 8, and 9 in the current
helper, with Rule 5 already represented by the existing Governance contract.
Core Governance is the architectural authority for operative authorization.
Core Coordination transports the raw proposal, risk evidence, requested action,
and provenance signal. Compatibility consumers receive the current effective
policy snapshot.

92B changes no production ownership. Future 92C must establish one
authoritative Rule 6 evaluator in Governance and make any compatibility
projection formatting-only.

## 6. Rule 4 Incremental-Migration Boundary

Rule 4 remains physically evaluated in Thinking and remains separately pending.
The Rule 4 provenance signal blocks downstream Rule 5 and future Rule 6
Governance activation. Future Rule 6 requires exact `clear` provenance.

Moving Rule 6 first does not imply that Rule 4 ownership is architecturally
reconciled. 92B changes no Rule 4 semantics. Future 92C may not change Rule 4
semantics without separate authorization. Rule 4 blocker classification is
A — `RULE_4_DOES_NOT_BLOCK_RULE_6`.

## 7. Current Effective Precedence

The current effective cross-layer precedence is:

```text
invalid policy
-> Identity Rule 1
-> Identity Rule 2
-> Rule 3
-> Rule 4
-> Governance Rule 5
-> Thinking Rule 6 proposal
-> Rule 7
-> Rule 8
-> Rule 9
```

The current Rule 6 proposal cannot override Rule 3 or Rule 4. Rule 7 is a
soft signal and does not authorize execution.

## 8. Future Target Precedence

The future target order is:

```text
invalid policy
-> Identity Rule 1
-> Identity Rule 2
-> Rule 3
-> Rule 4
-> Governance Rule 5
-> Governance Rule 6
-> Rule 7
-> Rule 8
-> Rule 9
```

Governance Rule 5 high-risk selection precedes Governance Rule 6 medium-risk
selection. Rule 6 cannot override Rule 3 or Rule 4. Rule 7 remains soft.

## 9. Risk Evidence and Requested-Action Transport

Current `aether.verification.risk.classify_risk` produces the existing risk
dictionary. `aether/core/loop.py` transports it as `risk_evidence`, transports
the suggested tool as `requested_action`, and transports the Thinking
provenance as `rule_3_4_precedence`. The current transport is compatible input
boundary only for Rule 6; 92B adds no operative consumer.

The future Governance condition is exactly:

```text
rule_3_4_precedence == "clear"
AND risk_evidence is a dict
AND risk_evidence["risk_level"] == "medium"
AND non-None requested_action
```

`non-None requested_action` must not be narrowed to a valid tool, a truthy
dictionary, a present `tool_id`, or a recognized tool. Raw evidence and
provenance values must not leak into public outputs or persistence.

## 10. Target Governance Rule 6 Evaluator

Future 92C only: Core Governance is the sole authoritative Rule 6 evaluator.
It evaluates the exact condition in Section 9 once, after the exact
precedence/provenance gates. It selects the authoritative decision and then
may produce the compatibility policy snapshot.

The projection may reproduce legacy fields only after Governance selects Rule
6. The projection is formatting-only and is not a second trigger evaluator.
Thinking must become a non-authoritative raw proposal producer in 92C. No such
runtime change is implemented by 92B.

## 11. Single-Authority and Single-Trigger Invariant

Future 92C must have one Rule 6 trigger evaluator, one authoritative owner,
and no duplicate evaluation in Thinking, Core Coordination, the approval
builder, the Action facade, or compatibility formatting. Core Coordination
must transport rather than re-evaluate. The approval builder must consume the
selected result rather than create authorization.

The 92B tests validate this as a decision-record contract and current
compatible-interface constraint. They do not require the future runtime branch.

## 12. Raw Thinking Proposal Contract

Future Thinking output is the actual raw Thinking proposal. For Rule 6 it is
not the authoritative authorization result. The raw proposal may contain the
current medium-risk approval proposal before 92C, but future 92C must not
claim that Thinking authorizes Rule 6 after Governance owns it.

The raw proposal, risk dictionary, requested action, and provenance must remain
unmodified by transport. 92B does not change current output.

## 13. Effective Compatibility Projection

Future Governance may project the selected Rule 6 result into the existing
effective policy fields consumed by response and approval compatibility code.
The projection preserves the existing effective fields, including
`decision_type`, confirmation, `blocked_reason`, `next_step`, warnings, and
false execution flags where applicable.

No new public envelope key, response field, schema, API model, or persistence
state is authorized. The effective projection must be a formatter only.

## 14. T3 Truthful Trace Contract

Future 92C uses Strategy T3:

- Thinking trace: actual raw Thinking proposal;
- Governance/Policy-Gate trace: authoritative Governance result;
- effective compatibility policy: `authorization_envelope["policy_snapshot"]`.

Future Governance approval must not be written back into the raw Thinking
trace. The trace schema, stage names, ordering, and count remain unchanged.
92B locks this future contract only and does not implement the change.

## 15. External Behavior Equivalence

Future Rule 6 migration must preserve externally:

- `decision_type=require_approval`;
- `required_user_confirmation=true`;
- `approval_required=true`;
- `approval_type=human_review`;
- `approval_status=pending`;
- existing approval reason semantics;
- risk level and action type;
- `execution_decision` and `execution_reason`;
- returned effective `thinking_policy`;
- `tool_execution_allowed=false`;
- `execution_allowed=false`;
- `tool_executed=false`;
- response shape;
- OpenAPI;
- `loop_trace` schema, stage ordering, and count;
- timeline behavior;
- approval persistence behavior.

No new public field or persistent state is authorized. This compatibility
contract does not authorize execution.

## 16. Rule 7 Protection

Rule 7 remains a Thinking soft signal for low risk with a suggested tool. It
may select `suggest_tool` within the hard-constraint boundary, but it does not
authorize execution and remains false for execution flags. Future Rule 6
Governance ownership must not promote Rule 7 or let it override Rule 6.

## 17. Rules 3, 8, and 9 Protection

Rule 3 remains the empty-input workflow rule. Rule 8 remains the short-input
without-tool clarification rule. Rule 9 remains the default textual response
rule. They remain Thinking workflow/default rules and do not become Governance
authorization rules through 92B or the future Rule 6 migration.

## 18. Current Consumer Map

Current consumers and transport are:

| Surface | Current relationship | Future 92C contract |
|---|---|---|
| `aether/thinking/policy.py` | produces current Rule 6 proposal and `clear` signal | raw non-authoritative proposal |
| `aether/core/loop.py` | transports risk, action, signal, envelope, effective snapshot | no duplicate evaluator |
| `aether/core/governance.py` | current envelope authority; no Rule 6 branch | sole Rule 6 evaluator |
| `aether/action/policy_gate.py` | compatibility facade | no Rule 6 evaluation |
| approval builder/queue | consumes pending authorization | no Rule 6 re-evaluation |
| response and loop trace | consume effective/envelope surfaces | T3 truthful separation |

## 19. Future 92C Supersession Matrix

Exactly eight existing test-function surfaces are future 92C inputs only. 92B
does not edit them:

1. `tests/test_thinking_policy.py::TestMediumRiskWithTool::test_medium_risk_tool_requires_approval`
2. `tests/test_milestone_88_cognitive_signal_arbitration_boundary.py::TestDecisionRecordStructure::test_07_actual_current_rule_count_is_seven`
3. `tests/test_milestone_88_cognitive_signal_arbitration_boundary.py::TestDecisionRecordStructure::test_09_exact_source_order_preserved`
4. `tests/test_milestone_88_cognitive_signal_arbitration_boundary.py::TestRuleInventoryAndOutputs::test_10_exact_trigger_conditions_from_ast`
5. `tests/test_milestone_88_cognitive_signal_arbitration_boundary.py::TestRuleInventoryAndOutputs::test_11_exact_current_decision_outputs`
6. `tests/test_milestone_88_cognitive_signal_arbitration_boundary.py::TestRuleInventoryAndOutputs::test_12_exact_confirmation_and_execution_fields`
7. `tests/test_milestone_89_identity_hard_constraint_migration_boundary.py::TestRulePrecedence::test_23_current_source_order_preserved`
8. `tests/test_milestone_91b_rule5_governance_migration_boundary.py::test_25_scenario_field_exact_matrix[s08_medium_tool]`

Future affected functions: 8. Future affected collected cases: 8. M91B is
1/45 future affected and 44/45 protected. Thinking policy is 1/19 future
affected and 18/19 protected.

## 20. Future 92C Runtime Production Matrix

Future candidates only:

- `aether/thinking/policy.py`;
- `aether/core/governance.py`.

Expected unchanged unless future re-verification proves necessity:

- `aether/core/loop.py`;
- `aether/action/policy_gate.py`;
- `aether/action/approval_request.py`;
- `aether/action/approval_queue.py`;
- `aether/verification/risk.py`;
- `aether/core/loop_trace.py`;
- `aether/interface/api_server.py`;
- `aether/interface/api_models.py`;
- all routers.

No runtime edit is authorized in 92B.

## 21. Protected Paths and Artifact Policy

The actual four-path Build scope is exactly:

1. `PROGRESS.md`;
2. `docs/architecture/MILESTONE_92_RULE6_GOVERNANCE_MIGRATION_BOUNDARY.md`;
3. `tests/test_milestone_92_rule6_governance_migration_boundary.py`;
4. `tests/test_progress_ledger_canonical_header.py`.

The three core boundary artifact paths are the first three conceptual
artifacts: ledger, record, and new boundary test. The canonical test path is
the only existing canonical supersession path. Exactly four canonical
functions may change. Finalized M87/M88/M89/M91 records, all finalized/runtime
tests, all Thinking-policy/runtime tests, all future 92C targets, production source, README, Constitution,
Architecture, API, routers, persistence, and runtime data are protected.

## 22. 92B Non-Capabilities

92B introduces no real tool execution, evidence collection, real apply,
rollback, new endpoint, API model, router, persistent store, background
scheduler, automatic Observe capture, Verification Aggregation, Critic/Repair
runtime triggering, Resource Governance runtime, or Economic Agency.

Candidate A-F remain deferred. Rule 4 migration remains separately pending.
Rule 6 runtime migration is not started. 92B is boundary-only.

## 23. Regression Gates and Accounting

Current full baseline is 2499. The new boundary file has exactly 48 tests,
with 15 `CURRENT_STATE_LOCK`, 23 `FUTURE_BOUNDARY_CONTRACT`, and 10
`NON_CAPABILITY_LOCK`; no parametrization. Canonical collection remains 23
after four function amendments. Expected 92B full total is 2547.

Expected focused labels are: M87 76, M88 50, M89 150, M91A+M91B 63,
Governance/policy/core 592, Progress 322, Architecture/Observation 363,
OpenAPI 304 paths / 108 schemas, api_server 8 / 23 / 0, and 9 existing
warnings / 0 new warnings.

## 24. Failure and Rollback Boundary

92B has no runtime rollback or apply capability. If a Build or gate fails, the
Build stops without broadening scope, repairing production, modifying any
additional existing test, committing, tagging, or pushing. No execution,
evidence collection, or persistence operation is authorized by failure
handling.

## 25. Future Migration Decision Gate

Future 92C requires independent audit of this local 92B Build, explicit human
authorization, a separately reviewed runtime plan, exact supersession review,
and proof of single Governance authority, T3 trace truthfulness, external
equivalence, no API/persistence expansion, and no execution capability.

92B Boundary Build is complete locally only after its focused and regression
gates pass. It remains unfinalized and uncommitted. Next authorized action is
independent audit of the Milestone 92B local Boundary Build before any commit,
tag, push, or future 92C decision.
