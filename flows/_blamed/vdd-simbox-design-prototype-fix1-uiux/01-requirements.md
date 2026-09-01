# Requirements: SimBox v2026 — compact actions, data grids and icon audit

> Version: 1.0  
> Status: APPROVED  
> Last Updated: 2026-09-01

## Problem Statement

`design/simbox-design-prototype-v2026/index.html` уже предлагает современную одностраничную реконструкцию SimBox: CSS Grid-таблицы, выбор строк, сортировку, фильтр, grouped actions и inline-логи. Однако вся реализация находится в одном крупном HTML-файле, toolbar плохо масштабируется по ширине, раскрытая action-панель закрывает верхние строки grid, нет hide/reorder колонок и language selector. Часть подписей и иконок не соответствует новой терминологии или legacy-семантике, а текущий каталог иконок не доказывает соответствие выбранного glyph его реальному назначению.

Нужно переработать все data-grid экраны и связанные action controls, сохранив бизнес-функции из `legacy/simbox-desktop-v2014` без добавления новых телеком-команд.

## Source Priority

При расхождениях применяется следующий порядок:

1. **Функции, поля, параметры, область действия и raw state:** legacy PHP (`sim.php`, `dongle.php`, `diagmode.php`, `hubs.php`, `readers.php`, `nabor.php`, `plan.php`, `proc.php`, `bablo.php`, `upgrade.php`, `debug.php`, `modules/html.php`).
2. **Интерактивная модель и демонстрационные данные:** текущий `design/simbox-design-prototype-v2026/index.html` и `support.js`.
3. **Уникальные телеком/operator/QoS glyphs:** `nativemind-adminka` taxonomy и provenance map.
4. **Общие action/status/navigation glyphs и Fugue-derived legacy glyphs:** `nativemind-fugue-icons`, оригинальная 16×16 + 32×32 density pair.
5. **Общие цвета, SF Pro Text и spacing:** NativeMind design system; Fugue sizing rules имеют приоритет над устаревшим generic 48px icon-tier правилом design system.

## User Stories

### Primary

**Как оператор SimBox**  
**я хочу** видеть фильтр и компактные действия в одной строке непосредственно над текущей таблицей  
**чтобы** быстро применять legacy-команды к выбранным строкам, не теряя контекст данных.

**Как оператор SimBox**  
**я хочу** раскрывать параметры действия внутри той же toolbar-строки  
**чтобы** таблица не сдвигалась и её строки не перекрывались.

**Как оператор плотной таблицы**  
**я хочу** сортировать, скрывать и переставлять столбцы  
**чтобы** собрать представление под конкретную операционную задачу.

### Secondary

**Как разработчик прототипа**  
**я хочу** разнести screen/table definitions, runtime и CSS по отдельным файлам  
**чтобы** изменения одного типа таблицы не требовали редактирования монолитного `index.html`.

**Как оператор на Retina/HiDPI**  
**я хочу** видеть семантически правильные резкие Fugue-иконки  
**чтобы** glyphs оставались pixel-faithful и не вводили в заблуждение.

## In-Scope Screens

| Route/state | English / Russian dictionary values | Legacy source | Grid/UI scope |
|---|---|---|---|
| `sim` | SIM cards / Симки | `sim.php` | Полная SIM grid, selection, filters, actions, columns, sort |
| `dongle` | Lines / Линии | `dongle.php` | Normal-mode grid и все modem/line actions |
| `diagmode` | Programmer / Программатор | `diagmode.php` | Update/firmware grid и programmer actions |
| `hubs` | Hubs / Хабы | `hubs.php` | USB tree и hub actions |
| `readers` | Readers / Ридеры | `readers.php` | Independent reader table and reader actions |
| `nabor` | Command sets / Наборы команд | `nabor.php` | Structured list/grid и существующее редактирование |
| `plan` | Plans / Планы | `plan.php` | Полная editable plan grid, column groups, save/create |
| `proc` | Processes / Процессы | `proc.php` | Compact command toolbar/panel; новых действий нет |
| `bablo` | Billing / Биллинг | `bablo.php` | Billing grid, existing filters/totals |
| `upgrade` | Update / Обновление | `upgrade.php` | Compact safe/danger action grouping |
| `debug` | Debug / Отладка | `debug.php` | Diagnostic structured data; no invented actions |
| `icons` | Icons / Иконки | legacy legends + taxonomy | Полная проверяемая таблица используемых glyphs |

`Линии` полностью заменяет пользовательские заголовки/навигационные подписи `Свистки (nm)` и `Свистки (normal mode)`. `Программатор` заменяет `Свистки (um)` и `Свистки (update mode)`. Route keys, raw `dongle*` identifiers, shell commands и legacy parameter names не переименовываются.

## Legacy Functional Parity

### SIM actions that must remain available

- Refresh/save, power on/off, pause/work.
- USSD; SMS number + message; Call60; CallSpeak; CallDTMF number + sequence.
- Set group; set plan without copy; set plan with copy; restore plan parameters; clear autoblock flags.
- Activate SIM; Get balance, number, minutes, tarif, options, dover; Activate work.
- Complex prepare; Complex prepare 2; Complex work.
- Export dongles; export numbers; masspayment with required balance, minimum and maximum payment fields.
- Delay, random delay and queue instead of immediate launch.
- SuperSIM/KI data actions, Auto new KI, Set data, Rotator options.
- Bulk SMS send.

### Lines, Programmer, hubs and readers

- Lines: refresh; change/blacklist IMEI; enter diagmode; restart; power; enter/change PIN; CARDLOCK; U2DIAG; GSM/WCDMA; frequency lock; AT command; delay/queue.
- Programmer: existing update/diagmode operations and progress states only.
- Hubs: refresh; port power on/off/restart; delay/queue; KI search; relevant APDU operations.
- Readers: refresh; remove/set PIN; KI search; APDU.
- Process and upgrade commands remain exactly the legacy command set, with destructive/system commands visually separated and confirmed.

The current v2026 implementation exposes only part of this inventory. Specifications must produce a legacy-to-prototype action matrix, and implementation must restore missing UI affordances without inventing new behavior.

## Toolbar and Actions Requirements

1. Filter, selection state, primary controls, action groups, Columns and Refresh live in one toolbar row above the current grid.
2. Opening a parameterized action must not change the grid's top/height, cover grid rows, or create page-level horizontal scrolling.
3. On wide containers, safe frequent actions retain short text labels. On narrower containers, action labels disappear and 16px logical icon buttons remain with `title`, `aria-label` and visible focus.
4. If the filter input no longer fits, it collapses to a filter icon that opens an anchored editor within the toolbar interaction layer; filter functionality remains one click away.
5. At most one action editor/group is open. Escape closes it and restores focus to the trigger.
6. Selection-only actions are disabled at zero selection and expose the reason. Page-level actions remain available without selection.
7. Dangerous actions are separated from everyday controls, use danger styling and require confirmation. No confirmation is added to harmless commands.
8. Running/success/error state occupies a reserved toolbar status slot, preventing layout shift.
9. No nested multilevel menus: a category and one inline editor are the maximum depth.
10. Responsive behavior is driven by the table container width, preferably with container queries, not only global viewport breakpoints.

## UI Alternatives to Explore in VISUAL

### A — Morphing inline action rail (recommended)

The toolbar stays one row. Opening a category temporarily compresses icon groups and replaces the middle segment with that category's inputs/actions. Filter and Columns stay pinned at the end. No popover enters the grid area.

### B — Upward anchored command popover

The toolbar remains unchanged; an action editor opens upward into free space above the table card. Compact and familiar, but requires collision handling with the application header.

### C — Searchable command palette

One `Actions` trigger opens a floating command palette outside the grid bounds; choosing a command reveals its fields in the same palette. Most compact, but frequent commands are less discoverable.

VISUAL must compare A/B/C on the SIM screen and show the recommended pattern adapted to every grid type.

## Data Grid Requirements

1. Apply to every structured data grid, including specialized Plans, Billing, Hubs/Readers and Command Sets, not only the generic SIM grid.
2. Header labels and textual/numeric cell values are right-aligned by default for scanability. Selection checkboxes and pure icon cells are centered; tree indentation and command/log prose may remain left-aligned where direction is semantically meaningful.
3. Use the recommended system monospace stack for identifiers, numbers that benefit from column alignment, raw codes and commands: `ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace`.
4. Keep SF Pro Text for human-readable names, actions and explanatory text. Enable `font-variant-numeric: tabular-nums` for aligned proportional-number contexts.
5. Existing sort remains functional for every sortable column. Sort state and direction are visibly indicated; non-sortable icon/action columns do not pretend to be sortable.
6. Columns control supports hide/show, drag reorder, keyboard move up/down, Reset and visible-count summary.
7. Selection/identity anchor columns remain pinned, visible and outside reorder/hide controls.
8. Header and body use the same ordered column definition so CSS Grid tracks cannot drift.
9. Column order/visibility and sort state persist per table key in localStorage with schema-safe fallback when definitions change.
10. Columns needed for selection, action targeting or minimum identity remain protected. All other legacy columns remain available even when hidden by user preference.
11. A column-by-column audit against every listed legacy PHP screen is required; missing legacy fields are restored, but no new domain fields are added.

## Icon Requirements and Complete Audit Table

1. "Полная таблица иконок" means every icon actually rendered or selectable by this prototype, including all legacy state variants, action/navigation controls and table headers—not all 3,570 unused Fugue glyphs.
2. The on-screen `Иконки` route becomes a real audit table with these columns:
   - rendered preview;
   - semantic category;
   - raw code/state;
   - UI meaning;
   - screen/component usage;
   - legacy PHP/function reference;
   - current local asset path;
   - Fugue 16×16 source filename;
   - Fugue 32×32 source filename;
   - provenance (`Fugue`, `Fugue modified`, `GostSimBox custom`);
   - verification status and notes.
3. Every row is verified against both what is visibly drawn and what the legacy source says it means. Similar-looking glyphs are not accepted without semantic match.
4. Generic UI actions use the closest exact Fugue glyph from `nativemind-fugue-icons`; arbitrary Lucide/emoji substitutions are not used.
5. Fugue-derived legacy icons use a 16×16/32×32 density pair with identical filenames in separate tiers. Standard-density displays receive 16×16 physical pixels; Retina/2× receives 32×32 physical pixels in the same 16×16 logical box.
6. Do not create or request a 48px Fugue tier. Padded 48px PSD canvases are not usable 48px icons.
7. Unique operator, modem, protocol/QoS and other hand-drawn GostSimBox glyphs remain when no semantically exact Fugue replacement exists. The audit table marks these explicit exceptions rather than silently replacing them with a generic image.
8. Font, row height, padding, gaps, hit areas and icon-led column widths derive from the logical icon unit so they remain visually proportional across densities.
9. Replace deprecated `pause2.png` with canonical `pause.png` / Fugue `control-pause.png`. No new use of deprecated provenance-map entries.
10. Missing assets degrade to a text label/status, not emoji. Icon and fallback are never shown simultaneously.
11. Only icons used by the prototype are vendored; do not copy the whole Fugue archive into the project.

## Language Selector

1. Add a shared selector in the application header with `English` as default, followed by `ไทย`, `Русский`, `हिन्दी`, `中文`.
2. Use the density-aware Fugue globe icon, not emoji.
3. Current selection, open/closed state, keyboard navigation, active checkmark and focus return are represented.
4. Selection persists locally and updates the language code/name shown in the header.
5. All five requested locales receive complete, key-parity UI dictionaries. Route keys, raw state,
   commands and domain identifiers stay untranslated; RTL is not introduced because the requested
   languages use left-to-right layout.

## File Decomposition Requirements

1. Move inline CSS out of `index.html` into purpose-specific files. Expected groups: tokens/base, app layout, toolbar/actions, data grid, icons, responsive states. Exact names are finalized in SPECIFICATIONS.
2. Move screen/table definitions into separate `.js` files by type: SIM, Lines, Programmer, Hubs/Readers, Command Sets, Plans, Billing and non-table command screens where useful.
3. Shared runtime owns selection, filtering, sorting, column preferences, toolbar editor state, language state, logs/toasts and icon resolution.
4. Shared action definitions are reused; screen files only declare which existing legacy actions are available.
5. Preserve the existing DC/plain-browser runtime. Do not add React/Vue, a bundler, external CDN dependency or backend.
6. Preserve simple local launching. Prefer classic deferred scripts/registry if ES modules would break `file://` behavior.
7. `index.html` becomes an application shell and template rather than the storage location for all data and behavior.

## Acceptance Criteria

### Must Have

1. **Given** any grid screen  
   **When** the toolbar renders at wide, medium or compact width  
   **Then** filter and actions stay in one row, remain reachable and never overlap or shift grid rows.

2. **Given** a parameterized action is opened  
   **When** its editor expands and closes  
   **Then** grid bounds remain unchanged and focus behavior is keyboard-correct.

3. **Given** comparison with legacy action forms  
   **When** the action-parity matrix is reviewed  
   **Then** every legacy action and parameter is reachable and no new business action exists.

4. **Given** any sortable/hideable grid  
   **When** the user sorts, hides, shows or reorders columns  
   **Then** header/body remain aligned, protected columns remain valid and preferences survive reload.

5. **Given** all grid definitions  
   **When** compared column-by-column to legacy PHP  
   **Then** every legacy field is present or explicitly documented as non-tabular/prototype-only; no domain column is invented.

6. **Given** table text and identifiers  
   **When** rows are scanned vertically  
   **Then** default alignment is right, icon/selection exceptions are centered, and identifiers use the agreed monospace stack.

7. **Given** `dongle` and `diagmode` screens  
   **When** navigation, page title, action heading and user-facing messages render  
   **Then** they use `Линии` and `Программатор` consistently while routes/raw identifiers stay unchanged.

8. **Given** a 1× or 2× display  
   **When** Fugue icons render  
   **Then** the 16×16 or 32×32 source is selected pixel-for-pixel in a 16px logical box and surrounding layout remains proportional.

9. **Given** the `Иконки` route  
   **When** its audit table is reviewed  
   **Then** every icon used/selectable in the prototype has traceable source, meaning, usage, density pair/provenance and verification status.

10. **Given** the application header  
    **When** language is selected  
    **Then** all five requested options exist, English is the initial default and selection state persists.

11. **Given** project structure after implementation  
    **When** files are inspected  
    **Then** CSS and screen/table definitions are separated from `index.html` without framework/build regressions.

12. **Given** the prototype is opened locally  
    **When** every route, action group and table control is exercised  
    **Then** there are no console errors, missing assets, broken grid tracks or inaccessible controls.

### Should Have

- Direct buttons for safe high-frequency commands and icon-only compact mode for the same commands.
- Search/filter and Columns remain pinned when the grid scrolls horizontally.
- Reset-all table preferences is available in addition to per-table reset.
- Audit table can filter by category, screen and failed verification status.
- Status announcements use a non-disruptive `aria-live` region.

### Won't Have (This Iteration)

- New telecom workflows, backend APIs, permissions or automation.
- Backend-driven translation management or server-synchronized locale preferences.
- Copying all 3,570 Fugue icons into the prototype.
- Replacing unique GostSimBox/operator glyphs with semantically weaker generic icons.
- Framework migration, bundler or production PHP rewrite.
- New data columns absent from legacy.

## Constraints

- **Functional:** legacy is authoritative; current prototype interactions must not regress.
- **Layout:** one grid scroller; no action overlay over data rows and no page-level horizontal scrollbar.
- **Density:** Fugue has only 16×16 and 32×32 usable tiers; 48px is forbidden.
- **Assets:** preserve CC BY 3.0 attribution for Yusuke Kamiyamane.
- **Technical:** DC/static browser runtime, local assets, no build step.
- **Accessibility:** keyboard navigation, accessible names, focus restoration, visible focus and non-color-only state.

## Assumptions Requiring Approval

- [ ] The complete icon table covers every icon used/selectable by this prototype, not the entire unused Fugue archive.
- [ ] All five requested languages use complete UI dictionaries with identical key sets and no
  bilingual labels.
- [ ] `32×32 on Retina` means a 32×32 physical source rendered in a 16×16 logical box, per the updated Fugue skill.
- [ ] Unique legacy glyphs remain when Fugue has no exact semantic equivalent.
- [ ] Routes/internal `dongle` identifiers remain unchanged while user-facing names become `Линии` and `Программатор`.

## References

- `design/simbox-design-prototype-v2026/index.html`
- `design/simbox-design-prototype-v2026/support.js`
- `legacy/simbox-desktop-v2014/www/simbox/`
- `/Users/anton/.codex/skills/nativemind-fugue-icons/SKILL.md`
- `/Users/anton/.codex/skills/nativemind-adminka/SKILL.md`
- `/Users/anton/.codex/skills/nativemind-adminka/assets/adminka/adminka-to-fugue-map.json`
- `/Users/anton/.codex/skills/nativemind-adminka/guidelines/adminka-taxonomy.html`

---

## Approval

- [x] Reviewed by: user
- [x] Approved on: 2026-09-01
- [x] Notes: explicitly approved with `requirements approved`

---

## Legacy Additions — complete table reconstruction and Readers route

> Added: 2026-09-01  
> Status: APPROVED  
> Authority: this additive clarification supersedes the combined `Хабы / ридеры` shorthand
> in the earlier scope table without removing any previously accepted requirement.

### Deep legacy audit rule

The implementation must reconstruct every primary legacy data table **column-for-column,
without loss**. Visual modernization, action grouping and responsive behavior may change the
presentation, but may not merge, omit or replace separate legacy fields with a summarized cell.

1. The initial/reset view exposes every legacy logical column. A column may disappear only after
   an explicit user choice in Columns; default-hiding is not accepted as parity.
2. Each legacy header cell receives a stable target column key. Blank/icon-only headers remain
   distinct columns and get an accessible semantic name instead of being silently collapsed.
3. A legacy cell that contains several intentionally stacked values (for example CELL/LAC) stays
   one logical column. Values from separate legacy `<td>` elements stay separate target columns.
4. `rowspan`, `colspan`, multi-row headers, conditional cells and totals rows are counted by their
   logical grid width, not by a naive count of tags.
5. Header definitions, sample/body rows and totals rows must resolve to the same logical width.
   Any legacy mismatch is documented and corrected explicitly in the target mapping rather than
   copied as an alignment bug.
6. The audit covers table data, formatting, raw state, icon helper/condition, action target identity,
   and whether a column is sortable, hideable, reorderable or protected.
7. Before implementation, SPECIFICATIONS must contain a complete legacy-table manifest with:
   route and PHP source; table purpose; legacy index/header; body expression/source; icon/helper;
   target key/label; alignment/font; target file; visibility/protection; parity status and notes.
8. Automated/static parity checks must compare each target definition against the approved manifest
   and verify unique keys, complete order, equal header/body widths and no unaccounted legacy field.

Primary audit sources are `sim.php`, `dongle.php`, `diagmode.php`, `hubs.php`, `readers.php`,
`nabor.php`, `plan.php`, `proc.php`, `bablo.php`, `upgrade.php`, `debug.php`, shared render helpers
in `modules/html.php`, and the navigation/router in `head.php` and `index.php`. Auxiliary result,
log and action-form tables are inventoried separately so they are not mistaken for primary grids.

### Separate Readers navigation destination

`readers` becomes a first-class prototype route and visible navigation item: **Readers** in
English and **Ридеры** in Russian. It is not embedded in or aliased to `hubs`.

| Route | Visible name | Legacy source | Required primary grid |
|---|---|---|---|
| `hubs` | Хабы | `hubs.php` | 9 logical columns: selection, six tree/device/power depth slots, raw USB device text, address |
| `readers` | Readers / Ридеры locale values | `readers.php` | 12 logical columns listed below |

The legacy router already resolves `?p=readers` through `index.php`; `head.php` contains the
Readers link inside a commented navigation block. Making it visible in the reconstructed menu is
restoration of an existing screen, not an invented workflow. The misleading `<h1>Ридеры</h1>` in
`hubs.php` does not make the two data models one table.

#### Readers: verified 12-column baseline

| # | Legacy header / role | Legacy body source | Target behavior |
|---:|---|---|---|
| 1 | selection checkbox | reader device id | protected, centered |
| 2 | model/icon (blank header) | `$device.model`; `1001` → `pl2303.ico` | centered, accessible name “Model” |
| 3 | Ридер | `$device` | right-aligned monospace identity |
| 4 | lock icon | `$device.lock` | centered header icon; value preserved |
| 5 | state | `$device.status` plus nonzero result code | right-aligned status |
| 6 | SPN | `$device.spn` | right-aligned text |
| 7 | ICCID | state `$device.iccid` | right-aligned monospace |
| 8 | PIN | `$device.pin` | right-aligned monospace |
| 9 | IMSI | SIM state `$iccid.imsi` | right-aligned monospace |
| 10 | KI | SIM state `$iccid.ki`; all-zero value abbreviated by legacy | right-aligned monospace |
| 11 | progress (blank header) | GSM file size / 58, displayed as progress `/31044` | right-aligned; accessible name “KI search progress” |
| 12 | dataport | `$device.dataport` | right-aligned monospace |

The Readers toolbar preserves exactly these `readers.php` actions: Refresh; Remove PIN; Set PIN;
Start KI search; Execute APDU command. Their parameter fields remain available in the same-row
adaptive action pattern defined earlier.

### File decomposition clarification

Hubs and Readers use separate table definition files (expected `tables/hubs.js` and
`tables/readers.js`, with exact paths finalized in SPECIFICATIONS). Shared grid/runtime behavior
is reused, but neither screen owns or mutates the other's schema.

### Additional acceptance criteria

13. **Given** any primary legacy table  
    **When** its approved manifest is compared with the target table definition  
    **Then** every logical legacy column exists once, in traceable order, and all columns are
    visible after Reset with no summarized or default-hidden loss.

14. **Given** the application navigation  
    **When** the operator selects **Readers** in English or **Ридеры** in Russian  
    **Then** the independent `readers` route opens its 12-column table and Readers actions; the
    `hubs` route remains a separate 9-column USB-tree screen.

15. **Given** the Readers table  
    **When** header, sample rows, sorting, hide/reorder and Reset are exercised  
    **Then** all 12 columns remain aligned, identity/selection protection is preserved and no
    Readers field or action from `readers.php` is lost.

### Added assumptions requiring approval

- [ ] “Все столбцы без потерь” means every legacy logical column is visible in the initial/reset
  view; operators may subsequently hide non-protected columns themselves.
- [ ] The visible navigation label is `Readers` in English and `Ридеры` in Russian while the stable
  internal route remains `readers`.

---

## User Clarification — one action pattern, Fugue-only UI glyphs, route labels

> Added: 2026-09-01  
> Status: APPROVED  
> Authority: this section narrows and supersedes conflicting wording in “UI Alternatives to
> Explore”, the custom-glyph exception, and the earlier Hubs label.

### One final toolbar pattern

Only **Morphing inline action rail** is carried into the final visual and implementation. The
earlier A/B/C list records considered directions, but does not require three production variants
or three complete mockup families.

“Morphing” means replacement inside a fixed toolbar track, not expansion:

```text
Idle
[ Filter __________________ ] [Selected: 3] [↻] [Power] [SIM] [Calls] … [Columns]

Power selected — same row, same height and table position
[ Filter __________ ] [3 selected] [← Power:  ON | OFF | RESTART  ✓ Run  ×] [Columns]
                                      ^ middle action rail is replaced in place ^
```

1. The toolbar has three zones: pinned context/filter, a flexible action rail, and pinned table
   controls. Its block size does not change between idle, editor, validation, confirmation,
   running, success and error states.
2. Activating a group replaces only the flexible rail with that action's compact editor. It does
   not add a row, open over the grid or alter the grid's top coordinate.
3. Short commands render as direct Fugue icon buttons. Commands with parameters render their
   existing fields, Run and Cancel inside the rail. No new workflow step or command is invented.
4. At medium width, action text disappears while `aria-label`, tooltip, focus and grouping remain.
   The active editor gets priority over idle buttons.
5. At compact width, filter becomes a Fugue icon trigger and inactive groups reduce to icons. The
   rail may scroll internally on the inline axis, but the page and table card do not gain a second
   horizontal scrollbar.
6. Escape/Cancel returns the idle rail and trigger focus. Only one editor or confirmation state is
   active. Validation and execution status replace a reserved segment rather than changing height.
7. Columns and Refresh stay reachable at the pinned edge in every state.

VISUAL therefore demonstrates this one pattern in representative idle, parameter-editor,
confirmation, narrow/icon-only and status/error states, then applies the same rules to all screens.

### Fugue-only UI icon policy and wishlist

Every navigation, action, status, filter, table-control and generic table glyph must use an exact
Fugue icon from the full local 3,570-icon upstream set. Existing emoji, Lucide/SVG approximations
and unrelated custom substitutes are not accepted.

1. Search the full `nativemind-fugue-icons` archive, not only the small sample or currently vendored
   project assets.
2. Vendor only selected glyphs, always as same-name 16×16 and 32×32 density pairs.
3. The icon audit table must mark `selected`, `candidate`, `missing semantic match` or `not a UI
   icon` for every visual asset location.
4. If the currently selected set lacks a needed glyph, add it to a **Fugue wishlist** with screen,
   action/state, required meaning, searched terms, candidate upstream filenames, preferred choice
   and unresolved reason. Do not silently substitute an emoji or a semantically weaker icon.
5. When a matching upstream Fugue glyph exists, the wishlist item is resolved by vendoring its
   density pair; no new artwork is drawn.
6. Brand/operator marks and content images are classified separately as data/identity, not UI
   controls. They remain only where the legacy field's value would otherwise be lost. Every such
   exception is explicit in the audit instead of being presented as a Fugue glyph.
7. If “Fugue everywhere” is intended to remove even operator/brand identity images, that would
   destroy legacy field semantics and requires a separate explicit approval; it is not assumed.

This policy supersedes the earlier allowance for generic custom UI glyphs. It does not change the
16px logical box, 1×/2× source selection, proportional spacing or CC BY 3.0 attribution rules.

### Localized route labels

| Route | English | Russian | Relationship |
|---|---|---|---|
| `hubs` | **Hubs** | **Хабы** | independent 9-column USB topology and hub actions |
| `readers` | **Readers** | **Ридеры** | independent 12-column reader table and reader actions |

Readers is never displayed inside the Hubs screen and neither schema is stored in a combined
table-definition file.

### Additional acceptance criteria

16. **Given** any idle or active action state  
    **When** a command group opens, validates, confirms, runs or closes  
    **Then** only the flexible rail content changes; toolbar height and grid bounds remain identical.

17. **Given** the prototype's UI glyph inventory  
    **When** the Fugue audit is reviewed  
    **Then** every UI glyph maps to an upstream Fugue 16×16/32×32 pair or appears as an unresolved
    wishlist item with no silent non-Fugue fallback.

18. **Given** navigation and page headings  
    **When** Hubs or Readers is opened  
    **Then** the active locale shows `Hubs`/`Readers` or `Хабы`/`Ридеры`, with separate routes,
    schemas and action inventories and no mixed labels.

---

## User Clarification — locale-pure copy and resolved navigation icons

> Added: 2026-09-01  
> Status: APPROVED  
> Authority: this section supersedes every bilingual label example and the earlier selector-only
> localization limitation.

### One active language, no mixed labels

Visible interface copy must belong to the currently selected locale. Parenthetical combinations
such as `Hubs (Хабы)` and `Ридеры (Readers)` are forbidden in the running UI.

| Stable route | English | Russian |
|---|---|---|
| `hubs` | Hubs | Хабы |
| `readers` | Readers | Ридеры |
| `proc` | Processes | Процессы |
| `bablo` | Billing | Биллинг |

The same rule applies everywhere: navigation, page titles, toolbar groups, actions, field labels,
column titles, empty/loading/error states, confirmations, tooltips, accessible names and messages.
Thai, Hindi and Chinese receive their own locale dictionaries in the approved language set rather
than English/Russian text joined in one label.

1. Route keys, command names, identifiers, raw state codes, shell paths and data values are not
   translated.
2. All five locale dictionaries must have the same key set. A development-time parity check reports
   missing and extra keys before implementation is considered complete.
3. English remains the initial default. Selecting another language updates the entire visible UI,
   not only the selector label.
4. If a translation key is unexpectedly absent at runtime, the UI uses the English value for that
   key and records the missing-key condition; it never constructs a bilingual parenthetical label.
5. The earlier statements that localization is selector-state-only and that full translation is a
   Won't Have are withdrawn by this clarification.

### Resolved Fugue navigation icons

| Route | Current problem | Selected upstream Fugue glyph | Reason |
|---|---|---|---|
| `bablo` / Billing | current `may.ico` is broken and semantically unrelated | `money.png` | recognizable banknote/cash glyph; exact Billing meaning |
| `proc` / Processes | current `conn.png` reads visually as a heart/health symbol | `application-task.png` | application window with task list; communicates managed processes/tasks |

Both selections are resolved, not wishlist items. Each must be vendored with the unchanged upstream
filename as an original 16×16 source and matching 32×32 `icons-2x` source, rendered in the same
16×16 logical box. The selected glyph is used consistently in navigation, relevant heading/context
locations and icon audit rows; unrelated action-specific icons inside these screens retain their
own audited Fugue meanings.

### Additional acceptance criteria

19. **Given** any selected locale  
    **When** any route or interaction state is rendered  
    **Then** all translatable UI copy comes from that locale, with no parenthetical language mixing.

20. **Given** the Billing navigation item  
    **When** it renders at 1× or 2× density  
    **Then** it uses the valid Fugue `money.png` density pair and no broken `may.ico` reference.

21. **Given** the Processes navigation item  
    **When** it renders at 1× or 2× density  
    **Then** it uses the Fugue `application-task.png` density pair and no `conn.png` heart-like glyph.

---

## Source-conflict resolution — active legacy behavior only

> Added: 2026-09-01  
> Status: APPROVED  
> User decision: preserve active legacy behavior; do not revive commented forms.

The apparent KI Search/APDU actions in `hubs.php:358-387` are inside a PHP block comment. They are
therefore historical source artifacts, not Hubs functionality. The implementation must expose only
the active Hubs actions: Refresh, Power on, Power off, Restart and the existing delay modifiers.

KI Search and APDU remain active on the independent Readers route, where `readers.php` actually
implements them. The same active-code rule applies to other commented artifacts discovered by the
audit: for example the commented SIM `rotki` and `save` controls are recorded as exclusions and are
not restored. This resolves the earlier contradiction without inventing functionality.

---

## Implementation clarification — apply icons to every active slot

> Added: 2026-09-01  
> Status: APPROVED by direct user request: «Иконки примени»

The four previously text-only wishlist slots now use intentional existing Fugue matches:

| Slot | Applied Fugue filename | Interpretation |
|---|---|---|
| SIM route | `card.png` | neutral physical card; label provides SIM specificity |
| Readers route | `scanner.png` | physical reading device |
| KI Search | `magnifier.png` | exact search action; label provides KI object |
| APDU | `terminal--arrow.png` | sending/executing a terminal command; label provides APDU context |

The more exact proposed filenames remain documented as future refinements, but all current routes
and active actions now display a real Fugue density pair.
