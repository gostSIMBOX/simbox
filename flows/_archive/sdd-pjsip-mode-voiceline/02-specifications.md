# Specifications: PJSIP Mode Voice Line (Direct Call)

> **Version**: 1.0
> **Status**: DRAFT
> **Last Updated**: 2026-03-06
> **Requirements**: [01-requirements.md](01-requirements.md)

---

## Overview

This document specifies the implementation of a PJSIP mode for direct voice line calling. This mode integrates SIP media streaming with GSM radio calls via hardware adapters, using differential signaling for echo-free audio.

**Key Dependency**: This mode uses `InversionPort` from `sdd-pjsip-mode-inversion` for right channel inversion.

---

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│  Voice Line Mode Architecture                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐                                           │
│  │  SIP Call (RX)   │                                           │
│  └────────┬─────────┘                                           │
│           │                                                      │
│           ▼                                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  InversionPort (from sdd-pjsip-mode-inversion)            │   │
│  │  - Mono → Stereo: [L] → [L, -L]                          │   │
│  │  - Stereo → Stereo: [L, R] → [L, -R]                     │   │
│  └────────┬─────────────────────────────────────────────────┘   │
│           │                                                      │
│           ▼                                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Android Audio Device (VOICE_CALL source)                 │   │
│  └────────┬─────────────────────────────────────────────────┘   │
│           │                                                      │
│           ▼                                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Hardware Adapter (TRRS/USB)                              │   │
│  │  - Inverts right channel (4R+1C analog circuit)          │   │
│  │  - Creates differential signal: L - R                    │   │
│  └────────┬─────────────────────────────────────────────────┘   │
│           │                                                      │
│           ▼                                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Phone / GSM Radio                                        │   │
│  │  - Sees differential: L - R                              │   │
│  │  - Echo canceller removes echo                           │   │
│  │  - Clean audio in phone line                             │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Call Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  SIP Caller  │     │   Gateway    │     │  GSM Radio   │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       │  INVITE            │                    │
       ├───────────────────>│                    │
       │                    │                    │
       │  200 OK            │                    │
       │<───────────────────┤                    │
       │                    │                    │
       │  ACK               │                    │
       ├───────────────────>│                    │
       │                    │                    │
       │  Media (RX)        │                    │
       ├───────────────────>│                    │
       │  [L, R]            │                    │
       │                    │                    │
       │                    │ InversionPort      │
       │                    │ [L, R] → [L, -R]   │
       │                    │                    │
       │                    │ Hardware Adapter   │
       │                    │ [L, -R] → [L, R]   │
       │                    │                    │
       │                    │ Differential       │
       │                    │ Phone sees: L - R  │
       │                    │                    │
       │                    │ To GSM Radio       │
       │                    ├───────────────────>│
       │                    │                    │
       │                    │                    │ GSM Call
       │                    │                    │ Established
       │                    │                    │
       │  Bidirectional     │                    │ Bidirectional
       │  Media             │                    │ Audio
       │<═══════════════════┼════════════════════>│
       │                    │                    │
```

---

## Integration with InversionPort

### Usage

```cpp
// Create inversion port for voice line mode
pjmedia_port *inversion_port;
pj_status_t status = create_inversion_port(
    med_endpt,
    upstream_port,  // SIP media stream
    &inversion_port
);

if (status != PJ_SUCCESS) {
    // Handle error
}

// Connect inversion port to audio device
pjmedia_port *audio_device_port;
// ... initialize audio device ...

// Connect: SIP Stream → InversionPort → Audio Device
pjmedia_port_connect(inversion_port, audio_device_port);
```

### Signal Processing

```
SIP Media (RX)
   │
   │ Format: Mono [L] or Stereo [L, R]
   │ Sample Rate: Any (8kHz, 16kHz, 48kHz)
   ▼
InversionPort
   │
   │ Processing:
   │ - Mono: [L] → [L, -L] (stereo expansion + inversion)
   │ - Stereo: [L, R] → [L, -R] (right channel inversion)
   │
   ▼
Android Audio Device
   │
   │ Output: [L, -R] to hardware jack/USB
   │
   ▼
Hardware Adapter (TRRS/USB)
   │
   │ Analog circuit (4R+1C) inverts R again
   │ [L, -R] → [L, -(-R)] = [L, R]
   │
   ▼
Phone / GSM Radio
   │
   │ Sees differential: L - R
   │ Echo canceller removes echo
   │
   ▼
Clean Audio in Phone Line
```

---

## Implementation Location

### New Files

```
nmpjsip-builder/src/patch_2.9/src/pjsip2/pjmedia/src/pjmedia-audiodev/voiceline_mode.c
nmpjsip-builder/src/patch_2.9/src/pjsip2/pjmedia/include/pjmedia-audiodev/voiceline_mode.h
```

### Modified Files

```
nmpjsip-builder/src/patch_2.9/src/pjsip2/pjmedia/src/pjmedia-audiodev/android_jni_dev.c
  - Include voiceline_mode.h
  - Initialize voice line mode when enabled
  - Create InversionPort for RX path

nmpjsip-builder/src/patch_2.9/src/pjsip2/pjsip/src/pjsua-lib/pjsua_call.c
  - Add voice line mode flag to call settings
  - Initialize voice line media path on call setup
```

### Dependencies

```
nmpjsip-builder/src/patch_2.9/src/pjsip2/pjmedia/src/pjmedia-audiodev/inversion_port.c
  - Required: InversionPort from sdd-pjsip-mode-inversion
```

---

## Configuration

### Compile-Time Options

```cpp
// Enable voice line mode
#define PJMEDIA_VOICELINE_MODE_ENABLED 1

// Default inversion port settings
#define VOICELINE_MODE_USE_INVERSION 1
#define VOICELINE_MODE_ANY_SAMPLE_RATE 1
```

### Runtime Configuration

```cpp
typedef struct voiceline_mode_config {
    pj_bool_t enabled;            // Enable voice line mode
    pj_bool_t use_inversion;      // Use InversionPort (recommended: true)
    pjmedia_format_id format;     // Audio format (auto-detect)
} voiceline_mode_config_t;
```

---

## Testing Strategy

### Unit Tests

```cpp
// Test voice line mode initialization
TEST(VoiceLineMode, Initialization) {
    // Verify InversionPort is created
    // Verify audio path is connected
}

// Test call establishment
TEST(VoiceLineMode, CallEstablishment) {
    // Verify SIP call connects to GSM radio
}
```

### Integration Tests

```cpp
// Test end-to-end call
TEST(VoiceLineModeIntegration, EndToEndCall) {
    // Make SIP call
    // Verify audio flows to GSM radio
    // Verify no echo feedback
}

// Test with hardware adapter
TEST(VoiceLineModeIntegration, HardwareAdapterIntegration) {
    // Connect TRRS/USB adapter
    // Verify differential signaling works
    // Verify echo cancellation
}
```

### Manual Verification

1. Build GOSTsimbox with voice line mode
2. Connect hardware adapter (TRRS or USB)
3. Make SIP call to gateway
4. Verify call is routed to GSM radio
5. Verify audio quality on both ends
6. Verify no echo or feedback

---

## Dependencies

### Requires

- **sdd-pjsip-mode-inversion** - InversionPort for right channel inversion
- **sdd-voiceline-hardwarejack-mode** - Hardware adapter integration
- **PJSIP 2.9+** - Media endpoint and call API
- **Android JNI Audio Device** - Audio path to hardware

### Blocks

- **GSM-SIP Bridging** - Requires this to be complete first
- **Voice Line Testing** - Cannot test without this

---

## Open Design Questions

- [ ] **Call Initiation**: Intent vs TelephonyManager API?
- [ ] **Call State Sync**: How to handle state mismatches?
- [ ] **Error Recovery**: What if GSM call drops?
- [ ] **Multi-Call**: Support multiple simultaneous calls?

---

## Approval

- [ ] Reviewed by: [name]
- [ ] Approved on: [date]
- [ ] Notes: [any conditions or clarifications]

---

*Created by /sdd - Direct voice line calling mode using InversionPort*
