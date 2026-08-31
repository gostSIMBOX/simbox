# Specifications: flutter_dialer

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-08-31
> Requirements: [01-requirements.md](01-requirements.md)
> Visual: [02-visual.md](02-visual.md)

## Overview

Fixes `flutter_dialer`'s callback-timing bug, adds two small missing
capabilities (launch-intent number surfacing, call-log query) needed for
the approved Visual mockups, and removes its dead/conflicting
`InCallService`. `flutter_dialer` remains a leaf package — role
management + call history + launch-intent handling only. Live call
state (ringing/active/DTMF/mute) is explicitly `flutter_tele`'s job, not
rebuilt here.

**Grounding fact that resolves the architecture question flagged in
Visual's Notes**: `flutter_tele`'s `pubspec.yaml` already declares
`flutter_dialer: ^2.0.0+101` (confirmed by reading it) and its
`lib/src/dialer.dart` already wraps `FlutterDialer`'s three methods as
`TeleDialer`. The dependency direction is `flutter_tele -> flutter_dialer`,
already in place, already correct per the leaf-package constraint. No
new dependency needs to be added in that direction — the only change is
in `flutter_dialer_replacement/example`'s `pubspec.yaml`, which gets a
path dependency on `flutter_tele` purely to demo the full call flow
(example apps aren't bound by their library's leaf constraint).

**Second grounding fact**: `flutter_tele`'s own `AndroidManifest.xml`
already registers a real `InCallService` (`org.telon.tele.flutter_tele.TeleService`,
520 lines, real `Call.Callback` state tracking) with the same
`android.telecom.InCallService` intent-filter action that
`flutter_dialer`'s `TeleService.kt` (50-line stub) also declares. Any
app that depends on both packages — which, per the fact above, is every
app that also wants `flutter_tele` — ends up with **two** manifest
entries competing for the same intent-filter after Gradle's manifest
merge. This is a real, previously undiagnosed bug, not just untidy
duplication. Deleting `flutter_dialer`'s copy (AC2's decision) fixes it.

## Affected Systems

| System | Impact | Notes |
|--------|--------|-------|
| `flutter_dialer/android/.../FlutterDialerPlugin.kt` | Modify | Add `ActivityAware`, fix `setDefaultDialer()` callback timing, revise `canSetDefaultDialer()` semantics, add `getCallLog` + launch-intent EventChannel handlers |
| `flutter_dialer/android/.../MainActivity.kt` | Modify | Replace dead `tel:`/`DIAL` stub with real EventChannel emission + initial-intent capture |
| `flutter_dialer/android/.../TeleService.kt` | **Delete** | Superseded by `flutter_tele`'s canonical `InCallService`; its manifest entry caused a real duplicate-intent-filter conflict |
| `flutter_dialer/android/src/main/AndroidManifest.xml` | Modify | Remove the `<service>` block for `TeleService` |
| `flutter_dialer/lib/flutter_dialer.dart` | Modify | Fix doc comments on existing 3 methods (behavior changes, not signatures); add `getCallLog()`, `initialNumber()`, `numberStream` |
| `flutter_dialer/lib/flutter_dialer_platform_interface.dart`, `flutter_dialer_method_channel.dart` | Modify | Wire new methods/streams through the platform-interface pattern already used for `getPlatformVersion` |
| `flutter_dialer_replacement/example/pubspec.yaml` | Modify | Add path dependency on `flutter_tele` (demo-only) |
| `flutter_dialer_replacement/example/lib/main.dart` | Modify | Split into 5 screens per `02-visual.md`; existing status/setup logic becomes one screen among five |
| `flutter_tele` (any file) | **None** | Already correct — canonical `InCallService`, already depends on `flutter_dialer`. Not touched by this flow. |

## Architecture

### Component Diagram

