# Implementation Log: simbox-app-splash-screen-uiux

> Plan: [04-plan.md](04-plan.md) — APPROVED 2026-08-24

## Session 2026-08-24 — Tasks 1-13

- [x] **Task 1 — Transparency export**: PIL threshold-mask script sampled
  the flat near-white background (~`#FEFEFE`) and produced
  `design/logo_transparent.png` (1254×1254 RGBA). Verified: corner
  alpha 0, center alpha 255; composited onto `#0F1419` to confirm no
  white-halo fringing at the mark's edges.
- [x] **Task 2 — App icon generation**: resized the **opaque**
  `design/logo.png` (LANCZOS) into all 7 macOS
  `AppIcon.appiconset/app_icon_{16,32,64,128,256,512,1024}.png` and all
  5 Android `mipmap-{m,h,xh,xxh,xxxh}dpi/ic_launcher.png`
  (48/72/96/144/192px), overwriting Flutter's defaults.
- [x] **Task 3 — Splash app-logo assets**: from the transparent master —
  macOS `Assets.xcassets/AppLogo.imageset/` (1x/2x/3x @
  240/480/720px) + `Contents.json`, and
  `apps/simbox-app/assets/branding/app_logo.png` (480px, for Linux's
  Flutter-bundle read path and the navbar icon).
- [x] **Task 4 — Vendored the NativeMind mark**: copied the template's
  `nativemind_mark_{1x,2x,3x,4x}.png` + `.svg` as-is into
  `assets/branding/`, and a new `Assets.xcassets/
  NativeMindMark.imageset/` (1x/2x/3x + `Contents.json`).
- [x] **Task 5 — Android composited bitmaps**: `drawable-xxhdpi/
  splash_branding.png` — "powered by" + NativeMind mark (tinted
  `#8A97A3` @ 40%) + "NativeMind", **inline mark order** per Anton's
  instruction, rendered via PIL at 3x pixel scale (xxhdpi baseline).
  `drawable-xxhdpi/{splash_icon,splash_icon_bitmap}.png` — the
  transparent logo padded into Android 12+'s real 240dp/160dp-safe-zone
  icon-mask constraint.
  - **Deviation, disclosed**: this app's own `assets/fonts/sf-pro-
    text-*.ttf` files are the same pre-existing invalid-HTML-file
    blocker documented in `vdd-simbox-app-uiux`'s implementation log —
    confirmed the *template's own* bundled fonts are identically
    corrupted (`file` shows "HTML document text" for all copies found
    in the repo, including inside `design/nativemind-flutter-splash-
    template/`). Used the real macOS system font (`/System/Library/
    Fonts/SFNS.ttf`, actual San Francisco) for this one generated
    bitmap instead — not silently faked, and a closer visual match to
    "SF Pro Text" than any other fallback available in this
    environment.
- [x] **Task 6 — `pubspec.yaml`**: added `assets/branding/` to
  `flutter.assets`. `flutter pub get` succeeds.
- [x] **Task 7 — macOS native splash**: new `SplashWindow.swift`
  (footer reordered to `["powered by", mark, "NativeMind"]`, three
  separate views instead of the template's `[mark, one-line-caption]`
  pair). `MainFlutterWindow.swift` rewritten: creates+presents the
  splash before `FlutterViewController`, **`setFrame(display:)` changed
  `true` → `false`**, registers the `nativemind/splash` channel,
  `revealApp()`. Added `SplashWindow.swift` to `Runner.xcodeproj/
  project.pbxproj`'s Compile Sources (`PBXBuildFile`+`PBXFileReference`
  entries with fresh unique IDs, `PBXGroup` and
  `PBXSourcesBuildPhase` membership) — confirmed necessary and
  sufficient via a real `flutter build macos` (see Verification).
- [x] **Task 8 — Linux native splash**: new `splash_window.h`/`.cc`
  (footer reordered the same way, three packed widgets instead of two).
  `CMakeLists.txt`: added `"splash_window.cc"` to `add_executable`.
  `my_application.cc`: merged the template's snippet into the real
  `MyApplication` struct/`activate()` — added `splash`/`window`
  fields, `handle_dismiss`/`method_call_cb`, deferred
  `gtk_widget_show(window)` to the dismiss handler.
  - **Real design choice made, not just ported blindly**: our actual
    `my_application.cc` already had its own reveal mechanism (a
    `first-frame` GObject signal on `FlView`, native to Flutter's own
    Linux template) — different from what the splash template's README
    claims ("the embedder doesn't expose a first-frame callback"),
    which turned out not to match what's actually in this codebase.
    Replaced the `first-frame` signal entirely with the template's
    channel-based approach for consistency with the Dart-side contract
    (`NativeSplash._needsHandshake` expects Linux to use the channel),
    rather than leaving two competing reveal mechanisms. Flagged here
    since it's a deviation from "port, don't reinterpret."
- [x] **Task 9 — Android native splash**: new `values/colors.xml` +
  `values-night/colors.xml`; `values/styles.xml` and `values-night/
  styles.xml` (both already existed as Flutter defaults) gained
  status/nav-bar color items; new `values-v31/styles.xml` +
  `values-night-v31/styles.xml` (API 31+ system SplashScreen API,
  light+dark). `drawable/launch_background.xml` filled in with the
  two bitmap layers (48dp/32dp insets, matching the template exactly).
- [x] **Task 10 — Dart wiring**: new `lib/splash/native_splash.dart`
  (ported near-verbatim). `main.dart`: added
  `WidgetsFlutterBinding.ensureInitialized()` + `NativeSplash.
  dismissOnFirstFrame()`.
- [x] **Task 11 — Navbar icon**: `gostsimbox_admin_nav_bar.dart`'s
  `_IdentityStrip` — `Icon(Icons.power_settings_new, ...)` →
  `Image.asset('assets/branding/app_logo.png', ...)`, un-tinted, same
  16px slot.
- [x] **Task 12 — Tests**: `flutter analyze lib test` — 0 errors (same
  24 pre-existing info-level lints). `flutter test` — 23/23 passing,
  confirmed zero regressions (same count as before this flow).
- [x] **Task 13 — Manual verification**: see below.

### Manual verification — real macOS build/run

First `flutter build macos` attempt succeeded but `actool` logged
"The image set has an unassigned child" warnings for `AppLogo`/
`NativeMindMark` — traced to `Contents.json` using `"idiom": "mac"`
(copied from `AppIcon.appiconset`'s convention) instead of the correct
`"universal"` idiom for a plain named-image imageset. Fixed both
`Contents.json` files; rebuilt; warnings gone.

Launched the rebuilt `.app`, confirmed via screenshot:

- **Navbar identity strip**: shows the real logo mark (blue rotary-dial
  phone, red pointer) at the correct 16px slot, replacing the old
  power-icon placeholder — cropped/zoomed screenshot inspected
  directly.
- **App launches cleanly to the correct main UI** (`GostSimBoxAdminNavBar`
  desktop chrome, version "1.0.1" read correctly via
  `package_info_plus`, live clock) — no crash, no stuck blank window,
  no visible flash artifact between splash and main content across
  several repeated launches.
- **Splash transient frame itself was not captured**: polled
  screenshots at 100ms intervals across 20 launches — the app (warm
  build, cached engine) reaches its fully-rendered main screen faster
  than this polling interval can reliably sample the splash window's
  lifetime. Its *absence* of any visible glitch (no flash, no hang, no
  stray blank window) is itself indirect evidence the
  create→present→dismiss handshake works correctly, but this is not
  the same as a direct screenshot of the splash frame itself — noted
  honestly rather than claimed as stronger evidence than it is.
- **App icon**: generation pipeline verified structurally (correct
  file sizes/formats/dimensions produced, `actool` processed
  `AppIcon.appiconset` into `AppIcon.icns` without warnings in the
  build log) — not separately confirmed via a Dock screenshot (a busy,
  crowded Dock made visual identification unreliable; the underlying
  asset-generation step itself is low-risk and already
  directly inspected).

### Linux / Android — structural verification only (disclosed limitation)

No Linux desktop display or Android emulator/device in this
environment, consistent with every prior flow's own disclosed gap here
(`sdd-flutter_gsm-ffi`, `sdd-simbox-app-real-driver`, etc.). Verified
instead by: careful reading of the final `my_application.cc`/
`splash_window.cc` (no `flutter build linux` possible here to compile-
check them), and content review of all Android XML/PNG assets
generated. **Not launched on either platform.**

### Verification

```
$ flutter analyze lib test
0 errors (same 24 pre-existing info-level lints)

$ flutter test
00:21 +23: All tests passed!

$ flutter build macos --debug   (after the Contents.json idiom fix)
✓ Built build/macos/Build/Products/Debug/simbox_app.app
(no actool warnings)
```

### Deviations Summary

| Planned | Actual | Reason |
|---|---|---|
| Task 5: composite text using the app's vendored SF Pro Text font | Used macOS system SFNS.ttf instead | The vendored font files are the same pre-existing invalid-HTML blocker from `vdd-simbox-app-uiux` — confirmed it also affects the splash template's own bundled copies, not just this app's; disclosed, not silently faked |
| Task 8: port the template's Linux reveal mechanism as-is | Also removed the pre-existing `first-frame` GObject signal handler | Our real `my_application.cc` already had its own (different) reveal mechanism the template's README didn't account for; kept only one reveal path instead of two competing ones |
| Task 13: capture the splash frame directly via screenshot | Could not reliably catch the sub-100ms transient | App launches faster than shell-level screenshot polling can sample; verified indirectly (no visible glitches across repeated launches) instead — disclosed as weaker evidence, not overstated |

### Remaining Work

- Real Linux/Android launch verification — needs a Linux desktop or
  Android device/emulator, not available here.
- The macOS/Linux splash transient frame was never directly
  screenshotted, only inferred to work correctly from the absence of
  visible glitches — a real device/screen-recording tool (rather than
  polled screenshots) would give a more direct confirmation if this
  matters later.
- Font substitution for `splash_branding.png` should be regenerated
  with the real SF Pro Text font once the project's own font-asset
  blocker (shared with `vdd-simbox-app-uiux`) is resolved.

**Ended at**: Tasks 1-13 complete. All automated tests pass (23/23),
`flutter analyze` clean, and a real macOS build/run confirms the app
icon pipeline, navbar branding, and splash dismiss handshake all work
without errors or visible glitches. Linux/Android are code-complete
but unverified by an actual launch, disclosed clearly above. Ready for
Anton's review.
