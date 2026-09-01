# Requirements: Command Sets Editor UI/UX

> Version: 1.2  
> Status: REVIEW  
> Last Updated: 2026-09-01

## Problem Statement

Legacy SimBox treats an operator command set (`nabor`) as an operational package: a stable set
identifier, group-transition constants, executable Shell/PHP commands and response parsers. A
plan stores the selected set identifier in `<plan>.nabor`, and runtime code executes files from
`/usr/simbox/nabor/<set>/commands/` and parses responses through `<set>/parse/`.

The legacy web screen `www/simbox/nabor.php` was never finished. It only reads
`/usr/simbox/nabor/nabor.list` into a one-column table and provides no way to inspect, add,
edit, clone or delete a set. The current visual source repeats that loss: it shows a decorative
list with guessed command counts, omits `kievstar` and `rostel_spb`, and misspells
`megafon_msk` as `megafon_mks`.

The prototype must turn this incomplete list into a usable command-set editor while preserving
the actual legacy packages and their regional identity. The old UI supplies meaning and logic,
not the target visual language. The visual source of truth remains
`design/simbox-design-prototype-v2026-dc`.

## Audited Legacy Baseline

### Set registry

`legacy/simbox-desktop-v2014/nabor/nabor.list` contains ten values in this exact order:

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

`default` has no physical package directory. It is a logical fallback used when a plan or SIM
has no explicit assignment and is also described by the legacy help as suitable for experiments.
It must therefore appear in the registry, but must never be presented as if it contained files.

### Physical package inventory

The following counts are literal files found in the active package directories. They are not
the guessed `6/9 commands` values from the design concept.

| Set ID | Operator | Country / region evidenced by legacy | Command files | Parser files |
|---|---|---|---:|---:|
| `megafon_msk` | MegaFon | Russia / Moscow | 5 | 3 |
| `megafon_spb` | MegaFon | Russia / Saint Petersburg | 11 | 8 |
| `beeline_spb` | Beeline | Russia / Saint Petersburg | 16 | 9 |
| `mts_spb` | MTS | Russia / Saint Petersburg | 5 | 4 |
| `tele2_spb` | Tele2 | Russia / Saint Petersburg | 16 | 10 |
| `rostel_spb` | Rostelecom | Russia / Saint Petersburg | 8 | 4 |
| `kievstar` | Kyivstar | Ukraine / nationwide-unspecified | 6 | 3 |
| `velcom` | Velcom | Belarus / nationwide-unspecified | 9 | 7 |
| `life` | life:) | Belarus / nationwide-unspecified | 6 | 3 |
| **Total physical files** | | | **82** | **51** |

Region must be a first-class editable attribute and must not be inferred only from the operator
name: the two MegaFon packages prove that one operator can have multiple regional command sets.
For legacy IDs without a regional suffix, the UI must show an explicit neutral value such as
“Not specified”, not invent a city.

### Command and parser files

All current package files must be seeded into the prototype so that no set looks empty and no
legacy package is silently collapsed into a generic template:

- `beeline_spb`: commands `123`, `activate_sim.sh`, `activate_work.sh`, `get_balance.sh`,
  `get_dover.sh`, `get_minutes.sh`, `get_number.sh`, `get_tarif.sh`, `inittarif.sh`,
  `send_may.sh`, `send_mon.sh`, `setdaylimit_0.sh`, `setdaylimit_2.sh`,
  `setdaylimit_new.sh`, `setdaylimit_sms.sh`, `setdaylimit.sh`; parsers `1.php`, `all.php`,
  `all.sh`, `parsebalance.php`, `parseblocked.php`, `parsedover.php`, `parseminutes.php`,
  `parsenumber.php`, `parsetarif.php`.
- `kievstar`: commands `activate_sim_fork`, `activate_sim.sh`, `activate_work.sh`,
  `get_balance.sh`, `get_number.sh`, `get_tarif.sh`; parsers `all.sh`, `parsebalance.sh`,
  `parsenumber.sh`.
- `life`: commands `activate_work.sh`, `get_balance.sh`, `get_number.sh`, `get_tarif.sh`,
  `send_may.sh`, `send_mon.sh`; parsers `all.sh`, `parsebalance.sh`, `parsenumber.sh`.
- `megafon_msk`: commands `activate_sim.sh`, `activate_work.sh`, `get_balance.sh`,
  `get_number.sh`, `get_tarif.sh`; parsers `all.sh`, `parsebalance.sh`, `parsenumber.sh`.
- `megafon_spb`: commands `activate_sim.sh`, `activate_work.sh`, `get_balance.sh`,
  `get_dover.sh`, `get_minutes.sh`, `get_number.sh`, `get_tarif.sh`, `send_may.sh`,
  `send_mon.sh`, `setdaylimit_new.sh`, `setdaylimit_set.sh`; parsers `all.php`, `all.sh`,
  `parsebalance.sh`, `parseblocked.sh`, `parselow.php`, `parseminutes.sh`, `parsenumber.php`,
  `parsenumber.sh`.
- `mts_spb`: commands `get_balance.sh`, `get_number.sh`, `getbalance.sh`, `getnumber.sh`,
  `inittarif.sh`; parsers `all.php`, `all.sh`, `parsebalance.php`, `parsenumber.php`.
- `rostel_spb`: commands `activate_sim.sh`, `activate_work.sh`, `get_balance.sh`,
  `get_dover.sh`, `get_minutes.sh`, `get_number.sh`, `get_options.sh`, `get_tarif.sh`;
  parsers `all.php`, `parseblocked.php`, `parselow.php`, `parsetarif.php`.
- `tele2_spb`: commands `activate_sim.sh`, `activate_work_old.sh`, `activate_work.sh`,
  `disable209.php`, `enter_pin.sh`, `get_balance.sh`, `get_dover.sh`, `get_minutes.sh`,
  `get_number.sh`, `get_options.sh`, `get_tarif.sh`, `send_may.sh`, `send_mon.sh`,
  `setdaylimit_new.sh`, `setdaylimit_reset.sh`, `setlimit_newday.php`; parsers `all.php`,
  `parsebalance.php`, `parsedover.php`, `parselow.php`, `parseminutes.php`, `parsenumber.php`,
  `parseoptions.php`, `parsepopolnenie.php`, `parsetarif.php`, `test.php`.
- `velcom`: commands `activate_sim.sh`, `activate_work_fork.sh`, `activate_work.sh`,
  `get_balance.sh`, `get_number_fork.sh`, `get_number.sh`, `get_tarif.sh`, `send_may.sh`,
  `send_mon.sh`; parsers `all.php`, `all.sh`, `parsebalance.php`, `parsebalance.sh`,
  `parsenumber.php`, `parsenumber.sh`, `parsetarif.php`.

Names such as `*_old`, `*_fork`, `test.php`, the standalone `123` maintenance script and files
under each package's `old/` directory are not safe to classify by filename alone. The prototype
must preserve them visibly with a `Legacy / review required` state, not silently delete them and
not claim that they are active. A known exception is `kievstar/activate_sim_fork`: it is invoked
by `activate_sim.sh` and therefore belongs to the active dependency chain. Historical `old/`
trees may be represented in a read-only “Legacy files” subsection; they are not executable
actions in the editor.

### Group-transition configuration

Each physical set has `config.sh` with the operator ID and group mappings for reserve, work,
manual stop, ACD stop, DATT stop, low balance and blocked states. The editor must expose these
values without losing their current numeric values. The seeded values are:

| Set | Reserve pre/ok | Work pre/ok/need-in | Stop manual/ACD/DATT | Low / blocked |
|---|---|---|---|---|
| `beeline_spb` | 32 / 52 | 82 / 102 / 142 | 300 / 333 / 333 | 402 / 502 |
| `kievstar` | 34 / 54 | 84 / 111 / 144 | 300 / 333 / 333 | 401 / 501 |
| `life` | 34 / 54 | 84 / 122 / 144 | 300 / 333 / 333 | 401 / 501 |
| `megafon_msk` | 34 / 54 | 84 / 104 / 144 | 300 / 333 / 333 | 401 / 501 |
| `megafon_spb` | 31 / 51 | 81 / 101 / 141 | 300 / 333 / 333 | 401 / 501 |
| `mts_spb` | 32 / 52 | 82 / 103 / 142 | 300 / 333 / 333 | 402 / 502 |
| `rostel_spb` | 31 / 51 | 81 / 220 / 141 | 300 / 333 / 333 | 401 / 501 |
| `tele2_spb` | 31 / 51 | 81 / 109 / 141 | 300 / 333 / 333 | 401 / 501 |
| `velcom` | 34 / 54 | 84 / 122 / 144 | 300 / 333 / 333 | 401 / 501 |

## Proposed Single UI/UX Direction

Use a master-detail editor rather than a second wide operational table:

- A compact registry pane lists all ten values with operator, region, file counts and status.
- Search and `Add set` remain in its header; selecting a row updates the detail area without
  navigation or a modal.
- The detail area has four stable tabs: **Overview**, **Commands**, **Parsers**, **Groups**.
- Commands and parsers use a file list plus a monospaced source editor. This is intentionally
  source-preserving: the legacy scripts contain arbitrary Shell/PHP control flow that cannot be
  faithfully represented by a handful of invented “USSD code” fields.
- `Add` offers **Blank** and **Clone existing**. Cloning is the recommended path for a regional
  variant because it preserves a known-working file structure while requiring a new unique ID.
- Edit uses an explicit draft state with **Save** and **Cancel**; unsaved changes are marked.
- Delete first shows impact/usage. An unreferenced user-created set can be deleted after
  confirmation. A set assigned to a plan must be reassigned before deletion. `default` is
  protected. This avoids leaving a plan pointing at a nonexistent package.
- File deletion uses the same review/confirmation pattern. Referenced aggregator/dependency
  files cannot be deleted until the dependency is removed.

This is the one proposed final direction. Alternative card grids and wizard-only editing are
rejected because they hide regional comparison and make frequent file-level editing slower.

## User Stories

### Primary

**As a** SimBox administrator  
**I want** every legacy operator and regional command set available on first load  
**So that** migrating to the prototype does not erase operational knowledge.

**As a** maintainer onboarding a new regional operator variant  
**I want** to clone a nearby set, change its region, commands, parsers and group mappings, then
save it under a unique stable ID  
**So that** I can adapt existing behavior without editing server files manually.

**As a** maintainer fixing an operator response  
**I want** to edit the relevant command or parser while keeping the whole source visible  
**So that** arbitrary legacy Shell/PHP behavior is not lost in an oversimplified form.

### Secondary

**As an** administrator  
**I want** destructive changes blocked when a set is still in use  
**So that** plans do not acquire broken references.

## Acceptance Criteria

### Must Have

1. **Given** the Command Sets route is opened for the first time  
   **When** the seeded registry renders  
   **Then** it contains the exact ten `nabor.list` IDs above, including `kievstar`,
   `rostel_spb` and correctly spelled `megafon_msk`, with no invented `megafon_mks` record.

2. **Given** a physical legacy set is selected  
   **When** its details render  
   **Then** every current command, parser and group value listed in this document is reachable
   without data loss, and counts are derived from the actual seeded arrays rather than hardcoded
   display numbers.

3. **Given** `default` is selected  
   **When** the detail area renders  
   **Then** it is clearly identified as a system fallback with no physical command/parser files;
   edit and delete actions that would imply a package directory are disabled with an explanation.

4. **Given** two sets belong to the same operator but different regions  
   **When** they appear in the registry  
   **Then** operator and region are separate visible fields, and filtering can find either value.

5. **Given** the user chooses Add  
   **When** they select Blank or Clone, provide a unique filesystem-safe ID, operator, country
   and region, and save  
   **Then** the new record appears immediately; cloning duplicates config/command/parser content
   but not the source record's ID or usage references.

6. **Given** an editable set is open  
   **When** the user changes metadata, group mappings, command source or parser source  
   **Then** the page enters a visible dirty/draft state and only explicit Save commits it;
   Cancel restores the last saved snapshot.

7. **Given** a command or parser is created or renamed  
   **When** the user saves it  
   **Then** its filename is unique within its own section, restricted to safe relative filenames,
   has an explicit Shell/PHP type inferred from or consistent with the extension, and is never
   allowed to escape the package directory.

8. **Given** a legacy artifact has ambiguous or historical status  
   **When** it is displayed  
   **Then** the UI labels it `Legacy / review required`; known dependency usage is shown where
   verified; it is never silently omitted or presented as certainly active.

9. **Given** the user requests deletion  
   **When** the set is `default` or referenced by a plan  
   **Then** deletion is blocked and the reason/usage is shown; an unreferenced non-system set
   requires an explicit confirmation before removal.

10. **Given** the viewport narrows  
    **When** master and detail no longer fit side by side  
    **Then** the registry becomes a compact selector/list above the detail area, editors remain
    usable without page-level horizontal overflow, and primary Save/Cancel actions remain visible.

11. **Given** any editor action succeeds or fails  
    **When** feedback is shown  
    **Then** it is conveyed with text plus a Fugue icon/status treatment, never by color alone;
    source code uses a legible monospaced stack and the surrounding UI follows the typography,
    spacing, color, radius and shadow language of `v2026-dc`.

12. **Given** this is a design prototype rather than a live server  
    **When** CRUD is exercised  
    **Then** all operations work locally and visibly (including validation, confirmation,
    dependency blocking and reset/reload behavior), while no real legacy file or service is
    modified.

### Should Have

- A compact comparison mode for group mappings across selected regional sets.
- Keyboard save/cancel (`Ctrl/Cmd+S`, Escape) when focus is inside an editor.
- Search across set ID, operator, country, region and filenames.
- A clear “Reset demo data” control for restoring the audited seed after prototype CRUD changes.

### Won't Have (This Iteration)

- No execution of Shell/PHP commands from the editor and no live modem test runner.
- No automatic conversion of arbitrary scripts into a new DSL or form schema.
- No backend persistence/API design; local prototype behavior only.
- No resurrection of files under `old/` as active commands.
- No renaming of an existing stable set ID in place. Create/clone a replacement and reassign
  references instead, because the ID is embedded in paths and plan values.
- No visual imitation of the 2014 PHP table.

## Constraints

- **Logic source of truth**: `legacy/simbox-desktop-v2014`, especially
  `legacy/simbox-desktop-v2014/www/simbox`, `nabor/` and plan assignment behavior.
- **Visual source of truth**: `design/simbox-design-prototype-v2026-dc`.
- **Implementation target**: the existing Flutter Web prototype at
  `design/simbox-web-design-prototype-v2026`. The previously recorded path without `-web-` was a
  request transcription error and is superseded by the user's corrected VDD invocation.
- **Integrity**: preserve stable IDs and arbitrary source text; do not normalize away duplicate
  PHP/Shell parser variants or operator-specific scripts.
- **Safety**: all destructive actions require dependency checks and confirmation.
- **Prototype boundary**: legacy files remain read-only evidence.

## Approved Defaults

- [x] Master-detail direction with four tabs is the single final UI approach.
- [x] `default` is protected/read-only and referenced sets are non-deletable until
  reassignment.
- [x] Ambiguous/historical files remain visible rather than being omitted, with
  `Legacy / review required` status and read-only `old/` subsection.
- [x] **Clone existing** is the recommended creation path for a regional variant, while
  retaining **Blank** for genuinely new operators.

## Requirement Amendment 1.1 — Semantic Operations, No Source Editor

This amendment is authoritative and supersedes every earlier requirement to expose, create,
rename or edit Shell/PHP files in the product UI. In particular, it replaces the source-editor
direction, the third primary user story, Must Have criteria 2, 6, 7, 10 and 11 where they refer
to files/source code, and the related integrity wording. The audited files remain migration
evidence, but are not the interaction model.

### Why raw Shell/PHP is not the domain model

The legacy audit shows two layers mixed together in the filesystem:

- transport and operational effects: send USSD, send SMS, make a call, send an AT command,
  change a SIM group, update a limit/counter/timestamp and invoke another operation;
- response handling: recognize text, extract a value, normalize it, store it in a typed SIM
  field and optionally change operational state.

