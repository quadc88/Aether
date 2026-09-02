from pathlib import Path
import json
import base64
import hashlib

import pytest

from aether.deployment.dependency_lock import DependencyLockError, verify_dependency_closure, verify_installed_closure


def test_offline_dependency_closure_is_complete_and_hash_bound():
    root = Path(__file__).parents[1]
    result = verify_dependency_closure(root / "deployment/requirements.lock.json", root / "deployment/wheelhouse")
    assert result["closure_status"] == "COMPLETE"
    assert result["artifact_count"] == 16


def test_dependency_lock_rejects_noncanonical_policy_change(tmp_path: Path):
    root = Path(__file__).parents[1]
    lock = tmp_path / "requirements.lock.json"
    value = json.loads((root / "deployment/requirements.lock.json").read_text())
    value["blockers"] = ["unexpected"]
    lock.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(DependencyLockError):
        verify_dependency_closure(lock, root / "deployment/wheelhouse")


def test_dependency_lock_rejects_wheel_byte_tampering(tmp_path: Path):
    root = Path(__file__).parents[1]
    lock = tmp_path / "requirements.lock.json"
    lock.write_bytes((root / "deployment/requirements.lock.json").read_bytes())
    wheelhouse = tmp_path / "wheelhouse"
    wheelhouse.mkdir()
    for source in (root / "deployment/wheelhouse").glob("*.whl"):
        target = wheelhouse / source.name
        target.write_bytes(source.read_bytes())
    target = wheelhouse / "click-8.4.2-py3-none-any.whl"
    data = bytearray(target.read_bytes())
    data[-1] ^= 1
    target.write_bytes(data)
    with pytest.raises(DependencyLockError):
        verify_dependency_closure(lock, wheelhouse)


def test_installed_dependency_closure_is_record_exact(tmp_path: Path):
    import_root = tmp_path / "site-packages"
    dist = import_root / "demo-1.0.dist-info"
    dist.mkdir(parents=True)
    metadata = b"Name: demo\nVersion: 1.0\n"
    module = b"value = 1\n"
    (import_root / "demo.py").write_bytes(module)
    (dist / "METADATA").write_bytes(metadata)
    rows = []
    for relative, data in (("demo.py", module), ("demo-1.0.dist-info/METADATA", metadata)):
        digest = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).decode().rstrip("=")
        rows.append(f"{relative},sha256={digest},{len(data)}")
    rows.append("demo-1.0.dist-info/RECORD,,")
    (dist / "RECORD").write_text("\n".join(rows) + "\n", encoding="utf-8")
    lock = tmp_path / "lock.json"
    lock.write_text(json.dumps({"closure_status": "COMPLETE", "artifacts": [{"name": "demo", "version": "1.0"}]}), encoding="utf-8")
    assert verify_installed_closure(lock, import_root)["project_count"] == 1
    (import_root / "extra.py").write_bytes(b"extra")
    with pytest.raises(DependencyLockError):
        verify_installed_closure(lock, import_root)
