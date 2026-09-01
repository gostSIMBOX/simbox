# Implementation Plan: SimBox v2026 UI/UX fixes

> Version: 1.0  
> Status: APPROVED  
> Last Updated: 2026-09-01  
> Specifications: [03-specifications.md](03-specifications.md)

This phase starts after explicit approval of specifications.

## 1. Delivery strategy

Implementation proceeds in dependency order and keeps the prototype runnable after each wiring
step. The target `design/simbox-design-prototype-v2026/` is its own clean nested Git repository;
all product edits and checks are scoped there. Generated `support.js` and `_ds/**` are read-only.

No package manager, network dependency or build step is introduced. The prototype must continue to
open over `file://` using classic scripts. Existing logo/content assets are preserved unless the
approved icon audit explicitly replaces a generic UI glyph.

Complexity scale: **S** = isolated/mechanical, **M** = multiple contracts or UI states, **L** =
cross-cutting/high-parity work.

## 2. Atomic implementation tasks

### P01 — Capture the executable baseline

- **Complexity**: S
- **Dependencies**: none
- **Reads**: `index.html`, nested Git status, current routes/data/actions/assets
- **Writes**: initial entry in `05-implementation-log.md`; no product behavior change
- **Work**:
  1. confirm the nested worktree is clean before edits;
  2. inventory current script/style blocks and all local asset references;
  3. open the current prototype and capture baseline desktop/compact screenshots;
  4. record current console errors and broken images separately from regressions.
- **Verify**: baseline loads via `file://`; route switching, sorting and current action rail are
  exercised once before refactoring.

### P02 — Add deterministic verification harness

- **Complexity**: M
- **Dependencies**: P01
- **Creates**: `tests/verify-prototype.mjs`
- **Work**: add a dependency-free Node static verifier for registry counts, route/table/action
  separation, locale-key parity, asset existence/dimensions, forbidden icon sources, and protected
  generated-file hashes captured at implementation start.
- **Verify**: run the verifier once against the pre-migration state and record expected failures;
  ensure a deliberately wrong assertion fails before relying on the harness, then restore it.

### P03 — Create classic-script namespace and registries

- **Complexity**: M
- **Dependencies**: P02
- **Creates**: `js/core/namespace.js`, `js/core/registry.js`
- **Work**: implement `window.SimBoxV2026`, duplicate-ID checks, registration/getter APIs and
  immutable copies for routes, tables, screens, locales and icons. No UI wiring yet.
- **Verify**: isolated browser/Node-compatible registry smoke check for registration, duplicate
  rejection and deterministic load order.

### P04 — Extract design tokens and static shell CSS

- **Complexity**: M
- **Dependencies**: P01
- **Creates**: `css/tokens.css`, `css/base.css`, `css/shell.css`
- **Modifies**: `index.html`
- **Work**: move tokens, reset/base typography, header/navigation/page shell styles from the inline
  block without visual redesign; establish `--fg-icon-unit: 16px` and proportional text/gap/row
  tokens.
- **Verify**: compare baseline and post-extraction screenshots at the same viewport; no route or
  layout shift beyond documented approved changes.

### P05 — Extract component CSS

- **Complexity**: M
- **Dependencies**: P04
- **Creates**: `css/toolbar.css`, `css/data-grid.css`, `css/dialogs.css`, `css/responsive.css`
- **Modifies**: `index.html`
- **Work**: move remaining toolbar, grid, overlays/dialogs and breakpoint rules; eliminate obsolete
  inline duplicates only after stylesheet order reproduces current cascade.
- **Verify**: inline application CSS is gone, stylesheet links resolve over `file://`, and static
  browser comparison passes at wide and compact widths.

### P06 — Implement icon registry and vendor resolved Fugue pairs

- **Complexity**: L
- **Dependencies**: P03
- **Creates**: `js/core/icons.js`, `assets/fugue/1x/`, `assets/fugue/2x/`, target
  `FUGUE-WISHLIST.md`, Fugue attribution note
- **Work**:
  1. copy only used upstream filenames from the full catalog;
  2. pair every 16×16 original with its 32×32 rebuild;
  3. implement one 16px-logical renderer using `src`/`srcset`;
  4. mark operator/telemetry images explicitly as `data/identity`;
  5. keep SIM, Readers, KI Search and APDU text-only/pending per wishlist.
- **Verify**: P02 checks every pair and intrinsic dimension; manually inspect a contact sheet and
  browser rendering at DPR 1 and DPR 2. Confirm no 48px tier, emoji, Lucide or invented filename.

### P07 — Implement complete localization runtime

- **Complexity**: L
- **Dependencies**: P03
- **Creates**: `js/core/i18n.js`, `js/locales/en.js`, `th.js`, `ru.js`, `hi.js`, `zh.js`
- **Work**: create the canonical English key set and complete Thai/Russian/Hindi/Chinese peers;
  implement English fallback logging and reactive active-locale lookup. Translate navigation,
  headings, columns, actions, fields, states, validation, confirmations, tooltips and accessible
  names. Identifiers/codes remain raw.
- **Verify**: exact key parity test; browser switch through all five locales; search rendered UI for
  mixed bilingual labels and previous-locale residue.

### P08 — Implement grid state/storage primitives

- **Complexity**: L
- **Dependencies**: P03
- **Creates**: `js/core/storage.js`, `js/core/grid.js`
- **Work**: stable typed sorting; filter normalization; visible/order derivation; schema-safe
  localStorage read/write; reorder; hide/show; Reset; selection-column protection; stable handling
  of nulls, stacked values, numbers and dates.
- **Verify**: execute one focused check at a time for sort, hide, reorder, Reset, corrupt storage,
  unknown/new columns and independent per-table keys.

### P09 — Implement morphing inline action state machine

- **Complexity**: L
- **Dependencies**: P03, P07
- **Creates**: `js/core/actions.js`
- **Work**: implement idle → group → edit → confirm → running → success/failure transitions,
  selection requirements, field validation, danger confirmation, Cancel/Escape and localized
  announcements. Keep entered values after validation failure; never persist execution state.
- **Verify**: focused transition checks plus browser measurement proving toolbar and grid top
  positions remain constant through every state.

### P10 — Extract SIM table definition and complete 43-column parity

- **Complexity**: L
- **Dependencies**: P03, P06–P09
- **Creates**: `js/tables/sim.js`, initial `js/app-data.js`
- **Work**: register all 43 columns in source order, metadata/renderers, right alignment and the full
  active SIM action inventory including `modules/actions.php`; preserve stacked legacy cells and
  source anomalies; exclude commented `save`/`rotki`.
- **Verify**: count 43; all visible after initial load/Reset; headers/cells maintain one-to-one order;
  every active action and parameter is reachable.

### P11 — Extract Lines and Programmer definitions

- **Complexity**: L
- **Dependencies**: P03, P06–P09
- **Creates**: `js/tables/lines.js`, `js/tables/programmer.js`
- **Work**: implement exact 26- and 6-column manifests, separate leading Lines cells, full active
  action sets, and locale-pure Lines/Линии and Programmer/Программатор labels.
- **Verify**: counts 26/6; all columns visible after Reset; legacy actions reachable; no “Свистки”
  copy remains in any locale.

### P12 — Extract Hubs and Readers as independent routes

- **Complexity**: L
- **Dependencies**: P03, P06–P09
- **Creates**: `js/tables/hubs.js`, `js/tables/readers.js`
- **Work**: register separate 9- and 12-column schemas, navigation items, state keys and action
  inventories. Hubs includes `prestart` and delay fields but no KI/APDU; Readers contains PIN,
  `findki` and `apducommandexec` controls.
- **Verify**: counts 9/12; route/title locale purity; independent persisted column orders; action
  separation assertions; no combined Hubs/Readers label.

### P13 — Extract Command sets and full 82-column Plans

- **Complexity**: L
- **Dependencies**: P03, P06–P09
- **Creates**: `js/tables/command-sets.js`, `js/tables/plans.js`
- **Work**: implement the 1-column command-set grid and all seven Plans groups totaling 82 active
  logical columns; map legacy header/source anomalies; exclude commented `ima`; preserve plan save
  and creation controls.
- **Verify**: counts 1/82; group subtotal assertion `5+7+4+23+16+15+12`; all 82 visible after Reset;
  horizontal grid scroll remains internal; sorting/hide/reorder remain responsive.

### P14 — Extract Billing and icon-audit tables

- **Complexity**: M
- **Dependencies**: P03, P06–P08
- **Creates**: `js/tables/billing.js`, `js/tables/icons.js`
- **Work**: implement Billing's exact four cells, keeping raw code/operator in one Direction cell;
  use `money.png`; implement the prototype icon-audit grid with provenance, density files, status
  and usage, including unresolved wishlist rows.
- **Verify**: Billing count 4, numeric right alignment and no broken `may.ico`; audit table detects
  every used UI glyph and flags missing/unresolved entries without broken images.

### P15 — Extract non-grid Processes, Update and Debug screens

- **Complexity**: M
- **Dependencies**: P03, P06, P07, P09
- **Creates**: `js/screens/processes.js`, `js/screens/update.js`, `js/screens/debug.js`
- **Work**: retain only active action/result surfaces for Processes and Update, their complete submit
  names, Update logs and Debug `sysdevs`/`usbdevs` one-column grids. Use
  `application-task.png` for Processes, not heart-like `conn.png`.
- **Verify**: action parity, Debug count 1+1, correct route icons, no invented domain grid.

### P16 — Consolidate representative prototype data

- **Complexity**: L
- **Dependencies**: P10–P15
- **Modifies**: `js/app-data.js`
- **Work**: move remaining monolithic sample records into route-keyed data. Add representative
  values for every active column without inventing new fields or backend semantics. Include normal,
  warning, empty, loading and failure examples required by the approved visual.
- **Verify**: every manifest column resolves against at least one sample row or is explicitly empty
  because the active legacy cell is empty (such as SIM PRI); no `undefined` text renders.

### P17 — Rewire `index.html` and DC component as a thin adapter

- **Complexity**: L
- **Dependencies**: P03–P16
- **Modifies**: `index.html`
- **Work**: load external scripts in deterministic order; replace hardcoded tables/actions/locales
  with registry consumers; keep only DC lifecycle/state-to-view adaptation inline; remove migrated
  data and duplicated definitions. Do not modify `support.js` or `_ds/**`.
- **Verify**: all routes load through `file://`; console is clean; static verifier confirms script
  order and protected-file hashes.

### P18 — Build the final toolbar and Columns UI

- **Complexity**: L
- **Dependencies**: P08, P09, P17
- **Modifies**: `index.html`, `css/toolbar.css`, `css/responsive.css`
- **Work**: implement fixed-height same-row Filter + morphing action rail + Columns control;
  full-label, compact icon-only and internal-scroll modes; inline validation/confirmation/result;
  Columns show/hide/reorder/Reset UI.
- **Verify**: measure constant toolbar height and grid top for idle/edit/error/running/success states;
  exercise all table types at wide, medium and compact widths.

### P19 — Apply final dense-grid typography and accessibility

- **Complexity**: M
- **Dependencies**: P17, P18
- **Modifies**: `css/data-grid.css`, `css/base.css`, relevant renderers
- **Work**: apply monospace stack, tabular numbers, right-aligned technical headers/cells, centered
  icon/control exceptions, icon-proportional row/column spacing, focus states, keyboard header sort,
  accessible icon names/tooltips and live result announcements.
- **Verify**: keyboard-only pass, focus visibility, header/cell alignment, readable dense rows and
  accessible-name inspection.

### P20 — Complete automated parity and regression checks

- **Complexity**: M
- **Dependencies**: P17–P19
- **Modifies**: `tests/verify-prototype.mjs`
- **Work**: turn the initial expected failures into passing assertions for exact table counts,
  actions, routes, locale parity, icon pairs/dimensions, local asset references, default/reset
  visibility, protected runtime hashes and prohibited fallbacks.
- **Verify**: run each test family separately, then the complete verifier; run nested-repository
  `git diff --check`.

### P21 — Browser visual/interaction acceptance sweep

- **Complexity**: L
- **Dependencies**: P20
- **Writes**: screenshots/test evidence and `05-implementation-log.md`
- **Work**:
  1. exercise every navigation route and table type;
  2. test filter, asc/desc sorting, hide/show, reorder, Reset and persistence;
  3. test every action group/state, especially Hubs vs Readers;
  4. switch all five languages;
  5. verify wide/medium/compact layouts and DPR 1/2 icon selection;
  6. inspect empty/loading/error states and browser console.
- **Verify**: compare against `02-visual.md` and all 21 requirements acceptance criteria; log any
  deviation before considering implementation complete.

### P22 — Final cleanup and handoff checkpoint

- **Complexity**: S
- **Dependencies**: P21
- **Modifies**: `05-implementation-log.md`, `_status.md`
- **Work**: remove dead migrated inline definitions and unused generic assets only when their lack
  of references is proven; summarize changed files, deviations, verification evidence and remaining
  wishlist items. Do not delete unrelated logos/content assets.
- **Verify**: nested Git status contains only intended changes; full verifier and `git diff --check`
  pass; protected files remain byte-identical.

## 3. Dependency path

```text
P01 → P02 → P03 ─┬→ P06 → P07 → P08 → P09 ─┬→ P10…P15 → P16 → P17
                 └→ P04 → P05              └─────────────────────┘
P17 → P18 → P19 → P20 → P21 → P22
```

P10–P15 may be implemented sequentially for easier review, but each definition is independently
verifiable and no combined table file is permitted.

## 4. Main risks and controls

| Risk | Control |
|---|---|
| Monolith extraction changes DC runtime timing | classic deterministic script order; keep DC adapter thin; test after every wiring step |
| Plans 82-column drift | exact group subtotals and manifest assertions before UI work |
| Legacy action loss through included files/comments | active-submit matrix includes `modules/actions.php`; exclusions explicitly asserted |
| Browser `file://` incompatibility | no modules/fetch/build/runtime network dependencies |
| Misleading Fugue fallback | full-catalog mapping plus text-only wishlist slots |
| Retina icon becomes 32 CSS pixels | shared 16px logical unit and intrinsic/density browser checks |
| Locale key or mixed-language drift | canonical key-parity test and five-locale rendered sweep |
| User storage breaks after schema change | versioned IDs, unknown-ID filtering and Reset path |
| Overlay/sizing regression | bounding-box checks for toolbar height and grid top in all action states |
| Nested repository confusion | run status/diff/tests explicitly with target repository as working directory |

## 5. Completion criteria

The implementation phase may be marked complete only when P01–P22 are logged as completed, the
automated verifier and browser acceptance sweep pass, every primary legacy column is visible after
Reset, all active actions remain reachable, all resolved generic icons use valid Fugue density
pairs, and only the four documented wishlist semantics remain intentionally iconless.

## 6. Plan approval gate

Status is **APPROVED**. The user approved this plan on 2026-09-01; implementation has started.
