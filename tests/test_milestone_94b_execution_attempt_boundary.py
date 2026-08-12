from pathlib import Path


def _source():
    return Path(__file__).parents[1]


def test_route_source_exists(): assert "execute-approved-read" in (_source() / "aether/interface/routers/file_routes.py").read_text()
def test_api_server_not_changed_for_route(): assert "execute-approved-read" not in (_source() / "aether/interface/api_server.py").read_text()
def test_coordinator_exists(): assert (_source() / "aether/core/coordination.py").exists()
def test_bridge_exists(): assert (_source() / "aether/action/services/restricted_file_read_bridge.py").exists()
def test_observation_is_private_module(): assert "dataclass" in (_source() / "aether/action/restricted_file_read_observation.py").read_text()
def test_verifier_exists(): assert "VERIFIED_SUCCESS" in (_source() / "aether/verification/restricted_file_read.py").read_text()
def test_generic_executor_not_in_coordinator(): assert "execute_tool" not in (_source() / "aether/core/coordination.py").read_text()
def test_observation_intake_not_in_coordinator(): assert "handle_observation_intake" not in (_source() / "aether/core/coordination.py").read_text()
def test_scope_not_serialized(): assert "json" not in (_source() / "aether/core/governance.py").read_text()
def test_endpoint_is_post(): assert '@file_router.post(' in (_source() / "aether/interface/routers/file_routes.py").read_text()
def test_phase_one_parser_is_anchored(): assert "fullmatch" in (_source() / "aether/action/tool_planner.py").read_text()
def test_phase_one_default_is_bounded(): assert "12000" in (_source() / "aether/action/tool_planner.py").read_text()
def test_claim_is_explicit(): assert "claim_approval_for_execution" in (_source() / "aether/action/approval_queue.py").read_text()
def test_approval_is_not_generic_execution(): assert "execute_tool" not in (_source() / "aether/core/coordination.py").read_text()
def test_bridge_calls_reader(): assert "mode=\"governed_chat\"" in (_source() / "aether/action/services/restricted_file_read_bridge.py").read_text()
def test_progress_is_authorized_path(): assert (_source() / "PROGRESS.md").exists()
def test_no_loop_trace_edit_requirement(): assert (_source() / "aether/core/loop_trace.py").exists()
def test_no_runtime_edit_requirement(): assert (_source() / "aether/core/runtime.py").exists()
def test_scope_has_dispatch_state(): assert "_dispatch_state" in (_source() / "aether/core/governance.py").read_text()
def test_route_response_model_is_present(): assert "RestrictedFileReadExecutionAttemptResponse" in (_source() / "aether/interface/routers/file_routes.py").read_text()
