# Requirements: RECEIVE_MMS / RECEIVE_WAP_PUSH Cleanup

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-08-31

## Problem Statement

`libsFlutter/flutter_gsmsip/example`'s `AndroidManifest.xml` declares
`android.permission.RECEIVE_MMS` and `android.permission.RECEIVE_WAP_PUSH`,
but no code anywhere in this repository backs them:

- `flutter_smsussd`'s own manifest (`android/src/main/AndroidManifest.xml`)
  declares only `SEND_SMS`/`RECEIVE_SMS`/`READ_SMS`/`WRITE_SMS`/
  `READ_PHONE_STATE` — no MMS or WAP-push permissions at all.
- `flutter_smsussd`'s only native class,
  `FlutterSmsussdPlugin.kt`, has zero MMS/WAP-push handling — confirmed
  by grep, no matches for `MMS`/`WAP_PUSH`/`WapPush` anywhere in
  `android/src/`.
- No `BroadcastReceiver` for `SMS_RECEIVED`/`WAP_PUSH_RECEIVED` intents
  exists in `flutter_smsussd`, `flutter_gsmsip`, or `flutter_gsmsip/example`
  itself.

This was found during `flows/flutter_gsmsip/vdd-flutter_gsmsip-example-uiux`'s
Permission Audit (see that flow's `01-requirements.md`) and flagged again
as an open checkpoint (Task 5.2) in its `04-plan.md` — moved here because
this is a `flutter_smsussd`-scoped correctness question, not a UI/UX
decision for the gateway example app.

## User Stories

### Primary

**As a** developer maintaining `flutter_gsmsip/example`'s manifest
**I want** to know whether `RECEIVE_MMS`/`RECEIVE_WAP_PUSH` are safe to
delete or need a real implementation
**So that** the manifest doesn't carry permissions that request user
trust for a capability the app doesn't actually have

## Acceptance Criteria

### Must Have

1. **Given** the confirmed absence of any MMS/WAP-push handling code in
   `flutter_smsussd` or anywhere else in the repo, **when** this flow
   reaches a decision, **then** it is one of exactly two outcomes:
   (a) delete both permissions from `flutter_gsmsip/example`'s manifest
   (no functionality lost, since nothing uses them today), or
   (b) MMS/WAP-push handling is confirmed as an actual planned feature,
   in which case this flow's scope expands to speccing that feature
   properly in `flutter_smsussd` (not left as a dangling permission).
2. **Given** outcome (a) is chosen, **when** Specifications are written,
   **then** they identify every file across the repo (not just the one
   already-found manifest) that declares either permission, so the fix
   isn't partial.

### Won't Have (This Iteration)

- Building actual MMS/WAP-push receive support, unless Anton confirms
  outcome (b) above.

## Constraints

- **Scope**: this touches `flutter_gsmsip/example`'s manifest (where the
  permissions currently live) and, if outcome (b), `flutter_smsussd`'s own
  manifest/source — not `flutter_gsmsip/lib/**`.
- **Dependency**: `flows/flutter_gsmsip/vdd-flutter_gsmsip-example-uiux`'s
  Task 5.2 is waiting on this flow's outcome before its own permission
  manifest comment-block task can mark this line item resolved.

## Open Questions

- [ ] **The core question**: does Anton want MMS/WAP-push receive support
      as an actual feature, or is this pure historical cruft to delete?
      Nothing in the codebase argues for keeping it as-is; deletion is the
      default recommendation pending Anton's answer.

## References

- `flows/flutter_gsmsip/vdd-flutter_gsmsip-example-uiux/01-requirements.md`
  — Permission Audit section, original finding
- `flows/flutter_gsmsip/vdd-flutter_gsmsip-example-uiux/04-plan.md` —
  Task 5.2, the checkpoint this flow replaces
- `libsFlutter/flutter_smsussd/android/src/main/AndroidManifest.xml` —
  the package's actual, correctly-scoped manifest (no MMS/WAP-push)
- `libsFlutter/flutter_smsussd/android/src/main/kotlin/net/nativemind/libs/flutter/smsussd/flutter_smsussd/FlutterSmsussdPlugin.kt`
  — the package's only native class, confirmed to have no MMS/WAP-push code

---

## Approval

- [ ] Reviewed by: Anton
- [ ] Approved on:
- [ ] Notes:
