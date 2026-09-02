# Specifications: simbox-web-design-prototype-readers-uiux

> Version: 1.0
> Status: APPROVED
> Last Updated: 2026-09-02
> Requirements: [01-requirements.md](01-requirements.md)
> Visual: [02-visual.md](02-visual.md)

## Overview

Adds a `Reader` model, mock data, `AdmPage.readers`, a sidebar entry, and `ReadersPage` — a flat
dense-table page reusing this codebase's existing `ColDef`/`DenseTable`/`ActionGroup`/
`SubAction`/`AdmField` machinery, exactly as `HubsPage`/`DonglesPage` already do. No new
architecture: every piece below is a straight extension of an existing, already-shipped pattern.

## Affected Systems

| System | Impact | Notes |
|--------|--------|-------|
| `lib/data/models.dart` | Modify | Add `Reader` class |
| `lib/data/icon_map.dart` | Modify | Add `Ico.readerModel(String model)` |
| `lib/data/mock.dart` | Modify | Add `const readers = <Reader>[...]` (6 rows, per Visual) |
| `lib/state/app_state.dart` | Modify | Add `AdmPage.readers`; `visibleReaders` getter; `runOnReaders(...)` helper (mirrors `runOnDongles`) |
| `lib/widgets/sidebar.dart` | Modify | Insert `(AdmPage.readers, 'Ридеры', 'pl2303.png')` before the `AdmPage.hubs` tuple in `_tabs` |
| `lib/pages/readers_page.dart` | Create | New page widget |
| `lib/main.dart` | Modify | Import + `AdmPage.readers => const ReadersPage()` switch arm |

## Data Models

### New Type — `Reader`

```dart
// lib/data/models.dart — new class, alongside HubNode/Dongle
class Reader {
  final int id;
  final String model;      // raw model code from readers.php's $model, e.g. '1001'; '' = unrecognized
  final String device;     // reader id string (readers.list entry) — shown in the "ридер" column
  final String lock;       // free-text, '' when absent (readers.php: $device.lock)
  final String state;      // e.g. 'Not connected', 'OK', 'Reading', 'Error'
  final String stateFault; // '' when the per-card result is 0 or 1000; else the fault code, e.g. '12'
                            // — rendered via Cell(text: state, sub: stateFault), the same
                            // two-line cell pattern ColDef already uses for Dongle's cell/lac
                            // and oper/operSub, not concatenated into one string.
  final String spn;        // operator name off the card, '' if no card
  final String iccid;
  final String pin;        // '' = no PIN on file (distinct from '0000', a real stored PIN)
  final String imsi;
  final String ki;         // '00' = all-zero placeholder (not yet found); else the found hex key
  final int progressDone;  // 0 = no KI search in progress
  final int progressTotal; // legacy constant 31044 (see readers.php:227); 0 when progressDone is 0
  final String dataport;   // e.g. '/dev/ttyUSB0'

  const Reader({
    required this.id,
    required this.model,
    required this.device,
    required this.lock,
    required this.state,
    this.stateFault = '',
    required this.spn,
    required this.iccid,
    required this.pin,
    required this.imsi,
    required this.ki,
    this.progressDone = 0,
    this.progressTotal = 0,
    required this.dataport,
  });

  bool get hasCard => iccid.isNotEmpty;
  String get progressDisplay => progressDone > 0 ? '$progressDone/$progressTotal' : '';

  /// Search haystack for the toolbar's filter box (mirrors Dongle.haystack/Sim.haystack).
  String get haystack => '$device $state $spn $iccid $imsi $dataport'.toLowerCase();
}
```

### `icon_map.dart` addition

```dart
// lib/data/icon_map.dart — inside class Ico, alongside dongle()
static IcoRef? readerModel(String model) => switch (model) {
      '1001' => const IcoRef('pl2303.png', 'PL2303'),
      _ => null, // unrecognized/absent model — Cell renders no icon
    };
```

Returns `null` rather than a sentinel empty `IcoRef` — the `ColDef` build callback does
`icons: [if (Ico.readerModel(r.model) case final ico?) ico]`, so `Cell` simply gets an empty
icon list for unrecognized models.

## Mock Data

