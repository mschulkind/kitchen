# Progress Log Rules

## Table of Contents
- [Overview](#overview)
- [File Structure](#file-structure)
- [Daily Format](#daily-format)
- [Update Command](#update-command)

## Overview

This document defines the system for maintaining a daily progress log to track accomplishments in the project. Logs are organized by month, with each file containing daily summaries. This ensures an up-to-date record of progress, viewable on GitHub. 

**Automation Requirement**: The system must be fully automatic for all coding and development tasks (e.g., in code, debug, architect, planning modes). Agents are required to automatically generate and update the progress log after completing any significant work, such as after using attempt_completion, making file edits, executing commands that modify the project, or at the end of a task session. Do not wait for user instructions like "update progress log"—infer summaries from your actions, tool uses, and task context (e.g., "Created progress-log.md rules file" or "Implemented feature X via edit_file"). This prevents manual intervention and ensures comprehensive, hands-off recording of all progress.

The progress logs are tracked in Git for persistence and review. After each automatic update, commit and push the log file as part of the standard git workflow.

Include liberal links to other files that are involved.

## File Structure

Progress logs are stored in the `.kilocode/progress/` directory (create if it does not exist). Each file represents one month and is named `YYYY-MM.md`, where:
- `YYYY` is the four-digit year.
- `MM` is the two-digit month (zero-padded).

Examples:
- `.kilocode/progress/2025-09.md` for September 2025.
- `.kilocode/progress/2025-10.md` for October 2025.

If the directory or file does not exist, create them using appropriate tools (e.g., `execute_command` for `mkdir -p .kilocode/progress` if needed, then `edit_file` for the content).

## Daily Format

Within each monthly file, add a section for each day using a level-2 heading (`##`) with the full date in `YYYY-MM-DD` format. Follow with a summary of the day's accomplishments.

Example structure in `2025-09.md`:

```
# Progress Log - September 2025

## 2025-09-18
- Implemented feature X.
- Updated rules for progress logging.
- Resolved issue Y.

## 2025-09-19
Summary of accomplishments for the day. Use paragraphs or bullet points for clarity.
```

- Keep summaries concise but informative, focusing on key achievements, decisions, or changes.
- Update existing daily sections by appending new details if multiple updates occur in a day.
- Ensure the file always starts with a title like `# Progress Log - Month YYYY`.
- Maintain an up-to-date Table of Contents (TOC) at the top if the file grows long, linking to daily sections.

## Update Command

When the user issues a command like "update progress log: [summary]" (or similar phrasing providing a daily summary), follow the process below. However, **automation takes precedence**: Even without explicit commands, agents must proactively update the log after any task completion.

1. Extract the summary from the user's message if provided. Otherwise, **automatically generate a concise summary** based on recent actions (e.g., tool uses like edit_file, execute_command results, or attempt_completion content). Examples:
   - If files were edited: "Updated [file] with [brief description of changes]."
   - If commands were run: "Executed [command] to [purpose, e.g., commit changes]."
   - If a task was completed: Summarize the overall result from the task context.
   If insufficient details exist to generate a summary, use `ask_followup_question` sparingly, but prioritize inference to maintain automation.

2. Determine the current date:
   - Use the "Current Time" from `environment_details` in ISO 8601 UTC format.
   - Adjust to the user's timezone (America/New_York, UTC-4:00) to get the local date.
   - Format as `YYYY-MM-DD` for the day and `YYYY-MM` for the month.

3. Identify the target file: `.kilocode/progress/YYYY-MM.md`.

4. Check if the file exists (use `list_files` or `read_file` if needed). If not:
   - Create it with the title `# Progress Log - Month Name YYYY` (e.g., `# Progress Log - September 2025`).
   - Add the TOC if applicable.

5. Locate or add the daily section `## YYYY-MM-DD`.
   - If the section exists, append the new summary to it.
   - If not, add the new section with the summary.
   - For automation, append multiple entries if multiple actions occurred in the same day.

6. Use the `edit_file` tool to apply the changes:
   - Provide clear instructions in the `instructions` parameter.
   - Use `// ... existing code ...` in `code_edit` to preserve unchanged content.

7. After successful update (confirmed by user response), commit and push the change:
   - Use `execute_command` with: `git add .kilocode/progress/YYYY-MM.md && git commit -m "Update progress log for YYYY-MM-DD: [brief summary]" && git push`.
   - Follow git workflow rules from [.kilocode/rules/git-workflow.md](.kilocode/rules/git-workflow.md). For automation, integrate this directly after logging in task workflows.

8. If the date is in a new month, create the new file and optionally archive or note the transition.

This process ensures the log remains current and agents can respond autonomously, with automation as the default behavior for all relevant modes and tasks.

For generic guidelines, see [.kilocode/rules/library/progress-log-automation.md](.kilocode/rules/library/progress-log-automation.md).
