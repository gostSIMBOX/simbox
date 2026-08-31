# Status: sdd-gateway-answer-directmodem-magisk

## Current Phase

**REQUIREMENTS** | SPECIFICATIONS | PLAN | IMPLEMENTATION | DOCUMENTATION

## Phase Status

**DRAFTING**

## Last Updated

2026-08-31 by Claude (split out of `vdd-flutter_gsmsip-example-uiux` at
Anton's explicit request, alongside two sibling flows for the other two
call-answer bypass methods)

## Blockers

- **Parked, not blocked** — Anton asked for this to be documented, not
  implemented. Do not advance past REQUIREMENTS without explicit
  instruction to resume.

## Progress

- [x] Requirements drafted
- [ ] Requirements approved
- [ ] Specifications drafted
- [ ] Specifications approved
- [ ] Plan drafted
- [ ] Plan approved
- [ ] Implementation started
- [ ] Implementation complete
- [ ] Documentation drafted
- [ ] Documentation approved

## Context Notes

Key decisions and context for resuming:

- **Origin**: same as its two siblings — see
  `sdd-gateway-answer-keyevent-magisk/_status.md` Context Notes for the
  shared backstory (AC4's warn-only resolution in
  `vdd-flutter_gsmsip-example-uiux` triggered Anton documenting the
  bypass options separately, not reopening AC4).
- **Method**: root access to the modem's TTY/serial port, issuing `ATA`
  directly to the baseband — answers the call fully outside Android's
  Telecom framework, so default-dialer status is irrelevant. Same
  TTY-access layer as `sdd-voiceline-mode-direct`, but that flow uses it
  for audio path only, not call control.
- **Riskiest of the three siblings**: two independent actors (the stock
  RIL daemon and this app) would both believe they control the modem's
  call state — real risk of Android's Telecom state and the modem's
  actual state desyncing (stuck ringing UI, dropped call, RIL crash,
  vendor-dependent). Requirements flags this as the central thing
  Specifications must resolve before this method is even viable.
- **Inherits an existing open question**: TTY port paths are
  device/manufacturer-specific — same undocumented "device database" gap
  already open in `vdd-flutter_gsmsip-example-voiceline-uiux`. This flow
  does not re-solve it, just inherits it.
- **Siblings**: `sdd-gateway-answer-keyevent-magisk` (input injection)
  and `sdd-gateway-answer-itelephony-magisk` (priv-app hidden API — most
  production-proven).

## Next Actions

1. **None until Anton reopens this flow.** If resumed: this is likely a
   last-resort fallback behind the other two siblings, given the
   RIL/modem state-desync risk — validate that risk concretely before
   investing further, then move to Specifications.
