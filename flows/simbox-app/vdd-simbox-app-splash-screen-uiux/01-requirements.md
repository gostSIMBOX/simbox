# Requirements: simbox-app-splash-screen-uiux

> Version: 1.1 (DRAFT — **correction**: v1.0 claimed no splash-screen
> guidance exists anywhere in the design assets. That was wrong — it
> exists at `design/nativemind-flutter-splash-template/`, a sibling
> directory to `nativemind-designsystem-v1.8/` that v1.0's search never
> looked at. Anton pointed to it directly. The Research section below
> is rewritten from that real template; the earlier "no guidance"
> claim and its "use `flutter_native_splash` package" recommendation
> are both retracted, not silently removed — see the struck-through
> history preserved in git if needed.)
> Status: APPROVED
> Last Updated: 2026-08-24

## Problem Statement

`apps/simbox-app` currently ships with **no real product identity** in
three places Anton pointed out directly:

1. **App icon** — macOS (`Assets.xcassets/AppIcon.appiconset/`) and
   Android (`mipmap-*dpi/ic_launcher.png`) both still carry Flutter's
   default generic icon (never customized since `flutter create`).
2. **Navbar** — the desktop `GostSimBoxAdminNavBar`'s identity strip
   (added in `vdd-simbox-app-navbar-uiux`) shows a generic
   `Icons.power_settings_new` placeholder next to "simbox-app", not a
   real logo.
3. **Splash screen** — Android's `launch_background.xml` is still
   Flutter's unmodified template (plain white, with the custom-bitmap
   slot explicitly commented out). macOS has no native launch-screen
   concept of its own (its "splash" is just how fast the window
   appears) — see Constraints.

`design/logo.png` (1254×1254, opaque RGB, no alpha — a blue/red rotary-
dial-phone mark on a light background) is the correct source logo:
confirmed via `guidelines/brand-logo.html`'s own "House mark vs. app
icon" distinction — this is a **product app icon**, not the abstract
NativeMind "house mark" (a separate isometric-cube glyph used only for
the company/design-system itself, "never recolored per app"). Other
candidates in `design/` (`legacy_logo_gost.png`, `logo_wide*.png`) are
older/differently-cropped variants — `design/logo.png` is the one
Anton named explicitly.

## Research: `design/nativemind-flutter-splash-template/` (corrected)

Anton pointed directly at this directory — a **complete, working
reference Flutter project** (`flutter_splash_template/`), not a design
specimen card. It ships real native code for all six Flutter target
platforms plus a README explaining the architecture. This is
NativeMind's standard splash-screen implementation, meant to be copied
into product apps wholesale, not a set of values to reinterpret.

### Architecture (README's own summary)

The one rule: **if the OS can show the first frame itself, it does —
no custom code.** A manual bootstrap window is only written where no
native launch-screen mechanism exists.

| Platform | Who draws it | Who dismisses it | Code needed |
|---|---|---|---|
| Android 12+ | SystemUI `SplashScreen` API | Flutter embedding (`LaunchTheme`→`NormalTheme`) | XML only |
| Android 5–11 | Window manager `windowBackground` | same | XML only |
| macOS | `SplashWindow.swift`, borderless `NSWindow` shown *before* `FlutterViewController` exists | Dart, via `nativemind/splash` `MethodChannel` | Swift + Dart |
| Linux | `splash_window.cc`, undecorated `GtkWindow` | same Dart channel pattern | GTK/C++ + Dart |
| iOS / Windows / Web | native storyboard / `SetNextFrameCallback` / `flutter-first-frame` JS event | — | not relevant here (see Constraints — `apps/simbox-app` has no `ios`/`windows`/`web` folders) |

Only macOS and Linux need the Dart-side handshake
(`NativeSplash.dismissOnFirstFrame()`, called once at the end of
`main()`) — the template's own comment explains why: those two
embedders don't expose a first-frame callback to native code, so the
signal has to come from Dart. Android/iOS do this declaratively via
theme switching; the Dart call is a no-op there.

**Both `apps/simbox-app` platforms plus Linux are all in scope** —
`apps/simbox-app/` has `android/`, `linux/`, and `macos/` folders
(confirmed earlier), and the template has real, ready-to-port code for
all three. This is materially more work than the v1.0 draft assumed
(which only considered Android and wrongly claimed macOS had no splash
mechanism at all).

### Exact design values (template README's own spec table)

| Element | Value |
|---|---|
| Background | `#F8F9FA` light / `#0F1419` dark — flat, no gradient |
| App logo | centered, width 240, nudged up slightly to leave room for the footer (README states "−24"; the two macOS Swift files literally use `centerYAnchor` constants of `+16` and `+24` respectively — AppKit's Y-up convention vs. the README's own Y-down design-tool convention, not a real conflict, just worth verifying against the actual ported file rather than assuming a sign) |
| NativeMind mark | height 18, `#303F49` @ 32% opacity — **dark mode**: per the template's own `.dc.html` prototype (`Splash Screen.dc.html`, checked directly, not just the README prose), the mark is *inverted* (`filter:invert(1)`) and shown at 42% opacity instead of 32%, for legibility on `#0F1419` |
| "powered by NativeMind" caption | SF Pro Text 13/400 @ 40% opacity, tracking +0.2 |
| Bottom padding | safe-area + 32 |
| Fade-out | 180ms, `cubic-bezier(.25,.1,.25,1)` — only on platforms where **our** code dismisses it (macOS/Linux) |

No brand-gradient background — the template explicitly reserves the
gradient for the connect-button treatment elsewhere in the DS, same
restraint already established in `vdd-simbox-app-uiux`'s work. This
**resolves v1.0's Open Question** (light-flat vs. gradient background)
in the direction I'd already recommended, but now on real evidence
instead of a guess.

Two macOS implementations exist in the template:
`SplashWindow.swift` (separate borderless window, shown before the
Flutter view controller is created) and `SplashOverlay.swift` (a view
added on top of the main window's content view instead). Only
`SplashWindow` is actually wired up in `MainFlutterWindow.swift` —
`SplashOverlay` is left in the template as an unused alternative. This
flow ports `SplashWindow`.

### What the splash actually shows

Two brand marks, not one: **our app's own logo** (centered, large) and
a small **NativeMind house-mark + "powered by NativeMind" caption**
docked at the bottom — the standard cross-product attribution footer.
Recorded as a real requirement below (AC #3), not assumed.

### Retracted from v1.0

- ~~No splash-screen guidance exists anywhere~~ — wrong, see above.
- ~~Recommend `flutter_native_splash` package~~ — wrong; the template
  deliberately uses **no package**, hand-written native code per
  platform, specifically to avoid the extra overlay/desync risk a
  generic package's `keepOnScreenCondition` hook can introduce at the
  most latency-sensitive point of app startup (template README's own
  stated rationale). This flow ports the template's actual files
  instead.
- ~~macOS has no native splash-screen mechanism~~ — wrong; see
  `SplashWindow.swift` above.

`guidelines/brand-logo.html`'s app-icon rule (Rounded-square icon on
the active theme accent, ~22:96 corner radius) still applies to AC
#1/#2 below (app icon, navbar) — unaffected by this correction, that
part of v1.0 was right.

## User Stories

**As a** simbox-app user
**I want** to see the real SimBox logo — as the app icon in my dock/
launcher, next to the app name in the desktop nav bar, and on the
loading screen while the app starts
**So that** the app has an actual product identity instead of Flutter's
generic default icon and a placeholder power glyph.

## Acceptance Criteria

### Must Have

1. **Given** `design/logo.png` as the source mark
   **When** the macOS and Android app icons are regenerated
   **Then** every required size is produced from this single source
   (macOS: 16/32/64/128/256/512/1024px `AppIcon.appiconset`; Android:
   `mipmap-{m,h,xh,xxh,xxxh}dpi/ic_launcher.png`), replacing Flutter's
   default template icon entirely.

2. **Given** the desktop `GostSimBoxAdminNavBar`'s identity strip
   **When** it's updated
   **Then** the generic `Icons.power_settings_new` placeholder is
   replaced with the real logo mark at the same 16px slot it occupies
   today (matching the DS's icon-sizing convention used everywhere
   else in that bar).

3. **Given** the real `design/nativemind-flutter-splash-template/`
   **When** a native splash/launch screen is added
   **Then** its actual per-platform files are ported (not
   reinterpreted) for all three platforms `apps/simbox-app` has:
   - **Android**: `values/{colors,styles}.xml` +
     `values-night/colors.xml` + `values-v31/styles.xml` (API 31+
     system `SplashScreen` API) + `drawable/launch_background.xml`,
     using `design/logo.png` as the centered icon bitmap and a
     generated `splash_branding.png` (NativeMind mark + caption,
     baked into one bitmap since Android's layer-list can't render
     text).
   - **macOS**: `SplashWindow.swift` (borderless `NSWindow`, shown in
     `MainFlutterWindow.awakeFromNib()` before `FlutterViewController`
     is created) + the `nativemind/splash` `MethodChannel` handler +
     `NativeSplash.dismissOnFirstFrame()` called at the end of Dart
     `main()`.
   - **Linux**: `splash_window.cc`/`.h` (undecorated `GtkWindow`) +
     the equivalent `my_application.cc` wiring + the same Dart-side
     dismiss call (the handshake code is platform-agnostic, shared
     with macOS).
   - Exact values per the Research table above: `#F8F9FA`/`#0F1419`
     background, 240-wide centered logo, 18px-tall NativeMind mark at
     32% opacity, "powered by NativeMind" caption, 32pt bottom inset,
     180ms fade-out (macOS/Linux only — Android's system splash has no
     app-controlled dismiss animation).
   - No elaborate animation beyond the template's own fade-out —
     matches the DS's general motion rule ("bounded and soft... no
     ambient loops").

### Should Have

- Reuse the template's `NativeSplash` Dart class (`lib/splash/
  native_splash.dart`) verbatim or near-verbatim — it's a small,
  self-contained, already-correct implementation (platform-gated
  no-op, `MissingPluginException`-safe).

### Won't Have (This Iteration)

- **Linux app *icon*** (distinct from the Linux *splash*, which is now
  in scope per AC #3): no icon convention is wired up in
  `linux/CMakeLists.txt`/`my_application.cc` today (no `.desktop`
  file, no `Icon=` entry, no icon-theme lookup) — adding one is OS
  packaging work, not a UI asset swap, and out of scope here. Flagged
  as a real gap, not silently skipped.
- **iOS/Windows/Web app icon or splash**: those platform folders don't
  exist in `apps/simbox-app/` yet (Linux-desktop-first + Android per
  the app's own stated scope) — nothing to update, even though the
  template has ready code for them.
- Any splash beyond the template's own static-frame-plus-fade design —
  no progress indicator, no logo animation, matches the DS's stated
  motion restraint and the template's own explicit "no animation"
  choice (`windowSplashScreenAnimationDuration = 0` on Android 12+).

## Constraints

- **Source of truth for the app mark**: `design/logo.png`, per Anton's
  explicit instruction — not `legacy_logo_gost.png`/`logo_wide*.png`/
  the DS's own `assets/logo.svg` (NativeMind's house mark, explicitly
  the wrong one per `brand-logo.html`'s own "never interchange them"
  rule).
- **Source of truth for splash mechanics/values**: `design/
  nativemind-flutter-splash-template/flutter_splash_template/` — port
  its actual files, don't re-derive the native code from the README
  table alone.
- **Asset format mismatch to resolve at IMPLEMENTATION, not guess
  now**: the template's own `AppLogo` slot expects a transparent PNG
  (its placeholder `app_logo.png` is 800×800 RGBA) that floats
  directly on the flat splash background. `design/logo.png` is 1254×
  1254 **opaque RGB** — a flat near-white background is baked in, no
  alpha channel. Used as-is, it would show as a visible white/near-
  white square patch on the `#0F1419` dark-mode background instead of
  blending. This needs a background-removed (transparent) derived
  export before it can be used as the splash `AppLogo` — a
  straightforward, reversible image-processing step (the background
  is a uniform near-white color, not photographic), not "drawing new
  artwork," so it's implementation work, not a design question to ask
  Anton about. Flagged here so it isn't discovered mid-IMPLEMENTATION
  as a surprise. The macOS/Android **app icon** (AC #1) doesn't have
  this problem — icon tiles are conventionally opaque squares anyway
  (matches `brand-logo.html`'s own "rounded-square... on the active
  theme accent" example), so `design/logo.png` can be used there
  directly.

## Open Questions

*(v1.0's background-color question is resolved — see Research above;
`#F8F9FA`/`#0F1419` is the template's own real value, not a guess.)*

- [ ] None currently blocking — the transparency-export step above is
      implementation work, not a design decision, so it's not listed
      as an open question requiring Anton's input before approval.

## References

- `design/logo.png` — source app mark (confirmed correct one, see
  Problem Statement).
- `design/nativemind-flutter-splash-template/flutter_splash_template/`
  — the real splash implementation to port: `README.md` (architecture
  + exact design table), `lib/splash/native_splash.dart`, `macos/
  Runner/{MainFlutterWindow,SplashWindow}.swift`, `linux/runner/
  splash_window.{cc,h}` + `my_application.cc.snippet`, `android/app/
  src/main/res/{values,values-night,values-v31}/` +
  `drawable/launch_background.xml`, `assets/branding/` (NativeMind
  mark source files, 1x-4x + SVG).
- `design/nativemind-designsystem-v1.8/guidelines/brand-logo.html` —
  app-icon guidance (house mark vs. app icon distinction, ~22:96
  corner-radius ratio, "on the active theme accent" treatment) — still
  applies to AC #1/#2, unaffected by the splash correction.
- `apps/simbox-app/macos/Runner/Assets.xcassets/AppIcon.appiconset/` —
  current (default) macOS icon set to replace.
- `apps/simbox-app/android/app/src/main/res/{mipmap-*dpi,drawable}/` —
  current (default) Android icon + launch background to replace.
- `apps/simbox-app/lib/navigation/gostsimbox_admin_nav_bar.dart` —
  `_IdentityStrip`'s placeholder icon.
- `flows/simbox-app/vdd-simbox-app-navbar-uiux/` — the flow that
  originally added the identity-strip placeholder this flow replaces.

---

## Approval

- [x] Reviewed by: Anton Dodonov
- [x] Approved on: 2026-08-24
- [x] Notes: "reqs approved" — v1.1, post-correction, no open
      questions remaining.
