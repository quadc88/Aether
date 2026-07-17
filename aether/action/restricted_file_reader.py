"""Restricted, read-only access to small public Aether project text files."""

from pathlib import Path
import json
import uuid

import yaml

from aether.action.tool_registry import get_tool, register_tool
from aether.time.clock import get_timezone, now_iso


ALLOWED_ROOTS = [
    Path("C:/Aether"),
    Path("C:/Aether/docs"),
    Path("C:/Aether/aether"),
    Path("C:/Aether/config"),
    Path("C:/Aether/identity"),
]
ALLOWED_EXTENSIONS = {".py", ".md", ".txt", ".yaml", ".yml", ".json", ".toml", ".ini", ".cfg"}
SENSITIVE_PATTERNS = {
    ".env", "secret", "secrets", "credential", "credentials", "password", "passwords",
    "private_key", "id_rsa", "id_ed25519", ".pem", ".key", "token", "tokens",
    "api_key", "apikey", "cookie", "cookies", "browser", "appdata", "windows",
    "system32", "users", "c:/users", "c:\\users",
}
MAX_FILE_SIZE_BYTES = 64 * 1024


def load_aether_config(path: str = "config/aether.yaml") -> dict:
    config_path = Path(path)
    if not config_path.exists():
        return {}
    with config_path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def get_file_access_dir() -> Path:
    private_dir = load_aether_config().get("paths", {}).get("private_dir", "private")
    return Path(private_dir) / "file_access"


def get_file_access_log_path() -> Path:
    return get_file_access_dir() / "file_access_log.json"


def _new_file_access_log() -> dict:
    timestamp = now_iso()
    return {
        "type": "restricted_file_access_log",
        "version": "0.1.0",
        "created": timestamp,
        "updated": timestamp,
        "timezone": get_timezone(),
        "accesses": [],
    }


def load_file_access_log() -> dict:
    path = get_file_access_log_path()
    if not path.exists():
        return _new_file_access_log()
    try:
        log = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return _new_file_access_log()
    log.setdefault("type", "restricted_file_access_log")
    log.setdefault("version", "0.1.0")
    log.setdefault("created", now_iso())
    log.setdefault("updated", log["created"])
    log.setdefault("timezone", get_timezone())
    log.setdefault("accesses", [])
    return log


def save_file_access_log(log: dict) -> None:
    path = get_file_access_log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    log["updated"] = now_iso()
    log["timezone"] = get_timezone()
    path.write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")


def normalize_path(path: str) -> str:
    return str(Path(path).expanduser().resolve(strict=False))


def list_allowed_roots() -> list[str]:
    return [str(root.resolve(strict=False)) for root in ALLOWED_ROOTS]


def is_path_allowed(path: str) -> dict:
    normalized_path = Path(normalize_path(path))
    normalized_text = str(normalized_path).replace("\\", "/").lower()
    extension = normalized_path.suffix.lower()

    if any(pattern in normalized_text for pattern in SENSITIVE_PATTERNS):
        return {"allowed": False, "reason": "Path appears sensitive and is blocked.", "normalized_path": str(normalized_path), "extension": extension}
    if not any(normalized_path.is_relative_to(root.resolve(strict=False)) for root in ALLOWED_ROOTS):
        return {"allowed": False, "reason": "Path is outside allowed roots.", "normalized_path": str(normalized_path), "extension": extension}
    if not normalized_path.exists():
        return {"allowed": False, "reason": "Path does not exist.", "normalized_path": str(normalized_path), "extension": extension}
    if not normalized_path.is_file():
        return {"allowed": False, "reason": "Path is not a file.", "normalized_path": str(normalized_path), "extension": extension}
    if extension not in ALLOWED_EXTENSIONS and normalized_path.name.lower() != ".gitignore":
        return {"allowed": False, "reason": "File extension is not allowed.", "normalized_path": str(normalized_path), "extension": extension}
    if normalized_path.stat().st_size > MAX_FILE_SIZE_BYTES:
        return {"allowed": False, "reason": "File is larger than the allowed 64 KB limit.", "normalized_path": str(normalized_path), "extension": extension}
    return {"allowed": True, "reason": "", "normalized_path": str(normalized_path), "extension": extension}


def read_restricted_file(path: str, max_chars: int = 12000, metadata: dict | None = None) -> dict:
    check = is_path_allowed(path)
    timestamp = now_iso()
    record = {
        "id": f"file_access_{uuid.uuid4().hex}",
        "created": timestamp,
        "updated": timestamp,
        "timezone": get_timezone(),
        "path": path,
        "normalized_path": check["normalized_path"],
        "allowed": check["allowed"],
        "status": "success" if check["allowed"] else "blocked",
        "reason": check["reason"],
        "size_bytes": None,
        "extension": check["extension"],
        "content": "",
        "truncated": False,
        "max_chars": max(0, max_chars),
        "metadata": metadata or {},
    }
    if check["allowed"]:
        file_path = Path(check["normalized_path"])
        record["size_bytes"] = file_path.stat().st_size
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            record["content"] = content[: record["max_chars"]]
            record["truncated"] = len(content) > record["max_chars"]
        except OSError as error:
            record["allowed"] = False
            record["status"] = "blocked"
            record["reason"] = f"File could not be read safely: {error}"
    log = load_file_access_log()
    log["accesses"].append(record)
    save_file_access_log(log)
    return record


def list_file_accesses(limit: int = 50) -> list[dict]:
    accesses = list(load_file_access_log()["accesses"])
    accesses.sort(key=lambda access: access.get("created", ""), reverse=True)
    return accesses[: max(0, limit)]


def get_file_access(access_id: str) -> dict | None:
    for access in load_file_access_log()["accesses"]:
        if access.get("id") == access_id:
            return access
    return None


def file_access_status() -> dict:
    log = load_file_access_log()
    return {
        "file_access_log_path": str(get_file_access_log_path()),
        "access_count": len(log["accesses"]),
        "allowed_roots": list_allowed_roots(),
        "created": log.get("created"),
        "updated": log.get("updated"),
        "timezone": log.get("timezone"),
    }


def seed_restricted_file_tool() -> dict:
    existing = get_tool("file.restricted_read")
    tool = register_tool(
        tool_id="file.restricted_read",
        name="Restricted File Read",
        description="Read small text files only from approved Aether project paths.",
        category="file",
        risk_level="medium",
        enabled=True,
        requires_verification=True,
        requires_user_approval=False,
        allow_auto_execute=False,
    )
    return {"tool": tool, "created": existing is None}
