# Requirements: Voice Line Mode Direct

> **Version**: 1.0
> **Status**: DRAFT
> **Last Updated**: 2026-03-06
> **Module**: voiceline-mode-direct
> **Dependencies**: `sdd-pjsip-mode-inversion` (right channel inversion)

---

## Problem Statement

**What problem are we solving?**

The GOSTsimbox Android Gateway needs to make **direct calls** into a phone line (GSM radio) via SIP **without Magisk module**, using device's built-in telephony with headphone/earphone output to microphone input loopback.

**Why does this matter?**

This enables:
- Direct SIP-to-GSM call bridging without root/Magisk
- Making phone calls through GSM radio via SIP initiation
- Using device's built-in microphone to capture earphone audio
- Fallback mode when Magisk module is not available

### Use Case

```
User Scenario:
1. User receives SIP call on gateway
2. Gateway initiates GSM call on device
3. Gateway routes SIP audio to earphone output
4. Device microphone captures earphone audio
5. Audio travels: Earphone → Air → Microphone → GSM radio
6. Both parties can communicate (with some quality loss)
```

---

## User Stories

### Primary

**As a** GSM-SIP Gateway User
**I want** to make direct calls into a phone line via SIP without Magisk
**So that** I can bridge SIP calls to GSM radio networks on non-rooted devices

### Secondary

**As a** System Operator
**I want** the call to work without system-level modifications
**So that** I can deploy on standard Android devices

**As a** Developer
**I want** a non-root voice line mode
**So that** I can support wider device compatibility

---

## Acceptance Criteria

### Must Have

1. **Given** an incoming SIP call
   **When** direct mode is enabled
   **Then** GSM call is initiated via Android TelephonyManager

2. **Given** a GSM call is active
   **When** SIP audio is played
   **Then** audio is routed to earphone/speaker output

3. **Given** audio is playing to earphone
   **When** device microphone is active
   **Then** microphone captures earphone audio and sends to GSM radio

4. **Given** a call in progress
   **When** either party speaks
   **Then** both parties can hear each other (acoustic coupling)

### Should Have

1. Support for both mono and stereo SIP streams
2. Any sample rate support (8kHz, 16kHz, 48kHz)
3. Integration with Android telephony for GSM call initiation
4. Call state synchronization between SIP and GSM
5. Echo cancellation (software-based, limited effectiveness)

### Won't Have (This Iteration)

- Hardware differential signaling (no TRRS adapter required)
- Magisk system-level integration
- Perfect echo cancellation (acoustic coupling has inherent limitations)
- TX path processing (GSM → SIP recording)

---

## Constraints

### Technical

- **Must** use PJSIP media endpoint
- **Must** integrate with InversionPort (optional, for better compatibility)
- **Must** use Android TelephonyManager for GSM calls
- **Must** work without root/Magisk

### Performance

- **Must** process frames in real-time (< 10ms latency)
- **Should** minimize acoustic echo (software AEC)
- **May have** lower audio quality than Magisk mode (acoustic coupling)

### Platform

- **Target**: Android with PJSIP 2.9+
- **Integration**: Standard Android API (no root required)
- **Deployment**: Part of GOSTsimbox Android Gateway
- **Hardware**: Works with standard headphones or speakerphone

### Dependencies

- **Requires**: `sdd-pjsip-mode-inversion` - Optional, for better compatibility
- **Requires**: Android TelephonyManager access
- **Requires**: Microphone and speaker/earphone access

---

## Open Questions

- [ ] **Call Initiation**: Intent vs TelephonyManager API?
- [ ] **Audio Routing**: Earphone vs speakerphone?
- [ ] **Echo Cancellation**: How effective can software AEC be?
- [ ] **Volume Control**: Automatic gain control for acoustic coupling?

---

## References

### Related Documentation

- `flows/sdd-pjsip-mode-inversion/` - Right channel inversion (optional dependency)
- `flows/sdd-voiceline-mode-magisk/` - Magisk-based voice line mode (better quality)
- `flows/sdd-voiceline-mode-earphone-to-mic/` - Acoustic coupling mode
- `flows/sdd-android-telecom-integration/` - Android telephony integration

---

## Approval

- [ ] Reviewed by: [name]
- [ ] Approved on: [date]
- [ ] Notes: [any conditions or clarifications]

---

*Created by /sdd - Direct voice line calling without Magisk*
