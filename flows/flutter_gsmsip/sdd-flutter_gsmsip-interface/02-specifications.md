# Specifications: flutter_gsmsip-interface

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-08-20
> Requirements: [01-requirements.md](01-requirements.md) — APPROVED 2026-08-20

## Decisions on Open Questions (carried from requirements)

1. **Entity naming**: new serial/AT-command device concept is named
   **`Modem`** (`ModemDevice`, `ModemStatus`, `ModemCall`, `ModemEvent`,
   `ModemGroupConfig`). `Dongle*` stays exactly as-is (Android audio
   adapter). `GatewayConfig`/`SipCall` stay as-is (SIP side).
2. **Federated packaging**: stay a **single package** for this flow. Add a
   `linux:` entry to `pubspec.yaml`'s `flutter.plugin.platforms` pointing at
   a new `linux/` native scaffold, rather than splitting into
   `flutter_gsmsip_platform_interface`/`_linux` packages now. Reason:
   `sdd-complete-refactoring` reports the package doesn't currently compile;
   splitting packages multiplies that problem. Revisit federation once
   `sdd-flutter_gsmsip-channel` needs real FFI/native code and the interface
   has proven stable.
3. **Carrier profiles**: `CarrierProfile` is a `flutter_gsmsip` domain
   entity (USSD-code templates + response-parsing rules), held in a
   `CarrierProfileRegistry` that ships with sane defaults but accepts
   app-supplied overrides/additions at runtime (`registry.register(profile)`)
   — so simbox-app can add operators without forking the plugin.
4. **IMEI pool**: out of scope. `changeImei(modemId, imei)` takes an
   already-known IMEI; sourcing one (external pool service, manual entry)
   is the caller's problem. No `imeiPool` seam added.

## Affected Systems / Components

| Component | Change |
|---|---|
| `lib/flutter_gsmsip_platform_interface.dart` | Add the full modem/call/SMS/USSD/event API as abstract members |
| `lib/flutter_gsmsip_method_channel.dart` | Implement new members via the existing `MethodChannel('flutter_gsmsip')` + a new `EventChannel('flutter_gsmsip/modem_events')` (Android path — real behavior unchanged, just routed through the interface now) |
| `lib/src/domain/entities/` | New: `modem_device.dart`, `modem_call.dart`, `carrier_profile.dart`, `modem_group_config.dart` |
| `lib/src/domain/models/` | New: `modem_state.dart`, `modem_event.dart`, `at_command_result.dart`, `network_mode.dart`, `restart_mode.dart` |
| `lib/src/domain/repositories/` | New: `modem_repository.dart` (interface only) |
| `lib/src/data/repositories/` | New: `modem_repository_impl.dart` — delegates every call to `FlutterGsmsipPlatform.instance` |
| `lib/src/services/telephony_service.dart` | Refactor to stop calling `MethodChannel('gsm_sip_gateway/telephony')` directly; route through `ModemRepository`/`FlutterGsmsipPlatform` instead |
| `lib/src/data/sources/voice_line/tty_port_source.dart` | Left as-is (Android voice-line concept); **not** reused for the new Linux modem driver — chan_svistok-derived serial I/O is a separate, more complete implementation to be added in `sdd-flutter_gsmsip-channel` |
| `pubspec.yaml` | Add `flutter.plugin.platforms.linux` entry |
| `linux/` (new) | Minimal CMake + plugin registration scaffold; `LinuxFlutterGsmsip` Dart class registered as the platform instance on Linux, all modem methods throw `UnimplementedError('...: implemented in sdd-flutter_gsmsip-channel')` |
| `android/src/` | No functional change; existing Kotlin channels (`flutter_gsmsip`, `flutter_gsmsip/dialer`, `flutter_gsmsip/replace_dialer`, `flutter_gsmsip/headless`) keep working, now reached only through the platform interface |

## Data Models

### `ModemDevice` (entity, `equatable`)
```
id            String   // stable id, e.g. tty path or platform-assigned handle
portPath      String?  // '/dev/ttyUSB0' on Linux; null/opaque on other platforms
displayName   String?
manufacturer  String?
model         String?
imei          String?
imsi          String?
iccid         String?
groupId       String?
state         ModemState
signal        int?     // 0-31 CSQ-style RSSI, null = unknown
registration  RegistrationState  // notRegistered, registered, roaming, searching
balance       String?  // last-known balance, carrier-formatted string
```

### `ModemState` (enum, mirrors chan_svistok's 8-state call machine at the
   device level, extended for non-call states)
```
init, ready, registering, registered, callActive, callOnHold, error, removed
```

### `ModemCall` (entity, parallel shape to `SipCall` but for modem-originated
   legs — kept separate rather than reusing `SipCall` because a modem call
   has no SIP account/URI concept)
```
id, modemId, number, direction (CallDirection, reused), state (CallState, reused),
startTime, connectTime, endTime, isOnHold
```
Reuses `CallDirection`/`CallState` from `sip_call.dart` (already generic
enough); does not reuse `SipCall` itself because `accountId` doesn't apply.

### `ModemEvent` (sealed class hierarchy — this is the new push-event
   contract required by requirements AC #5)
```
sealed class ModemEvent { final String modemId; final DateTime timestamp; }

  ModemAttached(ModemDevice device)
  ModemDetached(String modemId)
  ModemStateChanged(ModemState previous, ModemState current)
  ModemSignalChanged(int signal)
  ModemRegistrationChanged(RegistrationState state)
  ModemCallStateChanged(ModemCall call)
  ModemSmsReceived(String from, String text, DateTime receivedAt)
  ModemUssdReceived(String text)  // unsolicited USSD push
  ModemErrorOccurred(String code, String message)
```

### `AtCommandResult`
```
raw           String   // full raw response
ok            bool
error         String?  // CME/CMS error text if any
durationMs    int
```

### `ModemGroupConfig` (replaces flat `.online_max`/`.limit_max.N`/
   `.priority` files from simbox-desktop-v2015)
```
groupId, onlineMax, limitMaxByPeriod (4 ints), priority,
pacingAlgorithm (enum), pacingDiffSlow, pacingNoDiff
```

### `CarrierProfile`
```
operatorId, displayName, regionCode,
balanceUssdTemplate, tariffUssdTemplate, numberUssdTemplate,
responseParser (function/strategy id)
```

### `NetworkMode` / `RestartMode` (enums)
```
NetworkMode: auto, gsmOnly, wcdmaOnly
RestartMode: now, graceful, whenConvenient   // mirrors chan_svistok's 3 restart options
```

## `FlutterGsmsipPlatform` — New Abstract API

```dart
abstract class FlutterGsmsipPlatform extends PlatformInterface {
  // existing
  Future<String?> getPlatformVersion();

  // Discovery & state
  Future<List<ModemDevice>> listModems();
  Future<ModemDevice?> getModem(String modemId);
  Stream<ModemEvent> get modemEvents;

  // Raw / diagnostics
  Future<AtCommandResult> sendAtCommand(String modemId, String command,
      {Duration timeout = const Duration(seconds: 5)});
  Future<void> setDiagMode(String modemId, bool enabled);

  // Power / lifecycle
  Future<void> setPower(String modemId, {required bool on});
  Future<void> restartModem(String modemId, {RestartMode mode = RestartMode.now});

  // Identity / network
  Future<void> changeImei(String modemId, String imei);
  Future<void> setNetworkMode(String modemId, NetworkMode mode);
  Future<void> setGroup(String modemId, String groupId);

  // Calling
  Future<ModemCall> dial(String modemId, String number);
  Future<void> hangupCall(String callId);
  Future<void> answerCall(String callId);

  // SMS / USSD
  Future<void> sendSms(String modemId, String number, String text);
  Future<String> sendUssd(String modemId, String code);
}
```

Default `_instance` stays `MethodChannelFlutterGsmsip` on Android (unchanged
registration mechanism); `linux/` scaffold registers `LinuxFlutterGsmsip`
which extends this class and stub-throws on every modem method.

## Chan_svistok CLI → New API Mapping

| chan_svistok CLI | New API |
|---|---|
| `dongle show devices` / `devicesl` | `listModems()` |
| `dongle show device settings/state/statistics` | `getModem(id)`, fields on `ModemDevice` |
| `dongle cmd <dev> <at>` | `sendAtCommand(id, cmd)` |
| `dongle sms <dev> <num> <msg>` | `sendSms(id, num, msg)` |
| `dongle ussd <dev> <code>` | `sendUssd(id, code)` |
| `dongle reset <dev>` | `restartModem(id, mode: now)` |
| `dongle start <dev>` | `setPower(id, on: true)` |
| `restart gracefully` / `when convenient` | `restartModem(id, mode: graceful/whenConvenient)` |
| `dongle setgroup <dev> <g>` | `setGroup(id, groupId)` |
| `dongle setgroupimsi <imsi> <g>` | app-level: resolve `imsi → modemId` via `listModems()`, then `setGroup` |
| `dongle callwaiting <dev>` | deferred — no call-waiting method yet; add if/when `sdd-flutter_gsmsip-channel` needs it |
| IMEI change (`changeimei.sh`) | `changeImei(id, imei)` |
| Network/frequency lock (`AT^SYSCFG`/`AT^FREQLOCK`) | `setNetworkMode(id, mode)` (frequency-lock granularity deferred — flag in Open Items) |
| diag mode / firmware prep | `setDiagMode(id, enabled)`; actual firmware flashing (`ttyprog_*`) stays out of scope, per requirements |
| USB hub power-cycle (`hub-ctrl`) | deferred to `sdd-flutter_gsmsip-channel` (needs real USB bus/port addressing, not modeled by `ModemDevice.id` alone) |
| Group/plan limits (`plan.php`, `bs.php`) | `ModemGroupConfig` entity, set via app-level config store (not a platform-channel method — this is pure Dart state, no native call needed) |
| `nabor` USSD recipes | `CarrierProfile` + `CarrierProfileRegistry` |

## Behavior / Edge Cases

- **No device implementation available (this flow only)**: every
  `LinuxFlutterGsmsip` method throws `UnimplementedError` with a message
  pointing at `sdd-flutter_gsmsip-channel`. Callers (services, and later
  simbox-app UI) must treat `UnimplementedError` distinctly from a real
  "no device" business error — do not conflate the two. `ModemRepository`
  wraps this as a typed `ModemDriverNotAvailable` failure so UI code
  doesn't need to catch `UnimplementedError` directly.
- **Empty device list**: `listModems()` returning `[]` is valid (no
  hardware attached) and distinct from the driver-not-available case above.
- **Event stream lifecycle**: `modemEvents` is a broadcast stream; it must
  be safe to have zero or many listeners, and must not throw if no native
  event source exists yet (Linux stub) — it simply never emits.
- **AT command timeout**: `sendAtCommand` must resolve (not hang) even on
  the stub platform — stub implementations return immediately with the
  `UnimplementedError`, real timeout handling is a channel-flow concern.
- **Concurrent calls per modem**: chan_svistok's call-waiting exists at the
  channel-driver level; this interface does not yet model multiple
  concurrent `ModemCall`s per `ModemDevice`. Single active call per modem
  is assumed for this flow; revisit in `sdd-flutter_gsmsip-channel` if
  call-waiting is implemented.
- **`GatewayService` bidirectional routing**: `GatewayService`'s
  SIP↔GSM `CallRouting` orchestration must be updated to source the "GSM
  side" leg from `ModemCall`/`ModemRepository` instead of the old
  `TelephonyService` MethodChannel calls, preserving its existing
  ordered-init behavior (Telephony→SIP→SMPP becomes Modem→SIP→SMPP).

## Dependencies / Integration Points

- Depends on `sdd-complete-refactoring` reaching a compiling baseline first
  (tracked as a plan prerequisite, not a spec item here).
- No new pub dependencies required for this flow (no serial I/O yet — that's
  `sdd-flutter_gsmsip-channel`, which will likely add `dart:ffi`/
  `package:ffi` or a serial-port package).
- `vdd-simbox-app-uiux` consumes `ModemDevice`/`ModemEvent`/`ModemCall` and
  `ModemRepository` once this flow's implementation lands — UI code should
  depend on the repository interface, not `FlutterGsmsipPlatform` directly.

## Open Items Deferred (explicitly, not silently dropped)

- Call-waiting toggle, frequency-lock granularity, USB hub power control,
  firmware flashing, IMEI pool sourcing — noted above, out of scope for
  this flow, revisit in `sdd-flutter_gsmsip-channel` or a future flow.
- Whether `ModemGroupConfig`/`CarrierProfileRegistry` persist via the
  existing `shared_preferences`-based storage pattern
  (`local_storage_datasource.dart`) or a new store — decide in PLAN phase
  when touching `lib/src/data/datasources/`.

### Addendum (2026-08-23, flagged by `vdd-simbox-app-uiux`'s "Каналы"
redesign — not reopening this flow's approved specs, recorded here as a
follow-up requirement per that flow's established cross-flow-gap
pattern)

`ModemDevice` currently models one call-capable channel as a
modem+SIM unit — it has no concept of a SIM card that exists
independent of a modem (e.g. a spare/tray SIM not currently seated in
any device). Anton's explicit requirement (verbatim, recorded here at
his instruction, same permanence rule as
`vdd-simbox-app-uiux/01-requirements.md`'s CRITICAL note):

> Знает ли API sdd-flutter_gsmsip-interface о SIM-картах вне модема
> («не в модеме») - должен уметь работать с обоими сценариями,
> зависит от модема, должны поддерживаться все модемы. Запиши. Если
> нужно - скорректируй так же sdd-flutter_gsmsip-interface

(English gloss: the API must support **both** scenarios — a SIM
seated in a modem, and a SIM not currently in any modem — as a
first-class case, not an unsupported edge case; whether a given piece
of hardware can actually report "SIM in tray, not seated" depends on
that modem/hub's own capability, but the API shape itself must not
assume every SIM has a modem, across all supported modem types.)

**Not implemented by this addendum** — this is a real, currently-
unmodeled capability gap, not a small field addition like the
Симки-screen field gap noted above. It likely needs: (a) a new
`SimCard`-shaped entity distinct from `ModemDevice` (modem-nullable),
(b) a native-side concept of SIM inventory/tray state, which — per
`sdd-asterisk-chan-simbox`'s own findings — chan_dongle/`libsimbox`
do not currently have at all (their whole model is device/dongle-
centric, not SIM-tray-centric; this would be new capability there
too, not just a Dart-layer change). Scoping and designing this
properly is future work for a dedicated flow/amendment round, not
something to guess at here. Until it lands, `vdd-simbox-app-uiux`'s
"По SIM, все" flat mode ships showing only seated SIMs (i.e. the same
data as "По модемам," flattened) — see that flow's own status/specs
for how it documents this interim limitation.

---

## Approval

- [ ] Reviewed by: Anton Dodonov
- [ ] Approved on:
- [ ] Notes:
