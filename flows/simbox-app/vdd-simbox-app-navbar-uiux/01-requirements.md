# Requirements: simbox-app-navbar-uiux

> Version: 1.0 (mobile/tablet nav direction resolved with Anton — native
> chrome per OS, shared adminka-derived icon family everywhere; tablet
> stays width-breakpoint-driven, not a fixed device-type rule)
> Status: APPROVED
> Last Updated: 2026-08-23

## Problem Statement

`apps/simbox-app`'s top-level navigation (four destinations: Каналы,
Модемы, Операции, Настройки — "тот же порядок, что в текстовой
навигации 2015") currently lives in `lib/navigation/{app_shell.dart,
breakpoints.dart}`, built as part of `vdd-simbox-app-uiux`'s Task 3. It
uses generic Flutter chrome at every breakpoint: `NavigationBar`
(bottom tab bar) on phone, `NavigationRail` (compact then extended) on
tablet/desktop — all with plain Material icons, not the product's own
iconography.

Two things are being extracted/settled here, at Anton's explicit
request:

1. **All navbar-specific requirements/visual/specs/plan/implementation
   content currently split across `vdd-simbox-app-uiux`'s five
   documents** (Problem Statement's nav-order line, AC #5's "bottom tab
   bar vs. left rail" clause, `02-visual.md`'s Navigation Map and its
   bottom-tab-bar/left-rail rows in the Design-System token table,
   `04-plan.md`'s Task 3, `05-implementation-log.md`'s Task 3 entry) —
   moves here, the same extraction pattern already used for
   `vdd-simbox-app-channel-table-uiux`. `vdd-simbox-app-uiux` keeps
   only the four screens' own content (what's *inside* each tab), not
   the tab bar/rail chrome itself.
2. **Desktop/web must match `design/nativemind-designsystem-v1.8`'s
   `templates/gostsimbox-admin/` navigation exactly** — same design,
   same icons — for conservative users. Read the actual template
   (`GostSimBoxAdmin.dc.html`) directly rather than inferring from the
   readme: its real desktop nav is a **sticky top header** (device
   identity: hostname, IP, build, live clock/uptime) followed by a
   **horizontal row of icon+label tab buttons** sourced from
   `assets/adminka/` (`t.icon`/`t.label` per tab), where the active tab
   renders as a brand-tint pill (`rgba(0,91,234,.09)` background,
   `#005BEA` icon+text, 600-weight) and idle tabs are transparent with
   grey text and a 75%-opacity icon (hover → light grey wash). This is
   a materially different chrome from the generic `NavigationRail`
   currently shipped — replacing it is the concrete ask, not a
   restyle of the rail.

## Note: what stays in `vdd-simbox-app-uiux`

Per-screen content (Каналы/Модемы/Операции/Настройки's own layouts,
lists, tables, forms) is unaffected and stays documented there. Only
the **shell around** those screens — which destinations exist, in what
order, and how the shell itself renders per breakpoint — moves here.

## User Stories

**As a** simbox-app user on desktop/web
**I want** the navigation chrome to look like the GostSimBox-admin
panel I already know (same icons, same tab-pill styling, same sticky
device-identity header)
**So that** the modern app doesn't feel like a different, unfamiliar
product — a direct ask for **conservative users** who are used to the
2015-era look.

**As a** simbox-app support agent
**I want** navigation labels, order, and icon meaning to be identical
across platforms
**So that** I can tell a customer "tap the modem icon" or "second tab
from the left" over the phone and have it be correct regardless of
whether they're on iPhone, Android, iPad, or desktop — resolved via
the Resolved Design section below (native chrome per OS, shared icon
family/labels/order everywhere).

## Acceptance Criteria

### Must Have

1. **Given** the current `AppShell`/`AppBreakpoints` implementation
   (four destinations, breakpoint-switched chrome)
   **When** this flow's documents are drafted
   **Then** they become the single source of truth for the app's
   top-level navigation shell, superseding the corresponding fragments
   in `vdd-simbox-app-uiux` (which will be trimmed to forward-reference
   here once this flow reaches an approved state, matching the
   `vdd-simbox-app-channel-table-uiux` precedent).

2. **Given** `design/nativemind-designsystem-v1.8/templates/
   gostsimbox-admin/GostSimBoxAdmin.dc.html`'s real sticky-header +
   icon-label-tab-row pattern (read directly, not inferred)
   **When** the desktop/web navigation shell is (re)built
   **Then** it adopts that exact chrome: sticky top bar with device
   identity, horizontal tab row using `assets/adminka/` icons (not
   Material icons), active-tab brand-tint pill, idle-tab grey/
   75%-opacity treatment, hover wash — replacing `NavigationRail` on
   desktop/web. Tab **set** stays this app's own four destinations
   (Каналы, Модемы, Операции, Настройки), not the legacy panel's
   eleven — only the chrome/styling is adopted, not the legacy tab
   list.

3. **Given** the 2026 prototype's documented "same order as 2015 text
   nav" requirement (already settled in `vdd-simbox-app-uiux`)
   **When** any platform's nav is built (this flow or otherwise)
   **Then** destination order and labels stay identical across every
   breakpoint/platform — this was already true in the existing
   `AppShell._destinations` list and is carried forward as a hard
   constraint, not just a phone/desktop convention.

4. **Given** the resolved mobile/tablet discussion below (option 3:
   native chrome, shared icon family)
   **When** the phone/tablet navigation shell is (re)built
   **Then** each OS keeps its native tab-bar shape/interaction model
   (Cupertino-style on iOS, Material `NavigationBar` on Android) — no
   single custom cross-platform widget — but every platform (phone,
   tablet, desktop/web alike) uses the **same `assets/adminka/`-derived
   icon glyphs** and **identical destination labels/order**, not each
   OS's default icon set. This is what actually satisfies the support
   team's cross-platform-describability requirement: "the icon that
   looks like a modem" (or the tab in the same position, same label)
   means the same thing regardless of which device someone is holding.

5. **Given** the current `AppBreakpoints` width-based logic (phone <
   760, tablet 760–1024, desktop ≥ 1024) already produces a
   size-dependent chrome split rather than a fixed device-type rule
   **When** tablet nav chrome is decided
   **Then** that existing logic is kept and made explicit/intentional
   (not silently inherited): a narrow/portrait tablet gets phone-style
   bottom-tab chrome, a wide/landscape tablet or desktop-class window
   gets the GostSimBox-admin-style top nav from AC #2 — driven by
   available width, not by "this is an iPad" as a device check.

## Won't Have (This Iteration)

- Redesigning which four destinations exist, or their icons'
  *meaning* — only the chrome/styling around them.
- Rebuilding the legacy panel's own eleven-tab nav — reference for
  styling only, per AC #2.
- Anything about the screens' own internal content — stays in
  `vdd-simbox-app-uiux`.

## Constraints

- **Design source of truth for desktop/web**: the real
  `GostSimBoxAdmin.dc.html` template markup (confirmed via direct read,
  including its `tabDefs`/rendering logic), not just the readme's
  prose summary of it.
- **Icon source**: `design/nativemind-designsystem-v1.8/assets/
  adminka/` — vendor per-glyph as used, same rule as the rest of the
  app (per `vdd-simbox-app-uiux`'s existing asset-vendoring
  constraint).
- **Sequencing**: this flow does not touch `apps/simbox-app`'s screen
  content, only `lib/navigation/`. Can proceed independently of
  `vdd-simbox-app-channel-table-uiux`'s own remaining work.

## Resolved Design (discussed with Anton, 2026-08-23)

- **Mobile/tablet nav approach**: option 3 from the discussion — native
  chrome per OS (Cupertino-style tab bar on iOS, Material
  `NavigationBar` on Android), but a shared `assets/adminka/`-derived
  icon family and identical labels/order across every platform
  (phone/tablet/desktop/web alike). Rejected: a single pixel-identical
  custom widget (fights native conventions) and native-chrome-with-
  platform-default-icons (describability would rely on position/label
  alone, weaker than shared icons).
- **Tablet nav shape**: stays width-breakpoint-driven (the existing
  `AppBreakpoints` logic), not a fixed "this is an iPad" device-type
  rule — narrow/portrait tablet gets phone-style bottom-tab chrome,
  wide/landscape tablet or desktop-class window gets the
  GostSimBox-admin-style top nav. This was already how
  `AppBreakpoints.isTablet`/`isDesktop` worked; Anton confirmed it
  intentionally rather than leaving it as an inherited default.

See Acceptance Criteria #4 and #5 above for how these translate into
requirements.

## References

- `apps/simbox-app/lib/navigation/app_shell.dart`,
  `breakpoints.dart` — current implementation being extracted/revised.
- `design/nativemind-designsystem-v1.8/templates/gostsimbox-admin/
  GostSimBoxAdmin.dc.html` — real desktop nav markup (sticky header +
  icon-label tab row, `tabDefs`, active/idle pill styling).
- `design/nativemind-designsystem-v1.8/assets/adminka/` — icon source.
- `flows/simbox-app/vdd-simbox-app-uiux/` — parent flow, source of the
  extracted navbar content (trimmed as part of this flow's approval).
- `flows/simbox-app/vdd-simbox-app-channel-table-uiux/` — sibling
  extraction, same pattern (precedent for how the "move, not copy"
  split was done and documented).

---

## Approval

- [x] Reviewed by: Anton Dodonov
- [x] Approved on: 2026-08-23
- [x] Notes: Mobile/tablet direction resolved (2026-08-23, see Resolved
      Design). Approved as-is ("reqs approved").
