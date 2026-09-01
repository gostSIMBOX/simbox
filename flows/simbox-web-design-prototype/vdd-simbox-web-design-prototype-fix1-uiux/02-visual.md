# Visual Mockups: simbox-web-design-prototype-fix1-uiux

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-09-01

## Overview

ASCII mockups for the new app shell: left sidebar (full ↔ compact via logo click), table
header-bar action-group pills opening an overlay panel, and a sticky table header. Adapted
from `design/simbox-design-prototype-v2026-dc/index.html`, which already implements this
pattern in HTML — these mockups translate it into the Flutter shell and confirm layout intent
before touching Dart.

---

## Screen: Sims page — sidebar FULL, no action panel open (default / happy path)

```
+--------+-------------------------------------------------------------------+
|[LOGO-W]| (power) simbox-a4   10.42.0.17   SimBox 8f3c1a2+     12:04:33  up |
| wide   +-------------------------------------------------------------------+
|--------|                                                                   |
|[x]Симки|  +-------------------------------------------------------------+  |
| Свистки|  | Симки   Всего: 128   [Передатчик v][Простые v][Хитрые v]   |  |
|  (nm)  |  |                      [Планы v][Экспорт v]  [__filter__][Обновить]|
| Свистки|  +-------------------------------------------------------------+  |
|  (um)  |  | [ ] group cap im spec io напр план number oper balance ... |<-sticky
|  Хабы  |  |-------------------------------------------------------------|  |
| Наборы |  | [ ] ..............row 1........................ ......... |  |
|  команд|  | [ ] ..............row 2........................ ......... |  ~
|  Планы |  | [ ] ..............row 3........................ ......... |  ~ scrolls
|Процессы|  | [ ] ..............row 4........................ ......... |  ~
|Биллинг |  | [ ] ..............row 5........................ ......... |  |
|Обновле-|  | ...                                                       |  |
|  ние   |  +-------------------------------------------------------------+  |
|  Debug |                                                                   |
| Иконки |                                                                   |
|--------+-------------------------------------------------------------------+
|        | (=) Вывод команд   0 записей          [Очистить] [Развернуть]     |
+--------+-------------------------------------------------------------------+
```

Legend: `[LOGO-W]` = `logo_wide_transparent.png` (~30px tall), sidebar is ~208px wide, item
labels shown, active item (`Симки`) highlighted (brand-tint background + checkmark placeholder
`[x]` = selected-state pill, not a literal checkbox).

## Screen: Sims page — sidebar COMPACT (icons only, after clicking logo)

```
+---+---------------------------------------------------------------------+
|[S]| (power) simbox-a4   10.42.0.17   SimBox 8f3c1a2+       12:04:33  up |
|---+---------------------------------------------------------------------+
|[#]|  +-------------------------------------------------------------+    |
|[#]|  | Симки   Всего: 128   [Передатчик v][Простые v][Хитрые v]   |    |
|[#]|  |                      [Планы v][Экспорт v]  [__filter__][Обновить]|
|[#]|  +-------------------------------------------------------------+    |
|[#]|  | [ ] group cap im spec io напр план number oper balance ... |<-sticky
|[#]|  |---------------------------------------------------------------|  |
|[#]|  | [ ] ..............row 1........................ ......... |    |
|[#]|  | [ ] ..............row 2........................ ......... |    ~
|[#]|  | ...                                                         |    |
|[#]|  +-------------------------------------------------------------+    |
|[#]|                                                                     |
+---+---------------------------------------------------------------------+
|   | (=) Вывод команд   0 записей          [Очистить] [Развернуть]       |
+---+---------------------------------------------------------------------+
```

`[S]` = `logo_transparent.png` (square, ~34×34), sidebar collapses to ~64px, `[#]` = one 16×16
nav icon per row, active item still has the tint background, no label text. Hovering/focusing
an icon shows a tooltip with the section label (accessibility — not drawn in ASCII).

## Screen: Sims page — one action-group panel open ("Передатчик" clicked)

```
+--------+-------------------------------------------------------------------+
|[LOGO-W]| (power) simbox-a4   10.42.0.17   SimBox 8f3c1a2+     12:04:33  up |
|--------+-------------------------------------------------------------------+
|[x]Симки|  +-------------------------------------------------------------+  |
|  ...   |  | Симки  Всего:128 Выбрано:3 [Передатчик ^][Простые v][... ]  |<-pill "Передатчик" OPEN (^)
|        |  |                                        [__filter__][Обновить]|
|        |  +-------------------------------------------------------------+  |
|        |  | +-----------------------------+                             |  |
|        |  | | (icon) Передатчик и статус  |   <- overlay panel, absolute|  |
|        |  | |-----------------------------|      positioned under the  |  |
|        |  | | [ВКЛ]        [ВЫКЛ]         |      header bar; does NOT  |  |
|        |  | | [Пауза]      [В работу]     |      push the table down   |  |
|        |  | | [ ] Вместо запуска — в очередь|                           |  |
|        |  | | Задержка [__] + случ.до [__] сек |                       |  |
|        |  | +-----------------------------+                             |  |
|        |  +-------------------------------------------------------------+  |
|        |  | [ ] group cap im spec io напр план number oper balance ... |<-STILL sticky, panel overlays it
|        |  |-------------------------------------------------------------|  |
|        |  | [x] ..............row 1 (selected, tinted)................ |  |
|        |  | ...                                                         |  |
+--------+-------------------------------------------------------------------+
```

Clicking the same "Передатчик" pill again, or clicking a different pill (e.g. "Простые"),
closes this panel / swaps to the other group's panel — only one group panel open at a time.
Reaching e.g. "ВКЛ" is: click pill (1) → click ВКЛ (2).

## Screen: page WITHOUT a table (e.g. Планы, Процессы, Обновление, Debug)

Unchanged from current prototype except for the new sidebar — these pages keep their existing
always-visible `Panel` layout (no header bar, no pills, nothing to declutter since there's no
competing table). See Open Question in requirements — confirmed as "leave as-is" pending
sign-off below.

```
+--------+-------------------------------------------------------------------+
|[LOGO-W]| (power) simbox-a4 ...                                    12:04:33 |
|--------+-------------------------------------------------------------------+
| Симки  |  Процессы                                                        |
| ...    |  +----------------------+                                        |
|[x]Проц.|  | (icon) Процессы      |                                        |
| ...    |  |----------------------|                                        |
|        |  | [restart action 1]   |                                        |
|        |  | [restart action 2]   |                                        |
|        |  | [Перезапуск ОС]      |                                        |
|        |  +----------------------+                                        |
+--------+-------------------------------------------------------------------+
```

### States

#### Empty selection (no rows checked)

Header bar shows no "Выбрано: N" chip; action-group pills are still present (groups act on the
*current filtered table*, not only selection, mirroring today's `st.runOnSelection` semantics
which already handle the empty-selection case in the existing code — no change needed there).

#### Sidebar hover on compact icon

```
   [#]  <- hover
    \
     +--------------+
     | Свистки (nm) |   <- tooltip, matches AdmIcon's existing tooltip pattern
     +--------------+
```

#### Narrow viewport (no dedicated breakpoint — Won't-Have)

Table gets horizontal scroll (already `min-width:max-content` in the -dc mock / existing
`DenseTable`); sidebar keeps its two fixed widths (64/208px) at all viewport sizes for this
iteration.

---

## Flow: Compact/full sidebar toggle

```
[Sidebar FULL, logo_wide]  --(click logo)-->  [Sidebar COMPACT, logo_square]
         ^                                              |
         |______________(click logo again)______________|
```

### Step-by-Step

1. **Sidebar FULL**: wide sidebar (~208px), `logo_wide_transparent.png`, nav items show
   icon + label, active item highlighted.
   - Action: user clicks the logo header area.
   - Result: sidebar animates/snaps to compact.

2. **Sidebar COMPACT**: narrow rail (~64px), `logo_transparent.png` (square), nav items show
   icon only, centered, tooltip-on-hover for the label.
   - Action: user clicks the logo again.
   - Result: back to FULL.

## Flow: Action-group panel open/close

```
[No panel open] --(click pill A)--> [Panel A open] --(click pill A again)--> [No panel open]
                                          |
                                    (click pill B)
                                          v
                                    [Panel B open, A closed]
```

---

## Component: Action-group pill (table header bar)

```
Closed:  [ (icon) Передатчик  v ]   <- outline border, muted text, chevron down
Open:    [ (icon) Передатчик  ^ ]   <- filled brand-tint bg, brand text, chevron up
```

## Component: Left sidebar nav item

```
FULL, idle:    [ (icon)  Свистки (nm)        ]   transparent bg, muted text
FULL, active:  [ (icon)  Симки                ]   brand-tint bg, brand text, semibold
COMPACT, idle: [ (icon) ]   centered, transparent bg
COMPACT,active:[ (icon) ]   centered, brand-tint bg
```

## Component: Sticky table header

```
+-------------------------------------------------------------+
| [ ] col1  col2  col3  col4  ...                              |  <- always visible (sticky)
|===============================================================|
| [ ] row .......................................              |  ^
| [ ] row .......................................              |  | scrolls
| [ ] row .......................................              |  v
+-------------------------------------------------------------+
```

---

## Notes

- Table pages affected by the action-panel change: Sims, Dongles (Свистки nm), Diagmode
  (Свистки um), Hubs — the four that currently have `TableHeaderBar` + a `Wrap` of `Panel`s
  below the table.
- Non-table pages (Наборы, Планы, Процессы, Биллинг, Обновление, Debug, Иконки) only get the
  new sidebar; their body content is unchanged.
- `CommandLog` stays bottom-docked spanning the content column (right of the sidebar), same
  collapse/expand behavior as today.
- Colors/spacing/radii reuse existing `lib/design/tokens.dart` (`T.brandDeep`, `T.rowSel`,
  `T.radiusCtl`, `T.shadow`, etc.) — no new tokens introduced, matching the -dc mock's palette.
- Logo asset swap is the one place this flow deviates from the -dc mock's literal asset names
  (`logo_wide.png`/`logo_square.png` → `logo_wide_transparent.png`/`logo_transparent.png` per
  the user's explicit instruction).

---

## Approval

- [ ] Reviewed by: Anton Dodonov
- [ ] Approved on:
- [ ] Notes:
