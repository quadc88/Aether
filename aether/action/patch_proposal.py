"""Safe, private file-change proposals; this module never applies a patch."""
from pathlib import Path
import difflib, json, uuid
import yaml

from aether.action.approval_queue import create_approval_item
from aether.action.restricted_file_reader import read_restricted_file
from aether.action.tool_registry import get_tool, register_tool
from aether.memory.graph.store import add_edge
from aether.memory.timeline.recorder import record_event
from aether.time.clock import get_timezone, now_iso
from aether.verification.risk import verification_plan

CRITICAL_PATHS = {"identity/identity_seed.md", "docs/constitution.md", "docs/architecture.md", "aether/interface/api_server.py", "aether/action/tool_executor.py", "aether/action/restricted_file_reader.py", "aether/action/restricted_file_browser.py", "aether/action/approval_queue.py", "aether/verification/risk.py"}
VALID_STATUSES = {"draft", "approval_required", "approved", "rejected", "superseded"}

def load_aether_config(path: str = "config/aether.yaml") -> dict:
    p = Path(path)
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {} if p.exists() else {}

def get_patch_proposal_dir() -> Path:
    return Path(load_aether_config().get("paths", {}).get("private_dir", "private")) / "patch_proposals"

def get_patch_proposal_path() -> Path:
    return get_patch_proposal_dir() / "patch_proposals.json"

def load_patch_proposals() -> dict:
    path = get_patch_proposal_path()
    try: data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except json.JSONDecodeError: data = {}
    timestamp = now_iso()
    data.setdefault("type", "patch_proposals"); data.setdefault("version", "0.1.0"); data.setdefault("created", timestamp); data.setdefault("updated", data["created"]); data.setdefault("timezone", get_timezone()); data.setdefault("proposals", [])
    return data

def save_patch_proposals(data: dict) -> None:
    path = get_patch_proposal_path(); path.parent.mkdir(parents=True, exist_ok=True)
    data["updated"] = now_iso(); data["timezone"] = get_timezone()
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def _is_critical(normalized_path: str) -> bool:
    text = normalized_path.replace("\\", "/").lower()
    return any(text.endswith("/" + critical) for critical in CRITICAL_PATHS)

def create_patch_proposal(target_path: str, request_text: str, proposed_change_summary: str, proposed_excerpt: str, reason: str = "", original_excerpt: str | None = None, create_approval_if_required: bool = False, metadata: dict | None = None) -> dict:
    access = read_restricted_file(target_path, 12000, {"source": "patch_proposal"})
    warnings = []; normalized = access["normalized_path"]
    if access["status"] != "success":
        proposal = {"id": f"patch_proposal_{uuid.uuid4().hex}", "created": now_iso(), "updated": now_iso(), "timezone": get_timezone(), "status": "rejected", "target_path": target_path, "normalized_path": normalized, "request_text": request_text, "proposed_change_summary": proposed_change_summary, "reason": reason or access["reason"], "risk_level": "high", "requires_user_approval": True, "verification_plan": verification_plan(request_text), "original_excerpt": "", "proposed_excerpt": "", "patch_format": "unified_diff_preview", "patch_text": "", "diff_preview": "", "approval_id": None, "metadata": metadata or {}, "warnings": [f"Target was blocked: {access['reason']}"]}
        data=load_patch_proposals(); data["proposals"].append(proposal); save_patch_proposals(data); return proposal
    original = original_excerpt if original_excerpt is not None else access["content"][:4000]
    if len(original) > 4000: original=original[:4000]; warnings.append("Original excerpt truncated to 4000 characters.")
    proposed = proposed_excerpt[:8000]
    if len(proposed_excerpt) > 8000: warnings.append("Proposed excerpt truncated to 8000 characters.")
    plan = verification_plan(request_text); critical = _is_critical(normalized)
    risk = "high" if critical or plan["risk_level"] == "high" else "medium"
    required = risk == "high" or critical
    approval = create_approval_item(request_text, proposed_change_summary, {**plan, "risk_level": risk, "requires_user_approval": required}, metadata) if required and create_approval_if_required else None
    timestamp=now_iso(); diff="".join(difflib.unified_diff(original.splitlines(True), proposed.splitlines(True), fromfile=normalized, tofile=normalized + " (proposed)"))
    proposal={"id":f"patch_proposal_{uuid.uuid4().hex}","created":timestamp,"updated":timestamp,"timezone":get_timezone(),"status":"approval_required" if required else "draft","target_path":target_path,"normalized_path":normalized,"request_text":request_text,"proposed_change_summary":proposed_change_summary,"reason":reason,"risk_level":risk,"requires_user_approval":required,"verification_plan":plan,"original_excerpt":original,"proposed_excerpt":proposed,"patch_format":"unified_diff_preview","patch_text":diff,"diff_preview":diff,"approval_id":approval["id"] if approval else None,"metadata":metadata or {},"warnings":warnings}
    data=load_patch_proposals(); data["proposals"].append(proposal); save_patch_proposals(data)
    record_event("patch_proposal", f"Patch proposal created: {target_path}", f"Aether created patch proposal {proposal['id']} with status {proposal['status']}.", "high" if risk == "high" else "normal")
    try:
        for s,r,t in [("Aether","created_patch_proposal",proposal["id"]),(proposal["id"],"targets_file",normalized),(proposal["id"],"has_status",proposal["status"]),(proposal["id"],"has_risk_level",risk)]: add_edge(s,r,t)
        if approval: add_edge(proposal["id"],"created_approval_item",approval["id"])
    except Exception as error: proposal["warnings"].append(f"Graph Memory integration was unavailable: {error}"); save_patch_proposals(data)
    return proposal

def list_patch_proposals(status: str | None = None, limit: int = 50) -> list[dict]:
    items=load_patch_proposals()["proposals"]; return sorted([p for p in items if not status or p["status"]==status], key=lambda p:p["created"], reverse=True)[:max(0,limit)]
def get_patch_proposal(proposal_id: str) -> dict | None: return next((p for p in load_patch_proposals()["proposals"] if p["id"]==proposal_id), None)
def mark_patch_proposal_status(proposal_id: str, status: str, reason: str = "") -> dict | None:
    if status not in VALID_STATUSES: return None
    data=load_patch_proposals()
    for p in data["proposals"]:
        if p["id"]==proposal_id: p["status"]=status; p["updated"]=now_iso(); p["reason"]=reason or p["reason"]; save_patch_proposals(data); record_event("patch_proposal",f"Patch proposal status changed: {p['target_path']}",f"Aether changed patch proposal {proposal_id} to {status}.","high" if p["risk_level"]=="high" else "normal"); return p
    return None
def patch_proposal_status() -> dict:
    data=load_patch_proposals(); return {"patch_proposal_path":str(get_patch_proposal_path()),"proposal_count":len(data["proposals"]),"created":data["created"],"updated":data["updated"],"timezone":data["timezone"]}
def seed_patch_proposal_tool() -> dict:
    existing=get_tool("file.patch_proposal"); tool=register_tool("file.patch_proposal","File Patch Proposal","Draft a safe project-file patch without applying it.","file","medium",True,True,False,False); return {"tool":tool,"created":existing is None}
