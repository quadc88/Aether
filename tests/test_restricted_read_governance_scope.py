from pathlib import Path
from aether.core.governance import authorize_restricted_read_execution, RestrictedReadScope


def _action(): return {"tool_id":"file.restricted_read","action_type":"restricted_file_read","name":"Restricted File Read","target":str(Path(__file__).resolve()),"permission_class":"read_only","parameters":{"max_chars":1}}
def _kwargs(**changes):
    v={"thinking_policy":{"decision_type":"require_approval"},"requested_action":_action(),"risk_evidence":{"risk_level":"medium"},"identity_integrity_evidence":{"status":"verified"},"rule_3_4_precedence":"clear","rule4_risk_terms_detected":[],"approval_evidence":{"approval_valid":True},"execution_attempt_id":"a"}; v.update(changes); return v
def test_decision_type(): assert authorize_restricted_read_execution(**_kwargs()).generic_envelope["decision"] == "require_approval"
def test_scope_requires_root(): assert authorize_restricted_read_execution(**_kwargs()).authorization_granted is False
def test_empty_precedence_denies(): assert not authorize_restricted_read_execution(**_kwargs(rule_3_4_precedence=None)).authorization_granted
def test_rule3_denies(): assert not authorize_restricted_read_execution(**_kwargs(rule_3_4_precedence="rule_3")).authorization_granted
def test_block_denies(): assert not authorize_restricted_read_execution(**_kwargs(thinking_policy={"decision_type":"block"})).authorization_granted
def test_high_risk_denies(): assert not authorize_restricted_read_execution(**_kwargs(risk_evidence={"risk_level":"high"})).authorization_granted
def test_low_risk_denies(): assert not authorize_restricted_read_execution(**_kwargs(risk_evidence={"risk_level":"low"})).authorization_granted
def test_sensitive_denies(): assert not authorize_restricted_read_execution(**_kwargs(rule4_risk_terms_detected=["secret"])).authorization_granted
def test_missing_approval_denies(): assert not authorize_restricted_read_execution(**_kwargs(approval_evidence=None)).authorization_granted
def test_invalid_approval_denies(): assert not authorize_restricted_read_execution(**_kwargs(approval_evidence={"approval_valid":False})).authorization_granted
def test_missing_identity_denies(): assert not authorize_restricted_read_execution(**_kwargs(identity_integrity_evidence={"status":"missing"})).authorization_granted
def test_changed_identity_denies(): assert not authorize_restricted_read_execution(**_kwargs(identity_integrity_evidence={"status":"changed"})).authorization_granted
def test_wrong_tool_denies(): assert not authorize_restricted_read_execution(**_kwargs(requested_action={"tool_id":"x"})).authorization_granted
def test_wrong_permission_denies():
    a=_action(); a["permission_class"]="write"; assert not authorize_restricted_read_execution(**_kwargs(requested_action=a)).authorization_granted
def test_wrong_parameters_denies():
    a=_action(); a["parameters"]={"max_chars":12001}; assert not authorize_restricted_read_execution(**_kwargs(requested_action=a)).authorization_granted
def test_wrong_target_denies():
    a=_action(); a["target"]="/outside"; assert not authorize_restricted_read_execution(**_kwargs(requested_action=a)).authorization_granted
def test_generic_flags_preserved(): assert authorize_restricted_read_execution(**_kwargs()).generic_envelope["tool_execution_allowed"] is False
def test_scope_is_private_type(): assert RestrictedReadScope.__module__ == "aether.core.governance"
def test_scope_not_in_generic(): assert "scope" not in authorize_restricted_read_execution(**_kwargs()).generic_envelope
def test_safe_reason_bounded(): assert "secret" not in authorize_restricted_read_execution(**_kwargs()).safe_reason
def test_warnings_tuple(): assert isinstance(authorize_restricted_read_execution(**_kwargs()).warnings, tuple)
def test_state_invalid_action(): assert authorize_restricted_read_execution(**_kwargs(requested_action=None)).approval_requirement_state == "invalid_or_stale"
def test_state_missing_approval(): assert authorize_restricted_read_execution(**_kwargs(approval_evidence=None)).approval_requirement_state == "required_unsatisfied"
def test_state_invalid_approval(): assert authorize_restricted_read_execution(**_kwargs(approval_evidence={"approval_valid":False})).approval_requirement_state == "invalid_or_stale"
def test_scope_none_on_denial(): assert authorize_restricted_read_execution(**_kwargs()).scope is None
