"""Strict systemd socket-activation descriptor intake for the OAS service."""

from __future__ import annotations

from dataclasses import dataclass
import os
import socket
import stat
import sys
from types import MappingProxyType
from typing import Mapping, MutableMapping


LISTEN_FDS_START = 3
EXPECTED_ENDPOINT_NAMES = ("runtime", "bootstrap", "broker")
_ACTIVATION_ENVIRONMENT_KEYS = ("LISTEN_PID", "LISTEN_FDS", "LISTEN_FDNAMES")


class SocketActivationError(ValueError):
    """Raised when activation descriptors do not match the deployment contract."""


@dataclass(frozen=True, slots=True)
class SocketExpectation:
    endpoint_role: str
    expected_path: str
    expected_uid: int
    expected_gid: int
    expected_mode: int

    def __post_init__(self) -> None:
        if self.endpoint_role not in EXPECTED_ENDPOINT_NAMES:
            raise SocketActivationError("unknown endpoint role")
        if not isinstance(self.expected_path, str) or not self.expected_path.startswith("/"):
            raise SocketActivationError("expected socket path must be absolute")
        if not isinstance(self.expected_uid, int) or self.expected_uid < 0:
            raise SocketActivationError("expected socket uid is invalid")
        if not isinstance(self.expected_gid, int) or self.expected_gid < 0:
            raise SocketActivationError("expected socket gid is invalid")
        if not isinstance(self.expected_mode, int) or self.expected_mode & ~0o777:
            raise SocketActivationError("expected socket mode is invalid")


@dataclass(frozen=True, slots=True)
class ActivationContract:
    expectations: tuple[SocketExpectation, ...]

    def __post_init__(self) -> None:
        roles = tuple(item.endpoint_role for item in self.expectations)
        if roles != EXPECTED_ENDPOINT_NAMES:
            raise SocketActivationError("activation contract roles must be exact and ordered")

    @property
    def by_role(self) -> Mapping[str, SocketExpectation]:
        return MappingProxyType({item.endpoint_role: item for item in self.expectations})


@dataclass(slots=True)
class ActivatedDescriptors:
    sockets: dict[str, socket.socket]

    def __post_init__(self) -> None:
        if tuple(self.sockets) != EXPECTED_ENDPOINT_NAMES:
            raise SocketActivationError("activated descriptor roles are not exact")

    def close(self) -> None:
        for descriptor in tuple(self.sockets.values()):
            try:
                descriptor.close()
            except OSError:
                pass
        self.sockets.clear()

    def __enter__(self) -> "ActivatedDescriptors":
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()


def _activation_value(environment: Mapping[str, str], key: str) -> str:
    value = environment.get(key)
    if not isinstance(value, str) or not value:
        raise SocketActivationError(f"missing {key}")
    return value


def _parse_exact_integer(value: str, key: str) -> int:
    if not value.isdecimal():
        raise SocketActivationError(f"{key} is invalid")
    try:
        return int(value, 10)
    except ValueError as exc:
        raise SocketActivationError(f"{key} is invalid") from exc


def _validate_one_descriptor(
    descriptor_fd: int, expectation: SocketExpectation
) -> socket.socket:
    try:
        duplicate_fd = os.dup(descriptor_fd)
    except OSError as exc:
        raise SocketActivationError("activated descriptor cannot be duplicated") from exc
    descriptor: socket.socket | None = None
    try:
        os.set_inheritable(duplicate_fd, False)
        descriptor = socket.socket(fileno=duplicate_fd)
        duplicate_fd = -1
        if descriptor.family != socket.AF_UNIX:
            raise SocketActivationError("descriptor family is not AF_UNIX")
        if descriptor.type & 0xF != socket.SOCK_SEQPACKET:
            raise SocketActivationError("descriptor type is not SOCK_SEQPACKET")
        if descriptor.getsockopt(socket.SOL_SOCKET, socket.SO_ACCEPTCONN) != 1:
            raise SocketActivationError("descriptor is not listening")
        if descriptor.getsockname() != expectation.expected_path:
            raise SocketActivationError("descriptor path is not exact")

        descriptor_stat = os.fstat(descriptor.fileno())
        if not stat.S_ISSOCK(descriptor_stat.st_mode):
            raise SocketActivationError("descriptor is not a socket inode")
        path_stat = os.lstat(expectation.expected_path)
        if stat.S_ISLNK(path_stat.st_mode) or not stat.S_ISSOCK(path_stat.st_mode):
            raise SocketActivationError("socket path is not a regular socket entry")
        if path_stat.st_uid != expectation.expected_uid:
            raise SocketActivationError("socket owner is incorrect")
        if path_stat.st_gid != expectation.expected_gid:
            raise SocketActivationError("socket group is incorrect")
        if stat.S_IMODE(path_stat.st_mode) != expectation.expected_mode:
            raise SocketActivationError("socket mode is incorrect")
        if not _proc_socket_identity_matches(
            descriptor_stat.st_ino, expectation.expected_path
        ):
            raise SocketActivationError("descriptor inode does not match socket path")
        return descriptor
    except (OSError, SocketActivationError) as exc:
        if descriptor is not None:
            descriptor.close()
        elif duplicate_fd >= 0:
            os.close(duplicate_fd)
        if isinstance(exc, SocketActivationError):
            raise
        raise SocketActivationError("activated descriptor validation failed") from exc


def _proc_socket_identity_matches(inode: int, expected_path: str) -> bool:
    """Match the open socket inode to its kernel-owned pathname on Linux."""

    if not sys.platform.startswith("linux"):
        # The deployment contract is Linux/systemd-specific. Portable pathname
        # checks are not treated as equivalent kernel identity evidence.
        return False
    proc_unix = "/proc/net/unix"
    try:
        with open(proc_unix, "r", encoding="ascii") as source:
            content = source.read(1024 * 1024 + 1)
    except (OSError, UnicodeError, ValueError, TypeError, AttributeError):
        return False
    if not isinstance(content, str) or len(content) > 1024 * 1024:
        return False
    lines = content.splitlines()
    if not lines or lines[0].split() != [
        "Num",
        "RefCount",
        "Protocol",
        "Flags",
        "Type",
        "St",
        "Inode",
        "Path",
    ]:
        return False
    for line in lines[1:]:
        if not line.strip():
            continue
        fields = line.split(maxsplit=7)
        if len(fields) not in (7, 8) or not fields[6].isdecimal():
            return False
        if fields[6] == str(inode):
            return len(fields) == 8 and fields[7] == expected_path
    return False


def _clear_activation_environment(environment: MutableMapping[str, str]) -> None:
    for key in _ACTIVATION_ENVIRONMENT_KEYS:
        environment.pop(key, None)


def intake_activated_descriptors(
    contract: ActivationContract,
    *,
    environment: MutableMapping[str, str] | None = None,
    process_pid: int | None = None,
) -> ActivatedDescriptors:
    """Validate exactly systemd's three descriptors without consuming arbitrary fds."""

    env = os.environ if environment is None else environment
    pid = os.getpid() if process_pid is None else process_pid
    listen_pid = _parse_exact_integer(_activation_value(env, "LISTEN_PID"), "LISTEN_PID")
    listen_fds = _parse_exact_integer(_activation_value(env, "LISTEN_FDS"), "LISTEN_FDS")
    names = tuple(_activation_value(env, "LISTEN_FDNAMES").split(":"))
    if listen_pid != pid:
        raise SocketActivationError("LISTEN_PID is not the current process")
    if listen_fds != len(EXPECTED_ENDPOINT_NAMES):
        raise SocketActivationError("LISTEN_FDS count is not exactly three")
    if names != EXPECTED_ENDPOINT_NAMES:
        raise SocketActivationError("LISTEN_FDNAMES is not exact")

    descriptors: dict[str, socket.socket] = {}
    try:
        for index, endpoint_role in enumerate(EXPECTED_ENDPOINT_NAMES):
            descriptor_fd = LISTEN_FDS_START + index
            descriptors[endpoint_role] = _validate_one_descriptor(
                descriptor_fd, contract.by_role[endpoint_role]
            )
        # Original activation fds are changed only after every duplicate passed.
        for index in range(len(EXPECTED_ENDPOINT_NAMES)):
            os.set_inheritable(LISTEN_FDS_START + index, False)
        if isinstance(env, MutableMapping):
            _clear_activation_environment(env)
        return ActivatedDescriptors(descriptors)
    except Exception:
        for descriptor in descriptors.values():
            descriptor.close()
        raise
