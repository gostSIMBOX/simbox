# Status: vdd-simbox-app-navbar-uiux

## Current Phase

IMPLEMENTATION

## Phase Status

CODE COMPLETE — Tasks 1-8 all done and verified: `dart analyze`/
`flutter test` clean (23/23, was 18 before this session), and a real
`flutter build macos` + app launch + `screencapture` manual pass
confirmed the desktop chrome and the width-driven phone/tablet chrome
unification. Ready for DOCUMENTATION once Anton reviews.

## Last Updated

2026-08-23 by Claude (plan approved; implemented Tasks 1-8 —
`package_info_plus` dependency, `NavIcon` sealed type,
`GostSimBoxAdminNavBar`, `NavClock`, `NativeBottomBarShell` platform
branch, `AppShell` rewire (deleted `NavigationRail` entirely), 5 new
tests, and a real macOS manual verification pass. Along the way, found
and fixed a real pre-existing bug in `flutter_gsm.dart` — 4 platform
classes existed but were never exported, breaking every native build
target — see `05-implementation-log.md` for full detail.)

## Blockers

None. Two minor, non-blocking loose ends noted in
`05-implementation-log.md`'s Remaining Work: the desktop tab-row hover
screenshot wasn't captured (no pointer-simulation tool available in
this environment) and real vendored SVG icons are still pending per
the disclosed Icon Approach deviation.

## Progress

- [x] Requirements drafted (v1.0, 2026-08-23)
- [x] Requirements approved (2026-08-23)
- [x] Visual mockups drafted (v1.0, 2026-08-23)
- [x] Visual mockups approved (2026-08-23)
- [x] Specifications drafted (v1.0, 2026-08-23)
- [x] Specifications approved (2026-08-23)
- [x] Plan drafted (v1.0, 2026-08-23)
- [x] Plan approved (2026-08-23)
- [x] Implementation started (2026-08-23)
- [x] Implementation code complete (2026-08-23) — `dart analyze`/
      `flutter test` clean (23/23); real macOS manual verification done
- [ ] Documentation drafted
- [ ] Documentation approved

## Context Notes

- This flow extracted navbar-only content out of `vdd-simbox-app-uiux`
  (Problem Statement's nav-order line, AC #5's tab-bar/rail clause,
  `02-visual.md`'s Navigation Map + Design-System token rows for
  bottom-tab-bar/left-rail, `04-plan.md`'s Task 3, `05-implementation-
  log.md`'s Task 3 entry) — done early, right after requirements were
  approved, with forward references left in the parent flow's docs
  (same "move, not copy" pattern as `vdd-simbox-app-channel-table-
  uiux`). Per-screen content stays in `vdd-simbox-app-uiux` — only the
  shell around the four screens lives here.
- **Real code changed this session** (not just docs): `apps/simbox-app/
  lib/navigation/{app_shell.dart (rewritten), gostsimbox_admin_nav_bar.
  dart (new), nav_clock.dart (new)}`, plus `pubspec.yaml`
  (+`package_info_plus`) and `test/app_shell_test.dart` (new). Also
  `libsFlutter/flutter_gsm/lib/flutter_gsm.dart` — added 4 missing
  platform-class exports, a real bug found blocking every native build
  target, unrelated to this flow's own scope but fixed since it was
  low-risk and additive (see `05-implementation-log.md`).
- **`NavigationRail` is completely gone** from `apps/simbox-app` —
  confirmed via grep after Task 6. Any future work should not
  reintroduce it; tablet now shares phone's native bottom-bar chrome.
- Read the actual `GostSimBoxAdmin.dc.html` template directly (not
  just the readme's prose): desktop nav is a sticky header (hostname/
  IP/build/clock/uptime) + horizontal icon-label tab row
  (`assets/adminka/` icons per tab), active tab = brand-tint pill
  (`rgba(0,91,234,.09)` bg, `#005BEA` text/icon), idle = grey/
  75%-opacity icon, hover = light grey wash. Legacy template has 11
  tabs (Симки, Свистки×2, Хабы, Наборы команд, Планы, Процессы,
  Биллинг, Обновление, Debug, Иконки) — simbox-app keeps its own 4
  destinations, adopting only the *chrome*, not the legacy tab list.
- Mobile/tablet nav was a genuine open design question raised by
  Anton's support team: cross-platform describability (a user on one
  platform should be able to tell a user on another platform where to
  find something). Presented three candidate directions via
  AskUserQuestion (shared custom widget / native chrome + shared
  vocabulary / native chrome + shared icon family) — Anton picked the
  recommended option 3 (native chrome, shared adminka icon family) and
  confirmed tablet should stay width-breakpoint-driven rather than a
  fixed device-type rule. Both now recorded as Resolved Design + ACs
  #4/#5 in `01-requirements.md`.

## Fork History

Not forked. New flow, extracting navbar-specific content out of
`vdd-simbox-app-uiux` (see that flow's own `_status.md` once trimmed
for its side of the note).

## Next Actions

1. Anton: review the real macOS screenshots described in
   `05-implementation-log.md` (desktop chrome, phone/tablet bottom
   bar) — nothing further required from Claude unless changes are
   requested.
2. Optional, not blocking: real vendored SVG nav icons; a human
   eyeball pass on the desktop tab-row hover state.
3. When ready, proceed to DOCUMENTATION phase (client-facing
   `06-readme.md`).
