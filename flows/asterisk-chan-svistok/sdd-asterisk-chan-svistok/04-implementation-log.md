# Implementation Log: asterisk-chan-svistok

> Started: 2026-08-25  
> Plan: [03-plan.md](03-plan.md)

## Progress Tracker

| Task | Status | Notes |
|---|---|---|
| 0.1 Source identities/guards | Done | Commits, counts, cleanliness verified |
| 0.2 Automated inventory | Done | 52 included / 109 excluded reproduced |
| 1.x Legacy characterization | Done | Checkpoint 1 passed; 7 golden fixtures |
| 2.x AST slicing toolchain | Done | Checkpoint 2 passed; complete ownership manifest |
| 3.x Exact copy migration | Done | Checkpoint 3 passed; 40 matching receipts |
| 4.x Header/ABI integration | Done | Explicit ownership, ABI, config verified |
| 5.x Full function slicing | Done | 32 slices, 81 hidden bridges |
| 6.x Build composition | Done | Host compatibility `chan_svistok.so` linked |
| 7.x Final parity/audit | Done | 25 available check groups passed; T3/T4 gaps recorded |
| 8.x Expected-red purity gate | Done | Reproduced equivalent bodies physically present in old `src` |
| 9.x Physical overlay extraction | Done | 380 upstream units removed from all 28 modified paths |
| 10.x Promotion/build rewiring | Done | 16 baseline slices + 16 non-filtering overlay compositions |
| 11.x Corrected parity/audit | Done | 28 available check groups passed; T3/T4 gaps unchanged |

## Session Log

### Session 2026-08-25 — Codex

**Started at**: Phase 0, Task 0.1  
**Context**: Requirements, specifications, inventory, and plan approved.

#### Completed

- SDD transitioned to IMPLEMENTATION.
- Confirmed target `src` was empty at implementation start.
- Confirmed legacy and baseline worktrees were clean at implementation start.
- Task 0.1: added source baseline manifest and guard; isolated test passed.
- Task 0.2: added reproducible inventory and exclusion manifest; isolated test
  passed with 19 root units, 52 included, and 109 excluded.
- Checkpoint 0 passed with `src` empty and both source worktrees clean.
- Task 2.1: generated a Clang JSON-AST ownership manifest for all 28 modified
  paths: 420 root definitions, 147 macros, 139 definitions from ten directly
  included new `.c` paths, and zero unowned live entries.
- Task 2.2: syntax-aware dual slicing tests passed for equivalent, modified,
  new, removed, recursive `.c` include, macro, and conditional cases.
- Task 2.3: static calls and mutable state passed both-direction bridge tests.
  One variadic static bridge uses a hidden link-time alias, preserving the
  upstream bodies and the complete variadic argument list without forwarding
  through a generated C wrapper.
- Task 2.4: provenance tests reject edited and owner-swapped bodies.
- Task 2.5: composed `at_parse.c` slices compiled and matched the pre-copy
  legacy golden output.
- Checkpoint 2 passed with `src` empty and both source worktrees clean.
- Tasks 3.1–3.3: mechanically copied exactly 12 NEW and 28 MODIFIED paths
  from legacy into `src`; all 40 source/destination SHA-256 pairs match.
- Checkpoint 3 passed: all 12 IDENTICAL module paths and all 109 `DO NOT COPY`
  paths are absent from `src`; both source worktrees remain clean.
- Tasks 4.1–4.3: adapted includes to explicit local/upstream ownership, added
  the canonical `svistok_abi.h` contract, generated `svistok_config.h`, and
  verified both slice contexts plus a deliberately broken ABI case.
- Relocated four legacy header tentative definitions to one
  `svistok_state.c` storage owner, preserving names/types/zero initialization
  and allowing the complete build to use `-fno-common`.
- Tasks 5.1–5.3: generated 32 build-only slices for 16 modified roots,
  preserved all owner body hashes, compiled 36 total objects, and checked 296
  external symbols against their assigned object owner.
- Corrected Clang AST normalization to discard process-local declaration IDs;
  the stable manifest classifies 222 equivalent, 112 modified, 84 new, and
  two removed root definitions, with 81 required bridges.
- Tasks 6.1–6.3: replaced stale build wiring, linked `chan_svistok.so`, proved
  zero unresolved/public bridge symbols, and documented production and
  compatibility build commands in both READMEs.
- Tasks 7.1–7.4: all nine legacy oracle groups passed again; migrated PDU,
  AT parser, buffer, and AT-read compositions match frozen golden outputs.
  The final audit records 25 passing check groups.
- T3 Asterisk load/unload and T4 discovery/call/SMS/USSD/programmer hardware
  execution remain explicit external-environment gaps, not false passes.

#### In Progress

- None.

#### Deviations from Plan

- Added `build/` to the target `.gitignore` during Task 1.1 rather than Task
  6.1 because the pre-copy oracle harness already produces build-only objects.
- Added one target-owned state translation unit because the legacy header had
  four tentative definitions; a single owner is required by the approved ABI
  and bridge model.
- Expanded the declaration manifest after full compilation exposed a static
  forward declaration and an inline-struct data definition. Both are now
  handled by AST source ranges rather than text matching.

#### Discoveries

- The minimal host environment can execute complete legacy `at_queue.c` and
  `stat.c` translation units with target-owned ABI/recorder stubs. This added
  real queue and call-state transition coverage without filesystem or device
  writes.
- Legacy CUSD parsing and ringbuffer cross-boundary search have surprising but
  stable behavior; fixtures intentionally preserve it rather than fixing it.
- Full `limits.c`/`share.c`/`select.c`, discovery, serial programming, and
  Asterisk module scenarios require production Asterisk/Linux/device state and
  are explicitly recorded as T3/T4 gaps in
  `manifests/effective-legacy-config.json`.
- Clang JSON contains process-local `referencedMemberDecl` and related IDs;
  excluding these metadata fields changed many false-positive modifications
  into 110 additional correctly upstream-owned equivalent definitions.

**Ended at**: Phase 7 complete  
**Handoff notes**: Implementation and all host-available checks are complete.
Run the documented T3/T4 scenarios in Linux/Asterisk with supported hardware.

### Session 2026-08-25 — Requirements correction

- User clarified that final `src` must physically contain only new and modified
  source-level units; excluding equivalent bodies only in generated build
  slices is insufficient.
- Requirements advanced to version 1.3 and the SDD flow was reopened at the
  REQUIREMENTS approval gate.
- At that checkpoint, the existing implementation was recorded as
  nonconforming pending corrective specifications and plan. No corrective
  source changes were made before the renewed approvals.
- The concrete violation at that checkpoint was `app_register()`: manifest
  ownership marked it equivalent/upstream-owned while its body remained in
  `src/app.c`.
- Requirements 1.3 were explicitly approved. Specifications 1.2 were drafted
  with physical AST extraction of final overlay sources and direct compilation
  of those sources; no corrective code changes were started.
- Specifications 1.2 were explicitly approved. Corrective plan 1.2 was drafted
  with an expected-red purity gate, complete 28-file staging validation,
  atomic promotion, build rewiring, and parity/final-audit gates. No corrective
  production-source changes were started.
- Corrective plan 1.2 was explicitly approved. Corrective implementation
  entered Phase 8; production `src` remains unchanged until the expected-red
  purity gate is established.

### Session 2026-08-25 — Corrective implementation

- Added an expected-red physical-overlay test which identified
  `app_register()` and the remaining equivalent definitions in the copied
  modified sources.
- Extended ownership classification to header type units: 44 total, comprising
  30 equivalent, 13 modified, and one new type.
- Mechanically extracted 380 upstream-owned units from staged copies of all 28
  modified paths: 214 C definitions/declarations and 166 header
  declarations/types/macros/functions.
- Promoted the complete staged set atomically after purity, provenance, build,
  ABI, bridge, inventory, and golden checks passed. Pre-promotion content and
  hashes are retained below `build/corrective-backup` and in
  `manifests/overlay-promotion.json`.
- Rewired generation to emit 16 baseline slices and 16 non-filtering overlay
  compositions. Physical `src` delta files are included without a second
  filtering pass; build-only headers substitute baseline-owned header units
  directly from `asterisk-chan-dongle`.
- Verified `app_register()` is absent from the overlay object and defined under
  its original name by the baseline object. The complete object audit checks
  296 public symbols with zero ownership errors; all 81 required static bridges
  remain hidden.
- Built `chan_svistok.so` from 36 objects and replayed all available golden
  tests. The corrected final audit passed 28 sequential groups, followed by all
  test-discovery groups (11 top-level, 14 slicer, 9 characterization, and 3
  migrated tests).
- Recorded the two required include-only adaptations in otherwise-new
  `limits.c` and `share.c` separately from the original exact-copy receipts.
- T3/T4 Linux/Asterisk/hardware scenarios remain external-environment gaps.

### Session 2026-08-26 — Function/layout correction requested

- User requested physical separation of functions absent from dongle, safe
  decomposition of modified dongle functions into Svistok hooks plus direct
  baseline calls, and relocation of proxy-only files to `src/dongle`.
- Reopened the SDD flow at REQUIREMENTS and drafted version 1.4. No production
  source or build code was changed before renewed approvals.
- Preliminary read-only ownership inspection found 45 `new` functions across
  nine mixed modules. A source-line similarity check also found definitions
  currently labelled modified whose definition text is fully baseline-
  equivalent; the revised specification must re-audit these false positives.
- Requirements 1.4 were explicitly approved by the user. The flow advanced to
  SPECIFICATIONS; production source remains unchanged.
- Drafted specifications 1.3 with the complete function partition: 45 new
  definitions move to nine `src/svistok` module files; six false-modified
  definitions return directly to baseline; fourteen functions use six
  proxy-only `src/dongle` fragments plus six hook files; 87 inseparable
  modified definitions remain whole with per-module reason classes.
- Specifications 1.3 were explicitly approved by the user. The flow advanced
  to PLAN; production source remains unchanged.
- Drafted plan 1.3 as Phases 12–16: expected-red layout gates; staged new
  function extraction; six direct-baseline and fourteen hook/proxy
  compositions; complete staged validation and atomic promotion; parity,
  documentation, and final audit. No production source was changed.
- Plan 1.3 was explicitly approved by the user. Implementation entered Phase
  12; production source remains unchanged until the staged layout passes.

### Session 2026-08-26 — Function/layout implementation complete

- Froze the deterministic 45 new / 6 direct-baseline / 14 hook-proxy / 87
  inseparable function partition in `manifests/function-layout.json`.
- Added expected-red physical-path coverage, then generated the complete
  candidate tree under `build/staging-function-layout/src` without editing
  legacy or the supplied chan_dongle checkout.
- Moved all 45 new definitions into nine `src/svistok/*.c` fragments while
  preserving their legacy body hashes. Returned six false-modified bodies to
  their original baseline definitions.
- Created six `src/dongle/*.c` proxy-only fragments and six matching
  `src/svistok/hooks/*.c` fragments for 14 safely decomposed functions. Each
  proxy has exactly one hidden pristine `svistok_dongle_impl_*` call; source
  and runtime success/error ordering checks cover all 14.
- Extended non-filtering composition with early private prototypes and the
  baseline dependency bridges needed by hidden pristine entries. The final
  compatibility module is `chan_svistok.so`, built from 35 objects with 83
  hidden bridges and 14 hidden baseline entries.
- Removed empty root shells `at_parse.c`, `at_queue.c`, `ringbuffer.c`, and
  `cpvt.c`. The first three retain their necessary translation-unit preamble
  in their Svistok fragment; `cpvt.c` has no overlay-side unit left.
- Moved 23 external new-only declarations into six
  `src/svistok/<module>.h` headers and routed compatibility headers to them;
  static helpers remain private to their original logical translation units.
- Promoted the verified 65-file staging tree as one set after creating
  `build/function-layout-backup/src`. Promotion evidence is recorded in
  `manifests/function-layout-promotion.json`; extraction is reproducible from
  that frozen pre-promotion backup.
- The second corrected final audit passed 33 sequential host-available checks.
  Independent discovery passed 11 top-level, 14 slicer, 9 characterization,
  3 migrated, and 5 layout tests. Legacy and baseline source guards remained
  clean. T3/T4 Linux/Asterisk/hardware checks remain explicit external gaps.

## Deviations Summary

| Planned | Actual | Reason |
|---|---|---|
| Ignore `build/` during Task 6.1 | Ignored during Task 1.1 | Characterization outputs are build-only and existed before build composition |
| Header tentative state remains common | Four definitions relocated to `svistok_state.c` | Enforces one mutable storage owner and `-fno-common` |
| Declaration handling implicit in definition slicing | Explicit declaration ownership/ranges | Required for static forward declarations and inline struct data |

## Completion Checklist

- [x] All tasks completed or explicitly deferred
- [x] Tests passing
- [x] No regressions in available T0–T2 coverage
- [x] Documentation updated
- [x] Current implementation conforms to requirements 1.3
- [x] Corrective plan 1.2 completed and audited
