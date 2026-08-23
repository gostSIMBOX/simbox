# Specifications: flutter_gsm

> Version: 1.0
> Status: APPROVED
> Last Updated: 2026-08-21
> Requirements: [01-requirements.md](01-requirements.md) — APPROVED 2026-08-21

## 1. Rename Checklist (`flutter_gsmsip` → `flutter_gsm`)

Catalogued from the live `libsFlutter/flutter_gsm` tree (raw copy, not yet
renamed). Every occurrence below must change; nothing outside this list
needs to.

| File(s) | Change |
|---|---|
| `pubspec.yaml` | `name: flutter_gsmsip` → `flutter_gsm`; update `description` |
| `README.md` | Title/body references |
| `lib/flutter_gsmsip.dart` | Rename file → `flutter_gsm.dart`; barrel exports unchanged in content |
| `lib/flutter_gsmsip_platform_interface.dart` | Rename file → `flutter_gsm_platform_interface.dart`; class `FlutterGsmsipPlatform` → `FlutterGsmPlatform` |
| `lib/flutter_gsmsip_method_channel.dart` | Rename file → `flutter_gsm_method_channel.dart`; class `MethodChannelFlutterGsmsip` → `MethodChannelFlutterGsm`; channel name `'flutter_gsmsip'` → `'flutter_gsm'` |
| `lib/src/linux/linux_flutter_gsmsip.dart` | Rename file → `linux_flutter_gsm.dart`; class `LinuxFlutterGsmsip` → `LinuxFlutterGsm` |
| `lib/src/data/repositories/modem_repository_impl.dart` | Internal imports of the above renamed files |
| `lib/src/domain/exceptions/modem_exceptions.dart`, `lib/src/domain/entities/carrier_profile.dart` | No rename needed (already `flutter_gsm`-neutral names) — just verify imports |
| `lib/src/services/gsm_sip_bridge.dart` | **Delete** — this is bridging-logic naming (`gsm_sip_bridge`), belongs in `flutter_gsmsip`, not `flutter_gsm`; confirm nothing in `flutter_gsm`'s own scope calls it before deleting (Task in plan) |
| `test/flutter_gsmsip_test.dart`, `test/flutter_gsmsip_method_channel_test.dart`, `test/linux_flutter_gsmsip_test.dart` | Rename files; update `package:flutter_gsmsip/...` imports → `package:flutter_gsm/...` |
| `test/modem_entities_test.dart`, `test/modem_repository_impl_test.dart` | Update imports only, no rename needed |
| `android/build.gradle` | Gradle module identity |
| `android/settings.gradle` | Module name |
| `android/src/main/AndroidManifest.xml` | `package="org.telon.flutter_gsmsip"` → `org.telon.flutter_gsm` |
| `android/src/main/kotlin/org/telon/flutter_gsmsip/*.kt` (7 files: `FlutterGsmsipPlugin.kt`, `MainActivity.kt`, `BootUpReceiver.kt`, `GatewayDialerModule.kt`, `HeadlessModule.kt`, `HeadlessService.kt`, `HeadlessEventService.kt`) | Move to `org/telon/flutter_gsm/`; class `FlutterGsmsipPlugin` → `FlutterGsmPlugin`. **Open item**: `GatewayDialerModule`/`HeadlessModule`/`HeadlessService`/`HeadlessEventService` are dialer-replacement/headless-service glue — per requirements' redundancy findings, these likely duplicate `flutter_dialer`(dialer)/`react-native-headless`-lineage functionality. Decide in plan: delete in favor of a `flutter_dialer` dependency, or keep as `flutter_gsm`'s own (they're GSM-side concerns, arguably legitimate to keep here rather than push to `flutter_gsmsip`) — **recommend keeping them in `flutter_gsm`** since headless/dialer-replacement is about "keeping the GSM radio session alive," a GSM-side concern, not a SIP-bridging one; just rename, don't delete, unless plan-phase investigation finds they're truly dead code. |
| `android/src/test/kotlin/org/telon/flutter_gsmsip/FlutterGsmsipPluginTest.kt` | Move + rename to match above |
| `example/pubspec.yaml`, `example/pubspec.lock` | Dependency name/path |
| `example/README.md`, `example/lib/main.dart` | References |
| `example/android/app/build.gradle.kts` | Applied plugin reference |
| No `ios/` plugin dir exists | Nothing to rename there — iOS isn't implemented (unchanged from before) |
| `flows/` (all ~90 copied flow dirs, including `sdd-flutter_gsmsip-interface`, `sdd-split-lib-and-example`) | **Do not rename** — these are historical records of `flutter_gsmsip`'s own history, copied along with the repo. Renaming their *content* would falsify history. Leave as-is; this flow's own new docs live in `flows/sdd-flutter_gsm/` (already correctly named). |
| `legacy/` subfolder (inherited from `flutter_gsmsip`, a full old-generation app copy, already excluded from `dart analyze`) | Delete — confirmed no bearing on GSM-abstraction scope (it's a pre-`sdd-split-lib-and-example` full-app snapshot, unrelated to the modem/GSM domain work). Resolves the requirements' Should-Have. |

## 2. Platform-Interface Contract Revision

### 2.1 What stays unchanged from `sdd-flutter_gsmsip-interface`

`ModemDevice`, `ModemCall`, `ModemEvent` (+ 8 subtypes), `CarrierProfile`
(+ `CarrierProfileRegistry`), `ModemGroupConfig`, `AtCommandResult`,
`ModemState`, `NetworkMode`, `RestartMode`, `RegistrationState`,
`PacingAlgorithm`, the modem-exceptions hierarchy, and
`ModemRepository`'s method signatures — all carry over unchanged. They're
transport-agnostic already; renaming the package doesn't require
redesigning them.

### 2.2 What changes: Android backing

Per the decided architecture, `FlutterGsmPlatform`'s Android
implementation (`MethodChannelFlutterGsm`, or a new
`AndroidFlutterGsm` if a cleaner split is warranted — decide in plan)
stops returning `UnsupportedError`/empty results for modem methods and
instead wraps `flutter_dialer` + `flutter_tele`. Verified both packages'
real APIs (not guessed):

- **`flutter_dialer`**: `FlutterDialer.isDefaultDialer()`,
  `.setDefaultDialer()`, `.canSetDefaultDialer()` — all static,
  `Future<bool>`. Used for the one-time "become default dialer"
  precondition `flutter_tele` needs before it can receive calls via
  `InCallService`.
- **`flutter_tele`**: `TeleEndpoint` (instantiable class, not static) —
  `requestPermissions()`/`hasPermissions()`, `start(config)` (returns
  known accounts+calls), `on(eventType)` → `Stream<dynamic>` (event-type
  keyed, not a single unified stream), `makeCall(sim, destination,
  callSettings, msgData)` → `TeleCall`, `answerCall`/`hangupCall`/
  `declineCall`/`holdCall`/`unholdCall`/`muteCall`/`unMuteCall`/
  `useSpeaker`/`useEarpiece`/`sendEnvelope` (all take a `TeleCall`).
  `TeleCall` carries `simSlot`/`simSlot1`/`simSlot2` — i.e. **dual-SIM is
  already modeled** at this layer, relevant for `ModemDevice.id` mapping
  (see 2.3).

### 2.3 Android `ModemRepository` mapping

| `ModemRepository` method | Backed by |
|---|---|
| `listModems()` | One `ModemDevice` per SIM slot reported by `TeleEndpoint.start()`'s `accounts` (or a fixed 2-slot enumeration if the phone is dual-SIM — exact source TBD in plan once `flutter_tele`'s native side is inspected for how it reports available SIMs before any call is made) |
| `getModem(id)` | Lookup by `simSlot` |
| `modemEvents` | Adapt `TeleEndpoint.on('call_changed'|'call_received'|'call_terminated'|...)` streams into `ModemEvent` subtypes — event-type names TBD from `flutter_tele`'s native Kotlin source in plan phase |
| `sendAtCommand` | **Not supported** — Android's native radio isn't AT-command-addressable through `flutter_tele`; throw `UnsupportedError` still, this part of the original stub approach is correct and unchanged |
| `setPower`/`restartModem`/`changeImei`/`setNetworkMode`/`setDiagMode` | **Not supported** — same reasoning; these are modem-hardware-specific (chan_svistok-side) operations with no Android telecom equivalent |
| `dial(modemId, number)` | `TeleEndpoint.makeCall(simSlot, number, ...)` |
| `hangupCall`/`answerCall` | `TeleEndpoint.hangupCall`/`answerCall` (need a `TeleCall` — `ModemRepositoryImpl` must track the mapping from its own call-id scheme to `TeleCall` instances) |
| `sendSms`/`sendUssd` | **Not covered by `flutter_tele`/`flutter_dialer`** — Android SMS goes through `flutter_smsussd` (confirmed in prior research to actually be SMS-only despite its name) or Android's own `SmsManager`; USSD has no equivalent in either package. **Gap, flag for plan**: either depend on `flutter_smsussd` for `sendSms`, or leave both `UnsupportedError` on Android and document that SMS/USSD-over-native-radio isn't in this flow's scope. **Recommend**: depend on `flutter_smsussd` for `sendSms` (it exists and fits), leave `sendUssd` unsupported (no package provides it, out of scope). |

This is real, useful behavior on Android (not a stub), but it does **not**
cover the full `ModemRepository` surface — the AT-command/diagnostic/
firmware-adjacent methods have no Android equivalent and correctly stay
unsupported. Document this split explicitly in the rewritten platform
doc-comments so callers don't expect AT-command behavior on Android.

### 2.4 Windows/macOS

Per the decided default: mirror Linux exactly — `dartPluginClass`
registration (`WindowsFlutterGsm`/`MacosFlutterGsm`), every modem method
throws `UnimplementedError('...: implemented by sdd-asterisk-chan-simbox
+ a future windows/macos channel flow')`. `getPlatformVersion()` gets a
real trivial implementation per platform (mirrors Linux's `/etc/os-release`
read) since it's free and useful for diagnostics.

## 3. `flutter_gsmsip` Thin-Orchestrator Shape

### 3.1 Capability-gap check: `flutter_gsmsip`'s `sip_service.dart` vs. `flutter_nmsip`

Compared `SipRepositoryImpl`'s actual calls against `flutter_nmsip`'s
real public API (`FlutterSip2`, static methods) — both read directly from
source, not assumed:

| `SipRepositoryImpl` calls | `flutter_nmsip` equivalent | Gap? |
|---|---|---|
| `createAccount` | `FlutterSip2.createAccount` | ✅ covered |
| `registerAccount` | `FlutterSip2.registerAccount` | ✅ covered |
| `deleteAccount` | `FlutterSip2.deleteAccount` | ✅ covered (see note below on `unregisterAccount`) |
| `makeCall` | `FlutterSip2.makeCall` | ✅ covered |
| `answerCall`/`hangupCall`/`declineCall` | same names | ✅ covered |
| `holdCall`/`unholdCall`/`muteCall`/`unmuteCall`/`useSpeaker`/`useEarpiece` | same names | ✅ covered |
| `sendDtmf` | `dtmfCall` | ✅ covered, different name |
| `transferCall` | `xferCall` | ✅ covered, different name (blind transfer) |
| `attendedTransfer` | **none found** | ❌ **real gap** — `flutter_nmsip` has no attended-transfer method in its current public API |
| `unregisterAccount` | **none found** (only `deleteAccount`) | ❌ **real gap** — SIP "unregister" (send REGISTER Expires=0, keep local account) is semantically different from "delete" (remove the account object); `flutter_nmsip` only exposes delete |
| `destroyEndpoint`/`initializeEndpoint` | `start()` exists; no explicit destroy | ⚠️ **partial** — `start()` likely covers init; no teardown method found |
| `isConnected`/`isInitialized` | **none found** | ❌ **real gap** — no connection/init-state query; would need to be derived from `eventStream` state tracking on the caller side |
| `accounts`/`getAccounts`/`getAccount(id)` | **none found** | ❌ **real gap** — no account-listing/lookup API; `flutter_gsmsip` would need to track accounts itself from `createAccount`'s return values |
| `activeCalls` | **none found** | ❌ **real gap** — no call-listing API; same pattern, track locally from `makeCall`/event-stream data |
| `accountStream`/`callStream`/`connectivityStream` | single unified `eventStream` (`Stream<Map<String,dynamic>>`) | ⚠️ **shape mismatch, not a hard gap** — `flutter_nmsip` emits one raw event stream; `flutter_gsmsip` needs its own demuxing layer to split it into typed sub-streams |

**Conclusion**: `flutter_nmsip` covers the *command* surface (account
CRUD-minus-unregister, call control) essentially completely, but provides
**no state-query/listing API** (`accounts`, `activeCalls`,
`isConnected`/`isInitialized`) and **no attended transfer**. This means
`flutter_gsmsip`'s thin orchestrator can't be *purely* a pass-through —
it needs a **local state-tracking layer** (subscribe to `eventStream`,
maintain its own account/call registries) even though it delegates all
actual SIP protocol work to `flutter_nmsip`. This is still much thinner
than today's embedded `sip_service.dart` (no PJSIP glue, no protocol
logic), but "thin orchestrator" ≠ "zero logic" — document this
precisely so plan doesn't under-scope it.

**Recommendation, resolving the "delete outright vs. gap-check-first"
open question from requirements**: delete `flutter_gsmsip`'s embedded
`sip_service.dart` PJSIP-glue code, but **build** (not skip) a
`SipStateTracker`-shaped component in the new orchestrator that:
subscribes to `flutter_nmsip.FlutterSip2.eventStream`, demuxes by event
type, maintains account/call registries, and exposes the
`isConnected`/`accounts`/`activeCalls`-shaped queries `flutter_gsmsip`'s
own callers (and `simbox-app`) currently expect. `attendedTransfer`
and `unregisterAccount` get documented as **known gaps** — either
implement a workaround (e.g. `unregisterAccount` via re-registering with
a 0 expiry through raw account config, if `flutter_nmsip`'s
`registerAccount`/account config exposes that) or flag as a
`flutter_nmsip` feature request, decided in plan.

### 3.2 `GatewayService`/`CallRouting` reshape

`GatewayService`'s existing ordered-init pattern (previously
Telephony→SIP→SMPP, corrected last flow to Modem→SIP→SMPP) becomes:
initialize `ModemRepository` (from `flutter_gsm`) → initialize the new
`SipStateTracker`+`FlutterSip2` wiring (from `flutter_nmsip`) → SMPP
(unchanged, `smpp_service.dart` stays in `flutter_gsmsip` — it's
genuinely bridging-adjacent, SMS-gateway logic, not SIP or GSM hardware
access, no redundancy found against it in requirements' research).
`CallRouting`'s bidirectional logic (GSM call → dial out on SIP leg, and
vice versa) is unchanged in shape, just re-sourced: the "GSM leg" now
reads `ModemEvent`/`ModemCall` from `flutter_gsm.ModemRepository` instead
of the old in-package `TelephonyService`.

## 4. `simbox-app` Import Fixes

`simbox-app`'s `pubspec.yaml` currently depends on `flutter_gsmsip` (path
dependency, `../../libsFlutter/flutter_gsmsip` post-reorg) for
`ModemRepository`/`ModemDevice`/etc. Per the split, these types move to
`flutter_gsm`. Required change: add a `flutter_gsm` path dependency,
switch all `import 'package:flutter_gsmsip/flutter_gsmsip.dart'` (or
sub-imports) that reference Modem-layer types to
`import 'package:flutter_gsm/flutter_gsm.dart'`. `flutter_gsmsip` stays a
dependency only if `simbox-app` ends up needing bridging-specific types
(`GatewayService`, `CallRouting`) — check actual usage in plan phase
before assuming both are needed; `vdd-simbox-app-uiux`'s implementation
log shows it built against `FakeModemRepository`/`ModemRepository`
directly, so it may only need `flutter_gsm`.

## 5. Edge Cases / Behavior Notes

- **Android dual-SIM enumeration timing**: `flutter_tele`'s `TeleCall`
  models `simSlot`, but whether SIM slots are enumerable *before* any
  call/account exists (i.e. can `listModems()` return real devices at
  app startup, or only after `TeleEndpoint.start()` has been called at
  least once) needs verification against `flutter_tele`'s native Kotlin
  source in plan phase — don't assume `listModems()` works pre-`start()`.
- **`flutter_dialer` precondition**: `AndroidFlutterGsm`/
  `MethodChannelFlutterGsm`'s Android modem methods should check
  `FlutterDialer.isDefaultDialer()` before attempting calls, and surface
  a clear typed error (not a raw platform exception) if the app isn't
  the default dialer yet — this is a real, common failure mode (user
  hasn't granted default-dialer status), not an edge case to skip.
- **Event stream demuxing risk**: both `flutter_tele.TeleEndpoint.on()`
  and `flutter_nmsip.FlutterSip2.eventStream` use loosely-typed
  `Map<String, dynamic>`/`dynamic` event payloads with string-keyed
  `type` fields — the adapter code translating these into
  `ModemEvent`/typed SIP events needs defensive parsing (missing keys,
  unexpected types), not blind casts, since neither package's own code
  is strongly typed at this boundary (confirmed by reading their source
  — both use `print()` debug logging and permissive `Map` handling
  throughout, not exceptions-on-malformed-input).

## Dependencies / Integration Points

- Depends on `sdd-asterisk-chan-simbox` for eventual real Linux/Windows/
  macOS/OpenWRT behavior — not blocking this flow, per requirements.
- `flutter_gsm`'s Android implementation depends on `flutter_dialer`
  and `flutter_tele` as real pub dependencies (path-based, matching the
  monorepo's existing convention) — add to `pubspec.yaml`.
- `flutter_gsmsip`'s new orchestrator depends on `flutter_gsm` and
  `flutter_nmsip` (path-based) — remove the embedded PJSIP/Android
  telephony code this replaces.
- `simbox-app` depends on `flutter_gsm` directly (new), keeps
  `flutter_gsmsip` only if bridging types are actually used (verify in
  plan).

---

## Approval

- [x] Reviewed by: Anton Dodonov
- [x] Approved on: 2026-08-21
- [x] Notes: Approved as drafted.
