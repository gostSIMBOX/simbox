# Specifications: simbox-web-design-prototype-fix2-uiux

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-09-01
> Requirements: [01-requirements.md](01-requirements.md)
> Visual: [02-visual.md](02-visual.md)

## Overview

Replace fix1's `ActionGroupOverlay` (a `Positioned` panel floating below the header, covering
the table's top rows while open) with an in-row "rail" that expands the toolbar horizontally,
never vertically over the table. Split each table page's header into two stacked rows — a
heading row (title/count/selection chip, unchanged in spirit from fix1) and a new toolbar row
(action rail + filter + Columns + Обновить) — since the interaction-pattern reference
(`design/simbox-design-prototype-v2026-beta1`) keeps these separate, and it frees up the rail's
full width for actions+filter, which is what actually needed the room. Add column show/hide/
reorder to all 4 table pages via new `AppState` fields, consumed by each page's existing
`_cols(st)` pattern — `DenseTable` itself needs no changes.

## Affected Systems

| System | Impact | Notes |
|---|---|---|
| `lib/state/app_state.dart` | Modify | New rail/columns state: `railSubAction`, `columnsOpen` (mutually exclusive with `activeGroup`), `columnOrder`/`hiddenColumns` maps keyed by `AdmPage`, plus accessor/mutator methods |
| `lib/widgets/action_group_bar.dart` | Modify | `ActionGroup` gains `subActions: List<SubAction>` (replaces the single `builder`) + optional `sharedSettings`; delete `ActionGroupOverlay` (no longer positioned/floating); add `ActionRail` (the in-row idle/open-group renderer) |
| `lib/widgets/columns_editor.dart` | Create | Inline column show/hide/reorder chip row, same shape as `ActionRail`'s open-group state |
| `lib/pages/sims_page.dart` | Modify | `TableHeaderBar` splits into `TableHeading` (title/count/chip) + `TableToolbar` (rail+filter+columns+refresh); 5 groups restructured into `subActions` lists; add `_visibleCols(st)` |
| `lib/pages/dongles_page.dart` | Modify | Same restructuring, 3 groups |
| `lib/pages/diagmode_page.dart` | Modify | Same restructuring, 1 group (Rule C — single sub-action) |
| `lib/pages/hubs_page.dart` | Modify | Same restructuring, 1 group (Rule A — flat strip, i.e. a single "sub-action" whose builder is the 3-button strip) |
| `lib/widgets/dense_table.dart` | No change | Already accepts an arbitrary `cols: List<ColDef<T>>` — pages now pre-filter/reorder before passing it in |

## Architecture

### Component Diagram

```
Table page (e.g. SimsPage.build()):
Column
├─ TableHeading(title, count, groups-agnostic selection chip)      <- row 1, unchanged height
├─ SizedBox(height: 8)
├─ TableToolbar(groups, columnsCatalog, search, onSearch)          <- row 2, FIXED height (~44px)
│   └─ LayoutBuilder -> Row
│       ├─ Expanded(SingleChildScrollView(horizontal,              <- the "rail": never grows
│       │     child: ActionRail | ColumnsEditor))                     downward, scrolls sideways
│       └─ SizedBox(filter, compacts under narrow width)
│       └─ IconButton "Columns" (toggles ColumnsEditor)
│       └─ AdmButton "Обновить"
├─ SizedBox(height: 12)
└─ Expanded(DenseTable(cols: _visibleCols(st), rows: ...))          <- unchanged from fix1,
                                                                        never covered/shifted
```

`ActionRail` (inside `action_group_bar.dart`) renders exactly one of:
- **idle**: one pill per `ActionGroup` (unchanged visual from fix1's pills)
- **open group, `subActions.length == 1`** (Rule A/C): that single sub-action's `builder(context)`
  rendered directly — for Rule A this builder itself lays out a flat `Row` of N buttons; for
  Rule C it's the group's one action's fields+Run button, same as fix1's panel content minus the
  `Panel` card chrome (no title bar needed — the pill already labeled it, and the cancel button
  takes over the "how do I get out of this" job the panel header used to imply)
- **open group, `subActions.length > 1`** (Rule B): cancel icon-button, a dropdown of sub-action
  labels, the selected sub-action's `builder(context)`, and (if present) `sharedSettings(context)`

`ColumnsEditor` renders: cancel icon-button, Reset icon-button, then one chip per column in
`AppState.columnOrder[page]` order (checkbox + label + move-left/move-right), matching
`02-visual.md`'s "Column chip" component.

### Data Flow

- `AppState.activeGroup` (from fix1, kept): key of the open group, or `null` for idle. Opening
  a group (`toggleGroup`) now also sets `columnsOpen = false` and resets `railSubAction` to the
  new group's first sub-action's key.
- `AppState.railSubAction` (new, `String?`): key of the currently-selected sub-action within the
  open group (Rule B only — ignored/unused for Rule A/C since there's only one entry).
  Changed by the dropdown's `onChanged`.
- `AppState.columnsOpen` (new, `bool`): toggled by the "Columns" button; opening it sets
  `activeGroup = null` (closes any open group). `goTo()` resets both `activeGroup` and
  `columnsOpen` to their idle values, matching fix1's existing reset-on-navigate behavior.
- `AppState.columnOrder`/`hiddenColumns` (new, `Map<AdmPage, List<String>>` /
  `Map<AdmPage, Set<String>>`): lazily initialized per page from that page's default column-id
  list (the order `_cols(st)` already returns today) the first time it's read. Persists across
  page navigation within the session (NOT reset by `goTo`, unlike `activeGroup`/`columnsOpen` —
  per Requirements' Should-Have, column layout is a per-table user preference, not per-visit
  transient UI state). No `localStorage`/reload persistence (in-memory only, per Requirements'
  Won't-Have on new dependencies).
- Each table page's `build()` computes `final visible = _visibleCols(st, allCols);` — filters
  `allCols` (the existing `_cols(st)` return value, unchanged) by `hiddenColumns[page]` and
  reorders by `columnOrder[page]`, then passes `cols: visible` to `DenseTable` exactly as
  before. Sorting (`sortKey`/`sortDir`) is untouched — it already looks up rows by column *key*,
  independent of the `cols` list's order or membership, so a hidden or reordered column that
  happens to be the active sort key keeps sorting the data correctly (Requirements #9).

## Interfaces

### New/Modified Interfaces

```dart
// lib/widgets/action_group_bar.dart

class SubAction {
  final String key;
  final String label;                       // shown in the Rule-B dropdown; unused for Rule A/C
  final Widget Function(BuildContext) builder;
  const SubAction({required this.key, required this.label, required this.builder});
}

class ActionGroup {
  final String key;
  final String label;                       // pill label
  final String icon;                        // pill icon
  final List<SubAction> subActions;         // length 1 => Rule A/C (direct); length > 1 => Rule B (picker)
  final Widget Function(BuildContext)? sharedSettings; // e.g. queue+delay row; only rendered when subActions.length > 1
  const ActionGroup({
    required this.key, required this.label, required this.icon,
    required this.subActions, this.sharedSettings,
  });
}

/// Idle pills, or the open group's Rule A/B/C content — never the columns editor
/// (that's ColumnsEditor, mutually exclusive, rendered by the caller instead).
class ActionRail extends StatelessWidget {
  final List<ActionGroup> groups;
  const ActionRail({required this.groups, super.key});
}

// lib/widgets/columns_editor.dart (new file)
class ColumnsEditor extends StatelessWidget {
  final AdmPage page;
  final List<ColDef> allColumns;   // full default-order catalog (untyped ColDef reference; see note)
  const ColumnsEditor({required this.page, required this.allColumns, super.key});
}
```

`ColDef<T>` is generic per-table (`ColDef<Sim>`, `ColDef<Dongle>`, ...); `ColumnsEditor` only
needs `key`/`label`/`title` (for the chip text) — it takes `List<ColDef>` with the type
parameter erased at the call site (`allColumns: _cols(st).cast<ColDef>()` or, more simply, a
small `ColumnMeta {key,label,hideable}` projection built by each page to avoid generic-variance
friction; final choice left to Task 3 in 04-plan.md, not load-bearing for behavior).

```dart
// lib/state/app_state.dart additions
class AppState extends ChangeNotifier {
  // ...existing fix1 fields (page, selected, sortKey, sortDir, query, navCompact, activeGroup, ...)

  String? railSubAction;
  bool columnsOpen = false;
  final Map<AdmPage, List<String>> columnOrder = {};
  final Map<AdmPage, Set<String>> hiddenColumns = {};

  void toggleGroup(String key, {List<SubAction>? subActionsOfKey}) {
    if (activeGroup == key) {
      activeGroup = null;
      railSubAction = null;
    } else {
      activeGroup = key;
      columnsOpen = false;
      railSubAction = subActionsOfKey != null && subActionsOfKey.isNotEmpty
          ? subActionsOfKey.first.key
          : null;
    }
    notifyListeners();
  }

  void selectSubAction(String key) { railSubAction = key; notifyListeners(); }

  void toggleColumns() {
    columnsOpen = !columnsOpen;
    if (columnsOpen) activeGroup = null;
    notifyListeners();
  }

  List<String> columnOrderFor(AdmPage page, List<String> defaultIds) =>
      columnOrder.putIfAbsent(page, () => List.of(defaultIds));

  Set<String> hiddenColumnsFor(AdmPage page) => hiddenColumns.putIfAbsent(page, () => <String>{});

  void toggleColumnHidden(AdmPage page, String colId, List<String> defaultIds) {
    final hidden = hiddenColumnsFor(page);
    hidden.contains(colId) ? hidden.remove(colId) : hidden.add(colId);
    notifyListeners();
  }

  void moveColumn(AdmPage page, String colId, int direction, List<String> defaultIds) {
    final order = columnOrderFor(page, defaultIds);
    final i = order.indexOf(colId), n = i + direction;
    if (n < 0 || n >= order.length) return;
    order.removeAt(i);
    order.insert(n, colId);
    notifyListeners();
  }

  void resetColumns(AdmPage page, List<String> defaultIds) {
    columnOrder[page] = List.of(defaultIds);
    hiddenColumns[page] = <String>{};
    notifyListeners();
  }

  // goTo() gains: activeGroup = null; railSubAction = null; columnsOpen = false;
  // (activeGroup/columnsOpen reset already existed/is extended; columnOrder/hiddenColumns NOT reset)
}
```

`toggleGroup`'s signature grows a parameter compared to fix1 (needs the new group's sub-action
list to seed `railSubAction`) — call sites already have the `ActionGroup` in hand when building
pills, so this is a mechanical update, not a design risk.

### Modified: `TableHeaderBar` → `TableHeading` + `TableToolbar`

fix1's single `TableHeaderBar` (title+count+chip+pills+search+refresh in one `Row`) splits into
two widgets so the heading can stay a normal-height text row while the toolbar row is the fixed-
height, horizontally-scrolling one:

```dart
class TableHeading extends StatelessWidget {
  final String title;
  final int count;
  const TableHeading({required this.title, required this.count, super.key});
  // renders: Row(title, count, if selected.isNotEmpty: chip) — same visual as fix1's left cluster
}

class TableToolbar extends StatelessWidget {
  final List<ActionGroup> groups;
  final TextEditingController search;
  final ValueChanged<String> onSearch;
  final AdmPage page;
  final List<String> defaultColumnIds;
  const TableToolbar({ ...required fields..., super.key });
  // LayoutBuilder decides icon-only vs labeled based on available width (see Behavior below)
}
```

## Data Models

### Per-page `ActionGroup` inventories (unchanged action set from fix1 — see Requirements #10)

**Sims** (`lib/pages/sims_page.dart`) — 5 groups:

| Group key | Rule | Sub-actions |
|---|---|---|
| `power` | B | `on` (ВКЛ, no fields), `off` (ВЫКЛ, no fields), `pause` (Пауза, no fields), `work` (В работу, no fields) — `sharedSettings`: очередь checkbox + delay/rnd fields |
| `simple` | B | `ussd` (field: command), `sms` (fields: to, message), `call` (field: number, **two** run buttons Call60/CallSpeak) |
| `smart` | A | one sub-action whose builder renders the existing `smartActions` grid as a flat wrapping button strip (no fields on any of them) |
| `plans` | B | `setgroup` (field: group), `setplan` (field: plan dropdown, **two** run buttons без/с копирования), `restore` (no fields), `clearautoblock` (no fields) |
| `export` | A | one sub-action rendering the 3 export buttons as a flat strip |

**Dongles** (`lib/pages/dongles_page.dart`) — 3 groups:

| Group key | Rule | Sub-actions |
|---|---|---|
| `dact` | A | one sub-action rendering `dongleActions` as a flat strip |
| `pin` | B | `pin` (field: PIN), `cardlock` (no fields), `u2diag` (no fields) |
| `modes` | B | `gsm` (no fields), `wcdma` (no fields), `at` (field: command) |

**Diagmode** (`lib/pages/diagmode_page.dart`) — 1 group:

| Group key | Rule | Sub-actions |
|---|---|---|
| `fw` | C | one sub-action (Отправить в diagmode, no fields) — `sharedSettings`: Автообновление checkbox |

**Hubs** (`lib/pages/hubs_page.dart`) — 1 group:

| Group key | Rule | Sub-actions |
|---|---|---|
| `hubpwr` | A | one sub-action rendering ВКЛ/ВЫКЛ/РЕСТАРТ as a flat strip |

Every button's `onPressed` body (the exact `st.runOnSelection(...)`/`st.runOnDongles(...)`/
`st.push(...)` call, command string, toast text, icon) is moved **verbatim** from fix1's
existing `Panel` children into the corresponding `SubAction.builder` — Requirements #5 is the
hard constraint here (layout/reveal changes only, zero behavior drift).

### Column catalogs (per page, from the existing `_cols(st)` — unchanged column defs)

No new column data; `_visibleCols` only filters/reorders the existing `List<ColDef<T>>` each
page already builds. Default order = the order `_cols(st)` already returns today (becomes the
`defaultColumnIds` passed to `AppState.columnOrderFor`/`resetColumns`).

### Schema Changes

None (in-memory `AppState` fields only, no persisted storage).

## Behavior Specifications

### Happy Path (Rule B — "Простые" on Sims)

1. Idle rail shows 5 pills. User clicks "Простые".
2. `toggleGroup('simple', subActionsOfKey: simpleGroup.subActions)` → `activeGroup='simple'`,
   `railSubAction='ussd'` (first sub-action), `columnsOpen=false`.
3. Rail renders: cancel button, dropdown defaulted to "USSD", the `ussd` sub-action's field
   (command, default `*100#`) + "Отправить" button. Table underneath is untouched.
4. User picks "SMS" in the dropdown → `selectSubAction('sms')` → rail re-renders showing the
   `sms` sub-action's two fields + "SMS" button, USSD's field is gone (not just hidden).
5. User clicks "SMS" run button → identical `st.runOnSelection(...)` call fix1 already had for
   the SMS button; toast + log entry fire exactly as before.
6. User presses Escape (or clicks cancel, or clicks the "Простые" pill again) → `activeGroup`
   and `railSubAction` reset to `null`; rail returns to the 5 idle pills.

### Happy Path (Rule A — "Действия хитрые" on Sims)

1. User clicks "Действия хитрые" pill → `subActions.length == 1`, so the rail renders that one
   sub-action's builder directly: a wrapping/horizontally-scrolling row of every `smartActions`
   button, each independently clickable with no dropdown step.
2. Clicking any button fires its existing `st.runOnSelection(...)` call unchanged.

### Happy Path (Columns editor)

1. User clicks the "Columns" icon-button → `toggleColumns()` → `columnsOpen=true`,
   `activeGroup=null`.
2. Rail is replaced by `ColumnsEditor`: cancel, Reset, then one chip per column in
   `columnOrderFor(page, defaults)` order.
3. User unchecks "IMEI" → `toggleColumnHidden(page, 'imei', defaults)` → `DenseTable` re-renders
   without the IMEI column (header + every row cell for it disappear together).
4. User clicks the move-right arrow on "balance" → `moveColumn(page, 'balance', 1, defaults)` →
   header and every row's `balance` cell shift one position right, in sync.
5. User clicks "Reset" → `resetColumns(page, defaults)` → order and hidden set both restored;
   chips re-render in default order, all checked.
6. User clicks Columns again (or cancel, or Escape) → `columnsOpen=false`, rail returns to idle
   pills. Column order/visibility persists (not reset) — only the *editor's visibility* closes.

### Edge Cases

| Case | Trigger | Expected Behavior |
|---|---|---|
| Open a group while Columns editor is open | Click a pill while `columnsOpen == true` | `toggleGroup` sets `activeGroup` and leaves `columnsOpen` — need explicit `columnsOpen = false` inside `toggleGroup` too (mirrors `toggleColumns` closing `activeGroup`), so pills remain clickable as an implicit "close columns, open this group" action, matching 02-visual.md's Flow diagram |
| Sort key is a currently-hidden column | User hides "IMEI" while it's the active sort column | Sorting keeps working on the underlying data (unaffected — `sortRows` looks up by key, not by visible-columns list); the sort arrow simply isn't visible in the header since that column's header cell doesn't render. No error, no reset of `sortKey`. |
| Reorder the currently-sorted column | Move "balance" (active sort key) to a new position | Sort arrow moves with it (rendered per-column in the header, following `cols` order) — no special handling needed since header rendering already reads `sortKey`/`sortDir` per column at render time |
| All columns hidden except non-hideable | Hypothetically uncheck every hideable column | `select` column (always rendered by `DenseTable`, not part of `cols`) still shows; `cols` becomes empty — table renders a header with just the checkbox column and rows with just checkboxes. Not prevented (no "must keep ≥1 column" rule specified), but noted as an accepted degenerate state rather than crash risk — verified during manual testing. |
| Narrow window, group open, dropdown showing | Window shrinks below the icon-only breakpoint while a Rule-B group's picker is open | Dropdown and Run button also drop to icon-only per Requirements #6 / 02-visual.md's narrow-window Rule-B mockup; cancel button stays icon-only (it always was) |
| `railSubAction` stale after group toggled closed-then-reopened quickly | Rapid double-click on the same pill | Second click of `toggleGroup` on the same key closes it (existing fix1 toggle semantics preserved: same-key click = close) — `railSubAction` is cleared alongside `activeGroup`, so reopening later always re-defaults to the first sub-action, no stale selection carried over |

### Error Handling

Not applicable — no network/error states introduced (same as fix1).

## Dependencies

### Requires

- fix1's shell (sidebar, sticky `DenseTable`, `AppState`/`AppScope`) — already implemented and
  committed (`709d543` on the nested `design/simbox-web-design-prototype-v2026` repo).

### Blocks

- None.

## Integration Points

### Internal Systems

- `lib/design/tokens.dart` — reused as-is for the rail/pill/chip styling (no new tokens), same
  as fix1.
- `lib/widgets/panel.dart` (`AdmButton`, `AdmField`, `AdmCheck`) — reused unchanged inside
  `SubAction.builder`s; only the *container* around them changes (no more `Panel` card chrome
  inside the rail — the rail itself is the container now, matching beta1's chrome-less inline
  fields).

## Testing Strategy

No automated test suite (unchanged from fix1). Manual verification via `flutter analyze` +
`flutter build web` + a driven Chrome session, per fix1's precedent.

### Manual Verification

- [ ] Every group on all 4 pages opens correctly per its assigned Rule (A/B/C) and matches
      02-visual.md's mockups.
- [ ] For each Rule-B group, switching the dropdown swaps the visible fields without leaving
      stale widgets from the previous selection.
- [ ] Every button inside every sub-action fires the same toast/log-entry it did in fix1 (spot
      check at least one button per group, 10 groups total across 4 pages).
- [ ] Opening a group never moves or covers the table (visually confirm rows stay in place).
- [ ] Opening Columns closes an open group and vice versa; only one of {idle, group, columns}
      shows at a time.
- [ ] Column hide/show, reorder, and Reset work correctly on at least the Sims table (most
      columns) and one other table (fewer columns, confirms the shared code path generalizes).
- [ ] Sorting still works after hiding/reordering columns, including sorting by a since-hidden
      column's key (edge case above).
- [ ] Narrowing the browser window drops action-pill/dropdown/run-button labels to icon-only
      before anything wraps to a second line; filter narrows; selection chip hides if still
      tight.
- [ ] Escape key closes an open group or the columns editor from anywhere on the page.

## Migration / Rollout

Not applicable — single prototype app, in-memory state only, no user data to migrate.

## Open Design Questions

- [ ] `ColumnsEditor`'s `allColumns: List<ColDef>` typing — resolve the generic-variance
      approach (raw `List<ColDef>` cast vs. a small untyped `ColumnMeta` projection) during
      implementation; both are mechanical, neither changes behavior.
- [ ] Exact icon-only width breakpoint for `TableToolbar`'s `LayoutBuilder` — proposing to reuse
      beta1's ~1180px as a starting constant, tunable after visually testing at a few widths.

---

## Approval

- [ ] Reviewed by: Anton Dodonov
- [ ] Approved on:
- [ ] Notes:
