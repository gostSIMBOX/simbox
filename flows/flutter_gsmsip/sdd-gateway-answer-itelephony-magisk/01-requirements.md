# Requirements: Gateway Auto-Answer via ITelephony.answerRingingCall() (Magisk priv-app)

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-08-31
> **Parked — do not implement.** Split out of `vdd-flutter_gsmsip-example-uiux`
> at Anton's request to document the option, not to schedule it.

## Problem Statement

An incoming GSM call always physically rings on the device — that's the
OS's Telecom framework, independent of whether this app is the default
dialer. What default-dialer status actually gates is **programmatic
auto-answer + audio interception**: the standard `InCallService`/
`ConnectionService` API only grants answer control to whichever app is
currently set as the default dialer. Without that status,
`GatewayService._handleIncomingGsmCall()` cannot auto-answer and bridge
the call to SIP.

This is one of three non-standard ways to answer a call without holding
default-dialer status (siblings: `sdd-gateway-answer-keyevent-magisk`,
`sdd-gateway-answer-directmodem-magisk`). This method: the hidden AIDL
API `com.android.internal.telephony.ITelephony.answerRingingCall()`
answers the current ringing call directly, but is signature/privileged-
protected — normal apps can't call it via reflection. Root/Magisk can
install the APK as a **priv-app**, **force-grant** the runtime
permissions it needs (`MODIFY_PHONE_STATE`, `READ_PRIVILEGED_PHONE_STATE`),
and **hide `PermissionController`** at the filesystem level so those
grants can't be silently revoked. This is exactly what `gsm2sip`'s
existing Magisk module (`3rdparty/gsm2sip/magisk/`) does, and it's the
most reliable of the three methods since it uses a real, if hidden,
Android API rather than input simulation or raw modem access.

## User Stories

### Primary

**As a** developer evaluating auto-answer options for the Gateway
**I want** to know whether a priv-app-granted hidden Telephony API can
answer an incoming GSM call without default-dialer status
**So that** the Gateway can bridge GSM→SIP with the same reliability
`gsm2sip` already demonstrates in production

## Acceptance Criteria

### Must Have

1. **Given** a device with this app's Magisk module installed (priv-app
   + force-granted `MODIFY_PHONE_STATE`/`READ_PRIVILEGED_PHONE_STATE`)
   and an incoming GSM call ringing, **when** the app calls
   `ITelephony.answerRingingCall()` via reflection over
   `ServiceManager.getService(Context.TELEPHONY_SERVICE)`, **then** the
   call is answered without this app holding default-dialer status.
2. **Given** `gsm2sip`'s magisk module already implements this exact
   mechanism, **when** Specifications are written, **then** they document
   the delta needed to retarget it at `flutter_gsmsip/example`'s actual
   `applicationId` (`org.telon.flutter_gsmsip_example`) rather than
   `gsm2sip`'s `com.callagent.gateway` — same re-targeting gap already
   flagged in `vdd-flutter_gsmsip-example-uiux/01-requirements.md`'s
   Permission Audit for `sdd-voiceline-mode-magisk-v2`.
3. **Given** `sdd-voiceline-mode-magisk-v2` already owns priv-app
   installation + `PermissionController`-hiding infrastructure (for a
   *different* capability, `CAPTURE_AUDIO_OUTPUT`), **when**
   Specifications are written, **then** they evaluate reusing that same
   install/hide machinery for this capability's permission set instead of
   building a second, parallel Magisk module.

### Should Have

- A single shared Magisk module covering both this flow's permissions
  and `sdd-voiceline-mode-magisk-v2`'s, rather than two separately
  installed modules on the same device.

### Won't Have (This Iteration)

- Any actual implementation — this flow stays at Requirements until
  explicitly reopened.
- A new Magisk module distinct from `sdd-voiceline-mode-magisk-v2`'s,
  unless Specifications concludes the permission sets can't share one.

## Constraints

- **Technical**: hidden/internal API — no stable AIDL interface guarantee
  across Android versions; reflection call signature may need per-OS-
  version handling.
- **Delivery mechanism**: requires the full Magisk priv-app install +
  permission force-grant + `PermissionController` hiding — the heaviest
  of the three sibling methods to set up, but (per `gsm2sip`) the most
  production-proven.
- **Dependencies**: retargeting `sdd-voiceline-mode-magisk-v2` (or a
  shared successor module) to `org.telon.flutter_gsmsip_example` is a
  precondition for demonstrating this for real in the example app — same
  dependency already flagged in `vdd-flutter_gsmsip-example-uiux`.

## Open Questions

- [ ] Can this flow's permission set be folded into
      `sdd-voiceline-mode-magisk-v2`'s existing module, or does it need
      its own `privapp-permissions-*.xml`?
- [ ] Does `ITelephony`'s AIDL signature for `answerRingingCall()` vary
      across the Android versions this Gateway targets?
- [ ] After answering this way, does audio route through the app's
      normal `InCallService`-adjacent audio path, or does bridging to SIP
      need a separate audio-capture step (tie-in with
      `sdd-voiceline-mode-magisk-v2`'s `CAPTURE_AUDIO_OUTPUT` capability)?

## References

- `flows/flutter_gsmsip/vdd-flutter_gsmsip-example-uiux/01-requirements.md`
  AC4 — the consumer of this capability (Gateway screen's Default Dialer
  warning); this flow is the parked "what if we bypass it" alternative,
  not a dependency of AC4's current warn-only behavior.
- `3rdparty/gsm2sip/magisk/` — working reference implementation of the
  priv-app + force-grant + hide-PermissionController mechanism
- `flows/flutter_gsmsip/sdd-voiceline-mode-magisk-v2/` — owns the existing
  priv-app install/hide infrastructure for a different capability;
  strong candidate for sharing rather than duplicating
- `flows/flutter_gsmsip/sdd-gateway-answer-keyevent-magisk/` — sibling
  method (input-injection)
- `flows/flutter_gsmsip/sdd-gateway-answer-directmodem-magisk/` — sibling
  method (modem-level AT command)

---

## Approval

- [ ] Reviewed by: Anton
- [ ] Approved on:
- [ ] Notes: Parked at Anton's explicit request (2026-08-31) — documented
      for future reference, not scheduled for implementation.
