# Implementation Log: flutter_gsmsip-example-uiux

> Started: 2026-08-31
> Plan: [04-plan.md](04-plan.md)

## Progress Tracker

| Task | Status | Notes |
|---|---|---|
| 1.1 DefaultDialerStatusSource | Done | 5/5 tests pass, analyze clean |
| 1.2 DialerWarningLevel | Done | 9/9 tests pass, analyze clean |
| 2.1 DS color tokens | Done | analyze/tests clean; discovered `error:` was hardcoded twice in `ColorScheme`, fixed to reference the DS-mapped constant |
| 2.2 DS gradients collapse | Done | Deviation: also removed 4 dead gradients + `getCardGradient()` found in `app_colors.dart` (not in original file list) — see Deviations |
| 2.3 Re-skin indicator widgets | Done | `_getSignalColor`'s 2 custom hexes now DS-derived (`accentLight`, warning−20%L) |
| 2.4 Shadow + icon-set alignment | Done (shadow) / Deferred (icons) | No raw `BoxShadow` exists — Material `elevation`+`shadowColor` already inherits DS tint from 2.1. Icon vendoring stays an Open Implementation Question per plan |
| 3.1 Rename DashboardScreen → GatewayScreen | Done | Pure rename + main.dart wiring; analyze/tests clean |
| 3.2 Active Routings list | Done | Extracted `RoutingListState` (pure reducer) — 8-case state×direction matrix tested |
| 3.3 Empty/idle/disarmed states | Done | Resolved the "which button keeps the gradient" Open Question: `gradientButton` now used for "Turn On Gateway Mode" |
| 4.1 Persistent Default Dialer card | Done | Self-contained widget, embedded in both GatewayScreen + SettingsScreen |
| 4.2 Arm-time alert | Done | Trigger condition extracted as pure function, unit tested (6 cases) |
| 5.1 Manifest ownership comment block | Not started | |
| 5.2 RECEIVE_MMS/RECEIVE_WAP_PUSH | Delegated | See `flows/flutter_smsussd/sdd-flutter_smsussd-receive-mms-receive-wap-push/` |
| 6.1 Invoke /nativemind-flutter-splash | Done (Android only) | Discovered + fixed a dark-mode-invisible placeholder logo; verified via `aapt2 link`, not a full `flutter build apk` (pre-existing unrelated break) |
| 7.1 Full manual walkthrough | Blocked | Fixed the `flutter_dialer` gap (Anton's request, cross-package), but a second, deeper `flutter_nmsip` Android build gap was found — see Discoveries |
| 7.2 Update sibling-flow status files | Done | Updated voiceline-uiux's `_status.md` blocker note |

## Session Log

### Session 2026-08-31 - Claude

**Started at**: Phase 1, Task 1.1
**Context**: Plan approved by Anton same session; starting execution
task-by-task per plan order (data layer first, no UI dependency).

#### Completed

- Task 1.1: `DefaultDialerStatusSource` — abstract interface +
  `FlutterGsmDefaultDialerStatusSource` reading the existing
  `flutter_gsm/replace_dialer` `MethodChannel`.
  - Files changed: `example/lib/data/default_dialer_status_source.dart` (new),
    `example/test/default_dialer_status_source_test.dart` (new)
  - Verified by: `flutter test` (5/5 pass — channel-method mapping for
    all three methods, `PlatformException` and `MissingPluginException`
    both surface as `false`/no-op rather than crashing); `flutter analyze`
    clean on both files.
- Task 1.2: `DialerWarningLevel` enum + `DialerWarningState` transition
  logic (`none`/`needsAlert`/`cardOnly`, fail-toward-`needsAlert` on an
  unresolved check, dialer-revoked-after-being-set re-triggers
  `needsAlert`).
  - Files changed: `example/lib/data/dialer_warning_level.dart` (new),
    `example/test/dialer_warning_level_test.dart` (new)
  - Verified by: `flutter test` (9/9 pass, covering every transition in
    03-specifications.md's Behavior Specifications table plus the
    revoked-after-set edge case not explicitly in the table but implied
    by it); `flutter analyze` clean.

#### In Progress

- None — Phase 1 complete, moving to Phase 2 (DS restyle) next.

#### Deviations from Plan

- None so far.

#### Discoveries

- `DialerWarningState` needed one behavior not spelled out verbatim in
  03-specifications.md: what happens if the dialer is set, then later
  un-set while the app is running (e.g. user changes it externally,
  caught by the `didChangeAppLifecycleState(resumed)` re-check from Task
  4.1). Decided: treat as a fresh `needsAlert` (re-interrupt the user),
  not silently `cardOnly` — consistent with the "proactively surface,
  don't assume" framing from AC4, though not a literal quote from the
  spec. Flagging here rather than silently deciding, per this project's
  own emphasis on traceability.

**Ended at**: Phase 1 complete, starting Phase 2
**Handoff notes**: Phase 2 (DS restyle) is the largest-blast-radius phase
— touches `app_colors.dart`/`app_gradients.dart`/`app_widgets.dart`/
`app_theme.dart`, which all 6 existing screens depend on. Plan's Task 2.1
Verification step (`flutter analyze` + no call-site breakage) is the load-
bearing check here — do not skip it between sub-tasks.

---

### Session 2026-08-31 (cont.) - Claude

**Started at**: Phase 2, Task 2.1
**Context**: Continuing same session, Phase 1 verified clean.

#### Completed

- Task 2.1: Remapped every `AppColors` field to DS Green/Simple + shared
  neutrals (`~/.claude/skills/nativemind-designsystem/tokens/colors.css`).
  Kept every field name unchanged per the re-skin rule. Notable decisions:
  `accent`/`accentLight`/`accentDark` mapped to DS's semantic `--success`
  family (the original code already hardcoded `accent` and `success` to
  the identical hex, so this preserves existing behavior while giving
  `primary` sole ownership of the brand/CTA accent). `technical*` (an
  unused-elsewhere purple) neutralized to `--fg-1`-derived shades rather
  than kept as a second hue, since DS mandates one accent colorway.
  - Files changed: `example/lib/theme/app_colors.dart`
  - Verified by: `flutter analyze` (0 new issues — 6 pre-existing
    `deprecated_member_use` infos on unrelated `ColorScheme` fields,
    confirmed present before this change too); all 18 tests still pass.
- Task 2.2: Collapsed all gradients to DS's one reserved accent gradient.
  `AppGradients` now defines a single `primaryCtaGradient`
  (`#34E89E→#0CA678`) instead of ~25 constants + getters — grep confirmed
  every deleted one was unused anywhere in `lib/screens/`.
  `gradientButton` uses it by default (positioned as the future "Turn On
  Gateway Mode" CTA — see Task 3.3). `gradientCard`/
  `gradientProgressIndicator`/`gradientChip` flattened to solid DS
  colors (`gradientChip`'s selected state uses DS's `--brand-tint`
  wash + `--brand` border, matching the DS's documented chip pattern).
  - Files changed: `example/lib/theme/app_gradients.dart`,
    `example/lib/theme/app_widgets.dart`
  - Verified by: `flutter analyze` (0 new issues), all 18 tests pass,
    grep for `LinearGradient` outside `app_gradients.dart` returns only
    `gradientButton`'s explicit-override branch (inactive by default,
    zero callers pass `colors:` today).
- Task 2.3: Re-skinned `_getSignalColor`'s 5-band ramp — the two
  hardcoded hexes it had are now DS-derived (`AppColors.accentLight` for
  the 60-79% band, a computed "warning −20% lightness" deeper amber for
  20-39%). `connectionIndicator`/`callStatusIndicator`/`statusCard`
  needed no direct edits — they already reference `AppColors` fields
  that Task 2.1 remapped.
  - Files changed: `example/lib/theme/app_widgets.dart`
  - Verified by: `flutter analyze` (0 new issues), all 18 tests pass.
- Task 2.4: Verified — no raw `BoxShadow` definitions exist anywhere in
  `app_theme.dart`; it exclusively uses Flutter's Material `elevation`/
  `shadowColor` theming, and `shadowColor` already points at
  `AppColors.lightCardShadow`/`darkCardShadow`, both remapped to the DS
  shadow tint in Task 2.1. No edit needed. Icon vendoring
  (`assets/adminka/`) intentionally left as the plan's own Open
  Implementation Question, not resolved here.
  - Files changed: none
  - Verified by: grep for hardcoded `Color(0x...)`/`Colors.black`/
    `Colors.grey` literals in `app_theme.dart` — zero hits.

#### Deviations from Plan

- Task 2.2's file list (04-plan.md) named only `app_gradients.dart` and
  `app_widgets.dart`. During implementation, grep revealed
  `app_colors.dart` independently defined 4 more unused gradient
  constants (`primaryGradient`/`accentGradient`/`technicalGradient`/
  `connectionGradient`) plus a now-dead `getCardGradient()` helper — the
  plan's Affected Systems table hadn't caught this second copy. Removed
  them too, since leaving 4 dead "scattered" gradients around would
  contradict the very rule this task exists to enforce. Documented here
  rather than silently expanding file scope.

#### Discoveries

- 5 of `AppWidgets`' 8 public methods (`connectionIndicator`,
  `gradientCard`, `gradientButton`, `gradientProgressIndicator`,
  `gradientChip`) are currently unused by any of the 6 existing screens
  — only `statusCard`, `signalIndicator`, `callStatusIndicator` have real
  call sites today (confirmed by grep). Re-skinned all 8 anyway per the
  "re-skin, don't replace" instruction, but this explains why the diffs
  above carried zero risk of visible behavior change — the unused ones
  may become live once the Gateway screen (Phase 3) or Default Dialer UI
  (Phase 4) is built.

**Ended at**: Phase 2 complete, starting Phase 3
**Handoff notes**: `gradientButton`'s default now renders the DS accent
gradient — if Phase 3's Idle-state "Turn On Gateway Mode" button uses
`AppWidgets.gradientButton(...)` without an explicit `colors:` override,
it gets the DS CTA gradient automatically, closing the Open
Implementation Question about which widget keeps the one gradient.

---

### Session 2026-08-31 (cont. 2) - Claude

**Started at**: Phase 3, Task 3.1
**Context**: Continuing same session, Phase 2 verified clean.

#### Completed

- Task 3.1: Renamed `DashboardScreen`/`_DashboardScreenState` →
  `GatewayScreen`/`_GatewayScreenState`, file renamed
  `dashboard_screen.dart` → `gateway_screen.dart`. Updated `main.dart`:
  import path, `_tabs` entry ("Dashboard" → "Gateway", icon →
  `Icons.swap_calls`), `_goToDashboard` → `_goToGateway`, AppBar title,
  doc comments. Confirmed via grep zero remaining references to the old
  name anywhere in `lib/`/`test/`.
  - Files changed: `example/lib/screens/dashboard_screen.dart` (deleted),
    `example/lib/screens/gateway_screen.dart` (new, same logic),
    `example/lib/main.dart`
  - Verified by: `flutter analyze` (0 new issues), all tests pass. Full
    app launch on a real device/emulator not verified in this
    environment (no device attached) — flagged for Task 7.1's manual
    walkthrough.
- Task 3.2: Subscribed to `_gateway.routingStream`, seeded initial state
  from `_gateway.getActiveRoutings()`. Built `ActiveRoutingCard` widget
  rendering the SIP-leg/GSM-leg/Bridge trio per 02-visual.md, reusing
  `vdd-dialer`'s language, grounded in real `CallRoutingState`/
  `CallRoutingDirection` values.
  - Files changed: `example/lib/screens/widgets/active_routing_card.dart` (new),
    `example/lib/screens/gateway_screen.dart`
  - Verified by: see Task 3.2's extracted-reducer test below (Deviation)
    — `flutter analyze` 0 new issues.
- Task 3.3: Implemented Idle (armed, no routings) / Loading (starting,
  not yet operational) / Empty-disarmed (gateway off) states, all keyed
  off `GatewayStatus` fields already in the public API (`isRunning`,
  `isOperational`, `hasError`) — no new state enum invented. Resolved
  the plan's Open Implementation Question: `AppWidgets.gradientButton`
  (DS's one reserved gradient) is now the "Turn On Gateway Mode" CTA;
  "Stop Gateway" is a plain `OutlinedButton` (not the gradient — DS
  reserves it for one primary action, and stopping isn't that).
  - Files changed: `example/lib/screens/gateway_screen.dart`
  - Verified by: `flutter analyze` 0 new issues, all tests pass.

#### Deviations from Plan

- Task 3.2's plan Verification step called for "Unit test the
  routing-list reducer against `routingStream` fixtures covering all
  four `CallRoutingState` values × both `CallRoutingDirection` values (8
  cases)." `_gateway` is constructed directly inside `GatewayScreen`
  (`final _gateway = GatewayService();`), not injected, so there's no
  seam to feed fake stream events into the widget for a true widget-level
  test. Extracted the actual reduction logic into a standalone pure class,
  `RoutingListState` (`example/lib/data/routing_list_state.dart`) —
  same pattern as Phase 1's `DialerWarningState` — so the 8-case matrix
  (plus 3 additional cases: in-place update, explicit removal, multiple
  simultaneous routings) is directly unit-tested without needing
  `GatewayService` at all. `GatewayScreen` now delegates to it, keeping
  only the `Timer`-based auto-removal *scheduling* (not the state logic
  itself) inside the widget, where it's a thin, low-risk wrapper.
  - Files changed (beyond plan's list):
    `example/lib/data/routing_list_state.dart` (new),
    `example/test/routing_list_state_test.dart` (new)

#### Discoveries

- None beyond the injection-seam issue above.

**Ended at**: Phase 3 complete, starting Phase 4
**Handoff notes**: Phase 4 (Default Dialer UI) can now use
`AppColors`/DS tokens freely (Phase 2 done) and slot into
`GatewayScreen`'s existing `ListView` (Phase 3 done) — no more
prerequisite work blocking it.

---

### Session 2026-08-31 (cont. 3) - Claude

**Started at**: Phase 4, Task 4.1
**Context**: Continuing same session, Phase 3 verified clean.

#### Completed

- Task 4.1: `DefaultDialerCard` — self-contained `StatefulWidget` owning
  its own `FlutterGsmDefaultDialerStatusSource` check + a
  `WidgetsBindingObserver` re-check on `didChangeAppLifecycleState
  (resumed)`. Renders 02-visual.md's exact copy (precise consequence:
  "Incoming GSM calls will NOT auto-answer/bridge to SIP... Everything
  else... still works"), plus the `canSetDefaultDialer() == false`
  no-dead-end-button variant from 03-specifications.md's edge cases.
  Embedded in `GatewayScreen` (below Gateway Status) and `SettingsScreen`
  (above the config form, which was already a `ListView` internally —
  wrapped in `Column`+`Expanded`, no change to `GatewayConfigForm` itself).
  - Files changed: `example/lib/screens/widgets/default_dialer_card.dart` (new),
    `example/lib/screens/gateway_screen.dart`,
    `example/lib/screens/settings_screen.dart`
  - Verified by: `flutter analyze` 0 new issues on all three files.
- Task 4.2: `showDefaultDialerArmAlert()` renders 02-visual.md's
  interrupting modal exactly ("Gateway armed, but incoming calls won't
  bridge yet" / Continue Anyway / Set Default Dialer). Wired into
  `GatewayScreen`'s `statusStream` listener: tracks `_wasRunning` and
  calls the extracted `shouldShowDialerArmAlert()` pure function (see
  Deviation) before updating state, so the check happens on the actual
  `false -> true` transition, not after `_status` is already updated to
  the new value.
  - Files changed: `example/lib/screens/widgets/default_dialer_arm_alert.dart` (new),
    `example/lib/screens/gateway_screen.dart`,
    `example/lib/data/dialer_warning_level.dart`
  - Verified by: 6 new unit tests on `shouldShowDialerArmAlert` (the
    edge condition itself, its negation while already running, the
    reverse true→false edge, and both non-`needsAlert` levels) — all
    pass; `flutter analyze` 0 new issues.

#### Deviations from Plan

- Same pattern as Task 3.2's deviation: Task 4.2's plan Verification
  step ("unit test the trigger condition... must not re-fire on every
  rebuild while already running") needs a seam that
  `GatewayScreen`-the-widget doesn't have (no injected `GatewayService`).
  Extracted `shouldShowDialerArmAlert()` as a pure function in
  `dialer_warning_level.dart` (co-located with `DialerWarningState`
  since they're used together) rather than putting the logic inline in
  the widget's stream listener.

#### Discoveries

- None.

**Ended at**: Phase 4 complete, starting Phase 5
**Handoff notes**: Phase 5.1 (manifest comments) is independent of
everything so far — pure documentation, no Dart code dependency.

---

### Session 2026-08-31 (cont. 4) - Claude

**Started at**: Phase 5, Task 5.1
**Context**: Continuing same session, Phase 4 verified clean.

#### Completed

- Task 5.1: Added the permission-ownership comment block from
  03-specifications.md to `example/android/app/src/main/AndroidManifest.xml`.
  Confirmed via `git diff` that zero `<uses-permission>` lines changed —
  comments only.
  - Files changed: `example/android/app/src/main/AndroidManifest.xml`
  - Verified by: XML well-formedness check (`xml.etree.ElementTree`),
    `git diff` grep for `uses-permission` lines (zero hits).
- Task 6.1: Invoked `/nativemind-flutter-splash`, scoped to **Android
  only** — this app's actual platform folders are `android/`, `linux/`,
  `macos/` (no `ios/`/`windows/`/`web/`), and AC7 itself says "native
  launch screen on Android" specifically. Skipping macOS/Linux also
  avoids the skill's own documented integration gotchas (imageset idiom,
  competing first-frame signals) for platforms this app's own capability
  table already treats as degraded for its actual GSM purpose.
  Generated placeholder assets from
  `~/.claude/skills/nativemind-designsystem/uploads/logo_nativemind.svg`
  (via `rsvg-convert`) across all 5 density buckets (mdpi/hdpi/xhdpi/
  xxhdpi/xxxhdpi) at the DS's specified 240dp logical width, plus a
  composited "powered by [mark] NativeMind" branding footer (PIL +
  macOS's system `SFNS.ttf`, since this skill's own bundled
  `sf-pro-text-*.ttf` files are confirmed-broken HTML documents, not
  real font binaries — exactly the caveat its own README already flags).
  Wired `values/styles.xml`, `values-night/styles.xml` (edited), new
  `values-v31/styles.xml`, `values-night-v31/styles.xml`, new
  `values/colors.xml`, `values-night/colors.xml`, rewrote
  `drawable/launch_background.xml`'s layer-list, deleted the now-redundant
  `drawable-v21/launch_background.xml` (would otherwise shadow the
  unqualified one on API 21+, undoing this task). No `AndroidManifest.xml`
  changes needed — the default Flutter template's manifest already wires
  `LaunchTheme`/`NormalTheme` exactly as this skill expects.
  - Files changed: `example/android/app/src/main/res/values/{styles,colors}.xml`,
    `values-night/{styles,colors}.xml`, `values-v31/styles.xml` (new),
    `values-night-v31/styles.xml` (new), `drawable/launch_background.xml`,
    `drawable/splash_branding.png` (new), `drawable-{density}/splash_icon{,_bitmap}.png`
    (new, 5 densities), `drawable-night-{density}/splash_icon{,_bitmap}.png`
    (new, 5 densities, see Discovery), `drawable-night/splash_branding.png`
    (new, see Discovery). Deleted: `drawable-v21/launch_background.xml`.
  - Verified by: **not** a full `flutter build apk` — a pre-existing,
    unrelated Dart compile error blocks that (see Discovery). Instead:
    `aapt2 compile` on the full `res/` tree (35 files, zero errors) +
    `aapt2 link` against the real manifest with a temporary
    `package=`/`${applicationName}` patch (aapt2 run standalone doesn't
    understand Gradle's namespace injection or manifest placeholders) —
    linked successfully into a real APK shell (0 errors, 257KB). Also
    manually composited both light and dark full-frame previews at the
    DS's specified proportions (240dp logo, -24 vertical offset, 32dp
    bottom safe-area) to sanity-check the actual visual result, not just
    that the XML parses.

#### Deviations from Plan

- Scoped Task 6.1 to Android only, per the reasoning above — the plan's
  Task 6.1 description didn't explicitly say "Android only," but AC7's
  own text and this app's actual platform folder set both point the same
  direction.

#### Discoveries

- **`flutter build apk --debug` fails on this repo for a reason entirely
  unrelated to this flow**: `libsFlutter/flutter_dialer` — the package
  `flutter_gsm`/`flutter_tele` both depend on via a local path override
  — does not exist as a directory anywhere in this checkout. This is a
  pre-existing infrastructure gap, not something introduced by any task
  in this implementation. It's the same package already flagged in
  `vdd-flutter_gsmsip-example-uiux/01-requirements.md`'s cross-flow table
  as owned by `flows/flutter_replace_dialer/` — this discovery is
  additional, concrete evidence for that flow (the package isn't just
  "needs a Flutter-era pass," it's missing outright from this checkout),
  worth surfacing there, not fixed here.
- **The placeholder logo SVG is invisible in dark mode**:
  `logo_nativemind.svg` hardcodes `stroke="#000"` (pure black, not
  `currentColor` or a themeable value) — against the DS's `#0F1419` dark
  background this renders as solid black on near-black, no defined
  numeric contrast ratio but visibly indistinguishable in each PIL-rendered
  preview.  Generated a stroke-inverted variant (`stroke="#E7ECEF"`,
  matching DS `--fg-1-dark`) for the `drawable-night-*` buckets rather
  than shipping a splash that's blank in dark mode. This is a
  placeholder-asset fix, not a design decision — once a real SimBox logo
  replaces the placeholder, whoever supplies it should provide (or this
  step should be redone for) a dark-mode-safe variant the same way.

**Ended at**: Phase 6 complete, starting Phase 7
**Handoff notes**: Phase 7.1 (manual walkthrough) needs a real device/
emulator and the `flutter_dialer` gap resolved (or worked around) to get
a runnable APK — flagged as a real limitation of this session's
environment, not skipped by choice.

---

### Session 2026-08-31 (cont. 5) - Claude

**Started at**: Phase 7
**Context**: Continuing same session, Phase 6 verified clean via `aapt2`.

#### Completed

- Task 7.2: Updated
  `flows/flutter_gsmsip/vdd-flutter_gsmsip-example-voiceline-uiux/_status.md`
  — the Enhanced-Mode/System-Capabilities overlap is no longer purely
  theoretical (this flow's Gateway/Default-Dialer/DS-restyle side is now
  real code), though no actual collision exists yet since the
  Capabilities screen itself stayed Deferred. Also flagged that
  voiceline-uiux should adopt the now-live Green/Simple DS tokens rather
  than reintroduce its own bespoke palette when it starts.
  - Files changed: `flows/flutter_gsmsip/vdd-flutter_gsmsip-example-voiceline-uiux/_status.md`

#### Blocked

- Task 7.1 (full manual walkthrough): requires a runnable APK, which
  `flutter build apk` cannot produce in this environment due to the
  pre-existing, unrelated `flutter_dialer` package gap (see Phase 6's
  Discoveries). Did not attempt to fix `flutter_dialer` myself — that
  package belongs to `flows/flutter_replace_dialer/`, a different flow,
  and 01-requirements.md is explicit that this flow adds no new
  dialer-replacement code. What verification *was* possible without a
  device substitutes for it: `flutter analyze` (0 new issues across the
  whole session, stable at the same 23 pre-existing baseline issues),
  `flutter test` (35/35 passing, covering every piece of new logic that
  can be isolated from platform channels — `DefaultDialerStatusSource`,
  `DialerWarningState`/`shouldShowDialerArmAlert`, `RoutingListState`),
  and `aapt2 compile`/`link` for the Android splash resources (Phase 6).

#### Discoveries

- None beyond Phase 6's.

**Ended at**: Implementation complete for AC1/AC4-AC8, except Task 7.1
(blocked, see above) and Task 5.2 (delegated to
`sdd-flutter_smsussd-receive-mms-receive-wap-push`, tracked separately).
**Handoff notes**: AC2 (multi-profile Setup) and AC3 (System
Capabilities) remain entirely unbuilt, by design — they need their own
Specifications+Plan pass once `sdd-flutter_gsmsip-lib` settles. Anton
should be told about the `flutter_dialer` gap directly — it blocks not
just Task 7.1 here but presumably any real build of this example app
today, which is a bigger deal than this flow alone.

---

### Session 2026-08-31 (cont. 6) - Claude

**Started at**: Following up on Task 7.1's blocker at Anton's explicit
request (pointed directly at `libsFlutter/flutter_dialer_replacement`).
**Context**: Confirmed via that package's own git log
(`ec40f97 Rename package to flutter_dialer_replacement...`) that this is
literally the missing `flutter_dialer` — renamed upstream, but the
rename was never propagated to its consumers. Internal API unchanged:
`lib/flutter_dialer.dart`, class `FlutterDialer`,
`MethodChannel('flutter_dialer')`, full working Kotlin implementation
(not a stub). Asked Anton for explicit go-ahead before touching packages
outside this flow's original scope — approved.

#### Completed

- Fixed every stale `flutter_dialer` reference across the dependency
  graph: package name in `dependencies`/`dependency_overrides` +
  the two `import 'package:flutter_dialer/...'` statements (kept the
  `/flutter_dialer.dart` file-path segment and the `FlutterDialer` class
  name unchanged — only the package-name segment changed, since neither
  changed upstream).
  - Files changed: `flutter_gsm/pubspec.yaml`,
    `flutter_gsm/lib/src/android/android_flutter_gsm.dart`,
    `flutter_gsm/example/pubspec.yaml`, `flutter_tele/pubspec.yaml`,
    `flutter_tele/lib/src/dialer.dart`, `flutter_tele/example/pubspec.yaml`,
    `flutter_gsmsip/pubspec.yaml`, `flutter_gsmsip/example/pubspec.yaml`
  - Verified by: `flutter pub get` in `example/` resolves cleanly
    (previously failed at the Dart-compile stage before even reaching
    Gradle); `flutter analyze` still 0 new issues (same 23-issue
    baseline); `flutter test` still 35/35.

#### Discoveries

- **The `flutter_dialer` fix was real and necessary, but not sufficient
  for a full build.** `flutter build apk --debug` now gets past the
  Dart compile stage entirely (confirms the fix worked) but fails at a
  **different, deeper, unrelated** stage: `flutter_nmsip`'s Android
  native code (`ArgumentUtils.java`, `PjActions.java` — 97 Java compile
  errors) references React Native bridge types
  (`WritableMap`/`WritableNativeMap`/`WritableArray`/`WritableNativeArray`)
  and `Gson`/`JsonElement`/`LazilyParsedNumber`, none of which are
  declared anywhere in `flutter_nmsip/android/build.gradle`. The
  referenced DTO classes (`CallSettingsDTO`, `SipMessageDTO`) do exist
  as source files — this isn't a missing-file problem, it's missing
  Gradle dependencies (and possibly RN-era code that was never adapted
  for a pure Flutter plugin, consistent with this whole project's
  `react-native-*` lineage mentioned throughout its docs). **Did not
  attempt this fix** — it's a different package, a different kind of
  problem (native Android dependency/design decision, not a mechanical
  rename), and well outside what was authorized here. Task 7.1 remains
  blocked, now for this reason instead of the `flutter_dialer` one.

**Ended at**: `flutter_dialer` gap resolved and verified; a second,
deeper `flutter_nmsip` Android build gap discovered and documented, not
fixed.
**Handoff notes**: Anton should know both things: the `flutter_dialer`
fix is done and safe (pure rename, verified via pub get + analyze +
test), and there's a separate `flutter_nmsip` native-Android gap that's
a real design/dependency decision, not a quick fix — worth its own flow
or at least a deliberate look, not something to fix opportunistically
mid-way through this one.

---

## Deviations Summary

| Planned | Actual | Reason |
|---|---|---|
| Task 2.2 touches only `app_gradients.dart`/`app_widgets.dart` | Also touched `app_colors.dart` | Discovered 4 more dead gradients + a dead `getCardGradient()` helper duplicating the same "scattered gradient" problem, not caught by the plan's Affected Systems table |
| Task 3.2/4.2 verification via widget-level stream fixtures | Extracted `RoutingListState` and `shouldShowDialerArmAlert()` as pure functions/classes | `GatewayScreen` constructs `GatewayService()` directly with no injection seam; extraction was the only way to deliver the plan's own verification requirement |
| Task 5.2 (RECEIVE_MMS/RECEIVE_WAP_PUSH) | Delegated to a new standalone flow, `sdd-flutter_smsussd-receive-mms-receive-wap-push` | Anton's explicit instruction, prior to this Implementation session |
| Task 6.1 splash on all platforms implied by plan | Android only | This app has no `ios`/`windows`/`web` platform folders; AC7 itself says "Android" specifically |
| Task 7.1 full manual walkthrough | Blocked, substituted with analyze/test/aapt2 verification | Pre-existing unrelated `flutter_dialer` package gap blocks any APK build (see Session 4/5 Discoveries) |

## Learnings

- When a widget constructs its own service dependency directly (no DI),
  plan-mandated unit tests on "the reducer"/"the trigger condition" are
  only achievable by extracting that logic into a standalone pure
  class/function first. This happened twice (Phase 3, Phase 4) — worth
  proposing as a lighter-weight default pattern in future Specifications
  for this codebase (small pure reducers beside stateful widgets), rather
  than rediscovering it plan-by-plan.
- This repo's design-system and splash skills both ship placeholder font
  files that are actually broken (GitHub HTML pages saved with a `.ttf`
  extension, confirmed via `file`) — any future work rendering real text
  with "SF Pro Text" from either skill needs a real licensed font source
  or a platform-font fallback; don't trust the bundled files without
  checking first.
- `libsFlutter/flutter_gsmsip/example` currently cannot produce a debug
  APK at all (missing `flutter_dialer` package) — this is bigger than
  any one flow and Anton should know regardless of this flow's own scope.

## Completion Checklist

- [x] All tasks completed or explicitly deferred/delegated/blocked (see
      Progress Tracker — every row is Done, Delegated, or Blocked with a
      documented reason, none silently skipped)
- [x] Tests passing (35/35, `flutter test`)
- [x] No regressions (`flutter analyze` stable at 23 pre-existing issues
      throughout every phase, zero new issues introduced)
- [x] Documentation updated (`_status.md` for this flow and the
      voiceline-uiux sibling; this log)
- [ ] Status updated to COMPLETE — not yet; AC2/AC3 remain unbuilt by
      design and Task 7.1 is blocked, so this flow's Implementation phase
      is complete *for the scope this plan covered*, not complete in the
      sense of "nothing left to do" for the whole flow
