# Changelog

## 2026-05-15 — Editor tab strip; grouping fixes

- **Editor close bug fixed**: `close()` was removing the `.open` class but leaving an inline `style.height` set by `open()`, which overrode the CSS `height:0` — panel never collapsed. Fixed by clearing the inline style in `close()`.
- **Editor redesigned as persistent tab strip**: replaced the ✕ close button with a 36px tab strip always visible at the bottom of the main content area. Clicking the strip or the ▲ toggle expands/collapses the editor; the tab label shows the current scene filename when a scene is open.
- `#scene-editor` now defaults to `height:36px` (tab-only) instead of `height:0`; inner content and height-handle are `display:none` when collapsed, shown when `.open` is added.
- Vertical drag resize updated to save/restore only the content height (total minus tab and handle); min height enforced as `MIN_H + TAB_H + HANDLE_H`.
- Escape key closes the editor in both grid and focus modes (was blocked in focus mode).
- **Grouping fix — wrong position**: `createGroupFromSelection` was using `parentArr.push(group)` when the first selected scene was at index 0, inserting the group at the end instead of the front. Fixed to `parentArr.unshift(group)`.
- **Grouping fix — context menu**: "Create group from selection" now appears when `sel.size >= 2` regardless of whether the right-clicked card is in the selection (was requiring `sel.has(targetId)`).

## 2026-05-13 — Collapse/Expand All in list view; recursive folder hierarchy

- Moved "Collapse All" and "Expand All" buttons out of the grid-only header zone; they now live in a `.tree-btn-group` div immediately right of the view switcher and are visible in both grid and list views (hidden only in focus view)
- Buttons are view-aware: in list mode they expand/collapse filesystem folders; in grid mode they expand/collapse sequence groups as before
- List view now builds a full recursive folder tree from `asset.path` segments (`_buildFolderTree`) instead of grouping by the flat `dirOf()` result — any depth of subdirectory nesting is correctly rendered
- Folder rows indent by `depth × 20 px` (left padding); scene-row path cells indent by the same amount, keeping thumbnails flush-left
- Scene-count badge on each folder row shows the total recursive count of all scenes beneath it
- Collapse state is per full folder path (e.g. `chapter1/act1`); collapsing a parent implicitly hides all descendants without touching their individual collapse state
- Added `_renderFolderNode`, `_buildFolderTree`, `_countScenesInNode`, `_collectAllFolderPaths`, `_persistCollapsed`, `_collapseAllFolders`, `_expandAllFolders` helpers inside `App.Grid`

## 2026-05-13 — Phase 4: Branch-aware focus view and Variables panel

- Focus view now detects when the selected scene is inside a branch and switches to a horizontal lane-strip layout: each lane is rendered as a labelled row of `focus-strip-cell` thumbnails (96 px wide, current cell 144 px with accent outline); arrow keys navigate within the active lane
- Added `_findBranchContext(sequence, sceneId)` — walks the full sequence tree and returns the `branch_split` element whose lanes contain the given scene
- Added `_renderFocusBranched(branchEl, selectedId)` — renders lane strips with `#image-grid-inner.focus-lanes-wrap` layout; sets `_focusLaneScenes` so arrow keys follow the current lane
- Added `_focusLaneScenes` module var; arrow key handler uses `_focusLaneScenes || _lastFilteredScenes` so navigation stays within a branch lane when in branched view
- Added `App.VarMgr` module — CRUD dialog for `project.variables[]`; each variable has name, type (number|boolean), and defaultValue; type change resets defaultValue to `0` or `false`; dialog bound to `btn-vars` in the header
- Added Variables dialog HTML (`#variables-dialog`) and CSS (`.var-row-header`, `.var-row`) before the List View section

## 2026-05-13 — Phase 3: List view as file-system hierarchy

- `_renderList(scenes)` rebuilt as a folder-collapsible hierarchy: root-level scenes shown first, then each subdirectory as a collapsible folder row followed by its scene rows
- Added `_buildFolderRow(dir, count)` — clickable row with folder icon, directory name, scene count badge, and collapse arrow; collapse state persisted to `localStorage('storyboard_collapsedFolders')`
- Scenes under a folder show just `asset.filename` as the path label; full relative path shown in the row `title` attribute
- LazyLoader.observe called after fragment append to avoid missing newly rendered rows
- View-toggle button order changed to List → Grid → Focus; "Collapse All" / "Expand All" text buttons (no icons) for grid mode

## 2026-05-12 — Phase 2: Grid view rebuilt as recursive sequence tree renderer

- Replaced flat `_renderGrid(scenes)` with `_renderGridView(sequence)` — renders the full `project.sequence` tree without filtering; grid mode always shows the complete narrative structure
- Added `_renderSequenceInto(seq, container)` — recursive renderer; batches consecutive scenes into `.scene-grid` wrappers; groups, nodes, and branch sections appear full-width between scene clusters
- Added `_buildCard(scene)` — no checkbox; Ctrl/Cmd+click toggles selection, Shift+click range-selects, plain click opens editor, right-click opens context menu; card carries both `data-scene-id` (LazyLoader) and `data-element-id` (DnD/selection)
- Added `_buildGroup(el)` — collapsible group with expand/collapse arrow, scene count badge, dblclick-to-rename, collapsed preview strip (first thumb → count badge → last thumb), recursive body
- Added `_buildNodeCard(el)` — action / branch_split / rejoin cards with type-specific icons and right-click context menu
- Added `_buildBranchSection(branchEl)` — N side-by-side `.seq-lane` columns, each recursively rendered; empty lanes show placeholder text
- Added `_makeGroupThumb(scene)` — eager thumbnail loader for collapsed group previews (reads from cache or file handle)
- Added `_assignNewIds(el)` — deep new-ID assignment used by `duplicateElement` to ensure all copied elements get fresh IDs
- Added public API: `createGroupFromSelection`, `addGroupAfter`, `renameGroup`, `ungroup`, `duplicateElement`, `insertNode`, `deleteElement`, `collapseAll`, `expandAll`
- `render()` routes grid mode to `_renderGridView` (no filter applied); focus and list modes continue to apply `_applyFilter` to flat scenes
- `init()` wires `btn-collapse-all` / `btn-expand-all` / `btn-add-group` header buttons; calls `App.CtxMenu.init()`; sets initial `view-*` class on `#app-shell`
- `setViewMode()` now adds/removes `view-grid` / `view-list` / `view-focus` class on `#app-shell` (drives `.grid-only` button visibility); clears selection when leaving grid mode
- `App.DnD` updated to use `data-element-id` (falls back to `data-scene-id`) so groups and nodes are draggable alongside scene cards
- Removed dangling `toggle-select-mode` references from the home button handler and `App.Filters.init()` — select-mode checkbox was removed from the sidebar in Phase 2 HTML prep

## 2026-05-12 — Phase 1: Sequence tree data model

- Replaced flat `project.scenes[]` with a recursive `project.sequence[]` tree; project schema bumped to v1.1.0
- Added `project.variables[]` array to the project root (empty for now; will hold global named variables)
- Added `App.Seq` utility module with: `walk()`, `flatScenes()`, `buildIndex()`, `findById()`, `findSceneById()`, `move()`, `remove()`, `insertAfter()` — all tree-recursive, handling `group` and `branch_split` containers
- Added `migrateProject()` — automatically upgrades v1.0 projects (with `scenes[]`) to v1.1 on load; adds `type:'scene'` to every existing scene element; called at all three project-load paths
- `buildEmptyScene()` now sets `type:'scene'` on every new scene
- `App.State.mutateProject()` and `initIndex()` now call `App.Seq.buildIndex()` instead of iterating a flat array; `_sceneIndex` now covers all element types in the tree
- `reconcileScenes()` uses `App.Seq.flatScenes()` to find existing scenes and pushes new ones to `project.sequence`
- `App.DnD.onDrop()` uses `App.Seq.move()` for reordering — works across container boundaries
- All modules updated to use `App.Seq.flatScenes(project.sequence)` instead of `project.scenes`: `App.Grid`, `App.Stats`, `App.Filters`, `App.BatchEdit`, `App.Export`, `App.Hasher`
- `App.Editor` mutations use `App.Seq.findSceneById()` instead of `Array.find()` on the flat array
- Export functions updated: filtered JSON exports `sequence` key; LLM package raw JSON block also uses `sequence`

## 2026-05-11 — Adjustable editor height, configurable list columns

- Scene editor now has a 6px drag handle at its top edge; drag up/down to resize; preference saved to `localStorage('storyboard_editorH')` and restored on reopen; default height 480px (fits all fields without scrolling); minimum 200px; maximum is viewport height minus 80px
- `App.Editor.open()` now sets panel height from localStorage on every open instead of relying on the CSS `.open` rule
- List view columns are now configurable: click `⊞` at the far right of the header to open a checkbox dropdown that toggles individual columns on/off; column visibility and order persisted in `localStorage('storyboard_listCols')`
- Non-pinned list column headers are draggable for reorder; drag one header cell onto another to swap their positions; visual `drag-over` outline shown on drop target
- Pinned columns (thumbnail, status dot, path) are always the first three columns and cannot be hidden or moved
- New optional column: **Characters** (off by default) — shows up to 3 character aliases for the scene with `+N` overflow badge
- `_applyListColStyle()` updates a dedicated `<style id="list-col-style">` element with a dynamic `grid-template-columns` value whenever the column set changes

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
