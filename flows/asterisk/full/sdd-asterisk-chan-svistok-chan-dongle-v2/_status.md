# Status: sdd-asterisk-chan-svistok-chan-dongle-v2

## Current Phase

IMPLEMENTATION

## Phase Status

HALTED BY AUDIT — the approved plan is not being executed. A pre-write
collision check found the sibling `sdd-asterisk-chan-svistok` flow's
existing `libsCpp/asterisk-chan-svistok/src/` is a complete, working,
more sophisticated solution (code-generated bridges solving the exact
static-linkage problem this flow's plan could only work around). A full
function-by-function audit against it found zero genuine content gaps.
See "Audit Findings" below. No files were written under
`libsCpp/asterisk-chan-svistok/` by this flow.

## Last Updated

2026-08-26 by Claude

## Blockers

None. Open design questions listed in `02-specifications.md` should be
resolved before/alongside approval, per usual — none are hard blockers.

## Progress

- [x] Requirements drafted (restart of v1's scope, module-split content
      excluded)
- [x] Requirements approved (2026-08-26)
- [x] Specifications drafted (classification carried forward from v1 +
      new Static-Linkage Safety Analysis + revised single-module
      `src/` file list + concrete `<host>_new.c` companion naming)
- [x] Specifications approved (2026-08-26)
- [x] Plan drafted (2026-08-26)
- [ ] Plan approved
- [ ] Implementation started
- [ ] Implementation complete

## Context Notes

- User instruction that triggered this restart (2026-08-26, while resuming
  v1): "тебе в рамках задачи нужно вернуться только к оригинальной папке
  libsCpp/asterisk-chan-svistok и первоначальной задаче, остальное -
  больше не твоя зона ответственности" (return only to the original
  `libsCpp/asterisk-chan-svistok` folder and the original task; the rest
  — everything under `res-simbox-*`/`sdd-res-simbox` — is no longer your
  responsibility). This came right after a finding (in the now-out-of-
  scope res-simbox work) that core's own `do_discovery()` thread
  duplicates `res_simbox_discovery`'s standalone daemon — the user
  redirected away from resolving that rather than asking me to fix it.
- Then, asked what to actually do in `libsCpp/asterisk-chan-svistok`
  (implement fresh vs. validate the sibling flow's existing output vs.
  something else), user said: `/sdd new sdd-asterisk-chan-svistok-chan-dongle-v2`
  — a clean restart rather than continuing v1 (whose history is tangled
  up with the module-split detour) or auditing the sibling's output.
- **What was carried forward from v1** (all still valid, not redone):
  the full independent file/function classification — Full File
  Inventory, Function-Level Classification (~380 functions across 17
  files), Header Changes Summary, Build System Changes, the
  `#include "file.c"` composition discovery (now including the
  `chan_dongle.c`↔`simnode/adiscovery_svistok.c` one, found later than
  v1's original pass, added here for completeness even though its
  *placement* decision belongs to the out-of-scope flow).
- **What's new in v2, not in v1's original (pre-module-split) specs**:
  the **Static-Linkage Safety Analysis** — the empirical finding (made
  while implementing the out-of-scope module split against this same
  codebase) that naive "delete every UNCHANGED function" breaks on
  `static`-linkage functions still referenced by surviving code, and that
  this affects 12 of 16 module `.c` files, not an edge case. v1's
  original single-module plan (before it pivoted to the module split)
  never incorporated this lesson because the lesson didn't exist yet —
  v2 is not a naive copy of that old plan, it's corrected with real
  evidence.
- **Consequence for the `src/` file list**: only 4 files
  (`at_read.c`, `dc_config.c`, `helpers.c`, `ringbuffer.c`) can be safely
  trimmed to modified-only content. The other 12 are planned as
  carry-whole (full legacy content, legacy/bg111 copyright kept, `NEW`
  functions staying in place rather than being extracted to companion
  files) — a direct, logged consequence, not a shortcut.
- This flow does **not** read, reference, or touch anything under
  `libsCpp/asterisk-res-simbox-*/` or `flows/sdd-res-simbox/` going
  forward.

## Fork History

Not forked — a deliberate clean restart of
`flows/asterisk-chan-svistok/sdd-asterisk-chan-svistok-chan-dongle/`
("v1"), reusing its classification content, dropping its module-split
direction.

## Audit Findings (2026-08-26)

Before writing anything, per the plan's own flagged risk, checked
`libsCpp/asterisk-chan-svistok/src/` for collisions. Found the sibling
flow's output occupies nearly every path this flow's plan targeted, using
a fundamentally different (and more capable) mechanism:

- `svistok/<file>.c` — real Svistok-only (`NEW`) implementations
- `dongle/<file>.c` — generated proxy/hook wrappers for specific
  `MODIFIED` functions
- top-level `<file>.c` — the `MODIFIED` functions themselves, with
  generated `extern svistok_bridge_upstream_*` declarations resolving
  calls into upstream baseline objects/constants
- `svistok_abi.h`, `svistok_state.c` — their own generated ABI contract
  and canonical-storage relocation for header tentative definitions
- A full `tools/`+`tests/`+`build/` pipeline that reportedly builds and
  link-audits the result end to end (per that flow's own status notes)

This is a working, tested solution to the exact static-linkage problem
that forced this flow's plan into a "carry-whole" compromise for 12 of 16
files. Their manifest counts (28 modified / 12 new / 12 identical) align
closely with this flow's independent classification — good mutual
validation despite completely different methodologies.

**Full function-level audit** (every `MODIFIED`+`NEW` function from this
flow's classification, ~130 across 16 files, checked for a real
definition anywhere in their tree, not just file/path presence): found
exactly 4 apparent absences — `at_enque_set_ccwa`, `at_enque_reset`
(`at_command.c`), `send_sms` (`helpers.c`), `cpvt_alloc` (`cpvt.c`).
Direct diff of each against upstream found **all four differ only in
comment style or blank lines — zero behavioral difference**. The sibling
flow evidently ran a whitespace/comment-insensitive diff and correctly
excluded these as non-substantive; this flow's byte-level `func_diff.py`
classification does not distinguish cosmetic from behavioral differences
and over-counted these four as `MODIFIED`. This is why `cpvt.c` doesn't
exist in their tree at all — once `cpvt_alloc` is correctly excluded,
`cpvt.c` has no real content of its own.

**Conclusion**: no genuine gaps. `libsCpp/asterisk-chan-svistok/src/` is
complete and, in these four spots, more precise than this flow's own
classification. Recommend against writing anything there — this flow's
remaining value is the independent classification itself (now
additionally refined by this audit), not a competing file tree.

**Correction owed to this flow's own `02-specifications.md`**: the
Function-Level Classification should note `at_enque_set_ccwa`,
`at_enque_reset`, `send_sms`, `cpvt_alloc` as cosmetically-only different
(effectively `UNCHANGED` in behavior), not left as plain `MODIFIED`
without qualification. Not yet corrected in that document — flagging here
first.

## Plan Drafted (2026-08-26)

5 phases: (1) 9 genuinely-new files including the newly-found
`simnode/adiscovery_svistok.c`+`adiscovery_core.c` composition, (2) the 4
safe-to-trim files + `ringbuffer_new.c`, (3) the 12 carried-whole files +
their headers, (4) build files (`configure.in`/`Makefile.in`/`config.h.in`
carried, `single.c` regenerated), (5) a full structural audit.

**One important open item flagged in the plan itself, not resolved**:
`libsCpp/asterisk-chan-svistok/src/` already has extensive content from
the sibling `sdd-asterisk-chan-svistok` flow (different approach —
AST-slicing/bridges, already has `src/dongle/`, `src/svistok/`,
`src/programmator/`, `src/simnode/` subdirs populated). This plan's file
names may collide with what's already there. Before executing Phases
1-4, must check for collisions and stop to ask rather than overwrite
silently — this is the same "reconcile vs. independent output" question
v1's requirements raised and never resolved, now actually load-bearing
since implementation is about to start.

## Next Actions

1. Get "plan approved."
2. **Before any file write**: check `libsCpp/asterisk-chan-svistok/src/`
   for name collisions with this plan's file list; if found, stop and
   ask how to reconcile rather than overwriting.
3. Execute Phases 1-5 in order.
