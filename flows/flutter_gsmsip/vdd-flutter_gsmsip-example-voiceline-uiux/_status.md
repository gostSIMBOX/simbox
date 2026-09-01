# Status: vdd-flutter_gsmsip-example-voiceline-uiux

## Current Phase

REQUIREMENTS | VISUAL | SPECIFICATIONS | **PLAN** | IMPLEMENTATION | DOCUMENTATION

## Phase Status

APPROVED | APPROVED | APPROVED | APPROVED | **NOT STARTED** | PENDING

## Last Updated

2026-08-31 by Claude (corrected: 05-implementation-log.md shows every task
still PENDING and no `voice_line_*` files exist anywhere in
`libsFlutter/flutter_gsmsip/example` — this file previously claimed
Phases 1-4 complete, which did not match reality. Also fixed stale
`vdd-voiceline`/`vdd-dongles` cross-references left over from this flow's
move out of `flows/_archive/vdd-voiceline/`, and renamed this header to
match the current directory name. **Update**: the overlap noted below is
no longer purely theoretical — `vdd-flutter_gsmsip-example-uiux` has now
implemented its side (Gateway screen, Default Dialer UI, DS restyle,
splash) and its "System Capabilities panel" (AC3) remains explicitly
Deferred/unbuilt pending `sdd-flutter_gsmsip-lib`, so no real code
collision exists yet — but this flow's own Phase 1 should check that
flow's `03-specifications.md` Deferred section before designing "Enhanced
Mode" screen internals, not just its `02-visual.md` mockup.)

## Blockers

- None — ready to start Phase 1 (Domain Layer) whenever implementation
  begins.
- Before starting: coordinate with `flows/flutter_gsmsip/vdd-flutter_gsmsip-example-uiux`
  — its "System Capabilities panel" (still unbuilt, Deferred pending
  `sdd-flutter_gsmsip-lib`) and this flow's "Enhanced Mode" screen both
  surface Magisk-derived capability flags; avoid designing/building two
  overlapping screens independently. Since that flow's Gateway/Default
  Dialer/DS-restyle work is now implemented, its `example/lib/theme/`
  tokens (Green/Simple DS colors) are already live in this codebase —
  this flow's own screens should adopt the same tokens rather than
  reintroducing the old bespoke palette.

## Progress

- [x] VDD flow created
- [x] Requirements drafted
- [x] Requirements approved
- [x] Visual mockups drafted
- [x] Visual mockups approved
- [x] Specifications drafted
- [x] Specifications approved
- [x] Plan drafted
- [x] Plan approved
- [ ] Implementation started
- [ ] Phase 1: Domain Layer complete
- [ ] Phase 2: Data Layer complete
- [ ] Phase 3: Presentation complete
- [ ] Phase 4: Integration complete
- [ ] Documentation drafted
- [ ] Documentation approved

## Context Notes

### Source Materials

Analyzed from SDD flows:
- `sdd-voiceline-mode-direct` - Direct mode (acoustic coupling, no root)
- `sdd-voiceline-mode-magisk` - Magisk mode (system-level integration)
- `sdd-voiceline-mode-magisk-v2` - Magisk v2 (privileged permissions)

### Voice Line Access Methods

| Method | Interface | Root Required | Quality | Notes |
|--------|-----------|---------------|---------|-------|
| **TTY Port** | `/dev/tty*` or `/sys/class/tty/*` | No | High | Model-specific paths |
| **Telecom API** | `android.telecom.*` | No | Medium | Standard Android API |
| **Enhanced Mode** | System-level access | Yes | High | Privileged permissions, not mentioned in UI |
| **Dongle** | USB-C / TRRS | No | High | External hardware (see vdd-flutter_gsmsip-example-zatychka-uiux) |

### Key Constraints

1. **Magisk not mentioned in UI** - App stores don't like root-related features
   - Use "Enhanced Mode" or "System-level Access" naming
2. **Device-dependent** - Different phones have different capabilities
3. **Fallback chain** - Multiple methods, try from best to worst quality
4. **TTY paths** - Model-specific, need device database

### Architecture Decision

```
Voice Line Access Layer
├── TTY Port (/dev/ttyUSB*, /dev/ttyHS*)
├── Telecom API (android.telecom.ConnectionService)
├── Enhanced Mode (system-level, hidden from UI)
└── Dongle (external hardware, vdd-flutter_gsmsip-example-zatychka-uiux)
```

### Visual Design Decisions

- Auto-detection as primary UX pattern
- Quality indicators (★★★★★) for each method
- Fallback shown transparently to user
- "Why unavailable?" explanations for transparency
- Test screens for each method

## Next Actions

1. Resolve the Enhanced-Mode / System-Capabilities-panel overlap with
   `vdd-flutter_gsmsip-example-uiux` before writing code for either.
2. Start Phase 1 (Domain Layer) per `04-plan.md` and log real progress in
   `05-implementation-log.md` as tasks complete (not before).
3. After implementation: create client-facing README.md, document the
   feature in non-technical terms, add usage examples, get documentation
   approval.