```
 flutter_dialer (leaf plugin)                flutter_tele (consumer plugin)
+----------------------------+              +--------------------------------+
| Dart: FlutterDialer        |   depends    | Dart: TeleDialer (wraps        |
|  .isDefaultDialer()        |<-------------|   FlutterDialer, unchanged)    |
|  .setDefaultDialer()       |    on        | Dart: TeleCall, flutter_tele_  |
|  .canSetDefaultDialer()    |              |   events EventChannel          |
|  .getCallLog()      [NEW]  |              |                                 |
|  .initialNumber()   [NEW]  |              | Android: TeleService           |
|  .numberStream      [NEW]  |              |  (InCallService, canonical,    |
|                            |              |   already correct, untouched)  |
| Android:                   |              +--------------------------------+
|  FlutterDialerPlugin       |                          ^
|   (+ActivityAware)         |                          |
|  MainActivity              |                          |
|   (launcher + tel: intents)|                          |
|  [TeleService.kt DELETED]  |                          |
+----------------------------+                          |
              ^                                          |
              |  depends on both (demo only)             |
              +------------------------------------------+
                    flutter_dialer_replacement/example
                    5 screens: Status&Setup, Dial Pad,
                    Incoming Call, Active Call, Call Log
```

### Data Flow

- **Role management**: Dart `setDefaultDialer()` -> `MethodChannel
  'flutter_dialer'` -> `FlutterDialerPlugin.handleSetDefaultDialer` ->
  `activity.startActivityForResult(ACTION_CHANGE_DEFAULT_DIALER,
  RC_DEFAULT_PHONE)` -> user interacts with system dialog ->
  `onActivityResult` (via `ActivityPluginBinding.addActivityResultListener`)
  -> resolves the pending `Result` with the real outcome.
- **Launch-intent number**: system `tel:`/`DIAL` intent ->
  `MainActivity.onCreate`/`onNewIntent` -> either answered synchronously
  by `initialNumber()` (cold start) or pushed through `EventChannel
  'flutter_dialer/number_events'` (already-running app) -> example
  app's Dial Pad screen pre-fills the number.
- **Call log**: Dart `getCallLog()` -> `MethodChannel 'flutter_dialer'`
  -> native queries `android.provider.CallLog.Calls` via
  `ContentResolver` (permission already declared:
  `READ_CALL_LOG`, present in the manifest today but currently unused)
  -> returns a `List<Map>` decoded into `CallLogEntry` in Dart.
- **Live call state** (incoming/active call, DTMF, mute, duration):
  entirely `flutter_tele`'s existing `flutter_tele_events` EventChannel
  and `TeleCall` model. `flutter_dialer` has no part in this flow —
  the example app subscribes to `flutter_tele` directly for these two
  screens.

## Interfaces

### New Interfaces (Dart, `flutter_dialer.dart`)

```dart
class FlutterDialer {
  // Existing, signatures unchanged, behavior fixed (see Behavior Specifications):
  static Future<bool> isDefaultDialer();
  static Future<bool> setDefaultDialer();
  static Future<bool> canSetDefaultDialer();

  /// Phone number the app was cold-launched with via a tel:/DIAL intent,
  /// or null if launched normally. Read once per app start; does not
  /// update on subsequent intents while running (see [numberStream]).
  static Future<String?> initialNumber();

  /// Emits a phone number each time the app receives a new tel:/DIAL
  /// intent while already running (MainActivity.onNewIntent).
  static Stream<String> get numberStream;

  /// Returns up to [limit] most recent entries from the system call
  /// log (android.provider.CallLog), newest first. Requires
  /// READ_CALL_LOG permission to already be granted — throws
  /// PlatformException(code: 'PERMISSION_DENIED') otherwise, letting
  /// the caller decide how to prompt (matches existing error-handling
  /// style: catch, don't auto-request).
  static Future<List<CallLogEntry>> getCallLog({int limit = 50});
}

class CallLogEntry {
  final String number;
  final String? cachedName;      // from CallLog provider's CACHED_NAME, display-only
  final DateTime timestamp;
  final Duration duration;
  final CallLogDirection direction;
}

enum CallLogDirection { incoming, outgoing, missed, rejected, blocked }
```

