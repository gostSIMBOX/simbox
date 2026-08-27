# Specifications: asterisk-chan-svistok-chan-dongle

> Version: 1.2
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

Methodology: byte-for-byte comparison (`cmp`) of every file that exists in
both trees by relative path; for `.c` files that differ, a purpose-built
regex/brace-matching script (`func_diff.py`, not part of the sibling flow's
tooling) extracted top-level function bodies from both versions and compared
them by name to classify each legacy function as `UNCHANGED` / `MODIFIED` /
`NEW`, and flagged upstream functions absent from legacy as `REMOVED`. Two
functions in `at_command.c` (`at_fill_generic_cmd`, `at_enque_generic`) use a
`return_type __attribute__((...)) name(...)` declaration style that the
extractor's naming heuristic initially mis-labeled; their bodies were
diffed correctly, only their *names* needed manual correction below (already
fixed in this document). No other anomalies were found on manual spot-check
of the tables.

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
| `dsp.c` | `chan_dongle.c:74` — `//include "dsp.c"` | **commented out — dead code** |
| `share_mysql.c` | `cli.c:26` — `// include "share_mysql.c"` | **commented out — dead code** |

This is important for the planned `src/` layout: these files are not
independent subsystems to be linked separately — they must stay physically
next to (and be `#include`d by, or replace behavior within) their host file,
the same way they do today. This actually already satisfies "new
functionality lives in its own file" (Requirement acceptance criterion 5)
for these particular cases — the legacy codebase already separated them out
this way; this flow's job is to preserve that shape, not invent it.

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
| single.c | MODIFIED (trivial) | one extra commented-out `//include "share.c"` line — this is the alternate single-TU build mode; must be regenerated to match whatever final `src/` layout is chosen, not hand-copied |
| stamp-h.in | IDENTICAL | no action |
| TODO.txt | IDENTICAL | no action |

**Critical finding**: every one of the 17 module `.c` files that has any
custom code at all has **at least one** `MODIFIED` or `NEW` function. **None
of the top-level module files is a pure proxy** (100% unchanged functions).
Consequently, under acceptance criterion 6, `src/dongle/` is expected to
hold **none** of the 17 module files — see "Open Design Questions" below for
what, if anything, should live there.

### B. Matched subdirectories present in both trees

| Path | Status |
|---|---|
| `test/parse.c`, `test/test1.c` | IDENTICAL |
| `tools/discovery.c`, `tools/tty.h` | IDENTICAL |
| `tools/tty.c` | MODIFIED — exactly one function, `lock_build()`: lock-file name changed from `/var/lock/LCK..%s` to `/var/lock/LOCK..%s`. This is a **standalone helper tool** (`discovery_OBJS` in the Makefile), unrelated to the `chan_dongle.so` module's own (differently-named) `lock_build`/`lock_create` in `chan_dongle.c`. |
| `etc/dongle.conf`, `etc/extensions.conf` | IDENTICAL |
| `contrib/openwrt/*/Makefile` | IDENTICAL |

### C. Top-level entries that exist **only** in legacy (no upstream counterpart at all)

**Genuinely new source, part of the live `chan_dongle.so` build closure** (via `#include`, see table above):
`select.c`, `select.h`, `dserial.c`, `limits.c`, `share.c`, `share.h`, `stat.c`

**New source, but dead code** (included only in a commented-out line — not compiled):
`dsp.c` (would add custom Asterisk DSP/tone detection — 46 functions, unused), `share_mysql.c` / `share_mysql.h` (MySQL-backed billing variant of `share.c` — 14 functions, unused)

**New source, third-party, standalone (not chan_dongle.so, not Svistok-authored)**:
`hub-ctrl.c` — vendored "Free Software Initiative of Japan" USB hub power-control CLI tool; built ad-hoc (`gcc hub-ctrl.c -lusb -o hub-ctrl`) and invoked from `upgrade.sh`/`upgrade_prog.sh`, not from the module.

**Stale/duplicate — byte-identical to `old/`, not referenced by any build script or `#include` from a non-stale location** (exclude from `src`):
`tty_v2.c`, `ttyprog_core.c`, `ttyprog_programmator.c`, `ttyprog_test.c` (the live versions are the *different*, newer copies under `programmator/`, see section D). `ttyprog_svistok.c` at top level is also unused directly (the live include path is `programmator/ttyprog_svistok.c`), though its content happens to be byte-identical to the programmator/ copy.

**Build artifacts (autotools/compiler output — never source, exclude)**:
`aclocal.m4`, `autom4te.cache/`, `at_command.o`, `at_queue.o`, `at_read.o`, `at_response.o`, `chan_dongle.o`, `chan_dongle.h.gch`, `channel.o`, `cli.o`, `cpvt.o`, `pdiscovery.o`, `compile`, `config.guess`, `config.sub`, `install-sh`, `missing` (autotools helper symlinks), `config.h`, `config.log`, `config.log.orig`, `config.log.orig.orig`, `config.status`, `configure`, `Makefile`, `stamp-h1`

**Junk / scratch, no relation to source or build (exclude)**:
`1`, `2`, `3` (captured shell/build console output), `d` (one-line `CFLAGS=-g` snippet), `CONF!!!!!!!!!!!` (one-line note of a `./configure` invocation), `list`, `list2` (captured `adiscovery` device-detection log output), `todo` (personal Russian scratch notes), `LICENSE` (generic license text added later, unrelated to `LICENSE.txt`)

**New documentation** (keep, not code): `README.md`, `README_ru.md`

**New operational shell scripts** (deploy/build helpers, not compiled source):
- `make.sh` — `CC=gcc-4.5 ./configure && make` (build helper)
- `md.sh` — creates the `/var/svistok/{general,dongles,sim,bs}/...` runtime state directory tree (relevant background for the existing state-persistence ADR/flow)
- `prog.sh` — builds the standalone `programmator` tool
- `update.sh` — generic `git add/pull/commit/push`, not project-specific
- `upgrade.sh` — full redeploy: rebuild module, rebuild `programmator`, rebuild `hub-ctrl`, (commented-out) Asterisk restart
- `upgrade_prog.sh` — rebuild `programmator` + `hub-ctrl` only

### D. Subdirectories that exist **only** in legacy (whole new subprojects)

**`programmator/`** — firmware-flashing subsystem. `#include` graph:
- `programmator/ttyprog_svistok.c` — **live**, pulled into `cli.c` (module build). Includes `programmator/ttyprog_core.c`.
- `programmator/ttyprog_core.c` — **live** version (149 lines longer than the stale top-level/`old/` copy: adds IMEI-change command bytes and `#include "crc.c"`). Backs `cli.c`'s new `cli_changeimei`/`cli_dongle_update` via `ttyprog_changeimei()`/`ttyprog_set_diagmode()`.
- `programmator/crc.c` — new, checksum helper for the firmware protocol, included by the live `ttyprog_core.c`.
- `programmator/ttyprog_programmator.c` — separate standalone CLI tool (`main()`, built via `prog.sh`/`upgrade_prog.sh` as `/usr/simbox/programmator/programmator`), includes `tty_v2.c`, `ttyprog_core.c` (its own copy — same live version, same directory), `addons.c`.
- `programmator/addons.c` — new, extra helpers for the standalone tool only.
- `programmator/tty_v2.c` — new, standalone tool's own tty helper (parallel to top-level `tools/tty.c`, not shared with it).
- `programmator/ttyprog_test.c` — new, standalone test/diagnostic entry point for the flashing protocol.
- Non-source: `fuall.sh`, `fupdate3.sh`, `fupdate4.sh`, `updateall2.sh`, `updateall3.sh` (fleet update helper scripts — referenced from `chan_dongle.c`'s `usbdevs_filelist_*` calls, e.g. `/usr/simbox/programmator/fuall.sh`), `111`, `a.out`, `programmator` (build artifacts, exclude)

**`simnode/`** — standalone device-discovery daemon, not part of `chan_dongle.so` (no Makefile target, no `#include` from module sources):
- `simnode/adiscovery_core.c` — used by `adiscovery_svistok.c` and `adiscovery_test.c`. **This is the live/real implementation.**
- `simnode/adiscovery_core_new.c` — used only by `adiscovery_simnode.c`; opens with a literal `DIE!!!` comment marker and differs substantially (different buffer sizes, `IN_SIMBOX` conditional). Reads as an **abandoned/broken experiment**, not the active code path. Recommend excluding from `src` (or keeping only as a historical reference), pending user confirmation.
- `simnode/adiscovery_svistok.c`, `simnode/adiscovery_simnode.c`, `simnode/adiscovery_test.c` — three thin `main()` entry points over the two core variants above.
- Non-source: `a.out` (build artifact, exclude)

**`reader/`** — apparent smart-card (SIM) reader/emulator subsystem, not part of `chan_dongle.so`, not referenced from any module source or build script found:
- `reader/reader_core.c` / `reader/reader_core.h` — new. Includes `../programmator/tty_v2.c`.
- `reader/adapter.c`, `reader/emulator.c` — new, both `#include "reader_core.c"`.
- `reader/g.sh` — new, unreviewed helper script.
- `reader/old/comport.pas`, `reader/old/copy.c`, `reader/old/test.c` — nested "old", stale/historical, exclude.
- Non-source: `ada`, `emu` (build artifacts, exclude)

**`old/`** (top-level) — byte-identical duplicates of the stale top-level `tty_v2.c`/`ttyprog_*.c` files. Exclude entirely; superseded by the live `programmator/` copies.

## Function-Level Classification (all 17 modified module `.c` files)

Format: **MODIFIED** functions first (need the legacy body ported in),
then **NEW** (need the legacy body ported in as new code), then
**UNCHANGED** (must resolve to the upstream implementation — no code
needed in `src` for these at all), then **REMOVED** (exists upstream, has
no legacy counterpart — informational only, out of scope to reintroduce).

### app.c
- MODIFIED: `app_status_exec`
- UNCHANGED: `app_send_sms_exec`, `app_register`, `app_unregister`

### at_command.c
- MODIFIED: `at_fill_generic_cmd` *(name-corrected, see Overview)*, `at_enque_generic` *(name-corrected)*, `at_enque_initialization`, `at_enque_cops`, `at_enque_pdu`, `at_enque_sms`, `at_enque_ussd`, `at_enque_set_ccwa`, `at_enque_reset`, `at_enque_dial`, `at_enque_hangup`
- NEW: `at_enque_initialization_modem`, `at_enque_initialization_sim_e`, `at_enque_initialization_sim_mb`, `at_enque_initialization_sim`, `at_enque_cmd_proc`, `at_enque_spn`, `at_enque_iccid`, `at_enque_sn`, `at_enque_cfun_v`, `at_enque_cpin_v`, `at_enque_cfun1`, `at_enque_cfun5`, `at_enque_cfun6`, `at_enque_sysinfo`
- UNCHANGED: `at_fill_generic_cmd_va`, `at_enque_dtmf`, `at_enque_answer`, `at_enque_activate`, `at_enque_flip_hold`, `at_enque_ping`, `at_enque_user_cmd`, `at_enque_retrive_sms`, `at_enque_volsync`, `at_enque_clcc`, `at_enque_conference`, `at_hangup_immediality`

### at_parse.c
- MODIFIED: `at_parse_cpin`
- NEW: `at_parse_spn`, `at_parse_cds`, `at_parse_sysinfo`
- UNCHANGED: `mark_line`, `at_parse_cnum`, `at_parse_cops`, `at_parse_creg`, `at_parse_cmti`, `parse_cmgr_text`, `parse_cmgr_pdu`, `at_parse_cmgr`, `at_parse_cusd`, `at_parse_csq`, `at_parse_rssi`, `at_parse_mode`, `at_parse_csca`, `at_parse_clcc`, `at_parse_ccwa`

### at_queue.c
- MODIFIED: `at_write`
- NEW: `at_log`
- UNCHANGED: `at_queue_free_data`, `at_queue_free`, `at_queue_remove`, `at_queue_head_cmd_nc`, `at_queue_add`, `write_all`, `at_queue_remove_cmd`, `at_queue_run`, `at_queue_insert_const`, `at_queue_insert_task`, `at_queue_insert`, `at_queue_handle_result`, `at_queue_flush`, `at_queue_head_task`, `at_queue_head_cmd`, `at_queue_timeout`

### at_read.c
- MODIFIED: `at_read`, `at_read_result_iov`
- UNCHANGED: `at_wait`, `at_read_result_classification`

### at_response.c
- MODIFIED: `at_response_ok`, `at_response_error`, `at_response_rssi`, `at_response_mode`, `at_response_orig`, `at_response_conf`, `at_response_cend`, `at_response_conn`, `start_pbx`, `at_response_clcc`, `at_response_ring`, `at_response_cmgr`, `at_response_cusd`, `at_response_cpin`, `at_response_csq`, `at_response_cops`, `at_response_creg`, `at_response_cgmi`, `at_response_cgmm`, `at_response_cgmr`, `at_response_cgsn`, `at_response_cimi`, `at_response` (top-level dispatcher)
- NEW: `at_response_dsflowrpt`, `at_response_sysinfo`, `set_channel_vars2`, `at_response_cds`, `at_response_spn`, `at_response_cvoice`, `at_response_cardlock`, `at_response_freqlock`, `at_response_sn`, `at_response_iccid`, `at_response_cfun_v`, `at_response_simst`, `at_response_srvst`, `at_response_unknown`
- UNCHANGED: `at_res2str`, `request_clcc`, `at_response_csca`, `at_response_ccwa`, `at_response_cmti`, `at_response_sms_prompt`, `at_response_smmemfull`, `at_response_cnum`, `at_response_busy`

### chan_dongle.c
- MODIFIED: `lock_build`, `lock_create`, `opentty`, `disconnect_dongle`, `clean_read_data`, `do_monitor_phone`, `pvt_stop`, `pvt_discovery`, `pvt_start`, `pvt_free`, `pvt_destroy`, `do_discovery`, `ready4voice_call`, `find_device_ex`, `find_device_ext`, `pvt_state_base`, `pvt_str_state`, `pvt_str_state_ex`, `rssi2dBm`, `pvt_dsp_setup`, `pvt_create`, `pvt_time4restate`, `pvt_reconfigure`, `reload_config`, `load_module`, `public_state_init`, `public_state_fini`
- NEW: `can_sms`, `ast_channel_show_vars`, `ast_channel_get_var`, `pvt_create_new`
- UNCHANGED: `port_status`, `lock_try`, `closetty`, `start_monitor`, `discovery_restart`, `discovery_stop`, `pvt_on_create_1st_channel`, `pvt_on_remove_last_channel`, `pvt_get_pseudo_call_idx`, `is_dial_possible2`, `is_dial_possible`, `pvt_enabled`, `can_dial`, `GSM_regstate2str`, `sys_mode2str`, `sys_submode2str`, `pvt_try_restate`, `devices_destroy`, `unload_module`, `pvt_reload`, `reload_module`, `self_module`
- REMOVED (upstream-only, not reintroduced): `find_device_by_resource_ex`

### channel.c
- MODIFIED: `channels_loop`, `channel_call`, `channel_hangup`, `channel_answer`, `channel_digit_begin`, `channel_read`, `channel_write`, `channel_fixup`, `channel_devicestate`, `channel_indicate`, `change_channel_state`, `set_channel_vars`, `new_channel`, `queue_hangup`, `start_local_channel`, `channel_func_read`, `channel_func_write`
- NEW: `channel_request`
- UNCHANGED: `parse_dial_string`, `disactivate_call`, `activate_call`, `channel_digit_end`, `iov_write`, `timing_write`, `write_conference`, `queue_control_channel`

### cli.c
- MODIFIED: `getACD`, `cli_show_devices`, `cli_show_device_settings`, `cli_show_device_state`, `cli_show_device_statistics`, `cli_sms`
- NEW: `cli_show_devicesl`, `cli_show_devicesd`, `cli_show_devicesi`, `cli_diagmode`, `cli_changeimei`, `cli_dongle_update`, `cli_setgroup`, `cli_setgroupimsi`
- UNCHANGED: `complete_device`, `getASR`, `cli_show_version`, `cli_cmd`, `cli_ussd`, `cli_pdu`, `cli_ccwa_set`, `cli_reset`, `restate2str_msg`, `cli_restart_event`, `cli_stop`, `cli_restart`, `cli_remove`, `cli_start`, `cli_reload`, `cli_discovery`, `cli_register`, `cli_unregister`, `ast_str_truncate2`

### cpvt.c
- MODIFIED: `cpvt_alloc`
- UNCHANGED: `init_pipe`, `cpvt_free`, `pvt_find_cpvt`, `pvt_call_dir`

### dc_config.c
- MODIFIED: `dc_uconfig_fill`, `dc_sconfig_fill`
- UNCHANGED: `dc_dtmf_setting2str`, `dc_sconfig_fill_defaults`, `dc_gconfig_fill`, `dc_config_fill`
- REMOVED: `dc_dtmf_str2setting`

### helpers.c
- MODIFIED: `is_valid_ussd_string`, `send2`, `send_sms`, `schedule_restart_event`
- UNCHANGED: `is_valid_phone_number`, `get_at_clir_value`, `send_ussd`, `send_pdu`, `send_reset`, `send_ccwa_set`, `send_at_command`

### manager.c
- MODIFIED: `manager_show_devices`, `manager_register`
- UNCHANGED: (all other 22 functions unchanged)

### pdiscovery.c
- MODIFIED: `info_free`, `info_copy`, `cache_lookup`, `pdiscovery_handle_response`, `pdiscovery_get_info`, `pdiscovery_check_req`, `pdiscovery_lookup`
- NEW: `pdiscovery_handle_sn`
- UNCHANGED: (remaining 33 functions unchanged)

### pdu.c
- MODIFIED: `pdu_parse_number`, `pdu_build`, `pdu_parse`
- NEW: `pdu_parse_cds`
- UNCHANGED: `pdu_digit2code`, `pdu_code2digit`, `pdu_relative_validity`, `pdu_parse_byte`, `pdu_store_number`, `pdu_parse_sca`, `pdu_parse_timestamp`, `check_encoding`, `pdu_dcs_alpabet2encoding`

### ringbuffer.c
- NEW: `rb_read_until_char_after_iov`
- UNCHANGED: `rb_memcmp`, `rb_read_all_iov`, `rb_read_n_iov`, `rb_read_until_char_iov`, `rb_read_until_mem_iov`, `rb_read_upd`, `rb_read`, `rb_write_iov`, `rb_write_upd`, `rb_write_core`

### tools/tty.c (standalone helper tool, not the module)
- MODIFIED: `lock_build`
- UNCHANGED: `lock_create`, `lock_try`, `opentty`, `closetty`, `write_all`

## Header Changes Summary

- **at_command.h**: new `CMD_AT_CFUN_V`, `CMD_AT_SPN`, `CMD_AT_CARDLOCK`, `CMD_AT_SN`, `CMD_AT_ICCID`, `CMD_AT_FREQLOCK`, `CMD_AT_CSNR`, `CMD_AT_SYSINFO` enum values + matching string table entries; new prototypes for all the `at_enque_*` NEW functions listed above.
- **at_parse.h**: new prototypes for `at_parse_spn`, `at_parse_cds`, `at_parse_sysinfo`.
- **at_response.h**: new `RES_SPN`, `RES_SYSINFO`, `RES_DSFLOWRPT`, `RES_SIMST`, `RES_CFUN_V`, `RES_ICCID`, `RES_SN`, `RES_CDS` enum values; `RES_CVOICE` commented out (superseded by the new `at_response_cvoice`/handling).
- **chan_dongle.h**: substantial growth — copyright block changed; `#include "select.h"`; `MAXDONGLEDEVICES` 128→256; new `ACDL*`/`ASRL*`/`PDDL*` call-quality-tracking macros; new `STAT_*` macros; a large block of new `pvt` struct fields for **billing/statistics** (`stat_calls_answered`, `stat_acdl`, `stat_asrl`, `stat_pddl`, billing/limit fields, `soupri_t`/`soupri` SIM-priority tracking), **SIM/network identity** (`iccid`, `srna`/`srnb`, `provider_name2`, `freqlock`, `cfun`, `simst`, `srvst`, `sim_ready`, `sim_start`), **programming/diagnostics** (`diagmode`, `changeimei`, `newimei`, `cardlock`), and **device-selection** (`round_robin`/`random_select`/`limit_select` arrays — the `round_robin` fields exist in upstream too but are commented out there; Svistok re-enables and extends them, backing the new `select.c`); `pvt_dsp_setup`'s prototype dropped from the header (now file-local); new forward declarations `static struct pvt * pvt_create(...)`, `static void pvt_destroy(...)`.
- **channel.h**: `channel_tech` loses its `const` qualifier (Svistok mutates it at runtime — needs confirming why during planning).
- **cli.h**: `+#include "at_queue.h"`.
- **cpvt.h**: new `requestor` and `answered` fields on the call-tracking struct.
- **dc_config.h**: new `SERIAL_SIZE` macro, `DEVPATHLEN` 256→512, new `agroup`/`serial`/`dev`/`net` config fields; `dc_dtmf_str2setting` prototype removed (its definition was also `REMOVED` from `dc_config.c` above — dead in both places, consistent).
- **pdiscovery.h**: new `serial` field on the discovery-info struct; `pdiscovery_lookup()` signature gains a `serial` parameter.
- **pdu.h**: new `pdu_parse_cds` prototype.
- **ringbuffer.h**: new `rb_read_until_char_after_iov` prototype.
- **app.h**: `+#include "share.h"`.

## Build System Changes (informational — regeneration deferred to Plan phase)

- `configure.in`: package URL and `PACKAGE_REVISION` string changed — cosmetic, no functional build impact.
- `Makefile.in`: adds `-DASTERISK_VERSION_NUM=110000` to `DEFS`; comments out the `$(STRIP)` post-link step; minor whitespace. The object list itself (`chan_donglem_so_OBJS`) is unchanged from upstream — confirms the 19-file module closure above is exhaustive; every other new file reaches the module only via `#include`, never via a new `.o`/`SOURCES` entry.
- `single.c`: the alternate "everything in one translation unit" build mode. Must be treated as **generated/derived** from the final `src/` file list (whatever that ends up being), not hand-migrated, since its whole content is just an ordered list of `#include`s.

## Planned Module Layout — Moved

**2026-08-26**: the three-module output layout (`res_simbox_core`/
`res_simbox_discovery`/`res_simbox_programmator`) that was drafted here as
"Planned Module Layout (v1.1)" has been **moved to its own dedicated
flow**, `flows/sdd-res-simbox/`, per explicit user request ("все спеки и
reqs что связаны с res-simbox-* перенеси из предыдущего флоу в новый").
See that flow's `02-specifications.md` for the full three-module file
list, the `pvt_start()` cross-module coupling writeup, and the module-
split-specific open design questions (discovery/programmator module-
lifecycle restructuring, `hub-ctrl.c`/`reader/` placement, dead-code
disposition per module).

This flow retains the single source of truth for the underlying file/
function classification above (Full File Inventory, Function-Level
Classification, Header Changes Summary, Build System Changes) — the
`sdd-res-simbox` flow references it rather than duplicating it, so the two
don't drift apart. If you're deciding *what* a piece of legacy code is
(new/modified/unchanged), this document is authoritative; if you're
deciding *which of the three modules* it lands in, see `sdd-res-simbox`.

## Behavior Specifications

### Happy Path (per modified file)

1. Copy the legacy file verbatim into a scratch location (never hand-retype).
2. Diff function-by-function against the upstream file (tables above).
3. For each `UNCHANGED` function: delete its body from the `src/` copy;
   ensure the shared header still declares it so callers resolve to the
   upstream-compiled definition.
4. For each `MODIFIED` function: keep the legacy body verbatim in `src/`.
5. For each `NEW` function: move it out of the host file into its
   companion `_sim.c`/`_svistok.c` file (see table above).

### Edge Cases

| Case | Trigger | Handling |
|---|---|---|
| Function name collision between module and standalone tool (`lock_build`, `lock_create`, `lock_try` in both `chan_dongle.c` and `tools/tty.c`) | Two independent translation units, never linked together | No action needed — they are separate binaries; keep both, no renaming required. |
| `single.c` alternate build mode | Anyone still using `-DBUILD_SINGLE` | Regenerate its `#include` list from the final `src/` layout rather than porting the file's current (stale) content. |
| `#include "file.c"` composition (`select.c`, `dserial.c`, `limits.c`, `share.c`, `stat.c`, `programmator/ttyprog_svistok.c`) | Building the host `.c` file | Preserve the exact same relative-path `#include`, just pointed at the new `src/` location of the included file. |
| Two different `ttyprog_core.c`/`tty_v2.c` variants (top-level/`old/` vs `programmator/`) | Migrating firmware-flashing code | Use only the `programmator/` (live, longer) variant; do not migrate the stale top-level/`old/` copies. |
| `adiscovery_core.c` vs `adiscovery_core_new.c` | Migrating `simnode/` | Use `adiscovery_core.c` (referenced by 2 of 3 entry points); flag `adiscovery_core_new.c` as likely-abandoned for user confirmation before excluding outright. |

*(Module-split-specific edge cases — e.g. the `pvt_start()` cross-module
call — moved to `flows/sdd-res-simbox/02-specifications.md`.)*

## Open Design Questions

- [ ] **Wrapper mechanism for `UNCHANGED` functions.** Two options:
  - **(A) Direct link, no wrapper code** — since these functions are
    already `EXPORT_DECL`/non-static and declared in the shared headers,
    `src/`'s `.o` for e.g. `app.c` simply doesn't define `app_register`, and
    the final link step pulls the symbol from
    `asterisk-chan-dongle`'s compiled `app.o`. Simpler; matches
    requirements criterion 3's letter exactly ("callers ... invoke the
    corresponding function ... directly").
  - **(B) Thin wrapper `.c` files that call through** — matches what the
    sibling `sdd-asterisk-chan-svistok` flow already built (populated
    `src/dongle/*.c` with generated forwarding bodies). More files, but may
    be required if the eventual build only compiles `src/` and does not
    also link objects from `asterisk-chan-dongle/` directly.
  This decision should be made in the Plan phase once the build/link
  strategy for `libsCpp/asterisk-chan-svistok` itself is confirmed (does it
  compile `asterisk-chan-dongle/` as a static lib to link against, or not
  at all?). **This question also applies to `res_simbox_core` in
  `flows/sdd-res-simbox/` — whichever answer is chosen here is inherited
  there.**
- [ ] Confirm disposition of `dsp.c` and `share_mysql.c` (dead code, both
      excluded from the live build via a commented-out `#include`) — exclude
      from `src` entirely, or keep as reference material?
- [ ] Confirm `adiscovery_core_new.c` / `adiscovery_simnode.c` are safe to
      exclude as abandoned experiments.
- [ ] Confirm whether `reader/` (SIM reader/emulator, no build-script or
      module reference found at all) is still in active use anywhere, or
      should be excluded/kept only as reference.
- [ ] Confirm the "one companion file per host" grouping for `NEW`
      functions vs. the feature-based alternative grouping noted above.
- [ ] `channel_tech` losing its `const` qualifier (`channel.h`) — confirm
      this is intentional runtime mutation and not an oversight, since it
      changes a public ABI-ish contract.

*(Module-split-specific open questions — the `pvt_start()` coupling,
discovery/programmator module-lifecycle restructuring — moved to
`flows/sdd-res-simbox/02-specifications.md`.)*

## Testing Strategy

Deferred to Plan phase (this flow inherited no compatible Linux/Asterisk
build environment from the sibling flow either — same constraint applies
here). Recommend, at minimum: a per-file byte-diff assertion that every
`MODIFIED`/`NEW` function body in `src/` matches its legacy source
character-for-character (only deletions/moves allowed, no retyping), and a
link-time symbol check that every `UNCHANGED` function name resolves to
exactly one definition (whichever wrapper strategy is chosen above).

---

## Approval

- [ ] Reviewed by: Anton
- [ ] Approved on:
- [ ] Notes:
