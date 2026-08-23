# Visual: simbox-app-uiux

> Version: 1.4 (v1.3's Navigation Map + nav-chrome token-mapping rows
> **extracted 2026-08-23 into `vdd-simbox-app-navbar-uiux`** at Anton's
> explicit instruction — this document reverts to describing this
> flow's own screen-content scope, with forward references where the
> extracted content used to be. The earlier "Каналы" screen extraction
> into `vdd-simbox-app-channel-table-uiux` still stands, unaffected.)
> Status: APPROVED
> Last Updated: 2026-08-23
> Source: `design/simbox-app-maket-v2026/*.dc.html` (read directly — template-
> driven prototype using `sc-if`/`sc-for` bindings over live sample data, not
> static per-screen exports). Cross-referenced against
> `design/nativemind-designsystem-v1.8` tokens/components.

## Notation

- `[ ]` unchecked / `[x]` checked selection box
- `( )` circular element (icon chip, connect-style button)
- `‹ ›` back/forward chevrons
- `▼` dropdown caret, `›` disclosure chevron
- Icon placeholders: `(rssi)` `(op)` `(state)` `(qos)` etc. — refer to
  `assets/adminka/{rssi,napravleine,state,qos,spec}` per the DS icon
  taxonomy; `(⚙)` `(⚡)` `(⋯)` are generic/fugue fallbacks.
- `━━━` section divider inside a card; `┈┈┈` hairline separator

## Navigation Map

See `vdd-simbox-app-navbar-uiux/02-visual.md` for the full navigation
map (tab set, order, per-breakpoint chrome, detail-panel navigation
pattern) — extracted there whole 2026-08-23, including the note about
the Симки→Каналы rename's own navigation-map annotations (which had
already been forward-referenced to `vdd-simbox-app-channel-table-uiux`
before this second extraction; that reference now lives in the navbar
flow's copy). This document no longer carries a standalone nav map to
avoid three sources of truth.

Three breakpoint families, six documented layouts total (per
`Основной экран-ipad,desktop,phone.dc.html`): **Android portrait**,
**Android landscape**, **iPad** (split nav+list+detail), **Desktop window**
(top group-nav + dense table + side detail), plus two **legacy-preserving
web layouts** — "Веб в браузере" (desktop browser, keeps 2015 host-string
header + ` :: `-separated text nav) and "Веб-страница с телефона" (same
legacy page, mobile-width). See **Open Items** below — the two web layouts
are a scope question, not yet mocked here.

---

## Screen: Симки (SIM list)

See `vdd-simbox-app-channel-table-uiux/02-visual.md` for the full,
current mockups of this screen — it was renamed "Каналы" and given a
dual view mode (По модемам expandable rows / По SIM, все flat) plus a
table-view-anywhere toggle, extracted there whole 2026-08-23. This
document no longer carries a standalone mockup for this screen to
avoid two sources of truth diverging.

---

## Screen: Модемы (Modems — Хабы / Линии)

```
Phone (drill-in):                      Tablet/Desktop (expand-in-place):
┌─────────────────────────┐            ┌─────────────────────────────────┐
│ ‹ Модемы                │            │ Модемы            хаб / порт     │
│ [Хабы] [Линии]          │            │ ▾ hub1  USB-порт  засунут        │
├─────────────────────────┤            │   линия 1  ●вкл  RSSI ▮▮▮  no SIM│
│ hub1                    │            │   линия 2  ●вкл  RSSI ▮▮      │
│  порт 2-1 · питание внеш│            │ ▾ hub2  ...                      │
│  порт 2-2 · питание внеш│            │   ...                            │
│  ...                     │            └─────────────────────────────────┘
│ ▾ линия (радиомодуль)   │            Detail (either breakpoint):
│  Передатчик включён: ...│            ┌───────────────────────────────┐
│  Передатчик выключен: ..│            │ линия 3 · модем              │
│  [Перезагрузка]          │            │ Общий радиомодуль с линией 4 │
│  Прошивки модемов         │            │ [Перезагрузка][Прошивка][⋯]  │
│  версии панели и прошивок │            │ состояние: просыпается ...   │
└─────────────────────────┘            └───────────────────────────────┘
```
Row toggle for "Передатчик" (radio module) is the `Switch` DS component;
"перезагрузка"/reboot is a destructive-ish secondary action (outline
button, not filled). "Прошивки модемов" opens a sub-list of firmware/panel
version pairs (plain `ListRow`s, value right-aligned — same shape as
Настройки's read-only rows, see below).

**Note**: `vdd-simbox-app-channel-table-uiux` briefly considered
extending its table-view-anywhere toggle to this screen too, but found
during implementation that this screen's real tablet/desktop layout
(above) is a flat `ListView`/`ListTile` list, not a `DenseModemTable` —
that toggle stayed scoped to Каналы only. A real Модемы dense-table
remains a legitimate future enhancement; see that flow's `_status.md`.

---

## Screen: Операции → Звонки (Calls)

```
┌─────────────────────────────────────┐
│ ‹ Операции          [Звонки|СМС]     │  <- segmented toggle in header
├─────────────────────────────────────┤
│ Запустить звонок                      │
│ [номер назначения______________]      │
│ [линия ▾: любая / hub1-1 / hub1-2...] │
│ [        Позвонить        ]           │  <- brand-gradient CTA, full width
├─────────────────────────────────────┤
│ (→out) 79123456789        02:14      │  <- call log rows: direction icon,
│        Звонок с 79123456 ...  ok      │     number, duration (right,
│ (←in)  79987654321        —          │     tabular nums), sub meta,
│        нет ответа сервера   failed    │     result label (grey small)
└─────────────────────────────────────┘
```
Ringing/active state (not a separate screen in the prototype — implied by
`ModemCall`/`SipCall` state driving the log row's right-side color/weight):
`failed`→danger red, `active`→brand blue bold, `terminated`→grey normal.

## Screen: Операции → СМС

```
┌─────────────────────────────────────┐
│ Отправить СМС                         │
│ [номер получателя_______________]     │
│ [текст сообщения________________]     │
│ [        Отправить          ]         │
├─────────────────────────────────────┤
│ (→out) 79123456789      12:04         │
│        Услуга подключена. Стоимость...│
│        доставлено                     │
│ (←in)  79987654321      11:58         │
│        Код проверки 4412              │
└─────────────────────────────────────┘
```
Toast on send: `СМС отправлено на 79123456`. `шлюз для СМС` (SMS gateway)
is a Настройки concern (SMPP account/server), not this screen.

---

## Screen: Настройки (Settings)

```
Phone (drill-in list):                  Tablet/Desktop (left rail + form):
┌─────────────────────────┐            ┌──────────┬──────────────────────┐
│ ‹ Настройки              │            │ SIP       │ Хост или IP без      │
│ (icon) SIP    аккаунт,   │            │ SMPP      │ пробелов              │
│        сервер          › │            │ Линии     │ [_____________]      │
│ (icon) SMPP   аккаунт,   │            │ Наборы    │ Таймаут регистрации, с│
│        сервер          › │            │ Хабы      │ [___]                 │
│ (icon) Линии            › │            │           │                      │
│ (icon) Хабы              › │            │           │                      │
└─────────────────────────┘            │           │ ⚠ Есть несохранённые │
                                        │           │   изменения           │
                                        │           │ [Сохранить] [Сброс]  │
                                        └──────────┴──────────────────────┘
```
- Unsaved-changes banner: full-width warning strip
  `⚠ Есть несохранённые изменения` — persists until Сохранить/Сброс.
- Validation error state: field border → danger red, inline
  `Проверьте поля: <list>` under the form, save button stays enabled but
  save attempt surfaces `Не сохранено, есть ошибки`.
- Reset: `Сброшено к сохранённым значениям` toast.
- Save success: `аккаунт сохранён и перезарегистрирован` /
  `аккаунт сохранён, bind выполнен` (SIP vs SMPP copy differs).
- `Тест соединения SMPP` is a secondary action next to the SMPP form,
  independent of Save.

**Note**: `vdd-simbox-app-channel-table-uiux` later added an
"Интерфейс" section here (the "Табличный вид на любом экране" toggle)
— see that flow's `02-visual.md` for its mockup. This document's list
above reflects this flow's own original section set only.

---

## Shared: Detail Panel (channel / line / modem)

Same structural card everywhere, density varies by breakpoint (already
shown inline above for phone-full-screen / tablet-right-pane /
desktop-side-pane):

```
┌───────────────────────────────┐
│ ‹  79123456789      (state icons)│
│    ОП: до 30.07                  │
├───────────────────────────────┤
│ [Баланс 84.20р][ACDL 12/22][DATT]│  <- stat tile grid, 2-col phone /
│ [RSSI ▮▮▮▯][Оператор][Группа]   │     3-col tablet / 6-col desktop
├───────────────────────────────┤
│ [Включить][Выключить][Сброс]... │  <- action chips, wrap, icon+label
├───────────────────────────────┤
│ USSD-консоль                     │
│ [*100#______________][Отправить] │  <- mono input + presets row
│ (*100#) (*102#) (*105#)          │
├───────────────────────────────┤
│ Идентификаторы                   │
│ IMSI   250012345678901           │
│ IMEI   358920XXXXXXXXX           │
│ ICCID  8970120XXXXXXXXXXXX       │
├───────────────────────────────┤
│ Вывод команд                     │
│ 12:04:11 AT+CUSD=1,"*100#",15    │
│          +CUSD: 0,"Баланс..."    │
└───────────────────────────────┘
```
This panel is reused for SIM detail, line/modem detail (Модемы screen), and
is the natural place `sendAtCommand`/`sendUssd`/`changeImei`/`restartModem`
from [[sdd-flutter_gsmsip-interface]]'s API attach to UI actions.

---

## Design-System Token/Component Mapping (summary)

| Prototype element | DS source |
|---|---|
| Card shadow `0 1px 32px rgba(156,178,194,.10)`, radius 10px | `tokens/colors.css` + `spacing.css` elevation/radius tokens |
| Brand gradient CTA (`Позвонить`, `Отправить`, `Сохранить`) | `--brand-gradient` (Blue `#00C6FB→#005BEA`) |
| Filter chips | `Badge`/chip pattern, brand-tinted active state |
| Switch (передатчик toggle) | `Switch` component |
| Dense SIM/modem table (desktop) | `tokens/web.css` adminka tokens + `templates/gostsimbox-admin/` pattern — **mandatory**, see requirements AC #3 |
| Status icon columns (op/qos/spec/rssi/state) | `assets/adminka/{napravleine,qos,spec,rssi,state}` primary; `assets/fugue/` fallback |
| Search icon | `assets/fugue/magnifier.png` (already referenced directly in the prototype markup) |
| Bottom sheet / popover actions | VPN-kit `Sub`/sheet pattern, adapted |
| Toast | `Sub`/`Badge` family pattern, dark pill |
| Type scale (17px body, 13px secondary, 11px caption, 22/20/19px screen titles) | `tokens/typography.css` SF Pro Text roles |

`vdd-simbox-app-channel-table-uiux/02-visual.md` carries its own token
mapping for the expandable-row/view-switcher additions.
`vdd-simbox-app-navbar-uiux/02-visual.md` carries the nav-chrome rows
(bottom tab bar, rail, desktop GostSimBox-admin-style nav) removed from
the table above.

---

## Open Items (raised during visual research — need Anton's call)

- [ ] **New scope question**: the breakpoint-rationale document describes
      **six** layouts, two of which ("Веб в браузере", "Веб-страница с
      телефона") explicitly preserve the 2015 legacy web admin's URL/host-
      string header and ` :: `-separated text navigation, as a *distinct
      surface* from the native app. Requirements' "Won't Have" excluded
      rebuilding `templates/gostsimbox-admin/` as a target. Is this
      "web" layout (a) in scope as a real companion web surface for this
      flow, (b) a future/separate flow, or (c) just informational
      precedent in the design doc with no build target? Recommend (c)
      unless told otherwise — this visual doc mocks the 4 native-app
      layouts only (phone portrait/landscape, tablet, desktop).
- [ ] Confirm accent: mockups above assume Blue (unstyled default);
      no simbox-specific accent found in either prototype file.
- [ ] Desktop dense-table column set above (op/spec/balance/ACDL/DATT/qos/
      direction/rssi/hub-port) is inferred from the prototype's `detail.ids`
      and card `meta`/`stateIcons` fields, not a literal 33-column
      enumeration — the older design doc mentions "те же 33 колонки" (same
      33 columns as 2015). Full column list needs the actual 2015 adminka
      column order (`legacy/simbox-desktop-v2015/www/`) cross-checked in
      SPECIFICATIONS, not guessed here.

---

## Approval

- [x] Reviewed by: Anton Dodonov
- [x] Approved on: 2026-08-23
- [x] Notes: v1.4 reflects the 2026-08-23 extraction of the "Каналы"
      screen redesign into `vdd-simbox-app-channel-table-uiux` and the
      Navigation Map/nav-chrome token rows into
      `vdd-simbox-app-navbar-uiux` — no new content approval needed
      here, the underlying v1.0 approval for this flow's own scope
      stands unchanged.
