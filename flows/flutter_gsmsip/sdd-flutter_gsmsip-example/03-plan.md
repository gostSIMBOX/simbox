# Implementation Plan: flutter_gsmsip-example

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-08-24
> Specifications: [02-specifications.md](02-specifications.md)

## Summary

Sequenced per Anton: rewrite `example/README.md` first (it becomes the
contract the rest of the work must satisfy), then build the app to match
it — `ExampleConfigStore` + `PlatformCapabilities` foundation, then the 6
screens, then the `linux`/`macos` platform scaffolds, then verification
builds on all 3 platforms.

**New finding while planning** (`git log --diff-filter=D -- example/lib/
screens`, commit `e8f586d "example working"`): the example used to have a
full `screens/` folder, but it was a wholesale copy of the much bigger
`simbox-app`'s screens (`base_stations_screen.dart`, `sims_screen.dart`,
`codecs_screen.dart`, `ussd_screen.dart`, `language_screen.dart`,
`theme_demo_screen.dart`, etc. — matches `flows/_archive/vdd-screens/*`
exactly) — none of which correspond to concepts `GatewayService` actually
has (no base-station/SIM-inventory/codec/USSD/language API on this
plugin). That whole folder was correctly deleted. `example/lib/theme/*`
and `example/lib/l10n/*` were left behind, unreferenced by the surviving
`main.dart` — but they're **not** unrelated cruft: `app_widgets.dart` has
purpose-built `signalIndicator`/`connectionIndicator`/
`callStatusIndicator`/`statusCard` widgets, and `l10n/app_en.arb` has
`sipUsername`/`sipPassword`/`sipServer`/`sipPort`/`connect` keys —
clearly meant for exactly the Setup/Dashboard screens this plan builds.
**Decision: reuse `theme/` and `l10n/` (add missing keys, drop keys for
deleted simbox-app-only screens), don't delete them.** `utils/
easter_eggs.dart` and `utils/funny_messages.dart` have no plausible
connection to any spec'd screen — delete. `utils/imei_validator.dart`:
no screen in scope collects an IMEI (not a `SipAccount`/`SmppConfig`
field) — delete unless Task 3 finds a use.

## Task Breakdown

### Phase 1: README + Foundation

#### Task 1.1: Rewrite `example/README.md`
- **Description**: Replace the `GsmSipBridge`/fictional-`screens/`
  content with: real `GatewayService`-based quick-start (matching
  `02-specifications.md`'s Data Flow), the 6 real screens, the
  per-platform capability table, the SMPP-is-simulated disclosure, the
  `ExampleConfigStore` key-coupling risk note, actual permissions
  (already accurate — Android manifest already lists them), and a
  getting-started sequence that Task 4.4 will have actually run.
- **Files**: `example/README.md` — Modify
- **Dependencies**: None
- **Verification**: Manual read-through against `02-specifications.md`
  for accuracy; every claim traceable to a real method/class.
- **Complexity**: Low

#### Task 1.2: `ExampleConfigStore`
- **Description**: New class wrapping `SharedPreferences`, key
  `'gateway_config'`, using `GatewayConfig.toJson()`/`.fromJson()`.
  Methods: `Future<GatewayConfig?> load()`, `Future<void> save
  (GatewayConfig)`, `Future<void> clear()`.
- **Files**: `example/lib/data/example_config_store.dart` — Create
- **Dependencies**: None
- **Verification**: Unit test (Task 4.1) — save→load round-trip; clear
  removes key; a value saved by `ExampleConfigStore` is readable by
  `GatewayService().loadConfiguration()` and vice versa (cross-check,
  since both must agree on shape).
- **Complexity**: Low

#### Task 1.3: `PlatformCapabilities`
- **Description**: Static class per spec — `sipSupported`,
  `modemDriverSupported`, both `dart:io Platform.isX`-derived. Doc
  comment pointing back at `02-specifications.md`'s capability table as
  source of truth, with an explicit "keep in sync by hand" warning.
- **Files**: `example/lib/platform_capabilities.dart` — Create
- **Dependencies**: None
- **Verification**: Unit test (Task 4.1) if trivial via a `Platform`
  override seam; otherwise a manual truth-table comment is sufficient
  (decide when writing it — don't over-engineer a seam for 2 booleans).
- **Complexity**: Low

### Phase 2: Screens

#### Task 2.1: App shell + navigation
- **Description**: `main.dart` becomes `MaterialApp` + `Scaffold` +
  `NavigationBar` (6 destinations) + `IndexedStack`. Startup logic:
  `ExampleConfigStore.load()` → null routes to Setup tab initially, else
  Dashboard. Wire `AppTheme.lightTheme`/`darkTheme` (from the reused
  `theme/app_theme.dart`) instead of the current ad-hoc `ColorScheme.
  fromSeed`.
- **Files**: `example/lib/main.dart` — Modify (rewritten)
- **Dependencies**: Task 1.2, 1.3
- **Verification**: App launches, correct initial tab per config
  presence, all 6 tabs reachable without crashing (even with stub
  bodies before Tasks 2.2–2.6 land).
- **Complexity**: Medium

#### Task 2.2: Setup screen
- **Description**: Per spec §"1. Setup" — form → `GatewayConfig` →
  `.validationErrors` inline → `ExampleConfigStore.save()` → navigate to
  Dashboard tab.
- **Files**: `example/lib/screens/setup_screen.dart` — Create
- **Dependencies**: Task 1.2, 2.1
- **Verification**: Save with invalid data shows validation errors and
  does not persist; valid save round-trips through `ExampleConfigStore.
  load()`.
- **Complexity**: Medium

#### Task 2.3: Dashboard screen
- **Description**: Per spec §"2. Dashboard" — capability banner, modem
  device-info card (own `ModemRepositoryImpl()` from `flutter_gsm`),
  `GatewayStatus` card wired to `statusStream`, Start/Stop that **checks
  `initialize()`'s bool result** and surfaces the real `logStream` tail
  on failure (the concrete bug fixed vs. today's code), test-call/SMS
  quick actions with a real number field.
- **Files**: `example/lib/screens/dashboard_screen.dart` — Create
- **Dependencies**: Task 1.3, 2.1
- **Verification**: On this dev machine (Linux): Start Gateway shows the
  specific SIP-unsupported failure reason, not a generic message or
  silent no-op (AC #5). Modem card shows a real result or a graceful
  "not available" message, not a crash/infinite spinner.
- **Complexity**: High (the honest-failure-surfacing logic is the crux
  of this whole flow — see Requirements' Problem Statement)

#### Task 2.4: Settings screen
- **Description**: Per spec §"3. Settings" — same fields as Setup,
  pre-filled, plus Clear (stops gateway if running, then
  `ExampleConfigStore.clear()`).
- **Files**: `example/lib/screens/settings_screen.dart` — Create
- **Dependencies**: Task 1.2, 2.1
- **Verification**: Clear while gateway running stops it first (no
  dangling `_isRunning` state observable via `statusStream`), then wipes
  config; Setup tab shown again next launch.
- **Complexity**: Medium

#### Task 2.5: Call screen
- **Description**: Per spec §"4. Call" — `routingStream`/
  `getActiveRoutings()` list, make-via-SIP/make-via-GSM, end/end-all.
  Explicitly no answer/hold/mute controls (not in `GatewayService`'s
  surface) — the screen should say so in an empty-state or info tooltip
  rather than silently omitting with no explanation.
- **Files**: `example/lib/screens/call_screen.dart` — Create
- **Dependencies**: Task 2.1
- **Verification**: Routing list updates live as `routingStream` emits;
  End/End All actually call `endRouting`/`endAllRoutings`.
- **Complexity**: Medium

#### Task 2.6: SMS screen
- **Description**: Per spec §"5. SMS" — `SmsService()` directly for
  history/stream, send via `GatewayService().sendSms(...)`. SMPP toggle
  disabled when `config.smppConfig == null`. Visible, non-buried label
  that SMPP is simulated (reuses the lib's own doc-comment honesty, per
  spec).
- **Files**: `example/lib/screens/sms_screen.dart` — Create
- **Dependencies**: Task 1.2, 2.1
- **Verification**: Sent message appears with status transitioning
  pending→sent→delivered (or failed, ~5% of the time per the lib's own
  simulated roll) without the screen needing to poll — `messageStream`
  driven.
- **Complexity**: Medium

#### Task 2.7: Logs screen
- **Description**: Per spec §"6. Logs" — merge `GatewayService().
  logStream` + `SmsService().logStream` into a bounded (500-entry)
  in-memory list, text-search filter, clear (local only). No level
  filter (not real, per spec).
- **Files**: `example/lib/screens/logs_screen.dart` — Create
- **Dependencies**: Task 2.1
- **Verification**: Entries from both streams appear, interleaved by
  arrival order; clearing empties the visible list without affecting the
  underlying streams.
- **Complexity**: Low

#### Task 2.8: Prune/reuse `theme/`, `utils/`, `l10n/`
- **Description**: Delete `utils/easter_eggs.dart`, `utils/
  funny_messages.dart`, `utils/imei_validator.dart` (no spec'd screen
  uses them — confirm again at this point since screens are now written,
  not just planned). Wire `theme/app_theme.dart`'s `ThemeData` into
  `MaterialApp` (Task 2.1). Reuse `theme/app_widgets.dart`'s
  `signalIndicator`/`connectionIndicator`/`callStatusIndicator`/
  `statusCard` in Dashboard/Call screens instead of writing new ones.
  Prune `l10n/*.arb` keys that only make sense for deleted simbox-app
  screens (base stations, SIMs, codecs, USSD, language, theme-demo);
  keep and extend the SIP/gateway-relevant keys across all existing
  locales, or reduce to `en`+`ru` only if maintaining 36 locales for 6
  small screens is disproportionate (**decide with Anton before
  deleting 34 locale files** — flag as a checkpoint, not a unilateral
  call).
- **Files**: `example/lib/utils/*.dart` (3 files) — Delete;
  `example/lib/theme/*` — Modify (wire in, no structural rewrite needed);
  `example/lib/l10n/*.arb` (+generated `.dart`) — Modify
- **Dependencies**: Tasks 2.2–2.7 (need to know final string/widget
  usage before pruning)
- **Verification**: `flutter analyze` still clean after deletions (no
  dangling imports).
- **Complexity**: Low, except the locale-count decision (needs a
  checkpoint with Anton, see below)

### Phase 3: Platform Scaffolds

#### Task 3.1: Add `linux`/`macos` platform folders
- **Description**: `flutter create --platforms=linux,macos .` inside
  `example/` (mechanical, doesn't touch `lib/`). Add explicit
  `flutter_gsm: {path: ../../flutter_gsm}` dependency to `example/
  pubspec.yaml` (currently only transitive) per spec's Dependencies
  section.
- **Files**: `example/linux/**` — Create; `example/macos/**` — Create;
  `example/pubspec.yaml` — Modify
- **Dependencies**: None (can run in parallel with Phase 2)
- **Verification**: `flutter pub get` succeeds after the dependency
  addition.
- **Complexity**: Low

#### Task 3.2: Trim unused `pubspec.yaml` dependencies
- **Description**: Re-check after Phase 2 lands which of `workmanager`,
  `connectivity_plus`, `flutter_local_notifications`, `device_info_plus`,
  `crypto`, `flutter_svg`, `google_fonts` are actually referenced by the
  final screens; drop what isn't. (`device_info_plus` likely earns its
  keep via the Dashboard's device-info card; the rest are unverified
  against current `main.dart` — grep confirmed zero references as of
  2026-08-24, before this plan's screens existed.)
- **Files**: `example/pubspec.yaml` — Modify
- **Dependencies**: Tasks 2.1–2.7
- **Verification**: `flutter analyze` clean; `flutter pub get` clean.
- **Complexity**: Low

### Phase 4: Verification

#### Task 4.1: Unit tests
- **Description**: `ExampleConfigStore` save/load/clear round-trip test
  (per spec's Testing Strategy). `PlatformCapabilities` test only if a
  clean override seam is easy; otherwise skip with a one-line note in
  the test file explaining why (don't force an abstraction for 2
  booleans).
- **Files**: `example/test/example_config_store_test.dart` — Create
- **Dependencies**: Task 1.2
- **Verification**: `flutter test` passes.
- **Complexity**: Low

#### Task 4.2: `flutter analyze` clean
- **Description**: Zero errors across the whole example after all
  changes (lint/info-level acceptable, per AC #1).
- **Files**: N/A (verification only)
- **Dependencies**: All prior tasks
- **Verification**: Command output.
- **Complexity**: Low

#### Task 4.3: `flutter build linux` / `flutter build macos`
- **Description**: Both must succeed on this dev machine (AC #8).
- **Files**: N/A
- **Dependencies**: Task 3.1
- **Verification**: Command output; if either fails for a reason outside
  this flow's control (e.g. missing native toolchain), document exactly
  what's missing rather than silently marking the AC done.
- **Complexity**: Medium (unknowns until attempted — first real build of
  linux/macos platform folders for this example)

#### Task 4.4: Android build check
- **Description**: `flutter analyze`+ (if an Android SDK/toolchain is
  present in this environment) a debug assemble. If no Android toolchain
  is available here, explicitly document as unverified in the
  implementation log and README (matches the precedent already set in
  `sdd-flutter_gsmsip-interface`'s status notes for its own unverified
  Linux build) — not silently skipped.
- **Files**: N/A
- **Dependencies**: All Phase 2/3 tasks
- **Verification**: Command output, or explicit "unverified, needs an
  Android-capable environment" note.
- **Complexity**: Low

#### Task 4.5: Manual walkthroughs (Linux, this machine)
- **Description**: Execute the manual verification checklist from
  `02-specifications.md`'s Testing Strategy: fresh-install → Setup →
  Dashboard → Start (expect honest SIP-unsupported failure) → modem
  listing → Settings clear → SMS send (simulated delivery) → Logs
  populate from both streams.
- **Files**: N/A
- **Dependencies**: Task 4.3
- **Verification**: Each spec'd edge case in §"Edge Cases" reproduced
  and confirmed to behave as documented.
- **Complexity**: Medium

## Dependency Graph

```
1.1 (README) ─── informs all of Phase 2 (no code dependency, sequencing only)

1.2 ─┬─→ 2.2 ─┐
1.3 ─┤        │
     └─→ 2.1 ─┼─→ 2.3 ─┐
              ├─→ 2.4  │
              ├─→ 2.5  ├─→ 2.8 ─┬─→ 4.1
              ├─→ 2.6 ─┘        ├─→ 4.2 ─→ 4.3 ─┬─→ 4.4
              └─→ 2.7           │               └─→ 4.5
                                └─→ 3.2
3.1 (parallel to Phase 2) ──────────────────────→ 3.2, 4.3
```

## File Change Summary

| File | Action | Reason |
|------|--------|--------|
| `example/README.md` | Modify | Replace fictional API/screens docs with real ones |
| `example/lib/main.dart` | Modify | App shell + navigation, was a single dashboard |
| `example/lib/data/example_config_store.dart` | Create | Config persistence independent of `initialize()` success |
| `example/lib/platform_capabilities.dart` | Create | Honest per-platform capability surfacing |
| `example/lib/screens/{setup,dashboard,settings,call,sms,logs}_screen.dart` | Create | The 6 spec'd screens |
| `example/lib/utils/easter_eggs.dart`, `funny_messages.dart`, `imei_validator.dart` | Delete | Unused, no spec'd screen needs them |
| `example/lib/theme/*` | Modify | Wired into `MaterialApp`, reused widgets |
| `example/lib/l10n/*` | Modify | Prune deleted-screen keys, keep/extend SIP-relevant ones |
| `example/linux/**`, `example/macos/**` | Create | New platform scaffolds |
| `example/pubspec.yaml` | Modify | Explicit `flutter_gsm` dep; trim unused deps |
| `example/test/example_config_store_test.dart` | Create | Round-trip coverage |
| `libsFlutter/flutter_gsmsip/lib/**`, `flutter_gsm/**`, `flutter_nmsip/**` | **None** | Out of scope, confirmed again here |

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| `'gateway_config'` key drifts from a future lib version | Low | Medium | Documented in README + code comment; not silently assumed stable |
| `flutter build macos`/`linux` fails on missing native toolchain pieces in this environment | Medium | Low | Task 4.3 documents exactly what's missing rather than claiming success |
| 36-locale `l10n` maintenance burden disproportionate to 6 small screens | Medium | Low | Explicit checkpoint with Anton before any locale deletion (Task 2.8) |
| Android build unverifiable in this environment (no device/SDK) | Medium | Low | Documented as unverified per Task 4.4, same precedent as prior flows |

## Rollback Strategy

All changes are confined to `libsFlutter/flutter_gsmsip/example/**`
(a nested git repo per `git status` — has its own `.git`). If
implementation needs to be abandoned: `git -C libsFlutter/flutter_gsmsip
checkout -- example/` restores the pre-flow state; nothing outside that
directory is touched.

## Checkpoints

After each phase, verify:

- [ ] Phase 1: README reads as an accurate description of a not-yet-built
  app (internally consistent with `02-specifications.md`); config
  store/capabilities have passing unit tests.
- [ ] Phase 2: **Checkpoint with Anton on the l10n locale-count decision
  (Task 2.8)** before deleting any `.arb` files.
- [ ] Phase 3: `flutter pub get` clean on all 3 platforms.
- [ ] Phase 4: All ACs from `01-requirements.md` re-checked one by one
  against actual runs, not assumed.

## Open Implementation Questions

- [ ] Task 2.8's locale-count call — resolve with Anton mid-implementation,
  not guessed.
- [ ] Whether `NavigationRail` is worth it for wide/desktop windows
  (deferred from Specifications) — decide when Task 2.1 is actually
  being written, informed by how the Linux/macOS windows look with a
  bottom `NavigationBar` at typical desktop sizes.

---

## Approval

- [ ] Reviewed by: Anton
- [ ] Approved on:
- [ ] Notes:
