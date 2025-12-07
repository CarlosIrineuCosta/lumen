# Workspace Layout Control (Kilo + Codex + Explorer)

## Pane Structure
- Left (Secondary Side Bar): **Kilo Code (GLM)**
- Mid-left (Editor Group 1): **Codex / Bash**
- Mid-right (Editor Group 2): **Docs / Files**
- Right (Primary Side Bar): **Explorer**
- Bottom Panel: **Terminal** and **Ports/Console**

## Rules That Make This Stable
- **Codex tab is pinned** → cannot be replaced.
- **Docs pane is the default file target**.
- **Files opened by Kilo/GLM are forced to the right group.**

## Key Shortcuts
| Shortcut | Action |
|---------|--------|
| `Ctrl + Win + 1` | Focus Codex (left editor group) |
| `Ctrl + Win + 2` | Focus Docs (right editor group) |
| `Ctrl + Win + 3` | Focus Terminal panel |
| `Ctrl + Win + O` | Force opened files → Docs pane |
| `Ctrl + Shift + R` | Reload window |

## Shift+Enter (Command Override)
Disabled everywhere so it no longer conflicts with:
- Python REPL
- Jupyter cells
- Markdown editing
- Terminal sendSequence
- Interactive windows

## Secondary Side Bar (Kilo)
If it hides or moves:
