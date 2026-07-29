# Cognitive Loop Trace

**Status:** Implemented (Milestones 81C-81D)  
**Applies to:** `POST /chat`  
**Storage:** Response-only — not persisted  

---

## Purpose

The `loop_trace` object provides **structured observability** of the cognitive loop execution inside `POST /chat`. It reports which stages ran, their status, timing metadata, safety flags, and record IDs — all as a **safe, deterministic summary** built after the loop completes.

`loop_trace` is **not** chain-of-thought.  
`loop_trace` is **not** hidden reasoning.  
`loop_trace` is **not** a log of internal variables or model prompts.  

It is a **read-only report** of what the loop did, derived entirely from already-public response fields. It does **not** influence loop behavior, grant permissions, or expose private data.

---

## Scope

- **Endpoint:** `POST /chat` only
- **Added:** Milestone 81C — Cognitive Loop Observability
- **Hardened:** Milestone 81D — Cognitive Loop Trace Hardening Tests
- **Response-only:** returned in the `/chat` JSON response under the `loop_trace` key
- **No persistence:** not written to disk, timeline, memory, graph, or any storage
- **No trace endpoint:** there is no GET /trace or similar retrieval endpoint
- **No history:** each response contains only its own trace

---

## Current Contract

### Top-level fields

| Field | Type | Description |
|---|---|---|
| `trace_id` | `str` | Unique per-execution ID — format `chat_<YYYYMMDD_HHMMSS>_<8hex>` |
| `loop_version` | `str` | Loop version string (`"0.1.0"`) |
| `started_at` | `str` | ISO 8601 timestamp of loop start |
| `completed_at` | `str` | ISO 8601 timestamp of loop completion |
| `duration_ms` | `int` | Wall-clock elapsed milliseconds |
| `status` | `str` | Overall trace status (`"completed"`, `"error"`) |
| `stages` | `list[dict]` | Ordered list of stage entries |
| `safety` | `dict` | Boolean safety flags mirrored from response |
| `records` | `dict` | Record ID references from the loop execution |
| `warnings` | `list[str]` | Aggregated warning strings |

### Stage entry fields

| Field | Type | Description |
|---|---|---|
| `name` | `str` | Stage identifier (snake_case) |
| `status` | `str` | `"completed"`, `"skipped"`, `"warning"`, or `"error"` |
| `summary` | `str` | Short deterministic description (≤120 chars, no newlines) |
| `warnings_count` | `int` | Number of warnings produced by this stage |

### Safety dict fields

| Field | Type | Always |
|---|---|---|
| `tool_execution_allowed` | `bool` | `false` |
| `tool_executed` | `bool` | `false` |
| `execution_allowed` | `bool` | `false` |
| `approval_required` | `bool` | `true` for high-risk, `false` for safe |

### Records dict fields

| Field | Type | Notes |
|---|---|---|
| `working_memory_event_ids` | `list[str]` | Always `[]` — WM event IDs are not exposed internally |
| `timeline_event_id` | `str \| None` | Event ID from timeline recording, or `None` if recording failed |
| `approval_id` | `str \| None` | Approval record ID for high-risk input, `None` otherwise |

---

## Current Stage Names

These 12 stages are recorded in order during `run_core_chat_loop()`. Each maps to one step in the `/chat` implementation:

| # | Stage | Summary example | Conditional |
|---|---|---|---|
| 1 | `perception` | `"Input classified as text, en, 11 chars"` | No |
| 2 | `identity_integrity` | `"Identity verified"` | No |
| 3 | `time_state` | `"Time state captured (Asia/Kuala_Lumpur)"` | No |
| 4 | `working_memory` | `"Recorded 2 events"` | No |
| 5 | `risk_classification` | `"Classified as low (casual_conversation)"` | No |
| 6 | `tool_suggestion` | `"Tool suggested: file.search (likely)"` or `"No tool matched"` | No |
| 7 | `thinking_policy` | `"Decision: respond_only"` | No |
| 8 | `policy_gate` | `"Decision: deny"` | No |
| 9 | `approval_request` | `"Approval not required"` or `"Approval required"` | No |
| 10 | `approval_queue` | `"Approval record created (id: abc12345...)"` or `"No approval record needed"` with status `"skipped"` | Yes — present only for high-risk; status `"skipped"` for safe |
| 11 | `timeline_recording` | `"Timeline event recorded"` or `"Timeline recording failed"` | No |
| 12 | `response_generation` | `"Response generated"` | No |

---

## Safety Boundary

### loop_trace MUST NOT expose

- Chain-of-thought reasoning
- Hidden or latent reasoning
- Raw model reasoning output
- Raw prompt text (system, developer, or user)
- User input text verbatim
- Perception `normalized_text`
- Metadata dict values
- `session_id`
- API keys, tokens, passwords, credentials
- Secret-like values
- Private file contents or file paths
- Raw tool outputs (no tools execute)
- Raw approval record contents
- Raw internal/private runtime data
- Developer or system instructions

### loop_trace MAY expose

- Stage names (the 12 identifiers above)
- Stage statuses (`completed`, `skipped`, `warning`, `error`)
- Short deterministic summaries (≤120 chars, no newlines, no raw data)
- Warning counts per stage
- Safety booleans (`tool_execution_allowed`, `tool_executed`, `execution_allowed`, `approval_required`)
- Record IDs (`approval_id`, `timeline_event_id`) — only those already in the response
- `working_memory_event_ids` (empty list — documented as known limitation)
- Timing metadata (`trace_id`, `started_at`, `completed_at`, `duration_ms`)
- Warnings list (same as `response.warnings`)

---

## Storage Decision

- **Response-only:** `loop_trace` is returned in the `/chat` response dict and exists only in memory during request handling
- **Not persisted** to disk, database, timeline, memory, graph, or files
- **Not written** to timeline events or working memory
- **No trace endpoint** exists
- **No trace history** — each response contains only its own trace

**Future persistence** (if ever needed) requires:
1. A separate milestone
2. Privacy review (stored traces contain stage summaries that must remain safe)
3. Explicit storage decision with constitutional alignment
4. New endpoint(s) for trace retrieval

---

## Relationship to Aether Execution Loop

### Target philosophical loop (from ARCHITECTURE.md §12.1)

```
Receive Goal → Understand → Think → Plan → Act → Observe → Verify → Critic → Repair → Learn → Report
```

### Current implemented /chat loop

```
Input
→ Perception
→ Identity Integrity Guard
→ Time
→ Working Memory
→ Risk Verification
→ Tool Suggestion
→ Thinking Policy
→ Policy Enforcement Gate
→ Approval Request Object
→ Approval Queue / approval_id (high-risk only)
→ Timeline
→ Structured Response
```

The `loop_trace.stages` array maps 1:1 to this current implementation. The trace supports the **Report** aspect of the target loop — it summarizes what occurred.

**Important:** The presence of `loop_trace` does **not** mean the full Act / Observe / Verify / Critic / Repair / Learn cycle is implemented. Future milestones may extend trace coverage as more runtime loop stages are implemented.

---

## Developer Extension Rules

### When adding a new stage

1. Use a deterministic `name` string (snake_case)
2. Use `status` from the allowed set: `"completed"`, `"skipped"`, `"warning"`, `"error"`
3. Call `build_stage(name=..., status=..., summary=..., warnings_count=...)`
4. Summary must:
   - Be ≤120 characters
   - Contain no newlines
   - Be derived from already-public response fields
   - Never include user text, `normalized_text`, `metadata`, `session_id`, secrets, or internal state not in the response
5. Append the stage to the `stages` list after the stage completes
6. Update `EXPECTED_SAFE_STAGES` in `tests/test_cognitive_loop_observability.py`
7. Update minimum stage count in `tests/test_cognitive_loop_trace_hardening.py`
8. Update this documentation if new safety considerations arise

### When changing loop_trace fields

- **Additive changes** (new optional fields) are preferred
- Existing fields must not be removed or renamed without a migration plan
- Update `tests/test_cognitive_loop_contract.py` — field list and assertions
- Update `tests/test_cognitive_loop_observability.py` — trace structure tests
- Update `tests/test_cognitive_loop_trace_hardening.py` — privacy/truncation tests
- Update `PROGRESS.md` and this documentation
- Keep response-only unless a future persistence milestone approves storage
- **Never** use `loop_trace` to control execution, approval, or permission
- `loop_trace` must remain **read-only metadata** that does not influence behavior

---

## Test Coverage

Three test files protect the `loop_trace` contract:

### `tests/test_cognitive_loop_contract.py` (11 tests)

- **Protects:** response field existence, types, side effects, safety invariants
- **Covers:** full contract field list (33 fields including `loop_trace`), assertion that `loop_trace` is a dict with a valid `trace_id`
- **Update when:** a field is added, removed, renamed, or its type/behavior changes

### `tests/test_cognitive_loop_observability.py` (10 tests)

- **Protects:** trace structure, stage names, summary safety, high-risk records, safety flag mirroring, hidden-reasoning blocking, empty input behaviour, endpoint isolation
- **Covers:** all 12 stage names present, summaries are safe strings (≤120 chars, no newlines), no forbidden substrings (`api_key`, `password`, `token`, `secret`, etc.), safety flags match response, records keys exist, `/awaken` and `/memory/working` unaffected
- **Update when:** a stage is added/removed, stage naming convention changes, new observability requirements

### `tests/test_cognitive_loop_trace_hardening.py` (7 tests)

- **Protects:** no leakage of user text, `normalized_text`, metadata values, `session_id`, or raw approval record content into stage summaries
- **Covers:** verification that stage summaries exclude all private input data, strict truncation to 120 chars, minimum stage count (≥12), raw approval record not dumped in trace
- **Update when:** summary derivation logic changes, new data sources are introduced for summaries

**All three files must pass before any `loop_trace` change is complete.**

---

## Future Work

Possible future milestones related to `loop_trace`:

| Topic | Requires |
|---|---|
| Persistent trace storage | Separate milestone, privacy review, new endpoint(s) |
| Trace visualization | UI milestone, depends on persistence |
| Trace correlation across sessions | Storage + query capability |
| Trace export (debugging/audit) | Storage + format decision |
| Deeper Act/Observe/Verify/Critic/Repair/Learn coverage | Implementation of those loop stages first |

None of these are implemented or claimed.
