"""Deterministic, non-executing Tool Invocation Planner for Aether."""

from pathlib import Path
import json
import uuid

import yaml

from aether.action.approval_queue import create_approval_item
from aether.action.tool_registry import get_tool
from aether.time.clock import get_timezone, now_iso
from aether.verification.risk import verification_plan


INFERENCE_RULES = [
    ("file.patch_apply", ["apply patch", "apply proposal", "apply approved patch", "执行补丁", "应用补丁", "应用修改提案", "写入已批准修改"], "Request appears to apply an approved patch proposal."),
    ("file.patch_review", ["review patch", "approve patch proposal", "reject patch proposal", "request patch changes", "审核补丁", "批准修改提案", "拒绝修改提案", "要求修改", "审核文件修改"], "Request appears to involve reviewing a patch proposal."),
    ("file.patch_proposal", ["propose file change", "create patch", "draft patch", "patch proposal", "修改建议", "生成补丁", "创建修改方案", "文件修改提案", "edit file", "write file", "save file", "overwrite file"], "Request is handled safely by drafting a patch proposal first."),
    ("project.self_inspect", ["inspect project", "self inspection", "project report", "check aether structure", "检查项目", "自我检查", "项目报告", "检查 aether 结构"], "Request appears to involve project self-inspection."),
    ("file.restricted_search", ["find file", "search file", "locate file", "找文件", "搜索文件", "查找文件", "找到 api_server"], "Request appears to involve finding a project file."),
    ("file.restricted_browse", ["list files", "show folder", "browse project", "project tree", "file structure", "列出文件", "显示目录", "浏览项目", "项目结构", "文件结构", "看看有哪些文件"], "Request appears to involve browsing project files."),
    ("file.delete", ["delete file", "remove folder", "删除", "移除"], "Request appears to involve deleting files."),
    ("file.write", ["write file", "save file", "create file", "修改文件", "写入文件"], "Request appears to involve writing files."),
    ("file.restricted_read", ["read file", "open file", "inspect file", "查看文件", "读取文件", "打开文件", "检查文件", "看一下文件"], "Request appears to involve reading files."),
    ("shell.run", ["run command", "execute command", "terminal", "cmd", "powershell", "运行命令"], "Request appears to involve running a command."),
    ("email.send", ["send email", "send message", "发送邮件", "发信息"], "Request appears to involve sending a message."),
    ("email.draft", ["draft email", "write email draft", "草稿", "起草邮件"], "Request appears to involve drafting an email."),
    ("memory.clear", ["forget", "clear memory", "删除记忆", "清除记忆"], "Request appears to involve clearing memory."),
    ("memory.write", ["remember", "save memory", "记录记忆", "写入记忆"], "Request appears to involve writing memory."),
    ("web.search", ["search web", "look up", "查资料", "搜索网络", "搜索"], "Request appears to involve web search."),
    ("graph.add_relationship", ["relationship", "link", "relation", "关系", "关联"], "Request appears to involve a relationship."),
    ("approval.approve", ["approve", "批准", "审批"], "Request appears to involve approving an action."),
    ("approval.create", ["approval"], "Request appears to involve creating an approval item."),
]

RISK_ORDER = {"low": 0, "medium": 1, "high": 2}


def load_aether_config(path: str = "config/aether.yaml") -> dict:
    config_path = Path(path)
    if not config_path.exists():
        return {}
    with config_path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def get_tool_plan_dir() -> Path:
    private_dir = load_aether_config().get("paths", {}).get("private_dir", "private")
    return Path(private_dir) / "tool_plans"


def get_tool_plan_path() -> Path:
    return get_tool_plan_dir() / "tool_plans.json"


def _new_plan_store() -> dict:
    timestamp = now_iso()
    return {
        "type": "tool_invocation_plans",
        "version": "0.1.0",
        "created": timestamp,
        "updated": timestamp,
        "timezone": get_timezone(),
        "plans": [],
    }


def _load_plan_store() -> dict:
    path = get_tool_plan_path()
    if not path.exists():
        return _new_plan_store()
    try:
        store = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return _new_plan_store()
    store.setdefault("type", "tool_invocation_plans")
    store.setdefault("version", "0.1.0")
    store.setdefault("created", now_iso())
    store.setdefault("updated", store["created"])
    store.setdefault("timezone", get_timezone())
    store.setdefault("plans", [])
    return store


def _save_plan_store(store: dict) -> None:
    path = get_tool_plan_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    store["updated"] = now_iso()
    store["timezone"] = get_timezone()
    path.write_text(json.dumps(store, indent=2, ensure_ascii=False), encoding="utf-8")


def infer_candidate_tool(text: str) -> dict:
    normalized = text.lower().strip()
    for tool_id, keywords, reason in INFERENCE_RULES:
        if any(keyword.lower() in normalized for keyword in keywords):
            return {"tool_id": tool_id, "match_confidence": "likely", "reason": reason}
    return {"tool_id": None, "match_confidence": "uncertain", "reason": "No registered tool pattern matched the request.", "status": "no_tool_matched"}


def _highest_risk(first: str, second: str) -> str:
    return first if RISK_ORDER.get(first, 1) >= RISK_ORDER.get(second, 1) else second


def create_tool_invocation_plan(
    text: str,
    proposed_action: str | None = None,
    metadata: dict | None = None,
    create_approval_if_required: bool = False,
    tool_id: str | None = None,
) -> dict:
    candidate_tool = (
        {"tool_id": tool_id, "match_confidence": "confirmed", "reason": "Tool was explicitly requested."}
        if tool_id
        else infer_candidate_tool(text)
    )
    verification = verification_plan(text)
    tool_id = candidate_tool["tool_id"]
    tool = get_tool(tool_id) if tool_id else None
    final_risk = verification["risk_level"]
    reasons = list(verification["reasons"])
    approval_item = None

    if tool_id is None:
        plan_status = "no_tool_matched"
        requires_verification = verification["requires_verification"]
        requires_approval = verification["requires_user_approval"]
        allow_auto_execute = False
        reasons.append("No candidate tool was inferred.")
    elif tool is None:
        plan_status = "tool_not_found"
        requires_verification = verification["requires_verification"]
        requires_approval = verification["requires_user_approval"]
        allow_auto_execute = False
        reasons.append(f"Tool {tool_id} is not registered.")
    else:
        final_risk = _highest_risk(verification["risk_level"], tool["risk_level"])
        requires_verification = verification["requires_verification"] or tool["requires_verification"]
        requires_approval = verification["requires_user_approval"] or tool["requires_user_approval"]
        allow_auto_execute = tool["allow_auto_execute"] and not requires_approval
        reasons.append(f"Tool Registry classifies {tool_id} as {tool['risk_level']} risk.")
        if not tool["enabled"]:
            plan_status = "tool_disabled"
            allow_auto_execute = False
            reasons.append(f"Tool {tool_id} is disabled.")
        elif requires_approval:
            plan_status = "approval_required"
            allow_auto_execute = False
            reasons.append("User approval is required before execution.")
        elif allow_auto_execute:
            plan_status = "ready_auto"
            reasons.append("Tool policy permits automatic execution in principle.")
        else:
            plan_status = "ready_manual"
            reasons.append("Tool is available but requires manual invocation.")

    if create_approval_if_required and plan_status == "approval_required":
        approval_verification_plan = {
            **verification,
            "risk_level": final_risk,
            "requires_verification": requires_verification,
            "requires_user_approval": requires_approval,
        }
        approval_item = create_approval_item(
            request_text=text,
            proposed_action=proposed_action or text,
            verification_plan=approval_verification_plan,
            metadata=metadata,
        )

    timestamp = now_iso()
    plan = {
        "id": f"tool_plan_{uuid.uuid4().hex}",
        "created": timestamp,
        "updated": timestamp,
        "timezone": get_timezone(),
        "request_text": text,
        "proposed_action": proposed_action or text,
        "candidate_tool": candidate_tool,
        "tool": tool,
        "verification_plan": verification,
        "decision": {
            "plan_status": plan_status,
            "risk_level": final_risk,
            "can_execute": plan_status in {"ready_auto", "ready_manual"},
            "requires_verification": requires_verification,
            "requires_user_approval": requires_approval,
            "allow_auto_execute": allow_auto_execute,
            "approval_recommended": requires_approval,
            "approval_item_created": approval_item is not None,
            "reasons": reasons,
        },
        "approval_item": approval_item,
        "metadata": metadata or {},
    }
    store = _load_plan_store()
    store["plans"].append(plan)
    _save_plan_store(store)
    return plan


def list_tool_plans(limit: int = 50) -> list[dict]:
    plans = list(_load_plan_store()["plans"])
    plans.sort(key=lambda plan: plan.get("created", ""), reverse=True)
    return plans[: max(0, limit)]


def get_tool_plan(plan_id: str) -> dict | None:
    for plan in _load_plan_store()["plans"]:
        if plan.get("id") == plan_id:
            return plan
    return None


def tool_planner_status() -> dict:
    store = _load_plan_store()
    return {
        "tool_plan_path": str(get_tool_plan_path()),
        "plan_count": len(store["plans"]),
        "created": store.get("created"),
        "updated": store.get("updated"),
        "timezone": store.get("timezone"),
    }
