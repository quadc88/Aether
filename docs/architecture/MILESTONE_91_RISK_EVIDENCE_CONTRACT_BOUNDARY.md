# Milestone 91A — Risk-Evidence Contract and Rule 5 Governance Boundary Proof

## 1. Status and Scope

Milestone 91A is a boundary-only, documentation-and-tests-only milestone.
It is a static risk-evidence compatibility contract and future Rule 5
precedence design. It performs no runtime migration, adds no operative
consumer, activates no Rule 5 Governance branch, and changes no current
runtime behavior. It makes no API, persistence, or execution change.

The current facts, future binding requirements, forbidden assumptions, and
future Milestone 91B activation requirements are deliberately separated in
this record. This record does not add a production data model.

## 2. Architectural Authority

Verification supplies evidence. Thinking proposes. Governance authorizes.
Action executes only within authorization. Core Coordination transports
evidence and context through the current loop.

Governance is the required future authoritative owner for operative Rule 5
risk authorization. Governance is not currently consuming `risk_evidence`
operatively. Risk evidence remains descriptive evidence, not authority.

Identity Rule 2 remains authoritative in Governance and must continue to
precede Rule 4 and Rule 5 in every future migration.

## 3. Current Producer Contract

The exact current producer is `aether.verification.risk.classify_risk`.
Its current required output fields are exactly:

- `risk_level` — broad current string value;
- `action_type` — broad current string value;
- `confidence` — broad current string value;
- `reasons` — broad current list value, currently a list of strings.

These are current broad types, not a new Pydantic schema or runtime model.
Milestone 91A does not add validation or change the producer.

## 4. Current Transport Contract

The current transport is:

```text
classify_risk(text)
  -> risk
  -> run_core_chat_loop
  -> risk_evidence=risk
  -> evaluate_authorization_envelope
```

The same current risk object is transported to Governance. Transport exists;
operative consumption does not.

## 5. Current Input-Boundary Contract

`evaluate_authorization_envelope` accepts the keyword-only parameter
`risk_evidence`. This proves input-boundary presence only. A signature that
accepts evidence does not imply that Governance consumes it in a decision.

## 6. Current Non-Operative Contract

Throughout Milestone 91A, `risk_evidence` remains non-operative. High-risk
`risk_evidence` alone must not change an authorization envelope result.
`None`, non-dictionary evidence, an empty dictionary, missing fields, and an
unknown `risk_level` remain safe under the current behavior. Milestone 91A
does not implement validation or runtime rejection for these variants.

No Rule 5 Governance branch may exist during 91A. Rule 5 remains physically
evaluated in `aether/thinking/policy.py`.

## 7. Current Arbitration and Precedence

The current effective pipeline is:

```text
invalid policy
  -> Identity Rule 1 / Rule 2 Governance result
  -> Thinking Rule 3-9 proposal
  -> Governance envelope fallback
```

Current behavior and current effective cross-layer precedence are proven by
source and tests. Identity Rule 1 or Rule 2 winning over Rule 4 is proven for
current behavior and required for every future migration. Rule 4 must never
override an existing authoritative Rule 1 or Rule 2 decision.

## 8. Required Future Rule 5 Precedence

Future Rule 5 migration precedence is not yet implemented or proven. The
binding future effective order is:

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

Implementation may span Governance and Thinking, but externally authoritative
effective order must remain equivalent. Moving Rule 5 into Governance must
not allow Rule 5 to override Rule 3 or Rule 4, and must not allow Rules 6-9 to
override Rule 5 when Rule 5 applies.

## 9. Future Rule 5 Governance Ownership

A future, separately authorized Milestone 91B may consume `risk_evidence`
operatively, authoritatively evaluate high-risk Rule 5 in Governance, and
supersede Thinking as the authoritative Rule 5 owner. Milestone 91A does not
authorize or perform any of those changes.

The current operative Rule 5 Governance consumer is none. Future consumer
feasibility is strongly proven by the existing producer, transport,
input-boundary, envelope, and downstream consumers. Feasibility is not
runtime migration readiness.

## 10. Supersession Contract

A future Rule 5 migration must remove or make non-authoritative the Thinking
Rule 5 evaluator, prevent two authoritative Rule 5 evaluators, preserve Rule
3 and Rule 4 precedence, and preserve Rule 5 precedence over Rules 6-9. It
must explicitly amend affected finalized static tests and preserve current
API and execution safety invariants.

No current test is amended by 91A. No duplicate authoritative evaluator may
be introduced by 91A.

## 11. Exact Reason-Preservation Contract

Milestone 91A selects **OPTION A — EXACT REASON PRESERVATION**.

Current Rule 5 Thinking reason semantics are:

```text
High-risk request ({action_type}). Human approval required before any action.
```

Current Rule 5 Thinking warning semantics are:

```text
High-risk classification: {action_type}.
```

Current Governance envelope `reason` for a `require_approval` proposal is:

```text
Human approval is required before execution.
```

The current approval request uses the envelope reason, so its current Rule 5
`approval_request.reason` is also the Governance generic reason above. These
current layer-specific strings are not claimed to be identical. The future
Rule 5 migration must preserve each current externally visible surface
exactly: decision, raw Thinking reason and warning semantics, Governance
envelope reason, approval request reason, `required_user_confirmation`,
`tool_execution_allowed`, `action_execution_allowed`, response text, API
shape, persistence behavior, and execution behavior.

The target classification is:

```text
EXTERNALLY RESPONSE-, DECISION-, APPROVAL-REQUEST-, EXECUTION-FLAG-, AND
API-SHAPE-PRESERVING, WITH AN INTENTIONAL INTERNAL OWNERSHIP AND TRACE CHANGE
```

No Governance-generic replacement reason is authorized beyond preserving the
current envelope and approval-request values already produced by Governance.

## 12. Approval-Request Equivalence Contract

Future migration must preserve the current approval-request contract:

`approval_required`, `approval_type`, `approval_status`, `decision_type`,
`execution_decision`, `reason`, `risk_level`, `risk_action_type`,
`requested_action`, `required_confirmations`, `safety_checks`, and metadata
shape. No new approval-request schema is authorized.

## 13. Trace and T3 Contract

The raw Thinking trace must remain truthful about the actual Thinking
proposal. The effective Governance trace must remain truthful about the
authoritative result. The trace must not claim Rule 5 Governance ownership
before future activation.

Future 91B must explicitly define trace ownership after migration. The
required strategy is T3-style separation of raw Thinking proposal from
effective Governance result. Trace remains response-only and non-persistent.

## 14. Missing, Malformed, and Unknown Evidence

Current and future safe handling is defined for `None`, non-dict evidence,
missing `risk_level`, unknown `risk_level`, missing `action_type`, missing
`confidence`, and non-list `reasons`. During 91A these values remain safe
without new validation or runtime rejection. A future 91B implementation may
define stricter handling only through its separately authorized contract and
must remain fail-closed without enabling execution.

## 15. API Invariants

There is no change to OpenAPI paths, OpenAPI schemas, operation IDs, the
`/chat` response shape, the approval-request schema, or the authorization-
envelope shape. The current baseline is 304 paths and 108 schemas.

## 16. Persistence Invariants

Milestone 91A adds no record store, queue, risk-evidence persistence, trace
persistence, or private runtime file. Existing approval persistence semantics
remain unchanged.

Milestone 91A adds no new persistence.

## 17. Execution Invariants

All current execution flags remain false. No tool execution, action execution,
apply, evidence collection, rollback, simulation, or external call may be
enabled by 91A. Approval requests and records remain non-executing.

## 18. Protected Scope

Exactly these three repository paths are authorized for 91A:

```text
PROGRESS.md
docs/architecture/MILESTONE_91_RISK_EVIDENCE_CONTRACT_BOUNDARY.md
tests/test_milestone_91_risk_evidence_contract_boundary.py
```

The boundary record and boundary test are new. The future authoritative home
is `aether/core/governance.py`; the current Rule 5 evaluator remains
`aether/thinking/policy.py`. `PROGRESS.md` is the only existing repository file
authorized for modification. All production files,
prior architecture records, existing tests, Constitution, Architecture,
README, history records, identity seed, configuration, and runtime/private
data are protected.

## 19. Future Activation Gate

Before Milestone 91B may begin, all of the following are required: accepted
91A boundary record; accepted 91A independent audit; separately authorized
runtime migration plan; exact precedence design; exact supersession matrix;
exact existing-test amendment matrix; exact API-visible equivalence matrix;
proof of no duplicate evaluator; and proof of no execution or persistence
expansion.

## 20. Explicit Non-Authorization

Milestone 91A does not authorize Rule 5 migration, risk activation,
production edits, existing-test amendments, API changes, persistence,
execution, Milestone 91B, or Milestone 92. Milestone 91A is complete locally
only after its record and tests pass; it remains unfinalized pending audit.
