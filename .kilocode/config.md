# Kilo Code Configuration

## Available Modes

- **Architect** (slug: architect): Mode for planning, designing, and strategizing project architecture.
- **Code** (slug: code): Mode for writing, modifying, and refactoring code.
- **Ask** (slug: ask): Mode for explanations, documentation, and technical questions.
- **Debug** (slug: debug): Mode for troubleshooting and diagnosing issues.
- **Orchestrator** (slug: orchestrator): Mode for coordinating complex, multi-step projects.
- **Planning** (slug: planning): Mode for conversational spec-building and planning document management.

## Activation Notes

After creating mode files (e.g., modes/planning.md and updating modes.json/config.md), reload the VSCode window (Ctrl+Shift+P > 'Developer: Reload Window') or restart the Kilo Code extension to register the new mode. Verify in the modes list or by attempting switch_mode.

### Troubleshooting Visibility Issues (e.g., for Planning Mode)
- Verify .kilocode/modes.json format (valid JSON array of objects with slug, name, path).
- Check VSCode Developer Tools console (Help > Toggle Developer Tools) for Kilo Code extension errors related to modes.
- Ensure the Kilo Code extension is enabled and up-to-date (Extensions view > search "Kilo Code" > Reload if needed).
- If still not visible, the mode creation may require manual approval or a specific command in the extension settings; consider adding via the extension's config UI if available.

#### VSCode CLI Debug Commands for Planning Mode
- Open a terminal and run: `code --list-extensions | grep -i kilo` to verify Kilo Code extension is installed and its version, ensuring it supports custom modes like planning.
- Run: `code --disable-extensions` then relaunch VSCode to test if other extensions interfere with planning mode visibility, then re-enable Kilo Code.
- To inspect extension logs for planning mode issues: Run VSCode with `code --verbose` or check ~/.vscode/extensions logs for Kilo Code folder (e.g., ls ~/.vscode/extensions/*kilo*).
- If Kilo Code supports it, try `code --extensionDevelopmentPath=/path/to/kilo-code` for dev mode to see planning mode loading.
- Suggest reporting to extension author if logs show errors loading .kilocode/modes.json specifically for planning slug.

- Example: Open Kilo Code settings and look for "Custom Modes" or similar to add slug "planning".