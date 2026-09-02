# Requirements: simbox-web-design-prototype-readers-uiux

> Version: 1.0
> Status: APPROVED
> Last Updated: 2026-09-02

## Problem Statement

The v2026 Flutter prototype (`design/simbox-web-design-prototype-v2026`) has exactly one
sidebar nav item for USB-adjacent hardware — `AdmPage.hubs`, labelled **"Хабы"** in the sidebar
— which renders `HubsPage`. That page's on-screen heading currently reads **"Ридеры (хабы)"**,
even though every row it shows comes from `hubTree` (`HubNode`: `id`, `icons`, `device`, `port`)
— pure USB topology (`lsusb -t`) with per-port power actions (ВКЛ/ВЫКЛ/РЕСТАРТ via
`hub-ctrl`). There is no reader-specific data model, mock data, or page anywhere in the
prototype.

Deep-diving `legacy/simbox-desktop-v2014/www/simbox/` explains why: **`hubs.php` and
`readers.php` are two distinct legacy pages that got their `<h1>` swapped** — `hubs.php`
(392 lines: `lsusb -t` tree rendering + `hub-ctrl` power actions) literally contains
`<h1>Ридеры</h1>` at line 178, an evident copy-paste leftover from `readers.php` (308 lines:
a table of physical SIM-card-reader devices — ICCID/IMSI/KI/PIN/state/dataport — plus PIN
set/remove, KI-search, and raw APDU-command actions) which carries the *identical* heading at
its own line 174. The v2026 prototype inherited the mislabeled hub page and never built the
reader page at all — so "Ридеры" as a concept is entirely missing from the nav today, and
"Хабы" is displaying a title that isn't even its own.

This flow builds the missing **Ридеры (Readers)** page as its own nav tab, separate from
**Хабы (Hubs)**, restoring the two-page structure the legacy panel actually had — using
legacy `readers.php` as the source of truth for *logic and meaning only* (its 2014 HTML/table
styling is obsolete), and `design/simbox-design-prototype-v2026-dc` plus this repo's own
established Flutter patterns (`HubsPage`, `DonglesPage`) as the source of truth for visuals.

> **Scope note (2026-09-02):** the user confirmed this flow covers **Readers only** — `HubsPage`
> itself is out of scope beyond the one label fix. The mislabeled heading (`"Ридеры (хабы)"` →
> `"Хабы (Hubs)"`) was corrected immediately, ahead of the rest of this flow, in
> `hubs_page.dart:76`, so it wouldn't cause confusion while Readers work is designed. It is not
> tracked as a pending acceptance criterion below — it's already done.

## Deep Legacy Analysis — `readers.php` (308 lines)

**Data source paths** (all read via `file_get_contents_def2($path, $default)`, i.e.
"read file or return default if missing" — matches this codebase's general pattern of one
flat file per fact):
- Device list: `/var/svistok/lists/readers.list` (one device id per line, `asort()`-ed).
- Per-device static facts: `/var/svistok/devices/$device.model` (numeric model code — `1001`
  renders as the `pl2303.ico` chip image, i.e. a Prolific PL2303 USB-serial reader),
  `/var/svistok/devices/$device.dataport` (the serial device path used to launch `wts`).
- Per-device reader state: `/var/svistok/readers/$device.lock`, `.spn`, `.pin`.
- Per-device runtime state: `/var/svistok/readers/state/$device.iccid`,
  `/var/svistok/readers/state/$device.status` (free-text, default `"Not connected"`).
- Per-*card* (keyed by ICCID, not device — a card's identity follows it, not the reader slot):
  `/var/svistok/readers/sim/$iccid.result` (numeric; suffixed onto the state string in small
  font when non-zero and not `1000` — i.e. `1000` and `0` both read as "no error", any other
  code is a visible fault code), `.imsi`, `.ki` (32 hex chars; an all-zero KI
  `00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00` displays as literally `"00"`, meaning
  "not yet found" — any other value is a fully found key), `.gsm` (a raw byte-dump file whose
  size ÷ 58 estimates KI brute-force progress, rendered as `"<done>/31044"` only while > 0).

**Table columns** (`readers.php:176-191`, in order): select-checkbox, model icon, reader id
(`$device`, the value from `readers.list`), lock, state (+ inline fault code), SPN, ICCID, PIN,
IMSI, KI (monospace, "00" when unset), progress (blank until KI search starts), dataport
(monospace). A "Всего: N" footer row totals the list, same convention as every other dense
table in this codebase (Sims, Hubs).

**Actions** (only the *live*, non-commented-out ones — everything else in the file is
`/* ... */`-disabled 2014 dead code, listed below as explicit non-goals):
1. **Обновить** — plain refresh, no params. (`isset($_POST['refresh'])` has no handler in this
   file at all — the whole page just re-renders on POST, meaning "refresh" *is* the reload.)
2. **Снять PIN / Установить PIN** — two text fields (`pin`, `setpinpin`) each paired with its
   own submit button. Both compile to the *same* underlying AT-command path
   (`enterpin`/`setpin` → `atcommandexec` → `asterisk -rx 'dongle cmd $dongle $atcommand'`),
   just with different `AT+CPIN=`/`AT+CLCK=` payloads — i.e. this is the exact same
   "PIN field + AT-command dispatch" shape already implemented for dongles in
   `lib/pages/dongles_page.dart` (`_pin` controller, `AdmField`, `SubAction`), just aimed at a
   reader device instead of a dongle.
3. **Запустить поиск KI** — batch action over every checked row; for each, shells out to a
   `wts --device=reader ... --dev=$device` background job. The page shows a **red warning
   banner** above the result table while this runs: *"Внимание!!! Во время подбора KI карта
   недоступна для других операций."* ("Warning! The card is unavailable for other operations
   while KI search is running.") — this is a real safety caveat worth preserving as a visible
   warning state in the mockup/spec, not just a tooltip.
4. **APDU-команда** — one free-text field + submit, no visible handler bound to it in this file
   (`apducommandexec` is referenced in the input `name` but never `isset()`-checked) — in the
   live 2014 code this was evidently wired at a layer not present in this checkout. Treat it as
   "compose + submit a raw APDU string against the selected reader(s)", the same shape as the
   AT-command box, logged the same way (command log line), since that's the only sensible
   behavior implied by the UI shape itself.

**Explicitly out of scope** (dead/commented-out in `readers.php` itself, mirroring the same
commented blocks already correctly excluded from `HubsPage`): diagmode/firmware-flash trigger,
dongle restart, "blacklist this IMEI" action, a `nullpin` shortcut. These are 2014 leftovers
the legacy authors themselves disabled — not something this flow should resurrect.

## Deep Legacy Analysis — `hubs.php` (392 lines), for contrast

Confirms `HubsPage` is *already* a faithful, complete port of the real logic here: parses
`lsusb -t` output into a depth-annotated tree (`Bus`/`Dev`/`Port`, up to level 4), assigns an
icon per USB class (`root_hub` → `usb_pci.ico`, `hub` → `hub_16.ico`, `vend.` → `usb_port.ico`,
unknown → `unknown.ico`), shows a power-on/off glyph only on port-level rows, and exposes three
power actions (`hub-ctrl -p 0/1`, or off-then-on for restart) plus a delay/queue options block
that this codebase's `queueMode`/`ActionGroup` machinery already generalizes across pages. The
**only** defect to carry into this flow is the mislabeled `<h1>` — nothing else needs to change
in `HubsPage`'s actual table or actions.

## User Stories

### Primary

**As an** operator managing physical SIM-reader hardware (KI extraction, PIN provisioning)
**I want** a dedicated "Ридеры" tab, separate from "Хабы"
**So that** I can see and act on reader/card state (ICCID, IMSI, KI, PIN) without it being
mixed into — or mislabeled as — the unrelated USB-hub-topology/power-control screen.

### Secondary

**As an** operator who already relies on "Хабы" for port power-cycling
**I want** that page's heading and identity cleaned up (no more borrowed "Ридеры" title)
**So that** the two hardware concepts read as clearly distinct in the product, matching what
the sidebar labels already promise.

*(Resolved 2026-09-02, ahead of the rest of this flow — see scope note above.)*

## Acceptance Criteria

### Must Have

1. **Given** the sidebar nav, **when** viewing it, **then** there are two separate items —
   "Ридеры" and "Хабы" — each a distinct `AdmPage` enum value routing to its own page widget,
   positioned adjacently (Readers directly before or after Hubs, since both are USB-hardware
   concepts) rather than scattered.
2. **Given** the new Readers page, **when** it renders, **then** it shows a dense table of
   reader devices with columns: select, model icon (PL2303 chip icon on model `1001`, blank
   otherwise), reader id, lock, state (+ small fault-code suffix when the per-card result is
   neither `0` nor `1000`), SPN, ICCID, PIN, IMSI, KI (monospace; literal `"00"` when the stored
   KI is the all-zero placeholder), progress (`done/31044` only while a KI search is running for
   that card), dataport (monospace) — i.e. a 1:1 column mapping from `readers.php`, following
   this codebase's `ColDef<T>`/`DenseTable<T>` pattern (as `HubsPage`/`DonglesPage` already do).
3. **Given** the Readers page toolbar, **when** using row actions, **then** the following
   groups exist: **Обновить** (plain refresh call, matching the no-op-payload convention already
   used for refresh elsewhere); **PIN** (two `AdmField` text inputs + submit buttons — "Снять
   PIN" and "Установить PIN" — each producing an AT-command-shaped log entry, mirroring
   `DonglesPage`'s existing `_pin`/`AdmField`/`SubAction` PIN block); **Поиск KI** (batch action
   over selected rows that shows a red/warning-styled caption reproducing the legacy caution
   text about card unavailability during the search); **APDU-команда** (one `AdmField` text
   input + submit, logged the same way as the AT-command box on `DonglesPage`).
4. ~~`HubsPage` heading no longer says "Ридеры"~~ — **done** (2026-09-02, out of band, before
   this flow's Visual phase): `hubs_page.dart:76` now reads `"Хабы (Hubs)"`. Table, columns, and
   power actions were untouched, as specified.
5. **Given** the Readers page needs sample data to render, **when** mock data is seeded, **then**
   it includes 5-8 rows spanning: a reader with no card ("Not connected", blank ICCID/IMSI/KI),
   a reader with a fully-identified card (real-looking ICCID/IMSI, non-zero KI, no progress), a
   reader mid-KI-search (KI still `"00"`, non-zero progress `<31044`), and at least one row
   showing a non-trivial fault-code suffix on its state — enough variety to visually exercise
   every column's non-empty state.

### Should Have

- Column show/hide + reordering via the existing `columnOrderFor`/`hiddenColumnsFor` mechanism
  (`st.columnOrderFor(AdmPage.readers, ...)`), matching every other dense-table page.
- Search/filter box wired the same way as `HubsPage`'s (`TableToolbar`, `st.setQuery`).

### Won't Have (This Iteration)

- Any of the commented-out/dead legacy actions on `readers.php`: diagmode trigger, dongle
  restart, IMEI blacklist, `nullpin` shortcut — these were already disabled in the 2014 source
  and are not being resurrected.
- Live backend wiring for any action — this is a visual/UX prototype; actions push a command
  string into the existing mock command log / toast, exactly like every other page in this app.
- Deeper APDU protocol UI (hex validation, response parsing) — the legacy page itself never got
  further than "one text field, one submit."
- Reworking `HubsPage`'s tree/power logic — confirmed already correct; only its title changes.

## Constraints

- **Technical**: must reuse this codebase's established dense-admin-page architecture exactly
  (`ColDef`/`DenseTable`, `ActionGroup`/`SubAction`/`AdmField`, `TableHeading`/`TableToolbar`,
  `columnOrderFor`/`hiddenColumnsFor`, `AppState.push(cmd, logLines)` for command-log/toast
  side effects) — no new architectural pattern needed, this is additive within the existing
  shape (same conclusion the `zones`/`command_sets` flows reached for their features).
- **Visual source of truth**: `design/simbox-design-prototype-v2026-dc` (current brand/design
  system) governs colors, type, icon style for the new page — legacy `readers.php`'s actual
  2014 HTML/CSS is not to be replicated, only its logic/fields/actions.
- **Icons**: PL2303 chip icon already vendored (`assets/imgs/pl2303.png`), as is `lock.png`.
  No SIM-reader-specific or key/KI icon currently exists in the vendored Fugue subset
  (`assets/fugue/` has only 29 of the full 3,570-icon catalog) — Visual/Specifications phase
  should decide whether to vendor a new Fugue glyph (e.g. a card/chip icon) for the nav item
  and page heading, or reuse an existing asset, per `nativemind-fugue-icons` skill rules (no
  emoji/approximate fallbacks).
- **Dependencies**: none — additive, does not touch `zones`/`command_sets`/other in-flight work.

## Open Questions

- [ ] Nav icon for "Ридеры": reuse `lock.png` (already used inline in the reader table itself,
  so may read as redundant), vendor a new Fugue card/chip glyph, or reuse `pl2303.png` at nav
  size? — recommend deciding visually in the Visual phase rather than blocking Requirements on
  it.

## References

- `legacy/simbox-desktop-v2014/www/simbox/readers.php` (308 lines) — logic source of truth.
- `legacy/simbox-desktop-v2014/www/simbox/hubs.php` (392 lines) — contrast/confirmation source.
- `design/simbox-web-design-prototype-v2026/lib/pages/hubs_page.dart` — page to relabel.
- `design/simbox-web-design-prototype-v2026/lib/pages/dongles_page.dart` — PIN/AT-command UI
  precedent to mirror for the reader page's PIN/APDU actions.
- `design/simbox-web-design-prototype-v2026/lib/widgets/sidebar.dart` — nav tab list to extend.
- `design/simbox-design-prototype-v2026-dc` — visual design system source of truth.

---

## Approval

- [x] Reviewed by: Anton Dodonov
- [x] Approved on: 2026-09-02
- [x] Notes: Approved as drafted, scoped to Readers only (Hubs heading fix applied out of band,
  see scope note above).
