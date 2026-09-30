# streamlit_ui.py (v4.0.0) - Chat UI with hybrid providers and citations

import os
import time
from pathlib import Path

import streamlit as st

from config import (
    DOCS_PATH,
    LLM_PROVIDER,
    SEARCH_MODE,
    TEMPERATURE,
    VALID_PROVIDERS,
    VALID_SEARCH_MODES,
    default_model_for_provider,
)
from conversation import ConversationMemory
from llm_factory import key_configured, provider_health
from model_cache import ModelCache
from prompts import SYSTEM_ASSISTANT
from query_engine import prepare_query, suggest_follow_ups, summarize_document
from response_cache import response_cache
from ui_theme import theme_css
from utils import logger
from validation import ValidationError, safe_filename, safe_query

st.set_page_config(
    page_title="S3 On-Premise AI Assistant",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

PROVIDER_LABELS = {
    "ollama": "Ollama (local)",
    "openai": "OpenAI",
    "azure": "Azure OpenAI",
    "anthropic": "Anthropic",
    "groq": "Groq",
    "openai_compat": "OpenAI-compatible",
}


def _init_state():
    defaults = {
        "messages": [],
        "pending_prompt": "",
        "last_meta": {},
        "health": None,
        "theme_dark": False,
        "provider": LLM_PROVIDER,
        "model": default_model_for_provider(LLM_PROVIDER),
        "api_key": "",
        "base_url": "",
        "azure_endpoint": "",
        "azure_deployment": "",
        "search_mode": SEARCH_MODE,
        "temperature": TEMPERATURE,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _overrides():
    overrides = {
        "provider": st.session_state.provider,
        "model": st.session_state.model,
        "temperature": float(st.session_state.temperature),
    }
    if st.session_state.api_key:
        overrides["api_key"] = st.session_state.api_key
    if st.session_state.base_url:
        overrides["base_url"] = st.session_state.base_url
    if st.session_state.azure_endpoint:
        overrides["azure_endpoint"] = st.session_state.azure_endpoint
    if st.session_state.azure_deployment:
        overrides["azure_deployment"] = st.session_state.azure_deployment
        overrides["model"] = st.session_state.azure_deployment
    return overrides


def _render_citations(citations):
    if not citations:
        return
    with st.expander("Sources", expanded=False):
        for item in citations:
            page = f" page {item.get('page')}" if item.get("page") is not None else ""
            st.markdown(
                f"**{item.get('filename', 'unknown')}**{page} "
                f"({item.get('origin', 'source')})"
            )
            st.caption(item.get("excerpt", ""))


def _run_query(question: str):
    started = time.time()
    try:
        question = safe_query(question)
    except ValidationError as exc:
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": str(exc),
                "source": "validation",
                "citations": [],
                "follow_ups": [],
            }
        )
        return

    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    memory = ConversationMemory.from_dicts(st.session_state.messages)
    overrides = _overrides()
    answer = ""
    source = "error"
    citations = []
    follow_ups = []

    with st.chat_message("assistant"):
        status = st.empty()
        status.caption("Retrieving documents...")
        try:
            prepared = prepare_query(
                question,
                search_mode=st.session_state.search_mode,
                memory=memory,
                llm_overrides=overrides,
            )
        except ValidationError as exc:
            status.empty()
            st.error(str(exc))
            return

        citations = [item.to_dict() for item in prepared.citations]
        source = prepared.source
        if prepared.cached_answer is not None:
            status.empty()
            answer = prepared.cached_answer
            st.markdown(answer)
        else:
            status.caption("Generating answer...")
            from llm_factory import get_llm_client

            llm = get_llm_client(overrides)

            def _tokens():
                for token in llm.stream(prepared.prompt, system=SYSTEM_ASSISTANT):
                    yield token

            try:
                streamed = st.write_stream(_tokens())
                answer = streamed if isinstance(streamed, str) else "".join(streamed)
            except Exception as exc:
                status.empty()
                logger.error("Stream failed: %s", exc)
                st.error(f"Generation failed: {exc}")
                return
            status.empty()
            if prepared.use_cache and answer:
                response_cache.set(prepared.question, answer, source)

        follow_ups = []
        if answer:
            follow_ups = suggest_follow_ups(question, answer, overrides)
        _render_citations(citations)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer if isinstance(answer, str) else str(answer),
            "source": source,
            "citations": citations,
            "follow_ups": follow_ups,
        }
    )
    st.session_state.last_meta = {
        "latency": time.time() - started,
        "source": source,
        "provider": st.session_state.provider,
    }
    ConversationMemory.from_dicts(st.session_state.messages).persist()


