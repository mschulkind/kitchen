# Rules Library Triage

## Table of Contents
- [Overview](#overview)
- [Decisions Needed](#decisions-needed)
- [Next Steps](#next-steps)

## Overview

This file triages uncertainties and decisions arising from refactoring project-specific rules into a reusable .kilocode/rules/library/ structure. The goal is to ensure generic guidelines are centralized for reuse across projects, while preserving project-specific customizations.

## Decisions Needed

1. **Full Deduplication vs. References in Originals**:
   - During updates, some original files (e.g., auto-approver.md, response-style.md) retained their full content alongside library references due to the edit model's behavior. Should we:
     - Option A: Leave as-is for now, with references for clarity.
     - Option B: Edit originals to fully remove duplicated content, keeping only the reference and any project-specific additions (e.g., the personal note in markdown-docs.md).
     - Recommendation: Option B to avoid bloat, but confirm if any originals have unique project tweaks beyond what's already retained.

2. **Project-Specific Directories (scratch/, trash/, plans/, etc.)**:
   - Files like directory-usage.md reference kitchen-specific dirs (e.g., plans/ for meal planning, context/ for recipe datasets). The library/mode-permissions.md is purely generic.
     - Are scratch/ and trash/ standard reusable dirs, or kitchen-specific? If standard, add to a library/directory-standards.md.
     - Option A: Generalize further in a library file for common dirs.
     - Option B: Keep project-specific in original, no change needed.
     - Recommendation: Option B, as they seem tied to this workflow.

3. **Cross-References and Linking**:
   - Originals now link to library files (e.g., progress-log.md -> library/progress-log-automation.md). For reusability, should we:
     - Add an index.md in library/ listing all reusable rules with descriptions?
     - Ensure all links are relative and work across projects (e.g., [.kilocode/rules/library/...](.kilocode/rules/library/...))?
     - Recommendation: Yes to index.md for better discoverability.

4. **Potential Additional Splits/Merges**:
   - mobile-first.md and tech-stack.md are fully project-specific (React Native/Supabase for kitchen app). No generics extracted.
     - Is there value in extracting broad principles (e.g., general mobile UX, common tech patterns) to library/mobile-principles.md or library/tech-guidelines.md?
     - Option A: Leave as-is.
     - Option B: Extract if patterns apply broadly (e.g., offline handling, realtime collab).
     - Recommendation: Option A unless specific needs arise.

5. **Progress Log Automation Specificity**:
   - library/progress-log-automation.md generalized paths/examples, but ties to AI tools (update_todo_list, edit_file). Is this reusable outside Kilo Code/AI workflows?
     - Option A: Keep as AI-specific generic.
     - Option B: Broaden to general logging if applicable.
     - Recommendation: Option A, as it's tailored to this setup.

## Next Steps

- Review and approve/reject options above.
- If approved, perform additional edits (e.g., full dedup, add index.md).
- Once resolved, finalize with commit/push and remove this triage if no longer needed.

Fun fact: Did you know the first "library" was the Library of Ashurbanipal in ancient Mesopotamia around 7th century BCE? It housed over 30,000 clay tablets—talk about a reusable knowledge base, no git pushes required!