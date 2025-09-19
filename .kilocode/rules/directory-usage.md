# Directory Usage Rules
## Mode-Specific File Permissions

For generic mode-specific file permissions, see [.kilocode/rules/library/mode-permissions.md](.kilocode/rules/library/mode-permissions.md).

For generic directory standards (e.g., scratch/, trash/), see [.kilocode/rules/library/directory-standards.md](.kilocode/rules/library/directory-standards.md).

- **plans/**: Git-tracked directory for all planning, outlines, specs, and decisions (e.g., brief.md, design-system.md). Maintain an index.md for navigation.
- **context/**: Gitignored; for dumping research, data, temporary notes, and references (e.g., API docs, recipe datasets). Use index.md to organize and link content.
- **src/** or similar: For source code (backend in Python, frontend in TS/React). Keep tests separate but parallel.
- **General**: All paths relative to project root (/home/matt/code/kitchen). Use clear naming and READMEs in subdirs for clarity.