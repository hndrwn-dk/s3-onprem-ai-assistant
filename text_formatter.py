# text_formatter.py - Lightweight excerpt formatting


def smart_format_text(text: str, max_length: int = 600) -> str:
    """Collapse whitespace and trim to a readable excerpt."""
    if not text:
        return ""
    collapsed = " ".join(str(text).split())
    if len(collapsed) <= max_length:
        return collapsed
    trimmed = collapsed[:max_length].rsplit(" ", 1)[0]
    return trimmed + "..."
