# Requirements: Voice Line Access

> **Version**: 1.0
> **Status**: DRAFT
> **Last Updated**: 2026-03-11
> **Source**: sdd-voiceline-* flows

---

## Problem Statement

**What problem are we solving?**

The GOSTsimbox Android Gateway needs to route audio between SIP and the phone line (GSM radio). Different Android devices support different methods for accessing the phone line, ranging from built-in hardware codecs to external adapters.

**Why does this matter?**

This enables:
- Flexible deployment across different Android devices
- Optimal audio quality based on device capabilities
- Fallback options when preferred method is unavailable
- Support for both rooted and non-rooted devices

---

## Voice Line Access Methods

### Method 1: TTY Port (Serial Interface)

**Description**: Direct access to phone modem via serial port interface.

**Characteristics**:
- High quality digital audio
- Device-specific paths
- No root required (on some devices)
- Requires device-specific configuration

**Port Paths**:
```
/dev/ttyUSB*      # USB serial (common)
/dev/ttyHS*       # High-speed serial (Qualcomm)
/dev/ttyGS*       # GSM serial
/sys/class/tty/*  # Sysfs interface
```

**Note**: Path varies by device model and manufacturer.

---

### Method 2: Telecom API (Android Standard)

**Description**: Standard Android `android.telecom.*` API for call control.

**Characteristics**:
- Works on all Android devices
- Medium quality (uses device audio path)
- No special permissions required
- Limited control over audio routing

**API Classes**:
- `TelecomManager` - Call management
- `ConnectionService` - Call control
- `AudioManager` - Audio routing

---

### Method 3: System-Level Access (Magisk)

**Description**: System-level integration via Magisk module for privileged audio access.

**Characteristics**:
- High quality audio capture
- Requires root access
- **Not mentioned in UI** (app store compliance)
- Systemless installation (preserves OTA)

**Permissions Granted**:
- `CAPTURE_AUDIO_OUTPUT` - Capture call audio
- `READ_PRECISE_PHONE_STATE` - Detailed call state
- `MODIFY_PHONE_STATE` - Call control

**UI Treatment**:
- Feature appears as "Enhanced Audio Access" or "Advanced Mode"
- No explicit mention of Magisk/root
- Auto-detected and enabled if available

---

### Method 4: External Dongle

**Description**: External hardware adapter connected via USB-C or TRRS.

**Characteristics**:
- Works on any Android device
- High quality (depends on dongle type)
- Requires external hardware
- Detailed in `vdd-dongles` flow

**Interface Types**:
- USB-C with DAC (digital)
- USB-C Audio Accessory (analog)
- TRRS 3.5mm (analog)

**See**: `flows/vdd-dongles/02-visual.md` for dongle types and UI.

---

## User Stories

### Primary

**As a** GSM-SIP Gateway Operator
**I want** the system to automatically select the best available voice line method
**So that** I get optimal audio quality without manual configuration

### Secondary

**As a** System Integrator
**I want** to know which methods are available on a device
**So that** I can choose appropriate hardware

**As a** Developer
**I want** device-specific TTY port paths documented
**So that** I can add support for new devices

**As a** User
**I want** clear status indication of which method is active
**So that** I understand the audio quality expectations

---

## Acceptance Criteria

### Must Have

1. **Given** a device with multiple voice line methods available
   **When** the gateway starts
   **Then** the best available method is automatically selected

2. **Given** the preferred method is unavailable
   **When** fallback is needed
   **Then** the next best method is automatically selected

3. **Given** a voice line method is active
   **When** a call is in progress
   **Then** audio quality is maintained throughout the call

4. **Given** Magisk is installed
   **When** the app displays status
   **Then** no mention of "Magisk" or "root" appears in UI

### Should Have

1. User-visible indication of which method is currently active
2. Manual override option to select a specific method
3. Audio quality indicator for current method
4. Diagnostic information for troubleshooting

### Won't Have (This Iteration)

- Automatic Magisk installation
- Device database with pre-configured TTY paths
- Real-time method switching during active call
- Audio quality comparison between methods

---

## Constraints

### Technical

- **Must** support Android 8.0+ (API 26+)
- **Must** work without root on standard devices
- **Must** not mention Magisk/root in UI (app store compliance)
- **Must** integrate with existing PJSIP audio path

### Performance

- **Must** select method within 5 seconds of app start
- **Must** maintain audio quality < 10ms latency
- **Should** detect method availability without user intervention

### Platform

- **Target**: Android devices with varying capabilities
- **Integration**: Existing GOSTsimbox audio architecture
- **Deployment**: App store distribution (Google Play, etc.)

### Dependencies

- **Requires**: `vdd-dongles` - External dongle UI and detection
- **Requires**: PJSIP audio endpoint
- **Requires**: Android TelephonyManager API

---

## Open Questions

- [ ] **TTY Paths**: What are the exact TTY port paths for common device models?
- [ ] **Detection Order**: What is the priority order for method selection?
- [ ] **Magisk Naming**: What user-friendly name to use for Magisk mode in UI?
- [ ] **Fallback UI**: How to inform user when fallback occurs?
- [ ] **Direct Line**: Which exact devices have built-in RJ11 codec?

---

## References

### Related Documentation

- `flows/vdd-dongles/` - External dongle UI and types
- `flows/sdd-voiceline-mode-direct/` - Direct mode (acoustic coupling)
- `flows/sdd-voiceline-mode-magisk/` - Magisk integration
- `flows/sdd-voiceline-mode-magisk-v2/` - Magisk v2 permissions

### Android APIs

- `android.telecom.TelecomManager`
- `android.telecom.ConnectionService`
- `android.media.AudioManager`
- `android.hardware.usb.UsbManager` (for dongle detection)

---

## Approval

- [ ] Reviewed by: [name]
- [ ] Approved on: [date]
- [ ] Notes: [any conditions or clarifications]

---

*Created by /vdd - Voice line access methods requirements*
