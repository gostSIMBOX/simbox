# Function/Layout Corrective Implementation Plan: asterisk-chan-svistok

> Version: 1.3  
> Status: APPROVED  
> Last Updated: 2026-08-26  
> Specifications: [02-specifications.md](02-specifications.md)  
> Inventory: [02-file-inventory.md](02-file-inventory.md)

## Summary

Plan 1.1 completed the inventory, characterization, copy-first receipts,
ownership manifest, dual slicing, host-compatible link, and available parity
audit. It proved build-time symbol ownership, but left upstream-equivalent text
physically present in copied files under `src`. Requirements 1.3 and
specifications 1.2 make that final source state nonconforming.

This corrective plan reuses all valid evidence from plan 1.1. It first adds a
source-overlay purity test that demonstrates the current failure, including the
known `src/app.c::app_register()` case. It then produces a complete overlay-only
tree in staging by syntax-aware extraction, validates that staged tree, and
promotes only the 28 modified paths after the entire gate passes. The build is
changed to combine baseline-derived slices with directly compiled overlay
sources or non-filtering overlay composition units. It must no longer create a
Svistok slice from a mixed full-file legacy copy.

The final module remains `chan_svistok.so`. Legacy and
`asterisk-chan-dongle` remain read-only throughout.

Version 1.3 performs the approved second correction without discarding Phase
11 evidence. It stages the exact 45/6/14/87 function partition, separates new
definitions and hooks below `src/svistok`, creates proxy-only fragments below
`src/dongle`, returns six false-modified bodies to baseline, and promotes the
layout only after a complete staged build and parity replay.

## Existing Evidence Reused

- The 52 included / 109 excluded file inventory and source guards.
- Nine legacy oracle groups and seven frozen golden fixtures.
- Exact-copy receipts for 12 new and 28 modified paths.
- The stable ownership manifest and existing baseline/legacy body hashes.
- Existing ABI, bridge, object-symbol, link, and final-audit tests.
- Explicit T3/T4 Linux/Asterisk/hardware environment gaps.

Reusing this evidence does not grandfather the current mixed `src` files. Any
test whose assumption was “equivalent code may remain in `src` if filtered at
build time” must be replaced or tightened.

## Tooling Decision

- Extend the existing Clang JSON-AST/preprocessor toolchain; do not introduce a
  regex extractor or a network-fetched parser.
- Classify functions, data, declarations, types, macros, and inline bodies as
  atomic source-level units with spelling ranges.
- Generate candidate overlay files under `build/staging-overlay/`. Do not edit
  the 28 current target files incrementally while extraction is incomplete.
- Generated baseline slices and bridge/composition units remain under
  `build/generated/` and outside `src`.
- A composition unit may include an entire already-pure overlay file and append
  generated wrappers/accessors needed to reach its `static` symbols. It may not
  remove or replace text from that overlay file.
- Ordinary unchanged external symbols retain their upstream names. No
  forwarding wrapper, `dlsym`, weak selection, or link-order dispatch is added.

## Phase 8: Reopen Gate and Create Failing Purity Coverage

### Task 8.1: Freeze the corrective starting state

- **Description**: Re-run source guards, inventory, copy-receipt history,
  ownership-manifest stability, legacy oracle groups, and the existing final
  audit. Record current target hashes separately from the original copy hashes.
- **Files**:
  - `manifests/corrective-baseline.json` — Create
  - `04-implementation-log.md` — Update
- **Dependencies**: Specifications 1.2 approved; plan 1.2 approved
- **Verification**: Legacy and baseline are clean; 52/109 partition and frozen
  fixtures are unchanged; current target hashes are reproducible.
- **Complexity**: Low

### Task 8.2: Add source-overlay purity tests before extraction

- **Description**: Add a verifier/test that inspects only units physically
  spelled under `src` and rejects equivalent, unclassified, duplicated, or
  owner-mismatched units. Cover functions, data, declarations, types, macros,
  inline bodies, recursive includes, conditionals, and target-authored adapters.
- **Files**:
  - `tools/verify_overlay_purity.py` — Create
  - `tests/slicer/test_overlay_purity.py` — Create
  - `tests/slicer/fixtures/overlay-purity/` — Create
