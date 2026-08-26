# Requirements: flutter_gsmsip-example

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-08-24

## Problem Statement

`libsFlutter/flutter_gsmsip/example` has drifted from the library it's
supposed to demonstrate:

- It **compiles cleanly** (`flutter analyze` → 0 errors, only lint/
  deprecation infos) but **can't actually exercise the library**:
  `main.dart` is a single-screen dashboard that calls
  `GatewayService.loadConfiguration()` on launch; since no config is ever
  persisted (no setup UI exists), `Start Gateway` always fails with "No
  configuration found." There is no way to enter SIP/SMPP credentials
  through the app.
- Its own `README.md` documents a **fictional API** (`GsmSipBridge`,
  `bridge.sipService`, `bridge.telephonyService`) and a `screens/` folder
  (setup/dashboard/settings/call/sms/logs) that don't exist in the code.
  The real API is `GatewayService`, with the GSM leg sourced from
  `flutter_gsm`'s `ModemRepository` and the SIP leg from
  `SipRepositoryImpl` (`flutter_nmsip`-backed).
- The example is **Android-only** (only an `example/android/` platform
  folder exists), despite `flutter_gsm` having gained a real Linux modem
  driver (`SimboxModemRepository`, libsimbox-backed) and a macOS stub in
  recent flows (`sdd-flutter_gsm-ffi`, `sdd-simbox-app-real-driver`).

This flow brings the example back to a genuinely working, honest
reference implementation of `flutter_gsmsip` — **without modifying the
library itself** (`libsFlutter/flutter_gsmsip/lib/**`), and without
modifying its sibling libraries `flutter_gsm`/`flutter_nmsip`.

### Known per-platform capability ceiling (confirmed by reading the libs)

| Leg | Android | Linux | macOS |
|-----|---------|-------|-------|
| SIP (`flutter_nmsip`) | Real (only platform declared in its pubspec) | **No native impl** | **No native impl** |
| GSM/modem (`flutter_gsm`) | Real | Real (`SimboxModemRepository`, FFI→libsimbox) | Stub only (~90 lines, no real driver) |

Porting SIP/modem drivers to new platforms is out of scope (a multi-week
effort in sibling libraries, not an "example fix"). Anton confirmed
(2026-08-24): build/run the example on all three platforms, but the
README and in-app UI must **honestly surface** these limits rather than
silently failing or overclaiming.

## User Stories

### Primary

**As a** developer integrating `flutter_gsmsip`
**I want** the example's `README.md` to accurately describe the current
`GatewayService`-based API and real screens
**So that** I can learn the actual integration pattern instead of being
misled by stale docs.

**As a** developer
**I want** to run the example, enter SIP/SMPP credentials through a setup
screen, and start/stop the gateway, place a test call, send a test SMS,
and view logs
**So that** I can verify the library actually works end-to-end, not just
that it compiles.

### Secondary

**As a** developer targeting Linux or macOS
**I want** the example to build and run there too, with clear feedback
about what isn't backed by a real driver yet (SIP off-Android, GSM-modem
off-Android/Linux)
**So that** I'm not confused by a silent no-op when I press Start
Gateway.

## Acceptance Criteria

### Must Have

1. **Given** a fresh checkout, **when** running `flutter pub get &&
   flutter analyze` in `example/`, **then** zero analyzer errors (lint/
   info-level notices are acceptable).
2. **Given** the app launched with no saved config, **when** the user
   opens the Setup screen, enters SIP account fields (+ optional SMPP),
   and saves, **then** a `GatewayConfig` is persisted via
   `GatewayService`'s existing `shared_preferences`-backed
   save/loadConfiguration and is reloaded on next launch.
3. **Given** valid saved config on Android, **when** the user presses
   Start Gateway, **then** `GatewayService.initialize()` + `.start()`
   succeed and the dashboard reflects real SIP-connected / modem-
   discovered state via `statusStream`.
4. **Given** the gateway running on Android, **when** the user triggers
   "Make Test Call" / "Send Test SMS", **then** the real
   `GatewayService` methods are invoked and the resulting routing id /
   message id (or failure reason) is shown.
5. **Given** the app running on Linux, **when** the user presses Start
   Gateway, **then** it fails at the SIP-init step and the UI surfaces a
   specific, honest reason ("SIP is not supported on this platform yet")
   rather than a generic error or silent no-op.
