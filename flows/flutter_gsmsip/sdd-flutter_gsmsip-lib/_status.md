# Status: sdd-flutter_gsmsip-lib

## Current Phase

**REQUIREMENTS** | SPECIFICATIONS | PLAN | IMPLEMENTATION

## Phase Status

DRAFTING

## Last Updated

2026-08-31 by Claude

## Blockers

- Awaiting Anton's "requirements approved" (or requested changes).
- Two Open Questions in `01-requirements.md` need Anton's call before
  Specifications can commit to a design: (1) does multi-profile config
  belong in the library at all, (2) is a `GatewayCapabilities` proxy
  object worth adding given it has nothing of its own to check.

## Progress

- [x] Requirements drafted
- [ ] Requirements approved
- [ ] Specifications drafted
- [ ] Specifications approved
- [ ] Plan drafted
- [ ] Plan approved
- [ ] Implementation started
- [ ] Implementation complete

## Context Notes

Key decisions and context for resuming:

- **Origin**: split out of `flows/flutter_gsmsip/vdd-flutter_gsmsip-
  example-uiux` at Anton's explicit request — that flow is UI/UX-only
  for `example/**`; anything requiring changes under
  `libsFlutter/flutter_gsmsip/lib/**` belongs here instead.
- **Scope**: exactly four items, no more (see `01-requirements.md`'s
  "What's moving here" table): (1) public config save/clear API on
  `GatewayService` — real gap, only a private `_saveConfiguration()`
  exists today; (2) multi-profile config support; (3) whether/how a
  Magisk-capability model belongs in this pure-Dart package; (4)
  documenting the permission contract this library can't enforce itself
  (no `android/` folder — confirmed by design, not an oversight).
- **Important negative finding, already resolved — don't redo**: GSM→SIP
  auto-bridging (the core "gateway mode" behavior both
  `react-native-gsm-sip-gateway` and `gsm2sip` implement) **already
  exists** in `GatewayService._handleIncomingGsmCall()`
  (`gateway_service.dart:291`), gated by `GatewayConfig.routeGsmToSip`/
  `.autoAnswer`, producing `CallRouting` events on `routingStream`. This
  is not a lib gap — the UI flow just needs to surface the existing
  `statusStream`/`routingStream`/`activeRoutings` API. Confirmed by
  reading the actual source, not assumed.
- **`sdd-voiceline-mode-magisk-v2`'s `LineInfo`/`line_info.dart` design
  doesn't map onto this codebase** — its target package
  (`one.telefon.gateway`) matches neither `flutter_gsmsip/example`
  (`org.telon.flutter_gsmsip_example`) nor `gsm2sip`
  (`com.callagent.gateway`). Treat that spec as design inspiration for
  the *shape* of capability flags, not as a literal file-path target.
- **Cross-flow dependency**: `vdd-flutter_gsmsip-example-uiux`'s Setup/
  Capabilities screens are blocked on this flow's API decisions (AC1–4
  of its own requirements reference this flow by name) — keep both
  `_status.md` files in sync as this progresses.

## Fork History

N/A — new flow, not a fork.

## Next Actions

1. Get "requirements approved" from Anton, along with answers to the two
   Open Questions (multi-profile scope, capability-model existence).
2. On approval, draft `02-specifications.md`: exact method signatures
   for `saveConfiguration`/`clearConfiguration`, the multi-profile domain
   model decision, and the capability-model decision (or explicit
   "out of scope, proxy via permission_handler in the app" conclusion).
