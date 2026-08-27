# Specifications: asterisk-chan-svistok-chan-dongle-v2

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-08-26
> Requirements: [01-requirements.md](01-requirements.md)

## Overview

This is an **independent** classification (not reusing the tooling/manifests
from the sibling `sdd-asterisk-chan-svistok` flow) of the entire legacy tree
`legacy/asterisk-chan-svistok-v2014` (196 files) against the upstream
reference `libsCpp/asterisk-chan-svistok/asterisk-chan-dongle` (60 files,
`chan_dongle` bg111 fork). Scope is **full**: source, build system, and
everything else in the legacy tree, not just the channel-module build
closure.

**This document carries forward, unchanged, the classification work from
v1** (`flows/asterisk-chan-svistok/sdd-asterisk-chan-svistok-chan-dongle/02-specifications.md`).
What's different in v2: the "Planned `src/` File List" below reflects a
single-module `libsCpp/asterisk-chan-svistok/src` output only (no
res-simbox module split — that's a different flow's concern now), **and**
incorporates a hard technical lesson learned empirically while
implementing the (out-of-scope-here) module split against this exact
codebase: see "Static-Linkage Safety Analysis" below before assuming any
file can be safely trimmed to modified-functions-only.

Methodology: byte-for-byte comparison (`cmp`) of every file that exists in
both trees by relative path; for `.c` files that differ, a purpose-built
regex/brace-matching script (`func_diff.py`) extracted top-level function
bodies from both versions and compared them by name to classify each
legacy function as `UNCHANGED` / `MODIFIED` / `NEW`, and flagged upstream
functions absent from legacy as `REMOVED`. Two functions in `at_command.c`
(`at_fill_generic_cmd`, `at_enque_generic`) use a
`return_type __attribute__((...)) name(...)` declaration style that the
extractor's naming heuristic initially mis-labeled; their bodies were
diffed correctly, only their *names* needed manual correction below
(already fixed). No other anomalies were found on manual spot-check.

## Key Discovery: the legacy build already uses `#include "file.c"` composition

The legacy Makefile's real object list for the actual module
(`chan_donglem_so_OBJS`) is exactly the 19 upstream-shaped translation units
(`app.o at_command.o at_parse.o at_queue.o at_read.o at_response.o
chan_dongle.o channel.o char_conv.o cli.o helpers.o manager.o memmem.o
ringbuffer.o cpvt.o dc_config.o pdu.o mixbuffer.o pdiscovery.o`). Several of
the genuinely-new files are **not** separately compiled — they are pulled
into one of those 19 units via a textual `#include "sibling.c"`, a pattern
this codebase already uses in multiple places:

| Included file(s) | Included from | Status |
|---|---|---|
| `select.c` | `chan_dongle.c:1254` | **active** |
| `dserial.c`, `limits.c` | `at_response.c:27-28` | **active** |
| `share.c`, `stat.c` | `cli.c:25,27` | **active** |
| `programmator/ttyprog_svistok.c` (which itself `#include`s `programmator/ttyprog_core.c`) | `cli.c:28` | **active** |
| `simnode/adiscovery_svistok.c` (which itself `#include`s `simnode/adiscovery_core.c`) | `chan_dongle.c:73` | **active** — found late (during the out-of-scope module-split implementation), the original v1 pass here missed it; recorded now for completeness |
| `dsp.c` | `chan_dongle.c:74` — `//include "dsp.c"` | **commented out — dead code** |
| `share_mysql.c` | `cli.c:26` — `// include "share_mysql.c"` | **commented out — dead code** |

This matters for the planned `src/` layout: these files are not
independent subsystems to be linked separately — they must stay physically
next to (and be `#include`d by) their host file, the same way they do
today. This already satisfies "new functionality lives in its own file"
(acceptance criterion 4) for these particular cases.

## Static-Linkage Safety Analysis (governs which files can actually be trimmed)

**Before this analysis existed** (i.e., during v1 and the early part of
the out-of-scope module-split effort), the plan assumed every
`UNCHANGED` function could simply be deleted from a modified file's
`src/` copy, relying on the shared header's declaration to resolve the
call against `asterisk-chan-dongle`'s compiled object. **This assumption
is false for any function declared `static` in legacy that is still
referenced by surviving code in the same file** — `static` is internal
linkage; a linker cannot resolve such a call across translation units no
matter which "wrapper mechanism" is chosen (Open Design Questions below).
This was discovered empirically by actually attempting the trim on
`app.c` (the simplest candidate) and finding its surviving `dca[]`
dispatch table still referenced the deleted, `static` `app_send_sms_exec`.

A follow-up check (grep-based, all 16 module `.c` files: for each
`UNCHANGED` function, is it `static` in legacy, and is its name referenced
anywhere else in the file outside its own body?) found this is **not an
edge case** — it's the norm:

| File | Internally-referenced `static` `UNCHANGED` functions | Safe to trim? |
|---|---|---|
| app.c | 1 (`app_send_sms_exec`, via `dca[]`) | No — carry whole, or promote that one function |
| at_command.c | 1 | No |
| at_parse.c | 3 | No |
| at_queue.c | 5 | No |
| **at_read.c** | **0** | **Yes** |
| at_response.c | 8 | No |
| chan_dongle.c | 8 | No |
| channel.c | 7 | No |
| cli.c | 16 | No |
| cpvt.c | 1 | No |
| **dc_config.c** | **0** | **Yes** |
| **helpers.c** | **0** | **Yes** |
| manager.c | 12 | No |
| pdiscovery.c | 27 (one large internal cache subsystem) | No |
| pdu.c | 7 | No |
| **ringbuffer.c** | **0** | **Yes** |

Only **4 of 16** module `.c` files (`at_read.c`, `dc_config.c`,
`helpers.c`, `ringbuffer.c`) can safely have their `UNCHANGED` functions
deleted outright. The other 12 must either be carried whole (all
functions, `MODIFIED` and `UNCHANGED` together, exactly as legacy has
them), or have the specific blocking `static` functions individually
promoted to external linkage in `asterisk-chan-dongle` — a much larger
intervention on upstream than "expose symbols for the proxy calls"
originally implied, and not decided here (see Open Design Questions).

**This directly changes acceptance criterion 1's answer**: for 12 of 16
files, the "safe, minimal" version of this restructuring carries the
whole file (`MODIFIED` + `UNCHANGED` functions together, unmodified from
legacy, keeping legacy's original bg111/mixed copyright rather than a
NativeMind one — there is no clean "Svistok-only" extraction possible
without either the static-promotion intervention or accepting broken
builds).

## Full File Inventory

### A. Top-level files present in both trees (19 module-relevant `.c`, 14 headers, `single.c`, `configure.in`, `Makefile.in`, `config.h.in`)

| File | Status | Notes |
|---|---|---|
| app.c | MODIFIED | 1/4 functions changed |
| app.h | MODIFIED | `+#include "share.h"` |
| at_command.c | MODIFIED | 12 changed, 14 new, 11 unchanged (of 37) |
| at_command.h | MODIFIED | new `CMD_AT_*` enum values + prototypes |
| at_parse.c | MODIFIED | 1 changed, 3 new, 15 unchanged |
| at_parse.h | MODIFIED | 3 new prototypes |
| at_queue.c | MODIFIED | 1 changed, 1 new, 16 unchanged |
| at_queue.h | **IDENTICAL** | no action |
| at_read.c | MODIFIED | 2 changed, 2 unchanged |
| at_read.h | **IDENTICAL** | no action |
| at_response.c | MODIFIED | 20 changed, 13 new, 13 unchanged (of 46) |
| at_response.h | MODIFIED | new `RES_*` enum values |
| BUGS | IDENTICAL | no action |
| chan_dongle.c | MODIFIED | 21 changed, 4 new, 27 unchanged, 1 upstream fn removed (of 53) |
| chan_dongle.h | MODIFIED | extensive — many new struct fields/macros (billing/limits/stats), see below |
| channel.c | MODIFIED | 15 changed, 1 new, 10 unchanged |
| channel.h | MODIFIED | `const` qualifier dropped from `channel_tech` |
| char_conv.c | IDENTICAL | no action |
| char_conv.h | IDENTICAL | no action |
| cli.c | MODIFIED | 8 changed, 8 new, 17 unchanged (of 33) |
| cli.h | MODIFIED | `+#include "at_queue.h"` |
| config.h.in | IDENTICAL | no action |
| configure.in | MODIFIED | package URL/revision string only — cosmetic |
| COPYRIGHT.txt | IDENTICAL | no action |
| cpvt.c | MODIFIED | 1/5 changed |
| cpvt.h | MODIFIED | new `requestor`, `answered` fields |
| dc_config.c | MODIFIED | 2 changed, 4 unchanged, 1 upstream fn removed |
| dc_config.h | MODIFIED | `SERIAL_SIZE`, longer `DEVPATHLEN`, new `serial`/`net`/`dev`/`agroup` fields |
| export.h | IDENTICAL | no action |
| helpers.c | MODIFIED | 3/11 changed |
| helpers.h | IDENTICAL | no action |
| INSTALL | IDENTICAL | no action |
| LICENSE.txt | IDENTICAL | no action |
| Makefile.in | MODIFIED | `DEFS=-DASTERISK_VERSION_NUM=110000`, `$(STRIP)` disabled, whitespace |
| manager.c | MODIFIED | 2/24 changed |
| manager.h | IDENTICAL | no action |
| memmem.c / .h | IDENTICAL | no action |
| mixbuffer.c / .h | IDENTICAL | no action |
| mutils.h | IDENTICAL | no action |
| pdiscovery.c | MODIFIED | 5 changed, 1 new, 35 unchanged |
| pdiscovery.h | MODIFIED | new `serial` field; `pdiscovery_lookup()` gained a `serial` parameter |
| pdu.c | MODIFIED | 3 changed, 1 new, 9 unchanged |
| pdu.h | MODIFIED | new `pdu_parse_cds` prototype |
| ringbuffer.c | MODIFIED | 1 new (`rb_read_until_char_after_iov`), 10 unchanged |
| ringbuffer.h | MODIFIED | new prototype for the above |
| single.c | MODIFIED (trivial) | one extra commented-out `//include "share.c"` line — alternate single-TU build mode; must be regenerated to match the final `src/` layout, not hand-copied |
| stamp-h.in | IDENTICAL | no action |
| TODO.txt | IDENTICAL | no action |

### B. Matched subdirectories present in both trees

| Path | Status |
|---|---|
| `test/parse.c`, `test/test1.c` | IDENTICAL |
| `tools/discovery.c`, `tools/tty.h` | IDENTICAL |
| `tools/tty.c` | MODIFIED — exactly one function, `lock_build()`: lock-file name changed from `/var/lock/LCK..%s` to `/var/lock/LOCK..%s`. Standalone helper tool (`discovery_OBJS`), unrelated to `chan_dongle.c`'s own `lock_build`/`lock_create`. |
| `etc/dongle.conf`, `etc/extensions.conf` | IDENTICAL |
| `contrib/openwrt/*/Makefile` | IDENTICAL |

### C. Top-level entries that exist **only** in legacy (no upstream counterpart at all)

**Genuinely new source, part of the live `chan_dongle.so` build closure** (via `#include`):
`select.c`, `select.h`, `dserial.c`, `limits.c`, `share.c`, `share.h`, `stat.c`

**New source, but dead code** (included only in a commented-out line — not compiled):
`dsp.c` (46 functions, unused), `share_mysql.c` / `share_mysql.h` (14 functions, unused)

**New source, third-party, standalone (not chan_dongle.so, not Svistok-authored)**:
`hub-ctrl.c` — vendored USB hub power-control CLI tool; not part of the module.

**Stale/duplicate** (exclude from `src`):
`tty_v2.c`, `ttyprog_core.c`, `ttyprog_programmator.c`, `ttyprog_test.c`, `ttyprog_svistok.c` at top level — all byte-identical to `old/`, superseded by the live `programmator/` copies.

**Build artifacts** (exclude): `aclocal.m4`, `autom4te.cache/`, all `.o`/`.gch` files, `compile`, `config.guess`, `config.sub`, `install-sh`, `missing`, `config.h`, `config.log*`, `config.status`, `configure`, `Makefile`, `stamp-h1`

**Junk/scratch** (exclude): `1`, `2`, `3`, `d`, `CONF!!!!!!!!!!!`, `list`, `list2`, `todo`, `LICENSE`

**New documentation** (keep): `README.md`, `README_ru.md`

**New operational shell scripts**: `make.sh`, `md.sh` (runtime dir bootstrap), `prog.sh`, `update.sh` (generic, exclude), `upgrade.sh`, `upgrade_prog.sh`

### D. Subdirectories that exist **only** in legacy (whole new subprojects) — out of this flow's scope to place into modules, but relevant context for `src/`'s own build

**`programmator/`** (firmware-flashing): `ttyprog_svistok.c` (live, pulled into `cli.c`), `ttyprog_core.c` (live, 149 lines longer than the stale copy — IMEI-change support + `#include "crc.c"`), `crc.c`, `ttyprog_programmator.c` (standalone tool, own `main()`), `addons.c`, `tty_v2.c` (standalone tool's own copy), `ttyprog_test.c`. Non-source: `fuall.sh`, `fupdate3.sh`, `fupdate4.sh`, `updateall2.sh`, `updateall3.sh`, build artifacts.

**`simnode/`**: `adiscovery_core.c` (live, used by 2 of 3 entry points) + `adiscovery_svistok.c` (the one actually `#include`d into `chan_dongle.c` — see Key Discovery, this is core-module content, not a separate daemon) + `adiscovery_test.c` (a genuine standalone polling daemon, separate concern). `adiscovery_core_new.c`/`adiscovery_simnode.c` — likely-abandoned experiment (`DIE!!!` marker), recommend excluding.

**`reader/`**: `reader_core.c`/`.h`, `adapter.c`, `emulator.c` — SIM reader/emulator, no reference from any module source found anywhere.

**`old/`** (top-level): byte-identical duplicates, exclude entirely.

## Function-Level Classification (all 17 modified module `.c` files)

Format: **MODIFIED** functions first, then **NEW**, then **UNCHANGED**
(per the Static-Linkage Safety Analysis above, only actually deletable in
4 of these 16 files), then **REMOVED** (upstream-only, informational).

### app.c — NOT safe to trim (1 internally-referenced static)
- MODIFIED: `app_status_exec`
- UNCHANGED: `app_send_sms_exec`, `app_register`, `app_unregister`

### at_command.c — NOT safe to trim (1)
- MODIFIED: `at_fill_generic_cmd`, `at_enque_generic`, `at_enque_initialization`, `at_enque_cops`, `at_enque_pdu`, `at_enque_sms`, `at_enque_ussd`, `at_enque_dial`, `at_enque_hangup`
- MODIFIED (cosmetic only — comment-style/blank-line differences, zero behavioral change; confirmed 2026-08-26 while auditing the sibling flow's output, which correctly excludes these): `at_enque_set_ccwa`, `at_enque_reset`
- NEW: `at_enque_initialization_modem`, `at_enque_initialization_sim_e`, `at_enque_initialization_sim_mb`, `at_enque_initialization_sim`, `at_enque_cmd_proc`, `at_enque_spn`, `at_enque_iccid`, `at_enque_sn`, `at_enque_cfun_v`, `at_enque_cpin_v`, `at_enque_cfun1`, `at_enque_cfun5`, `at_enque_cfun6`, `at_enque_sysinfo`
- UNCHANGED: `at_fill_generic_cmd_va`, `at_enque_dtmf`, `at_enque_answer`, `at_enque_activate`, `at_enque_flip_hold`, `at_enque_ping`, `at_enque_user_cmd`, `at_enque_retrive_sms`, `at_enque_volsync`, `at_enque_clcc`, `at_enque_conference`, `at_hangup_immediality`

### at_parse.c — NOT safe to trim (3)
- MODIFIED: `at_parse_cpin`
- NEW: `at_parse_spn`, `at_parse_cds`, `at_parse_sysinfo`
- UNCHANGED: `mark_line`, `at_parse_cnum`, `at_parse_cops`, `at_parse_creg`, `at_parse_cmti`, `parse_cmgr_text`, `parse_cmgr_pdu`, `at_parse_cmgr`, `at_parse_cusd`, `at_parse_csq`, `at_parse_rssi`, `at_parse_mode`, `at_parse_csca`, `at_parse_clcc`, `at_parse_ccwa`

### at_queue.c — NOT safe to trim (5)
- MODIFIED: `at_write`
- NEW: `at_log`
- UNCHANGED: `at_queue_free_data`, `at_queue_free`, `at_queue_remove`, `at_queue_head_cmd_nc`, `at_queue_add`, `write_all`, `at_queue_remove_cmd`, `at_queue_run`, `at_queue_insert_const`, `at_queue_insert_task`, `at_queue_insert`, `at_queue_handle_result`, `at_queue_flush`, `at_queue_head_task`, `at_queue_head_cmd`, `at_queue_timeout`

### at_read.c — SAFE to trim
- MODIFIED: `at_read`, `at_read_result_iov`
- UNCHANGED: `at_wait`, `at_read_result_classification`

### at_response.c — NOT safe to trim (8)
- MODIFIED: `at_response_ok`, `at_response_error`, `at_response_rssi`, `at_response_mode`, `at_response_orig`, `at_response_conf`, `at_response_cend`, `at_response_conn`, `start_pbx`, `at_response_clcc`, `at_response_ring`, `at_response_cmgr`, `at_response_cusd`, `at_response_cpin`, `at_response_csq`, `at_response_cops`, `at_response_creg`, `at_response_cgmi`, `at_response_cgmm`, `at_response_cgmr`, `at_response_cgsn`, `at_response_cimi`, `at_response`
- NEW: `at_response_dsflowrpt`, `at_response_sysinfo`, `set_channel_vars2`, `at_response_cds`, `at_response_spn`, `at_response_cvoice`, `at_response_cardlock`, `at_response_freqlock`, `at_response_sn`, `at_response_iccid`, `at_response_cfun_v`, `at_response_simst`, `at_response_srvst`, `at_response_unknown`
- UNCHANGED: `at_res2str`, `request_clcc`, `at_response_csca`, `at_response_ccwa`, `at_response_cmti`, `at_response_sms_prompt`, `at_response_smmemfull`, `at_response_cnum`, `at_response_busy`

### chan_dongle.c — NOT safe to trim (8)
- MODIFIED: `lock_build`, `lock_create`, `opentty`, `disconnect_dongle`, `clean_read_data`, `do_monitor_phone`, `pvt_stop`, `pvt_discovery`, `pvt_start`, `pvt_free`, `pvt_destroy`, `do_discovery`, `ready4voice_call`, `find_device_ex`, `find_device_ext`, `pvt_state_base`, `pvt_str_state`, `pvt_str_state_ex`, `rssi2dBm`, `pvt_dsp_setup`, `pvt_create`, `pvt_time4restate`, `pvt_reconfigure`, `reload_config`, `load_module`, `public_state_init`, `public_state_fini`
- NEW: `can_sms`, `ast_channel_show_vars`, `ast_channel_get_var`, `pvt_create_new`
- UNCHANGED: `port_status`, `lock_try`, `closetty`, `start_monitor`, `discovery_restart`, `discovery_stop`, `pvt_on_create_1st_channel`, `pvt_on_remove_last_channel`, `pvt_get_pseudo_call_idx`, `is_dial_possible2`, `is_dial_possible`, `pvt_enabled`, `can_dial`, `GSM_regstate2str`, `sys_mode2str`, `sys_submode2str`, `pvt_try_restate`, `devices_destroy`, `unload_module`, `pvt_reload`, `reload_module`, `self_module`
- REMOVED: `find_device_by_resource_ex`
- **Note**: `do_discovery()` (a background thread `chan_dongle.c` starts unconditionally at module load) calls `sysdevs_find`/`usbdevs_find`/`usbdevs_log`/`usbdevs_filelist*` — functions defined in `simnode/adiscovery_core.c`, reached transitively via the `#include "simnode/adiscovery_svistok.c"` composition (Key Discovery). This is core device-lifecycle logic, not optional/removable.

### channel.c — NOT safe to trim (7)
- MODIFIED: `channels_loop`, `channel_call`, `channel_hangup`, `channel_answer`, `channel_digit_begin`, `channel_read`, `channel_write`, `channel_fixup`, `channel_devicestate`, `channel_indicate`, `change_channel_state`, `set_channel_vars`, `new_channel`, `queue_hangup`, `start_local_channel`, `channel_func_read`, `channel_func_write`
- NEW: `channel_request`
- UNCHANGED: `parse_dial_string`, `disactivate_call`, `activate_call`, `channel_digit_end`, `iov_write`, `timing_write`, `write_conference`, `queue_control_channel`

### cli.c — NOT safe to trim (16 — the largest cluster after pdiscovery.c)
- MODIFIED: `getACD`, `cli_show_devices`, `cli_show_device_settings`, `cli_show_device_state`, `cli_show_device_statistics`, `cli_sms`
- NEW: `cli_show_devicesl`, `cli_show_devicesd`, `cli_show_devicesi`, `cli_diagmode`, `cli_changeimei`, `cli_dongle_update`, `cli_setgroup`, `cli_setgroupimsi`
- UNCHANGED: `complete_device`, `getASR`, `cli_show_version`, `cli_cmd`, `cli_ussd`, `cli_pdu`, `cli_ccwa_set`, `cli_reset`, `restate2str_msg`, `cli_restart_event`, `cli_stop`, `cli_restart`, `cli_remove`, `cli_start`, `cli_reload`, `cli_discovery`, `cli_register`, `cli_unregister`, `ast_str_truncate2`

### cpvt.c — NO FILE NEEDED (corrected 2026-08-26)
- MODIFIED (cosmetic only — one blank-line difference, zero behavioral
  change; confirmed while auditing the sibling flow's output, which
  correctly has no `cpvt.c` at all for this reason): `cpvt_alloc`
- UNCHANGED: `init_pipe`, `cpvt_free`, `pvt_find_cpvt`, `pvt_call_dir`
- **Consequence**: with `cpvt_alloc` correctly treated as behaviorally
  unchanged, every function in `cpvt.c` resolves via direct link to
  upstream — no `src/cpvt.c` is needed at all (only `cpvt.h`, already
  `MODIFIED` for new struct fields, still needs carrying).

### dc_config.c — SAFE to trim
- MODIFIED: `dc_uconfig_fill`, `dc_sconfig_fill`
- UNCHANGED: `dc_dtmf_setting2str`, `dc_sconfig_fill_defaults`, `dc_gconfig_fill`, `dc_config_fill`
- REMOVED: `dc_dtmf_str2setting`

### helpers.c — SAFE to trim
- MODIFIED: `is_valid_ussd_string`, `send2`, `schedule_restart_event`
- MODIFIED (cosmetic only — two blank-line difference, zero behavioral
  change; confirmed 2026-08-26): `send_sms`
- UNCHANGED: `is_valid_phone_number`, `get_at_clir_value`, `send_ussd`, `send_pdu`, `send_reset`, `send_ccwa_set`, `send_at_command`

### manager.c — NOT safe to trim (12)
- MODIFIED: `manager_show_devices`, `manager_register`
- UNCHANGED: (all other 22 functions)

### pdiscovery.c — NOT safe to trim (27 — one large internal cache subsystem)
- MODIFIED: `info_free`, `info_copy`, `cache_lookup`, `pdiscovery_handle_response`, `pdiscovery_get_info`, `pdiscovery_check_req`, `pdiscovery_lookup`
- NEW: `pdiscovery_handle_sn`
- UNCHANGED: (remaining 33 functions)

### pdu.c — NOT safe to trim (7)
- MODIFIED: `pdu_parse_number`, `pdu_build`, `pdu_parse`
- NEW: `pdu_parse_cds`
- UNCHANGED: `pdu_digit2code`, `pdu_code2digit`, `pdu_relative_validity`, `pdu_parse_byte`, `pdu_store_number`, `pdu_parse_sca`, `pdu_parse_timestamp`, `check_encoding`, `pdu_dcs_alpabet2encoding`

### ringbuffer.c — SAFE to trim
- NEW: `rb_read_until_char_after_iov`
- UNCHANGED: `rb_memcmp`, `rb_read_all_iov`, `rb_read_n_iov`, `rb_read_until_char_iov`, `rb_read_until_mem_iov`, `rb_read_upd`, `rb_read`, `rb_write_iov`, `rb_write_upd`, `rb_write_core`

### tools/tty.c (standalone helper tool, not the module)
- MODIFIED: `lock_build`
- UNCHANGED: `lock_create`, `lock_try`, `opentty`, `closetty`, `write_all`

## Header Changes Summary

- **at_command.h**: new `CMD_AT_CFUN_V`, `CMD_AT_SPN`, `CMD_AT_CARDLOCK`, `CMD_AT_SN`, `CMD_AT_ICCID`, `CMD_AT_FREQLOCK`, `CMD_AT_CSNR`, `CMD_AT_SYSINFO` enum values + prototypes for the new `at_enque_*` functions.
- **at_parse.h**: new prototypes for `at_parse_spn`, `at_parse_cds`, `at_parse_sysinfo`.
- **at_response.h**: new `RES_SPN`, `RES_SYSINFO`, `RES_DSFLOWRPT`, `RES_SIMST`, `RES_CFUN_V`, `RES_ICCID`, `RES_SN`, `RES_CDS`; `RES_CVOICE` commented out.
- **chan_dongle.h**: copyright block changed; `#include "select.h"`; `MAXDONGLEDEVICES` 128→256; new `ACDL*`/`ASRL*`/`PDDL*` macros; new `STAT_*` macros; new `pvt` fields for billing/statistics, SIM/network identity, programming/diagnostics, device-selection; `pvt_dsp_setup`'s prototype now file-local; new forward decls for `pvt_create`/`pvt_destroy`.
- **channel.h**: `channel_tech` loses `const`.
- **cli.h**: `+#include "at_queue.h"`.
- **cpvt.h**: new `requestor`/`answered` fields.
- **dc_config.h**: new `SERIAL_SIZE`, `DEVPATHLEN` 256→512, new `agroup`/`serial`/`dev`/`net` fields; `dc_dtmf_str2setting` prototype removed (consistent with its removal from `dc_config.c`).
- **pdiscovery.h**: new `serial` field; `pdiscovery_lookup()` gains a `serial` parameter.
- **pdu.h**: new `pdu_parse_cds` prototype.
- **ringbuffer.h**: new `rb_read_until_char_after_iov` prototype.
- **app.h**: `+#include "share.h"`.

## Build System Changes

- `configure.in`: package URL/`PACKAGE_REVISION` — cosmetic.
- `Makefile.in`: `-DASTERISK_VERSION_NUM=110000` added, `$(STRIP)` disabled, whitespace. Object list unchanged from upstream — confirms the 19-file closure is exhaustive.
- `single.c`: regenerate from the final `src/` file list, don't hand-copy.

## Planned `src/` File List (the concrete deliverable)

Legend: **[carry-whole]** = entire legacy file copied verbatim, `MODIFIED`
+ `UNCHANGED` functions together, legacy copyright kept (per the
Static-Linkage Safety Analysis — no clean extraction possible without a
static-promotion intervention on upstream, not decided here);
**[trim]** = copy-then-delete `UNCHANGED` bodies, safe for the 4 files
where this doesn't break internal linkage; **[new]** = copy-as-is
(no upstream counterpart).

### Carried whole (11 files — `MODIFIED` + `UNCHANGED` together, legacy copyright)

`app.c`, `at_command.c`, `at_parse.c`, `at_queue.c`, `at_response.c`,
`chan_dongle.c`, `channel.c`, `cli.c`, `manager.c`, `pdiscovery.c`, `pdu.c`

(`cpvt.c` removed from this list 2026-08-26 — its one `MODIFIED` function
turned out to be cosmetic-only on closer diff, so no file is needed at
all; see Function-Level Classification above.)

Headers for these files (`app.h`, `at_command.h`, `at_parse.h`,
`at_response.h`, `chan_dongle.h`, `channel.h`, `cli.h`, `cpvt.h`,
`pdiscovery.h`, `pdu.h`) are always carried in full regardless of the
`.c` file's trim status — declarations must be complete for compilation
no matter which translation unit defines each function.

### Trimmed (4 files — `UNCHANGED` bodies deleted, resolved via direct link to `asterisk-chan-dongle`)

`at_read.c`, `dc_config.c`, `helpers.c`, `ringbuffer.c` (+ their headers
`dc_config.h`, `ringbuffer.h` carried in full; `at_read.h`/`helpers.h`
are IDENTICAL to upstream, not copied at all)

### `src/dongle/` — pure-proxy files

Still expected **empty** — every one of the 16 module `.c` files has at
least one `MODIFIED`/`NEW` function (see Function-Level Classification).

### Already-`#include`d files (keep as-is, same relative placement)

`select.c`, `select.h` (into `chan_dongle.c`); `dserial.c`, `limits.c`
(into `at_response.c`); `share.c`, `share.h`, `stat.c` (into `cli.c`);
`simnode/adiscovery_svistok.c`, `simnode/adiscovery_core.c` (into
`chan_dongle.c` — the newly-found composition; note this pulls the
whole `simnode/` device-scanning engine into `src/`, since `do_discovery()`
in `chan_dongle.c` depends on it directly, not optionally)

### New companion files for chan_svistok-only functions

Naming convention: `<host>_new.c` — one companion file per host that has
`NEW` functions, named after the file they're extracted from. Proposed,
not yet created except where noted:

| New file | Host | Contains | Status |
|---|---|---|---|
| `ringbuffer_new.c` | `ringbuffer.c` | `rb_read_until_char_after_iov` | **Actually creatable now** — `ringbuffer.c` is one of the 4 safe-to-trim files |
| `at_command_new.c` | `at_command.c` | `at_enque_initialization_modem`, `at_enque_initialization_sim_e`, `at_enque_initialization_sim_mb`, `at_enque_initialization_sim`, `at_enque_cmd_proc`, `at_enque_spn`, `at_enque_iccid`, `at_enque_sn`, `at_enque_cfun_v`, `at_enque_cpin_v`, `at_enque_cfun1`, `at_enque_cfun5`, `at_enque_cfun6`, `at_enque_sysinfo` | Reserved name only — extraction not done, host is carry-whole |
| `at_parse_new.c` | `at_parse.c` | `at_parse_spn`, `at_parse_cds`, `at_parse_sysinfo` | Reserved only |
| `at_response_new.c` | `at_response.c` | `at_response_dsflowrpt`, `at_response_sysinfo`, `set_channel_vars2`, `at_response_cds`, `at_response_spn`, `at_response_cvoice`, `at_response_cardlock`, `at_response_freqlock`, `at_response_sn`, `at_response_iccid`, `at_response_cfun_v`, `at_response_simst`, `at_response_srvst`, `at_response_unknown` | Reserved only |
| `chan_dongle_new.c` | `chan_dongle.c` | `can_sms`, `ast_channel_show_vars`, `ast_channel_get_var`, `pvt_create_new` | Reserved only |
| `channel_new.c` | `channel.c` | `channel_request` | Reserved only |
| `cli_new.c` | `cli.c` | `cli_show_devicesl`, `cli_show_devicesd`, `cli_show_devicesi`, `cli_diagmode`, `cli_changeimei`, `cli_dongle_update`, `cli_setgroup`, `cli_setgroupimsi` | Reserved only |
| `pdiscovery_new.c` | `pdiscovery.c` | `pdiscovery_handle_sn` | Reserved only |
| `pdu_new.c` | `pdu.c` | `pdu_parse_cds` | Reserved only |
| `at_queue_new.c` | `at_queue.c` | `at_log` | Reserved only |

"Reserved only" means: the name and contents are decided, but the file is
**not created yet** — its host is one of the 12 carry-whole files, so the
function currently stays physically in place in the whole-copied host
(extracting it risks the same static-linkage break as deleting an
`UNCHANGED` function, since `NEW` functions can call file-local `static`
helpers too — not verified clean per-function here). These 9 files get
created only if/when the static-promotion path (Open Design Questions)
is chosen for that host file, or if a future check confirms a specific
`NEW` function has no such internal dependency and can be safely
extracted on its own even while the rest of the host stays whole.

**Alternative naming considered**: group by feature instead of by host
file — e.g. one `sim_identity.c` covering the SIM/network-identity
functions spread across `at_command.c`/`at_parse.c`/`at_response.c`/
`pdiscovery.c`/`pdu.c` (`at_enque_spn`/`iccid`/`sn`/`cfun_v`/`cpin_v`,
`at_parse_spn`/`cds`/`sysinfo`, `at_response_spn`/`cvoice`/`cardlock`/
`freqlock`/`sn`/`iccid`/`cfun_v`/`simst`/`srvst`, `pdiscovery_handle_sn`,
`pdu_parse_cds`) rather than one file per host. Not chosen as the
default — per-host naming maps directly to the classification table
above and is easier to audit; feature-grouping is a Plan-phase judgment
call if preferred.

### Dead code — excluded

`dsp.c`, `share_mysql.c`/`.h`

### Non-code artifacts (carry forward)

`README.md`, `README_ru.md`, `md.sh`, build files (`configure.in`,
`Makefile.in`, regenerated `single.c`)

### Excluded entirely

`old/`, stale top-level duplicates, all build artifacts, all junk/scratch
files, `update.sh`. (`programmator/`, `simnode/adiscovery_test.c`,
`reader/`, `hub-ctrl.c` are out of this flow's scope — not this flow's
concern to place anywhere.)

## Behavior Specifications

### Happy Path

1. For the 4 trimmable files: copy verbatim, delete `UNCHANGED` bodies,
   verify byte-match on survivors.
2. For the 12 carried-whole files: copy verbatim in full, no deletions.
3. For genuinely-new files: copy as-is.
4. Apply copyright per file: legacy/bg111 kept on all 12 carried-whole +
   4 trimmed files (mixed authorship); NativeMind on genuinely-new files
   only (`select.c`, `share.c`, `stat.c`, `dserial.c`, `limits.c`).

### Edge Cases

| Case | Trigger | Handling |
|---|---|---|
| `single.c` alternate build mode | `-DBUILD_SINGLE` | Regenerate `#include` list from final `src/` layout, don't hand-copy |
| `#include "file.c"` composition | Building host `.c` | Preserve exact relative-path `#include` |
| Two `ttyprog_core.c`/`tty_v2.c` variants | N/A — out of scope here (programmator not this flow's concern) | — |
| `adiscovery_core.c` vs `_new.c` | `simnode/` composition into `chan_dongle.c` | Use `adiscovery_core.c` (the live one, `#include`d by `adiscovery_svistok.c`) |
| Static-linkage breakage on naive trim | Any of the 12 not-safe-to-trim files | Carry whole — see Static-Linkage Safety Analysis |

## Open Design Questions

- [ ] Whether to pursue the static-promotion path (expose the ~90
      blocking `static` functions across the 12 not-safe files as
      external linkage in `asterisk-chan-dongle`) to enable full trimming
      later, or accept carry-whole as the final state. Not decided —
      carry-whole is the safe default that ships without it.
- [ ] Confirm disposition of `dsp.c`/`share_mysql.c` (dead code) — exclude
      entirely, or keep as reference?
- [ ] `channel_tech` losing its `const` qualifier — confirm intentional.
- [ ] Whether `ringbuffer.c`'s single new function warrants its own
      companion file or can stay in place.

## Testing Strategy

No compatible Linux/Asterisk build environment available. Structural
verification: byte-diff every carried/trimmed file's surviving content
against legacy; for the 4 trimmed files, a link-time symbol check that
every deleted function's name resolves to exactly one definition
(`asterisk-chan-dongle`'s).

---

## Approval

- [x] Reviewed by: Anton
- [x] Approved on: 2026-08-26
- [x] Notes: approved including the concrete `<host>_new.c` companion-file
      naming added just before approval.
