# Status: vdd-simbox-web-design-prototype-plan-uiux

## Current Phase

REQUIREMENTS

## Phase Status

REVIEW

## Last Updated

2026-09-02 by Codex

## Blockers

- Product-owner answers to the four remaining open requirement decisions, including the newly
  evidenced conflict over lifecycle-group ownership.

## Progress

- [x] Requirements drafted
- [ ] Requirements approved
- [ ] Visual mockups drafted
- [ ] Visual approved
- [ ] Specifications drafted
- [ ] Specifications approved
- [ ] Plan drafted
- [ ] Plan approved
- [ ] Implementation started
- [ ] Implementation complete
- [ ] Documentation drafted
- [ ] Documentation approved

## Context Notes

- New flow requested with `$vdd new` for the existing Flutter target
  `design/simbox-web-design-prototype-v2026`.
- Logic source is legacy; visual source is `design/simbox-design-prototype-v2026-dc`.
- A command set has many plans; a plan selects exactly one command set; a SIM selects one plan.
- Archived `plan.list` contains 37 non-separator active IDs across seven command sets.
- Nine additional `.nabor` IDs are unlisted test/orphan evidence and one dashed ID is a separator
  artifact; requirements recommend excluding them from the operational seed.
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

1. Resolve the four remaining open requirement decisions.
2. Record explicit `requirements approved` before drafting ASCII visual states.
