# Status: vdd-simbox-web-design-prototype-zones-uiux

## Current Phase

PLAN

## Phase Status

REVIEW

## Last Updated

2026-09-02 by Claude

## Blockers

- Waiting on user approval of the Iteration 2 amendments to 03-specifications.md and
  04-plan.md before starting Implementation. (Requirements + Visual approved 2026-09-02.)

## Progress

**Iteration 1 (DEF-codes only) — shipped, see 05-implementation-log.md's first session:**
- [x] Requirements/Visual/Specifications/Plan/Implementation all done and approved 2026-09-02.

**Iteration 2 (group-selection rule layer) — in progress:**
- [x] Requirements amended
- [x] Requirements approved
- [x] Visual mockups amended
- [x] Visual approved
- [x] Specifications amended
- [ ] Specifications approved
- [x] Plan amended
- [ ] Plan approved
- [ ] Implementation started
- [ ] Implementation complete
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

## Context Notes (Iteration 2 — group-selection rule layer)

- **Discovery source**: user pointed to `legacy/simbox-desktop-v2014/asterisk/extensions/
  extensions_dial_zones.conf` (dialplan) and `libsCpp/asterisk-chan-svistok/src/select.c`
  (channel-driver device selection) — read both fully this session.
- **What a zone actually is, precisely**: DEF-codes decide which zone a dialled number belongs
  to (iteration 1, done). `extensions_dial_zones.conf`'s `[macro-makecall-std]` then maps each
  zone to an ORDERED list of `Macro(makecall-ru, <selector>, ...)` calls — Asterisk falls
  through to the next one only if the previous `Dial()` fails (`Goto(h-${DIALSTATUS},1)` in
  `[macro-dialdongle]`), i.e. this is a **priority-ordered fallback list**, not a set.
- **Selector string grammar** — `L<N><alg><type>=<XX><GGG>` (e.g. `L1D=NS101`), parsed byte-by-
  byte by `get_cr_group()` in `select.c` (lines ~148-177):
  - `L` — literal marker.
  - `<N>` (digit 0-9) — index into the SIM's `limit[10]` array (`chan_dongle.h:134`) — the same
    LIMIT0..LIMIT9 concept as the Sims table's `LIMIT0`/`LIMIT1` columns (`limitnum`).
  - `<alg>` (one of `^ * d D > <`) — load-balancing tie-breaker among candidate SIMs in the
    matched group (`alg`, compared against each SIM's own per-slot `alg[10]` tag deeper in
    `select.c`, e.g. `'P'`/`'v'` gate PRO-traffic routing — full ranking logic (lines 400-900ish)
    is intricate; not required reading to expose an editable rule, just to label the known
    letters sensibly in the UI).
  - `<type>` (one of `- = _`) — whether that limit slot is enforced (`-`/`_` = skip the check).
  - `<XX>` (2 uppercase letters) — `billing_direction`, written back onto the SIM after a
    successful call (`select.c:1036`, `select.c:1075`). Overlaps with `icon_map.dart`'s
    `_naprMap` codes for most zones (`NS`=megafon_spb, `BS`=beeline_spb, `SS`=mts_spb, `KU`=
    kievstar — all consistent with the zone's own rules) but **is its own namespace**, not
    guaranteed identical — e.g. `rostel_spb_mob`'s rules use code `SR`, which in `_naprMap` is
    already `mts_ru`'s code; treat as a separate, zone-level, freely-editable 2-letter field
    (default-suggest the `_naprMap` code when the zone has one, but don't force equality).
  - `<GGG>` (integer) — target **SIM group number**, the exact same `group` field already shown
    per-SIM in the Sims table (101, 333, 334, ... in mock data).
- **Scope boundary decided**: only `[macro-makecall-std]` (the default/normal-traffic rule set)
  is in scope for this iteration. The file also defines separate rule sets for special traffic
  modes — `makecall-pre` (prepaid surcharge), `makecall-pos` (postpaid), `makecall-sou`
  ("source"/test calls), `makecall-mag` ("mayak"/beacon), `makecall-nav` (blocked subscriber) —
  each with its own, mostly-sparser, per-zone rule list. These are a **separate, deeper,
  out-of-scope layer** for this iteration (Won't Have) — surfaced here only so a future flow
  doesn't have to rediscover them.
- **Not every zone has std rules today**: some zones (e.g. `beeline_sz`) have no case at all in
  `[macro-makecall-std]`'s dispatcher — calls for them currently fall through with no group
  rule. Some zones' dispatch `GotoIf` is commented out even though the rule block still exists
  below it (e.g. `meg_ru` — rules present, unreachable) — both are exactly the kind of
  legacy incompleteness ("не успели доделать") this page should surface and let the operator
  fix, not silently normalize away. New zones (created via this UI) naturally start with zero
  rules, same as they start with zero DEF-codes.
- **UI shape decided via AskUserQuestion**: add a second editable section per zone — an
  ordered, add/remove/reorder list of structured rule rows (limit slot, alg, type, group number;
  billing code stays zone-level, not per-rule, since every rule under one zone in the legacy
  data uses that same code) — alongside (not replacing) the existing DEF-codes textarea.
  Structured rows, not a textarea, since each rule has multiple distinct typed fields (unlike
  a DEF-code, which is one opaque pattern string).

## Fork History

N/A — new flow.

## Next Actions

Flow complete — implementation done and approved. Remaining, optional:
1. User's own call on committing (nested repo, no push without explicit ask).
2. Optional DOCUMENTATION phase (client-facing README) — not started, only pursue if requested.
3. Optional: a real pixel check of the <900px responsive layout outside this automation
   session's tooling limitation, if ever in doubt (logic is a verbatim copy of `command_sets`'
   already-shipped equivalent, so risk is low).
