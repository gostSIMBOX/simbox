# Status: sdd-flutter_gsmsip-interface

## Current Phase

IMPLEMENTATION

## Phase Status

APPROVED

## Last Updated

2026-08-23 by Claude (added a specifications addendum — not reopening
approved specs — flagging a new SIM-inventory-independent-of-modem
requirement from `vdd-simbox-app-uiux`)

## Blockers

- None. Anton approved the implementation log, including the Tasks 9/10
  deviation and the sip_service.dart near-miss, on 2026-08-20.
- Soft follow-up (non-blocking): no `flutter build linux` smoke test run
  yet in this environment (no Linux desktop build target available here).
  Worth running in a Linux-capable environment alongside
  `flows/flutter_gsm/sdd-flutter_gsm-ffi`/`flows/simbox-app/sdd-simbox-
  app-real-driver` (**2026-08-24 naming note**: `sdd-flutter_gsmsip-
  channel`, step 3 of the sequence below, was never actually created —
  those two flows fulfill its goal instead; confirmed with Anton).
- **New follow-up (2026-08-23, not blocking this flow's own APPROVED
  status)**: `vdd-simbox-app-uiux`'s "Каналы" redesign needs `ModemDevice`
  to represent SIM cards independent of a modem (a "not seated in any
  device" state), which doesn't exist today — `ModemDevice` models one
  modem+SIM unit, no `SimCard`-independent-of-modem concept. Anton's
  requirement recorded verbatim in `02-specifications.md`'s new
  Addendum section. Real scope (likely a new entity + native SIM-
  inventory/tray support that `libsimbox`/chan_dongle also don't have
  today) — needs its own dedicated flow/amendment round to design
  properly, not guessed here. `vdd-simbox-app-uiux` ships its "По SIM,
  все" mode showing only seated SIMs until this lands.

## Progress

- [x] Requirements drafted
- [x] Requirements approved (2026-08-20)
- [x] Specifications drafted
- [x] Specifications approved (2026-08-20)
- [x] Plan drafted
- [x] Plan approved (2026-08-20)
- [x] Implementation started
- [x] Implementation complete (12/14 tasks; 2 dropped as architecturally
      invalid — see Blockers/implementation log)

## Context Notes

Key decisions and context for resuming:

- This is step 1 of a 3-flow sequence requested by Anton in one command:
  (1) this flow — flutter_gsmsip API/interface for Linux telephony without
  Asterisk, modeled on legacy/simbox-desktop-v2015 + legacy/chan_svistok,
  (2) `vdd-simbox-app-uiux` (top-level `flows/vdd-simbox-app-uiux/`) — full
  UI refactor based on `design/simbox-app-maket-v2026`, sequenced to begin
  implementation only after this flow's implementation is complete,
  (3) `sdd-flutter_gsmsip-channel` — real ttyUSB/AT-command modem driver
  implementation, to be created only after both (1) and (2) have
  implemented code merged. **2026-08-24 naming note**: this flow name
  was never actually created — the goal it describes was instead
  fulfilled by `flows/flutter_gsm/sdd-flutter_gsm-ffi` (FFI binding to
  `libsimbox`) and `flows/simbox-app/sdd-simbox-app-real-driver`
  (end-to-end wiring), both complete. Confirmed with Anton; no new flow
  needed.
- Research completed via 3 parallel subagents before drafting requirements:
  - `flutter_gsmsip` current architecture: single non-federated package,
    Android-only (`pubspec.yaml` has no `linux:` platform entry).
    `FlutterGsmsipPlatform` (plugin_platform_interface) only exposes
    `getPlatformVersion()` — real telephony calls bypass it via ad-hoc
    `MethodChannel`s in `TelephonyService`/`SipService`. "Dongle"
    (`DongleType`/`DongleInterfaceType`) currently means an Android
    audio-passthrough adapter, NOT a serial modem — naming collision risk
    flagged as an open question. `VoiceLineMethod.ttyPort` and
    `ITtyPortSource`/`TtyPortSource` already exist as a 100%-stubbed seam
    closest to what chan_svistok needs. No EventChannel exists anywhere.
    `sdd-complete-refactoring` status notes the package fails to compile
    (1000+ errors) as of 2026-03-15 — must be accounted for in the plan.
  - `simbox-desktop-v2015` → Asterisk/chan_svistok wiring: AMI is disabled;
    the app never used a socket API. It shelled out to
    `asterisk -rx "dongle <subcmd>"` (chan_svistok's CLI) and polled flat
    state files under `/var/svistok/...`. Outgoing calls used the Asterisk
    call-file spooler. Functional surface (from `www/simbox/*.php`): SMS,
    USSD, raw AT passthrough, PIN ops, power/reset, network/frequency
    lock/unlock, IMEI change (via external pool server) + blacklist,
    diag-mode/firmware prep, USB hub power-cycling, per-plan/group
    limits+pacing, per-carrier "nabor" USSD-recipe profiles.
  - `design/simbox-app-maket-v2026`: real interactive `.dc.html` prototype
    (no JSON manifest — screens must be read by opening the HTML files),
    responsive across phone/iPad/desktop breakpoints. Sections identified:
    Симки (SIMs table), Модемы (modems/hub), Звонки (calls), СМС,
    Настройки, network/diagnostics console, engineering vs normal mode.
    The `_ds` folder is an unrelated shared VPN-app design system — don't
    use its component names for Simbox screens.
- Open naming decision deferred to specifications: new serial-modem entity
  name must not collide with existing `Dongle*` (Android) or `GatewayConfig`
  (SIP).

- Specifications resolved the 4 open questions from requirements: new
  entity prefix is `Modem*` (not `Dongle*`, not `Gateway*`); plugin stays a
  **single package** with a new `linux:` pubspec entry (no federated-package
  split yet, to avoid compounding `sdd-complete-refactoring`'s compile
  backlog); `CarrierProfile`/`CarrierProfileRegistry` is an injectable
  in-plugin entity; IMEI pool sourcing is explicitly out of scope (no seam
  added, `changeImei` just takes a known IMEI).
- Specifications include a full chan_svistok-CLI-to-new-API mapping table,
  with explicit deferrals (call-waiting, frequency-lock granularity, USB
  hub power control, firmware flashing) rather than silent omission.

- **Corrected a stale assumption during planning**: ran `dart analyze`
  directly instead of trusting `sdd-complete-refactoring`'s 2026-03-15
  "1000+ errors" claim. Reality: 1084 of 1086 errors are inside `legacy/`,
  which is a **separate Dart package** (`legacy/pubspec.yaml` → name
  `flutter_gsm_sip_gateway`, unrelated prior codebase) that `dart analyze`
  walks into only because it isn't excluded. The real `flutter_gsmsip`
  package has 2 trivial errors (a stale default test file). Requirements
  AC #8's "compile-clean-first" prerequisite is now Task 1 in the plan (~15
  min), not a multi-day blocker.
- Plan also refines one spec detail: Android's `MethodChannelFlutterGsmsip`
  does NOT get new native Kotlin code for modem methods (ttyUSB/AT is a
  Linux-only concept) — it returns empty/`UnsupportedError` for modem
  methods, keeping Android's existing audio-dongle+SIP path untouched.
- Linux registration uses Flutter's `dartPluginClass` (pure-Dart plugin
  registration, no CMake/native scaffold) rather than a native plugin —
  sets up `sdd-flutter_gsmsip-channel` to add `dart:ffi` bindings directly
  without touching plugin registration.

