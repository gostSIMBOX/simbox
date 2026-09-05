# Status: vdd-simbox-web-design-prototype-table-uiux

## Current Phase

IMPLEMENTATION

## Phase Status

COMPLETE — AWAITING REVIEW

## Last Updated

2026-09-05 by Claude

## Blockers

None. The one deferred manual-verification item (LIMIT0-5 columns' visual appearance) was closed
in a follow-up session: solved the browser-automation friction by dispatching a JS `WheelEvent`
directly on `<flt-glass-pane>` (Flutter web's real pointer-event host) instead of using the
`computer` tool's scroll/drag, which never worked against this CanvasKit table in either session.
All six columns confirmed rendering correctly with palevo flags in exactly the right two cells.

## Progress

- [x] Requirements drafted
- [x] Requirements approved (open questions resolved 2026-09-05; the deeper open questions found
      during Visual research were then explicitly descoped by the user, not answered — see below)
- [x] Visual mockups drafted
- [x] Visual approved (with descope)
- [x] Specifications drafted
- [x] Specifications approved
- [x] Plan drafted
- [x] Plan approved
- [x] Implementation started
- [x] Implementation complete (all items verified, including the LIMIT0-5 visual check)
- [ ] Plan drafted
- [ ] Plan approved
- [ ] Implementation started
- [ ] Implementation complete
- [ ] Documentation drafted
- [ ] Documentation approved

## Context Notes

- Legacy source of truth for logic: `legacy/simbox-desktop-v2014/www/simbox/sim.php` (main SIM
  table, ~line 1096 header, ~line 1280 row loop) + `modules/html.php` (icon helpers). Legacy visual
  design is explicitly obsolete — logic/meaning only. (User referred to this as "legacy v2015" once;
  confirmed no `legacy/simbox-desktop-v2015` tree exists — this is the same `v2014` source used
  throughout, per the original `/vdd new` instruction.)
- Design source of truth: `design/simbox-design-prototype-v2026-dc/` (tokens/design system already
  adopted by `lib/design/tokens.dart`).
- Target file to rework: `design/simbox-web-design-prototype-v2026/lib/pages/sims_page.dart` (+
  `lib/data/models.dart` `Sim` class, `lib/data/mock.dart` sample rows, `lib/data/icon_map.dart`,
  `lib/data/terminology.dart` for missing term IDs).

### 2026-09-05 scope decision — descope, don't resolve

User instruction: skip every item in 02-visual.md's Consolidated Open Questions list; implement
only what's confirmed by code. Concretely, **in scope**:

- Add missing `group` pause icon combos (holiday variants 2/12/22 — `icon_map.dart` only wires
  workday variants 1/11/21 today).
- Add `pro` column: raw value + set-vs-current blue (`T.brandDeep`) mismatch, bare-labeled like
  legacy's own unlabeled header. No claim about what the value means.
- `spec` cluster: add `fas` (fully resolved, boolean-present icon) and `vip` (exact 3-way icon
  branch, raw-value-only label) and `pre`/`pos` (reuse already-shipped `special.pre`/`special.pos`
  terms, not the current unverified "предоплата/постоплата" guess).
- `state` column: waiting/dialing/ring/active icons + elapsed-seconds counter, direction-aware
  `io`+`qos` union (add missing `SPAM`/`IMO`/`SYS` to `Ico`'s `_qosMap`), busy→numberb/numbera incl.
  the `#SOU` split (labeled "Внутренний звонок между SIM," never "self-call"), `em_type` as a raw
  uninterpreted value (matches legacy exactly).
- `may` column: add MSM line + SMS soft/hard-limit line (confirmed data-loss defect per
  icon-statuses Legacy Addition 1.1, not an open question).
- `PDDAS`/`LIMIT2-5` columns: add as columns (already-approved decisions), mock values only, no
  claim about exact real-world formula.
- `dongle_a` hub-port sub-line: add (self-explanatory from source, not an open question).
- Add `terminology.dart`'s 5 missing term IDs (`call.live.dial`, `call.live.active`,
  `call.result.busy`, `call.result.failed_unknown`, `call.end.unknown`) — these are confirmed rows
  in that flow's own approved-but-incompletely-implemented spec, not new invention.

**Explicitly out of scope this iteration** (descoped, not answered):
- `owner` operator-column line — **not added at all** (confirmed dead read path, no writer targets
  it; reproduce-bug-vs-fix is a product decision we're skipping, so the safest move is to add
  nothing rather than guess).
- Any asserted *meaning* for: `pro`'s value, `vip` tier distinction (11 vs 12 vs generic), `pre`/
  `pos` business model, `em_type`, `PDDAS`/`ASRL` exact formulas, `PAL`/`ipalevo` naming (keep the
  existing unresolved `captcha.pal` term as-is), `SPE`/`MAG`/`NAV`/`IMA`/`REC` subcodes, the `SR`
  direction-code collision fix.
- Full open-questions list with citations lives in 02-visual.md; not repeating it here.

- `Cell` widget (`lib/data/models.dart`) already supports 7 stackable slots (note/icons/text/mono/
  warn/sub/sub2) — most additions fit an existing empty slot rather than widening the table further.
- `ColDef`/`Cell`/`DenseTable` architecture should NOT be redesigned — this is an additive/
  corrective pass on `sims_page.dart`'s existing `_cols()`, not a rewrite.

## Fork History

None — new flow.

## Next Actions

1. User to review 05-implementation-log.md and the actual code changes (6 files modified:
   `terminology.dart`, `icon_map.dart`, `models.dart`, `dense_table.dart`, `sims_page.dart`,
   `mock.dart` + `test/icon_map_test.dart` extended).
2. Optional DOCUMENTATION phase (client-facing README) — not started, VDD marks this optional.

## Specifications Note (2026-09-05)

Verified every new asset path exists on disk before writing the spec (`ivip1.png`/`ivip2.png` not
`.ico`, `state_wait.png` at top level not under `state/`, `imode.png`, `spam.png`, etc.). Confirmed
`Cell`/`DenseTable`/`IconStack` already support everything needed (multi-icon `Wrap`, multi-line
`Text` via embedded `\n`) — no shared-widget changes required except the one `pro`-column styling
question. Corrected a Visual-phase overstatement: only 2 of the 5 "missing terminology.dart terms"
actually apply to this table (`call.live.dial`, `call.live.active`) — the other 3
(`call.result.busy`, `call.result.failed_unknown`, `call.end.unknown`) belong to the out-of-scope
calls-log page, not `sim.php`'s STATE column.

## Plan Note (2026-09-05)

5 phases, 16 tasks total. Resolved Specifications' one Open Design Question at the task level
(3.8: inline `Text` color override for the `pro` column, recommended approach, with the `Cell.tint`
alternative kept as a named fallback in Risk Assessment if it looks wrong on screen). No files
created or deleted — 5 files modified only, all within
`design/simbox-web-design-prototype-v2026/lib/`.
