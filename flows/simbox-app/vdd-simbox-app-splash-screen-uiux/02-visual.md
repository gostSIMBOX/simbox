# Visual: simbox-app-splash-screen-uiux

> Version: 1.1 (Amendment: footer order changed to "powered by [mark]
> NativeMind" — mark inline between the two words — per Anton's
> explicit instruction, deviating from the template's own default
> "[mark] powered by NativeMind" order. Approved as stated, not
> re-requested.)
> Status: APPROVED
> Last Updated: 2026-08-24
> Source: `design/logo.png` (app mark) +
> `design/nativemind-flutter-splash-template/flutter_splash_template/`
> (splash architecture/values, `Splash Screen.dc.html` prototype
> checked directly) + `design/nativemind-designsystem-v1.8/guidelines/
> brand-logo.html` (app-icon rule).

## Notation

- `[ ]` tile/frame boundary
- `( )` logo/mark placeholder
- `┈┈┈` hairline separator
- Percentages in mark placeholders = opacity, per the source values

---

## App Icon (AC #1)

### Before → After, macOS

```
Before (Flutter default):        After (design/logo.png):
┌──────────────┐                 ┌──────────────┐
│  ⚑ generic   │                 │  ╭────────╮  │
│   Flutter    │       ──▶       │  │ (☎ dial)│  │  <- design/logo.png,
│    mark      │                 │  ╰────────╯  │     ~22:96 corner-
└──────────────┘                 └──────────────┘     radius rounding,
  (all 7 sizes:                    (all 7 sizes:       per brand-logo.html
   16/32/64/128/                    16/32/64/128/
   256/512/1024)                    256/512/1024)
```

### Before → After, Android

```
Before:                          After:
┌──────────────┐                 ┌──────────────┐
│   default    │                 │  ╭────────╮  │
│  robot/leaf   │      ──▶       │  │ (☎ dial)│  │  <- same source,
│  placeholder  │                 │  ╰────────╯  │     mipmap-{m,h,xh,
└──────────────┘                 └──────────────┘     xxh,xxxh}dpi
```

The icon tile is the **opaque** `design/logo.png` used directly — icon
tiles are conventionally filled squares (matches `brand-logo.html`'s
own `vpnclient-logo.png` example), so no transparency work is needed
here (unlike the splash logo below).

---

## Navbar (AC #2)

### Desktop `GostSimBoxAdminNavBar` identity strip — before → after

```
Before:                                        After:
┌────────────────────────────────┐             ┌────────────────────────────────┐
│(⏻) simbox-app   1.0.1   08:23:13│             │(☎) simbox-app   1.0.1   08:23:13│
└────────────────────────────────┘             └────────────────────────────────┘
 ^                                               ^
 Icons.power_settings_new                        design/logo.png, 16px,
 (generic placeholder)                           same slot/size — no
                                                  layout change, only
                                                  the icon swaps
```

Same treatment as the nav-tab icons already ship with
(`vdd-simbox-app-navbar-uiux`'s `PngNavIcon`): `Image.asset` at 16px,
`FilterQuality.none`. Unlike the tab icons, this one is **not**
color-tinted (no active/idle state to distinguish here) — rendered in
its natural colors, same as the app icon.

---

## Splash Screen (AC #3)

Frame size shown below matches the template's own reference: macOS's
`SplashWindow` is 480×320 (a small centered card, not full-screen);
Android's is a full-screen phone frame (390×844 used illustratively,
actual device size at runtime). Both share the same internal layout.

### macOS — light (`#F8F9FA`)

```
┌──────────────────────────────────────────────┐  480×320, borderless,
│                                                │  10px corner radius,
│                                                │  floating level, shown
│                 ╭──────────╮                   │  before FlutterViewController
│                 │ (☎ dial) │                   │  exists (SplashWindow.swift)
│                 ╰──────────╯                   │
│              design/logo.png                   │
│              width 240, centered                │
│                                                │
│                                                │
│                                                │
│         powered by (⬡ NM mark @32%) NativeMind │  <- footer: mark inline
└──────────────────────────────────────────────┘     between the two words
                                                       (Anton's explicit
                                                       instruction, not the
                                                       template's own
                                                       "[mark] powered by
                                                       NativeMind" order),
                                                       13px caption @40%,
                                                       18px mark, group
                                                       centered, 32pt from
                                                       bottom
```

### macOS — dark (`#0F1419`)

```
┌──────────────────────────────────────────────┐
│                                                │
│                                                │
│                 ╭──────────╮                   │
│                 │ (☎ dial) │                   │
│                 ╰──────────╯                   │
│                                                │
│                                                │
│                                                │
│      powered by (⬡ NM mark @42%, inverted) NativeMind│  <- mark inverted +
└──────────────────────────────────────────────┘     42% (not 32%) for
                                                       legibility on dark bg,
                                                       per the .dc.html
                                                       prototype (checked
                                                       directly, not just
                                                       the README table);
                                                       same inline word
                                                       order as light mode
```

### Android — full-screen, light

```
┌─────────────────────────────┐
│                               │
│                               │
│                               │
│         ╭──────────╮          │
│         │ (☎ dial) │          │  <- centered bitmap layer,
│         ╰──────────╯          │     48dp from bottom of the
│                               │     *icon* layer (per
│                               │     launch_background.xml's
│                               │     layer-list — not the same
│                               │     inset as the footer below)
│                               │
│  powered by (⬡ NM mark) NativeMind│  <- pre-composited into one
│                               │     bitmap (splash_branding.png),
└─────────────────────────────┘     mark inline between the words
                                     (same order as macOS), @ 40%
                                     alpha, 32dp from bottom —
                                     Android's layer-list can't
                                     render live text, so mark+
                                     caption are baked into a
                                     single PNG at build time
```

**API 21–30**: exactly the layer-list above (`launch_background.xml`
already exists in Flutter's default template — this fills in its
commented-out bitmap slot).
**API 31+**: system `SplashScreen` API instead — background color +
`windowSplashScreenAnimatedIcon` (static, `AnimationDuration = 0`) +
the one system-provided `windowSplashScreenBrandingImage` slot at the
bottom. Same visual result where the OEM's firmware honors the
branding slot; **not guaranteed to show on every device** — this is a
real, documented platform limitation from the template's own README,
not something this flow can control. Not a scope reduction: the same
assets are provided either way, some Android 12+ builds just may not
render the bottom slot depending on OEM.

### Dismiss behavior (not a static-frame concern, but part of AC #3)

```
macOS/Linux:  splash window visible ──▶ Flutter first frame painted ──▶
              Dart calls dismissOnFirstFrame() ──▶ 180ms fade-out
              (cubic-bezier(.25,.1,.25,1)) ──▶ main window revealed

Android:      system splash ──▶ Flutter embedding switches
              LaunchTheme → NormalTheme automatically ──▶ no fade,
              no Dart involvement (matches the template's own
              "zero manual work" principle for this platform)
```

---

## Approval

- [x] Reviewed by: Anton Dodonov
- [x] Approved on: 2026-08-24
- [x] Notes: "visual approved"
