# File Inventory: asterisk-chan-svistok

> Version: 1.0  
> Status: APPROVED  
> Last Updated: 2026-08-25  
> Requirements: [01-requirements.md](01-requirements.md)

## Comparison Basis

- Legacy tree (strictly read-only):
  `legacy/asterisk-chan-svistok-v2014`
- Baseline tree:
  `libsCpp/asterisk-chan-svistok/asterisk-chan-dongle`
- Baseline commit:
  `ab939532c71b991de2f66582d7ee2c553b6a918e`
- Legacy commit:
  `1b358acd5ea29f1c10aebb9f1ed82246c52cdaed`
- Comparison is path-sensitive and byte-for-byte for regular files.
- `NEW` means the path exists in legacy and does not exist in the selected
  baseline. It does not by itself claim that a generated artifact was authored
  manually.
- `MODIFIED` means the same path exists in both trees and bytes differ.
- `IDENTICAL` means the same path exists in both trees and bytes match.
- Git administrative data under `.git/` is excluded.

## Inventory Totals

| Set | New | Modified | Identical | Total |
|---|---:|---:|---:|---:|
| Final-module source closure | 12 | 28 | 12 | 52 |
| Outside final-module source closure, regular files | 85 | 4 | 15 | 104 |
| Outside closure, generated symlinks | 5 | 0 | 0 | 5 |
| Entire legacy tree | 102 entries | 32 | 27 | 161 entries |

The 102 new entries consist of 97 regular files and 5 symlinks. The baseline
also has one path absent from legacy: `README.txt`.

## Final-Module Source Closure — Copy or Reuse

The closure starts with the 19 objects linked into `chan_dongle.so` by the
legacy `Makefile`, maps each object to its `.c` source, and recursively follows
project-local quoted includes. Generated `config.h` is tracked as a build
input, not as a source to copy.

### NEW — copy into `src` (12)

These project-specific files have no same-path counterpart in the baseline:

```text
dserial.c
limits.c
programmator/crc.c
programmator/ttyprog_core.c
programmator/ttyprog_svistok.c
select.c
select.h
share.c
share.h
simnode/adiscovery_core.c
simnode/adiscovery_svistok.c
stat.c
```

### MODIFIED — copy verbatim first, then adapt (28)

```text
app.c
app.h
at_command.c
at_command.h
at_parse.c
at_parse.h
at_queue.c
at_read.c
at_response.c
at_response.h
chan_dongle.c
chan_dongle.h
channel.c
channel.h
cli.c
cli.h
cpvt.c
cpvt.h
dc_config.c
dc_config.h
helpers.c
manager.c
pdiscovery.c
pdiscovery.h
pdu.c
pdu.h
ringbuffer.c
ringbuffer.h
```

### IDENTICAL — reuse directly from baseline; do not copy (12)

```text
at_queue.h
at_read.h
char_conv.c
char_conv.h
export.h
helpers.h
manager.h
memmem.c
memmem.h
mixbuffer.c
mixbuffer.h
mutils.h
```

## Complete DO NOT COPY Inventory (109)

Every entry below is outside the final-module source closure. This section is
the authoritative exclusion manifest: none of these entries may be copied to
`libsCpp/asterisk-chan-svistok/src`.

### NEW paths outside the module (85 regular files)

```text
1
2
3
CONF!!!!!!!!!!!
LICENSE
Makefile
README.md
README_ru.md
aclocal.m4
at_command.o
at_queue.o
at_read.o
at_response.o
autom4te.cache/requests
chan_dongle.h.gch
chan_dongle.o
channel.o
cli.o
config.h
config.log
config.log.orig
config.log.orig.orig
config.status
configure
contrib/openwrt/.svn/all-wcprops
contrib/openwrt/.svn/entries
contrib/openwrt/asterisk16-chan-dongle/.svn/all-wcprops
contrib/openwrt/asterisk16-chan-dongle/.svn/entries
contrib/openwrt/asterisk16-chan-dongle/.svn/text-base/Makefile.svn-base
contrib/openwrt/asterisk18-chan-dongle/.svn/all-wcprops
contrib/openwrt/asterisk18-chan-dongle/.svn/entries
contrib/openwrt/asterisk18-chan-dongle/.svn/text-base/Makefile.svn-base
cpvt.o
d
dsp.c
hub-ctrl.c
list
list2
make.sh
md.sh
old/tty_v2.c
old/ttyprog_core.c
old/ttyprog_programmator.c
old/ttyprog_svistok.c
old/ttyprog_test.c
pdiscovery.o
prog.sh
programmator/111
programmator/a.out
programmator/addons.c
programmator/fuall.sh
programmator/fupdate3.sh
programmator/fupdate4.sh
programmator/programmator
programmator/tty_v2.c
programmator/ttyprog_programmator.c
programmator/ttyprog_test.c
programmator/updateall2.sh
programmator/updateall3.sh
reader/ada
reader/adapter.c
reader/emu
reader/emulator.c
reader/g.sh
reader/old/comport.pas
reader/old/copy.c
reader/old/test.c
reader/reader_core.c
reader/reader_core.h
share_mysql.c
share_mysql.h
simnode/a.out
simnode/adiscovery_core_new.c
simnode/adiscovery_simnode.c
simnode/adiscovery_test.c
stamp-h1
todo
tty_v2.c
ttyprog_core.c
ttyprog_programmator.c
ttyprog_svistok.c
ttyprog_test.c
update.sh
upgrade.sh
upgrade_prog.sh
```

The list above includes human-authored standalone sources as well as generated
or non-source artifacts. Known generated/artifact subsets include object files
(`*.o`), `chan_dongle.h.gch`, ELF binaries under `programmator/`, `reader/`, and
`simnode/`, Autotools output/cache files, and `.svn/` metadata. Their `NEW`
classification records absence from the baseline path; it does not authorize
copying them.

### MODIFIED paths outside the module (4)

```text
Makefile.in
configure.in
single.c
tools/tty.c
```

### IDENTICAL paths outside the module (15)

```text
BUGS
COPYRIGHT.txt
INSTALL
LICENSE.txt
TODO.txt
config.h.in
contrib/openwrt/asterisk16-chan-dongle/Makefile
contrib/openwrt/asterisk18-chan-dongle/Makefile
etc/dongle.conf
etc/extensions.conf
stamp-h.in
test/parse.c
test/test1.c
tools/discovery.c
tools/tty.h
```

### Generated symlinks outside the module (5)

```text
compile -> /usr/share/automake-1.15/compile
config.guess -> /usr/share/automake-1.11/config.guess
config.sub -> /usr/share/automake-1.11/config.sub
install-sh -> /usr/share/automake-1.11/install-sh
missing -> /usr/share/automake-1.11/missing
```

## Baseline-Only Path

The following baseline file has no same-path legacy counterpart. It is not a
legacy migration source:

```text
README.txt
```

## Transitive Inclusion Evidence

These non-obvious `.c` inclusion chains explain why selected subproject files
are in the final module:

```text
cli.c
  -> share.c
  -> stat.c
  -> programmator/ttyprog_svistok.c
       -> programmator/ttyprog_core.c
            -> programmator/crc.c

chan_dongle.c
  -> simnode/adiscovery_svistok.c
       -> simnode/adiscovery_core.c
  -> select.c

at_response.c
  -> dserial.c
  -> limits.c
```

No source under `reader/` or `old/` is reachable from the final module's source
closure.

## Verification Invariants

1. The 52 included paths and 109 excluded paths partition all 161 legacy tree
   entries outside `.git/`.
2. The exclusion manifest is checked before and after migration; intersection
   between copied source paths and the exclusion manifest must be empty.
3. Every modified file must first have a recorded SHA-256-identical copy in
   `src` before adaptation.
4. Legacy and baseline Git worktrees must remain clean.

## Final Function Layout (2026-08-26)

The machine-readable authority, including destinations and body hashes, is
`libsCpp/asterisk-chan-svistok/manifests/function-layout.json`.

### New functions moved below `src/svistok` (45)

- `at_command.c`: `at_enque_cfun1`, `at_enque_cfun5`, `at_enque_cfun6`, `at_enque_cfun_v`, `at_enque_cmd_proc`, `at_enque_cpin_v`, `at_enque_iccid`, `at_enque_initialization_modem`, `at_enque_initialization_sim`, `at_enque_initialization_sim_e`, `at_enque_initialization_sim_mb`, `at_enque_sn`, `at_enque_spn`, `at_enque_sysinfo`
- `at_parse.c`: `at_parse_cds`, `at_parse_spn`, `at_parse_sysinfo`
- `at_queue.c`: `at_log`
- `at_response.c`: `at_response_cardlock`, `at_response_cds`, `at_response_cfun_v`, `at_response_cvoice`, `at_response_dsflowrpt`, `at_response_freqlock`, `at_response_iccid`, `at_response_simst`, `at_response_sn`, `at_response_spn`, `at_response_srvst`, `at_response_sysinfo`, `at_response_unknown`
- `chan_dongle.c`: `ast_channel_get_var`, `ast_channel_show_vars`, `can_sms`
- `cli.c`: `cli_changeimei`, `cli_diagmode`, `cli_dongle_update`, `cli_setgroup`, `cli_setgroupimsi`, `cli_show_devicesd`, `cli_show_devicesi`, `cli_show_devicesl`
- `pdiscovery.c`: `pdiscovery_handle_sn`
- `pdu.c`: `pdu_parse_cds`
- `ringbuffer.c`: `rb_read_until_char_after_iov`

### False-modified functions returned directly to baseline (6)

- `chan_dongle.c`: `closetty`, `lock_try`
- `channel.c`: `iov_write`
- `cpvt.c`: `init_pipe`
- `pdiscovery.c`: `pdiscovery_do_cmd`, `pdiscovery_list_begin`

### Hook/proxy compositions below `src/dongle` (14)

- `at_parse.c`: `at_parse_cpin`
- `at_queue.c`: `at_write`
- `at_response.c`: `at_response_cgmi`, `at_response_cgmr`, `at_response_cgsn`, `at_response_cimi`, `at_response_cops`, `at_response_csq`, `at_response_mode`, `at_response_rssi`
- `chan_dongle.c`: `load_module`
- `cli.c`: `getACD`
- `pdiscovery.c`: `info_copy`, `info_free`

### Retained inseparable modified functions (87)

- `app.c`: `app_status_exec`
- `at_command.c`: `at_enque_cops`, `at_enque_dial`, `at_enque_hangup`, `at_enque_initialization`, `at_enque_pdu`, `at_enque_sms`, `at_enque_ussd`
- `at_command.h`: `at_cmd2str`
- `at_read.c`: `at_read`, `at_read_result_iov`
- `at_response.c`: `at_response`, `at_response_cend`, `at_response_cgmm`, `at_response_clcc`, `at_response_cmgr`, `at_response_conn`, `at_response_cpin`, `at_response_creg`, `at_response_cusd`, `at_response_error`, `at_response_ok`, `at_response_ring`, `start_pbx`
- `chan_dongle.c`: `disconnect_dongle`, `do_discovery`, `do_monitor_phone`, `find_device_ex`, `find_device_ext`, `lock_build`, `lock_create`, `opentty`, `public_state_fini`, `public_state_init`, `pvt_create`, `pvt_destroy`, `pvt_discovery`, `pvt_dsp_setup`, `pvt_free`, `pvt_reconfigure`, `pvt_start`, `pvt_state_base`, `pvt_stop`, `pvt_str_state`, `pvt_str_state_ex`, `pvt_time4restate`, `ready4voice_call`, `reload_config`, `rssi2dBm`
- `channel.c`: `change_channel_state`, `channel_answer`, `channel_call`, `channel_devicestate`, `channel_digit_begin`, `channel_fixup`, `channel_func_read`, `channel_func_write`, `channel_hangup`, `channel_indicate`, `channel_read`, `channel_request`, `channel_write`, `channels_loop`, `new_channel`, `queue_hangup`, `set_channel_vars`, `start_local_channel`
- `cli.c`: `cli_show_device_settings`, `cli_show_device_state`, `cli_show_device_statistics`, `cli_show_devices`, `cli_sms`
- `dc_config.c`: `dc_sconfig_fill`, `dc_uconfig_fill`
- `helpers.c`: `is_valid_ussd_string`, `schedule_restart_event`, `send2`
- `manager.c`: `manager_register`, `manager_show_devices`
- `pdiscovery.c`: `cache_lookup`, `pdiscovery_check_req`, `pdiscovery_get_info`, `pdiscovery_handle_response`, `pdiscovery_lookup`
- `pdu.c`: `pdu_build`, `pdu_parse`, `pdu_parse_number`

The six proxy files are `src/dongle/at_parse.c`, `at_queue.c`,
`at_response.c`, `chan_dongle.c`, `cli.c`, and `pdiscovery.c`; matching hook
files use the same names below `src/svistok/hooks`. Empty root shells
`at_parse.c`, `at_queue.c`, `ringbuffer.c`, and `cpvt.c` are not copied into the
final layout.
