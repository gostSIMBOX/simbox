# Status: vdd-flutter_dialer

## Current Phase

**REQUIREMENTS** | VISUAL | SPECIFICATIONS | PLAN | IMPLEMENTATION | DOCUMENTATION

## Phase Status

DRAFTING

## Last Updated

2026-08-31 by Claude (added interface-parity mandate against the actual
`react-native-replace-dialer` source, corrected an earlier
mischaracterization of the top-level `tdd-replace-dialer` doc)

## Blockers

- Awaiting Anton's "requirements approved" (or requested changes).
- Five Open Questions need answers before Visual can lock down screens:
  keep-or-drop `canSetDefaultDialer()` for literal interface parity,
  scope of "interface match" (public contract vs. internal bug-for-bug
  fragility), default-dialer's actual necessity for GSM auto-answer,
  which `TeleService` becomes canonical, and call-log/caller-ID scope.

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

- **Directory placement decision**: this flow lives at
  `flows/flutter_replace_dialer/vdd-flutter_dialer/`, not
  `flows/flutter_dialer/...` — matching the mapping Anton established
  earlier in this session ("flow flutter_replace_dialer (это
  flutter_dialer)"). The top-level `flutter_replace_dialer` folder is
  now the canonical home for `flutter_dialer`-package flows; this VDD
  flow sits alongside the legacy `tdd-replace-dialer` doc there.
- **Hard mandate driving this flow (Anton, verbatim intent)**:
  `flutter_dialer`'s functionality must be *only* replacing Android's
  standard dialer — everything else is explicitly out of scope. This is
  encoded as both an architectural constraint (zero dependency on
  `flutter_gsmsip`/`flutter_gsm`/`flutter_nmsip`) and a Visual-phase
  boundary (no gateway/GSM/SIP screens, ever) in `01-requirements.md`.
- **Real bugs found by reading the actual code, not assumed from
  docs**: (1) `setDefaultDialer()` always returns `true` — it fires the
  `ACTION_CHANGE_DEFAULT_DIALER` intent via plain `startActivity()` and
  never waits for the result; a `RC_DEFAULT_PHONE` constant is declared
  but unused. (2) The registered `InCallService` (`TeleService.kt`, 50
  lines) has zero connection to `FlutterDialerPlugin.kt` — no channel
  bridges call events to Dart. (3) `MainActivity`'s `tel:` intent
  handler is a dead stub.
- **Scope leakage found in sibling packages** (not this flow's to fix,
  but blocking clean reasoning about this one): `flutter_gsm` has its
  own duplicate `ReplaceDialerModule.kt` (ironically implements the
  activity-result-listener pattern *correctly*, unlike this package's
  own copy) and a `GatewayDialerModule.kt` mixing gateway concerns into
  dialer-shaped code. `flutter_tele` has its own, different, 520-line
  `TeleService`/`InCallService` — same class name, same role, unrelated
  implementation. None of these get fixed *here*; `flutter_gsm`'s
  duplicate deletion is flagged for that package's own not-yet-opened
  flow.
- **Three pre-existing spec locations reconciled**: this flow supersedes
  `libsFlutter/flutter_dialer/flows/sdd-android-plugin/` (embedded,
  DRAFT, closest to correct architecture but missed the callback bug) on
  scope/architecture questions — kept for reference, not deleted.
- **Correction to an earlier claim in this same flow**: the top-level
  `flows/flutter_replace_dialer/tdd-replace-dialer/` doc is **not**
  unrelated legacy noise — `diff` confirmed it's byte-identical to
  `reactntive/react-native-replace-dialer/flows/tdd-replace-dialer/`,
  i.e. a direct copy of the porting source's own spec, placed here
  presumably as the intended reference. Don't repeat the "different
  codebase, ignore it" framing from this flow's first draft.
- **Interface-parity mandate (Anton, second directive)**: `flutter_dialer`'s
  API must match `react-native-replace-dialer`'s. Read the actual
  reference source (not its stale README) to ground this: `src/
  ReplaceDialer.js` exposes exactly two methods,
  `isDefaultDialer(cb)`/`setDefaultDialer(cb)`, callback-based, **no
  `canSetDefaultDialer`** (that's a Flutter-era-only addition present in
  both `flutter_dialer` and `flutter_gsm`'s duplicate — flagged as an
  open question, not silently kept). `isDefaultDialer()` short-circuits
  to `true` below Android API 23 — part of the interface, must be
  preserved.
- **The exact callback-timing bug already found in `flutter_dialer` is a
  literal bug-for-bug port** of a bug that exists — and is already
  documented with a proposed fix — in the reference's own
  `ReplaceDialerModule.java` (`startActivityForResult()` immediately
  followed by `myCallback.invoke(true)`, with a commented-out
  `ActivityEventListener`/`onActivityResult()` left as evidence of an
  unfinished fix) and its own `flows/adr-001-activity-result/context.md`.
  That ADR's proposed fix is exactly the `ActivityAware`+
  `addActivityResultListener` pattern already correctly implemented in
  `flutter_gsm`'s `ReplaceDialerModule.kt` — strong confirmation that
  file is the right thing to port from, not just a coincidence.
- **Cross-flow dependency**: `flows/flutter_gsmsip/vdd-flutter_gsmsip-
  example-uiux`'s "Default Dialer status card" AC reads whatever API
  this flow ships — keep that flow's status in sync once Specifications
  land here.

## Fork History

N/A — new flow, not a fork.

## Next Actions

1. Get "requirements approved" from Anton, plus answers to the three
   Open Questions (GSM auto-answer's actual dependency on default-dialer
   status, `flutter_tele` vs. `flutter_dialer` `TeleService` canonicity,
   call-log/caller-ID in-or-out).
2. On approval, draft `02-visual.md`: ASCII mockups for default-dialer
   status/setup, incoming call, active call, dial pad — and, if scoped
   in, call log. No gateway/GSM/SIP visual language anywhere.
