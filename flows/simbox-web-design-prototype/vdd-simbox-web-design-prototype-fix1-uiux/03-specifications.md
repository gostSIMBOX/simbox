# Specifications: simbox-web-design-prototype-fix1-uiux

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-09-01
> Requirements: [01-requirements.md](01-requirements.md)
> Visual: [02-visual.md](02-visual.md)

## Overview

Refactor the app shell of `design/simbox-web-design-prototype-v2026` from
(top status bar → wrapping horizontal nav tabs → single page-wide scroll containing table +
actions below it → bottom command log) to (left collapsible sidebar nav → top status strip →
per-page content where table pages get a sticky-header table with header-bar action-group pills
→ bottom command log). No page's data/business logic changes — this is confined to `main.dart`,
`widgets/top_bar.dart` (replaced by a new `widgets/sidebar.dart`), `widgets/dense_table.dart`,
`widgets/panel.dart` (new `ActionGroupBar`/pill component added), `state/app_state.dart` (two
new fields + methods), the four table pages, and the seven non-table pages (padding-only
change), plus new logo assets + `pubspec.yaml`.

## Affected Systems

| System | Impact | Notes |
|---|---|---|
| `lib/main.dart` | Modify | `AdminShell` becomes `Row(Sidebar, Column(StatusBar, content, CommandLog))`; drop the shared outer `SingleChildScrollView` |
| `lib/widgets/top_bar.dart` | Modify | Split into `lib/widgets/status_bar.dart` (device/IP/clock strip, unchanged content) + `lib/widgets/sidebar.dart` (new, replaces the `Wrap` of `_TabButton`) |
| `lib/widgets/sidebar.dart` | Create | Vertical nav, logo-click compact/full toggle, tooltip on collapsed items |
| `lib/widgets/dense_table.dart` | Modify | Split header/body so header is pinned and only rows scroll vertically; horizontal scroll still covers both |
| `lib/widgets/panel.dart` | Modify | Add `ActionGroupPill` + keep `Panel`/`AdmButton`/etc. unchanged (group panels reuse `Panel` as their card) |
| `lib/widgets/action_group_bar.dart` | Create | Header-bar row of pills + the floating overlay that shows the active group's `Panel` |
| `lib/state/app_state.dart` | Modify | Add `navCompact` (bool) + `toggleNav()`; add `activeGroup` (String?) + `toggleGroup(String)`; clear `activeGroup` in `goTo()` |
| `lib/pages/sims_page.dart` | Modify | `TableHeaderBar` gains a `groups` param; 5 `Panel`s become `ActionGroup` definitions rendered via the overlay instead of a trailing `Wrap` |
| `lib/pages/dongles_page.dart` | Modify | Same pattern, 3 groups |
| `lib/pages/diagmode_page.dart` | Modify | Same pattern, 1 group |
| `lib/pages/hubs_page.dart` | Modify | Same pattern, 1 group |
| `lib/pages/{nabor,plan,proc,bablo/billing,upgrade,debug,icons}_page.dart` | Modify | Wrap own body in `SingleChildScrollView(padding: EdgeInsets.all(22))` since `main.dart` no longer provides it globally |
| `pubspec.yaml` | Modify | Register `assets/brand/` |
| `assets/brand/logo_wide_transparent.png`, `assets/brand/logo_transparent.png` | Create | Copied from `design/logo_wide_transparent.png` / `design/logo_transparent.png` |

## Architecture

### Component Diagram

```
AdminShell (main.dart)
├─ Sidebar                              (new widget, full app height, left column)
│   ├─ logo header (onTap → st.toggleNav())
│   └─ NavItem × 11                     (icon [+ label if !navCompact], tooltip always)
└─ Column                               (right side, fills remaining width)
    ├─ StatusBar                        (renamed top_bar.dart content, unchanged fields)
    ├─ Expanded
    │   └─ _page(st.page)               (switch, per-page widget — see below)
    └─ CommandLog                       (unchanged, bottom-docked)

Table page (Sims/Dongles/Diagmode/Hubs), e.g. SimsPage.build():
Column
├─ TableHeaderBar(groups: [...])        (title, count, selection chip, N× ActionGroupPill,
│                                         search, refresh — replaces the old title-only bar)
├─ Stack                                (so the overlay floats without reflowing the table)
│   ├─ Column
│   │   └─ Expanded(DenseTable(...))    (sticky header, only rows scroll)
│   └─ if (st.activeGroup != null)
│       Positioned(top:0,left:0,right:0, child: ActionGroupOverlay(child: Panel(...)))
```

Non-table pages (Наборы, Планы, Процессы, Биллинг, Обновление, Debug, Иконки) are unaffected
structurally — they just gain their own `SingleChildScrollView` wrapper since the shell no
longer supplies one globally.

### Data Flow

- `AppState.page` still drives which page widget `_page()` returns (unchanged).
- `AppState.navCompact` (new) drives `Sidebar`'s width (64/208) and whether `NavItem` shows a
  label; toggled only by tapping the logo header inside `Sidebar`.
