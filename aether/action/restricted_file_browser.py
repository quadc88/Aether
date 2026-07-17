"""Restricted metadata-only browser for approved Aether project paths."""

from pathlib import Path
import json
import uuid

import yaml

from aether.action.restricted_file_reader import ALLOWED_EXTENSIONS, ALLOWED_ROOTS, is_sensitive_path, normalize_path
from aether.action.tool_registry import get_tool, register_tool
from aether.time.clock import get_timezone, now_iso


MAX_DEPTH = 6
MAX_ENTRIES = 1000


def load_aether_config(path: str = "config/aether.yaml") -> dict:
    config_path = Path(path)
    if not config_path.exists():
        return {}
    with config_path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def get_file_browser_dir() -> Path:
    private_dir = load_aether_config().get("paths", {}).get("private_dir", "private")
    return Path(private_dir) / "file_browser"


def get_file_browser_log_path() -> Path:
    return get_file_browser_dir() / "file_browser_log.json"


def _new_browser_log() -> dict:
    timestamp = now_iso()
    return {"type": "restricted_file_browser_log", "version": "0.1.0", "created": timestamp, "updated": timestamp, "timezone": get_timezone(), "browses": []}


def load_file_browser_log() -> dict:
    path = get_file_browser_log_path()
    if not path.exists():
        return _new_browser_log()
    try:
        log = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return _new_browser_log()
    log.setdefault("type", "restricted_file_browser_log")
    log.setdefault("version", "0.1.0")
    log.setdefault("created", now_iso())
    log.setdefault("updated", log["created"])
    log.setdefault("timezone", get_timezone())
    log.setdefault("browses", [])
    return log


def save_file_browser_log(log: dict) -> None:
    path = get_file_browser_log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    log["updated"] = now_iso()
    log["timezone"] = get_timezone()
    path.write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")


def list_browser_allowed_roots() -> list[str]:
    return [str(root.resolve(strict=False)) for root in ALLOWED_ROOTS]


def _is_under_allowed_root(path: Path) -> bool:
    return any(path.is_relative_to(root.resolve(strict=False)) for root in ALLOWED_ROOTS)


def is_browse_path_allowed(path: str) -> dict:
    normalized_path = Path(normalize_path(path))
    if is_sensitive_path(normalized_path):
        return {"allowed": False, "reason": "Path appears sensitive and is blocked.", "normalized_path": str(normalized_path)}
    if not _is_under_allowed_root(normalized_path):
        return {"allowed": False, "reason": "Path is outside allowed roots.", "normalized_path": str(normalized_path)}
    if not normalized_path.exists():
        return {"allowed": False, "reason": "Path does not exist.", "normalized_path": str(normalized_path)}
    if not normalized_path.is_dir():
        return {"allowed": False, "reason": "Path is not a directory.", "normalized_path": str(normalized_path)}
    return {"allowed": True, "reason": "", "normalized_path": str(normalized_path)}


def is_entry_visible(path: Path) -> bool:
    resolved_path = path.resolve(strict=False)
    if not _is_under_allowed_root(resolved_path) or is_sensitive_path(resolved_path):
        return False
    if resolved_path.is_dir():
        return True
    return resolved_path.suffix.lower() in ALLOWED_EXTENSIONS or resolved_path.name.lower() == ".gitignore"


def _entry_details(path: Path, root: Path) -> dict:
    relative_path = str(path.relative_to(root)).replace("\\", "/")
    if path.is_dir():
        return {"name": path.name, "path": str(path), "relative_path": relative_path, "type": "directory"}
    return {"name": path.name, "path": str(path), "relative_path": relative_path, "type": "file", "extension": path.suffix.lower(), "size_bytes": path.stat().st_size}


def _record_browse(record: dict) -> dict:
    log = load_file_browser_log()
    log["browses"].append(record)
    save_file_browser_log(log)
    return record


def browse_restricted_path(
    path: str,
    max_depth: int = 3,
    max_entries: int = 200,
    include_files: bool = True,
    include_dirs: bool = True,
    metadata: dict | None = None,
) -> dict:
    check = is_browse_path_allowed(path)
    max_depth = max(0, min(max_depth, MAX_DEPTH))
    max_entries = max(0, min(max_entries, MAX_ENTRIES))
    timestamp = now_iso()
    record = {
        "id": f"file_browse_{uuid.uuid4().hex}", "created": timestamp, "updated": timestamp, "timezone": get_timezone(),
        "path": path, "normalized_path": check["normalized_path"], "allowed": check["allowed"],
        "status": "success" if check["allowed"] else "blocked", "reason": check["reason"],
        "max_depth": max_depth, "max_entries": max_entries, "entry_count": 0, "truncated": False,
        "entries": [], "metadata": metadata or {}, "operation": "browse",
    }
    if not check["allowed"]:
        return _record_browse(record)

    root = Path(check["normalized_path"])
    pending = [(root, 0)]
    while pending and not record["truncated"]:
        current, depth = pending.pop(0)
        if depth >= max_depth:
            continue
        try:
            children = sorted(current.iterdir(), key=lambda child: child.name.lower())
        except OSError:
            continue
        for child in children:
            if not is_entry_visible(child):
                continue
            is_directory = child.is_dir()
            if (is_directory and include_dirs) or (not is_directory and include_files):
                if len(record["entries"]) >= max_entries:
                    record["truncated"] = True
                    break
                record["entries"].append(_entry_details(child, root))
            if is_directory and depth + 1 < max_depth:
                pending.append((child, depth + 1))
    record["entry_count"] = len(record["entries"])
    return _record_browse(record)


def search_restricted_files(query: str, root: str = "C:/Aether", max_results: int = 50, metadata: dict | None = None) -> dict:
    check = is_browse_path_allowed(root)
    max_results = max(0, min(max_results, MAX_ENTRIES))
    timestamp = now_iso()
    record = {
        "id": f"file_browse_{uuid.uuid4().hex}", "created": timestamp, "updated": timestamp, "timezone": get_timezone(),
        "query": query, "root": root, "normalized_root": check["normalized_path"], "allowed": check["allowed"],
        "status": "success" if check["allowed"] else "blocked", "reason": check["reason"], "result_count": 0,
        "truncated": False, "results": [], "metadata": metadata or {}, "operation": "search",
    }
    if not check["allowed"]:
        return _record_browse(record)

    root_path = Path(check["normalized_path"])
    query_lower = query.lower().strip()
    pending = [(root_path, 0)]
    while pending and not record["truncated"]:
        current, depth = pending.pop(0)
        if depth >= MAX_DEPTH:
            continue
        try:
            children = sorted(current.iterdir(), key=lambda child: child.name.lower())
        except OSError:
            continue
        for child in children:
            if not is_entry_visible(child):
                continue
            relative_path = str(child.relative_to(root_path)).replace("\\", "/")
            if query_lower and (query_lower in child.name.lower() or query_lower in relative_path.lower()):
                if len(record["results"]) >= max_results:
                    record["truncated"] = True
                    break
                record["results"].append(_entry_details(child, root_path))
            if child.is_dir() and depth + 1 < MAX_DEPTH:
                pending.append((child, depth + 1))
    record["result_count"] = len(record["results"])
    return _record_browse(record)


def list_file_browses(limit: int = 50) -> list[dict]:
    browses = list(load_file_browser_log()["browses"])
    browses.sort(key=lambda browse: browse.get("created", ""), reverse=True)
    return browses[: max(0, limit)]


def get_file_browse(browse_id: str) -> dict | None:
    for browse in load_file_browser_log()["browses"]:
        if browse.get("id") == browse_id:
            return browse
    return None


def file_browser_status() -> dict:
    log = load_file_browser_log()
    return {"file_browser_log_path": str(get_file_browser_log_path()), "browse_count": len(log["browses"]), "allowed_roots": list_browser_allowed_roots(), "created": log.get("created"), "updated": log.get("updated"), "timezone": log.get("timezone")}


def seed_restricted_browser_tools() -> dict:
    definitions = [
        ("file.restricted_browse", "Restricted File Browse", "List approved project files and directories without reading content."),
        ("file.restricted_search", "Restricted File Search", "Search approved project file names and paths without reading content."),
    ]
    tools = []
    created_count = 0
    for tool_id, name, description in definitions:
        if get_tool(tool_id) is None:
            created_count += 1
        tools.append(register_tool(tool_id, name, description, "file", "medium", True, True, False, False))
    return {"tools": tools, "created_count": created_count}
