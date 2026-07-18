"""Private, JSON-backed Tool Registry for Aether."""

from pathlib import Path
import json

import yaml

from aether.time.clock import get_timezone, now_iso


VALID_RISK_LEVELS = {"low", "medium", "high"}


def load_aether_config(path: str = "config/aether.yaml") -> dict:
    config_path = Path(path)
    if not config_path.exists():
        return {}
    with config_path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def get_tool_registry_dir() -> Path:
    private_dir = load_aether_config().get("paths", {}).get("private_dir", "private")
    return Path(private_dir) / "tool_registry"


def get_tool_registry_path() -> Path:
    return get_tool_registry_dir() / "tools.json"


def _new_registry() -> dict:
    timestamp = now_iso()
    return {
        "type": "tool_registry",
        "version": "0.1.0",
        "created": timestamp,
        "updated": timestamp,
        "timezone": get_timezone(),
        "tools": {},
    }


def load_registry() -> dict:
    registry_path = get_tool_registry_path()
    if not registry_path.exists():
        return _new_registry()
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return _new_registry()
    registry.setdefault("type", "tool_registry")
    registry.setdefault("version", "0.1.0")
    registry.setdefault("created", now_iso())
    registry.setdefault("updated", registry["created"])
    registry.setdefault("timezone", get_timezone())
    registry.setdefault("tools", {})
    return registry


def save_registry(registry: dict) -> None:
    registry_path = get_tool_registry_path()
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry["updated"] = now_iso()
    registry["timezone"] = get_timezone()
    registry_path.write_text(json.dumps(registry, indent=2, ensure_ascii=False), encoding="utf-8")


def _normalise_policy(
    risk_level: str,
    requires_user_approval: bool,
    allow_auto_execute: bool,
) -> tuple[str, bool, bool]:
    risk_level = risk_level.lower() if risk_level.lower() in VALID_RISK_LEVELS else "medium"
    if risk_level == "high":
        requires_user_approval = True
        allow_auto_execute = False
    if requires_user_approval:
        allow_auto_execute = False
    return risk_level, requires_user_approval, allow_auto_execute


def register_tool(
    tool_id: str,
    name: str,
    description: str,
    category: str,
    risk_level: str = "medium",
    enabled: bool = True,
    requires_verification: bool = True,
    requires_user_approval: bool = False,
    allow_auto_execute: bool = False,
    input_schema: dict | None = None,
    output_schema: dict | None = None,
    metadata: dict | None = None,
) -> dict:
    tool_id = tool_id.strip().lower()
    risk_level, requires_user_approval, allow_auto_execute = _normalise_policy(
        risk_level, requires_user_approval, allow_auto_execute
    )
    registry = load_registry()
    timestamp = now_iso()
    existing = registry["tools"].get(tool_id)
    tool = {
        "id": tool_id,
        "name": name,
        "description": description,
        "category": category,
        "risk_level": risk_level,
        "enabled": enabled,
        "requires_verification": requires_verification,
        "requires_user_approval": requires_user_approval,
        "allow_auto_execute": allow_auto_execute,
        "input_schema": input_schema or {},
        "output_schema": output_schema or {},
        "created": existing.get("created", timestamp) if existing else timestamp,
        "updated": timestamp,
        "timezone": get_timezone(),
        "metadata": metadata or {},
    }
    registry["tools"][tool_id] = tool
    save_registry(registry)
    return tool


def get_tool(tool_id: str) -> dict | None:
    return load_registry()["tools"].get(tool_id.strip().lower())


def list_tools(category: str | None = None, enabled: bool | None = None, limit: int = 100) -> list[dict]:
    tools = list(load_registry()["tools"].values())
    if category is not None:
        tools = [tool for tool in tools if tool.get("category") == category]
    if enabled is not None:
        tools = [tool for tool in tools if tool.get("enabled") is enabled]
    tools.sort(key=lambda tool: tool.get("id", ""))
    return tools[: max(0, limit)]


def search_tools(query: str, limit: int = 20) -> list[dict]:
    query = query.lower().strip()
    if not query:
        return []
    results = []
    for tool in list_tools(limit=10000):
        searchable = " ".join(
            [
                tool.get("id", ""), tool.get("name", ""), tool.get("description", ""),
                tool.get("category", ""), tool.get("risk_level", ""),
                json.dumps(tool.get("metadata", {}), ensure_ascii=False),
            ]
        ).lower()
        if query in searchable:
            results.append(tool)
    return results[: max(0, limit)]


def _change_enabled(tool_id: str, enabled: bool) -> dict | None:
    registry = load_registry()
    tool = registry["tools"].get(tool_id.strip().lower())
    if tool is None:
        return None
    tool["enabled"] = enabled
    tool["updated"] = now_iso()
    save_registry(registry)
    return tool


