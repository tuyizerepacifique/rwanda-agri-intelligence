"""
Theme: light/dark palettes, global CSS (--rai-* variables), sidebar helpers.

- Uses Streamlit's NATIVE sidebar collapse / expand controls (no custom JS,
  no st.rerun(), no visibility flags in session_state).
- NEVER hides <header> or [data-testid="stSidebarCollapsedControl"].
- Colors are exposed as CSS variables (--rai-*), so switching mode updates
  every styled element at once.
"""
import re
from pathlib import Path

import streamlit as st

# ---------------------------------------------------------------------------
# PALETTES
# ---------------------------------------------------------------------------
PALETTE = {
    "light": {
        "primary":      "#1B4332",
        "accent":       "#2D6A4F",
        "mid":          "#40916C",
        "light":        "#95D5B2",
        "pale":         "#D8F3DC",
        "warn":         "#D97706",
        "danger":       "#B91C1C",
        "text":         "#1F2937",
        "text_muted":   "#6B7280",
        "border":       "#E5E7EB",
        "bg":           "#FAFAF8",
        "bg_card":      "#FFFFFF",
        "bg_soft":      "#F9FAFB",
        "sidebar_bg":   "#FFFFFF",
        # badges
        "under_bg":     "#FEE2E2",
        "under_fg":     "#991B1B",
        "near_bg":      "#FEF3C7",
        "near_fg":      "#92400E",
        "over_bg":      "#D1FAE5",
        "over_fg":      "#065F46",
        # misc
        "insight_end":  "#ECFDF5",
        "shadow":       "rgba(0,0,0,0.08)",
    },
    "dark": {
        "primary":      "#B7E4C7",
        "accent":       "#52B788",
        "mid":          "#40916C",
        "light":        "#74C69D",
        "pale":         "#16281F",
        "warn":         "#FBBF24",
        "danger":       "#F87171",
        "text":         "#E5E7EB",
        "text_muted":   "#9CA3AF",
        "border":       "#2A3543",
        "bg":           "#0F1720",
        "bg_card":      "#1A2332",
        "bg_soft":      "#141C28",
        "sidebar_bg":   "#0B1219",
        # badges
        "under_bg":     "#3B1A1F",
        "under_fg":     "#FCA5A5",
        "near_bg":      "#3A2A12",
        "near_fg":      "#FCD34D",
        "over_bg":      "#12352A",
        "over_fg":      "#86EFAC",
        # misc
        "insight_end":  "#13221B",
        "shadow":       "rgba(0,0,0,0.45)",
    },
}

# Backward-compatible constant (light mode categorical sequence)
PLOTLY_SEQUENCE = ["#1B4332", "#2D6A4F", "#40916C", "#95D5B2", "#74C69D", "#52B788"]

PLOTLY_SEQUENCES = {
    "light": PLOTLY_SEQUENCE,
    "dark":  ["#B7E4C7", "#74C69D", "#52B788", "#40916C", "#2D6A4F", "#95D5B2"],
}

# Monotonic low -> high scales for continuous color axes
SEQUENTIAL_SCALES = {
    "light": ["#D8F3DC", "#95D5B2", "#40916C", "#1B4332"],
    "dark":  ["#1E3A2C", "#2D6A4F", "#52B788", "#B7E4C7"],
}

ASSETS = Path(__file__).parent.parent / "assets"

_FALLBACK_LOGO = (
    '<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" role="img" '
    'aria-label="Rwanda Agricultural Intelligence">'
    '<circle cx="32" cy="32" r="30" fill="#2D6A4F"/>'
    '<path d="M32 50V24" stroke="#D8F3DC" stroke-width="3" stroke-linecap="round"/>'
    '<path d="M32 30c-8 0-12-5-12-11 8 0 12 4 12 11zM32 30c8 0 12-5 12-11-8 0-12 4-12 11z'
    'M32 40c-7 0-10-4-10-9 7 0 10 3 10 9zM32 40c7 0 10-4 10-9-7 0-10 3-10 9z" '
    'fill="#95D5B2"/></svg>'
)


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
def _current_mode(mode: str | None = None) -> str:
    if mode is None:
        mode = st.session_state.get("theme_mode", "light")
    return mode if mode in PALETTE else "light"


def get_palette(mode: str | None = None) -> dict:
    """Palette dict for `mode` (defaults to the current session mode)."""
    return PALETTE[_current_mode(mode)]


def plotly_sequence(mode: str | None = None) -> list:
    """Categorical Plotly color sequence for `mode`."""
    return PLOTLY_SEQUENCES[_current_mode(mode)]


def get_scale(mode: str | None = None) -> list:
    """Monotonic light->dark (or dark->light) green scale for continuous axes."""
    return SEQUENTIAL_SCALES[_current_mode(mode)]


def apply_plotly_theme(fig, mode: str | None = None):
    """
    Make a Plotly figure match the active mode.

    Everything that carries text is set EXPLICITLY (axis ticks, axis titles,
    legend, colorbar, hover). Streamlit's own Plotly theme sets axis-specific
    tick colors that override the global font color, which made labels
    near-invisible in light mode when the browser/system was in dark mode.
    """
    p = get_palette(mode)
    text, border = p["text"], p["border"]

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans, sans-serif", color=text),
        legend=dict(font=dict(color=text), title=dict(font=dict(color=text))),
        hoverlabel=dict(
            bgcolor=p["bg_card"],
            bordercolor=border,
            font=dict(family="Plus Jakarta Sans, sans-serif", color=text),
        ),
    )

    axis_style = dict(
        gridcolor=border,
        zerolinecolor=border,
        linecolor=border,
        tickfont=dict(color=text),
        title=dict(font=dict(color=text)),
    )
    fig.update_xaxes(**axis_style)
    fig.update_yaxes(**axis_style)

    # Continuous color bars (px.bar with color=..., choropleth maps)
    fig.update_coloraxes(
        colorbar=dict(
            tickfont=dict(color=text),
            title=dict(font=dict(color=text)),
            outlinecolor=border,
        )
    )
    return fig


def _flatten(html: str) -> str:
    """Collapse HTML to one line so Markdown never treats it as a code block."""
    return " ".join(line.strip() for line in html.splitlines() if line.strip())


def svg_logo_inline() -> str:
    """Return assets/logo.svg as an inline, markdown-safe <svg> string (or a fallback)."""
    logo_path = ASSETS / "logo.svg"
    if not logo_path.exists():
        return _FALLBACK_LOGO
    try:
        svg = logo_path.read_text(encoding="utf-8")
    except OSError:
        return _FALLBACK_LOGO
    # Strip XML prolog, DOCTYPE and comments (they break inline HTML in markdown)
    svg = re.sub(r"<\?xml.*?\?>|<!DOCTYPE.*?>|<!--.*?-->", "", svg, flags=re.S)
    svg = _flatten(svg)
    return svg if "<svg" in svg else _FALLBACK_LOGO


# Native sidebar control selectors (covers Streamlit 1.30 -> latest)
_COLLAPSE_BTN = [
    'section[data-testid="stSidebar"] button[kind="header"]',
    '[data-testid="stSidebarCollapseButton"] button',
]
_EXPAND_BTN = [
    '[data-testid="stSidebarCollapsedControl"] button',
    '[data-testid="collapsedControl"] button',
    'button[data-testid="stExpandSidebarButton"]',
]


def _sel(selectors: list, suffix: str = "") -> str:
    return ",\n".join(f"{s}{suffix}" for s in selectors)


# ---------------------------------------------------------------------------
# THEME INJECTION
# ---------------------------------------------------------------------------
def inject_theme(mode: str = "light"):
    """Inject Google Font + global stylesheet (CSS variables) for the chosen mode."""
    mode = _current_mode(mode)
    p = PALETTE[mode]

    css_vars = " ".join(
        f"--rai-{k.replace('_', '-')}: {v};" for k, v in p.items()
    )
    all_btns = _COLLAPSE_BTN + _EXPAND_BTN

    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

:root {{
    {css_vars}
    color-scheme: {mode};
}}

/* ===================================================== */
/* GLOBAL                                                 */
/* ===================================================== */
html, body, .stApp {{
    background-color: var(--rai-bg) !important;
    color: var(--rai-text);
}}

