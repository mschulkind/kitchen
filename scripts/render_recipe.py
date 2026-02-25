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


def _load_emoji_imgs() -> None:
    """Load all emoji PNGs from the emoji directory as base64 data URIs."""
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
        return char  # No image available, keep the character
    return (
        f'<img src="{data_uri}" '
        f'style="height:1em;vertical-align:-0.15em;display:inline" />'
    )


def emojify(text: str) -> Markup:
    """Replace emoji characters with inline SVG images."""
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
