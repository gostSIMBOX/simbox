# Implementation Plan: simbox-web-design-prototype-fix1-uiux

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-09-01
> Specifications: [03-specifications.md](03-specifications.md)

## Summary

Six phases, in dependency order: (1) bring in the logo assets, (2) extend `AppState`, (3) build
the new `Sidebar` + restructure `main.dart`'s shell, (4) make `DenseTable` sticky-header, (5)
build the `ActionGroupBar`/pill/overlay component and wire it into the 4 table pages, (6) give
the 7 non-table pages their own scroll wrapper. Phases 3–6 are independent of each other once
phase 2 lands, so they can be done in any order, but are listed in the order that keeps the app
buildable/runnable after each step (verify-as-you-go, per the repo's own convention of no
automated tests — manual `flutter run` checks after each phase).

## Task Breakdown

### Phase 1: Assets

#### Task 1.1: Add brand logo assets
- **Description**: Copy the two logo files into the Flutter project and register them.
- **Files**:
  - `design/simbox-web-design-prototype-v2026/assets/brand/logo_wide_transparent.png` - Create (copy of `design/logo_wide_transparent.png`)
  - `design/simbox-web-design-prototype-v2026/assets/brand/logo_transparent.png` - Create (copy of `design/logo_transparent.png`)
  - `design/simbox-web-design-prototype-v2026/pubspec.yaml` - Modify (add `- assets/brand/` under `flutter: assets:`)
- **Dependencies**: None
- **Verification**: `flutter pub get` succeeds; a throwaway `Image.asset('assets/brand/logo_wide_transparent.png')` renders without the `errorBuilder` fallback firing.
- **Complexity**: Low

### Phase 2: State

#### Task 2.1: Extend AppState with nav + action-group state
- **Description**: Add `navCompact`/`toggleNav()`, `activeGroup`/`toggleGroup()`, and clear `activeGroup` in `goTo()`.
- **Files**:
  - `design/simbox-web-design-prototype-v2026/lib/state/app_state.dart` - Modify
- **Dependencies**: None
- **Verification**: Existing app still compiles/runs unchanged (new fields are additive, default `navCompact=false`, `activeGroup=null` preserve today's visible behavior until the UI wires them up).
- **Complexity**: Low

### Phase 3: Shell (Sidebar)

#### Task 3.1: Split `top_bar.dart` into `status_bar.dart` + `sidebar.dart`
- **Description**: Move the device/IP/clock strip into a new `StatusBar` widget (content unchanged, just the container it lives in). Build the new `Sidebar` widget: logo header (tap → `st.toggleNav()`, swaps `logo_wide_transparent.png` ↔ `logo_transparent.png`), vertical list of `NavItem`s reusing the existing `_tabs` constant, each item icon + optional label (`if (!st.navCompact)`), always-on `Tooltip` with the label, active-state styling matching the current `_TabButton`'s highlight (`T.rowSel` bg, `T.brandDeep` text).
- **Files**:
  - `design/simbox-web-design-prototype-v2026/lib/widgets/status_bar.dart` - Create
  - `design/simbox-web-design-prototype-v2026/lib/widgets/sidebar.dart` - Create
  - `design/simbox-web-design-prototype-v2026/lib/widgets/top_bar.dart` - Delete (fully superseded)
- **Dependencies**: Task 1.1 (logo assets), Task 2.1 (`navCompact`/`toggleNav`)
- **Verification**: Manual — sidebar renders all 11 items in order, active item highlighted, logo click toggles width/labels/logo image, tooltip shows on compact-mode hover.
- **Complexity**: Medium

#### Task 3.2: Restructure `AdminShell` in `main.dart`
- **Description**: Change `AdminShell.build()` from `Column(TopBar, Expanded(SingleChildScrollView(_page)), CommandLog)` to `Row(Sidebar, Expanded(Column(StatusBar, Expanded(_page(s.page)), CommandLog)))`. Remove the shared outer `SingleChildScrollView` — scrolling becomes each page's own responsibility (table pages get internal table scroll from Phase 4/5; non-table pages get their own wrapper in Phase 6).
- **Files**:
  - `design/simbox-web-design-prototype-v2026/lib/main.dart` - Modify
- **Dependencies**: Task 3.1
- **Verification**: App boots, layout shows sidebar+content+log; non-table pages will visibly lose their padding/scroll until Phase 6 lands in the same work session — acceptable transient state since this is one PR-sized change, not a shipped increment.
- **Complexity**: Low

### Phase 4: Sticky table header

#### Task 4.1: Restructure `DenseTable` for pinned header / scrolling body
- **Description**: Change the internal tree from `Scrollbar > SingleChildScrollView(horizontal) > Column(header, ...rows)` to `Scrollbar > SingleChildScrollView(horizontal) > SizedBox(width: totalWidth, child: Column(header, Expanded(ListView.builder(rows) or Column+Expanded+ListView)))`. Public API (`cols`, `rows`, `idOf`, `isSelected`, `onToggleRow`, `onToggleAll`, `sortKey`, `sortDir`, `onSort`) unchanged. Empty-state message moves inside the scrolling body region.
- **Files**:
  - `design/simbox-web-design-prototype-v2026/lib/widgets/dense_table.dart` - Modify
- **Dependencies**: None (independent of Phase 3)
- **Verification**: Manual — shrink the browser window height with a table page open; header row stays put, only body rows scroll; horizontal scroll still moves header + rows together.
- **Complexity**: Medium (Flutter has no native `position:sticky`; the fixed-header-above-bounded-ListView pattern is the standard workaround — needs a bounded-height ancestor, see Task 5.2/5.3).

### Phase 5: Action-group pills + overlay

#### Task 5.1: Build `ActionGroup` model + `ActionGroupPill` + `ActionGroupOverlay`
- **Description**: New file per Specifications' "New Interfaces" section. Pill visual: closed = outline border + muted text + `▼`; open = brand-tint fill + brand text + `▲` (matches -dc mock and 02-visual.md's Component section). Overlay: `ConstrainedBox(maxHeight: ~60% of viewport)` wrapping a `SingleChildScrollView` wrapping a `Wrap` of the (in practice single, per active key) `Panel` — reuses `Panel` verbatim as the card chrome.
- **Files**:
  - `design/simbox-web-design-prototype-v2026/lib/widgets/action_group_bar.dart` - Create
- **Dependencies**: Task 2.1 (`activeGroup`/`toggleGroup`)
- **Verification**: Unit-less manual check deferred to 5.2 integration (this widget has no page wiring it in yet).
- **Complexity**: Medium

#### Task 5.2: Wire `TableHeaderBar` to accept and render `groups`
- **Description**: Add `groups: List<ActionGroup>` param (default `const []`), render one `ActionGroupPill` per group after the selection chip, before the spacer/search/refresh. `TableHeaderBar` itself doesn't own the overlay (that's the page's `Stack`, Task 5.3) — it only renders the pill row.
- **Files**:
  - `design/simbox-web-design-prototype-v2026/lib/pages/sims_page.dart` - Modify (`TableHeaderBar` class only, at the bottom of the file)
- **Dependencies**: Task 5.1
- **Verification**: Pills render on Sims page once 5.3 supplies `groups` (visually check spacing/wrap against the header bar's existing `Row`).
- **Complexity**: Low

#### Task 5.3: Convert the 4 table pages' actions to `ActionGroup` lists + `Stack` overlay
- **Description**: For each of `sims_page.dart`, `dongles_page.dart`, `diagmode_page.dart`, `hubs_page.dart`: replace the trailing `Wrap(spacing: 18, ..., children: [panelA, panelB, ...])` with a list of `ActionGroup(key: ..., label: ..., icon: ..., builder: (context) => panelA)` (the existing `Panel(...)` widget trees move into these closures **unchanged** — same `Panel` title/icon/width/child, same `AdmButton`/`AdmField`/`onPressed` callbacks). Pass this list into `TableHeaderBar(groups: ...)`. Wrap `DenseTable` (now `Expanded`, per Task 4.1) together with a conditional `Positioned` `ActionGroupOverlay` in a `Stack`, per the Architecture diagram in 03-specifications.md. Group keys to use (matching the -dc mock's `S.grp` values for traceability): Sims → `power, simple, smart, plans, export`; Dongles → `dact, pin, modes`; Diagmode → `fw`; Hubs → `hubpwr`.
- **Files**:
  - `design/simbox-web-design-prototype-v2026/lib/pages/sims_page.dart` - Modify
  - `design/simbox-web-design-prototype-v2026/lib/pages/dongles_page.dart` - Modify
  - `design/simbox-web-design-prototype-v2026/lib/pages/diagmode_page.dart` - Modify
  - `design/simbox-web-design-prototype-v2026/lib/pages/hubs_page.dart` - Modify
- **Dependencies**: Task 4.1, Task 5.1, Task 5.2
- **Verification**: Manual, per Specifications' Manual Verification list — every action group opens via its pill, every button inside fires the same call as before (spot-check toast text/log entry per group), table stays put while a panel is open (no reflow), closing works via same-pill-again and via a different pill.
- **Complexity**: High (four pages, must preserve every existing `onPressed` body verbatim — mechanical but must not drop or mistype a single action).

### Phase 6: Non-table pages get their own scroll

#### Task 6.1: Wrap remaining pages in their own `SingleChildScrollView`
- **Description**: `main.dart` no longer supplies a shared scroll+padding wrapper (Task 3.2). Each of these pages must wrap its existing top-level widget in `SingleChildScrollView(padding: const EdgeInsets.all(22), child: ...)` to preserve today's look exactly.
- **Files**:
  - `design/simbox-web-design-prototype-v2026/lib/pages/nabor_page.dart` - Modify
  - `design/simbox-web-design-prototype-v2026/lib/pages/plan_page.dart` - Modify
  - `design/simbox-web-design-prototype-v2026/lib/pages/proc_page.dart` - Modify
  - `design/simbox-web-design-prototype-v2026/lib/pages/billing_page.dart` - Modify
  - `design/simbox-web-design-prototype-v2026/lib/pages/upgrade_page.dart` - Modify
  - `design/simbox-web-design-prototype-v2026/lib/pages/debug_page.dart` - Modify
  - `design/simbox-web-design-prototype-v2026/lib/pages/icons_page.dart` - Modify
- **Dependencies**: Task 3.2
- **Verification**: Each page visually matches its pre-change padding/scroll behavior when content overflows the viewport.
- **Complexity**: Low (mechanical, 7 near-identical one-line wraps)

## Dependency Graph

```
1.1 ─┬─→ 3.1 ─→ 3.2 ─┬─→ 6.1
     │                │
2.1 ─┴─→ 3.1          │
     └─→ 5.1 ─→ 5.2 ──┴─→ 5.3
                       │
              4.1 ─────┘
```

## File Change Summary

| File | Action | Reason |
|---|---|---|
| `assets/brand/logo_wide_transparent.png` | Create | Full-mode sidebar logo |
| `assets/brand/logo_transparent.png` | Create | Compact-mode sidebar logo |
| `pubspec.yaml` | Modify | Register `assets/brand/` |
| `lib/state/app_state.dart` | Modify | `navCompact`, `toggleNav()`, `activeGroup`, `toggleGroup()`, reset in `goTo()` |
| `lib/widgets/status_bar.dart` | Create | Device/IP/clock strip, split out of old `top_bar.dart` |
| `lib/widgets/sidebar.dart` | Create | New left nav |
| `lib/widgets/top_bar.dart` | Delete | Superseded by `status_bar.dart` + `sidebar.dart` |
| `lib/main.dart` | Modify | New `Row`-based shell, drop shared outer scroll |
| `lib/widgets/dense_table.dart` | Modify | Sticky header / scrolling body |
| `lib/widgets/action_group_bar.dart` | Create | `ActionGroup`, `ActionGroupPill`, `ActionGroupOverlay` |
| `lib/pages/sims_page.dart` | Modify | `TableHeaderBar.groups`, 5 action groups + `Stack` overlay |
| `lib/pages/dongles_page.dart` | Modify | 3 action groups + `Stack` overlay |
| `lib/pages/diagmode_page.dart` | Modify | 1 action group + `Stack` overlay |
| `lib/pages/hubs_page.dart` | Modify | 1 action group + `Stack` overlay |
| `lib/pages/{nabor,plan,proc,billing,upgrade,debug,icons}_page.dart` | Modify | Own `SingleChildScrollView` wrapper |

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| `DenseTable`'s bounded-height requirement isn't met by some caller, causing a Flutter "unbounded height" layout error | Medium | Medium | Every table page already places `DenseTable` inside a `Column` that will become `Expanded` inside a bounded content area (Task 3.2 gives `_page(...)` a bounded `Expanded` slot) — verify each of the 4 pages individually after Task 4.1+5.3 land together |
| Mechanically moving 10 `Panel` blocks into `ActionGroup.builder` closures accidentally drops or alters an `onPressed` body | Low | High (silently breaks an action the legacy panel supports) | Move code verbatim (cut/paste, not retype); Manual Verification checklist in Specifications explicitly spot-checks one action per group |
| Overlay `Positioned` panel overlaps table content awkwardly at small viewport heights | Medium | Low | `ConstrainedBox(maxHeight: ...)` + internal scroll on the overlay, matching the -dc mock's `max-height:60vh;overflow:auto` |
| Deleting `top_bar.dart` breaks an import elsewhere | Low | Low | `grep -rn "top_bar.dart"` before deleting; only `main.dart` imports it today |

## Rollback Strategy

Single-branch, single-PR-sized change with no external consumers or persisted data — if
implementation needs to be reverted, `git revert` the commit(s) or `git checkout` the prior
state of the affected files listed above. No data migration to undo.

## Checkpoints

After each phase:

- [ ] `flutter analyze` (or equivalent) shows no new errors.
- [ ] `flutter run -d chrome` boots and the app is interactive.
- [ ] Behavior matches the relevant Acceptance Criteria in 01-requirements.md and the ASCII
      states in 02-visual.md for whatever that phase touched.

## Open Implementation Questions

- [ ] Exact `ListView.builder` vs. a plain `Column` for the row list inside `DenseTable`
      (Task 4.1) — `ListView.builder` is preferred for a future with many more mock rows, but a
      plain scrollable `Column` is simpler and matches the current row count (~dozens); decide
      during Task 4.1 based on how `DenseTable` is asked to behave with `rows.length` in the
      hundreds (not currently the case in mock data).

---

## Approval

- [ ] Reviewed by: Anton Dodonov
- [ ] Approved on:
- [ ] Notes:
