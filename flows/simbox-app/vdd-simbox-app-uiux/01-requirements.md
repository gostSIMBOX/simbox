# Requirements: simbox-app-uiux

> Version: 1.5 (v1.4's navigation-shell/tab-bar content **extracted
> 2026-08-23 into `vdd-simbox-app-navbar-uiux`** at Anton's explicit
> instruction: "вынеси из vdd-simbox-app-uiux все про navbar" — this
> document reverts to describing this flow's own screen-content scope,
> with a forward reference where the nav-chrome clause used to be. The
> earlier "Каналы" table extraction into `vdd-simbox-app-channel-table-
> uiux` still stands, unaffected by this second extraction.)
> Status: APPROVED
> Last Updated: 2026-08-23

## Problem Statement

`apps/simbox-app` is currently pre-refactor scaffolding: `lib/` only has
`l10n/`, `theme/`, `utils/`, and a `main.dart` with a single inline demo
`DashboardScreen` (app title "GOSTsimbox Gateway"). There is no real
screen/widget structure yet. A 2026 design prototype exists at
`design/simbox-app-maket-v2026` (two interactive `.dc.html` click-through
files, responsive across phone/iPad/desktop) defining the target UI:
Симки (SIM list — **later renamed to "Каналы"/Channels and given a
dual view mode/table-view toggle by `vdd-simbox-app-channel-table-uiux`,
see the note below**), Модемы (modems/USB hub), Звонки (calls), СМС, Настройки,
network/diagnostics console, and an engineering-vs-normal mode toggle — an
explicit modernization of the 2015 desktop app's navigation, not a redesign
from scratch ("тот же порядок, что в текстовой навигации 2015").

Separately, `design/nativemind-designsystem-v1.8` is NativeMind's
product-agnostic design system (tokens, components, fonts) used across the
VPN Client family, TaxLien.online, the marketing portal, **and explicitly
documents `templates/gostsimbox-admin/` as the reference dense-table
pattern for this exact product** — a live recreation of the 2015 telephony
admin panel's SIM table, with its own token layer (`tokens/web.css`:
`--adm-row-odd/even`, `--adm-head-bg`, `--adm-row-sel`, `--adm-cell-pad`,
stacked-cell ink hierarchy, icon-only column headers) and a 224-file
telephony-specific icon set (`assets/adminka/`: `state/{cfun,simst,srvst,
end_party}`, `qos/`, `spec/`, `recog_types/`, `rssi/`, `napravleine/`
[operators], `usb/`, `tree/`, balance/SMS/dongle/day/playback icons), with
`assets/fugue/` as the documented fallback set.

This flow refactors `apps/simbox-app`'s UI to match the 2026 prototype's
screens/flows/breakpoints while building every surface out of the
NativeMind design system's tokens and components (not ad-hoc styling),
using the dense-table + adminka icon pattern specifically for the SIM/modem
tables, per the user's explicit instruction to use
`design/nativemind-designsystem-v1.8`.

## Note: "Симки" → "Каналы" work moved out (2026-08-23)

During this flow, a clarifying question about a table-view toggle grew
into a full screen redesign (rename to "Каналы", dual view mode,
expandable rows) — captured at the time as this document's AC #8 and a
CRITICAL permanent product note (a verbatim exchange with Anton). At
Anton's explicit instruction, **all of that content has been extracted
into its own flow, `vdd-simbox-app-channel-table-uiux`**, unchanged —
see that flow's `01-requirements.md` for the full verbatim record,
resolved design, and acceptance criteria. This document now describes
only this flow's own original scope (Tasks 1-13: navigation shell,
theme, base screens including the SIM-list screen as originally
built — desktop dense table + phone/tablet card view, no toggle, no
dual mode). The Симки/Каналы screen described below is that original
scope; do not reintroduce the extracted content here — it now lives
solely in the other flow to avoid two sources of truth diverging.

## User Stories

### Primary

**As a** simbox-app user (SIM-box operator)
**I want** a desktop-first (Linux now, Windows/macOS later) app that shows
my SIMs, modems, calls, and SMS in a dense, information-rich but calm
interface consistent with NativeMind's other products
**So that** I can monitor and control many devices at once without the
visual clutter of the 2015 PHP admin panel, while keeping the operational
detail (balance, quality, operator, state icons) that panel had.

**As a** simbox-app developer
**I want** the UI built from `nativemind-designsystem-v1.8` tokens and
components (colors, typography, spacing, dense-table pattern, adminka +
fugue icon sets) rather than one-off Flutter theming
**So that** the app is visually consistent with the rest of NativeMind's
product line and easy to re-skin/maintain.

### Secondary

**As a** simbox-app user on tablet/phone
**I want** the same screens to adapt per the prototype's documented
breakpoints (390/844 phone, 760–1024 iPad, 1440 desktop — "six layouts of
one screen")
**So that** the app is usable for quick checks away from the desktop.

**As a** power user
**I want** an "engineering mode" (per the prototype's Инженерный/Основной
режим toggle) exposing the raw AT-command console/diagnostics
**So that** I can troubleshoot modems directly without leaving the app.

## Acceptance Criteria

### Must Have

1. **Given** the 2026 prototype's `.dc.html` files (no machine-readable
   manifest)
   **When** the VISUAL phase begins
   **Then** both files are opened/rendered directly (browser) and every
   distinct screen/state is enumerated and translated into ASCII mockups in
   `02-visual.md` — at minimum: Симки (list + empty/filtered/bulk-select
   states), Модемы (hub/port console + reboot/firmware states), Звонки
   (call log + start-call + ring states), СМС (compose + delivery states),
   Настройки (form + unsaved-changes banner + validation-error states),
   diagnostics console, engineering-mode toggle, and any auth/plan-change/
   low-balance banner states found in the prototype.

2. **Given** `nativemind-designsystem-v1.8/tokens/{colors,typography,
   spacing,fonts,web}.css`
   **When** the Flutter theme layer is (re)built in `apps/simbox-app/lib/
   theme/`
   **Then** the existing `app_colors.dart`/`app_dimensions.dart`/
   `app_gradients.dart`/`app_theme.dart` are reconciled against these
   tokens (4-pt spacing scale, SF Pro Text type roles, single soft shadow
   `0 1px 32px rgba(156,178,194,0.10)`, 10px card radius, Blue accent
   `#00C6FB → #005BEA` as default) so values are sourced from the DS, not
   invented independently.

3. **Given** the DS's explicit "GOSTSIMBOX-ADMIN — DENSE TABLE" guidance
   and `templates/gostsimbox-admin/`
   **When** the Симки (SIM list) and Модемы (device list) screens are
   specified/built
   **Then** they follow the documented dense-table rules: brand-tint zebra
   (not grey), icon-only column headers (16px glyph + 11px label),
   stacked-cell ink hierarchy (primary/secondary/tertiary/alarm), icon
   stacks for status (captcha/multi-SIM/spec/direction/quality/operator),
   CSS-grid-equivalent fixed-column layout adapted to Flutter (e.g.
   `Table`/`DataTable`/custom grid with pinned columns + one scroller), and
   use `assets/adminka/` icons for state (cfun/simst/srvst/qos/spec/
   napravleine operator marks/rssi) with `assets/fugue/` (2× set) as
   fallback for any state the adminka set doesn't cover.

4. **Given** the existing font/icon assets in `nativemind-designsystem-v1.8/
   assets/{fonts,adminka,fugue}` and `uploads/*.ttf`
   **When** assets are integrated into the Flutter app
   **Then** SF Pro Text TTFs are bundled as the app font, adminka `.ico`/
   `.png` (16×16, nearest-neighbour scaling only — 16/32/48/64px) and
   vendored fugue PNGs (32px source, displayed 16px, sharp scaling) are
   copied into `apps/simbox-app/assets/` per-glyph as used (not the full
   3,570-file sets), matching the DS's own vendoring rule.

