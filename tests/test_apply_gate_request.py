"""Tests for Apply Gate Request Builder (Milestone 65A).

Verifies that build_apply_gate_request produces correct apply gate requests
from verification_verdict_records. No execution, apply, or rollback occurs.
"""

from __future__ import annotations

import pytest


@pytest.fixture()
def _build():
    from aether.action.apply_gate_request import build_apply_gate_request
    return build_apply_gate_request


@pytest.fixture()
def clean_pass_record():
    """Create a clean pass verification verdict record."""
    verif = {
        "decision": "pass",
        "reason": "All checks passed.",
        "simulation_result_id": "sim-001",
        "simulation_plan_id": "plan-1",
        "dry_run_id": "dr-1",
        "requested_action": {"tool_id": "test.tool", "action_type": "status_check"},
        "checks": [],
        "evidence_summary": [],
        "unresolved_risks": [{"name": "real_apply_not_authorized", "severity": "medium"}],
        "blocking_reasons": [],
        "recommended_next_step": "Proceed to future gate.",
        "apply_allowed": False,
        "rollback_allowed": False,
        "execution_allowed": False,
        "tool_execution_allowed": False,
        "dry_run_execution_allowed": False,
        "simulation_execution_allowed": False,
        "verdict_apply_allowed": False,
        "metadata": {"source": "simulation_verdict_builder", "schema_version": "1.0"},
        "warnings": [],
    }
    return {
        "verification_verdict_id": "vv-id-001",
        "status": "pending",
        "verification_verdict": verif,
        "verdict_decision": "pass",
        "created_at": "2026-01-01T00:00:00+00:00",
        "updated_at": "2026-01-01T00:00:00+00:00",
        "decision": "pass",
        "decided_at": None,
        "reviewer": None,
        "decision_reason": None,
        "verdict_persisted": True,
        "apply_authorized": False,
        "simulation_executed": False,
        "execution_allowed": False,
        "tool_execution_allowed": False,
        "dry_run_execution_allowed": False,
        "simulation_execution_allowed": False,
        "apply_allowed": False,
        "rollback_allowed": False,
        "verdict_apply_allowed": False,
        "metadata": {},
        "warnings": [],
    }


# ======================== TEST 1: MISSING RECORD → BLOCKED ======================== #

class TestMissingRecord:
    def test_missing_record_returns_blocked(self, _build):
        agr = _build(verification_verdict_record=None)
        assert agr is not None
        assert agr["decision"] == "blocked"
        assert agr["reason"] == "Verification verdict record was not found."
        assert agr["apply_gate_required"] is False
        assert agr["verification_verdict_id"] is None
        assert agr["apply_authorized"] is False
        assert agr["apply_allowed"] is False
        assert agr["execution_allowed"] is False
        assert agr["tool_execution_allowed"] is False
        assert agr["dry_run_execution_allowed"] is False
        assert agr["simulation_execution_allowed"] is False
        assert agr["apply_gate_execution_allowed"] is False

    def test_missing_record_blocking_reasons(self, _build):
        agr = _build(verification_verdict_record=None)
        assert "Verification verdict record was not found." in agr["blocking_reasons"]

    def test_missing_record_next_step(self, _build):
        agr = _build(verification_verdict_record=None)
        assert "Create or provide a valid verification verdict record" in agr["recommended_next_step"]


# ======================== TEST 2: CANCELLED RECORD → BLOCKED ======================== #

class TestCancelledRecord:
    @staticmethod
    def _cancelled_record():
        verif = {
            "decision": "pass",
            "simulation_result_id": "sim-002",
            "simulation_plan_id": "plan-2",
            "dry_run_id": "dr-2",
            "requested_action": None,
            "checks": [],
            "unresolved_risks": [],
            "blocking_reasons": [],
            "apply_allowed": False,
            "execution_allowed": False,
            "tool_execution_allowed": False,
            "dry_run_execution_allowed": False,
            "simulation_execution_allowed": False,
            "rollback_allowed": False,
            "verdict_apply_allowed": False,
            "metadata": {},
            "warnings": [],
        }
        return {
            "verification_verdict_id": "vv-id-cancelled",
            "status": "cancelled",
            "verification_verdict": verif,
            "verdict_decision": "pass",
            "apply_authorized": False,
        }

    def test_cancelled_record_returns_blocked(self, _build):
        rec = self._cancelled_record()
        agr = _build(rec)
        assert agr["decision"] == "blocked"
        assert agr["reason"] == "Verification verdict record is not pending."
        assert agr["verification_verdict_record_status"] == "cancelled"
        assert "Record status is not pending." in agr["blocking_reasons"]
        assert agr["apply_authorized"] is False


