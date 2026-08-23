# Specifications: Voice Line Adapter USB with DAC (USB Audio Class)

> **Version**: 1.0
> **Status**: DRAFT
> **Last Updated**: 2026-03-07
> **Requirements**: [01-requirements.md](01-requirements.md)

---

## Overview

This document specifies the implementation of a **USB Type-C Audio Class (UAC) adapter** with external DAC for direct phone line connection. This is an **active adapter** that provides consistent, high-quality digital-to-analog conversion.

**Key Characteristics**:
- Active adapter with external DAC chip
- Uses USB Audio Class (UAC) specification
- Requires InversionPort for right channel inversion
- 4R+1C differential circuit for phone line interface
- Works with any USB Type-C device (no Audio Accessory Mode required)

---

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  USB Audio Class (UAC) Adapter Architecture                  │
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
│           │ [L, -R] digital stream                           │
│           ▼                                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Android USB Audio Device (Digital)                  │   │
│  │  - USB Audio Class 1.0/2.0                           │   │
│  │  - Digital audio via D+/D- pins                      │   │
│  └────────┬─────────────────────────────────────────────┘   │
│           │                                                  │
│           │ USB Digital Audio                                │
│           ▼                                                  │
│  ╔══════════════════════════════════════════════════════╗   │
│  ║  USB Type-C Adapter (ACTIVE with DAC)                 ║   │
│  ║  ┌────────────────────────────────────────────────┐  ║   │
│  ║  │  USB Audio Class Device Controller             │  ║   │
│  ║  │  - USB 2.0 interface                           │  ║   │
│  ║  │  - UAC descriptor                              │  ║   │
│  ║  └────────────────────────────────────────────────┘  ║   │
│  ║  ┌────────────────────────────────────────────────┐  ║   │
│  ║  │  External DAC Chip                             │  ║   │
│  ║  │  - e.g., PCM2704, PCM2902, XMOS                │  ║   │
│  ║  │  - Digital → Analog [L, -R]                    │  ║   │
│  ║  └────────────────────────────────────────────────┘  ║   │
│  ║  ┌────────────────────────────────────────────────┐  ║   │
│  ║  │  4R+1C Differential Circuit                    │  ║   │
│  ║  │  - Analog summing network                      │  ║   │
│  ║  └────────────────────────────────────────────────┘  ║   │
│  ║  ┌────────────────────────────────────────────────┐  ║   │
│  ║  │  RJ11 Jack (Phone Line)                        │  ║   │
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

### USB Type-C Pinout (UAC Digital Audio)

