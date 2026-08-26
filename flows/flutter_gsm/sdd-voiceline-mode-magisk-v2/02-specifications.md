# Specifications: Magisk Voice Recording Integration

**Status**: DRAFT
**Type**: SDD (Spec-Driven Development)
**Module**: magisk-voice-recording
**Generated**: 2026-03-06 by /legacy

---

## System Architecture

### Magisk Module Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Magisk Framework                                                │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Mount Overlay FS                                          │  │
│  │  /data/adb/modules/gateway/ → /system/                    │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              ▼                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  System Permissions                                        │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │ privapp-permissions-gateway.xml                      │  │  │
│  │  │ /system/etc/permissions/                             │  │  │
│  │  │                                                       │  │  │
│  │  │ Grants to one.telefon.gateway:                        │  │  │
│  │  │  • CAPTURE_AUDIO_OUTPUT                               │  │  │
│  │  │  • READ_PRECISE_PHONE_STATE                           │  │  │
│  │  │  • MODIFY_PHONE_STATE                                 │  │  │
│  │  │  • READ_LOGS                                          │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Gateway App (one.telefon.gateway)                               │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Android AudioRecord                                       │  │
│  │  Audio Source: VOICE_CALL                                  │  │
│  │  Requires: CAPTURE_AUDIO_OUTPUT                            │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  PJSIP Audio Device                                        │  │
│  │  android_jni_dev.c                                         │  │
│  │  Captures: UPLINK + DOWNLINK                               │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  LineInfo Model                                            │  │
│  │  canRecordVoiceToRadio = true                              │  │
│  │  canGetVoiceFromRadio = true                               │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Permission Grant Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Device     │     │   Magisk     │     │   System     │
│    Boot      │     │   Install    │     │   Server     │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       │ Boot completed     │                    │
       ├───────────────────>│                    │
       │                    │                    │
       │                    │ Mount module       │
       │                    │ /system/etc/...    │
       │                    ├───────────────────>│
       │                    │                    │
       │                    │                    │ Parse XML
       │                    │                    │ Grant perms
       │                    │                    │
       │                    │                    │ Package installed
       │<─────────────────────────────────────────┤
       │                    │                    │
       │ App starts         │                    │
       ├─────────────────────────────────────────>│
       │                    │                    │
       │                    │                    │ Check perms
       │<─────────────────────────────────────────┤
       │ CAPTURE_AUDIO_OUTPUT granted             │
       │                    │                    │
       │ Initialize AudioRecord                   │
       ├─────────────────────────────────────────>│
       │ VOICE_CALL source                        │
       │                    │                    │
       │<─────────────────────────────────────────┤
       │ Audio capture started                    │
       │                    │                    │
```

---

## Component Specifications

### 1. Magisk Module Structure

```
magisk/gateway/
├── META-INF/com/google/android/
│   ├── update-binary          # Magisk update script (executable)
│   └── updater-script         # Updater script marker (#MAGISK)
├── common/
│   ├── post-fs-data.sh        # Early boot script (mode: post-fs-data)
│   ├── service.sh             # Late-start service (mode: late_start_service)
│   └── system.prop            # System properties (if PROPFILE=true)
├── system/
│   └── etc/permissions/
│       └── privapp-permissions-gateway.xml  # Privileged permissions
├── install.sh                 # Installation script (run during install)
└── module.prop                # Module metadata
```

### 2. Module Metadata (module.prop)

```properties
id=gateway
name=Gateway
version=1.0.0 (1.0.0)
versionCode=1
author=anton
description=Gateway App
```

**Specification**:
- `id`: Unique module identifier (lowercase, no spaces)
- `name`: Human-readable module name
- `version`: Version string (displayed in Magisk Manager)
- `versionCode`: Integer version code (for update checks)
- `author`: Module author
- `description`: Brief module description

### 3. Privapp Permissions XML (privapp-permissions-gateway.xml)

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

**Specification**:
- Root element: `<permissions>`
- Child element: `<privapp-permissions package="...">`
- Permission elements: `<permission name="..."/>`
- File location: `/system/etc/permissions/`
- File permissions: 0644 (rw-r--r--)
- Owner: root:root

### 4. Installation Script (install.sh)

```bash
##########################################################################################
# Config Flags
##########################################################################################