# ======================== TEST 3: APPLY_AUTHORIZED TRUE → BLOCKED ======================== #

class TestApplyAuthorizedTrue:
    def test_apply_authorized_true_returns_blocked(self, _build, clean_pass_record):
        clean_pass_record["apply_authorized"] = True
        agr = _build(clean_pass_record)
        assert agr["decision"] == "blocked"
        assert agr["reason"] == "Verification verdict record is unexpectedly marked apply-authorized."
        assert "apply_authorized is true." in agr["blocking_reasons"]
        assert agr["apply_authorized"] is False


# ======================== TEST 4: MISSING VERIFICATION_VERDICT → NOT_ELIGIBLE ======================== #

class TestMissingVerdict:
    @staticmethod
    def _no_verdict_record():
        return {
            "verification_verdict_id": "vv-no-verdict",
            "status": "pending",
            "verification_verdict": None,
            "verdict_decision": None,
            "apply_authorized": False,
        }

    def test_missing_verdict_returns_not_eligible(self, _build):
        rec = self._no_verdict_record()
        agr = _build(rec)
        assert agr["decision"] == "not_eligible"
        assert agr["reason"] == "Verification verdict payload is missing or invalid."
        assert agr["apply_authorized"] is False

    def test_no_verdict_has_unresolved_risk(self, _build):
        rec = self._no_verdict_record()
        agr = _build(rec)
        names = [r["name"] for r in agr["unresolved_risks"]]
        assert "missing_verdict_payload" in names


# ======================== TEST 5: WARNING VERDICT → NOT_ELIGIBLE ======================== #

class TestWarningVerdict:
    @staticmethod
    def _warning_record():
        verif = {
            "decision": "warning",
            "simulation_result_id": "sim-warn",
            "simulation_plan_id": "plan-w",
            "dry_run_id": "dr-w",
            "requested_action": None,
            "unresolved_risks": [{"name": "some_risk", "severity": "medium"}],
            "blocking_reasons": [],
            "apply_allowed": False,
            "execution_allowed": False,
            "tool_execution_allowed": False,
            "dry_run_execution_allowed": False,
            "simulation_execution_allowed": False,
            "rollback_allowed": False,
            "verdict_apply_allowed": False,
            "metadata": {},
            "warnings": [],
        }
        return {
            "verification_verdict_id": "vv-warning",
            "status": "pending",
            "verification_verdict": verif,
            "verdict_decision": "warning",
            "apply_authorized": False,
        }

    def test_warning_verdict_returns_not_eligible(self, _build):
        rec = self._warning_record()
        agr = _build(rec)
        assert agr["decision"] == "not_eligible"
        assert agr["reason"] == "Verification verdict has warnings and is not eligible for apply review."
        assert "Verification verdict decision is warning." in agr["blocking_reasons"]
        assert agr["apply_authorized"] is False


# ======================== TEST 6: FAIL VERDICT → BLOCKED ======================== #

class TestFailVerdict:
    @staticmethod
    def _fail_record():
        verif = {
            "decision": "fail",
            "simulation_result_id": "sim-fail",
            "simulation_plan_id": "plan-f",
            "dry_run_id": "dr-f",
            "requested_action": None,
            "unresolved_risks": [{"name": "high_fail", "severity": "high"}],
            "blocking_reasons": ["high_fail"],
            "apply_allowed": False,
            "execution_allowed": False,
            "tool_execution_allowed": False,
            "dry_run_execution_allowed": False,
            "simulation_execution_allowed": False,
            "rollback_allowed": False,
            "verdict_apply_allowed": False,
            "metadata": {},
            "warnings": [],
        }
        return {
            "verification_verdict_id": "vv-fail",
            "status": "pending",
            "verification_verdict": verif,
            "verdict_decision": "fail",
            "apply_authorized": False,
        }

    def test_fail_verdict_returns_blocked(self, _build):
        rec = self._fail_record()
        agr = _build(rec)
        assert agr["decision"] == "blocked"
        assert agr["reason"] == "Verification verdict failed."
        assert "Verification verdict decision is fail." in agr["blocking_reasons"]
        assert agr["apply_authorized"] is False


# ======================== TEST 7: BLOCKED VERDICT → BLOCKED ======================== #

class TestBlockedVerdict:
    @staticmethod
    def _blocked_record():
        verif = {
            "decision": "blocked",
            "simulation_result_id": "sim-block",
            "simulation_plan_id": "plan-b",
            "dry_run_id": "dr-b",
            "requested_action": None,
            "unresolved_risks": [],
            "blocking_reasons": ["some_block"],
            "apply_allowed": False,
            "execution_allowed": False,
            "tool_execution_allowed": False,
            "dry_run_execution_allowed": False,
            "simulation_execution_allowed": False,
            "rollback_allowed": False,
            "verdict_apply_allowed": False,
            "metadata": {},
            "warnings": [],
        }
        return {
            "verification_verdict_id": "vv-blocked",
            "status": "pending",
            "verification_verdict": verif,
            "verdict_decision": "blocked",
            "apply_authorized": False,
        }

    def test_blocked_verdict_returns_blocked(self, _build):
        rec = self._blocked_record()
        agr = _build(rec)
        assert agr["decision"] == "blocked"
        assert agr["reason"] == "Verification verdict is blocked."
        assert "Verification verdict decision is blocked." in agr["blocking_reasons"]
        assert agr["apply_authorized"] is False


# ======================== TEST 8: UNKNOWN DECISION → BLOCKED ======================== #

class TestUnknownDecision:
    @staticmethod
    def _unknown_record():
        verif = {
            "decision": "unknown_decision_xyz",
            "simulation_result_id": "sim-unk",
            "simulation_plan_id": "plan-u",
            "dry_run_id": "dr-u",
            "requested_action": None,
            "unresolved_risks": [],
            "blocking_reasons": [],
            "apply_allowed": False,
            "execution_allowed": False,
            "tool_execution_allowed": False,
            "dry_run_execution_allowed": False,
            "simulation_execution_allowed": False,
            "rollback_allowed": False,
            "verdict_apply_allowed": False,
            "metadata": {},
            "warnings": [],
        }
        return {
            "verification_verdict_id": "vv-unknown",
            "status": "pending",
            "verification_verdict": verif,
            "verdict_decision": "unknown_decision_xyz",
            "apply_authorized": False,
        }

    def test_unknown_verdict_decision_returns_blocked(self, _build):
        rec = self._unknown_record()
        agr = _build(rec)
        assert agr["decision"] == "blocked"
        assert agr["reason"] == "Unsupported verification verdict decision."
        assert "Unsupported verdict decision:" in agr["blocking_reasons"][0]
        assert agr["apply_authorized"] is False


# ======================== TESTS 9-13: CLEAN PASS VERDICT ======================== #

class TestCleanPassVerdict:
    def test_clean_pass_returns_eligible(self, _build, clean_pass_record):
        agr = _build(clean_pass_record)
        assert agr["decision"] == "eligible_for_human_review"
        assert agr["apply_gate_required"] is True

    def test_eligible_still_has_apply_authorized_false(self, _build, clean_pass_record):
        agr = _build(clean_pass_record)
        assert agr["apply_authorized"] is False

    def test_eligible_still_has_apply_allowed_false(self, _build, clean_pass_record):
        agr = _build(clean_pass_record)
        assert agr["apply_allowed"] is False

    def test_eligible_all_flags_false(self, _build, clean_pass_record):
        agr = _build(clean_pass_record)
        assert agr["execution_allowed"] is False
        assert agr["tool_execution_allowed"] is False
        assert agr["dry_run_execution_allowed"] is False
        assert agr["simulation_execution_allowed"] is False
        assert agr["apply_gate_execution_allowed"] is False
        assert agr["rollback_allowed"] is False


# ======================== TEST 14: ELIGIBILITY CHECKS INCLUDE ALL 8 ======================== #

class TestEligibilityChecks:
    def test_includes_all_eight_checks(self, _build, clean_pass_record):
        agr = _build(clean_pass_record)
        names = [c["name"] for c in agr["eligibility_checks"]]
        expected = [
            "verdict_record_pending", "verdict_persisted", "verdict_decision_pass",
            "apply_not_authorized_yet", "apply_flags_blocked", "execution_flags_blocked",
            "unresolved_risks_only_real_apply", "blocking_reasons_empty",
        ]
        for name in expected:
            assert name in names, f"Missing check: {name}"

    def test_all_checks_pass_for_clean_record(self, _build, clean_pass_record):
        agr = _build(clean_pass_record)
        for c in agr["eligibility_checks"]:
            assert c["passed"] is True, f"Check {c['name']} should pass but returned {c}"


# ======================== TESTS 16-19: CHECK SEVERITY-BASED DECISIONS ======================== #

class TestSeverityDecisions:
    def test_critical_check_failure_blocks(self, _build):
        # Break apply_not_authorized_yet by setting apply_authorized=True
        verif = {
            "decision": "pass",
            "simulation_result_id": "sim-crit",
            "simulation_plan_id": "plan-c",
            "dry_run_id": "dr-c",
            "requested_action": None,
            "unresolved_risks": [],
            "blocking_reasons": [],
            "apply_allowed": True,
            "execution_allowed": False,
            "tool_execution_allowed": False,
            "dry_run_execution_allowed": False,
            "simulation_execution_allowed": False,
            "rollback_allowed": False,
            "verdict_apply_allowed": False,
            "metadata": {},
            "warnings": [],
        }
        rec = {
            "verification_verdict_id": "vv-crit",
            "status": "pending",
            "verification_verdict": verif,
            "verdict_decision": "pass",
            "apply_authorized": False,
            "apply_authorized_override": True,  # We'll manually set below
        }
        rec["apply_authorized"] = True
        agr = _build(rec)
        assert agr["decision"] == "blocked"

    def test_high_check_failure_blocks(self, _build):
        # Break apply_flags_blocked (critical) by setting verdict_apply_allowed=True in verif
        verif = {
            "decision": "pass",
            "simulation_result_id": "sim-crit2",
            "simulation_plan_id": "plan-c2",
            "dry_run_id": "dr-c2",
            "requested_action": None,
            "unresolved_risks": [],
            "blocking_reasons": [],
            "apply_allowed": False,
            "execution_allowed": False,
            "tool_execution_allowed": False,
            "dry_run_execution_allowed": False,
            "simulation_execution_allowed": False,
            "rollback_allowed": False,
            "verdict_apply_allowed": True,
            "metadata": {},
            "warnings": [],
        }
        rec = {
            "verification_verdict_id": "vv-crit2",
            "status": "pending",
            "verification_verdict": verif,
            "verdict_decision": "pass",
            "apply_authorized": False,
            "verdict_persisted": True,
        }
        agr = _build(rec)
        assert agr["decision"] == "blocked"

    def test_medium_check_failure_returns_not_eligible(self, _build):
        verif = {
            "decision": "pass",
            "simulation_result_id": "sim-med2",
            "simulation_plan_id": "plan-m2",
            "dry_run_id": "dr-m2",
            "requested_action": None,
            "unresolved_risks": [{"name": "real_apply_not_authorized", "severity": "medium"}],
            "blocking_reasons": ["some_reason"],  # Breaks blocking_reasons_empty (medium)
            "apply_allowed": False,
            "execution_allowed": False,
            "tool_execution_allowed": False,
            "dry_run_execution_allowed": False,
            "simulation_execution_allowed": False,
            "rollback_allowed": False,
            "verdict_apply_allowed": False,
            "metadata": {},
            "warnings": [],
        }
        rec = {
            "verification_verdict_id": "vv-med2",
            "status": "pending",
            "verification_verdict": verif,
            "verdict_decision": "pass",
            "apply_authorized": False,
            "verdict_persisted": True,
            "apply_allowed": False,
            "verdict_apply_allowed": False,
            "execution_allowed": False,
            "tool_execution_allowed": False,
            "dry_run_execution_allowed": False,
            "simulation_execution_allowed": False,
        }
        agr = _build(rec)
        assert agr["decision"] == "not_eligible"

    def test_low_check_failure_returns_not_eligible(self, _build):
        verif = {
            "decision": "pass",
            "simulation_result_id": "sim-low2",
            "simulation_plan_id": "plan-l2",
            "dry_run_id": "dr-l2",
            "requested_action": None,
            "unresolved_risks": [{"name": "real_apply_not_authorized", "severity": "medium"}],
            "blocking_reasons": [],
            "apply_allowed": False,
            "execution_allowed": False,
            "tool_execution_allowed": False,
            "dry_run_execution_allowed": False,
            "simulation_execution_allowed": False,
            "rollback_allowed": False,
            "verdict_apply_allowed": False,
            "metadata": {},
            "warnings": [],
        }
        rec = {
            "verification_verdict_id": "vv-low2",
            "status": "pending",
            "verification_verdict": verif,
            "verdict_decision": "pass",
            "apply_authorized": False,
            "verdict_persisted": False,  # Break verdict_persisted (low)
            "apply_allowed": False,
            "verdict_apply_allowed": False,
            "execution_allowed": False,
            "tool_execution_allowed": False,
            "dry_run_execution_allowed": False,
            "simulation_execution_allowed": False,
        }
        agr = _build(rec)
        assert agr["decision"] == "not_eligible"


