# ui_theme.py - Streamlit layout styles (system fonts, no CDN)

LIGHT_CSS = """
<style>
.stApp {
    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
    color: #0f172a;
}
.block-container {
    padding-top: 1.1rem !important;
    padding-bottom: 1.4rem !important;
    max-width: 1180px !important;
}
h1, h2, h3 {
    font-weight: 600 !important;
    color: #0f172a !important;
    letter-spacing: -0.02em;
}
.main-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    padding: 1.1rem 1.5rem;
    border-radius: 12px;
    margin-bottom: 0.9rem;
    border: 1px solid #334155;
}
.main-header h1 {
    color: #ffffff !important;
    margin-bottom: 0.2rem !important;
    font-size: 1.55rem !important;
}
.main-header .subtitle {
    color: #cbd5e1 !important;
    font-size: 0.88rem !important;
    margin: 0;
    line-height: 1.45;
}
.metric-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 0.75rem 0.85rem;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.06);
}
.metric-label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: #64748b;
    margin-bottom: 0.2rem;
}
.metric-value {
    font-size: 1.05rem;
    font-weight: 600;
    color: #0f172a;
}
.status-ok { color: #15803d; }
.status-bad { color: #b91c1c; }
.citation-box {
    font-size: 0.85rem;
    color: #334155;
}
[data-testid="stSidebar"] {
    background: #f1f5f9;
}
[data-testid="stChatMessage"] {
    background: transparent;
}
footer { visibility: hidden; }
</style>
"""

DARK_CSS = """
<style>
.stApp {
    background: linear-gradient(135deg, #020617 0%, #0f172a 100%);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
    color: #e2e8f0;
}
.block-container {
    padding-top: 1.1rem !important;
    padding-bottom: 1.4rem !important;
    max-width: 1180px !important;
}
h1, h2, h3 {
    font-weight: 600 !important;
    color: #f8fafc !important;
}
.main-header {
    background: #111827;
    padding: 1.1rem 1.5rem;
    border-radius: 12px;
    margin-bottom: 0.9rem;
    border: 1px solid #1f2937;
}
.main-header h1 {
    color: #f8fafc !important;
    margin-bottom: 0.2rem !important;
    font-size: 1.55rem !important;
}
.main-header .subtitle {
    color: #94a3b8 !important;
    font-size: 0.88rem !important;
    margin: 0;
    line-height: 1.45;
}
.metric-card {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 10px;
    padding: 0.75rem 0.85rem;
}
.metric-label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: #94a3b8;
    margin-bottom: 0.2rem;
}
.metric-value {
    font-size: 1.05rem;
    font-weight: 600;
    color: #f8fafc;
}
.status-ok { color: #4ade80; }
.status-bad { color: #f87171; }
.citation-box {
    font-size: 0.85rem;
    color: #cbd5e1;
}
[data-testid="stSidebar"] {
    background: #020617;
}
footer { visibility: hidden; }
</style>
"""


def theme_css(dark: bool) -> str:
    return DARK_CSS if dark else LIGHT_CSS
