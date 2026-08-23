# Plan: Voice Line Adapter USB without DAC (Audio Accessory Mode)

> **Version**: 1.0
> **Status**: DRAFT
> **Last Updated**: 2026-03-07
> **Specifications**: [02-specifications.md](02-specifications.md)

---

## Overview

This plan outlines the implementation steps for the USB Audio Accessory Mode adapter. This is a **passive adapter** using the device's internal DAC.

---

## Tasks

### Phase 1: Software Implementation

#### 1.1 Create InversionPort Integration
- **File**: `nmpjsip-builder/src/patch_2.9/src/pjsip2/pjmedia/src/pjmedia-audiodev/voiceline_mode_usb_accessory.c`
- **Description**: Create USB accessory mode driver with InversionPort integration
- **Estimate**: 2 hours
- **Dependencies**: sdd-pjsip-mode-inversion complete

#### 1.2 Create Header File
- **File**: `nmpjsip-builder/src/patch_2.9/src/pjsip2/pjmedia/include/pjmedia-audiodev/voiceline_mode_usb_accessory.h`
- **Description**: Header with API definitions
- **Estimate**: 0.5 hours

#### 1.3 Modify Android JNI Device
- **File**: `android_jni_dev.c`
- **Description**: Add USB accessory mode audio routing
- **Estimate**: 1 hour

#### 1.4 Add Configuration Options
- **File**: `voiceline_mode_usb_accessory.c`
- **Description**: Runtime configuration struct and defaults
- **Estimate**: 0.5 hours

### Phase 2: Hardware Design

#### 2.1 Circuit Design
- **File**: `hardware/voiceline-adapter-usb-without-dac/schematic.pdf`
- **Description**: Design 4R+1C differential circuit schematic
- **Estimate**: 1 hour

#### 2.2 PCB Layout
- **File**: `hardware/voiceline-adapter-usb-without-dac/gerbers/`
- **Description**: Design 2-layer PCB layout
- **Estimate**: 2 hours

#### 2.3 Bill of Materials
- **File**: `hardware/voiceline-adapter-usb-without-dac/bom.csv`
- **Description**: Create BOM with component values and quantities
- **Estimate**: 0.5 hours

#### 2.4 Assembly Instructions
- **File**: `hardware/voiceline-adapter-usb-without-dac/assembly.md`
- **Description**: Document assembly steps
- **Estimate**: 0.5 hours

### Phase 3: Testing

#### 3.1 Unit Tests
- **Description**: Create C unit tests for USB accessory mode
- **Estimate**: 1 hour

#### 3.2 Integration Tests
- **Description**: Test with actual phone line connection
- **Estimate**: 2 hours

#### 3.3 Hardware Validation
- **Description**: Build prototype and validate audio quality
- **Estimate**: 4 hours

### Phase 4: Documentation

#### 4.1 User Guide
- **Description**: Document how to build and use the adapter
- **Estimate**: 1 hour

#### 4.2 API Documentation
- **Description**: Document software API
- **Estimate**: 0.5 hours

---

## Task Dependencies

```
1.1 InversionPort Integration
         │
         ▼
1.2 Header File
         │
         ▼
1.3 Modify Android JNI ───► 2.1 Circuit Design
         │                          │
         ▼                          ▼
1.4 Configuration           2.2 PCB Layout
         │                          │
         └─────────────┬────────────┘
                       │
                       ▼
                 2.3 BOM + 2.4 Assembly
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
                 4.1 User Guide + 4.2 API Docs
```

---

## File Changes Summary

### New Files

| Path | Purpose |
|------|---------|
| `voiceline_mode_usb_accessory.c` | USB accessory mode driver |
| `voiceline_mode_usb_accessory.h` | Header file |
| `hardware/.../schematic.pdf` | Circuit schematic |
| `hardware/.../gerbers/*` | PCB fabrication files |
| `hardware/.../bom.csv` | Bill of materials |
| `hardware/.../assembly.md` | Assembly instructions |

### Modified Files

| Path | Changes |
|------|---------|
| `android_jni_dev.c` | Add USB accessory mode routing |

---

## Estimates

| Phase | Hours |
|-------|-------|
| Software | 4 |
| Hardware | 4 |
| Testing | 7 |
| Documentation | 1.5 |
| **Total** | **16.5** |

---

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Device compatibility issues | High | Test on multiple devices |
| Audio quality below expectations | Medium | Optimize 4R+1C values |
| USB Type-C spec variations | Medium | Follow USB-IF spec strictly |

---

## Approval

- [ ] Plan reviewed by: [name]
- [ ] Plan approved on: [date]

---

*Created by /sdd - USB Audio Accessory Mode adapter plan*
