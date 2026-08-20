# Milestone 107A Final Real Apply Reviewed-Base Consumer-Proof Boundary

Classification: STRICT READ-ONLY FINAL-REAL-APPLY CONSUMER-PROOF REVIEW

Status: REVIEW COMPLETE LOCALLY / FINAL-ONLY BUILD BOUNDARY JUSTIFIED FOR PM REVIEW

This record determines whether the existing dry-run `original_hash_before`
evidence can support a truthful stale-base guard for the final-real-apply
consumer. It does not implement that guard, modify patch runtime, change
approval or persistence semantics, choose canonical mutation authority, or
resolve the direct-apply path.

## 1. Current Git and Authorization Boundary

- Git is authoritative.
- M106A is finalized locally at the reviewed baseline.
- M106A frozen evidence remains:
  - design SHA-256: `09576db02f27c16b66782bd76fdb890c067328e3fef746c540dc5a86d7250ee1`;
  - static-test SHA-256: `6f5e0c27eece15e4c49a9331fa72e3dd92ad340dade32e37a928c55636d19277`.
- M105B F03 rollback expected-state binding is closed and unchanged.
- M107A creates only this design candidate and its static/document lock as
  local review evidence.
- No `PROGRESS.md` change, production change, existing-test change, commit,
  tag, push, or M107B implementation is authorized by this review.

The only repository files permitted for M107A are:

- `docs/architecture/MILESTONE_107A_FINAL_REAL_APPLY_REVIEWED_BASE_CONSUMER_PROOF_BOUNDARY.md`;
- `tests/test_milestone_107a_final_real_apply_reviewed_base_consumer_proof_boundary.py`.

## 2. Binding M106A Decision

M106A selected no universal next HIGH fix:

```text
Selected finding: NONE
Selected model: MODEL_F_NO_NEXT_INDEPENDENT_BUILD
Decision: E_NO_NEXT_INDEPENDENT_HIGH_FIX_PROVEN
Future Build: NOT JUSTIFIED
```

M106A nevertheless identified one separately reviewable direction:
`FINAL-WORKFLOW-ONLY REVIEWED-BASE CONSUMER PROOF`. M107A is that separate
review. It must not reinterpret a final-only guard as a universal F02 fix.

## 3. Exact M107A Question

Can the current final-real-apply workflow consume the existing completed
dry-run record's `original_hash_before` as a reviewed-base source and reject a
changed final target before calling the real mutation primitive, without:

1. adding reviewed-base persistence or schema migration;
2. selecting a canonical relationship between direct apply and final apply;
3. changing approval, retry, rollback, or direct-caller semantics; or
4. claiming that direct apply has a reviewed-base source?

The answer is **YES, for the final-real-apply consumer only**.

## 4. Production Consumer Chain

The audited chain is:

```text
approved proposal/review
  -> approved_dry_run_gate
  -> patch_apply(dry_run=True)
  -> dry_run_review_gate(accept)
  -> real_apply_approval_gate
  -> final_real_apply_executor
  -> patch_apply(dry_run=False)
  -> post_apply_verification_gate
```

The relevant existing facts are:

| Stage | Existing identity/evidence | Consumer-proof result |
|---|---|---|
| Approved dry-run gate | Stores `proposal_id`, `patch_apply_id`, status, and target | Identifies the dry-run apply attempt for the approved proposal |
| Dry-run apply | Stores `dry_run=True`, status `dry_run`, normalized target, `original_hash_before`, and `original_hash_after` | Captures the UTF-8 SHA-256 of the target read at dry-run execution time |
| Dry-run review gate | Stores `approved_dry_run_gate_id`, `proposal_id`, `patch_apply_id`, and accepted review decision | Proves a human accepted that specific completed dry-run record |
| Real-apply approval gate | Stores the accepted review ID and `dry_run_patch_apply_id` | Carries the accepted dry-run record identity into final readiness |
| Final executor | Refreshes the gate, proposal, approval item, and linked dry-run record immediately before applying | Is the real mutation consumer that can consume the reviewed-base evidence |
| Shared patch apply | Reads current target and computes the final `original_hash_before` | Is the exact mutation boundary that must be preceded by the comparison |

Source evidence:

- `aether/action/approved_dry_run_gate.py:46-54` hard-codes the dry-run call
  and persists its `patch_apply_id`.
- `aether/action/patch_apply.py:31-56` computes `original_hash_before` with
  existing UTF-8 `sha256_text` before returning a dry-run record.
- `aether/action/dry_run_review_gate.py:27-48` binds review to the exact
  approved gate and patch-apply record.
- `aether/action/real_apply_approval_gate.py:149-186` carries the accepted
  review and dry-run apply IDs into final approval readiness.
- `aether/action/final_real_apply_executor.py:92-116` re-reads the linked
  dry-run record but currently does not compare its hash with final content.
- `aether/action/final_real_apply_executor.py:181-201` calls the shared real
  apply only after readiness refresh.

## 5. Current Gap

The dry-run record's `original_hash_before` is real execution evidence, but the
final executor currently uses the dry-run record only as a status/readiness
requirement. It does not prove that the bytes about to be mutated are the same
bytes read during the accepted dry-run.

The current excerpt uniqueness check is not equivalent. A changed file can
still contain the stored original excerpt exactly once, allowing a final apply
against surrounding content that was not present during review.

The direct path has no equivalent reviewed-base source. Direct callers invoke
the shared primitive without a dry-run ID and are intentionally outside this
boundary.

## 6. Candidate Models

| Model | Boundary | Result |
|---|---|---|
| `MODEL_A_FINAL_REVIEWED_BASE_EXECUTION_GUARD` | Consume the final gate's exact linked dry-run apply record; validate its target, mode, status, and SHA-256 base hash against a fresh final read before the real apply call | **SELECTED** |
| `MODEL_B_FINAL_DRY_RUN_RECORD_BINDING_FIRST` | Introduce a new immutable final-attempt or proposal/review binding before deciding how the existing dry-run hash becomes authoritative | Not selected; it adds persistence/authority design that is unnecessary for the bounded final-only stale-base consumer proof |
| `MODEL_C_UNIVERSAL_DIRECT_AND_FINAL_REVIEWED_BASE_BINDING` | Give direct apply and final apply one reviewed-base authority | Rejected; direct apply has no reviewed-base producer and this requires a canonical-route or new-state decision |
| `MODEL_F_NO_BUILD` | Stop without selecting the final-only boundary | Not selected; final consumer, source record, comparison, and failure behavior are sufficiently bounded for PM review |

## 7. Selected Model and Build-Readiness Decision

```text
Selected model: MODEL_A_FINAL_REVIEWED_BASE_EXECUTION_GUARD
Decision: A_FINAL_ONLY_REVIEWED_BASE_BUILD_JUSTIFIED
Future Build: JUSTIFIED FOR PM REVIEW
Actual Build: NOT STARTED
Universal F02 closure: NOT CLAIMED
```

This decision is a bounded authorization-to-review boundary, not production
authorization. A later PM-authorized Build may implement only the final
workflow guard described below. It must preserve direct apply as a separate
consumer unless a later authority decision explicitly changes that policy.

## 8. Exact Future Build Contract If Authorized

The future implementation must be local to the final executor readiness path
and its focused tests. Before `apply_patch_proposal(..., dry_run=False)` is
called, it must:

1. retrieve the final gate's `dry_run_patch_apply_id`;
2. require a record with `dry_run is True` and `status == "dry_run"`;
3. require a valid 64-character lowercase hexadecimal
   `original_hash_before`;
4. require the dry-run normalized target to equal the currently approved
   proposal normalized target;
5. read the current final target through the existing restricted reader;
6. compute the existing UTF-8 SHA-256 using the same semantics as
   `patch_apply.sha256_text`;
7. compare that current hash with the dry-run `original_hash_before`; and
8. fail closed before the real apply call when any source, target, read, or
   hash condition is missing, malformed, or mismatched.

The implementation must not create a new hash field, mutate the dry-run
record, persist proposal-time reviewed content, or use a different encoding or
normalization contract. The final mutation primitive remains the existing
shared `apply_patch_proposal` call.

## 9. Scenario Proof

| Scenario | Expected result under the selected future guard |
|---|---|
| A. Target is unchanged after accepted dry-run | Final hash equals dry-run `original_hash_before`; readiness may continue to existing apply checks |
| B. Target changes after dry-run but original excerpt remains unique | Hash mismatch; final apply is blocked before mutation |
| C. Dry-run ID is absent, record is missing, mode/status is wrong, or hash is malformed | Fail closed before mutation |
| D. Dry-run and final proposal target identities differ | Fail closed before mutation |
| E. Direct apply has no dry-run record | No new behavior; direct apply remains outside this final-only contract |
| F. Two final calls race | The guard does not solve F06 claim/mutation atomicity; no concurrency closure is claimed |

## 10. Security and Truthfulness Boundary

The selected guard addresses the final workflow's stale reviewed-base risk
only. It does not prove:

- direct apply is unauthorized;
- final-real-apply is the universal canonical mutation route;
- dry-run JSON records are tamper-proof or independently immutable;
- approval consumption is single-use;
- target write and record persistence are atomic;
- concurrent final execution is serialized;
- rollback or post-apply verification is redesigned; or
- F01, F04, F05, F06, or F07 is resolved.

The existing record is sufficient as a source for this narrowly scoped
consumer guard because the accepted final workflow already carries its exact
apply-record ID. Promoting that evidence to universal authority would be
false: direct apply never produces or consumes that record.

## 11. Persistence, API, and Compatibility Impact

If separately authorized and implemented exactly as scoped:

- persistence impact: NONE;
- schema migration: NONE;
- API/OpenAPI impact: NONE;
- route impact: NONE;
- approval semantics: UNCHANGED;
- retry semantics: unchanged except final stale-base attempts fail closed;
- direct apply behavior: UNCHANGED;
- rollback behavior: UNCHANGED;
- post-apply verification behavior: UNCHANGED;
- canonical patch authority: NOT PROVEN / UNCHANGED;
- Generic Act: NOT IMPLEMENTED / NOT AUTHORIZED / NOT GRANTED.

## 12. Failure-Closed and Removal Contract

The future guard must reject missing, malformed, stale, mismatched, unreadable,
or target-inconsistent reviewed-base evidence before reaching the real apply
call. It must not fall back to excerpt-only acceptance when the final workflow
requires a reviewed-base record.

Removal of this M107A review evidence is limited to deleting the two permitted
untracked files. No runtime rollback, data migration, schema rollback, route
restoration, or private-record conversion is needed because M107A implements
nothing.

## 13. Forbidden Scope

Without a separate PM-authorized decision, do not modify:

- `aether/action/patch_apply.py`;
- `aether/action/patch_rollback.py`;
- `aether/action/real_apply_approval_gate.py`;
- `aether/action/final_real_apply_executor.py`;
- `aether/action/patch_proposal.py` or `aether/action/patch_review.py`;
- approval queue, direct patch, tool-executor, or self-modification policy;
- API models, route registration, or `PROGRESS.md`;
- existing tests, dependencies, runtime data, or private records.

Do not implement the guard during M107A. Do not add proposal-time hash
persistence, universal direct-plus-final binding, final executor reservation,
transactional mutation, rollback redesign, automatic verification, or Generic
Act semantics.

## 14. M107A Gate Result

| Requirement | Result |
|---|---|
| Real production consumer exists | YES: final executor performs real mutation |
| Existing reviewed-base source exists | YES: linked dry-run `original_hash_before` |
| Exact source-to-consumer linkage exists | YES: final gate carries `dry_run_patch_apply_id` |
| Fresh final comparison is currently implemented | NO: this is the bounded gap |
| Final-only guard can avoid new persistence | YES |
| Direct path has equivalent source | NO |
| Canonical-route decision required | NO for final-only guard; YES for universal claim |
| Failure behavior is bounded and testable | YES |
| F06/F04 are solved by this guard | NO |
| Future Build boundary is small enough for PM review | YES |

```text
M107A review: COMPLETE LOCALLY
Selected model: MODEL_A_FINAL_REVIEWED_BASE_EXECUTION_GUARD
Decision: A_FINAL_ONLY_REVIEWED_BASE_BUILD_JUSTIFIED
Future Build: JUSTIFIED FOR PM REVIEW
Actual Build: NOT STARTED
Universal F02 closure: NOT CLAIMED
Canonical patch route: NOT SELECTED / NOT PROVEN
Generic Act: NOT_IMPLEMENTED / NOT_AUTHORIZED / NOT_GRANTED
```

Next authorized action: HUMAN/PROJECT-MANAGER REVIEW OF THE FINAL-ONLY BUILD
BOUNDARY. No production implementation, M107B, canonical-route decision, or
Generic Act work is authorized by this local review.
