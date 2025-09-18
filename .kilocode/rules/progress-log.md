# Progress Log Rules

## Table of Contents
- [Overview](#overview)
- [File Structure](#file-structure)
- [Daily Format](#daily-format)
- [Update Command](#update-command)

## Overview

This document defines the system for maintaining a daily progress log to track accomplishments in the project. Logs are organized by month, with each file containing daily summaries. This ensures an up-to-date record of progress, viewable on GitHub. Agents should follow these rules when instructed to "update progress log".

The progress logs are tracked in Git for persistence and review.

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

When the user issues a command like "update progress log: [summary]" (or similar phrasing providing a daily summary):

1. Extract the summary from the user's message. If no summary is provided, use `ask_followup_question` to request it (e.g., "What is the summary of today's accomplishments?").

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

6. Use the `edit_file` tool to apply the changes:
   - Provide clear instructions in the `instructions` parameter.
   - Use `// ... existing code ...` in `code_edit` to preserve unchanged content.

7. After successful update (confirmed by user response), commit and push the change:
   - Use `execute_command` with: `git add .kilocode/progress/YYYY-MM.md && git commit -m "Update progress log for YYYY-MM-DD: [brief summary]" && git push`.
   - Follow git workflow rules from [.kilocode/rules/rules.md](.kilocode/rules/rules.md).

8. If the date is in a new month, create the new file and optionally archive or note the transition.

This process ensures the log remains current and agents can respond to the command autonomously.