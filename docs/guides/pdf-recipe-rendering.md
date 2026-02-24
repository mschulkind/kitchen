# Recipe PDF Rendering Guide 📄🍳

> How the JSON → PDF pipeline works, what broke it, and how to keep it working.

## Architecture Overview

The recipe PDF pipeline is beautifully simple:

```
recipe.json  →  Jinja2 template  →  HTML  →  WeasyPrint  →  PDF
```

| Component | Path |
|-----------|------|
| Renderer script | `scripts/render_recipe.py` |
| Jinja2 template | `src/api/app/domain/recipes/templates/recipe.html.j2` |
| Font files | `src/api/app/domain/recipes/templates/fonts/` |
| Recipe JSONs | `phase0_flow/plans/<plan>/recipes/<name>.json` |
| Output PDFs | `phase0_flow/plans/<plan>/recipes/pdfs/<name>.pdf` |

### How to render a recipe

```bash
just render-all                    # renders all JSON recipes to PDF
uv run python scripts/render_recipe.py <input.json> <output.pdf>  # single recipe
```

## The Great Noto Emoji Incident of 2026 🐛💥

### What happened

A jailed agent added Noto Emoji font support (commit `5b26baa`) to make emoji render in recipe titles. It added:

1. An `@font-face` declaration for `NotoEmoji-Regular.ttf`
2. `"Noto Emoji"` as a fallback in the body `font-family` stack

This **completely broke text shaping** for all regular characters — numbers, punctuation, and symbols got spaced apart like they were in a long-distance relationship. 💔

```
Expected: T-40    13.5 oz can    1/2 tsp
Got:      T- 4  0    1  3 . 5  oz can    1 / 2  tsp
```

### Root cause

WeasyPrint uses **Pango** for text layout. When `"Noto Emoji"` was in the `font-family` fallback chain, Pango consulted the emoji font's glyph metrics for characters like digits and punctuation — which exist in the emoji font but have **wrong advance widths**. This caused Pango to space characters based on emoji metrics instead of the primary font's metrics.

Fun fact: this is a well-known footgun with emoji fonts! They define glyphs for ASCII characters (for emoji sequences like keycap digits) but with metrics optimized for emoji display, not body text. 🤓

### The fix

```css
/* ✅ GOOD: unicode-range restricts the font to emoji codepoints only */
@font-face {
    font-family: "Noto Emoji";
    src: url("fonts/NotoEmoji-Regular.ttf");
    unicode-range: U+200D, U+2300-23FF, U+2600-27BF, U+2B50, U+FE00-FE0F, U+1F000-1FAFF;
}

/* ✅ GOOD: emoji font NOT in the font-family stack */
body {
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
}
```

```css
/* ❌ BAD: emoji font in the fallback chain poisons ALL text metrics */
body {
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif, "Noto Emoji";
}
```

### ⚠️ Rule for future agents

**NEVER put an emoji font in a body-level `font-family` declaration.** Use `unicode-range` in the `@font-face` to restrict it to emoji codepoints. This lets the font activate only when actual emoji characters are encountered, without contaminating metrics for regular text.

## The Nix LD_LIBRARY_PATH Trap 🪤

### What happened

The justfile had an `LD_LIBRARY_PATH` export that globbed nix store paths to find pango/cairo/harfbuzz shared libraries:

```bash
# This glob is DANGEROUS
ls /nix/store/*/lib/libharfbuzz*.so
```

This matched `/nix/store/.../bin-path-links/lib/` which bundles **glibc** (`libc.so.6`). Loading nix's glibc alongside the system glibc causes an **ABI conflict → stack smashing crash** (`*** stack smashing detected ***`).

### The fix

Removed the nix `LD_LIBRARY_PATH` entirely. System-installed libs (Arch Linux packages) provide everything WeasyPrint needs:

| Library | System Version | Status |
|---------|---------------|--------|
| pango | 1.57.0 | ✅ Works |
| harfbuzz | 12.3.2 | ✅ Works |
| cairo | 1.18.4 | ✅ Works |
| glib2 | 2.86.4 | ✅ Works |
| fontconfig | 2.16.2 | ✅ Works |

### ⚠️ Rule for future agents

**Do NOT add nix store paths to `LD_LIBRARY_PATH`** on this system. The nix store `bin-path-links` directory contains a glibc that conflicts with the system glibc. System packages provide all required native libraries for WeasyPrint.

## Template Layout Notes 📐

### Ingredient boxes

Each ingredient gets its **own grey box** (`.ing-box`). This prevents horizontal overflow when a step has many ingredients — they just stack vertically instead.

```html
<!-- ✅ GOOD: one box per ingredient -->
{% for ing in step.ingredients %}
<div class="ing-box">
    <span class="amt">{{ ing.amount }}</span>
    <span class="name">{{ ing.name }}</span>
</div>
{% endfor %}
```

```html
<!-- ❌ BAD: all ingredients crammed into one box -->
<div class="ing-box">
    {% for ing in step.ingredients %}
    <div class="ing-row">...</div>
    {% endfor %}
</div>
```

### Debugging tips

1. **Render to HTML first** to inspect in a browser: change `render_recipe.py` to write the intermediate HTML
2. **Minimal repro**: if text looks broken, test with a minimal HTML file using just `font-family: sans-serif` to isolate font issues from template issues
3. **Compare against known-good**: `phase0_flow/plans/2026-02-22_chicken-thigh-stk/recipes/pdfs/golden-curry-coconut-roots.pdf` is a reference
4. **WeasyPrint version**: venv uses WeasyPrint 67.0 (system has 68.1) — both work, the venv version is pinned in `pyproject.toml`

## Diagnostic Commands

```bash
# Render a single recipe
uv run python scripts/render_recipe.py input.json output.pdf

# Check WeasyPrint version
uv run python -c "import weasyprint; print(weasyprint.__version__)"

# Check system native libs
pango-view --version
pkg-config --modversion harfbuzz cairo

# Verify no nix glibc contamination
ldd $(python -c "import cffi; print(cffi.__file__)") | grep libc
```
