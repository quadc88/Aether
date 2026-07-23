"""Deterministic risk classification and verification planning for Aether."""

from __future__ import annotations

# --- Verb + Object destructive-detection constants ---

_EN_DESTRUCTIVE_VERBS = [
    "delete", "remove", "clear", "wipe", "erase",
    "reset", "overwrite", "corrupt", "destroy", "purge", "forget",
]

_EN_PROTECTED_OBJECTS = [
    "identity seed", "identity file", "private memory", "all memory",
    "memory", "private data", "aetherdata", "vault", "timeline",
    "graph memory", "vector memory", "vector database",
]

_ZH_DESTRUCTIVE_VERBS = [
    "\u5220\u9664",       # delete
    "\u79fb\u9664",       # remove
    "\u6e05\u7a7a",       # clear/empty
    "\u6e05\u9664",       # cleanse/clear
    "\u64e6\u9664",       # erase
    "\u91cd\u7f6e",       # reset
    "\u8986\u76d6",       # overwrite
    "\u7834\u574f",       # corrupt/destroy
    "\u9500\u6bc1",       # destroy
    "\u5fd8\u8bb0",       # forget
]

_ZH_PROTECTED_OBJECTS = [
    "\u8eab\u4efd\u79cd\u5b50",   # identity seed
    "\u8eab\u4efd\u6587\u4ef6",   # identity file
    "\u79c1\u4eba\u8bb0\u5fc6",   # private memory
    "\u6240\u6709\u8bb0\u5fc6",   # all memory
    "\u8bb0\u5fc6",              # memory
    "\u79c1\u4eba\u8d44\u6599",   # private data
    "\u79c1\u6709\u6570\u636e",   # private data
    "\u65f6\u95f4\u7ebf",         # timeline
    "\u56fe\u8bb0\u5fc6",         # graph memory
    "\u5411\u91cf\u8bb0\u5fc6",    # vector memory
    "\u5411\u91cf\u6570\u636e\u5e93",  # vector database
    "\u6240\u6709\u6570\u636e",     # all data
]


def _detect_destructive_memory_or_identity_action(
    normalized_text: str,
) -> tuple[str | None, list[str]]:
    """Detect destructive actions targeting protected objects.

    Returns (action_type, matched_components) or (None, []).

    Priority:
    1. Exact destructive phrases always match first (reset/destroy/wipe Aether).
    2. Destructive verb + identity object → "identity_change".
    3. Destructive verb + memory/data object → "destructive_memory_action".
    """
    # Step 1: exact destructive phrases
    _EXACT_PHRASES = [
        "factory reset", "wipe aether", "destroy aether", "reset aether",
        "\u91cd\u7f6e aether", "\u6e05\u7a7a aether",
        "\u9500\u6bc1 aether", "\u6e05\u9664\u6240\u6709\u6570\u636e",
        "\u5f7b\u5e95\u6e05\u7a7a",
    ]
    for phrase in _EXACT_PHRASES:
        if phrase.lower() in normalized_text or phrase in normalized_text:
            return "destructive_reset", [phrase]

    # Step 2: find destructive verbs
    en_verbs = [v for v in _EN_DESTRUCTIVE_VERBS if v in normalized_text]
    zh_verbs = [v for v in _ZH_DESTRUCTIVE_VERBS if v in normalized_text]
    has_verb = bool(en_verbs or zh_verbs)

    # Step 3: find protected objects
    en_objects = [o for o in _EN_PROTECTED_OBJECTS if o.lower() in normalized_text]
    zh_objects = [o for o in _ZH_PROTECTED_OBJECTS if o in normalized_text]
    has_object = bool(en_objects or zh_objects)

    if not has_verb or not has_object:
        return None, []

    combined: list[str] = []
    if en_verbs:
        combined.extend(en_verbs[:2])
    if zh_verbs:
        combined.extend(zh_verbs[:2])
    if en_objects:
        combined.extend(en_objects[:2])
    if zh_objects:
        combined.extend(zh_objects[:2])

    # Check if any matched object is identity-related
    identity_keywords_en = ["identity seed", "identity file"]
    identity_keywords_zh = ["\u8eab\u4efd\u79cd\u5b50", "\u8eab\u4efd\u6587\u4ef6"]
    matched_identity = [
        o for o in en_objects + zh_objects
        if o in identity_keywords_en or o in identity_keywords_zh
    ]

    if matched_identity:
        return "identity_change", combined
    return "destructive_memory_action", combined


HIGH_RISK_RULES = {
    "file_delete": ["delete file", "remove folder", "format disk", "wipe", "删除", "移除", "格式化"],
    "external_send": ["send email", "send message", "发送邮件", "发送消息"],
    "financial_action": ["transfer money", "payment", "bank", "转账", "银行"],
    "secret_handling": ["password", "secret", "api key", "私人资料", "密码"],
    "medical_legal_tax": ["medical", "legal", "tax filing", "医疗", "法律", "报税"],
    "production_change": ["production system", "生产系统"],
    "software_install": ["install software", "安装软件"],
    "code_execution": ["run unknown code", "运行未知代码"],
    "destructive_reset": [
        "factory reset", "reset Aether", "wipe Aether",
        "destroy Aether", "purge memory", "purge private data",
        "\u91cd\u7f6e aether", "\u6e05\u7a7a aether",
        "\u9500\u6bc1 aether", "\u6e05\u9664\u6240\u6709\u6570\u636e",
        "\u5f7b\u5e95\u6e05\u7a7a",
    ],
    "identity_change": [
        "change identity seed", "modify identity seed", "修改身份种子",
        "delete identity seed", "remove identity seed",
        "erase identity seed", "overwrite identity seed",
        "reset identity", "corrupt identity", "erase identity",
        "\u8eab\u4efd\u6587\u4ef6",
        "\u5220\u9664\u8eab\u4efd", "\u5220\u9664\u8eab\u4efd\u79cd\u5b50", "\u91cd\u7f6e\u8eab\u4efd",
        "\u8986\u76d6\u8eab\u4efd", "\u7834\u574f\u8eab\u4efd",
    ],
    "memory_modification": ["modify memory", "clear memory", "\u6e05\u9664\u8bb0\u5fc6"],
    "destructive_memory_action": [
        "delete memory", "erase memory",
        "wipe memory", "forget all memory",
        "delete all memory", "clear all memory",
        "delete private memory", "wipe private memory",
        "delete private data", "wipe private data", "erase private data",
        "delete vault", "delete timeline", "erase timeline",
        "delete graph memory", "delete vector memory", "delete vector database",
        "wipe aetherdata", "delete aetherdata", "remove aetherdata",
        "purge memory", "purge private data",
        "\u5220\u9664\u8bb0\u5fc6", "\u6e05\u7a7a\u8bb0\u5fc6", "\u6e05\u9664\u8bb0\u5fc6", "\u64e6\u9664\u8bb0\u5fc6",
        "\u5fd8\u8bb0\u6240\u6709\u8bb0\u5fc6",
        "\u5220\u9664\u6240\u6709\u8bb0\u5fc6", "\u6e05\u7a7a\u6240\u6709\u8bb0\u5fc6",
        "\u5220\u9664\u79c1\u4eba\u8bb0\u5fc6", "\u6e05\u7a7a\u79c1\u4eba\u8bb0\u5fc6",
        "\u5220\u9664\u79c1\u4eba\u8d44\u6599", "\u6e05\u7a7a\u79c1\u4eba\u8d44\u6599",
        "\u5220\u9664\u79c1\u6709\u6570\u636e", "\u6e05\u7a7a\u79c1\u6709\u6570\u636e",
        "\u5220\u9664\u65f6\u95f4\u7ebf", "\u6e05\u7a7a\u65f6\u95f4\u7ebf",
        "\u5220\u9664\u56fe\u8bb0\u5fc6", "\u5220\u9664\u5411\u91cf\u8bb0\u5fc6",
        "\u5220\u9664\u5411\u91cf\u6570\u636e\u5e93",
    ],
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

    # --- Priority 1: verb + object destruct detection ---
    action_type, det_matches = _detect_destructive_memory_or_identity_action(
        normalized
    )
    if action_type is not None:
        return {
            "risk_level": "high",
            "action_type": action_type,
            "confidence": "probable",
            "reasons": [
                f"Destructive {action_type.replace('_', ' ')} detected involving "
                + ", ".join(det_matches[:3])
                + "."
            ],
        }

    # --- Priority 2: exact HIGH_RISK_RULES keywords ---
    action_type, matches = _first_match(normalized, HIGH_RISK_RULES)
    if action_type:
        # Multi-match gets higher confidence
        confidence = "probable" if len(matches) >= 2 else "likely"
        return {
            "risk_level": "high",
            "action_type": action_type,
            "confidence": confidence,
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
        "destructive_memory_action": [
            "Confirm which memory/data is targeted.",
            "Verify user intent — this action may be irreversible.",
            "Ensure backups exist before proceeding.",
            "Ask user for explicit approval.",
        ],
        "identity_change": [
            "Show the proposed Identity Seed change.",
            "Preserve backup and version history.",
            "Explain rollback options.",
            "Ask user for explicit approval.",
        ],
        "destructive_reset": [
            "This action may destroy core Aether data irreversibly.",
            "Verify user intent with explicit confirmation.",
            "Ensure full system backup exists.",
            "Ask user for explicit approval.",
        ],
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