/* Font: text elements ONLY — never span/div, or the Material icon font breaks */
.stApp, .stApp p, .stApp li, .stApp label, .stApp button, .stApp input,
.stApp textarea, .stApp select, .stApp h1, .stApp h2, .stApp h3, .stApp h4,
.stApp h5, .stApp td, .stApp th, [data-testid="stMarkdownContainer"] {{
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
}}
/* Restore Streamlit's icon font */
.stApp [data-testid="stIconMaterial"],
.stApp .material-symbols-rounded,
.stApp [class*="material-symbols"] {{
    font-family: 'Material Symbols Rounded', 'Material Icons' !important;
}}

/* Base text color — skips elements that set their own inline color */
.stApp :where(p, li, label, td, th, [data-testid="stMarkdownContainer"]):not([style*="color"]) {{
    color: var(--rai-text) !important;
}}
.stApp :where([data-testid="stCaptionContainer"], .stCaption) {{
    color: var(--rai-text-muted) !important;
}}

/* Hide ONLY menu, footer and toolbar. NEVER hide <header>. */
#MainMenu {{ visibility: hidden; }}
footer {{ visibility: hidden; }}
[data-testid="stToolbar"] {{ visibility: hidden; }}

/* Header stays in the DOM (it holds the sidebar controls) but is invisible */
header[data-testid="stHeader"] {{
    background: transparent !important;
    box-shadow: none !important;
    border: none !important;
}}

/* Guarantee the native open/close controls stay visible, even if a
   parent (e.g. the toolbar) is hidden in some Streamlit versions */
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"] button,
[data-testid="collapsedControl"] button,
button[data-testid="stExpandSidebarButton"],
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapseButton"] button {{
    visibility: visible !important;
}}

.block-container {{
    padding-top: 3rem;
    padding-bottom: 2rem;
    max-width: 1400px;
}}

/* Typography */
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5 {{
    color: var(--rai-primary) !important;
    letter-spacing: -0.02em;
}}
.stApp h1 {{ font-weight: 800; font-size: 2.1rem; }}
.stApp h2 {{ font-weight: 700; font-size: 1.5rem; margin-top: 1rem; }}
.stApp h3 {{ font-weight: 600; font-size: 1.15rem; }}

/* ===================================================== */
/* SIDEBAR                                                */
/* ===================================================== */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div:first-child,
[data-testid="stSidebarContent"] {{
    background: var(--rai-sidebar-bg) !important;
}}
section[data-testid="stSidebar"] {{
    border-right: 1px solid var(--rai-border);
}}
section[data-testid="stSidebar"] > div:first-child {{
    padding-top: 0.75rem;
    padding-bottom: 1rem;
}}

/* ---- Shared look for the native collapse / open buttons ---- */
{_sel(all_btns)} {{
    padding: 0 !important;
    border-radius: 50% !important;
    background: var(--rai-bg-card) !important;
    border: 1px solid var(--rai-border) !important;
    box-shadow: 0 2px 6px var(--rai-shadow) !important;
    color: var(--rai-accent) !important;
    font-size: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    transition: all 0.15s ease !important;
    cursor: pointer;
}}
{_sel(all_btns, ":hover")} {{
    background: var(--rai-pale) !important;
    border-color: var(--rai-light) !important;
}}

/* Collapse button (inside sidebar): 32x32 */
{_sel(_COLLAPSE_BTN)} {{
    width: 32px !important;
    height: 32px !important;
    min-width: 32px !important;
    min-height: 32px !important;
}}
/* Open button (shown when sidebar is collapsed, top-left): 40x40 */
{_sel(_EXPAND_BTN)} {{
    width: 40px !important;
    height: 40px !important;
    min-width: 40px !important;
    min-height: 40px !important;
}}

/* Hide whatever the native button renders (icon text / svg) ... */
{_sel(all_btns, " > *")} {{
    display: none !important;
}}
/* ... and draw a clean chevron instead */
{_sel(all_btns, "::after")} {{
    display: block;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700;
    line-height: 1;
    margin-top: -2px;
    color: var(--rai-accent);
}}
{_sel(_COLLAPSE_BTN, "::after")} {{ content: "\u2039"; font-size: 22px; }}
{_sel(_EXPAND_BTN, "::after")}   {{ content: "\u203A"; font-size: 26px; }}

/* ---- Sidebar nav (st.radio -> button-like items) ---- */
section[data-testid="stSidebar"] div[role="radiogroup"] {{
    display: flex;
    flex-direction: column;
    gap: 4px;
}}
section[data-testid="stSidebar"] div[role="radiogroup"] > label {{
    display: flex;
    align-items: center;
    width: 100%;
    padding: 9px 12px !important;
    border-radius: 8px !important;
    background: transparent;
    border: 1px solid transparent;
    color: var(--rai-text);
    font-weight: 500;
    font-size: 0.9rem;
    cursor: pointer;
    transition: all 0.15s ease;
}}
/* hide the radio circle */
section[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {{
    display: none !important;
}}
section[data-testid="stSidebar"] div[role="radiogroup"] > label p {{
    color: inherit !important;
    margin: 0;
    font-weight: inherit;
}}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {{
    background: var(--rai-bg-soft);
    border-color: var(--rai-border);
}}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {{
    background: var(--rai-pale) !important;
    color: var(--rai-primary) !important;
    font-weight: 600;
    border-color: var(--rai-light) !important;
}}

/* ---- Sidebar header / meta blocks ---- */
.rai-side-head {{ text-align: center; padding: 6px 0 10px 0; }}
.rai-logo {{
    width: 64px; height: 64px;
    margin: 0 auto;
    padding: 8px;
    box-sizing: border-box;
    border-radius: 16px;
    background: var(--rai-pale);
    border: 1px solid var(--rai-border);
}}
.rai-logo svg {{ width: 100%; height: 100%; display: block; }}
.rai-side-title {{
    color: var(--rai-primary);
    margin: 10px 0 2px 0;
    font-weight: 800;
    font-size: 1.02rem;
    line-height: 1.25;
    letter-spacing: -0.02em;
}}
.rai-side-sub {{
    color: var(--rai-text-muted);
    font-size: 0.68rem;
    margin-top: 6px;
    letter-spacing: 0.08em;
    font-weight: 600;
}}
.rai-hr {{
    border: none;
    border-top: 1px solid var(--rai-border);
    margin: 14px 0;
}}
.rai-meta {{
    font-size: 0.76rem;
    color: var(--rai-text-muted);
    line-height: 1.65;
}}
.rai-meta-h {{
    color: var(--rai-primary);
    font-weight: 700;
    font-size: 0.68rem;
    letter-spacing: 0.08em;
    margin-bottom: 6px;
}}
.rai-meta-b {{ margin-bottom: 14px; }}
.rai-toggle-label {{
    color: var(--rai-primary);
    font-weight: 700;
    font-size: 0.68rem;
    letter-spacing: 0.08em;
    margin: 4px 0 2px 0;
}}

/* ===================================================== */
/* CARDS, KPI, BADGES, DRIVERS, INSIGHT                   */
/* ===================================================== */
.rai-card {{
    background: var(--rai-bg-card);
    border-radius: 14px;
    padding: 22px 24px;
    border: 1px solid var(--rai-border);
    box-shadow: 0 1px 3px var(--rai-shadow);
    margin-bottom: 16px;
    color: var(--rai-text);
}}
.rai-kpi-label {{
    color: var(--rai-text-muted);
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 10px;
}}
.rai-kpi-value {{
    color: var(--rai-primary);
    font-size: 2.1rem;
    font-weight: 800;
    line-height: 1;
    letter-spacing: -0.03em;
}}
.rai-kpi-unit {{
    color: var(--rai-text-muted);
    font-size: 0.85rem;
    font-weight: 500;
    margin-left: 6px;
}}

.rai-badge {{
    display: inline-block;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
}}
.rai-badge-under {{ background: var(--rai-under-bg); color: var(--rai-under-fg); }}
.rai-badge-near  {{ background: var(--rai-near-bg);  color: var(--rai-near-fg); }}
.rai-badge-over  {{ background: var(--rai-over-bg);  color: var(--rai-over-fg); }}

.rai-insight {{
    background: linear-gradient(135deg, var(--rai-pale) 0%, var(--rai-insight-end) 100%);
    border-left: 4px solid var(--rai-accent);
    border-radius: 10px;
    padding: 18px 22px;
    margin: 18px 0;
    font-size: 0.95rem;
    line-height: 1.6;
    color: var(--rai-primary);
}}

.rai-driver {{
    padding: 10px 14px;
    margin-bottom: 6px;
    background: var(--rai-bg-soft);
    border-radius: 6px;
    font-size: 0.88rem;
    color: var(--rai-text);
    display: flex;
    justify-content: space-between;
    align-items: center;
}}
.rai-driver.pos {{ border-left: 3px solid var(--rai-accent); }}
.rai-driver.neg {{ border-left: 3px solid var(--rai-danger); }}
.rai-driver-name {{ font-weight: 500; }}
.rai-driver-val  {{ font-weight: 700; font-variant-numeric: tabular-nums; }}

/* ===================================================== */
/* WIDGETS                                                */
/* ===================================================== */

/* ---- Select boxes & inputs: background + border ---- */
.stApp div[data-baseweb="select"] > div,
.stApp div[data-baseweb="input"],
.stApp div[data-baseweb="base-input"],
.stApp textarea {{
    background: var(--rai-bg-card) !important;
    border-color: var(--rai-border) !important;
    border-radius: 8px !important;
}}

/* ---- Select boxes & inputs: text (the selected value!) ----
   Streamlit also sets -webkit-text-fill-color and opacity on the value
   text, so `color` alone can leave it invisible. Force all three. */
.stApp div[data-baseweb="select"],
.stApp div[data-baseweb="select"] *,
.stApp div[data-baseweb="input"] input,
.stApp div[data-baseweb="base-input"] input,
.stApp textarea {{
    color: var(--rai-text) !important;
    -webkit-text-fill-color: var(--rai-text) !important;
    opacity: 1 !important;
    caret-color: var(--rai-text);
}}
.stApp div[data-baseweb="select"] svg {{
    fill: var(--rai-text-muted) !important;
    color: var(--rai-text-muted) !important;
}}

/* ---- Dropdown menu (rendered in a portal outside .stApp) ---- */
div[data-baseweb="popover"],
div[data-baseweb="popover"] > div,
div[data-baseweb="popover"] ul,
div[data-baseweb="popover"] [data-baseweb="menu"],
div[data-baseweb="popover"] [role="listbox"],
[data-testid="stSelectboxVirtualDropdown"] {{
    background: var(--rai-bg-card) !important;
    border-color: var(--rai-border) !important;
}}
div[data-baseweb="popover"] li,
div[data-baseweb="popover"] li *,
div[data-baseweb="popover"] [role="option"],
div[data-baseweb="popover"] [role="option"] *,
[data-testid="stSelectboxVirtualDropdown"] * {{
    color: var(--rai-text) !important;
    -webkit-text-fill-color: var(--rai-text) !important;
    opacity: 1 !important;
}}
div[data-baseweb="popover"] li:hover,
div[data-baseweb="popover"] [role="option"]:hover,
div[data-baseweb="popover"] li[aria-selected="true"],
div[data-baseweb="popover"] [role="option"][aria-selected="true"] {{
    background: var(--rai-pale) !important;
}}

[data-testid="stMetricValue"] {{ color: var(--rai-primary) !important; }}
[data-testid="stMetricLabel"] p {{ color: var(--rai-text-muted) !important; }}

button[data-baseweb="tab"] p {{ color: var(--rai-text-muted) !important; font-weight: 600; }}
button[data-baseweb="tab"][aria-selected="true"] p {{ color: var(--rai-primary) !important; }}
div[data-baseweb="tab-highlight"] {{ background-color: var(--rai-accent) !important; }}
div[data-baseweb="tab-border"] {{ background-color: var(--rai-border) !important; }}

[data-testid="stExpander"] details {{
    background: var(--rai-bg-card);
    border: 1px solid var(--rai-border);
    border-radius: 10px;
}}
.stDataFrame {{
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid var(--rai-border);
}}
hr {{
    border: none;
    border-top: 1px solid var(--rai-border);
    margin: 20px 0;
}}

/* ===================================================== */
/* DOWNLOAD BUTTON                                        */
/* ===================================================== */
.stDownloadButton > button,
[data-testid="stDownloadButton"] > button {{
    background: var(--rai-bg-card) !important;
    color: var(--rai-primary) !important;
    border: 1px solid var(--rai-border) !important;
    border-radius: 10px !important;
    padding: 10px 18px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    box-shadow: 0 1px 3px var(--rai-shadow) !important;
    transition: all 0.15s ease !important;
}}
.stDownloadButton > button:hover,
[data-testid="stDownloadButton"] > button:hover {{
    background: var(--rai-pale) !important;
    color: var(--rai-primary) !important;
    border-color: var(--rai-light) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 3px 8px var(--rai-shadow) !important;
}}
.stDownloadButton > button:focus,
[data-testid="stDownloadButton"] > button:focus {{
    outline: none !important;
    box-shadow: 0 0 0 3px var(--rai-pale) !important;
}}
.stDownloadButton > button:active,
[data-testid="stDownloadButton"] > button:active {{
    background: var(--rai-light) !important;
    color: var(--rai-primary) !important;
    transform: translateY(0) !important;
}}
.stDownloadButton > button p,
[data-testid="stDownloadButton"] > button p,
.stDownloadButton > button span,
[data-testid="stDownloadButton"] > button span {{
    color: inherit !important;
    font-weight: inherit !important;
}}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# SIDEBAR COMPONENTS
# ---------------------------------------------------------------------------
def render_sidebar_header():
    """Sidebar top: inline SVG logo + project title + subtitle (both modes)."""
    html = f"""
    <div class="rai-side-head">
        <div class="rai-logo">{svg_logo_inline()}</div>
        <div class="rai-side-title">Rwanda Agricultural<br>Intelligence</div>
        <div class="rai-side-sub">NISR HACKATHON 2026</div>
    </div>
    """
    st.markdown(_flatten(html), unsafe_allow_html=True)


def _sync_theme_mode():
    """on_change callback: runs BEFORE the script reruns, so inject_theme()
    at the top of app.py already sees the new mode (no one-rerun lag)."""
    st.session_state["theme_mode"] = (
        "dark" if st.session_state.get("theme_toggle") else "light"
    )


def render_theme_toggle() -> str:
    """
    Sidebar light/dark toggle. Persists in st.session_state["theme_mode"].
    Returns "light" or "dark".
    """
    st.session_state.setdefault("theme_mode", "light")
    if "theme_toggle" not in st.session_state:
        st.session_state["theme_toggle"] = st.session_state["theme_mode"] == "dark"

    with st.sidebar:
        st.markdown(
            '<div class="rai-toggle-label">APPEARANCE</div>',
            unsafe_allow_html=True,
        )
        st.toggle("Dark mode", key="theme_toggle", on_change=_sync_theme_mode)

    _sync_theme_mode()
    return st.session_state["theme_mode"]


def render_sidebar_meta(row_count: int):
    """Sidebar metadata block — styled HTML only."""
    html = f"""
    <hr class="rai-hr">
    <div class="rai-meta">
        <div class="rai-meta-h">DATA SOURCE</div>
        <div class="rai-meta-b">
            NISR SAS 2025 microdata<br>
            {row_count:,} aggregated groups<br>
            62,497 plot observations
        </div>
        <div class="rai-meta-h">MODEL</div>
        <div class="rai-meta-b">
            XGBoost &middot; R&sup2; = 0.87<br>
            SHAP explainability
        </div>
        <div class="rai-meta-h">TRACK</div>
        <div>Track 1: Agricultural<br>Productivity</div>
    </div>
    <div class="rai-hr"></div>
    <div class="rai-meta" style="text-align:center; font-size:0.7rem;">
        <div style="color:var(--rai-text-muted); line-height:1.6;">
            Built by <b style="color:var(--rai-primary);">Pacifique TUYIZERE</b><br>
            for the <b style="color:var(--rai-primary);">NISR Big Data<br>Hackathon 2026</b>
        </div>
        <div style="color:var(--rai-text-muted); margin-top:8px; font-size:0.65rem;
                    letter-spacing:0.05em;">
            Data © NISR SAS 2025
        </div>
    </div>
    """
    st.markdown(_flatten(html), unsafe_allow_html=True)