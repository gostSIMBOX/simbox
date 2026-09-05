# Implementation Plan: Plans editor UI/UX

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-09-02
> Specifications: [03-specifications.md](03-specifications.md)

## Summary

Build `lib/features/plans/` end-to-end, mirroring the already-shipped `command_sets`/`zones`
feature shape: data layer (model, repository, generated seed) → controller (draft/save/cancel,
banner state) → UI (workspace, registry, detail sections, explanation banner) → wiring into
`AppState`/`plan_page.dart`, deleting the superseded `mock.dart` plan rows and old ultra-wide
grid last, once nothing references them. Seed generation is a one-off Python script (not
committed, matching the Zones precedent) run against the already-extracted legacy `plan/`
archive.

## Task Breakdown

### Phase 1: Data layer

#### Task 1.1: `Plan` and `DirectionSlot` models
- **Description**: `lib/features/plans/models.dart` — `DirectionSlot` and `Plan` per
  03-specifications.md's Interfaces section, with `copyWith` and value `==`/`hashCode`
  (directions compared via list equality, mirroring `Zone`'s `_listEquals` helper).
- **Files**: `lib/features/plans/models.dart` - Create
- **Dependencies**: None
- **Verification**: `flutter analyze` clean; a scratch `main()` (or just inspection) confirms
  `copyWith`/`==` behave like `Zone`'s.
- **Complexity**: Low

#### Task 1.2: `PlanRepository` / `InMemoryPlanRepository`
- **Description**: CRUD interface + in-memory impl, delete guard for `id == 'default'` and for
  any plan referenced by a live `Sim.plan`, via an injected `List<Sim> Function()` so the check
  reads current mock data rather than a stale snapshot. Typed `PlanRepositoryException`.
- **Files**: `lib/features/plans/repository.dart` - Create
- **Dependencies**: Task 1.1
- **Verification**: `flutter analyze` clean; shape matches `zones/repository.dart` 1:1 (create/
  replace/delete/reset + exception type).
- **Complexity**: Low

#### Task 1.3: Legacy field audit script
- **Description**: One-off Python script (scratchpad, not committed) that reads the extracted
  `legacy/simbox-desktop-v2014/var/simbox/plan/` directory, groups files by `<plan_id>` prefix,
  cross-references `plan/plan.list` for the 33 active IDs, derives the 8 audit-only IDs, and
  prints a mapping table: raw field suffix → modeled `Plan` field (or "UNMAPPED" with example
  raw values) using the normalization table below. This is the audit deliverable itself — not
  code that ships in the app.
- **Normalization table** (built from the 95 suffixes found this session):
  - Identity/ownership: `nabor`→`commandSetId`, `priority`→`priority`, `pro`→`proTag`
  - Capacity: `online_max`→`onlineMax`, `add_max`→`addMax` (`online_adddaymax`/`online_need` are
    runtime counters, UNMAPPED/audit-only per Requirements)
  - Call modes/quality: `can_in`→`canIn`, `can_out`→`canOut`, `can_sout`→`canSout`,
    `notvip`→`notVip`; `ivip/igoo/inor/ibad/inew/inos/irob/iblo`→`qualityFlags` (set membership);
    `capok`→`capOk`, `capnew`→`capNew`, `capfail`→`capFail` (VERIFIED independent booleans, not
    one mode; `capno`/`capyes` unset everywhere — UNMAPPED; `capnnew` mismatches `capnew` on
    2/33 plans — UNMAPPED, not merged as an alias)
  - Timing: `diff_slow`→`diffSlow`, `diff_min`→`diffMin`, `diff_min_out`→`diffMinOut`,
    `time_wake/sleep`→`timeWake/Sleep` (`-1`→`null`, the pair the banner names),
    `time_work_wake/sleep`→`timeWorkWake/Sleep` (`-1`→`null`), `time_holiday_wake/sleep`→
    `timeHolidayWake/Sleep` (`-1`→`null`) (`diff_goo/diff_min_goo/diff_min_imode/diff_min_inode/
    diff_min_nor/diff_min_sout/diff_min_vip/diff_nor/diff_vip/i_mode` are UNMAPPED — narrower
    legacy variants not evidenced as distinct from the four modeled timing fields; logged for
    review, not silently dropped)
  - Directions: `alg.N/nodiff.N/limit_max.N/limit_hard.N` (N=0-5)→`directions[N]` (`alg.N` is a
    VERIFIED numeric code, not a character)
  - Incoming generation: `iatt_min/max/soft`→`iattMin/Max/Soft`, `in_acd_min`→`inAcdMin`,
    `in_acd_max`→`inAcdMax`, `out_acd_min`→`outAcdMin`, `out_acd_max`→`outAcdMax`
    (double-underscore `in_acd__min`/`in_acd__max`/`out_acd__min`/`out_acd__max` disagree with
    the single-underscore fields on 5/15 plans that carry both — UNMAPPED, not merged),
    `forwarding`→`forwarding`, `out_in_ans`→`outInAns` (VERIFIED integer code, not boolean),
    `conn`→`conn`, `rand`→`rand` (`rnd` is always `1` where present and not evidenced as the same
    field — UNMAPPED, not merged), `in_wait`→`inWait`, `in_sound`→`inSound`
  - SMS/beacon: `may_limit`→`mayLimit`, `mon_limit`→`monLimit`, `msm_limit`→`msmLimit`,
    `smsout_soft/hard`→`smsoutSoft/Hard`, `satt_soft/hard/soft_day/hard_day/soft_total/
    hard_total`→matching `satt*` fields, `nospam`→`nospam` (VERIFIED integer code, not boolean)
  - Everything else found by the script but not listed above is printed as UNMAPPED with its
    raw value for manual review before Task 1.4 — includes `limit_may`/`limit_mon` (distinct
    from `may_limit`/`mon_limit`), `satt_min`/`satt_max`, `outin`, `out_in_dur`,
    `online_adddaymax`/`online_need`, `ime`/`ima`/`imb`/`imc`/`imd`/`imn`/`ine0`/`inec`/`inem`
    (a second im*/in* cluster distinct from the modeled `qualityFlags` set).
- **Files**: none committed (scratchpad script + printed output reviewed inline)
- **Dependencies**: Task 1.1 (need final field names to map onto)
- **Verification**: Script runs clean over all 4175 archive files; UNMAPPED list reviewed and
  judged acceptable (small, low-value legacy variants) before proceeding.
- **Complexity**: Medium

#### Task 1.4: Generate `seed.dart`
- **Description**: Extend the Task 1.3 script to emit `lib/features/plans/seed.dart` — 33
  `Plan` const records built from the archive via the normalization table, in `plan.list`'s
  order. The 8 audit-only ids are not emitted as `Plan` records (Requirements' resolved Open
  Question #1); their raw dumps stay in the script's printed audit output only.
- **Files**: `lib/features/plans/seed.dart` - Create
- **Dependencies**: Task 1.1, Task 1.3
- **Verification**: `flutter analyze` clean; spot-check 3-4 plans' key fields (e.g.
  `tele2_spb_good.online_max`, `default.time_wake`) against `cat plan/<id>.<field>` directly.
- **Complexity**: Medium

### Phase 2: Controller

#### Task 2.1: `PlanController`
- **Description**: `ChangeNotifier` with `load/records/visiblePlans/selected/isDirty/
  requestSelectPlan/keepEditing/discardAndContinue`, per-family `update*` draft-first mutators,
  `updateDirectionSlot` (rejects slot outside 1-4 as a no-op), `createPlan`/`deletePlan`/
  `resetDemo`, plus `explanationOpen`/`toggleExplanation()` defaulting to `true`. Mirrors
  `ZoneController`'s shape exactly for the shared plumbing (draft/dirty/guard).
- **Files**: `lib/features/plans/controller.dart` - Create
- **Dependencies**: Task 1.2
- **Verification**: `flutter analyze` clean; manual trace of one edit→save→cancel cycle against
  `ZoneController`'s equivalent methods to confirm parity.
- **Complexity**: Medium

### Phase 3: UI

#### Task 3.1: `ExplanationBanner`
- **Description**: Dismissible banner (verbatim 4-paragraph copy from Requirements/Visual), "?"
  reopen affordance rendered by the workspace title row when closed. Pure presentation, driven
  by `controller.explanationOpen`/`toggleExplanation()`.
- **Files**: `lib/features/plans/explanation_banner.dart` - Create
- **Dependencies**: Task 2.1
- **Verification**: Visual check in running app — open by default, X closes it, "?" reopens it
  with identical content.
- **Complexity**: Low

#### Task 3.2: `PlanRegistryPane`
- **Description**: Search box, command-set filter dropdown, add button, scrollable plan list
  with selection dot + command-set + usage-count subtitle. Mirrors `zones/registry_pane.dart`.
- **Files**: `lib/features/plans/registry_pane.dart` - Create
- **Dependencies**: Task 2.1
- **Verification**: Filter/search narrow the list correctly against the seeded 33 plans.
- **Complexity**: Low

#### Task 3.3: `PlanDetailHeader`
- **Description**: ID (read-only), command-set dropdown (direct edit, sourced from the live
  `CommandSetController`), priority field, PRO tag field, usage count (computed from
  `AppState.sims`), Clone/Delete overflow menu.
- **Files**: `lib/features/plans/detail_header.dart` - Create
- **Dependencies**: Task 2.1
- **Verification**: Changing the command-set dropdown dirties the draft and is reflected
  immediately in Task 3.6's route context.
- **Complexity**: Medium

#### Task 3.4: Policy-family sections (Identity, Capacity, Call modes/quality, Timing, Incoming generation, SMS/MAY-MON-MSM)
- **Description**: Six collapsible section widgets under `lib/features/plans/sections/`, one
  per remaining family (Identity fields live in the header per Task 3.3, so this task covers the
  other six), each a thin form bound to the matching `PlanController.update*` method. Timing
  section renders `-1`→`null` as a "выключено" state per Specifications' edge case table.
- **Files**: `lib/features/plans/sections/capacity_section.dart`,
  `call_modes_section.dart`, `timing_section.dart`, `incoming_generation_section.dart`,
  `sms_generation_section.dart` - Create
- **Dependencies**: Task 2.1
- **Verification**: Each field round-trips through Save/Cancel; `capMode`/`qualityFlags`
  render as their finite set, not raw legacy tokens.
- **Complexity**: Medium

#### Task 3.5: `DirectionsSection` + Zones cross-reference
- **Description**: Slots 1-4 as editable rows (alg/nodiff/limits), slots 0/5 as a fixed
  compatibility note. `routesForSlot(zones, commandSetId, slot)` per Specifications, using the
  `<operator>_<region>` prefix-match rule resolved in Specifications' "Resolved Design
  Decisions." Route chips render zone icon + name + billing code, "показать все N" for slots
  with more than a few matches, "нет данных для этого набора команд" when empty.
- **Files**: `lib/features/plans/directions_section.dart` - Create
- **Dependencies**: Task 2.1, requires `ZoneController` (shipped)
- **Verification**: Manually cross-check one plan's route chips against `zones` records sharing
  its command-set prefix; confirm live update when the command-set dropdown (Task 3.3) changes,
  pre-save.
- **Complexity**: Medium-High

#### Task 3.6: `PlansWorkspace` + dialogs
- **Description**: Assembles Tasks 3.1-3.5 into the registry+detail layout (wide) and the
  stacked layout (narrow, `< 900`) per 02-visual.md; unsaved-changes guard dialog; create dialog
  (Clone/Blank); delete dialogs (blocked/confirm) per Specifications' edge cases.
- **Files**: `lib/features/plans/workspace.dart`, `lib/features/plans/plan_dialogs.dart` - Create
- **Dependencies**: Tasks 3.1-3.5
- **Verification**: Full manual pass through Specifications' Manual Verification checklist.
- **Complexity**: Medium

### Phase 4: Wiring and cleanup

#### Task 4.1: Wire into `AppState` and `PlanPage`
- **Description**: `late final PlanController plans;` constructed/disposed in `AppState`
  alongside `commandSets`/`zones`; `lib/pages/plan_page.dart` rewritten as a thin wrapper
  (mirrors `zones_page.dart`) hosting `PlansWorkspace(controller: state.plans, zones:
  state.zones, commandSets: state.commandSets)`.
- **Files**: `lib/state/app_state.dart` - Modify; `lib/pages/plan_page.dart` - Modify
- **Dependencies**: Task 3.6
- **Verification**: App boots to the Планы page without error; navigating away/back preserves
  `explanationOpen` state.
- **Complexity**: Low

#### Task 4.2: Delete superseded mock data
- **Description**: Remove `mock.dart`'s `planRows`/`PlanRow` and the old `plan_page.dart`
  `_PlanCol`/`_planGroups` grid code, now unreferenced. Confirm via grep that nothing else reads
  `planRows` before deleting (Specifications' Migration/Rollout note).
- **Files**: `lib/data/mock.dart` - Modify
- **Dependencies**: Task 4.1
- **Verification**: `flutter analyze` clean, no dangling references.
- **Complexity**: Low

### Phase 5: Verification

#### Task 5.1: Full manual pass
- **Description**: `flutter analyze` (zero new errors), `flutter build web`, serve via
  `python3 -m http.server`, drive through `claude-in-chrome` against every item in
  Specifications' Manual Verification checklist (registry, filters, all 7 families, direct
  command-set edit, Directions route context + live update, delete guards, banner
  dismiss/reopen/persistence, narrow layout, no console errors).
- **Files**: None (verification only)
- **Dependencies**: All prior tasks
- **Verification**: Checklist fully passes; screenshots/console log reviewed.
- **Complexity**: Medium

## Dependency Graph

```
1.1 ─┬─→ 1.2 ─→ 2.1 ─┬─→ 3.1 ─┐
     │                ├─→ 3.2 ─┤
     └─→ 1.3 ─→ 1.4   ├─→ 3.3 ─┼─→ 3.6 ─→ 4.1 ─→ 4.2 ─→ 5.1
                       ├─→ 3.4 ─┤
                       └─→ 3.5 ─┘
```

## File Change Summary

| File | Action | Reason |
|---|---|---|
| `lib/features/plans/models.dart` | Create | `Plan`, `DirectionSlot` |
| `lib/features/plans/repository.dart` | Create | CRUD + delete guards |
| `lib/features/plans/seed.dart` | Create | 33 active plans from legacy archive |
| `lib/features/plans/controller.dart` | Create | Draft/save/cancel + banner state |
| `lib/features/plans/explanation_banner.dart` | Create | Dismissible banner |
| `lib/features/plans/registry_pane.dart` | Create | Search/filter/list |
| `lib/features/plans/detail_header.dart` | Create | Identity + command-set direct edit |
| `lib/features/plans/sections/*.dart` | Create | 6 policy-family forms |
| `lib/features/plans/directions_section.dart` | Create | Slots + read-only Zones cross-ref |
| `lib/features/plans/workspace.dart` | Create | Layout assembly, responsive |
| `lib/features/plans/plan_dialogs.dart` | Create | Create/delete/guard dialogs |
| `lib/state/app_state.dart` | Modify | Add `plans` controller |
| `lib/pages/plan_page.dart` | Modify | Thin wrapper, old grid deleted |
| `lib/data/mock.dart` | Modify | Remove `planRows`/`PlanRow` |

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Alias/typo normalization (Task 1.3) misses a field with real operator significance | Low | Medium | Script prints every UNMAPPED field for review before Task 1.4 proceeds; nothing silently dropped |
| `<operator>_<region>` prefix match (Task 3.5) fails to resolve some zones/command-sets with irregular legacy names | Low | Low | Falls into the existing empty-state UI ("нет данных"), not a crash; acceptable per Specifications' resolved decision |
| Seed generation script errors on an edge-case legacy value (e.g. malformed field file) | Low | Medium | Script run is inspected manually (Task 1.4 verification) before `seed.dart` is trusted |

## Rollback Strategy

1. All new code lives under `lib/features/plans/` plus additive changes to `app_state.dart`/
   `plan_page.dart` — revert those two files and delete the new directory to fully undo.
2. `mock.dart`'s `planRows` deletion (Task 4.2) is the only destructive edit to existing code;
   it's done last, after everything else is verified working, and is trivially restorable via
   git if needed.

## Checkpoints

After each phase, verify:

- [ ] `flutter analyze` shows no new errors/warnings vs. the pre-existing baseline
- [ ] `flutter build web` succeeds
- [ ] Behavior matches 03-specifications.md's Behavior Specifications and Edge Cases

## Open Implementation Questions

- [ ] None outstanding — Specifications' prior open questions were resolved before approval.

---

## Approval

- [ ] Reviewed by: Anton Dodonov
- [ ] Approved on:
- [ ] Notes:
