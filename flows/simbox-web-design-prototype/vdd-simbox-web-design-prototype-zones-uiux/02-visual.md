# Visual Mockups: simbox-web-design-prototype-zones-uiux

> Version: 2.0
> Status: APPROVED
> Last Updated: 2026-09-02

## Overview

ASCII mockups for the new "Направления (DEF коды)" section — a registry-pane + detail-pane
workspace mirroring `lib/features/command_sets/`'s already-implemented layout. Iteration 1
(shipped) has a single-textarea detail body. Iteration 2 (this amendment) adds a second section
below it: an ordered, editable list of group-selection rules.

---

## Screen: Zones workspace — wide layout, zone selected

```
+--------+------------------------------------------------------------------------+
|SIDEBAR |  Направления (DEF коды)                                                |
| ...    +------------------------------------------------------------------------+
|[x]Напр.|                                                                        |
| ...    |  +------------------+  +------------------------------------------+   |
|        |  |Направления   [+] |  | (icon) МегаФон СПб            [pencil][≡]|   |
|        |  |[search_______]   |  | megafon_spb · СПб                        |   |
|        |  |------------------|  +-------------------------------------------+   |
|        |  |(ico)МегаФон СПб  |  |                                            |  |
|        |  | megafon_spb·СПб  |  |  DEF-коды (20)                             |  |
|        |  |            20/-  |<-|  +--------------------------------------+ |  |
|        |  |------------------|  |  |792109XXXXX                          | |  |
|        |  |(ico)МегаФон Мск  |  |  |7921111XXXX                          | |  |
|        |  | megafon_msk·Мск  |  |  |792118XXXXX                          | |  |
|        |  |           137/-  |  |  |79213XXXXXX                          | |  |
|        |  |------------------|  |  |79214[0-4]XXXXX                      | |  |
|        |  |(ico)Билайн СПб   |  |  |...                                   | |  |
|        |  | beeline_spb·СПб  |  |  |                                      | |  |
|        |  |            54/-  |  |  +--------------------------------------+ |  |
|        |  |------------------|  |  Каждый код — новая строка. Пустые строки |  |
|        |  |... (19 total)    |  |  игнорируются.                            |  |
|        |  +------------------+  +--------------------------------------------+ |
+--------+------------------------------------------------------------------------+
```

Left registry pane: search box, "+" add button, one row per zone (icon, name, id·region,
code count), selected row highlighted. Right detail pane: header (icon, name, id·region,
edit-metadata pencil, "⋮" menu for clone/delete), then the single DEF-code textarea with a live
count and hint text. No save bar visible yet — nothing edited.

## Screen: Zones workspace — unsaved edit (draft bar appears)

```
|  +------------------------------------------------------------+ |
|  |792109XXXXX                                                  | |
|  |7921111XXXX                                                  | |
|  |NEWPATTERNXXXX          <- operator typed a new line          | |
|  |...                                                            | |
|  +----------------------------------------------------------------+ |
|  (i) Есть несохранённые изменения        [Отмена] [Сохранить]      |
+------------------------------------------------------------------+
```

Matches Наборы команд's `_DraftBar` exactly: info icon + message, Cancel discards back to the
saved value, Save (gradient button) commits — replaces the whole code list per Acceptance
Criteria #5.

## Screen: Zone detail — with group-selection rules (Iteration 2)

```
+-------------------------------------------------+
| (icon) МегаФон СПб                     [pencil][≡]|
| megafon_spb · СПб · код: NS                       |
+-------------------------------------------------+
|  DEF-коды (20)                                     |
|  +---------------------------------------------+  |
|  | 792109XXXXX                                  |  |
|  | ...                                          |  |
|  +---------------------------------------------+  |
|                                                     |
|  Правила выбора группы (4)          [+ добавить]   |
|  +---------------------------------------------+  |
|  | # | L  | alg | type | группа |            |  |
|  |---|----|-----|------|--------|------------|  |
|  | 1 |[1v]|[Dv] |[=v]  |[101__] | [^][v][x]   |  |
|  | 2 |[3v]|[>v] |[_v]  |[102__] | [^][v][x]   |  |
|  | 3 |[3v]|[>=v]|[_v]  |[162__] | [^][v][x]   |  |
|  | 4 |[1v]|[Dv] |[=v]  |[205__] | [^][v][x]   |  |
|  +---------------------------------------------+  |
|                                                     |
|  (i) Есть несохранённые изменения [Отмена][Сохранить]|
+-------------------------------------------------+
```

Each row: limit-slot dropdown (0-9), algorithm dropdown (raw letters `D ^ * > <`, per Open
Questions), type dropdown (raw `= - _`), a free-text group-number field, then move-up/move-down/
delete icon buttons (`^`/`v`/`x`) — same move-arrow visual language as fix2's `ColumnsEditor`
chips. Order is the fallback priority (row 1 tried first). Adding, editing, reordering, or
deleting a rule dirties the same per-zone draft as the DEF-code textarea — one Save/Cancel bar
governs both sections together (Acceptance Criteria #11-14).

## Screen: Zone detail — empty group-rules list (e.g. `beeline_sz`, never wired up in legacy)

```
|  Правила выбора группы (0)          [+ добавить]   |
|  +---------------------------------------------+  |
|  |     Правил пока нет. Нажмите «+ добавить».   |  |
|  +---------------------------------------------+  |
```

Same "incomplete on purpose, now fixable" framing as an empty DEF-code list.

## Screen: Create zone dialog

```
+----------------------------------------+
|  Новое направление                       |
|  ID (латиницей, уникальный)              |
|  [____________________]                 |
|  Название                                |
|  [____________________]                 |
|                                          |
|              [Отмена]   [Создать]        |
+----------------------------------------+
```

New zone starts with an empty DEF-code list, becomes selected immediately after creation
(matches command sets' `showCreateSetDialog` pattern).

## Screen: Delete confirmation

```
+----------------------------------------+
|  Удалить направление?                    |
|  «Билайн СПб» (beeline_spb) будет         |
|  удалено вместе со всеми 54 кодами.       |
|              [Отмена]   [Удалить]        |
+----------------------------------------+
```

No "system zone" exception (unlike command sets) — every zone, including imported ones, can be
deleted after this confirmation.

## Screen: Empty registry (search matches nothing)

```
+------------------+
|Направления   [+] |
|[xyz___________]  |
|-------------------|
|                   |
|  Направления не    |
|  найдены          |
|                   |
+------------------+
```

## Screen: Narrow window — stacked layout

```
+--------------------------------------------------+
| (ico) [Направления            v] [+]              |   <- compact registry pane
+--------------------------------------------------+
|  (icon) МегаФон СПб                    [pencil][≡]|
|  megafon_spb · СПб                                |
|------------------------------------------------------|
|  DEF-коды (20)                                     |
|  +-----------------------------------------------+ |
|  |792109XXXXX                                     | |
|  |...                                              | |
|  +-----------------------------------------------+ |
+--------------------------------------------------+
```

Below the responsive breakpoint (matches command sets' `narrow = constraints.maxWidth < 900`):
registry pane collapses to a single row — dropdown of zone names + "+" button — detail pane
takes the rest of the vertical space, same as `CommandSetsWorkspace`'s narrow branch.

---

## Flow: Editing a zone's codes

```
[Zone list] --(click a zone)--> [Detail: saved state] --(edit textarea)--> [Detail: dirty, draft bar shown]
                                        ^                                          |
                                        |______________(Сохранить)_________________|
                                        |______________(Отмена)_____________________|
```

### Step-by-Step

1. **Zone list**: operator clicks a zone row → detail pane loads that zone's metadata + codes.
2. **Detail, saved state**: textarea shows the current codes, one per line, no draft bar.
3. **Operator edits**: adds/removes/reorders lines → draft bar appears (dirty).
4. **Сохранить**: text re-split into a trimmed, non-empty-line list → zone's `defCodes` replaced
   → draft cleared, count updates, bar disappears.
5. **Отмена**: textarea reverts to the last-saved value, draft cleared, bar disappears.

## Flow: Switching zones with unsaved edits

Same guard as command sets: attempting to select a different zone while dirty prompts
"Сохраните текущее направление или отмените изменения перед переключением" with
Continue-editing / Discard-and-switch options.

---

## Component: Registry row

```
(icon) Zone name              <- bold if selected
zone_id · region                     N/–     <- code count (no second number, unlike
                                                  command sets' "commands/rules" pair)
```

## Component: DEF-code textarea

```
DEF-коды (N)
+----------------------------------------+
| pattern1                                 |
| pattern2                                 |
| ...                                      |  <- scrolls internally if content overflows
+----------------------------------------+
Каждый код — новая строка. Пустые строки игнорируются.
```

---

## Notes

- No tabbed sections (unlike command sets' Команды/Правила ответов `SegmentedButton`) — a zone's
  two editable bodies (DEF-codes, group-rules) stack vertically in one scrollable detail pane
  rather than living behind a tab switch; both are short enough to coexist without needing to be
  hidden from each other, and they share one draft/save cycle anyway.
- Icon reuse: registry rows and the detail header use `Ico.napr`-equivalent icon resolution
  (`assets/imgs/napravleine/<id>.png`, falling back to `hz.png`) — visually consistent with the
  Sims table's existing `напр` column.
- Sidebar gets one new item, "Направления," positioned after "Наборы команд" (Open Question in
  01-requirements.md — confirm slot).

---

## Approval

**Iteration 1**: approved 2026-09-01, shipped.

**Iteration 2** (group-selection rules section, this amendment):
- [x] Reviewed by: Anton Dodonov
- [x] Approved on: 2026-09-02
- [x] Notes: Approved alongside requirements.
