"""Static contract locks for the Milestone 94A boundary-only Build.

This module intentionally imports no Aether production module and performs no
endpoint, reader, executor, Observation Intake, persistence, or runtime call.
"""

from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "docs/architecture/MILESTONE_94A_GOVERNED_READ_ONLY_FILE_INSPECTION_BOUNDARY.md"
PROGRESS = ROOT / "PROGRESS.md"
CANONICAL = ROOT / "tests/test_progress_ledger_canonical_header.py"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _record() -> str:
    return _text(RECORD)


def _flat_record() -> str:
    return " ".join(_record().split())


def _header() -> str:
    return _text(PROGRESS).split("\n---\n", 1)[0]


def _calls(tree: ast.AST) -> set[str]:
    return {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }


def test_classification_is_boundary_contract_only():
    text = _record()
    assert "BOUNDARY / DESIGN / CONTRACT-LOCK BUILD ONLY" in text
    assert "Runtime capability: NONE" in text
    assert "Tool execution: NONE" in text
    assert "Configuration implementation: NONE" in text
    assert "Milestone 94B is NOT AUTHORIZED" in text
    assert "Milestone 94C is NOT DEFINED" in text
    assert "Production changes are zero" in text
    assert "README, Constitution, Architecture" in text


def test_parent_milestone_94_capability_purpose_is_exact():
    text = _flat_record()
    assert "Milestone 94 is OPEN and capability-driven" in text
    assert "exactly one governed, bounded, read-only file-inspection capability" in text
    assert "deny-by-default behavior for every other capability" in text
    assert "real observable result and deterministic verification" in text


def test_thinking_rule_inventory_is_restricted_to_3_7_8_9():
    text = _record()
    section = text.split("## 4. Correct Rule Inventory", 1)[1].split("## 5.", 1)[0]
    for rule in ("Rule 3", "Rule 7", "Rule 8", "Rule 9"):
        assert rule in section
    assert "Rule 6 is not a current Thinking rule" in section


def test_governance_rule_inventory_is_1_2_4_5_6():
    text = _record()
    section = text.split("Current authoritative Core Governance hard constraints", 1)[1]
    section = section.split("Rule 7 is a Soft Decision Signal", 1)[0]
    for rule in ("Rule 1", "Rule 2", "Rule 4", "Rule 5", "Rule 6"):
        assert rule in section
    assert "Rule 3" not in section


def test_strategy_c_is_selected():
    text = _flat_record()
    assert "Selected authorization strategy: STRATEGY C" in text
    assert "non-public, call-local, exact, one-shot" in text
    assert "one authoritative Governance evaluation" in text


def test_boolean_execution_flags_are_not_authority():
    text = _flat_record()
    for value in (
        "tool_execution_allowed",
        "execution_allowed",
        "policy_snapshot",
        "suggested_tool",
    ):
        assert value in text
    assert "tool_execution_allowed` remains false" in text
    assert "not authorization" in text


def test_exact_file_read_action_identity_is_locked():
    text = _flat_record()
    assert "file.restricted_read" in text
    assert "aether.action.restricted_file_reader.read_restricted_file" in text
    assert "permission class: `read_only`" in text


def test_direct_reader_bridge_rejects_generic_dispatch():
    text = _flat_record()
    assert "dedicated direct Action bridge" in text
    assert "must not use `execute_tool()`" in text
    assert "HTTP self-calling of `/action/file/read`" in text
    assert "duplicate reader implementation" in text


def test_scope_binding_is_exact_and_request_bound():
    text = _record()
    section = " ".join(
        text.split("## 7. Scope Binding and Lifetime", 1)[1]
        .split("## 8.", 1)[0]
        .split()
    )
    for phrase in (
        "exact capability",
        "exact bound implementation",
        "exact normalized target",
        "approved-root identity",
        "current execution attempt",
        "current request/task context",
        "bounded allowed parameters",
        "one dispatch only",
    ):
        assert phrase in section


def test_scope_lifetime_is_one_shot_and_non_replayable():
    text = _flat_record()
    for phrase in (
        "non-persistent",
        "non-serializable",
        "non-transferable",
        "non-replayable",
        "single-dispatch",
        "invalid after dispatch",
        "must not cross turns",
    ):
        assert phrase in text


def test_approval_persists_but_execution_authorization_does_not():
    text = _flat_record()
    assert "APPROVAL MAY PERSIST" in text
    assert "EXECUTION AUTHORIZATION MUST NOT PERSIST" in text
    assert "human-decision continuity evidence only" in text
    assert "not execution authority" in text


def test_pending_and_approved_records_are_not_executable_alone():
    text = _flat_record()
    assert "Pending approval never dispatches" in text
    assert "An approved record alone never dispatches" in text
    assert "not execution authority" in text
    assert "execution trigger" in text
    assert "approval ID" in text


def test_execution_time_governance_reauthorization_is_required():
    text = _record()
    section = text.split("## 9. Execution-Time Governance Reauthorization", 1)[1].split("## 10.", 1)[0]
    for phrase in (
        "identity integrity",
        "Rule 4 sensitive-term evidence",
        "risk and precedence",
        "approved-root policy",
        "exact normalized target and containment",
        "privacy conditions",
        "approval continuity",
    ):
        assert phrase in section
    assert "Changed material conditions fail closed" in section


def test_approval_cannot_trigger_automatic_or_background_execution():
    text = _flat_record()
    for phrase in (
        "no same-turn callback",
        "automatic continuation",
        "scheduler",
        "background wakeup",
        "auto execution after approval",
    ):
        assert phrase in text


def test_root_registration_is_manual_admin_configuration_edit():
    text = _flat_record()
    assert "ROOT_REGISTRATION_MECHANISM: MANUAL_ADMIN_CONFIG_EDIT" in text
    assert "config/aether.yaml" in text
    assert "aether/core/config.py" in text
    assert "No approved-root registration API" in text


def test_root_authority_denies_missing_malformed_and_implicit_sources():
    text = _flat_record()
    for phrase in (
        "Missing configuration",
        "an empty root list",
        "a malformed root list",
        "`/chat`, Thinking, the tool registry",
        "environment variables",
        "automatic project-root inference",
        "NOT IMPLEMENTED by 94A",
    ):
        assert phrase in text
    assert "/home/aether/projects/Aether" in text
    assert "not hardcoded as" in text


def test_cross_platform_containment_and_privacy_root_locks_are_present():
    text = _flat_record()
    for phrase in (
        "Windows/POSIX support",
        "project-relative root resolution",
        "Path.resolve()",
        "path-relationship containment",
        "traversal escape denial",
        "symlink-outside-root denial",
        "regular-file-only reads",
        "64 KiB target file limit",
        "bounded `max_chars`",
        "hard privacy or system-path denies",
    ):
        assert phrase in text


def test_privacy_filter_and_raw_content_boundary_are_locked():
    text = _flat_record()
    assert "Read-only is not privacy-safe" in text
    assert "Rule 4 before Action" in text
    assert "deterministic high-confidence" in text
    assert "No LLM, fuzzy model, or semantic classifier" in text
    assert "fail-closed behavior" in text
    assert "must not enter the scope, policy snapshot, approval records" in text
    assert "must not persist raw returned content" in text


def test_observation_intake_is_deferred_for_missing_provenance():
    text = _flat_record()
    assert "OBSERVATION_INTAKE: DEFER_FIRST_SLICE" in text
    for field in ("plan_step_id", "collector_contract_id", "evidence_items"):
        assert field in text
    assert "must not call `handle_observation_intake()`" in text
    assert "persist an Observation Record" in text


def test_action_observation_verification_are_distinct():
    text = _record()
    section = text.split("## 12. Observation Intake and Stage Separation", 1)[1].split("## 13.", 1)[0]
    for phrase in (
        "Action result: the actual bounded restricted-reader result",
        "Observation: the factual, privacy-filtered",
        "Verification: deterministic evaluation",
        "Observation does not authorize",
        "Verification does not execute or authorize",
    ):
        assert phrase in section


def test_verification_vocabulary_has_exactly_six_statuses():
    text = _record()
    section = text.split("## 13. Deterministic Verification Vocabulary", 1)[1].split("## 14.", 1)[0]
    statuses = (
        "VERIFIED_SUCCESS",
        "VERIFIED_PARTIAL",
        "DENIED",
        "NOT_FOUND",
        "CHANGED_DURING_READ",
        "INTERNAL_ERROR",
    )
    assert sum(section.count(status) for status in statuses) >= 6
    for status in statuses:
        assert status in section
    assert "No generic Verification Aggregator" in section


def test_toctou_contract_makes_no_false_atomicity_claim():
    text = _flat_record()
    for phrase in (
        "does not prove read-completion identity",
        "re-resolves immediately before reading",
        "pre/post identity/stat comparison is best-effort",
        "CHANGED_DURING_READ",
        "no silent retry",
        "no false atomicity claim",
    ):
        assert phrase in text


def test_public_trace_and_direct_api_compatibility_are_frozen():
    text = _flat_record()
    for phrase in (
        "94A changes none of the existing direct API semantics",
        "There is no ChatResponse expansion",
        "OpenAPI shape remains 304 paths / 108 schemas",
        "8 direct `@app` routes / 23 included routers / 0 direct `/action/*`",
        "no feature logic",
        "Thinking proposes; Governance authorizes",
        "must never claim Thinking executed or authorized",
    ):
        assert phrase in text


def test_boundary_test_is_static_and_has_no_runtime_imports_or_calls():
    source = _text(Path(__file__))
    tree = ast.parse(source)
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert not any(name.startswith("aether") for name in imports)
    assert not {"TestClient", "requests", "httpx"}.intersection(imports)
    calls = _calls(tree)
    assert not {
        "execute_tool",
        "read_restricted_file",
        "handle_observation_intake",
        "record_event",
        "create_approval_record",
        "write_text",
        "open",
    }.intersection(calls)
    assert "Runtime capability: NONE" in _record()
