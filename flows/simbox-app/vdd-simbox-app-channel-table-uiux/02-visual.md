# Visual: simbox-app-channel-table-uiux

> Version: 1.0
> Status: APPROVED
> Last Updated: 2026-08-23
> **Extracted 2026-08-23 from `vdd-simbox-app-uiux` v1.2** (the Каналы
> screen's mockups, the two view modes, and the Настройки → Интерфейс
> toggle) — content unchanged by the extraction, only relocated.
> Source: `design/simbox-app-maket-v2026/*.dc.html` + `design/
> nativemind-designsystem-v1.8` — same sources `vdd-simbox-app-uiux`
> used for the base screens this work extends.

## Notation

- `[ ]` unchecked / `[x]` checked selection box
- `( )` circular element (icon chip, connect-style button)
- `‹ ›` back/forward chevrons
- `▼` dropdown caret, `›` disclosure chevron
- `▾`/`▸` expanded/collapsed modem parent row (this flow's own
  addition to the base notation — see the Каналы screen below)
- Icon placeholders: `(rssi)` `(op)` `(state)` `(qos)` etc. — refer to
  `assets/adminka/{rssi,napravleine,state,qos,spec}` per the DS icon
  taxonomy; `(⚙)` `(⚡)` `(⋯)` are generic/fugue fallbacks.
- `━━━` section divider inside a card; `┈┈┈` hairline separator

## Where This Fits

`vdd-simbox-app-uiux`'s Navigation Map already shows Каналы as one of
four tabs, with a pointer into this flow for the view-switch/table-mode
details:

```
  ┌────────┐  tap row   ┌───────────────┐
  │ Каналы │──────────▶│ Деталь канала  │  (stats · actions · USSD ·
  │(list / │◀──────────│ (detail panel) │   identifiers · command log)
  │ table) │            └───────────────┘
  └────────┘  back ‹
       │ view switch → По модемам (expandable rows, default) ⇄
       │               По SIM, все (flat list, incl. unseated SIM cards)
       │ Настройки → "Табличный вид" toggle forces the dense table (По
       │   модемам view) at any screen size, horizontally scrolling on
       │   phone — card view (below) stays the default when off
       ▼
```

## Screen: Каналы (Channels — renamed from "Симки", see
01-requirements.md's CRITICAL product note)

A **channel** = one call-capable path: a modem hosting one SIM (the
common case), or one SIM/line among several on a multi-SIM/multi-line
modem. This screen has two view modes (Настройки-persisted, see the
Настройки → Интерфейс mockup below): **По модемам** (default — card
list on phone/tablet, expandable-row dense table on desktop) and **По
SIM, все** (flat, includes SIM cards not currently seated in any modem
— see the dedicated mockup after the desktop table below). Both modes
show the same underlying channel data, just grouped/flattened
differently — no separate data model, per 01-requirements.md's
resolved design.

### Phone — list state (По модемам, card view — default)
```
┌─────────────────────────────────────┐
│ ‹  Каналы                       (⚙)(🔍)│  <- back hidden at root; search icon
│    номер, план, модем, IMSI           │     toggles inline search input
├─────────────────────────────────────┤
│ [Все] [ОП: истекает] [Автоблок] [Мало│  <- filter chips, horiz scroll
│  денег] [В сети]                      │
├─────────────────────────────────────┤
│ ▾ Модем hub1/2-1              в сети  │  <- modem parent row (collapsible,
│   [ ] (op)(spec) 7912345678   84.20р │      only shown when modem hosts
│       (qos) канал 1   (rssi)          │      >1 channel — single-channel
│       ОП: до 30.07 · автоблок: низкий │      modems skip straight to their
│       ACDL · план default              │      one channel card, no parent
├─────────────────────────────────────┤      row, to avoid pointless nesting)
│ [ ] (op) 7998765432          240.50р │  <- single-channel modem: channel
│     (state:blocked) заблокирована     │     card shown directly
│     ⚠ ОП: нет, баланс                 │  <- alarm row, danger red, own icon
├─────────────────────────────────────┤
│         ⋯ more cards ⋯                │
└─────────────────────────────────────┘
│ (Каналы)│ (Модемы) │ (Операции)│(Настр)│  <- frosted bottom tab bar, 92px,
└─────────────────────────────────────┘     icon 32px + label 11px + ▼ caret
```
- Swipe a row left → 3 action tiles slide in from the right (56px each):
  `ВКЛ/Пауза` `USSD` `⋯`, icon + 10px label, colored per action.
- Select ≥1 row (tap checkbox) → header right shows a pill button
  `{N} действия` in the brand gradient → opens **bottom sheet**:
  ```
  ┌─────────────────────────────────────┐
  │              ▔▔▔▔ (grab handle)       │
  │ Действия · выбрано 2                  │
  │ ┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈ │
  │ (icon) Включить передатчик      `atcmd`│  <- each row: icon, label,
  │ (icon) Выключить передатчик     `atcmd`│     mono command hint (10px,
  │ (icon) Сменить план на default        │     right-aligned, grey)
  │ (icon) Снять флажки автоблока          │
  │ (icon) Проверка ОП                     │
  └─────────────────────────────────────┘
  ```
- Empty/filtered state: centered grey 14px text
  `Ничего не найдено по фильтру`.
- Toast (bottom, above tab bar): dark pill, e.g.
  `Флажки автоблокировки снялись` / `СМС отправлено на 79123456`.

### Phone — table mode (Настройки → "Табличный вид" toggle ON;
requirements AC #1, for conservative users)
```
┌─────────────────────────────────────┐
│ ‹  Каналы                       (⚙)(🔍)│
├─────────────────────────────────────┤
│ [Все] [ОП: истекает] [Автоблок] [Мало│
│  денег] [В сети]                      │
├──────────────────────────────scroll▸─┤  <- same GOSTSIMBOX-ADMIN dense
│┌──┬────┬────┬─────────┬───────┬─────┐│     table as desktop (below):
││▾ │    │    │ hub1/2-1│       │в сети││     fixed desktop-width columns,
││  │(op)│(sp)│79123456 │84.20р │ ... ││     single horizontal scroller —
││  │(op)│    │79987654 │240.50р│ ... ││     no reduced/adaptive column
│├──┼────┼────┼─────────┼───────┼─────┤│     set (per requirements AC #1,
││▸ │(op)│    │79912345 │12.00р │ ... ││     confirmed by Anton) — the
│└──┴────┴────┴─────────┴───────┴─────┘│     row content is identical to
└─────────────────────────────────────┘     the desktop table, just a
│ (Каналы)│ (Модемы) │ (Операции)│(Настр)│   narrower viewport onto it
└─────────────────────────────────────┘
```
`▾`/`▸` = expanded/collapsed modem parent row, same expand/collapse
mechanism as the desktop table below — tapping the chevron (not the
row) toggles it, tapping the row itself still opens channel detail.
Tablet's table mode is the same pattern, just wider (more columns
visible before the scroll boundary).

### Tablet (iPad) — split state (По модемам, card view — default)
```
┌────────┬──────────────┬───────────────────────┐
│ simbox- │ Каналы   (🔍)│ 79123456        84.20р│  <- selected row's detail
│ a4      ├──────────────┤ ОП: до 30.07  (rssi)   │     opens in right pane,
│ .17·up  │[✓](op)79123..│ ┌───────┬───────┬────┐│     same content as phone
│ 41д      │  ...          │ │Баланс │ACDL   │DATT││     detail (below) but
│         │[ ](op)79987..│ │84.20р │ 12/22 │0.4 ││     denser 3-col stat grid
│ ▸Хабы   │  ...          │ └───────┴───────┴────┘│
│  hub1   │  ...          │ [Включить][Сброс][USSD]│  <- action chips row
│  hub2   │              │ USSD: [____________][➤]│
│ ▸Линии  │              │ IMSI  250012345678901  │
│  л1..л8 │              │ IMEI  35892...          │
│         │              │ Вывод команд             │
│         │              │ 12:04:11  AT+CUSD=1,"*100#" ...│
└────────┴──────────────┴───────────────────────┘
```
Left rail = navigation groups (Хабы/Линии under Модемы, collapsible,
matches DS `ListRow` group pattern); middle = list (narrower cards, no
swipe — tap opens right pane instead); right = detail. This is the
"Карточка список слева / действия справа" layout explicitly called out
in the design notes.

