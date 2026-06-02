# Changelog

## 2026-06-01 — Add hash-based re-linking for moved/renamed assets (PRD §10b)

- **`App.Relink` module**: new IIFE added after `App.Hasher`. `relinkMissingAssets()` re-attaches scenes whose stored `asset.path` no longer resolves to a present file, by matching their stored `asset.hash` (SHA-256) against currently-present files. Updates `scene.asset.path` / `asset.filename` on match.
- **Cost control**: only runs when at least one re-linkable missing scene exists (path absent from `fileHandleCache` *and* `asset.hash` non-empty). Hashes only *candidate* files — present files whose path is not referenced by any scene (the only paths a moved file could now occupy). Hashing yields to the event loop every 10 files so the UI stays responsive on large folders. The common nothing-moved case does zero extra hashing and returns immediately.
- **No-guess safety**: a hash claimed by more than one missing scene, or matched by more than one present file, is treated as ambiguous and left missing. Scenes whose hash has no present match also stay missing.
- **Ordering**: runs in `_enterProject` *before* `reconcileScenes`, so a moved file re-attaches to its existing scene instead of spawning a duplicate empty scene for the new path. `reconcileScenes` then only adds scenes for genuinely new files. Mutations go through `App.State.mutateProject` so the re-link is saved (and undoable post-load).
- **Cache consistency**: `fileHandleCache` is rebuilt by `enumerateImages` on scan and already holds the new paths, so no re-keying is needed — stale old-path entries simply vanish on rebuild.
- **"Re-link" header button**: added before "Prefill…"; re-scans the folder (`enumerateImages`), runs the re-link pass, reconciles, re-renders, and re-hashes in the background. Disabled while running. Useful for files moved while the app is open.
- **`App.Toast` module + `#toast` element**: new transient bottom-center status message (3.5 s auto-dismiss). Reports how many assets were re-linked on project open and on manual re-link (and "No missing assets to re-link" when none).
- **CSS**: `#toast` / `#toast.show` rules added near the `.file-missing` badge style.

## 2026-06-01 — Add "Prefill from Filenames" dialog for heuristic metadata pre-fill

- **`App.Prefill` module**: new self-contained IIFE module added after `App.BatchEdit`. Tokenizes each scene's `asset.path` (splits on `/`, `_`, `-`, `.`, and camelCase boundaries; lowercases; drops pure-numeric tokens and tokens shorter than 2 chars) and maps tokens to metadata fields via an editable `TOKEN_RULES` table.
- **Token → field mapping table** (`TOKEN_RULES`): covers `shot.type` (`wide/ws`, `medium/mid/ms`, `closeup/cu/close/clos`, `pov`, `detail/extreme/ecu`), `shot.transition` (`cut`, `fade`, `dissolve`, `wipe`), and `contentRating` (`explicit/nsfw`, `suggestive`, `tasteful`, `neutral/safe/sfw`). The constant lives at the top of the module and is clearly marked as the edit point.
- **Character matching**: separately checks whether any scene path token (≥3 chars) appears in the tokenized name+alias of any project character. Matches add a `{characterId, pose:'', expression:''}` entry only when `scene.characters` is currently empty.
- **"Only empty" guarantee**: `_computeChanges` checks the current field value before producing any suggestion; fields that are already set are skipped entirely. The apply step also skips characters already present in `scene.characters`.
- **Preview pane**: right-hand pane of the dialog shows per-field rows with scene count and value breakdown (e.g. `Shot Type  12 scenes  wide ×8, medium ×4`) before any change is made. Footer shows `N of M scenes would be updated`. Apply button stays disabled until at least one match is found.
- **Scope pane**: left-hand pane reuses `batch-dir-row` / `batch-all-row` / `batch-scope-pane` CSS and the same folder-map pattern from `App.BatchEdit`. One-time `addEventListener` wiring (not per-`open()`) avoids duplicate listener accumulation.
- **Single undo snapshot**: apply calls `App.State.mutateProject` once, which pushes a full deep-clone snapshot before mutating. Ctrl+Z reverts the entire batch atomically.
- **"Prefill…" header button**: added before "Batch Edit" in `header-btns`; wired in the header wiring section via `App.Prefill.open()`.
- **CSS**: nine new rules under `/* PREFILL FROM FILENAMES DIALOG */` for `.prefill-field-row`, `.prefill-field-name`, `.prefill-field-count`, `.prefill-field-detail`, `.prefill-no-match`, and `#prefill-dialog`.

## 2026-06-01 — Add "Next untagged" jump control with live count and `N` hotkey

- **"Next ⊘" button**: added to the header toolbar immediately after the Jump-to-img widget. Clicking it (or pressing `N` when focus is not in an input/textarea/select) selects the next scene in flat sequence order whose status is missing or `'untagged'`, starting after the currently selected scene and wrapping around to the beginning.
- **Wrap-around search**: iterates through all scenes in `App.Seq.flatScenes(project.sequence)` order. If the current selection is mid-list it picks up from the next slot; if nothing is selected it starts from index 0.
- **View-aware scrolling**: in Focus view calls `App.Grid.render()` to re-center (identical to the Jump-to-img behavior); in Grid/List calls `scrollIntoView({ behavior: 'smooth', block: 'center' })` on the scene card.
- **"All tagged" feedback**: when every scene has a non-untagged status the button briefly flashes "All tagged ✓" and is disabled for 1.8 s, then reverts — no navigation occurs.
- **Live "N left" count**: a small `<span id="next-untagged-count">` next to the button shows `${n} left` (hidden when zero), updated on every `projectChange` event.
- **`N` hotkey**: a dedicated `keydown` listener inside the IIFE guards against modifier keys and active input elements, then calls `jumpToNextUntagged()`.

## 2026-06-01 — Add keyboard triage mode for fast status tagging in Focus view

- **Triage hotkeys**: in Focus view, keys `1` / `2` / `3` set the center scene's status to `included` / `maybe` / `excluded`; `0` or `` ` `` resets it to `untagged`. Keys are silently ignored when focus is in an input, textarea, or select.
- **Auto-advance**: after any triage key, the view automatically navigates forward one unit (reuses `_focusNavigate(1)`), so the user can sweep a large library without touching the mouse.
- **Branch support**: when centered on a branch unit, the status key applies to the active lane's current scene (`_focusBranchData.lanes[activeLaneIdx][laneCenterIdxs[activeLaneIdx]]`).
- **Undo behavior**: uses `mutateProjectCoalesced` keyed on `'triage'`. Rapid key presses within 750 ms coalesce into a single undo step; pausing longer than 750 ms between presses starts a new step. This gives clean Ctrl+Z behavior for a sweep without generating hundreds of undo entries. Chosen over per-key `mutateProject` precisely because triage is a flow operation, not a deliberate per-scene edit.
- **Immediate visual feedback**: `mutateProjectCoalesced` fires `projectChange` synchronously, which triggers `render()` → `_renderFocus()` and updates the status border before navigation begins.
- **Legend**: `_buildFocusNavBar` now appends a separator and a `<span class="focus-nav-triage-legend">` reading `1 incl · 2 maybe · 3 excl` at the right end of the nav bar. Styled at 10 px in `var(--text-2)` to be discoverable without competing with the nav buttons.

## 2026-06-01 — Coalesced undo for text-field edits with live stat refresh

- **`App.State.mutateProjectCoalesced(fn, key)`**: new helper that pushes ONE undo snapshot at the start of each typing burst (identified by a stable `key` string), then coalesces all subsequent keystrokes on the same key within 750 ms. Deep clone only happens once per burst, not per keystroke. Emits `'projectChange'` on every call so sidebar coverage percentages update live.
- **Burst reset on undo/redo**: `restoreProject` now clears the coalesced key/timer, ensuring the first edit after an undo always starts a fresh undo entry.
- **`_mutateTextBox` (editor panel)**: routed through `mutateProjectCoalesced`. Swatch color clicks get an explicit key (`sceneId:tb:boxId:color`); text field inputs get `sceneId:tb:boxId:field`.
- **`_mutateFocusTextBox` (focus view)**: same approach — coalescing key passed from both the swatch click handler and the input handler.
- **`_onFieldInput` text fields** (mood, notes, `video.motionPrompt`, `video.sequenceId`): replaced direct project mutation with `mutateProjectCoalesced` keyed on `sceneId:field:fieldName`.
- **`_onCharFieldInput`** (character pose/expression): replaced `mutateProject` (one snapshot per keystroke) with `mutateProjectCoalesced` keyed on `sceneId:char:idx:field`.
- **`_renderFocus` guard**: skips the focus-view rebuild when `document.activeElement` is inside a `.focus-text-boxes-panel`, so the user's cursor and text selection survive the `projectChange`-triggered re-render while typing.

