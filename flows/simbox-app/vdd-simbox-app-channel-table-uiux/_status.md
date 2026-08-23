# Status: vdd-simbox-app-channel-table-uiux

## Current Phase

IMPLEMENTATION

## Phase Status

CODE COMPLETE — implemented, `dart analyze`/`flutter test` clean;
final visual-fidelity sign-off gated on a font-asset blocker shared
with `vdd-simbox-app-uiux` (see Blockers)

## Last Updated

2026-08-23 by Claude (flow created by extracting the "Каналы"
table/view-mode work out of `vdd-simbox-app-uiux`, at Anton's explicit
instruction — all 5 phases' content moved as-is, nothing re-derived)

## Blockers

- **Shared font-asset blocker** (inherited from `vdd-simbox-app-uiux`,
  not this flow's own): all five files named `sf-pro-text-*.ttf` in
  both `design/nativemind-designsystem-v1.8/uploads/` and
  `design/nativemind-designsystem-v1.8/assets/fonts/` are GitHub HTML
  pages, not fonts. `apps/simbox-app/assets/fonts/`'s vendored copies
  are therefore invalid too. This flow's UI is built on the same app
  as `vdd-simbox-app-uiux`'s base screens, so final visual-fidelity
  sign-off (real bundled SF Pro Text) needs the same resolution —
  either valid licensed font files or Anton's explicit approval to use
  a platform-native fallback. **Does not block this flow's code/tests**
  — Tasks 1-5 are implemented and verified against the platform
  fallback, same precedent as `vdd-simbox-app-uiux`'s own Task 13.
- По-SIM-все's "не в модеме" row (unseated SIM cards) waits on
  `sdd-flutter_gsmsip-interface`'s SIM-inventory-independent-of-modem
  addendum (flagged there 2026-08-23, both copies — `libsFlutter/
  flutter_gsm/flows/` and `libsFlutter/flutter_gsmsip/flows/`) — not
  started, separate flow's work.
- A real Модемы dense-table (to extend the Табличный-вид toggle there
  too) is a legitimate future enhancement, not started — see
  05-implementation-log.md's Deviations Summary for why it's out of
  this flow's scope.

## Progress

- [x] Requirements drafted (v1.0, 2026-08-23 — extracted, approved
      content, unchanged)
- [x] Requirements approved (2026-08-23, as part of `vdd-simbox-app-uiux`
      v1.3, before extraction)
- [x] Visual mockups drafted (v1.0, 2026-08-23 — extracted, approved
      content, unchanged)
- [x] Visual mockups approved (2026-08-23, as part of `vdd-simbox-app-uiux`
      v1.1/v1.2, before extraction)
- [x] Specifications drafted (v1.0, 2026-08-23 — extracted, approved
      content, unchanged)
- [x] Specifications approved (2026-08-23, as part of `vdd-simbox-app-uiux`
      v1.1, before extraction)
- [x] Plan drafted (v1.0, 2026-08-23 — extracted, approved content,
      unchanged, renumbered Tasks 14-18 → 1-5)
- [x] Plan approved (2026-08-23, as part of `vdd-simbox-app-uiux` v1.1,
      before extraction)
- [x] Implementation started (2026-08-23)
- [x] Implementation code complete (2026-08-23) — `dart analyze`/
      `flutter test` clean (18/18); final visual-fidelity sign-off
      gated on the shared font blocker above
- [ ] Documentation drafted
- [ ] Documentation approved

## Context Notes

Key decisions and context for resuming:

- **This flow did not originate as a fresh REQUIREMENTS elicitation**
  — it was extracted whole from `vdd-simbox-app-uiux`, where the
  "Каналы" table/view-mode redesign began as a small clarifying
  question about a toggle's location and grew into a full screen
  redesign (verbatim exchange preserved in `01-requirements.md`'s
  CRITICAL note). Anton then asked (2026-08-23, same session) to move
  everything table-related out of `vdd-simbox-app-uiux` into this new
  flow. All 5 documents here are that content relocated, not
  rewritten — cross-check `vdd-simbox-app-uiux`'s own `_status.md`/docs
  if something here seems to reference missing context, since some
  background (the base screens, the original prototype research) stays
  documented only in the parent flow.
- **Real code is not duplicated or reverted** — the actual
  `apps/simbox-app` source files (e.g. `sims_screen.dart`) contain both
  the base card-view (from `vdd-simbox-app-uiux`) and this flow's
  table/view-mode logic as one coherent implementation. Only the
  *documentation* was split; nothing in the running app changed as
  part of this extraction.
- **Scope correction already baked into the extracted content**: the
  table-view-anywhere toggle was originally planned to also cover
  Модемы, but implementation found that screen has no dense-table
  representation to extend (flat `ListView`, not `DenseModemTable`) —
  scoped down to Каналы only, documented in all three docs
  (`02-visual.md`, `03-specifications.md`, `04-plan.md`) with an
  explicit correction note, not silently dropped.
- **Domain-model terminology settled by this flow, permanent**: "Modem"
  hosts one or more "Channels" (a channel = one call-capable path,
  tied to one SIM, further distinguished by "Line" for multi-line
  modems). "Trunk" is explicitly rejected — it implies a multiplexed
  aggregate facility (like a real E1/PRI trunk), which doesn't map onto
  independent, non-multiplexed GSM channels. Don't reintroduce "Транк"
  into this screen's UI or code without revisiting this decision
  directly with Anton.

## Fork History

Not forked — extracted from `vdd-simbox-app-uiux` (a full-content
relocation of that flow's AC #8 amendment / Tasks 14-18, not a fork of
its whole history). See `vdd-simbox-app-uiux/_status.md` for the
extraction note on that side.

## Next Actions

Nothing left to implement — Tasks 1-5 are done and verified. Optional
follow-ups, not blocking:

1. Resolve the shared font-asset blocker (same action item as
   `vdd-simbox-app-uiux`'s own Next Actions — Anton needs to supply
   valid licensed SF Pro Text TTFs or approve a platform-native
   fallback) before either flow's UI is final-sign-off complete.
2. Once resolved, do this flow's own manual verification pass (both
   view modes, expand/collapse, the Настройки → Интерфейс toggle on
   phone) — per `04-plan.md`'s Testing Strategy, independent of
   `vdd-simbox-app-uiux`'s own Task 13 pass.
3. `sdd-flutter_gsmsip-interface`'s SIM-inventory-independent-of-modem
   addendum — separate flow, whenever picked up, unblocks По-SIM-все's
   "не в модеме" row here without needing a UI rework.
4. A real Модемы dense-table — separate future enhancement, not
   scoped/planned yet.