- New public API surface now shipping in `libs/flutter_gsmsip`:
  `ModemDevice`, `ModemCall`, `ModemEvent` (+ 8 subtypes), `CarrierProfile`
  (+ `CarrierProfileRegistry`), `ModemGroupConfig`, `ModemRepository`
  (+ `ModemRepositoryImpl`), `AtCommandResult`, `ModemState`,
  `NetworkMode`, `RestartMode`, `RegistrationState`, `PacingAlgorithm`,
  and the modem-exceptions hierarchy — all exported from
  `flutter_gsmsip.dart`. `FlutterGsmsipPlatform` carries the full modem
  API with default throw-bodies; `LinuxFlutterGsmsip` (new,
  `dartPluginClass`-registered, no native scaffold) stubs every modem
  method; Android's `MethodChannelFlutterGsmsip` returns empty/
  `UnsupportedError` for modem methods, unchanged otherwise.
- `TelephonyService`/`GatewayService` (Android's real SIP↔GSM bridge) are
  untouched — confirmed out of scope for this flow after reading the
  actual code (see implementation log's Deviations section).
- Caught and reverted a real near-miss: almost deleted
  `lib/src/data/services/sip_service.dart` as "orphaned cleanup" — it's
  actually the live dependency behind the exported `SipRepositoryImpl`
  via a relative import my earlier grep-based verification missed.
  Restored via `git checkout --`.

## Next Actions

**Flow complete** (2026-08-20). SDD has no separate DOCUMENTATION phase
(unlike VDD) — implementation approval is the terminal state.

1. `vdd-simbox-app-uiux`'s IMPLEMENTATION phase is now unblocked per its
   gating constraint — started 2026-08-20.
2. Outstanding, not part of this flow: run a `flutter build linux` smoke
   test in a Linux-capable environment; flag the confirmed
   `SipService`/`GatewayService` duplicate-class tech debt to
   `sdd-complete-refactoring` (or a fresh flow) when convenient.
