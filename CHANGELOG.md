# Changelog

## 2026-05-10 — Project initialized

- Created `storyboard-editor-prd.md` with full product requirements for v1
- Created `CLAUDE.md` with standing session instructions
- Created `CHANGELOG.md` (this file)
- Built initial `index.html` with full v1 feature set (start screen, image grid, scene editor panel, character manager, filters, bulk actions, export, stats, auto-save, lazy loading, drag-and-drop reorder, background SHA-256 hashing, IndexedDB handle persistence)
- **Known gap from PRD:** folder scanning is flat (top-level only); recursive subdirectory scanning, correct `asset.path` storage, and subfolder-based initial ordering are not yet implemented — planned for next session

## 2026-05-10 — Three view modes: Grid, Focus Tableau, Detail List

- Added view mode switcher — three icon buttons (⊞ ⊟ ≡) in the header between the save indicator and stat chips; active button highlighted in accent color; selection persists across reloads via localStorage
- **Grid view** — existing behavior preserved; DnD and select-mode only active in this view; switching away clears selection and hides bulk bar
- **Focus Tableau view** — 5-cell horizontal strip: [far-prev 80px 45%] [prev 150px 75%] [CURRENT flex:1] [next 150px 75%] [far-next 80px 45%]; status border color on center cell; clicking a neighbor shifts focus; editor panel auto-opens and stays open (Escape no-ops); ←/→ arrow keys navigate when focus not in a text field; placeholders shown at sequence edges
- **Detail List view** — sticky header row, alternating row shading, 9-column layout: thumbnail | status dot | path | rating | shot | transition | mood | tags (≤3 chips + overflow badge) | narrative (80-char truncation with full-text tooltip); click row to open editor
- `App.Grid` refactored: `render()` branches on `viewMode`; existing card loop extracted to `_renderGrid()`; `_renderFocus()` and `_renderList()` added; `_lastFilteredScenes` module var enables arrow-key navigation without re-filtering; `refreshCard()` handles all three modes; `setViewMode()` added to public API
- Select-mode checkbox disabled (with tooltip) when not in grid view

## 2026-05-10 — Prominent scrollbar, stats moved to collapsible sidebar section

- Scrollbar width increased from 6px to 10px with a visible thumb and track; thumb has a 2px inset border for contrast
- Removed the "Stats" button and `stats-dialog` modal entirely
- Stats content moved inline to the sidebar "Project" section in a compact key-value layout (total, included, maybe, excluded, untagged, narrative %, character coverage %, characters defined)
- "Project" section is now collapsible: click the header to toggle; arrow rotates to indicate state
- When collapsed, shows "N in view" — the count of scenes currently passing the active filter — rather than total scenes
- `App.Grid.render()` now stores filtered scene count in state; `App.Stats` subscribes to both `projectChange` and `filterChange` so the "in view" count stays current

## 2026-05-11 — Alias display, collapsible filters, focus border height

- Characters now displayed by alias everywhere in the UI — filter character checkboxes, perspective dropdown, add-character select, characters-in-scene list, and LLM export character names and POV field — falling back to name when no alias is set
- Filter section headers (Status, Content Rating, Character Present) are clickable toggles that collapse/expand their checkbox groups; the arrow indicator rotates when collapsed; all three start expanded
- Focus view cells given `aspect-ratio:16/9` and the strip container switched to `align-items:center`; cells now sit at image height rather than stretching to the full panel height, so status border outlines only the image frame

## 2026-05-10 — Checkbox filters, focus layout, preview visibility, resizable divider

- Status, Content Rating, and Character filters converted from single-select dropdowns to multi-checkbox groups; filter state uses Sets (empty Set = show all)
- New "Apply Filters" button must be pressed before the three checkbox filters take effect; button turns accent-colored when pending changes are queued; `showExcluded` and `taggedOnly` checkboxes remain instant-apply
- `App.Filters.updateCharGroup()` replaces the old `_updateFilterDropdown` select-rebuild; character checkboxes are populated on project load and after any character add/delete/import, and checked selections are preserved across rebuilds
- Grid and focus card status borders increased from 2px to 3px for better contrast (especially yellow "maybe" on light thumbnails)
- Focus view cells switch from fixed pixel widths to proportional flex ratios (6:2:1 = 50%/16.6%/8.3%); images use `object-fit:contain` so the full image is always visible without cropping
- Editor preview pane (left side showing the image) is now hidden in Grid and Focus views via a `detail-mode` CSS class; it only appears when the editor is opened from the Detail List view
- Draggable resize handle added between the preview pane and the fields panel when in detail-mode; minimum preview width enforced at 112px (2× the 56px list thumbnail)

## 2026-05-10 — Expanded character schema with nine new optional fields

- Added `alias`, `color`, `age`, `occupation`, `orientation`, `kink`, `physicalAppearance`, `relationships`, and `notes` to the character data model
- Removed enum validation on `role`, `orientation`, and `kink` — all three now accept any free-form string; `role` input in the character manager changed from a `<select>` to a plain text field
- Batch import parser reads and stores all new fields when present; fields absent from the import payload are omitted (not defaulted) — no errors thrown for missing optional fields; `id` continues to be auto-generated and is never read from import payload
- Character manager dialog widened to 700 px; each character row now renders all new fields as editable inputs (single-line for alias, color, occupation, orientation, kink; number input for age; textareas for physicalAppearance, relationships, notes)
- Age field coerced to integer (null when cleared) in both the `change` and `input` event handlers via a shared `_coerceField()` helper
- LLM package export markdown now conditionally renders each new field — fields that are null or absent are hidden rather than emitted as blank lines
- Full JSON exports unchanged — `JSON.stringify` serializes the entire project graph so all populated fields are included automatically

## 2026-05-10 — Character batch import from LLM

- Added "Import from LLM…" button to the Characters dialog footer — visible only from that dialog
- Added `char-import-dialog`: paste a JSON array of character objects produced by an LLM
- Added "Show Schema" button inside the import dialog (only) — toggles a copyable JSON example annotated with field rules
- `App.CharImport` module handles parsing, validation, and merging: skips objects missing a `name`, skips names that already exist in the project (case-insensitive), sanitizes `role`/`playable`/`tags` types, auto-generates `id`
- Import preview updates live as the user types, showing valid count, invalid row numbers, and duplicate skip count
- Exposed `App.CharMgr.render()` so the character list refreshes immediately after a successful import without reopening the dialog
- Linked project to GitHub repo at `https://github.com/willpculbertson-wq/Storyboard-Editor.git`
- Updated `CLAUDE.md` standing rule: after every session, commit and push changes with a message mirroring the changelog summary

## 2026-05-10 — Recursive scanning, path-keyed caches, batch edit

- Replaced flat folder scan with recursive `walkDir()` that walks the full directory tree via `for await...of handle.entries()`
- `asset.path` now stores the correct relative path from the folder root (e.g. `01-chapter/img001.jpg`); was previously just the filename
- `fileHandleCache` and `thumbnailCache` now keyed by `asset.path` instead of `asset.filename` — prevents collisions when the same filename appears in different subdirectories
- `reconcileScenes()` now matches existing scenes by `asset.path` (was matching by filename)
- All modules (LazyLoader, Editor, Hasher) updated to use `scene.asset.path` for cache lookups
- Editor panel now displays full `asset.path`; card hover tooltip also shows `asset.path`
- Initial scene ordering: root-level files first, then subdirectories sorted by `localeCompare({numeric:true})`, then filename within each directory
- `IMG_EXTS` trimmed to exactly the five PRD-specified extensions: `.jpg .jpeg .png .webp .gif`
- Added `App.BatchEdit` module — dialog with two-pane layout: folder scope (per-subdirectory checkboxes + "All scenes" master) and field selection (status, content rating, shot type, transition, perspective)
- Batch edit field dropdowns require an active user selection; placeholder is disabled so no value is applied silently
- Perspective field supports a `__clear__` sentinel to explicitly blank the POV character for selected scenes
- Apply button shows a confirmation prompt with the affected scene count before mutating project state
- "Batch Edit" button added to the app header
