"""Text perception for Aether.

Provides lightweight analysis of input text without calling external APIs,
mutating memory, or executing tools.
"""

from __future__ import annotations


_COMMAND_HINTS = [
    "help", "status", "init", "initialize", "start", "stop",
    "clear", "reset", "list", "create", "delete", "modify",
    "enable", "disable", "export", "import", "search",
    "/help", "/status", "/chat", "/init", "/clear",
]

_SECRET_PATTERNS = [
    "password", "secret", "api key", "token", "private_key",
    "credential", "secret_key", "access_key",
]


def _detect_language(text: str) -> str:
    """Heuristically detect language hint.

    Returns one of: "en", "zh", "mixed", "unknown".
    """
    has_cjk = any("\u4e00" <= ch <= "\u9fff" for ch in text)
    has_latin = any(ch.isalpha() and not ("\u4e00" <= ch <= "\u9fff") for ch in text)
    if has_cjk and has_latin:
        return "mixed"
    if has_cjk:
        return "zh"
    if has_latin:
        return "en"
    # Check for digits/symbols only
    return "unknown"


def _has_question(text: str) -> bool:
    return "?" in text or "??" in text or "？" in text


def _has_command_hint(text: str) -> bool:
    lower = text.lower()
    return any(hint in lower for hint in _COMMAND_HINTS)


def _detect_risk_terms(text: str) -> list[str]:
    """Return risk-related terms found in the text."""
    lower = text.lower()
    detected = []
    for term in _SECRET_PATTERNS:
        if term in lower:
            detected.append(term)
    return detected


def perceive_text_input(
    text: str,
    metadata: dict | None = None,
) -> dict:
    """Analyze raw input text and return a perception dict.

    Does NOT call external APIs, mutate memory, or execute tools.

    Args:
        text: Raw user input string.
        metadata: Optional arbitrary metadata to pass through.

    Returns:
        Dict with keys: type, normalized_text, original_length,
        language_hint, contains_question, contains_command_hint,
        risk_terms_detected, warnings, metadata.
    """
    normalized = text.strip()
    risk_terms = _detect_risk_terms(normalized)
    warnings: list[str] = []
    if risk_terms:
        warnings.append(
            f"Text contains potentially sensitive terms: {', '.join(risk_terms)}. "
            "Ensure no secrets are shared."
        )

    return {
        "type": "text",
        "normalized_text": normalized,
        "original_length": len(text),
        "language_hint": _detect_language(normalized),
        "contains_question": _has_question(normalized),
        "contains_command_hint": _has_command_hint(normalized),
        "risk_terms_detected": risk_terms,
        "warnings": warnings,
        "metadata": metadata or {},
    }
