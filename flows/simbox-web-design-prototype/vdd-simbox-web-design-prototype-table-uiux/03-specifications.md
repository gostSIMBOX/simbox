# Specifications: simbox-web-design-prototype-table-uiux

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-09-05
> Requirements: [01-requirements.md](01-requirements.md)
> Visual: [02-visual.md](02-visual.md)

## Overview

Additive/corrective pass on `SimsPage`'s existing column set (`sims_page.dart`'s `_cols()`), scoped
strictly to what 02-visual.md marked code-confirmed (not descoped). No new widget architecture: a
pass over every asset referenced below confirms `Cell`/`DenseTable`/`IconStack` already support
everything needed (multi-icon stacks via `Wrap`, multi-line cells via `note/icons/text/mono/warn/
sub/sub2`) — so this is `Sim` model fields + `ColDef` entries + `Ico`/`terminology.dart` additions
+ `mock.dart` seed data, not a `Cell`/`ColDef`/`DenseTable` redesign.

One correction from the Visual phase: that document listed 5 missing `terminology.dart` term IDs
as needed (`call.live.dial`, `call.live.active`, `call.result.busy`, `call.result.failed_unknown`,
`call.end.unknown`). Re-checking against `icons_catalog.dart` shows the latter 3 belong to the
**calls-log page's** result/end-party icon group (`icons_catalog.dart:28-31`'s
`call.result.answer`/`call.result.no_answer` entries are wired there, not in any live table) — a
different, out-of-scope page. `sim.php`'s STATE column only ever shows **live** states
(dial/ring/active/wait), never completed-call results. Only **2** new terms are actually needed:
`call.live.dial`, `call.live.active`.

## Affected Systems

| System | Impact | Notes |
|--------|--------|-------|
| `lib/data/models.dart` | Modify | Add ~18 fields to `Sim`; no changes to `Cell`/`ColDef`/`LogLink`/`IcoRef` |
| `lib/pages/sims_page.dart` | Modify | `_cols()`: 1 new column (`pro`), 6 columns widened in place (`spec`→5-icon stack, `io`→full live state, `may`→4 lines, `dongle`→+sub-line, `lim0`/`lim1`→+palevo icon, add `lim2..lim5`, add `pddas`), `_log()`/toolbar unchanged |
| `lib/data/icon_map.dart` | Modify | `Ico.group()`: add pause 2/12/22; `Ico.qos()`'s `_qosMap`: add `SPAM`/`IMO`/`SYS`; new `Ico.fas()`, `Ico.vip()`, `Ico.pre()`, `Ico.pos()`, `Ico.liveCall()` |
| `lib/data/terminology.dart` | Modify | Add `call.live.dial`, `call.live.active`, `qos.spam`, `qos.imo`, `qos.sys` (all already-approved wording from the icon-statuses flow's own manifest — not new invention) |
| `lib/data/mock.dart` | Modify | Extend every `Sim(...)` literal with the new fields; add scenario rows per Testing Strategy |
| `lib/data/icons_catalog.dart`, `lib/pages/icons_page.dart` | **No change** | Out of scope — that page's own flow (`vdd-simbox-web-design-prototype-icon-statuses`) explicitly froze its layout/tile set |
| `lib/widgets/dense_table.dart`, `lib/widgets/adm_icon.dart` | **No change** | Verified: `IconStack` already `Wrap`s any icon count; `Cell` already has 7 stackable slots — sufficient for every new cell below |

## Data Models

### `Sim` additions (`lib/data/models.dart`)

```dart
// --- pro (col 3) ---
final String pro;        // raw legacy `.pro` value, e.g. 'A' — shown bare, no label invented
final bool proWarn;      // true when sim/state/<imsi>.pro != sim/settings/<imsi>.pro → T.brandDeep

// --- spec cluster (col 6) ---
final int vip;           // 0 (none) / 11 / 12 / >0 generic — legacy's exact 3-way branch
final bool pre, pos;     // per-SIM flags; render via already-shipped special.pre/special.pos terms
final bool fas;          // per-SIM flag; call.special... no, uses new Ico.fas() + plain boolean icon

// --- state / live call (col 7) ---
// io/qos already exist. New:
final String liveState;  // '' | 'dialing' | 'ring' | 'active' | 'cooldown'
final int elapsedSec;    // seconds, meaningful only when liveState is dialing/ring/active
final int cooldownMax;   // diff_min ceiling, meaningful only when liveState == 'cooldown'
final String emType;     // raw, default '0' — shown as-is, no interpretation (matches legacy)
final String numberb;    // busy-state B number; may carry legacy's raw '#SOU<15-digit-imsi>' suffix
final String numbera;    // busy-state A number; ignored/overridden when numberb carries the SOU suffix

// --- MAY/MON/MSM + SMS quota (col 25) ---
// may, mon already exist (String 'sent/limit'). New:
final String msm;        // 'sent/limit', e.g. '1/2'
final int smsSent, smsSoft, smsHard; // rendered "SMS:sent/[soft;hard]", exactly like legacy

// --- PDDAS (col 27, between existing asrl and pdd0) ---
final double pddas;      // mock value only — no claim which real-world formula it represents

// --- LIMIT0..LIMIT5 (cols 31-36) ---
// Replaces lim0/lim1 (String) with a 6-element parallel pair, mirroring the existing
// `dates: List<String>` precedent already in this class (same rationale: homogeneous repeats).
final List<String> limits;      // length 6, each "value/max" — LIMIT0..LIMIT5 in order
final List<bool> limitPalevo;   // length 6, parallel index — over-limit flag per slot

// --- dongle hub-port sub-line (col 14) ---
final String dongleA;    // hub port label (dongle0* rows only); '' elsewhere
```

Removed: `lim0`, `lim1` (superseded by `limits`/`limitPalevo`) — every current call site is
`sims_page.dart`'s single `lim0` `ColDef`, updated below; no other file references these two fields
(verified by grep before writing this spec).

`Sim.field()` (used only for column sorting, itself already partial/incomplete today — many
existing columns aren't sortable): no new entries required for these additions; `pddas` and `vip`
are reasonable future sort keys but adding them isn't blocking anything and isn't requested.

`Sim.haystack` (search box): unchanged — none of these new fields are the kind of identifying text
operators search by (numbers/plans/models/IMEI/IMSI already covered).

### No new types

`Cell`, `ColDef`, `IcoRef`, `LogLink` are unchanged. Every new cell fits the existing stacking
contract (`note → icons → text → mono → warn → sub → sub2`, plus `icons` already being a `List`
that `IconStack` wraps).

### `terminology.dart` additions

```dart
'call.live.dial': _term('call.live.dial', 'Dialing', 'Набор номера'),
'call.live.active': _term('call.live.active', 'Call active', 'Разговор активен'),
'qos.spam': _term('qos.spam', 'Suspicious', 'Подозрительно', confidence: TermConfidence.derived),
'qos.imo': _term('qos.imo', 'IM-related request class', 'IM-связанный класс запроса',
    confidence: TermConfidence.unresolved),
'qos.sys': _term('qos.sys', 'System class (not billed)', 'Системный класс (не биллится)'),
```

Wording for all five is copied verbatim from the icon-statuses flow's own **already-approved**
`03-specifications.md` manifest (`incomingRecency`/`outgoingSourceClass` tables) — not new
invention, just finally implementing rows that document already specified.

### `icon_map.dart` changes

```dart
// Ico.group(): add two branches (holiday variants; workday variants already exist)
if (pause == 2)  return const [IcoRef('pause2.png','пауза'), IcoRef('day_holiday.png','выходной')];
if (pause == 12) return const [IcoRef('wake.png','просыпается'), IcoRef('day_holiday.png','выходной')];
if (pause == 22) return const [IcoRef('sleep.png','спит'), IcoRef('day_holiday.png','выходной')];
// (existing pause==1/11/21 branches unchanged)

// _qosMap: add three entries
'SPAM': ['spam.png', 'qos.spam'],
'IMO':  ['imode.png', 'qos.imo'],   // legacy select.c numeric 6 → imode.png (html.php:340)
'SYS':  ['qos/inos.png', 'qos.sys'], // legacy has no distinct SYS icon — numeric 0 always
                                      // renders inos.png regardless of NOS/SYS (html.php:334);
                                      // reusing that exact asset is the confirmed behavior,
                                      // not a placeholder.

// New small helpers, same style as existing Ico methods:
static IcoRef? fas(bool v) => v ? const IcoRef('fas.png', 'fas') : null;

static IcoRef? vip(int v) => switch (v) {
  11 => const IcoRef('ivip1.png', 'vip=11'),
  12 => const IcoRef('ivip2.png', 'vip=12'),
  > 0 => const IcoRef('ivip.png', 'vip>0'),
  _ => null,
};
// Deliberately labeled by raw value only — no tier-meaning copy invented (descoped, see
// 02-visual.md Open Q2). Note: `assets/imgs/ivip.png` (this, per-SIM capability) is a
// confirmed-different file from `assets/imgs/qos/ivip.png` (qos.vip, call classification) —
// verified both exist on disk; do not conflate them.

static IcoRef pre(bool v) => _termRef('spec/pre.png', 'special.pre', v ? 'PRE' : '');
static IcoRef pos(bool v) => _termRef('spec/pos.png', 'special.pos', v ? 'POS' : '');
// Only rendered when v is true (caller filters), matching legacy's unconditional-icon-when-1
// behavior. Reuses the already-shipped special.pre/special.pos terms — not the current
// _specMap's unverified "предоплата"/"постоплата" guess-labels (descoped, Open Q3).

static IcoRef liveCall(String state) => switch (state) {
  'dialing' => _termRef('state/state_dial.png', 'call.live.dial', 'DIAL'),
  'ring'    => _termRef('state/state_ring.png', 'call.live.ring', 'RING'),
  'active'  => _termRef('state/state_active.png', 'call.live.active', 'ACTIVE'),
  'cooldown'=> _termRef('state_wait.png', 'call.live.wait', 'WAIT'),
  _ => throw ArgumentError('unknown liveState: $state'),
};
```

All asset paths above were verified to exist on disk before writing this spec (`find assets
-iname ...`), including the non-obvious ones: `ivip1.png`/`ivip2.png` (not `.ico` — already
vendored as `.png` in this port), `state_wait.png` at top level (not under `state/`), `imode.png`,
`spam.png`.

### `spec` column icon-stack ordering (matches legacy's exact render order, `sim.php:1385-1441`)

```dart
Cell(icons: [
  if (Ico.vip(s.vip) != null) Ico.vip(s.vip)!,
  if (s.pre) Ico.pre(true),
  if (s.pos) Ico.pos(true),
  if (Ico.fas(s.fas) != null) Ico.fas(s.fas)!,
  if (Ico.spec(s.spec) != null) Ico.spec(s.spec)!,
])
```

### `io`/`qos`/live-state column — one cell, composed from existing + new pieces

```dart
Cell(
  icons: [
    if (s.liveState.isNotEmpty) Ico.liveCall(s.liveState),
    if (Ico.io(s.io) != null) Ico.io(s.io)!,
    if (Ico.qos(s.qos, s.io) != null) Ico.qos(s.qos, s.io)!,
  ],
  mono: s.io == 'O' && s.emType != '0' ? s.emType : '',
  text: switch (s.liveState) {
    'dialing' || 'ring' || 'active' => '(${s.elapsedSec} сек.)',
    'cooldown' => '(${s.elapsedSec}/${s.cooldownMax} сек.)',
    _ => '',
  },
  sub: _busyNumberB(s),
  sub2: _busyNumberA(s),
)
```

Busy-number SOU split (`sim.php:1543-1548`'s exact `substr(-19,4)=="#SOU"` check, ported literally):

```dart
// In sims_page.dart, next to _log(): small pure helpers, not a new shared abstraction.
String _busyNumberB(Sim s) {
  if (s.numberb.length >= 19 &&
      s.numberb.substring(s.numberb.length - 19, s.numberb.length - 15) == '#SOU') {
    return s.numberb.substring(0, s.numberb.length - 15);
  }
  return s.numberb;
}

String _busyNumberA(Sim s) {
  if (s.numberb.length >= 19 &&
      s.numberb.substring(s.numberb.length - 19, s.numberb.length - 15) == '#SOU') {
    return s.numberb.substring(s.numberb.length - 15); // the OTHER managed SIM's IMSI
  }
  return s.numbera;
}
```

Tooltip/label for the SOU case must read **"Внутренний звонок между SIM"** (already the exact
wording of the shipped `call.sou` term) — never "self-call" (icon-statuses Owner clarification 1.3,
already corrected in this session).

### `pro` column (new)

```dart
ColDef(
  key: 'pro', w: 40, label: 'pro',
  build: (s) => s.proWarn
      ? Cell(warn: s.pro)          // T.cellAlarm is red, not blue — see note below
      : Cell(text: s.pro),
),
```

**Note:** `Cell.warn` renders in `T.cellAlarm` (red, used elsewhere for over-limit/blacklist alarm
states) — but the requirements doc's approved decision was `T.brandDeep` (blue) for this specific
"differs from setting" cue, matching legacy's own blue-text convention and avoiding a false "this
is an alarm" read. `Cell` has no blue-styled slot today. Two options, both minimal:

- (a) reuse `mono` styled with a one-off color override — `Cell` doesn't support per-cell color
  overrides today, so this means either a `Cell.tint` field (smallest addition) or an inline
  `Text(s.pro, style: T.cell.copyWith(color: T.brandDeep))` built directly in the `ColDef.build`
  callback (bypassing the shared `_cell()` stacking helper) since this is the **only** cell in the
  whole table needing this exact treatment.
- (b) add one generic `Cell({..., this.tint})` field consumed by `dense_table.dart`'s `_cell()` as
  an optional color override applied to whichever line is present.

Recommend (a): it's one column, one line, no shared-widget change — smaller than adding a new
`Cell` field for a single caller. Flagged here rather than silently decided since it's the one spot
this spec touches `dense_table.dart`'s rendering contract at all (by not using `_cell()` for this
one `ColDef`, not by modifying it).

### MAY/MON/MSM+SMS column

```dart
ColDef(
  key: 'may', w: 96, label: 'MAY', sub: 'MON/MSM/SMS',
  build: (s) => Cell(text:
    'MAY ${s.may}\nMON ${s.mon}\nMSM ${s.msm}\n'
    'SMS ${s.smsSent}/[${s.smsSoft};${s.smsHard}]'),
),
```

`Cell.text` renders via a plain `Text(...)`, which already handles embedded `\n` — confirmed by
reading `dense_table.dart`'s `_cell()`; no multi-field change needed for this 4-line cell. Widened
`w` from 72→96 to fit the longest line (`SMS 4/[0;10]`).

### PDDAS column (new, between `asrl` and `pdd0`)

```dart
ColDef(key: 'pddas', w: 46, label: 'PDDAS',
    build: (s) => Cell(text: s.pddas.toStringAsFixed(2))),
```

### LIMIT0..LIMIT5 (replaces the single `lim0` column)

```dart
for (var i = 0; i < 6; i++)
  ColDef(
    key: 'lim$i', w: 80, label: 'LIMIT$i',
    build: (s) => Cell(
      icons: s.limitPalevo[i]
          ? [const IcoRef('qos/ipalevo.png', 'PAL')] // existing captcha.pal term, unchanged wording
          : const [],
      text: s.limits[i],
    ),
  ),
```

(Generated in a loop rather than 6 near-identical literal `ColDef`s — the six columns are truly
homogeneous, unlike the rest of the table's bespoke cells, so a loop here doesn't fight the
codebase's existing "explicit over abstracted" style, it matches it: each column really is
"the same shape, index N.")

### `dongle` column — add hub-port sub-line

```dart
ColDef(key: 'dongle', w: 68, label: 'dev',
    build: (s) => Cell(mono: s.dongle, sub2: s.dongleA)),
```

## Behavior Specifications

### Happy Path

1. `_cols()` builds the same 33 existing columns plus: `pro` (new), `pddas` (new), `lim2`-`lim5`
   (new), for a new total of **38 columns** (33 existing − 1 (`lim1` merged into the loop) + 1
   (`pro`) + 1 (`pddas`) + 6 (`lim0`-`lim5` loop) = 33 − 2 + 1 + 1 + 6 = 39 — recount precisely in
   Plan phase against the final `_cols()` list, this is an estimate for sizing purposes only).
2. `mock.dart`'s existing 5 `Sim(...)` rows gain the new fields with plausible values; the sample
   set still renders without null-field crashes (all new fields are `required` or have safe
   defaults per the Data Models section — finalize `required` vs. default in the actual Dart edit).
3. Columns-editor (`ColumnsEditor`/`TableToolbar`) picks up the 6 new/changed columns automatically
   — it already iterates `_cols()` generically, no columns-editor code change needed.

### Edge Cases

| Case | Trigger | Expected Behavior |
|---|---|---|
| `liveState == ''` and `numberb.isEmpty` | Idle SIM, no live call | State cell shows only `io`+`qos` icons (today's existing behavior), no extra lines |
| `s.numberb` shorter than 19 chars but still has a literal `#SOU` inside it | Malformed/non-conforming mock data | `_busyNumberB`/`_busyNumberA` fall through to the plain (non-SOU) branch — matches legacy's own `substr` bounds check, no crash |
| `s.vip == 0` | No VIP capability | No icon added to the spec-cluster list (`Ico.vip` returns `null`) |
| `s.pre == false && s.pos == false && s.fas == false && s.vip == 0 && s.spec.isEmpty` | Fully inactive spec cluster | Empty icon list → `IconStack` returns `SizedBox.shrink()` (already how the empty-icons case is handled today) |
| `limitPalevo[i] == false` for all 6 | No over-limit slots | No `ipalevo.png` icons at all, matches legacy's default-off state |
| `s.pddas` in mock data | N/A (mock-only field) | Any plausible double; no formula correctness is claimed or testable |

### Error Handling

Not applicable — static mock prototype, no runtime inputs beyond the existing `mock.dart`
literals and user-driven column show/hide/sort (already-existing, unchanged code paths).

## Dependencies

### Requires

- Nothing beyond what's already in the repo — every asset path was verified to exist before
  writing this spec (see `icon_map.dart` changes section).

### Blocks

- Nothing outside this flow.

## Integration Points

### Internal Systems

- `lib/widgets/columns_editor.dart` — consumes `_cols()` generically; verify at implementation time
  that the widened `may` column's new `sub: 'MON/MSM/SMS'` label reads sensibly in the columns
  picker (per `columnDisplayLabel()`'s existing fallback chain in `sims_page.dart`).

## Testing Strategy

### Unit Tests

- [ ] `_busyNumberB`/`_busyNumberA` split correctly for: no-SOU number, SOU-tagged number
      (19+ chars, `#SOU` at the right offset), and a too-short string containing `#SOU` elsewhere
      (must not false-positive).
- [ ] `Ico.group()` returns the new holiday-pause icon pairs for `pause` 2/12/22 and the existing
      pairs are unchanged for 1/11/21.
- [ ] `Ico.vip()` returns the three distinct assets for 11/12/generic>0 and `null` for 0.
- [ ] `Ico.qos()` resolves `SPAM`/`IMO`/`SYS` to the specified assets/terms.
- [ ] Every new `termId` referenced resolves via `termById()` (mirrors the icon-statuses flow's own
      test convention).

### Manual Verification

- [ ] Load `SimsPage` in-browser; confirm no overflow/crash with the widened table (new horizontal
      scroll extent is expected and fine — this table already scrolls horizontally).
- [ ] Hover the `pro` column on a mismatch row: confirm blue text, not red/alarm-styled.
- [ ] Hover a `LIMITn` palevo flag: confirm it shows the existing (unresolved) `captcha.pal`
      tooltip text verbatim, not a new invented name.
- [ ] Confirm the SOU busy-state mock row's tooltip reads "Внутренний звонок между SIM", never
      any self-call wording.
- [ ] `flutter analyze` clean; existing test suite still passes.

## Migration / Rollout

N/A — static prototype, no persisted data, no migration.

## Open Design Questions

- [ ] Exactly one: the `pro` column's blue-text rendering approach — inline `Text` with a color
      override in this one `ColDef.build`, vs. adding a generic `Cell.tint` field. Recommendation
      given above (inline, smaller footprint); confirm before implementation.

---

## Approval

- [ ] Reviewed by:
- [ ] Approved on:
- [ ] Notes:
