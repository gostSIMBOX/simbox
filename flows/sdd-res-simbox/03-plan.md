# Implementation Plan: res-simbox (module split)

> Version: 1.2
> Status: DRAFT
> Last Updated: 2026-08-26
> Specifications: [02-specifications.md](02-specifications.md)

## Summary

Populate five empty module directories
(`libsCpp/asterisk-res-simbox-{core,discovery,programmator,reader,hub}/`)
from the already-classified legacy code, per `02-specifications.md`'s
"Planned Module Layout." Every task here is a **copy-then-trim or
copy-as-is** operation on already-identified legacy files — no new
business logic is authored anywhere in this plan (per the flow's Hard
Constraint). Phase 0 resolves the outstanding open design questions with
explicit recommendations, since several downstream tasks depend on which
way those go; everything after Phase 0 assumes those recommendations
unless the user corrects them at plan-approval time.

No compatible Linux/Asterisk build environment is available in this
development environment (consistent with every prior flow in this
family), so verification throughout is structural: byte-level diffs
against legacy, symbol/reference checks, and manual compile-sanity
review — not an actual `chan_dongle.so`-style link/load test.

The original v1.0 tasks below are retained as implementation history.
Their output already exists. The v1.2 amendment supersedes Tasks 0.3,
0.4, 4.2, 4.4, 5.1, and 5.2 wherever they describe reader as module-only
or hub as binary-only. No v1.2 implementation starts until this amended
plan is approved.

## Version 1.2 Amendment

### Phase 7: Freeze the Legacy Oracle and Add Tests First

#### Task 7.1: Record immutable provenance baselines
- **Description**: Add automated checks that hash and structurally map the
  relevant read-only legacy reader files and vendored `hub-ctrl.c`. Record
  the current copied-source counterparts separately. Tests fail if the
  legacy oracle is ever written or if an extracted operation loses its
  traceable source body.
- **Files**: New tests/fixtures only; no writes under `legacy/`.
- **Dependencies**: None.
- **Verification**: Run the provenance test against the untouched tree;
  record hashes and source-to-target mapping in the implementation log.
- **Complexity**: Low.

#### Task 7.2: Characterize reader behavior before extraction
- **Description**: Build a test harness around the legacy adapter and
  emulator entry points, renaming `main` only in the harness and replacing
  TTY/time boundaries with fakes. Capture device defaults, APDU ordering,
  read/write/close behavior, return paths, and the emulator's existing
  immediate-return/unreachable-close behavior without correcting it.
- **Files**: Reader tests and fake TTY boundary.
- **Dependencies**: Task 7.1.
- **Verification**: Tests pass against the legacy source before they are
  pointed at the extracted shared functions.
- **Complexity**: Medium.

#### Task 7.3: Characterize hub behavior before refactoring
- **Description**: Compile/invoke the vendored program through a harness
  with fake libusb and contained process-exit handling. Cover list,
  power-on/off, LED, hub-vs-bus/device selection, invalid arguments,
  device-not-found, USB-control failure, and success result codes.
- **Files**: Hub tests, fake `usb.h`, and fake USB implementation.
- **Dependencies**: Task 7.1.
- **Verification**: Golden call/result traces pass against the current
  vendored source before `main()`/`exit()` are separated.
- **Complexity**: Medium.

#### Task 7.4: Baseline current module adapters
- **Description**: Add structural tests for current reader CLI commands,
  current `AST_MODULE_INFO`, hub's lack of a module, and current Makefile
  outputs. These tests document precisely what v1.2 intentionally changes.
- **Files**: Structural tests only.
- **Dependencies**: Task 7.1.
- **Verification**: Baseline passes before source changes; expected
  assertions are revised one-by-one with later tasks.
- **Complexity**: Low.

### Phase 8: Create One Shared Implementation per Component

#### Task 8.1: Extract reader callable operations
- **Description**: Copy/move the exact legacy `adapter.c:main()` and
  `emulator.c:main()` bodies into `reader_adapter.c` and
  `reader_emulator.c`, changing only signatures, device-argument
  plumbing, result propagation, and injected boundaries required by the
  tests. Declare them in Asterisk-free `reader_service.h`. Remove the
  duplicated operation bodies from `reader_cli.c`; never retype them.
- **Files**: `reader_adapter.c`, `reader_emulator.c`, `reader_service.h`,
  current `adapter.c`, `emulator.c`, `reader_cli.c`.
- **Dependencies**: Tasks 7.2 and 7.4.
- **Verification**: Characterization tests pass against the shared
  operations; source audit finds one definition of each sequence.
- **Complexity**: High.

#### Task 8.2: Add the reader standalone adapter
- **Description**: Add `reader_main.c` producing `res-simbox-reader`.
  Parse `adapter` or `emulator`, accept an optional device path, preserve
  `/dev/ttyUSB24` and `/dev/ttyUSB25` as defaults, and call only the
  shared operations from Task 8.1.
- **Files**: `reader_main.c` and reader standalone tests.
- **Dependencies**: Task 8.1.
- **Verification**: Parser/result tests pass; dependency audit finds no
  Asterisk headers or symbols in the standalone target.
