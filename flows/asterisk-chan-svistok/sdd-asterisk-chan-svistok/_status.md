# Status: sdd-asterisk-chan-svistok

## Current Phase

IMPLEMENTATION

## Phase Status

FUNCTION/LAYOUT IMPLEMENTATION — COMPLETE

## Last Updated

2026-08-26 by Codex

## Blockers

- External verification only: no compatible Linux/Asterisk runtime or modem
  hardware is available on the current Darwin host for T3/T4 execution.
- None for host-available implementation work.

## Progress

- [x] Requirements drafted
- [x] Requirements version 1.2 approved
- [x] Requirements version 1.3 approved
- [x] Specifications revised for source-overlay purity
- [x] Revised specifications approved
- [x] Plan revised for physical source-level extraction
- [x] Revised plan approved
- [x] Corrective implementation started
- [x] Corrective implementation complete
- [x] Requirements 1.4 drafted for function/file separation
- [x] Requirements 1.4 approved
- [x] Specifications revised for hook/proxy layout
- [x] Revised specifications approved
- [x] Revised plan approved
- [x] Function/file separation implementation complete

## Context Notes

- User invoked `$sdd new asterisk-chan-svistok`; `new` is treated as the
  equivalent of the documented `start` command.
- `legacy/asterisk-chan-svistok-v2014` is strictly read-only.
- `libsCpp/asterisk-chan-svistok/asterisk-chan-dongle` is the supplied upstream
  source tree and must remain separated from project-specific code.
- New and modified project code is destined for
  `libsCpp/asterisk-chan-svistok/src`.
- Modified files must be copied verbatim from legacy before adaptation.
- Unchanged function implementations should remain in and be called from the
  upstream tree; changed function bodies should retain the legacy code.
- Initial inspection found source, build artifacts, generated files, utilities,
  and subprojects mixed in the legacy root; this led to the transitive
  module-build closure rule documented in requirements 1.1.
- User confirmed that the complete legacy tree must be classified and that the
  supplied `asterisk-chan-dongle` checkout is the comparison baseline.
- Build inspection established that `programmator/` and `simnode/` contribute
  selected sources transitively via `#include "*.c"`; `reader/` and `old/` do
  not contribute to the channel module.
- Characterization tests were created outside legacy before migration, with
  stable legacy behavior serving as the oracle/golden master.
- Requirements version 1.2 approved by the user on 2026-08-25.
- Requirements version 1.3 drafted on 2026-08-25 after the user clarified that
  `src` itself—not merely generated build slices—must contain only new and
  modified source-level units. The SDD flow is reopened at REQUIREMENTS.
- At the start of correction, `app_register()` was manifest-classified as
  equivalent/upstream-owned while its definition was still present in
  `src/app.c`. It is now physically absent there and resolves directly to the
  baseline-derived object.
- Requirements version 1.3 approved by the user on 2026-08-25.
- Specifications version 1.2 replaces the generated Svistok-slice-from-mixed-
  copy model with physical AST extraction: final overlay files compile directly
  and baseline-derived slices provide unchanged implementations.
- Specifications version 1.2 approved by the user on 2026-08-25.
- Corrective plan version 1.2 stages and validates all 28 modified overlay paths
  before promotion, replaces Svistok slicing with non-filtering composition,
  and makes source-overlay purity plus direct baseline ownership hard gates.
- Corrective plan version 1.2 approved and Phase 8 started on 2026-08-25.
- Every file outside the final module's transitive build closure must be listed
  exhaustively and must not be copied to `src`.
- Full inventory partitions 161 legacy entries into 52 module source/header
  paths and 109 `DO NOT COPY` entries.
- Historical plan 1.1 implemented function-level reuse through dual
  upstream/overlay slicing; corrective plan 1.2 retains baseline slicing but
  replaces overlay slicing with physical extraction and non-filtering
  composition.
- User confirmed the strict ownership model: every unchanged function body
  remains upstream-owned; changed/new bodies remain legacy-owned; cross-slice
  static functions and mutable state use generated build-time bridges.
- Specifications version 1.1 and file inventory version 1.0 were approved by
  the user on 2026-08-25.
- Corrected a narrative count from 20 to 19 root translation units; the audited
  52 included / 109 excluded partition is unchanged.
- Historical plan 1.1 required characterization and AST-slicer checkpoints
  while `src` was still empty, before the exact-copy migration gate.
- Clang JSON AST plus target-owned standard-library tooling is selected for
  syntax-aware slicing; generated slices remain build-only.
- User confirmed the final installable Asterisk module name
  `chan_svistok.so`; plan updated to version 1.1.
- Plan version 1.1 approved and implementation started on 2026-08-25.
- Checkpoint 0 passed: source guards and reproducible inventory are green;
  `src` remains empty.
- Checkpoint 1 passed with nine isolated tests, seven hashed golden fixtures,
  explicit T3/T4 environment gaps, empty `src`, and clean source worktrees.
- Checkpoint 2 passed: the complete 28-file ownership manifest contains 420
  root definitions, 147 macros, 222 declarations, ten directly included new `.c` paths, 81
  static bridges, and zero unowned live entries.
- Synthetic slicing, recursive include, conditional macro, static state/call,
  variadic bridge, provenance, and real `at_parse.c` pilot tests pass.
- Historical Phase 3 exact-copy gate passed before adaptation; its 40 receipts
  remain provenance evidence for corrective physical extraction.
- Checkpoint 3 passed: `src` contains exactly 12 NEW plus 28 MODIFIED paths;
  all 40 hashes match legacy, while 12 IDENTICAL and 109 excluded paths are
  absent. Adaptation may now begin against the recorded receipts.
- Phase 4 passed: explicit include ownership, generated configuration, and
  canonical ABI assertions are green in both slice contexts.
- Phase 5 passed: 32 slices compile, 81 bridges are resolved/hidden, 296
  external symbols have exactly one assigned object owner, and mutable header
  state has one storage owner under `-fno-common`.
- Phase 6 passed for the maximum host-compatible tier: 36 objects link to the
  confirmed `chan_svistok.so`; production build wiring accepts an external
  Asterisk include root.
- Phase 7 available audit passed 25 sequential check groups. Migrated PDU,
  AT parser, buffers, and AT-read outputs match frozen legacy goldens; all nine
  legacy oracle groups remain green.
- Final evidence: `manifests/final-audit.json`. T3/T4 environment gaps remain
  explicitly listed in `manifests/effective-legacy-config.json`.
- Corrective extraction removed 380 upstream-owned units from the 28 modified
  paths (214 C units and 166 header units). Physical `src` now passes the
  source-overlay purity gate.
- The corrected build emits 16 baseline slices and 16 non-filtering overlay
  compositions. `app_register()` and every other equivalent external function
  are supplied under their original names by baseline-derived objects.
- Corrected Phase 11 audit passed 28 sequential check groups; all discovery
  suites also pass. `chan_svistok.so` links from 36 objects with 81 hidden
  bridges and zero ownership errors across 296 checked public symbols.
- On 2026-08-26 the user requested a new source-layout correction: functions
  absent from dongle must move to dedicated files; safely separable changes to
  existing dongle functions must become Svistok hook plus one baseline call;
  proxy-only files must live under `src/dongle`.
- Preliminary manifest inspection finds 45 new functions across nine mixed
  modules. It also finds several supposedly modified definitions with 100%
  source-line equivalence to baseline, requiring ownership reclassification.

## Fork History

- None.

## Next Actions

1. In a compatible Linux/Asterisk environment, run the deferred T3/T4 checks.
