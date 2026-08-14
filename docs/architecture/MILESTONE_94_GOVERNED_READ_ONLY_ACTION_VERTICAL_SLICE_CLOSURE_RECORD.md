# Milestone 94 Governed Read-Only Action Vertical Slice Closure Record

Classification: PARENT MILESTONE CLOSURE RECORD

This is an authorized documentation / static design-lock / ledger-only Build.
It is not a new architecture revision. `docs/ARCHITECTURE.md` is unchanged.

No production code, runtime, API, configuration, Observation Intake,
persistent Observation Record, Verification Aggregation, Critic, Repair,
Learning, second capability, generic execution, or Milestone 95 work is part
of this Build.

## 1. PM Closure Decision

- Milestone 94A: FINALIZED / DURABLE BOUNDARY.
- Milestone 94B: FINALIZED / GIT-DURABLE / PM-ACCEPTED.
- Milestone 94C: FINALIZED / GIT-DURABLE / PM-ACCEPTED.
- Milestone 94D: FINALIZED / GIT-DURABLE / PM-ACCEPTED externally.
- Milestone 94: functionally closure-ready.
- Milestone 95: NOT AUTHORIZED.

This Build creates the durable parent closure record and static closure lock.
It does not itself make the parent closure Git-durable.

## 2. Original Parent Objective

Milestone 94's original objective is preserved exactly:

> Connect exactly one governed, bounded, read-only file-inspection capability
> from /chat to a real observable result and deterministic verification while
> preserving deny-by-default behavior for every other capability.

The completed mapping is:

```text
/chat lifecycle
  -> exactly one governed bounded read-only file inspection
  -> explicit human approval where required
  -> explicit Phase-2 execution attempt
  -> fresh execution-time Core Governance
  -> real file.restricted_read Action
  -> factual call-local Observation
  -> deterministic capability Verification
  -> truthful result
```

The parent did not require generic tools, multiple capabilities, Observation
Intake integration, persistent Observation Records, Verification Aggregation,
Critic, Repair, Learning, background execution, automatic retry, generic
approval-to-execute, or a generic `/chat` executor.

## 3. Exact Authorized Write Set

Exactly four repository paths are authorized:

1. `docs/architecture/MILESTONE_94_GOVERNED_READ_ONLY_ACTION_VERTICAL_SLICE_CLOSURE_RECORD.md`
2. `tests/test_milestone_94_governed_read_only_action_vertical_slice_closure_design.py`
3. `PROGRESS.md`
4. `tests/test_progress_ledger_canonical_header.py`

Production paths: NONE. A fifth repository path requires PM scope extension.

## 4. 94A Contribution

94A is the durable boundary and contract lock, not runtime completion. It
established and froze:

- capability `file.restricted_read`;
- bounded read-only scope and exact grammar;
- manual approved-root authority;
- deny-by-default capability freeze;
- `APPROVE != EXECUTE`;
- Strategy C private, nonpersistent, one-shot authorization;
- call-local first-slice Observation design;
- the six-status capability Verification boundary;
- `OBSERVATION_INTAKE: DEFER_FIRST_SLICE`.

Durable identity:

- tag: `milestone-94A-governed-read-only-file-inspection-boundary`;
- commit: `e063f76fb3200c2bcedb473da841f6188f528389`.

94A did not implement runtime Action or reinterpret its design boundary as
runtime completion.

## 5. 94B Contribution

94B is the durable runtime producer. It established:

- `TWO_PHASE` and `APPROVE != EXECUTE`;
- `POST /action/file/execute-approved-read`;
- operation ID `execute_approved_read`;
- fresh execution-time Governance;
- approval fingerprint binding and atomic approval claim;
- replay prevention and private one-shot Strategy C scope;
- the restricted reader, privacy fail-closed behavior, and TOCTOU handling;
- call-local `RestrictedReadObservation`;
- deterministic capability Verification;
- no generic `execute_tool`, generic tool-service execution, or capability
  expansion in Phase 2.

Durable runtime identity:

- implementation commit: `583204a11f543ff689193321922c6c9761e4b117`;
- tag: `milestone-94B-governed-read-only-file-inspection-runtime-bridge`.

The later historical test-only durability correction remains separate and is
not relabeled as the 94B runtime implementation.

## 6. 94C Contribution

94C is the consumer-proof decision boundary. Its exact selected outcome is
`C_NOT_YET_COMPATIBLE`.

The following remain unproven and are not fabricated:

- `collector_contract_id`: NOT_PROVEN;
- `plan_step_id`: NOT_PROVEN;
- expected/observed: NOT_PROVEN;
- privacy-safe persistence: NOT_PROVEN;
- Observation Intake production caller: NONE;
- persistent 94B Observation Record: NONE;
- runtime Intake bridge: NOT JUSTIFIED;
- Observation Intake: `DEFER_FIRST_SLICE`.

This negative result supports Milestone 94 closure because the parent required a
real observable/verifiable restricted-read slice, not fabricated Observation
Intake integration. The 94C durable identity is:

- commit: `93b42ff64724afbee418998ad8ccb26c02632517`;
- tag: `milestone-94C-restricted-read-observation-consumer-proof-decision-record`.

## 7. 94D Contribution

94D is the final parent-runtime completion and uses Model D:

```text
POST /chat
  -> proposal / Governance / pending approval / STOP
human approval
  -> NO dispatch
POST /chat/restricted-read/resume
  -> existing M94B producer
  -> fresh Core Governance
  -> Strategy C
  -> Action
  -> call-local Observation
  -> deterministic Verification
  -> truthful capability-specific response
```

The exact continuation is:

- operation ID: `resume_restricted_read_chat`;
- capability: `file.restricted_read`;
- governed capability count: 1;
- generic `POST /chat` execution: NO;
- generic `/chat` execution authority: NO;
- `TWO_PHASE`: YES;
- `APPROVE != EXECUTE`: YES;
- approval auto-dispatch: NO;
- `approval_state`: DERIVED;
- pre-execution `verification_status`: NONE.

Durable identity:

- commit: `05fb4e94f0dfd174b91957be0d86912fdfd1d52b`;
- tag: `milestone-94D-canonical-chat-restricted-read-execution-completion`.

## 8. Parent Completion Matrix

| Parent obligation | 94A contribution | 94B contribution | 94C contribution | 94D contribution | Final status |
|---|---|---|---|---|---|
| exactly one capability | capability boundary | one producer | capability freeze | one resume capability | SATISFIED |
| read-only | read-only permission class | restricted reader | privacy boundary | same producer | SATISFIED |
| bounded | grammar and max bounds | bounded Action read | no fabricated consumer | bounded response | SATISFIED |
| governed | Strategy C contract | fresh Governance producer | no authority from Intake | fresh resume Governance | SATISFIED |
| from /chat | parent contract | producer available | consumer boundary preserved | explicit resume route | SATISFIED |
| real Action | future Action contract | direct Action bridge | producer remains isolated | resume reaches producer | SATISFIED |
| observable | call-local design | factual Observation | persistence deferred | call-local Observation | SATISFIED |
| deterministically verifiable | six-status boundary | capability verifier | no status fabrication | truthful response status | SATISFIED |
| other capabilities deny-by-default | capability freeze | no generic Phase 2 | generic freeze | generic `/chat` authority NO | SATISFIED |
| fresh execution-time Governance | required contract | implemented producer | no override | resume preserves re-evaluation | SATISFIED |
| approval does not equal execution | approval continuity | atomic claim | no Intake execution | approval and resume separated | SATISFIED |

All original parent obligations: SATISFIED.

## 9. Deferred and Future Work

The following are NOT REQUIRED FOR M94 CLOSURE and are not assigned to M95:

- Observation Intake integration;
- persistent Observation Record;
- `collector_contract_id` mapping;
- `plan_step_id` mapping;
- expected/observed producer mapping;
- privacy-safe Observation persistence;
- Verification Aggregation;
- Critic, Repair, or Learning integration;
- a second governed capability;
- generic capability execution or generic `/chat` executor;
- automatic retry or background execution.

Each requires a separately authorized future milestone if ever justified.

## 10. Architecture Safety Statement

Milestone 94 did not change the Aether one-mind identity model, nine cognitive
organs, Core Governance ownership, Core Coordination ownership, ASC
architecture, canonical Execution Loop, the rule that Time provides context
but not authority, Resource Observation reports / Governance decides, the
Protected Core Interface boundary, or Observation/Verification future-consumer
gates.

Thinking proposes. Governance authorizes. Verification supplies evidence.
Action executes only within authorization.

## 11. Interface and Regression Baseline

Current interface closure baseline:

- OpenAPI: 306 paths / 112 schemas;
- operation IDs: `resume_restricted_read_chat`, `execute_approved_read`;
- `api_server`: 8 direct `@app` routes / 23 `include_router` / 0 direct
  `/action/*`;
- `ChatRequest`: UNCHANGED;
- `ChatResponse`: UNCHANGED;
- no generic execution API, new path, new schema, or new operation ID.

Durable pre-closure-record regression baseline:

- M94D: 36/36;
- M94A: 24/24;
- M94B: 224/224;
- M94C: 6/6;
- Observation: 472/472;
- Rule migration: 177/177;
- Canonical: 23/23;
- Progress: 362/362;
- Changelog: 4/4;
- M93 Rule4: 26/26;
- OpenAPI family: 653/653;
- Full: 2952/2952;
- failures: 0;
- errors: 0;
- warnings: 9;
- warning delta: 0.

The eight static closure tests are additive. The verified Build full suite is
2960/2960; the 2952 count remains the durable M94D pre-closure baseline.

## 12. Closure Status and Temporal Truth

The truthful dirty-Build state is:

```text
Milestone 94 functional obligations: COMPLETE
Milestone 94 closure record: COMPLETE LOCALLY
Milestone 94 durable closure: PENDING GIT FINALIZATION AND PM ACCEPTANCE
M95: NOT AUTHORIZED
```

The record makes no claim of a future closure commit SHA, closure tag, remote
publication, or future PM acceptance. Temporal truth passes for:

- STATE A: dirty local Build;
- STATE B: future closure commit;
- STATE C: future push;
- STATE D: future PM durable acceptance.

Git remains authoritative for durability, tags, and publication. No Git
lifecycle operation is part of this Build.

## 13. Finalization Boundary

Milestone 94 durable closure requires later verification of the exact
four-path commit, protected and production freezes, the focused and full
regression gates, any authorized closure tag and publication, and separate
human/project-manager closure acceptance. Until then, Milestone 94 remains
OPEN / NOT CLOSED YET.
