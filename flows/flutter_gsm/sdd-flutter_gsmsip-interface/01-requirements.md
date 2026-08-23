# Requirements: flutter_gsmsip-interface

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-08-20

## Problem Statement

`flutter_gsmsip` currently only speaks to telephony hardware through Android
(an audio-passthrough "dongle" scheme plus stub Android telecom/AT-command
code). There is no desktop backend. The legacy Linux product
(`legacy/simbox-desktop-v2015`) got its telephony from Asterisk + a custom
channel driver, **chan_svistok** (`legacy/chan_svistok`), which talks to
Huawei UMTS USB dongles over `/dev/ttyUSBx` with AT commands. The app layer
never called Asterisk's manager API — it shelled out to the `asterisk -rx
"dongle ..."` CLI and polled flat state files under `/var/svistok/...`.

We are rebuilding a Linux desktop app (`apps/simbox-app`, Flutter) that needs
the same functional capability — multi-device GSM/UMTS call, SMS, USSD,
device/SIM management — but **without Asterisk**. Asterisk's channel-driver
model, its CLI-command/flat-file "API", and the whole PBX layer are excluded
by design; chan_svistok's AT-command/serial/call-state logic is the reusable
part, and it needs to be re-hosted directly inside `flutter_gsmsip` as a
native (Linux, later Windows/macOS) platform implementation, exposed through
a real, structured, in-process Dart API instead of shell-outs and file polling.

This flow (`sdd-flutter_gsmsip-interface`) covers **only the API/interface
layer**: the platform-interface contract, the entity/repository/service
shape, and the seam a Linux implementation will plug into. It explicitly
does **not** implement the ttyUSB/AT-command driver itself — that is
`sdd-flutter_gsmsip-channel`, sequenced after this flow and after the
`vdd-simbox-app-uiux` UI refactor are both implemented (see Constraints).

## User Stories

### Primary

**As a** simbox-app developer
**I want** a `flutter_gsmsip` platform-interface and service layer that
models GSM/UMTS dongle telephony (calls, SMS, USSD, device/SIM state,
groups/plans, IMEI management) independently of any specific transport
**So that** I can build the Linux ttyUSB/AT-command backend and the new
desktop UI against a stable contract, without either of them depending on
the other's internals, and without Asterisk anywhere in the stack.

### Secondary

**As a** simbox-app developer targeting Windows/macOS later
**I want** the interface layer to have no Linux-specific assumptions baked in
**So that** a Windows (`COM*`) or macOS (`/dev/tty.*`) serial backend can
implement the same contract later without another interface redesign.

**As a** maintainer of the existing Android path
**I want** the Android audio-passthrough "dongle" concept (`DongleType`,
`DongleInterfaceType`) to stay intact and unambiguous
**So that** introducing a serial/AT-command "modem" concept doesn't collide
with or rename the existing Android dongle abstraction.

## Acceptance Criteria

### Must Have

1. **Given** the current single `MethodChannel('flutter_gsmsip')` design
   **When** the interface layer is refactored
   **Then** `FlutterGsmsipPlatform` (the `plugin_platform_interface` contract)
   exposes the full functional surface — modem discovery/state, calls, SMS,
   USSD, raw AT passthrough, power/reset, IMEI/network-mode/group
   management — as abstract methods/streams, not just `getPlatformVersion()`.

2. **Given** `TelephonyService`, `SipService`, `GatewayService` currently call
   ad-hoc `MethodChannel`s directly (bypassing `FlutterGsmsipPlatform`)
   **When** the refactor lands
   **Then** all telephony operations route through `FlutterGsmsipPlatform`,
   so a platform implementation (Android today, Linux later) is the only
   thing that needs to change to support a new OS.

3. **Given** chan_svistok's functional surface (device show/state, `cmd`,
   `sms`, `ussd`, `reset`/`start`/`restart`, `setgroup`, `callwaiting`,
   IMEI change, network/frequency lock, diag mode) and simbox-desktop-v2015's
   `www/` operations (documented in this flow's research)
   **When** the new domain entities/repositories are designed
   **Then** every one of those operations has a corresponding method,
   entity field, or documented deferral in the new interface (deferrals
   listed explicitly, not silently dropped).

4. **Given** the naming collision between the existing Android
   "dongle = audio-passthrough adapter" concept and the new "modem = serial
   AT-command GSM device" concept
   **When** new entities are introduced
   **Then** they use a distinct name (e.g. `Modem`/`ModemDevice`, exact name
   decided in specifications) so `DongleType`/`DongleInterfaceType` remain
   unambiguous and untouched.

5. **Given** chan_svistok's device/call/SMS events are inherently push-style
   (RING, `+CMTI`, disconnect, state transitions) and no `EventChannel`
   exists today
   **When** the interface is specified
   **Then** it defines a stream-based event contract (e.g.
   `Stream<ModemEvent>` covering device attach/detach, registration/signal
   changes, call state, incoming SMS/USSD) that a future Linux
   implementation backs with a real `EventChannel` or FFI callback bridge.

6. **Given** per-device/per-carrier config that lived as loose files in
   simbox-desktop-v2015 (`onlineMax`, 4 `limitMax` buckets, `priority`,
   pacing `alg`, `nabor` USSD-recipe profiles per operator/region)
   **When** the domain layer is specified
   **Then** structured entities exist for group/plan limits and for a
   pluggable "carrier profile" (USSD-code templates + response parsing per
   operator), replacing flat-file config with typed models.

7. **Given** this is an interface-only flow
   **When** implementation happens
   **Then** the Linux platform implementation is a thin, explicitly-stubbed
   placeholder (`UnimplementedError` or TODO-documented) that compiles and
   registers for `linux:` in `pubspec.yaml`, but does **not** contain real
   serial/AT-command logic — that belongs to `sdd-flutter_gsmsip-channel`.

8. **Given** `sdd-complete-refactoring`'s status notes the package currently
   fails to compile (1000+ errors) as of 2026-03-15
   **When** this flow's plan is scoped
   **Then** the plan includes getting `flutter_gsmsip` to a compiling,
   analyzer-clean state as a prerequisite/first task, not an afterthought.

### Should Have

- Deprecate/remove the redundant `gsm_sip_gateway/telephony` ad-hoc channel
  and the orphaned `lib/src/data/services/*` duplicate service files
  identified during research, to leave one clean service layer.
- Document the mapping from chan_svistok CLI verbs → new Dart API methods
  as a table in the specifications phase, for traceability.

### Won't Have (This Iteration)

- Real ttyUSB/AT-command I/O, serial port scanning, PDU SMS
  encoding/decoding, or any chan_svistok-derived C/FFI code — that is
  `sdd-flutter_gsmsip-channel`.
- Windows/macOS platform implementations (interface must not preclude them,
  but they are not built now).
- Any UI work — that is `vdd-simbox-app-uiux`, sequenced after this flow's
  implementation is complete.
- IMEI pool allocation service and firmware flashing (`ttyprog_*`/DIAG
  protocol) — these were external tools/services in the legacy stack;
  interface should leave a seam (method/entity) but not implement them.
- Asterisk compatibility of any kind, including AMI, dialplan, or call-file
  spooling — explicitly excluded per user instruction.

## Constraints

- **Technical**: Must preserve the existing Android platform path (audio
  dongle scheme, `DongleType`/`DongleInterfaceType`) without behavioral
  change; new abstractions must not require Android call sites to change
  semantics, only to route through `FlutterGsmsipPlatform` consistently.
- **Technical**: Federated-plugin shape — introduce `linux:` in
  `pubspec.yaml`'s `flutter.plugin.platforms`, following the same pattern
  Flutter uses for other multi-platform plugins (single package now;
  splitting into `flutter_gsmsip_platform_interface`/`_linux` packages is a
  specifications-phase decision, not decided here).
- **Sequencing**: This flow's implementation must land and compile *before*
  `vdd-simbox-app-uiux` implementation begins (UI refactor consumes this
  API). `sdd-flutter_gsmsip-channel` (real ttyUSB driver) must not be
  created until both this flow and `vdd-simbox-app-uiux` have implemented
  code merged, per explicit user instruction.
  See [[vdd-simbox-app-uiux]] for the dependent UI flow.
- **Platform**: Interface must be transport-agnostic enough to support
  Linux now, Windows/macOS later, without another breaking redesign.
- **Dependencies**: None blocking start of this flow; chan_svistok and
  simbox-desktop-v2015 are read-only references, not build dependencies.

## Open Questions

- [ ] Exact naming for the new "serial AT-command GSM device" entity
      (`Modem`? `SvistokDevice`? `GatewayDevice`?) — avoid collision with
      `Dongle*` (Android audio) and with `GatewayConfig` (SIP gateway).
      Decide in specifications.
- [ ] Should `flutter_gsmsip` split into federated packages
      (`_platform_interface`, `_android`, `_linux`) now, or stay a single
      package with a `linux:` platform entry until `sdd-flutter_gsmsip-channel`
      forces the split? Recommend deciding in specifications after
      evaluating `sdd-complete-refactoring`'s compile-error backlog.
- [ ] Where do carrier "nabor" USSD-recipe profiles live long-term — bundled
      in the plugin, or as app-level configuration data supplied by
      simbox-app? Affects whether `CarrierProfile` is a `flutter_gsmsip`
      entity or an injectable dependency.
- [ ] IMEI pool allocation was an external HTTP service in 2015
      (`simserver:8122`) — is a replacement service in scope for simbox-app,
      or out of scope entirely for now? Affects whether the interface needs
      an `imeiPool` seam at all.

## References

- `legacy/chan_svistok/README.md` — chan_svistok architecture, CLI surface,
  AT/serial specs, 8-state call machine.
- `legacy/simbox-desktop-v2015/www/`, `bin/`, `actions/`, `system/`,
  `config.sh`, `nabor/` — legacy app-to-Asterisk wiring and functional API
  surface (see this flow's research notes for the CLI-shellout/flat-file
  finding).
- `libs/flutter_gsmsip/lib/src/domain/`, `lib/src/services/`,
  `lib/src/data/sources/voice_line/tty_port_source.dart` — existing Clean
  Architecture layering and the stubbed `ITtyPortSource` seam.
- `libs/flutter_gsmsip/flows/sdd-complete-refactoring/_status.md` — known
  compile-error backlog to account for in planning.
- [[vdd-simbox-app-uiux]] — dependent UI refactor flow (top-level
  `flows/vdd-simbox-app-uiux/`).

---

## Approval

- [ ] Reviewed by: Anton Dodonov
- [ ] Approved on:
- [ ] Notes:
