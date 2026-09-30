# config.py (v3.0.0) - Hybrid providers and secure env loading

import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# Paths
DOCS_PATH = "docs"
VECTOR_INDEX_PATH = "s3_all_docs"
CHUNKS_PATH = "s3_all_chunks.pkl"
RECENT_QUESTIONS_FILE = "recent_questions.txt"
CACHE_DIR = "cache"

# Optional flattened bucket metadata file path (set via env to enable)
FLATTENED_TXT_PATH = os.getenv("FLATTENED_TXT_PATH", "")

# Embedding model
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
EMBED_DEVICE = os.getenv("EMBED_DEVICE", "cpu")
EMBED_BATCH_SIZE = int(os.getenv("EMBED_BATCH_SIZE", "64"))

# Performance settings
VECTOR_SEARCH_K = int(os.getenv("VECTOR_SEARCH_K", "3"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
CACHE_TTL_HOURS = int(os.getenv("CACHE_TTL_HOURS", "24"))
LLM_TIMEOUT_SECONDS = int(os.getenv("LLM_TIMEOUT_SECONDS", "20"))
VECTOR_LOAD_TIMEOUT_SECONDS = int(os.getenv("VECTOR_LOAD_TIMEOUT_SECONDS", "120"))

# Quick search settings
QUICK_SEARCH_MAX_RESULTS = int(os.getenv("QUICK_SEARCH_MAX_RESULTS", "10"))
QUICK_SEARCH_ENABLE_KEYWORD_FALLBACK = os.getenv(
    "QUICK_SEARCH_ENABLE_KEYWORD_FALLBACK", "false"
).lower() in ("1", "true", "yes")

# LLM model configuration (optimized for speed)
MODEL = os.getenv("MODEL", "phi3:mini")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))
NUM_PREDICT = int(os.getenv("NUM_PREDICT", "256"))
TOP_K = int(os.getenv("TOP_K", "5"))
TOP_P = float(os.getenv("TOP_P", "0.5"))

# Hybrid LLM providers. Default stays Ollama for air-gapped installs.
VALID_PROVIDERS = (
    "ollama",
    "openai",
    "azure",
    "anthropic",
    "groq",
    "openai_compat",
)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").strip().lower()
if LLM_PROVIDER not in VALID_PROVIDERS:
    LLM_PROVIDER = "ollama"

OLLAMA_HOST = os.getenv("OLLAMA_HOST") or os.getenv(
    "OLLAMA_BASE_URL", "http://localhost:11434"
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "")

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-20241022")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

OPENAI_COMPAT_API_KEY = os.getenv("OPENAI_COMPAT_API_KEY", "")
OPENAI_COMPAT_BASE_URL = os.getenv("OPENAI_COMPAT_BASE_URL", "")
OPENAI_COMPAT_MODEL = os.getenv("OPENAI_COMPAT_MODEL", "")

# Retrieval and chat
VALID_SEARCH_MODES = ("auto", "bucket", "vector", "fast_text")
SEARCH_MODE = os.getenv("SEARCH_MODE", "auto").strip().lower()
if SEARCH_MODE not in VALID_SEARCH_MODES:
    SEARCH_MODE = "auto"

CHAT_MEMORY_TURNS = int(os.getenv("CHAT_MEMORY_TURNS", "6"))
ENABLE_QUERY_REWRITE = os.getenv("ENABLE_QUERY_REWRITE", "true").lower() in (
    "1",
    "true",
    "yes",
)
ENABLE_FOLLOW_UPS = os.getenv("ENABLE_FOLLOW_UPS", "true").lower() in (
    "1",
    "true",
    "yes",
)
MAX_FOLLOW_UPS = int(os.getenv("MAX_FOLLOW_UPS", "3"))

# Security
API_KEY = os.getenv("API_KEY", "")
CORS_ORIGINS = [
    o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()
]

# FAISS loading safety
ALLOW_DANGEROUS_DESERIALIZATION = (
    os.getenv("ALLOW_DANGEROUS_DESERIALIZATION", "true").lower() == "true"
)


def default_model_for_provider(provider: str) -> str:
    """Return the configured default model name for a provider."""
    provider = (provider or "ollama").strip().lower()
    mapping = {
        "ollama": MODEL,
        "openai": OPENAI_MODEL,
        "azure": AZURE_OPENAI_DEPLOYMENT or OPENAI_MODEL,
        "anthropic": ANTHROPIC_MODEL,
        "groq": GROQ_MODEL,
        "openai_compat": OPENAI_COMPAT_MODEL or MODEL,
    }
    return mapping.get(provider, MODEL)
