# Specifications: simbox-app-splash-screen-uiux

> Version: 1.0
> Status: APPROVED
> Last Updated: 2026-08-24
> Visual: [02-visual.md](02-visual.md) — v1.1 APPROVED 2026-08-24

## Overview

Port `design/nativemind-flutter-splash-template/flutter_splash_template/`'s
real native splash code into `apps/simbox-app` for its three real
platforms (android/macos/linux), generate app-icon and splash assets
from `design/logo.png`, and swap the navbar's placeholder icon — with
one explicit content change from the template's default: the footer
reads "powered by [mark] NativeMind" (mark inline between the words),
not the template's own "[mark] powered by NativeMind".

Two asset-delivery mechanisms exist per platform, confirmed by reading
the template's actual source (not assumed from the README table
alone):

- **macOS**: `SplashWindow.swift` loads `NSImage(named: "AppLogo")` /
  `NSImage(named: "NativeMindMark")` — **native Xcode asset-catalog
  images**. The template ships **no** `Assets.xcassets` entries for
  these — they're per-product, must be added to *our* project's
  catalog (confirmed: no `AppLogo.imageset`/`NativeMindMark.imageset`
  exist anywhere in the template).
- **Linux**: `splash_window.cc` loads pixbufs directly from
  `data/flutter_assets/assets/branding/{app_logo.png,
  nativemind_mark_2x.png}` at runtime — the **Flutter asset bundle**,
  the same `assets/branding/` folder declared in `pubspec.yaml`.

Both need the same image content delivered through different
pipelines — not an oversight, an artifact of platform embedding
differences (macOS creates its splash before any Flutter assets are
unpacked; Linux's GTK runner can read the already-unpacked bundle).

## Asset Pipeline (new)

1. **Transparency export** (`design/logo.png` → splash-usable master):
   `design/logo.png` is 1254×1254 opaque RGB (flat near-white
   background baked in). Produce a transparent derived master by
   masking out the uniform background color (a flat brand mark, not a
   photo — straightforward threshold-based alpha masking via PIL, not
   "drawing new art"). Store the derived master alongside the source
   (e.g. `design/logo_transparent.png`) so it's a visible, reviewable
   artifact, not a hidden build step.
2. **App icon** (uses the **opaque** original, not the transparent
   master — icon tiles are conventionally filled squares, matches
   `brand-logo.html`'s own example):
   - macOS: resize into all 7 `AppIcon.appiconset` files
     (16/32/64/128/256/512/1024px), replacing Flutter's defaults.
   - Android: resize into `mipmap-{m,h,xh,xxh,xxxh}dpi/ic_launcher.png`
     (48/72/96/144/192px), replacing Flutter's defaults.
3. **Splash app logo** (uses the **transparent** master, target
   display width 240pt/dp):
   - macOS: new `Assets.xcassets/AppLogo.imageset/` — 1x/2x/3x PNGs
     (240/480/720px) + `Contents.json` (same idiom pattern already
     used by `AppIcon.appiconset`, confirmed by reading it).
   - Linux (+ shared Flutter-asset copy, also usable by any future
     Windows/web port): `apps/simbox-app/assets/branding/app_logo.png`.
4. **NativeMind mark**: **not regenerated** — the template's own
   `assets/branding/nativemind_mark_{1x,2x,3x,4x}.png` + `.svg` are
   NativeMind's generic cross-product mark, not per-app. Vendor as-is
   into both delivery paths: `apps/simbox-app/assets/branding/` (Linux/
   Flutter-bundle) and a new `Assets.xcassets/NativeMindMark.imageset/`
   (macOS).
5. **Android `splash_branding.png`** (API 21-30 layer-list AND the
   API 31+ `windowSplashScreenBrandingImage` slot both reference this):
   composited bitmap of "powered by " + the NativeMind mark + "
   NativeMind" — baked into one PNG since Android's `<layer-list>` and
   the system SplashScreen API can't render live text. Built with PIL
   using the already-vendored `assets/fonts/sf-pro-text-regular.ttf`,
   `#8A97A3` @ 40% alpha (matches the Linux GTK implementation's own
   `NM_CAPTION` color token, confirmed from `splash_window.cc`).
   Rendered once at a single generous pixel scale (matches this app's
   existing convention — `ic_launcher.png` etc. are per-density-bucket,
   but the template itself references `splash_branding`/`splash_icon`
   as **unqualified** `drawable/` resources, i.e. one file, no density
   variants) placed in `drawable-xxhdpi/` for crispness on
   high-density screens (a common single-source convention), per
   Android's own density-scaling behavior for unqualified vs.
   bucketed resources.
6. **Android `splash_icon`/`splash_icon_bitmap`** (API 31+ animated-icon
   slot / API 21-30 layer-list icon respectively): the transparent
   logo master, padded to fit Android 12+'s real platform constraint —
   the system clips the icon to a circle, safe content must stay
   within the inner ~160dp of a 192dp bounding box (a real, documented
   Android constraint, not a guess) — pad the mark rather than letting
   it fill edge-to-edge to avoid corner clipping by the system mask.

## Native Code Port

### macOS

| File | Change |
|---|---|
| `macos/Runner/Assets.xcassets/AppLogo.imageset/{Contents.json,*.png}` | New |
| `macos/Runner/Assets.xcassets/NativeMindMark.imageset/{Contents.json,*.png}` | New |
| `macos/Runner/SplashWindow.swift` | New — ported from the template, **footer view order changed**: template packs `[mark, caption]` as one `NSTextField`; ours splits the caption into `["powered by " label, mark ImageView, " NativeMind" label]` in the `NSStackView`, per Anton's explicit instruction |
| `macos/Runner/MainFlutterWindow.swift` | Modify — rewritten per the template's `awakeFromNib()`: create+present `SplashWindow` before `FlutterViewController`, **change `setFrame(windowFrame, display: true)` → `display: false`** (a real, easy-to-miss required change — showing the window immediately would flash an empty frame before the splash reveals it), register the `nativemind/splash` `MethodChannel` handler, add `revealApp()` |
| `Runner.xcodeproj/project.pbxproj` | Modify — **`SplashWindow.swift` must be added to the Runner target's Compile Sources build phase**, or `flutter build macos` will silently not compile it (dropping a `.swift` file into the folder alone does nothing without an Xcode project reference) — flagged as a real implementation risk to verify carefully, not assumed to "just work" |

### Linux

| File | Change |
|---|---|
| `linux/runner/splash_window.h` | New — ported verbatim (small, no product-specific content) |
| `linux/runner/splash_window.cc` | New — ported, **footer packing order changed**: template does `gtk_box_pack_start(footer, mark)` then `gtk_box_pack_start(footer, caption)` (mark first); ours packs three widgets — `"powered by "` label, mark image, `"NativeMind"` label, in that order |
| `linux/runner/CMakeLists.txt` | Modify — add `"splash_window.cc"` to the existing `add_executable(${BINARY_NAME} ...)` source list (confirmed exact insertion point by reading the real file) |
| `linux/runner/my_application.cc` | Modify — **merge**, not paste, the template's `my_application.cc.snippet` logic into our real `MyApplication` struct/`my_application_activate()` (our file already has its own struct fields and window setup — confirmed it exists at 148 lines, not empty) — add the `splash`/`window` struct fields, the `handle_dismiss`/`method_call_cb` functions, and reorder `activate()` to create the splash first and defer `gtk_widget_show(window)` until dismiss |

### Android

| File | Change |
|---|---|
| `android/app/src/main/res/values/colors.xml` | Modify — add `splash_background`/`nm_fg_1` (light) |
| `android/app/src/main/res/values-night/colors.xml` | New — dark variants |
| `android/app/src/main/res/values/styles.xml` | Modify — `LaunchTheme` gains `windowBackground`/status-bar/nav-bar color items (API 21-30 path) |
| `android/app/src/main/res/values-v31/styles.xml` | New — API 31+ system `SplashScreen` API theme |
| `android/app/src/main/res/values-night-v31/styles.xml` | New — dark variant of the above |
| `android/app/src/main/res/drawable/launch_background.xml` | Modify — fill in the existing commented-out bitmap slot (confirmed it's the unmodified Flutter default, exactly as the template expects to patch) |
| `android/app/src/main/res/drawable-xxhdpi/{splash_icon_bitmap,splash_icon,splash_branding}.png` | New — generated per the Asset Pipeline above |
| `android/app/src/main/AndroidManifest.xml` | **No change** — already references `@style/LaunchTheme` correctly (confirmed by reading it) |

### Dart

| File | Change |
|---|---|
| `lib/splash/native_splash.dart` | New — ported near-verbatim from the template (small, self-contained, already correct: platform-gated, `MissingPluginException`-safe) |
| `lib/main.dart` | Modify — `main()` gains `WidgetsFlutterBinding.ensureInitialized();` before `runApp()` (not currently present) and `NativeSplash.dismissOnFirstFrame();` after it |
| `pubspec.yaml` | Modify — add `assets/branding/` to the `flutter.assets` list |
| `lib/navigation/gostsimbox_admin_nav_bar.dart` | Modify — `_IdentityStrip`'s `Icon(Icons.power_settings_new, ...)` → `Image.asset('assets/branding/app_logo.png', ...)` at the same 16px slot, un-tinted (matches AC #2, same convention as the existing untinted bottom-bar nav icons) |

## Behavior / Edge Cases

- **Window-hidden-until-dismissed pattern is load-bearing on both
  macOS and Linux** — confirmed both the Swift and GTK code explicitly
  avoid showing the main window early (`display: false` / omitted
  `gtk_widget_show(window)`), specifically to prevent a blank-frame
  flash between window creation and the splash handing off. This is
  not optional polish; skipping it defeats the point of the splash.
- **`NativeSplash.dismissOnFirstFrame()` is a no-op on Android** — its
  own `_needsHandshake` check gates on `Platform.isMacOS ||
  Platform.isLinux`; calling it unconditionally in `main()` (as the
  template does) is safe and correct, not an accidental Android
  side-effect.
- **Existing widget tests are unaffected**: `flutter test` runs on the
  host's `defaultTargetPlatform` (macOS in this dev environment, per
  `dart:io Platform` — not `TargetPlatform`, a different check than
  `vdd-simbox-app-navbar-uiux`'s `Theme.of(context).platform` pattern).
  `NativeSplash.dismiss()` would attempt the real `MethodChannel` call
  in a macOS-hosted test run, but every existing test constructs
  `SimboxApp`/`AppShell` directly via `tester.pumpWidget(...)`, never
  calling `main()` itself — so `NativeSplash` is never invoked in the
  test suite at all. No test changes needed.
- **API 31+ branding-slot visibility is a real, documented platform
  limitation** (per the template's own README), not something this
  flow can guarantee — some OEM firmwares hide
  `windowSplashScreenBrandingImage`. The same asset is provided
  regardless; this is disclosure, not a scope reduction.
- **Manual verification gap, disclosed upfront**: this dev environment
  has no Linux desktop display and no Android emulator/device
  (consistent with every prior flow's own disclosed limitation here —
  `sdd-flutter_gsm-ffi`, `sdd-simbox-app-real-driver`, etc.). Only
  macOS can be actually built and run to visually confirm the splash.
  Linux/Android changes will be verified structurally (file
  presence/content correctness, `flutter analyze`) but not by
  launching the real app on those platforms.

## Testing Strategy

- No meaningful Flutter widget test exists for *native* splash
  rendering — it happens before the Flutter engine's first frame, by
  definition outside what `flutter_test` can observe.
- Real verification: `flutter build macos` + launch + screenshot
  (same method already used successfully in
  `vdd-simbox-app-navbar-uiux`) — confirms the splash appears, shows
  the correct logo/mark/footer-order, and dismisses cleanly into the
  real app with the updated navbar icon.
- `flutter analyze lib test` clean after the Dart-side changes
  (`main.dart`, `native_splash.dart`, `gostsimbox_admin_nav_bar.dart`).
- Full `flutter test` suite re-run to confirm zero regressions (per
  the Behavior note above, expected to be unaffected).
- Linux/Android: structural verification only (file content review,
  no live launch) — disclosed limitation, not silently skipped.

## Dependencies / Integration Points

- **No new `pubspec.yaml` package dependencies** — the template
  deliberately avoids one (see requirements' Retracted section); this
  flow follows that same choice.
- Builds on `vdd-simbox-app-navbar-uiux`'s `PngNavIcon`/`Image.asset`
  pattern for the navbar icon swap — no new icon-rendering abstraction
  needed, reuses what already exists.
- Independent of `vdd-simbox-app-channel-table-uiux` and
  `sdd-simbox-app-real-driver` — touches only app bootstrap/branding,
  not screen content or the modem driver.

---

## Approval

- [x] Reviewed by: Anton Dodonov
- [x] Approved on: 2026-08-24
- [x] Notes: "specs approved"
