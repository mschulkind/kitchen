# Recipe Output Format Design

**Status:** Finalized
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

2.  **Ingredients & Prep (`### Ingredients & Prep`):**
    -   A container `div` holding two groups for side-by-side layout.
    -   **Group 1: Ready to Use:** Ingredients needing no prep.
    -   **Group 2: To Prep:** Ingredients needing knife work (`Item -> Action`).
    -   **Markdown Syntax:**
        ```html
        <div class="prep-container">
        <div class="prep-group">
        <span class="prep-category">Ready to Use</span>
        ... bulleted list ...
        </div>
        <div class="prep-group">
        <span class="prep-category">To Prep</span>
        ... bulleted list ...
        </div>
        </div>
        ```

3.  **Execution Table (The Core):**
    -   **Full Width** table with fixed columns.
    -   **Columns:** `Time | Ingredients | Action`
    -   **Ingredient Formatting:**
        -   Must use `<span>` tags (not `div`) to ensure visibility in PDF engine.
        -   **Structure:** `<span class="ing-item"><span class="amt">Amount</span><span class="name">Name</span></span>`
        -   **Visual:** Each item on a new line, amount right-aligned, name left-aligned.

## 4. Table Layout Variants
We support one primary "Standard" layout, but the CSS allows for variations if needed.

### Standard Layout (Verified)

| Column Header | Width (Fixed) | Content Rules |
| :--- | :--- | :--- |
| **Time** | 10% | `T-Minus` format (e.g., **T-30**). Bold. |
| **Ingredients** | 35% | List ingredients using the `.ing-item` span class. |
| **Action** | 55% | **Bold Verb** followed by instruction. |

**Markdown Example:**
```markdown
| Time | Ingredients | Action |
| :--- | :--- | :--- |
| **T-10** | <span class="ing-item"><span class="amt">1 cup</span><span class="name">Peas</span></span> | **Simmer:** Add peas. Cover. |
```

## 5. Styling (CSS) Specifications
The `recipes.css` controls the visual presentation.

-   **Fonts:** Sans-serif (Helvetica Neue/Arial). Clean, modern.
-   **Layout:**
    -   **Body:** Full width (`max-width: 100%`).
    -   **Prep Columns:** `.prep-container` uses `column-count: 2`.
-   **Tables:**
    -   `table-layout: fixed;` (Critical for column sizing).
    -   `width: 100%`.
    -   `border-collapse: collapse`.
    -   `td`: Top alignment, generous padding (`10px`).
-   **Column Widths:**
    -   Enforced via `width: XX% !important`.
-   **Ingredient Items (`.ing-item`):**
    -   `display: block;` (Forces newline).
    -   `.amt`: `display: inline-block; width: 35%; text-align: right;`.
    -   `.name`: `display: inline-block; width: 60%; text-align: left;`.

## 6. Implementation Checklist
When generating a new recipe:
1.  [ ] Write the `### Ingredients & Prep` section using the HTML wrapper.
2.  [ ] Construct the table ensuring the `Time` column is chronological.
3.  [ ] Format ALL table ingredients using the `<span class="ing-item">...</span>` pattern.
4.  [ ] Verify `recipes.css` includes the fixed-width rules.