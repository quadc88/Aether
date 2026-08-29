"""Canonical, bounded IPC protocol for the M120A OAS service foundation."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re
from types import MappingProxyType
from typing import Any, Mapping


PROTOCOL_VERSION = 1
REQUEST_DIGEST_DOMAIN = "aether.oas.ipc.request-payload"
REQUEST_DIGEST_VERSION = 1
MAX_REQUEST_FRAME_BYTES = 16 * 1024
MAX_RESPONSE_FRAME_BYTES = 4 * 1024
MAX_JSON_DEPTH = 16
MAX_JSON_COLLECTION_ITEMS = 128
MAX_JSON_KEY_BYTES = 128
MAX_JSON_STRING_BYTES = 4096
MAX_JSON_INTEGER_DIGITS = 128

ENDPOINT_RUNTIME = "runtime"
ENDPOINT_BOOTSTRAP = "bootstrap"
ENDPOINT_BROKER = "broker"
ENDPOINT_ROLES = (ENDPOINT_RUNTIME, ENDPOINT_BOOTSTRAP, ENDPOINT_BROKER)

RUNTIME_OPERATIONS = ("PING", "GET_BOUNDED_RUNTIME_STATUS")
BOOTSTRAP_OPERATIONS = (
    "BEGIN_LOCAL_BOOTSTRAP_WINDOW",
    "CANCEL_LOCAL_BOOTSTRAP_WINDOW",
)
BROKER_OPERATIONS = (
    "ISSUE_LOCAL_BOOTSTRAP_CHALLENGE",
    "REGISTER_LOCAL_BOOTSTRAP_AUTHORIZATION",
    "REVOKE_LOCAL_BOOTSTRAP_AUTHORIZATION",
)
OPERATIONS_BY_ENDPOINT = MappingProxyType(
    {
        ENDPOINT_RUNTIME: RUNTIME_OPERATIONS,
        ENDPOINT_BOOTSTRAP: BOOTSTRAP_OPERATIONS,
        ENDPOINT_BROKER: BROKER_OPERATIONS,
    }
)

RESULT_CLASSIFICATIONS = frozenset(
    {
        "OK",
        "UNINITIALIZED",
        "NOT_READY",
        "NOT_IMPLEMENTED",
        "INVALID_REQUEST",
        "UNAUTHORIZED_PEER",
        "DEADLINE_EXCEEDED",
        "OVERLOADED",
        "UNAVAILABLE",
        "PROTOCOL_ERROR",
        "INTERNAL_ERROR",
    }
)
ERROR_CLASSIFICATIONS = frozenset(
    {
        "INVALID_REQUEST",
        "UNAUTHORIZED_PEER",
        "DEADLINE_EXCEEDED",
        "OVERLOADED",
        "UNAVAILABLE",
        "PROTOCOL_ERROR",
        "INTERNAL_ERROR",
    }
)

_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
_CLASS = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,63}$")
_SECRET_FIELD_WORDS = (
    "secret",
    "password",
    "credential",
    "token",
    "assertion",
    "session",
    "signing",
    "private_key",
    "recovery",
    "path",
    "sql",
    "traceback",
    "exception",
    "database",
    "audit",
)

REQUEST_FIELDS = frozenset(
    {
        "protocol_version",
        "endpoint_role",
        "request_id",
        "operation",
        "caller_class",
        "deadline_monotonic",
        "payload",
        "payload_digest",
    }
)
RESPONSE_FIELDS = frozenset(
    {"protocol_version", "request_id", "result_classification", "result", "error"}
)


class ProtocolError(ValueError):
    """Raised when a frame violates the bounded protocol contract."""


class RequestDeadlineExceeded(ProtocolError):
    """Raised when an absolute request deadline has elapsed."""


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ProtocolError("duplicate JSON field")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ProtocolError(f"non-finite JSON value: {value}")


def _validate_json(value: Any, *, reject_secret_fields: bool, depth: int = 0) -> None:
    if isinstance(value, Mapping):
        if depth >= MAX_JSON_DEPTH:
            raise ProtocolError("JSON maximum depth exceeded")
        if len(value) > MAX_JSON_COLLECTION_ITEMS:
            raise ProtocolError("JSON maximum collection size exceeded")
        for key, child in value.items():
            if not isinstance(key, str):
                raise ProtocolError("JSON object keys must be strings")
            if len(key.encode("utf-8")) > MAX_JSON_KEY_BYTES:
                raise ProtocolError("JSON key exceeds maximum size")
            if reject_secret_fields:
                folded = key.casefold()
                if any(word in folded for word in _SECRET_FIELD_WORDS):
                    raise ProtocolError("secret-bearing field is not allowed")
            _validate_json(child, reject_secret_fields=reject_secret_fields, depth=depth + 1)
        return
    if isinstance(value, (list, tuple)):
        if depth >= MAX_JSON_DEPTH:
            raise ProtocolError("JSON maximum depth exceeded")
        if len(value) > MAX_JSON_COLLECTION_ITEMS:
            raise ProtocolError("JSON maximum collection size exceeded")
        for child in value:
            _validate_json(child, reject_secret_fields=reject_secret_fields, depth=depth + 1)
        return
    if isinstance(value, str):
        if len(value.encode("utf-8")) > MAX_JSON_STRING_BYTES:
            raise ProtocolError("JSON string exceeds maximum size")
        return
    if value is None or isinstance(value, bool):
        return
    if isinstance(value, int):
        if len(str(abs(value))) > MAX_JSON_INTEGER_DIGITS:
            raise ProtocolError("JSON integer exceeds maximum size")
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ProtocolError("non-finite numbers are not allowed")
        return
    raise ProtocolError("unsupported JSON value")


def canonical_json(value: Any, *, reject_secret_fields: bool = True) -> str:
    """Serialize bounded JSON deterministically with no implicit authority fields."""

    _validate_json(value, reject_secret_fields=reject_secret_fields)
    try:
        encoded = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
    except (TypeError, ValueError, OverflowError) as exc:
        raise ProtocolError("value is not canonical JSON") from exc
    if len(encoded.encode("utf-8")) > MAX_REQUEST_FRAME_BYTES:
        raise ProtocolError("JSON encoded size exceeds request limit")
    return encoded


def canonical_payload_digest(
    *, endpoint_role: str, operation: str, payload: Mapping[str, Any]
) -> str:
    """Return the versioned digest for the exact endpoint payload contract."""

    if endpoint_role not in ENDPOINT_ROLES:
        raise ProtocolError("unknown endpoint role")
    if operation not in OPERATIONS_BY_ENDPOINT[endpoint_role]:
        raise ProtocolError("operation is not valid for endpoint")
    if not isinstance(payload, Mapping):
        raise ProtocolError("payload must be an object")
    material = {
        "domain": REQUEST_DIGEST_DOMAIN,
        "digest_contract_version": REQUEST_DIGEST_VERSION,
        "endpoint_role": endpoint_role,
        "operation": operation,
        "payload": dict(payload),
    }
    encoded = canonical_json(material).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _validate_request_values(values: Mapping[str, Any]) -> None:
    if set(values) != REQUEST_FIELDS:
        raise ProtocolError("request fields are not exact")
    if values["protocol_version"] != PROTOCOL_VERSION:
        raise ProtocolError("unsupported protocol version")
    endpoint_role = values["endpoint_role"]
    if endpoint_role not in ENDPOINT_ROLES:
        raise ProtocolError("unknown endpoint role")
    request_id = values["request_id"]
    if not isinstance(request_id, str) or not _IDENTITY.fullmatch(request_id):
        raise ProtocolError("request identity is invalid")
    operation = values["operation"]
    if not isinstance(operation, str) or operation not in OPERATIONS_BY_ENDPOINT[endpoint_role]:
        raise ProtocolError("operation is not valid for endpoint")
    caller_class = values["caller_class"]
    if not isinstance(caller_class, str) or not _CLASS.fullmatch(caller_class):
        raise ProtocolError("caller class is invalid")
    deadline = values["deadline_monotonic"]
    if isinstance(deadline, bool) or not isinstance(deadline, (int, float)):
        raise ProtocolError("deadline must be a finite number")
    if not math.isfinite(float(deadline)) or deadline <= 0:
        raise ProtocolError("deadline must be a positive finite number")
    payload = values["payload"]
    if not isinstance(payload, Mapping):
        raise ProtocolError("payload must be an object")
    digest = values["payload_digest"]
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise ProtocolError("payload digest is invalid")
    if canonical_payload_digest(
        endpoint_role=endpoint_role, operation=operation, payload=payload
    ) != digest:
        raise ProtocolError("payload digest does not match canonical payload")


@dataclass(frozen=True, slots=True)
class Request:
    protocol_version: int
    endpoint_role: str
    request_id: str
    operation: str
    caller_class: str
    deadline_monotonic: int | float
    payload: Mapping[str, Any]
    payload_digest: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "protocol_version": self.protocol_version,
            "endpoint_role": self.endpoint_role,
            "request_id": self.request_id,
            "operation": self.operation,
            "caller_class": self.caller_class,
            "deadline_monotonic": self.deadline_monotonic,
            "payload": dict(self.payload),
            "payload_digest": self.payload_digest,
        }

    def encode(self) -> bytes:
        values = self.to_dict()
        _validate_request_values(values)
        encoded = canonical_json(values).encode("utf-8")
        if len(encoded) > MAX_REQUEST_FRAME_BYTES:
            raise ProtocolError("request frame exceeds maximum size")
        return encoded


def build_request(
    *,
    endpoint_role: str,
    request_id: str,
    operation: str,
    caller_class: str,
    deadline_monotonic: int | float,
    payload: Mapping[str, Any],
) -> Request:
    return Request(
        protocol_version=PROTOCOL_VERSION,
        endpoint_role=endpoint_role,
        request_id=request_id,
        operation=operation,
        caller_class=caller_class,
        deadline_monotonic=deadline_monotonic,
        payload=dict(payload),
        payload_digest=canonical_payload_digest(
            endpoint_role=endpoint_role, operation=operation, payload=payload
        ),
    )


def decode_request(frame: bytes | bytearray | memoryview) -> Request:
    if not isinstance(frame, (bytes, bytearray, memoryview)):
        raise ProtocolError("request frame must be bytes")
    raw = bytes(frame)
    if not raw or len(raw) > MAX_REQUEST_FRAME_BYTES:
        raise ProtocolError("request frame size is invalid")
    try:
        text = raw.decode("utf-8")
        values = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_pairs,
            parse_constant=_reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProtocolError("request frame is not valid JSON") from exc
    if not isinstance(values, dict):
        raise ProtocolError("request frame must be an object")
    _validate_request_values(values)
    if canonical_json(values).encode("utf-8") != raw:
        raise ProtocolError("request frame is not canonical")
    return Request(
        protocol_version=values["protocol_version"],
        endpoint_role=values["endpoint_role"],
        request_id=values["request_id"],
        operation=values["operation"],
        caller_class=values["caller_class"],
        deadline_monotonic=values["deadline_monotonic"],
        payload=MappingProxyType(dict(values["payload"])),
        payload_digest=values["payload_digest"],
    )


def ensure_not_expired(request: Request, *, now: float) -> None:
    if not math.isfinite(now) or now >= float(request.deadline_monotonic):
        raise RequestDeadlineExceeded("request deadline expired")


@dataclass(frozen=True, slots=True)
class Response:
    protocol_version: int
    request_id: str
    result_classification: str
    result: Mapping[str, Any]
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        values: dict[str, Any] = {
            "protocol_version": self.protocol_version,
            "request_id": self.request_id,
            "result_classification": self.result_classification,
            "result": dict(self.result),
        }
        if self.error is not None:
            values["error"] = self.error
        return values

    def encode(self) -> bytes:
        if self.protocol_version != PROTOCOL_VERSION:
            raise ProtocolError("unsupported response protocol version")
        if not isinstance(self.request_id, str) or not _IDENTITY.fullmatch(self.request_id):
            raise ProtocolError("response request identity is invalid")
        if self.result_classification not in RESULT_CLASSIFICATIONS:
            raise ProtocolError("response classification is invalid")
        if not isinstance(self.result, Mapping):
            raise ProtocolError("response result must be an object")
        if self.error is not None and self.error not in ERROR_CLASSIFICATIONS:
            raise ProtocolError("response error is invalid")
        values = self.to_dict()
        encoded = canonical_json(values).encode("utf-8")
        if len(encoded) > MAX_RESPONSE_FRAME_BYTES:
            raise ProtocolError("response frame exceeds maximum size")
        return encoded


def make_response(
    *, request_id: str, classification: str, result: Mapping[str, Any]
) -> Response:
    return Response(
        protocol_version=PROTOCOL_VERSION,
        request_id=request_id,
        result_classification=classification,
        result=dict(result),
    )


def make_error_response(
    *, request_id: str = "rejected", classification: str = "PROTOCOL_ERROR"
) -> Response:
    if classification not in ERROR_CLASSIFICATIONS:
        classification = "PROTOCOL_ERROR"
    return Response(
        protocol_version=PROTOCOL_VERSION,
        request_id=request_id,
        result_classification=classification,
        result={"status": "REJECTED"},
        error=classification,
    )


def decode_response(frame: bytes | bytearray | memoryview) -> Response:
    raw = bytes(frame)
    if not raw or len(raw) > MAX_RESPONSE_FRAME_BYTES:
        raise ProtocolError("response frame size is invalid")
    try:
        values = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_reject_duplicate_pairs,
            parse_constant=_reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProtocolError("response frame is not valid JSON") from exc
    if not isinstance(values, dict) or not set(values) <= RESPONSE_FIELDS:
        raise ProtocolError("response fields are invalid")
    required = {"protocol_version", "request_id", "result_classification", "result"}
    if set(values) - {"error"} != required:
        raise ProtocolError("response fields are incomplete")
    response = Response(
        protocol_version=values["protocol_version"],
        request_id=values["request_id"],
        result_classification=values["result_classification"],
        result=values["result"],
        error=values.get("error"),
    )
    _ = response.encode()
    if _ != raw:
        raise ProtocolError("response frame is not canonical")
    return response
