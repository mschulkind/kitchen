#!/usr/bin/env python3
"""
Recipe Renderer - Converts recipe JSON to PDF using Jinja2 templates.

Usage:
    python render_recipe.py <recipe.json> [output.pdf]
    
Example:
    python render_recipe.py recipes/stew.json pdfs/stew.pdf
"""

import base64
import json
import re
import subprocess
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup
from weasyprint import HTML


# Template directory relative to this script
TEMPLATE_DIR = Path(__file__).parent.parent / "src/api/app/domain/recipes/templates"
EMOJI_DIR = TEMPLATE_DIR / "emoji"
TEMPLATE_NAME = "recipe.html.j2"

# Preload emoji images as base64 data URIs for inline rendering
_EMOJI_IMGS: dict[str, str] = {}
_FONT_CACHE: "TTFont | None" = None  # noqa: F821 — lazy-loaded


def _find_noto_color_emoji() -> Path | None:
    """Locate the Noto Color Emoji font via fc-match."""
    try:
        result = subprocess.run(
            ["fc-match", "--format=%{file}", "Noto Color Emoji"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout:
            p = Path(result.stdout.strip())
            if p.exists():
                return p
    except Exception:
        pass
    # Fallback to common paths
    for candidate in [
        Path("/usr/share/fonts/noto/NotoColorEmoji.ttf"),
        Path.home() / ".local/share/fonts/NotoColorEmoji.ttf",
    ]:
        if candidate.exists():
            return candidate
    return None


def _extract_emoji_png(char: str) -> bytes | None:
    """Extract a PNG bitmap for a single emoji from Noto Color Emoji (CBDT)."""
    global _FONT_CACHE
    try:
        from fontTools.ttLib import TTFont
    except ImportError:
        return None

    if _FONT_CACHE is None:
        font_path = _find_noto_color_emoji()
        if not font_path:
            _FONT_CACHE = False  # type: ignore[assignment]
            return None
        _FONT_CACHE = TTFont(str(font_path))

    if _FONT_CACHE is False:
        return None

    font = _FONT_CACHE
    if "CBDT" not in font:
        return None

    cmap = font.getBestCmap()
    glyph_name = cmap.get(ord(char))
    if not glyph_name:
        return None

    cbdt = font["CBDT"]
    for strike_idx, strike_data in enumerate(cbdt.strikeData):
        if glyph_name in strike_data:
            bitmap = strike_data[glyph_name]
            raw = bitmap.data
            # CBDT format 17: 5 bytes SmallGlyphMetrics + 4 bytes data-length + PNG
            data_len = int.from_bytes(raw[5:9], "big")
            return raw[9 : 9 + data_len]

    return None


def _load_emoji_imgs() -> None:
    """Load pre-baked emoji PNGs from disk as base64 data URIs."""
    if _EMOJI_IMGS:
        return
    for png_file in EMOJI_DIR.glob("*.png"):
        codepoint = int(png_file.stem, 16)
        char = chr(codepoint)
        b64 = base64.b64encode(png_file.read_bytes()).decode()
        _EMOJI_IMGS[char] = f"data:image/png;base64,{b64}"


# Regex matching emoji codepoints (and stripping U+FE0F variation selectors)
_EMOJI_RE = re.compile(
    r"([\u2300-\u23FF\u2600-\u27BF\u2B50"
    r"\U0001F300-\U0001FAFF])\uFE0F?"
)


def _emoji_to_img(match: re.Match) -> str:
    """Replace an emoji char with an inline color PNG <img> tag."""
    char = match.group(1)
    data_uri = _EMOJI_IMGS.get(char)
    if not data_uri:
        # Try extracting from system Noto Color Emoji font on the fly
        png_data = _extract_emoji_png(char)
        if png_data:
            b64 = base64.b64encode(png_data).decode()
            data_uri = f"data:image/png;base64,{b64}"
            _EMOJI_IMGS[char] = data_uri  # cache for reuse
        else:
            return ""  # strip unknown emoji — raw chars render giant via pango
    return (
        f'<img src="{data_uri}" '
        f'style="height:1em;vertical-align:-0.15em;display:inline" />'
    )


def emojify(text: str) -> Markup:
    """Replace emoji characters with inline PNG images."""
    return Markup(_EMOJI_RE.sub(_emoji_to_img, str(text)))


def load_recipe(json_path: Path) -> dict:
    """Load recipe from JSON file."""
    with open(json_path) as f:
        return json.load(f)


def render_html(recipe: dict) -> str:
    """Render recipe data to HTML using Jinja2 template."""
    _load_emoji_imgs()
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=False,  # We trust our recipe content
    )
    env.filters["emojify"] = emojify
    template = env.get_template(TEMPLATE_NAME)
    return template.render(recipe=recipe)


def render_pdf(html_content: str, output_path: Path) -> None:
    """Convert HTML to PDF using WeasyPrint."""
    HTML(string=html_content, base_url=str(TEMPLATE_DIR)).write_pdf(output_path)
    print(f"✅ Generated: {output_path}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    recipe_path = Path(sys.argv[1])
    if not recipe_path.exists():
        print(f"❌ Recipe not found: {recipe_path}")
        sys.exit(1)
    
    # Determine output path
    if len(sys.argv) >= 3:
        output_path = Path(sys.argv[2])
    else:
        output_path = recipe_path.with_suffix(".pdf")
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Load, render, and save
    recipe = load_recipe(recipe_path)
    html = render_html(recipe)
    render_pdf(html, output_path)


if __name__ == "__main__":
    main()
