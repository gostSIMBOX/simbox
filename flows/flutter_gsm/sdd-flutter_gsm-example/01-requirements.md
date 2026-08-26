# Requirements: flutter_gsm-example

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-08-24

## Problem Statement

`libsFlutter/flutter_gsm/example` is a Flutter plugin example app meant to
demonstrate `ModemRepository` usage from the `flutter_gsm` library. Right
now it cannot actually be *run* and verified on this development machine:

- The example directory only ships an `android/` platform runner folder.
  This dev machine has no Android device or emulator attached — only
  macOS desktop and Chrome are available via `flutter devices` — so there
  is currently no way to build-and-launch the example at all here.
- Even once a desktop platform folder exists, `flutter_gsm`'s macOS/
  Linux/Windows backends (`MacosFlutterGsm`, `LinuxFlutterGsm`,
  `WindowsFlutterGsm`) are deliberate stubs: every `ModemRepository`
  method throws `UnimplementedError('...: implemented by
  sdd-asterisk-chan-simbox')` (confirmed by reading
  `lib/src/macos/macos_flutter_gsm.dart`). The example's
  `_ModemListScreenState._refresh()` only catches `ModemException`, so
  that `UnimplementedError` would propagate uncaught and crash/red-screen
  the app instead of showing a usable UI.
- `example/pubspec.yaml` declares ~15 dependencies (`provider`,
  `shared_preferences`, `flutter_svg`, `google_fonts`, `device_info_plus`,
  `permission_handler`, `crypto`, `http`, `connectivity_plus`,
  `workmanager`, `dartz`, `equatable`, `get_it`,
  `flutter_local_notifications`, `collection`) that current `main.dart`
  never imports, and `example/lib/theme/`, `example/lib/utils/`,
  `example/lib/l10n/` hold dead code left over from an earlier, richer
  example — confirmed unreferenced by the current minimal `main.dart`.
  `flutter analyze` currently passes (25 info/warning-level lint issues,
  zero errors) precisely because this dead code still compiles on its
  own; it doesn't get exercised by running the app.

This flow makes the example buildable and runnable on the platforms
available in this dev environment, makes it degrade predictably instead
of crashing where the underlying library is still a stub, and removes
the unused weight so "working state" is honest — all **without changing
`flutter_gsm` itself** (library code, `pubspec.yaml`, or its native
Android/plugin registration are out of scope; the library is the fixed
point, the example adapts to it).

## User Stories

### Primary

**As a** developer evaluating or extending `flutter_gsm`
**I want** to run the example app on my desktop (macOS/Linux/Windows) or
Android and see it build, launch, and exercise `ModemRepository`
**So that** I can verify the library's public API surface actually works
end-to-end without needing real modem hardware or a device I don't have
attached

### Secondary

**As a** contributor adding a real native backend later (e.g. finishing
the `sdd-asterisk-chan-simbox`-backed macOS/Linux driver)
**I want** the example to already show a clear "not implemented on this
platform" state for stubbed platforms
**So that** I have a working baseline UI to wire real data into, instead
of a crash

## Acceptance Criteria

### Must Have

1. **Given** the example app on a machine with no Android device/emulator
   **When** the developer runs `flutter run -d macos` (or `linux`/
   `windows`) from `libsFlutter/flutter_gsm/example`
   **Then** the app builds and launches, using newly-added
   `macos/`, `linux/`, `windows/` platform runner folders (the existing
   `android/` folder is kept, untouched in its working parts).

2. **Given** the app is running on a platform whose `flutter_gsm` backend
   is a stub (macOS/Linux/Windows today)
   **When** `ModemRepository.listModems()` (or any other repository call
   the UI triggers) throws `UnimplementedError`
   **Then** the UI catches it distinctly from `ModemException` and shows
   a clear, non-crashing "not implemented on this platform yet" message
   instead of a red error screen.

3. **Given** `example/pubspec.yaml` and `example/lib/`
   **When** this flow completes
   **Then** every dependency in `pubspec.yaml` is actually used by the
   example's code, and `example/lib/theme/`, `example/lib/utils/`,
   `example/lib/l10n/` (or any other file unreferenced by the app) are
   removed unless something under them is still imported.

4. **Given** the cleaned-up example
   **When** `flutter analyze` is run from `libsFlutter/flutter_gsm/example`
   **Then** it reports zero errors (warnings/info allowed, but should not
   regress from cleanup).

5. **Given** the running example (any platform)
   **When** the developer interacts with it
   **Then** it still demonstrates the same `ModemRepository` surface
   already wired up today — discover modems (`listModems`, live updates
   via `modemEvents`), dial, and send SMS — visibly reflecting
   success/failure for each action.

### Should Have

- Android platform folder verified still analyzable/buildable
  (`flutter build apk --debug` or equivalent), since it's the one
  backend (`AndroidFlutterGsm`) that may not be a pure stub — confirm
  during specifications whether Android needs any example-side fix too.

### Won't Have (This Iteration)

- No changes to `flutter_gsm` library code, its `pubspec.yaml`, or its
  platform registration (`lib/src/**`, `lib/flutter_gsm.dart`, native
  Android/plugin glue) — the library is treated as a fixed dependency.
- No implementation of real macOS/Linux/Windows modem drivers — that's
  `sdd-asterisk-chan-simbox`/`sdd-flutter_gsm-ffi`'s scope, not this
  example's.
- No expansion of the demo beyond the `ModemRepository` methods already
  wired in `main.dart` today (dial, SMS, listModems/modemEvents) unless
  specifications identify a gap needed just to prove the library works.
- No iOS or web platform support — `flutter_gsm`'s own `pubspec.yaml`
  plugin map doesn't declare either, so neither is in scope here.

## Constraints

- **Technical**: Must not modify anything under `libsFlutter/flutter_gsm/`
  outside of `libsFlutter/flutter_gsm/example/`. The library's public
  API (`ModemRepository`, `ModemRepositoryImpl`, `ModemDevice`,
  `ModemException`, `ModemEvent`, etc.) is the interface the example
  must work against as-is.
- **Platform**: Verify on whatever this dev machine actually supports —
  macOS desktop confirmed available now (`flutter devices`); Linux/
  Windows platform folders should be added for completeness/parity but
  can only be analyzed/built for, not run, on this macOS host.
- **Dependencies**: New platform runner scaffolding (`flutter create
  --platforms=...`) must not disturb the existing `android/` folder or
  `pubspec.yaml`'s existing `flutter_gsm: {path: ../}` /
  `dependency_overrides` (needed for the monorepo's
  `flutter_dialer`/`flutter_tele`/`flutter_smsussd` version-constraint
  workaround, per that pubspec's own comment).

## Open Questions

- [ ] None currently blocking — platform scope, stub-error handling, and
      cleanup scope were resolved via user decision on 2026-08-24 (see
      Context Notes in `_status.md`).

## References

- `libsFlutter/flutter_gsm/lib/src/macos/macos_flutter_gsm.dart` — stub
  pattern shared by macOS/Linux/Windows backends.
- `flows/flutter_gsm/sdd-flutter_gsm-ffi/_status.md` — prior flow that
  wired the real Linux FFI driver to `libsimbox`; macOS/Windows FFI
  binding was explicitly out of scope there too.
- `flows/flutter_gsm/sdd-flutter_gsm/04-implementation-log.md` — history
  of `flutter_gsm` being split out of `flutter_gsmsip`, relevant to why
  the example still has leftover dead weight.

---

## Approval

- [ ] Reviewed by: Anton
- [ ] Approved on:
- [ ] Notes:
