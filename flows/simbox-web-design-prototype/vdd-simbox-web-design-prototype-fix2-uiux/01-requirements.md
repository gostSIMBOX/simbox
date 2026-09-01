# Requirements: simbox-web-design-prototype-fix2-uiux

> Version: 1.0
> Status: APPROVED
> Last Updated: 2026-09-01

## Problem Statement

Fix 1 (`vdd-simbox-web-design-prototype-fix1-uiux`, implemented) moved the SIM-box admin
prototype's per-table actions from a below-the-table `Wrap` of always-visible panels into
toggle pills in the table header bar, opening a floating overlay panel positioned absolutely
below the header. That solved "actions were buried a scroll away," but the overlay still visibly
**covers the top rows of the table** while open, and each pill's panel shows an entire former
2015-panel's worth of fields at once (e.g. "Действия простые" shows USSD + SMS + Call all
simultaneously) — not especially compact.

`design/simbox-design-prototype-v2026-beta1` (a separate, further-along prototype effort in this
repo) already solves this more elegantly: its `.toolbar`/`.action-rail` renders action groups as
pills; clicking one **replaces the pill row in place** with an inline editor (a dropdown to pick
the specific action within that group, that action's fields, and a Run button) — never growing
downward, never covering the table, never shifting it. The same row also hosts the filter input
and a "columns" toggle that swaps the rail for an inline column-management editor (show/hide,
reorder, all via the same row). This flow ports that interaction pattern — not beta1's specific
(larger) action inventory, not its visual styling — into the Flutter prototype, and adds column
show/hide/reordering to `DenseTable` (sorting already exists from fix1).

**Decision already made** (see `_status.md` Context Notes): action groups that contain more than
one distinct legacy action (e.g. "Простые" = USSD/SMS/Звонок) switch from "all visible at once"
to beta1's model — pick one action from a dropdown, only its fields + Run button show. This is a
deliberate interaction change; no action, field, or button is removed, only how many are visible
at a time changes.

## User Stories

### Primary

**As an** operator working the Sims table (the one with ~30 columns and 5 action groups)
**I want** an action group's controls to expand in the same toolbar row, never covering or
pushing the table
**So that** I keep visual context of the rows I'm about to act on while filling in an action's
fields

**As an** operator on a narrow window/laptop
**I want** the action rail and filter to still fit in one row, falling back to icon-only pills
when space is tight
**So that** the toolbar never wraps to a second line or forces horizontal page scrolling

**As an** operator dealing with the dense Sims table's ~30 columns
**I want** to hide columns I don't care about and reorder the ones I keep
**So that** I can focus the table on what matters for my current task without horizontal
scrolling past irrelevant columns

### Secondary

**As an** operator who opened an action group by mistake
**I want** a clear, obvious way to back out (cancel button and/or Escape key) without submitting
anything
**So that** I don't have to hunt for how to close it

## Acceptance Criteria

### Must Have

1. **Given** any of the 4 table pages (Sims, Dongles, Diagmode, Hubs)
   **When** the page renders
   **Then** the toolbar row contains, left to right: page title + row count (+ selection chip
   when rows are selected) + one pill per action group; and, right-aligned in the same row:
   filter input + a "Columns" icon-button + the existing "Обновить" button. All of this lives in
   one row — no separate `Wrap` of full-size action panels below the table anymore.

2. **Given** the toolbar row's action-group pills
   **When** the user clicks a pill for a group containing exactly one legacy action with no
   input fields (e.g. Hubs' "Питание порта" is 3 zero-field actions — see rule below)
   **Then** ... — see the two sub-rules below, which together replace a single blanket rule:

   **Rule A — all-zero-field groups** (every action in the group takes no input, e.g. "Действия
   хитрые", "Действия со свистками", "Экспорт / Импорт", "Питание порта"): clicking the pill
   expands, in place, a flat one-click button strip — every action button visible and directly
   clickable, no intermediate selection step (there's no field to protect space for).

   **Rule B — any-fielded groups** (at least one action in the group needs input, e.g.
   "Передатчик и статус", "Действия простые", "Группы и планы", "PIN и разблокировка", "Режимы
   и AT-команда"): clicking the pill expands, in place, the beta1-style editor — a dropdown to
   pick which action in the group, that action's field(s), and a Run button; only the selected
   action's fields are shown. A group-level "cancel"/back icon-button returns to the idle pill
   row. Group-level persistent settings that apply to every action in the group (Передатчик's
   "в очередь" checkbox + delay/random fields; Перепрошивка's "Автообновление" checkbox) render
   alongside the dropdown regardless of which action is selected, not as if they belonged to one
   specific action.

   **Rule C — single-action groups** (exactly one action, fielded or not, e.g. "Перепрошивка"):
   clicking the pill expands that one action's controls directly — no dropdown needed since
   there's nothing to choose between.

3. **Given** an action group is expanded (Rule A, B, or C)
   **When** the user looks at the table below
   **Then** the table has not moved and is not covered — the toolbar row grows to fit its
   content horizontally (scrolling sideways within the row if needed, matching beta1's
   `.action-rail { overflow-x: auto }`), never downward, and the table's `Expanded` region keeps
   its position and size.

4. **Given** an expanded action-group editor (Rule B or C)
   **When** the user presses Escape, or clicks the cancel/back icon-button, or clicks the same
   pill again
   **Then** the rail collapses back to the idle pill row with no side effects (no action fired,
   any in-progress field values discarded).

5. **Given** an action inside an expanded editor that has a Run button (Rule B/C) or is one of a
   flat button strip (Rule A)
   **When** the user clicks it
   **Then** it fires the exact same underlying call (`runOnSelection`/`runOnDongles`/`push`,
   same command string, same toast, same log entry) that it did in fix1 — this flow changes
   *layout and reveal granularity only*, never the command/behavior behind a button.

6. **Given** the toolbar row's available width shrinks (narrow browser window)
   **When** the action pills + filter + Columns + Обновить no longer fit comfortably in one row
   **Then** the action pills (idle and expanded states) drop their text labels and show icons
   only first; the filter input narrows; the selection-count chip hides if still too tight —
   the row must never wrap to a second line or force the whole toolbar into horizontal scroll
   (only the action-rail sub-region scrolls horizontally, per #3, as a last resort within an
   already-icon-only row).

7. **Given** any of the 4 table pages
   **When** the user clicks the new "Columns" icon-button in the toolbar
   **Then** the action-rail region (wherever it currently is — idle pills or an open group) is
   replaced by an inline column-management editor: one chip per column (in current order),
   each with a checkbox (hide/show — disabled for columns marked non-hideable, e.g. the row
   `select` column) and move-left/move-right buttons to reorder; plus a "Reset" control back to
   the table's default column set/order, and the same cancel/back affordance as action groups.
   Opening Columns closes any open action group and vice versa — only one of {idle pills, an
   open action group, the columns editor} occupies the rail at a time.

8. **Given** the column-management editor
   **When** the user toggles a column's checkbox or moves it left/right
   **Then** `DenseTable`'s rendered columns update immediately to match (hidden columns
   disappear from the header and every row; reordered columns move together, header+cells in
   sync, exactly as today for the always-visible columns).

9. **Given** sorting (already implemented in fix1 — click a column header to sort, click again
   to reverse)
   **When** this flow's column-visibility/order changes land
   **Then** sorting keeps working unchanged, including for columns that have been reordered or
   are currently hidden-then-reshown (sort state is independent of column order/visibility).

10. **Given** the 4 table pages' current action inventories (documented in fix1's
    `03-specifications.md`/`05-implementation-log.md`: Sims 5 groups, Dongles 3, Diagmode 1,
    Hubs 1 — same underlying buttons/fields as legacy `legacy/simbox-desktop-v2014/www/simbox`)
    **When** this flow is complete
    **Then** the exact same set of actions/fields exists — none added, none removed. Only
    beta1's *interaction pattern* (rail/dropdown/columns-editor, all inline in one row) is
    adopted, not beta1's own broader action list (`changeimei`, `supersim_new`, `get_balance`,
    etc. are beta1-specific and out of scope here).

### Should Have

- Column order/visibility persists across page navigation within the same session (so switching
  from Sims to Dongles and back doesn't reset Sims' customized columns) — in-memory in
  `AppState` is sufficient; browser-reload persistence (e.g. via `localStorage`, as beta1 does)
  is a nice-to-have, not required, and should not pull in a new package dependency to achieve.
- The "Reset" control in the columns editor restores both order and visibility to each table's
  original default (the column list/order as defined in each page's `_cols(st)` today).

### Won't Have (This Iteration)

- No new actions, fields, or columns beyond what fix1 already has — this is a pure UX/interaction
  refactor of the toolbar and table column controls.
- No adoption of beta1's own action inventory, its CSS/visual styling, or its vanilla-JS
  architecture — only the *interaction pattern* is ported; visual language stays governed by
  `design/simbox-design-prototype-v2026-dc` and the existing `lib/design/tokens.dart`.
- No multi-column sort (still single-column, click-to-cycle, as today).
- No drag-and-drop column reordering — move-left/move-right buttons only (matches beta1, avoids
  a drag-and-drop dependency for a prototype).
- No changes to the sidebar, logo, or `CommandLog` — fix1's shell stays as-is.

## Constraints

- **Technical**: same Flutter web prototype (`design/simbox-web-design-prototype-v2026`), same
  `AppState`/`AppScope` pattern; extend, don't replace.
- **Design source of truth for visuals**: `design/simbox-design-prototype-v2026-dc` (tokens,
  colors, radii, shadows) — beta1 is an *interaction-pattern* reference only, not a visual one
  (its CSS is a different, unapproved visual language).
- **Logic source of truth**: `legacy/simbox-desktop-v2014/www/simbox` (unchanged from fix1) —
  still the inventory of what actions/fields must exist; this flow doesn't touch that inventory.
- **Scope**: builds on top of fix1's already-implemented shell (sidebar, sticky header, sim
  status bar) — this flow only touches the table pages' toolbar/header-bar and `DenseTable`'s
  column handling.
- **No new dependencies**: implement with the existing `flutter`/`flutter_lints` dependency set
  (matches fix1's precedent of avoiding `package:collection` for a one-off helper).

## Open Questions

- [x] ~~Group-granularity for the rail (all-at-once vs. beta1's pick-one-via-dropdown)~~ —
  resolved via `AskUserQuestion`: beta1-style (list → one action), see Acceptance Criteria #2.
- [x] ~~All-zero-field-groups-get-a-flat-strip / any-fielded-groups-get-a-dropdown split~~ —
  resolved via `AskUserQuestion`: confirmed, Rules A/B/C above stand as specified.
- [x] ~~Which tables get column management~~ — resolved: **all 4** (Sims, Dongles, Diagmode,
  Hubs) via the same shared `DenseTable`.
- [ ] Should the "select" checkbox column and any other structurally-required column be excluded
  from the reorder list entirely (fixed at position 0), or merely non-hideable but still
  movable? Proposing: fixed at position 0, not shown in the reorder list at all (matches beta1's
  `hideable:false` treatment, extended to "not reorderable" since it's the row-selection
  affordance, not table data).

## References

- `design/simbox-design-prototype-v2026-beta1/js/app.js`, `js/core/grid.js`,
  `js/core/actions.js`, `js/core/storage.js`, `css/toolbar.css`, `css/data-grid.css`,
  `css/responsive.css` — interaction-pattern reference (rail, columns editor, responsive
  breakpoints, sort/order/hidden state shape).
- `flows/simbox-web-design-prototype/vdd-simbox-web-design-prototype-fix1-uiux/` — prior flow;
  this one builds directly on its shell and its documented action inventory per table.
- `legacy/simbox-desktop-v2014/www/simbox` — legacy logic/inventory source of truth (unchanged).
- `design/simbox-design-prototype-v2026-dc` — visual source of truth (unchanged).

---

## Approval

- [x] Reviewed by: Anton Dodonov
- [x] Approved on: 2026-09-01
- [x] Notes: Both open questions resolved via AskUserQuestion (column management → all 4
  tables; Rule A/B/C split confirmed as proposed). Remaining minor default (select column fixed
  at position 0, excluded from the reorder chip list) proceeds as proposed, not separately
  re-confirmed.
