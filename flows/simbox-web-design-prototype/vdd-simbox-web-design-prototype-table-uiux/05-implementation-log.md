# Implementation Log: simbox-web-design-prototype-table-uiux

> Started: 2026-09-05
> Plan: [04-plan.md](04-plan.md)

## Progress Tracker

| Task | Status | Notes |
|------|--------|-------|
| 1.1 Terminology entries | Done | 5 terms added to `terminology.dart` |
| 1.2 Group holiday pause | Done | pause 2/12/22 branches added to `Ico.group()` |
| 1.3 SPAM/IMO/SYS qos | Done | `_qosMap` extended |
| 1.4 fas/vip/pre/pos/liveCall helpers | Done | 4 new `Ico` methods |
| 2.1 `Sim` model fields | Done | ~18 fields added, `lim0`/`lim1` removed |
| 3.1 group column | Done | no code change needed, picks up Task 1.2 automatically |
| 3.2 spec column 5-icon stack | Done | |
| 3.3 io/state column | Done | + `_busyNumberB`/`_busyNumberA` helpers |
| 3.4 may/mon/msm/sms column | Done | |
| 3.5 pddas column | Done | |
| 3.6 LIMIT0-5 loop | Done | replaces old single `lim0` `ColDef` |
| 3.7 dongle sub-line | Done | |
| 3.8 pro column + blue-text | Done — **deviated from spec**, see Deviations | |
| 4.1 Extend mock.dart rows | Done | 8 rows, not 5 (see Discoveries) |
| 4.2 Scenario coverage | Done | see checklist below |
| 5.1 Static checks | Done | `flutter analyze` clean (3 pre-existing infos only), `flutter test` 34/34 pass |
| 5.2 Manual browser verification | Done | LIMIT0-5 confirmed in a follow-up session, see Session 2 below |

## Session Log

### Session 2026-09-05 - Claude

**Started at**: Phase 1, Task 1.1
**Context**: Plan approved; all 5 flow docs (requirements/visual/specifications/plan) already
written and approved earlier in this session.

#### Completed

All 16 planned tasks across Phases 1-5. Files changed:
- `lib/data/terminology.dart` — 5 new term IDs
- `lib/data/icon_map.dart` — group() holiday branches, qos SPAM/IMO/SYS, new fas()/vip()/pre()/
  pos()/liveCall() methods
- `lib/data/models.dart` — `Sim` gains ~18 fields (removes `lim0`/`lim1`), `Cell` gains one `bool
  pending` field
- `lib/widgets/dense_table.dart` — `_cell()` honors `Cell.pending` for blue text
- `lib/pages/sims_page.dart` — `pro` column added; `spec`, `io`, `may`, `dongle` columns rebuilt;
  `pddas` column added; `lim0`/`lim1` replaced by a 6-column `LIMIT0..LIMIT5` loop;
  `_busyNumberB`/`_busyNumberA` helpers added
- `lib/data/mock.dart` — all 8 existing `Sim(...)` rows extended with the new fields, redundant
  `const` lints cleaned up
- `test/icon_map_test.dart` — 5 new unit tests for the new `Ico` methods

Verified by: `flutter analyze` (clean except 3 pre-existing informational lints unrelated to this
flow — `models.dart`'s dangling doc comment, `zones/controller.dart`'s curly-braces style,
`hubs_page.dart`'s const-declaration style — matching the exact pattern the icon-statuses flow's
own implementation log already noted as pre-existing/out-of-scope); `flutter test` (34/34 pass,
29 pre-existing + 5 new); manual browser verification via `flutter run -d chrome` (see below).

#### Deviations from Plan

1. **`pro` column blue-text mechanism**: the plan's Task 3.8 (following Specifications) proposed
   "an inline `Text` built directly in this `ColDef`'s `build`, bypassing `_cell()`'s shared
   stacking helper." This turned out to be **impossible as specified** — `ColDef.build` is typed
   to return a `Cell`, not a `Widget`, so there is no way to hand `DenseTable` a one-off custom
   widget for a single column without changing that type contract. Also, `models.dart` is
   deliberately Flutter-import-free (verified: zero imports in the file before this change), so
   adding a `Color`-typed field to `Cell` would have broken that invariant. Resolved instead with
   the smallest change that preserves both constraints: added `Cell.pending` (a plain `bool`, no
   Flutter dependency), consumed by `dense_table.dart`'s existing `_cell()` to render `text` in
   `T.brandDeep` instead of `T.cell` when true. Same visual outcome, smaller and more consistent
   footprint than either option Specifications considered.
2. **LIMIT palevo icon**: Specifications' snippet used a raw `IcoRef('qos/ipalevo.png', 'PAL')`
   inline. Implemented as `Ico.captcha('ipalevo')` instead — an existing helper already wired to
   the shared `captcha.pal` term, giving the full "PAL · значение не установлено" tooltip via the
   terminology system rather than a bare literal string. Same asset, better-integrated tooltip.
3. **Mock row `id: 3`'s `qos` value**: caught during manual browser verification, not during
   implementation — see Discoveries below. Not a plan deviation so much as a bug the plan's own
   Task 5.2 checkpoint was designed to catch, and did.

#### Discoveries

- **`mock.dart` has 8 `Sim` rows, not 5.** Every prior doc in this flow (Requirements, Plan)
  said "5 existing rows," carried forward from an early, never-corrected assumption. Verified the
  actual count directly before touching the file (`grep -n "^  Sim($"` → 8 matches) and updated all
  8, not 5. Doesn't change anything structurally, just corrects a repeated inaccuracy.
- **A real mock-data bug caught by manual verification, not static analysis**: row `id: 3` was
  set up as "the SOU busy-call demo row" (its `numberb` carries the `#SOU<imsi>` encoding), but its
  `qos` field was left at the row's original `'BLO'` value. `flutter analyze`/`flutter test` can't
  catch this — it's a semantic inconsistency, not a type error. Hovering the row's state-column
  icon in the running app showed "BLO — Усиленная блокировка" instead of the expected SOU
  wording, because `Ico.qos(s.qos, s.io)` reads the `qos` *field*, which is independent of what
  string `numberb` happens to contain. In real legacy, both are set together by the same dialplan
  branch (`extensions_dial.conf`'s `s-SOU`), so a mock row demonstrating one should demonstrate
  both. Fixed by changing `qos: 'BLO'` → `qos: 'SOU'` for that row (with a comment explaining why
  they're coupled), verified by a fresh `flutter run` (see below) showing the corrected tooltip:
  "SOU — SIM-to-SIM: инициирующая сторона".
- **`flutter run`'s hot-reload does not trigger automatically on file save** from an external
  editor — it only reloads on an explicit signal (interactive `r` keypress, or IDE
  save-integration). Editing files while a `flutter run -d chrome` session is already running and
  then just refreshing the browser (F5) serves the **stale** already-compiled build; this cost one
  round of confusing "why didn't my fix apply" before realizing a full restart of the `flutter run`
  process was needed to pick up the `mock.dart` edit. Worth remembering for any future session in
  this repo: after editing Dart source while a dev server is already running, restart the process
  rather than trusting a browser refresh alone.
- **Driving `DenseTable`'s internal horizontal `SingleChildScrollView` via synthetic browser
  input didn't work in this session** (see Deviations/manual verification below) — multiple
  attempts (wheel-scroll with `scroll_direction: right`, drag on the visible scrollbar-thumb
  position, drag-pan directly on table content) all produced no visible movement. Root cause not
  conclusively diagnosed (CanvasKit renders to one canvas with no DOM scrollable for
  `find`/`read_page` to target, and this session's `find` tool confirmed the accessibility tree
  has no table structure at all — "generic containers... no table structure"). This is a browser-
  automation friction point specific to canvas-rendered Flutter web apps, not evidence of an app
  bug — the identical `Cell`/`ColDef` rendering mechanism used by `LIMIT0..LIMIT5` is already
  visually confirmed correct for 6 *other* new columns that happened to be within the initial
  viewport (`pro`, the 5-icon `spec` cluster, the `state`/`io` column including the corrected SOU
  tooltip, the 4-line `may` column, `pddas`, and the `dongle` hub-port sub-line all rendered
  without overflow or crash, confirmed by screenshot + zoomed inspection + console check showing
  zero new errors beyond one pre-existing, unrelated 404 for `application-monitor.png` —
  `lib/widgets/sidebar.dart:16`, not touched by this flow).

**Ended at**: Phase 5, Task 5.2 (partial — LIMIT0-5 columns not yet visually reachable)
**Handoff notes**: If a future session has working horizontal-scroll browser automation for this
app (or just wants to eyeball it directly rather than through this session's tooling), the
remaining unverified-in-browser item is: scroll the Sims table right past the `PDDL0`/`PDDL1`/
`pri` columns and confirm all six `LIMIT0`..`LIMIT5` columns render in order, with the palevo flag
icon appearing only on row `id:1`'s `LIMIT0` and row `id:4`'s `LIMIT3` (per the mock data seeded in
Task 4.2). Everything else in the Testing Strategy's manual checklist was confirmed.

---

### Session 2 (same day, 2026-09-05) - Claude

**Started at**: Phase 5, Task 5.2 (resuming the one deferred item)
**Context**: Restarted `flutter run -d chrome --web-port=8766` (session 1's process had been
killed as cleanup); re-confirmed the SOU tooltip fix persisted on a fresh build
("SOU — SIM-to-SIM: инициирующая сторона", not "BLO — Усиленная блокировка" — not stale).

#### Completed

- Solved the horizontal-scroll automation problem from Session 1. `computer` tool wheel-scroll and
  scrollbar-thumb drag both still failed against `DenseTable`'s `SingleChildScrollView` (same as
  before). What worked: dispatching a real `WheelEvent({deltaX: 1000, deltaY: 0, composed: true})`
  directly on the `<flt-glass-pane>` element via `javascript_tool` — Flutter web's actual
  pointer-event host (found by enumerating `document.querySelectorAll('*')` tag names; the
  `<flutter-view>` wrapper has no shadow root, `<flt-glass-pane>` is a plain light-DOM child and is
  the real event target). Window `resize_window` to 3400×900 was attempted first and did **not**
  work (`window.innerWidth` stayed 1920 after the call) — not a viable alternative in this
  environment.
- With the table scrolled, visually confirmed via zoomed screenshot: all six `LIMIT0`..`LIMIT5`
  headers present in order, values match `mock.dart` exactly (`6400/9000`, `2100/9000`, `0/9000`
  ×4-per-row, `8800/9000`/`120/9000`/`0/9000`/`150/150`/`0/9000`/`0/9000`), and the `ipalevo.png`
  flag icon appears in exactly two places: row `id:1`'s `LIMIT0` and row `id:4`'s `LIMIT3` — every
  other cell in every other row is plain text, no flag. Exactly matches the Task 4.2 scenario spec.
  Also visible in the same screenshot: `ASRL`/`PDDAS`/`PDDL0`/`PDDL1` as four distinct columns
  (headers truncated to "PDD.." at this zoom but four separate cells with four different values
  confirm they're not merged), and the pre-existing red-bold blacklisted-IMEI styling on row
  `id:3` still intact (no regression).
- Console check after the scroll: only the same 2 pre-existing messages from Session 1 (the
  `application-monitor.png` 404 from `sidebar.dart`, and a `Scrollbar`/`PrimaryScrollController`
  assertion that traces to a *different* widget than `DenseTable` — `DenseTable` explicitly
  constructs and passes its own `ScrollController` per `dense_table.dart:45`, so this pre-existing
  warning belongs elsewhere in the app, not to anything this flow touched). Zero new console output
  from scrolling into the LIMIT columns.
- Cleaned up: killed the `flutter run` background process.

#### Discoveries

- **Root cause of Session 1's scroll-automation failure, now identified**: it wasn't a Flutter-app
  bug, it was that synthetic input from the `computer` tool (mouse wheel emulation, drag-based
  scrollbar emulation) apparently isn't reaching `<flt-glass-pane>` the way a real OS-level input
  event would, while a JS-constructed `WheelEvent` dispatched directly on that element works
  correctly. Worth remembering for any future session driving this (or any other CanvasKit-based
  Flutter web) app: prefer `javascript_tool` + a direct `WheelEvent` dispatch on `<flt-glass-pane>`
  over the `computer` tool's scroll/drag actions for horizontal scroll regions.

**Ended at**: Phase 5, Task 5.2 (complete)
**Handoff notes**: None outstanding — every item in the Testing Strategy's manual verification
checklist is now confirmed.

## Deviations Summary

| Planned | Actual | Reason |
|---------|--------|--------|
| `pro` column: inline `Text` bypassing `_cell()` | `Cell.pending: bool` consumed by `_cell()` | Original plan was impossible given `ColDef.build`'s `Cell`-typed return contract and `models.dart`'s Flutter-import-free convention |
| LIMIT palevo icon: raw `IcoRef` literal | `Ico.captcha('ipalevo')` | Reuses the existing shared-term helper instead of a bare string, no behavior change |
| Manual verification: full LIMIT0-5 visual check | Deferred in Session 1, completed in Session 2 via a JS-dispatched `WheelEvent` on `<flt-glass-pane>` (the `computer` tool's scroll/drag couldn't drive it in either session) | Browser automation friction, not an app defect — see Session 2's Discoveries |

## Learnings

- When a spec proposes "bypass the shared render helper for just this one case," check the actual
  type signatures first — `ColDef.build: Cell Function(TRow)` made that literally impossible here,
  and the smaller-footprint fix (one new `bool` field, consumed at the one call site that cares)
  was available all along.
- Manual verification catches things static analysis structurally cannot: the `id:3` `qos`/
  `numberb` mismatch was invisible to `flutter analyze` and `flutter test` alike (both fields are
  independently valid strings; only the paired *meaning* was wrong) and only surfaced by actually
  reading the rendered tooltip.
- For this repo specifically: restart `flutter run` after editing source, don't rely on browser F5
  hot-reload.

## Completion Checklist

- [x] All tasks completed (all 16 plan tasks + the deferred LIMIT0-5 visual check, now closed)
- [x] Tests passing (34/34, including 5 new)
- [x] No regressions (`flutter analyze` shows only the same 3 pre-existing informational lints
      present before this flow started; console shows only the same 2 pre-existing runtime
      messages, both traced to code outside this flow's scope)
- [ ] Documentation updated if needed — DOCUMENTATION phase not yet started (optional per VDD flow)
- [ ] Status updated to COMPLETE — pending user review of this log
