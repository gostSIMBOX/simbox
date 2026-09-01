# Specifications: Command Sets Editor UI/UX

> Version: 2.0  
> Status: REVIEW  
> Last Updated: 2026-09-01  
> Requirements: [01-requirements.md](01-requirements.md)  
> Visual: [02-visual.md](02-visual.md)

## Outcome

Replace the read-only `NaborPage` with a local, fully interactive editor for regional operator
command sets. The product model is structured and finite: operator commands are protocol
operations, and parsers become typed response rules. The UI never exposes Shell/PHP, legacy
filenames, numeric groups, Plan limits or migration state.

The approved information architecture is one persistent set registry, one persistent selected-set
header and exactly two working sections:

1. **Commands** — structured operator actions and USSD dialogs;
2. **Response rules** — response matching, extraction, normalization and typed results.

Requirements and Visual Amendments 1.1–1.6 are authoritative. Any earlier source-editor,
Overview, Groups, limits or migration-status proposal is superseded and must not be implemented.

## Audited Target Baseline

| Existing target area | Current behavior | Required change |
|---|---|---|
| `lib/pages/nabor_page.dart` | Stateless 520px card with 8 guessed rows | Replace with responsive command-set workspace |
| `lib/data/mock.dart` | Incomplete `naborNames`; typo `megafon_mks` | Remove as authority; correct all sample references to `megafon_msk` |
| `lib/pages/sims_page.dart` | Set selector reads the incomplete constant | Read live selectable IDs from the controller |
| `lib/data/mock.dart::planRows` | Three sample Plan-to-set references | Use as delete/usage impact references |
| `lib/state/app_state.dart` | No command-set domain | Own and forward one feature controller |
| `lib/widgets/adm_icon.dart` | Original GostSimBox glyphs only | Keep existing surfaces; add a Fugue-only wrapper for this feature |
| `lib/design/tokens.dart` | NativeMind base and dense-table tokens | Add icon-relative command-editor tokens |
| `pubspec.yaml` | No Fugue assets | Register only selected 16×16/32×32 Fugue pairs |

The target is the nested Flutter project at `design/simbox-web-design-prototype-v2026`. Generated
`.dart_tool/` and `build/` content is not source and must not be edited or reverted.

## Domain Ownership

| Concern | Owner in the redesigned system | Command Sets behavior |
|---|---|---|
| Operator request sequence | Command Set | Edit as structured command operations |
| Recognition and extraction from replies | Command Set | Edit as response rules |
| Semantic result (`lowBalance`, `blocked`, `workReady`) | Command Set | Emit from a response rule |
| Mapping semantic result to numeric group | Plan | Show no numeric group input |
| Plan limits and MAY/MON/MSM/SMS quotas | Plan | Show no policy input |
| Current counters and current numeric group | SIM runtime | Show no runtime editor |
| Manual Set group | SIM action | Remains on SIM operational screens |
| Daily reset execution | Scheduler/system maintenance | Not a command-set command |
| Legacy import coverage | Development audit | Never a product status or filter |

Measured operator allowances are response data, not Plan policy. `remainingMinutes` and
`remainingSms` are separate typed fields. One operator reply may populate either one or both by
containing multiple response effects in one rule.

## Structured Seed Contract

### Registry

The initial repository contains the exact legacy order:

1. `default`
2. `megafon_msk`
3. `megafon_spb`
4. `beeline_spb`
5. `mts_spb`
6. `tele2_spb`
7. `rostel_spb`
8. `kievstar`
9. `velcom`
10. `life`

`default` is a protected logical fallback, not a physical package. It has no invented commands or
response rules. Its empty states explain that it is used when a Plan has no specific set.

Each physical record has explicit operator, ISO country code, country label and optional region.
Region is never inferred at render time from an ID. Moscow and Saint Petersburg MegaFon sets
remain separate records.

### User-facing command catalog

The seed normalizes active legacy behavior into stable purposes without exposing filenames:

| Stable purpose | Default display meaning | Notes |
|---|---|---|
| `activate_sim` | Activate SIM | Legacy name retained; does not itself imply a group change |
| `activate_work` | Activate work | Separate operator service action; no automatic Plan/SIM transition |
| `get_balance` | Get balance | Usually a one-step USSD request |
| `get_number` | Get phone number | May be an interactive USSD dialog |
| `get_tariff` | Get tariff | Operator tariff/service query |
| `get_minutes` | Get remaining minutes | Response writes measured allowance |
| `get_options` | Get active options | May emit several extracted option values |
| `get_promise_payment` | Get promise-payment information | Normalizes legacy `get_dover` behavior |
| `initialize_tariff` | Initialize tariff | Included only where active legacy behavior exists |
| `send_may` | MAY request | Keeps the legacy term; requires destination-number parameter |
| `send_mon` | MON request | Keeps the legacy term; does not invent billing semantics |
| `enter_pin` | Enter SIM PIN | Tele2 legacy case only; PIN is an invocation parameter, not set metadata |
| `disable_service` | Disable operator service | Seeded with its specific service description, e.g. Tele2 service 209 |
| `operator_service` | Operator-specific service | User-named extension using the same finite protocol operations |

`activate_sim` and `activate_work` remain separate because legacy calls them separately, but the
prototype assigns no unverified lifecycle semantics to either. MAY and MON similarly keep their
stable names until the domain supplies authoritative public descriptions.

Multiple commands may share a purpose when the legacy set contains genuinely distinct active
variants. Every command therefore has its own immutable `id` plus a `purpose` and display name.

### Legacy coverage audit

Raw legacy files are not bundled into the operational application. A development-only audit map
accounts for the exact 204-file legacy tree and records one disposition per relative path:

- folded into a structured command;
- folded into one or more response rules;
- Plan-owned policy evidence;
- SIM-runtime evidence;
- scheduler/maintenance evidence;
- historical, test, fork or inactive evidence;
- package metadata.

The audit retains source path, SHA-256 and structured target IDs. It has no product model,
product route, badge, filter or details drawer. `tool/verify_command_set_seed.dart` fails if a
legacy path is missing, duplicated, silently ignored or points at an unknown structured target.

Known helper behavior such as Kyivstar `activate_sim_fork` is folded into its parent structured
command rather than shown as another user command. `setdaylimit*`, daily resets, hardcoded group
numbers and counters are accounted for under their redesigned owners, not imported into the
command builder. Comment-only, test and `old/` artifacts remain audit evidence only.

User-facing counts are derived from structured commands and rules. They are never the legacy
file counts of 82 command files and 51 parser files.

## Data Model

```dart
enum CommandSetKind { systemFallback, operator }
enum CommandSetSection { commands, responseRules }

class CommandSet {
  final String id;                 // immutable stable ID
  final String name;
  final String operatorName;
  final String countryCode;        // ISO 3166-1 alpha-2
  final String countryName;
  final String? region;
  final CommandSetKind kind;
  final List<OperatorCommand> commands;
  final List<ResponseRule> responseRules;
  final List<String> usedByPlanIds;
}

enum CommandPurpose {
  activateSim, activateWork, getBalance, getNumber, getTariff,
  getMinutes, getOptions, getPromisePayment, initializeTariff,
  sendMay, sendMon, enterPin, disableService, operatorService,
}

class OperatorCommand {
  final String id;                 // safe immutable key inside the set
  final CommandPurpose purpose;
  final String name;
  final String? description;
  final bool enabled;
  final List<CommandParameter> parameters;
  final List<CommandOperation> operations;
}

enum ParameterType { phoneNumber, pin, text, integer, decimal }

class CommandParameter {
  final String key;
  final String label;
  final ParameterType type;
  final bool required;
  final bool secret;
}
```

PIN is present only when a command declares a `pin` parameter. The editor masks its sample value,
does not put a PIN into set metadata and does not persist an invocation value in the prototype.
The imported Tele2 operation uses `{{pin}}`, not the legacy hardcoded `0000` as canonical data.

### Command operations

The builder supports a finite union. It has no Shell, PHP, arbitrary expression or generic code
operation.

```dart
sealed class CommandOperation {
  final String id;
}

class UssdDialogOperation extends CommandOperation {
  final UssdStep start;
  final List<UssdReplyStep> replies;
}

class UssdStep {
  final String payloadTemplate;
  final String queueClass;         // audited transport class such as LOC/LO2
}

class UssdReplyStep {
  final String payloadTemplate;
  final int? fallbackAfterSeconds; // response-first transition fallback
}

class SendSmsOperation extends CommandOperation {
  final String destinationTemplate;
  final String messageTemplate;
  final String queueClass;
}

class PlaceCallOperation extends CommandOperation {
  final String numberTemplate;
  final String callProfile;
}

class SendAtOperation extends CommandOperation {
  final String commandTemplate;
}
```

One command may contain several operations, which covers verified workflows combining USSD and
SMS without adding a visual programming language. Operations and USSD replies can be reordered;
the USSD Start item always remains first within its dialog.

The preferred transition between USSD steps is an operator response. `fallbackAfterSeconds` is
optional transition metadata. There is no standalone Wait step and no canonical
`*105*0082#WWWWWWW1` string. Runtime correlation, timeout, retry, failover execution and compact
transport compilation remain deferred.

Templates accept literal text plus declared `{{parameterKey}}` references only. Device context
(dongle, SIM and IMSI) is supplied implicitly by a future executor and is not freely templated.
Unknown references, empty payloads, a reply without Start, invalid phone parameters and fallback
durations outside `1..300` are save-blocking field errors.

### Response rules

```dart
enum ResponseChannel { ussd, sms, callResult }
enum MatchMode { contains, startsWith, regularExpression }
enum ValueSource { fullMatch, capture, fixedValue }
enum Normalizer {
  trim, decimalNumber, integerNumber, digitsOnly,
  phoneWithCountryCode, dateTime, plainText,
}
enum ResponseField {
  balance, phoneNumber, tariff, remainingMinutes, remainingSms,
  options, promisePaymentAmount, promisePaymentState, promisePaymentDate,
}
enum SemanticOutcome {
  reservePreparation, reserveReady, workPreparation, workReady,
  workNeedsIncoming, stopped, lowBalance, blocked,
}

class ResponseRule {
  final String id;
  final String name;
  final bool enabled;
  final int priority;
  final ResponseChannel channel;
  final ResponseMatcher matcher;
  final List<ResponseEffect> effects;
  final SemanticOutcome? outcome;
}

class ResponseMatcher {
  final MatchMode mode;
  final String pattern;
  final bool caseSensitive;
}

class ResponseEffect {
  final ResponseField field;
  final ValueSource source;
  final String? captureNameOrIndex;
  final String? fixedValue;
  final List<Normalizer> normalizers;
}
```

A rule can save multiple effects, so one response can populate remaining minutes and SMS
together. Separate rules can populate them from separate operator replies. An outcome is semantic
only; no numeric group is stored in a command set.

Regular expressions are available under Advanced match. The prototype compiles the expression,
checks referenced captures and runs a pure sample preview. Preview output lists matched text,
each normalized field and the semantic outcome. It performs no modem request and no state write.

Normalizers execute in list order but come from the finite enum. No arithmetic expression,
embedded PHP or script callback is accepted.

### Drafts and session repository

```dart
class CommandSetDraft {
  final CommandSet baseline;
  final CommandSet working;
  bool get isDirty => working != baseline;
}

abstract interface class CommandSetRepository {
  List<CommandSet> get records;
  CommandSet? byId(String id);
  void create(CommandSet record);
  void replace(String id, CommandSet record);
  void delete(String id);
  void reset();
}
```

The repository initializes from typed `seed.dart`, keeps an immutable reset snapshot and mutates
only an in-memory session copy. Save survives route navigation but browser refresh and Reset demo
restore the seed. No legacy file, server or modem is touched.

