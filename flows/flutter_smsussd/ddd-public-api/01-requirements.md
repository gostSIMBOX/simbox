# Requirements: Public API

> Stakeholder-facing documentation for Flutter SMS/USSD plugin public API.

## Overview

The flutter_smsussd plugin provides a simple, cross-platform API for SMS messaging functionality. This document describes the public API from a stakeholder perspective.

## Stakeholders

- **App Developers**: Integrate SMS functionality into Flutter apps
- **Product Managers**: Understand feature capabilities and limitations
- **QA Teams**: Test SMS functionality across platforms
- **End Users**: Experience SMS features in the final app

## Functional Requirements

### FR-1: Send SMS Messages

**Description**: Send SMS messages from the app.

**User Story**: As a developer, I want to send SMS messages so that users can communicate via SMS.

**API**:
```dart
final plugin = FlutterSmsussd();

bool success = await plugin.sendSms(
  phoneNumber: '+1234567890',
  message: 'Hello from Flutter!',
);
```

**Platform Behavior**:
- **Android**: Sends SMS directly (user doesn't see composer)
- **iOS**: Opens Messages app with pre-filled content (user must tap Send)
- **Web**: Not supported

**Return Value**: `true` if successful, `false` otherwise

### FR-2: Read SMS Messages

**Description**: Read SMS messages from the device.

**User Story**: As a developer, I want to read SMS messages so that users can view their message history.

**API**:
```dart
List<SmsMessage> messages = await plugin.getSmsMessages();
```

**Platform Behavior**:
- **Android**: Returns all SMS messages from device
- **iOS**: Throws `UnsupportedError` (not supported)
- **Web**: Throws `UnsupportedError` (not supported)

**Return Value**: List of `SmsMessage` objects

### FR-3: Filter Messages by Phone Number

**Description**: Get SMS messages from a specific phone number.

**User Story**: As a developer, I want to filter messages by contact so that users can view conversation threads.

**API**:
```dart
List<SmsMessage> messages = await plugin.getSmsMessagesByPhoneNumber('+1234567890');
```

**Platform Behavior**:
- **Android**: Returns filtered SMS messages
- **iOS**: Throws `UnsupportedError` (not supported)
- **Web**: Throws `UnsupportedError` (not supported)

**Return Value**: List of `SmsMessage` objects from specified number

### FR-4: Check SMS Permissions

**Description**: Check if SMS permissions are granted.

**User Story**: As a developer, I want to check permissions before using SMS features so that I can guide users to enable them.

**API**:
```dart
bool hasPermission = await plugin.hasSmsPermissions();
```

**Platform Behavior**:
- **Android**: Checks SEND_SMS, READ_SMS, RECEIVE_SMS permissions
- **iOS**: Returns `true` (permissions not required)
- **Web**: Returns `true` (not applicable)

**Return Value**: `true` if permissions granted, `false` otherwise

### FR-5: Request SMS Permissions

**Description**: Request SMS permissions from the user.

**User Story**: As a developer, I want to request permissions so that users can enable SMS features.

**API**:
```dart
bool granted = await plugin.requestSmsPermissions();
```

**Platform Behavior**:
- **Android**: Shows system permission dialog
- **iOS**: Returns `true` (permissions not required)
- **Web**: Not applicable

**Return Value**: `true` if granted, `false` if denied

### FR-6: Get Platform Version

**Description**: Get the platform version string.

**User Story**: As a developer, I want to know the platform version for debugging and analytics.

**API**:
```dart
String? version = await plugin.getPlatformVersion();
```

**Return Value**: Platform version string (e.g., "Android 13")

## Data Models

### SmsMessage

Represents an SMS message.

**Properties**:
- `id` (String): Unique message identifier
- `address` (String): Phone number
- `body` (String): Message content
- `date` (DateTime): Message timestamp
- `type` (SmsType): Message type

**Example**:
```dart
SmsMessage(
  id: '123',
  address: '+1234567890',
  body: 'Hello World',
  date: DateTime(2024, 1, 1, 12, 0),
  type: SmsType.inbox,
)
```

### SmsType

Enum for message types.

**Values**:
- `SmsType.inbox`: Received messages
- `SmsType.sent`: Sent messages
- `SmsType.draft`: Draft messages
- `SmsType.outbox`: Outbox messages
- `SmsType.failed`: Failed messages
- `SmsType.queued`: Queued messages

## Platform Support Matrix

| Feature | Android | iOS | Web | Linux | macOS | Windows |
|---------|---------|-----|-----|-------|-------|---------|
| Send SMS | ✅ Full | ⚠️ Composer | ❌ | ❌ | ❌ | ❌ |
| Read SMS | ✅ Full | ❌ | ❌ | ❌ | ❌ | ❌ |
| Filter by Number | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Check Permissions | ✅ | ✅ (N/A) | ✅ (N/A) | ❌ | ❌ | ❌ |
| Request Permissions | ✅ | ✅ (N/A) | ❌ | ❌ | ❌ | ❌ |

**Legend**:
- ✅ Full support
- ⚠️ Limited support (user interaction required)
- ❌ Not supported
- ✅ (N/A) Returns true (not applicable)

## Error Handling

### Common Errors

**PERMISSION_DENIED**:
```dart
// SMS permissions not granted
// Android: Request permissions first
// iOS: Should not occur (permissions not required)
```

**INVALID_ARGUMENTS**:
```dart
// Missing required parameters
// Ensure phoneNumber and message are provided
```

**SMS_SEND_ERROR**:
```dart
// Failed to send SMS
// Check device SMS capability and network
```

**SMS_READ_ERROR**:
```dart
// Failed to read SMS messages
// Check permissions and device support
```

**NO_ACTIVITY**:
```dart
// No activity available for permission request
// Ensure plugin is used within active Flutter context
```

**NOT_SUPPORTED**:
```dart
// Feature not supported on this platform
// iOS/Web: Reading SMS not supported
```

### Error Handling Example

```dart
try {
  final messages = await plugin.getSmsMessages();
  // Process messages
} on PermissionDeniedException {
  // Request permissions first
  await plugin.requestSmsPermissions();
} on UnsupportedError {
  // Feature not available on this platform
  showPlatformNotSupportedDialog();
} on StateError catch (e) {
  // Application error
  logError(e.message);
}
```

## Usage Examples

### Basic SMS Sending

```dart
import 'package:flutter_smsussd/flutter_smsussd.dart';

class SmsService {
  final _plugin = FlutterSmsussd();

  Future<bool> sendVerificationCode(String phoneNumber, String code) {
    return _plugin.sendSms(
      phoneNumber: phoneNumber,
      message: 'Your verification code is: $code',
    );
  }
}
```

### Reading Messages

```dart
Future<List<SmsMessage>> getRecentMessages() async {
  try {
    final messages = await _plugin.getSmsMessages();
    return messages.take(10).toList(); // Last 10 messages
  } on UnsupportedError {
    return []; // Platform doesn't support reading
  }
}
```

### Permission Flow

```dart
Future<bool> ensurePermissions() async {
  // Check if already granted
  if (await _plugin.hasSmsPermissions()) {
    return true;
  }

  // Request permissions
  final granted = await _plugin.requestSmsPermissions();
  if (!granted) {
    // Show custom dialog explaining why permissions are needed
    showPermissionRationale();
  }
  return granted;
}
```

## Non-Functional Requirements

### NFR-1: Ease of Use

**Description**: API should be intuitive and easy to integrate.

**Metrics**:
- Integration time < 15 minutes
- Minimal boilerplate code
- Clear error messages

### NFR-2: Cross-Platform Consistency

**Description**: Same API across all platforms.

**Metrics**:
- Single codebase works on all platforms
- Consistent method signatures
- Clear documentation of platform differences

### NFR-3: Reliability

**Description**: Predictable behavior across platforms.

**Metrics**:
- Clear error messages for unsupported features
- Graceful degradation on limited platforms
- No crashes or undefined behavior

### NFR-4: Documentation

**Description**: Comprehensive documentation for stakeholders.

**Metrics**:
- README with setup instructions
- API reference documentation
- Platform-specific behavior documented
- Example code provided

## Constraints

### Platform Constraints

- **iOS**: Cannot send/read SMS programmatically (Apple restrictions)
- **Web**: No SMS capability in browsers
- **Desktop**: Linux/macOS/Windows not implemented

### Permission Constraints

- **Android 6.0+**: Requires runtime permission requests
- **Android Manifest**: Must declare SMS permissions

### Legal Constraints

- **Privacy Policies**: Must disclose SMS access in app privacy policy
- **App Store Guidelines**: Must comply with platform-specific rules

## Open Questions

None - API is stable and well-documented.

---

*Generated by /legacy analysis on 2026-03-04*
*Status: DRAFT*
