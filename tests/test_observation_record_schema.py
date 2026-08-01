"""
Milestone 83B — Observation Record Schema Foundation Tests.

These tests validate the Pydantic model contracts added to aether/interface/api_models.py
in the 83B Build.  They do NOT test runtime behavior, endpoint logic, or persistence.

83B intentionally adds schema models only.
Store/service/router/endpoints are deferred to 83C/83D.
api_server.py remains free of observation feature logic at all times.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from aether.interface.api_models import (
    ObservationRecordCancelRequest,
    ObservationRecordCreateRequest,
    ObservationRecordListResponse,
    ObservationRecordResponse,
    ObservationRecordUpdateStatusRequest,
)


# ---------------------------------------------------------------------------
# 1. Import tests
# ---------------------------------------------------------------------------

class TestImportValidation:
    """All five schema models must be importable from aether.interface.api_models."""

    def test_create_request_importable(self):
        assert ObservationRecordCreateRequest is not None

    def test_response_importable(self):
        assert ObservationRecordResponse is not None

    def test_list_response_importable(self):
        assert ObservationRecordListResponse is not None

    def test_update_status_request_importable(self):
        assert ObservationRecordUpdateStatusRequest is not None

    def test_cancel_request_importable(self):
        assert ObservationRecordCancelRequest is not None


# ---------------------------------------------------------------------------
# 2. Create request structure
# ---------------------------------------------------------------------------

class TestObservationRecordCreateRequest:
    """Validate the create request schema structure."""

    def test_accepts_all_fields(self):
        rec = ObservationRecordCreateRequest(
            plan_step_id="ps_001",
            evidence_item_id="ev_001",
            target="/tmp/output.txt",
            observed_value="line count = 42",
            expected_value="line count = 42",
            status="matched",
            collector_contract_id="cc_001",
            metadata={"source": "manual"},
        )
        assert rec.plan_step_id == "ps_001"
        assert rec.evidence_item_id == "ev_001"
        assert rec.target == "/tmp/output.txt"
        assert rec.observed_value == "line count = 42"
        assert rec.expected_value == "line count = 42"
        assert rec.status == "matched"
        assert rec.collector_contract_id == "cc_001"
        assert rec.metadata == {"source": "manual"}

    def test_defaults(self):
        rec = ObservationRecordCreateRequest(target="/tmp/x")
        assert rec.plan_step_id is None
        assert rec.evidence_item_id is None
        assert rec.observed_value is None
        assert rec.expected_value is None
        assert rec.status == "pending"
        assert rec.collector_contract_id is None
        assert rec.metadata is None

    def test_no_generated_fields_in_create(self):
        """observation_id, observation_type, observed_at, safety_flags must NOT be
        present as fields on the create request model."""
        fields = ObservationRecordCreateRequest.model_fields
        assert "observation_id" not in fields
        assert "observation_type" not in fields
        assert "observed_at" not in fields
        assert "safety_flags" not in fields


# ---------------------------------------------------------------------------
# 3. Response structure
# ---------------------------------------------------------------------------

class TestObservationRecordResponse:
    """Validate the response schema matches the builder output shape."""

    def test_contains_all_builder_fields(self):
        rec = ObservationRecordResponse(
            observation_id="abc123",
            observation_type="observation_record",
            plan_step_id="ps_001",
            evidence_item_id="ev_001",
            collector_contract_id="cc_001",
            target="/tmp/output.txt",
            observed_value="line count = 42",
            expected_value="line count = 42",
            status="matched",
            observed_at="2026-07-31T12:00:00+00:00",
            metadata={"source": "manual"},
            safety_flags={
                "tool_execution_allowed": False,
                "tool_executed": False,
                "evidence_collection_performed": False,
                "system_state_modified": False,
                "apply_performed": False,
                "rollback_performed": False,
                "persistent_write_performed": False,
                "external_side_effect_performed": False,
            },
        )
        assert rec.observation_id == "abc123"
        assert rec.observation_type == "observation_record"
        assert rec.plan_step_id == "ps_001"
        assert rec.evidence_item_id == "ev_001"
        assert rec.collector_contract_id == "cc_001"
        assert rec.target == "/tmp/output.txt"
        assert rec.observed_value == "line count = 42"
        assert rec.expected_value == "line count = 42"
        assert rec.status == "matched"
        assert rec.observed_at == "2026-07-31T12:00:00+00:00"
        assert rec.metadata == {"source": "manual"}
        assert rec.safety_flags["tool_execution_allowed"] is False

    def test_default_observation_type(self):
        rec = ObservationRecordResponse(
            observation_id="x",
            target="/tmp/x",
            status="pending",
            observed_at="2026-07-31T00:00:00+00:00",
        )
        assert rec.observation_type == "observation_record"

    def test_default_empty_collections(self):
        rec = ObservationRecordResponse(
            observation_id="x",
            target="/tmp/x",
            status="pending",
            observed_at="2026-07-31T00:00:00+00:00",
        )
        assert rec.metadata == {}
        assert rec.safety_flags == {}


# ---------------------------------------------------------------------------
# 4. List response structure
# ---------------------------------------------------------------------------

class TestObservationRecordListResponse:
    """Validate the list response schema."""

    def test_default_values(self):
        rec = ObservationRecordListResponse()
        assert rec.records == []
        assert rec.total == 0
        assert rec.limit == 50
        assert rec.offset == 0

    def test_contains_records_field(self):
        """records must be a list field."""
        fields = ObservationRecordListResponse.model_fields
        assert "records" in fields


# ---------------------------------------------------------------------------
# 5. Update status request structure
# ---------------------------------------------------------------------------

class TestObservationRecordUpdateStatusRequest:
    """Validate the update-status request schema."""

    def test_accepts_all_fields(self):
        req = ObservationRecordUpdateStatusRequest(
            new_status="matched",
            reviewer="human_001",
            reason="verified by manual check",
        )
        assert req.new_status == "matched"
        assert req.reviewer == "human_001"
        assert req.reason == "verified by manual check"

    def test_optional_reason(self):
        req = ObservationRecordUpdateStatusRequest(
            new_status="error",
            reviewer="system",
        )
        assert req.reason is None

    def test_no_generated_fields(self):
        """observation_id, observed_at, safety_flags must NOT be in this request."""
        fields = ObservationRecordUpdateStatusRequest.model_fields
        assert "observation_id" not in fields
        assert "observed_at" not in fields
        assert "safety_flags" not in fields


# ---------------------------------------------------------------------------
# 6. Cancel request structure
# ---------------------------------------------------------------------------

class TestObservationRecordCancelRequest:
    """Validate the cancel request schema."""

    def test_accepts_all_fields(self):
        req = ObservationRecordCancelRequest(
            reviewer="human_001",
            reason="incorrect observation",
        )
        assert req.reviewer == "human_001"
        assert req.reason == "incorrect observation"

    def test_optional_reason(self):
        req = ObservationRecordCancelRequest(reviewer="system")
        assert req.reason is None

    def test_no_generated_fields(self):
        """observation_id, observed_at, safety_flags must NOT be in this request."""
        fields = ObservationRecordCancelRequest.model_fields
        assert "observation_id" not in fields
        assert "observed_at" not in fields
        assert "safety_flags" not in fields


# ---------------------------------------------------------------------------
# 7. Structural-only rule
# ---------------------------------------------------------------------------

class TestStructuralOnly:
    """Ensure api_models.py does not introduce complex validation."""

    def test_no_field_import(self):
        path = Path("aether/interface/api_models.py")
        source = path.read_text(encoding="utf-8")
        assert "Field(" not in source, "api_models.py must not use Field()"

    def test_no_validator_decorators(self):
        path = Path("aether/interface/api_models.py")
        source = path.read_text(encoding="utf-8")
        assert "@validator" not in source, "api_models.py must not use @validator"
        assert "@root_validator" not in source, "api_models.py must not use @root_validator"

    def test_no_literal_import(self):
        path = Path("aether/interface/api_models.py")
        source = path.read_text(encoding="utf-8")
        assert "Literal[" not in source, "api_models.py must not use Literal"

    def test_no_enum_import(self):
        path = Path("aether/interface/api_models.py")
        source = path.read_text(encoding="utf-8")
        assert "Enum" not in source, "api_models.py must not import Enum"

    def test_no_action_builder_import(self):
        path = Path("aether/interface/api_models.py")
        source = path.read_text(encoding="utf-8")
        assert "aether.action.observation_record" not in source, (
            "api_models.py must not import from aether.action.observation_record"
        )

    def test_all_observation_models_are_basemodel_subclasses(self):
        path = Path("aether/interface/api_models.py")
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if node.name.startswith("ObservationRecord"):
                    bases = [ast.unparse(b) for b in node.bases]
                    assert "BaseModel" in bases, (
                        f"{node.name} must subclass BaseModel"
                    )


# ---------------------------------------------------------------------------
# 8. JSON-friendly sample serialization
# ---------------------------------------------------------------------------

class TestJsonSerialization:
    """Models with JSON-friendly values must round-trip through json.dumps."""

    def test_create_request_serializable(self):
        rec = ObservationRecordCreateRequest(
            plan_step_id="ps_001",
            target="/tmp/x",
            observed_value=42,
            expected_value=42,
            status="matched",
            metadata={"tags": ["a", "b"]},
        )
        data = rec.model_dump()
        dumped = json.dumps(data)
        loaded = json.loads(dumped)
        assert loaded["target"] == "/tmp/x"

    def test_response_serializable(self):
        rec = ObservationRecordResponse(
            observation_id="abc",
            target="/tmp/x",
            status="pending",
            observed_at="2026-07-31T00:00:00+00:00",
        )
        data = rec.model_dump()
        dumped = json.dumps(data)
        loaded = json.loads(dumped)
        assert loaded["observation_id"] == "abc"

    def test_list_response_serializable(self):
        rec = ObservationRecordListResponse()
        data = rec.model_dump()
        dumped = json.dumps(data)
        loaded = json.loads(dumped)
        assert loaded["total"] == 0


# ---------------------------------------------------------------------------
# 9. No-invocation self-check
# ---------------------------------------------------------------------------

class TestNoInvocationSelfCheck:
    """Parse this file and assert it does not violate boundary rules."""

    @pytest.fixture(scope="class")
    def this_tree(self):
        return ast.parse(Path(__file__).read_text(encoding="utf-8"))

    def test_no_testclient_import(self, this_tree):
        for node in ast.walk(this_tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "TestClient":
                        pytest.fail("Schema tests must not import TestClient")

    def test_no_build_observation_record_call(self, this_tree):
        for node in ast.walk(this_tree):
            if isinstance(node, ast.Call):
                func = ast.unparse(node.func)
                if "build_observation_record" in func:
                    pytest.fail("Schema tests must not call build_observation_record")

    def test_no_endpoint_calls(self, this_tree):
        forbidden = [
            "root(",
            "get_identity_integrity_status(",
            "post_initialize_identity_guard(",
            "post_verify_identity_integrity(",
            "identity(",
            "awaken(",
            "classify_verification_risk(",
        ]
        for node in ast.walk(this_tree):
            if isinstance(node, ast.Call):
                func = ast.unparse(node.func)
                for f in forbidden:
                    if func == f or func.endswith(f):
                        pytest.fail(f"Schema tests must not call {f}")

    def test_no_runtime_service_calls(self, this_tree):
        forbidden = [
            "runtime.process_chat",
            "runtime.status",
            "classify_risk(",
            "handle_awaken(",
        ]
        for node in ast.walk(this_tree):
            if isinstance(node, ast.Call):
                func = ast.unparse(node.func)
                for term in forbidden:
                    if term in func:
                        pytest.fail(f"Schema tests must not call {term}")

    def test_no_file_writes(self, this_tree):
        for node in ast.walk(this_tree):
            if isinstance(node, ast.Call):
                func = ast.unparse(node.func)
                if func.endswith(".write_text") or func.endswith(".write_bytes") or func == "open":
                    pytest.fail(f"Schema tests must not write files; found: {func}")
