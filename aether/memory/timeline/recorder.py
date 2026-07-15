from pathlib import Path
import json
import yaml

from aether.time.clock import now_iso, get_timezone


def load_aether_config(path: str = "config/aether.yaml") -> dict:
    config_path = Path(path)

    if not config_path.exists():
        return {}

    with config_path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def get_timeline_dir() -> Path:
    config = load_aether_config()
    paths = config.get("paths", {})
    timeline_dir = paths.get("timeline_dir", "timeline")
    return Path(timeline_dir)


def ensure_timeline_dir() -> Path:
    timeline_dir = get_timeline_dir()
    timeline_dir.mkdir(parents=True, exist_ok=True)
    return timeline_dir


def record_event(
    event_type: str,
    title: str,
    description: str,
    importance: str = "normal",
    related_files: list[str] | None = None,
) -> dict:
    timeline_dir = ensure_timeline_dir()

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

    file_path = timeline_dir / f"{event_id}.json"

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(event, file, indent=2, ensure_ascii=False)

    return event

def list_events(limit: int = 20) -> list[dict]:
    timeline_dir = ensure_timeline_dir()

    files = sorted(
        timeline_dir.glob("*.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    events = []

    for file_path in files[:limit]:
        try:
            event = json.loads(file_path.read_text(encoding="utf-8"))
            event["file_path"] = str(file_path)
            events.append(event)
        except json.JSONDecodeError:
            events.append(
                {
                    "file_path": str(file_path),
                    "error": "Invalid JSON timeline event.",
                }
            )

    return events


def latest_event() -> dict | None:
    events = list_events(limit=1)

    if not events:
        return None

    return events[0]


def search_events(query: str, limit: int = 20) -> list[dict]:
    query_lower = query.lower().strip()

    if not query_lower:
        return []

    timeline_dir = ensure_timeline_dir()

    files = sorted(
        timeline_dir.glob("*.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    results = []

    for file_path in files:
        try:
            event = json.loads(file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue

        searchable_text = " ".join(
            [
                str(event.get("id", "")),
                str(event.get("type", "")),
                str(event.get("title", "")),
                str(event.get("description", "")),
                str(event.get("importance", "")),
                " ".join(event.get("related_files", [])),
            ]
        ).lower()

        if query_lower in searchable_text:
            event["file_path"] = str(file_path)
            results.append(event)

        if len(results) >= limit:
            break

    return results


def timeline_status() -> dict:
    timeline_dir = ensure_timeline_dir()
    files = list(timeline_dir.glob("*.json"))

    return {
        "timeline_dir": str(timeline_dir),
        "event_count": len(files),
        "latest_event": latest_event(),
    }