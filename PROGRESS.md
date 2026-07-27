# Aether Project Progress Ledger

**Last updated:** Milestone 74A — Apply Executor Plan Record Store Core
**Aether version:** 0.2.0  
**Pipeline maturity:** Full safety chain built through apply_executor_plan_record (with persist, list/read/cancel/reject/approve-plan-intent)

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
```

Important state:
- All records persist as JSON files under `/home/aether/data/private/<record_type>/`
- Every record has a unique ID, timestamps, and safety flags
- `approved_intent`, `approved_execution_intent`, `approved_contract_intent` only **record intent** — they do NOT authorize execution or apply
- `approved_plan_intent` only records plan review intent — it does NOT authorize execution, apply, evidence collection, or rollback plan attachment
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

### 71-74: Executor Contract, Plan, and Record Store
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

---

## 7. Current Test Baseline

As of Milestone 74A:
- **Pytest:** 1095 passed, 0 failures (was 1014 after 73C, +81 from 74A tests)
- **Compile:** All 29 modules compiled successfully
- **Git safety:** Clean — no diffs on README.md, ARCHITECTURE.md, code_reviewer.py
- **Trailing whitespace:** Clean
- **Private/runtime paths:** Not tracked by git
- **Test modules:**
  - `tests/test_apply_executor_plan.py` — 56 unit tests
  - `tests/test_apply_executor_contract_queue.py` — 48 unit tests
  - `tests/test_apply_executor_contract.py` — 44 unit tests
  - `tests/test_apply_execution_gate_queue.py` — 41 unit tests
- `tests/test_apply_execution_gate_request.py` — 35 unit tests
- `tests/test_apply_executor_plan_queue.py` — 48 unit tests (Milestone 74A)
  - `tests/test_human_authorization_queue.py` — 42 unit tests
  - `tests/test_human_apply_authorization_request.py` — existing
  - `tests/test_human_authorization_queue.py` — existing
  - `tests/test_chat_api.py` — ~280 API integration tests
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

**Milestone 75 — Apply Executor Evidence Contract Object**

Expected chain continuation:
```text
apply_executor_plan_record (persisted, can be approved_plan_intent/rejected/cancelled)
→ apply_executor_evidence_contract (object to declare evidence requirements)
→ apply executor evidence contract record
→ evidence collection (future milestone)
→ real apply execution (much later)
```

Clarifications:
- Milestone 75 should declare exact evidence collection requirements before any execution attempt
- It must NOT collect evidence yet unless explicitly designed in a later milestone
- It must NOT execute apply
- It must NOT authorize execution/apply
- approved_plan_intent does NOT trigger evidence collection

---

## 11. Prompt Rule for Future OpenCode Tasks

> "Every future OpenCode prompt must begin by instructing OpenCode to read PROGRESS.md before editing. Every future milestone must update PROGRESS.md and write a milestone summary under /home/aether/summaries/."

Also:
> "When asked to continue with 'next', use PROGRESS.md to determine the next safe milestone."

---

## 12. File Summary (Git Status)

**New files added across milestones:**
- `aether/action/apply_executor_plan.py` — plan builder (Milestone 73A)
- `aether/action/apply_executor_plan_queue.py` — plan record store (Milestone 74A)
- `aether/action/apply_executor_contract.py` — contract builder (Milestone 71A)
- `aether/action/apply_execution_gate_queue.py` — execution gate store (Milestone 70A)
- `aether/action/apply_execution_gate_request.py` — execution gate request builder (Milestone 69A)
- `tests/test_apply_executor_plan.py` — 56 unit tests
- `tests/test_apply_executor_contract_queue.py` — 48 unit tests
- `tests/test_apply_executor_contract.py` — 44 unit tests
- `tests/test_apply_execution_gate_queue.py` — 41 unit tests
- `tests/test_apply_execution_gate_request.py` — 35 unit tests

**Modified files:**
- `aether/interface/api_server.py` — API endpoints for all CRUD operations
- `tests/test_chat_api.py` — API integration tests for each milestone

**No changes to:**
- `README.md`
- `docs/ARCHITECTURE.md`
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
