# Specifications: Plans editor UI/UX

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-09-02
> Requirements: [01-requirements.md](01-requirements.md)
> Visual: [02-visual.md](02-visual.md)

## Overview

Add `lib/features/plans/` — a repository/controller/workspace feature mirroring
`lib/features/command_sets/` and `lib/features/zones/`'s established architecture. Seed it from
the archived legacy plan directory (verified this session — see Data Models). A `Plan` has a
stable id, a directly-editable command-set reference, and the seven policy families from
Requirements, structured as typed fields (not raw key/value). The Directions family cross-
references the live `ZoneController` read-only — never a second copy of route/group data. A new
`ExplanationBanner` widget (dismiss/reopen, session-only state) sits above the workspace.

## Verified Legacy Data Shape

Confirmed by extracting `legacy/simbox-desktop-v2014/var/simbox/plan09042014.tar.gz` this
session (not assumed from the requirements narrative):

- `plan/` is a **flat key-value directory**: one file per `<plan_id>.<field_name>` (or
  `<plan_id>.<field_name>.<slot>` for the four numbered direction slots, e.g. `alg.3`,
  `nodiff.1`, `limit_hard.4`). File content is the field's raw value (single line/token).
- `plan/plan.list` lists plan IDs, one per line, with `-----------` separator lines between
  command-set groups — confirms Requirements' verified "33 non-separator entries" count directly.
- **95 unique field-name suffixes** exist across the archive (confirmed via
  `ls plan/ | sed -E 's/^[^.]+\.//;s/\.[0-9]+$//' | sort -u`), matching the "~100 stored suffix
  variants" the requirements narrative estimated. Includes the alias/typo cluster already
  flagged (`capfail/capnew/capnnew/capno/capok/capyes` — 6 cap variants, not the ~2 the naive
  reading suggests) and a 9-member quality-flag cluster (`ivip/igoo/inor/ibad/inew/inos/irob/
  iblo/notvip`) that maps directly to the same QOS vocabulary already used elsewhere in this app
  (`icon_map.dart`'s VIP/GOO/NOR/BAD/NEW/NOS/ROB/BLO codes) — Editable Policy Family #3's
  "quality/status eligibility flags."

## Affected Systems

| System | Impact | Notes |
|---|---|---|
| `lib/features/plans/models.dart` | Create | `Plan`, `DirectionSlot`, value-equality helpers |
| `lib/features/plans/repository.dart` | Create | `PlanRepository`/`InMemoryPlanRepository` — mirrors `zones/repository.dart`, delete guard checks SIM references (not `isSystem`) |
| `lib/features/plans/seed.dart` | Create | Generated from the extracted `plan09042014.tar.gz` archive — 33 active + 8 audit-only records |
| `lib/features/plans/controller.dart` | Create | `PlanController` — draft/save/cancel, unsaved-changes guard, plus `explanationOpen` (banner state) |
| `lib/features/plans/workspace.dart` | Create | Registry + detail master-detail, responsive `narrow < 900` |
| `lib/features/plans/registry_pane.dart` | Create | Searchable list + command-set filter + add button |
| `lib/features/plans/explanation_banner.dart` | Create | Dismissible banner + "?" reopen affordance (Requirements #25-27) |
| `lib/features/plans/detail_header.dart` | Create | ID, directly-editable command-set dropdown, priority, PRO tag, usage count, Clone/Delete menu |
| `lib/features/plans/sections/*.dart` | Create | One file per semantic policy family (7 files) — see Interfaces |
| `lib/features/plans/directions_section.dart` | Create | Slot 1-4 editable policy + read-only Zones route context; slots 0/5 compatibility note |
| `lib/features/plans/plan_dialogs.dart` | Create | Create (Clone/Blank), delete (blocked/confirm), unsaved-changes guard |
| `lib/state/app_state.dart` | Modify | `late final PlanController plans;`, constructed/disposed like `commandSets`/`zones` |
| `lib/widgets/sidebar.dart` | No change | `AdmPage.plan` already exists (legacy `PlanPage` swapped for the new workspace) |
| `lib/main.dart` | Modify | `AdmPage.plan => PlanPage()` continues to work; `PlanPage` itself rewritten to host `PlansWorkspace` |
| `lib/pages/plan_page.dart` | Modify | Rewritten as a thin wrapper (mirrors `zones_page.dart`), old `_PlanCol`/`_planGroups` grid deleted |
| `lib/data/mock.dart` | Modify | Old `planRows`/`PlanRow` mock removed — superseded by the live `PlanController` (Requirements Won't Have: no second mock source) |

## Architecture

### Component Diagram

```
AdmPage.plan -> PlanPage -> PlansWorkspace(controller: AppState.plans, zones: AppState.zones, commandSets: AppState.commandSets)
├─ ExplanationBanner (if controller.explanationOpen)
├─ PlanRegistryPane   (search, command-set filter, + add, list w/ usage count)
└─ Detail pane
    ├─ PlanDetailHeader   (id, command-set dropdown [direct-edit], priority, PRO tag, usage, ⋮)
    ├─ 7 × PolicySection  (collapsible; Directions cross-references ZoneController read-only)
    └─ _DraftBar (shared shape with command_sets/zones)
```

### Data Flow

- `PlanController` needs read access to `ZoneController` (for Directions' route context) and
  `CommandSetController` (for the command-set dropdown's options and the "used by N SIMs"
  check's — no, usage is SIM-side, see below). Rather than importing those controllers directly
  into `PlanController` (coupling one feature's controller to two others'), the **workspace
  widget** (`PlansWorkspace`) receives all three controllers as constructor params from
  `AppState` and passes the read-only data down to `DirectionsSection`/`PlanDetailHeader` as
  plain arguments — `PlanController` itself stays dependency-free, matching `ZoneController`'s
  own independence from `CommandSetController` today.
- Usage count ("используется N симками") reads `AppState.sims` (mock data) filtered by
  `sim.plan == plan.id` — a plain computed getter on the workspace/header, not stored on
  `Plan` itself (mirrors how Zones' `defCodes.length` is computed from the list, not cached).
- Draft/save/cancel: identical shape to `ZoneDraft`/`CommandSetDraft` — `PlanDraft { saved,
  working }`, `isDirty` via `Plan`'s `==`. Every section's field edits and the command-set
  dropdown all write into `draft.working`, one shared Save/Cancel bar.
- `explanationOpen` (banner state): lives on `PlanController` (not global `AppState`) since
  it's Plan-screen-specific, defaults to `true` (open on first visit, matching `logOpen`'s
  existing default-open convention), toggled by `toggleExplanation()`.

## Interfaces

### New Interfaces

```dart
// lib/features/plans/models.dart

/// One of the four editable direction slots (1-4) or the two compatibility-only
/// slots (0, 5) — see Requirements' Legacy Addition 1.1.
class DirectionSlot {
  final int slot;             // 0-5
  final bool editable;        // false for 0 and 5 (compatibility only)
  final int alg;               // VERIFIED numeric algorithm code (42/65/66/68/98 observed) — a Plan-level policy code, distinct from Zone's dialplan selector char
  final bool nodiff;          // "различие не учитывается" — nodiff.N in legacy
  final int limitSoft;        // limit_max.N
  final int limitHard;        // limit_hard.N
  const DirectionSlot({
    required this.slot, required this.editable, required this.alg,
    required this.nodiff, required this.limitSoft, required this.limitHard,
  });
  DirectionSlot copyWith({int? alg, bool? nodiff, int? limitSoft, int? limitHard}) => ...;
  // == / hashCode
}

class Plan {
  // Identity and ownership (Family 1)
  final String id;                 // stable, immutable after creation
  final String commandSetId;       // directly editable (Requirements Q3 resolution)
  final int priority;
  final String? proTag;            // routing tag, empty is normal (see Requirements' PRO note)

  // Capacity (Family 2)
  final int onlineMax;             // online_max
  final int addMax;                // add_max (online_adddaymax's daily-reset aspect is runtime, not Plan — Won't Have)

  // Call modes and quality eligibility (Family 3)
  final bool canIn, canOut, canSout;         // can_in / can_out / can_sout
  final bool notVip;                          // notvip
  final Set<String> qualityFlags;             // subset of {VIP,GOO,NOR,BAD,NEW,NOS,ROB,BLO} — ivip/igoo/... eligibility
  final bool capOk, capNew, capFail;          // capok/capnew/capfail — VERIFIED independent flags, not one mode
  // (capno/capyes are unset on every archive record — audit-only, not modeled;
  // capnnew mismatches capnew on 2/33 plans that carry both — kept audit-only,
  // not merged as an alias)

  // Timing and schedule (Family 4)
  final int diffSlow;              // guaranteed pause (ms/sec — unit TBD in Implementation, seed preserves raw)
  final int diffMin;               // pause on all calls
  final int diffMinOut;            // diff_min_out — used when GOO (see banner copy's min() rule)
  final int? timeWake, timeSleep;               // VERIFIED distinct from time_work_*/time_holiday_* below — this is the pair the banner names
  final int? timeWorkWake, timeWorkSleep;      // -1 (legacy disabled) => null
  final int? timeHolidayWake, timeHolidaySleep; // -1 (legacy disabled) => null

  // Directions (Family 5)
  final List<DirectionSlot> directions;  // exactly 6 entries, slots 0-5, only 1-4 editable

  // Incoming-call generation (Family 6)
  final int iattMin, iattMax, iattSoft;         // request threshold/range
  final int inAcdMin, inAcdMax;                 // incoming ACD range
  final int outAcdMin, outAcdMax;               // outgoing ACD range — VERIFIED: only single-underscore in_acd_*/out_acd_* mapped; the double-underscore variants disagree with these on 5/15 plans that carry both, so they're kept audit-only, not merged
  final bool forwarding, conn, rand, inWait, inSound;
  final int outInAns;    // VERIFIED integer answer-mode code (values seen: 4,5,6,8,10), not boolean

  // SMS and beacon generation (Family 7)
  final int mayLimit, monLimit, msmLimit;       // attempts, not "successes" (Legacy Addition 1.3)
  final int smsoutSoft, smsoutHard;
  final int sattSoft, sattHard, sattSoftDay, sattHardDay, sattSoftTotal, sattHardTotal;
  final int nospam;      // VERIFIED integer code (values seen: 1,2), not boolean

  const Plan({ /* ...required params, sensible defaults... */ });
  Plan copyWith({ /* one named param per field */ });
  // == / hashCode (field-by-field, directions via list equality)
}
```

```dart
// lib/features/plans/repository.dart — mirrors zones/repository.dart exactly in shape
abstract interface class PlanRepository {
  List<Plan> get records;
  Plan? byId(String id);
  void create(Plan record);
  void replace(String id, Plan record);
  void delete(String id); // throws if id == 'default', or if any Sim.plan == id
  void reset();
}
class PlanRepositoryException implements Exception { final String message; ... }
class InMemoryPlanRepository implements PlanRepository { /* delete() takes `List<Sim> Function() liveSims` so the referenced-by-SIM check reads current mock data, not a snapshot */ }
```

```dart
// lib/features/plans/controller.dart
enum PlanLoadState { loading, ready, error }
class PlanDraft { final Plan saved; Plan working; ZoneDraft-shaped isDirty getter; }
class PlanController extends ChangeNotifier {
  final PlanRepository repository;
  bool explanationOpen = true;
  String? selectedId;
  String query = '';
  String? commandSetFilter;      // Acceptance Criteria #4
  PlanDraft? draft;
  String? pendingSelectionId;

  void load();
  List<Plan> get records => repository.records;
  List<Plan> get visiblePlans; // filtered by query + commandSetFilter
  Plan? get selected;
  bool get isDirty;

  void toggleExplanation();                  // Acceptance Criteria #26
  bool requestSelectPlan(String id);
  void keepEditing(); void discardAndContinue();

  // Field mutations — one method per family, draft-first (mirrors updateCodesText)
  void updateIdentity({String? commandSetId, int? priority, String? proTag});
  void updateCapacity({int? onlineMax, int? addMax});
  void updateCallModes({...});
  void updateTiming({...});
  void updateDirectionSlot(int slot, {int? alg, bool? nodiff, int? limitSoft, int? limitHard}); // slot must be 1-4
  void updateIncomingGeneration({...});
  void updateSmsGeneration({...});

  void createPlan(String id, String commandSetId, {String? cloneFromId});
  void deletePlan(String id);     // throws via repository if blocked; caller shows the blocked-vs-confirm dialog per 02-visual.md
  void resetDemo();
}
```

```dart
// lib/features/plans/directions_section.dart — read-only Zones cross-reference
/// For a given plan's command-set id and direction slot, find every zone whose
/// GroupRule.limitSlot matches, across every zone belonging to that command set.
/// Read-only projection — never mutates ZoneController, never stored on Plan.
List<({Zone zone, GroupRule rule})> routesForSlot(
  ZoneController zones, String commandSetId, int slot,
) => [
  for (final zone in zones.records)
    for (final rule in zone.groupRules)
      if (rule.limitSlot == slot) (zone: zone, rule: rule),
  // Note: Zone has no explicit "belongs to command set" field today (Zones is
  // organized by operator/region, not by command set) — see Open Design
  // Questions below; this function's exact filter predicate is one of them.
];
```

## Data Models

### Seed generation

A one-off Python script (not committed, matching the Zones/`gen_zones_seed.py` precedent) will:

1. Extract `plan09042014.tar.gz` (or read the already-extracted `var/simbox/plan/` directory —
   both exist in the legacy checkout per this session's verification).
2. Group files by `<plan_id>` prefix; read `plan.list` for the 33 active IDs (skipping
   `-----------` separators) and derive the 8 audit-only IDs as "present in `plan/` but absent
   from `plan.list`" (cross-checked against Requirements' explicit list of 9 names).
3. For each of the 33 active plans, map the ~95 raw field-name suffixes onto `Plan`'s typed
   fields per a fixed normalization table (built during Implementation from the field audit
   above — e.g. `capok/capnew/capfail/capno/capyes` → `capMode` enum value, `capnnew` → alias
   of `capnew`, `in_acd__min`/`in_acd_min` double-underscore variants → the same field).
   Fields with **no evidenced equivalence** to a modeled field are **not silently dropped** —
   they're written to a companion `plans_audit.dart` (or a code comment block) listing
   `plan_id.raw_field_name = raw_value` for every unmapped entry, satisfying Acceptance
   Criteria #2 ("data may not disappear silently") without inventing a UI for ~15-20 rarely-used
   legacy variants.
4. Emit `lib/features/plans/seed.dart` (33 active `Plan` records) — the 8 audit-only IDs are
   **not** emitted as `Plan` records (they're not shown in the default active registry per
   Requirements' resolved Open Question #1); their raw field dumps go in the same audit
   companion output for a developer to consult, not surfaced in the product UI.

### Schema Changes

None (in-memory repository).

## Behavior Specifications

### Happy Path (edit + save)

1. Operator opens "Планы" → banner shows (first visit) → `PlansWorkspace` renders 33 plans,
   `tele2_spb_good` selected by default (or first record).
2. Clicks the "?" — wait, banner already open, so instead: dismisses the banner via X →
   `explanationOpen = false` → "?" appears next to the title.
3. Selects "tele2_spb_good" → detail pane shows its 7 sections, collapsed except a remembered/
   default-open one.
4. Expands "Направления" → sees slots 1-4 editable (alg/nodiff/limits) + slots 0/5 compatibility
   note + read-only route chips per slot (from `routesForSlot`).
5. Edits slot 1's `limitSoft` → `updateDirectionSlot(1, limitSoft: 45)` → draft created, dirty
   bar appears.
6. Changes the command-set dropdown in the header from `tele2_spb` to `beeline_spb` →
   `updateIdentity(commandSetId: 'beeline_spb')` → same draft, still one Save commits both
   changes together.
7. Saves → `repository.replace` persists; registry row's command-set label updates; Directions
   section's route chips re-query `routesForSlot` against the new command-set's zones.

### Happy Path (banner)

1. First visit: `explanationOpen == true` (controller default) → banner renders above the
   workspace, four paragraphs verbatim, X control.
2. Click X → `toggleExplanation()` → banner hides, "?" shows next to "Планы".
3. Click "?" → `toggleExplanation()` again → banner reappears, same content, no re-fetch (it's
   static copy, not loaded data).
4. Navigating away and back to the Планы page (`goTo`) does **not** reset `explanationOpen` —
   `PlanController` is constructed once in `AppState`, same lifetime as `ZoneController`/
   `CommandSetController`, so the dismissed state persists for the whole session (Requirements
   #26's "in-memory, session-only" — session means "app lifetime," not "per-visit").

### Edge Cases

| Case | Trigger | Expected Behavior |
|---|---|---|
| Delete `default` | Any delete attempt on `id == 'default'` | Blocked unconditionally — the delete action itself is absent/disabled in the UI (02-visual.md), not merely blocked after confirmation |
| Delete a plan referenced by ≥1 SIM | Delete on e.g. `tele2_spb_good` (6 SIMs) | `repository.delete` throws `PlanRepositoryException` listing the referencing count; UI shows the "недоступно" dialog, not the confirm dialog |
| Delete an unreferenced, non-default plan | Delete on e.g. `tele2_trash` (0 SIMs) | Confirmation dialog, then delete succeeds |
| Change command-set on a plan, then check Directions | Command-set dropdown edited mid-session | `routesForSlot` re-evaluates against the *draft's* `commandSetId` immediately (live preview of route context under the new ownership), not just after Save |
| A direction slot has zero matching zones for the current command-set | e.g. an obscure slot number nothing routes through | Route-context line shows "нет данных для этого набора команд" (02-visual.md), not an empty/broken chip row |
| Slot 0 or 5 | Rendering the Directions section | Rendered as a labeled compatibility note, not an editable `DirectionSlot` row — `updateDirectionSlot` rejects `slot` outside 1-4 (no-op, matches Legacy Addition 1.1's "must not be silently presented as ordinary Plan directions 1–4") |
| `time_work_wake`/`time_work_sleep` stored as `-1` in legacy | Seed generation | Mapped to `null` in the `Plan` model (Requirements: "legacy disabled value `-1` represented as a clear disabled state"); UI shows a "выключено" toggle/label, not a literal `-1` spinner |
| `msm_limit > 0` but `smsout_soft == 0` | Viewing the SMS/MAY-MON-MSM section | A warning is shown per Legacy Addition 1.3 ("MSM fallback = msm_limit available AND outgoing SMS soft limit available") — computed from the two live field values, not a stored flag |
| Command-set referenced by a plan is deleted from the live Command Sets registry | Hypothetical cross-feature edit | Out of scope to actively prevent in this iteration (Command Sets' own delete guard already blocks deleting a set with existing plans, per the original Command Sets flow — Plan doesn't need its own duplicate check, just relies on that) — noted here as an assumption, not built |

### Error Handling

Typed `PlanRepositoryException` for create (duplicate id), replace (not found), delete
(protected/referenced) — same scope as Zones/Command Sets, no network/async errors.

## Dependencies

### Requires

- `lib/features/zones/` (shipped) — read-only, for Directions' route context.
- `lib/features/command_sets/` (shipped) — read-only, for the command-set dropdown's options
  and (indirectly) for Command Sets' own plan-count validation on its side.
- `AppState.sims` (existing mock) — read-only, for usage-count / delete-guard.

### Blocks

- None.

## Integration Points

### Internal Systems

- `lib/design/tokens.dart`, `lib/widgets/fugue_icon.dart` — reused as-is, matching
  `command_sets`/`zones`' established visual language.
- `lib/pages/plan_page.dart` — rewritten to a thin wrapper; its current `_PlanCol`/`_planGroups`
  ultra-wide-grid implementation is deleted (Won't Have: no legacy grid reproduction).
- `lib/data/mock.dart`'s `planRows`/`PlanRow` — deleted; `Sim.plan` (a plan-id string) stays as
  the SIM-side reference, now resolved against the live `PlanController` instead of the removed
  mock (Requirements Acceptance Criteria #12).

## Testing Strategy

No automated test suite for this feature area (matches Zones/Command Sets' own precedent,
despite `command_sets` having gained a `test/` directory from separate work — not extending that
convention into Plans in this iteration unless requested). Manual verification via `flutter
analyze` + `flutter build web` + a driven Chrome session.

### Manual Verification

- [ ] All 33 active plans present with their seeded values; the 8 audit-only IDs are absent from
      the active registry (confirm via search — they should not appear).
- [ ] Command-set filter and search both work in the registry pane.
- [ ] Editing each of the 7 policy families dirties the shared draft; Save persists all
      simultaneously; Cancel reverts all.
- [ ] Command-set dropdown edit is immediate (no Clone dialog involved) and updates Directions'
      route context live, pre-save.
- [ ] Directions: slots 1-4 editable, slots 0/5 show the compatibility note only; route chips
      match what `routesForSlot` computes for at least one plan spot-checked against the live
      Zones data by hand.
- [ ] Delete: `default` has no delete affordance; a referenced plan shows the blocked dialog; an
      unreferenced plan shows the confirm dialog and succeeds.
- [ ] Explanation banner: open by default, dismiss shows "?", "?" reopens it, state survives
      navigating away and back.
- [ ] Narrow-width layout collapses the registry per the established breakpoint (code-review
      confidence only, per the same tooling limitation noted in prior flows' logs).
- [ ] No console errors.

## Migration / Rollout

Not applicable — single prototype app, in-memory seed data. Removing `mock.dart`'s `planRows`
and `plan_page.dart`'s old grid is a one-way deletion within this same iteration (not a phased
migration) — confirmed safe since nothing else in the app reads `planRows`.

## Data Quality Findings (verified against the archive during Implementation)

- `tele2_sms.pro` and `megafon_spb_vip.pro` contain a literal PHP warning string
  (`Warning: file_put_contents(...): failed to open stream: Permission denied ...`) instead of a
  real value — a write failure in the legacy admin panel corrupted these two files in place. The
  seed script detects any field value starting with `Warning:` and treats it as unset (`null`/
  default), logging it to the audit output rather than seeding literal garbage into `proTag`.
- Three pairs of timing fields are genuinely distinct in the archive, not two as originally
  modeled: `time_wake`/`time_sleep` (the pair the Explanation Banner names), `time_work_wake`/
  `time_work_sleep`, and `time_holiday_wake`/`time_holiday_sleep`. All three pairs are now on
  `Plan`.
- `capok`/`capnew`/`capfail` are independent booleans, not one normalized "mode" as originally
  drafted — confirmed by sampling: `capno`/`capyes` are unset on every record (audit-only,
  dropped from the model), and `capnnew` disagrees with `capnew` on 2 of the 33 plans that carry
  both (kept audit-only, not merged as an alias — too risky to silently overwrite).
- `in_acd__min`/`out_acd__min` (double underscore) disagree with the single-underscore
  `in_acd_min`/`out_acd_min` on 5 of the 15 plans that carry both — not a safe alias either;
  single-underscore is modeled (present on all plans that have the double-underscore variant, a
  strict superset), double-underscore values go to the audit dump only.
- `out_in_ans` and `nospam` are small integers (4/5/6/8/10 and 1/2 respectively) in the archive,
  not booleans as originally assumed — corrected to `int` fields.

## Resolved Design Decisions

- **Zone ↔ command-set relationship**: Both Zones and Command Sets are named by the same legacy
  `<operator>_<region>` convention (zone ids like `megafon_spb`, `beeline_sz`; command-set ids
  like `tele2_spb`, `megafon_msk`, `mts_spb` — VERIFIED as the actual command-set set derived
  from `plan.list`; `rostel_spb` is a real command set — shipped in `command_sets/seed.dart` — it
  simply owns zero plans in the legacy archive). `routesForSlot`'s filter therefore
  matches a zone into a command set's route context when the zone's id/region shares that same
  `<operator>_<region>` prefix as the command set's id — a plain string-prefix rule, grounded in
  the naming convention both features already ship with, no new lookup table needed. A zone
  whose name doesn't cleanly resolve to any command set is simply omitted from every plan's
  route context, falling into the existing "нет данных для этого набора команд" empty state
  rather than needing a special case.
- **Alias/typo field normalization**: deferred to the seed-generation script itself
  (implementation-time audit), not resolved field-by-field here — the script prints every raw
  field it could not map onto a modeled `Plan` field, for review, per the Seed generation
  section above.
- **Units for `diff_slow`/`diff_min`/`diff_min_out` and the ACD ranges**: modeled as plain
  seconds (the conventional unit for legacy Asterisk pacing/duration fields of this shape).
  Implementation may spot-check real archive values against `plan.php`'s field labels if that
  legacy source turns out to be available, but this doesn't block drafting the Plan phase since
  the underlying field type (`int`) is the same regardless.

---

## Approval

- [ ] Reviewed by: Anton Dodonov
- [ ] Approved on:
- [ ] Notes:
