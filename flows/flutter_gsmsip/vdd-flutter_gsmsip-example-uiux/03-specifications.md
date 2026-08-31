# Specifications: flutter_gsmsip-example-uiux

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-08-31
> Requirements: [01-requirements.md](01-requirements.md) (APPROVED)
> Visual: [02-visual.md](02-visual.md) (APPROVED)

## Overview

Specifications for AC1, AC4–AC8 of the approved requirements — the parts
that don't depend on `sdd-flutter_gsmsip-lib` reaching its own
Specifications. AC2 (multi-profile Setup) and AC3 (System Capabilities)
are covered under **Deferred** below: their screen shape is sketched from
`02-visual.md`, but their data model is explicitly not locked here.

Everything in this document lives under
`libsFlutter/flutter_gsmsip/example/**`. No file under
`libsFlutter/flutter_gsmsip/lib/**` is created, modified, or deleted by
this flow (AC8) — confirmed against the real repository, not assumed;
grep of the actual `GatewayRepository`/`GatewayConfig`/`CallRouting`
types below shows every capability AC1 needs already has a public API.

## Affected Systems

| System | Impact | Notes |
|---|---|---|
| `example/lib/screens/dashboard_screen.dart` | Rename/rework → `gateway_screen.dart` | AC1 — becomes the gateway-mode home |
| `example/lib/screens/setup_screen.dart` | Modify (deferred detail) | AC2 — blocked on `sdd-flutter_gsmsip-lib` |
| `example/lib/screens/settings_screen.dart` | Modify | Add entry point to new Capabilities screen (AC3, deferred) + embed Default Dialer card (AC4) |
| `example/lib/screens/` (new) | Create `capabilities_screen.dart` | AC3 — blocked on `sdd-flutter_gsmsip-lib`, sketch only |
| `example/lib/screens/widgets/` (new) | Create `default_dialer_card.dart`, `default_dialer_alert.dart` | AC4 |
| `example/lib/data/` (new) | Create `default_dialer_status_source.dart` | AC4 — thin abstraction over the currently-working `flutter_gsm/replace_dialer` channel |
| `example/lib/theme/app_widgets.dart` | Modify (re-skin, not replace) | AC6 |
| `example/lib/theme/app_colors.dart` | Modify | AC6 — swap bespoke palette for DS Green/Simple tokens |
| `example/lib/theme/app_gradients.dart` | Modify (mostly delete) | AC6 — DS allows exactly one accent gradient per build |
| `example/android/src/main/AndroidManifest.xml` | Modify (comments only, no permission removal without owning-library confirmation) | AC5 |
| `example/` splash config | Modify | AC7 — delegated entirely to `/nativemind-flutter-splash` |
| `libsFlutter/flutter_gsmsip/lib/**` | **None** | AC8 — verified untouched |

## Architecture

### Component Diagram

```
                    ┌─────────────────────┐
                    │   GatewayScreen      │  (was DashboardScreen)
                    │   (AC1)              │
                    └──────────┬───────────┘
                               │ reads (existing public API, no lib changes)
              ┌────────────────┼────────────────┬─────────────────┐
              ▼                ▼                ▼                 ▼
      GatewayService    GatewayService    GatewayService   DefaultDialerStatusSource
      .statusStream     .routingStream    .getActiveRoutings()   (AC4, new — example-local)
      (GatewayStatus)   (CallRouting)                                  │
                                                                        ▼
                                                          MethodChannel('flutter_gsm/replace_dialer')
                                                          (flutter_gsm's existing, working
                                                           ReplaceDialerModule.kt — see AC4 below
                                                           for why this is an interim source)

              ┌──────────────────────┐          ┌───────────────────────┐
              │  SetupScreen (AC2)    │          │ CapabilitiesScreen(AC3)│
              │  DEFERRED             │          │  DEFERRED              │
              └──────────┬────────────┘          └───────────┬────────────┘
                         │ blocked on                        │ blocked on
                         ▼                                   ▼
              sdd-flutter_gsmsip-lib's decision on   sdd-flutter_gsmsip-lib's decision on
              multi-profile storage API              capability-reporting API
```

### Data Flow (AC1 — Gateway screen)

```
GatewayService.statusStream ──> GatewayScreen._status (GatewayStatus)
GatewayService.routingStream ──> GatewayScreen._routings (List<CallRouting>, keyed by CallRouting.id)
DefaultDialerStatusSource.check() ──> GatewayScreen._dialerStatus (bool?, null = checking)
                                            │
                                            ▼
                        first time _status.isRunning flips false→true
                        while _dialerStatus == false
                                            │
                                            ▼
                        show DefaultDialerArmAlert (once per app session)
```

## Interfaces

All new interfaces below live in `example/lib/**` — none of them modify
`flutter_gsmsip`'s public API.

### New: `DefaultDialerStatusSource` (AC4)

```dart
// example/lib/data/default_dialer_status_source.dart

/// Reads default-dialer status for this app.
///
/// Interim implementation talks to `flutter_gsm`'s existing
/// `flutter_gsm/replace_dialer` MethodChannel (`ReplaceDialerModule.kt`
/// — the only currently-working implementation in this repo, per
/// 01-requirements.md's cross-flow table). `flutter_replace_dialer` may
/// later designate `flutter_dialer` as canonical instead; this
/// abstraction exists precisely so that swap doesn't touch
/// GatewayScreen/SettingsScreen — only this file's implementation
/// changes.
abstract class DefaultDialerStatusSource {
  /// True if this app is currently the default dialer.
  Future<bool> isDefaultDialer();

  /// True if the device even supports setting a default dialer
  /// (some OEM/Android builds don't expose `ACTION_CHANGE_DEFAULT_DIALER`).
  Future<bool> canSetDefaultDialer();

  /// Opens the OS's "set default dialer" flow. Does not await the
  /// result being "yes" — caller must re-check [isDefaultDialer] after
  /// the user returns to the app (existing `flutter_gsm` channel
  /// resolves the `MethodChannel` call once the request dialog is
  /// dismissed, not once the setting actually changes).
  Future<void> requestDefaultDialer();
}

class FlutterGsmDefaultDialerStatusSource implements DefaultDialerStatusSource {
  static const _channel = MethodChannel('flutter_gsm/replace_dialer');

  @override
  Future<bool> isDefaultDialer() async =>
      (await _channel.invokeMethod<bool>('isDefaultDialer')) ?? false;

  @override
  Future<bool> canSetDefaultDialer() async =>
      (await _channel.invokeMethod<bool>('canSetDefaultDialer')) ?? false;

  @override
  Future<void> requestDefaultDialer() =>
      _channel.invokeMethod('setDefaultDialer');
}
```

### Modified: `GatewayScreen` (was `DashboardScreen`) — AC1

No new public interface; reworks the existing `_DashboardScreenState`
pattern (already reading `_gateway.statusStream`/`_gateway.logStream`)
to also:
- subscribe to `_gateway.routingStream`, keeping a `Map<String,
  CallRouting>` keyed by `CallRouting.id`, removing entries where
  `routing.isCompleted` after a short delay (so `ended`/`failed` states
  are visible briefly, matching 02-visual.md's "Routing failed" mockup,
  not vanishing instantly)
- hold a `DefaultDialerStatusSource` instance, re-checked on `didChangeAppLifecycleState`
  (`AppLifecycleState.resumed`) so returning from the OS's default-dialer
  settings screen updates the card without a manual refresh
- render the Bridge Status card per `CallRouting.direction`
  (`sipToGsm`/`gsmToSip`) and `.state` (`connecting`/`active`/`ended`/
  `failed`) exactly as mocked in 02-visual.md — no new enum values invented

## Data Models

### New: `DialerWarningLevel` (AC4, example-local, not persisted)

```dart
enum DialerWarningLevel {
  /// isDefaultDialer == true
  none,
  /// isDefaultDialer == false, arm-time alert not yet shown this session
  needsAlert,
  /// isDefaultDialer == false, alert already shown/dismissed this session
  cardOnly,
}
```

Session-scoped (in-memory, resets on app restart) per 02-visual.md's
"re-fires once per app-restart if still unset" note — not persisted to
disk, so no new storage schema.

### Deferred (AC2/AC3) — sketch only, not locked

```dart
// NOT FINAL — shape only, pending sdd-flutter_gsmsip-lib Specifications
class GatewayProfileSketch {
  final String name;
  final GatewayConfig config; // existing type, unchanged
}

class CapabilityFlagSketch {
  final String label;           // e.g. "Capture Audio Output"
  final bool declared;          // present in some manifest
  final bool? grantable;        // null = unknown/checking, false = Magisk not installed
  final bool? wiredUp;          // null = n/a, false = declared+grantable but no backing code
}
```

These two types are placeholders to keep 02-visual.md's mockups
traceable to *something* — Specifications for AC2/AC3 will replace them
once `sdd-flutter_gsmsip-lib` commits to real method signatures. Do not
build storage or UI logic against `GatewayProfileSketch`/
`CapabilityFlagSketch` as if they were final.

## Behavior Specifications

### Happy Path — AC1 Gateway screen

1. User opens app → `GatewayScreen` subscribes to `statusStream`/
   `routingStream`, loads saved `GatewayConfig` via existing
   `ExampleConfigStore`.
2. Incoming GSM call arrives, `autoAnswer && routeGsmToSip` both true →
   `GatewayService._handleIncomingGsmCall()` fires (existing, unmodified
   library behavior) → a `CallRouting` with `direction: gsmToSip`,
   `state: connecting` appears on `routingStream`.
3. `GatewayScreen` renders the Active Routing card per 02-visual.md,
   transitions to `state: active` when the stream emits it.
4. Call ends normally → `state: ended` → card shows briefly, then is
   removed from the visible list (not from history — Logs screen,
   unchanged, still has it).

### Edge Cases

| Case | Trigger | Expected Behavior |
|---|---|---|
| Routing `failed` mid-call | GSM leg drops (no signal, network) | Card shows `failed` state with `errorMessage` if present (02-visual.md "Routing failed" mockup), `[Dismiss]` button removes it — does not auto-hide like `ended` |
| Default dialer revoked while app running | User changes default dialer to another app externally | `didChangeAppLifecycleState(resumed)` re-check catches it next time app is foregrounded; no background polling (battery cost not justified for a status that only changes via explicit user action in Settings) |
| Arm-time alert with no prior default-dialer check yet | User arms gateway before `isDefaultDialer()` future has resolved | Treat as `needsAlert` (fail toward showing the warning, not silently skipping it) — matches AC4's "proactively surface, don't assume" framing |
| `canSetDefaultDialer()` returns false | OEM/Android build without `ACTION_CHANGE_DEFAULT_DIALER` support | Card/alert copy changes from "Open Settings" to an explanation that this device doesn't support the standard flow — no dead-end button |
| Multiple simultaneous routings | `maxConcurrentCalls > 1` and more than one bridge active | List, not single card — 02-visual.md shows singular for clarity but the widget must handle `List<CallRouting>` |

### Error Handling

| Error | Cause | Response |
|---|---|---|
| `MethodChannel` `PlatformException` from `flutter_gsm/replace_dialer` | Channel not registered (e.g. running on iOS/desktop, where GSM/dialer concepts don't apply) | `DefaultDialerStatusSource` implementations are Android-only; on other platforms, `GatewayScreen` skips the card entirely (consistent with the existing "not supported here" pattern noted in 01-requirements.md's Constraints) |
| `GatewayService.statusStream` errors | Underlying platform channel failure | Existing `DashboardScreen` behavior (not touched) — this flow doesn't add new error handling beyond what already exists for the status stream |

## Design System Restyle (AC6)

**Confirmed accent**: `Green` = the DS's `Simple` colorway
(`~/.claude/skills/nativemind-designsystem/tokens/colors.css`,
`[data-theme="green"]`): `--brand-light: #34E89E`, `--brand: #0CA678`,
`--brand-gradient: linear-gradient(180deg, #34E89E 0%, #0CA678 100%)`,
`--brand-glow: rgba(12,166,120,0.20)`, `--brand-tint:
rgba(12,166,120,0.10)`. Neutrals are shared across all four colorways
(`--bg: #F8F9FA` / `--bg-dark: #0F1419`, etc.) — these match AC7's splash
background exactly, no discrepancy to reconcile.

**Re-skin, not replace** (confirmed with Anton) — every existing
`AppWidgets` static method keeps its call sites and signature; only
internal colors/shadows/gradients change:

| Widget (`app_widgets.dart`) | Current | DS re-skin |
|---|---|---|
| `gradientCard` | Per-call gradient (`AppColors.getCardGradient`) | Flat `--surface`/`--surface-dark` — DS reserves the one allowed gradient for a single primary CTA, not cards |
| `gradientButton` | Gradient `[AppColors.primary, AppColors.accent]` | Keep gradient **only** if this is the primary CTA (e.g. "Turn On Gateway Mode", "Set as Default Dialer") — DS's "one accent gradient per build" rule; otherwise flatten to `--brand` solid |
| `statusCard` | `statusColor` param, defaults to `AppColors.success` | Map to `--success`/`--warning`/`--danger` semantic tokens (shared across all colorways, not brand-accent) |
| `gradientProgressIndicator` | Gradient fill | Flatten to `--brand` solid — progress bars aren't the primary CTA |
| `gradientChip` | Gradient selected-state | Flatten to `--brand-tint` background + `--brand` border, per DS's chip pattern (`selected-row / chip wash` use of `--brand-tint`) |
| `signalIndicator` | Custom color ramp (`_getSignalColor`) | Keep the same 5-band logic, remap the two custom hexes (`0xFF34D399`, `0xFFF97316`) to `--success`/`--warning`/`--danger` — no new bands |
| `connectionIndicator` | `AppColors.gatewayConnected/-Connecting/-Disconnected` | Map to `--success`/`--warning`/`--danger` |
| `callStatusIndicator` | `AppColors.callActive` + custom | Map to `--success`/neutral `--fg-2` for the grey "ended" states already present |

**Shadow**: `app_theme.dart`'s existing shadow definitions (wherever they
diverge) collapse to DS's single app-wide shadow: `0 1px 32px
rgba(156,178,194,0.10)`.

**Iconography**: this app is a telephony/admin surface (gateway status,
call routing, capabilities) — DS's guidance for "admin/telephony
surfaces" applies: use `assets/adminka/` (GostSimBox 16px glyphs) where a
dense row needs a status glyph (routing state, capability tri-state
icons), not generic Lucide icons wholesale. Render at 16px (or an integer
multiple) with `image-rendering: pixelated`; fall back to Fugue 2× only
for states with no GostSimBox glyph. This is a more specific rule than
AC6's original "Lucide-style icons" phrasing — Specifications correct
that here based on reading the DS skill directly, not assumed from the
Requirements summary.

**No emoji**: confirmed already in 02-visual.md's symbol legend — no
further action needed, mockups already comply.

## Splash Screen (AC7)

No new specification content — `/nativemind-flutter-splash` owns the
entire implementation (native launch screen, zero hand-written splash
code, `#F8F9FA`/`#0F1419` + centered logo). This flow's only
responsibility: confirm `flutter_gsmsip/example` has a usable app logo
asset before invoking that skill; if not, source one from
`~/.claude/skills/nativemind-designsystem/uploads/logo_nativemind.svg` as
a placeholder pending a SimBox-specific mark.

## Permission Manifest Fix Plan (AC5)

Per 01-requirements.md's Permission Audit table, `example`'s own
`AndroidManifest.xml` gets a comment block (not permission removal —
removal is each owning library's decision, out of this flow's scope)
mapping each permission to where it *should* live:

```xml
<!-- Permission ownership map (added by vdd-flutter_gsmsip-example-uiux,
     see flows/flutter_gsmsip/vdd-flutter_gsmsip-example-uiux/01-requirements.md
     "Permission Audit" for full rationale). Do not remove permissions
     based on this comment alone — each row is a pointer to the flow
     that owns the actual fix. -->
<!-- READ_CONTACTS / WRITE_CONTACTS: no owning library yet;
     candidate = wherever vdd-dialer's contact integration lands -->
<!-- ACCESS_WIFI_STATE / CHANGE_WIFI_STATE, READ_PHONE_NUMBERS, USE_SIP,
     FOREGROUND_SERVICE_DATA_SYNC, SYSTEM_ALERT_WINDOW: no owning
     library; unclear if still needed — audit usage before next release -->
<!-- RECEIVE_BOOT_COMPLETED: gates a receiver that isn't registered
     anywhere (flutter_gsm's BootUpReceiver.kt has no manifest entry) —
     see flows/flutter_gsm/ -->
<!-- CALL_PRIVILEGED: signature-level, meaningless without the priv-app/
     Magisk path — see sdd-voiceline-mode-magisk-v2 -->
<!-- RECEIVE_MMS / RECEIVE_WAP_PUSH: unbacked cruft, no MMS/WAP-push
     code anywhere in flutter_smsussd — candidate for deletion unless
     MMS handling is an actual planned feature (confirm with Anton
     before removing) -->
```

