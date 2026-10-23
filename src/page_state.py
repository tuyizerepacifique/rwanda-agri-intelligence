"""
Loading state manager for smooth page transitions.
"""
import streamlit as st
from .theme import PALETTE


def show_loading(message: str = "Loading..."):
    """Show a styled loading indicator."""
    return st.markdown(f"""
    <div style="display:flex; align-items:center; justify-content:center;
                padding:60px 20px; flex-direction:column; gap:16px;">
        <div class="rai-spinner"></div>
        <div style="color:{PALETTE['text_muted']}; font-size:0.9rem;
                    font-weight:500;">{message}</div>
    </div>
    <style>
    .rai-spinner {{
        width:44px; height:44px;
        border:3px solid {PALETTE['pale']};
        border-top-color: {PALETTE['accent']};
        border-radius:50%;
        animation: rai-spin 0.8s linear infinite;
    }}
    @keyframes rai-spin {{
        to {{ transform: rotate(360deg); }}
    }}
    </style>
    """, unsafe_allow_html=True)


def page_content(render_fn, *args, **kwargs):
    """
    Wrap a page render function with a loading state.
    Uses an empty placeholder to swap spinner → content.
    """
    placeholder = st.empty()
    with placeholder.container():
        show_loading("Preparing dashboard...")

    # Small delay for smoothness
    import time
    time.sleep(0.15)

    placeholder.empty()
    render_fn(*args, **kwargs)