# Requirements: Voice Line Mode Magisk

> **Version**: 1.3
> **Status**: DRAFT
> **Last Updated**: 2026-03-06
> **Module**: voiceline-mode-magisk
> **Dependencies**: `sdd-pjsip-mode-inversion` (right channel inversion)

---

## Problem Statement

**What problem are we solving?**

The GOSTsimbox Android Gateway needs to support physical hardware adapter connectivity for voice line integration with GSM radio equipment via **Magisk system module**. Hardware adapters use differential signaling (stereo with inverted channel) to transmit mono audio over a TRRS jack or USB connection.

**Why does this matter?**

This enables the gateway to:
- Connect to external GSM radio hardware via physical jack (TRRS) or USB
- Support hardware adapters that require differential audio signaling
- Bridge SIP media streams to physical telephony hardware
- Enable bidirectional voice communication between SIP and GSM radio
- **Prevent echo** by using differential signaling with phone's echo cancellation
- **System-level integration** via Magisk module for privileged audio access

### Original Problem Description (from user)

> "Нам от SIP поступает сигнал на проигрывание в телефонную линию. Если он моно, то мы проигрываем его в левый канал обычно, а в правый инвертировано. Если он стерео то проигрываем левый канал как есть, а правый инвертируем. Это даст то, что по факту в телефонную линию уйдет сложенный сигнал (казалось бы что сложенный сигнал L минус R должна уйти в линию пустота, но за счет того что в телефонах добавлено эхоподавление - из пустоты вычитается эхоподавление и по факту происходит именно проигрывание в телефонную линию). Ноухау с инвертированием правого канала нужен для того чтобы одновременно обратно в линию не уходил сигнал полученный с самой линии и не создавалось эхо."

**Key Insight**: The differential signaling (L - R) combined with phone's echo cancellation results in clean audio playback into the phone line without echo feedback.

---

## Dependencies

This module **depends on** the following SDD flows:

| SDD Flow | Purpose | Status |
|----------|---------|--------|
| **`sdd-pjsip-mode-inversion`** | Right channel inversion for differential signaling | In development |

**Note**: The inversion logic has been **extracted** to a separate SDD flow (`sdd-pjsip-mode-inversion`) for reusability. This flow uses the `InversionPort` component from that flow.

### Magisk Module Dependency

This flow also requires:
- **`sdd-magisk-voice-recording`** - Magisk module for privileged permissions (CAPTURE_AUDIO_OUTPUT)

### Hardware Adapter Implementation Detail

**Important**: The TRRS/USB hardware adapter performs right channel inversion **at the hardware level** using a passive analog circuit:

```
TRRS/USB Hardware Adapter Circuit:
┌─────────────────────────────────────────────────────────┐
│  Hardware Implementation (Analog Circuit)                │
│                                                          │
│  Input (from device):  Left ─────────┬─────> Tip (TRRS) │
│                                      │                  │
│  Input (from device):  Right ────[R1]┴─[R2]─┬─[C1]─> Ring (TRRS)
│                                      │      │           │
│  Component Values (typical):         │     [R3]        [R4]
│  - R1, R2, R3, R4: 4 resistors       │      │          │
│  - C1: 1 capacitor                   │     GND        GND
│                                      │                  │
│  Function:                           │                  │
│  - Inverts right channel polarity    │                  │
│  - Creates differential signal       │                  │
│  - Passively sums L + (-R)           │                  │
└─────────────────────────────────────────────────────────┘
```

**Why This Matters**:
- Software inversion (HardwareAdapterPort) + Hardware inversion (adapter circuit) = Double inversion
- **Result**: Right channel is inverted twice, returning to original polarity
- **But**: Phone still sees differential signal (L - R) for echo cancellation
- **Benefit**: Hardware adapter expects inverted input, we provide it digitally

**Signal Chain**:
```
SIP Audio → HardwareAdapterPort (software: L, -R) 
              ↓
          Android Audio Device
              ↓
          TRRS/USB Adapter (hardware: inverts R again)
              ↓
          Phone sees: L - R (differential)
              ↓
          Echo canceller works correctly
              ↓
          Clean audio in phone line (no echo)
```

---

## User Stories

### Primary

**As a** GSM-SIP Gateway System
**I want** to convert mono/stereo SIP audio to stereo with inverted right channel
**So that** I can connect to hardware adapters using differential signaling via TRRS jack or USB, while preventing echo

### Secondary

**As a** System Integrator
**I want** the audio transformation to happen in real-time with minimal latency
**So that** voice quality is preserved during calls

**As a** Developer
**I want** a reusable PJSIP media port component
**So that** I can integrate hardware adapter mode into any PJSIP-based application

**As a** User
**I want** the system to work with both TRRS and USB hardware adapters
**So that** I can use different hardware configurations

---

## Acceptance Criteria

### Must Have

1. **Given** a mono audio frame from upstream PJSIP port
   **When** HardwareAdapterPort processes the frame
   **Then** output is stereo with left=original, right=inverted

2. **Given** a stereo audio frame from upstream PJSIP port
   **When** HardwareAdapterPort processes the frame
   **Then** left channel unchanged, right channel inverted

3. **Given** the HardwareAdapterPort is created
   **When** connected to PJSIP media endpoint
   **Then** it integrates seamlessly with existing SIP media stream

4. **Given** audio transformation is active
   **When** processing real-time voice frames
   **Then** latency added is < 10ms per frame

5. **Given** a call is established
   **When** audio flows through HardwareAdapterPort to hardware adapter
   **Then** both parties can hear each other clearly without echo

6. **Given** hardware adapter connected via TRRS or USB
   **When** audio is played through hardware adapter
   **Then** differential signaling prevents echo feedback

### Should Have

1. Memory: pre-allocated buffers (no runtime allocations in GetFrame)
2. Error handling for frame processing failures
3. Logging for debugging audio path issues
4. Compatible with PJSIP 2.9+
5. Support any sample rate (8kHz, 16kHz, 48kHz, etc.)

### Won't Have (This Iteration)

- Audio effects processing (EQ, compression, etc.)
- Dynamic format conversion (fixed format assumed)
- Bidirectional conversion (stereo→mono not needed)
- Hardware detection/auto-switching
- TX path processing (only RX: SIP → phone line)

---

## Constraints

### Technical

- **Must** use PJSIP pjmedia_port interface
- **Must** be compatible with existing PJSIP media endpoint
- **Must** work with Android JNI audio device (android_jni_dev.c)
- **Must** integrate with nmpjsip-builder patch structure
- **Must** support both TRRS and USB hardware adapters

### Performance

- **Must** process frames in real-time (< 10ms latency)
- **Must** use pre-allocated buffers (no malloc during GetFrame processing)
- **Should** support any sample rate without configuration
- **Should** handle both mono and stereo input formats

### Platform

- **Target**: Android with PJSIP 2.9+
- **Integration**: nmpjsip-builder/src/patch_2.9/
- **Deployment**: Part of GOSTsimbox Android Gateway
- **Hardware**: TRRS jack adapters and USB audio adapters

### Dependencies

- Requires PJSIP media endpoint initialization
- Requires upstream audio port (SIP stream or Android audio device)
- Requires integration with existing audio path
- Requires hardware adapter (TRRS or USB) for physical connection

---

## Open Questions

- [x] **Audio Format**: What sample rates must be supported? → **Any rate, no restrictions**
- [ ] **Buffer Management**: Pre-allocated buffer size for max frame size?
- [ ] **Error Propagation**: How should frame processing errors be handled? (silence, passthrough, error code?)
- [ ] **Testing**: How to test audio transformation without physical hardware?
- [x] **Integration Point**: Where exactly in the audio path should this be inserted? → **RX path: SIP stream → HardwareAdapterPort → Android audio device → TRRS/USB → phone line**

---

## References

### Code Provided

- `HardwareAdapterPort` class implementation (C++ with PJSIP) - reference implementation
- `create_hardware_adapter_mode()` factory function
- Integration example with PJSIP media endpoint

### Related Documentation

- `flows/sdd-magisk-voice-recording/` - Magisk module for voice recording
- `flows/sdd-patch-management/` - PJSIP patch management
- `nmpjsip-builder/src/patch_2.9/src/pjsip2/pjmedia/src/pjmedia-audiodev/android_jni_dev.c` - Android audio device

### PJSIP References

- pjmedia_port API: https://pjogndoc.appspot.com/html/structpjmedia__port.html
- pjmedia_frame structure: https://pjogndoc.appspot.com/html/structpjmedia__frame.html
- Audio format handling: https://github.com/pjsip/pjmedia/tree/master/pjmedia

### Hardware Adapter References

- TRRS differential signaling
- USB Audio Class adapters
- Echo cancellation in telephony

---

## Approval

- [ ] Reviewed by: [name]
- [ ] Approved on: [date]
- [ ] Notes: [any conditions or clarifications]

---

*Created by /sdd - Requirements elicitation in progress*
*Updated with user clarifications on differential signaling and echo prevention*
