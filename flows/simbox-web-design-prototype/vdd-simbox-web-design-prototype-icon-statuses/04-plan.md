# Implementation Plan: Icon legend labels and Glossary

> Version: 2.0
> Status: APPROVED
> Last Updated: 2026-09-02
> Specifications: [03-specifications.md](03-specifications.md)

## Goal

Correct every existing icon label/tooltip without changing the current Icons page composition, and
add a separate Glossary backed by the same terminology source. No telephony, selection, routing,
server classification or table geometry changes are included.

## Guardrails

- Preserve every current `icons_catalog.dart` group, tile asset, raw code, order and count.
- Do not add a missing historical/status icon to the legend during this flow.
- Do not replace or redraw existing legend icons.
- Keep `IconsPage` padding, cards, `Wrap`, 190px tiles, text overflow and Tooltip interaction.
- Raw codes, filenames and formulas are never translated.
- Unresolved meanings remain explicitly unresolved.
- Vendor exactly one new Fugue pair for Glossary navigation: `book-open-list.png` 16×16/32×32.

## Task 1 — Freeze the existing legend structure

**Files**

- Create `test/icon_legend_structure_test.dart`.

**Work**

1. Record the current ordered group titles/paths.
2. Record each group's ordered `(file, rawCode)` pairs before changing the catalog representation.
3. Assert group count, per-group item count and the complete flattened sequence.
4. Do not snapshot labels: labels are the intended change.

**Verification**

- The test passes against the current pipe-string catalog.
- The same test must continue to pass after Task 3's typed conversion.

## Task 2 — Add shared terminology primitives

**Files**

- Create `lib/data/terminology.dart`.
- Create `test/terminology_test.dart`.

**Work**

1. Implement `LocalizedText`, `TermConfidence` and `TermDefinition` from Specifications 2.0.
2. Add a deterministic resolver: selected locale → English fallback → explicit missing marker.
3. Add stable IDs for every term referenced by the current icon legend and `icon_map.dart`.
4. Populate corrected short labels and full tooltips from the approved semantic manifest.
5. Add glossary definitions/formulas only where source/owner evidence is sufficient.
6. Mark PAL, IMA, REC 90/91/92, IMO and other unresolved entries explicitly; do not infer.

**Verification**

- IDs are unique.
- All five locale keys are structurally supported; fallback behavior is tested.
- Formula tests preserve exact ACD/ASR/GOO expressions and inclusive thresholds.

## Task 3 — Type the current icon catalog without visual changes

**Files**

- Modify `lib/data/icons_catalog.dart`.
- Modify `lib/pages/icons_page.dart`.
- Extend `test/icon_legend_structure_test.dart`.
- Create `test/icons_page_test.dart`.

**Work**

1. Replace each `'file|code|label'` string with `IconLegendItem(file, code, termId)`.
2. Keep every group and item in its exact frozen sequence.
3. Change `_tile()` only to read typed fields and resolve terminology.
4. Change text content:
   - title → `Легенда иконок GostSimBox`;
   - instruction → corrected hover instruction;
   - misleading group titles → approved text-only replacements;
   - tile labels/tooltips → shared terminology.
5. Preserve the existing widget tree and layout constants.

**Verification**

- Structure snapshot from Task 1 remains green.
- Widget test asserts `Wrap`, tile width `190`, group order and Tooltip format.
- No search/filter/badge/expansion widgets appear.

## Task 4 — Correct operational table icon tooltips

**Files**

- Modify `lib/data/icon_map.dart`.
- Update/add focused tests in `test/icon_map_test.dart`.

**Work**

1. Preserve every current mapping function signature and selected asset.
2. Replace incorrect hard-coded tooltip text with shared terminology references.
3. Cover confirmed corrections including:
   - GOO formula/threshold meaning;
   - IM B/C/D/E/N meanings and historical IMA;
   - SOU as a call between two managed SIMs;
   - CFUN/SIMST/SRVST corrections;
   - MAY/MON/MSM separation;
   - END_PARTY wording;
   - incoming recency as caller-number + receiving-SIM history.
4. Preserve explicit unknown fallbacks and raw values.

**Verification**

- Representative `Ico.*()` results match the corresponding legend term text.
- No table column, size, sort behavior or runtime lookup changes.

## Task 5 — Add the Glossary catalog

**Files**

- Create `lib/data/glossary_catalog.dart`.
- Extend `test/terminology_test.dart`.

**Work**

1. Add approved groups in the Visual 2.0 order.
2. Store only ordered term IDs in groups; definitions stay in `terminology.dart`.
3. Include confirmed terms first: ACD, ASR, GOO, Number B, IM relations, END_PARTY, modem/network
   states, routing terms and MAY/MON/MSM.
4. Omit or explicitly mark unresolved definitions; do not complete from industry convention alone.

**Verification**

- Every glossary term ID resolves exactly once.
- No definition/formula is duplicated in the grouping file.

## Task 6 — Build the separate Glossary page

**Files**

- Create `lib/pages/glossary_page.dart`.
- Create `test/glossary_page_test.dart`.

**Work**

1. Reuse the current Icons title-card and group-card styling tokens.
2. Render grouped term/definition rows with optional formula/aliases.
3. At narrow width stack the definition below the term; avoid horizontal scrolling.
4. Do not decorate every glossary row with a status icon.
5. Provide English fallback for missing localized text.

**Verification**

- Wide and narrow widget tests verify row composition and wrapping.
- Empty groups are omitted.

## Task 7 — Vendor the Glossary Fugue pair and wire navigation

**Files**

- Add `assets/fugue/book-open-list.png` from canonical Fugue 3.5.6 16×16.
- Add `assets/fugue/2.0x/book-open-list.png` from the matching 32×32 rebuild.
- Modify `lib/state/app_state.dart`.
- Modify `lib/main.dart`.
- Modify `lib/widgets/sidebar.dart`.
- Extend `test/fugue_icon_test.dart` and add navigation coverage.

**Work**

1. Add `AdmPage.glossary` after `icons` in the reference/navigation order.
2. Route it to `GlossaryPage`.
3. Append `Глоссарий` after `Иконки` in the sidebar with
   `fugue:book-open-list.png`.
4. Preserve the existing 16-logical-pixel Fugue rendering footprint.

**Verification**

- File dimensions are exactly 16×16 and 32×32.
- Sidebar order and compact/full modes render correctly.
- Clicking Glossary opens only the separate Glossary page.

## Task 8 — Full validation and visual regression check

**Commands/checks**

1. `dart format lib test`
2. `flutter analyze`
3. `flutter test`
4. Run the prototype and capture Icons at the same wide viewport before/after.
5. Capture Glossary at wide and narrow viewports.

**Acceptance**

- Icons has identical controls, cards, group order, tile order, wrapping and asset placement.
- Only approved text differs on Icons.
- Every existing tile has corrected visible label, raw code and Tooltip.
- Glossary is a separate sidebar destination and is readable at both widths.
- Fugue density pair is used correctly.
- No unrelated files or user changes are modified.

## Dependency Order

```text
Task 1 structure snapshot
        ↓
Task 2 terminology
        ↓
Task 3 legend conversion ──────┐
Task 4 table tooltips          │
Task 5 glossary catalog ───────┤
        ↓                      │
Task 6 glossary page           │
        ↓                      │
Task 7 asset + navigation      │
        └──────────────────────┘
                 ↓
          Task 8 validation
```

## Risks and Controls

| Risk | Control |
|---|---|
| Typed conversion accidentally changes legend contents | Task 1 freezes asset/code sequence before conversion |
| A short label becomes misleading after truncation | Full meaning remains in Tooltip; test representative long labels |
| Glossary and tooltip drift | Both resolve the same `TermDefinition` ID |
| Unresolved legacy abbreviations become invented facts | Explicit confidence/unresolved state and source-backed review |
| Retina icon renders at 32 logical pixels | Existing Fugue widget keeps 16 logical pixels; 32×32 is density only |
| Scope expands into server/client classification | Formulas are explanatory only; runtime classification remains untouched |

## Approval

- [x] Reviewed by: Anton Dodonov
- [x] Approved on: 2026-09-02
- [x] Notes: Plan approved; implementation authorized.
