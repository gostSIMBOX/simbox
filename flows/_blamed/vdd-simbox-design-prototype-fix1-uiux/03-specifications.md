# Specifications: SimBox v2026 UI/UX fixes

> Version: 1.0  
> Status: APPROVED  
> Last Updated: 2026-09-01  
> Requirements: [01-requirements.md](01-requirements.md)

This phase starts after explicit approval of `02-visual.md`.

## 1. Outcome and authority

The v2026 prototype becomes a file-based, locale-complete, density-aware operations UI while
preserving the active behavior and logical cells of
`legacy/simbox-desktop-v2014/www/simbox/`. Authority is applied in this order:

1. explicit approved clarifications in this VDD flow;
2. active legacy PHP markup and handlers;
3. approved visual composition;
4. current prototype data, only when it does not contradict the first three.

Commented legacy forms are evidence, not functionality. Hubs therefore has no KI/APDU actions;
those remain Readers-only. Commented SIM `rotki` and `save` controls are also excluded.

The chosen toolbar is one implementation, not three variants: a **morphing inline action rail**.
Its fixed-height shell always shares one row with Filter and Columns. Selecting a group replaces
only the flexible center content with that group's parameters and Run/Cancel controls. It never
opens over the grid and never changes the grid's top edge. At narrower widths labels disappear;
icons, tooltips and accessible names remain. If even icon mode cannot fit, the rail scrolls
horizontally inside its own fixed-height area.

## 2. Affected file structure

`index.html` keeps the DC host markup and orchestration only. Generated `support.js` and `_ds/**`
are not edited. Plain scripts are loaded before the inline `data-dc-script` component and publish
one file-safe global registry, so the prototype continues to work from `file://` without a build.

```text
design/simbox-design-prototype-v2026/
├── index.html
├── css/
│   ├── tokens.css
│   ├── base.css
│   ├── shell.css
│   ├── toolbar.css
│   ├── data-grid.css
│   ├── dialogs.css
│   └── responsive.css
├── js/
│   ├── core/
│   │   ├── namespace.js
│   │   ├── registry.js
│   │   ├── icons.js
│   │   ├── i18n.js
│   │   ├── storage.js
│   │   ├── grid.js
│   │   └── actions.js
│   ├── locales/{en,th,ru,hi,zh}.js
│   ├── tables/
│   │   ├── sim.js
│   │   ├── lines.js
│   │   ├── programmer.js
│   │   ├── hubs.js
│   │   ├── readers.js
│   │   ├── command-sets.js
│   │   ├── plans.js
│   │   ├── billing.js
│   │   └── icons.js
│   ├── screens/{processes,update,debug}.js
│   └── app-data.js
├── assets/fugue/{1x,2x}/
└── FUGUE-WISHLIST.md
```

CSS extraction is responsibility-based rather than one stylesheet per route. Table definitions
are route-specific JavaScript files; shared grid behavior exists only in `grid.js`.

## 3. Runtime contracts

The public namespace is `window.SimBoxV2026`. Loading order is namespace → core registries →
locales → table/screen definitions → sample data → existing DC runtime → inline component.

```js
// Conceptual contract; exact syntax may remain classic ES5/ES2015 script-compatible.
SimBoxV2026.registerLocale(localeCode, dictionary)
SimBoxV2026.registerIcon(iconDefinition)
SimBoxV2026.registerTable(tableDefinition)
SimBoxV2026.registerScreen(screenDefinition)
SimBoxV2026.getInitialState()
```

### 3.1 Definitions

```text
IconDefinition
  id, filename, src1x, src2x, semantic, license

ColumnDefinition
  id, labelKey, legacyHeader, legacySource, type,
  align, width, minWidth, sortable, hideable, renderer

TableDefinition
  id, route, legacyFile, columns[], rows[], actions[], defaultSort

ActionDefinition
  id, labelKey, iconId, group, selection, fields[], danger, legacySubmit

RouteDefinition
  id, labelKey, iconId, kind(table|screen), definitionId
```

Stable IDs are never translated. `legacySource` cites the PHP field/expression or positional cell
that established the column. Data renderers may stack multiple values only where legacy used one
`<td>` for those values. They may not merge separate legacy cells.

### 3.2 Grid state and persistence

Each table owns `{order, hidden, sort:{columnId,direction}}`. Persistence key:
`simbox.v2026.grid.<tableId>.v1`. Invalid/unknown IDs are discarded; new schema columns append in
manifest order. Reset restores manifest order, makes every hideable column visible, and restores
the table's default sort. Selection and active action state are never persisted.

Sorting is stable, toggles ascending/descending, and handles numbers, dates, text, codes and nulls
by declared column type. Header keyboard activation performs the same transition as pointer input.
The Columns popover provides visible checkboxes, drag/reorder or Move left/right controls, and
Reset. It is anchored above the grid and may overlay only the toolbar/shell, never data rows.

## 4. Exact table manifests

All counts below are **logical legacy cells**. On initial load and after Reset, visible count must
equal manifest count. Selection cells count because they are real interaction columns.

### 4.1 SIM — `sim.php` — 43 columns

| # | Stable column ID | Legacy meaning/source | Type/alignment |
|---:|---|---|---|
| 1 | `select` | row checkbox | control/center |
| 2 | `group_pause` | group and pause state in one legacy cell | text/right |
| 3 | `pro` | `pro` flag | code/right |
| 4 | `cap` | CAP state | code/right |
| 5 | `im` | IM state | code/right |
| 6 | `spec` | special state | code/right |
| 7 | `state` | IO/QoS/call state stack | status/right |
| 8 | `direction` | billing/direction icon cell | status/right |
| 9 | `plan` | command set/plan/tariff stack | text/right |
| 10 | `number` | SIM number | mono/right |
| 11 | `operator` | operator/provider/owner stack | text/right |
| 12 | `balance` | balance and delta | number/right |
| 13 | `dongle_model_cfun` | model and CFUN in one legacy cell | text/right |
| 14 | `simst_srvst` | SIMST and SRVST in one legacy cell | code/right |
| 15 | `dongle_id` | dongle/channel ID | mono/right |
| 16 | `log_icons` | legacy log icon links | control/right |
| 17 | `tot_im` | TOT plus IM counters | number/right |
| 18 | `answered` | answered out/in (`a-o/a-i`) | number/right |
| 19 | `minutes` | minutes out/in (`m-o/m-i`) | number/right |
| 20 | `acd_out` | ACD-o | number/right |
| 21 | `acd_in` | ACD-i | number/right |
| 22 | `acdl` | ACDL | number/right |
| 23 | `datt` | DATT | number/right |
| 24 | `iatt` | IATT | number/right |
| 25 | `satt` | SATT | number/right |
| 26 | `sms_sended` | MAY/MON/MSM/SMS stack | number/right |
| 27 | `asrl` | ASRL | number/right |
| 28 | `pddas` | PDDAS header; body repeats legacy ASRL/stat source | number/right |
| 29 | `pddl0` | PDDL0 | number/right |
| 30 | `pddl1` | PDDL1 | number/right |
| 31 | `pri` | PRI cell; active legacy body intentionally empty | code/right |
| 32–37 | `limit0`…`limit5` | LIMIT0…LIMIT5 | number/right |
| 38 | `lac` | LAC | mono/right |
| 39 | `cell` | CELL | mono/right |
| 40 | `imei` | IMEI | mono/right |
| 41 | `imsi` | IMSI | mono/right |
| 42 | `log_links` | USSD/SMS and Calls text links | control/right |
| 43 | `lifecycle` | activated/first call/last successful/blocked dates | date-stack/right |

The stale legacy footer `colspan="53"` is not schema evidence. Commented timing/mode headers are
excluded. PDDAS and empty PRI reproduce the active source honestly and are marked in tooltips as
legacy-source anomalies rather than silently reinterpreted.

### 4.2 Lines — `dongle.php` — 26 columns

`select`, `model_icon`, `cfun`, `simst`, `srvst`, `line`, `lock`, `state`, `err0`, `err1`,
`err2`, `mode`, `channel`, `rssi`, `snr`, `operator`, `cell_lac`, `iccid`, `serial`, `imei`,
`firmware`, `model`, `manufacturer`, `audio`, `data`, `dev`.

These are 26 separate cells. In particular the four leading model/CFUN/SIMST/SRVST cells must not
be collapsed. Technical identifiers and numeric/status values are right-aligned; icon controls are
centered. The route label is Lines in English and `Линии` in Russian; it replaces “Свистки
(normal mode)” without changing source behavior.

### 4.3 Programmer — `diagmode.php` — 6 columns

`log`, `device`, `model`, `port`, `state`, `progress`. The route label is Programmer in English and
`Программатор` in Russian; it replaces “Свистки (update mode)” without changing source behavior.

### 4.4 Hubs — `hubs.php` — 9 columns

`select`, `topology_1`, `topology_2`, `topology_3`, `topology_4`, `topology_5`, `topology_6`,
`usb_device`, `address`. The six middle cells preserve the legacy USB topology/device/power path.
Hubs is never titled Readers and has no reader fields.

### 4.5 Readers — `readers.php` — 12 columns

`select`, `model`, `reader_id`, `lock`, `state_result`, `spn`, `iccid`, `pin`, `imsi`, `ki`,
`ki_progress`, `dataport`. Readers is an independent visible navigation route, table definition and
storage namespace.

### 4.6 Command sets — `nabor.php` — 1 column

`name` (supported command-set name). Existing edit/link rendering stays within this cell.

### 4.7 Plans — `plan.php` — 82 columns

The complete manifest is the concatenation below; the Columns control may hide groups, but default
and Reset show all 82.

| Group | Count | Stable IDs in legacy order |
|---|---:|---|
| Base | 5 | `online`, `add_reserve`, `plan_nabor`, `priority`, `pro` |
| Timing | 7 | `diff_slow`, `diff_min`, `diff_min_vip`, `diff_min_goo`, `diff_min_nor`, `diff_min_sout`, `diff_min_imode` |
| Schedule | 4 | `time_work_wake`, `time_work_sleep`, `time_holiday_wake`, `time_holiday_sleep` |
| Modes | 23 | `can_in`, `can_out`, `can_sout`, `ivip`, `notvip`, `igoo`, `inor`, `ibad`, `ine0`, `inec`, `inem`, `inew`, `inos`, `iblo`, `irob`, `capnew`, `capfail`, `capok`, `imn`, `imb`, `imc`, `imd`, `ime` |
| Directions/limits | 16 | for N=1…4: `algN`, `nodiffN`, `limit_maxN`, `limit_hardN` |
| IATT | 15 | `iatt_soft`, `iatt_min`, `iatt_max`, `out_in_ans`, `out_in_dur`, `in_acd_min`, `in_acd_max`, `out_acd_min`, `out_acd_max`, `forwarding`, `outin`, `conn`, `rand`, `in_wait`, `in_sound` |
| SATT | 12 | `may_limit`, `mon_limit`, `msm_limit`, `smsout_soft`, `smsout_hard`, `nospam`, `satt_soft`, `satt_soft_day`, `satt_soft_total`, `satt_hard`, `satt_hard_day`, `satt_hard_total` |

Legacy `ima` is commented and excluded. `online` stacks online_day/online_max and `add_reserve`
stacks add_day/reserv_day/add_max because those are the active legacy cells. The legacy header calls
`limit_maxN` “limit_soft”; that mismatch is retained in source metadata and localized presentation.

### 4.8 Billing — `bablo.php` — 4 columns

`date`, `direction`, `minutes`, `money`. The approved visual's conceptual `Code + Operator` is
rendered inside the single legacy `direction` cell (icon/name plus accessible raw code); it is not a
fifth column. Money uses numeric formatting and right alignment. The route uses Fugue `money.png`.

### 4.9 Non-grid routes

- Processes: no invented data grid; active action/result surface only.
- Update: no invented data grid; action/result surface plus Version and Local changes logs.
- Debug: two independent one-column log grids, `sysdevs` and `usbdevs`.
- Icons: prototype audit grid, not legacy business data. It lists semantic slot, 1×/2× files,
  source/provenance, status and usage.

## 5. Active action manifest

Action fields appear inline after choosing a group. Selection-aware actions disable with a localized
reason when no compatible row is selected. Dangerous power/restart/update operations require an
inline confirmation state in the same rail; the prototype simulates result state and does not add
backend behavior.

| Route | Active legacy submits/links preserved |
|---|---|
| SIM | `refresh`; shared active `modules/actions.php`: `changeimei`, `blackimei`, `diagmode`, `donglerestart`; `pon`, `poff`; `sendussd(ussdcommand)`; `sendsms(smsnumber,smstext)`; `call60(call60number)`; `callspeak(callspeaknumber)`; `calldtmf(calldtmfnumber,calldtmfnabor)`; `setgroup(setgroupnumber)`; `set_plan_set`, `set_plan(set_plan_select)`, `set_plan_copy`, `set_autoblock_null`; `activate_sim`, `get_balance`, `get_number`, `get_minutes`, `get_tarif`, `get_options`, `get_dover`, `activate_work`; `complex_prepare`, `complex_prepare2`, `Complex_work`; `export_dongles`, `export_numbers`, `export_masspayment(export_masspayment_balance,minimum,maximum)`; `supersim_new(supersim_ki_owner)`, `supersim_set(dat_imsi,dat_iccid,dat_ki,dat_smsc)`; `newki(ki_owner)`, `setki(dat_*)`; `smsspam`; existing `?p=numbers` link; delay modifiers `delay_min`, `delay_rnd`, `delay_queue` |
| Lines | `refresh`, `changeimei`, `blackimei`, `diagmode`, `donglerestart`, `pon`, `poff`, `enterpin(pin)`, `setpin(setpinpin)`, `unlock`, `u2diag`, `setmode_gsm`, `setmode_wcdma`, `freqlock(freq)`, `atcommandexec(atcommand)` plus delay modifiers |
| Programmer | `refresh` |
| Hubs | `refresh`, `pon`, `poff`, `prestart` plus delay modifiers `delay_min`, `delay_rnd`, `delay_queue` |
| Readers | `refresh`, `removepin(pin)`, `setpin(setpinpin)`, `findki`, `apducommandexec(apducommand)` |
| Plans | `refresh`, legacy group visibility controls represented by Columns, `save`, `create_plan(plan_name,plan_nabor)` |
| Processes | `clear_sms`, `restart_svistok`, `restart_system`, `modeswitch`, `u2diag`, `dongles_restart`, `hubs_restart`, `clearsms`, `smsmag` |
| Update | `upgrade_full`, `upgrade_svn`, `upgrade_compile`, `upgrade_restart`, `restart_system` |
| Billing/Debug/Command sets | no new command invented; preserve only source links/edit affordances |

`rotki`, SIM `save`, and Hubs KI/APDU are explicitly excluded because their forms are commented.
Names, casing and parameters in the registry keep the legacy submit contract even when translated
labels are clearer.

## 6. Fugue icon contract

Every generic UI icon resolves to the full Fugue catalog by unchanged upstream filename. Each
vendored icon has an original 16×16 file in `assets/fugue/1x/` and matching rebuilt 32×32 file in
`assets/fugue/2x/`. Rendering uses a 16×16 CSS box and density selection such as:

```html
<img width="16" height="16"
     src="assets/fugue/1x/money.png"
     srcset="assets/fugue/2x/money.png 2x"
     alt="">
```

No 48px tier, scaling-based substitute, emoji, Lucide icon, CSS-drawn glyph or
`image-rendering: pixelated` is allowed. Text, row height, button padding and column widths are
calibrated around the actual 16px logical glyph, not the 32px source bitmap.

| Semantic slot | Fugue filename | Status |
|---|---|---|
| Billing route | `money.png` | fixed |
| Processes route | `application-task.png` | fixed; replaces heart-like `conn.png` |
| Filter/search | `magnifier.png` | resolved |
| Columns | `table-select-column.png` | resolved |
| Refresh | `arrow-circle.png` | resolved |
| Language | `globe.png` | resolved |
| Run/confirm | `tick.png` | resolved |
| Cancel | `cross.png` | resolved |
| Running | `hourglass.png` | resolved |
| Warning | `exclamation.png` | resolved |
| Lines | `plug.png` | resolved |
| Programmer | `processor.png` | resolved |
| Hubs | `network-hub.png` | resolved |
| Command sets | `script-code.png` | resolved |
| Plans | `calendar.png` | resolved |
| Icon audit | `images.png` | resolved |

Operator/network marks and legacy telemetry glyphs may remain only when they are the value of a
data field, not generic chrome. The icon audit labels those exceptions as `data/identity`. Any
semantic slot without a defensible upstream match is added to `FUGUE-WISHLIST.md`, left without a
misleading icon, and remains accessible by text.

### 6.1 Complete UI semantic mapping

This is the complete mapping contract for navigation, global controls and active action families.
Actions in the same family intentionally reuse one glyph; the localized label supplies the exact
verb. Every filename below was found in the upstream catalog and must be rechecked in both density
folders before vendoring.

| Placement / action family | Fugue filename | Semantic check |
|---|---|---|
| SIM route | unresolved; see wishlist | Fugue has handset/card/chip pictures but no honest SIM-card glyph |
| Lines route / modem connection | `plug.png` | physical connection |
| Programmer route / DIAG | `processor.png` | hardware programming target |
| Hubs route | `network-hub.png` | exact hub topology |
| Readers route | unresolved; see wishlist | no exact smart-card reader glyph |
| Command sets | `script-code.png` | stored command/script set |
| Plans | `calendar.png` | scheduled operating plan |
| Billing / get balance | `money.png` | monetary value |
| Processes | `application-task.png` | managed tasks/processes |
| Update | `download.png` | software retrieval/update |
| Debug | `bug.png` | diagnostic/debug context |
| Icons audit | `images.png` | image inventory |
| Filter / modem search | `magnifier.png` | find/search |
| Columns | `table-select-column.png` | exact column selection |
| Language | `globe.png` | locale/world language |
| Refresh | `arrow-circle.png` | reload current state |
| Restart software/device/system | `arrow-circle-double.png` | repeated/restart cycle |
| Run / activate / confirm | `tick.png` | positive execution/confirmation |
| Cancel / close | `cross.png` | cancel current inline state |
| Warning / failed state | `exclamation.png` | warning/error |
| Pending / delay modifiers | `clock-select.png` | scheduled/selected wait |
| Running/progress | `hourglass.png` | operation in progress |
| Power on | `control-power.png` | exact power control |
| Power off | `switch--minus.png` | switch disabled/off |
| Lock / unlock | `lock.png` / `lock-unlock.png` | exact lock state |
| Set PIN / remove PIN | `lock--plus.png` / `lock--minus.png` | add/remove credential protection |
| Voice call family | `telephone.png` | telephony call |
| SMS family | `mail.png` | message |
| Clear SMS / spam state | `mail--minus.png` / `mail--exclamation.png` | remove/warn message |
| USSD / raw AT command | `terminal.png` | textual device command |
| Export data | `table-export.png` | export table records |
| Save plan | `disk.png` | persistent save |
| Create plan | `calendar--plus.png` | add scheduled plan |
| Compile | `compile.png` | exact compilation action |
| Maintenance / mode repair | `hammer-screwdriver.png` | device/software maintenance |
| Set KI / create KI | `key.png` / `key--plus.png` | secret key/update |
| KI Search | unresolved; see wishlist | search modifier is absent for `key` family |
| APDU command | unresolved; see wishlist | generic card/terminal icons are not smart-card specific |
| Logs / debug output links | `terminal.png` | command/log stream |

The specification wishlist is
[`FUGUE-WISHLIST.md`](FUGUE-WISHLIST.md). During implementation it is copied/maintained next to the
consuming prototype icon map so unresolved slots remain visible to future icon work.

## 7. Typography, density and alignment

