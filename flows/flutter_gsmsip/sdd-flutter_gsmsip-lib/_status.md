# Status: sdd-flutter_gsmsip-lib

## Current Phase

**REQUIREMENTS** | SPECIFICATIONS | PLAN | IMPLEMENTATION

## Phase Status

DRAFTING

## Last Updated

2026-08-31 by Claude (added AC0: live-verified broken dependency graph —
`flutter pub get` fails today in `flutter_gsmsip` because
`libsFlutter/flutter_dialer` was renamed to `flutter_dialer_replacement`
mid-session by the sibling `vdd-flutter_dialer_replacement` flow, and
three consumers' pubspecs still reference the old name)

## Blockers

- **New, urgent, external**: `flutter_gsm`'s and `flutter_tele`'s own
  `pubspec.yaml` files still reference the pre-rename `flutter_dialer`
  package (path + pub.dev version respectively) — both need fixing
  before this flow can run `pub get`/`analyze`/`test` cleanly, even
  after fixing this package's own `dependency_overrides` (AC0). Not this
  flow's files to fix; flagged for whoever picks up `flutter_gsm`'s own
  overdue flow (already noted in `vdd-flutter_dialer_replacement`'s
  status as a cross-package follow-up).
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

- **`flutter_*` dependency graph + maturity, measured 2026-08-31** (Dart
  LOC / native Android LOC / test files, `find`+`wc -l`, not estimated):

  | Package | Depends on (path) | Dart LOC (files) | Native Android LOC (files) | Tests | Other platforms | Notes |
  |---|---|---|---|---|---|---|
  | `flutter_gsmsip` | `flutter_gsm`, `flutter_nmsip`, (+`flutter_dialer_replacement` via broken override) | 13,854 (73) | 0 (0) | 1 | none | Pure-Dart orchestrator, largest Dart surface in the family, zero native code by design |
  | `flutter_gsm` | `flutter_dialer_replacement`(broken), `flutter_tele`, `flutter_smsussd` | 4,123 (24) | 872 (8) | 10 | none | Real modem/telephony driver + FFI to `libsimbox`; most heavily depended-on package |
  | `flutter_nmsip` | none | 771 (5) | 1,174 (10) | 1 | none | Small Dart surface, PJSIP-heavy native layer (SIP/RTP) |
  | `flutter_tele` | `flutter_dialer_replacement` (broken, via pub.dev version ref) | 652 (6) | 1,038 (3) | 2 | none | `TeleService.kt` alone is 520 of the 1,038 native lines — real `InCallService` |
  | `flutter_smsussd` | none | 255 (4) | 265 (1) | 2 | ios, linux (unverified how real) | Smallest real package; SMS-only, no MMS/WAP-push backing despite the example manifest claiming it |
  | `flutter_dialer_replacement` | none | 175 (3) | 310 (2) | 2 | none | Just rebuilt end-to-end by `vdd-flutter_dialer_replacement` — smallest but most recently verified (`flutter analyze` clean, tests pass, apk builds) |

  **Dependency direction**: `flutter_gsmsip` → `flutter_gsm` +
  `flutter_nmsip`; `flutter_gsm` → `flutter_dialer_replacement` +
  `flutter_tele` + `flutter_smsussd`; `flutter_tele` →
  `flutter_dialer_replacement`. `flutter_nmsip` and
  `flutter_dialer_replacement` are the only leaves (no `flutter_*`
  deps of their own).
  **Maturity reading**: `flutter_gsm` is the load-bearing package (most
  dependents, most native code, most tests) but its own manifest is
  still empty (see `vdd-flutter_gsmsip-example-uiux`'s permission
  audit) and its pubspec is currently broken (see AC0 above).
  `flutter_gsmsip` is Dart-only and largest by LOC but has essentially
  no test coverage (1 file) for 13.8k lines — worth flagging as risk
  once this flow starts adding new public API surface (AC1–3).
  `flutter_dialer_replacement` is the freshest/most-verified despite
  being smallest. `flutter_nmsip` is a black box from this audit's
  vantage point (small Dart, big native, 1 test) — not investigated
  deeper here, out of this flow's scope.

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
