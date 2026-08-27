# Implementation Log: res-simbox (module split)

> Started: 2026-08-26
> Plan: [03-plan.md](03-plan.md)

## Progress Tracker

| Task | Status | Notes |
|------|--------|-------|
| 0.1 Wrapper mechanism | Done | Direct link chosen, recorded |
| 0.2 pvt_start() coupling | Done | ast_module_check() guard chosen, recorded |
| 0.3 Reader scope | Done | Keep both adapter+emulator, config-selected |
| 0.4 Hub module-or-not | Done | Standalone tool, not an Asterisk module |
| 0.5 Dead code disposition | Done | dsp.c, share_mysql.c/.h, adiscovery_core_new.c, adiscovery_simnode.c excluded everywhere |
| 0.6 Build system shape | Done | Mirror core's autotools shape per module |
| 1.1/1.2 Core: trim 27 + create 10 companions | Done with approved deviation | Whole-file carries; details below |
| 1.3 Core: already-separated files | Done | |
| 1.4 Core: pvt_start() guard applied | Done | |
| 1.5 Core: build files | Done | |
| 1.6 Core: no-copy verification | Done | |
| 2.x Discovery | Done | |
| 3.x Programmator | Done | |
| 4.x Reader | Superseded by v1.2 | Now binary + independent/managed module |
| 5.x Hub | Superseded by v1.2 | Now binary + independent/managed module |
| 6.x Cross-cutting | Done | |
| 7.x v1.2 tests first | Done | 5 baseline tests before transfer |
| 8.x shared reader/hub + binaries | Done | Golden behavior retained |
| 9.x core registry | Done | Optional API, no lifecycle ownership |
| 10.x Asterisk adapters | Done structurally | Real Asterisk runtime deferred |
| 11.x build/deploy/audit | Done structurally | 17 tests pass; real host deferred |

## Session Log

### Session 2026-08-26 — Claude

**Started at**: Phase 0
**Context**: Plan approved same session; beginning Implementation immediately.

#### Completed

- **Task 0.1 (wrapper mechanism)**: Confirmed as-planned — direct link.
  `res_simbox_core`'s carried files will not redefine `UNCHANGED`
  functions; the module's build links against
  `asterisk-chan-dongle`'s compiled objects for those symbols. No wrapper
  `.c` files created.
- **Task 0.2 (`pvt_start()` coupling)**: Confirmed as-planned —
  `ast_module_check("res_simbox_programmator.so")` guard, applied in
  Task 1.4 once `chan_dongle.c` is carried.
- **Task 0.3 (reader scope)**: Confirmed as-planned — both `adapter.c`
  and `emulator.c` kept; config-selected at load, applied in Task 4.2.
- **Task 0.4 (hub module-or-not)**: Confirmed as-planned —
  `res_simbox_hub` stays a standalone utility (own build rule producing a
  plain `hub-ctrl` binary), not an `AST_MODULE_INFO` Asterisk module.
- **Task 0.5 (dead code)**: Confirmed as-planned — `dsp.c`,
  `share_mysql.c`/`.h`, `adiscovery_core_new.c`, `adiscovery_simnode.c`
  excluded from all five modules.
- **Task 0.6 (build shape)**: Confirmed as-planned — each module's build
  file mirrors `res_simbox_core`'s carried `configure.in`/`Makefile.in`
  autotools shape, with its own `_OBJS`/`SOURCES` list.

**Ended at**: Phase 0 complete, starting Phase 1, **blocked partway through
Task 1.1**
**Handoff notes**: see "Critical Discovery" below — do not resume Task 1.1
by just re-running the mechanical trim script; the mechanism itself needs
a decision first.

#### Critical Discovery — Task 0.1's "direct link" mechanism doesn't work for most of this codebase

Built an automated copy-then-trim script and ran it on `app.c` as a first
test (smallest file, 1 `MODIFIED` function, 3 `UNCHANGED`). It correctly
kept `app_status_exec` and deleted the other three functions' bodies —
but the surviving static table `dca[]` still references
`app_send_sms_exec` by name, and `app_send_sms_exec` is declared `static`
in legacy. **A `static` function has internal linkage — it can only be
called from within its own translation unit.** Deleting its body and
relying on "direct link against `asterisk-chan-dongle`'s compiled object"
(Task 0.1's chosen mechanism) cannot work for it: the linker has no way to
resolve a call to a `static` symbol defined in a different `.o`.

Wrote a second script to check, across all 16 module `.c` files, how many
`UNCHANGED` functions are both (a) `static` in legacy and (b) referenced
somewhere else in the same file (by a surviving `MODIFIED` function, by
another `UNCHANGED` function, or by file-scope data like `app.c`'s `dca[]`
table). Result: **this is not a small edge case — it's most of the
codebase.** Representative counts of affected functions per file:
`cli.c` 16, `pdiscovery.c` 27, `manager.c` 12, `chan_dongle.c` 8,
`channel.c` 7, `at_response.c` 8, `at_queue.c` 5, `pdu.c` 7, `at_parse.c`
3, `at_command.c` 1, `cpvt.c` 1, `app.c` 1. Only `at_read.c`, `dc_config.c`,
`helpers.c`, `ringbuffer.c` are "clean" (no internally-referenced statics
among their `UNCHANGED` functions). Files like `pdiscovery.c` turn out to
be built around one large, tightly-coupled internal `static` subsystem
(a device-info cache) where nearly every "unchanged" function calls
several other "unchanged" functions — there's no way to delete any of
them without either deleting the whole cluster together or breaking the
build.

**This means Task 0.1's decision (direct link, no wrapper code) needs to
be revisited before Task 1.1 can proceed safely** — pushing forward
mechanically would either silently produce non-compiling module sources,
or require promoting on the order of 100 `static` functions across the
upstream `asterisk-chan-dongle` reference copy to external linkage (a much
bigger intervention on upstream than "expose symbols for the proxy
calls" implied). Stopping here rather than picking a fix unilaterally —
see chat for the options being presented to the user.

**Cleanup**: the one file processed before this was caught
(`libsCpp/asterisk-res-simbox-core/src/app.c`) is left in place as a
concrete worked example of the problem, **not** as completed work — it
would not compile as-is. Task 1.1 remains `pending`, not `in_progress`,
until the mechanism question is resolved.

---

### Session 2026-08-26 (continued) — Claude

**Resolution from user**: "Перенеси все что нужно внутрь res_simbox_*
простым mv. Основная идея разделить от кода bg111, написанным другим
разработчиком" (move whatever's needed into `res_simbox_*` with a simple
`mv`; the real goal is separating from bg111's code, written by a
different developer).

**Deviation from 03-plan.md, recorded**: this reframes the goal away from
"minimize duplication via function-level surgery" toward "separate
Svistok-touched files from untouched-upstream files, simply." Consequence:
Tasks 1.1 and 1.2 (per-function trim + 10 companion files) are **replaced**
by a single whole-file-copy operation. Any of the 27→28 module files that
contain even one `MODIFIED`/`NEW` function (which, per the source flow's
classification, is all of them) is copied **in full** into
`libsCpp/asterisk-res-simbox-core/src/` — `MODIFIED`, `NEW`, and
`UNCHANGED` functions alike stay physically together in their original
file, exactly as legacy has them. This sidesteps the static-linkage
problem entirely (nothing is deleted, so no internal reference can break)
and is a much smaller, safer change than either promoting ~100 legacy
`static` functions to external linkage or hand-verifying every
`static`-but-safe-to-delete case individually.

**Copyright consequence**: since these 28 files now carry a genuine
*mix* of bg111's original code and Svistok's modifications (not a clean
Svistok-only extraction like the sibling flow's output), they get the
**same treatment as `chan_dongle.c`/`.h`** — original legacy copyright
kept, untouched, not replaced with NativeMind's. Only files with **zero**
upstream content (no bg111 authorship at all) get the NativeMind header.
This is an extension of the user's own stated principle
("chan_dongle остаётся bg111's, там его код") to every file in this
whole-file-copy set, not a new rule invented independently — flagging
here in case that extension isn't what was intended.

#### Completed

- **Task 1.1+1.2 (merged, revised)**: Copied all 28 files verbatim —
  `app.c/.h`, `at_command.c/.h`, `at_parse.c/.h`, `at_queue.c`, `at_read.c`,
  `at_response.c/.h`, `chan_dongle.c/.h`, `channel.c/.h`, `cli.c/.h`,
  `cpvt.c/.h`, `dc_config.c/.h`, `helpers.c`, `manager.c`, `pdiscovery.c/.h`,
  `pdu.c/.h`, `ringbuffer.c/.h` — into
  `libsCpp/asterisk-res-simbox-core/src/`. Verified byte-identical to
  legacy source for every file. Copyright headers untouched (legacy
  bg111/Artem Makhutov/Dmitry Vagin originals kept, per the deviation
  above). No companion files created (criterion 5's "new functions in
  dedicated files" is satisfied only at the level of files that already
  have zero upstream content, not by further splitting these 28 — logged
  as a scope reduction from the approved specs, not silently dropped).
- **Task 1.3**: Copied `select.c`, `select.h`, `dserial.c`, `limits.c`,
  `share.c`, `share.h`, `stat.c` verbatim (these have **zero** upstream
  content — 100% Svistok-original) with the NativeMind copyright header
  prepended. Verified content matches legacy exactly after the header.
- **Task 1.4**: Applied the `ast_module_check("res_simbox_programmator.so")`
  guard (Task 0.2's decision) around both the `diagmode` and `changeimei`
  blocks in the carried `chan_dongle.c`'s `pvt_start()`. Added an inline
  comment flagging that this assumes Asterisk's module loader uses lazy
  symbol binding (so an unresolved `ttyprog_set_diagmode`/
  `ttyprog_changeimei` reference doesn't itself block `res_simbox_core`
  from loading when `res_simbox_programmator` is absent) — **unverified,
  no Asterisk build/runtime available**, same T3/T4-style deferral this
  whole flow family has used throughout.
- **Task 1.5**: Carried `configure.in`, `Makefile.in`, `config.h.in`
  verbatim. `single.c` also carried **as-is, unmodified** (not
  regenerated as the plan assumed) — since the whole-file-copy strategy
  kept the exact same 19-file set `single.c` already expects, its
  `#include` list needed no changes.
  - **Discovered inconsistency, not fixed here**: `single.c`'s
    `#include`s assume `char_conv.c`, `memmem.c`, `mixbuffer.c` exist
    physically alongside it — but those are exactly the files Task 1.6
    deliberately does *not* copy (100%-identical-to-upstream, resolved by
    direct link instead). `single.c` (the alternate all-in-one-translation-
    unit build mode) is therefore **inconsistent with the direct-link
    strategy** as currently laid out; it would only build if those three
    files were also physically present. Not resolved — `single.c` is a
    legacy alternate build mode, not the primary one
    (`chan_donglem_so_OBJS`), so this doesn't block the main build path,
    but noting it rather than silently shipping a build mode that doesn't
    actually work.
- **Task 1.6**: Verified none of the 18 IDENTICAL-to-upstream files
  (`at_queue.h`, `at_read.h`, `BUGS`, `char_conv.c/.h`, `COPYRIGHT.txt`,
  `export.h`, `helpers.h`, `INSTALL`, `LICENSE.txt`, `manager.h`,
  `memmem.c/.h`, `mixbuffer.c/.h`, `mutils.h`, `stamp-h.in`, `TODO.txt`)
  were copied into `src/`.

**Ended at**: Phase 1 complete (36 files total in
`libsCpp/asterisk-res-simbox-core/src/`: 28 whole-file carries + 7
Svistok-original + `single.c`), moving to Phase 2.
**Handoff notes**: Phases 2-5 were always planned as simple copy-as-is
operations (no upstream counterpart to trim against for any of those
files), so the static-linkage problem that hit Phase 1 doesn't apply
there — proceeding as originally planned.

#### Discovery affecting Phase 2 — `adiscovery_svistok.c` is core content, not discovery-daemon content

While copying `simnode/`'s three files for Phase 2, found that
`chan_dongle.c:73` has `#include "simnode/adiscovery_svistok.c"` — a
textual composition the source flow's specs (02-specifications.md's "Key
Discovery" section) **missed** when it enumerated `select.c`/`dserial.c`/
`limits.c`/`share.c`/`stat.c`/`programmator/ttyprog_svistok.c` as the
files fused into `chan_dongle.so` this way. `adiscovery_svistok.c` defines
`pvt_adiscovery()` (a `static` function), which `chan_dongle.c`'s
`pvt_start()` calls **unconditionally** near the top of the device-connect
path (`r=pvt_adiscovery(pvt); if (!r) return;`) — not gated behind a flag
the way the programmator coupling was. This is load-bearing core logic,
not a discovery daemon.

**Correction applied**: moved `adiscovery_svistok.c` out of
`res_simbox_discovery` and into
`libsCpp/asterisk-res-simbox-core/src/simnode/adiscovery_svistok.c`
(matching the exact relative path `chan_dongle.c`'s `#include` already
expects — no path rewrite needed). Also copied `adiscovery_core.c`
(the shared device-enumeration logic `adiscovery_svistok.c` itself
`#include`s) into `res_simbox_core/src/simnode/` alongside it.
`res_simbox_discovery` keeps its **own** copy of `adiscovery_core.c`
(needed by `adiscovery_test.c`, the genuine standalone entry point) —
two physical copies of the same file, one per consumer, consistent with
"simple mv" over trying to share one physical file across two separate
modules.

**Second discovery, changes res_simbox_discovery's nature**:
`adiscovery_test.c` (the file that's actually left in
`res_simbox_discovery` after the correction above) is a genuine
standalone Unix polling daemon — `while(1) { sleep(1); ...poll USB
devices...; log to /var/svistok/lists/*.list; }` — using plain
`printf`/`FILE*` I/O, **zero** Asterisk API calls (no `ast_verb`,
no `ast_module_register`, nothing). Forcing an `AST_MODULE_INFO`/
load-unload lifecycle onto it (as Requirements v1.1 decision #2 and Plan
Task 2.2 assumed) would mean inventing Asterisk integration code that
never existed in legacy — in tension with "restructure only, don't
invent." Given Task 0.4 already established the same precedent for
`res_hub` (zero-Asterisk-coupling code stays a standalone tool rather
than being forced into module shape), applying it here too for
consistency: **`res_simbox_discovery` is a standalone polling-daemon
binary**, not an Asterisk-loaded `.so`. This directly contradicts
Requirements v1.1's decision #2 ("`res_simbox_discovery` ... become
genuine, independently loadable Asterisk modules") — flagging clearly
rather than silently reinterpreting a decision the user explicitly made;
worth a check-in.

#### Completed (Phase 2, revised)

- Copied `adiscovery_core.c` + `adiscovery_test.c` into
  `libsCpp/asterisk-res-simbox-discovery/src/` with the NativeMind
  copyright header (100% Svistok-original, no upstream counterpart).
  Verified byte-identical to legacy after the header.
- Moved `adiscovery_svistok.c` (+ its own `adiscovery_core.c` copy) into
  `libsCpp/asterisk-res-simbox-core/src/simnode/` instead (see discovery
  above).
- Did **not** restructure `adiscovery_test.c`'s `main()` into a module
  lifecycle (Task 2.2 as originally planned) — see discovery above for
  why.
- **User overruled the standalone-binary reclassification**: asked, user
  chose "force it into a real Asterisk module anyway" — keep
  Requirements v1.1 decision #2 as originally stated, even though the
  polling logic never used Asterisk's API.
- **Task 2.2 (revised)**: wrapped `adiscovery_test.c`'s `main()` into
  `load_module()`/`unload_module()`/`AST_MODULE_INFO`, modeled on
  `chan_dongle.c`'s own pattern (same `ast_pthread_create_background`
  idiom that file already uses for its monitor thread). The polling body
  itself (`sysdevs_find`/`usbdevs_find`/the five log calls/two
  `usbdevs_filelist` calls) is **untouched** from legacy — the only
  substantive change is `while(1)` → `while(!discovery_stop_flag)` so
  `unload_module()` has a way to stop the thread, which is required
  plumbing for any module to unload cleanly, not new business logic.
  Added an inline comment explaining the restructuring and its rationale
  for future readers.
- `res_simbox_discovery`'s build file (Task 2.3): still pending — now
  builds a real `res_simbox_discovery.so` Asterisk module, not a
  standalone binary.

**Ended at**: Phase 2 content complete (build file pending), moving to
Phase 3.

---

### Session 2026-08-26 (continued 2) — Claude

#### Discovery affecting Phase 3 — core's `cli.c` also `#include`s programmator content

Before copying Phase 3, checked whether core's (already whole-file-copied)
`cli.c` has the same kind of hidden coupling `chan_dongle.c` had. It does:
`cli.c:28` has `#include "programmator/ttyprog_svistok.c"` (the same
composition the source flow's specs already knew about, just hadn't been
traced through to what it means for the *core* copy specifically), and
`cli.c:872` calls `ttyprog_changeimei()` directly — inside
`cli_changeimei()`, one of the three functions Requirements v1.1 already
said should move to `res_simbox_programmator`.

**This time the extraction was actually safe to do** (unlike Phase 1's
attempted per-function trim) — `cli_diagmode`/`cli_changeimei`/
`cli_dongle_update` were always meant to move per an explicit, approved
acceptance criterion, not an ad-hoc optimization. Checked their bodies for
static-linkage traps first (the Phase-1 lesson applied): they call
`complete_device()` (for CLI tab-completion), `find_device()` (a
`static inline` in `chan_dongle.h`, safe — gets its own copy per TU),
`readpvtinfo()`/`readpvtlimits()`/`make_dongles_imsi_list()` (all
non-static in `share.c`, safe), and `gpublic` (already `EXPORT_DECL`,
safe). Only `complete_device()` was a problem — `static` in `cli.c`.

#### Completed

- **Task 3.3's linkage fix**: promoted `complete_device()` from `static`
  to `EXPORT_DEF` in `res_simbox_core/src/cli.c`, added its declaration to
  `cli.h` with a comment explaining why (needed by
  `res_simbox_programmator`'s CLI tab-completion now that those three
  commands live elsewhere). This is the same category of fix as Task
  0.2's `pvt_start()` guard — a small, explicit, documented cross-module
  exposure, not a silent one.
- **Task 3.3**: removed `cli_diagmode`, `cli_changeimei`,
  `cli_dongle_update`'s bodies and their three `AST_CLI_DEFINE` array
  entries from `res_simbox_core/src/cli.c`; removed the now-unneeded
  `#include "programmator/ttyprog_svistok.c"` from the same file (verified
  no other function in `cli.c` references any `ttyprog_*` symbol first).
  Created `res_simbox_programmator/src/cli_programmator.c` with the three
  function bodies (verbatim from legacy), a new `cli_programmator[]`
  `AST_CLI_DEFINE` array, and its own `load_module()`/`unload_module()`/
  `AST_MODULE_INFO` using `ast_cli_register_multiple`/
  `_unregister_multiple` — a real Asterisk module, consistent with
  Requirements v1.1. This module has a one-directional build dependency
  on `res_simbox_core` (needs `chan_dongle.h`/`cli.h`/`share.h`'s
  declarations and `gpublic`'s definition) — expected and fine, since
  Requirements only constrains *core* to load without the others, not the
  reverse.
- **Task 3.1**: copied `ttyprog_svistok.c`, `ttyprog_core.c` (the live,
  longer variant), `crc.c` verbatim into
  `libsCpp/asterisk-res-simbox-programmator/src/`, NativeMind copyright
  (100% Svistok-original). Verified byte-identical to legacy after header.
- **Task 3.2**: copied `ttyprog_programmator.c`, `tty_v2.c`, `addons.c`,
  `ttyprog_test.c` the same way. Verified byte-identical.
- **Task 3.4 reconsidered, not done as originally planned**:
  `ttyprog_programmator.c` is a manual argv-based CLI tool
  (`./programmator /dev/ttyUSB5 3-1.1.1 123.bin`) invoked by a human
  operator via `prog.sh`/`upgrade_prog.sh`, not a persistent service —
  qualitatively the same kind of artifact as `hub-ctrl.c` (Task 0.4's
  precedent: stays a standalone binary, not force-wrapped into an
  Asterisk module). Did **not** apply the discovery-daemon precedent here
  since this is a different kind of tool (one-shot operator command, not
  a background service) — flagging the distinction rather than assuming
  it generalizes.
- **Not yet done**: Task 3.5 (deploy scripts), Task 3.6 (build files).

**Ended at**: Phase 3 core content complete, moving to Phase 4.

---

### Session 2026-08-26 (continued 3) — Claude

#### Completed (Phase 4)

- Verified `reader/` has zero references from core (confirms the source
  flow's specs finding) — its only cross-module dependency is its own
  `reader_core.c:2: #include "../programmator/tty_v2.c"`.
- Copied `reader_core.c`, `reader_core.h`, `adapter.c`, `emulator.c`
  verbatim (NativeMind copyright, 100% Svistok-original) into
  `libsCpp/asterisk-res-simbox-reader/src/`.
- Also copied `tty_v2.c` **locally** into `res_simbox_reader/src/`
  (verified self-contained — only standard-library includes, no core
  dependency) rather than leaving a relative `../programmator/tty_v2.c`
  include reaching into a different module's directory; re-pointed
  `reader_core.c`'s include accordingly. Diffed to confirm this is the
  *only* change from legacy.
- Copied `g.sh` (trivial two-line build script:
  `gcc emulator.c -o emu; gcc adapter.c -o ada` — confirms `adapter.c`/
  `emulator.c` are standalone tools with their own `main()`, matching
  what the source flow's specs already suspected).

#### Discovered, not resolved — flagging rather than deciding

Read `adapter.c`/`emulator.c`'s actual bodies: both are **one-shot
hardcoded hardware-test scripts** (`adapter.c` runs a fixed sequence of
APDU commands against a hardcoded `/dev/ttyUSB24` and returns;
`emulator.c` is nearly a no-op, `emu_init(dev); return;`), not persistent
polling daemons like `res_simbox_discovery`'s `adiscovery_test.c` was.
Requirements v1.1 acceptance criterion 5 says this module should get "a
proper `AST_MODULE_INFO`/load-unload lifecycle" — but it's not obvious
what that means for a one-shot diagnostic script with a hardcoded device
path: running it automatically at `load_module()` time would block
Asterisk's startup on a hardware test; more likely it should become a CLI
command (`reader test adapter`/`reader test emulator`) triggered on
demand, similar in shape to `res_simbox_programmator`'s CLI commands. Not
implemented — left as legacy `main()`-based files pending this decision,
rather than guessing.

**Ended at**: Phase 4 content mostly complete (module-wrap approach
undecided), moving to Phase 5.

---

### Session 2026-08-26 (continued 4) — Claude

#### Completed (Phase 5)

- Copied `hub-ctrl.c` verbatim into `libsCpp/asterisk-res-simbox-hub/src/`
  — byte-identical, copyright **untouched** (vendor rule, confirmed
  correct: file header is "Free Software Initiative of Japan", unrelated
  to bg111 or NativeMind).
- Re-confirmed zero coupling with any other file (grepped for
  `usbdevs_filelist`/`reader_core`/`adiscovery`/`ttyprog`/`chan_dongle`
  inside `hub-ctrl.c` — no matches).
- Build file (Task 5.2) not yet created.

**Ended at**: Phase 5 content complete, build file pending.

---

### Session 2026-08-26 (continued 5) — Claude

**User decision**: expose `res_simbox_reader`'s `adapter.c`/`emulator.c`
diagnostics as on-demand Asterisk CLI commands (mirrors
`cli_programmator.c`'s shape), not auto-run-at-load or standalone.

#### Completed

- Created `res_simbox_reader/src/reader_cli.c`: a real Asterisk module
  (`load_module`/`unload_module`/`AST_MODULE_INFO`, same
  `ast_cli_register_multiple` idiom as `cli_programmator.c`) exposing
  `reader test adapter` and `reader test emulator` CLI commands. Bodies
  are `adapter.c`'s and `emulator.c`'s exact `main()` contents, only the
  function signature changed (CLI handler instead of `main(argc,argv)`)
  and `printf`/bare-`return` replaced with `ast_cli(a->fd, ...)`/
  `CLI_SUCCESS`/`CLI_FAILURE` (the minimum needed for the code to be a
  CLI handler at all, not a behavior change).
  - Combined both diagnostics into **one** file rather than two, because
    `adapter.c` and `emulator.c` each independently `#include
    "reader_core.c"` — a third wrapper file `#include`-ing both would
    redefine every symbol in `reader_core.c` twice. `adapter.c`/
    `emulator.c` themselves are left **unchanged** in the directory as
    reference (matching how `g.sh` is kept as reference too), not deleted,
    not compiled into the module.
  - **Caught and fixed my own mistake before finalizing**: my first draft
    of the emulator handler accidentally *executed* `closetty_spec()`,
    but legacy `emulator.c` has `fd=emu_init(dev);  return;` — an
    unconditional `return` that makes the `closetty_spec()` call after it
    dead code, never actually reached. Restored that exact
    (buggy-looking but authentic) control flow with a comment explaining
    why it looks wrong but isn't a bug to silently fix — this is exactly
    the kind of unannounced behavior change the flow's copy-then-trim
    discipline exists to prevent, caught by re-reading my own diff before
    moving on rather than assuming it was right.

**Ended at**: Phase 4 fully complete. All five modules now have their
content in place; only build files and Phase 6 remain. Handed back to
user for a checkpoint; user said "continue."

---

### Session 2026-08-26 (continued 6) — Claude

#### Completed

- **Task 3.5**: copied `fuall.sh`, `fupdate3.sh`, `fupdate4.sh`,
  `updateall2.sh`, `updateall3.sh` verbatim (all pure relative-path
  scripts, e.g. `./fupdate4.sh`/`./programmator` — no hardcoded absolute
  paths needed updating, unlike the two below). Copied and fixed
  `prog.sh` (source path `programmator/ttyprog_programmator.c` →
  `ttyprog_programmator.c`, since it's now a sibling file, not a
  subdirectory of the whole legacy tree) and `upgrade_prog.sh` (same path
  fix, **plus** removed its `gcc hub-ctrl.c ...` line entirely — hub-ctrl
  now builds from the separate `res_simbox_hub` module, not from here).
  Both changes documented inline in the scripts themselves.
- **Build files (Task 1.5/2.3/3.6/4.4/5.2/0.6)**: wrote a simple,
  standalone `Makefile` for each of the five modules (not a full
  autotools regeneration of the carried legacy `configure.in`/
  `Makefile.in` — those need a real `configure` run to resolve their
  `@VAR@` substitutions, unverifiable in this environment; kept them
  as historical reference in `res_simbox_core/` only, superseded by its
  new plain `Makefile`). Each new Makefile is explicitly marked
  UNVERIFIED (no build environment available) with placeholder
  `ASTERISK_INCLUDE`/similar variables the real deployment needs to set.
  Caught and fixed one mistake while writing core's Makefile: initially
  listed `select.c`/`dserial.c`/`limits.c`/`share.c`/`stat.c`/
  `simnode/adiscovery_svistok.c` as separate `OBJS` entries, then
  remembered they're textually `#include`d into `chan_dongle.c`/
  `at_response.c`/`cli.c` (the "Key Discovery" composition) and removed
  them before finalizing — would have caused duplicate-symbol link
  errors otherwise.
  - `res_simbox_programmator`'s Makefile builds two independent targets
    (`res_simbox_programmator.so` from `cli_programmator.c`; the
    standalone `programmator` tool from `ttyprog_programmator.c`),
    matching the module's two different kinds of content. Fixed
    `cli_programmator.c`'s cross-module include paths
    (`<asterisk-res-simbox-core/chan_dongle.h>` → `<.../src/chan_dongle.h>`,
    missing the `src/` component from the first draft) to match where
    core's headers actually live.
  - `res_simbox_reader`'s Makefile compiles only `reader_cli.c`;
    `adapter.c`/`emulator.c` are explicitly excluded from the build (each
    has its own conflicting `main()`, kept as reference only per Task
    4.2's log entry).
  - `res_simbox_hub`'s Makefile mirrors legacy's own one-line ad-hoc
    build (`gcc hub-ctrl.c -lusb -o hub-ctrl`) exactly.
- **Task 6.1**: wrote `res_simbox_core/upgrade.sh`, replacing legacy's
  single flat rebuild sequence with a `make -C` loop over all five module
  directories (`$SIMBOX_ROOT` env var for the base path). Also copied
  `README.md`, `README_ru.md`, `md.sh` into `res_simbox_core/` (shared/
  core-level docs and runtime-directory bootstrap, per specs).
- **Task 6.2 (final cross-module reference audit)**: ran a consolidated
  grep pass across all five modules' `src/` for: (a) leftover
  `cli_diagmode`/`cli_changeimei`/`cli_dongle_update` references in
  core (only comments remain, correctly); (b) any other unresolved
  cross-module relative `#include`; (c) `simnode/adiscovery_svistok.c`'s
  own dependencies (confirmed self-contained: only system + `<asterisk...>`
  headers, no further hidden coupling). Also noticed
  `libsCpp/asterisk-res-simbox-core/` (and, going by the same pattern
  seen earlier in this project, presumably the other four module dirs
  too) already had a **pre-existing `.git` repo** of its own, seeded
  before this session — not something this flow created, left untouched.
  Result: **no further hidden couplings found** beyond the three already
  fixed (`pvt_start()`, `adiscovery_svistok.c`'s reassignment,
  `complete_device()`'s linkage promotion).

#### Completion Checklist

- [x] All tasks completed or explicitly deferred (build files are
      intentionally simplified vs. `03-plan.md`'s literal autotools
      wording — logged as a deviation, not silently done differently)
- [ ] Tests passing — **N/A, cannot compile/run in this environment**;
      verification throughout was structural (byte-diffs against legacy,
      manual static-linkage review), consistent with every prior flow in
      this family's T3/T4 deferral
- [x] No regressions in the sense that matters here: every kept function
      body is byte-identical to its legacy source; no `MODIFIED`/`NEW`
      content was retyped from memory anywhere
- [x] Documentation updated (this log + `_status.md`)
- [ ] Status updated to COMPLETE — not yet; see Learnings below for why
      "complete" needs one more caveat before that label is accurate

## Deviations Summary

| Planned (`03-plan.md`) | Actual | Reason |
|---|---|---|
| Task 1.1/1.2: per-function trim of core's 27-28 files + 10 companion files | Whole-file copy, no trimming, no companion files | `static` functions referenced across the file are the norm, not the exception — deleting them broke compilation; user redirected to "simple mv" |
| Task 0.1: direct link, no wrapper | Superseded by whole-file copy for core (Task 0.1 only still matters for the 18 truly-identical files, which were never copied at all) | Same reason |
| Copyright: NativeMind on all core files | bg111 original kept on all 28 mixed-authorship files; NativeMind only on 100%-Svistok-original files | Extends the user's own `chan_dongle.c`/`.h` rule consistently |
| `res_simbox_discovery` = `adiscovery_svistok.c` + `adiscovery_core.c` + `adiscovery_test.c` | `adiscovery_svistok.c` moved to `res_simbox_core` instead (it's `#include`d into `chan_dongle.c`, load-bearing) | Source flow's specs missed this composition |
| Task 2.2: restructure discovery's `main()`s into module lifecycle | Only `adiscovery_test.c` needed it (the other file was reassigned) | See above |
| Task 3.4: restructure `ttyprog_programmator.c` into module lifecycle | Left as a standalone binary, same as `hub-ctrl.c` | It's a manual operator CLI tool, not a service — same category as hub-ctrl.c, not discovery's daemon |
| Task 4.2: restructure reader's `main()`s into module lifecycle | Exposed as on-demand CLI commands instead of auto-run-at-load | User's explicit choice once it was clear these are one-shot hardcoded hardware tests, not daemons |
| Build files: mirror core's autotools shape (Task 0.6) | Simple standalone Makefiles for all 5 modules; legacy autotools files kept only as historical reference in `res_simbox_core/` | Autotools `@VAR@` substitution needs a real `configure` run this environment can't perform; a working simple Makefile is more useful than an unverifiable "faithful" one |

## Learnings

- **"Direct link, no wrapper" as a blanket policy for legacy C code with
  heavy internal `static` coupling doesn't work** — this should be
  assumed false by default for any codebase of this vintage/style unless
  proven otherwise per-file, not assumed true and discovered false by
  trial. Worth remembering for any future flow in this family that
  proposes the same mechanism.
- **Always grep the *whole* legacy tree for `#include "thisfile.c"`
  before deciding a file is a clean standalone unit** — the source flow's
  specs missed two such compositions (`chan_dongle.c`↔`simnode/
  adiscovery_svistok.c`, and the already-known `cli.c`↔`programmator/
  ttyprog_svistok.c` wasn't mis-classified but its full implication for
  *this* module split wasn't traced through until implementation).
  Classification work should include this check exhaustively, not
  file-by-file as coupling is stumbled into.
- **"Give it a module lifecycle" needs a case-by-case read of what the
  code actually does**, not a blanket rule — persistent daemons
  (`adiscovery_test.c`), CLI-triggerable one-shot logic (`cli_programmator.c`,
  `reader_cli.c`), and genuinely-standalone operator tools
  (`hub-ctrl.c`, `ttyprog_programmator.c`) all warranted different
  treatment despite all starting from a `main()`.

## Completion Checklist (repeated per template, final state)

- [x] Requirements/Specifications/Plan approved
- [x] All five modules' source content in place, verified against legacy
- [x] Build files exist for all five modules (simplified vs. plan, logged)
- [x] Copyright/licensing rule applied consistently and verified
- [ ] **Not done, explicitly out of scope for this environment**: actual
      compilation, linking, and Asterisk load-time verification of any of
      the five modules. Every "UNVERIFIED" comment left inline in the new
      module-lifecycle files and Makefiles marks exactly where this
      matters most (Task 0.2's lazy-binding assumption; the five
      Makefiles' untested paths/flags).

## Version 1.2 Implementation — 2026-08-26

### Phase 7: Legacy oracle and tests

- Added `tests/test_v12_legacy_oracle.py` without modifying `legacy/`.
- Recorded SHA-256 hashes for the five reader/hub oracle files.
- Compiled the unchanged legacy reader `main()` bodies through fake-TTY
  harnesses. Captured the adapter APDU sequence and the emulator's
  immediate-return behavior.
- Compiled unchanged vendor `hub-ctrl.c` with fake libusb. Captured list,
  power, LED, invalid-argument, and result-code behavior.
- Baseline result before extraction: **5 tests passed**.

### Phase 8: Shared implementations and binaries

- Replaced reader's reference-only `adapter.c`/`emulator.c` and duplicated
  `reader_cli.c` bodies with one callable definition each:
  `reader_adapter.c` and `reader_emulator.c`, declared by
  `reader_service.h`.
- Added `reader_main.c`; the standalone artifact is
  `res-simbox-reader {adapter|emulator} [device]` with legacy defaults.
- Found a pre-existing link blocker: the reader's copied `tty_v2.c` had
  the required legacy `writetty_all`/`readtty_all` bodies inside a block
  comment even though reader code calls them. Activated those already-
  present legacy bodies; no replacement implementation was invented.
- Refactored vendor `hub-ctrl.c:main()` into
  `res_simbox_hub_run()` and converted process `exit()` paths to returned
  status. Vendor attribution remains untouched. Added typed
  list/power/LED wrappers and a thin `hub_main.c`.
- Added OS-visible advisory locks: reader identity is its device path;
  hub identity is resolved bus/device. Lock files remain present but the
  kernel lock is released by closing the descriptor, avoiding unlink/
  inode races. Same-device cross-process contention is tested.
- Reader standalone binary built and linked successfully on this macOS
  host. Its many warnings originate in unchanged legacy reader core code
  and are recorded, not silently rewritten.

### Phase 9: Core registry

- Added versioned public component/operation contract under
  `asterisk-res-simbox-core/include/`.
- Split optional APIs into core, reader-provider, and hub-provider headers
  and translation units. This is required by Asterisk 11's
  `AST_API_MODULE` macro model: a translation unit cannot safely be both
  provider and consumer of different optional-API headers.
- Added locked core registry with ABI/kind validation, duplicate
  rejection, module references around child dispatch, status/execute,
  and detach callbacks.
- Active dispatch makes core unload return busy instead of destroying the
  registry underneath a callback.
- Integrated registry init/fini into `chan_dongle.c`; core uses
  `AST_MODFLAG_GLOBAL_SYMBOLS` and never calls `ast_load_resource()` or
  `ast_unload_resource()` for children.

### Phase 10: Independent and managed Asterisk modules

- Replaced reader's old CLI-only translation unit with
  `reader_module.c` plus `reader_provider.c`.
- Added genuine `hub_module.c` plus `hub_provider.c`.
- Both modules keep their direct CLI operations when core is absent.
- Both can attach after core or be discovered/attached when core loads
  later. Core detach clears cached callbacks, returning the child to
  independent mode. Asterisk remains the only module lifecycle owner.
- Provider modules use `AST_MODFLAG_GLOBAL_SYMBOLS`; Makefiles enable the
  Asterisk 11 weakref optional-API path.

### Phase 11: builds, deployment, and audit

- Reader Makefile now builds `res-simbox-reader` and
  `res_simbox_reader.so` from the same common objects.
- Hub Makefile now builds `res-simbox-hub`, compatible `hub-ctrl`, and
  `res_simbox_hub.so` from the same common objects.
- Added explicit `AST_MODULE` build definitions to all five module
  Makefiles; previous simple external Makefiles omitted the definition
  required by Asterisk 11's `AST_MODULE_INFO` macro.
- Updated `upgrade.sh` with opt-in artifact installation. It installs but
  never starts the end-user binaries and introduces no service/process
  supervision.
- Added reader/hub READMEs describing independent and managed modes.
- Final available test result: **17 tests passed**. Coverage includes
  immutable hashes, legacy characterization, extracted golden behavior,
  registry lifecycle/dispatch, independent-then-managed child attach,
  stub compilation of all new Asterisk/API translation units, build-graph
  assertions, forbidden lifecycle/process calls, and real cross-process
  lock contention.
- `git diff --check` passes and generated build artifacts were cleaned.

### Deferred real-host verification

This workspace still lacks compatible Linux Asterisk/libusb hardware.
The following remains mandatory before production release: build/link all
five `.so` files against the target Asterisk, load reader and hub with
core absent, test both module load orders with core, unload in both
orders, run both end-user binaries, and exercise real TTY/USB devices.
