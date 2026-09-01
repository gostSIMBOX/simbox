# Status: vdd-flutter_gsmsip-example-uiux

## Current Phase

REQUIREMENTS | VISUAL | SPECIFICATIONS | PLAN | **IMPLEMENTATION** | DOCUMENTATION

## Phase Status

APPROVED | APPROVED | APPROVED | APPROVED | **IN PROGRESS**

## Last Updated

2026-08-31 by Claude — **Implementation pass complete for AC1/AC4-AC8**
(all 7 plan phases executed; see `05-implementation-log.md` for full
per-task detail). Summary:
- Phase 1: `DefaultDialerStatusSource`, `DialerWarningLevel`/`DialerWarningState`.
- Phase 2: DS Green/Simple restyle across `app_colors.dart`/`app_gradients.dart`/
  `app_widgets.dart` — collapsed ~29 gradients down to the one DS-sanctioned
  accent gradient.
- Phase 3: `DashboardScreen` → `GatewayScreen`, Active Routings list
  (`RoutingListState`), Idle/Loading/Disarmed states.
- Phase 4: persistent Default Dialer card + one-time arm alert, wired
  into both `GatewayScreen` and `SettingsScreen`.
- Phase 5.1: manifest permission-ownership comments (no permissions
  removed). Task 5.2 delegated, tracked separately.
- Phase 6: Android-only native splash via `/nativemind-flutter-splash`,
  including a placeholder-logo dark-mode-contrast fix discovered during
  verification.
- Phase 7.1 **blocked** (see below); 7.2 done (updated voiceline-uiux's
  status).

**Update (same day, Anton's follow-up)**: the `flutter_dialer` gap above
is **fixed**. Anton pointed at `libsFlutter/flutter_dialer_replacement`
directly — its own git log (`ec40f97 Rename package to
flutter_dialer_replacement...`) confirms it *is* the missing
`flutter_dialer`, renamed upstream with a fully working implementation
(not a stub), but the rename was never propagated to consumers. Fixed
every stale reference across the graph (package name in
`dependencies`/`dependency_overrides` + 2 import statements, class name
`FlutterDialer` and file path `flutter_dialer.dart` unchanged since
those didn't change upstream) in: `flutter_gsm/pubspec.yaml` (+ its
`android_flutter_gsm.dart` import), `flutter_gsm/example/pubspec.yaml`,
`flutter_tele/pubspec.yaml` (+ its `dialer.dart` import),
`flutter_tele/example/pubspec.yaml`, `flutter_gsmsip/pubspec.yaml`,
`flutter_gsmsip/example/pubspec.yaml`. Verified: `flutter pub get`
resolves cleanly (previously failed before reaching Gradle at all),
`flutter analyze`/`flutter test` unchanged at their existing clean
baseline. **This fix touched files outside this flow's own scope**
(`flutter_gsm`, `flutter_tele` — two other packages) — done with Anton's
explicit approval, not unilaterally.

**New discovery from attempting the fix**: fixing `flutter_dialer` was
necessary but not sufficient. `flutter build apk --debug` now gets past
the Dart-compile stage entirely (proves the fix worked) but fails at a
**separate, deeper, unrelated** stage: `flutter_nmsip`'s Android native
code (`ArgumentUtils.java`, `PjActions.java`) references React Native
bridge types (`WritableMap`/`WritableNativeMap`/etc.) and
`Gson`/`JsonElement`, none declared in `flutter_nmsip/android/build.gradle`
— 97 Java compile errors. The referenced DTO source files
(`CallSettingsDTO.java`, `SipMessageDTO.java`) exist, so this is a
missing-dependency/design problem, not a missing-file one — likely
leftover from this project's `react-native-*` lineage, never adapted for
a pure Flutter plugin. **Not fixed** — different package, different kind
of problem (native dependency/design decision), outside anything
authorized in this session. Task 7.1 stays blocked, now for this reason.

## Blockers

- **None for this flow's own scope** — AC1/AC4-AC8 implementation is
  done and self-verified (`flutter analyze`/`flutter test`/`aapt2`) to
  the extent possible without a runnable APK.
- Task 7.1 (manual walkthrough) stays blocked — `flutter_dialer` is
  fixed, but `flutter_nmsip`'s Android native build gap (see above) is a
  new, separate blocker, out of this flow's scope to fix.
- AC2 (multi-profile config) and AC3 (Magisk-capability display) remain
  gated on `flows/flutter_gsmsip/sdd-flutter_gsmsip-lib/` (still in
  REQUIREMENTS) — genuinely unbuilt, need their own Specifications+Plan
  pass once that flow settles.
- Capabilities screen overlap with `vdd-flutter_gsmsip-example-voiceline-uiux`'s
  "Enhanced Mode" screen remains unresolved but non-urgent — AC3 isn't
  built yet on either side.

## Progress

- [x] Requirements drafted
- [x] Requirements approved
- [x] Visual drafted
- [x] Visual approved
- [x] Specifications drafted
- [x] Specifications approved
- [x] Plan drafted
- [x] Plan approved
- [x] Implementation started
- [x] Implementation complete (for AC1/AC4-AC8 — AC2/AC3 excluded by
      design, Task 7.1 blocked on an external gap, Task 5.2 delegated)
- [ ] Documentation drafted
- [ ] Documentation approved

## Context Notes

Key decisions and context for resuming:

- **Goal**: bring the "gateway product" functionality from
  `reactntive/react-native-gsm-sip-gateway` (RN, per-device profile
  config, `Gateway` bridge class) and its native successor
  `3rdparty/gsm2sip` (Kotlin, `CallOrchestrator`, working Magisk module,
  default-dialer eligibility) into `libsFlutter/flutter_gsmsip/example`'s
  UI/UX — not into the `flutter_gsmsip` library itself.
- **Scope boundary (hard constraint)**: `libsFlutter/flutter_gsmsip/lib/**`
  stays untouched, same rule `sdd-flutter_gsmsip-example` operated under.
  This is a UI/UX flow for the *example app*.
- **Cross-flow discipline**: two adjacent concerns are explicitly routed
  elsewhere, not implemented here:
  - Default-dialer / `InCallService` / `ConnectionService` work →
    `flows/flutter_replace_dialer/` (tracks the **`flutter_dialer`**
    package — its current `tdd-replace-dialer` doc is legacy
    React-Native content for `react-native-replace-dialer` and needs a
    Flutter-era pass; this flow's example screens should call into
    `flutter_dialer` and *link to* that flow, not reimplement).
  - Magisk module content / privileged-permission mechanics →
    `flows/flutter_gsmsip/sdd-voiceline-mode-magisk` +
    `sdd-voiceline-mode-magisk-v2` (already own the `LineInfo`
    capability-flag design this flow's Capabilities screen should read).
- **Permission audit answered directly in 01-requirements.md** (Anton
  asked this explicitly): permissions are inconsistently declared across
  the plugin family. `flutter_gsmsip` has no `android/` folder by design
  (pure-Dart orchestrator) and can't declare any. `flutter_gsm`'s own
  library manifest is **empty** — all 25 of its permissions live only in
  `flutter_gsm/example`'s manifest, a real gap belonging to
  `flows/flutter_gsm/`, not this flow. `flutter_nmsip`, `flutter_smsussd`,
  `flutter_tele`, `flutter_dialer` are each correctly self-contained.
  Contacts (`READ/WRITE_CONTACTS`), wifi-state, `READ_PHONE_NUMBERS`,
  `USE_SIP`, boot-receiver, and `CALL_PRIVILEGED` exist **only** in
  `flutter_gsmsip/example`'s manifest, in no library anywhere — full
  table in 01-requirements.md's "Permission Audit" section.
- **Design mandates**: use `/nativemind-designsystem` (live skill, not
  the pinned `_ds/` snapshot bundled in the splash skill) and
  `/nativemind-flutter-splash` for the example's restyle — replacing the
  bespoke `example/lib/theme/app_*.dart` files and default Flutter splash.
  Accent colorway not yet chosen — flagged as an Open Question for the
  Visual phase.
- **Reuse, don't reinvent**: `flows/flutter_gsmsip/vdd-dialer/` already
  has an *approved* visual language for "Bridge call status: SIP leg +
  GSM leg" — the new Gateway screen should reuse that vocabulary rather
  than invent a new one.
- **Library split (2026-08-31)**: everything requiring changes under
  `libsFlutter/flutter_gsmsip/lib/**` was pulled out into a new sibling
  flow, `flows/flutter_gsmsip/sdd-flutter_gsmsip-lib/` — specifically:
  public config save/clear API on `GatewayService` (today only a private
  `_saveConfiguration()`), multi-profile config storage, whether a
  Magisk-capability model belongs in the library at all, and documenting
  the permission contract the library can't enforce itself (no
  `android/` folder). This flow's AC2/AC3 now explicitly depend on that
  one — don't re-derive those decisions here.
- **Confirmed NOT a gap**: GSM→SIP auto-bridging already works in
  `GatewayService._handleIncomingGsmCall()` (gated by
  `routeGsmToSip`/`autoAnswer`, emitting `CallRouting` on
  `routingStream`) — AC1's Gateway screen is pure visualization of
  existing public API, no library dependency.

## Next Actions

1. `flutter_nmsip`'s Android native build gap (missing Gson/RN-bridge
   dependencies in its `build.gradle`) needs its own investigation —
   likely its own flow, not a quick fix inside this one.
2. Once a runnable APK is possible, complete Task 7.1 (real-device manual
   walkthrough per `03-specifications.md`'s checklist) and update this
   status accordingly.
3. Watch `flows/flutter_smsussd/sdd-flutter_smsussd-receive-mms-receive-wap-push/`
   for its outcome (independent of this flow's own completion).
4. Watch `flows/flutter_gsmsip/sdd-flutter_gsmsip-lib/` — once it reaches
   Specifications, open a follow-up Specifications+Plan pass here for
   AC2/AC3 (this flow's own docs already sketch the shape in
   `03-specifications.md`'s Deferred section).
5. When ready, move to DOCUMENTATION phase (client-facing README section
   per 01-requirements.md's Should-Have) — needs Anton's go-ahead first,
   per this skill's phase-transition rule.
