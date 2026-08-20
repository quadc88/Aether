from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from aether.action.approval_queue import restricted_read_fingerprint
from aether.action.services.restricted_file_read_authority_binding import (
    RestrictedReadAuthorityBinding,
    RestrictedReadAuthorityBindingError,
    bind_restricted_read_authority,
)
from aether.core.governance import (
    RestrictedReadAuthorizationDecision,
    RestrictedReadScope,
    _ScopeDispatchState,
)


TARGET = str(Path("/approved/readme.md").resolve())
ATTEMPT_ID = "read_attempt_current"
SESSION_ID = "session-current"
APPROVAL_ID = "approval-current"


def _action(target: str = TARGET, max_chars: int = 12000) -> dict:
    return {
        "tool_id": "file.restricted_read",
        "action_type": "restricted_file_read",
        "name": "Restricted File Read",
        "target": target,
        "permission_class": "read_only",
        "parameters": {"max_chars": max_chars},
    }


def _inputs(**changes):
    action = _action()
    scope = RestrictedReadScope(
        "file.restricted_read",
        lambda *_args, **_kwargs: {"status": "success"},
        TARGET,
        Path("/approved").resolve(),
        "read_only",
        12000,
        ATTEMPT_ID,
        SESSION_ID,
        None,
        _ScopeDispatchState(),
    )
    decision = RestrictedReadAuthorizationDecision(
        {}, "required_satisfied", True, True, scope, "authorized", (),
    )
    record = {
        "approval_id": APPROVAL_ID,
        "status": "approved",
        "approval_request": {"requested_action": action},
        "metadata": {"session_id": SESSION_ID},
        "requested_action_fingerprint": restricted_read_fingerprint(action),
        "execution_consumed": False,
        "consumed_by_execution_attempt": None,
    }
    values = {
        "approval_id": APPROVAL_ID,
        "requested_action": action,
        "session_id": SESSION_ID,
        "execution_attempt_id": ATTEMPT_ID,
        "approval_binding": {
            "approval_valid": True,
            "decision": "allow_restricted_read",
            "approval_id": APPROVAL_ID,
            "approval_record": record,
        },
        "authorization_decision": decision,
    }
    values.update(changes)
    return values


def _bind(**changes) -> RestrictedReadAuthorityBinding:
    return bind_restricted_read_authority(**_inputs(**changes))


def test_success_binds_existing_authority_fields():
    binding = _bind()

    assert binding.capability_id == "file.restricted_read"
    assert binding.permission_class == "read_only"
    assert binding.execution_attempt_id == ATTEMPT_ID
    assert binding.session_id == SESSION_ID
    assert binding.approval_id == APPROVAL_ID
    assert binding.normalized_target == TARGET
    assert binding.max_chars == 12000
    assert binding.scope.execution_attempt_id == ATTEMPT_ID


def test_binding_is_immutable():
    binding = _bind()

    with pytest.raises(FrozenInstanceError):
        binding.capability_id = "generic.action"  # type: ignore[misc]


@pytest.mark.parametrize(
    "changes",
    [
        {"approval_id": ""},
        {"execution_attempt_id": ""},
        {"approval_binding": {}},
        {"authorization_decision": None},
    ],
)
def test_missing_required_binding_fails_closed(changes):
    with pytest.raises(RestrictedReadAuthorityBindingError):
        _bind(**changes)


def test_mismatched_approval_fails_closed():
    values = _inputs()
    values["approval_id"] = "approval-other"

    with pytest.raises(RestrictedReadAuthorityBindingError, match="approval"):
        bind_restricted_read_authority(**values)


def test_mismatched_session_fails_closed():
    with pytest.raises(RestrictedReadAuthorityBindingError, match="session"):
        _bind(session_id="session-other")


def test_mismatched_target_fails_closed():
    values = _inputs()
    values["requested_action"] = _action(target=str(Path("/approved/other.md").resolve()))

    with pytest.raises(RestrictedReadAuthorityBindingError):
        bind_restricted_read_authority(**values)


def test_mismatched_scope_fails_closed():
    values = _inputs()
    values["execution_attempt_id"] = "read_attempt-other"

    with pytest.raises(RestrictedReadAuthorityBindingError, match="scope"):
        bind_restricted_read_authority(**values)


def test_stale_or_unauthorized_decision_fails_closed():
    values = _inputs()
    decision = values["authorization_decision"]
    values["authorization_decision"] = RestrictedReadAuthorizationDecision(
        decision.generic_envelope,
        decision.approval_requirement_state,
        decision.approval_requirement_satisfied,
        False,
        decision.scope,
        "stale",
        decision.warnings,
    )

    with pytest.raises(RestrictedReadAuthorityBindingError, match="authorization"):
        bind_restricted_read_authority(**values)


def test_consumed_approval_fails_closed():
    values = _inputs()
    values["approval_binding"]["approval_record"]["execution_consumed"] = True

    with pytest.raises(RestrictedReadAuthorityBindingError, match="consumed"):
        bind_restricted_read_authority(**values)


def test_scope_attempt_freshness_mismatch_fails_closed():
    values = _inputs()
    scope = values["authorization_decision"].scope
    values["authorization_decision"] = RestrictedReadAuthorizationDecision(
        {}, "required_satisfied", True, True,
        RestrictedReadScope(
            scope.capability_id, scope.bound_function, scope.normalized_target,
            scope.approved_root, scope.permission_class, scope.max_chars,
            "read_attempt-stale", scope.session_id, scope.task_binding,
            scope._dispatch_state,
        ),
        "authorized", (),
    )

    with pytest.raises(RestrictedReadAuthorityBindingError, match="scope"):
        bind_restricted_read_authority(**values)


def test_binding_does_not_claim_or_mint_execution_permission():
    binding = _bind()

    assert not hasattr(binding, "execution_allowed")
    assert not hasattr(binding, "tool_execution_allowed")
    assert binding.approval_id == APPROVAL_ID
    assert values_have_no_generic_identity(binding)


def values_have_no_generic_identity(binding: RestrictedReadAuthorityBinding) -> bool:
    return not any(
        hasattr(binding, field)
        for field in ("generic_action_id", "generic_capability_id", "authorization_granted")
    )


def test_binding_does_not_dispatch_or_verify():
    called = []
    values = _inputs()
    scope = values["authorization_decision"].scope
    values["authorization_decision"] = RestrictedReadAuthorizationDecision(
        {}, "required_satisfied", True, True,
        RestrictedReadScope(
            scope.capability_id,
            lambda *_args, **_kwargs: called.append(True),
            scope.normalized_target,
            scope.approved_root,
            scope.permission_class,
            scope.max_chars,
            scope.execution_attempt_id,
            scope.session_id,
            scope.task_binding,
            scope._dispatch_state,
        ),
        "authorized", (),
    )

    binding = bind_restricted_read_authority(**values)

    assert binding.scope is values["authorization_decision"].scope
    assert called == []
    assert not hasattr(binding, "observation")
    assert not hasattr(binding, "verification_status")
