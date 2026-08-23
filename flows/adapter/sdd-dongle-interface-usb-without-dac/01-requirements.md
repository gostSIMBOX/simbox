# Requirements: Voice Line Adapter USB without DAC (Audio Accessory Mode)

> **Version**: 1.0
> **Status**: DRAFT
> **Last Updated**: 2026-03-07
> **Module**: voiceline-adapter-usb-without-dac
> **Dependencies**: `sdd-pjsip-mode-inversion` (right channel inversion), `sdd-voiceline-mode-direct`

---

## Problem Statement

**What problem are we solving?**

The GOSTsimbox Android Gateway needs a **USB Type-C to phone line adapter** that uses **Audio Accessory Mode** (analog pass-through) to connect the device's internal DAC output directly to a phone line interface via a differential signaling circuit.

**Why does this matter?**

This enables:
- Direct connection to phone lines without acoustic coupling losses
- Uses device's built-in DAC (no external DAC required)
- Lower cost solution (passive adapter, no active electronics)
- Better audio quality than acoustic coupling
- Works with devices supporting USB Type-C Audio Accessory Mode

### Use Case: USB Audio Accessory Mode Adapter

```
USB Type-C Adapter (Passive):
┌─────────────────────────────────────────────────────────┐
│  USB Type-C Plug                                        │
│  ┌─────────────────────────────────────────────────┐   │
│  │  CC Pin: Audio Accessory Mode Detect            │   │
│  │  SBU Pins: Analog Audio Pass-through           │   │
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
SIP → InversionPort [L, -R] → USB-C SBU Pins → 4R+1C Circuit → RJ11 → Phone Line
         (Digital)          (Analog Pass-through)  (Differential)
```

---

## User Stories

### Primary

**As a** GSM-SIP Gateway Operator
**I want** a USB Type-C adapter that connects directly to phone lines
**So that** I can make calls without acoustic coupling quality loss

### Secondary

**As a** System Integrator
**I want** a passive adapter solution (no external power)
**So that** I can deploy with minimal complexity

**As a** Developer
**I want** to use Audio Accessory Mode
**So that** I can leverage device's internal DAC for better audio quality

---

## Acceptance Criteria

### Must Have

1. **Given** an incoming SIP call
   **When** USB adapter mode is enabled
   **Then** audio is routed to USB Type-C port in Audio Accessory Mode

2. **Given** USB Audio Accessory Mode is active
   **When** InversionPort processes audio
   **Then** right channel is inverted: [L, R] → [L, -R]

3. **Given** [L, -R] analog signal on SBU pins
   **When** passed through 4R+1C differential circuit
   **Then** differential signal is produced for phone line

4. **Given** differential signal on phone line
   **When** connected to PSTN/GSM gateway
   **Then** clean audio is transmitted without acoustic losses

### Should Have

1. Support for both mono and stereo SIP streams
2. Any sample rate support (8kHz, 16kHz, 48kHz)
3. Impedance matching for phone line (600Ω typical)
4. Overcurrent protection for USB port
5. ESD protection for RJ11 connector

### Won't Have (This Iteration)

- External DAC (uses device's internal DAC)
- USB Audio Class support (that's the "with-dac" variant)
- Active electronics in adapter
- TX path processing (phone line → SIP recording)

---

## Constraints

### Technical

- **Must** use USB Type-C Audio Accessory Mode specification
- **Must** integrate with InversionPort for right channel inversion
- **Must** use passive 4R+1C differential circuit
- **Must** comply with USB Type-C analog audio specification

### Performance

- **Must** support 48kHz/16-bit audio minimum
- **Should** have frequency response 300Hz - 3.4kHz (phone band)
- **May have** limitations based on device's internal DAC quality

### Platform

- **Target**: Android devices with USB Type-C Audio Accessory Mode support
- **Integration**: Standard Android USB audio API
- **Deployment**: External hardware adapter (passive)
- **Hardware**: USB Type-C plug, RJ11 jack, 4 resistors, 1 capacitor

### Dependencies

- **Requires**: `sdd-pjsip-mode-inversion` - Right channel inversion
- **Requires**: `sdd-voiceline-mode-direct` - Voice line mode foundation
- **Requires**: USB Type-C port with Audio Accessory Mode support
- **Requires**: Android USB audio device API

---

## Open Questions

- [ ] **Device Compatibility**: Which Android devices support Audio Accessory Mode?
- [ ] **Impedance Matching**: What resistor values for optimal phone line matching?
- [ ] **Signal Level**: What is USB-C analog audio output level?
- [ ] **Protection**: What overcurrent/ESD protection is needed?

---

## References

### Related Documentation

- `flows/sdd-pjsip-mode-inversion/` - Right channel inversion (required)
- `flows/sdd-voiceline-mode-direct/` - Direct voice line mode
- `flows/sdd-voiceline-adapter-usb-with-dac/` - UAC variant with external DAC
- USB Type-C Audio Accessory Mode Specification

---

## Approval

- [ ] Reviewed by: [name]
- [ ] Approved on: [date]
- [ ] Notes: [any conditions or clarifications]

---

*Created by /sdd - USB Audio Accessory Mode adapter (passive, no DAC)*