Shell and PHP are only the implementation mechanisms around these operations. A form capable of
representing arbitrary Shell/PHP control flow would become a new low-code programming language.
That is explicitly outside this feature. The UI must instead cover the finite, legacy-verified
operation vocabulary and identify anything outside it as migration work rather than pretending
that it was converted safely.

### Authoritative information architecture

The persistent master-detail layout remains, but the tabs become:

1. **Overview** — identity, operator, country/region, usage and migration status.
2. **Commands** — functional command slots containing ordered, structured steps.
3. **Response rules** — recognition, extraction, normalization and typed outcomes; this replaces
   the implementation-facing term **Parsers**.
4. **Groups & limits** — group transitions, counters, limits and verified maintenance policies.

No normal UI shows source code, `.sh`/`.php` types, file creation, filenames or aggregator files
such as `all.php`. Technical provenance may be retained in the seed manifest and test fixtures,
but is not editable product content.

### Supported command model

Commands use stable functional slots found in legacy, including Activate SIM, Activate work,
Get balance, Get number, Get tariff, Get minutes, Get options, Promise payment, Send MAY,
Send MON, Enter PIN and daily-limit maintenance. A set may implement only the slots relevant to
its operator/region.

Each command is an ordered workflow assembled from these verified step types:

- Send USSD (code template, queue/class and optional parameter);
- Send SMS (destination and message template);
- Make call (number and verified call profile);
- Send AT command;
- Set SIM group;
- Set typed limit, counter or timestamp;
- Wait for response / delay;
- Run another command;
- Conditional branch limited to typed state such as current group.

Templates may insert only declared values such as SIM, dongle, IMSI and an operator-entered
parameter. The builder does not accept arbitrary executable expressions. Unknown legacy control
flow is marked **Needs migration** and is never exposed as an apparently valid executable form.

### Supported response-rule model

A response rule is an ordered, enableable record with:

- source channel: USSD, SMS or call result;
- match mode: contains, starts with or regular expression under **Advanced match**;
- extraction: fixed value or named/captured value;
- typed normalization: trim text, decimal comma/dot, numeric conversion, country-code prefix,
  date conversion or a specifically supported arithmetic transform;
- destination: balance, phone number, tariff, minutes, options, promise-payment value/state/date,
  group, limit, counter or timestamp;
- optional matched outcome: set group or update another typed operational field.

Rules are tested with pasted sample responses. The preview highlights the matched fragment and
shows the exact typed changes without calling a modem or writing legacy files. A failed match or
invalid conversion produces an explanation and no result.

### CRUD and migration behavior

- Clone existing remains the recommended way to create a regional variant.
- Commands are added from the supported functional-slot catalog; steps and response rules are
  added from finite menus, reordered, enabled/disabled, duplicated and deleted in a draft.
- Save/Cancel applies to the whole selected set and preserves dependency checks.
- All ten sets and all active legacy behavior must be present initially as structured commands,
  rules, groups and limits. Historical/test/fork artifacts are migration-audit records, not UI
  commands. A known active dependency such as Kyivstar's fork helper must be folded into its
  calling workflow.
- Each migrated item carries **Migrated**, **Needs review** or **Needs migration** status. Counts
  in the registry describe user-facing commands/rules, while the legacy file counts remain audit
  totals and must not be presented as the same measure.

### Revised acceptance criteria

1. Selecting a physical set reveals every active legacy behavior as a named command workflow,
   response rule, group transition or limit policy, with no Shell/PHP editor or filename CRUD.
2. A command can be created and edited only from the supported functional slots and step types;
   ordering, required fields, parameter references and dependencies are validated before Save.
3. A response rule can be created, reordered and tested against sample text; its match,
   extraction, normalization and typed outcomes are visible before Save.
4. Unsupported or ambiguous behavior is visible in migration status with a reason and cannot be
   silently activated, omitted or represented as a misleading generic step.
5. On narrow viewports, workflow steps and response rules become single-column cards; the set
   selector, tabs and sticky Save/Cancel remain usable without page-level horizontal overflow.
6. Command/rule controls use normal UI typography. Monospace is limited to literal USSD codes,
   phone numbers, regex patterns, templates and sample payloads—not the entire screen.
7. The prototype performs local validation and response previews only. It does not execute USSD,
   SMS, calls, AT commands, Shell or PHP and does not modify the legacy source.

### Revised non-goals

- No raw-code editor or source browser in the operator-facing UI.
- No arbitrary scripting, generic expression language or visual programming canvas.
- No automatic claim that every historical/test file is an active operation.
- No modem execution or live response capture in this prototype.

### Approval reset

- [x] Amendment 1.1 requirements approved
- [x] The prior source-editor direction is confirmed as superseded

## Requirement Amendment 1.2 — USSD Dialog Sequences

This amendment refines Amendment 1.1 after domain-owner feedback. Legacy sequences such as
`USSD → fixed delay → USSD reply` existed because the old system did not have a proper mechanism
for receiving and correlating intermediate USSD responses. The delay is therefore an
implementation workaround, not the business meaning of the command.

### Authoritative USSD model

- The command editor must treat an interactive command as an ordered **USSD dialog sequence**.
- The first item starts a USSD session with an initial code.
- Following items are replies/selections in that dialog, not unrelated new commands.
- The normal visual model must not expose a fixed `Wait N seconds` item between USSD steps.
- A sequence may contain one step; single-request USSD commands use the same model.
- Literal values and declared templates such as a destination number remain supported.
- The editor stores the logical order and payloads only. How runtime receives a response,
  correlates a session, advances a step, times out, retries or falls back is intentionally
  deferred and must not be implied by the prototype.

Example migration:

```text
Legacy implementation
1. Send USSD `*105*0082#`
2. Sleep 7 seconds
3. Send USSD `1`

Prototype domain model
USSD dialog: Enable outgoing calls
1. Start with `*105*0082#`
2. Reply `1`
```

The earlier generic `Wait for response / delay` command step remains valid only for a genuinely
intentional delayed business action verified independently of a missing USSD-response mechanism.
It must not be generated from legacy sleeps used to approximate an interactive USSD session.

### Acceptance additions

1. Migrating an interactive USSD script removes transport sleeps and preserves the ordered USSD
   start/reply sequence without claiming how it will execute.
2. The user can add, remove, duplicate and reorder USSD dialog steps and edit each payload.
3. The first step is visibly distinguished as **Start**, subsequent steps as **Reply**.
4. The prototype validates an empty sequence, empty payloads and invalid template references but
   does not execute, simulate or time the dialog.
5. Runtime session handling, response correlation, timeout, retry and failure policy are explicit
   non-goals for this VDD feature and will be decided later.

### Amendment 1.2 approval

- [x] USSD dialog-sequence model approved
- [x] Runtime mechanism confirmed as deferred

## Requirement Amendment 1.3 — USSD Transition Failover and Entity Ownership

> Added from domain-owner clarification and scoped legacy audit on 2026-09-01.

This amendment refines, and where necessary supersedes, the USSD transition and
**Groups & limits** wording in Amendments 1.1–1.2.

### USSD step transition

The canonical command remains a logical USSD Start/Reply sequence. A transition between two
payloads may additionally retain a fallback duration:

```text
1. Start `*105*0082#`
2. Reply `1`
   Preferred transition: after operator response
   Failover: after 7 seconds
```

An executor may later compile the same intent into a compact transport representation such as
`*105*0082#WWWWWWW1`, or implement a response-aware session and use the duration only when no
correlated response arrives. That representation and execution choice are not canonical UI data
and are explicitly deferred.

- Delay is a transition property, not a standalone USSD command step.
- Fallback is optional and may be enabled per transition when preserving a verified legacy
  duration is operationally useful.
- The prototype edits and validates the fallback duration but does not run or simulate it.
- UI copy must say **Fallback after**, not **Wait**, when the preferred transition is a response.

### Correct ownership of limits and counters

The legacy source confirms that command sets are not the owner of daily counters or plan limits:

| Concern | Authoritative redesigned entity | Legacy evidence |
|---|---|---|
| Soft/hard call limits and direction algorithms | Plan | `plan.php` writes `limit_max.*`, `limit_hard.*`, `alg.*` |
| MAY/MON/MSM and outgoing-SMS quotas | Plan | `plan.php` writes `may_limit`, `mon_limit`, `msm_limit`, `smsout_soft/hard` |
| SMS activity thresholds and daily/total quotas | Plan | `plan.php` writes `satt_*` values |
| Current sent/used counters | SIM runtime state | `*.may_sended`, `*.mon_sended`, `*.msm_sended`, `*.smsout_sended` |
| Daily reset execution | System scheduler | `cron/everynewday.sh` invokes reset scripts |
| Operator allowance recognition | Command-set response rules | parsers extract minutes/SMS and update runtime measurements |

`set_plan_copy.sh` copies Plan policy values into per-SIM runtime settings. The operator-specific
`setdaylimit*` files mix scheduler work, counter reset and hardcoded effective-limit overrides;
they are legacy responsibility leakage and must not become editable commands in the command-set
builder.

Consequently:

- the fourth command-set tab returns to **Groups**, containing only verified operator lifecycle
  group mappings from `config.sh`;
- Plan owns limit/quota policy editing;
- SIM views own current usage/counter display and any authorized per-SIM override;
- daily reset belongs to system scheduling/maintenance, not Plan and not Command Sets;
- response rules may populate measured allowances such as remaining minutes or SMS, but do not
  define the Plan's permitted usage policy;
- hardcoded legacy overrides are preserved in the migration audit with **Needs review**, pending
  later migration to Plan or another policy entity.

### Acceptance additions

1. A USSD reply transition can show an optional response-first fallback duration without exposing
   `W` encoding or pretending that runtime response handling exists.
2. Command Sets contains no editor for daily counters, soft/hard limits, MAY/MON/MSM quotas or
   reset schedules.
3. Legacy maintenance files are accounted for in migration status but excluded from the active
   command count and command builder.
4. The Command Sets workspace links to the owning Plan for policy values when context is useful,
   instead of duplicating those inputs.

### Amendment 1.3 approval

- [x] Response-first transition with optional time-based failover approved
- [x] Plan / SIM runtime / scheduler ownership split approved

## Requirement Amendment 1.4 — Group Mapping Belongs to Plan

> Added from domain-owner clarification and scoped legacy audit on 2026-09-01.

This amendment supersedes every earlier requirement for a **Groups** or **Groups & limits** tab in
Command Sets.

The legacy tree is inconsistent: each `nabor/*/config.sh` declares `GROUP_ZAPAS_*`,
`GROUP_WORK_*`, stop, low-balance and blocked numbers, but repository-wide usage search finds
those symbols only in their declarations. Active parsers and automation instead use hardcoded
numeric groups, while `plan.php` selects the command set and owns operational policy. The config
location therefore reflects unfinished legacy organization, not a sound target ownership model.

The redesigned ownership is:

| Concern | Owner |
|---|---|
| Semantic outcome such as `work_ready`, `low_balance`, `blocked` | Command-set response rule |
| Mapping semantic outcome to a numeric operational group | Plan |
| Current numeric group | SIM runtime state |
| Manual change of current group | SIM action |
| Global identity/description of a group, if formalized later | Group catalog / system configuration |

Consequently:

- Command Sets has exactly three primary tabs: **Overview**, **Commands**, **Response rules**.
- A response rule emits a typed semantic outcome and never embeds an editable numeric group.
- Plan owns lifecycle mappings for reserve preparation/ready, work preparation/ready/needs
  incoming, manual/automatic stop, low balance and blocked outcomes.
- The current SIM group remains visible and manually changeable in SIM operations, independently
  of editing a Plan or Command Set.
- Legacy `GROUP_*` declarations and hardcoded parser group numbers are imported into a migration
  comparison so the eventual Plan mapping can be reviewed without data loss; they are not fields
  in this feature.

### Acceptance additions

1. No numeric group editor appears anywhere in the Command Sets workspace.
2. Response-rule outcomes are selected from semantic statuses, not entered as group numbers.
3. Command-set migration reports conflicting declared/hardcoded group mappings without resolving
   them silently.
