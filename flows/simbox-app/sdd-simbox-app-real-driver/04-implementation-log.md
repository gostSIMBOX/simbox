# Implementation Log: simbox-app-real-driver

> Started: 2026-08-23
> Plan: [03-plan.md](03-plan.md)

## Progress Tracker

| Task | Status | Notes |
|------|--------|-------|
| 1.1 `simbox_config_bridge_set_dir()` | Done | New `simbox_config_bridge.h` (cross-platform, not `__linux__`-gated) |
| 1.2 Wire `simbox_init()` | Done | |
| 1.3 Native test | Done | 7/7 suites pass |
| 2.1 `SimboxModemRepository` config plumbing | Done | |
| 2.2 Config-dir test | Done | |
| 3.1 `SimboxApp` injection seam | Done | |
| 3.2 Update `widget_test.dart` | Done | |
| 4.1 `dongle.conf.example` | Done | Found + fixed a real inline-comment-stripping bug — see log |
| 4.2 README section | Done | |
| 5.1 Cross-package regression | Done | |
| 5.2 Close out flow docs | Done | |

## Session Log

### Session 2026-08-23 - Claude

**Started at**: Phase 1, Task 1.1
**Context**: Plan approved same session; implementation begins immediately.

#### Completed

- **Task 1.1 — `simbox_config_bridge_set_dir()`**:
  - Created `adapters/include/simbox_config_bridge.h` (new file) —
    deliberately **not** wrapped in `#ifdef __linux__` (unlike
    `simbox_internal_linux.h`, which was my first instinct and had to
    be reverted): `shim_config.c` compiles on every platform per the
    root Makefile's unconditional `adapters/src/*.c` wildcard, and
    Task 1.3's test needs to call this function directly on macOS too
    — gating the declaration behind `__linux__` would have made
    `shim_config.c`'s own definition lack a visible prototype on
    non-Linux builds and made the test uncompilable here.
  - `adapters/src/shim_config.c`: added `g_config_dir[512]` static
    buffer + `simbox_config_bridge_set_dir()` (copies immediately, no
    ownership transfer). `ast_config_load2()` now tries
    `<g_config_dir>/<filename>` first (if set) before its existing
    CWD-relative/`/etc/asterisk/<filename>` attempts — purely additive,
    zero behavior change when unset. Added a comment noting
    `#include`/`#exec` aren't handled by this parser (per
    specifications' Edge Cases — flagging, not fixing).
  - Verified: `make` clean (macOS, 28 pre-existing warnings, none new);
    `./test_simbox` — all 6 pre-existing suites still pass.

- **Task 1.2 — Wire `simbox_init()`**:
  - `src/simbox_api.c`: inside the existing `#ifdef __linux__` block,
    calls `simbox_config_bridge_set_dir(config->config_dir)` when
    `config && config->config_dir`, before
    `simbox_populate_from_gpublic(inst)`. Added
    `#include <simbox_config_bridge.h>` alongside the file's other
    Linux-only adapter includes.
  - Verified: `make` clean; `./test_simbox` all 6 suites pass;
    `gcc -fsyntax-only -D__linux__ -DHAVE_CONFIG_H` forced check on
    `simbox_api.c` — clean (this is what actually exercises the new
    line, since it's inside the `__linux__` branch and this dev
    machine is macOS).

- **Task 1.3 — Native test**:
  - `tests/test_simbox.c`: new `test_config_dir_override()` (Test 7).
    Writes a temp `dongle.conf` to a `mkdtemp()`-created temp
    directory, calls `simbox_config_bridge_set_dir(tmpdir)`, confirms
    `ast_config_load2()` finds and correctly parses it (`[general]
    interval=15`, `[dongle0] audio=/dev/ttyUSB1`); then calls with
    `NULL` and confirms the same bare filename now resolves to
    `CONFIG_STATUS_FILEMISSING` (neither this test-run's CWD nor
    `/etc/asterisk/` has a `dongle.conf` of their own) — proving the
    override doesn't leak once cleared, not just that setting it works.
  - Verified: `make && ./test_simbox` — all 7 suites pass (Test 7
    included), no regression in the other 6.

#### Deviations from Plan

- **Task 1.1's header location**: plan said "add the declaration to
  `src/simbox_internal_linux.h`" (per specifications' Interfaces
  section). Actual: new standalone `adapters/include/simbox_config_bridge.h`
  instead. Reason found during implementation, not anticipated at
  planning time: `simbox_internal_linux.h`'s entire body is wrapped in
  `#ifdef __linux__`, but `shim_config.c` (which defines this function)
  and `tests/test_simbox.c` (which calls it directly per Task 1.3) both
  need it visible on **every** platform, not just Linux — only
  `simbox_api.c`'s *call site* is Linux-gated (Task 1.2), not the
  function's existence. Caught before it caused a real build break
  (reverted the first attempt after re-reading the header's own guard),
  not discovered via a failing build.

#### Discoveries

- None beyond what the pre-implementation deep-research pass already
  surfaced during specifications (dsp.conf sharing the loader,
  serials.conf/share.c's hardcoded paths, `#include`/`#exec` gap) —
  implementation matched that research cleanly.

**Ended at**: Phase 1 complete (Tasks 1.1-1.3)

- **Task 2.1 — `SimboxModemRepository` config plumbing**:
  - `libsFlutter/flutter_gsm/lib/src/ffi/simbox_native_library.dart`:
    added `simboxConfigDirEnvVar = 'FLUTTER_GSM_SIMBOX_CONFIG_DIR'`,
    sibling to the existing `simboxLibEnvVar`.
  - `lib/src/linux/simbox_modem_repository.dart`: factory gains
    `String? configDir`, resolved from the param or the new env var.
    When resolved, allocates a `simbox_config_t` via its generated
    `$allocate` factory (only `config_dir` set; `state_dir`/
    `log_level`/`auto_discovery`/`auto_recover_diag` left at
    null/0/false — none of those are in this flow's scope), passes to
    `simbox_init()`, frees both the config struct and the string
    pointer immediately after — safe per specifications, since
    `simbox_config_bridge_set_dir()` (Task 1.1) copies synchronously
    before `simbox_init()` returns.
  - Verified: `dart analyze` clean; full package `flutter test` —
    57/57 passing (no regression) before adding Task 2.2's new test.

- **Task 2.2 — Config-dir test**:
  - `test/simbox_modem_repository_test.dart`: new test constructs
    `SimboxModemRepository(configDir: <temp dir>)` and confirms
    `listModems()` still works identically to the no-config-dir case.
    Resolved the plan's one Open Implementation Question: used the
    constructor-param path only, not a separate env-var-specific test
    — the env var is a one-line `Platform.environment[...]` read with
    no branching logic of its own, so the constructor-param test
    already covers the only code path that matters (the
    `simbox_config_t` construction/passing logic downstream of
    resolution, which doesn't care how `configDir` was resolved).
  - Verified: `dart analyze` clean; full package `flutter test` —
    58/58 passing.

**Ended at**: Phase 2 complete (Tasks 2.1-2.2)

- **Task 3.1 — `SimboxApp` injection seam**:
  - `apps/simbox-app/lib/main.dart`: `SimboxApp({super.key,
    ModemRepository? repository})`. `Provider<ModemRepository>`'s
    `create` uses `_injectedRepository ?? ModemRepositoryImpl()` — the
    DI swap from `FakeModemRepository` to the real repository.
    `dispose` callback narrowed to only call `.dispose()` when the
    resolved repository `is FakeModemRepository` (`ModemRepositoryImpl`
    has none — confirmed by reading it, per specifications).
  - Verified: `dart analyze lib/main.dart` clean; `dart analyze lib`
    (whole package) — same 24 pre-existing info/warning issues as
    before this flow started (all in `theme/`/`imei_validator.dart`/
    `filter_chip_row.dart`, none touched here), zero new.

- **Task 3.2 — Update `widget_test.dart`**:
  - Both `pumpWidget(const SimboxApp())` calls became
    `pumpWidget(SimboxApp(repository: FakeModemRepository()))`,
    decoupling these tests from `FlutterGsmPlatform.instance`
    resolution/`libsimbox` presence during `flutter test` runs — added
    the `fake_modem_repository.dart` import.
  - Verified: `flutter test test/widget_test.dart` — both tests pass,
    identical assertions to before; full package `flutter test` —
    10/10 passing (`widget_test.dart` ×2 + `sims_screen_test.dart` ×3,
    unaffected since it already built its own `Provider` independently
    of `main.dart`).

**Ended at**: Phase 3 complete (Tasks 3.1-3.2)

- **Task 4.1 — `dongle.conf.example`**:
  - `apps/simbox-app/dongle.conf.example` (new): trimmed one-device
    template (`[general]`, `[defaults]`, `[dongle0]`), header comment
    explaining it's a template + the setup steps (copy, edit
    `audio=`/`data=`, set `FLUTTER_GSM_SIMBOX_CONFIG_DIR`).
  - **Real bug found and fixed during Task 4.1's own validation step,
    not review**: a temporary one-off C harness pointed
    `simbox_config_bridge_set_dir()` at the new example and loaded it
    via `ast_config_load2()` — every value came back with its trailing
    `; comment` text still attached (e.g. `audio` parsed as
    `"/dev/ttyUSB1\t\t; tty port for audio"`, not
    `"/dev/ttyUSB1"`). Root cause: `shim_config.c`'s parser only ever
    skipped *whole-line* `;`/`#` comments, never `key=value ; comment`
    trailing ones — a real, pre-existing gap that affects **any** real
    config written in the idiomatic Asterisk style, including this
    SDK's own vendored reference sample
    (`asterisk_chan_svistok/chan_svistok/etc/dongle.conf`), which uses
    that style throughout. Fixed in `adapters/src/shim_config.c`: new
    `strip_inline_comment()` helper (truncates at the first `;`/`#`,
    re-trims), applied to both category names and variable values.
    Added `tests/test_simbox.c`'s Test 8
    (`test_inline_comment_stripping`) as permanent regression coverage
    — a config with tab-and-`;`-style and space-and-`#`-style trailing
    comments on different lines, confirming both get stripped
    correctly. Re-ran the one-off validation harness after the fix —
    the example now parses cleanly (all 5 expected values match
    exactly), then deleted the harness (not committed, matching this
    session's established "temporary one-off validation tool, deleted
    after use" pattern from earlier flows).
  - Verified: `make && ./test_simbox` — all 8 suites pass (7
    pre-existing/Phase-1 + new Test 8); `dongle.conf.example` parse-
    validated for real, not just visually reviewed.

- **Task 4.2 — README section**:
  - `apps/simbox-app/README.md`: appended (not rewrote — the file's
    pre-existing mismatch with a totally different example app is
    flagged inline in the new section itself, not silently ignored) a
    "🔌 Real Hardware Setup (Linux)" section: build `libsimbox`, copy
    `dongle.conf.example`, set `FLUTTER_GSM_SIMBOX_CONFIG_DIR`, attach
    hardware, `flutter run -d linux`. Notes the existing
    "driver unavailable" fallback explicitly so it's clear that's
    already-tested behavior, not something new here.
  - Verified: read-through (per plan's stated verification for this task).

**Ended at**: Phase 4 complete (Tasks 4.1-4.2)

- **Task 5.1 — Cross-package regression**:
  - `libsCpp/asterisk_chan_simbox`: `make clean && make` clean (same
    28 pre-existing vendored-tree warnings, none new); `./test_simbox`
    — all 8 suites pass.
  - `libsFlutter/flutter_gsm`: `dart analyze lib test` — 0 errors, same
    2 pre-existing infos as before this flow; `flutter test` — 58/58
    passing.
  - `apps/simbox-app`: `dart analyze lib` — 0 errors, same 24
    pre-existing infos/warnings as before this flow (all in
    `theme/`/`imei_validator.dart`/`filter_chip_row.dart`, none touched
    by this flow); `dart analyze test` — clean; `flutter test` — 10/10
    passing.
  - No regressions anywhere; every pre-existing issue count matches
    what it was before this flow started.

- **Task 5.2 — Close out flow docs**: this entry + `_status.md` (see
  next edit) mark the flow COMPLETE.

#### Deviations from Plan

| Planned | Actual | Reason |
|---------|--------|--------|
| Task 1.1: declare `simbox_config_bridge_set_dir()` in `src/simbox_internal_linux.h` | Declared in a new standalone `adapters/include/simbox_config_bridge.h` instead | `simbox_internal_linux.h`'s entire body is `#ifdef __linux__`-gated; `shim_config.c` (defines the function) and `tests/test_simbox.c` (calls it directly, Task 1.3) both need it visible on every platform — only `simbox_api.c`'s call site (Task 1.2) is actually Linux-only. Caught before it caused a build break, not via a failing build. |
| Task 4.1: ship a validated example config | Also fixed a real bug in `shim_config.c`'s comment handling (trailing `;`/`#` comments weren't stripped from values) + added Test 8 as permanent regression coverage | Found *while* validating the example per Task 4.1's own stated requirement ("actually parses cleanly," not just visual review) — every real config in the idiomatic Asterisk style (including this SDK's own vendored reference sample) would have silently corrupted values without this fix. Small, adapter-layer-only, directly motivated by verification work already in scope — not speculative scope creep. |

#### Learnings

- **"Validate it actually parses" (Task 4.1) is not a formality** — it
  found a real bug (`shim_config.c` not stripping trailing inline
  comments) that a visual review of the example config would very
  plausibly have missed, since the file *looked* correct and only
  failed when actually run through the real parser.
- **Header-gating discipline matters for cross-platform adapter code**:
  a function meant to be callable/definable on every platform must not
  be declared inside a header whose whole body is `#ifdef __linux__` —
  even if its only *caller* in `simbox_api.c` is itself Linux-gated.
  The gate belongs at the call site, not necessarily the declaration.

## Completion Checklist

- [x] All tasks completed or explicitly deferred (real-hardware/Linux-
      host verification explicitly deferred throughout, per
      specifications' Constraints — not an oversight)
- [x] Tests passing (8/8 native, 58/58 `flutter_gsm`, 10/10 `simbox-app`)
- [x] No regressions (every pre-existing warning/info count unchanged)
- [x] Documentation updated (`apps/simbox-app/README.md` + new
      `dongle.conf.example`)
- [x] Status updated to COMPLETE
