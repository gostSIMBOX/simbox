# Implementation Plan: flutter_dialer

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-08-31
> Specifications: [03-specifications.md](03-specifications.md)

## Summary

Four phases: (1) fix the native Kotlin plugin — `ActivityAware` +
callback-timing fix, `canSetDefaultDialer()` semantics change, delete
`TeleService.kt`/manifest entry; (2) add the two new Dart-facing
capabilities (launch-intent number, call log) end-to-end, native then
Dart; (3) rebuild the example app's 5 screens per `02-visual.md`,
wiring in `flutter_tele` as a new demo-only dependency; (4) tests +
manual device verification. Order matters: the library's native/Dart
surface must exist before the example app can consume it.

## Task Breakdown

### Phase 1: Fix the role-management plugin

#### Task 1.1: Add `ActivityAware` + fix `setDefaultDialer()` callback timing
- **Description**: Port the `ActivityAware` + `addActivityResultListener`
  pattern from `flutter_gsm`'s `ReplaceDialerModule.kt` into
  `FlutterDialerPlugin.kt`. Add the already-default short-circuit
  (`result.success(true)` without showing the system dialog). Add
  `NO_ACTIVITY` error path when no activity is attached.
- **Files**:
  - `libsFlutter/flutter_dialer_replacement/android/src/main/kotlin/org/tele/flutter_dialer/FlutterDialerPlugin.kt` - Modify
- **Dependencies**: None
- **Verification**: `FlutterDialerPluginTest.kt` cases pass (Task 4.1);
  manual device test (Task 4.3) confirms real accept/decline outcomes.
- **Complexity**: Medium

#### Task 1.2: Change `canSetDefaultDialer()` semantics
- **Description**: Remove the `defaultDialerPackage != packageName`
  check; return `Build.VERSION.SDK_INT >= M` only, per Specifications'
  decided semantics change.
- **Files**:
  - `libsFlutter/flutter_dialer_replacement/android/src/main/kotlin/org/tele/flutter_dialer/FlutterDialerPlugin.kt` - Modify
- **Dependencies**: None (independent of 1.1, same file)
- **Verification**: Unit test — returns `true` on API 23+ regardless of
  current default-dialer status.
- **Complexity**: Low

#### Task 1.3: Delete `TeleService.kt` and its manifest entry
- **Description**: Remove the file and the corresponding `<service>`
  block from `AndroidManifest.xml`, resolving the duplicate
  `InCallService` intent-filter conflict with `flutter_tele`.
- **Files**:
  - `libsFlutter/flutter_dialer_replacement/android/src/main/kotlin/org/tele/flutter_dialer/TeleService.kt` - Delete
  - `libsFlutter/flutter_dialer_replacement/android/src/main/AndroidManifest.xml` - Modify (remove `<service>` block)
- **Dependencies**: None
- **Verification**: `adb shell dumpsys package` on a build that also
  depends on `flutter_tele` shows exactly one `InCallService` entry
  (Task 4.3).
- **Complexity**: Low

### Phase 2: Add launch-intent and call-log capabilities

#### Task 2.1: Wire `tel:`/`DIAL` intents to Dart (native side)
- **Description**: Replace `MainActivity.onNewIntent`'s dead stub.
  Capture the number on `onCreate`/`onNewIntent`; add a new
  `EventChannel('flutter_dialer/number_events')` in
  `FlutterDialerPlugin.kt` (or a small dedicated handler class) that
  `MainActivity` pushes to when already running; add a
  `getInitialNumber` method-channel handler that reads-and-clears the
  stored cold-start value.
- **Files**:
  - `libsFlutter/flutter_dialer_replacement/android/src/main/kotlin/org/tele/flutter_dialer/MainActivity.kt` - Modify
  - `libsFlutter/flutter_dialer_replacement/android/src/main/kotlin/org/tele/flutter_dialer/FlutterDialerPlugin.kt` - Modify (add EventChannel + `getInitialNumber` method)
- **Dependencies**: None
- **Verification**: Manual device test (Task 4.3) — cold launch via
  `tel:` link and warm launch while running both deliver the number.
- **Complexity**: Medium

#### Task 2.2: Add `getCallLog()` (native side)
- **Description**: Query `CallLog.Calls.CONTENT_URI` via
  `ContentResolver`, sorted by `DATE DESC`, capped at the requested
  `limit`, mapping Android's `TYPE` constant to the direction string
  the Dart side will decode into `CallLogDirection`.
- **Files**:
  - `libsFlutter/flutter_dialer_replacement/android/src/main/kotlin/org/tele/flutter_dialer/FlutterDialerPlugin.kt` - Modify (add `getCallLog` method-channel handler)
- **Dependencies**: None
- **Verification**: Unit test with a fake `ContentResolver`/cursor
  (Task 4.1); manual device test against real call history (Task 4.3).
- **Complexity**: Medium

#### Task 2.3: Add Dart-side API surface
- **Description**: Add `initialNumber()`, `numberStream`,
  `getCallLog()`, and the `CallLogEntry`/`CallLogDirection` types to
  `flutter_dialer.dart`. Wire through `flutter_dialer_platform_interface.dart`
  and `flutter_dialer_method_channel.dart` following the existing
  `getPlatformVersion` pattern (platform-interface method +
  method-channel implementation).
- **Files**:
  - `libsFlutter/flutter_dialer_replacement/lib/flutter_dialer.dart` - Modify
  - `libsFlutter/flutter_dialer_replacement/lib/flutter_dialer_platform_interface.dart` - Modify
  - `libsFlutter/flutter_dialer_replacement/lib/flutter_dialer_method_channel.dart` - Modify
- **Dependencies**: Task 2.1, Task 2.2 (native handlers must exist to call)
- **Verification**: `dart analyze` clean; example app (Phase 3) actually
  calls these successfully.
- **Complexity**: Medium

### Phase 3: Rebuild the example app

#### Task 3.1: Add `flutter_tele` path dependency to the example app
- **Description**: Add `flutter_tele` as a path dependency in
  `example/pubspec.yaml` (demo-only — does not affect the library's own
  leaf-package `pubspec.yaml`).
- **Files**:
  - `libsFlutter/flutter_dialer_replacement/example/pubspec.yaml` - Modify
- **Dependencies**: None
- **Verification**: `flutter pub get` in `example/` resolves cleanly.
- **Complexity**: Low

#### Task 3.2: Status & Setup screen (refine existing)
- **Description**: Keep the existing two-card layout; add the Loading
  spinner state, the "cannot set / unsupported OS" state, and switch
  the "Set as Default Dialer" button's visibility condition from
  `if (canSet)` to `if (!isDefault)` per the `canSetDefaultDialer()`
  semantics change. Add "Go to Dial Pad" / "Go to Call Log" buttons,
  visible only when `isDefault` is true.
- **Files**:
  - `libsFlutter/flutter_dialer_replacement/example/lib/main.dart` - Modify (or split into `lib/screens/status_screen.dart` — see Task 3.6)
- **Dependencies**: Phase 1 (behavior it displays), Phase 2 (nav targets exist)
- **Verification**: Manual run — matches `02-visual.md`'s Status &
  Setup mockup and all 4 documented states.
- **Complexity**: Low

#### Task 3.3: Dial Pad screen
- **Description**: New screen — 12-key grid (reusable component per
  Task 3.7), number display, backspace, call button. Prefills from
  `FlutterDialer.initialNumber()`/`numberStream` when arriving via a
  `tel:` intent, or from a tapped Call Log entry (Task 3.5). "Calling..."
  transitional state subscribes to `flutter_tele`'s `flutter_tele_events`
  to detect connection and navigate to Active Call.
- **Files**:
  - `libsFlutter/flutter_dialer_replacement/example/lib/screens/dial_pad_screen.dart` - Create
- **Dependencies**: Task 2.3 (Dart API), Task 3.1 (flutter_tele available), Task 3.7 (shared grid component)
- **Verification**: Manual run — matches `02-visual.md`'s Dial Pad
  mockup and both states (Empty, Dialing).
- **Complexity**: Medium

#### Task 3.4: Incoming Call and Active Call screens
- **Description**: Subscribe to `flutter_tele`'s `TeleCall` stream.
  Incoming Call shows caller-ID (via `READ_CONTACTS` lookup keyed on
  `remoteNumber`, display-only) with Answer/Decline. Active Call shows
  duration (from `TeleCall.getConnectDuration()`, already implemented),
  mute/speaker/keypad controls, End Call. DTMF keypad toggle reuses the
  Task 3.7 grid component inline.
- **Files**:
  - `libsFlutter/flutter_dialer_replacement/example/lib/screens/incoming_call_screen.dart` - Create
  - `libsFlutter/flutter_dialer_replacement/example/lib/screens/active_call_screen.dart` - Create
- **Dependencies**: Task 3.1, Task 3.7
- **Verification**: Manual run against a real or emulated incoming
  call — matches `02-visual.md`'s two screens and their sub-states
  (no-caller-ID-match, unknown number, call-ended).
- **Complexity**: High (real device/emulator call required to verify;
  `flutter_tele` event shapes may need small adjustments discovered only
  at integration time)

