# Todo List Usage for Multistep Processes

- For any task that involves multiple steps, especially complex, iterative, or long-running processes, immediately initialize a todo list using the `update_todo_list` tool with a single-level markdown checklist in the intended execution order.
- Status options: [ ] for pending (not started), [x] for completed (fully finished), [-] for in progress (currently being worked on).
- Update the todo list after each step or set of related steps to reflect progress: mark completed items as [x], set the next as [-] if starting it, and add new actionable items discovered during execution.
- This applies to **all modes**, including but not to code, architect, debug, and especially planning mode, to ensure structured, trackable progress and prevent loss of context in multistep workflows.
- In **planning mode**, integrate this built-in tool with existing project todo handling (e.g., plans/development-todo.md for user-facing todos): use `update_todo_list` for AI-internal multistep planning (e.g., iterative spec updates), while updating the .md file for overall project milestones via "todo" commands.
- Do not remove unfinished todos unless irrelevant; only mark as completed when fully accomplished without unresolved issues. If blocked, keep as [-] and add a resolution todo.
- When the entire task is complete (all todos [x]), use `attempt_completion` to finalize.