## 2026-06-01 — Fix delete confirm copy, rejoin auto-link, and branch-lane group depth

- **Delete confirm copy**: changed "This cannot be undone." to "You can undo this." since `mutateProject` always pushes an undo snapshot before the delete.
- **Rejoin auto-link**: `insertNode('rejoin')` now scans backwards through its parent array at insert time and sets `branchSplitId` to the nearest preceding unmatched `branch_split` (one not already claimed by another rejoin in the same array). If none exists, `branchSplitId` stays null. Renderer logic untouched.
- **Branch-lane group depth**: `_buildBranchSection` now accepts and forwards a `depth` argument to `_renderSequenceInto`, and the call site in `_renderSequenceInto` passes the current `depth` through. Groups nested inside branch lanes now increment depth correctly instead of always drawing at depth-0 styling.

## 2026-06-01 — Fix focus view wheel scroll swallowing events over text box panel

- **Scrollable panel passthrough**: the `wheel` listener on `#image-grid` now checks whether the event originated inside a `.focus-text-boxes-panel` that has overflow content (`scrollHeight > clientHeight`). If so, it skips `preventDefault()` and scene navigation, letting the panel scroll natively.
- **No behavior change elsewhere**: wheel over the image area or a non-scrollable panel still advances/retreats scenes as before.

## 2026-05-20 — Add "Jump to img" number input in header toolbar

- **New jump widget**: a compact number input labeled "Img" sits between the Undo/Redo buttons and the view switcher in all views. Entering a number and pressing Enter (or blurring) selects the nth *included* image in unfiltered sequence order and scrolls it into view (or re-centers the focus filmstrip on it).
- **Total count display**: a "/ N" span next to the input shows the live count of included images, updated on every render.
- **Narrowed project title**: `#project-title` max-width reduced from 260 px to 160 px to reclaim header space for the new widget.

## 2026-05-20 — Text box UI tweaks: inline placement and reduced color palette

- **Text boxes below active image**: in branch focus view, the color/header/text panel now appears directly below the active lane's current image (inside the main mini-cell) rather than at the bottom of the branch cell. In flat focus view it was already inline — no change there.
- **Reduced color palette**: trimmed from 16 to 12 colors. Removed lime, teal, cyan, and magenta (indistinguishable mid-shades). Renamed silver → gray, indigo → purple to match user-facing names.
- **Color migration**: `migrateProject` now remaps removed color names (silver, indigo, lime, teal, cyan, magenta) to their nearest kept equivalent so existing saved data is not broken.

## 2026-05-20 — Redesign branch focus view as a single filmstrip slot

- **Branch as one slot**: a `branch_split` now appears as a single unit in the 5-slot focus filmstrip instead of replacing the whole view. In far/near positions it shows a ⑂ branch icon; when it reaches the center slot it expands into the dual-track view.
- **Virtual nav sequence**: `_buildFocusNavSeq` builds a flat navigation list from the project sequence treating each `branch_split` as one entry. Scenes inside branch lanes are excluded from this list and only accessible via the branch center.
- **Dual-track center**: when the branch is centered, the center cell shows two stacked horizontal mini-strips (one per lane), each with 3 slots — previous · current · next. Active lane is full opacity with the text boxes panel below; passive lane is 45% opacity and fully clickable.
- **Fixed outer context**: while navigating inside a branch, the pre- and post-branch scenes stay anchored in the near-left and near-right slots throughout.
- **Exit on overflow**: pressing ← at the first lane scene or → at the last exits the branch and moves to the adjacent nav unit (which becomes the new center).
- **Lane switching**: Up/Down arrows or clicking the passive lane track switches the active lane.
- **Recovery**: if the selected scene is inside a branch when focus mode is entered, the branch is automatically located and entered.

## 2026-05-20 — Fix toolbar layout shift and rewrite branched focus view

