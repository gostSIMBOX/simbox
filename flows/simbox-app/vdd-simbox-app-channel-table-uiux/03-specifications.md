# Specifications: simbox-app-channel-table-uiux

> Version: 1.0
> Status: APPROVED
> Last Updated: 2026-08-23
> **Extracted 2026-08-23 from `vdd-simbox-app-uiux` v1.1's "Каналы
> Redesign" amendment section** — content unchanged by the extraction,
> only relocated and lightly re-scoped to stand alone.
> Visual: [02-visual.md](02-visual.md) — APPROVED 2026-08-23

## Overview

This is the extracted, self-contained specification for the "Каналы"
screen rename + dual view mode + table-view-anywhere toggle, built on
top of `vdd-simbox-app-uiux`'s base screens (Tasks 1-13: navigation
shell, theme, `ModemDevice`/`SimBoxLine`/`ModemLineListController`,
`DenseModemTable`). Everywhere below, "Каналы" refers to the screen
`vdd-simbox-app-uiux` originally called "Симки" — see that flow's
01-requirements.md CRITICAL note for why/how it was renamed.

## Data Models — additions to `vdd-simbox-app-uiux`'s base

- **`ChannelViewMode`** (enum: `byModem`, `bySimAll`) — which of the
  two Каналы view modes (02-visual.md) is active. Drives both which
  data-shaping the table/list gets and which widget renders on
  phone/tablet (card list vs. table, per the `Табличный вид` toggle
  below).
- **`ModemLineListController`** (from `vdd-simbox-app-uiux`, extended
  here) additionally tracks: a `Set<String> expandedModemIds` (which
  modem parent rows are expanded in По-модемам view — persists only
  for the session, not across restarts, matching the DS's general
  "expand/collapse state isn't a saved preference" convention
  elsewhere), and exposes a **flattened row list** derived from
  `List<SimBoxLine>` + grouping + `expandedModemIds`: for По-модемам,
  modems hosting >1 channel become a synthetic parent row followed by
  their channel rows only when expanded (collapsed modems contribute
  zero rows to the flattened list, per the Widget Decision below);
  modems hosting exactly 1 channel skip the parent row entirely (no
  pointless nesting, per 02-visual.md). For По-SIM-все, the flattened
  list is just `List<SimBoxLine>` unchanged (already flat) — **interim
  scope**: only seated channels, since `sdd-flutter_gsmsip-interface`
  doesn't yet expose unseated SIM cards (see Dependency Gaps below).
- **`SimBoxLine`** (from `vdd-simbox-app-uiux`, extended here) gains a
  `modemGroupKey` getter grouping channels by exact `ModemDevice.
  portPath` match — the only real physical-location signal
  `ModemDevice` exposes today (no dedicated "parent modem" field
  exists; a dual-SIM/dual-line modem would appear as two independent
  `ModemDevice`s with no link between them otherwise). A device with
  no `portPath` falls back to its own `id` (always a singleton group).
  Documented as a pragmatic heuristic, not a real field — revisit if
  `sdd-flutter_gsmsip-interface` ever adds a dedicated modem-grouping
  field.
- **`UiPreferences`** (new, small `ChangeNotifier`, backed by
  `shared_preferences` — already a pubspec dependency, unused for this
  purpose until now): holds `bool preferTableView` (the Настройки →
  Интерфейс → "Табличный вид на любом экране" toggle), default
  `false`. Read by Каналы to decide card-list vs. dense-table rendering
  on phone (tablet/desktop always shows the table regardless of this
  flag — that was already true in `vdd-simbox-app-uiux`'s base
  screens, per its AC #3). **Scoped down from the original design
  during implementation (2026-08-23)**: does not extend to Модемы —
  that screen's real tablet/desktop layout turned out to be a flat
  `ListView`, not a `DenseModemTable`, so there's no existing table
  representation for the toggle to surface on phone; see 02-visual.md's
  Модемы cross-reference correction. Persists across restarts per
  requirements AC #1; takes effect immediately, no explicit
  Сохранить/Сброс step (it's a display preference, not a form field —
  see 02-visual.md's Настройки → Интерфейс mockup).

## Widget Decision — expandable rows built on top of `TableView`

Confirmed by reading the actual installed package source
(`two_dimensional_scrollables-0.3.9/lib/src/table_view/table.dart`,
not assumed): `TableView` is a flat, fixed-`rowCount` grid with an
index-based `TableSpan` builder — no native row-expand/collapse or
tree concept. `DenseModemTable` (from `vdd-simbox-app-uiux`, needed
**zero code changes** for this) therefore takes the controller's
already-flattened row list (see above) directly as its row source;
`rowCount` is `flattenedRows.length`, and each `TableSpan`/cell builder
indexes into that same flattened list — expand/collapse is entirely a
**pre-processing** step before the table ever sees the data, not
something the table widget itself needs to know about. A modem parent
row's leading cell renders the `▾`/`▸` chevron and its tap handler
toggles that modem's id in `expandedModemIds`, triggering a rebuild
with a new (shorter or longer) flattened list — same pattern as any
other filter-driven row-list change the controller already handles.

Row union type: a sealed `ChannelRow` class with two variants —
`ModemGroupRow` (modem key, its channels, `expanded` bool) and
`ChannelLineRow` (wraps one `SimBoxLine`) — is the pre-flattened row
type `DenseModemTable<ChannelRow>` actually renders; column
`cellBuilder`s pattern-match on the variant.

## Settings — Интерфейс section (new)

`vdd-simbox-app-uiux`'s Настройки screen state gains a new "Интерфейс"
section (see 02-visual.md's mockup) with one `Switch`-backed row bound
to `UiPreferences.preferTableView`. Unlike the SIP/SMPP sections, this
has no server round-trip and no dirty-state/Save-Reset flow — toggling
it calls `UiPreferences.setPreferTableView(bool)` directly, which
persists to `shared_preferences` and notifies listeners synchronously.
Implementation seam: `_SettingsSection` (in `settings_screen.dart`)
gains an optional `customContent` widget builder for sections that
aren't a dirty-tracked form — "Интерфейс" is the first user of this
seam.

## Dependency Gaps

**По-SIM-все's "не в модеме" row** needs a capability `ModemDevice`
doesn't have at all today: representing a SIM card independent of any
modem. This is **not** a small field addition — flagged, recorded
verbatim, and addended to `sdd-flutter_gsmsip-interface` directly
(both copies, in `libsFlutter/flutter_gsm/flows/` and
`libsFlutter/flutter_gsmsip/flows/`, `02-specifications.md`'s
"Addendum" section and `_status.md`'s Blockers) rather than guessed at
here. **Interim scope**: По-SIM-все ships showing only seated channels
(same rows as По-модемам, flattened) — see 02-visual.md's mockup. No UI
rework will be needed when the interface addendum lands — only the
data source grows.

## Affected Systems / Components

| Component | Change |
|---|---|
| `apps/simbox-app/lib/state/channel_view_mode.dart` | New — `ChannelViewMode` enum |
| `apps/simbox-app/lib/state/channel_row.dart` | New — sealed `ChannelRow`/`ModemGroupRow`/`ChannelLineRow` |
| `apps/simbox-app/lib/state/ui_preferences.dart` | New — `UiPreferences` |
| `apps/simbox-app/lib/state/sim_box_line.dart` | Modify — `modemGroupKey` getter |
| `apps/simbox-app/lib/state/modem_line_list_controller.dart` | Modify — `viewMode`, `expandedModemIds`, `flattenedRows`, `setViewMode()`, `toggleModemExpanded()` |
| `apps/simbox-app/lib/state/fake_modem_repository.dart` | Modify — added a dual-channel sample modem to exercise expand/collapse |
| `apps/simbox-app/lib/widgets/view_mode_switcher.dart` | New — По модемам / По SIM, все segmented control |
| `apps/simbox-app/lib/screens/sims/sims_screen.dart` | Modify — Каналы rename, `_PhoneTable` (new), `_channelColumns()`/`_handleChannelRowTap()` (new, shared by `_SplitLayout` and `_PhoneTable`), `UiPreferences`-gated phone layout branch |
| `apps/simbox-app/lib/screens/settings/settings_screen.dart` | Modify — `_SettingsSection.customContent` seam, new "Интерфейс" section, `_InterfaceSettings` widget |
| `apps/simbox-app/lib/navigation/app_shell.dart` | Modify — tab label "Симки" → "Каналы" |
| `apps/simbox-app/lib/main.dart` | Modify — `MultiProvider` wrapping `ChangeNotifierProvider<UiPreferences>` alongside the existing `Provider<ModemRepository>` |
| `apps/simbox-app/lib/widgets/dense_modem_table.dart` | **Unchanged** — already generic enough, see Widget Decision |

## Testing Strategy

- Controller tests (`modem_line_list_controller_test.dart`):
  single-channel-modem-no-parent-row, multi-channel-modem-collapsed-
  by-default, toggle-reveals-then-hides-channel-rows, По-SIM-все flat
  with no `ModemGroupRow`, view-mode-switch-back-restores-tree.
- `UiPreferences` tests (`ui_preferences_test.dart`): default value,
  persistence round-trip via `SharedPreferences.setMockInitialValues`,
  no-op-if-unchanged doesn't notify.
- Existing `sims_screen_test.dart`/`widget_test.dart` updated: provide
  `ChangeNotifierProvider<UiPreferences>` (a new hard dependency of
  `SimsScreen`/`SettingsScreen`), rename "Симки"/"Выберите симку" text
  expectations to "Каналы"/"Выберите канал".

## Dependencies / Integration Points

- Built directly on top of `vdd-simbox-app-uiux`'s base screens
  (`ModemDevice`, `SimBoxLine`, `ModemLineListController`,
  `DenseModemTable`, `FakeModemRepository`) — not a standalone screen,
  cannot be implemented independently of that flow's Tasks 1-13.
- Soft dependency (flagged, not blocking): the SIM-inventory-
  independent-of-modem addendum to `sdd-flutter_gsmsip-interface` —
  needed for По-SIM-все's "не в модеме" row; ships seated-only until it
  lands (see Dependency Gaps above).
- Shared font-asset blocker with `vdd-simbox-app-uiux` — see that
  flow's `_status.md`; does not block this flow's code/tests, only
  final visual-fidelity sign-off.

---

## Approval

- [x] Reviewed by: Anton Dodonov
- [x] Approved on: 2026-08-23 (as `vdd-simbox-app-uiux` v1.1's "Каналы
      Redesign" amendment, before extraction into this flow)
- [x] Notes: Content unchanged by the extraction.
