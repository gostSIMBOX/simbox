# Visual Mockups: SimBox v2026 compact operations UI

> Version: 1.0  
> Status: APPROVED  
> Last Updated: 2026-09-01

## Visual direction

One production direction is shown: a dense desktop operations surface with a fixed-height
**Morphing inline action rail** immediately above each table. The table starts at the same vertical
coordinate in every action state. Wide legacy schemas remain complete and use their own horizontal
scroller; the page itself does not scroll sideways.

Legend used below:

- `[fg:name]` — 16px logical Fugue glyph with 16×16/32×32 density pair.
- `|>` — more columns continue inside the table scroller.
- `||` — pinned boundary; selection and minimum identity remain visible.
- `···` — compact representation of repeated legacy columns, never an omitted target column.
- right-justified samples represent default right alignment and monospace identifiers/numbers.

## Application frame — English, wide

```text
+----------------------------------------------------------------------------------------------+
| [NativeMind SimBox]  simbox-01 · Online                         [fg:globe] English v   [User] |
+----------------------+-----------------------------------------------------------------------+
| [fg:card] SIM cards  |  SIM cards                                            128 total       |
| [fg:plug] Lines      | +-------------------------------------------------------------------+ |
| [fg:chip] Programmer | | FILTER + SELECTION + MORPHING ACTION RAIL + TABLE CONTROLS         | |
| [fg:server] Hubs     | +-------------------------------------------------------------------+ |
| [fg:drive] Readers   | | COMPLETE LEGACY TABLE · pinned identity || horizontal data scroll | |
| [fg:script] Cmd sets | |                                                                   | |
| [fg:clock] Plans     | |                                                                   | |
| [fg:application-    | |                                                                   | |
|       task] Processes| |                                                                   | |
| [fg:money] Billing  | |                                                                   | |
| [fg:arrow-circle]   | |                                                                   | |
|       Update        | |                                                                   | |
| [fg:bug] Debug      | |                                                                   | |
| [fg:images] Icons   | +-------------------------------------------------------------------+ |
+----------------------+-----------------------------------------------------------------------+
```

The navigation glyph and label form one target. `Processes` uses Fugue `application-task.png`;
`Billing` uses Fugue `money.png`. No heart-like `conn.png` or broken `may.ico` appears here.

## Same frame — Russian locale

```text
| [NativeMind SimBox]  simbox-01 · В сети                         [fg:globe] Русский v [Польз.] |
| [fg:card] Симки      |  Симки                                                   Всего: 128   |
| [fg:plug] Линии      |
| [fg:chip] Программатор|
| [fg:server] Хабы     |
| [fg:drive] Ридеры    |
| [fg:script] Наборы команд
| [fg:clock] Планы     |
| [fg:application-task] Процессы
| [fg:money] Биллинг   |
| [fg:arrow-circle] Обновление
| [fg:bug] Отладка     |
| [fg:images] Иконки   |
```

Only one locale is visible at a time. Thai, Hindi and Chinese use the identical layout with their
own dictionary values; labels are never assembled as `Hubs (Хабы)`.

## Morphing inline action rail

The rail has three persistent zones. Its height is one compact control row in all states.

```text
          ZONE A: CONTEXT                  ZONE B: FLEXIBLE ACTION RAIL        ZONE C: TABLE
+-----------------------------------+--------------------------------------+------------------+
| [fg:magnifier] Filter...          |                                      |                  |
| [x] 3 selected                    | actions or one active editor         | [Columns] [↻]   |
+-----------------------------------+--------------------------------------+------------------+
  pinned                              replaces content in place              pinned
```

### Idle, rows selected

```text
+----------------------------------------------------------------------------------------------+
| [fg:magnifier] Filter SIM cards... | 3 selected | [fg:power] Power | [fg:card] SIM |          |
| [fg:phone] Calls | [fg:mail] SMS/USSD | [fg:gear] More        | [fg:table] Columns | [fg:↻] |
+----------------------------------------------------------------------------------------------+ <- fixed edge
| [x] || group | pro | cap | im | spec | state | plan | number | operator | balance | ... |>   |
```

