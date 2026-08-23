# Implementation Log: simbox-app-navbar-uiux

> Plan: [04-plan.md](04-plan.md) — APPROVED 2026-08-23

## Session 2026-08-23 — Tasks 1-8

- [x] **Task 1 — `package_info_plus` dependency**: added to
  `pubspec.yaml` (`^8.0.0`, resolved to `8.3.1`). `flutter pub get`
  succeeds.
- [x] **Task 2 — `NavIcon` sealed type**: `app_shell.dart` gained
  `sealed class NavIcon` with `MaterialNavIcon`/`SvgNavIcon` variants;
  `AppShellDestination` (made public — was private `_AppShellDestination`,
  needed to be visible to the new `gostsimbox_admin_nav_bar.dart` file)
  now holds a `NavIcon navIcon` instead of separate `icon`/`selectedIcon`
  fields. All four `_destinations` entries updated to
  `MaterialNavIcon(...)`, wrapping their existing `Icons.*` pairs — no
  visible change, groundwork for Tasks 4/5.
- [x] **Task 3 — `NavClock`**: new `lib/navigation/nav_clock.dart` —
  `Timer.periodic(Duration(seconds: 1))`, `HH:mm:ss` via `intl`'s
  `DateFormat` (already a dependency). Disposes its timer.
- [x] **Task 4 — `GostSimBoxAdminNavBar`**: new
  `lib/navigation/gostsimbox_admin_nav_bar.dart` — sticky identity strip
  (app name + `PackageInfo.fromPlatform()`'s version via `FutureBuilder`
  + `NavClock`) and a `_TabRow` of `_NavTab` widgets. Active tab:
  `AppAdminTokens.rowSelected` background, `AppColors.primary`
  icon/text, 600-weight, 8px radius. Idle tab: transparent,
  `AppColors.lightTextSecondary`, `Opacity(0.75)` icon. Hover (desktop/
  web, `MouseRegion`): `AppAdminTokens.rowLine` wash. Header bottom
  border: `AppAdminTokens.chromeLine`. Confirms specifications' finding
  that `rowSelected`/`chromeLine` are byte-identical to the template's
  own active-pill/header-border colors — no new token constants needed.
- [x] **Task 5 — `NativeBottomBarShell`**: replaces `_PhoneShell`/
  `_RailShell` in `app_shell.dart`. Branches on
  `Theme.of(context).platform == TargetPlatform.iOS`: iOS gets
  `CupertinoTabBar` (from `package:flutter/cupertino.dart`) as
  `Scaffold.bottomNavigationBar`, no `BackdropFilterOrPlain` wrapper
  (would double-blur its own translucent background, per
  specifications' Behavior/Edge Cases); everything else keeps today's
  Material `NavigationBar`, still wrapped in `BackdropFilterOrPlain`.
- [x] **Task 6 — Rewired `AppShell.build()`**: `LayoutBuilder` now
  branches only on `AppBreakpoints.isDesktop(width)` —
  `GostSimBoxAdminNavBar` (Task 4) at/above 1024px,
  `NativeBottomBarShell` (Task 5) below it (covers both the old phone
  and tablet ranges identically). `_RailShell` deleted entirely;
  confirmed via `grep -rn "NavigationRail" lib test` — zero remaining
  references anywhere in the app.
- [x] **Task 7 — Tests**: new `test/app_shell_test.dart` (5 tests):
  chrome-selection at phone/tablet/desktop widths, the iOS
  platform-branch case (`ThemeData(platform: TargetPlatform.iOS)`),
  and the cross-platform-describability test (all four labels present,
  same order, across Android-phone/iOS-phone/desktop chrome). All 5
  pass; full suite 23/23 (was 18 before this session — confirmed 0
  regressions, not just 0 new failures).
- [x] **Task 8 — Manual verification pass**: see below — a real macOS
  build/run, not a screenshot harness (see Deviations).

### Real bug found and fixed while attempting Task 8: `flutter_gsm` platform classes not exported

`flutter build macos` failed before any of this flow's own code ran:
`.dart_tool/flutter_build/dart_plugin_registrant.dart` (Flutter's
generated plugin registrant) calls
`flutter_gsm.AndroidFlutterGsm.registerWith()` /
`LinuxFlutterGsm.registerWith()` / `MacosFlutterGsm.registerWith()` /
`WindowsFlutterGsm.registerWith()` through `flutter_gsm`'s **public**
import, but none of those four classes were exported from
`libsFlutter/flutter_gsm/lib/flutter_gsm.dart` — they exist under
`lib/src/{android,linux,macos,windows}/`, confirmed by grep, but were
never re-exported. This broke **every** native build target
(Android/Linux/macOS/Windows) for `apps/simbox-app`, not just this
flow's own work — almost certainly why prior sessions' visual
verification (`vdd-simbox-app-uiux`'s Task 13) used a temporary
widget-rendering harness instead of a real app run.

Fixed by adding the four missing exports to `flutter_gsm.dart` (purely
additive — no behavior change, confirmed via `flutter analyze lib` in
`libsFlutter/flutter_gsm` showing the same 2 pre-existing info-level
lints, and its own 58-test suite still passing in full). This is
outside this flow's own scope (a `flutter_gsm` bug, governed by its own
`sdd-flutter_gsm`/`sdd-flutter_gsm-ffi` flows) but was fixed directly
rather than left blocking, per this project's established precedent
for small, disclosed, low-risk fixes discovered while validating a
flow (e.g. `sdd-simbox-app-real-driver`'s `shim_config.c` inline-comment
fix). Flagging here for visibility rather than silently folding it in.

### Manual verification — real macOS app run

With the export fix in place, `flutter build macos --debug` succeeded
and `apps/simbox-app`'s full test suite (23/23) still passed. Launched
the built `.app`, resized its window via AppleScript/System Events, and
captured real screenshots (`screencapture`) at three widths:

- **1280×900 (desktop)**: `GostSimBoxAdminNavBar` renders correctly —
  sticky identity strip ("simbox-app 1.0.0" + live clock), horizontal
  tab row, active "Каналы" tab shown as a brand-blue-tinted pill with
  600-weight text, idle tabs (Модемы/Операции/Настройки) grey with
  dimmed icons — matches `02-visual.md`'s mockup.
- **390×844 (phone)** and **900×1024 (tablet)**: both render the
  identical Material `NavigationBar` bottom-tab-bar chrome (not a
  rail) — confirms AC #5's width-driven, not device-type-driven,
  tablet chrome change took effect. (Active-tab indicator renders in
  the app's existing green `secondary`/`accent` color, not blue — this
  is `NavigationBar`'s own pre-existing Material 3 default styling
  from `AppTheme.lightTheme`, untouched by this flow; not a defect.)
- **Not captured**: the desktop tab-row hover wash (no pointer-
  simulation tool available in this environment — `cliclick`/`Quartz`
  both absent) and the iOS `CupertinoTabBar` chrome (no iOS
  Simulator build attempted — `flutter_gsm` has no iOS platform
  implementation at all, since ttyUSB modems don't apply there, so an
  iOS build isn't a meaningful target for this app; the iOS branch's
  correctness is covered by Task 7's widget test instead, which does
  assert `CupertinoTabBar` renders with the right destinations).

### Deviations Summary

| Planned | Actual | Reason |
|---|---|---|
| Task 8: manual verification, method unspecified | First attempted a `RenderRepaintBoundary.toImage()` widget-screenshot harness (matching `vdd-simbox-app-uiux`'s Task 13 precedent) | `toImage()` hung indefinitely under plain `flutter test` (no real rasterization surface in that runner) — all 5 harness tests timed out after 10 minutes each (50 minutes total). Abandoned in favor of a real `flutter build macos` + `open` + `screencapture` run, which worked and is arguably a *stronger* verification (the actual compiled app, not a widget-only render) |
| (unplanned) | Fixed `flutter_gsm.dart`'s missing platform-class exports | Real, pre-existing bug blocking every native build target, discovered only because Task 8 attempted a real app build for the first time in this session's history; low-risk additive fix, disclosed above |

### Verification

```
$ dart analyze lib test   (apps/simbox-app)
0 errors (same 24 pre-existing info-level lints, none in touched files)

$ flutter test            (apps/simbox-app)
00:01 +23: All tests passed!   (was 18 before this session)

$ flutter analyze lib     (libsFlutter/flutter_gsm)
2 pre-existing info-level lints, unchanged

$ flutter test             (libsFlutter/flutter_gsm)
00:01 +58: All tests passed!

$ flutter build macos --debug   (apps/simbox-app)
✓ Built build/macos/Build/Products/Debug/simbox_app.app
```

### Remaining Work

- Real vendored SVG nav icons (`SvgNavIcon`) — waits on Anton/a
  designer, per specifications' disclosed Icon Approach deviation.
  `MaterialNavIcon` ships in the meantime.
- Desktop tab-row hover-state screenshot — not captured (tooling gap
  in this environment), but the `MouseRegion`/`AppAdminTokens.rowLine`
  implementation itself is straightforward and low-risk; worth a
  human eyeball pass at some point, not blocking.
- The `flutter_gsm` export fix should be mentioned to whoever owns
  that package's flows next time they're touched, so it isn't
  mistaken for scope creep from this flow.

**Ended at**: Tasks 1-8 complete. All automated tests pass (23/23 in
`apps/simbox-app`, 58/58 in `flutter_gsm`), and a real macOS build/run
visually confirmed the desktop chrome and the width-driven
phone/tablet chrome unification. This flow's IMPLEMENTATION is
code-complete; ready for DOCUMENTATION once Anton reviews.