- **Complexity**: Medium.

#### Task 8.3: Make hub operational code callable
- **Description**: Starting from the copied vendor file, separate its
  operational `main()` body into a callable service returning status.
  Replace host-process `exit()` paths with returned errors while keeping
  vendor behavior and attribution. Declare the Asterisk-free API in
  `hub_service.h`; do not copy the operational body elsewhere.
- **Files**: `hub-ctrl.c`, `hub_service.h`.
- **Dependencies**: Tasks 7.3 and 7.4.
- **Verification**: Pre-refactor golden USB/result traces pass against
  the callable implementation; no `exit()` remains reachable from it.
- **Complexity**: High.

#### Task 8.4: Add the hub standalone adapter
- **Description**: Add `hub_main.c` producing `res-simbox-hub`; retain
  `hub-ctrl` as a compatibility build/install alias to the same artifact.
  The adapter only forwards arguments and converts returned status.
- **Files**: `hub_main.c` and hub standalone tests.
- **Dependencies**: Task 8.3.
- **Verification**: Legacy command-line characterization passes through
  both accepted executable names.
- **Complexity**: Low.

#### Task 8.5: Add shared per-device ownership locking
- **Description**: Introduce a small Asterisk-free lock helper used by
  both standalone and module adapters before hardware open. Derive stable
  lock identities from reader device path and hub bus/device identity;
  return busy on collision and release on all error/success paths.
- **Files**: Shared lock helper/header in each component or one neutral
  shared location chosen during implementation; lock tests.
- **Dependencies**: Tasks 8.1 and 8.3.
- **Verification**: Same-device contention fails deterministically;
  different devices proceed; failure paths leave no held lock.
- **Complexity**: Medium.

### Phase 9: Core Component Registry

#### Task 9.1: Define the versioned public contract
- **Description**: Add `include/res_simbox_component.h` containing ABI
  version, reader/hub kind, owner module, status and typed operations,
  and optional attach/detach/quiesce/reload hooks. Declare registration
  APIs with Asterisk 11 `AST_OPTIONAL_API` stubs.
- **Files**: Core public header plus compile-contract tests.
- **Dependencies**: Approved Specifications v1.2.
- **Verification**: Header compiles for core and both child consumers;
  unavailable stubs leave child modules loadable without core.
- **Complexity**: Medium.

#### Task 9.2: Implement the core registry
- **Description**: Add a locked registry accepting one reader and one hub
  provider, validating ABI/kind/name, taking module references during
  dispatch, and rejecting duplicates. It must contain no Asterisk module
  load/unload and no process supervision calls.
- **Files**: `core/src/component_registry.c/.h`, core Makefile, unit tests.
- **Dependencies**: Task 9.1.
- **Verification**: Tests cover register/unregister, duplicate, ABI
  mismatch, missing provider, dispatch, and callback/unregister race.
- **Complexity**: High.

#### Task 9.3: Integrate registry with core lifecycle
- **Description**: Initialize registry during core load; discover/attach
  already-loaded child providers; on core unload call child detach hooks,
  wait for active dispatch, and destroy the registry without unloading
  children. Mark the provider module with
  `AST_MODFLAG_GLOBAL_SYMBOLS` as required by Asterisk optional APIs.
- **Files**: Core module lifecycle file and registry tests.
- **Dependencies**: Task 9.2.
- **Verification**: Core-first, core-last, core reload, and both-children-
  absent cases pass without `ast_load_resource`, `ast_unload_resource`,
  `fork`, or `exec` references.
- **Complexity**: High.

### Phase 10: Asterisk Adapters and Managed Mode

#### Task 10.1: Rebuild the reader module as a thin adapter
- **Description**: Replace `reader_cli.c` with `reader_module.c`. Keep both
  on-demand reader CLI operations, call Task 8.1 shared functions, expose
  the reader component descriptor, and implement optional attach/detach.
  Use `AST_MODFLAG_GLOBAL_SYMBOLS`; module load succeeds if core is absent.
- **Files**: Reader module adapter, descriptor tests, Makefile inputs.
- **Dependencies**: Tasks 8.1, 8.5, and 9.1.
- **Verification**: No operation-body duplication; independent CLI works;
  both core/child load orders and either unload order pass registry tests.
- **Complexity**: High.

#### Task 10.2: Add the hub Asterisk module adapter
- **Description**: Add `hub_module.c` with CLI wrappers for legacy list,
  power, and LED operations, its own `AST_MODULE_INFO`, hub descriptor,
  and optional attach/detach. It calls only Task 8.3 shared operations and
  loads successfully without core. Use `AST_MODFLAG_GLOBAL_SYMBOLS`.
- **Files**: Hub module adapter, tests, Makefile inputs.
- **Dependencies**: Tasks 8.3, 8.5, and 9.1.
- **Verification**: Independent CLI behavior matches hub characterization;
  managed registration/load-order tests pass; unload releases resources.
- **Complexity**: High.