- **Dependencies**: Task 8.1
- **Verification**: Synthetic valid overlays pass. Deliberate equivalent units
  fail with path, source range, kind, identity, and baseline provenance.
- **Complexity**: High

### Task 8.3: Lock the `app_register()` acceptance case

- **Description**: Add a focused regression test proving that equivalent
  `app_register()` must not be defined in `src/app.c`, must not have a
  Svistok forwarding wrapper, and must be owned under its original name by the
  baseline-derived object.
- **Files**:
  - `tests/slicer/test_app_upstream_reuse.py` — Create
- **Dependencies**: Task 8.2
- **Verification before extraction**: The test fails specifically because the
  current `src/app.c` still contains `app_register()`.
- **Verification after extraction**: The overlay object has no definition,
  the baseline object has the sole strong `app_register` definition, and the
  composed link resolves the original symbol.
- **Complexity**: Medium

### Checkpoint 8 — expected-red gate

- Source guards and historical characterization remain green.
- Purity verifier synthetic coverage is green.
- The real-tree purity test and focused `app_register()` test fail for the
  expected current-source reason, not because of harness/configuration errors.
- No production source has been changed.

## Phase 9: Extract and Validate the Physical Overlay

### Task 9.1: Complete the atomic-unit ownership manifest

- **Description**: Extend/revalidate ownership for all source-level units in
  the 28 modified paths. Add explicit entries for target-authored include,
  guard, ABI, state-storage, and adapter units introduced after copy-first.
- **Files**:
  - `tools/clang_manifest.py` — Modify
  - `manifests/symbol-ownership.json` — Regenerate/modify
  - `tests/slicer/test_manifest.py` — Modify
- **Dependencies**: Checkpoint 8
- **Verification**: Every local unit is classified; every equivalent unit is
  baseline-owned; every retained legacy unit is new/modified; every adapter has
  a reason. Zero unowned units.
- **Complexity**: High

### Task 9.2: Implement syntax-aware overlay extraction

- **Description**: Generate each candidate modified overlay from its
  receipt-verified legacy source plus recorded post-copy adaptations. Retain
  whole new/modified syntax units and physically omit equivalent units. Preserve
  the legacy code text of retained bodies and emit a source-range provenance
  map. Do not rewrite function implementations.
- **Files**:
  - `tools/extract_overlay.py` — Create
  - `tests/slicer/test_overlay_extraction.py` — Create
  - `build/staging-overlay/` — Generate only
  - `manifests/overlay-extraction.json` — Generate
- **Dependencies**: Task 9.1
- **Verification**: Synthetic and real extraction are deterministic. Every
  retained legacy body matches its normalized legacy hash; no equivalent unit
  appears in staging; all necessary adapter text is separately owned.
- **Complexity**: High

### Task 9.3: Extract modified headers and prove canonical ABI

- **Description**: Reduce modified headers to changed/new atomic declarations,
  types, macros, and inline bodies; import compatible unchanged declarations
  from baseline. Update distinct guards/include routing and compile both layers
  against the canonical Svistok ABI.
- **Files**:
  - Modified staged headers — Generate
  - `src/svistok_abi.h` — Modify only if required by verified ownership
  - `tests/test_abi.c` — Modify
  - header ownership tests — Modify/create
- **Dependencies**: Task 9.2
- **Verification**: No equivalent local header unit remains; dependency output
  identifies its physical owner; size/offset/type assertions pass in baseline
  and overlay contexts and fail on the existing negative fixture.
- **Complexity**: High

### Task 9.4: Replace Svistok slicing with non-filtering composition

- **Description**: Keep baseline slicing for definitions replaced/removed by
  Svistok. Replace generation of filtered Svistok slices with direct overlay
  compilation or a non-filtering composition source that includes the entire
  pure overlay and appends only required static bridges/accessors.
- **Files**:
  - `tools/slice_translation_unit.py` — Modify
  - `tools/generate_bridges.py` — Modify
  - `tests/slicer/test_slicing.py` — Modify
  - `tests/slicer/test_bridges.py` — Modify
- **Dependencies**: Tasks 9.2–9.3
- **Verification**: Composition output contains the complete overlay exactly
  once, performs no overlay range deletion, resolves both static dependency
  directions, and creates no duplicate mutable state.
- **Complexity**: High

### Task 9.5: Validate the complete staged tree before promotion

- **Description**: Compile all staged overlay files with generated baseline
  slices/composition units and run purity, provenance, ABI, bridge, object
  symbol, inventory, and host-compatible characterization checks.
- **Files**: Build outputs only
- **Dependencies**: Tasks 9.3–9.4
- **Verification**: Zero equivalent units in staged overlay; zero unowned
  units; every changed/new legacy body hash matches; one strong owner per
  external symbol; all available golden comparisons pass.
- **Complexity**: High

### Checkpoint 9 — staged overlay gate

- All 28 candidate modified paths exist in staging and pass as one set.
- The 12 new files remain unchanged unless a separately planned include-only
  adaptation is required and manifest-owned.
- `app_register()` is absent from staged `app.c` and solely baseline-owned.
- Current `src` has not yet been partially replaced.
- Legacy and baseline remain clean.

## Phase 10: Promote Overlay and Rewire the Build

### Task 10.1: Promote the verified 28-file overlay set

- **Description**: Back up current target hashes/content in scoped build
  staging, then mechanically replace exactly the 28 modified `src` paths with
  the verified candidates as one reviewed set. Do not touch the 12 new paths,
  legacy, baseline, or excluded paths.
- **Files**: The 28 modified paths under `src` — Modify
- **Dependencies**: Checkpoint 9
- **Verification**: Promoted hashes equal staged hashes; purity and provenance
  checks pass against the physical final `src`; excluded paths remain absent.
- **Complexity**: Medium

### Task 10.2: Rewire production and compatibility builds

- **Description**: Compile unchanged complete baseline files where possible,
  baseline slices where definitions are replaced/removed, new `src` files, and
  pure overlay files/non-filtering composition units. Remove generated Svistok
  slices from all build inputs.
- **Files**:
  - `Makefile` — Modify
  - build helper scripts/configuration — Modify
  - `.gitignore` — Modify only if new staging paths require it
- **Dependencies**: Task 10.1
- **Verification**: Build trace has no legacy source input, no excluded input,
  and no filtered Svistok slice. Host-compatible `chan_svistok.so` links with
  no duplicate/unresolved symbol and no public bridge symbol.
- **Complexity**: High

### Task 10.3: Re-run direct upstream ownership tests

- **Description**: Inspect source, generated inputs, objects, and link map for
  all equivalent external functions, not only `app_register()`.
- **Files**:
  - `tools/verify_object_symbols.py` — Modify
  - `tests/test_symbol_ownership.py` — Modify
- **Dependencies**: Task 10.2
- **Verification**: Each equivalent external symbol is absent as a definition
  from `src`/overlay objects, appears once in a baseline-derived object under
  its original name, and uses no forwarding wrapper.
- **Complexity**: Medium

### Checkpoint 10 — final source/build ownership gate

- Physical `src` passes source-overlay purity.
- Final build uses baseline code directly for every equivalent external unit.
- Static bridges/accessors equal the manifest and are hidden.
- `chan_svistok.so` passes all host-available ABI/link checks.

## Phase 11: Parity, Documentation, and Final Audit

### Task 11.1: Replay all available characterization tiers

- **Description**: Re-run the same frozen T0–T2 inputs against the corrected
  composition and compare normalized results exactly with legacy goldens.
- **Files**: Test outputs only
- **Dependencies**: Checkpoint 10
- **Verification**: All previously passing oracle/migrated groups remain green;
  any mismatch stops completion and is diagnosed against legacy.
- **Complexity**: Medium

### Task 11.2: Update ownership/build documentation

- **Description**: Document copy-first as an intermediate receipt gate,
  physical overlay extraction, direct external-symbol reuse, static-only
  bridges, purity verification, and reproducible generation/build commands.
- **Files**:
  - `README.md` — Modify
  - `README_ru.md` — Modify
  - relevant tool/test READMEs — Modify
- **Dependencies**: Task 11.1
- **Verification**: Documented commands reproduce purity, extraction,
  composition, link, and audit results from the checked-in source state.
- **Complexity**: Low

### Task 11.3: Produce the corrected final audit

- **Description**: Run source guards, 52/109 inventory, receipt history,
  physical purity, extraction provenance, ABI, bridge, object ownership, build,
  and characterization checks sequentially. Retain T3/T4 as explicit external
  gaps until the required environment/hardware is available.
- **Files**:
  - `manifests/final-audit.json` — Regenerate
  - `04-implementation-log.md` — Update
  - `_status.md` — Update
- **Dependencies**: Tasks 11.1–11.2
- **Verification**: Audit fails closed on any equivalent local unit or generated
  Svistok slice; all available checks pass; source worktrees remain clean.
- **Complexity**: Medium

## Phase 12: Freeze the 45/6/14/87 Classification and Add Red Gates

### Task 12.1: Freeze the second-correction starting state

- **Description**: Re-run source guards, the Phase 11 final audit, physical
  purity, symbol ownership, and golden fixtures. Record hashes of every current
  target source before any layout edit.
- **Files**:
  - `manifests/function-layout-baseline.json` — Create
  - `04-implementation-log.md` — Update
- **Dependencies**: Specifications 1.3 and plan 1.3 approved
- **Verification**: Baseline/legacy clean; 28 audit groups pass; current source
  hashes and the 45/6/14/87 partition reproduce deterministically.
- **Complexity**: Low

### Task 12.2: Add the function-layout manifest

- **Description**: Extend the AST ownership model with a physical
  `layout_owner`: `baseline`, `svistok-new`, `svistok-hook`, `dongle-proxy`, or
  `svistok-inseparable`. Check in the complete 45/6/14/87 mapping from
  specifications 1.3 and reject drift.
- **Files**:
  - `tools/clang_manifest.py` — Modify
  - `tools/function_layout.py` — Create
  - `manifests/function-layout.json` — Create
  - `tests/layout/test_function_layout_manifest.py` — Create
- **Dependencies**: Task 12.1
- **Verification**: Run the single manifest test; assert 45 new, 6 reclassified
  baseline, 14 decomposed, and 87 inseparable function implementations with no
  overlap or unclassified modified/new function.
- **Complexity**: Medium

### Task 12.3: Add expected-red physical-layout tests

- **Description**: Before moving code, add focused tests requiring all 45 new
  definitions below `src/svistok`, all proxy definitions below `src/dongle`,
  and the six false-modified definitions absent from `src`.
- **Files**:
  - `tools/verify_function_layout.py` — Create
  - `tests/layout/test_new_function_paths.py` — Create
  - `tests/layout/test_proxy_paths.py` — Create
  - `tests/layout/test_reclassified_baseline.py` — Create
- **Dependencies**: Task 12.2
- **Verification before implementation**: Run each new test separately. It
  fails for the intended current path/ownership reason, while existing purity
  and Phase 11 audit remain green.
- **Complexity**: Medium

### Task 12.4: Add proxy contract tests

- **Description**: Add synthetic and real-manifest checks that proxy files
  contain no business logic, call only their matching hook plus hidden
  baseline entry, have exactly one syntactic baseline call, and cannot recurse
  through the original public name.
- **Files**:
  - `tests/layout/test_proxy_contract.py` — Create
  - `tests/layout/fixtures/` — Create
- **Dependencies**: Task 12.2
- **Verification**: Valid before/after/result adapters pass; zero-call,
  double-call, recursive, mismatched-entry, and business-logic fixtures fail.
- **Complexity**: High

### Checkpoint 12 — expected-red layout gate

- Existing source/build/parity tests remain green.
- New manifest and synthetic proxy tests are green.
- Real path tests fail only because the approved split has not yet occurred.
- No production source or build input has changed.

## Phase 13: Generate the New-Function Layout in Staging

### Task 13.1: Extract 45 complete new definitions

- **Description**: Using recorded Clang spelling ranges, extract the complete
  legacy definitions into the nine approved `src/svistok/<module>.c` candidate
  fragments under staging. Remove those ranges from candidate root overlays
  without reformatting either retained or moved definitions.
- **Files**:
  - `tools/extract_function_layout.py` — Create
  - `build/staging-function-layout/svistok/*.c` — Generate
  - `build/staging-function-layout/root/*.c` — Generate
  - `manifests/function-layout-extraction.json` — Create
  - `tests/layout/test_new_function_extraction.py` — Create
