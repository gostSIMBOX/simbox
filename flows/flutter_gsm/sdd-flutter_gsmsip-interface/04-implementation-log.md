# Implementation Log: flutter_gsmsip-interface

> Plan: [03-plan.md](03-plan.md) — APPROVED 2026-08-20

## Summary

12 of 14 planned tasks completed as specified. Tasks 9 and 10 were
**dropped after inspecting the real code** — they were based on a mistaken
premise in specifications/plan (see Deviations below). This is a
substantive finding, not a minor tweak — read it before approving.

`dart analyze lib test` — **0 errors** (101 pre-existing info/warning-level
lints, none introduced by this work). `flutter test` — **17/17 passing**.

## Task-by-Task

- [x] **Task 1 — Analysis hygiene**: added `analyzer: exclude:
  [legacy/**, example/build/**, build/**]` to `analysis_options.yaml`;
  fixed `test/flutter_gsmsip_test.dart`'s stale `FlutterGsmsip()`
  reference. Verified: 0 errors.
- [x] **Task 2 — New domain models**: `modem_state.dart`,
  `network_mode.dart`, `restart_mode.dart`, `at_command_result.dart` in
  `lib/src/domain/models/`.
- [x] **Task 3 — New domain entities**: `modem_device.dart` (incl.
  `RegistrationState` enum), `modem_call.dart` (reuses
  `CallDirection`/`CallState` from `sip_call.dart`), `carrier_profile.dart`
  (incl. `CarrierProfileRegistry`), `modem_group_config.dart` (incl.
  `PacingAlgorithm` enum) in `lib/src/domain/entities/`; `modem_event.dart`
  sealed-class hierarchy (9 event types) in `lib/src/domain/models/`.
- [x] **Task 4 — `ModemRepository` + typed exceptions**: interface at
  `lib/src/domain/repositories/modem_repository.dart`. Deviated from
  specifications' `Failure`/dartz-`Either` sketch: inspected sibling
  repositories (`DongleRepository`, `VoiceLineRepository`) and found they
  use plain `Future<T>` + thrown `implements Exception` classes, not the
  `Failure` base class — followed that established convention instead.
  Added `lib/src/domain/exceptions/modem_exceptions.dart`
  (`ModemException`, `ModemDriverNotAvailableException`,
  `ModemNotFoundException`).
- [x] **Task 5 — Extend `FlutterGsmsipPlatform`**: added the full modem API
  to `lib/flutter_gsmsip_platform_interface.dart`. Gave every new member a
  default `throw UnimplementedError(...)` body (matching the existing
  `getPlatformVersion()` pattern) rather than a bare abstract signature —
  keeps the change non-breaking for any future `extends`-based
  implementation and simplified test stubs.
- [x] **Task 6 — Android `MethodChannelFlutterGsmsip`**: modem methods
  return empty/no-op or throw `UnsupportedError` pointing at the
  Dongle/SIP path, per plan's clarification. No native Kotlin changes.
- [x] **Task 7 — `linux:` platform registration**: added to
  `pubspec.yaml` via `dartPluginClass: LinuxFlutterGsmsip` +
  `fileName: src/linux/linux_flutter_gsmsip.dart`. New
  `lib/src/linux/linux_flutter_gsmsip.dart`: `getPlatformVersion()` reads
  `/etc/os-release` for a real value; every modem method throws
  `UnimplementedError('...: implemented by sdd-flutter_gsmsip-channel')`.
- [x] **Task 8 — `ModemRepositoryImpl`**: `lib/src/data/repositories/
  modem_repository_impl.dart`, catches `UnimplementedError` and rethrows
  `ModemDriverNotAvailableException`; `modemEvents` catches the same and
  falls back to `Stream.empty()` instead of throwing.
- [~] **Task 9 — `TelephonyService` refactor: DROPPED, see Deviations.**
- [~] **Task 10 — `GatewayService` routing update: DROPPED, see Deviations.**
- [x] **Task 11 — Cleanup: partially dropped, see Deviations.** No files
  deleted. `gsm_sip_gateway/telephony` channel constant left in place
  (still actively used by the real `TelephonyService`).
- [x] **Task 12 — Barrel exports**: `lib/flutter_gsmsip.dart` updated —
  new entities, models, exceptions, `ModemRepository`,
  `ModemRepositoryImpl` all exported, merged into existing section headers
  (there were already both an entities-exceptions and models section;
  avoided creating duplicate headers).
- [x] **Task 13 — Tests**: `test/modem_entities_test.dart` (10 tests:
  round-trips, `copyWith`, sealed-event exhaustive switch),
  `test/modem_repository_impl_test.dart` (2 tests: `UnimplementedError` →
  `ModemDriverNotAvailableException`, `modemEvents` safety),
  `test/linux_flutter_gsmsip_test.dart` (3 tests: registration, stub
  errors, stream safety). All existing tests still pass.
- [x] **Task 14 — README**: added a "Platform Support" section (Android
  full / Linux interface-registered / Windows-macOS planned) with a
  pointer to this flow.

## Deviations From Plan (read this)

### Tasks 9 & 10 dropped — specifications/plan conflated two different GSM mechanisms

Reading the actual `lib/src/services/telephony_service.dart` (642 lines,
real permission handling, real Android telephony state mapping, its own
working `MethodChannel('gsm_sip_gateway/telephony')`) revealed that
**`TelephonyService` is Android's own native SIM/phone-radio telephony
bridge** — a completely different physical mechanism from the new
ttyUSB/AT-command external-modem concept this flow is building. It's not
"ad-hoc code bypassing the platform interface that should route through
Modem" (what specifications assumed) — it's a legitimate, different,
already-working access method, most likely the backing implementation for
`VoiceLineMethod.telecomApi`.

Confirmed via `lib/src/services/gateway_service.dart` (the real,
exported orchestrator): it directly instantiates `TelephonyService()` and
listens to `callStateStream` as the GSM leg of its SIP↔GSM bridging — live,
wired-up, working code. Forcing this through `ModemRepository` would have
meant rewiring Android's own working phone-radio bridge onto an
architecturally unrelated external-USB-modem abstraction, which:
- serves no purpose (Android phones don't have ttyUSB modems),
- risks regressing real Android call-bridging behavior, and
- contradicts Task 6's own design, where Android modem methods explicitly
  say "use the Dongle/SIP path" — `TelephonyService` **is** that existing
  path and should stay untouched.

**Correction applied**: `TelephonyService` and `GatewayService` are left
completely unmodified. The Modem API added by this flow is purely additive
for Linux; it does not touch Android's existing SIP↔GSM bridge. If
simbox-app (Linux) eventually needs SIP↔Modem bridging analogous to
`GatewayService`'s Android SIP↔GSM bridging, that's new work for a future
flow — not a rename/rewire of the existing Android orchestrator.

### Task 11 — file-deletion part dropped after a near-miss

The interface-flow's own research (relayed into 01-requirements.md as a
"Should Have") claimed `lib/src/data/services/gateway_service.dart` and
`sip_service.dart` were orphaned duplicates. Deleted them, then
`dart analyze` immediately surfaced 2 new errors: the **exported, public**
`SipRepositoryImpl` (`lib/src/data/repositories/sip_repository_impl.dart`)
imports `../services/sip_service.dart` — a *relative* path that resolves
to the file just deleted, not to the differently-shaped `lib/src/services/
sip_service.dart`. The two `SipService` classes have incompatible APIs
(533 vs 290 lines, near-disjoint method sets) — this is real pre-existing
duplication/tech debt, not a safe cleanup target. **Restored both files
from git** (`git checkout --`) and verified 0 errors again. Left as-is;
flagging this duplication is arguably in `sdd-complete-refactoring`'s
scope, not this flow's.

**Lesson for future flows**: "unused" claims from research passes need
verification via relative-path-aware search (or just deleting +
re-analyzing, as done here), not literal substring grep — the miss here
was grepping for `data/services/sip_service` instead of resolving the
actual relative import path.

## Verification

```
$ dart analyze lib test
101 issues found. (0 errors — all info/warning, pre-existing)

$ flutter test
00:00 +17: All tests passed!
```

No manual `flutter build linux` run in this session (no Linux desktop
build target configured in this environment) — the `dartPluginClass`
registration mechanism is the Flutter-documented pure-Dart plugin pattern,
and `pub get` resolving cleanly plus `dart analyze` passing is the
available signal. Recommend a real `flutter build linux` smoke test in a
Linux desktop-capable environment before considering this flow fully done,
per the plan's Testing Strategy.

---

## Learnings for Specification Refinement

- Sibling repositories in this codebase use plain `Future<T>` + thrown
  exceptions, not the `Failure`/`Either` pattern despite `failures.dart`
  existing — worth a note in a future core-architecture ADR so new flows
  don't have to rediscover this each time.
- The codebase has at least two confirmed cases of same-named,
  differently-shaped classes in parallel directories (`SipService`,
  `GatewayService` in both `src/services/` and `src/data/services/`) —
  real tech debt, likely origin of `sdd-complete-refactoring`'s stalled
  state. Out of scope here; flagged for that flow.
