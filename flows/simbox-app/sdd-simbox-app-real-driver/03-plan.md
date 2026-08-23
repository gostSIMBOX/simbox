# Implementation Plan: simbox-app-real-driver

> Version: 1.0
> Status: APPROVED
> Last Updated: 2026-08-23
> Specifications: [02-specifications.md](02-specifications.md)

## Summary

Four phases, bottom-up: native config-dir override first (testable in
isolation on this macOS dev machine, no dependency on anything else),
then the Dart-side env var plumbing that depends on it, then
`simbox-app`'s DI swap (depends on both), then the shipped example
config + docs (depends on Phase 1's parser to validate against). A
final regression phase closes the flow out. Every phase's verification
is achievable in this development environment (no Linux host/hardware)
— real end-to-end hardware verification stays explicitly deferred, per
specifications' Manual Verification section.

## Task Breakdown

### Phase 1: Native config-dir override

#### Task 1.1: Declare + implement `simbox_config_bridge_set_dir()`
- **Description**: Add the declaration to
  `src/simbox_internal_linux.h` (alongside its existing Linux-only
  adapter-bridge functions). Implement in `adapters/src/shim_config.c`:
  a static buffer holding the override, set/cleared by the new
  function; `ast_config_load2()` tries `<override>/<filename>` first
  (if set) before its existing two-path resolution. One-line comment
  noting `#include`/`#exec` aren't handled by this parser (per
  specifications' Edge Cases — not implementing them, just flagging
  for the next person).
- **Files**:
  - `libsCpp/asterisk_chan_simbox/src/simbox_internal_linux.h` — Modify
  - `libsCpp/asterisk_chan_simbox/adapters/src/shim_config.c` — Modify
- **Dependencies**: None
- **Verification**: `make` clean (macOS build, zero regressions);
  `gcc -fsyntax-only -D__linux__` forced check on any Linux-only branch
  touched (none expected here — this function has no platform split of
  its own, only its *caller* in `simbox_api.c` does, per Task 1.2)
- **Complexity**: Low

#### Task 1.2: Wire `simbox_init()` to call it
- **Description**: Inside `simbox_init()`'s existing `#ifdef __linux__`
  block, before `simbox_populate_from_gpublic(inst)`: if
  `config && config->config_dir`, call
  `simbox_config_bridge_set_dir(config->config_dir)`.
- **Files**:
  - `libsCpp/asterisk_chan_simbox/src/simbox_api.c` — Modify
- **Dependencies**: Task 1.1
- **Verification**: `make` clean; `gcc -fsyntax-only -D__linux__
  -DHAVE_CONFIG_H` forced check on `simbox_api.c` (this flow's edit is
  inside the existing `__linux__` branch, so the forced check is what
  actually exercises it, matching the verification pattern
  `sdd-asterisk-chan-simbox` established throughout)
- **Complexity**: Low

#### Task 1.3: Native test for the override
- **Description**: Extend `tests/test_simbox.c` with a new test:
  write a temp `dongle.conf` (minimal `[general]`/one device section)
  to a temp directory, call `simbox_config_bridge_set_dir()` directly
  (or via `simbox_init()` with a populated `simbox_config_t`), confirm
  `ast_config_load()`/`ast_config_load2()` finds it there; then call
  with `NULL` and confirm the override clears (falls back to
  CWD/`/etc/asterisk/`, i.e. fails to find the temp file once it's not
  in either of those places). This tests the shim function directly —
  achievable on macOS per specifications' Testing Strategy, no real
  chan_dongle device population involved.
- **Files**:
  - `libsCpp/asterisk_chan_simbox/tests/test_simbox.c` — Modify
- **Dependencies**: Task 1.2
- **Verification**: `make && ./test_simbox` — new test passes, all
  pre-existing suites still pass (no regression)
- **Complexity**: Medium

### Phase 2: Dart-side env var plumbing

#### Task 2.1: `SimboxModemRepository` factory reads `configDir`/env var
- **Description**: Add `String? configDir` param to the factory,
  defaulting to `Platform.environment['FLUTTER_GSM_SIMBOX_CONFIG_DIR']`.
  When resolved non-null: allocate a `simbox_config_t` via its
  generated `$allocate` factory (`config_dir` set, other fields
  zeroed/false), pass to `simbox_init()`, free both the config struct
  and the `config_dir` string pointer immediately after `simbox_init()`
  returns (safe per specifications — the native side copies the string
  synchronously before returning, no async handoff like the event
  callback path).
- **Files**:
  - `libsFlutter/flutter_gsm/lib/src/linux/simbox_modem_repository.dart` — Modify
- **Dependencies**: Task 1.2 (needs the native side to actually do
  something with the passed config, though this task is separately
  syntax-valid without it)
- **Verification**: `dart analyze` clean
- **Complexity**: Low

#### Task 2.2: Test for the config-dir plumbing
- **Description**: New test constructing
  `SimboxModemRepository(configDir: <temp dir>)` (and one via the env
  var, using `Platform.environment` override if the existing test
  helper pattern supports it, otherwise via the constructor param
  directly) — confirms construction succeeds and basic operations
  (`listModems()`) still work identically to the no-config-dir case.
  Honestly scoped per specifications: proves the plumbing doesn't
  break anything on this non-Linux/simulated dev machine, not that
  real discovery works (that needs Linux + hardware, explicitly
  deferred).
- **Files**:
  - `libsFlutter/flutter_gsm/test/simbox_modem_repository_test.dart` — Modify
- **Dependencies**: Task 2.1
- **Verification**: `flutter test` — new test passes, full package
  suite still green (no regression)
- **Complexity**: Low

### Phase 3: `simbox-app` DI swap

#### Task 3.1: `SimboxApp` injection seam
- **Description**: `SimboxApp({super.key, ModemRepository? repository})`,
  `Provider<ModemRepository>`'s `create` uses the injected repository
  if given, otherwise builds `ModemRepositoryImpl()`. `dispose`
  callback only calls `.dispose()` when the resolved repository is a
  `FakeModemRepository` (per specifications — `ModemRepositoryImpl`
  has no `dispose()` to call).
- **Files**:
  - `apps/simbox-app/lib/main.dart` — Modify
- **Dependencies**: None (independent of Phases 1-2 structurally, but
  sequenced after them so the *default* real path has something real
  behind it by the time this lands)
- **Verification**: `dart analyze` clean
- **Complexity**: Low

#### Task 3.2: Update `widget_test.dart`
- **Description**: Both `pumpWidget(const SimboxApp())` calls become
  `pumpWidget(SimboxApp(repository: FakeModemRepository()))` — same
  assertions, now decoupled from `FlutterGsmPlatform.instance`
  resolution / native library presence during `flutter test`.
- **Files**:
  - `apps/simbox-app/test/widget_test.dart` — Modify
- **Dependencies**: Task 3.1
- **Verification**: `flutter test test/widget_test.dart` — both tests
  pass, identical assertions to before
- **Complexity**: Low

### Phase 4: Example config + documentation

#### Task 4.1: `dongle.conf.example`
- **Description**: A minimal, validated one-device example (adapted
  from the read-only reference at
  `asterisk_chan_svistok/chan_svistok/etc/dongle.conf`, not copied
  verbatim — trimmed to what a first-time real setup actually needs:
  `[general]`, `[defaults]`, one `[dongleN]` section with
  `audio=`/`data=` placeholders). "Validated" means: actually parses
  cleanly through the adapter's config loader, confirmed via a
  temporary one-off invocation of Phase 1's test infrastructure (point
  `simbox_config_bridge_set_dir()` at this file's real directory,
  confirm `ast_variable_browse()` returns the expected categories/
  values) — not just visually plausible.
- **Files**:
  - `apps/simbox-app/dongle.conf.example` — Create
- **Dependencies**: Task 1.3 (reuses its test infrastructure to validate)
- **Verification**: One-off validation run (see Description); file
  committed with a header comment explaining it's a template, not
  auto-loaded
- **Complexity**: Low

#### Task 4.2: README section
- **Description**: Append (not rewrite — the file's pre-existing
  content mismatch, per specifications' Edge Cases, is out of scope) a
  new "🔌 Real Hardware Setup (Linux)" section to
  `apps/simbox-app/README.md`: build `libsimbox`, copy
  `dongle.conf.example` to a real location, set
  `FLUTTER_GSM_SIMBOX_CONFIG_DIR` (and `FLUTTER_GSM_SIMBOX_LIB` if
  needed), attach real hardware, `flutter run`.
- **Files**:
  - `apps/simbox-app/README.md` — Modify
- **Dependencies**: Task 4.1
- **Verification**: Read-through only
- **Complexity**: Low

### Phase 5: Full regression

#### Task 5.1: Cross-package regression
- **Description**: `make && ./test_simbox` in
  `libsCpp/asterisk_chan_simbox`; `dart analyze lib test` +
  `flutter test` in `libsFlutter/flutter_gsm`; `dart analyze lib` +
  `flutter test` in `apps/simbox-app`.
- **Files**: None new — verification-only task
- **Dependencies**: Tasks 1.3, 2.2, 3.2, 4.2
- **Verification**: All green / 0 new errors across all three packages
- **Complexity**: Low

#### Task 5.2: Close out flow docs
- **Description**: Update `_status.md`/`04-implementation-log.md` to
  COMPLETE, with the same honest "structurally verified, real-hardware
  verification deferred" framing used throughout this flow chain.
- **Files**:
  - `flows/sdd-simbox-app-real-driver/_status.md` — Modify
  - `flows/sdd-simbox-app-real-driver/04-implementation-log.md` — Modify
- **Dependencies**: Task 5.1
- **Verification**: Read-through only
- **Complexity**: Low

## Dependency Graph

```
1.1 → 1.2 → 1.3 ─────────────────┬──→ 4.1 → 4.2 ─┐
              │                  │                │
              └──→ 2.1 → 2.2 ────┤                ├──→ 5.1 → 5.2
                                 │                │
                       3.1 → 3.2 ─────────────────┘
```

## File Change Summary

| File | Action | Reason |
|------|--------|--------|
| `libsCpp/asterisk_chan_simbox/src/simbox_internal_linux.h` | Modify | Declare `simbox_config_bridge_set_dir()` |
| `libsCpp/asterisk_chan_simbox/adapters/src/shim_config.c` | Modify | Implement the override, honor it in `ast_config_load2()` |
| `libsCpp/asterisk_chan_simbox/src/simbox_api.c` | Modify | `simbox_init()` calls the bridge function |
| `libsCpp/asterisk_chan_simbox/tests/test_simbox.c` | Modify | New override test |
| `libsFlutter/flutter_gsm/lib/src/linux/simbox_modem_repository.dart` | Modify | `configDir`/env var plumbing |
| `libsFlutter/flutter_gsm/test/simbox_modem_repository_test.dart` | Modify | New config-dir test |
| `apps/simbox-app/lib/main.dart` | Modify | DI swap + injection seam |
| `apps/simbox-app/test/widget_test.dart` | Modify | Inject `FakeModemRepository` explicitly |
| `apps/simbox-app/dongle.conf.example` | Create | Validated example config |
| `apps/simbox-app/README.md` | Modify | New setup section (additive) |
| `flows/sdd-simbox-app-real-driver/_status.md`, `04-implementation-log.md` | Modify | Close out |

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| `dongle.conf.example` looks plausible but doesn't actually parse correctly (e.g. a typo'd section header) | Low | Medium — a broken example is worse than none, misleads real setup | Task 4.1 requires an actual parse-validation run, not just visual review |
| `widget_test.dart`'s injection seam changes observable behavior subtly (e.g. `Provider` rebuild timing) | Low | Low — caught immediately by running the existing assertions | Task 3.2's verification is "identical assertions to before," not new ones — any behavior drift shows up as a test failure |
| Real Linux/hardware verification never actually gets exercised (this environment can't do it) | High (certain, given constraints) | Medium — a real config/hardware bug could slip through until first real deployment | Explicitly documented as deferred throughout (matches `sdd-asterisk-chan-simbox`'s Task 5.9 precedent) — not treated as "done," flagged in final status/next-actions for a future real-Linux-host session |

## Rollback Strategy

Every task is additive or a narrowly-scoped modify with no destructive
data/schema changes. If a task needs reverting: `git diff`/`git
checkout --` the specific file(s) listed in that task — no phase
depends on irreversible external state (no migrations, no persisted
data format changes).

## Checkpoints

After each phase, verify:

- [ ] Phase 1: `make && ./test_simbox` clean in `libsCpp/asterisk_chan_simbox`
- [ ] Phase 2: `dart analyze` + `flutter test` clean in `libsFlutter/flutter_gsm`
- [ ] Phase 3: `dart analyze` + `flutter test` clean in `apps/simbox-app`
- [ ] Phase 4: `dongle.conf.example` validated (Task 4.1's parse run), README read-through
- [ ] Phase 5: full three-package regression green

## Open Implementation Questions

- [ ] Task 2.2's exact mechanism for testing the env-var path (vs. the
  constructor param path) depends on whether
  `simbox_modem_repository_test.dart`'s existing helpers support
  setting/restoring `Platform.environment` cleanly in a test — if not,
  the constructor param alone is sufficient coverage (the env var is a
  one-line `Platform.environment[...]` read with no branching logic of
  its own to separately test).

---

## Approval

- [x] Reviewed by: Anton
- [x] Approved on: 2026-08-23
- [x] Notes: Approved as drafted.
