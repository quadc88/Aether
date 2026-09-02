from pathlib import Path
from dataclasses import replace
import hashlib
import os
import threading

import pytest

from aether.oas.host_entrypoint import (
    EntrypointAdapters,
    EntrypointError,
    RuntimeIdentitySnapshot,
    STANDARD_IMPORT_ROOTS,
    collect_runtime_identity_snapshot,
    _validate_runtime_identity,
    run_entrypoint,
    validate_environment,
)


def test_entrypoint_accepts_only_the_fixed_protocol_snapshot():
    environment = {
        "LISTEN_PID": "7", "LISTEN_FDS": "3",
        "LISTEN_FDNAMES": "runtime:bootstrap:broker", "NOTIFY_SOCKET": "@oas",
        "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "TZ": "UTC", "HOME": "/var/empty",
        "PATH": "/poisoned",
    }
    assert "PATH" not in validate_environment(environment, pid=7)
    with pytest.raises(EntrypointError):
        validate_environment({**environment, "LISTEN_FDS": "4"}, pid=7)


def test_ready_is_emitted_only_after_the_verified_start_transaction(monkeypatch):
    events = []
    record = {"state": "ACTIVATING"}

    def activation(*_args, **_kwargs):
        events.append("activation")
        return record

    class Descriptors:
        def close(self):
            events.append("descriptors-close")

    class Service:
        def start(self):
            events.append("service-start")

        def shutdown(self):
            events.append("service-stop")

    monkeypatch.setattr("aether.oas.host_entrypoint.validate_activation", activation)
    environment = {
        "LISTEN_PID": str(os.getpid()), "LISTEN_FDS": "3",
        "LISTEN_FDNAMES": "runtime:bootstrap:broker", "NOTIFY_SOCKET": "@oas",
        "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "TZ": "UTC", "HOME": "/var/empty",
    }
    adapters = EntrypointAdapters(
        descriptor_intake=lambda *_args, **_kwargs: (events.append("descriptors") or Descriptors()),
        service_factory=lambda *_args, **_kwargs: (events.append("service-created") or Service()),
    )
    shutdown = threading.Event()
    shutdown.set()
    run_entrypoint(
        "/tmp/aether-entrypoint-test",
        environment=environment,
        shutdown_event=shutdown,
        notifier=lambda **_kwargs: events.append("ready"),
        adapters=adapters,
    )
    assert events == ["activation", "descriptors", "service-created", "service-start", "ready", "service-stop"]


def test_fixed_verifier_is_not_candidate_importable():
    artifact = Path(__file__).parents[1] / "deployment/fixed_verifier/aether-release-verify"
    text = artifact.read_text(encoding="utf-8")
    assert "from aether" not in text
    assert "import aether" not in text
    assert artifact.stat().st_mode & 0o111


def test_runtime_identity_snapshot_binds_launcher_process_and_import_root(tmp_path: Path):
    root = tmp_path / "root"
    interpreter = root / "usr/bin/python3.11"
    launcher = root / "opt/aether/current/runtime/bin/python"
    import_root = root / "opt/aether/current/runtime/lib/python3.11/site-packages"
    interpreter.parent.mkdir(parents=True)
    interpreter.write_bytes(b"python")
    interpreter.chmod(0o755)
    launcher.parent.mkdir(parents=True)
    launcher.symlink_to("../../../../../usr/bin/python3.11")
    module = import_root / "aether/oas/host_entrypoint.py"
    module.parent.mkdir(parents=True)
    module.write_bytes(b"module")
    manifest = {"runtime": {
        "python": "/usr/bin/python3.11",
        "python_version": "3.11",
        "import_root": "/opt/aether/current/runtime/lib/python3.11/site-packages",
    }}
    snapshot = RuntimeIdentitySnapshot(
        proc_self_exe="/usr/bin/python3.11",
        sys_executable="/usr/bin/python3.11",
        python_version="3.11",
        abi_tag="cpython-311",
        soabi="cpython-311",
        machine="x86_64",
        module_path="/opt/aether/current/runtime/lib/python3.11/site-packages/aether/oas/host_entrypoint.py",
        module_sha256=hashlib.sha256(b"module").hexdigest(),
        sys_path=(manifest["runtime"]["import_root"], *STANDARD_IMPORT_ROOTS),
        uid=3003,
        gid=3003,
        groups=(),
        capabilities="0000000000000000",
        authorized_import_roots=(manifest["runtime"]["import_root"], *STANDARD_IMPORT_ROOTS),
    )
    _validate_runtime_identity(root, manifest, snapshot)
    with pytest.raises(EntrypointError):
        _validate_runtime_identity(root, manifest, replace(snapshot, proc_self_exe="/bad"))


@pytest.mark.parametrize("field,value", [
    ("uid", 0),
    ("gid", 0),
    ("groups", (3003,)),
    ("capabilities", "0000000000000001"),
    ("sys_path", ("", *STANDARD_IMPORT_ROOTS)),
    ("sys_path", ("relative/path", *STANDARD_IMPORT_ROOTS)),
    ("sys_path", ("/tmp/unauthorized", *STANDARD_IMPORT_ROOTS)),
    ("sys_path", ("/usr/lib/python3.11", *STANDARD_IMPORT_ROOTS)),
    ("authorized_import_roots", ("/tmp/unauthorized", *STANDARD_IMPORT_ROOTS)),
])
def test_runtime_identity_rejects_credential_and_import_root_drift(tmp_path: Path, field: str, value):
    root = tmp_path / "root"
    interpreter = root / "usr/bin/python3.11"
    launcher = root / "opt/aether/current/runtime/bin/python"
    import_root = root / "opt/aether/current/runtime/lib/python3.11/site-packages"
    interpreter.parent.mkdir(parents=True)
    interpreter.write_bytes(b"python")
    interpreter.chmod(0o755)
    launcher.parent.mkdir(parents=True)
    launcher.symlink_to("../../../../../usr/bin/python3.11")
    module = import_root / "aether/oas/host_entrypoint.py"
    module.parent.mkdir(parents=True)
    module.write_bytes(b"module")
    manifest = {"runtime": {
        "python": "/usr/bin/python3.11",
        "python_version": "3.11",
        "import_root": "/opt/aether/current/runtime/lib/python3.11/site-packages",
    }}
    snapshot = RuntimeIdentitySnapshot(
        proc_self_exe="/usr/bin/python3.11", sys_executable="/usr/bin/python3.11",
        python_version="3.11", abi_tag="cpython-311", soabi="cpython-311",
        machine="x86_64",
        module_path="/opt/aether/current/runtime/lib/python3.11/site-packages/aether/oas/host_entrypoint.py",
        module_sha256=hashlib.sha256(b"module").hexdigest(),
        sys_path=(manifest["runtime"]["import_root"], *STANDARD_IMPORT_ROOTS),
        uid=3003, gid=3003, groups=(), capabilities="0000000000000000",
        authorized_import_roots=(manifest["runtime"]["import_root"], *STANDARD_IMPORT_ROOTS),
    )
    with pytest.raises(EntrypointError):
        _validate_runtime_identity(root, manifest, replace(snapshot, **{field: value}))


def test_runtime_snapshot_preserves_empty_sys_path_entries(monkeypatch):
    import aether.oas.host_entrypoint as entrypoint

    monkeypatch.setattr(entrypoint.sys, "path", ["", "/usr/lib/python3.11"])
    snapshot = collect_runtime_identity_snapshot()
    assert snapshot.sys_path[:2] == ("", "/usr/lib/python3.11")


@pytest.mark.parametrize("key", [
    "LISTEN_PID", "LISTEN_FDS", "LISTEN_FDNAMES", "NOTIFY_SOCKET",
    "LANG", "LC_ALL", "TZ", "HOME",
])
def test_entrypoint_rejects_each_missing_protocol_or_fixed_environment_value(key: str):
    environment = {
        "LISTEN_PID": "7", "LISTEN_FDS": "3",
        "LISTEN_FDNAMES": "runtime:bootstrap:broker", "NOTIFY_SOCKET": "@oas",
        "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "TZ": "UTC", "HOME": "/var/empty",
    }
    environment.pop(key)
    with pytest.raises(EntrypointError):
        from aether.oas.host_entrypoint import validate_environment
        validate_environment(environment, pid=7)


def test_entrypoint_closes_descriptors_when_service_construction_fails(monkeypatch):
    events = []

    class Descriptors:
        def close(self):
            events.append("descriptors-close")

    def activation(*_args, **_kwargs):
        return {"state": "ACTIVATING"}

    environment = {
        "LISTEN_PID": str(os.getpid()), "LISTEN_FDS": "3",
        "LISTEN_FDNAMES": "runtime:bootstrap:broker", "NOTIFY_SOCKET": "@oas",
        "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "TZ": "UTC", "HOME": "/var/empty",
    }
    monkeypatch.setattr("aether.oas.host_entrypoint.validate_activation", activation)
    adapters = EntrypointAdapters(
        descriptor_intake=lambda *_args, **_kwargs: Descriptors(),
        service_factory=lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("factory")),
    )
    with pytest.raises(RuntimeError, match="factory"):
        run_entrypoint(
            "/tmp/aether-entrypoint-test",
            environment=environment,
            shutdown_event=threading.Event(),
            adapters=adapters,
        )


@pytest.mark.parametrize("failure", ["activation", "descriptor", "factory", "start", "notify"])
def test_entrypoint_fails_closed_at_each_startup_boundary(monkeypatch, failure: str):
    events = []
    environment = {
        "LISTEN_PID": str(os.getpid()), "LISTEN_FDS": "3",
        "LISTEN_FDNAMES": "runtime:bootstrap:broker", "NOTIFY_SOCKET": "@oas",
        "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "TZ": "UTC", "HOME": "/var/empty",
    }

    def activation(*_args, **_kwargs):
        events.append("activation")
        if failure == "activation":
            raise EntrypointError("activation")
        return {"state": "ACTIVATING"}

    class Descriptors:
        def close(self):
            events.append("descriptors-close")

    def descriptors(*_args, **_kwargs):
        events.append("descriptors")
        if failure == "descriptor":
            raise EntrypointError("descriptor")
        return Descriptors()

    class Service:
        def start(self):
            events.append("service-start")
            if failure == "start":
                raise RuntimeError("start")

        def serve_forever(self, **_kwargs):
            events.append("serve")

        def shutdown(self):
            events.append("service-stop")

    def factory(*_args, **_kwargs):
        events.append("factory")
        if failure == "factory":
            raise RuntimeError("factory")
        return Service()

    monkeypatch.setattr("aether.oas.host_entrypoint.validate_activation", activation)
    adapters = EntrypointAdapters(descriptor_intake=descriptors, service_factory=factory)
    notifier = (lambda **_kwargs: (_ for _ in ()).throw(RuntimeError("notify"))) if failure == "notify" else (lambda **_kwargs: events.append("ready"))
    with pytest.raises((EntrypointError, RuntimeError)):
        run_entrypoint("/tmp/aether-entrypoint-test", environment=environment, notifier=notifier, adapters=adapters)
    assert "ready" not in events
    if failure in {"factory", "descriptor"}:
        assert "descriptors-close" in events if failure == "factory" else "descriptors-close" not in events
    if failure in {"start", "notify"}:
        assert events[-1] == "service-stop"
