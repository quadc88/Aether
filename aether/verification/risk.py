"""Deterministic risk classification and verification planning for Aether."""

from __future__ import annotations


HIGH_RISK_RULES = {
    "file_delete": ["delete file", "remove folder", "format disk", "wipe", "删除", "移除", "格式化"],
    "external_send": ["send email", "send message", "发送邮件", "发送消息"],
    "financial_action": ["transfer money", "payment", "bank", "转账", "银行"],
    "secret_handling": ["password", "secret", "api key", "私人资料", "密码"],
    "medical_legal_tax": ["medical", "legal", "tax filing", "医疗", "法律", "报税"],
    "production_change": ["production system", "生产系统"],
    "software_install": ["install software", "安装软件"],
    "code_execution": ["run unknown code", "运行未知代码"],
    "identity_change": ["change identity seed", "modify identity seed", "修改身份种子"],
    "memory_modification": ["modify memory", "clear memory", "清除记忆"],
    "file_overwrite": ["overwrite file", "覆盖文件"],
}

MEDIUM_RISK_RULES = {
    "code_generation": ["write code", "写代码", "python", "代码"],
    "file_edit": ["edit file", "修改文件"],
    "config_change": ["change config", "改配置"],
    "debugging": ["debug", "explain technical issue", "解释错误"],
    "business_planning": ["business plan", "生意计划"],
    "financial_estimate": ["financial estimate", "财务估算"],
    "tax_explanation": ["tax explanation", "税务解释"],
    "server_setup": ["setup server", "设置服务器", "docker"],
    "git_operation": ["git reset", "git push"],
    "database_operation": ["database", "数据库"],
    "api_integration": ["api integration", "api 接入"],
}

LOW_RISK_RULES = {
    "brainstorming": ["brainstorm", "头脑风暴"],
    "summarization": ["summarize", "总结"],
    "text_rewrite": ["rewrite text", "改写", "宣传文案"],
    "creative_writing": ["creative writing", "创意写作"],
    "concept_explanation": ["explain concept", "解释概念"],
    "casual_conversation": ["casual conversation", "闲聊"],
    "naming": ["naming ideas", "取名字"],
}


def _matches(text: str, keywords: list[str]) -> list[str]:
    return [keyword for keyword in keywords if keyword.lower() in text]


def _first_match(text: str, rules: dict[str, list[str]]) -> tuple[str | None, list[str]]:
    for action_type, keywords in rules.items():
        matches = _matches(text, keywords)
        if matches:
            return action_type, matches
    return None, []


def detect_action_type(text: str) -> str:
    normalized = text.lower().strip()
    for rules in (HIGH_RISK_RULES, MEDIUM_RISK_RULES, LOW_RISK_RULES):
        action_type, _ = _first_match(normalized, rules)
        if action_type:
            return action_type
    return "general_request"


def classify_risk(text: str) -> dict:
    normalized = text.lower().strip()
    action_type, matches = _first_match(normalized, HIGH_RISK_RULES)
    if action_type:
        return {
            "risk_level": "high",
            "action_type": action_type,
            "confidence": "likely",
            "reasons": [f"Request appears to involve {match}." for match in matches],
        }

    action_type, matches = _first_match(normalized, MEDIUM_RISK_RULES)
    if action_type:
        return {
            "risk_level": "medium",
            "action_type": action_type,
            "confidence": "likely",
            "reasons": [f"Request appears to involve {match}." for match in matches],
        }

    action_type, matches = _first_match(normalized, LOW_RISK_RULES)
    if action_type:
        return {
            "risk_level": "low",
            "action_type": action_type,
            "confidence": "likely",
            "reasons": [f"Request appears to involve {match}." for match in matches],
        }

    return {
        "risk_level": "low",
        "action_type": "general_request",
        "confidence": "speculative",
        "reasons": ["No elevated-risk action indicators were detected."],
    }


def requires_verification(risk_level: str, action_type: str) -> bool:
    return risk_level in {"medium", "high"}


def requires_user_approval(risk_level: str, action_type: str) -> bool:
    return risk_level == "high"


def _recommended_checks(action_type: str, risk_level: str) -> list[str]:
    checks = {
        "file_delete": ["Confirm exact path.", "List affected files.", "Ask user for explicit approval.", "Prefer backup before deletion."],
        "file_overwrite": ["Confirm exact target file.", "Show the change to be made.", "Preserve a backup before overwrite.", "Ask user for explicit approval."],
        "external_send": ["Show final message body.", "Show recipients.", "Ask user for explicit approval.", "Prefer draft before send."],
        "code_execution": ["Show command.", "Explain expected effect.", "Run in sandbox when possible.", "Ask approval for high-risk commands."],
        "memory_modification": ["Show memory item.", "Explain change.", "Preserve backup or history.", "Ask approval before irreversible change."],
        "identity_change": ["Show the proposed Identity Seed change.", "Preserve backup and version history.", "Explain rollback options.", "Ask user for explicit approval."],
        "medical_legal_tax": ["Verify with trusted sources.", "State uncertainty and limits.", "Ask for clarification when facts are incomplete."],
        "financial_action": ["Confirm amount, destination, and currency.", "Ask user for explicit approval before execution.", "Verify current transaction details."],
        "secret_handling": ["Avoid exposing sensitive values.", "Confirm secure handling requirements.", "Ask user for explicit approval before external disclosure."],
    }
    if action_type in checks:
        return checks[action_type]
    if risk_level == "medium":
        return ["Perform a consistency check.", "Test or validate the result before reuse.", "State relevant uncertainty."]
    if risk_level == "high":
        return ["Verify relevant facts and targets.", "Explain expected effect and risk.", "Ask user for explicit approval before execution."]
    return ["State uncertainty when the result is not fully verified."]


def verification_plan(text: str) -> dict:
    classification = classify_risk(text)
    risk_level = classification["risk_level"]
    action_type = classification["action_type"]
    return {
        **classification,
        "requires_verification": requires_verification(risk_level, action_type),
        "requires_user_approval": requires_user_approval(risk_level, action_type),
        "recommended_checks": _recommended_checks(action_type, risk_level),
    }
