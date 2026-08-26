# Status: sdd-flutter_gsm-ffi

## Current Phase

IMPLEMENTATION

## Phase Status

IMPLEMENTATION COMPLETE — all planned tasks done or explicitly
deviated-with-rationale (see 04-implementation-log.md)

## Last Updated

2026-08-23 by Claude (Phases 1-5 all done: 3.4-3.6, 4.1, 4.2, 5.1-5.3
completed this session)

## Blockers

**Naming note (2026-08-24)**: this flow, together with
`flows/simbox-app/sdd-simbox-app-real-driver`, fulfills the goal
originally slotted as `sdd-flutter_gsmsip-channel` (step 3 of the
3-flow sequence noted in `sdd-flutter_gsmsip-interface`'s own status —
"real ttyUSB/AT-command modem driver implementation"). That flow name
was never actually created; someone looking for it should land here
and on `sdd-simbox-app-real-driver` instead. Confirmed with Anton, no
new flow needed.

None otherwise currently blocking. Two things carried forward for a
future real-Linux-host session (not gaps this flow introduced — see
04-implementation-log.md's final handoff note for full detail):

- The real `SIMBOX_DEV_REAL`/Linux code paths in `libsimbox`
  (`simbox_at_command`'s actual ~3s blocking wait, real
  `cpvt_alloc`-based call origination, etc.) have only been exercised
  via the non-Linux/simulated path on this macOS dev machine. Nothing
  is expected to behave differently on real Linux, but it's unverified
  here.
- `setNetworkMode`'s `auto`/`wcdmaOnly` `AT^SYSCFG` codes remain
  unconfirmed against real hardware/vendor AT reference — still throws
  `UnsupportedError` by design rather than guessing (see `03-plan.md`'s
  Open Implementation Questions).

## Progress

- [x] Requirements drafted
- [x] Requirements approved (2026-08-21)
- [x] Specifications drafted
- [x] Specifications approved (2026-08-21)
- [x] Plan drafted
- [x] Plan approved (2026-08-22)
- [x] Implementation started (2026-08-22)
- [x] Implementation complete (2026-08-23)

## Context Notes

Key decisions and context for resuming:

- **This flow binds `flutter_gsm`'s `LinuxFlutterGsm` (currently a full
  stub) to `libsimbox`** — the native C SDK `sdd-asterisk-chan-simbox`
  shipped (`libsCpp/asterisk_chan_simbox`, `simbox_api.h`/
  `simbox_types.h`, built as `libsimbox.a`/`.dylib`/`.so`). Via
  `dart:ffi`.
- **Real gap found by reading `simbox_api.c` directly, not assumed**:
  `libsimbox`'s discovery subsystem (`simbox_discovery_*`, USB/hub scan)
  and its device registry (`simbox_device_count`/`get_by_index`, what
  calls/SMS/AT-commands operate on) are **not connected** —
  `simbox_init()` never populates the device array, `auto_discovery` in
  `simbox_config_t` is accepted but unused, and the only thing that ever
  registers a device (`simbox_device_create()`) isn't even in the public
  header — only called by the test file to fabricate a fake device.
  Confirmed by Anton (2026-08-21) as **in scope for this flow** to fix
  natively (editing `src/simbox_api.c`/`simbox_discovery.c` — new
  adapter-layer files from this session's `sdd-asterisk-chan-simbox`
  work, not the read-only vendored `asterisk_chan_svistok/`).
- `sdd-asterisk-chan-simbox` itself is marked COMPLETE (by Anton's own
  tooling, "Antigravity", 2026-08-21) — that status describes
  compile/link/integration-test success, not full end-to-end
  discovery→registry→calls wiring, per the finding above.
- `simbox_api.h`'s public surface maps closely onto `ModemRepository`:
  `simbox_device_get_by_index/sn` → `listModems`/`getModem`,
  `simbox_call_originate/answer/hangup` → `dial`/`answerCall`/
  `hangupCall`, `simbox_sms_send`/`simbox_ussd_send` →
  `sendSms`/`sendUssd`, `simbox_at_command` → `sendAtCommand`,
  `simbox_change_imei` → `changeImei`. No native equivalent exists yet
  for `setPower`/`restartModem`/`setNetworkMode`/`setGroup` — flagged as
  Should-Have, likely AT-command-based, to verify in specifications.
- Windows/macOS FFI binding explicitly out of scope this iteration
  (`MacosFlutterGsm`/`WindowsFlutterGsm` stay stubbed) even though
  `libsimbox`'s Makefile already has a Darwin build branch.
- Biggest open architectural question for specifications: how
  `libsimbox.so`/`.dylib` actually ships/is discovered by a Flutter
  Linux app at runtime (system-installed vs. plugin-bundled build step
  vs. bundled prebuilt binary) — `flutter_gsm`'s `linux:` pubspec entry
  is currently pure-Dart (`dartPluginClass`, no native CMake scaffold at
  all), so this may require adding one.

## Next Actions

All 5 phases / 15 tasks are done (see 04-implementation-log.md for full
detail, including two deliberate deviations-with-rationale). Nothing is
required to close this flow out. Optional follow-ups, not blocking:

1. On a real Linux host: exercise the `SIMBOX_DEV_REAL` code paths this
   package's tests could only reach via the non-Linux/simulated
   `libsimbox` path here (real ~3s `simbox_at_command` blocking wait,
   real `cpvt_alloc`-based call origination).
2. Confirm `setNetworkMode`'s `auto`/`wcdmaOnly` `AT^SYSCFG` codes
   against real hardware/vendor AT reference (currently throw
   `UnsupportedError` by design, not guessed).
3. A real `linux/CMakeLists.txt` build-and-bundle step for `libsimbox`
   (currently dev-mode env-var/monorepo-relative loading only — see
   README's "Native Library Loading (Linux)" section) — flagged as a
   follow-up, not part of this flow's scope.
