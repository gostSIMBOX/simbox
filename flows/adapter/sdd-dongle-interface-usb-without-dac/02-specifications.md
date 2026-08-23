# Specifications: Voice Line Adapter USB without DAC (Audio Accessory Mode)

> **Version**: 1.0
> **Status**: DRAFT
> **Last Updated**: 2026-03-07
> **Requirements**: [01-requirements.md](01-requirements.md)

---

## Overview

This document specifies the implementation of a **USB Type-C Audio Accessory Mode adapter** for direct phone line connection. This is a **passive adapter** that uses the device's internal DAC and analog pass-through via SBU pins.

**Key Characteristics**:
- Passive adapter (no external DAC, no active electronics)
- Uses USB Type-C Audio Accessory Mode specification
- Requires InversionPort for right channel inversion
- 4R+1C differential circuit for phone line interface

---

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  USB Audio Accessory Mode Adapter Architecture               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐                                       │
│  │  SIP Call (RX)   │                                       │
│  └────────┬─────────┘                                       │
│           │                                                  │
│           ▼                                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  InversionPort (REQUIRED from sdd-pjsip-mode-...)    │   │
│  │  - Mono: [L] → [L, -L]                               │   │
│  │  - Stereo: [L, R] → [L, -R]                          │   │
│  └────────┬─────────────────────────────────────────────┘   │
│           │                                                  │
│           │ [L, -R] analog output                            │
│           ▼                                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Android Audio Device (USB Analog Audio)             │   │
│  │  - Routes to SBU1/SBU2 pins                          │   │
│  └────────┬─────────────────────────────────────────────┘   │
│           │                                                  │
│           │ Analog [L, -R] on SBU pins                       │
│           ▼                                                  │
│  ╔══════════════════════════════════════════════════════╗   │
│  ║  USB Type-C Adapter (PASSIVE)                         ║   │
│  ║  ┌────────────────────────────────────────────────┐  ║   │
│  ║  │  4R+1C Differential Circuit                    │  ║   │
│  ║  │  - R1, R2: Left channel path                   │  ║   │
│  ║  │  - R3, R4: Right channel path (inverted)       │  ║   │
│  ║  │  - C1: DC blocking / AC coupling               │  ║   │
│  ║  └────────────────────────────────────────────────┘  ║   │
│  ║  ┌────────────────────────────────────────────────┐  ║   │
│  ║  │  RJ11 Jack (Phone Line)                        │  ║   │
│  ║  │  - TIP: Differential +                         │  ║   │
│  ║  │  - RING: Differential -                        │  ║   │
│  ║  └────────────────────────────────────────────────┘  ║   │
│  ╚══════════════════════════════════════════════════════╝   │
│           │                                                  │
│           ▼                                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Phone Line (PSTN / GSM Gateway)                     │   │
│  │  - Receives differential audio signal                │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### USB Type-C Pinout (Audio Accessory Mode)

```
┌─────────────────────────────────────────────────────────────┐
│  USB Type-C Receptacle - Audio Accessory Mode Pinout         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  A1  GND          ┌──┐          B1  GND                     │
│  A2  TX1+         │  │          B2  TX1-                     │
│  A3  TX1-         │  │          B3  TX1+                     │
│  A4  VBUS         │  │          B4  VBUS                     │
│  A5  CC1    ──────┤◦ ◦│───────── B5  CC2          (Config)   │
│  A6  D+     ──────┤  │───────── B6  D-           (USB 2.0)   │
│  A7  D-     ──────┤  │───────── B7  D+           (USB 2.0)   │
│  A8  SBU1   ──────┤  │───────── B8  SBU2         (Audio L)   │
│  A9  VBUS         │  │          B9  VBUS                     │
│  A10 RX1-         │  │          B10 RX1+                    │
│  A11 RX1+         │  │          B11 RX1-                    │
│  A12 GND          └──┘          B12 GND                     │
│                                                              │
│  Audio Accessory Mode:                                       │
│  - SBU1: Analog Left Audio (L)                               │
│  - SBU2: Analog Right Audio (-R, inverted)                   │
│  - CC1/CC2: Detect Audio Accessory Mode (Ra pull-down)       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 4R+1C Differential Circuit

```
┌─────────────────────────────────────────────────────────────┐
│  4R+1C Differential Circuit Schematic                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  SBU1 (L) ────R1────┬────────R3──── TIP (+)                 │
│                     │                                        │
│                    C1                                        │
│                     │                                        │
│  SBU2 (-R) ───R2────┴────────R4──── RING (-)                 │
│                                                              │
│  Component Values (typical):                                 │
│  - R1, R2: 10kΩ (input impedance)                            │
│  - R3, R4: 10kΩ (output impedance)                           │
│  - C1: 100nF (DC blocking, AC coupling)                      │
│                                                              │
│  Circuit Function:                                           │
│  - Creates differential signal: TIP - RING = L - (-R)        │
│  - DC blocking via C1 prevents DC offset on phone line       │
│  - Impedance matching for phone line (600Ω typical)          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Location

### Software Files (GOSTsimbox Android Gateway)

```
nmpjsip-builder/src/patch_2.9/src/pjsip2/pjmedia/src/pjmedia-audiodev/voiceline_mode_usb_accessory.c
nmpjsip-builder/src/patch_2.9/src/pjsip2/pjmedia/include/pjmedia-audiodev/voiceline_mode_usb_accessory.h
```

### Modified Files

```
nmpjsip-builder/src/patch_2.9/src/pjsip2/pjmedia/src/pjmedia-audiodev/android_jni_dev.c
  - Include USB accessory mode header
  - Create InversionPort (required)
  - Route audio to USB Type-C SBU pins
  - Configure for analog audio output
```

### Hardware Files (Adapter Design)

```
hardware/voiceline-adapter-usb-without-dac/
  - schematic.pdf (4R+1C circuit)
  - bom.csv (Bill of Materials)
  - gerbers/ (PCB fabrication files)
  - assembly.md (Assembly instructions)
```

---

## Audio Routing

### Signal Chain

```
1. SIP Media Stream (RX)
   Input: Mono [L] or Stereo [L, R]
   
2. InversionPort (SOFTWARE INVERSION)
   Mono:   [L] → [L, -L]
   Stereo: [L, R] → [L, -R]
   
3. Android Audio Device (USB Analog Output)
   Routes [L, -R] to SBU1/SBU2 pins
   
4. USB Type-C Connector (Audio Accessory Mode)
   SBU1: L (analog)
   SBU2: -R (analog, inverted)
   
5. 4R+1C Differential Circuit
   Analog summing: L - (-R) = L + R (differential)
   
6. RJ11 Connector
   TIP: Differential +
   RING: Differential -
   
7. Phone Line
   Receives differential audio signal
```

---

## Configuration

### Compile-Time Options

```cpp
// Enable USB Audio Accessory Mode
#define PJMEDIA_VOICELINE_USB_ACCESSORY_ENABLED 1

// Require InversionPort
#define VOICELINE_USB_ACCESSORY_REQUIRE_INVERSION 1
```

### Runtime Configuration

```cpp
typedef struct voiceline_usb_accessory_config {
    pj_bool_t enabled;              // Enable USB accessory mode
    pj_bool_t use_inversion;        // Use InversionPort (required)
    pjmedia_format_id format;       // Audio format (typically 48kHz/16-bit)
    int output_volume;              // Output volume (0-100)
} voiceline_usb_accessory_config_t;
```

---

## Hardware Specifications

### Bill of Materials (BOM)

| Component | Value | Quantity | Package | Notes |
|-----------|-------|----------|---------|-------|
| R1, R2 | 10kΩ | 2 | 0603 | Input resistors |
| R3, R4 | 10kΩ | 2 | 0603 | Output resistors |
| C1 | 100nF | 1 | 0603 | DC blocking capacitor |
| J1 | USB Type-C | 1 | - | Receptacle |
| J2 | RJ11 | 1 | - | Phone line jack |
| PCB | - | 1 | - | 2-layer board |

### Enclosure

- 3D printed or small plastic enclosure
- USB Type-C plug exposed
- RJ11 jack accessible
- Compact size (~30mm x 20mm x 10mm)

---

## Testing Strategy

### Unit Tests

```cpp
// Test USB accessory mode initialization
TEST(USBAcessory, Initialization) {
    // Verify InversionPort is created
    // Verify audio routing to USB SBU pins
}

// Test inversion is applied
TEST(USBAcessory, InversionApplied) {
    // Verify [L, R] → [L, -R] transformation
}
```

### Integration Tests

```cpp
// Test with phone line
TEST(USBAcessoryIntegration, PhoneLineCall) {
    // Setup: Connect USB adapter to phone line
    // Make SIP call
    // Verify audio quality on phone line
    // Verify differential signaling
}
```

### Manual Verification

1. Build GOSTsimbox with USB accessory mode
2. Build/connect USB Type-C adapter (4R+1C circuit)
3. Plug adapter into device USB Type-C port
4. Connect RJ11 to phone line / GSM gateway
5. Make SIP call
6. Verify audio quality on phone line
7. Test with mono and stereo sources

---

## Dependencies

### Requires

- **sdd-pjsip-mode-inversion** - InversionPort (required)
- **sdd-voiceline-mode-direct** - Voice line mode foundation
- **USB Type-C port** - With Audio Accessory Mode support
- **Android USB audio API** - For analog audio routing

### Device Compatibility

| Device | Audio Accessory Mode | Notes |
|--------|---------------------|-------|
| Google Pixel | ✓ | Confirmed |
| Samsung Galaxy | ✓ | Most models |
| Huawei | ✓ | Most models |
| Xiaomi | ? | Needs testing |

---

## Open Design Questions

- [ ] **Resistor Values**: Optimal values for different phone line impedances?
- [ ] **Capacitor Value**: Trade-offs for different C1 values?
- [ ] **ESD Protection**: What level of protection is needed?
- [ ] **Enclosure**: Standard design or custom per deployment?

---

## Approval

- [ ] Reviewed by: [name]
- [ ] Approved on: [date]
- [ ] Notes: [any conditions or clarifications]

---

*Created by /sdd - USB Audio Accessory Mode adapter (passive, no DAC)*