One selected set has at most one set-level draft. Metadata, commands and rules commit atomically.
Cancel restores the baseline. Selection, route navigation and Reset with a dirty draft require
Keep editing or Discard changes; nothing is silently lost.

## Controller Contract

```dart
class CommandSetController extends ChangeNotifier {
  CommandSetLoadState loadState;
  String? selectedId;
  CommandSetSection section;
  String setQuery;
  String commandQuery;
  String ruleQuery;
  CommandSetDraft? draft;

  List<CommandSet> get visibleSets;
  CommandSet? get selected;
  List<String> get selectableIds;

  void selectSet(String id);                  // Commands by default
  void selectSection(CommandSetSection value);
  void beginMetadataEdit();
  void updateMetadata(CommandSetMetadata value);
  void addCommand(CommandPurpose purpose);
  void updateCommand(OperatorCommand value);
  void duplicateCommand(String commandId);
  void deleteCommand(String commandId);
  void reorderCommand(int from, int to);
  void addRule();
  void updateRule(ResponseRule value);
  void duplicateRule(String ruleId);
  void deleteRule(String ruleId);
  void reorderRule(int from, int to);
  ResponsePreview testRule(String ruleId, String sample);
  ValidationResult save();
  void cancelDraft();
  void createBlank(CommandSetMetadata metadata);
  void cloneSet(String sourceId, CommandSetMetadata metadata);
  DeleteImpact inspectDelete(String id);
  void confirmDelete(String id);
  void resetDemo();
}
```

Selecting a different set opens Commands. The controller may remember the last section per set
within the session, but first selection always opens Commands. Counts, filtering and Plan usage
are derived values.

`AppState` owns one controller, forwards its notifications and disposes it. Existing consumers
that only need set IDs use `AppState.commandSets.selectableIds`; widgets do not reach into the
repository.

## Validation and CRUD

### Metadata

| Field | Rule |
|---|---|
| Stable ID | `^[a-z0-9]+(?:_[a-z0-9]+)*$`, unique, 1–64; immutable after create |
| Name | Trimmed, required, max 100 |
| Operator | Trimmed, required, max 80 |
| Country | ISO code and display name required |
| Region | Optional, max 80; empty displays Not specified |

Metadata Edit opens a compact dialog/drawer from the persistent header. Submitting it updates the
set draft; the workspace Save/Cancel still owns the final commit.

### Commands and rules

- IDs are unique inside their collection and immutable after create.
- A command requires a name and at least one valid operation.
- An operator-service command requires a user-facing name; built-in purposes receive editable
  seeded names.
- A USSD dialog requires Start; every payload is non-empty; replies follow Start.
- Every template reference must name a declared parameter of a compatible type.
- A response rule requires a name, non-empty match pattern and at least one effect or outcome.
- Regex syntax and capture references validate before Save.
- Two effects in one rule cannot write the same field.
- Priority is the visible rule order and is normalized after reorder.

Errors attach to the exact field/card and explain a correction. There is no `Needs migration`
label. Invalid Save keeps the draft, focuses the first error and does not mutate the repository.

### Create, clone and delete

- Add set offers Clone existing first and Blank second.
- Clone deep-copies commands and rules, clears usage, and requires a new ID/name/region review.
- Blank creates an empty operator set with honest Commands and Response rules empty states.
- `default` metadata and delete are protected; Clone is allowed.
- A set referenced by any Plan cannot be deleted. The blocking view lists Plan IDs.
- An unreferenced non-system set requires an explicit final confirmation.
- Deleting a set selects the next registry record, or the previous one if it was last.
- Reset restores all ten seed records and removes user-created session records.

There are no file dependency checks because files and Run another script are not product
entities. The finite command model contains no cross-command invocation in this iteration.

## UI Composition

```text
NaborPage
└── CommandSetsWorkspace
    ├── desktop >= 900: Row
    │   ├── CommandSetRegistryPane
    │   └── CommandSetDetailPane
    └── narrow < 900: Column
        ├── CompactCommandSetSelector
        └── CommandSetDetailPane

CommandSetDetailPane
├── PersistentCommandSetHeader
├── Commands | Response rules segmented sections
├── CommandsSection
│   ├── command selector/search/add
│   └── operation cards / UssdDialogEditor
├── ResponseRulesSection
│   ├── rule list/search/channel filter/add
│   ├── WHEN / TAKE / SAVE cards
│   └── SampleResponseTester
└── DirtyDraftBar (Cancel, Save)
```

### Registry and persistent header

- Registry preferred width is 320px, minimum 288px; detail takes the remainder.
- Each row shows set name, stable ID, operator/region and derived command/rule counts.
- Registry has Search, Add set and Reset demo in overflow. It has no migration/status filter.
- Header first line shows name plus Edit and More; second line shows stable ID, country/region and
  Plan usage.
- The `default` header shows a lock plus System fallback. This is a domain kind, not migration
  status.
- The header remains fixed when Commands/Response rules switch and while their contents scroll.
- Plan usage opens a compact list of referencing Plans; it does not add Plan policy controls.

### Commands

- Commands section opens by default.
- A searchable command selector avoids a third nested permanent pane.
- Add command opens the purpose catalog; Operator-specific service is the finite escape hatch for
  a regional action, not a script editor.
- Operations are compact disclosure cards with Fugue icon, semantic summary, drag handle and More.
- USSD dialog Start/Reply nodes remain visually connected. Each reply transition may disclose
  optional Fallback after seconds.
- Literal protocol values and templates use the mono style; labels and descriptions do not.
- The prototype can edit sample invocation parameters for validation but has no Execute/Test
  command button.

### Response rules

- Each collapsed card shows WHEN, TAKE and SAVE/EMIT summaries.
- Reorder controls priority; disabled rules remain visible.
- Advanced match discloses regex, case sensitivity and capture mapping.
- Test response accepts pasted sample text and shows a pure preview labelled No writes.
- The rule list supports search and channel filter; empty filtering offers Clear filters.

### Responsive behavior

- Page padding: 22px desktop, 12px narrow; pane gap: 16px.
- Below 900px, registry becomes an anchored compact selector above detail.
- Below 560px, header secondary metadata collapses behind Information; Edit/More stay on the title
  row, and Commands/Response rules remain an equal-width segmented row.
- Step/rule fields stack to one column. Card secondary actions move into More.
- Dirty Save/Cancel becomes a sticky bottom row.
- No page-level horizontal overflow is allowed.
- Dense desktop hit targets are at least 32px; narrow targets are at least 40px. Visible Fugue
  glyphs remain 16 logical px.

## Feature Files

| Path | Action | Responsibility |
|---|---|---|
| `lib/features/command_sets/models.dart` | Create | Immutable domain unions and validation types |
| `lib/features/command_sets/seed.dart` | Create | Ten structured initial command sets |
| `lib/features/command_sets/repository.dart` | Create | Session snapshot, CRUD and reset |
| `lib/features/command_sets/controller.dart` | Create | Selection, drafts, filters, CRUD and preview |
| `lib/features/command_sets/workspace.dart` | Create | Responsive master-detail composition |
| `lib/features/command_sets/registry_pane.dart` | Create | Desktop registry and compact selector |
| `lib/features/command_sets/detail_header.dart` | Create | Persistent metadata and Plan usage |
| `lib/features/command_sets/commands_section.dart` | Create | Command catalog, selection and operation cards |
| `lib/features/command_sets/ussd_dialog_editor.dart` | Create | Start/Reply sequence and transition fallback |
| `lib/features/command_sets/response_rules_section.dart` | Create | Rule cards and sample tester |
| `lib/features/command_sets/set_dialogs.dart` | Create | Metadata, create/clone, delete and dirty guards |
| `lib/features/command_sets/legacy_audit.dart` | Create | Development/test-only path-to-target audit data |
| `lib/widgets/fugue_icon.dart` | Create | Density-aware Fugue asset wrapper |
| `lib/pages/nabor_page.dart` | Replace | Lightweight feature page entry |
| `lib/state/app_state.dart` | Modify | Own/forward/dispose controller |
| `lib/data/mock.dart` | Modify | Fix `megafon_mks`; remove incomplete set authority |
| `lib/pages/sims_page.dart` | Modify | Read live set IDs |
| `lib/widgets/sidebar.dart` | Modify | Use selected Fugue route icon |
| `lib/design/tokens.dart` | Modify | Add 16px-icon-relative editor metrics |
| `pubspec.yaml` | Modify | Register selected Fugue asset directory |
| `tool/verify_command_set_seed.dart` | Create | Verify legacy coverage and structured references |
| `test/command_set_seed_test.dart` | Create | Registry, seed semantics and audit coverage |
| `test/command_set_controller_test.dart` | Create | Validation, previews, CRUD, dirty guard and reset |
| `test/nabor_page_test.dart` | Create | Responsive states and primary user flows |

`legacy_audit.dart` must not be imported by production widgets or product models. If Dart build
tree-shaking cannot guarantee this cleanly, place it under `tool/` and `test/fixtures/` instead.

## Fugue Icon Contract

Every exact filename below exists and was visually reviewed in both the complete 16×16 catalog
and matching 32×32 rebuild. No emoji, Lucide, approximate fallback or 48px tier is permitted.

| Purpose | Fugue filename |
|---|---|
| Command Sets route / registry | `application-list.png` |
| Create/review metadata form | `application-form.png` |
| Edit metadata | `application--pencil.png` |
| Add set | `application--plus.png` |
| Delete set | `application--minus.png` |
| Clone set | `applications-stack.png` |
| More menu | `ui-menu.png` |
| Commands section | `application-task.png` |
| Response rules section | `funnel--pencil.png` |
| Add response rule | `funnel--plus.png` |
| USSD operation | `mobile-phone--arrow.png` |
| SMS operation | `mail.png` |
| Call operation | `telephone.png` |
| AT operation | `terminal.png` |
| Advanced regex | `regular-expression.png` |
| Test sample response | `beaker.png` |
| Reorder | `arrow-move.png` |
| Save | `disk.png` |
| Cancel/close | `cross.png` |
| System fallback | `lock.png` |
| Search | `magnifier.png` |
| Duplicate | `document-copy.png` |
| Validation warning | `exclamation.png` |
| Valid preview | `tick.png` |
| Collapsed metadata info | `information.png` |

No semantic slot is unresolved; no `FUGUE-WISHLIST.md` entry is required for this feature.

Flutter asset layout:

```text
assets/fugue/application-list.png       # original 16×16, 1x
assets/fugue/2.0x/application-list.png  # matching 32×32, 2x
```

`FugueIcon` calls `Image.asset` with a 16×16 logical box and lets Flutter select the `2.0x`
variant. It never uses a 32 logical-pixel Retina box, 48px asset, `FilterQuality.none` or
pixelated CSS rendering.

Add tokens derived from the shared logical icon unit:

```dart
static const fugueUnit = 16.0;
static const fugueFontSize = 12.0;     // unit × .75
static const fugueLineHeight = 18.0;   // unit × 1.125
static const fugueGap = 4.0;           // unit × .25
static const fuguePadX = 6.0;          // unit × .375
static const fugueRowMin = 28.0;       // unit × 1.75
static const protocolMono = TextStyle(
  fontFamily: 'monospace',
  fontFamilyFallback: ['SF Mono', 'Menlo', 'Consolas'],
  fontSize: 12,
  height: 1.5,
);
```

At 2×, Flutter doubles every physical UI measurement consistently while logical proportions
remain unchanged.

## Loading, Empty and Error States