4. Where a response outcome depends on Plan configuration, the UI may link to that Plan but does
   not duplicate its mapping controls.

### Amendment 1.4 approval

- [x] Remove Groups from Command Sets and place lifecycle mapping in Plan
- [x] Keep current/manual group state with SIM operations

## Requirement Amendment 1.5 — Remove the Redundant Overview Tab

> Added after reviewing the information architecture with the domain owner on 2026-09-01.

This amendment supersedes the three-tab requirement in Amendment 1.4. A separate **Overview**
page is unnecessary: its intended content is the identity and state of the currently selected
command set, which must remain visible while commands and response rules are edited. Making that
content a tab adds a navigation step without introducing a separate task.

The command-set detail therefore has exactly two primary sections:

- **Commands** — operator actions and USSD dialog sequences;
- **Response rules** — typed parsing, extracted values and semantic outcomes.

The persistent detail header owns the former Overview content:

- command-set name and stable ID;
- operator, country and region;
- system/default or migration status;
- number of Plans using the set, with a link to those Plans;
- **Edit metadata**, **Clone** and **Delete** actions where permitted.

Selecting a command set opens **Commands** by default. Metadata is edited from the header in a
compact drawer or dialog; it is not a third workspace. Migration issues open a contextual details
panel from the status badge and remain attached to the affected command or response rule where
possible. No synthetic dashboard, charts, activity feed or other new Overview functionality is
introduced.

### Acceptance additions

1. No Overview tab appears in the Command Sets workspace.
2. Identity, assignment and migration state remain visible from both primary sections.
3. Switching between Commands and Response rules does not move or replace the detail header.
4. Selecting a set opens Commands; returning to a set may restore its last selected section.
5. The `default` fallback uses the same header and two-section structure, with protected-system
   actions and honest empty states where it has no explicit commands or rules.

### Amendment 1.5 approval

- [x] Replace Overview with a persistent metadata header
- [x] Use only Commands and Response rules as primary sections

## Requirement Amendment 1.6 — Migration Is Not a Command-Set Status

> Added after domain-owner review on 2026-09-01.

This amendment removes **migration status** from the user-facing Command Sets workspace. It was
introduced as an audit aid for importing ambiguous legacy files, not as a business property of an
operator command set. Once seed data is created, operators should not need to know how a record
was obtained.

- The persistent header contains no Migrated, Legacy or Needs migration badge.
- The one-time import inventory and unresolved source artifacts belong to a developer/admin
  migration report outside the operational prototype.
- If an editable command or response rule is incomplete, the editor uses ordinary, actionable
  validation such as **Reply payload is required** or **Pattern is invalid**; it does not expose
  the historical cause as a migration state.
- Unsupported legacy artifacts remain accounted for in the source audit and implementation log,
  but they are not presented as active command-set records.
- No migration filter, migration details drawer or migration lifecycle is added to the product.

### Acceptance additions

1. Command-set headers, registry rows and filters contain no migration status.
2. Users see validation and save errors only when they can act on them.
3. Legacy coverage can be verified from implementation documentation without adding operational
   UI or a new domain field.

### Amendment 1.6 approval

- [x] Keep legacy migration audit outside the operational UI
- [x] Replace record-level migration labels with actionable editor validation

## References

- `legacy/simbox-desktop-v2014/www/simbox/nabor.php`
- `legacy/simbox-desktop-v2014/www/simbox/plan.php`
- `legacy/simbox-desktop-v2014/nabor/nabor.list`
- `legacy/simbox-desktop-v2014/nabor/*/{config.sh,commands,parse,old}`
- `legacy/simbox-desktop-v2014/system/{get_args_plan_nabor.sh,parseussdsms.sh,parsesmsussd.php}`
- `legacy/simbox-desktop-v2014/ai/sms/send_maymon.php`
- `design/simbox-design-prototype-v2026-dc/index.html`

---

## Approval

- [x] Reviewed by: Anton Dodonov
- [x] Approved on: 2026-09-01
- [x] Notes: approved with `reqs approved`; all proposed defaults accepted.