_init_state()

with st.sidebar:
    st.header("Settings")
    st.session_state.theme_dark = st.toggle(
        "Dark theme", value=st.session_state.theme_dark
    )

    provider = st.selectbox(
        "LLM provider",
        options=list(VALID_PROVIDERS),
        index=list(VALID_PROVIDERS).index(st.session_state.provider)
        if st.session_state.provider in VALID_PROVIDERS
        else 0,
        format_func=lambda value: PROVIDER_LABELS.get(value, value),
    )
    if provider != st.session_state.provider:
        st.session_state.provider = provider
        st.session_state.model = default_model_for_provider(provider)
        st.session_state.model_name = st.session_state.model
        ModelCache.reset_llm()
        st.rerun()

    st.session_state.model = st.text_input(
        "Model", value=st.session_state.model, key="model_name"
    )

    if provider != "ollama":
        st.session_state.api_key = st.text_input(
            "API key",
            value=st.session_state.api_key,
            type="password",
            help="Session only. Not written to disk. Prefer .env for servers.",
        )
    if provider in ("openai", "groq", "openai_compat", "ollama"):
        st.session_state.base_url = st.text_input(
            "Base URL",
            value=st.session_state.base_url,
            help="Optional. Ollama host or OpenAI-compatible endpoint.",
        )
    if provider == "azure":
        st.session_state.azure_endpoint = st.text_input(
            "Azure endpoint", value=st.session_state.azure_endpoint
        )
        st.session_state.azure_deployment = st.text_input(
            "Azure deployment", value=st.session_state.azure_deployment
        )

    st.session_state.search_mode = st.selectbox(
        "Search mode",
        options=list(VALID_SEARCH_MODES),
        index=list(VALID_SEARCH_MODES).index(st.session_state.search_mode)
        if st.session_state.search_mode in VALID_SEARCH_MODES
        else 0,
    )
    st.session_state.temperature = st.slider(
        "Temperature", 0.0, 1.0, float(st.session_state.temperature), 0.05
    )

    if st.button("Test connection", use_container_width=True):
        ModelCache.reset_llm()
        st.session_state.health = provider_health(_overrides())

    if st.session_state.health is None:
        st.session_state.health = provider_health(_overrides())

    health = st.session_state.health or {}
    ok = bool(health.get("ok"))
    st.markdown(
        f"**Provider:** {'Ready' if ok else 'Unavailable'}  \n"
        f"{health.get('detail') or 'No health details yet.'}"
    )
    st.caption(
        f"Key configured: {'yes' if key_configured(_overrides()) else 'no'} | "
        f"Vector index: {'yes' if health.get('vector_index') else 'no'}"
    )

    st.divider()
    st.subheader("Documents")
    uploads = st.file_uploader(
        "Upload vendor docs",
        type=["pdf", "txt", "md", "json", "docx"],
        accept_multiple_files=True,
    )
    if uploads and st.button("Save uploads", use_container_width=True):
        os.makedirs(DOCS_PATH, exist_ok=True)
        saved = 0
        for item in uploads:
            name = safe_filename(item.name)
            with open(os.path.join(DOCS_PATH, name), "wb") as handle:
                handle.write(item.getbuffer())
            saved += 1
        st.success(
            f"Saved {saved} file(s). Rebuild the index to include them in vector search."
        )

    if st.button("Rebuild index", use_container_width=True):
        with st.spinner("Building vector index..."):
            try:
                from build_embeddings_all import build_vector_index

                build_vector_index()
                ModelCache.reset_vector_store()
                ModelCache.get_vector_store()
                st.success("Knowledge base updated")
            except Exception as exc:
                st.error(f"Index rebuild failed: {exc}")

    doc_files = []
    docs_dir = Path(DOCS_PATH)
    if docs_dir.exists():
        doc_files = sorted(p.name for p in docs_dir.iterdir() if p.is_file())
    selected_doc = st.selectbox("Summarize document", options=["(none)"] + doc_files)
    if selected_doc != "(none)" and st.button(
        "Summarize selected", use_container_width=True
    ):
        with st.spinner("Summarizing..."):
            try:
                summary = summarize_document(selected_doc, _overrides())
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": summary,
                        "source": "summarize",
                        "citations": [
                            {
                                "filename": selected_doc,
                                "excerpt": "Full document summary",
                                "origin": "summarize",
                                "score": 1.0,
                            }
                        ],
                        "follow_ups": [],
                    }
                )
                st.rerun()
            except Exception as exc:
                st.error(str(exc))

    st.divider()
    col_a, col_b = st.columns(2)
    if col_a.button("Clear expired cache"):
        response_cache.clear_expired()
        st.success("Expired cache cleared")
    if col_b.button("Clear all cache"):
        response_cache.clear_all()
        st.success("All cache cleared")
    if st.button("New conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_meta = {}
        st.rerun()

st.markdown(theme_css(st.session_state.theme_dark), unsafe_allow_html=True)

st.markdown(
    """
    <div class="main-header">
        <h1>S3 On-Premise AI Assistant</h1>
        <p class="subtitle">Ask operational questions about your S3-compatible platform. Ollama stays the default; optional cloud keys are session-only or loaded from .env.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

cache_stats = response_cache.get_stats()
meta = st.session_state.last_meta
health = st.session_state.health or {}
m1, m2, m3, m4 = st.columns(4)
with m1:
    latency = meta.get("latency")
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">Last query</div>'
        f'<div class="metric-value">{latency:.2f}s</div></div>'
        if latency is not None
        else '<div class="metric-card"><div class="metric-label">Last query</div>'
        '<div class="metric-value">--</div></div>',
        unsafe_allow_html=True,
    )
with m2:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">Last source</div>'
        f'<div class="metric-value">{meta.get("source") or "--"}</div></div>',
        unsafe_allow_html=True,
    )
with m3:
    hit_rate = cache_stats.get("hit_rate", 0)
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">Cache hit rate</div>'
        f'<div class="metric-value">{hit_rate:.0%}</div></div>',
        unsafe_allow_html=True,
    )
with m4:
    cls = "status-ok" if health.get("ok") else "status-bad"
    label = "Ready" if health.get("ok") else "Check provider"
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">Provider</div>'
        f'<div class="metric-value {cls}">{label}</div></div>',
        unsafe_allow_html=True,
    )

for index, message in enumerate(st.session_state.messages):
    with st.chat_message(message.get("role", "assistant")):
        st.markdown(message.get("content", ""))
        if message.get("source"):
            st.caption(f"Source: {message['source']}")
        _render_citations(message.get("citations") or [])
        follow_ups = message.get("follow_ups") or []
        if message.get("role") == "assistant" and follow_ups:
            cols = st.columns(min(3, len(follow_ups)))
            for fu_index, suggestion in enumerate(follow_ups):
                if cols[fu_index].button(suggestion, key=f"hist_fu_{index}_{fu_index}"):
                    st.session_state.pending_prompt = suggestion
                    st.rerun()

prompt = st.chat_input("Ask about buckets, errors, or vendor procedures...")
if st.session_state.pending_prompt:
    prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = ""

if prompt:
    _run_query(prompt)
    st.rerun()
