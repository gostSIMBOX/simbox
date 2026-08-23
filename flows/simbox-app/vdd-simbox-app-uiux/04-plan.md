# Plan: simbox-app-uiux

> Version: 1.3 (Task 3 — Navigation shell — **extracted 2026-08-23 into
> `vdd-simbox-app-navbar-uiux/04-plan.md`** at Anton's explicit
> instruction; its body below is now a forward reference, numbering
> kept intact since no other task depends on it. The earlier
> extraction of Tasks 14-18 into `vdd-simbox-app-channel-table-uiux`
> still stands, unaffected.)
> Status: APPROVED
> Last Updated: 2026-08-23
> Specifications: [03-specifications.md](03-specifications.md) — v1.3 APPROVED 2026-08-23

## Pre-Plan Finding: `apps/simbox-app` doesn't currently resolve dependencies

Checked before planning. `apps/simbox-app/pubspec.yaml` is byte-identical to
`libs/flutter_gsmsip/example/pubspec.yaml` — it's an uncorrected copy:
`name: flutter_gsmsip_example`, and `flutter_gsmsip: path: ../` (which
resolves to `apps/`, not `libs/flutter_gsmsip/`). Ran `flutter pub get`:
fails outright — *"doesn't exist (No pubspec.yaml found for package
flutter_gsmsip in .../apps.)"*. So this app cannot currently build at all,
independent of anything UI-related. Fixing this is Task 1, not optional
polish.

Also confirmed: `provider: ^6.1.2` is **already a dependency** — resolves
03-specifications.md's open question on state-management approach. Use
`ChangeNotifier` + `provider`, matching existing convention, no new
package needed for state management.

## Task Breakdown

### Task 1 — Fix project identity & dependencies (prerequisite)
- `pubspec.yaml`: rename `name:` to `simbox_app`, fix `description`, fix
  `flutter_gsmsip: path: ../../libs/flutter_gsmsip`, add
  `two_dimensional_scrollables: ^0.3.3` (dense table, per specifications).
- Verify: `flutter pub get` succeeds; `flutter analyze` runs (even if it
  reports issues in the untouched demo `main.dart` — just confirm the
  dependency graph resolves).
- Complexity: trivial. Dependencies: none.

### Task 2 — Theme/token reconciliation
- Read `nativemind-designsystem-v1.8/tokens/{colors,typography,spacing,
  fonts,web}.css` values and reconcile against `lib/theme/{app_colors,
  app_dimensions,app_gradients,app_theme}.dart` — replace ad-hoc values
  with DS-sourced constants (4pt spacing scale, SF Pro Text type roles,
  single soft shadow, 10px radius, Blue accent `#00C6FB→#005BEA`,
  adminka dense-table tokens as a new `AppAdminTokens` class alongside the
  existing theme files).
- Vendor SF Pro Text TTFs from `nativemind-designsystem-v1.8/assets/
  fonts/uploads/*.ttf` into `apps/simbox-app/assets/fonts/`; register in
  `pubspec.yaml` `flutter.fonts`.
- Complexity: medium. Dependencies: Task 1.

### Task 3 — Navigation shell (extracted 2026-08-23)
- See `vdd-simbox-app-navbar-uiux/04-plan.md`'s own Task 3 for the full
  breakdown (replacing `main.dart`'s demo `DashboardScreen` with the
  real app shell — `lib/navigation/app_shell.dart`, `breakpoints.dart`)
  — moved there unchanged at Anton's explicit instruction, along with
  the rest of that flow's navigation-shell content. Kept as a numbered
  entry here only so Tasks 4+'s "Dependencies: Task 2" references
  don't need renumbering; nothing in this plan actually depends on
  Task 3's own completion.
- Complexity: n/a (forward reference). Dependencies: n/a.

### Task 4 — `FakeModemRepository` test double
- New `lib/state/fake_modem_repository.dart` (or `test/support/` if
  Anton prefers it kept out of shipped `lib/` — default to `lib/` behind
  a debug-only factory flag so QA builds can exercise real UI states
  without hardware): implements `ModemRepository` from `flutter_gsmsip`,
  seeded with prototype-realistic sample rows (matching 02-visual.md's
  card examples: 79123456789/84.20р/ОП:30.07, blocked SIM, low-balance
  SIM), emits `ModemEvent`s on a timer/on-demand for manual QA of
  loading/attach/detach/signal-change states.
- **This unblocks visually verifying every other task** without waiting
  on `sdd-flutter_gsmsip-channel` — build it early.
- Complexity: medium. Dependencies: Task 1 (needs `flutter_gsmsip` to
  resolve).

### Task 5 — Shared widgets
- `lib/widgets/`: `entity_card.dart` (phone list card w/ swipe actions),
  `detail_panel.dart` (stats grid + actions + USSD console + identifiers
  + command log — reused across Симки/Модемы), `stat_tile.dart`,
  `action_chip.dart`, `filter_chip_row.dart`, `bottom_action_sheet.dart` /
  `action_popover.dart` (breakpoint-switched), `ussd_console.dart`,
  `command_log.dart`, `dense_modem_table.dart` (wraps
  `two_dimensional_scrollables`' `TableView`, DS zebra/stacked-cell/
  icon-stack styling baked in per specifications).
- Complexity: large (this is the bulk of reusable UI). Dependencies:
  Task 2.

### Task 6 — Симки screen
- `lib/screens/sims/`: phone list view, tablet split view, desktop dense
  table view (via `DenseModemTable`), all three per 02-visual.md.
  `SimBoxLine` view-model (composes `ModemDevice` + `ModemGroupConfig` +
  `CarrierProfile`, "—" placeholders for the flagged Dependency-Gap
  fields per 03-specifications.md) and `ModemLineListController`
  (`ChangeNotifier`, subscribes to `ModemRepository.modemEvents`, owns
  filter/search/selection state).
- Complexity: large. Dependencies: Tasks 4, 5.

### Task 7 — Модемы screen
- `lib/screens/modems/`: Хабы/Линии drill-in (phone) / expand-in-place
  (tablet/desktop), reusing `DetailPanel` for line/modem detail, radio
  `Switch` toggle, reboot/firmware sub-list.
- Complexity: medium. Dependencies: Tasks 4, 5.

### Task 8 — Операции screen (Звонки + СМС)
- `lib/screens/operations/`: segmented Звонки/СМС toggle, call/SMS forms,
  logs. `CallLogController`/`SmsLogController` (`ChangeNotifier`,
  subscribe to `ModemEvent.ModemCallStateChanged`/`ModemSmsReceived`,
  bounded in-memory log per specifications).
- Complexity: medium. Dependencies: Tasks 4, 5.

### Task 9 — Настройки screen
- `lib/screens/settings/`: left-rail (tablet/desktop) / drill-in list
  (phone), `SettingsForm` widget with dirty-state tracking, unsaved-changes
  banner, validation errors, reset-to-saved, route-guard on navigate-away
  with unsaved changes (`PopScope`).
- Complexity: medium. Dependencies: Task 5.

### Task 10 — Cross-cutting states
- Driver-not-available banner (`ModemDriverNotAvailableException` from
  `flutter_gsmsip`) distinct from empty-filter state, wired into Симки/
  Модемы/Операции screens.
- Low-balance app-level banner, toast system, loading/"просыпается"
  pulse state on modem state icons (reuse connect-button pulse cadence
  per DS motion guidance).
- Complexity: small. Dependencies: Tasks 6, 7, 8.

### Task 11 — Icon/asset vendoring
- Per-glyph copy from `nativemind-designsystem-v1.8/assets/{adminka,
  fugue}` into `apps/simbox-app/assets/` **as each screen is built**
  (Task 5-9), not upfront — avoid bulk-copying the full 224+3570-file
  sets per specifications' constraint.
