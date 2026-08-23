# Implementation Log: simbox-app-uiux

> Plan: [04-plan.md](04-plan.md) — APPROVED 2026-08-20
> **2026-08-23**: Task 3's entry below was trimmed to a forward
> reference — its content now lives in
> `vdd-simbox-app-navbar-uiux/05-implementation-log.md`, per Anton's
> explicit instruction to extract all navbar content out of this flow.

## Progress: Tasks 1-4 of 13 complete and verified

- [x] **Task 1 — Fix project identity & dependencies**: `pubspec.yaml`
  renamed `flutter_gsmsip_example` → `simbox_app`, fixed the broken
  `flutter_gsmsip: path: ../` → `path: ../../libs/flutter_gsmsip`, added
  `two_dimensional_scrollables: ^0.3.3`. Ran `flutter create --platforms=
  linux .` to scaffold the missing `linux/` platform folder (app was
  Android-only before). **`flutter pub get` now succeeds** (previously
  failed outright).
- [x] **Task 2 — Theme/token reconciliation**: `lib/theme/app_colors.dart`
  — brand gradient now the DS's exact `#00C6FB → #005BEA`, neutrals/text/
  borders/shadow reconciled to DS values (`--bg #F8F9FA`, `--fg-1
  #303F49`, `--fg-2 #B6B6B6`, hairline `rgba(156,178,194,*)`), semantic
  success/warning/danger updated to DS hex. `app_dimensions.dart`:
  `cardRadius` corrected 16→10 (DS "cards round to 10px"), added
  `cardRadiusLarge`/shadow-blur constants. New
  `lib/theme/app_admin_tokens.dart`: dense-table tokens sourced from
  `nativemind-designsystem-v1.8/tokens/web.css`'s "GostSimBox-admin: dense
  operations table" block (not the *other*, legacy-verbatim `--adm-*`
  block in the same file — see file comment for the distinction, it would
  have been an easy mix-up). Vendored 5 SF Pro Text TTFs into
  `assets/fonts/`, registered in `pubspec.yaml`, wired as the app's
  `fontFamily` in both light/dark `ThemeData`. Fixed a real bug while at
  it: one hand-converted rgba→Color literal had 9 hex digits
  (`0x090005BEA`) instead of 8 — caught by `use_full_hex_values_for_flutter_colors`.
- [x] **Task 3 — Navigation shell**: originally built as
  `lib/navigation/breakpoints.dart` + `app_shell.dart` (bottom
  `NavigationBar` phone / `NavigationRail` tablet-desktop, four
  destinations in 2015-nav order) here — that content, along with the
  files themselves, is now documented in
  `vdd-simbox-app-channel-table-uiux`'s sibling flow
  `vdd-simbox-app-navbar-uiux/05-implementation-log.md` per the
  2026-08-23 extraction (see that flow for the up-to-date record of
  any future navbar changes). At the time this task originally ran,
  it also created four placeholder screens
  (`lib/screens/{sims,modems,operations,settings}/`) for Tasks 6-9 to
  fill in, and replaced `main.dart`'s demo `DashboardScreen` with
  `AppShell` + real `AppTheme` — that screen-scaffolding side-effect
  is this flow's own history and stays recorded here.
- [x] **Task 4 — `FakeModemRepository`**: `lib/state/fake_modem_repository.dart`
  implements `ModemRepository` from `flutter_gsmsip`, seeded with 3 sample
  devices matching 02-visual.md's mockup data (registered/84.20р,
  error-state/240.50р, registering-with-weak-signal/3.15р). Wired into
  the app via `provider` (`Provider<ModemRepository>` in `main.dart`,
  disposed on app teardown) so every future screen can
  `context.read<ModemRepository>()` without touching `main.dart` again.

## Verification

```
$ flutter pub get       # succeeds (was failing before Task 1)
$ flutter analyze lib test
0 errors (25 pre-existing info/warning-level lints in untouched files)

$ flutter test test/widget_test.dart
00:00 +2: All tests passed!
```

Manual run not yet done in this session (no Linux desktop display
available in this environment) — widget tests simulate a 390×844 (phone)
viewport and confirm all four destinations render and switching works;
tablet/desktop breakpoints are exercised by `LayoutBuilder` logic but not
yet eyeballed against 02-visual.md. Flag for Task 13.

## Progress: Tasks 5-9 also complete (all four screens now real)

- [x] **Task 5 — Shared widgets**: `lib/widgets/`: `stat_tile.dart`,
  `action_chip.dart`, `filter_chip_row.dart`, `entity_card.dart` (phone
  card with a hand-rolled horizontal-drag swipe-reveal — not a package,
  matches the prototype's own vanilla pointer-drag approach),
  `ussd_console.dart`, `command_log.dart`, `detail_panel.dart`,
  `dense_modem_table.dart` (wraps `two_dimensional_scrollables`'
  `TableView.builder` — verified the real API against the installed
  package source under `~/.pub-cache` before writing this, rather than
  guessing constructor signatures), `bottom_action_sheet.dart`
  (breakpoint-switched: bottom sheet on phone, anchored popover on
  tablet/desktop, via `showEntityActions()`). `lib/state/sim_box_line.dart`
  — the `SimBoxLine` view-model from specifications (Option 2: local
  composition over `ModemDevice`, nullable placeholder fields).
- [x] **Task 6 — Симки screen**: `lib/screens/sims/sims_screen.dart` +
  `lib/state/modem_line_list_controller.dart` (`ChangeNotifier`,
  subscribes to `modemEvents`, owns search/filter/selection state,
  distinguishes `ModemDriverNotAvailableException` from a legitimately
  empty list). Phone list (search, filter chips, swipe actions, bulk
  action sheet), tablet/desktop split (dense table + detail panel).
- [x] **Task 7 — Модемы screen**: `lib/screens/modems/modems_screen.dart`
  — line list + detail panel + radio `Switch`, reusing `DetailPanel`/
  `ModemLineListController` from Task 6 rather than duplicating.
- [x] **Task 8 — Операции screen**: `lib/screens/operations/
  operations_screen.dart` + `lib/state/operations_log_controller.dart`
  (`CallLogController`/`SmsLogController`, bounded 200-entry in-memory
  logs per specifications). Segmented Звонки/СМС toggle, dial/send forms
  with a modem dropdown, live logs.
- [x] **Task 9 — Настройки screen**: `lib/screens/settings/
  settings_screen.dart` + `lib/state/settings_form_controller.dart` +
  `lib/widgets/settings_form.dart` — dirty-state tracking, unsaved-changes
  banner, inline validation errors, reset-to-saved, and a real
  navigate-away guard (`PopScope` on phone, a confirm dialog on the
  tablet/desktop rail) rather than silently discarding edits.

## Verification (updated)

```
$ flutter analyze lib test
0 errors (pre-existing info/warning-level lints only, in files this flow
didn't touch)

$ flutter test
00:01 +8: All tests passed!
```

8 tests total: navigation shell (2), Симки screen against
`FakeModemRepository` sample data incl. search filtering (2, one test
caught a real `find.text` ambiguity — the search `TextField`'s own
rendered text also matches `find.text`, not just card titles — fixed by
asserting `findsWidgets` instead of `findsOneWidget`), `SettingsFormController`
dirty/validation/reset logic (4, one test had a logic bug of its own —
asserted "dirty" after setting an already-empty field back to empty,
which is correctly *not* dirty — fixed the test scenario, not the code).

## Deviations / Not Done This Round

- **Icon vendoring (Task 11) not started**: all icons in the four screens
  are Material Icons placeholders (`Icons.power_settings_new`,
  `Icons.router`, etc.), not the real `assets/adminka`/`assets/fugue`
  glyphs specifications call for. This is a real, visible gap versus the
  DS requirement — flagging clearly rather than letting Material icons
  quietly pass as "done." Vendoring + wiring real icons per-glyph is
  still open.
- **Cross-cutting states (Task 10) partial**: driver-unavailable banner
  is done (Симки, Модемы). Low-balance app-level banner and the
  "просыпается" loading-pulse animation on state icons are not built.
- **Manual verification pass (Task 13) not done**: no display available
  in this environment. Automated tests simulate a 390×844 viewport only;
  tablet/desktop breakpoints and the DS token mapping have not been
  eyeballed against 02-visual.md by running the app.
- Model/detail-field gaps noted in 03-specifications.md (phone number
  beyond `displayName`, LAC/CELL, call stats, autoblock reason,
  timestamps) render as "—" throughout, as planned — not a new gap, just
  confirming it's visible in the built screens now.

## Progress: Task 11 (icon vendoring) and the rest of Task 10 done

- [x] **Task 11 — Icon/asset vendoring**: vendored 15 PNGs (16×16,
  confirmed via `file`) from `nativemind-designsystem-v1.8/assets/adminka/`
  into `apps/simbox-app/assets/icons/adminka/` — power/stop, low-ACDL/
  high-DATT autoblock icons, 4 quality (qos) states, 6 call-state icons,
  USSD/SMS. New `lib/widgets/app_icons.dart`: `AppIcons` path constants,
  `AdminIcon` (renders at 16px or an exact integer multiple,
  `FilterQuality.none` — matches the DS's explicit nearest-neighbour
  resolution rule). Wired into `EntityCard`'s swipe actions (via a new
  `SwipeAction.iconWidget` field) and `ModemsScreen`'s state icon.
  - **Real, documented gap**: `rssi/` and most of `napravleine/`
    (operator marks) ship only as `.ico` (Windows icon container)
    files — confirmed via `file`, not assumed. Flutter's built-in image
    codec cannot decode `.ico` containers. Rather than adding an
    ICO-decode dependency for a handful of icons, built two real
    alternatives instead of skipping the concept entirely: `SignalBars`
    (a genuine bar-gauge widget — this actually matches the DS readme's
    own instruction that "signal strength stays a text bar gauge, not
    emoji," so it's arguably *more* correct than a static icon would
    have been) and `OperatorBadge` (colored text-initial badge, stable
    per-operator hash color). Both documented in `app_icons.dart`'s doc
    comment so this isn't a silent substitution.
- [x] **Task 10 — remaining cross-cutting states**: `lib/widgets/
  low_balance_banner.dart` (shown on Симки when any visible line's
  balance drops below a threshold — one of the fake sample devices is
  seeded at 3.15р specifically to exercise this). `lib/widgets/
  pulsing_icon.dart` (bounded 1.4s opacity pulse, matches the DS's
  "bounded and soft, no ambient loops beyond the connect-button cadence"
  motion rule) wired to `ModemState.registering` on both Симки cards and
  the Модемы line list.

## Real bug caught while wiring Task 10: infinite animation broke `pumpAndSettle()`

Adding `PulsingIcon` (an infinitely-repeating `AnimationController.repeat()`)
broke all 4 previously-passing tests — `pumpAndSettle()` waits for
animations to become idle, which a repeating animation never does, so
every test that rendered a Симки/Модемы screen timed out. This is a
well-known Flutter testing pitfall, not a logic bug, but it was a real
regression that needed a real fix: replaced every `pumpAndSettle()` call
in `test/widget_test.dart` and `test/sims_screen_test.dart` with a bounded
manual pump loop (`_settle()`: 5×50ms frames) instead of papering over it
by, say, disabling the animation under test or removing coverage.

## Verification (final for this round)

```
$ flutter analyze lib test
0 errors, 0 warnings (info-level lints only, pre-existing)

$ flutter test
00:00 +8: All tests passed!
```

## Remaining Work

- **Task 13 — manual verification pass**: still not done. No display
  available in this environment at any point in this session. Automated
  tests only simulate a 390×844 (phone) viewport; tablet/desktop
  breakpoints, the dense table's actual rendering, and the DS token
  mapping have never been visually confirmed by a human or a screenshot.
  This is the one task in the plan that structurally requires Anton (or
  a screenshot-capable environment) — recommend running the app locally
  next.
- Real `.ico`-format operator marks and signal-bar sprites remain
  unaddressed by design (see Task 11 above) — `SignalBars`/`OperatorBadge`
  are a considered substitution, not a stopgap to revisit unless Anton
  wants pixel-exact fidelity to the original sprite set specifically.

## Resume 2026-08-22 — Task 13 visual verification

Task 13 was resumed in a screenshot-capable environment. The app has no
web target and the approved scope explicitly excludes adding one, so the
in-app browser was not used to create a parallel product surface. Instead,
a temporary Flutter widget-rendering harness captured the shipped widgets
at the approved phone (390×844), tablet (900×1024), and desktop
(1440×900) breakpoints.

### States inspected

- All four top-level screens at all three breakpoints (12 captures).
- Phone: filtered-empty SIM list, modem detail, SMS form, settings form,
  validation failure, and dirty form (6 captures).
- Tablet and desktop: selected SIM detail and selected modem detail at
  each breakpoint (4 captures).

The 22 captures were visually inspected against `02-visual.md`. A real
macOS SF system font was loaded only inside the temporary harness so
Russian copy could be evaluated; it was not copied into the repository.

### Defects found and fixed

1. `DenseModemTable` exposed no row callback, making tablet/desktop SIM
   detail unreachable. Added `onRowTap`, wired it through every data cell,
   and included the opened row in the selected-state tint.
2. Modem detail placed `SwitchListTile` behind a decorated `Container`,
   hiding its Material ink and triggering Flutter's framework assertion.
   Replaced the wrapper with a rounded `Material`.
3. `SettingsForm` used a fixed footer `Row`; validation copy overflowed by
   57px at phone width. Replaced it with a wrapping action/status layout.
4. A corrected settings field retained its old validation error until the
   next Save. `setField()` now clears that field's stale error immediately.

Added permanent tests for dense-table row-to-detail navigation and stale
error clearing. Repository test count is now 10.

### New blocking design-system finding

Every `sf-pro-text-*.ttf` in both design-system font directories is an
HTML copy of a GitHub file page, not a font binary. Task 2 copied those
files verbatim, so all five app font assets are invalid. This was confirmed
with `file`; the issue exists at the source, not only in the vendored copy.
Because approved requirement AC #4 explicitly mandates bundled SF Pro
Text, the flow does not silently substitute another shipped font. Anton
must supply valid licensed files or approve platform-native fallback.

### Verification

```
temporary visual harness: 6/6 cases, 22 captures, no render exceptions
flutter test:              10/10 passed
flutter analyze lib test:  0 errors, 0 warnings; 24 info notices
```

**Ended at**: Task 13 complete and four visual defects fixed. IMPLEMENTATION
remains open solely on the invalid mandatory SF Pro asset decision; do not
advance to DOCUMENTATION until it is resolved.

## Note: Tasks 14-18 ("Каналы" redesign) moved out (2026-08-23)

This log previously carried a "Resume 2026-08-23 — Tasks 14-18, 'Каналы'
redesign amendment" entry (screen rename, `ChannelViewMode`, expandable
`DenseModemTable`, По-SIM-все + `ViewModeSwitcher`, `UiPreferences` +
Настройки → Интерфейс, tests — 18/18 tests passing). At Anton's explicit
instruction, that entire entry has been **extracted into
`vdd-simbox-app-channel-table-uiux/05-implementation-log.md`** (as its
"Session 2026-08-23 — Tasks 1-5" entry), unchanged. See that document
for the full session log, verification output, and deviations summary.

**Ended at (this flow's own scope)**: Task 13 complete and four visual
defects fixed (see the "Resume 2026-08-22" entry above). IMPLEMENTATION
remains open solely on the invalid mandatory SF Pro asset decision; do
not advance to DOCUMENTATION until it is resolved.
