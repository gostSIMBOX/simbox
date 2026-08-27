# Status: sdd-res-simbox

## Current Phase

IMPLEMENTATION

## Phase Status

CONTENT COMPLETE for v1.2 — reader and hub now have shared operational
implementations, standalone binaries, independent Asterisk modules, and
optional registration under `res_simbox_core`. All verification available
in this workspace passes. Production completion remains held for real
Linux/Asterisk/TTY/USB build and runtime verification.

## Last Updated

2026-08-26 by Codex

## Blockers

Compatible Linux Asterisk headers/runtime and real TTY/USB hardware are
not available in this workspace. This blocks final production build/load
verification, but not further source implementation here.

Real build/load verification still requires a Linux/Asterisk host, which
is not available in this workspace.

## Progress

- [x] Requirements v1.1 / Specifications / Plan approved
- [x] Requirements v1.2 approved
- [x] Specifications v1.2 approved
- [x] Plan v1.2 approved
- [x] Implementation v1.2 Phase 7 — legacy oracle + baseline tests
- [x] Implementation v1.2 Phase 8 — shared implementations + binaries
- [x] Implementation v1.2 Phase 9 — core registry
- [x] Implementation v1.2 Phase 10 — independent/managed Asterisk modules
- [x] Implementation v1.2 Phase 11 — builds/deployment/audit
- [x] Implementation: Phase 0 (6 decisions)
- [x] Implementation: Phase 1 `res_simbox_core` (36 content files + build
      file + upgrade.sh + docs)
- [x] Implementation: Phase 2 `res_simbox_discovery` (2 content files +
      build file, real AST_MODULE_INFO module)
- [x] Implementation: Phase 3 `res_simbox_programmator` (8 content files
      + `cli_programmator.c` + 7 deploy scripts + build file, two build
      targets: module + standalone tool)
- [x] Implementation v1.0: Phase 4 `res_simbox_reader` (former CLI-only
      module; superseded by v1.2 shared/binary/module layout)
- [x] Implementation v1.0: Phase 5 `res_simbox_hub` (former binary-only
      layout; superseded by v1.2 dual-artifact layout)
- [x] Implementation: Phase 6 (deploy script rewritten for 5-module
      layout; consolidated cross-module audit — clean, no further
      couplings found)
- [ ] Implementation complete — **held open pending real-environment
      build/load verification** (see Blockers)

## Summary of What Exists Now

| Module | Directory | Content | Build |
|---|---|---|---|
| Core | `libsCpp/asterisk-res-simbox-core/` | Existing channel driver plus versioned optional component registry/API for reader and hub | `res_simbox_core.so`; never loads children or starts binaries |
| Discovery | `libsCpp/asterisk-res-simbox-discovery/` | `adiscovery_core.c` + `adiscovery_test.c` (wrapped as a real Asterisk module) | `Makefile` |
| Programmator | `libsCpp/asterisk-res-simbox-programmator/` | Live slice (3 files) + standalone tool (4 files) + `cli_programmator.c` (new) + 7 deploy scripts | `Makefile` (two targets: `.so` + standalone `programmator` binary) |
| Reader | `libsCpp/asterisk-res-simbox-reader/` | One shared adapter/emulator implementation + standalone and Asterisk adapters + core provider + device locking | `res-simbox-reader` + `res_simbox_reader.so` |
| Hub | `libsCpp/asterisk-res-simbox-hub/` | One callable vendor implementation + standalone and Asterisk adapters + core provider + device locking | `res-simbox-hub`/`hub-ctrl` + `res_simbox_hub.so` |

All five have their own `LICENSE` (NativeMindNONC, correct copyright,
done earlier this flow).

## Major Deviations From `03-plan.md` (full detail in `04-implementation-log.md`)

1. Task 0.1/1.1/1.2 abandoned: per-function trim broke on `static`
   internal coupling (found via `app.c`); replaced with whole-file copy
   for core, per user's "simple mv" redirect. Copyright rule followed:
   bg111 original kept on all 28 mixed-authorship core files.
2. Two more `#include "file.c"` compositions found beyond what the source
   flow's specs listed: `chan_dongle.c`↔`simnode/adiscovery_svistok.c`
   (moved that file to core, not discovery) and `cli.c`↔`programmator/
   ttyprog_svistok.c` (handled correctly via the already-approved CLI
   extraction, with one linkage fix: `complete_device()` promoted from
   `static`).
3. `res_simbox_discovery`'s only real content was a zero-Asterisk-API
   polling daemon — user chose to force it into a module anyway; wrapped
   with the same `ast_pthread_create_background` idiom `chan_dongle.c`
   already uses.
4. v1.0 exposed reader only through on-demand CLI. v1.2 supersedes that
   decision: the operation bodies are shared by CLI/core dispatch and the
   new standalone `res-simbox-reader` binary.
5. `ttyprog_programmator.c` stays a standalone tool. v1.2 supersedes the
   old hub-only-binary decision: hub now builds both an end-user binary
   and `res_simbox_hub.so` from one callable vendor implementation.
6. Build files: simple standalone Makefiles for all five modules instead
   of a full autotools regeneration — the carried legacy `configure.in`/
   `Makefile.in` need a real `configure` run this environment can't
   perform. Kept as reference in `res_simbox_core/` only.

## Fork History

Not forked.

## Next Actions

1. **Real-environment verification** (whenever a Linux/Asterisk host is
   available): build all five modules via their `Makefile`s, fix
   whatever `ASTERISK_INCLUDE`/`DONGLE_INCLUDE`/etc. paths the real
   install needs, load all five into a test Asterisk instance, confirm
   `res_simbox_core` loads standalone with the other four absent (the
   core requirement this whole split was built around), then confirm it
   still works correctly with all four present.
2. Every inline `UNVERIFIED` comment left in the new module-lifecycle
   files (`chan_dongle.c`'s `pvt_start()` guard, `adiscovery_test.c`'s
   thread wrapper, both CLI modules) marks a specific thing to check
   first during that verification pass.
3. After real-host verification, record exact toolchain/Asterisk version,
   load/unload matrix, device results, and then mark the flow complete.
