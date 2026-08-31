# Status: sdd-gateway-answer-keyevent-magisk

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

- **Origin**: `vdd-flutter_gsmsip-example-uiux`'s AC4 (Default Dialer
  status) resolved to "warn, don't block" — but Anton separately noted
  that without default-dialer status, the Gateway's auto-answer/bridge
  genuinely cannot fire via the standard `InCallService` API. This flow
  (plus its two siblings) documents the non-standard ways around that
  limitation, for future reference — not because AC4's warn-only
  resolution is being revisited.
- **Method**: root/Magisk + `input keyevent KEYCODE_CALL` — simulates a
  hardware answer-button press at the input-injection layer, bypassing
  `InCallService` permissions entirely.
- **Siblings**: `sdd-gateway-answer-itelephony-magisk` (priv-app hidden
  API — most production-proven, `gsm2sip` already does this) and
  `sdd-gateway-answer-directmodem-magisk` (modem AT command — riskiest,
  state-desync concern with the OS's own RIL).
- **Open question worth flagging early**: this may not actually need a
  full Magisk *module* — plain root (`su`) might suffice, unlike the
  priv-app sibling. If Specifications confirms that, the "_magisk"
  naming may be revisited (or just kept as the project's established
  label for "non-standard root-adjacent workaround," which is broader
  than strictly requiring a Magisk module).

## Next Actions

1. **None until Anton reopens this flow.** If resumed: validate the
   `KEYCODE_CALL` approach on a real device, resolve the screen-lock and
   race-condition Open Questions, then move to Specifications.
