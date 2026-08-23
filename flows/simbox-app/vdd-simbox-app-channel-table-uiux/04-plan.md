# Plan: simbox-app-channel-table-uiux

> Version: 1.0
> Status: APPROVED
> Last Updated: 2026-08-23
> **Extracted 2026-08-23 from `vdd-simbox-app-uiux` v1.1's Tasks 14-18**
> (renumbered 1-5 here) — content unchanged by the extraction, only
> relocated and renumbered.
> Specifications: [03-specifications.md](03-specifications.md) — APPROVED 2026-08-23

## Summary

Five tasks, built directly on top of `vdd-simbox-app-uiux`'s already-
implemented Tasks 1-13 (navigation shell, theme, base screens,
`ModemDevice`/`SimBoxLine`/`ModemLineListController`/`DenseModemTable`/
`FakeModemRepository`). Cannot be implemented independently of that
flow's prerequisite work.

## Task Breakdown

### Task 1 — Rename Симки → Каналы, add `ChannelViewMode` + expansion state
- Rename `lib/screens/sims/` screen/widget identifiers to reflect
  "Каналы" (folder rename itself is an implementation-time call, not
  forced here — renaming the visible tab label/route title is the hard
  requirement, per 03-specifications.md).
- `ModemLineListController` gains `ChannelViewMode viewMode` (default
  `byModem`), `Set<String> expandedModemIds` (session-only, not
  persisted), and a `List<SimBoxLine> flattenedRows` getter computing
  the modem-grouped/expanded or flat-by-SIM row list per
  03-specifications.md's exact algorithm.
- Complexity: medium. Dependencies: `vdd-simbox-app-uiux`'s Task 6
  (already implemented — this task modifies it in place).

### Task 2 — Expandable `DenseModemTable`
- `dense_modem_table.dart`: consumes `flattenedRows` directly as its
  `TableView` row source (`rowCount = flattenedRows.length`); modem
  parent rows render the `▾`/`▸` chevron cell (per 02-visual.md), tap
  toggles `expandedModemIds` via the controller — no changes to
  `TableView` itself, all expand/collapse logic lives in the
  controller's flattening step (per specifications' Widget Decision).
- Complexity: medium. Dependencies: Task 1.

### Task 3 — По-SIM-все flat view + `ViewModeSwitcher`
- New `view_mode_switcher.dart` widget (segmented control, `Badge`/chip
  family per specifications) — swaps `ChannelViewMode`, shown on
  desktop's Каналы table header and reachable equivalently on
  phone table mode (Task 4 depends on this being visible wherever the
  table itself is visible).
- По-SIM-все renders `flattenedRows` with no expand/collapse column
  (per 02-visual.md) — **interim scope**: seated channels only (no "не
  в модеме" row), per 03-specifications.md's Dependency Gaps section.
- Complexity: small. Dependencies: Task 2.

### Task 4 — `UiPreferences` + Настройки → Интерфейс
- New `lib/state/ui_preferences.dart`: `ChangeNotifier`,
  `bool preferTableView` backed by `shared_preferences`
  (`getBool`/`setBool`, key e.g. `simbox.preferTableView`), default
  `false`, loads once at construction (async init pattern — matches
  how `SettingsFormController`'s initial values are seeded elsewhere).
- `lib/screens/settings/`: new "Интерфейс" section/route (phone
  drill-in row + tablet/desktop left-rail entry, per 02-visual.md), one
  `Switch` row bound to `UiPreferences.preferTableView` — no
  Save/Reset, takes effect immediately (per specifications).
- Каналы reads `UiPreferences.preferTableView` to decide card-list vs.
  table rendering on phone (desktop/tablet unaffected, already
  always-table per `vdd-simbox-app-uiux`'s original AC #3). **Scoped
  down during implementation**: does not extend to Модемы — discovered
  its real tablet/desktop layout is a flat `ListView`, not a
  `DenseModemTable`, so there's no existing table for the toggle to
  surface on phone; see 02-visual.md's correction note. Flagged as a
  future enhancement, not silently dropped.
- Complexity: medium. Dependencies: Task 3 (Каналы must already
  support table mode before this toggle can switch to it),
  `vdd-simbox-app-uiux`'s Task 9 (Настройки screen, already
  implemented).

### Task 5 — Tests
- Controller tests: `flattenedRows` for both view modes (empty modem,
  single-channel modem — no parent row, multi-channel modem
  expanded/collapsed, По-SIM-все flat output).
- `UiPreferences` test: default value, persistence round-trip via a
  fake/in-memory `SharedPreferences` (matches `shared_preferences`'s
  own documented `SharedPreferences.setMockInitialValues` testing
  pattern).
- Update existing `sims_screen_test.dart`/`widget_test.dart`: provide
  `ChangeNotifierProvider<UiPreferences>` (a new hard dependency),
  rename "Симки"/"Выберите симку" text expectations.
- One test at a time, per project testing protocol. Complexity:
  medium. Dependencies: Tasks 1-4.

## Explicitly Deferred

- **По-SIM-все's "не в модеме" row** (unseated SIM cards) — waits on
  `sdd-flutter_gsmsip-interface`'s SIM-inventory-independent-of-modem
  addendum (flagged there 2026-08-23, not designed/built anywhere yet).
  Task 3 ships seated-only in the meantime.
- **A real Модемы dense-table** (to extend the Task 4 toggle there
  too) — legitimate future enhancement, not part of this round; see
  Task 4's scope-down note.

## Testing Strategy

- `dart analyze lib test` clean after Task 4 (all screens/state
  touched); Task 5's tests per above; a manual verification pass
  (repeat `vdd-simbox-app-uiux`'s Task 13 method) covering specifically:
  both view modes, expand/collapse on a multi-channel modem, and the
  Настройки → Интерфейс toggle's effect on phone — before this flow is
  considered implementation-complete (independent of
  `vdd-simbox-app-uiux`'s own Task 13 pass, which covered its own base
  screens only).

## Rollback Considerations

- All work is additive (new files) except `sims_screen.dart`,
  `settings_screen.dart`, `main.dart`, `app_shell.dart`, and
  `sim_box_line.dart`/`modem_line_list_controller.dart`/
  `fake_modem_repository.dart` (modified in place) — no persisted user
  data or migrations involved anywhere in this plan; `UiPreferences`'s
  `shared_preferences` key is new and additive, doesn't touch existing
  stored data.

## Sequencing Reminder

Cannot start before `vdd-simbox-app-uiux`'s Tasks 1-13 are implemented
(they were, before this flow existed as a separate document) — this
flow is purely additive on top of that already-implemented base.
Final visual-fidelity sign-off is gated on the same font-asset blocker
`vdd-simbox-app-uiux` tracks (see that flow's `_status.md`); code/tests
are not blocked by it.

---

## Approval

- [x] Reviewed by: Anton Dodonov
- [x] Approved on: 2026-08-23 (as `vdd-simbox-app-uiux` v1.1's Tasks
      14-18, before extraction into this flow)
- [x] Notes: Content unchanged by the extraction, only renumbered
      14-18 → 1-5.