5. **Given** the 2026 prototype's responsive breakpoints
   **When** screens are implemented
   **Then** each major screen has phone/tablet/desktop layouts matching the
   prototype's documented adaptations (dense table vs. card view), using
   Flutter's standard responsive patterns (`LayoutBuilder`/breakpoint
   constants derived from the DS spacing tokens). The top-level
   navigation chrome itself (bottom tab bar vs. rail vs. desktop nav)
   that switches on these same breakpoints is specified in
   `vdd-simbox-app-navbar-uiux`, not here — `AppBreakpoints`' width
   thresholds are shared infrastructure both flows read from.

6. **Given** [[sdd-flutter_gsmsip-interface]] defines the new
   `FlutterGsmsipPlatform` API (modem/call/SMS/USSD/group entities, event
   streams) as a prerequisite flow
   **When** this flow's PLAN/IMPLEMENTATION phases are scoped
   **Then** screens are specified against that API's entities/streams
   (state management wired to `flutter_gsmsip`'s new domain types), and
   **implementation does not start until `sdd-flutter_gsmsip-interface`
   has merged, compiling, implemented code** (per explicit user sequencing
   instruction) — this flow may complete REQUIREMENTS/VISUAL/SPECIFICATIONS/
   PLAN phases in parallel, but IMPLEMENTATION is gated on the interface
   flow.

7. **Given** copy/tone rules in the DS readme (Russian-first, sentence
   case, 1–3 word labels, no exclamation marks, no emoji in shipped UI —
   emoji-as-icon is an *adminka-specific legacy exception*, not a rule for
   the new Flutter app)
   **When** UI copy is written
   **Then** it follows the DS's general product tone (calm-utility,
   concise), using real icon assets in the Flutter app rather than emoji,
   even though the old web adminka template uses emoji as a stopgap.

### Should Have

- A written token-mapping table (DS token → Flutter `ThemeData`/custom
  theme extension field) in `03-specifications.md` for traceability and
  future re-skinning.
- Reuse of the DS's "system layer" component vocabulary
  (`Button`/`Switch`/`Checkbox`/`Field`/`ListRow`/`Badge`/`TabBar`) as the
  naming/behavior reference for equivalent Flutter widgets, even though
  they must be reimplemented natively (the DS components are React/HTML).

### Won't Have (This Iteration)

- White-label multi-accent theming (Blue/Green/Orange/Pink) — simbox-app
  ships one accent (Blue) for now; the DS's colorway-switch mechanism is
  noted but not wired up.
- Payment/subscription UI — explicitly out of scope for the DS itself
  ("Billing UI is not in scope for this system yet").
- Any backend/state-management wiring beyond what
  `sdd-flutter_gsmsip-interface`'s API surface supports at the time this
  flow implements (features with no backing API method are stubbed/
  disabled in the UI, not faked).
- Windows/macOS-specific UI chrome — layout should not preclude it, but no
  platform-specific work now (Linux desktop first).
- Rebuilding the legacy PHP `templates/gostsimbox-admin/` web page itself —
  it's a design *reference* for the dense-table pattern, not a target to
  ship; simbox-app is the Flutter app, not the web panel.
- **Dual view mode, expandable rows, table-view-anywhere toggle, and the
  "Симки"→"Каналы" rename** — see `vdd-simbox-app-channel-table-uiux`,
  not this flow.

## Constraints

- **Technical**: Must consume `sdd-flutter_gsmsip-interface`'s API surface
  once implemented; must not implement its own parallel telephony logic.
  See [[sdd-flutter_gsmsip-interface]].
- **Design source of truth**: `design/simbox-app-maket-v2026` governs
  screen inventory, layout, and flow; `design/nativemind-designsystem-v1.8`
  governs tokens, components, fonts, and icon assets — **both are
  mandatory inputs**, per explicit user instruction. Where they conflict
  (e.g. a color or spacing value), the design system's tokens win, since
  it is the documented cross-product source of truth ("when Figma/mockup
  and code/tokens disagree, tokens win" — extending the DS's own stated
  rule for the VPN codebase to this project).
- **Sequencing**: VISUAL/SPECIFICATIONS/PLAN phases may proceed now;
  IMPLEMENTATION phase is gated on `sdd-flutter_gsmsip-interface` reaching
  merged, compiling implemented code. `sdd-flutter_gsmsip-channel` (the
  real ttyUSB driver) is created only after both this flow and the
  interface flow have implemented code — this flow does not need the real
  driver, only the interface's typed API (which may return "no device"/
  "not implemented" until the channel flow lands).
- **Platform**: Linux desktop first (matches `sdd-flutter_gsmsip-interface`
  scope); responsive layout must not break for future Windows/macOS.
- **Assets**: Vendor only the icon glyphs actually used, per-file, into
  `apps/simbox-app/assets/` — do not bulk-copy the full adminka/fugue sets.

## Open Questions

- [ ] Does simbox-app get its own accent color, or does it inherit Blue as
      "the NativeMind default" since it isn't one of the four VPN
      colorways? Recommend Blue (matches Portal's blue too) unless Anton
      specifies otherwise.
- [ ] Should the dense SIM/modem table be a custom Flutter grid widget
      (closest fidelity to the CSS-grid/pinned-column pattern) or
      `DataTable2`/similar package — decide in specifications after
      evaluating Flutter desktop table packages against the DS's exact
      layout requirements (icon-stack columns, stacked-cell ink levels).
- [ ] Confirm whether "Диагностика/консоль" (diagnostics console) in the
      prototype should surface raw AT-command I/O once
      `sdd-flutter_gsmsip-channel` exists, or is UI-only scaffolding for
      now (`execAtCommand` already appears as a Must-Have method in
      [[sdd-flutter_gsmsip-interface]]'s acceptance criteria, so it can be
      wired to the interface even before the real driver exists, returning
      a "no device connected" state).

## References

- `design/simbox-app-maket-v2026/Simbox прототип.dc.html`,
  `Основной экран-ipad,desktop,phone.dc.html` — screen inventory,
  breakpoints, interaction states (research notes: Симки/Модемы/Звонки/СМС/
  Настройки/diagnostics/engineering-mode).
- `design/nativemind-designsystem-v1.8/readme.md` — full DS guidelines
  (colour, type, spacing, elevation, iconography, motion, the
  GOSTSIMBOX-ADMIN dense-table section, the adminka icon taxonomy).
- `design/nativemind-designsystem-v1.8/tokens/` — `colors.css`,
  `typography.css`, `spacing.css`, `fonts.css`, `web.css` (adminka-specific
  dense-table tokens).
- `design/nativemind-designsystem-v1.8/assets/adminka/`,
  `assets/fugue/` — telephony-panel and fallback icon sets.
- `design/nativemind-designsystem-v1.8/guidelines/dense-table.html` —
  dense-table specimen card.
- `design/nativemind-designsystem-v1.8/templates/gostsimbox-admin/` —
  reference recreation of the legacy adminka panel (design reference only,
  not a build target).
- `apps/simbox-app/lib/theme/` — existing (pre-refactor) theme scaffolding
  to reconcile against DS tokens.
- [[sdd-flutter_gsmsip-interface]] — prerequisite API flow (`libs/
  flutter_gsmsip/flows/sdd-flutter_gsmsip-interface/`).
- `vdd-simbox-app-channel-table-uiux` — the "Симки"→"Каналы" rename,
  dual view mode, and table-view-anywhere toggle, extracted from this
  flow 2026-08-23.
- `vdd-simbox-app-navbar-uiux` — the top-level navigation shell/tab-bar
  chrome (destinations, order, breakpoint-switched shell styling,
  desktop GostSimBox-admin-style nav), extracted from this flow
  2026-08-23.

---

## Approval

- [x] Reviewed by: Anton Dodonov
- [x] Approved on: 2026-08-23
- [x] Notes: v1.5 reflects the 2026-08-23 extraction of the "Каналы"
      table/rename work into `vdd-simbox-app-channel-table-uiux` and
      the navigation-shell/tab-bar content into
      `vdd-simbox-app-navbar-uiux` — no new content approval needed
      here, the underlying v1.0 approval for this flow's own
      screen-content scope stands unchanged. The font-asset
      IMPLEMENTATION blocker (shared with both extracted flows)
      remains open — see `_status.md`.
