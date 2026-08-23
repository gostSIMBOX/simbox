# Specifications: simbox-app-uiux

> Version: 1.3 (navigation-shell specifics **extracted 2026-08-23 into
> `vdd-simbox-app-navbar-uiux`** at Anton's explicit instruction — a
> small clarifying note added where `lib/navigation/` is referenced.
> The earlier "Каналы Redesign" extraction into
> `vdd-simbox-app-channel-table-uiux` still stands, unaffected.)
> Status: APPROVED
> Last Updated: 2026-08-23
> Visual: [02-visual.md](02-visual.md) — v1.4 APPROVED 2026-08-23

## Assumption Locked In (per Anton's "approved" without override)

The "web in browser" / "web from phone" legacy layouts flagged as an open
item in 02-visual.md are treated as **out of scope** for this flow (design
precedent only, not a build target) — my recommended default, since no
correction came back. Revisit if this turns out wrong; it's cheap to add
a `sdd-simbox-app-web-admin`-style flow later since it doesn't touch the
native app's architecture.

## Note: "Каналы Redesign" work moved out (2026-08-23)

This document previously carried a "Каналы Redesign" amendment section
(screen rename to "Каналы", `ChannelViewMode`, expandable-row table,
`UiPreferences` + Настройки → Интерфейс toggle). At Anton's explicit
instruction, that entire section has been **extracted into
`vdd-simbox-app-channel-table-uiux/03-specifications.md`**, unchanged.
See that document for the full data models, widget decision, settings
section, and dependency-gap writeup. Everywhere below, "Симки" is this
flow's own original screen name and scope — the rename/dual-view-mode
work is out of scope here now.

## 2015 Column Audit (resolves 02-visual.md's Open Item on the 33-column claim)

Read `legacy/simbox-desktop-v2015/www/simbox/sim.php` (the real header row,
~line 1097-1178). Confirmed column set, in order:

```
[checkbox] group | pro | cap | im | spec | state | plan(nabor/tarif) |
number | operator/sim | balance/bal_diff | dongle |
tot(IMB/C · IMN/D/E) | a-o/a-i | m-o/m-i | ACD-o | ACD-i | ACDL | DATT |
IATT | SATT | sms_out(_sended) | ASRL | PDDAS | PDDL0 | PDDL1 | pri |
LIMIT0..LIMIT5 (6 cols) | LAC | CELL | IMEI | IMSI | log |
timestamps(засунут/первый звонок/последний успешный/автоблокировка)
```
~38 raw columns (design doc's "33" likely counts after dropping the
commented-out `<!-- -->` blocks visible in the same file, e.g. the
diff_min/start-end-time/state-icon columns that were disabled in 2015
itself).

### Consolidation into the 2026 dense table (per DS icon-stack guidance)

| 2015 columns | 2026 representation | UI data source |
|---|---|---|
| `pro`,`cap`,`im`,`spec` | icon stack (captcha/multi-SIM/spec flags) | new `ModemDevice.flags` — **addendum needed**, see Dependency Gaps |
| `state` | state icon (`assets/adminka/state/{cfun,simst,srvst}`) | `ModemDevice.state` (`ModemState`) |
| `plan`/`nabor`/`tarif` | text line under number ("план default") | `ModemDevice.groupId` → resolved plan/carrier display name |
| `number` | primary cell text | `ModemDevice` — **addendum needed**: no phone-number field on `ModemDevice` today |
| `operator`/`sim` | operator icon (`napravleine/*`) | `CarrierProfile.operatorId` resolved from ICCID/IMSI |
| `balance`/`bal_diff` | right-aligned stat, secondary delta line | `ModemDevice.balance` (delta — **addendum needed**) |
| `dongle` | hub/port meta line | `ModemDevice.portPath` |
| `tot`,`a-o/a-i`,`m-o/m-i`,`ACD-o/i`,`ACDL`,`DATT`,`IATT`,`SATT`,`ASRL`,`PDDAS`,`PDDL0/1` | detail-panel stat tiles (not all in the list row) | new `ModemStatistics` entity — **addendum needed** |
| `sms_out`/`_sended` | SMS icon in state-icon stack | derived from `ModemEvent`/SMS history, not a device field |
| `pri`,`LIMIT0..5` | `ModemGroupConfig` (already speced) | `ModemGroupConfig.priority`, `.limitMaxByPeriod` |
| `LAC`,`CELL` | Identifiers block in detail panel | new fields — **addendum needed** on `ModemDevice` |
| `IMEI`,`IMSI` | Identifiers block | already on `ModemDevice` |
| `log` | "Вывод команд" panel | AT command log, not a device field (transient/streamed) |
| timestamps (засунут/первый/последний/автоблок) | meta row under list card | new fields — **addendum needed** |

