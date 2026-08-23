# Specifications: simbox-app-navbar-uiux

> Version: 1.0
> Status: APPROVED
> Last Updated: 2026-08-23
> Visual: [02-visual.md](02-visual.md) — v1.0 APPROVED 2026-08-23

## Overview

Replaces `apps/simbox-app/lib/navigation/app_shell.dart`'s current
breakpoint logic (phone → `NavigationBar`, tablet/desktop →
`NavigationRail`) with the approved design: width < 1024px → native
per-OS bottom tab bar (iOS/Android), width ≥ 1024px → a new
GostSimBox-admin-style sticky top nav. Destinations, order, and icon
family stay identical across all three — that's the whole point (AC
#3/#4). `breakpoints.dart`'s existing thresholds are reused unchanged;
only what each range renders changes.

## Widget Decision — platform branch

`Theme.of(context).platform` (not `dart:io Platform.isIOS`) decides
the phone/tablet chrome variant: it's the Flutter-idiomatic seam
(testable via `debugDefaultTargetPlatformOverride`/`ThemeData(platform:
...)` in widget tests, and correctly reflects `MaterialApp`'s own
platform resolution on web/desktop rather than querying the host OS
directly).

```dart
final isIOS = Theme.of(context).platform == TargetPlatform.iOS;
```

- `TargetPlatform.iOS` → Cupertino-shaped bottom bar (`CupertinoTabBar`
  from `package:flutter/cupertino.dart`, used as `Scaffold.
  bottomNavigationBar` inside the existing `MaterialApp` — a standard,
  supported pattern; simbox-app does not need a `CupertinoApp` root for
  this).
- Everything else (Android, and — edge case — a narrow desktop/Linux
  window resized below 1024px) → Material `NavigationBar`, already
  shipped today. Desktop platforms have no native "mobile tab bar"
  convention of their own, so Material is the reasonable default for
  that edge case rather than inventing a fourth chrome variant.

This is a **new pattern** for the codebase — no existing platform
branching exists in `apps/simbox-app/lib/`. Confirmed via search before
writing this.

## Data Models

No new domain entities. The existing `_AppShellDestination` record in
`app_shell.dart` (label, icon, selectedIcon, screen) is reused as-is
by all three chrome variants — the single source of truth for
order/labels that AC #3 requires. One new field is added:

- `_AppShellDestination.navIcon` — see **Icon Approach** below for why
  this stays `IconData`-based rather than switching to vendored SVGs
  in this round.

## Icon Approach — practical implementation (deviates from the visual doc's literal wording)

`02-visual.md`'s Resolved Items call for "4 new simple icons drawn in
the DS's stroke/weight style." Flagging honestly before specifying
further: **hand-authoring new SVG artwork is not something this
text-based SDD/VDD flow can actually produce** — there's no design
tool or illustrator in this environment, only code. Two real options:

1. Ship with the **existing Material icon set already in
   `app_shell.dart`** (`Icons.sim_card_outlined`/`router_outlined`/
   `call_outlined`/`settings_outlined`, with filled variants for the
   selected state) — these already map sensibly onto the four
   destinations and are already implemented/shipping today. Not a
   pixel-match for the DS's custom single-path SVG style, but a real,
   buildable, currently-working icon set.
2. Vendor real custom SVGs once Anton (or a designer) supplies them,
   matching the DS's documented spec exactly (24px box,
   `currentColor`-fillable, ~2px stroke — see readme's ICONOGRAPHY
   §1, the same treatment the VPN app's own bottom-nav icons use).

**Decision**: ship option 1 now, structured so option 2 is a drop-in
later. `_AppShellDestination.navIcon` becomes a small sealed type
(`MaterialNavIcon(IconData, IconData selected)` today; a
`SvgNavIcon(String asset)` variant added later when real SVGs exist) —
this is the same "documented gap, not silently faked" pattern already
used in this app for the RSSI/`.ico` icon gap
(`app_icons.dart`'s `SignalBars`/`OperatorBadge`). Recorded here as a
**Dependency Gap**, not guessed past.

## Chrome: Desktop / Web (≥ 1024px) — new `GostSimBoxAdminNavBar`

New widget, `lib/navigation/gostsimbox_admin_nav_bar.dart`, replaces
`NavigationRail(extended: true)` on this breakpoint. Structure per
`02-visual.md`'s mockup:

- **Sticky header row**: app name + version + a live 1Hz clock (per
  the Resolved Items' "simplified device-identity strip" — no
  hostname/IP/uptime, those don't map onto a client app). Version
  comes from `package_info_plus` (**new dependency**, not currently in
  `pubspec.yaml` — nothing in the app reads its own version today).
  Clock ticks once per second, no smoothing/interpolation — matches
  the DS readme's own documented rule ("the timer ticks at 1Hz, no
  smoothing") for the exact same kind of live-clock UI.
- **Tab row**: one `Row` of tab buttons, one per `_AppShellDestination`.
  Active tab: background `AppAdminTokens.rowSelected`
  (`rgba(0,91,234,.09)` — **this token already exists**, created for
  the dense-table's selected-row tint in `vdd-simbox-app-uiux`'s work,
  and is byte-identical to the template's active-tab pill color; reuse
  it rather than defining a near-duplicate constant), text/icon
  `AppColors.primary` (`#005BEA`), 600-weight, 8px radius, `7px 12px`
  padding. Idle tab: transparent, `AppColors.lightTextSecondary`-ish
  grey text, icon at 75% opacity (`Opacity` wrapper, since Material
  icons don't have a native "dim" state); hover →
  `AppAdminTokens.rowLine`-family light wash (`onHover`/`MouseRegion`,
  desktop/web only — no-op on touch).
- Header border: `AppAdminTokens.chromeLine` (`rgba(156,178,194,.14)`
  — again, an exact match to the template's own header
  `border-bottom`, already defined).
- `Scaffold.appBar` slot is **not** used for this — it's a custom
  widget above the body, matching the template's own non-`<header>`
  sticky-div structure and giving full control over the two-row layout
  (identity strip + tab row).

## Chrome: Phone/Tablet (< 1024px) — native per OS

- Both `< 760` and `760–1024` now render the **same** chrome
  (`NativeBottomBarShell`, new small wrapper in `app_shell.dart`) —
  the only difference between them is available width for the screen
  content above the bar, not the bar itself. This removes
  `_RailShell`'s tablet-compact/`desktop`-extended split entirely;
  `NavigationRail` is no longer used anywhere in this app.
- iOS: `CupertinoTabBar` — `items: [BottomNavigationBarItem, ...]`
  built from the same `_AppShellDestination` list, `activeColor:
  AppColors.primary`.
- Android (default): existing Material `NavigationBar` — unchanged
  from today's implementation, just no longer conditional on
  `isPhone` alone (now conditional on `!isDesktop` combined with the
  platform check landing here).
- `BackdropFilterOrPlain`'s frosted-nav seam (existing) is kept for
  both — the DS's "frosted bottom nav" treatment applies to both
  platforms' bottom bar equally, it's a background effect independent
  of which bar widget renders inside it.

## Affected Systems / Components

| Component | Change |
|---|---|
| `apps/simbox-app/lib/navigation/app_shell.dart` | Modify — replace `_RailShell`/tablet-vs-desktop split with `NativeBottomBarShell` (<1024, platform-branched) vs `GostSimBoxAdminNavBar` (≥1024); `_AppShellDestination` gains `navIcon` (sealed `MaterialNavIcon`/`SvgNavIcon`) |
| `apps/simbox-app/lib/navigation/breakpoints.dart` | No change — `isPhone`/`isTablet`/`isDesktop` thresholds reused as-is; only their *meaning* to `app_shell.dart` changes (tablet no longer implies rail) |
| `apps/simbox-app/lib/navigation/gostsimbox_admin_nav_bar.dart` | New — desktop/web chrome widget (identity strip + tab row) |
| `apps/simbox-app/lib/navigation/nav_clock.dart` | New — small `StatefulWidget`, 1Hz `Timer.periodic` clock, used only by `GostSimBoxAdminNavBar` |
| `apps/simbox-app/lib/widgets/app_icons.dart` | Modify — no change to existing `AppIcons`/`AdminIcon`/`SignalBars`/`OperatorBadge`; nav-specific icon sealed type lives in `app_shell.dart` instead, since it's nav-only, not shared with the dense tables |
| `apps/simbox-app/pubspec.yaml` | Add `package_info_plus` (device-identity strip's version display) |
| `apps/simbox-app/lib/theme/app_admin_tokens.dart` | No change — `rowSelected`/`chromeLine` reused as-is, see Chrome: Desktop above |

## Behavior / Edge Cases

- **Window resize crossing 1024px live** (desktop/web only): `AppShell`
  already rebuilds via `LayoutBuilder` on every resize — chrome swap is
  just a different widget subtree, no special state-preservation logic
  needed beyond what `_selectedIndex` (already `State`-held) provides;
  confirmed no per-chrome-variant local state exists that would be lost
  on the swap.
- **iOS tab bar + existing frosted-nav wrapper**: `CupertinoTabBar` has
  its own default translucent-blur background; wrapping it in
  `BackdropFilterOrPlain` would double-blur. `BackdropFilterOrPlain`'s
  `child` slot is bypassed for the iOS branch specifically (pass
  `CupertinoTabBar` directly as `bottomNavigationBar`, no wrapper) —
  documented here so it isn't read as an oversight later.
- **`package_info_plus` unavailable at first frame**: its version
  lookup is async (`PackageInfo.fromPlatform()`). `GostSimBoxAdminNavBar`
  shows the identity strip with a blank/placeholder version string
  until it resolves (one `FutureBuilder`, no loading spinner needed —
  matches this app's existing pattern of not spinner-gating small,
  fast, non-blocking async reads).

## Testing Strategy

- Widget tests (`test/app_shell_test.dart`, new): at phone width
  (390), tablet width (900), and desktop width (1200) — confirm the
  correct chrome widget renders (`CupertinoTabBar`/`NavigationBar`/
  `GostSimBoxAdminNavBar`).
- Platform-branch test: render at phone width with `ThemeData(platform:
  TargetPlatform.iOS)` vs default — confirm `CupertinoTabBar` appears
  only for iOS.
- **Cross-platform-describability test** (the actual guarantee this
  flow exists to deliver): a single test asserting destination
  label/order is identical across all three chrome variants — walks
  `_AppShellDestination`'s list once, renders each chrome, and asserts
  the same four labels appear in the same order in each.
- One test at a time, per project testing protocol.

## Dependencies / Integration Points

- Self-contained within `lib/navigation/` plus one new `pubspec.yaml`
  dependency (`package_info_plus`) — does not touch
  `vdd-simbox-app-uiux`'s screens or `vdd-simbox-app-channel-table-uiux`'s
  Каналы logic; both are pure consumers of `AppShell`'s destination
  list, unaffected by the chrome swap.
- No dependency on `sdd-flutter_gsmsip-interface` or the real driver —
  navigation chrome doesn't touch modem data.

---

## Approval

- [x] Reviewed by: Anton Dodonov
- [x] Approved on: 2026-08-23
- [x] Notes: "specs approved" — including the disclosed Icon Approach
      deviation (ship existing Material icons now, structured for a
      real-SVG swap later).
