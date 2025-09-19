# Todo List Usage for Multistep Processes

- For any task that involves multiple steps, especially complex, iterative, or long-running processes, immediately initialize a todo list using the `update_todo_list` tool with a single-level markdown bulleted list in the intended execution order.
- Instead of using checkboxes, each item should have a "status" bullet at the top indicating its current state. Use descriptive status indicators like "pending", "completed", or "in_progress" rather than symbols.
- Update the todo list after each step or set of related steps to reflect progress: mark completed items with appropriate status, set the next item as in progress, and add new actionable items discovered during execution.
- This applies to **all modes**, including but not to code, architect, debug, and especially planning mode, to ensure structured, trackable progress and prevent loss of context in multistep workflows.
- In **planning mode**, integrate this built-in tool with existing project todo handling (e.g., project-todo.md for user-facing todos): use `update_todo_list` for AI-internal multistep planning (e.g., iterative spec updates), while updating the .md file for overall project milestones via "todo" commands.
- When adding timestamped updates to checklist items, use sub-bullets under the original item to make it easier to read and include metadata
- Do not remove unfinished todos unless irrelevant; only mark as completed when fully accomplished without unresolved issues. If blocked, keep as in progress and add a resolution todo.
- When the entire task is complete (all todos marked as completed), use `attempt_completion` to finalize.