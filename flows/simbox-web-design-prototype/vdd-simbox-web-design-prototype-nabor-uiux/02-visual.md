# Visual Mockups: Command Sets Editor UI/UX

> Version: 1.2  
> Status: REVIEW  
> Last Updated: 2026-09-01  
> Requirements: [01-requirements.md](01-requirements.md)

## Overview

The approved direction is a single master-detail workspace inside the existing SimBox shell.
It is intentionally calmer than an IDE and denser than a consumer settings screen:

- left pane: compact registry of the ten command-set IDs;
- right pane: persistent details with Overview, Commands, Parsers and Groups tabs;
- one primary gradient action at a time (`Add set` while browsing, `Save` while editing);
- all secondary actions are quiet surface/outline or icon buttons;
- Fugue glyphs provide semantics, but labels remain visible for primary and destructive actions;
- no modal is used for ordinary editing; only destructive confirmation uses a modal.

## Screen A — Registry + Overview (desktop, default state)

Target viewport: 1280px and wider. Existing navigation stays untouched. The workspace card uses
the remaining content width and a minimum practical height of about 640px.

```text
+--------------------------------------------------------------------------------------------------+
| Existing SimBox header / status / language                                                       |
+----------------+---------------------------------------------------------------------------------+
| Existing       | Command sets                                                [Reset demo] [＋ Add]|
| navigation     | 10 sets · 9 physical packages · 82 commands · 51 parsers                         |
|                +--------------------------------+------------------------------------------------+
|                | [⌕ Search ID/operator/region] |  MegaFon · Moscow                    [···]       |
|                |                                |  megafon_msk                                    |
|                | ● default              SYSTEM |  Russia / Moscow · physical package             |
|                |   System fallback        0 / 0 |                                                |
|                |                                |  [Overview] [Commands 5] [Parsers 3] [Groups]   |
|                | ● megafon_msk          ACTIVE |------------------------------------------------|
|                |   MegaFon · Moscow       5 / 3 |                                                |
|                |                                |  Package identity                              |
|                | ○ megafon_spb          ACTIVE |  Operator       MegaFon                         |
|                |   MegaFon · St Petersburg11/8 |  Country        Russia                          |
|                |                                |  Region         Moscow                          |
|                | ○ beeline_spb          ACTIVE |  Stable ID      megafon_msk          [copy]      |
|                |   Beeline · St Petersburg16/9 |                                                |
|                |                                |  Usage                                          |
|                | ○ mts_spb              ACTIVE |  Used by 2 plans                                |
|                |   MTS · St Petersburg    5 / 4 |  default_msk · outgoing_moscow         [view]    |
|                |                                |                                                |
|                | ○ tele2_spb            REVIEW |  Package summary                                |
|                |   Tele2 · St Petersburg 16/10 |  5 commands · 3 parsers · 9 group mappings      |
|                |                                |                                                |
|                | ... 5 more sets                |  [Clone set]   [Edit metadata]   [Delete]       |
|                +--------------------------------+------------------------------------------------+
|                |  ● Active   ◐ Review required   ◆ System fallback   Counts = commands/parsers   |
+----------------+---------------------------------------------------------------------------------+
```

### Registry row anatomy

```text
+----------------------------------------------------------------+
| [operator Fugue glyph]  megafon_spb                    [status] |
|                         MegaFon · Saint Petersburg     11 / 8  |
+----------------------------------------------------------------+
  16px logical icon       primary 13px / mono ID          counts
  32px source on Retina   secondary 11px                  tabular
```

- Selected row uses `--brand-tint`; hover is a 4% overlay.
- `ACTIVE`, `REVIEW`, `SYSTEM` are text badges with distinct Fugue glyphs; never color alone.
- Set ID and file counts use tabular/monospaced numerals.
- Operators with multiple regions remain separate rows and visually comparable.

## Screen B — Commands editor

Opening Commands changes only the right pane. The registry remains visible, so the operator and
region context cannot be lost.

```text
+--------------------------------+-----------------------------------------------------------------+
| Registry                       | MegaFon · Saint Petersburg          Draft changed  [Cancel] [Save]|
|                                | [Overview] [Commands 11] [Parsers 8] [Groups]                    |
| ● megafon_spb          ACTIVE |-----------------------------------------------------------------|
|   MegaFon · St Petersburg11/8 | [⌕ Filter files] [＋ New file]                                      |
|                                |+----------------------+------------------------------------------+|
|                                || Command files        | get_balance.sh          Shell     [···] ||
|                                ||                      | /megafon_spb/commands/get_balance.sh     ||
|                                || ● activate_sim.sh    |------------------------------------------||
|                                || ○ activate_work.sh   |  1  #!/bin/sh                            ||
|                                || ○ get_balance.sh     |  2                                       ||
|                                || ○ get_dover.sh       |  3  . /usr/simbox/config.sh              ||
|                                || ○ get_minutes.sh     |  4  . /usr/simbox/nabor/.../config.sh   ||
|                                || ○ get_number.sh      |  5                                       ||
|                                || ○ get_tarif.sh       |  6  echo "-- Getting balance"           ||
|                                || ...                  |  7  $ASTERISK ...                        ||
|                                ||----------------------|  8                                       ||
|                                || Legacy / review      |                                          ||
|                                || ◐ old_helper.sh      |                                          ||
|                                |+----------------------+------------------------------------------+|
|                                | Dependency: called by activate_work.sh          [Open dependency] |
+--------------------------------+-----------------------------------------------------------------+
```

### Editor behavior

- Source area uses `SFMono-Regular, ui-monospace, Menlo, Consolas, monospace`, 12px with a
  18px line height; UI labels remain SF Pro Text.
- Header Save/Cancel stays sticky within the detail card.
- A changed filename/source receives a small `Draft changed` badge and dot in the file list.
- The file menu contains Rename, Duplicate and Delete. Delete is disabled when a known active
  dependency exists and explains why.
- `Legacy / review required` is a separate collapsed subsection, not mixed silently with active
  files. `old/` content opens read-only with a lock badge.
- Editor uses one internal horizontal scroller if a source line is long; the whole page never
  becomes horizontally scrollable.

## Screen C — Parsers editor

The Parsers tab reuses Screen B exactly. Only terminology and the file inventory change.

```text
+----------------------+-----------------------------------------------------------+
| Parser files         | all.php                                    PHP     [···] |
|                      |-----------------------------------------------------------|
| ● all.php            |  1  <?php                                            |
| ○ all.sh             |  2  include(".../parsebalance.php");                    |
| ○ parsebalance.php   |  3  include(".../parsenumber.php");                     |
| ○ parsenumber.php    |  4  ?>                                               |
|                      |                                                           |
| Legacy / review      | Dependency chain                                          |
| ◐ test.php           | all.php -> parsebalance.php, parsenumber.php               |
+----------------------+-----------------------------------------------------------+
```

Shell and PHP variants with similar names remain separate; the UI does not merge them.

## Screen D — Groups editor

Group mappings are arranged by operational meaning, not by the raw order in `config.sh`.
Numeric inputs stay compact and right-aligned.

```text
+-----------------------------------------------------------------------------------+
| MegaFon · Saint Petersburg                    Draft changed          [Cancel] [Save]|
| [Overview] [Commands 11] [Parsers 8] [Groups]                                    |
|-----------------------------------------------------------------------------------|
| Reserve                         Work                                               |
| +----------------------------+  +-----------------------------------------------+ |
| | Pre-group             [ 31]|  | Pre-group                                [ 81]| |
| | Ready group           [ 51]|  | Ready group                              [101]| |
| +----------------------------+  | Needs incoming group                     [141]| |
|                                 +-----------------------------------------------+ |
| Stop                            Balance / blocking                                |
| +----------------------------+  +-----------------------------------------------+ |
| | Manual                [300]|  | Low balance group                        [401]| |
| | ACD                   [333]|  | Blocked group                            [501]| |
| | DATT                  [333]|  +-----------------------------------------------+ |
| +----------------------------+                                                       |
|                                                                                   |
| [Compare regional sets]                                                           |
+-----------------------------------------------------------------------------------+
```

### Optional comparison state

`Compare regional sets` opens an inline comparison below the editor rather than a modal:

```text
+--------------------+-------------+-------------+-------------+
| Mapping            | megafon_msk| megafon_spb| beeline_spb |
| Reserve pre / ok   |     34 / 54 |     31 / 51 |    32 / 52 |
| Work pre / ok / in | 84/104/144 | 81/101/141 | 82/102/142 |
| Stop M/ACD/DATT    | 300/333/333| 300/333/333| 300/333/333|
| Low / blocked      |   401 / 501 |   401 / 501 |  402 / 502 |
+--------------------+-------------+-------------+-------------+
```

## Screen E — Create set

Create is an in-workspace flow. The registry dims but remains visible; the detail pane becomes a
draft. Step count is deliberately limited to two.

### E1 — Choose starting point

```text
+--------------------------------------------------------------------------+
| New command set                                                 [Cancel] |
|                                                                          |
| Choose a starting point                                                  |
|                                                                          |
| +--------------------------------+  +----------------------------------+ |
| | [copy Fugue icon]              |  | [blank-file Fugue icon]         | |
| | Clone existing                 |  | Blank                            | |
| | Recommended for a regional     |  | For a genuinely new operator    | |
| | variant. Keeps files/groups.   |  | No commands, parsers or groups. | |
| | [Choose source ▼]              |  |                                  | |
| +--------------------------------+  +----------------------------------+ |
|                                                   [Continue]             |
+--------------------------------------------------------------------------+
```

### E2 — Identity and review

```text
+--------------------------------------------------------------------------+
| New command set                                       Step 2 of 2        |
|                                                                          |
| Stable ID *       [megafon_nsk____________________]                      |
| Operator *        [MegaFon________________________]                      |
| Country *         [Russia_________________________]                      |
| Region            [Novosibirsk____________________]                      |
|                                                                          |
| Cloned from       megafon_msk                                            |
| Will create       5 commands · 3 parsers · 9 group mappings              |
| Usage             none                                                   |
|                                                                          |
| [Back]                                             [Create set]          |
+--------------------------------------------------------------------------+
```

Validation appears below the exact field without clearing entered values:

```text
Stable ID *  [megafon/moscow________________]
             [error Fugue icon] Use lowercase letters, digits and underscores only.
```

After successful creation, the new registry row is selected and Overview opens with a calm
success toast: `[success Fugue icon] Command set created`.

## Screen F — Deletion and protection

### F1 — Deletion blocked by usage

This is an inline impact panel because no destructive choice can currently be made.

```text
+--------------------------------------------------------------------------+
| [lock Fugue icon] Cannot delete megafon_msk                              |
|                                                                          |
| This set is used by 2 plans:                                             |
| • default_msk                                                   [Open]   |
| • outgoing_moscow                                              [Open]   |
|                                                                          |
| Reassign those plans before deleting this set.                 [Close]  |
+--------------------------------------------------------------------------+
```

For `default`, the message reads: `System fallback cannot be deleted.` No delete-confirmation
button is shown.

### F2 — Unreferenced set confirmation

```text
                         +----------------------------------------------+
                         | [warning Fugue icon] Delete megafon_nsk?    |
                         |                                              |
                         | 5 commands, 3 parsers and group mappings     |
                         | will be removed from this prototype.         |
                         |                                              |
                         | This action can be undone only by Reset demo.|
                         |                                              |
                         | [Cancel]                 [Delete set]         |
                         +----------------------------------------------+
```

The modal is narrow, centered and uses the standard surface plus `--shadow-modal`; the danger
button is solid semantic red, never the brand gradient.

## Screen G — System fallback / meaningful empty state

`default` is not shown as a broken empty package.

```text
+--------------------------------------------------------------------------+
| System fallback · default                                      [system]  |
| [Overview] [Commands 0] [Parsers 0] [Groups]                              |
|--------------------------------------------------------------------------|
|                      [protected-package Fugue icon]                       |
|                         No physical package                              |
|                                                                          |
| `default` is used when a plan has no explicit command set.               |
| Create or clone a physical set to add operator commands.                 |
|                                                                          |
|                           [Clone as new set]                              |
+--------------------------------------------------------------------------+
```

For a new Blank set, the analogous empty state says `No command files yet` and offers
`Add command`; it is editable and does not use the system-protected treatment.

## Screen H — Loading, filtered-empty and load error

### Loading

```text
+------------------------------+--------------------------------------------------+
| [search skeleton__________]  | [title skeleton____________________]             |
| [row skeleton_____________]  | [tabs skeleton_____________________]             |
| [row skeleton_____________]  | [content skeleton______________________________] |
| [row skeleton_____________]  | [content skeleton______________________________] |
+------------------------------+--------------------------------------------------+
```

Skeletons preserve the final pane sizes to prevent layout shift.

### Filtered empty

```text
+------------------------------+
| [⌕ megafon_kazan__________]  |
|                              |
| No matching command sets     |
| [Clear search]               |
+------------------------------+
```

### Load error

```text
+--------------------------------------------------------------------------+
| [error Fugue icon] Command sets could not be loaded                      |
| Demo data was not changed.                              [Retry] [Reset]  |
+--------------------------------------------------------------------------+
```

## Screen I — Narrow responsive layout

At widths below approximately 900px the two panes stack. The registry becomes a compact,
single-row set switcher; it does not consume half the viewport height.

```text
+--------------------------------------------------------------+
| Command sets                                  [Reset] [＋ Add]|
| 10 sets · 82 commands · 51 parsers                           |
|--------------------------------------------------------------|
| [⌕ Search______________________________________________]      |
| [MegaFon icon] megafon_spb · St Petersburg · 11/8       [▼] |
|--------------------------------------------------------------|
| MegaFon · Saint Petersburg                     [···]         |
| [Overview] [Commands 11] [Parsers 8] [Groups]                |
|--------------------------------------------------------------|
| [⌕ Files______________] [＋] [get_balance.sh             ▼] |
| Shell · Active · /commands/get_balance.sh                    |
|--------------------------------------------------------------|
|  1  #!/bin/sh                                                |
|  2                                                           |
|  3  . /usr/simbox/config.sh                                  |
|  4  ...                                                      |
|                                                              |
|--------------------------------------------------------------|
| [Cancel]                                              [Save] |
+--------------------------------------------------------------+
```

- Below 900px, the registry dropdown opens as a bounded list anchored under the switcher.
- File list becomes a file selector; source editor gets the remaining vertical space.
- Below 560px, tab labels remain (four short words fit via internal tab scrolling); icons do not
  replace essential meaning.
- Save/Cancel forms a sticky bottom action row when the detail header can no longer hold them.

## Interaction flows

### Browse and edit

```text
[Command sets]
      |
      v
[Select set] --> [Overview] --> [Commands / Parsers / Groups]
                                      |
                                      v
                                  [Edit draft]
                                  /          \
                           [Cancel]          [Save]
                              |                 |
                              +------> [Saved overview/tab + toast]
```

Changing the selected set while dirty does not discard work silently:

```text
[Dirty draft] --select another set--> [Keep editing | Discard changes]
```

### Create

```text
[Add set] --> [Clone existing | Blank] --> [Identity + review] --> [Created set selected]
                  ^                                |
                  +------------- Back -------------+
```

### Delete

```text
[Delete]
    |
    +-- default ------------> [Protected explanation]
    |
    +-- referenced ---------> [Usage list; deletion blocked]
    |
    +-- unreferenced -------> [Confirmation] --Delete--> [Next registry row selected]
                                      |
                                    Cancel
                                      v
                                [Original set]
```

## Visual system

| Element | Visual rule |
|---|---|
| Page background | `#F8F9FA` |
| Workspace/detail surfaces | white, 10px radius, single soft card shadow |
| Primary CTA | blue `#00C6FB -> #005BEA` gradient; only one gradient CTA per state |
| Selected row/tab | brand tint, foreground `#303F49`, not a second shadow |
| Success/warning/danger | `#1FB67A` / `#FFB020` / `#E5484D`, always paired with icon + text |
| UI type | SF Pro Text; 20/600 screen title, 13–15px working text |
| Source type | SF Mono/ui-monospace, 12/18px, tabular line numbers |
| Spacing | 4px grid; 8/12/16/20/24/32px; working panes favor 8–12px density |
| Icons | Fugue at 16 logical px: original 16×16 at 1× and paired 32×32 at 2×; no 48px tier |
| Motion | 180–250ms, no bounce; pane selection does not animate spatially |
| Focus | 2px brand-tinted focus ring; complete keyboard traversal |

