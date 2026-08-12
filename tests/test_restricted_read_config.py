from pathlib import Path
from aether.core import config


def _set(value):
    config._CONFIG={"security":{"restricted_file_read":{"approved_roots":value}}}
    config._CONFIG_PATH=(config.get_project_root()/"config/aether.yaml").resolve()
def test_empty(): _set([]); assert config.get_restricted_file_read_approved_roots()==()
def test_none(): _set(None); assert config.get_restricted_file_read_approved_roots()==()
def test_non_list(): _set("x"); assert config.get_restricted_file_read_approved_roots()==()
def test_non_string(): _set([1]); assert config.get_restricted_file_read_approved_roots()==()
def test_empty_string(): _set([""]); assert config.get_restricted_file_read_approved_roots()==()
def test_relative(monkeypatch,tmp_path): monkeypatch.setattr(config,"get_project_root",lambda:tmp_path); _set(["src"]); assert config.get_restricted_file_read_approved_roots()==((tmp_path/"src").resolve(),)
def test_absolute(tmp_path): _set([str(tmp_path)]); assert config.get_restricted_file_read_approved_roots()==(tmp_path.resolve(),)
def test_mixed_invalid(tmp_path): _set([str(tmp_path),1]); assert config.get_restricted_file_read_approved_roots()==()
def test_env_dollar(): _set(["$ROOT"]); assert config.get_restricted_file_read_approved_roots()==()
def test_env_percent(): _set(["%ROOT%"]); assert config.get_restricted_file_read_approved_roots()==()
def test_windows_drive(): _set(["C:/Aether"]); assert config.get_restricted_file_read_approved_roots()==()
def test_windows_unc(): _set([r"\\server\share"]); assert config.get_restricted_file_read_approved_roots()==()
def test_security_scalar(): config._CONFIG={"security":"x"}; assert config.get_restricted_file_read_approved_roots()==()
def test_subsection_scalar(): config._CONFIG={"security":{"restricted_file_read":"x"}}; assert config.get_restricted_file_read_approved_roots()==()
def test_resolved_root(): _set(["."]); assert config.get_restricted_file_read_approved_roots()[0].is_absolute()
def test_multiple_roots(tmp_path): _set([str(tmp_path),str(tmp_path/"x")]); assert len(config.get_restricted_file_read_approved_roots())==2
def test_no_cwd_authority(monkeypatch,tmp_path): monkeypatch.chdir(tmp_path); _set([]); assert config.get_restricted_file_read_approved_roots()==()
def test_production_yaml_empty():
    config.clear_cache(); assert config.get_restricted_file_read_approved_roots()==()
