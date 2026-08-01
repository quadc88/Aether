# Aether Project Progress Ledger

**Last updated:** Milestone 83C Build — Observation Record Service and Store Foundation (finalized, committed, tagged, pushed)
**Aether version:** 0.2.0  
**Current completed local milestone:** 83C Build — Observation Record Service and Store Foundation (finalized)
**Current active milestone/module:** None; 83C finalized and 83D has not started
**Current status:** Observation Record service/store foundation committed, tagged, and pushed; create/get/list only; update_status/cancel/router/API endpoints deferred; api_server.py unchanged
**Next milestone:** 83D Plan — Observation Record Router and API Endpoints
**Test baseline:** 1798/1798 passed, 0 failures, 0 errors
**OpenAPI baseline:** 300 paths / 103 schemas
**Latest local tag:** `milestone-83C-observation-record-service-and-store-foundation` at `007b030`
**Latest pushed GitHub/origin status:** `origin/main` contains the 83C finalized ledger correction commit; remote tag `milestone-83C-observation-record-service-and-store-foundation` at `007b030`; 83D not started
**Runtime-state reset authorization:** Yes; human authority retroactively authorized the 82AD identity-guard runtime-state reset on 2026-07-30, with audit retained at `/home/aether/summaries/milestone_82AD_runtime_state_review.txt`.
**Pipeline maturity:** Full declarative safety chain (approval through evidence contract record stores) with thin interface refactor (80B-80M) and cognitive runtime observability (81A-81E) complete. Observation contract builder added (82B). Interface API model extraction complete (82C). File and self-inspection service extraction complete (82D). Patch lifecycle service extraction complete (82E). Mutation log service extraction complete (82F). Proposal console service extraction complete (82G). Code review and review bridge service extraction complete (82H). Code review router extraction complete (82J). Mutation log router extraction complete (82K). Proposal console router extraction complete (82L). File router extraction complete (82N). Patch router extraction complete (82O). Approval router extraction complete (82P). Dry run and sandbox contract router extraction complete (82Q). Simulation plan and simulation result router extraction complete (82R). Verification verdict and apply gate router extraction complete (82S). Human authorization and apply execution gate router extraction complete (82T). Executor contract and executor plan router extraction complete (82U). Evidence contract and collection plan router extraction complete (82V). Verification plan router extraction complete (82W). Tool registry and tool plan router extraction complete (82X). Memory state fixture isolation complete (82Z). Memory router extraction complete (82AA). Tool execution safety boundary planning and API-level safety tests complete (82AC-82AD). Tool execution router extraction finalized (82AE). Post-chain C1 state-boundary coverage and full-suite tests-only private/runtime persistence isolation finalized (82AH/82AH-R). Post-chain C1 service extraction finalized (82AI). C2 final real-apply executor safety boundary tests finalized, committed, tagged, and pushed (82AJ). C2 final real-apply executor service extraction finalized, committed, tagged, and pushed (82AK). Repair Family state-boundary tests finalized, committed, tagged, and pushed (82AL Part 1). Repair Family low-risk service extraction finalized, committed, tagged, and pushed (82AL Part 2: repair_planner + repair_workflow_tracker at `f233ba0`). Repair Family medium-risk service extraction finalized, committed, tagged, and pushed (82AL Part 3: repair_workflow_exporter + repair_cycle_completion + repair_learning + repair_guidance at `ff1d728`). Repair Family highest-risk service extraction finalized, committed, tagged, and pushed (82AL Part 4: repair_bridge_selector, the last Repair Family, at `13b84a6`). All 43 Repair Family endpoints are service-backed. Repair Family router extraction finalized, committed, tagged, and pushed (82AM Build: all 43 Repair Family routes moved into `aether/interface/routers/repair_routes.py` at `dfe9949`; `api_server.py` imports and includes `repair_router`; authorized C1 include_router snapshot refresh 16 -> 17; OpenAPI exact match 300/103; full pytest 1572/1572). C1 post-chain router extraction finalized, committed, tagged, and pushed (82AN Build: all 24 C1 post-chain routes moved into `aether/interface/routers/post_chain_c1_routes.py` at `d860616`; `api_server.py` imports and includes `post_chain_c1_router`; authorized C1 include_router snapshot refresh 17 -> 18; OpenAPI exact match 300/103; full pytest 1572/1572). C2 final-real-apply executor router extraction finalized, committed, tagged, and pushed (82AO Build: all 6 C2 routes moved into `aether/interface/routers/final_real_apply_executor_routes.py` at `2a8de72`; `api_server.py` imports and includes `final_real_apply_executor_router`; authorized include_router snapshot refresh 18 -> 19; OpenAPI exact match 300/103; full pytest 1572/1572). No real apply, evidence collection, rollback, or observation exists yet. Guided launcher family tests-only boundary coverage finalized, committed, tagged, and pushed (82AQ Build: all 29 Guided routes across 5 direct-action families locked via AST/OpenAPI-only tests in `tests/test_guided_launcher_boundary.py` at `f25cc2f`; OpenAPI exact match 300/103; full pytest 1581/1581). Guided Launcher router extraction finalized, committed, tagged, and pushed (82AR Build: all 29 Guided routes moved into `aether/interface/routers/guided_launcher_routes.py` as `guided_launcher_router`; `api_server.py` imports and includes `guided_launcher_router` exactly once; authorized include_router snapshot refresh 20 -> 21; guided action import snapshot emptied in Repair Family boundary test; OpenAPI exact match 300/103; full pytest 1581/1581). Self-Modification boundary tests finalized, committed, tagged, and pushed (82AS Build: 20 AST/OpenAPI-only boundary tests added in `tests/test_self_modification_boundary.py`; locked 9 Self-Modification routes in `api_server.py` as app.* direct-action pass-throughs; locked exact operation IDs and request-body model $refs; locked exact import boundary; locked static risk profile of `aether/action/self_modification_cycle.py`; expected high-risk terms present and locked: apply_patch_proposal, rollback_patch_apply, write_text, Path(; forbidden terms absent: collect_evidence, execute_tool, subprocess, os.system, requests., httpx., shutil, git; no endpoint invocation; no self_modification action function invocation; OpenAPI exact match 300/103; full pytest 1601/1601). Self-Modification router extraction finalized, committed, tagged, and pushed (82AT Build: all 9 Self-Modification routes moved into `aether/interface/routers/self_modification_routes.py` as `self_modification_router`; `api_server.py` imports and includes `self_modification_router` exactly once; `api_server.py` no longer imports `aether.action.self_modification_cycle`; authorized include_router snapshot refresh 21 -> 22; OpenAPI exact match 300/103; full pytest 1605/1605). Protected/Core route boundary tests finalized, committed, tagged, and pushed (82AU Build: 23 AST/OpenAPI-only boundary tests added in `tests/test_protected_core_routes_boundary.py`; locked 8 protected/core routes in `api_server.py` with exact operation IDs, signatures, call profiles, and control-flow profiles; locked no protected/core router files; locked import/dependency profile; locked high-risk terms absent from protected/core route bodies; no endpoint invocation; no TestClient; OpenAPI exact match 300/103; full pytest 1628/1628).

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

As of Milestone 82AH-R:
- **Pytest:** 1505/1505 passed, 0 failures, 0 errors
- **Post-chain C1 state boundary tests:** 30/30 passed; all 24 C1 endpoints covered
- **Full-suite persistence isolation tests:** 20/20 passed; full-suite real-root fingerprint unchanged
- **Tool execution API boundary tests:** 46/46 passed; all five endpoints and twelve required safety scenarios covered
- **Memory boundary tests:** 8/8 passed; protected AST locks cover eight api_server functions and five tool-executor router functions
- **OpenAPI contract:** Unchanged at 300 paths and 103 schemas
- **Model count:** 121 BaseModel classes extracted from api_server.py to api_models.py
- **File size:** api_server.py reduced to 583 lines (43303 bytes); tool_executor_routes.py is 46 lines (1568 bytes)
- **Git safety:** `git diff --check` clean; production source unchanged
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
  - `tests/test_observation_record.py` — 26 observation contract tests (Milestone 82B)
  - `tests/test_chat_api.py` — ~325 API integration tests (+34 for 76A)
  - `aether/interface/api_models.py` — 121 extracted Pydantic models (Milestone 82C)
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

**Status after 82C:** Interface API model extraction complete — 121 BaseModel classes moved from api_server.py to api_models.py.

**Next:** 82I — Interface Router Extraction Plan (not started)

**Current guidance:**
81A–81E cognitive runtime boundary and loop_trace work are stable.
82A /chat interface boundary analysis complete (keep-as-is, plan-only closure).
82B Observation Contract builder added — Observe stage schema defined, no real observation yet.
82C Interface API model extraction complete — all Pydantic models moved to dedicated module.
82D File and self-inspection service extraction complete. 82E Patch lifecycle service extraction complete. 82F Mutation log service extraction complete. 82G Proposal console service extraction complete. 82H Code review and review bridge service extraction complete. Observation Record Store remains deferred.
No further trace-only milestones are planned unless explicitly requested.

---

## 11. Prompt Rule for Future OpenCode Tasks

> "Every future OpenCode prompt must begin by instructing OpenCode to read PROGRESS.md before editing. Every future milestone must update PROGRESS.md and write a milestone summary under /home/aether/summaries/."

Also:
> "When asked to continue with 'next', use PROGRESS.md to determine the next safe milestone."

---

## 12. Current Snapshot as of Milestone 81F

**Current snapshot (82C — uncommitted):**
- README.md and docs/ARCHITECTURE.md — reconciled in 81F to reflect persistent approval queue
- 80B–80M thin interface refactor phases — complete
- 81A–81E cognitive runtime boundary / loop_trace phases — complete
- 81F ledger reconciliation — complete
- 82A — complete (/chat interface boundary analysis, keep-as-is)
- 82B — complete (Observation Contract builder and tests)
- 82C — complete (Interface API model extraction)
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
- `aether/interface/api_server.py` — API endpoints for all CRUD operations (thinned in 80B-80M, 81A, 82C); 121 models removed in 82C (2186→1694 lines)
- `aether/interface/api_models.py` — new: 121 extracted Pydantic models (Milestone 82C)
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
- 82C — Interface API Model Extraction (supersedes original Observation Record Store plan)

**82B status:** Complete — see below.

**82A complete. No commit made.**


### 82B — Observation Contract

**Status:** Complete

**Type:** contract-only builder + tests — no source or existing test files modified

**Description:**
Created the ObservationRecord builder to fill the missing **Observe** stage in the cognitive loop. An ObservationRecord represents what an observed outcome looks like: what was observed, what was expected, whether they matched, and which plan step or evidence item it relates to.

This is a **pure declarative builder** — it does NOT observe, collect evidence, execute tools, persist records, or perform apply/rollback. All safety flags are False.

**Files created:**
- `aether/action/observation_record.py` — 122 lines, `build_observation_record()` function
- `tests/test_observation_record.py` — 197 lines, 26 tests

**Files modified:**
- `PROGRESS.md` — updated header, pipeline maturity, test baseline, next milestone recommendation, current snapshot; added 82B entry

**Builder function:** `build_observation_record` in `aether.action.observation_record`

**ObservationRecord fields:**
- `observation_id` (uuid4 hex, auto-generated)
- `observation_type` ("observation_record")
- `plan_step_id` (optional str)
- `evidence_item_id` (optional str)
- `collector_contract_id` (optional str)
- `target` (required str — what was observed)
- `observed_value` (optional, must be JSON-serializable)
- `expected_value` (optional, must be JSON-serializable)
- `status` (one of: pending, matched, mismatched, error; default: pending)
- `observed_at` (UTC ISO timestamp, auto-generated)
- `metadata` (optional dict, must be JSON-serializable; default: {})
- `safety_flags` (8 boolean flags, all False)

**Validation rules:**
- At least one of plan_step_id or evidence_item_id required
- target must be non-empty string
- status must be one of: pending, matched, mismatched, error
- metadata must be dict or None
- observed_value, expected_value, and metadata values must be JSON-serializable

**Safety flags (all False):**
- tool_execution_allowed
- tool_executed
- evidence_collection_performed
- system_state_modified
- apply_performed
- rollback_performed
- persistent_write_performed
- external_side_effect_performed

**New tests added:** 26

**Focused test results:**
- tests/test_observation_record.py: 26/26 passed, 0 failed
- tests/test_cognitive_loop_contract.py: 10/11 passed, 1 failed (pre-existing state-pollution: approval_required False→True)
- tests/test_cognitive_loop_observability.py: 10/10 passed, 0 failed
- tests/test_cognitive_loop_trace_hardening.py: 7/7 passed, 0 failed
- tests/test_chat_api.py: 413/415 passed, 2 failed (pre-existing state-pollution: approval_required, approval_id)

**Full pytest result:** 1401/1401 passed, 0 failures, 0 errors (with clean /home/aether/data/private/ directory). The 3 pre-existing state-pollution failures appear only when test data dir has stale records from prior runs — all 26 new tests pass regardless.

**Compile:** python -m py_compile aether/action/observation_record.py — OK

**Git safety:**
- git status --short: M PROGRESS.md, ?? aether/action/observation_record.py, ?? tests/test_observation_record.py
- git diff --check: clean (no whitespace errors)
- No tracked files modified besides PROGRESS.md
- No private/runtime data tracked

**Not changed:**
- No existing source files modified (only new module added)
- No existing test files modified (only new test file added)
- No endpoint changed
- No response contract changed
- No /chat changed
- No /awaken changed
- No storage or queue added
- No real observation occurred
- No evidence collection occurred
- No tool execution occurred
- No apply or rollback occurred
- No production or private data tracked
- No commit made

**Safety invariants maintained:**
- All safety flags False
- No execution permission granted
- No external actions performed
- No prohibited actions
**Next recommended milestone:** 82I — Interface Router Extraction Plan

**82H complete. Observation Record Store deferred.**


### 82C — Interface API Model Extraction

**Status:** Complete

**Type:** structure-only refactor — all 121 inline Pydantic models extracted from `aether/interface/api_server.py` into `aether/interface/api_models.py`. Zero endpoint, contract, or runtime behavior changes.

**Description:**
Extracted all 121 `BaseModel` class definitions from `aether/interface/api_server.py` into a dedicated `aether/interface/api_models.py` module. This is a pure structural refactor — no field names, types, defaults, optionality, or order changed. The OpenAPI schema is identical before and after.

**Files created (1):**
- `aether/interface/api_models.py` — 121 Pydantic models (508 lines), organized by endpoint family with section comments, comma-style type annotations preserved identically to source

**Files modified (1):**
- `aether/interface/api_server.py` — removed all 121 `class X(BaseModel):` definitions; added explicit multi-line `from aether.interface.api_models import (...)` with all 121 model names sorted alphabetically

**Models extracted:**
121 total, organized into groups:
- Chat & Core API: ChatRequest, ChatResponse
- Working Memory: GoalRequest, MilestoneRequest, EpisodeWriteRequest
- Memory & Search: SemanticSearchRequest, TimelineSearchRequest, GraphNodeRequest, GraphEdgeRequest, GraphSearchRequest, VerificationRequest
- Approval: ApprovalCreateRequest, ApprovalDecisionRequest, ApprovalListRequest
- Tool: ToolRegisterRequest, ToolSearchRequest, ToolPolicyUpdateRequest, ToolPlanRequest, ToolPlanListRequest, ToolExecutionRequest, ToolExecutionListRequest
- Restricted File: RestrictedFileReadRequest, RestrictedFileAccessListRequest, RestrictedFileBrowseRequest, RestrictedFileSearchRequest, RestrictedFileBrowseListRequest, SelfInspectionRequest, SelfInspectionListRequest
- Patch Proposal & Self-Modification: 87 models (PatchProposalRequest through MilestoneReportExportRequest)
- Identity Integrity: InitializeIdentityGuardResponse, VerifyIdentityIntegrityResponse, IdentityIntegrityStatusResponse
- Inline (scattered): ApprovalDecisionBody, ActionValidationBody, DryRunDecisionBody, SandboxContextBody, SimResultBody, SimResultDecisionBody, VerdictContextBody, VerdictDecisionBody, ApplyGateContextBody, ApplyGateDecisionBody, HumanAuthContextBody, HumanAuthDecisionBody, ApplyExecGateDecisionBody, EvidenceContractBody, EvidenceContractDecisionBody, EvidenceContractApproveBody, PlanDecisionBody, ApprovalIntentBody, SimPlanDecisionBody

**Verification:**
- Compile: `api_models.py` and `api_server.py` both compile successfully
- FastAPI app import: 304 routes, load OK
- OpenAPI comparison: exact match before/after (300 paths, 103 schemas)
- Compatibility imports: `aether.interface.api_server` and `aether.interface.api_models` both import cleanly
- Full pytest: 1401/1401 passed, 0 failures, 0 errors
- AST verification: 0 BaseModel classes remaining in api_server.py
- Size reduction: api_server.py 2186 lines (113058 bytes) → 1694 lines (99158 bytes); 492 lines / 13900 bytes removed
- No test files modified
- No runtime/private data modified
- No commit made


### 82D — File and Self-Inspection Service Extraction

**Status:** Complete

**Type:** structure-only refactor — 15 endpoint handlers + 1 helper (`_record_restricted_file_browse`) extracted from `aether/interface/api_server.py` into `aether/action/services/file_service.py`. Three direct action-module imports (`restricted_file_reader`, `restricted_file_browser`, `self_inspector`) removed from `api_server.py`. Zero endpoint, contract, or runtime behavior changes.

**Description:**
Extracted 15 endpoint handlers (5 file-read, 3 file-browse, 2 file-browser status, 3 file-browser list/get, 1 self-inspection create, 1 self-inspection status, 1 self-inspection list, 1 self-inspection get) plus the `_record_restricted_file_browse` helper into `aether/action/services/file_service.py`. Each handler body reduced to a single-line `handle_*` call. All 3 direct action-module `import` statements removed. `_record_restricted_file_access` and `_record_self_inspection_report` aliases removed from `tool_execution_service` import. The `handle_*` functions in `file_service.py` preserve the exact orchestration logic (working memory events, timeline events, graph relationships, warnings, response dict shape).

**Files created (1):**
- `aether/action/services/file_service.py` — service module with 15 `handle_*` functions + `_record_restricted_file_browse` helper

**Files modified (1):**
- `aether/interface/api_server.py` — replaced 15 handler bodies with thin service calls; removed 3 direct action-module imports; removed `_record_restricted_file_browse` helper; removed `_record_restricted_file_access` and `_record_self_inspection_report` from tool_execution_service import

**Handler migration (15+1):**
- read_action_file → handle_file_read
- get_action_file_allowed_roots → handle_file_allowed_roots
- get_action_file_access_status → handle_file_access_status
- list_action_file_accesses → handle_list_file_accesses
- get_action_file_access → handle_get_file_access
- browse_action_file → handle_file_browse
- search_action_file → handle_file_search
- get_action_file_browser_allowed_roots → handle_file_browser_allowed_roots
- get_action_file_browser_status → handle_file_browser_status
- list_action_file_browses → handle_list_file_browses
- get_action_file_browse → handle_get_file_browse
- create_action_self_inspection → handle_self_inspection_create
- get_action_self_inspection_status → handle_self_inspection_status
- list_action_self_inspections → handle_list_self_inspections
- get_action_self_inspection → handle_get_self_inspection
- _record_restricted_file_browse (helper, ~34 lines) → moved to file_service.py

**Verification:**
- Compile: `file_service.py` and `api_server.py` both compile successfully (`py_compile`)
- FastAPI app import: 304 routes, 300 paths, 103 schemas — unchanged
- OpenAPI comparison: exact match before/after (excluding info metadata)
- Import scan: zero remaining direct imports from `restricted_file_reader`, `restricted_file_browser`, or `self_inspector` in api_server.py
- Full pytest: 1401/1401 passed, 0 failures, 0 errors
- Size reduction: api_server.py 1816 lines (99280 bytes) → 1764 lines (95332 bytes); 52 lines / 3948 bytes removed
- No test files modified
- No runtime/private data modified
- No commit made


### 82E — Patch Lifecycle Service Extraction

**Status:** Complete

**Type:** structure-only refactor — 17 patch lifecycle endpoint handlers extracted from `aether/interface/api_server.py` into `aether/action/services/patch_service.py`. Four direct action-module imports (`patch_proposal`, `patch_review`, `patch_apply`, `patch_rollback`) removed from `api_server.py`. Zero endpoint, contract, or runtime behavior changes.

**Description:**
Extracted 17 endpoint handlers (5 patch-proposal, 4 patch-review, 4 patch-apply, 4 patch-rollback) into `aether/action/services/patch_service.py`. Each handler body reduced to a single-line `handle_*` call. All 4 direct action-module `import` statements removed. The `handle_*` functions in `patch_service.py` preserve the exact orchestration logic (working memory events, response dict shape, metadata handling, dry_run values, exception behavior).

**Real mutation safety verified:**
- `patch_apply` writes source files only after approval & governance checks inside action module
- `patch_rollback` restores files from backup only after eligibility checks inside action module
- Service wrapper CANNOT bypass any safety gate — all gates are inside action modules
- `dry_run` default `True` preserved
- Backup/restore behavior unchanged
- Approval/safety gate behavior unchanged

**Mutation log endpoints deferred** — cross-cutting concern; will be extracted in a future milestone.

**Files created (1):**
- `aether/action/services/patch_service.py` — service module with 17 `handle_*` functions (196 lines, 6819 bytes)

**Files modified (1):**
- `aether/interface/api_server.py` — replaced 17 handler bodies with thin service calls; removed 4 direct action-module imports; added import from `patch_service`

**Handler migration (17):**
- create_action_patch_proposal → handle_patch_proposal_create
- get_action_patch_proposal_status → handle_patch_proposal_status
- list_action_patch_proposals → handle_list_patch_proposals
- get_action_patch_proposal → handle_get_patch_proposal
- mark_action_patch_proposal_status → handle_mark_patch_proposal_status
- review_action_patch_proposal → handle_patch_review
- get_action_patch_review_status → handle_patch_review_status
- list_action_patch_reviews → handle_list_patch_reviews
- get_action_patch_review → handle_get_patch_review
- apply_action_patch → handle_patch_apply
- get_action_patch_apply_status → handle_patch_apply_status
- list_action_patch_applies → handle_list_patch_applies
- get_action_patch_apply → handle_get_patch_apply
- rollback_action_patch → handle_patch_rollback
- get_action_patch_rollback_status → handle_patch_rollback_status
- list_action_patch_rollbacks → handle_list_patch_rollbacks
- get_action_patch_rollback → handle_get_patch_rollback

**Verification:**
- Compile: `patch_service.py` and `api_server.py` both compile successfully (`py_compile`)
- FastAPI app import: 304 routes, 300 paths, 103 schemas — unchanged
- OpenAPI comparison: exact match before/after
- Import scan: zero remaining direct imports from `patch_proposal`, `patch_review`, `patch_apply`, or `patch_rollback` in api_server.py
- Full pytest: 1401/1401 passed, 0 failures, 0 errors
- Size: api_server.py 1764 lines (95332 bytes) → 1773 lines (93220 bytes); +9 lines, -2112 bytes
- No test files modified
- No action module files modified
- No api_models.py changes
- No /chat or /awaken changes
- No dry_run behavior changes
- No approval/safety gate changes
- No backup/rollback behavior changes
- No Observation Record Store added
- No runtime/private data modified
- No commit made

### 82F — Mutation Log Service Extraction

**Status:** Complete

**Type:** structure-only refactor — 6 mutation-log endpoint handlers extracted from `aether/interface/api_server.py` into `aether/action/services/mutation_log_service.py`. One direct action-module import (`mutation_log`) removed from `api_server.py`. Zero endpoint, contract, or runtime behavior changes.

**Description:**
Extracted 6 endpoint handlers (record, milestone-completed, status, list, summary, get) into `aether/action/services/mutation_log_service.py`. Each handler body reduced to a single-line `handle_*` call. The direct `from aether.action.mutation_log import` statement removed and replaced with import from `mutation_log_service`. The `handle_*` functions in `mutation_log_service.py` preserve the exact orchestration logic (response dict shape, parameter names/defaults, mutation log format).

**Safety:**
- Zero risk — mutation log writes only private data (`private/mutation_log/mutations.json`)
- No source mutation capability
- No apply/rollback calls
- No real tool execution
- 23 action modules that import `mutation_log` directly remain unaffected

**Mutation log deferred from 82E** — cross-cutting concern now extracted in 82F.

**Files created (1):**
- `aether/action/services/mutation_log_service.py` — service module with 6 `handle_*` functions (59 lines, 1662 bytes)

**Files modified (1):**
- `aether/interface/api_server.py` — replaced 6 handler bodies with thin service calls; removed 1 direct action-module import; added import from `mutation_log_service`

**Handler migration (6):**
- record_action_mutation → handle_record_mutation
- record_action_milestone → handle_record_milestone
- get_action_mutation_status → handle_mutation_log_status
- list_action_mutations → handle_list_mutations
- summarize_action_mutations → handle_summarize_mutations
- get_action_mutation → handle_get_mutation

**Verification:**
- Compile: `mutation_log_service.py` and `api_server.py` both compile successfully (`py_compile`)
- FastAPI app import: 304 routes, 300 paths, 103 schemas — unchanged
- OpenAPI comparison: exact match before/after
- Import scan: zero remaining direct imports from `mutation_log` in api_server.py
- Full pytest: 1401/1401 passed, 0 failures, 0 errors
- Size: api_server.py 1773 lines (93220 bytes) → 1780 lines (93136 bytes); +7 lines, -84 bytes
- No test files modified
- No action module files modified
- No api_models.py changes
- No /chat or /awaken changes
- No source mutation changes
- No apply/rollback changes
- No Observation Record Store added
- No runtime/private data modified (same mutation log format/path)
- No commit made
- 82G not started

### 82G — Proposal Console Service Extraction

**Status:** Complete

**Type:** structure-only refactor — 18 proposal-console endpoint handlers extracted from `aether/interface/api_server.py` into `aether/action/services/proposal_console_service.py`. Three direct action-module imports (`proposal_review_console`, `proposal_revision_console`, `revised_proposal_review_loop`) removed from `api_server.py`. Zero endpoint, contract, or runtime behavior changes.

**Description:**
Extracted 18 endpoint handlers (6 proposal-review-console, 6 proposal-revision-console, 6 revised-proposal-review) into `aether/action/services/proposal_console_service.py`. Each handler body reduced to a single-line `handle_*` call. Three direct `from aether.action.* import` statements replaced with a single import from `proposal_console_service`. The `handle_*` functions preserve exact orchestration logic (response dict shape, parameter names/defaults, metadata handling).

**Safety:**
- Low risk — all three modules are review/proposal-creation only
- `submit_proposal_review` calls `review_patch_proposal` (review-only, never applies)
- `create_proposal_revision` calls `create_patch_proposal` (creates draft proposals, never applies)
- `open_revised_proposal_review` calls `open_proposal_review_console` (opens console, never applies)
- No source mutation capability
- No apply/rollback calls
- No real tool execution
- No subprocess or network

**Files created (1):**
- `aether/action/services/proposal_console_service.py` — service module with 18 `handle_*` functions (176 lines, 6038 bytes)

**Files modified (1):**
- `aether/interface/api_server.py` — replaced 18 handler bodies with thin service calls; removed 3 direct action-module imports; added import from `proposal_console_service`

**Handler migration (18):**
- open_proposal_review_console_action → handle_open_proposal_review_console
- submit_proposal_review_action → handle_submit_proposal_review
- get_proposal_review_console_status_action → handle_proposal_review_console_status
- list_proposal_review_console_action → handle_list_proposal_review_console
- summarize_proposal_review_console_action → handle_summarize_proposal_review_console
- get_proposal_review_console_action → handle_get_proposal_review_console
- open_proposal_revision_console_action → handle_open_proposal_revision_console
- create_proposal_revision_action → handle_create_proposal_revision
- get_proposal_revision_console_status_action → handle_proposal_revision_console_status
- list_proposal_revision_console_action → handle_list_proposal_revision_console
- summarize_proposal_revision_console_action → handle_summarize_proposal_revision_console
- get_proposal_revision_console_action → handle_get_proposal_revision_console
- open_revised_proposal_review_action → handle_open_revised_proposal_review
- submit_revised_proposal_review_action → handle_submit_revised_proposal_review
- get_revised_proposal_review_status_action → handle_revised_proposal_review_status
- list_revised_proposal_review_action → handle_list_revised_proposal_review
- summarize_revised_proposal_review_action → handle_summarize_revised_proposal_review
- get_revised_proposal_review_action → handle_get_revised_proposal_review

**Verification:**
- Compile: `proposal_console_service.py` and `api_server.py` both compile successfully (`py_compile`)
- FastAPI app import: 304 routes, 300 paths, 103 schemas — unchanged
- OpenAPI comparison: exact match before/after
- Import scan: zero remaining direct imports from `proposal_review_console`, `proposal_revision_console`, or `revised_proposal_review_loop` in api_server.py
- Full pytest: 1401/1401 passed, 0 failures, 0 errors
- Size: api_server.py 1780 lines (93136 bytes) → 1797 lines (92695 bytes); +17 lines, -441 bytes
- No test files modified
- No action module files modified
- No api_models.py changes
- No /chat or /awaken changes
- No source mutation changes
- No apply/rollback changes
- No real tool execution added
- No Observation Record Store added
- No commit made
- 82H — Code Review and Review Bridge Service Extraction
  - Created code_review_service.py (100 lines, 3086 bytes)
  - Extracted 10 endpoints (5 code-review + 5 review-bridge)
  - OpenAPI exact match: 304 routes / 300 paths / 103 schemas
  - pytest 1401/1401 passed
  - py_compile passed
  - import scan passed (no direct code_reviewer/review_bridge imports remain)
  - git diff --check clean
  - No /chat changes
  - No /awaken changes
  - No api_models.py changes
  - No action module changes
  - No test file changes
  - No source mutation
  - No apply/rollback
  - No self_modification execution
  - Observation Record Store deferred
  - Not committed
- 82I — Interface Router Extraction Plan
  82I not started
- 82J — Code Review Router Extraction
  - Created aether/interface/routers/__init__.py
  - Created aether/interface/routers/code_review_routes.py (84 lines, 2617 bytes)
  - Moved 10 code-review / review-bridge route definitions from api_server.py to code_review_routes.py
  - Added app.include_router(code_review_router, prefix="")
  - Removed code_review_service handler imports from api_server.py
  - OpenAPI exact match: 300 paths / 103 schemas
  - raw len(app.routes): 304→295 (10 APIRoute entries replaced by 1 _IncludedRouter container — FastAPI internal representation, not route loss)
  - effective API routes unchanged by OpenAPI contract: yes
  - Full pytest 1401/1401 passed
  - py_compile passed
  - No /chat changes
  - No /awaken changes
  - No api_models.py changes
  - No service module changes
  - No action module changes
  - No test file changes
  - No source mutation
  - No apply/rollback
  - No Observation Record Store
  - Not committed
- 82K — Mutation Log Router Extraction
  - Created aether/interface/routers/mutation_log_routes.py (58 lines, 1703 bytes)
  - Moved 6 mutation-log route definitions from api_server.py to mutation_log_routes.py
  - Added app.include_router(mutation_log_router, prefix="")
  - Removed mutation_log_service handler imports from api_server.py
  - OpenAPI exact match
  - OpenAPI path count unchanged: 300
  - OpenAPI schema count unchanged: 103
  - All 6 moved mutation-log paths present
  - Full pytest 1401/1401 passed
  - Raw len(app.routes) may change due to include_router representation and is not the contract gate
  - No /chat changes
  - No /awaken changes
  - No api_models.py changes
  - No service module changes
  - No action module changes
  - No test file changes
  - No source mutation
  - No apply/rollback
  - No Observation Record Store
  - Not committed
- 82L — Proposal Console Router Extraction
  - Created aether/interface/routers/proposal_console_routes.py (153 lines, 5761 bytes)
  - Moved 18 proposal-console route definitions from api_server.py to proposal_console_routes.py
  - Added app.include_router(proposal_console_router, prefix="")
  - Removed proposal_console_service handler imports from api_server.py
  - OpenAPI exact match
  - OpenAPI path count unchanged: 300
  - OpenAPI schema count unchanged: 103
  - All 18 moved proposal-console paths present
  - Full pytest 1401/1401 passed
  - Raw len(app.routes) may change due to include_router representation and is not the contract gate
  - No /chat changes
  - No /awaken changes
  - No api_models.py changes
  - No service module changes
  - No action module changes
  - No test file changes
  - No source mutation
  - No apply/rollback
  - No Observation Record Store
  - Not committed
- 82N — File Router Extraction
  - Created aether/interface/routers/file_routes.py (111 lines, 3210 bytes)
  - Moved 15 file/self-inspection route definitions from api_server.py to file_routes.py
  - Added app.include_router(file_router, prefix="")
  - Removed file_service handler imports from api_server.py
  - OpenAPI exact match
  - OpenAPI path count unchanged: 300
  - OpenAPI schema count unchanged: 103
  - All 15 moved file/self-inspection paths present
  - Full pytest 1401/1401 passed
  - Raw len(app.routes) may change due to include_router representation and is not the contract gate
  - No /chat changes
  - No /awaken changes
  - No api_models.py changes
  - No file_service.py changes
  - No service module changes
  - No action module changes
  - No test file changes
  - No file access behavior changes
  - No side-effect behavior changes
  - No source mutation
  - No apply/rollback
  - No Observation Record Store
  - Not committed
- 82O Build — Patch Router Extraction
  - Created aether/interface/routers/patch_routes.py (89 lines, 3839 bytes)
  - Moved 17 patch lifecycle route definitions from api_server.py to patch_routes.py
  - Added app.include_router(patch_router, prefix="")
  - Removed patch_service handler imports from api_server.py
  - OpenAPI exact match
  - OpenAPI path count unchanged: 300
  - OpenAPI schema count unchanged: 103
  - All 17 moved patch paths present
  - Full pytest 1401/1401 passed
  - Raw len(app.routes) may change due to include_router representation and is not the contract gate
  - No /chat changes
  - No /awaken changes
  - No api_models.py changes
  - No patch_service.py changes
  - No service module changes
  - No action module changes
  - No test file changes
  - No source mutation behavior changes
  - No apply behavior changes
  - No rollback behavior changes
  - No backup behavior changes
  - No side-effect behavior changes
  - No manual apply endpoint invocation
  - No manual rollback endpoint invocation
  - No Observation Record Store
  - Not committed
- 82P Build — Approval Router Extraction
  - Created aether/interface/routers/approval_routes.py (103 lines, 3633 bytes)
  - Moved 13 approval route definitions from api_server.py to approval_routes.py
  - Added app.include_router(approval_router, prefix="")
  - Removed approval_service handler imports from api_server.py
  - OpenAPI exact match
  - OpenAPI path count unchanged: 300
  - OpenAPI schema count unchanged: 103
  - All 13 moved approval paths present
  - Full pytest 1401/1401 passed
  - Raw len(app.routes) may change due to include_router representation and is not the contract gate
  - No /chat changes
  - No /awaken changes
  - No api_models.py changes
  - No approval_service.py changes
  - No service module changes
  - No action module changes
  - No test file changes
  - No approval behavior changes
  - No side-effect behavior changes
  - No manual approval endpoint invocation
  - No source mutation behavior changes
  - No apply behavior changes
  - No rollback behavior changes
  - No backup behavior changes
  - No Observation Record Store
  - Not committed
- 82Q Build — Dry Run + Sandbox Contract Router Extraction
  - Created aether/interface/routers/dry_run_routes.py (50 lines, 1647 bytes)
  - Moved 5 dry-run/sandbox route definitions from api_server.py to dry_run_routes.py
  - Added app.include_router(dry_run_router, prefix="")
  - Removed dry_run_service and sandbox_contract_service handler imports from api_server.py
  - simulation_plan_service imports left untouched in api_server.py
  - OpenAPI exact match
  - OpenAPI path count unchanged: 300
  - OpenAPI schema count unchanged: 103
  - All 5 moved dry-run/sandbox paths present
  - Simulation-plan paths still present
  - Simulation-plan imports unchanged
  - Full pytest 1401/1401 passed
  - Raw len(app.routes) may change due to include_router representation and is not the contract gate
  - No /chat changes
  - No /awaken changes
  - No api_models.py changes
  - No dry_run_service.py changes
  - No sandbox_contract_service.py changes
  - No simulation_plan_service.py changes
  - No service module changes
  - No action module changes
  - No test file changes
  - No dry-run behavior changes
  - No sandbox behavior changes
  - No side-effect behavior changes
  - No manual dry-run/sandbox endpoint invocation
  - No manual simulation-plan endpoint invocation
  - No source mutation behavior changes
  - No apply behavior changes
  - No rollback behavior changes
  - No Observation Record Store
  - Superseded next-step status: 82R Build completed locally after the 82R planning artifact
- 82R Build — Simulation Plan + Simulation Result Router Extraction
  - Created aether/interface/routers/simulation_routes.py (69 lines, 2624 bytes)
  - Moved 8 simulation-plan/result route definitions from api_server.py to simulation_routes.py
  - Added app.include_router(simulation_router, prefix="")
  - Removed both simulation_plan_service import blocks from api_server.py
  - Removed simulation_result_service import block from api_server.py
  - OpenAPI exact match
  - OpenAPI path count unchanged: 300
  - OpenAPI schema count unchanged: 103
  - All 8 moved simulation paths present
  - Operation IDs unchanged
  - Full pytest 1401/1401 passed
  - Raw len(app.routes) changed 227→220 due to include_router representation and is not the contract gate
  - No /chat changes
  - No /awaken changes
  - No api_models.py changes
  - No simulation_plan_service.py changes
  - No simulation_result_service.py changes
  - No service module changes
  - No action module changes
  - No test file changes
  - No simulation behavior changes
  - No side-effect behavior changes
  - No manual simulation-plan endpoint invocation
  - No manual simulation-result endpoint invocation
  - No source mutation
  - No apply/rollback
  - No Observation Record Store
  - Complete locally; not committed, tagged, or pushed
  - Superseded next-step status: 82S Build completed locally after the 82S planning artifact
- 82S Build — Verification Verdict + Apply Gate Router Extraction
  - Created aether/interface/routers/verification_apply_gate_routes.py (68 lines, 2889 bytes)
  - Moved 8 verification-verdict/apply-gate route definitions from api_server.py to verification_apply_gate_routes.py
  - Added app.include_router(verification_apply_gate_router, prefix="")
  - Removed verification_verdict_service import block from api_server.py
  - Removed apply_gate_service import block from api_server.py
  - OpenAPI exact match
  - OpenAPI path count unchanged: 300
  - OpenAPI schema count unchanged: 103
  - All 8 moved paths present
  - Operation IDs unchanged
  - Full pytest 1401/1401 passed
  - Raw len(app.routes) changed 220→213 due to include_router representation and is not the contract gate
  - No /chat changes
  - No /awaken changes
  - No api_models.py changes
  - No verification_verdict_service.py changes
  - No apply_gate_service.py changes
  - No service module changes
  - No action module changes
  - No test file changes
  - No verification-verdict behavior changes
  - No apply-gate behavior changes
  - No persistence behavior changes
  - No side-effect behavior changes
  - No manual verification-verdict endpoint invocation
  - No manual apply-gate endpoint invocation
  - No source mutation
  - No tool execution
  - No apply/rollback
  - No Observation Record Store
  - Committed, tagged, and pushed as milestone-82S-verification-apply-gate-router at 3f06269
  - Superseded next-step status: 82T Build completed locally after the 82T planning artifact
- 82T Build — Human Authorization + Apply Execution Gate Router Extraction
  - Created aether/interface/routers/authorization_execution_gate_routes.py (110 lines, 5107 bytes)
  - Moved 12 human-authorization/apply-execution-gate route definitions from api_server.py to authorization_execution_gate_routes.py
  - Added app.include_router(authorization_execution_gate_router, prefix="")
  - Removed human_authorization_service import block from api_server.py
  - Removed apply_execution_gate_service import block from api_server.py
  - Removed HumanAuthContextBody and HumanAuthDecisionBody imports from api_server.py after confirming they were unused there
  - Retained ApplyExecGateDecisionBody in api_server.py because executor contract and executor plan routes still require it
  - OpenAPI exact match
  - OpenAPI path count unchanged: 300
  - OpenAPI schema count unchanged: 103
  - All 12 moved paths present
  - Operation IDs unchanged
  - Full pytest 1401/1401 passed
  - Raw len(app.routes) changed 213→202 due to include_router representation and is not the contract gate
  - No /chat changes
  - No /awaken changes
  - No api_models.py changes
  - No human_authorization_service.py changes
  - No apply_execution_gate_service.py changes
  - No service module changes
  - No action module changes
  - No test file changes
  - No authorization behavior changes
  - No apply-execution-gate behavior changes
  - No persistence behavior changes
  - No side-effect behavior changes
  - No manual human-authorization endpoint invocation
  - No manual apply-execution-gate endpoint invocation
  - No source mutation
  - No tool execution
  - No apply/rollback
  - No Observation Record Store
  - Committed, tagged, and pushed as milestone-82T-authorization-execution-gate-router at 84d17b6
  - Superseded next-step status: 82U Build completed locally after the 82U planning artifact
- 82U Build — Executor Contract + Executor Plan Router Extraction
  - Created aether/interface/routers/executor_routes.py (137 lines, 4760 bytes)
  - Moved 12 executor-contract/executor-plan route definitions from api_server.py to executor_routes.py
  - Added app.include_router(executor_router, prefix="")
  - Removed executor_contract_service import block from api_server.py
  - Removed executor_plan_service import block from api_server.py
  - Removed ApplyExecGateDecisionBody from api_server.py after confirming it was unused there
  - Evidence routes and evidence service imports remain in api_server.py
  - OpenAPI exact match
  - OpenAPI path count unchanged: 300
  - OpenAPI schema count unchanged: 103
  - All 12 moved paths present
  - Operation IDs unchanged
  - Full pytest 1401/1401 passed
  - Raw len(app.routes) changed 202→191 due to include_router representation and is not the contract gate
  - No /chat changes
  - No /awaken changes
  - No api_models.py changes
  - No executor_contract_service.py changes
  - No executor_plan_service.py changes
  - No service module changes
  - No action module changes
  - No test file changes
  - No executor-contract behavior changes
  - No executor-plan behavior changes
  - No persistence behavior changes
  - No side-effect behavior changes
  - No evidence route changes
  - No evidence collection
  - No manual executor-contract endpoint invocation
  - No manual executor-plan endpoint invocation
  - No source mutation
  - No tool execution
  - No apply/rollback
  - No Observation Record Store
  - Committed, tagged, and pushed as milestone-82U-executor-router at 8864e27
  - Superseded next-step status: 82V Build completed locally after the 82V planning artifact
- 82V Build — Evidence Contract + Collection Plan Router Extraction
  - Created aether/interface/routers/evidence_routes.py (145 lines, 5893 bytes)
  - Moved 13 evidence-contract/collection-plan route definitions from api_server.py to evidence_routes.py
  - Added app.include_router(evidence_router, prefix="")
  - Removed evidence_contract_service import block from api_server.py
  - Removed collection_plan_service import block from api_server.py
  - Removed EvidenceContractBody, EvidenceContractDecisionBody, EvidenceContractApproveBody, PlanDecisionBody, and ApprovalIntentBody from api_server.py after confirming they were unused there
  - Verification, tool, memory, self-modification, repair, /chat, and /awaken routes remain in api_server.py
  - OpenAPI exact match
  - OpenAPI path count unchanged: 300
  - OpenAPI schema count unchanged: 103
  - All 13 moved paths present
  - Operation IDs unchanged
  - Full pytest 1401/1401 passed
  - Raw len(app.routes) changed 191→179 due to include_router representation and is not the contract gate
  - api_server.py reduced from 1041 lines / 58461 bytes to 891 lines / 52468 bytes
  - No /chat changes
  - No /awaken changes
  - No api_models.py changes
  - No evidence_contract_service.py changes
  - No collection_plan_service.py changes
  - No service module changes
  - No action module changes
  - No test file changes
  - No evidence-contract behavior changes
  - No collection-plan behavior changes
  - No collector-contract behavior changes
  - No persistence behavior changes
  - No side-effect behavior changes
  - No evidence collection behavior changes
  - No manual evidence-contract endpoint invocation
  - No manual collection-plan endpoint invocation
  - No manual collector-contract endpoint invocation
  - No source mutation
  - No tool execution
  - No apply/rollback
  - No Observation Record Store
  - Committed, tagged, and pushed as milestone-82V-evidence-router at 5d49431
  - Superseded next-step status: 82W Build completed locally after the 82W planning artifact
- 82W Build — Verification Plan Router Extraction
  - Created aether/interface/routers/verification_plan_routes.py (14 lines, 406 bytes)
  - Moved POST /verification/plan from api_server.py to verification_plan_routes.py
  - Added app.include_router(verification_plan_router, prefix="")
  - Removed verification_plan_service import block from api_server.py
  - Retained VerificationRequest in api_server.py because /verification/classify still requires it
  - /verification/classify and classify_risk remain unchanged
  - OpenAPI exact match
  - OpenAPI path count unchanged: 300
  - OpenAPI schema count unchanged: 103
  - POST /verification/plan present
  - POST /verification/classify present
  - Operation IDs unchanged
  - Full pytest 1401/1401 passed
  - Raw len(app.routes) remained 179→179; raw route count is diagnostic and is not the contract gate
  - api_server.py reduced from 891 lines / 52468 bytes to 881 lines / 52354 bytes
  - No /chat changes
  - No /awaken changes
  - No root or identity route changes
  - No api_models.py changes
  - No verification_plan_service.py changes
  - No service module changes
  - No action module changes
  - No test file changes
  - No verification-plan behavior changes
  - No classify behavior changes
  - No persistence behavior changes
  - No memory/timeline/graph behavior changes
  - No side-effect behavior changes
  - No manual verification-plan endpoint invocation
  - No manual verification-classify endpoint invocation
  - No source mutation
  - No tool execution
  - No apply/rollback
  - No evidence collection
  - No Observation Record Store
  - Committed, tagged, and pushed as milestone-82W-verification-plan-router at baa6f6b
  - Superseded next-step status: 82X Build completed locally after the 82X planning artifact
- 82X Build — Tool Registry + Tool Plan Router Extraction
  - Created aether/interface/routers/tool_registry_plan_routes.py (117 lines, 4000 bytes)
  - Moved 13 tool-registry/tool-plan routes from api_server.py to tool_registry_plan_routes.py
  - Added app.include_router(tool_registry_plan_router, prefix="")
  - Removed tool_registry_service import block from api_server.py
  - Removed tool_plan_service import block from api_server.py
  - Removed ToolRegisterRequest, ToolSearchRequest, ToolPolicyUpdateRequest, and ToolPlanRequest from api_server.py after unused-reference proof
  - /action/tool-executor routes remain in api_server.py
  - tool_execution_service imports remain in api_server.py
  - ToolExecutionRequest remains in api_server.py
  - ToolPlanListRequest and ToolExecutionListRequest remain unchanged in api_server.py
  - /chat remains unchanged
  - /awaken remains unchanged
  - Root and identity routes remain unchanged
  - /verification/classify remains unchanged
  - Memory routes remain unchanged
  - OpenAPI exact match
  - OpenAPI path count unchanged: 300
  - OpenAPI schema count unchanged: 103
  - All 13 moved paths present
  - All tool-execution protected paths present
  - Operation IDs unchanged
  - Full pytest 1401/1401 passed
  - Raw len(app.routes) changed 179→167 due to include_router representation and is not the contract gate
  - api_server.py reduced from 881 lines / 52354 bytes to 773 lines / 48903 bytes
  - No api_models.py changes
  - No tool_registry_service.py changes
  - No tool_plan_service.py changes
  - No tool_execution_service.py changes
  - No service module changes
  - No action module changes
  - No test file changes
  - No tool-registry behavior changes
  - No tool-plan behavior changes
  - No tool-execution behavior changes
  - No persistence behavior changes
  - No memory/timeline/graph behavior changes
  - No side-effect behavior changes
  - No manual tool-registry endpoint invocation
  - No manual tool-plan endpoint invocation
  - No manual tool-execution endpoint invocation
  - No source mutation
  - No tool execution added or performed
  - No apply/rollback
  - No evidence collection
  - No Observation Record Store
  - Complete locally; not committed, tagged, or pushed
  - Next: 82Y — Remaining Router Extraction Plan
  - 82Y not started
- 82AA Build — Memory Router Extraction
  - Created aether/interface/routers/memory_routes.py (159 lines, 4775 bytes)
  - Moved all 21 working, episodic, semantic, timeline, and graph memory routes from api_server.py to memory_routes.py
  - Added app.include_router(memory_router, prefix="")
  - Removed the complete memory_service import block from api_server.py
  - Removed EpisodeWriteRequest, GoalRequest, GraphEdgeRequest, GraphNodeRequest, GraphSearchRequest, MilestoneRequest, SemanticSearchRequest, and TimelineSearchRequest from api_server.py after unused-reference proof
  - /chat remains unchanged
  - /awaken remains unchanged
  - Root and identity routes remain unchanged
  - /verification/classify remains unchanged
  - Tool-executor routes remain unchanged
  - OpenAPI exact match
  - OpenAPI path count unchanged: 300
  - OpenAPI schema count unchanged: 103
  - All 21 moved memory paths present
  - All protected paths present
  - Operation IDs unchanged
  - tests/test_memory_state_boundary.py: 8/8 passed
  - Full pytest 1409/1409 passed
  - Real-store fingerprint before/after the full suite unchanged
  - Raw len(app.routes) changed 167→147 due to include_router representation and is not the contract gate
  - api_server.py reduced from 773 lines / 48903 bytes to 622 lines / 44552 bytes
  - No api_models.py changes
  - No memory_service.py changes
  - No aether/memory module changes
  - No test changes
  - No service or action module changes
  - No persistence behavior changes
  - No memory, timeline, graph, semantic, or vector behavior changes
  - No side-effect behavior changes
  - No manual memory endpoint invocation outside pytest
  - No source mutation
  - No tool execution
  - No apply/rollback
  - No Observation Record Store
  - Complete locally; not committed, tagged, or pushed
  - Next: 82AB — Remaining Interface Risk Plan
  - 82AB not started
- 82AD Build — Tool Execution Safety Tests
  - Created tests/test_tool_execution_api_boundary.py (525 lines, 20928 bytes)
  - Added 46 API-level tool-executor safety tests
  - Covered all five /action/tool-executor endpoints
  - Covered all 12 required tool execution safety scenarios
  - Denied tools are blocked
  - Approval-required tools are blocked pending approval
  - Non-existent tools return tool_not_found
  - Disabled tools return tool_disabled
  - dry_run advisory invariant covered
  - Source mutation denial proof included
  - All five tool-executor operation IDs locked
  - OpenAPI unchanged: 300 paths / 103 schemas
  - Tool execution API boundary tests: 46/46 passed
  - Memory state boundary tests: 8/8 passed
  - Full pytest 1455/1455 passed, 0 failures, 0 errors
  - Production source unchanged
  - Tool Execution Router Extraction not started
  - tool_executor_routes.py not created
  - Runtime-state reset was authorized retroactively by human authority on 2026-07-30
  - Runtime-state audit retained at /home/aether/summaries/milestone_82AD_runtime_state_review.txt
  - No tool execution behavior changes
  - No endpoint, request, response, persistence, or OpenAPI contract changes
  - Next: 82AE Build — Tool Execution Router Extraction
  - 82AE allowed: yes
  - 82AE not started
- 82AE Build — Tool Execution Router Extraction
  - Created aether/interface/routers/tool_executor_routes.py (46 lines, 1568 bytes)
  - Moved all five /action/tool-executor routes from api_server.py to tool_executor_routes.py
  - Updated tests/test_memory_state_boundary.py to relocate the five tool-executor AST locks from api_server.py to tool_executor_routes.py
  - Preserved all eight non-tool protected api_server.py AST locks unchanged
  - Added app.include_router(tool_executor_router, prefix="")
  - Removed the tool_execution_service import block from api_server.py
  - Removed ToolExecutionRequest from api_server.py after unused-reference proof
  - OpenAPI exact match
  - OpenAPI path count unchanged: 300
  - OpenAPI schema count unchanged: 103
  - All five moved paths present
  - All five operation IDs unchanged
  - tests/test_tool_execution_api_boundary.py: 46/46 passed
  - tests/test_memory_state_boundary.py: 8/8 passed
  - Full pytest 1455/1455 passed, 0 failures, 0 errors
  - Raw len(app.routes) changed 147→143 due to include_router representation and is not the contract gate
  - api_server.py reduced from 622 lines / 44552 bytes to 583 lines / 43303 bytes
  - No tool behavior changes
  - No approval behavior changes
  - No dry_run behavior changes
  - No sandbox whitelist behavior changes
  - No persistence behavior changes
  - No source mutation behavior changes
  - No memory/timeline/graph behavior changes
  - No side-effect behavior changes
  - No api_models.py changes
  - No tool_execution_service.py changes
  - No tool_executor.py changes
  - No tool_registry.py changes
  - No tool_planner.py changes
  - No approval_queue.py changes
  - No /chat or /awaken changes
  - No root/identity changes
  - No /verification/classify changes
  - No direct-action route changes
  - No manual endpoint invocation outside pytest
  - No Observation Record Store
  - Finalized, committed, tagged, and pushed as `milestone-82AE-tool-executor-router` at `55cf953`
  - Next: 82AF — Direct Action Service Extraction Plan
  - 82AF not started
- 82AH-R Build — Full-Suite Private Persistence Isolation Correction
  - Blocker-resolution milestone for 82AH Post-Chain Gate C1 State Boundary Tests
  - Root cause: pre-existing full-suite tests wrote private records through module-local config loaders and imported path getters into real `/home/aether/data/private`
  - Generalized `tests/conftest.py` to provide tests-only global private/runtime persistence isolation
  - Added `tests/test_full_suite_private_persistence_isolation.py` with 20 isolation contract tests
  - Added `tests/test_post_chain_c1_state_boundary.py` with 30 C1 state and API boundary tests
  - Covered all 24 approved-dry-run, dry-run-review, real-apply-approval, and post-apply-verification C1 endpoints
  - C1 operation IDs and OpenAPI contracts locked
  - Full-suite writes now use one pytest temporary data root outside the repository and `/home/aether/data`
  - Full-suite real-root fingerprint unchanged across private, timeline, graph, vector, vault, and logs roots
  - C2 `final_real_apply_executor` remains deferred
  - No production source changes
  - No service or router extraction
  - No real apply, rollback, evidence collection, or tool execution
  - OpenAPI unchanged: 300 paths / 103 schemas
  - Full pytest 1505/1505 passed, 0 failures, 0 errors
  - Finalized, committed, tagged, and pushed as `milestone-82AH-R-full-suite-private-persistence-isolation` at `8575d31`
  - Next: 82AI Build — Post-Chain Gate C1 Service Extraction
  - 82AI not started
- 82AI Build — Post-Chain Gate C1 Service Extraction
  - C1 service extraction finalized
  - Added `aether/action/services/approved_dry_run_gate_service.py`
  - Added `aether/action/services/dry_run_review_gate_service.py`
  - Added `aether/action/services/real_apply_approval_gate_service.py`
  - Added `aether/action/services/post_apply_verification_gate_service.py`
  - All 24 C1 routes now delegate to exactly one service handler
  - Each service handler delegates to exactly one existing C1 action function
  - Updated `tests/test_post_chain_c1_state_boundary.py` to lock the route → service → action boundary
  - C2 `final_real_apply_executor` remains deferred and unchanged
  - No router extraction
  - No action behavior or persistence-format changes
  - No endpoint, request model, response wrapper, method, path, default, or operation-ID changes
  - OpenAPI exact match: 300 paths / 103 schemas
  - C1 state boundary tests: 30/30 passed
  - Full pytest: 1505/1505 passed, 0 failures, 0 errors
  - Full-suite real-root fingerprint passed with drift count 0
  - No real apply, rollback, evidence collection, or tool execution
  - Finalized, committed, tagged, and pushed as `milestone-82AI-post-chain-c1-service-extraction` at `35f457b`
  - Next: 82AJ — Final Real-Apply Executor C2 Safety Boundary Plan/Tests
  - 82AJ started and completed
- 82AJ Build — Final Real-Apply Executor C2 Safety Boundary Plan/Tests
  - Tests-only C2 final-real-apply safety prerequisite complete locally
  - Added `tests/test_final_real_apply_executor_c2_safety_boundary.py` with 11 safety-boundary tests
  - Covered all 6 `/action/final-real-apply-executor` endpoints
  - Locked all 6 current C2 operation IDs and the exact OpenAPI contract
  - Locked the current route → direct action boundary before service extraction
  - Locked `execute_final_real_apply` as the sole C2 `apply_patch_proposal(..., False)` call site
  - Execute endpoint guarded by a fail-closed deny-real-apply monkeypatch
  - Missing/non-ready execute proved not to reach `apply_patch_proposal`
  - `final_real_apply_executor_service.py` not created
  - No production source changes
  - No router or service extraction
  - No action behavior changes
  - OpenAPI exact match: 300 paths / 103 schemas
  - Full pytest: 1516/1516 passed, 0 failures, 0 errors
  - Full-suite real-root fingerprint passed with drift count 0
  - No real apply, rollback, evidence collection, or tool execution
  - Finalized, committed, tagged, and pushed as `milestone-82AJ-final-real-apply-c2-safety-boundary` at `227c24c`
  - Next: 82AK Build — Final Real-Apply Executor C2 Service Extraction
  - 82AK started and completed
- 82AK Build — Final Real-Apply Executor C2 Service Extraction
  - C2 service extraction only; no action behavior changes
  - Created `aether/action/services/final_real_apply_executor_service.py` with 6 handle_* functions
  - Updated `aether/interface/api_server.py`: C2 routes now delegate to service handlers
  - Updated `tests/test_final_real_apply_executor_c2_safety_boundary.py`: C2_ENDPOINTS extended to 5 elements; route→service→action verification
  - Updated `tests/test_post_chain_c1_state_boundary.py`: expects C2 service module to exist; no C2 router extraction
  - OpenAPI exact match: 300 paths / 103 schemas
  - Full pytest: 1517/1517 passed, 0 failures, 0 errors
  - Full-suite real-root fingerprint passed with drift count 0
  - No real apply, rollback, evidence collection, or tool execution
  - Finalized, committed, tagged, and pushed as `milestone-82AK-final-real-apply-c2-service-extraction` at `03b726c`
  - Next: 82AL Plan — Repair Family State-Boundary Plan
  - 82AL Plan — Repair Family State-Boundary Plan
    - Scope: 43 endpoints across 7 Repair families (repair_planner 5, repair_bridge_selector 5, repair_workflow_tracker 5, repair_workflow_exporter 4, repair_cycle_completion 8, repair_learning 8, repair_guidance 8)
    - Strategy: Phased extraction by risk (bridge_selector highest-risk → extracted last)
      - Part 1: Boundary tests only — create tests/test_repair_family_service_boundary.py covering all 43 endpoints before any service extraction
      - Part 2: Low-Risk Service Extraction — repair_planner + repair_workflow_tracker only
      - Part 3: Medium-Risk Service Extraction — repair_workflow_exporter + repair_cycle_completion + repair_learning + repair_guidance
      - Part 4: Highest-Risk Service Extraction — repair_bridge_selector only
      - Router extraction is not part of the immediate next milestone and must not be presented as the next step
    - No production source changes in Part 1
- 82AL Build Part 1 — Repair Family State-Boundary Tests
  - Tests-only boundary milestone for all 43 Repair Family endpoints
  - Created `tests/test_repair_family_service_boundary.py` with 50 tests
  - Locked all 43 OpenAPI operation IDs for repair endpoints
  - Locked the exact OpenAPI contract: 300 paths / 103 schemas
  - Verified 41/43 endpoints return 200 with valid responses via isolated fixture
  - Documented 2 pre-existing bugs in repair_guidance/export-report and export-private
    (export_repair_guidance_report and export_private_repair_guidance_record crash on
    None when get_repair_guidance_record returns None for missing records)
  - Locked route→action function pass-through for all 43 routes
  - Verified no forbidden imports (executor/apply/rollback) in repair action modules
  - No production source changes
  - OpenAPI exact match: 300 paths / 103 schemas
  - Full pytest: 1567/1567 passed, 0 failures, 0 errors
  - No real apply, rollback, evidence collection, or tool execution
  - Finalized, committed, tagged, and pushed as `milestone-82AL-part1-repair-family-boundary-tests` at `9ed75f8`
  - Next: 82AL Build Part 2 — Low-Risk Repair Family Service Extraction (repair_planner + repair_workflow_tracker only)
  - 82AL Build Part 2 — Low-Risk Repair Family Service Extraction (finalized)
    - Created `aether/action/services/repair_planner_service.py` and `aether/action/services/repair_workflow_tracker_service.py`
      with 10 `handle_*` service functions, each a single-return passthrough to its action function
    - Updated `aether/interface/api_server.py`: the 10 repair_planner and repair_workflow_tracker
      routes now delegate to service handlers; decorators, paths, signatures, operation IDs,
      and wrapper keys unchanged
    - repair_bridge_selector (highest-risk) and the medium-risk families remain direct-action; no other
      service modules were created
    - Updated `tests/test_repair_family_service_boundary.py` to the mixed boundary model
      (service-backed: repair_planner, repair_workflow_tracker; direct-action: the other 5 families);
      52 tests including new service handler static AST tests
    - No action module changes; no router extraction; no real apply, rollback, evidence collection,
      or tool execution; no repair_guidance export bugfix (2 known bugs remain documented)
    - OpenAPI exact match: 300 paths / 103 schemas
    - Full pytest: 1569/1569 passed, 0 failures, 0 errors
    - Finalized, committed, tagged, and pushed as `milestone-82AL-part2-low-risk-repair-family-services` at `f233ba0`
  - Next: 82AL Build Part 3 — Medium-Risk Repair Family Service Extraction (repair_workflow_exporter + repair_cycle_completion + repair_learning + repair_guidance)
  - 82AL Build Part 3 — Medium-Risk Repair Family Service Extraction (finalized)
    - Created 4 service modules: `aether/action/services/repair_workflow_exporter_service.py` (4 handlers),
      `aether/action/services/repair_cycle_completion_service.py` (8 handlers),
      `aether/action/services/repair_learning_service.py` (8 handlers), and
      `aether/action/services/repair_guidance_service.py` (8 handlers), each handler a single-return
      passthrough to exactly one existing action function; export endpoints direct-return with no wrapper,
      all other endpoints preserve their exact response wrapper keys
    - Updated `aether/interface/api_server.py`: the 28 medium-risk routes now delegate to service handlers;
      decorators, paths, signatures, request models, operation IDs, and wrapper keys unchanged; direct action
      imports for the 4 medium-risk families removed; repair_bridge_selector remains direct-action
    - Updated `tests/test_repair_family_service_boundary.py` to the Part 3 mixed boundary model
      (service-backed: repair_planner, repair_workflow_tracker, repair_workflow_exporter,
      repair_cycle_completion, repair_learning, repair_guidance; direct-action: repair_bridge_selector only);
      52 tests; service static AST tests extended to all 6 service modules with direct-return awareness
    - No action module changes; no router extraction; repair_bridge_selector unchanged and deferred to Part 4;
      no real apply, rollback, evidence collection, or tool execution; no repair_guidance export bugfix
      (2 known bugs remain documented)
    - OpenAPI exact match: 300 paths / 103 schemas
    - Full pytest: 1569/1569 passed, 0 failures, 0 errors
    - Full-suite real-root fingerprint passed with drift count 0
    - Finalized, committed, tagged, and pushed as `milestone-82AL-part3-medium-risk-repair-family-services` at `ff1d728`
  - 82AL Build Part 4 — Highest-Risk Repair Family Service Extraction (finalized)
    - Highest-risk Repair Family service extraction complete locally
    - Added `aether/action/services/repair_bridge_selector_service.py` (5 handlers,
      each a single-return passthrough to exactly one existing action function)
    - Updated the 5 repair_bridge_selector routes in `aether/interface/api_server.py`
    - repair_bridge_selector routes now delegate route -> service -> action
    - all 43 Repair Family endpoints are now service-backed
    - direct-action Repair Family endpoints remaining: none
    - response wrappers preserved
    - operation IDs preserved
    - create_approval_if_required pass-through preserved exactly
    - no approval policy added
    - no direct approval creation added in service layer
    - OpenAPI exact match: 300 paths / 103 schemas
    - action modules unchanged
    - existing service modules unchanged
    - no router extraction
    - no real apply, rollback, evidence collection, or tool execution
    - known repair_guidance export bugs remain documented/deferred
    - full-suite real-root/docs-history fingerprint passed with drift count 0
    - Full pytest: 1570/1570 passed, 0 failures, 0 errors
    - Finalized, committed, tagged, and pushed as `milestone-82AL-part4-repair-bridge-selector-service` at `13b84a6`
  - 82AM Build — Repair Family Router Extraction (complete locally, not committed)
    - Repair Family router extraction complete locally
    - Added `aether/interface/routers/repair_routes.py`
    - Did not modify `aether/interface/routers/__init__.py`
    - Moved all 43 Repair Family routes from `aether/interface/api_server.py` into `aether/interface/routers/repair_routes.py`
    - `api_server.py` now imports and includes `repair_router`
    - `repair_router = APIRouter()` with empty prefix
    - all 43 Repair Family endpoints remain service-backed
    - direct-action Repair Family endpoints remaining: none
    - operation IDs preserved
    - OpenAPI exact match: 300 paths / 103 schemas
    - all 43 /action/repair-* paths present
    - route function names/signatures/defaults/request models preserved
    - response wrappers preserved
    - create_approval_if_required pass-through preserved
    - authorized C1 include_router snapshot refresh: 16 -> 17
    - no C1/C2 safety assertions weakened
    - no action modules changed
    - no service modules changed
    - no api_models.py change
    - no router files changed except new repair_routes.py
    - no repair_guidance bugfix
    - no real apply, rollback, evidence collection, or tool execution
    - full-suite real-root/docs-history fingerprint passed with drift count 0
    - Full pytest: 1572/1572 passed, 0 failures, 0 errors
    - Finalized, committed, tagged, and pushed as `milestone-82AM-repair-family-router-extraction` at `dfe9949`
  - Next: 82AN Plan — Remaining api_server Thin Interface Extraction Plan
  - 82AN Build — C1 Post-chain Router Extraction (complete locally, not committed)
    - C1 post-chain router extraction complete locally
    - Added `aether/interface/routers/post_chain_c1_routes.py`
    - Did not modify `aether/interface/routers/__init__.py`
    - Moved all 24 C1 post-chain routes (approved-dry-run-gate, dry-run-review-gate,
      real-apply-approval-gate, post-apply-verification-gate; 6 routes each) from
      `aether/interface/api_server.py` into `aether/interface/routers/post_chain_c1_routes.py`
    - `api_server.py` now imports and includes `post_chain_c1_router`
    - `post_chain_c1_router = APIRouter()` with empty prefix
    - all 24 C1 post-chain endpoints remain service-backed (route -> service -> action)
    - route function names/signatures/defaults/request models preserved
    - operation IDs preserved
    - response wrappers preserved
    - the 6 C2 final-real-apply-executor routes remain defined in `api_server.py`
    - the 4 C1 service imports moved from `api_server.py` into `post_chain_c1_routes.py`;
      the C2 service import remains in `api_server.py`
    - authorized C1 include_router snapshot refresh: 17 -> 18
    - no C1/C2 safety assertions weakened
    - no action modules changed
    - no service modules changed
    - no api_models.py change
    - no router files changed except new post_chain_c1_routes.py
    - no repair_guidance bugfix
    - no real apply, rollback, evidence collection, or tool execution
    - full-suite real-root/docs-history fingerprint passed with drift count 0
    - Full pytest: 1572/1572 passed, 0 failures, 0 errors
    - Finalized, committed, tagged, and pushed as `milestone-82AN-c1-post-chain-router-extraction` at `d860616`
  - Next: 82AO Plan — C2 Final Real-Apply Executor Router Extraction Plan
  - 82AO Build — C2 Final Real-Apply Executor Router Extraction (finalized, committed, tagged, pushed)
    - C2 final-real-apply executor router extraction complete locally
    - Added `aether/interface/routers/final_real_apply_executor_routes.py`
    - Did not modify `aether/interface/routers/__init__.py`
    - Did not modify `aether/interface/routers/post_chain_c1_routes.py`
    - Did not modify `aether/interface/routers/repair_routes.py`
    - Moved all 6 C2 final-real-apply executor routes from `aether/interface/api_server.py` into `aether/interface/routers/final_real_apply_executor_routes.py`
    - `api_server.py` now imports and includes `final_real_apply_executor_router`
    - `final_real_apply_executor_router = APIRouter()` with empty prefix
    - all 6 C2 endpoints remain service-backed
    - C1 post-chain routes remain in `post_chain_c1_routes.py`
    - Repair Family routes remain in `repair_routes.py`
    - direct-action C2 endpoints remaining in api_server: none
    - operation IDs preserved
    - OpenAPI exact match: 300 paths / 103 schemas
    - all 6 C2 paths present
    - all 24 C1 paths still present and unchanged
    - all 43 Repair paths still present and unchanged
    - route function names/signatures/defaults/request models preserved
    - response wrappers preserved
    - authorized include_router snapshot refresh: 18 -> 19
    - no C1/C2 safety assertions weakened
    - no action modules changed
    - no service modules changed
    - no api_models.py change
    - no real apply, rollback, evidence collection, or tool execution
    - full-suite real-root/docs-history fingerprint passed
    - Full pytest: 1572/1572 passed, 0 failures, 0 errors
    - Finalized, committed, tagged, and pushed as `milestone-82AO-c2-final-real-apply-executor-router-extraction` at `2a8de72`
  - Next: 82AQ Plan — Guided Launcher Boundary Tests Plan
  - 82AP Build — Changelog Router Extraction (finalized, committed, tagged, and pushed)
    - Changelog router extraction complete locally
    - Added `aether/interface/routers/changelog_routes.py`
    - Did not modify `aether/interface/routers/__init__.py`
    - Did not modify `aether/interface/routers/final_real_apply_executor_routes.py`
    - Did not modify `aether/interface/routers/post_chain_c1_routes.py`
    - Did not modify `aether/interface/routers/repair_routes.py`
    - Moved all 4 changelog routes from `aether/interface/api_server.py` into `aether/interface/routers/changelog_routes.py`
    - `api_server.py` now imports and includes `changelog_router`
    - `changelog_router = APIRouter()` with empty prefix
    - all 4 changelog endpoints remain direct-action pass-throughs
    - C1 post-chain routes remain in `post_chain_c1_routes.py`
    - Repair Family routes remain in `repair_routes.py`
    - C2 final-real-apply executor routes remain in `final_real_apply_executor_routes.py`
    - direct-action changelog endpoints remaining in api_server: none
    - operation IDs preserved
    - OpenAPI exact match: 300 paths / 103 schemas
    - all 4 changelog paths present
    - all 24 C1 paths still present and unchanged
    - all 43 Repair paths still present and unchanged
    - all 6 C2 paths still present and unchanged
    - route function names/signatures/defaults/request models preserved
    - response wrappers preserved
    - authorized include_router snapshot refresh: 19 -> 20
    - no C1/C2 safety assertions weakened
    - no action modules changed
    - no service modules changed
    - no api_models.py change
    - no real apply, rollback, evidence collection, or tool execution
    - full-suite real-root/docs-history fingerprint passed with drift count 0
    - Full pytest: 1576/1576 passed, 0 failures, 0 errors
    - Finalized, committed, tagged, and pushed as `milestone-82AP-changelog-router-extraction` at `f83ee15`
  - 82AQ Build — Guided Launcher Boundary Tests (finalized, committed, tagged, and pushed)
    - tests-only boundary coverage for all 29 Guided launcher routes across 5 direct-action families
    - added `tests/test_guided_launcher_boundary.py` (single consolidated AST/OpenAPI boundary file)
    - did not modify `aether/interface/api_server.py`
    - did not modify any router, action, service, or `api_models.py`
    - all 29 Guided route functions remain in `api_server.py` (no router exists)
    - operation IDs locked for all 29 guided endpoints
    - request models locked for all 9 POST guided endpoints
    - route-to-action pass-throughs locked (call args, wrappers, signatures)
    - 26 routes wrap results in `{"name": "Aether", ...}`; 3 export routes return action result directly
    - exact guided action import snapshot locked (5 modules, 29 names)
    - no guided router file and no guided router include
    - no guided service imports
    - guided test module never invokes endpoints, TestClient, or action functions
    - 5 guided action modules verified unchanged in git diff with zero forbidden terms
    - OpenAPI exact match: 300 paths / 103 schemas (guided 29, changelog 4, C2 6, C1 24, repair 43)
    - full-suite real-root/docs-history fingerprint passed with drift count 0
    - Full pytest: 1581/1581 passed, 0 failures, 0 errors
    - Finalized, committed, tagged, and pushed as `milestone-82AQ-guided-launcher-boundary-tests` at `f25cc2f`
  - Next: 82AR Plan — Guided Launcher Router Extraction Plan
  - 82AR Build — Guided Launcher Router Extraction (complete locally, not committed)
    - Guided Launcher router extraction complete locally
    - Added `aether/interface/routers/guided_launcher_routes.py`
    - Modified `aether/interface/api_server.py`
    - Updated `tests/test_guided_launcher_boundary.py`
    - Updated `tests/test_post_chain_c1_state_boundary.py` only for include_router 20 -> 21
    - Updated `tests/test_repair_family_service_boundary.py` only for guided direct-action import snapshot
    - Did not modify `aether/interface/routers/__init__.py`
    - Did not modify existing routers
    - Did not modify action modules
    - Did not modify service modules
    - Did not modify api_models.py
    - Moved all 29 Guided routes from `api_server.py` into `guided_launcher_routes.py`
    - `guided_launcher_router = APIRouter()` with empty prefix
    - `api_server.py` imports and includes `guided_launcher_router`
    - direct Guided routes remaining in api_server: none
    - api_server @app routes after extraction: 17
    - include_router calls after extraction: 21
    - all 29 Guided endpoints remain direct-action pass-throughs
    - 26 wrapped routes + 3 direct-return export routes preserved
    - operation IDs preserved
    - OpenAPI exact match: 300 paths / 103 schemas
    - Guided paths 29
    - Changelog paths 4
    - C2 paths 6
    - C1 paths 24
    - Repair paths 43
    - no service extraction
    - no endpoint invocation
    - no guided action function invocation
    - no docs/history write
    - no runtime/private write
    - no real apply, rollback, evidence collection, or tool execution
    - full-suite real-root/docs-history fingerprint passed with drift count 0
    - Full pytest: 1581/1581 passed, 0 failures, 0 errors
     - Finalized, committed, tagged, and pushed as `milestone-82AR-guided-launcher-router-extraction` at `5bcb836`
   - Next: 82AR Finalization — Guided Launcher Router Extraction
   - 82AS not started
  - 82AS Build — Self-Modification Boundary Tests (finalized, committed, tagged, and pushed)
    - 20 AST/OpenAPI-only boundary tests added in `tests/test_self_modification_boundary.py`
    - Did not modify `aether/interface/api_server.py`
    - Did not modify routers
    - Did not modify action modules
    - Did not modify service modules
    - Did not modify api_models.py
    - Did not modify existing tests
    - locked 9 Self-Modification routes in `api_server.py`
    - locked all 9 as app.* route decorators
    - locked no `self_modification_routes.py`
    - locked no `self_modification_router` include
    - locked exact OpenAPI operation IDs and request-body model refs
    - locked exact route signatures/defaults/request models
    - locked exact direct-action call names and call argument order
    - locked all 9 routes as wrapped single-return pass-throughs
    - static-risk locked `aether/action/self_modification_cycle.py`
    - expected high-risk terms present and locked: apply_patch_proposal, rollback_patch_apply, write_text, Path(
    - forbidden terms absent: collect_evidence, execute_tool, subprocess, os.system, requests., httpx., shutil, git
    - no endpoint invocation
    - no self_modification route function invocation
    - no self_modification action function invocation
    - no docs/history write
    - no runtime/private write
    - no real apply, rollback, evidence collection, or tool execution
    - OpenAPI exact match: 300 paths / 103 schemas
    - Self-Modification paths 9
    - Guided paths 29
    - Changelog paths 4
    - C2 paths 6
    - C1 paths 24
    - Repair paths 43
    - full-suite real-root/docs-history fingerprint passed with drift count 0
    - Full pytest: 1601/1601 passed, 0 failures, 0 errors
    - Finalized, committed, tagged, and pushed as `milestone-82AS-self-modification-boundary-tests` at `101eb3a`
  - Next: 82AT Plan — Self-Modification Router Extraction Plan
  - 82AT not started
  - 82AT Build — Self-Modification Router Extraction (complete locally, not committed)
    - 9 Self-Modification routes moved from `api_server.py` into `aether/interface/routers/self_modification_routes.py`
    - Did not modify action modules
    - Did not modify service modules
    - Did not modify api_models.py
    - Did not modify existing routers
    - locked `self_modification_router = APIRouter()`
    - locked exact route signatures/defaults preserved
    - locked exact direct-action call names/args preserved
    - locked all 9 routes as wrapped single-return pass-throughs
    - static-risk locked `aether/action/self_modification_cycle.py` unchanged
    - expected high-risk terms still present in module: apply_patch_proposal, rollback_patch_apply, write_text, Path(
    - forbidden terms still absent: collect_evidence, execute_tool, subprocess, os.system, requests., httpx., shutil, git
    - no endpoint invocation
    - no route function invocation
    - no self_modification action function invocation
    - no docs/history write
    - no runtime/private write
    - no real apply, rollback, evidence collection, or tool execution
    - OpenAPI exact match: 300 paths / 103 schemas
    - Self-Modification paths 9
    - Guided paths 29
    - Changelog paths 4
    - C2 paths 6
    - C1 paths 24
    - Repair paths 43
    - full-suite real-root/docs-history fingerprint passed with drift count 0
    - Full pytest: 1605/1605 passed, 0 failures, 0 errors
    - Finalized, committed, tagged, and pushed as `milestone-82AT-self-modification-router-extraction` at `f41e654`
  - Next: 82AU Plan — Protected/Core Route Boundary Tests Plan
  - 82AU not started
  - 82AU Build — Protected/Core Route Boundary Tests (complete locally, not committed)
    - 23 AST/OpenAPI-only boundary tests added in `tests/test_protected_core_routes_boundary.py`
    - Did not modify `aether/interface/api_server.py`
    - Did not modify routers
    - Did not modify action modules
    - Did not modify service modules
    - Did not modify api_models.py
    - Did not modify existing tests
    - locked 8 protected/core routes in `api_server.py` with exact operation IDs, signatures, call profiles, and control-flow profiles
    - locked no protected/core router files
    - locked import/dependency profile
    - locked high-risk terms absent from protected/core route bodies
    - no endpoint invocation
    - no TestClient
    - OpenAPI exact match: 300 paths / 103 schemas
    - Self-Modification paths 9
    - Guided paths 29
    - Changelog paths 4
    - C2 paths 6
    - C1 paths 24
    - Repair paths 43
    - full-suite real-root/docs-history fingerprint passed with drift count 0
    - Full pytest: 1628/1628 passed, 0 failures, 0 errors
    - Finalized, committed, tagged, and pushed as `milestone-82AU-protected-core-route-boundary-tests` at `7bc1a62`
  - Next: 82AV Plan — Protected/Core Extraction Decision or Thin Interface Stop/Reassessment
  - 82AV not started
  - 82AV Build — Protected/Core Thin Interface Decision Record (finalized, committed, tagged, pushed)
    - Added `docs/architecture/PROTECTED_CORE_INTERFACE_DECISION.md`
    - Decision accepted: stop extraction at protected/core boundary
    - `api_server.py` is intentionally defined as the Protected Core Interface
    - The final 8 protected/core routes remain in `api_server.py`
    - No protected/core router extraction planned unless reopened by a future decision record
    - Did not modify `aether/interface/api_server.py`
    - Did not modify routers
    - Did not create protected/core router files
    - Did not modify action modules
    - Did not modify service modules
    - Did not modify api_models.py
    - Did not modify existing tests
    - Did not modify `docs/THIN_INTERFACE_REFACTOR_PLAN.md`
    - Did not modify `docs/ARCHITECTURE.md`
    - Did not modify `docs/CONSTITUTION.md`
    - Did not modify existing docs
    - `api_server.py` remains at 8 direct `@app` protected/core routes
    - `api_server.py` remains at 22 include_router calls
    - zero `/action/*` routes remain in `api_server.py`
    - OpenAPI: 300 paths / 103 schemas
    - full-suite real-root/docs-history fingerprint passed with drift count 0
    - Full pytest: 1628/1628 passed, 0 failures, 0 errors
    - Finalized, committed, tagged, and pushed as `milestone-82AV-protected-core-interface-decision-record` at `063289a`
  - Next: 82AW Plan — Post-Refactor Closure and Next Development Selection
  - 82AW not started
  - 82AW Build — Post-Refactor Closure Record (complete locally, not committed)
    - Added `docs/architecture/POST_REFACTOR_CLOSURE.md`
    - Closed interface/thin-refactor phase
    - Confirmed action/orchestration extraction sequence is complete
    - Confirmed protected/core extraction boundary remains closed by 82AV decision
    - Confirmed `api_server.py` is intentionally complete as Protected Core Interface
    - Confirmed final 8 protected/core routes remain in `api_server.py`
    - Confirmed zero `/action/*` direct routes remain in `api_server.py`
    - Confirmed no protected/core router files exist
    - Confirmed next new-feature line should be `Milestone 83 Plan — Observation Record Store`
    - No api_server.py change
    - No router changes
    - No protected/core router files created
    - No action/service/api_models changes
    - No test changes
    - No existing docs changed
    - `docs/THIN_INTERFACE_REFACTOR_PLAN.md` unchanged
    - `docs/ARCHITECTURE.md` unchanged
    - `docs/CONSTITUTION.md` unchanged
    - `docs/architecture/PROTECTED_CORE_INTERFACE_DECISION.md` unchanged
    - `api_server.py` remains at 8 direct `@app` protected/core routes
    - `api_server.py` remains at 22 include_router calls
    - OpenAPI: 300 paths / 103 schemas
    - full-suite real-root/docs-history fingerprint passed with drift count 0
    - Full pytest: 1628/1628 passed, 0 failures, 0 errors
    - Finalized, committed, tagged, and pushed as `milestone-82AW-post-refactor-closure-record` at `70cb957`
  - Next: Milestone 83 Plan — Observation Record Store
  - Milestone 83 not started
  - 83A Build — Observation Record Boundary Tests (finalized, committed, tagged, pushed)
    - Added `tests/test_observation_record_boundary.py` (37 tests)
    - Locked pre-implementation boundary:
      - Observation builder exists (82B)
      - Observation Record Store not implemented
      - Observation router/service/store absent
      - No observation API models in api_models.py
      - No observation API paths or operation IDs in OpenAPI
      - api_server.py unchanged (8 routes, 22 include_router, zero /action/*)
      - OpenAPI remains 300 paths / 103 schemas
    - Confirmed future Observation implementation must use router/service/model/test structure
    - No production code changes
    - No api_server.py change
    - No router changes
    - No action/service/api_models changes
    - No existing tests changed
    - No docs changed
    - `docs/ARCHITECTURE.md` unchanged
    - `docs/CONSTITUTION.md` unchanged
    - `docs/THIN_INTERFACE_REFACTOR_PLAN.md` unchanged
    - `docs/architecture/PROTECTED_CORE_INTERFACE_DECISION.md` unchanged
    - `docs/architecture/POST_REFACTOR_CLOSURE.md` unchanged
    - Full pytest: 1665/1665 passed, 0 failures, 0 errors
    - real-root/docs-history fingerprint drift 0
    - Finalized, committed, tagged, and pushed as `milestone-83A-observation-record-boundary-tests` at `de3003a`
  - Next: 83B Plan — Observation Record Schema Foundation
  - 83B not started
  - 83B Build — Observation Record Schema Foundation (finalized, committed, tagged, pushed)
    - Added 5 simple Pydantic BaseModel schema classes in `aether/interface/api_models.py`:
      - ObservationRecordCreateRequest
      - ObservationRecordResponse
      - ObservationRecordListResponse
      - ObservationRecordUpdateStatusRequest
      - ObservationRecordCancelRequest
    - Added `tests/test_observation_record_schema.py` (33 tests)
    - Updated `tests/test_observation_record_boundary.py` (5 assertions changed from absent to present)
    - Confirmed schema-only scope:
      - no api_server.py change
      - no router change
      - no service/store/queue creation
      - no action module change
      - no endpoint implementation
      - no runtime behavior implementation
    - Confirmed schema style:
      - simple BaseModel only
      - no Field
      - no validators
      - no Literal
      - no Enum
      - no import from aether.action.observation_record
    - OpenAPI remains 300 paths / 103 schemas
    - Observation paths remain 0
    - Observation operation IDs remain 0
    - Full pytest: 1698/1698 passed, 0 failures, 0 errors
    - real-root/docs-history fingerprint drift 0
    - Finalized, committed, tagged, and pushed as `milestone-83B-observation-record-schema-foundation` at `8dd5ec0`
  - Next: 83C Plan — Observation Record Service and Store Foundation
  - 83C Plan — Observation Record Service and Store Foundation (complete; plan only)
    - Plan written to `/home/aether/summaries/milestone_83C_plan.txt`
    - Design decisions: queue module `aether/action/observation_record_queue.py`, service module `aether/action/services/observation_record_service.py`, storage `{get_private_dir()}/observation_records/observation_record_<id>.json`
    - First Build scope: create/get/list only (Option A); update_status/cancel deferred (no consumer yet; `cancelled` not in VALID_STATUSES; envelope-level `decision` field reserved)
    - Builder `aether/action/observation_record.py` and `api_models.py` unchanged; OpenAPI stays 300 paths / 103 schemas
  - 83C Build — Observation Record Service and Store Foundation (finalized, committed, tagged, pushed)
    - Added `aether/action/observation_record_queue.py`
    - Added `aether/action/services/observation_record_service.py`
    - Added `tests/test_observation_record_queue.py`
    - Added `tests/test_observation_record_service.py`
    - Updated `tests/test_observation_record_boundary.py`
    - Updated `tests/test_full_suite_private_persistence_isolation.py`
    - Updated `tests/conftest.py`
    - Implemented service/store functions:
      - save/load/list observation records
      - handle_create_observation_record
      - handle_get_observation_record
      - handle_list_observation_records
    - Confirmed deferred:
      - update_status not implemented
      - cancel not implemented
      - router/API endpoints not implemented
      - api_server.py unchanged
      - api_models.py unchanged
      - builder unchanged
    - Storage:
      - `{get_private_dir()}/observation_records/`
      - `observation_record_<observation_id>.json`
      - private persistence isolation registered in conftest and full-suite isolation test
    - OpenAPI remains 300 paths / 103 schemas
    - Observation paths remain 0
    - Observation operation IDs remain 0
    - Full pytest: 1798/1798 passed, 0 failures, 0 errors
    - real-root/docs/history fingerprint drift 0
    - Finalized, committed, tagged, and pushed as `milestone-83C-observation-record-service-and-store-foundation` at `007b030`
  - Next: 83D Plan — Observation Record Router and API Endpoints
  - 83D not started
  - Milestone 84 not started
