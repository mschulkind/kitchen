# Directory Standards

For generic directory standards across projects:

- **scratch/**: Gitignored; strictly for temporary files during development (e.g., quick prototypes, debug outputs, temporary scripts). No long-term storage or commits; clean up or abandon as needed. Use for any short-lived artifacts that shouldn't be tracked in version control.

- **trash/**: Gitignored; for moving files intended for deletion (e.g., via mv instead of rm for safer, reversible operations). Allows recovery of accidentally moved files without permanent loss. Periodically review and empty as needed.