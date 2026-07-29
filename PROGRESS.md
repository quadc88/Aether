# Aether Project Progress Ledger

**Last updated:** Milestone 81F — Project Ledger and Architecture Reconciliation
**Aether version:** 0.2.0  
**Pipeline maturity:** Full declarative safety chain (approval through evidence contract record stores) with thin interface refactor (80B-80M) and cognitive runtime observability (81A-81E) complete. No real tool execution, apply, evidence collection, or rollback yet.

---

## 1. Purpose

This file is the compact project memory ledger for Aether. Every future OpenCode milestone must read this file before planning or editing. Every completed milestone must update this file. This file prevents project drift when chat context becomes too long.

---

## 2. Mandatory Workflow

- Before starting any milestone, read `PROGRESS.md`.
- Before starting any milestone, also read `docs/CONSTITUTION.md` and `docs/ARCHITECTURE.md`.
- Before editing code, check current git status.
- After completing any milestone, update `PROGRESS.md`.
- After completing any milestone, write a summary to `/home/aether/summaries/milestone_<number><letter>_summary.txt`.
- Do not commit unless explicitly instructed.
- Keep runtime/private data outside git.
- Never track `/home/aether/data` or private runtime directories.

---

## 3. Current Identity / Philosophy

- Aether is a single persistent digital intelligence, not a chatbot, not a model router, not a multi-agent framework.
- AetherOS is the operating environment/body/world.
- Models/tools/plugins are organs/resources/consultants, not Aether itself.
- Aether must use verification, evidence, memory, time, identity continuity, and policy gates.
- External intelligence provides opinions; Aether decides.
- Verification is mandatory before learning, acting, or reporting completion.
- External tools/models assist but never override Aether's decision authority.

---

## 4. Target Execution Loop

```text
Receive Goal → Understand → Think → Plan → Act → Observe → Verify → Critic → Repair → Learn → Report
```

Core loop:
```text
Think → Plan → Act → Observe → Verify → Critic → Repair → Think
```

---

## 5. Current Implemented Safety Chain

```text
approval_record
  → approval
    → dry_run_record
      → sandbox_contract
        → simulation_plan
          → simulation_plan_record
            → simulation_result
              → simulation_result_record
                → verification_verdict
                  → verification_verdict_record
                    → apply_gate_request
                      → apply_gate_record
                        → human_apply_authorization_request
                          → human_authorization_record
                            → approved_intent
                              → apply_execution_gate_request
                                → apply_execution_gate_record
                                  → approved_execution_intent
                                    → apply_executor_contract
                                      → apply_executor_contract_record
                                        → approved_contract_intent
                                           → apply_executor_plan
      → apply_executor_plan_record (Milestone 74A)
        → approved_plan_intent / rejected / cancelled
          → apply_executor_evidence_contract
            → apply_executor_evidence_contract_record (Milestone 76A)
              → approved_evidence_contract_intent
                → apply_executor_evidence_collection_plan (Milestone 77A)
                  → apply_executor_evidence_collection_plan_record (Milestone 78A)
                    → approved_collection_plan_intent
                      → apply_executor_evidence_collector_contract (Milestone 79A)
```

This chain remains **declarative and non-executing**. It does not collect evidence, execute tools, apply changes, or rollback changes.

Important state:
- All records persist as JSON files under `/home/aether/data/private/<record_type>/`
- Every record has a unique ID, timestamps, and safety flags
- `approved_intent`, `approved_execution_intent`, `approved_contract_intent` only **record intent** — they do NOT authorize execution or apply
- `approved_plan_intent` only records plan review intent — it does NOT authorize execution, apply, evidence collection, or rollback plan attachment
- `approved_evidence_contract_intent`, `approved_collection_plan_intent`, and `collector_contract_ready` are also declarative — they do NOT authorize evidence collection, tool execution, apply, or rollback
- No real executor exists yet
- No real apply exists yet
- No rollback execution exists yet
- No evidence collection exists yet

---

## 6. Completed Milestones

### 48-50: Core Foundation
| Milestone | Description | Status |
|-----------|-------------|--------|
| 48 | Core integrity foundation | Complete |
| 48B | Core chat loop skeleton | Complete |
| 49 | Thinking policy layer | Complete |
| 50 | Verification rule expansion | Complete |

### 51-54: Policy, Approval, and Queue
| Milestone | Description | Status |
|-----------|-------------|--------|
| 51 | Policy enforcement gate | Complete |
| 52 | Approval request object | Complete |
| 53 | Architecture documentation sync | Complete |
| 54 | Approval queue record store | Complete |

### 55-62: Dry Run, Simulation, and Verdict
| Milestone | Description | Status |
|-----------|-------------|--------|
| 55 | Approval decision gate | Complete |
| 56 | Dry-run request object | Complete |
| 57 | Dry-run record store | Complete |
| 58 | Dry-run sandbox contract | Complete |
| 59 | Simulation plan object | Complete |
| 60 | Simulation plan record store | Complete |
| 61 | Simulation result object | Complete |
| 62 | Simulation result record store | Complete |

### 63-70: Verification, Apply Gate, Authorization, Execution Gate
| Milestone | Description | Tests | Status |
|-----------|-------------|-------|--------|
| 63 | Simulation verification verdict | - | Complete |
| 64A | Verification verdict record store | 4 tests | Complete |
| 64B | Live API verification verdict validation | 14/14 cases | Complete |
| 65A | Apply gate request object | - | Complete |
| 65B | Live API apply gate validation | 14/14 cases | Complete |
| 66A | Apply gate record store | ~17 tests | Complete |
| 66B | Live API apply gate record validation | 14/14 cases | Complete |
| 67A | Human apply authorization request object | 32 tests | Complete |
| 67B | Live API human authorization validation | 14/14 cases | Complete |
| 68A | Human authorization record store | 42 tests | Complete |
| 68B | Live API human authorization validation | 14/14 cases | Complete |
| 69A | Apply execution gate request object | 35 tests | Complete |
| 69B | Live API apply execution gate validation | 14/14 cases | Complete |
| 70A | Apply execution gate record store | 807 tests | Complete |
| 70B | Live API apply execution gate record validation | 16/16 cases | Complete |

### 71-76: Executor Contract, Plan, Record Store, Evidence Contract, and Evidence Contract Record Store
| Milestone | Description | Tests | Status |
|-----------|-------------|-------|--------|
| 71A | Apply executor contract object | 867 tests | Complete |
| 71B | Live API apply executor contract validation | 16/16 cases | Complete |
| 72A | Apply executor contract record store | 942 tests | Complete |
| 72B | Live API apply executor contract record validation | 16/16 cases | Complete |
| 73A | Apply executor plan object | 1014 tests | Complete |
| 73B | Live API apply executor plan validation | 18/18 cases | Complete |
| 73C | Progress ledger (this file) | 1014 tests | Complete |
| **74A** | **Apply executor plan record store core** | **1095 tests** | **Complete** |
| **75A** | **Apply executor evidence contract object** | **1166 tests** | **Complete** |
| **75B** | **Live API apply executor evidence contract validation** | **1166 tests** | **Complete** |
| **76A** | **Apply executor evidence contract record store** | **~84 tests** | **Complete** |

New in 74A:
- `aether/action/apply_executor_plan_queue.py` — create/read/list/update records
- Persist apply_executor_plan objects under `/home/aether/data/private/apply_executor_plans/`
- POST executor-plan now persists the generated apply_executor_plan_record
- GET /apply-executor-plans — list with status/decision filters
- GET /apply-executor-plans/{id} — read single record
- POST /apply-executor-plans/{id}/cancel, /reject, /approve-plan-intent
- approved_plan_intent requires plan_ready + confirmations; keeps all safety flags false
- Evidence, apply, rollback, execution always remain false

Each recent milestone (67-74):
- Added one or more objects + optional record stores
- Added API endpoints for CRUD operations
- Followed strict safety invariants (all flags always false)
- Passed full test suite with zero failures
- Verified git safety (no unwanted changes)

### 76A — Apply Executor Evidence Contract Record Store Core

**Status:** Complete
**Tests:** ~84 (50 queue unit tests + 34 API tests)
**Storage path:** `/home/aether/data/private/apply_executor_evidence_contracts/`

New in 76A:
- `aether/action/apply_executor_evidence_contract_queue.py` — create/read/list/update/persist records
- Persist apply_executor_evidence_contract objects under configured private data path
- POST `/apply-executor-plans/{id}/evidence-contract` now persists apply_executor_evidence_contract_record
- New endpoints: GET `/apply-executor-evidence-contracts`, GET `/apply-executor-evidence-contracts/{id}`, POST `/cancel`, `/reject`, `/approve-evidence-contract-intent`
- approved_evidence_contract_intent records intent only with all safety flags false
- All records persisted as JSON files with unique IDs and timestamps
- evidence_contract_ready/not_ready/blocked contracts persisted as audit evidence
- Evidence collection, apply execution, rollback remain in future milestones

---

## 7. Current Test Baseline

As of Milestone 81F:
- **Pytest:** 1375/1375 passed, 0 failures
- **Compile:** All modules compiled successfully
- **Git safety:** Clean — no diffs on README.md, ARCHITECTURE.md, code_reviewer.py
- **Trailing whitespace:** Clean
- **Private/runtime paths:** Not tracked by git
- **Test modules:**
  - `tests/test_cognitive_loop_contract.py` — 11 end-to-end contract tests (Milestone 81B)
  - `tests/test_cognitive_loop_observability.py` — 10 loop_trace observability tests (Milestone 81C)
  - `tests/test_cognitive_loop_trace_hardening.py` — 7 loop_trace hardening tests (Milestone 81D)
  - `tests/test_apply_executor_evidence_contract.py` — 60 unit tests (Milestone 75A)
  - `tests/test_apply_executor_evidence_contract_queue.py` — ~50 unit tests (Milestone 76A)
  - `tests/test_apply_executor_plan.py` — 56 unit tests
  - `tests/test_apply_executor_contract_queue.py` — 48 unit tests
  - `tests/test_apply_executor_contract.py` — 44 unit tests
  - `tests/test_apply_execution_gate_queue.py` — 41 unit tests
  - `tests/test_apply_execution_gate_request.py` — 35 unit tests
  - `tests/test_apply_executor_plan_queue.py` — 48 unit tests (Milestone 74A)
  - `tests/test_human_authorization_queue.py` — 42 unit tests
  - `tests/test_human_apply_authorization_request.py` — existing
  - `tests/test_chat_api.py` — ~325 API integration tests (+34 for 76A)
  - Plus all modules from milestones 48-66

---

## 8. Current Runtime/Storage Paths

- **Repo root:** `/home/aether/projects/Aether`
- **Runtime data:** `/home/aether/data`
- **Summaries:** `/home/aether/summaries`
- **Private records under `/home/aether/data/private/`:**
  - `approvals/`
  - `dry_runs/`
  - `simulation_plans/`
  - `simulation_results/`
  - `verification_verdicts/`
  - `apply_gates/`
  - `human_authorizations/`
  - `apply_execution_gates/`
  - `apply_executor_contracts/`
  - `apply_executor_plans/` — persists apply_executor_plan objects (Milestone 74A)
  - `apply_executor_evidence_contracts/` — persists apply_executor_evidence_contract records (Milestone 76A)

---

## 9. Hard Safety Invariants

These invariants must hold at ALL times:

1. **approval/intent/contract/plan readiness never equals execution permission**
   - `approved_intent` does NOT authorize apply
   - `approved_execution_intent` does NOT authorize apply
   - `approved_contract_intent` does NOT authorize apply
   - `ready_for_execution_gate_review` does NOT authorize execution
   - `contract_ready` does NOT authorize execution
   - `plan_ready` does NOT authorize execution

2. **Safety flags always false:**
   - `apply_authorized` = false
   - `apply_allowed` = false
   - `execution_allowed` = false
   - `tool_execution_allowed` = false
   - `apply_executed` = false
   - `rollback_executed` = false
   - `evidence_collected` = false
   - `rollback_plan_attached` = false
   - `dry_run_execution_allowed` = false
   - `simulation_execution_allowed` = false
   - `apply_gate_execution_allowed` = false
   - `human_authorization_execution_allowed` = false
   - `apply_execution_gate_execution_allowed` = false
   - `apply_executor_contract_execution_allowed` = false
   - `apply_executor_plan_execution_allowed` = false

3. **No external actions until explicit future executor milestones:**
   - No real tool execution
   - No real apply
   - No rollback execution
   - No evidence collection
   - No identity_seed.md modification unless explicitly authorized
   - No external LLM/API calls during code milestones unless explicitly authorized

---

## 10. Next Recommended Milestone

**Status after 81F:** Complete — project ledger and architecture reconciliation committed as `761c1eff`.

**Next:** 82B — Cognitive Loop Stage Coverage Plan (not started)

**Current guidance:**
81A–81E cognitive runtime boundary and loop_trace work are stable.
No further trace-only milestones are planned unless explicitly requested.
82A complete (plan-only closure — no Build needed).

---

## 11. Prompt Rule for Future OpenCode Tasks

> "Every future OpenCode prompt must begin by instructing OpenCode to read PROGRESS.md before editing. Every future milestone must update PROGRESS.md and write a milestone summary under /home/aether/summaries/."

Also:
> "When asked to continue with 'next', use PROGRESS.md to determine the next safe milestone."

---

## 12. Current Snapshot as of Milestone 81F

**Current snapshot (81F reconciliation committed as `761c1eff`):**
- README.md and docs/ARCHITECTURE.md — reconciled in 81F to reflect persistent approval queue
- 80B–80M thin interface refactor phases — complete
- 81A–81E cognitive runtime boundary / loop_trace phases — complete
- 81F ledger reconciliation — complete
- 82A — not started
- Historical milestone notes below this section are snapshots from their respective milestones and should not override the current snapshot.

**New files added across milestones:**
- `aether/action/apply_executor_evidence_contract.py` — evidence contract builder (Milestone 75A)
- `tests/test_apply_executor_evidence_contract.py` — 60 unit tests (Milestone 75A)
- `aether/action/apply_executor_plan.py` — plan builder (Milestone 73A)
- `aether/action/apply_executor_plan_queue.py` — plan record store (Milestone 74A)
- `docs/THIN_INTERFACE_REFACTOR_PLAN.md` — thin interface refactor plan (Milestone 80A)
- `aether/action/apply_executor_contract.py` — contract builder (Milestone 71A)
- `aether/action/apply_execution_gate_queue.py` — execution gate store (Milestone 70A)
- `aether/action/apply_execution_gate_request.py` — execution gate request builder (Milestone 69A)
- `aether/action/apply_executor_evidence_contract_queue.py` — evidence contract record store (Milestone 76A)
- `tests/test_apply_executor_evidence_contract_queue.py` — ~50 unit tests (Milestone 76A)
- `tests/test_apply_executor_plan.py` — 56 unit tests
- `tests/test_apply_executor_contract_queue.py` — 48 unit tests
- `tests/test_apply_executor_contract.py` — 44 unit tests
- `tests/test_apply_execution_gate_queue.py` — 41 unit tests
- `tests/test_apply_execution_gate_request.py` — 35 unit tests
- `tests/test_cognitive_loop_contract.py` — 11 end-to-end contract tests (Milestone 81B)
- `tests/test_cognitive_loop_observability.py` — 10 loop_trace observability tests (Milestone 81C)
- `tests/test_cognitive_loop_trace_hardening.py` — 7 loop_trace hardening tests (Milestone 81D)

**Modified files:**
- `aether/interface/api_server.py` — API endpoints for all CRUD operations (updated with evidence-contract persistence and new record store endpoints)
- `tests/test_chat_api.py` — API integration tests for each milestone (+34 tests for Milestone 76A)
- `aether/core/loop.py` — added loop_trace construction (Milestone 81C)
- `aether/core/loop_trace.py` — new: loop_trace helper (Milestone 81C)
- `PROGRESS.md` — updated with each milestone entry, test baseline, and next recommendation
- `README.md` — reconciled in Milestone 81F
- `docs/ARCHITECTURE.md` — reconciled in Milestone 81F; §12.4 added in Milestone 81E

**No changes to (as of 81F):**
- `docs/CONSTITUTION.md`
- `aether/action/code_reviewer.py`
- Any self-repair chain modules
- `identity_seed.md`

### 74B — Live API Validation of Apply Executor Plan Record Store

**Status:** Complete
**Validation cases:** 15/15 passed
**Pytest suite:** 318 passed (all tests in `tests/test_chat_api.py` for Milestone 74A/B)
**Source files modified:** None (validation script only, `/tmp/milestone_74b_validation.py`, not under source control)

**Validation summary:**
- All 15 validation cases (1_plan_ready_record_creation through 15_legacy_chat_works) passed.
- The approve-plan-intent endpoint correctly transitions record status to `approved_plan_intent` while keeping all safety flags false.
- The apply_executor_plan_record remains fully safe after approval:
  - `approved_plan_intent` does **not** authorize apply, execution, or rollback
  - `evidence_collected = false`
  - `rollback_plan_attached = false`
  - `apply_authorized = false`, `apply_allowed = false`
  - `execution_allowed = false`, `tool_execution_allowed = false`, `dry_run_execution_allowed = false`, `simulation_execution_allowed = false`
  - `apply_executed = false`, `rollback_executed = false`
  - No real tool execution, no real simulation, no apply/rollback occurred
- Storage paths verified: `/home/aether/data/private/apply_executor_plans/` and all related directories exist.
- Mutation checks: cancel, reject, and re-approve-plan-intent on already-approved record preserve state (no mutation).
- Legacy /chat endpoint works as expected (validation only, no tool execution).

**PROGRESS.md update:** This entry added for Milestone 74B.

### 75B — Live API Apply Executor Evidence Contract Validation

**Status:** Complete
**Validation cases:** 11/11 passed
**Pytest suite:** 1166 passed (with 0 failures)
**Source files modified:** None (validation and api checks run on local main state)

**Validation summary:**
- All 11 Live API validation cases (POST `/apply-executor-plans/{apply_executor_plan_id}/evidence-contract`) verified successfully.
- Correctly evaluates apply_executor_plan_record through all 24 required evidence contract checks.
- Returns `evidence_contract_ready` and status `prepared` when the plan intent is approved and ready.
- All safety-critical flags (such as `apply_authorized`, `apply_allowed`, `execution_allowed`, `tool_execution_allowed`, `apply_executed`, `rollback_executed`, `evidence_collected`, `rollback_plan_attached`) remain `False` as mandated.
- Declarative `required_evidence_items`, requirements groups (pre, during, post, rollback, audit), acceptance criteria, and confirmations are fully populated but remain uncollected (`collected = false` and `collection_allowed_now = false`).
- Returns `blocked` for pending, rejected, cancelled, and not_ready plans.
- Returns `not_ready` with unresolved risks if plan payload is missing.
- Confirmed mutation-free execution of the endpoint; no records are persisted or modified.
- Legacy `/chat` endpoint and full 1166 tests continue to pass cleanly.

**PROGRESS.md update:** This entry added for Milestone 75B.

### 79A — Apply Executor Evidence Collector Contract Object 

**Status:** Complete
**Implementation:** Created builder and endpoint, validated via live API
**Files:**
- `aether/action/apply_executor_evidence_collector_contract.py` — builder
- `aether/interface/api_server.py` — added POST `/apply-executor-evidence-collection-plans/{id}/collector-contract` endpoint
- `tests/test_apply_executor_evidence_collector_contract.py` — unit tests (35/35 passed)
- `tests/test_chat_api.py` — added API tests (9/9 passed for Milestone 79A class)
 
Pipeline update:
```
... → approved_evidence_contract_intent
   → apply_executor_evidence_collection_plan (Milestone 77A)
   → apply_executor_evidence_collection_plan_record (Milestone 78A)
   → apply_executor_evidence_collector_contract (Milestone 79A) ✓
```
 
The collector contract is purely declarative — does NOT collect evidence, execute tools, authorize apply, or modify state. All safety flags remain false. All unit and API tests pass.

**PROGRESS.md update:** Milestone 79A marked complete.


### 79B — Live API Apply Executor Evidence Collector Contract Validation 

**Status:** Complete
**Validation cases:** All 18 validation cases passed
**Test results:** 
- Unit tests: 35/35 passed
- API tests: 9/9 passed
- Full pytest: 1347/1347 passed, 0 failures, 0 errors

**API mode used:** FastAPI TestClient calling live endpoints

**Validation summary:**
All 18 validation cases verified successfully:
1. Case 01: Approved collection plan intent returns `collector_contract_ready` with all expected fields correct.
2. Case 02: All `collector_contract_checks` present and passed (25 checks).
3. Case 03: `collector_boundary` safe with all fields as expected.
4. Case 04: `collector_permission_model` safe with all permissions false and future authorization required.
5. Case 05: `collector_input_requirements` and `collector_output_requirements` present with correct items.
6. Case 06: `collector_forbidden_actions` include all prohibited methods.
7. Case 07: `collector_allowed_future_actions` are descriptive only.
8. Case 08: Pending collection plan record returns blocked.
9. Case 09: Rejected collection plan record returns blocked.
10. Case 10: Cancelled collection plan record returns blocked.
11. Case 11: Not ready source plan decision returns blocked.
12. Case 12: Blocked source plan decision returns blocked.
13. Case 13: Missing ID returns blocked.
14. Case 14: Each unsafe flag blocks as expected.
15. Case 15: Endpoint does not mutate collection plan record.
16. Case 16: Endpoint does not mutate upstream records.
17. Case 17: Collector contract is not persisted.
18. Case 18: Legacy /chat endpoint works normally.

**Compile results:** All modules compiled successfully.

**Git safety results:** Clean git diff, no whitespace errors, no commits made.

**Note about future api_server.py thinning:** The api_server.py file has grown large. A future milestone should move orchestration logic from the interface layer into core/action modules to thin the interface layer. This is not part of Milestone 79B.

**79B has NOT progressed to next milestone.**

**Changes have NOT been committed.**

**Safety invariants maintained throughout:** No evidence collection performed; no apply or rollback executed; no tool execution invoked; no execution or apply authorization granted; no prohibited actions occurred.

### 80A — Thin Interface Refactor Plan

**Status:** Complete (plan only — no code refactor, no behavior change)

**Description:**
Created a structured refactor plan to thin `aether/interface/api_server.py` according to the Aether organ model. The interface layer should only route HTTP requests and return responses. All business orchestration (builder calls, record persistence, safety flag construction, timeline/graph side-effects) should move into explicit `aether/action/services/` modules.

**Deliverables:**
- `docs/THIN_INTERFACE_REFACTOR_PLAN.md` — full refactor plan with 8 phases, scope definitions, risk list, test strategy, and invariant checklist
- `/home/aether/summaries/milestone_80A_summary.txt` — milestone summary

**Plan scope:**
- Current `api_server.py` responsibility map documented (4035 lines, ~400 endpoints)
- Target service structure defined (`aether/action/services/*.py`)
- Thin interface rule defined (route → one service call → response)
- 8 refactor phases scoped (80B through 80I)
- Phase 1 (80B) scoped: Milestone 77-79 only (evidence_collection_plan, collection plan CRUD, collector_contract)
- Test strategy defined (no test changes needed, full pytest after every phase)
- Risk list with mitigations compiled (import cycles, response shape drift, safety flags)

**What was NOT changed:**
- No source code edited (`aether/interface/api_server.py`, `aether/action/*.py`, `aether/core/*.py`)
- No test files edited
- No runtime/private data modified
- No commits made

**Next milestone:** 80B — Thin Interface Refactor Phase 1

**80B has NOT been started.**


### 80B — Thin Interface Refactor Phase 1

**Status:** Complete

**Description:**
Moved Milestone 77-79 orchestration from `aether/interface/api_server.py` into `aether/action/services/collection_plan_service.py`. This is a behavior-preserving structural refactor — no endpoint paths, response shapes, or safety logic changed.

**Scope moved:**
- `POST /apply-executor-evidence-contracts/{id}/evidence-collection-plan` — evidence collection plan creation
- `GET /apply-executor-evidence-collection-plans` — list collection plan records
- `GET /apply-executor-evidence-collection-plans/{id}` — get single collection plan record
- `POST /apply-executor-evidence-collection-plans/{id}/reject` — reject
- `POST /apply-executor-evidence-collection-plans/{id}/cancel` — cancel
- `POST /apply-executor-evidence-collection-plans/{id}/approve-collection-plan-intent` — approve
- `POST /apply-executor-evidence-collection-plans/{id}/collector-contract` — collector contract creation

**Files created:**
- `aether/action/services/__init__.py` — package init
- `aether/action/services/collection_plan_service.py` — 7 service functions

**Files modified:**
- `aether/interface/api_server.py` — thinned 7 endpoints to single service calls; removed unused builder/queue imports

**Service functions created:**
1. `handle_evidence_collection_plan_create(evidence_contract_id, context)` — build + persist + response
2. `handle_list_collection_plans(status, decision, limit)` — list records
3. `handle_get_collection_plan(plan_id)` — get single record
4. `handle_reject_collection_plan(plan_id, reviewer, reason)` — reject
5. `handle_cancel_collection_plan(plan_id, reviewer, reason)` — cancel
6. `handle_approve_collection_plan_intent(plan_id, reviewer, reason, confirmations)` — approve
7. `handle_collector_contract_create(plan_id, context)` — build + response (no persist)

**Verification:**
- Focused tests: 16/16, 22/22, 35/35, 40/40 all passed
- Full pytest: 1347/1347 passed, 0 failures, 0 errors
- All modules compiled successfully
- Git diff clean (no whitespace errors)
- No runtime/private data modified

**Safety invariants maintained:**
- No evidence collection performed
- No apply or rollback executed
- No tool execution invoked
- No execution or apply authorization granted
- No prohibited actions

**Not changed:**
- No builder modules modified
- No queue modules modified
- No test files modified
- No endpoint paths changed
- No response shapes changed
- No safety logic changed

**Next recommended milestone:**
Milestone 80C — Thin Interface Refactor Phase 2 (move executor_plan + evidence_contract service extraction)

**80C has NOT been started. No commit made.**


### 80C — Thin Interface Refactor Phase 2

**Status:** Complete

**Description:**
Moved Milestone 73-76 orchestration from `aether/interface/api_server.py` into `aether/action/services/executor_plan_service.py` and `aether/action/services/evidence_contract_service.py`. This is a behavior-preserving structural refactor — no endpoint paths, response shapes, or safety logic changed.

**Scope moved:**

Executor Plan (Milestones 73-74):
- `POST /apply-executor-contracts/{id}/executor-plan` — executor plan creation
- `GET /apply-executor-plans` — list executor plan records
- `GET /apply-executor-plans/{id}` — get single executor plan record
- `POST /apply-executor-plans/{id}/cancel` — cancel
- `POST /apply-executor-plans/{id}/reject` — reject
- `POST /apply-executor-plans/{id}/approve-plan-intent` — approve

Evidence Contract (Milestones 75-76):
- `POST /apply-executor-plans/{id}/evidence-contract` — evidence contract creation
- `GET /apply-executor-evidence-contracts` — list evidence contract records
- `GET /apply-executor-evidence-contracts/{id}` — get single evidence contract record
- `POST /apply-executor-evidence-contracts/{id}/cancel` — cancel
- `POST /apply-executor-evidence-contracts/{id}/reject` — reject
- `POST /apply-executor-evidence-contracts/{id}/approve-evidence-contract-intent` — approve

**Files created:**
- `aether/action/services/executor_plan_service.py` — 6 service functions
- `aether/action/services/evidence_contract_service.py` — 6 service functions + `_build_fallback_contract` helper

**Files modified:**
- `aether/interface/api_server.py` — thinned 12 endpoints to single service calls; removed unused builder/queue imports; removed `_build_fallback_contract` helper; kept `collection_plan_service` import and request model classes

**Service functions created:**

`executor_plan_service.py`:
1. `handle_executor_plan_create(contract_id, context)` — build + persist + response
2. `handle_list_executor_plans(status, decision, limit)` — list records
3. `handle_get_executor_plan(plan_id)` — get single record
4. `handle_cancel_executor_plan(plan_id, reviewer, reason)` — cancel
5. `handle_reject_executor_plan(plan_id, reviewer, reason)` — reject
6. `handle_approve_executor_plan_intent(plan_id, reviewer, reason, confirmations)` — approve

`evidence_contract_service.py`:
1. `handle_evidence_contract_create(plan_id, context)` — build + persist + response
2. `handle_list_evidence_contracts(status, decision, limit)` — list records
3. `handle_get_evidence_contract(contract_id)` — get single record
4. `handle_cancel_evidence_contract(contract_id, reviewer, reason)` — cancel
5. `handle_reject_evidence_contract(contract_id, reviewer, reason)` — reject
6. `handle_approve_evidence_contract_intent(contract_id, reviewer, reason, confirmations)` — approve

**Verification:**
- Focused tests: 56/56, 48/48, 60/60, 22/22 all passed
- 80C API integration tests: 106/106 passed
- 80B regression tests: 16/16, 22/22, 35/35 all passed
- 80B API integration tests: 40/40 passed
- Full pytest: 1347/1347 passed, 0 failures, 0 errors
- All 9 modules compiled successfully
- Git diff clean (no whitespace errors)
- No runtime/private data modified

**Safety invariants maintained:**
- No evidence collection performed
- No apply or rollback executed
- No tool execution invoked
- No execution or apply authorization granted
- No prohibited actions

**Not changed:**
- No builder modules modified
- No queue modules modified
- No test files modified
- No endpoint paths changed
- No response shapes changed
- No safety logic changed
- 80B `collection_plan_service.py` untouched

**Next recommended milestone:**
Milestone 80D — Thin Interface Refactor Phase 3 (executor_contract + apply_execution_gate service extraction)

**80D has NOT been started. No commit made.**


### 80D — Thin Interface Refactor Phase 3

**Status:** Complete

**Description:**
Moved Milestone 69-72 orchestration from `aether/interface/api_server.py` into `aether/action/services/apply_execution_gate_service.py` and `aether/action/services/executor_contract_service.py`. This is a behavior-preserving structural refactor — no endpoint paths, response shapes, or safety logic changed.

**Scope moved:**

Apply Execution Gate (Milestones 69-70):
- `POST /human-authorizations/{id}/apply-execution-gate-request` — execution gate request creation
- `GET /apply-execution-gates` — list execution gate records
- `GET /apply-execution-gates/{id}` — get single execution gate record
- `POST /apply-execution-gates/{id}/cancel` — cancel
- `POST /apply-execution-gates/{id}/reject` — reject
- `POST /apply-execution-gates/{id}/approve-execution-intent` — approve

Executor Contract (Milestones 71-72):
- `POST /apply-execution-gates/{id}/executor-contract` — executor contract creation
- `GET /apply-executor-contracts` — list executor contract records
- `GET /apply-executor-contracts/{id}` — get single executor contract record
- `POST /apply-executor-contracts/{id}/cancel` — cancel
- `POST /apply-executor-contracts/{id}/reject` — reject
- `POST /apply-executor-contracts/{id}/approve-contract-intent` — approve

**Files created:**
- `aether/action/services/apply_execution_gate_service.py` — 6 service functions
- `aether/action/services/executor_contract_service.py` — 6 service functions

**Files modified:**
- `aether/interface/api_server.py` — thinned 12 endpoints to single service calls; removed unused builder/queue imports; kept `ApplyExecGateDecisionBody` and `HumanAuthContextBody` model classes

**Service functions created:**

`apply_execution_gate_service.py`:
1. `handle_apply_execution_gate_create(ha_id, context)` — build + persist + response
2. `handle_list_apply_execution_gates(status, decision, limit)` — list records
3. `handle_get_apply_execution_gate(gate_id)` — get single record
4. `handle_cancel_apply_execution_gate(gate_id, reviewer, reason)` — cancel
5. `handle_reject_apply_execution_gate(gate_id, reviewer, reason)` — reject
6. `handle_approve_execution_intent(gate_id, reviewer, reason, confirmations)` — approve

`executor_contract_service.py`:
1. `handle_executor_contract_create(gate_id, context)` — build + persist + response
2. `handle_list_executor_contracts(status, decision, limit)` — list records
3. `handle_get_executor_contract(contract_id)` — get single record
4. `handle_cancel_executor_contract(contract_id, reviewer, reason)` — cancel
5. `handle_reject_executor_contract(contract_id, reviewer, reason)` — reject
6. `handle_approve_contract_intent(contract_id, reviewer, reason, confirmations)` — approve

**Verification:**
- Focused tests: 35/35, 41/41, 44/44, 48/48 all passed
- 80D API integration tests: 82/82 passed
- 80C regression: 56/56, 48/48, 60/60, 22/22 all passed
- 80C API integration tests: 106/106 passed
- 80B regression: 16/16, 22/22, 35/35 all passed
- 80B API integration tests: 40/40 passed
- Full pytest: 1347/1347 passed, 0 failures, 0 errors
- All 11 modules compiled successfully
- Git diff clean (no whitespace errors)
- No runtime/private data modified

**Safety invariants maintained:**
- No evidence collection performed
- No apply or rollback executed
- No tool execution invoked
- No execution or apply authorization granted
- No prohibited actions

**Not changed:**
- No builder modules modified
- No queue modules modified
- No test files modified
- No endpoint paths changed
- No response shapes changed
- No safety logic changed
- 80B `collection_plan_service.py` untouched
- 80C `executor_plan_service.py` and `evidence_contract_service.py` untouched

**Next recommended milestone:**
Milestone 80F — Thin Interface Refactor Phase 5 (simulation_result + simulation_plan + dry_run service extraction)

**80E done — see section below. No commit made.**


### 80E — Thin Interface Refactor Phase 4

**Status:** Complete

**Description:**
Moved Milestone 63-68 orchestration from `aether/interface/api_server.py` into three new service modules. Behavior-preserving refactor — no endpoint paths, response shapes, safety logic, or queue semantics changed.

**Correction note:** An earlier iteration added 4 out-of-scope new endpoints (reject/approve-intent for verification verdicts and apply gates) and extended queue semantics. These were reverted. 80E is a strict 14-endpoint refactor only.

**Scope moved (14 endpoints):**

Verification Verdict (Milestones 63-64):
- `POST /simulation-results/{id}/verification-verdict` — verification verdict creation
- `GET /verification-verdicts` — list verification verdict records
- `GET /verification-verdicts/{id}` — get single verification verdict record
- `POST /verification-verdicts/{id}/cancel` — cancel

Apply Gate (Milestones 65-66):
- `POST /verification-verdicts/{id}/apply-gate-request` — apply gate request creation
- `GET /apply-gates` — list apply gate records
- `GET /apply-gates/{id}` — get single apply gate record
- `POST /apply-gates/{id}/cancel` — cancel

Human Authorization (Milestones 67-68):
- `POST /apply-gates/{id}/human-authorization-request` — human authorization request creation
- `GET /human-authorizations` — list human authorization records
- `GET /human-authorizations/{id}` — get single human authorization record
- `POST /human-authorizations/{id}/cancel` — cancel
- `POST /human-authorizations/{id}/reject` — reject
- `POST /human-authorizations/{id}/approve-intent` — approve intent

**Files created:**
- `aether/action/services/verification_verdict_service.py` — 4 service functions
- `aether/action/services/apply_gate_service.py` — 4 service functions
- `aether/action/services/human_authorization_service.py` — 6 service functions

**Files modified:**
- `aether/interface/api_server.py` — thinned 14 endpoints to single service calls; removed unused builder/queue imports; kept all request model classes

**Files specifically NOT modified (queue semantics unchanged):**
- `aether/action/simulation_verdict_queue.py` — reverted, no changes
- `aether/action/apply_gate_queue.py` — reverted, no changes

**Service functions created:**

`verification_verdict_service.py`:
1. `handle_verification_verdict_create(sr_id, context)` — build + persist + response
2. `handle_list_verification_verdicts(status, decision, limit)` — list records
3. `handle_get_verification_verdict(vv_id)` — get single record
4. `handle_cancel_verification_verdict(vv_id, reviewer, reason)` — cancel

`apply_gate_service.py`:
1. `handle_apply_gate_create(vv_id, context)` — build + persist + response
2. `handle_list_apply_gates(status, decision, limit)` — list records
3. `handle_get_apply_gate(ag_id)` — get single record
4. `handle_cancel_apply_gate(ag_id, reviewer, reason)` — cancel

`human_authorization_service.py`:
1. `handle_human_authorization_create(ag_id, context)` — build + persist + response
2. `handle_list_human_authorizations(status, decision, limit)` — list records
3. `handle_get_human_authorization(ha_id)` — get single record
4. `handle_cancel_human_authorization(ha_id, reviewer, reason)` — cancel
5. `handle_reject_human_authorization(ha_id, reviewer, reason)` — reject
6. `handle_approve_intent_human_authorization(ha_id, reviewer, reason, confirmations)` — approve intent

**Verification:**
- Focused builder/queue tests: 30/30, 40/40, 33/33, 29/29, 30/30, 27/27 all passed
- 80E API integration tests: 81/81 passed
- 80D regression: 82/82 passed
- 80C regression: 106/106 passed
- 80B regression: 40/40 passed
- Full pytest: 1347/1347 passed, 0 failures, 0 errors
- All 6 modules compiled successfully (3 new services + api_server.py + 3 existing)
- Git diff clean: api_server.py -311 lines; no whitespace errors
- No runtime/private data modified

**Safety invariants maintained:**
- No evidence collection performed
- No apply or rollback executed
- No tool execution invoked
- No execution or apply authorization granted
- No prohibited actions

**Not changed:**
- No builder modules modified
- No queue modules modified
- No test files modified
- No endpoint paths changed
- No response shapes changed
- No safety logic changed
- 80B `collection_plan_service.py` untouched
- 80C `executor_plan_service.py` and `evidence_contract_service.py` untouched
- 80D `apply_execution_gate_service.py` and `executor_contract_service.py` untouched

**Next recommended milestone:**
Milestone 80G — Thin Interface Refactor Phase 6 (approval + sandbox_contract service extraction)


### 80F — Thin Interface Refactor Phase 5

**Status:** Complete

**Description:**
Moved Milestone 56A-62A orchestration from `aether/interface/api_server.py` into three new service modules. Behavior-preserving refactor — no endpoint paths, response shapes, safety logic, or queue semantics changed.

**Scope moved (12 endpoints):**

Dry Run (Milestones 56A-57A):
- `POST /approvals/{approval_id}/dry-run-request` — dry-run request creation (validate + build + persist)
- `GET /dry-runs` — list dry-run records
- `GET /dry-runs/{id}` — get single dry-run record
- `POST /dry-runs/{id}/cancel` — cancel

Simulation Plan (Milestones 59A-60A):
- `POST /dry-runs/{id}/simulation-plan` — simulation plan creation (build from sandbox contract + persist)
- `GET /simulation-plans` — list simulation plan records
- `GET /simulation-plans/{id}` — get single simulation plan record
- `POST /simulation-plans/{id}/cancel` — cancel

Simulation Result (Milestones 61A-62A):
- `POST /simulation-plans/{id}/simulation-result` — simulation result creation (build + persist)
- `GET /simulation-results` — list simulation result records
- `GET /simulation-results/{id}` — get single simulation result record
- `POST /simulation-results/{id}/cancel` — cancel

**Files created:**
- `aether/action/services/dry_run_service.py` — 4 service functions
- `aether/action/services/simulation_plan_service.py` — 4 service functions
- `aether/action/services/simulation_result_service.py` — 4 service functions

**Files modified:**
- `aether/interface/api_server.py` — thinned 12 endpoints to single service calls; removed unused builder/queue imports; kept all request model classes

**Files specifically NOT modified (queue semantics unchanged):**
- `aether/action/dry_run_queue.py` — untouched
- `aether/action/simulation_plan_queue.py` — untouched
- `aether/action/simulation_result_queue.py` — untouched
- `aether/action/dry_run_request.py` — untouched
- `aether/action/simulation_plan.py` — untouched
- `aether/action/simulation_result.py` — untouched
- `aether/action/dry_run_sandbox_contract.py` — untouched

**Service functions created:**

`dry_run_service.py`:
1. `handle_dry_run_create(approval_id, requested_action, context)` — validate + build + persist + response
2. `handle_list_dry_runs(status, decision, limit)` — list records
3. `handle_get_dry_run(dr_id)` — get single record
4. `handle_cancel_dry_run(dr_id, reviewer, reason)` — cancel

`simulation_plan_service.py`:
1. `handle_simulation_plan_create(dr_id, context)` — build sandbox contract + build sim plan + persist + response
2. `handle_list_simulation_plans(status, decision, limit)` — list records
3. `handle_get_simulation_plan(sp_id)` — get single record
4. `handle_cancel_simulation_plan(sp_id, reviewer, reason)` — cancel

`simulation_result_service.py`:
1. `handle_simulation_result_create(sp_id, context)` — build + persist + response
2. `handle_list_simulation_results(status, decision, limit)` — list records
3. `handle_get_simulation_result(sr_id)` — get single record
4. `handle_cancel_simulation_result(sr_id, reviewer, reason)` — cancel

**Verification:**
- Focused builder/queue tests: 19/19, 16/16, 23/23, 18/18, 21/21, 20/20 all passed
- 80F API integration tests: 60/60 passed
- 80E regression: 81/81 passed
- 80D regression: 82/82 passed
- 80C regression: 106/106 passed
- 80B regression: 40/40 passed
- Full pytest: 1347/1347 passed, 0 failures, 0 errors
- All 12 modules compiled successfully (3 new services + api_server.py + 6 builder/queue + __init__)
- Git diff clean: no whitespace errors; 3 new untracked service files
- No runtime/private data modified

**Safety invariants maintained:**
- No evidence collection performed
- No apply or rollback executed
- No tool execution invoked
- No execution or apply authorization granted
- No simulation or dry-run execution performed
- No prohibited actions

**Not changed:**
- No builder modules modified
- No queue modules modified
- No test files modified
- No endpoint paths changed
- No response shapes changed
- No safety logic changed
- 80B `collection_plan_service.py` untouched
- 80C `executor_plan_service.py` and `evidence_contract_service.py` untouched
- 80D `apply_execution_gate_service.py` and `executor_contract_service.py` untouched
- 80E `verification_verdict_service.py`, `apply_gate_service.py`, `human_authorization_service.py` untouched
- 80F `dry_run_service.py`, `simulation_plan_service.py`, `simulation_result_service.py` untouched

**Next recommended milestone:**
Milestone 80H — Thin Interface Refactor Phase 7 (repair/guided repair + memory/tool/file service extraction plan)


### 80G — Thin Interface Refactor Phase 6

**Status:** Complete

**Description:**
Moved approval orchestration (legacy /action/approval/*, Milestone 54A /approvals/*,
Milestone 55A approval decision gate) and sandbox contract orchestration (Milestone 58A)
from `aether/interface/api_server.py` into two new service modules. Behavior-preserving
refactor — no endpoint paths, response shapes, safety logic, or queue semantics changed.

**Scope moved (14 endpoints):**

Legacy Action Approval (pre-Milestone 52A):
- `POST /action/approval/create` — create approval item with working-memory, timeline, graph
- `GET /action/approval/status` — approval queue status
- `GET /action/approval/list` — list approval items
- `GET /action/approval/{id}` — get single approval item
- `POST /action/approval/approve` — approve
- `POST /action/approval/reject` — reject
- `POST /action/approval/cancel` — cancel

Milestone 54A Approval Records:
- `GET /approvals` — list approval records
- `GET /approvals/{id}` — get single approval record
- `POST /approvals/{id}/approve` — approve
- `POST /approvals/{id}/reject` — reject
- `POST /approvals/{id}/cancel` — cancel

Milestone 55A Approval Decision Gate:
- `POST /approvals/{id}/validate-action` — validate action against approved record

Milestone 58A Sandbox Contract:
- `POST /dry-runs/{id}/sandbox-contract` — build sandbox contract from dry-run record

**Files created:**
- `aether/action/services/approval_service.py` — 14 service functions (7 legacy + 5 M54A + 1 M55A + 1 internal helper)
- `aether/action/services/sandbox_contract_service.py` — 1 service function

**Files modified:**
- `aether/interface/api_server.py` — thinned 14 endpoints to single service calls;
  removed unused imports (7 approval_queue functions, approval_decision_gate,
  dry_run_sandbox_contract builder); kept all request model classes

**Files specifically NOT modified (queue semantics unchanged):**
- `aether/action/approval_queue.py` — untouched
- `aether/action/approval_decision_gate.py` — untouched
- `aether/action/dry_run_sandbox_contract.py` — untouched
- `aether/action/dry_run_queue.py` — untouched

**Service functions created:**

`approval_service.py`:
1. `handle_action_approval_create(text, proposed, metadata)` — legacy create
2. `handle_action_approval_status()` — legacy status
3. `handle_list_action_approvals(status, limit)` — legacy list
4. `handle_get_action_approval(id)` — legacy get
5. `handle_approve_action_approval(id, reason)` — legacy approve
6. `handle_reject_action_approval(id, reason)` — legacy reject
7. `handle_cancel_action_approval(id, reason)` — legacy cancel
8. `handle_list_approvals(status, decision, limit)` — M54A list
9. `handle_get_approval(id)` — M54A get
10. `handle_approve_approval(id, reviewer, reason)` — M54A approve
11. `handle_reject_approval(id, reviewer, reason)` — M54A reject
12. `handle_cancel_approval(id, reviewer, reason)` — M54A cancel
13. `handle_validate_action(id, requested_action, context)` — M55A validate
14. `_handle_approval_record_decision(id, decision, reviewer, reason)` — internal helper
15. `_record_approval_decision(id, reason, decision)` — legacy internal helper
16. `_add_approval_working_memory_event(item, event_type)` — legacy internal helper

`sandbox_contract_service.py`:
1. `handle_sandbox_contract_create(dr_id, context)` — build sandbox contract

**Verification:**
- Focused builder/queue tests: 15/15, 15/15, 18/18, 24/24 all passed
- 80G API integration tests (Approval + SandboxContract): 31/31 passed
- 80F regression: 117/117 builder/queue + 60/60 API = 177/177
- 80E regression: 189/189 builder/queue + 81/81 API = 270/270
- 80D regression: 168/168 builder/queue + 82/82 API = 250/250
- 80C regression: 186/186 builder/queue + 106/106 API = 292/292
- 80B regression: 73/73 builder/queue + 40/40 API = 113/113
- Full pytest: 1347/1347 passed, 0 failures, 0 errors
- All 8 modules compiled successfully (2 new services + api_server.py + 5 builder/queue)
- Git diff clean: api_server.py thinned; no whitespace errors
- No runtime/private data modified

**Safety invariants maintained:**
- No evidence collection performed
- No apply or rollback executed
- No tool execution invoked
- No execution or apply authorization granted
- No sandbox or dry-run execution performed
- No simulation executed
- No prohibited actions

**Not changed:**
- No builder modules modified
- No queue modules modified
- No test files modified
- No endpoint paths changed
- No response shapes changed
- No safety logic changed
- 80B `collection_plan_service.py` untouched
- 80C `executor_plan_service.py` and `evidence_contract_service.py` untouched
- 80D `apply_execution_gate_service.py` and `executor_contract_service.py` untouched
- 80E `verification_verdict_service.py`, `apply_gate_service.py`, `human_authorization_service.py` untouched
- 80F `dry_run_service.py`, `simulation_plan_service.py`, `simulation_result_service.py` untouched

**80I — Thin Interface Refactor Phase 7 (Tool Service Extraction). No commit made.

### 80I — Thin Interface Refactor Phase 7

**Status:** Complete

**Description:**
Moved tool registry, tool plan, and tool execution orchestration from `aether/interface/api_server.py`
into three new service modules. Also moved `_record_restricted_file_access` and
`_record_self_inspection_report` helpers (used by tool execution and file/self-inspection endpoints).
Behavior-preserving refactor — no endpoint paths, response shapes, safety logic, or tool semantics changed.

**Scope moved (14 endpoints):**

Tool registry (9 endpoints):
- `GET /action/tools/status` — tool registry status
- `POST /action/tools/register` — register tool with working-memory, timeline, graph
- `POST /action/tools/seed` — seed default tools
- `GET /action/tools/list` — list tools
- `GET /action/tools/{tool_id}` — get single tool
- `POST /action/tools/search` — search tools
- `POST /action/tools/enable/{tool_id}` — enable tool
- `POST /action/tools/disable/{tool_id}` — disable tool
- `POST /action/tools/policy` — update tool policy

Tool plan (4 endpoints):
- `POST /action/tool-plan/create` — create tool invocation plan with working-memory, timeline, graph
- `GET /action/tool-plan/status` — tool planner status
- `GET /action/tool-plan/list` — list tool plans
- `GET /action/tool-plan/{plan_id}` — get single tool plan

Tool execution (4 endpoints, including 1 sandbox):
- `POST /action/tool-executor/seed-sandbox-tools` — seed sandbox tools
- `POST /action/tool-executor/execute` — execute tool with working-memory, timeline, graph, file access audit, self-inspection audit
- `GET /action/tool-executor/status` — tool executor status
- `GET /action/tool-executor/list` — list executions
- `GET /action/tool-executor/{execution_id}` — get single execution

Note: 14 endpoint groups above (some with multiple HTTP methods); 17 individual route handlers thinned.

**Files created (3):**
- `aether/action/services/tool_registry_service.py` — 9 handler functions + 4 internal helpers
  (`_add_tool_working_memory_event`, `_add_tool_graph_relationships`, `_record_tool_timeline`,
  `_change_tool_enabled`)
- `aether/action/services/tool_plan_service.py` — 4 handler functions
- `aether/action/services/tool_execution_service.py` — 5 handler functions + 2 shared record helpers
  (`record_restricted_file_access`, `record_self_inspection_report`)

**Files modified (1):**
- `aether/interface/api_server.py` — thinned 17 tool endpoints to single service calls;
  removed `_add_tool_working_memory_event`, `_add_tool_graph_relationships`, `_record_tool_timeline`,
  `_change_tool_enabled`, `_record_restricted_file_access`, `_record_self_inspection_report`;
  removed tool_registry, tool_planner, tool_executor imports (replaced with service module imports)

**Files not modified:**
- `aether/action/tool_registry.py` — untouched
- `aether/action/tool_planner.py` — untouched
- `aether/action/tool_executor.py` — untouched
- All 80B–80G service modules — untouched
- All test files — untouched

**Verification:**
- Full pytest: 1347/1347 passed, 0 failures, 0 errors
- All 5 modules compiled successfully (3 new services + api_server.py + tool_execution_service helpers)
- Git diff clean: api_server.py thinned by 247 lines (329 removed, 41 added); no whitespace errors
- No runtime/private data modified

**Safety invariants maintained:**
- No evidence collection performed
- No apply or rollback executed
- No tool execution invoked beyond existing tests
- No execution or apply authorization granted
- No sandbox or dry-run execution performed beyond existing tests
- No simulation executed
- No prohibited actions
- All tool registry, planner, executor semantics unchanged
- All audit/memory/timeline/graph side effects unchanged

**80K has NOT been started. No commit made.**

### 80K — Thin Interface Refactor Phase 8

**Status:** Complete

**Description:**
Moved memory endpoint orchestration (working, episodic, semantic, timeline, graph memory)
from `aether/interface/api_server.py` into a single service module. Behavior-preserving
refactor — no endpoint paths, response shapes, safety logic, or side-effect changes.

**Scope moved (22 endpoints):**

Working Memory (4 endpoints):
- `GET /memory/working` — working memory summary with time state
- `POST /memory/working/goal` — set working goal
- `POST /memory/working/milestone` — set working milestone
- `POST /memory/working/clear` — clear working memory

Episodic Memory (3 endpoints):
- `POST /memory/episodic/write` — write episode with working memory event
- `GET /memory/episodic/list` — list episodes
- `GET /memory/episodic/latest` — latest episode

Semantic Memory (3 endpoints):
- `POST /memory/semantic/index` — build index with working memory event
- `GET /memory/semantic/status` — semantic memory status
- `POST /memory/semantic/search` — search with working memory event

Timeline Memory (4 endpoints):
- `GET /memory/timeline/status` — timeline status
- `GET /memory/timeline/list` — list timeline events
- `GET /memory/timeline/latest` — latest timeline event
- `POST /memory/timeline/search` — search with working memory event

Graph Memory (8 endpoints):
- `GET /memory/graph/status` — graph status
- `POST /memory/graph/node` — create node with working memory event
- `POST /memory/graph/edge` — create edge with timeline + working memory side effects
- `GET /memory/graph/nodes` — list nodes
- `GET /memory/graph/edges` — list edges
- `POST /memory/graph/search` — search with working memory event
- `POST /memory/graph/seed` — seed 10 hardcoded relationships with timeline + working memory events

**Files created (1):**
- `aether/action/services/memory_service.py` — 22 handler functions
  (4 working + 3 episodic + 3 semantic + 4 timeline + 8 graph)

**Files modified (1):**
- `aether/interface/api_server.py` — thinned 22 memory endpoints to single service calls;
  removed episodic, semantic, most timeline, and most graph module imports (replaced
  with memory_service import); kept `record_event`, `search_events`, `add_edge` imports
  (still used by non-memory endpoints)

**Files not modified:**
- `aether/memory/timeline/recorder.py` — untouched
- `aether/memory/episodic/writer.py` — untouched
- `aether/memory/semantic/indexer.py` — untouched
- `aether/memory/graph/store.py` — untouched
- All 14 existing service modules (80B–80I) — untouched
- All test files — untouched
- `/chat` — untouched
- `/awaken` — untouched
- All verification, file, repair, guided, identity, root endpoints — untouched

**Verification:**
- Full pytest: 1347/1347 passed, 0 failures, 0 errors
- Focused memory test: 1/1 passed (TestApprovalRequestInApiResponse high-risk memory deletion)
- All 7 modules compiled successfully (1 new service + api_server.py + 5 memory modules)
- Git diff clean: api_server.py thinned by 166 lines (219 removed, 53 added); no whitespace errors
- No runtime/private data modified

**Safety invariants maintained:**
- No evidence collection performed
- No apply or rollback executed
- No tool execution invoked beyond existing tests
- No execution or apply authorization granted
- No sandbox or dry-run execution performed
- No simulation executed
- No prohibited actions
- All memory/timeline/graph/working-memory side effects unchanged
- /chat and /awaken behavior unchanged

**Next recommended milestone:**
- 80L — Verification Plan Service Extraction Plan

**80K complete. No commit made.**

### 80M — Thin Interface Refactor Phase 9

**Status:** Complete

**Description:**
Moved verification plan orchestration (`POST /verification/plan`) from `aether/interface/api_server.py`
into a new service module. Behavior-preserving refactor — no endpoint paths, response shapes,
request parsing, risk verification semantics, or side-effect changes.

**Scope moved (1 endpoint):**
- `POST /verification/plan` — create verification plan with working-memory, timeline, and graph side effects

**Files created (1):**
- `aether/action/services/verification_plan_service.py` — 1 handler function (`handle_create_verification_plan`)

**Files modified (1):**
- `aether/interface/api_server.py` — thinned `POST /verification/plan` endpoint to single service call;
  removed `verification_plan` import from `aether.verification.risk` (kept `classify_risk` for `/verification/classify`);
  added import of `handle_create_verification_plan` from new service module

**Files not modified:**
- `aether/verification/risk.py` — untouched
- All 17 existing service modules (80B–80K) — untouched
- All test files — untouched
- `/chat` — untouched
- `/awaken` — untouched
- `/verification/classify` — untouched
- All memory, tool, file, repair, guided, identity, root endpoints — untouched
- All pipeline/gate/approval/sandbox endpoints — untouched

**Verification:**
- Full pytest: 1347/1347 passed, 0 failures, 0 errors
- Focused risk expansion tests: 27/27 passed
- Live endpoint validation (`POST /verification/plan`, 422 on missing `text`, `/verification/classify` unchanged): passed
- Memory regression: 1/1 passed
- Tool regression: 10/10 passed
- Approval/sandbox/dry-run/simulation regression: 31/31 passed
- All 3 modules compiled successfully (1 new service + api_server.py + risk.py)
- Git diff clean: api_server.py thinned by 38 lines; no whitespace errors
- No runtime/private data modified

**Safety invariants maintained:**
- No evidence collection performed
- No apply or rollback executed
- No tool execution invoked beyond existing tests
- No execution or apply authorization granted
- No sandbox or dry-run execution performed
- No simulation executed
- No prohibited actions
- All verification/risk semantics unchanged
- All working-memory/timeline/graph side effects unchanged
- `/chat` and `/awaken` behavior unchanged

**80M complete. No commit made.**

### 81A — Cognitive Runtime Boundary Phase 1

**Status:** Complete

**Description:**
Moved runtime awakening lifecycle orchestration (`POST /awaken`) from
`aether/interface/api_server.py` into a new service module. This is the
first milestone of the Cognitive Runtime Boundary series, following the
completion of the 80A–80M Thin Interface Refactor. `/chat` is intentionally
left untouched — it is already a thin response adapter.

**Scope moved (1 endpoint):**
- `POST /awaken` — runtime awakening with identity seed loading, timeline
  "First Awakening" event search/create, and working memory awakening event

**Files created (1):**
- `aether/action/services/runtime_lifecycle_service.py` — 1 handler function
  (`handle_awaken`)

**Files modified (1):**
- `aether/interface/api_server.py` — thinned `POST /awaken` endpoint to
  single service call; removed unused `load_identity_seed` import (kept
  `identity_preview` for `/identity`)

**Files not modified:**
- `aether/core/runtime.py` — untouched
- `aether/identity/loader.py` — untouched
- `aether/identity/guard.py` — untouched
- `aether/time/clock.py` — untouched
- All 19 existing service modules (80B–80M) — untouched
- All test files — untouched
- `POST /chat` — untouched
- All identity, memory, tool, file, repair, guided, verification,
  pipeline/gate/approval/sandbox endpoints — untouched

**Verification:**
- Full pytest: 1347/1347 passed, 0 failures, 0 errors
- Focused awaken/chat API tests: 415/415 passed
- Live endpoint validation (`POST /awaken` response fields, `/chat` untouched): passed
- 80M verification regression (test_risk_expansion): 27/27 passed
- 80K memory regression: 1/1 passed
- 80I tool regression: 10/10 passed
- 80G approval/sandbox regression (4 test files): 72/72 passed
- All 6 modules compiled successfully (1 new service + api_server.py + runtime.py +
  loader.py + guard.py + clock.py)
- Git diff clean: api_server.py thinned by 49 lines; no whitespace errors
- No runtime/private data modified

**Safety invariants maintained:**
- No evidence collection performed
- No apply or rollback executed
- No tool execution invoked beyond existing tests
- No execution or apply authorization granted
- No sandbox or dry-run execution performed
- No simulation executed
- No prohibited actions
- All identity/timeline/working-memory side effects unchanged
- `POST /chat` unchanged
- `runtime.process_chat()` unchanged

**Next recommended milestone:**
- 81B — End-to-End Cognitive Loop Verification Tests Plan

**81A complete. No commit made.**


### 81B — End-to-End Cognitive Loop Contract Tests

**Status:** Complete

**Description:**
Created end-to-end contract tests for `POST /chat` to lock down the current
response shape, observable side effects, and safety invariants before any
future cognitive runtime changes. Tests-only milestone — no source code
modified.

**Scope (11 test methods / 10 test specifications):**

1. `test_chat_safe_message_returns_full_contract` — verifies all 32 response
   fields exist with correct types for safe input
2. `test_chat_empty_input_returns_error_contract` — verifies error contract
   (status="error", warnings populated, perception=None, memory/timeline not
   recorded, response_text=None, response string present)
3. `test_chat_high_risk_message_exposes_verification_and_approval_contract` —
   verifies risk_level="high", approval_required=True, approval_id, approval_request,
   approval_record present; verifies GET /approvals/{id} returns the record
4. `test_chat_tool_like_request_suggests_tool_without_execution` — verifies
   "search files" produces suggested_tool with tool_id while tool_execution_allowed
   and tool_executed remain False
5. `test_chat_safe_message_records_working_memory_events` — verifies
   memory_recorded=True, working_memory_event_count>0, GET /memory/working has
   chat_input and chat_response event types
6. `test_chat_records_timeline_event` — verifies timeline_recorded=True,
   GET /memory/timeline/list includes chat_input events
7. `test_chat_accepts_session_id_and_metadata` — verifies session_id passthrough
   in request/response
8. `test_chat_safety_invariants_for_safe_input` — verifies tool_execution_allowed,
   tool_executed, execution_allowed all False; no apply_id/rollback_id/execution_id
9. `test_chat_safety_invariants_for_high_risk_input` — same safety invariants
   for high-risk input
10. `test_awaken_then_chat_preserves_identity_contract` — verifies POST /awaken
    returns all 10 expected fields and subsequent POST /chat still has full contract
11. `test_chat_no_apply_or_rollback_side_effects` — verifies tool_executed,
    execution_allowed, tool_execution_allowed all False; no pipeline keys leaked

**Files created (1):**
- `tests/test_cognitive_loop_contract.py` — 11 test methods

**Files modified:**
- `PROGRESS.md` — added 81B entry, updated test baseline to 1358

**Verification:**
- New contract tests: 11/11 passed
- Full pytest: 1358/1358 passed, 0 failures, 0 errors
- No source code modified
- No runtime/private data modified

**Safety invariants maintained:**
- No evidence collection performed
- No apply or rollback executed
- No tool execution invoked
- No execution or apply authorization granted
- No prohibited actions

**Next recommended milestone:**
- (TBD — cognitive runtime boundary series ongoing)

**81B complete. No commit made.**


### 81C — Cognitive Loop Observability

**Status:** Complete

**Description:**
Added a response-only `loop_trace` object to `POST /chat` that provides
structured observability of the cognitive loop execution without exposing
chain-of-thought, raw model reasoning, secrets, or private data. The trace
is ephemeral (returned in the response only) and is NOT persisted to disk.

**Scope:**

1. Created `aether/core/loop_trace.py` — deterministic helper functions:
   - `generate_trace_id()` — unique per-execution identifier
   - `build_stage()` — single stage entry factory
   - `sanitize_summary()` — safe summary truncation
   - `build_loop_trace()` — assemble complete trace dict

2. Modified `aether/core/loop.py` — added trace generation, stage recording
   after each loop step, and loop_trace construction in the result dict.
   Added `loop_trace` to `_error_response` for direct-loop error cases.

3. Modified `aether/interface/api_server.py` — added optional `loop_trace`
   field to `ChatResponse` model and pass-through from loop result.
   Added `loop_trace` to the direct empty-input error response.

4. Updated `tests/test_cognitive_loop_contract.py` — added `"loop_trace"`
   to the 33-field `CHAT_RESPONSE_CONTRACT_FIELDS` list with assertions
   that it exists and has a valid `trace_id`.

5. Created `tests/test_cognitive_loop_observability.py` — 10 tests covering
   trace structure, stage names, summary safety, high-risk approval records,
   safety flag mirroring, records structure, hidden-reasoning protection,
   empty input error trace, and awaken/memory endpoint isolation.

**Loop trace fields:**
- `trace_id` — unique per execution
- `loop_version` — loop version string
- `started_at`, `completed_at` — ISO timestamps
- `duration_ms` — wall-clock elapsed time
- `status` — overall trace status
- `stages` — list of `{name, status, summary, warnings_count}`
- `safety` — `{tool_execution_allowed, tool_executed, execution_allowed, approval_required}`
- `records` — `{working_memory_event_ids, timeline_event_id, approval_id}`
- `warnings` — aggregated warnings

**Stage names recorded:**
perception, identity_integrity, time_state, working_memory,
risk_classification, tool_suggestion, thinking_policy, policy_gate,
approval_request, approval_queue, timeline_recording, response_generation

**Stage summaries are safe:**
- Structured, deterministic, derived from already-public data
- Max 120 chars (truncated via sanitize_summary)
- No newlines, no raw dict dumps, no secrets, no file paths
- No chain-of-thought, no hidden reasoning, no system prompt exposure

**Files created (2):**
- `aether/core/loop_trace.py` — ~80 lines
- `tests/test_cognitive_loop_observability.py` — 10 tests

**Files modified (3):**
- `aether/core/loop.py` — added trace construction (~+60 lines)
- `aether/interface/api_server.py` — added ChatResponse.loop_trace (~+15 lines)
- `tests/test_cognitive_loop_contract.py` — added loop_trace to contract field list (~+5 lines)

**Verification:**
- New observability tests: 10/10 passed
- Updated contract tests: 11/11 passed
- Full pytest: 1368/1368 passed, 0 failures, 0 errors
- All modules compiled successfully (5 modules)
- Git diff clean: no whitespace errors, no private/runtime files tracked

**Not changed:**
- `aether/core/runtime.py` — `process_chat()` signature unchanged
- `aether/action/services/*.py` — all service modules untouched
- `aether/identity/*.py`, `aether/perception/*.py` — untouched
- `aether/verification/*.py`, `aether/thinking/*.py` — untouched
- `aether/action/policy_gate.py`, `aether/action/approval_request.py` — untouched
- `aether/action/approval_queue.py`, `aether/action/tool_planner.py` — untouched
- `aether/memory/*.py`, `aether/time/clock.py` — untouched
- `tests/test_chat_api.py`, `tests/test_risk_expansion.py` — untouched
- `POST /awaken` — unchanged
- `POST /chat` endpoint path — unchanged
- All endpoint response fields except additive `loop_trace` — unchanged
- No persistent trace storage added
- No new endpoints added

**Safety invariants maintained:**
- No evidence collection performed
- No apply or rollback executed
- No tool execution invoked
- No execution or apply authorization granted
- No prohibited actions
- `loop_trace` is a read-only summary built after loop completion
- `loop_trace` does not influence loop behavior
- `loop_trace` does not expose chain-of-thought or hidden reasoning
- `loop_trace` is not persisted to disk

**Next recommended milestone:**
- 81D — Cognitive Loop Trace Review and Hardening Plan

**81C complete. No commit made.**


### 81D — Cognitive Loop Trace Hardening Tests

**Status:** Complete

**Description:**
Added 7 hardening tests for the loop_trace object added in 81C. These tests
verify that stage summaries do NOT leak user input text, perception normalized
text, metadata values, session_id, or raw approval record content. Tests-only
milestone — no source code modified.

**Scope (7 hardening tests):**

1. `test_loop_trace_does_not_include_user_text` — request text not in any summary
2. `test_loop_trace_does_not_include_normalized_text` — perception normalized_text not in trace
3. `test_loop_trace_does_not_include_metadata_values` — metadata values not in summaries
4. `test_loop_trace_does_not_include_session_id` — session_id not in summaries
5. `test_loop_trace_summaries_are_tightly_truncated` — each summary ≤ 120 chars
6. `test_loop_trace_stage_count_matches_expected_minimum` — ≥ 12 stages present
7. `test_loop_trace_high_risk_summary_does_not_dump_approval_record` — raw approval record not in trace

**Files created (1):**
- `tests/test_cognitive_loop_trace_hardening.py` — 7 hardening tests

**Files modified:**
- `PROGRESS.md` — added 81D entry, updated test baseline

**Verification:**
- New hardening tests: 7/7 passed
- 81C observability tests: 10/10 passed
- 81B contract tests: 11/11 passed
- Full pytest: 1375/1375 passed, 0 failures, 0 errors
- No source code modified

**Not changed:**
- `aether/core/loop_trace.py` — no code changes
- `aether/core/loop.py` — no code changes
- `aether/interface/api_server.py` — no code changes
- `tests/test_cognitive_loop_contract.py` — no modifications
- `tests/test_cognitive_loop_observability.py` — no modifications
- All endpoint paths — unchanged
- All response fields — unchanged
- No new endpoints added
- No trace persistence added

**Safety invariants maintained:**
- All safety invariants from 81C remain intact
- No source code modified
- No behavioral impact

**Next recommended milestone:**
- 81E or higher — cognitive runtime feature work (trace is now hardened and safe)

**81D complete. No commit made.**


### 81E — Cognitive Loop Trace Documentation

**Status:** Complete

**Description:**
Created comprehensive documentation for the `loop_trace` object added in 81C
and hardened in 81D. Docs-only milestone — no source code or tests modified.

**Scope:**
1. Created `docs/COGNITIVE_LOOP_TRACE.md` — full reference document covering:
   - Purpose, scope, safety/privacy/chain-of-thought boundaries
   - Current contract (all fields, types, meanings)
   - Current stage names (12 stages with descriptions)
   - Storage decision (response-only, not persisted)
   - Relationship to Aether execution loop
   - Developer extension rules
   - Test coverage
   - Future work
2. Added `§12.4 Cognitive Loop Trace` reference section to `docs/ARCHITECTURE.md`
   linking to the new document

**Files created (1):**
- `docs/COGNITIVE_LOOP_TRACE.md` — ~300 lines

**Files modified (2):**
- `docs/ARCHITECTURE.md` — added §12.4 reference section
- `PROGRESS.md` — added 81E entry, updated test baseline

**Documentation assertions:**
- `loop_trace` is not chain-of-thought
- `loop_trace` is not hidden reasoning
- `loop_trace` is response-only, not persisted
- Full Act/Observe/Verify/Critic/Repair/Learn cycle is NOT implemented
- Future work section lists only hypothetical possibilities

**Verification:**
- 81D hardening tests: 7/7 passed
- 81C observability tests: 10/10 passed
- 81B contract tests: 11/11 passed
- Full pytest: 1375/1375 passed, 0 failures, 0 errors
- All modules compiled successfully

**Not changed:**
- No source files modified
- No test files modified
- No endpoint paths changed
- No response fields changed
- No trace contract changed
- No trace persistence added
- No chain-of-thought exposure claimed

**Safety invariants maintained:**
- All safety invariants from 81C-81D remain intact
- No source code modified
- No behavioral impact
- Documentation is accurate and does not claim unimplemented capabilities

**Next recommended milestone:**
- 81F — Cognitive Loop Trace Usage Review Plan (or higher-level cognitive runtime feature work)

**81E complete. No commit made.**


### 81F — Project Ledger and Architecture Reconciliation

**Status:** Complete

**Type:** Documentation reconciliation — no source code or tests modified.

**Description:**
Reconciled PROGRESS.md, README.md, docs/ARCHITECTURE.md, and
docs/THIN_INTERFACE_REFACTOR_PLAN.md to match actual Git/tag/test state.
Fixed stale metadata, incorrect milestone statuses, arithmetic errors, and
contradictions about the persistent approval queue.

**Fixes applied:**

PROGRESS.md:
- "Last updated" header: 81C → 81F
- Pipeline maturity description updated to reflect thin interface refactor
  and cognitive runtime boundary completion
- Section header "71-75" → "71-76" (76A was listed but excluded from range)
- 76A status: "In Progress" → "Complete" (confirmed by tag
  `milestone-76-apply-executor-evidence-contract-record-store`)
- 76A test count: "~146 (50 + 34)" → "~84 (50 + 34)" (corrected arithmetic)
- "Next Recommended Milestone": removed 82A reference (not yet authorized);
  set to TBD

README.md:
- "No persistent approval queue exists yet" → clarified that persistent
  approval queue exists via `aether/action/approval_queue.py` and
  `aether/action/services/approval_service.py`

docs/ARCHITECTURE.md:
- Two stale "No persistent approval queue" statements corrected to
  describe the existing persistent queue

docs/THIN_INTERFACE_REFACTOR_PLAN.md:
- "Next: Milestone 80B" → "All 80B-80M refactor phases complete"

**Verification:**
- 81D hardening tests: 7/7 passed
- 81C observability tests: 10/10 passed
- 81B contract tests: 11/11 passed
- Full pytest: 1375/1375 passed, 0 failures, 0 errors

**Not changed:**
- No source files modified
- No test files modified
- No docs modified beyond the four reconciled files
- No endpoint paths changed
- No response fields changed
- No trace persistence added
- No chain-of-thought exposure

**Safety invariants maintained:**
- All safety invariants from 81C–81E remain intact
- No source code modified
- No behavioral impact

**Next recommended milestone:**
- TBD — directed by project owner

**81F reconciliation committed as `761c1eff`. Consistency patch committed as `f169a98`.**


### 82A — /chat Interface Boundary and Service Extraction Plan

**Status:** Complete

**Type:** Architectural decision / plan-only closure — no source code or tests modified.

**Description:**
Analyzed whether POST /chat should remain in `aether/interface/api_server.py`
as an interface adapter, or be extracted into a dedicated service/module.

**Decision:** Keep `/chat` in `api_server.py` as an intentional interface adapter.
No source refactor needed.

**Reason:**
- `/chat` is mostly request/response adaptation (87 lines: input validation,
  one call to `runtime.process_chat()`, response mapping).
- `runtime.process_chat()` is already the true cognitive boundary — the endpoint
  performs no cognitive logic.
- `loop.run_core_chat_loop()` is the real core loop boundary — all reasoning,
  perception, identity, risk, policy, and approval orchestration lives there.
- Extracting `/chat` would add indirection (new service file, new import, new
  call chain) without meaningful benefit — the endpoint is already thin.
- `ChatRequest` and `ChatResponse` remain interface-layer models colocated
  with their single endpoint.

**Options evaluated:**
- Option A: Keep as-is (recommended and adopted)
- Option B: Extract response mapping into `aether/action/services/chat_service.py`
- Option C: Extract response mapping into `aether/interface/services/chat_response_service.py`
- Option D: Move into separate APIRouter module `aether/interface/cognitive_api.py`
- Option E: Extract schemas into `aether/interface/schemas/chat.py`
- Option F: Skip refactor, move to next cognitive capability

**Not changed:**
- No source files modified
- No test files modified
- No endpoint paths changed
- No response contract changed
- No `loop_trace` behavior changed
- No trace persistence added
- No tool execution added
- No evidence collection added
- No apply/rollback added

**Verification:**
- 81B contract tests: 11/11 passed
- 81C observability tests: 10/10 passed
- 81D hardening tests: 7/7 passed
- Full pytest: 1375/1375 passed, 0 failures, 0 errors

**Safety invariants maintained:**
- All safety invariants from 81C–81E remain intact
- No source code modified
- No behavioral impact

**Next recommended milestone:**
- 82B — Cognitive Loop Stage Coverage Plan

**82B status:** Not started

**82A complete. No commit made.**
