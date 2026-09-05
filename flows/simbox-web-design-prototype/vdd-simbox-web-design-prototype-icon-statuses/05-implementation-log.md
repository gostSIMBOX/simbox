# Implementation Log: Icon statuses and tooltips

> Status: COMPLETE — AWAITING VISUAL REVIEW
> Implemented: 2026-09-02

## Outcome

- Preserved the existing Icons page cards, Wrap layout, 190px tile width, icon assets, group/item
  order and 164-item inventory.
- Renamed the page content to “Легенда иконок GostSimBox” and corrected its hover instruction.
- Added typed public legend items with stable semantic IDs while retaining a compact, auditable
  legacy seed notation for the frozen inventory.
- Added shared localized terminology primitives with English fallback for `en/th/ru/hi/zh`.
- Corrected audited labels/tooltips for GOO, Number B recency, SOU, END_PARTY, CFUN/SIMST/SRVST,
  IM relationships, MAY/MON/MSM, recognition families and unresolved legacy codes.
- Added a separate responsive Glossary page after Icons in navigation.
- Vendored canonical Fugue `book-open-list.png` at 16×16 and its matching 32×32 density asset.

## Important Semantic Controls

- GOO remains a server-provided class; UI only explains the confirmed inclusive rule:
  `ACD >= 300 && ASR >= 80`.
- ACD and ASR formulas use `total_billsec`, `total_answered` and `total_calls` exactly as approved.
- Incoming recency explicitly refers to the caller-number + receiving-SIM pair.
- SOU explicitly means one managed SIM calling another managed SIM.
- MAY short-call beacon, MAY callback command, MON top-up request and MSM SMS fallback remain
  separate terms.
- PAL, IMA producer, REC 90/91/92, NE0/NEM live production and exact SPE/MAG/NAV/MON-spec
  meanings remain marked unresolved instead of inferred.

## Verification

- `flutter test`: 27 tests passed before golden coverage; full suite passes after additions.
- `flutter analyze`: no errors or warnings; three pre-existing informational lints remain outside
  this flow (`models.dart`, zones controller, hubs page).
- Structure regression: 10 groups, counts `12/13/13/19/13/16/18/6/26/28`, 164 items, stable
  asset/raw-code sequence hash.
- Fugue PNG checks: 16×16 logical source and 32×32 Retina density source.
- Widget coverage: Icons geometry, shared tooltips, terminology fallback/formulas, wide/narrow
  Glossary layout.
- Golden captures: `test/goldens/icon_legend_wide.png` (1400×900) and
  `test/goldens/glossary_narrow.png` (480×900). No overflow or table displacement observed.
- In-app browser runtime was unavailable (`agent.browsers.list()` returned no browsers), so
  interactive browser click-through could not be performed in this environment.

## Files Added

- `lib/data/terminology.dart`
- `lib/data/glossary_catalog.dart`
- `lib/pages/glossary_page.dart`
- `assets/fugue/book-open-list.png`
- `assets/fugue/2.0x/book-open-list.png`
- icon terminology, structure, page, Glossary and visual regression tests

## Review Request

Review the updated Icons labels/tooltips and the separate Glossary destination. Implementation is
complete; final VDD documentation approval remains open.