- **Dependencies**: Checkpoint 12
- **Verification**: Run the extraction test alone; all 45 definitions have
  legacy provenance hashes, occur once below staged `svistok`, and no longer
  occur in staged root overlays.
- **Complexity**: High

### Task 13.2: Split new-only declarations

- **Description**: Move declarations for the extracted external functions to
  `src/svistok/<module>.h` candidates. Generate private build-only prototypes
  for static fragments and keep modified ABI types in compatibility headers.
- **Files**:
  - `build/staging-function-layout/svistok/*.h` — Generate
  - staged compatibility headers — Modify
  - `tools/compose_headers.py` — Modify
  - `tests/layout/test_header_layout.py` — Create
- **Dependencies**: Task 13.1
- **Verification**: Run the header-layout test alone; new declarations have
  one physical owner, equivalent declarations remain baseline-derived, static
  helpers do not become public, and both ABI contexts compile.
- **Complexity**: High

### Task 13.3: Preserve logical translation-unit order and linkage

- **Description**: Extend non-filtering composition so root, new-function,
  hook, and proxy fragments share the original logical translation unit where
  static linkage requires it. Generate private forward declarations rather
  than duplicate implementations.
- **Files**:
  - `tools/generate_all_slices.py` — Modify
  - `tools/generate_bridges.py` — Modify
  - `tests/layout/test_fragment_composition.py` — Create
- **Dependencies**: Tasks 13.1–13.2
- **Verification**: Run the fragment-composition test alone; every moved static
  function remains static, every call resolves, and each definition appears
  exactly once in the preprocessed translation unit.
- **Complexity**: High

### Checkpoint 13 — staged new-function split

- Nine staged `svistok` C fragments contain all 45 new functions exactly once.
- New-only declarations are physically separate and ABI checks pass.
- Candidate compositions compile with unchanged legacy body hashes.
- Current checked-in `src` is still untouched.

## Phase 14: Reclassify Baseline Bodies and Build Hook/Proxy Composition

### Task 14.1: Return six false-modified definitions to baseline

- **Description**: Change ownership for the six approved definition bodies to
  baseline and remove them from staged root candidates. Preserve any required
  changed dependency through existing hidden bridge/accessor machinery.
- **Files**:
  - ownership/layout manifests — Regenerate
  - staged root candidates — Generate
  - baseline slicing tools — Modify if dependency routing requires it
  - `tests/layout/test_reclassified_baseline.py` — Complete green assertions
- **Dependencies**: Checkpoint 13
- **Verification**: Run the reclassification test alone; source tokens match
  baseline, overlay objects contain no definitions, and baseline-derived
  objects own the six original names once.
- **Complexity**: Medium

### Task 14.2: Generate hidden baseline entries for 14 functions

- **Description**: Retain each approved dongle definition in its baseline slice
  under `svistok_dongle_impl_<function>`, with hidden visibility and the same
  ABI. Do not rename or expose any function outside the approved set.
- **Files**:
  - `tools/slice_translation_unit.py` — Modify
  - `tools/generate_bridges.py` — Modify
  - `tests/layout/test_baseline_impl_entries.py` — Create
- **Dependencies**: Task 14.1
- **Verification**: Run the baseline-entry test alone; exactly 14 hidden entries
  exist, their body provenance matches baseline, and no public/internal naming
  collision is present.
- **Complexity**: High

### Task 14.3: Extract Svistok hooks and create six proxy fragments

- **Description**: Create the six approved hook files with only the additions
  specified in 1.3, and six proxy-only files with the original function names
  and exact before/after/result ordering. Remove all 14 full modified bodies
  from staged root candidates.
- **Files**:
  - `build/staging-function-layout/svistok/hooks/*.c` — Generate/create
  - `build/staging-function-layout/dongle/*.c` — Generate/create
  - `manifests/hook-proxy-provenance.json` — Create
  - `tests/layout/test_hook_extraction.py` — Create
- **Dependencies**: Task 14.2
- **Verification**: Run the hook extraction test alone; additions retain legacy
  provenance, proxies contain no business logic, every proxy has one matching
  hook sequence and one baseline call, and the full old body is absent.
- **Complexity**: High

### Task 14.4: Prove runtime call count and failure-path ordering

- **Description**: Instrument generated baseline entries in test builds and
  execute focused scenarios for all 14 wrappers, including success, parse
  failure, allocation/error returns where applicable, and conditional hooks.
- **Files**:
  - `tests/layout/test_proxy_runtime.py` — Create
  - test-only instrumentation support — Create
- **Dependencies**: Task 14.3
- **Verification**: Run the runtime proxy test alone; each invocation reaches
  baseline exactly once and its hook trace/return value equals the frozen
  legacy trace.
- **Complexity**: High

### Checkpoint 14 — complete staged function partition

- The staged tree proves the exact 45/6/14/87 partition.
- Six direct-baseline definitions and 14 full copied baseline bodies are absent
  from staged `src`.
- Six proxy files live only below staged `src/dongle`; six hook files live only
  below staged `src/svistok/hooks`.
- Proxy purity, call count, body provenance, ABI, symbol ownership, and focused
  behavior are green.

## Phase 15: Validate, Promote, and Rewire the Build

### Task 15.1: Compile and replay the complete staged tree

- **Description**: Build `chan_svistok.so` from the entire staged layout and run
  all existing T0–T2 characterization plus layout, purity, ABI, bridge, symbol,
  inventory, and migrated golden tests sequentially.
- **Files**: Build outputs only
- **Dependencies**: Checkpoint 14
- **Verification**: All available checks pass as one set; no test is updated to
  accept changed legacy output.
- **Complexity**: High

### Task 15.2: Promote the layout atomically

- **Description**: Back up every target path being replaced, added, moved, or
  removed, then promote the complete verified staging set. Do not partially
  move individual modules.
- **Files**:
  - `src/svistok/` — Create
  - `src/dongle/` — Create
  - root overlay source/header paths — Modify/remove only as recorded
  - `manifests/function-layout-promotion.json` — Create
- **Dependencies**: Task 15.1
- **Verification**: Promoted hashes equal staging; backup hashes equal the
  frozen starting state; legacy/baseline remain clean.
- **Complexity**: Medium

### Task 15.3: Remove empty forwarding shells

- **Description**: After promotion, remove root C files that own no remaining
  function/data unit. Expected candidates are `at_parse.c`, `at_queue.c`,
  `ringbuffer.c`, and `cpvt.c`; actual removal is driven by the checked layout
  manifest, not this prediction.
- **Files**: Empty root overlay paths — Remove
- **Dependencies**: Task 15.2
- **Verification**: No checked-in source consists only of includes, whitespace,
  markers, or forwarding declarations; module closure remains complete.
- **Complexity**: Low

### Task 15.4: Rewire production and compatibility build inputs

- **Description**: Build baseline slices, inseparable root overlays, new
  fragments, hook fragments, and proxy fragments according to the checked
  manifest. Reject any obsolete path or generated filtered Svistok slice.
- **Files**:
  - `tools/build_module.py` — Modify
  - `Makefile` — Modify if required
  - build/layout tests — Modify
- **Dependencies**: Tasks 15.2–15.3
- **Verification**: Compatibility `chan_svistok.so` links with one owner per
  public symbol, 14 hidden baseline entries, no public proxy infrastructure,
  and no unresolved bridge.
- **Complexity**: High

### Checkpoint 15 — final physical/build layout

- Checked-in paths conform to `baseline`/`svistok-new`/`svistok-hook`/
  `dongle-proxy`/`svistok-inseparable` ownership.
- No empty forwarding shell remains at root.
- `chan_svistok.so` passes layout, purity, ABI, link, and object ownership gates.

## Phase 16: Parity, Documentation, and Final Audit

### Task 16.1: Replay all frozen behavior tiers

- **Description**: Re-run the same available T0–T2 scenarios used by Phase 11
  against the promoted layout and compare exact normalized outputs.
- **Files**: Test outputs only
- **Dependencies**: Checkpoint 15
- **Verification**: All legacy oracle and migrated golden results remain exact;
  T3/T4 remain explicitly external if unavailable.
- **Complexity**: Medium

### Task 16.2: Update source-layout documentation and full lists

- **Description**: Document the final directory model, all 45 new-function
  destinations, six direct-baseline bodies, fourteen hook/proxy compositions,
  87 retained bodies, six proxy files, and any removed empty roots.
- **Files**:
  - `README.md` — Modify
  - `README_ru.md` — Modify
  - `02-file-inventory.md` — Add final physical-layout appendix
  - `04-implementation-log.md` — Update
- **Dependencies**: Task 16.1
- **Verification**: Documented commands reproduce manifest generation, layout
  verification, compatibility build, and final audit.
- **Complexity**: Low

### Task 16.3: Produce the second corrected final audit

- **Description**: Run source guards, inventory, receipt history, physical
  layout, proxy purity/call count, body provenance, ABI, bridges, symbol
  ownership, build, and all available characterization sequentially.
- **Files**:
  - `manifests/final-audit.json` — Regenerate
  - `_status.md` — Update
- **Dependencies**: Task 16.2
- **Verification**: Audit fails closed on wrong physical path, duplicate/new
  mixed definition, proxy business logic, wrong baseline call count, public
  internal symbol, or golden mismatch; all available checks pass.
- **Complexity**: Medium

## Revised Dependency Graph

```text
12 Freeze + expected-red layout gates
  -> 13 extract 45 new definitions and declarations in staging
  -> 14 reclassify 6 + compose 14 hooks/proxies + retain 87
  -> 15 full staged audit -> atomic promotion -> build rewiring
  -> 16 parity -> documentation -> final audit
```

## Version 1.3 File Change Summary

| Path | Action | Reason |
|---|---|---|
| `src/svistok/*.c` | Create 9 | Own 45 functions absent from dongle |
| `src/svistok/*.h` | Create as needed | Own new-only external declarations |
| `src/svistok/hooks/*.c` | Create 6 | Own additions from 14 decomposed functions |
| `src/dongle/*.c` | Create 6 | Proxy-only one-baseline-call composition |
| root `src/*.c` overlays | Modify/remove | Retain only 87 inseparable functions; remove empty shells |
| compatibility headers | Modify | Remove new-only declarations and preserve ABI units |
| ownership/layout manifests | Create/regenerate | Prove 45/6/14/87 classification and physical owner |
| extraction/composition/build tools | Modify/create | Deterministic staging and hidden baseline entries |
| layout/proxy tests | Create | Path, purity, call-count, recursion, and parity gates |
| READMEs/SDD | Modify | Full final lists and reproducible commands |

## Version 1.3 Rollback Strategy

1. All source generation occurs under `build/staging-function-layout`; discard
   only that scoped staging tree before promotion.
2. Promotion records and backs up every explicit target path, including root
   removals and new directories, before changing checked-in `src`.
3. If a post-promotion gate fails, restore only recorded pre-promotion paths and
   remove only newly promoted paths listed in the promotion manifest.
4. Never restore, clean, or write legacy or `asterisk-chan-dongle`.
5. Preserve the failing proxy/golden trace before revising the approved
   45/6/14/87 partition.

## Historical Version 1.2 Dependency Graph

```text
8 Freeze evidence → purity/app tests fail for expected reason
                         ↓
9 Complete manifest → extract 28 paths in staging → validate full staging set
                         ↓
10 Promote 28 paths → rewire build → verify direct baseline symbol ownership
                         ↓
11 Replay goldens → update docs → corrected final audit
```

## Historical Version 1.2 File Change Summary

| Path | Action | Reason |
|---|---|---|
| `src/` 28 modified paths | Physically reduce after staged validation | Keep only new/changed atomic units |
| `src/` 12 new paths | Preserve | Entire files are project-new and in module closure |
| `asterisk-chan-dongle/` | No change | Sole source of equivalent upstream implementation |
| `legacy/asterisk-chan-svistok-v2014/` | No change | Read-only oracle and provenance source |
| `tools/clang_manifest.py` | Modify | Complete atomic-unit ownership |
| `tools/extract_overlay.py` | Create | Deterministic physical overlay extraction |
| `tools/verify_overlay_purity.py` | Create | Fail on equivalent/unowned code in final `src` |
| slicer/bridge tools | Modify | Baseline slicing plus non-filtering overlay composition |
| `Makefile` and build helpers | Modify | Remove generated Svistok slices from build inputs |
| manifests | Create/regenerate | Corrective baseline, extraction map, final evidence |
| tests | Create/modify | Purity, `app_register`, headers, symbols, parity |
| READMEs | Modify | Document final source/build ownership model |

## Risk Assessment

| Risk | Impact | Mitigation |
|---|---|---|
| Removing an apparently equivalent declaration breaks parsing | High | Complete unit/dependency manifest; compile full staged set before promotion |
| Header extraction selects incompatible baseline declaration | Critical | Canonical ABI contexts plus size/offset/type and negative tests |
| Changed code loses access to upstream `static` symbol/state | Critical | Generated baseline wrapper/accessor and both-direction bridge tests |
| Upstream unchanged code loses access to changed `static` symbol/state | Critical | Non-filtering overlay composition appends wrapper in same translation unit |
| Extractor alters a changed legacy body | Critical | Normalized legacy provenance hash for every retained body |
| Partial promotion leaves mixed source state | High | Validate all 28 in staging; promote only the verified set; scoped backup |
| Adapter text hides duplicated implementation | High | Separate adapter ownership and purity rule; disabled duplicate bodies fail |
| Conditional compilation changes ownership | High | Verify with recorded effective defines and supported configuration contexts |
| Existing parity regresses | Critical | Replay frozen legacy goldens after staged build and final promotion |
| T3/T4 unavailable on Darwin host | Medium | Preserve exact external gaps; never claim those tiers passed |
| Moving a static function changes linkage/order | Critical | Non-filtering fragment composition plus generated private prototypes and symbol audit |
| Proxy calls baseline twice or recursively | Critical | AST call-count gate plus runtime instrumentation on all 14 functions |
| Hook ordering differs on an error path | Critical | Focused frozen traces for success/failure paths; reclassify as inseparable on mismatch |
| Proxy accumulates business logic | High | Proxy-purity checker restricts it to hook/result adaptation and one hidden baseline call |

## Historical Version 1.2 Rollback Strategy

1. Before promotion, discard only `build/staging-overlay/`; production `src`
   remains unchanged.
2. During promotion, retain a scoped hash-verified backup of exactly the 28
   replaced target paths under the ignored corrective build directory.
3. If any post-promotion gate fails, restore exactly those 28 target paths from
   the scoped backup and verify their recorded corrective-baseline hashes.
4. Never restore, clean, or write legacy or `asterisk-chan-dongle`.
5. Preserve failing purity/provenance/parity evidence in the implementation log
   before revising the approved plan.

## Approval Gates and Checkpoints

- [x] Historical plan 1.1 completed; evidence retained
- [x] Checkpoint 8: expected-red real-tree purity and `app_register()` tests
- [x] Checkpoint 9: complete staged 28-file overlay passes
- [x] Checkpoint 10: promoted physical overlay and build ownership pass
- [x] Checkpoint 11: parity, documentation, and corrected final audit pass
- [x] Checkpoint 12: function-layout manifest and expected-red path gates
- [x] Checkpoint 13: staged 45-function physical split
- [x] Checkpoint 14: staged 6 baseline + 14 proxy/hook + 87 retained partition
- [x] Checkpoint 15: promoted physical/build layout
- [x] Checkpoint 16: parity, documentation, and second corrected final audit

No version 1.3 production-source change may begin before explicit approval of
plan 1.3.

## Open Implementation Questions

- None. The final module remains `chan_svistok.so`; T3/T4 environment gaps are
  unchanged.

---

## Approval

- [x] Version 1.1 reviewed and approved by: user on 2026-08-25
- [x] Version 1.1 notes: approved by explicit `plan approved`.
- [x] Version 1.2 reviewed by: user
- [x] Version 1.2 approved on: 2026-08-25
- [x] Version 1.2 notes: corrective physical overlay extraction and direct
  baseline reuse.
- [x] Version 1.3 reviewed by: user
- [x] Version 1.3 approved on: 2026-08-26
- [x] Version 1.3 notes: staged 45/6/14/87 function split, `src/svistok` new
  code/hooks, six `src/dongle` proxy-only fragments, atomic promotion, and
  second parity audit.
