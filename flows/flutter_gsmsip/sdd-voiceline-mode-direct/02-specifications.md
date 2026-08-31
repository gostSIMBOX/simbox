# Specifications: Voice Line Mode Direct

> **Version**: 1.0
> **Status**: DRAFT
> **Last Updated**: 2026-03-06
> **Requirements**: [01-requirements.md](01-requirements.md)

---

## Overview

This document specifies the implementation of **direct voice line calling** without Magisk root. This mode uses Android's standard telephony API and acoustic coupling (earphone → microphone) for audio transfer to GSM radio.

**Key Difference from Magisk Mode**:
- **Magisk Mode**: Direct audio injection via CAPTURE_AUDIO_OUTPUT permission
- **Direct Mode**: Acoustic coupling via earphone → microphone (no root required)

---

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  Direct Voice Line Mode Architecture                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐                                       │
│  │  SIP Call (RX)   │                                       │
│  └────────┬─────────┘                                       │
│           │                                                  │
│           ▼                                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Optional: InversionPort (from sdd-pjsip-mode-...)   │   │
│  │  - Improves compatibility with some devices          │   │
│  │  - Can be skipped for simple passthrough             │   │
│  └────────┬─────────────────────────────────────────────┘   │
│           │                                                  │
│           ▼                                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Android Audio Device (Speaker/Earphone output)      │   │
│  └────────┬─────────────────────────────────────────────┘   │
│           │                                                  │
│           │ Audio plays through speaker/earphone             │
│           ▼                                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Acoustic Coupling (Air Path)                         │   │
│  │  - Sound travels through air                          │   │
│  │  - Some quality loss, potential echo                  │   │
│  └────────┬─────────────────────────────────────────────┘   │
│           │                                                  │
│           ▼                                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Device Microphone                                    │   │
│  │  - Captures speaker/earphone audio                    │   │
│  └────────┬─────────────────────────────────────────────┘   │
│           │                                                  │
│           ▼                                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Android Telephony (GSM Call)                         │   │
│  │  - Sends microphone audio to GSM radio                │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
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
       │                    │ Android Telecom    │
       │                    │ Make GSM Call      │
       │                    ├───────────────────>│
       │                    │                    │
       │                    │ Audio to Speaker   │
       │                    │ (earphone/earpiece)│
       │                    │                    │
       │                    │ Acoustic Coupling  │
       │                    │ Speaker → Air → Mic│
       │                    │                    │
       │                    │ Mic to GSM         │
       │                    ├───────────────────>│
       │                    │                    │
       │  Bidirectional     │                    │ Bidirectional
       │  Media             │                    │ Audio
       │<═══════════════════┼════════════════════>│
       │                    │                    │
```

---

## Implementation Location

### New Files

```
nmpjsip-builder/src/patch_2.9/src/pjsip2/pjmedia/src/pjmedia-audiodev/voiceline_mode_direct.c
nmpjsip-builder/src/patch_2.9/src/pjsip2/pjmedia/include/pjmedia-audiodev/voiceline_mode_direct.h
```

### Modified Files

```
android/app/src/main/kotlin/.../MainActivity.kt
  - Add TelephonyManager integration
  - Initiate GSM calls from Flutter

nmpjsip-builder/src/patch_2.9/src/pjsip2/pjmedia/src/pjmedia-audiodev/android_jni_dev.c
  - Add direct mode audio routing
  - Optional InversionPort integration
```

---

## Audio Routing

### Without InversionPort (Simple Passthrough)

```
SIP Media → Android Audio → Speaker → Air → Microphone → GSM
```

### With InversionPort (Better Compatibility)

```
SIP Media → InversionPort → Android Audio → Speaker → Air → Microphone → GSM
[L, R] → [L, -R] → Hardware inverts again → [L, R] → Better differential
```

**Note**: InversionPort may improve compatibility with devices that have hardware differential input.

---

## Configuration

### Compile-Time Options

```cpp
// Enable direct voice line mode
#define PJMEDIA_VOICELINE_DIRECT_ENABLED 1

// Optional: Use InversionPort
#define VOICELINE_DIRECT_USE_INVERSION 0  // 0 = disabled, 1 = enabled
```

### Runtime Configuration

```cpp
typedef struct voiceline_direct_config {
    pj_bool_t enabled;              // Enable direct mode
    pj_bool_t use_inversion;        // Use InversionPort (optional)
    pjmedia_format_id format;       // Audio format
    int speaker_volume;             // Speaker volume for acoustic coupling
} voiceline_direct_config_t;
```

---

## Dependencies

### Requires

- **Android TelephonyManager** - For GSM call initiation
- **PJSIP 2.9+** - Media endpoint
- **Android Audio Device** - Speaker/earphone output

### Optional

- **sdd-pjsip-mode-inversion** - For better hardware compatibility

---

## Testing Strategy

### Unit Tests

```cpp
// Test direct mode initialization
TEST(VoiceLineDirect, Initialization) {
    // Verify audio routing is configured
}

// Test call initiation
TEST(VoiceLineDirect, CallInitiation) {
    // Verify GSM call is initiated via TelephonyManager
}
```

### Integration Tests

```cpp
// Test end-to-end call
TEST(VoiceLineDirectIntegration, EndToEndCall) {
    // Make SIP call
    // Verify GSM call is initiated
    // Verify audio flows through acoustic coupling
}
```

### Manual Verification

1. Build GOSTsimbox with direct mode
2. Insert SIM card with calling credit
3. Make SIP call to gateway
4. Verify GSM call is initiated
5. Verify audio quality (expect some loss from acoustic coupling)
6. Test with earphone and speakerphone modes

---

## Open Design Questions

- [ ] **Call Initiation**: Intent vs TelephonyManager API?
- [ ] **Audio Routing**: Earphone vs speakerphone vs earpiece?
- [ ] **Echo Cancellation**: How aggressive should AEC be?
- [ ] **Volume Control**: Automatic gain control needed?

---

## Approval

- [ ] Reviewed by: [name]
- [ ] Approved on: [date]
- [ ] Notes: [any conditions or clarifications]

---

*Created by /sdd - Direct voice line calling without Magisk*
