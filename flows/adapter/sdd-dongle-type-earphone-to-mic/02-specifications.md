# Specifications: Voice Line Mode Earphone-to-Microphone

> **Version**: 1.0
> **Status**: DRAFT
> **Last Updated**: 2026-03-06
> **Requirements**: [01-requirements.md](01-requirements.md)

---

## Overview

This document specifies the implementation of **earphone-to-microphone acoustic coupling** mode. This mode uses physical contact between earphone speaker and device microphone for audio transfer, with right channel inversion for differential signaling.

**Key Characteristics**:
- Physical acoustic coupling (no electronic connection)
- Requires `InversionPort` for right channel inversion
- Works on any Android device (no root required)
- Lower audio quality than electronic connection (inherent to acoustic coupling)

---

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  Earphone-to-Microphone Mode Architecture                    │
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
│           │ [L, -R] output                                   │
│           ▼                                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Android Audio Device (Earphone output)              │   │
│  └────────┬─────────────────────────────────────────────┘   │
│           │                                                  │
│           │ Earphone plays audio                             │
│           ▼                                                  │
│  ╔══════════════════════════════════════════════════════╗   │
│  ║  PHYSICAL ACOUSTIC COUPLING                           ║   │
│  ║  ┌──────────────┐         ┌──────────────┐           ║   │
│  ║  │  Earphone    │ ──────► │  Microphone  │           ║   │
│  ║  │  Speaker     │ Contact │              │           ║   │
│  ║  └──────────────┘         └──────────────┘           ║   │
│  ║  (L + -R)              (Captures acoustic)            ║   │
│  ╚══════════════════════════════════════════════════════╝   │
│           │                                                  │
│           ▼                                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Android Telephony (GSM Call)                         │   │
│  │  - Sends microphone audio to GSM radio                │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Physical Setup

```
┌─────────────────────────────────────────────────────────────┐
│  Physical Coupling Setup                                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Device with Gateway App                                     │
│  ┌────────────────────────────────────────────────────┐     │
│  │                                                     │     │
│  │   Earphone Speaker ─────► Microphone               │     │
│  │   (plays SIP audio)      (captures for GSM)        │     │
│  │                                                     │     │
│  │   Positioning:                                      │     │
│  │   - Earphone speaker pressed against microphone    │     │
│  │   - Secure with tape, holder, or custom mount      │     │
│  │   - Ensure good acoustic contact                   │     │
│  │                                                     │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  Audio Path:                                                 │
│  SIP → InversionPort [L, -R] → Earphone                     │
│    → Physical Contact → Microphone → GSM Radio              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Signal Chain with Inversion

```
┌─────────────────────────────────────────────────────────────┐
│  Complete Signal Path                                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. SIP Media Stream (RX)                                    │
│     Input: Mono [L] or Stereo [L, R]                        │
│                     │                                        │
│                     ▼                                        │
│  2. InversionPort (SOFTWARE INVERSION)                       │
│     Mono:   [L] → [L, -L]    (stereo expansion + invert R)  │
│     Stereo: [L, R] → [L, -R] (invert right channel)         │
│                     │                                        │
│                     ▼                                        │
│  3. Android Audio Device (Earphone output)                   │
│     Output: [L, -R] to earphone speaker                     │
│                     │                                        │
│                     ▼                                        │
│  4. Earphone Speaker                                         │
│     Plays: [L, -R] as sound waves                           │
│                     │                                        │
│                     │ Acoustic Coupling                      │
│                     ▼                                        │
│  5. Physical Contact                                         │
│     Sound travels from earphone to microphone               │
│     (some quality loss, potential distortion)               │
│                     │                                        │
│                     ▼                                        │
│  6. Device Microphone                                        │
│     Captures: Acoustic signal [L, -R]                       │
│     Converts back to electrical signal                      │
│                     │                                        │
│                     ▼                                        │
│  7. Hardware Adapter (if connected)                          │
│     Analog circuit (4R+1C) inverts R again:                 │
│     [L, -R] → [L, -(-R)] = [L, R]  (double inversion)       │
│                     │                                        │
│                     ▼                                        │
│  8. Phone Input (if hardware adapter connected)              │
│     Sees differential signal: L - R                         │
│     Echo canceller works correctly                          │
│                     │                                        │
│                     ▼                                        │
│  9. GSM Radio / Phone Line                                   │
│     Clean audio (if differential) or standard audio         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Location

### New Files

```
nmpjsip-builder/src/patch_2.9/src/pjsip2/pjmedia/src/pjmedia-audiodev/voiceline_mode_earphone_mic.c
nmpjsip-builder/src/patch_2.9/src/pjsip2/pjmedia/include/pjmedia-audiodev/voiceline_mode_earphone_mic.h
```

### Modified Files

```
nmpjsip-builder/src/patch_2.9/src/pjsip2/pjmedia/src/pjmedia-audiodev/android_jni_dev.c
  - Include earphone-to-mic mode header
  - Create InversionPort (required)
  - Route audio to earphone output
  - Configure for acoustic coupling optimization
```

### Dependencies

```
nmpjsip-builder/src/patch_2.9/src/pjsip2/pjmedia/src/pjmedia-audiodev/inversion_port.c
  - REQUIRED: InversionPort from sdd-pjsip-mode-inversion
```

---

## Audio Optimization for Acoustic Coupling

### Volume Control

```cpp
// Optimal volume for acoustic coupling
typedef struct earphone_mic_config {
    pj_bool_t enabled;
    int earphone_volume;        // 0-100 (recommend: 80-100 for best coupling)
    pj_bool_t use_agc;          // Automatic gain control
    pj_bool_t use_aec;          // Acoustic echo cancellation
} earphone_mic_config_t;
```

### Recommended Settings

| Setting | Value | Rationale |
|---------|-------|-----------|
| Earphone Volume | 80-100% | Maximize signal-to-noise ratio |
| AGC | Enabled | Compensate for coupling variations |
| AEC | Enabled (light) | Reduce acoustic feedback |
| InversionPort | Required | For differential signaling compatibility |

---

## Configuration

### Compile-Time Options

```cpp
// Enable earphone-to-mic mode
#define PJMEDIA_VOICELINE_EARPHONE_MIC_ENABLED 1

// Require InversionPort
#define VOICELINE_EARPHONE_MIC_REQUIRE_INVERSION 1
```

### Runtime Configuration

```cpp
typedef struct earphone_mic_config {
    pj_bool_t enabled;              // Enable earphone-to-mic mode
    int earphone_volume;            // Volume for acoustic coupling (80-100)
    pj_bool_t use_agc;              // Automatic gain control
    pj_bool_t use_aec;              // Acoustic echo cancellation (light)
} earphone_mic_config_t;
```

---

## Testing Strategy

### Unit Tests

```cpp
// Test earphone-to-mic mode initialization
TEST(EarphoneMic, Initialization) {
    // Verify InversionPort is created
    // Verify audio routing to earphone
}

// Test inversion is applied
TEST(EarphoneMic, InversionApplied) {
    // Verify [L, R] → [L, -R] transformation
}
```

### Integration Tests

```cpp
// Test with physical coupling
TEST(EarphoneMicIntegration, PhysicalCoupling) {
    // Setup: Position earphone against microphone
    // Make SIP call
    // Verify audio is captured by microphone
    // Verify audio quality is acceptable
}
```

### Manual Verification

1. Build GOSTsimbox with earphone-to-mic mode
2. Configure earphone volume to 80-100%
3. Position earphone speaker against device microphone
4. Secure with tape or holder
5. Make SIP call
6. Verify audio quality (expect some loss from acoustic coupling)
7. Test with and without hardware adapter for differential signaling

---

## Dependencies

### Requires

- **sdd-pjsip-mode-inversion** - InversionPort (required for this mode)
- **Android Audio Device** - Earphone output
- **Device Microphone** - For capturing earphone audio

### Used By

| SDD Flow | Purpose |
|----------|---------|
| `sdd-voiceline-mode-magisk` | Can use earphone-to-mic as fallback |
| `sdd-voiceline-mode-direct` | Similar acoustic coupling approach |

---

## Open Design Questions

- [ ] **Volume Level**: Exact optimal volume for different devices?
- [ ] **Physical Mount**: Best way to secure earphone to microphone?
- [ ] **AEC Tuning**: How aggressive should acoustic echo cancellation be?
- [ ] **AGC Tuning**: Target gain level for consistent output?

---

## Approval

- [ ] Reviewed by: [name]
- [ ] Approved on: [date]
- [ ] Notes: [any conditions or clarifications]

---

*Created by /sdd - Earphone-to-microphone acoustic coupling mode with InversionPort*
