"""
Convert assets/logo.svg to assets/icon.png for Streamlit page icon.
Uses svglib + reportlab (pure Python — no native Cairo needed).
Run ONCE.
"""
from pathlib import Path
from io import BytesIO

from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg

ROOT = Path(__file__).parent.parent
ASSETS = ROOT / "assets"
SVG_PATH = ASSETS / "logo.svg"
PNG_PATH = ASSETS / "icon.png"

if not SVG_PATH.exists():
    raise SystemExit(f" {SVG_PATH} not found. Create the SVG first.")

# Parse SVG → drawing
drawing = svg2rlg(str(SVG_PATH))

# Scale to 128×128 (Streamlit recommends ~32–128px)
target = 128
if drawing.width and drawing.height:
    scale = target / max(drawing.width, drawing.height)
    drawing.width *= scale
    drawing.height *= scale
    drawing.scale(scale, scale)

# Render to PNG
renderPM.drawToFile(drawing, str(PNG_PATH), fmt="PNG")

print(f" Created: {PNG_PATH}")
print(f"   Size: {PNG_PATH.stat().st_size:,} bytes")