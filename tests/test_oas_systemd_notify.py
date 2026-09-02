import pytest
import socket

from aether.oas.systemd_notify import NotificationError, notify_ready, send_notification


def test_notification_rejects_relative_socket():
    with pytest.raises(NotificationError):
        notify_ready(environment={"NOTIFY_SOCKET": "relative.sock"})


def test_notification_rejects_overlong_address_and_payload():
    with pytest.raises(NotificationError):
        notify_ready(environment={"NOTIFY_SOCKET": "/" + "x" * 107})
    with pytest.raises(NotificationError):
        send_notification("x" * 4097, environment={"NOTIFY_SOCKET": "/tmp/oas.sock"})


def test_notification_rejects_non_protocol_fields():
    with pytest.raises(NotificationError):
        send_notification("ready", environment={"NOTIFY_SOCKET": "/tmp/oas.sock"})
    with pytest.raises(NotificationError):
        send_notification("READY=1\n", environment={"NOTIFY_SOCKET": "/tmp/oas.sock"})
    with pytest.raises(NotificationError):
        send_notification("READY=1\nSTATUS=running", environment={"NOTIFY_SOCKET": "/tmp/oas.sock"})


def test_notification_rejects_expired_deadline_without_opening_socket():
    def forbidden_factory(*_args):
        raise AssertionError("socket must not be opened")

    with pytest.raises(NotificationError):
        send_notification(
            "READY=1",
            environment={"NOTIFY_SOCKET": "@oas"},
            socket_factory=forbidden_factory,
            deadline_monotonic=0,
            clock=lambda: 1,
        )


def test_notification_requires_unix_datagram_socket():
    class WrongSocket:
        family = socket.AF_INET
        type = socket.SOCK_STREAM

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

    with pytest.raises(NotificationError):
        send_notification(
            "READY=1",
            environment={"NOTIFY_SOCKET": "@oas"},
            socket_factory=lambda *_args: WrongSocket(),
        )


def test_notification_sends_exactly_ready_to_abstract_socket():
    sent = []

    class AbstractSocket:
        family = socket.AF_UNIX
        type = socket.SOCK_DGRAM

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def settimeout(self, _timeout):
            return None

        def sendto(self, payload, target):
            sent.append((payload, target))
            return len(payload)

    send_notification("READY=1", environment={"NOTIFY_SOCKET": "@oas"}, socket_factory=lambda *_args: AbstractSocket())
    assert sent == [(b"READY=1", "\x00oas")]


@pytest.mark.parametrize("socket_error", [OSError("unavailable"), socket.timeout()])
def test_notification_rejects_socket_failures(socket_error):
    class FailingSocket:
        family = socket.AF_UNIX
        type = socket.SOCK_DGRAM

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def settimeout(self, _timeout):
            return None

        def sendto(self, *_args):
            raise socket_error

    with pytest.raises(NotificationError):
        send_notification("READY=1", environment={"NOTIFY_SOCKET": "@oas"}, socket_factory=lambda *_args: FailingSocket())


def test_notification_rejects_partial_datagram():
    class ShortSocket:
        family = socket.AF_UNIX
        type = socket.SOCK_DGRAM

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def settimeout(self, _timeout):
            return None

        def sendto(self, payload, _target):
            return len(payload) - 1

    with pytest.raises(NotificationError):
        send_notification("READY=1", environment={"NOTIFY_SOCKET": "@oas"}, socket_factory=lambda *_args: ShortSocket())
