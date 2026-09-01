# Specifications: simbox-design-prototype-fix1

> Version: 1.0
> Status: APPROVED
> Last Updated: 2026-09-01
> Requirements: [01-requirements.md](./01-requirements.md)
> Visual: [02-visual.md](./02-visual.md)

## Overview

`design/simbox-design-prototype/index.html` is one self-contained static HTML file (currently
917 lines): 11 screens, each a `<table>`-based dense grid + a row of filter/action cards, all
inline-styled, no build step. This spec covers the technical approach for all 8 acceptance
criteria from requirements, without changing that fundamental shape (one static HTML file +
`support.js` + `assets/`) — everything below is either inline `<style>`/`<script>` additions or
markup edits to `index.html`, plus a couple of asset additions.

## Affected Systems

| System | Impact | Notes |
|--------|--------|-------|
| `design/simbox-design-prototype/index.html` | Modify | All 8 ACs land here. ~917 → substantially larger given icon legends + JS added. |
| `design/simbox-design-prototype/assets/imgs/` | Modify | Fix wrong paths (flat vs nested), drop `pause2.png` reference, add any icons the column-parity audit finds missing. |
| `~/.claude/skills/nativemind-adminka/assets/adminka/adminka-to-fugue-map.json` | Already modified | `pause2.png` marked deprecated (done in Requirements phase). |
| `~/.claude/skills/nativemind-designsystem/assets/icons/icon-globe.svg` | Already added | New file (done in Requirements phase). |
| No new files planned | — | Hide/reorder + compact-mode JS lands as an inline `<script>` block in `index.html` itself (consistent with the file's existing all-inline-styles approach) rather than a new `.js` file — keeps the "one file" property intact. Open to revisiting in Plan phase if the script grows large enough to warrant `columns.js`. |

## Architecture

### Component diagram

```
index.html
├─ <style> (existing inline) + additions:
│    - .col-hidden[data-col]      -> display:none, targeted per table
│    - table[data-table] th, td   -> text-align:right (header + numeric cells)
│    - .mono                      -> ui-monospace stack, applied to identifier cells
│    - @container queries on .actions-row wrapper -> .compact-actions
│    - .lang-select / .lang-menu
├─ per-screen markup (11x):
│    - top bar: + <button class="lang-select">
│    - nav: "Свистки" -> "Модемы" text swap (nm/um screens' titles/H1 too)
│    - <table data-table="sim|dongle|...">  <- add data-table + data-col="<key>" per <th>/<td>
│    - + <button class="columns-btn">Columns</button> + <div class="columns-panel"> (hidden by default)
│    - icon legend block (expanded from existing "Примечание")
└─ <script> (new, appended before </body>):
     - COLUMN_DEFS[tableKey] = [{key, label}, ...]   // one array per table, seeded from legacy header order
     - initColumnsPanel(tableEl)     // reads/writes localStorage, wires checkboxes + drag handles
     - applyColumnState(tableEl, order, hidden)   // moves <td>/<th> DOM nodes + toggles display
     - initLangSelect()              // click-to-open menu, updates button label, no real i18n
```

### Data flow

```
localStorage["simbox-proto:cols:<tableKey>"] = { order: ["group","pro","cap",...], hidden: ["cap"] }
        |  read on page load
        v
applyColumnState() reorders <th>/<td> DOM nodes in every <tr> of that table to match `order`,
then adds/removes .col-hidden on cells whose key is in `hidden`
        ^
        |  write on every checkbox toggle / drag-drop
        |
columns-panel UI (checkboxes = hidden, [::] handles = order)
```

## Interfaces

### New JS surface (inline `<script>`, vanilla, no dependencies)

```js
// One definition per table, in legacy header order (source of truth: sim.php etc header row).
// This array *is* the "restore all legacy columns" fix from AC #8 made concrete: every column
// the audit confirms legacy has, gets an entry here, in legacy order, whether or not the
// pre-fix prototype had it.
const COLUMN_DEFS = {
  sim:    [{key:'group', label:'group'}, {key:'pro', label:'pro'}, /* ... ~38 entries ... */],
  dongle: [/* ... */],
  // one entry per table screen
};

function initColumnsPanel(tableEl, tableKey) { /* reads localStorage, renders panel, wires events */ }
function applyColumnState(tableEl, order, hiddenSet) { /* DOM cell reorder + display:none toggle */ }
function initLangSelect(rootEl) { /* open/close menu, update button label + aria-selected */ }
```

### Modified markup pattern (per table cell)

Before:
```html
<td style="...">group</td>
...
<td style="..."><img src="assets/imgs/pause2.png" style="width:14px;"></td>
```

After:
```html
<th data-col="group" style="text-align:right;...">group</th>
...
<td data-col="group" style="..."><img src="assets/imgs/pause.png" width="16" height="16"
    style="image-rendering:pixelated;"></td>
```

`data-col` is the join key between markup, `COLUMN_DEFS`, and localStorage state — every `<th>`
and every `<td>` in a table carries the same `data-col` value in a given column.

## Data Models

### `localStorage` schema

```ts
type ColumnsState = {
  order: string[];    // data-col keys, in display order (full set incl. hidden)
  hidden: string[];   // subset of `order` currently hidden
};
// key: `simbox-proto:cols:${tableKey}`  e.g. "simbox-proto:cols:sim"
```

No language state persisted — per requirements this is visual/state-only, resets on reload
(simpler, and avoids implying the switcher does something real across sessions).

### Icon rendering — corrected from the requirements-phase draft

Requirements AC #1 said "16/32/48 `srcset` triplet." Checking
`nativemind-adminka/assets/adminka/adminka-to-fugue-map.json` per-icon `resolution` field
during this phase found that's not quite right for every icon — refining, not reversing, the
same intent (no CSS-blurred upscaling):

| Icon's `resolution` in the map | Rendering rule |
|---|---|
| `16x16` (native GostSimBox hand-drawn art, no real higher-res source) | `<img width="16" height="16" style="image-rendering:pixelated">` on the **single** 16px file. No `srcset` — there's nothing to switch to. `pixelated` alone makes the browser use nearest-neighbour at any DPR, matching `guidelines/adminka-icons.html`'s documented default. |
| `32x32`, `status_2x: replaced_with_32x32` (Fugue-2x-sourced — real extra density, not upscaled) | `<img width="16" height="16">` on the file **as-is**, no `pixelated` — the file already has 2x-real detail baked in, downsamples cleanly per `nativemind-fugue-icons/SKILL.md`'s sizing rule. |
| New `icon-globe.svg` | Inline `<img>`/`<svg>` at `width="16" height="16"`, vector — scales natively, no density concern. |

So: no icon in this prototype actually needs a literal multi-file `srcset`; the map's
`resolution` field tells us which one-line rendering rule to apply per file. This still fully
satisfies the user's actual ask ("32×32 on retina, 16×16 on standard density, size chosen by
screen density") — that behavior falls out of `width/height=16` + the correct `pixelated`
flag, because a `32x32`-resolution source file naturally supplies real 2x density when the
browser needs it, without any explicit density-switching markup.

## Behavior Specifications

### Happy path — columns panel

1. Operator clicks "Columns (32/38)" above a table.
2. Panel opens showing every `COLUMN_DEFS[tableKey]` entry as a checkbox + drag handle, in
   current `order`, checked unless in `hidden`.
3. Unchecking a box immediately hides that column (`applyColumnState` re-runs, `localStorage`
   updated) — no "Apply" button, changes are live.
4. Dragging a row (via `[::]` handle, native HTML5 drag-and-drop, no library) to a new position
   reorders `order` and re-runs `applyColumnState` — header and every data row's matching cell
   move together, since both live under the same `data-col`.
5. Closing the panel (click outside / Esc) leaves the state applied; reopening the panel later
   or reloading the page restores it from `localStorage`.
6. "Reset" restores `order`/`hidden` to `COLUMN_DEFS`'s default (legacy order, nothing hidden).

### Happy path — compact actions row

1. Actions-row wrapper has `container-type: inline-size`.
2. Above the container-query breakpoint (draft: 480px per action-card container — exact number
   tunable in Plan/Implementation, not load-bearing here): cards render as today (label +
   input/button).
3. Below the breakpoint: `.compact-actions` styles apply — button/link text is visually hidden
   (`title` attribute carries the same text for a native tooltip), icons stay.
4. Filter panel (`Редактирование`) is explicitly excluded from `.compact-actions` — its inputs
   keep labels always, per requirements AC #4 ("filter controls remain reachable... never
   icon-only"). It simply stacks below the icon row when space is short, via normal flex-wrap.

### Happy path — language selector

1. Button shows globe icon + `EN` + caret, in the shared top bar.
2. Click opens a menu with the 5 languages, `English` checked.
3. Click an option: menu closes, button label updates to that language's 2-letter code,
   checkmark moves — no page content changes (Won't Have: real translation).

### Edge Cases

| Case | Trigger | Expected Behavior |
|------|---------|-------------------|
| Hide every column | Operator unchecks all boxes | `id`/checkbox column stays pinned+visible always (excluded from `COLUMN_DEFS`, not hideable) — table never becomes fully empty/unusable. |
| Drag column to same position | No-op drop | `order` unchanged, no redundant `applyColumnState` re-render (avoid layout thrash). |
| `localStorage` unavailable (private browsing / disabled) | `localStorage.setItem` throws | Catch and no-op — panel still works for the session via an in-memory fallback object, just doesn't persist across reload. Never let a storage error break the table. |
| Very narrow viewport (< compact breakpoint even for the icon row) | Phone-width access to an admin panel | Icon row itself wraps to 2 lines (normal `flex-wrap`, already a fallback) rather than overflowing/scrolling the page horizontally. |
| Columns panel open + window resized past the actions-row breakpoint simultaneously | Two independent responsive systems on screen at once | They're independent (`data-col` visibility vs. `@container` on actions-row) and don't interact — no shared state to reconcile. |

### Error Handling

| Error | Cause | Response |
|-------|-------|----------|
| Corrupt/stale `localStorage` value (e.g. `order` references a `data-col` that no longer exists after this fix adds/removes columns) | Schema drift between prototype versions | On load, filter `order`/`hidden` against the current `COLUMN_DEFS[tableKey]` keys; drop unknown keys, append any new legacy-sourced keys not yet in a stored `order` to the end. Never throw, never blank the table. |

## Dependencies

### Requires

- Column-parity audit results (in progress, background agents — see
  `_status.md` for live status) to finalize each table's `COLUMN_DEFS` entries and confirm
  every icon path fix before Plan phase task breakdown.

### Blocks

- Plan phase (needs `COLUMN_DEFS` per table finalized, which needs the audit).

## Integration Points

### Internal Systems

- `nativemind-adminka` skill assets (`assets/adminka/`) — icon source of truth, already has one
  patch (`pause2.png` deprecated) from this flow.
- `nativemind-designsystem` skill (`icon-density.html` rule, new `icon-globe.svg`).
- `_ds_bundle.js` / `support.js` (existing prototype tooling) — no changes needed; new `<script>`
  is independent vanilla JS appended to the page, doesn't touch the DC-runtime plumbing.

## Testing Strategy

### Manual Verification

- [ ] For each of the 11 screens: open Columns panel, hide 2-3 columns, reload page, confirm
      state persisted.
- [ ] Drag-reorder 2 columns, confirm header + every visible data row moved together.
- [ ] Resize browser window down past the actions-row breakpoint, confirm action buttons go
      icon-only with working `title` tooltips, filter panel stays labeled.
- [ ] Zoom/DPR check (e.g. Chrome device toolbar at 2x/3x) that `pixelated` icons stay crisp,
      Fugue-2x-sourced icons stay smooth (no visible upscale blur either way).
- [ ] Confirm "Свистки" no longer appears anywhere in the file (`grep -c "Свистки" index.html`
      returns 0) and "Модемы (nm)"/"Модемы (um)" appear in nav on all 11 screens + both screen
      titles.
- [ ] Language menu opens/closes, selecting an option updates the button label only.
- [ ] `grep` confirms no remaining reference to `pause2.png` in `index.html`.

## Column-Parity Audit Results (AC #8) — all 4 background agents complete

Legend: 🔴 wrong/missing icon (small, localized) · 🟠 missing column(s) · 🔵 structural
misalignment · ⚪️ whole section/table missing.

### 01 · Симки (`sim.php`) — 41 columns checked, 7 issues

| # | Column | Issue |
|---|---|---|
| 1 | group icon, row 2 | 🔴 `pause2.png` used; legacy `html_group()` only ever emits `pause.png` for that state (pre-confirmed, already fixed in the global skill's provenance map). |
| 2 | cap icon, row 2 | 🔴 `qos/capnew.png` used; `sim.php`'s inline cap logic only ever emits `capok.png`/`capfail.png` — `capnew.png` belongs to `plan.php`'s unrelated per-plan "NEW capacity" flag, not this column. |
| 3 | dongle-model/power + simst/srvst + dongle-path + ussd&sms/calls block | 🔵 Header row only has 2 `<td>` for this 4-column block (data rows correctly have all 4). Every header label from "tot" onward is shifted 2 columns left of the data it labels — **not cosmetic**, the header literally mislabels the data underneath it. |
| 4 | PDDAS | 🟠 Body still renders a value in that slot; header cell for `PDDAS` is missing entirely (compounds #3's shift). |
| 5 | pri | 🟠 Column (always-empty in legacy, but real) dropped entirely — header + body cell both absent. |
| 6 | LIMIT2, LIMIT3, LIMIT4, LIMIT5 | 🟠 4 columns entirely absent (only LIMIT0/LIMIT1 kept); legacy has 6. |

Everything else (34 of 41 columns) confirmed OK — icons/conditions match `html.php` exactly,
order matches legacy.

### 02 · Свистки/Модемы normal mode (`dongle.php`) — 26 columns, 3 issues

| # | Column | Issue |
|---|---|---|
| 1 | SIM-status icon (`html_simst`, 3rd of 4 leading icon slots) | 🟠 Missing column — legacy keys off `$simst`/`$pinrequired` (`state/simst/{0,1,4,16,255,-1}.ico`). |
| 2 | Service-status icon (`html_srvst`, 4th slot) | 🟠 Missing column — legacy keys off `$srvst`/`$simst` (`state/srvst/{0,1,2,112,-1}.ico`). |
| 3 | RSSI, sample row 1 | 🔴 Shows `rssi-3.ico` + "-71dBm"; formula (`rssi*2-113`) implies `rssi-4.ico` for that dBm value. Sample-data-only, low priority. |

This confirms and sharpens the requirements-phase finding: the "2 missing header columns" are
specifically the SIM-status and service-status icon columns.

### 03 · Свистки/Модемы update mode (`diagmode.php`) — 6 columns, 0 issues

Fully matches legacy: same 6 columns, same order, correct status icons. One cosmetic-only note:
prototype drops the `<a href="dmlog.php">` wrapper around the log icon (no data/column impact).

### 04 · Хабы (`hubs.php` + `readers.php`) — ⚪️ 1 entire table + 3 panels missing

- USB tree portion (from `hubs.php`): faithful, icons/order correct. **OK.**
- **`readers.php`'s entire SIM-reader table is not rendered anywhere on the screen** — 11
  columns (checkbox, `pl2303.ico` model icon, Ридер id, `lock.png`, state, SPN, ICCID, PIN,
  IMSI, KI, progress, dataport) plus its 3 action panels ("PIN", "Поиск KI",
  "APDU-команда") are completely absent from the reconstruction. This isn't a column tweak —
  it's a missing second table+panel-set on this screen.

### 05 · Наборы команд (`nabor.php`) — 0 issues

Single-column table, exact match.

### 06 · Планы (`plan.php`) — ⚪️ far larger than the known `msm.ico` gap

Block order that *is* present matches legacy sequence (no reordering issue) — but most blocks
are missing most of their columns:

| Section | Legacy has | Prototype keeps | Gap |
|---|---|---|---|
| SATT | `may.ico`, `mon.ico`, `msm.ico` + `sms_out.png`×2, `nospam.ico`, 4 soft/hard day/total fields (11 total) | SATT_soft/SATT_hard text only | 🟠 9 columns missing (incl. the known `msm.ico`) |
| Directions (4× алг/nodiff/limit_soft/limit_hard) | 16 columns | Only "Направление 1"'s alg/limit_soft/limit_hard | 🟠 13 of 16 missing — Directions 2-4 entirely gone |
| Timing (diff_slow, diff_min×4, diff_min_sout, diff_min_imode) | 7 | 5 | 🟠 2 missing |
| Time (work wake/sleep, holiday wake/sleep) | 4 | 2 | 🟠 2 missing (holiday) |
| Modes (can_in/out/sout, iVIP/notVIP/iGOO/iNOR/iBAD/iNE0/iNEC/iNEM/iNEW/iNOS/iBLO/iROB, capnew/fail/ok, IMN/B/C/D/E) | 23 | 6 (can_in, can_out, iVIP, iGOO, iNOR, iBAD) | 🟠 17 missing |
| IATT (soft/min/max, OUT_IN_ANS/DUR, IN/OUT_ACD_MIN/MAX + 6 icon columns) | 15 | 3 (soft/min/max text only) | 🟠 12 missing, incl. **all 6** icon columns |
| iVIP column | `imgs/ivip.png` | `assets/imgs/qos/ivip.png` | 🔴 wrong path |
| Header icons (diff_slow/diff_min*/time_work_*) | composite icons above label | text-only | 🔴 icons dropped |
| Group super-header row (Направление 1-4, need_in.png, state_sout_{in,out}.ico, satt.png banner) | present (plan.php:300-324) | absent | ⚪️ missing |

Net: Планы kept roughly a fifth of its legacy columns. This is not a small fix — but per user
decision (2026-09-01), it's in scope for this iteration, not split off.

### 07 · Процессы, 08 · Биллинг, 09 · Обновление, 10 · Debug — 0 issues

All four fully match legacy (button lists/order, the one real data table on Биллинг with 4
columns, log-dump sections). Биллинг's `state_sout.png` usage (flagged for verification in the
audit brief) is confirmed **correct**, not a bug.

### Scope decision (confirmed 2026-09-01)

The requirements-phase finding ("2 known gaps: msm.ico, 2 dongle columns") undersold the actual
gap by roughly an order of magnitude on two screens (Планы, Хабы). **Anton confirmed: full
restoration of both stays in this fix1 iteration**, not split into a follow-up flow. Симки and
Свистки(nm)'s issues (7 and 3 respectively) were already going to be fixed as targeted edits;
Планы and Хабы now get the same treatment at larger scale.

Architecturally this doesn't add new patterns — every missing block/column/panel on Планы and
Хабы follows the exact same markup shape as the rows/panels that already exist elsewhere in the
prototype (a `<td>` per column, an icon `<img>` where legacy has one, an action-panel `<div>`
per button group). It's a volume increase (~60-80% more markup on 2 screens), not a new
architecture — the Plan phase breaks it into one task per missing block, each citing the
specific legacy PHP reference from the audit table above.

## Open Design Questions

- [ ] Exact compact-mode breakpoint pixel value (draft 480px) — fine-tune visually during
      Implementation once real content is in the container-query context.
- [x] Final `COLUMN_DEFS` per table — resolved, see "Column-Parity Audit Results" above; all 4
      background audits complete.
- [x] Планы/Хабы restoration scope — resolved 2026-09-01, full restoration stays in this
      iteration (see "Scope decision" above).

---

## Approval

- [x] Reviewed by: Anton Dodonov
- [x] Approved on: 2026-09-01
- [x] Notes: Approved as drafted, including full Планы/Хабы restoration scope.
