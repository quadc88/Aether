# Thin Interface Refactor Plan

**Milestone:** 80A  
**Status:** Plan completed — no code refactor yet  
**Next:** All 80B-80M refactor phases complete. See PROGRESS.md for full status.

---

## 1. Purpose

Refactor `aether/interface/api_server.py` to conform to the Aether organ model. The interface layer should be thin — responsible only for routing HTTP requests to service functions and returning responses. All business orchestration (builder calls, record persistence, safety flag construction, timeline/graph side-effects) should live in explicit core/action service modules.

**Non-goals (excluded from 80A):**
- No code refactoring
- No endpoint path changes
- No response shape changes
- No safety logic changes
- No test changes
- No behavior changes

---

## 2. Current `api_server.py` Responsibility Map (4035 lines)

| Responsibility | Description | Approximate line range |
|---|---|---|
| **Routing** | All `@app.get` / `@app.post` decorators (~400 endpoints) | Throughout file |
| **Orchestration** | Chaining multiple builder and queue calls (e.g. dry-run → sandbox-contract → simulation-plan) | Lines 1310-1486, 1600-1650, 2862-3023 |
| **Record reads/writes** | Direct calls to `_get_*`, `_create_*`, `_list_*`, `_update_*` from queue modules | Nearly every endpoint |
| **Builder calls** | Direct calls to `_build_*` with record passing | Every pipeline endpoint |
| **Decision flows** | approve / reject / cancel status transitions on records | ~60 decision endpoints |
| **Response shaping** | Manual construction of large response dicts with all safety flags | 20+ pipeline endpoints |
| **Safety flag duplication** | Same ~15 flags copied into every pipeline response | 20+ endpoints |
| **Working memory side-effects** | Direct calls to `runtime.working_memory.add_event()` | 30+ endpoints |
| **Timeline side-effects** | Direct calls to `record_event()` | 20+ endpoints |
| **Graph side-effects** | Direct calls to `add_edge()` | 15+ endpoints |
| **Helper functions** | `_build_fallback_contract()`, `_record_*()`, `_add_*()` helpers | Inline with routing |
| **Request/response models** | ~80 Pydantic model classes | Lines 125-494 |

### Key observation

Each pipeline stage (approval → dry-run → sandbox-contract → simulation-plan → simulation-result → verification-verdict → apply-gate → human-authorization → apply-execution-gate → executor-contract → executor-plan → evidence-contract → collection-plan → collector-contract) repeats the identical pattern:

```
read parent record → call builder → persist record → construct response dict with safety flags
```

This redundancy violates DRY and makes `api_server.py` responsible for far more than routing.

---

## 3. Proposed Target Structure

```
aether/action/services/                  (NEW — one module per pipeline stage)
├── __init__.py
├── collection_plan_service.py           # Phase 1 (80B) — evidence collection plan + collector contract
├── evidence_contract_service.py         # Phase 2 (80C)
├── executor_plan_service.py             # Phase 2 (80C)
├── executor_contract_service.py         # Phase 3 (80D)
├── execution_gate_service.py            # Phase 3 (80D)
├── human_auth_service.py                # Phase 4 (80E)
├── apply_gate_service.py                # Phase 4 (80E)
├── verdict_service.py                   # Phase 4 (80E)
├── simulation_result_service.py         # Phase 5 (80F)
├── simulation_service.py                # Phase 5 (80F)
├── dry_run_service.py                   # Phase 5 (80F)
├── approval_service.py                  # Phase 5 (80F)
├── repair_workflow_service.py           # Phase 6 (80G)
├── guided_repair_service.py             # Phase 6 (80G)
├── tool_service.py                      # Phase 7 (80H)
├── memory_service.py                    # Phase 7 (80H)
└── pipeline_service.py                  # (OPTIONAL) shared response shaping + safety flags

aether/interface/
├── api_server.py                        # THIN: routes → service call → response
└── api_models.py                        # (OPTIONAL) extract all Pydantic models
```

---

## 4. Thin Interface Rule

After all phases, `api_server.py` must only:

1. **Receive HTTP request** — parse path params and body
2. **Call exactly one service function** — pass validated data
3. **Return the response** — pass through service result

It must NOT contain:
- Business orchestration (chaining builders/queues)
- Direct builder function calls
- Direct record store calls
- Working memory / timeline / graph side-effects
- Safety flag construction
- Inline helper functions

Example before refactor (current):
```python
@app.post("/apply-executor-plans/{id}/evidence-contract")
def endpoint(id: str, request: Body):
    plan_record = _get_aep(id)
    if plan_record is None:
        contract = _build_fallback_contract()
        eec_record = _create_aeecr(dict(contract), context)
        return { 35-line response }
    contract = _build_aeecc(plan_record, context)
    eec_record = _create_aeecr(dict(contract), context)
    return { 35-line response }
```

Example after refactor (target):
```python
@app.post("/apply-executor-plans/{id}/evidence-contract")
def endpoint(id: str, request: Body):
    return evidence_contract_service.handle_create(id, request)
```

---

## 5. Refactor Phases

| Phase | Scope | Milestones |
|---|---|---|
| **80B** | Evidence collection plan + collector contract endpoints | 77-79 |
| 80C | Executor plan + evidence contract endpoints | 73-76 |
| 80D | Executor contract + execution gate endpoints | 69-72 |
| 80E | Human auth + apply gate + verdict endpoints | 63-68 |
| 80F | Approval / dry-run / simulation endpoints | 54-62 |
| 80G | Repair workflow + guided repair endpoints | Later |
| 80H | Tool / file / memory endpoints | Early |
| 80I | Pydantic model extraction + deduplication | Global |

Each phase:
1. Creates new service file(s) in `aether/action/services/`
2. Moves orchestration logic out of `api_server.py` into the service
3. Leaves a thin route handler in `api_server.py` that calls the service
4. Changes NO endpoint paths, response shapes, or behavior
5. Passes full pytest after every phase

---

## 6. Recommended 80B Scope

Move only the **Milestone 77-79** orchestration:

### 6.1 Evidence Collection Plan

- `POST /apply-executor-evidence-contracts/{id}/evidence-collection-plan`
- Current: lines 2862-2941
- Calls: `_get_aeec()`, `_build_aeecp()`, `_create_aeecp()`

### 6.2 Evidence Collection Plan Record CRUD

- `GET /apply-executor-evidence-collection-plans`
- `GET /apply-executor-evidence-collection-plans/{id}`
- `POST /apply-executor-evidence-collection-plans/{id}/reject`
- `POST /apply-executor-evidence-collection-plans/{id}/cancel`
- `POST /apply-executor-evidence-collection-plans/{id}/approve-collection-plan-intent`

### 6.3 Collector Contract

- `POST /apply-executor-evidence-collection-plans/{id}/collector-contract`
- Current: lines 2944-3023
- Calls: `_get_aeecp()`, `_build_aeecp_collector()`

### Service module to create (Phase 1 / 80B)

`aether/action/services/collection_plan_service.py` containing:

- `handle_evidence_collection_plan_create(evidence_contract_id, context)` — build + persist + response
- `handle_collector_contract_create(collection_plan_id, context)` — build + response (no persist)
- `handle_list_plans(status, decision, limit)`
- `handle_get_plan(id)`
- `handle_reject_plan(id, reviewer, reason)`
- `handle_cancel_plan(id, reviewer, reason)`
- `handle_approve_plan_intent(id, reviewer, reason, confirmations)`

### No changes outside these files

- `aether/action/apply_executor_evidence_collection_plan.py` — untouched
- `aether/action/apply_executor_evidence_collector_contract.py` — untouched
- `aether/action/apply_executor_evidence_collection_plan_queue.py` — untouched
- `aether/core/*.py` — untouched
- `tests/*.py` — untouched

---

## 7. Test Strategy

- **Do not modify any test files** during any phase
- Tests use FastAPI TestClient hitting the same endpoints at the same paths
- Response shapes are identical (service functions return the same dicts)
- Full pytest must pass after every phase
- **Baseline:** `1347/1347 passed, 0 failures, 0 errors`

### Pre-phase checks

Before Phase 1 (80B), verify:
```bash
python -m pytest tests/ -v
git diff --stat
```

### Post-phase checks

After every phase:
```bash
python -m pytest tests/ -v                     # all tests pass
git diff --check                                 # no whitespace errors
git ls-files --others --exclude-standard         # no unexpected new files
```

---

## 8. Risk List

| Risk | Likelihood | Mitigation |
|------|-----------|-----------|
| **Import cycles** | Low | Service files import from `aether.action.*` and `aether.core.config` only, never from `aether.interface` |
| **Changed response shape** | Medium | Extract response dict construction verbatim; compare with `git diff` before commit |
| **Missing safety flags** | Low | All ~15 safety flags copied verbatim; can write a key-existence validation test |
| **Endpoint behavior drift** | Low | Full test suite runs after every phase; identical logic, same inputs |
| **Tests depending on api_server internals** | Low | Tests import `ap_mod.app` (TestClient), not internal functions |
| **Monkeypatching on api_server functions** | Low | Check `tests/` for `monkeypatch.setattr.*api_server` before each phase |
| **Stale imports in api_server.py** | Low | Remove unused imports after moving logic; `isort` / `flake8` detects |
| **Concurrent request safety** | None | Service functions are stateless and synchronous; same as current inline code |
| **Runtime data access** | None | Services use existing `get_private_dir()` via queue modules; unchanged |
| **Phase scope creep** | Manual | Each phase is scoped to exactly one pipeline group; no mixing |

---

## 9. Invariant Checklist (must hold at ALL times)

- [x] All endpoint paths unchanged
- [x] All response shapes unchanged
- [x] All safety flags remain `False`
- [x] No evidence collection performed
- [x] No apply / rollback executed
- [x] No tool execution invoked
- [x] No execution or apply authorization granted
- [x] No prohibited actions occurred
- [x] All tests pass (1347/1347)
- [x] No commits made without explicit instruction

---

## 10. Phase Checklist (for 80B and beyond)

- [ ] Service file created in `aether/action/services/`
- [ ] Orchestration logic moved from `api_server.py` to service
- [ ] Route handler in `api_server.py` thinned to single service call
- [ ] All imports cleaned up
- [ ] `python -m pytest tests/ -v` passes (1347/1347)
- [ ] `git diff --check` passes (no whitespace errors)
- [ ] No runtime/private data modified
- [ ] No source code outside scope modified
- [ ] No commits made
