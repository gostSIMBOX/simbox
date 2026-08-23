# Plan: Voice Line Adapter USB with DAC (USB Audio Class)

> **Version**: 1.0
> **Status**: DRAFT
> **Last Updated**: 2026-03-07
> **Specifications**: [02-specifications.md](02-specifications.md)

---

## Overview

This plan outlines the implementation steps for the USB Audio Class (UAC) adapter with external DAC. This is an **active adapter** providing consistent, high-quality audio conversion.

---

## Tasks

### Phase 1: Software Implementation

#### 1.1 Create InversionPort Integration
- **File**: `nmpjsip-builder/src/patch_2.9/src/pjsip2/pjmedia/src/pjmedia-audiodev/voiceline_mode_usb_uac.c`
- **Description**: Create USB UAC mode driver with InversionPort integration
- **Estimate**: 2 hours
- **Dependencies**: sdd-pjsip-mode-inversion complete

#### 1.2 Create Header File
- **File**: `nmpjsip-builder/src/patch_2.9/src/pjsip2/pjmedia/include/pjmedia-audiodev/voiceline_mode_usb_uac.h`
- **Description**: Header with API definitions
- **Estimate**: 0.5 hours

#### 1.3 Modify Android JNI Device
- **File**: `android_jni_dev.c`
- **Description**: Add USB UAC mode audio routing
- **Estimate**: 1 hour

#### 1.4 Add Configuration Options
- **File**: `voiceline_mode_usb_uac.c`
- **Description**: Runtime configuration struct and defaults
- **Estimate**: 0.5 hours

### Phase 2: Hardware Design

#### 2.1 DAC Chip Selection
- **File**: `hardware/voiceline-adapter-usb-with-dac/dac-selection.md`
- **Description**: Evaluate and select DAC chip (PCM2704 vs PCM2902 vs XMOS)
- **Estimate**: 1 hour

#### 2.2 Circuit Design
- **File**: `hardware/voiceline-adapter-usb-with-dac/schematic.pdf`
- **Description**: Design UAC DAC circuit + 4R+1C differential circuit
- **Estimate**: 2 hours

#### 2.3 PCB Layout
- **File**: `hardware/voiceline-adapter-usb-with-dac/gerbers/`
- **Description**: Design 2-layer PCB layout with DAC
- **Estimate**: 3 hours

#### 2.4 Bill of Materials
- **File**: `hardware/voiceline-adapter-usb-with-dac/bom.csv`
- **Description**: Create BOM with DAC chip and all components
- **Estimate**: 0.5 hours

#### 2.5 Assembly Instructions
- **File**: `hardware/voiceline-adapter-usb-with-dac/assembly.md`
- **Description**: Document assembly steps for active circuit
- **Estimate**: 0.5 hours

#### 2.6 Firmware (if custom UAC)
- **File**: `hardware/voiceline-adapter-usb-with-dac/firmware/`
- **Description**: USB descriptor and firmware (if using programmable DAC)
- **Estimate**: 4 hours (optional, skip if using pre-configured DAC)

### Phase 3: Testing

#### 3.1 Unit Tests
- **Description**: Create C unit tests for USB UAC mode
- **Estimate**: 1 hour

#### 3.2 Integration Tests
- **Description**: Test with actual phone line connection
- **Estimate**: 2 hours

#### 3.3 Hardware Validation
- **Description**: Build prototype and validate audio quality (THD+N, SNR)
- **Estimate**: 6 hours

#### 3.4 Compatibility Testing
- **Description**: Test with multiple Android devices
- **Estimate**: 3 hours

### Phase 4: Documentation

#### 4.1 User Guide
- **Description**: Document how to build and use the UAC adapter
- **Estimate**: 1 hour

#### 4.2 API Documentation
- **Description**: Document software API
- **Estimate**: 0.5 hours

#### 4.3 Hardware Reference
- **Description**: Document hardware specifications and troubleshooting
- **Estimate**: 1 hour

---

## Task Dependencies

```
1.1 InversionPort Integration
         │
         ▼
1.2 Header File
         │
         ▼
1.3 Modify Android JNI ───► 2.1 DAC Selection
         │                          │
         ▼                          ▼
1.4 Configuration           2.2 Circuit Design
         │                          │
         │                          ▼
         │                    2.3 PCB Layout
         │                          │
         │                          ▼
         │                    2.4 BOM + 2.5 Assembly
         │                          │
         │                          ▼
         └─────────────────────► 2.6 Firmware (optional)
                                      │
                                      ▼
                                3.1 Unit Tests
                                      │
                                      ▼
                                3.2 Integration Tests
                                      │
                                      ▼
                                3.3 Hardware Validation
                                      │
                                      ▼
                                3.4 Compatibility Testing
                                      │
                                      ▼
                                4.1-4.3 Documentation
```

---

## File Changes Summary

### New Files

| Path | Purpose |
|------|---------|
| `voiceline_mode_usb_uac.c` | USB UAC mode driver |
| `voiceline_mode_usb_uac.h` | Header file |
| `hardware/.../dac-selection.md` | DAC chip evaluation |
| `hardware/.../schematic.pdf` | Circuit schematic |
| `hardware/.../gerbers/*` | PCB fabrication files |
| `hardware/.../bom.csv` | Bill of materials |
| `hardware/.../assembly.md` | Assembly instructions |
| `hardware/.../firmware/*` | USB firmware (optional) |

### Modified Files

| Path | Changes |
|------|---------|
| `android_jni_dev.c` | Add USB UAC mode routing |

---

## Estimates

| Phase | Hours |
|-------|-------|
| Software | 4 |
| Hardware | 7-11 (depends on firmware) |
| Testing | 12 |
| Documentation | 2.5 |
| **Total** | **25.5-29.5** |

---

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| DAC chip availability | Medium | Select widely available chip |
| USB compatibility issues | High | Test on multiple devices |
| Audio quality below expectations | Medium | Use high-quality DAC |
| Power consumption too high | Low | Optimize circuit design |
| Firmware complexity | Medium | Use pre-configured DAC if possible |

---

## Approval

- [ ] Plan reviewed by: [name]
- [ ] Plan approved on: [date]

---

*Created by /sdd - USB Audio Class adapter with external DAC plan*
