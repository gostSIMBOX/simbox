# Implementation Plan: simbox-web-design-prototype-readers-uiux

> Version: 1.0
> Status: APPROVED
> Last Updated: 2026-09-02
> Specifications: [03-specifications.md](03-specifications.md)

## Summary

Additive-only change across 6 existing files plus 1 new file, all reusing established patterns
(`HubsPage`/`DonglesPage` shape) — no new architecture. Ordered so every intermediate state
compiles: data layer first (model → icon helper → mock data → state plumbing), then the nav
entry, then the page itself, then wiring it into `main.dart`, then verification.

## Task Breakdown

### Phase 1: Data Layer

#### Task 1.1: `Reader` model
- **Description**: Add the `Reader` class to `lib/data/models.dart` exactly as specified in
  03-specifications.md's "New Type — `Reader`" section (13 fields + `hasCard`/
  `progressDisplay`/`haystack`), placed alongside `HubNode`/`Dongle`.
- **Files**: `lib/data/models.dart` - Modify
- **Dependencies**: None
- **Verification**: `flutter analyze` — new class compiles standalone (not yet referenced
  anywhere, so no other errors expected from this task alone).
- **Complexity**: Low

#### Task 1.2: `Ico.readerModel()` helper
- **Description**: Add `static IcoRef? readerModel(String model)` to `lib/data/icon_map.dart`'s
  `Ico` class, alongside `dongle()` — returns the PL2303 icon for `'1001'`, `null` otherwise.
- **Files**: `lib/data/icon_map.dart` - Modify
- **Dependencies**: None (independent of Task 1.1)
- **Verification**: `flutter analyze`.
- **Complexity**: Low

#### Task 1.3: Mock data seed
- **Description**: Add `const readers = <Reader>[...]` to `lib/data/mock.dart` with the exact 6
  rows from 03-specifications.md's Mock Data section, alongside `hubTree`.
- **Files**: `lib/data/mock.dart` - Modify
- **Dependencies**: Task 1.1 (needs `Reader` to exist)
- **Verification**: `flutter analyze`; spot-check each row against 02-visual.md's stated
  per-row rationale (no-card, fully-ID'd, `0000` PIN, mid-search, error, unrecognized-model).
- **Complexity**: Low

### Phase 2: State Plumbing

#### Task 2.1: `AdmPage.readers` + `visibleReaders` + `runOnReaders` + sort accessor
- **Description**: Insert `readers` into the `AdmPage` enum (positioned immediately before
  `hubs`, per Specifications); add `visibleReaders` getter (search-filtered, sorted, mirrors
  `visibleDongles`); add `runOnReaders(...)` (mirrors `runOnDongles` verbatim, reader-flavored
  empty-selection toast text); add the mechanical `Reader.field(String key)` switch-on-column
  accessor (one arm per column key, returning the matching field as `String`/`num` per
  `Sim`/`Dongle`'s existing `field()` convention) needed for `visibleReaders`'s sort branch.
- **Files**: `lib/state/app_state.dart` - Modify, `lib/data/models.dart` - Modify (adds
  `Reader.field(key)`)
- **Dependencies**: Task 1.1, Task 1.3
- **Verification**: `flutter analyze`. Existing `AdmPage` switch statements elsewhere (e.g.
  `main.dart`'s `_page`) will now fail to compile (non-exhaustive switch) until Task 3.2 —
  expected and resolved in the same work session, not a regression to chase down separately.
- **Complexity**: Low-Medium (mechanical but touches a widely-referenced enum — grep for every
  existing `switch`/`case` on `AdmPage` before considering this task done, to catch any
  non-exhaustive-switch compile error immediately rather than at Task 4).

### Phase 3: Page + Navigation

#### Task 3.1: `ReadersPage` widget
- **Description**: Create `lib/pages/readers_page.dart` per 03-specifications.md's "New Widget"
  section: `_cols()` (11 `ColDef<Reader>`s in `readers.php`'s column order), `_visibleCols()`
  (identical shape to `HubsPage`'s), 4 `ActionGroup`s (Обновить, PIN, Поиск KI, APDU-команда)
  with the exact command strings/log lines from Specifications, the `_KiWarningBanner` private
  widget gated on `st.activeGroup == 'kisearch'`, and the page `build()` (`TableHeading` +
  `TableToolbar` + conditional banner + `DenseTable<Reader>`).
- **Files**: `lib/pages/readers_page.dart` - Create
- **Dependencies**: Task 1.1, Task 1.2, Task 2.1
- **Verification**: `flutter analyze` — file compiles in isolation (not yet imported by
  `main.dart`, so no route to it exists yet).
- **Complexity**: Medium (most UI surface of any task here, but every piece — `ColDef`,
  `ActionGroup`/`SubAction`/`AdmField`, the banner's `Container`/`BoxDecoration` — is a
  straight copy-adapt of an already-shipped pattern; no new widget behavior being invented).

#### Task 3.2: Sidebar entry + `main.dart` route
- **Description**: Insert `(AdmPage.readers, 'Ридеры', 'pl2303.png')` into `sidebar.dart`'s
  `_tabs` list directly before the `AdmPage.hubs` tuple; add `import 'pages/readers_page.dart';`
  and the `AdmPage.readers => const ReadersPage()` arm to `main.dart`'s `_page` switch
  (resolves Task 2.1's now-non-exhaustive switch).
- **Files**: `lib/widgets/sidebar.dart` - Modify, `lib/main.dart` - Modify
- **Dependencies**: Task 3.1
- **Verification**: `flutter analyze` — zero errors, app-wide. This is the point at which the
  whole feature first becomes reachable end-to-end.
- **Complexity**: Low

### Phase 4: Verification

#### Task 4.1: Build + manual browser pass
- **Description**: `flutter build web` (or run a local dev server), open the app in Chrome, and
  work through 03-specifications.md's Manual Verification checklist top to bottom: sidebar
  position/label, all 6 mock rows' per-column values, each of the 4 action groups (open/close,
  run → log entry + toast), KI banner show/hide tied to `activeGroup`, column show/hide/reorder
  persistence within the session, then confirm the existing `test/*.dart` suite still passes
  and `flutter analyze` is clean.
- **Files**: None (verification only)
- **Dependencies**: Task 3.2
- **Verification**: Checklist above, all boxes checked.
- **Complexity**: Low-Medium (breadth of manual checks, not implementation difficulty).

## Dependency Graph

```
Task 1.1 ─┬─→ Task 1.3 ─┐
          │             ├─→ Task 2.1 ─┬─→ Task 3.1 ─→ Task 3.2 ─→ Task 4.1
Task 1.2 ─┘             │             │
                         └─────────────┘
```

(Task 1.2 is independent until Task 3.1, which needs it for the model-icon column.)

## File Change Summary

| File | Action | Reason |
|------|--------|--------|
| `lib/data/models.dart` | Modify | Add `Reader` class + `Reader.field(key)` sort accessor |
| `lib/data/icon_map.dart` | Modify | Add `Ico.readerModel(String)` |
| `lib/data/mock.dart` | Modify | Add `const readers = <Reader>[...]` (6 rows) |
| `lib/state/app_state.dart` | Modify | Add `AdmPage.readers`, `visibleReaders`, `runOnReaders(...)` |
| `lib/pages/readers_page.dart` | Create | New `ReadersPage` widget + `_KiWarningBanner` |
| `lib/widgets/sidebar.dart` | Modify | Insert "Ридеры" nav tuple before "Хабы" |
| `lib/main.dart` | Modify | Import + switch arm for `AdmPage.readers` |

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Non-exhaustive `AdmPage` switch left broken between Task 2.1 and Task 3.2 if work is interrupted mid-session | Low | Low | Both tasks are small and meant to land together in one sitting (Task 2.1's Verification note calls this out explicitly); implementation log should note if they're ever split across sessions |
| `_KiWarningBanner`'s one-off color literals drift from whatever this app's design system settles on later (Open Design Question in Specifications, left unresolved by choice) | Low | Low | Scoped to one private widget in one file — trivial to find/update later; not blocking this flow |
| Mock ICCID/IMSI values accidentally collide with real-looking test data elsewhere in `mock.dart` causing a confusing diff read | Low | Low | Values are synthetic and distinct from existing `hubTree`/`dongles` mock IDs; visually inspect `mock.dart`'s diff before considering Task 1.3 done |

## Rollback Strategy

Purely additive change with no data migration and no modification to existing `HubsPage`/
`DonglesPage`/other pages' behavior. If needed: revert the 6 modified files' diffs and delete
`lib/pages/readers_page.dart` — no other state to clean up (no persisted storage, mock-data
prototype).

## Checkpoints

After each phase, verify:

- [ ] `flutter analyze` reports 0 new errors/warnings.
- [ ] Existing pages (`HubsPage`, `DonglesPage`, `SimsPage`, etc.) render and behave unchanged.
- [ ] Behavior matches 03-specifications.md's Behavior Specifications and Edge Cases tables.

## Open Implementation Questions

None beyond the two already carried from Specifications (danger-color token scoping;
`Reader.field(key)` written mechanically during Task 2.1, not pre-specified column-by-column).

---

## Approval

- [x] Reviewed by: Anton Dodonov
- [x] Approved on: 2026-09-02
- [x] Notes: Approved as drafted. Implemented as planned with one icon-asset deviation (see
  05-implementation-log.md) — no plan changes needed.
