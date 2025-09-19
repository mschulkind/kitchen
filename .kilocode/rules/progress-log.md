# Progress Log Rules

## Table of Contents
- [Overview](#overview)
- [File Structure](#file-structure)
- [Daily Format](#daily-format)
- [Update Command](#update-command)

## Overview

This document defines the system for maintaining a daily progress log to track accomplishments. Logs are organized by month in `.kilocode/progress/` and are viewable on GitHub.

**Automation Requirement**: Log updates must be fully automatic for all development tasks (e.g., in code, debug, architect, planning modes). Agents must infer summaries from actions (e.g., `edit_file`, `execute_command`) and update the log after any significant work. Do not wait for user instructions.

Progress logs are tracked in Git. After each update, commit and push the log file. Include links to relevant files.

## File Structure

Logs are stored in `.kilocode/progress/`, with monthly files named `YYYY-MM.md`. If the directory or file doesn't exist, create it.

Examples:
- `.kilocode/progress/2025-09.md`
- `.kilocode/progress/2025-10.md`

## Daily Format

Use a level-2 heading (`##`) for each day (`YYYY-MM-DD`), followed by a summary of accomplishments.

Example:
```
# Progress Log - September 2025

## 2025-09-18
- Implemented feature X.
- Updated rules for progress logging.

## 2025-09-19
- Summary of the day's work.
```

- Keep summaries concise.
- Append to existing daily sections if multiple updates occur.
- Start new files with a title (e.g., `# Progress Log - September 2025`).
- Maintain a TOC if the file grows long.

## Update Command

While automation is the default, user commands like "update progress log: [summary]" are supported.

1.  **Generate Summary**: Extract the summary from the user's message or, preferably, automatically generate it from recent actions. Prioritize inference.
2.  **Determine Date**: Use `environment_details` to get the current date in America/New_York time.
3.  **Identify Target File**: `.kilocode/progress/YYYY-MM.md`.
4.  **Check/Create File**: If the file doesn't exist, create it with a title and TOC.
5.  **Add/Update Section**: Locate or add the `## YYYY-MM-DD` section and append the summary.
6.  **Apply Changes**: Use `edit_file` to update the log.
7.  **Commit and Push**: After confirmation, run `git add .kilocode/progress/YYYY-MM.md && git commit -m "Update progress log for YYYY-MM-DD: [summary]" && git push`.
8.  **New Month**: For a new month, create the new file as needed.

This process ensures logs remain current, with a strong emphasis on autonomous agent behavior.
