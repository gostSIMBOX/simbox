# Status: vdd-flutter_gsmsip-example-uiux

## Current Phase

REQUIREMENTS | **VISUAL** | SPECIFICATIONS | PLAN | IMPLEMENTATION | DOCUMENTATION

## Phase Status

APPROVED | **DRAFTING**

## Last Updated

2026-08-31 by Claude (Anton approved 01-requirements.md — moving to VISUAL)

## Blockers

- AC2 (multi-profile config) and AC3 (Magisk-capability display) are still
  gated on `flows/flutter_gsmsip/sdd-flutter_gsmsip-lib/` reaching
  Specifications — mockups for those screens can proceed, but don't lock
  their data model until that flow settles.
- Before drafting the Capabilities/Enhanced-Mode surface, coordinate with
  `flows/flutter_gsmsip/vdd-flutter_gsmsip-example-voiceline-uiux` (its
  "Enhanced Mode" screen covers similar ground) so the two flows don't
  mock up two competing versions of the same screen.

## Progress

- [x] Requirements drafted
- [x] Requirements approved
- [ ] Visual drafted
- [ ] Visual approved
- [ ] Specifications drafted
- [ ] Specifications approved
- [ ] Plan drafted
- [ ] Plan approved
- [ ] Implementation started
- [ ] Implementation complete
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

1. Draft ASCII mockups in `02-visual.md` for the new/evolved screens:
   Gateway mode, multi-profile Setup, System Capabilities, Default Dialer
   status card — plus DS-restyled versions of the existing 6 screens and
   the splash screen.
2. Reuse `flows/flutter_gsmsip/vdd-dialer`'s approved "Bridge call
   status: SIP leg + GSM leg" visual language for the Gateway screen
   rather than inventing new vocabulary.
3. Resolve the accent-colorway Open Question with `/nativemind-designsystem`
   before finalizing mockups.
4. Wait for explicit "visual approved" from Anton before moving to
   SPECIFICATIONS.
