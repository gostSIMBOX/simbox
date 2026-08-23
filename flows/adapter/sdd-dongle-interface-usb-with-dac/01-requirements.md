# Requirements: Voice Line Adapter USB with DAC (USB Audio Class)

> **Version**: 1.0
> **Status**: DRAFT
> **Last Updated**: 2026-03-07
> **Module**: voiceline-adapter-usb-with-dac
> **Dependencies**: `sdd-pjsip-mode-inversion` (right channel inversion), `sdd-voiceline-mode-direct`

---

## Problem Statement

**What problem are we solving?**

The GOSTsimbox Android Gateway needs a **USB Type-C to phone line adapter** that uses **USB Audio Class (UAC)** with an external DAC to provide high-quality digital-to-analog conversion and differential signaling output to a phone line interface.

**Why does this matter?**

This enables:
- Direct connection to phone lines with high-quality external DAC
- Consistent audio quality across different devices (DAC in adapter)
- Better control over audio characteristics
- Works with any USB Type-C device (no Audio Accessory Mode required)
- Professional-grade audio conversion for phone line interface

### Use Case: USB Audio Class (UAC) Adapter

```
USB Type-C Adapter (Active with DAC):
┌─────────────────────────────────────────────────────────┐
│  USB Type-C Plug                                        │
│  ┌─────────────────────────────────────────────────┐   │
│  │  USB 2.0 Data Lines (D+/D-)                     │   │
│  │  ┌─────────────────────────────────────────┐   │   │
│  │  │  USB Audio Class (UAC) Device           │   │   │
│  │  │  - Digital audio receiver               │   │   │
│  │  │  - External DAC (e.g., PCM2704, DAC)    │   │   │
│  │  └─────────────────────────────────────────┘   │   │
│  │  ┌─────────────────────────────────────────┐   │   │
│  │  │  Differential Circuit (4R+1C)           │   │   │
│  │  │  - Converts [L, -R] to differential     │   │   │
│  │  │  - Analog summing network               │   │   │
│  │  └─────────────────────────────────────────┘   │   │
│  │  ┌─────────────────────────────────────────┐   │   │
│  │  │  RJ11 Jack (Phone Line)                 │   │   │
│  │  └─────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘

Audio Path:
SIP → InversionPort [L, -R] → USB Digital → UAC DAC → 4R+1C Circuit → RJ11 → Phone Line
         (Digital)           (USB Audio)    (External)  (Differential)
```

---

## User Stories

### Primary

**As a** GSM-SIP Gateway Operator
**I want** a USB Type-C adapter with external DAC for phone line connection
**So that** I can achieve consistent, high-quality audio regardless of device

### Secondary

**As a** System Integrator
**I want** a plug-and-play USB Audio Class adapter
**So that** I can deploy on any USB Type-C device without compatibility concerns

**As a** Developer
**I want** to use USB Audio Class for digital audio output
**So that** I can ensure consistent DAC performance across all deployments

---

## Acceptance Criteria

### Must Have

1. **Given** an incoming SIP call
   **When** USB UAC adapter mode is enabled
   **Then** audio is routed to USB Type-C port as digital USB Audio Class stream

2. **Given** USB Audio Class device is connected
   **When** InversionPort processes audio
   **Then** right channel is inverted: [L, R] → [L, -R]

3. **Given** [L, -R] digital audio stream
   **When** converted by external DAC in adapter
   **Then** analog [L, -R] signal is produced

4. **Given** analog [L, -R] signal
   **When** passed through 4R+1C differential circuit
   **Then** differential signal is produced for phone line

### Should Have

1. Support for 48kHz/16-bit and 8kHz/16-bit audio
2. Low-latency USB audio transfer (< 5ms)
3. Impedance matching for phone line (600Ω typical)
4. Self-powered or bus-powered operation
5. LED indicator for call activity

### Won't Have (This Iteration)

- TX path processing (phone line → SIP recording)
- Multiple DAC options (single DAC design)
- Wireless connectivity (USB wired only)

---

## Constraints

### Technical

- **Must** use USB Audio Class 1.0 or 2.0 specification
- **Must** integrate with InversionPort for right channel inversion
- **Must** use external DAC chip (e.g., PCM2704, PCM2902, or similar)
- **Must** use passive 4R+1C differential circuit for phone line

### Performance

- **Must** support 48kHz/16-bit audio minimum
- **Should** have THD+N < 0.01% for clean audio
- **Should** have SNR > 90dB for phone line output
- **Must** have latency < 10ms end-to-end

### Platform

- **Target**: Android devices with USB Type-C and USB Audio Class support
- **Integration**: Standard Android USB audio device API
- **Deployment**: External hardware adapter (active with DAC)
- **Hardware**: USB Type-C plug, UAC DAC chip, 4R+1C circuit, RJ11 jack

### Dependencies

- **Requires**: `sdd-pjsip-mode-inversion` - Right channel inversion
- **Requires**: `sdd-voiceline-mode-direct` - Voice line mode foundation
- **Requires**: USB Audio Class compatible DAC chip
- **Requires**: Android USB audio device API

---

## Open Questions

- [ ] **DAC Selection**: Which DAC chip for optimal cost/performance?
- [ ] **Power**: Bus-powered vs self-powered?
- [ ] **UAC Version**: UAC 1.0 (wider compatibility) vs UAC 2.0?
- [ ] **Impedance Matching**: What resistor values for optimal phone line matching?

---

## References

### Related Documentation

- `flows/sdd-pjsip-mode-inversion/` - Right channel inversion (required)
- `flows/sdd-voiceline-mode-direct/` - Direct voice line mode
- `flows/sdd-voiceline-adapter-usb-without-dac/` - Audio Accessory Mode variant (no DAC)
- USB Audio Class Specification

---

## Approval

- [ ] Reviewed by: [name]
- [ ] Approved on: [date]
- [ ] Notes: [any conditions or clarifications]

---

*Created by /sdd - USB Audio Class adapter with external DAC*
