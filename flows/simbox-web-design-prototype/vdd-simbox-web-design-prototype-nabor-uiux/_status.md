# Status: vdd-simbox-web-design-prototype-nabor-uiux

## Current Phase

IMPLEMENTATION

## Phase Status

READY FOR VISUAL REVIEW

## Last Updated

2026-09-01 by Codex

## Blockers

- None.

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
- [ ] Documentation drafted
- [ ] Documentation approved

## Context Notes

- Logic source: `legacy/simbox-desktop-v2014`, especially `www/simbox`, `nabor/` and plan
  assignment behavior.
- Visual source: `design/simbox-design-prototype-v2026-dc`.
- Target corrected by the user to the existing nested Flutter project
  `design/simbox-web-design-prototype-v2026`; the earlier path without `-web-` is superseded.
- Legacy registry contains ten IDs: one logical fallback (`default`) and nine physical packages.
- Physical audit found 82 command files and 51 parser files. Ambiguous/historical artifacts are
  preserved and labelled rather than silently discarded.
- The initial master-detail proposal with Overview, Commands, Parsers and Groups was superseded;
  the approved workspace has a persistent metadata header plus Commands and Response rules.
- Requirements approved by the user with `reqs approved`; all proposed defaults were accepted.
- The initial file-list/source-editor draft was superseded by semantic command sequences and typed
  response-rule cards. The persistent desktop registry and compact selector below 900px remain.
- NativeMind design-system rules used: single blue gradient CTA, SF Pro Text, 4px grid, 10px
  surface radius and one soft shadow. Adminka density rules shape the registry and status rows.
- Updated Fugue density rule applied: 16×16 at 1× and 32×32 at 2× in the same 16px logical box;
  no 48px tier, with surrounding metrics derived from the same icon unit.
- Visual approved by the user with `approved` before the corrected target invocation.
- Target audit: current `NaborPage` has only 8 guessed rows; `mock.dart` contains
  `megafon_mks`; `SimsPage` consumes the same incomplete constant. Specifications replace that
  authority with a typed feature controller owned by `AppState`.
- The earlier proposal to bundle the 204-file legacy tree is superseded. Specification 2.0 uses a
  typed structured seed in the product and a development-only path/checksum/target coverage audit.
- Full Fugue catalog discovery and visual inspection resolved every feature glyph; 27 unique
  filenames have verified 16×16/32×32 pairs, so no wishlist item is needed.
- User rejected Shell/PHP source editing. Requirement and visual Amendment 1.1 replace it with a
  finite legacy-derived command workflow builder and typed response rules with a sample tester.
- The prior requirements/visual approvals remain historical and their source-editor clauses are
  superseded; consolidated Amendments 1.1–1.6 have since been approved.
- Domain-owner clarification: sleeps between USSD requests were legacy workarounds for missing
  response handling. Amendment 1.2 models these commands as logical USSD Start/Reply sequences
  and explicitly defers runtime session correlation, timing, retry and failure behavior.
- Scoped audit confirms Plan owns configured call/SMS/MAY/MON/MSM limits, SIM runtime owns current
  counters, and cron owns daily reset execution. Amendment 1.3 removes limits/counters from
  Command Sets and retains a legacy duration only as optional response-transition failover.
- `GROUP_*` values are declared per legacy nabor but unused symbolically; active code hardcodes
  numeric groups. Amendment 1.4 removes Groups from Command Sets: response rules emit semantic
  outcomes, Plan maps outcomes to groups, and SIM owns current/manual group state.
- Information-architecture review found that Overview only duplicated the selected-set identity,
  Plan usage and migration state. Amendment 1.5 moves those values into a persistent detail
  header and leaves only Commands and Response rules as primary sections.
- Migration state was identified as import-audit metadata rather than a command-set business
  property. Amendment 1.6 removes it from the operational UI; unresolved legacy coverage remains
  in technical documentation and editable defects use normal actionable validation.
- User approved the consolidated Requirement and Visual Amendments 1.1–1.6 on 2026-09-01.
- Specification 2.0 now replaces the obsolete file/source-editor architecture with structured
  command operations, USSD Start/Reply sequences, multi-effect response rules and a persistent
  two-section workspace. Legacy completeness is enforced by a development-only coverage audit,
  not by runtime source assets or migration UI.
- Revised Fugue contract uses subject-specific glyphs for USSD, SMS, calls, AT, matching and
  sample testing. Every selected filename was verified at 16×16 and 32×32; the UI box remains
  16 logical pixels on both density tiers.
- User approved Specification 2.0 on 2026-09-01. Implementation Plan 2.0 is drafted in dependency
  order with explicit legacy-audit, per-operator seed, UI, integration and verification gates.
- User approved Implementation Plan 2.0 on 2026-09-01; implementation has started.
- Implementation now contains the semantic two-section editor, all ten sets, complete legacy
  path/content audit, Fugue density pairs and responsive test coverage. The web build is ready for
  review. Browser screenshot capture remains unavailable because this session exposes no browser.

## Fork History

N/A — new flow. It builds on earlier admin-prototype analysis without modifying those flows.

## Next Actions

1. Review the built Commands and Response rules workspace visually.
2. After visual acceptance, draft the final VDD documentation/handoff.
