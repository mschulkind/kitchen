#!/usr/bin/env python3
"""
Recipe Renderer - Converts recipe JSON to PDF using Jinja2 templates.

Usage:
    python render_recipe.py <recipe.json> [output.pdf]
    
Example:
    python render_recipe.py recipes/stew.json pdfs/stew.pdf
"""

import json
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML


# Template directory relative to this script
TEMPLATE_DIR = Path(__file__).parent.parent / "src/api/app/domain/recipes/templates"
TEMPLATE_NAME = "recipe.html.j2"


def load_recipe(json_path: Path) -> dict:
    """Load recipe from JSON file."""
    with open(json_path) as f:
        return json.load(f)


def render_html(recipe: dict) -> str:
    """Render recipe data to HTML using Jinja2 template."""
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=False,  # We trust our recipe content
    )
    template = env.get_template(TEMPLATE_NAME)
    return template.render(recipe=recipe)


def render_pdf(html_content: str, output_path: Path) -> None:
    """Convert HTML to PDF using WeasyPrint."""
    HTML(string=html_content).write_pdf(output_path)
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
