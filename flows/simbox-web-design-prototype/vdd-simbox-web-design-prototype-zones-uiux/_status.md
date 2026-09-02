# Status: vdd-simbox-web-design-prototype-zones-uiux

## Current Phase

IMPLEMENTATION

## Phase Status

APPROVED

## Last Updated

2026-09-02 by Claude

## Blockers

- None. User approved the implementation 2026-09-02.
- No git commit/push has been made (not requested). Reminder for any future session:
  `design/simbox-web-design-prototype-v2026` is its own nested git repo (`origin/master`),
  separate from the outer `simbox.nativemind.net` repo — same as fix1/fix2's precedent.

## Progress

- [x] Requirements drafted
- [x] Requirements approved
- [x] Visual mockups drafted
- [x] Visual approved
- [x] Specifications drafted
- [x] Specifications approved
- [x] Plan drafted
- [x] Plan approved
- [x] Implementation started
- [x] Implementation complete (all 9 tasks done, manually verified in Chrome; see log)
- [ ] Documentation drafted (optional phase, not started — not requested)
- [ ] Documentation approved

## Context Notes

- **New flow, not a continuation of fix1/fix2** (those are complete and committed — see below).
  This flow adds a brand-new admin section, "Направления (DEF коды)," that the legacy 2014
  panel never finished building.
- **Legacy data source**: `legacy/simbox-desktop-v2014/asterisk/extensions/zones/*.conf` — 25
  raw Asterisk dialplan files, ~9,013 total lines, one `exten => _<DEFCODE>,1,Macro(makecall,
  <zone>,${EXTEN})` line per DEF code. Filename `extensions_<zone>.conf` names the zone; all
  lines within a file target that same zone (spot-verified on `megafon_spb`). 6+ pairs of files
  are byte-identical abbreviated/full-name duplicates (e.g. `bee_msk.conf` ==
  `beeline_msk.conf`) — dedup to the canonical full name during seed generation, verify by
  actual diff, not by line-count-alone inference (a mistake caught and corrected mid-research
  this session — `bee_sz`/`beeline_sz` looked "maybe unpaired" from line counts alone until the
  file list was re-checked; don't repeat that shortcut in Specifications/Implementation).
- **No legacy PHP page exists for this** — confirmed via grep across
  `legacy/simbox-desktop-v2014/www/simbox/*.php` (only tangential "направление" mentions in
  `plan.php`'s per-SIM billing-direction docs and `sim.php`'s column header — unrelated concept,
  see below). This is being built from scratch, per the user's framing ("не успели доделать").
- **One "direction" concept, two touchpoints — corrected mid-session after user clarification**:
  a zone in the new page *is* a "направление" — the exact same thing the Sims table's `напр`
  column already shows one icon+letter-code for per SIM (e.g. Beeline icon with a "С" mark =
  Билайн СПб = zone id `beeline_spb`). `icon_map.dart`'s `_naprMap` is today's *display* catalog
  (short code → icon + Russian name) for that concept; this flow adds the missing *routing*
  layer underneath — the actual DEF-code pattern list that decides which zone a dialled number
  falls into. Every zone here should reuse `_naprMap`'s id/icon/name where one already exists.
  Initial drafting of 01-requirements.md wrongly framed these as two separate concepts not to be
  conflated — corrected before approval.
- **Architecture precedent**: `lib/features/command_sets/` (built after fix2, NOT part of any
  prior VDD flow in this project — discovered fully-formed this session) is now the established
  pattern for "a new CRUD admin section with a record list + detail pane": repository interface
  + in-memory impl (create/replace/delete/reset, throws a typed exception on invalid ops),
  ChangeNotifier controller with draft/dirty/save/cancel and an unsaved-changes switch-guard,
  responsive workspace (`narrow = width < 900` collapses list-pane to a dropdown row), `FugueIcon`
  widget (`assets/fugue/*.png`, not the older `AdmIcon`/`assets/imgs/*` set), and design tokens
  `T.denseHit`/`T.narrowHit`/`T.brandGradient` (newer additions to `lib/design/tokens.dart` since
  fix1/fix2). This flow's zones feature follows the same architecture, scaled down (no
  multi-section detail — a zone has one editable body, its code list).
- **fix1 and fix2 status**: both implemented and committed on the nested
  `design/simbox-web-design-prototype-v2026` repo (commits `709d543`, `022a1f0`), plus a further
  commit `5ac3cdb` (command_sets feature + Fugue assets + pubspec/token updates) made outside
  any VDD flow in this project, all authored by Anton Dodonov. Working tree was clean before
  this flow's research began (only harmless `.dart_tool`/`pubspec.lock` diffs from a `flutter
  pub get`). fix2's own `_status.md`/implementation log were left mid-verification (blocked on
  starting a local dev server for a Chrome check) when this new request arrived — not resumed;
  noted as a loose end, not a blocker for this new flow, since the code itself is committed and
  the build succeeded before the interruption.

## Fork History

N/A — new flow.

## Next Actions

Flow complete — implementation done and approved. Remaining, optional:
1. User's own call on committing (nested repo, no push without explicit ask).
2. Optional DOCUMENTATION phase (client-facing README) — not started, only pursue if requested.
3. Optional: a real pixel check of the <900px responsive layout outside this automation
   session's tooling limitation, if ever in doubt (logic is a verbatim copy of `command_sets`'
   already-shipped equivalent, so risk is low).
