"""The only Action bridge for a private governed-read scope."""


def dispatch_restricted_read(scope, *, execution_attempt_id: str) -> dict:
    from aether.action.restricted_file_read_observation import observation_from_reader
    from pathlib import Path
    from aether.action.restricted_file_reader import read_restricted_file
    if scope is None or execution_attempt_id != scope.execution_attempt_id:
        return {"status": "error", "reason": "Invalid restricted-read scope."}
    if (
        scope.capability_id != "file.restricted_read"
        or scope.permission_class != "read_only"
        or scope.bound_function is not read_restricted_file
        or not isinstance(scope.normalized_target, str)
        or not isinstance(scope.approved_root, Path)
        or Path(scope.normalized_target) != scope.approved_root
        and scope.approved_root not in Path(scope.normalized_target).parents
        or not isinstance(scope.max_chars, int)
        or not 0 <= scope.max_chars <= 12000
        or not hasattr(scope, "_dispatch_state")
    ):
        return {"status": "error", "reason": "Restricted-read scope binding is invalid."}
    with scope._dispatch_state.lock:
        if scope._dispatch_state.consumed:
            return {"status": "error", "reason": "Restricted-read scope was already consumed."}
        scope._dispatch_state.consumed = True
    result = scope.bound_function(
        scope.normalized_target,
        scope.max_chars,
        {"source": "governed_chat", "execution_attempt_id": execution_attempt_id},
        mode="governed_chat",
    )
    result["observation"] = observation_from_reader(result)
    return result
