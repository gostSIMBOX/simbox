# Status: vdd-simbox-web-design-prototype-readers-uiux

## Current Phase

IMPLEMENTATION

## Phase Status

APPROVED

## Last Updated

2026-09-02 by Claude

## Blockers

- None. All 7 plan tasks completed, verified live in-browser (Chrome, via claude-in-chrome),
  `flutter test` (15/15) and `flutter analyze` (0 issues) both clean. Flow is functionally
  complete. No commit made yet — only on explicit user request, per standing project convention.

## Progress

- [x] Requirements drafted
- [x] Requirements approved
- [x] Visual mockups drafted
- [x] Visual approved
- [x] Specifications drafted
- [x] Specifications approved
- [x] Plan drafted
- [x] Plan approved
- [x] Implementation started
- [x] Implementation complete
- [ ] Implementation complete
- [ ] Documentation drafted (optional — only if requested)
- [ ] Documentation approved

## Context Notes

- **Root cause found**: `legacy/simbox-desktop-v2014/www/simbox/hubs.php` and `readers.php`
  are two separate legacy pages that both literally contain `<h1>Ридеры</h1>` (a 2014
  copy-paste leftover — `hubs.php` is 100% USB-tree/power-control logic despite the borrowed
  title). The v2026 Flutter prototype ported only `hubs.php`'s logic into `HubsPage`
  (`AdmPage.hubs`), keeping the borrowed "Ридеры (хабы)" heading, and never built `readers.php`
  (physical SIM-card-reader devices: ICCID/IMSI/KI/PIN/state/dataport table + PIN/KI-search/APDU
  actions) at all.
- **Scope confirmed Readers-only** (2026-09-02): the `HubsPage` heading was fixed immediately,
  out of band, in `design/simbox-web-design-prototype-v2026/lib/pages/hubs_page.dart:76`
  (`"Ридеры (хабы)"` → `"Хабы (Hubs)"`) — not part of this flow's phase-gated deliverables,
  just a trivial correction done on request so the two concepts wouldn't stay conflated while
  Readers is designed. `HubsPage`'s table/columns/actions are otherwise untouched and out of
  scope.
- **Full column/action inventory extracted from `readers.php`** (live, non-commented-out code
  only) is in `01-requirements.md`'s "Deep Legacy Analysis" section — exact `/var/svistok/...`
  file-per-fact data sources, the KI-all-zero → `"00"` display rule, the `result` code suffix
  rule (visible unless `0` or `1000`), and the `.gsm` filesize÷58 progress-bar convention.
- **Page shape decided (Visual phase)**: flat dense-table page (`ColDef`/`DenseTable`,
  `TableHeading`/`TableToolbar`, `ActionGroup`/`SubAction`/`AdmField`) — same shape as
  `HubsPage`/`DonglesPage`, explicitly *not* the registry+detail workspace shape used by
  `zones`/`command_sets`. No narrow/stacked variant needed — `DenseTable` has no narrow branch
  anywhere in this codebase (Sims/Hubs/Dongles all just scroll horizontally).
- **Nav icon decided**: reuse `assets/imgs/pl2303.png` (already shown per-row as the reader-chip
  model icon) at nav size for the new "Ридеры" sidebar item — resolves the Open Question from
  Requirements. Rejected `lock.png` (collides in meaning with the per-row `lock` column, a
  physical card-lock state unrelated to "this nav item is about security") and a new vendored
  Fugue glyph (unnecessary — a fitting asset already exists locally).
- **Nav position decided**: "Ридеры" inserted directly before "Хабы" in the sidebar tab list —
  both are USB-hardware concepts and should sit adjacent, same reasoning as the existing
  Свистки (nm)/Свистки (um) adjacency.
- **Row modeling decided**: one mock row per reader **device** (from `readers.list`), with
  card-keyed fields (ICCID/IMSI/KI/progress/state-suffix) simply blank when no card is present —
  matches legacy's actual per-device iteration with per-card lookups keyed by that device's
  current ICCID. Not modeling readers/cards as two separate joined tables — out of proportion
  for a mock-data prototype.
- **Mock data coverage locked into the mockup** (6 rows in `02-visual.md`): no-card device
  (blank fields), no-card device with unrecognized model (blank model icon too), fully-ID'd
  card w/ resolved KI, fully-ID'd card w/ literal `0000` PIN (distinct from "no PIN" blank),
  mid-KI-search (KI still `"00"`, non-zero progress, fault-code suffix on state), card-present
  error row (state `Error`, KI still `"00"`, no progress) — exercises every column's non-empty
  state per Requirements Acceptance Criteria #5.
- **Architecture precedent to reuse (no new pattern needed)**: `lib/pages/dongles_page.dart`'s
  existing `_pin`/`AdmField`/`SubAction` PIN block and AT-command text-field block are the direct
  precedent for the new Readers page's PIN and APDU actions (same shape, different target
  device type). Poиск KI's warning banner reuses this codebase's existing danger/caution visual
  language (e.g. delete-confirmation dialogs), shown persistently while that action group is
  open — not a one-off toast.
- **Icon gap resolved, no vendoring needed**: only 29 of the full Fugue catalog are vendored in
  `assets/fugue/`; none is a card/chip/key glyph — but `assets/imgs/pl2303.png` covers the need,
  so no new Fugue glyph vendoring is required for this flow.

## Fork History

N/A — new flow.

## Next Actions

Flow complete — all 7 implementation tasks done and verified (see `05-implementation-log.md`).
Remaining, optional, user's call only:
1. Committing the change (this project's convention: only on explicit request).
2. Optional DOCUMENTATION phase (client-facing README) — not started, only pursue if requested.