## Accessibility and copy

- Status and validation never rely on color alone.
- Icon-only controls have tooltips and accessible names; destructive actions retain text labels.
- Minimum interactive target is 32px in the dense desktop editor and 40px in the narrow layout,
  while the visible Fugue glyph remains 16 logical px.
- Icon-led font, line-height, gap, padding and row tokens stay proportional to the shared 16px
  logical icon unit. Retina changes the physical source to 32×32, not the CSS box to 32px.
- Density pairs use `srcset`/equivalent 1× and 2× selection with no `image-rendering: pixelated`;
  there is no 48×48 asset tier because padded PSD canvases are not a third resolution.
- Russian-first labels use sentence case and concise wording; other configured app languages use
  the same semantic keys. Stable IDs, filenames and source code are never translated.
- No emoji, no decorative illustrations and no syntax-colored source in the first prototype;
  legibility and accurate file content take priority.

## Visual decisions to approve

- [x] Master-detail proportions and persistent registry context.
- [x] Four stable tabs with file-list + source-editor treatment for Commands/Parsers.
- [x] Two-step inline creation flow with Clone recommended.
- [x] Inline blocking explanation for protected/referenced sets; modal only for executable delete.
- [x] Stacked responsive layout with compact set/file selectors and sticky Save/Cancel.

---

## Approval

- [x] Reviewed by: Anton Dodonov
- [x] Approved on: 2026-09-01
- [x] Notes: approved with `approved` before the corrected target-path invocation.

## Visual Amendment 1.1 — Workflow and Response-Rule Builder

This amendment supersedes Screen B, Screen C, all source-editor responsive behavior and the
second checked visual decision above. The registry, Overview, Groups, creation and safe-delete
patterns remain valid. Updated tabs are **Overview**, **Commands**, **Response rules** and
**Groups & limits**.

### Revised Screen B — Command workflow

```text
+--------------------------------+------------------------------------------------------------------+
| Registry                       | MegaFon · Saint Petersburg    Draft changed  [Cancel] [Save] |
|                                | [Overview] [Commands 11] [Response rules 7] [Groups & limits]|
| ● megafon_spb          ACTIVE |------------------------------------------------------------------|
|   MegaFon · St Petersburg     | [Get balance                 ▼] [Duplicate] [Delete]          |
|                                | Gets the current balance via USSD              Migrated      |
|                                |------------------------------------------------------------------|
|                                |  1  Send USSD                                             [⋮] |
|                                |     Code  `*100#`     Queue  `LOC`                          |
|                                |                                                      [drag]  |
|                                |  2  Wait for response                                    [⋮] |
|                                |     Timeout  30 seconds · then apply “Balance response”       |
|                                |                                                      [drag]  |
|                                |                                                                  |
|                                | [+ Add step]       Parameters: Dongle, IMSI          [Test data]|
+--------------------------------+------------------------------------------------------------------+
```

- The command selector lists semantic slots, not files. Slot status is Migrated, Needs review
  or Needs migration with text and Fugue glyph.
- Each step is a compact, reorderable disclosure card. The collapsed sentence is meaningful on
  its own; opening it reveals only fields applicable to that step type.
- `Add step` opens a finite menu grouped as Communication, State & data and Flow. Unsupported
  arbitrary code cannot be pasted.
- Dependency steps link to the named command they invoke. Deleting a referenced command is
  blocked with the same inline impact treatment used for set deletion.

### Revised Screen C — Response rules

```text
+------------------------------------------------------------------------------------------------+
| Response rules                                                    Draft changed [Cancel] [Save]|
| [⌕ Search rules] [Channel: All ▼]                                      [+ Add response rule]  |
|------------------------------------------------------------------------------------------------|
| ≡  Balance response · USSD                         Migrated   Enabled                   [⋮] |
|    WHEN  text matches regex  `(?:Balance|Баланс)[: ]+([0-9,.]+)`                         |
|    TAKE  capture 1  → decimal number                                                       |
|    SAVE  Balance                                                                          |
|------------------------------------------------------------------------------------------------|
| ≡  Low balance · SMS                              Needs review  Enabled                   [⋮] |
|    WHEN  text contains “insufficient funds”                                                  |
|    SAVE  Group → Low balance                                                                 |
|------------------------------------------------------------------------------------------------|
| [Test a sample response]                                                                        |
| | Your balance: 127,45 RUB_______________________________________________________________ |    |
| Matched: Balance response   Extracted: `127,45`   Result: Balance = 127.45        [No writes] |
+------------------------------------------------------------------------------------------------+
```

- The default collapsed rule is a three-line WHEN / TAKE / SAVE summary.
- Regular expression is under **Advanced match**. A live sample tester highlights the capture
  and displays typed outcomes, making regex a testable matching tool rather than exposed PHP.
- Reordering changes rule priority. Disabled rules remain visible. An invalid rule cannot be
  saved and never falls through as if it succeeded.

### Revised Screen D — Groups & limits addition

The approved group cards remain. Beneath them, structured policies cover the limit/counter logic
found in maintenance scripts:

```text
| Limit policies                                                        [+ Add policy] |
| If current group is [Work ▼]  set [Daily call limit ▼] to [5960]       [⋮] |
| If current group is [Reserve ▼] set [SMS counter ▼] to [0]             [⋮] |
```

Only audited typed fields and conditions are selectable. A policy with behavior that cannot be
represented is labelled Needs migration rather than converted to a free-form expression.

### Responsive behavior

- At desktop width, registry and detail remain side-by-side; workflows/rules use the full detail
  width without an inner code-editor split.
- Below 900px, the registry becomes the approved compact selector and step/rule cards stack.
- Below 560px, each WHEN / TAKE / SAVE line wraps independently; step actions move into the
  overflow menu and Save/Cancel remains a sticky bottom row.
- Normal labels use SF Pro Text. Only literal codes, regex, templates and sample values use the
  monospaced stack.

### Amendment decisions to approve

- [x] Replace Shell/PHP editing with finite semantic command steps.
- [x] Rename Parsers to Response rules and use WHEN / TAKE / SAVE rule cards plus sample tester.
- Superseded by Amendments 1.3–1.4: group and limit maintenance belongs outside Command Sets.
- Superseded by Amendment 1.6: migration audit belongs outside the operational UI.

## Visual Amendment 1.2 — USSD Sequence Card

For an interactive USSD command, the generic step cards from Amendment 1.1 are replaced by a
compact dialog-sequence editor. Legacy sleeps are not shown.

```text
+----------------------------------------------------------------------------------+
| Enable outgoing calls                                             Migrated       |
| Interactive USSD dialog                                                          |
|----------------------------------------------------------------------------------|
|  1  START     Send  `*105*0082#`                                  [duplicate] [⋮]|
|     Initial request to operator                                                   |
|                                      |                                           |
|                                      v operator response                         |
|  2  REPLY     Send  `1`                                            [duplicate] [⋮]|
|     Select menu item                                                             |
|                                      |                                           |
|                                [+ Add reply]                                     |
|----------------------------------------------------------------------------------|
| Dialog execution and response handling will be configured by the runtime later.  |
+----------------------------------------------------------------------------------+
```

- Reorder handles appear when there are three or more replies; Start remains first.
- `Add reply` adds a USSD reply payload, not a timer or arbitrary workflow action.
- A small transcript preview may show `SIM → operator` direction, but it must not fabricate an
  operator response or imply that the dialog is executable in the prototype.
- Literal payloads use the monospaced stack; labels and descriptions remain normal UI text.
- On narrow screens, the ordinal, Start/Reply badge and payload stay on the first line; secondary
  actions collapse into the overflow menu.

### Amendment 1.2 visual approval

- [x] Replace legacy delay steps with visual USSD Start/Reply sequences.
- [x] Keep runtime response/timing mechanics outside the current prototype.

## Visual Amendment 1.3 — Transition Failover, Not a Wait Step

> Added from domain-owner clarification on 2026-09-01.

The sequence remains visually compact. Fallback is disclosed under the reply transition, without
adding a third `Wait` card:

```text
+----------------------------------------------------------------------------------+
| Enable outgoing calls                                                           |
|----------------------------------------------------------------------------------|
|  1  START   `*105*0082#`                                                        |
|                   |                                                              |
|                   | Continue after operator response                             |
|                   | Failover after [ 7 ] seconds                         [on]    |
|                   v                                                              |
|  2  REPLY   `1`                                                                  |
|                                                                    [+ Add reply] |
+----------------------------------------------------------------------------------+
```

- `Failover after` is an optional compact row in the connector/disclosure between steps.
- The UI does not show or store a generated `*105*0082#WWWWWWW1` string as the primary model.
- No success animation or simulated response is shown because executor behavior is deferred.
- The updated tab row is **Overview · Commands · Response rules · Groups**; limit/counter policy
  controls are removed from this workspace.

### Amendment 1.3 visual approval

- [x] Show fallback as a transition property between USSD steps.
- [x] Remove Limits and daily counters from the Command Sets workspace.

## Visual Amendment 1.4 — Three-Tab Command-Set Workspace

> Added from domain-owner clarification on 2026-09-01.

The command-set detail header now contains only:

```text
[Overview] [Commands 9] [Response rules 8]
```

Response-rule outcomes use semantic badges and Plan ownership disclosure:

```text
| Low balance response                                                     |
| WHEN  balance is below threshold                                         |
| EMIT  [Low balance]                                                       |
|                                                                          |
| Numeric group is selected by the assigned Plan.              [Open Plan] |
```

No group-number fields or group-comparison table appear in Command Sets. Current group display
and manual `Set group` remain SIM operations; Plan lifecycle mappings are designed in the Plan
workspace, outside this feature.

### Amendment 1.4 visual approval

- Superseded by Amendment 1.5: Overview is replaced by a persistent metadata header.
- [x] Show semantic outcomes with a link to the owning Plan instead of numeric group inputs.

## Visual Amendment 1.5 — Persistent Header and Two Sections

> Added after reviewing the information architecture with the domain owner on 2026-09-01.

The Overview tab is removed. The selected command set keeps a compact identity header above both
working sections:

```text
+----------------------------------------------------------------------------------+
| MegaFon · Saint Petersburg                         [Migrated] [Edit] [More ⋮]  |
| megafon_spb  •  Russia / Saint Petersburg  •  Used by 2 Plans        [Plans] |
|----------------------------------------------------------------------------------|
| [Commands 9]                         [Response rules 8]                          |
|----------------------------------------------------------------------------------|
| Current section content                                                          |
+----------------------------------------------------------------------------------+
```

- The first line carries the human-readable identity and compact actions.
- The second line carries stable ID, geographic scope and Plan usage; low-priority values may
  collapse into a metadata disclosure on narrow screens.
- Migration status is actionable and opens details, but does not become another primary section.
- The two section controls remain in the same position and do not replace or shift the header.
- Selecting another set opens Commands by default; section counts help compare the imported
  legacy coverage without adding a dashboard.
- On narrow screens the title/status/action line remains visible, overflow actions move behind
  the Fugue menu icon, and the two sections occupy an equal-width segmented row.

For the protected fallback:

```text
| Default fallback                                             [System] [Clone] |
| default  •  All operators  •  Used when no specific set is assigned           |
| [Commands 0]                                      [Response rules 0]          |
| No explicit commands in the system fallback.              [Create from copy] |
```

### Amendment 1.5 visual approval

- [x] Remove Overview and keep its useful information in the persistent header.
- [x] Make Commands the default section and Response rules the only peer section.

## Visual Amendment 1.6 — Remove Migration Status from the Workspace

> Added after domain-owner review on 2026-09-01.

The technical migration badge and its details panel are removed. The normal header is:

```text
+----------------------------------------------------------------------------------+
| MegaFon · Saint Petersburg                                  [Edit] [More ⋮]  |
| megafon_spb  •  Russia / Saint Petersburg  •  Used by 2 Plans        [Plans] |
|----------------------------------------------------------------------------------|
| [Commands 9]                         [Response rules 8]                          |
+----------------------------------------------------------------------------------+
```

An invalid editable item shows a local message attached to the field or card:

```text
| 2  REPLY   [                    ]                                                |
|            Reply payload is required.                                           |
```

There is no Migrated/Legacy/Needs migration badge, migration filter or migration drawer in the
registry or editor. Import coverage is verified outside the operational interface.

### Amendment 1.6 visual approval

- [x] Remove all migration-state UI from Command Sets.
- [x] Show only local, actionable validation in the editor.
