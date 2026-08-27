# Status: sdd-asterisk-chan-svistok-chan-dongle

## SUPERSEDED

**2026-08-26**: this flow is superseded by
`flows/asterisk-chan-svistok/sdd-asterisk-chan-svistok-chan-dongle-v2/`.
Its classification content (Full File Inventory, Function-Level
Classification, Header Changes, Build System Changes) was carried forward
into v2 unchanged and remains valid — nothing here was wrong. This flow
is left as-is (not deleted) for history; do not continue work in this
directory, use v2 instead.

## Current Phase

SPECIFICATIONS

## Phase Status

DRAFTING (module-split content moved out — awaiting review of the
remaining single-flow-of-truth classification content)

## Last Updated

2026-08-26 by Claude

## Blockers

None.

## Progress

- [x] Requirements drafted (v1.0)
- [x] Requirements open questions resolved (independent analysis; full scope)
- [x] Module-split revision (v1.1) drafted, then **moved out** to
      `flows/sdd-res-simbox/` per user request (v1.2 reflects the move)
- [ ] Requirements approved
- [x] Specifications drafted (v1.0, single-module layout)
- [x] Module-split layout (v1.1) drafted, then **moved out** to
      `flows/sdd-res-simbox/` (v1.2 reflects the move)
- [ ] Specifications approved
- [ ] Plan drafted
- [ ] Plan approved
- [ ] Implementation started
- [ ] Implementation complete

## Context Notes

- User asked (2026-08-26): "все спеки и reqs что связаны с res-simbox-*
  перенеси из предыдущего флоу в новый" — move everything related to
  `res-simbox-*` (the three-module split) out of this flow into a new one,
  `flows/sdd-res-simbox/`.
- **Completed the move**: `01-requirements.md`'s "Version 1.1 Revision:
  Three-Module Split" section and `02-specifications.md`'s "Planned
  Module Layout (v1.1)" section (plus the module-split-specific Edge Cases
  and Open Design Questions: `pvt_start()` coupling, discovery/
  programmator module-lifecycle restructuring, `hub-ctrl.c`/`reader/`
  placement) were removed from both documents here and now live in
  `flows/sdd-res-simbox/01-requirements.md` and
  `flows/sdd-res-simbox/02-specifications.md` respectively. Both documents
  here were bumped to version 1.2 with a short pointer section in place
  of the moved content.
- This flow now owns exactly one thing: the independent file/function
  classification of `legacy/asterisk-chan-svistok-v2014` against upstream
  `chan_dongle` (bg111) — Full File Inventory, Function-Level
  Classification (~380 functions across 17 module files), Header Changes
  Summary, Build System Changes. `sdd-res-simbox` references this rather
  than duplicating it, so the two flows don't drift apart.
- One item stayed here deliberately even though it also matters to
  `sdd-res-simbox`: the "wrapper mechanism for `UNCHANGED` functions"
  open design question (direct link vs. thin wrapper) — it's not specific
  to the module split (it would exist even in the original single-module
  plan), so it stays owned here, with a note in both flows that
  `res_simbox_core` inherits whichever answer is chosen.
- Everything else (dead-code disposition of `dsp.c`/`share_mysql.c`,
  `adiscovery_core_new.c` abandonment, `reader/`'s unclear status,
  new-function grouping granularity) is duplicated conceptually between
  the two flows since both need to resolve it for their own scope
  (classification-level vs. module-assignment-level) — kept as separate
  open questions in each, not an error.

## Fork History

Not forked (sibling of `sdd-asterisk-chan-svistok`, created independently
per explicit user choice). `flows/sdd-res-simbox/` is a **content move**,
not a fork, of this flow's module-split material.

## Next Actions

1. This flow's own remaining open questions (wrapper mechanism, dead code,
   `adiscovery_core_new.c`, `reader/`, grouping granularity) still need
   resolution before "specs approved" — see `02-specifications.md`'s Open
   Design Questions.
2. Get "requirements approved" + "specs approved" for the classification
   work itself.
3. Move to Plan phase for the classification/carry-forward mechanics —
   coordinate with `flows/sdd-res-simbox/`'s own Plan phase since the
   actual file copies will need to happen in an order that respects both
   (e.g. core's `src/` carry-forward happens once per the wrapper-
   mechanism decision, then `sdd-res-simbox` places each carried file into
   its module directory).