#### Task 3.5: Call Log screen
- **Description**: New screen — list view backed by
  `FlutterDialer.getCallLog()`, using the Task 3.6 `CallListItem`
  component. Empty/Loading/Error (permission) states per
  `02-visual.md`. Tapping an entry navigates to Dial Pad pre-filled
  with that number.
- **Files**:
  - `libsFlutter/flutter_dialer_replacement/example/lib/screens/call_log_screen.dart` - Create
- **Dependencies**: Task 2.3
- **Verification**: Manual run — matches `02-visual.md`'s Call Log
  mockup and all 3 states.
- **Complexity**: Medium

#### Task 3.6: Extract `CallListItem` component
- **Description**: Reusable row widget per `02-visual.md`'s "Component:
  Call List Item" — name/number, direction icon, timestamp.
- **Files**:
  - `libsFlutter/flutter_dialer_replacement/example/lib/widgets/call_list_item.dart` - Create
- **Dependencies**: None
- **Verification**: Used by Task 3.5.
- **Complexity**: Low

#### Task 3.7: Extract `DialPadGrid` component
- **Description**: Reusable 4x3 digit grid per `02-visual.md`'s
  "Component: Dial Pad Grid" — used full-screen (Task 3.3) and inline
  for DTMF (Task 3.4).
- **Files**:
  - `libsFlutter/flutter_dialer_replacement/example/lib/widgets/dial_pad_grid.dart` - Create
- **Dependencies**: None
- **Verification**: Used by Tasks 3.3 and 3.4 without duplication.
- **Complexity**: Low

#### Task 3.8: Wire up navigation
- **Description**: Replace the example's single-screen `MyHomePage`
  with named routes (or a simple `Navigator.push` flow) connecting all
  5 screens per `02-visual.md`'s Flow diagram, including the
  system-triggered (non-user-nav) jump to Incoming Call.
- **Files**:
  - `libsFlutter/flutter_dialer_replacement/example/lib/main.dart` - Modify
- **Dependencies**: Tasks 3.2–3.5
- **Verification**: Manual run through the full flow — Status & Setup
  -> Dial Pad -> (Active Call) -> Call Log -> Dial Pad, plus incoming
  call interrupting whatever screen is active.
- **Complexity**: Medium

### Phase 4: Testing & Verification

#### Task 4.1: Native unit tests
- **Description**: Extend `FlutterDialerPluginTest.kt` per
  Specifications' Testing Strategy — already-default short-circuit,
  `onActivityResult` mapping, `NO_ACTIVITY` error, `canSetDefaultDialer()`
  new semantics, `getCallLog()` TYPE-to-direction mapping and
  empty-list case.
- **Files**:
  - `libsFlutter/flutter_dialer_replacement/android/src/test/kotlin/org/tele/flutter_dialer/FlutterDialerPluginTest.kt` - Modify
- **Dependencies**: Tasks 1.1, 1.2, 2.1, 2.2
- **Verification**: `./gradlew test` passes.
- **Complexity**: Medium

#### Task 4.2: Integration test extension
- **Description**: Extend `example/integration_test/plugin_integration_test.dart`
  per Specifications — already-default no-dialog path, `initialNumber()`
  null-on-normal-launch case.
- **Files**:
  - `libsFlutter/flutter_dialer_replacement/example/integration_test/plugin_integration_test.dart` - Modify
- **Dependencies**: Phase 2, Phase 3
- **Verification**: `flutter test integration_test` passes on a
  connected device/emulator.
- **Complexity**: Medium

#### Task 4.3: Manual device verification
- **Description**: Run through Specifications' full Manual Verification
  checklist on a real Android device: accept/decline default-dialer
  dialog, cold/warm `tel:` intent launch, real call log match against
  system Phone app, and the single-`InCallService` manifest check.
- **Files**: None (verification only)
- **Dependencies**: All prior tasks
- **Verification**: Checklist in `03-specifications.md`'s "Manual
  Verification" section, all boxes checked.
- **Complexity**: Medium

## Dependency Graph

```
1.1 ─┬─→ 4.1 ─┐
1.2 ─┤        │
1.3 ─┘        │
              │
2.1 ─┬─→ 2.3 ─┼─→ 3.2 ─┬─→ 3.8 ─→ 4.2 ─→ 4.3
2.2 ─┘        │        │
              │        │
3.1 ──────────┼─→ 3.3 ─┤ (needs 3.7)
              │        │
3.6 ──────────┼─→ 3.5 ─┤
              │        │
3.7 ──────────┴─→ 3.4 ─┘ (needs 3.1)
```

## File Change Summary

| File | Action | Reason |
|------|--------|--------|
| `android/.../FlutterDialerPlugin.kt` | Modify | ActivityAware, callback fix, canSet semantics, +getCallLog, +number EventChannel |
| `android/.../MainActivity.kt` | Modify | Replace dead tel:/DIAL stub with real capture + push to plugin |
| `android/.../TeleService.kt` | Delete | Superseded by flutter_tele's canonical InCallService |
| `android/src/main/AndroidManifest.xml` | Modify | Remove `<service>` block for TeleService |
| `android/src/test/.../FlutterDialerPluginTest.kt` | Modify | New test cases for all behavior changes |
| `lib/flutter_dialer.dart` | Modify | +initialNumber, +numberStream, +getCallLog, +CallLogEntry/CallLogDirection |
| `lib/flutter_dialer_platform_interface.dart` | Modify | Platform-interface methods for new APIs |
| `lib/flutter_dialer_method_channel.dart` | Modify | Method-channel implementation for new APIs |
| `example/pubspec.yaml` | Modify | +flutter_tele path dependency (demo-only) |
| `example/lib/main.dart` | Modify | Becomes navigation shell instead of single screen |
| `example/lib/screens/status_screen.dart` | Create | Extracted from current main.dart, refined states |
| `example/lib/screens/dial_pad_screen.dart` | Create | New |
| `example/lib/screens/incoming_call_screen.dart` | Create | New |
| `example/lib/screens/active_call_screen.dart` | Create | New |
| `example/lib/screens/call_log_screen.dart` | Create | New |
| `example/lib/widgets/call_list_item.dart` | Create | Shared component |
| `example/lib/widgets/dial_pad_grid.dart` | Create | Shared component |
| `example/integration_test/plugin_integration_test.dart` | Modify | New test cases |

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| `flutter_tele`'s `TeleCall`/event shapes don't map cleanly onto the Incoming/Active Call mockups (e.g. SIP-flavored fields like `remoteUri` parsing) | Medium | Medium | Task 3.4 flagged High complexity precisely for this; budget time to adapt the example's UI to whatever `flutter_tele` actually emits rather than assuming a clean fit |
| Deleting `TeleService.kt` breaks a hypothetical consumer that uses `flutter_dialer` without `flutter_tele` and relied on *some* `InCallService` existing, even a non-functional one | Low | Low | Documented explicitly in Specifications' Migration/Rollout section as an accepted, justified tradeoff — no known such consumer exists in this repo |
| `getCallLog()` permission handling surprises the example app if `READ_CALL_LOG` isn't granted at runtime (API 23+ requires runtime request, manifest declaration alone isn't enough) | Medium | Low | Example app's Call Log Error state (already in Visual) handles this; Task 3.5 must actually implement the "Grant Permission" button, not just display the message |
| `startActivityForResult` deprecation on newer `androidx.activity` — Google recommends `ActivityResultLauncher` now | Low | Low | Out of scope for this flow — matches the pattern already proven correct in `flutter_gsm`'s reference implementation; not introducing a new deprecated API, just fixing a bug with the same API family already in use |

## Rollback Strategy

1. All changes are additive or isolated to `flutter_dialer_replacement`'s
   own package and its own `example/` app — no other package is
   modified. `flutter_tele` is read-only throughout this flow.
2. If `setDefaultDialer()`'s behavior change proves disruptive to an
   unknown external consumer, revert Task 1.1 only — Tasks 1.2/1.3/
   Phase 2/Phase 3 are independent and don't depend on the callback
   fix's specific implementation, only on the method's continued
   existence.
3. `TeleService.kt` deletion (Task 1.3) can be reverted by restoring the
   file and manifest entry from git history if an undiscovered consumer
   depended on it existing (even if non-functional).

## Checkpoints

After each phase, verify:

- [ ] Phase 1: `./gradlew test` passes; manual accept/decline test on
      a device confirms real (not always-`true`) results.
- [ ] Phase 2: New Dart methods callable from a throwaway test
      `main()`; `dart analyze` clean.
- [ ] Phase 3: Example app runs on a device; all 5 screens reachable
      and visually match `02-visual.md`.
- [ ] Phase 4: All automated tests pass; manual verification checklist
      complete.

## Open Implementation Questions

- [ ] Exact `EventChannel` vs. re-using the existing `MethodChannel`
      with a callback-style bridge for `numberStream` — Specifications
      names it `flutter_dialer/number_events` as a new EventChannel;
      confirm during Task 2.1 that a second channel is preferable to
      multiplexing onto the existing `flutter_dialer` MethodChannel (it
      is, for a stream — but flagged since it's a small API-surface
      decision not spelled out further in Specifications).

---

## Approval

- [x] Reviewed by: Anton
- [x] Approved on: 2026-08-31
- [x] Notes: Approved as drafted, no changes requested.