Interface text uses the existing NativeMind UI stack. Dense data and identifiers use
`"IBM Plex Mono", "Roboto Mono", ui-monospace, SFMono-Regular, Consolas, monospace`; implementation
may vendor IBM Plex Mono or use the fallback stack without network loading. Numeric, code, date,
identifier and technical text columns are right-aligned, including header labels. Control/icon
cells remain centered; genuinely prose-oriented labels may remain left-aligned when required for
scanability. Tabular numbers use `font-variant-numeric: tabular-nums`.

Normal density targets a 24px row, 16px glyph and 12–13px data text. Retina changes only the chosen
bitmap source, never CSS geometry. Focus rings, selected rows, sort state and disabled actions must
not depend on color alone.

## 8. Localization contract

English is the initial locale; choices are `en`, `th`, `ru`, `hi`, `zh`. Every dictionary has the
same complete key set covering routes, headings, actions, fields, columns, states, validation,
confirmations, tooltips and accessible labels. Development validation reports missing and extra
keys. Runtime missing keys fall back to English and log the key; no bilingual label is constructed.

Examples: `routes.hubs` is Hubs/Хабы in English/Russian and `routes.readers` is Readers/Ридеры.
Raw identifiers, submit names, state codes and device values are never translated. Locale changes
rerender current UI but do not reset grid state, selection or route.

## 9. Interaction and edge cases

- Filter applies to all rendered/searchable values, including stacked values, and announces the
  result count. Empty query restores all rows.
- Changing table route closes the current action mode and Columns popover, while retaining that
  table's persisted column configuration.
- One expanded rail group at a time. Escape/Cancel returns to idle without moving the grid.
- Validation errors stay inline in the rail and preserve entered values.
- Loading, success and failure replace the same flexible rail area and do not resize it.
- Long translated labels switch to icon-only mode before collision; tooltip and accessible name
  always use the active locale.
- Columns cannot hide the required selection column while a selection action exists. Reordering
  cannot detach headers from cells.
- All 82 Plan columns remain available through horizontal grid scrolling; the page itself does not
  become horizontally unstable.
- Empty tables retain headers and toolbar. Broken assets show a textual audit error, not a browser
  broken-image placeholder.

## 10. Verification gates

Implementation is complete only after these checks pass:

1. Static registry test asserts route presence and exact manifest counts: SIM 43, Lines 26,
   Programmer 6, Hubs 9, Readers 12, Command sets 1, Plans 82, Billing 4, Debug 1+1.
2. Default and Reset visible-column counts equal the corresponding manifests.
3. Action registry is compared against the active legacy list above; excluded commented actions
   are absent and Readers/Hubs inventories remain separate.
4. Every generic UI icon file exists in both 1× and 2× folders and both images have 16×16 and
   32×32 intrinsic dimensions respectively; no broken reference, emoji or Lucide fallback remains.
5. All five locale dictionaries have identical keys and switching locale removes prior-language
   copy from navigation, headings, toolbar and states.
6. Browser interaction verifies sort asc/desc, hide/show, reorder, Reset and persistence for every
   table type, including the 82-column Plans grid.
7. Browser widths verify full-label and icon-only modes keep the toolbar/grid boundary fixed.
8. Browser density verification confirms a 16px logical icon box at 1× and 2× DPR.
9. Keyboard verification covers navigation, filter, groups, action fields, confirmation, headers,
   Columns controls and Escape.
10. `git diff --check` and a broken-local-asset scan pass; `support.js` and `_ds/**` remain unchanged.

## 11. Specification approval gate

Status is **APPROVED**. The user approved this specification on 2026-09-01; PLAN may proceed.

### Implementation clarification — resolved wishlist slots

After implementation review, the user explicitly requested icons be applied. This supersedes the
text-only behavior for four slots: SIM=`card.png`, Readers=`scanner.png`, KI Search=`magnifier.png`,
APDU=`terminal--arrow.png`. All use the standard 16×16/32×32 Fugue density contract. Proposed exact
domain glyphs remain wishlist refinements only and are not referenced as current files.