- Complexity: small, spread across other tasks (tracked here for
  visibility, not a standalone deliverable).

### Task 12 — Tests
- Widget tests for `DenseModemTable`, `EntityCard`, `DetailPanel` against
  `FakeModemRepository` sample data (golden-ish structural tests, not
  pixel goldens — no golden-image infra exists yet).
- Controller tests: `ModemLineListController` filter/search/selection
  logic, `CallLogController`/`SmsLogController` event-to-log-append logic.
- One test at a time, per project testing protocol.
- Complexity: medium. Dependencies: Tasks 6-9.

### Task 13 — Manual verification pass
- Run the app (Linux desktop target) against `FakeModemRepository`,
  walk every screen × breakpoint × state combination enumerated in
  02-visual.md, confirm against the DS token mapping table.
- Complexity: small (but mandatory — this flow's own CLAUDE.md-derived
  house rule requires trying the feature in a browser/app before
  claiming UI work complete, not just relying on widget tests).
  Dependencies: Task 12.

## Note: "Каналы Redesign" amendment tasks moved out (2026-08-23)

This document previously carried Tasks 14-18 (the "Каналы Redesign"
amendment: screen rename, `ChannelViewMode`/expansion state, expandable
`DenseModemTable`, По-SIM-все + `ViewModeSwitcher`, `UiPreferences` +
Настройки → Интерфейс, tests). At Anton's explicit instruction, those
tasks have been **extracted into `vdd-simbox-app-channel-table-uiux/
04-plan.md`** as its Tasks 1-5, unchanged. See that document for the
full task breakdown — it builds directly on top of this flow's
already-implemented Tasks 1-13 below.

## Explicitly Deferred

- Real `ModemRepository` wiring (vs. `FakeModemRepository`) — waits on
  `sdd-flutter_gsmsip-channel`; this flow ships against the fake
  throughout, per specifications' assumption.
- The `ModemDevice`/`ModemStatistics` field addendum (phone number,
  LAC/CELL, call stats, autoblock reason, timestamps) — proposed as a
  follow-up to `sdd-flutter_gsmsip-interface`, not built here. UI renders
  "—" for these fields via `SimBoxLine`'s nullable placeholders.
- "Web in browser"/"web from phone" legacy layouts — out of scope per
  03-specifications.md's locked-in assumption.

## Testing Strategy

- `flutter analyze` clean after Tasks 1-3 (navigation shell baseline)
  and again after Task 9 (all screens).
- Widget/controller tests per Task 12, run one at a time.
- Manual app-run verification per Task 13 — required before this flow's
  IMPLEMENTATION phase is considered complete, since automated tests
  don't verify actual visual fidelity against the DS/prototype.

## Rollback Considerations

- All work is additive/new files except Task 1 (pubspec fix, required
  regardless of this flow — the app doesn't build without it) and Task 2
  (theme file edits — reversible, no runtime data affected).
- No persisted user data or migrations involved anywhere in this plan.

## Sequencing Reminder

Per 01-requirements.md's Constraints: this plan's tasks may all be
**built** now, but final merge/ship should track
`sdd-flutter_gsmsip-interface` reaching Anton's actual approval (currently
IMPLEMENTATION/REVIEW — see that flow's `_status.md`) — this flow depends
on its *compiling, exported* API, which already exists as of this session,
so implementation is unblocked in practice; formal completion should note
the upstream flow's approval status alongside this one's.

---

## Approval

- [x] Reviewed by: Anton Dodonov
- [x] Approved on: 2026-08-23
- [x] Notes: v1.3 reflects the 2026-08-23 extraction of Tasks 14-18
      (the "Каналы Redesign" amendment) into
      `vdd-simbox-app-channel-table-uiux`, and Task 3 (Navigation
      shell) into `vdd-simbox-app-navbar-uiux` — no new content
      approval needed here, the underlying v1.0 approval for Tasks
      1-13 stands unchanged.
