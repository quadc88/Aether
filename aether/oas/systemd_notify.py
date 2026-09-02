"""Small native systemd notification client with no subprocess fallback."""

from __future__ import annotations

import os
import socket
import time
from typing import Mapping


class NotificationError(ValueError):
    """Raised when the native notification protocol cannot be used safely."""


MAX_NOTIFY_SOCKET_BYTES = 107
NOTIFY_SEND_TIMEOUT_SECONDS = 0.2


def _address(value: str) -> str:
    if not isinstance(value, str) or not value or "\x00" in value:
        raise NotificationError("NOTIFY_SOCKET is invalid")
    if value.startswith("@"):
        if not 1 <= len(value[1:].encode("utf-8")) <= MAX_NOTIFY_SOCKET_BYTES:
            raise NotificationError("abstract NOTIFY_SOCKET is too long")
        return "\x00" + value[1:]
    if not value.startswith("/"):
        raise NotificationError("NOTIFY_SOCKET must be absolute or abstract")
    if len(value.encode("utf-8")) > MAX_NOTIFY_SOCKET_BYTES:
        raise NotificationError("NOTIFY_SOCKET path is too long")
    return value


def send_notification(
    message: str,
    *,
    environment: Mapping[str, str] | None = None,
    socket_factory=socket.socket,
    deadline_monotonic: float | None = None,
    clock=time.monotonic,
) -> None:
    """Send one bounded datagram directly to the systemd notify socket."""

    if not isinstance(message, str) or not message:
        raise NotificationError("notification is empty or too large")
    if "\x00" in message:
        raise NotificationError("notification contains NUL")
    try:
        payload = message.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise NotificationError("notification is not valid UTF-8") from exc
    if len(payload) > 4096:
        raise NotificationError("notification is empty or too large")
    if message != "READY=1":
        raise NotificationError("only the exact READY=1 notification is permitted")
    env = os.environ if environment is None else environment
    target = _address(env.get("NOTIFY_SOCKET", ""))
    deadline = clock() + NOTIFY_SEND_TIMEOUT_SECONDS if deadline_monotonic is None else deadline_monotonic
    if not isinstance(deadline, (int, float)) or deadline <= clock():
        raise NotificationError("notification deadline has expired")
    try:
        with socket_factory(socket.AF_UNIX, socket.SOCK_DGRAM) as notifier:
            if notifier.family != socket.AF_UNIX or notifier.type & 0xF != socket.SOCK_DGRAM:
                raise NotificationError("notification socket type is invalid")
            notifier.settimeout(max(0.001, min(NOTIFY_SEND_TIMEOUT_SECONDS, deadline - clock())))
            sent = notifier.sendto(payload, target)
    except NotificationError:
        raise
    except (OSError, socket.timeout) as exc:
        raise NotificationError("systemd notification failed") from exc
    if sent != len(payload):
        raise NotificationError("systemd notification was incomplete")


def notify_ready(*, environment: Mapping[str, str] | None = None) -> None:
    send_notification("READY=1", environment=environment)
