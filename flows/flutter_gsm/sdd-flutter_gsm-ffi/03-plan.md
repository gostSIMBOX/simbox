# Implementation Plan: sdd-flutter_gsm-ffi

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-08-21
> Specifications: [02-specifications.md](02-specifications.md)

## Summary

Bottom-up: fix the native discovery→registry gap first (nothing above it
can be tested for real otherwise), then generate FFI bindings, then build
`SimboxModemRepository` method-group by method-group (device listing →
calls → SMS/USSD → AT/diagnostics → power/network/group), then rewire
`LinuxFlutterGsm` to delegate to it, then tests. Each task ends with a
concrete verification step (`make`/`dart analyze`/`flutter test`) — no
task is "done" without running it, matching this session's established
checkpoint discipline.

## Task Breakdown

### Phase 1: Native fix

#### Task 1.1: `simbox_device_register()` + registry wiring
- **Description**: Add a new public function to `simbox_api.h`/
  `simbox_api.c` that constructs a `simbox_device_t` from a
  `simbox_discovered_device_t` (via the existing internal
  `simbox_device_create`) and appends it to `inst->devices[]`. This is
  the missing link between `simbox_discovery_scan()` and
  `simbox_device_count()`/`get_by_index()`.
- **Files**:
  - `libsCpp/asterisk_chan_simbox/src/simbox_api.h` — Modify (declare
    `int simbox_device_register(simbox_handle_t handle, const
    simbox_discovered_device_t *discovered);`)
  - `libsCpp/asterisk_chan_simbox/src/simbox_api.c` — Modify (implement;
    populate `simbox_device_info_t` from the discovered device's
    `serial_number`/`imei`/`data_port`/`audio_port` fields, append to
    `inst->devices[inst->device_count++]` under the existing mutex)
- **Dependencies**: None
- **Verification**: `make` in `libsCpp/asterisk_chan_simbox/` builds
  clean (`libsimbox.a`/`.dylib`, no new warnings)
- **Complexity**: Low

#### Task 1.2: Native test for the registry wiring
- **Description**: Extend `tests/test_simbox.c` with a test proving a
  `simbox_discovered_device_t` (from `simbox_discovery_device_get`, or a
  hand-built one if real USB enumeration returns 0 in the test
  environment — matches how Test 2 already fabricates data) becomes a
  queryable `simbox_device_t` via `simbox_device_register` +
  `simbox_device_count`/`get_by_index`, without using the test-only
  `simbox_device_create()` shortcut directly. Satisfies requirements'
  Acceptance Criterion 4.
- **Files**:
  - `libsCpp/asterisk_chan_simbox/tests/test_simbox.c` — Modify (add
    `test_discovery_registry_wiring()`, call from `main()`)
- **Dependencies**: Task 1.1
- **Verification**: `./test_simbox` (built by root Makefile) — all
  suites including the new one pass
- **Complexity**: Low

### Phase 2: FFI foundation

#### Task 2.1: `ffigen` setup + generated bindings
- **Description**: Add `ffigen` (dev dependency) and `ffi` (regular
  dependency) to `pubspec.yaml`. Write `ffigen.yaml` pointing at
  `libsCpp/asterisk_chan_simbox/src/simbox_api.h`. Run `dart run ffigen`
  to produce `lib/src/ffi/simbox_bindings.dart`.
- **Files**:
  - `pubspec.yaml` — Modify (add `ffi`, `ffigen` deps)
  - `ffigen.yaml` — Create
  - `lib/src/ffi/simbox_bindings.dart` — Create (generated, not hand-
    edited — note this in a header comment)
- **Dependencies**: Task 1.1 (header must have the final, real API
  surface including `simbox_device_register` before generating)
- **Verification**: `dart run ffigen` completes without error; `dart
  analyze lib/src/ffi/simbox_bindings.dart` clean
- **Complexity**: Low (mechanical, but first real FFI codegen in this
  monorepo — verify the generated output looks sane before building on
  top of it)

#### Task 2.2: Native library loader
- **Description**: `SimboxNativeLibrary` — `DynamicLibrary` loading per
  specifications' path-resolution strategy (env var →
  system-installed name → monorepo-relative dev path), throwing
  `ModemDriverNotAvailableException` if all candidates fail.
- **Files**:
  - `lib/src/ffi/simbox_native_library.dart` — Create
  - `test/simbox_native_library_test.dart` — Create (covers the
    fallback-chain logic with a fake/missing-library scenario; doesn't
    require a real `libsimbox` to be present)
- **Dependencies**: Task 2.1
- **Verification**: `dart analyze` clean; new test passes; manually
  confirm it actually loads the real `libsimbox.dylib`/`.so` built by
  Phase 1 (one-off `dart run` smoke check, not a committed test, since
  CI/other machines may not have it built)
- **Complexity**: Low

#### Task 2.3: Event struct union wrapper
- **Description**: Thin hand-written helper reading `simbox_event_t`'s
  tagged union (`ffigen` exposes it as raw bytes) based on `event.type`
  — one function per event's relevant field(s)
  (`_incomingSmsFrom(event)`/`_callStateOldNew(event)`/etc.).
- **Files**:
  - `lib/src/ffi/simbox_event_union.dart` — Create
  - `test/simbox_event_union_test.dart` — Create (construct raw struct
    bytes for each event type, verify correct field extraction)
- **Dependencies**: Task 2.1
- **Verification**: `flutter test test/simbox_event_union_test.dart`
  passes for all 9 event types
- **Complexity**: Medium (the one place this flow touches raw memory
  layout by hand — get it wrong and it's a silent wrong-field read, not
  a crash, so test every event type explicitly)

### Phase 3: `SimboxModemRepository` — core

#### Task 3.1: Lifecycle + device listing
- **Description**: `SimboxModemRepository` class: constructor calls
  `simbox_init`, owns the serial->handle map, implements
  `listModems()`/`getModem()` (populating/refreshing the map from
  `simbox_device_count`/`get_by_index`/`get_info`), `dispose()` calls
  `simbox_shutdown`.
- **Files**:
  - `lib/src/linux/simbox_modem_repository.dart` — Create
  - `test/simbox_modem_repository_test.dart` — Create (device listing/
    mapping tests only so far)
- **Dependencies**: Task 2.2
- **Verification**: `dart analyze`; new tests pass (unit-level, no real
  hardware — verify against a `libsimbox` instance with 0 devices, which
  is exactly what `test_lifecycle`'s own assertion already confirms is
  the baseline state)
- **Complexity**: Medium

#### Task 3.2: Event bridging
- **Description**: Wire `NativeCallable.listener` per specifications;
  dispatch each native event through the Task 2.3 union wrapper into the
  mapping table's `ModemEvent` subtypes; expose `modemEvents` stream;
  update/remove tracked devices on attach/detach events.
- **Files**:
  - `lib/src/linux/simbox_modem_repository.dart` — Modify
  - `test/simbox_modem_repository_test.dart` — Modify (add event-
    dispatch tests, feeding synthetic `simbox_event_t` structs through
    the same path the native callback would use)
- **Dependencies**: Task 3.1, Task 2.3
- **Verification**: tests pass; `dart analyze`
- **Complexity**: High (the `NativeCallable.listener` + cross-thread
  callback plumbing is the riskiest part of this flow per
  specifications — budget real debugging time)

#### Task 3.3: Call operations
- **Description**: `dial`/`hangupCall`/`answerCall`, per the
  `modemId == callId` identity mapping in specifications.
- **Files**:
  - `lib/src/linux/simbox_modem_repository.dart` — Modify
  - `test/simbox_modem_repository_test.dart` — Modify
- **Dependencies**: Task 3.1
- **Verification**: tests pass
- **Complexity**: Low

#### Task 3.4: SMS/USSD
- **Description**: `sendSms` (direct call); `sendUssd` (send +
  await matching `ModemUssdReceived` event with timeout, per
  specifications).
- **Files**:
  - `lib/src/linux/simbox_modem_repository.dart` — Modify
  - `test/simbox_modem_repository_test.dart` — Modify
- **Dependencies**: Task 3.2 (needs the event stream for USSD's
  response-await), Task 3.1
- **Verification**: tests pass, including a simulated-timeout case for
  `sendUssd`
- **Complexity**: Medium

#### Task 3.5: AT commands & diagnostics
- **Description**: `sendAtCommand` (direct, with `.timeout()`
  enforcement per specifications), `changeImei` (direct),
  `setDiagMode(enabled: true)` (via `simbox_prog_open` using the
  device's `tty_data` port + `simbox_prog_set_diagmode`;
  `enabled: false` throws `UnsupportedError`, documented gap).
- **Files**:
  - `lib/src/linux/simbox_modem_repository.dart` — Modify
  - `test/simbox_modem_repository_test.dart` — Modify
- **Dependencies**: Task 3.1
- **Verification**: tests pass
- **Complexity**: Medium

#### Task 3.6: Power / restart / network mode / group
- **Description**: `setPower` (`AT+CFUN=1,1` / `AT+CFUN=0`),
  `restartModem` (`AT+CFUN=1,1`, with `graceful`/`whenConvenient` call-
  state gating), `setNetworkMode` (`AT^SYSCFG` — `gsmOnly` real,
  `auto`/`wcdmaOnly` throw `UnsupportedError` with a clear message
  pointing at the unconfirmed-mode-code gap, **unless** Anton confirms
  real codes before/during this task, in which case wire them for
  real), `setGroup` (in-memory `Map<String, String>`, per specifications'
  resolution — no `shared_preferences` unless redirected).
- **Files**:
  - `lib/src/linux/simbox_modem_repository.dart` — Modify
  - `test/simbox_modem_repository_test.dart` — Modify
- **Dependencies**: Task 3.1, Task 3.2 (restart's graceful mode needs
  call-state visibility)
- **Verification**: tests pass
- **Complexity**: Medium

### Phase 4: Wiring & threading

#### Task 4.1: Threading (`Isolate.run` wrapping)
- **Description**: Audit every blocking native call added in Phase 3
  and wrap with `Isolate.run` per specifications, so nothing blocks the
  main isolate. Verify this doesn't break the `NativeCallable.listener`
  callback path from Task 3.2 (per specifications, `Pointer`/
  `DynamicLibrary` are process-global — confirm empirically here, not
  just by spec reasoning).
- **Files**:
  - `lib/src/linux/simbox_modem_repository.dart` — Modify
- **Dependencies**: Tasks 3.1-3.6
- **Verification**: existing tests still pass after wrapping; add one
  test asserting a slow AT-command call doesn't block a concurrent
  `Future` from completing (proves it's really off the main isolate)
- **Complexity**: Medium

#### Task 4.2: Rewire `LinuxFlutterGsm`
- **Description**: Replace every `_notImplemented(...)` stub method
  with delegation to a `SimboxModemRepository` instance. Keep
  `getPlatformVersion()`'s existing real implementation untouched.
- **Files**:
  - `lib/src/linux/linux_flutter_gsm.dart` — Modify
  - `test/linux_flutter_gsm_test.dart` — Modify (existing 3-test stub-
    behavior file needs rewriting to match real delegation — mock/fake
    `SimboxModemRepository` rather than hitting the real native library
    in this unit test)
- **Dependencies**: Task 3.6, Task 4.1
- **Verification**: `flutter test test/linux_flutter_gsm_test.dart`
  passes
- **Complexity**: Low

### Phase 5: Integration & polish

#### Task 5.1: Gated integration test
- **Description**: `test/simbox_modem_repository_integration_test.dart`
  — real end-to-end against the actual `libsimbox` (skips cleanly if it
  can't be loaded), covering the same lifecycle as `tests/test_simbox.c`
  plus the new registry wiring.
- **Files**:
  - `test/simbox_modem_repository_integration_test.dart` — Create
- **Dependencies**: Task 4.2
- **Verification**: passes when `libsimbox` is built and present;
  skips (not fails) when absent — confirm both cases manually
- **Complexity**: Low

#### Task 5.2: Full regression + example app smoke check
- **Description**: `dart analyze lib test`; `flutter test`
  (full suite, not just new files); update `flutter_gsm/example`'s
  `ModemListScreen` demo (already real-API-shaped from
  `sdd-flutter_gsm`'s barrel cleanup) to confirm it still compiles/runs
  against the now-real `LinuxFlutterGsm`; re-check `simbox-app`'s
  `dart analyze`/`flutter test` still pass (it depends on `flutter_gsm`
  directly).
- **Files**: none new — verification-only task
- **Dependencies**: Task 5.1
- **Verification**: 0 analyzer errors across `flutter_gsm` + example +
  `simbox-app`; full `flutter test` green in all three
- **Complexity**: Low

#### Task 5.3: Documentation
- **Description**: Update `flutter_gsm/README.md`'s "Known Issues"/
  platform-support section — Linux is no longer a stub. Document the
  env-var override (`FLUTTER_GSM_SIMBOX_LIB`) and the monorepo-dev-path
  fallback so a future reader knows this isn't yet a packaged/
  redistributable native dependency (see the CMake-bundling follow-up
  flagged in specifications).
- **Files**:
  - `libsFlutter/flutter_gsm/README.md` — Modify
- **Dependencies**: Task 5.2
- **Verification**: read-through only
- **Complexity**: Low

## Dependency Graph

```
1.1 ─→ 1.2
 │
 └─→ 2.1 ─┬─→ 2.2 ─┐
          └─→ 2.3 ─┤
                    ├─→ 3.1 ─┬─→ 3.2 ─┬─→ 3.4
                    │        │        │
                    │        ├─→ 3.3  ├─→ 3.5
                    │        │        │
                    │        └────────┴─→ 3.6 ─┐
                    │                            │
                    └────────────────────────────┴─→ 4.1 ─→ 4.2 ─→ 5.1 ─→ 5.2 ─→ 5.3
```

## File Change Summary

| File | Action | Reason |
|------|--------|--------|
| `libsCpp/asterisk_chan_simbox/src/simbox_api.h` | Modify | Declare `simbox_device_register` |
| `libsCpp/asterisk_chan_simbox/src/simbox_api.c` | Modify | Implement discovery→registry wiring |
| `libsCpp/asterisk_chan_simbox/tests/test_simbox.c` | Modify | New test for the wiring |
| `libsFlutter/flutter_gsm/pubspec.yaml` | Modify | Add `ffi`/`ffigen` deps |
| `libsFlutter/flutter_gsm/ffigen.yaml` | Create | ffigen config |
| `libsFlutter/flutter_gsm/lib/src/ffi/simbox_bindings.dart` | Create | Generated FFI bindings |
| `libsFlutter/flutter_gsm/lib/src/ffi/simbox_native_library.dart` | Create | Library loader |
| `libsFlutter/flutter_gsm/lib/src/ffi/simbox_event_union.dart` | Create | Event union reader |
| `libsFlutter/flutter_gsm/lib/src/linux/simbox_modem_repository.dart` | Create | Real Linux modem logic |
| `libsFlutter/flutter_gsm/lib/src/linux/linux_flutter_gsm.dart` | Modify | Delegate to `SimboxModemRepository` |
| `libsFlutter/flutter_gsm/test/*` | Create/Modify | Per-task unit + integration tests |
| `libsFlutter/flutter_gsm/README.md` | Modify | Document real Linux support + dev-mode lib loading |

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| `NativeCallable.listener` cross-thread callback misbehaves (crash, dropped events, wrong isolate) | Medium | High | Isolated as its own task (3.2) with dedicated tests; budget extra time; fall back to polling `simbox_device_get_info`/`simbox_device_state` on a `Timer` if the callback approach proves unreliable, documented as a spec deviation if taken |
| `setNetworkMode`'s unconfirmed `AT^SYSCFG` codes get guessed instead of verified, silently misconfiguring hardware | Low (already gated by design: unconfirmed codes throw `UnsupportedError`) | High if guessed wrong | Task 3.6 explicitly keeps them unsupported unless confirmed |
| No real hardware available during implementation to verify end-to-end | Medium | Medium | Phase 1-4 all have unit-level verification paths that don't need hardware (per specifications' testing strategy); only Task 5.1's integration test and final hardware-level confidence need it — flag remaining hardware-only verification explicitly in the implementation log rather than claiming full confidence without it |
| `ffigen` output has an unexpected shape (e.g. struct padding/union handling different from assumed) | Low | Medium | Task 2.1 verifies the generated file directly before Phase 3 builds on it |

## Rollback Strategy

1. Every task is additive (new files) except Tasks 1.1/4.2 (native
   header/`.c` modification, `LinuxFlutterGsm` rewrite) — both have a
   clear prior state (`_notImplemented` stubs, no `simbox_device_register`)
   to revert to file-by-file if a task proves unworkable.
2. No task deletes existing passing tests without replacing them in the
   same task (Task 4.2 explicitly rewrites, not deletes,
   `linux_flutter_gsm_test.dart`).
3. If Phase 3's `SimboxModemRepository` proves fundamentally blocked
   (e.g. `NativeCallable.listener` risk above materializes badly),
   `LinuxFlutterGsm` stays on its current stub implementation — Task 4.2
   is the only point of no return, sequenced last.

## Checkpoints

After each phase, verify:

- [x] Phase 1: `make` + `./test_simbox` clean in `libsCpp/asterisk_chan_simbox`
- [x] Phase 2: `dart analyze` clean on the 3 new `ffi/` files
- [x] Phase 3: `dart analyze` + `flutter test` clean, all `SimboxModemRepository` method groups covered
- [x] Phase 4: `flutter test` clean including rewritten `linux_flutter_gsm_test.dart`
- [x] Phase 5: full-package + example + `simbox-app` regression green

## Open Implementation Questions

- [ ] Real `AT^SYSCFG` codes for `auto`/`wcdmaOnly` network modes — not
  resolved (no real hardware available this session); Task 3.6 shipped
  with them unsupported (`UnsupportedError`), per this plan's own
  fallback — not a blocker, carried forward in `_status.md`.
- [x] Whether `NativeCallable.listener`'s cross-isolate behavior needs
  the polling fallback — resolved during Task 3.2 (prior session): it
  works correctly as designed, no polling fallback needed.

---

## Approval

- [ ] Reviewed by: Anton
- [ ] Approved on:
- [ ] Notes:
