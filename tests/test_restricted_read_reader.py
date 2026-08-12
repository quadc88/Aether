from pathlib import Path
from aether.action.restricted_file_reader import read_restricted_file, is_sensitive_path
from aether.core import config


def _root(tmp_path): config._CONFIG={"security":{"restricted_file_read":{"approved_roots":[str(tmp_path)]}}}
def _file(tmp_path,name="x.py",text="safe"): p=tmp_path/name; p.write_text(text); return p
def test_direct_signature_compatibility(tmp_path): assert "content" in read_restricted_file(str(_file(tmp_path)))
def test_governed_success(tmp_path): _root(tmp_path); assert read_restricted_file(str(_file(tmp_path)),mode="governed_chat")["status"]=="success"
def test_governed_content(tmp_path): _root(tmp_path); assert read_restricted_file(str(_file(tmp_path)),mode="governed_chat")["content"]=="safe"
def test_governed_truncated(tmp_path): _root(tmp_path); assert read_restricted_file(str(_file(tmp_path,text="safe text")),2,mode="governed_chat")["truncated"]
def test_governed_not_found(tmp_path): _root(tmp_path); assert read_restricted_file(str(tmp_path/"x.py"),mode="governed_chat")["status"]=="not_found"
def test_governed_empty_roots(tmp_path): config._CONFIG={}; assert read_restricted_file(str(_file(tmp_path)),mode="governed_chat")["status"]=="blocked"
def test_governed_outside(tmp_path): _root(tmp_path); assert read_restricted_file("/etc/hosts",mode="governed_chat")["status"]=="blocked"
def test_governed_sensitive(tmp_path): _root(tmp_path); assert is_sensitive_path(Path(tmp_path)/"secret.py")
def test_governed_extension(tmp_path): _root(tmp_path); assert read_restricted_file(str(_file(tmp_path,"x.bin")),mode="governed_chat")["status"]=="blocked"
def test_governed_bound_zero(tmp_path): _root(tmp_path); assert read_restricted_file(str(_file(tmp_path)),0,mode="governed_chat")["content"]==""
def test_governed_bound_high(tmp_path): _root(tmp_path); assert read_restricted_file(str(_file(tmp_path)),12000,mode="governed_chat")["status"]=="success"
def test_governed_bound_invalid(tmp_path): _root(tmp_path); assert read_restricted_file(str(_file(tmp_path)),12001,mode="governed_chat")["status"]=="blocked"
def test_governed_regular_file(tmp_path): _root(tmp_path); assert read_restricted_file(str(_file(tmp_path)),mode="governed_chat")["regular_file"]
def test_governed_audit_excludes_content(tmp_path):
    _root(tmp_path); result=read_restricted_file(str(_file(tmp_path)),mode="governed_chat"); assert result["content"]=="safe"
def test_governed_utf8(tmp_path): _root(tmp_path); assert read_restricted_file(str(_file(tmp_path,text="hé")),mode="governed_chat")["content"]=="hé"
def test_governed_symlink_escape(tmp_path):
    _root(tmp_path); outside=tmp_path.parent/"outside.py"; outside.write_text("x"); link=tmp_path/"link.py"; link.symlink_to(outside); assert read_restricted_file(str(link),mode="governed_chat")["status"]=="blocked"
def test_governed_private_key(tmp_path): _root(tmp_path); assert read_restricted_file(str(_file(tmp_path,text="-----BEGIN PRIVATE KEY-----")),mode="governed_chat")["status"]=="blocked"
def test_governed_metadata(tmp_path): _root(tmp_path); assert read_restricted_file(str(_file(tmp_path)),metadata={"x":1},mode="governed_chat")["status"]=="success"
def test_direct_mode_remains_available(tmp_path): assert "content" in read_restricted_file(str(_file(tmp_path)))
def test_governed_changed_flag_default(tmp_path): _root(tmp_path); assert read_restricted_file(str(_file(tmp_path)),mode="governed_chat")["changed_during_read"] is False
def test_governed_privacy_flag(tmp_path): _root(tmp_path); assert read_restricted_file(str(_file(tmp_path)),mode="governed_chat")["privacy_filtered"]
def test_governed_size(tmp_path): _root(tmp_path); assert read_restricted_file(str(_file(tmp_path,text="é")),mode="governed_chat")["size_bytes"] is not None
def test_governed_id(tmp_path): _root(tmp_path); assert read_restricted_file(str(_file(tmp_path)),mode="governed_chat")["id"].startswith("file_access_")
def test_governed_path(tmp_path): _root(tmp_path); assert read_restricted_file(str(_file(tmp_path)),mode="governed_chat")["normalized_path"]
