# Specifications: simbox-app-real-driver

> Version: 1.1 (added deep chan_svistok config-loading research)
> Status: APPROVED
> Last Updated: 2026-08-23
> Requirements: [01-requirements.md](01-requirements.md)

## Overview

Two independent pieces of work, both required for AC #1-#5:

1. **DI swap**: `apps/simbox-app/lib/main.dart` provides a real
   `ModemRepositoryImpl` instead of `FakeModemRepository`. `SimboxApp`
   gains a test-only injection seam (mirroring `LinuxFlutterGsm`'s own
   `{SimboxModemRepository? repository}` pattern from
   `sdd-flutter_gsm-ffi`) so `test/widget_test.dart` keeps injecting
   `FakeModemRepository` explicitly instead of depending on native
   library presence.
2. **Config-path plumbing**: `simbox_config_t.config_dir` (dead code
   today — `simbox_init()` copies it into the instance struct and never
   reads it again) becomes real. A new adapter-layer function lets
   `simbox_api.c` tell `shim_config.c`'s `ast_config_load2()` to check
   `<config_dir>/dongle.conf` before falling back to its existing
   CWD-relative/`/etc/asterisk/dongle.conf` resolution. `flutter_gsm`
   exposes this as a new `FLUTTER_GSM_SIMBOX_CONFIG_DIR` env var,
   mirroring the existing `FLUTTER_GSM_SIMBOX_LIB` pattern exactly —
   resolves requirements' AC #5 as **option (a)** (wire it through),
   not (b) (document-only), because a predictable absolute path is a
   real correctness win for a packaged desktop app whose working
   directory at launch isn't guaranteed, and the adapter-layer-only
   change stays inside the already-established "adapters/ and src/ are
   fair game, vendored trees are read-only" rule.

**Deep-dive research into chan_svistok** (full findings in
`04-implementation-log.md`'s Discoveries once implementation starts;
summarized here since they validate rather than change the design
above) confirmed: `dongle.conf` is the only config file `chan_dongle.c`
itself loads via `ast_config_load`; a static, set-once-before-first-load
global in `shim_config.c` is provably sufficient because every reload
trigger (CLI `dongle reload`, AMI, Asterisk's own `reload_module()` hook
— all three converge on the same `reload_config()`/`ast_config_load()`
call site) reloads the *same* file from the *same* directory, never a
different one; and the `config_dir` name should be kept as-is (already
public API, already used by `tests/test_simbox.c`, loosely mirrors real
Asterisk's own `astetcdir`/`AST_CONFIG_DIR` naming lineage even though
no in-repo precedent exists for it). See Edge Cases for the two real
limitations this research surfaced that this flow does **not** attempt
to fix (`serials.conf`/`share.c`'s hardcoded `/var/svistok/` paths, and
the adapter's minimal parser not supporting `#include`/`#exec`).

## Affected Systems

| System | Impact | Notes |
|--------|--------|-------|
| `apps/simbox-app/lib/main.dart` | Modify | DI swap: `FakeModemRepository` → `ModemRepositoryImpl`, `SimboxApp` gains injection seam |
| `apps/simbox-app/test/widget_test.dart` | Modify | Inject `FakeModemRepository` explicitly via the new seam |
| `apps/simbox-app/dongle.conf.example` | Create | Validated example config (none currently exists anywhere in this monorepo tree, per requirements' research) |
| `apps/simbox-app/README.md` | Modify | Append a new "Real Hardware Setup (Linux)" section — see Edge Cases for why this is additive-only, not a rewrite |
| `libsCpp/asterisk_chan_simbox/src/simbox_internal_linux.h` | Modify | Declare `simbox_config_bridge_set_dir()` |
| `libsCpp/asterisk_chan_simbox/adapters/src/shim_config.c` | Modify | Implement the override + honor it in `ast_config_load2()` |
| `libsCpp/asterisk_chan_simbox/src/simbox_api.c` | Modify | `simbox_init()` calls the new bridge function when `config->config_dir` is set |
| `libsCpp/asterisk_chan_simbox/tests/test_simbox.c` | Modify | New test for the config-dir override (see Testing Strategy) |
| `libsFlutter/flutter_gsm/lib/src/linux/simbox_modem_repository.dart` | Modify | Factory reads `FLUTTER_GSM_SIMBOX_CONFIG_DIR`, builds/passes a `simbox_config_t` |
| `libsFlutter/flutter_gsm/test/simbox_modem_repository_test.dart` | Modify | New test for the config-dir env var being threaded through without crashing |

## Architecture

### Component Diagram

```
apps/simbox-app/lib/main.dart
    Provider<ModemRepository>(create: (_) => ModemRepositoryImpl())
        |
        v
flutter_gsm: FlutterGsmPlatform.instance  (LinuxFlutterGsm, auto-
        |                                  registered via dartPluginClass)
        v
LinuxFlutterGsm -> SimboxModemRepository (lazy factory)
        |
        | reads FLUTTER_GSM_SIMBOX_CONFIG_DIR env var (new)
        | builds simbox_config_t{config_dir: <path>} if set
        v
libsimbox: simbox_init(config)
        |
        | (Linux only) config->config_dir != NULL?
        |   -> simbox_config_bridge_set_dir(dir)   [new]
        v
        simbox_populate_from_gpublic() -> simbox_module_bridge_load()
        -> chan_dongle.c's real load_module()/reload_config()
        -> ast_config_load("dongle.conf")            [read-only, unchanged]
        v
adapters/src/shim_config.c: ast_config_load2()
        1. if config_dir override set: try "<config_dir>/dongle.conf" [new]
        2. try "./dongle.conf" (CWD-relative)          [existing]
        3. try "/etc/asterisk/dongle.conf"              [existing]
```

### Data Flow

The override is a one-shot, process-global value: `simbox_init()` sets
it (if provided) before triggering config-driven device population,
and it stays set for the process's lifetime (matches
`g_active_linux_instance`'s existing "only one real Linux instance"
assumption already documented in `simbox_api.c`) — not per-call, not
reset by `simbox_shutdown()`. No new Dart-visible event or state; this
is purely a native-side path-resolution detail.

## Interfaces

### New Interfaces

`libsCpp/asterisk_chan_simbox/src/simbox_internal_linux.h` (new
declaration, alongside the file's existing Linux-only adapter-bridge
functions):

```c
/* Tells shim_config.c's ast_config_load2() to check
 * "<dir>/<filename>" before its existing CWD-relative/
 * "/etc/asterisk/<filename>" resolution (see adapters/src/
 * shim_config.c). Copies `dir` into an internal static buffer
 * immediately - safe to free/reuse the caller's string right after
 * this call returns (no ownership transfer, unlike simbox_event_cb).
 * Pass NULL to clear the override and restore the original two-path
 * resolution. Called from simbox_init() when config->config_dir is
 * set - not part of simbox_api.h's public surface, since it's an
 * adapter-internal wiring detail, not a modem-facing concept. */
void simbox_config_bridge_set_dir(const char *dir);
```

No changes to `simbox_api.h`'s public surface — `simbox_config_t`
already has `config_dir`; this just makes the existing field do
something. **No `ffigen` regeneration needed** in `flutter_gsm`
(confirmed: the field, and the struct's `$allocate` factory, already
exist in the generated `simbox_bindings.dart`).

### Modified Interfaces

`SimboxModemRepository`'s factory
(`lib/src/linux/simbox_modem_repository.dart`):

```dart
factory SimboxModemRepository({
  SimboxBindings? bindings,
  String? libraryPath,
  String? configDir, // new — defaults to FLUTTER_GSM_SIMBOX_CONFIG_DIR
}) {
  ...
  final resolvedConfigDir =
      configDir ?? Platform.environment[simboxConfigDirEnvVar];
  Pointer<simbox_config_t> configPtr = nullptr;
  Pointer<Char> configDirPtr = nullptr;
  if (resolvedConfigDir != null) {
    configDirPtr = resolvedConfigDir.toNativeUtf8().cast<Char>();
    configPtr = simbox_config_t.$allocate(
      calloc,
      config_dir: configDirPtr,
      state_dir: nullptr,
      log_level: 0,
      auto_discovery: false,
      auto_recover_diag: false,
    );
  }
  final handle = resolvedBindings.simbox_init(configPtr);
  if (configPtr != nullptr) {
    calloc.free(configDirPtr);
    calloc.free(configPtr);
  }
  ...
}
```

Freeing immediately after `simbox_init()` returns is safe (not a
use-after-free like Task 4.1's `Isolate.run` bugs) because
`simbox_config_bridge_set_dir()` makes its own copy synchronously,
before `simbox_init()` returns — no async handoff, unlike the event
callback path.

`apps/simbox-app/lib/main.dart`'s `SimboxApp`:

```dart
class SimboxApp extends StatelessWidget {
  const SimboxApp({super.key, ModemRepository? repository})
      : _injectedRepository = repository;

  final ModemRepository? _injectedRepository;

  @override
  Widget build(BuildContext context) {
    return Provider<ModemRepository>(
      create: (_) => _injectedRepository ?? ModemRepositoryImpl(),
      dispose: (_, repo) {
        if (repo is FakeModemRepository) repo.dispose();
        // ModemRepositoryImpl has no dispose() (it's a thin FlutterGsmPlatform
        // wrapper — see Edge Cases for why that's fine here).
      },
      child: MaterialApp(/* unchanged */),
    );
  }
}
```

`test/widget_test.dart` changes every `pumpWidget(const SimboxApp())`
to `pumpWidget(SimboxApp(repository: FakeModemRepository()))`.

## Data Models

No new persistent data types. `dongle.conf.example`'s format is
entirely defined by chan_dongle's existing (read-only, vendored)
config parser — this flow only ships a validated example, not a new
schema.

## Behavior Specifications

### Happy Path

1. Developer builds `libsimbox` (per `flutter_gsm`'s README), places a
   real `dongle.conf` (adapted from the new
   `apps/simbox-app/dongle.conf.example`) in a directory of their
   choosing, and sets `FLUTTER_GSM_SIMBOX_CONFIG_DIR` to that
   directory (and `FLUTTER_GSM_SIMBOX_LIB` if `libsimbox` isn't in one
   of the default candidate locations).
2. `flutter run` on Linux with a real modem attached at the
   `audio=`/`data=` paths named in `dongle.conf`.
3. `simbox-app` starts, `main.dart` provides a real
   `ModemRepositoryImpl`, `simbox_init()` picks up the config override,
   chan_dongle's real init/discovery threads open the device, and the
   Симки/Модемы screens show it via the existing (already-built)
   real-event-driven `ModemLineListController`.

### Edge Cases

| Case | Trigger | Expected Behavior |
|------|---------|--------------------|
| `FLUTTER_GSM_SIMBOX_CONFIG_DIR` unset | Default — most dev machines, all of this session's own testing | Behavior is byte-for-byte unchanged from today: `simbox_init(nullptr)`-equivalent path, `ast_config_load2()` falls straight to its existing CWD/`/etc/asterisk/` resolution. This is why the override is additive (checked *first*, not exclusive) rather than replacing the old paths. |
| `libsimbox` not built/discoverable | Dev machine without native lib built | Unchanged — `ModemDriverNotAvailableException` at first use, already handled by existing UI (`modem_line_list_controller.dart` etc., per requirements AC #2). |
| `dongle.conf` missing even at the overridden path | Typo'd path, file not copied yet | Falls through to the existing CWD/`/etc/asterisk/` attempts, then `is_bad_config()` (existing, from `sdd-asterisk-chan-simbox`'s Phase 5.2 fix) — no crash, `gpublic->devices` simply stays empty, UI shows zero devices (not "driver unavailable" — the driver *is* available, there's just nothing configured yet; these are different states and must not be conflated). |
| Non-Linux platform (macOS dev machine, this session's own environment) | Every test run in this development environment | `config->config_dir` is read but `simbox_config_bridge_set_dir()`/config-driven population is entirely inside `#ifdef __linux__` in `simbox_init()` — the Dart-side env var plumbing is exercised (doesn't crash, doesn't error), but has zero observable effect, same as every other Linux-only code path in this flow chain. |
| `apps/simbox-app/README.md` currently describes an unrelated app | Pre-existing defect discovered during this flow's research (the file is a stale copy from `flutter_gsmsip/example`, titled "flutter_gsmsip Example") | **Out of scope to fix wholesale** — this flow only appends a new, clearly-scoped "Real Hardware Setup (Linux)" section. Flagging the mismatch here so it isn't silently perpetuated as if unnoticed, without taking on an unrelated doc-rewrite task. |
| `ModemRepositoryImpl` has no `dispose()` | `SimboxApp`'s `Provider.dispose` callback | Confirmed by reading `modem_repository_impl.dart` directly — it's a stateless wrapper around `FlutterGsmPlatform.instance` (itself a long-lived singleton). Nothing to dispose; the `dispose` callback only does real work for `FakeModemRepository` (test/dev double holding its own `StreamController`). |
| `dsp.conf` also resolves through the same adapter config loader | Deep research found `dsp.c:1800` calls `ast_config_load2("dsp.conf", "dsp", ...)` through the identical `shim_config.c` code path `dongle.conf` uses | Inherits the `config_dir` override automatically — no separate handling needed. Currently dormant (`ast_dsp_init()`/`ast_dsp_reload()`, the only callers, are never invoked anywhere in chan_svistok or the adapters), so this has zero observable effect today, but is worth knowing before anyone later wires DSP tuning up. |
| `/var/svistok/serials.conf` and `share.c`'s ~12 hardcoded `/var/svistok/*` persistence paths (device/stats/list files) | Deep research: these bypass `ast_config_load`/`shim_config.c` entirely via raw `fopen("/var/svistok/...", ...)` calls baked directly into read-only vendored `dserial.c`/`share.c` | **Explicitly out of scope for this flow.** `config_dir` only affects files loaded through `ast_config_load2()`; it has and can have zero effect on these. This is the same class of problem as `config_dir` was before this flow (a dead `simbox_config_t` field — here, `state_dir` — paired with hardcoded paths in read-only code), but fixing it would need a different mechanism (the vendored code can't be redirected the same way, since it never calls through the adapter's config-loading seam at all) and touches an unrelated file set. Flagging as a discovered-but-deliberately-deferred limitation, not silently ignoring it. |
| A real `dongle.conf` uses `#include otherfile.conf` (a real-Asterisk config feature, copied from an online tutorial by an unsuspecting user) | Deep research: the adapter's minimal parser (`shim_config.c`) treats any `#`-prefixed line as a plain comment, identical to `;` — there's no special-casing | Silently ignored (no error, no crash) — a pre-existing gap in the adapter's parser, not something this flow introduces or is scoped to fix (the shipped example config doesn't use it, and neither does the real vendored sample). Worth a one-line comment in `shim_config.c` when this flow touches it, so the next person who *does* need `#include` isn't surprised. |

### Error Handling

| Error | Cause | Response |
|-------|-------|----------|
| `simbox_init()` called twice with different `config_dir` values (e.g. hot-restart during development) | Re-running `flutter run` without a full process restart isn't really possible for a native global like this, but worth stating | "Last `simbox_init()` wins," matching the existing documented behavior for `g_active_linux_instance` in `simbox_api.c`'s own header comment — not a new risk this flow introduces. |

## Dependencies

### Requires

- `sdd-flutter_gsm-ffi` (complete) — `LinuxFlutterGsm`/`SimboxModemRepository` must exist and work.
- `sdd-asterisk-chan-simbox` (complete apart from its own real-Linux-host follow-ups) — `libsimbox` itself, and the established adapters/vs-vendored-tree rule this flow's native change follows.

### Blocks

- Nothing currently depends on this flow.

## Integration Points

### External Systems

None — no new external service/API integration.

### Internal Systems

- `apps/simbox-app`'s existing screens/controllers
  (`modem_line_list_controller.dart`, `modems_screen.dart`,
  `sims_screen.dart`) — consumed as-is, no changes needed (confirmed
  their `ModemDriverNotAvailableException` handling already matches
  what a real repository will actually throw).
- `flutter_gsm`'s native library loader
  (`simbox_native_library.dart`) — the new `FLUTTER_GSM_SIMBOX_CONFIG_DIR`
  env var is a sibling to its existing `FLUTTER_GSM_SIMBOX_LIB`, read
  independently (config dir has nothing to do with which `.so`/`.dylib`
  gets loaded).

## Testing Strategy

### Unit Tests

- [ ] `libsCpp/asterisk_chan_simbox/tests/test_simbox.c`: new test
  exercising `simbox_config_bridge_set_dir()` + `ast_config_load2()`
  directly — write a temp `dongle.conf` to a temp directory, set the
  override, confirm `ast_config_load()` finds it; confirm passing NULL
  restores the old CWD/`/etc/asterisk/` behavior (verifiable on macOS —
  this tests the shim function directly, not real chan_dongle device
  population, so it doesn't need `#ifdef __linux__` or real hardware).
- [ ] `libsFlutter/flutter_gsm/test/simbox_modem_repository_test.dart`:
  new test constructing `SimboxModemRepository(configDir: '/some/tmp/dir')`
  (or via the env var) and confirming it doesn't crash and behaves
  identically to the no-config-dir case on this (non-Linux/simulated)
  dev machine — honestly scoped as "doesn't break anything," not "proves
  real discovery," since real discovery is Linux-only and needs
  hardware this environment doesn't have.
- [ ] `apps/simbox-app/test/widget_test.dart`: update both existing
  `pumpWidget(const SimboxApp())` calls to
  `pumpWidget(SimboxApp(repository: FakeModemRepository()))` — same
  assertions, now decoupled from native library presence.

### Integration Tests

- [ ] None new — `sims_screen_test.dart`/`settings_form_controller_test.dart`
  already construct `FakeModemRepository` independently of `main.dart`
  and are unaffected by this flow.

### Manual Verification

- [ ] On a real Linux host with a modem attached: build `libsimbox`,
  create a real `dongle.conf` from the shipped example, set both env
  vars, `flutter run`, confirm the device appears in Симки/Модемы.
  **Cannot be performed in this development environment** (no Linux
  host, no hardware) — explicitly deferred, matching this flow's
  Constraints.
- [ ] `dart analyze`/`flutter test` clean across `flutter_gsm` and
  `apps/simbox-app` after all changes (achievable and required in this
  environment).
- [ ] `make && ./test_simbox` clean in `libsCpp/asterisk_chan_simbox`
  after the native change (achievable in this environment).

## Migration / Rollout

No data migration. Purely additive: existing behavior is unchanged
when the new env var isn't set, which is every environment except a
real Linux deployment that opts in.

## Open Design Questions

All three of requirements' Open Questions are resolved here:

- [x] AC #5 config-path design: **wire `config_dir` through** (option
  a) — see Overview.
- [x] Example config/README location: **`apps/simbox-app/`** — it's
  the concrete consumer; `dongle.conf.example` at the package root
  (sibling to `pubspec.yaml`), README section appended (not a rewrite).
- [x] `linux/CMakeLists.txt`: **no changes this iteration** — matches
  `flutter_gsm`'s own documented dev-mode-only loading stance; a real
  build-and-bundle step stays a flagged follow-up for both packages,
  not duplicated here.

---

## Approval

- [x] Reviewed by: Anton
- [x] Approved on: 2026-08-23
- [x] Notes: Approved as drafted (v1.1, including the deep chan_svistok
      config-loading research and the two deliberately-out-of-scope
      limitations it surfaced — `serials.conf`/`share.c`'s hardcoded
      `/var/svistok/*` paths, and `#include`/`#exec` not being
      supported by the adapter's minimal parser).
