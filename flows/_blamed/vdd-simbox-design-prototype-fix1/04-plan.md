# Implementation Plan: simbox-design-prototype-fix1

> Version: 1.0
> Status: APPROVED
> Last Updated: 2026-09-01
> Specifications: [03-specifications.md](./03-specifications.md)

## Summary

Everything lands in `design/simbox-design-prototype/index.html` (single static file) plus the
two global-skill edits already made in Requirements phase. Order of work: (1) shared chrome
first since it's small and touches every screen — good to validate the "repeated block" edit
pattern early — (2) per-screen column-parity restoration (the bulk of the work, Симки/Свистки
are targeted, Планы/Хабы are large), (3) cross-cutting table UX infrastructure (alignment/mono,
columns hide/reorder, icon rendering rules, legend) applied once each table's final column set
is correct, (4) verification pass against the specs doc's manual checklist.

## Task Breakdown

### Phase 0: Already done (Requirements phase)

- `nativemind-adminka/assets/adminka/adminka-to-fugue-map.json` — `pause2.png` marked deprecated.
- `nativemind-designsystem/assets/icons/icon-globe.svg` — created.

No action needed; listed for completeness so Phase 1+ tasks below can reference them as done.

### Phase 1: Shared chrome (all 11 screens)

#### Task 1.1: Rename "Свистки" → "Модемы"
- **Description**: Nav short forms `Свистки (nm)`/`Свистки (um)` → `Модемы (nm)`/`Модемы (um)`
  on all 11 repeated nav bars; screen titles "02 · Свистки (normal mode)" / "03 · Свистки
  (update mode)" → "02 · Модемы (normal mode)" / "03 · Модемы (update mode)"; the two H1s
  inside those screens too. Routes (`/?p=dongle`, `/?p=diagmode`) unchanged.
- **Files**: `design/simbox-design-prototype/index.html` — Modify (~26 occurrences per earlier
  grep: 11 nav bars × up to 2 mentions each, + 2 titles + 2 H1s).
- **Dependencies**: None.
- **Verification**: `grep -c "Свистки" index.html` → 0. `grep -c "Модемы" index.html` matches
  expected count.
- **Complexity**: Low (mechanical find/replace, but must hit every repeated nav bar).

#### Task 1.2: Language selector in shared top bar
- **Description**: Add globe-icon button (`icon-globe.svg`) + current-language code + caret to
  the top bar (hostname/IP/version/uptime row), repeated on all 11 screens. Click opens a menu
  with English (default)/ไทย/Русский/हिन्दी/中文; selecting one updates the button label only
  (no real i18n — Won't Have per requirements). Inline `<style>`/`<script>` additions, vanilla
  JS, no dependencies.
- **Files**: `design/simbox-design-prototype/index.html` — Modify (top-bar markup × 11, shared
  CSS/JS added once).
- **Dependencies**: None (independent of 1.1).
- **Verification**: Open/close menu on 2-3 different screens, confirm consistent behavior;
  confirm no page content/layout shifts when a language is selected (visual-only per spec).
- **Complexity**: Low-Medium (new small JS component, but simple and self-contained).

### Phase 2: Column-parity restoration (per screen, from the audit in 03-specifications.md)

#### Task 2.1: Симки — icon fixes + header realignment + missing columns
- **Description**:
  1. `pause2.png` → `pause.png` (row 2, group column).
  2. `qos/capnew.png` → correct `capok.png`/`capfail.png` per `$cap` state (was borrowed from
     the wrong screen's icon vocabulary).
  3. Add the 2 missing header `<td>` for the dongle-model/power + simst/srvst block — fixes the
     2-column label shift affecting every header from "tot" onward.
  4. Add missing `PDDAS` header cell (body value already exists, was orphaned).
  5. Add `pri` column (header + always-empty body cell, matches legacy).
  6. Add `LIMIT2`, `LIMIT3`, `LIMIT4`, `LIMIT5` columns (header + body, same `ipalevo.png` +
     `limit.N`/`limit_max.N` pattern as the existing `LIMIT0`/`LIMIT1`).
  7. Fix flat-vs-nested icon path inconsistency (`assets/imgs/state_in.png` etc. → nested
     `assets/imgs/state/state_in.png` etc., matching `nativemind-adminka`'s folder structure).
- **Files**: `design/simbox-design-prototype/index.html` — Modify (Симки table, ~lines 56-220).
- **Dependencies**: None.
- **Verification**: Header cell count matches legacy's 41; every header label sits above its
  matching data; re-run a targeted diff against `sim.php`'s header row.
- **Complexity**: Medium (multiple small fixes in one table, header/body cells must move
  together).

#### Task 2.2: Свистки (nm) — missing status icon columns
- **Description**: Add SIM-status icon column (`html_simst` logic: `state/simst/{0,1,4,16,
  255,-1}.ico`) and service-status icon column (`html_srvst`: `state/srvst/{0,1,2,112,-1}.ico`)
  — the 3rd and 4th of the 4 leading icon slots in `dongle.php`'s header, currently only 2
  exist. Fix sample-row RSSI icon (`rssi-3.ico` → `rssi-4.ico` for the -71dBm sample value).
- **Files**: `design/simbox-design-prototype/index.html` — Modify (Свистки/Модемы nm table,
  ~lines 354-519).
- **Dependencies**: Task 1.1 (rename) touches the same screen's title/nav — do 1.1 first to
  avoid re-touching the same region twice.
- **Verification**: Header cell count matches legacy's 26; icons render for both new columns
  across sample rows.
- **Complexity**: Low-Medium.

#### Task 2.3: Свистки (um) — cosmetic only (optional)
- **Description**: Restore `<a href="dmlog.php">` wrapper around the log icon. No column/data
  impact — Should Have, not Must Have.
- **Files**: `design/simbox-design-prototype/index.html` — Modify (~lines 520-540).
- **Dependencies**: Task 1.1.
- **Verification**: Visual only.
- **Complexity**: Low. **Can be deferred/skipped without breaking any acceptance criterion.**

#### Task 2.4: Хабы — restore readers.php's entire SIM-reader table + 3 action panels
- **Description**: `hubs.php`'s USB tree is already correct (no change needed). Add the
  missing `readers.php` table: 11 columns (checkbox, `pl2303.ico` model icon, Ридер id,
  `lock.png`, state, SPN, ICCID, PIN, IMSI, KI, progress, dataport) — a new table section on
  the screen, not a column tweak to the existing tree. Add the 3 action panels from
  `readers.php` lines ~249-304: "PIN", "Поиск KI", "APDU-команда" (same panel-card pattern as
  existing action panels elsewhere in the file — copy the shape, not the specific fields).
- **Files**: `design/simbox-design-prototype/index.html` — Modify (Хабы screen, ~lines
  541-581 today, will grow substantially).
- **Dependencies**: None.
- **Verification**: All 11 columns present with legacy-matching icons/labels; 3 action panels
  present with legacy's field sets.
- **Complexity**: High (new table + 3 new panels from scratch, largest single content task
  besides Планы).

#### Task 2.5: Планы — restore to legacy column parity (largest task, split into sub-steps)
- **Description**: Per the audit table in `03-specifications.md` § "06 · Планы", restore in
  this order (each sub-step independently verifiable against `plan.php`):
  - **2.5a SATT block**: add missing `msm.ico` (already known) + `sms_out.png`×2 (soft/hard),
    `nospam.ico`, and the 4 soft/hard day/total fields (9 columns total).
  - **2.5b Directions 2-4**: replicate the "Направление 1" алг/nodiff/limit_soft/limit_hard
    block 3 more times (13 columns) — same shape as Direction 1, different plan-field keys.
  - **2.5c Timing + Time**: add `diff_min_sout`, `diff_min_imode` (timing) and holiday
    wake/sleep (time) — 4 columns, same pattern as existing siblings.
  - **2.5d Modes**: add the 17 missing flags (notVIP, iNE0/iNEC/iNEM/iNEW, iNOS/iBLO/iROB,
    capnew/capfail/capok, IMN/IMB/IMC/IMD/IME) alongside the 6 already present.
  - **2.5e IATT**: add the 12 missing fields, including **all 6** icon columns
    (forwarding/outin/conn/rand/in_wait/in_sound) — currently only soft/min/max text exists.
  - **2.5f Icon fixes**: `imgs/qos/ivip.png` → `imgs/ivip.png` (wrong path); restore composite
    header icons for diff_slow/diff_min*/time_work_* (currently text-only labels).
  - **2.5g Group super-header row**: restore the Направление 1-4 / `need_in.png` /
    `state_sout_{in,out}.ico` / `satt.png` banner row (`plan.php:300-324`), currently absent.
- **Files**: `design/simbox-design-prototype/index.html` — Modify (Планы screen, ~lines
  607-746 today, will grow substantially — likely the largest single edit in this flow).
- **Dependencies**: None, but do 2.5a-2.5g in order (each builds visual/structural context for
  the next; g depends on a-e existing to have something to head).
- **Verification**: Column-by-column re-check against the audit table; spot-check a couple of
  rows' worth of sample data for each restored block.
- **Complexity**: High (largest content-volume task in the whole flow — consider running as
  its own sub-plan/checklist during Implementation given the 7 sub-steps).

### Phase 3: Table UX infrastructure (cross-cutting, all 11 screens — do after Phase 2 so
column sets are final and `data-col` tagging only happens once per cell)

#### Task 3.1: `data-col` + `data-table` tagging
- **Description**: Add `data-table="<key>"` to each `<table>` and `data-col="<key>"` to every
  `<th>`/`<td>` within it, across all 11 tables — the join key for alignment CSS, mono CSS, and
  the columns-hide/reorder JS in later tasks. Do this in the same editing pass as Task 3.2
  (right-align/mono) to avoid touching every cell twice.
- **Files**: `design/simbox-design-prototype/index.html` — Modify (all tables).
- **Dependencies**: Phase 2 complete (final column sets must be stable before tagging).
- **Verification**: Every `<th>` has a unique `data-col` within its table; every `<td>` in a
  row has the same `data-col` sequence as its table's header.
- **Complexity**: Medium (mechanical but must cover ~11 tables × up to ~50 columns).

#### Task 3.2: Right-aligned headers + monospace identifiers
- **Description**: `text-align:right` on table headers (matching already-right-aligned numeric
  cell content); `.mono` class (`ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation
  Mono", monospace`) on identifier cells — IMEI, IMSI, ICCID, phone numbers, dongle path,
  counters — across all tables.
- **Files**: `design/simbox-design-prototype/index.html` — Modify (shared `<style>` + per-cell
  class additions).
- **Dependencies**: Task 3.1 (uses the same cells being tagged).
- **Verification**: Visual — headers align to their right-aligned data; identifier columns'
  digits line up vertically across rows.
- **Complexity**: Low-Medium.

#### Task 3.3: Icon rendering correction (density-correct markup)
- **Description**: Per-icon, per `nativemind-adminka/assets/adminka/adminka-to-fugue-map.json`'s
  `resolution` field: `16x16`-resolution icons get `width="16" height="16"
  style="image-rendering:pixelated"`; `32x32`-resolution (Fugue-2x-sourced) icons get
  `width="16" height="16"` with no `pixelated`. Applies to every `<img src="assets/imgs/...">`
  in the file (currently inconsistent inline `width` values like `14px`/`16px`/`13px`/`12px`).
- **Files**: `design/simbox-design-prototype/index.html` — Modify (every icon `<img>`, all
  screens).
- **Dependencies**: None, but do after Phase 2 so newly-restored icons (Планы/Хабы) get this
  treatment too rather than needing a second pass.
- **Verification**: Zoom/DPR check (browser devtools device toolbar at 2x/3x) — 16x16-sourced
  icons stay crisp square pixels, 32x32-sourced icons stay smooth, neither blurs.
- **Complexity**: Medium (high cell count, but same one-line fix pattern repeated).

#### Task 3.4: Columns hide/reorder control
- **Description**: `COLUMN_DEFS` JS object (one entry per table, from Task 3.1's `data-col`
  keys, in legacy header order); `initColumnsPanel`/`applyColumnState` functions;
  `localStorage`-backed state (`simbox-proto:cols:<tableKey>`); "Columns (N/M)" button +
  panel UI per table (checkboxes to hide, `[::]` drag handles to reorder, native HTML5
  drag-and-drop, no library); checkbox/id column pinned and non-hideable.
- **Files**: `design/simbox-design-prototype/index.html` — Modify (new `<script>` block near
  `</body>`, new button+panel markup per table, new `<style>` rules).
- **Dependencies**: Task 3.1 (`data-col` must exist first).
- **Verification**: Per specs doc's manual checklist — hide/show, drag-reorder, reload
  persistence, corrupt-localStorage fallback, all-hidden-except-checkbox edge case.
- **Complexity**: High (the one genuinely new piece of interactive JS in this flow).

#### Task 3.5: Adaptive actions + filter row
- **Description**: `container-type: inline-size` on the actions-row wrapper; `@container`
  query (draft breakpoint 480px, tune visually) toggling `.compact-actions` — button/link text
  hidden via CSS (kept in `title` attr) below the breakpoint, icons stay. Filter panel
  explicitly excluded from compact collapse (always keeps labels, per requirements) — just
  wraps below the icon row via existing `flex-wrap` when space is short.
- **Files**: `design/simbox-design-prototype/index.html` — Modify (shared `<style>` +
  action-panel wrapper markup, all screens with action panels).
- **Dependencies**: None (independent of 3.1-3.4).
- **Verification**: Resize browser width past the breakpoint — actions go icon-only with
  working tooltips, filter stays labeled and never goes icon-only.
- **Complexity**: Medium.

#### Task 3.6: Icon legend expansion
- **Description**: Expand each screen's "Примечание" block into a categorized icon-meaning
  table (grouping per `nativemind-adminka/guidelines/adminka-icons.html`), one row per icon
  actually used on that screen, meaning text taken verbatim/translated from `sim.php` /
  `modules/html.php` / the relevant screen's PHP legend where one exists.
- **Files**: `design/simbox-design-prototype/index.html` — Modify (notes section per screen).
- **Dependencies**: Phase 2 complete (icon set per screen must be final) + Task 3.3 (reuses the
  same density-correct `<img>` markup pattern).
- **Verification**: Every icon used in that screen's table appears in its legend with correct
  meaning text, traceable to the legacy source cited in Requirements/Specifications.
- **Complexity**: Medium (volume across 11 screens, but mechanical once the pattern is set on
  the first screen).

### Phase 4: Verification pass

#### Task 4.1: Run the full manual checklist from 03-specifications.md
- **Description**: Every item in "Testing Strategy → Manual Verification" — columns
  persistence, drag-reorder, compact-mode resize, DPR/zoom icon check, `Свистки`/`pause2.png`
  greps, language menu, plus a final full re-read of the file for anything the phased edits
  might have left inconsistent (e.g. a screen's nav bar missed in Task 1.1).
- **Files**: None (verification only).
- **Dependencies**: All prior phases.
- **Verification**: Is the verification.
- **Complexity**: Low-Medium (mostly time, not difficulty).

## Dependency Graph

```
Task 1.1 ─┬─→ Task 2.2 ─┐
Task 1.2 ─┘             │
                         ├─→ Task 3.1 ─┬─→ Task 3.2
Task 2.1 ────────────────┤             ├─→ Task 3.4
Task 2.4 ────────────────┤             └─→ Task 3.6 (also needs 3.3)
Task 2.5 (a→b→c→d→e→f→g) ┤
                         │
                         └─→ Task 3.3 ─→ Task 3.6
Task 3.5 (independent) ──────────────────────────┐
                                                   ↓
                                            Task 4.1 (final verification)
```

## File Change Summary

| File | Action | Reason |
|------|--------|--------|
| `design/simbox-design-prototype/index.html` | Modify (extensively) | Every task above — the single target file. |
| `nativemind-adminka/assets/adminka/adminka-to-fugue-map.json` | Already modified | `pause2.png` deprecated (Requirements phase). |
| `nativemind-designsystem/assets/icons/icon-globe.svg` | Already created | Language selector icon (Requirements phase). |

No other files. No new assets expected — the column-parity restoration reuses existing icons
already vendored in `design/simbox-design-prototype/assets/imgs/` (same files the legacy PHP
already references); if the Implementation phase finds a genuinely missing icon file, that's a
new open question at that point, not assumed here.

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Планы restoration (2.5a-g) introduces new column-order or icon-mismatch bugs of its own, given its size | Medium | Medium | Verify each sub-step against the audit table before moving to the next; don't batch all 7 sub-steps into one unreviewed edit. |
| Touching the same repeated block (nav bar, top bar) 11 times risks one screen being missed | Medium | Low | Task 1.1/1.2 verification is a `grep -c` count check specifically to catch a missed occurrence. |
| `data-col` tagging (3.1) happening after Phase 2 means large diffs land before the tagging that makes them independently toggleable — a mid-flow interruption would leave columns restored but not yet hide/reorder-able | Low | Low | Acceptable interim state — restored columns render correctly even before Task 3.1-3.4 land, they just aren't hideable yet. Not a broken state. |
| Container-query breakpoint choice doesn't feel right until real content is in place | High (expected) | Low | Explicitly called out as tunable in both specs and this plan — not a blocker, adjust visually during 3.5. |

## Rollback Strategy

Single file, plain git-trackable HTML — standard `git diff`/`git checkout` per task or per
phase if something regresses. No data migration, no build artifacts, no external state beyond
the two already-applied global-skill edits (which are additive/non-breaking — `pause2.png`
marked deprecated but not removed; `icon-globe.svg` is a new file, nothing depends on its
absence).

## Checkpoints

After each phase, verify:

- [ ] Phase 1: `Свистки` grep-clean, language menu opens/closes on 3 sample screens.
- [ ] Phase 2: Each restored screen's column count matches its legacy header count (see audit
      table for exact numbers: Симки 41, Свистки/nm 26, Хабы +11 (reader table), Планы full
      column set per the 06 · Планы audit table).
- [ ] Phase 3: Columns panel works on at least Симки + one other table; DPR check passes;
      compact-mode resize works on at least one screen with action panels.
- [ ] Phase 4: Full manual checklist from specs doc passes.

## Open Implementation Questions

- [ ] Планы's sub-steps (2.5a-g) may reveal further small discrepancies once actually building
      the markup (the audit was read-only analysis, not a byte-for-byte transcription) — treat
      any new finding the same way as the audit's existing findings (fix + note in the
      implementation log), don't silently skip.

---

## Approval

- [x] Reviewed by: Anton Dodonov
- [x] Approved on: 2026-09-01
- [x] Notes: Approved as drafted.
