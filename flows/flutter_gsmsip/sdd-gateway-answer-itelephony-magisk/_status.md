# Status: sdd-gateway-answer-itelephony-magisk

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
- **Method**: hidden AIDL `ITelephony.answerRingingCall()`, reached via
  reflection, requires the app be installed as a Magisk-granted priv-app
  with force-granted `MODIFY_PHONE_STATE`/`READ_PRIVILEGED_PHONE_STATE`
  and `PermissionController` hidden from revoking those grants — exactly
  what `3rdparty/gsm2sip/magisk/` already does in production.
- **Most production-proven of the three siblings** — reuses a real
  (if hidden) Android API rather than input simulation or raw modem
  access.
- **Strong reuse opportunity flagged**: `sdd-voiceline-mode-magisk-v2`
  already owns priv-app-install + `PermissionController`-hide
  infrastructure for a *different* capability (`CAPTURE_AUDIO_OUTPUT`).
  Specifications should evaluate folding this flow's permission set into
  that same module rather than shipping two Magisk modules.
- **Siblings**: `sdd-gateway-answer-keyevent-magisk` (input injection —
  simplest, no priv-app needed) and
  `sdd-gateway-answer-directmodem-magisk` (modem AT command — riskiest).

## Next Actions

1. **None until Anton reopens this flow.** If resumed: confirm with
   `sdd-voiceline-mode-magisk-v2` whether its module can be extended
   rather than duplicated, then move to Specifications.
