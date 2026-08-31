# Requirements: Gateway Auto-Answer via Direct Modem AT Command (Magisk)

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-08-31
> **Parked — do not implement.** Split out of `vdd-flutter_gsmsip-example-uiux`
> at Anton's request to document the option, not to schedule it.

## Problem Statement

An incoming GSM call always physically rings on the device — that's the
OS's Telecom framework, independent of whether this app is the default
dialer. What default-dialer status actually gates is **programmatic
auto-answer + audio interception** through Android's standard
`InCallService`/`ConnectionService` API. This method sidesteps that API
**entirely**: with root access to the modem's serial/TTY interface
(`/dev/ttyUSB*`, `/dev/smd*`, etc. — same device-specific paths already
flagged as an open question in
`vdd-flutter_gsmsip-example-voiceline-uiux`), the app issues the AT
command `ATA` directly to the baseband to answer the ringing call. This
happens below Android's Telecom stack — default-dialer status is
irrelevant because Android's framework isn't involved in "answering" at
all. This is the same modem-access layer as `sdd-voiceline-mode-direct`
("Direct Mode"), but that flow only uses it for **audio path** (acoustic
coupling); this flow is about using it for **call control**.

This is one of three non-standard ways to answer a call without holding
default-dialer status (siblings: `sdd-gateway-answer-keyevent-magisk`,
`sdd-gateway-answer-itelephony-magisk`).

## User Stories

### Primary

**As a** developer evaluating auto-answer options for the Gateway
**I want** to know whether direct modem AT commands can answer an
incoming GSM call fully outside Android's Telecom framework
**So that** the Gateway has an option that works even on devices where
neither input-injection nor priv-app API access is viable

## Acceptance Criteria

### Must Have

1. **Given** root access to the device's modem TTY port and an incoming
   GSM call ringing, **when** the app sends `ATA` over that port, **then**
   the call is answered at the modem level, independent of Android's
   Telecom/`InCallService` stack and default-dialer status.
2. **Given** the modem answers the call but Android's own Telecom
   framework was never told to answer it, **when** Specifications are
   written, **then** they must resolve the **serious open risk** flagged
   below: Android will likely still show the call as "ringing" in its
   own state model while the modem believes it's answered — a state
   desync between the OS and the radio that the standard `RIL` daemon
   isn't expecting, and that could produce undefined behavior (dropped
   call, stuck ringing UI, RIL crash) depending on vendor implementation.
3. **Given** the Gateway ultimately needs to bridge this call's audio
   into SIP, **when** Specifications are written, **then** they confirm
   whether Android's audio stack delivers *any* call audio when the OS
   itself never recognized the call as answered — if not, audio would
   also need to come from the direct-modem/TTY layer (same territory as
   `sdd-voiceline-mode-direct`'s acoustic-coupling approach), not the
   app's normal audio pipeline.

### Should Have

- A documented fallback: detect if the OS's own Telecom state and the
  modem's state diverge, and recover (e.g., end the call cleanly) rather
  than leave the device in a stuck state.

### Won't Have (This Iteration)

- Any actual implementation — this flow stays at Requirements until
  explicitly reopened.
- A device/TTY-path compatibility database (same gap already open in
  `vdd-flutter_gsmsip-example-voiceline-uiux`; this flow inherits it
  rather than re-solving it).

## Constraints

- **Technical**: modem TTY device nodes are typically restricted to the
  `radio`/`system` UID via SELinux — root alone may not suffice on
  hardened OEM builds; may require additional SELinux policy changes via
  Magisk, not just `su`.
- **Highest risk of the three siblings**: bypassing the RIL's own control
  of the modem while the RIL is still running is architecturally unlike
  the other two methods (which stay inside Android's frameworks, just
  without default-dialer permission) — this one has two independent
  actors (RIL + this app) both believing they control the same modem
  state machine.
- **Device-specific**: TTY port paths are model/manufacturer-specific,
  same gap already tracked in
  `vdd-flutter_gsmsip-example-voiceline-uiux/01-requirements.md`.

## Open Questions

- [ ] Does issuing `ATA` directly while the stock RIL daemon is also
      attached to the same port cause a conflict, or does the modem
      multiplex AT commands from multiple readers safely?
- [ ] After a direct-modem answer, does Android's Telecom framework
      eventually reconcile its "ringing" state on its own (e.g., via the
      RIL's own unsolicited response handling), or does it stay
      permanently desynced until the call ends?
- [ ] Is audio bridging to SIP even possible via the app's normal audio
      pipeline if Android's framework never recognized the call as
      answered — or does this method require its own acoustic-coupling-
      style audio path, same as `sdd-voiceline-mode-direct`?
- [ ] Should this be considered only as a last-resort fallback (behind
      the other two sibling methods), given the state-desync risk?

## References

- `flows/flutter_gsmsip/vdd-flutter_gsmsip-example-uiux/01-requirements.md`
  AC4 — the consumer of this capability (Gateway screen's Default Dialer
  warning); this flow is the parked "what if we bypass it" alternative,
  not a dependency of AC4's current warn-only behavior.
- `flows/flutter_gsmsip/sdd-voiceline-mode-direct/` — established the
  TTY-access precedent and shares the device/path-database gap (for
  audio path, not call control)
- `flows/flutter_gsmsip/vdd-flutter_gsmsip-example-voiceline-uiux/` —
  owns the TTY-port-path "device database" open question this flow
  inherits rather than re-opens
- `flows/flutter_gsmsip/sdd-gateway-answer-keyevent-magisk/` — sibling
  method (input-injection)
- `flows/flutter_gsmsip/sdd-gateway-answer-itelephony-magisk/` — sibling
  method (priv-app hidden API)

---

## Approval

- [ ] Reviewed by: Anton
- [ ] Approved on:
- [ ] Notes: Parked at Anton's explicit request (2026-08-31) — documented
      for future reference, not scheduled for implementation. Flagged as
      the riskiest of the three sibling methods (RIL/modem state-desync
      concern) — likely a last-resort option, not a first choice, pending
      Specifications resolving the open questions above.
