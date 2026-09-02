# Implementation Plan: simbox-web-design-prototype-zones-uiux

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-09-01
> Specifications: [03-specifications.md](03-specifications.md)

## Summary

Five phases: (1) generate the verified seed data from the 25 legacy files, (2) build the
non-UI feature layer (models/repository/controller), (3) build the UI layer mirroring
`command_sets`, (4) wire the new page into the app shell, (5) verify. Phases 2 and 3 depend on
Phase 1's exact `Zone` shape; Phase 4 depends on Phase 2+3 both existing.

## Task Breakdown

### Phase 1: Seed data

#### Task 1.1: Write and run the zone seed generator
- **Description**: A throwaway script (Python, run once from the repo root — not committed as
  a project dependency) that: reads the 25 `.conf` files under
  `legacy/simbox-desktop-v2014/asterisk/extensions/zones/`; extracts each `exten =>
  _<pattern>,1,Macro(makecall,<zone>,${EXTEN})` line's pattern; applies the merge rule from
  03-specifications.md's Data Models (same operator prefix + same region suffix → merge; content
  match alone does NOT imply merge, per the `bee_spb`/`bee_sz`/`beeline_sz` case); resolves each
  of the 18 zones' name from `icon_map.dart`'s `_naprMap` where present, else the proposed name
  from the Specifications table; resolves each icon path by checking
  `assets/imgs/napravleine/` for an exact `<id>.png`/`.ico` match, then an operator-generic
  match (`beeline.png` etc.), then `hz.png`; emits `lib/features/zones/seed.dart` as a `const
  List<Zone> zoneSeed = [...]` literal (each `Zone(id: ..., name: ..., region: ..., icon: ...,
  defCodes: const [...])`).
- **Files**: `lib/features/zones/seed.dart` - Create (generated output; the generator script
  itself is not committed, matching how one-off codegen has been handled elsewhere in this
  session)
- **Dependencies**: None (only needs 03-specifications.md's verified table, already computed)
- **Verification**: Generated file's total code count across all `Zone.defCodes` sums to
  ~6,073 (per Specifications); spot-check `megafon_spb`'s 20 codes and `all_tj`'s 1 code against
  the source `.conf` files directly; confirm the file is valid, analyzable Dart
  (`dart format`/`flutter analyze` clean).
- **Complexity**: Medium (mechanical but must not silently mis-merge or drop a zone — the
  `beeline_sz` vs `beeline_spb` distinction is the one place this is easy to get wrong).

### Phase 2: Feature core (non-UI)

#### Task 2.1: `Zone` model
- **Description**: Per 03-specifications.md's Interfaces — `id`/`name`/`region`/`icon`/
  `defCodes`, `copyWith`, value equality (`==`/`hashCode`) so `ZoneDraft.isDirty` works via
  simple `!=` comparison.
- **Files**: `lib/features/zones/models.dart` - Create
- **Dependencies**: Task 1.1 (needs the final field shape to match the seed's literal calls)
- **Verification**: `zone_seed.dart` compiles against this model.
- **Complexity**: Low

#### Task 2.2: `ZoneRepository` + `InMemoryZoneRepository`
- **Description**: Mirrors `command_sets/repository.dart` exactly minus the `isSystem`/
  `usedByPlanIds` delete-guard (Requirements #7 — every zone deletable, no exceptions).
- **Files**: `lib/features/zones/repository.dart` - Create
- **Dependencies**: Task 2.1
- **Verification**: Manual — construct with `zoneSeed`, confirm `records.length == 18`,
  exercise `create`/`replace`/`delete`/`reset` against the interface contract.
- **Complexity**: Low

#### Task 2.3: `ZoneController`
- **Description**: Per 03-specifications.md's Interfaces — `load`, `records`/`selected`/
  `isDirty`/`visibleZones` getters, `requestSelectZone`/`keepEditing`/`discardAndContinue`
  (mirrors command sets' unsaved-changes guard), `updateCodesText`/`cancelDraft`/`save` (the
  textarea draft cycle), `createZone`/`renameZone`/`deleteZone`/`resetDemo`.
- **Files**: `lib/features/zones/controller.dart` - Create
- **Dependencies**: Task 2.2
- **Verification**: No UI yet — verified indirectly once Phase 3 lands; logic is
  straightforward enough to trust from the `command_sets/controller.dart` precedent it mirrors.
- **Complexity**: Medium

### Phase 3: UI

#### Task 3.1: `ZoneIcon` + `ZoneCodeEditor`
- **Description**: `ZoneIcon` — small widget rendering `assets/imgs/${zone.icon}` with an
  `errorBuilder` fallback (same pattern as `AdmIcon`, not `FugueIcon` — zones use the
  `napravleine` set). `ZoneCodeEditor` — the one big multi-line `TextField` (no `maxLines` cap,
  internal scroll via a bounded-height container), live "N кодов" count label, hint text
  ("Каждый код — новая строка..."), wired to `controller.updateCodesText`.
- **Files**: `lib/features/zones/code_editor.dart` - Create (also holds `ZoneIcon` — small
  enough not to warrant its own file)
- **Dependencies**: Task 2.3
- **Verification**: Deferred to 3.4 integration.
- **Complexity**: Medium (large-text-in-`TextField` performance is the one thing worth actually
  eyeballing — `beeline_ru`'s 1550 lines is the stress case).

#### Task 3.2: `ZoneRegistryPane` + `zone_dialogs.dart`
- **Description**: Searchable list (icon, name, id·region, code count) + "+" add button +
  popup-menu reset, mirrors `command_sets/registry_pane.dart`. `zone_dialogs.dart`: create
  dialog (id + name + optional region), delete confirmation (quoting name/id/code-count),
  edit-metadata dialog (name/region only — no id field, per the immutable-id decision),
  `requestZoneSelection` helper (the discard/keep-editing prompt).
- **Files**: `lib/features/zones/registry_pane.dart` - Create, `lib/features/zones/
  zone_dialogs.dart` - Create
- **Dependencies**: Task 2.3
- **Verification**: Deferred to 3.4 integration.
- **Complexity**: Medium

#### Task 3.3: `ZoneDetailHeader` + `ZonesWorkspace`
- **Description**: `ZoneDetailHeader` — icon, name, id·region, edit-metadata pencil, "⋮" menu
  (clone via create-dialog prefill, delete), mirrors `command_sets/detail_header.dart` minus the
  "used by N plans" block. `ZonesWorkspace` — responsive `LayoutBuilder` (narrow < 900 collapses
  registry pane to a dropdown row, matching `CommandSetsWorkspace`), composes header + code
  editor + `_DraftBar` (reused shape, own copy since it's a small private widget in
  `command_sets/workspace.dart` today — duplicated here rather than shared to avoid a
  cross-feature import for a ~15-line widget).
- **Files**: `lib/features/zones/detail_header.dart` - Create, `lib/features/zones/
  workspace.dart` - Create
- **Dependencies**: Task 3.1, Task 3.2
- **Verification**: Full manual pass per 03-specifications.md's Manual Verification checklist.
- **Complexity**: Medium

### Phase 4: Wire into the app shell

#### Task 4.1: `AppState`, sidebar, `main.dart`
- **Description**: Add `AdmPage.zones` to the enum; `AppState` gets `late final ZoneController
  zones;` constructed the same way `commandSets` is (`ZoneController(InMemoryZoneRepository
  (zoneSeed))`, `.load()`, `.addListener(_forwardCommandSets)`-equivalent forwarding, disposed
  alongside `commandSets`). `sidebar.dart`'s `_tabs` gets `(AdmPage.zones, 'Направления',
  'napravleine/hz.png')` right after the `nabor` entry. `main.dart`'s page switch gets `AdmPage
  .zones => ZonesWorkspace(controller: s.zones)`.
- **Files**: `lib/state/app_state.dart` - Modify, `lib/widgets/sidebar.dart` - Modify,
  `lib/main.dart` - Modify
- **Dependencies**: Task 2.3, Task 3.3
- **Verification**: App boots, "Направления" appears in the sidebar in the right slot, clicking
  it navigates correctly.
- **Complexity**: Low (mechanical — same shape as every prior page addition, and as the
  already-landed `commandSets` wiring specifically).

### Phase 5: Verification

#### Task 5.1: Full verification pass
- **Description**: `flutter analyze` (0 new errors); `flutter build web`; drive the built app in
  Chrome through 03-specifications.md's full Manual Verification checklist (all 18 zones present
  with correct counts, search, select/edit/save/cancel, create, delete, switch-while-dirty
  guard, narrow-width layout, icon fallbacks, sidebar slot).
- **Files**: None (verification only)
- **Dependencies**: Task 4.1
- **Verification**: This *is* the verification task.
- **Complexity**: Medium (breadth — 18 zones × several interaction paths — not difficulty).

## Dependency Graph

```
1.1 ─→ 2.1 ─→ 2.2 ─→ 2.3 ─┬─→ 3.1 ─┐
                          ├─→ 3.2 ─┼─→ 3.3 ─→ 4.1 ─→ 5.1
                          └────────┘
```

## File Change Summary

| File | Action | Reason |
|---|---|---|
| `lib/features/zones/seed.dart` | Create | Generated, deduplicated legacy zone data |
| `lib/features/zones/models.dart` | Create | `Zone` |
| `lib/features/zones/repository.dart` | Create | `ZoneRepository`, `InMemoryZoneRepository` |
| `lib/features/zones/controller.dart` | Create | `ZoneController` |
| `lib/features/zones/code_editor.dart` | Create | `ZoneIcon`, `ZoneCodeEditor` |
| `lib/features/zones/registry_pane.dart` | Create | `ZoneRegistryPane` |
| `lib/features/zones/zone_dialogs.dart` | Create | Create/delete/edit-metadata dialogs |
| `lib/features/zones/detail_header.dart` | Create | `ZoneDetailHeader` |
| `lib/features/zones/workspace.dart` | Create | `ZonesWorkspace` |
| `lib/state/app_state.dart` | Modify | `AdmPage.zones`, `ZoneController zones` wiring |
| `lib/widgets/sidebar.dart` | Modify | New nav entry |
| `lib/main.dart` | Modify | New page-switch case |

## Risk Assession

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Seed generator mis-merges `beeline_spb`/`beeline_sz` (content-identical, different zones) | Medium | High (silently loses a real zone) | Merge rule explicitly requires operator+region match, not content match alone; verify 18 zones present post-generation, not just "no errors" |
| Hardcoded icon path 404s at runtime (e.g. `beeline_spb.png` doesn't exist) | Medium | Low (cosmetic — blank icon box) | Icon resolution happens in the generator (checks the actual `assets/imgs/napravleine/` directory listing), not hand-typed; `ZoneIcon`'s `errorBuilder` is the backstop |
| 1550-line textarea (`beeline_ru`) has visible input lag | Low | Medium | Plain `TextField` with no per-keystroke reformatting beyond trim/split-on-save (not on every keystroke — see note below); spot-checked in Task 3.1 |
| `ZoneController`/`ZoneRepository` diverge from `command_sets`' proven shape in a subtle way (e.g. missing the switch-guard) | Low | Medium | Built by direct structural mirroring, file-by-file, not from scratch |

Note refining Task 2.3/Specifications: `updateCodesText` should update `draft.working.defCodes`
on every keystroke (needed for the live "N кодов" count and for `isDirty` to react immediately),
but the *parse* (`split('\n').map(trim).where(isNotEmpty)`) is cheap even at 1550 lines — no
debouncing needed for a prototype; flagged here only so Task 3.1's implementer doesn't
over-engineer a debounce that isn't necessary.

## Rollback Strategy

Same as fix1/fix2: single working tree, additive-only changes (existing pages/widgets
untouched except the 3 mechanical wiring edits in Task 4.1). `git diff`/`git checkout` on the
affected files, or revert the eventual commit(s), if needed.

## Checkpoints

After Phase 1, Phase 2, Phase 3, and Phase 4:

- [ ] `flutter analyze` shows no new errors.
- [ ] `flutter build web` succeeds.
- [ ] Behavior matches the relevant Acceptance Criteria in 01-requirements.md and the ASCII
      states in 02-visual.md for whatever that phase touched.

## Open Implementation Questions

- [ ] Exact seed order (alphabetical vs. grouped) — cosmetic, resolve during Task 1.1, no
      approval needed.

---

## Approval

- [ ] Reviewed by: Anton Dodonov
- [ ] Approved on:
- [ ] Notes:
