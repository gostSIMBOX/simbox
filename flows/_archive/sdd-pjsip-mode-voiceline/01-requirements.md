# Requirements: PJSIP Mode Voice Line (Direct Call)

> **Version**: 1.0
> **Status**: DRAFT
> **Last Updated**: 2026-03-06
> **Module**: pjsip-mode-voiceline

---

## Problem Statement

**What problem are we solving?**

The GOSTsimbox Android Gateway needs to make direct calls into a phone line (GSM radio) via SIP, using hardware adapter connectivity with differential signaling for echo-free audio playback.

**Why does this matter?**

This enables:
- Direct SIP-to-GSM call bridging
- Making phone calls through GSM radio via SIP initiation
- Integration with external GSM hardware via TRRS/USB adapters
- Echo-free audio through differential signaling

---

## User Stories

### Primary

**As a** GSM-SIP Gateway User
**I want** to make calls directly into a phone line via SIP
**So that** I can bridge SIP calls to GSM radio networks

### Secondary

**As a** System Operator
**I want** the call to have clear audio without echo
**So that** both parties can communicate effectively

**As a** Developer
**I want** a reusable PJSIP mode for voice line calls
**So that** I can integrate direct GSM calling into applications

---

## Acceptance Criteria

### Must Have

1. **Given** an incoming SIP call
   **When** voice line mode is enabled
   **Then** call is routed to GSM radio via hardware adapter

2. **Given** a call is established
   **When** audio flows through voice line mode
   **Then** right channel is inverted for differential signaling

3. **Given** audio is played to phone line
   **When** phone's echo canceller processes the signal
   **Then** echo is cancelled and audio is clear

4. **Given** a call in progress
   **When** either party speaks
   **Then** both parties can hear each other without echo feedback

### Should Have

1. Support for both mono and stereo SIP streams
2. Any sample rate support (8kHz, 16kHz, 48kHz)
3. Integration with Android telephony for GSM call initiation
4. Call state synchronization between SIP and GSM

### Won't Have (This Iteration)

- TX path processing (GSM → SIP recording)
- Hardware detection/auto-switching
- Multi-call conferencing
- Call recording features

---

## Constraints

### Technical

- **Must** use PJSIP media endpoint
- **Must** integrate with InversionPort for right channel inversion
- **Must** work with Android JNI audio device
- **Must** integrate with nmpjsip-builder patch structure

### Performance

- **Must** process frames in real-time (< 10ms latency)
- **Must** maintain call quality (no audio artifacts)
- **Should** minimize CPU usage

### Platform

- **Target**: Android with PJSIP 2.9+
- **Integration**: nmpjsip-builder/src/patch_2.9/
- **Deployment**: Part of GOSTsimbox Android Gateway
- **Hardware**: TRRS or USB hardware adapter required

### Dependencies

- **Requires**: `sdd-pjsip-mode-inversion` - Right channel inversion
- **Requires**: `sdd-voiceline-hardwarejack-mode` - Hardware adapter integration
- Requires PJSIP media endpoint initialization
- Requires Android telephony for GSM call control

---

## Open Questions

- [ ] **Call Initiation**: How is GSM call triggered? (Intent, TelephonyManager?)
- [ ] **Call State Sync**: How to synchronize SIP and GSM call states?
- [ ] **Error Handling**: What if GSM call fails?
- [ ] **Testing**: How to test without physical GSM hardware?

---

## References

### Related Documentation

- `flows/sdd-pjsip-mode-inversion/` - Right channel inversion (dependency)
- `flows/sdd-voiceline-hardwarejack-mode/` - Hardware jack integration (uses inversion)
- `flows/sdd-android-telecom-integration/` - Android telephony integration
- `flows/sdd-magisk-voice-recording/` - Magisk module for voice recording

### PJSIP References

- pjmedia_port API: https://pjogndoc.appspot.com/html/structpjmedia__port.html
- Call management: https://github.com/pjsip/pjproject/tree/master/pjsip

---

## Approval

- [ ] Reviewed by: [name]
- [ ] Approved on: [date]
- [ ] Notes: [any conditions or clarifications]

---

*Created by /sdd - Direct voice line calling mode*
