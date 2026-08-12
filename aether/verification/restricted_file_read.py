"""Deterministic verification statuses for governed restricted reads."""


STATUSES = (
    "VERIFIED_SUCCESS", "VERIFIED_PARTIAL", "DENIED", "NOT_FOUND",
    "CHANGED_DURING_READ", "INTERNAL_ERROR",
)


def verify_restricted_file_read(
    *, authorized: bool, reader_result: dict | None, observation: object | None,
) -> str:
    required = {"status", "truncated", "privacy_filtered", "read_started"}
    if not isinstance(reader_result, dict) or not required.issubset(reader_result) or not hasattr(observation, "reader_status"):
        return "INTERNAL_ERROR"
    if not authorized:
        return "DENIED"
    if reader_result.get("status") == "blocked":
        return "DENIED"
    if reader_result.get("status") == "not_found":
        return "NOT_FOUND"
    if reader_result.get("status") == "changed" or reader_result.get("changed_during_read"):
        return "CHANGED_DURING_READ"
    if reader_result.get("status") == "error":
        return "INTERNAL_ERROR"
    if reader_result.get("status") != "success":
        return "INTERNAL_ERROR"
    return "VERIFIED_PARTIAL" if reader_result.get("truncated") else "VERIFIED_SUCCESS"
