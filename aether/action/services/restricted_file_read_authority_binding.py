"""Capability-specific binding for one authorized restricted-read attempt."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Mapping, NoReturn

from aether.action.approval_queue import restricted_read_fingerprint
from aether.core.governance import (
    RestrictedReadAuthorizationDecision,
    RestrictedReadScope,
)


CAPABILITY_ID = "file.restricted_read"
PERMISSION_CLASS = "read_only"


class RestrictedReadAuthorityBindingError(ValueError):
    """Raised when existing restricted-read authority evidence cannot bind."""


@dataclass(frozen=True, slots=True)
class RestrictedReadAuthorityBinding:
    """Immutable facts binding one existing authorized read scope to its attempt."""

    capability_id: Literal["file.restricted_read"]
    execution_attempt_id: str
    session_id: str | None
    approval_id: str
    approval_fingerprint: str
    normalized_target: str
    permission_class: Literal["read_only"]
    max_chars: int
    scope: RestrictedReadScope


def _reject(reason: str) -> NoReturn:
    raise RestrictedReadAuthorityBindingError(reason)


def bind_restricted_read_authority(
    *,
    approval_id: str,
    requested_action: Mapping[str, Any],
    session_id: str | None,
    execution_attempt_id: str,
    approval_binding: Mapping[str, Any],
    authorization_decision: RestrictedReadAuthorizationDecision,
) -> RestrictedReadAuthorityBinding:
    """Bind current approval and Governance evidence to one read attempt.

    This function validates existing authority evidence only. It does not make
    a Governance decision, claim approval, dispatch a reader, or verify output.
    """
    if not isinstance(approval_id, str) or not approval_id:
        _reject("Restricted-read approval identity is required.")
    if not isinstance(execution_attempt_id, str) or not execution_attempt_id:
        _reject("Restricted-read execution-attempt identity is required.")
    if not isinstance(requested_action, Mapping):
        _reject("Restricted-read action binding is invalid.")
    if restricted_read_fingerprint(dict(requested_action)) is None:
        _reject("Restricted-read action binding is invalid.")
    if not isinstance(approval_binding, Mapping):
        _reject("Restricted-read approval binding is invalid.")
    if approval_binding.get("approval_valid") is not True:
        _reject("Restricted-read approval binding is invalid or stale.")
    if approval_binding.get("decision") != "allow_restricted_read":
        _reject("Restricted-read approval decision is invalid.")
    if approval_binding.get("approval_id") != approval_id:
        _reject("Restricted-read approval identity does not match.")

    record = approval_binding.get("approval_record")
    if not isinstance(record, Mapping):
        _reject("Restricted-read approval record is unavailable.")
    if record.get("approval_id") != approval_id or record.get("status") != "approved":
        _reject("Restricted-read approval record is invalid or stale.")
    if record.get("execution_consumed") is True or record.get(
        "consumed_by_execution_attempt"
    ) is not None:
        _reject("Restricted-read approval record was already consumed.")

    approval_request = record.get("approval_request")
    if not isinstance(approval_request, Mapping) or approval_request.get(
        "requested_action"
    ) != dict(requested_action):
        _reject("Restricted-read approval action does not match.")
    expected_fingerprint = restricted_read_fingerprint(dict(requested_action))
    if record.get("requested_action_fingerprint") != expected_fingerprint:
        _reject("Restricted-read approval fingerprint is invalid.")

    metadata = record.get("metadata")
    if not isinstance(metadata, Mapping):
        _reject("Restricted-read approval context is invalid.")
    stored_session = metadata.get("session_id")
    if stored_session is not None and stored_session != session_id:
        _reject("Restricted-read session binding does not match.")

    if not isinstance(authorization_decision, RestrictedReadAuthorizationDecision):
        _reject("Restricted-read authorization decision is invalid.")
    if authorization_decision.authorization_granted is not True:
        _reject("Restricted-read authorization was not granted.")
    scope = authorization_decision.scope
    if not isinstance(scope, RestrictedReadScope):
        _reject("Restricted-read authorization scope is unavailable.")

    parameters = requested_action.get("parameters")
    target = requested_action.get("target")
    if (
        requested_action.get("tool_id") != CAPABILITY_ID
        or requested_action.get("permission_class") != PERMISSION_CLASS
        or not isinstance(target, str)
        or not isinstance(parameters, Mapping)
        or set(parameters) != {"max_chars"}
        or not isinstance(parameters.get("max_chars"), int)
        or isinstance(parameters.get("max_chars"), bool)
    ):
        _reject("Restricted-read action fields are invalid.")
    max_chars = parameters["max_chars"]
    if not 0 <= max_chars <= 12000:
        _reject("Restricted-read max_chars binding is invalid.")

    if (
        scope.capability_id != CAPABILITY_ID
        or scope.permission_class != PERMISSION_CLASS
        or scope.normalized_target != target
        or scope.max_chars != max_chars
        or scope.execution_attempt_id != execution_attempt_id
        or scope.session_id != session_id
    ):
        _reject("Restricted-read authorization scope does not match the attempt.")

    return RestrictedReadAuthorityBinding(
        capability_id=CAPABILITY_ID,
        execution_attempt_id=execution_attempt_id,
        session_id=session_id,
        approval_id=approval_id,
        approval_fingerprint=expected_fingerprint,
        normalized_target=target,
        permission_class=PERMISSION_CLASS,
        max_chars=max_chars,
        scope=scope,
    )