- `AppState.activeGroup` (new, `String?`) drives which `ActionGroupOverlay` is visible on the
  current table page. It is page-scoped by construction (each table page only defines its own
  group keys — `power/simple/smart/plans/export` for Sims, `dact/pin/modes` for Dongles, `fw`
  for Diagmode, `hubpwr` for Hubs — so a stale key from a different page never matches). It is
  also explicitly cleared in `goTo()` so switching pages always starts with no group open,
  matching the existing `selected`/`sortKey`/`query` reset behavior.
- `DenseTable` keeps its existing `rows`/`cols`/selection/sort props — only its internal render
  tree changes (header no longer part of the same scrollable as rows).

## Interfaces

### New Interfaces

```dart
// lib/state/app_state.dart additions
class AppState extends ChangeNotifier {
  bool navCompact = false;   // sidebar mode; false = full (labeled), true = compact (icons)
  String? activeGroup;       // key of the currently open action-group panel, or null

  void toggleNav() {
    navCompact = !navCompact;
    notifyListeners();
  }

  void toggleGroup(String key) {
    activeGroup = (activeGroup == key) ? null : key;
    notifyListeners();
  }

  // goTo() gains one line: activeGroup = null;
}

// lib/widgets/action_group_bar.dart (new file)
class ActionGroup {
  final String key, label, icon;
  final Widget Function(BuildContext) builder; // returns the existing Panel-based content
  const ActionGroup({required this.key, required this.label, required this.icon, required this.builder});
}

class ActionGroupPill extends StatelessWidget {
  final ActionGroup group;
  final bool open;
  final VoidCallback onTap;
  const ActionGroupPill({required this.group, required this.open, required this.onTap, super.key});
}

/// Renders the currently-open group's `builder(context)` output inside a Panel-styled
/// floating card, positioned via the parent Stack (see Architecture). No-op (renders
/// SizedBox.shrink) when nothing is open — callers guard with `if (st.activeGroup != null)`.
class ActionGroupOverlay extends StatelessWidget {
  final List<ActionGroup> groups;
  final String activeKey;
  const ActionGroupOverlay({required this.groups, required this.activeKey, super.key});
}

// lib/widgets/sidebar.dart (new file)
class Sidebar extends StatelessWidget {
  const Sidebar({super.key});
  // reads AppScope.of(context).navCompact / .page, renders logo header + NavItem list
}
```

### Modified Interfaces

```dart
// lib/pages/sims_page.dart — TableHeaderBar gains `groups`
class TableHeaderBar extends StatelessWidget {
  final String title;
  final int count;
  final TextEditingController search;
  final ValueChanged<String> onSearch;
  final List<ActionGroup> groups; // NEW, defaults to const [] for pages with none (none exist today, but keeps the type honest)
  const TableHeaderBar({
    super.key, required this.title, required this.count,
    required this.search, required this.onSearch, this.groups = const [],
  });
}
```

```dart
// lib/widgets/dense_table.dart — same public API, internal render tree only:
// before: Scrollbar > SingleChildScrollView(horizontal) > Column(header, ...rows)
// after:  Scrollbar > SingleChildScrollView(horizontal) > SizedBox(width: totalWidth,
//           child: Column(header, Expanded(ListView.builder(rows))))
// DenseTable must now be given a bounded height by its parent (Expanded in the table
// page's Column) — this is the one behavioral precondition callers must satisfy.
```

`top_bar.dart`'s `_tabs` constant (the `(AdmPage, label, icon)` list) moves as-is into
`sidebar.dart` — no reordering, no icon changes.

## Data Models

No new persisted/mock data types. `ActionGroup` (above) is a UI-only wiring struct, not a data
model — its `builder` closures wrap the *exact same* `Panel(...)` widget trees the pages already
build today, just relocated from an unconditional `Wrap` to a conditionally-rendered overlay
entry keyed by `key`.

### Schema Changes

None.

## Behavior Specifications

### Happy Path

1. App loads → `AdminShell` renders `Sidebar` (full, `navCompact=false`) + `StatusBar` + `SimsPage` (default `AdmPage.sim`) + `CommandLog`.
2. User clicks the sidebar logo → `st.toggleNav()` → sidebar animates/snaps to compact (64px, icons only, tooltips active).
3. User clicks "Свистки (nm)" icon → `st.goTo(AdmPage.dongle)` → page switches, `selected`/`sortKey`/`query`/`activeGroup` all reset.
4. User clicks the "Действия со свистками" pill in the Dongles table header → `st.toggleGroup('dact')` → `ActionGroupOverlay` renders that group's `Panel` floating under the header, table still fully visible underneath/behind it.
5. User clicks an action button inside the open panel (e.g. a dongle action) → existing `st.runOnDongles(...)` fires exactly as it does today (no change to this call).
6. User clicks the same pill again → `activeGroup` clears → overlay disappears, no other state changed.
7. User scrolls the dongle table body → header row (`model/cfun/name/lock/...`) stays pinned; only rows move.

### Edge Cases

| Case | Trigger | Expected Behavior |
|---|---|---|
| Open group panel, then switch page via sidebar | Click a different nav item while a group panel is open | `goTo()` resets `activeGroup` to null — the new page always opens with no panel showing, even though the new page may reuse the same key coincidentally (it won't, keys are page-unique, but reset is defensive and matches existing selection/sort reset semantics) |
| Open group panel, then click a different pill on the same page | Click pill B while pill A's panel is open | `toggleGroup('B')` sets `activeGroup='B'` unconditionally (only equal-key clicks toggle closed) — panel A is replaced by panel B, not both shown |
| Sidebar compact + long label overflow | `navCompact=true` | Labels are not rendered at all (icon-only), so no overflow is possible; only the tooltip carries the label text |
| Table with zero rows | `rows.isEmpty` (existing `DenseTable` behavior) | Sticky header still renders; body area shows the existing "Ничего не найдено" message inside the scrollable body region, not fighting the sticky header |
| Very tall action-group panel content | e.g. "Действия хитрые" grid of 8 buttons | Overlay panel already has `maxHeight`/scroll in the -dc mock (`max-height:60vh;overflow:auto`) — Flutter overlay gets the same `ConstrainedBox(maxHeight: ...)` + internal scroll so it can never push off-screen |
| Selection chip + pills both present | User has selected rows AND wants to open a group | Both render side-by-side in the header bar's `Wrap`/`Row`, matching current `TableHeaderBar` layout which already handles the selection chip conditionally |

### Error Handling

Not applicable — this is a static/mock-data prototype with no network/error states introduced by
this change. Existing `errorBuilder` on `AdmIcon` (missing asset → blank box) is untouched.

## Dependencies

### Requires

- `design/logo_wide_transparent.png` and `design/logo_transparent.png` must be copied into the
  Flutter project before the `Sidebar` widget can reference them.

### Blocks

- None — this is the only active flow against this prototype.

## Integration Points

### External Systems

None — pure Flutter web prototype, no backend.

### Internal Systems

- `lib/data/icon_map.dart` / `assets/imgs/*` — unchanged, `Sidebar` reuses the same `_tabs`
  icon paths and `AdmIcon` widget the old `TopBar` used.
- `lib/design/tokens.dart` — reused as-is (`T.brandDeep`, `T.rowSel`, `T.radiusCtl`, `T.shadow`,
  `T.hairline`) for the sidebar, pills, and overlay so visuals stay consistent with the rest of
  the app and with the -dc mock's palette.

## Testing Strategy

This prototype has no automated test suite (`flutter test` — none present under `test/`).
Verification is manual, per the project's own convention (visual prototype).

### Manual Verification

- [ ] `flutter run -d chrome` (or `flutter build web` + serve) boots without errors.
- [ ] Sidebar shows all 11 sections in the original order; clicking each navigates correctly
      and clears selection/sort/query/activeGroup (spot-check 2–3).
- [ ] Logo click toggles compact ↔ full; logo image swaps wide ↔ square; icon-only mode still
      shows tooltips on hover.
- [ ] On Sims/Dongles/Diagmode/Hubs: each documented action group opens via its pill, every
      button/field inside still fires the same `runOnSelection`/`runOnDongles`/`push` call it
      did before the refactor (spot-check the toast text + command-log entry match pre-change
      behavior for at least one action per group).
- [ ] Table header stays visible while scrolling a table with enough rows to overflow (mock
      data may need a temporary row-count bump to verify, or resize the window short).
- [ ] Non-table pages (Планы, Процессы, Биллинг, Обновление, Debug, Иконки, Наборы) render
      unchanged content, just under the new shell, and scroll correctly if they overflow.
- [ ] `CommandLog` still opens/closes/clears and spans the content column width (not full
      window width, since the sidebar is now beside it).

## Migration / Rollout

Not applicable — single prototype app, no users/data to migrate, no feature flag needed (this
*is* the intended new default shell).

## Open Design Questions

- [ ] Confirm sidebar widths 208px (full) / 64px (compact) are acceptable as literal constants,
      or should they derive from content (e.g. longest label)? Recommendation: literal
      constants matching the -dc mock, simplest and already visually validated.
- [ ] Confirm non-table pages (Планы/Процессы/Обновление/Debug/Биллинг/Наборы/Иконки) do **not**
      get the pill/overlay treatment (per requirements Open Question #1) — proceeding on that
      assumption; only their scroll wrapper changes.
- [ ] `ActionGroupOverlay` positioning: spec assumes `Stack` + `Positioned` inside the table
      page's body so the panel floats over the table without reflowing it (matches -dc mock's
      `position:absolute`). Confirm this reading of requirement #5 vs. an alternative where the
      panel pushes the table down (simpler Flutter layout, but contradicts req. #5's "does not
      push the table down" and the drawn ASCII mockup in 02-visual.md).

---

## Approval

- [ ] Reviewed by: Anton Dodonov
- [ ] Approved on:
- [ ] Notes:
