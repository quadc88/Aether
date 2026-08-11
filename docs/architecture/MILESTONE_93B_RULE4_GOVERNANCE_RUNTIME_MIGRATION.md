# Milestone 93B Rule 4 Governance Runtime Migration

Classification: RUNTIME IMPLEMENTATION / INTERNAL OWNERSHIP MIGRATION

This record describes the Milestone 93B Rule 4 Governance Runtime Migration
implementation content. Git is authoritative for whether this implementation
is committed, tagged, and published. This record does not self-assert its own
commit SHA, tag existence, or remote publication state. This record does not
itself authorize Git finalization.

## 1. Scope and Lifecycle

Milestone 93 is OPEN. Milestone 93A is the FINALIZED / DURABLE boundary. The
93B runtime implementation content is complete after all required gates pass.
Git directly determines whether that implementation content is durable, tagged,
and published.

The production scope is exactly:

1. `aether/thinking/policy.py`
2. `aether/core/governance.py`
3. `aether/core/loop.py`

No API, router, model, schema, persistence, execution, Observation,
Critic/Repair, Candidate A-F, organ, or capability expansion is included.

## 2. Rule 4 Ownership

Thinking no longer owns or authoritatively selects Rule 4. Its raw policy
domain is `rule_3 / clear`; it retains Rule 3, Rule 7, Rule 8, Rule 9, and
ordinary fall-through behavior.

Core Governance is the sole operative Rule 4 owner. It contains exactly one
operative `_SECRET_RISK_TERMS` set, one membership evaluation, and one complete
ten-key formatter. Perception remains the factual producer only.

The implementation provenance is `rule_3 / clear`. Governance Rule 4
selection is an authoritative decision, not Thinking provenance.

## 3. Private Sidecar and Loop

Governance accepts the keyword-only parameter:

```text
rule4_risk_terms_detected=_MISSING_RULE4_RISK_TERMS
```

The omitted sidecar defaults to `[]`. The private sentinel distinguishes an
omitted sidecar from explicit `None`. The sidecar is not copied into policy,
the envelope, approval records, responses, persistence, or trace output.

The loop passes exactly:

```python
rule4_risk_terms_detected=perception["risk_terms_detected"]
```

The loop performs transport only. It does not classify Rule 4, inspect terms,
own the term set, evaluate membership, materialize or copy the iterable,
normalize it, persist the sidecar, or expose the private sidecar name publicly.

## 4. Iterable Contracts

Contract A preserves native iteration semantics. Lists, tuples, generators,
strings, and other iterables are consumed as supplied. No list conversion,
copy, validation, or exception wrapping is added. Normal Perception production
continues to provide a reusable list.

Contract B preserves native malformed behavior on the Governance evaluation
path:

- missing sidecar: empty list, no Rule 4 selection;
- explicit `None`: native `TypeError`;
- non-iterable: native `TypeError`;
- unhashable encountered member: native membership `TypeError`.

Generator G1 and G2 cover matching-first and matching-later one-shot iterator
consumption, including the exact sequential reasons/warnings projection.

## 5. Ten-Key Projection

Governance constructs a fresh replacement projection in this exact order:

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

The effective Rule 4 values are `require_approval`, `high`, complete supplied
term joins, `True`, `False`, `False`, `None`, `None`, the existing sensitive
handling next step, and the existing sensitive-term warning. Raw Thinking
fields are not merged into the effective projection.

## 6. Precedence and Truth

Rule 3 remains Thinking-owned and blocks Governance Rule 4, Rule 5, and Rule 6.
Governance evaluates Rule 4 before the unchanged Rule 5 and Rule 6 branches.
Rule 5 and Rule 6 triggers, formatters, malformed behavior, and safety flags
remain protected.

For the Rule 7 collision, raw Thinking may return `suggest_tool` with
`tool_suggestion_allowed=True`; Governance replaces it with the complete Rule 4
projection and both tool flags set to `False`.

T3 remains truthful: the Thinking trace stage reports raw Thinking truth, the
policy-gate stage reports authoritative Governance truth, and effective
consumers use `authorization_envelope["policy_snapshot"]`.

## 7. Supersession Accounting

The final authorized inventory is:

- original accepted direct surfaces: 17;
- protected 93A current-runtime additions: 7;
- newly authorized additions: 3;
- corrected direct total: 27;
- existing parameter cases: 3;
- M89 wrapper independently counted: no.

The three newly authorized direct surfaces are:

1. `TestAppliedMigration.test_145_governance_signature_unchanged` in the M89
   boundary file. Only the Governance signature is reconciled to the exact
   seven-parameter form; the new parameter is keyword-only and uses the private
   missing-sidecar sentinel.
2. `TestGovernanceModuleExtraction.test_49_governance_function_signature_exact`
   in the M87 boundary file. Only the obsolete six-parameter signature lock is
   reconciled. The M89
   `TestReconciliationAccounting.test_78_m87_unaffected_tests_still_pass`
   wrapper remains unchanged and is not independently counted.
3. `test_no_capability_expansion_or_loop_mutation` in the M92C runtime file.
   Only the obsolete pre-93B loop byte snapshot is replaced by structural
   transport-only proof. All M92C scope, Rule 6, capability, persistence, and
   unrelated safety assertions remain.

The two previously authorized Thinking secret-term tests now distinguish raw
Thinking truth from effective Governance Rule 4 truth without removing the
sensitive-term compatibility proof.

## 8. Test Contract and Results

The new runtime contract remains exactly 26 ordinary non-parameterized tests,
with zero parameterized functions and zero parameter cases.

Recorded regression results:

- 93B runtime contract: 26 passed;
- 93A boundary: 34 passed;
- supersession family: 446 passed;
- Progress-equivalent five-file family: 362 passed;
- canonical ledger contract: 23 passed;
- full suite: 2631 passed, 0 failures, 0 errors;
- warning baseline: 9 `PytestRemovedIn10Warning` with zero category/occurrence delta.

The full candidate result is 2631 passed, with 0 failures and 0 errors.

## 9. Protected and Frozen Surfaces

The following remain byte-identical to their protected baseline:

- `README.md`;
- `docs/CONSTITUTION.md`;
- `docs/ARCHITECTURE.md` at version `0.3.0`;
- `docs/architecture/MILESTONE_93_RULE4_GOVERNANCE_MIGRATION_BOUNDARY.md`.

The API contract remains 304 OpenAPI paths and 108 schemas. The interface
shape remains 8 direct `@app` routes, 23 `include_router` calls, and 0 direct
`/action/*` routes. No interface, router, API model, schema, persistence,
approval, response, or trace path is modified.

Observation remains BLOCKED / deferred. Candidate A-F remain DEFERRED. No
Critic/Repair activation or capability expansion occurred.

## 10. Implementation Content Truth

`PROGRESS.md` reports Milestone 93 OPEN, Milestone 93A FINALIZED / DURABLE
boundary, Milestone 93B runtime implementation content complete, Core
Governance as the physical owner in the implemented content, provenance
`rule_3 / clear`, direct supersession `27`, parameter cases `3`, and new 93B
tests `26`.

Git directly determines implementation durability, tagging, and publication.
This record does not self-assert a commit SHA, tag existence, or remote
publication state.

## 11. Decision

All runtime, supersession, focused, Progress-equivalent, canonical,
interface/API, protected-core, and full regression gates pass. The durable
implementation-content decision is:

```text
MILESTONE_93B_RUNTIME_IMPLEMENTATION_CONTENT_COMPLETE
```

That decision does not itself authorize Git finalization.