### Dependency Gaps (raise with `sdd-flutter_gsmsip-interface`, not blocking here)

`ModemDevice` (as specified) covers id/portPath/displayName/manufacturer/
model/imei/imsi/iccid/groupId/state/signal/registration/balance — enough
for Модемы/Линии screens and the detail panel's core stats, but the
**Симки** screen needs additional fields the interface spec didn't
anticipate (phone number, LAC/CELL, ACDL/DATT/IATT/SATT/ASRL call
statistics, autoblock reason + timestamp, balance delta, captcha/spec
flags, засунут/first-call/last-success timestamps). Two options, to
propose to Anton before `vdd-simbox-app-uiux` implementation starts (this
is a PLAN-phase decision, not a blocker for finishing this flow's own
specs/plan):

1. Extend `ModemDevice` + add a `ModemStatistics` entity in a small
   addendum to `sdd-flutter_gsmsip-interface` (cleanest — keeps the UI
   thin).
2. Model these as a `SimBoxLine` UI-layer view-model in `apps/simbox-app`
   that composes `ModemDevice` with locally-tracked/derived fields until
   the interface grows them (faster to start, more rework later).

**Recommendation**: option 1, as a follow-up addendum PR to the interface
flow once its Task 1-14 plan lands — don't reopen its already-approved
02-specifications.md mid-flight. This flow's own specs below are written
against the *interface as currently approved*, with the gaps visibly
marked so nothing is silently faked.

## Affected Systems / Components

| Component | Change |
|---|---|
| `apps/simbox-app/lib/theme/` | Reconcile `app_colors.dart`/`app_dimensions.dart`/`app_gradients.dart`/`app_theme.dart` against `nativemind-designsystem-v1.8/tokens/*.css` |
| `apps/simbox-app/lib/screens/` (new) | `sims/`, `modems/`, `operations/` (calls+sms), `settings/` — one folder per tab |
| `apps/simbox-app/lib/widgets/` (new) | Shared: `DenseModemTable`, `EntityCard` (phone list card), `DetailPanel`, `StatTile`, `ActionChip`, `FilterChipRow`, `BottomActionSheet`/`ActionPopover`, `UssdConsole`, `CommandLog`, `SettingsForm` |
| `apps/simbox-app/lib/state/` (new) | State management layer (see Data Models) consuming `ModemRepository` |
| `apps/simbox-app/assets/` (new) | Per-glyph vendored icons from `nativemind-designsystem-v1.8/assets/{adminka,fugue}`, SF Pro Text TTFs |
| `apps/simbox-app/pubspec.yaml` | Add `flutter_gsm` (path dependency — **corrected here**: this table originally said `flutter_gsmsip`, written before that package split; `apps/simbox-app` actually depends on `flutter_gsm` directly per `sdd-flutter_gsm-ffi`, confirmed by reading its real `pubspec.yaml`), font/asset declarations, `two_dimensional_scrollables` (dense table — see Widget Decision; already a resolved dependency, confirmed via `pubspec.lock`) |
| `apps/simbox-app/lib/main.dart` | Replace demo `DashboardScreen` with real tab navigation shell |

`apps/simbox-app/lib/navigation/` (`app_shell.dart`, `breakpoints.dart`
— the navigation shell itself: destinations, order, breakpoint-switched
chrome) is specified in `vdd-simbox-app-navbar-uiux/03-specifications.md`,
not here, per the 2026-08-23 extraction.

`vdd-simbox-app-channel-table-uiux/03-specifications.md` has its own
Affected Systems table for the "Каналы" rename/dual-view-mode/
`UiPreferences`/`ViewModeSwitcher` additions built on top of the table
above.

## Widget Decision (resolves 01-requirements.md's open question)

**Dense table**: use `package:two_dimensional_scrollables`'s `TableView`
(Flutter-team-maintained, successor space to the deprecated `TwoDimensionalScrollable`
examples) rather than a community `DataTable2`-style package. Reasons:
native pinned-row/pinned-column support, built for large dense datasets,
single synchronized horizontal+vertical scroller — matches the DS's "CSS
grid + `min-width:max-content` + one scroller" requirement exactly, and
avoids a heavier third-party table dependency for a Flutter-desktop-first
app. `DenseModemTable` wraps it with the DS's zebra/stacked-cell/icon-stack
styling baked in as a themed `TableSpan` builder.

## Data Models (UI state layer)

- `SimBoxLine` (UI view-model, composes `ModemDevice` +
  `ModemGroupConfig` + resolved `CarrierProfile`, with the Dependency-Gap
  fields as **nullable placeholders** until the interface addendum lands —
  UI renders "—" for unavailable fields rather than fabricating data).
- `ModemLineListController` — subscribes to `ModemRepository.modemEvents`,
  maintains the sorted/filtered `List<SimBoxLine>` backing Симки/Модемы
  screens; filter-chip state, search query, and selection set live here.
  (`vdd-simbox-app-channel-table-uiux` extends this same controller with
  view-mode and modem-expansion state — see that flow's specifications.)
- `CallLogController` / `SmsLogController` — subscribe to
  `ModemEvent.ModemCallStateChanged`/`ModemSmsReceived`, append to an
  in-memory log (persistence out of scope — matches interface flow's own
  deferred-persistence stance).
- `DetailPanelController` — per-selected-line: stats, actions, USSD
  console state, command log tail (bounded ring buffer, e.g. last 200
  lines, to match "Вывод команд" being a live tail, not a full history
  browser).
- State management approach: no framework prescribed here beyond "not
  raw `setState` for cross-widget state" — pick `ChangeNotifier`+`provider`
  or `riverpod` at PLAN time (project has no existing precedent in
  `apps/simbox-app`; check `pubspec.yaml`/other NativeMind Flutter apps for
  the house convention before deciding, since the DS assets originate from
  the VPN Client codebase which may already have a convention worth
  matching).

## Behavior / Edge Cases

- **Driver not available** (`ModemDriverNotAvailable` from the interface
  flow, expected on Linux until `sdd-flutter_gsmsip-channel` lands): show
  a persistent banner on Симки/Модемы ("Драйвер модемов не подключён")
  rather than an empty-state — distinct from the prototype's legitimate
  "Ничего не найдено по фильтру" empty state.
  - **Practical near-term impact**: since this flow's implementation is
    gated to start only after `sdd-flutter_gsmsip-interface` ships, and
    that flow's Linux stub always throws `UnimplementedError`
    (`ModemDriverNotAvailable`) until `sdd-flutter_gsmsip-channel` exists,
    the Симки/Модемы/Звонки/СМС screens will show this banner for their
    entire real-device lists through this flow's whole implementation —
    build and visually verify against **mock/fake `ModemRepository` data**
    (a `FakeModemRepository` test double seeded with prototype-like sample
    rows), not the real driver, until the channel flow lands.
- **Loading/waking modem** ("просыпается"): `ModemState` transitional
  value between `init`→`ready`; row shows a subtle pulsing/skeleton state
  on the state icon, not a spinner overlay (matches DS motion guidance:
  bounded, soft, no ambient loops beyond the documented connect-button
  pulse pattern — reuse that cadence).
- **Captcha not passed** ("капча не пройдена"): distinct alarm state on
  the row (danger-red alarm line, per visual mockup), separate from
  autoblock.
- **Low balance** ("недостаточно средств"): app-level banner, not a
  per-row concern — shown when SMPP/SIP registration or a send action
  fails due to balance per the prototype copy.
- **Unsaved settings**: `SettingsForm` tracks dirty state locally; banner +
  Save/Reset per 02-visual.md; leaving the section with unsaved changes
  should prompt (standard Flutter `PopScope`/route-guard pattern), not
  silently discard.
- **Bulk actions on mixed-state selection**: if selected rows have
  incompatible states for an action (e.g. "Включить передатчик" on an
  already-on line), the action sheet still lists it — per-row success/
  failure is reported via toast/summary after execution, not pre-filtered
  (matches legacy behavior: bulk `dongle` CLI commands didn't
  pre-validate per-device either).

## Dependencies / Integration Points

- Hard dependency: `sdd-flutter_gsmsip-interface` implementation complete
  (`ModemRepository`, entities, event stream) — this flow's
  IMPLEMENTATION phase does not start before that (per 01-requirements.md
  Constraints).
- Soft dependency (flagged, not blocking): the `ModemDevice`/
  `ModemStatistics` field addendum described above — needed for full
  Симки fidelity, but the UI can ship with placeholder "—" values and
  backfill once the addendum lands, so it doesn't block this flow's plan.
- Asset dependency: `design/nativemind-designsystem-v1.8/assets/{adminka,
  fugue,fonts}` — vendor per-glyph into `apps/simbox-app/assets/` at PLAN/
  IMPLEMENTATION time as each screen is built (not all upfront).

---

## Approval

- [x] Reviewed by: Anton Dodonov
- [x] Approved on: 2026-08-23
- [x] Notes: v1.3 reflects the 2026-08-23 extraction of the "Каналы
      Redesign" amendment section into
      `vdd-simbox-app-channel-table-uiux` and the navigation-shell
      specifics into `vdd-simbox-app-navbar-uiux` — no new content
      approval needed here, the underlying v1.0 approval for this
      flow's own scope stands unchanged.
