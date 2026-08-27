# Specifications: res-simbox (module split)

> Version: 1.2
> Status: DRAFT
> Last Updated: 2026-08-26
> Requirements: [01-requirements.md](01-requirements.md)

> **Moved from**: `flows/asterisk-chan-svistok/sdd-asterisk-chan-svistok-chan-dongle/02-specifications.md`
> ("Planned Module Layout (v1.1)" section and the module-split-specific
> Open Design Questions/Edge Cases). The full file/function classification
> (NEW/MODIFIED/UNCHANGED/REMOVED tables, full legacy-tree inventory,
> header-change summary, `#include "file.c"` composition discovery) stays
> owned by that flow — this document references it rather than
> duplicating it, to avoid the two copies drifting apart.

## Overview

Output goes to five module directories instead of one flat `src/`:

- **`libsCpp/asterisk-res-simbox-core/src/`**
- **`libsCpp/asterisk-res-simbox-discovery/src/`**
- **`libsCpp/asterisk-res-simbox-programmator/src/`**
- **`libsCpp/asterisk-res-simbox-reader/src/`** (added v1.1)
- **`libsCpp/asterisk-res-simbox-hub/src/`** (added v1.1)

The file/function classification (which functions are NEW/MODIFIED/
UNCHANGED/REMOVED) lives in the source flow
(`flows/asterisk-chan-svistok/sdd-asterisk-chan-svistok-chan-dongle/02-specifications.md`)
and is unchanged here — this document only re-partitions *where* each
already-classified piece lands, per the user's explicit instruction that
this pass is a **pure move of existing classified code, nothing new
invented**. The one exception, called out below, is a real runtime
coupling discovered inside `chan_dongle.c` (`pvt_start`) that calls
directly into programmator's protocol functions — a genuine cross-module
boundary question, not a source-layout question.

## Version 1.2 Runtime Architecture: Reader and Hub

This section supersedes the v1.1 reader/hub delivery-shape assumptions
later in this document. Both components produce two artifacts from one
shared implementation:

| Component | Standalone artifact | Asterisk artifact |
|---|---|---|
| Reader | `res-simbox-reader` | `res_simbox_reader.so` |
| Hub | `res-simbox-hub` | `res_simbox_hub.so` |

`hub-ctrl` remains a compatible build/install alias for existing deploy
scripts, but it resolves to the same hub implementation rather than a
third copy.

### Source Composition

Each component has three layers:

1. **Shared implementation** — copied/refactored legacy hardware and
   protocol behavior, with no Asterisk lifecycle and no process
   termination. The same objects are linked into both artifacts.
2. **Standalone adapter** — argument parsing, user output, `main()`, and
   conversion of the shared return value to process exit status.
3. **Asterisk adapter** — `AST_MODULE_INFO`, CLI/config integration,
   optional registration with core, Asterisk logging/result adaptation,
   and unload cleanup.

The current `reader_cli.c` duplicates the bodies from `adapter.c` and
`emulator.c`; v1.2 removes that duplication. Each exact legacy sequence
is extracted once into a callable shared function, and both adapters call
it. Reference-only files must not remain as a second maintained
implementation.

The vendored `hub-ctrl.c` keeps its original authorship and copyright.
Its operational body is made callable without `exit()` so invoking it
cannot terminate Asterisk. The standalone `main()` is a separate adapter
over the same body. Asterisk/core headers do not enter the vendored
operational layer.

### Planned v1.2 Files

Legacy function bodies are moved into these destinations, not retyped:

| File | Responsibility |
|---|---|
| `reader/src/reader_core.c/.h` | Existing common reader/TTY implementation |
| `reader/src/reader_adapter.c` | Callable diagnostic extracted from legacy `adapter.c:main()` |
| `reader/src/reader_emulator.c` | Callable diagnostic extracted from legacy `emulator.c:main()` |
| `reader/src/reader_service.h` | Asterisk-free reader contract |
| `reader/src/reader_main.c` | `res-simbox-reader` entry point selecting adapter/emulator mode |
| `reader/src/reader_module.c` | Asterisk lifecycle/CLI and core-registration adapter |
| `hub/src/hub-ctrl.c` | Single vendored hub implementation, refactored to return errors |
| `hub/src/hub_service.h` | Asterisk-free hub contract |
| `hub/src/hub_main.c` | `res-simbox-hub` and compatible `hub-ctrl` entry point |
| `hub/src/hub_module.c` | Asterisk lifecycle/CLI and core-registration adapter |
| `core/include/res_simbox_component.h` | Versioned public descriptor and operations contract |
| `core/src/component_registry.c/.h` | Thread-safe registry owned by core; never a module loader |

Paths in the table are relative to the matching
`libsCpp/asterisk-res-simbox-*` directory.

Reader retains both legacy modes in both delivery forms. Legacy device
paths `/dev/ttyUSB24` and `/dev/ttyUSB25` remain defaults. An adapter may
pass an explicit path into the shared function without changing the
copied APDU/emulator sequence.

### Core Registration Contract

`res_simbox_core` owns a versioned `struct res_simbox_component` carrying
the ABI version, kind (`reader`/`hub`), stable name, owning
`struct ast_module *`, availability/status callback, and typed operation
callbacks. Reader operations cover adapter/emulator actions; hub
operations cover list, power, and LED actions. Optional quiesce/reload
callbacks exist only where a component keeps persistent state.

Core exports `res_simbox_component_register()` and
`res_simbox_component_unregister()` through Asterisk's optional-API
mechanism. Each child exports small optional descriptor/attach/detach
entry points too. Every module that provides these symbols uses
`AST_MODFLAG_GLOBAL_SYMBOLS`, as required by Asterisk 11's
`optional_api.h`. Both load orders work:

- child after core: register during the child's `load_module()`;
- core after child: core invokes the already-loaded child's attach entry;
- child unload: unregister before freeing its state;
- core unload: invoke each registered child's detach entry, then destroy
  the registry without unloading the child; the child clears its attached
  state and continues in independent-module mode.

Dispatch holds an Asterisk module reference for the callback duration.
Duplicate kind/name registration is rejected. ABI mismatch leaves the
child independently usable but unregistered and logs the mismatch.
After detach, the child must not call a cached core callback. A later core
load discovers the still-loaded child through its global optional
descriptor/attach API and establishes a fresh registration.

The contract contains no `ast_load_resource()` or
`ast_unload_resource()` calls. Core never starts, stops, monitors, or
communicates with standalone processes.

### Resource Ownership

Before opening hardware, either adapter acquires an OS-visible per-device
lock and releases it on every success, failure, and unload path. A second
binary/module request for the same device returns an explicit busy
result; it never takes over implicitly. Registration itself opens no
hardware and therefore cannot double-initialize a device.

### Build Graph

- Reader shared objects are linked into both `res-simbox-reader` and
  `res_simbox_reader.so`; only `reader_main.o` versus `reader_module.o`
  differs.
- Hub shared objects are linked into both `res-simbox-hub` and
  `res_simbox_hub.so`; only `hub_main.o` versus `hub_module.o` differs.
- Standalone targets include no Asterisk headers and link no Asterisk or
  core objects.
- Module targets use the public registration header, but load without
  core because registration is an optional API.

**Prerequisite context from the source flow** (summarized here for
convenience, not re-derived): the legacy build already composes several
new files into their host `.c` file via textual `#include "sibling.c"` —
`select.c` into `chan_dongle.c`; `dserial.c`+`limits.c` into
`at_response.c`; `share.c`+`stat.c`+`programmator/ttyprog_svistok.c`
(which itself `#include`s `programmator/ttyprog_core.c`) into `cli.c`.
`dsp.c` and `share_mysql.c` use the same pattern but are commented out —
dead code, not compiled in legacy. See the source flow's "Key Discovery"
section for the full evidence.

## Planned Module Layout (concrete deliverable)

Legend: **[carry]** = copy-then-trim (file already exists upstream, only
new/modified functions remain, per the source flow's criterion 3);
**[new]** = copy-as-is (no upstream counterpart, per criterion 2). This is
a **pure re-partitioning** of the source flow's classified functions — the
only functional change from that flow's original single-module plan is
that three CLI functions (`cli_diagmode`, `cli_changeimei`,
`cli_dongle_update`) move from the core companion file to the
programmator module, per acceptance criterion 2.

### `libsCpp/asterisk-res-simbox-core/src/` — the channel driver (direct successor of `chan_dongle.so`/`chan_svistok.so`, must load and run standalone)

**Modified module files, trimmed to MODIFIED functions + required local statics/types (UNCHANGED functions call straight through to `asterisk-chan-dongle`'s compiled implementation — see the source flow's Open Design Questions for the wrapper mechanism, a question that applies here unchanged)**:

`app.c` **[carry]**, `app.h` **[carry]**, `at_command.c` **[carry]**, `at_command.h` **[carry]**, `at_parse.c` **[carry]**, `at_parse.h` **[carry]**, `at_queue.c` **[carry]**, `at_read.c` **[carry]**, `at_response.c` **[carry]**, `at_response.h` **[carry]**, `chan_dongle.c` **[carry]**, `chan_dongle.h` **[carry]**, `channel.c` **[carry]**, `channel.h` **[carry]**, `cli.c` **[carry]**, `cli.h` **[carry]**, `cpvt.c` **[carry]**, `cpvt.h` **[carry]**, `dc_config.c` **[carry]**, `dc_config.h` **[carry]**, `helpers.c` **[carry]**, `manager.c` **[carry]**, `pdiscovery.c` **[carry]**, `pdiscovery.h` **[carry]**, `pdu.c` **[carry]**, `pdu.h` **[carry]**, `ringbuffer.c` **[carry]**, `ringbuffer.h` **[carry]**

**`src/dongle/` (pure-proxy files)**: expected empty — none of the 17
module files qualify as 100%-unchanged (every one has at least one
MODIFIED/NEW function; see the source flow's Function-Level
Classification). Borderline case: `tools/tty.c` (a standalone helper tool,
not part of this module, 5/6 functions unchanged, 1 modified) — not part
of any of the three modules' scope as currently understood; flagged in
the source flow, carried here for awareness only.

**New companion files for chan_svistok-only functions, core scope**:

| New file | Contains |
|---|---|
| `at_command_sim.c` **[new]** | `at_enque_initialization_modem`, `at_enque_initialization_sim_e`, `at_enque_initialization_sim_mb`, `at_enque_initialization_sim`, `at_enque_cmd_proc`, `at_enque_spn`, `at_enque_iccid`, `at_enque_sn`, `at_enque_cfun_v`, `at_enque_cpin_v`, `at_enque_cfun1`, `at_enque_cfun5`, `at_enque_cfun6`, `at_enque_sysinfo` |
| `at_parse_sim.c` **[new]** | `at_parse_spn`, `at_parse_cds`, `at_parse_sysinfo` |
| `at_response_sim.c` **[new]** | `at_response_dsflowrpt`, `at_response_sysinfo`, `set_channel_vars2`, `at_response_cds`, `at_response_spn`, `at_response_cvoice`, `at_response_cardlock`, `at_response_freqlock`, `at_response_sn`, `at_response_iccid`, `at_response_cfun_v`, `at_response_simst`, `at_response_srvst`, `at_response_unknown` |
| `chan_dongle_svistok.c` **[new]** | `can_sms`, `ast_channel_show_vars`, `ast_channel_get_var`, `pvt_create_new` |
| `channel_svistok.c` **[new]** | `channel_request` |
| `cli_svistok.c` **[new]** | `cli_show_devicesl`, `cli_show_devicesd`, `cli_show_devicesi`, `cli_setgroup`, `cli_setgroupimsi` — **`cli_diagmode`/`cli_changeimei`/`cli_dongle_update` excluded here; they move to the programmator module below** |
| `pdiscovery_svistok.c` **[new]** | `pdiscovery_handle_sn` |
| `pdu_svistok.c` **[new]** | `pdu_parse_cds` |
| `ringbuffer_svistok.c` **[new]** | `rb_read_until_char_after_iov` |
| `at_queue_svistok.c` **[new]** | `at_log` |

*(Alternative feature-based grouping — e.g. consolidating the SIM-identity
functions across `at_command_sim.c`/`at_parse_sim.c`/`at_response_sim.c`
into one file — remains a Plan-phase judgment call, per the source flow.)*

**Already-separated new files (`#include`d into a host — keep as-is, same relative placement)**:

`select.c` **[new]**, `select.h` **[new]** (included from `chan_dongle.c`)
`dserial.c` **[new]**, `limits.c` **[new]** (included from `at_response.c`)
`share.c` **[new]**, `share.h` **[new]**, `stat.c` **[new]** (included from `cli.c`)

**Build files**: `configure.in` **[carry]**, `Makefile.in` **[carry]**, `config.h.in` (identical, no action), `single.c` (regenerate from the final file list, don't hand-copy — it's just an ordered list of `#include`s)

**⚠️ Concrete cross-module coupling** (see "Open Design Questions" below): `chan_dongle.c`'s `pvt_start()` (already classified `MODIFIED`) directly calls `ttyprog_set_diagmode(pvt->data_fd)` and `ttyprog_changeimei(pvt->audio_fd, pvt->newimei)` when `pvt->diagmode==1` / `pvt->changeimei==1` (legacy lines ~737-761). Those flags are set **only** by the CLI commands moving to `res_simbox_programmator`. Core's own `pvt_start` — not just the CLI layer — has a real functional call into programmator's protocol functions.

**No physical copy needed at all (resolve via direct link to `asterisk-chan-dongle`, all IDENTICAL to upstream)**: `at_queue.h`, `at_read.h`, `BUGS`, `char_conv.c`, `char_conv.h`, `config.h.in`, `COPYRIGHT.txt`, `export.h`, `helpers.h`, `INSTALL`, `LICENSE.txt`, `manager.h`, `memmem.c`, `memmem.h`, `mixbuffer.c`, `mixbuffer.h`, `mutils.h`, `stamp-h.in`, `TODO.txt`

### `libsCpp/asterisk-res-simbox-discovery/src/` — device-discovery module (today: standalone `simnode/` daemon)

`adiscovery_core.c` **[new]** (the live core — used by 2 of 3 entry points), `adiscovery_svistok.c` **[new]**, `adiscovery_test.c` **[new]**

Recommended **excluded** (likely-abandoned experiment, pending confirmation): `adiscovery_core_new.c`, `adiscovery_simnode.c` (its only caller)

**Restructuring required beyond file placement** (still "move, don't invent" — the target shape is an `AST_MODULE_INFO`/load-unload lifecycle instead of a hand-rolled `main()`): the existing legacy `main()` bodies in `adiscovery_svistok.c`/`adiscovery_test.c` need their setup/loop logic relocated into `load_module()`/`unload_module()`-shaped entry points. Working assumption (not yet confirmed): reuse `chan_dongle.c`'s own existing `load_module`/`unload_module`/`self_module` as the structural template, since that pattern already exists in legacy — copying its shape is restructuring, not invention.

### `libsCpp/asterisk-res-simbox-programmator/src/` — firmware-flashing module (today: split between the standalone `programmator` tool and a slice linked into core's `cli.c`)

**From the slice already linked into core today** (transitively `#include`d via `cli.c` — the *live* versions from `programmator/`, not the stale top-level/`old/` copies):

`ttyprog_svistok.c` **[new]**, `ttyprog_core.c` **[new]**, `crc.c` **[new]**

**From the standalone flashing tool** (today built ad-hoc via `prog.sh`/`upgrade_prog.sh` as a separate binary, not an Asterisk module):

`ttyprog_programmator.c` **[new]** (has its own `main()` — needs relocating into a module lifecycle, same caveat as discovery above), `tty_v2.c` **[new]**, `addons.c` **[new]**, `ttyprog_test.c` **[new]**

**CLI commands moved from core** (per Requirements acceptance criterion 2 — same legacy function bodies, relocated, registering their own Asterisk CLI here instead of in core's `cli.c`):

| New file | Contains |
|---|---|
| `cli_programmator.c` **[new]** | `cli_diagmode`, `cli_changeimei`, `cli_dongle_update` (moved from core's `cli.c`/`cli_svistok.c` — no filename had been assigned for these when they were first listed as moving; naming them now so every function in this layout has a concrete destination file) |

**Fleet-update / deploy scripts** (non-code, referenced by `chan_dongle.c`'s `usbdevs_filelist_*` calls with paths like `/usr/simbox/programmator/fuall.sh` — paths will need updating once the module's install location is decided, a Plan-phase task): `fuall.sh`, `fupdate3.sh`, `fupdate4.sh`, `updateall2.sh`, `updateall3.sh`, `prog.sh`, `upgrade_prog.sh`

**⚠️ Same coupling flagged above, from the other side**: this module's `ttyprog_set_diagmode`/`ttyprog_changeimei` are called directly from core's `pvt_start()`, not just from the CLI commands being moved here.

### `libsCpp/asterisk-res-simbox-reader/src/` — SIM reader/emulator module (added v1.1; today: `reader/`, no build-script or module reference found anywhere in legacy)

**Superseded delivery shape:** v1.2 replaces the module-only duplicated
CLI implementation with the shared implementation and two adapters
specified above. The legacy inventory in this subsection remains valid.

`reader_core.c` **[new]**, `reader_core.h` **[new]** (currently `#include`s `../programmator/tty_v2.c` — that relative include needs re-pointing once both modules' final paths are fixed, a Plan-phase task), `adapter.c` **[new]**, `emulator.c` **[new]** (both `#include "reader_core.c"` today)

Excluded (nested stale duplicates, same rationale as top-level `old/`): `reader/old/comport.pas`, `reader/old/copy.c`, `reader/old/test.c`

Non-code: `reader/g.sh` (unreviewed helper script — carry forward, review during Plan phase)

**Resolved by v1.2:** both adapter and emulator modes remain available in
both delivery forms and share their extracted callable implementations.

### `libsCpp/asterisk-res-simbox-hub/src/` — USB hub power-control module (added v1.1; today: standalone `hub-ctrl.c`)

**Superseded delivery shape:** v1.2 requires both a standalone artifact
and an independently loadable/core-registering Asterisk module, backed by
the same vendored operational implementation.

`hub-ctrl.c` **[new]** (vendored third-party, unmodified from legacy — attribution comment should note it is vendored, not Svistok-authored)

**Zero legacy coupling found**: a full-tree grep found `hub-ctrl.c`
referenced only by `upgrade.sh`/`upgrade_prog.sh`'s ad-hoc build step.
The core relationship introduced by v1.2 is therefore explicit
lifecycle/coordination glue, not a newly discovered legacy coupling.

### Dead code — recommend excluding from all modules (confirm with user before Plan phase)

`dsp.c` (46 functions, disabled `#include` in `chan_dongle.c`), `share_mysql.c`/`share_mysql.h` (14 functions, disabled `#include` in `cli.c`)

### Non-code artifacts to carry forward as-is (documentation/ops, not compiled)

`README.md`, `README_ru.md` (core-level docs — cover the whole project, keep at `libsCpp/asterisk-res-simbox-core/` or a shared top level, Plan-phase call), `md.sh` (runtime directory bootstrap — cross-reference `flows/asterisk-chan-svistok/adr-003-file-state-persistence`), `upgrade.sh` (spans all five modules' build/deploy — needs updating once install layout is final)

### Excluded entirely (not copied anywhere)

`old/` (whole dir — stale duplicate), `reader/old/` (nested stale duplicate), top-level stale duplicates of `tty_v2.c`/`ttyprog_core.c`/`ttyprog_programmator.c`/`ttyprog_test.c`/`ttyprog_svistok.c`, all build artifacts and autotools-generated files, all junk/scratch files (`1`,`2`,`3`,`d`,`CONF!!!!!!!!!!!`,`list`,`list2`,`todo`,`LICENSE`), `update.sh` (generic, not project-specific)

## Edge Cases (module-split-specific)

| Case | Trigger | Handling |
|---|---|---|
| `chan_dongle.c`'s `pvt_start()` calls `ttyprog_set_diagmode`/`ttyprog_changeimei` directly | Core module code calling into what's now a separate `res_simbox_programmator` module | Not resolved here — see Open Design Questions. Core cannot statically link these symbols if it must load standalone without programmator present. |
| `adiscovery_core.c` vs `adiscovery_core_new.c` | Migrating `simnode/` into `res_simbox_discovery` | Use `adiscovery_core.c` (referenced by 2 of 3 entry points); flag `adiscovery_core_new.c` as likely-abandoned for user confirmation before excluding outright. |
| Two different `ttyprog_core.c`/`tty_v2.c` variants (top-level/`old/` vs `programmator/`) | Migrating firmware-flashing code into `res_simbox_programmator` | Use only the `programmator/` (live, longer) variant; do not migrate the stale top-level/`old/` copies. |
| Hand-rolled `main()` in `adiscovery_svistok.c`/`ttyprog_programmator.c` | Promoting standalone binaries to real Asterisk modules | Relocate setup/loop logic into `load_module()`/`unload_module()`-shaped entry points, reusing `chan_dongle.c`'s own registration pattern as the template (working assumption, unconfirmed). |
| Reader/hub child loads before core | Valid independent-module load order | Child works independently; core's later load calls its optional attach entry. |
| Core loads before reader/hub child | Valid managed-mode load order | Child registers from its own `load_module()`. |
| Core unloads while child stays loaded | Core is optional | Registry detaches; child continues independently. |
| Child unload races with core dispatch | Operator unload during managed action | Dispatch holds a module reference; unregister prevents new calls. |
| Binary and module select the same device | Cross-process ownership conflict | Per-device lock rejects the second owner as busy. |
| Vendored hub path calls `exit()` | Operational code invoked inside Asterisk | Return status to the adapter; only `hub_main.c` exits the process. |

## Open Design Questions

- [ ] **The `pvt_start()` cross-module call (highest-priority open
      question)**: core's `chan_dongle.c:pvt_start()` calls
      `ttyprog_set_diagmode()` and `ttyprog_changeimei()` directly —
      functions that now live in `res_simbox_programmator`. Per
      Requirements, core must load and run standalone with
      `res_simbox_programmator` absent. Options, **none chosen yet**:
  - **(A) Runtime-optional call via Asterisk's own module API** — guard
    the call with Asterisk's existing `ast_module_check()`/module-ref
    mechanism (a standard, already-existing Asterisk facility for
    optional inter-module calls, not something this flow would be
    inventing) so `pvt_start` simply skips the block if
    `res_simbox_programmator` isn't loaded.
  - **(B) Move the triggering logic, not just the CLI commands** — relocate
    the `if (pvt->diagmode==1) {...}` / `if (pvt->changeimei==1) {...}`
    blocks themselves out of `pvt_start()` into `res_simbox_programmator`
    (e.g. as a hook core calls unconditionally, which the programmator
    module implements as a no-op stub when absent — but a "stub" would be
    new code, in tension with "restructure only").
  - **(C) Weak symbol / dlsym lookup** — resolve
    `ttyprog_set_diagmode`/`ttyprog_changeimei` at runtime only if present,
    skip otherwise. Standard C mechanism, minimal new glue (a couple of
    `dlsym` calls), no core-side hard link dependency.
  This is the single biggest unresolved question standing between "full
  lists" (done, above) and an actual Plan phase — flagging clearly rather
  than picking one silently, per the user's "only move code, don't invent"
  instruction.
- [ ] Does `res_simbox_discovery` replace the standalone `simnode` daemon
      entirely, or coexist with a still-standalone build target?
- [ ] Confirm disposition of `dsp.c` and `share_mysql.c` (dead code) —
      exclude from all three modules entirely, or keep as reference
      material?
- [ ] Confirm `adiscovery_core_new.c` / `adiscovery_simnode.c` are safe to
      exclude as abandoned experiments.
- [x] **Resolved 2026-08-26**: `reader/` becomes its own module,
      `res_simbox_reader` — see "Planned Module Layout" above. v1.2 also
      resolves the sub-question: both `adapter` and `emulator` remain.
- [x] **Resolved 2026-08-26**: `hub-ctrl.c` becomes its own module,
      `res_simbox_hub`, not folded into `res_simbox_programmator` as v1.0
      tentatively proposed. v1.2 requires both module and binary forms.
- [x] `res_simbox_reader`: both adapter and emulator modes in standalone
      and Asterisk forms.
- [x] `res_simbox_hub`: both real Asterisk module (`AST_MODULE_INFO`) and
      standalone executable, sharing one implementation.
- [x] Core management: Asterisk loads/unloads modules; core coordinates
      already-loaded registered modules and never supervises binaries.
- [ ] Confirm the "one companion file per host" grouping for `NEW`
      functions in core vs. the feature-based alternative grouping.
- [ ] **Inherited from the source flow, still relevant to core**: wrapper
      mechanism for `UNCHANGED` functions (direct link against
      `asterisk-chan-dongle`'s compiled objects vs. generated thin-wrapper
      `.c` files) — see that flow's Open Design Questions for the full
      trade-off writeup; this flow's `res_simbox_core` inherits whichever
      answer is chosen there.

## Testing Strategy

The Plan adds tests before v1.2 transfer/refactoring wherever the legacy
seams permit it. Stable legacy behavior is the oracle.

Minimum automated matrix:

1. provenance assertions showing each extracted reader/hub operation
   originates in the matching legacy body and has one shared definition;
2. host-side tests using mock/injected TTY and USB boundaries for argument
   translation, result propagation, and cleanup without physical devices;
3. standalone-adapter tests for both reader modes and hub list/power/LED;
4. Asterisk-adapter tests using available Asterisk 11 headers/stubs for
   load/unload, CLI registration, cleanup, and operation without core;
5. registry tests for both load orders, duplicate registration, ABI
   mismatch, either unload order, and callback/unload races;
6. build/link assertions that both artifacts use the common objects,
   standalone binaries have no Asterisk dependency, and public symbols
   have exactly one definition;
7. lock tests proving two owners of one synthetic device cannot proceed
   while different devices remain independent.

Real Asterisk and USB/TTY integration remains deferred to a compatible
Linux host. It must cover both binaries, each `.so` without core, each
`.so` registered with core, and core with both absent.

## Copyright & Licensing (added 2026-08-26)

Each of the five module directories now has its own `LICENSE` file
(NativeMindNONC agreement, copied from `libsCpp/asterisk-chan-svistok/LICENSE`
with the copyright-holder placeholder filled in):
`libsCpp/asterisk-res-simbox-core/LICENSE`,
`libsCpp/asterisk-res-simbox-discovery/LICENSE`,
`libsCpp/asterisk-res-simbox-programmator/LICENSE`,
`libsCpp/asterisk-res-simbox-reader/LICENSE`,
`libsCpp/asterisk-res-simbox-hub/LICENSE` — all identical content:
copyright holder `Anton Dodonov (NativeMind)`, `2014-2026`, plus
`https://github.com/Anton-Dodonov`, `http://linkedin.com/in/anton-dodonov/`,
`anton.v.dodonov@gmail.com`. The same placeholder was also fixed in the
sibling `libsCpp/asterisk-chan-svistok/LICENSE` and
`libsCpp/asterisk-chan-simbox/LICENSE` (same template, same bug).

**Resolved 2026-08-26**: the source-file copyright headers in
`libsCpp/asterisk-chan-svistok/src/*.c`/`.h` (the sibling flow's output)
were replaced entirely with the NativeMind copyright block, **except**
`chan_dongle.c`/`chan_dongle.h`, which keep the original upstream `bg
<bg_one@mail.ru>` notice untouched — per user's explicit rule: chan_dongle
itself is bg111's authorship, everything else in that tree is Anton
Dodonov's. **This same rule is now a standing constraint for this flow's
own Plan/Implementation phases**: when this flow creates/carries source
files into the five module directories, every new/carried file gets the
NativeMind copyright header — **except** `hub-ctrl.c` (vendored
third-party USB tool, going into `res_simbox_hub`), whose original
copyright must be preserved unchanged ("вендорное решение, там copyright
не меняй").

---

## Approval

- [x] Version 1.1 reviewed by: Anton
- [x] Version 1.1 approved on: 2026-08-26
- [x] Version 1.1 notes: see `01-requirements.md`'s Approval notes — open questions
      carried to Plan phase.
- [x] Version 1.2 reviewed by: Anton
- [x] Version 1.2 approved on: 2026-08-26
- [x] Version 1.2 notes: shared implementations, two delivery forms,
      optional core registration, and option-A lifecycle approved.