The three permissions flagged as candidates for outright deletion
(`RECEIVE_MMS`, `RECEIVE_WAP_PUSH`) are **not removed by this
Specifications doc** — that's a Plan-phase decision requiring Anton's
confirmation first, per the comment above.

## Dependencies

### Requires

- `flows/flutter_gsmsip/sdd-flutter_gsmsip-lib/` reaching its own
  Specifications, for AC2/AC3's final data model (Deferred section
  above).
- Resolution of the Capabilities/Enhanced-Mode overlap with
  `vdd-flutter_gsmsip-example-voiceline-uiux` before AC3's screen is
  built (not before this document's non-AC3 sections are approved).
- `flutter_replace_dialer` eventually designating a canonical
  default-dialer module — `DefaultDialerStatusSource`'s interim
  `flutter_gsm`-backed implementation is explicitly a stopgap.

### Blocks

- Nothing outside this flow — `vdd-flutter_gsmsip-example-voiceline-uiux`
  and `-zatychka-uiux` are independent siblings, not downstream of this
  flow's implementation.

## Integration Points

### External Systems

- `flutter_gsm/replace_dialer` `MethodChannel` (existing, Android-only)

### Internal Systems

- `flutter_gsmsip.GatewayService` (`statusStream`, `routingStream`,
  `getActiveRoutings()`, `getConfig()`/`loadConfig()`) — read-only
  consumption, no new methods requested of the library for AC1/AC4.
- `example/lib/data/example_config_store.dart` (existing) — unchanged by
  this document; AC2's eventual profile storage may extend or replace it,
  deferred.

## Testing Strategy

### Unit Tests

- [ ] `FlutterGsmDefaultDialerStatusSource` — mock `MethodChannel`,
      verify all three methods map to the right method names and handle
      `PlatformException` by surfacing "not supported on this platform"
- [ ] `DialerWarningLevel` transition logic (none → needsAlert →
      cardOnly, session-scoped reset)
- [ ] `GatewayScreen`'s routing-list reducer: `CallRouting` add/update/
      remove-after-delay logic against `routingStream` fixtures covering
      all four `CallRoutingState` values and both `CallRoutingDirection`
      values

### Integration Tests

- [ ] Full arm→incoming-call→bridge→end flow against a fake
      `GatewayRepository` (existing test doubles from
      `sdd-flutter_gsmsip-example`, if any — reuse rather than duplicate)

### Manual Verification

- [ ] On a real rooted or non-rooted Android device: toggle default
      dialer off/on, confirm card + one-time alert behavior matches
      02-visual.md exactly, including the "Continue Anyway" path not
      permanently suppressing the persistent card
- [ ] Visual diff against 02-visual.md's Green/Simple accent once DS
      tokens are wired — confirm no scattered gradients remain outside
      the one designated primary CTA

## Migration / Rollout

No persisted data migration — `DialerWarningLevel` is session-only.
`GatewayConfig`/`ExampleConfigStore` schema is unchanged by this
document (AC2's eventual profile storage, when unblocked, will need its
own migration plan against whatever's already saved on developers'
devices from the current single-profile `ExampleConfigStore`).

## Open Design Questions

- [ ] Should `DefaultDialerStatusSource` live in `example/lib/data/` (as
      specified above) or as a tiny standalone example-local package, in
      case `vdd-flutter_gsmsip-example-voiceline-uiux`'s Enhanced Mode
      screen wants the same default-dialer read for its own purposes?
      Leaning toward keeping it in `example/lib/data/` until a second
      consumer actually needs it — avoid a premature shared package.
- [ ] Exact re-fire policy for the arm-time alert (02-visual.md left this
      open: "exact re-fire policy is a Specifications decision") —
      **resolved here**: session-scoped (in-memory `DialerWarningLevel`),
      resets on app restart, not on every screen navigation.

---

## Approval

- [ ] Reviewed by: Anton
- [ ] Approved on:
- [ ] Notes:

---

*Created by /vdd - flutter_gsmsip-example-uiux specifications*
