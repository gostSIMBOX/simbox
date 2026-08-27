# Requirements: res-simbox (module split)

> Version: 1.2
> Status: DRAFT
> Last Updated: 2026-08-26

> **Moved from**: `flows/asterisk-chan-svistok/sdd-asterisk-chan-svistok-chan-dongle/01-requirements.md`
> ("Version 1.1 Revision: Three-Module Split" section), per explicit user
> request to give this decision its own dedicated flow. That flow retains
> the base file/function classification work (which legacy code is
> new/modified/unmodified relative to upstream `chan_dongle`); this flow
> owns everything about *how that classified code is packaged into three
> Asterisk modules*.

## Problem Statement

The sibling flow `sdd-asterisk-chan-svistok-chan-dongle` produced a
complete, independent classification of `legacy/asterisk-chan-svistok-v2014`
against upstream `chan_dongle` (bg111), and an initial plan to land all
new/modified code in one flat `src/` tree for a single `chan_svistok.so`
successor module.

Having seen that inventory, the user asked whether the result should
instead be split into three separate Asterisk modules along boundaries the
inventory already surfaced: a core channel driver, a device-discovery
daemon (`simnode/`, today a standalone binary), and a firmware-flashing
subsystem (`programmator/`, today split between a standalone binary and a
slice linked into the channel driver's CLI).

## Decisions (elicited via clarifying questions, 2026-08-26)

1. **`res_simbox_core`** is the channel driver itself (chan_dongle-derived
   channel technology, config, pvt/device state, AT-command handling, and
   whatever CLI/manager actions stay in core) — **not** a new shared
   library that the other two modules depend on. It is the direct
   successor of what `chan_dongle.so` is today, renamed/repackaged as its
   own module. **It must load and run standalone, from its own config,
   with no other `res_simbox_*` module loaded.** (User's own words: "chan_svistok
   должен иметь возможность запускаться самостоятельно и работать с
   конфигом, без запуска res_.")
2. **`res_simbox_discovery`** and **`res_simbox_programmator`** become
   genuine, independently loadable Asterisk modules — their own
   `AST_MODULE_INFO`, load/unload lifecycle — not just reorganized
   standalone binaries as they are today.
3. The `cli_changeimei`, `cli_diagmode`, `cli_dongle_update` CLI commands
   (today part of core's `cli.c`) move into `res_simbox_programmator`,
   which registers them itself, rather than staying in core and calling
   out.
4. Target module directories (given explicitly by the user):
   - `libsCpp/asterisk-res-simbox-core/`
   - `libsCpp/asterisk-res-simbox-discovery/`
   - `libsCpp/asterisk-res-simbox-programmator/`
   - `libsCpp/asterisk-res-simbox-reader/` (added v1.1, see below)
   - `libsCpp/asterisk-res-simbox-hub/` (added v1.1, see below)
   (all exist on disk already, empty, as of 2026-08-26.)

## Version 1.1 Revision: `res_simbox_reader` and `res_simbox_hub`

**2026-08-26** — the user resolved two items that v1.0 had left as
"uncertain-status, not clearly any of the three modules" (`reader/` and
`hub-ctrl.c`, see the source flow's specifications), by explicitly
carving out two more modules:

- **`res_simbox_reader`** — the `reader/` subsystem (SIM smart-card reader/
  emulator: `reader_core.c`/`.h`, `adapter.c`, `emulator.c`). Previously
  flagged as "no build-script or module reference found anywhere,
  status/usage unconfirmed" — the user's decision resolves that
  ambiguity by promoting it to its own module regardless, following the
  same pattern as `res_simbox_discovery` (a legacy standalone/dormant tool
  becoming a real Asterisk module).
- **`res_simbox_hub`** — `hub-ctrl.c` (the vendored third-party USB hub power-
  control tool) "и работа с хабами" (and hub-related work). Grep across
  the full legacy tree found `hub-ctrl.c` has **zero code coupling** with
  any other legacy file — it's referenced only by `upgrade.sh`/
  `upgrade_prog.sh` as an ad-hoc `gcc hub-ctrl.c -lusb -o hub-ctrl` build
  step, never called from `chan_dongle.c` or any other module source.
  "Работа с хабами" (hub-handling work) in the legacy tree is entirely
  contained in this one file; there is no other hub-power logic
  elsewhere to also carve out.

Both follow the same target shape already established for
`res_simbox_discovery`/`res_simbox_programmator`: real, independently
loadable Asterisk modules with their own `AST_MODULE_INFO`/load-unload
lifecycle, built by relocating existing legacy `main()`-based logic rather
than rewriting it (same "restructure only" constraint as the rest of this
flow).

### New Acceptance Criteria (v1.1)

5. **Given** `reader/reader_core.c`, `reader/adapter.c`, `reader/emulator.c`
   **When** turned into `res_simbox_reader`
   **Then** the module gains a proper `AST_MODULE_INFO`/load-unload
   lifecycle instead of the current hand-rolled, dual-entry-point
   (`adapter` vs `emulator`) standalone binaries, reusing the existing
   legacy logic rather than rewriting it. `reader/old/` (nested stale
   duplicates) stays excluded, as already established.

6. **Given** `hub-ctrl.c`
   **When** turned into `res_simbox_hub`
   **Then** it becomes its own module, independent of
   `res_simbox_programmator` (the placement tentatively proposed in the
   source flow's v1.0 specs is superseded by this decision).

### New Open Questions (v1.1)

- [ ] `res_simbox_reader` currently has **two** legacy entry points over the same
      core (`adapter.c` = pass-through to real reader hardware,
      `emulator.c` = simulated reader for testing, both `#include
      "reader_core.c"`) — does the module need to support both modes
      simultaneously (e.g. config-selected), or is only one actually
      still needed?
- [ ] Does `res_simbox_hub` need real Asterisk module lifecycle/CLI integration
      at all, or is it simpler to keep it as the standalone `gcc`-built
      utility it already is today, just relocated under
      `libsCpp/asterisk-res-simbox-hub/`? Unlike every other module in this
      flow, it has no discovered coupling to `pvt`/channel state or any
      other legacy file — it may not need to be "in Asterisk" the way the
      others do. Flagging rather than assuming "make it a module" is
      right just because the other two were.

## Version 1.2 Revision: Three Runtime Modes for Reader and Hub

**2026-08-26** — the user expanded the required runtime shape of
`res-simbox-reader` and `res-simbox-hub`. Each component must support all
three modes below; choosing one mode must not remove either of the other
two:

1. **Standalone binary** — executable without an Asterisk process and
   without `res_simbox_core`.
2. **Independent Asterisk module** — independently loadable/unloadable
   `.so` with its own Asterisk module lifecycle, usable while
   `res_simbox_core` is absent or unloaded.
3. **Core-managed Asterisk module** — while loaded together with
   `res_simbox_core`, the component can operate under the core module's
   coordination rather than as an unrelated peer.

The user selected management option **A**: Asterisk remains responsible
for loading and unloading `res_simbox_reader.so` and
`res_simbox_hub.so`. When core and a child module are both loaded, the
child registers its capability with `res_simbox_core`, and core
coordinates its operation through that explicit interface. Core must not
load/unload the child module itself.

The required Asterisk artifacts are `res_simbox_reader.so` and
`res_simbox_hub.so`. Names of the standalone executable targets are a
build-level decision to be fixed in Specifications; retaining compatible
legacy names may be required for deployment scripts.

The standalone executable and Asterisk module for a component must reuse
the same underlying legacy implementation. Their entry points and
lifecycle adapters may differ, but the hardware/protocol behavior must
not be maintained as two divergent copies.

Standalone executables are optional deliverables for end users who need
reader or hub functionality outside Asterisk. They are not child
processes of `res_simbox_core`: core must neither start, stop, monitor,
nor otherwise supervise them.

"Core-managed" is not permission for duplicate initialization or
simultaneous, uncoordinated ownership of the same reader or hub. The
eventual design must define one owner for each physical resource and
produce a deterministic refusal or handover when another runtime mode
already owns it.

`res_simbox_core` remains independently usable: reader and hub are
optional capabilities, and their absence or failure to load must not
prevent core from loading and providing its own functionality.

### User Stories (v1.2)

**As an operator outside Asterisk**
**I want** reader and hub functionality to remain available as standalone
executables
**So that** diagnostics, maintenance, and deployments that do not run
Asterisk do not depend on it.

**As an Asterisk administrator**
**I want** `res_simbox_reader.so` and `res_simbox_hub.so` to load and work
independently
**So that** either capability can be deployed without
`res_simbox_core`.

**As a simbox operator**
**I want** the same modules to work under `res_simbox_core` coordination
when core is present
**So that** the complete system has one control plane and a consistent
lifecycle without sacrificing independent use.

### Acceptance Criteria (v1.2)

7. **Given** Asterisk and `res_simbox_core` are not running
   **When** the reader standalone executable is started
   **Then** it exposes the applicable legacy reader functionality without
   requiring either of them.

8. **Given** Asterisk and `res_simbox_core` are not running
   **When** the hub standalone executable is started
   **Then** it exposes the applicable legacy hub functionality without
   requiring either of them.

9. **Given** Asterisk is running and `res_simbox_core` is absent/unloaded
   **When** `res_simbox_reader.so` is loaded, used, reloaded where
   supported, and unloaded
   **Then** its reader lifecycle and operations work independently and
   clean up owned resources on unload.

10. **Given** Asterisk is running and `res_simbox_core` is absent/unloaded
    **When** `res_simbox_hub.so` is loaded, used, reloaded where supported,
    and unloaded
    **Then** its hub lifecycle and operations work independently and
    clean up owned resources on unload.

11. **Given** `res_simbox_core` and either child module are both loaded
    **When** managed operation is activated
    **Then** core and the child use an explicit coordination contract,
    the child remains independently unloadable, and no physical resource
    is initialized or controlled twice.

12. **Given** reader or hub is absent, fails, or is unloaded
    **When** `res_simbox_core` loads or continues running
    **Then** core remains operational and reports the optional capability
    as unavailable instead of acquiring a hard load-time dependency.

13. **Given** both delivery forms of one component
    **When** their source composition is audited
    **Then** the standalone executable and Asterisk module share the same
    copied legacy business implementation; only entry-point, lifecycle,
    and explicitly approved coordination glue may be mode-specific.

### Resolved Question (v1.2)

- [x] **Core-management boundary** — option **A**, confirmed by the user
      on 2026-08-26. Asterisk loads/unloads the modules; core coordinates
      already-loaded modules through registration. Standalone binaries
      are end-user tools and are never supervised by core.

## Hard Constraint

**"Файлы НЕЛЬЗЯ ДОПИСЫВАТЬ, НЕЛЬЗЯ СОЗДАВАТЬ, можно только
реструктурировать"** ("files cannot be appended to, cannot be created,
only restructured") — restated explicitly by the user for this revision.
No new business logic may be authored; this is a reorganization/move of
existing legacy code only, same discipline as the source flow (copy-then-
trim, never retype, never invent).

The unavoidable minimum of new glue a real 3-module split requires (each
new module needs its own `AST_MODULE_INFO` block, and *some* way for core
to reach a loaded `res_simbox_programmator` for the one concrete coupling
found so far — see Open Questions) should be minimized and, where
possible, adapted from patterns `chan_dongle.c` already uses for its own
module registration, rather than invented from scratch.

## User Stories

**As a** system operator
**I want** `res_simbox_core` to load and fully operate (calls, SMS, USSD,
device management) with only its own config, whether or not
`res_simbox_discovery` or `res_simbox_programmator` are installed/loaded
**So that** the discovery daemon and the firmware-flashing tooling are
optional add-ons, not hard dependencies of basic telephony.

**As a** maintainer
**I want** `res_simbox_discovery` and `res_simbox_programmator` to be real
Asterisk-loaded modules (not external binaries invoked via shell/exec as
today)
**So that** they're managed the same way as every other Asterisk module
(load/unload, `module show`, config reload) instead of ad-hoc processes.

**As a** maintainer
**I want** the firmware-flashing CLI commands
(`dongle changeimei|diagmode|update`) to live in `res_simbox_programmator`
**So that** core's `cli.c` doesn't carry flashing-protocol code it doesn't
otherwise need.

## Acceptance Criteria

1. **Given** `res_simbox_core` is loaded with `res_simbox_discovery` and
   `res_simbox_programmator` both absent/unloaded
   **When** Asterisk starts and the module registers
   **Then** all core channel functionality (calls, SMS, USSD, CLI device
   commands other than the three flashing ones) works exactly as before,
   with no load-time dependency on the other two modules.

2. **Given** the three-module split
   **When** classifying `cli_changeimei`, `cli_diagmode`,
   `cli_dongle_update`
   **Then** they are registered by `res_simbox_programmator`, not by core's
   `cli.c`.

3. **Given** `simnode/adiscovery_core.c` and its three legacy entry points
   (`adiscovery_svistok.c`, `adiscovery_simnode.c`, `adiscovery_test.c`)
   **When** turned into `res_simbox_discovery`
   **Then** the module gains a proper `AST_MODULE_INFO`/load-unload
   lifecycle instead of a hand-rolled `main()`, reusing the existing
   legacy logic rather than rewriting it.

4. **Given** the source flow's independent file/function classification
   (NEW / MODIFIED / UNCHANGED / REMOVED, ~380 functions across 17 module
   files, plus the full legacy-tree inventory)
   **When** producing this flow's module layout
   **Then** every already-classified file/function is assigned to exactly
   one of the three modules (or explicitly excluded, per the source
   flow's dead-code/junk/stale findings) — this flow re-partitions, it
   does not reclassify.

## Constraints

- **Copyright/licensing (added 2026-08-26)**: every one of the five module
  directories gets its own `LICENSE` file (NativeMindNONC agreement,
  identical text to `libsCpp/asterisk-chan-svistok/LICENSE`) with the
  copyright holder filled in as: `Anton Dodonov (NativeMind)`, `2014-2026`,
  `https://github.com/Anton-Dodonov`, `http://linkedin.com/in/anton-dodonov/`,
  `anton.v.dodonov@gmail.com`. Already done for all five
  `libsCpp/asterisk-res-simbox-*/LICENSE` files (previously had an unfilled
  `Copyright Holder: Software Development Company` placeholder — same
  placeholder was also found and fixed in the sibling
  `libsCpp/asterisk-chan-svistok/LICENSE` and
  `libsCpp/asterisk-chan-simbox/LICENSE`, since they're the same template).
  Any new source file created during this flow's Plan/Implementation
  phases must carry a matching copyright header comment.
- **No new code**: this flow only moves/reorganizes already-classified
  legacy code (see Hard Constraint above). Any new glue code a real module
  boundary requires must be flagged explicitly as an open question, not
  decided or written silently.
- **Core independence**: `res_simbox_core` must build and load without
  `res_simbox_discovery` or `res_simbox_programmator` present.
- **Depends on**: the source flow's file/function classification
  (`flows/asterisk-chan-svistok/sdd-asterisk-chan-svistok-chan-dongle/02-specifications.md`)
  is the ground truth for *what* code exists and its NEW/MODIFIED/
  UNCHANGED status; this flow does not redo that classification.

## Won't Have (This Iteration)

- Redoing or second-guessing the underlying file/function classification
  (owned by the source flow).
- Runtime/hardware verification (compiling and running against a real
  Asterisk + modem) — no compatible environment available.
- Inventing new inter-module APIs/business logic to fully resolve the
  `pvt_start()` coupling (see Open Questions) — options are documented,
  none chosen yet.
- Treating a standalone reader/hub process and its Asterisk module as
  simultaneous owners of the same physical device.

## Open Questions

- [ ] **`pvt_start()` cross-module call**: core's `chan_dongle.c:pvt_start()`
      calls `ttyprog_set_diagmode()`/`ttyprog_changeimei()` directly —
      functions that now live in `res_simbox_programmator`. This is the
      one concrete conflict with "core loads standalone." Three options
      on the table (Asterisk module-check guard; move the triggering
      logic into programmator; weak-symbol/dlsym lookup) — see
      `02-specifications.md`'s Open Design Questions for the full
      writeup. Not resolved yet.
- [ ] Does `res_simbox_discovery` replace the standalone `simnode` daemon
      entirely (nothing left running outside Asterisk), or does it
      coexist with a still-standalone build target for non-Asterisk
      deployments?
- [ ] Minimum viable inter-module mechanism for core to reach
      `res_simbox_programmator` beyond the `pvt_start()` case, if any —
      working assumption is to reuse `chan_dongle.c`'s own existing
      `load_module`/`unload_module`/`self_module` scaffolding as the
      template for the two new modules' registration boilerplate, since
      copying existing legacy code is "restructuring," not "creating."
      Not yet confirmed.
- [ ] Placement of `hub-ctrl.c` (vendored third-party USB power-control
      tool) and status of `reader/` (SIM reader/emulator, no build-script
      or module reference found) — neither clearly belongs to any of the
      three modules. See `02-specifications.md`.

## References

- `flows/asterisk-chan-svistok/sdd-asterisk-chan-svistok-chan-dongle/` —
  source flow; owns the file/function classification this flow builds on.
- `libsCpp/asterisk-res-simbox-core/`, `libsCpp/asterisk-res-simbox-discovery/`,
  `libsCpp/asterisk-res-simbox-programmator/` — target module directories
  (empty as of flow creation).
- `legacy/asterisk-chan-svistok-v2014/` — read-only legacy source.
- `libsCpp/asterisk-chan-svistok/asterisk-chan-dongle/` — upstream
  reference used by the source flow's classification.

---

## Approval

- [x] Version 1.1 reviewed by: Anton
- [x] Version 1.1 approved on: 2026-08-26
- [x] Version 1.1 notes: approved with the remaining Open Questions (pvt_start()
      coupling; res_simbox_reader adapter-vs-emulator scope;
      res_simbox_hub module-or-standalone) carried forward to be resolved
      during Plan phase, not blocking approval.
- [x] Version 1.2 reviewed by: Anton
- [x] Version 1.2 approved on: 2026-08-26
- [x] Version 1.2 notes: management scope resolved as option A;
      standalone binaries are optional tools for end users and are not
      supervised by core.