- **Toolbar layout fix**: moved the Collapse/Expand tree controls to after the view-toggle pill in DOM order so they disappear to the right (not the left) when hidden in focus mode. Undo → Redo → view-toggle now always occupy a fixed left position regardless of view.
- **Branched focus view rewrite**: when the selected scene is inside a `branch_split`, focus view now renders two stacked horizontal strips (one per lane) instead of a thumbnail grid. Each strip shows the same 5-slot layout as flat focus (far · near · center · near · far). The active lane is full-opacity with the text boxes panel; passive lanes are 45% opacity.
- **Pre/post branch anchoring**: the scene immediately before the branch appears in the near-left slot when centered on the first lane scene; the scene after the branch appears in the near-right slot when at the last lane scene.
- **Escape navigation**: pressing ← past the first lane scene or → past the last lane scene exits the branch and opens the pre/post branch scene in flat focus view.
- **Lane switching**: Up/Down arrow keys cycle through lanes; clicking any cell in a passive lane switches to that lane centered on the clicked scene.
- **State persistence**: lane center positions are preserved across re-renders so passive lanes remember where you left off.
- **`_findBranchContext` rewrite**: now returns `{ branchEl, preBranchScene, postBranchScene }` and always finds the innermost branch (depth-first recursion before checking each level).

## 2026-05-20 — Show editable text boxes in focus view

- **Focus view text panel**: the current (center) scene now shows its text boxes below the image. Each entry displays 16 color swatches, a header input, and a text textarea — all editable in place, saving immediately on input.
- **Layout priority**: the image area uses `flex:1 1 0` so it shrinks to give the panel room; the panel has `min-height:80px` (≈3 lines) and scrolls when content exceeds `max-height:45%` of the cell.
- **Nav bar anchoring**: the ←/→ navigation bar now floats over the image portion of the current cell, not over the text panel.
- **Shared color table**: `TEXT_BOX_COLORS` hoisted to `App.TEXT_BOX_COLORS` / `App.TEXT_BOX_COLOR_HEX` so both the editor and focus view use the same source.

## 2026-05-20 — Redo support and header toolbar layout tweaks

- **Redo system**: added a redo stack to `App.Undo`. New mutations clear it; performing undo saves the current state onto the redo stack; `redo()` does the reverse. Keyboard shortcuts: Ctrl+Y and Ctrl+Shift+Z.
- **Header reorder**: Undo and Redo buttons now appear to the left of the view-toggle group (was: Undo appeared to the right). Order is now: tree controls → Undo → Redo → view toggle.
- **Larger view-toggle buttons**: padding increased from `4px 10px` to `7px 18px`, font size from 15px to 17px, with 12px margin on each side.

## 2026-05-20 — Replace single narrative field with multiple text boxes per scene

- **Data model**: `scene.narrative` (string) replaced by `scene.textBoxes` (array of `{ id, header, color, text }`). Each box has a free-form header label, one of 16 preset colors, and a text body.
- **Migration**: `migrateProject` auto-converts any scene with a `narrative` string into a single-entry `textBoxes` array on first load; `narrative` is then deleted.
- **Scene editor UI**: the narrative textarea is replaced by a dynamic list of text box entries. Each entry shows a row of 16 color swatches, a header input, a delete button (disabled when only one box remains), and a textarea. An "+ Add text box" button appends a new entry inheriting the last box's color.
- **List view**: the Narrative column previews the first non-empty box, prefixed with its header if set.
- **Stats**: narrative coverage now counts scenes with at least one text box containing non-empty text.
- **LLM export**: text boxes are emitted in order, each labeled by header (or "Narrator" if blank).

## 2026-05-20 — Add scroll wheel and nav buttons to focus view

- **Scroll wheel navigation**: scrolling down/up in focus mode advances or retreats by one image.
- **Navigation button bar**: a centered overlay bar at the bottom of focus view shows six buttons — ←100, ←10, ←1, 1→, 10→, 100→ — for jumping by 1, 10, or 100 images in either direction. Works in both flat and branched focus layouts.
- **`_focusNavigate(delta)` helper**: extracted from the existing keydown handler; shared by keyboard, scroll, and button navigation. Clamps to valid index range.
- **Cleanup**: nav bar is removed when switching away from focus mode via `_resetGridContainer`, `_renderGridView`, and `_renderList`.

## 2026-05-17 — Fix inline edit, add lane drops, improve DnD indicators

- **Group name inline edit fix**: added `mousedown`/`click` `stopPropagation` on the input element so clicks within the text field don't bubble to the header's collapse handler.
- **Branch lane drop zones**: lanes now accept drag-and-drop of scenes, selections, and groups. Added `data-lane-id`/`data-branch-id` attributes to lane divs, delegated dragover/drop handlers for `.seq-lane` targets, a `_resolveTargetSeq` helper for lane-aware insertion, and visual feedback (dashed outline + tinted background on hover). Empty lanes now show "Drop scenes here" text.
- **More prominent DnD indicators**: vertical card indicators now use a 6px bar with a blue glow spread; horizontal group indicators are 4px tall with stronger glow; group header drag-over outline is 2px.

## 2026-05-17 — Performance optimizations

- **Throttle concurrent thumbnail loads**: `App.LazyLoader` now limits to 4 simultaneous `handle.getFile()` calls via a queue, preventing saturation of the File System Access API when scrolling rapidly through hundreds of images.
- **Event delegation for card interactions**: replaced 6 per-card `addEventListener` calls in `_buildCard` (click, contextmenu, dragstart, dragover, drop, dragend) with a single set of delegated handlers on `#image-grid-inner`. Eliminates ~3000 closure allocations for large projects.
- **Deferred undo localStorage writes**: `App.Undo.push()` now debounces the `localStorage.setItem` call by 2 seconds, removing a synchronous multi-MB JSON serialization from the DnD hot path. Undo/pop still persists immediately.
- **Lazy-load group preview thumbnails**: collapsed group previews now route their thumbnail `<img>` elements through `App.LazyLoader.observe()` instead of eagerly calling `handle.getFile()`. Each preview thumb is wrapped in a `<div data-scene-id>` for LazyLoader compatibility.
- **Cache group scene counts**: `_buildSequenceNumbers` now also computes a `Map<groupId, sceneCount>` as a side-effect, eliminating redundant `flatScenes()` recursive walks in `_buildGroup`.

## 2026-05-16 — DnD indicator polish, selection persistence, Escape-to-clear

- **Vertical drop indicator between images**: replaced the full-width horizontal `.dnd-placeholder` line with a `box-shadow` side-bar on the hovered card (`-4px 0 0 var(--accent)` for before, `4px 0 0` for after). This gives a clear vertical line exactly between the two cards rather than a confusing row-wide stripe.
- **Horizontal indicator when dropping before a group**: group headers now split top/bottom — hovering the top half shows a `.dnd-h-indicator` horizontal line above the group (insert before); hovering the bottom half highlights the header as before (append to group). Groups can also be repositioned relative to each other this way.
- **Selection survives grouping**: `createGroupFromSelection` no longer clears `selectedCards` after the operation. The grouped scenes remain highlighted inside their new group, so the user can immediately act on them again.
- **Escape clears selection (undoably)**: pressing Escape when cards are selected pushes a full undo snapshot (including the current selection), then clears `selectedCards` and re-renders. Ctrl+Z restores both the project state AND the selection that was active before the clear. Individual Ctrl+click selection changes are NOT recorded in the undo stack; only the batch-clear is.
- **Undo snapshots include selection**: every `mutateProject` call now snapshots `{ project, selectedCards }` instead of just the project. Performing undo restores the project to its pre-mutation state AND re-applies the selection that was active at that moment.

## 2026-05-16 — Undo system, improved DnD, selection-aware movement buttons

- **Undo system**: `App.Undo` module with 50-step stack persisted per-project in `localStorage`. `mutateProject` pushes a deep snapshot before every mutation (except the initial `reconcileScenes` scan). `App.State.restoreProject()` restores a snapshot directly without triggering another undo push. The ↩ Undo button in the header is disabled when the stack is empty; Ctrl+Z (or ⌘Z) also triggers undo. The stack is loaded from localStorage when opening a project, so undo history survives page reloads.
- **Drag-and-drop overhaul** (`App.DnD` rewrite):
  - *Multi-image drag*: dragging a scene card that is part of a multi-selection drags the entire selection; dragging an unselected card drags only that card.
  - *Precision drop-line indicator*: a thin blue `.dnd-placeholder` bar (spanning the full grid row) appears between cards as you drag, showing exactly where images will land. Position is based on which half of the nearest card the cursor is in.
  - *Group drag*: group headers are now `draggable`. Dragging a group header and dropping it onto another group header nests it inside that group.
  - *Group header drop target*: dragging any scene(s) onto a group header highlights the header and appends the scenes to the end of that group on drop.
  - *Cross-group movement*: scenes can be dragged out of a child group and dropped into a parent group's scene grid for precise positioning — this was the primary missing use case.
- **Selection-aware ⇈↑↓⇊ buttons**: when one or more image cards are selected, the order buttons on every group header move the selection instead of the group. With no selection, the buttons move the group as before. Movement is per-parent-array: each parent that contains selected scenes is sorted independently.

## 2026-05-16 — Collapsed thumbnails 3+3, cutout sequence badges, header UX

- **Collapsed group preview now shows first 3 + badge + last 3** thumbnails (≤6 images → show all; >6 → first 3 · count badge · last 3). Thumb size reduced to 50×31 px.
- **Cutout sequence number badge** on every image card: semi-transparent gray pill centered on the image. The number is punched out as a transparent hole using CSS `isolation: isolate` + `mix-blend-mode: destination-out`, showing the image through the digit shapes. 1–2 digit numbers produce a circle; longer numbers auto-expand to an oval via `border-radius: 9999px` + `min-width: 28px`.
- **Global sequence numbering**: computed via `_buildSequenceNumbers()` — a depth-first walk that assigns 1…N across the entire project. Branch lanes each get their own letter suffix (lane 0 = `a`, lane 1 = `b`, …); both lanes start counting from the pre-split position; after rejoin the counter continues from the highest lane value.
- **Group header click-to-collapse**: the full header bar (except the name text and the order buttons) now toggles expand/collapse on click. The arrow is now a purely visual indicator (`pointer-events: none`). Group name is `flex: 0 0 auto` (shrinks to text width) with `margin-left: auto` on the count pushing the right-side controls to the far right — so only clicking the literal label text enters rename mode.

## 2026-05-15 — Fix grid filter, selection grouping, and add jump-to-top/bottom for groups

- **Grid view now respects filters**: extracted `_passesFilter(scene, filter)` helper; `_renderSequenceInto` calls it per scene so excluded (and other filtered-out) images are hidden in grid mode, not just list/focus mode.
- **`+ Group` button uses selection**: if any cards are selected, clicking `+ Group` now calls `createGroupFromSelection()` instead of making an empty group. `createGroupFromSelection` also now works with a single selected image (was requiring ≥ 2).
- **Jump-to-top/bottom buttons**: every group header now has ⇈ (move to top of its parent) and ⇊ (move to bottom) flanking the existing ↑/↓ step buttons. Same operations added to the right-click context menu.

## 2026-05-15 — Reimagine grid view as a scene-ordering engine with root container and depth-aware groups

- **Root "All Images" container**: the entire grid is now wrapped in a named root box with a thick accent border and large editable heading. Click the heading to rename it (stored as `project.rootName`, defaults to "All Images" for new and migrated projects).
- **Depth-aware group styling**: groups at depth 0 get a blue border and H2-sized (15px) label; depth 1 gets green + H3 (13px) with 16px left indent; depth 2+ gets amber/purple + H4 (12px) with further indent. Border color and font size signal hierarchy at a glance.
- **Inline rename — no more prompts**: clicking a group name swaps it for an in-place text input. Enter/blur commits; Escape cancels. `addGroupAfter` and `createGroupFromSelection` now auto-enter inline edit immediately after the group is created so you can name it without a second click.
- **↑ / ↓ reorder buttons**: every group header has subtle up/down arrow buttons that swap the group with its neighbour in the sequence array. Also accessible via "Move up" / "Move down" in the right-click context menu.
- **Collapsed preview shows scene count badge** (`N scene(s)`).
- Removed double-padding on `#image-grid-inner.grid-view` (was 8px inner + 8px outer; now uses only `#image-grid`'s 8px).

## 2026-05-15 — Editor selection/expand behaviour fixes

- **Editor no longer auto-expands on card click**: `open(sceneId)` now only auto-expands in list view; in grid and focus views it tracks the selected scene and updates the tab label without expanding the panel. The user must tap the tab strip to expand in those views.
- **Selection preserved on collapse**: `close()` no longer clears `selectedSceneId` or `_currentId`; collapsing simply hides the panel content while leaving the card highlight and scene tracking intact.
- Added `_expand()` — internal function called by the tab strip to force-expand the panel for the currently tracked scene regardless of view mode.
- Added `syncDetailMode(inList)` — called from `setViewMode` to keep the preview-pane `detail-mode` class correct when switching views without reopening the editor.
- Added `reset()` — full teardown (clears `_currentId`, clears `selectedSceneId`, resets tab label, collapses panel) called on project close via the home button; `close()` no longer does this.
- Arrow key navigation in focus mode calls `App.Editor.open()` (select-only, no expand) so the center scene can shift without forcing the editor open.

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