### Modified Interfaces (Android, `FlutterDialerPlugin.kt`)

`FlutterDialerPlugin` gains `ActivityAware` (pattern lifted directly
from `flutter_gsm`'s `ReplaceDialerModule.kt`, confirmed correct by
reading it):

```kotlin
class FlutterDialerPlugin : FlutterPlugin, MethodCallHandler, ActivityAware {
    private var activity: Activity? = null
    private var pendingSetDefaultResult: Result? = null

    override fun onAttachedToActivity(binding: ActivityPluginBinding) {
        activity = binding.activity
        binding.addActivityResultListener { requestCode, resultCode, _ ->
            if (requestCode == RC_DEFAULT_PHONE) {
                pendingSetDefaultResult?.success(resultCode == Activity.RESULT_OK)
                pendingSetDefaultResult = null
                true
            } else false
        }
    }
    // onDetachedFromActivity / onReattachedToActivityForConfigChanges /
    // onDetachedFromActivityForConfigChanges: same pattern as flutter_gsm's copy.

    private fun setDefaultDialer(result: Result) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.M) {
            result.success(true); return
        }
        val tm = context.getSystemService(TELECOM_SERVICE) as TelecomManager
        if (tm.defaultDialerPackage == context.packageName) {
            result.success(true); return   // already default, no dialog needed
        }
        val act = activity
        if (act == null) {
            result.error("NO_ACTIVITY", "setDefaultDialer requires a foreground activity", null)
            return
        }
        pendingSetDefaultResult = result
        act.startActivityForResult(
            Intent(TelecomManager.ACTION_CHANGE_DEFAULT_DIALER)
                .putExtra(TelecomManager.EXTRA_CHANGE_DEFAULT_DIALER_PACKAGE_NAME, context.packageName),
            RC_DEFAULT_PHONE
        )
    }
}
```

`canSetDefaultDialer()` semantics **change** (decision below, Behavior
Specifications): becomes a pure API-level capability check, matching
`flutter_gsm`'s simpler semantics, decoupled from current default-dialer
status.

## Data Models

No new persisted data models. `CallLogEntry` (above) is a transient
read-only projection over Android's existing `CallLog.Calls` content
provider — no local storage, no schema owned by this package.

## Behavior Specifications

### Happy Path — `setDefaultDialer()`

1. App calls `FlutterDialer.setDefaultDialer()`.
2. If already the default dialer: resolves `true` immediately, no
   system dialog shown (avoids an unnecessary interruption — this is a
   deliberate improvement over both the buggy original *and*
   `flutter_gsm`'s copy would otherwise re-trigger the same UX issue).
3. Otherwise: system `ACTION_CHANGE_DEFAULT_DIALER` dialog appears via
   `startActivityForResult`.
4. User accepts -> `onActivityResult(RC_DEFAULT_PHONE, RESULT_OK, _)` ->
   resolves `true`. User declines/back-presses -> resolves `false`.

### Happy Path — `canSetDefaultDialer()` (semantics change, decided)

**Old semantics** (current code): `true` iff API>=23 AND app is *not
already* the default dialer.
**New semantics** (this spec): `true` iff API>=23, full stop — matches
`flutter_gsm`'s implementation, which is simpler and doesn't conflate
"capable of" with "not currently." The "already default, nothing to
do" case is instead handled inside `setDefaultDialer()`'s short-circuit
(above), which is the correct place for it — a status check shouldn't
change meaning based on current status.
**Consequence for the example app's Visual mockups**: the "Set as
Default Dialer" button (`02-visual.md`, Status & Setup screen) stays
visible even when already default; tapping it is now a harmless no-op
(instant `true`) rather than something that needs to be hidden via
`canSet`. Mockup's `if (canSet)` visibility condition is replaced with
`if (!isDefault)` in Specifications — a small, deliberate deviation
from the literal ASCII, justified by this semantics fix. Flagging
explicitly rather than silently diverging from the approved Visual.

### Happy Path — launch-intent number

1. App is not running. User taps a `tel:0102030405` link in another
   app, or the system dialer chooser routes a `DIAL` intent to this
   app (only possible once it holds the role).
2. `MainActivity.onCreate` captures `intent.data` if scheme is `tel`,
   stores it in a static/companion field.
3. Dart calls `FlutterDialer.initialNumber()` once at startup -> reads
   that stored value -> clears it (so a later cold-start read without a
   fresh intent returns `null`, not a stale number).
4. If the app is already running and receives another such intent,
   `onNewIntent` pushes the number through `numberStream` instead
   (no polling needed, no stale-read risk since there's no stored
   state to clear).

### Happy Path — `getCallLog()`

1. Dart calls `getCallLog(limit: 50)`.
2. Native queries `CallLog.Calls.CONTENT_URI` sorted by
   `DATE DESC`, capped at `limit`, mapping `TYPE` (`INCOMING_TYPE` /
   `OUTGOING_TYPE` / `MISSED_TYPE` / `REJECTED_TYPE` / `BLOCKED_TYPE`)
   to `CallLogDirection`.
3. Returns the list; empty list (not an error) when there's no history
   — matches the Visual phase's "Empty" state for the Call Log screen.

### Edge Cases

| Case | Trigger | Expected Behavior |
|------|---------|-------------------|
| `setDefaultDialer()` called with no foreground `Activity` attached (e.g. background isolate) | App calls it before `onAttachedToActivity` fires, or after `onDetachedFromActivity` | `result.error("NO_ACTIVITY", ...)` — caller must retry once the app is foregrounded. Matches Visual's Error state pattern (SnackBar with red background). |
| Two overlapping `setDefaultDialer()` calls | Caller invokes it twice before the first resolves | Second call's `pendingSetDefaultResult` overwrites the first, orphaning the first `Result` (Flutter will just never get a reply for it). Documented as caller's responsibility to not double-invoke — matches how `flutter_gsm`'s reference copy already behaves (no request-dedup there either), not a new gap introduced here. |
| `getCallLog()` without `READ_CALL_LOG` granted | Permission not requested/denied | `PlatformException(code: 'PERMISSION_DENIED')` — maps to Visual's Call Log "Error" state ("Grant Permission" button). `flutter_dialer` does **not** request the permission itself (that's the consuming app's job via `permission_handler` or similar — this package only declares the `<uses-permission>`, consistent with how `CALL_PHONE`/`ANSWER_PHONE_CALLS` are already just declared, not runtime-requested, in the existing manifest). |
| `initialNumber()` called more than once per cold start | App code calls it twice | Second call returns `null` (value cleared after first read) — documented, not a bug; mirrors `uni_links`-style "initial link" packages' established behavior. |
| App holds default-dialer role but does **not** depend on `flutter_tele` | A future consumer only wants role-management (e.g. checking eligibility without handling calls) | Becoming default dialer "succeeds" but literally nothing is bound to receive `InCallService` callbacks — silent no-op for the OS, not a crash. This is now an explicit, documented tradeoff of the leaf-package design (see Constraints below), not an accidental gap — callers who need call handling **must** add `flutter_tele`. |

### Error Handling

| Error | Cause | Response |
|-------|-------|----------|
| `IS_DEFAULT_DIALER_ERROR` / `CAN_SET_DEFAULT_DIALER_ERROR` | `TelecomManager` cast/lookup throws (unchanged from current code) | Existing `result.error(...)` pattern retained as-is |
| `NO_ACTIVITY` | See Edge Cases | New error code |
| `PERMISSION_DENIED` | See Edge Cases | New error code, `getCallLog()` only |

## Dependencies

### Requires

- Nothing new for `flutter_dialer` itself — no new pubspec dependency
  added (leaf constraint preserved).
- `flutter_dialer_replacement/example/pubspec.yaml` requires a new path
  dependency on `flutter_tele` (demo-only).

### Blocks

- `flows/flutter_gsmsip/vdd-flutter_gsmsip-example-uiux`'s "Default
  Dialer status card" AC — unaffected by the `canSetDefaultDialer()`
  semantics change in practice (that flow reads `isDefaultDialer()`
  for status display, not `canSetDefaultDialer()`), but worth a note in
  that flow's status when this one implements.

## Integration Points

### External Systems

- Android `TelecomManager` (`ACTION_CHANGE_DEFAULT_DIALER`,
  `defaultDialerPackage`) — unchanged surface, fixed usage.
- Android `CallLog.Calls` content provider — new integration point.
- Android `Intent` `tel:`/`DIAL` scheme handling — existing manifest
  intent-filters, now actually wired to Dart instead of a dead stub.

### Internal Systems

- `flutter_tele` — consumes `flutter_dialer` (pre-existing, unchanged).
  The example app additionally consumes `flutter_tele` directly for
  Incoming/Active Call screens.

## Testing Strategy

### Unit Tests

- [ ] `FlutterDialerPluginTest.kt` (existing file) — add cases for:
      `setDefaultDialer()` already-default short-circuit,
      `onActivityResult` RESULT_OK/RESULT_CANCELED mapping, `NO_ACTIVITY`
      error when `activity == null`.
- [ ] `canSetDefaultDialer()` — API-level-only semantics (no longer
      reads `defaultDialerPackage`).
- [ ] `getCallLog()` — mapped `CallLogDirection` enum values for each
      Android `TYPE` constant, empty-list-on-no-history case.

### Integration Tests

- [ ] `example/integration_test/plugin_integration_test.dart` (existing
      file) — extend to cover the new Status & Setup "already default"
      no-dialog path, and `initialNumber()` returning `null` on a normal
      (non-`tel:`) launch.

### Manual Verification

- [ ] Real device: trigger `ACTION_CHANGE_DEFAULT_DIALER`, both accept
      and decline the system dialog, confirm `setDefaultDialer()`
      resolves the real outcome (not always `true`).
- [ ] Real device: tap a `tel:` link from another app (e.g. Contacts)
      while this example app is (a) not running, (b) running in
      background — confirm `initialNumber()` and `numberStream`
      fire correctly for each case.
- [ ] Real device with call history present: `getCallLog()` returns
      entries matching the system Phone app's own call log.
- [ ] Confirm (via `adb shell dumpsys package <app>` or manifest
      inspection of the built APK) that only **one** `InCallService`
      entry exists once `flutter_dialer`'s is deleted and `flutter_tele`
      is present — verifies the manifest-merge conflict is actually gone.

## Migration / Rollout

- **Breaking behavioral change** (flagged in Requirements' Constraints):
  any existing caller relying on `setDefaultDialer()` always returning
  `true` will now see real `false` results on decline. No Dart method
  signature changes, so this doesn't break compilation — only runtime
  behavior for callers not already handling the `false` case.
- **`canSetDefaultDialer()` semantics change**: callers using it to
  decide "should I show the button" need to also check `!isDefault` if
  they want the old hide-when-already-default UX — documented in the
  Behavior Specifications entry above and called out for anyone
  integrating this package outside the example app.
- Deleting `TeleService.kt` and its manifest entry is safe for any app
  that already also depends on `flutter_tele` (the manifest-merge
  conflict meant `flutter_dialer`'s copy was never reliably the one
  actually bound anyway). For a hypothetical app depending on
  `flutter_dialer` **without** `flutter_tele`, this removes the only
  `InCallService` it had — but per the Edge Cases table, that
  `InCallService` was never wired to anything in Dart regardless, so no
  functional behavior is lost, only a non-functional stub.

## Open Design Questions

- [ ] Should `getCallLog()` support pagination/`before` cursor beyond a
      flat `limit`, or is a single capped fetch sufficient for v1? This
      flow's working assumption: flat `limit` is sufficient (Visual's
      Call Log mockup shows a simple list, no "load more" UI) — flag if
      Anton wants paging designed now instead of later.

---

## Approval

- [x] Reviewed by: Anton
- [x] Approved on: 2026-08-31
- [x] Notes: Approved as drafted, no changes requested.
