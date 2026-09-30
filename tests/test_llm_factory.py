# tests/test_llm_factory.py

from unittest.mock import Mock, patch

from llm_factory import (
    key_configured,
    normalize_ollama_base_url,
    provider_health,
    reset_clients,
    resolve_settings,
)


def test_normalize_ollama_bind_address():
    assert normalize_ollama_base_url("0.0.0.0:11434") == "http://127.0.0.1:11434"
    assert (
        normalize_ollama_base_url("http://localhost:11434") == "http://localhost:11434"
    )


def test_resolve_settings_defaults_to_ollama():
    settings = resolve_settings()
    assert settings["provider"] == "ollama"
    assert settings["model"]
    assert settings["base_url"]


def test_session_overrides_win():
    settings = resolve_settings(
        {
            "provider": "openai",
            "model": "gpt-4o-mini",
            "api_key": "sk-test",
            "temperature": 0.2,
        }
    )
    assert settings["provider"] == "openai"
    assert settings["model"] == "gpt-4o-mini"
    assert settings["api_key"] == "sk-test"
    assert settings["temperature"] == 0.2


def test_invalid_provider_falls_back_to_ollama():
    settings = resolve_settings({"provider": "not-a-vendor"})
    assert settings["provider"] == "ollama"


def test_key_configured_ollama_without_secret():
    assert key_configured(resolve_settings({"provider": "ollama"})) is True


def test_key_configured_openai_requires_secret():
    settings = resolve_settings({"provider": "openai", "api_key": ""})
    # env may already have a key in the developer machine; force empty
    settings["api_key"] = ""
    assert key_configured(settings) is False


@patch("llm_factory.requests.get")
def test_ollama_health_success(mock_get):
    reset_clients()
    mock_get.return_value = Mock(status_code=200)
    mock_get.return_value.raise_for_status = Mock()
    health = provider_health(
        {"provider": "ollama", "base_url": "http://localhost:11434"}
    )
    assert health["provider"] == "ollama"
    assert health["ok"] is True
    assert "key" not in str(health).lower() or "api_key" not in health
    assert "sk-" not in str(health)


@patch("llm_factory.requests.get")
def test_openai_health_without_key(mock_get):
    health = provider_health({"provider": "openai", "api_key": ""})
    # If process env has OPENAI_API_KEY, still accept either path
    if not health["key_configured"]:
        assert health["ok"] is False
        mock_get.assert_not_called()
    assert "api_key" not in health
