"""Static content locks for the Milestone 94 parent closure record."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "docs/architecture/MILESTONE_94_GOVERNED_READ_ONLY_ACTION_VERTICAL_SLICE_CLOSURE_RECORD.md"
PROGRESS = ROOT / "PROGRESS.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_title_and_parent_objective_are_locked():
    text = _text(RECORD)
    assert text.startswith("# Milestone 94 Governed Read-Only Action Vertical Slice Closure Record\n")
    assert "Classification: PARENT MILESTONE CLOSURE RECORD" in text
    assert "exactly one governed, bounded, read-only file-inspection capability" in text
    assert "real observable result and deterministic verification" in text
    assert "deny-by-default behavior for every other capability" in text


def test_94a_durable_boundary_identity_and_contribution_are_locked():
    text = _text(RECORD)
    for marker in (
        "## 4. 94A Contribution",
        "file.restricted_read",
        "bounded read-only scope",
        "manual approved-root authority",
        "APPROVE != EXECUTE",
        "Strategy C private, nonpersistent, one-shot authorization",
        "OBSERVATION_INTAKE: DEFER_FIRST_SLICE",
        "milestone-94A-governed-read-only-file-inspection-boundary",
        "e063f76fb3200c2bcedb473da841f6188f528389",
        "not runtime completion",
    ):
        assert marker in text


def test_94b_durable_runtime_identity_and_producer_are_locked():
    text = _text(RECORD)
    for marker in (
        "## 5. 94B Contribution",
        "TWO_PHASE",
        "POST /action/file/execute-approved-read",
        "execute_approved_read",
        "fresh execution-time Governance",
        "approval fingerprint binding",
        "atomic approval claim",
        "replay prevention",
        "RestrictedReadObservation",
        "no generic `execute_tool`",
        "583204a11f543ff689193321922c6c9761e4b117",
        "milestone-94B-governed-read-only-file-inspection-runtime-bridge",
    ):
        assert marker in text


def test_94c_negative_consumer_proof_and_deferred_intake_are_locked():
    text = _text(RECORD)
    for marker in (
        "## 6. 94C Contribution",
        "C_NOT_YET_COMPATIBLE",
        "collector_contract_id`: NOT_PROVEN",
        "plan_step_id`: NOT_PROVEN",
        "expected/observed: NOT_PROVEN",
        "privacy-safe persistence: NOT_PROVEN",
        "Observation Intake production caller: NONE",
        "persistent 94B Observation Record: NONE",
        "runtime Intake bridge: NOT JUSTIFIED",
        "DEFER_FIRST_SLICE",
        "supports Milestone 94 closure",
        "fabricated Observation",
        "93b42ff64724afbee418998ad8ccb26c02632517",
        "milestone-94C-restricted-read-observation-consumer-proof-decision-record",
    ):
        assert marker in text


def test_94d_model_d_identity_and_chat_continuation_are_locked():
    text = _text(RECORD)
    for marker in (
        "## 7. 94D Contribution",
        "Model D",
        "POST /chat/restricted-read/resume",
        "resume_restricted_read_chat",
        "file.restricted_read",
        "governed capability count: 1",
        "generic `POST /chat` execution: NO",
        "generic `/chat` execution authority: NO",
        "approval auto-dispatch: NO",
        "approval_state`: DERIVED",
        "pre-execution `verification_status`: NONE",
        "05fb4e94f0dfd174b91957be0d86912fdfd1d52b",
        "milestone-94D-canonical-chat-restricted-read-execution-completion",
    ):
        assert marker in text


def test_parent_completion_matrix_is_fully_satisfied():
    text = _text(RECORD)
    section = text.split("## 8. Parent Completion Matrix", 1)[1].split(
        "## 9.", 1
    )[0]
    assert "Parent obligation" in section
    assert "94A contribution" in section
    assert "94B contribution" in section
    assert "94C contribution" in section
    assert "94D contribution" in section
    assert section.count("SATISFIED") == 12
    assert "All original parent obligations: SATISFIED." in section


def test_deferred_work_is_explicitly_outside_closure_and_m95():
    text = _text(RECORD)
    section = text.split("## 9. Deferred and Future Work", 1)[1].split(
        "## 10.", 1
    )[0]
    for marker in (
        "NOT REQUIRED FOR M94 CLOSURE",
        "Observation Intake integration",
        "persistent Observation Record",
        "collector_contract_id",
        "plan_step_id",
        "Verification Aggregation",
        "Critic",
        "Repair",
        "Learning",
        "second governed capability",
        "generic `/chat` executor",
        "automatic retry",
        "background execution",
        "not assigned to M95",
    ):
        assert marker in section


def test_closure_safety_lifecycle_and_no_generic_authority_are_locked():
    text = _text(RECORD)
    for marker in (
        "Thinking proposes. Governance authorizes. Verification supplies evidence.",
        "Action executes only within authorization.",
        "OpenAPI: 306 paths / 112 schemas",
        "ChatRequest`: UNCHANGED",
        "ChatResponse`: UNCHANGED",
        "no generic execution API",
        "Milestone 94 functional obligations: COMPLETE",
        "Milestone 94 closure record: COMPLETE LOCALLY",
        "Milestone 94 durable closure: PENDING GIT FINALIZATION AND PM ACCEPTANCE",
        "STATE A: dirty local Build",
        "STATE B: future closure commit",
        "STATE C: future push",
        "STATE D: future PM durable acceptance",
        "M95: NOT AUTHORIZED",
        "No Git\nlifecycle operation is part of this Build.",
    ):
        assert marker in text
