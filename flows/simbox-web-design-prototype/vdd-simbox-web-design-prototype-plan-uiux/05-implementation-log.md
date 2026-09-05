# Implementation Log: Plans editor UI/UX

> Started: 2026-09-02
> Plan: [04-plan.md](04-plan.md)

## Progress Tracker

| Task | Status | Notes |
|---|---|---|
| 1.1 Plan/DirectionSlot models | Done | |
| 1.2 PlanRepository/InMemoryPlanRepository | Done | |
| 1.3 Legacy field audit script | Done | Surfaced several corrections to Requirements/Specifications — see Discoveries |
| 1.4 Generate seed.dart | Done | 33 plans (not 37 — see Discoveries) |
| 2.1 PlanController | Done | |
| 3.1 ExplanationBanner | Done | |
| 3.2 PlanRegistryPane | Done | |
| 3.3 PlanDetailHeader | Done | Fixed: delete menu item now hidden for `default` |
| 3.4 Policy-family sections | Done | 5 files (Identity lives in header, Directions is separate) |
| 3.5 DirectionsSection + Zones cross-reference | Done | Verified live against real Zone/CommandSet data |
| 3.6 PlansWorkspace + dialogs | Done | |
| 4.1 Wire into AppState/PlanPage | Done | |
| 4.2 Delete superseded mock data | Done | `planRows`/`PlanRow`/`planShow`/`setPlanGroup` removed |
| 5.1 Full manual verification pass | Partial | See below — browser extension disconnected mid-pass |

## Session Log

### Session 2026-09-02 - Claude

**Started at**: Phase 1, Task 1.1 (Specifications and Plan already approved)
**Context**: Continuing plan-uiux from an approved Plan (04-plan.md); no code existed yet.

#### Completed
- All of Phase 1-4 (data layer, controller, UI, wiring, mock cleanup) — see Progress Tracker.
- Files created: `lib/features/plans/{models,repository,controller,workspace,detail_header,
  registry_pane,explanation_banner,directions_section,plan_dialogs}.dart`,
  `lib/features/plans/sections/{section_fields,capacity_section,call_modes_section,
  timing_section,incoming_generation_section,sms_generation_section}.dart`, `seed.dart`
  (generated).
- Files modified: `lib/state/app_state.dart` (added `plans` controller), `lib/pages/plan_page.dart`
  (rewritten as thin wrapper), `lib/data/mock.dart` (removed `planRows`/`PlanRow`, fixed 4 stray
  `Sim.plan` values that referenced command-set names instead of real plan ids), `lib/data/
  models.dart` (removed `PlanRow`).
- Verified by: `flutter analyze` clean throughout (only 2 pre-existing baseline infos, unrelated
  to this feature); `flutter build web` succeeds; extensive manual pass via `claude-in-chrome`
  against a served `build/web` (see Manual Verification below).

#### Manual Verification (via Chrome, against `python3 -m http.server 8734`)
- [x] Registry: all plans listed, search/filter work, correct usage counts (`default` → 4→5
  after the mock.dart fix, spot-checked against `Sim.plan` values).
- [x] Section editing: edited `onlineMax` on `default`, draft bar appeared, Save persisted,
  toast shown; field values cross-checked against raw archive files for `default` and
  `tele2_spb_good` (priority, diff_min, nospam, out_in_ans, alg.1, limits, quality flags, cap
  flags) — all exact matches.
- [x] Directions section: slot 0/5 compatibility notes render correctly; slots 1-4 show correct
  alg/nodiff/limits; route-context chips for `tele2_spb_good` match the live `tele2_spb` zone's
  actual `GroupRule`s exactly (slot 1 → 3 chips TS109/TS209/TS210, slot 3 → 1 chip TS102, slots
  2/4 → "нет данных", matching the zone having no rules for those slots).
- [x] Command-set direct edit: changing the dropdown live-updates Directions' route context
  *before* saving (switched to Beeline, chips changed to BS102/BS162/BS202 immediately); Cancel
  reverted cleanly.
- [x] Explanation banner: open by default, dismiss shows "?" affordance, "?" reopens with
  identical content, state survived (session-lifetime, not tied to selection).
- [x] Create (Clone): dialog matches Visual mockup (SegmentedButton, source dropdown, id/command-
  set fields); created `tele2_spb_test_clone` cloned from `tele2_spb_good`, verified cloned data
  correct, then deleted it via the confirm-dialog path (unreferenced-plan case) successfully.
- [x] Delete guard for `default`: **found a real bug** — the ⋮ menu unconditionally showed
  "Удалить" for every plan, including `default`, contradicting Specifications' edge case
  ("the delete action itself is absent/disabled in the UI, not merely blocked after
  confirmation"). Fixed in `detail_header.dart` (delete `PopupMenuItem` now conditional on
  `plan.id != 'default'`); rebuilt and re-verified in-browser that the menu now shows only
  "Клонировать" for `default`.
- [ ] Delete guard for a referenced-but-non-default plan (blocked dialog with usage count):
  code-reviewed only (same `inspectDelete`/`showDeletePlanDialog` path as the verified
  unreferenced-plan case, just gated by `impact.allowed`), not re-driven live after the
  `mock.dart` fix — the browser extension disconnected (`tabs_context_mcp` started returning
  "Browser extension is not connected") before this specific case could be re-driven.
- [ ] Narrow-width layout (`< 900`): not visually verified this session (same tooling
  limitation noted in prior flows' logs) — code mirrors Zones' `LayoutBuilder`/`compact` pattern,
  which was verified working in that earlier flow.

#### Deviations from Plan
- Added `PlanController.inspectDelete`/`PlanDeleteImpact` (mirroring `CommandSetController`'s
  established `inspectDelete`/`DeleteImpact` pattern) instead of the plan's originally-sketched
  ad-hoc re-derivation inside `plan_dialogs.dart` — cleaner separation, single source of truth
  for the delete-guard decision. Not a scope change, just an implementation-time cleanup.
- `PlanController` takes a `usageCount` callback directly (in addition to the repository's own
  `liveSimPlanIds` for its delete guard) rather than threading a separate `usageCount` parameter
  through every widget — simplifies `PlanRegistryPane`/`PlanDetailHeader` call sites.

#### Discoveries (significant — corrected already-approved Requirements/Specifications)
- **Plan count**: `plan.list` has **33** active plans, not 37 — the earlier-approved figure was
  wrong. Verified directly: `plan.list` is 38 lines, 5 are `-----------` separators. **8**
  audit-only ids, not 9 (`local` doesn't exist in the archive). Requirements/Specifications/Plan/
  `_status.md` all corrected in place, with the correction noted inline rather than silently
  overwritten.
- **`rostel_spb`**: is a real command set (shipped in `command_sets/seed.dart`, alongside
  `kievstar`/`life`/`velcom`) but owns **zero** plans in the legacy archive — an earlier draft
  had fabricated `rostel_sms`/`rostel_trash`/`rostel_good`/`localrostel_sms` plan ids that don't
  exist anywhere in `plan/`. Corrected; also verified the app's own command-set dropdown lists
  `Kyivstar`/`Velcom`/`life:)` as real, separate international-operator command sets.
- **Three distinct timing pairs**, not two: `time_wake`/`time_sleep` (the pair the Explanation
  Banner names), `time_work_wake`/`time_work_sleep`, `time_holiday_wake`/`time_holiday_sleep`.
  Added the missing `timeWake`/`timeSleep` fields to `Plan`.
- **`capok`/`capnew`/`capfail`** are three independent booleans, not one normalized "mode" —
  `capno`/`capyes` are unset on every record (dropped, audit-only), `capnnew` disagrees with
  `capnew` on 2/33 plans (kept audit-only, not merged). Model changed from a single `capMode`
  string to `capOk`/`capNew`/`capFail` booleans.
- **`alg.N`** (direction slot algorithm) is a numeric code (42/65/66/68/98/97/60 observed), not
  the single-character selector Zones' `GroupRule.alg` uses — despite the superficially similar
  name, it's an unrelated Plan-level concept. Model field changed from `String` to `int`.
- **`out_in_ans`** and **`nospam`** are small integers (4/5/6/8/10 and 1/2 observed), not
  booleans as originally assumed. Model fields changed from `bool` to `int`.
- **`in_acd__min`/`out_acd__min`** (double underscore) disagree with the single-underscore
  fields on 5/15 plans that carry both — not a safe alias; only single-underscore is modeled.
- **Two `.pro` files are corrupted**: `tele2_sms.pro` and `megafon_spb_vip.pro` contain a
  literal PHP warning string (a legacy admin-panel write failure), not a real value. The seed
  script detects and discards `Warning:`-prefixed values rather than seeding them literally.
- **`Sim.plan` mock data** (pre-existing, not part of this flow's original scope) referenced
  command-set names (`'beeline_spb'`, `'tele2_spb'`, `'megafon_msk'`, `'life'`) rather than real
  plan ids — leftover from the deleted `planRows` mock. Fixed to reference real seeded plan ids
  (`beeline_spb_good`, `tele2_spb_good`, `megafon_msk_good`, and `default` for `life:)` per the
  banner's own "use default for new operators" guidance) so usage counts and delete guards
  demo correctly.

**Ended at**: Phase 5, Task 5.1 (partial — blocked-delete-for-referenced-plan and narrow-layout
checks not re-driven live)
**Handoff notes**: Core feature is functionally complete and heavily spot-checked against the
legacy archive. Remaining before calling this fully DONE: (1) reconnect `claude-in-chrome` and
re-verify the blocked-delete dialog for a referenced, non-default plan (e.g. `beeline_spb_good`,
now used by 1 SIM) shows the correct "недоступно" copy with count; (2) visually confirm the
narrow (`<900px`) stacked layout. Both are low-risk — same code paths already verified in
adjacent scenarios (Command Sets/Zones shipped the identical patterns) — but not yet re-driven
live in *this* feature after the late mock.dart fix.

---

## Deviations Summary

| Planned | Actual | Reason |
|---|---|---|
| `capMode: String` (normalized enum-like) | `capOk`/`capNew`/`capFail`: bool | Archive data showed 3 independent flags, not one mode |
| `DirectionSlot.alg: String` | `DirectionSlot.alg: int` | Archive values are numeric codes, unrelated to Zone's char selector |
| `outInAns`/`nospam`: bool | `outInAns`/`nospam`: int | Archive values are small integers, not booleans |
| Seed: 37 active + 9 audit-only | Seed: 33 active + 8 audit-only | Original count didn't survive direct archive verification |

## Learnings

- Every "obvious" alias/typo pair in the legacy field audit (`capnnew`/`capnew`, double-vs-
  single-underscore ACD fields) turned out to have real value disagreements on a meaningful
  fraction of records (6-33%) — the "audit, don't silently merge" principle from Requirements
  was the right call, not just a defensive formality.
- Cross-checking a handful of raw archive files against generated seed output (`cat plan/<id>.
  <field>` vs. the generated Dart) caught a real Python `True`/`False` → Dart boolean-literal
  bug in the seed script before it shipped — worth doing even when the script "looks obviously
  correct."
- Flutter web's `CanvasKit`/`SingleChildScrollView` didn't respond to the browser tool's
  simulated mouse-wheel `scroll` action in this session (root cause unclear — possibly a
  pointer-signal event property mismatch); dispatching a synthetic `WheelEvent` via
  `javascript_tool` directly onto `flt-glass-pane` was a reliable workaround.

## Completion Checklist

- [x] All tasks completed or explicitly deferred
- [x] `flutter analyze` clean (baseline infos only)
- [x] `flutter build web` succeeds
- [ ] Full manual verification pass (2 checks pending live re-verification — see Handoff notes)
- [x] No regressions found in adjacent features during this session
- [ ] Status updated to COMPLETE (pending the 2 outstanding checks)
