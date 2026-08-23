# Requirements: sdd-flutter_gsm-ffi

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-08-21

## Problem Statement

`flutter_gsm`'s Linux platform implementation (`LinuxFlutterGsm`,
`lib/src/linux/linux_flutter_gsm.dart`) is a complete stub today: every
`ModemRepository` method (`listModems`, `dial`, `hangupCall`,
`answerCall`, `sendSms`, `sendUssd`, `sendAtCommand`, `changeImei`,
`setDiagMode`, `setPower`, `restartModem`, `setNetworkMode`, `setGroup`)
throws `UnimplementedError('...: implemented by sdd-asterisk-chan-simbox')`.

`sdd-asterisk-chan-simbox` (`libsCpp/asterisk_chan_simbox`) has now
shipped a real, tested native C SDK — `simbox_api.h`/`simbox_types.h`,
built as `libsimbox.a`/`libsimbox.dylib`/`libsimbox.so` — covering modem
discovery, calls, SMS/USSD, raw AT commands, IMEI change, a DIAG
programmator, and an APDU SIM reader, all over ttyUSB AT-command modems,
Asterisk-free. This is the real driver `LinuxFlutterGsm` was always
meant to defer to.

This flow binds the two: wire `LinuxFlutterGsm` to `libsimbox` via
`dart:ffi`, so `flutter_gsm`'s `ModemRepository` actually works against
real hardware on Linux, instead of throwing.

**Load-bearing finding from source, not assumption**: `libsimbox`'s
discovery subsystem (`simbox_discovery_start/scan/stop`, USB/hub
enumeration → `simbox_discovered_device_t`) and its device registry
(`simbox_device_count`/`simbox_device_get_by_index`, what calls/SMS/AT
commands actually operate on) are currently **not connected** —
`simbox_init()` never populates `inst->devices[]`, `auto_discovery`/
`auto_recover_diag` in `simbox_config_t` are accepted but unused, and the
only thing that ever adds a device to the registry
(`simbox_device_create()`) isn't in the public header — it's called only
by `tests/test_simbox.c` to fabricate a fake device for testing calls/SMS
in isolation from real discovery. **Confirmed in scope for this flow**
(Anton, 2026-08-21): closing this gap on the native side
(`libsCpp/asterisk_chan_simbox/src/simbox_api.c`/`simbox_discovery.c` —
these are new adapter files this session's `sdd-asterisk-chan-simbox`
flow wrote, not the vendored/read-only `asterisk_chan_svistok/`, so
editing them is in-bounds) is part of this flow, not deferred to a
separate one.

## User Stories

### Primary

**As a** developer using `flutter_gsm` on Linux desktop (directly, or via
`simbox-app`)
**I want** `ModemRepository`'s discovery/call/SMS/USSD/AT-command methods
to operate against real ttyUSB modems
**So that** `simbox-app` (and any other `flutter_gsm` consumer) is
functional on Linux, not just Android — closing the gap this whole
package split was building toward.

### Secondary

**As a** developer debugging modem behavior
**I want** `sendAtCommand`/`setDiagMode`/`changeImei` to reach the real
modem over FFI
**So that** diagnostics work the same way on desktop as the historical
chan_svistok tooling did.

## Acceptance Criteria

### Must Have

1. **Given** a Linux host with `libsimbox` built and discoverable
   **When** `ModemRepository.listModems()` is called
   **Then** it returns real `ModemDevice`s reflecting actually-attached
   ttyUSB modems (not an empty list due to the discovery/registry gap
   above, and not `UnimplementedError`).

2. **Given** a real modem returned by `listModems()`
   **When** `dial`/`answerCall`/`hangupCall`/`sendSms`/`sendUssd`/
   `sendAtCommand`/`changeImei` are called with its `modemId`
   **Then** each reaches the corresponding `simbox_*` C function via FFI
   and returns/throws based on the real result (`simbox_call_originate`,
   `simbox_call_answer`, `simbox_call_hangup`, `simbox_sms_send`,
   `simbox_ussd_send`, `simbox_at_command`, `simbox_change_imei`).

3. **Given** a modem attaches, detaches, changes call state, or receives
   an SMS/USSD response while the app is running
   **When** `libsimbox` fires its C event callback (`simbox_event_cb`)
   **Then** `ModemRepository.modemEvents` emits the matching `ModemEvent`
   sealed subtype (`ModemAttached`/`ModemDetached`/
   `ModemCallStateChanged`/`ModemSmsReceived`/`ModemUssdReceived`/
   `ModemErrorOccurred`/etc.) — bridged safely across the FFI callback
   boundary (native callbacks can fire from a non-Dart thread; must not
   crash or drop events).

4. **Given** the current native gap where discovery and the device
   registry aren't connected
   **When** this flow's native-side fix lands
   **Then** `libsimbox`'s existing `tests/test_simbox.c` integration
   suite still passes, plus a new test demonstrates a discovered device
   (from `simbox_discovery_scan`) becoming a queryable
   `simbox_device_t` (via `simbox_device_count`/`get_by_index`) without
   the test-only `simbox_device_create()` shortcut.

5. **Given** `flutter_gsm`'s existing `ModemRepositoryImpl` (which wraps
   `UnimplementedError` into `ModemDriverNotAvailableException`)
   **When** `libsimbox` genuinely isn't available (library not found,
   `dart:ffi` load failure)
   **Then** the same typed-exception behavior is preserved — FFI load
   failure must not crash the app or leak a raw `dart:ffi` exception to
   callers.

### Should Have

- `setPower`/`restartModem`/`setNetworkMode`/`setGroup`: `simbox_api.h`
  has no dedicated functions for these. Likely implementable via
  `simbox_at_command()` with known AT strings (e.g. `AT+CFUN` for power),
  same as chan_svistok did — needs verification against chan_svistok's
  own AT command usage during specifications, not assumed.
- A documented answer to "where does `libsimbox.so`/`.dylib` actually
  ship from at runtime" (system-installed vs. built-and-bundled by the
  plugin's own build step vs. bundled prebuilt binary) — see Open
  Questions; whichever is chosen should be reflected in
  `flutter_gsm`'s `linux/CMakeLists.txt` (currently a `dartPluginClass`
  pure-Dart registration with **no native CMake scaffold at all** — one
  may need to be added).

### Won't Have (This Iteration)

- Windows/macOS FFI binding — `libsimbox` targets Linux/macOS build
  (Makefile has `Darwin`/else branches) but this flow's *Dart-side* FFI
  work is scoped to `LinuxFlutterGsm` only; `MacosFlutterGsm`/
  `WindowsFlutterGsm` stay stubbed until a follow-up flow, even though
  the native library may already build on macOS.
- Exposing `libsimbox`'s DIAG programmator (`simbox_prog_*`) or APDU SIM
  reader (`simbox_reader_*`) — `ModemRepository`'s interface has no
  matching methods (firmware flashing, raw APDU) and adding them is a
  separate interface-design decision, not implied by this flow.
- Android — already real, via `flutter_tele`/`flutter_dialer`/
  `flutter_smsussd` (Tasks 1-7 of `sdd-flutter_gsm`), unrelated to FFI.
- Touching `asterisk_chan_svistok/` (vendored chan_svistok source) or
  `adapters/` (the Asterisk-API compatibility shim) — both remain
  strictly read-only per the Strangler Fig pattern established in
  `sdd-asterisk-chan-simbox`. Only `src/simbox_*.c`/`.h` (the new,
  already-adapter-layer files) are in scope for the discovery/registry
  fix.

## Constraints

- **Technical**: `dart:ffi` (no third-party FFI codegen package assumed
  yet — `ffigen` could reduce hand-written bindings from
  `simbox_api.h`/`simbox_types.h`; worth deciding in specifications).
- **Threading**: native events must be bridged to Dart via a
  thread-safe mechanism (`NativeCallable.listener` or an isolate
  `SendPort`) — `simbox_set_event_callback`'s callback can fire from any
  thread `libsimbox` spawns internally (the codebase uses `pthread`
  throughout).
- **Platform**: Linux only for this iteration (see Won't Have).
- **Dependencies**: `sdd-asterisk-chan-simbox` (native library +
  discovery/registry fix, both in scope here) must be functionally
  correct before the Dart FFI layer can be verified end-to-end against
  real hardware — but unit-level FFI plumbing (marshalling, callback
  bridging) can be developed/tested against `libsimbox`'s existing
  `test_simbox` fixtures independent of real hardware.
- **Read-only forever**: `asterisk_chan_svistok/`, `adapters/` (per
  established Strangler Fig convention this whole native track follows).

## Open Questions

- [ ] How is `libsimbox`'s shared library actually shipped/discovered at
  runtime by a Flutter Linux app? (system package, bundled build step via
  a new `linux/CMakeLists.txt`, or a bundled prebuilt binary as a plugin
  asset) — this is the single most consequential decision for this flow
  and should be resolved in specifications.
- [ ] `modemId: String` (the `ModemRepository` interface's key) should
  map to `libsimbox`'s device serial number (`simbox_device_sn`), not the
  raw `simbox_device_t` opaque pointer — confirm this in specifications;
  raw pointers are unstable/unsafe to expose as a Dart-facing identifier.
- [ ] Exact AT command strings for `setPower`/`restartModem`/
  `setNetworkMode`/`setGroup` — verify against chan_svistok's own AT
  command tables (`asterisk_chan_svistok/chan_svistok/at_command.c` or
  similar) rather than guessing standard 3GPP AT syntax.
- [ ] Does `simbox_discovery_scan()` need to run continuously in a
  background thread (to catch hot-plug events) or is a one-shot scan
  triggered by `listModems()` sufficient for v1? Affects whether
  `ModemAttached`/`ModemDetached` events are ever emitted, or only
  synchronous `listModems()` snapshots change.

## References

- `libsCpp/asterisk_chan_simbox/src/simbox_api.h` — public C API.
- `libsCpp/asterisk_chan_simbox/src/simbox_types.h` — public C types.
- `libsCpp/asterisk_chan_simbox/tests/test_simbox.c` — existing
  integration test, the only current example of real API usage.
- `libsCpp/asterisk_chan_simbox/flows/sdd-asterisk-chan-simbox/` — the
  native-side flow this depends on (marked COMPLETE by Anton's own
  tooling 2026-08-21; this flow's own findings above amend that with a
  real, confirmed gap).
- `libsFlutter/flutter_gsm/flows/sdd-flutter_gsm/` — prior flow that
  created `ModemRepository`/`LinuxFlutterGsm` as stubs pointing here.

---

## Approval

- [ ] Reviewed by: Anton
- [ ] Approved on:
- [ ] Notes:
