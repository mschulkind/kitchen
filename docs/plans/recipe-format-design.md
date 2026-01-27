# Recipe Output Format Design 🍳

**Status:** ✅ Finalized
**Last Updated:** 2026-01-25
**Context:** Phase 0 Meal Planning Workflow

---

## 1. Goal & Philosophy

The goal is to produce recipe PDFs that are **glanceable**, **action-oriented**, and **flexible**.

- **Glanceable:** A cook should be able to look at the sheet from 3 feet away and know exactly where they are in the process.
- **Action-Oriented:** Verbs and times should be prominent. Ingredients should be listed *when* they are needed.
- **Flexible:** The format should support linear single-pot meals as well as complex, multi-component meals with parallel timelines.

---

## 2. Architecture Overview 🏗️

### Data-Driven Rendering

Recipes are defined as **JSON data** and rendered to HTML/PDF using a **Jinja2 template**:

```
recipe.json  →  render_recipe.py  →  recipe.html.j2  →  WeasyPrint  →  recipe.pdf
```

### File Locations

| File Type | Location |
|-----------|----------|
| **Recipe JSON** | `phase0_flow/plans/<date>_<name>/recipes/<slug>.json` |
| **Template** | `src/api/app/domain/recipes/templates/recipe.html.j2` |
| **Schema** | `src/api/app/domain/recipes/schema/recipe.schema.json` |
| **Renderer** | `scripts/render_recipe.py` |
| **Output PDF** | `phase0_flow/plans/<date>_<name>/recipes/pdfs/<slug>.pdf` |

### Commands

```bash
# Render a single recipe
just recipe <recipe-name>

# Render all JSON recipes in current plan
just render-all
```

---

## 3. Recipe JSON Schema 📋

### Structure

```json
{
  "title": "Recipe Name",
  "emoji": "🍅",
  "subtitle": "A tasty description.",
  "servings": 6,
  "total_time_minutes": 40,
  "prep": {
    "ready_to_use": [
      { "amount": "1 cup", "name": "Quinoa", "note": "rinsed" }
    ],
    "knife_work": [
      { "amount": "1 large", "name": "Onion", "prep": "Dice" }
    ]
  },
  "steps": [
    {
      "minutes_before_done": 40,
      "duration_minutes": 7,
      "action_name": "Sauté Base",
      "action_description": "Heat oil in pot...",
      "ingredients": [
        { "amount": "1 tbsp", "name": "Olive Oil" }
      ],
      "meanwhile": {
        "ingredients": "Cheese + Broth",
        "action": "Blend until smooth."
      }
    }
  ]
}
```

### Key Fields

| Field | Required | Description |
|-------|----------|-------------|
| `title` | ✅ | Recipe name |
| `emoji` | ❌ | Optional emoji for title |
| `subtitle` | ❌ | Tagline or description |
| `prep.ready_to_use` | ✅ | Ingredients needing no prep |
| `prep.knife_work` | ✅ | Ingredients needing cutting |
| `steps` | ✅ | Execution steps in countdown order |
| `steps[].minutes_before_done` | ✅ | T-minus (40 = T-40, 0 = done) |
| `steps[].meanwhile` | ❌ | Optional parallel task |

---

## 4. Visual Design Decisions 🎨

### Final Format: "Subtle Background" Style

After iterating through multiple variants, we chose the **Subtle Background** approach:

- **Ingredients Column:** Light grey box (`#f5f5f5`) containing all ingredients for each step
- **Amounts:** Orange (`#e67e22`) bold text, right-aligned
- **Names:** Regular text, left-aligned
- **Layout:** HTML table for alignment, CSS Grid for header

### Color Palette

| Element | Color | Hex |
|---------|-------|-----|
| Headers | Dark blue | `#2c3e50` |
| Amounts | Orange | `#e67e22` |
| Body text | Dark grey | `#333333` |
| Grey backgrounds | Light grey | `#f5f5f5` |
| Meanwhile block | Light blue | `#e8f4fd` |
| Meanwhile border | Blue | `#3498db` |

### Typography

- **Font:** Helvetica Neue, Helvetica, Arial, sans-serif
- **Body:** 10pt, 1.4 line-height
- **Headers:** 20pt (h1), 12pt (h3), uppercase with letter-spacing
- **Countdown times:** 14pt bold

---

## 5. Execution Steps Layout 📊

### Table Structure (not CSS Grid)

We use an HTML `<table>` for execution steps to ensure proper column alignment across all rows:

```html
<table class="exec-table">
  <thead>
    <tr>
      <th class="col-time">Time</th>
      <th class="col-ing">Ingredients</th>
      <th class="col-action">Action</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td class="col-time">...</td>
      <td class="col-ing">...</td>
      <td class="col-action">...</td>
    </tr>
  </tbody>
</table>
```

### Column Widths

| Column | Width | Contents |
|--------|-------|----------|
| Time | 70px | T-XX countdown + duration |
| Ingredients | 180px | Grey box with amounts/names |
| Action | Remaining (1fr) | Bold verb + instructions |

### Page Break Prevention

Rows use `break-inside: avoid` to prevent splitting across pages.

---

## 6. Time Column Display ⏱️

The Time column shows **two pieces** stacked vertically:

| Element | Purpose | Example | Style |
|---------|---------|---------|-------|
| **Countdown** | Time until meal is done | `T-20` | Large, bold, dark |
| **Duration** | How long this step takes | `⏱ 7 min` | Small, orange |

At `T-00`, the duration shows "🍽️ Done!" instead.

### Template:

```html
<div class="time-countdown">T-{{ "%02d"|format(step.minutes_before_done) }}</div>
<div class="time-duration">
  {% if step.minutes_before_done == 0 %}🍽️ Done!
  {% else %}⏱ {{ step.duration_minutes }} min{% endif %}
</div>
```

---

## 7. Ingredients Column - Grey Box Style 🥕

All ingredients for a step are contained in a unified grey box:

```html
<div class="ing-box">
  {% for ing in step.ingredients %}
  <div class="ing-row">
    <span class="amt">{{ ing.amount }}</span>
    <span class="name">{{ ing.name }}</span>
  </div>
  {% endfor %}
</div>
```

### CSS:

```css
.col-ing {
    width: 180px;
    min-width: 180px;
}

.ing-box {
    background: #f5f5f5;
    padding: 6px 8px;
    border-radius: 4px;
}

.ing-row {
    display: flex;
    padding: 2px 0;
    border-bottom: 1px solid #e8e8e8;
    white-space: nowrap;
}

.amt {
    flex: 0 0 60px;
    text-align: right;
    font-weight: bold;
    color: #e67e22;
    padding-right: 8px;
}
```

---

## 8. Meanwhile Block 📋

For parallel tasks (e.g., blending cheese while chicken cooks):

```html
<div class="meanwhile-block">
  <div class="meanwhile-header">MEANWHILE</div>
  <div class="meanwhile-content">
    <span class="meanwhile-ing">{{ step.meanwhile.ingredients }}</span>
    → {{ step.meanwhile.action }}
  </div>
</div>
```

### Styling:

- Light blue background (`#e8f4fd`)
- Blue left border (4px `#3498db`)
- Clipboard emoji prefix (📋)

---

## 9. Implementation Checklist ✅

When creating a new recipe:

1. [ ] Create recipe JSON following the schema
2. [ ] Include all ingredients in both `prep` and `steps` sections
3. [ ] Use T-minus format for `minutes_before_done` (40, 33, 32, 20, 10, 5, 0)
4. [ ] Add `meanwhile` objects for parallel tasks
5. [ ] Run `just recipe <name>` to generate PDF
6. [ ] Verify columns align and no rows split across pages
7. [ ] Check grey boxes contain all text (no overflow)

---

## 10. Design Iteration History 📜

### Variants Explored

| Variant | Approach | Result |
|---------|----------|--------|
| **A: Subtle Background** | Grey box per step | ✅ **CHOSEN** |
| B: Vertical Divider | Orange pipe between amt/name | Rejected - alignment issues |
| C: Pill Tags | Orange pills on names | Rejected - too busy |

### Key Learnings

1. **Tables beat CSS Grid** for consistent column alignment across rows
2. **white-space: nowrap** prevents awkward ingredient wrapping
3. **min-width on columns** prevents overflow from grey boxes
4. **Meanwhile as inline block** (not separate row) keeps context together

---

## 11. Fun Fact 🐋

Did you know? The "mise en place" approach used in this format comes from French culinary tradition, literally meaning "putting in place." Professional kitchens have used this technique since the 19th century to ensure smooth service. 

Our digital version adds the countdown timer element, so you're basically running your kitchen like a NASA mission control! 🚀
