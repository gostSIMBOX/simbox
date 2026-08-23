# PJSIP Voice Line Modes - Architecture Overview

> **Version**: 1.0
> **Created**: 2026-03-06
> **Status**: DRAFT

---

## Overview

This document provides an architectural overview of all PJSIP Voice Line modes available in the GOSTsimbox Android Gateway. Each mode provides a different approach to bridging SIP calls to GSM radio networks.

---

## Mode Comparison

| Mode | Root Required | Audio Quality | Complexity | Use Case |
|------|---------------|---------------|------------|----------|
| **Magisk** | ✅ Yes (Magisk v20.0+) | ⭐⭐⭐⭐⭐ Highest | High | Production deployment with root |
| **Direct** | ❌ No | ⭐⭐ Lower | Medium | Fallback, non-root devices |
| **Earphone-to-Mic** | ❌ No | ⭐⭐ Lower | Low | Quick deployment, any device |

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│  PJSIP Voice Line Modes Architecture                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│                          SIP Call (RX)                           │
│                               │                                  │
│                               ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  sdd-pjsip-mode-inversion (BASE COMPONENT)               │    │
│  │  ┌──────────────────────────────────────────────────┐   │    │
│  │  │  InversionPort                                    │   │    │
│  │  │  - Mono: [L] → [L, -L]                           │   │    │
│  │  │  - Stereo: [L, R] → [L, -R]                      │   │    │
│  │  │  - Any sample rate                               │   │    │
│  │  └──────────────────────────────────────────────────┘   │    │
│  └──────────────────┬──────────────────────────────────────┘    │
│                     │                                             │
│         ┌───────────┼───────────┬──────────────────────┐        │
│         │           │           │                       │        │
│         ▼           ▼           ▼                       │        │
│  ┌─────────────┐ ┌─────────────┐ ┌──────────────────┐  │        │
│  │   MAGISK    │ │   DIRECT    │ │ EARPHONE-TO-MIC  │  │        │
│  │   MODE      │ │   MODE      │ │ MODE             │  │        │
│  │             │ │             │ │                  │  │        │
│  │ System-level│ │ Acoustic    │ │ Physical         │  │        │
│  │ injection   │ │ coupling    │ │ acoustic         │  │        │
│  │             │ │ (air path)  │ │ coupling         │  │        │
│  │ [L, -R]     │ │ [L, -R]     │ │ [L, -R]          │  │        │
│  └──────┬──────┘ └──────┬──────┘ └────────┬─────────┘  │        │
│         │               │                  │            │        │
│         ▼               ▼                  ▼            │        │
│  ┌─────────────┐ ┌─────────────┐ ┌──────────────────┐  │        │
│  │ Android     │ │ Android     │ │ Android          │  │        │
│  │ Audio       │ │ Audio       │ │ Audio            │  │        │
│  │ (VOICE_CALL)│ │ (Speaker)   │ │ (Earphone)       │  │        │
│  └──────┬──────┘ └──────┬──────┘ └────────┬─────────┘  │        │
│         │               │                  │            │        │
│         ▼               ▼                  ▼            │        │
│  ┌─────────────┐ ┌─────────────┐ ┌──────────────────┐  │        │
│  │ Hardware    │ │ Air Path    │ │ Physical         │  │        │
│  │ Adapter     │ │ (Speaker →  │ │ Contact          │  │        │
│  │ (TRRS/USB)  │ │  Mic)       │ │ (Earphone → Mic) │  │        │
│  │ 4R+1C       │ │             │ │                  │  │        │
│  └──────┬──────┘ └──────┬──────┘ └────────┬─────────┘  │        │
│         │               │                  │            │        │
│         ▼               ▼                  ▼            │        │
│  ┌──────────────────────────────────────────────────┐  │        │
│  │  Phone / GSM Radio                                │  │        │
│  │  - Differential input (L - R)                    │  │        │
│  │  - Echo cancellation                              │  │        │
│  │  - Clean audio (Magisk mode)                      │  │        │
│  │  - Some quality loss (Direct/Earphone modes)     │  │        │
│  └──────────────────────────────────────────────────┘  │        │
│                                                          │        │
└──────────────────────────────────────────────────────────┘        │
```

---

## Mode Details

### 1. Magisk Mode (`sdd-voiceline-mode-magisk`)

**Best For**: Production deployment with rooted devices

**Requirements**:
- Magisk v20.0+ installed
- `sdd-magisk-voice-recording` module
- `sdd-pjsip-mode-inversion` component
- TRRS/USB hardware adapter

**Audio Path**:
```
SIP → InversionPort → Android Audio (VOICE_CALL) → 
Hardware Adapter → Phone Line
```

**Pros**:
- ✅ Highest audio quality
- ✅ Direct electronic injection
- ✅ Perfect echo cancellation
- ✅ System-level integration

**Cons**:
- ❌ Requires root/Magisk
- ❌ More complex deployment
- ❌ May void device warranty

---

### 2. Direct Mode (`sdd-voiceline-mode-direct`)

**Best For**: Non-root devices, fallback mode

**Requirements**:
- Android TelephonyManager access
- Standard Android permissions
- Optional: `sdd-pjsip-mode-inversion`

**Audio Path**:
```
SIP → (Optional InversionPort) → Android Audio (Speaker) → 
Air → Microphone → GSM
```

**Pros**:
- ✅ No root required
- ✅ Works on standard devices
- ✅ Simpler deployment

**Cons**:
- ❌ Lower audio quality (acoustic coupling)
- ❌ Echo cancellation less effective
- ❌ Ambient noise pickup

---

### 3. Earphone-to-Microphone Mode (`sdd-voiceline-mode-earphone-to-mic`)

**Best For**: Quick deployment, any Android device

**Requirements**:
- `sdd-pjsip-mode-inversion` (required)
- Earphone/speaker output
- Microphone input
- Physical mounting (tape, holder)

**Audio Path**:
```
SIP → InversionPort → Earphone → 
Physical Contact → Microphone → GSM
```

**Pros**:
- ✅ No root required
- ✅ Works on any device
- ✅ InversionPort for compatibility
- ✅ Simple physical setup

**Cons**:
- ❌ Lower audio quality
- ❌ Requires physical mounting
- ❌ Acoustic coupling losses

---

## Component Dependencies

```
┌────────────────────────────────────────────────────────────┐
│  Dependency Graph                                           │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  sdd-pjsip-mode-inversion (BASE)                           │
│  │                                                          │
│  ├─────────────────┬─────────────────┬──────────────────┐  │
│  │                 │                 │                  │  │
│  ▼                 ▼                 ▼                  │  │
│  Magisk Mode       Direct Mode       Earphone-to-Mic    │  │
│  (uses)            (optional)        (requires)         │  │
│  │                 │                 │                  │  │
│  ▼                 │                 │                  │  │
│  sdd-magisk-voice- │                 │                  │  │
│  recording         │                 │                  │  │
│  (requires)        │                 │                  │  │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

---

## Selection Guide

### Choose Magisk Mode When:
- ✅ Devices are rooted with Magisk
- ✅ Highest audio quality required
- ✅ Production deployment
- ✅ Hardware adapters available

### Choose Direct Mode When:
- ✅ Non-root devices only
- ✅ Can tolerate lower quality
- ✅ Need quick deployment
- ✅ No hardware modifications possible

### Choose Earphone-to-Mic Mode When:
- ✅ Universal device compatibility needed
- ✅ Physical setup acceptable
- ✅ InversionPort compatibility required
- ✅ Simple deployment priority

---

## Implementation Status

| Mode | Requirements | Specifications | Implementation | Status |
|------|--------------|----------------|----------------|--------|
| **Magisk** | ✅ Complete | ✅ Complete | ⏹ Not started | DRAFT |
| **Direct** | ✅ Complete | ✅ Complete | ⏹ Not started | DRAFT |
| **Earphone-to-Mic** | ✅ Complete | ✅ Complete | ⏹ Not started | DRAFT |
| **Inversion (Base)** | ✅ Complete | ✅ Complete | ⏹ Not started | DRAFT |

---

## Next Steps

1. **Review all mode specifications**
2. **Approve requirements** for each mode
3. **Approve specifications** for each mode
4. **Start with InversionPort** (base component)
5. **Implement Magisk mode** (highest quality)
6. **Implement Direct mode** (fallback)
7. **Implement Earphone-to-Mic mode** (universal)

---

## Related Documentation

- `flows/sdd-pjsip-mode-inversion/` - Base inversion component
- `flows/sdd-voiceline-mode-magisk/` - Magisk-based mode
- `flows/sdd-voiceline-mode-direct/` - Direct mode (no root)
- `flows/sdd-voiceline-mode-earphone-to-mic/` - Acoustic coupling mode
- `flows/sdd-magisk-voice-recording/` - Magisk module for permissions

---

*Created by /sdd - PJSIP Voice Line Modes Architecture Overview*
