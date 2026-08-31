# Requirements: Gateway Auto-Answer via KEYCODE_CALL Injection (Magisk)

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
the call to SIP — the call rings, but the Gateway can't pick it up.

This is one of three non-standard ways to answer a call without holding
default-dialer status (siblings:
`sdd-gateway-answer-itelephony-magisk`,
`sdd-gateway-answer-directmodem-magisk`). This method: with root/Magisk,
run `input keyevent KEYCODE_CALL` — a system-level simulated press of the
hardware "answer" key. Because it operates at the input-injection layer,
not through `InCallService`, it works **regardless of default-dialer
status**.

## User Stories

### Primary

**As a** developer evaluating auto-answer options for the Gateway
**I want** to know whether input-injection can answer an incoming GSM
call without default-dialer status
**So that** the Gateway can bridge GSM→SIP on devices where setting the
default dialer is undesirable or unavailable

## Acceptance Criteria

### Must Have

1. **Given** a rooted device with Magisk and an incoming GSM call
   ringing, **when** the app detects the ringing state (via
   `TelephonyManager`'s call-state listener — available to any app, not
   just the default dialer) and shells out `su -c "input keyevent
   KEYCODE_CALL"`, **then** the call is answered without this app holding
   default-dialer status.
2. **Given** the call is answered this way, **when** the Gateway needs to
   bridge audio to SIP, **then** Specifications must confirm whether
   Android's standard audio stack still routes call audio normally after
   an injected-keyevent answer (expected: yes, since Android's own
   Telecom framework registers the call as answered through its normal
   UI path — unlike the direct-modem method, this doesn't bypass
   Telecom, only the *permission* to trigger answer).

### Should Have

- Detect and log injection failures (e.g., OEM key-handling overrides)
  rather than silently doing nothing.

### Won't Have (This Iteration)

- Any actual implementation — this flow stays at Requirements until
  explicitly reopened.
- Answering on non-rooted devices (out of scope by definition).

## Constraints

- **Technical**: Requires root (`su` binary) and a shell-exec bridge from
  Dart/Kotlin — no library in this repo currently owns that; Specifications
  must name where it lives (candidate: `flutter_gsmsip` platform channel,
  or a shared root-utility module referenced by all three sibling flows).
- **Reliability**: device/OEM-dependent — some manufacturers remap or
  intercept `KEYCODE_CALL` before it reaches the standard input pipeline;
  no known device-compatibility list exists yet.
- **Timing**: requires reliably detecting "ringing" state first, and racing
  against the stock dialer UI, which will still show its own incoming-call
  screen (unaffected by which app injects the keyevent).
- **Dependencies**: shares "does this need Magisk at all vs. plain `su`"
  question with the sibling flows — some devices allow raw `input
  keyevent` via ADB shell without a Magisk module specifically, only root.

## Open Questions

- [ ] Does this work reliably when the screen is locked / off?
- [ ] Race condition: does the stock incoming-call UI need to be dismissed
      separately, or does answering via keyevent also dismiss it?
- [ ] Is a full Magisk module needed here, or does plain root (`su`)
      suffice, unlike `sdd-gateway-answer-itelephony-magisk`'s priv-app
      requirement? If the latter, the "_magisk" naming may overstate the
      dependency — revisit at Specifications.

## References

- `flows/flutter_gsmsip/vdd-flutter_gsmsip-example-uiux/01-requirements.md`
  AC4 — the consumer of this capability (Gateway screen's Default Dialer
  warning); this flow is the parked "what if we bypass it" alternative,
  not a dependency of AC4's current warn-only behavior.
- `flows/flutter_gsmsip/sdd-gateway-answer-itelephony-magisk/` — sibling
  method (priv-app hidden API)
- `flows/flutter_gsmsip/sdd-gateway-answer-directmodem-magisk/` — sibling
  method (modem-level AT command)
- `flows/flutter_gsmsip/sdd-voiceline-mode-magisk-v2/` — existing Magisk
  module precedent (different capability — audio capture, not call
  answering — but shares the "priv-app + Magisk module" delivery
  mechanism if Specifications concludes plain root isn't enough)

---

## Approval

- [ ] Reviewed by: Anton
- [ ] Approved on:
- [ ] Notes: Parked at Anton's explicit request (2026-08-31) — documented
      for future reference, not scheduled for implementation.
