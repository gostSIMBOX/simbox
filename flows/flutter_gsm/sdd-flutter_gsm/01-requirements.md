# Requirements: flutter_gsm

> Version: 1.0
> Status: APPROVED
> Last Updated: 2026-08-21

## Problem Statement

`libsFlutter/flutter_gsmsip` currently conflates two distinct
responsibilities in one package: (a) raw GSM/UMTS hardware access — modem
discovery, calls, SMS, USSD, AT commands, cross-platform — and (b)
SIP↔GSM voice-gateway bridging (bidirectional call routing between a SIP
account and a GSM line, SMPP SMS gateway). This flow (built on top of
`sdd-flutter_gsmsip-interface`, which added the GSM/modem abstractions
into `flutter_gsmsip` directly) splits them: Anton copied
`flutter_gsmsip` to a new package, `libsFlutter/flutter_gsm`
(filesystem copy done outside this flow, still carrying `flutter_gsmsip`'s
bundle identity — renaming is part of this flow's scope), which will own
the GSM stack abstraction. `flutter_gsmsip` becomes a thin bridging layer
built on top of `flutter_gsm`.

**Why this matters**: `flutter_gsm` needs to be independently reusable —
any app that just needs "talk to a GSM modem" (not necessarily bridging to
SIP) should be able to depend on it alone. The current mixing makes that
impossible and makes `flutter_gsmsip` harder to reason about.

### Pre-existing, stalled prior art (context, not a blocker)

`flutter_gsmsip/flows/sdd-split-lib-and-example/` is a **different, older,
stalled** flow (last touched 2026-03-15, stuck at Plan phase with ~180
unresolved import errors) about separating the plugin's *library code from
its example app*— not about carving GSM out from SIP-bridging. Different
axis, same package. Worth knowing it exists (it's evidence this codebase
has unfinished-refactor debt as a pattern), but this flow doesn't need to
resolve it and shouldn't be confused with it.

### Redundancy findings that reshape scope (from pre-requirements research)

Research into the now-reorganized `libsFlutter`/`libsAndroid`/
`libsReactNative` ecosystem surfaced that several things `flutter_gsmsip`
currently reimplements **already exist as separate, purpose-built
packages**:

- **`flutter_nmsip`** — a real PJSIP-based SIP client, built on
  `libsAndroid/sip2-android-core` (a proper native PJSIP core shared
  across React Native/Flutter/native Android). `flutter_gsmsip`'s own
  `lib/src/services/sip_service.dart` is very likely duplicate/inferior
  PJSIP glue.
- **`flutter_dialer`** — Android dialer-replacement (`InCallService`,
  `MANAGE_OWN_CALLS`), the direct Flutter-generation successor of
  `react-native-replace-dialer` (confirmed via matching
  `isDefaultDialer`/`setDefaultDialer` method names).
- **`flutter_tele`** — Android telecom/`InCallService` call control
  (answer/hangup/hold/mute/speaker), depends on `flutter_dialer`, the
  direct successor of `react-native-tele`.
- `flutter_gsmsip`'s `telephony_service.dart` (`MethodChannel
  ('gsm_sip_gateway/telephony')`) does **not** trace back to the RN
  lineage — it's a later, Dart-side-only invention, not battle-tested
  legacy logic. Its sibling `gsm_sip_gateway/headless` channel *does*
  trace to `react-native-headless` (exact method-name match:
  `startService`/`stopService`/`toForeground`/`toBackground`), and
  `flutter_gsmsip/dialer` traces to `react-native-replace-dialer`.

**Implication for this flow**: `flutter_gsm`'s Android implementation
should be built by **depending on `flutter_dialer` + `flutter_tele`**
(already-Flutter, already-modern) rather than re-porting RN code or
inventing new telecom glue — this is the Android equivalent of "Linux
depends on chan_svistok-derived AT-command logic." The RN packages
(`react-native-replace-dialer`, `react-native-headless`, `react-native-
tele`) remain useful as *historical reference* for what capabilities are
achievable, especially the Magisk/root finding below, but are not meant to
be re-ported directly since Flutter already has successors.

### Native ttyUSB driver work — carved out to its own flow

The chan_svistok/chan_dongle/Asterisk-compatibility-shim investigation
that used to live in this section grew into its own substantial body of
work and was **moved to a dedicated flow**:
`libsCpp/asterisk_chan_simbox/flows/sdd-asterisk-chan-simbox/`. That flow
owns: the real state of `libsCpp/asterisk_chan_simbox/asterisk_chan_svistok`
(still Asterisk-coupled, 115 `ast_*` functions/~15 types counted),
the Strangler Fig / Asterisk-compatibility-shim strategy (module source
stays unmodified; a new shim in `adapters/`/`src/` lets it run without
real Asterisk), the three discovery-implementation generations, the
`programmator/` (Huawei DIAG-mode firmware flashing/recovery) and
`reader/` (ttyUSB SIM readers, APDU, no radio — needs its own
`SimReaderDevice`-shaped domain entity) components, the two read-only
upstream chan_dongle reference forks (`asterisk-chan-dongle-by-wdoekes`,
`asterisk-chan-dongle-by-pulpoff`), and OS-portability macro layering
(Linux/Windows/macOS/Android/OpenWRT).

**This flow's remaining relationship to that one**: `flutter_gsm`'s
platform-interface contract is designed to be FFI-bindable to whatever C
API surface `sdd-asterisk-chan-simbox` eventually exposes, but this flow
does not do that native work itself — it ships stubs on the native/desktop
side (matching `sdd-flutter_gsmsip-interface`'s original precedent) until
that flow's output is ready to bind against. See that flow's requirements
for the full detail; don't duplicate it here.

### Critical operational finding — same git remote

`libsFlutter/flutter_gsm`'s `.git` was carried over from the filesystem
copy and **still points at `flutter_gsmsip`'s real GitLab remote**
(`git@gitlab.com:GOSTsimbox/GOSTsimbox_androidgateway.git`). Any commit +
push from `flutter_gsm` before this is fixed would land in the wrong
repository. **Must be repointed or detached before any git operation
beyond local commits in this flow** — flagged as a Must-Have, not an
afterthought.

## User Stories

### Primary

**As a** simbox-app/flutter_gsmsip developer
**I want** raw GSM/UMTS hardware access (modem discovery, calls, SMS,
USSD, AT commands) in its own `flutter_gsm` package, cross-platform
(Linux, Windows, macOS via serial/AT-command modems; Android via native
telephony)
**So that** any app needing GSM hardware access can depend on it without
pulling in SIP/SMPP bridging logic, and `flutter_gsmsip` can be a thin,
legible orchestrator instead of a monolith.

**As a** simbox-app/flutter_gsmsip developer
**I want** `flutter_gsmsip` to depend on `flutter_gsm` (GSM side) and
`flutter_nmsip` (SIP side, PJSIP) for its two "legs," implementing only
the bridging/routing logic itself
**So that** the SIP and GSM implementations aren't duplicated across
packages and each can evolve independently.

### Secondary

**As a** developer targeting Windows/macOS later (not yet built, per
`sdd-flutter_gsmsip-interface`'s scope)
**I want** `flutter_gsm`'s platform-interface to have no Linux-specific
assumptions baked in
**So that** Windows (`COM*`) and macOS (`/dev/tty.*`) serial backends can
be added without another interface redesign — this constraint carries
over unchanged from the prior flow.

**As a** developer inspecting the Android story
**I want** `flutter_gsm`'s Android implementation to route through
`flutter_dialer`/`flutter_tele` rather than reinvent telecom glue
**So that** the already-working, already-Flutter dialer-replacement/
InCallService logic isn't duplicated a third time (RN → ad-hoc Dart →
this).

## Acceptance Criteria

### Must Have

1. **Given** `libsFlutter/flutter_gsm`'s current raw-copy state (pubspec
   `name: flutter_gsmsip`, Android package `org.telon.flutter_gsmsip`,
   class `FlutterGsmsipPlugin`, git remote pointing at
   `GOSTsimbox_androidgateway.git`)
   **When** this flow's implementation lands
   **Then** every bundle-identity string is renamed to `flutter_gsm`
   (pubspec name/description, Dart file names and class names
   `FlutterGsm`/`FlutterGsmPlatform`/`MethodChannelFlutterGsm`, Android
   Gradle module + `AndroidManifest.xml` + Kotlin package
   `org.telon.flutter_gsm` + class `FlutterGsmPlugin`, test imports,
   README, `example/` app), and the git remote is repointed/detached
   (exact resolution — new remote vs. no remote — is an Open Question
   below).

2. **Given** the Modem/GSM domain work from `sdd-flutter_gsmsip-interface`
   (`ModemDevice`, `ModemCall`, `ModemEvent`, `ModemRepository`,
   `CarrierProfile`, `ModemGroupConfig`, the extended
   `FlutterGsmsipPlatform` modem API, `LinuxFlutterGsmsip`) already
   present in `flutter_gsm`'s copied `lib/`
   **When** this flow scopes what stays vs. moves
   **Then** all of it stays in `flutter_gsm` (renamed
   `FlutterGsm`/`FlutterGsmPlatform` etc.) as the package's core API —
   this is the flow's foundation, not new work, but it needs
   specification-phase review against this flow's improved architecture
   (see "better to improve upon it" in Anton's brief — Open Questions
   below list candidate improvements).

3. **Given** `flutter_gsmsip`'s current embedded `sip_service.dart`,
   `gateway_service.dart`, `telephony_service.dart`, `smpp_service.dart`,
   `sms_service.dart` (and their `lib/src/data/services/` duplicates)
   **When** the split lands
   **Then** `flutter_gsmsip` no longer embeds its own PJSIP/telephony
   implementations — it depends on `flutter_gsm` for the GSM leg and
   `flutter_nmsip` for the SIP leg, keeping only bridging/routing logic
   (`GatewayService`'s `CallRouting` orchestration, reshaped to compose
   the two dependencies rather than own both legs).

4. **Given** cross-platform scope explicitly requested (Linux, Windows,
   macOS, Android, and OpenWRT), and that the native ttyUSB driver work
   now lives in `sdd-asterisk-chan-simbox`
   **When** `flutter_gsm`'s platform coverage is specified
   **Then**: the platform-interface contract is designed to be
   FFI-bindable to whatever C API `sdd-asterisk-chan-simbox` eventually
   exposes, but this flow's *implementation* ships stubs on Linux/
   Windows/macOS/OpenWRT (matching `sdd-flutter_gsmsip-interface`'s
   original precedent) until that flow's output is ready to integrate;
   Android's implementation wraps `flutter_dialer` + `flutter_tele`
   rather than reimplementing telecom glue (this one *is* real
   implementation, not a stub, since those dependencies already exist
   and work). OpenWRT is understood as embedded Linux — a cross-compile
   target for `sdd-asterisk-chan-simbox`'s native core, not a separate
   Flutter UI platform the way Windows/macOS/Android are (Flutter itself
   doesn't run on OpenWRT devices); this flow's own scope re: OpenWRT is
   limited to not designing the contract in a way that would preclude it.

5. **Given** `simbox-app`'s existing dependency on `flutter_gsmsip`
   (`ModemRepository`, `ModemDevice`, etc. — built across `vdd-simbox-app-
   uiux`'s implementation)
   **When** the split lands
   **Then** `simbox-app`'s import paths/dependency graph are updated to
   depend on `flutter_gsm` directly for Modem-layer types (and
   `flutter_gsmsip` only if/where it still needs bridging-specific
   types) — this must not silently break the UI work already merged.

### Should Have

- A short ADR (or a section in specifications) documenting the
  `flutter_gsm` / `flutter_gsmsip` / `flutter_nmsip` / `flutter_dialer` /
  `flutter_tele` dependency graph, since this is exactly the kind of
  decision that's easy to re-litigate or duplicate again later (as
  evidenced by `sdd-split-lib-and-example`'s stall and the
  `SipService`/`GatewayService` duplicate-class debt found in the prior
  flow).
- Delete or clearly quarantine `flutter_gsm`'s inherited `legacy/`
  subfolder (a full old-generation app copy, already excluded from
  `dart analyze` via `analysis_options.yaml`) if it has no bearing on the
  GSM-abstraction scope — confirm in specifications rather than assuming.
- (Native ttyUSB driver deliverables — file map, `ast_*` symbol
  inventory, discovery-generation choice — now belong to
  `sdd-asterisk-chan-simbox`, not this flow.)

### Won't Have (This Iteration)

- Publishing either package to pub.dev.
- Resolving `sdd-split-lib-and-example`'s stalled lib/example split — out
  of scope, different flow, different axis.
- Windows/macOS *real* driver implementations (stubs/interface-parity
  only, mirroring the Linux precedent) unless specifications decide
  otherwise.
- Rewriting `flutter_nmsip`, `flutter_dialer`, or `flutter_tele`
  themselves — this flow *consumes* them, doesn't modify them, unless a
  genuine gap is found (flag as an addendum to those packages, don't
  silently patch them here).
- UI work in `simbox-app` beyond import-path fixes needed for the split
  (`vdd-simbox-app-uiux` owns UI; this flow only touches its dependency
  graph, not its screens).

## Constraints

- **Technical**: `flutter_gsm`'s platform-interface contract is the
  source of truth `flutter_gsmsip` builds on — changes to it are a
  breaking change for `flutter_gsmsip`'s dependency, so the two packages'
  work should be sequenced (rename + stabilize `flutter_gsm` first, then
  refactor `flutter_gsmsip` against it), not developed in lockstep blind.
- **Operational**: git remote repoint/detach (see Critical Operational
  Finding above) must happen before any push from `flutter_gsm` — this is
  a safety issue, not a style preference.
- **Dependencies**: `flutter_gsmsip`'s refactor depends on `flutter_gsm`
  reaching a stable, renamed, compiling state first. `simbox-app`'s
  import fixes depend on both. `flutter_gsm`'s native/desktop platform
  implementations depend on `sdd-asterisk-chan-simbox`'s output for real
  (non-stub) behavior, but that dependency doesn't block this flow's own
  completion — stubs are an accepted interim state, same pattern as
  `sdd-flutter_gsmsip-interface`.
- **Platform**: Must not regress the audio-passthrough Dongle scheme.
  The existing embedded SIP path is *intentionally* superseded by
  depending on `flutter_nmsip` (decided above) — this is an explicit,
  approved architectural change, not something to preserve for
  compatibility's sake.

## Decided (previously Open Questions)

- [x] **DECIDED — thin-orchestrator architecture confirmed by Anton
      (2026-08-21)**: `flutter_gsmsip` becomes `CallRouting`/
      `GatewayService` orchestration only, consuming `flutter_gsm` for
      the GSM leg and `flutter_nmsip` for the SIP leg — not a partial
      rename, a real architectural refactor. This directly extends to:
      (a) `flutter_gsmsip`'s embedded `sip_service.dart` is replaced by
      wiring against `flutter_nmsip` (still needs the capability-gap
      check below before deletion, but the *direction* is decided, not
      open); (b) whether `ModemRepository`'s Android implementation
      should route through `flutter_dialer`/`flutter_tele` (rather than
      the `UnsupportedError`-stub approach `sdd-flutter_gsmsip-interface`
      used, which assumed Android has no GSM access worth modeling) is
      now essentially answered too — Android *does* have real GSM access
      via the phone's own radio, and now that `flutter_dialer`/
      `flutter_tele` exist as dependencies, `flutter_gsm`'s
      `ModemRepository` should back Android with them instead of
      stubbing. Confirm this specific extension in specifications since
      it's a step beyond the literal question asked, but it follows
      directly from the decided direction.

## Decided (previously Open Questions, resolved 2026-08-21)

- [x] **Git remote**: Anton removed `flutter_gsm`'s `.git` remote
      directly; a dedicated remote will be added later (by Anton, not
      this flow). No action needed here beyond not assuming a remote
      exists.
- [x] **`flutter_gsmsip`'s embedded `sip_service.dart`/
      `gateway_service.dart` fate**: recommended default confirmed —
      capability-gap check first in specifications (does `flutter_nmsip`
      cover every method `flutter_gsmsip` currently calls?), delete only
      what's proven redundant.
- [x] **Windows/macOS scaffold**: recommended default confirmed — mirror
      Linux's `dartPluginClass` pure-Dart registration, no native CMake
      scaffold yet.
- [x] **Visual/design scope**: recommended default confirmed — this flow
      stays backend-only.

**Session note**: Anton is handling all git commits himself across every
flow this session — this flow (and any other work in this session)
should not run `git add`/`commit`/`push` unless explicitly asked.

## References

- `libsFlutter/flutter_gsmsip/flows/sdd-flutter_gsmsip-interface/` — the
  flow this one builds on and is asked to improve upon.
- `libsFlutter/flutter_gsmsip/flows/sdd-split-lib-and-example/` — related
  but distinct stalled prior art (lib/example split, not GSM/SIP split).
- `libsFlutter/{flutter_nmsip,flutter_dialer,flutter_tele,flutter_smsussd}`
  — sibling packages this flow's architecture depends on/must not
  duplicate.
- `libsAndroid/sip2-android-core` — native PJSIP core behind
  `flutter_nmsip`.
- `libsCpp/asterisk_chan_simbox/flows/sdd-asterisk-chan-simbox/` — owns
  all native ttyUSB/chan_svistok/chan_dongle/Asterisk-shim work; this
  flow only consumes its eventual C API via FFI.
- `legacy/react-native-gsm-sip-gateway-v2015`,
  `libsReactNative/{react-native-replace-dialer,react-native-headless,
  react-native-tele}` — Android reference lineage; confirmed ancestors of
  `flutter_dialer`/`flutter_tele`, which are the actual dependency target
  (not these RN packages directly). Magisk/root requirement for
  privileged permissions (`MODIFY_PHONE_STATE`, raw audio capture) noted
  as a real constraint on any *deeper* Android telephony control beyond
  what `InCallService`/default-dialer allows.
- `design/simbox-app-maket-v2026`, `design/nativemind-designsystem-v1.8`
  — visual references, scope TBD per Open Questions.

---

## Approval

- [x] Reviewed by: Anton Dodonov
- [x] Approved on: 2026-08-21
- [x] Notes: Approved with the 4 recommended defaults confirmed as-is.
      Git remote handled directly by Anton (removed, will re-add later).
      Anton is committing everywhere himself this session — no commit
      actions from Claude unless explicitly asked.
