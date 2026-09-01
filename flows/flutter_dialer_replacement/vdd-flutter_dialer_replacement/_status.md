# Status: vdd-flutter_dialer

## Current Phase

REQUIREMENTS | VISUAL | SPECIFICATIONS | PLAN | **IMPLEMENTATION** | DOCUMENTATION

## Phase Status

NEARLY COMPLETE — all 17 plan tasks done except Task 4.3 (manual
device verification), which needs Anton and a physical Android device.

## Last Updated

2026-08-31 by Claude (Phases 1–4 implemented and verified by every
automated means available. Package renamed mid-session from
`flutter_dialer` to `flutter_dialer_replacement` (Anton, matching the
directory name) — reconciled across every actual dependent in this
flow's build path (`flutter_tele`, this package's own tests/example/
README). Applied the `nativemind-designsystem` skill's tokens to the
Status & Setup screen and app-wide `ThemeData`; other 4 screens not yet
converted. All verification re-run green afterward: `flutter analyze`
clean, `flutter test` passing, 7/7 native unit tests, `flutter build
apk --debug` succeeding. Only Task 4.3 — real-device manual
verification — remains, blocked on hardware not present here.)

## Blockers

- **Boundary clarified**: `flutter_tele` is a separate, unrelated
  library — this flow depends on it (example app only) but must never
  edit its files or fold its functionality into
  `flutter_dialer_replacement`. Reverted an earlier overreach where
  this flow edited `flutter_tele`'s own `pubspec.yaml`/`dialer.dart` to
  follow the rename; Anton fixed those files himself instead. Task
  1.3's decision (no InCallService inside `flutter_dialer_replacement`,
  `flutter_tele` used externally for call-state) was confirmed correct,
  not reverted.
- **Task 4.3 (Manual device verification) needs Anton.** `adb devices`
  returns empty in this environment — no physical device or emulator to
  run `03-specifications.md`'s checklist (accept/decline the real
  system dialog, cold/warm `tel:` intent launch, real call-log match,
  single-`InCallService` manifest check).
- **Design-system pass is partial**: only `main.dart`'s `ThemeData` and
  `status_screen.dart` use the NativeMind DS tokens
  (`example/lib/design/`). Dial Pad, Incoming Call, Active Call, and
  Call Log screens still use plain Material defaults — not yet
  converted. Not a functional blocker, but incomplete if Anton expects
  full visual consistency across all 5 screens.
- Documentation phase (optional, client-facing README) not started —
  `README.md` still describes the old always-`true` `setDefaultDialer()`
  and doesn't mention `getCallLog()`/`initialNumber()`/`numberStream`
  (its two usage-example imports were fixed for the rename, but the
  content itself wasn't updated for the new APIs).
- Discovered mid-implementation: `flutter_gsm/pubspec.yaml`'s
  `dependency_overrides` has a stale path (`path: ../flutter_dialer`) —
  the actual directory is `flutter_dialer_replacement` (renamed at some
  point). Out of this flow's scope to fix (it's `flutter_gsm`'s file);
  flagged here for whoever opens that package's own flow, alongside the
  already-flagged `ReplaceDialerModule.kt` duplicate-deletion item.
- Discovered mid-implementation: `flutter_dialer_replacement/flows/
  tdd-incall-service/` is a pre-existing TDD flow planning work on the
  now-deleted `TeleService.kt` — superseded by this flow's decision
  (AC2) to delegate call-state to `flutter_tele` instead. Kept for
  historical reference, not deleted, same policy as this flow's other
  superseded docs.
- One non-blocking open item carried forward (does not block this flow):
  whether `flutter_gsmsip`'s GSM auto-answer path actually requires
  default-dialer status — affects `flutter_gsmsip`'s own flow, not this
  one's mockups.
- Separate, out-of-band item raised by Anton: `react-native-replace-dialer`
  (the reference package) has its own unfixed callback-timing bug,
  already documented in its own `flows/adr-001-activity-result/` +
  `flows/tdd-replace-dialer/`. Recommended NOT to open a new VDD flow for
  it (no UI/visual change involved, it's a native-bridge bug fix) —
  resume/complete its existing `tdd-replace-dialer` flow instead, as a
  separate task, whenever Anton wants it addressed. Not started.

## Progress

- [x] Requirements drafted
- [x] Requirements approved (2026-08-31)
- [x] Visual drafted
- [x] Visual approved (2026-08-31)
- [x] Specifications drafted
- [x] Specifications approved (2026-08-31)
- [x] Plan drafted
- [x] Plan approved (2026-08-31)
- [x] Implementation started
- [x] Implementation complete (except Task 4.3, needs Anton + device)
- [ ] Documentation drafted (optional phase, not started)
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

1. **Anton runs Task 4.3** (manual device verification) per
   `03-specifications.md`'s checklist — this is the only remaining item
   before Implementation can be marked fully COMPLETE. Needs a physical
   Android device or emulator, which this environment doesn't have.
2. Anton reviews the two deliberate deviations flagged in
   `05-implementation-log.md`: the `canSetDefaultDialer()` semantics
   change's effect on the Status & Setup button visibility
   (`if (canSet)` → `if (!isDefault)`), and the DTMF keypad being
   UI-only (no send-tone API exists in `flutter_tele` yet).
3. If Anton wants full visual consistency, extend the design-system
   pass (`example/lib/design/`) to the remaining 4 screens (Dial Pad,
   Incoming Call, Active Call, Call Log) — currently only `main.dart`'s
   theme and `status_screen.dart` use it.
4. Decide whether to proceed to the optional Documentation phase
   (client-facing README — the current one still describes the old
   always-`true` `setDefaultDialer()` and doesn't mention the 3 new
   APIs), or close this flow as done once 4.3 passes.
5. Separately, decide whether/when to act on the two cross-package
   follow-ups this flow surfaced but didn't fix (out of scope here):
   `flutter_gsm`'s stale `dependency_overrides` path, and its
   `ReplaceDialerModule.kt` duplicate — both packages also still
   reference the pre-rename `flutter_dialer` name in their own
   pubspec.yaml/pubspec.lock, unrelated to this flow's build.