#### Task 10.3: Prove core-managed dispatch
- **Description**: Exercise reader adapter/emulator and hub list/power/LED
  through registered descriptors owned by core, while retaining direct
  child CLI operation. Confirm registration does not acquire hardware and
  absent/failed children do not affect core startup.
- **Files**: Integration tests and implementation log.
- **Dependencies**: Tasks 9.3, 10.1, and 10.2.
- **Verification**: Full mocked matrix passes for independent and managed
  modes, including detach back to independent mode.
- **Complexity**: Medium.

### Phase 11: Build, Deployment, and Final Audit

#### Task 11.1: Build both reader artifacts
- **Description**: Update reader Makefile so common objects feed both
  `res-simbox-reader` and `res_simbox_reader.so`; only main/module objects
  differ. Standalone target has no Asterisk linkage.
- **Files**: Reader Makefile.
- **Dependencies**: Tasks 8.2 and 10.1.
- **Verification**: Make dry-run/object graph and, where host-compatible,
  build/symbol/dependency checks.
- **Complexity**: Medium.

#### Task 11.2: Build both hub artifacts
- **Description**: Update hub Makefile so common objects feed both
  `res-simbox-hub` and `res_simbox_hub.so`; retain `hub-ctrl` compatibility
  alias. Only the module target uses Asterisk headers/linkage.
- **Files**: Hub Makefile.
- **Dependencies**: Tasks 8.4 and 10.2.
- **Verification**: Make dry-run/object graph and, where host-compatible,
  build/symbol/dependency checks.
- **Complexity**: Medium.

#### Task 11.3: Update deployment without starting binaries
- **Description**: Update project deployment scripts to build/install the
  two new binaries for end users and both `.so` modules for Asterisk.
  Preserve `hub-ctrl` compatibility. Never add service units, autostart,
  process supervision, or core-triggered binary execution.
- **Files**: Existing deploy scripts only.
- **Dependencies**: Tasks 11.1 and 11.2.
- **Verification**: Script audit confirms all four artifacts are handled
  and no binary-launch path was introduced.
- **Complexity**: Medium.

#### Task 11.4: Complete structural and provenance audit
- **Description**: Run all baseline, characterization, registry, lock,
  source-mapping, duplicate-symbol, and dependency tests. Diff every
  moved legacy operation against its oracle and document each intentional
  adapter-only edit. Confirm `legacy/` remains unchanged.
- **Files**: Tests and `04-implementation-log.md` only.
- **Dependencies**: Tasks 11.1-11.3.
- **Verification**: All available tests pass; `git diff --check` clean;
  real Linux/Asterisk/hardware verification remains explicitly listed.
- **Complexity**: High.

### v1.2 Execution Order

```text
7.1 -> {7.2, 7.3, 7.4}
7.2 -> 8.1 -> 8.2
7.3 -> 8.3 -> 8.4
{8.1, 8.3} -> 8.5
9.1 -> 9.2 -> 9.3
{8.1, 8.5, 9.1} -> 10.1
{8.3, 8.5, 9.1} -> 10.2
{9.3, 10.1, 10.2} -> 10.3
{8.2, 10.1} -> 11.1
{8.4, 10.2} -> 11.2
{11.1, 11.2} -> 11.3 -> 11.4
```

### v1.2 Completion Gate

- Characterization tests run against the legacy oracle before extraction.
- Both standalone binaries work without Asterisk libraries.
- Both `.so` adapters work with core absent.
- Both `.so` adapters register with core in either load order.
- Core stays operational with either/both children absent or detached.
- Core contains no child module loading and no binary supervision.
- One shared operation implementation feeds both delivery forms.
- Same-device concurrent ownership is rejected and cleanup is proven.
- Vendor/upstream copyright exceptions and read-only legacy rule hold.
- Deferred real-host checks are listed with exact commands/artifacts.

## Task Breakdown

### Phase 0: Resolve Outstanding Open Design Questions

#### Task 0.1: Wrapper mechanism for UNCHANGED functions
- **Description**: Decide how `res_simbox_core`'s carried files resolve
  calls to functions classified `UNCHANGED` (identical to upstream
  `chan_dongle`). Recommendation: **(A) direct link** — `res_simbox_core`'s
  build links against `asterisk-chan-dongle`'s compiled objects for every
  symbol it doesn't redefine; no wrapper `.c` files. Simplest, matches
  requirements criterion 3 literally, avoids inventing ~196 forwarding
  stubs. Only fall back to thin wrappers (option B) if Task 0.6 (build
  system) finds the two-object-set link approach isn't actually feasible
  for an Asterisk module (`.so` modules conventionally are one
  self-contained object).
- **Files**: None (decision only).
- **Dependencies**: None.
- **Verification**: Recorded decision unblocks Tasks 1.1-1.4, 6.1.
- **Complexity**: Low (decision), Medium (consequences).

