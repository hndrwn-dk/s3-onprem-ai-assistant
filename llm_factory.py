# llm_factory.py - Hybrid LLM providers with invoke, stream, and health

from __future__ import annotations

import hashlib
import json
import threading
from typing import Any, Dict, Iterator, Optional

import requests

from config import (
    ANTHROPIC_API_KEY,
    ANTHROPIC_MODEL,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_DEPLOYMENT,
    AZURE_OPENAI_ENDPOINT,
    GROQ_API_KEY,
    GROQ_BASE_URL,
    GROQ_MODEL,
    LLM_PROVIDER,
    LLM_TIMEOUT_SECONDS,
    MODEL,
    NUM_PREDICT,
    OLLAMA_HOST,
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    OPENAI_COMPAT_API_KEY,
    OPENAI_COMPAT_BASE_URL,
    OPENAI_COMPAT_MODEL,
    OPENAI_MODEL,
    TEMPERATURE,
    TOP_K,
    TOP_P,
    VALID_PROVIDERS,
    default_model_for_provider,
)
from utils import logger

_clients: Dict[tuple, "LLMClient"] = {}
_lock = threading.Lock()


class LLMError(RuntimeError):
    """Raised when a provider cannot complete a request."""


def _normalize_provider(provider: Optional[str]) -> str:
    value = (provider or LLM_PROVIDER or "ollama").strip().lower()
    return value if value in VALID_PROVIDERS else "ollama"


def _trim_host(url: str) -> str:
    return (url or "").rstrip("/")


def normalize_ollama_base_url(url: Optional[str]) -> str:
    """Turn server bind addresses into a client URL requests can use."""
    value = (url or "http://localhost:11434").strip()
    if not value:
        value = "http://localhost:11434"
    if "://" not in value:
        value = "http://" + value
    rest = value.split("://", 1)[1]
    if rest.startswith("0.0.0.0"):
        value = value.replace("://0.0.0.0", "://127.0.0.1", 1)
    elif rest.startswith("[::]"):
        value = value.replace("://[::]", "://127.0.0.1", 1)
    return value.rstrip("/")


def resolve_settings(overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Merge env defaults with optional session overrides. Never logs secrets."""
    overrides = overrides or {}
    provider = _normalize_provider(overrides.get("provider"))
    settings: Dict[str, Any] = {
        "provider": provider,
        "temperature": float(overrides.get("temperature", TEMPERATURE)),
        "num_predict": int(overrides.get("num_predict", NUM_PREDICT)),
        "top_k": int(overrides.get("top_k", TOP_K)),
        "top_p": float(overrides.get("top_p", TOP_P)),
        "timeout": int(overrides.get("timeout", LLM_TIMEOUT_SECONDS)),
        "model": overrides.get("model") or default_model_for_provider(provider),
        "api_key": "",
        "base_url": "",
        "azure_endpoint": AZURE_OPENAI_ENDPOINT,
        "azure_deployment": AZURE_OPENAI_DEPLOYMENT,
        "azure_api_version": AZURE_OPENAI_API_VERSION,
    }

    if provider == "ollama":
        settings["base_url"] = normalize_ollama_base_url(
            overrides.get("base_url") or OLLAMA_HOST or "http://localhost:11434"
        )
        settings["model"] = overrides.get("model") or MODEL
    elif provider == "openai":
        settings["api_key"] = overrides.get("api_key") or OPENAI_API_KEY
        settings["base_url"] = _trim_host(
            overrides.get("base_url") or OPENAI_BASE_URL or "https://api.openai.com/v1"
        )
        settings["model"] = overrides.get("model") or OPENAI_MODEL
    elif provider == "azure":
        settings["api_key"] = overrides.get("api_key") or AZURE_OPENAI_API_KEY
        settings["azure_endpoint"] = _trim_host(
            overrides.get("azure_endpoint") or AZURE_OPENAI_ENDPOINT
        )
        settings["azure_deployment"] = (
            overrides.get("azure_deployment")
            or overrides.get("model")
            or AZURE_OPENAI_DEPLOYMENT
        )
        settings["azure_api_version"] = (
            overrides.get("azure_api_version") or AZURE_OPENAI_API_VERSION
        )
        settings["model"] = settings["azure_deployment"]
    elif provider == "anthropic":
        settings["api_key"] = overrides.get("api_key") or ANTHROPIC_API_KEY
        settings["model"] = overrides.get("model") or ANTHROPIC_MODEL
    elif provider == "groq":
        settings["api_key"] = overrides.get("api_key") or GROQ_API_KEY
        settings["base_url"] = _trim_host(overrides.get("base_url") or GROQ_BASE_URL)
        settings["model"] = overrides.get("model") or GROQ_MODEL
    elif provider == "openai_compat":
        settings["api_key"] = overrides.get("api_key") or OPENAI_COMPAT_API_KEY
        settings["base_url"] = _trim_host(
            overrides.get("base_url") or OPENAI_COMPAT_BASE_URL
        )
        settings["model"] = overrides.get("model") or OPENAI_COMPAT_MODEL or MODEL

    return settings


def _client_cache_key(settings: Dict[str, Any]) -> tuple:
    secret = settings.get("api_key") or ""
    digest = hashlib.sha256(secret.encode("utf-8")).hexdigest()[:16]
    return (
        settings["provider"],
        settings.get("model") or "",
        settings.get("base_url") or "",
        settings.get("azure_endpoint") or "",
        settings.get("azure_deployment") or "",
        digest,
        str(settings.get("temperature")),
        str(settings.get("num_predict")),
    )


class LLMClient:
    """Unified invoke/stream wrapper around Ollama and cloud providers."""

    def __init__(self, settings: Dict[str, Any]):
        self.settings = settings
        self.provider = settings["provider"]
        self.model = settings.get("model") or MODEL

    def __call__(self, prompt: str) -> str:
        return self.invoke(prompt)

    def invoke(self, prompt: str, system: Optional[str] = None) -> str:
        chunks = list(self.stream(prompt, system=system))
        return "".join(chunks).strip()

    def stream(self, prompt: str, system: Optional[str] = None) -> Iterator[str]:
        if self.provider == "ollama":
            yield from self._stream_ollama(prompt, system)
        elif self.provider == "anthropic":
            yield from self._stream_anthropic(prompt, system)
        elif self.provider == "azure":
            yield from self._stream_openai(prompt, system, azure=True)
        else:
            yield from self._stream_openai(prompt, system, azure=False)

    def _require_key(self) -> str:
        key = (self.settings.get("api_key") or "").strip()
        if self.provider != "ollama" and not key:
            raise LLMError(
                f"{self.provider} API key is not configured. "
                "Set it in .env or the Settings panel."
            )
        return key

    def _stream_ollama(self, prompt: str, system: Optional[str]) -> Iterator[str]:
        url = f"{self.settings['base_url']}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": self.settings["temperature"],
                "num_predict": self.settings["num_predict"],
                "top_k": self.settings["top_k"],
                "top_p": self.settings["top_p"],
            },
        }
        if system:
            payload["system"] = system
        try:
            with requests.post(
                url,
                json=payload,
                stream=True,
                timeout=self.settings["timeout"],
            ) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    token = data.get("response") or ""
                    if token:
                        yield token
                    if data.get("done"):
                        break
        except requests.RequestException as exc:
            raise LLMError(f"Ollama request failed: {exc}") from exc

    def _stream_openai(
        self, prompt: str, system: Optional[str], azure: bool
    ) -> Iterator[str]:
        try:
            from openai import AzureOpenAI, OpenAI
        except ImportError as exc:
            raise LLMError("The openai package is required for this provider.") from exc

        key = self._require_key()
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            if azure:
                endpoint = self.settings.get("azure_endpoint")
                deployment = self.settings.get("azure_deployment")
                if not endpoint or not deployment:
                    raise LLMError(
                        "Azure OpenAI requires AZURE_OPENAI_ENDPOINT and a deployment name."
                    )
                client = AzureOpenAI(
                    api_key=key,
                    azure_endpoint=endpoint,
                    api_version=self.settings.get("azure_api_version"),
                    timeout=self.settings["timeout"],
                )
                model = deployment
            else:
                kwargs: Dict[str, Any] = {
                    "api_key": key,
                    "timeout": self.settings["timeout"],
                }
                if self.settings.get("base_url"):
                    kwargs["base_url"] = self.settings["base_url"]
                client = OpenAI(**kwargs)
                model = self.model

            stream = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=self.settings["temperature"],
                max_tokens=self.settings["num_predict"],
                stream=True,
            )
            for event in stream:
                try:
                    delta = event.choices[0].delta.content
                except (AttributeError, IndexError):
                    delta = None
                if delta:
                    yield delta
        except LLMError:
            raise
        except Exception as exc:
            raise LLMError(f"{self.provider} request failed: {exc}") from exc

    def _stream_anthropic(self, prompt: str, system: Optional[str]) -> Iterator[str]:
        try:
            from anthropic import Anthropic
        except ImportError as exc:
            raise LLMError(
                "The anthropic package is required for this provider."
            ) from exc

        key = self._require_key()
        try:
            client = Anthropic(api_key=key, timeout=self.settings["timeout"])
            kwargs: Dict[str, Any] = {
                "model": self.model,
                "max_tokens": self.settings["num_predict"],
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.settings["temperature"],
            }
            if system:
                kwargs["system"] = system
            with client.messages.stream(**kwargs) as stream:
                for text in stream.text_stream:
                    if text:
                        yield text
        except LLMError:
            raise
        except Exception as exc:
            raise LLMError(f"Anthropic request failed: {exc}") from exc


def get_llm_client(overrides: Optional[Dict[str, Any]] = None) -> LLMClient:
    """Return a cached client for the resolved provider settings."""
    settings = resolve_settings(overrides)
    cache_key = _client_cache_key(settings)
    client = _clients.get(cache_key)
    if client is not None:
        return client
    with _lock:
        client = _clients.get(cache_key)
        if client is None:
            client = LLMClient(settings)
            _clients[cache_key] = client
            logger.info(
                "LLM client ready provider=%s model=%s",
                settings["provider"],
                settings.get("model"),
            )
        return client


def reset_clients() -> None:
    with _lock:
        _clients.clear()
    logger.info("LLM client cache reset")


def key_configured(settings: Optional[Dict[str, Any]] = None) -> bool:
    settings = settings or resolve_settings()
    if settings["provider"] == "ollama":
        return True
    return bool((settings.get("api_key") or "").strip())


def provider_health(overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Ping the selected provider. Never returns secret values."""
    from utils import check_vector_index_exists

    settings = resolve_settings(overrides)
    result: Dict[str, Any] = {
        "provider": settings["provider"],
        "model": settings.get("model") or "",
        "ok": False,
        "detail": "",
        "key_configured": key_configured(settings),
        "vector_index": check_vector_index_exists(),
    }

    provider = settings["provider"]
    timeout = min(int(settings.get("timeout") or 8), 8)

    try:
        if provider == "ollama":
            url = f"{settings['base_url']}/api/tags"
            resp = requests.get(url, timeout=timeout)
            resp.raise_for_status()
            result["ok"] = True
            result["detail"] = "Ollama is reachable"
            result["base_url"] = settings["base_url"]
        elif not result["key_configured"]:
            result["detail"] = f"{provider} API key is not configured"
        elif provider == "anthropic":
            resp = requests.get(
                "https://api.anthropic.com/v1/models",
                headers={
                    "x-api-key": settings["api_key"],
                    "anthropic-version": "2023-06-01",
                },
                timeout=timeout,
            )
            if resp.status_code < 400:
                result["ok"] = True
                result["detail"] = "Anthropic is reachable"
            else:
                result["detail"] = f"Anthropic health check failed ({resp.status_code})"
        elif provider == "azure":
            endpoint = settings.get("azure_endpoint")
            if not endpoint or not settings.get("azure_deployment"):
                result["detail"] = "Azure endpoint or deployment is not configured"
            else:
                url = (
                    f"{endpoint}/openai/models"
                    f"?api-version={settings.get('azure_api_version')}"
                )
                resp = requests.get(
                    url,
                    headers={"api-key": settings["api_key"]},
                    timeout=timeout,
                )
                if resp.status_code < 400:
                    result["ok"] = True
                    result["detail"] = "Azure OpenAI is reachable"
                else:
                    result["detail"] = f"Azure health check failed ({resp.status_code})"
        else:
            base = settings.get("base_url") or "https://api.openai.com/v1"
            url = f"{base}/models"
            resp = requests.get(
                url,
                headers={"Authorization": f"Bearer {settings['api_key']}"},
                timeout=timeout,
            )
            if resp.status_code < 400:
                result["ok"] = True
                result["detail"] = f"{provider} is reachable"
            else:
                result[
                    "detail"
                ] = f"{provider} health check failed ({resp.status_code})"
    except requests.RequestException as exc:
        result["detail"] = f"{provider} unreachable: {exc}"
    except Exception as exc:
        result["detail"] = f"Health check error: {exc}"

    return result
