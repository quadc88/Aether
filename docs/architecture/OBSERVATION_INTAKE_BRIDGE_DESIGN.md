# Observation Intake Bridge Design

**Milestone:** 84A Build — Observation Intake Bridge Design Record
**Date:** 2026-08-02
**Status:** Design record only — documentation of the future observation intake
bridge. No source code exists, no endpoint exists, and no runtime/API changes
are made by this record. This document is locked by the doc-only design lock
test `tests/test_observation_intake_bridge_design.py`.
**Plan sources:** `/home/aether/summaries/milestone_84_plan.txt` (Milestone 84
Plan, Candidate A selected) and `/home/aether/summaries/milestone_84A_plan.txt`
(84A Plan decision: design record + doc-only design lock test).

---

## 1. Purpose

The Observation Intake Bridge connects the Observe stage of the Aether
Execution Loop to the closed Observation Record Store (Milestone 83). It
accepts supplied `observed_value` / `expected_value` inputs and creates
Observation Records through the existing 82B builder
(`build_observation_record`) and the 83C store
(`queue.save_observation_record`).

It provides the store's first safe producer without real execution. Later
consumers (verification bridge, timeline/memory learning) are deferred
(Milestone 84 Plan candidates B/C); this bridge is the producer they need.

---

## 2. Non-execution Boundary

The intake bridge is declarative and non-executing. It:

- does not execute tools
- does not collect evidence
- does not call executor code
- does not call real apply
- does not call rollback
- does not call the policy/execution gate (policy_gate) for execution
- does not call /chat
- does not call /awaken
- does not call /identity*
- does not call /verification/classify
- does not call / (root path)
- performs no network calls (no web/network client usage)
- does not call protected/core route functions directly
- does not write runtime/private data during tests
- uses only the supplied observed_value (no automatic observation capture yet)
- uses only supplied observed_value; it never captures observations on its
  own
- automatic Observe-stage capture from tools/executors remains deferred
  (Milestone 83 closure deferred-items list)

---

## 3. Future Service Module and Function

- Future module: `aether/action/services/observation_intake_service.py`
- Future public function: `handle_observation_intake(request, context=None)`
- The function follows the repo service convention of `handle_*` functions
  (`handle_create_observation_record`,
  `handle_update_observation_record_status`, etc.). It was chosen over
  `create_observation_records_from_intake` to match that convention.
- The exact module path and function name are documented here so the 84A
  boundary-tests step can lock them statically.
- The module does NOT exist yet; it is implemented in Milestone 84B (Service
  Foundation). No implementation is created by 84A.

---

## 4. Intake Input Contract

Top-level required fields:

- `plan_step_id`: required, non-empty string
- `collector_contract_id`: required, non-empty string (intake records
  observations against a declared collector contract context; linkage
  preserved via the builder's `collector_contract_id` field)
- `evidence_items`: required, non-empty list of evidence item dicts

Top-level optional fields:

- `metadata`: optional dict (JSON-serializable)
- `safety_flags`: NOT accepted — the builder generates all-False safety flags;
  intake clients cannot supply them

Each evidence item (dict) fields:

- `evidence_item_id`: optional, non-empty string if present
- `target`: required, non-empty string (what was observed)
- `observed_value`: required, JSON-like value (any JSON-serializable type)
- `expected_value`: required, JSON-like value (any JSON-serializable type)
- `metadata`: optional dict (JSON-serializable)
- internal/lifecycle fields: forbidden (see section 5)

The builder's own constraint is satisfied automatically: `plan_step_id` is
always present, so the "at least one of plan_step_id/evidence_item_id" rule
holds for every generated record.

---

## 5. Forbidden Input Fields

Any forbidden field causes ValueError and **zero records are created** (the
whole intake is rejected, never partially created).

Rejected at top level:

- `observation_id`, `observation_type`, `observed_at`, `status`,
  `created_at`, `updated_at`, `decision`, `decided_at`, `reviewer`,
  `decision_reason`, `warnings`, `context_metadata`

Rejected lifecycle action fields (default no, unless a later Plan proves
reviewer/reason needed; default is NO):

- `new_status`, `reason`

Rejected per evidence item (same set minus plan-level keys):

- `observation_id`, `observation_type`, `observed_at`, `status`,
  `created_at`, `updated_at`, `decision`, `decided_at`, `reviewer`,
  `decision_reason`, `warnings`, `context_metadata`, `new_status`, `reason`,
  `safety_flags`

---

## 6. Intake Status Decision

The initial status is never client-supplied; it is decided by strict
comparison:

- `observed_value == expected_value` (strict JSON-normalized equality) ->
  `matched`
- otherwise -> `mismatched`
- pending is NOT a valid intake outcome for a fully supplied intake (no
  pending by default)
- error is never inferred by intake; validation failure raises `ValueError`
  and creates no record
- cancelled is never created by intake (cancel belongs to the 83E lifecycle)

The bridge therefore produces only `matched` or `mismatched` records from a
fully supplied intake: pending is not produced (no pending by default),
error is not inferred (a validation failure raises `ValueError` instead),
and cancelled is never created by intake (cancel belongs to the 83E
lifecycle).

---

## 7. Output Contract

The future service returns a pure service envelope, NOT an API schema:

```json
{
  "name": "observation_intake",
  "status": "completed",
  "created": <count of created records>,
  "observation_records": [<full store record dicts>],
  "errors": []
}
```

- The envelope must not call API response models
  (`ObservationRecordResponse` etc.) directly; no API layer exists in 84A/84B.
- The envelope must not leak runtime/private paths (no directory paths in the
  envelope).
- Records returned preserve the Observation Record STORE shape (builder
  fields + queue lifecycle envelope: `created_at`, `updated_at`, `decision`,
  `decided_at`, `reviewer`, `decision_reason`, `warnings`,
  `context_metadata`), not the route pure response shape; the route pure
  shape is for a future API (84C) only.

---

## 8. Matching Semantics

- JSON-like deep equality computed on JSON-serializable representations:
  `normalized(v) = json.dumps(v, sort_keys=True)` — the normalized form is
  computed with `json.dumps(value, sort_keys=True)` (strict serialization;
  no default=str; non-serializable input raises ValueError BEFORE any
  comparison).
- `normalized(observed_value) == normalized(expected_value)` -> `matched`
- otherwise -> `mismatched`
- deterministic strict equality: no type coercion, no fuzzy matching,
  no LLM judgment, no external verification, no tool calls.
- 1 and 1.0 are treated as not equal — i.e. 1 vs 1.0 NOT equal — by strict
  equality.

---

## 9. Atomicity

The bridge is all-or-nothing (ALL-OR-NOTHING): if any evidence item is
invalid (missing target, forbidden key, non-serializable value, malformed
item), the whole intake raises `ValueError` and **zero records are created**.

Justification: partial creation would leave orphan observation records from
an incomplete intake; the closed store has no bulk-rollback; single-failure
semantics keep the bridge deterministic; a corrected retry creates exactly
the intended set with no duplicates. There is no partial creation and
no orphan observation records: a failed intake leaves nothing behind.
---

## 10. Persistence and Testing Boundary

- Persistence uses only `build_observation_record`
  (`aether/action/observation_record.py`) + `queue.save_observation_record`
  (`aether/action/observation_record_queue.py`); no direct filesystem writes
  by the service.
- Tests monkeypatch `queue.get_observation_records_dir` to a `tmp_path`;
  no runtime/private mutation; no new persistence directory.
- no new runtime persistence directory is created by the bridge or its
  tests.
- JSON serialization and queue envelope validated by existing queue tests;
  intake tests validate records persisted via the temp-dir queue.

---

## 11. Forbidden Imports

The future service must not import:

- `aether.interface.api_server`
- `fastapi.testclient.TestClient` and `starlette.testclient.TestClient`
  (FastAPI/Starlette test clients; the bridge and its tests never use a
  test client)
- executor/apply/rollback execution modules (`apply_executor_*` builders are
  allowed only as pure data reference; execution/collector modules must not
  be called)
- tool execution modules (`tool_executor*`)
- the policy/execution gate for execution (`aether.action.policy_gate`)
- web/network clients (`requests`, `httpx`, `urllib`)
- runtime route handlers
- private runtime paths directly (use queue path helpers only)

---

## 12. Preserved Milestone 83 Invariants

- `VALID_STATUSES` exact set `{pending, matched, mismatched, error, cancelled}`
- no completed status is introduced by the intake bridge. completed is not introduced anywhere in 84A or 84B.
- builder immutable fields preserved (`observation_id`, `observation_type`,
  `observed_at`, `safety_flags` generated by the builder; intake never
  supplies them)
- safety_flags all False after every create (builder guarantees)
- 83E decision semantics preserved: update `decision == new_status`,
  `decision_reason == reason`; cancel `decision == "cancelled"`
- missing-record behavior preserved: queue returns None, service `found=False`
- queue lifecycle envelope preserved (decision semantics untouched; intake
  does not call update_status/cancel)
- store shape returned in the intake envelope (no route pure shape until 84C)

---

## 13. OpenAPI and Protected Core Interface Locks

- OpenAPI remains 304 paths / 108 schemas through 84A and 84B (the lock
  holds: OpenAPI stays 304 paths / 108 schemas).
- api_server stays 8 protected/core @app routes / 23 include_router / zero
  direct /action/* routes.
  (Protected Core Interface unchanged: zero direct /action/* routes.)
- The invariant 8 @app routes / 23 include_router / zero direct /action/*
  is preserved.
- New feature code must not be added to api_server.py; the Protected Core
  Interface is unchanged.
- No endpoint, no router, and no API model is added by 84A or 84B.

---

## 14. Future Boundary Tests Plan

- File: `tests/test_observation_intake_boundary.py` (new, AST/OpenAPI/
  doc-contract only; no service import; no TestClient; no endpoint
  invocation).
- REQUIRED before 84B.
- Locks (based on this design record):
  - design doc exists and contains required non-execution boundary wording
  - planned service module path/name documented
    (`observation_intake_service.py` / `handle_observation_intake`)
  - forbidden imports list documented
  - input contract documented (required vs forbidden fields)
  - matched/mismatched semantics documented (strict JSON-normalized equality)
  - all-or-nothing atomicity documented
  - no completed status introduced
  - OpenAPI stays 304 paths / 108 schemas
  - api_server stays 8 protected/core @app routes / 23 include_router / zero
    direct /action/* routes
  - the future service module does NOT yet exist (no implementation before
    its own milestone); tests are doc/static-contract only in this step
  - preserved 83 invariants wording (VALID_STATUSES, immutable fields,
    safety_flags all False, queue envelope, store shape)

---

## 15. Future 84B / 84C / 84D Sequence

Milestone 84 selected Candidate A (non-executing observation intake bridge).
84B not started. Milestone 85 not started.

1. 84A Build (this design record + doc-only design lock test) -> 84A
   Finalization (tag `milestone-84A-observation-intake-bridge-design`)
2. 84A Build Boundary Tests (tests-only:
   `tests/test_observation_intake_boundary.py`) -> its finalization (tag
   `milestone-84A-observation-intake-boundary-tests`); REQUIRED before 84B;
   no service implementation
3. 84B Service Foundation Plan/Build/Finalize:
   - implement `aether/action/services/observation_intake_service.py` using
     only `build_observation_record` + `queue.save_observation_record`
   - no router/API; no OpenAPI change (stays 304 paths / 108 schemas)
   - temp-dir persistence tests; service tests; forbidden-import compliance
   - full suite and drift 0 before finalization
4. 84C Router/API (optional, ONLY IF a real consumer need is proven):
   - if implemented: router/service/model/test structure; api_server.py
     registration-only (include_router); api_models request model; OpenAPI
     change intentional (304 -> 305 paths) with all lock tests updated via
     the authorized-lock workflow
   - otherwise skip 84C
5. 84D Closure record (required before Milestone 84 can close):
   - `docs/architecture/MILESTONE_84_OBSERVATION_INTAKE_CLOSURE.md` +
     doc-only closure test; deferred items (real tool-driven evidence
     collection, loop wiring, verification bridge from Candidate C);
     Milestone 85 eligibility

---

## 16. Deferred Items

- automatic Observe-stage capture from tools/executors (remains deferred;
  Milestone 83 closure deferred-items list)
- real evidence collection
- loop wiring (ObservationRecord -> verification/critic/repair)
- timeline/memory learning from observations
- verification bridge (Milestone 84 Plan candidate C)
- 84C Router/API only if a real consumer need is proven
- a completed status decision (a future milestone only if a later
  architecture decision proves it necessary)