SKIPMOUNT=false      # Mount system files
PROPFILE=false       # Do not load system.prop (enable for Qualcomm restrictions)
POSTFSDATA=false     # No post-fs-data script
LATESTARTSERVICE=false  # No late-start service script

##########################################################################################
# Replace list
##########################################################################################

REPLACE="
"

##########################################################################################
# Installation Callbacks
##########################################################################################

print_modname() {
  ui_print "*******************************"
  ui_print "*   Gateway  - Anton          *"
  ui_print "*******************************"
}

on_install() {
  # Extract system files
  unzip -o "$ZIPFILE" 'system/*' -d $MODPATH >&2
  
  # Set permissions
  set_permissions
}

set_permissions() {
  set_perm_recursive $MODPATH 0 0 0755 0644
}
```

**Specification**:
- `SKIPMOUNT=false`: Magisk mounts files automatically
- `PROPFILE=false`: system.prop not loaded (change to `true` for Qualcomm restrictions)
- `POSTFSDATA=false`: No early boot script needed
- `LATESTARTSERVICE=false`: No late service script needed
- `on_install()`: Extract files, set permissions
- `set_permissions()`: Recursive 0755/0644 permissions

### 5. Update Script (update-binary)

**Specification**:
- Magisk v20.0+ compatible
- Checks Magisk version code (`MAGISK_VER_CODE >= 20000`)
- Uses Magisk util_functions.sh
- Supports boot mode installation (Magisk Manager)

**Key Functions**:
```bash
require_new_magisk() {
  ui_print " Please install Magisk v20.0+! "
  abort
}

# Version check
[ $MAGISK_VER_CODE -lt 20000 ] && require_new_magisk
```

### 6. Build Script (build.sh)

```bash
#!/bin/bash
cd gateway
zip -r ../gateway.zip *
cd ..
adb push gateway.zip /storage/self/primary/Download
```

**Specification**:
- Packages module into `gateway.zip`
- Pushes to device Download folder
- Ready for installation via Magisk Manager

---

## Audio Capture Specification

### Android AudioRecord API

```java
// Audio source for voice call recording
int audioSource = MediaRecorder.AudioSource.VOICE_CALL;

// Requires CAPTURE_AUDIO_OUTPUT permission
AudioRecord audioRecord = new AudioRecord(
    audioSource,
    sampleRate,
    channelConfig,
    audioFormat,
    bufferSize
);

// Start capture
audioRecord.startRecording();

// Read audio data
int bytesRead = audioRecord.read(audioBuffer, 0, bufferSize);
```

### PJSIP Android JNI Device

From `nmpjsip-builder/src/patch_2.9/`:

```c
// Audio capture sources (android_jni_dev.c)
#define AUDIO_SOURCE_VOICE_CALL        4  // Requires CAPTURE_AUDIO_OUTPUT
#define AUDIO_SOURCE_VOICE_UPLINK      5  // Requires CAPTURE_AUDIO_OUTPUT
#define AUDIO_SOURCE_VOICE_DOWNLINK    6  // Requires CAPTURE_AUDIO_OUTPUT
#define AUDIO_SOURCE_VOICE_COMMUNICATION 19 // VoIP communication

// JNI AudioRecord initialization
jclass audio_record_class = (*env)->FindClass(env, "android/media/AudioRecord");
jmethodID audio_record_ctor = (*env)->GetMethodID(
    env, 
    audio_record_class, 
    "<init>",
    "(IIIIII)V"  // Constructor signature
);

jobject audio_record = (*env)->NewObject(
    env,
    audio_record_class,
    audio_record_ctor,
    audio_source,    // VOICE_CALL
    sample_rate,     // 16000 or 48000
    channel_config,  // CHANNEL_IN_MONO
    audio_format,    // ENCODING_PCM_16BIT
    buffer_size,     // Calculated min buffer size
    0                // Session ID
);
```

### Audio Stream Types

| Stream Type | Value | Use Case | Recording Support |
|-------------|-------|----------|-------------------|
| AUDIO_STREAM_VOICE_CALL | 0 | Voice calls | ✓ (requires privileged perm) |
| AUDIO_STREAM_SYSTEM | 1 | System sounds | ✗ |
| AUDIO_STREAM_RING | 2 | Ringtone | ✗ |
| AUDIO_STREAM_MUSIC | 3 | Media playback | ✗ |
| AUDIO_STREAM_BLUETOOTH_SCO | 6 | Bluetooth headset | ✓ (with restrictions) |

### Qualcomm Restrictions

**System Properties** (if PROPFILE=true in install.sh):

```properties
# Disable concurrent recording restriction
voice.record.conc.disabled=false

# Disable VoIP recording restriction
voice.voip.conc.disabled=false
```

**Location**: `/system/build.prop` or via `system.prop` in Magisk module

**Effect**:
- Enables simultaneous voice recording + VoIP recording
- Required for GSM↔SIP bidirectional bridging
- Device-specific (Qualcomm chipsets only)

---

## LineInfo Capability Specification

### Capability Detection

```dart
class LineInfo {
  // Voice recording capabilities
  final bool canRecordVoiceToRadio;      // Record voice to radio interface
  final bool canGetVoiceFromRadio;       // Get voice from radio interface
  final bool canWriteToVoiceCommunication; // Write to voice comm stream

  // Detection logic (pseudo-code)
  static Future<LineInfo> detectCapabilities() async {
    // Check if CAPTURE_AUDIO_OUTPUT permission granted
    final hasCapturePerm = await PermissionChecker.hasCapturedAudioOutput();
    
    // Check if Qualcomm restrictions disabled
    final qualcommDisabled = await SystemProperties.getBool(
      'voice.record.conc.disabled',
      defaultValue: false
    );
    
    // Determine capabilities
    return LineInfo(
      canRecordVoiceToRadio: hasCapturePerm && qualcommDisabled,
      canGetVoiceFromRadio: hasCapturePerm,
      canWriteToVoiceCommunication: hasCapturePerm,
      // ... other fields
    );
  }
}
```

### Capability Matrix

| Condition | canRecordVoiceToRadio | canGetVoiceFromRadio | canWriteToVoiceCommunication |
|-----------|----------------------|---------------------|------------------------------|
| No Magisk | false | false | false |
| Magisk installed | true | true | true |
| Magisk + Qualcomm disabled | true | true | true |

---

## Gateway Configuration Specification

### enableCallRecording Flag

```dart
class GatewayConfig {
  final bool enableCallRecording;  // Default: false
  
  GatewayConfig({
    this.enableCallRecording = false,
    // ... other config
  });
  
  // Copy with modification
  GatewayConfig copyWith({bool? enableCallRecording}) {
    return GatewayConfig(
      enableCallRecording: enableCallRecording ?? this.enableCallRecording,
      // ...
    );
  }
}
```

**Usage**:
```dart
// Enable call recording
final config = gatewayConfig.copyWith(enableCallRecording: true);

// Check if recording enabled
if (config.enableCallRecording && lineInfo.canRecordVoiceToRadio) {
  // Start voice recording
  await audioRecorder.startRecording();
}
```

---

## Installation Flow Specification

### Step 1: Prepare Device

```
1. Device must be rooted with Magisk v20.0+
2. Magisk Manager installed
3. Gateway app installed (user app)
4. Download gateway.zip to device
```

### Step 2: Install Module

```
1. Open Magisk Manager
2. Navigate to Modules
3. Tap "Install from storage"
4. Select gateway.zip
5. Module installs:
   - Extracts system/* to Magisk mount
   - Copies privapp-permissions-gateway.xml
   - Sets permissions
6. Reboot device
```

### Step 3: Verify Installation

```
1. After reboot, open Settings → Apps
2. Find "Gateway" app
3. Check App Info → Permissions
4. Verify privileged permissions granted:
   - CAPTURE_AUDIO_OUTPUT (should show as granted)
   - READ_PRECISE_PHONE_STATE (should show as granted)
```

### Step 4: Enable Call Recording

```
1. Open Gateway app
2. Navigate to Settings
3. Enable "Call Recording" toggle
4. Verify LineInfo.canRecordVoiceToRadio = true
```

---

## Testing Specifications

### Test 1: Module Installation

```dart
test('Magisk module installs successfully', () async {
  // Prerequisites: Rooted device, Magisk v20.0+
  
  // Install module
  final result = await MagiskModule.install('gateway.zip');
  
  // Verify
  expect(result.success, true);
  expect(result.moduleId, 'gateway');
  expect(result.requiresReboot, true);
});
```

### Test 2: Permission Grant

```dart
test('CAPTURE_AUDIO_OUTPUT permission granted', () async {
  // After reboot
  
  // Check permission
  final hasPerm = await PermissionChecker.hasPermission(
    'android.permission.CAPTURE_AUDIO_OUTPUT'
  );
  
  expect(hasPerm, true);
});
```

### Test 3: Audio Capture

```dart
test('Voice call audio capture works', () async {
  // Prerequisites: Magisk module installed, permission granted
  
  // Initialize AudioRecord
  final recorder = AudioRecord(
    source: AudioSource.VOICE_CALL,
    sampleRate: 16000,
    channelConfig: ChannelConfiguration.MONO,
    audioFormat: AudioFormat.ENCODING_PCM_16BIT,
  );
  
  // Start recording
  await recorder.startRecording();
  
  // Verify capture
  final buffer = await recorder.read(1024);
  expect(buffer.isNotEmpty, true);
  expect(buffer.isSilent, false);  // Should capture audio
  
  await recorder.stopRecording();
});
```

### Test 4: LineInfo Capabilities

```dart
test('LineInfo reports recording capabilities', () async {
  // Prerequisites: Magisk module installed
  
  final lineInfo = await LineInfo.detect('slot_1');
  
  expect(lineInfo.canRecordVoiceToRadio, true);
  expect(lineInfo.canGetVoiceFromRadio, true);
  expect(lineInfo.canWriteToVoiceCommunication, true);
});
```

### Test 5: Qualcomm Restrictions

```dart
test('Qualcomm restrictions disabled', () async {
  // Check system properties
  final recordDisabled = await SystemProperties.getBool(
    'voice.record.conc.disabled'
  );
  final voipDisabled = await SystemProperties.getBool(
    'voice.voip.conc.disabled'
  );
  
  // Should be false (recording enabled)
  expect(recordDisabled, false);
  expect(voipDisabled, false);
});
```

---

## Known Issues and Limitations

### Issue 1: Device Compatibility

**Problem**: Not all devices support VOICE_CALL audio source

**Affected Devices**: Some Samsung, Xiaomi, Huawei devices

**Workaround**: Use VOICE_UPLINK + VOICE_DOWNLINK separately

### Issue 2: Android Version Changes

**Problem**: Android 10+ restricts background audio capture

**Impact**: Recording may stop when app in background

**Workaround**: Use foreground service with persistent notification

### Issue 3: Encryption

**Problem**: Some devices encrypt voice audio path

**Impact**: Recorded audio may be silent or one-sided

**Workaround**: Device-specific patches required

### Issue 4: Legal Compliance

**Problem**: Call recording laws vary by jurisdiction

**Impact**: May be illegal without consent

**Mitigation**: Implement consent mechanism, user warnings

---

## Legacy Additions - 2026-03-06

> Added by /legacy after analyzing apgateway third-party module

### Enhanced system.prop Configuration

**Discovered from**: `3rdparty/apgateway/system.prop`

**Missing in current spec**: Complete Qualcomm audio restrictions disable

```properties
# Allow concurrent VoIP audio during GSM voice calls
voice.record.conc.disabled=false
voice.voip.conc.disabled=false
voice.playback.conc.disabled=false

# Disable Qualcomm Fluence noise/echo processing
ro.qc.sdk.audio.fluencetype=none
persist.audio.fluence.voicerec=false
persist.audio.fluence.speaker=false
persist.audio.fluence.voicecall=false
```

**Impact**: 
- Current spec only mentions 2 properties
- apgateway uses 7 properties for full audio control
- Fluence disable is critical - modem AEC cancels SIP audio from GSM uplink

**Recommendation**: Update `install.sh` to set `PROPFILE=true` and use enhanced system.prop

### Extended Privileged Permissions

**Discovered from**: `3rdparty/apgateway/system/etc/permissions/privapp-permissions-gateway.xml`

**Missing in current spec**: 7 additional permissions for full telephony integration

```xml
<!-- Additional telephony permissions -->
<permission name="android.permission.READ_PRIVILEGED_PHONE_STATE" />
<permission name="android.permission.CALL_PRIVILEGED" />

<!-- System permissions -->
<permission name="android.permission.WRITE_SECURE_SETTINGS" />
<permission name="android.permission.INTERACT_ACROSS_USERS" />

<!-- Telecom permissions -->
<permission name="android.permission.REGISTER_CALL_PROVIDER" />
<permission name="android.permission.REGISTER_SIM_SUBSCRIPTION" />
<permission name="android.permission.BIND_INCALL_SERVICE" />
<permission name="android.permission.BIND_TELECOM_CONNECTION_SERVICE" />
```

**Impact**:
- Current spec has only 4 permissions
- Missing permissions limit telephony/telecom integration capabilities
- `BIND_INCALL_SERVICE` required for proper InCallService implementation
- `CALL_PRIVILEGED` enables programmatic call initiation

**Recommendation**: Add all 11 permissions to privapp-permissions-gateway.xml

### service.sh - APK Synchronization Service

**Discovered from**: `3rdparty/apgateway/service.sh`

**Missing in current spec**: Automatic APK sync on boot

```bash
#!/system/bin/sh
MODDIR="${0%/*}"
TAG="GatewayMagisk"

PRIV_DIR="$MODDIR/system/priv-app/Gateway"
PRIV_APK="$PRIV_DIR/Gateway.apk"

# Sync APK from /data/app to priv-app overlay
APK_PATH=$(pm path com.callagent.gateway | head -1 | sed 's/^package://')

if [ -f "$APK_PATH" ] && [ -f "$PRIV_APK" ]; then
    if ! cmp -s "$APK_PATH" "$PRIV_APK" 2>/dev/null; then
        cp "$APK_PATH" "$PRIV_APK"
        chmod 644 "$PRIV_APK"
        log -t "$TAG" "Synced updated APK (reboot needed)"
    fi
fi

# Log permission status
PERM_DUMP=$(dumpsys package com.callagent.gateway)
if echo "$PERM_DUMP" | grep -q "CAPTURE_AUDIO_OUTPUT.*granted=true"; then
    log -t "$TAG" "CAPTURE_AUDIO_OUTPUT: GRANTED"
else
    log -t "$TAG" "CAPTURE_AUDIO_OUTPUT: NOT GRANTED"
fi
```

**Benefits**:
- Automatically syncs APK updates from `/data/app` to priv-app overlay
- Logs permission grant status for debugging
- No need to reinstall Magisk module after app updates

**Recommendation**: Implement service.sh with LATESTARTSERVICE=true

### post-fs-data.sh - Mount Guarantee

**Discovered from**: `3rdparty/apgateway/post-fs-data.sh`

**Missing in current spec**: skip_mount removal

```bash
#!/system/bin/sh
MODDIR="${0%/*}"
rm -f "$MODDIR/skip_mount"
```

**Purpose**: Ensures module filesystem overlay is active even if skip_mount exists

**Recommendation**: Implement post-fs-data.sh with POSTFSDATA=true

### Enhanced install.sh

**Discovered from**: `3rdparty/apgateway/install.sh`

**Missing in current spec**:
1. `SKIPUNZIP=1` for manual extraction control
2. APK fallback copying from installed app
3. User guidance if APK not found
4. Explicit priv-app directory permissions
5. skip_mount removal

**Recommendation**: Update install.sh with enhanced installation logic

### update-binary Standardization

**Discovered from**: `3rdparty/apgateway/META-INF/com/google/android/update-binary`

**Current spec uses**: Manual installation logic

**apgateway uses**: Standard Magisk `install_module` function

**Benefits**:
- More robust installation
- Better error handling
- Standard Magisk framework integration

**Recommendation**: Update update-binary to use install_module function

---

## Security Considerations

### Permission Scope

**Principle**: Minimal permission scope

```xml
<!-- Only grant to specific package -->
<privapp-permissions package="one.telefon.gateway">
  <!-- Only necessary permissions -->
  <permission name="android.permission.CAPTURE_AUDIO_OUTPUT"/>
</privapp-permissions>
```

### Data Protection

**Requirements**:
- Encrypt recorded call audio
- Store in app-private storage
- Implement secure deletion
- Access control (app-only access)

### Audit Trail

**Logging**:
- Log permission usage
- Log recording start/stop events
- Log file access
- Retain logs for compliance

---

## Deployment Checklist

- [ ] Magisk v20.0+ installed on device
- [ ] Device rooted
- [ ] Gateway app installed
- [ ] gateway.zip downloaded to device
- [ ] Module installed via Magisk Manager
- [ ] Device rebooted
- [ ] Permissions verified (CAPTURE_AUDIO_OUTPUT granted)
- [ ] Call recording enabled in settings
- [ ] Test call recording successful
- [ ] Legal compliance reviewed

---

*Generated by /legacy reverse engineering*
*Status: DRAFT*
