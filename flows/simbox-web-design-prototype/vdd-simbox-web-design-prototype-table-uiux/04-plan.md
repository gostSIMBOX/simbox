# Implementation Plan: simbox-web-design-prototype-table-uiux

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-09-05
> Specifications: [03-specifications.md](03-specifications.md)

## Summary

Bottom-up implementation order: shared vocabulary first (`terminology.dart` → `icon_map.dart`),
then the data shape (`models.dart`), then the page that consumes both (`sims_page.dart`), then the
sample data that exercises it (`mock.dart`), then manual browser verification. Each task is small
enough to `flutter analyze` independently. The one open design question from Specifications (the
`pro` column's blue-text approach) is resolved as part of Task 4.3, using the recommended inline
approach — flagged again there in case that turns out to be wrong once it's on screen.

## Task Breakdown

### Phase 1: Vocabulary (terminology + icon lookups)

#### Task 1.1: Add 5 terminology entries
- **Description**: Add `call.live.dial`, `call.live.active`, `qos.spam`, `qos.imo`, `qos.sys` to
  the `terminology` map, wording copied verbatim from the icon-statuses flow's approved spec.
- **Files**: `lib/data/terminology.dart` — Modify
- **Dependencies**: None
- **Verification**: `termById('call.live.dial')` etc. resolve without falling back to the
  "Unknown term" placeholder.
- **Complexity**: Low

#### Task 1.2: Extend `Ico.group()` with holiday pause variants
- **Description**: Add `pause == 2/12/22` branches (workday variants 1/11/21 already exist).
- **Files**: `lib/data/icon_map.dart` — Modify
- **Dependencies**: None
- **Verification**: Unit test — `Ico.group(150, 2)` etc. return the `day_holiday.png` pair.
- **Complexity**: Low

#### Task 1.3: Extend `Ico.qos()`'s `_qosMap` with SPAM/IMO/SYS
- **Description**: Add the three entries per spec (`SYS` intentionally reuses `qos/inos.png`).
- **Files**: `lib/data/icon_map.dart` — Modify
- **Dependencies**: Task 1.1 (terms must exist first)
- **Verification**: `Ico.qos('SPAM','I')` etc. resolve to the specified assets/tooltips.
- **Complexity**: Low

#### Task 1.4: Add `Ico.fas()`, `Ico.vip()`, `Ico.pre()`, `Ico.pos()`, `Ico.liveCall()`
- **Description**: Four small new lookup helpers per spec, using already-verified asset paths.
- **Files**: `lib/data/icon_map.dart` — Modify
- **Dependencies**: Task 1.1 (`liveCall` needs the two new terms)
- **Verification**: Each returns the exact asset for its documented input range; `null`/throws
  match the spec's edge-case table.
- **Complexity**: Low

### Phase 2: Data shape

#### Task 2.1: Add new fields to `Sim`
- **Description**: Add the ~18 fields from the spec's Data Models section (`pro`, `proWarn`,
  `vip`, `pre`, `pos`, `fas`, `liveState`, `elapsedSec`, `cooldownMax`, `emType`, `numberb`,
  `numbera`, `msm`, `smsSent`, `smsSoft`, `smsHard`, `pddas`, `limits`, `limitPalevo`, `dongleA`).
  Remove `lim0`/`lim1`, superseded by `limits`/`limitPalevo`.
- **Files**: `lib/data/models.dart` — Modify
- **Dependencies**: None (can run in parallel with Phase 1)
- **Verification**: `flutter analyze` — confirms every removed-field reference elsewhere in the
  repo is caught at compile time (there should be exactly one: `sims_page.dart`'s `lim0` `ColDef`,
  fixed in Task 3.6).
- **Complexity**: Medium (many fields, but each is a single-line addition; the risk is naming
  consistency with the spec, not logic)

### Phase 3: Page changes (`sims_page.dart`'s `_cols()`)

Each sub-task touches one column group and can be verified independently by running the app and
looking at just that column, but all land in the same file/method — sequence them to avoid
merge-style confusion within one editing session, not because of a real dependency between them.

#### Task 3.1: `group` column — no code change needed here
- **Description**: `_cols()`'s existing `group` `ColDef` already calls `Ico.group(...)`; Task 1.2
  makes it automatically pick up the holiday variants. Confirm no edit needed, just re-verify.
- **Files**: None
- **Dependencies**: Task 1.2
- **Verification**: Mock row with `pause: 2` renders the holiday-pause icon pair.
- **Complexity**: Low

#### Task 3.2: `spec` column — 5-icon stack
- **Description**: Replace the single-icon `Cell(icons: [if (Ico.spec(s.spec) != null) ...])` with
  the 5-source stack from the spec (vip, pre, pos, fas, spec-code, in that order).
- **Files**: `lib/pages/sims_page.dart` — Modify
- **Dependencies**: Task 1.4, Task 2.1
- **Verification**: Mock row with all 5 flags active shows all 5 icons in legacy's order; a fully
  inactive row shows an empty cell (no crash, no stray spacing).
- **Complexity**: Low

#### Task 3.3: `io` column → full live-call/state cell
- **Description**: Replace the current 2-icon `io` `ColDef` with the composed cell from the spec
  (live-call icon + io + qos icons, `em_type` mono line, elapsed/cooldown text, busy numberb/numbera
  subs). Add the `_busyNumberB`/`_busyNumberA` helper functions next to `_log()`.
- **Files**: `lib/pages/sims_page.dart` — Modify
- **Dependencies**: Task 1.3, Task 1.4, Task 2.1
- **Verification**: Four mock rows exercise dialing/ring/active/cooldown; one SOU-tagged busy row
  confirms the numberb split and the "Внутренний звонок между SIM" tooltip (never "self-call").
- **Complexity**: Medium (most state combinations of any single column in this pass)

#### Task 3.4: `may` column → 4-line MAY/MON/MSM/SMS cell
- **Description**: Replace `Cell(text: 'MAY ${s.may}', sub: 'MON ${s.mon}')` with the 4-line
  `\n`-joined text from the spec; widen column from 72→96.
- **Files**: `lib/pages/sims_page.dart` — Modify
- **Dependencies**: Task 2.1
- **Verification**: Mock row shows all 4 lines, none clipped at 96px at the app's default zoom.
- **Complexity**: Low

#### Task 3.5: Add `pddas` column
- **Description**: New `ColDef` between `asrl` and `pdd0`.
- **Files**: `lib/pages/sims_page.dart` — Modify
- **Dependencies**: Task 2.1
- **Verification**: Column appears in the right position and in the columns-editor picker.
- **Complexity**: Low

#### Task 3.6: Replace `lim0`/`lim1` with looped `LIMIT0..LIMIT5`
- **Description**: Remove the old single `lim0` `ColDef`; generate 6 `ColDef`s in a loop per spec,
  each with its own `ipalevo.png` conditional icon.
- **Files**: `lib/pages/sims_page.dart` — Modify
- **Dependencies**: Task 2.1
- **Verification**: 6 columns appear in order; a mock row with `limitPalevo[3] = true` shows the
  flag icon only on `LIMIT3`, with the existing (unresolved) `captcha.pal` tooltip text verbatim.
- **Complexity**: Low

#### Task 3.7: `dongle` column — add hub-port sub-line
- **Description**: Add `sub2: s.dongleA` to the existing `dongle` `ColDef`.
- **Files**: `lib/pages/sims_page.dart` — Modify
- **Dependencies**: Task 2.1
- **Verification**: A `dongle0*` mock row shows the hub/port sub-line; a non-hub row shows nothing
  extra.
- **Complexity**: Low

#### Task 3.8: Add `pro` column, resolve the blue-text open question
- **Description**: New `ColDef` per spec. Resolve Specifications' one Open Design Question by
  implementing the recommended approach: an inline `Text(s.pro, style: T.cell.copyWith(color:
  T.brandDeep))` built directly in this `ColDef`'s `build`, bypassing `_cell()`'s shared stacking
  helper for this one column only (not a `Cell`/`dense_table.dart` change).
- **Files**: `lib/pages/sims_page.dart` — Modify
- **Dependencies**: Task 2.1
- **Verification**: A mismatch row (`proWarn: true`) renders in `T.brandDeep` blue, not
  `T.cellAlarm` red; a matching row renders in the plain cell color.
- **Complexity**: Medium (the one place this plan deviates from the "just add a `ColDef`" pattern
  — worth a second look once it's actually on screen, per the flag in Specifications)

### Phase 4: Sample data

#### Task 4.1: Extend `mock.dart`'s existing 5 `Sim(...)` rows
- **Description**: Add the ~18 new fields to every existing literal with plausible, varied values
  (not all-default/all-zero, so the visual review isn't blank columns).
- **Files**: `lib/data/mock.dart` — Modify
- **Dependencies**: Task 2.1
- **Verification**: `flutter analyze` clean (every `Sim(...)` call is exhaustively required or
  defaulted).
- **Complexity**: Medium (breadth, not difficulty — 5 rows × 18 fields)

#### Task 4.2: Add targeted scenario rows
- **Description**: Ensure the mock set includes at least one row each for: holiday pause (2/12/22),
  all-5-icons-active spec cluster, each of dialing/ring/active/cooldown, a SOU busy call, a `pro`
  mismatch, and a `limitPalevo` flag on a slot other than 0/1 (to prove the loop isn't hardcoded to
  the first two).
- **Files**: `lib/data/mock.dart` — Modify (new rows, or repurpose existing ones)
- **Dependencies**: Task 4.1
- **Verification**: Matches 05-implementation-log.md's manual verification checklist one-for-one.
- **Complexity**: Low

### Phase 5: Verification

#### Task 5.1: Static checks
- **Description**: `flutter analyze`, existing test suite.
- **Files**: None
- **Dependencies**: All of Phase 1-4
- **Verification**: Clean run, no new warnings.
- **Complexity**: Low

#### Task 5.2: Manual browser verification
- **Description**: Run the manual checklist from 03-specifications.md's Testing Strategy against
  the running app (`flutter run -d chrome` or equivalent).
- **Files**: None
- **Dependencies**: Task 5.1
- **Complexity**: Low

## Dependency Graph

```
1.1 ─┬─→ 1.3 ─┐
     └─→ 1.4 ─┼─→ 3.2 ─┐
2.1 ─────┬────┴─→ 3.3 ─┼─→ 4.1 ─→ 4.2 ─→ 5.1 ─→ 5.2
1.2 ─────┤            │
         ├───────────→ 3.4 ─┤
         ├───────────→ 3.5 ─┤
         ├───────────→ 3.6 ─┤
         ├───────────→ 3.7 ─┤
         └───────────→ 3.8 ─┘
```

## File Change Summary

| File | Action | Reason |
|------|--------|--------|
| `lib/data/terminology.dart` | Modify | 5 new term IDs (Task 1.1) |
| `lib/data/icon_map.dart` | Modify | Group holiday pause, qos SPAM/IMO/SYS, new fas/vip/pre/pos/liveCall helpers (Tasks 1.2-1.4) |
| `lib/data/models.dart` | Modify | ~18 new `Sim` fields, remove `lim0`/`lim1` (Task 2.1) |
| `lib/pages/sims_page.dart` | Modify | 6 column changes + 1 new column + 2 helper functions (Tasks 3.1-3.8) |
| `lib/data/mock.dart` | Modify | Extend 5 existing rows + targeted scenario coverage (Tasks 4.1-4.2) |

No files created, no files deleted, no files outside `design/simbox-web-design-prototype-v2026/lib/`
touched.

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| `pro` column's inline-`Text` approach looks visually inconsistent once on screen (font weight, alignment) next to `_cell()`-rendered columns | Medium | Low | It's one column; if it looks wrong, swap to the `Cell.tint` alternative from Specifications — contained, no ripple |
| Widened `may` column (72→96) or new `LIMIT0-5`×6 columns push total table width uncomfortably far, requiring more horizontal scroll | High (expected) | Low | Table already scrolls horizontally by design (`DenseTable`'s `SingleChildScrollView`); this is a known, accepted tradeoff of the approved "6 separate columns" decision, not a defect |
| `mock.dart`'s 5 rows aren't enough to demonstrate every new state (holiday pause × 3, live-call × 4, SOU, pro-mismatch, palevo-on-slot-3+) | Medium | Medium | Task 4.2 explicitly enumerates the required scenario coverage as its own checklist |

## Rollback Strategy

Every task is additive/localized to 5 files with no schema/persistence layer — reverting is a
plain `git revert`/`git checkout` of this flow's commit(s); no data migration exists to unwind.

## Checkpoints

After each phase:

- [ ] Phase 1: `flutter analyze` clean; new `Ico.*`/`termById` calls resolve in a scratch test.
- [ ] Phase 2: `flutter analyze` shows exactly the expected `lim0`/`lim1` breakage in
      `sims_page.dart`, nothing else.
- [ ] Phase 3: App runs; every touched column renders without overflow/crash on the existing 5
      mock rows (before Phase 4's new scenario rows land).
- [ ] Phase 4: Every scenario in Task 4.2's checklist has a visible mock row.
- [ ] Phase 5: Manual verification checklist fully checked off.

## Open Implementation Questions

None — the only open item (pro column styling) is resolved as a task-level decision (3.8), with an
explicit fallback noted in Risk Assessment if it doesn't look right on screen.

---

## Approval

- [ ] Reviewed by:
- [ ] Approved on:
- [ ] Notes:
