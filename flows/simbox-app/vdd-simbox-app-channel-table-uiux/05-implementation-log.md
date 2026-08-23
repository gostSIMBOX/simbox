# Implementation Log: simbox-app-channel-table-uiux

> Plan: [04-plan.md](04-plan.md) — APPROVED 2026-08-23
> **Extracted 2026-08-23 from `vdd-simbox-app-uiux/05-implementation-log.md`'s
> "Resume 2026-08-23 — Tasks 14-18" entry** — content unchanged by the
> extraction, only relocated and renumbered (14-18 → 1-5).

## Session 2026-08-23 — Tasks 1-5 (originally Tasks 14-18 of `vdd-simbox-app-uiux`)

Requirements → visual → specifications → plan all drafted and approved
earlier the same session (see those docs' own Approval sections).
Re-assessed the font-asset blocker before starting: it blocks final
visual-fidelity sign-off, not writing/analyzing/testing/running new
Dart code — `vdd-simbox-app-uiux`'s own Task 13 precedent already ran
the app against the platform-native fallback font. This work proceeded
on that basis.

- [x] **Task 1 — Rename Симки → Каналы, `ChannelViewMode` + expansion
  state**: `lib/state/channel_view_mode.dart` (new, `byModem`/`bySimAll`),
  `lib/state/channel_row.dart` (new, sealed `ChannelRow` with
  `ModemGroupRow`/`ChannelLineRow` variants — the pre-flattened row
  union `DenseModemTable` actually renders). `SimBoxLine` gained
  `modemGroupKey` (groups by exact `portPath` match — the only real
  physical-location signal `ModemDevice` exposes today; documented as
  a pragmatic heuristic, not a real field, same spirit as the existing
  Dependency-Gap fields). `ModemLineListController` gained `viewMode`,
  `expandedModemIds`, `setViewMode()`, `toggleModemExpanded()`, and the
  `flattenedRows` getter implementing the grouping/expansion algorithm
  from 03-specifications.md exactly (single-channel modems skip the
  parent row; collapsed modems contribute zero rows). Renamed the
  visible "Симки" label to "Каналы" in `app_shell.dart` and
  `sims_screen.dart`.
  - **`FakeModemRepository` extended**: added a dual-channel sample
    modem (`ttyUSB3-line1`/`ttyUSB3-line2`, sharing `portPath:
    '/dev/ttyUSB3'`) — no such sample existed before this work, so
    expand/collapse would have had nothing to exercise. Documented
    inline why it was added.
- [x] **Task 2 — Expandable `DenseModemTable`**: confirmed by reading
  the actual installed package source
  (`two_dimensional_scrollables-0.3.9/lib/src/table_view/table.dart`)
  that `TableView` needed **zero changes** — it was already fully
  generic (`rows: List<T>`, `columns: List<DenseTableColumn<T>>`), so
  expand/collapse is entirely `_channelColumns()`'s cell builders
  pattern-matching on `ChannelRow` (chevron column for
  `ModemGroupRow`, blank for `ChannelLineRow`) plus
  `_handleChannelRowTap()` dispatching tap-to-toggle vs.
  tap-to-open-detail. Simpler than planned — flagging the positive
  deviation rather than silently taking credit for "Task 2 was easy."
- [x] **Task 3 — По-SIM-все + `ViewModeSwitcher`**: new
  `lib/widgets/view_mode_switcher.dart` (two `ChoiceChip`s, same visual
  family as `FilterChipRow`). `flattenedRows` already handled the flat
  branch (Task 1) — this task was wiring the switcher into
  `_SplitLayout`'s header and confirming По-SIM-все renders correctly
  (interim seated-only scope, per the Dependency Gaps section).
- [x] **Task 4 — `UiPreferences` + Настройки → Интерфейс**: new
  `lib/state/ui_preferences.dart` (`ChangeNotifier`, `shared_preferences`-
  backed, async-loads with a `false` default like
  `ModemLineListController._load()`'s existing pattern). Wired into
  `main.dart` via `MultiProvider` (alongside the existing
  `Provider<ModemRepository>`). New `_InterfaceSettings` widget +
  `_SettingsSection.customContent` seam (settings sections that aren't
  a dirty-tracked form — "Интерфейс" is the first user of this, "Обновление"
  could adopt it later but wasn't touched). `sims_screen.dart` gained a
  new `_PhoneTable` widget (same header as `_PhoneList`, table body
  instead of cards, full-screen detail navigation like `_PhoneList` —
  not `_SplitLayout`'s side-pane, which doesn't fit phone width) and a
  `context.watch<UiPreferences>()` branch in `SimsScreen.build()`.
  - **Scope correction found while implementing, not assumed going
    in**: 02-visual.md and 03-specifications.md both originally
    claimed the toggle would "also apply" to Модемы via an
    expand-in-place hub→line tree already shown for tablet/desktop.
    Reading the real `modems_screen.dart` found that tree **does not
    exist** — it's a flat `ListView`/`ListTile` list at every
    breakpoint, no `DenseModemTable`. That claim was Claude's own
    inference when drafting the original AC wording, not something
    Anton specifically asked for beyond Каналы. **Scoped down**: the
    toggle applies to Каналы only; corrected both docs with an
    explicit note rather than silently building a mismatched
    half-feature or quietly dropping the claim. A real Модемы
    dense-table would be materially more work (building the
    hub-grouping tree from scratch) — flagged as a legitimate future
    enhancement.
- [x] **Task 5 — Tests**: new `test/modem_line_list_controller_test.dart`
  (5 tests — single-channel-no-parent-row, multi-channel-collapsed-by-
  default, toggle-reveals-then-hides, По-SIM-все flat with no
  `ModemGroupRow`, view-mode-switch-back-restores-tree) and new
  `test/ui_preferences_test.dart` (3 tests — default, persist round-trip
  via `SharedPreferences.setMockInitialValues`, no-op-if-unchanged
  doesn't notify). Updated `test/sims_screen_test.dart`'s `_wrap()` to
  provide `ChangeNotifierProvider<UiPreferences>` (missing it threw
  `ProviderNotFoundException` once `sims_screen.dart` started reading
  it) and renamed its "Симки"/"Выберите симку" text expectations to
  "Каналы"/"Выберите канал". Updated `test/widget_test.dart`'s "Симки"
  text expectation the same way.

### Verification

```
$ dart analyze lib test
0 errors (same 24 pre-existing info-level lints as before this work,
all in files it didn't touch)

$ flutter test
00:01 +18: All tests passed!
```

18 tests total in `apps/simbox-app` (was 10 before this work): +5
`modem_line_list_controller_test.dart`, +3 `ui_preferences_test.dart`,
existing 10 all still passing after the rename/provider fixes above —
confirmed 0 regressions, not just 0 new failures (re-ran the full
suite after every file change, per this session's checkpoint
discipline).

### Deviations Summary

| Planned | Actual | Reason |
|---------|--------|--------|
| Task 2: possibly modify `DenseModemTable` for row expansion | Zero changes to that widget | Confirmed via reading the actual package source that it was already generic enough; expand/collapse lives entirely in the pre-flattening step, exactly as 03-specifications.md's Widget Decision anticipated |
| Task 4: toggle applies to Каналы and Модемы | Каналы only | `modems_screen.dart`'s real tablet/desktop layout has no dense-table representation to surface on phone — discovered while implementing, not assumed; corrected 02-visual.md/03-specifications.md/04-plan.md with explicit notes, flagged as future work rather than silently built-wrong or silently dropped |

### Remaining Work

- **Font-asset blocker** (shared with `vdd-simbox-app-uiux`, unaffected
  by this flow's split-out): still needs Anton to supply valid
  licensed SF Pro Text TTFs or approve a platform-native fallback
  before this flow's UI can be considered implementation-complete in
  the strict sense (real bundled font, not the fallback used for
  verification here).
- A real Модемы dense-table (to extend the Табличный-вид toggle there
  too) is a legitimate future enhancement, not part of this round.
- `sdd-flutter_gsmsip-interface`'s SIM-inventory-independent-of-modem
  addendum (needed for По-SIM-все's "не в модеме" row) — separate flow,
  not started.

**Ended at**: Tasks 1-5 code-complete and verified. Final visual-
fidelity sign-off gated on the shared font-asset blocker, same as
`vdd-simbox-app-uiux`.
