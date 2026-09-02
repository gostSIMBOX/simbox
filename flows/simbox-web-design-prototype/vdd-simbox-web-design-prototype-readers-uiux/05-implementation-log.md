# Implementation Log: simbox-web-design-prototype-readers-uiux

> Started: 2026-09-02
> Plan: [04-plan.md](04-plan.md)

## Progress Tracker

| Task | Status | Notes |
|------|--------|-------|
| 1.1 Reader model | Done | |
| 1.2 Ico.readerModel() | Done | |
| 1.3 Mock data | Done | |
| 2.1 AdmPage.readers + state plumbing | Done | includes Reader.field(key) sort accessor |
| 3.1 ReadersPage widget | Done | one deviation, see below |
| 3.2 Sidebar + main.dart wiring | Done | |
| 4.1 Build + manual verification | Done | |

## Session Log

### Session 2026-09-02 - Claude

**Started at**: Phase 1, Task 1.1
**Context**: Requirements → Visual → Specifications → Plan all approved in this same session,
based on a full read of `legacy/simbox-desktop-v2014/www/simbox/readers.php` and `hubs.php`.

#### Completed
- Task 1.1: Added `Reader` class to `lib/data/models.dart` (alongside `HubNode`), exactly per
  03-specifications.md.
  - Files changed: `lib/data/models.dart`
  - Verified by: `flutter analyze` — 0 new issues.
- Task 1.2: Added `Ico.readerModel(String model)` to `lib/data/icon_map.dart`, returning the
  PL2303 icon for `'1001'`, `null` otherwise.
  - Files changed: `lib/data/icon_map.dart`
  - Verified by: `flutter analyze` — 0 issues.
- Task 1.3: Added `const readers = <Reader>[...]` (6 rows) to `lib/data/mock.dart`.
  - Files changed: `lib/data/mock.dart`
  - Verified by: `flutter analyze`; visual spot-check of each row against the approved
    02-visual.md rationale (no-card, fully-ID'd, `0000` PIN, mid-search, error, unrecognized
    model) — later re-confirmed live in Task 4.1's browser pass.
- Task 2.1: Inserted `AdmPage.readers` into the enum (before `hubs`); added `visibleReaders`
  getter and `runOnReaders(...)` to `AppState` (verbatim mirrors of `visibleDongles`/
  `runOnDongles`); added `Reader.field(String key)` mechanical sort accessor (11 arms, one per
  column) to `models.dart`.
  - Files changed: `lib/state/app_state.dart`, `lib/data/models.dart`
  - Verified by: `flutter analyze` — confirmed the *expected* single `non_exhaustive_switch_expression`
    error on `main.dart:123` (not yet wired to `AdmPage.readers`), exactly as called out in the
    Plan's Task 2.1 Verification note. No other regressions.
- Task 3.1: Created `lib/pages/readers_page.dart` — `_cols()` (11 `ColDef<Reader>`), 4
  `ActionGroup`s (Обновить, PIN, Поиск KI, APDU-команда), `_KiWarningBanner` gated on
  `st.activeGroup == 'kisearch'`.
  - Files changed: `lib/pages/readers_page.dart` (new)
  - Verified by: `flutter analyze` — 0 issues on the new file.
- Task 3.2: Inserted `(AdmPage.readers, 'Ридеры', 'pl2303.png')` into `sidebar.dart`'s `_tabs`
  before the `hubs` tuple; added the import + switch arm in `main.dart`.
  - Files changed: `lib/widgets/sidebar.dart`, `lib/main.dart`
  - Verified by: `flutter analyze` — 0 issues app-wide (the Task 2.1 non-exhaustive-switch error
    is now resolved).
- Task 4.1: `flutter test` (existing suite, 15 tests, all passing, unaffected by this change);
  `flutter build web --release` (succeeded); served the build with a plain static HTTP server
  (`python3 -m http.server`, not `flutter run -d web-server`/DDS — see Deviations) and drove it
  in Chrome via the claude-in-chrome tools:
  - Sidebar shows "Ридеры" directly before "Хабы" — confirmed visually.
  - All 6 mock rows render with correct per-column values, including the model icon present on
    readers 1-5 and correctly blank on reader6 (unrecognized model).
  - Opened "Поиск KI" → red warning banner appeared with the exact legacy caution text; selected
    reader2, ran "Запустить поиск KI" → exact `wts --svistokmode=1 --device=reader --speed=9600
    --ignorects --port=/dev/ttyUSB1 --dev=reader2` log entry + toast appeared; closing the group
    hid the banner.
  - Opened "PIN", typed `1234` into the "Снять PIN" field, ran it → exact
    `asterisk -rx 'dongle cmd reader2 AT+CPIN="1234";+CLCK="SC",0,"1234";+CFUN=1,1'` log entry
    appeared.
  - Clicked "Хабы" → heading reads "Хабы (Hubs)" (the out-of-band fix from the Requirements
    phase), table/tree/power actions unchanged.
  - Verified by: the browser pass above; `flutter test` and `flutter analyze` both clean.

