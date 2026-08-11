# Milestone 93 Rule 4 Governance Migration Boundary

Classification: BOUNDARY / DESIGN / EQUIVALENCE PROOF

This is not a runtime migration. It is the authoritative Milestone 93A
boundary contract and tests-only equivalence lock. It records current source
truth, future ownership, compatibility obligations, and explicit
supersession. It does not authorize production edits, Rule 4 migration,
execution, persistence expansion, commits, tags, or pushes.

## 1. Status and Scope

Milestone 93A Boundary Build is complete locally only when this record and the
tests-only boundary lock pass. Milestone 93 is OPEN. Milestone 92C is CLOSED.
Runtime migration has not started. This record is boundary/design/equivalence
proof only and does not itself change runtime behavior.

The exact repository Build scope is four paths:

1. `PROGRESS.md`
2. `docs/architecture/MILESTONE_93_RULE4_GOVERNANCE_MIGRATION_BOUNDARY.md`
3. `tests/test_milestone_93_rule4_governance_migration_boundary.py`
4. `tests/test_progress_ledger_canonical_header.py`

No fifth path is authorized. The canonical path is limited to truthful local
93A ledger state; no existing finalized/runtime test is superseded by this
Build.

## 2. PM Authorization and Non-Authorization

PM accepted Plan-R2 and authorized the 93A boundary Build with decision
`READY_FOR_93A_BOUNDARY_BUILD`.

Authorized here: creation of this decision record, creation of the new static
and pure-call boundary lock, and truthful updates to the four-path local
ledger state.

Not authorized: production source edits, Rule 4 runtime migration, Rule 3
migration, Rule 5/6 rewrite, API/router/model/persistence changes, execution,
apply, rollback, evidence collection, Observation wiring, commits, tags, or
pushes. The future runtime milestone still requires separate PM
authorization.

## 3. Authoritative Baseline

Architecture version is `0.3.0`; Constitution version is `0.2.0`. The accepted
Plan-R2 baseline is:

```text
branch: main
HEAD: fc5fde643b19daefc82a451052734cb17f32d9a6
origin/main: fc5fde643b19daefc82a451052734cb17f32d9a6
working tree: clean
staged: none
unstaged: none
git diff --check: clean
```

The current verified same-environment full baseline is 2571 passed with 9
existing `PytestRemovedIn10Warning`. A previously observed
`StarletteDeprecationWarning` is environment/run-dependent and is not part of
the stable warning baseline. OpenAPI is 304 paths / 108 schemas. The interface
shape is 8 direct `@app` routes / 23 `include_router` calls / 0 direct
`/action/*` routes.

## 4. Rule 4 Classification

Rule 4 is an Operational Hard Constraint under the corrected Milestone 88
classification. It narrows the allowed decision space when sensitive-term
evidence is present. It is not a soft optimization signal, a constitutional
literal dictionary, a public data model, or an execution capability.

The constitutional grounding is the permission and stronger-review boundary
for write/execute tools, protection of credentials and sensitive information,
human authority, accountability, and verification. The exact ten-key strings
remain implementation compatibility fields.

## 5. Current Rule Inventory

The current effective cross-layer order is:

```text
invalid policy
-> Identity Rule 1
-> Identity Rule 2
-> Rule 3
-> Rule 4
-> Rule 5
-> Rule 6
-> Rule 7
-> Rule 8
-> Rule 9
```

Rules 1 and 2 are Governance-owned. Rule 3, Rule 4, Rule 7, Rule 8, and Rule
9 are Thinking branches. Rules 5 and 6 are Governance-owned. Rule 4 is the
only remaining secret-term authorization branch in Thinking before this
future migration.

## 6. Current Rule 4 Physical Ownership

The current physical owner and selection function are
`aether/thinking/policy.py::_evaluate_chat_policy_with_precedence`.

Current Rule 4 selection owner: Thinking. Current Governance behavior is the
generic `decision_type == "require_approval"` proposal path. Governance has
no operative Rule 4-specific evaluator and no Rule 4-specific formatter.
Governance currently has: NO operative Rule 4-specific evaluator.
Governance remains the final envelope authority for the proposal it receives;
that generic envelope handling does not make Governance the current Rule 4
trigger owner.

## 7. Exact Current Rule 4 Trigger

The current source truth is:

```python
risk_terms = perception.get("risk_terms_detected", [])
secret_found = any(
    t in _SECRET_RISK_TERMS
    for t in risk_terms
)
if secret_found:
```

The exact current set, with case-sensitive direct membership, is:

```text
password
secret
api key
token
private_key
credential
secret_key
access_key
```

The Rule 3 empty/whitespace branch runs first and prevents this trigger. Rule
4 does not inspect `risk_level`, `action_type`, `suggested_tool`, metadata,
or normalized text beyond the earlier Rule 3 gate.

## 8. Exact Current Rule 4 Ten-Key Projection

The current Rule 4 policy has exactly these ten keys in source insertion order:

```text
decision_type
confidence
reasons
required_user_confirmation
tool_suggestion_allowed
tool_execution_allowed
blocked_reason
clarification_question
next_step
warnings
```

Its exact values are:

```text
decision_type = require_approval
confidence = high
reasons = [
  "Text contains sensitive terms: {', '.join(risk_terms)}. User confirmation required before handling."
]
required_user_confirmation = True
blocked_reason = None
clarification_question = None
next_step = "Confirm whether sensitive information should be handled."
warnings = ["Potentially sensitive terms detected: " + ", ".join(risk_terms)]
```

`risk_terms` is the complete detected list, including nonmatching terms. The
complete detected-term list is used in both joined fields. The
future projection is locked to this complete ten-key shape. It must not omit
either tool flag, reduce the list to matching terms, or inherit raw fields.

## 9. Current Governance Envelope Behavior

When the current Rule 4 proposal reaches Governance, the actual generic
approval envelope is:

```text
allowed = False
reason = Human approval is required before execution.
required_user_confirmation = True
requested_action = unchanged
policy_snapshot = shallow copy of the exact current ten-key Rule 4 policy
warnings = []
```

The envelope has no additional invented fields. The current `policy_snapshot`
is the copied Rule 4 policy. Approval construction, response construction, and
execution flags consume the existing envelope/effective policy behavior.

## 10. Current Cross-Layer Precedence

Identity Governance decisions precede the normal proposal path. Thinking Rule
3 precedes Thinking Rule 4. The current Rule 4 return prevents Thinking
fall-through and returns private `rule_4`; Governance recognizes that value as
not `clear`, so Governance Rule 5 and Rule 6 risk branches do not select.

The current result is therefore Thinking-selected Rule 4 followed by generic
Governance approval handling. This is distinct from future Governance Rule 4
selection and must not be described as already migrated.

## 11. Current Rule 3/4 Provenance Domain

The current private provenance domain is exactly:

```text
rule_3
rule_4
clear
```

`rule_3` means Thinking Rule 3 selected. `rule_4` means Thinking evaluated
the Rule 4 predicate and selected the Rule 4 proposal. `clear` means neither
current Thinking Rule 3 nor current Thinking Rule 4 selected. The value is
transport-only and is not copied into public policy, envelopes, approvals,
responses, persistence, or trace output.

## 12. Future Provenance Domain

The future produced domain, and specifically the future Thinking-produced domain, is exactly: `rule_3 / clear`.

```text
rule_3
clear
```

Future `rule_4` provenance is REMOVED. No Thinking code may produce future
`rule_4`, and Core Coordination may not synthesize it. Governance selects Rule
4 internally from factual evidence; that selection is an authoritative
decision, not Thinking provenance.

The future signal may retain the existing private variable name temporarily,
but its contract is Rule 3 precedence only.

## 13. Future Meaning of Clear

Future `clear` means only: Rule 3 did not win. It does not mean Rule 4 was evaluated, passed, or pre-cleared. Rule 4 remains unevaluated until Core
Governance evaluates the private factual evidence.

For future `rule_3`, Governance must preserve the Rule 3 blocker and must not
evaluate Rule 4, Rule 5, or Rule 6. For future `clear`, Governance evaluates
Rule 4 first, then permits Rule 5/6 only if Rule 4 does not select.

## 14. Rule 4 Evidence Producer

Perception is the factual evidence producer. It produces
`risk_terms_detected`; it does not authorize, select, or format the Rule 4
decision. Normal Perception lowercasing is preserved. Direct membership
semantics remain case-sensitive after Perception has produced its list.

Evidence production is not authorization.

## 15. Rule 4 Evidence Transport

Core Coordination transports the complete `risk_terms_detected` list
unchanged through a private sidecar to Governance. The sidecar is not public,
not persisted, not an API/model field, not an approval field, not a response
field, and not a trace field. Raw user text is not sent to Governance.

The loop is a transport boundary only. It must not inspect, classify, or
re-evaluate Rule 4. The future runtime scope must include `loop.py` if no
already-existing safe private channel can carry the sidecar; no new loop stage
or capability is authorized.

## 16. Future _SECRET_RISK_TERMS Ownership

The selected future strategy is one operative `_SECRET_RISK_TERMS` set in
Core Governance. No operative set or predicate remains in Thinking. No
duplicate operative predicate remains in Core Coordination. No neutral taxonomy
module is introduced by 93A.

The exact eight terms remain unchanged. Perception's factual labels do not
make Perception an authorization owner. This is a conceptual ownership lock;
the future runtime milestone may implement it only after separate PM
authorization.

## 17. Single-Authority and Single-Trigger Invariant

The exact Rule 4 membership predicate must be evaluated exactly once in the
future, by one operative Governance evaluator. The formatter runs only after
Governance has selected Rule 4 and is formatting-only.

The boundary prohibits a Thinking Rule 4 branch, a Thinking `secret_found`
authorization predicate, a Core Coordination Rule 4 predicate, an Action-layer
Rule 4 predicate, and duplicate Governance evaluators. Approval construction,
the Action facade, response construction, and trace construction consume the
selected result and do not evaluate Rule 4.

## 18. Future Governance Precedence

The conceptual future order is exact:

1. invalid policy;
2. Identity Rule 1;
3. Identity Rule 2;
4. Rule 3 blocker;
5. Rule 4;
6. Rule 5;
7. Rule 6;
8. raw Thinking Rules 7/8/9 proposal handling;
9. existing fail-closed and synthetic compatibility behavior.

Rule 3 is not migrated. Rule 4 is evaluated only when Rule 3 did not win.
Rule 5/6 are evaluated only when Rule 4 did not win. Thinking does not
authoritatively pre-clear Rule 4.

## 19. Rule 3 Protection Boundary

Rule 3 remains Thinking-owned, with the current exact empty/whitespace trigger,
`ask_clarification` decision, and `rule_3` provenance. It remains first in raw
Thinking order and is not migrated or reclassified.

Rule 3 prevents Governance evaluation of Rule 4, Rule 5, and Rule 6. No Rule
3 output, clarification question, precedence position, or effective behavior
is changed by this boundary Build.

## 20. Rule 5 Protection Boundary

Rule 5 remains Core Governance-owned, with its exact durable high-risk
evidence trigger, projection, generic envelope reason, and existing malformed
evidence behavior. It remains after Rule 4 and before Rule 6.

The only incoming semantic change is that future `clear` says Rule 3 did not
win; Governance must evaluate Rule 4 before Rule 5 becomes eligible. No Rule 5
trigger or projection rewrite is authorized.

## 21. Rule 6 Protection Boundary

Rule 6 remains Core Governance-owned after Rule 5, with exact medium risk,
non-None `requested_action`, existing malformed-action behavior, ten-key
projection, and envelope behavior. Rule 4 precedes Rule 6.

No Rule 6 semantic rewrite is authorized. Future Rule 6 eligibility follows
Governance's internal fact that Rule 4 was evaluated and did not select; it
does not depend on Thinking asserting Rule 4 `clear`.

## 22. Raw Thinking Fall-Through Contract

After Rule 4 deauthorization, raw Thinking behavior is intentionally limited
to the remaining branches:

```text
Rule 3: ask_clarification + rule_3
Rule 7: suggest_tool + clear
Rule 8: ask_clarification + clear
Rule 9: respond_only + clear
```

For Rule 4 factual evidence, raw Thinking returns whichever remaining branch
naturally wins. It never returns an authoritative Rule 4 approval. The raw
result is not universally `respond_only`; Rule 3, Rule 7, and Rule 8 cases are
distinct.

## 23. Effective Compatibility Projection

Future Governance must construct a fresh, complete Rule 4 ten-key dictionary
with the exact values in Section 8. Partial overlays, `dict.update` on raw
policy, inheritance of Rule 7/8/9 fields, implicit defaults, and raw/effective
field merge are forbidden.

`authorization_envelope["policy_snapshot"]` is the effective projection used
by approval construction, response construction, returned legacy policy
fields, decision fields, and confirmation fields. It must explicitly contain
`tool_suggestion_allowed = False` and `tool_execution_allowed = False`.

## 24. Rule 7 Collision Contract

The boundary locks a non-empty low-risk input with Rule 4 evidence and a
suggested tool. Future raw Thinking may return `suggest_tool` with
`tool_suggestion_allowed = True`. Governance must instead return the complete
Rule 4 projection with `decision_type = require_approval`,
`tool_suggestion_allowed = False`, and `tool_execution_allowed = False`.

No raw `True` may leak into the effective policy snapshot. Rule 7 remains a
Thinking soft signal and never authorizes execution.

## 25. T3 Trace Truth Contract

The Thinking stage records the actual raw Thinking result. The Policy-Gate /
Governance stage records the authoritative Governance result. Effective
consumers use `authorization_envelope["policy_snapshot"]`.

The raw and effective policies must not be merged. Do not merge raw and
effective policies, and the effective result
must not be written back into the raw Thinking trace. No new trace stage, stage
rename, stage reorder, persistence field, or public trace field is authorized.

## 26. Downstream Consumer Map

| Consumer | Current Rule 4 relationship | Future contract |
|---|---|---|
| Perception | produces `risk_terms_detected` | unchanged factual producer |
| Thinking policy | selects current Rule 4 | raw Rule 3/7/8/9 fall-through only |
| Core Coordination loop | transports policy, signal, evidence, action | unchanged transport plus private sidecar |
| Core Governance | generic approval handling | sole Rule 4 evaluator and formatter |
| Action policy facade | delegates envelope compatibility | no Rule 4 evaluation |
| Approval builder/queue | consumes pending approval | no Rule 4 evaluation; persistence unchanged |
| Response builder | consumes effective policy | projection-backed response unchanged |
| Trace builder | consumes precomputed stage data | truthful T3 raw/effective separation |
| `/chat` adapter | returns existing response shape | OpenAPI and response shape unchanged |

## 27. Malformed and Edge-Case Boundary

Current Thinking contract is preserved exactly: missing
`risk_terms_detected` defaults to `[]`; an explicit `None` raises native
`TypeError`; malformed iterables retain native iteration semantics; an
unhashable member raises native membership `TypeError` where applicable; direct
membership is case-sensitive; normal Perception lowercasing is preserved.

The exact future private-sidecar contract is Contract B:

- The sidecar value is the detected-term iterable itself. Any iterable is
  accepted, including the normal Perception `list`, tuples, generators, and
  strings, preserving current iteration semantics.
- A missing sidecar means `[]` and therefore does not trigger Rule 4.
- An explicit `None` is not iterable and raises native `TypeError`.
- A non-iterable sidecar raises its native `TypeError` during iteration.
- An iterable with an unhashable member raises native membership `TypeError`.
- These exceptions are raised by Core Governance, the sole future owner; no
  parallel Thinking validation or fail-closed conversion is added.
- Valid direct Governance calls use the same predicate semantics as target
  `/chat` calls. The same malformed direct Governance calls match the target
  pipeline's native exception class. No runtime implementation is performed
  by 93A.

## 28. Direct Thinking Semantic Supersession

The future raw change is intentional internal semantic supersession. Direct
`decide_chat_policy()` and
`_evaluate_chat_policy_with_precedence()` will no longer select Rule 4 or
return `rule_4`; they will return the reduced raw fall-through domain.

This is not falsely classified as unchanged. It is permitted only because
effective `/chat` decision, approval behavior, response shape, execution flags,
and public compatibility fields remain preserved through Governance's complete
projection and T3 routing.

## 29. Finalized Artifact Supersession Matrix

Historical architecture records remain byte-identical. M88's nine-rule
classification and Rule 4 classification remain historical. M89, M91, M92B,
and M92C records remain historical context and are not rewritten to claim Rule
4 was always Governance-owned.

The re-audited direct current-source surfaces are:

| Surface | Classification |
|---|---|
| `tests/test_thinking_policy.py::TestSecretRiskTerms::test_require_approval_on_password_term` | FULL |
| `tests/test_thinking_policy.py::TestSecretRiskTerms::test_require_approval_on_token_term` | FULL |
| `tests/test_milestone_88_cognitive_signal_arbitration_boundary.py::TestDecisionRecordStructure::test_07_actual_current_rule_count_is_seven` | FULL |
| `tests/test_milestone_88_cognitive_signal_arbitration_boundary.py::TestDecisionRecordStructure::test_08_every_source_rule_inventoried_once` | UNCHANGED historical classification |
| `tests/test_milestone_88_cognitive_signal_arbitration_boundary.py::TestDecisionRecordStructure::test_09_exact_source_order_preserved` | FULL |
| `tests/test_milestone_88_cognitive_signal_arbitration_boundary.py::TestRuleInventoryAndOutputs::test_10_exact_trigger_conditions_from_ast` | FULL |
| `tests/test_milestone_88_cognitive_signal_arbitration_boundary.py::TestRuleInventoryAndOutputs::test_11_exact_current_decision_outputs` | PARTIAL |
| `tests/test_milestone_88_cognitive_signal_arbitration_boundary.py::TestRuleInventoryAndOutputs::test_12_exact_confirmation_and_execution_fields` | PARTIAL |
| `tests/test_milestone_89_identity_hard_constraint_migration_boundary.py::TestRulePrecedence::test_23_current_source_order_preserved` | FULL |
| `tests/test_milestone_91b_rule5_governance_migration_boundary.py::test_25_scenario_field_exact_matrix` | PARAMETER-ONLY, 3 Rule 4 cases |
| `tests/test_milestone_91b_rule5_governance_migration_boundary.py::test_rule4_signal_from_single_ordered_evaluation` | FULL |
| `tests/test_milestone_91b_rule5_governance_migration_boundary.py::test_one_evaluation_no_duplicate_predicates` | FULL |
| `tests/test_milestone_91b_rule5_governance_migration_boundary.py::test_loop_transports_sidecar_unchanged` | FULL |
| `tests/test_milestone_92_rule6_governance_migration_boundary.py::TestPrecedenceAndTransport::test_rule4_precedes_rule6_in_current_thinking` | FULL |
| `tests/test_milestone_92c_rule6_governance_runtime_migration.py::test_current_rule6_trigger_exact` | PARTIAL, Rule 4 clause only |
| `tests/test_milestone_92c_rule6_governance_runtime_migration.py::test_thinking_rule3_rule4_provenance_retained` | FULL |
| `tests/test_milestone_92c_rule6_governance_runtime_migration.py::test_rule4_provenance_blocks_rule6` | FULL |
| `tests/test_milestone_92c_rule6_governance_runtime_migration.py::test_no_rule4_migration_or_duplicate_evaluator` | FULL |

This is 17 direct surfaces, with 3 Rule 4 cases inside one parameterized
matrix. The future implementation milestone, not this Build, may supersede
the named current-source assertions.

## 30. Future Runtime Production Matrix

The minimal future candidate set is:

- `aether/thinking/policy.py`: remove the operative branch and preserve raw
  fall-through;
- `aether/core/governance.py`: own the one term set, predicate, and formatter;
- `aether/core/loop.py`: transport private evidence if no existing safe private
  channel suffices.

The current conclusion is that `loop.py` is required for private evidence
transport unless a separately proven existing channel is selected. No neutral
taxonomy module, API/router/model/persistence path, or loop stage is required.

## 31. API Persistence and Capability Non-Expansion

No API field, route, router, schema, model, persistence field/store, approval
field, response field, trace field, or public envelope key is added. No tool or
action execution, apply, rollback, evidence collection, background runtime,
resource governance, economic agency, or capability expansion is enabled.

The current safety flags remain false. Existing approval persistence remains a
pending non-executing record. Raw/effective policy merge is forbidden.

## 32. Observation and Candidate A-F Deferral

Observation Intake has no proven production producer/consumer integration.
Verification Aggregation remains undefined. The producer-proof and
aggregator-proof gates remain active. Candidate A-F remain deferred.

93A does not consume Observation evidence, wire automatic capture, connect
Verification Aggregation, or connect Critic/Repair.

## 33. Protected Artifact Policy

README.md, Constitution, Architecture, all production `aether/*`, all
finalized architecture records, and all existing finalized/runtime tests are
protected and must remain byte-identical during this Build. In particular,
historical M88/M89/M91/M92 records are not rewritten.

Only the four paths in Section 1 may change. No existing historical/runtime
test is edited; the new boundary test records future supersession only. No
runtime/private files are touched.

## 34. Regression Gates and Accounting

The required gates are the new 93A boundary tests; M88, M89, M91B, M92B, and
M92C regressions; canonical ledger tests; Progress-referencing tests;
Architecture/Observation tests; and `python -m pytest -q`.

The pre-Build full baseline is 2571. The new boundary test count is reported
from pytest collection; no existing test is deleted for arithmetic. The
expected full result is 2571 plus the exact new collected count. Warning delta
caused by 93A must be zero. The parent warning inventory is 9
`PytestRemovedIn10Warning`; no stable Starlette warning category is included
in the current baseline.

OpenAPI must remain 304 paths / 108 schemas. `api_server.py` must remain 8
direct routes / 23 included routers / 0 direct `/action/*` routes.

## 35. Failure and Rollback Boundary

This Build has no runtime rollback or apply capability. If a gate fails, stop
without broadening scope, editing production, modifying other existing tests,
rewriting historical records, committing, tagging, or pushing. Failure cannot
authorize execution, persistence, evidence collection, or capability
expansion.

The raw final repository state must contain exactly the four authorized paths,
nothing staged, and a clean `git diff --check`. HEAD and origin remain the
accepted baseline.

## 36. Future Runtime Migration Decision Gate

Future runtime migration requires a separately authorized PM prompt, a reviewed
implementation plan, exact sidecar and malformed behavior implementation,
single Governance evaluator proof, complete ten-key projection proof, T3
truthfulness, Rule 3/5/6 protection, explicit test supersession, no API or
persistence expansion, no capability expansion, and full regression gates.

93A Boundary Build decision: `READY_FOR_93A_PM_REVIEW`. Git determines boundary
durability and publication state. The next capability step requires separate PM
authorization. Do not begin runtime migration.

Milestone 93A Boundary Build complete: yes
Repository modified: yes, exactly four authorized paths
Decision record H1 and H2 contract: PASS
Current Rule 4 key count: 10/10
Future Rule 4 evaluator: Core Governance, exactly one
Malformed future sidecar contract: resolved
Runtime migration: not started
Lifecycle durability:
determined from Git; this decision record does not self-assert its own commit,
tag, or remote publication state.
Next capability step: requires separate PM authorization
