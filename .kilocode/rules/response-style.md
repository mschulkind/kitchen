# Response Style Guidelines

## Table of Contents
- [Structure](#structure)
- [Readability](#readability)
- [Appearance](#appearance)
- [Attention to User Feedback](#attention-to-user-feedback)

## Structure
- Use clear sections with # headings to organize content logically.
- Employ bullet lists for steps, options, or key points to break down information.
- Use numbered lists for sequences or ordered processes.
- Use tables for comparisons or data presentation.
- Keep attempt_completion results concise yet comprehensive, summarizing key outcomes without unnecessary details.

## Readability
- Write short paragraphs to maintain flow and prevent dense text.
- Use active voice for direct, engaging communication.
- Employ technical but accessible language, assuming familiarity with development concepts.
- Avoid walls of text; integrate bold (**bold**) and italics (*italics*) for emphasis on important terms or actions.

## Appearance
- Leverage GitHub Markdown features, such as code blocks (```) for commands or examples.
- Include Mermaid diagrams if needed for visualizing workflows or architecture (ensure compatibility by avoiding double quotes and parentheses in brackets).
- Add subtle emojis (e.g., ✅ for completions) sparingly to highlight positives without clutter.
- Ensure mobile-friendly formatting: avoid wide tables, use line breaks for readability.

## Attention to User Feedback
- Pay close attention to user feedback provided in responses.
- Reference it explicitly in subsequent responses to demonstrate incorporation (e.g., "Based on your feedback about X, I updated Y").
- Adapt future outputs accordingly to align with user preferences.

## Completeness
- Always detail assumptions you've made.
- Never return just a command response like execute_command, always return some description with each command so that I know what you're thinking as much as possible.
- Whenever a file is mentioned, ensure that it is linked so I can just click on it to view it.