```dart
// lib/data/mock.dart — new const, alongside hubTree
const readers = <Reader>[
  Reader(id: 201, model: '1001', device: 'reader1', lock: '', state: 'Not connected',
      spn: '', iccid: '', pin: '', imsi: '', ki: '', dataport: '/dev/ttyUSB0'),
  Reader(id: 202, model: '1001', device: 'reader2', lock: 'locked', state: 'OK',
      spn: 'Beeline', iccid: '8979025912345634471', pin: '1234', imsi: '250014912345671',
      ki: 'A1B2C3D4E5F60718293A4B5C6D7E8F90', dataport: '/dev/ttyUSB1'),
  Reader(id: 203, model: '1001', device: 'reader3', lock: '', state: 'Reading',
      stateFault: '12', spn: 'MTS', iccid: '8977011912345631183', pin: '', imsi: '250991912345699',
      ki: '00', progressDone: 812, progressTotal: 31044, dataport: '/dev/ttyUSB2'),
  Reader(id: 204, model: '1001', device: 'reader4', lock: 'locked', state: 'OK',
      spn: 'MegaFon', iccid: '8977029012345632290', pin: '0000', imsi: '250021912345678',
      ki: 'F3C9A87654321000FEDCBA9876543210', dataport: '/dev/ttyUSB3'),
  Reader(id: 205, model: '1001', device: 'reader5', lock: '', state: 'Error',
      spn: '', iccid: '8979007112345630071', pin: '', imsi: '', ki: '00', dataport: '/dev/ttyUSB4'),
  Reader(id: 206, model: '', device: 'reader6', lock: '', state: 'Not connected',
      spn: '', iccid: '', pin: '', imsi: '', ki: '', dataport: '/dev/ttyUSB5'),
];
```

Matches Requirements Acceptance Criteria #5 and the row-by-row rationale already written into
`02-visual.md`'s idle-table screen (no-card/no-model, fully-ID'd with resolved KI, literal
`0000` PIN, mid-search with fault suffix + progress, card-present error, no-card/no-model).

## `AppState` changes

```dart
// lib/state/app_state.dart

enum AdmPage {
  sim, dongle, diagmode,
  readers,   // NEW — inserted here so it's adjacent to hubs in both the enum and the sidebar
  hubs,
  nabor, zones, plan, proc, bablo, upgrade, debug, icons
}

// alongside visibleDongles:
List<Reader> get visibleReaders {
  var list = readers // from data/mock.dart
      .where((r) => query.isEmpty || r.haystack.contains(query.toLowerCase()))
      .toList();
  final k = sortKey;
  if (k != null) list.sort((a, b) => _cmp(a.field(k), b.field(k)) * sortDir);
  return list;
}

// alongside runOnDongles:
void runOnReaders(LogEntry Function(Reader) build,
    {String? toastText, String icon = 'free.png'}) {
  final rows = visibleReaders.where((r) => selected.contains(r.id)).toList();
  if (rows.isEmpty) {
    showToast('Не выбрано ни одного ридера', 'stop.png');
    return;
  }
  for (final r in rows.take(4)) {
    final e = build(r);
    push(e.cmd, e.lines, e.warn);
  }
  showToast(toastText ?? 'Отправлено: ${rows.length}', icon);
}
```

`visibleReaders`'s sort branch calls `r.field(k)` — **open design question**, see below: `Sim`/
`Dongle` implement a `field(String key)` dynamic accessor for generic sort; `Reader` needs the
same small switch-on-key method (mechanical, one line per column) for sort-by-column to work,
matching the existing convention rather than inventing a different sort mechanism.

## `sidebar.dart` change

```dart
const _tabs = <(AdmPage, String, String)>[
  (AdmPage.sim, 'Симки', 'free.png'),
  (AdmPage.dongle, 'Свистки (nm)', 'dongle1550.png'),
  (AdmPage.diagmode, 'Свистки (um)', 'diagmode/diagmode_update.png'),
  (AdmPage.readers, 'Ридеры', 'pl2303.png'),   // NEW — directly before Хабы
  (AdmPage.hubs, 'Хабы', 'usb/hub_16.png'),
  // ...unchanged rest...
];
```

## `main.dart` change

```dart
import 'pages/readers_page.dart';
// ...
Widget _page(AdmPage p) => switch (p) {
      // ...
      AdmPage.readers => const ReadersPage(),
      AdmPage.hubs => const HubsPage(),
      // ...
    };
```

## New Widget — `lib/pages/readers_page.dart`

Structural shape is a direct adaptation of `hubs_page.dart`/`dongles_page.dart`:

```dart
class ReadersPage extends StatefulWidget { ... }
class _ReadersPageState extends State<ReadersPage> {
  final _search = TextEditingController();
  final _removePin = TextEditingController();
  final _setPin = TextEditingController();
  final _apdu = TextEditingController();

  List<ColDef<Reader>> _cols() => [
    ColDef(key: 'model', w: 38, title: 'модель',
        build: (r) => Cell(icons: [if (Ico.readerModel(r.model) case final ico?) ico])),
    ColDef(key: 'device', w: 90, label: 'Ридер', build: (r) => Cell(mono: r.device)),
    ColDef(key: 'lock', w: 70, label: 'lock', build: (r) => Cell(text: r.lock)),
    ColDef(key: 'state', w: 100, label: 'state',
        build: (r) => Cell(text: r.state, sub: r.stateFault)),
    ColDef(key: 'spn', w: 90, label: 'SPN', build: (r) => Cell(text: r.spn)),
    ColDef(key: 'iccid', w: 150, label: 'ICCID', build: (r) => Cell(mono: r.iccid)),
    ColDef(key: 'pin', w: 60, label: 'PIN', build: (r) => Cell(mono: r.pin)),
    ColDef(key: 'imsi', w: 140, label: 'IMSI', build: (r) => Cell(mono: r.imsi)),
    ColDef(key: 'ki', w: 260, label: 'KI', build: (r) => Cell(mono: r.ki.isEmpty ? '00' : r.ki)),
    ColDef(key: 'progress', w: 90, label: 'прогр', build: (r) => Cell(text: r.progressDisplay)),
    ColDef(key: 'dataport', w: 110, label: 'dataport', build: (r) => Cell(mono: r.dataport)),
  ];
  // _visibleCols(...) identical shape to HubsPage's (columnOrderFor/hiddenColumnsFor keyed by AdmPage.readers)

  List<ActionGroup> _groups(AppState st) => [
    ActionGroup(key: 'refresh', label: 'Обновить', icon: 'free.png', subActions: [
      SubAction(key: 'all', label: 'Обновить',
          builder: (_) => AdmButton('Обновить', primary: true,
              onPressed: () => st.showToast('Обновлено', 'free.png'))),
    ]),
    ActionGroup(key: 'pin', label: 'PIN', icon: 'lock.png', subActions: [
      SubAction(key: 'all', label: 'PIN', builder: (_) => Wrap(spacing: 12, runSpacing: 8, children: [
        Row(mainAxisSize: MainAxisSize.min, children: [
          AdmField(_removePin, hint: 'PIN', width: 90),
          const SizedBox(width: 8),
          AdmButton('Снять PIN', onPressed: () => st.runOnReaders(
              (r) => LogEntry('', "asterisk -rx 'dongle cmd ${r.device} "
                  "AT+CPIN=\"${_removePin.text.isEmpty ? '0000' : _removePin.text}\";"
                  "+CLCK=\"SC\",0,\"${_removePin.text.isEmpty ? '0000' : _removePin.text}\";+CFUN=1,1'",
                  const ['OK']),
              toastText: 'PIN снят', icon: 'lock.png')),
        ]),
        Row(mainAxisSize: MainAxisSize.min, children: [
          AdmField(_setPin, hint: 'новый PIN', width: 90),
          const SizedBox(width: 8),
          AdmButton('Установить PIN', primary: true, onPressed: () => st.runOnReaders(
              (r) => LogEntry('', "asterisk -rx 'dongle cmd ${r.device} "
                  "AT+CLCK=\"SC\",1,\"${_setPin.text}\";+CFUN=1,1'", const ['OK']),
              toastText: 'PIN установлен', icon: 'lock.png')),
        ]),
      ])),
    ]),
    ActionGroup(key: 'kisearch', label: 'Поиск KI', icon: 'pl2303.png', subActions: [
      SubAction(key: 'all', label: 'Поиск KI',
          builder: (_) => AdmButton('Запустить поиск KI', primary: true,
              onPressed: () => st.runOnReaders(
                  (r) => LogEntry('',
                      'wts --svistokmode=1 --device=reader --speed=9600 --ignorects '
                      '--port=${r.dataport} --dev=${r.device}',
                      const ['поиск запущен']),
                  toastText: 'Поиск KI запущен', icon: 'pl2303.png'))),
    ]),
    ActionGroup(key: 'apdu', label: 'APDU-команда', icon: 'terminal.png', subActions: [
      SubAction(key: 'all', label: 'APDU-команда',
          builder: (_) => Row(mainAxisSize: MainAxisSize.min, children: [
            AdmField(_apdu, mono: true, width: 200),
            const SizedBox(width: 8),
            AdmButton('Выполнить', primary: true, onPressed: () => st.runOnReaders(
                (r) => LogEntry('', 'apdu ${r.device} ${_apdu.text}', const ['OK']),
                toastText: 'APDU-команда')),
          ])),
    ]),
  ];

  @override
  Widget build(BuildContext context) {
    final st = AppScope.of(context);
    final rows = st.visibleReaders;
    return Padding(
      padding: const EdgeInsets.all(22),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        TableHeading(title: 'Ридеры', count: rows.length),
        const SizedBox(height: 10),
        TableToolbar(groups: _groups(st), search: _search, onSearch: st.setQuery,
            page: AdmPage.readers,
            allColumns: [for (final c in _cols()) (key: c.key, label: columnDisplayLabel(c))]),
        if (st.activeGroup == 'kisearch') ...[
          const SizedBox(height: 8),
          _KiWarningBanner(),
        ],
        const SizedBox(height: 12),
        Expanded(child: DenseTable<Reader>(
          cols: _visibleCols(st, _cols()), rows: rows, idOf: (r) => r.id,
          isSelected: st.isSelected, onToggleRow: st.toggleRow,
          onToggleAll: () => st.toggleAll(rows.map((e) => e.id).toList()),
          sortKey: st.sortKey, sortDir: st.sortDir, onSort: st.sortBy,
        )),
      ]),
    );
  }
}
```

### `_KiWarningBanner` — new small private widget in `readers_page.dart`

```dart
class _KiWarningBanner extends StatelessWidget {
  @override
  Widget build(BuildContext context) => Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: const Color(0x1AE5484D), // reuse existing danger-tint pattern (see Open
                                           // Design Questions — exact token TBD)
          borderRadius: BorderRadius.circular(T.radiusCtl),
          border: Border.all(color: const Color(0x59E5484D)),
        ),
        child: const Text(
          'Внимание! Во время подбора KI карта недоступна для других операций.',
          style: TextStyle(fontFamily: 'SF Pro Text', fontSize: 12, color: Color(0xFFB3261E)),
        ),
      );
}
```

Gated purely on `st.activeGroup == 'kisearch'` — no new state field needed, `AppState` already
tracks which action-group pill is open (`app_state.dart:44`, used today only to drive
`ActionGroupPill`'s open/closed rendering; this is its first read from outside that widget).

## Behavior Specifications

### Happy Path

1. Operator opens "Ридеры" from the sidebar → `ReadersPage` renders `readers` mock data via
   `st.visibleReaders`, respecting any active search filter and column order/visibility for
   `AdmPage.readers`.
2. Operator checks one or more rows, opens an action group, fills any required field, and
   presses the group's run button → `st.runOnReaders(...)` pushes one `LogEntry` per selected
   row (capped at 4, matching `runOnDongles`'s existing cap) and shows a toast.
3. Closing the group (`[<]`) or pressing Escape (already global, `main.dart:95-97`) clears
   `activeGroup`, hiding the KI warning banner if it was showing.

### Edge Cases

| Case | Trigger | Expected Behavior |
|------|---------|--------------------|
| No rows selected, action group run pressed | Operator opens a group without checking any row | `runOnReaders` shows "Не выбрано ни одного ридера" toast, no log entries pushed (mirrors `runOnDongles`'s existing empty-selection guard) |
| KI already `"00"` for a row not mid-search | `progressDone == 0` and `ki == '00'` | Renders `"00"`, blank progress cell — same as a plain "not yet found" row (`reader5`), not visually distinguished from a genuinely-idle unfound-KI row; no separate visual state needed since legacy itself doesn't distinguish these two |
| Empty PIN field, "Снять PIN" pressed | Operator clicks without typing a PIN | Falls back to `'0000'`, matching `readers.php`'s own default-less `enterpin` path AND `DonglesPage`'s existing identical fallback (`dongles_page.dart:115`) |
| Unrecognized/blank `model` | `model != '1001'` | `Ico.readerModel` returns `null`, `Cell(icons: [])` renders no icon — same convention as `Ico.dongle`'s `_ => 'dongle.png'` fallback is *not* mirrored here, because legacy's own fallback for readers is "print the raw code" or nothing, not a generic reader icon (no such asset exists) |
| Column sort by `ki` or `iccid` | Operator clicks those column headers | `Reader.field(key)` returns the string as-is; string comparison sorts lexicographically — acceptable for a prototype (same as `Sim`/`Dongle`'s existing string-column sort behavior) |

### Error Handling

Not applicable — this is a mock-data prototype with no real backend calls; every action is a
synchronous local state mutation (`push`/`showToast`), matching every other page.

## Dependencies

### Requires

Nothing beyond what's already in the repo — no changes to `zones`/`command_sets`/other in-flight
flows.

### Blocks

Nothing currently depends on this.

## Integration Points

### Internal Systems

- `AppState.columnOrderFor`/`hiddenColumnsFor` (keyed by the new `AdmPage.readers`) — existing
  mechanism, no changes needed to the methods themselves.
- `CommandLog` widget — receives pushed `LogEntry`s exactly as from every other page; no changes.

## Testing Strategy

### Manual Verification

- [ ] Sidebar shows "Ридеры" directly before "Хабы"; clicking it renders the new page; the
      previously-selected page's selection/sort/query state doesn't leak in (matches existing
      per-page `AppState.query`/`selected` reset behavior — confirm `goTo` already clears these,
      since `HubsPage`/`DonglesPage` rely on the same behavior today).
- [ ] All 6 mock rows render with the expected per-column values from Mock Data above.
- [ ] Each of the 4 action groups opens/closes correctly; running each pushes a `LogEntry`
      visible in `CommandLog`, with a toast.
- [ ] Opening "Поиск KI" shows the red banner; closing the group (or Escape) hides it.
- [ ] Column show/hide + reorder works and persists while the app is open (matches existing
      per-`AdmPage` column-state behavior, not persisted across reloads — same as every other
      page).
- [ ] `flutter analyze` and existing test suite (`test/*.dart`) still pass after the change.

## Open Design Questions

- [ ] **Danger/warning color token**: the codebase's `design/tokens.dart` (`T.*`) doesn't
  currently expose a named danger/red token used elsewhere for a *persistent inline banner*
  (only ad-hoc reds inside dialogs) — confirm whether to add `T.danger`/`T.dangerBg` tokens for
  reuse, or keep the one-off `Color(0x1AE5484D)`/`Color(0xFFB3261E)` literals shown above scoped
  to `_KiWarningBanner` only, since this is the first persistent (non-dialog, non-toast) warning
  surface in the app. Leaning towards the scoped literals for now (smallest change), but calling
  it out since a future flow will likely want the same treatment and shouldn't have to
  reverse-engineer these exact values from this file.
- [ ] **`Reader.field(key)` sort accessor**: mechanical (one switch arm per column), to be
  written during implementation — no design ambiguity, just noting it's not spelled out
  line-by-line above to avoid restating all 11 columns twice.

---

## Approval

- [x] Reviewed by: Anton Dodonov
- [x] Approved on: 2026-09-02
- [x] Notes: Approved as drafted, including the leaning decisions on both Open Design Questions
  (scoped color literals over new design tokens; mechanical per-column sort accessor left
  unspelled in the doc).
