# Product Requirements Document
## Storyboard Editor — Visual Novel Asset Pipeline Tool
**Version:** 0.1 (Draft)
**Status:** In Progress

---

## 1. Overview

A browser-based local tool for organizing, tagging, and sequencing a large library of images (and eventually video clips) into a structured metadata format consumable by an LLM for visual novel game development. The tool is the first stage of a two-stage pipeline: human-curated metadata in, AI-assisted game script out.

---

## 2. Goals

- Reduce token cost of AI-assisted game development by doing heavy asset organization work outside of LLM context
- Produce a clean, versioned JSON schema that can be handed directly to an LLM as structured context
- Support a linear graphic novel workflow now, with extensibility toward branching narratives, gamification, and video generation in future versions
- Require zero installation beyond a modern browser (Chrome/Edge required for File System Access API)

---

## 3. Non-Goals (v1)

- Branching logic editor (schema placeholder only)
- Gamification system (schema placeholder only)
- Video playback or editing
- AI-assisted auto-tagging (future feature)
- Multi-user or cloud sync

---

## 4. Users

Single user. The tool is personal and local. No authentication, no accounts.

---

## 5. Technical Constraints

- Delivered as a single self-contained HTML file
- Vanilla JS only — no frameworks, no build step, no server
- File System Access API for local folder access (Chrome/Edge only; this is a known and accepted limitation)
- All data persisted in a single JSON file saved alongside the image folder
- No network requests in v1

---

## 6. Core Concepts

### Project
A named collection of scenes tied to a local image folder. One project = one JSON file.

### Scene
The atomic unit of the storyboard. One scene = one image (or one video clip in future). Scenes are ordered by their position in the scenes array — no explicit order field.

### Character
A named participant in the story, defined once at the project level and referenced by ID within scenes. Characters can be playable (protagonist perspectives) or NPCs.

### Video Sequence
A grouping of multiple scenes intended to be rendered as a single continuous video clip. Each scene in a sequence carries a motion prompt describing its contribution to the clip.

---

## 7. Data Schema

```json
{
  "project": {
    "id": "uuid",
    "title": "string",
    "version": "1.0.0",
    "created": "ISO8601",
    "modified": "ISO8601"
  },

  "characters": [
    {
      "id": "uuid",
      "name": "string",
      "role": "protagonist | npc",
      "playable": true,
      "description": "string",
      "tags": []
    }
  ],

  "scenes": [
    {
      "id": "uuid",
      "status": "included | excluded | maybe",

      "asset": {
        "filename": "string",
        "path": "string",
        "type": "image | video",
        "hash": "string",
        "duration": null
      },

      "contentRating": "explicit | suggestive | tasteful | neutral",

      "perspective": "characterId | null",

      "characters": [
        {
          "characterId": "uuid",
          "pose": "string",
          "expression": "string"
        }
      ],

      "shot": {
        "type": "wide | medium | closeup | pov | detail",
        "transition": "cut | fade | dissolve | wipe | none"
      },

      "narrative": "string",
      "mood": "string",
      "notes": "string",

      "video": {
        "sequenceId": "uuid | null",
        "indexInSequence": 0,
        "motionPrompt": "string"
      },

      "audio": null,

      "alternateOf": "sceneId | null",

      "tags": [],

      "branch": null,
      "gamification": null
    }
  ]
}
```

---

## 8. Features — v1

### 8.1 Project Management
- Create new project (prompts for folder selection and project title)
- Open existing project (loads JSON from folder)
- Auto-save on every change
- Project title editable in-app

### 8.2 Image Browser
- Load all images from selected local folder via File System Access API
- Display images as a scrollable grid (filmstrip view)
- Lazy-load thumbnails for performance across 2000+ images
- Visual status indicator per image (included = green, excluded = red, maybe = yellow, untagged = grey)
- Click image to open Scene Editor panel
- Drag-and-drop to reorder scenes
- Bulk actions: mark selected as included / excluded / maybe
- Filter view by: status, content rating, tagged/untagged, character present

### 8.3 Scene Editor Panel
Appears as a side panel or modal when a scene is selected. Contains:

- **Image preview** (full-size)
- **Status toggle** — included / maybe / excluded
- **Content rating** — dropdown: explicit / suggestive / tasteful / neutral
- **Perspective** — dropdown of defined characters + "none"
- **Characters present** — multi-select from character list; per-character pose and expression text fields
- **Shot type** — dropdown: wide / medium / closeup / pov / detail
- **Transition** — dropdown: cut / fade / dissolve / wipe / none
- **Narrative** — large textarea (the on-screen text for this scene)
- **Mood** — freeform text field
- **Notes** — private production notes textarea
- **Video sequence** — assign to a sequence ID, set index, write motion prompt
- **Alternate of** — link to another scene ID
- **Tags** — freeform tag input with autocomplete from existing tags
- **Filename / hash** — read-only display

### 8.4 Character Manager
- Define characters with name, role, playable flag, description, tags
- Edit and delete characters
- Character list accessible from sidebar

### 8.5 Export
- Export full project JSON (all scenes including excluded)
- Export filtered JSON (included scenes only, in array order)
- Export LLM prompt package: filtered JSON + a plain-text summary of project structure intended for pasting directly into an LLM context window

### 8.6 Statistics Panel
- Total scenes, included count, excluded count, maybe count, untagged count
- Coverage: % of included scenes with narrative text, with characters assigned

---

## 9. Features — Future Versions

### v2 — AI Integration
- "Describe this image" button: sends image to Anthropic API, populates description and suggests tags
- Batch describe: processes a selected subset of images
- API key stored in localStorage (user-supplied)

### v3 — Branch Logic Editor
- Visual node graph for defining scene branches
- Condition builder (flag-based, stat-based)
- Populates the `branch` field in schema

### v4 — Gamification Layer
- Define player stats, inventory, skills at project level
- Per-scene stat modifiers and item triggers
- Populates the `gamification` field in schema

### v5 — Video Pipeline
- Group scenes into video sequences visually
- Export video generation prompt bundles per sequence
- Preview mode: plays sequence of images as slideshow with timing

---

## 10. UI Layout

```
┌─────────────────────────────────────────────────────┐
│  [Project Title]          [Stats] [Export] [Settings]│
├──────────┬──────────────────────────────────────────┤
│          │                                          │
│ Sidebar  │  Image Grid (filmstrip / grid toggle)   │
│          │                                          │
│ Characters│  [img][img][img][img][img][img][img]   │
│ Sequences │  [img][img][img][img][img][img][img]   │
│ Filters  │                                          │
│          ├──────────────────────────────────────────┤
│          │  Scene Editor Panel (slide-in on select) │
│          │                                          │
└──────────┴──────────────────────────────────────────┘
```

---

## 10b. File System Behavior

### Recursive Folder Scanning
The image folder may contain nested subdirectories (e.g. `Images/00-prelude/`, `Images/01-chapter/`). The app must recursively walk the entire directory tree from the selected root folder and discover all image files regardless of nesting depth. Subfolder paths should be preserved in the `asset.path` field and optionally surfaced as a filter or grouping in the UI.

Supported image extensions to scan for: `.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`

### File Handle Persistence and Permission Recovery
File System Access API permissions are session-scoped and do not persist across browser restarts or new tabs. The app must handle this gracefully:

- On load, if a project JSON is found but the folder handle is stale, prompt the user to re-grant access to the same folder with a clear explanation of why
- If a specific image file cannot be found at its stored path (moved, renamed, deleted), display a missing asset indicator on that scene card rather than erroring silently
- The `asset.hash` field exists to help detect file identity even if the filename changes — implement hash comparison as a fallback for re-linking missing assets

---

## 11. Resolved Decisions

- **Excluded scenes** are hidden from the grid by default. A toggle in the filter menu reveals them in-place with a visual indicator (red border/overlay). They remain in the JSON and in array order.
- **Multiple projects** are supported via a simple project switcher screen shown on load (list of recently opened JSON files + "Open folder" + "New project"). No persistent app state required — the user navigates their filesystem. Simplicity over convenience.
- **Drag-and-drop reordering** applies to all scenes regardless of status. Excluded scenes are hidden by default but their array position is preserved and reorderable when revealed.
- **LLM export format** is annotated markdown — a human-readable document that describes the project structure, character roster, and each included scene in sequence with all metadata fields labeled. Designed to be pasted directly into an LLM context window as a briefing document.
