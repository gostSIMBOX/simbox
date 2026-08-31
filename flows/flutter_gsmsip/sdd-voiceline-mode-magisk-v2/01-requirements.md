# Requirements: Magisk Voice Recording Integration

**Status**: DRAFT
**Type**: SDD (Spec-Driven Development)
**Module**: magisk-voice-recording
**Generated**: 2026-03-06 by /legacy

---

## Overview

The Magisk Voice Recording Integration module provides system-level privileges to enable voice call recording from the Android phone line (radio interface). It uses Magisk's systemless root framework to grant privileged permissions and disable hardware-specific recording restrictions, enabling the gateway app to capture bidirectional call audio for GSM↔SIP bridging.

---

## Functional Requirements

### FR-1: Privileged Permissions Grant

The system SHALL grant the following privileged permissions to the gateway app (`one.telefon.gateway`):

| Permission | Purpose | Required For |
|------------|---------|--------------|
| `android.permission.CAPTURE_AUDIO_OUTPUT` | Capture audio from voice call sources | Voice recording from radio |
| `android.permission.READ_PRECISE_PHONE_STATE` | Access detailed phone state | Call state synchronization |
| `android.permission.MODIFY_PHONE_STATE` | Modify phone state | Call control operations |
| `android.permission.READ_LOGS` | Access system logs | Debugging and monitoring |

**Source**: `magisk/gateway/system/etc/permissions/privapp-permissions-gateway.xml`

### FR-2: Privapp Permissions Whitelist

The system SHALL implement a privapp permissions whitelist XML file:

**Requirements**:
- FR-2.1: File location: `/system/etc/permissions/privapp-permissions-gateway.xml`
- FR-2.2: Package name: `one.telefon.gateway`
- FR-2.3: Valid XML structure with `<permissions>` root element
- FR-2.4: Each permission declared with `<permission name="..."/>` element
- FR-2.5: Permissions restricted to privileged-only permissions

**Source**: `magisk/gateway/system/etc/permissions/privapp-permissions-gateway.xml`

### FR-3: Magisk Module Installation

The system SHALL install as a Magisk module:

**Requirements**:
- FR-3.1: Module ID: `gateway`
- FR-3.2: Require Magisk v20.0+ (version code 20000+)
- FR-3.3: Extract system files to Magisk mount point
- FR-3.4: Set proper file permissions (0755 for directories, 0644 for files)
- FR-3.5: Install as systemless modification (no system partition changes)

**Source**: `magisk/gateway/META-INF/com/google/android/update-binary`, `magisk/gateway/install.sh`

### FR-4: Qualcomm Recording Restrictions Disable

The system SHALL provide mechanism to disable Qualcomm audio recording restrictions:

**Requirements**:
- FR-4.1: Set system property: `voice.record.conc.disabled=false`
- FR-4.2: Set system property: `voice.voip.conc.disabled=false`
- FR-4.3: Apply properties during boot (post-fs-data mode)
- FR-4.4: Enable concurrent voice recording and VoIP recording

**Source**: `flows/sdd-patch-management/02-specifications.md` (Audio API research)

### FR-5: Voice Capture Source Support

The system SHALL support multiple Android audio capture sources:

| Source | Purpose | Permission Required |
|--------|---------|---------------------|
| `VOICE_CALL` | Full bidirectional call audio | CAPTURE_AUDIO_OUTPUT |
| `VOICE_UPLINK` | Local party (microphone) audio | CAPTURE_AUDIO_OUTPUT |
| `VOICE_DOWNLINK` | Remote party (speaker) audio | CAPTURE_AUDIO_OUTPUT |
| `VOICE_COMMUNICATION` | VoIP communication audio | CAPTURE_AUDIO_OUTPUT |

**Source**: `nmpjsip-builder/src/patch_2.9/src/pjsip2/pjmedia/src/pjmedia-audiodev/android_jni_dev.c`

### FR-6: Line Capability Flags

The system SHALL expose voice recording capabilities via `LineInfo` model:

**Capabilities**:
- FR-6.1: `canRecordVoiceToRadio` - Can record voice call audio to radio interface
- FR-6.2: `canGetVoiceFromRadio` - Can receive voice audio from radio interface
- FR-6.3: `canWriteToVoiceCommunication` - Can write audio to voice communication stream

**Default State**: All capabilities disabled (`false`) until Magisk module installed

**Source**: `lib/models/line_info.dart`

### FR-7: Call Recording Configuration

The system SHALL provide configuration option for call recording:

**Requirements**:
- FR-7.1: Config property: `enableCallRecording` (boolean)
- FR-7.2: Default value: `false` (disabled by default)
- FR-7.3: Configurable via gateway settings
- FR-7.4: Requires Magisk module to be functional

**Source**: `lib/domain/entities/gateway_config.dart`

### FR-8: System App Installation

The system SHALL install the gateway app as a system application:

**Requirements**:
- FR-8.1: App installed in system partition context (via Magisk mount)
- FR-8.2: Privileged permissions automatically granted on boot
- FR-8.3: App survives factory reset (if Magisk preserved)
- FR-8.4: No APK modification required (permissions granted externally)

**Source**: Magisk framework documentation

---

## Non-Functional Requirements

### NFR-1: Systemless Operation

- NFR-1.1: SHALL NOT modify system partition
- NFR-1.2: SHALL use Magisk's overlay filesystem
- NFR-1.3: SHALL be removable without system damage
- NFR-1.4: SHALL support OTA updates (with Magisk preservation)

### NFR-2: Security

- NFR-2.1: SHALL only grant permissions to specific package (`one.telefon.gateway`)
- NFR-2.2: SHALL NOT expose privileged permissions to other apps
- NFR-2.3: SHALL require Magisk root access for installation
- NFR-2.4: SHALL validate Magisk version before installation

### NFR-3: Compatibility

- NFR-3.1: SHALL support Android 8.0+ (API 26+)
- NFR-3.2: SHALL support Magisk v20.0+ (version code 20000+)
- NFR-3.3: SHALL support Qualcomm chipsets (recording restrictions)
- NFR-3.4: SHALL support dual-SIM devices

### NFR-4: Performance

- NFR-4.1: SHALL NOT impact call quality or latency
- NFR-4.2: SHALL NOT increase boot time significantly
- NFR-4.3: SHALL handle audio capture with minimal CPU overhead
- NFR-4.4: SHALL support concurrent recording (both parties)

### NFR-5: Reliability

- NFR-5.1: SHALL persist across reboots
- NFR-5.2: SHALL auto-start with system boot
- NFR-5.3: SHALL handle permission grant failures gracefully
- NFR-5.4: SHALL log installation errors for debugging

### NFR-6: Maintainability

- NFR-6.1: SHALL provide clear installation documentation
- NFR-6.2: SHALL log module installation status
- NFR-6.3: SHALL support module updates via Magisk Manager
- NFR-6.4: SHALL provide uninstallation mechanism

---

## Configuration Entities

### Magisk Module Metadata

```properties
id=gateway
name=Gateway
version=1.0.0 (1.0.0)
versionCode=1
author=anton
description=Gateway App
```

### Privapp Permissions Configuration

```xml
<?xml version="1.0" encoding="utf-8"?>
<permissions>
    <privapp-permissions package="one.telefon.gateway">
        <permission name="android.permission.READ_LOGS"/>
        <permission name="android.permission.CAPTURE_AUDIO_OUTPUT"/>
        <permission name="android.permission.READ_PRECISE_PHONE_STATE"/>
        <permission name="android.permission.MODIFY_PHONE_STATE"/>
    </privapp-permissions>
</permissions>
```

### Qualcomm System Properties

```properties
voice.record.conc.disabled=false
voice.voip.conc.disabled=false
```

### Gateway Configuration

```dart
class GatewayConfig {
  final bool enableCallRecording;  // Default: false
}
```

### LineInfo Capabilities

```dart
class LineInfo {
  final bool canRecordVoiceToRadio;
  final bool canGetVoiceFromRadio;
  final bool canWriteToVoiceCommunication;
}
```

---

## Dependencies

### External Dependencies

| Dependency | Purpose | Version |
|------------|---------|---------|
| Magisk | Root management framework | v20.0+ |
| Android System | Privapp permissions framework | API 26+ |
| Qualcomm BSP | Audio hardware abstraction | Device-specific |

### Internal Dependencies

| Module | Purpose |
|--------|---------|
| Gateway App (`one.telefon.gateway`) | Target app for permissions |
| PJSIP Audio Device | Audio capture implementation |
| LineInfo Model | Capability exposure |
| GatewayConfig | Feature configuration |

---

## Constraints

### C-1: Root Access Required

**Constraint**: Device must be rooted with Magisk v20.0+

**Impact**: Limits deployment to rooted devices only

**Mitigation**: Provide clear rooting instructions, support common rooting tools

### C-2: System Property Restrictions

**Constraint**: Some devices may lock system properties (cannot be modified)

**Impact**: Qualcomm restrictions may not be disableable on all devices

**Mitigation**: Test on target devices, provide device-specific workarounds

### C-3: Android Version Changes

**Constraint**: Android security model evolves (permissions may change)

**Impact**: Future Android versions may break privileged permissions

**Mitigation**: Monitor Android security changes, update module accordingly

### C-4: Hardware Dependencies

**Constraint**: Audio capture quality depends on hardware capabilities

**Impact**: Some devices may not support bidirectional recording

**Mitigation**: Detect hardware capabilities, provide fallback options

---

## Open Questions

1. **CallRecorder APK**: Should the module include CallRecorder APK installation?
   - Currently commented out in `install.sh`
   - **Recommendation**: Keep optional, provide as separate download

2. **System Properties**: Should `system.prop` be enabled for Qualcomm restrictions?
   - Currently `PROPFILE=false` in `install.sh`
   - **Recommendation**: Enable for Qualcomm devices, detect chipset first

3. **Boot Scripts**: Should `post-fs-data.sh` or `service.sh` be implemented?
   - Currently empty scripts
   - **Recommendation**: Implement for dynamic permission checks and logging

4. **Multi-App Support**: Should permissions be granted to multiple packages?
   - Currently only `one.telefon.gateway`
   - **Recommendation**: Keep single-package for security, support aliases if needed

---

## Risks

### R-1: Security Vulnerability

**Risk**: Privileged permissions could be exploited if app compromised

**Likelihood**: Low (app is trusted system component)

**Impact**: High (system-level access)

**Mitigation**: App security hardening, minimal permission scope

### R-2: Device Instability

**Risk**: Audio capture may interfere with phone calls

**Likelihood**: Medium (depends on implementation)

**Impact**: High (call quality degradation)

**Mitigation**: Extensive testing, provide disable option

### R-3: Legal Compliance

**Risk**: Call recording may violate local laws

**Likelihood**: High (varies by jurisdiction)

**Impact**: High (legal liability)

**Mitigation**: Clear user warnings, consent mechanisms, compliance documentation

### R-4: Magisk Detection

**Risk**: Some apps (banking, DRM) detect Magisk and refuse to run

**Likelihood**: Medium (depends on user's app ecosystem)

**Impact**: Medium (other apps may break)

**Mitigation**: MagiskHide support, provide uninstallation instructions

---

*Generated by /legacy reverse engineering*
*Status: DRAFT*