6. **Given** the app running on macOS, **when** the user presses Start
   Gateway, **then** the UI communicates that neither the SIP nor the
   GSM-modem leg has a real backend on this platform yet.
7. `example/README.md` is rewritten to document: the real
   `GatewayService`/`ModemRepository`/`SipRepositoryImpl` API (not
   `GsmSipBridge`), the screens actually shipped, the per-platform
   capability table above, actual required permissions, and a
   getting-started flow that has actually been run (pub get / analyze /
   build) rather than assumed.
8. The example builds for **Android, Linux, and macOS** (verified via
   `flutter build` for each platform reachable from this dev machine;
   Android verified at minimum via `flutter analyze` + a Gradle
   assemble if an Android toolchain is available in this environment).
9. Screens cover, at minimum: **Setup** (SIP+SMPP entry/edit), **Dashboard**
   (status + controls — evolves the existing one), **Settings**
   (edit/clear saved config, toggle auto-answer/logging), **Call**
   (active SIP/GSM calls + routings — only actions actually exposed by
   `SipRepositoryImpl`/`GatewayService`), **SMS** (sent/received via
   `SmsService`), **Logs** (tail of `GatewayService.logStream`, clear).
   No screen may reference a method that doesn't exist on the real
   library API — verify against the actual class before writing UI for
   it.
10. `libsFlutter/flutter_gsmsip/lib/**` is untouched by this flow. No
    changes to `flutter_gsm` or `flutter_nmsip`.

### Should Have

- A visible per-platform capability banner/indicator in the app itself
  (not just the README), so the limit in AC #5/#6 is discoverable without
  reading docs.
- Basic widget/unit tests for new screens where trivial (existing
  `example/test/` is currently empty).

### Won't Have (This Iteration)

- No new native platform bindings for SIP (Linux/macOS) or a real
  macOS/Windows modem driver — sibling-library work, separate flow(s).
- No production-grade credential security (dev/demo affordance only).
- No CI pipeline changes for the example.
- No library features invented to make the example prettier — the
  example follows the library, not the other way around.

## Constraints

- **Technical**: Must not modify `libsFlutter/flutter_gsmsip/lib/**`,
  `flutter_gsm/**`, or `flutter_nmsip/**`. Example-only changes
  (`example/**`, including its own `README.md`).
- **Platform**: Android (existing `example/android/`), plus new
  `example/linux/` and `example/macos/` platform scaffolds (currently
  absent — `flutter create --platforms=linux,macos .` equivalent).
- **Dependencies**: Existing `dependency_overrides` (`plugin_platform_
  interface: ^2.1.8`, `flutter_dialer` path override) must be preserved —
  they exist for a documented reason (unpublished-package version
  mismatch across the monorepo).
- **SDK versions**: library (`flutter_gsmsip/pubspec.yaml`) declares
  `sdk: ^3.10.8`; example currently declares `sdk: ^3.8.1`. Needs
  reconciling in Specifications (likely bump example's lower bound to
  match what it actually depends on transitively).

## Open Questions

- [ ] Exact fidelity of the Call screen's actions (answer/end/mute/hold)
  depends on what `SipRepositoryImpl`/`GatewayService` actually expose —
  to be confirmed by reading the code during Specifications, not assumed
  from the old README.
- [ ] Whether `example/test/` gets real coverage or stays a stub —
  resolve during Specifications/Plan.

## References

- `libsFlutter/flutter_gsmsip/lib/flutter_gsmsip.dart` (current public
  API surface)
- `libsFlutter/flutter_gsmsip/lib/src/services/gateway_service.dart`
- `libsFlutter/flutter_gsmsip/example/README.md` (current, stale)
- `flows/flutter_gsmsip/sdd-flutter_gsmsip-interface/_status.md` (prior
  flow that split `ModemDevice`/etc. out into `flutter_gsm`)
- `flows/flutter_gsm/sdd-flutter_gsm-ffi`,
  `flows/simbox-app/sdd-simbox-app-real-driver` (Linux modem driver work)

---

## Approval

- [ ] Reviewed by: Anton
- [ ] Approved on:
- [ ] Notes:
