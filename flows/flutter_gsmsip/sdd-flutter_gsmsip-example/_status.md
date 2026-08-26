# Status: sdd-flutter_gsmsip-example

## Current Phase

IMPLEMENTATION

## Phase Status

REVIEW

## Last Updated

2026-08-24 by Claude (all 18 planned tasks executed; awaiting Anton's
review before marking complete)

## Blockers

- Not blocking this flow's own completion, but flagged for Anton's
  attention:
  1. **l10n wiring deferred, not deleted**: Task 2.8's locale-count
     checkpoint (keep 36 vs. trim) is still unresolved, so the 6 new
     screens ship with hardcoded English strings and `l10n/` is left
     completely untouched (neither wired in nor pruned).
  2. **Android build is currently broken for anyone**, not just this
     example: `flutter build apk --debug` fails with 97 Java compile
     errors inside `flutter_nmsip`'s native Android code (missing
     `WritableMap`/`Gson`/etc. symbols — looks like a missing Gradle
     dependency in `flutter_nmsip/android/build.gradle`). Confirmed
     pre-existing (that source is unmodified per `git status`), not
     caused by this flow. Since Android was supposed to be the one
     platform where everything actually works, this is worth its own
     fix.
  3. **Linux build/run unverified**: this dev machine is macOS, not
     Linux (a wrong assumption baked into `01`–`03`'s "this dev
     machine" wording) — `flutter build linux` can't run here at all
     (host-only limitation). Manual verification used macOS instead.
  4. **Unrelated pre-existing uncommitted state discovered, not
     touched**: `flutter_gsmsip/README.md` (top-level) has a leftover
     1-line uncommitted correction from a prior flow, and the sibling
     `flutter_gsm/example/` (never in this flow's scope) has its own
     large uncommitted cleanup (theme/l10n/utils removed, platform
     folders added) that predates this session. Investigated carefully
     (see `04-implementation-log.md`'s "Pre-flight check" section) and
     concluded neither came from this session's tool calls — left
     entirely alone either way, just flagging so Anton isn't surprised
     by `git status` showing changes outside this flow.

## Progress

- [x] Requirements drafted
- [x] Requirements approved (2026-08-24)
- [x] Specifications drafted
- [x] Specifications approved (2026-08-24)
- [x] Plan drafted
- [x] Plan approved (2026-08-24)
- [x] Implementation started
- [x] Implementation complete (all 18 tasks executed 2026-08-24; 3
      explicitly flagged gaps above, not silently glossed over)

## Context Notes

Key decisions and context for resuming:

- Task: bring `libsFlutter/flutter_gsmsip/example` into a working state
  that genuinely exercises the library, **without modifying the library**
  (`libsFlutter/flutter_gsmsip/lib/**`), per Anton's instruction.
- Investigated current state before drafting requirements (no assumptions):
  the example **already compiles clean** (`flutter analyze` → 0 errors),
  but can't functionally demonstrate the library — no setup UI, so
  `GatewayService.loadConfiguration()` always returns null and `Start
  Gateway` always fails with "No configuration found."
- `example/README.md` is stale/fictional: documents a `GsmSipBridge` API
  and `screens/` folder that don't exist. Real API is `GatewayService`
  (GSM leg via `flutter_gsm`'s `ModemRepository`, SIP leg via
  `SipRepositoryImpl`/`flutter_nmsip`).
- Confirmed via reading sibling-lib pubspecs: `flutter_nmsip` (SIP) only
  declares an **Android** platform implementation. `flutter_gsm` (GSM/
  modem) has a real Linux driver (`SimboxModemRepository`, FFI→
  libsimbox, 818 lines) but only a ~90-line unimplemented stub on macOS.
  This is a hard ceiling on what "working" can mean per platform without
  touching sibling libraries — out of scope for this flow.
- Anton's decisions (2026-08-24, via `AskUserQuestion`):
  1. **Sequencing**: fix `example/README.md` to match the library's real
     implementation *first*, then rebuild the example app to match that
     corrected README (not the other way around, not leaving README
     stale).
  2. **Platforms**: Android + Linux + macOS all in scope for this flow
     (Anton added macOS himself beyond the two options offered).
  3. **Non-Android honesty**: build/run on all 3 platforms, but
     README + in-app UI must honestly surface the real per-platform
     capability ceiling (table above) — Start Gateway should fail with a
     specific, honest reason on Linux/macOS, not a silent no-op or
     generic error.
- Example currently only has an `android/` platform folder — `linux/`
  and `macos/` platform scaffolds need to be created as part of this
  flow's Plan/Implementation.
- SDK version mismatch noted as an open question for Specifications:
  library declares `sdk: ^3.10.8`, example currently declares
  `sdk: ^3.8.1`.

## Next Actions

1. Anton to review `03-plan.md` and either approve ("plan approved") or
   request changes.
2. On approval, move to IMPLEMENTATION starting with Task 1.1 (README
   rewrite), per the plan's sequencing.

## Plan Highlights (for resuming without re-reading the doc)

- **New finding while planning**: `git log --diff-filter=D -- example/
  lib/screens` (commit `e8f586d "example working"`) shows the example
  used to have a full `screens/` folder that was a wholesale copy of the
  much bigger `simbox-app`'s screens (base stations, SIMs, codecs, USSD,
  language, theme-demo — matches `flows/_archive/vdd-screens/*` exactly).
  None of that corresponds to anything `GatewayService` actually has —
  correctly deleted. But `theme/app_widgets.dart` (has purpose-built
  `signalIndicator`/`connectionIndicator`/`callStatusIndicator`/
  `statusCard`) and `l10n/app_en.arb` (has `sipUsername`/`sipPassword`/
  `sipServer`/`sipPort`/`connect` keys) were left behind unreferenced —
  these were clearly meant for exactly the Setup/Dashboard screens this
  plan builds. **Decision: reuse them, don't delete.** Only
  `utils/easter_eggs.dart`, `utils/funny_messages.dart`, `utils/
  imei_validator.dart` are genuinely unused cruft — those get deleted.
- **Mid-implementation checkpoint, not a phase gate**: Task 2.8 needs
  Anton's call on whether to keep all 36 `l10n` locales or trim to
  en/ru before deleting any `.arb` file — flag this when reached, don't
  decide unilaterally.
- 12 tasks across 4 phases (README → foundation classes → 6 screens →
  platform scaffolds → verification). Full task-by-task detail,
  dependency graph, and file list are in `03-plan.md` — this section is
  only a resumability summary, not a substitute for reading it.

## Specifications Highlights (for resuming without re-reading the doc)

- **Config persistence gap**: `GatewayService` has no public save/clear
  method — only a private `_saveConfiguration()` triggered inside
  `initialize()`, which never runs if SIP init fails (always true on
  Linux/macOS). Fix (without touching the lib): new example-local
  `ExampleConfigStore` reads/writes `SharedPreferences['gateway_config']`
  directly using `GatewayConfig`'s already-public `toJson()`/`fromJson()`
  — same key/shape the lib itself uses. Accepted risk: that key is an
  implementation detail, not a public contract; documented in the new
  README.
- **Call screen scope**: `GatewayService` only exposes
  `makeCallViaSip`/`makeCallViaGsm`/`endRouting`/`endAllRoutings`/
  `getActiveRoutings`/`routingStream` — no answer/hold/mute/DTMF (those
  exist on `SipRepository` but aren't proxied by `GatewayService`). The
  Call screen must not invent controls for these.
- **SMS/Logs data source**: `SmsService()` and `flutter_gsm`'s
  `ModemRepositoryImpl()` are independently-instantiable public
  singletons/classes — example reads them directly rather than through
  `GatewayService`'s private internals.
- **SMPP is simulated** in the library today (`sms_service.dart`'s own
  comments admit it: `Future.delayed` + always-connected, random 95%
  delivery roll) — the example must say so plainly in its README, not
  present it as real.
- **Platform capability table** (hand-derived from reading sibling libs,
  not queryable at runtime): SIP → Android only; GSM modem → Android +
  Linux only (macOS throws typed `ModemDriverNotAvailableException`).
