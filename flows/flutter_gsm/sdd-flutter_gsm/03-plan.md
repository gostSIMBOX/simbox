# Plan: flutter_gsm

> Version: 1.0
> Status: APPROVED
> Last Updated: 2026-08-21
> Specifications: [02-specifications.md](02-specifications.md) — APPROVED 2026-08-21

## Sequencing Overview

Three packages touched, in dependency order: `flutter_gsm` (rename +
Android backing) must reach a compiling state before `flutter_gsmsip`
(thin orchestrator) is refactored against it, which must compile before
`simbox-app`'s imports are fixed. Tasks below are grouped by package in
that order; within `flutter_gsm`, the rename (Tasks 1-3) must land before
the new Android work (Tasks 4-6) so there's no churn on soon-to-be-renamed
files.

**Session-wide constraint carried from requirements**: no `git add`/
`commit`/`push` in this plan's execution — Anton is committing everywhere
himself this session.

## `flutter_gsm` Tasks

### Task 1 — Rename bundle identity (mechanical)
- Execute the full rename checklist from specifications §1: `pubspec.yaml`,
  `lib/flutter_gsmsip*.dart` → `flutter_gsm*.dart` (+ class renames
  `FlutterGsmsipPlatform`→`FlutterGsmPlatform`,
  `MethodChannelFlutterGsmsip`→`MethodChannelFlutterGsm`,
  `LinuxFlutterGsmsip`→`LinuxFlutterGsm`), `test/*` renames + import
  fixes, `android/build.gradle`+`settings.gradle`+`AndroidManifest.xml`,
  `android/src/main/kotlin/org/telon/flutter_gsmsip/` →
  `org/telon/flutter_gsm/` (7 files, class `FlutterGsmsipPlugin` →
  `FlutterGsmPlugin`; **keep** `GatewayDialerModule`/`HeadlessModule`/
  `HeadlessService`/`HeadlessEventService`, just move+rename package —
  per specifications' recommendation), `android/src/test/kotlin/...`,
  `example/pubspec.yaml`+`pubspec.lock`+`README.md`+`lib/main.dart`,
  `example/android/app/build.gradle.kts`.
- **Verify**: `dart analyze` on the renamed package — 0 errors expected
  (mechanical rename shouldn't introduce logic errors, but broken import
  paths are easy to miss).
- Complexity: medium (large mechanical surface, low risk per-change, but
  many files — go file-by-file, don't batch-sed blindly given Kotlin
  package-directory moves are involved).
- Dependencies: none.

### Task 2 — Cleanup: delete `legacy/` and `gsm_sip_bridge.dart`
- Delete `flutter_gsm/legacy/` (confirmed in specifications: no bearing
  on GSM-abstraction scope, already excluded from `dart analyze`).
- Delete `lib/src/services/gsm_sip_bridge.dart` — bridging-logic naming,
  belongs conceptually to `flutter_gsmsip`. First verify nothing in
  `flutter_gsm`'s own `lib/` imports it (should be nothing, given its
  name, but confirm with a grep before deleting, not after).
- **Verify**: `dart analyze` stays clean after deletion.
- Complexity: trivial. Dependencies: Task 1 (do cleanup after rename to
  avoid renaming a file about to be deleted).

### Task 3 — Add `flutter_dialer`/`flutter_tele`/`flutter_smsussd` dependencies
- `pubspec.yaml`: add path dependencies to the three sibling packages
  (`../flutter_dialer`, `../flutter_tele`, `../flutter_smsussd` — confirm
  exact relative paths against `libsFlutter/`'s actual layout).
- **Verify**: `flutter pub get` succeeds.
- Complexity: trivial. Dependencies: Task 1 (pubspec already touched
  there; do this as a follow-up edit, not a separate pubspec pass).

### Task 4 — Investigate `flutter_tele`'s native Kotlin (verification, not implementation)
- Read `flutter_tele/android/.../TeleService.java`(or `.kt`)/
  `TeleModule` native source (per prior research, this extends
  `InCallService`) to answer specifications' two open verification
  points: (a) can SIM slots be enumerated before `TeleEndpoint.start()`
  is called, or only after; (b) exact event-type strings emitted via the
  `flutter_tele_events` EventChannel (`call_changed`/`call_received`/
  `call_terminated` were named in JS-era docs — confirm the Kotlin
  source uses the same strings, don't assume the RN-era names carried
  over unchanged).
- Output: a short findings note appended to this plan (not a separate
  doc) — feeds directly into Task 5's implementation.
- Complexity: small (reading, not writing). Dependencies: none (can run
  parallel to Tasks 1-3).

### Task 5 — `AndroidFlutterGsm`: real `ModemRepository` backing
- New file `lib/src/android/android_flutter_gsm.dart`:
  `AndroidFlutterGsm extends FlutterGsmPlatform`. Wraps a `TeleEndpoint`
  instance + `FlutterDialer` static calls per specifications §2.2-2.3:
  - `listModems()`/`getModem()`: map SIM slots (source confirmed by
    Task 4) to `ModemDevice`.
  - `modemEvents`: adapt `TeleEndpoint.on(...)` streams (event-type
    strings confirmed by Task 4) into `ModemEvent` subtypes; defensive
    `Map` parsing per specifications' edge-case note (no blind casts).
  - `dial`/`hangupCall`/`answerCall`: wrap `TeleEndpoint.makeCall`/
    `hangupCall`/`answerCall`, tracking a `modemId`↔`TeleCall` mapping
    internally (repository methods take `modemId`/`callId` strings, not
    `TeleCall` objects).
  - `sendSms`: wrap `flutter_smsussd`'s send API (confirm its exact
    method signature when writing this — not yet verified in
    specifications, do it here).
  - `sendUssd`, `sendAtCommand`, `setPower`, `restartModem`, `changeImei`,
    `setNetworkMode`, `setDiagMode`: throw `UnsupportedError` with a
    message naming the unsupported capability (mirrors the existing
    `MethodChannelFlutterGsm`'s pattern from `sdd-flutter_gsmsip-
    interface`) — these are correctly unsupported per specifications,
    not oversights.
  - Before any call/dial operation: check `FlutterDialer.isDefaultDialer()`
    and surface a typed error (new `ModemNotDefaultDialerException` in
    `modem_exceptions.dart`) if false, rather than letting the underlying
    platform call fail opaquely.
- **Decide registration mechanism**: does Android already use
  `pluginClass`+Kotlin (`FlutterGsmPlugin.kt`, unchanged from before), or
  does adding `AndroidFlutterGsm` mean the Kotlin plugin's
  `getPlatformVersion` handler now also needs to set
  `FlutterGsmPlatform.instance = AndroidFlutterGsm()` at registration
  time? Likely the latter — investigate `FlutterGsmPlugin.kt`'s
  `onAttachedToEngine` during implementation, adjust registration if
  needed.
- Complexity: large (the real functional core of this flow's Android
  story). Dependencies: Tasks 1-4.

### Task 6 — Windows/macOS stub scaffolds
- `pubspec.yaml`: add `windows:`/`macos:` entries under
  `flutter.plugin.platforms`, `dartPluginClass` pattern mirroring Linux
  (`WindowsFlutterGsm`/`MacosFlutterGsm`, `fileName:` pointing at new
  `lib/src/windows/windows_flutter_gsm.dart` /
  `lib/src/macos/macos_flutter_gsm.dart`).
- Both classes: every modem method throws `UnimplementedError('...:
  implemented by sdd-asterisk-chan-simbox + a future windows/macos
  channel flow')`; `getPlatformVersion()` gets a real trivial
  per-platform implementation (Windows: registry or `ver` equivalent;
  macOS: `sw_vers`-equivalent read) — small, free, useful for
  diagnostics, matches Linux's precedent.
- Complexity: small (near-copy of the existing `LinuxFlutterGsm`
  pattern). Dependencies: Task 1.

### Task 7 — Tests
- Update renamed test files (Task 1) to pass under new names/imports.
- New: `test/android_flutter_gsm_test.dart` — fake/mock
  `FlutterDialer`/`TeleEndpoint` interactions (or a thin seam allowing
  injection, since both are currently static/concrete classes in their
  respective packages — may need a small wrapper interface in
  `AndroidFlutterGsm` itself to make this testable; decide during
  implementation, don't let untestability block the task).
- New: `test/windows_flutter_gsm_test.dart`,
  `test/macos_flutter_gsm_test.dart` — mirror
  `linux_flutter_gsm_test.dart`'s pattern (registration + stub-throws +
  stream-safety checks).
- One test at a time, per project testing protocol.
- Complexity: medium. Dependencies: Tasks 5, 6.

## `flutter_gsmsip` Tasks

### Task 8 — Add `flutter_gsm`/`flutter_nmsip` dependencies
- `pubspec.yaml`: add path dependencies.
- **Verify**: `flutter pub get` succeeds.
- Complexity: trivial. Dependencies: Task 1 (needs `flutter_gsm` renamed
  and stable first, per specifications' sequencing constraint).

### Task 9 — `SipStateTracker`
- New `lib/src/services/sip_state_tracker.dart`: subscribes to
  `FlutterSip2.eventStream` (from `flutter_nmsip`), demuxes by the
  event's `type` key (enumerate actual type strings by reading
  `flutter_nmsip`'s native source during implementation — not yet
  catalogued), maintains local `accounts`/`activeCalls` registries and
  `isConnected`/`isInitialized` derived state — the state-query surface
  `flutter_nmsip` itself doesn't provide (per specifications §3.1's gap
  table).
- Complexity: large (this is real new logic, not a thin wrapper — treat
  it with the care its name implies). Dependencies: Task 8.

### Task 10 — Replace embedded SIP implementation
- Delete `lib/src/services/sip_service.dart` and its duplicate under
  `lib/src/data/services/sip_service.dart` (confirmed real dependency of
  `SipRepositoryImpl` last flow — this time the replacement is ready,
  not a premature deletion).
- Rewrite `SipRepositoryImpl` to call `FlutterSip2` (from `flutter_nmsip`)
  directly for commands, and `SipStateTracker` (Task 9) for state
  queries.
- Document `attendedTransfer`/`unregisterAccount` as known gaps at the
  call sites that need them: either implement a workaround now (if one's
  findable — e.g. `unregisterAccount` via re-`registerAccount`ing with a
  0-second expiry, if `flutter_nmsip`'s account config exposes that) or
  leave a clearly-marked `UnimplementedError` + code comment linking back
  to this plan, decided during implementation rather than deferred
  again.
- **Verify**: `dart analyze` clean; existing `SipRepository` interface
  consumers (if any outside this file) still compile.
- Complexity: large. Dependencies: Task 9.

### Task 11 — `GatewayService`/`CallRouting` reshape
- Update `lib/src/services/gateway_service.dart`: GSM leg sources from
  `flutter_gsm.ModemRepository` (via `ModemRepositoryImpl`) instead of
  the old in-package `TelephonyService`; SIP leg sources from the
  Task 10 `SipRepositoryImpl`. Ordered init becomes
  Modem→SIP→SMPP (SMPP/`smpp_service.dart` unchanged — confirmed not
  redundant with anything in specifications' research).
- Remove `telephony_service.dart` and its `gsm_sip_gateway/telephony`
  channel — confirmed in prior research to be a later Dart-only
  invention, not battle-tested legacy logic, now fully superseded by
  `flutter_gsm.ModemRepository`.
- **Verify**: `dart analyze` clean.
- Complexity: medium. Dependencies: Task 10, and `flutter_gsm`'s Task 5
  (needs real Android modem behavior to route to, not just the interface
  — though compiling against the interface alone is possible earlier;
  full behavior verification waits on Task 5).

### Task 12 — Barrel exports + cleanup
- Update `lib/flutter_gsmsip.dart` exports: remove deleted files, ensure
  `SipStateTracker` (if it's meant to be public) is exported.
- Remove the duplicate `lib/src/data/services/gateway_service.dart` if
  (and only if) a fresh check (same grep-the-real-relative-import
  method from last flow's near-miss) confirms it's genuinely unused —
  don't repeat last time's near-deletion without re-verifying.
- Complexity: small. Dependencies: Task 11.

### Task 13 — Tests
- Unit tests for `SipStateTracker` (event demuxing, state derivation)
  — the highest-value new test surface, since this is genuinely new
  logic.
- Update/adapt existing `GatewayService`/`SipRepositoryImpl`-adjacent
  tests if any exist for the new dependency wiring.
- One test at a time.
- Complexity: medium. Dependencies: Tasks 9-12.

## `simbox-app` Tasks

### Task 14 — Import path fixes
- `pubspec.yaml`: add `flutter_gsm` path dependency.
- Audit actual `simbox-app` usage: does it need `flutter_gsmsip` at all
  (bridging types), or only `flutter_gsm` (Modem-layer types)? Per
  specifications, `vdd-simbox-app-uiux`'s implementation log suggests
  only `ModemRepository`/`ModemDevice`/etc. (Modem-layer) — verify by
  grepping `simbox-app/lib/` for `package:flutter_gsmsip/` imports before
  deciding whether to drop the dependency entirely or keep it.
- Update all `import 'package:flutter_gsmsip/...'` → `package:flutter_gsm/
  ...'` for Modem-layer types; keep/adjust `flutter_gsmsip` imports only
  where actually needed.
- **Verify**: `flutter analyze` clean; existing `simbox-app` tests
  (Симки/Настройки/widget tests from `vdd-simbox-app-uiux`) still pass —
  this is a real regression risk, run the full suite, not a spot check.
- Complexity: medium (mechanical import changes, but the "does it still
  need flutter_gsmsip" question needs a real answer, not an assumption).
- Dependencies: Tasks 1-7 (flutter_gsm) at minimum; Tasks 8-13
  (flutter_gsmsip) only if `simbox-app` keeps that dependency.

## Testing Strategy

- `dart analyze`/`flutter analyze` clean as a checkpoint after every
  package's task group (7, 13, 14) — don't let errors accumulate across
  groups.
- `flutter test` full suite per package after its task group completes.
- `simbox-app`'s existing test suite (from `vdd-simbox-app-uiux`, 8
  tests as of that flow's last checkpoint) is the regression backstop
  for Task 14 — must stay green.

## Rollback Considerations

- `flutter_gsm`'s rename (Task 1) is high-surface but mechanical —
  revert by re-running the checklist in reverse if something breaks
  fatally; low semantic risk.
- `flutter_gsmsip`'s Task 10-11 (deleting embedded SIP/telephony code)
  is the highest-risk change in this plan — real working code is
  removed in favor of new integration code. Land Task 9 (`SipStateTracker`)
  and verify it independently before Task 10 deletes anything, so
  there's a tested replacement in place before the old code is removed,
  not after.
- `simbox-app`'s Task 14 must not land until `flutter_gsm` (and
  `flutter_gsmsip`, if kept) are independently verified compiling+
  tested — don't debug three packages' worth of breakage at once.

## Explicitly Deferred

- Real Windows/macOS/Linux native driver behavior — waits on
  `sdd-asterisk-chan-simbox`, tracked there.
- `attendedTransfer`/`unregisterAccount` gaps — resolved with a
  workaround-or-documented-limitation decision inside Task 10, not a
  separate future flow, unless Task 10 finds the workaround infeasible.

---

## Approval

- [x] Reviewed by: Anton Dodonov
- [x] Approved on: 2026-08-21
- [x] Notes: Approved as drafted.
