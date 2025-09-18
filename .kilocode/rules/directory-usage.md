# Directory Usage Rules
## Mode-Specific File Permissions

- **plans/**: Git-tracked directory for all planning, outlines, specs, and decisions (e.g., brief.md, design-system.md). Maintain an index.md for navigation.
- **context/**: Gitignored; for dumping research, data, temporary notes, and references (e.g., API docs, recipe datasets). Use index.md to organize and link content.
- **scratch/**: Gitignored; strictly for temporary files during development (e.g., quick prototypes, debug outputs). No long-term storage or commits; clean up or abandon as needed.
- **src/** or similar: For source code (backend in Python, frontend in TS/React). Keep tests separate but parallel.
- **General**: All paths relative to project root (/home/matt/code/kitchen). Use clear naming and READMEs in subdirs for clarity.

### Mode-Specific File Permissions
- architect (architect): edit_file restricted to *.md
- code (code): edit_file restricted to *.ts,*.js,*.py,*.md
- ask (ask): edit_file unrestricted
- debug (debug): edit_file restricted to *.ts,*.js,*.py
- orchestrator (orchestrator): edit_file unrestricted
- planning (planning): edit_file restricted to plans/*.md