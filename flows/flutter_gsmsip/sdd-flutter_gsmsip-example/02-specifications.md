# Specifications: flutter_gsmsip-example

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-08-24
> Requirements: [01-requirements.md](01-requirements.md)

## Overview

Rebuild `libsFlutter/flutter_gsmsip/example` as a truthful, working
reference app for `GatewayService` (the real orchestrator), sequenced
README-first: `example/README.md` is rewritten to document the actual API
before the app is built to match it. Every screen is scoped to methods
that demonstrably exist on the public API — verified by reading the
source in this document, not carried over from the old README's
`GsmSipBridge` fiction. Nothing in `libsFlutter/flutter_gsmsip/lib/**`,
`flutter_gsm/**`, or `flutter_nmsip/**` is touched.

## Affected Systems

| System | Impact | Notes |
|--------|--------|-------|
| `example/README.md` | Modify | Rewritten first, to match reality |
| `example/lib/main.dart` | Modify | Becomes app shell + navigation only |
| `example/lib/screens/*.dart` | Create | setup, dashboard, settings, call, sms, logs |
| `example/lib/data/example_config_store.dart` | Create | Local `SharedPreferences` wrapper (see §"Config Persistence Gap" below) |
| `example/lib/platform_capabilities.dart` | Create | Static Android/Linux/macOS capability table |
| `example/lib/theme/*`, `example/lib/utils/*` | Modify/Prune | Keep what's used, drop dead fluff (imei_validator/easter_eggs/funny_messages — audit for actual use) |
| `example/pubspec.yaml` | Modify | Add nothing new required by design below; trim unused deps found during Plan (e.g. `workmanager`, `connectivity_plus`, `flutter_local_notifications` are not referenced by current `main.dart`) |
| `example/android/**` | Keep | Existing manifest/permissions already cover SIP+GSM+SMS use cases |
| `example/linux/**`, `example/macos/**` | Create | New platform scaffolds (`flutter create --platforms=linux,macos .`) |
| `libsFlutter/flutter_gsmsip/lib/**` | **None** | Explicitly out of scope |
| `flutter_gsm/**`, `flutter_nmsip/**` | **None** | Explicitly out of scope |

## Architecture

### Navigation

Single `MaterialApp` → `Scaffold` with a Material 3 `NavigationBar` (or
`NavigationRail` on wide/desktop layouts) switching between 6 screens via
`IndexedStack` (so screen state — e.g. in-progress SMS text — survives
tab switches):

```
Setup | Dashboard | Settings | Call | SMS | Logs
```

On first launch (no config found via `ExampleConfigStore.load()`), the
app opens directly on **Setup** instead of Dashboard. This is example-app
routing logic only — no lib change.

### Config Persistence Gap (must-read before implementing Setup/Settings)

`GatewayService.loadConfiguration()` is public, but there is **no public
save or clear method** — configuration is only persisted as a side effect
of a successful `initialize()` (`_saveConfiguration()` is private, and
`initialize()` returns `false` before reaching it if SIP account creation
fails — which it always does on Linux/macOS). Confirmed by reading
`gateway_service.dart` lines ~95–160 and ~497–523.

**Design decision**: `ExampleConfigStore` (new, example-local class) reads
and writes `SharedPreferences` directly under the same key
(`'gateway_config'`) and same JSON shape
(`GatewayConfig.toJson()`/`GatewayConfig.fromJson()`, both public) that
`GatewayService` itself uses. This makes Setup/Settings screens able to
persist and clear config independent of whether `initialize()` ever
succeeds, using only the lib's already-public serialization contract.

**Accepted risk** (documented, not silently ignored): `'gateway_config'`
is an internal storage-key implementation detail of `GatewayService`, not
part of its documented public contract. If a future version of the
library changes that key or shape, `ExampleConfigStore` would silently
desync from `GatewayService.loadConfiguration()`. There is no public API
alternative today without modifying the lib. `example/README.md` must
call this out explicitly so a future maintainer isn't surprised.

### Platform Capability Table (static, example-local)

```dart
// example/lib/platform_capabilities.dart
class PlatformCapabilities {
  static bool get sipSupported => Platform.isAndroid;
  static bool get modemDriverSupported => Platform.isAndroid || Platform.isLinux;
}
```

Values are hand-derived from reading `flutter_nmsip/pubspec.yaml` (Android
only) and `flutter_gsm`'s `Linux`/`Macos` platform implementations
(`SimboxModemRepository` real; `MacosFlutterGsm` stub-only, confirmed
throws `ModemDriverNotAvailableException`). Not queried from the libs at
runtime (no such API exists) — **must be kept in sync by hand** if
sibling-lib platform support changes; comment in the file says so and
points back at this spec.

Used to:
- Show a capability banner on Dashboard/Setup ("SIP not available on this
  platform" / "GSM modem not available on this platform").
- Pre-empt a doomed `Start Gateway` press with an explanatory dialog
  rather than only discovering the failure after the fact (both are
  implemented — see Behavior Specs below — the banner doesn't replace
  the real failure path, which must work regardless in case the table
  ever drifts from reality).

## Screens

### 1. Setup (`screens/setup_screen.dart`)

Form fields, backed by `SipAccount`/`SmppConfig`/`GatewayConfig`
constructors (all real, public):

- SIP: `username`, `password`, `domain`, `port` (default 5060),
  `transport` (`SipTransport` enum dropdown), `displayName` (optional).
- SMPP (optional, collapsible section): `host`, `port` (default 2775),
  `systemId`, `password`.
- Gateway toggles: `autoAnswer`, `enableLogging`, `routeSipToGsm`,
  `routeGsmToSip`, `routeSmsToSmpp`, `routeSmppToSms`,
  `maxConcurrentCalls`.

On Save: build a `GatewayConfig`, run `.validationErrors` (public getter,
already exists), show them inline if non-empty, else
`ExampleConfigStore.save(config)` and navigate to Dashboard.

### 2. Dashboard (`screens/dashboard_screen.dart`)

Evolves the existing single-file dashboard:

- Platform capability banner (from `PlatformCapabilities`).
- Modem device info card: a **separate, example-owned**
  `ModemRepositoryImpl()` from `flutter_gsm` (per the existing code
  comment in current `main.dart` — this pattern is already the intended
  one, just not built out) — `listModems()` on screen init, display
  `displayName`/`signal`/`registration`/`imei` for the first device found,
  or the capability-driven "not available" message if empty/throws
  `ModemDriverNotAvailableException`.
- `GatewayStatus` card, unchanged in spirit from today (`isRunning`,
  `sipState`, `smppState`) but wired to real `statusStream`.
- Start/Stop button: calls `loadConfiguration()` → if null, prompt to go
  to Setup (existing behavior, kept) → else `initialize(config)` **and
  checks its bool result** (today's code discards it — this is the
  concrete bug behind AC #5/#6): on `false`, surface the specific reason
  by reading the tail of `logStream` (both `GatewayService` and the SIP/
  modem-init log lines flow through it) in a dialog/snackbar, not a
  generic message.
- Quick actions kept from today (`Make Test Call`, `Send Test SMS`) but
  now take a real number via a text field instead of a hardcoded
  `+1234567890`.

### 3. Settings (`screens/settings_screen.dart`)

Same field set as Setup, pre-filled from `ExampleConfigStore.load()`,
plus:
- **Clear saved configuration**: `ExampleConfigStore.clear()` (deletes
  the `'gateway_config'` key directly — again, no public lib method for
  this, same accepted-risk note applies).
- Toggle logging/auto-answer/routing flags without re-entering
  credentials.

### 4. Call (`screens/call_screen.dart`)

Bound to `GatewayService().routingStream` /
`GatewayService().getActiveRoutings()` — a list of `CallRouting` (id,
number, direction, state, `formattedDuration`). Actions, **exactly** what
`GatewayService` exposes and nothing invented:
- "Test Call via SIP→GSM" (`makeCallViaSip(number)`)
- "Test Call via GSM→SIP" (`makeCallViaGsm(number)`)
- "End" per routing (`endRouting(id)`)
- "End All" (`endAllRoutings()`)

No answer/decline/hold/mute/DTMF controls — `GatewayService` does not
proxy `SipRepository`'s per-call methods that provide those (confirmed:
`SipRepositoryImpl` has `answerCall`/`holdCall`/`muteCall`/etc., but
`GatewayService` never calls or exposes them for direct use). Documented
in `example/README.md` as a known, honest limitation — not silently
dropped, not faked with a no-op button.

### 5. SMS (`screens/sms_screen.dart`)

Bound directly to `SmsService()` (public exported singleton — same
instance `GatewayService` uses internally, since it's a `factory`-backed
singleton) — `.messages`, `.messageStream`, `.getMessageStats()`. Send
form calls `GatewayService().sendSms(recipient, content, useSmpp: bool)`.

**Must document, not hide**: `SmsService.initializeSmpp`/`connectSmpp`
are simulated in the current library implementation (`await
Future.delayed(...)` then always report connected;
`_simulateMessageDelivery` uses a random 95% success roll) — this is a
property of the library as it stands today, not something the example
invents or should "fix" (fixing it would mean modifying the lib, out of
scope). `example/README.md`'s SMPP section must say plainly: *SMPP in
this build is a simulated stub, not a real SMPP client* — reusing the
library's existing honest doc comments (`sms_service.dart` already says
"Simulate SMPP bind operation") rather than presenting it as production
behavior.

### 6. Logs (`screens/logs_screen.dart`)

Merges `GatewayService().logStream` and `SmsService().logStream` (two
separate real streams — confirmed, no unified stream exists) into one
in-memory bounded list (e.g. last 500 entries) held in screen state.
Actions: clear (local list only), text-search filter (no level filtering
— the lib's log lines aren't leveled/tagged, so a "Filter by log level"
control as in the old README would be fake; dropped).

## Data Flow

```
Setup screen ──save──▶ SharedPreferences['gateway_config']
                              │
                              ▼ (read by both)
                    ExampleConfigStore.load()
                              │
                    GatewayService.loadConfiguration()
                              │
Dashboard "Start" ──▶ GatewayService.initialize(config)
                              │
                 ┌────────────┴─────────────┐
            modem discovery            SIP init + createAccount
         (non-fatal; logs on         (fatal on failure — returns
          ModemDriverNotAvailable)    false; only path that also
                              │        calls the private
                              │        _saveConfiguration())
                              ▼
                    GatewayService.start()
                              │
                statusStream / routingStream / logStream
                              │
                 Dashboard / Call / Logs screens re-render
```

## Behavior Specifications

### Happy Path (Android, real SIP server reachable)

1. First launch → Setup (no config found).
2. Enter valid SIP creds, optional SMPP, save → `ExampleConfigStore`
   persists, navigates to Dashboard.
3. Press Start Gateway → `initialize()` discovers a modem (if present),
   registers SIP account, returns `true` → `start()` registers, gateway
   marked running; status card shows `sipState: connected`.
4. Test Call / Send Test SMS produce real routing ids / message ids,
   visible on Call/SMS screens and in Logs.

### Edge Cases

| Case | Trigger | Expected Behavior |
|------|---------|-------------------|
| No config on launch | Fresh install, nothing in `SharedPreferences` | App opens on Setup, not Dashboard |
| Start pressed on Linux/macOS | SIP init always fails (no platform impl) | `initialize()` returns `false`; Dashboard shows the real failure reason from `logStream` tail (e.g. the `MissingPluginException`-derived message from `ServiceUnavailableFailure`), not a generic error, per AC #5 |
| Modem-less platform (macOS) | `listModems()` throws `ModemDriverNotAvailableException` | Dashboard's device-info card shows "GSM modem driver not available on this platform" instead of crashing or showing an empty spinner forever |
| Wrong SIP credentials (any platform) | `createAccount`/`registerAccount` fails | Same honest-failure-surfacing path as the platform-unsupported case — the UI doesn't distinguish "why" beyond what `logStream`/`Failure.message` already says, since `GatewayService` doesn't structure the failure reason beyond a string |
| Config saved but `initialize()` never yet called | User fills Setup, force-quits before pressing Start | Config still persisted (via `ExampleConfigStore`, independent of `initialize()`'s internal save) — reloads correctly next launch, including on Linux/macOS where `initialize()` would never reach its own save path |
| Clear configuration | Settings → Clear | `ExampleConfigStore.clear()`; if gateway currently running, also `GatewayService().stop()` first so state doesn't dangle |
| SMPP not configured | `smppConfig == null` in saved config | SMS screen's "send via SMPP" option disabled/hidden; only local-GSM send available (matches `sendSms(..., useSmpp: false)` default) |

### Error Handling

No new error types are introduced. All failures surface through the
lib's existing `Either<Failure, T>` (`dartz`) results, `bool` returns, or
thrown `ModemException`/subclasses — the example's job is to *display*
these accurately (via `.fold()`, checked booleans, and `try`/`catch` on
`ModemException`), not to invent new categorization.

## Dependencies

### Requires
- `libsFlutter/flutter_gsmsip` (path dependency, existing)
- `libsFlutter/flutter_gsm` (transitive via `flutter_gsmsip`, but example
  imports it **directly** too for the modem-listing use case above — this
  already happens transitively in `pubspec.lock`, just needs an explicit
  `flutter_gsm` entry so `import 'package:flutter_gsm/flutter_gsm.dart'`
  resolves cleanly rather than relying on transitive resolution)

### Blocks
- None (this is a leaf example app)

## Integration Points

### External Systems
- SIP server (user-supplied, Android only, real)
- SMPP server (user-supplied host/port, but the leg is simulated per
  library behavior today — see SMS screen spec)
- Real GSM modem (Android telephony stack, or Linux `/dev/ttyUSB*` via
  libsimbox)

### Internal Systems
- `SharedPreferences` (`'gateway_config'` key, shared contract with
  `GatewayService`, see Config Persistence Gap above)

## Testing Strategy

### Unit Tests
- [ ] `ExampleConfigStore`: save → load round-trip; clear removes key.
- [ ] `PlatformCapabilities`: pure functions of `Platform.isX`, trivial
  to unit test with `Platform`-override seams if needed, else skip if
  not worth the indirection (decide in Plan).

### Integration Tests
- Out of scope for this iteration (Should Have at most — decide in Plan
  whether trivial enough to include).

### Manual Verification
- [ ] `flutter analyze` clean on `example/` (0 errors).
- [ ] `flutter build linux` and `flutter build macos` succeed on this
  dev machine.
- [ ] `flutter build apk --debug` or equivalent succeeds if an Android
  toolchain is available in this environment; else document as
  unverified (matches the existing precedent in
  `sdd-flutter_gsmsip-interface`'s status notes for `flutter build
  linux`).
- [ ] Manual run on Linux (this dev machine) exercising: Setup → save →
  Dashboard → Start (expect honest SIP-unsupported failure) → modem
  listing (expect real result via libsimbox if a device is attached, or
  a graceful empty state).
- [ ] Manual run on macOS confirming the modem-unsupported message and
  SIP-unsupported message both appear distinctly.
- [ ] Android manual run deferred to Anton if no device/emulator is
  available in this environment — flagged, not silently skipped.

## Migration / Rollout

N/A — example app only, no persisted user data beyond
`SharedPreferences`, no released consumers to migrate.

## Open Design Questions

- [ ] Exact pruning list for `example/lib/theme/*` and
  `example/lib/utils/*` (easter eggs, funny messages, IMEI validator) —
  resolve during Plan by checking actual references from the new
  screens; nothing here blocks specification-level design.
- [ ] Whether `NavigationRail` (desktop-friendly) vs. sticking with
  `NavigationBar` on all platforms is worth the extra responsive-layout
  code — default to `NavigationBar` everywhere unless Plan finds it
  awkward on Linux/macOS windows.

---

## Approval

- [ ] Reviewed by: Anton
- [ ] Approved on:
- [ ] Notes:
