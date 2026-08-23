# Status: sdd-flutter_gsm

## Current Phase

IMPLEMENTATION

## Phase Status

DONE

## Last Updated

2026-08-21 by Claude

## Blockers

None. Both post-implementation architecture questions were put to Anton
directly and resolved (both "recommended/delete" option):
- `flutter_gsm`'s barrel cruft (leftover Sip/Gateway/Dongle/VoiceLine/
  Analytics/Settings domain code from the original filesystem copy) —
  deleted, barrel now exports only the real Modem-layer surface.
- `flutter_gsmsip`'s leftover native Android Kotlin plugin code — the
  entire `android/` directory removed; the package is now pure Dart, no
  `plugin:` platforms declared in pubspec.yaml.

See `04-implementation-log.md`'s final section for full detail,
including a process note: the first deletion pass for the barrel
cleanup ran broader than what was shown in the approval question before
Anton confirmed it (caught by the permission system, no data loss, but
worth remembering for future broad-deletion asks — describe scope by
listing categories, not just illustrative examples).

- **Session-wide note**: Anton is handling all git commits himself this
  session, across all flows — do not run `git add`/`commit`/`push`
  without explicit request.
- Native ttyUSB driver work remains carved out to
  `libsCpp/asterisk_chan_simbox/flows/sdd-asterisk-chan-simbox/`
  (proceeding independently, doesn't block this flow).
- Git remote: Anton removed it directly, will re-add later himself — no
  action needed from this flow.

## Progress

- [x] Requirements drafted
- [x] Requirements approved (2026-08-21)
- [x] Specifications drafted
- [x] Specifications approved (2026-08-21)
- [x] Plan drafted
- [x] Plan approved (2026-08-21)
- [x] Implementation started
- [x] Tasks 1-11 and 14 of 14 complete and verified (Task 12 covered as a
      side effect of 8-11; Task 13 has minimal real coverage)
- [x] Both post-implementation Blockers resolved per Anton's decisions
- [x] Implementation complete

## Context Notes

Specifications drafted (2026-08-21), grounded in actual source reads, not
guesses:

- **Rename checklist** is file-by-file concrete (pubspec, Dart files/
  classes, Android Gradle+manifest+7 Kotlin files, tests, example app).
  One judgment call flagged: `GatewayDialerModule`/`HeadlessModule`/
  `HeadlessService`/`HeadlessEventService` (Kotlin) recommended to STAY
  in `flutter_gsm` (renamed, not deleted) since headless/dialer-
  replacement is a GSM-radio-session concern, not SIP-bridging — confirm
  in plan.
- **Android `ModemRepository` mapping** designed against `flutter_dialer`/
  `flutter_tele`'s real APIs (read from source): dial/answer/hangup/hold/
  mute/speaker are real implementations; AT-command/firmware/diag
  methods correctly stay unsupported (no Android equivalent exists).
  `sendSms` recommended via `flutter_smsussd`; `sendUssd` has no Android
  path, stays unsupported. Two things need plan-phase verification
  against `flutter_tele`'s native Kotlin (not just its Dart surface):
  whether SIM slots enumerate before `TeleEndpoint.start()`, and the
  exact event-type strings `on()` emits.
- **Capability-gap check done for real** (Should-Have from requirements):
  compared `flutter_gsmsip`'s actual `SipRepositoryImpl` calls against
  `flutter_nmsip`'s real `FlutterSip2` API. Command surface (account CRUD
  minus unregister, call control) is covered. Real gaps found:
  `attendedTransfer` (no equivalent), `unregisterAccount` (only
  `deleteAccount` exists), `isConnected`/`isInitialized`/`accounts`/
  `activeCalls` (no state-query API — `flutter_nmsip` only exposes
  commands + one raw event stream). **Conclusion**: `flutter_gsmsip`'s
  orchestrator needs a local `SipStateTracker` component (demux
  `eventStream`, track accounts/calls itself) — "thin" doesn't mean
  "zero logic." Recommended: delete embedded `sip_service.dart` PJSIP
  glue, build the state tracker, document `attendedTransfer`/
  `unregisterAccount` as known gaps to resolve in plan (workaround or
  flag as a `flutter_nmsip` feature request).

Key decisions and context for resuming:

- **Workspace reorganized since the prior session** (2026-08-20 →
  2026-08-21): `libs/` is now split into `libsFlutter/`, `libsAndroid/`,
  `libsReactNative/`, with several new sibling packages that materially
  change this flow's scope (see below). Any future session resuming this
  flow should re-orient from this new layout, not the old `libs/` one.
- `libsFlutter/flutter_gsm` is a raw filesystem copy of
  `libsFlutter/flutter_gsmsip` taken *after* `sdd-flutter_gsmsip-
  interface`'s Modem/GSM work landed — so it already contains
  `ModemDevice`/`ModemRepository`/`LinuxFlutterGsmsip`/etc., still under
  the `flutter_gsmsip` bundle identity. It also still contains the SIP/
  SMPP/Gateway/Telephony bridging code (`sip_service.dart`,
  `gateway_service.dart`, `telephony_service.dart`, `smpp_service.dart`)
  that needs to move back out / be replaced by dependencies.
- Its `.git` carries real history and the **same remote** as
  `flutter_gsmsip` — flagged as a Must-Have to fix before any push.
- Research surfaced that `flutter_gsmsip`'s embedded SIP/Android-telephony
  code is likely **redundant** with already-existing sibling packages:
  `flutter_nmsip` (real PJSIP SIP client, built on `libsAndroid/
  sip2-android-core`), `flutter_dialer` + `flutter_tele` (Android
  dialer-replacement/InCallService call control, confirmed direct
  successors of `react-native-replace-dialer`/`react-native-tele` via
  matching method names). This reshapes the "improve upon it" ask from
  the prior flow into something bigger than a rename: `flutter_gsmsip`
  should likely become a thin orchestrator over `flutter_gsm` (GSM leg)
  + `flutter_nmsip` (SIP leg), not keep its own embedded implementations.
  This is proposed in requirements, not yet decided by Anton.
- `flutter_gsmsip/flows/sdd-split-lib-and-example` is a *different*,
  older, stalled flow (lib/example split, not GSM/SIP split) — noted as
  related context, explicitly not this flow's problem to solve.
- Android's Magisk/root requirement (from `legacy/react-native-gsm-sip-
  gateway-v2015`'s `magisk/gateway/` privileged-permissions manifest) is
  a real constraint on deep telephony control (`MODIFY_PHONE_STATE`, raw
  audio capture) beyond default-dialer/`InCallService` — worth carrying
  into specifications if Android's `ModemRepository` implementation ends
  up needing it.

## Next Actions

1. **`flutter_gsm`'s entire task group (Tasks 1-7 of 14) is complete and
   verified** — 0 analyzer errors/warnings, 30/30 tests passing. Real
   Android call control now backed by `flutter_dialer`+`flutter_tele`+
   `flutter_smsussd`; Windows/macOS stubbed to match Linux.
2. **Tasks 8-11 complete and verified** — `flutter_gsmsip` is now a real
   thin orchestrator: `SipStateTracker` + rewritten `SipRepositoryImpl`
   (flutter_nmsip-backed, replacing the old embedded PJSIP-glue
   `SipService`) + `GatewayService` reshaped to source its GSM leg from
   `flutter_gsm.ModemRepository` (replacing `TelephonyService`, deleted)
   and its SIP leg from `SipRepositoryImpl`. `dart analyze lib` → 0
   errors; `flutter test` → 4/4 passing; `flutter pub get` clean for
   package + example. Also deleted, all confirmed dead via grep first:
   duplicate `data/services/{gateway_service,sip_service}.dart`, orphaned
   `gsm_sip_bridge.dart`, and a second full duplicate of the Modem-layer
   platform-interface code that `flutter_gsmsip` still had left over
   from before `flutter_gsm` existed as a separate package.
3. Task 12 (barrel/dead-code audit) is largely done as a side effect of
   2 above — worth a final pass to confirm nothing else is stale.
4. Task 13 (tests) — only `sip_state_tracker_test.dart` exists in this
   package currently; consider adding coverage for the reshaped
   `GatewayService`/`SipRepositoryImpl` wiring if feasible (no existing
   test harness pattern for method-channel-backed `flutter_nmsip`/
   `flutter_gsm` calls in this package yet, would need building one).
5. **Task 14 complete and verified** — `simbox-app` repointed from the
   stale/broken `flutter_gsmsip` path dep (`../../libs/flutter_gsmsip`,
   `libs/` no longer exists post-reorg) to `flutter_gsm` (only the
   Modem-layer types are actually used there; `flutter_gsmsip`'s SIP/
   Gateway orchestration isn't needed by this SIM-box UI at all). All 9
   importing files updated, `dart analyze` → 0 errors, `flutter test` →
   8/8 passing (full `vdd-simbox-app-uiux` regression suite).
6. **Both post-implementation Blockers resolved** — `flutter_gsm`'s
   barrel cruft deleted (barrel down to 11 real Modem-layer exports;
   `sip_call.dart` renamed to `call_state.dart`), `flutter_gsmsip`'s
   `android/` directory removed entirely (now pure Dart, no `plugin:`
   platforms in pubspec.yaml). Fallout fixed: both example apps had
   independently gone stale (referencing types removed in Tasks 8-11)
   and were rewritten to use the current real APIs. Full regression
   sweep after all of this: `flutter_gsm` 30/30, `flutter_gsmsip` 4/4,
   `simbox-app` 8/8, all `dart analyze`/`flutter pub get` clean across
   both packages + both examples + `simbox-app`.
7. **This flow is now complete** — all 14 plan tasks done, both open
   architecture questions resolved by Anton, nothing outstanding.
8. `sdd-asterisk-chan-simbox` proceeds independently — check its status
   when real (non-stub) native modem behavior is wanted; not a
   dependency of this flow's completion.
