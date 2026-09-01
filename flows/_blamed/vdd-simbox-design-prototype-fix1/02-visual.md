# Visual Mockups: simbox-design-prototype-fix1

> Version: 1.0
> Status: APPROVED
> Last Updated: 2026-09-01

## Overview

ASCII mockups for the 8 fixes agreed in requirements: icon correctness/density, right-aligned
+ monospace table headers, adaptive actions/filter row, column hide/reorder, Модемы rename,
language selector, and the two already-found column-parity gaps. Scope is the shared chrome
(top bar + nav, repeated on all 11 screens) plus the Симки table as the representative dense
table — the same column-header/columns-control/actions-row patterns apply to every other table
screen without needing a separate mockup each.

---

## Screen: Shared top bar + nav (every screen)

Two changes here: language selector added to the top bar, "Свистки" → "Модемы" in the nav.

```
+----------------------------------------------------------------------------------+
|  simbox-a4   10.42.0.17   SimBox 8f3c1a2+          29.07.26  up 41d 6:12  (o) EN v|
+----------------------------------------------------------------------------------+
|  [Симки]  Модемы (nm)  Модемы (um)  Хабы  Наборы команд  Планы  Процессы  ...    |
+----------------------------------------------------------------------------------+
```

`(o) EN v` = the new language selector: globe icon (`icon-globe.svg`) + current language code +
caret, right-aligned in the top bar next to the uptime text.

### State: language dropdown open

```
+----------------------------------------------------------------------------------+
|  simbox-a4   10.42.0.17   SimBox 8f3c1a2+          29.07.26  up 41d 6:12  (o) EN ^|
+----------------------------------------------------------------------+-----------+
|  [Симки]  Модемы (nm)  Модемы (um)  Хабы  Наборы команд  ...          | English * |
|                                                                        | ไทย       |
|                                                                        | Русский   |
|                                                                        | हिन्दी      |
|                                                                        | 中文       |
+------------------------------------------------------------------------------------+
```

