# Recipe Output Format Design

**Status:** Draft
**Last Updated:** 2026-01-25
**Context:** Phase 0 Meal Planning Workflow

## 1. Goal & Philosophy
The goal is to produce recipe PDFs that are **glanceable**, **action-oriented**, and **flexible**. 
- **Glanceable:** A cook should be able to look at the sheet from 3 feet away and know exactly where they are in the process.
- **Action-Oriented:** Verbs and times should be prominent. Ingredients should be listed *when* they are needed.
- **Flexible:** The format should support linear single-pot meals as well as complex, multi-component meals with parallel timelines.

## 2. File Structure
Recipes are stored as Markdown (`.md`) files which are then converted to PDF via `pandoc` + `weasyprint`.

- **Path:** `phase0_flow/plans/<date>_<name>/recipes/<recipe-slug>.md`
- **Assets:** `phase0_flow/plans/<date>_<name>/recipes/recipes.css` (local override) or global default.

## 3. Markdown Structure
Each recipe file MUST follow this high-level structure:

1.  **Header:**
    -   `# Title 🥘` (H1 with Emoji)
    -   `*Subtitle/Vibe description in italics.*`

2.  **Mise-en-place Section (`### Mise-en-place`):**
    -   A bulleted list of prep tasks that *must* be completed before cooking starts.
    -   **Rule:** These are order-independent tasks (e.g., "Dice onion", "Rinse lentils").
    -   **Grouping:** Group by category (Produce, Protein, Pantry) or by station (Board, Sink).

3.  **Execution Table (The Core):**
    -   A Markdown table that drives the cooking process.
    -   **Constraint:** Horizontal rules between steps (standard row borders). No vertical borders.
    -   **Time Tracking:** The first column is always `Time` (e.g., `T-40`).

## 4. Table Variants
We support three primary table layouts depending on the complexity of the meal.

### Variant A: Standard (Linear)
*Best for: One-pot meals, soups, stews, or simple stir-frys.*

| Column Header | Width (Approx) | Content Rules |
| :--- | :--- | :--- |
| **Time** | 15% | `T-Minus` format (e.g., **T-30**). Bold. |
| **Ingredients** | 35% | List *only* ingredients added in this step. Include amounts. |
| **Action** | 50% | **Bold Verb** followed by instruction. |

**Markdown Example:**
```markdown
| Time | Ingredients | Action |
| :--- | :--- | :--- |
| **T-10** | 1 cup Peas | **Simmer:** Add peas. Cover. |
```

### Variant B: Parallel (Multi-Track)
*Best for: Meals with a Main + Side, or Oven + Stove workflows.*

| Column Header | Width (Approx) | Content Rules |
| :--- | :--- | :--- |
| **Time** | 15% | `T-Minus` format. |
| **Station 1** | 42% | e.g., "Pot (Heat)" or "Main". |
| **Station 2** | 42% | e.g., "Board (Prep)" or "Side Dish". |

**Markdown Example:**
```markdown
| Time | Pot (Heat) | Board (Prep) |
| :--- | :--- | :--- |
| **T-20** | **Simmer:** Cover pot. | Chop cucumber side. |
```

### Variant C: High-Density (Compact)
*Best for: Complex recipes needing maximum vertical efficiency.*

| Column Header | Width (Approx) | Content Rules |
| :--- | :--- | :--- |
| **Time** | 15% | `T-Minus` format. |
| **Action** | 20% | **ALL CAPS VERB** (e.g., **SAUTÉ**). |
| **Details** | 65% | Ingredients (bolded) mixed with instructions. |

**Markdown Example:**
```markdown
| Time | Action | Details |
| :--- | :--- | :--- |
| **T-05** | **WILT** | Stir in **2 cups Spinach**. Season w/ S&P. |
```

## 5. Styling (CSS) Specifications
The `recipes.css` controls the visual presentation.

-   **Fonts:** Sans-serif (Helvetica Neue/Arial). Clean, modern.
-   **Tables:**
    -   `border-collapse: collapse;`
    -   `th`: Light gray background (`#f8f9fa`), bold, bottom border (`2px solid #ddd`).
    -   `td`: Bottom border (`1px solid #eee`) only. **No vertical borders.**
    -   Padding: `4px 8px` for comfortable density.
-   **Headers:**
    -   H1: spans all columns (if multi-column layout used).
    -   H2/H3: Colored (Orange `#e67e22` for H2, Grey `#7f8c8d` for H3).
-   **Page Layout:**
    -   Margins: `1.5cm`.
    -   Footer: "Page X" centered.

## 6. Implementation Checklist
When generating a new recipe:
1.  [ ] Determine if the flow is Linear (Var A) or Parallel (Var B).
2.  [ ] Write the `### Mise-en-place` section first.
3.  [ ] Construct the table ensuring the `Time` column is chronological (counting down to T-00).
4.  [ ] verify `recipes.css` is present in the directory or logically linked.
