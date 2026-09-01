# Implementation Plan: simbox-web-design-prototype-fix2-uiux

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-09-01
> Specifications: [03-specifications.md](03-specifications.md)

## Summary

Five phases: (1) extend `AppState` with rail/columns state, (2) rebuild
`action_group_bar.dart`'s model + `ActionRail` widget and delete the old floating overlay,
(3) build `ColumnsEditor`, (4) split `TableHeaderBar` into `TableHeading`/`TableToolbar` and
rewire all 4 table pages' groups into the new `SubAction` shape + wire column filtering, (5)
verify. Phases are listed in dependency order; within Phase 4 the 4 pages are independent of
each other and can be done in any order.

## Task Breakdown

### Phase 1: State

#### Task 1.1: Extend `AppState`
- **Description**: Add `railSubAction`, `columnsOpen`, `columnOrder`, `hiddenColumns` fields and
  the `toggleGroup` (signature change), `selectSubAction`, `toggleColumns`, `columnOrderFor`,
  `hiddenColumnsFor`, `toggleColumnHidden`, `moveColumn`, `resetColumns` methods per
  03-specifications.md's Interfaces section. Update `goTo()` to also reset `railSubAction` and
  `columnsOpen` (not `columnOrder`/`hiddenColumns` — those persist across navigation).
  `toggleGroup` also clears `columnsOpen` when opening a group (Edge Case in Specifications).
- **Files**: `lib/state/app_state.dart` - Modify
- **Dependencies**: None
- **Verification**: Compiles; existing fix1 call sites to `toggleGroup(key)` will need updating
  in Phase 4 (this task alone breaks the build until then — acceptable, matches fix1's
  additive-first-then-wire-up pattern only where unavoidable; keep this and Task 4.x in the same
  work session).
- **Complexity**: Low

### Phase 2: Action rail

#### Task 2.1: Rebuild `action_group_bar.dart`
- **Description**: Replace `ActionGroup`'s single `builder` with `subActions: List<SubAction>` +
  optional `sharedSettings`; add the `SubAction` class; delete `ActionGroupOverlay` entirely;
  add `ActionRail` (idle pills / Rule A·C direct content / Rule B dropdown+fields+shared
  settings, per 03-specifications.md's Architecture). Keep `ActionGroupPill`'s visuals unchanged
  from fix1 (outline/▼ closed, brand-tint/▲ open). Rail's horizontal scroll:
  `SingleChildScrollView(scrollDirection: horizontal)` wrapping the pill row / open-group row /
  cancel+dropdown+fields row, fixed row height (no `Wrap`, no vertical growth).
- **Files**: `lib/widgets/action_group_bar.dart` - Modify (large rewrite)
- **Dependencies**: Task 1.1
- **Verification**: Deferred to Phase 4 integration (no page wires this in yet).
- **Complexity**: High (the dropdown-swaps-fields-in-place mechanism plus fixed-height
  horizontal-scroll layout is the trickiest layout work in this flow).

### Phase 3: Columns editor

#### Task 3.1: Build `ColumnsEditor`
- **Description**: New widget per 03-specifications.md — cancel + Reset icon-buttons, then a
  horizontally-scrolling row of column chips (checkbox + label + move-left/move-right, disabled
  arrows at the ends, disabled/non-interactive checkbox for non-hideable columns — though in
  practice the `select` column is never part of `cols` at all, so no chip needs
  `hideable:false` handling unless a future column is marked non-hideable). Resolve the generic
  `List<ColDef>` typing (Open Design Question) — simplest: accept
  `List<({String key, String label})>` records instead of raw `ColDef<T>`, built by each page
  via `.map((c) => (key: c.key, label: c.label))` — avoids generic variance entirely with no
  behavior cost.
- **Files**: `lib/widgets/columns_editor.dart` - Create
- **Dependencies**: Task 1.1
- **Verification**: Deferred to Phase 4 integration.
- **Complexity**: Medium

### Phase 4: Wire up the 4 table pages

#### Task 4.1: Split `TableHeaderBar` → `TableHeading` + `TableToolbar` (in `sims_page.dart`)
- **Description**: `TableHeading` keeps title/count/selection-chip (fix1's left cluster,
  unchanged visuals). `TableToolbar` is new: `LayoutBuilder` + `Row` of
  `Expanded(ActionRail-or-ColumnsEditor)` + filter `TextField` + "Columns" `IconButton` +
  "Обновить" `AdmButton`, with the icon-only breakpoint logic (~1180px, per Specifications'
  Open Design Question — implement as a local constant, easy to retune). Both new widgets are
  defined where `TableHeaderBar` used to be (bottom of `sims_page.dart`, imported by the other
  3 pages exactly as `TableHeaderBar` was).
- **Files**: `lib/pages/sims_page.dart` - Modify (widget definitions only in this task; page
  `build()` bodies updated in 4.2–4.5)
- **Dependencies**: Task 2.1, Task 3.1
- **Verification**: N/A standalone — verified per-page in 4.2–4.5.
- **Complexity**: Medium

#### Task 4.2: Rewire Sims page (5 groups)
- **Description**: Replace the 5 `ActionGroup(..., builder: (_) => _panelMethod(st))` entries
  with the `subActions` shapes from 03-specifications.md's Data Models table: `power` (4
  no-field sub-actions + sharedSettings), `simple` (3 sub-actions: ussd/sms/call — call has 2
  run buttons), `smart` (1 sub-action = flat strip), `plans` (4 sub-actions: setgroup/setplan
  [2 run buttons]/restore/clearautoblock), `export` (1 sub-action = flat strip). Every
  `AdmButton.onPressed` body is moved verbatim from the current `_transmitter`/`_simpleActions`/
  `_smartActions`/`_groupsAndPlans`/`_exports` methods — split each method's internal `Column`
  of multiple field-rows into one `SubAction.builder` per row/action instead of one `Panel` for
  the whole group. Add `_visibleCols(AppState st)` computing
  `AppState.columnOrderFor`/`hiddenColumnsFor`-filtered columns from the existing `_cols(st)`;
  pass to `DenseTable`. Update `build()` to render `TableHeading` + `TableToolbar` +
  `Expanded(DenseTable(...))` (no more `Stack`/`Positioned` overlay — the rail is now inline in
  `TableToolbar`, so the table area goes back to a plain `Expanded(DenseTable(...))`, no `Stack`
  needed).
- **Files**: `lib/pages/sims_page.dart` - Modify
- **Dependencies**: Task 4.1
- **Verification**: Manual — all 5 groups open per their Rule, every button still fires its
  fix1-identical call, columns hide/reorder/reset, sort still works.
- **Complexity**: High (most groups, most sub-actions to carve apart correctly).

#### Task 4.3: Rewire Dongles page (3 groups)
- **Description**: Same pattern — `dact` (1 sub-action, flat strip), `pin` (3 sub-actions:
  pin/cardlock/u2diag), `modes` (3 sub-actions: gsm/wcdma/at). `_visibleCols` +
  `TableHeading`/`TableToolbar` wiring same as 4.2.
- **Files**: `lib/pages/dongles_page.dart` - Modify
- **Dependencies**: Task 4.1
- **Verification**: Same checklist as 4.2, scoped to Dongles' 3 groups + its columns.
- **Complexity**: Medium

#### Task 4.4: Rewire Diagmode page (1 group, Rule C)
- **Description**: `fw` group becomes 1 sub-action (Отправить в diagmode) + `sharedSettings`
  (Автообновление checkbox) — no dropdown rendered since `subActions.length == 1`.
  `_visibleCols` + heading/toolbar wiring.
- **Files**: `lib/pages/diagmode_page.dart` - Modify
- **Dependencies**: Task 4.1
- **Verification**: Same checklist, scoped to Diagmode.
- **Complexity**: Low

#### Task 4.5: Rewire Hubs page (1 group, Rule A)
- **Description**: `hubpwr` group becomes 1 sub-action rendering ВКЛ/ВЫКЛ/РЕСТАРТ as a flat
  strip. `_visibleCols` + heading/toolbar wiring.
- **Files**: `lib/pages/hubs_page.dart` - Modify
- **Dependencies**: Task 4.1
- **Verification**: Same checklist, scoped to Hubs.
- **Complexity**: Low

### Phase 5: Verification

#### Task 5.1: Full verification pass
- **Description**: `flutter analyze` (0 new errors/warnings beyond fix1's 3 pre-existing style
  infos); `flutter build web`; drive the built app in Chrome through 03-specifications.md's
  Manual Verification checklist in full (all 4 pages × all groups × Rule-appropriate behavior,
  columns editor on ≥2 tables, sort-after-hide/reorder, responsive breakpoint, Escape key).
- **Files**: None (verification only)
- **Dependencies**: Tasks 4.2–4.5
- **Verification**: This *is* the verification task.
- **Complexity**: Medium (breadth, not difficulty)

## Dependency Graph

```
1.1 ─┬─→ 2.1 ─┬─→ 4.1 ─┬─→ 4.2 ─┐
     │        │        ├─→ 4.3 ─┤
     └─→ 3.1 ─┘        ├─→ 4.4 ─┼─→ 5.1
                        └─→ 4.5 ─┘
```

## File Change Summary

| File | Action | Reason |
|---|---|---|
| `lib/state/app_state.dart` | Modify | Rail sub-action + columns state/methods |
| `lib/widgets/action_group_bar.dart` | Modify | `SubAction`, reshaped `ActionGroup`, new `ActionRail`, delete `ActionGroupOverlay` |
| `lib/widgets/columns_editor.dart` | Create | Inline column show/hide/reorder |
| `lib/pages/sims_page.dart` | Modify | `TableHeading`/`TableToolbar` (replacing `TableHeaderBar`), 5 groups restructured, `_visibleCols` |
| `lib/pages/dongles_page.dart` | Modify | 3 groups restructured, `_visibleCols` |
| `lib/pages/diagmode_page.dart` | Modify | 1 group restructured, `_visibleCols` |
| `lib/pages/hubs_page.dart` | Modify | 1 group restructured, `_visibleCols` |

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Splitting a group's fields across multiple `SubAction`s accidentally drops or mistypes an `onPressed` body | Medium | High (silently breaks a legacy action) | Move code verbatim (cut/paste per sub-action, not retype); Manual Verification spot-checks a button per group across all 10 groups |
| Fixed-height horizontal-scroll rail overflows awkwardly for a wide Rule-B group (e.g. "Простые"'s SMS fields: to+message+button) | Medium | Low | `SingleChildScrollView(horizontal)` is the explicit fallback per Requirements #3/#6; verify visually, not just by code review |
| `LayoutBuilder` breakpoint logic picks a bad threshold, causing premature or late icon-only collapse | Low | Low | Constant is a single named value, trivially retunable; verify at 2-3 window widths during Task 5.1 |
| Column reorder/hide state keyed by `AdmPage` collides or leaks between pages | Low | Medium | `Map<AdmPage, ...>` keys are the enum itself — no string-typo risk, compiler-checked |
| Removing `Stack`/`Positioned` from table pages changes some other unrelated layout assumption | Low | Low | The `Stack` was fix1-only scaffolding for the overlay; removing it and going back to a plain `Expanded(DenseTable(...))` is a simplification, not a new risk surface |

## Rollback Strategy

Same as fix1: single working tree, no external consumers. `git diff`/`git checkout` on the
affected files, or revert the eventual commit(s), if needed. fix1's own commit (`709d543`) is
untouched by this plan and remains a safe rollback point.

## Checkpoints

After Phase 2, Phase 3, and each page in Phase 4:

- [ ] `flutter analyze` shows no new errors.
- [ ] `flutter build web` succeeds.
- [ ] Behavior matches the relevant Acceptance Criteria in 01-requirements.md and the ASCII
      states in 02-visual.md.

## Open Implementation Questions

- [ ] Exact `ColumnsEditor` typing resolution (record type vs. raw generic cast) — decided in
      Task 3.1's description above (records), flagged here only because Specifications left it
      open; no further approval needed, it's a mechanical implementation detail.

---

## Approval

- [ ] Reviewed by: Anton Dodonov
- [ ] Approved on:
- [ ] Notes:
