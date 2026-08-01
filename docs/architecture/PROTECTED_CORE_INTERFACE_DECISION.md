# Protected Core Interface Decision

## Status
Accepted.

## Decision
Aether intentionally stops the thin-interface extraction at the protected/core boundary.

`aether/interface/api_server.py` remains the Protected Core Interface for the final 8 protected/core routes.

The following routes remain directly in `api_server.py`:
- `GET /`
- `GET /identity/integrity/status`
- `POST /identity/integrity/initialize`
- `POST /identity/integrity/verify`
- `GET /identity`
- `POST /awaken`
- `POST /chat`
- `POST /verification/classify`

No protected/core router extraction is planned unless a future decision record explicitly reopens this boundary.

## Context
The thin-interface refactor successfully extracted all action/orchestration surfaces from `aether/interface/api_server.py` into dedicated router modules under `aether/interface/routers/`. After the 82AU milestone, `api_server.py` contains:
- 8 direct protected/core `@app` routes
- 22 `include_router` calls
- zero `/action/*` routes

The 82AU milestone added `tests/test_protected_core_routes_boundary.py` — 23 AST/OpenAPI-only boundary tests that lock the protected/core route surface. The OpenAPI baseline is 300 paths / 103 schemas. The full pytest baseline is 1628/1628 passed, 0 failures, 0 errors.

## Scope Boundary
This decision applies only to protected/core routes. It does not reverse or weaken action route extraction. New action/orchestration routes should still use routers and services. `api_server.py` must not become a general route dumping ground again.

## Rationale
- `/chat` is Aether's primary cognitive runtime entrypoint — it invokes the full cognitive loop (`runtime.process_chat`, loop trace construction, response shaping).
- Identity integrity routes (`/identity/integrity/*`, `/identity`) protect identity continuity, which is priority #2 in the Aether Constitution.
- `/awaken` touches runtime lifecycle via `handle_awaken`.
- `/verification/classify` touches safety/risk classification via `classify_risk` — a safety gate.
- Pure thin-interface architectural purity is not worth the risk to Aether's core runtime, identity, or safety.
- The `docs/THIN_INTERFACE_REFACTOR_PLAN.md` explicitly scoped its work to business orchestration: builder calls, record persistence, safety flag construction, timeline/graph side-effects. Protected/core routes are core entrypoints, not action orchestration routes.
- All action surfaces (approval, dry-run, simulation, verification, apply-gate, executor, memory, tool, repair, guided-launcher, self-modification, etc.) have already been extracted.

## Invariants
- `api_server.py` should remain limited to protected/core entrypoints plus router registration.
- `api_server.py` should retain exactly 8 protected/core `@app` routes unless a future decision record changes this.
- `api_server.py` should retain zero `/action/*` direct routes.
- `api_server.py` should continue including all 22 extracted routers.
- No protected/core router files should be introduced without a new Plan milestone and explicit decision record.
- Existing OpenAPI compatibility must be preserved (300 paths / 103 schemas).
- Existing operation IDs must be preserved.
- Boundary tests must remain green.

## Verification
- `tests/test_protected_core_routes_boundary.py` (23 tests) — AST/OpenAPI-only boundary tests; no TestClient; no endpoint invocation.
- OpenAPI exact match: 300 paths / 103 schemas.
- Full pytest baseline: 1628/1628 passed, 0 failures, 0 errors.
- No endpoint invocation in the boundary test.
- No TestClient in the boundary test.
- Runtime behavior remains covered by existing runtime tests: `tests/test_chat_api.py`, `tests/test_identity_awaken.py`, `tests/test_cognitive_loop_contract.py`, `tests/test_cognitive_loop_observability.py`, `tests/test_cognitive_loop_trace_hardening.py`, `tests/test_risk_expansion.py`.

## Future Work
- Future milestones may strengthen documentation or boundary tests.
- Future protected/core route extraction is not allowed by default.
- Reopening extraction requires:
  - a new Plan milestone
  - explicit risk assessment
  - OpenAPI exact-match gates
  - manual audit before finalization
  - no behavior changes
- Recommended next area after finalization is architecture cleanup or the next non-protected feature, not automatic protected/core extraction.
