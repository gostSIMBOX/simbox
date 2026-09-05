# Requirements: simbox-web-design-prototype-table-uiux

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-09-05

## Problem Statement

The current v2026 prototype (`design/simbox-web-design-prototype-v2026`, page `lib/pages/sims_page.dart`)
already re-implements the legacy main SIM table (`legacy/simbox-desktop-v2014/www/simbox/sim.php`)
with a modern dense-table UI, and it's already close. But it was built from memory/approximation
rather than a column-by-column port, so some columns from the original were dropped, some were
silently merged in a way that loses data, and a couple were never carried over. Since this table
is the primary "cockpit" screen operators live in all day, any field that quietly went missing is a
regression, not a simplification — operators built muscle memory around every column in the legacy
table.

Source of truth for **logic/meaning** (what each column is, what state each icon reflects): the
legacy PHP, specifically `legacy/simbox-desktop-v2014/www/simbox/sim.php` (row/column rendering)
plus `modules/html.php` (icon helper functions `html_group`, `html_fas`, `html_spec`, `html_io`,
`html_qos`, `html_napr`, `html_dongle`, `html_cfun`, `html_simst`, `html_srvst`, `html_op`). The
legacy *visual* styling (plain HTML tables, tiny fonts, inline colors) is explicitly obsolete and
not to be copied.

Source of truth for **visual design**: `design/simbox-design-prototype-v2026-dc` (design system /
tokens) — already the basis for the current prototype's look (`lib/design/tokens.dart`,
`DenseTable`, `Cell` stacking pattern). This work should extend that existing visual language, not
invent a new one.

## Gap Analysis (legacy `sim.php` vs. current `sims_page.dart`)

Legacy renders **42 data columns** (+ the select-all checkbox). Current prototype renders **33**.
Below, "legacy source" cites the PHP variable(s)/line range; "current" cites the `ColDef` key in
`sims_page.dart` or "MISSING".

| # | Legacy header | Legacy source (state file / var) | Current `ColDef` key | Status |
|---|---|---|---|---|
| 1 | `group` (+ schedule pause icon, group number) | `.group`, computed `$pause` | `group` | OK |
| 2 | `pro` | `.pro` (set) vs `.pro` (state) — blue if differs from setting | **none** | **MISSING** |
| 3 | `cap` | `.cap` (OK/FAIL captcha icon) | `cap` | OK |
| 4 | `im` | `.im` (A–E multi-sim icon) | `im` | OK |
| 5 | `spec` | `.fas`, `.spec`, `.vip`, `.pre`, `.pos` (stacked icons) | `spec` | Partial — only `.spec`; `.fas`/`.vip`/`.pre`/`.pos` not modeled |
| 6 | `state` (io/qos + live call state + busy numbers) | `.state_waiting`, `.state_in/out`, `.qos`, `.sout`, `.em_type`, `.state_dialing/ring/active` (+ elapsed timer), `.busy`+`.numberb`+`.numbera` | `io` | Partial — only io+qos icons; waiting/dialing/ring/active/busy-number/timer entirely missing |
| 7 | *(blank header)* napr | `.billing_direction` | `napr` | OK |
| 8 | `plan` / `nabor` / `tarif` | `.plan`, plan's `.nabor`, `.tarif` | `plan` | OK |
| 9 | `number` | `.number` | `number` | OK |
| 10 | `operator` / `sim` | `.provider_name`, `.provider_name2`, **`.owner`** | `oper` | Partial — `owner` (3rd line) not modeled |
| 11 | `balance` / `bal_diff` | `.balance`, get_balance age+color, `.op_t/op_d`, `.bal_yest/bal_minus/bal_plus` | `bal` | OK |
| 12 | *(blank)* dongle model+power | `.model`, `.cfun` | `model` | OK |
| 13 | *(blank)* simst/srvst | `.simst`, `.srvst`, `.pinrequired` | `simst` | OK |
| 14 | `dongle` | dongle id + `.imei_name` (dongle0 hubs only) | `dongle` | Partial — `dongle_a` (hub port label) not modeled |
| 15 | *(blank)* log icons | ussd&sms / calls tooltip icons | *(none as icons — see #41)* | Merged into `log` col (#41), OK as UX choice |
| 16 | `tot` / `IMB/C` / `IMN/D/E` | `.stat_out_calls`, `.imb_count/imc_count/imn_count/imd_count/ime_count` | `tot` | OK |
| 17 | `a-o` / `a-i` | `.stat_calls_answered`, `.stat_in_answered` | `ao` (holds ao/ai) | OK |
| 18 | `m-o` / `m-i` | `.stat_calls_duration`, `.stat_in_duration` (minsec) | `mo` (holds mo/mi) | OK |
| 19 | `ACD-o` | avg(`stat_calls_duration`/`stat_calls_answered`) | `acdo` | OK |
| 20 | `ACD-i` | avg(`stat_in_duration`/`stat_in_answered`) | `acdi` | OK |
| 21 | `ACDL` | `.stat_acdl` + `.low_acdl` flag | `acdl` | OK |
| 22 | `DATT` | `.stat_datt` + `.high_datt` flag | `datt` | OK |
| 23 | `IATT` | `.stat_iatt` + `.need_in` flag | `iatt` | OK |
| 24 | `SATT` | `.stat_satt` + `.need_sms` flag | `satt` | OK |
| 25 | *(sms_out icon)* `_sended` | `.may_sended/limit`, `.mon_sended/limit`, **`.msm_sended/limit`**, **`.smsout_sended` + soft/hard** | `may` | Partial — MON shown, **MSM line and SMS soft/hard line missing** |
| 26 | `ASRL` | `.stat_asrl` | `asrl` | OK |
| 27 | `PDDAS` | *(legacy reads `.stat_asrl` again — apparent copy-paste bug; conceptually "post-dial delay, answered")* | **none** | **MISSING** |
| 28 | `PDDL0` | `.stat_pddl0` | `pdd0` | OK |
| 29 | `PDDL1` | `.stat_pddl1` | `pdd1` | OK |
| 30 | `pri` | *(commented out in legacy — dead column, not rendered)* | `pri` | Extra — legacy never actually shows this; keep or drop? (see Open Questions) |
| 31 | `LIMIT0` | `.limit.0` / `.limit_max.0` + `.palevo` flag | `lim0` (holds LIMIT0/1 only) | Partial |
| 32 | `LIMIT1` | `.limit.1` / `.limit_max.1` + `.1.palevo` flag | *(merged into lim0)* | Partial |
| 33 | `LIMIT2` | `.limit.2` / `.limit_max.2` + `.2.palevo` flag | **none** | **MISSING** |
| 34 | `LIMIT3` | `.limit.3` / `.limit_max.3` + `.3.palevo` flag | **none** | **MISSING** |
| 35 | `LIMIT4` | `.limit.4` / `.limit_max.4` + `.4.palevo` flag | **none** | **MISSING** |
| 36 | `LIMIT5` | `.limit.5` / `.limit_max.5` + `.5.palevo` flag | **none** | **MISSING** |
| 37 | `LAC` | `.lac` | `lac` (holds LAC/CELL) | OK |
| 38 | `CELL` | `.cell` | *(merged into lac)* | OK |
| 39 | `IMEI` | dongle `.imei` + blacklist bold-red flag | `imei` | OK |
| 40 | `IMSI` | imsi (the row key) | `imsi` | OK |
| 41 | `log` | links to `showlog.php` / `showcalls.php` | `log` | OK |
| 42 | dates | `.date_activated/date_1call/date_lcall/date_blocked` | `dates` | OK |

**Net: 8 fully missing columns** (`pro`, `PDDAS`, `LIMIT2`, `LIMIT3`, `LIMIT4`, `LIMIT5`, plus the
`state` column's busy/live-call sub-state, plus `spec`'s `fas`/`vip`/`pre`/`pos` icons) **and 4
columns with partial data loss** (`spec`, `oper` missing owner, `may` missing MSM+SMS line,
`dongle` missing hub port label).

## User Stories

### Primary

**As an** operator running the SIM fleet dashboard day-to-day
**I want** the main table to show every field the legacy desktop tool showed, under the new visual
design
**So that** I don't lose any operational signal (blacklist flags, per-slot limits, live call state,
SIM owner, SMS quota) when the interface is modernized

### Secondary

**As a** designer/reviewer comparing the two tools side by side
**I want** a clear map from legacy column → new column
**So that** I can confirm nothing was silently dropped in translation

## Acceptance Criteria

### Must Have

1. **Given** the legacy table has 42 data columns, **when** the table is rebuilt, **then** every
   legacy column's *data* is represented somewhere in the new table (either as its own column, or
   explicitly merged into a compound cell alongside a directly related column — never dropped).
2. **Given** the `pro` column exists in legacy (shows current provisioning state, blue when it
   differs from the pending setting), **when** rebuilt, **then** a `pro` column is added showing
   the same info with the existing "changed from setting" visual convention already used elsewhere
   in the app (if one exists) or a sensible new one.
3. **Given** `LIMIT0`–`LIMIT5` are six independent per-slot limits (each with its own `palevo`
   over-limit flag), **when** rebuilt, **then** all six are visible/reachable (as 6 columns, or as
   one compact multi-slot cell/popover — see Open Questions), not just slots 0–1.
4. **Given** `PDDAS` is a distinct header in legacy, **when** rebuilt, **then** a `PDDAS` column
   exists distinct from `ASRL` (treat legacy's identical data source as a legacy bug, not a spec —
   mock it as its own plausible stat).
5. **Given** the `may` column's `_sended` cell shows MAY/MON/**MSM** quota lines plus a separate
   SMS soft/hard-limit line, **when** rebuilt, **then** all four lines are present.
6. **Given** the `operator` column shows provider name + secondary provider name + **owner**,
   **when** rebuilt, **then** owner is shown as a third line.
7. **Given** the `spec` column stacks `fas`/`spec`/`vip`/`pre`/`pos` icons, **when** rebuilt,
   **then** all five icon sources are represented (not just `spec`).
8. **Given** the `state` column shows: waiting icon, io+qos, an outgoing `em_type` marker, a live
   dialing/ringing/active indicator with elapsed-seconds timer, and — when the line is busy — the
   two connected numbers, **when** rebuilt, **then** these sub-states are represented in the new
   column (static/mocked timer values are fine; this is a design prototype, not a live system).
9. Existing already-correct columns (see gap table "OK" rows) are preserved as-is — this is an
   additive/corrective pass, not a rewrite of the whole page.
10. Column order in the new table follows legacy left-to-right order, adjusted only where an
    earlier compound-cell precedent already reordered things (e.g. LAC+CELL merge) — no arbitrary
    reshuffling.

### Should Have

- Update the columns-editor labels/tooltips for any new/changed columns so `Столбцы` picker stays
  usable (consistent with existing `title`/`label` fallback pattern).
- Update `mock.dart` sample data so new fields have plausible, varied demo values (including at
  least one row that trips each new "flag" state: pro mismatch, palevo on a higher limit slot,
  blacklisted IMEI already covered, busy call, etc.) so the visual review isn't all-blank columns.

### Won't Have (This Iteration)

- No live/real backend wiring — this remains a static Flutter mock prototype.
- No changes to other pages (`dongles_page`, `readers_page`, etc.) except where a shared widget
  (e.g. `Ico` helpers in `icon_map.dart`) needs a new icon mapping used only by this table.
- Not reproducing legacy's literal PDDAS/ASRL data-source bug — see AC #4.
- Not implementing the commented-out `pri` column's original intent beyond keeping it as a plain
  numeric column (legacy itself never shipped it live).

## Constraints

- **Technical**: Flutter/Dart, must fit the existing `ColDef<Sim>` / `Cell` / `DenseTable` widget
  architecture in `design/simbox-web-design-prototype-v2026/lib/`. Extend `Sim` model, `_cols()`,
  and `mock.dart`; avoid introducing a parallel table system.
- **Visual**: must follow `design/simbox-design-prototype-v2026-dc` tokens/spacing already in use
  (`lib/design/tokens.dart`), not legacy's raw HTML table look.
- **Column budget**: legacy already crams 42 columns into a small-font table; the new design uses
  larger touch-friendly cells, so very wide tables (LIMIT0–5 especially) need a real layout answer,
  not just 6 more raw columns bolted on — this is an open question for the Visual phase.

## Open Questions

- [ ] `LIMIT0`–`LIMIT5`: six separate columns (matches legacy exactly, very wide) vs. one compact
      "limits" cell/popover showing all six + palevo flags (matches data, saves horizontal space)?
- [ ] `state` column's live call sub-state (dialing/ring/active + elapsed timer, busy numbers):
      full fidelity mock, or a simplified single "activity" indicator given this is a static
      prototype where a live timer can't actually tick?
- [ ] `pro` column: legacy's only visual cue is "blue text when current ≠ setting" — is there
      already an established "pending change" visual convention elsewhere in the v2026 prototype to
      reuse, or should this introduce a new one?
- [ ] Is the dead/commented-out legacy `pri` column worth keeping at all, or should it be dropped
      now that we know legacy never rendered it?
- [ ] `dongle_a` (hub port label, `dongle0*` rows only) — fold into the existing `dongle` column as
      a sub-line, or skip since it only applies to hub-connected dongles?

## References

- Legacy table: `legacy/simbox-desktop-v2014/www/simbox/sim.php` (header ~L1096-1180, row render
  ~L1280-1876), helpers in `legacy/simbox-desktop-v2014/www/simbox/modules/html.php`.
- Current prototype: `design/simbox-web-design-prototype-v2026/lib/pages/sims_page.dart`,
  `lib/data/models.dart` (`Sim`, `Cell`, `ColDef`), `lib/data/mock.dart`, `lib/data/icon_map.dart`,
  `lib/data/icons_catalog.dart`.
- Design source of truth: `design/simbox-design-prototype-v2026-dc/`.

---

## Approval

- [ ] Reviewed by:
- [ ] Approved on:
- [ ] Notes:
