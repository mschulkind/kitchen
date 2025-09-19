# Auto-Approver Guidelines

## Table of Contents
- [Overview](#overview)
- [Configuration](#configuration)
- [Usage](#usage)
- [Best Practices](#best-practices)
- [CLI Command Construction](#cli-command-construction)

## Overview

This file outlines guidelines for auto-approver functionality in the project workflow.

## Configuration

## Usage

## Best Practices

## CLI Command Construction

- **Careful Construction**: When using the `execute_command` tool, construct CLI commands meticulously to ensure compatibility and approval by the autoapprover system.
- **Avoid Multiline Strings**: The autoapprover struggles with multiline strings, including heredocs or any other multiline formats. Instead of embedding multiline content directly in commands, write it to a temporary file using `write_to_file` (or equivalent file writing tools) and pass the file path as a CLI argument.
- **Temporary Files in Scratch Folder**: Use the `scratch/` directory (which is gitignored) for any temporary files created during command execution. You can abandon these files without deletion, as they are not tracked.
- **Safe Deletions**: Avoid using `rm` to remove files. Instead, move them to the `trash/` directory (also gitignored) using `mv` for safer, reversible operations.