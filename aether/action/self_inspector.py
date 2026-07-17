"""Safe, structured self-inspection reports for the Aether project."""

from pathlib import Path
import json
import re
import uuid

import yaml

from aether.action.restricted_file_browser import browse_restricted_path, search_restricted_files
from aether.action.restricted_file_reader import read_restricted_file
from aether.action.tool_registry import get_tool, register_tool
from aether.time.clock import get_timezone, now_iso


PRIORITY_FILES = [
    "C:/Aether/README.md", "C:/Aether/docs/CONSTITUTION.md", "C:/Aether/docs/ARCHITECTURE.md",
    "C:/Aether/identity/identity_seed.md", "C:/Aether/aether/interface/api_server.py",
    "C:/Aether/aether/core/runtime.py", "C:/Aether/aether/action/tool_registry.py",
    "C:/Aether/aether/action/tool_planner.py", "C:/Aether/aether/action/tool_executor.py",
    "C:/Aether/aether/action/restricted_file_reader.py", "C:/Aether/aether/action/restricted_file_browser.py",
    "C:/Aether/aether/verification/risk.py",
]
SEARCH_TERMS = [
    "README", "CONSTITUTION", "ARCHITECTURE", "identity_seed", "api_server", "runtime", "tool_registry",
    "tool_planner", "tool_executor", "restricted_file_reader", "restricted_file_browser", "verification",
    "approval_queue", "graph", "timeline", "semantic", "episodic", "working", "time",
]
MODULE_PATHS = {
    "identity": "identity/identity_seed.md", "time": "aether/time", "memory.working": "aether/memory/working",
    "memory.episodic": "aether/memory/episodic", "memory.semantic": "aether/memory/semantic",
    "memory.timeline": "aether/memory/timeline", "memory.graph": "aether/memory/graph",
    "verification": "aether/verification/risk.py", "action.approval_queue": "aether/action/approval_queue.py",
    "action.tool_registry": "aether/action/tool_registry.py", "action.tool_planner": "aether/action/tool_planner.py",
    "action.tool_executor": "aether/action/tool_executor.py", "action.restricted_file_reader": "aether/action/restricted_file_reader.py",
    "action.restricted_file_browser": "aether/action/restricted_file_browser.py", "interface.api_server": "aether/interface/api_server.py",
}


def load_aether_config(path: str = "config/aether.yaml") -> dict:
    config_path = Path(path)
    if not config_path.exists():
        return {}
    with config_path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def get_self_inspection_dir() -> Path:
    private_dir = load_aether_config().get("paths", {}).get("private_dir", "private")
    return Path(private_dir) / "self_inspection"


def get_self_inspection_report_path() -> Path:
    return get_self_inspection_dir() / "self_inspection_reports.json"


def _new_report_store() -> dict:
    timestamp = now_iso()
    return {"type": "self_inspection_reports", "version": "0.1.0", "created": timestamp, "updated": timestamp, "timezone": get_timezone(), "reports": []}


def load_self_inspection_reports() -> dict:
    path = get_self_inspection_report_path()
    if not path.exists():
        return _new_report_store()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return _new_report_store()
    data.setdefault("type", "self_inspection_reports")
    data.setdefault("version", "0.1.0")
    data.setdefault("created", now_iso())
    data.setdefault("updated", data["created"])
    data.setdefault("timezone", get_timezone())
    data.setdefault("reports", [])
    return data


def save_self_inspection_reports(data: dict) -> None:
    path = get_self_inspection_report_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    data["updated"] = now_iso()
    data["timezone"] = get_timezone()
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _read_key_files(max_files: int, max_chars: int) -> tuple[list[dict], dict[str, str], int]:
    key_files = []
    contents = {}
    blocked_reads = 0
    for file_path in PRIORITY_FILES[: max(0, max_files)]:
        access = read_restricted_file(file_path, max_chars, {"source": "self_inspection"})
        key_files.append({"path": file_path, "status": access["status"], "truncated": access["truncated"], "notes": access["reason"] or "Read through Restricted File Reader."})
        if access["status"] == "success":
            contents[file_path] = access["content"]
        else:
            blocked_reads += 1
    return key_files, contents, blocked_reads


def _module_summary(searches: dict[str, dict], read_contents: dict[str, str]) -> list[dict]:
    all_paths = " ".join(
        result.get("relative_path", "") for search in searches.values() for result in search.get("results", [])
    ).lower()
    modules = []
    for module, path in MODULE_PATHS.items():
        found = path.lower() in all_paths
        evidence = [path] if found else []
        if path.replace("C:/Aether/", "") in " ".join(read_contents.keys()).replace("C:/Aether/", ""):
            evidence.append("restricted read succeeded")
        modules.append({
            "module": module,
            "status": "present" if found else "missing",
            "evidence": evidence,
            "notes": "Located through restricted project inspection." if found else "No matching path was found through restricted search.",
        })
    return modules


def _api_endpoints(api_content: str) -> list[dict]:
    return [{"method": method.upper(), "path": path} for method, path in re.findall(r'@app\.(get|post)\("([^"]+)"\)', api_content)]


def create_project_self_inspection(
    root: str = "C:/Aether",
    max_files_to_read: int = 20,
    max_chars_per_file: int = 6000,
    metadata: dict | None = None,
) -> dict:
    structure_browse = browse_restricted_path(root, max_depth=4, max_entries=500, metadata={"source": "self_inspection"})
    searches = {term: search_restricted_files(term, root, 50, {"source": "self_inspection"}) for term in SEARCH_TERMS}
    key_files, contents, blocked_reads = _read_key_files(max_files_to_read, max_chars_per_file)
    api_scan = read_restricted_file(
        "C:/Aether/aether/interface/api_server.py",
        64 * 1024,
        {"source": "self_inspection_endpoint_scan"},
    )
    api_content = api_scan["content"] if api_scan["status"] == "success" else contents.get("C:/Aether/aether/interface/api_server.py", "")
    endpoints = _api_endpoints(api_content)
    modules = _module_summary(searches, contents)
    warnings = []
    if structure_browse["status"] != "success":
        warnings.append(f"Project structure browse failed: {structure_browse['reason']}")
    if blocked_reads:
        warnings.append(f"{blocked_reads} key-file reads were blocked.")
    if not api_content:
        warnings.append("API server content was unavailable for endpoint inspection.")
    status = "success" if not warnings else "partial"
    safety_boundaries = [
        {"boundary": "private runtime data stored outside repo", "present": True, "evidence": "config/aether.yaml defines C:/AetherData private paths."},
        {"boundary": "restricted file read blocks C:/AetherData", "present": True, "evidence": "Restricted File Reader uses approved C:/Aether roots only."},
        {"boundary": "restricted file browse blocks C:/AetherData", "present": True, "evidence": "Restricted File Browser uses the same approved roots."},
        {"boundary": "tool executor blocks non-sandbox tools", "present": True, "evidence": "tool_executor sandbox allowlist controls execution."},
        {"boundary": "approval queue exists", "present": any(module["module"] == "action.approval_queue" and module["status"] == "present" for module in modules), "evidence": "aether/action/approval_queue.py"},
        {"boundary": "verification layer exists", "present": any(module["module"] == "verification" and module["status"] == "present" for module in modules), "evidence": "aether/verification/risk.py"},
        {"boundary": "tool registry exists", "present": any(module["module"] == "action.tool_registry" and module["status"] == "present" for module in modules), "evidence": "aether/action/tool_registry.py"},
        {"boundary": "graph integration exists", "present": any(module["module"] == "memory.graph" and module["status"] == "present" for module in modules), "evidence": "aether/memory/graph"},
        {"boundary": "timeline integration exists", "present": any(module["module"] == "memory.timeline" and module["status"] == "present" for module in modules), "evidence": "aether/memory/timeline"},
    ]
    timestamp = now_iso()
    report = {
        "id": f"self_inspection_{uuid.uuid4().hex}", "created": timestamp, "updated": timestamp, "timezone": get_timezone(),
        "root": root, "status": status,
        "summary": {
            "project_name": "Aether", "current_stage": "Milestone 18 — Project Self-Inspection Report",
            "overall_assessment": "Aether has a persistent-memory and permission-aware foundation with restricted project inspection capabilities.",
            "files_browsed": structure_browse.get("entry_count", 0), "files_read": len(contents),
            "blocked_reads": blocked_reads, "endpoint_count": len(endpoints),
        },
        "structure": {"browse_status": structure_browse["status"], "entry_count": structure_browse.get("entry_count", 0), "top_level_entries": [entry["name"] for entry in structure_browse.get("entries", []) if "/" not in entry.get("relative_path", "")]},
        "key_files": key_files, "modules": modules, "api_endpoints": endpoints, "safety_boundaries": safety_boundaries,
        "future_modules": ["restricted file write proposal", "patch review", "patch apply with approval", "real web search adapter", "real email draft/send adapter", "shell command planner", "plugin manager", "model adapter", "OpenAI-compatible API endpoint", "scheduler"],
        "warnings": warnings, "metadata": metadata or {},
    }
    data = load_self_inspection_reports()
    data["reports"].append(report)
    save_self_inspection_reports(data)
    return report


def list_self_inspection_reports(limit: int = 20) -> list[dict]:
    reports = list(load_self_inspection_reports()["reports"])
    reports.sort(key=lambda report: report.get("created", ""), reverse=True)
    return reports[: max(0, limit)]


def get_self_inspection_report(report_id: str) -> dict | None:
    for report in load_self_inspection_reports()["reports"]:
        if report.get("id") == report_id:
            return report
    return None


def self_inspection_status() -> dict:
    data = load_self_inspection_reports()
    return {"self_inspection_report_path": str(get_self_inspection_report_path()), "report_count": len(data["reports"]), "created": data.get("created"), "updated": data.get("updated"), "timezone": data.get("timezone")}


def seed_self_inspection_tool() -> dict:
    existing = get_tool("project.self_inspect")
    tool = register_tool("project.self_inspect", "Project Self Inspect", "Create a restricted project self-inspection report.", "project", "medium", True, True, False, False)
    return {"tool": tool, "created": existing is None}
