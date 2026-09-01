# Visual Mockups: simbox-web-design-prototype-fix2-uiux

> Version: 1.0
> Status: APPROVED
> Last Updated: 2026-09-01

## Overview

ASCII mockups for the reworked toolbar row (action rail + filter + columns, one row, never
covering/shifting the table) and the inline column-management editor. Adapted from the
interaction pattern in `design/simbox-design-prototype-v2026-beta1` (`.toolbar`/`.action-rail`/
`.columns-inline`), restyled to the fix1 shell (sidebar + sticky table already in place) and the
`-dc` visual language (brand-tint pills, `T.radiusCtl`, `T.shadow`).

---

## Screen: Sims toolbar — idle (all pills collapsed)

```
+-----------------------------------------------------------------------------+
| Симки  Всего:128  Выбрано:3 | [Передатчик v][Простые v][Хитрые v]           |
|                              [Группы и планы v][Экспорт v] |  [filter][Обновить]|
+-----------------------------------------------------------------------------+
| [ ] group cap im ... (sticky header, unchanged from fix1)                   |
|-------------------------------------------------------------------------------|
| [ ] row 1 ...                                                                |
| [ ] row 2 ...                                                                |
```

One row: title/count/selection-chip + pills on the left (scrolls sideways if it doesn't fit),
filter + Columns icon + Обновить pinned right. Same as fix1's idle state, now explicitly a
single non-wrapping row (fix1 already used `Wrap`+`Expanded`; this flow drops the `Wrap` in
favor of a horizontally-scrolling rail so it truly never wraps to a 2nd line).

## Screen: Sims toolbar — Rule A group open ("Действия хитрые", all zero-field → flat strip)

```
+-------------------------------------------------------------------------------+
| Симки Всего:128 [<] [wake][sleep][clear IMB][clear IMN][retry SMS][...more>] | [filter][Обновить]
+-------------------------------------------------------------------------------+
| [ ] group cap im ...                            <- table header, untouched   |
```

`[<]` = cancel/back icon-button, collapses to idle. Every "Действия хитрые" button is directly
clickable — no dropdown, since none of them take input. If the strip is wider than the
available row, it scrolls sideways within the rail (`[...more>]` hints at overflow, not a
literal button) — filter/Обновить on the right never move.

## Screen: Sims toolbar — Rule B group open ("Действия простые", mixed fields → dropdown)

```
+-------------------------------------------------------------------------------+
| Симки Всего:128 [<] [USSD, SMS, Звонок v] USSD: [*100#______] [Отправить]    | [filter][Обновить]
+-------------------------------------------------------------------------------+
```

Dropdown defaults to the first action ("USSD"); only its field(s) + run button show. Selecting
"SMS" in the dropdown swaps the row's content in place:

```
| Симки Всего:128 [<] [USSD, SMS, Звонок v] SMS: [номер___][сообщение________] [SMS]         |
```

Selecting "Звонок" shows the shared number field with **two** run buttons (Call60/CallSpeak are
two outcomes of the same input — kept as two buttons rather than forcing an awkward 4th dropdown
entry for what fix1 already treats as one field with two actions):

```
| Симки Всего:128 [<] [USSD, SMS, Звонок v] Звонок: [89261112233___] [Call60][CallSpeak]      |
```

## Screen: Sims toolbar — Rule B group open ("Передатчик и статус", with group-level settings)

```
| Симки Всего:128 [<] [ВКЛ,ВЫКЛ,Пауза,В работу v] [ВКЛ] | (·)очередь Задержка[0]+до[0]сек     |
```

The dropdown here still lets you pick which of the 4 to run (each is a single click, no fields
of its own — matches Rule B because the *group* has shared settings even though individual
actions don't have per-action fields); "в очередь" checkbox + delay/random fields are
group-level, shown regardless of which action is selected, positioned after a separator.

## Screen: Diagmode toolbar — Rule C group open ("Перепрошивка", single action)

```
| Свистки (um) Всего:2 [<] (·)Автообновление  [Отправить в diagmode]           | [filter][Обновить]
```

No dropdown — there's only one action in this group, so the pill expands straight to its
controls (checkbox setting + the one Run button).

## Screen: Sims toolbar — Columns editor open

```
+-------------------------------------------------------------------------------+
| Симки Всего:128 [<][Reset] [<>group][<>cap][<>im][<>spec][<>io][<>напр][...>]| [filter][Обновить]
+-------------------------------------------------------------------------------+
```

Each `[<>label]` is a column chip: checkbox (checked = visible) + label + two tiny move arrows.
Unchecking hides the column immediately in the table below; move arrows swap it with its
neighbor in the order. Opening Columns closes any open action group (mutually exclusive with
the rail's other two states). `[Reset]` restores the table's default column set/order.

### Column chip detail

```
+-----------------------------+
| [x] balance        [<][>]   |   <- visible, movable both ways
| [x] number          [ ][>]  |   <- visible, at the start (no move-left)
| [ ] IMEI            [<][>]  |   <- hidden (unchecked), still reorderable
| [x] ✓ (select)      —  —    |   <- non-hideable, non-reorderable, not in the chip list at all
+-----------------------------+
```

(The `select` checkbox column is excluded from the chip list entirely — fixed at position 0,
per the Open Question's proposed default.)

## Screen: Narrow window — icon-only responsive fallback

```
+-------------------------------------------------------------------+
| Симки 128 [⚡][✉][🔧][📋][📤] |  [🔍_____][⚙]  [Обновить]          |
+-------------------------------------------------------------------+
```

Below the width breakpoint: pills lose their text labels (icon-only, tooltip still carries the
label), selection chip hides first if still tight, filter input narrows. Row height is
unchanged — this is purely a label/width adjustment, not a wrap.

### Narrow window — Rule B group open, icon-only mode

```
| Симки 128 [<] [v] USSD:[*100#___] [➤]  |  [⚙] [Обновить]           |
```

Dropdown and run button also go icon-only (dropdown shows just a caret, run button shows just
its action icon) — labels return via tooltip on hover/focus, matching the idle-pill fallback.

---

## Flow: Opening and closing rail states

```
[Idle pills] --(click group pill)--> [Group open: Rule A/B/C] --(click same pill / [<] / Esc)--> [Idle pills]
[Idle pills] --(click Columns)-----> [Columns editor] --(click Columns / [<] / Esc)------------> [Idle pills]
[Group open] --(click Columns)-----> [Columns editor]   (closes the group automatically)
[Columns editor] --(click a pill)--> [Group open]        (closes columns automatically)
```

Exactly one of {idle, one open group, columns editor} occupies the rail at any time — same
`AppState`-single-active-state pattern fix1 already uses for `activeGroup`, extended with a
`columnsOpen` flag that's mutually exclusive with it.

---

## Component: Action-group pill (unchanged visual from fix1)

```
Closed:  [ (icon) Простые  v ]   outline, muted text, chevron down
Open:    [ (icon) Простые  ^ ]   brand-tint fill, brand text, chevron up
```

## Component: Rail cancel/back icon-button

```
[ < ]   16px icon-only button, always the first element of an open group/columns editor
```

## Component: Column chip

```
[x] label [<][>]     checkbox + label + move-left + move-right, ~30px tall, outline border
```

---

## Notes

- This is a pure toolbar/table-header rework; the sticky `DenseTable` body, the sidebar, the
  status bar, and `CommandLog` from fix1 are all unchanged and not re-mocked here.
- Every ASCII state above must render inside the *same row* — the row's height must stay
  constant across idle/open-group/columns-editor/responsive states; only its horizontal content
  and the visibility of text labels change.
- Diagmode/Hubs mockups follow the same component vocabulary as Sims/Dongles; not fully redrawn
  above since Diagmode has 1 group (Rule C, shown) and Hubs has 1 all-zero-field group (Rule A,
  same shape as the "Действия хитрые" mockup above with Hubs' 3 buttons instead).

---

## Approval

- [x] Reviewed by: Anton Dodonov
- [x] Approved on: 2026-09-01
- [x] Notes: Approved alongside requirements.
