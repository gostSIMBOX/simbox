# Status: vdd-simbox-web-design-prototype-table-uiux

## Current Phase

REQUIREMENTS

## Phase Status

REVIEW

## Last Updated

2026-09-05 by Claude

## Blockers

- Waiting on user answers to the 5 open questions in 01-requirements.md (LIMIT0-5 layout, state/busy
  fidelity, `pro` column visual convention, dead `pri` column, `dongle_a` placement) before
  requirements can be marked approved.

## Progress

- [x] Requirements drafted
- [ ] Requirements approved
- [ ] Specifications drafted
- [ ] Specifications approved
- [ ] Plan drafted
- [ ] Plan approved
- [ ] Implementation started
- [ ] Implementation complete
- [ ] Documentation drafted
- [ ] Documentation approved

## Context Notes

- Legacy source of truth for logic: `legacy/simbox-desktop-v2014/www/simbox/sim.php` (main SIM
  table, ~line 1096 header, ~line 1280 row loop) + `modules/html.php` (icon helpers). Legacy visual
  design is explicitly obsolete — logic/meaning only.
- Design source of truth: `design/simbox-design-prototype-v2026-dc/` (tokens/design system already
  adopted by `lib/design/tokens.dart`).
- Target file to rework: `design/simbox-web-design-prototype-v2026/lib/pages/sims_page.dart` (+
  `lib/data/models.dart` `Sim` class, `lib/data/mock.dart` sample rows, `lib/data/icon_map.dart` /
  `icons_catalog.dart` for any new icon mappings).
- Full column-by-column gap analysis done: legacy has 42 data columns, current prototype has 33.
  8 columns fully missing (`pro`, `PDDAS`, `LIMIT2`-`LIMIT5`, plus `state` col's live-call/busy
  sub-state, plus `spec` col's `fas`/`vip`/`pre`/`pos` icons), 4 columns have partial data loss
  (`spec`, `oper` missing owner line, `may` missing MSM+SMS-limit line, `dongle` missing hub port
  label). Full table is in 01-requirements.md.
- `Cell` widget (`lib/data/models.dart`) already supports 7 stackable slots (note/icons/text/mono/
  warn/sub/sub2) — most partial-data-loss columns can likely be fixed by using an existing empty
  slot rather than widening the table further.
- `ColDef`/`Cell`/`DenseTable` architecture should NOT be redesigned — this is an additive/
  corrective pass on `sims_page.dart`'s existing `_cols()`, not a rewrite.

## Fork History

None — new flow.

## Next Actions

1. Get user's answers to the open questions in 01-requirements.md (or explicit "use your
   recommended defaults" / direct edits).
2. Mark requirements APPROVED.
3. Move to VISUAL phase: ASCII mockups of the reworked column set (esp. however LIMIT0-5 and the
   `state` busy/live-call sub-state get resolved) for sign-off before touching Dart code.
