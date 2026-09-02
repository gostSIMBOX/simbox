# Implementation Log: simbox-web-design-prototype-zones-uiux

> Started: 2026-09-02
> Plan: [04-plan.md](04-plan.md)

## Progress Tracker

**Iteration 1 (DEF-codes):**

| Task | Status | Notes |
|------|--------|-------|
| 1.1 Generate zone seed data | Done | 18 zones, 6,073 codes, verified programmatically |
| 2.1 Zone model | Done | |
| 2.2 ZoneRepository | Done | |
| 2.3 ZoneController | Done | |
| 3.1 ZoneIcon + ZoneCodeEditor | Done | |
| 3.2 ZoneRegistryPane + dialogs | Done | |
| 3.3 ZoneDetailHeader + ZonesWorkspace | Done | |
| 4.1 AppState/sidebar/main.dart wiring | Done | |
| 5.1 Full verification pass | Done | See below |

**Iteration 2 (group-selection rules):**

| Task | Status | Notes |
|------|--------|-------|
| 6.1 Extend seed generator, re-emit seed.dart | Done | 38 rules across 18 zones; defCodes unchanged (diffed) |
| 6.2 GroupRule, Zone extension, controller methods, dialog field | Done | |
| 6.3 GroupRulesEditor, wire into workspace | Done | |
| 6.4 Verification pass | Done | See below |

## Session Log

### Session 2026-09-02 - Claude

**Started at**: Phase 1, Task 1.1
**Context**: Requirements, Visual, Specifications, and Plan all approved. Specifications
already contained the verified 18-zone catalog. Implemented all 5 phases in one pass, then
verified in Chrome.

#### Completed
- Task 1.1: Wrote a one-off Python generator (not committed) reading the 25 legacy `.conf`
  files, applying the operator+region merge rule, resolving names against `_naprMap` /
  proposed-fresh names, and resolving icons against the actual project asset directory
  (`assets/imgs/napravleine/` — **not** the legacy `.ico` directory, which has a different file
  list; caught and corrected before generating, see Discoveries). Output: `lib/features/
  zones/seed.dart`, 18 zones, 6,073 codes total — matches Specifications exactly.
  - Verified by: script's own printed summary cross-checked against 03-specifications.md's
    table (all 18 ids, all code counts, all icon paths matched).
- Task 2.1–2.3: `lib/features/zones/{models,repository,controller}.dart`, mirroring
  `lib/features/command_sets/`'s equivalents structurally, with the two documented deltas: no
  `isSystem`/`usedByPlanIds` delete-guard, no multi-section (`CommandSetSection`) machinery.
- Task 3.1–3.3: `lib/features/zones/{code_editor,registry_pane,zone_dialogs,detail_header,
  workspace}.dart` — full UI layer, mirroring `command_sets`' widgets file-by-file.
- Task 4.1: `AdmPage.zones` added to the enum (`app_state.dart`, positioned between `nabor` and
  `plan`); `AppState.zones` (`ZoneController`) constructed/disposed alongside the existing
  `commandSets` wiring; `sidebar.dart`'s `_tabs` gained `(AdmPage.zones, 'Направления',
  'napravleine/hz.png')` right after `nabor`; new `lib/pages/zones_page.dart` (thin wrapper,
  mirrors `nabor_page.dart`); `main.dart` got the import + switch case.

#### Verification performed
- `flutter analyze`: 0 new errors, same 2 pre-existing style infos as the baseline before this
  session's changes.
- `flutter build web`: succeeded.
- Served `build/web` and drove it in Chrome:
  - "Направления" appears in the sidebar right after "Наборы команд"; navigating to it shows
    all 18 zones (registry pane) with correct icons, names, id·region, and code counts.
  - Selected "МегаФон СПб" — its 20 codes matched the raw legacy `.conf` file content exactly
    (spot-checked visually against the file read earlier in the session).
  - "Билайн СЗ" renders the `hz.png` fallback icon correctly (no broken-image box) — confirms
    the icon-resolution fallback chain works end-to-end.
  - Edited МегаФон СПб's textarea (appended a line) → draft bar appeared with a live updated
    count (21) → clicked Сохранить → draft bar disappeared, registry row's count updated to 21,
    a success snackbar appeared. Persisted correctly.
  - Created a new zone ("Тестовое направление" / `test_zone`) via the "+" dialog → appeared
    selected immediately with 0 codes; confirmed present via the registry search filter.
  - Deleted it via the "⋮" menu → confirmation dialog quoted the right name/id/code-count →
    confirmed → zone removed, search now shows "Направления не найдены", selection fell back to
    the first remaining zone.
  - Console: no app errors (only unrelated browser-extension warnings).
  - Did **not** get a pixel-verified check of the narrow-width (`<900`) responsive layout — the
    browser automation's `resize_window` call doesn't affect the captured viewport in this
    remote session (same limitation hit during fix1's verification). Confidence here instead
    comes from code review: the `narrow` breakpoint logic in `workspace.dart` is copied verbatim
    from `command_sets/workspace.dart`'s already-shipped, already-working equivalent.

#### Deviations from Plan
- Icon resolution had to be corrected mid-Task-1.1: Specifications originally assumed a
  three-tier fallback (exact → operator-generic → `hz.png`) based on the *legacy* `.ico`
  directory's file list, which includes generic icons (`beeline.ico`, `megafon.ico`, etc.) that
  were never converted into this Flutter project's actual `assets/imgs/napravleine/` PNG set.
  Corrected to a two-tier chain (exact → `hz.png`) and 03-specifications.md was updated in place
  before generating the seed, so the committed spec and the generated data agree.
- `ZoneRepositoryException`/dialog error messages are in Russian, matching
  `CommandSetRepositoryException`'s precedent — not explicitly specified but an obvious
  consistency call.

#### Discoveries
- The legacy `.ico` source directory and this Flutter project's already-converted
  `assets/imgs/napravleine/*.png` directory have **different file lists** — always verify icon
  paths against the actual project asset directory, not the legacy source, when doing this kind
  of asset-mapping work in this repo.

**Ended at**: Phase 5, Task 5.1 — all plan tasks complete and manually verified in Chrome
(narrow-layout responsiveness verified by code review only, not pixel-checked, per the tooling
limitation above).
**Handoff notes**: Local `build/web` output exists from this session's verification; not
committed (build artifact). Dev server stopped. No git commit/push was made — changes sit in
the working tree of the nested `design/simbox-web-design-prototype-v2026` repo, awaiting the
user's review/commit decision, same as fix1/fix2.

---

---

### Session 2026-09-02 (continued) - Claude — Iteration 2: group-selection rules

**Started at**: Task 6.1
**Context**: User pointed to `extensions_dial_zones.conf` and `libsCpp/asterisk-chan-svistok/
src/select.c`, revealing that a "направление" also has an ordered group-selection fallback list
underneath the DEF-codes. Reopened Requirements, amended through to an approved Plan (all in
this same session), then implemented.

#### Completed
- Task 6.1: Extended the Task-1.1 generator to also parse `extensions_dial_zones.conf`'s
  `[macro-makecall-std]`, reusing the exact same abbreviated→canonical merge dict. Parsed each
  `L<N><alg><type>=<XX><GGG>` selector via `get_cr_group()`'s byte grammar. Billing code
  resolution prefers `_naprMap`'s code over the first rule's own code when both exist (catches
  two real legacy data inconsistencies — see Discoveries). Re-emitted `seed.dart`: 38
  group-selection rules across 18 zones (`beeline_sz`: 0, matching that it was never wired into
  the legacy dispatcher).
  - Verified by: `git diff` on `seed.dart` showed zero changes to any `defCodes:` content —
    only additive `billingCode:`/`groupRules:` fields, confirming Iteration 1's data untouched.
- Task 6.2: `GroupRule` added to `models.dart`; `Zone` extended with `billingCode`/`groupRules`
  (constructor, `copyWith`, `==`, `hashCode`); `ZoneController` gained `addGroupRule`/
  `updateGroupRule`/`moveGroupRule`/`removeGroupRule` (all draft-first, mirroring
  `updateCodesText`); `renameZone` gained an optional `billingCode` param; `zone_dialogs.dart`'s
  metadata dialog gained the "Код направления" field.
- Task 6.3: New `lib/features/zones/group_rules_editor.dart` (`GroupRulesEditor` + `_RuleRow`,
  a `StatefulWidget` holding its own `TextEditingController` for the group-number field with
  the same sync-on-external-change pattern as `ZoneCodeEditor`, to avoid fighting the cursor
  during normal typing). Wired into `workspace.dart`'s `_DetailPane`: gave `ZoneCodeEditor` a
  fixed 280px height (it needs a bounded ancestor for its internal `Expanded`/`expands: true`
  textarea) inside a `SingleChildScrollView`, with `GroupRulesEditor` stacked below it in the
  same scrollable region, and the shared `_DraftBar` still pinned outside the scroll.

#### Verification performed
- `flutter analyze`: 0 new errors, same 2 pre-existing style infos.
- `flutter build web`: succeeded.
- Served `build/web`, drove it in Chrome:
  - "МегаФон СПб" shows exactly 4 rules matching the hand-traced legacy data precisely,
    including the alg/type character-by-character (`L1D=NS101` → L=1,alg=D,type='=',group=101;
    `L3>_NS102` → L=3,alg='>',type='_',group=102; `L3>=NS162` → L=3,alg='>',type='=',group=162).
  - "Билайн СЗ" shows "Правила выбора группы (0)" with the empty-state message — confirms a
    zone genuinely absent from the legacy dispatcher imports with zero rules, not a crash or a
    guessed default.
  - Clicked "Добавить правило" → count went 4→5, shared draft bar appeared → clicked "Отмена" →
    reverted to 4, draft bar gone — confirms the add/cancel cycle and the *shared* draft with
    DEF-codes (one bar governs both sections).
  - Opened the metadata (pencil) dialog for "МегаФон СПб" → "Код направления" field pre-filled
    with "NS", matching `_naprMap`'s code for this zone exactly.
  - Console: no app errors (only unrelated browser-extension warnings).
  - Did not get a full screenshot of the 4th rule row in the narrow test-window screenshot
    session (short viewport cut it off) — not re-verified pixel-by-pixel, but the same generator
    output that produced the 3 visually-confirmed rows produced it, and the printed
    per-zone rule counts (4 for `megafon_spb`) were already cross-checked against the source
    file's line count during Task 6.1.

#### Deviations from Plan
- None beyond the two data-quality warnings anticipated in Specifications' Edge Cases table
  (`beeline_ru` and `mts_msk` each have one rule using the wrong 2-letter code — legacy
  copy-paste artifacts) — handled exactly as planned (billing code falls back to `_naprMap`,
  warning printed, build not blocked).

#### Discoveries
- Two more legacy data inconsistencies surfaced by the "prefer `_naprMap`, warn on disagreement"
  rule: `beeline_ru`'s first rule uses code `BC` (bee_**chel**'s code) instead of `BR`, and
  `mts_msk`'s uses `BM` (bee**line**_msk's code) instead of `SM` — both are separate, smaller
  instances of the same kind of copy-paste bug the `beeline_spb`/`beeline_sz` naming confusion
  already demonstrated in Iteration 1. Worth remembering: this legacy dataset has several of
  these small cross-contamination bugs; don't assume any single zone's data is internally
  self-consistent without checking.

**Ended at**: Task 6.4 — all Iteration 2 tasks complete and manually verified in Chrome.
**Handoff notes**: Same as Iteration 1 — no commit made, dev server stopped, changes sit in the
working tree of the nested `design/simbox-web-design-prototype-v2026` repo.

---

## Deviations Summary

| Planned | Actual | Reason |
|---------|--------|--------|
| 3-tier icon fallback (exact → operator-generic → hz.png) | 2-tier (exact → hz.png) | This project's converted PNG set has no generic operator icons (`beeline.png` etc. don't exist), unlike the legacy `.ico` source directory used to draft the original plan |
| (Iteration 2) None | — | Implemented exactly as specified |

## Learnings

- When mapping legacy assets into this Flutter project, always check the actual
  `assets/imgs/...` directory the app ships with — the legacy source tree's file list is not a
  reliable proxy for it, even for files that look like a 1:1 conversion.
- The `command_sets` repository/controller/workspace architecture generalizes cleanly to a much
  simpler record shape (a zone vs. a full command set with sub-sections) — mirroring it
  file-by-file kept this implementation fast and low-risk with no structural surprises.
- (Iteration 2) This legacy dataset has multiple small copy-paste inconsistencies (wrong
  2-letter billing codes reused across similarly-named zones) — when importing legacy data
  programmatically, prefer a known-good cross-reference (here, `_naprMap`) over "trust the
  first occurrence" whenever one is available, and always print/log disagreements rather than
  silently picking one.

## Completion Checklist

- [x] All tasks completed or explicitly deferred (narrow-layout pixel check and one rule row's
      on-screen visibility deferred to code/data review, see notes above)
- [x] Tests passing (N/A — no automated test suite; manual verification per plan)
- [x] No regressions (fix1/fix2/Iteration-1 functionality re-verified working in the same
      session's screenshots)
- [ ] Documentation updated if needed (no README claims contradicted; optional Documentation
      phase not started, pending user request)
- [ ] Status updated to COMPLETE (pending user sign-off on this log)
