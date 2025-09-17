# Kilo Code Configuration

## Activating New Modes

After creating mode files (e.g., modes/planning.md and updating modes.json/config.md), reload the VSCode window (Ctrl+Shift+P > 'Developer: Reload Window') or restart the Kilo Code extension to register the new mode. Verify in the modes list or by attempting switch_mode.

### Troubleshooting Visibility Issues
- Verify .kilocode/modes.json format (valid JSON array of objects with slug, name, path).
- Check VSCode Developer Tools console (Help > Toggle Developer Tools) for Kilo Code extension errors related to modes.
- Ensure the Kilo Code extension is enabled and up-to-date (Extensions view > search "Kilo Code" > Reload if needed).
- If still not visible, the mode creation may require manual approval or a specific command in the extension settings; consider adding via the extension's config UI if available.

#### VSCode CLI Debug Commands
- Open a terminal and run: `code --list-extensions | grep -i kilo` to verify Kilo Code extension is installed and its version.
- Run: `code --disable-extensions` then relaunch VSCode to test if other extensions interfere, then re-enable Kilo Code.
- To inspect extension logs: Run VSCode with `code --verbose` or check ~/.vscode/extensions logs for Kilo Code folder (e.g., ls ~/.vscode/extensions/*kilo*).
- If Kilo Code supports it, try `code --extensionDevelopmentPath=/path/to/kilo-code` for dev mode to see mode loading.
- Suggest reporting to extension author if logs show errors loading .kilocode/modes.json.

- Example: Open Kilo Code settings and look for "Custom Modes" or similar to add slug "planning".