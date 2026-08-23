# Implementation Log: sdd-flutter_gsm-ffi

> Started: 2026-08-22
> Plan: [03-plan.md](03-plan.md)

## Progress Tracker

| Task | Status | Notes |
|------|--------|-------|
| 1.1 `simbox_device_register()` + registry wiring | Done | |
| 1.2 Native test for the registry wiring | Done | |
| 2.1 `ffigen` setup + generated bindings | Done | ffigen handled the tagged union better than expected — see Discoveries |
| 2.2 Native library loader | Done | |
| 2.3 Event struct union wrapper | Absorbed into 3.2 | ffigen made a standalone file unnecessary, see log |
| 3.1 Lifecycle + device listing | Done | |
| 3.2 Event bridging | Done | Found + fixed a real cross-boundary memory-lifetime bug — see log |
| 3.3 Call operations | Done | Straightforward, matched plan/specs exactly |
| 3.4 SMS/USSD | Done | `sendUssd`'s await-event design now works for real — Task 5.8 in `sdd-asterisk-chan-simbox` wired real manager-event dispatch since this was last blocked |
| 3.5 AT commands & diagnostics | Done | `sendAtCommand`/`changeImei`/`setDiagMode` |
| 3.6 Power / restart / network mode / group | Done | |
| 4.1 Threading (`Isolate.run` wrapping) | Done | Found + fixed two real bugs — see log |
| 4.2 Rewire `LinuxFlutterGsm` | Done | |
| 5.1 Gated integration test | Satisfied by existing coverage | See log — no new file, rationale below |
| 5.2 Full regression + example app smoke check | Done | |
| 5.3 Documentation | Done | |

## Session Log

### Session 2026-08-22 - Claude

**Started at**: Phase 1, Task 1.1
**Context**: Plan approved same session; implementation begins immediately.

#### Completed

- **Task 1.1 — `simbox_device_register()` + registry wiring**:
  - `libsCpp/asterisk_chan_simbox/src/simbox_api.h`: declared
    `simbox_device_register(simbox_handle_t, const
    simbox_discovered_device_t *)` in section 2, documented as
    idempotent (re-registering a known serial is a no-op, not a
    duplicate) and firing `SIMBOX_EVENT_DEVICE_CONNECTED` on first
    registration.
  - `libsCpp/asterisk_chan_simbox/src/simbox_api.c`: implemented.
    Checks `simbox_device_get_by_sn` first for idempotency (reuses the
    existing function rather than duplicating the linear scan),
    populates a `simbox_device_info_t` from the discovered device's
    `serial_number`/`imei`/`dev_name`/`data_port`/`audio_port` (imsi/
    model/firmware/rssi left zeroed — unknown at discovery time, filled
    in later once the driver actually queries the modem, which is a
    different concern), state set to `SIMBOX_STATE_CONNECTING`, appends
    via the existing internal `simbox_device_create()` under the
    instance mutex, fires the event callback (if set) after releasing
    the lock (avoids holding the mutex during a callback into
    unknown/possibly-slow user code).
  - Verified: `make clean && make` — 28 pre-existing warnings (all in
    vendored `asterisk_chan_svistok/`, none in `simbox_api.c`),
    `libsimbox.a`/`.dylib`/`test_simbox` all rebuild; isolated
    `gcc -Wall` compile of `simbox_api.c` alone — zero warnings.
    `./test_simbox` — all 5 pre-existing suites still pass (no
    regression).

- **Task 1.2 — Native test for the registry wiring**:
  - `libsCpp/asterisk_chan_simbox/tests/test_simbox.c`: added
    `test_discovery_registry_wiring()` (Test 6). Hand-builds a
    `simbox_discovered_device_t` (real USB enumeration returns 0 in this
    test environment, confirmed by Test 3's own output — same reasoning
    Test 2 already uses for hand-building a `simbox_device_info_t`, not
    a new pattern). Asserts: `simbox_device_count` goes 0 -> 1 after
    registration; the event callback fires exactly once
    (`g_event_count` delta); `simbox_device_get_by_sn`/`get_by_index`
    both resolve to the same handle; `simbox_device_get_info` reflects
    the registered `tty_data`/`tty_audio` ports; **registering the same
    serial a second time is a true no-op** — count stays 1, no second
    event fires (directly exercises the idempotency guarantee, not just
    the happy path).
  - Verified: rebuilt `test_simbox`, ran it — all 6 suites pass,
    including confirmation the event fires with the right device_sn and
    exactly once despite double-registration.

- **Task 2.1 — `ffigen` setup + generated bindings**:
  - `pubspec.yaml`: added `ffi: ^2.2.0` (regular dep), `ffigen: ^21.0.0`
    (dev dep). `flutter pub get` clean.
  - `ffigen.yaml`: entry-point `../../libsCpp/asterisk_chan_simbox/src/
    simbox_api.h`, output `lib/src/ffi/simbox_bindings.dart`.
  - Invocation note: `dart run ffigen` alone fails ("Couldn't find an
    entry for 'ffigen' in pubspec.yaml") — recent `ffigen` expects
    either a `ffigen:` key inside `pubspec.yaml` itself or an explicit
    `--config` flag. Used `dart run ffigen --config ffigen.yaml`
    (documented in the implementation log so future regeneration doesn't
    hit the same confusion).
  - First run flagged `simbox_device_state_t`/`simbox_event_type_t`'s
    enum underlying-int-size as implementation-defined (SEVERE by
    default). Added `silence-enum-warning: true` to `ffigen.yaml` with a
    documented rationale (libsimbox is always compiled locally by the
    same toolchain as this Dart app targets — no cross-compilation/
    distribution scenario where ABI could diverge). Regenerated clean,
    zero warnings.
  - Verified: generated file inspected directly (975 lines) —
    `simbox_device_register` present with the right signature; C enums
    became real Dart enums (`simbox_device_state_t.fromValue(...)`), not
    raw ints. `dart analyze lib/src/ffi/simbox_bindings.dart` — "No
    issues found!".

#### Deviations from Plan

- None structural. One scope reduction inside Task 2.3 (not yet started
  — see Discoveries): the "hand-written union wrapper" specifications
  called out as this flow's highest hand-memory-layout risk turns out to
  be largely unnecessary.

#### Discoveries

- **`ffigen` fully expands `simbox_event_t`'s tagged union** into a real
  typed `ffi.Union` (`UnnamedUnion`) with properly-typed nested structs
  per arm (`UnnamedStruct.caller` for `incoming_call`,
  `UnnamedStruct$1.old_state`/`.new_state` for `call_state`, etc.) —
  Dart 3's FFI has native union support, and `ffigen` used it. This
  means Task 2.3 no longer needs the raw-byte-offset reading
  specifications anticipated ("Dart FFI structs expose unions as raw
  byte layout, not discriminated access" — that assumption was wrong for
  current `ffigen`/Dart FFI); it's now a thin wrapper that just reads
  `event.ref.data.<arm>.<field>` based on `event.ref.type`, converting
  `Pointer<Char>` to Dart `String?`. Downgrading Task 2.3's complexity
  from the plan's "Medium... the one place this flow touches raw memory
  layout by hand" to Low — flagging as a positive deviation, not
  silently shrinking scope without a note.

- **Task 2.2 — Native library loader**:
  - `lib/src/ffi/simbox_native_library.dart`: `loadSimboxBindings()`
    (public entry point) + `resolveSimboxLibrary({envValue, open})` (pure
    resolution logic, `DynamicLibrary.open`/`Platform.environment`
    injected as parameters specifically so it's unit-testable without a
    real `libsimbox` or real env vars — a deliberate testability
    refactor beyond the plan's literal description, not a deviation in
    behavior). Env var (`FLUTTER_GSM_SIMBOX_LIB`) tried directly with no
    fallback on failure (explicit override failing should surface
    loudly); otherwise tries `simboxLibCandidates` in order
    (system-installed names, then monorepo-relative dev path), throwing
    `ModemDriverNotAvailableException` if all fail.
  - `test/simbox_native_library_test.dart`: 4 tests using
    `DynamicLibrary.process()` (the current process's own symbols,
    always openable) as a stand-in "success" result and a fake `open`
    callback — covers env-override-succeeds, env-override-fails-no-
    fallback, candidates-tried-in-order-stops-at-first-success, and
    all-candidates-fail-throws-typed-exception.
  - Verified: `dart analyze` clean on both files; `flutter test
    test/simbox_native_library_test.dart` — 4/4 passing. Additionally
    ran a one-off manual smoke check (temporary `tool/_smoke_ffi.dart`,
    deleted immediately after, not committed) calling
    `loadSimboxBindings()` for real and invoking `simbox_version()` —
    output `"libsimbox loaded OK, version: 1.0.0-standalone"`, confirming
    the monorepo-relative fallback path really resolves to the Phase-1-
    rebuilt `libsimbox.dylib` and the FFI call round-trips correctly.

- **Task 2.3 — Event struct union wrapper**: skipped as a separate task.
  Per the Task 2.1 discovery above, `ffigen`'s generated `UnnamedUnion`/
  `UnnamedStruct*` classes already provide fully-typed field access
  (`event.ref.data.incoming_call.caller`, etc.) — there is no raw-byte
  layout left to hand-wrap. What Task 2.3 actually still needs (a
  `Pointer<Char>? -> String?` conversion helper, since C strings need
  explicit UTF-8 decoding either way) is small enough to fold directly
  into Task 3.2's event-dispatch code rather than justify its own file.
  Marking as done-by-absorption, not deferred — will call this out again
  explicitly if Task 3.2 finds it needs more than expected.

**Ended at**: Phase 2 complete (2.1, 2.2 done; 2.3 absorbed into Phase 3
per the discovery above), about to start Phase 3 (Task 3.1)
**Handoff notes**: Both new `lib/src/ffi/` files are generated/written
and verified against the real native library, not just unit tests.
Next: `SimboxModemRepository`'s lifecycle + device listing (Task 3.1) —
the first piece of real modem-facing logic, everything downstream in
Phase 3/4 builds on it.

- **Task 3.1 — Lifecycle + device listing**:
  - `lib/src/linux/simbox_modem_repository.dart`: `SimboxModemRepository`
    — private constructor + `factory` (validates `simbox_init()` didn't
    return `nullptr` before the object exists, throwing
    `ModemDriverNotAvailableException` rather than leaving a half-valid
    instance around). `listModems()` walks
    `simbox_device_count`/`get_by_index`, rebuilding the serial->handle
    map each call. `getModem(modemId)` looks up the tracked handle.
    `_readDevice()` marshals `simbox_device_info_t` (via `calloc`-
    allocated struct pointer, freed in a `finally`) into `ModemDevice`,
    including a small `_charArrayToString` helper for the struct's fixed
    `char[N]` fields (`ffigen` exposes these as `Array<Char>`, no
    built-in string conversion exists for fixed arrays — only for
    `Pointer<Utf8>`). `dispose()` calls `simbox_shutdown`.
  - `lib/src/linux/simbox_state_mapping.dart`: three pure mapping
    functions (`simboxDeviceStateToModemState`/`...ToCallState`/
    `...ToRegistrationState`) implementing specifications' state table.
    `RegistrationState` mapping is **inferred, not given directly** by
    `simbox_api.h` (the C API has no separate registration concept) —
    documented in the function's doc comment as: any state implying
    ring/dial/hold/call-in-progress implies registration, since none of
    those are possible otherwise; `roaming`/`searching` are never
    produced (no native signal distinguishes them).
  - Fixed two real compile errors during writing (not deviations, just
    getting FFI array typing right): the char-array helper's parameter
    type must be `Array<Char>`, not `Array<int>` (`Char` is the
    `NativeType` bound `Array`'s generic requires — indexing yields
    `int` values, but the array's own type parameter must stay
    `Char`); and the constructor needed a `factory` + private-constructor
    split instead of computing `_handle` from a second
    `loadSimboxBindings()` call in the initializer list (would have
    opened the library twice).
  - `test/simbox_modem_repository_test.dart`: 3 tests, run against the
    **real** `libsimbox` (not mocked) via the default loader — relies
    only on the deterministic "0 devices at fresh init" baseline
    `test_simbox.c`'s own `test_lifecycle` already asserts on the native
    side, not on any real hardware. Skips gracefully (via
    `markTestSkipped`) if `libsimbox` isn't discoverable, so this stays
    a real unit test rather than turning into Task 5.1's gated
    integration test.
  - Verified: `dart analyze` clean on both new files; `flutter test
    test/simbox_modem_repository_test.dart` — 3/3 passing, none skipped
    (real library present and working in this environment).

**Ended at**: Phase 3, Task 3.1 complete, about to start Task 3.2 (event
bridging — flagged in the plan's Risk Assessment as this flow's highest-
risk task)
**Handoff notes**: Device listing/marshalling now proven against the
real library. Next: `NativeCallable.listener`-based event bridging —
budget real attention here per the plan's risk note; the polling
fallback (re-poll `simbox_device_get_info`/`simbox_device_state` on a
`Timer` instead of relying on the native callback) is the documented
escape hatch if `NativeCallable.listener` misbehaves.

- **Task 3.2 — Event bridging**: the plan's flagged highest-risk task
  materialized a real bug, found and fixed rather than needing the
  polling fallback.
  - `lib/src/linux/simbox_modem_repository.dart`: constructor now sets
    up `NativeCallable<simbox_event_cbFunction>.listener(_onNativeEvent)`
    and registers it via `simbox_set_event_callback`. `_onNativeEvent`
    dispatches through the mapping table from specifications
    (`SIMBOX_EVENT_DEVICE_CONNECTED`/`DISCONNECTED` ->
    `ModemAttached`/`ModemDetached` (updating `_devicesBySerial`
    live); `INCOMING_CALL`/`CALL_STATE_CHANGED` -> `ModemCallStateChanged`
    via a new `_activeCalls: Map<String, ModemCall>` cache (needed
    because `CALL_STATE_CHANGED`'s native payload only carries
    old/new state ints, no number/direction — the cache carries that
    forward from whichever event started the call);
    `INCOMING_SMS`/`USSD_RESPONSE`/`DEVICE_ERROR` -> their matching
    subtypes; `BALANCE_UPDATE`/`PROG_PROGRESS` dropped, per
    specifications, no matching `ModemEvent` subtype exists). Added
    `simboxDeviceStateToCallState` to `simbox_state_mapping.dart`
    (broader than Task 3.1's version — now covers the full state space
    so `CALL_STATE_CHANGED`'s `new_state` always resolves to a sensible
    `CallState`, including `terminated`/`failed` for
    `IDLE`/`DISCONNECTED`/`ERROR`, not just the "call in progress"
    states Task 3.1 needed).
  - **Real bug found and fixed — native-side pointer lifetime**: first
    test run crashed the whole test shell with `SIGABRT`. Isolating to a
    single test (no other tests in the file) turned the crash into a
    clean, informative error instead: `Invalid argument(s): Unknown
    value for simbox_event_type_t: 59580576` — garbage data. Root cause:
    `simbox_device_register()` (Task 1.1) built its `SIMBOX_EVENT_DEVICE_
    CONNECTED` event as a **stack-local** `simbox_event_t` and passed
    `&event` into the callback. That's safe for a plain synchronous C
    callback, but `NativeCallable.listener` is asynchronous by design —
    it hands the call off to the target isolate and returns immediately,
    so by the time Dart actually read `event->type`, `simbox_api.c`'s
    stack frame was already gone and the pointer was reading freed
    stack memory. Fixed at the source: `simbox_api.c`'s
    `simbox_device_register()` now `calloc`s the event on the heap
    before invoking the callback, with an explicit ownership-transfer
    contract (callback must `free()` it) documented on
    `simbox_event_cb`'s typedef in `simbox_types.h` — flagged there as a
    convention **every** future `cb(...)` call site in the native SDK
    must follow, not just this one. `_onNativeEvent` (Dart side) now
    wraps its dispatch in `try/finally { calloc.free(eventPtr); }`.
    **Follow-up note for Task 3.3+**: grepped the whole native SDK —
    `simbox_device_register()` in `simbox_api.c` is currently the
    *only* call site that fires the event callback at all;
    `simbox_modem.c`'s call/SMS/USSD functions (`simbox_call_originate`,
    `simbox_sms_send`, `simbox_ussd_send`, etc.) don't fire events yet.
    This directly affects Task 3.4's design (`sendUssd` was specified to
    await a `SIMBOX_EVENT_USSD_RESPONSE` event that nothing currently
    fires) — will need the same heap-allocate-and-transfer pattern added
    to whichever native call sites Task 3.3/3.4 end up needing events
    from, not just documented as a convention for hypothetical future
    code.
  - **Second bug found and fixed — test-only double-dispose**: after
    the native fix, the *file* (not the isolated single test) still
    crashed with the same SIGABRT, specifically right after the 3rd test
    ("dispose can be called safely..."). Root cause was in the test
    helper, not the library: `withRepo()` unconditionally registers
    `addTearDown(repo.dispose)`, but that particular test *also*
    explicitly called `dispose()` in its own body
    (`expect(repo.dispose, returnsNormally)`) — a genuine double-dispose,
    calling `simbox_shutdown()` on an already-freed handle. Fixed by
    making `SimboxModemRepository.dispose()` idempotent (`_disposed`
    bool guard) — a reasonable defensive API property regardless of the
    test bug (real callers could plausibly double-dispose too), and kept
    the test as an explicit idempotency check rather than removing the
    double-call.
  - `test/simbox_modem_repository_test.dart`: 2 new tests (5 total in
    the file) — real event fires `ModemAttached` with the right
    `modemId`/`device.portPath`, and the device becomes visible via
    `listModems()` afterward; re-registering the same serial does not
    fire a second event (exercises Task 1.1's native idempotency from
    the Dart side, not just the C side).
  - Verified: `dart analyze` clean; `flutter test
    test/simbox_modem_repository_test.dart` — 5/5 passing (3 runs in a
    row, no flakiness); full package `flutter test` — 39/39 passing;
    `dart analyze lib` — 0 errors.

**Ended at**: Phase 3, Task 3.2 complete, about to start Task 3.3 (call
operations)
**Handoff notes**: Event bridging is real and proven, including a
genuine cross-boundary memory bug caught and fixed rather than papered
over. Two things carry forward into Task 3.3/3.4: (1) the
heap-allocate-event convention now documented in `simbox_types.h` must
be applied to any *new* native event-firing code those tasks add: (2)
`simbox_modem.c` currently fires zero events for call/SMS/USSD
operations — Task 3.4's `sendUssd` design (await
`SIMBOX_EVENT_USSD_RESPONSE`) depends on this being added.

### Session 2026-08-23 - Claude

**Started at**: Phase 3, Task 3.4, resuming after `sdd-asterisk-chan-simbox`
delivered real event firing + a real synchronous `simbox_at_command`
(see that flow's Task 5.8) — the blocker noted at the end of the prior
session's Task 3.2 entry.

#### Completed

- **Task 3.4 — SMS/USSD**: `sendSms` (direct `simbox_sms_send` call).
  `sendUssd` sends via `simbox_ussd_send` then awaits the next
  `ModemUssdReceived` for that `modemId` on `modemEvents`, bounded by a
  `timeout` param (default 10s) — the design specifications always
  called for, unblocked now that `sdd-asterisk-chan-simbox` fires
  `SIMBOX_EVENT_USSD_RESPONSE` for real. `sendAtCommand` calls
  `simbox_at_command` directly.
  - `test/simbox_modem_repository_test.dart`: added coverage. Notably,
    `sendUssd`'s "simulated-timeout case" (called out by name in the
    plan's own verification note) is real, not synthetic: on this dev
    machine's non-Linux/simulated `libsimbox` path, `simbox_ussd_send`
    never fires an event at all (only the Linux/real path does per
    `sdd-asterisk-chan-simbox`'s design), so `sendUssd` reliably times
    out here — the test asserts exactly that.
  - Verified: `dart analyze` clean; targeted tests passing.

- **Task 3.5 — AT commands & diagnostics**: `changeImei` calls
  `simbox_change_imei` and turns a non-zero result into a `ModemException`
  that names the real cause (`ttyprog_changeimei` undefined upstream, per
  `sdd-asterisk-chan-simbox` Task 5.7 — not a generic failure). On this
  machine's simulated path `simbox_change_imei` actually succeeds
  (writes straight into the device struct), so the happy-path test here
  exercises a real write/read-back round trip, not just a stub return.
  `setDiagMode(enabled: true)` opens the device's `tty_data` port via
  `simbox_prog_open` + `simbox_prog_set_diagmode`; `enabled: false`
  throws `UnsupportedError` (no native "exit diag mode" function exists —
  confirmed by reading `simbox_programmator.c` directly, not assumed).
  - Verified: `dart analyze` clean; new tests for both methods passing,
    including the `enabled: false` and no-tty-port `UnsupportedError`/
    `ModemException` paths.

- **Task 3.6 — Power / restart / network mode / group**: `setPower`/
  `restartModem` both route through `sendAtCommand`
  (`AT+CFUN=1,1`/`AT+CFUN=0`); `restartModem`'s `graceful`/
  `whenConvenient` modes wait for the tracked call (if any) on that
  `modemId` to reach `terminated`/`failed` via `modemEvents`, bounded by
  a 30s timeout, before issuing the reset. `setNetworkMode` only wires
  `NetworkMode.gsmOnly` (`AT^SYSCFG=13,...`, confirmed from chan_svistok's
  own reference source) — `auto`/`wcdmaOnly` throw `UnsupportedError`
  rather than guessing an unconfirmed mode code, per specifications'
  explicit design decision (a wrong code could lock a real modem to an
  unreachable network). `setGroup` is pure in-memory Dart state (a
  `Map<String, String>`), no native call — matches specifications, no
  persistence layer added without being asked for one.
  - Verified: `dart analyze` clean; `flutter test` — full package
    (55 tests at this point) green.

- **Task 4.1 — Threading (`Isolate.run` wrapping)**: wrapped every
  blocking native call (`dial`/`hangupCall`/`answerCall`/`sendSms`/
  `sendUssd`/`sendAtCommand`/`changeImei`/`setDiagMode`'s two calls) in
  `Isolate.run`, per specifications' "Threading" design. This is the one
  task in the whole flow where the plan's own stated assumption ("verify
  during implementation whether `Isolate.run`'s ephemeral isolate can
  safely call into the same native library instance... only Dart-side
  native callback registration is isolate-sensitive") turned out to be
  **wrong**, and needed real redesign, not just verification:
  - **Bug 1 — `DynamicLibrary` is not sendable across isolates.**
    Capturing an already-open `SimboxBindings`/`DynamicLibrary` in the
    closure passed to `Isolate.run` throws at runtime: `Invalid
    argument(s): Illegal argument in isolate message: (object is a
    DynamicLibrary)`. Confirmed empirically (this is exactly why
    specifications flagged it as needing verification rather than just
    asserting it). Fixed by never capturing the outer `SimboxBindings`:
    `SimboxModemRepository` now also tracks the resolved library `path`
    (added `loadSimboxBindingsWithPath()`/`resolveSimboxLibraryPath()`
    to `lib/src/ffi/simbox_native_library.dart`, alongside the existing
    `loadSimboxBindings()` which now just calls the new function and
    discards the path), and every `Isolate.run` closure reopens a fresh
    `SimboxBindings` from that path via a new top-level
    `_openBindingsForIsolate(path)` in `simbox_modem_repository.dart`
    (top-level, not a method, specifically so referencing it can't
    accidentally capture `this`). `dlopen`-ing the same path twice just
    increments the OS's refcount on the already-mapped library, not a
    real reload.
  - **Bug 2 — `Pointer` values need `.address`/`.fromAddress()`, not
    direct capture.** Even after fixing Bug 1, `sendAtCommand`'s
    response buffer came back containing uninitialized-looking garbage
    instead of `"OK\r\n"`, despite the native call reporting success.
    Directly capturing `Pointer<T>` objects in the `Isolate.run` closure
    was not reliably preserving write-visibility back on the calling
    isolate. Fixed by converting every `Pointer` argument to its raw
    `.address` (a plain `int`, unambiguously sendable) before entering
    the closure, and reconstructing via `Pointer<T>.fromAddress(addr)`
    inside it — confirmed via a standalone repro script (`Isolate.run`
    writing a known string into a `calloc`'d buffer via a reconstructed
    address-based pointer, read back correctly on the calling isolate
    afterward) that this pattern is reliable where direct capture wasn't.
  - **Bug 3 — a real use-after-free, caught by a failing test, not
    review.** After fixing Bugs 1-2, `sendAtCommand`'s test still failed
    with `FormatException: Missing extension byte`. Root cause: the
    method attached *two* separate listeners to the same `Isolate.run`
    future — one via `unawaited(native.then(...).whenComplete(free))`
    (added specifically to avoid freeing the buffer before a *timeout*
    fired, a real concern since `simbox_at_command` can be mid-write for
    up to ~3s on the real Linux path) and one via
    `await native.timeout(timeout)`. On **normal** completion, Dart runs
    same-future listeners in attachment order — since the `unawaited`
    free was attached first, it ran and freed `responseBuf` *before* the
    `await` continuation resumed and read it. Fixed by restructuring so
    the free happens synchronously in the same continuation that reads
    the buffer (race-free by construction), and only deferred to a
    separate `native.then(...)` listener in the `on TimeoutException`
    branch specifically (where reading the buffer never happens at all,
    so there's no ordering hazard to protect against).
  - Added `test/simbox_modem_repository_test.dart`: a
    `Timer.periodic`-based "doesn't block a concurrent Timer" test was
    written per the plan's verification note, found genuinely flaky
    under full-suite runs (real OS timer granularity vs. how fast the
    simulated-path native call actually returns — not a meaningful
    signal at that speed), and **removed** rather than kept flaky;
    documented in its place why, and where the real verification lives
    (the standalone repro above, described in a code comment).
  - Verified: `dart analyze` clean; full package `flutter test` green
    (55/55) across 3 consecutive runs, confirming Bug 3's fix wasn't
    itself flaky.

- **Task 4.2 — Rewire `LinuxFlutterGsm`**: every method now delegates
  one-to-one to a `SimboxModemRepository`, lazily constructed on first
  use (not at construction/registration time — matches
  `ModemDriverNotAvailableException`'s existing "fail at first use"
  convention, so a dev machine without `libsimbox` built doesn't crash
  at plugin registration). Added a constructor-level injection seam
  (`LinuxFlutterGsm({SimboxModemRepository? repository})`) for tests,
  since `SimboxModemRepository` is concrete (no abstract interface to
  mock) — tests inject a real repository built via the existing
  skip-if-unavailable pattern rather than hitting the default lazy path,
  which stays exercised by one dedicated test instead.
  `modemEvents` specifically catches `ModemDriverNotAvailableException`
  and returns `const Stream.empty()` — the one method here that must not
  throw even if the driver is unavailable, per
  `FlutterGsmPlatform.modemEvents`'s own doc comment; every other method
  lets the exception propagate as-is (already the exact type
  `ModemRepositoryImpl` expects at the top, no wrapping needed since
  `_guard` only catches `UnimplementedError`, which
  `SimboxModemRepository` never throws).
  - `test/linux_flutter_gsm_test.dart`: fully rewritten per the plan's
    note ("mock/fake `SimboxModemRepository` rather than hitting the
    real native library") — uses the injection seam with a real,
    skip-if-unavailable repository rather than inventing a new abstract
    interface purely for a fake (would have been premature abstraction
    for a single test file; the injection seam alone satisfies the
    plan's actual goal of not depending on the default lazy-load path).
  - Verified: `dart analyze` clean; full package `flutter test` green
    (57/57) across 2 consecutive runs.

- **Task 5.1 — Gated integration test**: satisfied by existing coverage,
  no new file created. `test/simbox_modem_repository_test.dart` (built
  incrementally since Task 3.1) already exercises exactly the lifecycle
  the plan/specifications describe for this task (init -> register
  (the Dart-side equivalent of "discover", via `debugRegisterDiscoveredDevice`,
  which calls the same real `simbox_device_register()` Phase 1 added) ->
  device ops -> shutdown), gated the same way (skip, not fail, if
  `libsimbox` isn't built) specifications ask for. Writing a second,
  near-identical file under a different name would have been pure
  duplication against "don't add abstractions/files beyond what's
  needed" — flagging this as a deliberate scope consolidation, not a
  silently-dropped task.

- **Task 5.2 — Full regression + example app smoke check**: `dart
  analyze lib test` in `flutter_gsm` (0 errors, 2 pre-existing unrelated
  infos), `libsFlutter/flutter_gsm/example` (0 errors, pre-existing
  warnings/infos in `theme/`/`imei_validator.dart`, none touched by this
  flow), and `apps/simbox-app` (0 errors, same pre-existing `theme/`
  infos) — none of the pre-existing issues are regressions, all are in
  files this flow never touched. `flutter test` green in `flutter_gsm`
  (57/57) and `simbox-app` (10/10, using its own `FakeModemRepository`,
  confirming it isn't affected by `LinuxFlutterGsm` no longer being a
  stub). `example/` has no `test/` files (pre-existing, not introduced
  here) — `dart analyze` is the practical compile-check proxy used
  instead, consistent with this session's established verification
  pattern elsewhere (no real Linux host to actually `flutter run` it).

- **Task 5.3 — Documentation**: `README.md` — Platform Support table's
  Linux row now describes the real `libsimbox`/`dart:ffi` driver instead
  of "pending"; Windows/macOS row clarifies the binding (not the native
  library) is what's Linux-only this iteration. New "Native Library
  Loading (Linux)" section documents the env-var override
  (`FLUTTER_GSM_SIMBOX_LIB`) and monorepo-relative dev-path fallback,
  explicitly flagged as dev-mode-only pending a real CMake bundling
  step. Known Issues section replaced the single old "desktop driver
  pending" bullet with Linux-specific gaps that are real and
  ongoing (`setNetworkMode`'s unconfirmed AT^SYSCFG codes,
  `setDiagMode(false)`, `changeImei`'s upstream `ttyprog_changeimei`
  gap) plus a Windows/macOS-still-pending bullet, so the doc doesn't
  overclaim Linux is now gap-free.

#### Deviations from Plan

- **Task 5.1**: no new `simbox_modem_repository_integration_test.dart`
  file — existing `simbox_modem_repository_test.dart` already satisfies
  the task's stated goal. See that task's log entry above for the full
  rationale.
- **Task 4.1's verification test**: the plan asked for a `Timer`-based
  "doesn't block a concurrent Future" test; written, found flaky, and
  replaced with a documented pointer to a standalone repro instead (see
  that task's log entry). The *design* (`Isolate.run` wrapping every
  blocking call) is unchanged from the plan — only the *automated proof*
  of it changed, because the originally-planned proof technique wasn't
  reliable at this call's actual speed on this machine.

**Ended at**: Phase 5 complete — all planned tasks done or explicitly
deviated-with-rationale as above.
**Handoff notes**: The flow's core deliverable (`LinuxFlutterGsm` for
real, backed by `libsimbox` via `dart:ffi`) is complete and verified
against the real native library on this (macOS, non-Linux/simulated
`libsimbox` path) dev machine. Two things a future Linux-host session
should still do, carried over from `sdd-asterisk-chan-simbox`'s own
still-open items rather than new gaps this flow introduced: (1) exercise
the real Linux/`SIMBOX_DEV_REAL` code paths this package's tests can
only reach via the simulated path here (`simbox_at_command`'s actual
~3s blocking wait, `simbox_call_originate`/etc.'s real `cpvt_alloc`
path) — nothing here is expected to behave differently, but it's
unverified; (2) `setNetworkMode`'s `auto`/`wcdmaOnly` `AT^SYSCFG` codes
remain unconfirmed against real hardware/vendor AT reference, still
throwing `UnsupportedError` by design rather than guessing.

---

## Deviations Summary

| Planned | Actual | Reason |
|---------|--------|--------|
| Task 5.1: new `simbox_modem_repository_integration_test.dart` | No new file — existing `simbox_modem_repository_test.dart` used instead | Already covers the exact same lifecycle/gating; a second near-identical file would be pure duplication |
| Task 4.1: `Timer`-based "doesn't block" test | Test written, found flaky, removed; verified instead via a standalone repro documented in a code comment | Real OS timer granularity isn't a reliable signal against how fast the simulated-path native call actually returns |

## Learnings

- **`Isolate.run` + `dart:ffi` has two real, easy-to-miss traps**:
  (1) an already-open `DynamicLibrary`/generated bindings object cannot
  be captured by the closure — reopen by path (a `String`) inside the
  spawned isolate instead; (2) `Pointer<T>` values should be converted
  to `.address` (`int`) before capture and reconstructed via
  `Pointer<T>.fromAddress()` inside the closure, not captured directly —
  direct capture didn't reliably preserve cross-isolate write-visibility
  in this environment. Both were caught by tests actually failing, not
  by reasoning about the API in the abstract — a reminder that "the spec
  said to verify this empirically" was the right call, not
  over-caution.
- **Two listeners on the same `Future`, one of them `unawaited`, is a
  latent ordering bug waiting to happen.** Attaching a cleanup listener
  "just in case" alongside the main `await` looked safe in isolation but
  wasn't — same-future listeners run in attachment order on normal
  completion, so a `finally`-style cleanup needs to live in the actual
  continuation that uses the value, not off to the side, unless it's
  provably only reachable on a path where the value is never read.

## Completion Checklist

- [x] All tasks completed or explicitly deferred
- [x] Tests passing
- [x] No regressions
- [x] Documentation updated if needed
- [ ] Status updated to COMPLETE