def enable_tool(tool_id: str) -> dict | None:
    return _change_enabled(tool_id, True)


def disable_tool(tool_id: str) -> dict | None:
    return _change_enabled(tool_id, False)


def update_tool_policy(
    tool_id: str,
    risk_level: str | None = None,
    requires_verification: bool | None = None,
    requires_user_approval: bool | None = None,
    allow_auto_execute: bool | None = None,
) -> dict | None:
    registry = load_registry()
    tool = registry["tools"].get(tool_id.strip().lower())
    if tool is None:
        return None
    risk_level, requires_user_approval, allow_auto_execute = _normalise_policy(
        risk_level if risk_level is not None else tool["risk_level"],
        requires_user_approval if requires_user_approval is not None else tool["requires_user_approval"],
        allow_auto_execute if allow_auto_execute is not None else tool["allow_auto_execute"],
    )
    tool["risk_level"] = risk_level
    tool["requires_user_approval"] = requires_user_approval
    tool["allow_auto_execute"] = allow_auto_execute
    if requires_verification is not None:
        tool["requires_verification"] = requires_verification
    tool["updated"] = now_iso()
    save_registry(registry)
    return tool


def tool_registry_status() -> dict:
    registry = load_registry()
    tools = registry["tools"]
    return {
        "tool_registry_path": str(get_tool_registry_path()),
        "tool_count": len(tools),
        "enabled_count": sum(1 for tool in tools.values() if tool.get("enabled")),
        "disabled_count": sum(1 for tool in tools.values() if not tool.get("enabled")),
        "created": registry.get("created"),
        "updated": registry.get("updated"),
        "timezone": registry.get("timezone"),
    }


DEFAULT_TOOLS = [
    ("project.self_modification.create", "Create Self-Modification Session", "Create a guarded self-modification session.", "project", "medium", True, False, False),
    ("project.self_modification.review", "Review Self-Modification Session", "Record a session review.", "project", "medium", True, False, False),
    ("project.self_modification.dry_run", "Dry Run Self-Modification", "Dry-run an approved session.", "project", "medium", True, False, False),
    ("project.self_modification.apply", "Apply Self-Modification", "Apply an approved session.", "project", "high", True, True, False),
    ("project.self_modification.rollback", "Rollback Self-Modification", "Rollback an applied session.", "project", "high", True, True, False),
    ("project.self_modification.summary", "Summarize Self-Modification", "Summarize a self-modification session.", "project", "low", False, False, True),
    ("project.mutation_log.record", "Record Project Mutation", "Record a private project mutation.", "project", "medium", True, False, False),
    ("project.mutation_log.summary", "Summarize Project Mutations", "Summarize private project mutation history.", "project", "low", False, False, True),
    ("file.read", "Read File", "Read a local file from an approved path.", "file", "medium", True, False, False),
    ("file.write", "Write File", "Write content to a local file.", "file", "medium", True, True, False),
    ("file.delete", "Delete File", "Delete files from an approved path.", "file", "high", True, True, False),
    ("shell.run", "Run Shell Command", "Run a shell command.", "system", "high", True, True, False),
    ("email.draft", "Draft Email", "Create an email draft.", "communication", "medium", True, False, False),
    ("email.send", "Send Email", "Send an email to recipients.", "communication", "high", True, True, False),
    ("memory.write", "Write Memory", "Write a durable memory record.", "memory", "medium", True, False, False),
    ("memory.clear", "Clear Memory", "Clear durable memory records.", "memory", "high", True, True, False),
    ("web.search", "Search Web", "Search public web information.", "web", "low", False, False, True),
    ("graph.add_relationship", "Add Graph Relationship", "Add a Graph Memory relationship.", "memory", "medium", True, False, False),
    ("approval.create", "Create Approval", "Create an action approval item.", "action", "medium", True, False, True),
    ("approval.approve", "Approve Action", "Approve a pending action item.", "action", "high", True, True, False),
]


def seed_default_tools() -> dict:
    tools = []
    created_count = 0
    created_tool_ids = []
    for tool_id, name, description, category, risk_level, requires_verification, requires_user_approval, allow_auto_execute in DEFAULT_TOOLS:
        if get_tool(tool_id) is None:
            created_count += 1
            created_tool_ids.append(tool_id)
        tools.append(
            register_tool(
                tool_id=tool_id,
                name=name,
                description=description,
                category=category,
                risk_level=risk_level,
                requires_verification=requires_verification,
                requires_user_approval=requires_user_approval,
                allow_auto_execute=allow_auto_execute,
            )
        )
    return {"tools": tools, "created_count": created_count, "created_tool_ids": created_tool_ids}
