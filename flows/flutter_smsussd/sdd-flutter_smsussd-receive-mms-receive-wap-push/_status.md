# Status: sdd-flutter_smsussd-receive-mms-receive-wap-push

## Current Phase

**REQUIREMENTS** | SPECIFICATIONS | PLAN | IMPLEMENTATION | DOCUMENTATION

## Phase Status

**DRAFTING**

## Last Updated

2026-08-31 by Claude (split out of
`flows/flutter_gsmsip/vdd-flutter_gsmsip-example-uiux`'s Task 5.2 at
Anton's explicit request, since this is a `flutter_smsussd`-scoped
correctness question, not a UI/UX decision for that flow)

## Blockers

- Awaiting Anton's answer to the one Open Question: delete
  `RECEIVE_MMS`/`RECEIVE_WAP_PUSH` as cruft, or is MMS/WAP-push receive
  an actual planned feature? No code anywhere in the repo argues for
  keeping them as-is — deletion is the default recommendation.

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

- **Origin**: `vdd-flutter_gsmsip-example-uiux`'s Permission Audit
  (01-requirements.md) found `RECEIVE_MMS`/`RECEIVE_WAP_PUSH` declared
  only in `flutter_gsmsip/example`'s manifest with zero backing code
  anywhere — flagged as "unbacked cruft," carried into that flow's
  `04-plan.md` as Task 5.2 (an approval checkpoint, not a coded task).
  Anton asked for it to be its own SDD flow instead of a footnote there.
- **Confirmed empty-handed**: grepped `flutter_smsussd`'s entire
  `android/src/` for `MMS`/`WAP_PUSH`/`WapPush` — zero matches. Its own
  manifest doesn't declare these permissions either. This isn't a
  "permission declared in the wrong file" gap (unlike most of the audit's
  other findings) — it's a permission with **no owner anywhere**.
- **Two possible outcomes**, both acceptable, both need Anton's call:
  delete (default recommendation) or spec a real feature.

## Next Actions

1. Get "requirements approved" from Anton, specifically an answer to the
   one Open Question above.
2. If deletion: Specifications just needs to enumerate every file
   declaring either permission (only one found so far,
   `flutter_gsmsip/example`'s manifest — Specifications should
   double-check nothing else does before calling it complete).
3. If real feature: Specifications scopes actual MMS/WAP-push receive
   support in `flutter_smsussd` from scratch.
4. Once resolved, notify `vdd-flutter_gsmsip-example-uiux` so its Task
   5.2 checkpoint can close (cross-reference already added there).