### Desktop — dense table state (mandatory: GOSTSIMBOX-ADMIN pattern),
По модемам (default view)
```
┌───────────────────────────────────────────────────────────────────────┐
│ (⚡) simbox-a4   10.42.0.17   SimBox 8f3c1a2+          up 41 days, 6:12│
│ ▾Хабы [hub1][hub2][hub3] | ▾Линии [л1][л2]...[л8] | ▾Операции ... │    │
├───────────────────────────────────────────────────────────────────────┤
│ Каналы  (По модемам ▾)(По SIM, все)  фильтр: номер, IMSI  [N выбрано] │  <- segmented view switcher,
│┌──┬────┬────┬─────────┬───────┬──────┬──────┬────┬────┬────┬────┬───┐│     left of the filter field
││✓ │(op)│(sp)│ Номер   │Баланс │ ACDL │ DATT │(q) │(d) │(rs)│Хаб/│...││
││  │    │    │         │       │12px/ │alarm │    │    │    │порт│   ││
││  │    │    │         │       │10px  │bold  │    │    │    │    │   ││
│├──┼────┼────┼─────────┼───────┼──────┼──────┼────┼────┼────┼────┼───┤│
││▾ │    │    │ hub1/2-1│       │      │      │    │    │    │    │   ││  <- modem parent row (only for
││ [ ]│(op)│(m) │79123456 │84.20р │12/22 │ 0.4  │(qg)│(→) │▮▮▮ │канал1│..││     modems hosting >1 channel;
││ [✓]│(op)│    │79987654 │240.50р│ —    │ —    │    │    │▮   │канал2│..││     single-channel modems show
│├──┼────┼────┼─────────┼───────┼──────┼──────┼────┼────┼────┼────┼───┤│     their one row directly, no
││▸ │(op)│(m) │79912345 │12.00р │ —    │ —    │    │    │▮▮  │hub2│...││     collapsed parent — same
│├──┴────┴────┴─────────┴───────┴──────┴──────┴────┴────┴────┴────┴───┤│     "no pointless nesting" rule
││ Всего каналов: 24  Модемов: 19  Баланс: 3 412.80 р.  Выбрано: 1      ││  <- footer row, colspan
│└─────────────────────────────────────────────────────────────────────┘│
└───────────────────────────────────────────────────────────────────────┘
```
`▾`/`▸` = expanded/collapsed modem row — click the chevron to
expand/collapse; click elsewhere on a channel row still opens its
detail panel as before. This is the screen the DS readme's
"GOSTSIMBOX-ADMIN — DENSE TABLE" section is written for. **Required
per `vdd-simbox-app-uiux`'s AC #3**: brand-tint zebra (not grey),
icon-only column headers, stacked-cell ink hierarchy
(primary/secondary/tertiary/alarm), icon-stack status columns
(captcha/multi-SIM/spec/direction/quality/operator, fixed order), CSS-grid
/ pinned-column layout with one horizontal scroller. Row click opens the
detail panel to the right or below (desktop keeps list+detail side by
side, wider stat grid — 6 columns vs tablet's 3).

### Desktop — По SIM, все (flat mode)
```
┌───────────────────────────────────────────────────────────────────────┐
│ Каналы  (По модемам)(По SIM, все ▾)  фильтр: номер, IMSI  [N выбрано] │
│┌──┬────┬────┬─────────┬───────┬──────┬──────┬────┬────┬────┬────┬───┐│
││✓ │(op)│(sp)│ Номер   │Баланс │ ACDL │ DATT │(q) │(d) │(rs)│Хаб/│...││
│├──┼────┼────┼─────────┼───────┼──────┼──────┼────┼────┼────┼────┼───┤│
││[ ]│(op)│(m) │79123456 │84.20р │12/22 │ 0.4  │(qg)│(→) │▮▮▮ │1/2-1│..││  <- flat, no modem grouping;
││[✓]│(op)│    │79987654 │240.50р│ —    │ —    │    │    │▮   │1/2-2│..││     same columns as По модемам
││[ ]│(op)│    │79912345 │12.00р │ —    │ —    │    │    │▮▮  │hub2│...││     (identical data, same
│├──┼────┼────┼─────────┼───────┼──────┼──────┼────┼────┼────┼────┼───┤│     dense-table styling), just
││ Всего SIM (в модемах): 24         Баланс: 3 412.80 р.  Выбрано: 1    ││     no expand/collapse column
│└─────────────────────────────────────────────────────────────────────┘│
└───────────────────────────────────────────────────────────────────────┘
```
Same columns/styling as По модемам, minus the expand/collapse
affordance (nothing to nest — flat by definition). **Interim scope**
(per the resolved open item below): shows only SIMs currently seated
in a modem — same rows as По модемам, just flattened, no modem
grouping/parent rows. A future "(не в модеме)" row for spare/tray SIM
cards is designed but **not shippable yet** — it needs
`sdd-flutter_gsmsip-interface`'s new SIM-inventory-independent-of-modem
capability (flagged there as a follow-up addendum, not yet designed or
implemented). When that lands, this same view gains those rows without
a UI redesign — the column set already accommodates a modem-less row
(`Хаб/порт` reading e.g. `(не в модеме)`), only the data source needs
to grow. "Только активные в модеме" (the other half of Anton's
original SIM filter framing) becomes moot until then, since every SIM
this view can currently show already is active in a modem.

---

## Cross-Reference: Модемы Screen (owned by `vdd-simbox-app-uiux`, not this flow)

**Correction (Tasks 14-18 implementation, 2026-08-23)**: an earlier
draft of this content claimed the Настройки → Интерфейс toggle "also
applies" to Модемы via an expand-in-place hub→line tree assumed to
already exist for tablet/desktop there. That tree **does not exist in
the actual implementation** — `modems_screen.dart`'s real
tablet/desktop layout is a flat `ListView`/`ListTile` list (no hub
grouping, no `DenseModemTable`), discovered while implementing, not
assumed. That claim was Claude's own inference when drafting the
original AC wording, not something Anton specifically asked for beyond
Каналы — **scoped down**: the toggle applies to Каналы only. Giving
Модемы a real dense/expandable table would be materially more work
(building the hub-grouping tree from scratch, not just wiring an
existing toggle) and wasn't part of what was actually requested —
flagged here as a legitimate future enhancement, not silently dropped.
Модемы's own mockups/behavior stay documented in
`vdd-simbox-app-uiux/02-visual.md`, unchanged by this flow.

---

## Настройки → Интерфейс (new, per approved requirements AC #1)

```
┌─────────────────────────────────────┐
│ ‹ Интерфейс                          │
├─────────────────────────────────────┤
│ Табличный вид на любом экране    (◯)│  <- Switch component; off by
│ Показывать плотную таблицу           │     default (card view stays the
│ Каналы вместо карточек на            │     default per requirements —
│ телефоне, как в настольной версии    │     this is opt-in)
└─────────────────────────────────────┘
```
- Lives in `vdd-simbox-app-uiux`'s Настройки screen (a new section
  alongside SIP/SMPP/Линии/Хабы/Обновление) — this flow only owns the
  section's own content/behavior, not the Настройки screen shell
  itself.
- Takes effect immediately (no Сохранить/Сброс — this is a display
  preference, not a form field with server-side effects; persists via
  local storage, survives app restart per requirements AC #1).
- Applies to Каналы (По модемам view) only — see the Модемы
  cross-reference correction above for why it doesn't extend there.

---

## Design-System Token/Component Mapping (this flow's additions to
`vdd-simbox-app-uiux`'s table)

| Prototype element | DS source |
|---|---|
| Dense channel table (desktop, and phone when Табличный вид is on) | `tokens/web.css` adminka tokens + `templates/gostsimbox-admin/` pattern — **mandatory**, see `vdd-simbox-app-uiux`'s AC #3 and this flow's AC #1 |
| Expandable modem→channel/line row (По модемам view) | Same dense-table styling, `▾`/`▸` disclosure chevron per this doc's Notation — see Open Items below for the underlying Flutter table widget's row-expansion support |
| Segmented view switcher (По модемам / По SIM, все) | `Badge`/chip pattern (same family as filter chips), single-select instead of multi-select |

---

## Open Items

- [x] **Resolved by Anton (2026-08-23)**: the dense table scrolls
      horizontally on phone when forced on — same fixed desktop-width
      columns, same GOSTSIMBOX-ADMIN design/icons, just a narrower
      viewport with a horizontal scroller. No reduced/adaptive column
      variant.
- [x] **Resolved 2026-08-23 by reading the actual installed package
      source** (`~/.pub-cache/hosted/pub.dev/two_dimensional_scrollables-0.3.9/
      lib/src/table_view/table.dart`): `TableView` is a flat,
      fixed-`rowCount` grid with an index-based `TableSpan` builder —
      no expand/collapse, no tree/hierarchy concept anywhere in its
      API. Confirmed, not assumed. **Design decision**: the expandable
      modem→channel tree is built on top — `DenseModemTable` computes
      a flattened, filtered row list from expansion state (row N maps
      to "the Nth currently-visible row given which modems are
      expanded"), and `rowCount` is that flattened list's length, not
      the raw channel count. Collapsing a modem is just "its channel
      rows are absent from the flattened list," nothing removed from
      the underlying data. Carried into 03-specifications.md's data
      model.
- [x] **Resolved 2026-08-23 by Anton, with a specifications addendum
      added to `sdd-flutter_gsmsip-interface`** (both copies —
      `libsFlutter/flutter_gsm/flows/` and `libsFlutter/flutter_gsmsip/
      flows/`, kept in sync, not reopening that flow's approved
      specs): the API **must** support both "SIM seated in a modem"
      and "SIM not currently in any modem" as first-class cases — this
      is a real, currently-unmodeled gap in `ModemDevice` (device+SIM
      are one unit today, no independent `SimCard` concept), not a
      small field addition. It needs its own dedicated flow/amendment
      round (likely a new entity, plus native SIM-inventory/tray
      support that `libsimbox`/chan_dongle don't have today either) —
      not designed here, not guessed at. **Interim resolution**: По
      SIM, все ships showing only seated SIMs (same data as По
      модемам, flattened, no "не в модеме" row) until the interface
      addendum lands.

---

## Approval

- [x] Reviewed by: Anton Dodonov
- [x] Approved on: 2026-08-23 (as `vdd-simbox-app-uiux` v1.1/v1.2,
      before extraction into this flow)
- [x] Notes: Content unchanged by the extraction — the "Каналы"
      rename, the По-модемам expandable-tree / По-SIM-все flat dual
      view, and the Настройки → Интерфейс toggle were all approved
      there and are relocated here as-is.
