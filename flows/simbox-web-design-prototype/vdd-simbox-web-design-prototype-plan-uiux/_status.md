# Status: vdd-simbox-web-design-prototype-plan-uiux

## Current Phase

IMPLEMENTATION

## Phase Status

REVIEW

## Last Updated

2026-09-02 by Claude

## Blockers

- None functional. All code written, `flutter analyze` clean, `flutter build web` succeeds.
  Two manual-verification checklist items (blocked-delete dialog for a referenced non-default
  plan; narrow-width `<900px` layout) were not re-driven live in the browser after a late
  `mock.dart` fix, because the `claude-in-chrome` extension became unstable
  (connect/disconnect) partway through this session's verification pass. Both use code paths
  already verified either earlier in this same pass (the identical delete-dialog code for the
  unreferenced-plan case) or in the already-shipped Zones/Command Sets features (the identical
  `LayoutBuilder`/narrow pattern). Low risk, but not yet re-confirmed live — see
  05-implementation-log.md's Handoff notes for exactly what to re-check.

## Requirements — resolved and approved 2026-09-02

- Seed: 33 active + 8 audit-only (corrected during Implementation from an earlier "37+9" claim
  that didn't survive direct archive verification — see 01-requirements.md's Canonical Initial
  Registry). Deletion: all three rules (protect default / block if
  referenced / confirm if unused). Command-set association: **direct editing allowed** for an
  existing plan (opposite of the doc's original recommendation — Clone stays the *creation*
  path only). Group ownership: **new evidence accepted** — Plan gets no editable group mapping,
  Directions shows read-only route context from the live Zones registry (overturns the
  earlier-approved Command Sets amendment; verified independently against
  `lib/features/zones/models.dart`'s actual shipped `GroupRule` shape, not just the narrative).
  Plus: Explanation Banner (Acceptance Criteria #25-27, dismissible top banner + "?" reopen,
  exact copy recorded verbatim).

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
- [ ] Implementation complete (2 manual-verification items pending — see Blockers)
- [ ] Documentation drafted
- [ ] Documentation approved

## Context Notes

- New flow requested with `$vdd new` for the existing Flutter target
  `design/simbox-web-design-prototype-v2026`.
- Logic source is legacy; visual source is `design/simbox-design-prototype-v2026-dc`.
- A command set has many plans; a plan selects exactly one command set; a SIM selects one plan.
- Archived `plan.list` contains 33 non-separator active IDs across six command sets (default,
  tele2_spb, beeline_spb, megafon_spb, megafon_msk, mts_spb — `rostel_spb` is a real command set
  (shipped in command_sets/seed.dart) but owns zero plans in the legacy archive; an earlier draft
  wrongly attributed plans to it).
- Eight additional `.nabor` IDs are unlisted test/orphan evidence; requirements recommend
  excluding them from the operational seed.
- Legacy exposes roughly 100 stored suffix variants, including aliases and typos. The UI will use
  a finite semantic schema and a development audit instead of raw key/value editing.
- Runtime counters shown by legacy next to capacity limits are outside editable Plan policy.
- Recommended UI direction is responsive registry + single-plan semantic editor, not the legacy
  ultra-wide grid.
- `PRO` is now verified as a routing tag copied from Plan to SIM and compared with the call's tag
  by direction algorithms `P/p/v`; it is not a product tier. The UI must keep it near routing
  policy, with verified examples only.
- The optional comparison idea was rejected as unnecessary and removed from scope.
- Direction routing is now traced through `extensions_dial_zones.conf` into
  `libsCpp/asterisk-chan-svistok/src/select.c`: the route resource encodes slot, modifier,
  limit mode, billing direction and target group; SIM selection first matches current group.
- This conflicts with the earlier approved Command Sets amendment that assigned lifecycle-group
  mapping to Plan. Direct legacy evidence instead splits it across operator config, dialplan and
  SIM runtime. No editable group mapping is added to Plan until the owner resolves this conflict.
- `nativemind-adminka` governs dense operational information and `nativemind-designsystem`
  supplies the existing product tokens. Fugue-specific 16/32 density remains authoritative for
  feature actions.

## Fork History

N/A — new flow. It follows the completed Command Sets workspace but does not fork its documents.

## Next Actions

1. Re-verify live (once `claude-in-chrome` is stable): the blocked-delete dialog for a
   referenced, non-default plan (e.g. `beeline_spb_good`, now used by 1 SIM after this
   session's `mock.dart` fix) shows the correct "недоступно" copy with usage count; and the
   narrow (`<900px`) stacked layout renders correctly.
2. On confirming both, mark Implementation complete and move to the optional DOCUMENTATION
   phase if desired, or close out the flow.

## Addendum (2026-09-02, this session)

Product owner asked for a dismissible explanation banner on the Plans screen, offering to
propose alternatives — presented three options (top banner / title-icon popover / first-visit
modal) via AskUserQuestion; **top banner** chosen. Exact copy (4 paragraphs: purpose, time_wake/
time_sleep semantics, diff_slow/diff_min pause semantics, post-edit "Восстановить параметры
плана" reminder) recorded verbatim in 01-requirements.md's new "Explanation Banner" section, not
paraphrased. Reopens via a "?" affordance near the page title after dismissal; in-memory session
state, no persistence, matching the prototype's existing `navCompact`/`logOpen` convention.
