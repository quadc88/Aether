"""Restricted, read-only access to small public Aether project text files."""

from pathlib import Path
import re
import json
import uuid
from typing import Literal

import yaml

from aether.action.tool_registry import get_tool, register_tool
from aether.time.clock import get_timezone, now_iso
from aether.core.config import get_restricted_file_read_approved_roots


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
    "private", "private_key", "id_rsa", "id_ed25519", ".pem", ".key", "key", "keys",
    "token", "tokens", "api_key", "apikey", "cookie", "cookies", "appdata", "windows",
    "system32", "users", "c:/users", "c:\\users",
}
SENSITIVE_NAME_TOKENS = {
    "secret", "secrets", "credential", "credentials", "password", "passwords", "private",
    "private_key", "id_rsa", "id_ed25519", "key", "keys", "token", "tokens", "api_key",
    "apikey", "cookie", "cookies",
}
BASIC_SENSITIVE_DIRECTORY_NAMES = {"appdata", "windows", "system32", "users"}
BROWSER_PROFILE_MARKERS = {"profile", "profiles", "cache", "cookies", "cookie", "userdata", "user data"}
MAX_FILE_SIZE_BYTES = 64 * 1024


def _scan_governed_content_for_secrets(content: str) -> bool:
    if not isinstance(content, str):
        raise TypeError("content must be text")
    assignment = r"\b(?:password|passwd|pwd|secret|secret_key|token|access_token|api_key|api-key|apikey|access_key|credential|credentials)\b[ \t]*[:=][^\r\n]+"
    private_key = r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----|-----END [A-Z0-9 ]*PRIVATE KEY-----"
    return bool(re.search(f"(?:{assignment}|{private_key})", content, re.IGNORECASE))


def _identity_tuple(path: Path, *, follow_symlinks: bool = False) -> tuple[int, int, int, int]:
    stat = path.stat() if follow_symlinks else path.lstat()
    return stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns


def _governed_read(path: str, max_chars: int, metadata: dict | None) -> dict:
    timestamp = now_iso()
    base = {
        "id": f"file_access_{uuid.uuid4().hex}", "created": timestamp,
        "updated": timestamp, "timezone": get_timezone(), "path": path,
        "normalized_path": "", "allowed": False, "status": "blocked",
        "reason": "", "size_bytes": None, "extension": "", "content": None,
        "regular_file": False,
        "truncated": False, "max_chars": max_chars, "metadata": metadata or {},
        "read_started": False, "changed_during_read": False, "privacy_filtered": False,
    }
    if not isinstance(max_chars, int) or not 0 <= max_chars <= 12000:
        base["reason"] = "Read bound is invalid."
        return base
    try:
        requested = Path(path).expanduser()
        resolved = requested.resolve(strict=True)
    except FileNotFoundError:
        base["status"], base["reason"] = "not_found", "File was not found."
        return base
    except OSError:
        base["status"], base["reason"] = "error", "File path could not be resolved safely."
        return base
    base["normalized_path"] = str(resolved)
    base["extension"] = resolved.suffix.lower()
    roots = get_restricted_file_read_approved_roots()
    try:
        contained = any(resolved == root or root in resolved.parents for root in roots)
        if not roots or not contained or is_sensitive_path(resolved) or not resolved.is_file():
            base["reason"] = "Path is not approved for governed reading."
            return base
        base["regular_file"] = True
        if base["extension"] not in ALLOWED_EXTENSIONS and resolved.name.lower() != ".gitignore":
            base["reason"] = "File extension is not allowed."
            return base
        if resolved.stat().st_size > MAX_FILE_SIZE_BYTES:
            base["reason"] = "File is larger than the allowed 64 KB limit."
            return base
        before_lstat = _identity_tuple(requested)
        before_stat = _identity_tuple(resolved, follow_symlinks=True)
        base["read_started"] = True
        content = resolved.read_text(encoding="utf-8", errors="replace")
        after_lstat = _identity_tuple(requested)
        after_stat = _identity_tuple(resolved, follow_symlinks=True)
        after_resolved = requested.resolve(strict=True)
        if str(after_resolved) != str(resolved) or before_lstat != after_lstat or before_stat != after_stat:
            base.update(status="changed", reason="File changed during read.", changed_during_read=True)
            return base
        bounded = content[:max_chars]
        base["size_bytes"] = len(content.encode("utf-8"))
        base["truncated"] = len(content) > max_chars
        try:
            privacy_hit = _scan_governed_content_for_secrets(bounded)
        except Exception:
            base.update(status="error", reason="Content privacy check failed safely.")
            return base
        base["privacy_filtered"] = True
        if privacy_hit:
            base.update(status="blocked", reason="Content is not eligible for disclosure.")
            return base
        base.update(allowed=True, status="success", content=bounded, reason="")
        return base
    except FileNotFoundError:
        if base["read_started"]:
            base.update(status="error", reason="File could not be classified safely after read.")
        else:
            base.update(status="not_found", reason="File was not found during read.")
        return base
    except OSError:
        base.update(status="error", reason="File could not be read safely.")
        return base


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


def is_sensitive_path(path: Path) -> bool:
    """Block sensitive path components without rejecting harmless source filenames."""
    normalized = str(path).replace("\\", "/").lower()
    parts = [part for part in normalized.split("/") if part]
    path_tokens = {token for part in parts for token in re.split(r"[^a-z0-9]+", part) if token}
    filename = path.name.lower()
    name_tokens = {token for token in re.split(r"[^a-z0-9]+", filename) if token}

    if path_tokens & (BASIC_SENSITIVE_DIRECTORY_NAMES | SENSITIVE_NAME_TOKENS):
        return True
    if filename == ".env" or filename.startswith(".env.") or path.suffix.lower() in {".pem", ".key"}:
        return True
    if name_tokens & SENSITIVE_NAME_TOKENS:
        return True
    return "browser" in path_tokens and bool(path_tokens & BROWSER_PROFILE_MARKERS)


def list_allowed_roots() -> list[str]:
    return [str(root.resolve(strict=False)) for root in ALLOWED_ROOTS]


def is_path_allowed(path: str) -> dict:
    normalized_path = Path(normalize_path(path))
    extension = normalized_path.suffix.lower()

    if is_sensitive_path(normalized_path):
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


def read_restricted_file(path: str, max_chars: int = 12000, metadata: dict | None = None, *, mode: Literal["direct", "governed_chat"] = "direct") -> dict:
    if mode == "governed_chat":
        record = _governed_read(path, max_chars, metadata)
        audit_record = {key: value for key, value in record.items() if key not in {"content", "metadata", "path"}}
        log = load_file_access_log()
        log["accesses"].append(audit_record)
        save_file_access_log(log)
        return record
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