| State | Required UI |
|---|---|
| Initial load | Stable two-pane skeleton; no false empty state |
| Seed failure | Error panel with Retry and Reset demo; other routes remain usable |
| No registry match | No command sets found + Clear search |
| `default` selected | Protected fallback explanation and two honest empty sections |
| Blank set | Add first command / Add first response rule actions |
| No command/rule filter match | Section-specific empty result + Clear filters |
| Invalid draft | Local errors, preserved focus/draft, no repository mutation |
| Dirty selection/navigation | Keep editing or Discard changes; Keep is default |
| Referenced delete | Plan usage list; no executable Delete CTA |
| Unexpected repository error | Snackbar plus intact prior snapshot and draft |
| Sample no match | No rule matched; no result and no write |
| Sample conversion error | Identify the effect and failed normalization |

There is no migration loading/status/error state.

## Accessibility and Copy

- Every icon-only action has Tooltip and a semantic label.
- Registry rows, segmented sections, menus, cards, reorder controls and dialogs are keyboard
  reachable with visible focus.
- Reordering has Move up/Move down alternatives; drag is not the only mechanism.
- Errors and enabled state use icon plus localized text, never color alone.
- Focus returns to the invoking control after a dialog/menu closes.
- Normal UI uses SF Pro Text. Only protocol literals, patterns, capture values and samples use the
  monospaced stack.
- Stable IDs and protocol literals are never translated. Feature labels use the application's
  localization boundary when that global capability is present; this feature does not create a
  competing language selector.

## Tests and Verification

### Seed/audit tests

- exact ten IDs in legacy order, including `kievstar`, `rostel_spb`, `megafon_msk`, and no
  `megafon_mks`;
- nine physical operator records plus protected empty `default`;
- distinct MegaFon regional records;
- every structured command has valid purpose, parameters and operations;
- every response rule has valid matcher/effects/outcome;
- every legacy path has exactly one audit disposition and every referenced target exists;
- Plan/group/counter/reset files map outside Command Sets;
- no migration status exists in product models.

### Controller tests

- first/select set opens Commands and section switching preserves the header;
- Blank/Clone creation and immutable ID validation;
- metadata, command, operation, USSD reply and rule CRUD;
- set-level Save/Cancel and dirty selection/navigation guard;
- template, fallback, regex, capture, duplicate-effect and normalization validation;
- multi-effect response preview for minutes plus SMS and no-write guarantee;
- referenced/default delete blocking and unreferenced delete;
- reset restores seed and removes user-created records;
- live selectable IDs update for SimsPage.

### Widget tests

- desktop registry/detail and narrow compact selector;
- exactly Commands and Response rules, with Commands default;
- persistent header with no Overview and no migration badge/filter;
- default, blank, filtered-empty, loading and error states;
- USSD Start/Reply editor with optional Fallback after;
- response WHEN/TAKE/SAVE cards and sample tester;
- metadata/create/clone/delete/dirty dialogs;
- 32px desktop and 40px narrow targets with 16px logical Fugue glyphs;
- tooltip/semantic labels and keyboard reorder alternatives.

### Commands

```text
dart run tool/verify_command_set_seed.dart
flutter test
flutter analyze
flutter build web
```

Final browser verification covers wide desktop, approximately 900px and narrow/mobile widths,
including 1× and 2× device-pixel ratios.

## Explicit Non-Goals

- No Shell/PHP/file editor or source browser.
- No command execution, modem test, simulated USSD response or runtime protocol compiler.
- No generic DSL, arbitrary expression or visual programming canvas.
- No numeric group, Plan limit, quota, counter or scheduler editor.
- No migration status, migration route or migration filter.
- No backend persistence/API in this prototype.
- No app-wide localization redesign inside this feature.

## Open Questions

None for implementation planning. Runtime USSD response correlation, retry and failover execution
remain intentionally deferred to a later architecture decision.

---

## Approval

- [x] Reviewed by: Anton Dodonov
- [x] Approved on: 2026-09-01
- [x] Notes: approved with `approved`; Specification 2.0 is the implementation authority.
