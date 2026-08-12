from aether.action.services.restricted_file_read_bridge import dispatch_restricted_read
from aether.core.governance import RestrictedReadScope, _ScopeDispatchState
from aether.action.restricted_file_reader import read_restricted_file
from pathlib import Path


def _scope(target=None): return RestrictedReadScope("file.restricted_read",read_restricted_file,target or str(Path(__file__).resolve()),Path(__file__).resolve().parent,"read_only",1,"a",None,None,_ScopeDispatchState())
def test_missing_scope(): assert dispatch_restricted_read(None,execution_attempt_id="a")["status"]=="error"
def test_wrong_attempt(): assert dispatch_restricted_read(_scope(),execution_attempt_id="b")["status"]=="error"
def test_wrong_capability():
    s=_scope(); object.__setattr__(s,"capability_id","x"); assert dispatch_restricted_read(s,execution_attempt_id="a")["status"]=="error"
def test_wrong_permission():
    s=_scope(); object.__setattr__(s,"permission_class","write"); assert dispatch_restricted_read(s,execution_attempt_id="a")["status"]=="error"
def test_wrong_target_root(): assert dispatch_restricted_read(_scope("/tmp/x"),execution_attempt_id="a")["status"]=="error"
def test_wrong_bound_function():
    s=_scope(); object.__setattr__(s,"bound_function",lambda *a,**k:{}); assert dispatch_restricted_read(s,execution_attempt_id="a")["status"]=="error"
def test_invalid_max():
    s=_scope(); object.__setattr__(s,"max_chars",12001); assert dispatch_restricted_read(s,execution_attempt_id="a")["status"]=="error"
def test_dispatch_state_consumed():
    s=_scope(); s._dispatch_state.consumed=True; assert dispatch_restricted_read(s,execution_attempt_id="a")["status"]=="error"
def test_scope_target_is_bound(): assert _scope().normalized_target
def test_scope_root_is_bound(): assert _scope().approved_root
def test_scope_attempt_is_bound(): assert _scope().execution_attempt_id=="a"
def test_scope_reader_is_direct_reader(): assert _scope().bound_function is read_restricted_file
def test_scope_dispatch_state_exists(): assert _scope()._dispatch_state
def test_scope_parameter_is_bounded(): assert _scope().max_chars==1
def test_scope_capability_exact(): assert _scope().capability_id=="file.restricted_read"
def test_scope_permission_exact(): assert _scope().permission_class=="read_only"
def test_no_generic_executor_source():
    import inspect; assert "execute_tool" not in inspect.getsource(dispatch_restricted_read)
def test_no_observation_intake_source():
    import inspect; assert "handle_observation_intake" not in inspect.getsource(dispatch_restricted_read)
