# Implementation Plan: flutter_gsm-example

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-08-24
> Specifications: 02-specifications.md

## Summary

Work directly in `libsFlutter/flutter_gsm/example/` (never touching the
library). Four sequential phases, each independently verifiable:
scaffold the missing desktop platform folders, fix the one analyzer
error that scaffolding introduces, trim dependencies/dead code down to
what's actually used, then verify end-to-end (analyze + macOS
build/run + Android build). No production Dart logic changes are
expected — specifications found the "graceful stub" behavior already
works; this plan's only functional check is confirming that, not
building it.

## Task Breakdown

### Phase 1: Platform Scaffolding

#### Task 1.1: Add macOS/Linux/Windows platform folders
- **Description**: Run `flutter create --platforms=macos,linux,windows --project-name flutter_gsm_example .` from `libsFlutter/flutter_gsm/example/`.
- **Files**:
  - `example/macos/` - Create (generated)
  - `example/linux/` - Create (generated)
  - `example/windows/` - Create (generated)
  - `example/test/widget_test.dart` - Create (generated; broken, fixed in Task 2.1)
- **Dependencies**: None
- **Verification**: `git status` inside `libsFlutter/flutter_gsm` (nested repo) shows only new files under `macos/`, `linux/`, `windows/`, `test/` — `diff` confirms `pubspec.yaml` and `android/` are byte-identical to before.
- **Complexity**: Low (already dry-run verified in a scratch copy during specifications; no surprises expected)

### Phase 2: Fix Generated Test

#### Task 2.1: Replace placeholder widget test
- **Description**: Rewrite `test/widget_test.dart`'s single test to pump `FlutterGsmExampleApp` (the real app widget) and assert its app bar title renders, instead of the generated counter-app assertions against a nonexistent `MyApp`.
- **Files**:
  - `example/test/widget_test.dart` - Modify
- **Dependencies**: Task 1.1
- **Verification**: `flutter analyze` reports zero errors (the `MyApp isn't a class` error is gone); `flutter test` passes.
- **Complexity**: Low

### Phase 3: Dependency & Dead Code Cleanup

#### Task 3.1: Delete dead code directories
- **Description**: Delete `example/lib/theme/`, `example/lib/utils/`, `example/lib/l10n/` — confirmed zero references from `main.dart` or from each other during specifications.
- **Files**:
  - `example/lib/theme/` - Delete
  - `example/lib/utils/` - Delete
  - `example/lib/l10n/` - Delete
- **Dependencies**: None (independent of Phase 1/2, but ordered after so any accidental new analyze errors are attributable to one change at a time)
- **Verification**: `flutter analyze` — the 25 theme/utils lint issues from the original baseline disappear; no new errors from removing them (nothing else imports these paths).
- **Complexity**: Low

#### Task 3.2: Trim `pubspec.yaml`
- **Description**: Remove the 19 confirmed-unused entries from `dependencies:` (`provider`, `shared_preferences`, `flutter_svg`, `google_fonts`, `device_info_plus`, `permission_handler`, `crypto`, `logger`, `http`, `connectivity_plus`, `workmanager`, `intl`, `dartz`, `equatable`, `get_it`, `flutter_local_notifications`, `collection`, `flutter_localizations`, `cupertino_icons`); remove `generate: true` from the `flutter:` section. Keep `flutter`, `flutter_gsm` (path), `flutter_test`, `flutter_lints`, and the entire `dependency_overrides` block untouched.
- **Files**:
  - `example/pubspec.yaml` - Modify
- **Dependencies**: Task 3.1 (must delete the code using `intl`/`flutter_localizations` before removing those deps, else `flutter pub get`/analyze would still need them)
- **Verification**: `flutter pub get` succeeds; `flutter analyze` still zero errors; `grep -rl "package:X" lib/` confirms no removed package is imported anywhere left in `example/lib/`.
- **Complexity**: Low

### Phase 4: Verification

#### Task 4.1: Full analyze + macOS build/run
- **Description**: Run `flutter analyze` (expect 0 errors) and `flutter build macos --debug`, then launch the built `.app` and confirm it (a) shows the modem list screen, (b) does not crash when `listModems()` hits `MacosFlutterGsm`'s stub — i.e., empirically re-confirm the specifications-phase finding still holds after cleanup.
- **Files**: None (verification only)
- **Dependencies**: Tasks 1.1, 2.1, 3.1, 3.2
- **Verification**: Build succeeds; app process stays alive after launch; UI shows the "Modem driver is not available on this platform yet" message rather than a crash/red screen.
- **Complexity**: Low

#### Task 4.2: Android regression check
- **Description**: Confirm the pre-existing `android/` platform still builds after the `pubspec.yaml`/dead-code changes (Should-Have from requirements, since `AndroidFlutterGsm` is a real, non-stub implementation and its example path shouldn't regress).
- **Files**: None (verification only)
- **Dependencies**: Tasks 3.1, 3.2
- **Verification**: `flutter build apk --debug` succeeds from `example/`.
- **Complexity**: Low (no device/emulator to actually run it here — build success is the achievable bar, matching the Should-Have's own scope)

#### Task 4.3: Linux/Windows scaffold-only confirmation
- **Description**: Document (in `04-implementation-log.md`) that Linux/Windows are scaffolded and analyze-clean but not build/run-verified, since this macOS host's Flutter tooling refuses `flutter build linux`/`windows` cross-host (confirmed during specifications). Not a task that changes files — a recorded limitation.
- **Files**: None
- **Dependencies**: Task 1.1
- **Verification**: N/A — documentation only
- **Complexity**: Low

## Dependency Graph

```
Task 1.1 ─→ Task 2.1 ─┐
                       ├─→ Task 4.1 ─→ Task 4.2
Task 3.1 ─→ Task 3.2 ─┘
                       └─→ Task 4.3
```

## File Change Summary

| File | Action | Reason |
|------|--------|--------|
| `example/macos/` | Create | Enable native macOS build/run on this dev machine |
| `example/linux/` | Create | Platform parity with library's declared support; scaffold+analyze only here |
| `example/windows/` | Create | Same as Linux |
| `example/test/widget_test.dart` | Create then Modify | Generated broken by scaffolding; fixed to a real smoke test |
| `example/lib/theme/` | Delete | Dead code, zero references |
| `example/lib/utils/` | Delete | Dead code, zero references |
| `example/lib/l10n/` | Delete | Dead code, zero references; also frees `intl`/`flutter_localizations` |
| `example/pubspec.yaml` | Modify | Remove 19 unused dependencies + `generate: true` |

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| `flutter create` behaves differently in the real repo than the scratch spike (e.g. picks up a stray `.metadata`/git state) | Low | Low | Diff `pubspec.yaml`/`android/` immediately after running it (Task 1.1's own verification step); abort and investigate if anything unexpected changes |
| Removing a "confirmed unused" dependency turns out to be used via some indirect mechanism (e.g. asset generation, not a Dart import) | Low | Medium | `flutter pub get` + `flutter analyze` + `flutter build macos --debug` + `flutter build apk --debug` all re-run after cleanup, not just after scaffolding — catches build-time breakage even if grep missed a usage |
| Android build regresses from pubspec/dead-code changes | Low | Medium | Task 4.2 explicitly re-verifies Android build after cleanup, not just before |
| Nested `libsFlutter/flutter_gsm` git repo — changes here don't automatically get committed to the outer monorepo | N/A (informational) | N/A | Confirm with Anton whether/how to commit inside the nested repo once done; not this plan's call to make unilaterally |

## Rollback Strategy

`libsFlutter/flutter_gsm` is its own git repo with a clean working tree
as of this flow's start (confirmed via `git status --short`). If any
step goes wrong:

1. `git status`/`git diff` inside `libsFlutter/flutter_gsm` to see
   exactly what changed.
2. `git checkout -- <path>` / `git clean -fd <path>` for the specific
   generated/modified paths (scoped, not a blanket reset) to return to
   the pre-flow state.
3. Since nothing outside `example/` is touched, worst case is deleting
   the new `example/{macos,linux,windows}/` folders and restoring
   `example/pubspec.yaml`/`example/lib/` from git.

## Checkpoints

After each phase, verify:

- [ ] `flutter analyze` run and result recorded (error count trending
      to zero, not up)
- [ ] `git status`/`diff` reviewed for unexpected changes outside the
      phase's stated files
- [ ] Behavior matches specifications (especially Task 4.1's "no crash
      on stub" re-verification)

## Open Implementation Questions

- [ ] Should the nested `libsFlutter/flutter_gsm` repo's changes be
      committed (and if so, with what commit message/scope), or left
      as uncommitted working-tree changes for Anton to review first?
      Defaulting to **leave uncommitted** unless told otherwise — this
      plan does not assume commit authority over a separate nested repo.

---

## Approval

- [ ] Reviewed by: Anton
- [ ] Approved on:
- [ ] Notes:
