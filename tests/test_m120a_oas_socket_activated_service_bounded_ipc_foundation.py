"""Adversarial repository tests for the M120A OAS IPC foundation."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
import io
import json
import os
from pathlib import Path
import socket
import threading
import time

import pytest

import aether.oas.service as service_module
import aether.oas.socket_activation as activation_module
from aether.oas.ipc_protocol import (
    ENDPOINT_BOOTSTRAP,
    ENDPOINT_BROKER,
    ENDPOINT_RUNTIME,
    MAX_REQUEST_FRAME_BYTES,
    MAX_RESPONSE_FRAME_BYTES,
    ProtocolError,
    build_request,
    canonical_json,
    decode_request,
    decode_response,
    make_response,
)
from aether.oas.service import (
    OASService,
    PeerExpectation,
    ServiceIdentityContract,
)
from aether.oas.socket_activation import (
    ActivationContract,
    ActivatedDescriptors,
    EXPECTED_ENDPOINT_NAMES,
    SocketActivationError,
    SocketExpectation,
    intake_activated_descriptors,
)


def _contract(paths: dict[str, Path]) -> ActivationContract:
    uid = os.getuid()
    gid = os.getgid()
    return ActivationContract(
        tuple(
            SocketExpectation(role, str(paths[role]), uid, gid, 0o660)
            for role in EXPECTED_ENDPOINT_NAMES
        )
    )


def _identity_contract() -> ServiceIdentityContract:
    uid = os.getuid()
    gid = os.getgid()
    return ServiceIdentityContract(
        runtime=PeerExpectation("aether-runtime", uid, gid),
        bootstrap=PeerExpectation("aether-bootstrap", uid, gid),
        broker=PeerExpectation("root-broker", uid, gid),
    )


def _listeners(tmp_path: Path) -> tuple[dict[str, socket.socket], dict[str, Path]]:
    paths = {role: tmp_path / f"{role}.sock" for role in EXPECTED_ENDPOINT_NAMES}
    listeners: dict[str, socket.socket] = {}
    for role in EXPECTED_ENDPOINT_NAMES:
        listener = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        listener.bind(str(paths[role]))
        listener.listen(64)
        os.chmod(paths[role], 0o660)
        listeners[role] = listener
    return listeners, paths


@pytest.fixture
def listener_set(tmp_path: Path):
    listeners, paths = _listeners(tmp_path)
    yield listeners, paths
    for listener in listeners.values():
        listener.close()
    for path in paths.values():
        path.unlink(missing_ok=True)


@pytest.fixture
def service_fixture(tmp_path: Path):
    listeners, paths = _listeners(tmp_path)
    service = OASService(
        tmp_path / "service" / "oas.sqlite3",
        ActivatedDescriptors(dict(listeners)),
        _identity_contract(),
    )
    yield service, paths
    service.shutdown(timeout=2.0)
    for listener in listeners.values():
        listener.close()
    for path in paths.values():
        path.unlink(missing_ok=True)


def _request(
    role: str,
    operation: str,
    caller_class: str,
    *,
    request_id: str = "req_1",
    deadline: float | None = None,
    payload: dict | None = None,
):
    return build_request(
        endpoint_role=role,
        request_id=request_id,
        operation=operation,
        caller_class=caller_class,
        deadline_monotonic=deadline or time.monotonic() + 1.0,
        payload=payload or {},
    )


def _round_trip(service: OASService, role: str, path: Path, request) -> object:
    if not service.ready:
        service.start()
    with socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET) as client:
        client.settimeout(2.0)
        client.connect(str(path))
        client.send(request.encode())
        return decode_response(client.recv(MAX_RESPONSE_FRAME_BYTES))


def test_protocol_request_is_versioned_canonical_and_digest_bound():
    request = _request(ENDPOINT_RUNTIME, "PING", "aether-runtime")
    encoded = request.encode()
    assert len(encoded) <= MAX_REQUEST_FRAME_BYTES
    assert decode_request(encoded) == request
    assert encoded == canonical_json(request.to_dict()).encode()


@pytest.mark.parametrize(
    "raw_builder",
    [
        lambda request: request.replace(b'"operation":"PING"', b'"operation":"NOPE"'),
        lambda request: request.replace(b'"protocol_version":1', b'"protocol_version":2'),
        lambda request: request.replace(b'"payload_digest":"', b'"payload_digest":"0'),
        lambda request: b" " + request,
    ],
)
def test_protocol_rejects_wrong_version_operation_digest_and_noncanonical(raw_builder):
    request = _request(ENDPOINT_RUNTIME, "PING", "aether-runtime").encode()
    with pytest.raises(ProtocolError):
        decode_request(raw_builder(request))


def test_protocol_rejects_duplicate_unknown_and_non_object_fields():
    request = _request(ENDPOINT_RUNTIME, "PING", "aether-runtime").to_dict()
    encoded = json.dumps(
        {**request, "unknown": 1}, separators=(",", ":"), sort_keys=True
    ).encode()
    with pytest.raises(ProtocolError, match="fields"):
        decode_request(encoded)
    duplicate = encoded.replace(b',"unknown":1', b',"endpoint_role":"runtime","unknown":1')
    with pytest.raises(ProtocolError):
        decode_request(duplicate)
    with pytest.raises(ProtocolError):
        decode_request(b"[]")


def test_protocol_rejects_secret_fields_nonfinite_and_resource_overruns():
    with pytest.raises(ProtocolError, match="secret"):
        _request(
            ENDPOINT_RUNTIME,
            "PING",
            "aether-runtime",
            payload={"password": "not accepted"},
        )
    with pytest.raises(ProtocolError, match="finite"):
        canonical_json(float("nan"))
    with pytest.raises(ProtocolError):
        decode_request(b"x" * (MAX_REQUEST_FRAME_BYTES + 1))


def test_response_is_bounded_and_cannot_leak_private_fields():
    with pytest.raises(ProtocolError):
        make_response(
            request_id="req_large",
            classification="OK",
            result={"value": "x" * MAX_RESPONSE_FRAME_BYTES},
        ).encode()
    with pytest.raises(ProtocolError, match="secret"):
        make_response(
            request_id="req_secret",
            classification="OK",
            result={"database_path": "/private/oas.sqlite3"},
        ).encode()
    response = make_response(
        request_id="req_ok",
        classification="OK",
        result={"status": "AVAILABLE"},
    )
    assert decode_response(response.encode()) == response


def test_activation_intake_accepts_exact_descriptors_and_clears_environment(
    listener_set,
):
    listeners, paths = listener_set
    saved: dict[int, int | None] = {}
    try:
        for index, role in enumerate(EXPECTED_ENDPOINT_NAMES):
            fd = 3 + index
            try:
                saved[fd] = os.dup(fd)
            except OSError:
                saved[fd] = None
            os.dup2(listeners[role].fileno(), fd)
        environment = {
            "LISTEN_PID": str(os.getpid()),
            "LISTEN_FDS": "3",
            "LISTEN_FDNAMES": "runtime:bootstrap:broker",
        }
        descriptors = intake_activated_descriptors(
            _contract(paths), environment=environment
        )
        assert tuple(descriptors.sockets) == EXPECTED_ENDPOINT_NAMES
        assert environment == {}
        assert all(not os.get_inheritable(fd) for fd in range(3, 6))
        descriptors.close()
    finally:
        for fd, old_fd in saved.items():
            if old_fd is None:
                os.close(fd)
            else:
                os.dup2(old_fd, fd)
                os.close(old_fd)


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("LISTEN_PID", "999999"),
        ("LISTEN_FDS", "2"),
        ("LISTEN_FDNAMES", "runtime:runtime:broker"),
    ],
)
def test_activation_environment_must_be_exact(listener_set, key, value):
    listeners, paths = listener_set
    saved: dict[int, int | None] = {}
    try:
        for index, role in enumerate(EXPECTED_ENDPOINT_NAMES):
            fd = 3 + index
            try:
                saved[fd] = os.dup(fd)
            except OSError:
                saved[fd] = None
            os.dup2(listeners[role].fileno(), fd)
        environment = {
            "LISTEN_PID": str(os.getpid()),
            "LISTEN_FDS": "3",
            "LISTEN_FDNAMES": "runtime:bootstrap:broker",
        }
        environment[key] = value
        with pytest.raises(SocketActivationError):
            intake_activated_descriptors(_contract(paths), environment=environment)
        assert set(environment) == {"LISTEN_PID", "LISTEN_FDS", "LISTEN_FDNAMES"}
    finally:
        for fd, old_fd in saved.items():
            if old_fd is None:
                os.close(fd)
            else:
                os.dup2(old_fd, fd)
                os.close(old_fd)


@pytest.mark.parametrize("field", ["expected_uid", "expected_gid", "expected_mode"])
def test_activation_rejects_wrong_owner_group_or_mode_without_consuming_fds(
    listener_set, field
):
    listeners, paths = listener_set
    saved: dict[int, int | None] = {}
    try:
        for index, role in enumerate(EXPECTED_ENDPOINT_NAMES):
            fd = 3 + index
            try:
                saved[fd] = os.dup(fd)
            except OSError:
                saved[fd] = None
            os.dup2(listeners[role].fileno(), fd)
        expectations = list(_contract(paths).expectations)
        current = expectations[0]
        value = {
            "expected_uid": current.expected_uid + 1,
            "expected_gid": current.expected_gid + 1,
            "expected_mode": 0o600,
        }[field]
        expectations[0] = replace(current, **{field: value})
        invalid_contract = ActivationContract(tuple(expectations))
        before = [os.get_inheritable(fd) for fd in range(3, 6)]
        with pytest.raises(SocketActivationError):
            intake_activated_descriptors(
                invalid_contract,
                environment={
                    "LISTEN_PID": str(os.getpid()),
                    "LISTEN_FDS": "3",
                    "LISTEN_FDNAMES": "runtime:bootstrap:broker",
                },
            )
        assert [os.get_inheritable(fd) for fd in range(3, 6)] == before
    finally:
        for fd, old_fd in saved.items():
            if old_fd is None:
                os.close(fd)
            else:
                os.dup2(old_fd, fd)
                os.close(old_fd)


def test_activation_rejects_descriptor_substitution_and_path_identity(listener_set):
    listeners, paths = listener_set
    saved: dict[int, int | None] = {}
    try:
        for index, role in enumerate(EXPECTED_ENDPOINT_NAMES):
            fd = 3 + index
            try:
                saved[fd] = os.dup(fd)
            except OSError:
                saved[fd] = None
            os.dup2(listeners[role].fileno(), fd)
        os.dup2(listeners[ENDPOINT_RUNTIME].fileno(), 4)
        with pytest.raises(SocketActivationError, match="path|inode"):
            intake_activated_descriptors(
                _contract(paths),
                environment={
                    "LISTEN_PID": str(os.getpid()),
                    "LISTEN_FDS": "3",
                    "LISTEN_FDNAMES": "runtime:bootstrap:broker",
                },
            )
    finally:
        for fd, old_fd in saved.items():
            if old_fd is None:
                os.close(fd)
            else:
                os.dup2(old_fd, fd)
                os.close(old_fd)


def test_activation_rejects_non_seqpacket_or_non_listening_descriptor(tmp_path: Path):
    path = tmp_path / "wrong.sock"
    stream = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    stream.bind(str(path))
    stream.listen(1)
    os.chmod(path, 0o660)
    try:
        expectations = tuple(
            SocketExpectation(role, str(tmp_path / f"{role}.sock"), os.getuid(), os.getgid(), 0o660)
            for role in EXPECTED_ENDPOINT_NAMES
        )
        contract = ActivationContract(expectations)
        saved: dict[int, int | None] = {}
        for index in range(3):
            fd = 3 + index
            try:
                saved[fd] = os.dup(fd)
            except OSError:
                saved[fd] = None
            os.dup2(stream.fileno(), fd)
        with pytest.raises(SocketActivationError):
            intake_activated_descriptors(
                contract,
                environment={
                    "LISTEN_PID": str(os.getpid()),
                    "LISTEN_FDS": "3",
                    "LISTEN_FDNAMES": "runtime:bootstrap:broker",
                },
            )
        for fd, old_fd in saved.items():
            if old_fd is None:
                os.close(fd)
            else:
                os.dup2(old_fd, fd)
                os.close(old_fd)
    finally:
        stream.close()
        path.unlink(missing_ok=True)


@pytest.mark.parametrize(
    "evidence",
    [
        OSError("procfs unavailable"),
        "not a proc unix table\n",
        "Num       RefCount Protocol Flags    Type St Inode Path\n"
        "00000000: 00000002 00000000 00010000 0005 01 999 /other.sock\n",
    ],
)
def test_linux_kernel_socket_identity_evidence_fails_closed(monkeypatch, evidence):
    monkeypatch.setattr(activation_module.sys, "platform", "linux")

    if isinstance(evidence, BaseException):
        def unavailable(*_args, **_kwargs):
            raise evidence

        monkeypatch.setattr("builtins.open", unavailable)
    else:
        monkeypatch.setattr(
            "builtins.open", lambda *_args, **_kwargs: io.StringIO(evidence)
        )
    assert activation_module._proc_socket_identity_matches(123, "/expected.sock") is False


def test_concurrent_duplicate_start_is_serialized(service_fixture):
    service, _paths = service_fixture
    barrier = threading.Barrier(8)

    def invoke(_: int):
        barrier.wait()
        service.start()

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(invoke, range(8)))
    assert service.ready
    assert len(service._accept_threads) == 3
    service.shutdown(timeout=1.0)


def test_partial_start_failure_cleans_accept_threads_and_executor(service_fixture, monkeypatch):
    service, _paths = service_fixture
    real_thread = threading.Thread
    calls = 0

    def failing_thread(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise RuntimeError("forced thread start failure")
        return real_thread(*args, **kwargs)

    monkeypatch.setattr(service_module.threading, "Thread", failing_thread)
    with pytest.raises(RuntimeError, match="forced thread start failure"):
        service.start()
    assert not service.ready
    assert service._executor is None
    assert service.in_flight_requests == 0
    assert all(not thread.is_alive() for thread in service._accept_threads)
    service.shutdown(timeout=0.0)


def test_executor_submission_failure_releases_reservation(service_fixture, monkeypatch):
    service, _paths = service_fixture
    service.start()

    def fail_submit(*_args, **_kwargs):
        raise RuntimeError("executor unavailable")

    monkeypatch.setattr(service._executor, "submit", fail_submit)
    client, connection = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
    try:
        service._admit_connection(ENDPOINT_RUNTIME, connection)
        assert service.in_flight_requests == 0
        assert service.active_requests == 0
        assert service.queued_requests == 0
    finally:
        client.close()
        connection.close()
        service.shutdown(timeout=1.0)


def test_active_and_queued_request_ceiling_and_first_overload_are_deterministic(
    service_fixture,
):
    service, _paths = service_fixture
    service.start()
    entered = threading.Event()
    release = threading.Event()
    admitted: list[tuple[socket.socket, socket.socket]] = []

    def blocked_worker(_endpoint_role: str, _connection: socket.socket) -> None:
        entered.set()
        release.wait(2.0)

    service._connection_worker = blocked_worker
    try:
        for _ in range(service_module.MAX_IN_FLIGHT_REQUESTS):
            client, connection = socket.socketpair(
                socket.AF_UNIX, socket.SOCK_SEQPACKET
            )
            admitted.append((client, connection))
            service._admit_connection(ENDPOINT_RUNTIME, connection)
        deadline = time.monotonic() + 1.0
        while time.monotonic() < deadline and service.active_requests < service_module.MAX_ACTIVE_REQUESTS:
            time.sleep(0.005)
        assert service.active_requests == service_module.MAX_ACTIVE_REQUESTS
        assert service.queued_requests == service_module.MAX_QUEUED_REQUESTS
        assert service.in_flight_requests == service_module.MAX_IN_FLIGHT_REQUESTS

        extra_client, extra_connection = socket.socketpair(
            socket.AF_UNIX, socket.SOCK_SEQPACKET
        )
        try:
            extra_client.settimeout(1.0)
            service._admit_connection(ENDPOINT_RUNTIME, extra_connection)
            response = decode_response(extra_client.recv(MAX_RESPONSE_FRAME_BYTES))
            assert response.result_classification == "OVERLOADED"
            assert service.in_flight_requests == service_module.MAX_IN_FLIGHT_REQUESTS
        finally:
            extra_client.close()
            extra_connection.close()
    finally:
        release.set()
        service.shutdown(timeout=1.0)
        for client, connection in admitted:
            client.close()
            connection.close()


def test_stalled_receive_is_interrupted_by_bounded_shutdown(service_fixture):
    service, paths = service_fixture
    service.start()
    client = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
    client.settimeout(1.0)
    client.connect(str(paths[ENDPOINT_RUNTIME]))
    time.sleep(0.02)
    started = time.monotonic()
    service.shutdown(timeout=0.2)
    elapsed = time.monotonic() - started
    client.close()
    assert elapsed < 0.5
    assert service.in_flight_requests == 0
    assert not service.ready


def test_blocked_worker_shutdown_returns_at_timeout_and_tracks_outstanding_work(
    service_fixture,
):
    service, _paths = service_fixture
    service.start()
    release = threading.Event()
    client, connection = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)

    def blocked_worker(_endpoint_role: str, _connection: socket.socket) -> None:
        release.wait(2.0)

    service._connection_worker = blocked_worker
    service._admit_connection(ENDPOINT_RUNTIME, connection)
    started = time.monotonic()
    service.shutdown(timeout=0.05)
    elapsed = time.monotonic() - started
    assert elapsed < 0.3
    assert not service.ready
    assert service.in_flight_requests == 1
    release.set()
    service.shutdown(timeout=1.0)
    assert service.in_flight_requests == 0
    client.close()
    connection.close()


def test_concurrent_shutdown_is_idempotent_and_leak_free(service_fixture):
    service, _paths = service_fixture
    service.start()
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(lambda _index: service.shutdown(timeout=1.0), range(8)))
    assert not service.ready
    assert service.in_flight_requests == 0
    assert service._state == service_module._STATE_STOPPED


def test_accept_and_shutdown_race_releases_every_reservation(service_fixture):
    service, _paths = service_fixture
    service.start()
    barrier = threading.Barrier(17)
    pairs: list[tuple[socket.socket, socket.socket]] = []
    pairs_lock = threading.Lock()

    def admit(_: int) -> None:
        client, connection = socket.socketpair(
            socket.AF_UNIX, socket.SOCK_SEQPACKET
        )
        with pairs_lock:
            pairs.append((client, connection))
        barrier.wait()
        service._admit_connection(ENDPOINT_RUNTIME, connection)

    with ThreadPoolExecutor(max_workers=16) as pool:
        futures = [pool.submit(admit, index) for index in range(16)]
        barrier.wait()
        service.shutdown(timeout=1.0)
        for future in futures:
            future.result()
    assert service.in_flight_requests == 0
    assert service.active_requests == 0
    assert service.queued_requests == 0
    for client, connection in pairs:
        client.close()
        connection.close()


def test_malformed_request_has_deterministic_protocol_classification(service_fixture):
    service, _paths = service_fixture
    client, connection = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
    try:
        thread = threading.Thread(
            target=service._serve_connection,
            args=(ENDPOINT_RUNTIME, connection),
        )
        thread.start()
        client.send(b"{}")
        response = decode_response(client.recv(MAX_RESPONSE_FRAME_BYTES))
        thread.join(1.0)
        assert response.result_classification == "INVALID_REQUEST"
        assert response.error == "INVALID_REQUEST"
    finally:
        client.close()
        connection.close()


def test_deadline_expiry_during_slow_status_read_cannot_return_success(service_fixture):
    service, _paths = service_fixture
    original_status = service._runtime_status

    def slow_status(request_id: str):
        time.sleep(0.03)
        return original_status(request_id)

    service._runtime_status = slow_status
    response = service.handle_request(
        ENDPOINT_RUNTIME,
        _request(
            ENDPOINT_RUNTIME,
            "GET_BOUNDED_RUNTIME_STATUS",
            "aether-runtime",
            deadline=time.monotonic() + 0.005,
        ),
        peer_uid=os.getuid(),
        peer_gid=os.getgid(),
    )
    assert response.result_classification == "DEADLINE_EXCEEDED"


def test_runtime_ping_and_redacted_uninitialized_status_use_real_af_unix(
    service_fixture,
):
    service, paths = service_fixture
    ping = _round_trip(
        service,
        ENDPOINT_RUNTIME,
        paths[ENDPOINT_RUNTIME],
        _request(ENDPOINT_RUNTIME, "PING", "aether-runtime"),
    )
    assert ping.result_classification == "OK"
    assert ping.result["response"] == "PONG"
    status = _round_trip(
        service,
        ENDPOINT_RUNTIME,
        paths[ENDPOINT_RUNTIME],
        _request(
            ENDPOINT_RUNTIME,
            "GET_BOUNDED_RUNTIME_STATUS",
            "aether-runtime",
            request_id="status_1",
        ),
    )
    assert status.result_classification == "UNINITIALIZED"
    assert status.result["canonical_instance_state_exists"] is False
    assert status.result["redacted_lifecycle_readiness"] == "UNINITIALIZED"
    assert "aether_instance_id" not in status.result
    assert "trust_generation" not in status.result
    assert "lifecycle_state" not in status.result
    assert "database_path" not in status.result


def test_status_reports_only_redacted_readiness_when_kernel_has_instance(service_fixture):
    service, paths = service_fixture
    # The service endpoint cannot initialize state; use a separate kernel request
    # only through the service-owned test fixture to establish read-only reporting.
    from aether.oas.security_kernel import SecurityKernel, SecurityTransactionRequest

    kernel_request = SecurityTransactionRequest.build(
        transaction_id="tx_setup",
        aether_instance_id="instance_m120a",
        expected_trust_generation=0,
        exact_operation="initialize_instance",
        idempotency_key="idem_setup",
        payload={},
    )
    SecurityKernel(service.store_path).initialize_instance(kernel_request)
    status = _round_trip(
        service,
        ENDPOINT_RUNTIME,
        paths[ENDPOINT_RUNTIME],
        _request(
            ENDPOINT_RUNTIME,
            "GET_BOUNDED_RUNTIME_STATUS",
            "aether-runtime",
            request_id="status_2",
        ),
    )
    assert status.result_classification == "OK"
    assert status.result["canonical_instance_state_exists"] is True
    assert status.result["redacted_lifecycle_readiness"] == "READY"
    assert all(secret not in json.dumps(status.result) for secret in ("instance_m120a", "trust_generation", "UNCLAIMED"))


@pytest.mark.parametrize(
    ("role", "operation", "caller"),
    [
        (ENDPOINT_BOOTSTRAP, "BEGIN_LOCAL_BOOTSTRAP_WINDOW", "aether-bootstrap"),
        (ENDPOINT_BOOTSTRAP, "CANCEL_LOCAL_BOOTSTRAP_WINDOW", "aether-bootstrap"),
        (ENDPOINT_BROKER, "ISSUE_LOCAL_BOOTSTRAP_CHALLENGE", "root-broker"),
        (ENDPOINT_BROKER, "REGISTER_LOCAL_BOOTSTRAP_AUTHORIZATION", "root-broker"),
        (ENDPOINT_BROKER, "REVOKE_LOCAL_BOOTSTRAP_AUTHORIZATION", "root-broker"),
    ],
)
def test_bootstrap_and_broker_operations_fail_closed_without_kernel_mutation(
    service_fixture, role, operation, caller
):
    service, _paths = service_fixture
    before = service._kernel.list_audit_events()
    response = service.handle_request(
        role,
        _request(role, operation, caller),
        peer_uid=os.getuid(),
        peer_gid=os.getgid(),
    )
    assert response.result_classification == "NOT_IMPLEMENTED"
    assert response.result == {
        "authorization": "NOT_AUTHORIZED_IN_M120A",
        "mutation": "NONE",
    }
    assert service._kernel.list_audit_events() == before


def test_endpoint_specific_operation_vocabularies_fail_closed(service_fixture):
    service, _paths = service_fixture
    with pytest.raises(ProtocolError):
        service.handle_request(
            ENDPOINT_BOOTSTRAP,
            _request(ENDPOINT_RUNTIME, "PING", "aether-runtime"),
            peer_uid=os.getuid(),
            peer_gid=os.getgid(),
        )


def test_kernel_peer_credentials_override_caller_class_and_wrong_identity_is_rejected(
    service_fixture,
):
    service, _paths = service_fixture
    unauthorized = service.handle_request(
        ENDPOINT_RUNTIME,
        _request(ENDPOINT_RUNTIME, "PING", "claimed-owner"),
        peer_uid=os.getuid(),
        peer_gid=os.getgid(),
    )
    assert unauthorized.result_classification == "UNAUTHORIZED_PEER"
    wrong_uid = service.handle_request(
        ENDPOINT_RUNTIME,
        _request(ENDPOINT_RUNTIME, "PING", "aether-runtime"),
        peer_uid=os.getuid() + 1,
        peer_gid=os.getgid(),
    )
    assert wrong_uid.result_classification == "UNAUTHORIZED_PEER"


def test_actual_scm_rights_and_unexpected_ancillary_data_are_rejected(service_fixture):
    service, paths = service_fixture
    service.start()
    with socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET) as client:
        client.settimeout(2.0)
        client.connect(str(paths[ENDPOINT_RUNTIME]))
        with open(__file__, "rb") as supplied:
            request = _request(ENDPOINT_RUNTIME, "PING", "aether-runtime").encode()
            client.sendmsg([request], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, supplied.fileno().to_bytes(4, "little"))])
            response = decode_response(client.recv(MAX_RESPONSE_FRAME_BYTES))
    assert response.result_classification == "PROTOCOL_ERROR"


def test_actual_oversized_and_truncated_messages_fail_closed(service_fixture):
    service, paths = service_fixture
    service.start()
    with socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET) as client:
        client.settimeout(2.0)
        client.connect(str(paths[ENDPOINT_RUNTIME]))
        client.send(b"{" + b"x" * MAX_REQUEST_FRAME_BYTES)
        response = decode_response(client.recv(MAX_RESPONSE_FRAME_BYTES))
    assert response.result_classification == "PROTOCOL_ERROR"


def test_expired_request_and_runtime_mutation_attempt_are_bounded(service_fixture):
    service, paths = service_fixture
    expired = _round_trip(
        service,
        ENDPOINT_RUNTIME,
        paths[ENDPOINT_RUNTIME],
        _request(
            ENDPOINT_RUNTIME,
            "PING",
            "aether-runtime",
            deadline=time.monotonic() - 1,
        ),
    )
    assert expired.result_classification == "DEADLINE_EXCEEDED"
    mutation = replace(
        _request(ENDPOINT_RUNTIME, "PING", "aether-runtime"),
        operation="initialize_instance",
    )
    with pytest.raises(ProtocolError):
        service.handle_request(
            ENDPOINT_RUNTIME,
            mutation,
            peer_uid=os.getuid(),
            peer_gid=os.getgid(),
        )
    assert service._kernel.list_audit_events() == []


def test_endpoint_deadline_bounds_cannot_be_extended_by_the_request(service_fixture):
    service, _paths = service_fixture
    response = service.handle_request(
        ENDPOINT_RUNTIME,
        _request(
            ENDPOINT_RUNTIME,
            "PING",
            "aether-runtime",
            deadline=time.monotonic() + 2.0,
        ),
        peer_uid=os.getuid(),
        peer_gid=os.getgid(),
    )
    assert response.result_classification == "INVALID_REQUEST"


def test_concurrent_runtime_requests_and_bounded_shutdown(service_fixture):
    service, paths = service_fixture

    def call(index: int):
        return _round_trip(
            service,
            ENDPOINT_RUNTIME,
            paths[ENDPOINT_RUNTIME],
            _request(
                ENDPOINT_RUNTIME,
                "PING",
                "aether-runtime",
                request_id=f"concurrent_{index}",
            ),
        )

    with ThreadPoolExecutor(max_workers=16) as pool:
        responses = list(pool.map(call, range(16)))
    assert all(response.result_classification == "OK" for response in responses)
    assert service.in_flight_requests == 0
    service.shutdown(timeout=2.0)
    assert not service.ready


def test_service_entry_has_no_application_or_public_package_surface():
    import aether.oas as package

    assert package.__all__ == ()
    assert not hasattr(package, "OASService")
    assert not hasattr(package, "Request")
    assert not hasattr(package, "SecurityKernel")
