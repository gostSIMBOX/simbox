# Implementation Plan: Command Sets Editor UI/UX

> Version: 2.0  
> Status: REVIEW  
> Last Updated: 2026-09-01  
> Specifications: [03-specifications.md](03-specifications.md)

## Delivery Strategy

Build the feature depth-first from a validated structured domain to the visible workspace. Each
stage leaves a compilable/testable increment. Legacy parsing is used only to prove coverage; no
Shell/PHP source becomes product data or UI.

Implementation target:
`design/simbox-web-design-prototype-v2026`

Protected existing work:

- preserve modified `.dart_tool/package_graph.json`;
- preserve modified `build/**` outputs and do not treat them as source;
- preserve all unrelated user changes in the nested repository;
- do not modify `legacy/simbox-desktop-v2014`.

## Dependency Order

```text
Models + validation
        |
        +--> Legacy coverage map --> Structured seed --> Repository
        |                                      |
        +--> Response preview engine ----------+--> Controller
        |                                              |
Fugue pairs + tokens + wrapper ------------------------+--> Workspace UI
                                                       |
                                          AppState / Sims / Sidebar integration
                                                       |
                                       Responsive + accessibility + visual QA
```

## Task Breakdown

### 0. Establish the baseline

Complexity: **S**  
Dependencies: none

- [ ] Record the nested repository status without reverting generated/user-owned changes.
- [ ] Run the existing `flutter analyze` and `flutter test` baseline from the target project.
- [ ] If no tests exist, record that fact rather than fabricating a passing test baseline.
- [ ] Log baseline warnings/failures in `05-implementation-log.md` before changing source.

Exit criteria: current health and pre-existing dirty files are documented.

### 1. Add immutable domain models and pure validation

Complexity: **L**  
Dependencies: Task 0

Files:

- `lib/features/command_sets/models.dart`
- `lib/features/command_sets/validation.dart`
- `test/command_set_models_test.dart`

Steps:

- [ ] Add `CommandSet`, metadata, purpose, parameter and section models.
- [ ] Add sealed operations for USSD dialog, SMS, call and AT.
- [ ] Add response matcher/effect/outcome models, including multiple effects per rule.
- [ ] Add immutable `copyWith`, value equality and derived command/rule counts.
- [ ] Implement pure validation for IDs, templates, USSD Start/Reply order, transition fallback,
  regex/captures, duplicate response destinations and required effects/outcome.
- [ ] Add focused tests one behavior at a time, including PIN as a secret invocation parameter,
  minutes+SMS in one response and absence of group/limit/migration fields.

Exit criteria: models and validation are UI-independent and all focused tests pass.

### 2. Build the development-only legacy coverage audit

Complexity: **L**  
Dependencies: Task 1

Files:

- `tool/command_set_legacy_audit.dart`
- `tool/verify_command_set_seed.dart`
- `test/fixtures/command_set_legacy_coverage.dart`
- `test/command_set_seed_test.dart`

Steps:

- [ ] Inventory the exact legacy `nabor` tree by relative path and SHA-256.
- [ ] Assign exactly one disposition to every one of the 204 audited files.
- [ ] Map active command/parser evidence to stable structured target IDs.
- [ ] Map `GROUP_*`, daily limits, counters and resets to Plan/SIM/scheduler ownership.
- [ ] Map `old/`, test, commented, duplicate and inactive helpers to audit-only evidence.
- [ ] Fold active Kyivstar helper behavior into its parent command target.
- [ ] Make verification fail on missing/extra paths, duplicate disposition, unknown target,
  checksum drift or any production import of audit-only data.

Exit criteria: every legacy path is accounted for without exposing audit state in product models.

### 3. Author and validate the ten structured seed sets

Complexity: **XL**  
Dependencies: Tasks 1–2

Files:

- `lib/features/command_sets/seed.dart`
- `test/command_set_seed_test.dart`

Implementation slices:

- [ ] Add protected empty `default` and registry order contract.
- [ ] Add `megafon_msk` and `megafon_spb`, preserving regional separation and interactive USSD
  sequences such as Start `*105*0082#` → Reply `1` with optional 7-second fallback.
- [ ] Add `beeline_spb` and distinguish active operator commands from daily-policy leakage.
- [ ] Add `mts_spb`, merging only equivalent evidence and retaining distinct active behaviors.
- [ ] Add `tele2_spb`, with Enter PIN represented by `{{pin}}` and service-specific operations.
- [ ] Add `rostel_spb` with queries for promise payment, minutes, options and tariff where active.
- [ ] Add `kievstar`, folding its active fork/helper chain into semantic operations.
- [ ] Add `velcom` and `life`, importing only active protocol behavior while auditing inactive MON
  or fork artifacts outside the UI.
- [ ] Add response rules for all active parser behavior, allowing combined minutes/SMS effects.
- [ ] Keep MAY/MON stable labels and identifiers without inventing unverified billing meaning.
- [ ] Validate every set and cross-check every audit target after each operator slice.

Exit criteria: exact ten records load; all structured items validate; every active audit target
resolves; no legacy source text or migration status is product data.

### 4. Implement repository and response-preview engine

Complexity: **M**  
Dependencies: Tasks 1 and 3

Files:

- `lib/features/command_sets/repository.dart`
- `lib/features/command_sets/response_preview.dart`
- `test/command_set_repository_test.dart`
- `test/response_preview_test.dart`

Steps:

- [ ] Create immutable seed/reset snapshot and mutable in-memory session snapshot.
- [ ] Implement create/replace/delete/reset with invariant checks and typed errors.
- [ ] Implement contains, starts-with and Dart-regex matching.
- [ ] Implement the finite normalization pipeline and multi-effect preview.
- [ ] Guarantee tester purity: no AppState, repository, modem or filesystem mutation.
- [ ] Test no-match, invalid capture, conversion errors, multiple effects and semantic outcomes.

Exit criteria: repository mutations are atomic and preview results are deterministic and pure.

### 5. Implement CommandSetController and draft lifecycle

Complexity: **L**  
Dependencies: Task 4

Files:

- `lib/features/command_sets/controller.dart`
- `test/command_set_controller_test.dart`

Steps:

- [ ] Add load/selection, Commands-default section selection and per-set section memory.
- [ ] Add registry/command/rule search and channel filtering.
- [ ] Add set-level draft, metadata updates and atomic Save/Cancel.
- [ ] Add command, operation, USSD reply and response-rule CRUD/reordering.
- [ ] Add Blank/Clone creation and immutable stable-ID validation.
- [ ] Add default/Plan-reference deletion impact and confirmed deletion.
- [ ] Add dirty selection/navigation/reset guard state.
- [ ] Add typed success/error results consumable by inline UI and snackbars.

Exit criteria: all specified controller flows pass without Flutter widget dependencies.

### 6. Vendor the verified Fugue density pairs and wrapper

Complexity: **M**  
Dependencies: Task 0; parallel-safe with Tasks 1–5

Files:

- `assets/fugue/*.png`
- `assets/fugue/2.0x/*.png`
- `lib/widgets/fugue_icon.dart`
- `lib/design/tokens.dart`
- `pubspec.yaml`
- `test/fugue_icon_test.dart`

Steps:

- [ ] Copy only the approved 25 semantic glyphs, preserving upstream filenames.
- [ ] Copy every original 16×16 and matching 32×32 `2.0x` pair.
- [ ] Register the asset directory; do not vendor the full catalog or any 48px asset.
- [ ] Add `FugueIcon` with a fixed 16 logical-pixel box and semantic/tooltip support.
- [ ] Add icon-relative typography, spacing, padding, row and hit-target tokens.
- [ ] Test asset presence, paired filenames and logical size at 1×/2× device-pixel ratios.

Exit criteria: all feature glyphs resolve at both densities with identical logical geometry.

### 7. Build registry, persistent header and responsive workspace shell

Complexity: **L**  
Dependencies: Tasks 5–6

Files:

- `lib/features/command_sets/workspace.dart`
- `lib/features/command_sets/registry_pane.dart`
- `lib/features/command_sets/detail_header.dart`
- `lib/pages/nabor_page.dart`
- `test/nabor_page_test.dart`

Steps:

- [ ] Replace the old 520px decorative list with the desktop master-detail shell.
- [ ] Add all ten registry records, query, counts, selection, Add and Reset overflow.
- [ ] Add compact set selector below 900px.
- [ ] Add persistent name/ID/operator/country/region/Plan-usage header.
- [ ] Add Edit/Clone/Delete actions and protected System fallback treatment.
- [ ] Add exactly Commands and Response rules controls, with Commands default.
- [ ] Add loading, seed error, no-selection, registry-empty and default empty states.
- [ ] Assert there is no Overview, Groups, limits, migration badge/filter or technical file count.

Exit criteria: shell and states match the approved visual structure at desktop and narrow widths.

### 8. Build Commands editor

Complexity: **XL**  
Dependencies: Task 7

Files:

- `lib/features/command_sets/commands_section.dart`
- `lib/features/command_sets/command_operation_card.dart`
- `lib/features/command_sets/ussd_dialog_editor.dart`
- `test/commands_section_test.dart`

Steps:

- [ ] Add searchable command selector and finite Add command purpose menu.
- [ ] Add operator-specific service with safe ID/name but no raw-code field.
- [ ] Add enable, duplicate, delete and accessible reorder actions.
- [ ] Add operation cards for USSD, SMS, call and AT with type-specific fields.
- [ ] Add USSD Start/Reply editing, Add reply and optional Fallback after `1..300` seconds.
- [ ] Keep Start fixed first while allowing reply/operation reordering.
- [ ] Add typed command-parameter editor and masked PIN sample field.
- [ ] Show protocol literals in mono and local actionable validation at the affected field.
- [ ] Confirm there is no Execute/Test button or fabricated runtime response state.

Exit criteria: a Blank set can build and save every supported operation without exposing code.

### 9. Build Response rules editor and sample tester

Complexity: **XL**  
Dependencies: Tasks 5 and 7

Files:

- `lib/features/command_sets/response_rules_section.dart`
- `lib/features/command_sets/response_rule_card.dart`
- `lib/features/command_sets/response_tester.dart`
- `test/response_rules_section_test.dart`

Steps:

- [ ] Add search, channel filter, Add, enable, duplicate, delete and accessible reorder.
- [ ] Add collapsed WHEN/TAKE/SAVE-or-EMIT summaries.
- [ ] Add contains/starts-with matching and Advanced regex/case/capture controls.
- [ ] Add one-or-more typed effects and optional semantic outcome.
- [ ] Permit remaining minutes and remaining SMS as separate effects in the same rule.
- [ ] Add sample payload, matched-fragment and normalized No writes preview.
- [ ] Add no-match and per-effect conversion error states.
- [ ] Confirm no numeric group or Plan quota appears in rule inputs.

Exit criteria: rules can be authored, reordered, validated and previewed without state writes.

### 10. Add create/edit/delete and dirty-guard dialogs

Complexity: **M**  
Dependencies: Tasks 7–9

Files:

- `lib/features/command_sets/set_dialogs.dart`
- `test/command_set_dialogs_test.dart`

Steps:

- [ ] Add metadata dialog/drawer that updates the current set draft.
- [ ] Add Clone-first/Blank-second creation flow with identity validation.
- [ ] Add inline blocked-delete impact for default and Plan-referenced sets.
- [ ] Add explicit confirmation only for an executable unreferenced delete.
- [ ] Add Keep editing/Discard guard for selection, navigation and Reset.
- [ ] Restore focus to invoking controls after closing each flow.

Exit criteria: all destructive and draft-loss paths are explicit and keyboard usable.

### 11. Integrate AppState, SimsPage, Plan usage and sidebar

Complexity: **M**  
Dependencies: Tasks 5–10

Files:

- `lib/state/app_state.dart`
- `lib/data/mock.dart`
- `lib/pages/sims_page.dart`
- `lib/widgets/sidebar.dart`
- `lib/main.dart`
- relevant integration tests

Steps:

- [ ] Let AppState own, forward and dispose one CommandSetController.
- [ ] Give the feature dirty-state guard first handling of Escape and Ctrl/Cmd+S while active;
  preserve existing action-rail Escape behavior otherwise.
- [ ] Correct every `megafon_mks` sample reference to `megafon_msk`.
- [ ] Remove `naborNames`/`naborIcons` as live authority.
- [ ] Populate SimsPage set selection from live controller IDs.
- [ ] Derive Plan usage from current sample Plan rows and expose the usage list from the header.
- [ ] Replace the Command Sets route glyph with approved Fugue `application-list.png`.
- [ ] Verify unrelated routes remain behaviorally unchanged.

Exit criteria: CRUD updates dependent selectors safely and existing shell behavior is preserved.

### 12. Responsive, accessibility and visual QA pass

Complexity: **L**  
Dependencies: Tasks 7–11

- [ ] Verify desktop, approximately 900px and below-560px layouts without page overflow.
- [ ] Verify sticky header and dirty bar do not obscure editor content or CommandLog.
- [ ] Verify 32px desktop and 40px narrow targets while glyphs remain 16 logical px.
- [ ] Add tooltips, semantic labels, visible focus and Move up/down reorder alternatives.
- [ ] Verify validation never relies on color and every error is actionable.
- [ ] Verify SF Pro Text for UI and mono only for protocol/pattern/sample literals.
- [ ] Capture browser screenshots at 1× and 2× DPR and compare geometry/asset selection.
- [ ] Remove no debug overflow, placeholder status, emoji or non-Fugue feature glyphs.

Exit criteria: all approved happy, empty, error and responsive states have visual evidence.

### 13. Final verification and handoff

Complexity: **M**  
Dependencies: all tasks

- [ ] Run `dart run tool/verify_command_set_seed.dart`.
- [ ] Run focused tests one at a time while fixing failures, then full `flutter test`.
- [ ] Run `flutter analyze`.
- [ ] Run `flutter build web`.
- [ ] Run `git diff --check` in the relevant repository/workspace.
- [ ] Confirm no raw legacy source assets, migration UI, Overview, Groups/limits or 48px icons.
- [ ] Record changed files, commands, results, deviations and screenshot paths in
  `05-implementation-log.md`.
- [ ] Update `_status.md` only when implementation and visual verification are genuinely complete.

Exit criteria: all verification passes or any pre-existing/environmental exception is explicitly
evidenced in the implementation log.

## Complexity Summary

| Area | Complexity | Main risk |
|---|---|---|
| Domain/validation | L | Keeping the finite model expressive without becoming a DSL |
| Legacy audit and seed | XL | Accounting for every artifact while importing only active behavior |
| Repository/controller | L | Atomic drafts and safe cross-route selection |
| Fugue/density assets | M | Pair completeness and logical-vs-physical sizing |
| Workspace shell | L | Stable two-pane/narrow layout with persistent header |
| Commands editor | XL | USSD sequence UX and nested validation |
| Response rules | XL | Multi-effect extraction and understandable preview |
| Integration/QA | L | Preserving existing shell and dirty generated worktree |

## Approval Gate

- [x] Reviewed by: Anton Dodonov
- [x] Approved on: 2026-09-01
- [x] Notes: approved with `approved`; implementation may proceed.
