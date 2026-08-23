# Requirements: Voice Line Mode Earphone-to-Microphone

> **Version**: 1.0
> **Status**: DRAFT
> **Last Updated**: 2026-03-06
> **Module**: voiceline-mode-earphone-to-mic
> **Dependencies**: `sdd-pjsip-mode-inversion` (right channel inversion)

---

## Problem Statement

**What problem are we solving?**

The GOSTsimbox Android Gateway needs to transfer audio from earphone output directly to device microphone input using **physical acoustic coupling** (earphone speaker pressed against microphone) for scenarios where electronic connection is not possible or desired.

**Why does this matter?**

This enables:
- Audio transfer without electronic modification
- Works on any Android device (no root required)
- Useful for legacy systems or locked-down devices
- Physical isolation between SIP and GSM audio paths
- Simple deployment (just position earphone near microphone)

### Use Case: Physical Acoustic Coupling

```
Physical Setup:
┌─────────────────────────────────────────┐
│  Device 1 (Gateway Phone)               │
│  ┌─────────────────────────────────┐   │
│  │  Earphone/Speaker               │   │
│  │  (plays SIP audio)              │   │
│  └─────────────────────────────────┘   │
│           │                             │
│           │ Physical contact            │
│           │ (pressed together)          │
│           ▼                             │
│  ┌─────────────────────────────────┐   │
│  │  Microphone                     │   │
│  │  (captures for GSM call)        │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘

Audio Path:
SIP → Earphone → Physical contact → Microphone → GSM Radio
```

---

## User Stories

### Primary

**As a** GSM-SIP Gateway Operator
**I want** to couple earphone output to microphone input physically
**So that** I can transfer audio without electronic modifications or root access

### Secondary

**As a** System Integrator
**I want** a simple physical setup
**So that** I can deploy quickly without technical complexity

**As a** Developer
**I want** software support for acoustic coupling mode
**So that** I can optimize audio quality for physical coupling

---

## Acceptance Criteria

### Must Have

1. **Given** an incoming SIP call
   **When** earphone-to-mic mode is enabled
   **Then** audio is routed to earphone output at optimal volume

2. **Given** audio is playing to earphone
   **When** earphone is positioned against microphone
   **Then** microphone captures the audio and sends to GSM radio

3. **Given** physical coupling is active
   **When** both parties speak
   **Then** audio is transferred (with some quality loss from acoustic coupling)

4. **Given** earphone-to-mic mode
   **When** active
   **Then** right channel inversion is applied (for differential signaling if supported by hardware)

### Should Have

1. Automatic gain control for optimal acoustic coupling
2. Echo cancellation tuned for acoustic coupling
3. Support for both mono and stereo SIP streams
4. Volume optimization for physical coupling

### Won't Have (This Iteration)

- Electronic audio injection (no direct electrical connection)
- Perfect audio quality (acoustic coupling has inherent limitations)
- Magisk system-level integration
- TX path processing (GSM → SIP recording)

---

## Constraints

### Technical

- **Must** use PJSIP media endpoint
- **Must** integrate with InversionPort for right channel inversion
- **Must** work without root/Magisk
- **Must** support physical acoustic coupling

### Performance

- **Must** process frames in real-time (< 10ms latency)
- **Should** optimize volume for acoustic coupling
- **May have** lower audio quality than electronic connection

### Platform

- **Target**: Android with PJSIP 2.9+
- **Integration**: Standard Android API (no root required)
- **Deployment**: Part of GOSTsimbox Android Gateway
- **Hardware**: Requires earphone/speaker and microphone physical contact

### Dependencies

- **Requires**: `sdd-pjsip-mode-inversion` - Right channel inversion
- **Requires**: Android audio device (earphone output)
- **Requires**: Device microphone access

---

## Open Questions

- [ ] **Volume Level**: What is optimal volume for acoustic coupling?
- [ ] **Echo Cancellation**: How to handle acoustic feedback?
- [ ] **Physical Setup**: Best positioning for earphone-to-mic?
- [ ] **Testing**: How to test without physical setup?

---

## References

### Related Documentation

- `flows/sdd-pjsip-mode-inversion/` - Right channel inversion (required)
- `flows/sdd-voiceline-mode-direct/` - Direct mode (similar, no physical coupling)
- `flows/sdd-voiceline-mode-magisk/` - Magisk mode (electronic injection)

---

## Approval

- [ ] Reviewed by: [name]
- [ ] Approved on: [date]
- [ ] Notes: [any conditions or clarifications]

---

*Created by /sdd - Earphone-to-microphone acoustic coupling mode*
