from pathlib import Path
import json
from aether.time.clock import now_iso, get_timezone


TIMELINE_DIR = Path("timeline")


def ensure_timeline_dir():
    TIMELINE_DIR.mkdir(parents=True, exist_ok=True)


def record_event(
    event_type: str,
    title: str,
    description: str,
    importance: str = "normal",
    related_files: list[str] | None = None,
) -> dict:
    ensure_timeline_dir()

    timestamp = now_iso()
    safe_timestamp = timestamp.replace(":", "-").replace("+", "_")
    event_id = f"event_{safe_timestamp}"

    event = {
        "id": event_id,
        "time": timestamp,
        "timezone": get_timezone(),
        "type": event_type,
        "title": title,
        "description": description,
        "importance": importance,
        "related_files": related_files or [],
    }

    file_path = TIMELINE_DIR / f"{event_id}.json"

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(event, file, indent=2, ensure_ascii=False)

    return event