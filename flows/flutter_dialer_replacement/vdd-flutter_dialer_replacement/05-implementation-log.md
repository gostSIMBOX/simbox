# Implementation Log: flutter_dialer

> Started: 2026-08-31
> Plan: [04-plan.md](04-plan.md)

## Progress Tracker

| Task | Status | Notes |
|------|--------|-------|
| 1.1 ActivityAware + callback fix | Done | |
| 1.2 canSetDefaultDialer semantics | Done | |
| 1.3 Delete TeleService.kt + manifest | Done | |
| 2.1 tel:/DIAL intents to Dart | Done | |
| 2.2 getCallLog (native) | Done | |
| 2.3 Dart API surface | Done | Deviation: bypassed platform_interface (see below) |
| 3.1 flutter_tele path dependency | Done | Also added dependency_overrides (flutter_dialer path, plugin_platform_interface) + permission_handler |
| 3.2 Status & Setup refine | Done | |
| 3.3 Dial Pad screen | Done | |
| 3.4 Incoming/Active Call screens | Done | DTMF keypad UI-only, flutter_tele has no send-tone API (flagged) |
| 3.5 Call Log screen | Done | |
| 3.6 CallListItem component | Done | |
| 3.7 DialPadGrid component | Done | |
| 3.8 Navigation wiring | Done | Global incoming-call listener via GlobalKey<NavigatorState> in main.dart |
| 4.1 Native unit tests | Done | Required a testability seam + build.gradle fix, see below |
| 4.2 Integration test extension | Done | Also fixed stale test/widget_test.dart (unrelated pre-existing breakage) |
| 4.3 Manual device verification | **Blocked — needs Anton** | No Android device/emulator attached in this environment (`adb devices` empty) |

## Session Log

### Session 2026-08-31 - Claude

**Started at**: Phase 1, Task 1.1
**Context**: Requirements, Visual, Specifications, and Plan all approved
same session. Beginning Implementation from a clean read of the actual
current code (not assumptions).

#### Completed

- **Task 1.1**: Added `ActivityAware` to `FlutterDialerPlugin.kt`,
  ported the `addActivityResultListener` pattern from `flutter_gsm`'s
  `ReplaceDialerModule.kt`. `setDefaultDialer()` now calls
  `startActivityForResult` and resolves the real `Activity.RESULT_OK`/
  cancelled outcome in `onActivityResult`, instead of always resolving
  `true` immediately.
  - Files changed: `android/src/main/kotlin/org/tele/flutter_dialer/FlutterDialerPlugin.kt`
  - Verified by: Kotlin compiles (Gradle `assembleDebug` succeeded, see below).

- **Task 1.2**: `canSetDefaultDialer()` changed to a pure API-level
  check (`SDK_INT >= M`), decoupled from current default-dialer status.
  `setDefaultDialer()` gained the already-default short-circuit
  (`result.success(true)` without showing the system dialog) to absorb
  the behavior the old `canSetDefaultDialer()` used to gate.
  - Files changed: same file as above.
  - Verified by: same build.

- **Task 1.3**: Deleted `TeleService.kt` and its `<service>` block in
  `AndroidManifest.xml`. Confirmed via `grep` that no other source file
  in the package referenced the class (only docs under `flows/` did).
  - Files changed:
    `android/src/main/kotlin/org/tele/flutter_dialer/TeleService.kt` (deleted),
    `android/src/main/AndroidManifest.xml`
  - Verified by: same build; `grep -rl TeleService` shows no remaining
    code references.
  - Discovery: found `flows/tdd-incall-service/` — a pre-existing,
    separate TDD flow in this same package planning work *on* the now-
    deleted `TeleService`. Flagging as superseded in `_status.md`, not
    deleting (kept for historical reference, same policy as the other
    superseded docs this flow already tracks).

- **Task 2.1**: Replaced `MainActivity.kt`'s dead `tel:`/`DIAL` stub.
  `onCreate` now captures a cold-start number into
  `FlutterDialerPlugin.initialNumber` (companion `var`); `onNewIntent`
  pushes subsequent numbers through a new
  `EventChannel('flutter_dialer/number_events')` via a static
  `onNewNumberIntent()` bridge method. Added `getInitialNumber` method-
  channel handler (read-and-clear semantics, matches Specifications).
  - Files changed: `MainActivity.kt`, `FlutterDialerPlugin.kt`
  - Verified by: same build.

- **Task 2.2**: Added `getCallLog` method-channel handler — queries
  `CallLog.Calls.CONTENT_URI` via `ContentResolver`, sorted `DATE DESC`,
  capped at the requested `limit`, mapping Android's `TYPE` constant to
  a direction string (`incoming`/`outgoing`/`missed`/`rejected`/
  `blocked`/`unknown`). `SecurityException` maps to a
  `PERMISSION_DENIED` error code per Specifications.
  - Files changed: `FlutterDialerPlugin.kt`
  - Verified by: same build.

- **Task 2.3**: Added Dart-side `initialNumber()`, `numberStream`,
  `getCallLog()`, plus `CallLogEntry`/`CallLogDirection` types, to
  `lib/flutter_dialer.dart`.
  - Files changed: `lib/flutter_dialer.dart`
  - Verified by: `flutter analyze lib` — 0 errors (8 pre-existing
    `avoid_print` info-level lints, same style as the 3 existing
    methods, not new).

- **Pre-existing blocker fixed (out-of-plan, environment-level)**:
  `pubspec.yaml` declared `plugin_platform_interface: ^3.0.0`, but no
  3.x version of that package has ever been published (confirmed via
  pub.dev API — latest is 2.1.8). This blocked `flutter pub get`
  entirely, so nothing could be verified. Found the exact same bug
  already diagnosed and fixed in `flutter_gsm`/`flutter_gsmsip`'s
  `pubspec.yaml` in an earlier session, with a comment explaining it.
  Applied the same one-line fix (`^2.1.8`) here, since it's a clearly-
  broken constraint (not a design choice) blocking all verification —
  not scope creep on the feature itself.
  - Files changed: `pubspec.yaml`
  - Note: `flutter_gsm`'s own `pubspec.yaml` has a `dependency_overrides`
    path pointing at `../flutter_dialer`, but the actual directory is
    `flutter_dialer_replacement` (renamed at some point) — that path is
    stale/broken. Out of this flow's scope (it's `flutter_gsm`'s file),
    flagging in `_status.md` for whoever opens that package's flow.

- **Build verification**: `cd example && flutter build apk --debug`
  succeeded end-to-end (Gradle `assembleDebug`, ~47s) — confirms all
  Kotlin changes (ActivityAware, EventChannel, CallLog query, deleted
  TeleService/manifest entry) compile and link correctly against real
  Android APIs, not just visual inspection.

#### Deviations from Plan

- **Task 2.3**: Plan said to wire new methods through
  `flutter_dialer_platform_interface.dart` and
  `flutter_dialer_method_channel.dart`, "following the existing
  `getPlatformVersion` pattern." On inspection, that pattern is
  actually unused boilerplate — all three *real* existing API methods
  (`isDefaultDialer`/`setDefaultDialer`/`canSetDefaultDialer`) bypass
  platform_interface entirely and call `MethodChannel` directly inside
  the static `FlutterDialer` class. Followed that real, established
  convention instead for consistency; left `platform_interface`/
  `method_channel` files untouched. Flagging explicitly per this flow's
  "document deviations" rule.

#### Discoveries

- `flutter_tele`'s `pubspec.yaml` already depends on `flutter_dialer`
  (confirmed during Specifications, reconfirmed still true here) — no
  new dependency direction needed for the leaf-package constraint.
- `flutter_gsm`/`flutter_gsmsip` had already independently discovered
  and fixed the exact `plugin_platform_interface: ^3.0.0` bug this
  session hit fresh in `flutter_dialer` — cross-package confirmation
  this is a real, repo-wide, previously-known issue.

#### Phase 3 (example app) — completed same session

