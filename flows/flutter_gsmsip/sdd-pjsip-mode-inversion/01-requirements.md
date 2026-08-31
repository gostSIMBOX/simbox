# Requirements: PJSIP Mode Inversion (Right Channel)

> **Version**: 1.0
> **Status**: DRAFT
> **Last Updated**: 2026-03-06
> **Module**: pjsip-mode-inversion

---

## Problem Statement

**What problem are we solving?**

The GOSTsimbox Android Gateway needs to invert the right audio channel for differential signaling when playing audio into a phone line via hardware adapters. This prevents echo feedback by matching the phone's differential input expectation.

**Why does this matter?**

Without right channel inversion:
- Phone's echo canceller doesn't work correctly
- Echo feedback occurs (audio from line leaks back to SIP)
- Call quality is degraded or unusable

With right channel inversion:
- Phone sees differential signal (L - R)
- Echo canceller subtracts echo from same path
- Clean audio playback into phone line without echo

### Original Problem Description (from user)

> "Нам от SIP поступает сигнал на проигрывание в телефонную линию. Если он моно, то мы проигрываем его в левый канал обычно, а в правый инвертировано. Если он стерео то проигрываем левый канал как есть, а правый инвертируем. Это даст то, что по факту в телефонную линию уйдет сложенный сигнал (казалось бы что сложенный сигнал L минус R должна уйти в линию пустота, но за счет того что в телефонах добавлено эхоподавление - из пустоты вычитается эхоподавление и по факту происходит именно проигрывание в телефонную линию). Ноухау с инвертированием правого канала нужен для того чтобы одновременно обратно в линию не уходил сигнал полученный с самой линии и не создавалось эхо."

---

## User Stories

### Primary

**As a** GSM-SIP Gateway System
**I want** to invert the right audio channel for all audio played to phone line
**So that** the phone's differential input receives the correct signal and echo cancellation works properly

### Secondary

**As a** System Integrator
**I want** the inversion to work with any sample rate
**So that** I don't need to configure or restrict audio formats

**As a** Developer
**I want** a reusable PJSIP media port for channel inversion
**So that** I can integrate it into any PJSIP-based application requiring differential signaling

---

## Acceptance Criteria

### Must Have

1. **Given** a mono audio frame from upstream
   **When** InversionPort processes the frame
   **Then** output is stereo with left=original, right=inverted

2. **Given** a stereo audio frame from upstream
   **When** InversionPort processes the frame
   **Then** left channel unchanged, right channel inverted

3. **Given** any sample rate (8kHz, 16kHz, 48kHz, etc.)
   **When** audio is processed
   **Then** inversion works correctly without configuration

4. **Given** real-time audio processing
   **When** frames are processed
   **Then** latency added is < 10ms per frame

5. **Given** hardware adapter connected (TRRS/USB)
   **When** audio flows through inversion port to hardware
   **Then** phone sees differential signal (L - R) and echo cancellation works

### Should Have

1. Memory: pre-allocated buffers (no runtime allocations in GetFrame)
2. Error handling for frame processing failures
3. Logging for debugging audio path issues
4. Compatible with PJSIP 2.9+

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

### Performance

- **Must** process frames in real-time (< 10ms latency)
- **Must** use pre-allocated buffers (no malloc during GetFrame processing)
- **Should** support any sample rate without configuration

### Platform

- **Target**: Android with PJSIP 2.9+
- **Integration**: nmpjsip-builder/src/patch_2.9/
- **Deployment**: Part of GOSTsimbox Android Gateway

### Dependencies

- Requires PJSIP media endpoint initialization
- Requires upstream audio port (SIP stream or Android audio device)
- Requires hardware adapter (TRRS/USB) for physical connection

---

## Open Questions

- [x] **Audio Format**: What sample rates must be supported? → **Any rate, no restrictions**
- [ ] **Buffer Management**: What is optimal pre-allocated buffer size?
- [ ] **Error Propagation**: How should frame processing errors be handled?
- [ ] **Testing**: How to test inversion without physical hardware?

---

## References

### Related Documentation

- `flows/sdd-voiceline-hardwarejack-mode/` - Hardware jack integration (uses this inversion)
- `flows/sdd-pjsip-mode-voiceline/` - Direct voice line calling
- `flows/sdd-magisk-voice-recording/` - Magisk module for voice recording
- `flows/sdd-patch-management/` - PJSIP patch management

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

*Created by /sdd - Split from sdd-voiceline-hardwarejack-mode to separate inversion logic*
