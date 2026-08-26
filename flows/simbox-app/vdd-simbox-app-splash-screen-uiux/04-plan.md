# Plan: simbox-app-splash-screen-uiux

> Version: 1.0
> Status: APPROVED
> Last Updated: 2026-08-24
> Specifications: [03-specifications.md](03-specifications.md) — v1.0 APPROVED 2026-08-24

## Summary

Thirteen tasks: an asset-generation pipeline first (everything else
consumes its output), then native code per platform, then the small
Dart-side wiring, then tests and manual verification.

## Task Breakdown

### Task 1 — Transparency export of `design/logo.png`
- PIL script: sample the flat near-white background color, mask it to
  alpha 0, save `design/logo_transparent.png` (RGBA) alongside the
  source as a reviewable artifact.
- Complexity: small. Dependencies: none.

### Task 2 — App icon generation (macOS + Android)
- From the **opaque** `design/logo.png`: resize into macOS
  `AppIcon.appiconset`'s 7 files (16/32/64/128/256/512/1024px) and
  Android `mipmap-{m,h,xh,xxh,xxxh}dpi/ic_launcher.png`
  (48/72/96/144/192px), overwriting Flutter's defaults.
- Complexity: small. Dependencies: none.

### Task 3 — Splash app-logo assets (macOS imageset + Flutter bundle)
- From the **transparent** master (Task 1): generate macOS
  `Assets.xcassets/AppLogo.imageset/` (1x/2x/3x @ 240/480/720px +
  `Contents.json`, same idiom pattern as the existing
  `AppIcon.appiconset`) and `apps/simbox-app/assets/branding/
  app_logo.png` (for Linux's Flutter-bundle read path and the navbar
  icon).
- Complexity: small. Dependencies: Task 1.

### Task 4 — Vendor the NativeMind mark
- Copy the template's `assets/branding/nativemind_mark_{1x,2x,3x,4x}.
  png` + `.svg` as-is into `apps/simbox-app/assets/branding/` (Linux/
  Flutter-bundle path) and a new `Assets.xcassets/
  NativeMindMark.imageset/` + `Contents.json` (macOS path).
- Complexity: small. Dependencies: none.

### Task 5 — Android `splash_branding`/`splash_icon` bitmaps
- PIL: composite "powered by " + NativeMind mark + " NativeMind" (per
  the approved footer word order) into `drawable-xxhdpi/
  splash_branding.png`, using the already-vendored `assets/fonts/
  sf-pro-text-regular.ttf`, `#8A97A3` @ 40% alpha.
- Pad the transparent logo master (Task 1) into Android 12+'s real
  192dp/160dp-safe-zone icon-mask constraint, save as
  `drawable-xxhdpi/{splash_icon,splash_icon_bitmap}.png`.
- Complexity: medium. Dependencies: Task 1, Task 4.

### Task 6 — `pubspec.yaml`
- Add `assets/branding/` to `flutter.assets`.
- Verify: `flutter pub get` succeeds.
- Complexity: trivial. Dependencies: Tasks 3, 4.

### Task 7 — macOS native splash
- New `macos/Runner/SplashWindow.swift` — ported from the template,
  footer reordered to `["powered by " label, mark, "NativeMind"
  label]`.
- Modify `macos/Runner/MainFlutterWindow.swift` — create+present
  `SplashWindow` before `FlutterViewController`, change
  `setFrame(windowFrame, display: true)` → `display: false`, register
  the `nativemind/splash` `MethodChannel` handler, add `revealApp()`.
- Modify `Runner.xcodeproj/project.pbxproj` — add `SplashWindow.swift`
  to the Runner target's Compile Sources build phase (verify via a
  real `flutter build macos` — a missing entry fails silently as "file
  not found" at link time, not a clear error).
- Complexity: medium. Dependencies: Task 3, Task 4.

### Task 8 — Linux native splash
- New `linux/runner/splash_window.h`/`.cc` — ported, footer reordered
  the same way as Task 7.
- Modify `linux/runner/CMakeLists.txt` — add `"splash_window.cc"` to
  the existing `add_executable(${BINARY_NAME} ...)` source list.
- Modify `linux/runner/my_application.cc` — merge the template's
  `my_application.cc.snippet` logic into the real `MyApplication`
  struct/`my_application_activate()` (adapt, don't paste — our file
  has its own existing struct fields/window setup).
- Complexity: medium. Dependencies: Task 3, Task 4, Task 6 (Linux
  reads the logo from the *bundled* Flutter assets, so `pubspec.yaml`
  must already declare them).

### Task 9 — Android native splash
- Modify `values/colors.xml` (add `splash_background`/`nm_fg_1`), new
  `values-night/colors.xml` (dark variants).
- Modify `values/styles.xml` (`LaunchTheme` gains `windowBackground`/
  status-bar/nav-bar items, API 21-30 path); new `values-v31/
  styles.xml` + `values-night-v31/styles.xml` (API 31+ system
  `SplashScreen` API theme, light + dark).
- Modify `drawable/launch_background.xml` — fill in the existing
  commented-out bitmap slot.
- Complexity: medium. Dependencies: Task 5.

### Task 10 — Dart wiring
- New `lib/splash/native_splash.dart` — ported near-verbatim from the
  template.
- Modify `lib/main.dart` — `main()` gains
  `WidgetsFlutterBinding.ensureInitialized();` before `runApp()` and
  `NativeSplash.dismissOnFirstFrame();` after.
- Complexity: small. Dependencies: none (can run in parallel with
  Tasks 7-9; needed before Task 13's manual verification makes sense).

### Task 11 — Navbar icon swap
- `lib/navigation/gostsimbox_admin_nav_bar.dart`'s `_IdentityStrip`:
  `Icon(Icons.power_settings_new, ...)` → `Image.asset('assets/
  branding/app_logo.png', width: 16, height: 16, filterQuality:
  FilterQuality.none)`, un-tinted (matches AC #2/the existing untinted
  bottom-bar nav icons).
- Complexity: trivial. Dependencies: Task 3, Task 6.

### Task 12 — Tests
- `flutter analyze lib test` clean.
- Full `flutter test` suite re-run — confirm zero regressions (per
  specifications' Behavior/Edge Cases note, `NativeSplash` is never
  invoked by any existing test's `pumpWidget`-based setup, so no test
  changes are expected — verify this holds, don't just assume it).
- No new Flutter tests planned (native splash isn't observable via
  `flutter_test`, per specifications).
- Complexity: small. Dependencies: Tasks 10, 11.

### Task 13 — Manual verification
- **macOS** (real build available in this environment): `flutter
  build macos` + launch + screenshot, confirm the splash appears with
  correct logo/mark/footer word order in both light and dark mode,
  dismisses cleanly (no blank-frame flash), and the navbar/app icon
  are updated.
- **Linux/Android**: structural verification only (file content
  review, `flutter analyze`) — disclosed limitation, no Linux desktop
  display or Android emulator in this dev environment. Flag clearly in
  the implementation log rather than silently skipping.
- Complexity: small but mandatory (matches this project's house rule
  of visually verifying UI work before claiming done). Dependencies:
  Task 12.

## Explicitly Deferred

- iOS/Windows/Web splash or app icon — those platform folders don't
  exist in `apps/simbox-app/` yet, per requirements' Won't Have.
- Linux app *icon* (`.desktop` file / `Icon=` entry) — separate,
  OS-packaging-level gap, not a UI asset swap, per requirements' Won't
  Have.
- Real device/emulator verification for Linux and Android — carried
  forward as a known gap, same disclosed pattern as prior flows
  (`sdd-flutter_gsm-ffi`, etc.).

## Testing Strategy

- `flutter analyze lib test` clean after Task 11 (all Dart changes
  landed).
- Full `flutter test` suite re-run per Task 12.
- Manual verification per Task 13 — macOS real, Linux/Android
  structural-only (disclosed).

## Rollback Considerations

- All native-platform work is additive (new files) except
  `MainFlutterWindow.swift`, `my_application.cc`,
  `launch_background.xml`, `styles.xml`/`colors.xml`, and
  `project.pbxproj` (modified in place) — no persisted user data or
  migrations anywhere in this plan. `design/logo_transparent.png` is a
  new derived design artifact, not a replacement of the source.

## Sequencing Reminder

Independent of every other active `simbox-app` flow
(`vdd-simbox-app-channel-table-uiux`, `sdd-simbox-app-real-driver`) —
touches only app bootstrap/branding assets and native runner files,
none of which those flows consume.

---

## Approval

- [x] Reviewed by: Anton Dodonov
- [x] Approved on: 2026-08-24
- [x] Notes: "plan approved"