# ======================== TESTS 20-22: SPECIFIC CHECK BEHAVIORS ======================== #

class TestSpecificChecks:
    def test_unresolved_risks_only_real_apply_passes(self, _build, clean_pass_record):
        agr = _build(clean_pass_record)
        chk = next(c for c in agr["eligibility_checks"] if c["name"] == "unresolved_risks_only_real_apply")
        assert chk["passed"] is True

    def test_unresolved_risks_only_real_apply_fails_with_extra(self, _build):
        verif = {
            "decision": "pass",
            "simulation_result_id": "sim-extra",
            "simulation_plan_id": "plan-e",
            "dry_run_id": "dr-e",
            "requested_action": None,
            "unresolved_risks": [
                {"name": "real_apply_not_authorized", "severity": "medium"},
                {"name": "extra_unexpected_risk", "severity": "high"},
            ],
            "blocking_reasons": [],
            "apply_allowed": False,
            "execution_allowed": False,
            "tool_execution_allowed": False,
            "dry_run_execution_allowed": False,
            "simulation_execution_allowed": False,
            "rollback_allowed": False,
            "verdict_apply_allowed": False,
            "metadata": {},
            "warnings": [],
        }
        rec = {
            "verification_verdict_id": "vv-extra",
            "status": "pending",
            "verification_verdict": verif,
            "verdict_decision": "pass",
            "apply_authorized": False,
        }
        agr = _build(rec)
        chk = next(c for c in agr["eligibility_checks"] if c["name"] == "unresolved_risks_only_real_apply")
        assert chk["passed"] is False

    def test_blocking_reasons_empty_fails_when_present(self, _build):
        verif = {
            "decision": "pass",
            "simulation_result_id": "sim-blk",
            "simulation_plan_id": "plan-blk",
            "dry_run_id": "dr-blk",
            "requested_action": None,
            "unresolved_risks": [],
            "blocking_reasons": ["some_blocking_reason"],
            "apply_allowed": False,
            "execution_allowed": False,
            "tool_execution_allowed": False,
            "dry_run_execution_allowed": False,
            "simulation_execution_allowed": False,
            "rollback_allowed": False,
            "verdict_apply_allowed": False,
            "metadata": {},
            "warnings": [],
        }
        rec = {
            "verification_verdict_id": "vv-blk",
            "status": "pending",
            "verification_verdict": verif,
            "verdict_decision": "pass",
            "apply_authorized": False,
        }
        agr = _build(rec)
        chk = next(c for c in agr["eligibility_checks"] if c["name"] == "blocking_reasons_empty")
        assert chk["passed"] is False


# ======================== TESTS 23-24: CONFIRMATIONS AND NEXT STEP ======================== #

class TestConfirmationsAndNextStep:
    def test_required_human_confirmations_included(self, _build, clean_pass_record):
        agr = _build(clean_pass_record)
        confs = agr["required_human_confirmations"]
        assert len(confs) >= 5
        assert any("requested action is still desired" in c.lower() for c in confs)
        assert any("target is correct" in c.lower() for c in confs)

    def test_recommended_next_step_for_eligible(self, _build, clean_pass_record):
        agr = _build(clean_pass_record)
        step = agr["recommended_next_step"]
        assert "human reviewer" in step.lower() or "human" in step.lower()
        assert "do not apply" in step.lower() or "not apply" in step.lower()


# ======================== TESTS 25-27: METADATA, WARNINGS, CONTENT ======================== #

class TestMetadataWarningsContent:
    def test_metadata_source_and_schema_version(self, _build, clean_pass_record):
        agr = _build(clean_pass_record)
        meta = agr["metadata"]
        assert meta["source"] == "apply_gate_request_builder"
        assert meta["schema_version"] == "1.0"

    def test_context_session_id_copied(self, _build, clean_pass_record):
        agr = _build(clean_pass_record, context={"session_id": "manual-65a-sid"})
        assert agr["metadata"]["session_id"] == "manual-65a-sid"

    def test_warnings_include_no_apply_authorization(self, _build, clean_pass_record):
        agr = _build(clean_pass_record)
        warns_text = " ".join(agr["warnings"])
        assert "does not authorize apply" in warns_text

    def test_verification_verdict_warnings_copied_with_prefix(self, _build, clean_pass_record):
        clean_pass_record["verification_verdict"]["warnings"] = ["custom verdict warning"]
        agr = _build(clean_pass_record)
        assert any("verification_verdict_warning: custom verdict warning" in w for w in agr["warnings"])

    def test_requested_action_copied(self, _build, clean_pass_record):
        agr = _build(clean_pass_record)
        ra = agr["requested_action"]
        assert ra is not None
        assert ra["tool_id"] == "test.tool"

    def test_sim_result_plan_dry_run_ids_copied(self, _build, clean_pass_record):
        agr = _build(clean_pass_record)
        assert agr["simulation_result_id"] == "sim-001"
        assert agr["simulation_plan_id"] == "plan-1"
        assert agr["dry_run_id"] == "dr-1"


# ======================== TEST 29: VERDICT_PERSISTED FALSE CHECK ======================== #

class TestEdgeCases:
    def test_verdict_persisted_false_returns_not_eligible(self, _build):
        verif = {
            "decision": "pass",
            "simulation_result_id": "sim-pers2",
            "simulation_plan_id": "plan-p2",
            "dry_run_id": "dr-p2",
            "requested_action": None,
            "unresolved_risks": [{"name": "real_apply_not_authorized", "severity": "medium"}],
            "blocking_reasons": [],
            "apply_allowed": False,
            "execution_allowed": False,
            "tool_execution_allowed": False,
            "dry_run_execution_allowed": False,
            "simulation_execution_allowed": False,
            "rollback_allowed": False,
            "verdict_apply_allowed": False,
            "metadata": {},
            "warnings": [],
        }
        rec = {
            "verification_verdict_id": "vv-pers2",
            "status": "pending",
            "verification_verdict": verif,
            "verdict_decision": "pass",
            "apply_authorized": False,
            "verdict_persisted": False,
            "apply_allowed": False,
            "verdict_apply_allowed": False,
            "execution_allowed": False,
            "tool_execution_allowed": False,
            "dry_run_execution_allowed": False,
            "simulation_execution_allowed": False,
        }
        agr = _build(rec)
        assert agr["decision"] == "not_eligible"
