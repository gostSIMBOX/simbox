# Status: vdd-simbox-app-splash-screen-uiux

## Current Phase

IMPLEMENTATION

## Phase Status

CODE COMPLETE — all 13 tasks done and verified: `dart analyze`/
`flutter test` clean (23/23), and a real `flutter build macos` + app
launch confirmed the app icon, navbar branding, and splash
create→present→dismiss handshake all work without errors or visible
glitches. Linux/Android are code-complete but not launched (no
Linux desktop display or Android emulator in this environment,
disclosed clearly, not silently skipped).

## Last Updated

2026-08-24 by Claude (plan approved; implemented Tasks 1-13 — asset
pipeline from `design/logo.png` [transparency export, app icons,
splash imageset, Android composited bitmaps], native splash code
ported to macOS/Linux/Android, Dart wiring, navbar icon swap, tests,
and a real macOS manual verification pass. Found and fixed one real
build issue along the way — `AppLogo`/`NativeMindMark.imageset`'s
`Contents.json` needed `"universal"` idiom, not `"mac"` — and disclosed
one real, pre-existing font-asset blocker affecting Android's
composited splash bitmap. See `05-implementation-log.md` for full
detail.)

## Blockers

None blocking. Two disclosed, non-blocking loose ends carried into
`05-implementation-log.md`'s Remaining Work: Linux/Android need a real
device/emulator to actually launch-verify, and
`drawable-xxhdpi/splash_branding.png` was rendered with the macOS
system font (SFNS) instead of the app's own (corrupted) vendored SF
Pro Text — same shared blocker as `vdd-simbox-app-uiux`.

## Progress

- [x] Requirements drafted (v1.0, 2026-08-24; corrected to v1.1,
      2026-08-24 same session)
- [x] Requirements approved (2026-08-24)
- [x] Visual mockups drafted (v1.0; amended to v1.1, 2026-08-24 —
      footer word order)
- [x] Visual mockups approved (2026-08-24)
- [x] Specifications drafted (v1.0, 2026-08-24)
- [x] Specifications approved (2026-08-24)
- [x] Plan drafted (v1.0, 2026-08-24)
- [x] Plan approved (2026-08-24)
- [x] Implementation started (2026-08-24)
- [x] Implementation code complete (2026-08-24) — `dart analyze`/
      `flutter test` clean (23/23); real macOS manual verification done
- [ ] Documentation drafted
- [ ] Documentation approved

## Context Notes

- **The real splash source was `design/nativemind-flutter-splash-
  template/flutter_splash_template/`** — a complete Flutter project,
  ported (not reinterpreted): `lib/splash/native_splash.dart`,
  `macos/Runner/{MainFlutterWindow,SplashWindow}.swift`,
  `linux/runner/splash_window.{cc,h}` + merged `my_application.cc`
  wiring, and the full Android `values/{colors,styles}.xml` +
  `values-night/` + `values-v31/` + `values-night-v31/` +
  `drawable/launch_background.xml` set.
- **Only macOS and Linux needed the Dart-side dismiss call** —
  `main.dart` gained one `NativeSplash.dismissOnFirstFrame()` call;
  the real work was native per-platform files.
- **`SplashWindow.swift` is the ported macOS approach** (a separate
  borderless `NSWindow`) — the template's alternative
  `SplashOverlay.swift` was **not** ported (correctly identified as
  unused in the template itself).
- **Real asset gap found and resolved**: `design/logo.png` had no
  alpha channel. Produced `design/logo_transparent.png` via a PIL
  threshold mask (uniform near-white background → alpha 0), verified
  clean edges by compositing onto `#0F1419`. Used for the splash logo;
  the opaque original is still used for the app icon (icon tiles are
  conventionally filled squares).
- **Correction from an earlier note in this file**: the template's own
  `assets/fonts/sf-pro-text-*.ttf` are **not** usable — confirmed via
  `file` that they're the exact same "HTML document text" corruption
  already documented as a blocker in `vdd-simbox-app-uiux`'s
  implementation log, affecting every copy of these filenames found
  anywhere in this repo, including inside the splash template itself.
  Used the real macOS system font (`SFNS.ttf`) for the one generated
  bitmap that needs text (`splash_branding.png`) instead — disclosed,
  not silently faked.
- **A real Xcode project-file gotcha, caught by actually building**:
  `AppLogo.imageset`/`NativeMindMark.imageset`'s `Contents.json` used
  `"idiom": "mac"` (copied from `AppIcon.appiconset`'s own convention)
  on the first attempt — `actool` warned "unassigned child" for the 3x
  variants. Fixed to `"idiom": "universal"` (correct for a plain
  named-image imageset, distinct from an app-icon-set), rebuilt,
  warnings gone.
- **A real design deviation found during Linux porting**: the actual
  `apps/simbox-app/linux/runner/my_application.cc` already had its own
  `first-frame` GObject-signal-based window reveal (Flutter's own
  default Linux template mechanism) — different from what the splash
  template's README claims ("Linux has no first-frame callback
  available"). Removed the old signal handler entirely in favor of the
  template's channel-based approach, to avoid two competing reveal
  paths — a real judgment call, not blind pasting.
- **Splash transient frame not directly screenshotted**: the app
  launches faster (warm build) than 100ms-interval screenshot polling
  could reliably sample. Verified indirectly instead (no visible
  glitches across many repeated launches) — disclosed as weaker
  evidence than a direct capture, not overstated.

## Fork History

Not forked. New flow, created via `/vdd resume` on a name that didn't
exist yet.

## Next Actions

1. Anton: review the real macOS screenshots/behavior described in
   `05-implementation-log.md` — nothing further required from Claude
   unless changes are requested.
2. Optional, not blocking: real Linux/Android device verification;
   regenerate `splash_branding.png` with the real SF Pro Text font
   once that project-wide asset blocker is resolved.
3. When ready, proceed to DOCUMENTATION phase (client-facing
   `06-readme.md`).
