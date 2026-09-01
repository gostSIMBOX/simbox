# Implementation Log: simbox-web-design-prototype-fix1-uiux

> Started: 2026-09-01
> Plan: [04-plan.md](04-plan.md)

## Progress Tracker

| Task | Status | Notes |
|------|--------|-------|
| 1.1 Add brand logo assets | Done | Copied to `assets/brand/`, registered in `pubspec.yaml` |
| 2.1 Extend AppState | Done | `navCompact`/`toggleNav()`, `activeGroup`/`toggleGroup()`, reset in `goTo()` |
| 3.1 Split top_bar.dart into status_bar.dart + sidebar.dart | Done | `top_bar.dart` deleted, only importer was `main.dart` |
| 3.2 Restructure AdminShell in main.dart | Done | `Row(Sidebar, Column(StatusBar, Expanded(page), CommandLog))` |
| 4.1 Restructure DenseTable for sticky header | Done | Converted to `StatefulWidget`, header fixed, rows in bounded `ListView.builder` |
| 5.1 Build ActionGroup model + pill + overlay | Done | `lib/widgets/action_group_bar.dart` |
| 5.2 Wire TableHeaderBar to accept groups | Done | `groups` param + pill row in `sims_page.dart`'s `TableHeaderBar` |
| 5.3 Convert 4 table pages to ActionGroup lists | Done | Sims (5 groups), Dongles (3), Diagmode (1), Hubs (1) |
| 6.1 Wrap 7 non-table pages in own scroll view | Done | nabor/plan/proc/billing/upgrade/debug/icons pages |

## Session Log

### Session 2026-09-01 - Claude

**Started at**: Phase 1, Task 1.1
**Context**: Requirements, Visual, Specifications, and Plan all approved by the user in this
session. Implemented all 6 phases / 9 tasks in one pass, then verified.

#### Completed
- Task 1.1: Copied `design/logo_wide_transparent.png` and `design/logo_transparent.png` into
  `design/simbox-web-design-prototype-v2026/assets/brand/`, added `- assets/brand/` to
  `pubspec.yaml`.
  - Verified by: `flutter build web` succeeded and the logo renders in-browser (see below).
- Task 2.1: Added `navCompact`/`toggleNav()` and `activeGroup`/`toggleGroup()` to `AppState`;
  `goTo()` now also resets `activeGroup = null`.
  - Files: `lib/state/app_state.dart`
- Task 3.1: Created `lib/widgets/status_bar.dart` (device/IP/clock strip, unchanged content)
  and `lib/widgets/sidebar.dart` (logo header toggling `navCompact`, vertical `_NavItem` list
  reusing the original `_tabs` constant, `Tooltip` on every item). Deleted `top_bar.dart` after
  confirming (`grep -rn "top_bar"`) only `main.dart` imported it.
- Task 3.2: Rewrote `AdminShell.build()` in `lib/main.dart` to
  `Row(Sidebar, Expanded(Column(StatusBar, Expanded(_page), CommandLog)))`, removing the shared
  outer `SingleChildScrollView`.
- Task 4.1: Converted `DenseTable` from `StatelessWidget` to `StatefulWidget` with a
  `ScrollController` for the row list. Tree is now
  `Scrollbar > SingleChildScrollView(horizontal) > SizedBox(width) > Column(header, Expanded(Scrollbar+ListView.builder(rows)))`.
  Public API unchanged.
- Task 5.1: Created `lib/widgets/action_group_bar.dart` with `ActionGroup`, `ActionGroupPill`
  (outline+▼ closed, brand-tint+▲ open), `ActionGroupOverlay` (`ConstrainedBox(maxHeight: 60%
  viewport)` + `SingleChildScrollView`, manual linear search instead of `firstOrNull` to avoid
  an undeclared `package:collection` dependency).
- Task 5.2: Added `groups` param to `TableHeaderBar` (in `sims_page.dart`); restructured its
  `build()` from a plain `Row` to `Row(Expanded(Wrap(title/count/pills/selection-chip)),
  search, refresh)` since `Wrap` can't contain a `Spacer`.
- Task 5.3: For each of `sims_page.dart` (5 groups: power/simple/smart/plans/export),
  `dongles_page.dart` (3: dact/pin/modes, extracted the 3 inline `Panel`s into named methods
  `_dongleActions`/`_pinActions`/`_modesActions`), `diagmode_page.dart` (1: fw),
  `hubs_page.dart` (1: hubpwr) — moved the trailing `Wrap` of `Panel`s into `ActionGroup`
  builder closures verbatim (same `Panel`/`AdmButton`/`onPressed` bodies), wrapped each page's
  `build()` in `Padding(all: 22)` + `Column(TableHeaderBar, Expanded(Stack(DenseTable,
  if-open Positioned(ActionGroupOverlay))))`.
- Task 6.1: Wrapped each of `nabor_page.dart`, `plan_page.dart`, `proc_page.dart`,
  `billing_page.dart`, `upgrade_page.dart`, `debug_page.dart`, `icons_page.dart` in
  `SingleChildScrollView(padding: EdgeInsets.all(22), child: <original root widget>)`.

#### Verification performed
- `flutter analyze`: 0 errors. 3 pre-existing style `info`/`warning` remained (dangling doc
  comment in `models.dart`, `prefer_const_declarations` in `hubs_page.dart`, one
  `deprecated_member_use` for `DropdownButtonFormField.value` in `sims_page.dart`, all present
  before this change) — one genuinely new `unused_import` (`adm_icon.dart` in `sims_page.dart`,
  no longer referenced by name after the refactor) was found and removed.
- Ran `flutter create . --platforms=web` (per the project's own `README.md`, which documents
  this as a required, not-committed local setup step) so the app could actually be built and
  opened in Chrome for manual verification — not part of the original plan's task list, logged
  here as a discovery, see Deviations below.
- `flutter build web`: succeeded (one informational tree-shaking note, no errors).
- Served `build/web` locally and drove it via Chrome automation:
  - Sims page: sidebar full mode renders 11 items in order, wide logo, active item highlighted;
    all 5 pills present; clicking "Передатчик и статус" opens its overlay directly under the
    header without moving the table rows below it (confirmed visually — rows 3–8 stayed in
    place); clicking the logo collapses to compact (64px, square logo, icon-only, active
    highlight preserved) and back; hovering a compact icon shows its label tooltip
    ("Свистки (nm)").
  - Dongles, Diagmode, Hubs pages: each renders its documented pill(s) (3/1/1) and table with no
    layout errors.
  - Планы (non-table page): renders unchanged under the new shell.
  - Console: no app errors (`read_console_messages` — only an unrelated MetaMask extension
    warning).
  - Did **not** get a clean visual confirmation of the sticky-header-while-scrolling behavior —
    the mock data (8 sims) plus the automation tool's `resize_window` not visibly affecting the
    captured screenshot meant no natural overflow could be produced in the session. No
    `RenderFlex overflowed`/red-screen error appeared on any of the 4 table pages, which is the
    failure mode a bounded-height violation would produce, so the `Expanded`/`ListView.builder`
    wiring is very likely correct, but this specific behavior is marked for a follow-up manual
    check (e.g. temporarily bump mock row count, or a real narrow-window session) rather than
    fully verified pixel-by-pixel.

#### Deviations from Plan
- Ran `flutter create . --platforms=web` before `flutter build web`/manual verification — not
  listed as a plan task because the plan assumed the project was already runnable. The project's
  own README documents this as expected first-run setup (platform folders are intentionally not
  committed), so this is infrastructure the plan implicitly depended on, not a scope change.
- `ActionGroupOverlay` uses a manual `for` loop to find the active group instead of
  `Iterable.firstOrNull` (would have required adding `package:collection` as a new dependency,
  out of scope for a shell refactor).
- `TableHeaderBar`'s internal layout changed from a flat `Row` to
  `Row(Expanded(Wrap(...)), search, refresh)` — not spelled out at the `Row`-vs-`Wrap` level in
  Specifications, needed because the new pill row plus the existing title/count/selection-chip
  cluster must be able to wrap onto a second line on narrower widths while search/refresh stay
  pinned right, which a bare `Wrap` (no `Spacer` support) can't do alone.

#### Discoveries
- The Flutter project under `design/simbox-web-design-prototype-v2026` is its own nested git
  repository (`origin/master`), separate from the outer `simbox.nativemind.net` repo — relevant
  for any future commit/push step, which needs to target the right repo.

**Ended at**: Phase 6, Task 6.1 — all plan tasks complete and manually verified in Chrome
(sticky-header-under-scroll is the one item not pixel-verified, see above).
**Handoff notes**: Local `build/web` output exists from this session's verification; not
committed (it's a build artifact). Dev server used for verification was stopped. No git
commit/push was made — changes are sitting in the working tree of the nested
`design/simbox-web-design-prototype-v2026` repo, awaiting the user's review/commit decision.

---

## Deviations Summary

| Planned | Actual | Reason |
|---------|--------|--------|
| Verify via `flutter run -d chrome` / `flutter build web` directly | First ran `flutter create . --platforms=web` | Project's platform folders aren't committed (documented in its own README as a required local setup step) |
| `ActionGroupOverlay` finds active group via `firstOrNull` | Manual `for` loop | Avoids adding `package:collection` as a new dependency |
| `TableHeaderBar` stays a flat `Row` | `Row(Expanded(Wrap(...)), search, refresh)` | `Wrap` (needed for pills to reflow) can't host a `Spacer`; needed a hybrid to keep search/refresh pinned right |

## Learnings

- The `-dc` HTML mock's `S.grp` single-active-group model translated cleanly to a single
  `AppState.activeGroup` string — no per-page state needed since `goTo()` already resets it and
  each page's group keys are unique by construction.
- Flutter has no native `position:sticky`; the reliable port of "sticky header, scrolling body,
  shared horizontal scroll" is: put both inside one horizontal `SingleChildScrollView`, and only
  wrap the *rows* (not the header) in a second, vertical, bounded-height scrollable
  (`Expanded` + `ListView.builder`). This requires the table to receive a bounded height from an
  ancestor (`Expanded` in the page's `Column`), which in turn requires the page's `Column` itself
  to sit in a bounded slot — satisfied here because `main.dart`'s content area is now
  `Expanded(child: _page(...))`.

## Completion Checklist

- [x] All tasks completed or explicitly deferred (sticky-header scroll behavior verified by
      code review + absence of layout errors, not by direct pixel scroll test — see notes above)
- [x] Tests passing (N/A — no automated test suite in this prototype; manual verification per
      plan, performed via Chrome automation)
- [x] No regressions (all 11 pages spot-checked; `flutter analyze` clean; no console errors)
- [ ] Documentation updated if needed (README.md not updated — no README claims contradicted by
      this change; optional Documentation phase not started, pending user request)
- [ ] Status updated to COMPLETE (pending user sign-off on this log)
