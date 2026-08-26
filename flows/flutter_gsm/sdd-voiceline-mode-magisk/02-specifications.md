# Specifications: Voice Line Hardware Jack Mode

> **Version**: 1.2
> **Status**: DRAFT
> **Last Updated**: 2026-03-06
> **Requirements**: [01-requirements.md](01-requirements.md)
> **Dependencies**: `sdd-pjsip-mode-inversion` (InversionPort component)

---

## Overview

This document specifies the implementation of hardware adapter connectivity for voice line integration using TRRS jack or USB connections. This flow **uses** the `InversionPort` component from `sdd-pjsip-mode-inversion` for right channel inversion.

### Relationship with sdd-pjsip-mode-inversion

**This flow consumes** the `InversionPort` component:

```
sdd-voiceline-hardwarejack-mode (this flow)
    │
    │ uses
    ▼
sdd-pjsip-mode-inversion
    │
    │ provides
    ▼
InversionPort (reusable component)
```

**Separation of Concerns**:
- `sdd-pjsip-mode-inversion`: Right channel inversion logic (reusable)
- `sdd-voiceline-hardwarejack-mode`: Hardware adapter integration (uses inversion)
- `sdd-pjsip-mode-voiceline`: Direct voice line calling (uses inversion)

### Original Design Insight (from user)

> "Нам от SIP поступает сигнал на проигрывание в телефонную линию. Если он моно, то мы проигрываем его в левый канал обычно, а в правый инвертировано. Если он стерео то проигрываем левый канал как есть, а правый инвертируем. Это даст то, что по факту в телефонную линию уйдет сложенный сигнал (казалось бы что сложенный сигнал L минус R должна уйти в линию пустота, но за счет того что в телефонах добавлено эхоподавление - из пустоты вычитается эхоподавление и по факту происходит именно проигрывание в телефонную линию). Ноухау с инвертированием правого канала нужен для того чтобы одновременно обратно в линию не уходил сигнал полученный с самой линии и не создавалось эхо."

**Key Technical Insight**: Differential signaling (L - R) + phone echo cancellation = clean audio playback without echo.

### Hardware Adapter Circuit Implementation

**Critical Detail**: The TRRS/USB hardware adapter performs right channel inversion **at the hardware level** using a passive analog circuit with **4 resistors and 1 capacitor**:

```
┌─────────────────────────────────────────────────────────────────┐
│  TRRS/USB Hardware Adapter - Analog Circuit                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Input from Device (3.5mm TRS or USB Audio DAC)                │
│   ┌──────────────────────────────────────────────────────┐     │
│   │                                                       │     │
│   │  Left Channel  ───────────┬───────────────> Tip      │     │
│   │                           │                (TRRS)     │     │
│   │                           │                          │     │
│   │  Right Channel ──[R1]──┬──┴──[R2]──┬──[C1]──> Ring   │     │
│   │                        │           │       (TRRS)     │     │
│   │                        │          [R3]               │     │
│   │                        │           │                 │     │
│   │                        │          GND               │     │
│   │                        │                             │     │
│   │  Component Values (typical):                         │     │
│   │  - R1: 10kΩ (input resistor)                         │     │
│   │  - R2: 10kΩ (inversion resistor)                     │     │
│   │  - R3: 10kΩ (ground reference)                       │     │
│   │  - R4: 10kΩ (load resistor, if needed)               │     │
│   │  - C1: 100nF (DC blocking capacitor)                 │     │
│   │                                                       │     │
│   │  Function:                                            │     │
│   │  1. R1-R2 form inverting summing amplifier           │     │
│   │  2. C1 blocks DC offset                              │     │
│   │  3. R3 provides ground reference                     │     │
│   │  4. Output: Right channel inverted (-R)              │     │
│   └──────────────────────────────────────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Software + Hardware Inversion Chain

```
┌─────────────────────────────────────────────────────────────────┐
│  Complete Signal Path (Software + Hardware)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. SIP Media Stream (RX)                                        │
│     Input: Mono [L] or Stereo [L, R]                            │
│                     │                                            │
│                     ▼                                            │
│  2. HardwareAdapterPort (SOFTWARE INVERSION)                     │
│     Mono:   [L] → [L, -L]    (stereo expansion + invert R)      │
│     Stereo: [L, R] → [L, -R] (invert right channel)             │
│                     │                                            │
│                     ▼                                            │
│  3. Android Audio Device (VOICE_CALL source)                     │
│     Output: [L, -R] to hardware jack/USB                        │
│                     │                                            │
│                     ▼                                            │
│  4. TRRS/USB Adapter (HARDWARE INVERSION)                        │
│     Analog circuit inverts right channel AGAIN:                 │
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

### Why Double Inversion Works

| Stage | Signal | Explanation |
|-------|--------|-------------|
| **Software** | `[L, -R]` | HardwareAdapterPort inverts right channel digitally |
| **Hardware** | `[L, R]` | Adapter circuit inverts right channel again (analog) |
| **Phone Input** | `L - R` | Phone sees differential (tip - ring) |
| **Echo Canceller** | `(L - R) - echo` | Phone removes echo from differential path |
| **Result** | **Clean audio** | No echo feedback to SIP |

**Key Insight**: The hardware adapter **expects** an inverted right channel input. By providing `[L, -R]` from software, the hardware inversion creates the correct differential signal `[L, R]` that the phone interprets as `L - R` for echo cancellation.

---

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  PJSIP Media Endpoint (RX Path)                              │
│                                                               │
│  ┌─────────────────┐     ┌──────────────────────────────┐   │
│  │  SIP Media      │────►│  InversionPort                │   │
│  │  Stream (RX)    │     │  (from sdd-pjsip-mode-       │   │
│  │  Mono or Stereo │     │   inversion)                 │   │
│  └─────────────────┘     │                               │   │
│                          │  ┌─────────────────────────┐  │   │
│                          │  │  Right Channel Inverter │  │   │
│                          │  │  (any sample rate)      │  │   │
│                          │  └─────────────────────────┘  │   │
│                          │  Stereo Output (L + -R)       │   │
│                          └───────────────────────────────┘   │
│                                               │               │
└───────────────────────────────────────────────┼───────────────┘
                                                │
                                                ▼
                                    ┌───────────────────────┐
                                    │  Android Audio Device │
                                    │  (VOICE_CALL source)  │
                                    └───────────┬───────────┘
                                                │
                                                ▼
                        ┌───────────────────────────────────┐
                        │  Hardware Adapter                  │
                        │  ┌─────────────────────────────┐  │
                        │  │  TRRS Jack (3.5mm)          │  │
                        │  │  Tip:   Left  (+)           │  │
                        │  │  Ring:  Right (-) inverted  │  │
                        │  │  Sleeve: Ground             │  │
                        │  └─────────────────────────────┘  │
                        │  ┌─────────────────────────────┐  │
                        │  │  USB Audio Adapter          │  │
                        │  │  Same differential signaling│  │
                        │  └─────────────────────────────┘  │
                        └───────────────────────────────────┘
                                                │
                                                ▼
                                    ┌───────────────────────┐
                                    │  Phone Line / GSM     │
                                    │  Differential Input   │
                                    │  + Echo Cancellation  │
                                    └───────────────────────┘
```

**Note**: `InversionPort` is provided by `sdd-pjsip-mode-inversion` flow - this flow uses it rather than implementing inversion logic.

### Differential Signaling Explained

```
┌─────────────────────────────────────────────────────────────┐
│  The Echo Prevention Mechanism                               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  HardwareAdapterPort Output: [L, -R] (inverted right)       │
│                                                              │
│  Hardware Adapter (TRRS/USB):                                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Tip:   Left  = L                                     │   │
│  │  Ring:  Right = -R (inverted)                         │   │
│  │  Differential: L - (-R) = L + R                       │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  Phone receives differential signal:                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Phone sees: L - R (differential expectation)         │   │
│  │  Echo canceller subtracts echo from same path         │   │
│  │  Result: Clean audio without echo feedback            │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  Key: Inverted right channel matches phone's expectation     │
│       Echo canceller works correctly, no feedback loop       │
└─────────────────────────────────────────────────────────────┘
```

### Audio Flow (RX Path: SIP → Phone Line)

```
1. SIP Call Receives Media
         │
         ▼
2. PJSIP Media Stream (RX direction)
         │
         ├─────────────────────────────────┐
         │                                 │
         ▼ (mono)                          ▼ (stereo)
3. HardwareAdapterPort::GetFrame()         │
         │                                 │
         │  ┌──────────────────────────┐   │
         │  │  Mono Input: [L]         │   │
         │  │  Stereo Output: [L, -L]  │   │
         │  └──────────────────────────┘   │
         │                                 │
         │                                 │  ┌──────────────────────────┐
         │                                 ├─►│  Stereo Input: [L, R]    │
         │                                 │  │  Stereo Output: [L, -R]  │
         │                                 │  └──────────────────────────┘
         │                                 │
         └──────────────┬──────────────────┘
                        │
                        ▼
4. Stereo Frame Output (L + -R)
         │
         ▼
5. Android Audio Device (VOICE_CALL source)
         │
         ▼
6. Hardware Adapter (TRRS or USB)
         │
         │  Differential Signal
         │  + Echo Cancellation in Phone
         │  = Clean Audio in Phone Line
         │
         ▼
7. Phone Line / GSM Radio (clean audio, no echo)
```

---

## Interfaces

### Custom Media Port Interface

```cpp
/**
 * Hardware Adapter Port
 * 
 * Converts mono/stereo audio to stereo with inverted right channel
 * for differential signaling via TRRS/USB hardware adapters.
 * Prevents echo by matching phone's differential input expectation.
 */
class HardwareAdapterPort : public pjmedia_port {
public:
    // Constructor
    HardwareAdapterPort(pjmedia_port *upstream_port);
    
    // Static callback functions (PJSIP C interface)
    static pj_status_t GetFrame(pjmedia_port *port, pjmedia_frame *frame);
    static pj_status_t PutFrame(pjmedia_port *port, pjmedia_frame *frame);
    static pj_status_t OnDestroy(pjmedia_port *port);

private:
    pjmedia_port *upstream_port;   // Upstream audio source
    pj_pool_t *pool;               // Memory pool from media endpoint (shared)
    
    // Pre-allocated buffer for mono→stereo conversion
    // Size: max_samples_per_frame * 2 (stereo expansion)
    pj_int16_t conversion_buffer[MAX_SAMPLES_PER_FRAME * 2];
    
    // Helper functions
    void convertMonoToStereo(pj_int16_t *input, pj_int16_t *output, pj_size_t sample_count);
    void invertRightChannel(pj_int16_t *samples, pj_size_t stereo_sample_count);
};
```

### Factory Function

```cpp
/**
 * Create Hardware Adapter mode port
 * 
 * @param med_endpt     PJSIP media endpoint
 * @param upstream_port Upstream audio port (SIP stream or audio device)
 * @param p_port        Output: created hardware adapter port
 * @return              PJ_SUCCESS on success
 */
pj_status_t create_hardware_adapter_mode(
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
Sample Rate: Any (8kHz, 16kHz, 48kHz, etc. - no restrictions)
Bit Depth: 16-bit PCM (typical)
Samples per Frame: Variable (typically 10ms worth of samples)
```

**Output Format** (to hardware):
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
   - `create_hardware_adapter_mode()` called with media endpoint and upstream port
   - Memory pool obtained from media endpoint (shared pool)
   - `HardwareAdapterPort` instance allocated
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

## Dependencies

### Requires

- **PJSIP 2.9+** - Media endpoint and port API
- **Android JNI Audio Device** - Upstream/downstream audio path
- **nmpjsip-builder** - Build system integration

### Blocks

- **Hardware Jack Integration** - Requires this to be complete first
- **Voice Line Testing** - Cannot test hardware without this

---

## Integration Points

### External Systems

- **Hardware Adapter (TRRS)** - Physical 3.5mm jack with differential input
- **Hardware Adapter (USB)** - USB Audio Class adapter with differential output
- **GSM Radio** - External hardware connected via adapter

### Internal Systems

| Component | Integration Point | File |
|-----------|------------------|------|
| PJSIP Media Endpoint | Port registration | `pjmedia_endpt_create_port()` |
| Android Audio Device | Upstream port | `android_jni_dev.c` |
| SIP Call Stream | RX media stream | `pjsua_call_media_start()` |
| Build System | Patch integration | `nmpjsip-builder/src/patch_2.9/` |

---

## Implementation Location

### New Files

```
nmpjsip-builder/src/patch_2.9/src/pjsip2/pjmedia/src/pjmedia-audiodev/hardware_adapter_port.c
nmpjsip-builder/src/patch_2.9/src/pjsip2/pjmedia/include/pjmedia-audiodev/hardware_adapter_port.h
```

### Modified Files

```
nmpjsip-builder/src/patch_2.9/src/pjsip2/pjmedia/src/pjmedia-audiodev/android_jni_dev.c
  - Include hardware_adapter_port.h
  - Create HardwareAdapterPort when hardware mode enabled
  - Connect port in RX audio path
```

---

## Testing Strategy

### Unit Tests

```cpp
// Test mono-to-stereo conversion
TEST(HardwareAdapterPort, MonoToStereoConversion) {
    // Input: [1, 2, 3, 4]
    // Expected output: [1, -1, 2, -2, 3, -3, 4, -4]
}

// Test stereo inversion
TEST(HardwareAdapterPort, StereoInversion) {
    // Input: [1, 10, 2, 20, 3, 30]
    // Expected output: [1, -10, 2, -20, 3, -30]
}

// Test error handling
TEST(HardwareAdapterPort, NullParameterHandling) {
    // Verify PJ_EINVAL returned for NULL parameters
}

// Test any sample rate
TEST(HardwareAdapterPort, AnySampleRate) {
    // Test with 8kHz, 16kHz, 48kHz - all should work
}
```

### Integration Tests

```cpp
// Test with PJSIP media endpoint
TEST(HardwareAdapterPortIntegration, MediaEndpointIntegration) {
    // Create port, connect to media endpoint, verify audio flows
}

// Test with Android audio device
TEST(HardwareAdapterPortIntegration, AndroidAudioDevice) {
    // Integrate with android_jni_dev, verify end-to-end audio
}

// Test echo prevention
TEST(HardwareAdapterPortIntegration, EchoPrevention) {
    // Verify differential signaling prevents echo feedback
}
```

### Manual Verification

1. Build GOSTsimbox with hardware adapter mode
2. Connect TRRS or USB hardware adapter to device
3. Make SIP call
4. Verify audio quality on both ends
5. Verify no echo or feedback
6. Test with both mono and stereo SIP streams

---

## Build Integration

### CMakeLists.txt Addition

```cmake
# Add hardware adapter port to PJSIP build
pjmedia_audiodev_src(hardware_adapter_port.c)
```

### Header Include Path

```cmake
include_directories(
    ${PJMEDIA_INCLUDE_DIR}
    ${PJMEDIA_AUDIODEV_INCLUDE_DIR}
)
```

---

## Configuration

### Compile-Time Options

```cpp
// Enable/disable hardware adapter mode
#define PJMEDIA_HARDWARE_ADAPTER_ENABLED 1

// Max samples per frame (supports any sample rate up to 48kHz @ 20ms)
#define MAX_SAMPLES_PER_FRAME 1920  // 48kHz * 0.02s * 2 channels
```

### Runtime Configuration

```cpp
typedef struct hardware_adapter_config {
    pj_bool_t enabled;        // Enable hardware adapter mode
    pjmedia_format_id format; // Audio format (auto-detect from upstream)
} hardware_adapter_config_t;
```

---

## Memory Management

### Pool Strategy: Shared Pool from Media Endpoint

```cpp
// Use shared pool from media endpoint (recommended)
pj_pool_t *pool = pjmedia_endpt_create_pool(med_endpt, "hardware_adapter", ...);

// Benefits:
// - Efficient memory management
// - No per-frame allocations
// - Pool released automatically on endpoint destruction
```

### Pre-allocated Buffer

```cpp
class HardwareAdapterPort {
    // Pre-allocated conversion buffer (no runtime allocation)
    pj_int16_t conversion_buffer[MAX_SAMPLES_PER_FRAME * 2];
};
```

---

## Open Design Questions

- [x] **Sample Rate Support**: Any rate supported ✓ Resolved
- [ ] **Buffer Size**: What is MAX_SAMPLES_PER_FRAME? (suggest 1920 for 48kHz @ 20ms)
- [ ] **Error Propagation**: Silence, passthrough, or error code? (suggest passthrough)
- [ ] **Logging Level**: DEBUG or INFO? (suggest DEBUG for frame processing)

---

## Approval

- [ ] Reviewed by: [name]
- [ ] Approved on: [date]
- [ ] Notes: [any conditions or clarifications]

---

*Created by /sdd - Specifications based on provided reference code*
*Updated with user clarifications on differential signaling, echo prevention, and TRRS/USB support*
