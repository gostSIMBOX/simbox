# Visual: simbox-app-navbar-uiux

> Version: 1.0 (all three Open Items resolved per stated recommendations)
> Status: APPROVED
> Last Updated: 2026-08-23
> Source: real `design/nativemind-designsystem-v1.8/templates/
> gostsimbox-admin/GostSimBoxAdmin.dc.html` markup (read directly —
> sticky header + `sc-for`-rendered tab row, not inferred from the
> readme's prose summary), plus `apps/simbox-app/lib/navigation/
> {app_shell.dart,breakpoints.dart}`'s current implementation.

## Notation

- `[ ]` unchecked / `[x]` checked selection box
- `( )` circular element / icon placeholder
- `‹ ›` back/forward chevrons
- Icon placeholders: `(sim)` `(modem)` `(call)` `(gear)` — refer to the
  shared adminka-derived icon family this flow adopts for all four
  destinations (Каналы/Модемы/Операции/Настройки), on every platform.
- `━━━` pill/active-state highlight; `┈┈┈` hairline separator

## Where This Fits

This flow owns the **shell around** the four screens (Каналы, Модемы,
Операции, Настройки) — which destinations exist, their order, and how
the chrome that switches between them renders per breakpoint/platform.
It does not own what's *inside* each screen — see `vdd-simbox-app-uiux`
(base screens) and `vdd-simbox-app-channel-table-uiux` (Каналы's dual
view mode) for that.

## Navigation Map

```
                    ┌───────────────────────────────────────┐
                    │              simbox-app                │
                    └───────────────────────────────────────┘
   Destinations (2015 text-nav order preserved, identical on every
   platform per AC #3): Каналы · Модемы · Операции · Настройки
   "Модемы" expands to: Хабы / Линии    "Операции" expands to: Звонки / СМС

  Chrome varies by width, not by device type (AC #5):
   < 760px  → native bottom tab bar (phone-class canvas)
   760–1024 → native bottom tab bar (tablet-class canvas, same chrome
              as phone — more vertical room, not a different pattern)
  ≥ 1024px  → GostSimBox-admin-style sticky top nav (desktop/web/
              landscape-tablet-class canvas)

  Every destination's icon, label, and position are identical across
  all three — only the container chrome (bottom bar vs. top nav) and
  each OS's native interaction details change (AC #4).
```

---

## Chrome: Desktop / Web (≥ 1024px) — GostSimBox-admin style

Adopts the real template's sticky header + icon-label tab row, not a
generic `NavigationRail`. Read directly from
`GostSimBoxAdmin.dc.html`: sticky top bar (device identity + live
clock/uptime), then a horizontal row of icon+label tab buttons; active
tab is a brand-tint pill, idle tabs are transparent/grey with a
dimmed icon, hover is a light grey wash.

```
┌──────────────────────────────────────────────────────────────────────┐
│(⚡) simbox-a4   10.42.0.17   SimBox 8f3c1a2+        12:04:11  up 41д 6:12│ <- sticky, 40px z-index,
├──────────────────────────────────────────────────────────────────────┤    box-shadow 0 1px 32px
│ ┌────────────┐  ( modem)Модемы   ( call)Операции   ( gear)Настройки    │    rgba(156,178,194,.14)
│ │(sim)Каналы │                                                        │
│ └────────────┘                                                        │
├──────────────────────────────────────────────────────────────────────┤
│                                                                        │
│                         ‹ active screen content ›                     │
│                                                                        │
└──────────────────────────────────────────────────────────────────────┘
```
- Active tab (`Каналы` above): `rgba(0,91,234,.09)` background pill,
  `#005BEA` icon + 600-weight text, 8px radius, `7px 12px` padding —
  exact values from the template's `t.active` branch.
- Idle tabs: transparent background, `#546675` text (400-weight),
  icon at 75% opacity; hover → `rgba(156,178,194,.14)` wash — exact
  values from the template's `t.idle` branch.
- Device-identity strip (hostname/IP/build/clock/uptime) is **kept**
  from the template even though simbox-app isn't itself the box being
  administered the way the legacy panel was — it still reports which
  simbox-app instance/build the operator is looking at, which is
  useful context for conservative users used to seeing it there.
  *(Open Item — confirm with Anton, see below.)*
- Only 4 tabs here vs. the legacy panel's 11 — set stays simbox-app's
  own destinations (per AC #2/#3), only the *chrome* is adopted.

---

## Chrome: Phone (< 760px) and Tablet (760–1024px) — native per OS

Same width-driven chrome for both ranges (AC #5) — a native bottom tab
bar, not a side rail. Each OS keeps its own native shape/interaction
model; only the icon family, labels, and order are shared (AC #4).

### iOS (Cupertino-style)
```
┌─────────────────────────────────────┐
│ ‹  Каналы                             │
├─────────────────────────────────────┤
│                                        │
│         ‹ active screen content ›     │
│                                        │
├─────────────────────────────────────┤
│  (sim)   (modem)   (call)   (gear)    │ <- hairline top border, no
│ Каналы   Модемы   Операции  Настройки │    background pill; icon
└─────────────────────────────────────┘    18pt above 10pt label,
                                            selected = brand blue tint
                                            on icon+label, unselected
                                            = grey — iOS convention,
                                            not a custom widget
```

### Android (Material `NavigationBar`)
```
┌─────────────────────────────────────┐
│  Каналы                          (⋮) │
├─────────────────────────────────────┤
│                                        │
│         ‹ active screen content ›     │
│                                        │
├─────────────────────────────────────┤
│  ┌────┐                               │
│  │(sim)│  (modem)   (call)   (gear)   │ <- Material pill indicator
│  └────┘                               │    behind the selected
│ Каналы   Модемы   Операции  Настройки │    icon, ripple on tap —
└─────────────────────────────────────┘    Android convention
```

Both use the **same four icon glyphs** (`(sim)` `(modem)` `(call)`
`(gear)` — adminka-derived, see Design-System mapping below), the same
labels, and the same left-to-right order as the desktop tab row. This
is what actually delivers the support-team requirement: a customer on
iOS and one on Android can both say "tap the phone-handset icon"
(Операции) and mean the same thing, even though the surrounding chrome
looks different.

### Tablet at 760–1024px uses this same phone-style chrome
```
┌───────────────────────────────────────────────────┐
│ ‹  Каналы                                            │
├───────────────────────────────────────────────────┤
│                                                       │
│              ‹ active screen content, wider ›        │
│                                                       │
├───────────────────────────────────────────────────┤
│   (sim)     (modem)     (call)     (gear)            │
│  Каналы     Модемы     Операции    Настройки         │
└───────────────────────────────────────────────────┘
```
Same bottom-bar pattern as phone, just a wider canvas above it — no
side rail at this width. This is a **behavior change** from the
current implementation (today, 760–1024px gets a compact
`NavigationRail`, not a bottom bar) — flagged explicitly, see Open
Items.

---

## Design-System Token/Component Mapping

| Chrome element | Source |
|---|---|
| Desktop/web sticky header + icon-label tab row, active pill, idle/hover states | `design/nativemind-designsystem-v1.8/templates/gostsimbox-admin/GostSimBoxAdmin.dc.html` (read directly — exact colors/padding above) |
| Shared tab icon family (Каналы/Модемы/Операции/Настройки, all platforms) | `design/nativemind-designsystem-v1.8/assets/adminka/` — vendor 4 glyphs (or the closest adminka concept per destination — see Open Items) |
| iOS bottom tab bar shape/interaction | Cupertino native convention (`CupertinoTabBar` or Material's adaptive equivalent) — chrome only, icons/labels shared per above |
| Android bottom tab bar shape/interaction | Material `NavigationBar` (already used today) — chrome only, icons/labels shared per above |
| Device-identity strip (desktop) | `assets/adminka/power.png` + plain text, per the template |

---

## Resolved Items (approved as drafted, 2026-08-23)

Anton approved this document without overriding any of the three open
items, so the stated recommendations stand as the design:

- [x] **Device-identity strip on desktop**: keep a **simplified**
      version — app name + version + local clock — not the legacy
      panel's full hostname/IP/uptime set, since simbox-app is the
      operator's own client app, not a per-device admin page.
- [x] **Icon approach per destination**: draw **4 new simple icons**
      in the DS's stroke/weight style (option b/c) rather than
      repurposing adminka status glyphs — matches the DS's own
      precedent for this exact problem (the VPN app's custom
      single-path bottom-nav SVGs).
- [x] **Tablet chrome change accepted**: 760–1024px moves from
      `NavigationRail` to the native bottom tab bar, same as phone,
      per the width-driven design in `01-requirements.md`.

---

## Approval

- [x] Reviewed by: Anton Dodonov
- [x] Approved on: 2026-08-23
- [x] Notes: "visual approved" — all three Open Items resolved per the
      stated recommendations above (Resolved Items section).