#### Task 0.2: `pvt_start()` cross-module call (core ↔ programmator)
- **Description**: `chan_dongle.c`'s `pvt_start()` calls
  `ttyprog_set_diagmode()`/`ttyprog_changeimei()` directly, but core must
  load standalone without `res_simbox_programmator`. Recommendation:
  **(A) runtime-optional call via Asterisk's own module API** —
  `pvt_start()` guards the two blocks with
  `ast_module_check("res_simbox_programmator.so")` (a real, existing
  Asterisk facility, not new invention) before calling out; if not loaded,
  behaves as if `diagmode`/`changeimei` flags were never set (which is
  also the only way they can be `1` in the first place, since only the
  moved CLI commands set them). Chosen over (B) move-the-trigger-logic
  (would require a new hook/stub, more new-code surface) and (C) dlsym
  (works but `ast_module_check` is the idiomatic Asterisk-native
  equivalent already built for exactly this).
- **Files**: `libsCpp/asterisk-res-simbox-core/src/chan_dongle.c` (the
  carried, trimmed copy — `pvt_start()`'s two conditional blocks gain the
  module-check guard).
- **Dependencies**: Task 1.4 (chan_dongle.c carried into core).
- **Verification**: Manual review confirms the guard compiles conditionally
  correct C (structurally — no live build available); confirms the two
  blocks are unreachable if `res_simbox_programmator` is absent.
- **Complexity**: Medium.

#### Task 0.3: `res_simbox_reader` — adapter vs. emulator scope
- **Description**: Decide whether `res_simbox_reader` needs both legacy
  entry points (`adapter.c` = real hardware, `emulator.c` = simulated) or
  just one. Recommendation: **keep both**, selected by a config directive
  at module load (mirrors how `res_simbox_core`'s own config already
  selects device behavior) — cheaper than deciding to drop a legacy
  capability with `reader/`'s usage otherwise unconfirmed. Revisit only if
  user says `emulator.c` (test-only) can be dropped.
- **Files**: None yet (decision only; affects Task 4.1's structure).
- **Dependencies**: None.
- **Verification**: N/A (decision).
- **Complexity**: Low.

#### Task 0.4: `res_simbox_hub` — real module or standalone tool
- **Description**: Decide whether `hub-ctrl.c` becomes a real Asterisk
  module or stays the standalone `gcc`-built CLI tool it is today, just
  relocated. Recommendation: **keep it standalone** — it has zero
  discovered coupling to Asterisk/`pvt` state (per specs), so forcing an
  `AST_MODULE_INFO`/load-unload lifecycle onto it would be inventing
  structure the tool doesn't need, in tension with "restructure only."
  `libsCpp/asterisk-res-simbox-hub/` holds it as a utility directory (own
  `Makefile`/build rule producing a standalone `hub-ctrl` binary), not an
  Asterisk-loadable `.so`.
- **Files**: None yet (decision only; affects Task 5.1).
- **Dependencies**: None.
- **Verification**: N/A (decision).
- **Complexity**: Low.

#### Task 0.5: Dead code and abandoned-experiment disposition
- **Description**: Confirm exclusion of `dsp.c`, `share_mysql.c`/`.h`
  (dead code, disabled `#include`) and `adiscovery_core_new.c`/
  `adiscovery_simnode.c` (abandoned experiment). Recommendation: **exclude
  all four from every module** — none are reachable from any live build
  path, and copying dead/abandoned code into a fresh module split would
  reintroduce the exact "everything in one pile" problem this whole effort
  exists to fix. Available as historical reference only in
  `legacy/asterisk-chan-svistok-v2014/` (read-only, already there).
- **Files**: None (exclusion decision).
- **Dependencies**: None.
- **Verification**: N/A (decision).
- **Complexity**: Low.

#### Task 0.6: Per-module build system shape
- **Description**: Each module directory needs its own build file
  (Makefile/`configure.in`-equivalent) producing its own `.so` (or, for
  `res_simbox_hub` per Task 0.4, a plain binary). Recommendation: adapt
  `res_simbox_core`'s `Makefile.in`/`configure.in` (carried from legacy,
  Task 1.5) as the template for `res_simbox_discovery`/`programmator`/
  `reader`'s build files — same autotools shape, different `_OBJS`/
  `SOURCES` lists — since copying/adapting an existing legacy build
  pattern is restructuring, not invented infrastructure.
