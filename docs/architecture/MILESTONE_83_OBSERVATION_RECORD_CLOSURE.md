# Milestone 83 Observation Record Closure

## Status

- Status: Closure record for Milestone 83
- Milestone 83 is not considered closed until 83F Finalization is accepted.
- 83F Build does not start Milestone 84.

## Purpose

The Observation Record Store is the durable record layer for the Observe stage of
the Execution Loop. It records observed values, expected values, status, metadata,
and safety flags. It supports create, get, list, update-status, and cancel after
milestone 83E.

## Timeline

- 83A — Observation Record boundary tests
- 83B — Observation Record schema foundation
- 83C — Observation Record service and store foundation
- 83D — Observation Record router and API endpoints
- 83E — Observation Record update/cancel lifecycle

Tags:

- milestone-83A-observation-record-boundary-tests
- milestone-83B-observation-record-schema-foundation
- milestone-83C-observation-record-service-and-store-foundation
- milestone-83D-observation-record-router-and-api-endpoints
- milestone-83E-observation-record-update-cancel-lifecycle

## Final Public API

Endpoints:

- POST /observation-records
- GET /observation-records
- GET /observation-records/{observation_id}
- PATCH /observation-records/{observation_id}/status
- POST /observation-records/{observation_id}/cancel

Operation IDs:

- create_observation_record
- get_observation_record
- list_observation_records
- update_observation_record_status
- cancel_observation_record

- OpenAPI remains 304 paths / 108 schemas.
- Observation paths exact 4.
- Observation operation IDs exact 5.

## Final Internal Components

- aether/action/observation_record.py
- aether/action/observation_record_queue.py
- aether/action/services/observation_record_service.py
- aether/interface/routers/observation_routes.py
- aether/interface/api_models.py
- tests/test_observation_record.py
- tests/test_observation_record_schema.py
- tests/test_observation_record_queue.py
- tests/test_observation_record_service.py
- tests/test_observation_record_routes.py
- tests/test_observation_record_boundary.py

## Final Invariants

- VALID_STATUSES = pending, matched, mismatched, error, cancelled
- update_status: status == new_status
- update_status: decision == new_status
- update_status: decision_reason == reason
- cancel: status == "cancelled"
- cancel: decision == "cancelled"
- cancel: decision_reason == reason
- missing record: queue update/cancel return None
- service missing update: found=False, updated=False, observation_record=None
- service missing cancel: found=False, cancelled=False, observation_record=None
- non-pending records do not transition again
- list ordering remains newest first by created_at
- observation_id is generated and immutable
- immutable builder fields remain immutable during update/cancel

## Safety/Security Boundary

- api_server.py remains the Protected Core Interface.
- api_server.py has 8 protected/core @app routes.
- api_server.py has 23 include_router calls.
- api_server.py has zero direct /action/* routes.
- New feature code must not be added to api_server.py.
- Observation routes live in aether/interface/routers/observation_routes.py.
- Forbidden raw fields for update:
  observation_id, observation_type, observed_at, safety_flags, created_at,
  updated_at, decision, decided_at, decision_reason, warnings, context_metadata,
  status
- Forbidden raw fields for cancel:
  all update forbidden fields plus new_status
- Cancel only accepts reviewer and reason.
- Update-status only accepts new_status, reviewer, reason.
- No generated/internal/store lifecycle fields are accepted from API clients.

## Persistence Boundary

- Observation records persist under private runtime data using runtime path helpers.
- Runtime/private data must not be tracked by git.
- 83F does not create runtime/private data.
- Closure doc does not alter persistence behavior.
- JSON serialization remains validated by tests.

## Response Shape Contract

- API responses use pure ObservationRecordResponse.
- No service envelope leakage:
  name, found, updated, cancelled, observation_record
- No store lifecycle leakage:
  created_at, updated_at, decision, decided_at, reviewer, decision_reason,
  warnings, context_metadata
- ObservationRecordListResponse wraps pure response items.

## Status Lifecycle Contract

- pending is the entry state.
- matched, mismatched, error, cancelled are terminal statuses.
- no completed status is added.
- this closure record does not recommend adding a completed status.
- a completed status or completion endpoint would be a future milestone only if a later architecture decision proves it necessary.

## Intentionally Deferred Items

- Real observation execution/wiring into the broader execution loop.
- Automatic Observe-stage capture from tools/executors.
- Rich evidence payload formats beyond observed_value/expected_value.
- Audit history of lifecycle transitions.
- Bulk update/cancel operations.
- Any future completed status.
- UI/admin review workflow for observation records.
- Cross-record correlation or analytics.

## Closure Criteria

- 83A–83E finalized and pushed.
- 83F closure doc created.
- 83F closure test added and passing.
- OpenAPI remains 304 / 108.
- api_server remains 8 / 23 / zero direct /action/*.
- full test baseline from 83E preserved.
- drift 0.
- PROGRESS updated.
- 83F Finalization accepted.
- Only after 83F Finalization accepted can Milestone 83 be declared closed.

## Next Milestone Rule

- Milestone 84 Plan may start only after 83F Finalization is accepted.
- Milestone 84 is not started by 83F Build.
- The content of Milestone 84 must be decided by a future Plan after re-reading
  PROGRESS/architecture.
