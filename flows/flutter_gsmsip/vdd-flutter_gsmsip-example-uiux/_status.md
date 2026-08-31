# Status: vdd-flutter_gsmsip-example-uiux

## Current Phase

**REQUIREMENTS** | VISUAL | SPECIFICATIONS | PLAN | IMPLEMENTATION | DOCUMENTATION

## Phase Status

**DRAFTING**

## Last Updated

2026-08-31 by Claude (split library-code items out to new sibling flow
`sdd-flutter_gsmsip-lib`, per Anton's explicit request)

## Blockers

- Awaiting Anton's "requirements approved" (or requested changes) before
  moving to VISUAL.
- AC2 (multi-profile config) and AC3 (Magisk-capability display) are now
  gated on `flows/flutter_gsmsip/sdd-flutter_gsmsip-lib/` reaching
  Specifications — don't build example-local workarounds for either
  while that flow is still in REQUIREMENTS.

## Progress

- [x] Requirements drafted
- [ ] Requirements approved
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

1. Get explicit "requirements approved" from Anton (or incorporate
   requested changes to `01-requirements.md`).
2. On approval, move to VISUAL: ASCII mockups for the new/evolved
   screens (Gateway mode, multi-profile Setup, System Capabilities,
   Default Dialer status card) plus the DS-restyled versions of the
   existing 6 screens and the splash screen.
