# Requirements: simbox-web-design-prototype-zones-uiux

> Version: 1.0
> Status: APPROVED
> Last Updated: 2026-09-01

## Problem Statement

The legacy 2014 panel never shipped an admin page for **"Направления (DEF коды)"** — the table
that maps dialed-number patterns ("DEF codes," Asterisk dialplan extension patterns like
`_792109XXXXX`) to a named zone/direction (`megafon_spb`, `beeline_msk`, ...) used for call
routing (`Macro(makecall,<zone>,${EXTEN})`). The data exists, but only as ~9,000 hand-edited
lines spread across 25 raw Asterisk config files
(`legacy/simbox-desktop-v2014/asterisk/extensions/zones/extensions_*.conf`) with no UI at all —
adding, removing, or reviewing a zone's codes meant hand-editing dialplan text on the box.

This flow builds that missing admin page: import the full legacy dataset so it's populated from
day one (not empty demo data), and let an operator create/delete a zone and edit a zone's entire
DEF-code list through one multi-line textarea (one code per line) — matching how the user
describes the natural editing unit: not per-code CRUD rows, but "the whole list for one
direction, edited together."

`design/simbox-web-design-prototype-v2026`'s most recent precedent for "a new CRUD admin
section" is the **"Наборы команд"** feature (`lib/features/command_sets/`) — a
repository/controller/workspace architecture (searchable record list on the left, detail pane on
the right, draft-then-save editing, responsive narrow-width fallback) that superseded the
Panel/AdmButton-per-page style used elsewhere. This flow follows that same architecture for
consistency, scaled down to zones' simpler shape (a zone has a name and a list of code strings —
no commands, no response rules, no multi-section detail).

## User Stories

### Primary

**As an** operator setting up call routing
**I want** every zone the legacy system already routes calls for to be present and populated
with its real DEF codes the first time I open the page
**So that** I'm reviewing/adjusting an existing routing table, not rebuilding it from scratch

**As an** operator maintaining a zone's coverage
**I want** to open one zone and edit its whole DEF-code list in a single textarea (one code per
line), then save
**So that** adding a new prefix or removing a stale one is a quick text edit, not a sequence of
per-row add/delete actions

### Secondary

**As an** operator onboarding a new operator/region
**I want** to create a new zone (id/name) with an empty or pasted-in code list
**So that** I can add routing for a direction the legacy system's 25 files didn't cover

**As an** operator cleaning up
**I want** to delete a zone that's no longer needed
**So that** the list doesn't accumulate dead entries

## Acceptance Criteria

### Must Have

1. **Given** the app loads
   **When** the operator opens the new "Направления (DEF коды)" section from the sidebar
   **Then** every zone from the legacy `.conf` files is present, each showing its real DEF-code
   count and content — imported once at build time into a generated seed file (`lib/features/
   zones/seed.dart`), not fetched/parsed at runtime.

2. **Given** the 25 legacy `.conf` files
   **When** they're imported
   **Then** exact-duplicate pairs (an abbreviated filename like `bee_msk` and a full-name
   filename like `beeline_msk` whose code lists are byte-identical) collapse into **one** zone,
   keeping the fuller/canonical name — the one already used by `lib/data/icon_map.dart`'s
   `_naprMap`. This is not a coincidental naming overlap: **a zone in this new page *is* a
   "направление"** — the exact same thing the Sims table's `напр` column already shows one
   icon+letter-code for per SIM (e.g. the Beeline icon with a "С" mark = Билайн СПб, zone id
   `beeline_spb`). `_naprMap` is today's *display* catalog for that concept (one short code →
   icon + Russian name); this flow adds the missing *routing* layer underneath it — the actual
   list of DEF-code patterns that decides which zone/direction a dialled number belongs to.
   Every zone this page manages should use the same id, icon, and Russian name a SIM's `напр`
   cell would already show for it. Zones with no `_naprMap` entry yet (e.g. `all_spb`,
   `kievstar_ua` → `kievstar`, `rostel_spb_gor`) get a reasonable Russian display name and reuse
   an existing `assets/imgs/napravleine/*.ico` icon where one matches, falling back to the same
   "не определено" icon `_naprMap` already falls back to (`hz.ico`) otherwise.