- **Files**: New `Makefile.in`/`configure.in`-equivalents per module
  (exact filenames decided per-module in Phase 2-5's build tasks).
- **Dependencies**: Task 1.5.
- **Verification**: Structural review only (no build environment available).
- **Complexity**: Medium.

### Phase 1: `res_simbox_core`

#### Task 1.1: Copy-then-trim the 27 modified module files
- **Description**: For each of the 27 carried files (`app.c/.h`,
  `at_command.c/.h`, `at_parse.c/.h`, `at_queue.c`, `at_read.c`,
  `at_response.c/.h`, `chan_dongle.c/.h`, `channel.c/.h`, `cli.c/.h`,
  `cpvt.c/.h`, `dc_config.c/.h`, `helpers.c`, `manager.c`, `pdiscovery.c/.h`,
  `pdu.c/.h`, `ringbuffer.c/.h`): copy verbatim from
  `legacy/asterisk-chan-svistok-v2014/` into
  `libsCpp/asterisk-res-simbox-core/src/`, then delete every `UNCHANGED`
  function body (per `02-specifications.md`'s Function-Level
  Classification, reproduced from the source flow), leaving only
  `MODIFIED` functions + whatever local statics/types they require. Apply
  the NativeMind copyright header per file (per the Copyright/Licensing
  constraint), matching the same rule already applied to the sibling
  flow's files: replace entirely, except none of these 27 are literally
  named `chan_dongle.c`/`.h`'s upstream-authored twin — wait, `chan_dongle.c`/
  `.h` **are** in this list; per the established rule they keep bg111's
  original copyright, not NativeMind's (same exception as the sibling
  flow's identically-named files).
- **Files**: 27 files created under `libsCpp/asterisk-res-simbox-core/src/`.
- **Dependencies**: Task 0.1 (wrapper mechanism, affects what "unchanged
  function" resolution looks like at the call sites that remain).
- **Verification**: Per-file diff confirms every remaining function body
  matches its legacy source character-for-character (no retyping); confirms
  no `UNCHANGED`-classified function body remains.
- **Complexity**: High (volume — 27 files, ~150 functions to remove
  precisely).

#### Task 1.2: Create the 10 new companion files
- **Description**: Create `at_command_sim.c`, `at_parse_sim.c`,
  `at_response_sim.c`, `chan_dongle_svistok.c`, `channel_svistok.c`,
  `cli_svistok.c`, `pdiscovery_svistok.c`, `pdu_svistok.c`,
  `ringbuffer_svistok.c`, `at_queue_svistok.c`, each containing the `NEW`
  functions listed for it in specs (verbatim from legacy, copy-then-move,
  never retyped). `cli_svistok.c` excludes `cli_diagmode`/
  `cli_changeimei`/`cli_dongle_update` (Task 3.3). All ten get the
  NativeMind copyright header (all are Svistok-original, no upstream
  exception applies).
- **Files**: 10 new files under `libsCpp/asterisk-res-simbox-core/src/`.
- **Dependencies**: Task 1.1 (functions are being extracted from the
  just-trimmed host files).
- **Verification**: Each function's body diffed against its legacy
  source; confirms it no longer appears in its original host file.
- **Complexity**: Medium.

#### Task 1.3: Carry the already-`#include`d files
- **Description**: Copy `select.c/.h`, `dserial.c`, `limits.c`,
  `share.c/.h`, `stat.c` verbatim into
  `libsCpp/asterisk-res-simbox-core/src/`, preserving their existing
  `#include "file.c"` relationships from `chan_dongle.c`/`at_response.c`/
  `cli.c` (just re-pointed at the new relative paths, which are unchanged
  since everything stays siblings in the same `src/` directory).
  NativeMind copyright header (all Svistok-original).
- **Files**: 7 files.
- **Dependencies**: None (independent of 1.1/1.2).
- **Verification**: Confirm `#include` paths still resolve; confirm file
  contents byte-match legacy.
- **Complexity**: Low.

#### Task 1.4: Apply Task 0.2's `pvt_start()` guard
- **Description**: Add the `ast_module_check()` guard decided in Task 0.2
  to the carried `chan_dongle.c`'s `pvt_start()`.
- **Files**: `libsCpp/asterisk-res-simbox-core/src/chan_dongle.c`.
- **Dependencies**: Task 1.1, Task 0.2.
- **Verification**: Structural review — the two blocks (`diagmode`/
  `changeimei`) are now conditionally reachable only when
  `res_simbox_programmator` is loaded.
- **Complexity**: Medium.

#### Task 1.5: Build files
- **Description**: Carry `configure.in`, `Makefile.in`, `config.h.in`
  (unchanged, no action needed for the last one) into
  `libsCpp/asterisk-res-simbox-core/`; regenerate `single.c` as an ordered
  `#include` list reflecting the final file set from Tasks 1.1-1.3 (not
  hand-copied from legacy, since its legacy content is stale relative to
  this new layout).
- **Files**: `configure.in`, `Makefile.in`, `single.c` (regenerated) under
  `libsCpp/asterisk-res-simbox-core/`.
- **Dependencies**: Tasks 1.1-1.3 (final file list must be known).
- **Verification**: `single.c`'s `#include` list matches exactly the files
  produced by 1.1-1.3.
- **Complexity**: Low.

#### Task 1.6: LICENSE / no-copy-needed files
- **Description**: `LICENSE` already exists and is correct (done prior to
  this plan). Confirm the 18 IDENTICAL-to-upstream files (`at_queue.h`,
  `at_read.h`, `BUGS`, `char_conv.c/.h`, `config.h.in`, `COPYRIGHT.txt`,
  `export.h`, `helpers.h`, `INSTALL`, `LICENSE.txt`, `manager.h`,
  `memmem.c/.h`, `mixbuffer.c/.h`, `mutils.h`, `stamp-h.in`, `TODO.txt`)
  are deliberately **not** copied — `res_simbox_core` resolves them via
  the Task 0.1 link mechanism against `asterisk-chan-dongle` directly.
- **Files**: None created (explicit non-action, documented).
- **Dependencies**: Task 0.1.
- **Verification**: Confirm none of these 18 filenames exist under
  `libsCpp/asterisk-res-simbox-core/src/`.
- **Complexity**: Low.

### Phase 2: `res_simbox_discovery`

#### Task 2.1: Copy live discovery sources
- **Description**: Copy `adiscovery_core.c`, `adiscovery_svistok.c`,
  `adiscovery_test.c` from `legacy/asterisk-chan-svistok-v2014/simnode/`
  into `libsCpp/asterisk-res-simbox-discovery/src/`, verbatim. Exclude
  `adiscovery_core_new.c`/`adiscovery_simnode.c` per Task 0.5. NativeMind
  copyright header (all Svistok-original, no upstream exception).
- **Files**: 3 files.
- **Dependencies**: Task 0.5.
- **Verification**: Byte-diff against legacy source.
- **Complexity**: Low.

#### Task 2.2: Restructure into module lifecycle
- **Description**: Relocate `adiscovery_svistok.c`'s (and, if Task 0.3's
  reader precedent generalizes, `adiscovery_test.c`'s) hand-rolled
  `main()` setup/loop logic into `load_module()`/`unload_module()`-shaped
  entry points, reusing `chan_dongle.c`'s own
  `load_module`/`unload_module`/`self_module` pattern (carried into core
  in Task 1.1) as the structural template — copying an existing legacy
  pattern, not inventing one.
- **Files**: `adiscovery_svistok.c`, `adiscovery_test.c` (modified in
  place after the verbatim copy).
- **Dependencies**: Task 2.1, Task 1.1 (need the template pattern
  available to reference).
- **Verification**: Manual structural review — module has
  `AST_MODULE_INFO`, `load_module()`, `unload_module()`; no business logic
  changed from legacy, only control-flow entry point.
- **Complexity**: Medium.

#### Task 2.3: Build files
- **Description**: New `Makefile.in`/`configure.in`-equivalent per Task
  0.6's template, `_OBJS`/`SOURCES` = the 3 files from Task 2.1.
- **Files**: New build files under `libsCpp/asterisk-res-simbox-discovery/`.
- **Dependencies**: Task 0.6, Task 2.1.
- **Verification**: Structural review only.
- **Complexity**: Low.

### Phase 3: `res_simbox_programmator`

#### Task 3.1: Copy the live slice (already linked into core today)
- **Description**: Copy `ttyprog_svistok.c`, `ttyprog_core.c` (the
  **live**, longer variant — not the stale top-level/`old/` copy), `crc.c`
  from `legacy/asterisk-chan-svistok-v2014/programmator/` into
  `libsCpp/asterisk-res-simbox-programmator/src/`, verbatim.
- **Files**: 3 files.
- **Dependencies**: None.
- **Verification**: Byte-diff against the `programmator/` (not top-level)
  legacy source specifically.
- **Complexity**: Low.

#### Task 3.2: Copy the standalone tool's remaining sources
- **Description**: Copy `ttyprog_programmator.c`, `tty_v2.c`, `addons.c`,
  `ttyprog_test.c` from `legacy/asterisk-chan-svistok-v2014/programmator/`
  verbatim.
- **Files**: 4 files.
- **Dependencies**: None.
- **Verification**: Byte-diff against legacy.
- **Complexity**: Low.

#### Task 3.3: Create `cli_programmator.c`
- **Description**: Move `cli_diagmode`, `cli_changeimei`,
  `cli_dongle_update` (currently classified as `NEW` functions in
  `cli.c`) into a new `cli_programmator.c`, registering them as this
  module's own Asterisk CLI commands instead of core's.
- **Files**: `cli_programmator.c` (new).
- **Dependencies**: Task 1.1 (must know these three are excluded from
  core's `cli.c`/`cli_svistok.c`).
- **Verification**: Function bodies diffed against legacy `cli.c`;
  confirm they don't appear in core's `cli_svistok.c` (Task 1.2).
- **Complexity**: Medium (these functions reference `pvt`/device lookup —
  confirm the lookup mechanism still resolves once physically relocated
  to a different module; may surface a second instance of the Task 0.2
  cross-module-reference problem, worth a dedicated look during
  implementation, not assumed clean here).

#### Task 3.4: Restructure standalone tool into module lifecycle
- **Description**: Same treatment as Task 2.2 — relocate
  `ttyprog_programmator.c`'s hand-rolled `main()` into a module lifecycle,
  using the same `chan_dongle.c`-derived template.
- **Files**: `ttyprog_programmator.c` (modified in place).
- **Dependencies**: Task 3.2, Task 1.1.
- **Verification**: Structural review.
- **Complexity**: Medium.

#### Task 3.5: Carry deploy/fleet-update scripts
- **Description**: Copy `fuall.sh`, `fupdate3.sh`, `fupdate4.sh`,
  `updateall2.sh`, `updateall3.sh`, `prog.sh`, `upgrade_prog.sh` verbatim;
  update any hardcoded `/usr/simbox/programmator/...` paths to match this
  module's actual install location once Task 0.6 settles it.
- **Files**: 7 scripts.
- **Dependencies**: Task 0.6.
- **Verification**: Confirm script content matches legacy except the
  path updates, explicitly diffed and called out.
- **Complexity**: Low.

#### Task 3.6: Build files
- **Description**: New build file(s) per Task 0.6's template covering
  both the module (`.so`, from Task 3.1's slice + Task 3.3) and the
  standalone tool binary (from Task 3.2/3.4).
- **Files**: New build files under
  `libsCpp/asterisk-res-simbox-programmator/`.
- **Dependencies**: Task 0.6, Tasks 3.1-3.4.
- **Verification**: Structural review only.
- **Complexity**: Medium.

### Phase 4: `res_simbox_reader`

#### Task 4.1: Copy reader sources
- **Description**: Copy `reader_core.c/.h`, `adapter.c`, `emulator.c`
  from `legacy/asterisk-chan-svistok-v2014/reader/` verbatim. Per Task
  0.3, keep both `adapter.c` and `emulator.c`. Re-point
  `reader_core.h`'s `#include "../programmator/tty_v2.c"` to
  `libsCpp/asterisk-res-simbox-programmator/src/tty_v2.c`'s final
  location (cross-module include — flag if this turns out to need the
  same kind of resolution as Task 0.2's coupling, don't assume it's free).
- **Files**: 4 files.
- **Dependencies**: Task 0.3, Task 3.2 (need `tty_v2.c`'s final path).
- **Verification**: Byte-diff against legacy except the one re-pointed
  include line, explicitly called out.
- **Complexity**: Medium (the cross-module include is a real wrinkle, not
  a trivial copy).

#### Task 4.2: Restructure into module lifecycle
- **Description**: Same treatment as Task 2.2, for both `adapter.c` and
  `emulator.c` (per Task 0.3's "keep both, config-selected" decision) —
  likely a single `load_module()` that reads a config directive to decide
  which core variant's behavior to expose, rather than two separate
  `AST_MODULE_INFO`s.
- **Files**: `adapter.c`, `emulator.c` (modified in place).
- **Dependencies**: Task 4.1, Task 1.1 (template).
- **Verification**: Structural review.
- **Complexity**: Medium.

#### Task 4.3: Carry non-code artifact
- **Description**: Copy `reader/g.sh`, review its content (previously
  flagged "unreviewed") before deciding if it needs adaptation.
- **Files**: `g.sh`.
- **Dependencies**: None.
- **Verification**: Content review recorded in implementation log.
- **Complexity**: Low.

#### Task 4.4: Build files
- **Description**: New build file per Task 0.6's template.
- **Files**: New build files under `libsCpp/asterisk-res-simbox-reader/`.
- **Dependencies**: Task 0.6, Task 4.1.
- **Verification**: Structural review only.
- **Complexity**: Low.

### Phase 5: `res_simbox_hub`

#### Task 5.1: Copy `hub-ctrl.c`
- **Description**: Copy verbatim from
  `legacy/asterisk-chan-svistok-v2014/hub-ctrl.c`. Per Task 0.4, this
  stays a standalone utility, not an Asterisk module — **copyright
  header is NOT touched** (vendor/third-party code, per explicit user
  rule).
- **Files**: `hub-ctrl.c`.
- **Dependencies**: Task 0.4.
- **Verification**: Byte-diff against legacy; confirm copyright header
  unchanged from legacy original.
- **Complexity**: Low.

#### Task 5.2: Build file
- **Description**: Simple build rule producing a standalone `hub-ctrl`
  binary (mirrors legacy's ad-hoc `gcc hub-ctrl.c -lusb -o hub-ctrl`), not
  an Asterisk module build.
- **Files**: New build file under `libsCpp/asterisk-res-simbox-hub/`.
- **Dependencies**: Task 0.4, Task 5.1.
- **Verification**: Structural review only.
- **Complexity**: Low.

### Phase 6: Cross-Cutting / Integration

#### Task 6.1: Update deploy scripts for the five-module layout
- **Description**: `upgrade.sh` (legacy) rebuilds the module + programmator
  + hub-ctrl as one combined sequence; update it (in whichever module
  ends up hosting it, likely `res_simbox_core` as the "top-level" deploy
  entry point) to build/install all five module directories.
- **Files**: `upgrade.sh` (carried + modified).
- **Dependencies**: Tasks 1.5, 2.3, 3.6, 4.4, 5.2 (all five modules' build
  files must exist first).
- **Verification**: Structural review — script references all five
  module directories' build outputs.
- **Complexity**: Medium.

#### Task 6.2: Full cross-module reference audit
- **Description**: One consolidated pass confirming every cross-module
  reference discovered during Phases 1-5 (Task 0.2's `pvt_start()` guard,
  Task 3.3's CLI-command pvt lookup, Task 4.1's `tty_v2.c` cross-module
  include) is accounted for and consistent — a final integration check
  rather than a new discovery step.
- **Files**: None (audit/verification task).
- **Dependencies**: All of Phases 1-5.
- **Verification**: Written audit note in `04-implementation-log.md`
  listing every cross-module reference and its resolution.
- **Complexity**: Medium.

## Dependency Graph

```
Task 0.1 (wrapper) ──┬──→ Task 1.1 ──→ Task 1.2
                      │         │
Task 0.2 (pvt_start) ─┼─────────┴──→ Task 1.4
                      │
Task 0.5 (dead code) ─┴──→ Task 2.1 ──→ Task 2.2
                                             │
Task 0.6 (build) ──┬──→ Task 1.5            │
                    ├──→ Task 2.3 ←──────────┘
                    ├──→ Task 3.6 ←── Tasks 3.1-3.4
                    ├──→ Task 4.4 ←── Task 4.1 (needs Task 0.3, Task 3.2)
                    └──→ Task 5.2 ←── Task 5.1 (needs Task 0.4)

Task 1.1 ──→ Task 3.3 (needs to know what's excluded from core's cli.c)
Task 3.2 ──→ Task 4.1 (tty_v2.c cross-module include)

All Phase 1-5 build tasks ──→ Task 6.1 ──→ Task 6.2
```

## File Change Summary

| Module | New files | Notes |
|---|---|---|
| `res_simbox_core` | 27 carried + 10 new companion + 7 already-separated + 3 build (incl. regenerated `single.c`) = **47** | `chan_dongle.c`/`.h` keep bg111 copyright; rest get NativeMind header; 18 files deliberately not copied (link to upstream) |
| `res_simbox_discovery` | 3 carried + build file(s) = **4+** | 2 files excluded (abandoned) |
| `res_simbox_programmator` | 3 + 4 + 1 new (`cli_programmator.c`) + 7 scripts + build file(s) = **15+** | |
| `res_simbox_reader` | 4 carried + 1 script + build file(s) = **6+** | |
| `res_simbox_hub` | 1 carried (copyright untouched) + build file = **2** | Not an Asterisk module (Task 0.4) |

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Task 0.2's `ast_module_check()` guard doesn't behave as expected without a real Asterisk runtime to test against | High (no build env) | Medium | Structural review + careful reading of Asterisk's module API docs/other in-tree usages; flag as a T3/T4-style deferred verification, consistent with every prior flow in this family |
| Task 3.3 surfaces a second `pvt`-lookup cross-module coupling, symmetric to Task 0.2 | Medium | Medium | Task 6.2 exists specifically to catch this; don't assume Task 3.3 is "just a file move" going in |
| Task 4.1's cross-module `#include` (`reader` → `programmator`'s `tty_v2.c`) turns out to be load-order-fragile between two separate `.so` modules | Medium | Medium | Flagged explicitly in Task 4.1; may force `tty_v2.c` to be duplicated into `res_simbox_reader` instead (a legitimate small deviation, log it if it happens) |
| Manual per-function trimming (Task 1.1, ~150 functions across 27 files) introduces a transcription error despite "copy-then-delete, never retype" discipline | Medium | High | Byte-diff verification per function against legacy is mandatory per task, not optional |

## Rollback Strategy

1. Every task's output lives entirely under the five new
   `libsCpp/asterisk-res-simbox-*/` directories — none of them existed
   with content before this plan, so rollback is simply: delete the
   directory contents created by the task(s) being reverted.
2. `legacy/` and `libsCpp/asterisk-chan-svistok/asterisk-chan-dongle/`
   are never written to by this plan — always available as the source of
   truth to re-derive from.
3. No shared/external state (databases, running services) is touched —
   all work is source-file creation.

## Checkpoints

After each phase, verify:

- [ ] Every new file's content byte-matches its legacy source in the
      surviving (non-deleted) portions.
- [ ] No `UNCHANGED`-classified function body survives in any core file
      (Phase 1).
- [ ] No dead/abandoned file (Task 0.5's exclusion list) appears in any
      module.
- [ ] Copyright headers match the rule: NativeMind everywhere, except
      `chan_dongle.c`/`.h` (bg111) and `hub-ctrl.c` (vendor, untouched).
- [ ] `04-implementation-log.md` records every cross-module reference
      found, per Task 6.2.

## Open Implementation Questions

- [ ] Task 0.2/3.3/4.1 collectively suggest this module split has *more*
      cross-module coupling than the five-clean-boxes framing implies —
      worth a brief check-in with the user after Phase 0/early Phase 1 to
      confirm the recommended defaults (especially Task 0.2's
      `ast_module_check()` approach) still feel right once their full
      shape is visible, rather than only surfacing it at the end.
- [ ] Exact final directory convention for build files per module (single
      `Makefile` vs. autotools `configure.in`+`Makefile.in` per Task 0.6)
      — recommended default is "mirror core's autotools shape," but this
      is worth a quick sanity check against how `libsCpp/asterisk-chan-svistok/`
      (the sibling flow) actually built things, for consistency across
      the two flows' outputs.

---

## Approval

- [x] Version 1.0 reviewed by: Anton
- [x] Version 1.0 approved on: 2026-08-26
- [x] Version 1.0 notes: implemented with deviations documented in
      `04-implementation-log.md`; retained as history.
- [x] Version 1.2 reviewed by: Anton
- [x] Version 1.2 approved on: 2026-08-26
- [x] Version 1.2 notes: characterization tests precede source transfer;
      implementation authorized.
