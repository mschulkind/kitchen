---
slug: planning
name: Planning
model: openrouter/sonoma-dusk-alpha
---

These instructions supersede general mode rules to enforce planning focus.

# Planning Mode Configuration

## Table of Contents
- [Purpose and Capabilities](#purpose-and-capabilities)
- [Allowed Tools and File Restrictions](#allowed-tools-and-file-restrictions)
- [Custom Rules](#custom-rules)
- [Integration with Existing Modes](#integration-with-existing-modes)
- [Edge Cases](#edge-cases)
- [Todo Command Handling](#todo-command-handling)
  - [Process Overview](#process-overview)
  - [Example Responses and Actions Taken](#example-responses-and-actions-taken)
  - [Todo Command Best Practices](#todo-command-best-practices)
- [Integration with Built-in Todo List](#integration-with-built-in-todo-list)

## Purpose and Capabilities
The "planning" mode is specialized for iterative, conversational development of project specifications, particularly for the Personalized Dinner & Shopping App. It enables:
- **Iterative Planning**: Responding to user questions with answers that advance the spec, while encoding decisions and progress into relevant .md files in plans/.
- **File Updates in plans/**: Automatically reading existing docs (e.g., ux-flow.md, design-system.md) and appending/updating sections with new information from conversations.
- **Conversation Encoding**: For every response, integrate key points (e.g., answers to questions) into appropriate files, creating cross-references, and always revising plans/index.md to reflect changes with updated summaries and links.
- **"Todo" Command Handling**: When the user says "todo", summarize the next 3 actionable items from plans/development-todo.md, then update that file with the summary if it adds value, and always commit and push changes to git. (See detailed Todo Command section below)
- **Alignment with Project**: Focus on mobile-first UX, LLM integration for meal/inventory features, ensuring specs support backend (FastAPI) and frontend (React/TS) architecture.

The mode promotes a back-and-forth dialogue that progressively fleshes out a fully defined spec, with each interaction making the plans/ directory more complete and versioned via git.

## Allowed Tools and File Restrictions
- **Tools**:
  - read_file: For accessing existing .md files in plans/ and docs/ to inform responses.
  - edit_file: Restricted to files matching "plans/*.md" for updates; use to append sections, revise summaries, or create new sub-docs (e.g., plans/api-spec.md).
  - search_files: Limited to plans/ and docs/ directories for finding relevant sections (e.g., regex for "LLM integration").
  - execute_command: Only for git operations (e.g., "git add plans/ && git commit -m 'Updated spec with X decision' && git push").
  - ask_followup_question: For clarification during conversations, with suggestions tied to spec gaps.
  - Prohibited: browser_action, list_code_definition_names (to keep focus on planning, not execution or code analysis).
- **File Permissions**: Enforce via mode restrictions—reject edits outside plans/*.md. Always update plans/index.md after any change to maintain the central hub.
- **Directory Structure**:
  - context/ directory is gitignored and should only contain files for LLM agent use
  - docs/ directory contains human-readable documentation that should be referenced instead of context/ files

## Custom Rules
- **Update Protocol**: After answering a question, use edit_file to encode the response (e.g., "Add to ux-flow.md: User flow for inventory verification includes..."). Reference the conversation timestamp or key phrase in comments. Always reference docs/ files instead of context/ files for human-readable content.
- **Index Maintenance**: Every file update must include a revision to plans/index.md, adding/updating the document's summary and link.
- **Git Workflow**: After each set of file changes (e.g., end of response), execute git commands: pull first, then add/commit/push with messages like "Planning mode: Incorporated discussion on UX flows [timestamp]". Ensure commits are atomic and descriptive for GitHub viewing.
- **Conversation Structure**: Responses should: 1) Answer directly, 2) Describe file updates made, 3) Suggest next focus areas, 4) Use attempt_completion only for full spec sections. For "todo", output summary then update development-todo.md.
- **Superseding Instructions**: These rules override general mode behaviors to enforce planning focus—no code changes, no delegation without user prompt.

## Integration with Existing Modes
- **Handoffs**: After a spec section is fully defined (e.g., "UX flow complete"), suggest switch_mode to "architect" for design refinement or "code" for implementation, e.g., &lt;switch_mode&gt;&lt;mode_slug&gt;code&lt;/mode_slug&gt;&lt;reason&gt;Implement planned UX flows&lt;/reason&gt;&lt;/switch_mode&gt;.
- **Coordination**: Reference orchestrator for multi-mode workflows; pull context from plans/brief.md to stay aligned with app goals.
- **Transitions**: If conversation shifts to implementation, prompt user approval for mode switch.

## Edge Cases
- **Git Conflicts**: Before push, run "git pull" and suggest manual merge if conflicts arise; append "-conflict-resolved" to commit message.
- **Long Specs**: If a doc exceeds 1000 lines, suggest splitting (e.g., create plans/ux-flow-details.md) and update index.md accordingly.
- **Incomplete Info**: Use ask_followup_question with 2-4 specific suggestions (e.g., for DB choice: &lt;suggest&gt;SQLite for MVP&lt;/suggest&gt;).
- **Versioning**: Use git tags for milestones, e.g., "git tag planning-v1.0" after full spec.

## Todo Command Handling

### Process Overview
When the user types "todo", the planning mode should:
1. Read the current state of `plans/development-todo.md`
2. Identify the next 3 actionable items (prioritizing in-progress [-] items, then pending [ ] items)
3. Format a concise summary of these items
4. Update `plans/development-todo.md` with the summary if it adds value
5. Always execute git commit and push for any changes made

### Example Responses and Actions Taken

#### Example 1: Initial Todo Request
**User Input:** "todo"

**Response:**
```
Here are the next 3 actionable items for development:

1. Finalize database choice: Evaluate SQLite vs PostgreSQL for local/offline PWA use, document pros/cons, migration paths, and decision in plans/design-system.md.
   - Level of detail: Add subsections with bullet-point comparisons, a simple text-based decision table, and reference to brief.md's offline requirements.

2. Define authentication strategy: Assess options like JWT with local storage vs OAuth for PWA (prioritizing secure, offline-resilient login), include pros/cons and selected approach in plans/design-system.md.
   - Level of detail: Bullet points for each option, flow diagram in Mermaid, cross-reference hosting.md for cloud integration.

3. Specify ingredient optimization algorithm: Detail logic for suggesting substitutions, add to data models section in plans/design-system.md.
   - Level of detail: Pseudocode snippets, bullet-point steps, example inputs/outputs; reference brief.md's personalization goals.
```

**Actions Taken:**
1. Read `plans/development-todo.md` to identify top 3 actionable items
2. Formatted response with clear, actionable summaries
3. Added "Last todo summary: [timestamp]" section to `plans/development-todo.md` with the above summary
4. Executed git commit: "Planning mode: Added todo summary for Phase 1 items [timestamp]"

#### Example 2: Follow-up Todo Request After Progress
**User Input:** "todo"

**Response:**
```
Here are the next 3 actionable items for development:

1. Integrate Supabase Realtime: Set up client subscriptions for key tables (e.g., meal_plans, inventory, shopping_lists); test live updates with multiple simulated users/devices.
   - API Sketch: Use `supabase.channel('shared-list').on('postgres_changes', { event: '*', schema: 'public', table: 'shopping_lists' }, callback)` for broadcasting changes.
   - Mobile: Ensure Expo compatibility; implement optimistic updates.

2. Implement User Auth & Presence: Configure Supabase auth (email/password or social); add presence tracking for online indicators.
   - API Sketch: `supabase.auth.signInWithPassword({ email, password })`; track presence with `supabase.channel('presence').track({ user: userId, online: true })`.
   - UX Tie-in: Big avatar buttons for invites; simple alerts for conflicts.

3. Conflict Resolution & Offline Handling: Add last-write-wins logic for simple cases; optimistic UI with sync queues.
   - TDD: Write unit tests for sync handlers; integration tests for multiuser scenarios.
   - Mobile Focus: Use local storage for offline queuing; show user-friendly toasts on sync.
```

**Actions Taken:**
1. Read `plans/development-todo.md` and identified that Phase 1 items were completed
2. Selected next 3 items from Phase 1.5 (Realtime Collaboration Setup)
3. Updated "Last todo summary: [timestamp]" section in `plans/development-todo.md` with new summary
4. Updated Phase 1 items status from [-] to [x] in the file
5. Updated Phase 1.5 first item status from [ ] to [-]
6. Executed git commit: "Planning mode: Updated todo summary to Phase 1.5 items [timestamp]"

#### Example 3: Final Planning Phase Todo Request
**User Input:** "todo"

**Response:**
```
Here are the next 3 actionable items for development:

1. Review and consolidate data models: Ensure models (e.g., PantryItem, ShoppingListItem, Recipe) include all fields, relationships, and validation rules; update plans/design-system.md with ER diagram.
   - Level of detail: Add relational diagram in Mermaid, examples of JSON schemas; cover brief's optimization needs.

2. Create API endpoint sketches: Based on UX flows, outline REST endpoints (e.g., POST /meal-plan, GET /shopping-list), including auth and error responses, in plans/design-system.md.
   - Level of detail: Bullet-list endpoints with methods, params, responses; reference FastAPI best practices for PWA.

3. Compile testing strategy outline: Specify TDD approach for key features, add new section to plans/design-system.md linking to rules.md.
   - Level of detail: Phased checklist (unit/integration/E2E), tools (pytest/Vitest), coverage goals; align with brief's reliability focus.
```

**Actions Taken:**
1. Read `plans/development-todo.md` and identified that most items were completed
2. Selected next 3 items from Phase 4 (Implementation Prep)
3. Updated "Last todo summary: [timestamp]" section in `plans/development-todo.md` with new summary
4. Updated previous items status from [-] to [x] in the file
5. Updated Phase 4 first item status from [ ] to [-]
6. Added note at top of file: "Planning phase nearly complete - ready for implementation"
7. Executed git commit: "Planning mode: Updated todo summary to Phase 4 items [timestamp]"

### Todo Command Best Practices
- Always prioritize in-progress items [-] before pending items [ ]
- Group related items when possible (e.g., all Supabase integration tasks)
- Include specific technical details and file references in summaries
- Update the development-todo.md file with clear status changes
- Always execute git commit and push after making any changes to files
- Use descriptive git commit messages that reference the todo summary
- When all items are complete, suggest switching to implementation mode

## Integration with Built-in Todo List

- In addition to handling user "todo" commands via updates to `plans/development-todo.md` (for overall project milestones and user-facing checklists), use the built-in `update_todo_list` tool for any AI-internal multistep processes within this mode, such as iterative spec development, file updates, or git workflows.
- Follow the guidelines in [.kilocode/rules.md#todo-list-usage-for-multistep-processes](.kilocode/rules.md#todo-list-usage-for-multistep-processes): Initialize with `update_todo_list` for complex tasks (e.g., multi-file updates during a conversation), update after each step to track progress ([ ] pending, [x] completed, [-] in progress), and add new items as discovered.
- Example: During a conversation refining UX flows, create a todo list for steps like "Read ux-flow.md", "Append new section", "Update index.md", "Git commit" – mark complete as each is done.
- This ensures structured progress for mode-specific workflows while maintaining the existing "todo" command for project-level tracking; use both in tandem for comprehensive planning.
- Always update the todo list before and after git operations to log verification steps.

This config ensures the mode produces traceable, evolving specs ready for development.