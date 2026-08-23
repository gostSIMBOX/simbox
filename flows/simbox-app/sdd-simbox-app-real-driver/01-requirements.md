# Requirements: simbox-app-real-driver

> Version: 1.0
> Status: APPROVED
> Last Updated: 2026-08-23

## Problem Statement

`apps/simbox-app` (the Flutter desktop SIM-box management UI built by
`vdd-simbox-app-uiux`) is wired entirely against `FakeModemRepository`
— a hardcoded, 3-device test double — because at the time that flow
was built, no real modem driver existed. That gap has since closed:
`flutter_gsm` (which `simbox-app` already depends on via a path
dependency) now has a real Linux implementation
(`LinuxFlutterGsm` → `SimboxModemRepository`, via `dart:ffi` into
`libsimbox`, delivered by `sdd-asterisk-chan-simbox` +
`sdd-flutter_gsm-ffi`). `simbox-app` needs to actually use it.

Beyond the dependency-injection swap itself, real device visibility
depends on chan_dongle's config-file-driven discovery — which
currently has no working example, no override mechanism reachable from
Dart/`simbox-app`, and a fragile hardcoded lookup path (current working
directory, or `/etc/asterisk/`) inherited from chan_dongle's original
Asterisk-hosted design. This needs to become something `simbox-app` can
actually rely on, not just a manual `cd`-and-hope setup step.

## User Stories

### Primary

**As a** simbox-app user with a real ttyUSB GSM modem attached to a
Linux machine
**I want** the app to discover and control that modem through the real
driver
**So that** I can manage SIMs/calls/SMS against actual hardware, not
just the demo dataset `FakeModemRepository` provides

### Secondary

**As a** developer working on `simbox-app` without `libsimbox` built or
without real hardware attached
**I want** the app to start normally and clearly show a "driver
unavailable" / "no devices" state, not crash or silently show fake data
**So that** I can still work on unrelated parts of the UI without a
full hardware setup

**As a** developer setting up `simbox-app` on a real Linux machine for
the first time
**I want** a documented, reliable way to point the app at a
`dongle.conf` describing the attached modem(s)
**So that** I don't have to reverse-engineer chan_dongle's original
Asterisk-era config-path assumptions

## Acceptance Criteria

### Must Have

1. **Given** `apps/simbox-app` is built and run on Linux with
   `libsimbox` present
   **When** the app starts
   **Then** its dependency-injection point (`main.dart`) provides a
   real `ModemRepositoryImpl` (backed by `FlutterGsmPlatform.instance`
   / `LinuxFlutterGsm`), not `FakeModemRepository`

2. **Given** `libsimbox` cannot be loaded (not built, or the resolved
   path doesn't exist)
   **When** the app starts and any screen queries modems
   **Then** the existing `ModemDriverNotAvailableException` handling
   already present in `modem_line_list_controller.dart` /
   `modems_screen.dart` / `sims_screen.dart` continues to work
   unchanged — this flow must not need to invent new error-handling UI

3. **Given** a correctly formatted `dongle.conf` describing at least
   one device, placed wherever this flow's config-loading design says
   it should go
   **When** `simbox_init()` runs chan_dongle's real config-driven
   device population
   **Then** `simbox-app` is *structurally* capable of showing that
   device once real hardware is attached — this flow delivers the
   config-loading path and a validated example config, not a live
   demonstration against real hardware (no Linux host / USB modem is
   available in this development environment; see Constraints)

4. **Given** the existing `apps/simbox-app/test/sims_screen_test.dart`
   (and any other test currently constructing `FakeModemRepository`
   directly)
   **When** this flow's changes land
   **Then** those tests still compile and pass — `FakeModemRepository`
   itself is not deleted (it stays a legitimate test double for widget
   tests), only `main.dart`'s production wiring changes

5. **Given** the config-path resolution question researched for this
   flow (chan_dongle's `ast_config_load("dongle.conf")` resolves to
   CWD-relative or `/etc/asterisk/dongle.conf`, with a dead/unwired
   `simbox_config_t.config_dir` field and no override mechanism
   currently reachable from the adapter layer)
   **When** specifications are drafted
   **Then** they must explicitly decide, with tradeoffs stated: (a)
   wire `config_dir` through the currently-unused field so
   `simbox-app` can pass an absolute, predictable path (touches
   `libsCpp/asterisk_chan_simbox/adapters/src/shim_config.c` — adapter
   layer, not the read-only vendored trees, consistent with
   `sdd-asterisk-chan-simbox`'s established Strangler Fig rules), or
   (b) document and rely on the existing CWD/`/etc/asterisk/`
   resolution as-is. This is this flow's biggest open design question
   and must not be silently assumed.

### Should Have

- A real, validated example `dongle.conf` for `simbox-app` (no working
  example currently exists anywhere in the vendored/adapter tree —
  `libsCpp/asterisk_chan_simbox/tests/` doesn't have one; only
  `asterisk_chan_svistok/chan_svistok/etc/dongle.conf` does, and that's
  read-only reference material, not something `simbox-app` ships).
- A short README/setup note in `apps/simbox-app` (or `flutter_gsm`,
  wherever specifications decide is the right home) covering: where
  `libsimbox` must be built, where `dongle.conf` must live, and what a
  minimal one-device entry looks like — aimed at "first real Linux
  machine setup," not just developers already fluent in this
  monorepo's history.

### Won't Have (This Iteration)

- Windows/macOS real-driver wiring (still stubbed platforms — out of
  scope, matches `flutter_gsm`'s own current scope).
- Any UI for *editing* `dongle.conf` from within `simbox-app` (config
  authoring stays a manual/external step this iteration).
- Real end-to-end verification against actual USB hardware — this
  development environment has neither a Linux host nor attached
  modems. Verification here is structural (analyzer, existing/adapted
  widget tests, a config-parsing sanity check) with real hardware
  verification explicitly flagged as a follow-up for a real Linux
  host, the same pattern already established by
  `sdd-asterisk-chan-simbox`'s Task 5.9.
- Building/wiring real USB discovery UI (device pairing wizards, etc.)
  beyond what `modems_screen.dart`/`sims_screen.dart` already have.
- Reopening `vdd-simbox-app-uiux`'s still-blocked font-asset issue —
  unrelated to this flow, left for Anton's separate decision.

## Constraints

- **Technical**: Must not modify the read-only vendored trees
  (`asterisk_chan_svistok/`, `asterisk_chan_dongle/`) — only
  `libsCpp/asterisk_chan_simbox/adapters/`/`src/` (if AC #5 chooses
  option (a)) and `apps/simbox-app/` are fair game, matching the rule
  already established and enforced throughout `sdd-asterisk-chan-simbox`.
- **Platform**: Linux only, matching `flutter_gsm`'s current real-driver
  scope.
- **Environment**: No real Linux host or USB GSM hardware is available
  in this development environment (confirmed: this is a macOS
  machine). Every acceptance criterion above is written to be
  verifiable without either, with real-hardware verification
  explicitly deferred.
- **Dependencies**: Requires `sdd-flutter_gsm-ffi` (complete) and
  `sdd-asterisk-chan-simbox` (complete apart from its own
  real-Linux-host follow-ups, which don't block this flow).

## Open Questions

- [ ] AC #5's config-path design decision (wire `config_dir` through
  vs. document the existing hardcoded resolution) — to be resolved in
  specifications, not left open past that phase.
- [ ] Where should the example `dongle.conf`/setup README physically
  live — `apps/simbox-app/`, `libsFlutter/flutter_gsm/`, or
  `libsCpp/asterisk_chan_simbox/`? Leaning `apps/simbox-app/` since
  it's the concrete consumer, but worth confirming in specifications.
- [ ] Does `simbox-app`'s current `linux/CMakeLists.txt` (stock
  Flutter-generated, no `libsimbox` build step) need anything added in
  this flow, or is "developer manually builds `libsimbox` first,
  `flutter_gsm`'s existing env-var/monorepo-relative loader finds it"
  sufficient for this iteration? Leaning toward the latter (matches
  `flutter_gsm`'s own documented dev-mode-only loading strategy) but
  flagging explicitly rather than assuming.

## References

- `libsFlutter/flutter_gsm/README.md` — "Native Library Loading
  (Linux)" section (env var / candidate path resolution `libsimbox`
  already uses).
- `flows/sdd-flutter_gsm-ffi/` — delivered the real `LinuxFlutterGsm`/
  `SimboxModemRepository` this flow wires in.
- `flows/sdd-asterisk-chan-simbox/` — delivered `libsimbox` itself and
  established the read-only-vendored-tree / adapters-are-fair-game
  rule this flow's Constraints section reaffirms.
- `flows/vdd-simbox-app-uiux/` — built the UI/screens this flow wires
  real data into; currently blocked on an unrelated font-asset
  decision (see Won't Have).
- `apps/simbox-app/lib/state/fake_modem_repository.dart`,
  `apps/simbox-app/lib/main.dart` — current fake wiring this flow
  replaces.
- `libsCpp/asterisk_chan_simbox/asterisk_chan_svistok/chan_svistok/etc/dongle.conf`
  — read-only reference config format (not itself shippable, per
  Acceptance Criteria's "Should Have").

---

## Approval

- [x] Reviewed by: Anton
- [x] Approved on: 2026-08-23
- [x] Notes: Approved as drafted, including scope (DI swap + discovery/
      config setup) and no-fallback-to-fake decision from the
      clarifying questions.
