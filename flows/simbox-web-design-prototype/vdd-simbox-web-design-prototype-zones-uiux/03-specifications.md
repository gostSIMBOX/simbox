# Specifications: simbox-web-design-prototype-zones-uiux

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-09-01
> Requirements: [01-requirements.md](01-requirements.md)
> Visual: [02-visual.md](02-visual.md)

## Overview

Add `lib/features/zones/` — a repository/controller/workspace feature mirroring
`lib/features/command_sets/`'s architecture, scaled to a zone's simpler shape (id, name, region
hint, icon, and one list of DEF-code pattern strings). Seed it with the deduplicated,
content-verified legacy dataset (18 zones, ~6,073 codes total — see Data Models). Wire in a new
`AdmPage.zones` route, sidebar entry, and `main.dart` case.

## Affected Systems

| System | Impact | Notes |
|---|---|---|
| `lib/features/zones/models.dart` | Create | `Zone` record (id, name, region, icon, defCodes) |
| `lib/features/zones/repository.dart` | Create | `ZoneRepository` interface + `InMemoryZoneRepository`, mirrors `command_sets/repository.dart` exactly (create/replace/delete/reset, typed exceptions) — no `isSystem`/`usedByPlanIds` guard (Requirements #7: every zone deletable) |
| `lib/features/zones/seed.dart` | Create | Generated from the 25 legacy `.conf` files — 18 deduplicated `Zone` const literals |
| `lib/features/zones/controller.dart` | Create | `ZoneController extends ChangeNotifier` — mirrors `CommandSetController` minus the sections/commands/rules machinery (no `CommandSetSection`, no `selectedCommandId`) |
| `lib/features/zones/workspace.dart` | Create | Responsive list+detail layout, mirrors `CommandSetsWorkspace` |
| `lib/features/zones/registry_pane.dart` | Create | Searchable zone list + add button, mirrors `CommandSetRegistryPane` |
| `lib/features/zones/detail_header.dart` | Create | Name/id/region + edit-metadata pencil + clone/delete menu, mirrors `CommandSetDetailHeader` minus the "used by N plans" block (no cross-references for zones) |
| `lib/features/zones/code_editor.dart` | Create | The one DEF-code textarea + count + hint (replaces command_sets' two-section split — a zone has one editable body) |
| `lib/features/zones/zone_dialogs.dart` | Create | Create/delete/edit-metadata dialogs, mirrors `set_dialogs.dart` |
| `lib/state/app_state.dart` | Modify | Add `late final ZoneController zones;`, construct + listener-forward in constructor/dispose, exactly like the existing `commandSets` wiring |
| `lib/widgets/sidebar.dart` | Modify | Add `(AdmPage.zones, 'Направления', 'napravleine/hz.png')` to `_tabs`, positioned right after the `nabor` entry |
| `lib/main.dart` | Modify | Add `AdmPage.zones` to the enum (in `app_state.dart`) and a `case AdmPage.zones => ZonesWorkspace(controller: s.zones)` in the page switch |
| `lib/data/icon_map.dart` | No change | `_naprMap` reused read-only for names/icons; not modified (Requirements Won't-Have) |

## Architecture

### Component Diagram

```
AdmPage.zones (main.dart) -> ZonesWorkspace(controller: AppState.zones)
├─ ZoneRegistryPane          (search, + add, list of zones w/ icon+name+id+region+count)
└─ Detail pane
    ├─ ZoneDetailHeader      (icon, name, id · region, edit-metadata pencil, ⋮ clone/delete)
    ├─ ZoneCodeEditor        (textarea bound to draft.workingCodesText, live count, hint)
    └─ _DraftBar (if dirty)  (Отмена / Сохранить — same widget shape as command_sets')
```

### Data Flow

- `ZoneController` holds `selectedId`, `query`, and `ZoneDraft? draft` (mirrors
  `CommandSetDraft`: `working: Zone`, `saved: Zone`, `isDirty` via equality check).
- The code editor's `TextEditingController` is seeded from
  `draft.working.defCodes.join('\n')` whenever the selection changes; on every keystroke it
  updates `draft.working = draft.working.copyWith(defCodes: _parseLines(text))` and calls
  `notifyListeners()` — `isDirty` becomes `draft.working != draft.saved` (list equality).
- Save: `repository.replace(id, draft.working)` (or `.create()` for a brand-new zone not yet
  persisted — see Behavior below), `draft = null`, `notifyListeners()`.
- Cancel: `draft = null` (or reset `draft.working = draft.saved`), `notifyListeners()` — textarea
  re-seeds from the reverted value on next build.
- Same unsaved-changes switch-guard as command sets: `requestSelectZone(id)` returns `false` and
  sets `pendingSelectionId` if dirty; the registry pane shows the same discard/keep-editing
  dialog (`zone_dialogs.dart` reuses the exact dialog shape from `set_dialogs.dart`'s
  `requestSetSelection`, parameterized).

## Interfaces

### New Interfaces

```dart
// lib/features/zones/models.dart
class Zone {
  final String id;          // e.g. 'beeline_spb' — immutable after creation (Requirements Open Q, resolved: yes)
  final String name;        // e.g. 'Билайн СПб'
  final String? region;     // e.g. 'СПб' — display hint only, free text
  final String icon;        // e.g. 'napravleine/beeline_spb.png' — full asset-relative path
  final List<String> defCodes; // e.g. ['792109XXXXX', ...] — no leading '_', that's dialplan boilerplate

  const Zone({
    required this.id,
    required this.name,
    this.region,
    required this.icon,
    this.defCodes = const [],
  });

  Zone copyWith({String? name, String? region, String? icon, List<String>? defCodes}) => Zone(
        id: id,
        name: name ?? this.name,
        region: region ?? this.region,
        icon: icon ?? this.icon,
        defCodes: defCodes ?? this.defCodes,
      );

  @override
  bool operator ==(Object other) =>
      other is Zone &&
      id == other.id && name == other.name && region == other.region &&
      icon == other.icon && _listEq(defCodes, other.defCodes);
  @override
  int get hashCode => Object.hash(id, name, region, icon, Object.hashAll(defCodes));
}
```

```dart
// lib/features/zones/repository.dart — same shape as CommandSetRepository, no isSystem/usedBy guard
abstract interface class ZoneRepository {
  List<Zone> get records;
  Zone? byId(String id);
  void create(Zone record);
  void replace(String id, Zone record);
  void delete(String id);
  void reset();
}
class ZoneRepositoryException implements Exception { final String message; ... }
class InMemoryZoneRepository implements ZoneRepository { /* mirrors InMemoryCommandSetRepository, delete() has no isSystem/usedByPlanIds check */ }
```

```dart
// lib/features/zones/controller.dart
enum ZoneLoadState { loading, ready, error }
class ZoneDraft {
  final Zone saved;
  Zone working;
  ZoneDraft(this.saved) : working = saved;
  bool get isDirty => working != saved;
}
class ZoneController extends ChangeNotifier {
  final ZoneRepository repository;
  ZoneLoadState loadState = ZoneLoadState.loading;
  String? selectedId;
  String query = '';
  ZoneDraft? draft;
  String? pendingSelectionId;

  ZoneController(this.repository);
  void load() { loadState = ZoneLoadState.ready; selectedId ??= repository.records.firstOrNull?.id; notifyListeners(); }
  List<Zone> get records => repository.records;
  Zone? get selected => draft?.working ?? (selectedId == null ? null : repository.byId(selectedId!));
  bool get isDirty => draft?.isDirty ?? false;
  List<Zone> get visibleZones { /* filter by query over id/name/region, same shape as visibleSets */ }

  bool requestSelectZone(String id) { /* mirrors requestSelectSet */ }
  void keepEditing(); void discardAndContinue(); // mirror command_sets

  void beginEditingCodes() { draft ??= ZoneDraft(selected!); } // lazily starts a draft on first textarea edit
  void updateCodesText(String text) {
    draft ??= ZoneDraft(selected!);
    draft!.working = draft!.working.copyWith(defCodes: _parseCodeLines(text));
    notifyListeners();
  }
  void cancelDraft() { draft = null; notifyListeners(); }
  void save() {
    final d = draft; if (d == null) return;
    repository.replace(d.saved.id, d.working);
    draft = null; notifyListeners();
  }

  void createZone(String id, String name, String? region) { /* repository.create(Zone(...)); select it */ }
  void renameZone(String id, String name, String? region) { /* repository.replace with copyWith(name/region) — id unchanged */ }
  void deleteZone(String id) { /* repository.delete(id); reselect first remaining or null */ }
  void resetDemo() { /* repository.reset(); reselect */ }
}

List<String> _parseCodeLines(String text) => text
    .split('\n')
    .map((l) => l.trim())
    .where((l) => l.isNotEmpty)
    .toList();
```

## Data Models

### Verified deduplicated zone catalog (18 zones, ~6,073 codes total)

Diffed programmatically (byte-identical code-list check, not line-count inference — see
`_status.md`'s note on a mid-session correction) across all 25 legacy `.conf` files. Merge rule:
collapse an abbreviated/full-name pair **only when both the operator prefix and region suffix
match** (e.g. `bee_msk`+`beeline_msk` → `beeline_msk`); do **not** merge same-content files
across different region suffixes (`bee_spb`, `bee_sz`, and `beeline_sz` are byte-identical in
the legacy data but are 2 distinct zones — SPb and Northwest — that happen to share a code list
snapshot; `bee_spb` renames to `beeline_spb` alone, `bee_sz`+`beeline_sz` merge together).

| Zone id | Name (RU) | Region | Codes | Icon | Source file(s) |
|---|---|---|---|---|---|
| `megafon_spb` | МегаФон СПб | СПб | 20 | `napravleine/megafon_spb.png` | meg_spb + megafon_spb |
| `megafon_msk` | МегаФон Мск | Мск | 137 | `napravleine/megafon_msk.png` | meg_msk + megafon_msk |
| `megafon_sz` | МегаФон СЗ | СЗ | 20 | `napravleine/megafon_sz.png` | meg_sz + megafon_sz |
| `megafon_ru` | МегаФон РФ | РФ | 1103 | `napravleine/megafon_ru.png` | meg_ru + megafon_ru |
| `beeline_spb` | Билайн СПб | СПб | 54 | `napravleine/beeline_spb.png` | bee_spb |
| `beeline_msk` | Билайн Мск | Мск | 55 | `napravleine/beeline_msk.png` | bee_msk + beeline_msk |
| `beeline_sz` | Билайн СЗ | СЗ | 54 | `napravleine/hz.png` (no exact or generic-operator icon exists in this project's converted PNG set) | bee_sz + beeline_sz |
| `beeline_ru` | Билайн РФ | РФ | 1550 | `napravleine/beeline_ru.png` | bee_ru + beeline_ru |
| `mts_spb` | МТС СПб | СПб | 14 | `napravleine/mts_spb.png` | mts_spb |
| `mts_msk` | МТС Мск | Мск | 49 | `napravleine/mts_msk.png` | mts_msk |
| `tele2_spb` | Tele2 СПб | СПб | 15 | `napravleine/tele2_spb.png` | tele2_spb |
| `kievstar` | Kyivstar UA | UA | 4 | `napravleine/kievstar.png` | kievstar_ua (id normalized, matches `_naprMap`'s `'KU'` entry) |
| `rostel_spb_gor` | Ростелеком СПб (городские) | СПб | 2851 | `napravleine/rostel_spb_gor.png` | rostel_spb_gor |
| `rostel_spb_mob` | Ростелеком СПб (мобильные) | СПб | 7 | `napravleine/rostel_spb_mob.png` | rostel_spb_mob |
| `all_spb` | Все операторы, СПб | СПб | 137 | `napravleine/hz.png` (no all-operator icon exists) | all_spb |
| `all_tj` | Все операторы, Таджикистан | TJ | 1 | `napravleine/hz.png` | all_tj |
| `all_ua` | Все операторы, Украина | UA | 1 | `napravleine/hz.png` | all_ua |
| `all_uz` | Все операторы, Узбекистан | UZ | 1 | `napravleine/hz.png` | all_uz |

Icon paths verified directly against this Flutter project's actual asset directory
(`design/simbox-web-design-prototype-v2026/assets/imgs/napravleine/`, the already-converted PNG
set — **not** the legacy `.ico` source directory, which has a different, smaller file list and
was a misleading reference during drafting). This project's set has no bare operator-generic
icon (`beeline.png`/`megafon.png`/etc. don't exist, only region-specific files) — so `beeline_sz`
(and any other zone with no exact-match file) falls straight back to `hz.png`, a two-tier chain
(exact → `hz.png`) rather than the three-tier one originally proposed.

11 of these 18 already exist as entries in `icon_map.dart`'s `_naprMap` (`megafon_spb/msk/sz/ru`,
`beeline_spb/msk/ru`, `mts_spb/msk`, `tele2_spb`, `kievstar`) — their names above are taken
directly from that map, and all of their icon files do exist in this project's asset set. The
other 7 (`beeline_sz`, `rostel_spb_gor`, `rostel_spb_mob`, `all_spb`, `all_tj`, `all_ua`,
`all_uz`) have no `_naprMap` entry and get names proposed fresh in this table; of those, only
`beeline_sz` lacks a matching icon file and falls back to `hz.png` — `rostel_spb_gor`/
`rostel_spb_mob` both have exact-match files despite no `_naprMap` entry.

### Seed generation

A one-off script (`scripts/gen_zones_seed.py` or inline in the implementation session — not a
committed runtime dependency) reads the 25 `.conf` files, applies the merge rule above, resolves
each zone's icon path against the actual files in `assets/imgs/napravleine/` (falling back
operator-generic → `hz.png` per the table), and emits `lib/features/zones/seed.dart` as a
`const List<Zone> zoneSeed = [...]` literal — checked into the repo like `command_sets/seed.dart`
is, not regenerated at runtime.

### Schema Changes

None (in-memory repository, no persistence layer).

## Behavior Specifications

### Happy Path

1. App loads → `AppState.zones` (a `ZoneController`) constructed with `InMemoryZoneRepository(zoneSeed)`, `load()` called, `selectedId` defaults to the first zone (`megafon_spb`, alphabetical-ish seed order — exact order per Plan Task 2).
2. Operator opens "Направления" from the sidebar → `ZonesWorkspace` renders the registry pane (18 rows, search box) and the detail pane for the selected zone.
3. Operator clicks "Билайн СЗ" → `requestSelectZone('beeline_sz')` (not dirty) → immediate select → detail pane shows its 54 codes in the textarea.
4. Operator edits the textarea (adds 2 lines, removes 1) → `updateCodesText` fires on every change → draft becomes dirty → `_DraftBar` appears with a live "55 кодов" count (or whatever the new count is).
5. Operator clicks "Сохранить" → `repository.replace('beeline_sz', draft.working)` → draft cleared → registry-pane row's count updates to match.

### Happy Path (create/delete)

1. Operator clicks "+" → dialog asks for id + name (+ optional region) → `createZone(...)` →
   `repository.create(Zone(id: ..., name: ..., defCodes: const []))` → new zone selected, empty
   textarea, no draft (nothing to save yet, it's already persisted via `create`).
2. Operator selects a zone, opens the "⋮" menu → "Удалить" → confirmation dialog quoting the
   zone's name/id/code-count → `deleteZone(id)` → `repository.delete(id)` → selection moves to
   the first remaining zone (or `null` if the list is now empty).

### Edge Cases

| Case | Trigger | Expected Behavior |
|---|---|---|
| Icon file doesn't actually exist for a mapped path | `beeline_spb.png`/`beeline_sz` region icons (verified absent above) | Seed generation resolves to the operator-generic icon (`beeline.png`) instead of hardcoding a 404; `Image.asset`'s existing `errorBuilder` (already present on the icon-rendering widget used, `FugueIcon`-style or a small local `ZoneIcon`) is a last-resort safety net, not the primary mechanism |
| Textarea has only blank lines / all lines deleted | Operator clears the whole textarea and saves | `_parseCodeLines` returns `[]` — a zone with zero codes is allowed (same as a freshly created zone before any codes are added); no validation blocks this per Requirements #5 ("no per-line syntax validation beyond non-empty") |
| Duplicate lines within one zone's textarea | Operator pastes the same pattern twice | Not deduplicated automatically — kept as-is (matches "no per-line validation" scope; Asterisk itself would just have a redundant/unreachable second `exten` line, harmless in this UI-only prototype) |
| Switch zones while dirty | Click a different registry row mid-edit | Same discard/keep-editing guard as command sets (`requestSelectZone` returns `false`, dialog shown) |
| Delete the currently-selected zone | Confirm delete on the open zone | Selection reassigned to first remaining zone (or `null` — registry empty state) before `notifyListeners()`, so the detail pane never renders a dangling `Zone?` for a deleted id |
| Create a zone with an id that already exists | Operator types an existing id in the create dialog | `repository.create` throws `ZoneRepositoryException` (mirrors command sets' duplicate-id guard) — dialog shows the message inline, does not close |
| Rename attempts to change `id` | N/A — by design (Requirements Open Q resolved: id immutable) | The rename/edit-metadata dialog only exposes name/region fields, no id field, after creation — same UI-level prevention as command sets (its dialog also never lets you edit `id` post-creation) |

### Error Handling

Not applicable beyond the typed `ZoneRepositoryException` cases above (duplicate id on create,
not-found on replace/delete) — same scope as command sets, no network/async errors in this
prototype.

## Dependencies

### Requires

- `lib/features/command_sets/` as the structural reference (already implemented, committed).
- `assets/imgs/napravleine/*` (existing asset folder, already registered in `pubspec.yaml`).

### Blocks

- None.

## Integration Points

### Internal Systems

- `lib/data/icon_map.dart`'s `_naprMap` — read-only reference during seed generation only (not
  imported at runtime by the zones feature; the resolved icon path is baked into `seed.dart`
  directly, avoiding a runtime dependency from `features/zones` back into `data/icon_map.dart`
  for something that's static content anyway).
- `lib/design/tokens.dart` — reused as-is (`T.denseHit`, `T.narrowHit`, `T.brandGradient`,
  `T.radiusCard`, `T.shadow`, etc.), matching command_sets' usage.
- `lib/widgets/fugue_icon.dart`'s `FugueIcon` is **not** reused for zone icons (zones use the
  existing `assets/imgs/napravleine/*.png` set, not the Fugue set) — zones get their own tiny
  `ZoneIcon` widget (`Image.asset('assets/imgs/${zone.icon}', ...)` with an `errorBuilder`),
  matching how `AdmIcon` already renders `assets/imgs/*` elsewhere in the app.

## Testing Strategy

No automated test suite (unchanged project convention). Manual verification via `flutter
analyze` + `flutter build web` + a driven Chrome session, per fix1/fix2's precedent.

### Manual Verification

- [ ] All 18 zones present on load with their correct (verified) code counts.
- [ ] Registry-pane search filters by id/name/region.
- [ ] Selecting a zone loads its codes into the textarea correctly (spot-check `beeline_ru`'s
      1550-line zone for scroll/performance, and `all_tj`'s 1-line zone for the minimal case).
- [ ] Editing the textarea → draft bar appears → Save persists the new list → registry row's
      count updates. Cancel reverts the textarea to the saved value.
- [ ] Create a new zone → appears in the list, empty textarea, selected immediately.
- [ ] Delete a zone → removed from the list, selection moves sensibly, no crash.
- [ ] Switching zones mid-edit triggers the unsaved-changes dialog; both Continue-editing and
      Discard-and-switch paths work.
- [ ] Narrow-window layout collapses the registry pane to the dropdown+add-button row.
- [ ] Sidebar shows "Направления" right after "Наборы команд"; navigating to/from it behaves
      like every other page (selection/query resets appropriately — no special exemption).
- [ ] Icon fallback chain renders something for every zone (no broken-image icon) — especially
      `beeline_spb`/`beeline_sz` (operator-generic fallback) and the 4 `all_*` zones (`hz.png`).

## Migration / Rollout

Not applicable — single prototype app, in-memory seed data.

## Open Design Questions

- [ ] Exact seed order (alphabetical by id vs. grouped by operator vs. matching the 25-file
      directory listing order) — cosmetic, decided during Task 2 of the Plan, not blocking.

---

## Approval

- [ ] Reviewed by: Anton Dodonov
- [ ] Approved on:
- [ ] Notes:
