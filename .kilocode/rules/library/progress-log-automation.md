# Progress Log Automation Rules

## Overview

This document defines a system for maintaining daily progress logs to track accomplishments. Logs are organized by month, with each file containing daily summaries for GitHub viewing.

**Automation Requirement**: Fully automatic for development tasks. Agents generate and update logs after significant work (e.g., after attempt_completion, file edits, or command executions). Infer summaries from actions without user prompts.

Logs are tracked in Git. After updates, commit and push per git workflow.

Include links to involved files.

## File Structure

Progress logs stored in a dedicated directory (e.g., .kilocode/progress/; create if needed). Monthly files named `YYYY-MM.md`.

Examples:
- `2025-09.md` for September 2025.

Create directory/file using tools if absent.

## Daily Format

Use level-2 headings (`##`) for dates in `YYYY-MM-DD` format, followed by accomplishment summaries.

Example:

```
# Progress Log - September 2025

## 2025-09-18
- Implemented feature X.
- Updated rules for logging.
- Resolved issue Y.

## 2025-09-19
Summary of day's work. Use bullets or paragraphs.
```

- Keep concise, focus on key changes.
- Append to existing sections if multiple updates.
- Start with `# Progress Log - Month YYYY`.
- Add TOC for long files.

## Update Process

1. Generate summary from actions (e.g., "Updated [file] with changes.", "Executed [command] for [purpose]."). Prioritize inference.

2. Determine date from environment_details (UTC to local timezone, format `YYYY-MM-DD` and `YYYY-MM`).

3. Target file: `{progress-dir}/YYYY-MM.md`.

4. If new, create with title and TOC.

5. Add/append `## YYYY-MM-DD` section with summary.

6. Use edit_file with clear instructions and `// ... existing code ...` for unchanged parts.

7. After update, commit/push: `git add {file} && git commit -m "Update progress log for YYYY-MM-DD: [summary]" && git push`.

8. For new months, create file and note transition.

This ensures autonomous, current logging.