Safe frequent groups have short text on wide containers. Zero-selection state disables only
selection-dependent controls and keeps page-level Refresh/Columns usable.

### Parameter editor replaces the middle rail

```text
+----------------------------------------------------------------------------------------------+
| [fg:magnifier] Filter... | 3 selected | [fg:arrow-180] SMS | To [____________] |             |
| Message [________________________] | [fg:tick] Send | [fg:cross] Cancel | Columns | [↻]      |
+----------------------------------------------------------------------------------------------+ <- same fixed edge
| [x] || group | pro | cap | im | spec | state | plan | number | operator | balance | ... |>   |
```

The table does not move or become covered. Input labels stay visible; placeholders are examples,
not replacements for labels.

### Inline validation

```text
| Filter... | 3 selected | SMS | To [____________ !]  [fg:exclamation] Number is required      |
|                              [Send disabled] [fg:cross] Cancel | Columns | [↻]               |
```

Error text occupies the reserved status segment; rail height is unchanged.

### Dangerous action confirmation

```text
| Filter... | 3 selected | [fg:exclamation] Power off 3 selected lines?                         |
|                         [fg:power] Confirm power off | [fg:cross] Cancel | Columns | [↻]      |
```

Danger is communicated by icon, wording and border/color, never by color alone. Harmless Refresh
does not pass through confirmation.

### Running, success and failure

```text
RUNNING | Filter... | 3 selected | [fg:hourglass] Sending SMS... 2/3 | [Cancel] | Columns | [↻]
SUCCESS | Filter... | 3 selected | [fg:tick] Sent to 3 SIM cards     | [Close]  | Columns | [↻]
ERROR   | Filter... | 3 selected | [fg:cross] 1 failed · [Details]  | [Retry]  | Columns | [↻]
```

Opening Details changes only the inline log area below the table card if that screen already has a
legacy result/log surface; the action editor itself never overlays table rows.

### Medium and compact widths

```text
MEDIUM
| [fg:magnifier] Filter... | 3 | [fg:power] [fg:card] [fg:phone] [fg:mail] [fg:gear] | [Cols] [↻] |

COMPACT
| [fg:magnifier] | 3 | < [fg:power] [fg:card] [fg:phone] [fg:mail] [fg:gear] > | [fg:table] [↻] |
                       internal rail scroll only

COMPACT EDITOR
| [fg:magnifier] | 3 | < [fg:arrow-180] PIN [____] [fg:tick] [fg:cross] > | [fg:table] [↻]       |
```

Every icon-only control has a localized tooltip, accessible name and visible focus ring. The filter
icon changes the same rail into a compact filter editor; it does not open over the table.

## Column management

Columns is a deliberate utility dialog, separate from command expansion. It does not reflow the
table and closes back to the Columns trigger.

```text
                         +--------------------------------------------+
                         | Columns · SIM cards              [x Close]|
                         | 41 / 41 visible                           |
                         | [Filter column names...]                  |
                         |--------------------------------------------|
                         | [lock] Selection       protected           |
                         | [lock] SIM identity     protected           |
                         | [x] [::] Group                 [up] [down] |
                         | [x] [::] Operator              [up] [down] |
                         | [x] [::] Balance               [up] [down] |
                         | ...every approved legacy column...         |
                         |--------------------------------------------|
                         | [Reset table] [Reset all]          [Done] |
                         +--------------------------------------------+
```

Unchecked columns disappear only after user action. Reset restores the complete approved legacy
order and makes all columns visible. Drag handle and keyboard up/down perform the same reorder.

## Table anatomy

```text
+------------------------------------------------------------------------------------------------+
| [x] || IDENTITY            |              ALL LEGACY COLUMNS, INITIAL/RESET VISIBLE          |> |
|-----||---------------------|------------------------------------------------------------------| |
| [ ] ||        dongle0      | ...                                  00000000084.20              |> |
| [x] ||        dongle1      | ...                                  00000000012.05              |> |
+------------------------------------------------------------------------------------------------+
  center   mono/right            icon=center · prose exceptions=left · values=right/mono
```

Header sort direction uses Fugue arrows plus accessible text. Header and row cells share one schema
definition. Pinned identity remains visible while the internal data region scrolls horizontally.

## Screen inventory

Every screen uses the common frame and rail. The sketches show structural differences; ellipses
mean horizontally continuing columns documented in the legacy manifest, not removed data.

### SIM cards / Симки

```text
| Filter | selected | Power | SIM | Calls | SMS/USSD | Plans | Data/KI | More | Columns | Refresh |
| [x] || group | pro | cap | im | spec | state | plan | number | operator | balance | ... LIMIT5 |> |
| [ ] ||   101 | ... all logical sim.php columns in legacy order ...                         |> |
```

This is the widest operational grid. The rail prioritizes frequent actions; less frequent legacy
commands remain in single-level groups and become the active inline editor when chosen.

### Lines / Линии

```text
| Filter | selected | Power | PIN | Network | IMEI | AT | More | Columns | Refresh |
| [x] || model | cfun | simst | srvst | Line | lock | state | ERR0 | ERR1 | ... | dev |> |
```

The four leading status/model slots remain separate. User-facing copy says Lines/Линии while raw
`dongle*` identifiers and commands remain unchanged.

### Programmer / Программатор

```text
| Filter | selected | Program | Log | Columns | Refresh |
| [x] || Device | Model | Firmware | [fg:status] State | Progress | Dataport |
| [ ] || dongle4| E173  | 11.126...| Updating            |     63% | ttyUSB7  |
```

### Hubs / Хабы — independent route

```text
| Filter hubs... | selected | Power on | Power off | Restart | Delay/Queue | Columns | Refresh |
| [x] | depth-0 | depth-1 | depth-2 | depth-3 | device/power | extra slot | Device text       | Address |
| [ ] |[fg:pci] |         |         |         |              |            | Bus 02...root_hub |      02 |
| [ ] |[tree]   |[fg:hub] |[fg:on]  |         |              |            | Port 1...Class=hub|  02:2:1 |
```

Nine logical columns are represented. The heading is Hubs in English and Хабы in Russian; no
Readers table or reader actions appear here.

### Readers / Ридеры — independent route

```text
| Filter readers... | selected | PIN | KI search | APDU | Columns | Refresh |
| [x] | Model | Reader | Lock | State | SPN | ICCID | PIN | IMSI | KI | Progress | Dataport |
| [ ] |[fg:usb]| rdr01 |      | Ready | MTS | 8970… |     |25001…|00  |  440/31044| ttyUSB2 |
```

All 12 verified `readers.php` columns are visible after Reset. PIN morphs into Remove/Set plus the
existing PIN inputs; APDU morphs into command input plus Execute. Hubs and Readers do not share a
schema file.

### Command sets / Наборы команд

```text
| Filter sets... | selected | Edit | Save | Columns | Refresh |
| [x] || Set name | Command count | Existing legacy fields ... |
```

### Plans / Планы

```text
| Filter plans... | selected | Create | Save | Groups | Columns | Refresh |
|      identity      |---- SATT ----|------ Directions 1..4 ------|---- IATT ----| ... |> |
| [x] Plan | enabled | icon/value...| alg | nodiff | soft | hard ...| all fields  | ... |> |
```

Multi-row/group headers visually span their child tracks, but every child remains an independently
mapped logical column. Horizontal group separators aid scanning without compressing fields.

### Processes / Процессы

```text
Navigation: [fg:application-task] Processes

| Filter actions... | [fg:broom] Clear SMS | [fg:arrow-circle] Restart software |              |
| [fg:plug] Find modems | [fg:power] Restart modems | [fg:server] Restart hubs | [Status slot] |
|----------------------------------------------------------------------------------------------|
| Command/result log — monospace, left aligned, existing legacy output only                    |
```

This command surface does not invent a fake process data grid. Each existing `proc.php` operation
uses its own audited Fugue action glyph; the navigation glyph is `application-task.png`.

### Billing / Биллинг

```text
Navigation: [fg:money] Billing

| Filter billing... | Columns | Refresh |
| Date | Code | Operator | Minutes | Money |
| 29.07|   TS | Tele2    |    14.1 |  0.00 |
|                         Total:   |  7.96 |
```

Money values are right-aligned with tabular numerals. `money.png` is the valid Fugue navigation and
context glyph; broken `may.ico` is not rendered.

### Update / Обновление

```text
| [fg:arrow-circle] Update code | [fg:compile] Recompile | [fg:power] Restart software | status |
|----------------------------------------------------------------------------------------------|
| command/result log                                                                           |
```

System-impacting commands use inline confirmation where legacy effect is destructive/disruptive.

### Debug / Отладка

```text
| Filter diagnostics... | Columns | Refresh |
| Key / source                         | Value / diagnostic output                             |
| /var/simbox/...                      | ...                                                   |
```

### Icons / Иконки

```text
| Filter icons... | Category v | Screen v | Verification v | Wishlist only [ ] | Columns |
| Preview | Meaning | Raw state | Usage | Legacy ref | 16×16 | 32×32 | Provenance | Status | Notes |
| [money] | Billing | route     | Nav   | bablo.php  |money.png|money.png|Fugue    |verified|       |
| [task]  |Processes| route     | Nav   | proc.php   |application-task.png|...|Fugue|verified|     |
| [?]     | needed… | ...       | ...   | ...        | —      | —      | wishlist |missing |terms…|
```

## Empty, loading and failure states

States live inside the table viewport so the toolbar and table geometry remain stable.

```text
LOADING
| headers remain visible                                                                            |
|                         [fg:hourglass] Loading Readers...                                          |

EMPTY DATA
| headers remain visible                                                                            |
|                  [fg:table] No readers found                         [Refresh]                     |

EMPTY FILTER RESULT
| headers remain visible                                                                            |
|              [fg:magnifier] No matches for "rdr99"                  [Clear filter]                |

LOAD ERROR
| headers remain visible                                                                            |
|          [fg:exclamation] Readers could not be loaded              [Retry] [Details]              |
```

No emoji or broken-image placeholder is used. Error/details copy follows the active locale.

## Navigation and interaction flow

```text
Application start
  --> English default
  --> SIM cards, complete legacy columns visible

Select locale
  --> dictionary changes for the entire UI
  --> same route, selection, sort and column state retained

Choose Hubs
  --> Hubs route / 9-column USB table / hub actions

Choose Readers
  --> Readers route / 12-column reader table / reader actions

Select rows --> choose action group --> rail morphs to editor
  --> validate --> optional confirmation --> run --> success/error --> return to idle rail

Columns --> utility dialog --> hide/reorder --> Done
  --> same table with persisted view
  --> Reset restores every approved legacy column
```

## Visual invariants for approval

- [x] One action-rail pattern, not three competing UI variants.
- [x] Filter and actions share one fixed-height row.
- [x] Active actions neither cover nor move the table.
- [x] Compact state keeps Fugue icons and accessibility names.
- [x] Every primary route has a represented structure.
- [x] Hubs and Readers are separate navigation destinations and schemas.
- [x] Readers shows all 12 verified columns; Hubs shows all 9 logical columns.
- [x] Complete legacy tables remain horizontally scrollable without default column loss.
- [x] Billing uses Fugue `money.png`; Processes uses `application-task.png`.
- [x] Locale examples never mix two languages in one runtime label.
- [x] Loading, empty, filtered-empty, validation, running, success and error states are shown.

---

## Approval

- [x] Reviewed by: user
- [x] Approved on: 2026-09-01
- [x] Notes: explicitly approved with `visual approved`