#### Deviations from Plan
- **APDU action-group icon**: 03-specifications.md proposed `icon: 'terminal.png'` for the
  APDU-команда group, reasoning by analogy to a "terminal" concept. That asset only exists in
  the vendored Fugue set (`assets/fugue/terminal.png`) — but `ActionGroup.icon` renders through
  `AdmIcon`, which unconditionally loads from `assets/imgs/$path` (only `sidebar.dart`'s
  `_NavItem` has special-case handling for a `fugue:` prefix; `ActionGroupPill` does not).
  Using `'terminal.png'` as specified would have silently rendered a blank icon (`AdmIcon`'s
  `errorBuilder` swallows the missing-asset error). Caught this during implementation (Task 3.1)
  by checking `assets/imgs/` before writing the icon reference, and used `'conn.png'` instead —
  the same icon `dongles_page.dart` already uses for its analogous "Режимы и AT-команда" group,
  which is the closer precedent anyway (APDU-команда is the reader-flavored counterpart of that
  same AT-command concept). No other deviations.
- **Dev server for manual verification**: the Plan/Specs both said "`flutter build web` (or run
  a local dev server)". `flutter run -d web-server` crashed on this machine with a
  `DartDevelopmentServiceException: ... WebSocketException: ... was not upgraded to websocket`
  (Dart Development Service can't establish its debug websocket in this sandboxed environment).
  Worked around by using `flutter build web --release` (as already planned as the primary
  option) and serving the static output with `python3 -m http.server`, which has no DDS/debug
  websocket dependency. Fully sufficient for a visual/UX verification pass; no debugging
  features (hot reload) were needed.

#### Discoveries
- Confirmed the `AdmIcon`/`ActionGroup.icon` asset-path convention (`assets/imgs/` only, no
  `fugue:` prefix support outside `sidebar.dart`) is worth remembering for any future flow that
  adds an `ActionGroup` — the Fugue-vs-imgs distinction is easy to miss since it *is* supported
  in one specific widget (`_NavItem`) but not the general case.

**Ended at**: Phase 4, Task 4.1 — flow complete.
**Handoff notes**: None outstanding. Feature is fully implemented, verified in-browser, and the
existing test suite is unaffected. No commit has been made — per this project's standing
guidance, commits are only created when the user explicitly asks.

---

## Deviations Summary

| Planned | Actual | Reason |
|---------|--------|--------|
| APDU-команда `ActionGroup` icon: `'terminal.png'` | `'conn.png'` | `'terminal.png'` only exists in the Fugue asset set, not `assets/imgs/`, which is the only path `ActionGroup.icon`/`AdmIcon` actually load from outside the sidebar's special-cased nav rendering — would have rendered blank. `'conn.png'` matches `DonglesPage`'s existing AT-command group icon, the closer precedent. |
| Manual verification via `flutter run -d web-server` | `flutter build web --release` + static `python3 -m http.server` | The dev-server path crashed on a DDS/websocket error in this environment; the static-build path (already the Plan's stated primary option) has no such dependency and is sufficient for a visual pass. |

## Learnings

- When adding a new `ActionGroup` icon in this codebase, verify the asset exists under
  `assets/imgs/` (not just anywhere in the repo, e.g. `assets/fugue/`) before writing the
  reference — `AdmIcon`'s `errorBuilder` fails silently (renders nothing) rather than throwing,
  so a wrong path won't surface as a build error, only as a visibly blank icon.

## Completion Checklist

- [x] All tasks completed or explicitly deferred
- [x] Tests passing (`flutter test`: 15/15; `flutter analyze`: 0 issues)
- [x] No regressions (Hubs/Sims/Dongles pages unaffected; confirmed Hubs visually in-browser)
- [x] Documentation updated if needed (N/A — no DOCUMENTATION phase requested)
- [x] Status updated to COMPLETE
