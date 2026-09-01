# Status: vdd-simbox-web-design-prototype-fix1-uiux

## Current Phase

VISUAL

## Phase Status

REVIEW

## Last Updated

2026-09-01 by Claude

## Blockers

- Waiting on user approval of 01-requirements.md and 02-visual.md before moving to
  Specifications.

## Progress

- [x] Requirements drafted
- [ ] Requirements approved
- [x] Visual mockups drafted
- [ ] Visual approved
- [ ] Specifications drafted
- [ ] Specifications approved
- [ ] Plan drafted
- [ ] Plan approved
- [ ] Implementation started
- [ ] Implementation complete
- [ ] Documentation drafted
- [ ] Documentation approved

## Context Notes

- Target project: `design/simbox-web-design-prototype-v2026` (Flutter web prototype of the
  SimBox admin panel).
- Design source of truth: `design/simbox-design-prototype-v2026-dc/index.html` — a static HTML
  mock (`_ds` NativeMind design system + hand-authored bindings) that **already implements**
  the requested pattern almost exactly: left sidebar with `navOpen`/`navCompact` toggled by
  clicking the logo header, `logo_wide.png`/`logo_square.png` swap, table with
  `position:sticky` header, and per-page `actionGroups` rendered as toggle pills in the table's
  header bar that open a single absolutely-positioned overlay panel (`S.grp` — one group open
  at a time). This flow is largely a "port this existing HTML pattern into the Flutter shell"
  task, not a from-scratch design exercise.
- Logic source of truth: `legacy/simbox-desktop-v2014/www/simbox` (old PHP admin, especially
  `head.php` for the nav section list and the various `*.php` action pages) — old visuals are
  NOT authoritative, only the functional inventory (which actions/fields/log entries must
  exist).
- User's explicit numbered asks (from the `/vdd new ...` invocation) map to requirements as:
  1. Logo → `design/logo_wide_transparent.png` (full) / `design/logo_transparent.png`
     (compact) — req. #9. Deliberately different filenames than the -dc mock's
     `logo_wide.png`/`logo_square.png` placeholders.
  2. Nav moved to the left — req. #1.
  3. Nav compact (icons only) vs full (icons + labels) — req. #1/#3.
  4. Compact/full toggled by clicking the logo; logo itself swaps square ↔ wide — req. #2/#9.
  5. Actions moved from below-the-table to a collapsible panel above/in the header bar, grouped
     for ≤2-click access — req. #4/#5.
  6. Table header always visible, only body scrolls — req. #6.
- Four pages get the action-panel treatment (they currently have `TableHeaderBar` + a `Wrap` of
  action `Panel`s below a `DenseTable`): Sims, Dongles, Diagmode, Hubs
  (`lib/pages/sims_page.dart`, `dongles_page.dart`, `diagmode_page.dart`, `hubs_page.dart`).
  Non-table pages (Наборы, Планы, Процессы, Биллинг, Обновление, Debug, Иконки) keep their
  current always-visible `Panel` layout — only the new sidebar affects them. Flagged as an open
  question in requirements; proceeding on this assumption unless the user corrects it.
- `CommandLog` (bottom "Вывод команд" console) is explicitly out of scope beyond repositioning
  under the new sidebar+content shell — no behavior change.
- No token/color/typography changes — reuse `lib/design/tokens.dart` as-is.

## Fork History

N/A — new flow.

## Next Actions

1. Get explicit "requirements approved" + "visual approved" from the user (both drafted in the
   same pass since the -dc mock already answers most visual-alignment questions).
2. Resolve the three Open Questions in 01-requirements.md (non-table pages get pill treatment
   or not; exact sidebar widths; default sidebar state on load) — currently answered with
   reasonable defaults inline, but call out for explicit confirmation.
3. On approval, move to SPECIFICATIONS: inventory exact `AppState` additions needed (sidebar
   open/compact flag, active action-group key per page), enumerate the action groups per page
   (reading `dongles_page.dart`, `diagmode_page.dart`, `hubs_page.dart` bodies, not yet read in
   full), and design the `Sidebar`/`ActionGroupBar`/`StickyDenseTable` widget shapes.
