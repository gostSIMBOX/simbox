# 02-Technical Specifications: IMEI Modification

> **Status**: DRAFT
> **Type**: DDD (Domain-Driven Development)
> **Date**: 2026-03-07
> **Module**: imei-modification

---

## Overview

This document specifies the technical implementation of IMEI modification features for Huawei and Qtech devices. This module provides safe IMEI reading, writing, backup, and restoration capabilities.

---

## ⚠️ Legal Warning

**IMPORTANT**: IMEI modification may be illegal in your jurisdiction. This tool is provided for:

**Permitted Use Cases:**
- ✅ Restoring IMEI after firmware flash/reset
- ✅ Replacing faulty device motherboard
- ✅ Testing and development purposes
- ✅ Research and educational purposes

**Prohibited Use Cases:**
- ❌ Cloning IMEI from stolen devices
- ❌ Bypassing carrier blacklists
- ❌ Evading law enforcement tracking
- ❌ Any fraudulent activity

**Users must acknowledge legal warnings before using this feature.**

---

## Architecture

### Component Hierarchy

```
IMEI Modification Module
├── DeviceCommunicator      # Serial/USB communication
├── HuaweiNVManager         # NV item management
├── IMEIValidator          # Luhn algorithm validation
├── IMEIBackupManager      # Backup/restore operations
└── ATCommandProcessor     # AT command handling
```

### Supported Devices

| Device | Method | Status |
|--------|--------|--------|
| Huawei E3372 | AT Commands | ✅ Supported |
| Huawei E5573 | AT Commands | ✅ Supported |
| Huawei B525 | AT Commands | ✅ Supported |
| Huawei E8372 | AT Commands | ✅ Supported |
| Qtech QMP-M1-N | Proprietary | ⚠️ Limited |

---

## Class Specifications

### DeviceCommunicator

**Purpose**: Handle serial communication with devices via USB

**API**:
```dart
class DeviceCommunicator {
  /// Initialize communicator
  Future<void> initialize();

  /// Detect connected devices
  Future<List<DeviceInfo>> detectDevices();

  /// Open connection to device
  Future<bool> connect(DeviceInfo device);

  /// Close connection
  Future<void> disconnect();

  /// Send AT command
  Future<String> sendCommand(String command, {Duration? timeout});

  /// Check if connected
  bool get isConnected;

  /// Connection state stream
  Stream<ConnectionState> get connectionStateStream;
}

class DeviceInfo {
  final String port;
  final String description;
  final String? serialNumber;
  final String? manufacturer;
  final String? model;
  final DeviceType type;
}

enum DeviceType {
  huawei,
  qtech,
  unknown,
}
```

**Implementation Notes**:
- Uses `serial_port` package for USB communication
- Auto-detects Huawei/Qtech devices by VID/PID
- Handles connection timeouts gracefully
- Supports multiple concurrent connections

---

### HuaweiNVManager

**Purpose**: Manage NV (Non-Volatile) items on Huawei devices

**API**:
```dart
class HuaweiNVManager {
  /// Read NV item
  Future<NVItem> readNVItem(int itemId);

  /// Write NV item
  Future<bool> writeNVItem(int itemId, Uint8List data);

  /// Backup NV items
  Future<NVBackup> backupNVItems(List<int> itemIds);

  /// Restore NV items
  Future<bool> restoreNVItems(NVBackup backup);

  /// Get IMEI NV item (0x0001)
  Future<String> readIMEI();

  /// Set IMEI NV item
  Future<bool> writeIMEI(String imei);
}

class NVItem {
  final int itemId;
  final Uint8List data;
  final DateTime readTime;
}

class NVBackup {
  final String deviceSerial;
  final String deviceModel;
  final Map<int, NVItem> items;
  final DateTime backupDate;
  final String checksum;
}
```

**NV Item IDs**:
| ID | Name | Description |
|----|------|-------------|
| 0x0001 | NV_IMEI | Device IMEI |
| 0x0002 | NV_ESN | Device ESN |
| 0x0003 | NV_MEID | Device MEID |

---

### ATCommandProcessor

**Purpose**: Process AT commands for device communication

**Supported Commands**:

| Command | Description | Response |
|---------|-------------|----------|
| `AT` | Test command | `OK` |
| `AT+CGSN` | Read IMEI | IMEI number |
| `AT+CGSN=1` | Read IMEI (alternative) | IMEI number |
| `AT^CIMEI=<IMEI>` | Write IMEI | `OK` or `ERROR` |
| `AT+CFUN=1,1` | Reboot device | `OK` |
| `AT^ICCID?` | Read ICCID | ICCID number |
| `AT+CIMI` | Read IMSI | IMSI number |
| `AT+CSQ` | Signal quality | `+CSQ: <rssi>,<ber>` |
| `AT+COPS?` | Operator selection | Current operator |

**Implementation**:
```dart
class ATCommandProcessor {
  final DeviceCommunicator communicator;

  /// Send test command
  Future<bool> test();

  /// Read IMEI
  Future<String> readIMEI();

  /// Write IMEI
  Future<bool> writeIMEI(String imei);

  /// Reboot device
  Future<bool> reboot();

  /// Read ICCID
  Future<String> readICCID();

  /// Read IMSI
  Future<String> readIMSI();

  /// Get signal quality
  Future<SignalQuality> getSignalQuality();
}
```

---

### IMEIValidator

**Purpose**: Validate IMEI using Luhn algorithm

**API**:
```dart
class IMEIValidator {
  /// Validate IMEI format and checksum
  static bool isValid(String imei);

  /// Calculate Luhn check digit
  static String calculateCheckDigit(String imeiWithoutCheck);

  /// Verify Luhn checksum
  static bool verifyLuhn(String imei);

  /// Parse IMEI structure
  static IMEIStructure parse(String imei);
}

class IMEIStructure {
  final String reportingBodyIdentifier;  // AA (2 digits)
  final String modelIdentifier;          // BBBBBB (6 digits)
  final String serialNumber;             // CCCCCC (6 digits)
  final String checkDigit;               // D (1 digit)

  /// Full IMEI without check digit (14 digits)
  String get imeiWithoutCheck;

  /// Full IMEI with check digit (15 digits)
  String get fullIMEI;
}
```

**Luhn Algorithm**:
```dart
bool verifyLuhn(String imei) {
  if (!RegExp(r'^\d{15}$').hasMatch(imei)) return false;

  int sum = 0;
  bool isEven = false;

  // Loop through digits from right to left
  for (int i = imei.length - 1; i >= 0; i--) {
    int digit = int.parse(imei[i]);

    if (isEven) {
      digit *= 2;
      if (digit > 9) digit -= 9;
    }

    sum += digit;
    isEven = !isEven;
  }

  return sum % 10 == 0;
}
```

---

### IMEIBackupManager

**Purpose**: Manage IMEI backups and restoration

**Backup Format**:
```json
{
  "version": "1.0",
  "device": {
    "serial": "C657843210",
    "model": "Huawei E3372",
    "manufacturer": "Huawei"
  },
  "original_imei": "861234567890123",
  "backup_date": "2024-03-04T10:00:00Z",
  "nv_items": {
    "1": "base64_encoded_data",
    "2": "base64_encoded_data",
    "3": "base64_encoded_data"
  },
  "checksum": "sha256_hash_of_backup"
}
```

**API**:
```dart
class IMEIBackupManager {
  /// Create backup
  Future<BackupResult> createBackup({
    required String deviceSerial,
    required String deviceModel,
    required String currentIMEI,
  });

  /// Restore from backup
  Future<RestoreResult> restoreBackup(String backupPath);

  /// List available backups
  Future<List<BackupInfo>> listBackups();

  /// Delete backup
  Future<bool> deleteBackup(String backupPath);

  /// Verify backup integrity
  Future<bool> verifyBackup(String backupPath);
}

class BackupResult {
  final bool success;
  final String? backupPath;
  final String? error;
}

class RestoreResult {
  final bool success;
  final String? restoredIMEI;
  final String? error;
}
```

---

## Safety Features

### Pre-Operation Checks

```dart
class SafetyChecks {
  /// Verify device is supported
  static Future<bool> verifyDeviceSupport(DeviceInfo device);

  /// Check battery level (minimum 50%)
  static Future<bool> checkBatteryLevel();

  /// Verify USB connection stability
  static Future<bool> verifyConnectionStability();

  /// Check if IMEI is already backed up
  static Future<bool> checkBackupExists(String deviceSerial);

  /// Get user acknowledgment of legal warnings
  static Future<bool> getUserLegalAcknowledgment();
}
```

### Error Recovery

```dart
class ErrorRecovery {
  /// Attempt to restore original IMEI on failure
  static Future<bool> restoreOnFailure(String backupPath);

  /// Reboot device to recover from error state
  static Future<bool> recoverWithReboot();

  /// Reset device to factory state (last resort)
  static Future<bool> factoryReset();
}
```

---

## User Interface Flow

### Main Flow

```
1. Connect Device
   └── Auto-detect USB device
   └── Verify device compatibility

2. Read Current IMEI
   └── Display current IMEI
   └── Validate IMEI checksum

3. Create Backup (Required)
   └── Save current IMEI to backup file
   └── Verify backup integrity

4. Enter New IMEI
   └── Validate format (15 digits)
   └── Validate Luhn checksum
   └── Show legal warning

5. Write New IMEI
   └── Send AT^CIMEI command
   └── Verify write success

6. Reboot Device
   └── Send AT+CFUN=1,1
   └── Wait for reboot

7. Verify New IMEI
   └── Read IMEI after reboot
   └── Compare with expected value
```

---

## Error Handling

### Error Codes

| Code | Description | Recovery |
|------|-------------|----------|
| IMEI_001 | Device not found | Reconnect USB |
| IMEI_002 | Device not supported | Check compatibility list |
| IMEI_003 | Invalid IMEI format | Validate input |
| IMEI_004 | Invalid Luhn checksum | Recalculate checksum |
| IMEI_005 | Backup creation failed | Retry or free storage |
| IMEI_006 | Write command failed | Retry with timeout |
| IMEI_007 | Verification failed | Restore from backup |
| IMEI_008 | Reboot failed | Manual reboot required |
| IMEI_009 | Permission denied | Run as administrator |
| IMEI_010 | Device busy | Close other connections |

### Error Messages

```dart
class IMEIErrorMessages {
  static const Map<String, String> messages = {
    'IMEI_001': 'Device not found. Please check USB connection.',
    'IMEI_002': 'Device not supported. Only Huawei and Qtech devices are supported.',
    'IMEI_003': 'Invalid IMEI format. Must be 15 digits.',
    'IMEI_004': 'Invalid IMEI checksum. Please verify the number.',
    'IMEI_005': 'Failed to create backup. Please free storage space.',
    'IMEI_006': 'Failed to write IMEI. Please retry.',
    'IMEI_007': 'Verification failed. Restoring original IMEI...',
    'IMEI_008': 'Device reboot failed. Please reboot manually.',
    'IMEI_009': 'Permission denied. Run as administrator.',
    'IMEI_010': 'Device is busy. Close other connections and retry.',
  };
}
```

---

## Testing Requirements

### Unit Tests

```dart
// IMEIValidator tests
test('Valid IMEI should pass Luhn check', () {
  expect(IMEIValidator.isValid('861234567890123'), isTrue);
});

test('Invalid IMEI should fail Luhn check', () {
  expect(IMEIValidator.isValid('861234567890124'), isFalse);
});

test('Calculate check digit', () {
  expect(IMEIValidator.calculateCheckDigit('86123456789012'), '3');
});

// ATCommandProcessor tests
test('Parse AT command response', () {
  final processor = ATCommandProcessor();
  expect(processor.parseIMEIResponse('AT+CGSN\n861234567890123\nOK'), '861234567890123');
});
```

### Integration Tests

```dart
// Full IMEI change flow
test('Full IMEI change workflow', () async {
  // 1. Connect device
  final device = await communicator.detectDevices();
  expect(device, isNotEmpty);

  // 2. Read current IMEI
  final oldIMEI = await processor.readIMEI();
  expect(IMEIValidator.isValid(oldIMEI), isTrue);

  // 3. Create backup
  final backup = await backupManager.createBackup(...);
  expect(backup.success, isTrue);

  // 4. Write new IMEI
  const newIMEI = '861234567890124';  // Valid test IMEI
  await processor.writeIMEI(newIMEI);

  // 5. Reboot and verify
  await processor.reboot();
  await Future.delayed(Duration(seconds: 30));  // Wait for reboot

  final verifiedIMEI = await processor.readIMEI();
  expect(verifiedIMEI, equals(newIMEI));
});
```

---

## Dependencies

### Flutter Packages

```yaml
dependencies:
  serial_port: ^2.0.0      # USB serial communication
  permission_handler: ^11.0 # Runtime permissions
  path_provider: ^2.1.0    # Storage paths
  crypto: ^3.0.0          # Checksum calculation
```

### Native Dependencies

**Android**:
- USB Host mode support
- Serial driver for FTDI/CP210x chips
- Device permission handling

**Linux/Mac**:
- libusb-1.0
- User must be in dialout group (Linux)

---

## Security Considerations

### Data Protection

- Backups stored with SHA-256 checksum
- No cloud storage of IMEI data
- Local storage only
- Option to encrypt backups

### Logging

```dart
class AuditLogger {
  /// Log IMEI modification attempt
  static void logModification({
    required String deviceSerial,
    required String oldIMEI,
    required String newIMEI,
    required String user,
    required String ipAddress,
  });
}
```

**Log Entry Format**:
```
[2024-03-04 10:00:00] IMEI_MODIFICATION
Device: Huawei E3372 (C657843210)
Old IMEI: 861234567890123
New IMEI: 861234567890124
User: admin
IP: 192.168.1.100
Status: SUCCESS
```

---

## Open Questions

1. **Qtech Support**: What proprietary protocol does Qtech use?
2. **Additional Devices**: Should we support more Huawei models?
3. **Batch Operations**: Support for modifying multiple devices?
4. **GUI vs CLI**: Should this be a GUI tool or command-line only?

---

*Generated by Layer 2 Verification | Status: DRAFT | Review required*
