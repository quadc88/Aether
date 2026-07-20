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
    ("project.approved_dry_run_gate.status", ["approved dry run gate status", "批准 dry run 状态"], "Request appears to inspect approved dry-run gate status."),
    ("project.approved_dry_run_gate.summary", ["summarize approved dry run gate", "approved dry run summary", "总结批准 dry run"], "Request appears to summarize an approved dry-run gate."),
    ("project.approved_dry_run_gate.execute", ["execute approved dry run", "run approved proposal dry run", "执行批准提案测试", "运行批准提案 dry run"], "Request appears to execute an approved proposal dry-run."),
    ("project.approved_dry_run_gate.open", ["open approved dry run gate", "dry run approved proposal", "prepare dry run for approved proposal", "打开批准提案 dry run", "执行批准提案 dry run", "准备批准提案测试"], "Request appears to open an approved dry-run gate."),
    ("project.revised_proposal_review.status", ["revised proposal review status", "修订提案审核状态"], "Request appears to inspect revised proposal review status."),
    ("project.revised_proposal_review.summary", ["summarize revised proposal review", "revised proposal review summary", "总结修订提案审核"], "Request appears to summarize revised proposal review."),
    ("project.revised_proposal_review.submit", ["submit revised proposal review", "approve revised proposal", "reject revised proposal", "request changes on revised proposal", "提交修订提案审核", "批准修订提案", "拒绝修订提案", "要求修改修订提案"], "Request appears to submit a revised proposal review."),
    ("project.revised_proposal_review.open", ["open revised proposal review", "review revised proposal", "open review for revised proposal", "打开修订提案审核", "审核修订提案", "人工审核修订提案"], "Request appears to open review for a revised proposal."),
    ("project.proposal_revision_console.status", ["proposal revision console status", "提案修订状态"], "Request appears to inspect proposal revision console status."),
    ("project.proposal_revision_console.summary", ["summarize proposal revision console", "proposal revision summary", "总结提案修订"], "Request appears to summarize a proposal revision console."),
    ("project.proposal_revision_console.create_revision", ["create proposal revision", "submit revised proposal", "create revised patch proposal", "提交修订提案", "创建修订补丁"], "Request appears to create a caller-authored proposal revision."),
    ("project.proposal_revision_console.open", ["open proposal revision console", "revise proposal", "revise requested changes", "handle requested changes", "create revised proposal", "打开提案修改", "修改提案", "处理要求修改", "创建修订提案"], "Request appears to open a proposal revision console."),
    ("project.proposal_review_console.status", ["proposal review console status", "提案审核状态"], "Request appears to inspect proposal review console status."),
    ("project.proposal_review_console.summary", ["summarize proposal review console", "proposal review console summary", "总结提案审核"], "Request appears to summarize a proposal review console."),
    ("project.proposal_review_console.submit", ["submit proposal review", "approve proposal review", "reject proposal review", "request changes on proposal", "提交提案审核", "批准提案", "拒绝提案", "要求修改提案"], "Request appears to submit an explicit proposal review decision."),
    ("project.proposal_review_console.open", ["open proposal review console", "review this proposal", "open human proposal review", "open review console from workflow", "从修复流程打开提案审核", "打开提案审核", "人工审核提案"], "Request appears to open a safe proposal review console."),
    ("project.repair_workflow_export.status", ["repair workflow export status", "workflow export status", "修复流程导出状态"], "Request appears to inspect repair workflow export status."),
    ("project.repair_workflow_export.export_private", ["private repair workflow export", "detailed workflow export", "私人修复流程报告", "详细修复流程导出"], "Request appears to export a private workflow report."),
    ("project.repair_workflow_export.export_index", ["export repair workflow index", "generate repair workflow dashboard index", "workflow index", "导出修复流程索引", "生成修复流程索引"], "Request appears to export a workflow dashboard index."),
    ("project.repair_workflow_export.export_report", ["export repair workflow report", "generate repair workflow report", "repair workflow dashboard", "export workflow dashboard", "导出修复流程报告", "生成修复流程报告", "修复流程仪表板"], "Request appears to export a workflow report."),
    ("project.repair_workflow.status", ["repair workflow tracker status", "workflow tracker status", "修复流程追踪状态"], "Request appears to inspect repair workflow tracker status."),
    ("project.repair_workflow.summary", ["summarize repair workflow", "repair workflow summary", "总结修复流程"], "Request appears to summarize a repair workflow."),
    ("project.repair_workflow.trace", ["trace repair workflow", "repair workflow status", "workflow tracker", "trace repair pipeline", "where is this repair now", "跟踪修复流程", "修复流程状态", "追踪修复管线", "这个修复到哪一步了"], "Request appears to trace an existing repair workflow."),
    ("project.repair_bridge_selection.status", ["repair bridge selection status", "修复桥接选择状态"], "Request appears to inspect repair bridge selection status."),
    ("project.repair_bridge_selection.summary", ["summarize repair bridge selection", "repair bridge selection summary", "总结修复桥接选择"], "Request appears to summarize a repair bridge selection."),
    ("project.repair_bridge_selection.create", ["select repair bridge candidate", "create bridge from repair plan", "bridge repair plan finding", "turn repair plan candidate into proposal", "从修复计划创建桥接", "从修复计划生成修改建议", "选择修复候选"], "Request appears to select a repair-plan candidate for a guarded review bridge."),
    ("project.repair_plan.status", ["repair plan status", "修复计划状态"], "Request appears to inspect repair-plan status."),
    ("project.repair_plan.summary", ["summarize repair plan", "repair plan summary", "总结修复计划"], "Request appears to summarize a repair plan."),
    ("project.repair_plan.create", ["prioritize review findings", "repair plan", "create repair plan", "plan fixes from code review", "prioritize code review", "排序审查结果", "修复计划", "从代码审查制定修复计划", "优先处理 findings"], "Request appears to create a repair plan."),
    ("project.review_bridge.status", ["review bridge status", "审查桥接状态"], "Request appears to inspect bridge status."),
    ("project.review_bridge.summary", ["summarize review bridge", "review bridge summary", "总结审查桥接"], "Request appears to summarize a review bridge."),
    ("project.review_bridge.create", ["bridge code review finding", "create self modification from finding", "turn finding into proposal", "review bridge", "从代码审查生成修改", "从 finding 创建自我修改", "把审查结果转成修改建议"], "Request appears to bridge a review finding."),
    ("project.code_review.status", ["code review status", "代码审查状态"], "Request appears to inspect code-review status."),
    ("project.code_review.summary", ["summarize code review", "code review summary", "总结代码审查"], "Request appears to summarize a code review."),
    ("project.code_review.create", ["code review", "review code", "inspect code", "check project code", "audit source code", "审查代码", "代码审查", "检查源代码", "项目代码审计"], "Request appears to create a restricted code review."),
    ("project.changelog.status", ["changelog status", "changelog exporter status", "变更日志状态"], "Request appears to inspect changelog status."),
    ("project.changelog.export_private", ["private changelog report", "detailed private changelog", "私人变更报告", "详细变更日志"], "Request appears to export a private changelog."),
    ("project.changelog.export_milestone", ["export milestone report", "generate milestone report", "milestone changelog", "导出 milestone 报告", "生成 milestone 报告"], "Request appears to export a milestone report."),
    ("project.changelog.export_public", ["export changelog", "generate changelog", "write changelog", "changelog export", "导出变更日志", "生成变更日志", "写入 changelog"], "Request appears to export a public changelog."),
    ("project.self_modification.summary", ["summarize self modification session", "self modification summary", "总结自我修改", "自我修改总结"], "Request appears to summarize a self-modification session."),
    ("project.self_modification.rollback", ["rollback self modification", "revert self modification", "回滚自我修改", "撤销自我修改"], "Request appears to roll back a self-modification session."),
    ("project.self_modification.apply", ["apply self modification", "应用自我修改"], "Request appears to apply a self-modification session."),
    ("project.self_modification.dry_run", ["dry run self modification", "test self modification", "自我修改 dry run", "测试自我修改"], "Request appears to dry-run a self-modification session."),
    ("project.self_modification.review", ["review self modification", "approve self modification", "审核自我修改", "批准自我修改"], "Request appears to review a self-modification session."),
    ("project.self_modification.create", ["self modification", "self modify", "improve aether safely", "safe self update", "自我修改", "安全自我修改", "改进 aether", "安全更新 aether"], "Request appears to create a self-modification session."),
    ("project.mutation_log.summary", ["summarize project changes", "show changelog", "mutation summary", "总结项目变更", "查看变更日志", "总结成长记录"], "Request appears to summarize mutation history."),
    ("project.mutation_log.record", ["record project change", "mutation log", "changelog", "project history", "record milestone", "记录项目变更", "变更日志", "成长记录", "项目历史", "记录 milestone"], "Request appears to record project history."),
    ("file.patch_rollback", ["rollback patch", "revert patch", "restore backup", "undo patch", "回滚补丁", "撤回补丁", "还原备份", "撤销修改"], "Request appears to roll back a patch apply."),
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
