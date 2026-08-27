# Implementation Plan: asterisk-chan-svistok-chan-dongle-v2

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-08-26
> Specifications: [02-specifications.md](02-specifications.md)

## Summary

Populate `libsCpp/asterisk-chan-svistok/src` per the approved
classification: 7 genuinely-new files copied as-is; 4 files trimmed to
modified-only content (with one new-function companion file); 12 files
carried whole (mixed legacy/Svistok authorship, no safe extraction
possible — see specs' Static-Linkage Safety Analysis); build files
carried/regenerated. Every step is copy-then-verify against legacy —
nothing is retyped from memory anywhere in this plan.

## Task Breakdown

### Phase 1: Genuinely-new files (no upstream counterpart)

#### Task 1.1: Copy the 7 already-`#include`d new files
- **Description**: Copy `select.c`, `select.h`, `dserial.c`, `limits.c`,
  `share.c`, `share.h`, `stat.c` verbatim from
  `legacy/asterisk-chan-svistok-v2014/` into
  `libsCpp/asterisk-chan-svistok/src/`. These are 100% Svistok-original
  (no upstream content) — NativeMind copyright header.
- **Files**: 7 new files.
- **Dependencies**: None.
- **Verification**: Byte-diff each against legacy after the header.
- **Complexity**: Low.

#### Task 1.2: Copy the `simnode/` composition (found late, part of the Key Discovery)
- **Description**: Copy `simnode/adiscovery_svistok.c` and
  `simnode/adiscovery_core.c` into `src/simnode/` — required because
  `chan_dongle.c` (Task 3.x) `#include`s
  `"simnode/adiscovery_svistok.c"` directly, and `chan_dongle.c`'s own
  `do_discovery()` thread depends on functions defined in
  `adiscovery_core.c`. NativeMind copyright (100% Svistok-original).
- **Files**: 2 new files under `src/simnode/`.
- **Dependencies**: None (independent of Task 1.1, but required before
  Task 3.x's `chan_dongle.c` copy will actually compile).
- **Verification**: Byte-diff against legacy.
- **Complexity**: Low.

### Phase 2: Trimmed files (the 4 safe cases)

#### Task 2.1: Copy-then-trim `at_read.c`, `dc_config.c`, `helpers.c`, `ringbuffer.c`
- **Description**: For each: copy verbatim from legacy, then delete the
  body of every function classified `UNCHANGED` in
  `02-specifications.md`'s Function-Level Classification, leaving only
  `MODIFIED` functions (and, for `ringbuffer.c`, relocate the one `NEW`
  function per Task 2.2 instead of leaving it in place). Legacy/bg111
  copyright is kept (these files are still a mix of upstream-authored
  surrounding code — types, includes — even though the function bodies
  left behind are Svistok's).
  - `at_read.c`: keep `at_read`, `at_read_result_iov`; delete `at_wait`,
    `at_read_result_classification`.
  - `dc_config.c`: keep `dc_uconfig_fill`, `dc_sconfig_fill`; delete
    `dc_dtmf_setting2str`, `dc_sconfig_fill_defaults`, `dc_gconfig_fill`,
    `dc_config_fill`.
  - `helpers.c`: keep `is_valid_ussd_string`, `send2`, `send_sms`,
    `schedule_restart_event`; delete `is_valid_phone_number`,
    `get_at_clir_value`, `send_ussd`, `send_pdu`, `send_reset`,
    `send_ccwa_set`, `send_at_command`.
  - `ringbuffer.c`: delete all 10 `UNCHANGED` functions; the 1 `NEW`
    function (`rb_read_until_char_after_iov`) goes to Task 2.2, not left
    in place.
- **Files**: `at_read.c`, `dc_config.c`, `helpers.c`, `ringbuffer.c`
  (modified in `src/` after the verbatim copy).
- **Dependencies**: None.
- **Verification**: Per-function byte-diff of every surviving function
  body against legacy; confirm every deleted function's name still
  resolves via `asterisk-chan-dongle`'s header declarations (structural
  check only — no build environment available to link-verify).
- **Complexity**: Medium (4 files, ~25 functions to remove precisely).

#### Task 2.2: Create `ringbuffer_new.c`
- **Description**: Move `rb_read_until_char_after_iov` out of the
  trimmed `ringbuffer.c` into a new `ringbuffer_new.c`. NativeMind
  copyright (function is Svistok-original).
- **Files**: `ringbuffer_new.c` (new).
- **Dependencies**: Task 2.1 (ringbuffer.c trim).
- **Verification**: Byte-diff the function body against legacy; confirm
  it no longer appears in `ringbuffer.c`.
- **Complexity**: Low.

#### Task 2.3: Carry headers for the 4 trimmed files
- **Description**: `dc_config.h`, `ringbuffer.h` are `MODIFIED` (carry in
  full, always — headers aren't trimmed, see specs). `at_read.h`,
  `helpers.h` are IDENTICAL to upstream — **not copied at all**, resolved
  by using `asterisk-chan-dongle`'s copy directly.
- **Files**: `dc_config.h`, `ringbuffer.h`.
- **Dependencies**: None.
- **Verification**: Byte-diff the 2 carried headers against legacy;
  confirm the 2 identical ones are absent from `src/`.
- **Complexity**: Low.

### Phase 3: Carried-whole files (the 12 not-safe-to-trim cases)

#### Task 3.1: Copy the 12 files whole
- **Description**: Copy `app.c`, `at_command.c`, `at_parse.c`,
  `at_queue.c`, `at_response.c`, `chan_dongle.c`, `channel.c`, `cli.c`,
  `cpvt.c`, `manager.c`, `pdiscovery.c`, `pdu.c` verbatim from legacy —
  full content, `MODIFIED` and `UNCHANGED` functions together, no
  deletions. Legacy/bg111 copyright kept (mixed authorship; the
  `chan_dongle.c` precedent already established this rule — extend it to
  all 12).
- **Files**: 12 files.
- **Dependencies**: None.
- **Verification**: Byte-diff each in full against legacy (should be 100%
  identical, unlike the trimmed files).
- **Complexity**: Low (mechanical, but 12 files — budget time
  accordingly).

#### Task 3.2: Carry headers for the 12 carried-whole files
- **Description**: Copy `app.h`, `at_command.h`, `at_parse.h`,
  `at_response.h`, `chan_dongle.h`, `channel.h`, `cli.h`, `cpvt.h`,
  `pdiscovery.h`, `pdu.h` verbatim (all `MODIFIED`, always carried in
  full). `at_queue.h` is IDENTICAL — not copied, resolved via
  `asterisk-chan-dongle` directly.
- **Files**: 10 headers.
- **Dependencies**: None.
- **Verification**: Byte-diff against legacy; confirm `at_queue.h` absent
  from `src/`.
- **Complexity**: Low.

#### Task 3.3: Confirm no-op for `manager.h`
- **Description**: `manager.h` is IDENTICAL to upstream — not copied,
  resolved via `asterisk-chan-dongle` directly (this is the one header
  among the 12 hosts' headers that's actually identical, unlike the other
  9 which are all `MODIFIED`).
- **Files**: None (explicit non-action).
- **Dependencies**: None.
- **Verification**: Confirm absent from `src/`.
- **Complexity**: Low.

### Phase 4: Build files

#### Task 4.1: Carry build files
- **Description**: Copy `configure.in`, `Makefile.in`, `config.h.in`
  verbatim (the object list `chan_donglem_so_OBJS` doesn't need to change
  — same 19 translation units as before, since nothing was removed at
  the file level, only function bodies within some of them).
- **Files**: `configure.in`, `Makefile.in`, `config.h.in`.
- **Dependencies**: None.
- **Verification**: Byte-diff against legacy.
- **Complexity**: Low.

#### Task 4.2: Regenerate `single.c`
- **Description**: `single.c` (the alternate one-translation-unit build
  mode) must reflect the final file list — regenerate its `#include`
  list rather than hand-copying legacy's (which has one stray
  commented-out `//include "share.c"` line not worth preserving as-is).
- **Files**: `single.c`.
- **Dependencies**: Tasks 1.1-3.2 (final file list must be known).
- **Verification**: Confirm the `#include` list matches exactly the
  files produced by Phases 1-3.
- **Complexity**: Low.

### Phase 5: Verification pass

#### Task 5.1: Full structural audit
- **Description**: One consolidated pass: (a) every surviving function
  body in the 4 trimmed files byte-matches legacy; (b) every one of the
  12 carried-whole files is 100% byte-identical to legacy (no accidental
  edits); (c) every genuinely-new file byte-matches legacy after its
  header; (d) copyright rule followed consistently (legacy on
  carried-whole/trimmed files, NativeMind on genuinely-new files); (e)
  `src/dongle/` remains empty (per specs, no file qualifies); (f) the 4
  IDENTICAL-to-upstream headers/sources not copied (`at_read.h`,
  `helpers.h`, `at_queue.h`) are confirmed absent.
- **Files**: None (audit).
- **Dependencies**: All prior phases.
- **Verification**: Written audit note in `04-implementation-log.md`.
- **Complexity**: Medium.

## Dependency Graph

```
Task 1.1 ──┐
Task 1.2 ──┼──→ Task 4.2 (single.c needs final file list)
Task 2.1 ──┼──→ Task 2.2 ──┘
Task 2.3 ──┤
Task 3.1 ──┼──→ Task 3.2 ──→ Task 3.3
Task 4.1 ──┘

All of the above ──→ Task 5.1 (final audit)
```

## File Change Summary

| Category | Files | Copyright |
|---|---|---|
| Genuinely new | `select.c/.h`, `dserial.c`, `limits.c`, `share.c/.h`, `stat.c`, `simnode/adiscovery_svistok.c`, `simnode/adiscovery_core.c` (9) | NativeMind |
| Trimmed | `at_read.c`, `dc_config.c/.h`, `helpers.c`, `ringbuffer.c/.h` (6) | Legacy/bg111 |
| New companion (from trimmed) | `ringbuffer_new.c` (1) | NativeMind |
| Carried whole | `app.c/.h`, `at_command.c/.h`, `at_parse.c/.h`, `at_queue.c`, `at_response.c/.h`, `chan_dongle.c/.h`, `channel.c/.h`, `cli.c/.h`, `cpvt.c/.h`, `manager.c`, `pdiscovery.c/.h`, `pdu.c/.h` (22) | Legacy/bg111 |
| Build files | `configure.in`, `Makefile.in`, `config.h.in`, `single.c` (regenerated) (4) | Legacy (unmodified) / N/A |
| Not copied (link to upstream) | `at_read.h`, `helpers.h`, `at_queue.h`, `manager.h` (4) | N/A |

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Manual per-function deletion (Task 2.1, ~25 functions across 4 files) introduces a transcription error | Low-Medium | High | Byte-diff verification per surviving function is mandatory, not optional |
| `single.c` regeneration (Task 4.2) drifts from the actual file set if Phase 5 finds something later | Low | Medium | Task 4.2 explicitly depends on all prior phases completing first |
| No real compiler/linker available to verify the trimmed files actually link against `asterisk-chan-dongle` correctly | High (environment limitation) | Medium | Structural verification only, consistent with every prior flow in this family; flag clearly, don't claim more confidence than warranted |

## Rollback Strategy

1. Everything created lives under `libsCpp/asterisk-chan-svistok/src/`
   (already has content from the sibling `sdd-asterisk-chan-svistok`
   flow — **this plan does not touch or overwrite that flow's existing
   files**; new/changed content from this plan should be reviewed against
   what's already there before writing, and any real conflict flagged
   rather than silently overwritten).
2. `legacy/` and `libsCpp/asterisk-chan-svistok/asterisk-chan-dongle/`
   are never written to — always available to re-derive from.

## Checkpoints

- [ ] Every trimmed file's surviving functions byte-match legacy
- [ ] Every carried-whole file is 100% byte-identical to legacy
- [ ] Every genuinely-new file byte-matches legacy after its header
- [ ] Copyright rule applied consistently
- [ ] `src/dongle/` empty
- [ ] `single.c` regenerated, not hand-copied

## Open Implementation Questions

- [ ] `libsCpp/asterisk-chan-svistok/src/` already has extensive content
      from the sibling `sdd-asterisk-chan-svistok` flow (different
      files/approach — AST-slicing with bridges, `src/dongle/`,
      `src/svistok/`, `src/programmator/`, `src/simnode/` subdirs
      already populated). This plan's file names may collide with
      existing files there. **Must check before writing any file in
      Phases 1-4** — if a name collision exists, stop and ask rather
      than overwrite silently (this was flagged as an open question in
      Requirements and never explicitly resolved: reconcile vs.
      independent output).

---

## Approval

- [x] Reviewed by: Anton
- [x] Approved on: 2026-08-26
- [x] Notes: approved as drafted.
