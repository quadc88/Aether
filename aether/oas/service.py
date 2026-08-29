"""Standalone bounded OAS IPC service foundation for M120A."""

from __future__ import annotations

from dataclasses import dataclass
from concurrent.futures import Future, ThreadPoolExecutor
import logging
import os
from pathlib import Path
import socket
import struct
import threading
import time
from typing import Mapping

from .ipc_protocol import (
    ENDPOINT_BOOTSTRAP,
    ENDPOINT_BROKER,
    ENDPOINT_RUNTIME,
    MAX_REQUEST_FRAME_BYTES,
    OPERATIONS_BY_ENDPOINT,
    ProtocolError,
    RequestDeadlineExceeded,
    Request,
    Response,
    ensure_not_expired,
    decode_request,
    make_error_response,
    make_response,
)
from .security_kernel import SecurityKernel
from .socket_activation import ActivationContract, ActivatedDescriptors, intake_activated_descriptors


LOGGER = logging.getLogger(__name__)
MAX_ACTIVE_REQUESTS = 32
MAX_QUEUED_REQUESTS = 64
MAX_IN_FLIGHT_REQUESTS = MAX_ACTIVE_REQUESTS + MAX_QUEUED_REQUESTS
RUNTIME_DEADLINE_SECONDS = 1.0
BOOTSTRAP_BROKER_DEADLINE_SECONDS = 5.0
CONNECTION_TIMEOUT_SECONDS = 2.0
SHUTDOWN_TIMEOUT_SECONDS = 10.0
_STATE_STOPPED = "STOPPED"
_STATE_STARTING = "STARTING"
_STATE_RUNNING = "RUNNING"
_STATE_STOPPING = "STOPPING"


@dataclass(frozen=True, slots=True)
class PeerExpectation:
    caller_class: str
    uid: int
    gid: int


@dataclass(frozen=True, slots=True)
class ServiceIdentityContract:
    runtime: PeerExpectation
    bootstrap: PeerExpectation
    broker: PeerExpectation

    def for_endpoint(self, endpoint_role: str) -> PeerExpectation:
        try:
            return {
                ENDPOINT_RUNTIME: self.runtime,
                ENDPOINT_BOOTSTRAP: self.bootstrap,
                ENDPOINT_BROKER: self.broker,
            }[endpoint_role]
        except KeyError as exc:
            raise ValueError("unknown endpoint role") from exc


DeploymentIdentityContract = ServiceIdentityContract


def _peer_credentials(connection: socket.socket) -> tuple[int, int, int]:
    raw = connection.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12)
    if len(raw) != 12:
        raise OSError("SO_PEERCRED returned an invalid credential record")
    peer_pid, peer_uid, peer_gid = struct.unpack("3i", raw)
    return peer_uid, peer_gid, peer_pid


class OASService:
    """Bounded socket service with no IPC operation that mutates canonical state."""

    def __init__(
        self,
        store_path: str | Path,
        activated_descriptors: ActivatedDescriptors | Mapping[str, socket.socket],
        identity_contract: ServiceIdentityContract,
        *,
        clock=time.monotonic,
    ) -> None:
        if not isinstance(store_path, (str, Path)) or not str(store_path):
            raise TypeError("service-owned store_path is required")
        self._store_path = Path(store_path)
        if isinstance(activated_descriptors, ActivatedDescriptors):
            self._descriptors = activated_descriptors
        else:
            self._descriptors = ActivatedDescriptors(dict(activated_descriptors))
        self._identity_contract = identity_contract
        self._clock = clock
        self._kernel = SecurityKernel(self._store_path)
        self._stop_event = threading.Event()
        self._start_lock = threading.Lock()
        self._state_condition = threading.Condition(threading.RLock())
        self._state = _STATE_STOPPED
        self._in_flight = 0
        self._executor: ThreadPoolExecutor | None = None
        self._accept_threads: list[threading.Thread] = []
        self._reservations: dict[Future[object], socket.socket] = {}
        self._connections: set[socket.socket] = set()
        self._shutdown_complete = threading.Event()
        self._shutdown_complete.set()
        self._listeners_closed = False
        self._started = False

    @property
    def store_path(self) -> Path:
        return self._store_path

    @property
    def ready(self) -> bool:
        with self._state_condition:
            return self._state == _STATE_RUNNING

    @property
    def in_flight_requests(self) -> int:
        with self._state_condition:
            return self._in_flight

    @property
    def active_requests(self) -> int:
        with self._state_condition:
            return sum(future.running() for future in self._reservations)

    @property
    def queued_requests(self) -> int:
        with self._state_condition:
            return self._in_flight - self.active_requests

    def _maybe_finish_shutdown_locked(self) -> None:
        if self._state != _STATE_STOPPING:
            return
        if self._reservations or any(thread.is_alive() for thread in self._accept_threads):
            return
        self._state = _STATE_STOPPED
        self._started = False
        self._executor = None
        self._accept_threads.clear()
        self._connections.clear()
        self._shutdown_complete.set()
        self._state_condition.notify_all()

    def _future_done(self, future: Future[object]) -> None:
        with self._state_condition:
            connection = self._reservations.pop(future, None)
            if connection is None:
                return
            self._connections.discard(connection)
            if future.cancelled():
                try:
                    connection.close()
                except OSError:
                    pass
            self._in_flight -= 1
            self._maybe_finish_shutdown_locked()
            self._state_condition.notify_all()

    def _reject_connection(
        self, connection: socket.socket, classification: str
    ) -> None:
        try:
            connection.settimeout(0.05)
            self._send_response(
                connection, make_error_response(classification=classification)
            )
        finally:
            connection.close()

    def _admit_connection(self, endpoint_role: str, connection: socket.socket) -> None:
        rejection: str | None = None
        with self._state_condition:
            executor = self._executor
            if self._state != _STATE_RUNNING or executor is None:
                rejection = "UNAVAILABLE"
            elif self._in_flight >= MAX_IN_FLIGHT_REQUESTS:
                rejection = "OVERLOADED"
            else:
                self._in_flight += 1
                self._connections.add(connection)
                try:
                    future = executor.submit(
                        self._connection_worker, endpoint_role, connection
                    )
                except (RuntimeError, OSError):
                    self._connections.discard(connection)
                    self._in_flight -= 1
                    rejection = "UNAVAILABLE"
                else:
                    self._reservations[future] = connection
                    future.add_done_callback(self._future_done)
        if rejection is not None:
            self._reject_connection(connection, rejection)

    def start(self) -> None:
        with self._start_lock:
            with self._state_condition:
                if self._state == _STATE_RUNNING:
                    return
                if self._state in (_STATE_STARTING, _STATE_STOPPING):
                    raise RuntimeError("OAS service lifecycle transition is in progress")
                if self._listeners_closed:
                    raise RuntimeError("OAS service cannot restart after shutdown")
                self._state = _STATE_STARTING
                self._shutdown_complete.clear()
                self._stop_event.clear()
                try:
                    self._executor = ThreadPoolExecutor(
                        max_workers=MAX_ACTIVE_REQUESTS,
                        thread_name_prefix="aether-oas",
                    )
                except BaseException:
                    self._state = _STATE_STOPPED
                    self._shutdown_complete.set()
                    raise

            try:
                for endpoint_role, listener in self._descriptors.sockets.items():
                    with self._state_condition:
                        if self._state != _STATE_STARTING:
                            raise RuntimeError("OAS service start was interrupted")
                    listener.settimeout(0.2)
                    thread = threading.Thread(
                        target=self._accept_loop,
                        args=(endpoint_role, listener),
                        name=f"aether-oas-{endpoint_role}-accept",
                        daemon=True,
                    )
                    thread.start()
                    with self._state_condition:
                        self._accept_threads.append(thread)
                        self._state_condition.notify_all()
                with self._state_condition:
                    if self._state != _STATE_STARTING:
                        raise RuntimeError("OAS service start was interrupted")
                    self._state = _STATE_RUNNING
                    self._started = True
                    self._state_condition.notify_all()
            except BaseException:
                with self._state_condition:
                    self._stop_event.set()
                    self._listeners_closed = True
                    if self._state == _STATE_STARTING:
                        self._state = _STATE_STOPPING
                    listeners = tuple(self._descriptors.sockets.values())
                    executor = self._executor
                for listener in listeners:
                    try:
                        listener.close()
                    except OSError:
                        pass
                if executor is not None:
                    executor.shutdown(wait=False, cancel_futures=True)
                deadline = time.monotonic() + 0.5
                while time.monotonic() < deadline:
                    with self._state_condition:
                        self._maybe_finish_shutdown_locked()
                        threads = tuple(self._accept_threads)
                        if self._state == _STATE_STOPPED:
                            break
                    for thread in threads:
                        thread.join(min(0.01, max(0.0, deadline - time.monotonic())))
                raise

    def _accept_loop(self, endpoint_role: str, listener: socket.socket) -> None:
        try:
            while not self._stop_event.is_set():
                try:
                    connection, _ = listener.accept()
                except socket.timeout:
                    continue
                except OSError:
                    if self._stop_event.is_set():
                        return
                    LOGGER.warning("OAS accept failed classification=UNAVAILABLE")
                    return
                self._admit_connection(endpoint_role, connection)
        finally:
            with self._state_condition:
                current = threading.current_thread()
                self._accept_threads = [
                    thread for thread in self._accept_threads if thread is not current
                ]
                self._maybe_finish_shutdown_locked()
                self._state_condition.notify_all()

    def _connection_worker(self, endpoint_role: str, connection: socket.socket) -> None:
        try:
            self._serve_connection(endpoint_role, connection)
        finally:
            with self._state_condition:
                self._connections.discard(connection)
                self._state_condition.notify_all()

    def _send_response(self, connection: socket.socket, response: Response) -> None:
        try:
            connection.sendall(response.encode())
        except (OSError, ProtocolError):
            LOGGER.info("OAS response unavailable classification=UNAVAILABLE")

    def _serve_connection(self, endpoint_role: str, connection: socket.socket) -> None:
        connection.settimeout(CONNECTION_TIMEOUT_SECONDS)
        request: Request | None = None
        try:
            try:
                peer_uid, peer_gid, _peer_pid = _peer_credentials(connection)
            except OSError:
                self._send_response(
                    connection,
                    make_error_response(classification="UNAUTHORIZED_PEER"),
                )
                return
            expectation = self._identity_contract.for_endpoint(endpoint_role)
            if (peer_uid, peer_gid) != (expectation.uid, expectation.gid):
                self._send_response(
                    connection,
                    make_error_response(classification="UNAUTHORIZED_PEER"),
                )
                return
            ancillary_space = socket.CMSG_SPACE(256)
            frame, ancillary, flags, _address = connection.recvmsg(
                MAX_REQUEST_FRAME_BYTES + 1, ancillary_space
            )
            if not frame:
                return
            if (
                ancillary
                or flags & (socket.MSG_TRUNC | socket.MSG_CTRUNC)
                or len(frame) > MAX_REQUEST_FRAME_BYTES
            ):
                self._send_response(
                    connection,
                    make_error_response(classification="PROTOCOL_ERROR"),
                )
                return
            try:
                request = decode_request(frame)
                self._set_request_timeout(connection, request.deadline_monotonic)
                response = self.handle_request(
                    endpoint_role,
                    request,
                    peer_uid=peer_uid,
                    peer_gid=peer_gid,
                    now=self._clock(),
                )
            except RequestDeadlineExceeded:
                response = make_error_response(classification="DEADLINE_EXCEEDED")
            except ProtocolError:
                response = make_error_response(classification="INVALID_REQUEST")
            except Exception:
                LOGGER.warning("OAS handler failed classification=INTERNAL_ERROR")
                response = make_error_response(classification="INTERNAL_ERROR")
            if request is not None:
                self._set_response_timeout(connection, request.deadline_monotonic)
            self._send_response(connection, response)
        except socket.timeout:
            LOGGER.info("OAS connection expired classification=DEADLINE_EXCEEDED")
        except OSError:
            LOGGER.info("OAS connection failed classification=UNAVAILABLE")
        finally:
            connection.close()

    def _set_request_timeout(self, connection: socket.socket, deadline: float) -> None:
        remaining = float(deadline) - self._clock()
        connection.settimeout(
            max(0.001, min(CONNECTION_TIMEOUT_SECONDS, remaining))
            if remaining > 0
            else 0.05
        )

    def _set_response_timeout(self, connection: socket.socket, deadline: float) -> None:
        self._set_request_timeout(connection, deadline)

    def handle_request(
        self,
        endpoint_role: str,
        request: Request,
        *,
        peer_uid: int,
        peer_gid: int,
        now: float | None = None,
    ) -> Response:
        """Dispatch one already-kernel-authenticated request for deterministic tests."""

        if endpoint_role not in OPERATIONS_BY_ENDPOINT:
            raise ProtocolError("unknown endpoint role")
        request.encode()
        expectation = self._identity_contract.for_endpoint(endpoint_role)
        if (peer_uid, peer_gid) != (expectation.uid, expectation.gid):
            return make_error_response(
                request_id=request.request_id, classification="UNAUTHORIZED_PEER"
            )
        if request.endpoint_role != endpoint_role:
            raise ProtocolError("request endpoint role does not match descriptor")
        if request.caller_class != expectation.caller_class:
            return make_error_response(
                request_id=request.request_id, classification="UNAUTHORIZED_PEER"
            )
        request_now = self._clock() if now is None else now
        try:
            ensure_not_expired(request, now=request_now)
        except RequestDeadlineExceeded:
            return make_error_response(
                request_id=request.request_id, classification="DEADLINE_EXCEEDED"
            )
        endpoint_deadline = (
            RUNTIME_DEADLINE_SECONDS
            if endpoint_role == ENDPOINT_RUNTIME
            else BOOTSTRAP_BROKER_DEADLINE_SECONDS
        )
        if float(request.deadline_monotonic) > request_now + endpoint_deadline:
            return make_error_response(
                request_id=request.request_id, classification="INVALID_REQUEST"
            )

        if endpoint_role == ENDPOINT_RUNTIME:
            if request.operation == "PING":
                response = make_response(
                    request_id=request.request_id,
                    classification="OK",
                    result={
                        "service_availability": "AVAILABLE",
                        "response": "PONG",
                        "ipc_protocol_version": 1,
                    },
                )
            elif request.operation == "GET_BOUNDED_RUNTIME_STATUS":
                response = self._runtime_status(request.request_id)
            else:
                raise ProtocolError("operation is not valid for endpoint")
        elif request.operation in OPERATIONS_BY_ENDPOINT[endpoint_role]:
            response = make_response(
                request_id=request.request_id,
                classification="NOT_IMPLEMENTED",
                result={
                    "authorization": "NOT_AUTHORIZED_IN_M120A",
                    "mutation": "NONE",
                },
            )
        else:
            raise ProtocolError("operation is not valid for endpoint")
        try:
            ensure_not_expired(request, now=self._clock())
        except RequestDeadlineExceeded:
            return make_error_response(
                request_id=request.request_id, classification="DEADLINE_EXCEEDED"
            )
        return response

    def _runtime_status(self, request_id: str) -> Response:
        try:
            instance = self._kernel.get_instance_trust()
        except Exception:
            return make_error_response(
                request_id=request_id, classification="UNAVAILABLE"
            )
        exists = instance is not None
        return make_response(
            request_id=request_id,
            classification="OK" if exists else "UNINITIALIZED",
            result={
                "service_availability": "AVAILABLE",
                "ipc_protocol_version": 1,
                "security_kernel_schema_version": 1,
                "redacted_lifecycle_readiness": "READY" if exists else "UNINITIALIZED",
                "canonical_instance_state_exists": exists,
            },
        )

    def shutdown(self, *, timeout: float = SHUTDOWN_TIMEOUT_SECONDS) -> None:
        deadline = time.monotonic() + max(0.0, timeout)
        with self._state_condition:
            if self._state == _STATE_STOPPED:
                return
            if self._state == _STATE_STOPPING:
                completion = self._shutdown_complete
            else:
                self._state = _STATE_STOPPING
                self._started = False
                self._stop_event.set()
                self._listeners_closed = True
                listeners = tuple(self._descriptors.sockets.values())
                connections = tuple(self._connections)
                executor = self._executor
                completion = self._shutdown_complete
                for listener in listeners:
                    try:
                        listener.close()
                    except OSError:
                        pass
                for connection in connections:
                    try:
                        connection.shutdown(socket.SHUT_RDWR)
                    except OSError:
                        pass
                    try:
                        connection.close()
                    except OSError:
                        pass
                if executor is not None:
                    # wait=False is intentional; completion is polled through
                    # tracked futures so shutdown has a real deadline.
                    executor.shutdown(wait=False, cancel_futures=True)
                self._maybe_finish_shutdown_locked()
                self._state_condition.notify_all()
        while not completion.is_set():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return
            with self._state_condition:
                self._maybe_finish_shutdown_locked()
                if completion.is_set():
                    return
                threads = tuple(self._accept_threads)
            for thread in threads:
                thread.join(min(0.01, max(0.0, deadline - time.monotonic())))
            with self._state_condition:
                self._maybe_finish_shutdown_locked()
                if not completion.is_set():
                    self._state_condition.wait(
                        min(0.01, max(0.0, deadline - time.monotonic()))
                    )

    def serve_forever(self, *, shutdown_event: threading.Event | None = None) -> None:
        self.start()
        event = shutdown_event or self._stop_event
        try:
            while not event.wait(0.2):
                if self._stop_event.is_set():
                    break
        finally:
            self.shutdown()


def create_service_from_activation(
    store_path: str | Path,
    activation_contract: ActivationContract,
    identity_contract: ServiceIdentityContract,
    *,
    environment: dict[str, str] | None = None,
) -> OASService:
    descriptors = intake_activated_descriptors(
        activation_contract, environment=environment
    )
    try:
        return OASService(store_path, descriptors, identity_contract)
    except Exception:
        descriptors.close()
        raise


def run_service(
    store_path: str | Path,
    activated_descriptors: ActivatedDescriptors,
    identity_contract: ServiceIdentityContract,
    *,
    shutdown_event: threading.Event | None = None,
    shutdown_timeout: float = SHUTDOWN_TIMEOUT_SECONDS,
) -> None:
    """Explicit service entry boundary; it never performs host installation."""

    service = OASService(store_path, activated_descriptors, identity_contract)
    service.start()
    event = shutdown_event or service._stop_event
    try:
        while not event.wait(0.2):
            if service._stop_event.is_set():
                break
    finally:
        service.shutdown(timeout=shutdown_timeout)