`*` marks the active language (English, default). Selecting an option in this prototype only
updates the button label/checkmark — no copy actually translates (per requirements, Won't Have).

---

## Screen: Симки — table header (right-aligned + mono)

Representative slice of the header row, showing the alignment fix. Icon-only headers keep their
icon; text headers move to the right edge of their column so they line up with the (already
right-leaning) numeric cell content below them.

```
+-----+-------+-----+-----+-----+--------+---------------+-----------------+
|  [] | group |  pro| cap |  im |  state |          план |          number |
|     |       |     |     |     |        | набор / тариф |                 |
+-----+-------+-----+-----+-----+--------+---------------+-----------------+
|  [] | (>)   |     |(ok) |(B)  | (out)  |       default |     9219981122  |
|     | 101   |     |     |     |        | megafon_spb/MC|                 |
+-----+-------+-----+-----+-----+--------+---------------+-----------------+
```

Identifier-shaped columns (IMEI, IMSI, ICCID, phone numbers, dongle path) switch to
`ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace` so digits line up
column-to-column across rows — e.g.:

```
IMEI              IMSI
35782000112233    250017201029356
86234500019922    250021401138821    <- digits align vertically, proportional font wouldn't
```

---

## Component: Columns control (hide + reorder)

New "Columns" (gear/list icon) button sits at the top-right of each table, above the header row.

```
                                                          [ ... Columns (32/38) v ]
+-----+-------+-----+-----+-----+--------+---------------+-----------------+
|  [] | group |  pro| cap |  im |  state |          план |          number |
```

### State: panel open

```
                                                          +--------------------------+
                                                          | Columns          [Reset] |
                                                          +--------------------------+
                                                          | (x) [::] group           |
                                                          | (x) [::] pro             |
                                                          | ( ) [::] cap             |  <- unchecked = hidden
                                                          | (x) [::] im              |
                                                          | (x) [::] state           |
                                                          | (x) [::] план            |
                                                          | (x) [::] number          |
                                                          | (x) [::] operator        |
                                                          | ...                      |
                                                          +--------------------------+
```

- `(x)` checkbox = column visible; unchecking hides it immediately from the table.
- `[::]` = drag handle; dragging a row up/down reorders that column in the table (both header
  and every data row move together — CSS grid stays in `min-width: max-content`, one horizontal
  scroller, so header/body columns never drift out of sync).
- `id`/checkbox column is pinned (not draggable, not hideable) — always the leftmost column.
- State persists per table (localStorage key per screen) for the session.

---

## Component: Actions + filter row — full width

Current behaviour, unchanged when there's room:

```
+------------------+  +----------------+  +--------------------------------+  +---...
| Редактирование   |  | Передатчик     |  | Действия простые                |  | Действия
| фильтр по группе |  | [ON] [OFF]     |  | USSD запрос [___] [USSD]        |  | групповые
| ...              |  |                |  | SMS на номер [_] сообщение [__] |  | ...
+------------------+  +----------------+  +--------------------------------+  +---...
```

### State: narrow viewport, still fits with wrapping (existing `flex-wrap`)

```
+------------------+  +----------------+
| Редактирование   |  | Передатчик     |
+------------------+  +----------------+
+--------------------------------+
| Действия простые                |
+--------------------------------+
```

### State: too narrow — compact/icon-only mode

Below the breakpoint where even one filter/action card can't sit comfortably, action panels
collapse to a single icon row (labels hidden, `title` tooltip on hover/long-press); the filter
panel stays as fields (never collapses to icons — filters need visible values) but drops below
the icon row instead of sitting beside it:

```
+----------------------------------------------------------------------+
| [USSD] [SMS] [Call60] [CallSpeak] [CallDTMF] [Set grp] [Set plan] ... |  <- icon-only, title=
+----------------------------------------------------------------------+
| Редактирование                                                        |
| фильтр по группе [___] не [___]                                       |
| фильтр по плану  [default v] не [ v]           [Обновить]             |
+----------------------------------------------------------------------+
```

Tapping an icon in the compact row opens that action's fields inline (below the icon row) or in
a small popover — exact interaction detailed in Specifications, but the layout contract is: the
icon row never wraps to two lines, and the filter panel is always fully visible, never
icon-only (its inputs carry values the operator is actively editing).

---

## Component: Icon legend (per-screen notes section)

Expands the existing "Примечание" block into a categorized table, one row per icon actually
used on that screen — mirrors `nativemind-adminka/guidelines/adminka-icons.html`'s grouping.

```
+--------------------------------------------------------------------------+
| Иконки — Симки                                                            |
+--------------------------------------------------------------------------+
| Number quality (QoS)                                                      |
|  (ivip)  iVIP   звонки с достоверных источников (карточный, свой и т.д.)  |
|  (igoo)  iGOO   белый список номеров с очень качественными звонками       |
|  (inor)  iNOR   белый список номеров с нормальными показателями           |
|  (ibad)  iBAD   черный список номеров с низкими показателями              |
|  ...                                                                       |
+--------------------------------------------------------------------------+
| Call state                                                                 |
|  (state_in)   can in    разрешает входящие                                |
|  (state_out)  can out   разрешает исходящие                               |
|  ...                                                                       |
+--------------------------------------------------------------------------+
| Group / auto-block                                                        |
|  (high_datt)  автоблокировка при высоком DATT                             |
|  (low_acdl)   автоблокировка при низком ACDL                              |
|  ...                                                                       |
+--------------------------------------------------------------------------+
```

Each row's glyph resolves through the `16/32/48` `srcset` triplet, so on a retina display the
same markup renders the sharper @2x bitmap — no separate "32px mode" toggle needed for this to
look right on either kind of screen.

---

## Flow: Compact-mode breakpoint

```
[Full row: filters + actions side by side]
        |  window narrows
        v
[Wrapped: cards flow to next line, still full labels]  (existing flex-wrap, unchanged)
        |  window narrows further, a card no longer fits at readable width
        v
[Compact: actions -> icon-only row, filters stay as fields, stacked below]
        ^
        |  window widens back past the breakpoint
        |
[back to Wrapped / Full row]
```

No manual toggle — purely responsive (CSS `@media`/container query on card width), matching how
the rest of the prototype already behaves (the existing `flex-wrap` step is unchanged, compact
is a new third step below it).

---

## Notes

- Симки is the representative table; the same header-alignment, mono-identifiers, and
  columns-control patterns apply verbatim to Модемы (nm/um), Хабы, Наборы команд, Планы,
  Процессы, Биллинг, Обновление, Debug — no separate mockup needed per screen.
- The two already-found column-parity gaps (missing `msm.ico` on Планы, 2 missing header
  columns on the dongle table) aren't shown as a separate mockup — they're just restored
  columns using the exact same header-cell pattern shown above, in the position legacy PHP has
  them.
- Language selector copy (`EN`/`TH`/`RU`/`HI`/`ZH` vs. full names in the dropdown) and exact
  compact-row tooltip wording will be finalized in Specifications — mockup above is layout-only.

---

## Approval

- [x] Reviewed by: Anton Dodonov
- [x] Approved on: 2026-09-01
- [x] Notes: Approved as drafted.