3. **Given** the zone list (registry pane, left side, matching Наборы команд's layout)
   **When** the operator clicks "+ добавить" (or the mobile/narrow equivalent)
   **Then** a new zone is created with an id/name the operator supplies and an empty DEF-code
   list, and becomes the selected/editable zone.

4. **Given** a selected zone's detail pane
   **When** the operator opens its DEF-code editor
   **Then** they see one multi-line textarea pre-filled with every current code, one per line
   (no leading `_` dialplan prefix — that's serialization boilerplate, not the operator-facing
   value), with a live count ("128 кодов") and a Save/Cancel bar that only appears once the text
   differs from the saved value (matching Наборы команд's dirty-draft pattern).

5. **Given** the DEF-code textarea with unsaved edits
   **When** the operator clicks "Сохранить"
   **Then** the text is split into lines, blank lines are dropped, each remaining line is
   trimmed, and the zone's code list is replaced with the result — added lines are new codes,
   removed lines are gone, reordered lines reorder the list. No per-line syntax validation
   beyond "not empty" (an Asterisk pattern's `X`/`[a-b]`/etc. wildcard syntax isn't otherwise
   checked in this iteration — see Won't Have).

6. **Given** a zone's metadata (id/name)
   **When** the operator wants to rename it or, for a zone they created, change its id
   **Then** an edit-metadata affordance exists (matching Наборы команд's "Редактировать
   метаданные" pencil icon + dialog).

7. **Given** any zone
   **When** the operator chooses "Удалить" from its detail-header menu
   **Then** it's removed from the list after a confirmation (matching Наборы команд's delete
   dialog) — no "system/non-deletable" zone concept is needed here (unlike command sets' system
   fallback), every zone including imported ones may be deleted.

8. **Given** the zone list
   **When** the operator types in its search box
   **Then** it filters by id, name, and (loosely) region/operator hint — same behavior as
   Наборы команд's registry-pane search.

9. **Given** the app's left sidebar
   **When** this flow lands
   **Then** a new nav entry "Направления" appears (new `AdmPage.zones`), positioned near the
   other routing/plan-adjacent entries (proposing right after "Наборы команд" — see Open
   Questions), navigable and reachable the same way every other section is.

### Should Have

- Reuse `napravleine/*.ico` icons per zone in both the registry-pane row and the detail header,
  the same way the Sims table's `напр` column already does via `Ico.napr` — visually ties this
  new page to the direction icons the operator already recognizes elsewhere in the app.
- A "Сбросить демо-данные" reset action (matching Наборы команд's popup-menu reset item),
  restoring the full imported legacy dataset if the operator has been experimenting.

### Won't Have (This Iteration)

- No live Asterisk dialplan file generation/export — this stays a UI-only CRUD prototype over
  in-memory seed data, consistent with the rest of the app (`AppState`'s own
  `// TODO(api): replace with real exec transport` precedent). "Adding a code" here does not
  write to any `.conf` file.
- No DEF-code pattern syntax validation/linting (e.g. verifying `X`/`[a-b]` Asterisk wildcard
  syntax, detecting overlapping patterns across zones). Only "non-empty line" is enforced.
- No per-code metadata (price, description) — a code is just a string pattern, matching the
  legacy data exactly (one `exten =>` line held nothing but the pattern + a fixed macro call).
- No import/upload of a new `.conf` file from the UI — the legacy dataset is imported once,
  programmatically, into the committed seed file; new zones/codes are entered by hand via the
  textarea from then on.
- No change to the existing `напр` column / `Ico.napr` / `_naprMap` code-to-icon lookup on the
  Sims table — it keeps working exactly as it does today. This flow *reuses* its ids/icons/names
  as the canonical identity for each zone (they're the same directions, see Acceptance Criteria
  #2), and *adds* the DEF-code routing detail underneath, but doesn't modify that lookup, the
  Sims table, or how a SIM's own direction is displayed.

## Constraints

- **Technical**: same Flutter web prototype; new code lives under `lib/features/zones/`,
  mirroring `lib/features/command_sets/`'s file layout (`models.dart`, `repository.dart`,
  `controller.dart`, `seed.dart`, `workspace.dart`, `registry_pane.dart`, `detail_header.dart`,
  plus whatever the single-textarea detail body needs — likely one file, not command_sets'
  two-section split, since there's only one thing to edit).
- **Design source of truth**: `design/simbox-design-prototype-v2026-dc` for original tokens,
  but **`lib/features/command_sets/`'s already-implemented widgets are the closer, current
  reference** for this specific kind of page (list+detail, draft/save, `FugueIcon`,
  `T.denseHit`/`T.narrowHit`/`T.brandGradient`) — follow its established look, not the older
  `Panel`/`AdmButton` style used by Sims/Dongles/etc.
- **Logic/data source of truth**: `legacy/simbox-desktop-v2014/asterisk/extensions/zones/*.conf`
  (the 25 raw files) for the seed data; `lib/data/icon_map.dart`'s `_naprMap` for canonical zone
  ids, Russian names, and icon filenames where a zone already has an entry there.
- **Scope**: additive — no existing page, route, or shared widget changes except: registering
  the new `AdmPage.zones` enum value, a new sidebar entry, and a new `case` in `main.dart`'s
  page switch (mechanical, same shape as every prior page addition).

## Open Questions

- [ ] Sidebar position for "Направления" — proposing directly after "Наборы команд" (both are
  routing/plan-adjacent reference data, as opposed to live SIM/dongle operations). Confirm or
  specify a different slot.
- [ ] Exact final zone count after deduplication — I described the *rule* (collapse
  byte-identical abbreviated/full-name pairs, keep the canonical `_naprMap`-aligned name) rather
  than a hardcoded list; the precise resulting count (~18-19 zones) will be confirmed
  programmatically when the seed-generation script actually diffs the 25 files during
  Specifications/Implementation. Flagging so the number isn't a surprise later.
- [ ] Should zone `id` be freely editable after creation (like command sets' id, which — per
  `repository.dart`'s `replace()` — is actually **not** allowed to change once created,
  `'ID существующего набора нельзя изменить.'`)? Proposing the same rule for zones: id fixed
  after creation, only `name` (and the DEF-code list) editable thereafter — keeps the pattern
  consistent with the precedent and avoids dangling references if anything elsewhere ever keys
  off a zone id.

## References

- `legacy/simbox-desktop-v2014/asterisk/extensions/zones/*.conf` (25 files, ~9,013 lines) — raw
  DEF-code data, source of truth for content.
- `legacy/simbox-desktop-v2014/asterisk/extensions/extensions_dial_zones.conf` — the
  `Macro(makecall,...)` consumer, confirms each zone file's codes all target one zone name
  matching the filename.
- `lib/data/icon_map.dart`'s `_naprMap` — existing canonical zone id → (icon, Russian name) map,
  reused/extended here.
- `lib/features/command_sets/` (`models.dart`, `repository.dart`, `controller.dart`,
  `workspace.dart`, `registry_pane.dart`, `detail_header.dart`, `set_dialogs.dart`) —
  architecture and visual pattern this flow follows.
- `assets/imgs/napravleine/*.ico` — per-operator/region icon set, reused per zone.

---

## Approval

- [x] Reviewed by: Anton Dodonov
- [x] Approved on: 2026-09-01
- [x] Notes: Corrected mid-review — zones ARE directions (напр column concept), not a separate
  thing; see Acceptance Criteria #2. Three open questions proceed on stated defaults (sidebar
  slot after Наборы команд; zone count confirmed programmatically; id immutable after creation).
