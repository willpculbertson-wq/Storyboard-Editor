# Storyboard Editor — Claude Instructions

## Standing Rules

- **After every session**, update `CHANGELOG.md` with the date, a one-line summary, and bullet points describing what changed.
- **This app is a single self-contained HTML file** — no frameworks, no npm, no build step, no server, no external dependencies. Everything lives in `index.html`.
- **All images are referenced in place via the File System Access API** — never copy or cache image data to disk. ObjectURLs are created from file handles at render time and revoked when no longer needed.
- **Before writing any code**, read the existing files to understand current state.
- **Never preview the HTML file within Claude Code.** If changes require a browser reload to take effect, tell the user to reload — do not attempt to preview or interact with the file directly.
- **Ask clarifying questions** if a request is ambiguous before writing code.

## Project Overview

A browser-based, single-file visual novel asset pipeline tool. The user selects a local image folder; the app scans it recursively, builds a scene list, and lets the user tag/order/annotate each image. All metadata is stored in `storyboard.json` inside the selected folder. The structured JSON is the output — fed to an LLM as context for game script generation.

## Technical Constraints

- Vanilla JS only — no frameworks, no build tools
- File System Access API (Chrome/Edge only — known, accepted limitation)
- Single output file: `index.html`
- All persistence via one `storyboard.json` file written into the user's image folder
- No network requests

## Key Files

| File | Purpose |
|---|---|
| `index.html` | The entire application |
| `storyboard.json` | Project data (written into user's image folder, not here) |
| `storyboard-editor-prd.md` | Product requirements — read this before planning any feature work |
| `CHANGELOG.md` | Session-by-session record of changes |

## Image Handling

- Supported extensions: `.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`
- Scan recursively through all subdirectories from the selected root folder
- `asset.path` stores the relative path from the folder root (e.g. `00-prelude/scene_001.jpg`)
- `asset.filename` stores just the bare filename (e.g. `scene_001.jpg`)
- The `fileHandleCache` is keyed by `asset.path` (not filename), since the same filename may appear in different subfolders
- Initial scene ordering: sort subfolders by their natural/numeric name order, then files within each subfolder alphabetically