```
┌─────────────────────────────────────────────────────────────┐
│  USB Type-C Receptacle - USB Audio Class Pinout              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  A1  GND          ┌──┐          B1  GND                     │
│  A2  TX1+         │  │          B2  TX1-                     │
│  A3  TX1-         │  │          B3  TX1+                     │
│  A4  VBUS         │  │          B4  VBUS                     │
│  A5  CC1    ──────┤◦ ◦│───────── B5  CC2          (Config)   │
│  A6  D+     ──────┤  │───────── B6  D-           (USB 2.0)   │
│  A7  D-     ──────┤  │───────── B7  D+           (USB 2.0)   │
│  A8  SBU1         │  │          B8  SBU2                     │
│  A9  VBUS         │  │          B9  VBUS                     │
│  A10 RX1-         │  │          B10 RX1+                    │
│  A11 RX1+         │  │          B11 RX1-                    │
│  A12 GND          └──┘          B12 GND                     │
│                                                              │
│  USB Audio Class Mode:                                       │
│  - D+/D-: USB 2.0 data (digital audio)                       │
│  - VBUS: Power for DAC circuit (500mA max bus power)         │
│  - GND: Ground reference                                     │
│  - CC1/CC2: USB Type-C configuration                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### UAC DAC Block Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  UAC DAC Internal Architecture                               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  USB Type-C                                                  │
│     │                                                        │
│     │ D+/D- (Digital Audio)                                  │
│     ▼                                                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  USB Audio Class Controller                          │   │
│  │  - USB endpoint handling                             │   │
│  │  - Audio stream decoding                             │   │
│  │  - Sample rate conversion (if needed)                │   │
│  └─────────────────────┬────────────────────────────────┘   │
│                        │ I2S / PCM                           │
│                        ▼                                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  DAC Chip (e.g., PCM2704)                            │   │
│  │  - Digital-to-Analog Conversion                      │   │
│  │  - Low-pass filter                                   │   │
│  │  - Output: [L, -R] analog                            │   │
│  └─────────────────────┬────────────────────────────────┘   │
│                        │ Analog [L, -R]                      │
│                        ▼                                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  4R+1C Differential Circuit                          │   │
│  │  - Creates differential for phone line               │   │
│  └─────────────────────┬────────────────────────────────┘   │
│                        │                                     │
│                        ▼                                     │
│                   RJ11 Jack                                  │
│                   (Phone Line)                               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 4R+1C Differential Circuit

```
┌─────────────────────────────────────────────────────────────┐
│  4R+1C Differential Circuit Schematic                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  DAC Left (L) ────R1────┬────────R3──── TIP (+)              │
│                         │                                    │
│                        C1                                    │
│                         │                                    │
│  DAC Right (-R) ───R2────┴────────R4──── RING (-)            │
│                                                              │
│  Component Values (typical):                                 │
│  - R1, R2: 10kΩ (input impedance)                            │
│  - R3, R4: 10kΩ (output impedance)                           │
│  - C1: 100nF (DC blocking / AC coupling)                     │
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
nmpjsip-builder/src/patch_2.9/src/pjsip2/pjmedia/src/pjmedia-audiodev/voiceline_mode_usb_uac.c
nmpjsip-builder/src/patch_2.9/src/pjsip2/pjmedia/include/pjmedia-audiodev/voiceline_mode_usb_uac.h
```

### Modified Files

```
nmpjsip-builder/src/patch_2.9/src/pjsip2/pjmedia/src/pjmedia-audiodev/android_jni_dev.c
  - Include USB UAC mode header
  - Create InversionPort (required)
  - Route audio to USB Audio Class device
  - Configure for digital audio output
```

### Hardware Files (Adapter Design)

```
hardware/voiceline-adapter-usb-with-dac/
  - schematic.pdf (UAC DAC + 4R+1C circuit)
  - bom.csv (Bill of Materials)
  - gerbers/ (PCB fabrication files)
  - assembly.md (Assembly instructions)
  - firmware/ (USB descriptor, if custom)
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
   
3. Android Audio Device (USB Digital Output)
   Routes [L, -R] as USB Audio Class stream
   
4. USB Type-C Connector (Digital)
   D+/D-: USB 2.0 differential pair
   VBUS: Power for adapter (500mA max)
   
5. UAC DAC Chip
   Receives digital audio via USB
   Converts to analog [L, -R]
   
6. 4R+1C Differential Circuit
   Analog summing: L - (-R) = L + R (differential)
   
7. RJ11 Connector
   TIP: Differential +
   RING: Differential -
   
8. Phone Line
   Receives differential audio signal
```

---

## Configuration

### Compile-Time Options

```cpp
// Enable USB Audio Class mode
#define PJMEDIA_VOICELINE_USB_UAC_ENABLED 1

// Require InversionPort
#define VOICELINE_USB_UAC_REQUIRE_INVERSION 1

// DAC chip selection
#define VOICELINE_USB_UAC_DAC_CHIP PCM2704  // or PCM2902, XMOS, etc.
```

### Runtime Configuration

```cpp
typedef struct voiceline_usb_uac_config {
    pj_bool_t enabled;              // Enable USB UAC mode
    pj_bool_t use_inversion;        // Use InversionPort (required)
    pjmedia_format_id format;       // Audio format (48kHz/16-bit typical)
    int output_volume;              // Output volume (0-100)
    int dac_sample_rate;            // DAC sample rate (8k/16k/48k)
} voiceline_usb_uac_config_t;
```

---

## Hardware Specifications

### Recommended DAC Chips

| Chip | Resolution | SNR | Interface | Notes |
|------|------------|-----|-----------|-------|
| PCM2704 | 16-bit | 98dB | USB 1.1 | Low cost, widely available |
| PCM2902 | 16-bit | 100dB | USB 1.1 | Integrated headphone amp |
| XMOS XU208 | 24-bit | 120dB | USB 2.0 | High-end, programmable |

### Bill of Materials (BOM) - PCM2704 Example

| Component | Part Number | Quantity | Package | Notes |
|-----------|-------------|----------|---------|-------|
| U1 | PCM2704 | 1 | SSOP-28 | DAC chip |
| R1, R2 | 10kΩ | 2 | 0603 | Input resistors |
| R3, R4 | 10kΩ | 2 | 0603 | Output resistors |
| C1 | 100nF | 1 | 0603 | DC blocking |
| C2-C5 | Various | 4 | 0603 | DAC decoupling |
| X1 | 12MHz | 1 | - | Crystal (if needed) |
| J1 | USB Type-C | 1 | - | Receptacle |
| J2 | RJ11 | 1 | - | Phone line jack |
| PCB | - | 1 | - | 2-layer board |

### Power Considerations

- **Bus Powered**: Draws power from USB VBUS (500mA max)
- **Typical Consumption**: ~50-100mA for DAC chip
- **Self-Powered Option**: External 5V supply for higher power DACs

### Enclosure

- 3D printed or small plastic enclosure
- USB Type-C plug exposed
- RJ11 jack accessible
- LED indicator (optional, for activity)
- Compact size (~40mm x 25mm x 12mm)

---

## Testing Strategy

### Unit Tests

```cpp
// Test USB UAC mode initialization
TEST(USBUAC, Initialization) {
    // Verify InversionPort is created
    // Verify USB audio device is detected
    // Verify audio routing to USB digital output
}

// Test inversion is applied
TEST(USBUAC, InversionApplied) {
    // Verify [L, R] → [L, -R] transformation
}
```

### Integration Tests

```cpp
// Test with phone line
TEST(USBUACIntegration, PhoneLineCall) {
    // Setup: Connect USB UAC adapter to phone line
    // Make SIP call
    // Verify audio quality on phone line
    // Verify differential signaling
    // Measure THD+N and SNR
}
```

### Manual Verification

1. Build GOSTsimbox with USB UAC mode
2. Build/connect USB Type-C adapter (UAC DAC + 4R+1C circuit)
3. Plug adapter into device USB Type-C port
4. Verify device recognizes USB audio device
5. Connect RJ11 to phone line / GSM gateway
6. Make SIP call
7. Verify audio quality on phone line
8. Measure audio quality (THD+N, SNR)
9. Test with mono and stereo sources

---

## Dependencies

### Requires

- **sdd-pjsip-mode-inversion** - InversionPort (required)
- **sdd-voiceline-mode-direct** - Voice line mode foundation
- **USB Type-C port** - With USB Audio Class support
- **Android USB audio API** - For digital audio output
- **UAC DAC chip** - PCM2704, PCM2902, or equivalent

### Device Compatibility

| Device | USB Audio Class | Notes |
|--------|----------------|-------|
| Google Pixel | ✓ | Confirmed |
| Samsung Galaxy | ✓ | Confirmed |
| Huawei | ✓ | Most models |
| Xiaomi | ✓ | Most models |
| Generic Android | ✓ | Android 5.0+ |

---

## Comparison: With-DAC vs Without-DAC

| Feature | With DAC (UAC) | Without DAC (Accessory) |
|---------|----------------|------------------------|
| Cost | Higher (~$5-10) | Lower (~$1-2) |
| Audio Quality | Consistent, high | Depends on device DAC |
| Compatibility | Universal | Audio Accessory Mode required |
| Complexity | Active circuit | Passive circuit |
| Power | Bus/self-powered | No power needed |
| Size | Larger | Smaller |

---

## Open Design Questions

- [ ] **DAC Selection**: PCM2704 vs PCM2902 vs XMOS for cost/performance?
- [ ] **Power**: Bus-powered sufficient or need self-powered option?
- [ ] **UAC Version**: UAC 1.0 (wider compatibility) vs UAC 2.0?
- [ ] **Resistor Values**: Optimal values for different phone line impedances?
- [ ] **LED Indicator**: Activity LED useful or unnecessary?

---

## Approval

- [ ] Reviewed by: [name]
- [ ] Approved on: [date]
- [ ] Notes: [any conditions or clarifications]

---

*Created by /sdd - USB Audio Class adapter with external DAC*
