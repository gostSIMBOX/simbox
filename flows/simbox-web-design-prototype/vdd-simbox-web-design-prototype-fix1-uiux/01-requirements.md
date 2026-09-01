# Requirements: simbox-web-design-prototype-fix1-uiux

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-09-01

## Problem Statement

`design/simbox-web-design-prototype-v2026` is a Flutter web re-implementation of the legacy
SimBox admin panel (`legacy/simbox-desktop-v2014/www/simbox`). Its current shell layout has four
structural problems compared to the already-approved target design in
`design/simbox-design-prototype-v2026-dc/index.html` ("the -dc mock"):

1. Navigation is a horizontal tab strip under the top status bar (wraps to multiple rows once
   all 11 sections are shown), instead of a left sidebar that can collapse to icons-only.
2. The logo is not used as a UI control — there is no compact/full toggle, and the specific
   brand asset (`design/logo_wide_transparent.png` / `design/logo_transparent.png`) isn't wired
   in at all (the -dc mock uses placeholder `logo_wide.png` / `logo_square.png`).
3. Per-page action panels (transmitter, simple actions, smart actions, groups/plans, export,
   dongle actions, PIN, modes, firmware, hub power, etc.) render as a `Wrap` **below** the data
   table, all simultaneously visible — pushing the table down and requiring a scroll to reach
   both the table and the actions on smaller viewports.
4. The data table scrolls as part of the whole page (`SingleChildScrollView` wraps table +
   actions together in `main.dart`/`sims_page.dart`), so the column header scrolls out of view
   on long lists (e.g. many SIMs) instead of staying pinned.

The `-dc` mock already demonstrates the target interaction pattern (left rail with
compact/full toggle on logo click, table with `position:sticky` header, action groups collapsed
into toggle-pill buttons that open a single overlay panel). This flow ports that pattern into
the Flutter prototype, swaps in the correct brand logo assets, and verifies against the legacy
PHP admin (`legacy/simbox-desktop-v2014/www/simbox`) that no action/field/log-item is dropped in
the process — the legacy app is the source of truth for *what functionality must exist*, the
`-dc` mock is the source of truth for *how it should look and be organized*.

## User Stories

### Primary

**As an** operator running many SIM boxes from a laptop or a narrow browser window
**I want** the navigation collapsed to icons and the row actions tucked into an on-demand panel
**So that** the SIM/dongle table gets maximum horizontal and vertical space, while every action
from the legacy panel stays reachable in at most two clicks

### Secondary

**As an** operator scanning a long SIM table
**I want** the column header to stay pinned while I scroll through rows
**So that** I don't lose track of which column (of ~30 dense columns) I'm looking at

**As an** operator who prefers the full navigation with labels
**I want** to toggle back to the labeled sidebar at will
**So that** I can orient myself when I'm less familiar with the icon set

## Acceptance Criteria

### Must Have

1. **Given** the app loads for the first time
   **When** the shell renders
   **Then** the top horizontal nav tab strip (`TopBar`'s `Wrap` of `_TabButton`s) is gone,
   replaced by a left-hand vertical sidebar listing the same 11 sections (Симки, Свистки (nm),
   Свистки (um), Хабы, Наборы команд, Планы, Процессы, Биллинг, Обновление, Debug, Иконки), in
   the same order, each still navigating via `AppState.goTo`.

2. **Given** the sidebar is in full mode
   **When** the user clicks the logo at the top of the sidebar
   **Then** the sidebar collapses to a fixed icon-only rail (~64px wide, matching the -dc mock's
   `navW`/`navJustify` behavior) and the logo image swaps from the wide/rectangular asset
   (`design/logo_wide_transparent.png`) to the compact/square asset
   (`design/logo_transparent.png`); clicking again reverses both changes. No other control
   toggles this state (single, discoverable affordance, matching req. #4 in the request).

3. **Given** the sidebar is collapsed (icon-only)
   **When** the user hovers or focuses a nav icon
   **Then** the section label is still available (tooltip, matching the mock's `title="{{ t.label }}"`)
   so the icon-only mode stays identifiable, not just decorative.

4. **Given** a page that has row/selection actions (Sims, Dongles, Diagmode/Свистки um, Hubs —
   the four pages that currently render a `TableHeaderBar` + action `Wrap` below the table)
   **When** the page renders
   **Then** the actions are no longer a `Wrap` below the table; instead each action group
   (e.g. "Передатчик и статус", "Действия простые", "Действия хитрые", "Группы и планы",
   "Экспорт / Импорт", plus any per-page groups such as dongle/PIN/modes/firmware/hub-power
   actions) is represented by a toggle-pill button placed in the table's header bar, to the
   right of the row count / selection chip.

5. **Given** the table header bar
   **When** the user clicks one action-group pill
   **Then** exactly one group's panel opens as an overlay directly below the header bar
   (absolutely positioned so it does not push the table down), showing that group's fields and
   buttons; clicking the same pill again, or clicking a different pill, closes/replaces it.
   Reaching any individual action therefore takes at most two clicks: one to open its group,
   one to trigger it (matching request #5 — grouped so accessible in 2 clicks instead of the
   current 1-click/always-visible layout).

6. **Given** a scrollable data table (Sims, Dongles, Diagmode, Hubs pages)
   **When** the user scrolls the table body
   **Then** the column header row stays pinned at the top of the table (CSS `position:sticky`
   equivalent — a fixed header widget outside the scrolling row list), and only the row content
   scrolls. The outer page must not add a second, competing scroll container around the table.

7. **Given** any page (including non-tabular ones: Наборы, Планы, Процессы, Биллинг,
   Обновление, Debug, Иконки)
   **When** it renders inside the new shell
   **Then** it still receives the same `AppState` data/actions it does today — this is a shell
   layout change, not a data/behavior change. No action, field, tooltip, or log line documented
   in the legacy PHP admin (`legacy/simbox-desktop-v2014/www/simbox`) or already present in the
   current Flutter prototype may be silently dropped.

8. **Given** the bottom "Вывод команд" (`CommandLog`) console
   **When** the shell is restructured
   **Then** it remains a bottom-docked, collapsible console spanning the content area (unchanged
   behavior) — out of scope for this fix beyond adjusting its position under the new
   sidebar+content layout.

9. **Given** the two provided logo assets
   **When** they are added to the Flutter project
   **Then** `design/logo_wide_transparent.png` is used in full/expanded sidebar mode and
   `design/logo_transparent.png` is used in compact/collapsed mode, both rendered at a size
   consistent with the -dc mock's proportions (~30px tall wide logo, ~34×34 square logo),
   scaled for the app's actual sidebar header height.

### Should Have

- Reuse the -dc mock's action-group pill visual treatment (open = filled brand-tint pill with
  ▲, closed = outline pill with ▼) rather than inventing a new toggle affordance.
- Sidebar collapse/expand state persists only for the session (in `AppState`), no persistence
  requirement across reloads unless trivial to add.
- Keep the existing top status strip (device name/IP/version/clock/uptime) as-is, just re-flow
  it into the content column now that nav no longer lives above it.

### Won't Have (This Iteration)

- No changes to the underlying data model, `AppState`, mock data, or icon catalog.
- No new pages/sections beyond the 11 that exist today.
- No responsive/mobile breakpoint work beyond what's needed for the sidebar and sticky header
  (no hamburger menu, no bottom nav for phones).
- No change to the `CommandLog` console's own internal behavior (open/closed, clear) — only its
  position in the new shell.
- No design-token/color/typography changes — token values in `lib/design/tokens.dart` stay as
  they are; this flow is layout/structure only.

## Constraints

- **Technical**: Flutter web app under `design/simbox-web-design-prototype-v2026`; must keep
  using `AppState`/`AppScope` (`lib/state/app_state.dart`) for page routing and selection state
  — extend it rather than replacing it.
- **Design source of truth**: `design/simbox-design-prototype-v2026-dc/index.html` for visual
  structure/interaction (sidebar, action pills, sticky header). Deviate only where the user's
  explicit numbered instructions differ (logo asset choice) or where the -dc mock is silent.
- **Logic source of truth**: `legacy/simbox-desktop-v2014/www/simbox` (PHP) for what actions,
  fields, and log content must exist per page — old visual styling is *not* authoritative, only
  the functional inventory (`head.php` nav list, `sim.php`/`dongle.php`/etc. action forms).
- **Assets**: exact files `design/logo_wide_transparent.png` and `design/logo_transparent.png`
  must be copied into the Flutter project's asset folder and registered in `pubspec.yaml`.
- **Scope**: this is fix #1 on top of the existing prototype — a shell/layout refactor, not a
  rebuild. Existing page bodies (column definitions, mock data, icon mapping) are reused as-is.

## Open Questions

- [ ] Should the 4 non-tabular-but-action-heavy pages (Планы, Процессы, Обновление, Debug) also
  gain the pill/overlay action-group treatment, or do they keep their current always-visible
  `Panel` layout since they have no competing table/header-bar to declutter? (Leaning: leave
  them as-is — the request's "actions below → panel above" complaint is about the *table*
  pages; confirm before Specifications.)
- [ ] Exact collapsed sidebar width and full sidebar width — mock uses 64px / 208px; confirm
  these are fine for the Flutter port or should be adjusted to fit the existing dense-table
  column widths.
- [ ] Default sidebar state on first load: full (labeled) or compact (icons)? Mock's initial
  state is `navOpen: true` (full) — proposing to match.

## References

- `design/simbox-design-prototype-v2026-dc/index.html` — target visual/interaction mock (source
  of truth for design)
- `legacy/simbox-desktop-v2014/www/simbox/head.php` — legacy nav section list (source of truth
  for logic/inventory)
- `design/simbox-web-design-prototype-v2026/lib/` — current Flutter prototype being fixed
- `design/logo_wide_transparent.png`, `design/logo_transparent.png` — new brand logo assets

---

## Approval

- [ ] Reviewed by: Anton Dodonov
- [ ] Approved on:
- [ ] Notes:
