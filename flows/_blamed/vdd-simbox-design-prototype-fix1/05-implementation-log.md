# Implementation Log: simbox-design-prototype-fix1

> Started: 2026-09-01
> Plan: [04-plan.md](./04-plan.md)

## Progress Tracker

| Task | Status | Notes |
|------|--------|-------|
| 1.1 Rename Свистки→Модемы | Done | 24 occurrences renamed, grep-clean |
| 1.2 Language selector | Done | Added to all 10 top bars (screen 11 has no top bar) |
| 2.1 Симки fixes | Done | Header now 43 cells, matches all 3 body rows |
| 2.2 Модемы (nm) icon columns | Done | Header+rows now 26 cells each |
| 2.3 Модемы (um) log link | Done | Restored `<a href="dmlog.php">` wrapper |
| 2.4 Хабы readers table | Done | New 12-col table + 3 action panels added |
| 2.5a-g Планы | Done | Table rebuilt to 82 columns, matches `plan.php` exactly |
| 3.1 data-col/data-table tagging | Done | All 8 tables, colspan-aware, header/body parity verified |
| 3.2 Right-align headers + `.mono` | Done | Shared CSS + per-cell class, done alongside 3.1 |
| 3.3 Icon rendering correction | Done | All 162 `<img>` tags, 0 unresolved fallbacks |
| 3.4 Columns hide/reorder | Done | 7/8 tables (Наборы команд excluded, no id/no use case) |
| 3.5 Adaptive actions + filter row | Done | 4 actions-rows, 480px breakpoint, icon-btns only |
| 3.6 Icon legend expansion | Done | All 6 screens with icon-bearing tables |

## Session Log

### Session 2026-09-01 - Implementation agent

**Started at**: Phase 1, Task 1.1
**Context**: Fresh start on approved plan; index.html at 917 lines pre-edit.

#### Completed
- Task 1.1: Global `sed -i '' 's/Свистки/Модемы/g'` across `index.html`. Verified:
  `grep -c "Свистки"` → 0; `grep -o "Модемы" | wc -l` → 24 (10 nav bars × 2 mentions +
  2 screen titles + 2 H1s). Routes (`/?p=dongle`, `/?p=diagmode`) and `(nm)`/`(um)`
  suffixes untouched, as required.
  - Files changed: `design/simbox-design-prototype/index.html`
  - Verified by: grep counts above.

- Task 1.2: Added a `.lang-select` button+menu component to the shared top bar
  (hostname/IP/version/uptime row). Copied
  `~/.claude/skills/nativemind-designsystem/assets/icons/icon-globe.svg` to
  `design/simbox-design-prototype/assets/icon-globe.svg` (new asset file — required by
  the plan, not a deviation). Markup (button: globe icon + "EN" code + caret; menu:
  English/ไทย/Русский/हिन्दी/中文, English checked by default) inserted at the end of
  each of the 10 top-bar flex rows (right after the last `<span>`, so it lands at the
  right edge next to the date/uptime text). Added 3 CSS rules to the existing `<head>`
  `<style>` block (hover states + checkmark styling) and one vanilla `<script>` block
  before `</body>` wiring click-to-open/close, Escape-to-close, click-outside-to-close,
  and per-option selection (updates the button's code label + moves the checkmark; no
  page content changes — visual/state-only per requirements).
  - Files changed: `design/simbox-design-prototype/index.html`,
    `design/simbox-design-prototype/assets/icon-globe.svg` (new).
  - Verified by: `grep -c 'class="lang-select"'` → 10 (all top bars); visual read of
    the inserted markup at 3 sample locations (screens 01, 02, 06) confirms correct
    nesting inside the existing flex row, no broken tags.

#### Deviations from Plan
- Requirements/plan text says "repeated on all 11 screens" / "all 11 top bars," but
  screen 11 ("Диалоги — результаты действий") has no shared top bar row at all (it's a
  results-panel gallery, not a normal screen with hostname/nav chrome) — confirmed by
  re-reading the file structure. Applied the selector to all 10 screens that actually
  have a top bar (01–10). Flagging this as the resolution of requirements' open
  question "where exactly... in the top bar" is now moot since screen 11 has none to
  begin with; not treated as a gap since there's no top bar there to add it to.

#### Discoveries
- None yet beyond the above.

- Task 2.1: Симки table fixes, all 7 audit items addressed.
  1. Global `pause2.png`→`pause.png` fix (also caught the 2nd occurrence in the
     Планы "Отображение информации" panel, line 633, as instructed).
  2. `qos/capnew.png`→`qos/capfail.png` on row 2 (the row previously showing the
     wrong/nonexistent icon; `$cap` in `sim.php` only ever emits `capok.png` or
     `capfail.png`, never `capnew.png` — confirmed by reading sim.php:1374-1379).
     Row 2 already carries other "troubled SIM" signals (red balance diff, paused
     group icon), so `capfail.png` is the legacy-faithful choice for it.
  3. Inserted 2 empty `<td>` header cells before the existing "dongle" header
     cell — these align with the body's dongle-model+power icon cell and the
     simst+srvst status icon cell (confirmed via `sim.php:1678-1691`: legacy's
     4-cell dongle block is [model+power icons (no header text)] [simst+srvst
     icons (no header text)] [dongle path, labeled "dongle"] [ussd&calls icons
     (no header text)] — the existing "dongle" header label was correctly
     positioned for the 3rd body cell all along; the table just needed 2 more
     blank header cells ahead of it, not a rename).
  4. Added `PDDAS` header cell between `ASRL` and `PDDL0` (`sim.php:1132-1133`).
     No body edit needed for this one specifically — once the dongle-block fix
     (#3) landed, the body's previously-orphaned value naturally lines up under
     the new `PDDAS` header without moving.
  5. `pri` header cell — found ALREADY PRESENT in the file (contradicts audit's
     claim that both header+body were absent; flagging as a discrepancy, see
     below). Left the header cell as-is (no action needed) and inserted a
     genuinely empty `<td>` in the body of all 3 data rows at the `pri` position
     (`sim.php:1791` — legacy's pri cell is always empty, content is HTML-commented
     out) — the prototype had been showing a stray "5" value there before this fix
     (now that "5" reads as `PDDL1`'s value instead, one position earlier, which is
     a plausible minsec-style figure).
  6. Added `LIMIT2`/`LIMIT3`/`LIMIT4`/`LIMIT5` header cells after `LIMIT1`
     (`sim.php:1137-1142`) and matching empty `<td>` body cells in all 3 rows
     (`sim.php:1806-1811` — `ipalevo.png` + `limit.N`/`limit_max.N` pattern;
     left empty for all 3 sample rows since none of them have that palevo flag
     set, consistent with how LIMIT0/LIMIT1 already render conditionally).
  7. Fixed 2 flat `assets/imgs/state_out.png` / `state_wait.png` references in
     this table to the nested `assets/imgs/state/state_out.png` /
     `assets/imgs/state/state_wait.png` paths — confirmed the nested copies
     already existed in the prototype's own `assets/imgs/state/` folder (no new
     asset copy needed). Left the Планы screen's `state_in.png`/`state_out.png`
     (lines ~657-658, to be handled under 2.5g) and the Биллинг screen's
     `state_sout.png` (line ~804, audit explicitly confirmed correct/intentional,
     out of scope) untouched.
  - Files changed: `design/simbox-design-prototype/index.html`.
  - Verified by: `grep -c '<td'` on the header row and each of the 3 body rows
    all return 43, confirming header/body column-count parity across the whole
    table.

#### Discoveries
- The "pri" header cell was already present in the file before this session's
  edits, despite the audit table (03-specifications.md) stating it was "dropped
  entirely (header + body cell both absent)." Re-verified directly against the
  file rather than trusting the audit blindly. Treated as: header needs no
  change, body needed the always-empty cell added (which was genuinely missing).
  Flagging per the instructions ("if a decision only they can make... make the
  most legacy-faithful reasonable call... note it").

- Task 2.2: Модемы (nm) table. Confirmed against `dongle.php:337-364` (4 empty leading
  `<td>` before "Свисток") and `:508-535` (body order: checkbox, model icon
  (`html_dongle`), power icon (`html_cfun`), simst icon (`html_simst`), srvst icon
  (`html_srvst`), dongle path). Prototype only had 2 of the 4 leading icon slots
  (model+power); added 2 more empty header `<td>`s and the matching simst/srvst
  `<img>` cells in both body rows.
  - Row 1 (dongle0, idle/powered-on): `state/simst/1.ico` + `state/srvst/1.ico`
    (matches the same simst=1/srvst=1 "registered" combo already used for the
    equivalent SIM on the Симки screen).
  - Row 2 (dongle1, locked/powered-off): `state/-1.ico` for both slots (no SIM
    communication possible while locked/off — `html_simst`/`html_srvst` both
    return `state/-1.ico` for the "unknown" case per `modules/html.php:202,219`).
  - Also fixed the sample RSSI icon on row 1: `rssi/rssi-3.ico` → `rssi/rssi-4.ico`
    to match the displayed "-71dBm" value (formula `rssi*2-113` implies bucket 4).
  - Files changed: `design/simbox-design-prototype/index.html`.
  - Verified by: `grep -c '<td'` on header + both body rows all return 26,
    matching the audit's legacy column count for this table.

- Task 2.3: Модемы (um) — cosmetic fix. Wrapped both rows' `diagmode_log.png` icon
  in `<a href="dmlog.php">` per `diagmode.php:26`. No column/data impact.
  - Files changed: `design/simbox-design-prototype/index.html`.
  - Verified by: visual read of the edited rows.

- Task 2.4: Хабы — read `readers.php` in full (308 lines). USB tree table left
  untouched (already correct per audit). Added the entirely-missing SIM-reader
  table below it plus its 3 action panels, matching `readers.php:174-304`:
  - Table: 12 header `<td>` (checkbox, empty/model-icon slot, "Ридер", `lock.png`,
    state, SPN, ICCID, PIN, IMSI, KI, empty/progress slot, dataport —
    `readers.php:179-190`), 12 in each of 2 sample body rows (`:205-239`). Audit
    table said "11 columns"; direct read of the source shows 12 — used the
    source as authoritative. Row 1 = a connected/"ready" reader with sample
    ICCID/IMSI, `KI="00"` (legacy shows literal "00" for the all-zeroes/unset-KI
    case per `readers.php:224`), and a progress fraction; row 2 = a
    "Not connected" reader with all dependent fields blank, matching legacy's
    `file_get_contents_def2(...,"")` defaults for an unconnected reader.
  - Panels: "PIN" (снять/установить PIN, `readers.php:261-276`), "Поиск KI"
    (start button + the same red warning copy as `readers.php:16`,
    `:281-289`), "APDU-команда" (`readers.php:295-304`). Copied the existing
    "PIN" panel's card/input/button styling (border, radius, padding, font
    sizes) from the Модемы(nm) screen's PIN panel (line ~505 pre-edit) as
    instructed, with `readers.php`'s actual field/button labels substituted in.
  - Files changed: `design/simbox-design-prototype/index.html`.
  - Verified by: `grep -c '<td'` on header + both rows all return 12 (parity);
    Python div-open/close balance check across the whole screen block returned
    0 (no broken nesting from the insertion).

- Task 2.5 (a-g): Планы — read `plan.php` in full (994 lines) rather than only the
  audit's summary table, since the table's own scope note flagged it as
  "read-only analysis, not a byte-for-byte transcription." Confirmed the audit's
  overall shape but found several undercounts (consistent with the pattern
  already seen in Tasks 2.1/2.4 — noting each below rather than silently
  trusting the audit numbers). Given the volume (single table growing from 29
  to 82 columns), built it with a small generator script
  (`/tmp/.../scratchpad/gen_plans.py`, not committed to the repo — throwaway
  tooling) rather than dozens of manual edits, then spliced the generated HTML
  into `index.html` and hand-verified column counts and nesting afterward. Did
  not literally reproduce legacy's two-row `rowspan`/`colspan` header mechanism
  (`plan.php:219-414`) since the prototype's table doesn't use `rowspan`
  anywhere else — instead added the group banner as a genuinely new `<tr>`
  above the existing flat-header `<tr>`, using `colspan` only for the grouped
  blocks (directions/IATT/SATT) and leaving the rest of that row visually
  blank over the individually-already-labeled columns. This keeps the same
  markup shape as the rest of the file (flat per-column header) while still
  satisfying 2.5g's ask.
  - **2.5a SATT** (`plan.php:391-408`): legacy has 12 fields (may.ico, mon.ico,
    msm.ico, sms_out soft, sms_out hard, nospam.ico, SATT_soft,
    SATT_soft_day, SATT_soft_total, SATT_hard, SATT_hard_day,
    SATT_hard_total), not the audit's "11 total" — direct read used as
    authoritative. Old prototype had 4 (may, mon, SATT_soft, SATT_hard); all
    12 now present.
  - **2.5b Directions** (`plan.php:337-355` header, `:602-740` body): legacy
    is 4 directions × 4 fields (alg, nodiff, limit_soft/max, limit_hard) = 16.
    Found Направление 1 itself was missing `nodiff` in the old prototype (only
    alg/limit_soft/limit_hard existed, 3 not 4) — added it there too, plus all
    of Directions 2-4.
  - **2.5c Timing+Time** (`plan.php:439-458`): added `diff_min_sout`,
    `diff_min_imode` (timing now 7 total) and `time_holiday_wake`,
    `time_holiday_sleep` (time now 4 total).
  - **2.5d Modes** (`plan.php:259-288` header, `:470-591` body): legacy has 23
    flag columns (can_in, can_out, can_sout, iVIP, notVIP, iGOO, iNOR, iBAD,
    iNE0, iNEC, iNEM, iNEW, iNOS, iBLO, iROB, capnew, capfail, capok, IMN,
    IMB, IMC, IMD, IME) — the audit's own count ("17 missing... alongside 6
    already present" = 22) is short by one: `can_sout` appears in
    `plan.php`'s display loop (`:480-483`) but wasn't in either the audit's
    "present" or "missing" list. Added all 23, using legacy's actual
    checkbox-checked defaults (`plan.php:472-589`) for row 1 ("default" plan)
    and varied a handful for row 2 ("beeline_spb") for sample-data visual
    variety — flagged as invented-but-plausible, same as the rest of this
    prototype's fabricated sample data.
  - **2.5e IATT** (`plan.php:366-381` header, `:755-794` body): added all 12
    missing fields — `OUT_IN_ANS`/`OUT_IN_DUR`, `IN_ACD_MIN`/`MAX`,
    `OUT_ACD_MIN`/`MAX` (6 text fields) and the 6 icon toggle columns
    (`forwarding.png`, `outin.png`, `conn.png`, `rand.ico`, `in_wait.png`,
    `in_sound.png`) — IATT now 15 total (was 3).
  - **2.5f Icon fixes**: `qos/ivip.png` → `ivip.png` (root path, per
    `plan.php:262`) — applied in the new modes-section iVIP column and the
    diff_min_vip composite header icon. Restored the composite header icons
    for `diff_slow`/`diff_min*`/`time_work_*`/`time_holiday_*` (were text-only
    labels; legacy pairs 1-3 icons above each label per `plan.php:230-249`) —
    e.g. `diff_slow` = `state_wait.png`+`slow.png` above the label,
    `time_work_wake` = `pause.png`+`day_work.png`+`wake.png`, etc. Used the
    nested `assets/imgs/state/` path for `state_wait.png`/`state_sout.png`
    (rather than legacy's literal root-level `imgs/state_wait.png` string) for
    consistency with the flat→nested normalization already established in
    Task 2.1 and applied throughout this same table's modes section — flagged
    decision: prioritizing the adminka canonical asset layout over legacy's
    pre-reorg literal path here, same principle, not a new one.
  - **2.5g Group super-header row** (`plan.php:300-324`): new `<tr>` above the
    header row with `colspan` groups: blank spacer over the 5 core + 7 timing
    + 4 time + 23 modes columns (39, unlabeled — legacy doesn't label these in
    row 1 either, they're individually labeled), "Направление 1"–"Направление
    4" (colspan 4 each), `need_in.png` + "Запрос входящих" (colspan 5),
    `state/state_sout_out.ico` + "длит. исходящих" (colspan 2),
    `state/state_sout_in.ico` + "длит. входящих" (colspan 2), "Входящие"
    (colspan 6), `satt.png` + "SATT" (colspan 12). Colspan sum verified to
    equal 82 (the final column count) via script.
  - New asset copies: none — every icon referenced already existed in
    `design/simbox-design-prototype/assets/imgs/` (verified each of the ~35
    distinct icon paths with `ls`/`find` before using it); the two
    `state_sout_in.ico`/`state_sout_out.ico` files needed for 2.5g only exist
    nested (`assets/imgs/state/`), not at root — used the nested path, no copy
    needed.
  - Files changed: `design/simbox-design-prototype/index.html`.
  - Verified by: `grep -c '<td'` on the group-header row (colspan sum),
    detail-header row, and both data rows all resolve to 82; a first splice
    attempt left a duplicate stale group-header `<tr>` in place (caught by
    the `<td>`-count check showing 13 instead of 82 on what should have been
    the header row) — found and removed before finishing. Whole-file
    div-open/close, `<table>`-open/close, and `<tr>`-open/close counts all
    balanced after the fix (322/322, 8/8, 35/35).

**Ended at**: All Phase 1 and Phase 2 tasks (1.1, 1.2, 2.1-2.4, 2.5a-g) complete.
**Handoff notes**: Phase 3 (data-col tagging, right-align/mono CSS, icon
srcset/pixelated rules, adaptive actions row, icon legend expansion) and Phase 4
(verification pass) are explicitly out of scope for this session — next session
picks those up per 04-plan.md.

---

## Deviations Summary

| Planned | Actual | Reason |
|---------|--------|--------|
| Language selector on "all 11" top bars | Applied to 10 top bars | Screen 11 has no shared top bar markup to attach it to. |
| Task 2.1: pri header+body both missing per audit | Header already present; only body cell was missing | Direct file read contradicted the audit's claim; header needed no change. |
| Task 2.4: readers.php table is "11 columns" per audit | Built as 12 columns | Direct count of `readers.php:179-190` gives 12; audit undercounted by one. |
| Task 2.5d: Моды "17 missing flags... alongside 6 already present" (=22) per audit | Built as 23 total (18 new) | `can_sout` is a real legacy column (`plan.php:480-483`) omitted from both the audit's "present" and "missing" lists. |
| Task 2.5g: literal two-row `rowspan`/`colspan` header restore | New standalone group-header `<tr>` with `colspan` grouping only, layered above the existing flat single-row header | Prototype's table doesn't use `rowspan` anywhere; matching legacy's exact mechanism would have required restructuring every already-correct header cell. The `colspan` group banner achieves the same visual/informational restoration without a new markup pattern. |

## Learnings

- The specifications.md audit table (03-specifications.md) undercounted columns
  in at least 3 places (Симки's `pri`, Хабы's readers table, Планы's modes
  section) — always worth a direct read of the cited legacy PHP line range
  before treating an audit count as final, even when the audit is the
  "approved" spec artifact for this flow.
- For a single table growing by 50+ columns (Планы), hand-editing cell-by-cell
  is error-prone and slow; generating the row HTML with a small throwaway
  Python script, verifying column/colspan counts programmatically, then
  splicing it in was much faster and caught an easy-to-miss mistake (a
  duplicate stale header row from a re-splice) immediately via a `<td>`-count
  assertion rather than a slow manual re-read.

## Completion Checklist (Phase 1+2 session)

- [x] Phase 1 and Phase 2 tasks (1.1, 1.2, 2.1, 2.2, 2.3, 2.4, 2.5a-g) completed
- [ ] Phase 3 and Phase 4 — explicitly out of scope for this session, not started
- [x] No regressions — whole-file tag balance check (div/table/tr/td/button/select/label) passes
- [ ] Documentation updated if needed — n/a, no docs outside this flow's own artifacts
- [ ] Status updated to COMPLETE — flow as a whole isn't complete (Phase 3/4 remain); this session's scope is done

---

### Session 2026-09-01 (cont.) - Phase 3 implementation agent

**Started at**: Phase 3, Task 3.1. Picked up from the Phase 1+2 session's handoff; file was
1250 lines / 8 `<table>`s at start (Симки 43 cols, Модемы(nm) 26, Модемы(um) 6, Хабы USB-tree +
readers 12, Наборы 1, Планы 82, Биллинг 4).

#### Task 3.1 + 3.2: `data-col`/`data-table` tagging, right-align headers, `.mono` class

Given the scale (425 `<td>`/`<th>` cells across 8 tables, one growing to 82 columns), did this
with a throwaway Python script
(`/private/tmp/.../scratchpad/tag_columns.py`, not committed) rather than manual edits — same
approach the Phase 1+2 session used for generating the Планы table. The script:

- Regex-tokenizes each `<table>…</table>` block (no nested tables/trs in this file, so a
  non-greedy DOTALL match is safe) into rows, then cells, tracking a running column-position
  cursor that advances by each cell's `colspan` (default 1).
- Assigns `data-col="<key>"` positionally from a hand-built `COLUMN_DEFS`-equivalent list per
  table (built directly from each table's already-finalized Phase 2 header row, one array per
  table, asserted to the exact column count from the Phase 2 log: 43/26/6/8/12/1/82/4).
- **Cells with `colspan>1` get no `data-col`** — they don't correspond to a single logical
  column (Планы's group-header banner row `plan.php:300-324`, and Хабы USB-tree's
  variable-depth indentation filler cells). Only `colspan=1` cells participate in the
  hide/reorder join-key system built in Task 3.4. This is a deliberate scope-narrowing not
  explicit in the spec: the spec's markup example only shows the simple 1:1 case. Verified via
  a colspan-aware "row width" check (sum of colspan per row) that every row in every table still
  sums to the table's full column count (43/26/6/8/12/1/82/4) even where individual cells were
  skipped — confirms no column was silently dropped from the position cursor, only from the
  `data-col` tag.
- Хабы's USB-tree table is structurally a tree/indentation display, not a flat data grid (row
  cell-count varies: 4, 6, or 8 real `<td>`s per row depending on tree depth, via variable
  colspan on the trailing blank filler). Modeled its 5 indentation/icon slots as `tree1`..`tree5`
  positionally (only tagged where colspan=1, i.e. a real per-slot icon exists) rather than one
  shared `tree` key — cleaner than an earlier draft that considered collapsing them into a
  single shared key across multiple cells in the same row (rejected: would have broken the
  "each column has en internally-consistent single data-col" invariant relied on by Task 3.4).
- Converted every header-row `<td>` to `<th>` (both of Планы's two header rows — group-banner +
  detail row — count as "header" here, matching the file's own established two-row-header
  shape from Task 2.5g). Body rows stay `<td>`. This matches 03-specifications.md's own
  before/after markup example (`<th data-col="group" ...>`), and makes the right-align CSS
  selector (`table[data-table] th`) unambiguous without needing a "first row" heuristic in CSS.
  Added `table[data-table] th{text-align:right;font-weight:normal;}` to the shared `<style>`
  block — `font-weight:normal` specifically to prevent the browser's default bold/center `<th>`
  styling from leaking into header cells that don't carry an explicit inline `font-weight`
  (many of them don't); every cell's existing inline `style=` attribute (background, padding,
  explicit `font-weight:600` where legacy-faithful, Планы's inline `text-align:center` on the
  banner row) is untouched and still wins over the new stylesheet rule as expected.
- `.mono` class added to the `<style>` block with the spec's exact stack. Folded pre-existing
  inline `font-family:monospace;` into `class="mono"` (stripped the inline declaration, added
  the class) on every cell whose `data-col` is in that table's identifier set, rather than
  keeping both — avoids the "your call, just be consistent" ambiguity by picking one mechanism.
  Per-table mono sets: sim {dongle, imei, imsi, number}; nm {dongle, iccid, serial, imei, audio,
  data, dev}; um {device, model, port}; hubs_tree {device, busdevport}; hubs_readers {reader,
  iccid, imsi, ki, dataport}; nabor/plans/billing: none (no identifier-shaped columns in those
  tables). Added `.mono` to `number` (Симки's phone-number column, line ~119/164/209) and
  `reader`/`iccid`/`imsi`/`ki`/`dataport` (Хабы readers) which hadn't been inline-monospaced
  before — genuinely new mono application per spec's "phone numbers... across all tables" ask,
  not just a fold of what already existed.
- `id`/checkbox columns (sim, nm, hubs_tree, hubs_readers — the 4 tables that actually have a
  row-selection checkbox) tagged `data-col="id"` per-instructions, for later pinning in 3.4.
  Модемы(um), Наборы команд, Планы, Биллинг have no checkbox column in legacy, so no `id` key
  exists for those four — their first real column is just a normal (non-pinned) column.
- **Judgment call**: Наборы команд (1 column, "Поддерживаемые наборы команд") got `data-table`/
  `data-col="name"` tagging for consistency (task said tag "any table with real columns"), but
  is being excluded from the Task 3.4 Columns panel — hiding/reordering the single column of a
  1-column table has no meaningful use, and there's no `id` column to pin as an anchor. Flagged
  now, will confirm when 3.4 lands.

**Files changed**: `design/simbox-design-prototype/index.html`.
**Verified by**:
1. Colspan-aware per-row width check (script above) — every row in all 8 tables sums to the
   table's exact expected column count, no silent drops.
2. Whole-file tag balance: `<table>`/`</table>` 8/8, `<tr>`/`</tr>` 35/35, `<td>`/`</td>`
   425/425, `<th>`/`</th>` 191/191 — all even, no broken nesting introduced by the retag.
3. `grep -o 'data-table="[a-z_]*"'` returns exactly the 8 expected keys (sim, nm, um, hubs_tree,
   hubs_readers, nabor, plans, billing), one each.
4. Manual read of: Симки header row (`data-col="id"`/`"group"`/`"pro"` on new `<th>` tags,
   styling intact), Симки body `dongle`/`imei`/`imsi`/`number` cells (`class="mono"` present,
   inline `font-family:monospace` gone where it existed), Планы's group-header row (all 13
   `<th colspan=N>` cells correctly have **no** `data-col`, `text-align:center` inline intact).

#### Task 3.3: Icon rendering correction (density-correct markup)

Extracted all 83 distinct `assets/imgs/...` paths referenced by `<img>` tags in `index.html`
(162 total `<img>` occurrences) and resolved each against
`~/.claude/skills/nativemind-adminka/assets/adminka/adminka-to-fugue-map.json`'s 226 entries by
stripping the map's `assets/adminka/` prefix and the file's `assets/imgs/` prefix and comparing
the remaining relative path (e.g. `qos/capok.png`, `state/simst/1.ico`) — **all 83 resolved on
an exact relative-path match**, including every basename that's duplicated across folders in
this prototype (`imb.png` root vs `im/imb.png`; `igoo.png`/`ivip.png`/`inew.png` root vs their
`qos/` counterparts; `state_wait.png`/`state_sout.png` root vs their `state/` counterparts) —
the map itself carries both root and nested entries for each of those, so the full-path compare
disambiguated every one cleanly. **No basename-only fallback and no 16x16-default fallback was
needed** — worth noting since the task brief anticipated needing one; logging that the
anticipated ambiguity didn't materialize rather than silently having nothing to report.

Wrote a throwaway Python script (`/private/tmp/.../scratchpad/fix_icons.py`) that regexes every
`<img src="assets/imgs/...">` tag, looks up its resolved `resolution`, and rewrites the tag to
`width="16" height="16"` plus `style="image-rendering:pixelated;"` (16x16-resolution, 67 icons)
or bare `width="16" height="16"` with no `pixelated` (32x32-resolution/Fugue-2x-sourced, 95
icons) — replacing whatever inline `width:12px`/`13px`/`14px`/`16px` existed before. Preserved
`vertical-align:middle` where the original style carried it (a handful of inline icons next to
text, e.g. the "Передатчик" panel header icon and Биллинг's direction icons) by detecting and
re-appending it after the resolution-driven style. `assets/icon-globe.svg` (not under
`assets/imgs/`) and the inline caret `<svg>` were untouched by the regex's path prefix
(`assets/imgs/` only), exactly as intended — verified directly, still `width="14" height="14"`.

- **Files changed**: `design/simbox-design-prototype/index.html`.
- **Verified by**: script's own resolved-count assertion (162/162 `<img src="assets/imgs/...">`
  tags replaced, 0 fallbacks); `grep -c` confirms 0 remaining `style="width:Npx"` inside an
  `assets/imgs` `<img>` tag (all remaining `width:Npx` styles in the file belong to unrelated
  `<input>`/`<select>` elements, checked by grep); whole-file `<table>`/`</table>` (8/8) and
  `<div>`/`</div>` (322/322) balance unchanged after the rewrite; manually spot-checked 10+
  icons across every screen (Симки's `napravleine/megafon_spb.ico`, Модемы(nm)'s
  `rssi/rssi-4.ico`, Хабы's `usb/hub_16.ico` and `pl2303.ico`, Планы's `satt.png`, Модемы(um)'s
  `diagmode/diagmode_done.png`) — 16x16-resolution icons all correctly carry `pixelated`,
  32x32-resolution ones correctly don't.

#### Task 3.4: Columns hide/reorder control

Built via a third throwaway generator script
(`/private/tmp/.../scratchpad/add_columns_panel.py`) that (1) re-derives `COLUMN_DEFS` per
table from the exact same key lists used for Task 3.1's tagging (source-of-truth reuse, not a
re-transcription — guarantees the JS defs and the `data-col` markup can never drift out of
sync), dropping the pinned `id` key where one exists; (2) inserts a
`<div style="position:relative..."><button class="columns-btn" data-cols-btn="KEY">Columns</
button><div class="columns-panel" data-cols-panel="KEY">` marker pair immediately above each
table (above the `overflow-x:auto` wrapper for the 4 tables that have one, so the button doesn't
scroll away with the table body; directly above the bare `<table>` for the other 3); (3) appends
one shared vanilla-JS `<script>` block before `</head>`'s... before `</body>` (matches the
lang-select script's existing placement pattern) implementing `loadState`/`saveState`/
`applyColumnState`/`renderPanel`/`initColumnsPanel` exactly as specced.

- **`localStorage` key**: `simbox-proto:cols:${tableKey}`, `{order:[...], hidden:[...]}`.
  `saveState` always writes to an in-memory `MEM_STATE[tableKey]` object first, then tries
  `localStorage.setItem` in a try/catch that silently no-ops on failure — satisfies the spec's
  "private browsing / disabled storage: catch and no-op, panel still works for the session"
  edge case without a separate code path.
- **Schema-drift edge case** (spec's Error Handling table): `loadState` filters any stored
  `order`/`hidden` against the table's *current* `COLUMN_DEFS` keys, drops unknown ones, and
  appends any current key missing from a stored `order` to the end — handles both "column
  removed since last save" and "column added since last save" without ever throwing or blanking
  the table.
- **`id`/checkbox column pinning**: `PINNED = {sim:"id", nm:"id", hubs_tree:"id",
  hubs_readers:"id"}` (the 4 tables that actually have a checkbox column, per Task 3.1's
  finding — Модемы(um)/Планы/Биллинг have no checkbox in legacy, so nothing to pin there,
  every column in those 3 is hideable). `applyColumnState` always prepends the pinned key to
  `fullOrder` before reordering, and `COLUMN_DEFS` never includes `id`, so it can never appear
  as a checkbox/draggable row in the panel — matches "no checkbox, no drag handle, always
  visible, always leftmost."
- **Drag-and-drop**: native HTML5 (`draggable="true"` rows inside the panel list,
  `dragstart`/`dragover`/`drop`/`dragend`), no library. Same-position drop (dropping onto the
  row already at that slot) is a deliberate no-op (`targetKey === dragSrc` short-circuits before
  any `splice`/re-render), matching the spec's "no redundant `applyColumnState` re-render" edge
  case.
- **Reordering mechanics**: for every `<tr>` that contains at least one `[data-col]` cell,
  `applyColumnState` walks the target order and `row.appendChild()`s the matching
  `[data-col="key"]` cell into place (repeated `appendChild` on an already-attached node moves
  it, standard DOM behavior) — header and body rows reorder in lockstep since they're driven by
  the same `data-col` join key from Task 3.1.
- **Judgment call / documented limitation — colspan rows don't participate in reordering**:
  rows where *no* cell carries `data-col` (Планы's group-banner row, whose cells are all
  `colspan>1` and intentionally left untagged in Task 3.1) are skipped by the "has a
  `[data-col]` child" guard, so the banner row is never touched by a reorder. This means
  reordering Планы's 82 columns will desync the group-banner labels ("Направление 1",
  "SATT", etc.) from the columns they visually sit above, since the banner cells don't move
  with their underlying columns. Hide/show still works correctly everywhere (targets `[data-col]`
  directly, independent of row position). Accepted as a structural limitation of layering a
  `colspan` banner row on top of a flat per-column hide/reorder model — full colspan-aware
  reordering (recomputing every banner cell's `colspan` live) was judged out of scope for a
  static prototype; noting it explicitly rather than silently shipping a half-working reorder
  on that one table. Хабы's USB-tree table has a milder version of the same caveat (its
  colspan filler cells for collapsed tree depth also don't move), same reasoning.
- **Наборы команд deliberately excluded** from the Columns panel entirely (no button/panel
  markup inserted, no `COLUMN_DEFS.nabor` entry) — single-column table, no checkbox to pin,
  hiding/reordering its one column has no meaningful use. `initColumnsPanel`'s
  `if (!COLUMN_DEFS[tableKey]) return;` guard makes this a clean no-op rather than a special
  case in the main loop (the loop still iterates `nabor`'s `<table data-table="nabor">`, harmlessly).
- Column panel `label`s are auto-derived from `data-col` keys (underscores → spaces, e.g.
  `sms_sended` → "sms sended") rather than hand-written friendly names — acceptable for a
  prototype where the keys already mirror legacy field names operators recognize; flagging as a
  low-effort choice, not a spec requirement violation (spec's `{key,label}` shape is satisfied,
  it just doesn't mandate label wording).

**Files changed**: `design/simbox-design-prototype/index.html`.
**Verified by**: `node --check` on the extracted inline `<script>` (syntax-valid); `node -e`
`eval`-loaded the generated `COLUMN_DEFS` object and confirmed array lengths per table (sim 42,
nm 25, um 6, hubs_tree 7, hubs_readers 11, plans 82, billing 4 — each exactly
Task-3.1's-total-columns minus 1 where a pinned `id` exists, 0 pinned otherwise); confirmed
`PINNED` object contents; `grep` confirms exactly 7 `data-cols-btn="<key>"` markers (sim, nm,
um, hubs_tree, hubs_readers, plans, billing — nabor correctly absent) each sitting on the line
immediately before that table's opening tag (or its scroll wrapper); whole-file `<div>`/`</div>`
(336/336) and `<script>`/`</script>` (4/4) balance intact. **No headless-browser/DOM runtime
test was available in this environment** (no jsdom, no Chromium/Playwright installed, no network
access to fetch one) — verification here is syntax + structural + manual code-trace only; live
interaction (click Columns, hide/drag/reload-persist/Reset) is deferred to Phase 4's manual
browser checklist, flagging this explicitly rather than claiming behavior I couldn't observe.

#### Task 3.5: Adaptive actions + filter row

Identified the file's actual flex-wrap action-panel-row wrappers via
`grep -n 'display:flex;flex-wrap:wrap;gap:20px'` — 5 matches total, but only 4 are genuine
button/card action rows (sim's `margin-top:24px` row holding Редактирование/Передатчик/Действия
x4/Экспорт-Импорт/Опции/Замена KI x2/SMS-рассылка; Модемы(nm)'s equivalent; Хабы's two rows —
USB-tree "Действия"/"Питание"/"Опции" and readers' "Действия"/"PIN"/"Поиск KI"/"APDU-команда").
The 5th match (screen 11, `margin-top` absent) is the "Диалоги — результаты действий" static
result-card gallery — no buttons in it at all, so there's nothing for compact-mode to affect;
deliberately left untouched rather than tagging a container-query root with no effect.

Added `class="actions-row"` to those 4 wrappers and `.actions-row{container-type:inline-size;}`
to the shared `<style>` block, plus:
```css
@container (max-width:480px){
  .actions-row .icon-btn .btn-label{ /* visually-hidden technique: absolute, 1x1px, clip */ }
  .actions-row .filter-panel .btn-label{ /* explicit opt-out, restores normal layout */ }
}
```
**480px breakpoint kept as drafted** — the widest single card in any of the 4 rows is ~460px
wide (Экспорт/Импорт), and most cards are 200-360px, so 480px reliably triggers compact mode
only once a card's own available inline space genuinely gets tight, not on every normal-width
render. Not re-tuned since the static side-by-side gallery layout at `min-width:9200px` doesn't
naturally exercise a container down to 480px anyway — flagging that the true fit-and-feel check
(actually resizing a single card's container) is a Phase-4/real-browser exercise, not
something a static line-count read can fully confirm.

- **Judgment call / deviation from literal spec wording**: the spec says "button/link text
  visually hidden... icons stay," implying every button in these rows has an icon fallback. In
  the actual markup, only 7 of the roughly 50 buttons across these 4 rows have a leading
  `<img>` (the reused Передатчик ВКЛ/ВЫКЛ panel in sim and nm; Хабы USB-tree's Питание
  ВКЛ/ВЫКЛ/РЕСТАРТ panel). The rest (`Обновить`, `Set group`, `Activate SIM`, `unlock
  CARDLOCK`, the whole "PIN"/"Поиск KI"/"APDU-команда" panel, etc.) are plain text with no
  icon. Blindly hiding all button text per the literal spec wording would leave roughly 43
  buttons as empty, zero-affordance pills — clearly worse than the existing `flex-wrap`
  fallback the spec itself allows for the filter panel. **Only wrapped the 7 buttons that
  actually have an icon** in `<span class="btn-label">` + `class="icon-btn"` + a `title`
  attribute (native tooltip, carries the same button text) and scoped the compact-mode
  text-hiding CSS to `.icon-btn .btn-label` specifically. Text-only buttons keep their text at
  all container widths and simply wrap via the pre-existing `flex-wrap` on the row, the same
  fallback the spec already prescribes for the filter panel. This is a scope-narrowing of the
  literal instruction to fit the file's actual content, not a skip — logging it clearly per the
  "make the most reasonable call... note it" guidance rather than shipping obviously-broken
  empty buttons or silently inventing icons for buttons that don't have any in the legacy
  source.
- Filter panel (`Редактирование`, sim screen only — no other screen's action row has an
  equivalent labeled-filter card) tagged `class="filter-panel"` and given an explicit CSS
  override restoring `.btn-label` to normal flow inside it, even though it currently contains
  no icon-buttons anyway (belt-and-suspenders against a future edit adding one, and it makes
  the "explicitly excluded" requirement traceable in the CSS itself rather than being true only
  by the current absence of icon-buttons).

**Files changed**: `design/simbox-design-prototype/index.html`.
**Verified by**: `grep -c 'class="actions-row"'` -> 4; `grep -c 'class="filter-panel"'` -> 1;
the generator script's own regex-substitution assertion required exactly 7 icon-button matches
(else it would have hard-failed) — got exactly 7, confirmed by grep afterward (3x ВКЛ, 3x ВЫКЛ,
1x РЕСТАРТ, each now carrying `title="..."` with the original label text); whole-file
`<button>`/`</button>` (91/91) and `<div>`/`</div>` (336/336) balance unchanged.

#### Task 3.6: Icon legend expansion

**Completed for all 6 screens whose tables actually use icons**: Симки (expanded in place),
Модемы(nm), Модемы(um), Хабы (one combined legend for both its USB-tree and readers tables),
Планы, Биллинг. Наборы команд, Процессы, Обновление, Debug, and screen 11 have no icons in
their tables/content, so no legend was added there (nothing to document) — not a deferral, a
correct no-op per the task's own scope ("one row per icon actually used on that screen's
table(s)").

Built this in two layers:
1. `/private/tmp/.../scratchpad/legend_data.py` — a hand-built `ICONS` dict (83 entries, one per
   distinct icon path referenced anywhere in the file) mapping `"folder/file"` → `(category,
   meaning)`. Category labels copied **verbatim** from
   `~/.claude/skills/nativemind-adminka/guidelines/adminka-icons.html`'s own `sets` grouping
   (`"SIM state (simst)"`, `"Number quality (QoS)"`, `"Operators & directions (направление)"`,
   `"Root set — balance, SMS, calls, dongles, days, playback"`, etc. — 12 categories total, in
   a fixed display order). Meanings sourced from, in order of preference: (a)
   `legacy/simbox-desktop-v2014/www/simbox/modules/html.php`'s `html_group`/`html_cfun`/
   `html_simst`/`html_srvst`/`html_spec`/`html_im`/`html_qos` functions (exact per-value icon
   logic — e.g. `html_simst($simst,$pinrequired)`: `simst=0` → `state/simst/0.ico`, `simst=1`
   → `state/simst/1.ico`); (b) `sim.php:2164-2221`'s own existing legend text (iVIP/iGOO/iNOR/
   iBAD/iNEW/iNOS/high_datt/low_acdl/need_in/satt — this is what the pre-existing Симки
   "Примечание" block was already built from, now folded into the categorized table rather than
   restated inline); (c) `plan.php`'s inline HTML comments near the SATT/IATT/modes blocks
   (`plan.php:895-947` — `diff_slow`/`diff_min`/IATT_SOFT/MIN/MAX/OUT_IN_ANS/DUR/SATT_SOFT/HARD
   definitions; `plan.php:133-148`'s `file_put_contents` calls confirming `forwarding`/
   `in_wait`/`in_sound`/`nospam` are literal per-plan checkbox flags).
   - **Judgment call flagged**: `may.ico`/`mon.ico`/`msm.ico` (3 of the 83) have no explicit
     legacy comment anywhere in `plan.php` or `html.php` — they sit visually in the SATT/SMS
     block (`plan.php:391-393`) between the modes columns and `SATT_soft`, with no accompanying
     `<!-- -->` comment or docstring. Gave them a hedged meaning ("доп. условие разрешения
     генерации SMS, см. SATT") rather than inventing false precision — flagging this as the one
     place in this task where the source genuinely doesn't spell out the semantics, so the
     legend text is inferred-from-position, not transcribed.
2. `/private/tmp/.../scratchpad/insert_legends.py` — extracts the actual distinct
   `assets/imgs/...` paths used inside each `<table data-table="X">...</table>` block (reusing
   the same regex approach as Tasks 3.1/3.3), looks each one up in `ICONS`, groups by category,
   and renders a `<table>` of icon+meaning rows (icon markup reuses Task 3.3's density-correct
   `width="16" height="16"` + conditional `pixelated`, confirmed via the same provenance-map
   lookup rather than hand-guessing resolution again). The script **hard-fails if any icon
   found in a table has no `ICONS` entry** (`missing` list + `sys.exit(1)`) — ran clean, zero
   missing, on the first attempt (all 83 icons from Task 3.3's inventory were already
   catalogued while building `legend_data.py`).
   - Симки: the existing "Примечание" block's abbreviation-glossary paragraph (m-i/m-o/ACD/ASR/
     PDD/DATT/IATT — not icon-related) is kept as prose; the two icon-inline paragraphs below
     it (the ones added in the original prototype build) are replaced by the categorized table.
     29 distinct icons found in the Симки table, all resolved.
   - Модемы(nm): new card, 10 icons (simst/srvst/rssi/im/qos mix).
   - Модемы(um): new card, 3 icons (all `diagmode/*`, one category).
   - Хабы: **one combined card** covering both `hubs_tree` (6 icons: usb/tree categories) and
     `hubs_readers` (2 icons) tables, inserted once after the readers panel's action row (the
     last one on that screen) rather than duplicating a legend under each of the two tables —
     matches the task's own framing ("actually used ON THAT SCREEN's table(s)", plural,
     singular legend).
   - Планы: new card (46 distinct icons — by far the largest, unsurprising given the table
     grew to 82 columns in Phase 2), inserted directly above the pre-existing "Пояснение" prose
     panel (kept untouched — it's a different kind of content, mechanics/behavior explanation
     rather than icon glossary, so it stays as its own card rather than being merged).
   - Биллинг: new card, 3 icons (2 operator icons + `state_sout.png`).
   - Insertion mechanics: for the 4 screens whose actions-row already exists (nm, hubs — via
     its readers row), used a hand-rolled tag-depth-counting `end_of_div()` helper (walks
     `<div`/`</div>` occurrences tracking depth from the actions-row's own opening tag) to find
     exactly where that row's matching `</div>` closes, then inserted the legend card as the
     next sibling — avoids the wrong-`</div>`-picked-by-non-greedy-regex failure mode that a
     naive `.*?</div>` would hit given how deeply nested these action-panel rows are. Screens
     without an actions-row (um, plans, billing) used literal unique-text anchors instead
     (simpler, safe since each anchor string is asserted unique in the file before use).
   - Icon markup reuses `vertical-align:middle` (not part of Task 3.3's table-cell icons, which
     don't need it, but needed here since these are inline icon-before-text glossary rows).

**Files changed**: `design/simbox-design-prototype/index.html`.
**Verified by**: `insert_legends.py`'s own `assert`s on every anchor string (each required to
be found exactly once — all passed on first run, no silent multi-match risk); the script's
`missing` list was empty (0 unmapped icons across all 6 legends); whole-file tag balance
after the insertion: `<div>` 351/351, `<table>` 14/14 (8 data tables + 6 new legend tables),
`<tr>` 157/157, `<td>` 646/646, `<th>` 191/191, `<button>` 91/91, `<script>` 4/4 — all even,
confirming the depth-counting insertion logic didn't corrupt nesting anywhere. Manually
re-read all 6 rendered legend blocks in the file: row counts match each table's actual
distinct-icon count exactly (sim 29, nm 10, um 3, hubs 8 combined, plans 46, billing 3 — 99
rows total across 12 categories), each screen's legend confirmed sitting under the correct
screen title by grepping the nearest preceding `NN · ScreenName — /?p=...` marker for every
insertion point.

**Ended at**: All Phase 3 tasks (3.1-3.6) complete. `index.html` grew from 1250 to 1637 lines.
Final whole-file balance check: `<div>` 351/351, `<table>` 14/14, `<tr>` 157/157, `<td>`
646/646, `<th>` 191/191, `<button>` 91/91, `<script>` 4/4 (2 non-`src` inline blocks, both
`node --check`-clean). `grep -c "Свистки"` and `grep -c "pause2.png"` both still 0 (Phase 1/2
work undisturbed). Only `index.html` modified this session — no other files touched, no new
assets added (Task 3.3 only rewrote existing `<img>` tags, didn't add files).
**Handoff notes**: Phase 4 (the full manual browser checklist from `03-specifications.md` —
columns persistence/drag-reorder/reload, compact-actions resize, DPR/zoom icon check, language
menu) is explicitly next-session scope. This session's own verification was syntax +
structural + programmatic (no headless browser available in this environment) — flagging that
Phase 4 is the first point in this flow where the columns panel and compact-actions CSS will
actually be exercised in a real browser.

## Completion Checklist (Phase 3 session)

- [x] Task 3.1 (`data-col`/`data-table` tagging) — all 8 tables, colspan-aware, verified.
- [x] Task 3.2 (right-align headers + `.mono`) — shared CSS + per-cell class, verified.
- [x] Task 3.3 (icon rendering correction) — all 162 `<img>` tags, 0 fallbacks needed.
- [x] Task 3.4 (columns hide/reorder) — 7 of 8 tables (Наборы команд deliberately excluded,
      logged); syntax/structural verification only, live interaction deferred to Phase 4.
- [x] Task 3.5 (adaptive actions + filter row) — 4 actions-rows, 480px breakpoint kept as
      drafted, scoped to icon-bearing buttons only (deviation logged).
- [x] Task 3.6 (icon legend expansion) — all 6 screens with icon-bearing tables covered.
- [ ] Phase 4 — explicitly out of scope for this session, not started.
