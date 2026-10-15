"""
Reusable UI components.
All colors come from get_palette() so they follow the active light/dark mode.
"""
import streamlit as st

from src.theme import get_palette


ICONS = {
    "overview":  '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="9"/><rect x="14" y="3" width="7" height="5"/><rect x="14" y="12" width="7" height="9"/><rect x="3" y="16" width="7" height="5"/></svg>',
    "map":       '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>',
    "alert":     '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    "chart":     '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>',
    "leaf":      '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 20A7 7 0 0 1 4 13V5a2 2 0 0 1 2-2h8a7 7 0 0 1 7 7v10a2 2 0 0 1-2 2z"/></svg>',
    "arrow_up":  '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M7 17 17 7"/><path d="M7 7h10v10"/></svg>',
    "arrow_dn":  '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M7 7l10 10"/><path d="M17 7v10H7"/></svg>',
    "book":      '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>',
}


def page_header(title: str, subtitle: str = "", icon_key: str = "overview"):
    """Render a page title with icon and optional subtitle."""
    p = get_palette()
    icon = ICONS.get(icon_key, "")
    subtitle_html = (
        f'<p style="color:{p["text_muted"]}; font-size:1rem; margin-top:4px;">{subtitle}</p>'
        if subtitle else ""
    )
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:12px; margin-bottom:6px;">
        <div style="color:{p['accent']};">{icon}</div>
        <h1 style="margin:0; padding:0;">{title}</h1>
    </div>
    {subtitle_html}
    """, unsafe_allow_html=True)


def kpi_card(label: str, value: str, unit: str = "", accent: str = None):
    """One KPI card."""
    p = get_palette()
    accent_color = accent or p["accent"]
    unit_html = f'<span class="rai-kpi-unit">{unit}</span>' if unit else ""
    st.markdown(f"""
    <div class="rai-card" style="border-left:4px solid {accent_color};">
        <div class="rai-kpi-label">{label}</div>
        <div class="rai-kpi-value">{value}{unit_html}</div>
    </div>
    """, unsafe_allow_html=True)


def signal_badge(signal: str) -> str:
    cls = {
        "Under-performing": "rai-badge-under",
        "Near median": "rai-badge-near",
        "Over-performing": "rai-badge-over",
    }.get(signal, "rai-badge-near")
    return f'<span class="rai-badge {cls}">{signal}</span>'


def insight_box(text: str):
    st.markdown(f'<div class="rai-insight">{text}</div>', unsafe_allow_html=True)


def driver_row(name: str, value: float):
    p = get_palette()
    cls = "pos" if value > 0 else "neg"
    color = p["accent"] if value > 0 else p["danger"]
    arrow = ICONS["arrow_up"] if value > 0 else ICONS["arrow_dn"]
    st.markdown(f"""
    <div class="rai-driver {cls}">
        <span class="rai-driver-name">{name}</span>
        <span class="rai-driver-val" style="color:{color};">{arrow} {value:+.3f}</span>
    </div>
    """, unsafe_allow_html=True)