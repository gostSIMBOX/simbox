# Specifications: PJSIP Mode Inversion (Right Channel)

> **Version**: 1.0
> **Status**: DRAFT
> **Last Updated**: 2026-03-06
> **Requirements**: [01-requirements.md](01-requirements.md)

---

## Overview

This document specifies the implementation of a custom PJSIP media port (`InversionPort`) that inverts the right audio channel for differential signaling. This is a **reusable component** that can be used by any audio path requiring differential signaling (TRRS hardware adapters, USB audio adapters, etc.).

### Original Design Insight (from user)

> "Нам от SIP поступает сигнал на проигрывание в телефонную линию. Если он моно, то мы проигрываем его в левый канал обычно, а в правый инвертировано. Если он стерео то проигрываем левый канал как есть, а правый инвертируем. Это даст то, что по факту в телефонную линию уйдет сложенный сигнал (казалось бы что сложенный сигнал L минус R должна уйти в линию пустота, но за счет того что в телефонах добавлено эхоподавление - из пустоты вычитается эхоподавление и по факту происходит именно проигрывание в телефонную линию). Ноухау с инвертированием правого канала нужен для того чтобы одновременно обратно в линию не уходил сигнал полученный с самой линии и не создавалось эхо."

**Key Technical Insight**: Differential signaling (L - R) + phone echo cancellation = clean audio playback without echo.

---

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  PJSIP Media Endpoint (RX Path)                              │
│                                                               │
│  ┌─────────────────┐     ┌──────────────────────────────┐   │
│  │  Upstream Port  │────►│  InversionPort                │   │
│  │  (SIP Stream /  │     │                               │   │
│  │   Audio Device) │     │  ┌─────────────────────────┐  │   │
│  │  Mono or Stereo │     │  │  Right Channel Inverter │  │   │
│  └─────────────────┘     │  │  (any sample rate)      │  │   │
│                          │  └─────────────────────────┘  │   │
│                          │  Stereo Output (L + -R)       │   │
│                          └───────────────────────────────┘   │
│                                               │               │
└───────────────────────────────────────────────┼───────────────┘
                                                │
                                                ▼
                                    (To downstream: hardware adapter, etc.)
```

### Audio Transformation

```
┌─────────────────────────────────────────────────────────────┐
│  Inversion Logic                                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Mono Input: [L]                                            │
│          │                                                   │
│          ▼                                                   │
│  Stereo Expansion + Inversion:                               │
│  [L, -L]  (left=original, right=inverted)                   │
│                                                              │
│                                                              │
│  Stereo Input: [L, R]                                       │
│          │                                                   │
│          ▼                                                   │
│  Right Channel Inversion:                                    │
│  [L, -R]  (left unchanged, right inverted)                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Signal Chain (Complete Path)

```
┌─────────────────────────────────────────────────────────────────┐
│  Complete Signal Path (Software + Hardware)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. SIP Media Stream (RX)                                        │
│     Input: Mono [L] or Stereo [L, R]                            │
│                     │                                            │
│                     ▼                                            │
│  2. InversionPort (SOFTWARE INVERSION)                           │
│     Mono:   [L] → [L, -L]    (stereo expansion + invert R)      │
│     Stereo: [L, R] → [L, -R] (invert right channel)             │
│                     │                                            │
│                     ▼                                            │
│  3. Android Audio Device (VOICE_CALL source)                     │
│     Output: [L, -R] to hardware jack/USB                        │
│                     │                                            │
│                     ▼                                            │
│  4. TRRS/USB Adapter (HARDWARE INVERSION)                        │
│     Analog circuit (4R+1C) inverts right channel AGAIN:         │
│     [L, -R] → [L, -(-R)] = [L, R]  (double inversion)           │
│                     │                                            │
│                     ▼                                            │
│  5. Phone Input (TRRS jack)                                      │
│     Sees differential signal: L - R                             │
│     (because phone expects tip-ring differential)               │
│                     │                                            │
│                     ▼                                            │
│  6. Phone Echo Canceller                                         │
│     Expects: L - R (differential)                               │
│     Subtracts echo from same differential path                  │
│     Result: Clean audio without echo feedback                   │
│                     │                                            │
│                     ▼                                            │
│  7. Phone Line / GSM Radio                                       │
│     Clean audio injected into phone line                        │
│     No echo feedback to SIP stream                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Interfaces

### Custom Media Port Interface

```cpp
/**
 * Inversion Port
 * 
 * Inverts right audio channel for differential signaling.
 * Reusable component for any audio path requiring L + -R output.
 */
class InversionPort : public pjmedia_port {
public:
    // Constructor
    InversionPort(pjmedia_port *upstream_port);
    
    // Static callback functions (PJSIP C interface)
    static pj_status_t GetFrame(pjmedia_port *port, pjmedia_frame *frame);
    static pj_status_t PutFrame(pjmedia_port *port, pjmedia_frame *frame);
    static pj_status_t OnDestroy(pjmedia_port *port);

private:
    pjmedia_port *upstream_port;   // Upstream audio source
    pj_pool_t *pool;               // Memory pool from media endpoint (shared)
    
    // Pre-allocated buffer for mono→stereo conversion
    pj_int16_t conversion_buffer[MAX_SAMPLES_PER_FRAME * 2];
    
    // Helper functions
    void convertMonoToStereo(pj_int16_t *input, pj_int16_t *output, pj_size_t sample_count);
    void invertRightChannel(pj_int16_t *samples, pj_size_t stereo_sample_count);
};
```

### Factory Function

```cpp
/**
 * Create Inversion Port
 * 
 * @param med_endpt     PJSIP media endpoint
 * @param upstream_port Upstream audio port (SIP stream or audio device)
 * @param p_port        Output: created inversion port
 * @return              PJ_SUCCESS on success
 */
pj_status_t create_inversion_port(
    pjmedia_endpt *med_endpt,
    pjmedia_port *upstream_port,
    pjmedia_port **p_port
);
```

---

## Data Models

### Audio Frame Format

**Input Format** (from upstream):
```
Format: PJMEDIA_TYPE_AUDIO
Channels: 1 (Mono) or 2 (Stereo)
Sample Rate: Any (8kHz, 16kHz, 48kHz, etc.)
Bit Depth: 16-bit PCM (typical)
Samples per Frame: Variable
```

**Output Format** (to downstream):
```
Format: PJMEDIA_TYPE_AUDIO
Channels: 2 (Stereo) - always
Sample Rate: Same as input
Bit Depth: Same as input
Samples per Frame: 
  - If mono input: 2 * input_samples (stereo expansion)
  - If stereo input: same as input (in-place processing)
```

### Frame Structure

```cpp
// Input mono frame
struct MonoFrame {
    pj_int16_t samples[N];  // N mono samples
};

// Output stereo frame (from mono)
struct StereoFrame {
    struct {
        pj_int16_t left;    // Original sample
        pj_int16_t right;   // Inverted sample (-left)
    } pairs[N];             // N stereo pairs
};

// Input stereo frame
struct StereoInputFrame {
    struct {
        pj_int16_t left;
        pj_int16_t right;
    } pairs[N];             // N stereo pairs
};

// Output stereo frame (from stereo)
struct StereoOutputFrame {
    struct {
        pj_int16_t left;     // Unchanged
        pj_int16_t right;    // Inverted (-right)
    } pairs[N];              // N stereo pairs
};
```

---

## Behavior Specifications

### Happy Path

1. **Initialization**
   - `create_inversion_port()` called with media endpoint and upstream port
   - Memory pool obtained from media endpoint (shared pool)
   - `InversionPort` instance allocated
   - Pre-allocated `conversion_buffer` initialized
   - Port interface functions set (get_frame, put_frame, destroy)
   - Port registered with media endpoint

2. **Frame Processing - Mono Input (GetFrame)**
   - Upstream port returns mono audio frame
   - Input buffer: `int16_t[N]` (N mono samples)
   - Use pre-allocated `conversion_buffer` for output
   - For each sample `i` from 0 to N-1:
     - `conversion_buffer[i*2] = input[i]` (Left channel = original)
     - `conversion_buffer[i*2+1] = -input[i]` (Right channel = inverted)
   - Frame buffer pointer updated to `conversion_buffer`
   - Frame size updated to `N*2*sizeof(int16_t)`
   - Return `PJ_SUCCESS`

3. **Frame Processing - Stereo Input (GetFrame)**
   - Upstream port returns stereo audio frame
   - Input buffer: `int16_t[N*2]` (N stereo pairs)
   - Process in-place (no buffer needed)
   - For each stereo pair `i` from 0 to N-1:
     - `samples[i*2]` unchanged (Left channel)
     - `samples[i*2+1] = -samples[i*2+1]` (Right channel = inverted)
   - Frame size unchanged
   - Return `PJ_SUCCESS`

4. **Frame Playback (PutFrame)**
   - No-op (playback-only port)
   - Return `PJ_SUCCESS`

5. **Destruction**
   - `OnDestroy()` called
   - Resources cleaned up (pool released by endpoint)

### Edge Cases

| Case | Trigger | Expected Behavior |
|------|---------|-------------------|
| Empty frame | Upstream returns empty buffer | Pass through unchanged, return success |
| Non-audio frame | Frame type != `PJMEDIA_FRAME_TYPE_AUDIO` | Pass through unchanged, return success |
| Upstream error | Upstream `GetFrame()` returns error | Propagate error code to caller |
| Null pointers | port or frame is NULL | Return `PJ_EINVAL` error |
| Unsupported format | Non-PCM format | Log warning, pass through unchanged |

### Error Handling

| Error | Cause | Response |
|-------|-------|----------|
| `PJ_EINVAL` | Invalid parameters (NULL) | Return error code immediately |
| Upstream error | Upstream port failed | Propagate error code |
| Frame type mismatch | Non-audio frame | Pass through without transformation |

---

## Implementation Location

### New Files

```
nmpjsip-builder/src/patch_2.9/src/pjsip2/pjmedia/src/pjmedia-audiodev/inversion_port.c
nmpjsip-builder/src/patch_2.9/src/pjsip2/pjmedia/include/pjmedia-audiodev/inversion_port.h
```

### Modified Files

```
nmpjsip-builder/src/patch_2.9/src/pjsip2/pjmedia/src/pjmedia-audiodev/android_jni_dev.c
  - Include inversion_port.h
  - Create InversionPort when inversion mode enabled
  - Connect port in RX audio path
```

---

## Testing Strategy

### Unit Tests

```cpp
// Test mono-to-stereo conversion
TEST(InversionPort, MonoToStereoConversion) {
    // Input: [1, 2, 3, 4]
    // Expected output: [1, -1, 2, -2, 3, -3, 4, -4]
}

// Test stereo inversion
TEST(InversionPort, StereoInversion) {
    // Input: [1, 10, 2, 20, 3, 30]
    // Expected output: [1, -10, 2, -20, 3, -30]
}

// Test any sample rate
TEST(InversionPort, AnySampleRate) {
    // Test with 8kHz, 16kHz, 48kHz - all should work
}
```

### Integration Tests

```cpp
// Test with PJSIP media endpoint
TEST(InversionPortIntegration, MediaEndpointIntegration) {
    // Create port, connect to media endpoint, verify audio flows
}

// Test with hardware adapter
TEST(InversionPortIntegration, HardwareAdapterEchoPrevention) {
    // Verify differential signaling prevents echo feedback
}
```

---

## Memory Management

### Pool Strategy: Shared Pool from Media Endpoint

```cpp
// Use shared pool from media endpoint (recommended)
pj_pool_t *pool = pjmedia_endpt_create_pool(med_endpt, "inversion_port", ...);

// Benefits:
// - Efficient memory management
// - No per-frame allocations
// - Pool released automatically on endpoint destruction
```

### Pre-allocated Buffer

```cpp
class InversionPort {
    // Pre-allocated conversion buffer (no runtime allocation)
    pj_int16_t conversion_buffer[MAX_SAMPLES_PER_FRAME * 2];
};
```

---

## Configuration

### Compile-Time Options

```cpp
// Max samples per frame (supports any sample rate up to 48kHz @ 20ms)
#define MAX_SAMPLES_PER_FRAME 1920  // 48kHz * 0.02s * 2 channels
```

---

## Consumers

This inversion port is used by:

| Consumer | Description | File |
|----------|-------------|------|
| **sdd-voiceline-hardwarejack-mode** | TRRS hardware adapter integration | Uses InversionPort for differential signaling |
| **sdd-pjsip-mode-voiceline** | Direct voice line calling | Uses InversionPort for echo prevention |

---

## Approval

- [ ] Reviewed by: [name]
- [ ] Approved on: [date]
- [ ] Notes: [any conditions or clarifications]

---

*Created by /sdd - Split from sdd-voiceline-hardwarejack-mode to separate inversion logic*
