# Visual Mockups: simbox-web-design-prototype-readers-uiux

> Version: 1.0
> Status: REVIEW
> Last Updated: 2026-09-02

## Overview

ASCII mockups for the new **"Ридеры"** nav tab and page — a dense table + action-toolbar page,
following the exact same shape as `HubsPage`/`DonglesPage` (`ColDef`/`DenseTable`,
`TableHeading`/`TableToolbar`, `ActionGroup`/`SubAction`/`AdmField`), not the
registry+detail workspace shape used by `zones`/`command_sets`. No narrow/stacked variant is
mocked below — `DenseTable` has no narrow branch anywhere in this codebase; every dense table
(Sims, Hubs, Dongles) just scrolls horizontally, and Readers follows that same precedent.

---

## Screen: Sidebar — Ридеры added, adjacent to Хабы

```
+----------------+
| [logo]         |
|----------------|
| (ico) Симки    |
| (ico) Свистки..|
| (ico) Свистки..|
| (ico) Ридеры   |   <- NEW, inserted directly before Хабы
| (ico) Хабы     |
| (ico) Наборы.. |
| (ico) Направл..|
| (ico) Планы    |
| (ico) Процессы |
| (ico) Биллинг  |
| (ico) Обновлен.|
| (ico) Debug    |
| (ico) Иконки   |
+----------------+
```

Both hardware-adjacent items sit together, matching the existing convention that related
concepts are neighbors in the list (Свистки (nm)/Свистки (um) are already adjacent for the same
reason). Same active-state/compact-mode behavior as every other `_NavItem` — no new interaction.

## Screen: Ридеры — idle, table populated

```
+-----------------------------------------------------------------------------------+
| Ридеры  Всего: 6                                                                   |
+-----------------------------------------------------------------------------------+
| [Обновить v] [PIN v] [Поиск KI v] [APDU-команда v]              [filter][Обновить]|
+-----------------------------------------------------------------------------------+
| [ ] мод.  ридер   lock  state         SPN     ICCID          PIN   IMSI      KI    прогр  dataport |
|-------------------------------------------------------------------------------------|
| [ ] (pl) reader1        Not connected  —       —              —     —         —      —     /dev/ttyUSB0 |
| [ ] (pl) reader2  🔒    OK             Beeline 8979...4471    1234  25001...  A1B2..  —     /dev/ttyUSB1 |
| [ ] (pl) reader3        Reading[12]   MTS     8977...1183    —     25099...  00      812/31044  /dev/ttyUSB2 |
| [ ] (pl) reader4  🔒    OK             MegaFon 8977...2290    0000  25002...  F3C9..  —     /dev/ttyUSB3 |
| [ ] (pl) reader5        Error         —       8979...0071    —     —         00      —     /dev/ttyUSB4 |
| [ ]      reader6        Not connected  —       —              —     —         —      —     /dev/ttyUSB5 |
|-------------------------------------------------------------------------------------|
| Всего: 6                                                                             |
+-----------------------------------------------------------------------------------+
```

Column order matches `readers.php:176-191` exactly (select, model icon, reader id, lock, state,
SPN, ICCID, PIN, IMSI, KI, progress, dataport). Notes on the mocked rows (Acceptance Criteria
#5's required state coverage):
- `reader1`/`reader6` — no card present ("Not connected", every card-keyed column blank).
  `reader6` additionally has no recognized model (`pl2303` icon blank) — an unknown-reader edge
  case worth keeping since `readers.php`'s `$model_str` falls back to the raw code when it isn't
  `1001`.
- `reader2`/`reader4` — fully-identified cards: real ICCID/IMSI, resolved KI (no longer "00"),
  no progress. `reader4`'s PIN is literally `0000` (a real stored value, not a placeholder for
  "none") — distinguishing an actual `0000` PIN from reader1/6's blank PIN matters, so the
  mockup keeps both.
- `reader3` — mid-KI-search: KI still shows `"00"` (not yet found), progress column populated
  (`812/31044`), state carries a small fault-code suffix (`Reading[12]`, since its stored result
  is neither `0` nor `1000`).
- `reader5` — a fault row with a card present (ICCID known) but state `Error` and KI still `00`
  — covers "card inserted, something's wrong" independent of the KI-search-in-progress case.

## Screen: Ридеры — Обновить (plain refresh)

```
| [Обновить v] ...                                                                    |
```

No dropdown/fields — a single-action group like Hubs' "Питание порта" today, immediately
triggers a reload/log line on click. No confirmation, no fields.

## Screen: Ридеры — PIN group open

```
+-----------------------------------------------------------------------------------+
| Ридеры Всего:6 [<] PIN: [____] [Снять PIN]     [________] [Установить PIN]  | [filter][Обновить]
+-----------------------------------------------------------------------------------+
```

Two independent field+button pairs in one open pill, mirroring `DonglesPage`'s existing PIN
block exactly (`AdmField(_pin, hint: 'PIN', width: 100)` pattern) — left pair removes the PIN
using the typed value, right pair sets a new PIN. Acts on every checked row.

## Screen: Ридеры — Поиск KI group open (warning state)

```
+-----------------------------------------------------------------------------------+
| Ридеры Всего:6 [<] [Запустить поиск KI]                                     | [filter][Обновить]
+-----------------------------------------------------------------------------------+
| (!) Внимание! Во время подбора KI карта недоступна для других операций.            |
+-----------------------------------------------------------------------------------+
| [ ] мод.  ридер   lock  state         ...                                           |
```

The warning banner (`(!)`, danger/red-tinted per design tokens — same visual language as other
destructive/caution banners already in this codebase, e.g. delete-confirmation dialogs) appears
directly under the toolbar the moment this group is open — reproducing
`readers.php`'s inline red caution text as a persistent state cue, not just a one-off toast,
since the caution applies for the whole duration a search could be running.

## Screen: Ридеры — APDU-команда group open

```
+-----------------------------------------------------------------------------------+
| Ридеры Всего:6 [<] APDU: [________________________] [Выполнить APDU команду] | [filter][Обновить]
+-----------------------------------------------------------------------------------+
```

Same shape as `DonglesPage`'s AT-command field — one `AdmField` + one run button, logged as a
command-log entry on submit (Acceptance Criteria #3).

## Screen: Ридеры — Columns editor open

```
+-----------------------------------------------------------------------------------+
| Ридеры Всего:6 [<][Reset] [<>мод.][<>ридер][<>lock][<>state][<>SPN][...>]    | [filter][Обновить]
+-----------------------------------------------------------------------------------+
```

Identical mechanism to every other dense table's Columns editor (fix2 precedent) — `select`
column excluded from the chip list, fixed at position 0.

---

## Flow: Running a KI search

```
[Ридеры idle] --(check rows, open "Поиск KI")--> [Warning banner shown] --(Запустить поиск KI)--> [Log entry pushed, banner stays while group open] --([<] back)--> [Ридеры idle]
```

### Step-by-Step

1. **Idle**: operator checks one or more reader rows.
2. **Opens "Поиск KI"**: pill expands, red warning banner appears above the table immediately
   (matches legacy: the warning is shown regardless of whether the search has been launched yet,
   since it's about the risk of running it, not a live-progress indicator).
3. **Запустить поиск KI**: pushes one command-log line per selected reader (mirrors legacy's
   per-device loop), toast confirms; `reader3`-style progress rows are how the mocked mid-search
   state is represented afterward (static mock data, not live progress ticking, per Won't Have).
4. **Back (`[<]`)**: collapses the pill, banner disappears, table returns to idle.

---

## Component: Reader row — KI cell

```
KI column:
  "00"        <- all-zero stored KI (not yet found) — plain text, no warning styling needed,
                 this is just the default/empty state, not an error
  "A1B2C3.."  <- monospace, truncated/scrollable like ICCID/IMSI, a real found key
```

## Component: Reader row — state cell with fault suffix

```
state column:
  "OK"                 <- result is 0 or 1000, no suffix
  "Reading" + "[12]"   <- result is some other code (12), shown smaller/dimmer next to the
                            main state text, same "primary text + small secondary annotation"
                            pattern already used for balance-age/diff cells on the Sims table
```

---

## Notes

- Icon choice for the sidebar's "Ридеры" item (Open Question from Requirements) — decided here:
  reuse `assets/imgs/pl2303.png` (the reader-chip icon already shown per-row in the table) at
  nav size, rather than `lock.png` (too easily confused with the per-row `lock` column, which
  means something different — a physical card-lock state, not "this nav item is about security")
  or vendoring a brand-new Fugue glyph (adds an asset for a prototype where an appropriate one
  already exists locally). Same reasoning `zones` used for reusing `_naprMap` icons instead of
  inventing new ones.
- No tabs, no detail pane — this is a flat dense-table page like Hubs/Dongles, not a
  registry+detail workspace like zones/command_sets. Matches Requirements' Constraints section.
- Row identity: mocked as one row per reader **device**, with card-keyed fields (ICCID, IMSI, KI,
  progress, result/state-suffix) simply blank when no card is present — matches legacy's actual
  per-device iteration (`readers.list`) with per-card lookups keyed by that device's current
  ICCID, rather than trying to model readers and cards as two separate joined tables (out of
  proportion for a mock-data prototype).

---

## Approval

- [ ] Reviewed by: Anton Dodonov
- [ ] Approved on:
- [ ] Notes:
