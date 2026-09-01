# Status: vdd-simbox-design-prototype-fix1

## Current Phase

IMPLEMENTATION

## Phase Status

DRAFTING

## Last Updated

2026-09-01 by Claude

- None.

## Progress

- [x] Requirements drafted
- [x] Requirements approved (2026-09-01)
- [x] Visual mockups drafted
- [x] Visual mockups approved (2026-09-01)
- [x] Specifications drafted
- [x] Specifications approved (2026-09-01)
- [x] Plan drafted
- [x] Plan approved (2026-09-01)
- [x] Implementation started
- [ ] Implementation complete (Phase 1+2 done, Phase 3+4 remain)
- [ ] Documentation drafted
- [ ] Documentation approved

## Context Notes (updated after 2nd round of discovery)

- **Skill split discovered mid-flow**: the GostSimBox icon set, guidelines and live template
  moved out of `nativemind-designsystem` into a new dedicated skill, `nativemind-adminka`.
  `nativemind-designsystem/readme.md` already correctly points there (§ "Web & admin
  surfaces") — verified not stale. All requirements-doc references now say
  `nativemind-adminka/...` for adminka-specific assets/guidelines/template, and
  `nativemind-designsystem/...` only for the general `icon-density.html` rule and the new
  `assets/icons/icon-globe.svg`.
- **Global-skill edits made already** (per user's explicit "fix the global skill too" answer):
  1. `nativemind-adminka/assets/adminka/adminka-to-fugue-map.json` — `pause2.png` entry marked
     `"deprecated": true` with a reason (accidental duplicate of `pause.png`, same Fugue
     source, never referenced by legacy PHP). Found because the local prototype used
     `pause2.png` in the SIM table where legacy logic only ever emits `pause.png`.
  2. `nativemind-designsystem/assets/icons/icon-globe.svg` — new file, created for the
     language-selector requirement. No globe/language icon existed anywhere in the design
     system before. Manual vector redraw (16-unit grid, `viewBox="0 0 16 16"`) of Fugue's
     `globe.png`, per the user's explicit request for "Fugue style" over the generic
     Lucide-style convention the rest of `assets/icons/` otherwise follows.
- **Scope expanded twice more since first draft**, both confirmed by the user:
  1. Full column-parity audit, not just icon-correctness — every column of every table screen
     checked against its legacy PHP source, not just icons. Two concrete gaps already found and
     folded into AC #8: missing `msm.ico` column on Планы (`plan.php` has may/mon/msm in a row,
     prototype only has may/mon), and 2 missing header/data columns on the dongle table
     (`dongle.php` has 4 empty leading `<td>` before the "Свисток" label, prototype has 2).
  2. `nativemind-adminka/guidelines/adminka-taxonomy.html` found — has the folder=semantic-axis
     grouping and full Fugue provenance table; this is the primary reference for the
     column-parity audit's "what does this icon mean" column, better than deriving everything
     from PHP by hand.
- Given the scope, the actual column-by-column audit execution (10 screens × up to ~50 columns
  each) is heavy research — plan to delegate it to parallel background Explore/general-purpose
  agents (2-3 screens per agent) during Specifications phase, each reporting a structured
  diff (missing column / wrong icon / correct) rather than doing it all inline.

- Target file: `design/simbox-design-prototype/index.html` (single static HTML file, 917
  lines, 11 screens, uses `nativemind-designsystem`'s `_ds_bundle.js` + local `support.js`).
- Source of truth for icons/columns/labels: `legacy/simbox-desktop-v2014/www/simbox/sim.php`
  (icon legend at lines 2164–2221, group legend 2190–2221) and `modules/html.php` (icon
  selection functions).
- Icon asset home: `nativemind-designsystem` skill's `assets/adminka/` (229 files, GostSimBox
  16×16 originals) + `adminka-to-fugue-map.json` for provenance/2× status.
- Icon sizing decision (confirmed by user): NOT a UI-size bump to 32px. Follow
  `guidelines/icon-density.html` — one logical 16px icon, `srcset` 16/32/48 for 1×/2×/3× DPR.
  "32×32 on retina" in the user's ask = the @2x density asset, not a bigger on-screen icon.
- Monospace font (confirmed): system stack `ui-monospace, SFMono-Regular, Menlo, Consolas,
  "Liberation Mono", monospace` — no embedded font file.
- Column hide/reorder + adaptive actions row (confirmed): real working vanilla JS, no
  framework — consistent with the prototype's existing plain HTML/JS approach. User's answer
  was "как есть" (consistent with how the prototype already works), interpreted as: build real
  interactivity, not a static one-state mockup.
- Scope (confirmed): ALL screens with a `<table>` in the prototype — not just "01 · Симки".
  That's effectively every screen (01 Симки, 02/03 Модемы nm/um, 04 Хабы, 05 Наборы команд,
  06 Планы, 07 Процессы, 08 Биллинг, 09 Обновление, 10 Debug).
- Mid-turn scope addition from user (folded into requirements as AC #6 and #7):
  - Rename "Свистки (nm)"/"Свистки (um)" → "Модемы (nm)"/"Модемы (um)" everywhere (nav on all
    11 screens' repeated nav bars + the two screen titles "Свистки (normal/update mode)" →
    "Модемы (normal/update mode)"). Routes (`/?p=dongle`, `/?p=diagmode`) unchanged.
  - Add a language selector to the shared top bar: English (default), Thai, Russian, Hindi,
    Chinese. Visual/state-only — no real translation of the Russian copy in this iteration.
- Existing reference implementation worth reusing patterns from (not swapping runtimes):
  `templates/gostsimbox-admin/GostSimBoxAdmin.dc.html` in the design system already has
  row-selection + sortable-column-header state logic we can mirror in vanilla JS for the new
  hide/reorder-columns feature.
- Concrete bug already found during research (to fix, not just note): SIM table row 2's group
  column uses `assets/imgs/pause2.png`, but the legacy `html_group()` logic only ever emits
  `pause.png` (never `pause2.png`) for that state — likely a wrong icon copied into the
  prototype.

## Fork History

None — new flow.

## Next Actions

1. Get explicit "plan approved" from Anton on `04-plan.md` (4 phases, 13 tasks — Планы
   restoration split into 7 sub-steps given its size).
2. Move to IMPLEMENTATION phase: execute task by task per the plan's dependency graph, logging
   progress/deviations in `05-implementation-log.md`.
