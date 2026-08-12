"""Call-local observation for the governed restricted-read capability."""

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class RestrictedReadObservation:
    reader_status: Literal["success", "blocked", "not_found", "changed", "error"]
    normalized_target: str
    regular_file: bool
    extension: str
    size_bytes: int | None
    content: str | None
    truncated: bool
    action_id: str | None
    privacy_filtered: bool


def observation_from_reader(result: dict) -> RestrictedReadObservation:
    return RestrictedReadObservation(
        reader_status=result.get("status", "error"),
        normalized_target=result.get("normalized_path", ""),
        regular_file=result.get("regular_file", result.get("status") in {"success", "blocked", "changed"}),
        extension=result.get("extension", ""),
        size_bytes=result.get("size_bytes"),
        content=result.get("content") if result.get("status") == "success" else None,
        truncated=bool(result.get("truncated", False)),
        action_id=result.get("id"),
        privacy_filtered=bool(result.get("privacy_filtered", False)),
    )
