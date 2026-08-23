# Plan: flutter_gsmsip-interface

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-08-20
> Specifications: [02-specifications.md](02-specifications.md) — APPROVED 2026-08-20

## Pre-Plan Correction (verified against live repo, not the stale flow note)

Requirements AC #8 assumed `sdd-complete-refactoring`'s claim of "1000+
compile errors" (dated 2026-03-15) as a prerequisite risk. Ran
`dart analyze` against the current tree before planning:

- **1084 of 1086 total errors are inside `legacy/`** — which is a
  **separate Dart package** (`legacy/pubspec.yaml` → `name:
  flutter_gsm_sip_gateway`, a prior-generation codebase kept for
  reference), not part of `flutter_gsmsip` (`name: flutter_gsmsip`) at
  all. It only surfaces in `dart analyze` because `analysis_options.yaml`
  doesn't exclude it.
- The **real package has 2 errors**, both in `test/flutter_gsmsip_test.dart`
  (a stale `flutter create` template test referencing a non-existent
  `FlutterGsmsip()` class/function — the actual library has no such
  top-level class).

So "get to compiling baseline" is a ~15-minute hygiene fix, not a
multi-day prerequisite. Task 1 below does it; everything after assumes a
clean `dart analyze` on the real package.

## Task Breakdown

### Task 1 — Analysis hygiene (prerequisite)
- Add `analyzer: exclude: [legacy/**, example/build/**, build/**]` to
  `analysis_options.yaml`.
- Fix `test/flutter_gsmsip_test.dart`: replace the stale
  `FlutterGsmsip()` reference with a real smoke test (e.g. instantiate
  `MethodChannelFlutterGsmsip` and verify `FlutterGsmsipPlatform.instance`
  defaults to it — mirrors the existing
  `flutter_gsmsip_method_channel_test.dart` pattern).
- **Verify**: `dart analyze` exits clean (0 errors) on the real package.
- Complexity: trivial. Dependencies: none.

### Task 2 — New domain models
- New files in `lib/src/domain/models/`: `modem_state.dart` (enum),
  `network_mode.dart` (enum), `restart_mode.dart` (enum),
  `at_command_result.dart` (class, per 02-specifications.md shape).
- Style: match existing `voice_line_method.dart` pattern (enum +
  extension for `displayName`/`toJson`/`fromJson` where applicable).
- Complexity: small. Dependencies: Task 1.

### Task 3 — New domain entities
- New files in `lib/src/domain/entities/`: `modem_device.dart`,
  `modem_call.dart` (reuses `CallDirection`/`CallState` from
  `sip_call.dart` — import, don't duplicate), `carrier_profile.dart`,
  `modem_group_config.dart`.
- New file `lib/src/domain/models/modem_event.dart`: sealed class
  hierarchy (`ModemAttached`, `ModemDetached`, `ModemStateChanged`,
  `ModemSignalChanged`, `ModemRegistrationChanged`,
  `ModemCallStateChanged`, `ModemSmsReceived`, `ModemUssdReceived`,
  `ModemErrorOccurred`) per 02-specifications.md.
- Style: `Equatable`, `copyWith`, `toJson`/`fromJson`, matching
  `sip_call.dart`/`voice_line_config.dart` conventions.
- Complexity: medium (event hierarchy is the fiddliest part — use Dart 3
  `sealed class` + pattern-matchable subclasses, not an enum+payload
  union). Dependencies: Task 2.

### Task 4 — `ModemRepository` interface + typed failure
- New file `lib/src/domain/repositories/modem_repository.dart`: abstract
  class mirroring the `FlutterGsmsipPlatform` methods from
  02-specifications.md, minus `getPlatformVersion`.
- New failure type `ModemDriverNotAvailable` in
  `lib/src/domain/exceptions/` (or extend existing `failures.dart` if it
  already has a suitable base) — wraps "platform threw
  `UnimplementedError`" distinctly from "empty device list" and from
  other command failures.
- Complexity: small. Dependencies: Task 3.

### Task 5 — Extend `FlutterGsmsipPlatform`
- Edit `lib/flutter_gsmsip_platform_interface.dart`: add the full
  abstract API from 02-specifications.md (`listModems`, `getModem`,
  `modemEvents` stream getter, `sendAtCommand`, `setDiagMode`,
  `setPower`, `restartModem`, `changeImei`, `setNetworkMode`, `setGroup`,
  `dial`, `hangupCall`, `answerCall`, `sendSms`, `sendUssd`).
- **This is the one intentionally breaking change** in the flow: any
  future platform implementation must implement the full surface. Today
  only `MethodChannelFlutterGsmsip` implements it, so no other call sites
  break.
- Complexity: small (mechanical). Dependencies: Task 4.

### Task 6 — Android `MethodChannelFlutterGsmsip`: plumb through, don't fake support
- Edit `lib/flutter_gsmsip_method_channel.dart`: implement the new
  abstract members. **Clarification vs. specifications' phrasing**: since
  ttyUSB/AT-command modems are a Linux desktop concept (not something
  Android phones expose), the Android implementation does **not** get new
  Kotlin/native code in this flow — `listModems()` returns `[]`,
  `modemEvents` is an empty broadcast stream, and command methods
  (`sendAtCommand`, `dial`, etc.) throw `UnsupportedError('Modem/AT
  commands are not available on Android — use the Dongle/SIP path')`.
  This keeps existing Android behavior (audio-dongle + SIP) completely
  unchanged while satisfying the interface contract.
- Complexity: small. Dependencies: Task 5.

### Task 7 — `linux:` platform registration (stub)
- Add to `pubspec.yaml` under `flutter.plugin.platforms`:
  ```yaml
  linux:
    dartPluginClass: LinuxFlutterGsmsip
  ```
  Using Flutter's **pure-Dart plugin registration** (`dartPluginClass`,
  no native C++/CMake scaffold) — appropriate since this flow adds no
  native code, and `sdd-flutter_gsmsip-channel` will likely use
  `dart:ffi` directly from Dart rather than a native GTK plugin wrapper.
- New file `lib/src/linux/linux_flutter_gsmsip.dart`:
  `class LinuxFlutterGsmsip extends FlutterGsmsipPlatform` — every modem
  method throws `UnimplementedError('Implemented by
  sdd-flutter_gsmsip-channel')`; `getPlatformVersion()` returns a real
  value (e.g. reads `/etc/os-release`) since that's trivial and useful
  for diagnostics immediately.
- Complexity: small. Dependencies: Task 5.

### Task 8 — `ModemRepositoryImpl`
- New file `lib/src/data/repositories/modem_repository_impl.dart`:
  implements `ModemRepository`, delegates every call to
  `FlutterGsmsipPlatform.instance`, catches `UnimplementedError` and
  rethrows as `ModemDriverNotAvailable`.
- Complexity: small. Dependencies: Task 6, Task 7.

### Task 9 — `TelephonyService` refactor
- Edit `lib/src/services/telephony_service.dart`: remove direct
  `MethodChannel('gsm_sip_gateway/telephony')` usage; inject/use
  `ModemRepository` instead. Preserve existing public method signatures
  used by `GatewayService` where practical to limit blast radius.
- Complexity: medium (need to trace all current call sites first).
  Dependencies: Task 8.

### Task 10 — `GatewayService` routing update
- Edit `lib/src/services/gateway_service.dart`: `CallRouting`
  orchestration's GSM leg sources from `ModemRepository`/`ModemCall`
  instead of the old direct-channel `TelephonyService` calls. Ordered
  init becomes Modem→SIP→SMPP (was Telephony→SIP→SMPP) — same order,
  renamed step.
- Complexity: medium. Dependencies: Task 9.

### Task 11 — Cleanup (Should Have)
- Remove orphaned `lib/src/data/services/*` duplicate service files
  (confirmed unused during interface-flow research).
- Deprecate/remove the now-unused `gsm_sip_gateway/telephony` channel
  constant if nothing else references it after Task 9.
- Complexity: trivial. Dependencies: Task 10.

### Task 12 — Barrel exports
- Edit `lib/flutter_gsmsip.dart`: export the new entities, models,
  `ModemRepository`, `ModemRepositoryImpl` following the existing
  export grouping style.
- Complexity: trivial. Dependencies: Task 8.

### Task 13 — Tests
- `test/`: entity `toJson`/`fromJson`/`copyWith` round-trip tests for
  `ModemDevice`, `ModemCall`, `CarrierProfile`, `ModemGroupConfig`
  (pattern after existing model tests if any exist, else plain
  `flutter_test`).
- `ModemRepositoryImpl` test: verify `UnimplementedError` from a fake
  `FlutterGsmsipPlatform` surfaces as `ModemDriverNotAvailable`.
- Platform-interface test: verify default instance is
  `MethodChannelFlutterGsmsip` (extends existing
  `flutter_gsmsip_platform_interface_test.dart` if present, else new
  file) and that `LinuxFlutterGsmsip` satisfies the `PlatformInterface`
  token check.
- One test at a time, per project testing protocol.
- Complexity: medium. Dependencies: Tasks 3, 8, 12.

### Task 14 — README update
- `README.md`: add a short "Platform Support" section noting Android
  (full) and Linux (interface registered, driver pending
  `sdd-flutter_gsmsip-channel`) status, plus Windows/macOS as planned.
- Complexity: trivial. Dependencies: Task 13.

## Explicitly Deferred (not in this plan)

- Persisting `ModemGroupConfig`/`CarrierProfile` via
  `local_storage_datasource.dart` or elsewhere — no storage requirement in
  requirements' Must-Haves; revisit when `sdd-flutter_gsmsip-channel` or
  `vdd-simbox-app-uiux` implementation actually needs persistence.
- Any native Linux code (CMake/FFI) — intentionally not started; Task 7's
  `dartPluginClass` approach means `sdd-flutter_gsmsip-channel` can add
  `dart:ffi` bindings without touching plugin registration at all.

## Testing Strategy

- `dart analyze` clean (Task 1 baseline) stays clean after every
  subsequent task — run it as a checkpoint after Tasks 5, 8, 10, 12.
- Unit tests only for this flow (no integration/device tests needed —
  there's no real driver yet). Android's existing behavior must not
  regress: run existing `flutter_gsmsip_method_channel_test.dart` after
  Task 6.
- Manual check: `flutter pub get` succeeds and `flutter build linux`
  (or at minimum `flutter analyze` targeting linux) doesn't fail due to
  the new `dartPluginClass` registration, in an environment with Linux
  desktop support enabled.

## Rollback Considerations

- All changes are additive except Task 5 (extending the abstract
  `FlutterGsmsipPlatform`) and Task 9/10 (refactoring existing services).
  Task 5 is safe because `MethodChannelFlutterGsmsip` is the only
  implementer. Tasks 9/10 touch live Android call paths — land and verify
  those two tasks with extra care (re-run Android example app) before
  proceeding to Task 11's cleanup/deletions.
- No persisted data/schema changes in this plan, so no migration/rollback
  concern there.
- If Task 9/10 regress Android behavior, they can be reverted
  independently of Tasks 1–8 (new files) since those don't depend on the
  service refactor.

## Sequencing vs. Other Flows

- This plan must fully land (through Task 14) before
  `vdd-simbox-app-uiux` begins its IMPLEMENTATION phase, per that flow's
  Constraints.
- `sdd-flutter_gsmsip-channel` (not yet created) starts after both this
  plan and `vdd-simbox-app-uiux`'s implementation are merged.

---

## Approval

- [ ] Reviewed by: Anton Dodonov
- [ ] Approved on:
- [ ] Notes:
