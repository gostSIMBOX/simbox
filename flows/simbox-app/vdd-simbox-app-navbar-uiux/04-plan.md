# Plan: simbox-app-navbar-uiux

> Version: 1.0
> Status: APPROVED
> Last Updated: 2026-08-23
> Specifications: [03-specifications.md](03-specifications.md) — v1.0 APPROVED 2026-08-23

## Summary

Seven tasks, built directly on top of `vdd-simbox-app-uiux`'s
already-implemented `app_shell.dart`/`breakpoints.dart`. All work is
confined to `lib/navigation/` plus one `pubspec.yaml` addition — no
screen content is touched.

## Task Breakdown

### Task 1 — Add `package_info_plus` dependency
- `pubspec.yaml`: add `package_info_plus` (device-identity strip's
  version display, per specifications).
- Verify: `flutter pub get` succeeds.
- Complexity: trivial. Dependencies: none.

### Task 2 — `_AppShellDestination.navIcon` sealed type
- In `app_shell.dart`: replace the plain `IconData icon`/`selectedIcon`
  fields with a small sealed `NavIcon` type (`MaterialNavIcon(IconData,
  IconData selected)` for now; `SvgNavIcon(String asset)` variant added
  but unused until real SVGs land — per specifications' Icon Approach).
  Update the four existing `_destinations` entries to use
  `MaterialNavIcon` wrapping their current icon/selectedIcon pairs — no
  visible change yet, this is groundwork for Tasks 4/5.
- Complexity: small. Dependencies: none.

### Task 3 — `NavClock` widget
- New `lib/navigation/nav_clock.dart`: small `StatefulWidget`,
  `Timer.periodic(Duration(seconds: 1))` updating a `DateTime.now()`
  -formatted text (`HH:mm:ss`, per the DS's "1Hz, no smoothing" motion
  rule already documented in specifications). Disposes its timer in
  `dispose()`.
- Complexity: small. Dependencies: none.

### Task 4 — `GostSimBoxAdminNavBar` widget
- New `lib/navigation/gostsimbox_admin_nav_bar.dart`: sticky header
  (app name + `PackageInfo.fromPlatform()`'s version via one
  `FutureBuilder`, no spinner + `NavClock` from Task 3) followed by a
  `Row` of tab buttons built from `_AppShellDestination`/`NavIcon`
  (Task 2). Active tab: `AppAdminTokens.rowSelected` background,
  `AppColors.primary` icon+text, 600-weight, 8px radius, `7px 12px`
  padding. Idle tab: transparent, secondary-grey text, `Opacity(0.75)`
  icon; `MouseRegion`-driven hover wash (desktop/web only) using
  `AppAdminTokens.rowLine`. Header bottom border:
  `AppAdminTokens.chromeLine`.
- Complexity: medium. Dependencies: Tasks 1, 2, 3.

### Task 5 — `NativeBottomBarShell` (replaces `_PhoneShell`/`_RailShell`)
- In `app_shell.dart`: new `NativeBottomBarShell` widget covering both
  `< 760` and `760–1024`. Branches on `Theme.of(context).platform`:
  `TargetPlatform.iOS` → `CupertinoTabBar` (from
  `package:flutter/cupertino.dart`) as `Scaffold.bottomNavigationBar`,
  built from the same `_AppShellDestination` list, `activeColor:
  AppColors.primary`, **no** `BackdropFilterOrPlain` wrapper (its own
  translucent background would double-blur, per specifications'
  Behavior/Edge Cases). Everything else → today's existing Material
  `NavigationBar` code path, unchanged, still wrapped in
  `BackdropFilterOrPlain`.
- Complexity: medium. Dependencies: Task 2.

### Task 6 — Rewire `AppShell.build()`
- Replace the `LayoutBuilder`'s branching: `width < 1024` →
  `NativeBottomBarShell` (Task 5), `width >= 1024` →
  `GostSimBoxAdminNavBar` (Task 4) wrapping the selected screen below
  it. Delete `_RailShell` and every `NavigationRail` reference —
  confirm via `grep` that nothing else in the app imports/uses
  `NavigationRail` before deleting.
- Complexity: small. Dependencies: Tasks 4, 5.

### Task 7 — Tests
- New `test/app_shell_test.dart`: renders `AppShell` at phone (390),
  tablet (900), and desktop (1200) widths, asserts the expected chrome
  widget is present (`CupertinoTabBar`/`NavigationBar`/
  `GostSimBoxAdminNavBar`) and `NavigationRail` is never found at any
  width.
- Platform-branch case: same phone-width render wrapped in
  `Theme(data: ThemeData(platform: TargetPlatform.iOS), ...)` vs. the
  default — confirms `CupertinoTabBar` appears only for iOS.
- **Cross-platform-describability test**: iterate `_AppShellDestination`
  once per chrome variant, assert identical label/order in all three
  renders — the concrete, testable form of AC #4's actual guarantee.
- One test at a time, per project testing protocol. Complexity:
  medium. Dependencies: Task 6.

### Task 8 — Manual verification pass
- Run the app (or a screenshot-capable harness, matching
  `vdd-simbox-app-uiux`'s own Task 13 precedent) at phone/tablet/
  desktop widths, and with both platform branches, confirming: the
  `GostSimBoxAdminNavBar`'s active/idle/hover states match
  `02-visual.md`'s mockup, the clock ticks, the `CupertinoTabBar`
  renders correctly embedded in the `MaterialApp` root (no
  cross-framework rendering issues), and no visible regression to the
  Android bottom bar (unchanged code path, but confirm nothing broke
  from the surrounding refactor).
- Complexity: small (mandatory — matches this project's house rule of
  visually verifying UI work, not just widget tests). Dependencies:
  Task 7.

## Explicitly Deferred

- Real vendored SVG nav icons (`SvgNavIcon`) — waits on Anton/a
  designer supplying actual DS-style artwork; `MaterialNavIcon` ships
  in the meantime, per specifications' disclosed deviation.
- Desktop identity strip showing anything beyond app name/version/
  clock (no per-device fields — simbox-app isn't administering "one
  box" the way the legacy panel was).

## Testing Strategy

- `flutter analyze lib test` clean after Task 6 (all navigation files
  touched).
- Widget/platform/describability tests per Task 7, one at a time.
- Manual verification per Task 8 — required before this flow's
  IMPLEMENTATION is considered complete.

## Rollback Considerations

- All work is additive (new files: `gostsimbox_admin_nav_bar.dart`,
  `nav_clock.dart`) except `app_shell.dart` (modified in place —
  reversible, no persisted state) and `pubspec.yaml` (one new
  dependency, additive). No migrations, no persisted user data
  involved.

## Sequencing Reminder

Independent of `vdd-simbox-app-channel-table-uiux`'s remaining work
(font-asset blocker, По-SIM-все's "не в модеме" row) — this flow only
touches `lib/navigation/`, which neither of those consume. Can be
implemented in any order relative to that flow.

---

## Approval

- [x] Reviewed by: Anton Dodonov
- [x] Approved on: 2026-08-23
- [x] Notes: "plan approved"