- Read `flutter_tele`'s `TeleService.kt` `onCallAdded`/`Call.Callback`
  code (not just `call.dart`'s model) and its `endpoint.dart` — this
  resolved the Risk Assessment's flagged concern: the InCallService
  code path (which is what matters for a default-dialer app) uses
  plain Android telecom state strings (`INCOMING`/`RINGING`/`ACTIVE`/
  `HOLDING`/`DIALING`/`CONNECTING`/`DISCONNECTED`), not the SIP/PJSIP
  states also present in the shared `TeleCall` model (those come from a
  separate PJSIP call path in the same package, unrelated to
  InCallService calls). `TeleCall.isTerminated()` checks specifically
  for `'PJSIP_INV_STATE_DISCONNECTED'`, so it does **not** correctly
  detect termination for InCallService-sourced calls — worked around by
  checking `state == 'DISCONNECTED'` directly in
  `active_call_screen.dart`/`dial_pad_screen.dart` rather than relying
  on that helper. This is `flutter_tele`'s own latent bug; not fixed
  here (read-only per this flow's constraint), just avoided.
- `flutter_tele`'s `TeleEndpoint` (`endpoint.dart`) already exposes
  exactly what was needed: `.on('call_received'|'call_changed'|
  'call_terminated')` broadcast streams, `makeCall`/`answerCall`/
  `declineCall`/`hangupCall`/`muteCall`/`unMuteCall`/`useSpeaker`/
  `useEarpiece`. **Gap found**: no DTMF/send-tone method exists at all
  in `flutter_tele`'s method channel. Active Call's inline keypad
  (Task 3.4) is built to match `02-visual.md`'s layout but shows a
  SnackBar stating tones aren't actually sent, rather than silently
  faking the feature — flagged in-code and here, not hidden.
- Added `permission_handler: ^11.3.1` to `example/pubspec.yaml`
  (demo-only) for the Call Log screen's "Grant Permission" action,
  since `getCallLog()` deliberately doesn't request `READ_CALL_LOG`
  itself (Specifications' Edge Cases table). Matched the exact version
  already used in `flutter_gsm`/`flutter_gsmsip`.
- Created `lib/tele.dart` — a single app-wide `TeleEndpoint` instance.
  Not in the original plan's file list; a lightweight addition (no new
  package/pattern) to avoid threading the endpoint through every
  screen's constructor for what is a single-instance, whole-app
  concern in a demo app.
- Global incoming-call navigation (`02-visual.md`'s "system-triggered
  jump to Incoming Call") wired via a `GlobalKey<NavigatorState>` in
  `main.dart`, listening to `teleEndpoint.on('call_received')` at the
  app root — matches the plan's Task 3.8 description.
- **Build-verified twice**: `flutter analyze lib` → 0 issues (after
  fixing 2 trivial style lints it initially flagged); `flutter build
  apk --debug` succeeded end-to-end with `flutter_tele` now wired in,
  confirming the full dependency graph (`flutter_dialer` +
  `flutter_tele` + `permission_handler`, with the `dependency_overrides`
  for the local path and the `plugin_platform_interface` version bug)
  resolves and compiles.

#### Phase 4 (tests) — completed same session, except 4.3

- **Task 4.1**: Replaced the pre-existing `FlutterDialerPluginTest.kt`
  (its one test called a `getPlatformVersion` method-channel case that
  `onMethodCall` doesn't even handle — dead boilerplate from
  `flutter create --template=plugin`, never actually passing) with 7
  real tests covering Specifications' Testing Strategy: already-default
  short-circuit, `NO_ACTIVITY` error, `onActivityResult` OK/cancelled
  mapping, `canSetDefaultDialer()`'s new API-level-only semantics,
  `getCallLog()`'s empty-list and `PERMISSION_DENIED` cases.
  - **Discovery mid-task**: this module has no Robolectric configured,
    so `android.os.Build.VERSION.SDK_INT` reads as a real static field
    with no shadowing — always `0` under the plain JVM unit-test stub
    jar. Every API-gated branch silently took the "below Android M"
    path regardless of Mockito stubbing, which made an early "passing"
    test pass for the wrong reason (see below). Fixed by adding a
    minimal testability seam — `FlutterDialerPlugin.sdkIntForTesting:
    Int?` (test-only override, null in production, falls back to the
    real field) — rather than pulling in Robolectric as a new
    dependency for one field.
  - Also hit and fixed: `android.util.Log.d/e` throw
    `RuntimeException("not mocked")` under the same stub jar. Fixed by
    adding `testOptions.unitTests.returnDefaultValues = true` to
    `android/build.gradle` (standard, minimal fix for this exact class
    of error, not a new pattern).
  - Also hit and fixed: a classic Mockito gotcha — evaluating one
    mock's getter (`context.packageName`) as an argument expression
    inside another mock's `when(...).thenReturn(...)` chain corrupts
    Mockito's stubbing state (`UnfinishedStubbingException`). Fixed by
    extracting the value to a local `val` first.
  - Files changed: `FlutterDialerPluginTest.kt`, `FlutterDialerPlugin.kt`
    (added the `sdkInt`/`sdkIntForTesting` seam, replaced 3 direct
    `Build.VERSION.SDK_INT` reads with it), `android/build.gradle`.
  - Verified by: `./gradlew :flutter_dialer:testDebugUnitTest` — all 7
    tests pass. Re-ran `flutter build apk --debug` afterward to confirm
    the seam didn't affect the production build — still succeeds.

- **Task 4.2**: Rewrote `plugin_integration_test.dart` — the existing
  version called `FlutterDialer().getPlatformVersion()`, an instance
  method that doesn't exist on `FlutterDialer` (a static-only class); it
  would not have compiled, let alone run. New version has 4 tests per
  Specifications: `isDefaultDialer`/`canSetDefaultDialer` round-trip,
  already-default short-circuit (conditional on the test device's
  actual state), `initialNumber()` null-on-normal-launch, `getCallLog()`
  list-or-`PERMISSION_DENIED` (both outcomes valid, device-state
  dependent). Verified via `flutter analyze integration_test` (0
  issues) — cannot execute without a device (see Task 4.3).
  - **Unrelated pre-existing breakage also fixed**: `test/widget_test.dart`
    searched for text (`'Running on:'`) that never existed in this
    app's actual UI — also dead boilerplate, would always fail if run.
    Rewrote as a real smoke test (mocks the `flutter_dialer`
    MethodChannel, pumps `MyApp`, asserts the Status & Setup screen
    renders). Verified: `flutter test test/widget_test.dart` passes.
  - Files changed: `integration_test/plugin_integration_test.dart`,
    `test/widget_test.dart`.

- **Task 4.3**: `adb devices` returns empty — no Android device or
  emulator is attached in this environment. **Left pending for Anton**
  to run `03-specifications.md`'s Manual Verification checklist:
  accept/decline the real system dialog, cold/warm `tel:` intent
  launch, real call-log match, and the single-`InCallService` manifest
  check.

#### Final verification pass

- `flutter analyze` (whole `example/` project: `lib/`, `test/`,
  `integration_test/`) — 0 issues.
- `flutter analyze lib` (library itself) — 0 errors (8 pre-existing
  `avoid_print` info lints, unchanged style).
- `flutter test test/widget_test.dart` — passes.
- `./gradlew :flutter_dialer:testDebugUnitTest` — 7/7 pass.
- `flutter build apk --debug` (example app, arm64) — succeeds, run
  three times across this session as changes accumulated.

#### Post-Phase-4: package rename reconciliation + design system pass

- **Package renamed mid-session**: `pubspec.yaml`'s `name:` changed
  from `flutter_dialer` to `flutter_dialer_replacement` (matching the
  directory name, `version:` to `1.0.0`, `homepage:` updated). This
  broke `pub get` everywhere the old name was referenced as an import
  or dependency key — pub requires the declared `name:` to match the
  key any dependent uses. Fixed every actual dependent in this flow's
  build path: `flutter_tele/pubspec.yaml` (dependency key + version
  constraint) and `flutter_tele/lib/src/dialer.dart` (import) — the one
  sibling package genuinely required for the example app to build —
  plus this package's own `example/pubspec.yaml` (dependency +
  `dependency_overrides` keys), all example screen/widget imports, both
  pre-existing top-level `test/*.dart` files, `integration_test/
  plugin_integration_test.dart`, and `README.md`'s two usage examples.
  - **Deliberately not touched**: `flutter_gsm` and `flutter_gsmsip`
    also reference the old name in their own `pubspec.yaml`/
    `pubspec.lock`/source, but neither is part of this flow's build
    graph (this example depends only on `flutter_dialer_replacement` +
    `flutter_tele`) — fixing them is out of scope, already noted as a
    follow-up in `_status.md`.
  - **Also fixed while touching these files**: two more pieces of
    stale `flutter create --template=plugin` boilerplate discovered in
    `test/flutter_dialer_test.dart` and `test/flutter_dialer_method_channel_test.dart`
    — both called `FlutterDialer().getPlatformVersion()`, an instance
    method that doesn't exist on the static-only `FlutterDialer` class
    (same class of bug as the two test files fixed in Task 4.2).
    Rewrote the affected test to exercise the platform-interface swap
    mechanism on its own terms instead.
  - Verified: `flutter pub get` (library + example) resolves clean;
    `flutter analyze` clean on both; `flutter test test/` (library, 3
    tests) and `flutter test test/widget_test.dart` (example) pass;
    `flutter build apk --debug` succeeds; native unit tests still 7/7.

- **Applied NativeMind Design System to the example app's UI**, per
  Anton's direction to use the `nativemind-designsystem` skill for
  UI/UX work. Since the skill ships CSS tokens + React components (no
  Dart), translated the relevant values by hand into
  `example/lib/design/{app_colors,app_typography,app_spacing}.dart` —
  neutral + semantic palette, Blue/Pro accent (the default colorway;
  this app isn't tied to any VPN tier so it doesn't need theme
  switching), 8-role type scale, 4pt spacing grid, single card shadow,
  10px card radius — plus a `GradientButton` widget reserving the one
  accent gradient for a screen's single primary CTA, per the DS's "one
  gradient per build" rule.
  - Wired into `main.dart`'s `ThemeData` (scaffold background, card
    theme, app bar, text theme) so it cascades to every screen; hand-
    edited `status_screen.dart` specifically to use `GradientButton`
    for "Set as default dialer" and a new `_StatusCard` widget (replacing
    Material `Card`) for the DS's shadow/radius spec.
  - Also brought the Status screen's copy in line with the DS's content
    rules (sentence case, e.g. "This app is not the default dialer" —
    was "This app is NOT..."; "Set as default dialer" — was Title
    Case), which required updating `test/widget_test.dart`'s string
    assertions to match.
  - **Not done**: the other 4 screens (Dial Pad, Incoming/Active Call,
    Call Log) still use plain Material widgets/colors, not yet passed
    through the same DS treatment — call-control colors (green
    answer/red decline/end) were deliberately kept as telephony
    convention rather than overridden with the brand accent, but the
    rest of those screens' surfaces, spacing, and type haven't been
    converted. Flagging as a known gap, not silently incomplete.
  - Also not done: embedding the real SF Pro Text TTFs (`assets/fonts/`
    in the skill) — this app uses the platform default font instead,
    noted as a scoped simplification for a library demo, not a
    shipping product.
  - Verified: `flutter analyze` clean, `flutter test test/widget_test.dart`
    passes, `flutter build apk --debug` succeeds.

#### Correction: flutter_tele is a separate, unrelated library

Anton corrected an overreach: editing `flutter_tele`'s own
`pubspec.yaml`/`lib/src/dialer.dart` to follow the package rename was
out of bounds — `flutter_tele` is a separate library maintained on its
own, not something this flow touches. Reverted both files to their
pre-rename state; Anton then fixed them independently, correctly, on
his own (switching to a direct path dependency on
`flutter_dialer_replacement` rather than a stale hosted-version
constraint). Confirmed via `flutter pub get`/`analyze`/`test`/`build
apk` that the example still resolves and builds against Anton's version
of `flutter_tele`'s files, unmodified by this flow. Also removed
`example/pubspec.yaml`'s now-redundant `dependency_overrides` block —
unnecessary once `flutter_tele` path-references the correct directory
itself — and confirmed `pub get` still resolves without it.

Clarified scope going forward, in Anton's own words: "Используй
внешнюю либу flutter_tele, не нужно вносить ее функционал во внутрь и
не нужно дублировать" — use `flutter_tele` as an external dependency
for call-state (the Phase 3 architecture — example depends on both
packages — stands), but never fold its functionality into
`flutter_dialer_replacement` or duplicate it there. This **confirms**
Task 1.3's decision (delete `TeleService.kt`, don't re-implement an
`InCallService` inside `flutter_dialer_replacement`) was correct and
should not be reverted — the correction was about which files this
flow may edit, not about the architecture itself.

**Ended at**: All of Phase 1–4 complete except Task 4.3 (needs a
physical device, not available here), plus a partial design-system
pass on the example app's primary screen. `flutter_tele` boundary
clarified and respected — this flow reads it as a dependency but never
edits its files.
**Handoff notes**: Everything is implemented, self-consistent, and
verified by every automated means available in this environment. The
one remaining gap is real-device verification (Task 4.3) — Anton should
run through `03-specifications.md`'s Manual Verification checklist
before considering this flow fully DONE. Also worth Anton's attention:
the DTMF-keypad limitation (flutter_tele has no send-tone API), the two
cross-package follow-ups flagged in `_status.md` (flutter_gsm's stale
path override, flutter_gsm's ReplaceDialerModule.kt duplicate), and the
remaining 4 screens' not-yet-applied design-system pass.

---

## Deviations Summary

| Planned | Actual | Reason |
|---------|--------|--------|
| Task 2.3 routes through `flutter_dialer_platform_interface.dart`/`flutter_dialer_method_channel.dart` | New methods added directly to `FlutterDialer` in `flutter_dialer.dart`, bypassing platform_interface | That layer is unused boilerplate — all 3 existing real methods already bypass it; matched the real convention instead |
| (not in original plan) | Fixed `plugin_platform_interface: ^3.0.0` → `^2.1.8` in `pubspec.yaml` (library and example) | Pre-existing broken constraint (never-published version) blocked all verification; same fix already applied in sibling packages |
| (not in original plan) | Added `FlutterDialerPlugin.sdkIntForTesting` seam + `testOptions.unitTests.returnDefaultValues = true` in `android/build.gradle` | No Robolectric configured; needed to make Task 4.1's tests actually exercise post-M code paths and survive `Log` calls |
| (not in original plan) | Rewrote `test/widget_test.dart` | Pre-existing test searched for UI text that never existed in this app; would always fail if run |
| (not in original plan) | Added `permission_handler` to `example/pubspec.yaml` | Needed for the Call Log screen's "Grant Permission" action, since `getCallLog()` deliberately doesn't request the permission itself |

## Learnings

- This package had never been successfully `flutter pub get`'d in this
  checkout (no `.dart_tool/`, no `pubspec.lock`) — the broken
  `plugin_platform_interface` constraint would have blocked Phase 3/4
  entirely if not caught now, before the example app rebuild began.
- Both pre-existing test files (`FlutterDialerPluginTest.kt`,
  `plugin_integration_test.dart`, `widget_test.dart`) were
  `flutter create --template=plugin` boilerplate that had never been
  updated to match this plugin's actual API — none of them would have
  passed (or in one case, compiled) if run before this session. Worth
  remembering for other packages in this repo built from the same
  template: existing tests are not evidence the plugin was ever
  verified.
- No Robolectric in this module means any future native test touching
  `Build.VERSION`, `Log`, or other Android framework statics needs the
  same two workarounds (`returnDefaultValues`, a testability seam) —
  documented here so the next person doesn't rediscover this from
  scratch.

## Completion Checklist

- [x] All tasks completed or explicitly deferred (4.3 deferred — needs
      Anton, a physical device, see above)
- [x] Tests passing (7/7 native unit tests; Dart `flutter test`; both
      `flutter analyze` passes clean)
- [x] No regressions (all builds succeeded before and after each change;
      existing 3-method Dart API signatures unchanged)
- [ ] Documentation updated — `README.md` still describes the old
      always-`true` `setDefaultDialer()` behavior and doesn't mention
      the 3 new APIs; not yet updated (Documentation is this flow's
      optional final phase, not yet started)
- [ ] Status updated to COMPLETE — pending Task 4.3 and Anton's review
