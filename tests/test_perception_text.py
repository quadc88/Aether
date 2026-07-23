"""Tests for text perception (Milestone 48B)."""

from aether.perception.text import perceive_text_input


class TestLanguageDetection:
    def test_english_text(self):
        result = perceive_text_input("Hello, how are you?")
        assert result["language_hint"] == "en"

    def test_chinese_text(self):
        result = perceive_text_input("你好，请帮我写一段代码。")
        assert result["language_hint"] in ("zh", "mixed")

    def test_mixed_text(self):
        result = perceive_text_input("请帮我写一个Python函数。")
        assert result["language_hint"] == "mixed"

    def test_short_english_question(self):
        result = perceive_text_input("What is Aether?")
        assert result["language_hint"] == "en"
        assert result["contains_question"] is True

    def test_command_hint_detected(self):
        result = perceive_text_input("/status")
        assert result["contains_command_hint"] is True

    def test_normal_conversation_no_command_hint(self):
        result = perceive_text_input("Let me think about this.")
        assert result["contains_command_hint"] is False


class TestRiskTerms:
    def test_secret_term_detected(self):
        result = perceive_text_input("Check my password for me")
        assert "password" in result["risk_terms_detected"]

    def test_api_key_term_detected(self):
        result = perceive_text_input("My API key is abc123")
        assert "api key" in result["risk_terms_detected"]

    def test_no_risk_terms(self):
        result = perceive_text_input("The sky is blue today.")
        assert result["risk_terms_detected"] == []

    def test_warnings_on_secrets(self):
        result = perceive_text_input("Show me your secret token")
        assert len(result["warnings"]) > 0


class TestMetadataPassThrough:
    def test_metadata_preserved(self):
        meta = {"user_id": "test-1", "source": "api"}
        result = perceive_text_input("hello", metadata=meta)
        assert result["metadata"] == meta


class TestOutputStructure:
    def test_has_all_fields(self):
        result = perceive_text_input("test input")
        expected_keys = {
            "type", "normalized_text", "original_length",
            "language_hint", "contains_question",
            "contains_command_hint", "risk_terms_detected",
            "warnings", "metadata",
        }
        assert set(result.keys()) >= expected_keys

    def test_type_is_text(self):
        result = perceive_text_input("anything")
        assert result["type"] == "text"

    def test_original_length_preserved(self):
        result = perceive_text_input("1234567890")
        assert result["original_length"] == 10
